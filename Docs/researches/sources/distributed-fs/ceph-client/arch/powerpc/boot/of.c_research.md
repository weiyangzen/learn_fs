# sources/distributed-fs/ceph-client/arch/powerpc/boot/of.c

Purpose: initializes Open Firmware based booting and selects OF/FDT behavior for common start().

Important APIs/types/functions: functions `of_image_hdr`, `of_platform_init`, `platform_init`; macros `PROG_START`, `RAM_END`, `ONE_MB`. Source size is 93 lines / 2129 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state includes dt_ops callbacks, the relocated FDT buffer or PROM pointer, and loader_info fields used until final kernel entry.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
