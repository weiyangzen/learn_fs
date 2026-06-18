## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hypfs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hypfs.h` is a hypervisor filesystem
diagnostic ABI in the s390 ceph-client Linux source snapshot. It has 55 lines and 1382 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
DIAG 304 and DIAG 0C data layouts exported for hypfs users
Important macros/constants: `_ASM_HYPFS_H`, `HYPFS_IOCTL_MAGIC`, `HYPFS_DIAG304`.
Important types/layouts: `hypfs_diag304`, `hypfs_diag0c_hdr`, `hypfs_diag0c_entry`, `hypfs_diag0c_data`.
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
hypfs, z/VM/LPAR metadata reporting, and userspace virtualization inventory tools. Direct include
dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for hypfs, z/VM/LPAR metadata reporting,
and userspace virtualization inventory tools. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
layout drift misreports hypervisor CPU and partition data

### Test Signals
hypfs reads under z/VM/LPAR and ioctl structure checks
