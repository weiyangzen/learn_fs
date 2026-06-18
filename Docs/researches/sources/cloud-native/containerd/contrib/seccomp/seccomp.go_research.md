# sources/cloud-native/containerd/contrib/seccomp/seccomp.go

Purpose: OCI spec options for attaching seccomp profiles to container specs.

Important APIs: `WithProfile(profile string)` returns an `oci.SpecOpts` that initializes `s.Linux.Seccomp`, reads a JSON seccomp profile from disk, and unmarshals it into the runtime-spec structure. `WithDefaultProfile()` returns an `oci.SpecOpts` that calls `DefaultProfile(s)`.

Control flow and state: both options mutate only the in-memory OCI `specs.Spec` passed by containerd OCI generation. `WithProfile` performs a synchronous file read and JSON decode. `WithDefaultProfile` depends on process capabilities already being set, because default syscall allowances are capability-sensitive.

Dependencies and integration: integrates with `github.com/containerd/containerd/v2/pkg/oci` spec option pipelines, `core/containers.Container`, and `opencontainers/runtime-spec/specs-go`. It depends on the platform-specific `DefaultProfile` implementation in sibling files.

Risks: both functions assume `s.Linux` is non-nil; callers must use normal Linux spec initialization before applying them. A malformed or unavailable profile fails container spec generation. Applying default profile before capabilities are configured can produce an over- or under-permissive profile.

Test signals: default profile behavior is covered in `seccomp_default_test.go`; external profile loading errors are not directly tested here.
