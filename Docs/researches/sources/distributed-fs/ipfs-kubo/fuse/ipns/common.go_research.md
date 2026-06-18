<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/common.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/common.go

## Purpose

This file contains the shared IPNS initialization helper used by tests and mount orchestration. It initializes a key's IPNS record to an empty directory so writable IPNS mounts have a valid MFS root.

## Important APIs, Types, and Functions

`InitializeKeyspace` creates a cancellable context from the node context, constructs `unixfs.EmptyDirNode`, pins and flushes it through `n.Pinning`, creates a `namesys.NewIPNSPublisher`, and publishes the empty directory CID with the supplied private key.

## Control Flow, State, and Integration

The function mutates node state by adding a pinned empty directory and writing an IPNS record into the repo datastore/routing backend. It is used by IPNS FUSE tests and node-level mount tests before mounting `/ipns`.

## Dependencies, Risks, and Test Signals

Dependencies are boxo UnixFS, namesys, Kubo core, libp2p crypto, and datastore-backed IPNS publishing. Risks include pin/flush failures leaving partial state and publication failures in offline or misconfigured routing contexts. Tests verify persistence by mounting, writing, unmounting, and remounting the same node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/common.go -->
