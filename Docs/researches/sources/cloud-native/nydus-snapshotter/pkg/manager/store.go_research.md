# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/store.go

This file defines the `Store` interface for daemon and RAFS persistence. It includes daemon CRUD and walking, RAFS instance CRUD and walking, cleanup, and sequence allocation through `NextInstanceSeq`. The compile-time assertion ensures `store.DaemonRafsStore` implements the interface.

The interface is used by `Manager` to persist `daemon.ConfigState` and whole `rafs.Rafs` records. It is central to restart recovery because `Manager.Recover` walks daemon and RAFS records to reconstruct in-memory cache and mount state. `AddRafsInstance` obtains a sequence number from this store so RAFS recovery can later preserve mount order.

This file contains no concrete control flow, but it defines a contract boundary between manager orchestration and the database layer. Risks include interface changes affecting store implementations, no explicit transaction grouping between daemon and RAFS updates, and reliance on callers to update store before cache. There are no direct tests here; store behavior is tested wherever `store.DaemonRafsStore` is covered.
