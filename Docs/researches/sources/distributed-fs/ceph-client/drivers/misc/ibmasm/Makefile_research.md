# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/Makefile

## Purpose
The `ibmasm/Makefile` builds the IBM ASM service processor driver object from its component files and conditionally includes UART support.

## Important APIs, Types, and Functions
It defines `obj-$(CONFIG_IBM_ASM) := ibmasm.o`, lists core objects `module.o`, `ibmasmfs.o`, `event.o`, `command.o`, `remote.o`, `heartbeat.o`, `r_heartbeat.o`, `dot_command.o`, and `lowlevel.o`, and adds `uart.o` when `CONFIG_SERIAL_8250` is enabled.

## Control Flow
Kbuild links the listed objects into one `ibmasm.o` module/built-in object. The order reflects module entry points first, then filesystem/event/command/remote/heartbeat/protocol/low-level support.

## State and Persistence
No runtime state exists in the Makefile.

## Dependencies and Integration Points
It integrates with Kbuild configuration symbols `CONFIG_IBM_ASM` and `CONFIG_SERIAL_8250`.

## Risks and Edge Cases
If optional UART code is excluded, the inline stubs in `ibmasm.h` must satisfy all references. Adding new source files requires updating this list or symbols will be missing.

## Test Signals
Build with `CONFIG_IBM_ASM=m/y` and with `CONFIG_SERIAL_8250` enabled and disabled to validate both object compositions.
