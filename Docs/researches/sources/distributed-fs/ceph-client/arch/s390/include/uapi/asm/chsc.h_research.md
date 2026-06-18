## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chsc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chsc.h` is a Channel-Subsystem Call
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 144 lines and 2903 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
async/sync CHSC areas, response structures, configuration descriptors, and CHSC ioctl numbers
Important macros/constants: `_ASM_CHSC_H`, `CHSC_SIZE`, `CHSC_IOCTL_MAGIC`, `CHSC_START`, `CHSC_INFO_CHANNEL_PATH`, `CHSC_INFO_CU`, `CHSC_INFO_SCH_CU`, `CHSC_INFO_CI`, `CHSC_INFO_CCL`, `CHSC_INFO_CPD`, `CHSC_INFO_DCAL`, `CHSC_START_SYNC`, `CHSC_ON_CLOSE_SET`, `CHSC_ON_CLOSE_REMOVE`.
Important types/layouts: `chsc_async_header`, `subchannel_id`, `chsc_async_area`, `chsc_header`, `chsc_sync_area`, `chsc_response_struct`, `chsc_chp_cd`, `chp_id`, `chsc_cu_cd`, `chsc_sch_cud`, `conf_id`, `chsc_conf_info`, `ccl_parm_chpid`, `ccl_parm_cssids`, `chsc_comp_list`, `chsc_dcal`, `chsc_cpd_info`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 11.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
cio userspace tools, subchannel/channel-path discovery, and hardware configuration queries. Direct
include dependencies detected here: `linux/types.h`, `linux/ioctl.h`, `asm/chpid.h`, `asm/schid.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for cio userspace tools,
subchannel/channel-path discovery, and hardware configuration queries. For UAPI files, the
integration point also includes headers_install and userspace programs compiled against the exported
layout.

### Risks
packed structure or ioctl-number drift breaks channel management utilities

### Test Signals
CHSC ioctl tests across channel path, CU, SCH-CU, CCL, and configuration queries
