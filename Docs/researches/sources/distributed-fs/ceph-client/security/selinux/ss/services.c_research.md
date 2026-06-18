# sources/distributed-fs/ceph-client/security/selinux/ss/services.c

## Purpose
`services.c` implements the SELinux security server: access-vector decisions, context/SID translation, SID computation for transitions and object creation, policy load/commit/cancel, boolean updates, network/object-context SID lookup, audit rule support, NetLabel conversion, and policy readback.

## Important APIs, Types, and Functions
Central exported functions include `security_compute_av()`, `security_compute_xperms_decision()`, `security_transition_sid()`, `security_member_sid()`, `security_change_sid()`, `security_validate_transition()`, `security_bounded_transition()`, `security_sid_to_context*()`, `security_context_to_sid*()`, `security_load_policy()`, `selinux_policy_commit()`, `selinux_policy_cancel()`, `security_port_sid()`, `security_netif_sid()`, `security_node_sid()`, `security_genfs_sid()`, `security_fs_use()`, `security_set_bools()`, `security_sid_mls_copy()`, audit-rule helpers, NetLabel helpers, and policy readback helpers. The file owns class/permission mapping via `struct selinux_map` and context conversion via `services_convert_context()`.

## Control Flow
Access decisions map kernel class IDs to policy class IDs, find source/target contexts in the active RCU-protected sidtab, evaluate TE and conditional AV table entries across source/target type-attribute bitmaps, merge extended permissions, apply constraints/MLS, role transition restrictions, type bounds, permissive and neveraudit flags, then map results back to kernel permission bits. SID computation selects user/role/type defaults, transition/change/member AV rules, filename transitions, role transitions, MLS values, validates the new context, and inserts or reuses a SID. Policy load reads a new `policydb`, builds the kernel mapping, loads initial SIDs, preserves booleans, converts the live SID table, and publishes via RCU only at commit.

## State and Persistence
The active policy is `selinux_state.policy` under RCU plus `policy_mutex` for updates. `latest_granting` is the policy sequence for AVC and audit invalidation. Boolean changes create a shallow policy copy plus duplicated conditional portions, reevaluate conditionals, then publish a new policy object.

## Dependencies and Integration Points
This file integrates with AVC (`avc_ss_reset`), netlink policyload notifications, status page updates, NetLabel cache invalidation, XFRM policyload notification, IMA state measurement, audit, LSM blobs, filesystem superblock security, policycap globals, and the SID table conversion machinery.

## Risks
The highest risks are RCU lifetime mistakes, `-ESTALE` retry omissions during sidtab conversion, mismatched kernel/policy class mapping, invalid-context handling under permissive versus enforcing mode, boolean update shallow-copy mistakes, and incorrect network fallback labels. Permission mapping must handle unknown policy entries consistently with `allow_unknown` and `reject_unknown`.

## Test Signals
Exercise policy reload under concurrent context-to-SID insertions, AVC checks before and after boolean flips, unknown class/permission modes, filename transitions with object names, validatetrans denials, bounded transition denials, NetLabel and XFRM peer SID resolution, genfs/fs_use lookup, audit-rule stale detection, and policy readback length consistency.
