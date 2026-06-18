# Research: subset-b-006041

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/hibernate.c -->
# sources/distributed-fs/ceph-client/kernel/power/hibernate.c

## Purpose
Implements the kernel hibernation coordinator: validating whether hibernation is available, creating a suspend-to-disk image, writing it through the swsusp backend, powering the machine down, and restoring a saved image during boot or explicit resume. It is the policy/control layer above `snapshot.c` memory-image construction and `swap.c` image storage.

## Important APIs, Types, and Functions
Global state includes `swsusp_resume_device`, `swsusp_resume_block`, `in_suspend`, `hib_comp_algo`, `freezer_test_done`, `hibernation_mode`, `hibernation_ops`, and `hibernate_atomic`. `hibernate_acquire()`/`hibernate_release()` serialize hibernation and `/dev/snapshot` ownership. `hibernation_available()` gates hibernation on command-line disablement, lockdown, secretmem, and CXL memory state.

Primary entry points are `hibernate()`, `software_resume()`, `hibernation_snapshot()`, `hibernation_restore()`, `hibernation_platform_enter()`, `hibernation_set_ops()`, `pm_hibernation_mode_is_suspend()`, `system_entering_hibernation()`, and exported `hibernate_quiet_exec()`. Sysfs handlers implement `/sys/power/disk`, `resume`, `resume_offset`, `image_size`, and `reserved_size`; boot parameters include `resume=`, `resume_offset=`, `hibernate=`, `noresume`, `resumewait`, `resumedelay=`, and `nohibernate`. The `compressor` module parameter selects LZO or LZ4, validated through the crypto acomp API.

## Control Flow
`hibernate()` first checks availability and compression support, locks `system_transition_mutex` via `lock_system_sleep()`, acquires the hibernation token, prepares the console, calls robust PM notifiers, syncs filesystems, optionally freezes filesystems, freezes user tasks, locks device hotplug, creates memory bitmaps, and calls `hibernation_snapshot()`.

`hibernation_snapshot()` begins platform mode if requested, preallocates image memory, freezes kernel threads, prepares devices, reclaims shmem pages, suspends consoles, restricts GFP I/O and filesystem allocation flags, suspends devices, and then calls `create_image()`. `create_image()` runs late/noirq device freeze, platform pre-snapshot, CPU disable, IRQ disable, syscore suspend, processor-state save, and `swsusp_arch_suspend()`. After the architecture snapshot returns, it resumes syscore, IRQs, CPUs, platform, and devices with `PMSG_THAW`, `PMSG_RECOVER`, or `PMSG_RESTORE` depending on whether execution is still in the image kernel or has returned after restore.

If `in_suspend` remains true, `hibernate()` builds swsusp flags for platform mode, no-compress mode, CRC/compression algorithm, writes the image with `swsusp_write()`, and either performs `test_resume` or calls `power_down()`. `power_down()` enters suspend mode, platform hibernation, poweroff, reboot, or halt based on `/sys/power/disk`; it restores the swap signature through `swsusp_unmark()` only when a wakeup event rolls back the transition.

Resume is handled by late initcall `software_resume_initcall()`: it resolves the resume device, calls `swsusp_check()`, validates compression support from header flags, freezes processes and kernel threads, reads the image via `load_image_and_restore()`, and jumps into the restored kernel through `hibernation_restore()` and `resume_target_kernel()`. Restore uses DPM quiesce callbacks, platform pre-restore, CPU disable, syscore suspend, highmem restore, and `swsusp_arch_resume()`.

## State and Persistence
Persistent user-visible state is held in sysfs tunables and boot parameters. Persistent on-disk state is delegated to `swap.c`, but this file chooses flags encoded in the image header. `hibernate_atomic` prevents concurrent hibernation or snapshot-device access. `in_suspend` is `__nosavedata` and distinguishes the image kernel after snapshot creation from execution after a successful restore. `entering_platform_hibernation` tells platform code and poweroff paths that firmware hibernation is underway. `hibernation_mode` persists until changed through `/sys/power/disk`.

## Dependencies and Integration Points
The file integrates with DPM (`dpm_prepare`, `dpm_suspend`, `dpm_suspend_end`, resume phases), freezer/OOM/usermode-helper code, filesystem freeze/thaw, console suspend, CPU hotplug, syscore ops, architecture swsusp hooks, PM notifiers, crypto compression, block-device lookup, security lockdown, secretmem/CXL guards, wakeup-event accounting, and platform hibernation ops. It is invoked from `/sys/power/state`, `/sys/power/disk`, boot resume initcalls, `/dev/snapshot`, and exported PM APIs.

## Risks
The highest risks are ordering regressions across freezer, device, CPU, IRQ, and syscore phases; missing cleanup on error paths; image/swap signature corruption if `power_down()` returns unexpectedly; races with wakeup events; compression algorithm/header mismatches; holding `system_transition_mutex` around paths that may wait for device discovery; and platform callbacks that do not implement the full required hibernation contract. Resume is especially sensitive because a partially restored image can leave devices, highmem, or filesystems inconsistent.

## Test Signals
Exercise `/sys/power/state` with `disk`, `/sys/power/disk` modes `shutdown`, `reboot`, `platform`, `suspend`, and `test_resume`; boot with `resume=`, `resume_offset=`, `resumewait`, `resumedelay=`, `hibernate=noresume`, `hibernate=nocompress`, and `nohibernate`; validate LZO/LZ4 compressor selection; run PM test levels through `/sys/power/pm_test`; inject DPM, freezer, swap, and wakeup-count failures; verify lockdown/secretmem/CXL disable paths; and confirm resume leaves swap signatures, suspend statistics, notifier events, and filesystem state consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/main.c -->
# sources/distributed-fs/ceph-client/kernel/power/main.c

## Purpose
Provides the PM subsystem core sysfs/debugfs surface and shared helpers used by suspend and hibernation. It owns `/sys/power`, common sleep-state dispatch, wakeup-count handshake, PM notifiers, suspend statistics, PM workqueues, debug toggles, and filesystem sync helpers.

## Important APIs, Types, and Functions
Exported helpers include `lock_system_sleep()`, `unlock_system_sleep()`, `ksys_sync_helper()`, `register_pm_notifier()`, `unregister_pm_notifier()`, `pm_notifier_call_chain_robust()`, `pm_notifier_call_chain()`, `pm_report_hw_sleep_time()`, `pm_report_max_hw_sleep()`, `pm_sleep_transition_in_progress()`, `pm_debug_messages_should_print()`, and exported workqueue `pm_wq`.

State includes `saved_gfp_count`, `saved_gfp_mask`, `pm_fs_sync_count`, `pm_fs_sync_wq`, `pm_chain_head`, `pm_async_enabled`, `sync_on_suspend_enabled`, `pm_test_level`, `suspend_stats`, `pm_print_times_enabled`, `pm_debug_messages_on`, `power_kobj`, `filesystem_freeze_enabled`, and the PM kobjects/attribute groups. `struct suspend_stats` records success/fail counts, per-step failures, recent failed devices/errno/steps, and hardware sleep time.

Sysfs attributes include `state`, `pm_async`, `mem_sleep`, `sync_on_suspend`, `pm_test`, `wakeup_count`, `autosleep`, `wake_lock`, `wake_unlock`, `pm_trace`, `pm_trace_dev_match`, `pm_freeze_timeout`, `freeze_filesystems`, `pm_print_times`, `pm_wakeup_irq`, `pm_debug_messages`, and `suspend_stats/*`.

## Control Flow
`pm_init()` is a core initcall that allocates `pm_wq` and `pm_fs_sync_wq`, initializes hibernation image/reserved sizes, initializes suspend state labels, creates `/sys/power`, installs attribute groups, initializes PM debug timing, and initializes autosleep.

Writing `/sys/power/state` enters `state_store()`: it locks autosleep, rejects manual writes while autosleep is active, decodes labels, maps `mem` to `mem_sleep_current`, and dispatches to `pm_suspend()` or `hibernate()`. Writing `/sys/power/mem_sleep` updates the selected `mem` implementation when autosleep is not active. Writing `/sys/power/wakeup_count` implements the race-free wakeup-event protocol by saving the observed wakeup count or printing active wakeup sources.

`pm_sleep_fs_sync()` runs `ksys_sync()` on an ordered workqueue and waits in short intervals so wakeup events can abort a suspend or hibernate attempt with `-EBUSY`. `pm_restrict_gfp_mask()` and `pm_restore_gfp_mask()` maintain a nesting count while clearing `__GFP_IO` and `__GFP_FS` under `system_transition_mutex`, preventing allocations that require I/O while devices are suspended.

Suspend statistics are updated by DPM and suspend paths through `dpm_save_failed_dev()`, `dpm_save_failed_step()`, and `dpm_save_errno()`. Sysfs and debugfs readers expose the current ring-buffered failure details.

## State and Persistence
Most state is runtime-only kernel state exposed through sysfs/debugfs. Sysfs writes persist only until reboot unless boot parameters set defaults. `pm_async_enabled`, `sync_on_suspend_enabled`, `pm_test_level`, `freeze_timeout_msecs`, and `filesystem_freeze_enabled` directly affect later suspend/hibernate behavior. `suspend_stats` persists in memory across multiple transitions and is observable under `/sys/power/suspend_stats` and debugfs.

## Dependencies and Integration Points
This file binds the PM core to sysfs/kobject infrastructure, debugfs/seq_file, workqueues, system calls (`ksys_sync`), wakeup-source accounting, autosleep, wakelocks, PM trace, ACPI low-power S0 reporting, freezer timeout configuration, PM notifier chains, hibernation, and suspend. It is the public user-space control plane for the rest of `kernel/power`.

## Risks
Risks include incorrect serialization around `system_transition_mutex`, wakeup-count races causing lost wakeups or unnecessary suspend failures, failure to restore `gfp_allowed_mask`, sysfs stores accepting invalid states while autosleep is active, statistics updates without sufficient locking for all fields, and initialization ordering problems because later hibernation/suspend files add sysfs groups under `power_kobj`.

## Test Signals
Check `/sys/power/state`, `mem_sleep`, `wakeup_count`, `autosleep`, `pm_async`, `sync_on_suspend`, `pm_test`, `freeze_filesystems`, and debug attributes under supported configs. Race tests should read/write `wakeup_count` while generating wakeup events, toggle autosleep while writing state attributes, inject filesystem sync wakeups, verify suspend-stat counters after failed DPM steps, and boot with `pm_async=off` or `pm_debug_messages`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/power.h -->
# sources/distributed-fs/ceph-client/kernel/power/power.h

## Purpose
Defines the private interface shared by the kernel power-management implementation files. It centralizes hibernation image metadata, snapshot streaming contracts, sysfs attribute helpers, suspend/hibernate cross-file prototypes, test-level constants, and config-dependent stubs.

## Important APIs, Types, and Functions
`struct swsusp_info` is the page-aligned image header payload containing UTS data, kernel version, physical page count, CPU count, image page counts, and total image size. `struct snapshot_handle` abstracts streaming hibernation images page by page through `snapshot_read_next()` and `snapshot_write_next()`; callers use `data_of(handle)` to access the current buffer and `sync_read` to detect buffers that require synchronous reads.

Macros `power_attr()` and `power_attr_ro()` define common `/sys/power` kobj attributes. Hibernation flag definitions include `SF_PLATFORM_MODE`, `SF_NOCOMPRESS_MODE`, `SF_CRC32_MODE`, `SF_HW_SIG`, and compression algorithm selector `SF_COMPRESSION_ALG_LZ4` with dummy LZO value. PM test constants range from `TEST_NONE` through `TEST_FREEZER`.

The header declares shared variables such as `image_size`, `reserved_size`, `in_suspend`, `swsusp_resume_device`, `swsusp_resume_block`, `swsusp_header_flags`, `pm_labels`, `pm_states`, `mem_sleep_states`, `pm_test_level`, and `hib_comp_algo`. It declares cross-file entry points for memory bitmaps, hibernation preallocation, snapshot streaming, swap I/O, suspend entry, notifier chains, autosleep, wakelocks, CPU disable/enable wrappers, and DPM error recording.

## Control Flow
This file has no runtime control flow beyond small inline wrappers. It controls compile-time flow through `CONFIG_HIBERNATION`, `CONFIG_SUSPEND`, `CONFIG_PM_SLEEP`, `CONFIG_PM_AUTOSLEEP`, `CONFIG_HIGHMEM`, `CONFIG_ARCH_HIBERNATION_HEADER`, and `CONFIG_STRICT_KERNEL_RWX`. When features are disabled, callers get no-op stubs or default values to keep common code buildable.

## State and Persistence Behavior
The header itself owns no storage except through external declarations. Its definitions shape persistent hibernation image format (`struct swsusp_info` and `SF_*` flags) and user-visible sysfs ABI naming via `power_attr`. Changes to this file can affect image compatibility between the hibernating kernel and boot kernel.

## Dependencies and Integration Points
It includes suspend ioctls, UTS names, freezer, CPU, cpuidle, crypto, and compiler headers. It links `hibernate.c`, `snapshot.c`, `swap.c`, `suspend.c`, `main.c`, `user.c`, `wakelock.c`, and platform/architecture hibernation hooks. It also connects the `/dev/snapshot` UAPI to in-kernel snapshot streaming.

## Risks
Risks are ABI and contract drift: changing `struct swsusp_info`, flag semantics, snapshot streaming expectations, or config stubs can break resume, user-space suspend tools, and platform ports. The comment typo "hibernatig hernel" is harmless, but the surrounding flag documentation is important because `hibernate.c` and `swap.c` must agree exactly on compression and CRC behavior.

## Test Signals
Build matrix coverage is important: hibernation on/off, suspend on/off, highmem on/off, autosleep/wakelocks on/off, strict RWX image protection, and architecture hibernation headers. Runtime signals include successful image save/read across compression modes and `/dev/snapshot` ioctl compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/poweroff.c -->
# sources/distributed-fs/ceph-client/kernel/power/poweroff.c

## Purpose
Registers the SysRq `o` handler that requests a graceful kernel poweroff. It is a small bridge from emergency keyboard/sysrq handling into the normal reboot/power-management poweroff path.

## Important APIs, Types, and Functions
`do_poweroff()` is a workqueue callback that calls `kernel_power_off()`. `handle_poweroff()` schedules that work on the first online CPU with `schedule_work_on(cpumask_first(cpu_online_mask), &poweroff_work)`. `sysrq_poweroff_op` describes the SysRq key operation, help text, action text, and `SYSRQ_ENABLE_BOOT` enable mask. `pm_sysrq_init()` registers key `o` with `register_sysrq_key()` as a `subsys_initcall`.

## Control Flow
When SysRq `o` is triggered, the sysrq layer calls `handle_poweroff()`. The handler does not power off directly from sysrq context; it schedules `poweroff_work` on the boot/first online CPU. The workqueue callback then invokes `kernel_power_off()`, allowing the existing kernel poweroff path to run in process context.

## State and Persistence Behavior
The only state is the statically declared work item and key operation. There is no persistent configuration or sysfs state. Registration lasts for the boot lifetime once the initcall succeeds.

## Dependencies and Integration Points
The file depends on sysrq, reboot/poweroff, workqueue, CPU mask, and initcall infrastructure. It integrates with the global sysrq key registry and the generic `kernel_power_off()` path, including architecture and platform poweroff handlers.

## Risks
Risks are limited but include scheduling on an invalid CPU mask if called during severe CPU-hotplug failure, assuming workqueue execution is still possible during an emergency, and interactions with platform poweroff handlers that may sleep or fail. Because it uses `SYSRQ_ENABLE_BOOT`, policy around sysrq enable masks controls exposure.

## Test Signals
Enable sysrq and issue SysRq `o` on a test machine or VM, then verify `kernel_power_off()` is reached and no direct sysrq-context sleeping occurs. Build coverage should include sysrq-enabled kernels and CPU hotplug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/process.c -->
# sources/distributed-fs/ceph-client/kernel/power/process.c

## Purpose
Implements task and workqueue freezing/thawing for suspend and hibernation transitions. It stops user tasks, freezable kernel threads, and freezable workqueues so memory images and low-power transitions happen from a quiescent task state.

## Important APIs, Types, and Functions
Global `freeze_timeout_msecs` defaults to 20 seconds and is exposed through `/sys/power/pm_freeze_timeout` in `main.c`. `try_to_freeze_tasks(bool user_only)` is the core loop. Public entry points are `freeze_processes()`, `freeze_kernel_threads()`, `thaw_processes()`, and `thaw_kernel_threads()`.

The implementation uses `pm_freezing`, `pm_nosig_freezing`, the `freezer_active` static key, `PF_SUSPEND_TASK`, `__usermodehelper_disable()`, `__usermodehelper_set_disable_depth()`, `usermodehelper_enable()`, `oom_killer_disable()`, `oom_killer_enable()`, `freeze_task()`, `frozen()`, `freezing()`, freezable workqueue helpers, and tracepoint `trace_suspend_resume()`.

## Control Flow
`freeze_processes()` disables usermode helpers in freezing mode, marks the current task as `PF_SUSPEND_TASK`, activates the freezer static key, clears wakeup state, sets `pm_freezing`, and calls `try_to_freeze_tasks(true)`. On success it fully disables usermode helpers and disables the OOM killer with the same timeout budget. On failure it thaws all processes.

`freeze_kernel_threads()` sets `pm_nosig_freezing` and calls `try_to_freeze_tasks(false)`, which additionally begins and polls freezable workqueue freezing. Failure thaws only kernel threads/workqueues, leaving user-space thawing to the caller.

`try_to_freeze_tasks()` repeatedly walks all process threads under `tasklist_lock`, calls `freeze_task()`, counts tasks still needing the refrigerator, adds workqueue busy state, backs off sleeps from 1 ms to 8 ms, and aborts on timeout or `pm_wakeup_pending()`. It prints refusing tasks and freezable workqueues when debugging or non-wakeup failure occurs.

`thaw_processes()` disables freezer state, re-enables the OOM killer and usermode helpers, thaws workqueues and all tasks, clears `PF_SUSPEND_TASK` on the current task, schedules once, and emits trace/log messages. `thaw_kernel_threads()` clears kernel-thread freezing and thaws only `PF_KTHREAD` tasks plus workqueues.

## State and Persistence Behavior
Freezer state is transient but globally visible while a transition is active. `PF_SUSPEND_TASK` prevents the initiating task from freezing itself. Usermode-helper disable depth and OOM killer state must be restored on every error path. No persistent on-disk state is created.

## Dependencies and Integration Points
This file integrates with the scheduler, freezer subsystem, workqueues, usermode helper infrastructure, OOM killer, wakeup-source detection, tracepoints, and suspend/hibernate orchestration. `suspend.c`, `hibernate.c`, and `user.c` rely on these calls for both normal kernel-driven transitions and `/dev/snapshot` flows.

## Risks
Risks include deadlocks from tasks refusing to freeze, freezer state leaks after partial failure, OOM killer left disabled, usermode helpers left at the wrong depth, wakeup events aborting without enough diagnostic signal, and workqueue freezing regressions. The task walk runs under `tasklist_lock`, so changes must avoid sleeping while holding it.

## Test Signals
Use `/sys/power/pm_test=freezer`, hibernation freezer tests, deliberate non-freezable tasks, freezable workqueue workloads, wakeup-event injection during freezing, OOM-victim scenarios, and usermode-helper activity during suspend. Verify thaw paths restore usermode helpers, OOM killer, workqueues, and `PF_SUSPEND_TASK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/qos.c -->
# sources/distributed-fs/ceph-client/kernel/power/qos.c

## Purpose
Implements the base Power Management Quality of Service aggregation engine plus global CPU latency QoS and frequency QoS helpers. It lets kernel and user-space clients submit constraints that are aggregated into effective latency or frequency limits and optionally reported through notifiers.

## Important APIs, Types, and Functions
Core helpers are `pm_qos_read_value()`, `pm_qos_update_target()`, and `pm_qos_update_flags()`. A global `pm_qos_lock` protects constraint lists, flags lists, and notifier updates. PM QoS constraints use `struct pm_qos_constraints`, `plist_head`, `plist_node`, and action enum values `PM_QOS_ADD_REQ`, `PM_QOS_UPDATE_REQ`, and `PM_QOS_REMOVE_REQ`. Constraint type `PM_QOS_MIN` chooses the lowest priority value; `PM_QOS_MAX` chooses the highest.

When `CONFIG_CPU_IDLE` is enabled, CPU latency APIs include `cpu_latency_qos_limit()`, `cpu_latency_qos_request_active()`, `cpu_latency_qos_add_request()`, `cpu_latency_qos_update_request()`, and `cpu_latency_qos_remove_request()`. User space accesses the same aggregate through `/dev/cpu_dma_latency`. Optional `CONFIG_PM_QOS_CPU_SYSTEM_WAKEUP` adds `/dev/cpu_wakeup_latency` and `cpu_wakeup_latency_qos_limit()`.

Frequency QoS APIs include `freq_constraints_init()`, `freq_qos_read_value()`, `freq_qos_apply()`, `freq_qos_add_request()`, `freq_qos_update_request()`, `freq_qos_remove_request()`, `freq_qos_add_notifier()`, and `freq_qos_remove_notifier()`.

## Control Flow
`pm_qos_update_target()` takes the spinlock, computes the previous aggregate, normalizes default values, mutates the plist according to add/update/remove, computes and stores the new aggregate with `WRITE_ONCE`, drops the lock, emits a tracepoint, and notifies subscribers if the aggregate changed. `pm_qos_update_flags()` performs the same pattern for OR-aggregated flags.

CPU latency request operations validate handles and values, attach the request to `cpu_latency_constraints`, update the aggregate, and wake all idle CPUs if the effective latency changes. The misc-device open path allocates a request with default value; write accepts either a binary `s32` or text value and updates the request; release removes and frees it.

Frequency QoS initializes independent min and max constraint lists with opposite aggregation directions: min frequency uses `PM_QOS_MAX`, and max frequency uses `PM_QOS_MIN`. Add/update/remove operations validate active handles and then delegate to `pm_qos_update_target()`.

## State and Persistence Behavior
QoS requests are runtime constraints associated with kernel-owned request objects or open misc-device file descriptors. Closing `/dev/cpu_dma_latency` or `/dev/cpu_wakeup_latency` removes that request. Effective values are held in `target_value` and observed locklessly via `READ_ONCE`. No state persists across reboot.

## Dependencies and Integration Points
The file depends on plist, spinlocks, blocking notifiers, misc devices, user-copy helpers, debug/trace infrastructure, CPU idle wakeups, and cpufreq-style frequency constraints. CPU idle governors, cpufreq drivers, device PM, and user-space latency-sensitive applications consume these limits.

## Risks
Risks include callers updating inactive request objects, invalid negative constraints, missed notifier transitions, lock ordering with notifier callbacks, user-space ABI compatibility for binary vs text writes, and stale requests if file release paths fail. Because one global spinlock protects all PM QoS lists, expensive work must remain outside the critical section.

## Test Signals
Exercise kernel add/update/remove APIs, duplicate add/remove warnings, notifier callbacks, `/dev/cpu_dma_latency` binary and text writes, close cleanup, optional `/dev/cpu_wakeup_latency`, cpufreq min/max constraints, and tracepoints. Runtime validation should confirm idle CPUs wake when CPU latency limits tighten.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/snapshot.c -->
# sources/distributed-fs/ceph-client/kernel/power/snapshot.c

## Purpose
Builds, streams, loads, and restores the in-memory hibernation image used by swsusp. It tracks which physical pages must be saved, copies saveable memory into image pages, serializes image metadata as PFN bitmaps, allocates safe restore memory, and performs final page restoration support including highmem handling.

## Important APIs, Types, and Functions
Public/shared entry points include `hibernate_reserved_size_init()`, `hibernate_image_size_init()`, `get_safe_page()`, `register_nosave_region()`, `swsusp_set_page_free()`, `swsusp_unset_page_free()`, `swsusp_page_is_forbidden()`, `create_basic_memory_bitmaps()`, `free_basic_memory_bitmaps()`, `clear_or_poison_free_pages()`, `snapshot_additional_pages()`, `hibernate_preallocate_memory()`, `swsusp_save()`, `snapshot_get_image_size()`, `snapshot_read_next()`, `snapshot_write_next()`, `snapshot_write_finalize()`, `snapshot_image_loaded()`, and `restore_highmem()`.

Key types are `struct pbe`, `struct linked_page`, `struct chain_allocator`, `struct memory_bitmap`, `struct mem_zone_bm_rtree`, `struct rtree_node`, `struct bm_position`, `struct nosave_region`, and highmem-only `struct highmem_pbe`. Global image state includes `restore_pblist`, `safe_pages_list`, `buffer`, `allocated_unsafe_pages`, `forbidden_pages_map`, `free_pages_map`, `orig_bm`, `copy_bm`, `zero_bm`, `nr_copy_pages`, `nr_meta_pages`, `nr_zero_pages`, `alloc_normal`, and `alloc_highmem`.

## Control Flow
Before hibernation, `create_basic_memory_bitmaps()` creates two memory bitmaps and marks nosave ranges. `hibernate_preallocate_memory()` creates `orig_bm`, `copy_bm`, and `zero_bm`, marks free pages, counts saveable data/highmem pages, estimates metadata overhead and minimum image size, preallocates image pages under `image_size` and `reserved_size` constraints, and frees unnecessary pages.

During the architecture snapshot, `swsusp_save()` computes available normal/highmem pages, calls `swsusp_alloc()` to allocate copy pages, then `copy_data_pages()` copies saveable pages into allocated image pages while marking original PFNs, copy PFNs, and zero pages. The image is later streamed out through `snapshot_read_next()`: first a `struct swsusp_info` header, then metadata pages packed by `pack_pfns()`, then copied data pages.

During resume, `snapshot_write_next()` receives that stream. It loads and validates the header, builds copy and zero bitmaps from metadata pages, calls `prepare_image()` to mark unsafe original PFNs and allocate safe restore storage, then returns buffers where the caller should place each image page. It skips zero pages by clearing them directly. `snapshot_write_finalize()` drains trailing zero pages, copies pending highmem data, protects restored pages when strict RWX protection is enabled, and recycles bitmap memory.

For final atomic restore, `restore_highmem()` swaps highmem copy pages back to original pages when the direct restore path cannot overwrite them immediately. Lowmem final restore is completed by architecture code using `restore_pblist`.

## State and Persistence Behavior
All state is runtime memory used for one hibernation/resume attempt. The serialized image format is persistent while stored by `swap.c`: header, PFN metadata pages, and data pages. `register_nosave_region()` records boot-time PFN ranges that must not enter the image. `image_size` and `reserved_size` are initialized here but exposed through hibernation sysfs.

## Dependencies and Integration Points
This file depends on MM zones, memblock, highmem, page flags, direct-map/set_memory helpers, architecture hibernation headers, TLB/cache maintenance, debug pagealloc, freezer/suspend orchestration, and swap/user snapshot readers. It is the memory engine behind `hibernate.c`, `swap.c`, and `/dev/snapshot`.

## Risks
Risks are severe: bitmap off-by-one errors, PFN validation mistakes, unsafe-page allocation during restore, highmem copy-list corruption, image-size underestimation, failure to exclude nosave/free pages, missed cache/TLB maintenance, strict RWX protection not undone correctly on errors, and memory pressure deadlocks during atomic phases. Resume image loading must reject mismatched kernel/memory metadata to avoid corrupting the running kernel.

## Test Signals
Run hibernation on lowmem and highmem systems, with zero-heavy memory, memory hotplug-like layouts, strict RWX image protection, debug pagealloc, and constrained free memory. Validate `image_size` and `reserved_size` tuning, nosave-region registration, `/dev/snapshot` read/write streaming, CRC/compressed and uncompressed swap paths, and injected allocation failures around bitmap creation and safe-page allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/suspend.c -->
# sources/distributed-fs/ceph-client/kernel/power/suspend.c

## Purpose
Implements system suspend states: suspend-to-idle (`freeze`/s2idle), standby (`shallow`), and suspend-to-RAM (`mem`/`deep`). It registers platform suspend operations, exposes state labels, coordinates process freezing and device suspend phases, executes low-level platform entry, and resumes the system.

## Important APIs, Types, and Functions
Exported state includes `pm_labels`, `pm_states`, `mem_sleep_states`, `mem_sleep_current`, `mem_sleep_default`, `pm_suspend_target_state`, and `pm_suspend_global_flags`. Platform hooks are stored in `suspend_ops` and `s2idle_ops`. S2idle state uses `s2idle_state`, `s2idle_lock`, and `s2idle_wait_head`.

Important entry points are `pm_suspend_default_s2idle()`, `s2idle_set_ops()`, `s2idle_wake()`, `pm_states_init()`, `suspend_set_ops()`, `suspend_valid_only_mem()`, `suspend_devices_and_enter()`, and exported `pm_suspend()`. Weak architecture hooks are `arch_suspend_disable_irqs()` and `arch_suspend_enable_irqs()`.

## Control Flow
`pm_suspend()` validates the requested state, logs entry, calls `enter_state()`, records the result in suspend stats, and logs exit. `enter_state()` validates platform support, locks `system_transition_mutex`, initializes s2idle state if needed, optionally syncs filesystems, clears wakeup flags, runs `suspend_prepare()`, handles freezer test mode, and calls `suspend_devices_and_enter()`.

`suspend_prepare()` checks support, prepares the console, runs robust suspend notifiers, optionally freezes filesystems, and calls `suspend_freeze_processes()`. Failure records `SUSPEND_FREEZE`, thaws filesystems, posts notifiers, and restores the console.

`suspend_devices_and_enter()` sets the target state, begins platform suspend, suspends consoles, starts DPM suspend, and loops through `suspend_enter()` while platform `suspend_again()` requests another cycle. `suspend_enter()` runs platform prepare, late device suspend, s2idle-specific prepare, noirq device suspend, platform noirq prepare, and PM test checks. For s2idle it runs `s2idle_loop()` with devices suspended and CPUs idling until wake. For platform states it disables secondary CPUs, disables IRQs, sets `SYSTEM_SUSPEND`, suspends syscore, checks wakeups, calls `suspend_ops->enter()`, and unwinds syscore, IRQs, CPUs, platform, and DPM resume phases.

`s2idle_enter()` uses a raw spinlock to avoid losing wakeups between `pm_wakeup_pending()` and `s2idle_state` updates, wakes idle CPUs, and waits until `s2idle_wake()` transitions state to wake.

## State and Persistence Behavior
Suspend state is runtime-only. `mem_sleep_current` persists until changed by `/sys/power/mem_sleep` or boot `mem_sleep_default=`, influencing future `mem` requests. `pm_suspend_target_state` identifies the active transition to drivers. `pm_suspend_global_flags` can carry flags from platform/device code. Suspend statistics are updated in `main.c`.

## Dependencies and Integration Points
The file integrates with platform suspend ops, platform s2idle ops, DPM phases, syscore ops, CPU hotplug, cpuidle, console suspend, freezer/filesystem freeze, PM notifiers, wakeup sources, tracepoints, PM test/debug infrastructure, and `/sys/power/state`/`mem_sleep` dispatch from `main.c`.

## Risks
Risks include lost wakeups in s2idle, invalid platform callback ordering, not resuming devices after partial failures, IRQ state mismatches, CPU hotplug races, CXL memory restrictions for deep suspend, PM test modes unsupported for s2idle, and inconsistent `pm_suspend_target_state` cleanup. The nested unwind labels must preserve resume ordering after every failure point.

## Test Signals
Test `/sys/power/state` values `freeze`, `standby`, and `mem`; `/sys/power/mem_sleep` values `s2idle`, `shallow`, and `deep`; `mem_sleep_default=` boot parameter; PM test levels `freezer`, `devices`, `platform`, `processors`, and `core`; wakeup injection during late/noirq/syscore phases; platform `suspend_again()`; and failure injection in DPM/platform callbacks. Validate suspend_stats fields and tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/suspend_test.c -->
# sources/distributed-fs/ceph-client/kernel/power/suspend_test.c

## Purpose
Provides a boot-time suspend self-test facility driven by RTC wake alarms. It can automatically enter a requested suspend state shortly after boot and rely on a wakealarm-capable RTC to resume the system.

## Important APIs, Types, and Functions
`TEST_SUSPEND_SECONDS` defines the alarm delay. State includes `suspend_test_start_time`, `test_repeat_count_max`, `test_repeat_count_current`, and initdata `test_state_label`. Runtime timing helpers `suspend_test_start()` and `suspend_test_finish()` are called by `suspend.c` around device suspend/resume phases. Boot setup is handled by `setup_test_suspend()` registered through `__setup("test_suspend", ...)`. The late initcall `test_suspend()` locates an RTC and calls `test_wakealarm()`.

## Control Flow
`setup_test_suspend()` parses `test_suspend=<state>[,<repeat>]`, where state is one of the PM labels and repeat is an optional count. `test_suspend()` runs after PM and RTC initialization, validates that the requested state is currently exposed in `pm_states`, finds an RTC device with `RTC_FEATURE_ALARM` whose parent may wake the system, opens it, and calls `test_wakealarm()`.

`test_wakealarm()` reads current RTC time, sets a wake alarm `TEST_SUSPEND_SECONDS` in the future, then attempts the requested suspend state. If `mem` returns `-ENODEV`, it falls back to standby; if standby fails, it falls back to suspend-to-idle. It repeats until the configured count is reached, then disables the alarm.

`suspend_test_start()` records `jiffies`; `suspend_test_finish()` prints elapsed time for a labeled phase and warns if it exceeded the alarm window, because the wake alarm may have fired before the system fully entered sleep.

## State and Persistence Behavior
All state is boot-time or per-test runtime state. The RTC alarm is programmed in hardware and explicitly disabled after testing. The repeat counter persists only for the initcall execution.

## Dependencies and Integration Points
Depends on RTC class devices, wakealarm capability, PM state labels from `suspend.c`, `pm_suspend()`, and suspend device timing hooks in `suspend_devices_and_enter()`. It is controlled solely by the kernel command line.

## Risks
Risks include false failures on systems with uninitialized RTCs, RTCs that cannot wake the platform despite advertising alarms, races with long suspend entry taking longer than the alarm delay, fallback masking failures in the originally requested state, and reliance on `jiffies` instead of a suspend-resilient clock for timing diagnostics.

## Test Signals
Boot with `test_suspend=mem`, `test_suspend=standby`, `test_suspend=freeze`, and repeat forms such as `test_suspend=mem,3`. Validate behavior with and without wakealarm-capable RTCs, with RTC wake disabled, and on platforms where `mem` is unsupported. Watch logs for phase timing warnings and suspend failure codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/suspend_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/swap.c -->
# sources/distributed-fs/ceph-client/kernel/power/swap.c

## Purpose
Stores and retrieves hibernation images on swap-backed block devices. It manages swap-map metadata, hibernation signatures, asynchronous BIO I/O, optional compression/decompression, CRC validation, hardware signatures, and sysfs/boot controls for compression threading.

## Important APIs, Types, and Functions
Externally used entry points are `alloc_swapdev_block()`, `free_all_swap_pages()`, `swsusp_swap_in_use()`, `swsusp_write()`, `swsusp_read()`, `swsusp_check()`, `swsusp_close()`, and `swsusp_unmark()`. Global state includes `swsusp_hardware_signature`, `swsusp_header_flags`, `swsusp_header`, `swsusp_extents`, `root_swap`, `hib_resume_bdev_file`, `clean_pages_on_read`, and `clean_pages_on_decompress`.

Key structures are `struct swap_map_page`, `struct swap_map_page_list`, `struct swap_map_handle`, `struct swsusp_header`, `struct swsusp_extent`, `struct hib_bio_batch`, `struct crc_data`, `struct cmp_data`, and `struct dec_data`. Compression constants define 32-page uncompressed chunks, worst-case compressed size, default thread count, and read-buffer bounds.

## Control Flow
Saving starts in `swsusp_write()`: it obtains a swap writer, verifies enough swap for uncompressed mode, reads the snapshot header from `snapshot_read_next()`, writes it as the first image page, then calls either `save_image()` or `save_compressed_image()`. `swap_write_page()` allocates a swap slot, writes the page, appends the sector to the current swap-map page, and links map pages as needed. `swap_writer_finish()` writes the header signature through `mark_swapfiles()`, flushes the final map page, frees allocated slots on error, and closes the block device.

Compressed save starts compression kthreads plus one CRC32 kthread, batches pages from `snapshot_read_next()` into per-thread uncompressed buffers, compresses with `crypto_acomp`, writes a length header plus compressed payload pages, updates CRC over uncompressed bytes, and records compressed size.

Resume starts with `swsusp_check()`, which opens the resume block device, reads the swap header, looks for `HIBERNATE_SIG`, restores the original swap signature immediately, captures image flags, and validates optional hardware signature. `swsusp_read()` obtains the swap-map list, reads the image header, then calls either `load_image()` or `load_compressed_image()`. Uncompressed load reads pages into buffers returned by `snapshot_write_next()` and finalizes the snapshot. Compressed load maintains a ring of read pages, starts decompression workers and CRC worker, validates compressed/uncompressed lengths, feeds decompressed pages to `snapshot_write_next()`, finalizes the image, and checks CRC when present.

## State and Persistence Behavior
The persistent on-disk marker is `struct swsusp_header` in the resume swap area. It stores the original swap signature, hibernation signature `S1SUSPEND`, first swap-map sector, flags, CRC32, and optional hardware signature. Swap-map pages form the persistent sector list for all image pages. Runtime `swsusp_extents` tracks allocated swap slots so failures and `swsusp_unmark()` can free them.

## Dependencies and Integration Points
Depends on swap slot allocation, block device open/read/write, BIOs, blk plugs, crypto acomp, kthreads, CRC32, CPU count, VM allocation, cache flushing for executable restored pages, and snapshot streaming from `snapshot.c`. `hibernate.c` chooses flags and calls read/write/check; `/dev/snapshot` uses swap allocation helpers for user-space hibernation.

## Risks
Risks include corrupting swap signatures, leaking hibernation swap slots, malformed swap maps causing invalid reads, BIO error propagation mistakes, insufficient low-memory reserves during async I/O, compression length validation bugs, CRC mismatches, hardware signature false positives/negatives, cache maintenance gaps on architectures needing clean executable pages, and races around block-device ownership.

## Test Signals
Test compressed and `SF_NOCOMPRESS_MODE` images, LZO and LZ4, `hibernate_compression_threads=` boot/sysfs values, low-swap and low-memory failures, BIO read/write errors, CRC mismatch injection, hardware signature mismatch, resume offset handling, `swsusp_unmark()` rollback, and repeated hibernate/resume cycles verifying swap slots are freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/user.c -->
# sources/distributed-fs/ceph-client/kernel/power/user.c

## Purpose
Implements the `/dev/snapshot` misc device, the user-space ABI for software suspend/resume. It lets privileged user space freeze tasks, create/read a hibernation image, write/load an image, allocate/free swap pages, request atomic restore, and trigger platform poweroff.

## Important APIs, Types, and Functions
State is held in global `snapshot_state` of `struct snapshot_data`, containing a `snapshot_handle`, swap type, open mode, frozen/ready/platform flags, bitmap ownership, and selected resume device. `need_wait` delays writes/ioctls until device probing completes. `is_hibernate_resume_dev()` reports whether a device matches the active snapshot resume device.

File operations are `snapshot_open()`, `snapshot_release()`, `snapshot_read()`, `snapshot_write()`, `snapshot_ioctl()`, optional `snapshot_compat_ioctl()`, and misc registration `snapshot_device_init()`. `snapshot_set_swap_area()` handles native and compat `SNAPSHOT_SET_SWAP_AREA` payloads.

Supported ioctls include `SNAPSHOT_FREEZE`, `SNAPSHOT_UNFREEZE`, `SNAPSHOT_CREATE_IMAGE`, `SNAPSHOT_ATOMIC_RESTORE`, `SNAPSHOT_FREE`, `SNAPSHOT_PREF_IMAGE_SIZE`, `SNAPSHOT_GET_IMAGE_SIZE`, `SNAPSHOT_AVAIL_SWAP_SIZE`, `SNAPSHOT_ALLOC_SWAP_PAGE`, `SNAPSHOT_FREE_SWAP_PAGES`, `SNAPSHOT_S2RAM`, `SNAPSHOT_PLATFORM_SUPPORT`, `SNAPSHOT_POWER_OFF`, and `SNAPSHOT_SET_SWAP_AREA`.

## Control Flow
`snapshot_open()` rejects unavailable hibernation and read/write mode, serializes with `system_transition_mutex`, acquires the hibernation token, initializes state, calls hibernation or restore notifiers depending on open direction, and creates memory bitmaps for restore writers.

Read mode is image creation: user space calls `SNAPSHOT_FREEZE`, which syncs filesystems, freezes processes, and creates bitmaps; `SNAPSHOT_CREATE_IMAGE`, which calls `hibernation_snapshot()` and returns `in_suspend`; then reads from the device. `snapshot_read()` advances `snapshot_read_next()` on page boundaries and copies the current page to user space.

Write mode is image restore: user space writes pages to the device. `snapshot_write()` advances `snapshot_write_next()` on page boundaries and copies user data into the returned kernel buffer. `SNAPSHOT_ATOMIC_RESTORE` finalizes image loading, verifies the image is complete and tasks are frozen, then calls `hibernation_restore()`.

Swap ioctls let user space identify a swap area, query available swap, allocate individual swap-backed pages with `alloc_swapdev_block()`, and free them. `SNAPSHOT_S2RAM` allows entering suspend-to-RAM after tasks are frozen. `snapshot_release()` frees swsusp pages, swap pages, bitmaps, thaws processes if needed, posts notifiers, releases the hibernation token, and unlocks system sleep.

## State and Persistence Behavior
`snapshot_state` is singleton process-global state; only one opener is allowed through `hibernate_acquire()`. Image data is streamed but not persisted by this file unless user space uses swap allocation ioctls. `data->dev` persists only for the open lifetime to protect the active resume device.

## Dependencies and Integration Points
Depends on miscdevice, snapshot ioctls UAPI, user-copy helpers, freezer, PM notifiers, hibernation/suspend core, swap helpers, memory bitmaps, console/device hotplug serialization through downstream calls, compat syscall support, and CAP_SYS_ADMIN authorization for ioctls.

## Risks
Risks include singleton state corruption if open/release assumptions change, incomplete cleanup when user space exits mid-transition, CAP_SYS_ADMIN ioctl misuse, compat layout mistakes, writing image data out of order, missed `snapshot_write_finalize()`, deadlock around `system_transition_mutex` and device probe waits, and allowing swap pages to be freed while an image is still in use. The ABI is sensitive because external suspend tools may depend on exact ioctl semantics.

## Test Signals
Use user-space suspend tools against `/dev/snapshot` for create/read and write/restore flows; test compat ioctls, partial reads/writes, non-page-aligned offsets, open mode rejection, unprivileged ioctl rejection, freeze/unfreeze cleanup, swap-area setup, swap page allocation/freeing, `SNAPSHOT_S2RAM`, platform support/poweroff flags, and abrupt process termination during each phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/wakelock.c -->
# sources/distributed-fs/ceph-client/kernel/power/wakelock.c

## Purpose
Implements the `/sys/power/wake_lock` and `/sys/power/wake_unlock` user-space wakelock compatibility interface. It maps named user-space locks to kernel `wakeup_source` objects so privileged processes can prevent system sleep, optionally with timeouts.

## Important APIs, Types, and Functions
`struct wakelock` stores the user-visible name, red-black tree node, registered `struct wakeup_source *`, and optional LRU node for garbage collection. Global state includes `wakelocks_lock`, `wakelocks_tree`, optional `number_of_wakelocks`, optional `wakelocks_lru_list`, `wakelock_work`, and `wakelocks_gc_count`.

Public entry points are `pm_show_wakelocks(char *buf, bool show_active)`, `pm_wake_lock(const char *buf)`, and `pm_wake_unlock(const char *buf)`. Internal helpers include `wakelock_lookup_add()`, limit tracking helpers, LRU helpers, and optional `__wakelocks_gc()`.

## Control Flow
`pm_wake_lock()` requires `CAP_BLOCK_SUSPEND`, parses a non-empty lock name up to whitespace, optionally parses a timeout in nanoseconds, locks `wakelocks_lock`, finds or creates a wakelock, and calls `__pm_wakeup_event()` for timed locks or `__pm_stay_awake()` for indefinite locks. Timed nanoseconds are rounded up to milliseconds.

`wakelock_lookup_add()` searches the RB tree by name. If missing and creation is allowed, it enforces the configured limit, allocates the wakelock/name, registers a wakeup source, initializes `last_time`, links it into the RB tree, optionally adds it to the LRU list, and increments the count.

`pm_wake_unlock()` also requires `CAP_BLOCK_SUSPEND`, trims a trailing newline, looks up an existing lock, calls `__pm_relax()`, marks it most recent in the LRU list, and triggers optional GC. `pm_show_wakelocks()` walks the RB tree and prints names whose wakeup source active state matches the requested view.

With `CONFIG_PM_WAKELOCKS_GC`, every 100 unlocks schedules work that scans the LRU list from oldest to newest and unregisters inactive wakelocks idle for at least 300 seconds.

## State and Persistence Behavior
Wakelocks are runtime-only kernel objects. Names persist in the RB tree until GC removes inactive old entries or until reboot. Active state and timestamps live in each `wakeup_source`. The sysfs show functions expose active or inactive names through `wake_lock` and `wake_unlock` attributes in `main.c`.

## Dependencies and Integration Points
Depends on capabilities, sysfs PM attributes, `wakeup_source_register()`, wakeup-source active accounting, RB trees, optional LRU/workqueue GC, and autosleep/suspend wakeup checks. It is integrated into `/sys/power` only when `CONFIG_PM_WAKELOCKS` is enabled.

## Risks
Risks include unbounded named lock growth without a configured limit or GC, name parsing surprises around whitespace, timeout unit mismatch for user space, missing capability checks if reused elsewhere, lock contention around sysfs show/store, and stale inactive wakeup sources if GC is disabled. The configured limit check uses the current count before increment, so limit semantics should be verified against expected maximum.

## Test Signals
Write lock names and timed locks to `/sys/power/wake_lock`, unlock through `/sys/power/wake_unlock`, verify active/inactive listings, test `CAP_BLOCK_SUSPEND` denial, invalid empty/timeout inputs, many unique lock names with `CONFIG_PM_WAKELOCKS_LIMIT`, GC behavior after idle timeout, and autosleep prevention while a lock is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/wakelock.c -->
