## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/dasd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/dasd.h` is a DASD block-device ioctl
ABI in the s390 ceph-client Linux source snapshot. It has 354 lines and 13078 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
DASD information, format, feature, profile, copy-pair, timeout, reservation, and UID structures plus
ioctl codes
Important macros/constants: `DASD_H`, `DASD_IOCTL_LETTER`, `DASD_API_VERSION`, `DASD_FORMAT_NONE`, `DASD_FORMAT_LDL`, `DASD_FORMAT_CDL`, `DASD_FEATURE_READONLY`, `DASD_FEATURE_USEDIAG`, `DASD_FEATURE_INITIAL_ONLINE`, `DASD_FEATURE_ERPLOG`, `DASD_FEATURE_FAILFAST`, `DASD_FEATURE_FAILONSLCK`, `DASD_FEATURE_USERAW`, `DASD_FEATURE_DISCARD`, `DASD_FEATURE_PATH_AUTODISABLE`, `DASD_FEATURE_REQUEUEQUIESCE`, `DASD_FEATURE_DEFAULT`, `DASD_PARTN_BITS`, `DASD_FMT_INT_FMT_R0`, `DASD_FMT_INT_FMT_HA`; plus 38 more.
Important types/layouts: `dasd_information2_t`, `dasd_information_t`, `dasd_rssd_perf_stats_t`, `profile_info_t`, `dasd_profile_info_t`, `format_data_t`, `dasd_copypair_swap_data_t`, `format_check_t`, `attrib_data_t`, `dasd_symmio_parms`, `dasd_snid_data`, `dasd_snid_ioctl_data`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 24.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
DASD block driver, formatting tools, storage-management utilities, and PPRC/safe-offline workflows.
Direct include dependencies detected here: `linux/types.h`, `linux/ioctl.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for DASD block driver, formatting tools,
storage-management utilities, and PPRC/safe-offline workflows. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
ABI changes risk destructive formatting or incorrect storage feature control

### Test Signals
dasdfmt/dasdview tooling, ioctl ABI tests, and feature/profile readback
