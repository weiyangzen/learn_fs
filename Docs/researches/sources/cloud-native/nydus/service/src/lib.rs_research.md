# sources/cloud-native/nydus/service/src/lib.rs

Purpose: crate root for `nydus-service`, documenting service modes and exporting the public daemon, filesystem, blob-cache, block-device, and UFFD APIs behind platform/feature gates.

Important APIs/types: exports `BlobCacheMgr`, `FsBackendCollection`, `FsBackendMountCmd`, `FsBackendUmountCmd`, `FsService`, `create_fuse_daemon`, `create_vfs_backend`, `FusedevDaemon`, `create_daemon`, and Linux `FsCacheHandler`. Defines central `Error`, `Result`, `FuseNotifyError`, `FsBackendType`, `FsBackendDescriptor`, `validate_threads_configuration`, and `ServiceArgs`.

Control flow: there is no runtime loop here; it normalizes error conversion into `io::Error` and `nydus_api::DaemonErrorKind`, parses backend type strings, validates thread counts in `[1,1024]`, and exposes modules conditionally based on target OS and block features.

State and persistence: only serializable descriptors/types live here. `FsBackendDescriptor` records backend type, mountpoint, mounted time, and optional sanitized `ConfigV2`; versionize annotations allow mount commands and backend type values to participate in upgrade snapshots.

Dependencies and integration: centralizes integration with `fuse-backend-rs`, RAFS, serde, versionize, and `nydus_api`. Non-Linux builds get a stub `BlobCacheMgr` with unimplemented mutation methods, keeping API shape available while Linux-only cache implementation is excluded.

Risks: broad error-to-`io::Error` conversion maps everything to invalid input; adding backend types requires updating parsing/display/version compatibility and tests. Conditional modules mean some exported APIs exist only under Linux or feature gates, which callers must handle.

Test signals: tests cover backend type parsing aliases/errors/display, thread-count boundaries, error conversion to `DaemonErrorKind`, `FuseNotifyError` display, and representative `Error` display messages.
