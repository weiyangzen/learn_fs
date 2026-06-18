# subset-b-005839 research

Grouped research report for Linux compatibility and block-layer headers under `sources/distributed-fs/ceph-client/include/linux`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitmap.h -->
# sources/distributed-fs/ceph-client/include/linux/bitmap.h

## Purpose
`bitmap.h` declares and inlines the generic Linux bitmap API: allocation helpers, bitwise set operations, scans, transformations, region allocation, endian-aware array conversions, and small-field reads/writes. It is a central utility header used by block queues, CPU masks, cgroups, allocation maps, and any component that stores dense bit state in arrays of `unsigned long`.

## Important APIs, Types, And Functions
The allocation surface is `bitmap_alloc()`, `bitmap_zalloc()`, node-aware variants, `bitmap_free()`, `DEFINE_FREE(bitmap, ...)`, and device-managed `devm_bitmap_alloc()`/`devm_bitmap_zalloc()`. Core operations include `bitmap_zero()`, `bitmap_fill()`, `bitmap_copy()`, `bitmap_copy_clear_tail()`, logical operations (`bitmap_and()`, `bitmap_or()`, `bitmap_xor()`, `bitmap_andnot()`, `bitmap_complement()`, `bitmap_replace()`), comparisons (`bitmap_equal()`, `bitmap_or_equal()`, `bitmap_intersects()`, `bitmap_subset()`, `bitmap_empty()`, `bitmap_full()`), weights (`bitmap_weight()`, `bitmap_weight_and()`, `bitmap_weight_andnot()`, `bitmap_weight_from()`), ranges (`bitmap_set()`, `bitmap_clear()`), shifts, remapping (`bitmap_remap()`, `bitmap_bitremap()`, `bitmap_onto()`, `bitmap_fold()`), and sparse/dense conversions (`bitmap_scatter()`, `bitmap_gather()`).

The conversion helpers bridge bitmap storage with fixed-width arrays: `bitmap_from_arr32()`, `bitmap_to_arr32()`, `bitmap_from_arr64()`, `bitmap_to_arr64()`, `BITMAP_FROM_U64()`, and `bitmap_from_u64()`. `bitmap_read()` and `bitmap_write()` read or write values up to `BITS_PER_LONG` at arbitrary bit offsets, including cross-word cases. `BITMAP_FIRST_WORD_MASK()`, `BITMAP_LAST_WORD_MASK()`, and `bitmap_size()` define the sizing and tail-mask rules.

## Control Flow And State
Most public functions are `static __always_inline` wrappers that choose a fast single-word path when `small_const_nbits(nbits)` is true, a byte-oriented path when alignment permits `memcpy()`/`memset()`/`memcmp()`, or an out-of-line `__bitmap_*()` implementation in `lib/bitmap.c` for general multiword cases. `bitmap_set()` and `bitmap_clear()` additionally special-case single-bit updates and byte-aligned constant ranges before falling back to `__bitmap_set()`/`__bitmap_clear()`.

`bitmap_scatter()` and `bitmap_gather()` iterate `for_each_set_bit()` over a mask and assign target bits with `__assign_bit()`. Region allocation uses `bitmap_find_free_region()` to scan power-of-two aligned regions, `bitmap_allocate_region()` to test and set a region, and `bitmap_release_region()` to clear it. There is no hidden persistence: state lives only in caller-provided bitmap memory or allocated bitmap storage.

## Dependencies And Integration Points
The header depends on `linux/bitops.h`, `linux/find.h`, `linux/bitmap-str.h`, `linux/align.h`, string primitives, errno values, and type definitions. Architecture-specific bitops and `lib/bitmap.c` supply the heavy implementations. It integrates directly with block queue bitmaps, tag maps, cgroup policy bitmaps, and any subsystem using `DECLARE_BITMAP()`.

## Risks And Test Signals
Primary risks are tail-bit leakage, off-by-one masks, invalid `nbits` to `bitmap_read()`/`bitmap_write()`, endian conversion mistakes on 32-bit big-endian systems, and non-atomic use where callers actually require atomic bitops. Test signals should include single-word and multiword bitmaps, unaligned starts, cross-word reads/writes, `nbits` not divisible by `BITS_PER_LONG`, BE/LE conversion checks, region allocation failure paths, and scatter/gather equivalence tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitops.h -->
# sources/distributed-fs/ceph-client/include/linux/bitops.h

## Purpose
`bitops.h` is the generic front door for Linux bit operations. It ties together type-sized bit counting, architecture bitops, pure-C constant-foldable bitops, rotates, sign extension, order calculations, parity, first-set helpers, and atomic-looking compare/exchange mask helpers.

## Important APIs, Types, And Functions
Size conversion macros are `BITS_TO_LONGS()`, `BITS_TO_U64()`, `BITS_TO_U32()`, `BITS_TO_BYTES()`, and `BYTES_TO_BITS()`. Software Hamming weight functions are declared as `__sw_hweight8/16/32/64()`, with `hweight_long()` selecting 32- or 64-bit counting. The `bitop()` macro routes `__set_bit()`, `__clear_bit()`, `__change_bit()`, test-and-modify variants, `test_bit()`, and `test_bit_acquire()` to compile-time C helpers when possible and otherwise to normal architecture operations.

The header exports rotate helpers `rol64()`/`ror64()`, `rol32()`/`ror32()`, `rol16()`/`ror16()`, and `rol8()`/`ror8()`, sign extension helpers `sign_extend32()` and `sign_extend64()`, order helpers `get_bitmask_order()`, `get_count_order()`, and `get_count_order_long()`, `fls_long()`, `parity8()`, `__ffs64()`, `fns()`, and assignment/pointer-bit macros `assign_bit()`, `__assign_bit()`, `__ptr_set_bit()`, `__ptr_clear_bit()`, and `__ptr_test_bit()`. Under `__KERNEL__`, `set_mask_bits()` and `bit_clear_unless()` update words with `READ_ONCE()` plus `try_cmpxchg()`.

## Control Flow And State
The main control pattern is dispatch through `bitop()`: if the bit number, address non-nullness, and referenced word value are compile-time constants, the macro invokes a `const*` implementation from generic non-atomic bitops; otherwise it invokes the runtime operation. This preserves architecture behavior while allowing constants to optimize into immediate expressions. Rotates mask the shift count and use complementary shifts, avoiding undefined full-width shifts. `parity8()` folds the byte into four bits and indexes a parity constant. `set_mask_bits()` and `bit_clear_unless()` loop until a compare/exchange succeeds or until the test mask blocks clearing.

## Dependencies And Integration Points
The header depends on `asm/types.h`, `linux/bits.h`, `linux/typecheck.h`, `uapi/linux/kernel.h`, `asm-generic/bitops/generic-non-atomic.h`, and `asm/bitops.h`. Static assertions verify that architecture, constant, and generic bitop prototypes match. `bitmap.h`, request flags, queue flags, cgroup bitmaps, and pointer tagging helpers build on this API.

## Risks And Test Signals
Risks include using non-atomic `__*` bitops for shared state, invoking `__ffs64()` with zero, passing invalid sign-bit indexes, relying on pointer bit operations when alignment does not leave spare low bits, or breaking prototype parity between architecture and generic helpers. Test signals should cover constant folding, runtime bitops, 32-bit and 64-bit builds, rotate by zero and word-size multiples, compare/exchange retry behavior, and sparse/typecheck warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitrev.h -->
# sources/distributed-fs/ceph-client/include/linux/bitrev.h

## Purpose
`bitrev.h` provides bit-reversal helpers for 8-, 16-, and 32-bit values, plus a four-byte byte-wise reversal helper. It supports either architecture-provided implementations or a generic table/composition implementation.

## Important APIs, Types, And Functions
When `CONFIG_HAVE_ARCH_BITREVERSE` is set, `__bitrev32`, `__bitrev16`, and `__bitrev8` alias architecture implementations from `asm/bitrev.h`. Otherwise the header declares `byte_rev_table[256]`, implements `__bitrev8()` as a table lookup, and composes `__bitrev16()` and `__bitrev32()` from smaller reversals. `__bitrev8x4(x)` reverses bits in each byte after `swab32(x)`.

The public macros `bitrev32()`, `bitrev16()`, `bitrev8x4()`, and `bitrev8()` use `__builtin_constant_p()` to select constant-expression algorithms (`__constant_bitrev32()`, `__constant_bitrev16()`, `__constant_bitrev8x4()`, `__constant_bitrev8()`) or runtime helpers.

## Control Flow And State
This header has no mutable state except the external byte reversal table in the generic path. Runtime control flow is a simple constant-vs-runtime branch inside statement-expression macros. Constant helpers perform staged swaps: halves, bytes/nibbles, two-bit groups, then one-bit groups. Generic runtime helpers compose table lookups to avoid repeated masking at runtime.

## Dependencies And Integration Points
It depends on `linux/types.h`, optional `asm/bitrev.h`, and byte-swap support for `swab32()` as made available in the kernel include environment. It is commonly used by protocol, storage, CRC, flash, and hardware drivers that need wire-format or register bit-order transformations.

## Risks And Test Signals
Risks are confusion between whole-word reversal and per-byte reversal (`bitrev8x4()`), missing byte-swap declarations in unusual include contexts, and architecture implementations diverging from generic semantics. Tests should compare constant and nonconstant inputs for all helpers, use asymmetric values such as `0x01234567`, and validate table-backed and architecture-backed builds where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bitrev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bits.h -->
# sources/distributed-fs/ceph-client/include/linux/bits.h

## Purpose
`bits.h` defines common bit and mask construction macros used throughout the kernel. It layers Linux-specific type-checked mask helpers over VDSO and UAPI definitions while keeping assembly-compatible fallbacks.

## Important APIs, Types, And Functions
The basic helpers are `BIT_MASK()`, `BIT_WORD()`, `BIT_ULL_MASK()`, `BIT_ULL_WORD()`, `BITS_PER_BYTE`, and `BITS_PER_TYPE(type)`. In C contexts, `GENMASK_TYPE()` creates a contiguous mask for a specified unsigned type, with public variants `GENMASK()`, `GENMASK_ULL()`, `GENMASK_U8()`, `GENMASK_U16()`, `GENMASK_U32()`, `GENMASK_U64()`, and `GENMASK_U128()`. Fixed-width single-bit macros are `BIT_U8()`, `BIT_U16()`, `BIT_U32()`, and `BIT_U64()`.

## Control Flow And State
There is no runtime state. Compile-time control is performed through `GENMASK_INPUT_CHECK()` and `BIT_INPUT_CHECK()`, which use `BUILD_BUG_ON_ZERO(const_true(...))` and compiler shift diagnostics to catch inverted ranges or out-of-width bit numbers. In assembly mode, typed helpers requiring `sizeof()` are unavailable, so the header maps `GENMASK()` and `GENMASK_ULL()` directly to UAPI-style `__GENMASK()` and `__GENMASK_ULL()`.

## Dependencies And Integration Points
The header includes `vdso/bits.h` and `uapi/linux/bits.h` for foundational `BIT()`/`BIT_ULL()` and mask macros. C-only checks depend on `linux/build_bug.h`, `linux/compiler.h`, and `linux/overflow.h`. It underpins `bitops.h`, `bitmap.h`, block request flags, queue feature flags, and nearly every register or mask definition in the tree.

## Risks And Test Signals
Risks are invalid macro arguments with side effects, negative bit numbers, width overflow, and assembly users accidentally depending on C-only typed helpers. Test signals are compile-time build failures for `GENMASK(15, 20)`, `GENMASK_U32(33, 15)`, and `BIT_U8(8)`, plus successful mask values for boundary cases such as bit 0, the top bit of each type, and full-width masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/blk-cgroup.h

## Purpose
`blk-cgroup.h` declares the common block I/O controller cgroup interface used to associate bios with block cgroups, throttle current tasks, observe congestion, and carry Fibre Channel application identifiers.

## Important APIs, Types, And Functions
With `CONFIG_BLK_CGROUP`, the header exposes `blkcg_root_css`, `blkcg_schedule_throttle()`, `blkcg_maybe_throttle_current()`, `blk_cgroup_congested()`, `blkcg_pin_online()`, `blkcg_unpin_online()`, `blkcg_get_cgwb_list()`, and `bio_blkcg_css()`. Without cgroup block support, it provides inert fallbacks: root CSS is an `ERR_PTR(-EINVAL)`, throttling is a no-op, congestion is false, and `bio_blkcg_css()` returns `NULL`.

The Fibre Channel app-id helpers `blkcg_set_fc_appid()` and `blkcg_get_fc_appid()` are declared outside the config block. `FC_APPID_LEN` defines the maximum application identifier storage length.

## Control Flow And State
The header itself owns no state; all state lives in cgroup subsystem state, bios, request queues, and block-cgroup internals. The config-gated wrappers make caller code compile regardless of kernel configuration while preserving behavior only when the block cgroup controller exists. Pin/unpin calls imply lifetime protection for online cgroups; throttle calls integrate with scheduling and memdelay behavior.

## Dependencies And Integration Points
It depends on `linux/types.h` and forward declarations for `bio`, `cgroup_subsys_state`, and `gendisk`. `blk_types.h` stores per-bio cgroup data under `CONFIG_BLK_CGROUP`, and `request_queue` stores policy bitmaps and root block groups. The app-id functions integrate with FC storage paths and cgroup identity.

## Risks And Test Signals
Risks include forgetting that cgroup helpers may be compiled out, using `blkcg_root_css` without checking the error pointer in non-cgroup builds, and mishandling cgroup lifetime around online pinning. Test signals include builds with and without `CONFIG_BLK_CGROUP`, throttling behavior under cgroup I/O limits, bio-to-cgroup attribution, and app-id length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-crypto-profile.h -->
# sources/distributed-fs/ceph-client/include/linux/blk-crypto-profile.h

## Purpose
`blk-crypto-profile.h` defines the inline-encryption capability and keyslot-management interface implemented by storage drivers and consumed by the block crypto layer. It describes what crypto modes and key types a device supports and how keys are programmed, evicted, wrapped, imported, generated, and prepared.

## Important APIs, Types, And Functions
`struct blk_crypto_ll_ops` contains driver callbacks: `keyslot_program()`, `keyslot_evict()`, `derive_sw_secret()`, `import_key()`, `generate_key()`, and `prepare_key()`. `struct blk_crypto_profile` contains public driver-initialized fields `ll_ops`, `max_dun_bytes_supported`, `key_types_supported`, `modes_supported[]`, and optional runtime-PM `dev`. Private fields track `num_slots`, a serializing `rw_semaphore lock`, lockdep class, idle slot wait queue/list/spinlock, a key-to-slot hash table, slot hash size, and per-slot state.

Lifecycle and capability functions include `blk_crypto_profile_init()`, `devm_blk_crypto_profile_init()`, `blk_crypto_profile_destroy()`, `blk_crypto_keyslot_index()`, `blk_crypto_reprogram_all_keys()`, `blk_crypto_import_key()`, `blk_crypto_generate_key()`, `blk_crypto_prepare_key()`, `blk_crypto_intersect_capabilities()`, `blk_crypto_has_capabilities()`, and `blk_crypto_update_capabilities()`.

## Control Flow And State
The profile serializes all low-level driver operations through `profile->lock`; operations may sleep and are not called while `profile->dev` is runtime-suspended. If hardware has keyslots, programming and eviction operate on unused slots. If a layered device lacks slots, eviction propagates to underlying devices. Hardware-wrapped-key callbacks convert between raw, long-term wrapped, ephemeral wrapped, and software-secret forms.

Persistent state is in the profile: supported mode bitmasks, key type bitmasks, keyslot hash state, idle LRU ordering, wait queues, and per-keyslot metadata. The header defines contracts but the actual state transitions live in block crypto implementation files.

## Dependencies And Integration Points
It includes `linux/bio.h` and `linux/blk-crypto.h`. `request_queue` references `struct blk_crypto_profile` under `CONFIG_BLK_INLINE_ENCRYPTION`, while drivers register profiles via `blk_crypto_register()` in `blkdev.h`. Filesystems and dm/stacking devices use capability intersection/update helpers to advertise only common supported modes.

## Risks And Test Signals
Risks include failing to initialize capability bitmasks, advertising wrapped-key support without all required callbacks, incorrect DUN byte limits, keyslot leaks, eviction races, runtime-PM misuse, and capability intersection bugs in stacked devices. Tests should cover profile init/destroy, slot reuse and wait paths, key reprogramming after reset, raw and hardware-wrapped key workflows, unsupported mode rejection, and runtime suspend/resume around low-level callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-crypto-profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-crypto.h -->
# sources/distributed-fs/ceph-client/include/linux/blk-crypto.h

## Purpose
`blk-crypto.h` defines the block-layer inline encryption key and bio context API. It lets upper layers attach encryption metadata to bios and lets the block layer decide whether to submit directly to inline hardware or fall back to software crypto.

## Important APIs, Types, And Functions
`enum blk_crypto_mode_num` defines supported modes: invalid, AES-256-XTS, AES-128-CBC-ESSIV, Adiantum, SM4-XTS, and max. `enum blk_crypto_key_type` defines bitflag key types: raw and hardware-wrapped. Size constants are `BLK_CRYPTO_MAX_RAW_KEY_SIZE`, `BLK_CRYPTO_MAX_HW_WRAPPED_KEY_SIZE`, `BLK_CRYPTO_MAX_ANY_KEY_SIZE`, `BLK_CRYPTO_SW_SECRET_SIZE`, `BLK_CRYPTO_MAX_IV_SIZE`, and `BLK_CRYPTO_DUN_ARRAY_SIZE`.

`struct blk_crypto_config` stores mode, data unit size, DUN width, and key type. `struct blk_crypto_key` stores immutable config, log2 data unit size, key size, and key bytes. `struct bio_crypt_ctx` stores a key pointer and starting DUN array. With `CONFIG_BLK_INLINE_ENCRYPTION`, helper APIs include `bio_has_crypt_ctx()`, `bio_crypt_ctx()`, `bio_crypt_set_ctx()`, `bio_crypt_dun_is_contiguous()`, `blk_crypto_init_key()`, `blk_crypto_start_using_key()`, `blk_crypto_evict_key()`, `blk_crypto_config_supported_natively()`, `blk_crypto_config_supported()`, and `blk_crypto_derive_sw_secret()`. `blk_crypto_submit_bio()` wraps `__blk_crypto_submit_bio()` and falls through to `submit_bio()` when appropriate. `bio_crypt_clone()` clones crypt contexts through `__bio_crypt_clone()`.

## Control Flow And State
When inline encryption is enabled, a bio with `bi_crypt_context` carries a key and DUN. `blk_crypto_submit_bio()` checks whether a crypto context exists and whether `__blk_crypto_submit_bio()` handled fallback setup; direct submission proceeds when there is no crypto context or when native hardware support is available. Clone flow copies encryption context only if the source bio has one. Without `CONFIG_BLK_INLINE_ENCRYPTION`, context accessors return false/NULL, keeping call sites buildable but featureless.

State is shared by immutable keys, per-bio crypto contexts, and device profiles/keyslots declared elsewhere. The key lifetime contract is explicit: keys must outlive all bios using them and eviction from all devices.

## Dependencies And Integration Points
The header includes `linux/minmax.h`, `linux/types.h`, `uapi/linux/blk-crypto.h`, `linux/blk_types.h`, and `linux/blkdev.h`. It integrates with `struct bio`, `struct block_device`, request queues, block crypto profiles, filesystems with encrypted data, dm targets, and hardware inline encryption drivers.

## Risks And Test Signals
Risks include freeing keys too early, DUN discontinuity across splits/merges, unsupported crypto configurations, fallback bio allocation failures, hardware-wrapped key misuse, and config-disabled call sites assuming contexts exist. Test signals should include encrypted read/write submission, bio splitting/cloning, DUN contiguity checks, unsupported hardware fallback, memory allocation failure in clone/fallback paths, and eviction after I/O completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-integrity.h -->
# sources/distributed-fs/ceph-client/include/linux/blk-integrity.h

## Purpose
`blk-integrity.h` declares the block-layer data integrity/protection information API. It connects request queues, bios, DMA mapping, metadata buffers, and integrity profiles so devices can verify or generate per-sector metadata.

## Important APIs, Types, And Functions
`enum blk_integrity_flags` defines profile behavior such as no verify, no generate, device capable, reference tags, stacked integrity, and split-interval capability. Always-declared helpers include `blk_integrity_profile_name()`, `queue_limits_stack_integrity()`, and `queue_limits_stack_integrity_bdev()`.

With `CONFIG_BLK_DEV_INTEGRITY`, the header declares `blk_rq_map_integrity_sg()`, `blk_rq_count_integrity_sg()`, `blk_rq_integrity_map_user()`, `blk_get_meta_cap()`, `blk_rq_integrity_dma_map_iter_start()`, and `blk_rq_integrity_dma_map_iter_next()`. Inline helpers expose queue support, disk/bdev integrity profiles, maximum integrity segments, interval and byte calculations, request integrity flag checks, and `rq_integrity_vec()`. Without integrity support, stubs return neutral values or errors.

`enum bio_integrity_action` describes required actions: allocate buffer, check/generate protection information, and zero buffer. `bio_integrity_action()` skips work when the target has no integrity profile or the bio already has integrity metadata; otherwise it calls `__bio_integrity_action()`.

## Control Flow And State
The header gates most behavior on `CONFIG_BLK_DEV_INTEGRITY`. Runtime flow checks queue limits for `integrity.metadata_size`, inspects `REQ_INTEGRITY`, and converts sectors to integrity intervals using `interval_exp`. Request mapping functions operate over request/bio integrity payloads and DMA iterators; action selection is deferred to the implementation when metadata must be synthesized or verified.

State lives in `queue_limits.integrity`, bio integrity payloads, request flags, and DMA iterator state. The header itself does not persist anything.

## Dependencies And Integration Points
It includes `linux/blk-mq.h`, `linux/bio-integrity.h`, and `linux/blk-mq-dma.h`. It integrates with `struct queue_limits` from `blkdev.h`, `struct request` from `blk-mq.h`, `struct bio` from `blk_types.h`, and user ioctls for metadata capabilities.

## Risks And Test Signals
Risks include interval exponent assumptions, division/shift mismatches for non-512-byte intervals, missing stubs in non-integrity builds, DMA iterator errors, integrity segment limits, and failing to allocate or zero metadata buffers. Tests should cover config-enabled and disabled builds, profile stacking, request SG counts, user metadata mapping, `REQ_INTEGRITY` propagation, and action masks for bios with and without preexisting integrity payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-integrity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-mq-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/blk-mq-dma.h

## Purpose
`blk-mq-dma.h` defines DMA mapping iterators for blk-mq requests. It abstracts walking request data or integrity vectors and coalescing them into DMA address ranges, including support for PCI peer-to-peer DMA and IOVA-based coalescing.

## Important APIs, Types, And Functions
`struct blk_map_iter` stores the current `bvec_iter`, current `bio`, bvec array, and whether the iterator is walking integrity data. `struct blk_dma_iter` exposes output `addr` and `len`, peer-to-peer map state, final `blk_status_t status`, and internal `blk_map_iter`.

The main functions are `blk_rq_dma_map_iter_start()` and `blk_rq_dma_map_iter_next()`. `blk_rq_dma_map_coalesce()` returns whether the DMA state represents a single coalesced IOVA range via `dma_use_iova()`. `blk_rq_dma_unmap()` handles teardown: bus-address peer-to-peer mappings need no action, IOVA mappings are destroyed with optional `DMA_ATTR_MMIO`, and non-IOVA mappings report whether manual unmapping is still needed based on `dma_need_unmap()`.

## Control Flow And State
Mapping starts with a request, DMA device, `dma_iova_state`, and iterator. Repeated `*_next()` calls advance the internal bio/bvec state and emit address ranges until false is returned; at that point `iter->status` indicates the terminal error/status. Unmap control branches on the peer-to-peer mapping type and whether an IOVA state was used.

State is transient and caller-owned: DMA address/length outputs, peer-to-peer state, IOVA state, and the iterator cursor. The request's data direction is derived through `rq_dma_dir(req)`.

## Dependencies And Integration Points
The header includes `linux/blk-mq.h` and `linux/pci-p2pdma.h`; it also relies on DMA APIs such as `dma_use_iova()`, `dma_iova_destroy()`, and `dma_need_unmap()`. It is used by block drivers that map requests for hardware submission, and by integrity code for protection metadata mapping.

## Risks And Test Signals
Risks include leaked DMA mappings on partial failure, wrong DMA direction, mishandling peer-to-peer bus addresses vs host-bridge mappings, assuming all segments coalesced, and ignoring `iter->status`. Tests should exercise normal multi-segment mapping, IOVA coalesced mapping, P2PDMA map types, integrity mapping, partial-map failure cleanup, and devices where `dma_need_unmap()` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-mq-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-mq.h -->
# sources/distributed-fs/ceph-client/include/linux/blk-mq.h

## Purpose
`blk-mq.h` declares the multiqueue block request layer. It defines the request object, hardware queue contexts, tag sets, driver callbacks, queue mapping structures, request allocation/completion APIs, requeue/quiesce/freeze helpers, and request data iteration utilities.

## Important APIs, Types, And Functions
Key types include `struct request`, `struct rq_list`, `struct blk_mq_hw_ctx`, `struct blk_mq_queue_map`, `enum hctx_type`, `struct blk_mq_tag_set`, `struct blk_mq_queue_data`, `struct blk_mq_ops`, `struct blk_mq_tags`, `struct req_iterator`, and `struct rq_map_data`. Request flags include `RQF_STARTED`, `RQF_FLUSH_SEQ`, `RQF_MIXED_MERGE`, `RQF_DONTPREP`, scheduler/hash/stat/special-payload/zone-timeout/reserved flags, plus `RQF_NOMERGE_FLAGS`. Request states are `MQ_RQ_IDLE`, `MQ_RQ_IN_FLIGHT`, and `MQ_RQ_COMPLETE`.

Driver callbacks in `blk_mq_ops` include `queue_rq()`, `commit_rqs()`, `queue_rqs()`, budget get/put/token helpers, `timeout()`, `poll()`, `complete()`, hctx/request init and exit hooks, `cleanup_rq()`, `busy()`, `map_queues()`, and optional debugfs display.

Lifecycle APIs include disk/queue allocation (`blk_mq_alloc_disk()`, `blk_mq_alloc_queue()`), tag-set allocation/free, request allocation (`blk_mq_alloc_request()` and hctx-specific variant), request start/end/complete/requeue helpers, queue stop/start/run/delay functions, quiesce/unquiesce, freeze/unfreeze, queue mapping, hardware queue count update, tag iteration, and timeout injection. Data helpers expose request op, direction, ioprio, positions, byte/sector counts, payload bytes, bvec iteration, SG mapping, and clone/execute/map-user/map-kernel operations.

## Control Flow And State
A request flows from allocation from a tag set, through optional scheduler tags, into a hardware context, then to driver `queue_rq()`/`queue_rqs()`, then through completion. State fields track `cmd_flags`, `rq_flags`, tag/internal tag, bio chain, sector and length cursors, timings, physical segment counts, crypto keyslot, deadline, scheduler/private pointers, flush state, and `end_io`. `blk_mq_start_request()` moves a request into flight, completion helpers move it to complete and either batch, direct-complete, remote-complete, or end/free it.

Hardware context state includes dispatch lists, queue state bits, CPU masks, run work, scheduler data, tag sets, wait queues, sysfs/debugfs nodes, CPU hotplug list nodes, and active counts. Tag sets own shared or per-hctx tags, queue maps, locks, SRCU, and update locks. Freeze/quiesce helpers coordinate queue teardown, elevator switching, and resource updates.

## Dependencies And Integration Points
The header includes `linux/blkdev.h`, `linux/sbitmap.h`, lockdep, scatterlist, prefetch, SRCU, write-hint, and rwsem support. It is tightly coupled with `blk_types.h` operations, `blkdev.h` queue/disk state, bio iteration, DMA mapping, I/O schedulers, debugfs, cgroups, zone write plugging, polling, and driver-specific command PDUs placed after `struct request`.

## Risks And Test Signals
Risks include request state races, tag leaks, wrong queue mapping, failing to call budget put on errors, using request fields directly despite cursor comments, mishandling special payloads, batching completions with incompatible handlers, freeze/quiesce deadlocks, and stale queue limits during hctx updates. Tests should cover request allocation/free, queue_rq error returns, batched completion eligibility, timeouts, requeue paths, polling, CPU hotplug queue remapping, shared tag sets, user/kernel request mapping, SG counts, and request clone/unprep behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-mq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-pm.h -->
# sources/distributed-fs/ceph-client/include/linux/blk-pm.h

## Purpose
`blk-pm.h` declares block-layer runtime power-management hooks for request queues. It lets the block layer coordinate queue state before and after runtime suspend/resume.

## Important APIs, Types, And Functions
With `CONFIG_PM`, exported functions are `blk_pm_runtime_init()`, `blk_pre_runtime_suspend()`, `blk_post_runtime_suspend()`, `blk_pre_runtime_resume()`, and `blk_post_runtime_resume()`. Without power management, only `blk_pm_runtime_init()` remains as an empty inline stub. The header forward-declares `struct device` and `struct request_queue`.

## Control Flow And State
The header defines no state. Runtime PM state is stored in `request_queue` fields under `CONFIG_PM` (`dev` and `rpm_status`) and in the PM core. The pre/post hooks are intended to bracket suspend/resume transitions: pre-suspend can block or drain queue activity, post-suspend records success/failure, pre-resume prepares queue state, and post-resume finishes restoration.

## Dependencies And Integration Points
It integrates with `blkdev.h` queue PM fields, `blk-mq` runtime PM request flags (`RQF_PM` and `BLK_MQ_REQ_PM`), and drivers that call the runtime init helper when binding a queue to a device. It intentionally keeps dependencies low through forward declarations.

## Risks And Test Signals
Risks include missing PM stubs for non-PM builds, queue activity racing with suspend, failing to allow PM requests while normal I/O is blocked, and mismatched pre/post calls. Test signals include builds with and without `CONFIG_PM`, suspend/resume under active I/O, PM-only request submission, and error propagation through `blk_post_runtime_suspend()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk_types.h -->
# sources/distributed-fs/ceph-client/include/linux/blk_types.h

## Purpose
`blk_types.h` defines foundational block-layer data structures and constants while deliberately avoiding heavier include cycles. It provides sector units, `struct block_device`, block status codes, `struct bio`, bio flags, request operation encodings, request flags, and helper classifiers.

## Important APIs, Types, And Functions
Sector constants are `SECTOR_SHIFT`, `SECTOR_SIZE`, `PAGE_SECTORS_SHIFT`, `PAGE_SECTORS`, and `SECTOR_MASK`. `struct block_device` stores partition start/size, disk and queue pointers, per-cpu stats, flags (`BD_PARTNO`, `BD_READ_ONLY`, `BD_WRITE_HOLDER`, `BD_HAS_SUBMIT_BIO`, `BD_RO_WARNED`, optional fail flag), device number, mapping, opener/holder/freeze state, metadata, writers, security, and embedded device.

`blk_status_t` values include OK, unsupported, timeout, no space, transport/target/reservation/medium/protection/resource errors, dm requeue, again, device resource, zone open/active resource, offline, duration limit, and invalid alignment/size. `blk_path_error()` classifies errors for failover retry.

`struct bio` stores queue linkage, target bdev, op/flags, ioprio, write hint/stream, status, bvec gap bit, remaining count, vec array/iterator, poll cookie or zone segments, end_io, private data, optional cgroup, crypto and integrity pointers, vector counts, refcount, and bio pool. Bio flags include cloned, chained, quiet, throttled/accounted/remapped, zone write plugging, and zone append emulation. Request operations include read, write, flush, discard, secure erase, zone append/management, write zeroes, and driver private in/out. Request flags cover failfast, sync/meta/prio/nomerge/idle, integrity, FUA, preflush, readahead, background, nowait, polled, allocation cache, swap, driver/filesystem private, atomic writes, and write-zeroes nounmap.

## Control Flow And State
The header supplies inline classifiers: `bio_op()`, `op_is_write()`, `op_is_flush()`, `op_is_sync()`, `op_is_discard()`, `op_is_zone_mgmt()`, and `op_stat_group()`. It does not implement I/O submission; it defines the state that submission, splitting, scheduling, tracing, and drivers mutate. Bio and bdev lifetimes are reference-counted elsewhere, but the fields here are the common persisted in-memory state for block I/O.

## Dependencies And Integration Points
It includes types, bvecs, device, time, and write-hint headers. `blkdev.h`, `blk-mq.h`, crypto, integrity, tracing, cgroup, and filesystem block helpers all depend on these definitions. It forward-declares several structures to keep include dependencies minimal.

## Risks And Test Signals
Risks include op/flag bit overlap, incorrect assumptions about low operation bit meaning direction, bio lifetime/refcount bugs, cgroup/crypto/integrity fields compiled out, and error classification changes affecting multipath retry. Test signals include compile-time flag layout checks, read/write/flush/zone classifier tests, bio clone/reset preservation around `BIO_RESET_BYTES`, status-to-errno mappings, and bdev flag operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blk_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blkdev.h -->
# sources/distributed-fs/ceph-client/include/linux/blkdev.h

## Purpose
`blkdev.h` is the main block-device interface header. It defines disk metadata, queue limits/features, request queue state, block device operations, queue/disk registration APIs, queue limit update helpers, zoned block helpers, plugging, discard/zeroout helpers, bdev open/claim/sync/freeze APIs, I/O accounting, and atomic-write capability helpers.

## Important APIs, Types, And Functions
Top-level constants include `BLKCG_MAX_POLS`, `DISK_MAX_PARTS`, `DISK_NAME_LEN`, partition metadata lengths, disk capability flags (`GENHD_FL_*`), disk events and event flags, integrity checksum types, and block open modes (`BLK_OPEN_*`). `struct gendisk` stores major/minor info, name, events, partition table, part0 bdev, fops, queue, private data, split bioset, flags/state bits (`GD_*`), open mutex/partition count, bdi/sysfs objects, optional zoned fields, cdrom info, badblocks, lockdep, disk sequence, open mode, independent access ranges, and rq-qos mutex. Helpers include `disk_openers()`, `disk_has_partscan()`, `dev_to_disk()`, `disk_to_dev()`, `disk_devt()`, and `blk_validate_block_size()`.

Queue features include write cache, FUA, rotational, add-random, I/O stats, stable writes, synchronous completion, nowait, DAX, polling, zoned, P2PDMA, skip tagset quiesce, atomic writes, and bcache stripe behavior. `struct queue_limits` records feature/flag bits, segment and boundary masks, sector and segment limits, block sizes and topology, discard/secure erase/write zeroes limits, zone append and write granularity, atomic write limits, stream limits, zone resource limits, DMA alignment/padding, and integrity profile.

`struct request_queue` stores driver data, elevator, mq ops, per-cpu software queues, flags, timeouts, depth, refcounts, hardware queue array, usage counter, merge state, queue lock, disk pointer, kobjects, limits, PM state, pm-only count, stats, rq-qos, id, nr_requests, crypto profile, timeout work, cgroup data, requeue state, tracing, flush queue/list, elevator/sysfs/limits locks, unused hctx list, freeze state/locks/waitqueue, tag set, debugfs entries, and RCU head.

`struct block_device_operations` defines driver callbacks: `submit_bio()`, `poll_bio()`, `open()`, `release()`, ioctl/compat ioctl, event checking, native capacity unlock, geometry, read-only change, disk free, swap notification, zone reporting, devnode, unique ID, owner, persistent reservation ops, and alternative GPT sector.

## Control Flow And State
Disk lifecycle flows through allocation (`blk_alloc_disk()` or blk-mq allocation), queue setup, `add_disk()`/`device_add_disk()`, queue registration, I/O submission, media change and capacity updates, then `del_gendisk()` and `put_disk()`. Queue limit updates use `queue_limits_start_update()` to lock and snapshot limits, then `queue_limits_commit_update()`/`queue_limits_commit_update_frozen()` or `queue_limits_cancel_update()`. Queue entry/exit protects active I/O while reconfiguration and zoned metadata updates occur.

I/O helper flow includes `submit_bio_noacct()`, bio splitting to limits, polling, plugging via `blk_start_plug()`/`blk_finish_plug()`, discard/secure erase/zeroout issuing, block-size validation, sync/invalidate/freeze/thaw, and I/O accounting start/end. Zoned helpers compute zone numbers, check straddling, decide when zone write plugging is required, and expose zone capacity/alignment. Atomic-write helpers check queue limits and partition start alignment before advertising min/max units.

State is persistent in `gendisk`, `block_device`, and `request_queue`. Many fields are protected by explicit locks: `open_mutex`, `limits_lock`, `elevator_lock`, `sysfs_lock`, `queue_lock`, freeze locks/waitqueues, cgroup mutex, and debugfs mutex. Feature and queue flags are accessed through bit helpers and limit fields.

## Dependencies And Integration Points
The header includes core kernel list, timer, workqueue, wait, bio, GFP, device number, RCU, percpu refcount, zoned block, scheduler, sbitmap, uuid, xarray, file, and lockdep headers. It integrates with `blk_types.h`, `blk-mq.h`, request queues, elevators, cgroups, rq-qos, tracing, inline crypto, integrity, zoned devices, filesystems/superblocks, partition scanning, sysfs/debugfs, PM, and device-mapper or stacking drivers.

## Risks And Test Signals
Risks include queue limit races, stale capacity/partition state, improper bdev claiming, incorrect feature inheritance in stacked devices, deadlocks between freeze and elevator/limits locks, zone write plugging omissions, unsafe racy feature disable helpers, request queue lifetime/refcount bugs, and config-gated fields used unguarded. Test signals should include disk add/remove, partition scanning suppression, queue limit validation/stacking, block-size changes, discard/zeroout paths, zoned writes and zone management, freeze/thaw/sync, bdev open/claim conflicts, PM-only mode, inline crypto registration, cgroup policy bitmaps, and atomic-write alignment on whole disks vs partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blkdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blkpg.h -->
# sources/distributed-fs/ceph-client/include/linux/blkpg.h

## Purpose
`blkpg.h` exposes block partition table and disk geometry ioctl definitions to kernel code, while adding compatibility structure support for 32-bit userspace on 64-bit kernels.

## Important APIs, Types, And Functions
The header includes `linux/compat.h` and `uapi/linux/blkpg.h`. Under `CONFIG_COMPAT`, it defines `struct blkpg_compat_ioctl_arg` with compat-sized `op`, `flags`, `datalen`, and user pointer `data` fields. The UAPI include supplies the normal `blkpg_ioctl_arg` and operation/data structures.

## Control Flow And State
There are no functions or mutable state. The only behavior is compile-time: compat builds get a layout matching 32-bit userspace pointer and integer sizes; non-compat builds only use the UAPI definitions.

## Dependencies And Integration Points
This header integrates with block ioctl handling in disk/partition management paths, especially add/delete partition operations. It depends on the compat layer to translate userspace pointers safely.

## Risks And Test Signals
Risks include ABI layout drift between native and compat structs, missing compat handling for partition ioctls, and unsafe use of compat user pointers. Test signals include native and 32-bit compat ioctl tests for partition add/delete, structure size checks, and invalid pointer/datalen handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blkpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blktrace_api.h -->
# sources/distributed-fs/ceph-client/include/linux/blktrace_api.h

## Purpose
`blktrace_api.h` declares the kernel side of block I/O tracing. It connects request queues, relay channels, trace setup ioctls, cgroup-aware trace messages, driver-private trace payloads, and request-to-sector formatting helpers.

## Important APIs, Types, And Functions
With `CONFIG_BLK_DEV_IO_TRACE`, `struct blk_trace` stores version, trace state, relay channel, per-cpu sequence and message buffers, action mask, LBA filter range, pid, device, debugfs directory, running list, and dropped count. Exported functions include `blk_trace_ioctl()`, `blk_trace_shutdown()`, `__blk_trace_note_message()`, `blk_add_driver_data()`, `blk_trace_setup()`, `blk_trace_startstop()`, and `blk_trace_remove()`.

Macros `blk_add_cgroup_trace_msg()` and `blk_add_trace_msg()` RCU-read `q->blk_trace` and emit formatted messages when tracing is active. `blk_trace_note_message_enabled()` checks whether notification tracing is enabled. `BLK_TN_MAX_MSG` caps message size. Without tracing config, the API compiles to `-ENOTTY`, no-op, or false stubs. Under `CONFIG_COMPAT`, `struct compat_blk_user_trace_setup` and `BLKTRACESETUP32` define the 32-bit setup ioctl layout.

Always-available helpers are `blk_fill_rwbs()`, `blk_rq_trace_sector()`, and `blk_rq_trace_nr_sectors()`. The sector helpers suppress sector counts for passthrough requests and unset sectors.

## Control Flow And State
Trace message emission is lockless from the caller perspective: enter RCU read-side section, dereference `q->blk_trace`, conditionally emit, then unlock. Setup/start/stop/remove manage relay and debugfs state in implementation code. Runtime trace state persists in `struct blk_trace`, referenced from `request_queue` under `CONFIG_BLK_DEV_IO_TRACE`.

## Dependencies And Integration Points
The header includes `blk-mq.h`, relay, compat, UAPI blktrace definitions, list, and blk types. It integrates with request queues, debugfs/relayfs, cgroup CSS for tagged messages, request tracing, and userspace blktrace tooling.

## Risks And Test Signals
Risks include RCU lifetime bugs, dropped trace accounting, message truncation, compat ioctl layout issues, tracing passthrough requests with bogus sectors, and missing stubs in non-trace builds. Tests should cover trace setup/start/stop/remove, concurrent queue teardown, cgroup trace messages, driver data payloads, compat setup ioctl, LBA/pid/action filters, and non-configured `-ENOTTY` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blktrace_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blockgroup_lock.h -->
# sources/distributed-fs/ceph-client/include/linux/blockgroup_lock.h

## Purpose
`blockgroup_lock.h` provides a small hashed spinlock array for per-block-group locking, originally for ext2/ext3 block group operations. It trades exact one-lock-per-group storage for a fixed number of cacheline-aligned locks.

## Important APIs, Types, And Functions
`NR_BG_LOCKS` is `1` on UP builds and `4 << ilog2(min(NR_CPUS, 32))` on SMP builds. `struct bgl_lock` wraps a `spinlock_t` and is cacheline-aligned in SMP builds. `struct blockgroup_lock` stores an array of `bgl_lock` entries. `bgl_lock_init()` initializes every lock. `bgl_lock_ptr()` selects a lock by hashing `block_group` with `block_group & (NR_BG_LOCKS - 1)`.

## Control Flow And State
The header contains only inline initialization and lookup. Persistent state is the caller-embedded `struct blockgroup_lock`. Lock selection is deterministic and lossy: multiple block groups can map to the same spinlock. The power-of-two lock count makes masking valid.

## Dependencies And Integration Points
It depends on `linux/spinlock.h` and `linux/cache.h`, and uses `NR_CPUS` and `ilog2()` from the broader kernel environment. Filesystem code uses it to protect block group metadata updates without allocating large lock arrays.

## Risks And Test Signals
Risks include lock contention when many hot groups hash to the same lock, assuming unique locks per group, missing initialization before lookup, and compile assumptions around `NR_BG_LOCKS` being a power of two. Test signals include SMP and UP builds, lockdep coverage around block group updates, hash distribution tests, and stress tests with concurrent allocation/free in adjacent block groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/blockgroup_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bma150.h -->
# sources/distributed-fs/ceph-client/include/linux/bma150.h

## Purpose
`bma150.h` defines platform data for the Bosch BMA150 accelerometer driver. It is a small board-configuration header for range, bandwidth, interrupt behavior, and optional IRQ GPIO setup.

## Important APIs, Types, And Functions
`BMA150_DRIVER` names the driver string. Range constants are `BMA150_RANGE_2G`, `BMA150_RANGE_4G`, and `BMA150_RANGE_8G`. Bandwidth constants range from `BMA150_BW_25HZ` through `BMA150_BW_1500HZ`.

`struct bma150_cfg` stores booleans for any-motion, high-G, and low-G interrupts; duration/threshold/hysteresis fields for motion/high-G/low-G; selected range; and selected bandwidth. `struct bma150_platform_data` wraps the config and an optional `irq_gpio_cfg()` callback.

## Control Flow And State
The header has no functions except the board-provided callback pointer. Runtime state is initialized by platform or board code and consumed by the accelerometer driver during probe/configuration. The callback, if provided, lets board code configure the interrupt GPIO before the driver uses it.

## Dependencies And Integration Points
It has no explicit includes, so it relies on included context for `bool`. It integrates with legacy platform-data based device registration and the BMA150 input/IIO driver code.

## Risks And Test Signals
Risks include invalid range/bandwidth enum values, uninitialized threshold/duration fields, missing `bool` type in standalone include contexts, and failing IRQ GPIO setup. Test signals include driver probe with default and custom platform data, interrupt enable paths, invalid board data rejection or clamping, and suspend/resume preserving configured range and bandwidth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bma150.h -->
