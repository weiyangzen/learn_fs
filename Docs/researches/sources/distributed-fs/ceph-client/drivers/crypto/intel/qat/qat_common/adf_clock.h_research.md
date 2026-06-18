# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.h

## Purpose
This header declares the common QAT clock-measurement helper used by device-specific hardware-data files.

## Important APIs, Types, And Functions
The only public API is `adf_dev_measure_clock(struct adf_accel_dev *accel_dev, u32 *frequency, u32 min, u32 max)`.

## Control Flow
No executable flow exists. The implementation performs admin timestamp synchronization and range validation.

## State And Persistence Behavior
The header defines no state. Callers pass an output pointer and store results elsewhere.

## Dependencies And Integration Points
It depends on `struct adf_accel_dev` from the common device model. It is included by Gen2 hardware-data files that need measured AE frequency.

## Risks
Callers must invoke it only after admin communication is available and must provide correct min/max frequencies.

## Test Signals
Build coverage and successful C3xxx/C62x clock measurement validate the declaration.
