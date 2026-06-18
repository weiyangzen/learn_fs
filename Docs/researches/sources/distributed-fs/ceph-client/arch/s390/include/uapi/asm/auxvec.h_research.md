## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/auxvec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/auxvec.h` is a s390 auxiliary vector
constants in the s390 ceph-client Linux source snapshot. It has 9 lines and 214 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
AT_SYSINFO_EHDR and vector sizing constants used to expose the vDSO to userspace loaders
Important macros/constants: `__ASMS390_AUXVEC_H`, `AT_SYSINFO_EHDR`, `AT_VECTOR_SIZE_ARCH`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
ELF exec, glibc/musl startup, vDSO mapping, and process auxiliary vectors. Direct include
dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for ELF exec, glibc/musl startup, vDSO
mapping, and process auxiliary vectors. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong constants make runtimes miss or misread the vDSO

### Test Signals
getauxval/ld.so startup and vdso selftests
