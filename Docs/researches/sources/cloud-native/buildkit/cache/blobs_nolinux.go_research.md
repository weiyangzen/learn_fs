# sources/cloud-native/buildkit/cache/blobs_nolinux.go

Purpose: non-Linux stub for overlayfs blob computation.

Important APIs/types/functions: `(*immutableRef).tryComputeOverlayBlob` has the same signature as the Linux implementation and returns an unsupported error.

Control flow: no computation is attempted; it returns an empty descriptor, `ok=true`, and an error saying overlayfs diff computing is unsupported. The caller in `blobs.go` only reaches this on non-Windows paths when overlay diff was enabled, which is normally avoided outside Linux.

State and persistence behavior: no content or metadata is written.

Dependencies and integration points: keeps the package buildable on non-Linux platforms while satisfying the shared call site in `blobs.go`.

Risks: returning `ok=true` means a caller with fallback disabled will surface the unsupported error. Platform gating in callers must remain correct.

Test signals: compile coverage on non-Linux platforms is the main signal; behavior is simple enough that higher-level diff fallback tests cover it indirectly.
