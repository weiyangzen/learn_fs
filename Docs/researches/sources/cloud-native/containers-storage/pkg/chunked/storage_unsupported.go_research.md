## sources/cloud-native/containers-storage/pkg/chunked/storage_unsupported.go

Purpose: non-Linux fallback implementation of `NewDiffer`.

Important APIs/types/functions: `NewDiffer` with `//go:build !linux`.

Control flow: ignores the detailed inputs and returns `ErrFallbackToOrdinaryLayerDownload` wrapping "format not supported on this system".

State and persistence: none.

Dependencies and integration points: preserves API availability for non-Linux builds while directing callers to ordinary layer download. Depends on storage and graphdriver interfaces only for signature compatibility.

Risks: callers that require partial images must treat the fallback wrapper correctly; no conversion path exists on unsupported platforms.

Test signals: no direct tests selected. Behavior is simple but depends on build tags.
