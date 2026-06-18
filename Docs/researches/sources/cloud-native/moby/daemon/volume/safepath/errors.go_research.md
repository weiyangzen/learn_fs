# sources/cloud-native/moby/daemon/volume/safepath/errors.go

## Purpose
Typed errors for safe subpath resolution failures.

## Important APIs, Types, And Functions
`ErrNotAccessible` records path and cause, implements `NotFound`, `Unwrap`, and `Error`. `ErrEscapesBase` records base/subpath and implements `InvalidParameter` plus `Error`.

## Control Flow
Platform join/open code returns these errors for missing/inaccessible paths, symlink replacement, and base escape attempts. Marker methods allow error classification by Moby errdefs.

## State And Persistence
No state beyond error values.

## Dependencies And Integration Points
Used by `safepath.Join` and mount setup for volume/image subpaths. Higher layers can map them to API not-found or invalid-parameter responses.

## Risks
Error classification is part of API behavior. Avoid leaking sensitive full paths if future call sites expose messages directly.

## Test Signals
Join tests assert `ErrEscapesBase` for escaping symlinks and indirectly exercise `ErrNotAccessible` in failure paths.
