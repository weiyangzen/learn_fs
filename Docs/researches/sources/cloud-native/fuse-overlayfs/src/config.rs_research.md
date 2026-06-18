<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/config.rs -->
# sources/cloud-native/fuse-overlayfs/src/config.rs

Purpose: command-line and `-o` option parser for the Rust fuse-overlayfs implementation.

Important APIs and flow: `OverlayConfig` stores paths, UID/GID mapping strings and parsed mappings, timeouts, xattr/NFS modes, squash options, booleans, FUSE pass-through options, and effective UID. `parse_args` injects default FUSE options based on root/non-root, handles `-f`, `-d`, help/version, `-o` separated and concatenated forms, records mountpoint, parses mappings, and makes `volatile` disable fsync. `split_options`, `unescape_path`, `parse_single_option`, `parse_lowerdir`, and `parse_plugin_path` handle comma/colon escaping, plugin lowerdir syntax, and known C-compatible options.

State and persistence: builds in-memory config only. Integration points are `main.rs`, `mapping.rs`, and `layer.rs`. Risks include unknown arguments being warnings rather than hard failures, partial plugin support, quoting/escape edge cases, and C compatibility expectations for option behavior. Test signal covers lowerdir parsing, plugin path parsing, option splitting, basic parse, xino, volatile, and multiple `-o`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/config.rs -->
