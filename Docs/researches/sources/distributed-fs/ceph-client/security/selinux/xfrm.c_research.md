# sources/distributed-fs/ceph-client/security/selinux/xfrm.c

## Purpose
`xfrm.c` implements SELinux hooks for labeled IPsec/XFRM policies and states. It allocates, clones, frees, authorizes, and matches SELinux security contexts on XFRM policy/state objects and extracts peer SIDs from packet transform paths.

## Important APIs, Types, and Functions
Important functions include `selinux_xfrm_policy_alloc()`, `selinux_xfrm_policy_clone()`, `selinux_xfrm_policy_free()`, `selinux_xfrm_policy_delete()`, `selinux_xfrm_policy_lookup()`, `selinux_xfrm_state_alloc()`, `selinux_xfrm_state_alloc_acquire()`, `selinux_xfrm_state_free()`, `selinux_xfrm_state_delete()`, `selinux_xfrm_state_pol_flow_match()`, `selinux_xfrm_decode_session()`, `selinux_xfrm_skb_sid()`, `selinux_xfrm_sock_rcv_skb()`, and `selinux_xfrm_postroute_last()`. `selinux_xfrm_refcount` tracks labeled XFRM objects.

## Control Flow
User-provided XFRM contexts are validated for LSM/SELinux DOI and algorithm, copied into `xfrm_sec_ctx`, converted to a SID, and authorized with `ASSOCIATION__SETCONTEXT`. Policy lookup checks `ASSOCIATION__POLMATCH`; EACCES is mapped to ESRCH so the XFRM layer treats it as no policy match. State/policy/flow matching rejects label mismatches and requires `ASSOCIATION__SENDTO`. Packet SID extraction scans ingress `sec_path` or egress destination transforms. Receive/postroute hooks enforce `RECVFROM`/`SENDTO` against labeled or unlabeled association SIDs.

## State and Persistence
Security contexts are stored on XFRM policy/state objects and freed with those objects. The global refcount records active labeled XFRM usage. Packet-derived SIDs are transient.

## Dependencies and Integration Points
This file integrates SELinux AVC checks with the Linux XFRM/IPsec stack, skb security paths, destination transforms, socket receive/send paths, and `security_context_to_sid()`/`security_sid_to_context()`.

## Risks
Risks include accepting malformed user contexts, inconsistent ingress transform labels, incorrect unlabeled fallback enforcement, refcount imbalance, and lifetime bugs when cloning variable-length contexts. The `-EACCES` to `-ESRCH` conversion is behaviorally important for XFRM policy search.

## Test Signals
Exercise labeled and unlabeled IPsec policies, mismatched SA/policy/flow labels, deletion authorization, acquire-state allocation from secid, ingress stacks with multiple labels, postroute unlabeled checks, and refcount balance under clone/free/error paths.
