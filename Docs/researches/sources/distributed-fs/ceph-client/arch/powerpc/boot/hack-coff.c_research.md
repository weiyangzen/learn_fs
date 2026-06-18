# sources/distributed-fs/ceph-client/arch/powerpc/boot/hack-coff.c

Purpose: post-processes AIX COFF zImage output so legacy RS/6000 firmware accepts the boot image.

Important APIs/types/functions: types `external_filehdr`, `external_scnhdr`; functions `main`; assembly labels/symbols `readerr`; macros `AOUT_MAGIC`, `get_16be(x)`, `put_16be(x, v)`, `get_32be(x)`. Source size is 80 lines / 2187 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdio.h`, `stdlib.h`, `unistd.h`, `fcntl.h`, `string.h`, `rs6000.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
