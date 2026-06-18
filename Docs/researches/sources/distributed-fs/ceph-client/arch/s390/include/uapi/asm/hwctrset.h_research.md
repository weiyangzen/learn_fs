## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hwctrset.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hwctrset.h` is a hardware counter-set
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 51 lines and 1686 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
start/read/stop structures and ioctls for CPU counter-set diagnostic access
Important macros/constants: `_PERF_CPUM_CF_DIAG_H`, `S390_HWCTR_DEVICE`, `S390_HWCTR_START_VERSION`, `S390_HWCTR_MAGIC`, `S390_HWCTR_START`, `S390_HWCTR_STOP`, `S390_HWCTR_READ`.
Important types/layouts: `s390_ctrset_start`, `s390_ctrset_setdata`, `s390_ctrset_cpudata`, `s390_ctrset_read`.
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
perf tooling, CPU measurement facility diagnostics, and privileged monitoring. Direct include
dependencies detected here: `linux/ioctl.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf tooling, CPU measurement facility
diagnostics, and privileged monitoring. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
counter-set version or buffer-size mismatches corrupt measurement data

### Test Signals
S390_HWCTR_* ioctl tests and perf counter validation
