<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/security.h -->
# sources/distributed-fs/ceph-client/security/selinux/include/security.h

## Purpose
Defines the central SELinux security-server interface used by the LSM hooks, selinuxfs, network labeling code, and policy database services. It declares policy-version bounds, mount-labeling flags, global SELinux state, access-vector decision structures, extended-permission structures, SID/context conversion APIs, filesystem/network/IB lookup APIs, policy load/read APIs, status-page ABI, and cache initialization entry points.

## Important APIs, Types, and Functions
Key types are `struct selinux_state`, `struct selinux_load_state`, `struct av_decision`, `struct extended_perms_data`, `struct extended_perms_decision`, `struct extended_perms`, and `struct selinux_kernel_status`. Important inline APIs expose initialization state, enforcing mode, fixed `checkreqprot`, and policy capabilities such as `selinux_policycap_netpeer()`, `selinux_policycap_netlink_xperm()`, and `selinux_policycap_memfd_class()`. Declared services include `security_compute_av()`, `security_compute_xperms_decision()`, context/SID conversion, transition/member/change SID computation, NetLabel conversion, network SID lookup, genfs lookup, boolean/policy metadata lookup, netlink message lookup, and allocator-cache initialization.

## Control Flow
Callers load a policy through `security_load_policy()`, publish it via `selinux_policy_commit()`, or cancel with `selinux_policy_cancel()`. Permission paths compute `av_decision` and optional extended permissions from subject SID, target SID, class, driver, and base permission. Labeling paths convert between strings and SIDs, compute transition/member/change SIDs, and validate transitions. Network and filesystem hooks call specialized lookup helpers to map ports, nodes, interfaces, genfs paths, and NetLabel security attributes to SIDs.

## State and Persistence
`selinux_state` persists enforcing state when development mode is enabled, initialization state, policy capability bits, the mmap status page, and the RCU-protected active policy under `policy_mutex`. The status-page ABI persists sequence, enforcing, policyload, and deny-unknown values for userspace. Policycap and mount flags influence behavior until the next policy reload or remount.

## Dependencies and Integration Points
Depends on generated SELinux `flask.h` classes/permissions, policy capability definitions, RCU, mutexes, workqueues, VFS dentries/superblocks, NetLabel declarations, and selinuxfs/netlink consumers. It is included by most SELinux implementation files, so ABI-like changes ripple broadly.

## Risks
Policy version constants gate binary policy compatibility and must match readers/writers. `selinux_state.initialized` uses acquire/release ordering; weakening that risks policy visibility races. Extended-permission bit math assumes 256-bit driver windows. Stub NetLabel functions must return errors that callers treat as nonlabel support, not success.

## Test Signals
Validate policy load/read across supported policy versions, enforcing toggles, policycap reporting, SID/context conversion including invalid contexts, extended permissions for ioctls/netlink, NetLabel enabled/disabled builds, status-page mmap updates, and network/filesystem SID lookups after policy reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/security.h -->
