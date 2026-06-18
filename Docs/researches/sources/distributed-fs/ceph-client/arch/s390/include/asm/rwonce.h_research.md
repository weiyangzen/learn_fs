## sources/distributed-fs/ceph-client/arch/s390/include/asm/rwonce.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/rwonce.h` is a s390 READ_ONCE extensions
in the s390 ceph-client Linux source snapshot. It has 31 lines and 689 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
a 128-bit aligned read helper layered on the generic rwonce implementation for lockless structures
that need atomic pair sampling
Important macros/constants: `__ASM_S390_RWONCE_H`, `READ_ONCE_ALIGNED_128(x)`.
Important types/layouts: none detected.
Important declarations or inline helpers: `volatile`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic compiler-barrier READ_ONCE users and architecture alignment assumptions. Direct include
dependencies detected here: `linux/compiler_types.h`, `asm-generic/rwonce.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic compiler-barrier READ_ONCE users and
architecture alignment assumptions. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
misaligned or non-atomic 128-bit reads can observe torn state in lockless algorithms

### Test Signals
KCSAN/lockless data-race tests and compile coverage for 128-bit consumers
