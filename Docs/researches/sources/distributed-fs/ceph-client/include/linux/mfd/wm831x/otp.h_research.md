<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/otp.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/otp.h

## Purpose
`otp.h` describes the WM831x one-time-programmable memory register window. It covers unique ID words, factory OTP identity and trim fields, customer OTP identity/finality, and DBE check-data readback.

## Important APIs, types, and functions
The driver-facing entry points are `wm831x_otp_init(struct wm831x *wm831x)` and `wm831x_otp_exit(struct wm831x *wm831x)`. Register macros define repeated `WM831X_UNIQUE_ID_*` fields for `0x7800` through `0x7807`, factory fields such as `WM831X_OTP_FACT_ID_MASK`, `WM831X_OTP_FACT_FINAL`, DC trim masks, `WM831X_CHIP_ID_MASK`, oscillator/bandgap trims, child I2C address fields, charge trim fields, customer fields `WM831X_OTP_AUTO_PROG`, `WM831X_OTP_CUST_ID_MASK`, and `WM831X_OTP_CUST_FINAL`.

## Control flow
Initialization code can read OTP registers to discover chip identity, trim data, and customer-programmed behavior. Exit tears down any OTP-created state. The header itself performs no reads or writes; it supplies the bit definitions for register accessors in the core.

## State and persistence behavior
OTP contents are persistent in hardware and normally immutable after finalization bits are set. Runtime driver state should treat these registers as calibration and identity inputs, not as ordinary mutable configuration.

## Dependencies and integration points
The prototypes depend on `struct wm831x` from the WM831x core. OTP values influence regulator trims, oscillator/bandgap calibration, child addressing, and customer-specific startup behavior.

## Risks and test signals
Risks include treating duplicate `WM831X_UNIQUE_ID_*` macro names as register-specific constants, writing to final OTP areas accidentally, and mishandling customer/factory final bits. Test signals are read-only register dumps, chip-ID/unique-ID exposure tests, calibration application checks, and fault-injection around init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/otp.h -->
