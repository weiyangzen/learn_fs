## sources/distributed-fs/ceph-client/arch/s390/include/asm/vtime.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vtime.h` is a virtual CPU accounting hooks
in the s390 ceph-client Linux source snapshot. It has 57 lines and 1783 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
timer update declarations for system, machine-check, and idle accounting plus idle-data access
Important macros/constants: `_S390_VTIME_H`.
Important types/layouts: `lowcore`, `s390_idle_data`.
Important declarations or inline helpers: `update_timer_sys`, `update_timer_mcck`, `update_timer_idle`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
CPU measurement facility, lowcore timers, idle accounting, and scheduler time accounting. Direct
include dependencies detected here: `asm/lowcore.h`, `asm/cpu_mf.h`, `asm/idle.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for CPU measurement facility, lowcore timers,
idle accounting, and scheduler time accounting. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
missed accounting updates skew CPU time and idle statistics

### Test Signals
vtime accounting tests, idle stress, machine-check paths, and cpuacct counters
