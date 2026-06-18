## sources/distributed-fs/ceph-client/arch/s390/include/asm/vmlinux.lds.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vmlinux.lds.h` is a s390 linker-script
fragments in the s390 ceph-client Linux source snapshot. It has 33 lines and 1167 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
BOOT_DATA and BOOT_DATA_PRESERVED output sections for early boot data placement
Important macros/constants: `BOOT_DATA`, `BOOT_DATA_PRESERVED`.
Important types/layouts: none detected.
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
vmlinux.lds.S, setup/sections.h boot-data annotations, and initmem freeing. Direct include
dependencies detected here: `asm/page.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for vmlinux.lds.S, setup/sections.h boot-data
annotations, and initmem freeing. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect section attributes can discard needed boot state or retain discardable memory

### Test Signals
link-map inspection and boot with initmem poisoning
