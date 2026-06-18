# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_linux.go

Purpose: implements overlayfs-specific change detection, adapted from BuildKit/containerd continuity.

Important APIs and flow: `GetUpperdir` compares lower and upper mount descriptions to identify the top diff directory. `GetOverlayLayers` parses `lowerdir`, `upperdir`, and known overlay options, returning bottom-to-top layers. `cancellableWriter` stops writes when context is canceled. `Changes` walks the upperdir, rebases paths, filters `withoutPaths`, detects unsupported redirect directories and appends them for separate mount commits, classifies whiteout deletes, modifies, and adds by comparing against the base, skips unchanged directory entries with `sameDirent`, handles opaque directories through a nested continuity diff, and finally emits delete records for `withPaths` so those lower files are replaced by separately committed mount blobs. Helper functions detect whiteouts, opaque xattrs, redirect xattrs, compare stat/capability/symlink/content, and use pooled buffers for file comparison.

State and persistence: reads overlay upper/base/view trees and xattrs; no direct writes except via supplied change callback.

Dependencies and integration: central to committer correctness. Integrates selected mount path handling with `MountList.Add`, `archive.ChangeWriter`, and snapshotter-converter pack.

Risks and test signals: redirect_dir is not supported and is surfaced as append-mount work rather than diffed. Xattr access may require privileges. Unknown overlay options intentionally fail. Path filtering is prefix-based and should use normalized absolute paths to avoid surprises.
