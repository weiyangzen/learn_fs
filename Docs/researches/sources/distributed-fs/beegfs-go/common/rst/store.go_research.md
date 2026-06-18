# sources/distributed-fs/beegfs-go/common/rst/store.go

Purpose: maintains a thread-safe mapping from RST IDs to provider clients, including the special job-builder provider.

Important APIs/types are `ClientStore`, `NewClientStore`, `Get`, `JobBuilderRstId`, `UpdateConfig`, and `SetMockClientForTesting`.

Control flow: a new store starts empty with a mount point. `UpdateConfig` either initializes clients by calling `New` for each config and then adding `JobBuilderRstId=0`, or, after initialization, rejects any dynamic changes. The rejection path verifies count, forbids RST ID 0, compares existing configs with `proto.Equal`, and ensures all existing configs are present.

State is the `clients` map protected by an RW mutex plus the mount point. Once initialized, provider configs are effectively immutable for the process. The testing hook mutates the map directly under lock.

Dependencies include `sync`, filesystem provider, protobuf cloning/equality, and RST provider construction.

Integration points are worker/manager code that needs current clients by RST ID, dynamic config reload paths, and tests injecting `MockClient`.

Risks: callers are warned not to retain provider references, but the API cannot enforce that. Dynamic updates are currently all-or-nothing rejected, so config changes require restart. `SetMockClientForTesting` can bypass invariants such as adding the builder.

Test signals: `store_test.go` covers initial config and rejection of update/add/remove changes.
