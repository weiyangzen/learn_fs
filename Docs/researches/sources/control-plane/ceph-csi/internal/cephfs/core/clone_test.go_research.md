## sources/control-plane/ceph-csi/internal/cephfs/core/clone_test.go

Purpose: Unit test for clone-state-to-error translation.

Important APIs: `TestCloneStateToError` constructs a map from `cephFSCloneState` values to expected internal errors using go-ceph clone states `CloneComplete`, `CloneInProgress`, `ClonePending`, and `CloneFailed`, plus `CephFSCloneError`.

Control flow and state: The test iterates table entries and asserts `require.ErrorIs(t, state.ToError(), err)`. It is parallelized with `t.Parallel()` and does not touch Ceph or persistent state.

Dependencies and risks: Depends on `testify/require`, go-ceph admin enums, and internal CephFS errors. It verifies error wrapping compatibility but not clone cleanup, progress reporting, or actual FSAdmin interactions. Risk is map iteration obscuring case order in failure output, but coverage is focused and cheap.
