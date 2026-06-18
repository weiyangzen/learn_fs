# sources/distributed-fs/ceph-client/arch/powerpc/boot/serial.c

Purpose: selects and exposes the proper serial backend as generic console_ops and supports command-line editing.

Important APIs/types/functions: types `serial_console_data`, `serial_console_data`, `serial_console_data`, `serial_console_data`; functions `serial_open`, `serial_write`, `serial_edit_cmdline`, `serial_close`, `serial_console_init`; assembly labels/symbols `err_out`, `err_out`. Source size is 153 lines / 3489 bytes.

Implementation notes: The dispatcher follows /chosen stdout-path, checks device_type and compatible strings, initializes ns16550/CPM/PSC/OPAL backends, and exposes write/open/close/edit_cmdline through console_ops.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `string.h`, `stdio.h`, `io.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
