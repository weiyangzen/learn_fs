# sources/cloud-native/moby/daemon/internal/distribution/push_v2.go

## Purpose
Implements Registry v2 image push: layer upload/mount/existence checks, manifest creation, metadata updates, and refstore digest recording.

## APIs, Control Flow, and Integration
`newPusher` wires metadata, refs, endpoint, and config. `push` creates a push/pull-capable repository and records whether auth info exists. `pushRepository` pushes one tag or all tags. `pushTag` loads image config/rootfs, resolves top layer, computes auth HMAC key, creates reverse-order `pushDescriptor`s, uploads layers via upload manager, builds schema2 manifest, pushes it with tag, emits digest progress/aux, and records digest ref. `pushDescriptor.Upload` checks shared remote layer state, consults v2 metadata, attempts cross-repo mounts, performs existence checks by layer size policy, uploads/compresses as needed, and records HMAC-tagged metadata.

## State, Dependencies, and Risks
State spans remote registry blobs/manifests, Moby layer store, image store, refstore, upload manager, and v2 metadata. Risks include stale metadata removal heuristics, auth-sensitive mount candidate cleanup, dedupe map locking, upload cancellation, unsupported layer media types, and schema2-only manifest creation. Tests heavily cover mount candidate sorting, existence checks, metadata add/remove, and auth-info cleanup behavior.
