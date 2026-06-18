# subset-b-006010 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/auditsc.c -->
# sources/distributed-fs/ceph-client/kernel/auditsc.c

Purpose: implements Linux syscall-specific audit context management, filtering, object/name collection, and final audit record emission for syscalls and io_uring operations. It is the bridge between generic audit rules and concrete kernel events such as execve, filesystem paths, IPC, POSIX message queues, seccomp, ptrace, capabilities, netfilter config changes, and core dumps.

Important APIs/types/functions: global knobs include `audit_n_rules` and `audit_signals`. Local aux structures store PID targets, bprm file capabilities, audit-tree refs, and netfilter operation names. Core lifecycle APIs are `audit_alloc`, `__audit_free`, `__audit_syscall_entry`, `__audit_syscall_exit`, `__audit_uring_entry`, and `__audit_uring_exit`. Filtering is centered on `audit_filter_rules`, `__audit_filter_op`, `audit_filter_task`, `audit_filter_syscall`, `audit_filter_uring`, and `audit_filter_inodes`. Object collection APIs include `__audit_getname`, `__audit_inode`, `__audit_file`, and exported `__audit_inode_child`. Event-specific capture APIs include `__audit_mq_*`, `__audit_ipc_*`, `__audit_bprm`, `__audit_socketcall`, `__audit_sockaddr`, `__audit_ptrace`, `audit_signal_info_syscall`, `__audit_log_bprm_fcaps`, `__audit_log_capset`, `__audit_openat2_how`, `__audit_log_nfcfg`, `audit_core_dumps`, and `audit_seccomp`.

Control flow: task creation calls `audit_alloc`, which runs task filters and installs a per-task `audit_context` plus syscall audit work if auditing is relevant. Syscall entry populates architecture, syscall number, arguments, timestamp, and context state. During syscall execution, VFS and subsystem hooks append names, inodes, sockets, IPC metadata, capabilities, module names, and other aux records. Exit fixes restart return codes, evaluates syscall and inode filters, kills pending watched trees if needed, and emits a main `AUDIT_SYSCALL` or `AUDIT_URINGOP` record followed by aux, special, fd pair, socket address, PID target, cwd, path, proctitle, and EOE records. io_uring follows a parallel path and has special handling when an uring operation runs while a syscall context is already active.

State and persistence: all event state is transient in `task_struct->audit_context`; path/name objects and aux records are freed by `audit_reset_context` after each syscall/uring event or by `audit_free_context` at task exit. The file keeps reusable tree-ref arrays attached to a context until context free. Audit records persist only through the audit logging subsystem, not in this file. RCU protects rule lists, inode hash checks, task creds, audit tree lookups, and LSM label use.

Dependencies and integration: depends on `kernel/audit.h`, audit rule lists, audit watches/trees, fsnotify marks, VFS namei/dentry/inode data, LSM security label helpers, credentials, namespaces, seccomp, io_uring hooks, POSIX mqueue, IPC, netfilter nftables/xtables enums, fanotify audit responses, and architecture syscall metadata. `__audit_inode_child` and `__audit_log_nfcfg` are GPL exports used outside this compilation unit.

Risks: this is a high-risk security/audit path. Lost allocations can mark contexts auditable or lose detail; name/inode matching must avoid double references and must handle rename races; `audit_log_execve_info` intentionally handles user memory carefully to avoid double-fetch trust; LSM matching treats temporary errors as matches to avoid missing records; path and tree-ref handling must remain balanced to avoid leaks or missed watched-directory matches. Filter priority and `filterkey` replacement order affect which rule annotates an event.

Test signals: audit syscall and path rule tests, audit-testsuite coverage for execve/proctitle/capabilities/mqueue/IPC/seccomp, io_uring audit tests, LSM audit rule tests, netfilter config audit tests, and stress tests involving rename races and failed allocations are relevant. Kernel warnings in tree ref handling, unmatched context states, or missing EOE/path records are strong regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/auditsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/backtracetest.c -->
# sources/distributed-fs/ceph-client/kernel/backtracetest.c

Purpose: a small loadable module regression test that deliberately emits stack traces from process context, BH workqueue context, and, when available, saved stack-trace APIs.

Important APIs/types/functions: `backtrace_test_normal` calls `dump_stack`; `backtrace_test_bh` queues `backtrace_test_bh_workfn` on `system_bh_wq` and waits with `flush_work`; `backtrace_test_saved` uses `stack_trace_save` and `stack_trace_print` under `CONFIG_STACKTRACE`; `backtrace_regression_test` is the `module_init` entry point.

Control flow: module initialization prints a banner, emits a direct stack dump, schedules and flushes BH-context work that dumps another stack, optionally captures and prints an array of saved return addresses, then prints an end banner. Module exit is intentionally empty.

State and persistence: uses one static `DECLARE_WORK` item and a stack-local `entries[8]` buffer for saved traces. It does not persist data beyond kernel logs.

Dependencies and integration: integrates with module loading, kernel workqueues, `dump_stack`, and optional `CONFIG_STACKTRACE`. Its output appears in the kernel log and is expected to look alarming while being a self-test.

Risks: false-positive bug reports are expected if users miss the banner. Test value depends on architecture stack unwinding quality and workqueue availability. The module does not assert results, so regressions are detected manually or by log inspection.

Test signals: successful load should show three self-test phases where saved trace is either printed or explicitly skipped. Oopses, missing workqueue trace, or stacktrace API build failures indicate regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/backtracetest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bounds.c -->
# sources/distributed-fs/ceph-client/kernel/bounds.c

Purpose: build-time generator that emits constants for `include/generated/bounds.h` through kbuild's `DEFINE()` mechanism.

Important APIs/types/functions: `main` calls `DEFINE` for `NR_PAGEFLAGS`, `MAX_NR_ZONES`, optional `NR_CPUS_BITS`, `SPINLOCK_SIZE`, and optional multigenerational LRU widths `LRU_GEN_WIDTH` and `__LRU_REFS_WIDTH`.

Control flow: the host-built program includes kernel headers with `__GENERATING_BOUNDS_H` and `COMPILE_OFFSETS`, emits constants as assembler-like output consumed by kbuild post-processing, then exits.

State and persistence: no runtime kernel state. Its generated constants persist in build artifacts and influence preprocessor-visible kernel configuration.

Dependencies and integration: depends on page flags, memory zone, spinlock type, `linux/kbuild.h`, `linux/log2.h`, SMP and LRU generation Kconfig symbols. It is part of early generated-header build plumbing.

Risks: incorrect constants can break low-level layout assumptions across the kernel. Conditional constants must stay aligned with headers that consume generated bounds. Host compilation must avoid depending on unavailable runtime kernel state.

Test signals: full kernel builds, generated header diffs, SMP/non-SMP builds, and `CONFIG_LRU_GEN` on/off builds catch most issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/bpf/Kconfig

Purpose: declares core BPF subsystem configuration symbols, including interpreter availability, architecture JIT capability flags, the `bpf()` syscall, JIT policy, unprivileged defaults, preload inclusion, and BPF LSM enablement.

Important APIs/types/functions: key symbols are `BPF`, `HAVE_CBPF_JIT`, `HAVE_EBPF_JIT`, `ARCH_WANT_DEFAULT_BPF_JIT`, `BPF_SYSCALL`, `BPF_JIT`, `BPF_JIT_ALWAYS_ON`, `BPF_JIT_DEFAULT_ON`, `BPF_UNPRIV_DEFAULT_OFF`, and `BPF_LSM`.

Control flow: Kconfig selects foundational dependencies when `BPF_SYSCALL` is enabled, gates JIT on architecture support, makes `BPF_JIT_ALWAYS_ON` remove interpreter fallback, defaults unprivileged BPF to disabled, sources preload Kconfig, and requires security/JIT/event support for BPF LSM.

State and persistence: persists as compile-time `.config` decisions and runtime sysctl defaults such as unprivileged BPF and JIT behavior.

Dependencies and integration: selects crypto SHA-256, IRQ work, Tasks RCU flavors, binary printf, networking support symbols when enabled, EXECMEM for JIT, and security/BPF events for LSM hooks.

Risks: changing defaults can affect kernel attack surface, performance, and compatibility. JIT-always-on changes interpreter availability and speculative execution posture. BPF LSM depends on BTF/JIT/prototype ordering elsewhere.

Test signals: allmodconfig/defconfig matrix builds, unprivileged BPF sysctl behavior, JIT sysctl tests, BPF LSM selftests, and preload builds are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/Makefile -->
# sources/distributed-fs/ceph-client/kernel/bpf/Makefile

Purpose: defines the BPF subsystem object composition and per-object compiler flags.

Important APIs/types/functions: always builds `core.o`; conditionally includes syscall/verifier/map/helper/iterator/BTF/JIT/network/perf/cgroup/LSM/preload objects based on Kconfig. It removes ftrace instrumentation from selected low-level allocator/list/ringbuf objects and disables GCC GCSE for `core.o` on x86 when the interpreter remains.

Control flow: object lists are appended for `CONFIG_BPF_SYSCALL`, `CONFIG_BPF_JIT`, `CONFIG_BPF_LSM`, networking, perf events, cgroups, inet, sysfs, crypto, DMA-buf, and MMU+64-bit arena support. LSM prototype object ordering deliberately precedes `bpf_lsm.o` for BTF dedup behavior.

State and persistence: affects build artifacts only, determining which BPF features are compiled into the kernel.

Dependencies and integration: integrates with top-level kbuild and the Kconfig symbols in this folder. It ties source files in this research subset into the build: `arena.o`, `arraymap.o`, `backtrack.o`, `bloom_filter.o`, `bpf_cgrp_storage.o`, `bpf_inode_storage.o`, `bpf_insn_array.o`, `bpf_iter.o`, and `bpf_local_storage.o`.

Risks: object ordering and conditional inclusion are behaviorally significant. Missing `CONFIG_MMU && CONFIG_64BIT` around arena would break unsupported architectures; incorrect LSM ordering can produce wrong BTF prototypes; accidental ftrace instrumentation in lock-sensitive BPF internals can recurse or perturb timing.

Test signals: build matrix across BPF syscall/JIT/LSM/net/perf/cgroup configs, pahole/BTF generation, and boot/runtime BPF selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/arena.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/arena.c

Purpose: implements `BPF_MAP_TYPE_ARENA`, a sparse shared virtual memory arena visible to userspace through mmap and to BPF programs through JIT-supported arena addressing and kfunc page allocation.

Important APIs/types/functions: `struct bpf_arena` embeds `struct bpf_map`, user and kernel VM ranges, a `range_tree`, locks, tracked VMAs, and deferred free queues. Map ops include `arena_map_alloc`, `arena_map_free`, `arena_map_mmap`, `arena_get_unmapped_area`, and `arena_map_direct_value_addr`. Page lifecycle is handled by `arena_alloc_pages`, `arena_free_pages`, `arena_reserve_pages`, `arena_free_worker`, and `arena_free_irq`. BPF kfuncs are `bpf_arena_alloc_pages`, `bpf_arena_free_pages`, and `bpf_arena_reserve_pages`, plus non-sleepable internal variants. `bpf_prog_report_arena_violation` reports JIT arena faults.

Control flow: map creation validates mmapable 64-bit/MMU/JIT support, address range, flags, and 32-bit user address window, reserves a guarded 4GB-ish kernel vmalloc area, initializes the free range tree, and pre-populates upper page tables except PTEs. mmap fixes a single shared userspace range and records VMAs. User faults either map an already allocated kernel page or allocate one unless `BPF_F_SEGV_ON_FAULT` requests SIGSEGV. BPF kfunc allocation clears range-tree availability, allocates pages in batches, maps them into kernel vmalloc PTEs, and returns the userspace address. Freeing clears kernel PTEs, flushes TLB/cache, zaps user VMAs, and frees pages; non-sleepable failures defer through irq_work/workqueue.

State and persistence: arena state lives for the BPF map lifetime. Allocated pages persist until explicitly freed or map destruction. `range_tree` records unallocated/reserved ranges; VMA list tracks active mmaps; `free_spans` persists deferred frees until workqueue drain. It does not support ordinary lookup/update/delete semantics.

Dependencies and integration: depends on BPF map memory accounting, JIT arena support hooks, BTF kfunc registration, vmalloc/page-table APIs, TLB/cache flushing, range-tree support, memcg charging, user VMA fault handling, irq_work, workqueues, and BPF stream diagnostics.

Risks: page table manipulation, TLB lifetime, and shared user/kernel mappings are high risk. Address calculations intentionally use lower 32 bits; validation must prevent crossing boundaries. Failed non-sleepable deferred-free allocation intentionally leaks until arena destruction. Incorrect VMA tracking can free a map with active mappings or leave stale user mappings. JITs must match the addressing contract.

Test signals: BPF arena selftests should cover mmap address selection, `BPF_F_SEGV_ON_FAULT`, kfunc allocation/free/reserve, non-sleepable paths, user faults after BPF allocation, map teardown with no VMAs, and arena violation reports. KASAN/KCSAN, memcg, and TLB stress are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/arena.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/arraymap.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/arraymap.c

Purpose: implements BPF array-family map types: plain arrays, per-CPU arrays, program arrays for tail calls, perf event arrays, cgroup fd arrays, and array-of-maps.

Important APIs/types/functions: allocation and common ops include `array_map_alloc_check`, `array_map_alloc`, `array_map_lookup_elem`, `array_map_update_elem`, `bpf_percpu_array_copy`, `bpf_percpu_array_update`, `bpf_array_get_next_key`, `array_map_mmap`, iterator seq ops, and `bpf_for_each_array_elem`. FD-backed variants use `bpf_fd_array_map_lookup_elem`, `bpf_fd_array_map_update_elem`, `__fd_array_map_delete_elem`, and type-specific get/put callbacks. Program arrays add `prog_array_map_poke_track`, `prog_array_map_poke_run`, deferred clear work, and `prog_array_map_ops`.

Control flow: creation validates key/value sizes and flags, rounds element size to 8 bytes, optionally expands backing storage for Spectre v1 masking, and either allocates contiguous map memory or per-cpu pointers. Lookup checks bounds and applies `index_mask`. Updates copy values or per-cpu values and free BTF-described fields. mmapable arrays remap vmalloc storage. Iterators pin a map uref and feed entries into BPF iterator programs. FD arrays exchange stored object pointers with `xchg` and release old pointers through map-specific callbacks; program arrays patch JIT tail-call sites under `poke_mutex`.

State and persistence: plain arrays preallocate all slots for map lifetime. Per-cpu arrays persist one allocation per entry per possible CPU. Program/perf/cgroup/array-of-map variants persist referenced kernel objects and release them on delete, map release, or map free. `BPF_F_PRESERVE_ELEMS` changes perf event array release behavior.

Dependencies and integration: uses BPF map core, BTF record cleanup, JIT direct lookup generation, RCU, perf events, cgroups, map-in-map metadata, BPF iterators, SHA-256 hashing for map hash, and architecture poke hooks for tail calls.

Risks: boundary and overflow checks protect preallocated memory. Speculation masking must stay aligned with generated lookup instructions. FD map object lifetime relies on RCU and put callbacks. Program array tail-call patching is subtle because tracked program aux data may be visible before final JIT stability. Per-cpu copy flags must not expose padding or cross invalid CPU IDs.

Test signals: BPF map selftests for array/percpu array, mmapable arrays, batch ops, BTF spin_lock values, map iterators, `bpf_for_each_map_elem`, tail calls and prog-array updates, perf event arrays, cgroup arrays, and array-of-maps should detect regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/arraymap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/backtrack.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/backtrack.c

Purpose: implements verifier backtracking for scalar precision, allowing BPF state pruning while preserving exact scalar ranges only where later instructions require them.

Important APIs/types/functions: `bpf_push_jmp_history` records branch/call/exit history and stack access flags; `bpf_mark_chain_precision` is the main exported precision propagation routine; `bpf_mark_all_scalars_precise` is the conservative fallback; `backtrack_insn` interprets instructions in reverse; mask helpers manage per-frame register and stack-slot dependency sets; `bpf_fmt_stack_mask` formats debug output.

Control flow: verifier records jump history as it explores states. When precision is required for a register, `bpf_mark_chain_precision` initializes a backtrack mask at the current frame and walks instructions backward through the current and parent verifier states. `backtrack_insn` propagates dependencies through ALU moves, loads from stack spills, stores to stack, conditional jumps, helper/kfunc calls, static/global subprogram calls, callbacks, exits, and ldimm instructions. Unsupported or ambiguous patterns fall back to marking all scalar registers and spilled scalars in parent states precise.

State and persistence: state is stored in `bpf_verifier_state` parent chains, `jmp_history`, register `precise` bits, and spilled stack slot metadata. Backtracking state is transient in `env->bt`.

Dependencies and integration: depends on verifier instruction flags, subprogram discovery, callback detection, register/stack metadata, verifier logging, BPF instruction encoding, and state equivalence/pruning logic.

Risks: under-marking precision can make unsafe state pruning possible; over-marking reduces verifier performance and program acceptance. Subprogram/callback frame transitions are subtle. Pointer arithmetic or stack access through unsupported patterns intentionally triggers conservative fallback. Jump history consistency bugs produce verifier errors.

Test signals: verifier selftests involving scalar precision, callbacks, subprograms, tail calls, atomic fetch/load, stack spills, bounded loops, and log-level replay are relevant. Unexpected `backtracking misuse`, `unexpected regs`, or fallback explosions indicate regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/backtrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bloom_filter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bloom_filter.c

Purpose: implements keyless BPF Bloom filter maps using push/peek operations and a power-of-two bitset.

Important APIs/types/functions: `struct bpf_bloom_filter` stores the embedded map, bitset mask, hash seed, hash count, and flexible bitset. `hash` uses `jhash`/`jhash2`. Map ops are `bloom_map_alloc_check`, `bloom_map_alloc`, `bloom_map_push_elem`, `bloom_map_peek_elem`, `bloom_map_free`, `bloom_map_check_btf`, and `bloom_map_mem_usage`.

Control flow: creation rejects keys, zero values, unsupported flags, and invalid `map_extra`; `map_extra` low four bits choose hash count, defaulting to five. It sizes the bitset from expected entries and hash count, approximating optimal Bloom filter sizing, rounds to a power of two, and optionally randomizes the seed. Push sets all hash bits for a value. Peek returns success only if all corresponding bits are set. Pop, delete, get-next-key, ordinary lookup, and ordinary update are unsupported.

State and persistence: bitset state persists for map lifetime and only grows more set bits; there is no deletion. Seed persists per map unless `BPF_F_ZERO_SEED` is requested.

Dependencies and integration: integrates with BPF map core, BTF map typing, `jhash`, random seed generation, bitmap bit operations, and BPF queue/stack-like push/peek map callbacks.

Risks: false positives are expected by design; false negatives indicate bugs. Large `max_entries` and hash-count calculations must avoid overflow. Concurrent `set_bit`/`test_bit` use is lockless, so tests should consider atomic bitops semantics. Keyless BTF validation must reject non-void keys.

Test signals: BPF map selftests for Bloom filter creation flags, zero seed determinism, push/peek behavior, expected false-positive envelope, unsupported operations, and BTF key validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bloom_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_cgrp_storage.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_cgrp_storage.c

Purpose: provides cgroup-owned BPF local storage maps and helper prototypes.

Important APIs/types/functions: `DEFINE_BPF_STORAGE_CACHE(cgroup_cache)` creates the storage cache. `cgroup_storage_ptr`, `bpf_cgrp_storage_free`, `cgroup_storage_lookup`, fd-based map ops, `bpf_cgrp_storage_get`, and `bpf_cgrp_storage_delete` wrap generic local storage for `struct cgroup`. `cgrp_storage_map_ops` wires the map into BPF core.

Control flow: userspace map lookup/update/delete takes a cgroup fd, obtains a cgroup reference, performs generic local-storage lookup/update/unlink, and drops the cgroup. BPF helpers operate on a `struct cgroup *` under BPF RCU, optionally create storage if the cgroup refcount is not dying, and return a map-value pointer or delete status.

State and persistence: storage attaches to `cgroup->bpf_cgrp_storage` and persists until explicit deletion, map free, or cgroup destruction through `bpf_cgrp_storage_free`.

Dependencies and integration: depends on cgroup fd lookup, generic `bpf_local_storage`, BTF id for cgroup helper argument validation, BPF RCU locking, and map memory accounting from the generic engine.

Risks: helper create must not attach to dying cgroups. fd operations must correctly refcount cgroups. Missing BPF RCU lock is warned. No key iteration is supported.

Test signals: cgroup local storage selftests should cover fd lookup/update/delete, helper get with and without create, deletion during cgroup teardown, and invalid fd/refcount-dying cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_cgrp_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_inode_storage.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_inode_storage.c

Purpose: provides inode-owned BPF local storage maps and LSM/helper accessors.

Important APIs/types/functions: `DEFINE_BPF_STORAGE_CACHE(inode_cache)`, `inode_storage_ptr`, `inode_storage_lookup`, `bpf_inode_storage_free`, fd-based lookup/update/delete ops, `bpf_inode_storage_get`, `bpf_inode_storage_delete`, and `inode_storage_map_ops`.

Control flow: fd-based syscalls use `CLASS(fd_raw, f)` to resolve a file and operate on `file_inode`. Updates reject inodes without a BPF storage blob. BPF helpers accept a `struct inode *`, require BPF RCU, optionally create storage using `BPF_LOCAL_STORAGE_GET_F_CREATE`, and return a map value pointer or deletion result. Inode teardown calls `bpf_inode_storage_free`, which destroys all local storage attached to the inode.

State and persistence: storage lives in the inode's `bpf_storage_blob` and persists with the inode until deletion, map free, or inode destruction.

Dependencies and integration: integrates with generic BPF local storage, inode BPF blobs, file descriptor handling, BPF LSM/BTF id validation, RCU read-side sections, and map BTF validation.

Risks: helper callers must guarantee the inode has a refcount and cannot be freed. Not all inodes have storage blobs, so update/create must check `inode_storage_ptr`. Lifetime bugs can become UAFs because storage is owner-attached.

Test signals: BPF LSM inode storage selftests, fd-based map operation tests, deletion on inode eviction, invalid fd handling, and inodes without storage blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_inode_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_insn_array.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_insn_array.c

Purpose: implements `BPF_MAP_TYPE_INSN_ARRAY`, a read-only-to-BPF jump-table-like map that stores original, translated, and JIT offsets for indirect instruction pointer access.

Important APIs/types/functions: `struct bpf_insn_array` stores an embedded map, single-use `used` flag, `ips` array, and flexible `values`. Map ops include allocation, lookup, update, direct value address, BTF checking, and memory usage. Runtime APIs are `bpf_insn_array_init`, `bpf_insn_array_ready`, `bpf_insn_array_release`, `bpf_insn_array_adjust`, `bpf_insn_array_adjust_after_remove`, and `bpf_prog_update_insn_ptrs`.

Control flow: map creation requires u32 keys, exact value size, no flags, and marks the map `BPF_F_RDONLY_PROG`. Userspace update may only set `orig_off`; `xlated_off` and `jitted_off` must be zero. Verifier initialization requires a frozen map, validates offsets against the program and 64-bit immediate pairs, atomically claims single-program use, and copies original offsets into translated offsets. Later instruction insert/remove adjustments rewrite translated offsets or mark deleted entries. JITs call `bpf_prog_update_insn_ptrs` with offset tables and image base to fill `jitted_off` and executable IPs.

State and persistence: map values persist for map lifetime; `used` serializes ownership by one program at a time; `ips` are populated only after JIT update and cleared only by overwrite/free.

Dependencies and integration: depends on BPF map core, program verifier freeze semantics, JIT offset reporting, direct value address support, and common array next-key helper.

Risks: stale or invalid offsets can jump into wrong instructions. The map must be frozen before program use and exclusive to one program. Offset adjustment must track verifier instruction rewrites exactly. JITs must call pointer update with correct subprogram-relative offsets.

Test signals: selftests for insn arrays should cover map creation validation, frozen-map requirement, invalid offsets into ldimm64 pairs, instruction insertion/removal adjustment, JIT pointer readiness, and single-use `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_insn_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_iter.c

Purpose: implements BPF iterator target registration, iterator link creation, iterator file operations, seq_file integration, and generic callback helpers such as `bpf_loop`.

Important APIs/types/functions: target and link types are `bpf_iter_target_info`, `bpf_iter_link`, and `bpf_iter_priv_data`. Public APIs include `bpf_iter_reg_target`, `bpf_iter_unreg_target`, `bpf_iter_prog_supported`, `bpf_iter_get_func_proto`, `bpf_iter_link_attach`, `bpf_iter_new_fd`, `bpf_iter_get_info`, and `bpf_iter_run_prog`. Helpers include `bpf_for_each_map_elem`, `bpf_loop`, and numeric iterator kfuncs `bpf_iter_num_new`, `bpf_iter_num_next`, `bpf_iter_num_destroy`.

Control flow: targets register static metadata under `targets_mutex`. Program verification checks attach function prefix and target name/BTF id, then initializes context arg info. Link attach validates user iterator info, finds target by cached BTF id, enforces sleepable/resched compatibility, primes a BPF link, and calls target attach hooks. Opening an iterator anon inode prepares a seq_file, pins the current program under `link_mutex`, initializes target-private seq state, and assigns a unique session id. Reads use custom `bpf_seq_read` to run seq start/show/next/stop with a fixed buffer, sequence numbering, overflow handling, optional rescheduling, and object-count cap.

State and persistence: registered targets persist until unregistered. Iterator links persist as BPF links and may be updated with compatible programs. Each open file has private session/sequence state and target-private data. Numeric iterators store current/end in BPF stack-visible iterator storage.

Dependencies and integration: depends on anon inodes, seq_file, BPF link core, BTF attach ids, BPF program run context, RCU trace/dont-migrate locking, map iterator seq info, and target-specific attach/detach/fdinfo callbacks.

Risks: iterator read loops must handle buggy `next` functions, overflow, skipped objects, and long scans without livelock. Link update must protect program lifetime. Sleepable programs are allowed only for resched-capable targets. User link info copying must preserve tail-zero validation.

Test signals: BPF iterator selftests for task/map/prog/link targets, link fdinfo/info, program replacement, sleepable iterator constraints, partial reads and overflow, `bpf_for_each_map_elem`, `bpf_loop`, and numeric iterator kfunc bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_local_storage.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_local_storage.c

Purpose: generic engine for BPF local storage maps, attaching map values to kernel owner objects such as sockets, cgroups, and inodes while also indexing those values by map for cleanup.

Important APIs/types/functions: allocation and ownership helpers include `bpf_selem_alloc`, `bpf_local_storage_alloc`, `bpf_local_storage_update`, `bpf_local_storage_lookup` (declared elsewhere), `bpf_selem_unlink`, `bpf_local_storage_destroy`, `bpf_local_storage_map_alloc_check`, `bpf_local_storage_map_check_btf`, `bpf_local_storage_map_alloc`, and `bpf_local_storage_map_free`. Internal helpers manage owner storage pointers, map buckets, local-storage caches, RCU freeing, memory charge/uncharge, and nofail unlink during destroy/free races.

Control flow: update validates flags and spin_lock usage, finds or creates owner storage through the map's `map_owner_storage_ptr`, allocates a storage element, links it first into the map bucket and then into owner storage under rqspinlocks, and unlinks any replaced element. Delete unlinks from map then owner storage and schedules RCU/Tasks-Trace freeing. Owner destruction walks storage elements and uses `bpf_selem_unlink_nofail` to tolerate races with map free. Map free prevents new users, synchronizes RCU, walks all buckets unlinking elements, waits for storage users and RCU callbacks, then frees buckets and map memory.

State and persistence: each owner has a `bpf_local_storage` list plus small cache slots; each element is linked both to owner storage and to a per-map bucket. Elements persist until deleted, owner destruction, or map free. Memory charge counters track owner-attached storage and element sizes.

Dependencies and integration: depends on BPF map core, owner-specific map ops for storage pointer and optional memory charge hooks, raw rescheduling spinlocks, RCU and RCU Tasks Trace, BTF record field cleanup, map value copy/swap helpers, and cache-index allocation shared by owner-specific storage caches.

Risks: this is concurrency-sensitive two-index lifetime code. Races between owner destruction, map free, update, and delete can leak or double free without the state bits and RCU barriers. rqspinlock timeout paths intentionally warn and may defer cleanup. Cache insertion must not publish deleted elements. BTF object fields must be freed exactly once.

Test signals: local-storage selftests for sockets/cgroups/inodes, concurrent update/delete/map free/owner free stress, BTF spin_lock values, clone flags, memory accounting, RCU torture/KCSAN, and leak detection around nofail unlink paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_local_storage.c -->
