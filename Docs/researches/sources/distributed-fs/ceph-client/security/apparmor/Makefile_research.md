# sources/distributed-fs/ceph-client/security/apparmor/Makefile

## Purpose
This Makefile assembles the AppArmor LSM object, conditionally includes hash support, builds the KUnit policy-unpack test, and generates compile-time name tables for capabilities, rlimits, and network families/types. It is the concrete build graph for the AppArmor directory.

## Important build targets
- `obj-$(CONFIG_SECURITY_APPARMOR) += apparmor.o` creates the main linked AppArmor object.
- `apparmor-y` lists core components: apparmorfs, audit, capability, task, ipc, lib, match, path, domain, policy, policy_unpack, procattr, lsm, resource, secid, file, policy_ns, label, mount, net, policy_compat, and af_unix.
- `apparmor-$(CONFIG_SECURITY_APPARMOR_HASH) += crypto.o` adds SHA-256 policy hashing.
- `obj-$(CONFIG_SECURITY_APPARMOR_KUNIT_TEST)` builds `apparmor_policy_unpack_test.o` from `policy_unpack_test.o`.
- Generated headers are `capability_names.h`, `rlim_names.h`, and `net_names.h`.

## Control flow and generated data
The sed pipelines transform UAPI/kernel definitions into lowercase string arrays and securityfs feature masks. Capability names feed `capability.c` audit output and `AA_SFS_CAPS_MASK`; rlimit names feed resource policy output and `AA_SFS_RLIMIT_MASK`; network family/type names feed network policy feature reporting.

## State and persistence
Generated headers are build artifacts, not source state. They are marked in `clean-files`, so normal kernel clean targets remove them. The generated names become compiled-in read-only lookup tables used by audit and apparmorfs feature reporting.

## Dependencies
The generation rules depend on `include/uapi/linux/capability.h`, `include/uapi/asm-generic/resource.h`, `include/linux/socket.h`, and `include/linux/net.h`. They also depend on GNU sed behavior including extended regex and lowercase conversion.

## Risks
Regex drift against upstream header formatting can silently omit names or masks. The network generator intentionally excludes `AF_MAX`, `AF_LOCAL`, and `AF_ROUTE`, so compatibility assumptions must be explicit. Build failures or stale generated headers would directly affect audit readability and userspace feature discovery.

## Test signals
Build with AppArmor enabled and confirm generated headers appear before dependent objects compile. Inspect generated masks for expected capabilities, rlimits, families, and socket types. KUnit builds should include only `policy_unpack_test.o` through the declared test object.
