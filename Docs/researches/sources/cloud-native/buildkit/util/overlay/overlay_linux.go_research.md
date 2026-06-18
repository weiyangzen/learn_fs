## sources/cloud-native/buildkit/util/overlay/overlay_linux.go

Purpose: Linux overlayfs-aware differ that derives layer changes directly from overlay upperdir and writes layer tar archives efficiently.

Important APIs/functions: `GetUpperdir`, `GetOverlayLayers`, `WriteUpperdir`, `Changes`, `checkDelete`, `checkOpaque`, `checkRedirect`, `sameDirent`, stat/xattr/content comparison helpers.

Control flow: `GetUpperdir` compares lower and upper mount layer lists to identify the single top upper layer. `GetOverlayLayers` parses `upperdir` and reversed `lowerdir` options while rejecting unknown options. `WriteUpperdir` mounts lower and an upperdir view over an empty lower, then uses archive `ChangeWriter` over `Changes`. `Changes` walks upperdir, rebases paths, rejects redirect_dir xattrs, interprets char device 0/0 as whiteout deletes, compares existing base entries as modifies while skipping unchanged parent dirs, detects adds, and for opaque directories delegates to continuity `fs.Changes` against the clean upper view.

State/persistence: reads overlay upperdir, xattrs, device nodes, and may create temp mount points; writes tar stream to provided writer. Uses a typed `sync.Pool` buffer for slow content comparison. Dependencies: containerd mount/archive/continuity fs/sysx/devices, unix, BuildKit pools.

Integration points: snapshot differ/export code can use overlay metadata instead of full walking differ. Risks: redirect_dir unsupported and errors; unknown overlay options cause fallback; requires privilege/mount support; slow content compare still needed for truncated timestamps; xattr access can fail by filesystem/capabilities. Test signals: `overlay_linux_test.go` ports many continuity differ cases for adds/modifies/deletes, renames, nested deletions, permissions, timestamps, symlinks.
