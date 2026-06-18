## sources/cloud-native/buildkit/util/overlay/overlay_linux_test.go

Purpose: validates overlayfs-optimized change detection against continuity-style filesystem diff cases.

Important tests: simple file/dir add-modify-delete, rename fallback, empty unchanged file, nested deletion collapse, directory replace, remove directory trees, file replaced by directory, parent directory permissions, timestamp/content comparison edge cases, and symlink lchtimes. Helper functions mount overlay with temp lower/upper/work dirs, apply fstest layers, collect `Changes`, and compare path/kind/source metadata.

State/control flow: requires Linux overlay mount support; uses temp dirs and actual overlayfs behavior including whiteouts and xattrs.

Risks covered: wrong whiteout handling, unchanged parent dirs being emitted, timestamp truncation decisions, and recursive opaque-like directory behavior. Gaps: explicit redirect_dir error path, `GetUpperdir`, `WriteUpperdir`, and xattr capability comparison are not directly isolated.
