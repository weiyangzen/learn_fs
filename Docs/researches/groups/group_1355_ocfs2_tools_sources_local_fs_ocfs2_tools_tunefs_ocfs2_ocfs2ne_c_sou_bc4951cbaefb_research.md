# Group Research: group_1355_ocfs2_tools_sources_local_fs_ocfs2_tools_tunefs_ocfs2_ocfs2ne_c_sou_bc4951cbaefb

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/ocfs2-tools` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/ocfs2ne.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/ocfs2ne.c

## Role

`tunefs.ocfs2` front controller. This file owns command-line parsing, option-to-operation dispatch, operation ordering, progress setup, filesystem open/reopen policy, and the main program entrypoint.

## Main Structures

- `struct tunefs_option`: wraps `getopt_long()` metadata, help text, operation pointer, parse handler, seen flag, and private option state.
- `struct tunefs_journal_option`: maps `-J` journal sub-options such as `size`, `block64`, and `block32` to tunefs operations.
- `struct tunefs_run`: linked-list entry for queued operations.
- Global `tunefs_run_list`: ordered list of operations to execute.
- Global `tunefs_op_count` and `tunefs_op_progress`: top-level progress accounting.

## Operation Registration

External operations declared here include sparse listing, query, UUID reset, feature toggles, resize, journal size/block mode changes, label changes, slot count changes, cluster stack update, cloned volume handling, and quota sync interval changes.

The option table maps user-visible flags to those operations:

- `-Q/--query` -> `query_op`
- `--list-sparse` -> `list_sparse_op`
- `-U/--uuid-reset[=uuid]` -> `reset_uuid_op`
- `--update-cluster-stack` -> `update_cluster_stack_op`
- `--cloned-volume[=label]` -> `cloned_volume_op`
- `-N/--node-slots` -> `set_slot_count_op`
- `-L/--label` -> `set_label_op`
- `--fs-features` plus derived feature aliases -> `features_op`
- `-S/--volume-size` -> `resize_volume_op`
- `-J/--journal-options` -> journal operation table
- `--usrquota-sync-interval` / `--grpquota-sync-interval` -> quota interval ops

## Parsing Flow

`build_options()` dynamically builds both short and long getopt tables from the `options[]` array. Long-only options initially use `CHAR_MAX`; the builder assigns unique unprintable values above `CHAR_MAX`.

`parse_options()` loops through `getopt_long()`, rejects duplicate options except verbosity handlers that explicitly clear `opt_set`, calls any `opt_handle`, and appends `opt_op` to the run list. It then folds feature-oriented options into one feature string via `parse_feature_strings()`, validates the device argument, and invokes `parse_resize()` for historical resize syntax where the new size may be a trailing positional argument.

## Special Cases

Feature parsing is delayed until after all options are processed. `-M local`, `-M cluster`, `--backup-super`, and `--fs-features` all contribute strings to one final `features_op`.

Resize is prepended, not appended. `parse_resize()` queues `resize_volume_op` at the head so filesystem growth happens before later operations that may need newly available space.

Journal sub-options are parsed as comma-separated `name[=value]` tokens. Unknown options cause the valid journal sub-option list to be printed.

## Execution Flow

`run_operations()` repeatedly computes combined open flags from pending operations, opens the filesystem with `tunefs_open()`, and then decides which subset can run:

- `TUNEFS_ET_CLUSTER_SKIPPED`: run only `TUNEFS_FLAG_SKIPCLUSTER` operations, mainly cloned volume handling.
- `TUNEFS_ET_INVALID_STACK_NAME`: run only `TUNEFS_FLAG_NOCLUSTER` operations, mainly cluster stack update.
- `TUNEFS_ET_PERFORM_ONLINE`: run online-capable operations before failing offline-only operations.
- Normal open: run remaining operations in queued order.

After each pass it closes and, if needed, reopens the filesystem so metadata changes such as UUID or cluster-stack updates are reflected before continuing.

## Safety Model

The file itself does not perform metadata writes; it sequences operations and delegates write safety to `tunefs_open()`, `tunefs_op_run()`, and each operation implementation. It does preserve important ordering constraints: cloned volume and cluster-stack repair can unblock later normal opens, online-capable operations can still run on mounted filesystems, and resize happens before space-consuming changes.

## Dependencies

Uses `libocfs2ne.h` for tunefs abstractions, progress, verbosity, interaction, open/close, operation execution, and error codes. Uses `ocfs2/ocfs2.h` and list helpers from the OCFS2 userspace library.

## Notable Risks

- Duplicate operation instances can be queued through different options if the option layer allows it, although duplicate exact options are rejected.
- `parse_feature_strings()` returns `errcode_t` but locally uses integer-style `rc`; functionally this works for success/failure but blurs error-code fidelity.
- `handle_journal_arg()` appends operations as it parses. If later journal tokens fail, already-appended operations remain on the run list before `print_usage()` exits the process, so this is not observable in normal execution but matters for reuse.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/ocfs2ne.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_cloned_volume.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_cloned_volume.c

## Role

Implements `--cloned-volume[=new-label]`, a dangerous recovery/administration operation that changes a cloned OCFS2 volume's UUID and optionally its label without normal cluster coordination.

## Behavior

`cloned_volume()` prompts with `tools_interact_critical()`, generates a new UUID, updates the label, writes the superblock, and reports progress across three steps.

If `new_label` is provided, `update_volume_label()` truncates it to `OCFS2_MAX_VOL_LABEL_LEN` and skips writing when it already matches. If no label is provided, it appends `-cloned` to the current label, truncating the original label if necessary.

`update_volume_uuid()` uses `uuid_generate()` and copies the raw UUID bytes into `s_uuid`.

The operation is defined with `TUNEFS_FLAG_RW | TUNEFS_FLAG_SKIPCLUSTER`, so the main driver can run it when cluster access is intentionally skipped for a cloned volume.

## Metadata Touched

- `OCFS2_RAW_SB(fs->fs_super)->s_uuid`
- `OCFS2_RAW_SB(fs->fs_super)->s_label`
- Superblock write via `ocfs2_write_super()`

## Safety Model

The file explicitly warns that it bypasses cluster software and requires the operator to guarantee no other node is using the filesystem. Writes are wrapped in `tunefs_block_signals()` / `tunefs_unblock_signals()` around the superblock write.

## Notable Risks

- In the no-label path, the suffix check uses `label_buf + len - CLONED_LABEL_LEN`. If the existing label length is shorter than `CLONED_LABEL_LEN`, this forms a pointer before the buffer. That is a real bounds risk.
- Label comparison for provided labels uses the truncated length and may treat a long supplied label as already matching if the stored prefix matches.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_cloned_volume.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_features.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_features.c

## Role

Implements `--fs-features` and feature-derived options by parsing requested OCFS2 feature enables/disables, checking they are supported by this tunefs binary, and invoking feature-specific implementations.

## Feature Table

The supported tunefs feature list includes:

- backup superblocks
- extended slot map
- inline data
- local mount mode
- metaecc
- sparse files
- unwritten extents
- xattrs
- user quota
- group quota
- refcount
- indexed directories
- discontiguous block groups
- clusterinfo
- append direct I/O

Each entry is an external `struct tunefs_feature` with name, feature bitset, enable/disable handlers, action, and open flags.

## Parse Flow

`features_parse_option()` allocates `struct feature_op_state`, parses the feature string with `ocfs2_parse_feature()`, then iterates enable and disable sets.

`check_supported_func()` verifies each requested feature exists in the local table and supports the requested direction. It sets `feat->tf_action` and ORs the feature's required open flags into the parent operation.

## Run Flow

`features_run()` runs disables first via `ocfs2_feature_reverse_foreach()`, then enables via `ocfs2_feature_foreach()`. Each callback resolves the feature and calls `tunefs_feature_run()`.

The operation is declared with initial open flags `0`; required flags are accumulated dynamically during parse based on the selected features.

## Metadata Touched

This file does not directly modify filesystem metadata. Actual mutations are delegated to each `tunefs_feature` implementation.

## Notable Risks

- `struct run_features_context` has `rc_error`, but `run_feature_func()` never assigns it, and `features_run()` ignores the return values of the foreach calls. Unless the iterator itself has non-obvious side effects, callback errors may not be propagated correctly.
- Feature actions are stored in global feature descriptors. That is simple for a one-shot CLI, but it makes the design stateful and awkward for library-style reuse.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_features.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_list_sparse_files.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_list_sparse_files.c

## Role

Implements `--list-sparse`, a reporting operation that recursively scans regular files and reports files containing sparse holes. It also summarizes total hole clusters and free clusters.

## Data Structures

- `struct multi_link_file`: red-black-tree node keyed by inode block number, used to avoid double-counting hard-linked files.
- `struct list_ctxt`: traversal state including current path, inode, accumulated hole length, duplicate flag, callback pointer, and hard-link tree.

## Scan Flow

`list_sparse()` scans from the root directory, then scans each per-slot orphan directory. For each directory entry, `list_sparse_func()` reads the inode and recurses into directories or calls `list_sparse_file()` for regular files.

`iterate_file()` uses `ocfs2_get_clusters()` over the file's virtual cluster range. When `p_cluster` is zero, it treats the range as a hole and invokes the supplied callback. It also supports callbacks for unwritten extents and extents beyond `i_size`, though this operation only uses the hole callback.

`list_sparse_file()` skips inline-data files, uses the hard-link tree for files with `i_links_count > 1`, and prints inode number, hole cluster count, and path when holes are present.

`get_total_free_clusters()` reads the global bitmap inode and computes `i_total - i_used`.

## Output

The operation prints tabular lines:

- inode block number
- cluster count for holes
- filepath

It also prints per-root/per-orphan-dir totals, total hole clusters in the volume, and total free clusters from the global bitmap.

## Open Flags

Declared as `TUNEFS_FLAG_RW`, even though the implementation is read/report oriented. This may be because directory iteration or library open semantics require stronger locking.

## Notable Risks

- `list_sparse_func()` allocates `di_buf`, then returns immediately for non-directory/non-regular files without freeing it. That is a memory leak during traversal.
- The path buffer is `OCFS2_MAX_FILENAME_LEN`, but the length guard compares against `PATH_MAX`. If `PATH_MAX` is larger, path construction can overflow the smaller buffer.
- Recursion is depth-first through directories with a fixed path buffer; extremely deep trees are not robustly handled.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_list_sparse_files.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_query.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_query.c

## Role

Implements `-Q/--query <query-format>`, a read-only formatted metadata query facility for `tunefs.ocfs2`.

## Format Specifiers

The operation registers custom GNU printf handlers:

- `%B`: block size
- `%T`: cluster size
- `%N`: number of node slots
- `%R`: root directory block
- `%Y`: system directory block
- `%P`: first cluster group block
- `%V`: volume label
- `%U`: UUID string
- `%M`: compat feature flags
- `%H`: incompat feature flags plus tunefs in-progress flags
- `%O`: read-only compatible feature flags

It rejects standard printf specifiers during parse via `parse_printf_format()` so only custom query specifiers are allowed.

## Run Flow

`query_parse_option()` stores the format string in `op->to_private`.

`process_escapes()` converts C-style escapes such as `\n`, `\t`, `\r`, and `\a`.

`query_run()` registers custom printf handlers, sets global `query_fs`, prints the processed format string to stdout, then clears the global and frees the processed string.

## Dependencies

Uses GNU extensions: `_GNU_SOURCE`, `asprintf()`, `register_printf_function()`, and `parse_printf_format()`.

## Safety Model

This is declared `TUNEFS_FLAG_RO` and does not modify metadata.

## Notable Risks

- Uses a global `query_fs` to pass filesystem context into printf handlers. That is fine for a CLI but not thread-safe or reentrant.
- `fprintf(stdout, fmt)` intentionally treats user input as a format string after custom validation. The validation is important; any missed standard specifier could become a format-string issue.
- `register_printf_function()` is a GNU libc extension and deprecated in newer glibc contexts, limiting portability.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_query.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_reset_uuid.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_reset_uuid.c

## Role

Implements `-U/--uuid-reset[=new-uuid]`, resetting the OCFS2 volume UUID either to a generated UUID or to a user-supplied UUID.

## Accepted UUID Forms

The parser accepts:

- 32 hex digits without dashes
- 36-character conventional UUID form with dashes

`translate_uuid()` converts the 32-character form to the dashed 36-character form before `uuid_parse()`.

## Run Flow

`reset_uuid_parse_option()` validates any supplied UUID and stores the original argument pointer in `op->to_private`.

`update_volume_uuid()` prompts the user. If a custom UUID was supplied, it adds a critical warning about duplicate UUID danger. It then starts progress, generates or parses the UUID, copies it into `s_uuid`, and writes the superblock under signal blocking.

## Metadata Touched

- `OCFS2_RAW_SB(fs->fs_super)->s_uuid`
- Superblock write via `ocfs2_write_super()`

## Open Flags

Declared as `TUNEFS_FLAG_RW`.

## Notable Risks

- If `uuid_parse()` failed inside `update_volume_uuid()` after progress start, progress cleanup would be skipped. Normal CLI parse validation should prevent this path for supplied UUIDs.
- The operation stores `arg` directly rather than copying it; safe for argv lifetime in this CLI, but not reusable as an independent library API.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_reset_uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_resize_volume.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_resize_volume.c

## Role

Implements `-S/--volume-size` and trailing resize size handling. It grows an OCFS2 filesystem online via kernel ioctls or offline by directly updating allocation metadata. Shrinking is explicitly unsupported.

## Size Parsing

`resize_volume_parse_option()` accepts an optional unit prefix stored by `ocfs2ne.c`:

- `bytes:`
- `blocks:`
- `clusters:`

If no size is supplied, `rs_size` remains zero and later means grow to device capacity.

`resize_volume_run()` converts the stored unit into bytes using superblock block/cluster size bits, handles wrap by saturating to `UINT64_MAX`, then calls `update_volume_size()`.

## Validation

`check_new_size()` enforces:

- requested size cannot exceed `UINT32_MAX` clusters
- requested clusters must fit the device
- requested clusters cannot be less than current filesystem clusters
- if journal block64 is not enabled, target block count must not exceed `UINT32_MAX`

If size is zero, it derives target clusters from current device size.

## Offline Growth

`update_volume_size_offline()` sets `OCFS2_FEATURE_INCOMPAT_RESIZE_INPROG`, calls `run_resize()`, clears the in-progress flag, and writes the superblock.

`run_resize()` reads the global bitmap inode, extends the tail group if possible, creates new group descriptors, updates chain records, updates bitmap totals, grows `i_clusters` / `i_size`, and updates filesystem cluster/block counts.

`init_new_gd()` initializes new cluster groups, zeroes the first cluster in each group, reserves backup superblock clusters when needed, links groups into chain records, and writes descriptors.

## Online Growth

`update_volume_size_online()` takes a DLM lock named `tunefs-online-resize-lock`, calls `run_resize(..., online=1)`, then unlocks.

For online changes:

- tail extension uses `OCFS2_IOC_GROUP_EXTEND`
- new groups use `OCFS2_IOC_GROUP_ADD`
- group descriptors are prepared by userspace but linked by kernel ioctls

## Backup Superblock Handling

`reserve_backup_in_group()` checks whether backup-super support is enabled and reserves clusters corresponding to backup superblock offsets inside newly added groups.

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION | TUNEFS_FLAG_ONLINE`.

## Notable Risks

- This is high-blast-radius metadata code: it modifies global bitmap, chain records, group descriptors, superblock state, and filesystem size counters.
- Error recovery relies heavily on the resize in-progress flag for offline operations.
- Online and offline paths share `run_resize()` but differ in who commits linkage; maintaining invariant parity is subtle.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_resize_volume.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_block.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_block.c

## Role

Implements journal block mode toggles exposed through `-J block64`, `-J block32`, `-J noblock64`, and `-J noblock32`.

## Operations

`set_journal_block32_run()` clears `JBD2_FEATURE_INCOMPAT_64BIT` from journal feature options by passing a mask with no corresponding option bit. It refuses block32 mode if the filesystem has more than `UINT32_MAX` blocks.

`set_journal_block64_run()` enables `JBD2_FEATURE_INCOMPAT_64BIT` for all journals and also sets `OCFS2_FEATURE_COMPAT_JBD2_SB` in the OCFS2 superblock before resizing/updating journals.

Both paths call `tunefs_set_journal_size(fs, 0, mask, options)`, where size zero means preserve or infer current journal sizing while updating features.

## Metadata Touched

- Journal superblock feature bits through `tunefs_set_journal_size()`
- OCFS2 superblock `s_feature_compat` for block64 enablement
- Superblock write on block64 path

## Open Flags

Both operations require `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Notable Risks

- The block64 path writes the OCFS2 superblock before updating all journal feature bits. If the journal update then fails, the filesystem may have partially advanced compatibility metadata.
- Error message says “more that” rather than “more than”; cosmetic only.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_block.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_size.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_size.c

## Role

Implements `-J size=<journal-size>`, resizing all OCFS2 journals.

## Parse Flow

`set_journal_size_parse_option()` requires an argument, allocates a `uint64_t`, parses the size with `tunefs_get_number()`, and stores the pointer in `op->to_private`.

## Run Flow

`set_journal_size_run()` reads and frees the stored size pointer, prompts the user, then calls `tunefs_set_journal_size()` with null feature masks/options to resize journals without changing journal feature bits.

Writes are wrapped in `tunefs_block_signals()` / `tunefs_unblock_signals()`.

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`, because journal resizing allocates or frees filesystem space.

## Notable Risks

- The code frees `op->to_private` before prompting. That is fine because it copies the value to `new_size`, but retry/reuse of the same operation object would not have parse state afterward.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_size.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_label.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_label.c

## Role

Implements `-L/--label <label>`, changing the OCFS2 volume label in the superblock.

## Parse Flow

`set_label_parse_option()` requires an argument and stores the argv pointer in `op->to_private`.

## Run Flow

`update_volume_label()` compares the requested label against the current superblock label, including NUL when possible, and skips work if already matching. Otherwise it prompts, starts progress, zeroes `s_label`, copies the requested label truncated to `OCFS2_MAX_VOL_LABEL_LEN`, and writes the superblock under signal blocking.

## Metadata Touched

- `OCFS2_RAW_SB(fs->fs_super)->s_label`
- Superblock write via `ocfs2_write_super()`

## Open Flags

Declared as `TUNEFS_FLAG_RW`.

## Notable Risks

- The label argument is not rejected when longer than the max; it is silently truncated.
- The operation stores an argv pointer rather than duplicating the label. This is acceptable for the CLI lifecycle.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_label.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_quota_sync_interval.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_quota_sync_interval.c

## Role

Implements `--usrquota-sync-interval <ms>` and `--grpquota-sync-interval <ms>`, changing the interval used to sync local quota structures to global quota files.

## Parse Flow

`set_quota_sync_interval_parse_option()` parses an unsigned decimal integer with `strtoul()`. It requires:

- fully numeric input
- minimum `100`
- maximum `4294967295`
- not `ULONG_MAX`

The value is stored directly in `op->to_private` via integer-to-pointer cast.

## Run Flow

`update_sync_interval()` checks that the relevant quota feature is enabled, initializes quota info, reads global quota info, compares the existing `dqi_syncms`, prompts if changing, writes the new interval to `fs->qinfo[type].qi_info.dqi_syncms`, and calls `ocfs2_write_global_quota_info()` under signal blocking.

## Metadata Touched

- Global user or group quota info file, specifically `dqi_syncms`

## Open Flags

Both operations are declared `TUNEFS_FLAG_RW`.

## Notable Risks

- The integer value is carried through `void *`. This is common in older C code but not type-safe and relies on pointer width being sufficient.
- On progress allocation failure, the code calls `tcom_err(err, ...)` where `err` may contain the previous successful value rather than `TUNEFS_ET_NO_MEMORY`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_quota_sync_interval.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_slot_count.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_slot_count.c

## Role

Implements `-N/--node-slots <count>`, increasing or decreasing the maximum number of OCFS2 node slots. This is one of the most invasive tunefs operations because slots own journals, local allocators, orphan dirs, truncate logs, and quota files.

## Parse Flow

`set_slot_count_parse_option()` parses a positive integer with `strtol()`, rejects non-numeric input, overflow sentinel values, values below 1, and values above `INT_MAX`. It defers filesystem-format-specific max validation until the filesystem is open.

## Increasing Slots

`add_slots()` determines the max slot count from slot map format:

- extended slot map: `INT16_MAX`
- old slot map: `OCFS2_MAX_SLOTS`

It creates per-slot system files for each new slot and each non-global system inode type. It skips local quota files unless the corresponding quota feature is enabled. Directory system inodes are initialized with `ocfs2_init_dir()`, all new inodes are linked into the system directory, and local quota files are initialized when created.

After adding slots, `update_slot_count()` sets `s_max_slots`, calls `tunefs_set_journal_size(fs, 0, ...)` to allocate space for new journals, formats the slot map, and writes the superblock.

## Decreasing Slots

Before removing slots, `remove_slot_check()` ensures slots being removed are safe:

- orphan directories must be empty
- local alloc files must be empty
- truncate logs must be empty

`remove_slots()` sets `OCFS2_TUNEFS_INPROG_REMOVE_SLOT`, then removes slots one at a time from the highest slot downward. For each removed slot it:

1. Relinks extent allocator chains into remaining slots.
2. Relinks inode allocator chains into remaining slots.
3. Truncates the removed slot's orphan directory.
4. Zeroes and truncates the removed slot's journal.
5. Truncates local quota files when quota is enabled.
6. Decrements `s_max_slots` and writes the primary superblock before deleting system dir entries.
7. Deletes system directory entries for the removed slot.
8. Decrements the system directory link count for the removed orphan dir.

`update_slot_count()` clears the remove-slot in-progress flag only after successful removal, formats the slot map, and writes the final superblock.

## Allocator Relinking

`relink_system_alloc()` moves allocator chain records from a removed slot to remaining slots.

`move_chain_rec()` reads all group descriptors in a chain into a temporary reversed list, updates suballocator slot metadata in allocated inodes or extent blocks, and moves each group to a destination allocator.

`move_group()` rewrites group descriptor parent/chain linkage and updates destination bitmap inode totals, free counts, cluster counts, and size.

This careful order is designed so `fsck.ocfs2` can recover or continue after failures.

## Journal Cleanup

`empty_journal()` writes zeroes over the journal contents before truncation. The comment explains this prevents old journal blocks from later looking like valid inode blocks if the space is reused.

## Metadata Touched

- System directory entries
- Per-slot system inodes
- Local quota files
- Orphan dirs
- Journals
- Extent and inode allocator chain records
- Group descriptors
- Inode/extent suballocator slot fields
- Superblock `s_max_slots`
- Slot map
- Tunefs in-progress flags

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Notable Risks

- Very high blast radius. Failures can leave partially moved allocator groups or removed-slot artifacts, although the operation uses in-progress state and ordering to aid fsck recovery.
- `decrease_link_count()` takes `uint16_t blkno`, but inode block numbers elsewhere are `uint64_t`. Passing `fs->fs_sysdir_blkno` through `uint16_t` can truncate block numbers on large filesystems.
- `remove_slot_iterate()` computes `dname + (dirent->name_len - taillen)` without first checking that `dirent->name_len >= taillen`; malformed or unexpected short names can underflow the pointer.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_slot_count.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_update_cluster_stack.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_update_cluster_stack.c

## Role

Implements `--update-cluster-stack`, updating on-disk OCFS2 cluster stack information to match the currently running cluster.

## Run Flow

`update_cluster_stack_run()` only performs the update when invoked under `TUNEFS_FLAG_NOCLUSTER`, which is how the main driver routes operations after `tunefs_open()` reports invalid stack information. If the filesystem is already configured for the running cluster, it prints a no-op message.

`update_cluster()` prompts with a critical warning, starts progress, obtains the running cluster descriptor with `o2cb_running_cluster_desc()`, writes it to the filesystem with `ocfs2_set_cluster_desc()`, frees the descriptor, and stops progress.

## Metadata Touched

- On-disk cluster descriptor via `ocfs2_set_cluster_desc()`

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_NOCLUSTER`.

## Safety Model

The prompt warns that no other node may be using the filesystem while its cluster configuration is modified. The metadata write is wrapped in signal blocking.

## Notable Risks

- This operation changes cluster identity/configuration metadata. Misuse can make the filesystem unsafe in a multi-node cluster.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_update_cluster_stack.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/tunefs.ocfs2.8.in -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/tunefs.ocfs2.8.in

## Role

Manual page template for `tunefs.ocfs2(8)`. It documents the command synopsis, operational expectations, options, query format specifiers, example usage, related tools, and copyright.

## Documented Behavior

The description says `tunefs.ocfs2` adjusts OCFS2 filesystem parameters on disk and expects the cluster to be online so it can take appropriate cluster locks for safe writes.

Documented options include:

- `--cloned-volume[=new-label]`
- `--fs-features=[no]feature...`
- `-J/--journal-options`
- `-L/--label`
- `-N/--node-slots`
- `-S/--volume-size`
- `-Q/--query`
- `-q/--quiet`
- `-U/--uuid-reset[=new-uuid]`
- `-v/--verbose`
- `-V/--version`
- `-y/--yes`
- `-n/--no`
- `--backup-super`
- `--list-sparse`
- `--update-cluster-stack`
- resize trailing `blocks-count`

The query section documents the same custom specifiers implemented in `op_query.c`: `B`, `T`, `N`, `R`, `Y`, `P`, `V`, `U`, `M`, `H`, and `O`.

## Important Warnings

The manual warns that `--cloned-volume` does not clone a volume; it only changes UUID/label so a clone can be mounted near the original.

The UUID reset section warns that duplicate UUIDs can cause erratic behavior or filesystem corruption.

The cluster stack section points users who want to update on-disk cluster stack without starting the new cluster toward `o2cluster(8)`.

## Consistency Notes

- The manpage documents `-N` valid range as 1 to 255, but the implementation allows larger counts when the filesystem uses the extended slot map.
- The synopsis does not mention the quota sync interval options implemented in `op_set_quota_sync_interval.c`.
- The synopsis includes short option cluster `-ipqnSUvVy`; implementation also has long-only progress and several long-only operations.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/tunefs.ocfs2.8.in -->