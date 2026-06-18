## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sclp_ctl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sclp_ctl.h` is a SCLP control-device
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 25 lines and 465 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
sclp_ctl_sccb pointer/length wrapper and ioctl number for submitting SCCBs
Important macros/constants: `_ASM_SCLP_CTL_H`, `SCLP_CTL_IOCTL_MAGIC`, `SCLP_CTL_SCCB`.
Important types/layouts: `sclp_ctl_sccb`.
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
sclp_ctl userspace tooling and SCLP event/service-call paths. Direct include dependencies detected
here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for sclp_ctl userspace tooling and SCLP
event/service-call paths. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
pointer/length mismatch can submit malformed SCCBs to firmware

### Test Signals
SCLP_CTL_SCCB ioctl tests and SCCB length validation
