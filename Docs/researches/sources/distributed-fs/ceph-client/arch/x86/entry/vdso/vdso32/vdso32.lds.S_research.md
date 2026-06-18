## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vdso32.lds.S

Purpose: 32-bit vDSO linker/version script.

Important declarations: defines `BUILD_VDSO32`, includes `common/vdso-layout.lds.S`, sets `ENTRY(__kernel_vsyscall)`, and exports symbols under `LINUX_2.6` and legacy `LINUX_2.5`.

Control flow: link-time only. It combines common layout with 32-bit ABI symbol visibility, including time/getcpu symbols plus syscall and sigreturn trampolines.

State/persistence: produces a 32-bit ELF shared object whose entry point is used for AT_SYSINFO and whose symbols are user ABI.

Integration points: vdso32 objects, libc symbol lookup, process auxv setup, and kernel signal/syscall recognition.

Risks: removing or renaming versioned symbols breaks old 32-bit userspace. Test signals include readelf symbol/version checks, AT_SYSINFO validation, and 32-bit process startup/signal tests.
