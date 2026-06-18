<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_test.go

## Purpose

This file tests the `/ipns` FUSE mount and adapts the shared writable suite to the writable `/ipns/local` directory. It also covers IPNS-specific symlink, namespace mode, persistence, and statfs behavior.

## Important APIs, Types, and Functions

`mountWrap` tracks the mounted directory, `Root`, and go-fuse server. `fakeMount` simulates an active daemon IPNS mount so publish guards are exercised. `setupIpnsTest` creates or reuses a node, initializes keyspace, builds CoreAPI, creates a root with alias `local`, mounts it with writable capabilities, and sets `nd.Mounts.Ipns`. `newIpnsMount` translates `writable.Config` to `config.Mounts` and returns `/local`.

## Control Flow, State, and Integration

The tests create real FUSE mounts, write through MFS-backed IPNS directories, close roots to flush/publish, and remount against the same node to check persistence. `TestIpnsLocalLink` verifies the alias symlink points to the peer ID directory. `TestNamespaceRootMode` checks execute-only root permissions. `TestStatfs` points the root at a real repo directory and verifies non-zero filesystem stats.

## Dependencies, Risks, and Test Signals

Dependencies include Kubo core, CoreAPI, config, go-fuse, `fusetest`, and `fuse/writable`. Risks covered include issue #2168's publish guard bypass, missing root close on unmount, stale IPNS state after remount, incorrect namespace permissions, and Finder-visible zero statfs values. The broad writable suite provides regression coverage for POSIX operations on `/ipns/local`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_test.go -->
