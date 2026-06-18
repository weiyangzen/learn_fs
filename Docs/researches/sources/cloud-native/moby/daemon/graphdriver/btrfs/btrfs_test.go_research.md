# sources/cloud-native/moby/daemon/graphdriver/btrfs/btrfs_test.go

Purpose: Btrfs graphdriver conformance tests.

Important APIs and control flow: `TestBtrfsSetup` acquires a shared `graphtest` driver. `TestBtrfsCreateEmpty`, `TestBtrfsCreateBase`, and `TestBtrfsCreateSnap` run generic layer creation and snapshot validation. `TestBtrfsSubvolDelete` creates a writable layer, creates a nested Btrfs subvolume inside its mounted filesystem, removes the layer, and asserts the nested subvolume path no longer exists. `TestBtrfsTeardown` releases the shared driver.

State, dependencies, and risks: tests require Linux, cgo, a Btrfs-backed temp driver root, and privileges/capabilities sufficient for Btrfs ioctls. The shared driver pattern means setup/teardown ordering matters, and a failed intermediate test can leave cleanup work to `PutDriver`. The strongest signal is recursive subvolume deletion, which protects against leaked child subvolumes that regular directory removal cannot handle.
