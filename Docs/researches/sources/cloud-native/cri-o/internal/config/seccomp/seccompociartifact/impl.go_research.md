# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/impl.go

Purpose: defines the minimal datastore abstraction needed by seccomp OCI artifact resolution.

Important APIs/types/functions: `Impl` interface with `PullData(context.Context, string, *datastore.PullOptions) ([]datastore.ArtifactData, error)`.

Control flow: no implementation; `SeccompOCIArtifact` depends on this interface to pull artifact bytes.

State and persistence behavior: none in this file.

Dependencies/integration points: references CRI-O `internal/ociartifact/datastore`. Tests replace the implementation through a test-only setter to mock pull behavior.

Risks: the interface exposes only pull data; callers cannot inspect source metadata beyond returned artifact data.

Test signals: mocked in `seccompociartifact_test.go`.
