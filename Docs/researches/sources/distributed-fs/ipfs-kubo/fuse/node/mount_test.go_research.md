<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_test.go

## Purpose

This file tests node-level mount orchestration, especially detection of external unmounts for `/ipfs`, `/ipns`, and `/mfs`.

## Important APIs, Types, and Functions

`mkdir` creates mount directories. `TestExternalUnmount` mounts all three filesystems, invokes the platform unmount command externally, waits briefly, then asserts `IsActive` is false and `Unmount` returns `mount.ErrNotMounted`. `setupAllMounts` creates an online mock node, initializes IPNS keyspace, creates temp mountpoints, mounts all filesystems, and registers cleanup.

## Control Flow, State, and Integration

The test exercises `node.Mount`, individual mount implementations, and the `fuse/mount` goroutine that watches `fuse.Server.Wait`. State is real FUSE kernel mount state plus node `Mounts` fields.

## Dependencies, Risks, and Test Signals

Dependencies include FUSE availability, mock core nodes, IPNS initialization, and system unmount commands. Risks are timing sensitivity after external unmount and environment-specific helper behavior. Passing tests confirm active-state reconciliation and idempotent cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_test.go -->
