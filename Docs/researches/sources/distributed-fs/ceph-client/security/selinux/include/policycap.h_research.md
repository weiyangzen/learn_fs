## sources/distributed-fs/ceph-client/security/selinux/include/policycap.h

### Purpose
`policycap.h` enumerates SELinux policy capabilities: feature flags set by policy that opt into newer kernel SELinux semantics or capabilities.

### Important APIs, types, and functions
The enum includes capabilities for network peer controls, open permission, extended socket classes, always-check-network, cgroup seclabels, NNP/nosuid transitions, genfs symlink labels, ioctl cloexec skip, userspace initial context, netlink extended permissions, netif/genfs wildcards, functionfs seclabels, memfd class, and BPF token permissions. It defines `__POLICYDB_CAP_MAX`, `POLICYDB_CAP_MAX`, and declares `selinux_policycap_names[]`.

### Control flow
Policy load code maps names to enum bits. Runtime code reads `selinux_state.policycap[index]` through helper functions in `security.h` and branches on enabled semantics throughout `hooks.c`.

### State and persistence
This header stores no live state. Policy capability state lives in loaded policy and `selinux_state.policycap[]`.

### Dependencies and integration points
It is included by `policycap_names.h`, `security.h`, `ima.c`, selinuxfs, and security-server policy parsing.

### Risks
Adding a capability requires updating this enum, names, policy parsing/validation, IMA measurement length, and any runtime helper. Ordering must stay aligned with names and policy encoding.

### Test signals
Load policies with each capability, verify selinuxfs policycap entries, IMA state strings, and behavior toggles in hooks such as openperm, extsockclass, memfd, netlink xperm, and BPF token permissions.
