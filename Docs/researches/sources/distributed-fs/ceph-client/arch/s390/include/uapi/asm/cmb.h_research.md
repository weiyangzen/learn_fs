## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/cmb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/cmb.h` is a Channel Measurement Block
ABI in the s390 ceph-client Linux source snapshot. It has 54 lines and 1920 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
DASD CMB ioctl numbers and cmbdata counter structure
Important macros/constants: `_UAPIS390_CMB_H`, `BIODASDCMFENABLE`, `BIODASDCMFDISABLE`, `BIODASDREADALLCMB`.
Important types/layouts: `cmbdata`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 3.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
DASD performance monitoring tools and channel measurement collection. Direct include dependencies
detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for DASD performance monitoring tools and
channel measurement collection. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
counter layout drift corrupts performance statistics

### Test Signals
DASD CMB enable/read/disable tests
