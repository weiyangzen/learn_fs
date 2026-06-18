## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32-setup.c

Purpose: initializes and exposes runtime controls for mapping the 32-bit vDSO.

Important APIs/state: global `vdso32_enabled`, boot parser `vdso32_setup()`, `__setup("vdso32=", ...)`, 32-bit `vdso=` alias, sysctl table for `abi/vsyscall32` on x86_64 or `vm/vdso_enabled` on x86_32, and `ia32_binfmt_init()`.

Control flow: boot parameters parse numeric enablement and clamp unsupported values to disabled. Sysctl registration happens at init when `CONFIG_SYSCTL` is enabled.

State/persistence: `vdso32_enabled` is `__read_mostly` runtime configuration read by `vma.c` during `load_vdso32()`. Sysctl changes persist until reboot and affect subsequent exec mappings.

Integration points: compat vDSO mapping, IA32 binfmt, kernel boot parameters, sysctl, `CONFIG_COMPAT_VDSO`, and `arch_setup_additional_pages()`.

Risks: enabling/disabling changes user ABI availability and libc syscall path behavior. Invalid historical values are intentionally rejected. Test signals include booting with `vdso32=0/1`, sysctl writes, 32-bit exec tests, and compat syscall/vDSO fallback checks.
