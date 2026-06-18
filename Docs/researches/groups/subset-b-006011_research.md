# subset-b-006011 Research

Grouped source research for BPF LRU, LSM, struct_ops, and task-local storage sources in `sources/distributed-fs/ceph-client/kernel/bpf`. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.c

## Purpose
`bpf_lru_list.c` implements the allocator and eviction list machinery used by preallocated BPF LRU hash maps. It owns the movement of embedded `struct bpf_lru_node` objects between free, inactive, active, and per-CPU local lists, and delegates actual hash table removal to the map-specific `del_from_htab` callback.

## Important APIs, Types, and Functions
The external entry points are `bpf_lru_init()`, `bpf_lru_populate()`, `bpf_lru_pop_free()`, `bpf_lru_push_free()`, and `bpf_lru_destroy()`. The core internal operations are `__bpf_lru_node_move_to_free()`, `__bpf_lru_node_move_in()`, `__bpf_lru_node_move()`, `__bpf_lru_list_rotate_active()`, `__bpf_lru_list_rotate_inactive()`, and `__bpf_lru_list_shrink()`. Common-LRU mode uses per-CPU `struct bpf_lru_locallist` caches and a single global `struct bpf_lru_list`; per-CPU-LRU mode uses one `struct bpf_lru_list` per possible CPU. `LOCAL_FREE_TARGET`, `PERCPU_FREE_TARGET`, and `nr_scans` bound refill and scan work.

## Control Flow
Initialization allocates either per-CPU global lists or per-CPU local lists plus one shared LRU list, initializes all list heads and locks, records `hash_offset`, and stores the hash-table deletion callback. Population walks the preallocated element buffer, finds each embedded node by `node_offset`, clears its ref bit, and places it on the initial free list.

On allocation, `bpf_lru_pop_free()` dispatches by mode. Per-CPU mode locks the CPU's list, rotates active/inactive lists, shrinks inactive/free lists if needed, writes the requested hash into the element at `hash_offset`, and moves the node to inactive. Common mode first tries the local free list under the local lock, refills it from the shared LRU by flushing pending nodes, rotating, taking global free nodes, and shrinking if needed, then puts the chosen node on the local pending list. If no local/global node is available, it round-robin steals from local free or pending lists on possible CPUs and rehomes the node as current CPU pending.

On deletion or replacement, `bpf_lru_push_free()` dispatches by mode. Common mode converts local pending nodes directly to local free when their original CPU local list still owns them; otherwise it falls back to moving an LRU-list node to the shared free list. Per-CPU mode locks the node CPU's LRU list and moves the node to free.

## State and Persistence Behavior
All state is in memory and tied to the lifetime of the owning BPF map. Node state is encoded in `node->type`, `node->cpu`, `node->ref`, the list linkage, and the hash stored at `hash_offset` inside the containing element. Active and inactive counts track only the two counted LRU lists, not free/local lists. `next_inactive_rotation` persists scan position across allocations so inactive promotion is spread over time. There is no disk persistence.

## Dependencies and Integration Points
This file depends on Linux list, raw spinlock, per-CPU allocation, CPU mask iteration, and atomic `READ_ONCE`/`WRITE_ONCE` helpers. It integrates directly with `kernel/bpf/hashtab.c`, which embeds `struct bpf_lru_node` in preallocated hash elements, sets ref bits on lookup/update, supplies `htab_lru_map_delete_node()` as `del_from_htab`, and calls pop/push around map update/delete paths.

## Risks
Correctness depends on holding the right local or global raw spinlock for every list transition. Type mismatches are guarded with `WARN_ON_ONCE`, but a corrupted type can still leak capacity or break list accounting. The forced shrink path deliberately ignores the ref bit when no inactive unreferenced victim can be deleted, so hot entries can be evicted under pressure. Common-LRU stealing touches remote CPU local lists and relies on stable possible-CPU iteration and local lock coverage. The callback must safely remove the node from the hash table and may fail, in which case the LRU scan continues or allocation fails.

## Test Signals
Useful signals are BPF selftests for `BPF_MAP_TYPE_LRU_HASH` and `BPF_MAP_TYPE_LRU_PERCPU_HASH`, stress tests that churn updates/lookups/deletes across many CPUs, lockdep/KCSAN coverage around LRU list operations, map update tests where `del_from_htab` refuses candidates, and accounting checks that active/inactive/free/local counts reconcile after allocation failure and map teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.h

## Purpose
`bpf_lru_list.h` declares the private LRU data model used by BPF LRU hash maps. It defines list states, embedded node metadata, shared and per-CPU list containers, the delete callback contract, and the small public API implemented by `bpf_lru_list.c`.

## Important APIs, Types, and Functions
`enum bpf_lru_list_type` separates global list states (`ACTIVE`, `INACTIVE`, `FREE`) from local-only states (`LOCAL_FREE`, `LOCAL_PENDING`). `struct bpf_lru_node` is embedded in map elements and carries `list`, `cpu`, `type`, and `ref`. `struct bpf_lru_list` contains the three global lists, active/inactive counts, `next_inactive_rotation`, and a cacheline-aligned raw spinlock. `struct bpf_lru_locallist` contains local free/pending lists, a round-robin steal cursor, and a raw spinlock. `struct bpf_lru` is the owning controller and stores either a common-LRU layout or a per-CPU-LRU layout, plus `del_from_htab`, `hash_offset`, scan/free targets, and mode. `bpf_lru_node_set_ref()` is the inline hot-path reference marker used by hash-map lookup/update code.

## Control Flow
Callers initialize a `struct bpf_lru`, populate it with preallocated elements and their embedded-node offsets, mark references as entries are used, pop nodes for insertion, push nodes back on deletion or failed insertion, and finally destroy per-CPU allocations. The header intentionally exposes only the high-level pop/push/init/populate/destroy operations plus reference-bit setting; all list migration details stay in the C file.

## State and Persistence Behavior
The structures persist for the lifetime of the owning map. The `ref` byte is a second-chance hint rather than a refcount; it is set without locking by callers through `READ_ONCE`/`WRITE_ONCE` and cleared when nodes rotate or are reinserted. The `cpu` field records the local/per-CPU owner used for per-CPU free return and common-LRU pending ownership. No state is persistent across map destruction or reboot.

## Dependencies and Integration Points
The header depends on Linux cacheline alignment, intrusive lists, spinlock types, and BPF integer types from surrounding includes. Its primary consumer is BPF hashtable code, but the API is intentionally map-internal rather than UAPI. The `del_from_htab_func` callback is the handshake between generic LRU policy and map-specific hash bucket deletion.

## Risks
ABI-like coupling exists between the map element layout and `hash_offset`/`node_offset` values passed to the implementation. Incorrect offsets corrupt element memory. Because `type` is an 8-bit state machine shared with list membership, any unsynchronized direct mutation outside the implementation can make subsequent list operations unsafe. Ref-bit semantics are lossy by design, so tests should not interpret them as precise usage counts.

## Test Signals
Build coverage should catch missing type declarations across kernel configuration variants. Runtime signals include BPF LRU hash selftests, map element layout tests, ref-bit preservation tests under lookup/update churn, and teardown tests that verify `bpf_lru_destroy()` frees only the per-CPU container chosen by `bpf_lru_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm.c

## Purpose
`bpf_lsm.c` wires BPF programs into Linux Security Module hooks. It creates attachable weak BPF LSM hook symbols, builds BTF ID allow/deny sets for verifier checks, exposes LSM-specific helper prototypes, classifies hooks as sleepable/trusted/current-cgroup/socket-option-capable, and constrains verifier return ranges for LSM programs.

## Important APIs, Types, and Functions
The `LSM_HOOK` macro expansion over `<linux/lsm_hook_defs.h>` emits weak `bpf_lsm_<hook>()` functions returning each hook default value and builds the `bpf_lsm_hooks` BTF set. `bpf_lsm_verify_prog()` enforces GPL-compatible programs, rejects disabled hooks, and verifies that `attach_btf_id` is in the BPF LSM hook set. Under `CONFIG_CGROUP_BPF`, `bpf_lsm_find_cgroup_shim()` chooses the cgroup shim runner based on hook arguments and cgroup/current hook sets. Helper implementations and prototypes include `bpf_bprm_opts_set`, `bpf_ima_inode_hash`, `bpf_ima_file_hash`, and `bpf_get_attach_cookie`. `bpf_lsm_func_proto()` exposes those helpers plus inode/sk storage, spin locks, cgroup helpers, sockopt helpers for selected cgroup LSM hooks, and generic tracing helpers. `bpf_lsm_is_sleepable_hook()`, `bpf_lsm_is_trusted()`, and `bpf_lsm_get_retval_range()` are verifier-facing policy APIs.

## Control Flow
At build time, BTF ID macros assemble hook sets. During program verification, the verifier calls `bpf_lsm_verify_prog()` and `lsm_verifier_ops.get_func_proto`. Helper availability is determined by function id, expected attach type, attach BTF id, and optional kernel configuration. During runtime attach and execution, the trampoline/cgroup code uses the hook symbol and, for cgroup LSM, a selected shim to run programs against current, socket, or sock contexts.

## State and Persistence Behavior
This file does not persist dynamic state. The important state is static BTF ID sets and helper prototype tables compiled into the kernel. `bpf_bprm_opts_set()` mutates `linux_binprm->secureexec` for the current exec path; IMA helpers fill caller-provided buffers; `bpf_get_attach_cookie()` reads the active trace run context. These effects last only for their kernel operation context.

## Dependencies and Integration Points
The file depends on BTF/BTF ID infrastructure, BPF verifier and trampoline support, LSM hook definitions, IMA, cgroup BPF, socket storage, inode storage, tracing helper policy, and optional network/audit/key/security-path configuration. It integrates with `kernel/bpf/verifier.c` for attach checks, sleepable checks, trusted pointer decisions, and return-value ranges, and with LSM hook registration through the generated `bpf_lsm_*` symbols.

## Risks
Hook-set drift is the central risk: adding or changing an LSM hook without updating disabled, sleepable, cgroup-current, sockopt, trusted, or bool-return sets can expose unsafe helpers or reject valid programs. Sleepable classification must match hook execution context because IMA helpers may sleep. Sockopt helper exposure is intentionally limited to hooks where the socket is locked or early-init unlocked; misclassification can introduce locking bugs. Return range constraints must stay aligned with hook semantics, especially bool hooks and void hooks. Disabled hooks document ABI and verifier safety exclusions that should be revisited carefully.

## Test Signals
Relevant tests include BPF LSM selftests for attach success/failure, GPL license rejection, disabled hook rejection, sleepable helper availability, IMA hash helper use, cgroup LSM current/socket/sock dispatch, sockopt helper availability only on the named hooks, attach-cookie reads through trampoline-attached programs, and verifier return-range diagnostics for bool and errno-returning hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm_proto.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm_proto.c

## Purpose
`bpf_lsm_proto.c` supplies a strong prototype definition for the `mmap_file` BPF LSM hook. Its purpose is not custom runtime behavior, but precise BTF metadata: the `file__nullable` parameter name marks the `struct file *` argument as nullable for verifier argument checking.

## Important APIs, Types, and Functions
The only function is `int bpf_lsm_mmap_file(struct file *file__nullable, unsigned long reqprot, unsigned long prot, unsigned long flags)`. It returns `0`, matching the default allow result for this hook. The `__nullable` suffix is the important contract because BTF-aware verifier code recognizes the suffix and treats the pointer as `PTR_MAYBE_NULL`.

## Control Flow
The weak `bpf_lsm_mmap_file()` generated in `bpf_lsm.c` would otherwise define the hook. This file provides a strong definition with the same symbol name, overriding the weak one at link time. BPF LSM programs attached to `mmap_file` therefore see a context where the file pointer may be NULL and must check it before dereference.

## State and Persistence Behavior
There is no owned state and no persistence. The function has no side effects and always returns success; the lasting effect is compile-time/link-time BTF metadata used by verifier policy.

## Dependencies and Integration Points
The file includes `<linux/fs.h>` for `struct file` and `<linux/bpf_lsm.h>` for BPF LSM declarations. It integrates with the broader `bpf_lsm.c` hook table because the same symbol appears in BTF ID sets such as `bpf_lsm_hooks` and `sleepable_lsm_hooks`. It also relies on the verifier's suffix-based nullable-argument handling.

## Risks
The main risk is prototype drift from the real LSM hook signature. If `mmap_file` arguments change and this strong definition is not updated exactly, BTF attachment or trampoline setup can become incorrect. Renaming or dropping the `__nullable` suffix would silently weaken verifier null-safety requirements. Returning a different default would change security semantics for unattached/default paths.

## Test Signals
Useful tests attach a BPF LSM program to `mmap_file` and verify that dereferencing `file` without a NULL check is rejected while a checked dereference is accepted. Build and BTF validation should confirm that the strong symbol replaces the weak definition and retains the expected function prototype.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_struct_ops.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_struct_ops.c

## Purpose
`bpf_struct_ops.c` implements the kernel side of BPF struct operations: BPF maps whose single value describes a kernel operations struct and whose function-pointer members are backed by BPF programs through trampolines. It validates struct_ops BTF descriptors, converts userspace values into kernel registration objects, manages trampoline executable images and symbols, supports direct map registration or `BPF_F_LINK` link-based registration, and tracks program-to-struct_ops associations.

## Important APIs, Types, and Functions
`struct bpf_struct_ops_map` extends `struct bpf_map` with a struct_ops descriptor, update lock, BPF links, trampoline ksyms, executable image pages, owner BTF, userspace-facing `uvalue`, and kernel-facing `kvalue`. `struct bpf_struct_ops_link` wraps a `bpf_link`, RCU map pointer, and hangup waitqueue. Descriptor setup uses `bpf_struct_ops_desc_init()`, `is_valid_value_type()`, `prepare_arg_info()`, `bpf_struct_ops_supported()`, and `bpf_struct_ops_desc_release()`. Map operations include `bpf_struct_ops_map_alloc_check()`, `bpf_struct_ops_map_alloc()`, `bpf_struct_ops_map_update_elem()`, `bpf_struct_ops_map_delete_elem()`, `bpf_struct_ops_map_sys_lookup_elem()`, `bpf_struct_ops_map_seq_show_elem()`, and `bpf_struct_ops_map_free()`. Trampoline and symbol helpers include `bpf_struct_ops_prepare_trampoline()`, `bpf_struct_ops_image_free()`, and ksym add/delete/free helpers. Exported subsystem helpers are `bpf_struct_ops_get()`, `bpf_struct_ops_put()`, and `bpf_struct_ops_id()`. Link APIs include `bpf_struct_ops_link_create()`, link detach/update/poll/fdinfo methods, and `bpf_struct_ops_map_lops`. Program association APIs are `bpf_prog_assoc_struct_ops()`, `bpf_prog_disassoc_struct_ops()`, and `bpf_prog_get_assoc_struct_ops()`.

## Control Flow
Descriptor initialization finds the target operations struct and its `bpf_struct_ops_<name>` value wrapper in BTF, validates that the wrapper contains `bpf_struct_ops_common_value` followed by the target struct, rejects unsupported anonymous/bitfield/module cases, distills function-pointer prototypes into verifier models, and prepares nullable/refcounted argument metadata from CFI stub function parameter suffixes.

Map allocation accepts only one-entry maps with key size `u32`, valid value BTF, and flags limited to `BPF_F_LINK` and module-BTF selection. It resolves vmlinux or module BTF, pins module ownership when needed, finds the struct_ops descriptor, allocates the map, `uvalue`, link array, and ksym array, and initializes the map base.

`bpf_struct_ops_map_update_elem()` is the main materialization path. It rejects nonzero flags, nonzero key, nonzero padding holes, non-INIT map state, nonzero user state/refcnt, and invalid member payloads. For each member, it handles module-owner pointers, delegates subsystem-specific initialization to `st_ops->init_member`, requires unhandled non-function-pointer fields to be zero, converts function-pointer member values from program FDs to BPF programs, validates program type and attach identity, creates BPF trampoline links, associates programs with the map, allocates ksyms, prepares trampolines into bounded image pages, stores executable trampoline addresses in `kvalue`, and replaces userspace FDs in `uvalue` with program ids. After optional subsystem validation and architecture protection of image pages, it either sets state `READY` for link-based maps or calls `st_ops->reg()` and transitions to `INUSE`. Failure unwinds ksyms, images, associations, links, and values.

Deletion for non-link maps atomically transitions `INUSE` to `TOBEFREE`, unregisters the subsystem object, and drops the map reference acquired at registration. Link creation registers a `READY` map through `st_ops->reg(kdata, link)`, stores the map in the link under `update_mutex`, and lets detach/unregister be driven by link lifetime. Link update validates that the new map is `READY`, update support exists, and old/new descriptors match, then calls subsystem `update`, swaps the RCU map pointer, and adjusts references.

## State and Persistence Behavior
Persistent runtime state lives in the map object. `kvalue.common.state` moves through `INIT`, `READY`, `INUSE`, and `TOBEFREE`; release/acquire barriers make lookup observe initialized `uvalue` and state consistently. `uvalue` is the userspace report copy with program ids, while `kvalue` is the registered kernel operations struct with module owner pointers and trampoline addresses. Trampoline images are charged as JIT memory, made executable/protected, registered as BPF ksyms, and freed after both normal RCU and RCU-tasks grace periods. Link objects hold a live map reference until detach/dealloc and report `EPOLLHUP` after detach. There is no on-disk persistence.

## Dependencies and Integration Points
This file depends on BTF type metadata, BPF verifier models, architecture trampoline allocation/protection APIs, JIT memory accounting, BPF map and link core, RCU/RCU-tasks, module BTF ownership, kallsyms naming, and subsystem-provided `struct bpf_struct_ops` methods (`init`, `init_member`, `validate`, `reg`, `unreg`, and optional `update`). It integrates with syscall paths for map lookup/update/delete, map info fill, link creation, and program association; with verifier code for struct_ops attach checks and argument metadata; and with subsystems such as TCP congestion control that register concrete struct_ops providers.

## Risks
This file is sensitive to BTF layout drift, padding validation, function-pointer prototype mismatches, and CFI stub metadata errors. A missed unwind can leak BPF program references, map references, ksym registrations, or JIT memory. State transitions must prevent double registration/unregistration and races between map update, delete, link detach, and link update. Executable trampoline page limits (`MAX_TRAMP_IMAGE_PAGES`) and architecture trampoline sizes can reject large operation structs. Module BTF maps depend on module lifetime pinning. Program association uses `BPF_PTR_POISON` to preserve backward compatibility after conflicting associations, so callers must handle a poisoned/NULL association.

## Test Signals
Strong signals are BPF selftests for struct_ops map creation, one-entry key behavior, padding-hole rejection, wrong program fd/type/attach member rejection, module-BTF struct_ops, direct registration/delete, `BPF_F_LINK` registration/detach/poll/update, trampoline execution, ksym visibility, verifier handling of `__nullable` and `__ref` struct_ops arguments, and teardown under RCU with active callbacks. Fault-injection tests around allocation and `st_ops->reg()` failure are important because the unwind path is large.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_struct_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_task_storage.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/bpf_task_storage.c

## Purpose
`bpf_task_storage.c` implements `BPF_MAP_TYPE_TASK_STORAGE`, a BPF local-storage map type keyed by tasks. It supports helper-based access from BPF programs using `struct task_struct *` and syscall map operations using pidfds, while delegating most storage mechanics to the generic BPF local storage framework.

## Important APIs, Types, and Functions
`DEFINE_BPF_STORAGE_CACHE(task_cache)` defines the allocator cache used for task storage elements. `task_storage_ptr()` returns the `task->bpf_storage` owner pointer used by generic local storage. `task_storage_lookup()` wraps `bpf_local_storage_lookup()`. `bpf_task_storage_free()` destroys all BPF storage attached to a task during task teardown. Syscall map operations are `bpf_pid_task_storage_lookup_elem()`, `bpf_pid_task_storage_update_elem()`, and `bpf_pid_task_storage_delete_elem()`, all using an integer pidfd key. Helper implementations are `bpf_task_storage_get()` and `bpf_task_storage_delete()`. `task_storage_map_ops` wires allocation, free, BTF checking, memory accounting, owner storage pointer, and unsupported key iteration. `bpf_task_storage_get_proto` and `bpf_task_storage_delete_proto` define verifier-visible helper signatures.

## Control Flow
For syscall lookup/update/delete, the map key is read as a pidfd, `pidfd_get_pid()` converts it to a `struct pid`, and `pid_task()` resolves the live task under the expected RCU read-side critical section. Lookup returns the data pointer if storage exists. Update rejects `BPF_F_LOCK` when the map record has user pointers, then creates or updates task-local storage through `bpf_local_storage_update()`. Delete looks up storage without caching and unlinks the storage element. All pid references are dropped through `put_pid()`.

For helper access, BPF programs pass a map and `task_struct` pointer. `bpf_task_storage_get()` requires BPF RCU protection, rejects unsupported flags and NULL tasks, returns existing storage if present, and creates new storage only when the task usage refcount is nonzero and `BPF_LOCAL_STORAGE_GET_F_CREATE` is requested. `bpf_task_storage_delete()` rejects NULL tasks and unlinks the entry, relying on helper call sites to provide task lifetime safety.

## State and Persistence Behavior
Storage hangs off `task_struct::bpf_storage` and lives no longer than the task or map. `bpf_task_storage_free()` destroys the per-task local storage container when the task exits. Map values are runtime kernel memory; they are not persistent across task exit, map destruction, or reboot. Lookup may cache local-storage map hits through the generic framework when `cacheit_lockit` is true.

## Dependencies and Integration Points
The file depends on pidfd/PID lookup, task lifetime and RCU rules, generic BPF local storage, BTF IDs for `task_struct`, BPF helper prototype infrastructure, and map record metadata for lock/user-pointer checks. It integrates with helper dispatch in `kernel/bpf/helpers.c`, with task teardown code through `bpf_task_storage_free()`, and with syscall map operations through `task_storage_map_ops`.

## Risks
Task lifetime is the main risk. Pidfd map operations assume an RCU read-side critical section before calling `pid_task()`, and helper access requires BPF RCU protection or another task lifetime guarantee. Creating storage for a task with zero usage refcount is explicitly blocked to avoid attaching memory to a dying task. `BPF_F_LOCK` plus user-pointer fields is unsupported to prevent unsafe locked access. `get_next_key` is unsupported, so userspace must not expect enumeration.

## Test Signals
Useful tests include task storage helper get/delete from tracing/LSM programs, pidfd syscall lookup/update/delete against live and exited tasks, create-on-missing behavior with and without `BPF_LOCAL_STORAGE_GET_F_CREATE`, rejection of NULL task pointers and bad pidfds, `BPF_F_LOCK` rejection for maps containing user pointers, task exit cleanup, and no-key-iteration behavior returning `-ENOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/bpf_task_storage.c -->
