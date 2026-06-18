## sources/distributed-fs/ceph-client/arch/s390/include/asm/stp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/stp.h` is a Server Time Protocol
interfaces in the s390 ceph-client Linux source snapshot. It has 99 lines and 1727 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
STP interrupt parameter blocks, time-zone/control structures, notifier hooks, enabled flag, and
work-queue entry points
Important macros/constants: `__S390_STP_H`, `STP_OP_SYNC`, `STP_OP_CTRL`.
Important types/layouts: `atomic_notifier_head`, `stp_irq_parm`, `stp_sstpi`, `stp_tzib`, `stp_tcpib`, `stp_lsoib`, `stp_stzi`.
Important declarations or inline helpers: `stp_sync_check`, `stp_island_check`, `stp_queue_work`, `stp_enabled`.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
timekeeping, clock sync, external interrupt handling, and sysfs/diagnostic STP consumers. Direct
include dependencies detected here: `linux/compiler.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for timekeeping, clock sync, external interrupt
handling, and sysfs/diagnostic STP consumers. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect packed layout or missed notifications can leave system time unsynchronized

### Test Signals
STP interrupt injection, time sync checks, notifier registration, and LPAR clock-change events
