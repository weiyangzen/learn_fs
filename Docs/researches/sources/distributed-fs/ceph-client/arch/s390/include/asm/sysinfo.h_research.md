## sources/distributed-fs/ceph-client/arch/s390/include/asm/sysinfo.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/sysinfo.h` is a STSI/STHYI system
information layouts in the s390 ceph-client Linux source snapshot. It has 231 lines and 5077 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
packed STSI structures for machine/LPAR/topology/capacity data plus helpers for service-level
registration and topology nesting
Important macros/constants: `__ASM_S390_SYSINFO_H`, `LPAR_CHAR_DEDICATED`, `LPAR_CHAR_SHARED`, `LPAR_CHAR_LIMITED`, `TOPOLOGY_NR_MAG`.
Important types/layouts: `sysinfo_1_1_1`, `sysinfo_1_2_1`, `sysinfo_1_2_2`, `sysinfo_1_2_2_extension`, `sysinfo_2_2_1`, `sysinfo_2_2_2`, `sysinfo_3_2_2`, `topology_core`, `topology_container`, `topology_entry`, `sysinfo_15_1_x`, `service_level`, `list_head`, `seq_file`.
Important declarations or inline helpers: `volatile`, `min`, `stsi`, `register_service_level`, `unregister_service_level`, `sthyi_fill`, `topology_mnest_limit`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
topology, hypfs, CPU management, virtualization diagnostics, and machine capacity reporting. Direct
include dependencies detected here: `linux/uuid.h`, `asm/bitsperlong.h`, `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for topology, hypfs, CPU management,
virtualization diagnostics, and machine capacity reporting. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
bitfield layout drift misreports topology/capacity or corrupts hypervisor information

### Test Signals
STSI/STHYI tests, topology sysfs validation, LPAR/zVM boots, and service-level registration
