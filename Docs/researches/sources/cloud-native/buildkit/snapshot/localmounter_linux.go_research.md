## sources/cloud-native/buildkit/snapshot/localmounter_linux.go

Purpose: Linux implementation of local mount/unmount with rootless mount option adjustment and file-bind support.

Important APIs/types/functions: `Mount` lazily obtains mounts, applies `rootlessmountopts.FixUp` in user namespaces, returns writable bind/rbind source unless forced, detects single bind source files, creates temp dirs/files, and calls `mount.All`. `Unmount` uses `syscall.MNT_DETACH`, removes target, and calls release.

Control flow: mutex protects state. For a single bind/rbind, non-read-only mounts avoid remounting unless `forceRemount`; read-only/file binds are mounted into a temp target. File bind creates an empty placeholder file under the temp dir before mounting.

State and persistence: temp mount target, possibly a placeholder file, mountable release callback. State is cleaned on unmount.

Dependencies and integration points: used heavily by diff apply, snapshot tests, and BuildKit filesystem access. Integrates rootless user namespace handling.

Risks and test signals: if placeholder file creation fails, the code calls `os.RemoveAll(dest)` after `dest` has been changed to `<tmp>/file`, leaving the temp directory behind. Rootless option rewriting mutates `lm.mounts`. Linux snapshot tests exercise this path indirectly.
