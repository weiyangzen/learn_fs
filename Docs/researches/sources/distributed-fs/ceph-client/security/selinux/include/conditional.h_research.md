## sources/distributed-fs/ceph-client/security/selinux/include/conditional.h

### Purpose
`conditional.h` declares the security-server interface for SELinux policy booleans. These booleans control conditional policy rules and are exported to selinuxfs.

### Important APIs, types, and functions
The interface includes `security_get_bools(struct selinux_policy *policy, u32 *len, char ***names, int **values)`, `security_set_bools(u32 len, const int *values)`, and `security_get_bool_value(u32 index)`.

### Control flow
Consumers ask for the current policy's boolean list and values, update values by index array, or query one boolean by index. The implementation lives in the security server and is synchronized with active policy state.

### State and persistence
This header stores no state. Boolean names and values live in policy data structures and active SELinux state. Persistence across boot is userspace policy/configuration responsibility, not this header.

### Dependencies and integration points
It includes `security.h` for `struct selinux_policy` and integrates with selinuxfs boolean files and policy conditional evaluation.

### Risks
Boolean index mismatch between userspace and policy can toggle unintended conditional rules. Callers must handle allocation and lifetime of returned names/values according to the implementation contract.

### Test signals
Read and set booleans through selinuxfs, verify conditional allow rules change as expected, reload policy, and test invalid index/value lengths.
