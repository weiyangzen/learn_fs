# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.cpp

Purpose: shared stress-test engine for generating tar layers, maintaining an expected in-memory overlay tree, building stacked EROFS images, and verifying mounted EROFS output against the model.

Important APIs/types/functions: `get_randomstr`, `is_substring`, and `str_n_equal` support randomized generation and path checks. `StressFsTree::add_node`, `get_same_name`, and `get_type` encode overlay semantics for replacement and whiteout deletion. `build_layer_tree` creates a random directory hierarchy from per-directory file counts. `append_tar` shells out to GNU tar and tar concatenation. `StressBase::create_layer`, `mkfs`, `verify`, and `run` drive the full lifecycle.

Control flow: `run` rejects pre-existing workdirs, adds root to the expected tree, calls `create_layer` for each layer, builds stacked image state in `mkfs`, mounts it, and calls `verify`. `create_layer` creates a randomized host tree beneath a random prefix, calls virtual generator hooks for metadata/content, appends each object to a tar, and updates `StressFsTree`; `.wh.` names are modeled as deletion operations. `mkfs` wraps each tar in an LSMT virtual device, stacks upper layers on lower layers, and invokes `LibErofs::extract_tar`. `verify` breadth-first traverses the EROFS filesystem, reconstructs `StressNode` values via virtual hooks, and removes matching nodes from the expected tree.

State and persistence: state is split between host workdirs, layer tar files, LSMT `.idx`/`.meta` files, stacked image mappings, and in-memory `StressFsTree`. `append_tar` persists each generated object immediately into a layer tar. On success `run` removes the workdir; on error it leaves the tree and generated tars in place.

Dependencies/integration: uses Photon local filesystem, Photon directory iteration, Photon xattr-capable files supplied by case classes, `LibErofs`, `create_erofs_fs`, LSMT warp and stack APIs, and external GNU tar commands with `--xattrs --xattrs-include='*'`.

Risks: command strings are built by concatenation without shell escaping, but generated names are alphanumeric and prefixes are fixed by tests. `StressFsTree::add_node` erases map entries without deleting the old `StressNode`, so long stress runs can leak memory. Verification uses directory iteration order but tree comparison itself is path keyed. The random layer tree builder deletes `LayerNode` objects during traversal, but nested ownership is manual and fragile.

Test signals: this file is exercised indirectly by all nine stress cases and is the core signal for overlay replacement, directory/file type conflicts, whiteout deletion, xattr preservation, metadata preservation, and content hash correctness.
