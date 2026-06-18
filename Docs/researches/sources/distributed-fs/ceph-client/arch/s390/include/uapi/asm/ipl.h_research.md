## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipl.h` is a IPL/re-IPL parameter
block ABI in the s390 ceph-client Linux source snapshot. It has 209 lines and 3849 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
IPL/re-IPL headers and FCP/NVMe/CCW/ECKD/NSS/DUMP/certificate structures used for boot and dump
control
Important macros/constants: `_ASM_S390_UAPI_IPL_H`, `IPL_PL_FLAG_IPLPS`, `IPL_PL_FLAG_SIPL`, `IPL_PL_FLAG_IPLSR`, `IPL_PL_FLAG_SBP`, `IPL_PB0_FLAG_LOADPARM`, `IPL_PB0_FCP_OPT_IPL`, `IPL_PB0_FCP_OPT_DUMP`, `IPL_PB0_NVME_OPT_IPL`, `IPL_PB0_NVME_OPT_DUMP`, `IPL_PB0_ECKD_OPT_IPL`, `IPL_PB0_ECKD_OPT_DUMP`, `IPL_PB0_CCW_VM_FLAG_NSS`, `IPL_PB0_CCW_VM_FLAG_VP`, `IPL_RB_COMPONENT_FLAG_SIGNED`, `IPL_RB_COMPONENT_FLAG_VERIFIED`.
Important types/layouts: `ipl_pl_hdr`, `ipl_pb_hdr`, `ipl_pb0_common`, `ipl_pb0_fcp`, `ipl_pb0_nvme`, `ipl_pb0_ccw`, `ipl_pb0_eckd`, `ipl_pb1_scp_data`, `ipl_rl_hdr`, `ipl_rb_hdr`, `ipl_rb_certificate_entry`, `ipl_rb_certificates`, `ipl_rb_component_entry`, `ipl_rb_components`, `ipl_pbt`, `ipl_rbt`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
s390 boot loader, sysfs reipl/dump controls, firmware IPL records, and userspace boot management.
Direct include dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for s390 boot loader, sysfs reipl/dump
controls, firmware IPL records, and userspace boot management. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
packed block drift can boot from the wrong device or lose dump configuration

### Test Signals
IPL/reipl sysfs tests across FCP, NVMe, CCW, ECKD, and dump configurations
