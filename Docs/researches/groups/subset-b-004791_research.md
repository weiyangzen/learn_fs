# subset-b-004791 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_nphy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_nphy.c

Purpose: Implements Broadcom b43 N-PHY table data, table MMIO access helpers, revision-specific table initialization, and exported lookup helpers for N-PHY calibration and gain-control paths. Most of the file is static calibration payload: frame structure, TMAP, TDTRN, pilot, channel-estimate, noise-variance, MCS, per-core estimate/adjust-power, gain-control, IQ, LO feedthrough, antenna switch, TX gain, RF power offset, IQ/LO calibration ladder, RF override, and gain-control workaround tables.

Important APIs and data: `b43_ntab_read`, `b43_ntab_read_bulk`, `b43_ntab_write`, and `b43_ntab_write_bulk` provide typed 8/16/32-bit access using the high bits supplied by `B43_NTAB8/16/32`. `b43_nphy_tables_init` selects the initializer for PHY rev 0, rev 3+, rev 7+, or rev 16+. `b43_nphy_get_tx_gain_table`, `b43_ntab_get_rf_pwr_offset_table`, `b43_nphy_get_gain_ctl_workaround_ent`, and `b43_nphy_get_rf_ctl_over_rev7` export table selections for later N-PHY calibration code in `phy_n.c`. The public constant exports include PAPD gain deltas, IQ calibration gain parameters, LO/IQ ladders, LO scale values, TX IQ/LO calibration command arrays, filter coefficients, and RF control override tables.

Control flow: Single table reads mask off `B43_NTAB_TYPEMASK`, program `B43_NPHY_TABLE_ADDR`, then read low and optional high data registers. Bulk reads and writes program the address once and rely on hardware table address auto-increment. BCM43224 chip revision 1 has explicit workaround handling in bulk paths: reads force a dummy low-register read and rewrite the address; writes do the same for table 9. Table initialization is gated by `dev->phy.do_full_init` for static tables and always programs volatile tables. Rev 0 uploads legacy static and volatile tables. Rev 3 uses rev3 table addresses and antenna switch LUTs from SPROM. Rev 7 uploads the rev7 TMAP/noise variants and uses an antenna software LUT writer. Rev 16 only refreshes noise/shared LUT static content on full init, then reuses the rev7 volatile path.

State and persistence: The file has no heap ownership or persistent kernel object state of its own. Its effects are persisted in device PHY table SRAM and PHY registers until reset, suspend, or reinitialization. Several helpers return pointers into static file-scope tables. `b43_nphy_get_gain_ctl_workaround_ent` is stateful in a subtle way: it returns a pointer to mutable static workaround entries and adjusts fields in place based on `tr_iso`, `ext_lna`, band, PHY revision, radio revision, and channel width. Repeated calls can therefore observe already-masked or ORed workaround values.

Dependencies and integration points: Depends on `b43.h`, `tables_nphy.h`, `phy_common.h`, and `phy_n.h`; on `b43_phy_read/write`, `b43_current_band`, `b43_is_40mhz`, `b43err`, `B43_WARN_ON`, and `BUILD_BUG_ON`; on `struct b43_wldev`, `dev->phy`, `dev->phy.n`, chip id/revision, radio revision, SPROM FEM fields, and `NL80211_BAND_*`. It is called heavily from `phy_n.c`: table init during N-PHY initialization, RF override lookup, gain workaround upload, TX gain table programming, RF power offset programming, PAPD/IQ/LO calibration, and runtime table save/restore paths.

Risks: Hardware table values are opaque and revision-sensitive; wrong table address, width tag, or array length can silently corrupt calibration. `assert_ntab_array_sizes` is reached only through an unreachable tail after `return` in `b43_ntab_write`, but the referenced `BUILD_BUG_ON` expressions are still compiled and provide size validation. Bulk access assumes natural alignment when casting `u8 *` to `u16 *` or `u32 *`; current callers pass arrays of matching type, but generic callers must not pass misaligned buffers. Error paths for unknown gain/RF tables return `NULL`; callers must check before bulk writes. The mutable static workaround entry behavior can surprise future code that expects pure lookup semantics.

Test signals: Build coverage should catch table-size mismatches, missing symbols, and invalid struct declarations. Runtime validation needs N-PHY hardware or MMIO trace comparison: confirm initialization for rev 0/3/7/16, BCM43224 rev1 bulk workaround behavior, 2 GHz vs 5 GHz table selection, IPA vs EPA gain table selection, SPROM antenna LUT handling, and expected `b43err` messages for unsupported tables without NULL dereference in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_nphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_nphy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_nphy.h

Purpose: Declares the public N-PHY table interface and the data structures used by N-PHY calibration, RF override, TX IQ/LO calibration, gain-control workaround, and table access code.

Important APIs and types: Defines `struct b43_phy_n_sfo_cfg`, `struct nphy_txiqcal_ladder`, `struct nphy_rf_control_override_rev2`, `struct nphy_rf_control_override_rev3`, `struct nphy_rf_control_override_rev7`, and `struct nphy_gain_ctl_workaround_entry`. Defines `B43_NTAB_TYPEMASK`, the width tags `B43_NTAB_8BIT`, `B43_NTAB_16BIT`, `B43_NTAB_32BIT`, and the address constructors `B43_NTAB8/16/32`. Declares `b43_ntab_read`, `b43_ntab_read_bulk`, `b43_ntab_write`, `b43_ntab_write_bulk`, `b43_nphy_tables_init`, TX gain and RF power table lookup helpers, gain workaround lookup, and rev7 RF control override lookup.

Control flow encoded by the header: Callers construct a typed table offset with `B43_NTAB8/16/32`; the implementation decodes the high bits and routes to the correct register-width access sequence. Macro constants map logical N-PHY table names to table ids and offsets for legacy static tables, legacy volatile tables, rev3+ tables, rev7+ variants, and TX IQ/LO calibration table sizes. This header does not execute logic but establishes the table addressing contract used across `tables_nphy.c` and `phy_n.c`.

State and persistence: No state is stored in the header. The declared helpers mutate device table SRAM and return pointers to static calibration tables in `tables_nphy.c`. The comment on `b43_nphy_get_gain_ctl_workaround_ent` promises a non-NULL return, but the returned object is mutable static storage, so callers should treat it as shared driver data.

Dependencies and integration points: Includes `<linux/types.h>` and forward-declares `struct b43_wldev`. It is consumed by `tables_nphy.c` and N-PHY runtime code in `phy_n.c`. The address and size constants must remain synchronized with the static arrays in the implementation.

Risks: The width tag lives in the upper nibble of a `u32` offset while table and element offsets share the lower bits. Passing a raw address without a width tag triggers warning paths and usually returns zero or writes nothing useful. Changing any `*_SIZE` constant without matching the implementation arrays breaks compile-time assertions. The non-NULL comment for the workaround helper is stronger than the implementation's general style and could conceal the fact that returned entries are shared and modified in place.

Test signals: Compile tests validate declarations and many table-size invariants indirectly. Static analysis should check every `B43_NTAB*` use for correct width. Runtime tests should exercise reads/writes for all three widths and ensure callers handle NULL from gain/RF table lookup helpers declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_nphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_ht.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_ht.c

Purpose: Provides Broadcom b43 HT-PHY static calibration tables and generic HT-PHY table access helpers. It initializes the table set used by `phy_ht.c` during HT PHY bring-up and exposes one late gain-control table used by later runtime configuration.

Important APIs and data: `b43_httab_read`, `b43_httab_read_bulk`, `b43_httab_write`, `b43_httab_write_few`, and `b43_httab_write_bulk` implement typed table access via `B43_HTTAB8/16/32`. `b43_phy_ht_tables_init` uploads the static HT table arrays to their hardware table ids and offsets. `b43_httab_0x1a_0xc0_late` is exported for the later update path in `phy_ht.c`. Static arrays include MCS/rate lookup data, power/gain/IQ/LO tables for multiple HT cores, and per-core coefficient/gain control tables.

Control flow: Reads and writes decode the width tag, mask the address to 16 bits, write `B43_PHY_HT_TABLE_ADDR`, and read or write `B43_PHY_HT_TABLE_DATALO` plus `B43_PHY_HT_TABLE_DATAHI` for 32-bit values. Bulk operations program the table address once and stream through sequential entries. `b43_httab_write_few` is a varargs helper for small inline update sequences used by HT init code. `b43_phy_ht_tables_init` performs a fixed upload order with `httab_upload`, beginning with table ids `0x12`, `0x27`, `0x26`, `0x25`, and `0x2f`, then per-core table families `0x1a`, `0x1b`, `0x1c`, and finally additional 32-bit tables `0x1f` through `0x24`.

State and persistence: The file owns no dynamic state. The static constants are immutable driver data. Writes persist only in device HT-PHY table memory/register state until the PHY is reset or reinitialized. The late exported table is read-only data that other HT code can upload later.

Dependencies and integration points: Includes `b43.h`, `tables_phy_ht.h`, `phy_common.h`, and `phy_ht.h`. It depends on the common PHY register helpers and HT register definitions. `phy_ht.c` calls `b43_phy_ht_tables_init`, uses `b43_httab_read` for save/readback operations, `b43_httab_write_few` for compact init patches, and uploads `b43_httab_0x1a_0xc0_late` in a later gain table step.

Risks: Varargs values in `b43_httab_write_few` are read as `int` and stored in `u32`; callers must pass values in range for the chosen width. There is no chip-specific workaround equivalent to N-PHY's BCM43224 table auto-increment handling, so this assumes HT-PHY table auto-increment is reliable. Like the other table files, buffer casts in bulk read/write require callers to pass naturally aligned arrays of matching element width. A table id or offset typo can corrupt unrelated HT calibration entries.

Test signals: `BUILD_BUG_ON` validates the exported late table size. Compile coverage checks the varargs prototype and register symbols. Runtime validation should confirm HT initialization writes the expected table sequence, `b43_httab_write_few` increments addresses correctly, and HT calibration/readback paths in `phy_ht.c` see expected values after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_ht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_ht.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_ht.h

Purpose: Declares the HT-PHY table access contract for the b43 driver and exposes the late HT gain table used outside the table initializer.

Important APIs and types: Defines `B43_HTTAB_TYPEMASK`, width tags `B43_HTTAB_8BIT`, `B43_HTTAB_16BIT`, `B43_HTTAB_32BIT`, and address constructors `B43_HTTAB8/16/32`. Declares `b43_httab_read`, `b43_httab_read_bulk`, `b43_httab_write`, `b43_httab_write_few`, `b43_httab_write_bulk`, and `b43_phy_ht_tables_init`. Defines `B43_HTTAB_1A_C0_LATE_SIZE` and declares `b43_httab_0x1a_0xc0_late`.

Control flow encoded by the header: The caller chooses data width through the address macro, then the implementation routes the operation to 8-, 16-, or 32-bit register access. The varargs write helper supports small sequential writes without defining temporary arrays in callers.

State and persistence: The header stores no state. All declared writes affect HT-PHY table memory on the device. The exported late table is immutable static data defined in `tables_phy_ht.c`.

Dependencies and integration points: Relies on `struct b43_wldev` being visible to including C files through other b43 headers. Used by `tables_phy_ht.c` and HT runtime code in `phy_ht.c`.

Risks: The macros do not validate table ids or offsets; misuse can route valid-width writes to wrong hardware locations. The varargs API has no type safety beyond runtime `B43_WARN_ON` range checks for 8/16-bit values. The late table size constant must stay synchronized with the implementation.

Test signals: Compile tests validate prototypes and the exported array size assertion in `tables_phy_ht.c`. Runtime tests should cover all width constructors and small varargs writes from `phy_ht.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_ht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_lcn.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_lcn.c

Purpose: Implements LCN-PHY table constants, typed LCN table access helpers, and the LCN table initialization path for b43 devices. It covers static LCN table payload upload, 2 GHz external-PA TX gain table programming, RF power table touch-up, software control table selection, and PAPD compensation table reset.

Important APIs and data: Defines private `struct b43_lcntab_tx_gain_tbl_entry` with GM, PGA, PAD, DAC, and BB multiplier components. Exports `b43_lcntab_read`, `b43_lcntab_read_bulk`, `b43_lcntab_write`, `b43_lcntab_write_bulk`, and `b43_phy_lcn_tables_init`. Static arrays `b43_lcntab_0x00` through `0x18` hold calibration values; `b43_lcntab_tx_gain_tbl_2ghz_ext_pa_rev0` supplies 128 TX gain entries; `b43_lcntab_sw_ctl_4313_epa_rev0` supplies software control values for the supported FEM configuration.

Control flow: The access helpers mirror the N/HT table pattern: decode `B43_LCNTAB_TYPEMASK`, program `B43_PHY_LCN_TABLE_ADDR`, then stream through `B43_PHY_LCN_TABLE_DATALO` and optional `DATAHI`. `b43_phy_lcn_upload_static_tables` writes the fixed calibration arrays in a fixed order. `b43_phy_lcn_load_tx_gain_tab` constructs 32-bit gain values for table 7 offsets `0xc0+i` and updates DAC/BB multiplier fields at offsets `0x140+i`, preserving lower 20 bits from the existing table value. `b43_phy_lcn_load_rfpower` currently reads BB multiplier and RF gain values but leaves the computed write as TODO. `b43_phy_lcn_rewrite_rfpower_table` reads and rewrites table 7 offset `0x240+i`, likely forcing hardware refresh. `b43_phy_lcn_clean_papd_comp_table` writes `0x80000` to 128 PAPD compensation entries.

State and persistence: No dynamic state is owned by the file. The initialization writes persistent device PHY table state until reset/reinit. Initialization depends on SPROM board flags: only 2 GHz cards with `B43_BFL_FEM` get the known TX gain table, and only FEM without `B43_BFH_FEM_BT` gets the known software-control table. Unsupported combinations log errors and leave those portions unprogrammed.

Dependencies and integration points: Includes `b43.h`, `tables_phy_lcn.h`, `phy_common.h`, and `phy_lcn.h`. Depends on `b43_current_band`, SPROM board flags, `B43_BFL_FEM`, `B43_BFH_FEM_BT`, PHY register definitions, and common PHY IO helpers. `phy_lcn.c` calls `b43_phy_lcn_tables_init` during LCN PHY initialization.

Risks: Support is partial: non-FEM cards and FEM+BT software-control variants log "unknown" and skip known table programming. `b43_phy_lcn_load_rfpower` reads values without using them, so RF power table calculation remains incomplete. Table 7 rewrite-by-readback is hardware-behavior dependent and not self-documenting. Bulk buffer casts carry the same alignment expectations as N/HT helpers. An incorrect boardflag interpretation can program the wrong PA gain (`0x70` vs `0x10`) into every TX gain entry.

Test signals: Runtime tests need LCN hardware or MMIO traces for 2 GHz FEM and unsupported board variants. Verify static table upload order, TX gain table values at `0xc0/0x140`, SW control table selection for BCM4313 EPA rev0-style boards, PAPD entries reset to `0x80000`, and expected `b43err` messages for unknown combinations. Build tests cover symbol and type consistency but do not validate calibration content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_lcn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_lcn.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_lcn.h

Purpose: Declares the LCN-PHY table access API and typed table-address macros for b43 LCN PHY code.

Important APIs and types: Defines `B43_LCNTAB_TYPEMASK`, width tags `B43_LCNTAB_8BIT`, `B43_LCNTAB_16BIT`, `B43_LCNTAB_32BIT`, and address constructors `B43_LCNTAB8/16/32`. Defines `B43_LCNTAB_TX_GAIN_SIZE` as 128. Declares `b43_lcntab_read`, `b43_lcntab_read_bulk`, `b43_lcntab_write`, `b43_lcntab_write_bulk`, and `b43_phy_lcn_tables_init`.

Control flow encoded by the header: LCN callers construct typed offsets with the macros, then the C implementation decodes the high bits and performs matching register-width IO. The TX gain size constant constrains the private gain table and the initializer loop.

State and persistence: The header has no stored state. Declared operations mutate device LCN-PHY table memory; initialization effects last until PHY reset or reinitialization.

Dependencies and integration points: Relies on b43 include ordering for `u32`, `size_t`, and `struct b43_wldev`. Used by `tables_phy_lcn.c` and LCN code in `phy_lcn.c`.

Risks: Raw offsets without width tags hit warning paths in the implementation. The macros do not range-check table ids or offsets. `B43_LCNTAB_TX_GAIN_SIZE` must remain synchronized with the private 128-entry LCN gain table.

Test signals: Compile tests catch prototype drift. Runtime table IO tests should verify all three width tags and confirm the initializer writes exactly 128 TX gain entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_lcn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/wa.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/wa.c

Purpose: Implements legacy PHY workarounds for the Broadcom b43 driver, primarily for G-PHY revisions. These routines program PHY, radio, OFDM, and G-table registers with workaround values for gain initialization, RSSI, analog behavior, fine frequency, noise, rotor, noise scale, ADV retard, minimum sigma square, carrier-sense thresholds, AGC, board-specific settings, and CPLL non-pilot behavior.

Important APIs and functions: `b43_wa_initgains` initializes LNA/LPF/radio gain-related registers and revision-specific fields. `b43_wa_all` is the public orchestration entry point. Private helpers include `b43_wa_rssi_lt`, `b43_wa_analog`, `b43_wa_fft`, `b43_wa_nft`, `b43_wa_rt`, `b43_wa_nst`, `b43_wa_art`, `b43_wa_msst`, `b43_wa_crs_ed`, `b43_wa_crs_thr`, `b43_wa_crs_blank`, `b43_wa_cck_shiftbits`, `b43_wa_wrssi_offset`, `b43_wa_txpuoff_rxpuon`, `b43_wa_altagc`, `b43_wa_tr_ltov`, `b43_wa_cpll_nonpilot`, and `b43_wa_boards_g`.

Control flow: `b43_wa_all` only supports `B43_PHYTYPE_G`. For G rev1 it applies CRS, CCK shift, fine frequency, noise, rotor, noise scale, ADV retard, WRSSI offset, and alternate AGC workarounds. For G rev2 and rev6 through rev9 it applies TR original lookup value, CRS, RSSI lookup, noise, noise scale, min sigma square, WRSSI offset, alternate AGC, analog, and TX power-off/RX power-on workarounds. Unsupported revisions trigger `B43_WARN_ON`. Board-specific G workarounds always run after the revision branch, then `b43_wa_cpll_nonpilot` runs at the end for both supported and warning paths.

State and persistence: The file has no persistent software data. It writes device state into PHY/radio/OFDM/G table registers. Table payloads are sourced from `tables.h` arrays such as fine frequency, noise, rotor, noise scale, retard, and sigma-square tables. Effects persist until hardware reset, channel/PHY reconfiguration, or later calibration writes overwrite them.

Dependencies and integration points: Includes `b43.h`, `main.h`, `tables.h`, `phy_common.h`, and `wa.h`. Depends on common register helpers (`b43_phy_write`, `b43_phy_mask`, `b43_phy_maskset`, `b43_phy_set`, `b43_radio_write16`, `b43_radio_set`, `b43_ofdmtab_write16/32`, `b43_gtab_write`) and on SPROM board flags/vendor/type/revision. `phy_g.c` calls `b43_wa_all` during G-PHY initialization; `b43_wa_initgains` is available separately for gain setup.

Risks: Workaround values are magic hardware constants with limited local explanation, so changes require hardware documentation or trace comparison. G rev1 is annotated with a review comment, and APHY rev2 RSSI behavior is guarded by a permanent false `FIXME` branch. Unsupported PHY types/revisions warn but still run the final CPLL non-pilot write. `b43_wa_boards_g` has board-specific exclusions and SPROM flag handling that can affect external-LNA/FEM boards; wrong matching can degrade sensitivity or gain behavior.

Test signals: Build tests validate symbol and table references. Runtime validation needs G-PHY hardware across rev1, rev2, rev6-rev9, external-LNA, FEM, and excluded BU4306 board rev `0x17` cases. Useful signals include MMIO write traces, receive sensitivity/RSSI sanity, OFDM/CCK association tests, and absence of warnings on supported revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/wa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/wa.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/wa.h

Purpose: Declares the public PHY workaround entry points for the b43 driver.

Important APIs and types: Declares `b43_wa_initgains(struct b43_wldev *dev)` for gain initialization and `b43_wa_all(struct b43_wldev *dev)` for the full workaround sequence. Uses a conventional include guard and relies on surrounding b43 headers for the `struct b43_wldev` declaration.

Control flow encoded by the header: The header only exposes the two phases. Callers choose between gain-only setup and the complete workaround set implemented in `wa.c`.

State and persistence: No state is stored here. The declared functions write persistent hardware register/table state through the implementation.

Dependencies and integration points: Included by `wa.c` and G-PHY initialization code. It is a narrow interface boundary between PHY bring-up code and the workaround implementation.

Risks: The header does not document PHY-type restrictions; `b43_wa_all` currently only supports G-PHY in the implementation and warns for other PHY types. Callers must ensure the device is in a state where PHY/radio/table writes are valid.

Test signals: Compile tests catch prototype drift. Runtime tests should verify callers invoke these functions only for supported PHY paths and that unsupported PHY types do not rely on side effects beyond warning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/wa.h -->
