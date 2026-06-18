# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact_test_inject.go

Purpose: exposes a test-only setter for replacing `SeccompOCIArtifact`’s implementation.

Important APIs/types/functions: `(*SeccompOCIArtifact).SetImpl(impl Impl)`.

Control flow: directly assigns the provided implementation to `s.impl`.

State and persistence behavior: mutates only the in-memory implementation pointer.

Dependencies/integration points: build tag `test` keeps the hook out of production builds; tests use it to install a gomock implementation.

Risks: bypasses constructor invariants and should remain test-only.

Test signals: used by `seccompociartifact_test.go`.
