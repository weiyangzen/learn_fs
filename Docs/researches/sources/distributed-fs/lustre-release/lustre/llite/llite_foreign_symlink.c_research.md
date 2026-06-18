<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign_symlink.c -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_foreign_symlink.c

## Purpose

`llite_foreign_symlink.c` implements the fake-symlink behavior declared in `foreign_symlink.h`. It turns foreign LOV/LMV metadata into a VFS symlink target by prefixing a mount-local absolute path and parsing the foreign free-form value either directly or through a userspace-provided format. It also exposes sysfs configuration for enabling the feature, setting the prefix, registering an upcall, and accepting the upcall's parse descriptors.

## Important APIs, Types, And Functions

- `foreign_symlink_alloc_and_copy_prefix()`: allocates a destination path buffer and writes `/<prefix>/`, returning the suffix insertion offset.
- `ll_foreign_symlink_default_parse()`: uses the whole foreign `lfm_value` as the relative suffix.
- `ll_foreign_symlink_upcall_parse()`: builds the suffix from configured `STRING_TYPE` constants and `POSLEN_TYPE` substrings of `lfm_value`.
- `ll_foreign_symlink_parse()`: selects default or upcall parse based on `LL_SBI_FOREIGN_SYMLINK_UPCALL`.
- `ll_foreign_readlink_internal()`: loads full foreign LOV/LMV metadata from regular-file CL layout or directory LMV cache and returns the parsed symlink target.
- `ll_foreign_get_link()` / `ll_foreign_put_link()`: VFS `.get_link` implementation and delayed cleanup.
- `ll_foreign_dir_lookup()`: rejects lookup inside fake directory symlinks with `-ENODATA`.
- `foreign_symlink_enable_show/store()`, `foreign_symlink_prefix_show/store()`, `foreign_symlink_upcall_show/store()`, `foreign_symlink_upcall_info_store()`: sysfs control surface.
- `ll_foreign_file_symlink_inode_operations` and `ll_foreign_dir_symlink_inode_operations`: operation tables installed by `llite_foreign.c`.
- `ll_foreign_symlink_getattr()`: calls `ll_getattr_dentry(..., foreign=true)` so fake symlinks stat as symlinks.

## Control Flow

For symlink traversal, VFS calls `ll_foreign_get_link()`. It rejects RCU-walk style calls with `-ECHILD`, then calls `ll_foreign_readlink_internal()`. Regular files fetch the layout size with `cl_object_layout_get()` using a zero-length buffer, allocate the returned size, and fetch the full LOV foreign metadata. Directories take a reference on cached `lli_lsm_obj` and treat its `lso_lfm` as a `lov_foreign_md` because the foreign LOV and LMV formats are intentionally compatible for this use.

Parsing then depends on mount configuration. Without an upcall descriptor, `ll_foreign_symlink_default_parse()` copies the foreign value after the configured prefix. With an installed descriptor array, `ll_foreign_symlink_upcall_parse()` first computes the output suffix size from all items, allocates the prefixed path, then appends either constant strings or substrings from the foreign value. Bounds checks ensure substring positions fit in `lfm_length`. The generated path is returned to VFS and freed through a delayed call.

Sysfs writes are mount-namespace gated by `has_same_mount_namespace()`. Enabling toggles `LL_SBI_FOREIGN_SYMLINK`. Prefix writes require an absolute path, allocate a replacement string, and swap it under `ll_foreign_symlink_sem`. Upcall writes accept an absolute executable or `"none"`, replace the upcall path, clear the upcall-active bit, and invoke the helper with the mount kobject name. The helper is expected to write binary parse info back to `foreign_symlink_upcall_info_store()`, which validates item alignment, count, string sizes, explicit end marker, allocates a new item array, swaps it under the semaphore, and frees the previous descriptor set.

## State And Persistence Behavior

All configuration state is per-mounted-client in `ll_sb_info`: feature bits, prefix path and size, upcall path, descriptor array, descriptor count, mount namespace, and `ll_foreign_symlink_sem`. The code allocates symlink target buffers per lookup and frees them with `OBD_FREE_LARGE`. Regular-file foreign metadata buffers are allocated per readlink and freed after parsing; directory metadata uses a referenced cached LMV object. No on-disk metadata is modified.

## Dependencies And Integration Points

The file depends on Linux VFS symlink/getattr/inode-operation APIs, sysfs kobject show/store conventions, usermode helper execution, Lustre allocation macros, CL layout retrieval, LMV stripe-object references, `ll_getattr_dentry()` from `file.c`, and foreign parsing structs/macros such as `ll_foreign_symlink_upcall_item`, `STRING_ITEM_SZ`, `POSLEN_ITEM_SZ`, `MAX_NB_UPCALL_ITEMS`, `STRING_TYPE`, `POSLEN_TYPE`, and `EOB_TYPE`.

It is installed by `llite_foreign.c` when foreign file/dir metadata identifies symlink type. The sysfs handlers are declared in `foreign_symlink.h` and are typically wired into the llite mount kobject elsewhere.

## Risks And Edge Cases

- `foreign_symlink_alloc_and_copy_prefix()` subtracts one from `ll_foreign_symlink_prefix_size`; configuration must ensure the prefix is initialized and NUL-terminated.
- Prefix and upcall store comments note that CR/LF/space stripping is not implemented. Sysfs writes with trailing newlines may become part of the path unless sanitized by callers.
- Default parsing trusts `lfm_length` and `lfm_value`; the code comments note missing double-checks of magic, length, and type after metadata load.
- Upcall path replacement and helper execution can race with descriptor installation; comments note a possible mismatch between the path and the format that eventually sets `LL_SBI_FOREIGN_SYMLINK_UPCALL`.
- `foreign_symlink_upcall_info_store()` parses binary data from userspace and allocates per-string memory. Error cleanup must free only initialized string items.
- The failure cleanup in `ll_foreign_symlink_upcall_parse()` frees `suffix_pos + items_size`, while allocation used `suffix_size + prefix_size + 3`; memory-debug correctness depends on allocator semantics and size matching expectations.
- Mount namespace checks protect sysfs writes, but reads are unrestricted.
- Fake directory symlink lookup returns `-ENODATA` for already cached directories when the feature was enabled after caching; callers must tolerate this transitional state.

## Test Signals

Tests should cover default parsing for file and directory foreign metadata, prefix length and `PATH_MAX` enforcement, missing CL object/LMV cache failures, encrypted or unusual path bytes in `lfm_value`, VFS `readlink`/`stat` mode exposure, RCU get-link `-ECHILD`, enabling/disabling from same and different mount namespaces, prefix updates while links are read, upcall path `"none"` and absolute path handling, successful helper invocation, valid descriptor arrays with string and substring items, malformed descriptor sizes/types/early EOB/too many items, substring out-of-bounds rejection, replacement/freeing of old descriptor arrays, and stale cached fake directory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign_symlink.c -->
