# sources/distributed-fs/ceph-client/arch/sparc/mm/execmem.c

Purpose: SPARC implementation of executable memory allocation range setup.

Important APIs/functions: `execmem_arch_setup()` initializes a static `struct execmem_info` with `EXECMEM_DEFAULT` range from `MODULES_VADDR` to `MODULES_END`, `PAGE_KERNEL` protection, and 1-byte alignment, then returns it.

Control flow: single init-time assignment to `execmem_info` using a compound literal.

State and persistence: `execmem_info` is static and `__ro_after_init`, so the configured executable allocation policy persists read-only after init.

Dependencies/integration: includes `linux/mm.h` and `linux/execmem.h`; depends on SPARC module address constants and `PAGE_KERNEL` initialized by architecture paging setup. Used by generic execmem/module/BPF-style executable allocation infrastructure.

Risks: `PAGE_KERNEL` must be initialized before use. Range mismatch with module mapping limits would allow allocation outside executable kernel virtual space or unnecessarily constrain callers.

Test signals: boot with `CONFIG_EXECMEM`, module load/unload, BPF/JIT or other execmem users if enabled, and verification that allocations land between `MODULES_VADDR` and `MODULES_END`.
