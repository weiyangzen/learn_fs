# subset-b-004790 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_lpphy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_lpphy.c

## Purpose
`tables_lpphy.c` is the LP-PHY table and radio calibration data module for the Broadcom `b43` wireless driver. It owns the static init tables for B2062/B2063 radios, the generic LP-PHY table read/write helpers, the PHY revision-specific table uploads, and the TX gain lookup table programming used by the LP PHY bring-up path.

Most of the file is immutable device calibration data: radio register/value tables, PHY lookup tables for noise/filter/power/gain behavior, PAPD tables, and 128-entry TX gain tables split by PHY revision, band, and board PA configuration. The executable code is a small set of upload and packing functions that translate those constants into MMIO/PHY/radio writes.

## Important APIs, Types, And Functions
- `struct b206x_init_tab_entry` stores a radio register `offset`, an A-band value, a G-band value, and flags selecting which bands should receive the entry. `B206X_FLAG_A` and `B206X_FLAG_G` decide whether each entry is emitted during upload.
- `b2062_upload_init_table()` and `b2063_upload_init_table()` iterate their static init arrays and write only entries matching the current band via `b43_radio_write()`.
- `b43_lptab_read()` and `b43_lptab_write()` implement scalar 8/16/32-bit LP table accesses. The encoded offset contains a type tag in the top nibble; the function strips `B43_LPTAB_TYPEMASK`, writes `B43_LPPHY_TABLE_ADDR`, and uses `B43_LPPHY_TABLEDATALO` plus `B43_LPPHY_TABLEDATAHI` for data.
- `b43_lptab_read_bulk()` and `b43_lptab_write_bulk()` stream repeated LP table accesses after programming the table address once. They treat the caller buffer as host-endian typed elements, not byte-serialized firmware data.
- `lpphy_rev0_1_table_init()` uploads the base table set for LP PHY rev 0/1, including minimum signal square, noise scale, CRS gain/NFT, rev0/1 filter control, power-save control, PLL fraction, IQ/LO calibration, OFDM/CCK gain tables, gain delta, and TX power control.
- `lpphy_rev2plus_table_init()` uploads the rev >= 2 base table set. It first clears 704 32-bit entries in table 7, then uploads rev2+ noise/filter/power-save/gain/PAPD tables and substitutes special A0 gain tables for chip `0x4325` revision `0`.
- `struct lpphy_tx_gain_table_entry`, declared in the header, is packed by `lpphy_rev0_1_write_gain_table()` or `lpphy_rev2plus_write_gain_table()` into LP table TX power rows.
- `lpphy_write_gain_table()` dispatches to the revision-specific packer.
- `lpphy_write_gain_table_bulk()` writes a range of table entries by repeatedly calling `lpphy_write_gain_table()`.
- `lpphy_init_tx_gain_table()` selects one of the static 128-entry gain tables based on `dev->phy.rev`, SPROM board flags (`B43_BFH_NOPA`, `B43_BFL_HGPA`), and current band.

## Control Flow
Radio init is data-driven. `b2062_upload_init_table()` and `b2063_upload_init_table()` walk the appropriate static table from top to bottom. For 2 GHz, they require `B206X_FLAG_G` and write `value_g`; for other bands, they require `B206X_FLAG_A` and write `value_a`. This preserves vendor-specified register order while allowing many documented-default entries to remain commented out.

LP table accessors follow the same decoding pattern:
1. Extract type from the encoded offset.
2. Strip the type bits and warn if the remaining address exceeds 16 bits.
3. Program `B43_LPPHY_TABLE_ADDR`.
4. Read or write low/high data registers according to width.

Bulk accesses rely on hardware auto-increment semantics after a single address write. Each loop iteration reads or writes one typed element. Width is chosen only from the encoded type, so mismatched buffers or element counts will silently program the wrong hardware sequence aside from debug warnings.

Base table initialization branches by PHY revision. The rev0/1 path warns on rev >= 2 and chooses rev0 or rev1 OFDM/CCK gain data. The rev2+ path warns on rev < 2, clears table 7, uploads a different set of table IDs, and patches in chip 4325 A0-specific gain tables after the generic rev2+ tables.

TX gain table programming has two hardware formats. Rev0/1 writes packed RF gain bits to table 10 offsets `0xC0 + offset`, then writes BB multiplier bits to table 10 offsets `0x140 + offset`. Rev2+ writes packed pad/PGA/GM and band/revision selector bits to table 7 offsets `0xC0 + offset`, then writes BB multiplier and DAC bits to table 7 offsets `0x140 + offset`. `lpphy_init_tx_gain_table()` chooses the static source table and writes 128 entries.

## State And Persistence Behavior
The C arrays are static `const`; this file has no persistent software state of its own. Its side effects are hardware state changes:
- Radio register writes through `b43_radio_write()`.
- PHY table address and table data register writes through `b43_phy_write()`.
- LP table contents that later power-control, calibration, and gain code reads back.

The table state is assumed to persist in the device until reset/reinitialization or later writes. Integration code in `phy_lp.c` reads and rewrites these tables during power-control setup and PR41573 workaround handling, so the upload helpers are part of the device state restoration story rather than pure initialization.

## Dependencies And Integration Points
The file includes `b43.h`, `tables_lpphy.h`, `phy_common.h`, and `phy_lp.h`. It depends on:
- Register constants for B2062/B2063 radio offsets and LP-PHY table registers.
- `struct b43_wldev`, `dev->phy.rev`, `dev->phy.lp`, `dev->dev->chip_id`, `dev->dev->chip_rev`, and `dev->dev->bus_sprom`.
- `b43_current_band()` and `NL80211_BAND_2GHZ`/`NL80211_BAND_5GHZ`.
- `b43_radio_write()`, `b43_phy_write()`, `b43_phy_read()`, and `B43_WARN_ON()`.
- SPROM board flags `B43_BFH_NOPA`, `B43_BFL_HGPA`.

Primary callers are in `phy_lp.c`: `lpphy_table_init()` selects `lpphy_rev0_1_table_init()` or `lpphy_rev2plus_table_init()` and then calls `lpphy_init_tx_gain_table()`. Radio-specific init paths call `b2062_upload_init_table()` and `b2063_upload_init_table()` before applying additional crystal, PA, and band-specific setup. TX power control and workaround code later use the LP table read/write helpers to preserve or adjust power table rows.

## Risks And Edge Cases
- The static calibration tables are magic-number hardware contracts. Any value, order, table ID, or width change can break RF bring-up, power calibration, sensitivity, or regulatory behavior.
- `b43_lptab_read_bulk()` and `b43_lptab_write_bulk()` cast byte pointers to `u16 *` or `u32 *`. Callers must provide suitably aligned typed arrays; unaligned buffers are architecture-sensitive.
- Bulk helpers document host-endian data. They are not suitable for direct firmware/image byte blobs without conversion.
- Width mismatch is only guarded by `B43_WARN_ON()` for scalar value overflow and invalid type. In production builds, incorrect encoded widths can still write truncated or malformed hardware values.
- `lpphy_write_gain_table_bulk()` loops `for (i = offset; i < count; i++)`, treating `count` as an exclusive end index rather than a number of elements. Current callers pass `offset = 0, count = 128`, but nonzero-offset callers could easily misuse the API.
- TX gain table packers do not range-check `offset`; callers must ensure the selected static table has enough entries and the hardware table window accepts the destination rows.
- `lpphy_rev2plus_table_init()` clears exactly 704 entries in table 7 before upload. This is a hardware-specific constant; changing table layout or revision support would need careful validation.
- Chip 4325 revision 0 receives special A0 overrides after generic rev2+ uploads. Missing that branch would likely regress early silicon only, making it easy to miss without targeted hardware.
- There is an apparent formatting/indentation oddity near the rev0/1 table init `else` block close, but the braces still form a valid function.

## Test Signals
Useful validation is hardware-oriented:
- LP PHY init on rev0, rev1, rev2, and rev3+ hardware, covering both 2 GHz and 5 GHz where supported.
- Boards with `B43_BFH_NOPA`, `B43_BFL_HGPA`, and normal PA configurations to exercise all TX gain table choices.
- B2062 and B2063 radio bring-up logs, association success, receive sensitivity, transmit power, and calibration stability after cold boot and channel changes.
- Debug instrumentation around `B43_WARN_ON()` for invalid table type, overflow, or wrong PHY revision path.
- PR41573 workaround and TX power-control paths that read back and restore table 7/table 10 rows.
- Static build checks with `W=1` or sparse may catch alignment/cast concerns, but the meaningful regressions are RF behavior and table readback mismatches on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_lpphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_lpphy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_lpphy.h

## Purpose
`tables_lpphy.h` is the public interface for the B43 LP-PHY table module. It defines the encoded LP table offset format, exposes the low-level table accessors, declares radio init upload helpers, defines the TX gain table entry shape, and exports the PHY revision-specific table initialization entry points.

The header is intentionally compact: it gives other LP PHY code enough information to address hardware tables without exposing the large calibration arrays in `tables_lpphy.c`.

## Important APIs, Types, And Macros
- `B43_LPTAB_TYPEMASK` reserves the top nibble of an encoded table offset for access width.
- `B43_LPTAB_8BIT`, `B43_LPTAB_16BIT`, and `B43_LPTAB_32BIT` tag encoded offsets with element width.
- `B43_LPTAB8(table, offset)`, `B43_LPTAB16(table, offset)`, and `B43_LPTAB32(table, offset)` encode a table ID and row offset as `((table) << 10) | offset | type`. The C helpers later strip the type and program the low 16-bit address into `B43_LPPHY_TABLE_ADDR`.
- `B43_LPTAB_TXPWR_R2PLUS` and `B43_LPTAB_TXPWR_R0_1` name the TX power lookup table bases for newer and older LP PHY revisions.
- `b43_lptab_read()` and `b43_lptab_write()` are scalar table accessors.
- `b43_lptab_read_bulk()` and `b43_lptab_write_bulk()` transfer typed arrays of 8/16/32-bit LP table entries and return/consume host-endian values.
- `b2062_upload_init_table()` and `b2063_upload_init_table()` upload band-filtered radio initialization tables.
- `struct lpphy_tx_gain_table_entry` contains `gm`, `pga`, `pad`, `dac`, and `bb_mult` fields consumed by the gain-table packers.
- `lpphy_write_gain_table()` and `lpphy_write_gain_table_bulk()` write one or many TX gain rows using the correct hardware packing for the active PHY revision.
- `lpphy_rev0_1_table_init()`, `lpphy_rev2plus_table_init()`, and `lpphy_init_tx_gain_table()` are the main initialization hooks used by LP PHY setup.

## Control Flow And Contracts
The header establishes an encoded-address contract. Callers do not pass a raw table address plus width separately; they build a single `u32` with one of the `B43_LPTAB*()` macros. The implementation decodes the type tag, strips it from the address, writes the table address register, and uses the width to choose which data registers to touch.

Bulk accessors rely on the caller's `nr_elements` matching the width embedded in the encoded offset and on the data pointer referencing a typed array in host byte order. The comment explicitly warns that returned bulk data is not a byte array.

The table init contract is revision split: LP PHY rev 0/1 callers must use `lpphy_rev0_1_table_init()`, rev >= 2 callers must use `lpphy_rev2plus_table_init()`, and all revisions then use `lpphy_init_tx_gain_table()` to select PA/band-specific TX gain rows.

## State And Persistence Behavior
The header itself stores no state. It declares functions that mutate radio registers and LP PHY hardware tables. The encoded table macros make the destination table/offset part of the call-site state contract; bad macro selection persists as incorrect device table contents until later reinitialization or reset.

`struct lpphy_tx_gain_table_entry` is a transient software representation. Once written, its fields are packed into hardware-specific table rows; the original struct is not retained by this module.

## Dependencies And Integration Points
This header assumes prior visibility of kernel integer typedefs (`u8`, `u32`) and `struct b43_wldev`, which are provided by surrounding B43 includes in normal compilation. It is included by `tables_lpphy.c` and by LP PHY implementation files such as `phy_lp.c`.

Integration points include:
- LP PHY base initialization, which chooses rev0/1 or rev2+ table init and then initializes the TX gain table.
- Radio initialization paths for B2062 and B2063.
- TX power-control and calibration code that reads/writes LP table entries by using the `B43_LPTAB*()` macros.

## Risks And Edge Cases
- `B43_LPTAB8/16/32` do not mask `table` or `offset`; callers must keep the encoded address within the 16-bit hardware table address space after the type bits are stripped.
- The table ID is shifted by 10, so the lower 10 bits are the row offset. Larger offsets can overlap table ID bits in the encoded address.
- `B43_LPTAB_TXPWR_R0_1` uses `B43_LPTAB32(0xA0, 0)`, which produces an address that relies on the implementation's broad 16-bit address handling rather than the small table IDs used in most call sites. Treat it as a named hardware base, not a general table number example.
- Bulk accessor users must respect host-endian typed-array semantics and alignment requirements.
- The `lpphy_write_gain_table_bulk()` declaration names `count`, but the implementation treats it as an exclusive end index when `offset` is nonzero.

## Test Signals
Header-level validation comes from build coverage and call-site behavior:
- Compile all B43 LP PHY objects with this header included from both `tables_lpphy.c` and `phy_lp.c`.
- Exercise scalar and bulk table reads/writes on representative LP PHY revisions and verify readback width and row addressing.
- Test revision-specific table init and TX gain table initialization across rev0/1 and rev2+ devices.
- Add focused checks or review for new `B43_LPTAB*()` call sites with nonzero offsets, large table IDs, or byte-buffer bulk transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_lpphy.h -->
