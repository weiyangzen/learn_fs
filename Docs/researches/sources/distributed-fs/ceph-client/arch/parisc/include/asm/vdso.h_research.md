<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/vdso.h

Source read size: 25 lines, 664 bytes.

Purpose: declares PA-RISC vDSO symbol lookup helpers and version/link constants. Important APIs: `VDSO64_SYMBOL()`, `VDSO32_SYMBOL()`, `VDSO_LBASE`, and `VDSO_VERSION_STRING`. Control flow: signal and exec setup code add generated offsets to `mm->context.vdso_base` to locate vDSO trampoline symbols; absent 32-bit support returns zero for `VDSO32_SYMBOL`. State and persistence: per-mm `vdso_base` persists for the process address space. Dependencies and integration points: includes generated `vdso64-offsets.h`/`vdso32-offsets.h`, integrates with `kernel/vdso.c`, `vdso32/`, `vdso64/`, and signal trampolines. Risks: generated offset headers must match the linked vDSO image; version-string changes affect userspace tooling expectations. Test signals: auxv `AT_SYSINFO_EHDR`, signal trampoline execution, restart syscall behavior, 32-bit compat vDSO tests, and vdso symbol inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vdso.h -->
