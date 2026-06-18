# sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.h Research

## Purpose
`ptp_fc3.h` defines private constants and state for the FemtoClock3 PHC driver.

## Important APIs, Types, And Functions
It defines default firmware name `idtfc3.bin`, maximum frequency offset `MAX_FFO_PPB`, TDC polling period `TDC_GET_PERIOD`, and `struct idtfc3`. The state struct contains PTP caps and clock pointer, device and parent MFD/regmap references, shared lock, hardware parameter cache, TDC and time-reference frequencies, sub-sync timing, LPF mode, software timecounter fields, update/write timeouts, and measured TOD write overhead.

## Control Flow
There is no executable code. `ptp_fc3.c` fills the structure during probe and uses it across all PTP operations and aux worker runs.

## State And Persistence
The struct is the driver's in-memory representation of hardware configuration and current PHC time. `last_counter` and `ns` are especially important because they extend a hardware counter into PTP time.

## Dependencies And Integration Points
The header depends on PTP clock types, regmap, and `ktime`. It also assumes register-derived `struct idtfc3_hw_param` from the included FC3 MFD register header.

## Risks
If hardware parameters are stale or firmware parsing does not update them, all time conversions based on `ns_per_counter` and `ns_per_sync` are affected. The header's limits must match the chip's actual DCO/TDC capabilities.

## Test Signals
Validation should assert initialized fields after probe, sane derived periods, max adjustment consistency with PTP caps, and robust behavior if firmware leaves optional parameters at defaults.
