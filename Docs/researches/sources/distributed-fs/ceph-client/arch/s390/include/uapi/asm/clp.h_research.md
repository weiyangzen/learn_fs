## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/clp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/clp.h` is a Command Logical Processor
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 29 lines and 549 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
CLP request buffer structure and synchronous CLP ioctl number
Important macros/constants: `_ASM_CLP_H`, `CLP_IOCTL_MAGIC`, `CLP_SYNC`.
Important types/layouts: `clp_req`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 1.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
PCI/zPCI and system-management userspace using CLP requests. Direct include dependencies detected
here: `linux/types.h`, `linux/ioctl.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for PCI/zPCI and system-management
userspace using CLP requests. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
size or ioctl mismatches can truncate command buffers

### Test Signals
CLP_SYNC userspace smoke tests and headers_install
