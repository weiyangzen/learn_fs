# sources/control-plane/rook/cmd/rook/ceph/cleanup.go

## Purpose

Defines `rook ceph clean` subcommands for host cleanup, filesystem subvolume group cleanup, block pool rados namespace cleanup, and block pool cleanup.

## Important APIs, Types, and Functions

Commands are `cleanUpCmd`, `cleanUpHostCmd`, `cleanUpSubVolumeGroupCmd`, `cleanUpRadosNamespaceCmd`, and `cleanUpBlockPoolCmd`. Flags include host data path, namespace dir, monitor secret, cluster FSID, sanitize method/source/iteration. Entry points are `startHostCleanUp`, `startSubVolumeGroupCleanUp`, `startRadosNamespaceCleanup`, and `startBlockPoolCleanup`.

## Control Flow

`init()` wires flags, env-derived flags, subcommands, and RunE handlers. Host cleanup removes host path/mon store when configured, builds admin cluster info, creates a disk sanitizer, and starts disk sanitization. Resource cleanup subcommands read required names from operator controller environment variables, build context/admin cluster info, and call the corresponding cleanup package function; missing environment values terminate fatally.

## State and Persistence Behavior

The file can delete host data directories, monitor store state, sanitize disks, and remove Ceph resources associated with subvolume groups, rados namespaces, or block pools. It reads Kubernetes namespace and cleanup target names from environment variables.

## Dependencies and Integration Points

It integrates with `pkg/daemon/ceph/cleanup`, Ceph API clients, Ceph CRD types, operator controller env constants, Rook logging/flag env helpers, and Kubernetes pod namespace conventions.

## Risks and Edge Cases

Cleanup is destructive by design. Incorrect environment variables or flags can target the wrong resource or disk. `startBlockPoolCleanup` logs startup info using `cleanUpRadosNamespaceCmd.Flags()` instead of block pool flags, which looks like a copy/paste bug affecting logs.

## Test Signals

Integration/canary OSD removal and cleanup policy tests provide end-to-end signals. Unit tests for cleanup package functions cover lower-level behavior outside this command wrapper.
