# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.h

## Purpose
`lis3lv02d.h` defines the shared internal interface for LIS3-family accelerometer core and bus glue. It lists register addresses, chip IDs, control/status bit definitions, axis conversion, and the central `struct lis3lv02d`.

## Important APIs, types, and functions
Important enums include `lis3_reg`, `lis302d_reg`, `lis3lv02d_reg`, `lis3_who_am_i`, sensor type identifiers, control-register bit sets, status bits, freefall/wakeup bits, click bits, and regulator states. `union axis_conversion` maps hardware axes to logical axes. `struct lis3lv02d` carries bus callbacks, ODR tables, register cache, input/faux/misc devices, regulators, IRQ state, platform data, mutex, and optional OF node. Function prototypes expose the core to bus transports, and `extern struct lis3lv02d lis3_dev` declares the singleton.

## Control flow
The header provides no executable flow but defines how transports call into the core: they fill `init`, `read`, `write`, optional `blkread`, optional `reg_ctrl`, bus private data, IRQ, axis conversion, platform data, and PM device before calling `lis3lv02d_init_device`.

## State and persistence
The state schema includes hardware register context (`regs`, `reg_cache`, `regs_stored`), runtime sensor parameters (`whoami`, `scale`, `odrs`, `odr_mask`, `shift_adj`), OS integration objects (`idev`, `fdev`, `miscdev`), and interrupt counters. This state persists for the lifetime of the bound transport device.

## Dependencies and integration points
The header depends on faux devices, input, regulators, miscdevice, and public platform data from `linux/lis3lv02d.h`. It is included by the shared core plus I2C/SPI transport files.

## Risks
Register and bit definitions are ABI-like for hardware; incorrect values break multiple transports. The singleton declaration encodes the driver's single-device assumption. Adding a new sensor variant requires consistent updates to IDs, control bits, data-reading behavior, and core initialization.

## Test signals
Build coverage should include both transports and OF/platform-data configurations. Runtime tests should confirm each register definition used by initialization, IRQ configuration, and sysfs/selftest paths matches the target sensor datasheet.
