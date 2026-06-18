# sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc52xx-psc.c

Purpose: implements an MPC5200 PSC UART backend for the generic boot-wrapper serial console.

Important APIs/types/functions: functions `psc_open`, `psc_putc`, `psc_tstc`, `psc_getc`, `mpc5200_psc_console_init`; macros `MPC52xx_PSC_SR`, `MPC52xx_PSC_SR_RXRDY`, `MPC52xx_PSC_SR_RXFULL`, `MPC52xx_PSC_SR_TXRDY`, `MPC52xx_PSC_SR_TXEMP`, `MPC52xx_PSC_BUFFER`. Source size is 65 lines / 1503 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `types.h`, `io.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
