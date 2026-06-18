# sources/distributed-fs/ceph-client/include/linux/jz4740-adc.h

## Purpose
Declares the shared configuration interface and register bit definitions for the Ingenic JZ4740 ADC MFD device.

## Important APIs, Types, And Functions
The single exported function is `jz4740_adc_set_config(struct device *dev, uint32_t mask, uint32_t val)`, used by child cells to update masked bits in the shared configuration register. Macros define config bits and field encoders for pen-down/sample, external input, data count, DMA, XYZ mode, sample count, clock divider, and battery measurement.

## Control Flow
There is no inline runtime logic. Child drivers compute a mask/value pair and delegate the register update to the ADC core driver through `jz4740_adc_set_config()`.

## State And Persistence
State is hardware register configuration on the ADC device. It persists until changed by a driver or reset by hardware/power management.

## Dependencies And Integration Points
Depends on `struct device` and bit macros from the broader kernel include context. It integrates with MFD child drivers for touchscreen, battery, or ADC channels on JZ4740 SoCs.

## Risks
The macro `JZ_ADC_CONFIG_XYZ_OFFSET(dnum)` expands using `xyz`, not its parameter name, which is a compile-time hazard if used. Mask/value mismatches can corrupt unrelated shared register fields. No locking contract is visible in this header, so concurrency must be handled by the implementation.

## Test Signals
Build coverage should exercise every field encoder, especially the XYZ macro. Driver tests should validate masked register updates, concurrent child updates, suspend/resume restoration, and hardware sampling modes.
