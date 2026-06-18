# Research: sources/cloud-native/containerd/client/pull.go

## Purpose
Implements high-level image pulling: resolve a remote reference, fetch content, optionally unpack it into snapshots, then create/update an image record and return a platform-bound `Image`.

## Important APIs, Control Flow, And State
`Client.Pull` builds a `RemoteContext`, configures resolver transfer options, validates single-platform local pull semantics, starts tracing, creates a lease, optionally initializes an `unpack.Unpacker`, wraps handlers so content can be unpacked as it is fetched, calls `fetch`, waits for deferred unpack, creates or updates the image with `createNewImage`, and falls back to `Image.Unpack` when the unpacker saw no unpackable manifests. `fetch` resolves/fetches through a resolver, rejects Docker schema 1, builds a handler chain for fetching, legacy config detection, children/platform filtering, labels, referrers, distribution source labels, and optional wrapper, dispatches descriptors, converts legacy Docker manifests when needed, and returns an image target. Persistent state includes content blobs, labels, snapshots, and image records.

## Dependencies And Integration
Uses remotes, Docker resolver helpers, transfer options, unpack, platform matching, tracing, image handlers, semaphores, and errdefs. It is the main client entry point for remote image ingestion.

## Risks And Test Signals
Risks include platform selection errors, unsupported schema 1 references, handler wrapper ordering, unpack wait errors surfaced after fetch, concurrent image create/update races, and all-metadata behavior. Tests should cover resolver option propagation, multi-platform rejection, unpack success/fallback, referrers, legacy conversion, distribution labels, and image update races.
