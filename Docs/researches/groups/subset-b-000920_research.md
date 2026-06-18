# Research: subset-b-000920

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie-asm.h

## Purpose
This generated Xtensa variant header provides assembler save and restore macros for optional non-coprocessor state and configured TIE coprocessor state on the `test_kc705_hifi` core. It is not meant for direct inclusion; it feeds lower-level Xtensa HAL and kernel context-switch assembly that needs exact save-area layout knowledge.

## Important APIs, types, and macros
The public surface is assembler macros and constants rather than C types. `XTHAL_SAS_*` bitmasks classify save-area entries by option/TIE source, compiler use, and ABI lifetime. `XTHAL_SAS3()` composes those selectors. `xchal_ncp_store` and `xchal_ncp_load` save and restore non-coprocessor optional state: `THREADPTR`, MAC16 `ACCLO`/`ACCHI`, `M0` through `M3`, `BR`, and `SCOMPARE1`. `xchal_cp1_store` and `xchal_cp1_load`, aliased as `xchal_cp_AudioEngineLX_store/load`, handle AudioEngineLX coprocessor state. Empty `xchal_cpN_store/load` macros are emitted for unconfigured coprocessor IDs. `XCHAL_NCP_NUM_ATMPS`, `XCHAL_CP1_NUM_ATMPS`, and `XCHAL_SA_NUM_ATMPS` document scratch-register needs.

## Control flow
Each save/load macro begins with `xchal_sa_start`, aligns the caller-provided save-area pointer via `xchal_sa_align`, conditionally emits stores or loads according to `select`, and optionally advances offsets for allocated-but-not-selected categories via `alloc`. The NCP flow writes compact 4-byte special/user registers. The CP1 flow saves six AudioEngineLX user registers, sixteen `aed` 64-bit registers, and four alignment registers, using pointer bumps after 64-byte groups.

## State and persistence behavior
The file defines volatile CPU execution state layout for context save areas. It does not persist state by itself; persistence is the caller-provided memory block. Layout must match `tie.h` sizes: NCP state is 36 bytes, CP1 state is 184 bytes, and the total aligned state is 240 bytes. The macros intentionally exclude zero-overhead loop registers.

## Dependencies and integration points
The macros depend on Xtensa assembler support for `rur.*`, `wur.*`, `rsr.*`, `wsr.*`, `AE_S64.I`, `AE_L64.I`, `AE_SALIGN64.I`, `AE_LALIGN64.I`, and HAL helper macros such as `xchal_sa_start` and `xchal_sa_align`. They integrate with Xtensa kernel context switch, signal frame, exception, and coprocessor enable paths that include generated variant headers.

## Risks
The highest risk is layout drift between this assembler header and C metadata in `tie.h`; a mismatch corrupts task or interrupt context. The macros clobber the pointer and first scratch register, so callers must satisfy the contract. The CP1 macro updates `.Lxchal_pofs_` and `.Lxchal_ofs_` in a non-obvious way after pointer increments; assembler helper bugs or manual changes can silently break save-area offsets.

## Test signals
Useful signals are Xtensa allmodconfig or defconfig builds for the variant, assembler compilation of context-switch files that expand these macros, runtime context-switch tests while using AudioEngineLX registers, and ABI checks comparing save-area sizes and offsets against `XCHAL_*_SA_LIST` in `tie.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie.h

## Purpose
This generated Xtensa HAL header describes the TIE and coprocessor configuration for the `test_kc705_hifi` variant. C and assembly consumers use it to size save areas, enumerate optional registers, identify coprocessors, and decode instruction lengths for this Xtensa core.

## Important APIs, types, and macros
The header defines coprocessor topology with `XCHAL_CP_NUM`, `XCHAL_CP_MAX`, `XCHAL_CP_MASK`, and `XCHAL_CP_PORT_MASK`. CP1 is `AudioEngineLX` with 184 bytes of save area and 8-byte alignment; CP7 is `XTIOP` with no saved state but a port-coprocessor identity. `XCHAL_NCP_SA_SIZE` is 36 bytes and `XCHAL_TOTAL_SA_SIZE` is 240 bytes. `XCHAL_NCP_SA_LIST(s)` enumerates `threadptr`, `acclo`, `acchi`, `m0` through `m3`, `br`, and `scompare1`. `XCHAL_CP1_SA_LIST(s)` enumerates AudioEngineLX user registers and register files: `ae_ovf_sar`, `ae_bithead`, `ae_ts_fts_bu_bp`, `ae_cw_sd_no`, `ae_cbegin0`, `ae_cend0`, `aed0` through `aed15`, and `u0` through `u3`. Instruction decoding tables are exposed through `XCHAL_OP0_FORMAT_LENGTHS` and `XCHAL_BYTE0_FORMAT_LENGTHS`.

## Control flow
There is no executable control flow. Consumers define `XCHAL_SA_REG` and expand the list macros to generate save routines, debuggers, offset tables, or diagnostics. The order of list entries defines the logical save-area ordering that the assembler file must honor.

## State and persistence behavior
This file is a declarative contract for CPU state. It encodes which registers must be carried across task switches or inspected by tooling and how much memory to reserve. It does not allocate or mutate memory.

## Dependencies and integration points
The header is coupled to `tie-asm.h`, Xtensa HAL include paths, low-level context save/restore code, and debugging tools that understand Xtensa target register numbers. Kernel arch code may use the CP masks to decide whether `CPENABLE` and lazy coprocessor handling are required.

## Risks
Because this is generated hardware metadata, manual edits risk breaking ABI-level assumptions. Inconsistency with assembler macros can cause truncated or misaligned state saves. CP7 has an identity but zero save area, so code must treat the CP mask and save-area list as separate concepts.

## Test signals
Build-time expansion of `XCHAL_SA_REG` users, comparison against generated assembler offsets, Xtensa boot tests with coprocessor state enabled, and debugger/register-list validation are the primary signals. A focused invariant check can verify that NCP plus CP save sizes align to `XCHAL_TOTAL_SA_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/core.h

## Purpose
This generated Xtensa core-configuration header describes the base ISA, cache, interrupt, exception, debug, and MMU capabilities of the `test_mmuhifi_c3` core. It is a compile-time hardware contract for privileged and non-privileged Xtensa code.

## Important APIs, types, and macros
The header is macro-only. ISA capability flags include windowed registers, density instructions, loops, NSA, min/max, CLAMPS, MUL16, MUL32, S32C1I, release sync, thread pointer, booleans, coprocessor support, and HiFi2 Audio Engine. It describes core geometry through `XCHAL_NUM_AREGS`, instruction size, fetch and data width, write-buffer entries, endian setting, and unaligned access exception behavior. Privileged sections define cache sizes and associativity, interrupt counts and masks, timer interrupt numbers, external interrupt mappings, exception vector virtual and physical addresses, debug level, and MMU properties such as TLB presence, PTP MMU support, ASID bits, and rings.

## Control flow
There is no runtime flow. Conditional compilation is provided by `XTENSA_HAL_NON_PRIVILEGED_ONLY`: privileged cache, interrupt, vector, debug, and MMU details are hidden when non-privileged consumers include the header.

## State and persistence behavior
The file does not store runtime state. It fixes architectural constants that determine kernel memory layout, exception vector placement, cache maintenance behavior, interrupt handling tables, and MMU setup for this variant.

## Dependencies and integration points
The macros integrate with Xtensa arch initialization, cache/TLB code, interrupt controller setup, exception vector assembly, scheduler context management, and HAL code. Several values reference external symbolic constants such as `XTHAL_INTTYPE_*` and `XTHAL_TIMER_UNCONFIGURED`, expected from broader Xtensa HAL headers.

## Risks
Misstated MMU, cache, or vector constants can prevent boot or cause memory corruption. This variant has unaligned load/store exceptions and no hardware unaligned support, so generic code must not assume cheap unaligned access. It has coherent write-back caches and an MMU, which makes cache/TLB maintenance and vector address correctness critical.

## Test signals
Signals include Xtensa kernel builds for `test_mmuhifi_c3`, early boot through exception vector installation, timer interrupt delivery on interrupts 6 and 8, TLB autorefill/page-table tests, cache line size assertions, and runtime tests that exercise S32C1I, thread pointer, boolean registers, and HiFi2 coprocessor state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie-asm.h

## Purpose
This generated assembler header supplies save and restore macros for non-coprocessor optional state and the AudioEngineLX coprocessor on the `test_mmuhifi_c3` Xtensa variant.

## Important APIs, types, and macros
`XTHAL_SAS_*` selector constants classify saved state. `xchal_ncp_store` and `xchal_ncp_load` handle optional non-coprocessor registers `BR`, `SCOMPARE1`, and `THREADPTR`. `xchal_cp1_store` and `xchal_cp1_load`, aliased through `xchal_cp_AudioEngineLX_store/load`, save and restore the HiFi2 AudioEngineLX state: user registers `AE_OVF_SAR`, `AE_BITHEAD`, `AE_TS_FTS_BU_BP`, `AE_SD_NO`, eight `aep` 48-bit registers, and four `aeq` 56-bit registers. Empty macros are provided for unconfigured coprocessor IDs 0 and 2 through 7.

## Control flow
The NCP macros start a save-area sequence, align to 4-byte boundaries, then conditionally store or load each selected optional register. The CP1 macros align the pointer to 8 bytes, store fixed user registers at offsets 0 through 12, store `aep0` through `aep7` in two groups, then store `aeq0` through `aeq3`; load reverses by loading `aeq` after an 80-byte pointer bump and then loading `aep` with negative offsets. Selection is controlled by assembler `.ifeq` expressions over `select`.

## State and persistence behavior
The file defines how task or exception code serializes volatile core and coprocessor registers into a caller-owned save area. The NCP layout is 12 bytes and the CP1 layout is 112 bytes, matching `tie.h`; total alignment padding brings combined save area to 128 bytes.

## Dependencies and integration points
The macros depend on Xtensa assembler opcodes such as `rur240`, `wur240`, `AE_SP24X2S.I`, `AE_SQ56S.I`, `AE_LP24X2.I`, and `AE_LQ56.I`, plus HAL helpers `xchal_sa_start` and `xchal_sa_align`. They integrate with Xtensa low-level context management and any lazy coprocessor switching logic for CP1.

## Risks
Pointer arithmetic in CP1 load/store is asymmetric but layout-compatible; changing offsets without checking `tie.h` can break restore. The save-area pointer contract says 8-byte alignment for CP1, and violations can fault or corrupt state on this core. `select` lacks the newer `alloc` parameter present in other generated variants, so callers must match this HAL generation.

## Test signals
Build the Xtensa assembly that expands these macros, run context-switch tests while executing HiFi2 instructions, compare CP1 save size against `XCHAL_CP1_SA_SIZE`, and validate that disabled CP macros assemble as no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie.h

## Purpose
This generated Xtensa TIE metadata header describes the coprocessor and save-area layout for the `test_mmuhifi_c3` HiFi2 variant.

## Important APIs, types, and macros
The core has one coprocessor, CP1 `AudioEngineLX`, exposed through `XCHAL_CP_NUM`, `XCHAL_CP_MAX`, `XCHAL_CP_MASK`, `XCHAL_CP1_NAME`, `XCHAL_CP1_IDENT`, and `XCHAL_CP_ID_AUDIOENGINELX`. `XCHAL_CP1_SA_SIZE` is 112 bytes with 8-byte alignment. Non-coprocessor optional state is 12 bytes and consists of `br`, `scompare1`, and `threadptr` in `XCHAL_NCP_SA_LIST`. `XCHAL_CP1_SA_LIST` enumerates four AudioEngineLX user registers, eight `aep` registers, and four `aeq` registers. `XCHAL_TOTAL_SA_SIZE` is 128 bytes. `XCHAL_OP0_FORMAT_LENGTHS` describes FLIX instruction lengths.

## Control flow
The file has no execution flow. The main pattern is macro expansion: clients define `XCHAL_SA_REG` and invoke the save-area list macros to emit code, tables, or metadata.

## State and persistence behavior
The state described here is per-thread CPU and coprocessor state that must be preserved by architecture code. The header itself is static metadata and does not allocate memory or perform persistence.

## Dependencies and integration points
It must match `tie-asm.h` exactly. It is consumed by Xtensa HAL, kernel context switch paths, debugger register enumeration, and code that sizes kernel task save areas for optional and TIE state.

## Risks
The most important risk is save-area mismatch with the assembler macro offsets. The header records `ae_ovf_sar` as 7 significant bits and `ae_sd_no` as 28 bits; generic tooling must honor the significant-bit metadata rather than assuming full 32-bit logical values. This variant has no port coprocessor mask.

## Test signals
Compile-time checks that list counts and sizes match generated assembly, context-switch tests under HiFi2 workloads, and debugger register-read validation are useful. A small macro-expansion test can verify that all `XCHAL_CPn_SA_LIST` empty cases remain syntactically valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/Kconfig -->
# sources/distributed-fs/ceph-client/block/Kconfig

## Purpose
This Kconfig file defines the Linux block layer configuration menu for this source tree. It controls whether the block layer is built and gates optional features such as block integrity, zoned devices, cgroup controllers, writeback throttling, debugfs, Opal SED support, and inline encryption.

## Important APIs, types, and symbols
`menuconfig BLOCK` is the root switch, defaulting to enabled and selecting `FS_IOMAP` and `SBITMAP`. Feature symbols include `BLOCK_LEGACY_AUTOLOAD`, `BLK_DEV_BSGLIB`, `BLK_DEV_INTEGRITY`, `BLK_DEV_WRITE_MOUNTED`, `BLK_DEV_ZONED`, `BLK_DEV_THROTTLING`, `BLK_WBT`, `BLK_WBT_MQ`, `BLK_CGROUP_IOLATENCY`, `BLK_CGROUP_FC_APPID`, `BLK_CGROUP_IOCOST`, `BLK_CGROUP_IOPRIO`, `BLK_DEBUG_FS`, `BLK_SED_OPAL`, `BLK_INLINE_ENCRYPTION`, `BLK_INLINE_ENCRYPTION_FALLBACK`, `BLK_PM`, `BLOCK_HOLDER_DEPRECATED`, and `BLK_MQ_STACKING`.

## Control flow
Kconfig control is declarative. All nested options are visible only under `if BLOCK`. Several options select lower-level dependencies, for example integrity selects CRC libraries, throttling selects `BLK_CGROUP_RWSTAT`, IOCOST selects request allocation timestamps, and inline encryption fallback selects crypto primitives. The file also includes `block/partitions/Kconfig` and `block/Kconfig.iosched`.

## State and persistence behavior
The persistent output is the kernel `.config`; selected symbols drive compiled code and default runtime behavior. `BLK_DEV_WRITE_MOUNTED` is particularly visible at runtime because `bdev.c` initializes `bdev_allow_write_mounted` from it while still allowing a boot parameter override.

## Dependencies and integration points
The symbols map directly to `block/Makefile` object inclusion and to conditional code throughout the block layer. They also expose user-facing policy choices through help text and cgroup/debugfs interfaces.

## Risks
Disabling `BLOCK` removes block device usability and dependent storage subsystems. Enabling experimental or policy-heavy controllers changes IO behavior. `BLK_DEV_WRITE_MOUNTED=n` improves protection but can break tools that expect to write mounted read-only block devices. Dependency errors here produce missing objects or unused code paths.

## Test signals
Run Kconfig parsing, build `allnoconfig`, `defconfig`, and configurations toggling each option. Boot smoke tests should verify block device nodes, cgroup IO files, inline encryption fallback, debugfs entries, and mounted-device write policy under both config and boot-parameter settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/Makefile -->
# sources/distributed-fs/ceph-client/block/Makefile

## Purpose
This Makefile defines which block-layer objects are built into the kernel or optional modules. It is the build-side counterpart to `block/Kconfig`.

## Important APIs, types, and targets
`obj-y` lists mandatory block core objects including `bdev.o`, `bio.o`, `blk-core.o`, multi-queue files, partition support, request QoS, disk events, and `badblocks.o`. Conditional `obj-$(CONFIG_*)` lines include BSG, block cgroup controllers, IO schedulers, integrity, zoned support, writeback throttling, debugfs, Opal, power management, inline encryption, and deprecated holder support. `bfq-y` composes the BFQ scheduler from `bfq-iosched.o`, `bfq-wf2q.o`, and `bfq-cgroup.o`.

## Control flow
Kbuild evaluates config symbols and appends matching objects. If `CONFIG_IOSCHED_BFQ` is enabled, the composite `bfq.o` is linked from the `bfq-y` list. Objects in `obj-y` are always included when the block directory is built.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the object graph baked into the kernel build output.

## Dependencies and integration points
It depends on Kconfig symbols from `block/Kconfig` and scheduler Kconfig files. It integrates with top-level kernel Kbuild and with C files that expect symbols to be available only when their configuration is enabled.

## Risks
Object omissions cause link failures or missing runtime features. Adding an object to `obj-y` rather than a guarded `obj-$(CONFIG_*)` can force unwanted code into all block builds. Composite object ordering matters for BFQ because `bfq-cgroup.o` supplies hooks referenced by the main scheduler.

## Test signals
Build matrix coverage with BFQ, cgroups, inline encryption, integrity, zoned block devices, and debugfs toggled on and off is the key signal. Link-time undefined symbol checks are especially useful for conditional combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/badblocks.c -->
# sources/distributed-fs/ceph-client/block/badblocks.c

## Purpose
`badblocks.c` implements a compact in-kernel bad-sector range table for block devices and related subsystems. It tracks acknowledged and unacknowledged bad ranges, supports querying, adding, clearing, acknowledging, and sysfs text import/export.

## Important APIs, types, and functions
The exported API is `badblocks_check`, `badblocks_set`, `badblocks_clear`, `ack_all_badblocks`, `badblocks_show`, `badblocks_store`, `badblocks_init`, `devm_init_badblocks`, and `badblocks_exit`. Internal helpers operate on packed 64-bit table entries through macros from `linux/badblocks.h`: start offset, length, and ACK bit are encoded in one word. Important helpers include `prev_badblocks`, `can_merge_front`, `front_merge`, `can_combine_front`, `front_combine`, `overlap_front`, `overlap_behind`, `can_front_overwrite`, `front_overwrite`, `insert_at`, `try_adjacent_combine`, `_badblocks_set`, `_badblocks_clear`, and `_badblocks_check`.

## Control flow
`badblocks_set` delegates to `_badblocks_set`, which validates enablement and length, rounds by `bb->shift`, takes the seqlock for writing, then iterates from the requested start to end. Each loop uses `prev_badblocks` with a hint to find the prior range, then chooses among insertion before all ranges, front combination, same-ack merge, acknowledged overwrite of unacknowledged ranges, overlap skipping, or insertion before the next range. Large operations are deliberately split into smaller pieces to handle maximum range length and table-full cases.

`badblocks_clear` delegates to `_badblocks_clear`, rounds conservatively, then walks the range. It treats clearing non-bad sectors as success, removes whole entries, shrinks entries from front or tail, and splits an entry only when table space permits. `badblocks_check` reads under a seqlock retry loop and returns `0` for no bad blocks, `1` for only acknowledged bad blocks, and `-1` if any unacknowledged bad block overlaps. `ack_all_badblocks` marks all entries acknowledged only when `changed` is clear, then merges adjacent compatible ranges.

## State and persistence behavior
`struct badblocks` owns a single page table, a count, a shift, a seqlock, and flags such as `changed` and `unacked_exist`. The in-memory table is sorted by sector range. Persistence is external: users such as MD or device drivers must store metadata and use `ack_all_badblocks` after metadata catches up. `badblocks_show` and `badblocks_store` provide sysfs-facing text serialization and insertion.

## Dependencies and integration points
The implementation depends on `linux/badblocks.h`, seqlocks, kernel allocation, device-managed allocation, and block-sector types. It is compiled unconditionally by the block Makefile and exported GPL symbols are available to block drivers and MD-like components that need bad-sector accounting.

## Risks
The packed entry format has a hard `MAX_BADBLOCKS` page-sized table and `BB_MAX_LEN` range length; very fragmented media can exhaust space. Partial progress in `_badblocks_set` can return failure when the original range is not fully represented. Overwrite semantics only allow acknowledged ranges to replace unacknowledged ones, so caller intent must be clear. Rounding via `bb->shift` differs for set and clear to avoid false negatives, which can surprise callers expecting exact sector removal. The code uses memmove-heavy table updates under a write seqlock, so large fragmented operations can hold interrupts disabled.

## Test signals
Strong tests include range insertion permutations, adjacent merges, ack/unack overwrite behavior, table-full cases, split-on-clear, shift rounding, sysfs parse failures, seqlock retry under concurrent readers, and `ack_all_badblocks` behavior when `changed` is set or clear. Build/link tests should also verify all exported symbols under module consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/badblocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bdev.c -->
# sources/distributed-fs/ceph-client/block/bdev.c

## Purpose
`bdev.c` implements the VFS-facing block-device object model: internal block-device inodes, pseudo-filesystem setup, open and close paths, exclusive claims, block-size management, cache invalidation, freeze/thaw hooks, device lookup, write-access policy, and statx reporting.

## Important APIs, types, and functions
The central private type is `struct bdev_inode`, which embeds `struct block_device` with its VFS inode. Conversion helpers include `BDEV_I`, `BD_INODE`, exported `I_BDEV`, and exported `file_bdev`. Public functions include `invalidate_bdev`, `truncate_bdev_range`, `bdev_validate_blocksize`, `set_blocksize`, `sb_set_blocksize`, `sb_min_blocksize`, `sync_blockdev_nowait`, `sync_blockdev`, `sync_blockdev_range`, `bdev_freeze`, `bdev_thaw`, `bdev_cache_init`, `bdev_alloc`, `bdev_set_nr_sectors`, `bdev_add`, `bdev_unhash`, `bdev_drop`, `bd_prepare_to_claim`, `bd_abort_claiming`, `bdev_permission`, `blkdev_get_no_open`, `blkdev_put_no_open`, `bdev_open`, `bdev_file_open_by_dev`, `bdev_file_open_by_path`, `bdev_release`, `bdev_fput`, `lookup_bdev`, `bdev_mark_dead`, `sync_bdevs`, `bdev_statx`, `disk_live`, and `block_size`.

## Control flow
Initialization starts in `bdev_cache_init`, creating a slab cache, registering the `bdev` pseudo-fs, mounting it, and storing `blockdev_superblock`. `bdev_alloc` creates an inode, initializes locks and mappings, attaches the request queue and disk, allocates per-CPU stats, and returns the embedded `block_device`. `bdev_add` assigns the `dev_t`, inode number, and hash entry.

Open flow begins with permission checks, no-open lookup by `dev_t`, pseudo-file allocation, and `bdev_open`. `bdev_open` optionally prepares an exclusive claim, blocks disk events, serializes on `disk->open_mutex`, verifies disk liveness and module ownership, enforces mounted-write restrictions, opens whole disks or partitions, claims write access, finalizes exclusive holder state, sets file flags/mapping/private data, and unblocks events. Error paths release claims, modules, mutexes, and event blocks.

Release flow in `bdev_release` syncs early if it appears to be the last opener, yields write access, ends claims, flushes media-change events, decrements whole or partition openers, releases the module, and drops the no-open device reference. `bdev_fput` proactively yields claims before deferred `fput`. Freeze/thaw paths count nested freezes and either call holder operations or sync the blockdev.

## State and persistence behavior
Persistent kernel state includes hashed block-device inodes, open counts, holder and claiming fields, write counters, freeze counts, block size bits, mapping folio order, sector count, device stats, and superblock-wide inode lists. Dirty data persists through the block-device mapping until explicit sync, invalidation, or final close flushes it. The global `bdev_allow_write_mounted` starts from `CONFIG_BLK_DEV_WRITE_MOUNTED` and can be overridden by the `bdev_allow_write_mounted=` boot parameter.

## Dependencies and integration points
This file sits between VFS, block core, gendisk drivers, device cgroups, security hooks, writeback, buffer heads, partitions, mount/pseudo-fs code, and statx. Holder operations allow filesystems or volume managers to freeze, thaw, mark dead, and coordinate exclusive ownership. Disk event blocking integrates with media-change polling and exclusive write holders.

## Risks
Open/close ordering is delicate: missing cleanup on any error path leaks claims, module refs, event blocks, or device refs. Write restriction depends on `bd_writers` sign conventions and correct pairing in yield paths. Block-size changes must flush and invalidate before changing folio minimum order; races here can corrupt page-cache assumptions. Exclusive claim behavior spans whole disks and partitions, so holder identity and `bd_claiming` wakeups are high-risk. `bdev_mark_dead` may call into holder ops with lock handoff assumptions.

## Test signals
Signals include block-device open/close stress, exclusive claim nesting and contention, whole-disk versus partition opens, module removal races, mounted-block-device write policy tests with both config and boot parameter, block-size change tests around page-cache folios, freeze/thaw nesting, hot unplug/media-change tests, `lookup_bdev` namespace checks, and statx direct-IO/atomic-write field validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bfq-cgroup.c -->
# sources/distributed-fs/ceph-client/block/bfq-cgroup.c

## Purpose
`bfq-cgroup.c` implements blk-cgroup integration for the BFQ I/O scheduler. It maps bios and BFQ queues to cgroups, manages BFQ group lifecycle and hierarchy, exposes cgroup weight controls and statistics, and handles queue migration when tasks move between cgroups.

## Important APIs, types, and functions
When `CONFIG_BFQ_CGROUP_DEBUG` is enabled, `struct bfq_stat` helpers wrap percpu counters and auxiliary counters for recursive stats. Group stat functions update queued IO, wait time, service time, merged IO, idle time, empty time, average queue size, dequeue count, bytes, and IO counts. Under `CONFIG_BFQ_GROUP_IOSCHED`, key helpers include `pd_to_bfqg`, `bfqg_to_blkg`, `blkg_to_bfqg`, `bfqg_parent`, `bfqq_group`, `bfqg_and_blkg_get/put`, `bfq_init_entity`, `bfq_pd_alloc/init/free/offline/reset_stats`, `bfq_link_bfqg`, `bfq_bio_bfqg`, `bfq_bfqq_move`, `bfq_bic_update_cgroup`, `bfq_end_wr_async`, cgroup weight show/write handlers, and `bfq_create_group_hierarchy`. `blkcg_policy_bfq`, `bfq_blkcg_legacy_files`, and `bfq_blkg_files` register the policy and cgroup files.

## Control flow
Policy activation allocates per-cgroup policy data with default weights, then allocates per-device `bfq_group` data for each blkcg-gq. `bfq_pd_init` wires the group to `bfq_data`, initializes its scheduling entity and service trees, and uses blkcg weight defaults. `bfq_bio_bfqg` walks from `bio->bi_blkg` up to the nearest online BFQ policy data, reassociating the bio if it falls back to an ancestor or root.

Queue migration starts in `bfq_bic_update_cgroup`, which compares the cached blkcg serial number with the bio's current group. On change, it links missing ancestors into BFQ's private hierarchy and calls `__bfq_bic_change_cgroup` across actuators. Asynchronous queues are detached if they belong to the old group; synchronous queues are moved with `bfq_sync_bfqq_move`, unless merge chains cross cgroup boundaries, in which case cooperators are broken. `bfq_bfqq_move` temporarily pins the queue, removes it from old service structures, expires in-service queues if needed, updates parent/sched_data, pins the new group, reactivates busy queues, and schedules dispatch if the device became idle.

Offline flow in `bfq_pd_offline` grabs the scheduler lock, reparents active and in-service queues to root, flushes idle service trees, deactivates the group entity, releases async queues, then transfers dead-group stats to parent auxiliary counters so recursive stats remain meaningful.

## State and persistence behavior
Runtime state includes BFQ group hierarchy, per-group scheduling entities, weights and device-specific weights, references on bfq groups and blkgs, per-group service trees, async queue sets, cgroup serial numbers cached in BFQ IO contexts, and cgroup statistics. State is not persisted across reboot; user-visible controls and stats are exposed through cgroup v1 legacy files and cgroup v2 block files.

## Dependencies and integration points
The file depends on blk-cgroup core, cgroup kernfs APIs, BFQ scheduler internals from `bfq-iosched.h`, request queues, bios, rbtree service trees, ioprio classes, and optional debug stats infrastructure. It is linked into the composite BFQ scheduler object by `block/Makefile`.

## Risks
Reference management is subtle because BFQ queues can outlive cgroup online state and can move while merge chains exist. Incorrect migration can dispatch IO under the wrong group or leave stale service-tree entities. Offline reparenting must cover active, idle, and in-service entities to avoid dangling group pointers. Weight updates rely on a write memory barrier before setting `prio_changed`; removing it could expose stale weights to scheduler code. Debug recursive stats intentionally lose completions after offline transfer, which is accepted but important for interpretation.

## Test signals
Useful tests include BFQ enabled with cgroup v1 and v2, task migration during active synchronous and asynchronous IO, queue merge and split scenarios across cgroups, group deletion under load, weight and per-device weight writes including invalid ranges, recursive stat accounting before and after cgroup removal, root fallback for offline blkgs, and builds with `CONFIG_BFQ_GROUP_IOSCHED` and `CONFIG_BFQ_CGROUP_DEBUG` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bfq-cgroup.c -->
