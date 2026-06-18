<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h` implements arm64 vmap-stack allocation with consistent alignment for stack overflow detection. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VMAP_STACK_H`. The file is 25 lines / 641 bytes. Direct includes are `linux/gfp.h`, `linux/vmalloc.h`, `linux/pgtable.h`, `asm/memory.h`, `asm/thread_info.h`.

### Control Flow
`arch_alloc_vmap_stack` calls `__vmalloc_node` with `THREAD_ALIGN` and thread-info GFP flags, then resets KASAN tags before returning the stack pointer.

### State, Persistence, And Dependencies
Allocated stacks persist as vmalloc-backed kernel stacks owned by task/thread lifecycle code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong alignment or tag reset can weaken overflow detection, confuse KASAN, or produce stacks incompatible with thread-info assumptions.

### Test Signals
Enable `CONFIG_VMAP_STACK`, KASAN, and guard pages; run fork/exit stress, stack overflow probes, and CPU hotplug workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmap_stack.h -->
