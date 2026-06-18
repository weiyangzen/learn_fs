## sources/distributed-fs/ceph-client/security/selinux/include/policycap_names.h

### Purpose
`policycap_names.h` defines the string names corresponding to the policy capability enum in `policycap.h`.

### Important APIs, types, and functions
The key artifact is `const char *const selinux_policycap_names[__POLICYDB_CAP_MAX]`, with names such as `network_peer_controls`, `open_perms`, `extended_socket_class`, `always_check_network`, `cgroup_seclabel`, `nnp_nosuid_transition`, `genfs_seclabel_symlinks`, `ioctl_skip_cloexec`, `userspace_initial_context`, `netlink_xperm`, `netif_wildcard`, `genfs_seclabel_wildcard`, `functionfs_seclabel`, `memfd_class`, and `bpf_token_perms`.

### Control flow
Consumers index this array by `POLICYDB_CAP_*` enum value. Security-server policy loading uses the strings to identify supported policycap names, selinuxfs exposes them, and IMA state measurement serializes them.

### State and persistence
The array is static compiled data. It represents the stable text interface between policy, selinuxfs, IMA measurement output, and runtime capability bits.

### Dependencies and integration points
It includes `policycap.h` and is included by sources that need the names rather than only enum values.

### Risks
Name ordering must exactly match `policycap.h`. Renaming a string breaks policy compatibility and changes IMA state text. Adding enum values without adding names will break userspace visibility and measurement completeness.

### Test signals
Build checks, policy load with named capabilities, selinuxfs policycap listing, and IMA `selinux-state` measurement contents should all show matching ordered names.
