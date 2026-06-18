# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2056.c lines 1-4002

## Scope

This chunk covers the first 4002 lines of `drivers/net/wireless/broadcom/b43/radio_2056.c`. It contains Broadcom b43 N-PHY radio 0x2056 static data: revision-specific radio initialization tables, table pointer/length bundles, helper macros for channel-table construction, and the first part of the PHY revision 3 channel table. The actual upload and channel lookup functions are later in the same source file, outside this chunk, but are noted here as consumers because they define how these static tables are used.

## Purpose

The chunk supplies hard-coded register programming data for Broadcom 2056 radios used by the b43 N-PHY path. It separates initialization defaults into synthesizer (`SYN`), transmit (`TX`), and receive (`RX`) tables, with distinct values for 5 GHz and 2.4 GHz operation and per-entry flags controlling whether a register should be uploaded during normal initialization. It also starts the channel tuning table for PHY rev3, mapping operating frequencies to PLL, LO generator, RX LNA, TX boost, and PHY bandwidth register values.

The data is source-tree aligned with the b43 radio and PHY code. `radio_2056.h` provides register address constants and routing prefixes such as `B2056_SYN`, `B2056_TX0`, `B2056_TX1`, `B2056_RX0`, and `B2056_RX1`; `phy_n.c` later writes the channel-table fields into hardware through `b43_radio_write()`.

## Important Types and Macros

- `struct b2056_inittab_entry`: one initialization-table cell with `.ghz5`, `.ghz2`, and `.flags`. The values are `u16`, but most literal values are 8-bit radio register values. The flags decide whether the entry is valid and whether it should be uploaded by the later uploader.
- `B2056_INITTAB_ENTRY_OK`: marks an initialized table slot as meaningful. Entries without this flag are skipped by the upload path.
- `B2056_INITTAB_UPLOAD`: marks an entry for normal upload. Entries without this flag can still be uploaded when the caller passes an override flag to the uploader.
- `UPLOAD` and `NOUPLOAD`: designated-initializer shorthands for `.flags = OK | UPLOAD` and `.flags = OK`.
- `struct b2056_inittabs_pts`: groups the SYN/TX/RX table pointers and their lengths for one PHY/radio revision choice.
- `INITTABSPTS(prefix)`: creates a `static const struct b2056_inittabs_pts` named after the table prefix and fills pointer/length pairs with `ARRAY_SIZE()`.
- `RADIOREGS3(...)`: expands 37 radio tuning literals into named fields of `struct b43_nphy_channeltab_entry_rev3`, covering SYN PLL calibration/divider/filter registers, LO generator registers, RX0/RX1 LNA tuning, and TX0/TX1 boost tune fields.
- `PHYREGS(...)`: expands six PHY bandwidth register literals into the embedded `.phy_regs` fields of a channel table entry.

## Initialization Table Layout

The first major part of the chunk is a set of static `const struct b2056_inittab_entry` arrays. They are indexed directly by symbolic radio register offsets, for example `B2056_SYN_PLL_CP2`, `B2056_TX_PADA_IDAC`, or `B2056_RX_TIA_IOPAMP`. This is important: the uploader later writes to `routing | i`, so the array index is the radio register offset. Sparse or missing designated entries are not safe unless their default zero flags are intentionally skipped.

Revision groups in this chunk:

- PHY rev3: `b2056_inittab_phy_rev3_syn`, `_tx`, `_rx`.
- PHY rev4: `b2056_inittab_phy_rev4_syn`, `_tx`, `_rx`.
- Radio rev5: `b2056_inittab_radio_rev5_syn`, `_tx`, `_rx`.
- Radio rev6: `b2056_inittab_radio_rev6_syn`, `_tx`, `_rx`.
- Radio rev7/9: `b2056_inittab_radio_rev7_9_syn`, `_tx`, `_rx`.
- Radio rev8: `b2056_inittab_radio_rev8_syn`, `_tx`, `_rx`.
- Radio rev11: compact override-style `b2056_inittab_radio_rev11_syn`, `_tx`, `_rx`, containing only selected uploaded entries instead of full reserved/default coverage.

The full tables for rev3, rev4, rev5, rev6, rev7/9, and rev8 mostly repeat the same register map but alter key revision-sensitive values. Examples include PLL/PFD/loop-filter entries, TX PA and GMBB bias/IDAC entries, RX mixer/TIA bias entries, RX LPF output common-mode values, VGA DC-cancel bias, and spare registers. Rev11 is notable because it does not list the entire address map; it records only entries that are flagged for upload. This relies on skipped zero-flag holes for all other indexes and makes `ARRAY_SIZE()` equal to the highest designated index plus one.

## Control Flow and Data Use

Within this chunk there is no executable control flow beyond macro expansion and static initialization. The control model is table-driven:

1. Hardware revision selection happens later by choosing one `b2056_inittabs_pts` bundle.
2. The later uploader iterates each selected SYN/TX/RX table by index.
3. For every entry with `B2056_INITTAB_ENTRY_OK`, it writes either `.ghz5` or `.ghz2` when the entry has `B2056_INITTAB_UPLOAD` or when upload flags are ignored by the caller.
4. TX and RX tables are applied to both cores by using `B2056_TX0`/`B2056_TX1` and `B2056_RX0`/`B2056_RX1` routing prefixes.

The channel-table portion starts at line 3076 with `b43_nphy_channeltab_phy_rev3[]`. Each entry has `.freq`, `RADIOREGS3(...)`, and `PHYREGS(...)`. The table begins with 5 GHz frequencies from 4920 MHz through 5910 MHz and, within this chunk, begins the 2.4 GHz entries from 2412 MHz through the start of the 2437 MHz entry. Later lines outside this chunk finish this table and define equivalent tables for other revisions.

## State and Persistence Behavior

All data in this chunk is static `const` table data stored in the kernel image. It does not mutate driver state directly. Persistence is therefore indirect: once later b43 code uploads an entry, the chosen value persists in the radio/PHY hardware registers until reset, reinitialization, channel change, or another calibration path overwrites it.

The tables encode persistent assumptions about analog calibration and board/radio behavior. Because many entries are marked `NOUPLOAD`, the difference between normal initialization and forced/full initialization is significant. The later uploader's `ignore_uploadflag` mode can write far more registers, including reserved or default-looking locations, so the meaning of `NOUPLOAD` is part of the hardware contract.

## Dependencies

- `b43.h`: driver core types such as `struct b43_wldev`, logging/warning helpers, and radio access declarations used by consumers later in the file.
- `radio_2056.h`: all `B2056_*` register offsets and routing prefixes used as designated indexes and write addresses.
- `phy_common.h`: common PHY support included by this source.
- `tables_nphy.h`: channel-table struct definitions, including `struct b43_nphy_channeltab_entry_rev3` and its embedded PHY register fields.
- Linux kernel helpers/types: `u16`, `u8`, `bool`, and `ARRAY_SIZE()`.
- Downstream hardware access: later upload/setup code uses `b43_radio_write()` and PHY register writers to apply values from these arrays.

## Integration Points

- `phy_n.c` has `b43_chantab_radio_2056_upload()`, which consumes `struct b43_nphy_channeltab_entry_rev3` values by writing the `RADIOREGS3` fields to `B2056_SYN_*`, `B2056_RX0/1 | B2056_RX_*`, and `B2056_TX0/1 | B2056_TX_*` registers.
- Later in `radio_2056.c`, `b43_nphy_get_inittabs_rev3()` selects the appropriate `b2056_inittabs_pts` bundle based on `dev->phy.rev` and `phy->radio_rev`.
- Later in `radio_2056.c`, `b2056_upload_inittabs()` uploads the selected SYN table and duplicates TX/RX tables to both cores.
- Later in `radio_2056.c`, `b2056_upload_syn_pll_cp2()` pulls only the selected `B2056_SYN_PLL_CP2` entry, so that indexed entry must exist and be correct for each supported revision.
- Later channel lookup code returns a `b43_nphy_channeltab_entry_rev3` by frequency. The chunk's rev3 table entries must align with the frequencies accepted by mac80211/cfg80211 and the b43 channel setup path.

## Risks and Sharp Edges

- Index-as-address coupling: changing an index constant in `radio_2056.h`, adding an entry under the wrong `B2056_*` symbol, or removing a designated initializer can silently redirect writes to the wrong register.
- Sparse table semantics: rev11 has sparse, upload-only entries. A reader or tool that assumes a dense table would misunderstand its intended behavior; the later uploader skips zero-flag holes.
- Upload flag mistakes: marking an entry `UPLOAD` instead of `NOUPLOAD` can cause normal initialization to touch registers that were meant only for forced upload, while missing `UPLOAD` can omit required calibration/bias state.
- Band value mistakes: each entry carries separate `.ghz5` and `.ghz2` values even when most are equal. A swapped or stale value can break only one band and may be hard to diagnose without RF tests.
- Revision selection risk: the same source serves PHY rev3/4 and radio rev5/6/7/8/9/11. Copy-paste similarity makes small revision-specific deltas easy to lose.
- Channel table truncation at chunk boundary: this research chunk only includes the start of `b43_nphy_channeltab_phy_rev3[]`. The table continues past line 4002, so full channel coverage and final array closure are outside this work item.
- Hardware-only validation: most defects here are not caught by normal compile tests because the code is static data. Wrong values compile cleanly but can cause PLL lock failures, weak TX power, RX sensitivity loss, or band/channel-specific association failures.

## Test Signals

- Build signal: compile the b43 driver with `CONFIG_B43` and N-PHY support enabled. This catches missing register symbols, struct-field mismatches, macro arity errors, and array syntax problems.
- Static inspection: verify every `B2056_*` designated index belongs to the correct SYN/TX/RX register namespace and that table lengths produced by `ARRAY_SIZE()` include all intended upload entries.
- Runtime probe signal: driver initialization for devices with PHY rev3, PHY rev4, and radio revisions 5, 6, 7, 8, 9, and 11 should not hit the later `B43_WARN_ON(1)` unsupported-table path.
- Radio upload trace: instrument or trace `b43_radio_write()` during 2056 init and confirm normal uploads include only `UPLOAD` entries unless the caller intentionally forces full upload.
- Channel-change signal: for PHY rev3 devices, switching across the frequencies covered here should select the matching channel table entry and write the expected PLL/LO/LNA/TX boost and PHY bandwidth values.
- RF/functional signal: association, scan, RSSI stability, and TX throughput should be checked on both 2.4 GHz and 5 GHz channels, because the tables contain separate band values and per-core RX/TX paths.
