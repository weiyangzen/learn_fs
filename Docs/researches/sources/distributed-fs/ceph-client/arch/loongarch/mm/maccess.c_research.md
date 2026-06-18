<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/maccess.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/maccess.c

### Purpose
`maccess.c` defines the architecture policy for nofault kernel memory reads.

### Important APIs, Types, And Functions
The only function is `copy_from_kernel_nofault_allowed(const void *unsafe_src, size_t size)`.

### Control Flow
The helper returns true only when the source pointer has its highest address bit set, treating that as kernel space. The `size` argument is not inspected.

### State, Persistence, And Dependencies
No state is stored. It depends on pointer-width constants and the LoongArch virtual address split.

### Integration Points
Generic `copy_from_kernel_nofault()` users call this to reject user-space probes before attempting exception-table-backed kernel reads.

### Risks
The high-bit test must match all kernel address ranges on supported LoongArch modes. Ignoring size means overflow/range-end validation is left to the caller or fault path.

### Test Signals
Run nofault access tests for direct-map, vmalloc/module, invalid kernel, and user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/maccess.c -->
