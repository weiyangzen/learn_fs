# sources/cloud-native/composefs-rs/crates/composefs-storage/src/layer.rs

## Purpose
This module models containers-storage overlay layers. It opens layer directories, exposes diff content, reads short link IDs and lower parent links, resolves parent chains, and detects overlay whiteout and opaque-directory markers.

## Important APIs, Types, and Functions
`Layer` stores full layer ID, layer directory handle, diff directory handle, short link ID, and parent link IDs. Public methods include `open()`, `id()`, `link_id()`, `parent_links()`, `parents()`, `layer_dir()`, `diff_dir()`, `layer_chain()`, `open_file()`, `open_file_std()`, `metadata()`, `read_dir()`, `has_whiteout()`, and `is_opaque_dir()`. Internal helpers `read_link()` and `read_lower()` parse layer metadata files.

## Control Flow
`Layer::open()` opens `overlay/<id>`, `diff/`, reads `link`, and parses optional `lower`. `read_lower()` treats missing `lower` as a base layer and otherwise parses colon-separated `l/<link-id>` references. `parents()` maps parent link IDs through `Storage::resolve_link()`. `layer_chain()` walks from self through all parents breadth-first by appending opened parent layers until exhaustion or `MAX_DEPTH = 500`. File operations delegate to the `diff_dir` handle. `has_whiteout()` checks `.wh.<filename>` in root or a parent directory. `is_opaque_dir()` checks `.wh..wh..opq` in root or a target directory, returning false for missing directories.

## State and Persistence
The module reads persistent overlay storage state: `overlay/<layer-id>/diff`, `link`, `lower`, whiteout files, and opaque markers. It stores only open directory handles and parsed metadata in memory.

## Dependencies and Integration Points
It uses `cap_std::fs::Dir`, crate `Storage`, and `StorageError`. It is used by storage layer retrieval, tar-split reconstruction, chain traversal, and any direct layer file access logic.

## Risks
The layer chain traversal has a depth cap but no explicit visited set, so cycles below 500 entries will eventually hit the depth error rather than reporting a cycle. `read_lower()` silently ignores lower components without `l/`, which may hide malformed lower files. Whiteout checks are existence-based and do not validate marker file type. Path inputs are passed to `cap_std` APIs, so capability scoping helps, but callers still need to avoid semantic confusion from unusual relative paths.

## Test Signals
Tests cover lower-file parsing, mock layer opening, whiteout detection in root/subdirectories/nested directories/nonexistent parents/multiple files, opaque marker detection in root/subdirectories/normal dirs/nonexistent/nested paths, coexistence of whiteout and opaque markers, and the `.wh..wh.` edge case that is a whiteout for `.wh.` rather than an opaque marker.
