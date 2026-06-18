## sources/distributed-fs/ceph-client/arch/s390/include/asm/text-patching.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/text-patching.h` is a text patch
synchronization in the s390 ceph-client Linux source snapshot. It has 16 lines and 301 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
sync_core aliases and text_poke synchronization lock declarations for instruction patching
Important macros/constants: `_ASM_S390_TEXT_PATCHING_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: `text_poke_sync`, `text_poke_sync_lock`, `sync_core`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
alternatives, static keys, ftrace, livepatch-like text modification, and CPU serialization. Direct
include dependencies detected here: `asm/barrier.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for alternatives, static keys, ftrace, livepatch-
like text modification, and CPU serialization. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
missing serialization can execute stale or partially patched instructions

### Test Signals
alternatives boot, ftrace toggling, static key stress, and SMP patch races
