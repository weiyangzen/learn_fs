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
