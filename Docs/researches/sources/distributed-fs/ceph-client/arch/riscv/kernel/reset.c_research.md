<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/reset.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/reset.c

Purpose: Provides architecture reset, halt, and power-off entry points for RISC-V and a weak default power-off loop.

Important APIs/types/functions: Defines exported `pm_power_off`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, and internal `default_power_off()`.

Control flow: Restart, halt, and poweroff call `do_kernel_restart()`, `pm_power_off()` when registered, and finally fall back to an infinite wait loop. Firmware-specific reset/poweroff providers, such as SBI SRST, install `pm_power_off` or reboot notifiers elsewhere.

State and persistence: The only global state is the `pm_power_off` function pointer. These paths are terminal and do not persist data.

Dependencies and integration points: Hooks generic kernel reboot/poweroff paths and is completed by platform firmware code in `sbi.c` or board drivers.

Risks: If no firmware power-off implementation registers, halt/poweroff spins forever. Late replacement of `pm_power_off` must be safe for shutdown ordering.

Test signals: Reboot, halt, and poweroff under SBI SRST and under minimal firmware without SRST; confirm registered notifiers run before fallback loops.

Source read size: 34 lines, 529 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/reset.c -->
