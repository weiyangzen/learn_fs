## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/Kbuild

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/Kbuild` is a UAPI export manifest in
the s390 ceph-client Linux source snapshot. It has 4 lines and 90 bytes; exported UAPI contract:
yes.

### Important APIs, Types, And Functions
the generated-y and generic-y lists controlling which s390 asm headers are exported or generated
during headers_install
Important macros/constants: none detected.
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
UAPI header installation, syscall-header generation, and userspace build environments. Direct
include dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for UAPI header installation, syscall-
header generation, and userspace build environments. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
missing entries break userspace compilation or omit generated syscall headers

### Test Signals
make headers_install and userspace include smoke tests
