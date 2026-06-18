## `sources/distributed-fs/ceph-client/arch/x86/hyperv/Makefile`

Purpose: selects x86 Hyper-V integration objects and generated assembly-offset headers.

Important build rules: base objects are `hv_init.o`, `mmu.o`, `nested.o`, `irqdomain.o`, and `ivm.o`. x86-64 adds `hv_apic.o`; VTL mode adds `hv_vtl.o` and `mshv_vtl_asm.o`; paravirt spinlocks add `hv_spinlock.o`; root crash dump support adds `hv_crash.o` and `hv_trampoline.o`. `mshv_vtl_asm.o` depends on generated `mshv-asm-offsets.h`, produced from `mshv-asm-offsets.s` via `filechk`.

Control flow: build-time only. It also removes profiling and stack protector from `hv_trampoline.o` for crash-path assembly safety.

State and persistence: no runtime state, but generated offset headers are build artifacts and cleaned by `clean-files`.

Dependencies and integration points: x86 Hyper-V Kconfig symbols, kbuild offset generation, crash dump, VTL, paravirt spinlock, and x86-64 build constraints.

Risks: missing offset dependency would break VTL assembly when context layout changes. Incorrect instrumentation flags on crash trampoline code could make devirtualization entry unsafe.

Test signals: clean incremental builds across combinations of `CONFIG_HYPERV_VTL_MODE`, `CONFIG_PARAVIRT_SPINLOCKS`, `CONFIG_MSHV_ROOT`, and `CONFIG_CRASH_DUMP`; generated `mshv-asm-offsets.h` updates when `struct mshv_vtl_cpu_context` changes.
