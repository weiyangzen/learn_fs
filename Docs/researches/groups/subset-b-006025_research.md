# subset-b-006025 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/context_tracking.c -->
# sources/distributed-fs/ceph-client/kernel/context_tracking.c

## Purpose
`context_tracking.c` records high-level CPU execution-context transitions among kernel, user, guest, idle, IRQ, and NMI contexts. Its main job is to let RCU and virtual time accounting know when a CPU has entered or left an extended quiescent state, especially for nohz-full and idle CPUs where the periodic tick can be stopped.

## Important APIs, types, and functions
The key state is the per-CPU exported `struct context_tracking context_tracking`, whose fields include atomic context state, nesting, NMI nesting, recursion, and active tracking flags. Idle/interrupt entry points include `ct_idle_enter()`, `ct_idle_exit()`, `ct_irq_enter()`, `ct_irq_exit()`, `ct_irq_enter_irqson()`, `ct_irq_exit_irqson()`, `ct_nmi_enter()`, and `ct_nmi_exit()`. User/guest entry points include `__ct_user_enter()`, `ct_user_enter()`, `user_enter_callable()`, `__ct_user_exit()`, `ct_user_exit()`, `user_exit_callable()`, `ct_cpu_track_user()`, and optionally `context_tracking_init()`.

Internal helpers `ct_kernel_exit_state()` and `ct_kernel_enter_state()` update the atomic RCU-watching state with ordering guarantees. `ct_kernel_exit()` and `ct_kernel_enter()` handle nesting, tracepoints, deferred RCU quiescent states, task-RCU idle markers, and NMI nesting normalization. `context_tracking_recursion_enter()` prevents re-entrant user/guest tracking from corrupting state.

## Control flow
Idle entry calls `ct_kernel_exit(false, CT_RCU_WATCHING + CT_STATE_IDLE)` with IRQs already disabled, decrementing nesting and, at the outermost transition, marking RCU as no longer watching. Idle exit saves IRQ flags, calls `ct_kernel_enter(false, CT_RCU_WATCHING - CT_STATE_IDLE)`, and restores IRQs.

IRQ tracking is a thin wrapper around the NMI machinery: `ct_irq_enter()` and `ct_irq_exit()` require disabled IRQs and delegate to `ct_nmi_enter()` and `ct_nmi_exit()`. NMI entry checks whether RCU is currently watching; if not, it marks the CPU watching before the handler runs and increments `nmi_nesting` by one. If already watching, it increments by two so the outermost interrupt of an RCU-idle CPU can be distinguished on exit. NMI exit reverses that encoding and may re-enter RCU-idle state.

User and guest transitions use `__ct_user_enter()` and `__ct_user_exit()` with interrupts disabled. They first enter the recursion guard, compare the current tracked state, and either perform full RCU/vtime work when `ct->active` is true or only maintain state for inactive CPUs. Active user entry may trace/vtime-enter, request an RCU irq-work reschedule, then call `ct_kernel_exit(true, CT_RCU_WATCHING + state)`. Exit calls `ct_kernel_enter(true, CT_RCU_WATCHING - state)` before any kernel-side RCU usage and then runs vtime/trace exit for real user state.

## State and persistence behavior
All persistent state is per-CPU runtime state. `ct->state` encodes RCU watching plus context bits and is updated atomically with ordering requirements because other CPUs and RCU grace-period machinery observe it. `ct->nesting` and `ct->nmi_nesting` track nested idle/IRQ/NMI transitions and are written with `WRITE_ONCE()` to avoid tearing. `ct->active` is enabled by `ct_cpu_track_user()`, which also increments the `context_tracking_key` static branch and may seed `TIF_NOHZ` into `init_task`. No disk or user-visible persistent files are written.

## Dependencies and integration points
The file integrates with RCU (`rcu_is_watching_curr_cpu()`, `rcu_preempt_deferred_qs()`, `rcu_irq_work_resched()`, `rcu_irq_enter_check_tick()`), vtime accounting, lockdep, tracepoints for RCU and context tracking, architecture low-level entry/exit code, task-RCU idle markers, and nohz-full configuration. Many functions are `noinstr` and deliberately bracket trace/vtime calls inside `instrumentation_begin()` and `instrumentation_end()`.

## Risks and edge cases
The main risks are unbalanced nesting, calling entry/exit routines with the wrong IRQ state, using RCU in noinstr windows after RCU has been marked idle, and incorrect arch integration around user/guest entry. The obsolete callable wrappers use `local_irq_save/restore()` and are documented as unsafe for strict noinstr tracing/lockdep rules. NMI nesting uses a non-obvious one-versus-two increment encoding; regressions can lead to false RCU idle state or RCU stall reports. `CONFIG_CONTEXT_TRACKING_IDLE`, `CONFIG_CONTEXT_TRACKING_USER`, and nohz options substantially change behavior.

## Test signals
Useful test signals include booting with `CONFIG_RCU_EQS_DEBUG=y`, exercising idle entry/exit, NMI-in-idle, IRQ-in-idle, syscall/user transitions on nohz-full CPUs, guest entry/exit if present, migration after user exceptions, and tracing `rcu_watching`/context-tracking events. Stress cases should include nested interrupts, obsolete callable paths, full-dynticks CPUs, and RCU stall detection under high interrupt rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/context_tracking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cpu.c -->
# sources/distributed-fs/ceph-client/kernel/cpu.c

## Purpose
`cpu.c` implements Linux CPU hotplug, CPU mask initialization, SMT runtime control, CPU hotplug sysfs state controls, suspend/hibernate CPU freezing, and global CPU mitigation command-line parsing. It is the central state machine for bringing CPUs from offline to online and back while coordinating scheduler, RCU, timers, IRQs, workqueues, perf, watchdogs, architecture callbacks, and dynamically registered subsystem callbacks.

## Important APIs, types, and functions
The core types are `struct cpuhp_cpu_state`, a per-CPU state record containing current/target state, injected failure state, hotplug thread data, rollback fields, callback instance fields, AP synchronization state, and completions; and `struct cpuhp_step`, the global table entry for each CPU hotplug state with startup/teardown callbacks, multi-instance list, and `cant_stop` metadata.

Public and exported APIs include `cpu_maps_update_begin()`, `cpu_maps_update_done()`, `cpus_read_lock()`, `cpus_read_trylock()`, `cpus_read_unlock()`, `cpu_hotplug_disable()`, `cpu_hotplug_enable()`, `cpu_hotplug_disable_offlining()`, `cpu_smt_possible()`, `cpu_device_down()`, `remove_cpu()`, `notify_cpu_starting()`, `cpuhp_online_idle()`, `cpu_device_up()`, `add_cpu()`, `bringup_hibernate_cpu()`, `freeze_secondary_cpus()`, `thaw_secondary_cpus()`, `__cpuhp_setup_state_cpuslocked()`, `__cpuhp_setup_state()`, `__cpuhp_state_add_instance_cpuslocked()`, `__cpuhp_state_add_instance()`, `__cpuhp_state_remove_instance()`, `__cpuhp_remove_state_cpuslocked()`, `__cpuhp_remove_state()`, `cpuhp_smt_disable()`, `cpuhp_smt_enable()`, `set_cpu_online()`, `set_cpu_possible()`, `init_cpu_present()`, `init_cpu_possible()`, `boot_cpu_init()`, `boot_cpu_hotplug_init()`, `cpu_attack_vector_mitigated()`, `cpu_mitigations_off()`, and `cpu_mitigations_auto_nosmt()`.

Important internal flow helpers include `cpuhp_invoke_callback()`, `cpuhp_next_state()`, `cpuhp_set_state()`, `cpuhp_reset_state()`, `cpuhp_up_callbacks()`, `cpuhp_down_callbacks()`, `cpuhp_thread_fun()`, `cpuhp_invoke_ap_callback()`, `_cpu_up()`, `_cpu_down()`, `bringup_cpu()` or split-startup `cpuhp_kick_ap_alive()`/`cpuhp_bringup_ap()`, `takedown_cpu()`, and dynamic callback storage/rollback helpers.

## Control flow
CPU bringup starts through `cpu_up()` or device/sysfs wrappers. After validating `cpu_possible()`, node online state, hotplug-disable flags, and SMT bootability, `_cpu_up()` takes the CPU hotplug write lock, prepares the idle task for an offline CPU, sets the target state, and runs boot-processor callbacks up to `CPUHP_BRINGUP_CPU`. Architecture code then starts the AP. The AP calls `notify_cpu_starting()` before IRQs are enabled, runs non-failing starting callbacks, reaches `cpuhp_online_idle()`, unparks stop-machine, marks itself `CPUHP_AP_ONLINE_IDLE`, and completes the bringup completion. Remaining AP-bound online callbacks are executed by that CPU's `cpuhp/%u` smpboot thread.

CPU teardown starts through `cpu_down()` or device/sysfs wrappers. `_cpu_down()` rejects the last online CPU and preserves a housekeeping CPU for scheduler domains, sets `cpuhp_tasks_frozen`, and uses the AP hotplug thread for AP-bound callbacks down to `CPUHP_TEARDOWN_CPU`. `takedown_cpu()` parks smpboot threads, locks sparse IRQ allocation, uses stop-machine to run `take_cpu_down()` on the target CPU, invokes non-failing DYING callbacks, parks stopper threads, waits for `cpuhp_report_idle_dead()`, calls architecture CPU death, synchronizes AP/BP dead state, cleans lockdep state, and migrates RCU callbacks.

Dynamic hotplug states are installed through `__cpuhp_setup_state*()`. They reserve dynamic slots when requested, store callbacks under `cpuhp_state_mutex`, optionally invoke startup callbacks for already-present CPUs whose state is at or above the new state, and roll back earlier CPUs if a startup fails. Multi-instance states use hlist nodes and separate add/remove instance calls.

SMT control parses `nosmt`, tracks `cpu_smt_control`, `cpu_smt_num_threads`, and `cpu_smt_max_threads`, and exposes `/sys/devices/system/cpu/smt/control` and `active`. Disabling offlines non-primary or disallowed sibling CPUs while updating device offline state; enabling brings eligible present CPUs online.

## State and persistence behavior
Persistent runtime state includes per-CPU `cpuhp_state`, global `cpuhp_hp_states`, CPU masks (`__cpu_possible_mask`, `__cpu_online_mask`, `__cpu_enabled_mask`, `__cpu_present_mask`, `__cpu_active_mask`, `__cpu_dying_mask`), `__num_online_cpus`, `cpus_booted_once_mask`, `cpu_hotplug_disabled`, `cpu_hotplug_offline_disabled`, `cpuhp_tasks_frozen`, SMT control variables, and CPU mitigation configuration parsed at boot. Sysfs exposes hotplug state, target, fail injection, state listing, and SMT controls but this file does not write persistent storage.

Synchronization is layered. `cpu_add_remove_lock` serializes CPU map updates and hotplug-disable changes. `cpu_hotplug_lock` is a percpu rwsem used by subsystems to exclude hotplug. `cpuhp_state_mutex` protects callback table changes. Per-CPU completions coordinate BP/AP state machine handoffs. Optional atomic AP sync states handle early alive/dead handshake timeouts.

## Dependencies and integration points
This file integrates with scheduler CPU activation/deactivation, RCU prepare/online/offline/dead callbacks, timers/hrtimers/tick, IRQ affinity and sparse IRQ locking, workqueues, smpboot threads, stop_machine, perf, watchdogs, random, relay, CPU device sysfs, PM notifier/freezer paths, hibernation, CPU topology/SMT helpers, housekeeping masks, architecture `__cpu_up()`, `__cpu_disable()`, `__cpu_die()`, arch hotplug sync hooks, and mitigation parser support.

## Risks and edge cases
The hotplug state machine is rollback-heavy and many callback ranges cannot fail. Bugs can leave CPUs between states, fail to re-enable hotplug after suspend paths, leak dynamic callback registrations, or race with sysfs/device hotplug. The AP hotplug thread and BP side share per-CPU state with memory barriers; changing ordering around `should_run`, completions, or rollback fields is high risk. SMT controls interact with `cpus_booted_once_mask`, platform errata, device offline flags, node online state, and topology primary-thread rules. The sysfs `fail` attribute intentionally injects callback failures but rejects atomic/dead states; failures elsewhere may exercise rare rollback paths.

## Test signals
Important signals include CPU online/offline through device sysfs and `target`, dynamic callback registration/unregistration with invoke enabled, multi-instance add/remove rollback, fail-injection through `hotplug/fail`, suspend/hibernate `freeze_secondary_cpus()` and `thaw_secondary_cpus()`, kexec/reboot `smp_shutdown_nonboot_cpus()`, SMT `on`, `off`, `forceoff`, and numeric thread-count control, parallel boot with `cpuhp.parallel=`, `nosmt`, mitigation command-line parsing, CPU mask counters, and RCU/timer/workqueue/perf callbacks after repeated hotplug loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cpu_pm.c -->
# sources/distributed-fs/ceph-client/kernel/cpu_pm.c

## Purpose
`cpu_pm.c` provides a raw notifier-chain API for CPU and CPU-cluster low-power entry/exit. It lets low-level platform code notify drivers that per-CPU or cluster-local hardware state may be lost and must be saved/restored with interrupts disabled.

## Important APIs, types, and functions
The file owns `cpu_pm_notifier`, a `raw_notifier_head` plus `raw_spinlock_t`. Public APIs are `cpu_pm_register_notifier()`, `cpu_pm_unregister_notifier()`, `cpu_pm_enter()`, `cpu_pm_exit()`, `cpu_cluster_pm_enter()`, and `cpu_cluster_pm_exit()`. Internal helpers `cpu_pm_notify()` and `cpu_pm_notify_robust()` call raw notifier chains and translate notifier return values with `notifier_to_errno()`.

When `CONFIG_PM` is enabled, `cpu_pm_suspend()` and `cpu_pm_resume()` are registered as syscore suspend/resume operations by `cpu_pm_init()`. Suspend runs CPU then cluster entry notifications; resume runs cluster then CPU exit notifications.

## Control flow
Register/unregister calls take the raw spinlock with IRQ save/restore and update the notifier chain. Entry calls use `raw_notifier_call_chain_robust()` under the raw lock so a failing entry callback receives the matching failure event for already-called notifiers. Exit calls use `raw_notifier_call_chain()` under RCU read lock rather than the raw lock. Platform code is expected to call the entry/exit APIs on the affected CPU with interrupts disabled and with correct nesting.

## State and persistence behavior
State is limited to the in-kernel notifier chain and lock. There is no on-disk persistence or sysfs state. Robust entry notifications may partially execute callbacks and then issue failure notifications when a notifier returns an error.

## Dependencies and integration points
This module integrates with CPU idle/power-management platform code, syscore suspend/resume, interrupt-controller drivers, local timer drivers, floating-point/co-processor context code, and any driver that registers a CPU PM notifier. It deliberately uses raw notifiers and raw spinlock locking because idle-task notification paths must not block under PREEMPT_RT.

## Risks and edge cases
Ordering is strict: cluster entry must follow per-CPU entry for all CPUs in the power domain, and cluster exit must precede per-CPU exit. Callers must avoid double entry on the same CPU before exit. Notifier callbacks run with interrupts disabled and must not sleep. Exit notifications are not robust, so failed restore-style callbacks are only reflected by notifier return aggregation. A callback that assumes normal spinlocks can block on RT kernels would be unsafe in this path.

## Test signals
Test by registering synthetic notifiers that record event ordering, inject failures in `CPU_PM_ENTER` and `CPU_CLUSTER_PM_ENTER`, verify robust failure callbacks, exercise syscore suspend/resume ordering, and run on PREEMPT_RT-style configurations to catch sleeping callbacks. Platform idle paths should validate IRQ-disabled preconditions and no duplicate entry without exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cpu_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_core.c -->
# sources/distributed-fs/ceph-client/kernel/crash_core.c

## Purpose
`crash_core.c` implements shared crash-kernel support for kdump/kexec: copying vmcoreinfo into crash memory, deciding when oops paths should crash-kexec, executing the crash kernel, generating ELF core headers and CPU notes, shrinking reserved crash memory, and optionally updating crash-kernel segments when CPU or memory hotplug events occur.

## Important APIs, types, and functions
Important globals include per-CPU `crash_notes`, `kexec_crash_image`, crash resource variables from reservation code, and crash hotplug locks/notifiers under `CONFIG_CRASH_HOTPLUG`. Public functions include `kimage_crash_copy_vmcoreinfo()`, `kexec_should_crash()`, `kexec_crash_loaded()`, `__crash_kexec()`, BPF kfunc `crash_kexec()`, `crash_prepare_elf64_headers()`, `crash_exclude_mem_range()`, `crash_get_memory_size()`, `crash_shrink_memory()`, `crash_save_cpu()`, and `crash_check_hotplug_support()`.

Internal helpers include `crash_cma_clear_pending_dma()`, `crash_resource_size()`, `__crash_shrink_memory()`, `crash_notes_memory_init()`, `crash_handle_hotplug_event()`, memory and CPU hotplug notifiers, and `crash_hotplug_init()`.

## Control flow
When a crash kimage is loaded, `kimage_crash_copy_vmcoreinfo()` allocates pages from crash memory, maps them with `vmap()`, stores `image->vmcoreinfo_data_copy`, and points the vmcoreinfo safe-copy machinery at that mapping. On panic or eligible oops, `crash_kexec()` uses `panic_try_start()` so only one CPU proceeds. `__crash_kexec()` takes the kexec lock, saves registers and vmcoreinfo, runs machine crash shutdown, waits for crashkernel CMA DMA quiescence if configured, and calls `machine_kexec()`.

`crash_prepare_elf64_headers()` allocates an ELF64 core header, emits one PT_NOTE for each possible CPU's `crash_notes`, one PT_NOTE for vmcoreinfo, optionally one PT_LOAD for the kernel text virtual mapping, and one PT_LOAD per crash memory range. `crash_exclude_mem_range()` mutates a sorted `struct crash_mem` range list to remove a closed interval, handling complete removal, left/right trimming, and splitting with `-ENOMEM` if no spare range slot exists.

`crash_shrink_memory()` rejects shrinking while a crash image is loaded, rounds the requested size, releases the tail of `crashk_res` or `crashk_low_res` back to system RAM, reinserts freed resources, and swaps high/low resource roles if needed. Crash hotplug notifiers locate the elfcorehdr segment, unprotect crash reserved memory, set `image->hp_action`, call arch update code, mark the elfcorehdr updated, and re-protect the region.

## State and persistence behavior
Persistent kernel state includes allocated per-CPU `crash_notes`, the protected crash kimage, vmcoreinfo safe copy, crash reserved resources, image hotplug metadata, and ELF header buffers passed to kexec. `crash_shrink_memory()` changes the kernel resource tree and frees reserved physical ranges back to normal RAM. Crash hotplug updates modify the loaded crash image in reserved memory, but there is no filesystem persistence.

## Dependencies and integration points
The file integrates with kexec image locking and segment management, architecture crash shutdown/kexec/protect/unprotect hooks, vmcoreinfo, panic ownership, BPF kfunc exposure, ELF core definitions, per-CPU allocation, memblock/resources, RCU crash callback migration indirectly through CPU hotplug, memory hotplug notifier chains, cpuhp dynamic states, CMA crashkernel ranges, and kdump tooling expectations for ELF core headers.

## Risks and edge cases
`__crash_kexec()` runs in panic context and must tolerate broken system state. Lock acquisition can fail if another kexec operation owns the lock. `crash_exclude_mem_range()` assumes sorted non-overlapping ranges and requires spare capacity before split operations. Shrinking crash memory while image state or resource tree state is inconsistent could expose reserved memory incorrectly. Crash hotplug intentionally does not roll back CPU/memory hotplug on update failure, so a stale elfcorehdr can be left behind with only diagnostics. CMA reservations force a fixed 10-second delay before entering the crash kernel.

## Test signals
Existing direct test coverage comes from `crash_core_test.c` for `crash_exclude_mem_range()`. Additional signals include kdump boot with and without vmcoreinfo safe copy, ELF header validation with per-CPU notes and memory ranges, panic/oops paths with `crash_kexec_post_notifiers` and `panic_on_oops`, crash memory shrink via sysfs/control callers, memory and CPU hotplug while a hotplug-capable crash image is loaded, CMA crashkernel reservations, and architecture protect/unprotect verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_core_test.c -->
# sources/distributed-fs/ceph-client/kernel/crash_core_test.c

## Purpose
`crash_core_test.c` is a KUnit suite for `crash_exclude_mem_range()`. It validates how the crash-memory range exclusion helper mutates sorted memory ranges when an interval is outside, touching, overlapping, contained, covering, or splitting an existing range.

## Important APIs, types, and functions
The suite uses `struct crash_mem`, `struct range`, and KUnit assertions. Helpers are `create_crash_mem()`, which allocates a variable-sized `struct crash_mem` with KUnit-managed memory; `assert_ranges_equal()`, which checks range count and start/end values; and `run_exclude_test_case()`, which invokes `crash_exclude_mem_range()` and validates either expected output ranges or unchanged range count on expected errors.

Test data is represented by `struct exclude_test_param`. Test cases are `exclude_single_range_test()` and `exclude_range_regression_test()`, registered in `crash_exclude_mem_range_suite`.

## Control flow
Each test iterates over static parameter arrays, logs the case description, allocates a `crash_mem` sized by `initial_max_ranges`, copies initial ranges, calls `crash_exclude_mem_range(mem, exclude_start, exclude_end)`, checks the expected return code, and compares mutated ranges when success is expected. Error cases currently assert that `nr_ranges` remains equal to the initial count.

## State and persistence behavior
All memory is KUnit-managed and scoped to the test. The tests do not modify global crash-kernel state, resources, kexec images, or persistent storage. Static compound-literal range arrays define expected data.

## Dependencies and integration points
The suite depends on KUnit, `linux/crash_core.h`, and the linked implementation of `crash_exclude_mem_range()` from `crash_core.c`. It is a low-level algorithm test rather than an integration test for kexec or crash reservations.

## Risks and edge cases
The suite gives broad single-range coverage, including no overlap, boundary-touch no-ops, partial trims, full removals, point exclusions, split success, and split ENOMEM. The regression set includes a low-1M full exclusion and a known out-of-bound/capacity case. It does not validate unsorted input, overlapping initial ranges, multi-range partial mutation beyond the regression cases, invalid `mstart > mend`, or content preservation on ENOMEM beyond `nr_ranges`.

## Test signals
The primary signal is the KUnit suite name `crash_exclude_mem_range_tests`. High-value additions would cover multiple ranges with split plus removal in one call, range-list ordering after complex exclusions, invalid reversed intervals if the API should reject them, maximum capacity boundaries, and explicit verification that range contents remain unchanged on `-ENOMEM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_core_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_dump_dm_crypt.c -->
# sources/distributed-fs/ceph-client/kernel/crash_dump_dm_crypt.c

## Purpose
`crash_dump_dm_crypt.c` preserves dm-crypt keys across a kexec crash dump by collecting configured logon keys from the current kernel keyring, adding them as a kexec buffer in crash memory, and restoring them into the kdump kernel's user keyring. It exposes a configfs interface for selecting keys, reusing already-saved keys, and restoring keys in the crash kernel.

## Important APIs, types, and functions
Key data types are `struct dm_crypt_key`, containing size, description, and up to 256 bytes of key data; `struct keys_header`, a counted flexible-array header; and `struct config_key`, a configfs item with a key description. Globals include `key_count`, `keys_header`, exported `dm_crypt_keys_addr`, `is_dm_key_reused`, `restore`, and configfs subsystem `crash_dm_crypt_keys`.

Important functions are `setup_dmcryptkeys()`, weak `dm_crypt_keys_read()`, `read_key_from_user_keyring()`, `build_keys_header()`, `crash_load_dm_crypt_keys()`, `restore_dm_crypt_keys_to_thread_keyring()`, `get_keys_from_kdump_reserved_memory()`, configfs attribute handlers for `description`, `count`, `reuse`, and `restore`, and `configfs_dmcrypt_keys_init()`.

## Control flow
The normal kernel exposes configfs items under `crash_dm_crypt_keys`. Users create per-key items and write key descriptions. During crash-image load, `crash_load_dm_crypt_keys()` returns early if no keys are configured. Otherwise it builds a fresh `keys_header` unless reuse mode is active, reads each configured logon key with `request_key(&key_type_logon, description, NULL)`, copies the payload under the key semaphore, and adds the header as a randomized `kexec_buf`. The crash image records the resulting physical address and size.

In a kdump kernel, the early `dmcryptkeys=` parameter sets `dm_crypt_keys_addr`. The configfs subsystem uses a reduced item type exposing only `restore`. Writing restore triggers `restore_dm_crypt_keys_to_thread_keyring()`, which reads the key count and header from old memory through `dm_crypt_keys_read()`, allocates a local header, and recreates user keys in `KEY_SPEC_USER_KEYRING` with `key_create_or_update()`.

Reuse mode checks that a crash image has a stored dm-crypt key address, unprotects crash reserved memory, maps the saved page, copies the header into current memory, and re-protects the crash reserved region.

## State and persistence behavior
Configured key descriptions persist only as configfs kernel objects until removed. Key material is copied into `keys_header` and then into a kexec buffer in crash reserved memory; that memory intentionally persists across kexec into the dump kernel. The kdump kernel restores keys into the current user's keyring. `key_count` is global and tracks configfs items, while `keys_header` is reused and freed with `kvfree()`/`kzalloc()` across loads. No disk files are written by this code.

## Dependencies and integration points
The file integrates with the kernel key retention service, logon key type, user keyring permissions, configfs, kexec file buffer loading, crash reserved memory protection, old-memory reads, confidential-computing memory-encryption attributes, `is_kdump_kernel()`, and kexec image fields `dm_crypt_keys_addr` and `dm_crypt_keys_sz`.

## Risks and edge cases
This code handles sensitive key material. Risks include inadequate zeroization of freed `keys_header`, global `key_count` and `keys_header` races through configfs operations, off-by-one maximum-key check because item creation rejects only `key_count > KEY_NUM_MAX`, and restoring from old memory with weak validation of `dm_crypt_keys_read()` return values. `config_key_release()` frees the `struct config_key` but not its duplicated `description`, which is a leak unless configfs releases attributes elsewhere. `restore_dm_crypt_keys_to_thread_keyring()` leaks the looked-up keyring reference on early failure after `lookup_user_key()`. A malformed old-memory header can carry invalid per-key sizes or descriptions unless all fields are checked before key creation.

## Test signals
Test signals include configfs create/remove/count behavior, description length and empty-description rejection, loading with zero keys, missing logon key, revoked key, oversized key payload, multiple keys up to the maximum, reuse from crash reserved memory, restoration in a kdump kernel with `dmcryptkeys=`, encrypted-memory oldmem reads, keyring permission failures, and repeated load/unload cycles with memory-leak and key-material lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_dump_dm_crypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_reserve.c -->
# sources/distributed-fs/ceph-client/kernel/crash_reserve.c

## Purpose
`crash_reserve.c` parses `crashkernel=` command-line forms and reserves physical memory for a crash kernel. It supports simple, range-based, high/low split, and optional CMA crashkernel reservations, then publishes reserved crash resources into the kernel I/O memory resource tree.

## Important APIs, types, and functions
Global resources are `crashk_res` and `crashk_low_res`, both named "Crash kernel" with system RAM and crash-kernel descriptors. Parsing helpers include `parse_crashkernel_mem()`, `parse_crashkernel_simple()`, `parse_crashkernel_suffix()`, `get_last_crashkernel()`, `__parse_crashkernel()`, and exported/arch-called `parse_crashkernel()`.

Reservation helpers include dummy early parameter handler `parse_crashkernel_dummy()`, `reserve_crashkernel_low()`, `reserve_crashkernel_generic()`, `reserve_crashkernel_cma()`, and `insert_crashkernel_resources()`. CMA state includes `crashk_cma_ranges` and `crashk_cma_cnt` when supported.

## Control flow
`parse_crashkernel()` first parses the last plain `crashkernel=` that is not a known suffix. It chooses range syntax if the selected token contains a colon before the next space, otherwise simple `size[@offset]`. On architectures with generic reservation, if no plain value is present it parses `,high`, optionally parses `,low` or defaults low memory, and separately parses optional `,cma`.

`reserve_crashkernel_generic()` reserves the requested size with `memblock_phys_alloc_range()`. It honors a fixed base if supplied, otherwise tries low memory first for plain reservations, can fall back to high memory with a default low allocation, and for explicit high reservations can fall back to low memory. If the selected base is high and low memory is needed, it calls `reserve_crashkernel_low()`. Successful reservations update `crashk_res` and possibly `crashk_low_res`, mark the physical ranges ignored by kmemleak, and may insert resources immediately depending on architecture support.

`reserve_crashkernel_cma()` attempts to reserve the requested CMA amount in one or more contiguous regions, halving the request block size on allocation failure until a page-sized lower bound or maximum range count is reached.

## State and persistence behavior
The file mutates early-boot global reservation state: `crashk_res`, `crashk_low_res`, `crashk_cma_ranges`, and `crashk_cma_cnt`. It reserves memory with memblock/CMA so normal allocators cannot use it and later inserts resources into `iomem_resource`. These reservations persist for the running kernel lifetime and across crash-kernel load operations, but are not written to disk.

## Dependencies and integration points
Dependencies include memblock, CMA, kmemleak, I/O resource management, architecture constants such as `CRASH_ALIGN`, `CRASH_ADDR_LOW_MAX`, `CRASH_ADDR_HIGH_MAX`, optional `HAVE_ARCH_ADD_CRASH_RES_TO_IOMEM_EARLY`, command-line early parameters, and arch code that calls `parse_crashkernel()` and `reserve_crashkernel_generic()`.

## Risks and edge cases
Parsing uses the last matching `crashkernel=` token and filters known suffixes, so duplicate or malformed command lines can be surprising. Range syntax rounds total RAM up to 128M to tolerate firmware reservations. The parser rejects zero or system-RAM-sized reservations but suffix and CMA values have separate handling. Fixed-base reservations fail if the region is busy; fallback behavior differs between plain and high reservations. CMA reservation may reserve less than requested and only warn. Resource insertion is conditional on architecture timing, so early/late I/O resource visibility differs by platform.

## Test signals
Useful tests include command lines for simple size, size with offset, range lists, malformed ranges, duplicate crashkernel entries, `,high`, `,low`, `,cma`, missing low default, fixed-base busy failure, low-to-high and high-to-low fallback, resource-tree insertion, kmemleak ignore behavior, and CMA partial-reservation warnings with range count limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/crash_reserve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cred.c -->
# sources/distributed-fs/ceph-client/kernel/cred.c

## Purpose
`cred.c` implements the kernel credential lifecycle: allocation, copying for fork/exec, committing changed credentials, aborting unused credentials, RCU-safe destruction, credential comparison for filesystem access, user-count tracking, kernel-service credentials, and LSM override helpers.

## Important APIs, types, and functions
The file owns the credential slab cache `cred_jar`. Public functions include `__put_cred()`, `exit_creds()`, `get_task_cred()`, `cred_alloc_blank()`, `prepare_creds()`, `prepare_exec_creds()`, `copy_creds()`, `commit_creds()`, `abort_creds()`, `cred_fscmp()`, `set_cred_ucounts()`, `cred_init()`, `prepare_kernel_cred()`, `set_security_override()`, and `set_create_files_as()`. Internal helpers include `put_cred_rcu()` and `cred_cap_issubset()`.

The relevant data is `struct cred` and its references to UID/GID values, user namespace, user and ucounts objects, group_info, keyrings, request-key auth, security blob, capability sets, and RCU head.

## Control flow
`prepare_creds()` allocates a new credential object, copies current credentials, resets use count to one, pins group/user/user_ns/keyring/ucount references, clears the security blob, and asks the LSM layer to prepare copied security state. Callers mutate the copy and either `commit_creds()` or `abort_creds()`.

`commit_creds()` verifies the task is not in subjective override state, takes an extra reference for subjective credentials, adjusts dumpability and parent-death signal if IDs/capabilities become less privileged, updates keyring fsuid/fsgid state, increments new user process counts if user or namespace changed, RCU-publishes `real_cred` and `cred`, decrements old process counts, switches credential namespace state, sends proc connector UID/GID events, and drops both old references.

`copy_creds()` shares credentials for new threads when possible. Otherwise it prepares a copy, optionally creates a new user namespace and ucounts for `CLONE_NEWUSER`, handles thread/process keyring inheritance, installs the new object as both objective and subjective credentials for the child, and accounts the process count. `exit_creds()` drops task credential references and cached requested keys. Destruction runs either immediately for `non_rcu` or through `call_rcu()`, then frees LSM, keyrings, group_info, user, ucounts, user namespace, and slab memory.

## State and persistence behavior
Credential objects are refcounted and RCU-published. Task pointers `task->real_cred` and `task->cred` are the authoritative runtime state; old objects remain valid to RCU readers until grace period completion. User process counts and namespace references are adjusted during fork, commit, and free. Keyring references and LSM security blobs are owned by each credential object. There is no filesystem persistence, but credential changes are observable through proc connector events and process access-control behavior.

## Dependencies and integration points
This file integrates with the LSM hooks (`security_prepare_creds()`, `security_cred_free()`, `security_kernel_act_as()`, `security_kernel_create_files_as()`), keyrings, user namespaces, ucounts and RLIMIT_NPROC accounting, proc connector, ptrace/dumpability rules, scheduler task lifecycle, RCU, slab accounting, and filesystem UID/GID access comparisons.

## Risks and edge cases
Credential mutation is security-critical. Callers must never modify published credentials directly and must not call `commit_creds()` while subjective credentials differ from objective credentials. The memory barrier before RCU publication is required so ptrace observes nondumpability before privilege changes. Reference balancing across keys, namespaces, group info, ucounts, and LSM security blobs is subtle, especially on error paths. `cred_cap_issubset()` handles nested user namespace capability semantics; mistakes can make dumpability too permissive or too restrictive. `prepare_kernel_cred()` rejects a NULL daemon and strips keyrings for kernel service credentials.

## Test signals
Test signals include fork thread sharing versus process copy behavior, `CLONE_NEWUSER` success and failure paths, exec credential reset of fs IDs and keyrings, UID/GID changes triggering proc connector events, dumpability changes under privilege drop and capability subset changes, ptrace races, keyring fsuid/fsgid changes, LSM allocation failure rollback, ucounts exhaustion, RCU delayed free behavior, and `cred_fscmp()` ordering across fsuid/fsgid/groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/Makefile -->
# sources/distributed-fs/ceph-client/kernel/debug/Makefile

## Purpose
This Makefile wires the kernel debugger objects into the build. It builds the KGDB core and GDB remote stub when `CONFIG_KGDB` is enabled and descends into the KDB frontend directory when `CONFIG_KGDB_KDB` is enabled.

## Important APIs, types, and functions
There are no C APIs or runtime types. The important build variables are `obj-$(CONFIG_KGDB) += debug_core.o gdbstub.o` and `obj-$(CONFIG_KGDB_KDB) += kdb/`.

## Control flow
Kbuild evaluates the config-controlled object lists. Enabling KGDB compiles and links `debug_core.o` and `gdbstub.o`; enabling KGDB_KDB additionally includes the `kdb/` subdirectory in the build.

## State and persistence behavior
The file affects build outputs only. It does not generate source, write runtime state, or expose persistent configuration beyond compiled object inclusion.

## Dependencies and integration points
It integrates with Kconfig symbols `CONFIG_KGDB` and `CONFIG_KGDB_KDB`, and with the child KDB Makefile for frontend commands and generated KDB command data.

## Risks and edge cases
Misconfiguring this file can omit required debugger objects or include KDB without the core objects. Because `gdbstub.o` is tied to `CONFIG_KGDB`, downstream KDB/GDB transition helpers depend on this build linkage.

## Test signals
Build matrix checks should cover `CONFIG_KGDB=n`, `CONFIG_KGDB=y CONFIG_KGDB_KDB=n`, and both enabled. Link errors in KGDB symbols or missing KDB directory objects are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/debug_core.c -->
# sources/distributed-fs/ceph-client/kernel/debug/debug_core.c

## Purpose
`debug_core.c` is the architecture-independent KGDB/KDB core. It manages debugger entry from exceptions, CPU rendezvous, software breakpoints, master/slave CPU state, debugger I/O module registration, sysrq/panic/reboot hooks, optional KGDB console output, early `kgdbwait`, and switching between KDB and GDB remote modes.

## Important APIs, types, and functions
Global state includes `kgdb_info[NR_CPUS]`, `kgdb_connected`, `kgdb_io_module_registered`, `dbg_io_ops`, `kgdb_active`, `masters_in_kgdb`, `slaves_in_kgdb`, `kgdb_break[]`, `kgdb_usethread`, `kgdb_contthread`, `kgdb_single_step`, `kgdb_cpu_doing_single_step`, `dbg_switch_cpu`, `dbg_kdb_mode`, and boot/module parameters `kgdb_use_con` and `kgdbreboot`.

Public functions include weak arch hooks `kgdb_arch_set_breakpoint()`, `kgdb_arch_remove_breakpoint()`, `kgdb_validate_break_address()`, `kgdb_arch_pc()`, `kgdb_arch_init()`, `kgdb_skipexception()`, `kgdb_call_nmi_hook()`, and `kgdb_roundup_cpus()`; breakpoint APIs `dbg_activate_sw_breakpoints()`, `dbg_set_sw_break()`, `dbg_deactivate_sw_breakpoints()`, `dbg_remove_sw_break()`, `kgdb_isremovedbreak()`, `kgdb_has_hit_break()`, `dbg_remove_all_break()`, and `kgdb_free_init_mem()`; entry APIs `kgdb_handle_exception()`, `kgdb_nmicallback()`, `kgdb_nmicallin()`, `kgdb_panic()`, `dbg_late_init()`, `kgdb_register_io_module()`, `kgdb_unregister_io_module()`, `dbg_io_get_char()`, and `kgdb_breakpoint()`.

## Control flow
Software breakpoint setup validates an address by temporarily writing and removing a breakpoint instruction, then records it in `kgdb_break[]` as `BP_SET`. Activation writes all set breakpoints into kernel text and flushes icache where safe; deactivation restores saved instructions; removal marks matching inactive breakpoints removed; remove-all clears both software and architecture hardware breakpoints.

`kgdb_handle_exception()` constructs a `kgdb_state`, rejects non-trap exceptions when `panic_timeout` would auto-reboot, checks recursive entry, and calls `kgdb_cpu_enter()` as a would-be master. `kgdb_cpu_enter()` disables hardware breakpoints, records per-CPU debugger info, arbitrates the master CPU with `dbg_master_lock`, optionally rounds up other CPUs into slave loops, disables active software breakpoints, turns tracing off, and dispatches to `kdb_stub()` or `gdb_serial_stub()`. It handles mode switching, CPU master switching, lockdown blocking of GDB write access, breakpoint reactivation, post-exception hooks, release of slave CPUs, watchdog touches, and IRQ/RCU restoration.

I/O module registration initializes the driver, replaces a deinit-capable existing driver if necessary, registers debugger callbacks, sysrq key, module/reboot notifiers, console output if requested, and triggers `kgdbwait` early breakpoints when possible. Unregistration requires no active GDB connection, unregisters callbacks, clears `dbg_io_ops`, and deinitializes the driver.

## State and persistence behavior
State is entirely in-kernel and volatile. Breakpoints mutate kernel text while active and keep saved instructions in `kgdb_break[]`. Debugger sessions update per-CPU `kgdb_info`, active CPU atomics, master/slave counters, connection mode, and selected thread pointers. Boot parameters persist for the running kernel lifetime. KGDB console registration affects console output routing while enabled.

## Dependencies and integration points
The core integrates with architecture KGDB operations, GDB stub, KDB frontend, sysrq, panic notifier path, reboot notifier, module notifier, console subsystem, security lockdown, SMP call-single/NMI roundup, tracing, watchdogs, RCU stall reset, hardirq state, icache flushing, and blocklisted breakpoint addresses.

## Risks and edge cases
Debugger entry runs in exceptional contexts with interrupts disabled and may stop all CPUs. Recursive entry is dangerous: the code may remove all breakpoints and panic if recursion exceeds one level. Breakpoint writes use nofault kernel memory access and can fail or corrupt text if remove fails. CPU roundup can time out, leaving non-stopped CPUs interfering with debugging. Lockdown can force KDB mode or bail out of GDB. Unregistering an I/O module while connected is a BUG. Early debugging supports pre-percpu environments by using NR_CPUS arrays rather than percpu data.

## Test signals
Signals include software breakpoint set/hit/remove, breakpoints in init memory and `kgdb_free_init_mem()`, hardware breakpoint arch hooks, sysrq-g entry, panic entry with and without `panic_timeout`, `kgdbwait`, replacing I/O modules, `kgdbcon`, reboot notifier detach, KDB/GDB mode switching, CPU switching, single-step on SMP, roundup timeout behavior, lockdown mode, and recursive breakpoint-in-debugger recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/debug_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/debug_core.h -->
# sources/distributed-fs/ceph-client/kernel/debug/debug_core.h

## Purpose
`debug_core.h` is the private interface between the KGDB core, GDB stub, and KDB frontend. It defines shared debugger state structures, CPU exception-state flags, special control return values, and cross-file function declarations.

## Important APIs, types, and functions
The main type is `struct kgdb_state`, which carries exception vector, signal, error code, CPU, pass-exception flag, thread query/current thread IDs, selected thread ID, registers, and optional `send_ready` synchronization pointer. `struct debuggerinfo_struct` stores per-CPU debugger info pointer, task, exception state, return state, IRQ depth, entry count, and roundup flag.

Flags include `DCPU_WANT_MASTER`, `DCPU_NEXT_MASTER`, `DCPU_IS_SLAVE`, and `DCPU_WANT_BT`. Special return values are `DBG_PASS_EVENT` for KDB/GDB mode switching and `DBG_SWITCH_CPU_EVENT` for switching the master CPU. Declarations cover software breakpoint APIs, polled I/O, `gdb_serial_stub()`, `gdbstub_msg_write()`, `gdbstub_state()`, KDB entry and parser helpers, and `kdb_dump_stack_on_cpu()`.

## Control flow
The header has no runtime flow. It provides the contracts that allow `debug_core.c` to call the selected frontend, GDB stub to hand commands to KDB, and KDB to request CPU backtraces or switch modes. When `CONFIG_KGDB_KDB` is disabled, `kdb_stub()` is an inline stub returning `DBG_PASS_EVENT`.

## State and persistence behavior
The header declares shared runtime state such as `kgdb_info`, `dbg_switch_cpu`, and `dbg_kdb_mode` but owns no storage. It has no persistence behavior.

## Dependencies and integration points
It depends on kernel task/register types through included users and is included by KGDB core, GDB stub, and KDB implementation files. It is tightly coupled to `include/linux/kgdb.h`, arch KGDB register handling, and KDB private code.

## Risks and edge cases
Because this is a private ABI among debugger components, changes to `struct kgdb_state`, flag meanings, or special return values must be reflected across all frontends. The inline KDB stub preserves buildability without KDB, but code paths must still handle `DBG_PASS_EVENT` when no alternate frontend exists.

## Test signals
Build tests should cover KGDB with and without KDB. Runtime mode-switch tests, CPU-switch tests, and GDB qRcmd-to-KDB paths exercise most of this header's shared contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/debug_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/gdbstub.c -->
# sources/distributed-fs/ceph-client/kernel/debug/gdbstub.c

## Purpose
`gdbstub.c` implements the GDB remote serial protocol for KGDB. It translates packets from a host GDB into kernel register access, memory reads/writes, breakpoint control, thread queries, qRcmd KDB commands, continue/single-step requests, detach/kill, and emergency reboot.

## Important APIs, types, and functions
Static buffers `remcom_in_buffer`, `remcom_out_buffer`, and `gdbmsgbuf` hold protocol packets. `gdb_regs` stores architecture registers in GDB format. Core packet helpers are `gdbstub_read_wait()`, `get_packet()`, `put_packet()`, and `gdbstub_msg_write()`. Conversion helpers include `kgdb_mem2hex()`, `kgdb_hex2mem()`, `kgdb_hex2long()`, `kgdb_ebin2mem()`, `pt_regs_to_gdb_regs()`, and `gdb_regs_to_pt_regs()`.

Command handlers include `gdb_cmd_status()`, `gdb_cmd_getregs()`, `gdb_cmd_setregs()`, `gdb_cmd_memread()`, `gdb_cmd_memwrite()`, register get/set handlers, `gdb_cmd_binwrite()`, `gdb_cmd_detachkill()`, `gdb_cmd_reboot()`, `gdb_cmd_query()`, `gdb_cmd_task()`, `gdb_cmd_thread()`, `gdb_cmd_break()`, and `gdb_cmd_exception_pass()`. Public entry points are `gdb_serial_stub()`, `gdbstub_state()`, and `gdbstub_exit()`.

## Control flow
`gdb_serial_stub()` initializes selected-thread state, optionally sends a `T` stop reply when already connected, then loops reading `$packet#checksum` frames with `get_packet()`. It dispatches by first packet character, fills `remcom_out_buffer`, and sends a reply with `put_packet()` unless a continue/detach/kill path exits to the KGDB core. Unsupported or arch-specific commands fall through to `kgdb_arch_handle_exception()`.

Memory and register commands use nofault kernel copy helpers and arch register accessors. Breakpoint packets call KGDB software breakpoint APIs for type 0 or architecture hardware breakpoint hooks for supported types. Thread packets map idle CPU contexts to negative shadow PIDs and normal tasks to init PID namespace PIDs. Query packets enumerate CPUs and tasks in batches, return current thread, provide thread extra info, pass `qRcmd` payloads into KDB when configured, and delegate architecture qXfer features when available.

`gdbstub_state()` lets KDB transition commands feed commands back into the GDB stub, including saved packet replay. `gdbstub_exit()` sends a minimal `Wxx` exit packet during reboot if connected and in GDB mode.

## State and persistence behavior
State is session-scoped and static in the kernel. `kgdb_connected`, `kgdb_usethread`, `kgdb_contthread`, per-session fields in `kgdb_state`, replay-buffer counters, and selected register images are mutated. Memory write packets can modify arbitrary kernel memory and flush icache where safe. No filesystem persistence exists, but writes and breakpoints can permanently affect the running kernel until reboot or repair.

## Dependencies and integration points
The stub depends on KGDB I/O operations, debug core state, KDB polling and parser hooks when enabled, architecture register definitions and exception handlers, nofault kernel memory access, PID/task iteration, init PID namespace, emergency reboot, cache flushing, and optional architecture qXfer packet support.

## Risks and edge cases
The packet parser is intentionally simple and runs with the system stopped; malformed packets are retried by checksum NAKs. Memory/register write commands are powerful and are blocked only by higher-level KGDB lockdown logic in the core. Buffer sizes limit packet payloads; `kgdb_mem2hex()` uses the upper half of the output buffer as a raw-copy staging area, so callers must keep requested lengths within protocol buffer assumptions. Thread enumeration races are mitigated by KGDB stopping CPUs and using RCU-friendly PID lookup, but sleeping tasks only expose switch-saved register state. Detach/kill remove all breakpoints and return to default arch handling.

## Test signals
Test with host GDB attach/status, register read/write, memory read/write hex and binary forms, software and hardware breakpoint set/remove, continue, single-step, detach, kill, emergency reboot packet `R0`, thread list batching, CPU shadow thread access, thread extra info, qRcmd KDB commands, unsupported packet fallback, checksum retry behavior, console `O` packets, and reboot `Wxx` exit notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/gdbstub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/Makefile -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/Makefile

## Purpose
This Makefile builds the KDB frontend objects and generates `gen-kdb_cmds.c` from the textual `kdb_cmds` file. It is used when the parent debugger Makefile descends into `kernel/debug/kdb/`.

## Important APIs, types, and functions
There are no runtime APIs. Build objects are `kdb_io.o`, `kdb_main.o`, `kdb_support.o`, `kdb_bt.o`, `gen-kdb_cmds.o`, `kdb_bp.o`, and `kdb_debugger.o`, with optional `kdb_keyboard.o` under `CONFIG_KDB_KEYBOARD`. `clean-files := gen-kdb_cmds.c` marks the generated source for cleanup.

The `cmd_gen-kdb` AWK rule emits C strings from non-comment, non-empty `kdb_cmds` lines and builds an `__initdata` `kdb_cmds[]` array.

## Control flow
Kbuild compiles the listed KDB objects. When `gen-kdb_cmds.c` is needed, the rule reads `$(src)/kdb_cmds` and the Makefile, escapes quotes, emits one static string per command line, and emits a NULL-terminated `kdb_cmds` pointer array.

## State and persistence behavior
The only persistent artifact is generated build output `gen-kdb_cmds.c`, which is cleaned by Kbuild. The Makefile has no runtime state.

## Dependencies and integration points
It depends on Kbuild, AWK, `kdb_cmds`, KDB source files, and `CONFIG_KDB_KEYBOARD`. The generated command table is consumed by KDB initialization.

## Risks and edge cases
The AWK generator skips comments and blank lines and escapes quotes; malformed command lines in `kdb_cmds` become embedded strings and may fail later at KDB parse time. Missing AWK or stale generated output would break KDB builds. The dependency includes the Makefile itself so generator changes rebuild the source.

## Test signals
Build KDB with and without keyboard support, inspect regenerated `gen-kdb_cmds.c`, run clean targets, and boot KDB to verify built-in commands from `kdb_cmds` are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bp.c -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bp.c

## Purpose
`kdb_bp.c` implements KDB breakpoint and single-step commands. It maintains the KDB breakpoint table, parses `bp`/`bph` commands, installs/removes breakpoints through KGDB core and architecture hardware-breakpoint hooks, and registers `bp`, `bl`, `bc`, `be`, `bd`, `ss`, and optional `bph` commands.

## Important APIs, types, and functions
Global state is `kdb_breakpoints[KDB_MAXBPT]`, an array of `kdb_bp_t`. Important helpers include `kdb_setsinglestep()`, `kdb_bptype()`, `kdb_parsebp()`, `_kdb_bp_remove()`, `kdb_handle_bp()`, `_kdb_bp_install()`, `kdb_bp_install()`, `kdb_bp_remove()`, `kdb_printbp()`, command handler `kdb_bp()`, command handler `kdb_bc()`, command handler `kdb_ss()`, and initializer `kdb_initbptab()`.

## Control flow
`kdb_initbptab()` clears the breakpoint table, marks all entries free, registers core breakpoint commands, and registers `bph` only if architecture KGDB ops advertise hardware breakpoint support. `kdb_bp()` with no arguments lists active entries. With an address, it parses the symbol/address, validates software breakpoint ability immediately, allocates a free table slot, parses hardware type and length for `bph`, rejects duplicate addresses, enables the entry, and prints it.

`kdb_bp_install()` runs before leaving KDB and installs enabled breakpoints. Software breakpoints call `dbg_set_sw_break()`, while hardware breakpoints call `arch_kgdb_ops.set_hw_breakpoint()`. Delayed breakpoints and single-step state are handled by setting KDB single-step flags and marking the breakpoint delayed. `kdb_bp_remove()` runs on debugger entry in reverse order and removes installed breakpoints through KGDB or arch hooks.

`kdb_bc()` implements clear, enable, and disable for a breakpoint number, address, or `*`. Clearing marks entries free; disabling leaves them allocated but inactive. `kdb_ss()` sets KDB single-step state and returns `KDB_CMD_SS`.

## State and persistence behavior
State persists only during the running kernel debugger session in `kdb_breakpoints` and KDB state flags such as `DOING_SS` and `SSBPT`. Active software breakpoints are also reflected in the KGDB core breakpoint table and temporarily modify kernel text when activated. No filesystem state is written.

## Dependencies and integration points
The file depends on KDB command registration/parsing helpers, KGDB software breakpoint APIs, `arch_kgdb_ops` hardware breakpoint support, KDB state macros, symbol printing, SMP/scheduling context, and architecture instruction-pointer access.

## Risks and edge cases
Breakpoint installation can fail when kernel text is read-only or blocked, and the user-facing message suggests `rodata=off` or hardware breakpoints. Duplicate detection is address-only, so it disallows separate read/write hardware breakpoints on the same address. Delayed breakpoint handling around single-step is subtle and depends on KDB state flags. Hardware length is limited to 8 bytes. Breakpoints in KDB internals are intentionally delayed until leaving the debugger, but mistakes can trigger recursive debugger entry.

## Test signals
Exercise listing with no breakpoints, setting software `bp`, setting hardware `bph inst`, `datar`, and `dataw` with lengths, duplicate-address rejection, table-full behavior, invalid addresses, `bc`, `bd`, `be` by number/address/star, delayed breakpoints with single-step, install/remove ordering, unsupported hardware breakpoint builds, and rodata-protected software breakpoint failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bt.c -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bt.c

## Purpose
`kdb_bt.c` implements KDB stack traceback commands: current task backtrace, task-by-pid backtrace, task-struct-address backtrace, all-task backtrace, and current-task-on-CPU backtrace.

## Important APIs, types, and functions
Functions include `kdb_show_stack()`, `kdb_bt1()`, `kdb_bt_cpu()`, and command handler `kdb_bt()`. It uses KDB helpers `kdb_task_has_cpu()`, `kdb_process_cpu()`, `KDB_TSK()`, `kdb_task_state()`, `kdb_ps1()`, `kdb_getarea()`, `kdb_getchar()`, `kdbgetintenv()`, `kdbgetenv()`, `kdbgetularg()`, `kdbgetaddrarg()`, and `kdb_parse()`.

## Control flow
`kdb_show_stack()` increments `kdb_trap_printk`, then either asks the stopped CPU to dump its own stack via `kdb_dump_stack_on_cpu()` when the task is actively running and no alternate stack address is supplied, or calls `show_stack()` for the target task/address. It temporarily raises console loglevel for remote CPU self-dumps.

`kdb_bt()` dispatches by command name. `bta` walks online current tasks first, then all non-current process threads, filtering by a task-state mask from the argument or `PS` environment and optionally prompting between tasks based on `BTAPROMPT`. `btp` finds a task by PID in the init PID namespace. `btt` treats the argument as a `struct task_struct *`. `btc` dumps one CPU's current task or, with no CPU argument, prints CPU status via recursive `kdb_parse("cpu\n")` and then dumps every online CPU. Plain `bt` dumps the current KDB task or uses an address expression as an alternate stack location.

## State and persistence behavior
The command mutates transient KDB output state: `kdb_trap_printk`, pager line tracking, console loglevel during CPU stack dumps, and watchdog touch timing. It does not persist data or change debug breakpoints.

## Dependencies and integration points
It integrates with KGDB/KDB CPU roundup state through `kdb_dump_stack_on_cpu()`, scheduler task iteration, init PID namespace task lookup, stack unwinder `show_stack()`, KDB process display helpers, KDB environment variables, console logging, and NMI watchdog touch logic.

## Risks and edge cases
Backtracing a running task on another CPU is architecture-sensitive, so this file asks stopped slave CPUs to dump themselves when possible. If a CPU failed to stop in the debugger or lacks a recorded task, `btc` prints warnings. `btt` trusts an arbitrary address after only `kdb_getarea()` checks in `kdb_bt1()`. `bta` can produce very large output and uses prompting plus interrupt flag checks to stop. Recursive `kdb_parse()` means `btc` must discard `argv` afterward.

## Test signals
Test current `bt`, alternate-stack `bt <addr>`, `btp <pid>`, `btt <task_addr>`, `bta` with default and explicit masks, prompt quit/continue behavior, `btc` for one CPU and all CPUs, CPUs that are offline or not rounded up, KDB interrupt during all-task traversal, and systems with/without reliable frame pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bt.c -->
