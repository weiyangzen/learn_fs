<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_unsupported.go

## Purpose
This non-Linux fallback exposes the `SupportsNativeOverlay` symbol for platforms where the overlay driver implementation is not built.

## Important APIs, Types, And Functions
`SupportsNativeOverlay(graphroot, rundir string) (bool, error)` always returns `false, nil`.

## Control Flow
There is no probing on unsupported platforms.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
The `!linux` build tag keeps callers portable when they compile shared code that asks whether native overlay is available.

## Risks And Test Signals
The behavior is intentionally conservative. Any caller requiring an explanatory error must not rely on this function for unsupported-platform diagnostics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_unsupported.go -->
