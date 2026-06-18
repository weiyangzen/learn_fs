# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_a.h

## Purpose
`phy_a.h` defines A/OFDM PHY register addresses, bit masks, OFDM table selector encodings, and table access function prototypes for b43. It is a register-contract header used by A/G PHY code that needs OFDM baseband, gain, RSSI, TSSI, DAC, antenna diversity, and threshold tables.

## Important APIs, Types, and Functions
- Register macros wrap raw offsets with `B43_PHY_OFDM()` routing from `phy_common.h`.
- Important registers include A-PHY versioning, baseband config, powerdown, CRS thresholds, LNA/HPF and LPF gain controls, antenna dwell/settle, IQ balance, TX DC bias, OFDM table control/data, hardware power TSSI control, ADC control, idle TSSI, temperature sense, NRSSI threshold, clip thresholds, and diversity gain registers.
- OFDM table helpers include `B43_OFDMTAB(number, offset)` and named table selectors such as AGC, gain, noise scale, rotor, DAC, DC, power dynamic, LNA gain, RSSI, TSSI, and revision-specific tables.
- Prototypes provide 16-bit and 32-bit OFDM table read/write access.

## Control Flow
There is no direct control flow. Consumer code writes `B43_PHY_OTABLECTL` with one of the encoded table selectors and then accesses `B43_PHY_OTABLEI/Q` or uses the declared helper functions.

## State and Persistence
The header owns no driver state. It names hardware registers and tables whose values persist in the PHY until changed by init, calibration, channel switching, or power-control routines.

## Dependencies and Integration Points
- Depends on `phy_common.h` for PHY register routing macros and `struct b43_wldev`.
- Used by G-PHY and OFDM/A-PHY code paths for calibration, gain tables, noise/TSSI handling, and antenna-diversity programming.
- The OFDM table accessors are implemented elsewhere and provide the safer integration point for table operations.

## Risks and Edge Cases
- Many names carry FIXME/TODO markers, indicating incomplete hardware documentation; accidental reuse of poorly named registers can create hard-to-debug RF behavior.
- Table selector encodings combine table number and offset bits; wrong offsets can corrupt unrelated OFDM tables.
- Revision-specific table aliases must be chosen carefully because A/G PHY revisions interpret some table numbers differently.

## Test Signals
- Build coverage should include PHY_G/A-OFDM users that include this header.
- RF regression signals include broken channel calibration, bad RSSI/TSSI, degraded OFDM rates, antenna diversity regressions, and unexpected PHY errors after table changes.
