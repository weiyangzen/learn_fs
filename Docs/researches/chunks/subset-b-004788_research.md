# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2056.c lines 4003-10305

## Scope

This chunk covers the end of the Broadcom b43 2056 radio channel-switch tables and the helper functions that publish those tables to the N-PHY channel and radio initialization code. The slice begins in the final eight entries of `b43_nphy_channeltab_phy_rev3[]`, includes all channel tables for PHY rev4 and radio revisions 5, 6, 7/9, 8, and 11, and ends with the init-table selector, init-table upload helpers, PLL CP2 upload helper, and channel-table lookup API.

The source path is in a Ceph client kernel snapshot, but this file is not filesystem code. It is wireless hardware data and control glue for Broadcom B43 IEEE 802.11n radios using the 2056 radio block.

## Purpose

`radio_2056.c` provides static calibration and channel programming data for the Broadcom 2056 radio used by b43 N-PHY devices. Earlier lines define the init-table data and the channel-table macros; this chunk supplies most of the channel-frequency tables and the runtime accessors that select and upload the correct data according to `dev->phy.rev`, `dev->phy.radio_rev`, and current band.

At runtime, this chunk supports two main operations:

- Radio initialization: pick the correct SYN/TX/RX init table for the attached PHY/radio revision and write selected register defaults through `b43_radio_write()`.
- Channel switching: return a per-frequency `struct b43_nphy_channeltab_entry_rev3` that downstream N-PHY code uploads into SYN, RX0/RX1, TX0/TX1, and PHY bandwidth registers.

## Data Tables

The channel-table entries are `struct b43_nphy_channeltab_entry_rev3` values declared in `radio_2056.h`. Each entry contains a frequency in MHz, 37 radio register bytes, and six PHY SFO/bandwidth register values in `struct b43_phy_n_sfo_cfg`.

This chunk includes:

- Tail of `b43_nphy_channeltab_phy_rev3[]`: 8 visible 2.4 GHz entries from 2442 MHz through 2484 MHz. The table started before this chunk.
- `b43_nphy_channeltab_phy_rev4[]`: 124 entries, covering 4920 MHz through 5910 MHz plus 2.4 GHz channels 2412 MHz through 2484 MHz.
- `b43_nphy_channeltab_radio_rev5[]`: 124 entries with the same frequency coverage, tuned for radio rev5.
- `b43_nphy_channeltab_radio_rev6[]`: 124 entries with the same frequency coverage, tuned for radio rev6.
- `b43_nphy_channeltab_radio_rev7_9[]`: 124 entries shared by radio rev7 and rev9.
- `b43_nphy_channeltab_radio_rev8[]`: 124 entries for radio rev8.
- `b43_nphy_channeltab_radio_rev11[]`: 124 entries for radio rev11.

All complete tables in this chunk are organized as ascending 5 GHz frequency entries first, then 2.4 GHz entries. The lookup helper performs a linear search by `.freq`, so table ordering is not required for correctness, but duplicate frequencies would make the first matching entry authoritative.

The `RADIOREGS3(...)` macro maps positional constants into named fields such as `radio_syn_pll_vcocal1`, `radio_syn_pll_refdiv`, `radio_syn_pll_mmd*`, loop filters, logen buffer/mixer values, RX LNA tune values, and TX boost tune values for both chains. The `PHYREGS(...)` macro maps six constants into `phy_bw1a` through `phy_bw6`. This avoids runtime parsing; every table entry is a compile-time initializer.

## Important APIs And Functions

- `b43_nphy_get_inittabs_rev3(struct b43_wldev *dev)`: private selector for `struct b2056_inittabs_pts`. It returns PHY-specific init tables for PHY rev3 and rev4, and otherwise selects by `phy->radio_rev` for radio rev5, rev6, rev7/rev9, rev8, or rev11. Unsupported combinations return `NULL`.
- `b2056_upload_inittab(...)`: private upload loop for one register route. It walks an init table by array index, skips entries without `B2056_INITTAB_ENTRY_OK`, and writes entries marked `B2056_INITTAB_UPLOAD` unless `ignore_uploadflag` forces all valid entries to upload.
- `b2056_upload_inittabs(struct b43_wldev *dev, bool ghz5, bool ignore_uploadflag)`: public radio init helper. It uploads SYN, TX0, TX1, RX0, and RX1 tables through the route constants `B2056_SYN`, `B2056_TX0`, `B2056_TX1`, `B2056_RX0`, and `B2056_RX1`.
- `b2056_upload_syn_pll_cp2(struct b43_wldev *dev, bool ghz5)`: public special-case helper that writes only `B2056_SYN_PLL_CP2` from the selected SYN init table. N-PHY radio setup calls this after channel-table upload so PLL charge-pump state matches the selected band and hardware revision.
- `b43_nphy_get_chantabent_rev3(struct b43_wldev *dev, u16 freq)`: public channel-table lookup. It selects the right channel table using the same rev3/rev4/radio-revision split, then returns the first entry whose `.freq` equals the requested center frequency. Unsupported radio revisions warn and return `NULL`; missing frequencies return `NULL` without a warning.

## Control Flow

Initialization flow:

1. N-PHY 2056 radio initialization calls `b2056_upload_inittabs(dev, 0, 0)` from `phy_n.c`.
2. `b2056_upload_inittabs()` calls `b43_nphy_get_inittabs_rev3()` to select the revision-specific init table bundle.
3. Each of SYN, TX0, TX1, RX0, and RX1 routes is passed to `b2056_upload_inittab()`.
4. `b2056_upload_inittab()` writes `routing | i` to the radio for every valid and upload-enabled entry, choosing `e->ghz5` or `e->ghz2` from the current band flag.

Channel switch flow:

1. `b43_nphy_set_channel()` in `phy_n.c` requests a rev3-style table entry with `b43_nphy_get_chantabent_rev3(dev, channel->center_freq)` for PHY revs 3 through 6.
2. The helper selects a table by `phy->rev` first for rev3/rev4, or by `phy->radio_rev` for later revs using the 2056 radio.
3. It linearly scans the selected static table for the requested frequency.
4. The returned entry is consumed by `b43_chantab_radio_2056_upload()` and `b43_radio_2056_setup()`, which write the SYN PLL, logen, RX LNA, and TX boost fields to radio registers, then apply board-flag and package-specific adjustments.
5. `b2056_upload_syn_pll_cp2()` refreshes PLL CP2 from the init-table data after channel-table upload.

## State And Persistence Behavior

The channel tables and init-table bundles are immutable `static const` data. This chunk does not allocate memory, register sysfs/debugfs files, persist to disk, or retain dynamic state between calls.

State changes happen only through hardware register writes:

- `b2056_upload_inittab()` writes selected init-table values to the 2056 radio register space.
- `b2056_upload_syn_pll_cp2()` writes one SYN PLL register.
- `b43_nphy_get_chantabent_rev3()` has no side effects except `B43_WARN_ON(1)` on unsupported radio revisions.

The caller-owned `struct b43_wldev` and `struct b43_phy` provide all selection state. In particular, `dev->phy.rev`, `dev->phy.radio_rev`, and the `ghz5` flag are trusted to describe the current hardware and operating band.

## Dependencies And Integration Points

Direct dependencies:

- `radio_2056.h`: register route constants (`B2056_SYN`, `B2056_TX0`, `B2056_RX0`, etc.), per-register offsets such as `B2056_SYN_PLL_CP2`, `struct b43_nphy_channeltab_entry_rev3`, and function prototypes.
- `b43.h` and `phy_common.h`: `struct b43_wldev`, `struct b43_phy`, warning macros, radio access helpers, and common PHY definitions.
- Linux kernel helpers and types: `u8`, `u16`, `bool`, and `ARRAY_SIZE`.

Main consumers:

- `phy_n.c:b43_radio_init2056()` calls `b2056_upload_inittabs()` during 2056 radio initialization.
- `phy_n.c:b43_nphy_set_channel()` calls `b43_nphy_get_chantabent_rev3()` for N-PHY rev3+ 2056 channel changes.
- `phy_n.c:b43_chantab_radio_2056_upload()` writes every radio field from the selected channel table entry into actual hardware registers.
- `phy_n.c:b43_radio_2056_setup()` calls the channel upload helper, refreshes CP2 with `b2056_upload_syn_pll_cp2()`, and layers board-flag/package workarounds over the table values.

## Risks And Edge Cases

- Hardware-revision selection is exact. PHY rev3 and rev4 bypass `radio_rev`, while later supported PHYs depend on radio revisions 5, 6, 7, 8, 9, or 11. Any new 2056 radio revision without a table triggers `B43_WARN_ON(1)` and returns `NULL`, causing channel setup or init upload to fail quietly at the caller level.
- `b2056_upload_syn_pll_cp2()` indexes `pts->syn[B2056_SYN_PLL_CP2]` without checking `syn_length`. The existing tables are expected to cover that register; a future shortened table would risk an out-of-bounds read.
- `b2056_upload_inittab()` derives radio addresses as `routing | i`. This relies on init-table indices matching the low register offsets from `radio_2056.h`; changing enum/register values or sparse table shape can redirect writes to wrong hardware registers.
- The `ignore_uploadflag` path writes every valid entry, including `NOUPLOAD` defaults. That is intentional for forced full upload scenarios, but using it at the wrong time could overwrite calibration or runtime-tuned values that normal init leaves untouched.
- Channel lookup is linear over 124 entries. This is small and simple, but it means duplicate `.freq` entries are not detected and the first match wins.
- The 5 GHz tables include many frequencies outside ordinary regulatory channel lists. Correct exposure to userspace depends on higher mac80211/cfg80211 regulatory filtering; this table only says the hardware programming values exist.
- The chunk starts inside `b43_nphy_channeltab_phy_rev3[]`, so final per-file reconciliation should merge the preceding part of that table with this tail before making whole-table claims.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware/driver behavior oriented:

- Build coverage should catch malformed initializers, missing struct fields, bad prototypes, and route/register macro type issues.
- Runtime probe of PHY rev3/rev4 and radio rev5/6/7/8/9/11 devices should not trigger `B43_WARN_ON(1)` in `b43_nphy_get_inittabs_rev3()` or `b43_nphy_get_chantabent_rev3()`.
- Channel-switch tests should cover representative 2.4 GHz channels (2412, 2437, 2462, 2484 MHz) and 5 GHz channels across the low/mid/high ranges (for example 4920, 5180, 5500, 5745, 5910 MHz) and confirm no `-ESRCH` from `b43_nphy_set_channel()` for supported frequencies.
- Register tracing or hardware instrumentation can verify that channel changes write SYN PLL, logen, RX LNA, TX boost, and PHY bandwidth values matching the selected table entry and that board-flag workarounds intentionally override only their documented registers.
- Forced-init tests using `ignore_uploadflag=true` should be treated as high-risk hardware tests because they exercise writes that normal init suppresses.
