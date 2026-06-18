<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.c

## Purpose

`phytbl_n.c` is the N-PHY/MIMO static table bank for brcmsmac. It stores large immutable tables for frame structure, frame lookup, tone maps, training, interleaving, pilots, TDI data for 20/40 MHz and antenna/core combinations, channel estimation, MCS, noise variance, estimated/adjusted power, gain control, IQ, LOFT, antenna switch control, and PAPD compensation/scalar data. It exports `struct phytbl_info` arrays grouped by N-PHY revision so `phy_n.c` can initialize hardware tables by iterating descriptors.

## Important APIs, Types, And Data

- Rev0 exports: `mimophytbl_info_rev0`, `mimophytbl_info_rev0_volatile`, and size constants. Rev0 splits baseline tables from volatile power/gain/IQ/LOFT tables.
- Rev3 exports: `mimophytbl_info_rev3`, four antenna-switch volatile variants (`mimophytbl_info_rev3_volatile*`), and size constants. Rev3 also exports `noise_var_tbl_rev3[]`.
- Rev7 exports: `mimophytbl_info_rev7`, `mimophytbl_info_sz_rev7`, and `noise_var_tbl_rev7[]`. Rev7 reuses many rev3 tables, changes tone/noise data, and adds PAPD epsilon/scalar tables.
- Rev16 exports: `mimophytbl_info_rev16` and size. This is a smaller descriptor set focused on noise/power/gain/IQ/LOFT tables reused from rev7/rev3 data.
- Many private `static const` arrays back those descriptor exports, including `frame_struct_rev0`, `frame_struct_rev3`, `tmap_tbl_rev0`, `tmap_tbl_rev3`, `tmap_tbl_rev7`, `tdtrn_tbl_*`, `mcs_tbl_*`, per-core TX power control tables, and PAPD tables.

## Control Flow

The file has no functions. Runtime behavior is driven by `phy_n.c`: N-PHY init chooses `mimophytbl_info_rev16`, `rev7`, `rev3`, or `rev0` based on PHY revision and writes each descriptor with `wlc_phy_write_table_nphy()`. Additional volatile writes are selected for rev3 antenna-switch control based on board flags, using `ANT_SWCTRL_TBL_REV3_IDX` from `phytbl_n.h` to substitute one of the variant arrays.

## State And Persistence

All data is immutable driver text/rodata. Hardware table state changes only when users write these descriptors into the device. Exported `noise_var_tbl_rev3` and `noise_var_tbl_rev7` are also read directly by calibration/noise code in `phy_n.c` to derive minimum noise variance values.

## Dependencies And Integration Points

The file includes `<types.h>`, `phy_int.h` for `struct phytbl_info`/`ARRAY_SIZE`, and `phytbl_n.h` for exported declarations. It is tightly coupled to `phyreg_n.h` table ID definitions and to `phy_n.c` initialization around lines that iterate `mimophytbl_info_sz_rev*` and program volatile arrays. Noise calibration paths in `phy_n.c` index `noise_var_tbl_rev3`/`rev7` directly, so those arrays are both table payloads and algorithm inputs.

## Risks And Edge Cases

- Descriptor metadata is as important as payload values. Wrong table ID, offset, width, or size can write a valid array into the wrong N-PHY table region.
- Revision reuse is subtle: rev7 and rev16 intentionally reuse rev3 arrays for several tables. A change meant for one revision can affect others.
- Volatile antenna switch tables for rev3 have four variants; wrong board selection can break antenna routing and RF performance.
- Direct `noise_var_tbl_*` indexing in `phy_n.c` assumes stable table lengths and positions. Truncating or reordering those arrays can break calibration without a compile error.
- The file is mostly numeric literals, so review requires comparison against known-good hardware tables rather than semantic code reasoning.

## Test Signals

Build coverage should ensure descriptor symbols and size constants match the header. Runtime validation includes successful N-PHY init for rev0/rev3/rev7/rev16 paths, table write completion, correct antenna-switch variant selection on supported boards, stable noise calibration using `noise_var_tbl_*`, and no regressions in receive sensitivity, MCS operation, transmit power control, PAPD, or channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.c -->
