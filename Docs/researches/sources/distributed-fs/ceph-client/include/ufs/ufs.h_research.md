<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs.h -->
# sources/distributed-fs/ceph-client/include/ufs/ufs.h

Purpose: defines core UFS protocol constants, descriptor/query offsets, UPIU transaction metadata, device feature bits, response structures, regulator/device info, and shared device state used by the UFS host controller stack.

Important APIs and types: key exports include UFS LUN/WLUN constants, task management codes, UPIU transaction/flag/attribute enums, query flag/attribute/descriptor IDs, descriptor parameter offsets, WriteBooster/HPB/HID/temperature feature bits, power modes, query opcodes/results, `utp_cmd_rsp`, `utp_upiu_rsp`, `ufs_vreg`, `ufs_vreg_info`, and `ufs_dev_info`.

Control flow: the UFS core builds UPIU commands using these enums, issues query requests to read/write flags, attrs, and descriptors, interprets response/result codes, configures feature bits such as WriteBooster/HPB/HID, and fills `ufs_dev_info` during probe for later PM, queue, RPMB, RTC, and exception handling.

State and persistence: protocol constants are static; `ufs_dev_info` is runtime cached device identity/capability state including write protection, LU counts, manufacturer/model/spec, queue depth, WriteBooster settings, RPMB/RTC/HID info, and device ID. Persistent state lives on the UFS device in descriptors, attributes, flags, flash, and RPMB.

Dependencies and integration points: depends on Linux bitops/types/time and UAPI SCSI BSG UFS definitions for UPIU wire structures. It integrates with SCSI UFS core, BSG passthrough, regulator handling, RPMB, power management, and device feature management.

Risks and test signals: risks include descriptor offset drift across UFS spec versions, endian/wire-structure assumptions, feature gating for pre-3.1 devices, query length validation, and WriteBooster/RPMB/RTC state transitions. Test probe descriptor parsing, query read/write attrs/flags, WLUN handling, feature enable/disable, RPMB multi-region info, and malformed device responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs.h -->
