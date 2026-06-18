# sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_unix.go

Purpose: reusable Unix conformance tests for graphdriver implementations.

Important APIs and control flow: `GetDriver` lazily creates a shared temp-root driver by name and increments a refcount; `PutDriver` decrements and cleans up. `DriverTestCreateEmpty` verifies a new empty layer exists, mounts, has expected directory metadata, and contains no entries except filtered `lost+found`. `DriverTestCreateBase` and `DriverTestCreateSnap` validate base creation and parent snapshot content. `DriverTestDeepLayerRead` builds many layers and checks top-layer and lower-file visibility. `DriverTestDiffApply` builds a base and upper, removes entries, diffs upper, applies into a sibling layer, compares size, content, and deletions. `DriverTestChanges` compares reported change lists. `DriverTestSetQuota` writes below and above a requested quota and expects `EDQUOT` or `ENOSPC`.

State, dependencies, and risks: shared driver state makes setup/teardown order important. Tests require Unix filesystem semantics, mount privileges depending on driver, and quota support for quota tests. These are the primary cross-driver behavioral signals for create/get/put/remove/diff/apply/quota.
