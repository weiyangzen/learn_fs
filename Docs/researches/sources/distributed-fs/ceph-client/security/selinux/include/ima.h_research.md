## sources/distributed-fs/ceph-client/security/selinux/include/ima.h

### Purpose
`ima.h` declares SELinux IMA measurement entry points and provides empty stubs when IMA is disabled.

### Important APIs, types, and functions
The APIs are `selinux_ima_measure_state()` and `selinux_ima_measure_state_locked()`. With `CONFIG_IMA`, they are external functions implemented in `ima.c`; otherwise, inline stubs compile away calls.

### Control flow
Callers can measure SELinux state without local `#ifdef` logic. The locked variant requires `selinux_state.policy_mutex` to be held; the unlocked variant handles locking internally.

### State and persistence
No header state exists. Measurements are emitted to IMA only in IMA-enabled builds.

### Dependencies and integration points
It includes `security.h` and is used by selinuxfs and security-server policy paths that need to record SELinux state/policy in IMA.

### Risks
Calling the locked variant without holding the policy mutex violates the implementation's lockdep assertions. Stubbed builds provide no integrity measurement signal.

### Test signals
Build with and without `CONFIG_IMA`; in IMA builds, validate measurement records after policy load or SELinux state changes.
