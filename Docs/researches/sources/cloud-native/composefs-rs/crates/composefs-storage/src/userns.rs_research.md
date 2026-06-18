# sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns.rs

Purpose: Provides the permission-bypass probe used to decide whether rootless containers-storage access needs a helper running inside `podman unshare`.

Important APIs and types: The single public API is `can_bypass_file_permissions() -> bool`. It checks whether the current process is real root or has `CAP_DAC_OVERRIDE` in its effective capability set.

Control flow: The function first calls `rustix::process::getuid()` and returns true for UID 0. Otherwise it calls `rustix::thread::capabilities(None)` and checks `CapabilitySet::DAC_OVERRIDE`. Capability-query failure is nonfatal and falls through to false.

State and persistence: There is no persisted state. The result reflects current process credentials and effective capabilities at the moment of the call.

Dependencies and integration: Depends on `rustix` process and thread capability APIs. `StorageProxy::spawn` in `userns_helper.rs` uses this as a fast path to skip spawning a user namespace helper when the current process can already read restrictive overlay files.

Risks: It only tests DAC override style permission bypass. Other access-control systems, mount namespaces, LSM policy, or missing execute permissions on parent directories can still affect real file access. A transient capabilities error is treated as "cannot bypass", causing a helper spawn attempt.

Test signals: The unit test verifies deterministic repeated results and asserts root returns true. It does not emulate Linux capability combinations.
