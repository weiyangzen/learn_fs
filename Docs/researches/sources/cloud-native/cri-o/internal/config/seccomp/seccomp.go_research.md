# sources/cloud-native/cri-o/internal/config/seccomp/seccomp.go

Purpose: manages seccomp enablement, CRI-O’s adjusted default profile, profile loading, OCI artifact profile resolution, and application of selected profiles to OCI specs.

Important APIs/types/functions: `DefaultProfile`, `validateSyscallIndex`, `removeStringFromSlice`, `Config`, `New`, `SetNotifierPath`, `NotifierPath`, `LoadProfile`, `LoadDefaultProfile`, `IsDisabled`, `Profile`, `Setup`, and `applyProfileFromBytes`.

Control flow: `DefaultProfile` lazily clones Podman/common’s default profile, removes `clone`, `clone3`, and `unshare` from an allow list, re-adds them only for `CAP_SYS_ADMIN`, blocks namespace-creating `clone` for non-`CAP_SYS_ADMIN`, and makes non-admin `clone3` return `ENOSYS` for glibc fallback. `Setup` first lets OCI artifact annotations provide a profile when the security field is nil or unconfined. Nil profile means unconfined. Disabled seccomp allows only unconfined/runtime-default semantics, rejecting custom profiles. Runtime default loads the configured profile into the generator config and may inject a notifier. Localhost reads the specified file and applies it from bytes.

State and persistence behavior: caches the default profile globally with `sync.Once`. `Config` holds enabled flag, current profile pointer, and notifier base path. It reads profile files and OCI artifact data but writes no profile state.

Dependencies/integration points: depends on goccy JSON, runtime-tools generator, Podman/common seccomp, CRI API `SecurityProfile`, image system context, unix constants, CRI-O seccomp OCI artifact store, and CRI-O tracing/logging. Container creation calls this to set `specGenerator.Config.Linux.Seccomp`.

Risks: `validateSyscallIndex` fatal-exits when upstream default profile layout changes, intentionally making vendor bumps loud. Default profile mutation relies on exact syscall list indexes. OCI artifact profiles take priority only when profile field is nil/unconfined. The disabled-seccomp branch policy is subtle for runtime default versus localhost.

Test signals: `seccomp_test.go` covers default profile retrieval, profile file loading, default reload, runtime-default setup, localhost setup, and missing localhost errors under enabled seccomp.
