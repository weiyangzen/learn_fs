# Research: sources/cloud-native/containerd/internal/cri/sputil/seccomp_linux_test.go

This Linux test file verifies seccomp profile parsing and spec option generation. `TestGenerateSeccompSecurityProfileSpecOpts` uses table cases for legacy string profile inputs, default profile fallback, privileged containers, disabled seccomp support, unconfined/no-profile behavior, runtime/docker defaults, localhost profiles, and direct CRI `SecurityProfile` structs.

Expected spec options are applied to an OCI runtime spec with Linux process capabilities, and actual options are applied to a deep copy of the same spec. Comparing the mutated specs validates that `seccomp.WithDefaultProfile` and `seccomp.WithProfile` produce the intended effect. The capability-rich process fixture also exercises more of the default seccomp profile generation path.

The tests cover important risks: unsupported seccomp requests fail loudly unless unconfined/nil, privileged containers skip seccomp, unset profile can use configured default, localhost prefixes are trimmed for both legacy and struct paths, and `LocalhostRef` on runtime-default profiles is invalid. Gaps include actual seccomp profile file existence, container runtime enforcement, non-Linux behavior, and malformed profile paths beyond the parser cases. This is a pure unit test suite with no persistent state.
