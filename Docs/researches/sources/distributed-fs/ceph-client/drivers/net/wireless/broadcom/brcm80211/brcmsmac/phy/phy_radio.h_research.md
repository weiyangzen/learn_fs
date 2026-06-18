<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_radio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_radio.h

## Purpose

`phy_radio.h` is a hardware register map header for Broadcom radio cores used by the brcmsmac PHY layer. It names radio register offsets, read-offset encodings, core-selection constants, power/RSSI/calibration bit masks, and per-core 2055/2056/2057 register addresses. It lets PHY calibration and channel code use symbolic names when programming RF analog blocks.

## Important APIs, Types, And Functions

The file defines no functions or types. Its important symbols are macro families:

- Common symbols such as `RADIO_IDCODE`, `RADIO_DEFAULT_CORE`, RSSI/TSSI control bits, and read-offset constants like `RADIO_2055_READ_OFF`, `RADIO_2057_READ_OFF`, and `RADIO_2064_READ_OFF`.
- `RADIO_2055_*` register offsets and masks for PLL, VCO, LGEN, RX/TX, RSSI, calibration, core1/core2 gain, and gain-boost controls.
- `RADIO_MIMO_CORESEL_*` values for selecting one or more MIMO RF cores.
- `RADIO_2064_REG000` through `RADIO_2064_REG130`, a dense numeric map for the 2064 radio.
- `RADIO_2056_*` block selectors (`SYN`, `TX0`, `TX1`, `RX0`, `RX1`, `ALLTX`, `ALLRX`) and synth/TX/RX local register offsets plus power-up and RSSI selection masks.
- `RADIO_2057_*` and `RADIO_2057v7_*` offsets for shared, core0, core1, TX IQ/TSSI, AFE, RCCAL, override, and revision-specific registers.

## Control Flow

There is no runtime control flow. Compile-time structure is an include guard `_BRCM_PHY_RADIO_H_` around a large list of constants. Higher-level PHY code combines these addresses with radio read/write helpers and revision checks.

## State And Persistence

The header defines symbolic constants only. It does not store hardware state, but its values address persistent radio hardware registers. Writes through users of these macros can affect RF power-up, calibration, gain, RSSI, TSSI, PLL, and transmit/receive behavior until hardware reset or reprogramming.

## Dependencies And Integration Points

This header integrates with N-PHY and LCN-PHY code that performs low-level radio register reads and writes through brcmsmac PHY helper functions. The constants are consumed by calibration, channel switching, RSSI, TSSI, power control, and RF-sequence logic. It is coupled to actual Broadcom silicon register layouts for 2055, 2056, 2057, and 2064 radio families.

## Risks And Edge Cases

- A wrong numeric constant can silently program the wrong analog register, causing radio failure, poor sensitivity, bad transmit power, or regulatory issues.
- Several radio families and revisions share similarly named registers with different address composition rules; users must combine block selectors and offsets correctly.
- The header provides masks and shifts but no type safety, so accidental use with the wrong radio family is a compile-clean runtime bug.
- Because register effects are hardware-dependent, many changes cannot be validated by ordinary unit tests.

## Test Signals

The best validation is compile coverage plus hardware bring-up: successful attach, channel set, RF calibration completion, stable RSSI/TSSI readings, expected transmit power, and no PHY watchdog/calibration errors. Static review should compare changed addresses against vendor register specs or known-good upstream history.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_radio.h -->
