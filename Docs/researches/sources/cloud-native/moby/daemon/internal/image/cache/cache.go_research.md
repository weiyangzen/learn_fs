## sources/cloud-native/moby/daemon/internal/image/cache/cache.go

Purpose: Implements builder image cache resolution against local children and optional `--cache-from` image histories.

Important APIs/types: `ImageCacheStore` abstracts image lookup, parent metadata, image creation, built-locally metadata, and child enumeration. `New` returns either `LocalImageCache` or history-based `ImageCache`. `LocalImageCache.GetCache` checks direct local children. `ImageCache.Populate`, `GetCache`, `restoreCachedImage`, `isParent`, `getLayerForHistoryIndex`, `isValidConfig`, `isValidParent`, and `getLocalCachedImage` implement cache matching and restoration.

Control flow: `New` builds a local cache, then resolves each `cacheFrom` ref with `GetByRef`, skipping missing refs but propagating context cancellation/deadline. `ImageCache.GetCache` first tries local child cache and only accepts it if the child belongs to one populated cache source. If that fails, it compares each source image against the requested parent history/rootfs and command config. Exact next-step hits return the target ID and possibly set parent metadata. Partial matches synthesize a restored cache image with one more history entry and layer diff ID.

State and persistence: In-memory `sources` list and store-backed parent/built-local/image creation metadata. `restoreCachedImage` may persist a new image through `store.Create` and `SetParent`.

Dependencies and integration: Used by the classic builder cache interface. Integrates daemon image, layer DiffID, OCI platform matching, container config comparison, logging, and ref lookup.

Risks: `isParent` is recursive and assumes parent metadata eventually terminates. `getLayerForHistoryIndex` indexes `RootFS.DiffIDs` with minimal validation. Config matching uses `strings.Join(cfg.Cmd, " ")`, which can lose argument boundaries. Cache restoration mutates `rootFS := parent.RootFS` by appending to the same pointer, so store implementations must tolerate this or callers must avoid reusing parent objects unsafely.

Test signals: `compare_test.go` covers lower-level config/platform matching; this file has no direct tests in the requested set.
