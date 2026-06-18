# sources/distributed-fs/ceph-client/include/linux/execmem.h

Purpose: architecture-parameterized executable memory allocator for modules, kprobes, ftrace, BPF, and module data.

Important APIs/types/functions: `MODULE_ALIGN`, `enum execmem_type`, `enum execmem_range_flags`, ROX hooks `execmem_fill_trapping_insns()` and `execmem_restore_rox()`, `struct execmem_range`, `struct execmem_info`, `execmem_arch_setup()`, `execmem_alloc()`, `execmem_alloc_rw()`, `execmem_free()`, cleanup helper, `execmem_vmap()`, `execmem_is_rox()`, and `execmem_init()`.

Control flow: early init obtains arch ranges/defaults; subsystems allocate executable memory by type; architectures may enforce placement, permissions, alignment, KASAN shadow, and ROX cache. Callers using writable allocations must restore/manage permissions.

State/persistence: runtime allocator state and virtual mappings; no disk persistence. Allocated code/data remains until freed or module/subsystem teardown.

Dependencies/integration: module loader, vmalloc/vmap, KASAN, architecture text permissions, BPF JIT, ftrace, kprobes, cleanup annotations.

Risks/test signals: risks are W+X exposure, wrong executable range for branch reachability, KASAN shadow gaps, ROX restoration failure, alignment mistakes, and late init ordering. Test module load/unload, BPF JIT allocation, kprobe/ftrace text allocation, strict W^X/debug page permissions, KASAN configs, and arch fallback ranges.
