## sources/cloud-native/moby/daemon/internal/image/store.go

Purpose: Provides the daemon image store over a `StoreBackend` and layer reference manager. It creates, restores, searches, deletes, and tracks parent/child image relationships.

Important APIs/types: `Store` is the public interface. `LayerGetReleaser` abstracts layer retention. Internal `imageMeta` stores the retained top layer and child set. `store` keeps maps, a digest prefix set, backend, and layer store.

Control flow: `NewImageStore` calls `restore`. Restore walks backend digests, loads each image, checks OS, retains the rootfs chain layer when present, adds it to the digestset and image map, then does a second pass to reconstruct children from parent metadata. `Create` parses config JSON, rejects impossible history/rootfs layer counts, writes config through `fs.Set`, checks duplicates, validates OS, retains the rootfs layer, inserts metadata, and adds the digest to the lookup set. `Search` resolves partial IDs with `digestset`. `Get` reads config, parses it, sets computed ID, and hydrates parent metadata when present. `Delete` removes child parent metadata, unlinks from parent, removes digestset and backend content, and releases retained layer. Metadata helpers persist parent, lastUpdated, and builtLocally values. `Children`, `Heads`, `Map`, and `Len` expose in-memory views.

State and persistence: Durable state is image JSON plus metadata keys in `StoreBackend`. In-memory state is protected by an RW mutex and includes retained layer references. Layer persistence and reference counts live in `layer.Store`.

Dependencies and integration: Integrates with digestset, daemon image model, layer store, errdefs, logging, and filesystem backend.

Risks: `Create` writes config before validating layer existence, so failed layer retention can leave untracked backend content. `Delete` ignores backend delete errors. Children metadata is removed when parent is deleted, flattening child relationships. `imagesMap` calls `Get` while holding an RLock, so backend latency occurs under lock.

Test signals: `store_test.go` covers create validation, restore, search, add/delete, parent reset, lastUpdated, and length/map behavior.
