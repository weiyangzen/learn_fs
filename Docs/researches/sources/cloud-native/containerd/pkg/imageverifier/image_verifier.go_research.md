# sources/cloud-native/containerd/pkg/imageverifier/image_verifier.go

Purpose: defines the minimal image-verification contract used by containerd components and implementations such as `bindir`.

Important APIs/types/functions: `ImageVerifier` is an interface with `VerifyImage(ctx, name, desc) (*Judgement, error)`. `Judgement` contains `OK bool` and `Reason string`.

Control flow: none directly. Implementations decide how to inspect the image name and OCI descriptor, whether to accept or reject, and whether failures are infrastructure errors or negative judgements.

State/persistence: no state. `Judgement` is a transient result object suitable for callers to log or surface.

Dependencies/integration: imports `context` and OpenContainers image-spec descriptors. `pkg/imageverifier/bindir` implements this interface and uses `Judgement` to aggregate external verifier decisions.

Risks: the interface intentionally does not distinguish policy rejection from infrastructure failure except through `Judgement.OK` vs returned error; callers must preserve that distinction. `Reason` is unstructured text and may include external verifier output.

Test signals: implementation tests should assert accept, reject, and error paths all map to the expected interface semantics.
