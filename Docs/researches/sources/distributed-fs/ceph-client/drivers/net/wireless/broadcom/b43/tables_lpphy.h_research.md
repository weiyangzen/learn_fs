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
