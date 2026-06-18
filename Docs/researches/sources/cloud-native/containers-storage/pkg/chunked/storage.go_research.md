## sources/cloud-native/containers-storage/pkg/chunked/storage.go

Purpose: platform-neutral public contracts and errors for chunked blob access and fallback signaling.

Important APIs/types/functions: `ImageSourceChunk`, `ImageSourceSeekable`, `ErrBadRequest`, `ErrFallbackToOrdinaryLayerDownload`, and `newErrFallbackToOrdinaryLayerDownload`.

Control flow: callers pass chunk offset/length requests to `ImageSourceSeekable.GetBlobAt`, receiving separate stream and error channels. Fallback errors wrap a root cause and remain detectable through `errors.As`/`Unwrap`.

State and persistence: no state; defines wire-like contracts between image sources and differs.

Dependencies and integration points: implemented by image source adapters, `seekableFile`, and tests; consumed heavily by `storage_linux.go` for range fetches and fallback decisions.

Risks: dual-channel API is awkward and requires careful draining; `storage_linux.go` adds `getBlobAt` to normalize it. `ErrBadRequest` drives request-merging retry behavior.

Test signals: behavior is indirectly tested in `storage_linux_test.go` and `filesystem_linux_test.go`. No direct tests in this file; local execution unavailable due to missing `go`.
