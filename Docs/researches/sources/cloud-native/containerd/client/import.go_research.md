# Research: sources/cloud-native/containerd/client/import.go

## Purpose
Implements `Client.Import`, which ingests an image tar stream into the content store and creates/updates image records from the imported OCI index or manifest set. It is the client-side archive import path and complements remote pull/export operations.

## Important APIs, Control Flow, And State
`ImportOpt` configures reference translation, digest references, index naming, platform filtering, compression, layer discard labels, missing blob tolerance, image labels, and referrer handling. `Client.Import` applies options, creates a temporary lease with `WithLease`, imports content with `archive.ImportIndex`, walks descriptors from the top-level index, derives image names through `imageName`, optionally creates digest-named images, filters by platform, sets children/referrer/GC labels, then updates or creates image service records. Persistent state is in the content store, image store, descriptor labels, and optional referrer metadata; the lease protects temporary imported content while records are established.

## Dependencies And Integration
Depends on `core/content`, `core/images`, `core/images/archive`, `errdefs`, OCI descriptors, and `platforms`. It integrates with GC label propagation, image reference annotations, digest references, platform-specific imports, and content referrer providers.

## Risks And Test Signals
Risks include incomplete archives with `WithSkipMissing`, incorrect reference translation, skipped referrer images, platform filters dropping desired manifests, and shared image label maps being assigned to all output images. Tests should cover multi-platform indexes, referrer descriptors, digest reference callbacks, missing blobs, layer-discard labels, update-vs-create behavior, and lease cleanup on error.
