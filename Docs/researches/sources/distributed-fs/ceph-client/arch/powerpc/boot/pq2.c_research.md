# sources/distributed-fs/ceph-client/arch/powerpc/boot/pq2.c

Purpose: derives PowerQUICC II clocks and patches CPU, bus, timebase, brg, and CPM clock properties.

Important APIs/types/functions: functions `pq2_get_clocks`, `pq2_set_clocks`, `pq2_fixup_clocks`; macros `PQ2_SCCR`, `PQ2_SCMR`. Source size is 99 lines / 2273 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `types.h`, `fsl-soc.h`, `pq2.h`, `stdio.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
