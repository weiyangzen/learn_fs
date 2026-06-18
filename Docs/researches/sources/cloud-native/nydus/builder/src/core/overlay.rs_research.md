# sources/cloud-native/nydus/builder/src/core/overlay.rs

## Purpose
`overlay.rs` centralizes whiteout and overlay-state semantics for merging multiple RAFS filesystem trees. It supports OCI image whiteouts, Linux overlayfs whiteouts, and a mode that disables whiteout handling. The module is intentionally small but critical: `Tree::merge_overaly()` relies on these classifications to decide which lower-layer nodes are removed, replaced, retained, or marked opaque.

## Important APIs, types, and functions
The public constants are `OCISPEC_WHITEOUT_PREFIX` (`.wh.`), `OCISPEC_WHITEOUT_OPAQUE` (`.wh..wh..opq`), and `OVERLAYFS_WHITEOUT_OPAQUE` (`trusted.overlay.opaque`). `WhiteoutSpec` is a parseable/displayable enum with `Oci`, `Overlayfs`, and `None`. `WhiteoutType` distinguishes OCI opaque/removal and overlayfs opaque/removal; `is_removal()` groups the removal variants. `Overlay` marks a node as `Lower`, `UpperAddition`, or `UpperModification` and exposes `is_lower_layer()`.

The module implements methods on `Node`: `is_overlayfs_whiteout()` detects character-device 0/0 whiteouts under overlayfs mode, `is_overlayfs_opaque()` detects directory xattr `trusted.overlay.opaque=y`, `whiteout_type()` combines spec and node state into a whiteout classification while ignoring lower-layer nodes, and `origin_name()` maps whiteout nodes back to the original lower-layer name to remove.

## Control flow, state, and persistence
`whiteout_type()` returns `None` for lower-layer nodes and when `WhiteoutSpec::None` is active. Under OCI mode it inspects the node name for `.wh..wh..opq` or `.wh.` prefix. Under overlayfs mode it checks device number and opaque xattr. `origin_name()` strips `.wh.` for OCI removals and returns the node name for overlayfs device whiteouts.

The module does not persist state directly; its output controls tree mutation in `tree.rs`. Overlayfs opaque handling also affects persistence indirectly because `Tree::merge_children()` removes the `trusted.overlay.opaque` xattr after applying opacity so the marker does not leak into the merged image.

## Dependencies and integration points
It depends on `Node`, unix `OsStrExt`, and `nydus_utils::compact::{major_dev, minor_dev}` through fully-qualified calls. `DirectoryBuilder` uses `Node::whiteout_type()` to skip upper-layer whiteout markers in single-layer builds. `Tree::merge_children()` uses all four `WhiteoutType` values. CLI/config parsing can use `WhiteoutSpec::from_str()`.

## Risks and test signals
OCI whiteouts require UTF-8 names because `whiteout_type()` uses `to_str()`; non-UTF-8 `.wh.` byte sequences would not be treated as whiteouts. Overlayfs whiteout detection depends on the source inode being a character device and `NodeInfo.rdev` being accurate. Tests cover `WhiteoutSpec` parsing/display, `WhiteoutType::is_removal()`, and overlay lower-layer checks; tree/merge integration provides the strongest behavior coverage.
