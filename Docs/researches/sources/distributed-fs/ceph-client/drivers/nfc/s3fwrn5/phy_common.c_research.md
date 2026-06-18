# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.c

## Purpose
`phy_common.c` provides GPIO-based wake and mode/power sequencing shared by S3FWRN5 I2C and S3FWRN82 UART physical layers.

## Important APIs and functions
- `s3fwrn5_phy_set_wake()` sets the firmware wake GPIO and waits when waking.
- `s3fwrn5_phy_power_ctrl()` changes COLD/NCI/FW mode, drives enable and wake GPIOs, and performs required 20 ms waits.
- `s3fwrn5_phy_set_mode()` wraps power control in the common mutex.
- `s3fwrn5_phy_get_mode()` returns the current mode under the same mutex.

## Control flow
Mode changes first short-circuit if already in the requested mode. Otherwise the function updates `phy->mode`, asserts enable, drops wake, asserts wake for firmware mode, and for non-COLD modes pulses enable low after waits. Wake control is separate and can be used by NCI open/close and firmware update steps.

## State and persistence
The only state is the in-memory `phy_common.mode` plus hardware GPIO output levels. There is no persistent state.

## Dependencies and integration points
The helpers depend on GPIO descriptors, mutexes, delays, and `struct phy_common`. They are exported for transport modules and used through `s3fwrn5_phy_ops`.

## Risks
Mode is updated before GPIO sequencing completes, so failures are not representable because GPIO set calls are void for already acquired descriptors. Fixed waits may be marginal on slow boards. `s3fwrn5_phy_set_wake()` locks the same common mutex as mode changes, preventing direct races but making wake latency blocking.

## Test signals
Tests should verify GPIO transitions for COLD/NCI/FW, no-op same-mode transitions, wake timing expectations, and concurrent wake/mode calls from send/open/firmware paths.
