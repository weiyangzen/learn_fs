# sources/cloud-native/nydus/service/src/fs_service.rs

Purpose: provides the common filesystem-service trait and backend factory used by FUSE daemons to mount RAFS, passthroughfs, and optional overlayfs layers into a `fuse_backend_rs::api::Vfs`.

Important APIs/types: `FsBackendMountCmd`, `FsBackendUmountCmd`, `FsBackendCollection`, `FsService`, `mountpoint_invalidation_target`, `validate_prefetch_file_list`, and `fs_backend_factory`. `FsBackendCollection::add` records sanitized RAFS config, mountpoint, backend type, and mounted time for API status/metrics.

Control flow: `mount` rejects duplicate mountpoints, creates a backend, mounts it into VFS, records backend metadata, and updates upgrade state/VFS bytes. `remount` finds an existing RAFS backend, opens the new bootstrap, parses config, calls `Rafs::update`, and refreshes metrics/upgrade mount state. `restore_mount` recreates a backend at a saved VFS index. `umount` optionally sends FUSE invalidation for RAFS trees, unmounts from VFS, deletes collection state, saves upgrade VFS state, and runs blob factory GC.

State and persistence: mount state lives in VFS, `FsBackendCollection`, and `UpgradeManager` mount/VFS snapshots. RAFS bootstrap/config sources are not persisted here beyond `FsBackendMountCmd`; upgrade replay reuses those commands.

Dependencies and integration: uses `fuse-backend-rs` VFS, RAFS import/update APIs, `nydus_api::ConfigV2`, `BLOB_FACTORY`, Linux `PassthroughFs` and `OverlayFs`, and versionize for mount-command compatibility. `FusedevFsService` implements this trait and API handlers call its default methods.

Risks: mount/remount/umount are documented as not thread-safe and rely on single-threaded FSM/API usage; invalidation target resolution must handle root and nested pseudo-fs paths; overlayfs requires valid upper/work dirs and is Linux-only; prefetch paths must be absolute; remount assumes existing backend is RAFS.

Test signals: unit tests cover backend collection add/delete, prefetch path validation, root/nested/missing invalidation target resolution, passthrough descriptor behavior, and RAFS backend creation from a fixture bootstrap.
