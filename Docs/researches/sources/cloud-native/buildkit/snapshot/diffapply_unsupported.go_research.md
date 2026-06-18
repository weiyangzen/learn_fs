## sources/cloud-native/buildkit/snapshot/diffapply_unsupported.go

Purpose: non-Linux fallback for merge diff application.

Important APIs/types/functions: `mergeSnapshotter.diffApply` returns an error saying diffApply is not supported on the current GOOS. `needsUserXAttr` similarly returns unsupported.

Control flow: direct error return only.

State and persistence: none.

Dependencies and integration points: selected by `//go:build !linux`; lets the package compile on unsupported platforms while preventing runtime merge behavior from silently doing the wrong thing.

Risks and test signals: callers of `Merge` on non-Linux will fail when diff application is needed. Platform-specific local mounters still exist, but merge application is Linux-only. Tests for merge are Linux build-tagged.
