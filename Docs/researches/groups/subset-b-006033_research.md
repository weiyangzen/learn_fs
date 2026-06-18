# subset-b-006033 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irqdomain.c -->
# sources/distributed-fs/ceph-client/kernel/irq/irqdomain.c

## Purpose
`irqdomain.c` is the generic IRQ-domain core. It maps hardware interrupt numbers and firmware interrupt specifiers to Linux virtual IRQ descriptors, publishes and removes interrupt domains, manages reverse maps, and implements the allocation/free/activation path for hierarchical interrupt controllers.

## Important APIs, types, and functions
Global state is `irq_domain_list`, `irq_domain_mutex`, and `irq_default_domain`. `struct irqchip_fwid` backs synthetic fwnodes created by `__irq_domain_alloc_fwnode()` and destroyed by `irq_domain_free_fwnode()`. Creation and lifecycle entry points include `irq_domain_instantiate()`, `irq_domain_create_simple()`, `irq_domain_create_legacy()`, `irq_domain_remove()`, and `irq_domain_update_bus_token()`. Mapping APIs include `irq_find_matching_fwspec()`, `irq_create_mapping_affinity()`, `irq_create_fwspec_mapping()`, `irq_create_of_mapping()`, `irq_dispose_mapping()`, and `__irq_resolve_mapping()`. Hierarchy-specific APIs include `__irq_domain_alloc_irqs()`, `irq_domain_free_irqs()`, `irq_domain_alloc_irqs_parent()`, `irq_domain_free_irqs_parent()`, `irq_domain_push_irq()`, `irq_domain_pop_irq()`, `irq_domain_activate_irq()`, and `irq_domain_deactivate_irq()`.

## Control flow
Domain instantiation allocates the `struct irq_domain`, derives a debugfs-safe name from fwnode or bus token data, initializes revmap storage, attaches generic chips and parent/root hierarchy metadata when configured, publishes the domain on the global list, and optionally pre-associates legacy fixed virqs. Firmware mapping first resolves a domain from fwspec/fwnode and bus token, translates the specifier to hwirq/type through `.translate` or `.xlate`, reuses an existing mapping when type-compatible, otherwise allocates descriptors and either associates a flat domain mapping or invokes hierarchical allocation. Free paths remove mappings, clear handlers/chips, synchronize interrupt execution, call domain `.free`/`.unmap`, free hierarchy `irq_data`, and release descriptors.

## State and persistence
All state is in-memory kernel state: domain list membership, fwnode references, `domain->mapcount`, linear and radix-tree reverse maps, default-domain pointer, domain flags, hierarchy `irq_data` chains, and debugfs dentries. Nothing persists across boot, but mappings remain authoritative while descriptors and domains live.

## Dependencies and integration points
This file integrates firmware descriptions from OF, ACPI, software nodes, synthetic irqchip fwnodes, irq descriptors, generic chips, MSI helper hooks, hierarchical irqchips, RCU-protected lookup, debugfs, radix trees, and module-exported genirq APIs. Device-tree xlate helpers and fwspec translate helpers provide common binding formats for interrupt-controller drivers.

## Risks and test signals
Important risks are domain name collisions, leaked fwnode references, revmap corruption during hierarchy push/pop, type mismatches on reused mappings, races between lookup and removal, missing synchronize before descriptor reuse, invalid hierarchy trimming markers, MSI wired-domain special cases, and debugfs lifetime bugs. Test signals include simple and legacy domain creation, OF/fwspec mapping reuse, type mismatch rejection, radix revmap entries beyond linear size, hierarchical parent allocation rollback, push/pop before request_irq, activate failure rollback, domain removal with nonempty revmaps, and debugfs output for parent chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irqdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/kexec.c -->
# sources/distributed-fs/ceph-client/kernel/irq/kexec.c

## Purpose
`kexec.c` provides the genirq shutdown helper used before jumping into a kexec kernel. It masks and shuts down started interrupts and, where possible, clears active state or sends EOI so the next kernel does not inherit in-flight interrupt state.

## Important APIs, types, and functions
The only function is `machine_kexec_mask_interrupts()`. It iterates every `struct irq_desc` with `for_each_irq_desc()`, inspects the descriptor `irq_chip`, uses `irqd_is_started()`, optionally calls `irq_set_irqchip_state(..., IRQCHIP_STATE_ACTIVE, false)`, conditionally invokes `chip->irq_eoi()`, and finishes each descriptor through `irq_shutdown()`.

## Control flow
For each started interrupt, the function skips missing chips, tries VM-forwarded active-state clearing when `CONFIG_GENERIC_IRQ_KEXEC_CLEAR_VM_FORWARD` is enabled, falls back to EOI for in-progress IRQs with an EOI callback, and then shuts the descriptor down through the normal genirq shutdown path.

## State and persistence
The routine intentionally mutates live interrupt-controller and descriptor state immediately before kexec. It clears active/in-progress hardware state where supported and transitions descriptors to shutdown. No persistent storage is involved.

## Dependencies and integration points
It depends on the generic descriptor iterator, irqchip state callbacks, irqchip EOI operations, and `irq_shutdown()` from the core IRQ internals. It is invoked by architecture kexec flows rather than ordinary driver code.

## Risks and test signals
Risks include chips lacking active-state or EOI support, VM-forwarded interrupts not being cleared, EOI issued to the wrong in-progress state, and shutdown callbacks running late in a crash-like transition. Test signals include kexec with active device interrupts, passthrough/forwarded interrupts, chips with and without EOI callbacks, and verifying the new kernel does not see stuck interrupt lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/manage.c -->
# sources/distributed-fs/ceph-client/kernel/irq/manage.c

## Purpose
`manage.c` is the main driver-facing genirq management layer. It implements interrupt request/free APIs, enable/disable nesting, synchronization, trigger configuration, SMP affinity and affinity notifications, forced threaded interrupt handling, per-CPU IRQs, NMI setup, wakeup control, vCPU affinity hooks, and irqchip state access.

## Important APIs, types, and functions
Important public APIs include `request_threaded_irq()`, `request_any_context_irq()`, `request_nmi()`, `free_irq()`, `free_nmi()`, `enable_irq()`, `disable_irq()`, `disable_irq_nosync()`, `disable_hardirq()`, `synchronize_irq()`, `synchronize_hardirq()`, `irq_set_irq_wake()`, `irq_set_affinity()`, `irq_force_affinity()`, `irq_set_affinity_notifier()`, `irq_set_vcpu_affinity()`, `request_percpu_irq_affinity()`, `free_percpu_irq()`, `request_percpu_nmi()`, `prepare_percpu_nmi()`, `teardown_percpu_nmi()`, `irq_get_irqchip_state()`, and `irq_set_irqchip_state()`. Core internals are `__setup_irq()`, `__free_irq()`, `irq_thread()`, `irq_finalize_oneshot()`, `irq_do_set_affinity()`, `irq_set_affinity_locked()`, and `__irq_set_trigger()`.

## Control flow
Requesting an IRQ validates flags, allocates an `irqaction`, powers the irqchip, optionally rewrites the handler for forced threading, creates kthreads for threaded actions, serializes setup through `request_mutex`, bus lock, and `desc->lock`, requests chip resources, checks sharing and trigger compatibility, activates the IRQ domain, starts the interrupt unless `NO_AUTOEN`, installs PM accounting, registers proc entries, and waits for threads to become ready. Freeing removes the matching action, updates PM counters, shuts down the line if it was the last action, unregisters proc entries, synchronizes hard and threaded handlers, stops kthreads, deactivates the domain, releases chip resources, and drops module/PM references.

## State and persistence
State is descriptor-local and runtime-only: `desc->action`, depth counters, `istate` bits such as `IRQS_ONESHOT` and `IRQS_NMI`, `threads_active`, `threads_oneshot`, wake depth, affinity masks, pending affinity masks, affinity notifier refs, per-CPU enabled masks, PM suspend counters, and irqchip activation state. Forced threading is controlled by the early `threadirqs` parameter static key.

## Dependencies and integration points
This file depends on irq descriptors, irq domains, irq chips, kthreads, task work, cpumasks, CPU isolation/housekeeping, PM-runtime irqchip hooks, proc registration helpers, `irq_work` redirect synchronization, and architecture/chip callbacks for affinity, wake, NMI setup, resource management, and irqchip state. It is the bridge between device drivers and lower-level interrupt-controller implementations.

## Risks and test signals
Risks include deadlocks from synchronization while holding driver locks, sharing mismatches, unbalanced enable/disable or wake depth, stale oneshot masks, kthread teardown races, affinity updates during CPU hotplug, managed IRQ behavior on isolated/offline CPUs, NMI misuse, irqchip PM/resource leaks on setup failure, and pending move handling. Test signals include shared threaded IRQs, `handler=NULL` oneshot validation, forced `threadirqs`, setup failure rollback at each stage, free while interrupt threads are active, wake enable nesting, trigger mismatch warnings, affinity notifier lifetime, per-CPU IRQ enable/disable on each CPU, NMI request/free, and irqchip state get/set through parent data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/manage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/matrix.c -->
# sources/distributed-fs/ceph-client/kernel/irq/matrix.c

## Purpose
`matrix.c` implements a per-CPU bitmap allocator for interrupt vectors or similar finite IRQ resources. It tracks system-reserved bits, regular allocations, managed interrupt reservations, online CPU availability, and global reservation accounting.

## Important APIs, types, and functions
The main types are internal `struct irq_matrix` and per-CPU `struct cpumap`. Public functions include `irq_alloc_matrix()`, `irq_matrix_online()`, `irq_matrix_offline()`, `irq_matrix_assign_system()`, `irq_matrix_reserve_managed()`, `irq_matrix_remove_managed()`, `irq_matrix_alloc_managed()`, `irq_matrix_assign()`, `irq_matrix_reserve()`, `irq_matrix_remove_reserved()`, `irq_matrix_alloc()`, `irq_matrix_free()`, `irq_matrix_available()`, `irq_matrix_reserved()`, `irq_matrix_allocated()`, and debugfs-only `irq_matrix_debug_show()`.

## Control flow
Initialization allocates a matrix plus per-CPU maps, with each CPU map carrying allocation and managed bitmaps. CPU online initializes its available count from alloc range minus managed and system bits, then contributes to global availability; offline subtracts it. Allocation picks a best online CPU, finds zero areas after combining system, managed, and allocated maps, marks the selected map, and updates global/per-CPU counters. Managed reservations allocate one managed bit per target CPU and roll back on failure; managed allocation selects the CPU with the lowest managed allocation count.

## State and persistence
State is purely in-memory allocator state: global counters, per-CPU `available`, `allocated`, `managed`, `managed_allocated`, `online` flags, `system_map`, `managed_map`, and `alloc_map`. CPU hotplug changes accounting but does not persist across boot.

## Dependencies and integration points
It depends on bitmap helpers, percpu allocation, CPU masks/hotplug assumptions, tracepoints from `trace/events/irq_matrix.h`, and optional seq_file debug output. Architectures such as x86 vector allocation use this as a resource allocator under genirq affinity and managed IRQ paths.

## Risks and test signals
Risks include counter skew between online/offline paths, managed bits being freed while allocated, allocation from empty masks, global reservation underflow, system-bit replacement misuse, and lockless debug snapshots observing transient state. Test signals include CPU hotplug with active vectors, allocation exhaustion, managed reservation rollback, managed allocation balancing, freeing managed and non-managed bits, system vector replacement, reservation warnings, and debugfs consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/matrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/migration.c -->
# sources/distributed-fs/ceph-client/kernel/irq/migration.c

## Purpose
`migration.c` handles pending IRQ affinity moves, especially when interrupts must be migrated while masked or during CPU hotplug. It completes, clears, or defers move-pending state around irqchip affinity callbacks.

## Important APIs, types, and functions
The file exports `irq_fixup_move_pending()`, `irq_force_complete_move()`, `irq_move_masked_irq()`, `__irq_move_irq()`, and `irq_can_move_in_process_context()`. It operates on `struct irq_desc`, `struct irq_data`, descriptor `pending_mask`, and irqdata move-pending flags.

## Control flow
CPU hotplug cleanup checks whether a pending mask still intersects online CPUs and clears move-pending when it no longer has a valid target or when forced. Masked move handling clears move-pending, rejects per-CPU or empty masks, requires `irq_set_affinity`, and calls `irq_do_set_affinity()` while the line is masked; `-EBUSY` re-establishes pending state for a later interrupt. `__irq_move_irq()` masks the interrupt when needed, delegates to `irq_move_masked_irq()`, and restores mask state.

## State and persistence
State is descriptor-local and transient: `IRQD_SETAFFINITY_PENDING`, `desc->pending_mask`, and irqchip/vector migration state. There is no persistence outside live descriptor state.

## Dependencies and integration points
It depends on genirq affinity helpers in `manage.c`, irqchip callbacks, descriptor locking rules, CPU online masks, and hierarchical top-level irqdata resolution. Flow handlers call these helpers when safe to move an IRQ.

## Risks and test signals
Risks include losing pending affinity when the last target CPU goes offline, reprogramming an unmasked edge interrupt, move storms when vector cleanup returns `-EBUSY`, and invalid calls for per-CPU interrupts. Test signals include CPU down with pending moves, edge-triggered IO-APIC-like interrupts, vector allocator busy responses, process-context-capable chips, and forced completion callbacks in parent irqdata chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/migration.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/msi.c -->
# sources/distributed-fs/ceph-client/kernel/irq/msi.c

## Purpose
`msi.c` is the generic Message Signaled Interrupt core for PCI and non-PCI devices. It manages per-device MSI descriptor stores, MSI irqdomains, per-device MSI domains, MSI message programming, allocation/free of Linux IRQs for MSI table entries, sysfs visibility, wired-to-MSI translation, and isolated-MSI capability detection.

## Important APIs, types, and functions
Important internal types are `struct msi_device_data`, storing per-device properties, a descriptor mutex, domain slots, xarrays, and iterator state, and `struct msi_ctrl`, describing domain/range/nirq operations. Public APIs include `msi_setup_device_data()`, `msi_domain_insert_msi_desc()`, `msi_domain_free_msi_descs_range()`, `msi_domain_first_desc()`, `msi_next_desc()`, `msi_domain_get_virq()`, `get_cached_msi_msg()`, `msi_create_irq_domain()`, `msi_create_parent_irq_domain()`, `msi_create_device_irq_domain()`, `msi_remove_device_irq_domain()`, `msi_match_device_irq_domain()`, `msi_domain_alloc_irqs_range()`, `msi_domain_alloc_irqs_all_locked()`, `msi_domain_alloc_irq_at()`, `msi_device_domain_alloc_wired()`, `msi_domain_free_irqs_range()`, `msi_domain_free_irqs_all()`, `msi_device_domain_free_wired()`, `msi_get_domain_info()`, `msi_device_has_isolated_msi()`, and `msi_domain_set_affinity()`.

## Control flow
Device setup allocates devres-managed MSI data, creates an optional `msi_irqs` sysfs group, initializes xarrays, and imports a legacy global MSI domain when present. Descriptor allocation inserts `msi_desc` objects by fixed or xarray-selected index. MSI domain creation fills default domain/chip ops, creates a hierarchical IRQ domain, applies bus tokens, and records domain metadata. Allocation prepares domain-specific alloc info, optionally creates simple descriptors, allocates IRQ descriptors through irqdomain hierarchy, associates each virq with the MSI descriptor, initializes/reserves/activates virqs, writes MSI messages on activation, and populates sysfs files. Freeing deactivates IRQs, frees irqdomain allocations, removes sysfs files, clears descriptor IRQs, and optionally frees descriptors.

## State and persistence
State is runtime-only and tied to `struct device`: xarray descriptor stores indexed by MSI table slot/domain id, per-device domain pointers, cached MSI messages in descriptors, sysfs attribute allocations, iterator position, and devres-owned domain/data cleanup. Hardware MSI table state is programmed via irqchip message writes and cleared on deactivation.

## Dependencies and integration points
This file integrates the generic IRQ domain hierarchy, `struct msi_domain_info` and `struct msi_domain_ops`, irqchip MSI message composition/writes, PCI MSI/MSI-X attributes, xarrays, devres, sysfs, cpumask affinity descriptors, device fwnodes, MSI parent domains, wire-to-MSI controllers, and architecture isolated-MSI policy.

## Risks and test signals
Risks include descriptor leaks when associated IRQs still exist, xarray index range errors, PCI multi-MSI fallback behavior, reservation-mode misuse on unmaskable devices, MSI message writes without level-capable support, per-device domain cleanup ordering, sysfs file lifetime, managed IRQ shutdown when no target CPU is online, and security assumptions around isolated MSI. Test signals include PCI MSI and MSI-X allocation/free, simple platform MSI descriptors, multi-domain devices, device removal with active descriptors, allocation failure rollback, reservation-mode activation, affinity changes rewriting messages, wired-to-MSI fwspec allocation, sysfs `msi_irqs` population/removal, and VFIO-style isolated-MSI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/pm.c -->
# sources/distributed-fs/ceph-client/kernel/irq/pm.c

## Purpose
`pm.c` implements system power-management behavior for interrupts. It suspends device IRQs, preserves wakeup-capable lines, records wakeup events, and resumes early or normal IRQs during syscore and device resume.

## Important APIs, types, and functions
Key functions are `irq_pm_handle_wakeup()`, `irq_pm_install_action()`, `irq_pm_remove_action()`, `suspend_device_irqs()`, `rearm_wake_irq()`, `resume_device_irqs()`, and the syscore resume hook registered by `irq_pm_init_ops()`. Internal helpers are `suspend_device_irq()`, `resume_irq()`, and `resume_irqs()`.

## Control flow
Action installation/removal updates descriptor counters for `IRQF_FORCE_RESUME`, `IRQF_NO_SUSPEND`, and `IRQF_COND_SUSPEND`. Suspend iterates descriptors, skips nested-thread IRQs and no-suspend/chained/unused lines, arms wakeup IRQs, optionally enables disabled wake lines for chips requiring that, disables non-wakeup IRQs, masks chips that request mask-on-suspend, and synchronizes when needed. Resume clears wakeup-armed state, restores IRQs enabled only for suspend wakeup, force-resumes requested lines, and separates early resume (`IRQF_EARLY_RESUME`) from normal resume.

## State and persistence
State lives in `desc->istate`, `desc->depth`, PM action counters, and irqdata flags such as `IRQD_WAKEUP_ARMED` and `IRQD_IRQ_ENABLED_ON_SUSPEND`. It persists only across the active suspend/resume cycle.

## Dependencies and integration points
It depends on irq descriptor locking, wakeup irqchip flags, genirq enable/disable helpers, `pm_system_irq_wakeup()`, syscore registration, suspend infrastructure, and action flags installed by `manage.c`.

## Risks and test signals
Risks include wakeup IRQs left enabled or disabled incorrectly, missing synchronization before suspend completes, nested threaded IRQ mishandling, force-resume depth inconsistencies, shared no-suspend/conditional-suspend accounting errors, and chips requiring mask-on-suspend. Test signals include suspend/resume with wake-capable disabled IRQs, early-resume handlers, force-resume actions, shared IRQs mixing suspend flags, wake event rearming, and irqchips with `IRQCHIP_ENABLE_WAKEUP_ON_SUSPEND` or `IRQCHIP_MASK_ON_SUSPEND`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/proc.c -->
# sources/distributed-fs/ceph-client/kernel/irq/proc.c

## Purpose
`proc.c` exposes generic IRQ state through procfs. It creates `/proc/irq`, per-IRQ control/status files, handler directories, default SMP affinity controls, and `/proc/interrupts` output for generic IRQ accounting.

## Important APIs, types, and functions
Important entry points are `init_irq_proc()`, `register_irq_proc()`, `unregister_irq_proc()`, `register_handler_proc()`, `unregister_handler_proc()`, and `show_interrupts()`. SMP helpers expose `smp_affinity`, `smp_affinity_list`, `affinity_hint`, `effective_affinity`, `effective_affinity_list`, `node`, and `default_smp_affinity`. `irq_spurious_proc_show()` reports spurious counters.

## Control flow
Initialization creates `/proc/irq`, registers `default_smp_affinity`, then creates directories for existing IRQ descriptors. When a handler is requested, `register_irq_proc()` creates `/proc/irq/<n>` plus affinity and spurious files, and `register_handler_proc()` creates a unique handler-name directory. Affinity writes parse cpumasks or CPU lists, reject masks without online CPUs except for architecture autoselection, and call `irq_set_affinity()`. `/proc/interrupts` iterates IRQ numbers, skips hidden/chained/unallocated descriptors, prints per-CPU counts, chip/domain/hwirq/level metadata, and action names.

## State and persistence
State consists of proc dentries stored in descriptors/actions plus user-visible snapshots of descriptor counters and affinity masks. Writes update live genirq affinity state; proc entries disappear when IRQs or handlers are unregistered.

## Dependencies and integration points
It depends on procfs, seq_file, irq descriptors, affinity helpers from `manage.c`, cpumask parsers, sparse IRQ lookup rules, kernel interrupt statistics, and architecture `arch_show_interrupts()` extension.

## Risks and test signals
Risks include proc entry lifetime races with descriptor removal, affinity writes making systems unusable, duplicate handler names, stale action directories, hidden IRQ leakage, and inconsistent `/proc/interrupts` snapshots without descriptor-specific proc protection. Test signals include request/free cycles, concurrent proc reads during free, affinity bitmask and list writes, default affinity rejection of offline-only masks, effective-affinity display, duplicate shared handler names, spurious file contents, and architecture-specific interrupt rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/resend.c -->
# sources/distributed-fs/ceph-client/kernel/irq/resend.c

## Purpose
`resend.c` retries pending edge interrupts that may have arrived while disabled or masked. It prefers hardware retrigger support and falls back to a software tasklet resend when configured.

## Important APIs, types, and functions
Important functions are `check_irq_resend()`, optional `irq_inject_interrupt()`, `clear_irq_resend()`, and `irq_resend_init()`. Software resend uses `irq_resend_list`, `irq_resend_lock`, `resend_tasklet`, `resend_irqs()`, and `irq_sw_resend()`. Hardware retry uses `try_retrigger()` and irqchip `irq_retrigger` or hierarchy retrigger callbacks.

## Control flow
`check_irq_resend()` runs with interrupts disabled and `desc->lock` held. It rejects level-triggered IRQs, avoids duplicate replay, clears pending state, attempts hardware retrigger, falls back to software enqueue, and marks `IRQS_REPLAY` on success. Software resend queues the descriptor on an hlist and later invokes `desc->handle_irq()` from the tasklet. Generic injection first tries `irq_set_irqchip_state(...PENDING...)`, then uses resend for activated non-NMI interrupts.

## State and persistence
Runtime state is `IRQS_PENDING`, `IRQS_REPLAY`, each descriptor `resend_node`, and the global software resend list. There is no persistent storage.

## Dependencies and integration points
It depends on irq descriptor internals, irqchip retrigger/state callbacks, tasklets, nested-thread parent IRQ routing, hierarchy helpers, and optional `CONFIG_GENERIC_IRQ_INJECTION` testing support.

## Risks and test signals
Risks include resending level IRQs incorrectly, invoking handlers from unsuitable context, nested threaded IRQs without valid parent IRQs, replay bit not clearing in flow handlers, list races during descriptor teardown, and injection perturbing affinity changes. Test signals include disabled edge IRQ pending replay, chips with and without hardware retrigger, nested threaded interrupts, software resend disabled builds, clear during free, and debug injection success/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/resend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/settings.h -->
# sources/distributed-fs/ceph-client/kernel/irq/settings.h

## Purpose
`settings.h` centralizes internal accessors for `irq_desc->status_use_accessors`, replacing direct use of IRQ status macros and making descriptor settings changes explicit.

## Important APIs, types, and functions
It defines internal `_IRQ_*` aliases for settings bits, intentionally poisons direct macro names such as `IRQ_PER_CPU` and `IRQ_LEVEL`, and provides inline helpers including `irq_settings_clr_and_set()`, `irq_settings_is_per_cpu()`, `irq_settings_is_per_cpu_devid()`, `irq_settings_set_per_cpu()`, `irq_settings_set_no_balancing()`, `irq_settings_get_trigger_mask()`, `irq_settings_set_trigger_mask()`, `irq_settings_is_level()`, request/thread/probe/autoenable checks and setters, nested-thread and polled checks, disable-unlazy helpers, hidden checks, and no-debug helpers.

## Control flow
There is no runtime control flow beyond inline bit tests and mutations. Callers in genirq code use these helpers while holding the appropriate descriptor locks or during initialization.

## State and persistence
The header mutates only `desc->status_use_accessors`. The state is descriptor-local and runtime-only, though it strongly affects whether IRQs can be requested, probed, threaded, balanced, displayed, autoenabled, debugged, or treated as level/per-CPU.

## Dependencies and integration points
It depends on IRQ flag definitions from public genirq headers and is included by internal IRQ subsystem files such as management, PM, procfs, resend, and spurious handling. The macro poisoning enforces use of accessors inside the IRQ core.

## Risks and test signals
Risks include callers bypassing accessors, modifying flags without required locking, confusing irqdata flags with descriptor settings, and trigger-level settings getting out of sync with irqchip programming. Test signals include builds catching poisoned macro use, requestability/threadability/probeability transitions, trigger changes through `__irq_set_trigger()`, per-CPU and hidden IRQ behavior, and no-debug/spurious detector interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/settings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/spurious.c -->
# sources/distributed-fs/ceph-client/kernel/irq/spurious.c

## Purpose
`spurious.c` detects and mitigates bad, unhandled, or misrouted interrupts. It reports bogus handler returns, counts repeated unhandled interrupts, disables lines that appear stuck, and optionally polls shared handlers to recover misrouted IRQs.

## Important APIs, types, and functions
The primary entry point is `note_interrupt()`, called after IRQ handlers return. Recovery helpers include `try_one_irq()`, `misrouted_irq()`, and `poll_spurious_irqs()`. Diagnostics use `bad_action_ret()`, `__report_bad_irq()`, and `report_bad_irq()`. Boot/module controls are `noirqdebug_setup()`, `irqfixup_setup()`, `irqpoll_setup()`, `noirqdebug`, and `irqfixup`.

## Control flow
Handler returns are validated first. Threaded IRQ wakeups defer spurious accounting until the next hard interrupt so thread completion can be observed. `IRQ_NONE` updates recent unhandled counters with a decay window. When fixup/polling is enabled, the code polls other shared IRQ handlers looking for a misrouted interrupt and compensates the unhandled count if one handled it. After 100,000 samples, if more than 99,900 were unhandled, it reports handlers, marks the IRQ spurious-disabled, increments depth, disables the line, and starts a timer to periodically poll disabled shared lines.

## State and persistence
State lives in descriptor counters and bits: `irq_count`, `irqs_unhandled`, `last_unhandled`, `threads_handled`, `threads_handled_last`, `IRQS_POLL_INPROGRESS`, `IRQS_PENDING`, and `IRQS_SPURIOUS_DISABLED`. Global runtime state includes `irqfixup`, `noirqdebug`, `irq_poll_cpu`, `irq_poll_active`, and the poll timer.

## Dependencies and integration points
It depends on timer/jiffies, module parameters and boot options, genirq flow handling, shared IRQ actions, descriptor locking, `handle_irq_event()`, and settings helpers for per-CPU/nested/polled/no-debug behavior. It is part of the post-handler accounting path for normal interrupts.

## Risks and test signals
Risks include false disabling of a rarely handled shared line, high overhead from `irqpoll`, PREEMPT_RT incompatibility for fixup options, races with action removal during diagnostics, deferred threaded accounting mistakes, and polling handlers that are not safe when the device did not interrupt. Test signals include bogus return values, repeated `IRQ_NONE`, shared threaded handlers, `irqfixup` and `irqpoll` boot options, spurious-disabled polling recovery, handler removal during reporting, and `noirqdebug` disabling lockup detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/spurious.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq_work.c -->
# sources/distributed-fs/ceph-client/kernel/irq_work.c

## Purpose
`irq_work.c` implements the IRQ-work framework for NMI-safe enqueueing of callbacks that run from hardirq-like context, timer tick fallback, remote CPU IPI delivery, or per-CPU threads on PREEMPT_RT.

## Important APIs, types, and functions
Per-CPU state includes `raised_list`, `lazy_list`, `irq_workd`, and SMP `irq_work_wakeup`. Public functions are `irq_work_queue()`, `irq_work_queue_on()`, `irq_work_needs_cpu()`, `irq_work_single()`, `irq_work_run()`, `irq_work_tick()`, and `irq_work_sync()`. Architecture integration is through weak `arch_irq_work_raise()` and `arch_irq_work_has_interrupt()`.

## Control flow
Queueing atomically claims work with `IRQ_WORK_CLAIMED`, `IRQ_WORK_PENDING`, and `CSD_TYPE_IRQ_WORK`, then places it on the local raised or lazy list depending on flags and PREEMPT_RT rules. Remote queueing uses `__smp_call_single_queue()` and, on PREEMPT_RT for non-hard work, queues a hard wakeup item to wake the target CPU's `irq_work/%u` thread. Running drains lockless lists, clears pending, invokes callbacks under lockdep IRQ-work annotations, clears busy state, and wakes synchronizers when needed. Tick fallback drains work when no arch interrupt exists and wakes the RT thread for lazy work.

## State and persistence
State is per-CPU lockless-list membership plus atomic flags embedded in each `struct irq_work`. `irq_work_sync()` waits for busy state using `rcuwait` plus RCU synchronization in threaded/fallback modes or spins when hard IRQ delivery is available. No state persists beyond queued work lifetime.

## Dependencies and integration points
It depends on llist, atomic bit flags, SMP call-single queues, tick/nohz, hardirq/preempt state, lockdep, KASAN aux stack recording, RCU wait, smpboot per-CPU threads, trace IPI events, and architecture IRQ-work interrupt support. Many kernel subsystems use irq_work to defer NMI/hardirq-unsafe work.

## Risks and test signals
Risks include double queueing, callbacks freeing work before busy clears, remote queue attempts to offline CPUs, NMI use of non-NMI-safe remote IPI backends, lazy work starvation without ticks, PREEMPT_RT hard-vs-lazy context mistakes, and sync deadlocks if called with IRQs disabled. Test signals include local and remote queueing, requeue while callback is running, nohz tick-stopped lazy work, architectures without IRQ-work interrupts, PREEMPT_RT threaded execution, CPU hotplug flushing, `irq_work_sync()` before freeing memory, and lockdep/KASAN reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq_work.c -->
