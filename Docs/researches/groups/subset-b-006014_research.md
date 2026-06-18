# subset-b-006014 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/crypto.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/crypto.c

## Purpose
`crypto.c` exposes kernel crypto operations to selected BPF program types through BTF kfuncs. It manages a registry of `struct bpf_crypto_type` providers, creates refcounted `struct bpf_crypto_ctx` objects from BPF-provided parameters, and implements encrypt/decrypt calls over BPF dynptr buffers.

## Important APIs, types, and functions
`struct bpf_crypto_params` is the BPF ABI for context creation: operation `type`, algorithm name, key material, key length, and optional authentication size. `struct bpf_crypto_ctx` stores the selected provider, provider transform pointer, IV/state length, RCU head, and refcount. `bpf_crypto_register_type()` and `bpf_crypto_unregister_type()` maintain the global provider list under `bpf_crypto_types_sem` and are exported GPL symbols for crypto provider modules. `bpf_crypto_ctx_create()` is a sleepable acquire kfunc for `BPF_PROG_TYPE_SYSCALL`; `bpf_crypto_ctx_acquire()` and `bpf_crypto_ctx_release()` implement kptr-style ownership; `bpf_crypto_encrypt()` and `bpf_crypto_decrypt()` are RCU kfuncs for sched cls, sched act, and XDP.

## Control flow
Provider registration rejects duplicate names, allocates a list node, and links it under a write semaphore. Context creation validates the parameter size and reserved bytes, finds a provider by name with `try_module_get()`, checks algorithm support, authsize compatibility, key length, allocates the context, allocates the provider transform, optionally sets authsize, sets the key, rejects transforms still reporting `CRYPTO_TFM_NEED_KEY`, calculates `siv_len`, and returns a refcount-one object. Any failure unwinds transform, context, and module references. Encrypt/decrypt calls funnel through `bpf_crypto_crypt()`, which validates dynptr mutability and sizes, maps source, destination, and optional state/IV dynptr memory, checks `siv_len`, then dispatches to the provider's `encrypt` or `decrypt` method.

## State and persistence behavior
The provider registry is global process-lifetime kernel state guarded by an rwsem. Crypto contexts are heap objects whose lifetime is explicit through BPF kfunc acquire/release semantics and map kptr destructors. Final release uses `call_rcu()` before freeing the transform and dropping the provider module reference, so BPF-side RCU readers can finish safely.

## Dependencies and integration points
The file depends on BTF kfunc registration, BPF dynptr internals, the Linux crypto API abstraction in `linux/bpf_crypto.h`, module reference counting, and BPF memory/kptr destructor infrastructure. `crypto_kfunc_init()` registers init kfuncs for syscall programs, encrypt/decrypt kfuncs for XDP and TC program types, and a destructor kfunc for `struct bpf_crypto_ctx`.

## Risks and test signals
Risk is concentrated around ABI validation, object lifetime, and dynptr mutability. Useful tests should cover malformed `bpf_crypto_params`, missing or duplicate providers, module unload after context creation, authsize mismatch, zero/oversized keys, wrong SIV length, readonly destination dynptr rejection, successful encryption/decryption round trips, kptr map storage, acquire/release balancing, and RCU-safe use from XDP/TC. Provider unregister while contexts still exist should not free provider code because each context holds a module reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/devmap.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/devmap.c

## Purpose
`devmap.c` implements `BPF_MAP_TYPE_DEVMAP` and `BPF_MAP_TYPE_DEVMAP_HASH`, the map backends used by XDP `bpf_redirect_map()` to redirect packets to net devices. It is optimized for lockless datapath lookup under RCU while keeping updates, deletions, flushes, and netdevice unregister cleanup coherent.

## Important APIs, types, and functions
`struct bpf_dtab` is the map container; array maps use `netdev_map`, while hash maps use `dev_index_head`, `index_lock`, `items`, and `n_buckets`. `struct bpf_dtab_netdev` is the map value object containing the netdev reference, optional devmap XDP program, RCU head, key/index, and exposed `bpf_devmap_val`. `struct xdp_dev_bulk_queue` is a per-CPU transmit queue attached to a netdevice. Public integration functions include `dev_xdp_enqueue()`, `dev_map_enqueue()`, `dev_map_enqueue_multi()`, `dev_map_generic_redirect()`, `dev_map_redirect_multi()`, and `__dev_flush()`. Map ops are exported through `dev_map_ops` and `dev_map_hash_ops`.

## Control flow
Allocation validates key/value sizes and flags, forces `BPF_F_RDONLY_PROG`, allocates either an array of RCU netdev pointers or a power-of-two hash table, and links the map into `dev_map_list` for notifier scans. Updates copy `bpf_devmap_val`, resolve the ifindex with `dev_get_by_index()`, optionally acquire an XDP program fd compatible with `BPF_XDP_DEVMAP`, then publish the new object with `xchg()` for array maps or under `index_lock` for hash maps. Old entries are freed by RCU callback. Deletion removes the entry with `xchg()` or `hlist_del_init_rcu()` and schedules `__dev_map_entry_free()`.

The datapath looks up entries under RCU/local BH protection. XDP frame redirects validate target XDP transmit support, scatter-gather support, and MTU using `xdp_ok_fwd_dev()`, then enqueue frames in the target device's per-CPU bulk queue. `bq_xmit_all()` optionally runs a devmap-attached XDP program, transmits via `ndo_xdp_xmit`, frees unsent frames, resets the queue count, and emits tracepoints. Broadcast/multi redirect clones all but the final frame/SKB and can exclude ingress and upper devices.

## State and persistence behavior
The map persists netdevice references and optional BPF program references until update/delete/free. Per-CPU bulk queues live on netdevices with `ndo_xdp_xmit` and are allocated on `NETDEV_REGISTER`. Map free unlinks from the global list, waits for RCU and any earlier entry-free callbacks, then frees all entries and backing storage. Netdevice unregister scans all devmaps and removes matching entries before the device disappears.

## Dependencies and integration points
This file is tightly coupled with XDP redirect core (`__bpf_xdp_redirect_map()`), netdevice notifier infrastructure, `netdev_ops->ndo_xdp_xmit`, generic XDP SKB transmit, trace events, RCU, local locks, and BPF map ops. It depends on drivers calling `xdp_do_flush()` before leaving NAPI poll so queued frames are transmitted outside the lookup critical path.

## Risks and test signals
Important risks are RCU lifetime bugs, stale netdev references during unregister, flush-list leaks, incorrect clone/free ownership in multi redirect, unsupported XDP feature handling, and races among syscall update/delete, BPF redirect, and notifier removal. Tests should exercise array and hash map update/delete/lookup, value sizes with and without prog fd, redirect to devices lacking `ndo_xdp_xmit` or SG support, broadcast with ingress exclusion, netdevice unregister cleanup, XDP program actions on devmap egress, generic SKB redirect drops, and map free after pending RCU callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/devmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/disasm.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/disasm.c

## Purpose
`disasm.c` prints human-readable eBPF instructions for verifier logs, debugging, and userspace/shared disassembly contexts. It maps BPF opcode classes, ALU/jump operations, load/store sizes, helper ids, pseudo calls, kfunc calls, atomic operations, and newer special instruction encodings into stable textual output.

## Important APIs, types, and functions
The public entry points are `func_id_name()` and `print_bpf_insn()`. Static helpers include `__func_get_name()` for helper, pseudo-call, and kfunc call names; `__func_imm_name()` for ldimm64 rendering; `print_bpf_end_insn()` and `print_bpf_bswap_insn()` for endian/byteswap operations; and recognizers for signed div/mod, movsx, address-space casts, and per-CPU address moves. The file exports `bpf_class_string` and `bpf_alu_string` tables declared in `disasm.h`.

## Control flow
`print_bpf_insn()` computes the instruction class and dispatches by class. ALU/ALU64 handles endian conversion, negation, address-space cast, per-CPU address pseudo-move, register-source operations, immediate operations, signed division/modulo spelling, and sign-extending moves. `BPF_STX` handles plain stores and all supported atomic forms, including fetch variants, cmpxchg, xchg, acquire load, and release store. `BPF_ST` handles immediate stores and internal nospec. `BPF_LDX` validates normal or sign-extending memory loads. `BPF_LD` prints ABS/IND packet loads and ldimm64, masking map pointers when pointer leaks are not allowed. Jump classes print helper/kfunc/pseudo calls, gotos, gotox, may_goto, exit, and conditional jumps with 32-bit or 64-bit register names.

## State and persistence behavior
The file is stateless apart from constant string tables. It never mutates BPF programs or global state; all output goes through the callback supplied in `struct bpf_insn_cbs`. Pointer secrecy is controlled per call by the `allow_ptr_leaks` argument.

## Dependencies and integration points
The disassembler depends on UAPI/internal BPF opcode definitions, `__BPF_FUNC_MAPPER`, stringification, and callback hooks from `disasm.h`. It is used by verifier/logging paths and other components that need a formatted instruction without embedding formatting logic.

## Risks and test signals
Risks are stale opcode coverage, unsafe immediate formatting, pointer leaks for map ldimm64 instructions, and misleading output for internal pseudo encodings. Tests should format representative instructions for every class, signed div/mod, movsx widths, addr-space cast, per-CPU move, all atomics, ldabs/ldind, ldimm64 with and without pointer leak permission, helper call name fallback, pseudo call offsets, kfunc calls, may_goto, gotox, and invalid class/mode fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/disasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/disasm.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/disasm.h

## Purpose
`disasm.h` defines the callback interface and exported declarations for the BPF instruction disassembler implemented in `disasm.c`. It is deliberately small so both kernel and non-kernel builds can share the same formatting API.

## Important APIs, types, and functions
The header declares the exported opcode string tables `bpf_alu_string` and `bpf_class_string`, `func_id_name(int id)`, and `print_bpf_insn()`. It defines `bpf_insn_print_t` as a printf-style output callback, `bpf_insn_revmap_call_t` as an optional callback for resolving call instructions, and `bpf_insn_print_imm_t` as an optional callback for formatting 64-bit immediates. `struct bpf_insn_cbs` bundles those callbacks with caller-owned `private_data`.

## Control flow
There is no executable control flow in the header. Its contract is that callers provide at least a print callback and optionally provide call/immediate resolvers. `print_bpf_insn()` consumes this callback bundle, one `struct bpf_insn`, and an `allow_ptr_leaks` policy bit.

## State and persistence behavior
The header owns no state. The only persistent values are external const string tables defined in `disasm.c`. Callback private data lifetime remains the caller's responsibility.

## Dependencies and integration points
The header includes `linux/bpf.h`, `linux/kernel.h`, and `linux/stringify.h`; for non-kernel builds it also includes stdio/string headers. It is the integration point for verifier log printers, debugging code, and any userspace-compatible build that reuses the kernel disassembler source.

## Risks and test signals
The main risk is callback contract misuse: `cb_print` must match the printf annotation, optional callbacks must tolerate the instruction forms they are asked to resolve, and private data must outlive the print call. Compile tests should cover kernel and non-kernel include paths. API tests should verify custom call and immediate callbacks are honored and that callers can pass null optional callbacks without crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/disasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/dispatcher.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/dispatcher.c

## Purpose
`dispatcher.c` implements the generic BPF dispatcher, a multiway branch code generator that replaces expensive indirect BPF program calls with generated direct calls when retpolines or indirect-call costs matter. A dispatcher tracks a bounded set of BPF programs and updates a trampoline/static-call target to point at generated dispatch code or a nop fallback.

## Important APIs, types, and functions
`bpf_dispatcher_change_prog()` is the public mutation entry point. Internal helpers find existing or free slots, add/remove program references, prepare the generated image through `arch_prepare_bpf_dispatcher()`, and publish updates with `__BPF_DISPATCHER_UPDATE()`. The weak `arch_prepare_bpf_dispatcher()` returns `-ENOTSUPP` unless an architecture supplies code generation.

## Control flow
Changing a program first ignores no-op `from == to`. Under the dispatcher mutex it lazily allocates one executable packed page and one writable executable buffer, initializes kallsyms metadata, records the previous program count, removes `from`, adds `to`, and if the set changed calls `bpf_dispatcher_update()`. Update chooses one half of the page as the new image, alternating halves when an existing image is live. It prepares code into the writable mirror, copies it into the RO+X image with `bpf_arch_text_copy()`, updates the static dispatcher target to the generated image or `bpf_dispatcher_nop_func`, then waits for an RCU grace period before allowing the old half to be reused.

## State and persistence behavior
The dispatcher stores program slots, per-slot user refcounts, total program count, generated image pointers, current image offset, mutex, and kallsyms state in `struct bpf_dispatcher` supplied by the caller. Program references are acquired with `bpf_prog_inc()` and released with `bpf_prog_put()`. Generated images persist until dispatcher teardown managed elsewhere.

## Dependencies and integration points
This file integrates with architecture-specific dispatcher generation, BPF JIT executable memory allocation (`bpf_prog_pack_alloc`, `bpf_jit_alloc_exec`), text patching, static calls/macros, kallsyms registration, and RCU synchronization. It expects the arch generator to consume an array of BPF function addresses and emit valid branch code for the target trampoline ABI.

## Risks and test signals
Risks include stale direct-call targets, use-after-free of BPF programs, text patch failure leaving an old dispatcher active, incorrect half-page alternation, and architecture generator ABI mismatch. Tests should add/remove duplicate programs, exhaust `BPF_DISPATCHER_MAX`, handle allocation and arch-prepare failures, verify program refcounts, ensure fallback to nop when the last program is removed, and stress concurrent readers while changing the dispatch set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/dispatcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/dmabuf_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/dmabuf_iter.c

## Purpose
`dmabuf_iter.c` adds BPF iterator support for DMA-BUF objects. It supports the seq-file based `bpf_iter` target named `dmabuf` and also exposes open-coded iterator kfuncs so BPF programs can iterate `struct dma_buf` objects directly.

## Important APIs, types, and functions
`struct dmabuf_iter_priv` holds one retained `dma_buf` pointer across seq stop/start boundaries. `struct bpf_iter__dmabuf` is the BPF iterator context with metadata and nullable `struct dma_buf *`. Seq operations are `dmabuf_iter_seq_start()`, `dmabuf_iter_seq_next()`, `dmabuf_iter_seq_stop()`, and `dmabuf_iter_seq_show()`. Registration is described by `bpf_dmabuf_reg_info`. Open-coded iterator ABI is `struct bpf_iter_dmabuf` with kernel view `struct bpf_iter_dmabuf_kern`, plus kfuncs `bpf_iter_dmabuf_new()`, `bpf_iter_dmabuf_next()`, and `bpf_iter_dmabuf_destroy()`.

## Control flow
The seq iterator starts at `dma_buf_iter_begin()` for position zero. For later starts it resumes from the retained `p->dmabuf`, clears the retained slot, and ignores the numeric position. `next` advances with `dma_buf_iter_next()`. `stop` retains the current object so it cannot be destroyed before a resumed `start`; final iterator cleanup drops any retained reference. `show` builds a `bpf_iter_meta` and `bpf_iter__dmabuf` context, fetches the attached BPF iterator program, and runs it if present.

The open-coded kfunc iterator initializes its opaque state to null, returns the first dma-buf on the first `next`, advances on subsequent `next` calls, and drops the retained object in `destroy`.

## State and persistence behavior
Seq iterator state is per-open private data and may hold one extra dma-buf reference between `stop` and the next `start` or final release. The open-coded iterator state is caller-owned stack/storage with one retained dma-buf pointer. The registration itself is global after `late_initcall()`.

## Dependencies and integration points
The file depends on DMA-BUF iteration primitives (`dma_buf_iter_begin`, `dma_buf_iter_next`, `dma_buf_put`), BPF iterator registration, BTF id lookup for `struct dma_buf`, seq-file operations, and kfunc definition macros. `bpf_iter_reg_target()` registers the target with `BPF_ITER_RESCHED`, allowing long walks to reschedule.

## Risks and test signals
Primary risks are dma-buf reference leaks, stale pointers across seq stop/start, missing final stop callback behavior, BTF id registration failures, and opaque/kern iterator layout mismatch. Tests should open and read the `dmabuf` iterator with and without attached programs, stop/resume reads, release before resume, verify fdinfo text, iterate with the kfunc API until null, call destroy after partial and complete walks, and validate no leaked dma-buf refs under concurrent buffer creation/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/dmabuf_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/fixups.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/fixups.c

## Purpose
`fixups.c` is the verifier/JIT rewrite engine for BPF programs after verification. It patches instructions, maintains verifier metadata while program length changes, converts context accesses, removes dead code and nops, prepares BPF-to-BPF calls for JIT or interpreter fallback, rewrites helper and kfunc calls, adds security/speculation guards, inlines selected helpers and loops, and finalizes tail-call poke tracking.

## Important APIs, types, and functions
Key exported functions include `bpf_patch_insn_data()`, `bpf_clear_insn_aux_data()`, `bpf_insn_is_cond_jump()`, `bpf_opt_hard_wire_dead_code_branches()`, `bpf_opt_remove_dead_code()`, `bpf_opt_remove_nops()`, `bpf_opt_subreg_zext_lo32_rnd_hi32()`, `bpf_convert_ctx_accesses()`, `bpf_dup_insn_aux_data()`, `bpf_restore_insn_aux_data()`, `bpf_jit_subprogs()`, `bpf_fixup_call_args()`, `bpf_do_misc_fixups()`, `bpf_optimize_bpf_loop()`, and `bpf_remove_fastcall_spills_fills()`. Internals adjust subprogram starts, line info, poke descriptors, instruction-array maps, kfunc descriptors, and jump offsets.

## Control flow
Instruction patching expands or replaces one instruction and then keeps all side metadata aligned: aux data is moved/zeroed, subprogram starts are shifted, instruction-array maps and poke descriptors are adjusted, and range errors are logged. Removal performs the inverse, clearing dynamic aux fields, shrinking insns, adjusting subprograms and line info, and shifting aux records.

Optimization passes first hard-wire branches whose verified taken/untaken side is unreachable, remove unseen instruction ranges, remove nop/may_goto-zero instructions, and optionally add JIT-required zero extension or randomized high 32 bits for test mode. Context conversion injects program-type prologues/epilogues, nospec barriers, probe-memory loads for untrusted BTF/mem pointers, arena probe modes, program-specific ctx access sequences, narrow-load masks, and sign extension.

BPF-to-BPF JIT handling splits the program into subprogram `bpf_prog` objects, temporarily rewrites pseudo-call/pseudo-func immediates, compiles each function, patches final call addresses, locks subprograms read-only, registers kallsyms, and restores dump-friendly interpreter instructions. On non-fatal JIT failure it restores state for interpreter fallback; on unsupported interpreter features it rejects.

`bpf_do_misc_fixups()` is the dense final pass. It creates a hidden exception callback if needed, rewrites address-space casts, converts marked ALU64 operations to ALU32, makes div/mod exceptional cases deterministic, guards probe-memory against user addresses, expands LD_ABS/LD_IND, sanitizes pointer arithmetic for speculation, expands `may_goto`, rewrites kfunc calls, rewrites or inlines helper calls, converts map ops to direct map op calls or generated lookup sequences, sets program flags for route realm/random/override/tail calls, adds tail-call poke descriptors, handles timer callback aux, per-CPU allocation pointer calls, tracing arg/ret/ip helpers, branch snapshot, jiffies, current task/cpu helpers, and kptr xchg. It then initializes extra may_goto stack slots, publishes poke tracking, and sorts kfunc descriptors by final call immediate/offset.

## State and persistence behavior
The file mutates `env->prog`, `env->insn_aux_data`, `env->subprog_info`, line info, map poke tables, kfunc tables, and program aux fields. Many rewrites are persistent changes to the loaded program image; some temporary JIT changes are restored for interpreter/dump consistency. Memory state includes vmalloc aux copies, subprogram arrays, JIT images, exception tables, and kfunc descriptor sorting.

## Dependencies and integration points
It integrates with the verifier environment, BPF JIT core, BTF/kfunc tables, map ops, tail-call poke tracking, offload hooks, XDP/socket/ctx access converters, perf branch snapshot static calls, architecture support flags, disassembler helper names for errors, and BPF instruction array maps.

## Risks and test signals
Risks are metadata drift after patch/remove, jump offset overflow, incorrect line/subprogram info, unsafe fallback after failed JIT, helper rewrite ABI mismatches, verifier-approved access becoming unsafe after conversion, tail-call poke mis-tracking, and architecture feature condition bugs. Tests should include dead-code/nop removal with BTF line info, ctx narrow loads, nospec insertion, untrusted BTF probe loads, arena loads/stores, all div/mod edge cases, LD_ABS/IND rewrite, pointer arithmetic sanitization, timed and untimed may_goto, BPF-to-BPF JIT success/failure/fallback, kfunc far/near calls, map lookup inlining, tail-call poke setup, tracing helpers, branch snapshot, loop inlining, and fastcall spill/fill removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/fixups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/hashtab.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/hashtab.c

## Purpose
`hashtab.c` implements the kernel BPF hash-map family: normal hash, LRU hash, per-CPU hash, LRU per-CPU hash, and hash-of-maps. It provides allocation, lookup, update, delete, lookup-and-delete, batch operations, BPF iterators, callback iteration, memory accounting, BTF field destructors, and JIT lookup generation.

## Important APIs, types, and functions
`struct bpf_htab` embeds `struct bpf_map` and owns bucket array, allocators, preallocated element pool or LRU, optional extra per-CPU elements, counters, bucket count, element size, and hash seed. `struct bucket` combines a nulls hlist with `rqspinlock_t`. `struct htab_elem` stores hash/list/LRU/freelist state followed by aligned key and value or per-CPU pointer. Map ops are `htab_map_ops`, `htab_lru_map_ops`, `htab_percpu_map_ops`, `htab_lru_percpu_map_ops`, and `htab_of_maps_map_ops`.

## Control flow
Allocation validates flags, preallocation/LRU constraints, key/value sizes, zero-seed permission, NUMA restrictions, and per-CPU size limits. It allocates buckets, initializes hash seed, chooses per-CPU counter versus atomic count, and either preallocates all elements plus freelist/LRU state or initializes `bpf_mem_alloc` caches. Preallocated normal maps may allocate per-CPU extra elements so replacement can avoid pop/push while holding a bucket lock.

Lookup hashes the key with jhash, selects a bucket, and walks a nulls hlist under RCU; LRU lookups optionally mark the element referenced. Generated lookup paths call `__htab_map_lookup_elem()` directly and adjust the returned element pointer to the value, with special per-CPU and map-in-map variants.

Updates lock the target bucket after hashing. Normal non-per-CPU updates allocate a replacement element, insert it at the head, then unlink and free the old element after unlock for non-prealloc maps. `BPF_F_LOCK` can update an existing element in place under the element spin lock. LRU updates allocate/pop from LRU before taking the bucket lock to preserve lock ordering. Per-CPU and map-in-map updates modify values in place when the key already exists. Deletes unlink under the bucket lock and free or return the node to LRU/freelist afterward. Batch lookup/delete scans buckets, optionally locks non-empty buckets, stages keys/values outside user-copy regions, and defers freeing deleted nodes until after bucket unlock.

Iterator support walks buckets under RCU using seq-file callbacks, keeps bucket/skip state, copies per-CPU values into a temporary buffer, and runs attached BPF iterator programs. `bpf_for_each_hash_elem()` iterates under migration-disabled context and invokes a BPF callback with current-CPU value for per-CPU maps.

## State and persistence behavior
Persistent map state includes bucket chains, preallocated storage or allocator caches, LRU/freelist ownership, per-CPU value areas, map-in-map inner references, BTF special fields, and element counters. Free paths distinguish preallocated and dynamic maps, free special BTF fields, release inner map references, destroy allocators/counters, and release buckets/map storage. Dynamic maps rely on `bpf_mem_alloc` for RCU-safe freeing.

## Dependencies and integration points
This file integrates with BPF map core, BTF record management, BPF memory allocators, pcpu freelist, LRU list, map-in-map helpers, RCU/nulls hlist, rqspinlock/raw locking, syscall batch APIs, BPF iterators, JIT helper inlining via `map_gen_lookup`, and verifier map op contracts.

## Risks and test signals
Risks include bucket/LRU lock inversion, RCU lookup races, incorrect count accounting under prealloc vs dynamic allocation, per-CPU value leaks or wrong CPU selection, BTF field destructor omissions, map-in-map reference leaks, batch user-copy error handling, nulls-list restart bugs, and generated lookup mismatches. Tests should cover all map variants with prealloc and no-prealloc where allowed, update flags (`BPF_ANY`, `BPF_EXIST`, `BPF_NOEXIST`, `BPF_F_LOCK`, per-CPU CPU flags), LRU eviction, concurrent lookup/update/delete, lookup-and-delete, batch lookup/delete with small buffers and faults, iterator stop/resume, callback iteration early stop, memory accounting, zero-seed permission, BTF fields, and hash-of-maps fd lookup/update/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/hashtab.c -->
