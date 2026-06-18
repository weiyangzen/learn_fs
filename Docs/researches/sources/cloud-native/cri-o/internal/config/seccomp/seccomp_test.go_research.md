# sources/cloud-native/cri-o/internal/config/seccomp/seccomp_test.go

Purpose: tests seccomp config construction, profile loading, default profile loading, and basic `Setup` behavior for runtime-default and localhost profiles.

Important APIs/types/functions: uses `seccomp.New`, `Profile`, `LoadProfile`, `LoadDefaultProfile`, `Setup`, and a helper `writeProfileFile` that writes a minimal JSON profile. It uses runtime-tools `generate.New("linux")` and CRI API `SecurityProfile`.

Control flow: each test creates a fresh config. Profile tests compare the default profile pointer/value and load a local temp profile. Setup tests skip when seccomp is disabled, then verify runtime-default setup returns the runtime-default string, localhost setup returns the local file path, and missing localhost files fail.

State and persistence behavior: writes temp profile files and mutates `sut.profile`. It may skip based on host/build seccomp enablement.

Dependencies/integration points: Ginkgo/Gomega, runtime-tools generator, CRI API security profiles, and host seccomp availability.

Risks: one conditional around "should not fail with non-existing profile" is guarded by `if sut != nil && !sut.IsDisabled()` even though enabled seccomp should make `LoadProfile` fail on missing files; this looks like a test description/condition mismatch or dead-risk path depending on build behavior. Tests do not cover OCI artifact priority, notifier injection, disabled custom-profile rejection, or default-profile syscall mutation details.

Test signals: useful smoke coverage for profile loading and setup, but important seccomp notifier and OCI artifact flows require separate tests.
