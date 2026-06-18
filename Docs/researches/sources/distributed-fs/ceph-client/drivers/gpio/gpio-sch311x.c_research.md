# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch311x.c

## Purpose
This driver detects SMSC SCH3112/SCH3114/SCH3116 Super-I/O chips, creates a platform device for the runtime register base, and registers six eight-line GPIO blocks with per-line configuration registers.

## Important APIs, Types, and Functions
Detection uses `sch311x_sio_enter/exit/inb/outb()` to access Super-I/O config space at known ports. `struct sch311x_gpio_block_def` describes each block's data register, per-line config registers, and static GPIO base. `struct sch311x_gpio_block` contains the gpio chip, register addresses, runtime base, and lock. GPIO callbacks implement request/free, get/set, direction, direction query, and open-drain/push-pull config.

## Control Flow
Module init scans four Super-I/O config ports, enters config mode, checks device ID, selects logical device 0x0a, reads the runtime base, registers the platform driver, then adds a platform device. Probe reserves the contiguous GP1-GP6 data registers, allocates private state, and registers six gpio chips. Per-line request reserves its config byte and rejects unavailable lines with zero config register entries.

## State and Persistence
GPIO direction, value, and open-drain state live in Super-I/O runtime registers. The driver stores static register tables and no PM state. Platform device lifetime is managed manually at module init/exit.

## Dependencies and Integration Points
It depends on x86 I/O port APIs, Super-I/O config conventions, platform devices with private data, gpiolib, pinconf config parameters for drive mode, and static GPIO bases 10/20/30/40/50/60.

## Risks
Static base numbering and six separate chips reflect older userspace expectations but can conflict with dynamic allocation assumptions. Missing config-register entries are only rejected in `.request()`, so direct internal use before request would be unsafe. The init path must unregister the platform driver if platform device creation fails. There is no IRQ support.

## Test Signals
Test detection for all three device IDs, inactive logical-device warning, runtime-base absence, unavailable GPIO request rejection, per-block data register reservation, direction get/set, open-drain and push-pull config, and module exit cleanup.
