# sources/distributed-fs/ceph-client/arch/mips/ralink/reset.c

Purpose: Ralink restart support. It wires the generic MIPS `_machine_restart` hook to a system-controller reset sequence.

Important APIs and control flow: `mips_reboot_setup()` runs as an `arch_initcall()` and assigns `_machine_restart`. `ralink_restart()` optionally asserts the PCI reset bit, delays for 50 ms, disables local interrupts, writes `RSTCTL_RESET_SYSTEM` to `SYSC_REG_RESET_CTRL`, and never returns.

State, persistence, and integration: it mutates only sysc reset registers during shutdown. Dependencies include `rt_sysc_w32()` and `rt_sysc_m32()` having a valid system-controller mapping from `ralink_of_remap()`. Risks are reset failure if sysc was not remapped, PCI reset side effects when CONFIG_PCI is enabled, and no halt/poweroff implementation. Test signals are reboot behavior on supported boards and the absence of post-reset execution after the write.
