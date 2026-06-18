## sources/cloud-native/moby/daemon/internal/image/fs.go

Purpose: Implements a filesystem-backed `StoreBackend` for image configuration blobs and per-image metadata.

Important APIs/types: `DigestWalkFunc`, `StoreBackend`, and `fs`. Public constructor `NewFSStoreBackend` calls `newFSStore`. Methods are `Walk`, `Get`, `Set`, `Delete`, `SetMetadata`, `GetMetadata`, and `DeleteMetadata`. Constants define `content` and `metadata` subdirectories.

Control flow: Initialization creates `content/sha256` and `metadata/sha256`. `Set` rejects empty data, computes `digest.FromBytes`, and atomically writes content to `content/<algo>/<encoded>`. `Get` reads and verifies content digest. `Walk` enumerates canonical sha256 content entries, validates digest filenames, logs and skips invalid entries, and stops on callback error. Metadata methods require the content to exist before reading/writing sidecars under `metadata/<algo>/<encoded>/<key>`. `Delete` removes metadata then content.

State and persistence: Persistent state is disk files under the backend root. A RW mutex serializes backend operations in-process. Atomic writer reduces torn content/metadata writes.

Dependencies and integration: Used by `image.Store` as durable storage for image config JSON and metadata such as parent, lastUpdated, and builtLocally.

Risks: Only canonical sha256 is walked/created by initialization. Metadata keys are used as path components with no extra sanitization in this file. Digest verification catches content corruption but means every `Get` reads full content.

Test signals: `fs_test.go` covers invalid roots, get/set digest verification, empty set rejection, metadata, walking, deletion, and callback errors.
