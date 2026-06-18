# sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/export.go

## Purpose
Implements the Moby image-store exporter for BuildKit results. It converts BuildKit refs into Moby image layers/configs, tags images, writes a temporary OCI descriptor reference, and returns BuildKit exporter metadata.

## APIs, Control Flow, and Integration
Key interfaces are `Differ` for turning snapshot refs into Moby layer diffIDs and `ImageTagger` for tag updates. `Opt` wires image store, differ, content store, lease manager, tagger, and callbacks. `Resolve` parses `name` exporter attributes into normalized references and stores all other attrs as metadata. `Export` rejects multiple refs, resolves the single ref/config, finalizes/extracts the ref, calls `EnsureLayer`, normalizes history, patches image config, creates the Moby image, tags target names, writes response keys, and creates a descriptor reference via `newTempReference`.

## State, Dependencies, and Risks
Persistence touches Moby image store, ref/tag store through callbacks, containerd content store, and temporary leases. Risks include only single-platform/single-ref support, nil-ref scratch handling, stale temporary leases if write/unlease fails, and history/rootfs mismatch bugs. Test coverage is mostly helper-level (`writer_test.go`), so full exporter behavior relies on integration tests.
