## sources/cloud-native/moby/daemon/internal/image/store_test.go

Purpose: Tests image store lifecycle and metadata behavior.

Important tests: `TestCreate` rejects missing RootFS. `TestRestore` seeds backend content including invalid JSON, restores two valid images, checks parent/children/heads/search and not-found behavior. `TestAddDelete` creates parent/child images, sets parent, deletes parent, and verifies child remains with parent metadata cleared. `TestSearchAfterDelete` ensures digestset removal. `TestDeleteNotExisting` checks not-found classification. `TestParentReset` moves a child from one parent to another. `TestGetAndSetLastUpdated` checks zero default and persisted timestamp. `TestStoreLen` checks map length after several creates.

Control flow and state: `defaultImageStore` uses a temporary FS backend and `mockLayerGetReleaser` that returns nil layers. Tests use static JSON configs and known digest expectations.

Dependencies and integration: Uses containerd errdefs matching, daemon layer metadata interfaces, and `gotest.tools`.

Risks covered: Invalid restore entries are skipped, parent metadata reconstruction, partial ID lookup, delete cleanup, and metadata writes. Gaps include actual layer retention/release behavior, OS mismatch, builtLocally metadata, and create failures after backend writes.

Persistence: Exercises temporary on-disk backend state and in-memory restored state.
