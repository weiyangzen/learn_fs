# sources/distributed-fs/ceph-client/arch/m68k/mac/Makefile

## Purpose
Defines the core object list for classic Macintosh m68k platform support.

## APIs, Flow, And State
The file contributes `config.o`, `macints.o`, `iop.o`, `via.o`, `oss.o`, `psc.o`, `baboon.o`, `macboing.o`, and `misc.o` to `obj-y`. There is no runtime state; its control flow is Kbuild object selection.

## Dependencies And Integration
This Makefile is consumed by the m68k architecture build. The selected objects collectively provide machine detection, machdep hooks, interrupt controllers, VIA/OSS/PSC/IOP support, Baboon IDE interrupt fan-out, sound, PRAM/RTC, reset, and poweroff services.

## Risks And Test Signals
Because every object is unconditional within the Mac directory, compile-time dependencies must be internally guarded by `CONFIG_*` checks and runtime model detection. Missing an object breaks early boot or device registration. Test signals are Mac m68k defconfig builds and successful boot through `config_mac()`, IRQ setup, timer init, and platform-device registration.
