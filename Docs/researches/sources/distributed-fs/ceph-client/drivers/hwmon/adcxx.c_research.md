# sources/distributed-fs/ceph-client/drivers/hwmon/adcxx.c

## Purpose
`adcxx.c` is an SPI hwmon driver for National Semiconductor ADCxxS converter families. It exposes raw analog input channels scaled to millivolts using a writable reference value.

## Important APIs, Types, And Functions
`struct adcxx` stores the hwmon device pointer, mutex, channel count, and reference voltage. `adcxx_show` performs the SPI conversion read and scales the 12-bit raw value by `reference`. `adcxx_min_show`, `adcxx_max_show`, and `adcxx_max_store` expose reference range metadata. `adcxx_name_show` emits the SPI modalias. Probe manually creates `name`, `in_min`, `in_max`, and as many `inN_input` files as the matched channel count, then registers hwmon.

## Control Flow
Probe derives channel count from the SPI ID (`adcxx1s`, `adcxx2s`, `adcxx4s`, `adcxx8s`), initializes a default 3300 mV reference, creates the relevant sysfs files under lock, and calls `hwmon_device_register`. For single-channel devices, reads use `spi_read`; multi-channel devices send the channel index shifted into the command byte with `spi_write_then_read`. Remove unregisters hwmon and removes the same files.

## State And Persistence
The only mutable state is the in-memory reference voltage set through `in_max`; it is not written to hardware and is lost when the device unbinds. There is no sample cache. Each `in*_input` read triggers a fresh SPI transfer.

## Dependencies And Integration Points
The driver depends on SPI synchronous transfer APIs, legacy manual sysfs file management, hwmon registration, and SPI device IDs. Userspace controls scaling through `in_max`, reads fixed `in_min` as zero, and reads `in0_input` through `in7_input` depending on variant.

## Risks And Test Signals
Risks include absence of reference range validation, no explicit masking of unused ADC bits before scaling, manual sysfs cleanup correctness, and shared mutex use during remove versus reads. Test signals include correct number of channel files per ID, SPI error propagation, scaling with default and user-provided references, successful cleanup after partial file creation failure, and correct command byte generation for multi-channel devices.
