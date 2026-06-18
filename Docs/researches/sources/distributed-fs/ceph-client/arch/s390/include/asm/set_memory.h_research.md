## sources/distributed-fs/ceph-client/arch/s390/include/asm/set_memory.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/set_memory.h` is a kernel mapping
permission changes in the s390 ceph-client Linux source snapshot. It has 68 lines and 2175 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
set_memory_* wrappers and direct-map validity helpers that batch page attribute changes under a
global mutex
Important macros/constants: `_ASMS390_SET_MEMORY_H`, `SET_MEMORY_RO`, `SET_MEMORY_RW`, `SET_MEMORY_NX`, `SET_MEMORY_X`, `SET_MEMORY_4K`, `SET_MEMORY_INV`, `SET_MEMORY_DEF`, `set_memory_rox`, `__SET_MEMORY_FUNC(fname, flags)`.
Important types/layouts: `mutex`, `page`.
Important declarations or inline helpers: `__set_memory`, `set_direct_map_invalid_noflush`, `set_direct_map_default_noflush`, `set_direct_map_valid_noflush`, `kernel_page_present`, `fname`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
module/text patching, STRICT_KERNEL_RWX, vmalloc, debug pagealloc, and direct-map manipulation.
Direct include dependencies detected here: `linux/mutex.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for module/text patching, STRICT_KERNEL_RWX,
vmalloc, debug pagealloc, and direct-map manipulation. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
missing TLB synchronization or wrong flag composition can leave executable/writable aliases

### Test Signals
STRICT_KERNEL_RWX tests, module load/unload, ftrace/static-key patching, and debug_pagealloc
