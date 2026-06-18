# sources/distributed-fs/ceph-client/arch/powerpc/boot/stdio.c

Purpose: implements minimal printf/sprintf/vsprintf and numeric formatting for the boot wrapper.

Important APIs/types/functions: functions `strnlen`, `skip_atoi`, `number`, `vsprintf`, `sprintf`, `printf`; macros `do_div(n, base)`, `do_div(n,base)`, `ZEROPAD`, `SIGN`, `PLUS`, `SPACE`, `LEFT`, `SPECIAL`, `LARGE`. Source size is 354 lines / 7190 bytes.

Implementation notes: Formatting supports common integer, string, character, pointer, width, precision, and qualifier cases. On 32-bit builds 64-bit division is delegated to div64.S.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `string.h`, `stdio.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
