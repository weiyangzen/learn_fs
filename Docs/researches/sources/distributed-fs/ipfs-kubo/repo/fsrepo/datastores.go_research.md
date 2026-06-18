# sources/distributed-fs/ipfs-kubo/repo/fsrepo/datastores.go

Purpose: translates repo datastore spec maps into concrete datastore instances and stable on-disk identity specs.

Important APIs and control flow: `DatastoreConfig` exposes `DiskSpec` and `Create`. `AnyDatastoreConfig` dispatches by `"type"` using the package registry initialized with `mount`, `mem`, `log`, and `measure`; plugins can extend it through `AddDatastoreConfigHandler`. `MountDatastoreConfig` recursively parses child specs, sorts mountpoints descending for deterministic longest-prefix behavior, and creates a `mount.Datastore`. `log` and `measure` wrap children while returning the child disk spec.

State and persistence: `DiskSpec` JSON is stored as `datastore_spec` at repo init and compared on open to prevent using an incompatible datastore layout. Memory datastore has nil disk spec and no persistence.

Dependencies and integration: integrates with `repo.Datastore`, go-datastore mount/sync/log, go-ds-measure, and plugin-provided datastore handlers such as flatfs and levelds.

Risks and test signals: malformed specs can panic if `mountpoint` exists but is not a string. Handler registry is package-global and not synchronized after init. Tests verify disk spec canonicalization and concrete datastore construction.
