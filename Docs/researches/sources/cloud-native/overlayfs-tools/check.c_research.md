# sources/cloud-native/overlayfs-tools/check.c

Purpose: implements the main consistency scanner and repair engine for `fsck.overlay`, validating whiteouts, redirect directories, opaque state, and missing impure xattrs across upper and lower overlay layers.

Important APIs/types/functions: public `ovl_scan_fix`; internal lookup contexts/data, redirect list entries, `ovl_lookup_single`, `ovl_lookup_layer`, `ovl_lookup_lower`, `ovl_lookup`, `ovl_check_whiteout`, `ovl_check_redirect`, `ovl_check_impure`, `ovl_count_impurity`, and scan result aggregation helpers.

Control flow: scanning has two passes. Pass one checks redirect xattrs and directory-tree consistency, recording valid redirect origins to detect duplicates. Pass two checks whiteouts and counts origin/redirect/merge subdirectories so missing `trusted.overlay.impure` can be repaired. It scans lower layers from bottom to top, then upper, switching read-only lower layers to no-change mode.

State and persistence: may remove invalid whiteouts, remove redirect xattrs, create missing whiteouts, set opaque xattrs, and set impure xattrs. Global `status` records changed, abort, and unresolved inconsistency bits. A transient in-memory redirect list tracks duplicate origins.

Dependencies/integration: called by `fsck.c`; depends on `scan_dir` from `lib.c`, overlay xattr constants, path helpers, kernel-style list macros, and global user flags.

Risks: repair decisions are interactive unless auto/yes/no flags override. Redirect resolution is subtle and only supports xattr-capable layers. Incorrect repair can change overlay semantics, so mounted filesystems are blocked earlier.

Test signals: direct tests should create layered fixtures with orphan whiteouts, invalid redirect xattrs, duplicate redirects, missing impure xattrs, read-only lowers, and `-n`/`-y`/`-p` behavior.
