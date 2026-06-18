# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31-eusb2.c

## Purpose
This driver implements a Qualcomm M31 eUSB2 high-speed PHY for the SM8750 binding `qcom,sm8750-m31-eusb2-phy`. It exposes a generic PHY provider, sequences regulators, a reference clock, reset, and MMIO register programming, and also delegates mode/init/exit work to a downstream repeater PHY obtained from the device tree.

## Important APIs, Types, and Functions
The core data model is `struct m31eusb2_phy`, which stores the generic `struct phy`, MMIO base, match data, regulator bulk array, clock, reset, and repeater PHY. `struct m31_eusb2_priv_data` points at three register tables: setup, override, and reset sequences. `m31eusb2_phy_write_readback()` masks and writes an individual register field, then verifies the write by reading it back. `m31eusb2_phy_write_sequence()` applies table entries with left-shifted field values based on `__ffs(mask)`. PHY ops are `m31eusb2_phy_init()`, `m31eusb2_phy_exit()`, and `m31eusb2_phy_set_mode()`.

## Control Flow
Probe allocates driver state, reads match data, maps MMIO resource 0, gets an exclusive reset, a clock, two regulators (`vdd`, `vdda12`), creates the PHY, obtains the repeater via `devm_of_phy_get_by_index()`, then registers `of_phy_simple_xlate`. Init enables regulators, initializes the repeater, enables the ref clock, asserts/deasserts the PHY reset, writes setup registers, programs `FSEL` for 38.4 MHz, applies override tuning, and finally applies the reset-release sequence. Exit disables the clock, regulators, and repeater. Mode changes are cached locally and forwarded to the repeater through `phy_set_mode_ext()`.

## State and Persistence
Runtime state is in the devm-managed `m31eusb2_phy` object and in hardware registers. The only remembered software mode is `phy->mode`, with no persistence across reprobe or suspend. The table-driven register writes define power-on hardware state; shutdown only disables resources and exits the repeater, so register retention depends on platform power/reset behavior.

## Dependencies and Integration Points
The driver depends on the Linux PHY, platform, reset, clock, regulator, MMIO, bitfield, and device-tree match-data APIs. Its integration contract is the DT compatible string, MMIO resource, one unnamed reset, one unnamed clock, `vdd` and `vdda12` supplies, and a child or referenced repeater PHY at index 0. It is part of the Qualcomm PHY driver set but does not reuse the QMP table helper.

## Risks and Edge Cases
`m31eusb2_phy_init()` ignores return values from the three table-write calls and the direct `FSEL` write; write/readback failures therefore do not currently abort init. The error path after `phy_init(repeater)` returns `0` after disabling regulators, masking clock-enable or repeater-init failures in some branches. Register values are tightly coupled to SM8750 M31 eUSB2 hardware and to the 38.4 MHz FSEL assumption. Repeater failures are user-visible because mode changes and init/exit are forwarded.

## Test Signals
Useful test signals are successful probe with all resources present, regulator/clock/reset sequencing visible in boot logs, no write/readback error messages during init, successful repeater init/exit, and working USB high-speed enumeration through the eUSB2 path. Negative tests should cover missing supplies, missing repeater, failed clock enable, and bad register readback if fault injection is available.
