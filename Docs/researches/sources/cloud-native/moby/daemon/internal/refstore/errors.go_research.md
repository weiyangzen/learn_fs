<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/errors.go -->
# sources/cloud-native/moby/daemon/internal/refstore/errors.go

Purpose: defines typed errors for image reference store operations.

Important APIs and types: `notFoundError`, `invalidTagError`, and `conflictingTagError`, implementing Docker/containerd errdefs marker methods.

Control flow: each type returns its string message and exposes marker methods `NotFound`, `InvalidParameter`, or `Conflict`.

State and persistence: none.

Dependencies and integration: used by `store.go` so callers can classify reference errors through errdefs helpers.

Risks: marker methods have no payload beyond string text; callers needing structured context must parse or wrap elsewhere.

Test signals: `store_test.go` checks conflict and invalid-argument classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/errors.go -->
