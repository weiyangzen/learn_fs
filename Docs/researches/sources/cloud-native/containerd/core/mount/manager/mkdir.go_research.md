<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir.go -->
# sources/cloud-native/containerd/core/mount/manager/mkdir.go

Purpose: built-in mount transformer that consumes `X-containerd.mkdir.path=...` options and creates directories under configured allowed roots before a mount is performed.

Important APIs/types/functions: `mkdir` holds `rootMap map[string]*os.Root`; `(*mkdir).Transform` implements `mount.Transformer`. Options follow `X-containerd.mkdir.path=value[:mode[:uid:gid]]`; default mode is `0700`, default ownership is the current process uid/gid.

Control flow: transform scans options, parses mkdir-specific options, selects an `os.Root` whose path prefixes the requested directory, converts to a root-relative subpath, stats the path, creates it when absent, and strips consumed mkdir options from the mount. Non-mkdir options are preserved.

State and persistence: persists only the created directory in the filesystem. The returned mount has internal options removed so kernel mount parsing will not see them.

Dependencies and integration points: used by `manager.go` for `mkdir/<type>` transform prefixes. It relies on `os.Root` path-scoped filesystem operations and `errdefs` for invalid argument/not implemented classification.

Risks: only one directory level is created because `os.Root.MkdirAll` is not yet used; chmod/chown are explicitly not implemented; root selection uses map iteration and simple prefix matching, which can be ambiguous for overlapping roots and string-prefix false positives. Mode parsing rejects non-permission bits.

Test signals: `mkdir_linux_test.go` verifies successful creation with explicit mode and current uid/gid, option stripping indirectly, and likely error classification for unsupported ownership/mode cases on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir.go -->
