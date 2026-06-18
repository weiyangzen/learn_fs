# subset-b-006343 Security LSM Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/syscalls.c -->
# sources/distributed-fs/ceph-client/security/landlock/syscalls.c

## Purpose

`syscalls.c` implements Landlock's userspace ABI: creating ruleset file descriptors, adding filesystem and network rules, querying ABI version/errata, and enforcing a ruleset on the calling task. It is the boundary between untrusted userspace buffers and Landlock's internal ruleset/domain machinery.

## Important APIs, Types, and Functions

- `SYSCALL_DEFINE3(landlock_create_ruleset)` validates `landlock_ruleset_attr`, handles `LANDLOCK_CREATE_RULESET_VERSION` and `LANDLOCK_CREATE_RULESET_ERRATA`, creates a one-layer `landlock_ruleset`, and exposes it through an anonymous fd.
- `SYSCALL_DEFINE4(landlock_add_rule)` dispatches `LANDLOCK_RULE_PATH_BENEATH` and `LANDLOCK_RULE_NET_PORT` to rule import helpers.
- `SYSCALL_DEFINE2(landlock_restrict_self)` merges a ruleset into current credentials and optionally synchronizes sibling threads through `landlock_restrict_sibling_threads()`.
- `copy_min_struct_from_user()` wraps `copy_struct_from_user()` with minimum-size, page-size, and null checks for forward-compatible ABI structs.
- `get_ruleset_from_fd()` verifies Landlock anonymous fd identity and read/write mode, then returns a referenced ruleset.
- `get_path_from_fd()`, `add_rule_path_beneath()`, and `add_rule_net_port()` import user-supplied rule attributes.
- `ruleset_fops` gives ruleset fds dummy read/write methods so fd modes can gate later add/enforce operations.

## Control Flow

Every syscall first rejects use when `landlock_initialized` is false, returning `-EOPNOTSUPP` and warning once. Ruleset creation either returns ABI metadata for special flags or copies and validates `landlock_ruleset_attr`, ensuring fs/net/scope masks contain no unknown bits before calling `landlock_create_ruleset()`. Successful rulesets are installed as anonymous `O_RDWR | O_CLOEXEC` fds; fd creation failure drops the ruleset reference.

Rule addition obtains the ruleset with `FMODE_CAN_WRITE`, checks flags, then copies the exact rule structure for the selected type. Path rules reject empty access masks, accesses outside the ruleset mask, Landlock ruleset fds, internal/no-user/private filesystems, and then call `landlock_append_fs_rule()`. Network rules reject empty masks, masks outside the handled network mask, and ports above `U16_MAX`, then call `landlock_append_net_rule()`.

Restricting self requires either `no_new_privs` or `CAP_SYS_ADMIN` in the current user namespace. It validates flags, prepares new credentials, adjusts audit logging options, optionally merges a ruleset with the current domain, replaces the prepared credential domain, marks the new layer as exec-active for audit, optionally runs thread synchronization, and finally commits credentials.

## State and Persistence Behavior

Ruleset fds hold referenced `struct landlock_ruleset` objects in `file->private_data`; release drops the reference. Enforced policy persists in `struct cred` through `landlock_cred_security->domain` and audit logging fields. Restriction is monotonic because merging creates a new domain layered over the old one, and `landlock_merge_ruleset()` enforces the maximum layer limit. `landlock_abi_version` is a stable userspace contract constant, currently `9`.

## Dependencies and Integration Points

The file depends on Landlock internals from `cred.h`, `domain.h`, `fs.h`, `net.h`, `ruleset.h`, `setup.h`, and `tsync.h`; kernel helpers for anonymous fds, credentials, capabilities, path refs, and user copy; and UAPI definitions from `uapi/linux/landlock.h`. It integrates with audit behavior under `CONFIG_AUDIT` and with cross-thread propagation through `tsync.c`.

## Risks and Edge Cases

User-copy size handling is ABI-critical: too-small structs are `-EINVAL`, very large sizes are `-E2BIG`, and future fields must zero-fill safely. The `ruleset_fd == -1` logging-only path is intentionally narrow and must not accept unrelated flags. Path fd filtering prevents impossible or internal objects from becoming path-beneath anchors. Thread synchronization may abort credential changes after preparation; callers must not assume local `prepare_creds()` implies final enforcement.

## Test Signals

Useful tests include ABI version/errata queries, unknown flag and unknown mask rejection, short/oversized struct copies, path rule addition against regular directories versus internal filesystems, network port validation, empty-rule `-ENOMSG`, fd mode checks, layer-limit `-E2BIG`, no-new-privs/capability gating, audit logging flag behavior, and `LANDLOCK_RESTRICT_SELF_TSYNC` with concurrent sibling threads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.c -->
# sources/distributed-fs/ceph-client/security/landlock/task.c

## Purpose

`task.c` registers Landlock LSM hooks for task-to-task and IPC interactions. It enforces domain ordering for ptrace, scoped access to abstract Unix sockets, and scoped signal delivery so Landlock policies can restrict cross-domain process interaction beyond filesystem and network port access.

## Important APIs, Types, and Functions

- `domain_scope_le()` checks whether a parent domain is an ancestor of, or equal to, a child domain.
- `domain_ptrace()` turns the domain ordering check into `0` or `-EPERM`.
- `hook_ptrace_access_check()` and `hook_ptrace_traceme()` enforce ptrace constraints and emit Landlock denial audit records.
- `domain_is_scoped()` compares client/server hierarchies and layer scope bits for abstract Unix socket and signal restrictions.
- `hook_unix_stream_connect()` and `hook_unix_may_send()` restrict cross-domain access to abstract Unix sockets.
- `hook_task_kill()` and `hook_file_send_sigiotask()` restrict direct signals and SIGIO/SIGURG-style file-owner signals.
- `landlock_add_task_hooks()` registers the hook table with `security_add_hooks()`.

## Control Flow

Ptrace enforcement is based on hierarchy ancestry. A non-Landlocked tracer is allowed. A Landlocked tracer can access only a target with a domain that is at least as restrictive as the tracer's domain. `ptrace_traceme` applies the same rule from the proposed parent tracer to the current task and logs the parent domain when denied.

Scoped IPC checks first locate an applicable subject and the layer that handles the relevant scope bit. Abstract Unix socket hooks ignore non-Landlocked tasks, non-abstract sockets, already-connected datagram peers, and sockets whose peer domain is not scoped relative to the requester. Denials log network audit data for the target socket.

Signal checks allow same-thread-group kernel credential-change signals when `cred` is null, then evaluate the subject domain against the target task's domain under RCU. File-owner signals use the saved Landlock subject in `landlock_file(fown->file)->fown_subject`, protected by the caller-held `fown->lock`, instead of recomputing from current credentials.

## State and Persistence Behavior

The file maintains no global mutable state. It reads domain hierarchies from credentials and saved file-owner Landlock state. Domain comparisons are stable through referenced credential and socket/file state, with task domains read under RCU. Scope semantics depend on each layer's `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` and `LANDLOCK_SCOPE_SIGNAL` bits.

## Dependencies and Integration Points

The hooks depend on Landlock credential/domain/ruleset helpers, `landlock_log_denial()`, Unix socket internals from `net/af_unix.h`, generic LSM task/socket hooks, and common audit structures. They integrate with Landlock ruleset creation through scope bits accepted in `landlock_create_ruleset()` and with file-owner state populated elsewhere in the Landlock file hooks.

## Risks and Edge Cases

Hierarchy walking in `domain_is_scoped()` is subtle because client and server may have different domain depths or no server domain. It must preserve the rule that a scoped client can interact only with domains in the allowed ancestry relationship. Abstract Unix sockets are singled out; pathname Unix sockets are left to filesystem policy. Signal exceptions for same thread group are necessary for POSIX credential changes and must not be widened.

## Test Signals

Tests should cover ptrace from unconstrained to constrained tasks, constrained to less-constrained tasks, sibling domains, and child domains; abstract stream connect and datagram send across same and different domains; pathname socket non-enforcement here; normal `kill`, `tgkill`, and SIGIO delivery; audit records for denied ptrace/socket/signal operations; and behavior when `PTRACE_MODE_NOAUDIT` is set.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.h -->
# sources/distributed-fs/ceph-client/security/landlock/task.h

## Purpose

`task.h` is the small internal declaration header for Landlock task-related hooks. It exposes only the initialization entry point needed by Landlock setup code.

## Important APIs, Types, and Functions

- `landlock_add_task_hooks()` is declared as an `__init` function. Its implementation in `task.c` registers Landlock ptrace, Unix socket, signal, and file-owner signal hooks.

## Control Flow

The header itself has no runtime control flow. During Landlock initialization, setup code includes this header and calls `landlock_add_task_hooks()`, which installs the task hook list into the LSM framework.

## State and Persistence Behavior

No state is defined here. Hook registration state is owned by the LSM core after `security_add_hooks()` runs in `task.c`.

## Dependencies and Integration Points

The header is guarded by `_SECURITY_LANDLOCK_TASK_H` and is consumed by Landlock initialization code. It intentionally avoids pulling in heavier task or socket headers.

## Risks and Edge Cases

The main risk is interface drift: if the hook registration implementation changes signature or init ordering, this declaration and callers must be updated together. Because it is an internal header, ABI stability is not a concern.

## Test Signals

Build coverage is the relevant signal. Runtime coverage comes indirectly from tests that confirm Landlock task hooks are present after initialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.c -->
# sources/distributed-fs/ceph-client/security/landlock/tsync.c

## Purpose

`tsync.c` implements Landlock's cross-thread synchronization path for `LANDLOCK_RESTRICT_SELF_TSYNC`. It updates sibling threads in the current thread group to the same tentative Landlock credentials with all-or-nothing semantics, using task work callbacks and completion barriers rather than directly modifying another task's credentials.

## Important APIs, Types, and Functions

- `landlock_restrict_sibling_threads()` is the exported internal entry point called by `landlock_restrict_self`.
- `struct tsync_shared_context` coordinates old/new credentials, no-new-privs propagation, preparation errors, and preparation/commit completion barriers.
- `struct tsync_work` carries per-task `task_work` state and a task reference.
- `restrict_one_thread()` prepares or reuses credentials in each sibling, waits for the global commit/abort decision, sets `no_new_privs` when needed, and commits or aborts.
- `tsync_works_grow_by()`, `tsync_works_provide()`, `tsync_works_trim()`, and `tsync_works_release()` manage a growable preallocated work array.
- `count_additional_threads()`, `schedule_task_work()`, and `cancel_tsync_works()` discover, schedule, and opportunistically cancel sibling task work.

## Control Flow

The initiating thread tries to take `current->signal->exec_update_lock` with `down_write_trylock()`. If another TSYNC or exec-style update owns it, the syscall is restarted so pending task work can run. The function then repeatedly counts sibling threads not yet scheduled, grows the work array, schedules a signaled `task_work` on each newly discovered non-exiting sibling, and waits until all scheduled siblings have reached the preparation barrier.

Each sibling callback either reuses the caller's prepared `new_cred` when it still has `old_cred`, or allocates fresh credentials and copies the Landlock credential blob. Any allocation failure records an atomic preparation error but still follows the barrier protocol. After all discovered threads are prepared and no further unscheduled siblings remain, the caller completes `ready_to_commit`; all callbacks either commit credentials or abort based on the shared error, then signal `all_finished`.

If the caller is interrupted while waiting for preparation, it stores `-ERESTARTNOINTR`, tries to cancel queued task work that has not run, and still releases all in-flight callbacks through the commit/abort barrier before returning.

## State and Persistence Behavior

All synchronization state is stack-local to `landlock_restrict_sibling_threads()` except referenced task and credential objects. The shared context uses atomics and completions for phase transitions. The persistent effect, on success, is that every participating sibling commits credentials containing the new Landlock domain and possibly `no_new_privs`. On failure, every prepared credential is aborted and the caller later aborts its own pending credentials in `sys_landlock_restrict_self()`.

## Dependencies and Integration Points

This file depends on the credential API, task iteration under RCU, `task_work_add()`/`task_work_cancel()`, completions, atomics, `exec_update_lock`, and Landlock credential-copy helpers. It is integrated only through `tsync.h` and the restrict-self syscall path.

## Risks and Edge Cases

Thread creation races are handled by looping until no new siblings are found, but this relies on scheduled siblings being unable to spawn new threads while blocked in task work. The preallocation logic must keep task references and work slots consistent across races with exiting tasks. Deadlock avoidance depends on restarting instead of blocking when `exec_update_lock` is already held. A failure in any sibling must abort all siblings, so barrier counters and cancellation paths are security-critical.

## Test Signals

Tests should create multithreaded processes that enforce Landlock with TSYNC while threads are creating more threads, exiting, blocking in syscalls, or racing another TSYNC call. Signals interrupting the caller should return restartable errors without partial enforcement. Observing all threads' Landlock status after success and no thread changed after injected allocation/task-work failure are the strongest signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.h -->
# sources/distributed-fs/ceph-client/security/landlock/tsync.h

## Purpose

`tsync.h` declares Landlock's internal thread-synchronization entry point used when userspace requests `LANDLOCK_RESTRICT_SELF_TSYNC`.

## Important APIs, Types, and Functions

- `landlock_restrict_sibling_threads(const struct cred *old_cred, const struct cred *new_cred)` synchronizes the prepared Landlock credential update to sibling threads and returns `0`, a restart code, or another negative errno.

## Control Flow

The header has no runtime flow. It connects `syscalls.c`, which owns the user-facing restrict-self operation, to `tsync.c`, which owns the task-work synchronization algorithm.

## State and Persistence Behavior

No state is declared here. The credential pointers passed through the function are managed by the caller and by the implementation's task-work protocol.

## Dependencies and Integration Points

It includes `<linux/cred.h>` for `struct cred`. Any Landlock file wanting TSYNC behavior should use this declaration rather than duplicating internals from `tsync.c`.

## Risks and Edge Cases

The function contract is narrow: callers must pass the current old credentials and an uncommitted prepared credential. Passing already-committed or unrelated credentials would break the implementation's optimization and safety assumptions.

## Test Signals

Build coverage plus `landlock_restrict_self(..., LANDLOCK_RESTRICT_SELF_TSYNC)` runtime tests validate this interface.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Kconfig -->
# sources/distributed-fs/ceph-client/security/loadpin/Kconfig

## Purpose

`loadpin/Kconfig` defines configuration options for the LoadPin LSM, which pins kernel-read files such as modules, firmware, kexec images, and policies to the first filesystem used for such loads.

## Important APIs, Types, and Functions

- `SECURITY_LOADPIN` enables the LSM and depends on `SECURITY` and `BLOCK`.
- `SECURITY_LOADPIN_ENFORCE` makes LoadPin enforcing at boot and depends on module compression being compatible with in-kernel decompression when modules are compressed.
- `SECURITY_LOADPIN_VERITY` allows trusted dm-verity-backed filesystems outside the pinned root and depends on built-in `DM_VERITY` and `SECURITYFS`.

## Control Flow

Kconfig selection controls whether `loadpin.o` is built, whether enforcement defaults to on, and whether the securityfs dm-verity digest interface is compiled. Runtime behavior is implemented in `loadpin.c`.

## State and Persistence Behavior

The configuration determines default boot state. `SECURITY_LOADPIN_ENFORCE` seeds the `enforce` module parameter; `SECURITY_LOADPIN_VERITY` adds persistent in-kernel trusted root digest state populated once at runtime.

## Dependencies and Integration Points

The options integrate with the LSM framework, block-device read-only checks, module loading, firmware loading, kernel file-reading hooks, dm-verity, and securityfs.

## Risks and Edge Cases

Enabling enforcement on systems with initrds, writable roots, or module compression not decompressed in-kernel can block legitimate loads. Verity support expands the trust model and depends on a carefully supplied digest list.

## Test Signals

Build matrix tests should cover LoadPin disabled, permissive, enforcing, and dm-verity-enabled configurations. Boot tests should verify enforcement defaults and kernel parameter override behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Makefile -->
# sources/distributed-fs/ceph-client/security/loadpin/Makefile

## Purpose

The LoadPin Makefile connects `CONFIG_SECURITY_LOADPIN` to the `loadpin.o` object.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SECURITY_LOADPIN) += loadpin.o` includes the LoadPin implementation in the build when the Kconfig option is enabled.

## Control Flow

There is no runtime control flow. Kbuild evaluates the object list based on configuration.

## State and Persistence Behavior

No state is defined here. Runtime state such as pinned superblock and enforcement mode lives in `loadpin.c`.

## Dependencies and Integration Points

This file integrates the LoadPin source with the kernel security Makefile hierarchy.

## Risks and Edge Cases

The risk is build omission or stale object naming if `loadpin.c` is renamed or split. Verity support is conditional inside `loadpin.c`, so no extra object is listed here.

## Test Signals

`CONFIG_SECURITY_LOADPIN=y` should produce `security/loadpin/loadpin.o`; disabled builds should omit it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/loadpin.c -->
# sources/distributed-fs/ceph-client/security/loadpin/loadpin.c

## Purpose

`loadpin.c` implements the LoadPin LSM. It records the superblock of the first file loaded through kernel file-reading paths and then allows future kernel loads only from that superblock or, when configured, from dm-verity devices whose root digests are trusted.

## Important APIs, Types, and Functions

- `loadpin_check()` is the core policy function for `kernel_read_file` and `kernel_load_data`.
- `loadpin_read_file()` and `loadpin_load_data()` are LSM hook adapters.
- `loadpin_sb_free_security()` reacts when the pinned superblock is unmounted.
- `parse_exclude()` processes boot/module parameter read-file type exclusions.
- `proc_handler_loadpin()` controls `/proc/sys/kernel/loadpin/enforce` writes when sysctl support is enabled.
- Under `CONFIG_SECURITY_LOADPIN_VERITY`, `read_trusted_verity_root_digests()`, `dm_verity_ioctl()`, and `init_loadpin_securityfs()` implement a one-shot securityfs ioctl interface for trusted verity root digests.
- `DEFINE_LSM(loadpin)` registers the LSM, hooks, and optional fs initcall.

## Control Flow

Initialization logs enforcing state, parses excluded read-file IDs, optionally registers the `kernel/loadpin/enforce` sysctl, and registers LSM hooks. On each kernel-read operation, LoadPin ignores configured IDs, rejects old fileless APIs in enforcing mode, and otherwise uses the file's mount superblock as the load root. The first accepted file pins `pinned_root` under a spinlock, records whether the device is writable, and logs the pin.

After pinning, a load is allowed only if its superblock matches `pinned_root` or, with verity support, `dm_verity_loadpin_is_bdev_trusted()` accepts the source block device. Mismatches are logged and either denied with `-EPERM` or ignored in permissive mode. If the pinned filesystem is unmounted, enforcing mode stores `ERR_PTR(-EIO)` to deny future loads; permissive mode clears the pin so it can be reestablished.

The verity ioctl reads a supplied fd through `kernel_read_file(..., READING_POLICY)`, requires a fixed header, parses newline-separated hex digests into `dm_verity_loadpin_trusted_root_digests`, rejects malformed input, clears partial state on failure, and permanently denies retry after corrupt input.

## State and Persistence Behavior

Key state includes `enforce`, exclusion arrays, `pinned_root`, `loadpin_root_writable`, and optional `deny_reading_verity_digests`. The pinned root persists until unmount. Trusted verity digests can be loaded only once and persist in the global dm-verity LoadPin list. The sysctl allows changing enforcement only while the pinned root was writable; read-only pinning prevents later userspace relaxation.

## Dependencies and Integration Points

LoadPin depends on LSM hooks for `sb_free_security`, `kernel_read_file`, and `kernel_load_data`; block-device read-only checks; kernel read-file ID names; module parameters; sysctl; securityfs; and dm-verity LoadPin helpers. It integrates with all kernel subsystems that use the kernel file-reading API, including module, firmware, kexec, and policy loading.

## Risks and Edge Cases

The first load defines trust for the rest of the boot, so early unexpected loads can pin the wrong filesystem. Old fileless module APIs are impossible to attribute and are denied only when enforcing. Unmounting the pinned root in enforcing mode intentionally bricks later loads. Exclusions weaken coverage and must match kernel read-file names exactly. Verity digest parsing is intentionally one-shot because accepting retries after malformed input could allow policy confusion.

## Test Signals

Tests should cover first-load pinning, allowed same-superblock loads, denied different-superblock loads, permissive logging, excluded IDs, null-file load-data behavior, unmount handling, sysctl changes before and after read-only pinning, boot parameter enforcement, and verity digest loading with valid header, malformed hex, duplicate attempts, and trusted/untrusted dm-verity devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/loadpin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Kconfig -->
# sources/distributed-fs/ceph-client/security/lockdown/Kconfig

## Purpose

`lockdown/Kconfig` defines the kernel Lockdown LSM options, including whether lockdown support is built, whether it initializes early, and the default lockdown level.

## Important APIs, Types, and Functions

- `SECURITY_LOCKDOWN_LSM` builds the lockdown LSM and selects module signature support when modules are enabled.
- `SECURITY_LOCKDOWN_LSM_EARLY` places lockdown in the early LSM init path so early boot parameters can be restricted.
- `LOCK_DOWN_KERNEL_FORCE_NONE`, `LOCK_DOWN_KERNEL_FORCE_INTEGRITY`, and `LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY` choose the default lockdown mode.

## Control Flow

Kconfig determines whether `lockdown.o` is built, whether it uses `DEFINE_EARLY_LSM` or `DEFINE_LSM`, and which forced mode the init function applies before registering hooks.

## State and Persistence Behavior

The selected default mode seeds the runtime `kernel_locked_down` level in `lockdown.c`. Runtime lockdown is monotonic; it can be raised but not lowered.

## Dependencies and Integration Points

The options depend on the generic security framework and integrate with module signature requirements, early LSM ordering, command-line parsing, and the securityfs lockdown control.

## Risks and Edge Cases

Late initialization may miss checks needed during early boot. Forced integrity or confidentiality can block debugging, kexec, kernel memory access, or other administrative workflows depending on hooks elsewhere in the kernel.

## Test Signals

Build and boot tests should verify each default mode, early versus normal LSM registration, command-line `lockdown=` handling, and visibility through `/sys/kernel/security/lockdown`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Makefile -->
# sources/distributed-fs/ceph-client/security/lockdown/Makefile

## Purpose

The lockdown Makefile adds the lockdown implementation object when lockdown LSM support is enabled.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SECURITY_LOCKDOWN_LSM) += lockdown.o` connects Kconfig to Kbuild.

## Control Flow

There is no runtime flow. The build system includes or excludes `lockdown.c` based on `CONFIG_SECURITY_LOCKDOWN_LSM`.

## State and Persistence Behavior

No state is defined here. Runtime lockdown level and hooks are in `lockdown.c`.

## Dependencies and Integration Points

This file integrates with the kernel security directory build.

## Risks and Edge Cases

The primary risk is build drift if the implementation file changes name or is split into multiple objects.

## Test Signals

`CONFIG_SECURITY_LOCKDOWN_LSM=y` should build `security/lockdown/lockdown.o`; disabled builds should not.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/lockdown.c -->
# sources/distributed-fs/ceph-client/security/lockdown/lockdown.c

## Purpose

`lockdown.c` implements the Lockdown LSM policy state and control interface. It exposes a `locked_down` hook that denies operations at or below the active lockdown level and a securityfs file for querying or raising the level.

## Important APIs, Types, and Functions

- `kernel_locked_down` stores the current `enum lockdown_reason` threshold.
- `lock_kernel_down()` raises the lockdown level and logs the source.
- `lockdown_param()` parses early `lockdown=integrity` or `lockdown=confidentiality`.
- `lockdown_is_locked_down()` is the LSM hook used by other kernel code through `security_locked_down()`.
- `lockdown_read()` and `lockdown_write()` implement `/sys/kernel/security/lockdown`.
- `lockdown_lsm_init()` applies forced Kconfig defaults and registers the hook.
- `lockdown_secfs_init()` creates the securityfs file.

## Control Flow

Early parameter parsing can raise the level before normal initialization. During LSM init, forced Kconfig modes may raise it again and the `locked_down` hook is registered. Every later lockdown check passes a reason; invalid reasons at or above `LOCKDOWN_CONFIDENTIALITY_MAX` warn and fail closed. If the current level is at least the requested reason, a rate-limited notice names the current command and reason, then returns `-EPERM`.

The securityfs read path prints available levels with the current one in brackets. The write path copies a userspace string, strips a trailing newline, compares it to known level labels, and calls `lock_kernel_down("securityfs", level)`. Attempts to set the current or lower level fail because lockdown is monotonic.

## State and Persistence Behavior

`kernel_locked_down` is global runtime state. It only increases from `LOCKDOWN_NONE` toward integrity or confidentiality maximums and has no lowering path. Securityfs provides persistence only for the running kernel; boot defaults and command-line parameters decide initial state on reboot.

## Dependencies and Integration Points

The file depends on the LSM hook framework, `lockdown_reasons[]`, early parameter infrastructure, securityfs, and UAPI LSM IDs. It is used indirectly by kernel subsystems that call `security_locked_down()` for module loading, kernel memory access, debug interfaces, and confidentiality-sensitive reads.

## Risks and Edge Cases

Reason ordering is security-critical: the numeric lockdown reasons must align with integrity and confidentiality thresholds. `lock_kernel_down()` returns `-EPERM` for already-equal or lower requests, so userspace writes are intentionally not idempotent. If securityfs creation fails, the hook still enforces but runtime visibility/control is reduced.

## Test Signals

Tests should cover boot `lockdown=` parsing, forced Kconfig modes, reading active securityfs state, raising from none to integrity and confidentiality, refusal to lower or repeat levels, invalid strings, invalid hook reasons, and representative `security_locked_down()` callers returning `-EPERM` with rate-limited notices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/lockdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm.h -->
# sources/distributed-fs/ceph-client/security/lsm.h

## Purpose

`lsm.h` is the private header for the generic Linux Security Module framework implementation. It centralizes debug helpers, global LSM ordering state, blob-size/cache declarations, allocator prototypes, and securityfs initialization glue.

## Important APIs, Types, and Functions

- `lsm_debug`, `lsm_pr()`, `lsm_pr_cont()`, and `lsm_pr_dbg()` support optional initialization logging.
- `lsm_active_cnt` and `lsm_idlist[]` describe enabled LSMs.
- `blob_sizes`, `lsm_file_cache`, `lsm_backing_file_cache`, and `lsm_inode_cache` expose blob layout and caches.
- `lsm_cred_alloc()` and `lsm_task_alloc()` allocate LSM security blobs for credentials and tasks.
- `securityfs_init()` is declared or stubbed depending on `CONFIG_SECURITYFS`.

## Control Flow

The header defines macros and declarations only. `lsm_init.c` consumes these declarations during early and normal LSM initialization, blob cache setup, and initcall sequencing.

## State and Persistence Behavior

All state is external. Blob sizes persist after initialization and define offsets for each enabled LSM's per-object storage. The active LSM list persists as the runtime source for syscalls such as `lsm_list_modules()`.

## Dependencies and Integration Points

It depends on `<linux/lsm_hooks.h>` and `<linux/lsm_count.h>`. It is shared by LSM initialization, syscalls, blob allocators, and securityfs setup code in the security subsystem.

## Risks and Edge Cases

The declarations must stay synchronized with actual globals and allocator implementations. Blob cache globals are used only when sizes are nonzero; consumers must tolerate absent caches for object classes no enabled LSM uses.

## Test Signals

Build coverage across securityfs-enabled and disabled configs, plus boot `lsm.debug` output and `lsm_list_modules()` results, validate the interface.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_audit.c -->
# sources/distributed-fs/ceph-client/security/lsm_audit.c

## Purpose

`lsm_audit.c` provides common audit helpers used by LSMs to format network, path, task, capability, key, lockdown, and other security-relevant data into audit records.

## Important APIs, Types, and Functions

- `ipv4_skb_to_auditdata()` fills `common_audit_data` from IPv4 skb headers and optional layer-4 ports.
- `ipv6_skb_to_auditdata()` does the same for IPv6, including extension-header skipping, when IPv6 is enabled.
- `audit_log_lsm_data()` serializes a `common_audit_data` union based on its `type`.
- `dump_common_audit_data()` adds current process pid/comm and common LSM data.
- `common_lsm_audit()` opens an `AUDIT_AVC` buffer, runs optional LSM-specific pre/post callbacks, dumps common data, and closes the record.

## Control Flow

Packet helpers copy addresses first, optionally report protocol, and avoid parsing non-initial IPv4 fragments. For TCP, UDP, and SCTP they extract source/destination ports; unknown protocols return `-EINVAL` after address population. IPv6 uses `skb_header_pointer()` for safe transport header reads after extension-header traversal.

Audit formatting switches on `a->type`. Path, file, ioctl, dentry, and inode cases emit pathname plus device/inode details. Task cases emit target pid and command. Network cases prefer socket-local details when an sk is present, including AF_UNIX pathname or abstract name hex, then also format address-family fields and netif names from `init_net`. Optional sections cover keys, InfiniBand, lockdown, anonymous inode class, and netlink message type.

`common_lsm_audit()` uses `GFP_ATOMIC | __GFP_NOWARN`, so audit can be attempted from restricted contexts without sleeping; if no buffer is available, it silently drops the record.

## State and Persistence Behavior

The file has no persistent mutable state. It reads current task data, skb headers, inode/dentry state, socket state, and optional audit context at the time of logging.

## Dependencies and Integration Points

It depends on audit core APIs, networking headers, AF_UNIX internals, IPv4/IPv6 helpers, LSM audit data types, lockdown reason strings, and optional key support. LSMs call `common_lsm_audit()` or `audit_log_lsm_data()` to avoid duplicating formatting logic.

## Risks and Edge Cases

Audit formatting touches many object types and must avoid sleeping or dereferencing unstable pointers. IPv6 extension parsing may fail and intentionally returns partial data. AF_UNIX abstract names can contain null bytes and are logged as hex when needed. The `BUILD_BUG_ON` guards `common_audit_data` union size to prevent stack bloat.

## Test Signals

Audit tests should cover path/file/dentry/inode/task records, IPv4/IPv6 TCP/UDP/SCTP and fragmented packets, AF_UNIX pathname and abstract sockets, key and lockdown data, netif lookup, no-audit-buffer behavior, and LSM-specific pre/post callbacks producing a well-formed `AUDIT_AVC` record.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_init.c -->
# sources/distributed-fs/ceph-client/security/lsm_init.c

## Purpose

`lsm_init.c` implements the generic LSM framework initialization pipeline: parsing boot ordering, enabling/disabling modules, assigning per-object blob offsets, registering static-call hook slots, initializing early and normal LSMs, creating blob caches, running staged initcalls, and notifying when all LSMs have started.

## Important APIs, Types, and Functions

- `lsm_choose_security()`, `lsm_choose_lsm()`, and `lsm_debug_enable()` parse `security=`, `lsm=`, and `lsm.debug`.
- `lsm_order_append()` and `lsm_order_parse()` build the enabled LSM order from built-in config, command line, legacy major selection, and first/last ordering classes.
- `lsm_prepare()` assigns blob offsets by accumulating `struct lsm_blob_sizes`.
- `lsm_init_single()` calls each enabled LSM's `init`.
- `lsm_static_call_init()` assigns a hook to an available static-call slot.
- `security_add_hooks()` records hook ownership and enables the static call branch for each hook.
- `early_security_init()` initializes early LSMs before normal security init.
- `security_init()` performs normal ordering, blob cache creation, initial cred/task blob allocation, and LSM init.
- `security_initcall_*()` run per-LSM staged initcall hooks from pure through late.

## Control Flow

Early LSMs are discovered from linker sections, force-enabled, appended to order, prepared, and initialized before normal command-line parsing. Normal initialization logs debug details when requested, chooses command-line `lsm=` over legacy `security=`, parses the selected list, appends `LSM_ORDER_FIRST` modules, then mutable listed modules, then a legacy major if specified, and finally `LSM_ORDER_LAST` modules. Nonselected modules are disabled.

For each enabled LSM, blob requests are aligned and converted into offsets while global blob sizes grow. Caches are created for file, backing-file, and inode blobs when needed. The current task's initial credentials and task blobs are allocated before non-early LSM init functions run. Hook registration does not append linked lists here; it installs static-call targets and activates branch keys, panicking if a hook exhausts the fixed per-hook LSM slot count.

After main initialization, separate kernel initcall levels invoke optional LSM initcall callbacks in the enabled order. The core level also initializes securityfs. The late level broadcasts `LSM_STARTED_ALL`.

## State and Persistence Behavior

Persistent state includes `lsm_active_cnt`, `lsm_idlist[]`, enabled flags in `struct lsm_info`, `lsm_order[]`, exclusive LSM selection, global blob sizes, and blob caches. Boot parameters are `__initdata` and discarded after init. Blob offsets assigned during init become stable contracts for all object allocations.

## Dependencies and Integration Points

The file depends on linker-provided LSM info sections, static call infrastructure, slab caches, the LSM blob allocator implementations, securityfs, and the LSM notifier chain. It is the central integration point for all built-in LSMs that use `DEFINE_LSM` or `DEFINE_EARLY_LSM`.

## Risks and Edge Cases

Ordering bugs can silently change security semantics when multiple LSMs stack. Exclusive LSM conflict handling must disable later incompatible modules. `security=` legacy behavior intentionally disables other legacy majors and is overridden by `lsm=`. Static-call slot exhaustion panics during boot. Blob offset alignment must be stable because every object allocation uses those offsets.

## Test Signals

Boot tests should cover default `CONFIG_LSM`, `lsm=` ordering, `security=` legacy selection, duplicate names, disabled modules, exclusive conflicts, first/last ordering, `lsm.debug` output, max LSM count handling, blob size/offset sanity, hook slot exhaustion under debug configs, staged initcall ordering, and `LSM_STARTED_ALL` notifier delivery.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_notifier.c -->
# sources/distributed-fs/ceph-client/security/lsm_notifier.c

## Purpose

`lsm_notifier.c` implements a blocking notifier chain for LSM lifecycle events. It lets kernel code register for events such as all enabled LSMs completing startup.

## Important APIs, Types, and Functions

- `blocking_lsm_notifier_chain` is the global blocking notifier head.
- `call_blocking_lsm_notifier()` dispatches an `enum lsm_event` and data pointer to registered listeners.
- `register_blocking_lsm_notifier()` registers a listener.
- `unregister_blocking_lsm_notifier()` unregisters a listener.

## Control Flow

Callers register a `struct notifier_block`. Event producers call `call_blocking_lsm_notifier()`, which invokes `blocking_notifier_call_chain()`. `lsm_init.c` calls this at late init with `LSM_STARTED_ALL`.

## State and Persistence Behavior

The notifier chain stores registered callbacks for the lifetime of their registration. Because it is a blocking chain, callbacks may sleep but event producers must call it from contexts that permit sleeping.

## Dependencies and Integration Points

The file depends on the kernel notifier API and `<linux/security.h>` for event definitions. It exports all three functions for use outside the core security directory.

## Risks and Edge Cases

Listeners must unregister before their storage disappears. Slow callbacks can delay event delivery. Event data is untyped `void *`, so producers and consumers must agree on semantics for each `enum lsm_event`.

## Test Signals

Tests can register a temporary notifier, trigger or simulate `LSM_STARTED_ALL`, verify call order and return propagation, and validate unregister prevents later invocation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_notifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_syscalls.c -->
# sources/distributed-fs/ceph-client/security/lsm_syscalls.c

## Purpose

`lsm_syscalls.c` implements userspace syscalls for the Linux Security Module API: setting and getting current task security attributes and listing active LSM module IDs.

## Important APIs, Types, and Functions

- `lsm_name_to_attr()` maps textual attribute names to `LSM_ATTR_*` identifiers.
- `SYSCALL_DEFINE4(lsm_set_self_attr)` delegates setting an attribute to `security_setselfattr()`.
- `SYSCALL_DEFINE4(lsm_get_self_attr)` delegates querying attributes to `security_getselfattr()`.
- `SYSCALL_DEFINE3(lsm_list_modules)` copies the active LSM id list to userspace.

## Control Flow

Attribute set/get syscalls are thin wrappers; validation and module-specific behavior are owned by the security core and active LSMs. `lsm_list_modules()` rejects nonzero flags, reads the userspace buffer size, stores the required total byte size back through `size`, returns `-E2BIG` if the supplied buffer is too small, then writes each active LSM numeric id from `lsm_idlist[]` and returns the count.

## State and Persistence Behavior

The file does not mutate LSM framework state except through delegated set-self calls. It reads `lsm_active_cnt` and `lsm_idlist[]`, which are fixed after security initialization.

## Dependencies and Integration Points

It depends on syscall infrastructure, `security_setselfattr()`, `security_getselfattr()`, LSM UAPI structs and flags, and private `lsm.h` globals. It is the userspace ABI bridge for tools that need to inspect or set stacked LSM contexts.

## Risks and Edge Cases

The list syscall writes the required size before checking capacity, so userspace can use a probe-and-retry pattern. A null or invalid `size` pointer fails with `-EFAULT`. Attribute name mapping must stay synchronized with UAPI names exposed elsewhere. The syscall wrappers rely on lower layers for per-LSM authorization and context validation.

## Test Signals

Tests should cover all known name mappings, unknown names returning `LSM_ATTR_UNDEF`, list probe with zero-sized buffer returning `-E2BIG` and required size, successful list matching boot LSM order, invalid flags, bad user pointers, and set/get behavior for each active LSM that supports a given attribute.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/min_addr.c -->
# sources/distributed-fs/ceph-client/security/min_addr.c

## Purpose

`min_addr.c` owns the global low-address mmap protection floor exposed through `vm.mmap_min_addr`. It combines a DAC-controlled sysctl value with the configured LSM minimum to decide the effective `mmap_min_addr`.

## Important APIs, Types, and Functions

- `mmap_min_addr` is the effective low virtual-address floor used by mmap checks.
- `dac_mmap_min_addr` stores the sysctl-controlled DAC value, initialized from `CONFIG_DEFAULT_MMAP_MIN_ADDR`.
- `update_mmap_min_addr()` sets `mmap_min_addr` to `max(dac_mmap_min_addr, CONFIG_LSM_MMAP_MIN_ADDR)` when an LSM floor exists, otherwise to the DAC value.
- `mmap_min_addr_handler()` enforces `CAP_SYS_RAWIO` for writes, delegates parsing to `proc_doulongvec_minmax()`, and refreshes the effective floor.
- `mmap_min_addr_init()` registers the sysctl and initializes the effective value.

## Control Flow

At pure initcall time, the file registers `/proc/sys/vm/mmap_min_addr` and computes the initial effective floor. Sysctl reads and writes go through `mmap_min_addr_handler()`. Writes without `CAP_SYS_RAWIO` fail before parsing; reads and authorized writes use the generic unsigned-long vector handler. After the generic handler returns, the effective value is recomputed.

## State and Persistence Behavior

`dac_mmap_min_addr` is mutable at runtime via sysctl, but `mmap_min_addr` never drops below `CONFIG_LSM_MMAP_MIN_ADDR` when that option is set. Changes persist only until reboot unless userspace reapplies sysctl settings.

## Dependencies and Integration Points

The file depends on initcall, mm, security, sysctl, capability, and min/max helpers. The effective global is consumed by memory-management security checks that reject low-address mappings or round non-fixed hints.

## Risks and Edge Cases

Calling `update_mmap_min_addr()` even after a failed generic parse preserves consistency but may recompute from the previous value. Systems expecting to lower the floor below the LSM default cannot do so. Capability checks use `CAP_SYS_RAWIO`, reflecting the security sensitivity of mapping low addresses.

## Test Signals

Tests should verify boot initialization from config, sysctl readback, unauthorized write `-EPERM`, authorized write updates, effective floor clamping by `CONFIG_LSM_MMAP_MIN_ADDR`, and mmap behavior for addresses below and above the resulting floor.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/min_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Kconfig -->
# sources/distributed-fs/ceph-client/security/safesetid/Kconfig

## Purpose

`safesetid/Kconfig` defines the SafeSetID LSM option, which restricts UID/GID transitions and related `CAP_SETUID`/`CAP_SETGID` uses according to system-wide allowlists.

## Important APIs, Types, and Functions

- `SECURITY_SAFESETID` builds SafeSetID, depends on `SECURITY`, selects `SECURITYFS`, defaults to `n`, and documents the allowlist-based setid transition model.

## Control Flow

When enabled, Kbuild includes the SafeSetID objects and the LSM registers hooks plus securityfs policy files. When disabled, no SafeSetID runtime policy exists.

## State and Persistence Behavior

The configuration only controls availability. Runtime policies are supplied through securityfs and live in RCU-protected rulesets in `lsm.c` and `securityfs.c`.

## Dependencies and Integration Points

SafeSetID depends on the generic LSM framework and securityfs. It integrates with credential-changing syscalls and capability checks through LSM hooks.

## Risks and Edge Cases

Improperly configured allowlists can prevent privileged processes from dropping privileges, which SafeSetID treats as dangerous enough to kill the process on denied setid transitions. Enabling the option without a policy has no transition constraints.

## Test Signals

Build tests should confirm `SECURITYFS` is selected. Runtime tests should verify securityfs policy files exist only when the LSM initializes and that no policy means default kernel setid behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Makefile -->
# sources/distributed-fs/ceph-client/security/safesetid/Makefile

## Purpose

The SafeSetID Makefile builds the SafeSetID composite object from enforcement and securityfs policy-editor sources.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SECURITY_SAFESETID) := safesetid.o` includes the LSM when enabled.
- `safesetid-y := lsm.o securityfs.o` links the hook implementation and securityfs interface into one object.

## Control Flow

There is no runtime flow. Kbuild creates `safesetid.o` from both component objects when `SECURITY_SAFESETID` is enabled.

## State and Persistence Behavior

No runtime state is defined here. Ruleset state and initialization flags are in the C sources.

## Dependencies and Integration Points

This file integrates the SafeSetID directory with the kernel security build.

## Risks and Edge Cases

If either component is omitted, SafeSetID would either enforce without a policy interface or expose an interface without hooks. The composite object list avoids that split.

## Test Signals

Configured builds should compile both `lsm.o` and `securityfs.o` into `safesetid.o`; disabled builds should omit them.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.c -->
# sources/distributed-fs/ceph-client/security/safesetid/lsm.c

## Purpose

`safesetid/lsm.c` implements SafeSetID enforcement. It restricts setuid/setgid/setgroups transitions for source IDs covered by policy and blocks non-setid uses of `CAP_SETUID` or `CAP_SETGID` for those constrained IDs.

## Important APIs, Types, and Functions

- `safesetid_initialized` gates later securityfs setup.
- `safesetid_setuid_rules` and `safesetid_setgid_rules` are RCU-protected active rulesets.
- `_setid_policy_lookup()` checks a supplied ruleset for default, constrained, or explicitly allowed source-to-destination transitions.
- `setid_policy_lookup()` selects the active UID or GID ruleset under RCU.
- `safesetid_security_capable()` constrains `CAP_SETUID`/`CAP_SETGID` uses outside setid syscall paths.
- `id_permitted_for_cred()` validates a candidate new UID/GID against old credentials and policy.
- `safesetid_task_fix_setuid()`, `safesetid_task_fix_setgid()`, and `safesetid_task_fix_setgroups()` enforce transitions after normal credential calculations.
- `safesetid_security_init()` registers hooks and schedules securityfs init.

## Control Flow

Policy lookup hashes by source ID. If a source has no rule, the result is `SIDPOL_DEFAULT`. If at least one rule for the source exists but no destination matches, the source is `SIDPOL_CONSTRAINED`. A matching destination is `SIDPOL_ALLOWED`. Capability checks ignore unrelated capabilities and allow `CAP_OPT_INSETID` paths to proceed to the later transition hooks. For other `CAP_SETUID` or `CAP_SETGID` uses, a constrained source ID is denied so it cannot use those capabilities for user namespace mappings or other auxiliary operations.

The setuid/setgid hooks first skip enforcement when the old real ID has no policy. Otherwise every new real, effective, saved, and filesystem ID must either already be present in the old credentials or be allowed by policy. Setgroups similarly validates every new supplementary group. On denial, the hook sends `SIGKILL` to the current process and returns `-EACCES`.

## State and Persistence Behavior

Active UID/GID policies persist in global RCU pointers populated by `securityfs.c`. `safesetid_initialized` is `__initdata` and only coordinates init sequencing. Rulesets are immutable after publication from the enforcement side; updates replace the entire pointer and old rules are freed after an RCU grace period.

## Dependencies and Integration Points

The file depends on LSM hooks for `task_fix_setuid`, `task_fix_setgid`, `task_fix_setgroups`, and `capable`; Linux credential and group-info structures; RCU; capability options; and policy types from `lsm.h`. It integrates with the securityfs policy writer through shared globals and `_setid_policy_lookup()`.

## Risks and Edge Cases

`id_permitted_for_cred()` uses the old real UID as the UID policy source; for GID checks the intended source is the old real GID, and any mismatch here would be security-sensitive. Killing on denied transitions prevents partially privileged processes from continuing after failing to drop privileges, but it is operationally harsh. Policy lookup mutates `pol->type` in `setid_policy_lookup()`, so ruleset type correctness relies on matching pointer selection.

## Test Signals

Tests should cover unconstrained default behavior, allowed and denied UID/GID transitions, transitions to IDs already in old credentials, fsuid/fsgid coverage, setgroups validation, denial-triggered `SIGKILL`, constrained `CAP_SETUID`/`CAP_SETGID` denial for user namespace mapping, `CAP_OPT_INSETID` pass-through, concurrent policy replacement under RCU, and warnings for blocked transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.h -->
# sources/distributed-fs/ceph-client/security/safesetid/lsm.h

## Purpose

`safesetid/lsm.h` defines SafeSetID's internal policy model shared by enforcement and securityfs code.

## Important APIs, Types, and Functions

- `enum sid_policy_type` represents default, constrained, and allowed decisions.
- `kid_t` wraps `kuid_t` or `kgid_t` in one union.
- `enum setid_type` distinguishes UID and GID policies.
- `struct setid_rule` stores one source-to-destination allow rule in a hash bucket.
- `SETID_HASH_BITS` sets the policy hash table to 256 buckets.
- `INVALID_ID` provides an invalid `kid_t` sentinel.
- `struct setid_ruleset` stores the hash table, original policy string, RCU head, and UID/GID type.
- `_setid_policy_lookup()`, active ruleset globals, and `safesetid_init_securityfs()` are declared for cross-file use.

## Control Flow

The header has no runtime flow, but it defines how callers interact: securityfs builds a complete `setid_ruleset`, enforcement looks up decisions, and old rulesets are retired through RCU.

## State and Persistence Behavior

The active ruleset pointers declared here are global and RCU-protected. Each ruleset retains the original policy string so securityfs reads can return the configured allowlist exactly as written.

## Dependencies and Integration Points

It depends on kernel UID/GID types and hash-table support. It is included by both `lsm.c` and `securityfs.c`, making it the contract between policy parsing and policy enforcement.

## Risks and Edge Cases

The `kid_t` union and `INVALID_ID` require callers to respect the accompanying `setid_type`; mixing UID and GID interpretations can produce invalid comparisons. Hashing by numeric kernel ID value assumes IDs are already mapped and valid in the relevant user namespace.

## Test Signals

Build coverage plus policy lookup tests for default, constrained, allowed, duplicate, invalid ID, UID, and GID cases validate the definitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/lsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/securityfs.c -->
# sources/distributed-fs/ceph-client/security/safesetid/securityfs.c

## Purpose

`safesetid/securityfs.c` implements the SafeSetID policy management interface under securityfs. It parses complete UID/GID allowlist replacements, validates and repairs unsafe transitive gaps, publishes new rulesets atomically under RCU, and serves the stored policy text back to readers.

## Important APIs, Types, and Functions

- `parse_policy_line()` parses one `<ID>:<ID>` line into a typed `setid_rule` using the writer file credential's user namespace.
- `insert_rule()` inserts a rule into the UID or GID hash table.
- `verify_ruleset()` detects destinations that would be unconstrained if reached and inserts self-rules to constrain them, returning `-EINVAL` for bogus-but-fixed policies.
- `handle_policy_update()` parses, validates, and publishes a full policy replacement.
- `safesetid_uid_file_write()` and `safesetid_gid_file_write()` enforce `CAP_MAC_ADMIN`, offset zero, and call the common update helper.
- `safesetid_file_read()` returns the current stored policy string under the relevant update mutex.
- `safesetid_init_securityfs()` creates `/sys/kernel/security/safesetid/uid_allowlist_policy` and `gid_allowlist_policy`.

## Control Flow

Policy writes must start at offset zero and come from a file credential capable of `CAP_MAC_ADMIN` in `init_user_ns`. The update helper allocates a fresh ruleset, duplicates the userspace buffer for parsing and for later readback, then requires every policy line to end with `\n`. Each line is split on `:`, parsed as u32, mapped with `make_kuid()` or `make_kgid()` in the writer's namespace, validated, checked for duplicates through `_setid_policy_lookup()`, and inserted.

After parsing, `verify_ruleset()` walks all rules and checks whether each destination ID is itself constrained. If not, it warns and inserts a self-transition rule so a process that transitions into that ID cannot later escape policy. Non-allocation verification errors are allowed to fall through after this fix-up, preserving the policy with added constraints. Publication uses the UID or GID update mutex and `rcu_replace_pointer()`, then releases the old ruleset after an RCU grace period.

Reads take the same update mutex, dereference the ruleset with lockdep protection, and copy the stored original policy string with `simple_read_from_buffer()`. Securityfs initialization is skipped if the LSM hook init did not set `safesetid_initialized`.

## State and Persistence Behavior

There are separate UID and GID update mutexes. Published rulesets persist until the next full replacement or shutdown. Old rulesets are freed asynchronously by `call_rcu()`, including all hash entries and stored policy text. The securityfs files expose the original submitted text, not necessarily the self-rules inserted during verification.

## Dependencies and Integration Points

This file depends on securityfs, credentials, namespace-aware UID/GID mapping, `CAP_MAC_ADMIN`, RCU, hash tables, and the enforcement-side globals and lookup helper in `lsm.c`. It is initialized through SafeSetID's `initcall_fs` hook.

## Risks and Edge Cases

The parser requires a trailing newline on the final line; missing it rejects the whole update. Failed updates release the fresh ruleset and leave the old active policy untouched. Returning `len` after a policy that `verify_ruleset()` judged insecure but fixed may surprise userspace because warnings are the only signal of the inserted self-rules. Readback omits fix-up rules because it uses the original policy string.

## Test Signals

Tests should cover permission denial without `CAP_MAC_ADMIN`, nonzero offset writes, malformed lines, missing newline, invalid namespace IDs, duplicate entries, valid UID and GID replacement, concurrent readers during replacement, RCU freeing under stress, transitive-unconstrained warnings and self-rule behavior, readback contents, and securityfs creation failure cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/securityfs.c -->
