<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phyreg_n.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phyreg_n.h

## Purpose

`phyreg_n.h` defines N-PHY table IDs, register bit masks, RF sequence command values, classifier/IQ/sample-control bits, and small register-address selector macros. It is the symbolic bridge between N-PHY control code and the numeric PHY table/register layout.

## Important APIs, Types, And Functions

There are no functions or types. Important macro groups include:

- `NPHY_TBL_ID_*` constants for gain, RF sequence, AFECTRL, antenna switch, IQ local, noise variance, sample play, per-core TX power-control, and PAPD epsilon/scalar tables.
- Band and RF-control masks such as `NPHY_BandControl_currentBand`, `RFCC_CHIP0_PU`, `RFCC_POR_FORCE`, `RIFS_ENABLE`, `BPHY_BAND_SEL_UP20`, and `NPHY_MLenable`.
- RF sequence mode, trigger, status, operation index, and command constants for pre-rev3 and rev3 hardware.
- Classifier, IQ flip, sample command, IQ estimation, TX power index, RSSI selector, rail selector, and rev7 RF-control override/gain-code masks.
- `NPHY_Iqest*Acc*()` macros that choose per-core IQ estimator accumulator register addresses.

## Control Flow

The file has no runtime control flow and no include guard. It is a macro-only header; control decisions happen in callers such as `phy_n.c`, which use the constants under PHY revision and core-selection branches.

## State And Persistence

No software state is declared. The constants identify hardware state fields and tables whose values are programmed by N-PHY initialization, calibration, gain control, IQ estimation, and power-control routines.

## Dependencies And Integration Points

`phytbl_n.c` table descriptors use compatible table IDs, and `phy_n.c` writes those tables with `wlc_phy_write_table_nphy()`. The RF sequence and override constants are consumed by N-PHY state-machine setup and calibration paths. The per-core accumulator macros are used when collecting IQ/power estimates for a selected receive/transmit chain.

## Risks And Edge Cases

- No include guard means repeated inclusion is normally harmless for identical macros but still relies on consistent definitions and compiler tolerance for redefinitions.
- Table ID mismatches with `phytbl_n.c` descriptors would load valid data into the wrong hardware table.
- Pre-rev3 and rev3 RF sequence command values differ; using the wrong macro family can corrupt the RF transition program.
- The per-core address macros assume only core `0` and nonzero/other core; callers must not pass arbitrary indexes expecting more than two distinct address sets.

## Test Signals

Compile `phy_n.c` users, then validate N-PHY initialization on rev0, rev3, rev7, and rev16 hardware paths if available. Runtime signals include successful table programming, RF sequence completion, IQ estimate collection, gain updates, and absence of PHY calibration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phyreg_n.h -->
