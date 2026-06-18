# subset-b-006576 Research

Grouped code research for the Ceph client `tools/include/linux` compatibility headers. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/gfp_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/gfp_types.h

## Purpose
This header defines the `gfp_t` allocation flag bit layout and common GFP flag combinations used by user-space tools that build against kernel-style allocator APIs.

## APIs And Flow
It exports internal `___GFP_*` bit positions, public `__GFP_*` flags, `GFP_ZONEMASK`, `__GFP_BITS_SHIFT`, `__GFP_BITS_MASK`, and composites such as `GFP_ATOMIC`, `GFP_KERNEL`, `GFP_NOIO`, `GFP_NOFS`, `GFP_USER`, `GFP_HIGHUSER_MOVABLE`, and THP combinations. There is no executable flow; allocation behavior is expressed as bitmask composition consumed by `linux/gfp.h`, `slab.h`, and tool allocator shims.

## State, Dependencies, Risks, Tests
State is compile-time only. It depends on `linux/bits.h`, `gfp_t` from tool types, and config symbols such as `CONFIG_KASAN_HW_TAGS` and `CONFIG_LOCKDEP`. Risks are drift from kernel GFP layout, especially because comments require synchronized updates in trace/mm flag users and perf kmem tooling. Test signals are compile checks for every GFP macro, bitmask value comparisons against the kernel copy, and allocator tests proving `__GFP_ZERO`, reclaim, accounting, and KASAN-related flags are accepted by tools shims.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/gfp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hash.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/hash.h

## Purpose
`hash.h` provides fast integer and pointer hash helpers for kernel-derived user-space tools.

## APIs And Flow
The main APIs are `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, `GOLDEN_RATIO_PRIME`, `__hash_32_generic()`, `hash_32()`, `hash_64_generic()`, `hash_long()`, `hash_ptr()`, and `hash32_ptr()`. Flow is purely inline: values are multiplied by golden-ratio constants and high bits are selected according to the requested bucket bit count; 64-bit inputs fall back to folded 32-bit hashing on 32-bit hosts.

## State, Dependencies, Risks, Tests
There is no persistent state. It depends on `asm/types.h`, `linux/compiler.h`, `BITS_PER_LONG`, and optional arch overrides from `asm/hash.h`. Risks include using too many bits, host word-size differences, and assuming `hash32_ptr()` is a real hash when it is only a fold. Test signals include kernel `test_hash` parity, 32-bit and 64-bit host builds, arch override comparisons, and bucket-distribution checks for table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hashtable.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/hashtable.h

## Purpose
This header implements statically sized hash tables backed by `hlist_head` buckets for tools code.

## APIs And Flow
It exposes `DEFINE_HASHTABLE`, `DECLARE_HASHTABLE`, `HASH_SIZE`, `HASH_BITS`, `hash_min()`, `hash_init()`, `hash_add()`, `hash_hashed()`, `hash_empty()`, `hash_del()`, and iteration macros including safe and bucket-specific variants. Flow is simple: table size is inferred at compile time, keys are reduced with `hash_min()`, and entries are linked into or walked through the selected hlist bucket.

## State, Dependencies, Risks, Tests
State lives in caller-owned hlist bucket arrays and embedded `hlist_node` members. Dependencies include `list.h`, `bitops.h`, `hash.h`, `kernel.h`, `log2.h`, and `types.h`. Unlike the kernel header, RCU variants are absent, so concurrent readers need external synchronization. Tests should cover initialization, empty detection, add/delete, safe deletion during iteration, bucket lookup collisions, and compile failures when a pointer is passed where a fixed array is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hashtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/init.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/init.h

## Purpose
`init.h` provides a minimal user-space replacement for kernel init/exit annotations and boot-parameter registration structures.

## APIs And Flow
It defines no-op `__init`, `__exit`, `__initconst`, `__meminit`, `__meminitdata`, `__refdata`, and `__initdata`, plus `__section()`, `struct obs_kernel_param`, `__setup_param()`, `__setup()`, and `early_param()`. Setup macros emit static strings and `obs_kernel_param` records into `.init.setup`; there is no runtime parser in this header.

## State, Dependencies, Risks, Tests
State is generated object-file sections rather than heap or global runtime state. It depends on `linux/compiler.h` for `__used`, `__aligned`, and related attributes. Risks are linker-section mismatch with tools that expect kernel boot-param layouts and the fact that most kernel section lifetime semantics are intentionally erased. Tests should compile users with normal and early params and inspect object sections or linker maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interrupt.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/interrupt.h

## Purpose
This is an intentionally empty compatibility include for code that references `<linux/interrupt.h>` while building in the tools tree.

## APIs And Flow
It exports only an include guard and no types, constants, or functions. There is no control flow.

## State, Dependencies, Risks, Tests
There is no state and no dependencies. The key integration point is compile compatibility for sources that include interrupt headers but do not actually use IRQ APIs in user space. The risk is silent inadequacy if code later starts using `IRQF_*`, `irqreturn_t`, or `request_irq()` symbols. Test signal is building all tools consumers and checking that no interrupt-specific symbol is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interval_tree_generic.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/interval_tree_generic.h

## Purpose
This header is a macro template for generating interval tree insert, remove, and overlap-iteration functions over augmented red-black trees.

## APIs And Flow
`INTERVAL_TREE_DEFINE()` generates prefixed `_insert`, `_remove`, `_subtree_search`, `_iter_first`, and `_iter_next` helpers for caller-provided node type, rb-node field, interval endpoint type, subtree max field, and start/last accessors. Insert walks by start endpoint, updates ancestor subtree maxima, links the rb node, and rebalances with cached leftmost support. Search prunes by subtree maximum and leftmost start before returning overlapping intervals.

## State, Dependencies, Risks, Tests
State is caller-owned `struct rb_root_cached` plus each node's rb linkage and last-in-subtree field. It depends on `rbtree_augmented.h` and its callback macros. Risks include stale augmentation if callers mutate endpoints in place, invalid intervals where start exceeds last, and missing external locking. Tests should insert/remove overlapping and disjoint ranges, verify ordered iteration, exercise cached-leftmost fast paths, and fuzz endpoint values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interval_tree_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/io.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/io.h

## Purpose
`io.h` forwards tools code to architecture-specific I/O accessor definitions.

## APIs And Flow
It includes `<asm/io.h>` and defines no extra helpers. Any `read*`, `write*`, `ioremap`-like, or port I/O semantics come from the selected tools architecture header.

## State, Dependencies, Risks, Tests
There is no state here. The dependency and integration point is the architecture include path. The risk is that this tools header lacks the rich kernel `linux/io.h` managed mapping API, so consumers must only rely on symbols supplied by `asm/io.h`. Test signals are per-architecture tool builds and compile coverage for any accessor used by perf or other tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/jhash.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/jhash.h

## Purpose
`jhash.h` provides Jenkins lookup3-style 32-bit hashing for arbitrary bytes and arrays of 32-bit words.

## APIs And Flow
Important APIs are `jhash_size()`, `jhash_mask()`, `JHASH_INITVAL`, `__jhash_mix`, `__jhash_final`, `jhash()`, `jhash2()`, `__jhash_nwords()`, `jhash_3words()`, `jhash_2words()`, and `jhash_1word()`. `jhash()` consumes 12-byte blocks using unaligned 32-bit loads, handles the final tail with fall-through cases, and finalizes into `c`; `jhash2()` performs the same mixing over u32 words.

## State, Dependencies, Risks, Tests
There is no persistent state. Dependencies are `linux/bitops.h` for `rol32` and `linux/unaligned/packed_struct.h` for byte-safe loads. Risks include endian-dependent byte hashes, fall-through warning sensitivity, and using the non-cryptographic hash for adversarial inputs. Tests should compare vectors with the kernel copy, exercise lengths 0 through 12 and longer, verify word-array hashing, and run on big-endian and little-endian hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/jhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kallsyms.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kallsyms.h

## Purpose
This header provides minimal kallsyms-style symbol lookup hooks for lockdep and tools diagnostics.

## APIs And Flow
It defines `KSYM_NAME_LEN`, forward declares `struct module`, and provides `kallsyms_lookup()` returning `NULL`. With `HAVE_BACKTRACE_SUPPORT`, `print_ip_sym()` calls `backtrace_symbols()` for a single instruction pointer and prints via `printk`; otherwise it is an empty stub.

## State, Dependencies, Risks, Tests
State is transient stack storage and libc-allocated symbol strings in the optional backtrace path. Dependencies include `linux/kernel.h`, `linux/types.h`, optional `<execinfo.h>`, and printk-compatible logging. Risks are weak symbol fidelity compared with kernel kallsyms, allocation behavior in diagnostics, and silent empty output when backtrace support is absent. Tests should build both config paths and verify a known address produces useful diagnostic text when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kallsyms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kasan-tags.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kasan-tags.h

## Purpose
`kasan-tags.h` supplies memory-tag constants shared with kernel-style KASAN code.

## APIs And Flow
It defines `KASAN_TAG_KERNEL`, `KASAN_TAG_INVALID`, `KASAN_TAG_MAX`, and `KASAN_TAG_MIN`. There are no functions or branches.

## State, Dependencies, Risks, Tests
There is no state and no dependencies beyond integer macro use. Integration is through allocation and pointer-tagging code that wants the same tag vocabulary as the kernel. Risks are value drift from kernel KASAN definitions and misuse on tools builds that do not actually implement tag checking. Test signals are compile-time assertions against the kernel copy and builds of allocators that include KASAN flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kasan-tags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kconfig.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kconfig.h

## Purpose
This header implements Kconfig-style compile-time predicates for tools code.

## APIs And Flow
It defines placeholder and boolean-composition macros `__is_defined`, `__and`, `__or`, `IS_BUILTIN`, `IS_MODULE`, `IS_REACHABLE`, and `IS_ENABLED`. Macro expansion tests whether `CONFIG_FOO` or `CONFIG_FOO_MODULE` expands to `1` and folds module reachability based on `MODULE`.

## State, Dependencies, Risks, Tests
All state is preprocessor state. There are no includes. Integration points are headers that use kernel `IS_ENABLED()` idioms in user-space tools. Risks include subtle macro expansion breakage, non-1 config definitions, and differences between built-in and module builds. Tests should compile small translation units for defined, undefined, builtin, module, and `MODULE` combinations and verify preprocessor output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kern_levels.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kern_levels.h

## Purpose
`kern_levels.h` defines kernel log-level string prefixes for tools logging compatibility.

## APIs And Flow
It exports `KERN_SOH`, `KERN_SOH_ASCII`, severity macros from `KERN_EMERG` through `KERN_DEBUG`, `KERN_DEFAULT`, and `KERN_CONT`. In this tools copy the prefixes are empty strings or empty character constants, so they do not encode kernel control bytes.

## State, Dependencies, Risks, Tests
There is no state and no dependencies. It integrates with `printk`-style macros that concatenate log level markers into format strings. Risks are loss of severity information in user-space output and portability of the empty character definition. Test signals are compile checks for every log-level macro and diagnostics proving user-space logging does not expose raw kernel control bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kern_levels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kernel.h

## Purpose
This is a compact tools replacement for common kernel utility macros, endian conversions, assertion hooks, and snprintf helpers.

## APIs And Flow
It includes libc and tools headers, defines `UINT_MAX`, `_RET_IP_`, `PERF_ALIGN`, `offsetof`, type-safe `min`, `max`, `min_t`, `max_t`, `clamp`, `BUG_ON`, `BUG`, endian conversion aliases, `vscnprintf()`, `scnprintf()`, `scnprintf_pad()`, `ARRAY_SIZE`, `current_gfp_context()`, and `synchronize_rcu()`. Flow is inline macro evaluation with single-evaluation min/max temporaries and host-endian conversion selection from `__BYTE_ORDER`.

## State, Dependencies, Risks, Tests
No persistent state is stored here. Dependencies include libc headers, `asm/bug.h`, `byteswap.h`, `assert.h`, `linux/build_bug.h`, and `linux/compiler.h`. Risks are weaker kernel semantics: `BUG_ON` becomes `assert` unless `NDEBUG`, RCU synchronization is a no-op, and endian conversion macros are function-like aliases. Tests should cover debug and `NDEBUG` builds, endian conversions on both byte orders, ARRAY_SIZE type checking, and snprintf truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/linkage.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/linkage.h

## Purpose
`linkage.h` gives tools assembly code a minimal subset of kernel symbol annotation macros.

## APIs And Flow
It includes `linux/export.h` and defines `SYM_FUNC_START`, `SYM_FUNC_END`, `SYM_DATA_START`, `SYM_DATA_START_LOCAL`, and `SYM_DATA_END`. Start macros emit `.globl` and a label; end macros are empty.

## State, Dependencies, Risks, Tests
There is no runtime state. Integration is with assembler sources imported from the kernel that expect modern `SYM_*` annotations. Risks are missing ELF type, size, alignment, and CFI metadata compared with the kernel macros, which can affect tooling but not simple labels. Test signals are assembling tools objects and checking exported symbols with `nm` or `readelf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/list.h

## Purpose
`list.h` provides Linux intrusive doubly linked list and hlist primitives for user-space tools.

## APIs And Flow
It defines list heads, initialization, add, tail add, delete, replace, move, splice, cut, rotate, emptiness tests, entry accessors, forward/reverse/safe iteration macros, and hlist equivalents including add, delete, fake nodes, membership checks, and hlist iteration. Control flow is pointer rewriting around embedded `struct list_head` or `struct hlist_node`; safe iterators prefetch the next cursor before body execution.

## State, Dependencies, Risks, Tests
State is entirely caller-owned intrusive linkage. Dependencies are `linux/types.h`, `linux/poison.h`, `linux/kernel.h`, and `linux/compiler.h`; optional debug-list paths require external implementations. Risks include use-after-delete via poisoned pointers, no inherent locking, unsafe iteration if non-safe macros remove entries, and hlist nodes needing initialization before membership tests. Tests should cover add/delete/move/splice/cut, safe iteration with removal, hlist bucket operations, poison-triggered misuse, and debug-list builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list_sort.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/list_sort.h

## Purpose
This header declares the generic list sorting routine for intrusive kernel-style lists.

## APIs And Flow
It includes `linux/list.h` and declares `list_sort(void *priv, struct list_head *head, int (*cmp)(void *priv, const struct list_head *a, const struct list_head *b))`. The actual control flow lives in the linked implementation; callers provide private comparison context and a comparator over list nodes.

## State, Dependencies, Risks, Tests
State is the caller's list, reordered in place by the implementation. Dependencies are `list.h` and whatever object file supplies `list_sort`. Risks are comparator instability, corrupt lists, and missing linkage if the implementation is not included in a tool build. Tests should sort empty, one-element, already sorted, reverse, duplicate-key, and large lists while validating list integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list_sort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/livepatch_external.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/livepatch_external.h

## Purpose
This header defines the external livepatch ELF metadata structures consumed by tooling.

## APIs And Flow
It provides constants such as `KLP_RELA_PREFIX`, `KLP_SYM_PREFIX`, and `KLP_SYMPOS_MAX`, and structures `klp_module_reloc`, `klp_object_relocs`, `klp_section_relocs`, and symbol-position metadata used by livepatch relocation processing. There is no executable flow; it is an ABI description for parsing or emitting sections.

## State, Dependencies, Risks, Tests
State is persistent in compiled ELF objects and livepatch metadata sections. Dependencies are fixed-width integer types and ELF/livepatch tools that interpret these records. Risks include ABI drift with kernel livepatch consumers, incorrect symbol position handling for duplicate names, and malformed relocation counts. Tests should parse representative livepatch objects, validate section names and relocation arrays, and compare structure sizes with the kernel header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/livepatch_external.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/log2.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/log2.h

## Purpose
`log2.h` supplies integer base-2 logarithm, power-of-two tests, and round-to-power helpers.

## APIs And Flow
It defines `__ilog2_u32()`, `__ilog2_u64()`, `is_power_of_2()`, `__roundup_pow_of_two()`, `__rounddown_pow_of_two()`, and constant-capable macros `ilog2()`, `roundup_pow_of_two()`, and `rounddown_pow_of_two()`. Compile-time constants use a long ternary cascade; runtime values dispatch to `fls`, `fls64`, or `fls_long`.

## State, Dependencies, Risks, Tests
There is no state. Dependencies are `linux/bitops.h` and `linux/types.h`. Risks include undefined behavior for zero in round helpers, `ilog2(0)` returning zero by macro convention, and width differences between `unsigned long` hosts. Tests should cover compile-time and runtime inputs, 32-bit and 64-bit maxima, powers and non-powers, zero edge cases where allowed, and table-size users such as `HASH_BITS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/log2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/math.h

## Purpose
This header provides simple integer rounding and division helper macros for tools code.

## APIs And Flow
It defines `__round_mask()`, `round_up()`, `round_down()`, `DIV_ROUND_UP()`, and `roundup()`. The macros use typed temporaries or typed masks so argument evaluation and bit width are controlled.

## State, Dependencies, Risks, Tests
There is no state and no includes. Integration points are allocation sizing, buffer alignment, and page or record boundary calculations. Risks include divisor zero, non-power-of-two use with bitmask-based `round_up` and `round_down`, overflow in `(n + d - 1)`, and side effects in arguments not protected by every macro. Tests should cover powers of two, non-powers where supported, boundary values, type widths, and expressions with side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math64.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/math64.h

## Purpose
`math64.h` adapts kernel 64-bit division helpers to user-space tool builds.

## APIs And Flow
It includes standard integer support and exposes macros or inline helpers such as `do_div`, `div_u64`, `div64_u64`, `div64_u64_rem`, `div_u64_rem`, `mul_u64_u64_div_u64`, and rounding variants depending on host word size. Flow is arithmetic-only: callers pass 64-bit numerators, optional remainder pointers, and 32-bit or 64-bit divisors.

## State, Dependencies, Risks, Tests
No persistent state is stored. Dependencies are fixed-width types and compiler support for 64-bit arithmetic. Risks include divide-by-zero, truncation when returning 32-bit remainders, host/compiler differences from kernel assembly helpers, and overflow in multiply-then-divide helpers. Tests should compare against known 128-bit reference arithmetic, cover 32-bit and 64-bit hosts, and exercise max-value numerators and divisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/mm.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/mm.h

## Purpose
This tools `mm.h` provides minimal page, physical-address, and memory accounting helpers expected by kernel-derived code.

## APIs And Flow
It defines `PAGE_SHIFT`, `PAGE_SIZE`, `PAGE_MASK`, `PHYS_ADDR_MAX`, `PAGE_ALIGN`, `PAGE_ALIGN_DOWN`, `__va`, `__pa`, `__pa_symbol`, `pfn_to_page()`, `phys_to_virt()`, `virt_to_phys()`, `totalram_pages_inc()`, `totalram_pages_add()`, and `early_pfn_to_nid()`. Address conversion is identity-style casting, and memory accounting helpers are no-ops.

## State, Dependencies, Risks, Tests
There is no real MM state. Dependencies are `linux/align.h`, `linux/mmzone.h`, and `linux/sizes.h`. Risks include assuming kernel virtual/physical translation semantics in user space, fixed 4 KiB page constants on nonmatching hosts, and NUMA always collapsing to node 0. Tests should compile users on supported architectures and verify callers only use these helpers for layout arithmetic or simulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/module.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/module.h

## Purpose
`module.h` stubs kernel module APIs needed by tools and lockdep code.

## APIs And Flow
It defines `module_param(name, type, perm)` as an empty macro and provides `__is_module_percpu_address()` returning `false`. There is no module registration or parameter parsing flow.

## State, Dependencies, Risks, Tests
There is no module state. It depends on `bool` being available through included context. Integration is with code shared from the kernel that annotates module parameters or checks module per-cpu address ranges. Risks are silently disabling module-specific behavior in tools and losing diagnostics for addresses that would be module-owned in-kernel. Tests should build shared code with module annotations and verify address classification callers handle `false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/moduleparam.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/moduleparam.h

## Purpose
This header provides a minimal placeholder for kernel module parameter documentation macros.

## APIs And Flow
It defines `MODULE_PARM_DESC(parm, desc)` as empty. No declarations, parsing tables, or runtime flow are generated.

## State, Dependencies, Risks, Tests
There is no state or dependencies. It integrates with imported code that leaves module parameter descriptions in place. Risks are lost help text and accidental assumption that parameters can be set in tools binaries. Test signal is successful compilation of code containing `MODULE_PARM_DESC` uses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/moduleparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/mutex.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/mutex.h

## Purpose
This is an empty compatibility header for includes of `<linux/mutex.h>` in tools code.

## APIs And Flow
It exports only an include guard. It does not define `struct mutex`, lock helpers, or debug annotations.

## State, Dependencies, Risks, Tests
There is no state. The integration point is include compatibility for code paths that do not actually use mutex APIs after preprocessing. The risk is build breakage if a consumer starts requiring kernel mutex symbols instead of using pthread or other tools locks. Test signal is all tools builds passing with no unresolved mutex references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/nmi.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/nmi.h

## Purpose
`nmi.h` is an empty file in this tools include tree.

## APIs And Flow
It exports no include guard, macros, types, or functions. There is no control flow.

## State, Dependencies, Risks, Tests
There is no state or dependency. Its role is effectively as a path placeholder for source imports that include NMI support conditionally elsewhere. Risks are that direct inclusion may not be protected against repeated reads and any future use of NMI watchdog or backtrace APIs will fail to compile. Test signal is compile coverage of current consumers and a check that no symbol from this header is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/numa.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/numa.h

## Purpose
This header defines minimal NUMA node constants and validation for tools builds.

## APIs And Flow
It maps `NODES_SHIFT` from `CONFIG_NODES_SHIFT` or zero, defines `MAX_NUMNODES`, `NUMA_NO_NODE`, and `numa_valid_node()`. Flow is a range check that accepts node IDs from zero up to `MAX_NUMNODES - 1`.

## State, Dependencies, Risks, Tests
There is no runtime state. The only dependency is the optional config macro. Integration points include allocators and topology code that need to accept or ignore node IDs. Risks are defaulting to a single node in tools, mismatch with host NUMA topology, and callers treating `NUMA_NO_NODE` as valid. Tests should compile with and without `CONFIG_NODES_SHIFT` and validate boundary node IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/objtool_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/objtool_types.h

## Purpose
`objtool_types.h` defines unwind and annotation constants shared with objtool-aware assembly and metadata consumers.

## APIs And Flow
It declares `struct unwind_hint` for non-assembly builds, with fields for instruction pointer, stack offset, stack register, unwind type, and signal flag. It defines `UNWIND_HINT_TYPE_*`, `ANNOTYPE_*`, and `ANNOTYPE_DATA_SPECIAL`. There is no control flow; these values describe metadata.

## State, Dependencies, Risks, Tests
State persists in generated object metadata or inline assembly annotations. It depends on `linux/types.h` outside assembly. Risks are ABI drift with objtool and ORC unwinder expectations, incorrect packed layout assumptions, and assembly/C disagreement over numeric constants. Tests should compare structure size and constant values with kernel headers and run objtool over representative annotated objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/objtool_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/overflow.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/overflow.h

## Purpose
This header centralizes checked arithmetic and saturated size calculations for allocation and structure sizing.

## APIs And Flow
It exports type-limit helpers `is_signed_type`, `type_min`, `type_max`, overflow wrappers `check_add_overflow`, `check_sub_overflow`, `check_mul_overflow`, and size helpers `size_mul()`, `array_size()`, `array3_size()`, `__ab_c_size()`, and `struct_size()`. Flow delegates arithmetic checks to compiler builtins after enforcing matching operand and destination types.

## State, Dependencies, Risks, Tests
There is no state. Dependencies are `linux/compiler.h`, `SIZE_MAX`, `typeof`, and compiler overflow builtins. Risks include unsupported compilers, accidental type mismatches, `_Bool` arithmetic edge cases, and callers ignoring `SIZE_MAX` saturation before allocation. Tests should cover signed and unsigned limits, add/sub/mul overflow and non-overflow, flexible array sizing, and compile-time type mismatch detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/overflow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/panic.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/panic.h

## Purpose
`panic.h` provides a user-space implementation of kernel `panic()` semantics for fatal tools errors.

## APIs And Flow
It defines inline `panic(const char *fmt, ...)`, which formats the message to `stderr` with `vfprintf()` and exits the process with status `-1`.

## State, Dependencies, Risks, Tests
State is limited to process termination and stderr output. Dependencies are `<stdarg.h>`, `<stdio.h>`, and `<stdlib.h>`. Integration points are imported kernel code that expects `panic()` to be noreturn-like. Risks are cleanup bypass, exit status truncation by shells, and no automatic newline or stack dump. Tests should execute a small child process that calls `panic()` and assert output and nonzero termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/panic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pci_ids.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/pci_ids.h

## Purpose
`pci_ids.h` is a registry of PCI vendor, device, subvendor, class, and related numeric identifiers shared with tools.

## APIs And Flow
The file is macro data only. It defines thousands of `PCI_VENDOR_ID_*`, `PCI_DEVICE_ID_*`, `PCI_SUBVENDOR_ID_*`, and `PCI_SUBDEVICE_ID_*` constants covering common vendors and devices, including storage, audio, network, bridge, GPU, and platform devices. There is no executable control flow.

## State, Dependencies, Risks, Tests
State is compile-time numeric identity mapping that becomes persistent wherever tools encode device tables. There are no includes. Integration points include PCI decoders, perf tooling, tracing, and imported drivers or hardware tables. Risks are stale IDs relative to the kernel copy, duplicate or reused names, and consumers assuming the list is complete. Tests should compare the tools copy to the kernel header, compile table users, and spot-check recently added IDs and duplicate values with intentional aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pci_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pfn.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/pfn.h

## Purpose
`pfn.h` provides page frame number conversion macros for tools.

## APIs And Flow
It includes `linux/mm.h` and defines `PFN_UP()`, `PFN_DOWN()`, `PFN_PHYS()`, and `PHYS_PFN()`. Flow is shift and add arithmetic based on `PAGE_SHIFT` and `PAGE_SIZE`.

## State, Dependencies, Risks, Tests
There is no state. Dependencies are the page constants and `phys_addr_t` from the tools MM/type layer. Risks are overflow in `PFN_UP(x)` near address maxima, fixed page-size assumptions, and accidental use for real kernel physical memory semantics. Tests should cover aligned and unaligned addresses, zero, max safe values, and round-trip `PFN_PHYS(PHYS_PFN(x))` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/poison.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/poison.h

## Purpose
This header defines poison pointer and byte patterns used to detect invalid list, timer, slab, page, and subsystem states.

## APIs And Flow
It exports `POISON_POINTER_DELTA`, `LIST_POISON1`, `LIST_POISON2`, `TIMER_ENTRY_STATIC`, `PAGE_POISON`, `TAIL_MAPPING`, `SLUB_RED_*`, `POISON_*`, `JBD*_POISON_FREE`, pool poison values, `ATM_POISON`, mutex debug values, and `KEY_DESTROY`. There is no control flow.

## State, Dependencies, Risks, Tests
Poison values become persistent in freed or invalidated data structures. It depends on `_AC`, optional `CONFIG_ILLEGAL_POINTER_VALUE`, and C/C++ differences where list poisons become `NULL` under C++. Risks include poisoned pointers becoming mappable on unusual systems, C++ behavior weakening detection, and consumers relying on exact byte values for diagnostics. Tests should delete list entries and confirm poison writes, validate configured pointer deltas, and compare constants with kernel expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/poison.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/prandom.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/prandom.h

## Purpose
`prandom.h` implements a small deterministic pseudo-random generator compatible with kernel-style stateful callers.

## APIs And Flow
It defines `struct rnd_state`, `__seed()`, `prandom_seed_state()`, and `prandom_u32_state()`. Seeding derives a 32-bit value from a 64-bit seed and enforces minimum values for the four Tausworthe state words. Generation updates each word with a `TAUSWORTHE` recurrence and returns the XOR of all four states.

## State, Dependencies, Risks, Tests
State persists in caller-owned `struct rnd_state`. It depends on `linux/types.h`. Risks are deterministic and non-cryptographic output, weak seeding because all four state words derive from one folded seed value, and data races if a state is shared without locking. Tests should compare fixed seed sequences, boundary seeds below each minimum, repeated calls, and independent state objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/prandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rbtree.h

## Purpose
`rbtree.h` defines intrusive red-black tree node/root types and common insertion, lookup, cached-leftmost, replacement, and iteration helpers for tools.

## APIs And Flow
It declares `struct rb_node`, `struct rb_root`, `struct rb_root_cached`, root initializers, parent/color helpers, external balancing and traversal functions, `rb_link_node()`, `rb_entry_safe()`, postorder safe iteration, `rb_erase_init()`, cached insert/erase/replace helpers, `rb_add()`, `rb_add_cached()`, `rb_find_add()`, `rb_find()`, `rb_find_first()`, `rb_next_match()`, and `rb_for_each()`. Flow is caller-directed binary search using comparison callbacks, then link and rebalance.

## State, Dependencies, Risks, Tests
State is caller-owned tree roots and embedded rb nodes with parent/color packed into one word. Dependencies are `linux/kernel.h` and `linux/stddef.h`, plus linked rbtree implementation objects. Risks include corrupt parent/color bits, comparator partial-order ambiguity, missing locking, and unsafe postorder iteration if tree rotations occur. Tests should insert/search/delete duplicate and unique keys, cached-leftmost updates, replacement, postorder cleanup, and randomized tree invariant validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree_augmented.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rbtree_augmented.h

## Purpose
This header provides augmented red-black tree callbacks and erase/insert helpers used by interval trees and other metadata-indexed structures.

## APIs And Flow
It defines `struct rb_augment_callbacks`, declares `__rb_insert_augmented()` and `__rb_erase_color()`, provides `rb_insert_augmented()`, `rb_insert_augmented_cached()`, `RB_DECLARE_CALLBACKS()`, `RB_DECLARE_CALLBACKS_MAX()`, color/parent helpers, `__rb_change_child()`, `__rb_erase_augmented()`, `rb_erase_augmented()`, and `rb_erase_augmented_cached()`. Erase handles zero, one, or two child cases, copies augmentation to successors, propagates changes, and rebalances if a black node removal requires it.

## State, Dependencies, Risks, Tests
State is augmentation stored in caller node fields plus rb topology. Dependencies are `linux/compiler.h` and `linux/rbtree.h`. Risks include depending on implementation-detail helpers, callbacks that fail to recompute after rotations, cached-leftmost desynchronization, and code bloat from macro-generated callbacks. Tests should exercise all erase cases, rotations with augmentation recomputation, interval tree users, and cached-tree leftmost updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree_augmented.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rcu.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rcu.h

## Purpose
`rcu.h` supplies the tiny RCU and lockdep-facing stubs needed by liblockdep-style tools code.

## APIs And Flow
It defines a global `rcu_scheduler_active`, inline status helpers `rcu_lockdep_current_cpu_online()`, `rcu_is_cpu_idle()`, and `rcu_is_watching()`, plus `rcu_assign_pointer()` and `RCU_INIT_POINTER()`. Flow is stubbed: CPU-online and idle checks return true, watching returns false, and pointer publication is a plain assignment.

## State, Dependencies, Risks, Tests
The only declared state is `rcu_scheduler_active`; there is no grace-period engine or read-side tracking. Integration points are lockdep and imported kernel code that probes RCU state while running in a single-process tools context. Risks are treating these stubs as concurrency protection, missing memory barriers around pointer publication, and multiple-definition hazards if the non-extern global is included in several linked objects. Tests should compile current consumers, inspect linkage for `rcu_scheduler_active`, and verify shared data structures use separate synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/refcount.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/refcount.h

## Purpose
`refcount.h` implements a saturation-aware reference counter on top of tools `atomic_t`.

## APIs And Flow
It defines `refcount_t`, `REFCOUNT_INIT()`, `refcount_set()`, `refcount_set_release()`, `refcount_read()`, `refcount_inc_not_zero()`, `refcount_inc()`, `refcount_sub_and_test()`, and `refcount_dec_and_test()`. Increment loops use relaxed compare-exchange, reject zero, and saturate at `UINT_MAX`; decrement loops use release compare-exchange, reject saturated counters, detect underflow, and return true on transition to zero.

## State, Dependencies, Risks, Tests
State is the embedded atomic counter. Dependencies are `linux/atomic.h` and `linux/kernel.h`; warnings become `BUG_ON` unless `NDEBUG` disables them. Risks include weaker memory ordering than general atomics, saturated counters intentionally leaking objects, assertions disappearing in release builds, and callers ignoring `__must_check` decrement results. Tests should cover zero increment, saturation, underflow, normal lifecycle, concurrent increment/decrement, and debug versus `NDEBUG` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/refcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/ring_buffer.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/ring_buffer.h

## Purpose
This header provides perf mmap ring-buffer head and tail accessors with the required user-space memory barriers.

## APIs And Flow
`ring_buffer_read_head()` reads `perf_event_mmap_page::data_head` using `smp_load_acquire()` on architectures where that is efficient, or `READ_ONCE()` plus `smp_rmb()` elsewhere. `ring_buffer_write_tail()` stores `data_tail` with `smp_store_release()`. The comments document the kernel producer/user consumer barrier pairing.

## State, Dependencies, Risks, Tests
State is in the shared perf mmap page maintained by kernel producer and user-space consumer. Dependencies are `asm/barrier.h` and `linux/perf_event.h`. Risks include stale or torn reads if barriers are changed, architecture condition mistakes, and consumers updating tail before reading data. Tests should run perf ring-buffer consumption on supported architectures, validate lost-event behavior under load, and use memory-model or stress tests around head/data/tail ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/ring_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rwsem.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rwsem.h

## Purpose
`rwsem.h` maps kernel read/write semaphore APIs onto POSIX read/write locks for tools.

## APIs And Flow
It defines `struct rw_semaphore` containing `pthread_rwlock_t` and inline helpers `init_rwsem()`, `exit_rwsem()`, `down_read()`, `up_read()`, `down_write()`, `up_write()`, plus nested variants mapped to the same operations. Flow delegates directly to pthread rwlock init, destroy, read lock, write lock, and unlock.

## State, Dependencies, Risks, Tests
State is the pthread rwlock object. Dependency is `<pthread.h>`. Risks include different fairness and signal behavior from kernel rwsems, ignored lockdep subclass arguments, and required destruction ordering. Tests should cover parallel readers, writer exclusion, init/destroy errors, nested macro compile paths, and tools linked with pthreads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rwsem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/clock.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sched/clock.h

## Purpose
This is an empty tools compatibility header for scheduler clock includes.

## APIs And Flow
It exports only an include guard and no `sched_clock()`, `cpu_clock()`, or local clock functions. There is no control flow.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration is limited to sources where scheduler clock APIs are compiled out or supplied elsewhere. The risk is compile failure if imported code starts using kernel clock helpers. Test signal is building all current tools consumers and grepping for unresolved scheduler clock symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/mm.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sched/mm.h

## Purpose
`sched/mm.h` provides the single allocation-context annotation needed by tools code.

## APIs And Flow
It defines `might_alloc(gfp)` as a no-op statement macro. No scheduler or mm lifetime functions are present.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration is with allocator paths that retain kernel debug annotations while building in user space. Risks are losing might-sleep or reclaim-context diagnostics and assuming this header provides real `mm_struct` helpers. Test signal is compilation of allocator code with `might_alloc()` calls and separate checks that real mm APIs are not required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/task.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sched/task.h

## Purpose
This is an empty compatibility header for task-lifetime scheduler includes in the tools tree.

## APIs And Flow
It defines only an include guard. It does not provide `task_struct`, clone helpers, task refcounting, or scheduler callbacks.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration is include-level compatibility for code paths that avoid task APIs in user space. Risks are compile failures if new imported code uses kernel task lifetime interfaces. Test signals are full tools builds and static checks that no `sched/task.h` symbols are referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/seq_file.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/seq_file.h

## Purpose
`seq_file.h` supplies a forward declaration for code that mentions kernel sequence files.

## APIs And Flow
It forward declares `struct seq_file` and provides no operations such as `seq_printf()` or iteration callbacks. There is no control flow.

## State, Dependencies, Risks, Tests
There is no state. It has no dependencies. Integration is limited to pointer declarations or opaque references in shared headers. Risks are incomplete type misuse and missing implementation if code tries to emit seq-file output in tools. Tests should compile all consumers and ensure only opaque pointers or disabled branches use `struct seq_file`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/seq_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sizes.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sizes.h

## Purpose
`sizes.h` defines common byte-size constants from 1 byte through 4 GiB.

## APIs And Flow
It includes `linux/const.h` and exports `SZ_1` through `SZ_512`, `SZ_1K` through `SZ_512K`, `SZ_1M` through `SZ_512M`, `SZ_1G`, `SZ_2G`, and `SZ_4G`. There is no executable flow.

## State, Dependencies, Risks, Tests
There is no state. The dependency is `_AC` for the 64-bit `SZ_4G` constant. Integration points are memory maps, buffer sizing, and page arithmetic. Risks include signed integer overflow if large constants are used in signed 32-bit expressions and assumptions that `SZ_4G` fits in `unsigned long` on every host. Tests should compile constants in 32-bit and 64-bit builds and use static assertions for expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sizes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/slab.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/slab.h

## Purpose
This header declares the tools slab and kmalloc compatibility API, including cache objects and sheaf bulk-allocation helpers.

## APIs And Flow
It defines slab flags, `kzalloc_node`, `struct kmem_cache`, `struct kmem_cache_args`, `struct slab_sheaf`, `kzalloc()`, `kmalloc()`, `kfree()`, `kmalloc_array()`, cache allocation/free APIs, cache creation variants selected by `_Generic`, bulk alloc/free, sheaf prefill/refill/return helpers, `kmem_cache_sheaf_size()`, `__alloc_objs()`, and `kzalloc_obj()`. Inline flow mostly adapts arguments, adds `__GFP_ZERO`, or computes overflow-checked object sizes.

## State, Dependencies, Risks, Tests
State persists in `kmem_cache` fields: pthread mutex, object size, alignment, constructor, free-object storage, counters, non-kernel allocation tracking, callbacks, and private data. Dependencies include `linux/types.h`, `linux/gfp.h`, `pthread.h`, list types, and overflow helpers. Risks include divergence from kernel slab semantics, constructor/freeptr constraints, pthread locking requirements, `SLAB_TYPESAFE_BY_RCU` semantics in user space, and overflow handling in object allocation. Tests should cover kmalloc/kzalloc, arrays, cache create variants, ctor invocation, bulk/sheaf paths, counters, locking, and failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/slab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/spinlock.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/spinlock.h

## Purpose
`spinlock.h` maps kernel spinlock APIs to POSIX mutexes for tools.

## APIs And Flow
It typedefs `spinlock_t` and `arch_spinlock_t` to `pthread_mutex_t`, defines initializers, and maps `spin_lock*`, `spin_unlock*`, IRQ-save, bottom-half, nested, and arch lock helpers to pthread mutex operations. `arch_spin_is_locked()` always returns true.

## State, Dependencies, Risks, Tests
State is the pthread mutex object. Dependencies are `<pthread.h>` and `<stdbool.h>`. Risks are semantic mismatch with real spinlocks: operations can sleep, IRQ and bottom-half state is ignored, saved flags are unused, lockdep subclassing is absent, and `arch_spin_is_locked()` is not a real query. Tests should exercise initialization, lock/unlock, contention, IRQ-save macro compilation, and deadlock behavior expected by tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/static_call_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/static_call_types.h

## Purpose
This header defines static-call symbol naming, site metadata, and dispatch structures used by kernel and tooling builds.

## APIs And Flow
It exports key and trampoline prefix macros, string forms, site flags, `struct static_call_site`, `DECLARE_STATIC_CALL()`, `struct static_call_key`, and `static_call()` or `static_call_mod()` forms selected by `CONFIG_HAVE_STATIC_CALL`, `CONFIG_HAVE_STATIC_CALL_INLINE`, and `MODULE`. With inline static calls, key symbols are marked addressable so objtool can create `.static_call_sites`; without static call support, calls dereference the key's function pointer.

## State, Dependencies, Risks, Tests
State is in static call keys, trampolines, and generated site tables. Dependencies are `linux/types.h`, `linux/stringify.h`, `linux/compiler.h`, objtool, and architecture static-call support. Risks include stripped key symbols, wrong low-bit site flags, module versus built-in dispatch differences, and stale tooling metadata. Tests should build with each config combination, inspect static-call site sections, and verify fallback function-pointer dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/static_call_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/string.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/string.h

## Purpose
`string.h` bridges libc string functions with kernel-style string helper declarations used by tools.

## APIs And Flow
It includes libc `<string.h>`, declares `memdup()`, `argv_split()`, `argv_free()`, `strtobool()`, `strlcpy()` for glibc builds, `str_error_r()`, `strreplace()`, `skip_spaces()`, `strim()`, `remove_spaces()`, `memchr_inv()`, and `memparse()`, and defines inline `strstarts()` and `str_ends_with()`. `strscpy` is aliased to unsafe libc `strcpy` in this tools copy.

## State, Dependencies, Risks, Tests
State is caller-owned strings and allocated argv/memdup buffers. Dependencies are `linux/types.h`, libc, compiler diagnostic pragmas, and external implementations of declared helpers. Risks include `strscpy` losing kernel truncation safety, redundant `strlcpy` declarations across libcs, ownership leaks from `argv_split`, and in-place mutation by trim/remove helpers. Tests should cover prefix/suffix helpers, bool parsing, argv split/free, memparse units, `str_error_r` variants, and overflow/truncation call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/stringify.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/stringify.h

## Purpose
`stringify.h` provides two-level macro stringification for tools code.

## APIs And Flow
It defines `__stringify_1(x...)` and `__stringify(x...)`. The first macro turns arguments into a string literal; the second expands macro arguments before stringifying them.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration points include symbol-name generation, static-call metadata, assembler strings, and debug strings. Risks are comma/variadic macro portability and drift from the kernel copy, which has extra conveniences not present here. Tests should compile direct and indirect stringification cases, including a macro value expanded before stringification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/stringify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/time64.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/time64.h

## Purpose
This tools header defines common time-unit conversion constants without importing the full kernel time64 API.

## APIs And Flow
It exports `MSEC_PER_SEC`, `USEC_PER_MSEC`, `NSEC_PER_USEC`, `NSEC_PER_MSEC`, `USEC_PER_SEC`, `NSEC_PER_SEC`, and `FSEC_PER_SEC`. There are no time structures, normalization helpers, or conversion functions.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration points are duration conversions in perf and other tools. Risks include callers expecting kernel `timespec64` APIs, signed overflow in large conversions, and unit mistakes because all constants are untyped long or long long. Tests should compile users, static-assert constant values, and check arithmetic at millisecond, microsecond, nanosecond, and femtosecond scales.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/time64.h -->
