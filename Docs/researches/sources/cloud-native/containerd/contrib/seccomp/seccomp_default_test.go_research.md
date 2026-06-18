# sources/cloud-native/containerd/contrib/seccomp/seccomp_default_test.go

Purpose: regression test for one security property of the default seccomp profile.

Important test: `TestIOUringIsNotAllowed` builds a default profile with an empty bounding capability set and scans all `ActAllow` syscall entries for `io_uring_enter`, `io_uring_register`, and `io_uring_setup`.

Control flow and state: constructs a minimal `specs.Spec` with `Process.Capabilities.Bounding` initialized, calls `DefaultProfile`, and fails if any disallowed io_uring syscall is in an allow rule.

Dependencies and integration: depends on the Linux default profile implementation and runtime-spec types. It is a targeted security regression test, not a profile conformance suite.

Risks: it only detects allowlisted io_uring names in `ActAllow` blocks; it does not validate default action, `ErrnoRet`, arch lists, capability gates, socket filters, or kernel-version behavior.

Test signals: strong signal for the explicit io_uring policy. Additional tests would be valuable for nil capability handling, blocked socket domains, `clone3` ENOSYS, and capability-derived syscalls.
