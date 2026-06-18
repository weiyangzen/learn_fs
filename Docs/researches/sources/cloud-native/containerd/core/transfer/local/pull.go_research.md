# sources/cloud-native/containerd/core/transfer/local/pull.go

## Purpose
This file implements local image pull from a remote image fetcher into content, image records, and optional snapshots.

## Important APIs, Types, and Functions
`localTransferService.pull` coordinates resolve, verify, fetch, filter, unpack, schema conversion, and store. `fetchHandler` fetches each descriptor. `getSupportedPlatform` matches requested unpack configurations to service-supported snapshotter/platform combinations.

## Control Flow
The pull sets resolver options for concurrency, resolves the image, rejects Docker schema 1, runs configured verifiers, obtains a fetcher, builds handlers for progress, content fetch, media-type bug detection, children, and distribution-source labels, optionally wraps with an unpacker, dispatches the descriptor graph, waits for unpack, converts Docker manifests affected by the legacy media-type bug, then stores image records and emits progress.

## State and Persistence
Persistent effects are fetched content, distribution labels, unpacked snapshots, uncompressed labels from unpack, and image store records. A lease protects in-flight content. Progress uses content status polling.

## Dependencies and Integration Points
Integrates remotes/docker resolver/fetcher, image verifier plugins, image filters, local transfer config, unpack package, diff progress, snapshotter remote annotations, defaults, and transfer progress callbacks.

## Risks
Descriptor graph order affects progress parent tracking. Unpack is asynchronous and must always be waited on before storing the image. Schema 1 is rejected. Platform/snapshotter matching prefers default snapshotter when requested snapshotter is empty, which may surprise configurations with multiple matches.

## Test Signals
`pull_test.go` directly covers `getSupportedPlatform`. Integration client tests cover pull, selected platforms, all platforms, discard content after unpack, concurrency limit, tracing, and concurrent unpacks.
