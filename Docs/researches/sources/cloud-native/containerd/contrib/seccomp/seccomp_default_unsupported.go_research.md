# sources/cloud-native/containerd/contrib/seccomp/seccomp_default_unsupported.go

Purpose: non-Linux fallback for `DefaultProfile`.

Important API: under build tag `!linux`, `DefaultProfile(sp *specs.Spec)` returns an empty `specs.LinuxSeccomp` object.

Control flow and state: no logic, no state, ignores the input spec. It exists to satisfy package builds on unsupported platforms.

Dependencies and integration: imports runtime-spec types only. Used indirectly by `WithDefaultProfile` on non-Linux builds.

Risks: callers expecting meaningful enforcement on non-Linux receive an empty profile. This is likely acceptable because Linux seccomp is not portable, but downstream code should not interpret the returned object as a hardened policy.

Test signals: no direct tests. Build coverage on non-Linux platforms is the main signal.
