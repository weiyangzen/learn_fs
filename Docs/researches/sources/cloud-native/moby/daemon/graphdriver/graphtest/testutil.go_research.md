# sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil.go

Purpose: shared graphdriver test helpers for deterministic file content, layer mutations, and assertions.

Important APIs and control flow: `randomContent` creates deterministic pseudo-random bytes from a seed. Helpers mount layers with `Get`, defer `Put`, and create/check/remove files and directories. `addManyFiles`, `changeManyFiles`, and `checkManyFiles` build grouped directory/file workloads and expected `archive.Change` entries. `checkChanges` sorts expected and actual changes before comparing. `addManyLayers` chains random layer IDs and writes per-layer marker files; `checkManyLayers` verifies the top layer and parent chain markers. `readDir` hides `lost+found` to normalize ext filesystems.

State, dependencies, and risks: helpers mutate real graphdriver layers through mounted paths, so correctness depends on driver `Get`/`Put` and filesystem behavior. Paths are joined with OS filepath, while some expected change paths include leading slash-style archive paths. Risks include hidden assumptions about permissions, deterministic random content size, and change-kind semantics. The helpers underpin nearly all graphtest conformance and benchmark signals.
