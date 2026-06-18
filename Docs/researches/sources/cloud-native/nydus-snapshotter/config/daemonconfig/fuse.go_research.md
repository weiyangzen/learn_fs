# sources/cloud-native/nydus-snapshotter/config/daemonconfig/fuse.go

Purpose: FUSE/vhost-user nydusd configuration model.

Flow: `LoadFuseConfig` reads JSON and requires `Device`. `Supplement` fills backend host/repo, sets device ID to `/<snapshotID>` when present, and sets blobcache work dir from params. `FillAuth` sets registry token or base64 auth. `StorageBackend`, `DumpString`, and `DumpFile` implement the common interface.

State/dependencies: reads/writes JSON config files. Depends on auth and common dump helpers.

Integration points: default `fusedev` path used by packaged configs, systemd unit, and integration tests.

Risks/tests: `params[CacheDir]` is assigned without presence check, so missing params clear work_dir. Tests cover JSON shape and amplify_io but not supplement behavior.
