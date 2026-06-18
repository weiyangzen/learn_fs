# subset-b-006122 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.c -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.c

## Purpose
`zstd_decompress_block.c` implements the compressed-block decoder for the in-kernel Zstandard library. It parses block and sequence headers, decodes literal sections, builds or reuses entropy tables, reconstructs literal/match sequences, and maintains history-window continuity across blocks and standalone block calls.

## Important APIs, types, and functions
Key exported or externally consumed entry points are `ZSTD_getcBlockSize`, `ZSTD_decodeSeqHeaders`, `ZSTD_buildFSETable`, `ZSTD_decompressBlock_internal`, `ZSTD_checkContinuity`, `ZSTD_decompressBlock_deprecated`, and `ZSTD_decompressBlock`. Internal machinery includes `ZSTD_decodeLiteralsBlock`, `ZSTD_allocateLiteralsBuffer`, `ZSTD_buildSeqTable`, `ZSTD_decodeSequence`, `ZSTD_execSequence`, `ZSTD_execSequenceEnd`, split-literal variants, and long-offset prefetch variants. Important transient types are `seq_t`, `ZSTD_fseState`, `seqState_t`, `ZSTD_OffsetInfo`, and `ZSTD_longOffset_e`.

## Control flow
Compressed block decoding first rejects overlarge blocks, decodes the literal section, then decodes sequence headers and FSE tables for literal length, offset, and match length. Literal buffers are placed either after the output, in `litExtraBuffer`, or split between both depending on streaming mode, block size, and destination capacity. Sequence decoding initializes FSE states from the bitstream, regenerates each sequence, copies literals, resolves repeat offsets and external dictionary references, copies matches, and finally appends remaining literals. Runtime dispatch chooses normal, split-literal, or long-offset/prefetch loops, with BMI2-specialized wrappers when enabled.

## State and persistence
Persistent decompression state lives in `ZSTD_DCtx`: entropy tables, repeat offsets, literal buffer metadata, prefix and external-dictionary pointers, frame parameters, checksum state, and cold-dictionary hints. `ZSTD_checkContinuity` updates `prefixStart`, `virtualStart`, `dictEnd`, and `previousDstEnd` when output is not contiguous. Sequence execution updates repeat offsets for later blocks, and table pointers may continue to reference default, dictionary, repeated, or freshly built tables.

## Dependencies and integration points
The file depends on Zstd common helpers for memory, bits, FSE, Huffman, CPU feature dispatch, and internal frame constants. It integrates with higher-level frame decompression in `zstd_decompress.c`, dictionary loading through `zstd_ddict.h`, the public block API in `<linux/zstd.h>`, and the decompressor aggregation path in `decompress_sources.h`.

## Risks and test signals
Risks cluster around malformed headers, unchecked assumptions after FSE/Huffman validation, destination/literal-buffer overlap, 32-bit pointer overflow, repeat-offset underflow, external dictionary boundary math, and streaming writes that could overwrite history. Test signals include fuzzed compressed blocks, empty and zero-sequence blocks, all literal encodings, repeated entropy tables with and without dictionaries, split-literal streaming blocks, offsets crossing prefix/ext-dict boundaries, 32-bit long offsets, BMI2 and non-BMI2 builds, and standalone `ZSTD_decompressBlock()` continuity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.h -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.h

## Purpose
This header exposes the internal compressed-block decompression interface used by the Zstd decompressor implementation. It bridges public declarations in `<linux/zstd.h>` and private block-level helpers needed by frame and dictionary code.

## Important APIs, types, and functions
It defines `streaming_operation` with `not_streaming` and `is_streaming`, declares `ZSTD_decompressBlock_internal`, `ZSTD_buildFSETable`, and `ZSTD_decompressBlock_deprecated`, and relies on `ZSTD_DCtx`, `blockProperties_t`, and `ZSTD_seqSymbol` from included headers. The comments also identify related declarations published elsewhere: `ZSTD_decompressBlock`, `ZSTD_getcBlockSize`, and `ZSTD_decodeSeqHeaders`.

## Control flow
There is no executable control flow. Consumers include the header to call block decompression with explicit streaming context, construct sequence FSE tables from already validated normalized counts, or call the non-deprecated wrapper name without deprecation warnings inside the implementation.

## State and persistence
The header owns no state. Its `streaming_operation` flag influences how `zstd_decompress_block.c` stores literals in `ZSTD_DCtx`, especially whether destination-space literal storage is safe.

## Dependencies and integration points
It includes Zstd dependency, public API, internal constants, and decompression-internal definitions. It is part of the private interface between `zstd_decompress.c`, dictionary code, and the compressed-block decoder.

## Risks and test signals
Risks are ABI drift between public and private prototypes, misuse of `ZSTD_buildFSETable` with invalid or undersized workspace, and callers passing the wrong streaming mode. Test signals are build coverage of all decompressor translation units, static workspace-size assertions, and block decompression tests through both streaming and non-streaming APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_internal.h -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_internal.h

## Purpose
`zstd_decompress_internal.h` defines the internal decompression data model shared by the Zstd decompressor modules. It contains sequence base tables, entropy table storage, decompression stages, dictionary-use policy, and the full `ZSTD_DCtx_s` layout.

## Important APIs, types, and functions
Important constants include `LL_base`, `OF_base`, `OF_bits`, `ML_base`, `ZSTD_BUILD_FSE_TABLE_WKSP_SIZE`, `ZSTD_HUFFDTABLE_CAPACITY_LOG`, and literal-buffer sizing macros. Core types are `ZSTD_seqSymbol_header`, `ZSTD_seqSymbol`, `ZSTD_entropyDTables_t`, `ZSTD_dStage`, `ZSTD_dStreamStage`, `ZSTD_dictUses_e`, `ZSTD_DDictHashSet`, `ZSTD_litLocation_e`, and `struct ZSTD_DCtx_s`. It declares `ZSTD_loadDEntropy` and `ZSTD_checkContinuity`, and provides `ZSTD_DCtx_get_bmi2`.

## Control flow
The header supplies the state machine labels used by frame and stream decompression, but contains no major runtime flow itself. Compile-time BMI2 handling makes `ZSTD_DCtx_get_bmi2` either read `dctx->bmi2` or return zero.

## State and persistence
`ZSTD_DCtx_s` persists all decompressor runtime state: entropy table pointers and storage, Huffman workspace, output continuity pointers, expected frame sizes, block type, stage, entropy reuse flags, checksum state, dictionary references, streaming buffers, output hostage-byte tracking, literal buffers, and optional fuzzing metadata. This state is per-context and reused across frames or streams until reset or freed.

## Dependencies and integration points
It depends on common memory types and Zstd internal constants. It is included by block, frame, dictionary, and streaming decompression code, and it must match the opaque `ZSTD_DCtx` public type expected by `<linux/zstd.h>`.

## Risks and test signals
Risks include layout assumptions across modules, workspace-size mismatches, stale entropy or dictionary pointers after reset, incorrect output-continuity classification, and streaming buffer edge cases around `hostageByte` and `noForwardProgress`. Test signals include context reset/reuse, dictionary switching, checksum validation, static-context allocation bounds, streaming with tiny input/output buffers, and builds with dynamic BMI2 enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress_sources.h -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress_sources.h

## Purpose
`decompress_sources.h` is an aggregation header that includes every C source needed for Zstd decompression in a single translation unit. It is intended for kernel decompression users that need source inclusion rather than normal module linkage.

## Important APIs, types, and functions
The file defines `ZSTD_DISABLE_ASM` before including dependencies, then includes common debug, entropy, error, FSE, Zstd common, Huffman decompression, DDict, frame decompression, block decompression, and the Linux decompressor module wrapper.

## Control flow
There is no direct runtime control flow. At compile time, inclusion order assembles a complete decompressor implementation. The ASM Huffman path is disabled so that all required code comes from included C sources.

## State and persistence
The header creates no state itself, but the included files define the decompressor context, static tables, exported wrappers, and any module metadata present in the included sources.

## Dependencies and integration points
It integrates with `lib/decompress_unzstd.c` and similar early/standalone decompression paths. Because it includes `.c` files directly, it is sensitive to include ordering, macro environment, and duplicate symbol exposure.

## Risks and test signals
Risks include duplicate definitions if included alongside normal objects, incorrect macro leakage, missing source inclusion after upstream Zstd updates, and disabled ASM changing performance characteristics. Test signals are kernel decompression builds, initramfs or compressed-kernel boot tests, link checks for duplicate symbols, and decompression tests under configurations without module-loaded Zstd objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress_sources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/zstd_common_module.c -->
# sources/distributed-fs/ceph-client/lib/zstd/zstd_common_module.c

## Purpose
`zstd_common_module.c` exports common Zstd helper symbols shared by the kernel compression and decompression modules. It packages error handling and entropy-table parsing functions into a common GPL-visible module surface.

## Important APIs, types, and functions
The file exports `FSE_readNCount`, `HUF_readStats`, `HUF_readStats_wksp`, `ZSTD_isError`, `ZSTD_getErrorName`, and `ZSTD_getErrorCode`. It undefines `ZSTD_isError` first because `zstd_internal.h` may define it as a macro.

## Control flow
There is no custom runtime path beyond module loading. The export declarations make common routines available to separately linked Zstd compression and decompression modules.

## State and persistence
The file maintains no runtime state. Module metadata declares dual BSD/GPL licensing and the description `Zstd Common`.

## Dependencies and integration points
It includes Linux module support plus Zstd common `huf.h`, `fse.h`, and `zstd_internal.h`. It is a dependency boundary for `zstd_compress_module.c` and `zstd_decompress_module.c`.

## Risks and test signals
Risks are missing exports after upstream symbol changes, macro/function name mismatches, and license/export incompatibilities for consumers. Test signals include module link/load tests, `modpost` export validation, and compression/decompression module builds as separate objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/zstd_common_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/zstd_compress_module.c -->
# sources/distributed-fs/ceph-client/lib/zstd/zstd_compress_module.c

## Purpose
`zstd_compress_module.c` is the Linux kernel export wrapper for Zstd compression. It translates the kernel-facing `zstd_*` API into upstream `ZSTD_*` context, parameter, dictionary, one-shot, streaming, and external-sequence APIs.

## Important APIs, types, and functions
The helper `zstd_cctx_init` resets a compression context, sets pledged source size, and applies compression and frame parameters. Exported symbols include compression level queries, bound/parameter helpers, workspace-bound helpers with and without external sequence producers, static and dynamic context creation/free, CDict creation/free, one-shot compression, CDict compression, streaming init/reset/compress/flush/end, sequence producer registration, and `zstd_compress_sequences_and_literals`.

## Control flow
Most wrappers validate only the static workspace pointer or normalize Linux API conventions before calling upstream APIs. `zstd_cctx_init` is the central setup path for one-shot and streaming initialization. The external-sequence workspace-bound helpers register a dummy producer to force sizing for contexts that may use producer state. Streaming init and reset map a pledged size of zero to `ZSTD_CONTENTSIZE_UNKNOWN`.

## State and persistence
State is held in caller-provided or dynamically allocated `zstd_cctx`, `zstd_cstream`, and `zstd_cdict` objects. The module itself stores no mutable global state. Context state persists until reset or free and includes parameters, pledged size, dictionaries, and optional sequence producer hooks.

## Dependencies and integration points
It depends on Linux module/string/kernel headers, `<linux/zstd.h>`, Zstd deps/internal headers, and compression internals. Kernel users such as filesystems, crypto users, or storage code link to these exported wrappers instead of the raw upstream names.

## Risks and test signals
Risks include parameter translation drift, workspace-bound underestimation, static-context NULL handling, pledged-size convention mismatches, external sequence producer sizing, and error propagation through `size_t` Zstd error codes. Test signals include all compression levels, static and dynamic context paths, CDict by-reference lifetime tests, streaming with known and unknown sizes, external-sequence compression, and module export checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/zstd_compress_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/zstd_decompress_module.c -->
# sources/distributed-fs/ceph-client/lib/zstd/zstd_decompress_module.c

## Purpose
`zstd_decompress_module.c` is the Linux kernel export wrapper for Zstd decompression. It exposes stable `zstd_*` names for error inspection, decompression contexts, DDicts, one-shot decompression, streaming decompression, frame size lookup, and frame header parsing.

## Important APIs, types, and functions
Exported symbols include `zstd_is_error`, `zstd_get_error_code`, `zstd_get_error_name`, `zstd_dctx_workspace_bound`, `zstd_create_dctx_advanced`, `zstd_free_dctx`, `zstd_create_ddict_byreference`, `zstd_free_ddict`, `zstd_init_dctx`, `zstd_decompress_dctx`, `zstd_decompress_using_ddict`, `zstd_dstream_workspace_bound`, `zstd_init_dstream`, `zstd_reset_dstream`, `zstd_decompress_stream`, `zstd_find_frame_compressed_size`, and `zstd_get_frame_header`.

## Control flow
Wrappers mainly forward to upstream `ZSTD_*` functions. Static initialization rejects a NULL workspace. `zstd_init_dstream` accepts `max_window_size` for the Linux API but discards it before calling `ZSTD_initStaticDStream`, while workspace sizing still uses the max-window parameter.

## State and persistence
Runtime state is in `zstd_dctx`, `zstd_dstream`, and `zstd_ddict` instances. DDicts created by reference depend on the caller keeping dictionary bytes alive. The module itself has no global mutable decompression state.

## Dependencies and integration points
It includes Linux kernel/module/string headers, `<linux/zstd.h>`, and Zstd deps. It integrates with kernel consumers that need decompression without directly depending on upstream symbol names, and with the common module for shared error helpers.

## Risks and test signals
Risks include by-reference dictionary lifetime errors, static workspace sizing mismatches, ignored `max_window_size` surprises at init, and callers failing to check `size_t` error returns. Test signals include frame and streaming decompression, malformed input, DDict reuse, reset behavior, workspace-bound allocation tests, and exported-symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/zstd_decompress_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/Kconfig -->
# sources/distributed-fs/ceph-client/mm/Kconfig

## Purpose
`mm/Kconfig` defines the memory-management configuration surface for this kernel tree. It controls swap, zswap, zsmalloc, slab hardening, memory models, hotplug, compaction, migration, CMA, THP, NUMA, device memory, BPF-visible memory control support through dependent objects, and many debug/test options.

## Important APIs, types, and functions
As Kconfig input, the important entities are symbols and dependency relationships rather than functions. Relevant symbols for this work item include `ZSWAP`, `ZSMALLOC`, `MEMORY_HOTPLUG`, `HAVE_BOOTMEM_INFO_NODE`, `BALLOON`, `BALLOON_MIGRATION`, `COMPACTION`, `MIGRATION`, `CMA`, `CMA_DEBUGFS`, `CMA_SYSFS`, `CMA_AREAS`, `MEMCG`, `BPF_SYSCALL`, and `USERFAULTFD`.

## Control flow
Configuration selection flows from menus, choices, defaults, `depends on`, and `select`. For example, `CMA` depends on `MMU` and selects `MIGRATION` and `MEMORY_ISOLATION`; `BALLOON_MIGRATION` depends on `MIGRATION && BALLOON`; memory hotremove selects bootmem-info support on selected architectures; and zswap compressor choices select the appropriate crypto algorithms.

## State and persistence
The file has no runtime state, but selected symbols persist into `.config` and generated autoconf headers, which determine compiled code, static defaults, exposed sysfs/debugfs features, and boot-time behavior.

## Dependencies and integration points
It integrates with architecture Kconfig symbols, generated build configuration, `mm/Makefile`, documentation references, and runtime kernel parameters mentioned in help text such as `zswap.enabled`, `zswap.compressor`, memory-hotplug auto-online policy, THP defaults, and page allocator shuffling.

## Risks and test signals
Risks include invalid dependency combinations, silently missing mm features, security-sensitive defaults such as slab merging or uninitialized mmap, and symbols selected without required architecture support. Test signals are `olddefconfig`, randconfig/allmodconfig builds, feature-specific boot tests for CMA, ballooning, memory hotplug, zswap, THP, and Kconfig dependency linting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/Makefile -->
# sources/distributed-fs/ceph-client/mm/Makefile

## Purpose
`mm/Makefile` maps memory-management configuration symbols to built objects and sets sanitizer/instrumentation exceptions for core allocator paths. It is the build integration point for the `mm/` implementation files in this work item.

## Important APIs, types, and functions
Important variables include `obj-y`, `mmu-y`, `page-alloc-y`, `memory-hotplug-y`, and many `obj-$(CONFIG_...)` lines. Relevant mappings are unconditional `backing-dev.o`, `obj-$(CONFIG_BALLOON) += balloon.o`, `obj-$(CONFIG_HAVE_BOOTMEM_INFO_NODE) += bootmem_info.o`, `obj-$(CONFIG_CMA) += cma.o`, and conditional `obj-$(CONFIG_MEMCG) += bpf_memcontrol.o` under `CONFIG_BPF_SYSCALL`.

## Control flow
The build first establishes sanitizer exclusions for allocator files, then builds the core `mm` object set and conditionally appends feature objects. `ifdef CONFIG_MMU`, `CONFIG_SWAP`, `CONFIG_CMA`, and `CONFIG_BPF_SYSCALL` blocks further refine object inclusion.

## State and persistence
The Makefile has no runtime state. Its persistent effect is the compiled kernel image or modules selected by `.config`, including whether debug/test objects and feature-specific mm code are present.

## Dependencies and integration points
It integrates generated Kconfig symbols with Kbuild, sanitizer tooling, KCOV/KCSAN/KASAN configuration, mm subdirectories such as `kasan/`, `kfence/`, `damon/`, and external users expecting core mm exports.

## Risks and test signals
Risks include missing object inclusion for selected Kconfig symbols, accidental instrumentation of fragile allocator paths, feature objects built without dependencies, and ordering issues for core objects. Test signals include allyesconfig/allmodconfig/randconfig builds, sanitizer-enabled builds, BPF+MEMCG combinations, CMA/balloon/hotplug configurations, and link checks for exported mm symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/backing-dev.c -->
# sources/distributed-fs/ceph-client/mm/backing-dev.c

## Purpose
`backing-dev.c` manages `struct backing_dev_info` registration, visibility, sysfs/debugfs attributes, writeback workqueue setup, and cgroup writeback domains. It is the central lifetime manager connecting filesystems and block devices to kernel writeback accounting and throttling.

## Important APIs, types, and functions
Important global state includes `noop_backing_dev_info`, `bdi_lock`, `bdi_tree`, `bdi_list`, and `bdi_wq`. Public functions include `bdi_init`, `bdi_alloc`, `bdi_register_va`, `bdi_register`, `bdi_set_owner`, `bdi_unregister`, `bdi_put`, `inode_to_bdi`, `bdi_dev_name`, and, with cgroup writeback, `wb_get_lookup`, `wb_get_create`, `wb_memcg_offline`, and `wb_blkcg_offline`. Internal helpers manage `bdi_writeback` initialization, shutdown, stats, debugfs, sysfs stores, and cgwb release.

## Control flow
`bdi_class_init` registers the `bdi` class and debugfs root, while `default_bdi_init` creates the global writeback workqueue. `bdi_alloc` initializes a BDI and root writeback state. `bdi_register_va` creates a class device, links the root writeback, registers debugfs, assigns an ID in the rb-tree, and publishes the BDI on the RCU list. Unregister removes global visibility, shuts down writeback work, tears down cgroup writebacks, resets ratios, removes devices/debugfs, and drops owner references.

## State and persistence
State is runtime-only: BDI IDs, rb-tree/list membership, krefs, device names, owner refs, ratio/byte limits, read-ahead values, writeback lists, delayed work, bandwidth counters, per-cpu counters, cgroup writeback radix trees, and offline cgwb lists. RCU and kref rules control when removed objects can be freed.

## Dependencies and integration points
It depends on device core, debugfs, writeback, memcg/blkcg, cgroups, workqueues, RCU, radix trees, percpu refs/counters, and tracepoints. It integrates with superblocks, block devices, sysfs `/sys/class/bdi`, debugfs `bdi`, and dirty throttling helpers.

## Risks and test signals
Risks include registration/unregistration races, use-after-free through RCU-visible lists, delayed work after shutdown, cgroup writeback offlining races, blkcg association changes, ratio accounting imbalance, and sysfs validation errors. Test signals include repeated BDI register/unregister, concurrent writeback and unmount, memcg/blkcg offlining, debugfs reads during teardown, sysfs min/max ratio and byte writes, block-device inode lookup, and lockdep/RCU stall checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/backing-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/balloon.c -->
# sources/distributed-fs/ceph-client/mm/balloon.c

## Purpose
`balloon.c` provides common helper code for memory balloon drivers, including page allocation, enqueue/dequeue accounting, and optional migration support for inflated balloon pages.

## Important APIs, types, and functions
Exported helpers are `balloon_page_list_enqueue`, `balloon_page_list_dequeue`, `balloon_page_alloc`, `balloon_page_enqueue`, and `balloon_page_dequeue`. Internal migration helpers include `balloon_page_device`, `balloon_page_isolate`, `balloon_page_putback`, `balloon_page_migrate`, and the `balloon_mops` `movable_operations`. Shared state is protected by `balloon_pages_lock`.

## Control flow
Drivers allocate pages via `balloon_page_alloc`, enqueue them after inflation, and dequeue them before returning memory to the guest. Enqueue marks pages offline, optionally stores the owning balloon device in `page_private`, adjusts managed page counts, and updates VM events and node page state. Dequeue removes pages from the balloon list, restores accounting, clears private migration state, and returns pages to the caller. With migration enabled, compaction can isolate a balloon page, ask the driver to migrate it, install the replacement page into the balloon list, or handle deflation.

## State and persistence
State lives in each `balloon_dev_info`: page list, isolated-page count, optional accounting callback, and driver migration callback. Individual pages persist offline state until freed to buddy; migration mode uses `page_private` to locate the owning balloon device.

## Dependencies and integration points
It depends on page allocator, page flags, VM event accounting, node page state, movable page operations, migration/compaction, and `linux/balloon.h`. It integrates with virtio or hypervisor balloon drivers that own actual inflate/deflate protocol behavior.

## Risks and test signals
Risks include losing pages when dequeue races isolation, incorrect managed-page accounting across zones, stale `page_private`, driver migration callback failures, and the hard `BUG()` path when accounting says pages exist but none are listable or isolated. Test signals include inflate/deflate loops, list enqueue/dequeue batching, compaction-induced balloon migration, migration failure paths, zone-crossing migration, and VM counters for inflate/deflate/migrate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/balloon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/bootmem_info.c -->
# sources/distributed-fs/ceph-client/mm/bootmem_info.c

## Purpose
`bootmem_info.c` tracks boot-time metadata pages so they are not freed prematurely and can be released correctly during memory hotplug teardown. It registers pgdat and sparsemem section metadata as reserved bootmem-backed pages.

## Important APIs, types, and functions
Public functions are `get_page_bootmem`, `put_page_bootmem`, and `register_page_bootmem_info_node`. The internal helper `register_page_bootmem_info_section` registers `mem_section` usage metadata. It uses `bootmem_type`, `page_private`, page refcounts, and kmemleak physical-range freeing.

## Control flow
`get_page_bootmem` encodes an info value and bootmem type into `page_private`, sets `PagePrivate`, and increments the page refcount. `put_page_bootmem` validates the type and, when the reference drops to one, clears private state, reinitializes the list head, tells kmemleak about the freed physical page, and releases it as a reserved page. Node registration marks the `pglist_data` pages and iterates valid sparsemem sections belonging to the node.

## State and persistence
Metadata ownership persists in `page_private` and elevated refcounts until hotplug or teardown calls `put_page_bootmem`. There is no on-disk state.

## Dependencies and integration points
It depends on sparsemem section helpers, memblock-era metadata, memory hotplug type ranges, kmemleak, and page allocator reserved-page release. It is compiled when `HAVE_BOOTMEM_INFO_NODE` is selected.

## Risks and test signals
Risks include bad type encoding, reference leaks that keep bootmem pages reserved forever, double release, registering PFNs assigned to multiple nodes, and mismatches with preinitialized vmemmap sections. Test signals include memory hotplug add/remove, sparsemem section metadata release, kmemleak noise checks, multi-node boot with overlapping early PFN ownership, and debug page refcount validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/bootmem_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/bpf_memcontrol.c -->
# sources/distributed-fs/ceph-client/mm/bpf_memcontrol.c

## Purpose
`bpf_memcontrol.c` registers BPF kfuncs that let BPF programs acquire memory cgroups and read selected memory controller statistics and events.

## Important APIs, types, and functions
Kfuncs are `bpf_get_root_mem_cgroup`, `bpf_get_mem_cgroup`, `bpf_put_mem_cgroup`, `bpf_mem_cgroup_vm_events`, `bpf_mem_cgroup_usage`, `bpf_mem_cgroup_memory_events`, `bpf_mem_cgroup_page_state`, and `bpf_mem_cgroup_flush_stats`. The `BTF_KFUNCS_START` block annotates acquire/release/null/RCU/sleepable semantics, and `bpf_memcontrol_init` registers the set for `BPF_PROG_TYPE_UNSPEC`.

## Control flow
At late init, the file registers a BTF kfunc ID set. BPF callers can acquire the root memcg, translate an arbitrary css to the memory-controller css if needed under RCU, release acquired references, read validated vm events or stat counters, read memory usage and memory events, or flush memcg stats in sleepable contexts.

## State and persistence
The file stores no private mutable state. It operates on memcg/css references and counters maintained by the memory controller. Acquired memcg references persist until a matching `bpf_put_mem_cgroup`.

## Dependencies and integration points
It depends on memcontrol, cgroup css lifetime rules, BPF kfunc registration, BTF ID metadata, RCU, and page counter/stat helpers. The Makefile builds it only for `CONFIG_BPF_SYSCALL` plus `CONFIG_MEMCG`.

## Risks and test signals
Risks include reference leaks in BPF programs, invalid enum reads, css translation races, exposing sleepable flushing to non-sleepable program contexts, and behavior when memcg is disabled. Test signals include verifier checks for acquire/release pairing, RCU requirements, root and non-root cgroup lookups, invalid counter indexes, disabled-memcg boots, and BPF selftests for kfunc availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/bpf_memcontrol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma.c -->
# sources/distributed-fs/ceph-client/mm/cma.c

## Purpose
`cma.c` implements the Contiguous Memory Allocator. It reserves boot-time physical memory areas, activates them as migratable CMA pageblocks, allocates physically contiguous ranges at runtime, supports multi-range CMA areas, and releases allocated ranges back to CMA.

## Important APIs, types, and functions
Public APIs include `cma_get_base`, `cma_get_size`, `cma_get_name`, `cma_validate_zones`, `cma_reserve_pages_on_error`, `cma_init_reserved_mem`, `cma_declare_contiguous_multi`, `cma_declare_contiguous_nid`, `cma_alloc_frozen`, `cma_alloc_frozen_compound`, `cma_alloc`, `cma_release`, `cma_release_frozen`, `cma_for_each_area`, `cma_intersects`, and `cma_reserve_early`. Core internal helpers include bitmap alignment helpers, `cma_activate_area`, `cma_new_area`, `cma_alloc_mem`, `cma_range_alloc`, `__cma_alloc_frozen`, and `find_cma_memrange`.

## Control flow
Early declaration reserves memory through memblock, validates size/alignment/order constraints, creates a `struct cma`, and records one or more PFN ranges. `core_initcall(cma_init_reserved_areas)` allocates bitmaps, validates that ranges do not cross zones, marks early-reserved bits, initializes CMA pageblocks, locks, and debug state. Runtime allocation scans range bitmaps for an aligned free area, marks bits under spinlock, calls `alloc_contig_frozen_range` under `alloc_mutex`, clears bits on retryable failure, and returns frozen or refcounted pages. Release verifies the pages belong to one CMA range, drops page refs for normal allocations, frees the frozen range, clears bitmap bits, and updates accounting.

## State and persistence
Global `cma_areas`, `cma_area_count`, and `totalcma_pages` persist after boot. Each CMA area stores total and available page counts, order-per-bit, locks, flags, NUMA node, sysfs/debugfs accounting, and up to `CMA_MAX_RANGES` physical ranges. Bitmap bits persist allocation state; `early_pfn` tracks pre-activation bottom-up reservations until activation replaces it with bitmaps.

## Dependencies and integration points
It depends on memblock, pageblock migration types, `alloc_contig_frozen_range`, `free_contig_frozen_range`, KASAN tag reset, kmemleak, tracepoints, sysfs/debugfs accounting hooks, NUMA-aware free range iteration, and exported CMA APIs used by DMA, hugetlb CMA, device drivers, and architecture setup code.

## Risks and test signals
Risks include zone-crossing ranges, bitmap/count imbalance, multi-range rollback bugs, alignment/order mistakes, early reservations not represented in bitmaps, contiguity failures from memory holes, alloc/release refcount misuse, and error handling that either leaks reserved memory or frees memory that callers own. Test signals include fixed and dynamic reservation, highmem and above-4G placement, multi-range fallback, CMA sysfs/debugfs accounting, concurrent allocations, `-EBUSY` retry paths, release of invalid pages, `cma_reserve_early`, memory hotplug interactions, and tracepoint/VM event counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma.h -->
# sources/distributed-fs/ceph-client/mm/cma.h

## Purpose
`cma.h` defines private data structures and helpers for the Contiguous Memory Allocator implementation. It captures multi-range CMA metadata, allocation bitmaps, debug/sysfs integration fields, flags, and shared accounting declarations.

## Important APIs, types, and functions
Important types are `struct cma_kobject`, `struct cma_memrange`, `struct cma`, and `enum cma_flags`. Constants include `CMA_MAX_RANGES`. It declares global `cma_areas` and `cma_area_count`, defines `cma_bitmap_maxno`, and declares or stubs `cma_sysfs_account_success_pages`, `cma_sysfs_account_fail_pages`, and `cma_sysfs_account_release_pages`.

## Control flow
The header contains only inline/stub behavior. `cma_bitmap_maxno` converts a range page count into bitmap bits using `order_per_bit`; sysfs accounting calls either link to real functions when `CONFIG_CMA_SYSFS` is enabled or compile away.

## State and persistence
The structures defined here describe persistent runtime CMA state: per-range base/count and early-PFN-or-bitmap union, per-area counts and locks, optional debugfs bitmap views, sysfs counters, activation/validation flags, and NUMA node ownership.

## Dependencies and integration points
It depends on debugfs and kobject definitions and is shared by `cma.c`, `cma_debug.c`, and `cma_sysfs.c`. It connects private CMA internals to optional observability layers while keeping public CMA users on `<linux/cma.h>`.

## Risks and test signals
Risks include misuse of the `early_pfn`/`bitmap` union before or after activation, bitmap sizing mismatches, stale sysfs/debugfs pointers, and assumptions that a CMA area has only one range. Test signals include builds with and without `CONFIG_CMA_DEBUGFS` and `CONFIG_CMA_SYSFS`, multi-range reservations, `cma_get_base` warning behavior, sysfs accounting updates, and bitmap boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma.h -->
