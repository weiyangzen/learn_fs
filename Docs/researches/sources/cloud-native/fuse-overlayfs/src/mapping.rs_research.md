<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/mapping.rs -->
# sources/cloud-native/fuse-overlayfs/src/mapping.rs

Purpose: UID/GID mapping and overflow ID utilities.

Important APIs: `IdMapping` represents a `host:to:len` range. `OverflowIds::read` reads kernel overflow UID/GID with fallback to `65534`. `parse_mappings` parses colon-separated triples and tolerates empty segments. `find_mapping` maps host-to-container for direct reads or container-to-host for writes, with direct-mode `squash_to_uid/gid` taking precedence over `squash_to_root`, and returns overflow ID for unmapped IDs when mappings are configured.

State and integration: reads `/proc/sys/kernel/overflowuid` and `overflowgid`; otherwise stateless. Used by config parsing and overlay ownership presentation/mutation. Risks include no overlap validation, empty segment filtering accepting unusual strings, and overflow behavior surprising callers when mappings are partial. Test signal covers parse success/failure, leading colon, direct/reverse mapping, squash-to-root, and squash-to-id precedence.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/mapping.rs -->
