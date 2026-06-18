# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_mpu.h

## Purpose
Defines the PowerMac G5 MPU EEPROM calibration layout and provides `wf_get_mpu()` for model drivers that need CPU thermal, fan, pump, and PID calibration data.

## Important APIs, Types, And Functions
`struct mpu_data` describes the 0xa0-byte CPU card calibration blob, including target/max temperatures, max power adjustment, PID gains, diode calibration, heatsink parameters, fan min/max RPMs, pump hints in `processor_part_num`, serial numbers, and checksums. `wf_get_mpu(int cpu)` builds a fixed OF path to `/u3@0,f8000000/i2c@f8001000/cpuid@a0` or `cpuid@a2`, fetches the `cpuid` property, drops the node reference, and returns a pointer to the property data.

## Control Flow
Consumers call `wf_get_mpu()` at model-driver init or fan discovery time. PM72 and RM31 require MPU data before registering their platform drivers, while FCU controls use it opportunistically to refine fan and pump limits.

## State, Dependencies, And Integration
The header has no mutable state. It depends on Open Firmware device-tree APIs and PowerMac-specific immutable device trees. Integration points include `windfarm_fcu_controls.c`, `windfarm_pm72.c`, and `windfarm_rm31.c`.

## Risks And Test Signals
The helper intentionally returns a pointer after `of_node_put()`, relying on non-removable PowerMac OF nodes. It hardcodes U3/I2C paths and unit-address assumptions, so it is not generic across other Apple layouts. Test signals include MPU lookup for CPU 0/1, sane PID history and fan min/max fields, pump fallback behavior when EEPROM values are invalid, and failure paths when MPU data is absent.
