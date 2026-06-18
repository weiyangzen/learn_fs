# subset-b-005707 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.c

## Purpose
This file implements NILFS2 sysfs support. It creates the global `/sys/fs/nilfs2` kset, a global `features` group, per-mounted-device groups named by `sb->s_id`, per-device subgroups for mounted snapshots, checkpoints, segments, superblock state, and segment-constructor state, plus per-snapshot kobjects.

## Important APIs, Types, And Functions
The public entry points are `nilfs_sysfs_init()`, `nilfs_sysfs_exit()`, `nilfs_sysfs_create_device_group()`, `nilfs_sysfs_delete_device_group()`, `nilfs_sysfs_create_snapshot_group()`, and `nilfs_sysfs_delete_snapshot_group()`. Macro families `NILFS_DEV_INT_GROUP_OPS`, `NILFS_DEV_INT_GROUP_TYPE`, and `NILFS_DEV_INT_GROUP_FNS` generate repetitive sysfs show/store plumbing for internal device subgroups. Attribute callbacks expose data from `struct the_nilfs`, `struct nilfs_root`, `nilfs_cpfile_get_stat()`, `nilfs_sufile_get_stat()`, `nilfs_sufile_get_ncleansegs()`, and raw NILFS superblock fields.

## Control Flow
Module initialization creates the root kset under `fs_kobj`, then adds the `features` attribute group. Mount-time `nilfs_sysfs_create_device_group()` allocates `nilfs_sysfs_dev_subgroups`, initializes the device kobject, and creates subgroups in a strict order: mounted snapshots, checkpoints, segments, superblock, and segctor. Error paths unwind previously-created groups in reverse. Snapshot groups are attached either as `current_checkpoint` under the device group for checkpoint zero, or by checkpoint number under `mounted_snapshots`.

## State, Persistence, And Dependencies
Sysfs files are live views of in-memory and on-disk state rather than persistent files. Reads use `ns_sem`, `ns_segctor_sem`, `ns_last_segment_lock`, and metadata semaphores as appropriate. The only writable attribute is `superblock/sb_update_frequency`; its store parser clamps values below `NILFS_SB_FREQ` and updates `nilfs->ns_sb_update_freq` under `ns_sem`.

## Integration Points
`the_nilfs.c` calls the device-group creator after loading metadata files and calls deletion during failed mount cleanup. `nilfs_find_or_create_root()` and `nilfs_put_root()` create/delete snapshot groups. The exported telemetry is consumed by userspace monitoring, diagnostics, and filesystem administration tools.

## Risks
Kobject lifetime is the main risk: subgroups use `kobject_put()` and release completions, but this file does not wait on the completions directly. Any mismatch between creation order and deletion order can leak or expose stale sysfs nodes. Attribute callbacks also assume required metadata inodes and raw superblock pointers are valid while sysfs is visible. `nilfs_dev_volume_name_show()` uses `scnprintf()` with the raw field size, so malformed non-NUL-terminated volume names should be treated carefully by reviewers.

## Test Signals
Useful signals are mount/unmount cycles, fault injection in each subgroup creation step, reads of every sysfs attribute while segment construction and checkpoint creation are active, writes of `sb_update_frequency` including invalid and too-small values, snapshot mount/unmount tests, and KASAN/KCSAN runs around kobject teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.h

## Purpose
This header declares the NILFS2 sysfs support data structures and attribute-definition macros used by `sysfs.c`. It centralizes the sysfs root name, per-device subgroup kobjects, and strongly-typed attribute wrapper structures for feature, device, subgroup, and snapshot sysfs files.

## Important APIs, Types, And Functions
`NILFS_ROOT_GROUP_NAME` defines the root sysfs directory name `nilfs2`. `struct nilfs_sysfs_dev_subgroups` embeds kobjects and unregister completions for `superblock`, `segctor`, `mounted_snapshots`, `checkpoints`, and `segments`. Macro families `NILFS_KOBJ_ATTR_STRUCT`, `NILFS_DEV_ATTR_STRUCT`, and `NILFS_CP_ATTR_STRUCT` define attribute structs with matching callback signatures. `NILFS_RO_ATTR`, `NILFS_RW_ATTR`, and the group-specific wrappers instantiate `__ATTR()` records, while `*_ATTR_LIST()` macros feed attribute arrays.

## Control Flow
The header has no executable control flow; it shapes compile-time code generation. `sysfs.c` uses the macros by defining concrete show/store functions first, then expanding macros such as `NILFS_SUPERBLOCK_RW_ATTR(sb_update_frequency)` and placing their `struct attribute` members into `ATTRIBUTE_GROUPS()` arrays.

## State, Persistence, And Dependencies
State is embedded into `struct the_nilfs` through `ns_dev_subgroups` and into `struct nilfs_root` through snapshot kobjects declared in `the_nilfs.h`. Dependencies are Linux sysfs, kobject, and completion infrastructure plus forward declarations supplied by NILFS headers.

## Integration Points
The declarations are tightly coupled to `sysfs.c` naming conventions: callback names must match `nilfs_<type>_<name>_show` and optional `_store`. The subgroup structure layout is also used by generated release functions through `container_of()`, so field names and macro arguments must remain synchronized.

## Risks
The macro layer reduces repetition but hides type relationships. A mismatched macro argument can generate code that compiles against the wrong field or callback signature. `NILFS_SEGMENTS_RW_ATTR` expands to `NILFS_RW_ATTR(segs_info, name)`, which is suspicious because the file defines `struct nilfs_segments_attr`, not `nilfs_segs_info_attr`; it is currently unused, but using it would likely break compilation.

## Test Signals
Compile coverage is the primary signal. Adding a temporary read/write attribute for each macro family, building with `W=1`, and checking generated sysfs mode bits verifies the header. Runtime tests should confirm every declared subgroup appears under `/sys/fs/nilfs2/<device>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.c

## Purpose
This file implements lifecycle, mount-time initialization, recovery setup, superblock selection, disk-layout validation, segment accounting helpers, discard handling, and mounted-checkpoint root management for the shared `struct the_nilfs` object.

## Important APIs, Types, And Functions
Externally used functions include `alloc_nilfs()`, `destroy_nilfs()`, `init_nilfs()`, `load_nilfs()`, `nilfs_set_last_segment()`, `nilfs_nrsvsegs()`, `nilfs_set_nsegments()`, `nilfs_discard_segments()`, `nilfs_count_free_blocks()`, `nilfs_near_disk_full()`, `nilfs_lookup_root()`, `nilfs_find_or_create_root()`, `nilfs_put_root()`, `nilfs_fall_back_super_block()`, and `nilfs_swap_super_block()`. Internal helpers validate superblocks with CRC32, load the super root and metadata files, parse block size, store disk layout, choose primary versus secondary superblock, and track recovery metadata.

## Control Flow
`alloc_nilfs()` allocates and initializes locks, lists, rb-tree roots, atomics, and defaults. `init_nilfs()` sets an initial block size, loads and validates superblocks, checks feature compatibility, adjusts the VFS block size if needed, stores layout fields, initializes the log cursor, and marks the object initialized. `load_nilfs()` searches for a super root, optionally rolls back to the spare superblock, loads DAT/CPFILE/SUFILE from the super root, creates sysfs state, and performs roll-forward recovery when the filesystem was not clean. Failure paths drop sysfs and metadata inodes in reverse order.

## State, Persistence, And Dependencies
The file mirrors persistent superblock and super-root contents into `struct the_nilfs`: block geometry, segment count, CRC seed, mount state, last partial segment, checkpoint number, and metadata inode pointers. It depends on NILFS recovery, segment, DAT, CPFILE, SUFILE, and segbuf helpers, Linux buffer-head I/O, block-device size/flush/discard APIs, rbtrees, spinlocks, rwsems, and refcounts.

## Integration Points
Mount code calls `init_nilfs()` and `load_nilfs()` before the filesystem is usable. Segment construction updates last-segment state through `nilfs_set_last_segment()`. Cleaner and allocator paths use reserved-segment and near-full helpers. Snapshot/current-root users use the rb-tree root lookup/create/put functions, which also integrate with sysfs snapshot groups.

## Risks
Superblock choice and fallback are high-risk because invalid CRCs, mismatched block sizes, or a bad secondary-superblock offset can decide whether recovery is possible. `nilfs_find_or_create_root()` inserts the new root into the rb-tree before creating its sysfs group; if sysfs creation fails, the function frees the object without erasing the rb-node, leaving a stale tree pointer. Discard batching assumes contiguous segment ranges are supplied in ascending order for optimal merging. Recovery temporarily clears read-only mount flags when it must write, so failures must always restore `sb->s_flags`.

## Test Signals
Signals include mounting images with valid, stale, corrupt, and missing primary/secondary superblocks; forced block-size changes; malformed layout fields; clean versus unclean mounts with `norecovery`; read-only block devices; injected failures in metadata-file loads and sysfs creation; discard tests with contiguous and discontiguous segment lists; and KASAN tests for checkpoint root creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.h

## Purpose
This header defines the shared NILFS2 filesystem state object `struct the_nilfs`, the mounted checkpoint/snapshot root object `struct nilfs_root`, state flags, mount option helpers, public lifecycle/function prototypes, and small inline helpers for superblock update policy, segment arithmetic, and block-device flushing.

## Important APIs, Types, And Functions
`enum THE_NILFS_*` flags describe initialization, discontinued log chain, GC activity, dirty superblock, and purge state. `struct the_nilfs` holds the backing block device, superblock buffers, log cursor, latest-segment state, metadata inodes, checkpoint rb-tree, dirty/GC inode lists, mount options, block geometry, CRC seed, and sysfs kobjects. `struct nilfs_root` tracks one mounted checkpoint with refcount, rb-node, ifile, counters, and sysfs snapshot kobject. Inlines include `nilfs_sb_need_update()`, `nilfs_sb_will_flip()`, segment range conversion helpers, `nilfs_shift_to_next_segment()`, `nilfs_last_cno()`, `nilfs_segment_is_active()`, and `nilfs_flush_device()`.

## Control Flow
This header mainly defines data and inline decision logic. Flag macros generate setters, clearers, and testers. Segment helpers are called during allocation, recovery, and segment construction. `nilfs_flush_device()` gates `blkdev_issue_flush()` on the BARRIER mount option and `ns_flushed_device`, sets the flushed flag with an ordering barrier, and normalizes non-EIO errors to success.

## State, Persistence, And Dependencies
Most fields either cache persistent on-disk data or track volatile mount/session state. `ns_sem` protects shared superblock state, `ns_segctor_sem` protects log-write cursor fields, `ns_last_segment_lock` protects latest committed segment fields, and `ns_cptree_lock` protects mounted checkpoint roots. The header depends on Linux block-device, fs, rbtree, buffer-head, refcount, and backing-device definitions.

## Integration Points
Almost every NILFS2 subsystem uses this header: mount/recovery, segment constructor, cleaner, metadata files, sysfs, inode handling, and checkpoint management. `sb->s_fs_info` points at `struct the_nilfs`, making it the cross-subsystem state anchor.

## Risks
The structure mixes persistent metadata, mutable runtime cursor state, and sysfs lifetime state, so lock discipline is critical. Helpers such as `nilfs_segment_is_active()` read cursor fields without locking and are safe only in contexts that already serialize segment state. `nilfs_flush_device()` intentionally suppresses non-EIO flush errors, which matches existing semantics but can hide device behavior from callers.

## Test Signals
Compile tests across NILFS2 are essential because this header affects many users. Runtime signals include KCSAN lock checking during segment construction and sysfs reads, checkpoint mount/unmount refcount tests, flush behavior with and without BARRIER, and boundary tests for segment-zero arithmetic and maximum segment counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/Kconfig -->
# sources/distributed-fs/ceph-client/fs/nls/Kconfig

## Purpose
This Kconfig file defines the kernel Native Language Support configuration menu. It enables the base NLS layer and exposes individual codepage/charset modules used by filesystems such as FAT, Joliet, HFS/HFS+, SMB/NCP, and related legacy filename encodings.

## Important APIs, Types, And Functions
The top-level `menuconfig NLS` is a tristate that builds `nls_base` when enabled. `NLS_DEFAULT` selects the default mount-time charset string. Individual `config NLS_CODEPAGE_*`, `NLS_ISO8859_*`, `NLS_KOI8_*`, `NLS_MAC_*`, `NLS_UTF8`, and hidden `NLS_UCS2_UTILS` symbols drive Makefile object inclusion.

## Control Flow
There is no runtime control flow. Configuration flow is conditional: all child options are visible only inside `if NLS`. User choices become `CONFIG_NLS_*` symbols consumed by the NLS Makefile and by filesystem code that requests charset tables.

## State, Persistence, And Dependencies
The persistent state is the generated kernel `.config`. Many entries are tristate so encodings can be built in, built as loadable modules, or disabled. The help text documents intended filesystem usage and the valid strings for `NLS_DEFAULT`.

## Integration Points
`fs/nls/Makefile` maps these symbols to object files. Filesystems use NLS by calling the core NLS lookup/register APIs and by accepting mount options such as `iocharset=` or defaults from `CONFIG_NLS_DEFAULT`.

## Risks
The default string is free-form and can name a charset that was not built; the help text says the kernel falls back to a built-in iso8859-1-compatible table. Some help text is historical and broad, so distro configs may enable many rarely-used modules. Adding a new charset requires keeping Kconfig, Makefile, module name, and userspace mount strings consistent.

## Test Signals
Useful checks are `olddefconfig/menuconfig` visibility, build matrices for built-in and module NLS options, module autoload by charset name, and filesystem mount tests using explicit and default charset options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/Makefile -->
# sources/distributed-fs/ceph-client/fs/nls/Makefile

## Purpose
This Makefile maps `CONFIG_NLS*` Kconfig symbols to the native language support object files compiled into the kernel or as modules.

## Important APIs, Types, And Functions
The build API is the kernel `obj-$(CONFIG_SYMBOL) += object.o` pattern. `CONFIG_NLS` builds `nls_base.o`. Codepage, ISO-8859, KOI8, UTF-8, Mac, and UCS2 utility symbols each add their corresponding table implementation. Some symbols build multiple objects, such as CP932 adding both `nls_cp932.o` and `nls_euc-jp.o`, and KOI8-U adding `nls_koi8-u.o` and `nls_koi8-ru.o`.

## Control Flow
There is no runtime control flow. Kbuild expands selected symbols into object lists. If a symbol is `m`, the object becomes a module; if `y`, it is linked built-in.

## State, Persistence, And Dependencies
State comes from the generated kernel configuration. The Makefile assumes each listed `.o` has a matching source file in `fs/nls` and that Kconfig exposes or selects the symbol.

## Integration Points
This file is the bridge between `fs/nls/Kconfig` and concrete charset modules such as `mac-celtic.o`, `mac-centeuro.o`, `mac-croatian.o`, `mac-cyrillic.o`, and `mac-gaelic.o`. Filesystem runtime charset lookup depends on the selected objects registering their `struct nls_table`.

## Risks
Symbol/object drift causes build failures or missing charset modules. The entries use a mix of tabs and spaces around `+=`, which is harmless for make but can make style checks noisy. Multi-object mappings must remain intentional because disabling one symbol can remove more than one charset table.

## Test Signals
Build all NLS symbols as modules and built-ins, run `make M=fs/nls`, verify expected `.ko` names, and mount a filesystem with each configured charset string to confirm lookup registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-celtic.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-celtic.c

## Purpose
This generated NLS module registers the `macceltic` single-byte Macintosh Celtic codepage. It translates bytes to Unicode and exact Unicode code points back to bytes for legacy Mac/HFS filenames.

## Important APIs, Types, And Functions
The key data are `charset2uni[256]`, sparse reverse pages `page00`, `page01`, `page03`, `page1e`, `page20`, `page21`, `page22`, `page25`, `page26`, `page_uni2charset[256]`, and placeholder `charset2lower`/`charset2upper` tables. `uni2char()` validates output space and looks up the high-byte page plus low-byte index. `char2uni()` maps one input byte through `charset2uni`. `struct nls_table table` names the charset `macceltic`; module init/exit call `register_nls()` and `unregister_nls()`.

## Control Flow
Loading the module registers the table with the NLS core. Filesystems call `uni2char` or `char2uni` through that table. Conversion is single-byte and returns `1` on success, `-ENAMETOOLONG` for no output space, and `-EINVAL` for unmapped code points or byte zero.

## State, Persistence, And Dependencies
All mapping state is read-only static data generated from Unicode mapping files. There is no persistent runtime state. Dependencies are `linux/nls.h`, module infrastructure, and errno values.

## Integration Points
`CONFIG_NLS_MAC_CELTIC` in Kconfig and `mac-celtic.o` in the NLS Makefile control availability. HFS-family and other NLS consumers can request `macceltic` by name.

## Risks
The mapping is exact-only, so Unicode normalization or visually equivalent composed/decomposed forms are not handled. Byte `0x00` maps to Unicode NUL but `char2uni()` treats resulting zero as invalid, which is consistent with pathname expectations. Case maps are sentinel-filled, so callers should not expect meaningful case folding from this table.

## Test Signals
Tests should round-trip every nonzero byte with a reverse mapping, verify selected Celtic/Welsh code points including Euro and W/Y diacritics, exercise unmapped Unicode returning `-EINVAL`, and load/unload the module repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-celtic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-centeuro.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-centeuro.c

## Purpose
This generated NLS module registers the `maccenteuro` Macintosh Central European codepage. It supports exact filename translation between the legacy single-byte Mac encoding and Unicode.

## Important APIs, Types, And Functions
The module defines `charset2uni[256]`, reverse lookup pages `page00`, `page01`, `page02`, `page20`, `page21`, `page22`, and `page25`, plus `page_uni2charset[256]`. Conversion callbacks `uni2char()` and `char2uni()` are installed in a `struct nls_table` with `.charset = "maccenteuro"`. Init and exit handlers register and unregister the table.

## Control Flow
The NLS core calls into the callbacks after a filesystem resolves the charset by name. `uni2char()` splits the Unicode value into high and low bytes, selects a reverse page, and emits one byte if the entry is nonzero. `char2uni()` indexes the direct byte table and returns one consumed byte unless the result is zero.

## State, Persistence, And Dependencies
The file is almost entirely static mapping tables generated from Unicode data. It has no mutable state beyond the registration lifetime managed by the module loader. It depends on the kernel module and NLS APIs.

## Integration Points
Availability is controlled by `CONFIG_NLS_MAC_CENTEURO` and the `mac-centeuro.o` Makefile entry. It is intended for Apple HFS-family filenames using Central European Mac encodings.

## Risks
Exact mapping means no fallback transliteration and no Unicode normalization. Some Unicode characters have no byte representation and return `-EINVAL`. The case conversion arrays are filled with sentinel values rather than useful lower/upper mappings, so case-insensitive filesystem code must not infer locale-aware folding from them.

## Test Signals
Round-trip tests across all mapped bytes, checks for Central European letters in Unicode pages `0x01` and `0x02`, module registration by the string `maccenteuro`, and negative tests for unmapped characters provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-centeuro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-croatian.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-croatian.c

## Purpose
This generated NLS module registers the `maccroatian` Macintosh Croatian codepage for single-byte legacy filename conversion.

## Important APIs, Types, And Functions
The module provides `charset2uni[256]`, reverse pages `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`, and a sparse `page_uni2charset` index. The `pagef8` entry handles the private-use Unicode point used by this mapping. `uni2char()`, `char2uni()`, and `struct nls_table table` follow the standard NLS table pattern with charset name `maccroatian`.

## Control Flow
Module initialization registers the table. Runtime conversion is one byte at a time. Unicode-to-byte conversion fails when the high-byte page is absent or the page entry is zero; byte-to-Unicode conversion fails only when the direct table yields zero.

## State, Persistence, And Dependencies
All conversion data are immutable static tables generated from Unicode source data. The only runtime state is whether the table is registered. The file depends on `linux/nls.h`, module infrastructure, and `errno.h`.

## Integration Points
`CONFIG_NLS_MAC_CROATIAN` and `mac-croatian.o` expose this module to kernel builds. Filesystems that store HFS-style Croatian Mac filenames can request the `maccroatian` NLS table.

## Risks
The private-use mapping requires exact agreement with userspace tools; substituting a different mapping table could break round trips. Like the sibling Mac tables, this file does not implement normalization or meaningful case maps. Generated table edits are easy to get wrong by hand.

## Test Signals
Round-trip every mapped byte, explicitly test Croatian letters and the private-use `0xf8ff` mapping, verify unmapped Unicode failure, and confirm module lookup by `maccroatian`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-croatian.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-cyrillic.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-cyrillic.c

## Purpose
This generated NLS module registers the `maccyrillic` Macintosh Cyrillic codepage, translating legacy Mac Cyrillic filename bytes to and from Unicode.

## Important APIs, Types, And Functions
The direct table `charset2uni[256]` contains ASCII, symbols, Cyrillic code points, Numero sign, Euro, and related characters. Reverse lookup uses `page00`, `page01`, `page04`, `page20`, `page21`, and `page22` through `page_uni2charset[256]`; page `0x04` is the main Cyrillic block. `uni2char()` and `char2uni()` are registered in `struct nls_table table` with `.charset = "maccyrillic"`.

## Control Flow
Loading calls `register_nls(&table)`, and unloading calls `unregister_nls(&table)`. Conversion callbacks use constant-time table indexing for single-byte characters and return kernel errno values for insufficient space or unmapped input.

## State, Persistence, And Dependencies
Mapping state is static and read-only. There is no persistence beyond module registration. Dependencies are the kernel NLS core and module loader.

## Integration Points
The Kconfig symbol `NLS_MAC_CYRILLIC` and Makefile object `mac-cyrillic.o` control inclusion. Consumers request the table by the name `maccyrillic`, commonly for HFS-family legacy filenames.

## Risks
Cyrillic codepage compatibility depends on exact historical mappings, including Ukrainian/Serbian/Macedonian extensions and symbol entries. The table does not normalize Unicode or provide transliteration. Placeholder case maps mean case-insensitive comparisons require separate logic.

## Test Signals
Test round trips for the full Cyrillic alphabet range, selected extended Cyrillic code points, Euro and Numero sign, all mapped nonzero bytes, `-EINVAL` on unmapped Unicode, and module load/unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-cyrillic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-gaelic.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-gaelic.c

## Purpose
This generated NLS module registers the `macgaelic` Macintosh Gaelic codepage. It provides exact one-byte conversion for legacy Gaelic Mac filename encodings.

## Important APIs, Types, And Functions
`charset2uni[256]` maps each byte to Unicode, including Gaelic-specific Latin extended letters and symbols. Reverse lookup pages include `page00`, `page01`, `page02`, `page1e`, `page20`, `page21`, `page22`, and `page26`, selected by `page_uni2charset[256]`. `uni2char()`, `char2uni()`, and the `struct nls_table` named `macgaelic` implement the NLS interface.

## Control Flow
The module init function registers the table; exit unregisters it. At runtime, Unicode-to-byte conversion splits a `wchar_t` into page and offset, then emits one byte if an exact reverse mapping exists. Byte-to-Unicode conversion directly indexes `charset2uni`.

## State, Persistence, And Dependencies
The conversion tables are read-only generated data. Runtime state is limited to registration in the NLS core. The file depends on module infrastructure, `linux/nls.h`, and errno definitions.

## Integration Points
`CONFIG_NLS_MAC_GAELIC` and `mac-gaelic.o` connect the module to kernel builds. Filesystems request the table by `macgaelic` when decoding or encoding legacy Mac Gaelic filenames.

## Risks
Exact-only mappings reject decomposed Unicode and unrelated but visually similar characters. Gaelic-specific extended Latin coverage must stay synchronized with the Unicode source table. Case maps are placeholders, so locale-aware case folding is outside this module.

## Test Signals
Round-trip mapped bytes, test Gaelic extended letters in pages `0x01` and `0x1e`, validate symbol mappings such as Euro, check unmapped Unicode failure, and verify module registration under `macgaelic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-gaelic.c -->
