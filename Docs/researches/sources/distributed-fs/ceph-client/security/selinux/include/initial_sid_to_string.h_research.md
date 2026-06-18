## sources/distributed-fs/ceph-client/security/selinux/include/initial_sid_to_string.h

### Purpose
`initial_sid_to_string.h` maps generated SELinux initial SID numbers to their string names. Initial SIDs label kernel/bootstrap objects before full policy-derived labels are available.

### Important APIs, types, and functions
The file defines `static const char *const initial_sid_to_string[]`. Entries include `kernel`, `security`, `unlabeled`, `file`, `init`, `any_socket`, `port`, `netif`, `netmsg`, `node`, and `devnull`, with null placeholders for obsolete or unnamed initial SIDs.

### Control flow
Consumers index the array by initial SID numeric constant. There is no logic other than compile-time data selection for kernel vs host-program include paths.

### State and persistence
The table is static read-only data. It is part of the generated/compiled SELinux policy interface and must align with initial SID constants.

### Dependencies and integration points
It includes `stddef.h` or kernel `linux/stddef.h`. It is used by SELinux tooling/security-server code that needs textual initial SID names.

### Risks
Array ordering must remain synchronized with `SECINITSID_*` constants. Null placeholders are intentional; consumers must tolerate missing names.

### Test signals
Build generated headers and policy tooling, verify initial SID string lookups, and test boot labels before policy load.
