# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.c

## Purpose
This file implements the two cx23418 I2C adapters using the Linux bit-banging algorithm over CX23418 I2C registers, and registers card subdevices on those buses.

## Important APIs, Types, and Functions
Public functions are `init_cx18_i2c()`, `exit_cx18_i2c()`, `cx18_i2c_register()`, and `cx18_find_hw()`. Bit operations are `cx18_setscl()`, `cx18_setsda()`, `cx18_getscl()`, and `cx18_getsda()`. Static maps associate cx18 hardware flags with default addresses, bus indices, and device names.

## Control Flow
Initialization builds two `i2c_adapter` and `i2c_algo_bit_data` instances, resets/enables I2C hardware, clears stale interrupts, initializes SCL/SDA high, resets downstream I2C chips through GPIO, and registers both bit-banged buses. Subdevice registration handles tuner probing across radio/demod/TV address lists, creates Z8F0811 IR devices with platform data, and creates fixed-address V4L2 I2C subdevs such as CS5345. Exit disables hardware lines and unregisters adapters.

## State and Persistence
Per-device adapter, algorithm, and callback data live in `struct cx18`. Subdevices registered on the adapters become children of the V4L2 device until cleanup. Hardware line state is volatile.

## Dependencies and Integration Points
The file depends on I2C bit-algo, V4L2 I2C helpers, card I2C tables, GPIO reset subdevice, IRQ register constants, and IR keyboard platform data. It is central to tuner, demod, EEPROM, CS5345, and IR integration.

## Risks and Edge Cases
Hardware flag bit positions must match address/bus/name arrays. Tuner registration considers success if any of three scanned groups succeeds. I2C hardware reset values are magic constants. There is a TODO for interrupt-based I2C, but current logic is polling/bit-banged.

## Test Signals
Use `i2cdetect`-style debug or driver logs to confirm two adapters, verify EEPROM/tuner/CS5345/IR discovery per board, test failure cleanup when second bus registration fails, and confirm GPIO reset improves device discovery.
