## sources/distributed-fs/ceph-client/security/selinux/ima.c

### Purpose
`ima.c` measures SELinux critical state into IMA: initialization state, enforcing mode, checkreqprot value, policy capability booleans, and the loaded policy hash. This lets integrity/audit infrastructure detect policy and state changes relevant to SELinux enforcement.

### Important APIs, types, and functions
The exported functions are `selinux_ima_measure_state()` and `selinux_ima_measure_state_locked()`. The internal helper `selinux_ima_collect_state()` builds a semicolon-delimited state string such as `initialized=1;enforcing=1;...policycap=0;` using `selinux_policycap_names[]` and `selinux_state.policycap[]`.

### Control flow
`selinux_ima_measure_state()` asserts the policy mutex is not already held, locks `selinux_state.policy_mutex`, delegates to the locked variant, and unlocks. The locked variant asserts the mutex is held, builds the state string, measures it as `selinux-state`, frees it, then returns early if SELinux is not initialized. Once initialized, it reads the kernel policy via `security_read_state_kernel()`, measures it as `selinux-policy-hash` with hashing enabled, and frees the vmalloc policy buffer.

### State and persistence
The file does not persist state itself. It snapshots live SELinux state and policy bytes into IMA measurements. Memory ownership is explicit: `kzalloc`/`kfree` for the state string and `security_read_state_kernel()`/`vfree()` for the policy buffer.

### Dependencies and integration points
It depends on IMA (`<linux/ima.h>`), vmalloc freeing, `security.h`, and `ima.h`. `selinuxfs.c` and security-server policy load paths call these functions to measure SELinux state after user-visible state or policy changes.

### Risks
Buffer length calculation must stay aligned with policy capability names and fixed state keys. Missing a new state knob would weaken integrity coverage. Locking discipline matters: policy bytes and policycap state must be read under `policy_mutex` for coherent measurement.

### Test signals
Run with `CONFIG_IMA`, load policy, toggle enforcing/booleans/policy capabilities where possible, and verify IMA contains `selinux-state` and `selinux-policy-hash` records. Also test allocation/read failures for logged errors without leaks.
