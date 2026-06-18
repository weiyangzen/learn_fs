<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hyperv.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hyperv.h

## Purpose
`hyperv.h` defines the userspace/kernel message ABI for Hyper-V integration services on Linux: VSS backup coordination, host-to-guest file copy, and key-value-pair exchange including IP injection.

## Important APIs, types, and functions
Version and registration constants include `UTIL_*`, `VSS_OP_REGISTER`, `VSS_OP_REGISTER1`, `FCOPY_CURRENT_VERSION`, `KVP_OP_REGISTER`, and `KVP_OP_REGISTER1`. VSS types include `enum hv_vss_op`, `struct hv_vss_hdr`, `hv_vss_check_feature`, `hv_vss_check_dm_info`, and `hv_vss_msg`. File copy types include `enum hv_fcopy_op`, `struct hv_fcopy_hdr`, `hv_start_fcopy`, and `hv_do_fcopy`. KVP definitions include registry value types, `enum hv_kvp_exchg_op`, `enum hv_kvp_exchg_pool`, Hyper-V status codes, address-family constants, `hv_kvp_ipaddr_value`, `hv_kvp_hdr`, `hv_kvp_exchg_msg_value`, `hv_kvp_msg_*`, `hv_kvp_msg`, and `hv_kvp_ip_msg`.

## Control flow
Userspace daemons register with kernel Hyper-V utility drivers. The kernel relays host requests to daemons: VSS create/freeze/thaw/checks, fcopy start/write/complete/cancel chunks, or KVP get/set/delete/enumerate/IP operations. Daemons respond with data or error status, and the kernel forwards completion to the host.

## State and persistence behavior
VSS state is transaction-scoped but affects filesystem freeze/thaw. Fcopy state persists for the duration of a host file transfer and writes guest files. KVP pools can persist host/guest key-value data and network configuration. The fixed message sizes and packed UTF-16 fields are ABI-critical.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with Hyper-V VMBus/hv_utils, connector or netlink daemon channels, filesystem freeze code, guest file I/O, registry-compatible KVP exchange, and IP configuration tooling.

## Risks and test signals
Risks include daemon/kernel version mismatch, undersized VSS buffers for large host messages, UTF-16 length mistakes, file copy path traversal or overwrite behavior, stale KVP pool data, and incomplete thaw after failures. Test signals include daemon registration compatibility, VSS freeze/thaw under I/O, fcopy chunk sequencing and cancel paths, KVP enumerate invalid-index behavior, IP injection validation, and Hyper-V status-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hyperv.h -->
