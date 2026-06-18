# sources/cloud-native/containers-storage/drivers/chown.go

## Purpose
`chown.go` implements ID-map based ownership rewriting for layer trees. It registers a reexec helper that chroots/chdirs into a layer and walks it, translating UIDs/GIDs from an old mapping to a new one.

## Important APIs, Types, And Functions
`chownByMapsCmd` names the reexec command. `chownByMapsMain` decodes four ID-map slices from stdin, enters the target root, builds `IDMappings`, and parallel-walks the tree with a platform `LChown` implementation. `ChownPathByMaps` marshals mapping data and invokes the reexec command. `naiveLayerIDMapUpdater` implements `LayerIDMapUpdater` with `UpdateLayerIDMap` and `SupportsShifting`.

## Control Flow
Callers invoke `UpdateLayerIDMap`, which mounts/gets the layer, defers `Put`, and calls `ChownPathByMaps`. The child process reads JSON config, enters the layer root, skips `"."`, and calls platform-specific `LChown` on each entry. Errors propagate through combined process output.

## State And Persistence
The persistent effect is changed file ownership, restored mode bits, and restored security capability xattrs inside the target layer tree. No metadata sidecar is written.

## Dependencies And Integration Points
It depends on `idtools`, `reexec`, `pwalkdir`, package-local `json`, `chrootOrChdir`, and platform `newLChowner`. `NaiveDiffDriver` and drivers without native shifting use `NewNaiveLayerIDMapUpdater`.

## Risks
Running in a reexec/chroot path protects against path traversal but depends on platform chroot behavior. Mapping failures are tolerated only for zero IDs in the old map. Hardlink preservation is delegated to platform code. Combined output error wrapping can expose stderr text as part of errors.

## Test Signals
No direct test in this subset. Indirect coverage comes from drivers using naïve ID-map updating and any tests that exercise user namespace or mapping transitions.
