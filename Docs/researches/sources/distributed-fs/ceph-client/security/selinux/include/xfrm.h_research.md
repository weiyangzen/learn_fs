<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/xfrm.h -->
# sources/distributed-fs/ceph-client/security/selinux/include/xfrm.h

## Purpose
Declares SELinux support for XFRM/IPsec policy and state LSM hooks. The header lets the core SELinux network hooks allocate, clone, delete, free, match, and decode XFRM security contexts while compiling to no-op stubs when `CONFIG_SECURITY_NETWORK_XFRM` is disabled.

## Important APIs, Types, and Functions
Always-declared APIs include `selinux_xfrm_policy_alloc()`, `selinux_xfrm_policy_clone()`, `selinux_xfrm_policy_free()`, `selinux_xfrm_policy_delete()`, `selinux_xfrm_state_alloc()`, `selinux_xfrm_state_alloc_acquire()`, `selinux_xfrm_state_free()`, `selinux_xfrm_state_delete()`, `selinux_xfrm_policy_lookup()`, and `selinux_xfrm_state_pol_flow_match()`. With XFRM security enabled, the network packet surface adds `selinux_xfrm_sock_rcv_skb()`, `selinux_xfrm_postroute_last()`, `selinux_xfrm_decode_session()`, and `selinux_xfrm_skb_sid()`. `selinux_xfrm_enabled()` tests the external `selinux_xfrm_refcount`.

## Control Flow
Policy/state management functions are used when XFRM objects are created or destroyed from netlink or acquire paths. Packet hooks decode the session SID from matching XFRM state and check receive/postroute access against socket SIDs. On SELinux policy load, `selinux_xfrm_notify_policyload()` bumps route generation IDs in every network namespace so cached routes observe updated policy.

## State and Persistence
Persistent state is mostly external: XFRM policy/state security contexts and `selinux_xfrm_refcount`. The disabled-build stubs return success or `SECSID_NULL`, preserving normal networking without SELinux XFRM enforcement.

## Dependencies and Integration Points
Depends on `linux/lsm_audit.h`, `net/flow.h`, `net/xfrm.h`, `net_rwsem`, network namespace iteration, and route generation invalidation. It integrates with XFRM netlink, routing cache invalidation, socket receive/postroute hooks, and SELinux policy reload notifications.

## Risks
The enabled/disabled split must preserve identical call signatures. Route generation bumping under `net_rwsem` is broad and must stay synchronized with policy loads. Returning `SECSID_NULL` in disabled stubs is security-sensitive because callers must distinguish "no XFRM SID" from a meaningful label.

## Test Signals
Exercise IPsec policy/state creation with security contexts, policy clone/delete/free paths, receive and postroute checks with matching and mismatching SIDs, policy reload route invalidation, and builds with `CONFIG_SECURITY_NETWORK_XFRM` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/xfrm.h -->
