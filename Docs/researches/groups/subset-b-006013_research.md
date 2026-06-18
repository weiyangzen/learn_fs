# subset-b-006013 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cfg.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/cfg.c

## Purpose
`cfg.c` implements verifier control-flow graph support for eBPF programs. It checks reachability and illegal loops, records jump and prune points used by state pruning, builds jump-table metadata for indirect `gotox` branches, models hidden abnormal exits for `tail_call` and `LD_ABS`/`LD_IND`, and computes postorder plus strongly connected components for later verifier analyses.

## Important APIs, types, and functions
The file uses `env->cfg.insn_state`, `env->cfg.insn_stack`, `env->cfg.insn_postorder`, `env->insn_aux_data[*].jt`, `env->subprog_info`, and `env->scc_info`. `bpf_check_cfg()` is the main validation pass. `visit_insn()`, `push_insn()`, `visit_func_call_insn()`, `visit_gotox_insn()`, and `visit_abnormal_return_insn()` encode successor discovery. `bpf_iarray_realloc()` and `bpf_copy_insn_array_uniq()` support dynamic successor arrays. `bpf_compute_postorder()` fills instruction postorder ranges per subprogram, and `bpf_compute_scc()` assigns nonzero SCC IDs to real or implicit loops.

## Control flow
`bpf_check_cfg()` allocates arrays sized to `env->prog->len`, starts DFS at instruction 0, and optionally walks the exception callback subprogram if it was not reached from main. `push_insn()` validates branch targets, labels fall-through and branch edges, rejects back edges for unprivileged programs, and records branch targets as prune and jump points. `visit_insn()` routes by opcode class: non-branch instructions fall through, subprogram calls add a callee edge plus a return edge, helper/kfunc calls may mark sleep or packet-data side effects, tail calls and packet absolute loads get an abnormal exit edge, direct jumps have one successor, conditional jumps have two successors, and `BPF_JA | BPF_X` expands through a verifier-discovered jump table.

## State and persistence
All state is verifier-lifetime state. Temporary DFS arrays are freed before `bpf_check_cfg()` returns. Jump-table arrays stored in `insn_aux_data[t].jt` persist for later verifier passes. The pass also persists derived flags into `prog->aux->changes_pkt_data`, `prog->aux->might_sleep`, subprogram side-effect flags, `insn_postorder`, and SCC IDs. There is no on-disk or runtime persistence outside the loaded BPF program metadata.

## Dependencies and integration points
This file depends on verifier helpers such as `mark_prune_point`, `mark_jmp_point`, `bpf_insn_successors`, `bpf_find_containing_subprog`, helper/kfunc metadata lookup, BPF instruction decoding macros, and BPF array maps used as instruction arrays. It feeds later verifier phases including constant folding, liveness, state convergence, iterator loop handling, and `may_goto` timed-loop analysis.

## Risks and test signals
Key risks are off-by-one branch targets, jumps into the second half of `ldimm64`, inaccurate subprogram side-effect propagation, treating all instruction-array maps as jump tables, stale jump table bounds across subprograms, abnormal exit modeling mismatches, DFS stack overflow, and SCC mislabeling around callbacks or self edges. Test signals include verifier tests for unreachable instructions, backward branches with and without privilege, indirect `gotox` tables, tail call hidden exits, `LD_ABS` in subprograms, callbacks requiring convergence checkpoints, exception callback reachability, branch pruning point coverage, and SCC IDs on loops, self loops, and acyclic code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cgroup.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/cgroup.c

## Purpose
`cgroup.c` is the core implementation for BPF programs attached to cgroups. It manages cgroup program lists, effective inherited program arrays, cgroup BPF links, cgroup local storage, cgroup lifetime cleanup, LSM cgroup attach slots, and execution hooks for networking, devices, sysctl, socket options, and LSM shims.

## Important APIs, types, and functions
Global state includes `cgroup_bpf_enabled_key[]`, `cgroup_bpf_destroy_wq`, and, with `CONFIG_BPF_LSM`, the `cgroup_lsm_atype[]` slot table. Attachment and lifetime functions include `cgroup_bpf_inherit()`, `update_effective_progs()`, `__cgroup_bpf_attach()`, `__cgroup_bpf_detach()`, `cgroup_bpf_prog_attach()`, `cgroup_bpf_link_attach()`, `cgroup_bpf_replace()`, and `cgroup_bpf_release()`. Execution entry points include `__cgroup_bpf_run_filter_skb()`, `__cgroup_bpf_run_filter_sk()`, `__cgroup_bpf_run_filter_sock_addr()`, `__cgroup_bpf_run_filter_sock_ops()`, `__cgroup_bpf_check_dev_permission()`, `__cgroup_bpf_run_filter_sysctl()`, and the sockopt filter functions. Helper prototypes include `bpf_get_local_storage`, `bpf_get_retval`, `bpf_set_retval`, sysctl helpers, and sockopt helpers.

## Control flow
Cgroup lifetime online initializes a per-cgroup `percpu_ref`, inherits parent program arrays, and takes parent BPF references. Offline kills the refcount and schedules cleanup on the dedicated workqueue. Attach validates flag combinations, revision, hierarchy override rules, duplicate or replacement targets, per-cgroup storage, and LSM trampoline shims. It then recomputes effective arrays for the target cgroup and descendants before publishing them with RCU. Detach marks the target list entry inactive, recomputes descendants, falls back to purging array slots with a dummy program on allocation failure, and releases program/link references. Link release calls the same detach path while protecting against auto-detach from a dying cgroup. Execution hooks resolve the current or socket cgroup, install a `bpf_cg_run_ctx`, iterate the effective program array, combine return values and flags, and map BPF return semantics into kernel-specific decisions.

## State and persistence
State is runtime kernel state attached to `struct cgroup::bpf`: direct `progs[]` hlist entries, `effective[]` RCU program arrays, `flags[]`, revision counters, inactive arrays during recompute, linked cgroup storage objects, and the lifetime refcount. Program arrays persist while cgroups and links/progs remain alive and are freed after RCU grace periods. Storage is keyed by cgroup inode ID and attach type. There is no disk persistence; all attachment state disappears with cgroup/program/link lifetimes.

## Dependencies and integration points
The file integrates with the cgroup core notifier chain, `cgroup_mutex`, BPF syscall attach/query/link APIs, BPF trampoline support for cgroup LSM programs, socket and networking stacks, sysctl handlers, sockopt paths, device cgroup checks, BPF local storage maps, RCU and percpu refs, verifier ops for cgroup program types, and static keys used by fast paths to skip hooks when no programs are attached.

## Risks and test signals
Major risks include cgroup lifetime races with link release, incorrect inheritance under `ALLOW_OVERRIDE`, `ALLOW_MULTI`, `PREORDER`, `BEFORE`, and `AFTER`, stale effective arrays after attach failure, refcount leaks for parent cgroups, programs, links, storage, and LSM slots, revision compare mistakes, LSM trampoline double unlink, and return-value translation bugs in egress, sysctl, and sockopt paths. Test signals include attach/detach/query across hierarchy depth, multi-attach ordering and replacement, revision `-ESTALE`, cgroup deletion with live links, cgroup storage reuse, LSM cgroup slot exhaustion, concurrent socket/sysctl/sockopt execution during detach, effective query output, and verifier access checks for device, sysctl, and sockopt contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cgroup_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/cgroup_iter.c

## Purpose
`cgroup_iter.c` implements BPF iterator support for cgroup hierarchies and open-coded cgroup subsystem-state iterators exposed as kfuncs. It lets iterator programs walk descendants in pre-order or post-order, ancestors, a single cgroup, or direct children, and emits `struct cgroup *` context values to BPF.

## Important APIs, types, and functions
Important types are `struct bpf_iter__cgroup`, `struct cgroup_iter_priv`, opaque `struct bpf_iter_css`, and internal `struct bpf_iter_css_kern`. The seq-file path is implemented by `cgroup_iter_seq_start()`, `cgroup_iter_seq_next()`, `cgroup_iter_seq_stop()`, and `cgroup_iter_seq_show()`. Target registration uses `bpf_cgroup_reg_info` and `bpf_cgroup_iter_init()`. Attach and metadata functions are `bpf_iter_attach_cgroup()`, `bpf_iter_detach_cgroup()`, `bpf_iter_cgroup_show_fdinfo()`, and `bpf_iter_cgroup_fill_link_info()`. Kfuncs are `bpf_iter_css_new()`, `bpf_iter_css_next()`, and `bpf_iter_css_destroy()`.

## Control flow
Iterator attach validates the requested order, resolves either a cgroup fd, cgroup id, or root path, and stores a referenced start cgroup in iterator aux data. Seq initialization takes an additional CSS reference for the read session. `start()` locks the cgroup hierarchy and refuses multi-session reads: if user space resumes after `pos > 0` before the walk completed, it returns `-EOPNOTSUPP`. `next()` advances using the cgroup core traversal helper matching the selected order. `show()` skips dead cgroups, prepares `bpf_iter_meta`, and runs the iterator program; nonzero program return sets `terminate`. `stop()` unlocks and, on normal completion, calls the program once with a NULL cgroup for epilogue processing.

## State and persistence
Iterator state is per-link and per-read-session only. Aux data holds the start cgroup and traversal order for the link. Seq private state holds `start_css`, `visited_all`, `terminate`, and `order`. CSS references keep the start node alive during iteration. The kfunc iterator stores start, current position, and flags in the opaque object supplied by the BPF program. No persistent storage exists.

## Dependencies and integration points
This file depends on cgroup traversal APIs, `cgroup_mutex`, seq-file based BPF iterator infrastructure, BTF IDs for `struct cgroup`, fdinfo/link-info reporting, and verifier context metadata using `PTR_TO_BTF_ID_OR_NULL | PTR_TRUSTED`. The kfunc iterator depends on BPF kfunc registration elsewhere and on the same CSS traversal helpers.

## Risks and test signals
Risks include the single-session seq limitation surprising readers, dead cgroups being skipped silently, holding `cgroup_mutex` while running iterator programs, refcount imbalance between attach and seq init/fini, namespace-sensitive fdinfo paths, and opaque iterator size/alignment drift. Test signals include all five traversal orders, fd-vs-id-vs-root attach, invalid order rejection, early termination, NULL final callback, dead cgroup skip, partial reads returning `-EOPNOTSUPP`, fdinfo path under cgroup namespaces, and kfunc iterator behavior for descendants, children, and ancestors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cgroup_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/check_btf.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/check_btf.c

## Purpose
`check_btf.c` validates BTF metadata supplied with a BPF program load. It handles function info, line info, and CO-RE relocations, links BTF function names into verifier subprogram metadata, and enforces that abnormal-return instructions in subprograms have compatible BTF return types.

## Important APIs, types, and functions
The public entry points are `bpf_check_btf_info_early()` and `bpf_check_btf_info()`. Validation helpers include `check_abnormal_return()`, `check_btf_func_early()`, `check_btf_func()`, `check_btf_line()`, and `check_core_relo()`. State is stored in `prog->aux->btf`, `func_info`, `func_info_cnt`, `func_info_aux`, `linfo`, `nr_linfo`, and each `subprog_info[*].name` and `linfo_idx`.

## Control flow
The early pass obtains the user BTF by fd when func or line info is present, rejects kernel BTF as program metadata, copies function records with tail-zero checks, validates record sizes, strictly increasing instruction offsets, and BTF func/prototype type IDs, and stores the records. If no func info is present, it rejects `LD_ABS` or `tail_call` in non-main subprograms because return type information is unavailable. The later pass requires the number of func records to match subprogram count, checks each func record offset against the verifier subprogram layout, records linkage and names, validates abnormal-return subprograms return a scalar int-like type, validates line records and subprogram coverage, and applies CO-RE relocation records one at a time to target instructions.

## State and persistence
BTF, function info, auxiliary function info, and line info persist in `bpf_prog_aux` for the lifetime of the loaded program and are later used by verifier diagnostics, kallsyms names, stack/source reporting, and JIT line mappings. CO-RE relocations mutate the program instruction stream during load; relocation records themselves are not retained here. Failed checks free newly allocated arrays on the failing path, while the retained BTF reference is owned by the program aux after early success.

## Dependencies and integration points
The file depends on BPF syscall load attributes, `bpfptr_t` copy helpers for user or kernel attributes, BTF type lookup and string lookup, verifier-discovered subprogram layout, `bpf_core_apply()`, and program aux metadata consumed by `core.c` and verifier logging. It is tightly ordered with subprogram discovery: early function record validation can run before final subprogram matching, and the full pass relies on `env->subprog_info`.

## Risks and test signals
Risks include record-size compatibility bugs, nonzero tail handling, leaked BTF references after partial failure, mismatches between BTF func offsets and subprogram discovery, missing line records for subprogram starts, allowing abnormal returns from non-int functions, and CO-RE relocation offset unit confusion because relocations use byte offsets divided by 8. Test signals include old and new record sizes, invalid type IDs, non-monotonic offsets, no-BTF subprograms with `LD_ABS` or `tail_call`, func count mismatch, line info covering every subprogram, malformed BTF strings, CO-RE relocation bounds, and user-kernel attribute pointer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/check_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/const_fold.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/const_fold.c

## Purpose
`const_fold.c` performs a verifier dataflow analysis that discovers constant register values at instruction boundaries and uses them to rewrite conditional branches with known outcomes. This removes dead CFG edges before liveness analysis and improves later verifier precision.

## Important APIs, types, and functions
The central type is `struct const_arg_info`, whose state can be unvisited, unknown, known constant, map pointer, map value pointer, or subprogram pointer. `const_reg_xfer()` is the instruction transfer function, `const_reg_join()` merges predecessor outputs into successor inputs, `bpf_compute_const_regs()` runs the fixed-point pass and records results in `insn_aux_data`, `eval_const_branch()` evaluates conditional predicates, and `bpf_prune_dead_branches()` rewrites constant conditional jumps to `BPF_JMP_A`.

## Control flow
`bpf_compute_const_regs()` allocates an input state array per instruction and initializes every subprogram entry register to unknown. It iterates over reverse postorder until no successor state changes. The transfer function handles constant moves, sign-extending moves, simple add/sub/and operations, 64-bit immediates, map pointer and map-value pseudo loads, subprogram pseudo loads, read-only direct map-value loads, call clobbering of R0-R5, and selected atomic side effects. After convergence it saves only 32-bit constants plus map pointer and subprogram identifiers into each instruction aux record. `bpf_prune_dead_branches()` then scans conditional jumps, skips `may_goto`, fetches recorded constant operands, applies 32-bit signed casts for `BPF_JMP32`, evaluates the branch, rewrites it into an unconditional jump to either the taken target or fall-through, and recomputes postorder if anything changed.

## State and persistence
The analysis workspace is temporary and freed after the pass. Persisted state is per-instruction aux metadata: `const_reg_mask`, `const_reg_map_mask`, `const_reg_subprog_mask`, and `const_reg_vals[]`. Branch rewrites persist by modifying `env->prog->insnsi` and replacing `env->cfg.insn_postorder` with a recomputed order after CFG changes. No runtime state is introduced.

## Dependencies and integration points
This pass depends on postorder computed by `cfg.c`, successor information from `bpf_insn_successors()`, verifier map metadata, direct-read support for read-only maps, and subprogram lookup. It feeds liveness and later verifier optimization paths that use `insn_aux_data` constants. It also depends on the verifier having already resolved pseudo map references into `env->used_maps` indices.

## Risks and test signals
Risks include unsound constant propagation across calls, incomplete handling of ALU operations, map value direct-read races if a map is not truly read-only, losing 64-bit constants because only 32-bit values are saved for branch pruning, signed/unsigned comparison mistakes for `BPF_JMP32`, and failing to recompute dependent CFG metadata after rewrites. Test signals include constant branches with K and X sources, 32-bit signed comparisons, read-only map value loads, non-read-only map loads remaining unknown, subprogram entry isolation, call clobbers, atomic fetch/CMPXCHG behavior, `may_goto` not pruned, and liveness not propagating through pruned edges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/const_fold.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/core.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/core.c

## Purpose
`core.c` is the central BPF runtime implementation. It allocates and frees `struct bpf_prog`, hashes and patches instructions, manages JIT memory and kallsyms registration, implements the interpreter when JIT is not mandatory, selects the execution runtime, manages program arrays, provides built-in and weak helper definitions, initializes global BPF memory allocation, emits BPF tracepoints, and supports source-line and stack-to-program lookup.

## Important APIs, types, and functions
Important allocation and metadata APIs include `bpf_prog_alloc_no_stats()`, `bpf_prog_alloc()`, `bpf_prog_realloc()`, `__bpf_prog_free()`, `bpf_prog_calc_tag()`, `bpf_prog_fill_jited_linfo()`, `bpf_patch_insn_single()`, and `bpf_remove_insns()`. JIT and symbol functions include `bpf_prog_kallsyms_add()`, `bpf_prog_kallsyms_del()`, `bpf_address_lookup()`, `bpf_jit_binary_alloc()`, `bpf_jit_binary_pack_alloc()`, `bpf_jit_blind_constants()`, `bpf_prog_select_runtime()`, and many weak architecture hooks. Runtime support includes `___bpf_prog_run()`, generated stack-size-specific interpreter wrappers, `bpf_patch_call_args()`, `bpf_prog_array_*()` helpers, `bpf_prog_free()`, `bpf_user_rnd_u32()`, `bpf_get_raw_cpu_id()`, `bpf_find_linfo()`, and `bpf_prog_find_from_stack()`.

## Control flow
Program allocation reserves vmalloc instruction storage, aux data, active context tracking, optional stats, mutexes, and syscall stream state. Program patching expands or removes instructions while adjusting branch offsets and line info. Runtime selection chooses an interpreter wrapper by verified stack depth unless JIT is required, allocates JIT line-info storage, optionally clones and blinds constants, invokes the architecture JIT, checks tail-call map compatibility after final JIT/interpreter status is known, and locks the program read-only. The interpreter is a computed-goto dispatch loop covering ALU, jumps, calls, tail calls, memory, probe-memory, atomics, acquire/release operations, and exit. Program free is deferred to workqueue context where maps, BTFs, trampolines, subprograms, device-bound state, cgroup attach slots, and executable memory are released.

## State and persistence
Loaded program state persists in `struct bpf_prog` and `struct bpf_prog_aux`: instruction image, aux metadata, maps, BTFs, JIT image, line info, kallsyms nodes, program arrays, stats, tokens, and association locks. Global runtime state includes `bpf_global_ma`, JIT sysctl knobs and memory charge counters, the BPF kallsyms latch tree/list, the program pack allocator list, static `bpf_empty_prog_array`, per-CPU random state, and `bpf_stats_enabled_key`. Persistence is kernel-runtime only; unloading a program schedules deferred teardown and RCU frees where needed.

## Dependencies and integration points
This file integrates nearly every BPF subsystem: verifier output, JIT back ends, execmem, kallsyms and stack unwinding, RCU, BTF line info, program/map ownership compatibility, cgroup BPF, offload, struct ops, trampolines, perf callchain buffers, memory cgroups, helper prototypes from syscall and networking code, tracepoints, and architecture hooks for text patching, exception support, arenas, private stacks, and timed `may_goto`.

## Risks and test signals
Risks include branch-offset overflow during patching, aux ownership errors while cloning/blinding/reallocating, executable memory leaks or permission mistakes, JIT charge accounting bypass, kallsyms lifetime races, interpreter/JIT semantic drift, tail-call compatibility computed too early or too late, deferred free ordering with maps/BTF/trampolines, global pack allocator fragmentation, and weak hook defaults causing unexpected `-ENOTSUPP`. Test signals include interpreter vs JIT conformance, constant blinding with branches and `ldimm64`, patch/remove instruction stress, JIT pack allocation and free, kallsyms lookup during program unload, tail-call map compatibility for mixed program types, BTF line lookup for subprograms, deferred free with used maps and kfunc BTFs, `BPF_JIT_ALWAYS_ON`, and timed `may_goto` violation reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cpumap.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/cpumap.c

## Purpose
`cpumap.c` implements `BPF_MAP_TYPE_CPUMAP`, an XDP redirect backend that moves XDP frames or generic skb redirects to per-CPU kernel threads. It isolates early XDP processing from normal network stack work and can optionally run a second XDP program on the target CPU before building or receiving skbs.

## Important APIs, types, and functions
Core types are `struct bpf_cpu_map`, `struct bpf_cpu_map_entry`, and per-CPU `struct xdp_bulk_queue`. Map operations are exposed through `cpu_map_ops`: `cpu_map_alloc()`, `cpu_map_update_elem()`, `cpu_map_delete_elem()`, `cpu_map_lookup_elem()`, `cpu_map_get_next_key()`, `cpu_map_free()`, `cpu_map_mem_usage()`, and `cpu_map_redirect()`. Runtime functions include `cpu_map_enqueue()`, `cpu_map_generic_redirect()`, `__cpu_map_flush()`, `cpu_map_kthread_run()`, `cpu_map_bpf_prog_run_xdp()`, `cpu_map_bpf_prog_run_skb()`, and `__cpu_map_entry_replace()`.

## Control flow
Map creation validates key and value sizes, flags, and `max_entries <= NR_CPUS`, then allocates an RCU pointer array. Updating an element validates map flags, target CPU, qsize, and optional XDP program fd, allocates per-CPU bulk queues, a `ptr_ring`, GRO node, optional attached `BPF_XDP_CPUMAP` program, and a bound kthread. The new entry is atomically swapped into the map; the old entry is freed through `queue_rcu_work()` after readers and pending flushes drain. XDP enqueue stores frames in a per-CPU bulk queue and links it into the current BPF net context flush list. Flush moves batched frames into the target ring and wakes the kthread. The kthread consumes frames/skbs, optionally runs the cpumap program under RCU and BPF net context, handles pass/drop/redirect results, builds skbs from frames, feeds GRO, emits tracepoints, and exits only after stop is requested and the ring is empty.

## State and persistence
State is per map and per populated CPU entry: RCU pointer slots, qsize, target CPU, map id, per-CPU bulk queues, ptr ring contents, kthread, optional BPF program reference, GRO state, completion, and deferred free work. Entries persist until map update/delete/free, then remain reachable through RCU until enqueue/flush critical sections finish. Packet queues are transient and intentionally short-lived across a NAPI poll and kthread processing cycle.

## Dependencies and integration points
This file integrates XDP redirect helpers, BPF map APIs, RCU and local locks, ptr rings, kthreads, workqueues, GRO, skb allocation caches, netdevice/XDP frame conversion, BPF net context flush lists, tracepoints, and optional cpumap XDP programs checked by `bpf_prog_map_compatible()`. Generic skb redirect uses a tagged pointer bit to distinguish skbs in the same ring.

## Risks and test signals
Risks include target CPU hotplug assumptions, RCU lifetime races between map updates and NAPI flush, producer ring overflow and frame return correctness, tagged skb pointer handling, kthread stop ordering, GRO flush latency, optional program compatibility errors, qsize memory pressure, and map memory accounting that omits dynamic entry allocations. Test signals include update/delete/free under redirect load, qsize zero delete behavior, invalid CPU rejection, cpumap program pass/drop/redirect paths, generic skb redirect paths, ring-full drops, kthread wake and drain on teardown, tracepoint counters, GRO behavior under empty and non-empty rings, and map lookup under RCU/read-bh contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cpumap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cpumask.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/cpumask.c

## Purpose
`cpumask.c` exposes refcounted cpumask objects and cpumask operations to BPF programs as kfuncs. It lets tracing, struct_ops, and syscall BPF programs create mutable masks, acquire and release references, query and mutate bits, combine masks, select CPUs, count bits, and populate a cpumask from BPF memory.

## Important APIs, types, and functions
The core type is `struct bpf_cpumask`, which embeds `cpumask_t` as its first field and a `refcount_t`. Allocation uses the global `bpf_cpumask_ma` BPF memory allocator. Lifetime kfuncs are `bpf_cpumask_create()`, `bpf_cpumask_acquire()`, `bpf_cpumask_release()`, and `bpf_cpumask_release_dtor()`. Operation kfuncs include first/first_zero/first_and, set/clear/test/test_and_set/test_and_clear, setall/clear, and/or/xor/copy, equal/intersects/subset/empty/full, any_distribute/any_and_distribute, weight, and `bpf_cpumask_populate()`. Registration is done by `cpumask_kfunc_init()`.

## Control flow
`bpf_cpumask_create()` allocates from the BPF memory cache, zeroes the object, verifies first-field layout for casting to `struct cpumask`, and starts refcount at one. `acquire()` increments the refcount and returns the same trusted pointer. `release()` decrements and frees through the BPF allocator's RCU-safe free path on the final reference; the destructor calls the same release function for kptr map ownership. Bit operations validate CPU indices against `nr_cpu_ids` where they target a single CPU, then delegate to kernel cpumask helpers. Registration initializes the allocator, registers the kfunc set for tracing, struct_ops, and syscall program types, and registers the destructor BTF mapping.

## State and persistence
Each `bpf_cpumask` persists while references exist, including references held as BPF kptrs in maps. Final release is RCU-safe through `bpf_mem_cache_free_rcu()`. The kfunc registration and allocator persist for the life of the kernel/module. Mask contents are mutable runtime state only and are not stored outside BPF-managed objects unless a program copies them elsewhere.

## Dependencies and integration points
The file depends on kernel cpumask APIs, BPF kfunc and BTF ID registration, BPF memory allocator, refcounting, CFI annotations for the destructor, verifier acquire/release semantics (`KF_ACQUIRE`, `KF_RELEASE`, `KF_RET_NULL`, `KF_RCU`), and kptr destructor infrastructure. The first-field layout enables passing a `struct bpf_cpumask *` to helpers expecting `struct cpumask *`.

## Risks and test signals
Risks include refcount leaks or double releases through kptr movement, verifier trust mistakes for mutable vs const mask pointers, CPU bounds differences between `nr_cpu_ids`, `nr_cpumask_bits`, and possible CPUs, alignment and size checks in `bpf_cpumask_populate()`, allocator initialization failures stopping kfunc registration, and race expectations when multiple BPF contexts mutate the same mask. Test signals include acquire/release lifetime tests with map kptrs, invalid CPU operations, all boolean cpumask operations, distribution helpers on empty and non-empty masks, populate with too-small or unaligned memory, registration for the three program types, destructor invocation on map cleanup, and RCU use-after-free tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/cpumask.c -->
