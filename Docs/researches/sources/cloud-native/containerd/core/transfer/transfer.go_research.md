# sources/cloud-native/containerd/core/transfer/transfer.go

## Purpose
This file defines the core transfer abstraction and endpoint interfaces used across local and proxy transfer implementations.

## Important APIs, Types, and Functions
`Transferrer` exposes `Transfer`. Source/destination contracts include resolver/fetcher/pusher, image filter/store/get/lookup, importer/exporter, stream import/export, unpacker, and platform getter interfaces. Options include progress, download limiter, max concurrent downloads, and concurrent layer fetch buffer. `Progress` is the common progress event shape.

## Control Flow
There is no implementation; concrete services use these interfaces as a dispatch matrix. Option functions mutate simple config structs.

## State and Persistence
No persistence. The interfaces describe which implementations may read/write content, images, remote registries, streams, and snapshots.

## Dependencies and Integration Points
This package connects content store writers, image store records, OCI descriptors/platforms, `images.HandlerFunc`, and `semaphore.Weighted`. Local transfer and proxy transfer are primary consumers.

## Risks
Because routing is interface-based, endpoint types implementing multiple contracts can be dispatched differently depending on source/destination combinations. Progress event names are convention-based rather than typed enums.

## Test Signals
Covered through tests of concrete local, image, registry, streaming, and integration client behavior.
