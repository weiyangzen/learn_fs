# Research: subset-b-006079

Grouped research for Linux `lib/` and `lib/842/` sources in the ceph-client source snapshot. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_compress.c -->
# sources/distributed-fs/ceph-client/lib/842/842_compress.c

## Purpose
Implements the software compressor for IBM/NX 842 format. It accepts arbitrary input, emits the 842 template stream plus a big-endian CRC32, and exports `sw842_compress()` for kernel compression users that select `CONFIG_842_COMPRESS`.

## APIs, Types, and Functions
The public API is `sw842_compress(const u8 *in, unsigned int ilen, u8 *out, unsigned int *olen, void *wmem)`. The caller supplies scratch memory that must fit `SW842_MEM_COMPRESS`. Internal state lives in `struct sw842_param`: input/output cursors, remaining lengths, bit cursor, cached 8/4/2-byte input fragments, candidate indexes, and three rolling hash tables. `comp_ops` maps each normal template to four actions and the encoded opcode. Important helpers are `add_bits()`, `add_template()`, `add_repeat_template()`, `add_short_data_template()`, `add_zeros_template()`, `add_end_template()`, `check_template()`, `get_next_data()`, `update_hashtables()`, and `process_next()`.

## Control Flow, State, and Persistence
`sw842_compress()` initializes rolling dictionaries for 8-, 4-, and 2-byte matches, rejects non-8-byte input in `strict` mode, then processes full 8-byte groups. It coalesces repeated 8-byte blocks into repeat templates, emits a zeros template for all-zero blocks, otherwise searches `comp_ops` from best to fallback template and writes either literal data fields or dictionary indexes. After each block it updates the ring-indexed hash tables from current input. Remaining 1-7 bytes use the software-only short-data template unless strict mode rejected the buffer. The stream ends with `OP_END`, CRC32, and zero padding to an 8-byte output length. Persistent state is limited to module parameters and optional debugfs counters; compression dictionaries are per-call scratch state.

## Dependencies and Integration
Depends on `842.h` for opcodes and format constants, `842_debugfs.h` for optional counters, `linux/hashtable.h`, unaligned big-endian accessors, CRC32, module parameters, and exported symbol plumbing. It is built by `lib/842/Makefile` when `CONFIG_842_COMPRESS` is set and is selected from `lib/Kconfig`; zswap, crypto/compression wrappers, or architecture NX fallback paths can call the exported function.

## Risks and Test Signals
Risks include bitstream boundary errors in `add_bits()`, output-length accounting near `ENOSPC`, dictionary-index mismatches between compressor and decompressor, non-hardware-compatible short-data templates, CRC endian mismatch, and template-table corruption. The `strict` module parameter changes accepted input shape. Test signals should include round trips through `sw842_decompress()`, buffers of 0-15 bytes, non-8-byte inputs with strict on/off, repeated and zero blocks, every normal template, output buffers that are exactly full or one byte short, CRC mismatch injection, and hardware 842 compatibility checks for strict-mode streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_debugfs.h -->
# sources/distributed-fs/ceph-client/lib/842/842_debugfs.h

## Purpose
Provides optional debugfs instrumentation shared by the 842 compressor and decompressor modules. It exposes per-template counters when the module parameter `template_counts` is enabled.

## APIs, Types, and Functions
This header defines the static module parameter `sw842_template_counts`, atomic counters for normal templates plus repeat, zeros, short-data, and end templates, the debugfs root dentry, and two helpers: `sw842_debugfs_create()` and `sw842_debugfs_remove()`. There are no exported global functions because the header is included directly into each 842 module, making the state module-local.

## Control Flow, State, and Persistence
At module init, the compressor/decompressor call `sw842_debugfs_create()` only if `template_counts` is true. The helper checks `debugfs_initialized()`, creates a directory named by `MODULE_NAME`, and creates writable atomic files for each counter. At exit, `sw842_debugfs_remove()` recursively removes the tree. Counters persist only for the lifetime of the loaded module and are incremented by compression/decompression template paths.

## Dependencies and Integration
Depends on `linux/debugfs.h`, atomic debugfs helpers, `OPS_MAX`, `MODULE_NAME`, and module-parameter support from the including C file. Integration is intentionally header-local so both `842_compress.c` and `842_decompress.c` get independent counters and debugfs directories.

## Risks and Test Signals
Risks are duplicate static definitions if included incorrectly, debugfs root creation failures being non-fatal, and counter ABI changes affecting diagnostic scripts. Test signals include module load with `template_counts=0` and `1`, verifying created debugfs files match all template names, exercising compressor/decompressor paths and observing counters, and unloading modules to confirm recursive cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_decompress.c -->
# sources/distributed-fs/ceph-client/lib/842/842_decompress.c

## Purpose
Implements software decompression for 842 streams. It reconstructs the original byte stream from template opcodes, literal fields, dictionary indexes, repeat/zero/short-data commands, and validates the trailing CRC.

## APIs, Types, and Functions
The exported API is `sw842_decompress(const u8 *in, unsigned int ilen, u8 *out, unsigned int *olen)`. Internal `struct sw842_param` tracks input bit cursor, compressed bytes remaining, output cursor, output start, and output bytes remaining. `decomp_ops` maps template opcodes to four decode actions. Core helpers are `next_bits()`, `do_data()`, `__do_index()`, `do_index()`, and `do_op()`.

## Control Flow, State, and Persistence
The decompressor reads 5-bit opcodes until `OP_END`. Normal opcodes dispatch through `decomp_ops`, copying literal 2/4/8-byte data from the bitstream or copying 2/4/8 bytes from a rolling output FIFO. Index resolution computes a candidate offset from the index and adjusts it into the current FIFO section so it refers to already-produced bytes. `OP_REPEAT` copies the previous 8 bytes `rep + 1` times, `OP_ZEROS` writes eight zero bytes, and `OP_SHORT_DATA` copies 1-7 literal bytes for software-generated non-8-byte inputs. After `OP_END`, it reads the 32-bit CRC and compares it with `crc32_be()` over reconstructed output. State is per-call except optional template counters.

## Dependencies and Integration
Depends on `842.h`, `842_debugfs.h`, unaligned big-endian accessors, CRC32, exported symbol support, and module init/exit. It is compiled by `lib/842/Makefile` under `CONFIG_842_DECOMPRESS`, which selects CRC32 from `lib/Kconfig`. It is the correctness counterpart for `sw842_compress()` and can also consume hardware-compressed streams that use the standard template set.

## Risks and Test Signals
Risks include malformed index offsets pointing before available output, `OP_REPEAT` before any prior block, short-data underflow if output space checks regress, bit-reading over compressed-buffer boundaries, CRC validation rejecting valid streams if endian handling changes, and stream padding being ignored after end. Test signals include round trips from the software compressor, hardware sample streams, all templates, invalid opcodes, out-of-range indexes, repeat-at-start rejection, small output buffers, truncated compressed input, corrupt CRC, and optional debugfs counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/Makefile -->
# sources/distributed-fs/ceph-client/lib/842/Makefile

## Purpose
Builds the 842 compression subdirectory objects according to kernel configuration.

## APIs, Types, and Functions
The file has two object rules: `obj-$(CONFIG_842_COMPRESS) += 842_compress.o` and `obj-$(CONFIG_842_DECOMPRESS) += 842_decompress.o`. It defines no source-level APIs.

## Control Flow, State, and Persistence
Kbuild includes this directory when the parent `lib/Makefile` adds `842/` for either 842 option. The rules independently compile the compressor and decompressor, allowing one direction to be enabled without the other. There is no runtime state.

## Dependencies and Integration
Depends on parent `lib/Makefile` recursion and `lib/Kconfig` symbols. Both selected objects depend on `842.h`; each object includes `842_debugfs.h` and gets its own module metadata.

## Risks and Test Signals
Risks are configuration skew where a consumer expects both compression and decompression but selects only one, or missing parent recursion rules preventing this Makefile from being reached. Test signals include build matrices for `CONFIG_842_COMPRESS=m/y`, `CONFIG_842_DECOMPRESS=m/y`, both enabled, and neither enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/Kconfig -->
# sources/distributed-fs/ceph-client/lib/Kconfig

## Purpose
Declares kernel configuration symbols for generic library routines. In this subset it governs compression libraries, BCH/Reed-Solomon support, ASN.1, associative arrays, generic atomics, GCC helper routines, bootconfig embedding, and many infrastructure helpers used throughout the kernel.

## APIs, Types, and Functions
The API is Kconfig symbols rather than C functions. Important symbols for the researched files include `842_COMPRESS`, `842_DECOMPRESS`, `BCH`, `BCH_CONST_PARAMS`, `BCH_CONST_M`, `BCH_CONST_T`, `ASSOCIATIVE_ARRAY`, `GENERIC_ATOMIC64`, `ASN1_ENCODER`, `GENERIC_LIB_ASHLDI3`, `GENERIC_LIB_ASHRDI3`, `AUDIT_GENERIC`, `AUDIT_COMPAT_GENERIC`, `BITREVERSE`, `BOOT_CONFIG`, `BOOT_CONFIG_EMBED`, and `MEM_ALLOC_PROFILING`-related selections from other Kconfig fragments.

## Control Flow, State, and Persistence
Kconfig evaluation determines which library objects are compiled and which dependency symbols are selected. Compression options select lower-level CRC or companion libraries as needed. BCH can be built generically or specialized at compile time by `BCH_CONST_PARAMS`, which hardwires field order and correction strength for optimized code. The file also sources subordinate Kconfig trees for math, crypto, raid, xz, vDSO, fonts, and DMA. Persistent state is the generated `.config`; runtime behavior follows selected object inclusion and static key defaults in C code.

## Dependencies and Integration
This file integrates with the top-level kernel configuration system and the parent build. Its symbols are consumed by `lib/Makefile` and by drivers/filesystems that `select` library capabilities. `842_*` select CRC32; `BCH` selects `BITREVERSE`; `SIGNATURE` selects SHA1 and MPILIB; `ASN1_ENCODER` controls `asn1_encoder.o`.

## Risks and Test Signals
Risks include hidden symbols without prompts being mis-selected by drivers, dependency omissions causing link failures, constant BCH parameters not matching driver requests, and symbols allowing incompatible partial feature sets. Test signals include `allyesconfig`, `allmodconfig`, `randconfig`, build tests for each selected object, and targeted configs enabling 842, BCH constant/generic modes, ASN.1 encoder/decoder, generic atomic64, and GCC helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/Makefile -->
# sources/distributed-fs/ceph-client/lib/Makefile

## Purpose
Defines the Kbuild object graph for the kernel generic library directory. It selects always-built helper libraries, conditionally built test modules, architecture fallback helpers, compression subdirectories, sanitizer instrumentation controls, generated sources, and bootconfig embedding artifacts.

## APIs, Types, and Functions
The "API" is Kbuild variables and targets: `lib-y`, `obj-y`, `obj-$(CONFIG_...)`, `lib-$(CONFIG_...)`, per-object flags such as `CFLAGS_string.o`, sanitizer disables like `KASAN_SANITIZE_stackdepot.o := n`, generated target rules for `default.bconf` and `oid_registry_data.c`, and recursion into subdirectories such as `842/`, `zlib_*`, `lzo/`, `lz4/`, `zstd/`, `xz/`, `raid6/`, `kunit/`, and `tests/`.

## Control Flow, State, and Persistence
Kbuild expands this Makefile after configuration. Core objects such as `argv_split.o`, `bcd.o`, `bitmap.o`, `bitmap-str.o`, and `base64.o` are always included. Feature-selected objects include `alloc_tag.o`, `assoc_array.o`, `atomic64.o`, `asn1_decoder.o`, `asn1_encoder.o`, `bch.o`, `audit.o`, `bitrev.o`, `ashldi3.o`, and `ashrdi3.o`. Generated artifacts are produced from configured inputs, for example embedded bootconfig data from `CONFIG_BOOT_CONFIG_EMBED_FILE`. Runtime persistence is not in this file, but build inclusion determines which exported symbols and initcalls exist.

## Dependencies and Integration
Depends on Kbuild, `lib/Kconfig`, compiler feature variables, sanitizer/profiler infrastructure, and generated-file helper macros such as `filechk`. It integrates nearly every kernel subsystem with shared library code and test modules, so object names and config symbols must remain aligned with declarations in Kconfig and exported symbols in source.

## Risks and Test Signals
Risks include object duplication between `lib-y` and `obj-y`, missing sanitizer opt-outs for low-level code, generated target dependency drift, and config symbols selecting source files without required dependencies. Test signals include `make lib/` under multiple configs, `randconfig` link tests, bootconfig embedding builds, OID registry generation, sanitizer builds, and module builds for conditional test objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/alloc_tag.c -->
# sources/distributed-fs/ceph-client/lib/alloc_tag.c

## Purpose
Implements memory allocation profiling support based on code tags. It exposes allocation-site accounting through `/proc/allocinfo`, manages page allocation tag references, handles module allocation tag sections, and controls boot/sysctl toggles for memory profiling.

## APIs, Types, and Functions
Important exports and globals include `mem_alloc_profiling_key`, `mem_profiling_compressed`, `kernel_tags`, `alloc_tag_ref_mask`, `alloc_tag_ref_offs`, `alloc_tag_top_users()`, `pgalloc_tag_split()`, `pgalloc_tag_swap()`, and `page_alloc_tagging_ops`. Major internal functions are seq-file callbacks for `/proc/allocinfo`, `shutdown_mem_profiling()`, `alloc_tag_sec_init()`, module tag area helpers under `CONFIG_MODULES`, early parameter parsing in `setup_early_mem_profiling()`, optional debug early-PFN tracking, sysctl registration, and `alloc_tag_init()`.

## Control Flow, State, and Persistence
Boot state starts from config defaults and the early parameter `sysctl.vm.mem_profiling`. `alloc_tag_sec_init()` initializes compressed tag indexing by locating allocation-tag sections and mapping them into spare page-flag bits; otherwise page extension storage is requested through `page_alloc_tagging_ops`. `alloc_tag_init()` creates `/proc/allocinfo`, reserves module tag virtual memory, and registers the codetag type. For modules, a maple tree tracks reserved tag ranges, grows the backing `execmem_vmap()` area, assigns percpu counters on module load, and marks ranges unloaded until counters reach zero. `/proc/allocinfo` iterates codetags under the codetag module-list lock and prints bytes/calls plus tag text. Persistent state is runtime-only: static keys, proc/sysctl visibility, codetag sections, percpu counters, module range map, and page tag references.

## Dependencies and Integration
Depends on `linux/alloc_tag.h`, codetag infrastructure, page extension and page-allocation tag helpers, procfs, sysctl, module loader callbacks, maple tree, KASAN vmalloc shadow setup, kmemleak, kallsyms, static keys, and RCU. It is built by `lib/Makefile` under `CONFIG_MEM_ALLOC_PROFILING`.

## Risks and Test Signals
Risks are high because this code touches allocation and module unload paths. Important risks include static-key state diverging from `mem_profiling_support`, compressed tag count exceeding spare page-flag capacity, module tag virtual space exhaustion, leaked percpu counters for unloaded modules with live allocations, races while clearing early PFN tag refs in debug mode, and proc/sysctl toggles after shutdown. This snapshot also shows suspicious duplicated source lines around `kallsyms_lookup_name()` and `if (!mod)`, which should be treated as source-integrity/build-risk signals. Test signals include boot with profiling disabled/enabled/compressed/never, `/proc/allocinfo` format version checks, sysctl write permissions, module load/unload with outstanding allocations, page split/swap tag propagation, KASAN/module shadow growth, page_ext initialization, and stress under allocation-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/alloc_tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/argv_split.c -->
# sources/distributed-fs/ceph-client/lib/argv_split.c

## Purpose
Provides a small helper for splitting a whitespace-delimited kernel string into a NULL-terminated argv-style array.

## APIs, Types, and Functions
Exports `argv_split(gfp_t gfp, const char *str, int *argcp)` and `argv_free(char **argv)`. Internal `count_argc()` counts transitions from whitespace to non-whitespace using `isspace()`.

## Control Flow, State, and Persistence
`argv_split()` copies the source with `kstrndup(..., KMALLOC_MAX_SIZE - 1)` to avoid races with mutable sysctl/user-provided backing storage, counts tokens, allocates `argc + 2` pointers, stores the backing string in the hidden pointer immediately before the returned argv, then walks the copy, replacing whitespace with NUL bytes and recording starts of tokens. `argv_free()` expects the returned pointer, steps back one slot, frees the backing string, then frees the pointer array. There is no persistent state.

## Dependencies and Integration
Depends on kernel ctype, slab allocation, string helpers, and export support. Callers are kernel parsers that need simple whitespace splitting without shell quoting.

## Risks and Test Signals
Risks include callers forgetting to use `argv_free()`, passing a pointer not returned by `argv_split()` to `argv_free()`, expecting quote or escape handling, and very large input allocation failure. Test signals include empty/whitespace-only input, multiple whitespace classes, embedded tabs/newlines, NULL `argcp`, allocation-failure injection, and round-trip freeing under KASAN/KMEMLEAK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/argv_split.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashldi3.c -->
# sources/distributed-fs/ceph-client/lib/ashldi3.c

## Purpose
Provides the generic libgcc-style 64-bit arithmetic left shift helper `__ashldi3()` for architectures or compiler modes lacking a native helper.

## APIs, Types, and Functions
Exports `long long notrace __ashldi3(long long u, word_type b)`. It uses `DWunion` from `linux/libgcc.h` to access low and high 32-bit halves.

## Control Flow, State, and Persistence
If shift count is zero, it returns the input. Otherwise it computes `bm = 32 - b`. For shifts of 32 or more, the low half becomes zero and the high half is the old low half shifted by `b - 32`. For smaller shifts, carries from the low half fill the high half while the low half shifts left. There is no state; this is pure arithmetic.

## Dependencies and Integration
Depends on `linux/libgcc.h`, `linux/export.h`, and `notrace` because compiler-emitted helpers may be used from tracing-sensitive paths. Built when `CONFIG_GENERIC_LIB_ASHLDI3` is selected.

## Risks and Test Signals
Risks include undefined behavior for unsupported shift counts if callers/compiler ever pass values outside the expected 0-63 range, and ABI mismatches for `DWunion` layout. Test signals include compiler helper selftests on 32-bit targets, shifts by 0, 1, 31, 32, 33, 63, negative input bit patterns, and tracing builds verifying no instrumentation recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashldi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashrdi3.c -->
# sources/distributed-fs/ceph-client/lib/ashrdi3.c

## Purpose
Provides the generic libgcc-style 64-bit arithmetic right shift helper `__ashrdi3()` for targets that need a kernel-local implementation.

## APIs, Types, and Functions
Exports `long long notrace __ashrdi3(long long u, word_type b)`. It uses `DWunion` to manipulate signed high and unsigned low 32-bit halves.

## Control Flow, State, and Persistence
Shift by zero returns the input. For shifts of 32 or more, the high half is sign-filled from the old high sign bit and the low half receives the old high half shifted by `b - 32`. For smaller shifts, the high half is arithmetically shifted right and carries from high bits are ORed into the low half. There is no mutable state.

## Dependencies and Integration
Depends on `linux/libgcc.h` and export support. Built when `CONFIG_GENERIC_LIB_ASHRDI3` is selected, typically for 32-bit architectures without the helper supplied elsewhere.

## Risks and Test Signals
Risks include sign-extension mistakes, shift-count assumptions, and mismatch with compiler expectations for helper calling convention. Test signals include positive and negative 64-bit values shifted by 0, 1, 31, 32, 33, and 63, cross-compiler builds, and comparing results against native C arithmetic on test platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashrdi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/asn1_decoder.c -->
# sources/distributed-fs/ceph-client/lib/asn1_decoder.c

## Purpose
Implements a bytecode-driven ASN.1 BER/DER/CER decoder. It walks encoded input according to a machine generated by `asn1_compiler` and invokes caller-supplied action callbacks for matched elements.

## APIs, Types, and Functions
Exports `asn1_ber_decoder(const struct asn1_decoder *decoder, void *context, const unsigned char *data, size_t datalen)`. Internal `asn1_op_lengths[]` describes bytecode instruction sizes. `asn1_find_indefinite_length()` scans nested indefinite-length constructed elements. The decoder uses fixed stacks for constructed objects and jump/return bytecode calls.

## Control Flow, State, and Persistence
The main loop fetches an opcode, optionally matches a tag and length from input, pushes constructed boundaries, and handles match, skip, action, jump, return, end-of-sequence/set, and complete operations. Primitive matches advance the data pointer by element length; constructed matches restrict `datalen` until the corresponding end opcode validates exact consumption or indefinite-length EOC. Action callbacks receive context, header length, tag, data pointer, and element length. State is local to the decode call: program counter, data cursor, tag/length flags, constructed stack, jump stack, and last-match flags. It enforces `datalen <= 65535`, no long-form tags, at most two length bytes in the main parser, and stack depths of ten.

## Dependencies and Integration
Depends on `linux/asn1_decoder.h`, generated `linux/asn1_ber_bytecode.h`, errno, module/export infrastructure, and caller-provided `struct asn1_decoder` tables. It is built under `CONFIG_ASN1` and used by key, certificate, crypto, and security parsers.

## Risks and Test Signals
Risks include malformed length handling, unsupported long tags, constructed stack overflow, jump stack overflow, action callbacks trusting unvalidated semantic content, SET limitations, and rejecting valid but unsupported BER forms. Test signals include DER certificates/keys, indefinite-length constructed data, malformed EOC, length overrun, long tags, nested constructed depth, optional fields and skip paths, callback error propagation, and fuzzing of machine/data pairs for `-EBADMSG` without overread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/asn1_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/asn1_encoder.c -->
# sources/distributed-fs/ceph-client/lib/asn1_encoder.c

## Purpose
Provides simple ASN.1 BER/DER/CER encoder primitives for positive integers, object identifiers, context-specific tags, octet strings, sequences, and booleans.

## APIs, Types, and Functions
Exports `asn1_encode_integer()`, `asn1_encode_oid()`, `asn1_encode_tag()`, `asn1_encode_octet_string()`, `asn1_encode_sequence()`, and `asn1_encode_boolean()`. Internal helpers are `asn1_encode_oid_digit()` for base-128 OID arcs and `asn1_encode_length()` for short and long-form lengths up to `0xffffff`.

## Control Flow, State, and Persistence
Each encoder accepts a current output pointer and one-past-end pointer and returns the next write position or `ERR_PTR()`. The functions propagate existing error pointers, validate minimum space, write tag and length, then copy or encode payload. Integer encoding rejects negative values and prepends a zero byte when needed to keep positive two's-complement form. OID encoding requires 2-32 arcs and encodes the first two arcs as `oid[0] * 40 + oid[1]`. Tag and sequence helpers support two-pass in-place encoding by first reserving tag/length with negative length and later recoding a known length by stepping back two bytes. No state persists beyond the caller's buffer.

## Dependencies and Integration
Depends on `linux/asn1_encoder.h` tag macros, `linux/bug.h`, string helpers, module/export support, and consumers that build ASN.1 structures for keys, signatures, or protocol payloads. Built with `CONFIG_ASN1_ENCODER`.

## Risks and Test Signals
Risks include limited negative-integer support, short-tag-only context tags, in-place recoding limited to <=127 bytes, OID first-arc semantic validation being left to callers, and length handling above supported range. Test signals include encoding known DER fixtures, zero and high-bit positive integers, invalid negative integer calls, OIDs with multi-byte arcs, buffer-boundary failures, sequence/tag two-pass recoding, and decode/encode round trips through `asn1_ber_decoder()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/asn1_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/assoc_array.c -->
# sources/distributed-fs/ceph-client/lib/assoc_array.c

## Purpose
Implements the generic RCU-friendly associative array used for key-indexed object collections. It provides lockless read-side find/iterate support while writers precompute edit scripts and publish updates atomically.

## APIs, Types, and Functions
Exports `assoc_array_iterate()`, `assoc_array_find()`, `assoc_array_destroy()`, `assoc_array_insert()`, `assoc_array_insert_set_object()`, `assoc_array_delete()`, `assoc_array_clear()`, `assoc_array_apply_edit()`, `assoc_array_cancel_edit()`, and `assoc_array_gc()`. Internal types include `assoc_array_walk_result`, `assoc_array_walk_status`, deletion collapse context, and metadata nodes/shortcuts from `assoc_array_priv.h`.

## Control Flow, State, and Persistence
Readers walk the root pointer through nodes and shortcuts using key chunks supplied by caller ops. `assoc_array_find()` lands at a terminal node and compares leaves. Iteration performs a two-pass node traversal: leaves first, then metadata, so concurrent reshapes do not miss objects, though duplicates are possible. Inserts walk to an empty tree, terminal node, or wrong shortcut, allocate needed nodes/shortcuts ahead of time, and return an edit script. Deletes clear a leaf and may collapse small subtrees. `assoc_array_apply_edit()` publishes leaf, parent-slot, back-pointer, and root changes with write barriers, adjusts leaf counts up the ancestry, and defers cleanup through RCU. GC duplicates the tree while filtering leaves through a callback, compresses sparse nodes, and swaps in the new root. State persists in caller-owned `struct assoc_array`, metadata allocations, leaf counts, and RCU-delayed destruction.

## Dependencies and Integration
Depends on `linux/assoc_array_priv.h`, RCU, slab allocation, pointer tagging helpers, and caller-provided `struct assoc_array_ops` for key extraction/comparison, object retention, and object freeing. Used by keyrings and other kernel indexes needing concurrent reads.

## Risks and Test Signals
Risks include incorrect caller locking around edit construction/application, RCU misuse by readers, pointer-tagging alignment assumptions, tree corruption from parent/back-pointer mistakes, leaf-count drift, duplicate iteration surprises, and allocation failure during complex splits. This snapshot also contains duplicated source text in cleanup logic, a source-integrity signal to verify with compilation. Test signals include insert/find/delete/replace, shortcut split cases with long common prefixes, full-node splits, GC retention and discard paths, concurrent RCU readers under writer updates, cancellation after allocation failure, KASAN/RCU stall detection, and keyring regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/assoc_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64.c -->
# sources/distributed-fs/ceph-client/lib/atomic64.c

## Purpose
Provides a generic 64-bit atomic operation implementation using hashed spinlocks for architectures without native 64-bit atomic instructions.

## APIs, Types, and Functions
Exports `generic_atomic64_read()`, `generic_atomic64_set()`, generated add/sub/and/or/xor operations, return variants, fetch variants, `generic_atomic64_dec_if_positive()`, `generic_atomic64_cmpxchg()`, `generic_atomic64_xchg()`, and `generic_atomic64_fetch_add_unless()`. Internal state is an array of 16 cacheline-aligned `arch_spinlock_t` locks.

## Control Flow, State, and Persistence
`lock_addr()` hashes an `atomic64_t *` address to a lock. Every operation disables local interrupts, locks the hashed spinlock, reads/modifies `v->counter`, unlocks, and restores interrupts. Return/fetch variants differ only in whether they return the updated or previous value. `dec_if_positive()` writes only if decrement stays non-negative; `cmpxchg()` and `fetch_add_unless()` conditionally modify based on old value. Persistent state is the static lock array; atomic values are caller-owned.

## Dependencies and Integration
Depends on architecture spinlocks, local IRQ save/restore, cacheline sizing, `atomic64_t`, and export support. Built under `CONFIG_GENERIC_ATOMIC64` and expected to satisfy generic atomic64 API calls.

## Risks and Test Signals
Risks include lock hash contention, deadlock if used where local IRQ disabling is insufficient, memory-ordering expectations for atomic API variants, and mismatches between generic wrappers and architecture-specific atomic semantics. Test signals include `atomic64_test.c`, LKMM-style atomic tests, SMP stress with multiple atomic64 variables sharing locks, interrupt-context use, and compare/exchange/add-unless edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64_test.c -->
# sources/distributed-fs/ceph-client/lib/atomic64_test.c

## Purpose
Provides a load-time testsuite for `atomic_t` and `atomic64_t` operations, especially the generic 64-bit atomic implementation.

## APIs, Types, and Functions
The module defines test macros for plain, return, fetch, exchange, compare-exchange, increment, and decrement families across relaxed/acquire/release variants. Functions are `test_atomic()`, `test_atomic64()`, `test_atomics_init()`, and an empty `test_atomics_exit()`.

## Control Flow, State, and Persistence
On module init, it runs deterministic checks against known constants. Each macro initializes an atomic variable, performs an operation, calculates the expected C result, and uses `BUG_ON()` or `WARN()` when the observed value or return differs. On x86 it prints platform feature information for CX8 and SSE. There is no persistent state after init other than module load status.

## Dependencies and Integration
Depends on `linux/atomic.h`, init/module support, BUG/WARN helpers, and optional x86 CPU feature headers. Built by `lib/Makefile` when `CONFIG_ATOMIC64_SELFTEST` is set.

## Risks and Test Signals
Risks include tests being destructive because `BUG_ON()` can crash a system, limited coverage of concurrency and memory ordering, and architecture-specific feature print assumptions. Its own pass/fail output is the primary signal; additional useful signals are running under generic atomic64 configs, native atomic64 architectures, SMP stress, KCSAN, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/audit.c -->
# sources/distributed-fs/ceph-client/lib/audit.c

## Purpose
Provides generic audit syscall classification and syscall-class registration for architectures that use `CONFIG_AUDIT_GENERIC`.

## APIs, Types, and Functions
Exports `audit_classify_arch(int arch)` and `audit_classify_syscall(int abi, unsigned syscall)`. Internal arrays define directory-write, read, write, attribute-change, and signal syscall classes by including architecture-generic audit lists. `audit_classes_init()` registers native and optional compat class arrays.

## Control Flow, State, and Persistence
`audit_classify_arch()` returns whether the audit architecture is compat. `audit_classify_syscall()` routes compat ABIs to `audit_classify_compat_syscall()` and otherwise special-cases open, openat, socketcall, execve/execveat, and openat2 before returning `AUDITSC_NATIVE`. The initcall registers class arrays with the audit subsystem. Registered classes persist for the lifetime of the kernel.

## Dependencies and Integration
Depends on `linux/audit.h`, `asm/unistd.h`, asm-generic audit class include files, optional `CONFIG_AUDIT_COMPAT_GENERIC`, and audit registration APIs. Built through `lib/Makefile` under `CONFIG_AUDIT_GENERIC`.

## Risks and Test Signals
Risks include syscall-number availability differences across architectures, compat classification drift, missing new syscall special cases, and class arrays not matching arch syscall tables. Test signals include audit rule tests for open/openat/openat2/execve/socketcall, compat 32-bit syscall auditing, class-based audit filters, and build tests on architectures with and without each `__NR_*` define.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/base64.c -->
# sources/distributed-fs/ceph-client/lib/base64.c

## Purpose
Implements Base64 encoding and decoding with standard, URL-safe, and IMAP alphabets, with optional padding support.

## APIs, Types, and Functions
Exports `base64_encode(const u8 *src, int srclen, char *dst, bool padding, enum base64_variant variant)` and `base64_decode(const char *src, int srclen, u8 *dst, bool padding, enum base64_variant variant)`. Static data includes `base64_tables` and 256-entry reverse maps generated by macros for each variant.

## Control Flow, State, and Persistence
Encoding processes full 3-byte groups into four characters, then handles one- or two-byte tails and optional `=` padding. Decoding processes full 4-character groups via reverse maps, detects negative values for invalid characters or padding, and supports unpadded 2- or 3-character tails when `padding` is false. It returns output length or `-1` for invalid input. The only state is immutable lookup tables.

## Dependencies and Integration
Depends on kernel types, string/kernel helpers, `linux/base64.h`, and export support. Used by filesystems, crypto/key code, protocol helpers, and other consumers needing non-MIME Base64 without line wrapping.

## Risks and Test Signals
Risks include unchecked `variant` index from callers, destination buffer sizing being caller responsibility, strict padding behavior rejecting mixed forms, and signed arithmetic in invalid-character detection. Test signals include RFC4648 vectors, URL-safe and IMAP alphabet vectors, padded and unpadded tails of length 1/2/3, invalid characters, malformed padding, zero-length input, and round trips for binary data with high bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/base64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bcd.c -->
# sources/distributed-fs/ceph-client/lib/bcd.c

## Purpose
Provides binary-coded decimal conversion helpers used by RTCs, firmware tables, and legacy hardware interfaces.

## APIs, Types, and Functions
Exports `_bcd2bin(unsigned char val)` and `_bin2bcd(unsigned val)`. Public wrappers/macros are declared in `linux/bcd.h`.

## Control Flow, State, and Persistence
`_bcd2bin()` converts the low nibble plus ten times the high nibble. `_bin2bcd()` computes decimal tens with `(val * 103) >> 10`, then packs tens into the high nibble and remainder into the low nibble. There is no state.

## Dependencies and Integration
Depends on `linux/bcd.h` and export support. The helpers are always built by `lib/Makefile` as `bcd.o`.

## Risks and Test Signals
Risks include callers passing values outside valid BCD or binary 0-99 ranges; the helpers do not validate and will produce mechanically packed results. Test signals include conversions for 0, 9, 10, 42, 99, invalid BCD nibbles, and RTC driver round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bch.c -->
# sources/distributed-fs/ceph-client/lib/bch.c

## Purpose
Implements a runtime-configurable binary BCH error-correction library. It can generate ECC parity bytes, decode data/ECC syndromes, and locate bit errors for callers such as NAND flash drivers.

## APIs, Types, and Functions
Exports `bch_init()`, `bch_encode()`, `bch_decode()`, and `bch_free()`. Key internal types include `struct gf_poly` and `struct gf_poly_deg1`; public state is in `struct bch_control` from `linux/bch.h`. Internal helpers cover bit swapping, ECC byte/word conversion, Galois field arithmetic, syndrome computation, Berlekamp-Massey error locator generation, low-degree root solvers, Berlekamp Trace factorization, optional Chien search, generator polynomial construction, GF table construction, mod-8 encoding table construction, and degree-2 base generation.

## Control Flow, State, and Persistence
`bch_init()` validates `m` and `t`, optionally enforces `CONFIG_BCH_CONST_PARAMS`, chooses or validates a primitive polynomial, allocates tables/buffers, builds GF log/power tables, computes the generator polynomial, builds encoding lookup tables, and prepares root-solving bases. `bch_encode()` loads existing ECC or clears it, processes unaligned bytes, then aligned 32-bit words through four precomputed mod-8 tables, and stores parity bytes. `bch_decode()` accepts raw data plus received ECC, received/calculated ECC, XORed ECC, or hardware syndromes; it computes syndromes if needed, builds the error locator polynomial, finds roots, and maps raw roots into caller-facing bit locations. `bch_free()` releases all allocations. State persists in the allocated `bch_control` and is intended to be initialized during driver setup, not fast paths.

## Dependencies and Integration
Depends on kernel allocation, bit operations, bit reversal, byteorder helpers, `linux/bch.h`, Kconfig options `BCH`, `BCH_CONST_PARAMS`, `BCH_CONST_M`, and `BCH_CONST_T`. NAND/MTD ECC engines and other storage code integrate by keeping a `bch_control`, calling encode/decode for page data, and correcting returned bit locations themselves.

## Risks and Test Signals
Risks include parameter mismatch under constant-parameter builds, stack/table bounds for large `m*t`, primitive polynomial validity, caller interpretation of data-vs-ECC error locations, bit order controlled by `swap_bits`, and performance cost of initialization. This snapshot contains suspicious duplicated source text in the degree-2 root path, making compile and algorithm regression tests especially important. Test signals include known BCH vectors for multiple `(m,t)`, NAND page ECC correction up to `t` bits, uncorrectable error returns, `swap_bits` variants, hardware syndrome input, invalid parameter rejection, allocation-failure cleanup, and comparison against Chien-search/reference implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap-str.c -->
# sources/distributed-fs/ceph-client/lib/bitmap-str.c

## Purpose
Implements string and user-buffer conversion helpers for kernel bitmaps, including hex bitmask parsing, decimal list/range parsing, and sysfs-friendly printing.

## APIs, Types, and Functions
Exports `bitmap_parse_user()`, `bitmap_print_to_pagebuf()`, `bitmap_print_bitmask_to_buf()`, `bitmap_print_list_to_buf()`, `bitmap_parselist()`, `bitmap_parselist_user()`, and `bitmap_parse()`. Internal `struct region` represents list ranges with optional used/group pattern syntax. Helpers include region find/parse/check/set routines, number parsing with `N` as the last-bit token, reverse hex chunk parsing, and buffered printing through `kasprintf()` plus `memory_read_from_buffer()`.

## Control Flow, State, and Persistence
User parsers copy user buffers with `memdup_user_nul()` before delegating. `bitmap_parselist()` clears the output mask, repeatedly finds comma/whitespace-separated regions, parses single bits, ranges, `all`, `N`, and `start-end:used/group` patterns, validates bounds, then sets selected bits. `bitmap_parse()` walks a hex bitmask string from right to left in comma-separated 32-bit chunks, writing host-order u32 chunks into the bitmap and clearing/validating tail bits beyond `nmaskbits`. Print helpers format either `%*pb` hex masks or `%*pbl` lists; bin-attribute variants support offset/count at the cost of allocating the full string each call. No persistent state is owned.

## Dependencies and Integration
Depends on bitmap core helpers, ctype, errno, user-copy helpers, hex conversion, page offsets, `kstrtox` internals, and printk `%*pb/%*pbl` formatting. Used heavily by sysfs/procfs cpumask and nodemask interfaces.

## Risks and Test Signals
Risks include confusing byte/character offsets with bit offsets in bin-attribute printers, partial list output being non-parseable, integer overflow in list parameters, dynamic `N` values changing with bitmap width, big-endian 64-bit u32 chunk ordering, and accepting empty comma groups in hex parser. Test signals include list forms `all`, `N`, ranges, patterns such as `0-1023:2/256`, overflow and out-of-range values, whitespace/comma edge cases, big-endian parse/print fixtures, user-copy fault injection, and sysfs bin-attribute partial reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap-str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap.c -->
# sources/distributed-fs/ceph-client/lib/bitmap.c

## Purpose
Provides core generic bitmap operations for equality, set logic, shifting, cutting, setting/clearing, allocation, remapping, NUMA mapping, and array conversion.

## APIs, Types, and Functions
Exports many helpers including `__bitmap_equal()`, `__bitmap_or_equal()`, `__bitmap_complement()`, `__bitmap_shift_right()`, `__bitmap_shift_left()`, `bitmap_cut()`, `__bitmap_and()`, `__bitmap_or()`, `__bitmap_xor()`, `__bitmap_andnot()`, `__bitmap_replace()`, `__bitmap_intersects()`, `__bitmap_subset()`, weight helpers, `__bitmap_set()`, `__bitmap_clear()`, `bitmap_find_next_zero_area_off()`, `bitmap_remap()`, `bitmap_bitremap()`, optional `bitmap_onto()` and `bitmap_fold()` under `CONFIG_NUMA`, allocation/devm allocation helpers, and 32/64-bit array conversion helpers.

## Control Flow, State, and Persistence
Most operations iterate over full `unsigned long` words and mask the final partial word with `BITMAP_LAST_WORD_MASK()` when results must ignore unused tail bits. Shift helpers handle word and intra-word offsets separately. `bitmap_cut()` removes a bit range and shifts later bits downward. Set/clear helpers build first/last masks and apply whole words between. `bitmap_find_next_zero_area_off()` scans for aligned zero ranges, retrying after occupied bits. Remap functions use the ordinal of set bits in an old-domain bitmap to map into a new-range bitmap, with modulo wrapping if the new map is smaller. Allocation helpers wrap `kmalloc_array()` and devres cleanup. Array conversion handles `BITS_PER_LONG` 32/64 differences and clears tail bits. State is entirely caller-owned except devm cleanup registrations.

## Dependencies and Integration
Depends on `linux/bitmap.h`, bitops/find-bit helpers, device-managed resources, slab allocation, export support, and NUMA configuration. It is always built by `lib/Makefile` and underpins cpumasks, nodemasks, ID maps, drivers, filesystems, and scheduler/resource code.

## Risks and Test Signals
Risks include in-place use where not supported (`bitmap_remap()`, `bitmap_onto()`, `bitmap_fold()` early-return), tail-bit mishandling, zero-size or shift >= nbits edge cases, modulo-by-zero if callers misuse `bitmap_fold()` with `sz == 0`, alignment arithmetic overflow in zero-area search, and endian/word-size conversion mistakes. Test signals include `CONFIG_TEST_BITMAP`, random bitmap algebra property tests, partial-word boundaries, overlapping source/destination cases, 32-bit and 64-bit builds, NUMA mapping examples, devm cleanup, and fuzzing shift/cut/remap parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitrev.c -->
# sources/distributed-fs/ceph-client/lib/bitrev.c

## Purpose
Provides the generic byte bit-reversal table for platforms without architecture-specific bit-reverse support.

## APIs, Types, and Functions
Exports `byte_rev_table[256]` when `CONFIG_HAVE_ARCH_BITREVERSE` is not set. Higher-level inline helpers in `linux/bitrev.h` use this table to reverse bits in bytes and wider values.

## Control Flow, State, and Persistence
There is no runtime control flow beyond module metadata. The table maps each possible byte to its bit-reversed byte and is immutable.

## Dependencies and Integration
Depends on `linux/bitrev.h`, module/export support, and Kconfig symbols `BITREVERSE` and `HAVE_ARCH_BITREVERSE`. BCH, packing helpers, and drivers that need bit-order conversion may rely on it.

## Risks and Test Signals
Risks are table corruption, duplicate definitions when an architecture supplies its own implementation, or missing export for modules. Test signals include bitrev8 vectors for every byte, bitrev16/32/64 helper tests, builds with and without `CONFIG_HAVE_ARCH_BITREVERSE`, and BCH `swap_bits` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bootconfig-data.S -->
# sources/distributed-fs/ceph-client/lib/bootconfig-data.S

## Purpose
Embeds a default bootconfig blob into the kernel image.

## APIs, Types, and Functions
Defines two global linker-visible symbols: `embedded_bootconfig_data` and `embedded_bootconfig_data_end`. Between them it includes the binary contents of `lib/default.bconf`.

## Control Flow, State, and Persistence
There is no executable code. The assembler places the data in `.init.rodata` with writable/alloc section flags as declared. At boot, bootconfig code can locate the embedded blob through the exported symbols and consume it during init; the data is init-time persistent only.

## Dependencies and Integration
Depends on `lib/Makefile` generating `default.bconf` from `CONFIG_BOOT_CONFIG_EMBED_FILE` and building this object when `CONFIG_BOOT_CONFIG_EMBED` is enabled. Integration is through the bootconfig parser and linker symbol resolution.

## Risks and Test Signals
Risks include missing generated `default.bconf`, empty embed file producing no effective defaults, section flag/linker-script mismatch, and consumers reading beyond the end symbol. Test signals include builds with and without `CONFIG_BOOT_CONFIG_EMBED_FILE`, `nm`/linker checks for both symbols, boot tests confirming embedded bootconfig options are applied, and init memory discard checks after parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bootconfig-data.S -->
