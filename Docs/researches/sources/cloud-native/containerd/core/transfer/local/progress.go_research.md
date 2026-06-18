# sources/cloud-native/containerd/core/transfer/local/progress.go

## Purpose
This file implements progress aggregation for local pull, push, and unpack operations.

## Important APIs, Types, and Functions
`ProgressTracker` tracks descriptors, parent relationships, extraction progress, and shutdown. `NewProgressTracker`, `HandleProgress`, `Add`, `MarkExists`, `AddChildren`, `ExtractProgress`, and `Wait` are the primary API. `StatusTracker` abstracts content or push status, and `NewContentStatusTracker` adapts `content.Store`.

## Control Flow
`HandleProgress` runs a goroutine loop receiving added descriptors, extraction updates, periodic ticks, and context cancellation. It polls active jobs, emits `waiting`, transfer-state, `already exists`, `complete`, `extracting`, and `extracted` events with descriptor metadata and parent refs.

## State and Persistence
Progress state is in-memory maps and channels. It reads content ingest statuses and content existence but does not persist data itself.

## Dependencies and Integration Points
Used by local pull fetch handlers, push wrappers, and unpack apply options. It depends on `content.Status`, `remotes.MakeRefKey`, OCI descriptors, `go-digest`, and transfer progress callbacks.

## Risks
Parent mappings may be incomplete if children are added before parent metadata. `Wait` uses a timeout to avoid hanging, so late progress goroutines can be cut short. Channel buffers are small and rely on nonblocking sends after closure.

## Test Signals
No direct tests; pull, push, and concurrent unpack integration provide indirect coverage.
