## sources/distributed-fs/ceph-client/arch/s390/include/asm/tpi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/tpi.h` is a Test Pending Interruption
block in the s390 ceph-client Linux source snapshot. It has 37 lines and 738 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
tpi_info and adapter-interrupt fields used to decode pending I/O interrupts
Important macros/constants: `_ASM_S390_TPI_H`.
Important types/layouts: `tpi_info`, `subchannel_id`, `tpi_adapter_info`.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
channel-subsystem interrupt handling, TPI instruction users, and subchannel identifiers. Direct
include dependencies detected here: `linux/types.h`, `uapi/asm/schid.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for channel-subsystem interrupt handling, TPI
instruction users, and subchannel identifiers. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
packed layout mistakes lose adapter or subchannel interrupt details

### Test Signals
I/O interrupt injection, adapter interrupt tests, and channel-device bring-up
