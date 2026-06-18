## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/diag.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/diag.h` is a diagnose ioctl payload
ABI in the s390 ceph-client Linux source snapshot. It has 32 lines and 811 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
DIAG 324 program information block and DIAG 310 memory-top buffers plus ioctl request codes
Important macros/constants: `__S390_UAPI_ASM_DIAG_H`, `DIAG_MAGIC_STR`, `DIAG324_GET_PIBBUF`, `DIAG324_GET_PIBLEN`, `DIAG310_GET_STRIDE`, `DIAG310_GET_MEMTOPLEN`, `DIAG310_GET_MEMTOPBUF`.
Important types/layouts: `diag324_pib`, `diag310_memtop`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 5.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
z/VM/LPAR diagnostic drivers and userspace management tools. Direct include dependencies detected
here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for z/VM/LPAR diagnostic drivers and
userspace management tools. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
wrong lengths or magic values produce invalid hypervisor diagnostic calls

### Test Signals
diagnose ioctl tests under z/VM and LPAR
