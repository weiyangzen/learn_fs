<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mirred.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_mirred.h

Purpose: Defines TC mirror/redirect action state for sending packets to another net device or block.

Important APIs/types/functions: `struct tcf_mirred` embeds `tc_action`, stores mirror/redirect direction/action, block id, MAC header transmit mode, RCU net_device pointer, netdevice tracker, and list node. Helpers identify egress redirect, egress mirror, ingress redirect, ingress mirror, and return the target device with RTNL dereference.

Control flow: Action execution clones or redirects packets to the configured target device/block based on `tcfm_eaction`. Offload/classifier code uses helpers to classify direction and mode.

State and persistence behavior: Target device pointer is RCU-protected and tracked with `netdevice_tracker`; action is linked into a mirred list for lifecycle management.

Dependencies/integration points: Depends on TC mirred UAPI, act API, net_device, RTNL, and `tc_wrapper.h`.

Risks: Device unregister races, redirect loops, and incorrect ingress/egress classification can misroute packets or leak device references.

Test signals: Mirror and redirect tests for ingress/egress, target device removal, block redirect, action dump, and loop prevention checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mirred.h -->
