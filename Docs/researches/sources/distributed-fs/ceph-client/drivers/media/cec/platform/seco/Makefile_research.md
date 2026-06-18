# sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/Makefile

## Purpose
This Makefile builds the SECO x86 CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_SECO` to `seco-cec.o`.

## Control Flow
Kbuild includes the SECO driver when the config option is enabled as a module or built-in.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The file depends on the surrounding Kconfig to select the driver. The implementation handles ACPI, GPIO IRQ, SMBus I/O ports, CEC, and optional RC input.

## Risks and Test Signals
Build coverage should confirm the object is linked only when `CONFIG_CEC_SECO` is enabled.
