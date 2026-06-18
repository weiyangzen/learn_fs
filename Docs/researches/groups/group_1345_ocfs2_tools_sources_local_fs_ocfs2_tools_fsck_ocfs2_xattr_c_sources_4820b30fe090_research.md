# Group Research: group_1345_ocfs2_tools_sources_local_fs_ocfs2_tools_fsck_ocfs2_xattr_c_sources_4820b30fe090

Scope: `Docs/research_subset_a.md`, covering `sources/local-fs/ocfs2-tools`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/xattr.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/xattr.c

This file implements fsck validation and repair for OCFS2 extended attributes stored inline in inodes, in external xattr blocks, and in indexed xattr buckets.

Key structures and helpers:
- Defines xattr locations `IN_INODE`, `IN_BLOCK`, and `IN_BUCKET`, with `xattr_info` carrying location, max valid offset, and block number for diagnostics.
- Uses `used_area` and `used_map` to track occupied header, entry, and name/value regions while validating xattr layout.
- `check_xattr_count()` detects plausible entry count from terminators, bucket hash ordering, and object size limits, then optionally fixes `xh_count`.
- `check_xattr_entry()` validates entry placement, name offsets, local-vs-external value sizing, name/value overlap, and name hash correctness; bad entries are compacted out of the header.
- `check_xattr_value()` verifies extent lists for non-local xattr values through shared extent-checking callbacks.

Control flow:
- `check_xattr()` runs count, entry, external-value, and bucket-only free-space metadata checks.
- `ocfs2_check_xattr_buckets()` reads a run of xattr buckets, detects or fixes bucket count, validates each bucket, and writes changed buckets.
- `o2fsck_check_xattr_index_block()` validates indexed xattr extent records, writes the root if changed, then walks bucket records via `ocfs2_xattr_get_rec()`.
- `o2fsck_check_xattr_block()` validates the external xattr block signature, then dispatches to inline block-header checking or indexed checking.
- `o2fsck_check_xattr_ibody()` locates inline xattr storage at the end of the inode block.
- Public entry `o2fsck_check_xattr()` is gated by `OCFS2_HAS_XATTR_FL`, handles inline xattrs first, writes changed inodes, then checks `i_xattr_loc`.

Integration notes:
- Depends on libocfs2 xattr helpers, fsck prompt/problem infrastructure, and `check_el()` from extent validation.
- Repairs are interactive via `prompt()` and mark buffers dirty through local `changed` flags.
- Important correctness concern: layout validation is defensive but manually manages offset arithmetic and list allocation; bad repair choices can leave stale name/value data intentionally in place while compacting only entries.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/Makefile

This Makefile builds the `fswreck` test utility, a deliberately destructive OCFS2 corruption injector used to exercise `fsck.ocfs2`.

Key build content:
- Includes top-level `Preamble.make` and `Postamble.make`.
- Defines `UNINST_PROGRAMS = fswreck`, so the utility is built but not installed as a normal public program.
- Compiles corruption modules for chains, extents, groups, inodes, local alloc, truncate logs, special files, symlinks, directories, journals, quotas, refcounts, and discontiguous block groups.
- Exports matching headers under `include/`.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, GLib, com_err, and AIO libraries.
- Conditionally links `-ldlm_lt` when `BUILD_FSDLM_SUPPORT` is enabled.

Integration notes:
- The source list mirrors the corruption dispatch table in `main.c`.
- `dist-subdircreate` ensures the distribution include directory exists.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/chain.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/chain.c

This file injects corruption into OCFS2 chain allocator metadata and superblock cluster counts.

Key behavior:
- `mess_up_sys_file()` reads a bitmap/chain inode, verifies `OCFS2_BITMAP_FL` and `OCFS2_CHAIN_FL`, then mutates chain list, chain record, inode bitmap, or pointed group descriptor fields depending on `fsck_type`.
- Supported chain corruptions include invalid `cl_count`, `cl_next_free_rec`, zero chain head block, bad inode `i_clusters` or `i_size`, bad bitmap used count, out-of-range chain head block, bad group generation, bad group signature, bad group next pointer, bad `c_total`, and bad `cl_cpg`.
- `mess_up_sys_chains()` resolves either the global bitmap system inode or a slot-local inode allocator before calling `mess_up_sys_file()`.
- Public wrappers group corruption families for the dispatcher: chain list, record, inode, group, group magic, and CPG.
- `mess_up_superblock_clusters()` copies the superblock inode block, changes `i_clusters` by roughly 2.5 cluster groups, and writes it directly with `io_write_block()`.
- `mess_up_superblock_clusters_excess()` and `_lack()` choose increment or decrement.

Integration notes:
- Uses libocfs2 system inode lookup, group descriptor reads/writes, and block allocation geometry helpers.
- Some corruption paths require at least one chain record and warn instead of changing metadata if none exists.
- Superblock cluster corruption is marked in `main.c` as needing `nometaecc`, because it writes a copied superblock directly.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/chain.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/corrupt.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/corrupt.c

This file is the central dispatcher from `enum fsck_type` values to specific corruption helper functions.

Key behavior:
- `create_named_directory()` ensures a named directory exists under the root, creating and linking it if absent.
- `corrupt_file()` maps file-oriented corruption codes to helpers for extents, inodes, symlinks, root/special files, directories, inline data, duplicate clusters, and refcount inode fields. It creates/uses a root-level `tmp` directory as the parent object.
- `corrupt_sys_file()` maps system-file corruption codes to chain, superblock, inode orphan/allocation, journal, and quota helpers.
- `corrupt_group_desc()` maps allocation group descriptor corruption codes to group helpers.
- `corrupt_local_alloc()` maps local allocation corruption codes.
- `corrupt_truncate_log()` maps truncate log corruption codes.
- `corrupt_refcount()` maps refcount tree/block corruption codes and uses `tmp` as a parent directory.
- `corrupt_discontig_bg()` directly forwards to discontiguous block-group corruption.

Integration notes:
- The switch coverage must stay synchronized with `fsck_type.h` and `main.c` prompt table.
- Invalid codes terminate via `FSWRK_FATAL`.
- This file has little mutation logic itself; its main risk is stale or incomplete dispatch mapping when new fsck prompt codes are added.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/corrupt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/dir.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/dir.c

This file creates directory and dirent corruptions for fsck testing.

Key behavior:
- `create_directory()` creates a uniquely named directory under a parent using `ocfs2_new_inode()`, `ocfs2_init_dir()`, and `ocfs2_link()`.
- Dirent iterator helpers rename entries, alter inode numbers, and alter record lengths via `ocfs2_dir_iterate()`.
- `damage_dir_content()` injects dirent-level corruptions:
  - duplicate `.`
  - rename `.` away from dot
  - invalid `.` or `..` inode number
  - excessive dot record length
  - zero-length/zero-name entry
  - invalid slash-containing name
  - out-of-range inode
  - free inode reference
  - mismatched file type
  - duplicate names
  - invalid record length
- `mess_up_dir_ent()` creates a child directory and corrupts its content.
- `mess_up_dir_parent_dup()` creates one directory linked from two parents.
- `mess_up_dir_inode()` corrupts directory inode extent state, including an empty directory extent list (`DIR_ZERO`) or manipulated extent records creating a directory hole (`DIR_HOLE`).
- `mess_up_dir_not_connected()` creates an initialized directory inode without linking it into any parent.

Integration notes:
- Relies on helpers from `extent.c` and `corrupt.c` for creating files/directories.
- Uses `mktemp()`, intentionally noted by comments as acceptable for this Linux-only utility.
- Several corruption paths assume non-inline directory data or enough generated entries to create extents.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/discontig_bg.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/discontig_bg.c

This file injects corruption into OCFS2 discontiguous block group descriptors.

Key behavior:
- `create_discontig_bg_list()` builds a synthetic extent-list mapping for a group descriptor by splitting the group’s clusters across several records.
- `create_discontig_bg()` adds a new discontiguous inode allocation group for a slot:
  - resolves the slot inode allocator
  - allocates a cluster group
  - initializes an OCFS2 group descriptor
  - replaces the target chain head and links the previous group through `bg_next_group`
  - updates chain totals, inode clusters, inode size, and bitmap accounting
- `mess_up_discontig_bg()` verifies the volume supports discontiguous block groups, creates a fresh discontiguous group, then corrupts one requested field.

Supported corruptions:
- Bad extent-list tree depth, list count, record block range, record cluster counts, total cluster accounting through `l_next_free_rec`, and mixed list/record corruption patterns.

Integration notes:
- Uses `assert.h`, libocfs2 group initialization, allocation, and geometry helpers.
- Many corruptions deliberately make extent list cluster totals inconsistent with the group’s cluster-per-group value.
- Requires an OCFS2 volume with discontiguous block group support.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/discontig_bg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/extent.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/extent.c

This file creates extent tree, extent block, and extent record corruptions.

Key behavior:
- `create_file()` creates and links a regular file under a directory.
- `custom_extend_allocation()` allocates clusters and inserts them in reverse order to prevent extent coalescing and force extent-tree growth.
- `damage_extent_block()` reads a file inode and its first extent block, then corrupts extent block self block number, generation, signature, list depth, list count, or next-free record.
- `damage_extent_block_by_type()` creates a file and extends it enough to guarantee an extent block before damaging it.
- `mess_up_extent_list()` and `mess_up_extent_block()` both delegate to `damage_extent_block_by_type()`.
- `mess_up_record()` corrupts inline inode extent records:
  - invalid unwritten/refcounted flags on unsupported filesystems
  - unaligned block number
  - cluster overrun near filesystem end
  - block number in invalid range
  - overlapping extents
  - holes by moving `e_cpos`
- `mess_up_extent_record()` creates a file, allocates one cluster, then corrupts its first record.

Integration notes:
- Uses libocfs2 allocation and extent insertion APIs rather than raw bitmap writes for setup.
- Feature-gated corruptions intentionally require volumes without unwritten or refcount support.
- `EXTENT_OVERLAP` and `EXTENT_HOLE` re-read the inode after extending, but keep using the already assigned extent list pointer from the buffer.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/extent.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/group.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/group.c

This file injects allocation group descriptor and global bitmap corruptions.

Key behavior:
- `create_test_group_desc()` allocates one cluster and writes a cloned group descriptor at that block, with adjusted `bg_blkno` and cleared `bg_next_group`.
- `damage_group_desc()` reads a bitmap chain inode, finds the first chain record and group descriptor, then mutates group linkage and fields.
- Supported descriptor corruptions include missing expected descriptor, unexpected fake descriptor, bad generation, bad parent dinode, bad block number, bad chain number, self-looped group chain, and impossible free-bit count.
- `mess_up_group_desc()` resolves either the global bitmap or a slot inode allocator, then calls `damage_group_desc()`.
- Public wrappers split minor field, generation, list, cluster group descriptor, and cluster allocation bit corruption.
- `mess_up_cluster_group_desc()` allocates clusters, locates their group descriptor, then inflates `bg_free_bits_count`.
- `mess_up_cluster_alloc_bits()` allocates a cluster without using it later, leaving global bitmap bits marked.

Integration notes:
- Used by `corrupt_group_desc()` and some bitmap-related prompt codes.
- Depends on OCFS2 chain allocator structures and group bitmap sizing.
- Some paths write cloned/fake descriptors directly, so generated test volumes may contain extra allocated-but-inconsistent metadata.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/group.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/chain.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/chain.h

This header declares chain and superblock cluster corruption entry points implemented in `chain.c`.

Exports:
- Chain list, record, inode, group, group magic, and CPG corruption functions.
- Superblock cluster excess/lack corruption functions.
- All functions accept `ocfs2_filesys *`, `enum fsck_type`, and slot number.

Integration notes:
- Included through `main.h`.
- Used by `corrupt.c` dispatch for system-file corruption codes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/chain.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/corrupt.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/corrupt.h

This header declares the top-level fswreck corruption dispatch functions implemented in `corrupt.c`.

Exports:
- Dispatchers for file, system file, group descriptor, inode, local alloc, truncate log, refcount, and discontiguous block-group corruption.
- `create_named_directory()` helper for creating root-level working directories.

Integration notes:
- Included by `main.h`.
- `corrupt_inode()` is declared here but no implementation was present in this grouped source set; main dispatch uses other corruption dispatchers directly.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/corrupt.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/dir.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/dir.h

This header declares directory corruption helpers implemented in `dir.c`.

Exports:
- Directory inode, dot, dotdot, dirent, duplicate-parent, and disconnected-directory corruption functions.
- `create_directory()` helper.

Integration notes:
- `mess_up_dir_dot()` and `mess_up_dir_dotdot()` are declared but not implemented in the read `dir.c`; dot and dotdot corruptions are handled through `mess_up_dir_ent()` cases.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/discontig_bg.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/discontig_bg.h

This header declares `mess_up_discontig_bg()` for discontiguous block-group corruption.

Integration notes:
- Included through `main.h`.
- Implemented in `discontig_bg.c` and called through `corrupt_discontig_bg()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/discontig_bg.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/extent.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/extent.h

This header declares extent corruption helpers and the shared regular-file creation helper.

Exports:
- `mess_up_extent_list()`
- `mess_up_extent_block()`
- `mess_up_extent_record()`
- `create_file()`

Integration notes:
- `create_file()` is reused by inode, directory, symlink, and refcount corruption modules.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/extent.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/fsck_type.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/fsck_type.h

This header defines the fswreck corruption code namespace.

Key content:
- `enum fsck_type` enumerates corruption IDs from `EB_BLKNO` through `INODE_VALID_FLAG`, ending at `NUM_FSCK_TYPE`.
- The enum mirrors `fsck.ocfs2` prompt codes so fswreck can create test cases for fsck repairs.
- Covers extent blocks/lists/records, chain metadata, superblock clusters, group descriptors, discontiguous block groups, inode fields, local alloc, truncate logs, symlinks, directories, inline data, duplicate clusters, journals, quotas, refcounts, metadata ECC, and inode valid flag.
- Long comment groups enum values into conceptual categories and notes unimplemented historical local alloc codes.

Integration notes:
- `main.c` uses enum values as direct indexes into `prompt_codes[]` and `corrupt[]`.
- Any insertion or reorder must be synchronized with prompt table definitions and fsck prompt-code expectations.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/fsck_type.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/group.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/group.h

This header declares group descriptor and cluster allocation corruption helpers.

Exports:
- `mess_up_group_minor()`
- `mess_up_group_gen()`
- `mess_up_group_list()`
- `mess_up_cluster_group_desc()`
- `mess_up_cluster_alloc_bits()`

Integration notes:
- Implemented in `group.c`.
- Used by `corrupt_group_desc()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/group.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/inode.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/inode.h

This header declares inode, inline-data, and duplicate-cluster corruption helpers.

Exports:
- Field corruption, disconnected inode, orphaned inode, invalid inode allocation, inline flag, inline inode metadata, and duplicate cluster helpers.

Integration notes:
- Implemented in `inode.c`.
- Used mainly by `corrupt_file()` and `corrupt_sys_file()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/journal.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/journal.h

This header declares `mess_up_journal()` for journal system-file corruption.

Integration notes:
- Implemented in `journal.c`.
- Dispatched from `corrupt_sys_file()` for journal-related fsck types.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/local_alloc.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/local_alloc.h

This header declares local allocation inode corruption helpers.

Exports:
- Empty local alloc metadata corruption.
- Local alloc bitmap corruption.
- Local alloc used-count corruption.

Integration notes:
- Implemented in `local_alloc.c`.
- Used by `corrupt_local_alloc()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/local_alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/main.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/main.h

This is fswreck’s shared umbrella header.

Key content:
- Enables `_GNU_SOURCE`.
- Includes standard C/POSIX, GLib, Linux type, and libocfs2 headers.
- Defines fatal/warning macros:
  - `FSWRK_FATAL`
  - `FSWRK_COM_FATAL`
  - `FSWRK_FATAL_STR`
  - `FSWRK_WARN`
  - `FSWRK_WARN_STR`
- Defines local `max`, `min`, and `ARRAY_ELEMENTS`.
- Includes `fsck_type.h` and every fswreck module header.

Integration notes:
- All fswreck C files include this header, making it the central dependency surface.
- Fatal macros raise `SIGTERM` and exit, so most helper errors terminate the process rather than returning status.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/main.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/quota.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/quota.h

This header declares `mess_up_quota()` for quota system-file corruption.

Integration notes:
- Implemented in `quota.c`.
- Dispatched from `corrupt_sys_file()` for quota fsck types.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/refcount.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/refcount.h

This header declares refcount tree corruption helpers.

Exports:
- `mess_up_refcount_tree_block()` for root/leaf refcount block and record corruption.
- `mess_up_refcount_tree()` for tree-level `rf_clusters` and `rf_count` corruption.

Integration notes:
- Implemented in `refcount.c`.
- Requires refcount-enabled volumes for most paths.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/special.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/special.h

This header declares `mess_up_root()` for root/lost+found related special-file corruption.

Integration notes:
- Implemented in `special.c`.
- Used by `corrupt_file()` for root directory and lost+found prompt codes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/special.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/symlink.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/symlink.h

This header declares `mess_up_symlink()` for symlink corruption.

Integration notes:
- Implemented in `symlink.c`.
- Used by `corrupt_file()` for symlink prompt codes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/symlink.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/truncate_log.h -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/include/truncate_log.h

This header declares truncate log corruption helpers.

Exports:
- `mess_up_truncate_log_list()` for truncate log header/list fields.
- `mess_up_truncate_log_rec()` for individual truncate records.

Integration notes:
- Implemented in `truncate_log.c`.
- Used by `corrupt_truncate_log()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/include/truncate_log.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/inode.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/inode.c

This file creates inode, inline-data, orphan, allocation, refcount-flag, metadata-ECC, and duplicate-cluster corruptions.

Key behavior:
- `damage_inode()` mutates a target inode field based on `fsck_type`, including generation, block number, delete time, suballoc slot, size, sparse size/clusters, link count, metadata ECC, valid flag, refcount feature flag, and refcount location.
- `mess_up_inode_field()` creates a file under the supplied directory, optionally prepares sparse/allocated state, feature-gates refcount scenarios, then calls `damage_inode()`.
- `mess_up_inode_not_connected()` allocates a regular inode without linking it.
- `mess_up_inode_orphaned()` creates a file under a slot orphan directory.
- `mess_up_inode_alloc()` allocates an inode and clears `OCFS2_VALID_FL`.
- `mess_up_inline_flag()` sets inline-data flags on regular file and directory inodes on a volume that does not support inline data.
- `mess_up_inline_inode()` creates inline regular and directory inodes, then corrupts `id_count`, `i_size`, or `i_clusters`.
- `mess_up_dup_clusters()` creates duplicate cluster ownership between two regular files or between a regular file and the journal system file.

Integration notes:
- Reuses `create_file()` and `create_directory()`.
- Uses `ocfs2_write_inode_without_meta_ecc()` specifically to preserve bad ECC for `INODE_BLOCK_ECC`.
- Many paths are feature-sensitive and intentionally abort if run against the wrong mkfs feature set.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/journal.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/journal.c

This file corrupts OCFS2 journal system files.

Key behavior:
- `mess_up_journal()` resolves the journal system inode for the requested slot, reads its cached inode, maps the first journal block, and reads the JBD2 journal superblock.
- `JOURNAL_FILE_INVALID` flips the JBD2 magic.
- `JOURNAL_UNKNOWN_FEATURE` sets unknown incompatible and read-only compatible feature bits.
- `JOURNAL_MISSING_FEATURE` requires multiple slots, sets all known features on an adjacent journal, then clears known features on the target journal.
- `JOURNAL_TOO_SMALL` sets the journal inode’s cluster count to zero.
- Writes the modified journal superblock and cached inode.

Integration notes:
- Depends on libocfs2 cached inode and extent map APIs plus JBD2 constants.
- Slot default is the last configured slot when caller passes `UINT16_MAX`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/local_alloc.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/local_alloc.c

This file creates corruptions in slot-local allocation system inodes.

Key behavior:
- `get_local_alloc_window_bits()` returns a fixed test window of 256 bits.
- `create_local_alloc()` populates an empty local alloc inode by allocating clusters, setting `la_bm_off`, total/used bitmap counts, and clearing the bitmap.
- `damage_local_alloc()` mutates local alloc metadata:
  - invalid `la_size`
  - nonzero used count with zero total
  - nonzero bitmap offset with zero total
  - bitmap offset overrun or straddle
  - bitmap total larger than bitmap capacity
  - used count greater than total
- Public wrappers resolve the slot’s local alloc system inode and optionally create a non-empty local alloc before damaging bitmap/used cases.

Integration notes:
- Requires `OCFS2_LOCAL_ALLOC_FL` system inode.
- Some corruption types cannot run on an empty local alloc and warn/return.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/local_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/main.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/main.c

This is the `fswreck` command-line entry point and corruption-code registry.

Key structures:
- Global `progname`, `device`, selected `slotnum`, and `corrupt[NUM_FSCK_TYPE]`.
- `struct prompt_code` binds enum code, string name, required mkfs feature string, slot count, corruption function, and description.
- `prompt_codes[]` is indexed by `enum fsck_type` and defines all supported corruption codes, including unimplemented `LALLOC_REPAIR` and `LALLOC_USED` entries with NULL handlers.

CLI behavior:
- `-c` parses comma-separated corruption names.
- `-C` selects corruption by number.
- `-L` prints the string for a selected numeric code.
- `-l` lists all codes and descriptions.
- `-n` prints `NUM_FSCK_TYPE`.
- `-M` prints suggested mkfs options for the selected corruption, including required slots and feature toggles.
- `-N` selects a slot number.

Runtime flow:
- Initializes OCFS error table and signal handlers.
- Parses options, opens the target device read-write with `ocfs2_open()`.
- Iterates all selected corruption codes, skips NULL handlers with a message, and invokes each function.
- Closes the filesystem before returning.

Integration notes:
- This file must stay synchronized with `fsck_type.h` and implementation dispatchers in `corrupt.c`.
- The tool is intentionally destructive and prints a prominent warning in usage text.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/quota.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/quota.c

This file corrupts OCFS2 global user/group quota files.

Key behavior:
- Requires both user and group quota read-only compatible features.
- Initializes quota info for `USRQUOTA` and `GRPQUOTA`.
- `o2fswreck_read_blk()` and `o2fswreck_write_blk()` read/write quota-file logical blocks through `ocfs2_file_read()` and `ocfs2_file_write()`.
- `o2fswreck_get_data_blk()` recursively walks the quota tree to find a data block and records its block reference in global `g_actref`.
- `QMAGIC_INVALID` flips a user quota header magic after endian swapping.
- `QTREE_BLK_INVALID` corrupts a group quota tree block trailer checksum/ECC.
- `DQBLK_INVALID` corrupts a user quota data entry and leaf header free-list/entry counts.
- `DUP_DQBLK_INVALID` duplicates a group quota ID but gives the duplicate invalid limits and corrupts the leaf header.
- `DUP_DQBLK_VALID` duplicates a group quota ID with copied limit values.

Integration notes:
- Uses quota endian-swap helpers for on-disk structures.
- Allocates `tree_depth + 1` blocks as traversal/read scratch space.
- The global `g_actref` is a traversal side channel for writing the found data block back.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/refcount.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/refcount.c

This file creates and corrupts OCFS2 refcount trees.

Key behavior:
- `create_refcount_tree()` creates three files, allocates a new refcount root, attaches it to two files, inserts many refcounted extents in reverse order to force desired tree depth, updates refcounts to 2, and uses a third file to consume intervening clusters.
- `damage_refcount_block()` corrupts refcount block self block number, generation, parent, or signature.
- `damage_refcount_list()` corrupts refcount record-list count, used count, record cluster range, cluster collision, or empty-list state.
- `damage_refcount_record()` creates redundant/inconsistent records or invalid refcount values.
- `mess_up_refcount_tree_block()` creates both a depth-0 root-only tree and a depth-1 tree, then applies block/list/record corruption to root and/or leaf blocks as appropriate.
- `mess_up_refcount_tree()` creates a deeper tree and corrupts `rf_clusters` or `rf_count`.

Integration notes:
- Requires refcount-tree filesystem support.
- Uses assertions for expected tree layout after setup.
- Writes every touched root and leaf refcount block after corruption.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/special.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/special.c

This file handles root/lost+found style special corruptions.

Key behavior:
- `mess_up_root()` ignores the passed block number, resolves the filesystem root block from the superblock, reads the root inode, verifies it is valid, sets `i_mode` to zero, and writes it back.
- This makes the root no longer a directory, which also makes normal lost+found lookup fail.

Integration notes:
- Used for `ROOT_NOTDIR`, `ROOT_DIR_MISSING`, and `LOSTFOUND_MISSING` codes through `corrupt_file()`.
- The printed message always labels the corruption as `ROOT_NOTDIR` even when invoked for related codes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/special.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/symlink.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/symlink.c

This file creates and corrupts symbolic links.

Key behavior:
- Uses fixed target text `"/dummy00/dummy00"`.
- `fillup_block()` fills a block with repeated dummy text and is used as a block-iterator callback.
- `add_symlink()` maps the first allocated block of a symlink inode, writes the dummy target, and sets inode size.
- `create_symlink()` creates a symlink inode, links it into a directory, allocates one cluster, and initializes its target data.
- `corrupt_symlink_file()` validates the inode is a symlink, then applies:
  - `LINK_FAST_DATA`: set `i_clusters` to zero
  - `LINK_NULLTERM`: fill all blocks with dummy text and set size to a full cluster
  - `LINK_SIZE`: inflate `i_size`
  - `LINK_BLOCKS`: inflate first extent record’s `e_leaf_clusters`
- `mess_up_symlink()` creates a symlink and corrupts it.

Integration notes:
- Uses block iteration and cached inode helpers from libocfs2.
- Creates non-fast symlinks by allocating a cluster before corruption.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/truncate_log.c -->
# File Research: sources/local-fs/ocfs2-tools/fswreck/truncate_log.c

This file corrupts truncate log system inodes.

Key behavior:
- `create_truncate_log()` populates an empty truncate log with allocated cluster ranges, up to `tl_count`.
- `damage_truncate_log()` validates the inode has `OCFS2_DEALLOC_FL`, checks record availability for record-level corruptions, and mutates:
  - `tl_count`
  - `tl_used`
  - record start beyond filesystem cluster count
  - wrapped record start plus near-`UINT32_MAX` cluster count
  - record cluster count beyond filesystem size
- `get_truncate_log()` resolves the slot truncate log system inode.
- `mess_up_truncate_log_list()` damages header/list fields.
- `mess_up_truncate_log_rec()` creates ten truncate records, then damages selected records.

Integration notes:
- Uses endian conversion macros when creating records but direct assignment when corrupting fields.
- Slot default is slot 0 when caller passes `UINT16_MAX`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fswreck/truncate_log.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/include/Makefile

This Makefile coordinates installation/distribution of public include subdirectories.

Key content:
- Includes top-level make preamble/postamble.
- Defines `SUBDIRS = tools-internal ocfs2-kernel o2dlm o2cb ocfs2`.

Integration notes:
- This is a routing Makefile; actual header lists live in child directories.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/include/o2cb/Makefile

This Makefile prepares and installs public `o2cb` headers.

Key content:
- Generates `o2cb_err.h` by copying from `libo2cb`, building it there if needed.
- Lists public headers: `o2cb.h`, nodemanager, heartbeat, and client protocol.
- Sets `HEADERS_SUBDIR = o2cb`.
- Cleans generated `o2cb_err.h`.

Integration notes:
- Public include output depends on generated error-table headers from the library build.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/o2cb.h -->
# File Research: sources/local-fs/ocfs2-tools/include/o2cb/o2cb.h

This is the public userspace API header for O2CB cluster configuration, heartbeat, and control operations.

Key content:
- Defines cluster stack names: `o2cb`, `pcmk`, and `cman`.
- Provides inline validators for stack names, cluster names, classic O2CB alphanumeric cluster names, and heartbeat modes.
- Declares initialization, cluster create/remove/list, node add/delete/list/query, heartbeat region list/query, heartbeat mode, and daemon debug APIs.
- Defines `o2cb_cluster_desc` and `o2cb_region_desc`.
- Declares heartbeat lifecycle and group join/leave APIs.
- Declares region reference helpers and node property accessors.
- Declares control-daemon open/close, node-down notification, max locking protocol query, heartbeat control path lookup, and stack setup.

Integration notes:
- Includes generated `o2cb_err.h`, nodemanager/heartbeat public structs, and OCFS2 kernel filesystem definitions.
- Used by OCFS2 userspace tools that need cluster stack and heartbeat coordination.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/o2cb.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/o2cb_client_proto.h -->
# File Research: sources/local-fs/ocfs2-tools/include/o2cb/o2cb_client_proto.h

This header defines the userspace client protocol interface for OCFS2/O2CB control daemons.

Key content:
- Defines line length, argument count, and socket path constants for `ocfs2_controld` and `o2cb_controld`.
- Enumerates client messages such as mount, mount result, unmount, status, list filesystems, list mounts, list clusters, item count/item, and dump.
- Declares socket listen/connect helpers.
- Provides inline helpers for OCFS2 controld listen/connect.
- Declares message send/receive, full receive with rest string, received-list free, list receive, and status parse helpers.

Integration notes:
- This is protocol-facing API; implementations live outside this header.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/o2cb_client_proto.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_heartbeat.h -->
# File Research: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_heartbeat.h

This header defines the on-disk heartbeat block layout shared with the OCFS2 heartbeat subsystem.

Key structure:
- `struct o2hb_disk_heartbeat_block` contains sequence number, node id, checksum, generation, and dead timeout milliseconds.

Integration notes:
- Uses fixed-size endian-annotated integer types.
- Consumed by userspace code that reads or writes heartbeat region blocks.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_heartbeat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_nodemanager.h -->
# File Research: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_nodemanager.h

This header defines userspace-visible constants for the OCFS2 nodemanager kernel interface.

Key content:
- `O2NM_API_VERSION = 5`
- Maximum nodes: 255
- Invalid node number: 255
- Maximum name length: 64
- Maximum global heartbeat regions: 32, with warning that changing it breaks DLM compatibility.

Integration notes:
- Pure constants header; included by `o2cb.h`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_nodemanager.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2dlm/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/include/o2dlm/Makefile

This Makefile prepares and installs public `o2dlm` headers.

Key content:
- Generates `o2dlm_err.h` by copying from `libo2dlm`, building it there if missing.
- Installs `o2dlm.h` plus generated error header under `o2dlm`.
- Cleans generated `o2dlm_err.h`.

Integration notes:
- Mirrors the generated-error-header pattern used by the `o2cb` include Makefile.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2dlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2dlm/o2dlm.h -->
# File Research: sources/local-fs/ocfs2-tools/include/o2dlm/o2dlm.h

This is the public userspace API for OCFS2 DLM locking through dlmfs/stack glue.

Key content:
- Defines max lock ID length, max domain length, full domain path length, valid flags, and lock levels.
- Forward-declares `struct o2dlm_ctxt`.
- Declares `o2dlm_initialize()` and `o2dlm_destroy()`.
- Declares lock/unlock/drop-lock APIs.
- Declares `o2dlm_lock_with_bast()` and `o2dlm_process_bast()` for blocking AST notification through a pollable file descriptor.
- Declares LVB read/write APIs.
- Declares optional feature probes for BAST and stackglue support.

Integration notes:
- Includes generated `o2dlm_err.h`.
- API users must respect lock ID and domain length constraints.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/o2dlm/o2dlm.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/Makefile

This Makefile lists kernel-derived OCFS2 compatibility headers exported for userspace builds.

Key content:
- Installs under `ocfs2-kernel`.
- Header list includes list helpers, OCFS1 compatibility, OCFS2 filesystem/ioctl/lockid definitions, quota tree, and sparse endian type annotations.

Integration notes:
- The grouped source list only included `kernel-list.h` and `ocfs1_fs_compat.h`; this Makefile references additional headers in the same public include area.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/kernel-list.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/kernel-list.h

This header provides a small userspace copy of Linux kernel doubly linked-list primitives.

Key content:
- Defines `struct list_head`.
- Defines list initialization macros.
- Implements inline add, add-tail, delete, empty check, and splice operations.
- Provides `list_entry`, `list_for_each`, and `list_for_each_safe`.

Integration notes:
- Used by OCFS2 userspace code needing kernel-style list manipulation.
- Does not poison deleted entries, unlike some kernel debug variants.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/kernel-list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs1_fs_compat.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs1_fs_compat.h

This header defines OCFS1 compatibility volume header structures written by OCFS2.

Key content:
- Defines OCFS1 length limits, version constants, and `OCFS1_VOLUME_SIGNATURE`.
- `struct ocfs1_vol_disk_hdr` models the sector-0 OCFS1 volume header, including signature, mount point, offsets, sizes, node counts, and config fields.
- `struct ocfs1_disk_lock` models an OCFS1 disk lock with explicit padding for alignment.
- `struct ocfs1_vol_label` models the sector-1 volume label, including disk lock, label, volume ID, and cluster name.

Integration notes:
- OCFS2 writes valid but unmountable OCFS1 headers so OCFS1 can detect the partition and fail cleanly.
- This is structure definition only; no functions are declared.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs1_fs_compat.h -->