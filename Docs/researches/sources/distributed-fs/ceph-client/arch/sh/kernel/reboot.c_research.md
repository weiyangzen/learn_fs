# sources/distributed-fs/ceph-client/arch/sh/kernel/reboot.c

Purpose: supplies SH machine poweroff, restart, halt, shutdown, and crash-shutdown dispatch.

Important APIs and control flow: `machine_ops` defaults to native handlers. Restart disables interrupts, globally flushes TLBs, tries an address-error reset path, then triggers the watchdog and sleeps forever if reset fails. Shutdown stops other CPUs. Poweroff calls `do_kernel_power_off()`. Halt shuts down then stops the current CPU. Public `machine_power_off()`, `machine_shutdown()`, `machine_restart()`, `machine_halt()`, and optional `machine_crash_shutdown()` delegate through `machine_ops`.

State, dependencies, and risks: state includes exported `pm_power_off` and mutable `machine_ops`. Dependencies include watchdog registers, TLB flush, trap reset trigger, SMP stop, kernel poweroff core, and optional kexec crash shutdown. Risks are platform reset methods that hang, machine_ops override mistakes, and crash shutdown doing too little on SMP unless platform code supplies more. Test signals are reboot/poweroff/halt on boards, watchdog reset fallback, and kexec crash path.
