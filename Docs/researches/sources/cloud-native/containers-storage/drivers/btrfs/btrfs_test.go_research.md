# sources/cloud-native/containers-storage/drivers/btrfs/btrfs_test.go

## Purpose
`btrfs_test.go` validates Btrfs graphdriver integration through the shared `graphtest` suite and one Btrfs-specific nested subvolume deletion test.

## Important APIs, Types, And Functions
Tests include `TestBtrfsSetup`, `TestBtrfsCreateEmpty`, `TestBtrfsCreateBase`, `TestBtrfsCreateSnap`, `TestBtrfsCreateFromTemplate`, `TestBtrfsSubvolDelete`, `TestBtrfsEcho`, `TestBtrfsListLayers`, and `TestBtrfsTeardown`.

## Control Flow
The setup test creates a shared Btrfs driver with no cleanup so later tests can reuse it. Shared tests exercise create, snapshot, template, echo/diff, and list behavior. `TestBtrfsSubvolDelete` creates a layer, creates a nested Btrfs subvolume inside it, removes the layer, and asserts the nested subvolume path is gone.

## State And Persistence
Temporary graph roots are managed by `graphtest`. The nested subvolume test creates real Btrfs subvolume state inside a layer and expects `Remove` to recursively destroy it.

## Dependencies And Integration Points
The file depends on `graphdriver`, `graphtest`, Btrfs driver internals, and Linux+cgo build tags.

## Risks
Tests skip or fail depending on Btrfs support, cgo headers, filesystem type, and privileges. The shared driver pattern means setup/teardown ordering matters.

## Test Signals
Strong signal for recursive subvolume cleanup and baseline graphdriver contract behavior. Quota-specific paths are not directly covered here.
