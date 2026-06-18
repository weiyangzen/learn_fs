# sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_32.c

Purpose: provides the export policy macro for 32-bit x86 `atomic64_t` helper symbols and includes the generic Linux atomic64 implementation.

Important APIs/types/functions: defines `ATOMIC64_EXPORT` as `EXPORT_SYMBOL`, then includes `<linux/export.h>` and `<linux/atomic.h>`. The included atomic code uses the macro to export the architecture-backed 64-bit atomic operations implemented by the selected x86 assembly helpers.

Control flow: there is no local runtime control flow. The file acts as a compile-time wrapper that causes generated/included atomic64 operations to be exported from this translation unit.

State and persistence behavior: no state is stored locally. Runtime state is the caller-provided `atomic64_t` memory manipulated by the included implementations and assembly backends.

Dependencies/integration points: built only on 32-bit x86 via the Makefile. It links generic atomic definitions with x86-specific `atomic64_386_32.S` or `atomic64_cx8_32.S` depending on CPU config. Exported symbols are used by kernel code and modules needing 64-bit atomics on 32-bit kernels.

Risks: the file is tiny but symbol visibility matters. If `ATOMIC64_EXPORT` changes or this wrapper is not built, modules may fail to link against atomic64 helpers. Correctness depends on the assembly implementation matching the generic atomic operation ABI.

Test signals: 32-bit build/link tests with modular users of atomic64, plus atomic API selftests or stress tests on CX8 and non-CX8 configurations.
