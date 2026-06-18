# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cmm.c

Purpose: Implements IBM pseries Collaborative Memory Management, a ballooning driver that loans pages to the hypervisor and reclaims them based on PowerVM memory pressure requests.

Important APIs/types/functions: Defines module parameters `delay`, `hotplug_delay`, `oom_kb`, `min_mem_mb`, `debug`, `simulate`, and `disable`; globals `loaned_pages`, `loaned_pages_target`, `oom_freed_pages`, `hotplug_mutex`, `cmm_thread_ptr`, and `b_dev_info`; helpers `plpar_page_set_loaned()`, `plpar_page_set_active()`, `cmm_alloc_pages()`, `cmm_free_pages()`, `cmm_get_mpp()`, `cmm_thread()`, OOM/reboot/memory notifiers, sysfs registration, optional `cmm_migratepage()`, and module init/exit.

Control flow: Init checks CMO firmware support or simulation mode, registers notifiers and sysfs, initializes balloon metadata, and starts `cmmthread` unless disabled. The thread sleeps, pauses after memory hotplug, calls `h_get_mpp()` or simulation state, computes a target respecting minimum memory and OOM freed pages, then loans or frees balloon pages. OOM notification frees a configured amount of loaned pages. Disable stops the thread and frees all loaned pages.

State and persistence: Persistent kernel state includes the balloon page list, atomic loaned count, target count, OOM freed count, hotplug occurrence flag, sysfs device files, module parameters, and the CMM kthread. Loaned state also persists in hypervisor page state via `H_PAGE_INIT`.

Dependencies and integration points: Integrates with PowerVM hcalls, CMO page size, Linux balloon subsystem, OOM notifier, reboot notifier, memory hotplug notifier, sysfs bus/device registration, and optional balloon migration.

Risks: Hypervisor page-state transitions must be rolled back correctly on partial failure. Hotplug and balloon activity share delicate locking. OOM and disable paths can change the target while the thread is active. Simulation exposes extra sysfs control. Failure after sysfs registration must unwind all notifiers and devices.

Test signals: CMO-enabled LPAR ballooning, sysfs `loaned_kb`/`loaned_target_kb`/`oom_freed_kb`, OOM-triggered reclaim, memory hotplug suspend/resume behavior, reboot returning all pages active, balloon migration, simulation mode, and module unload are key signals.

Source read size: 631 lines, 15741 bytes.
