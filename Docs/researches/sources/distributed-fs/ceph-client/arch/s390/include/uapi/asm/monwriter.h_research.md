## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/monwriter.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/monwriter.h` is a z/VM monitor writer
ABI in the s390 ceph-client Linux source snapshot. It has 32 lines and 939 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
monitor event header and ioctl constants for interval/config/event writes
Important macros/constants: `_ASM_390_MONWRITER_H`, `MONWRITE_START_INTERVAL`, `MONWRITE_STOP_INTERVAL`, `MONWRITE_GEN_EVENT`, `MONWRITE_START_CONFIG`.
Important types/layouts: `monwrite_hdr`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
monwriter character device and z/VM monitor-stream consumers. Direct include dependencies detected
here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for monwriter character device and z/VM
monitor-stream consumers. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
header or ioctl drift corrupts monitor records delivered to z/VM

### Test Signals
monwriter ioctl smoke tests and z/VM monitor record validation
