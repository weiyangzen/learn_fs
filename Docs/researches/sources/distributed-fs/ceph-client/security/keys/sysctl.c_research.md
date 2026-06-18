# sources/distributed-fs/ceph-client/security/keys/sysctl.c

## Purpose

`sysctl.c` registers `/proc/sys/kernel/keys` controls for the key management subsystem. It exposes quota and garbage-collection tunables used by normal users, root, and persistent keyrings.

## Important APIs, Types, and Functions

`key_sysctls[]` contains `ctl_table` entries for `maxkeys`, `maxbytes`, `root_maxkeys`, `root_maxbytes`, `gc_delay`, and, under `CONFIG_PERSISTENT_KEYRINGS`, `persistent_keyring_expiry`. Each entry points at global keyring variables declared in key internals and uses `proc_dointvec_minmax` with lower/upper bounds. `init_security_keys_sysctls()` calls `register_sysctl_init("kernel/keys", key_sysctls)` and is registered with `early_initcall()`.

## Control Flow

At early init, the sysctl table is registered once. Runtime reads and writes are handled by the sysctl core, which clamps values through the min/max handler. Most values require at least `1`; delay and persistent expiry allow `0`.

## State and Persistence Behavior

The file does not persist data itself. It exposes mutable kernel globals that affect later key allocations, quota reservations, garbage collection delay, and persistent-keyring expiry. Settings persist only for the running kernel unless user space re-applies sysctl configuration.

## Dependencies and Integration Points

The file integrates with the sysctl framework, the key quota variables in `security/keys/internal.h`, and persistent keyring support when enabled. It is intentionally small because policy is enforced by the key allocation and GC code elsewhere.

## Risks and Test Signals

Bad bounds would let administrators set impossible quotas or negative delays. Useful tests are sysctl read/write smoke tests, boundary writes of `0`, `1`, and `INT_MAX`, and key allocation attempts before and after quota changes.
