# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/reset.c

Purpose: provides Falcon reboot, halt, poweroff, and boot-source query support.

Important APIs/functions: `ltq_boot_select`, `machine_restart`, `machine_halt`, `machine_power_off`, and `mips_reboot_setup`.

Control flow: `arch_initcall` installs `_machine_restart`, `_machine_halt`, and `pm_power_off`. Restart disables interrupts, writes boot password registers and reset vector, then enables watchdog reset with magic values. Halt/poweroff disable interrupts and spin via `unreachable()`.

State and persistence: writes boot and watchdog MMIO registers; no software persistence.

Dependencies and integration: integrates with `asm/reboot.h` hooks and platform reset paths.

Risks: `ltq_boot_select()` is a dummy always returning SPI, so consumers cannot infer real boot media. Restart relies on magic register sequences.

Test signals: reboot command resets hardware, poweroff/halt paths stop execution, and watchdog reset is visible on Falcon boards.
