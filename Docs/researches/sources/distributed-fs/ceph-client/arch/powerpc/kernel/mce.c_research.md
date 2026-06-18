
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce.c

Purpose: common PowerPC machine-check and hypervisor-maintenance interrupt support: event capture, per-CPU queues, notification, deferred memory-failure processing, printing, HMI special-trigger handling, and MCE data allocation.

Important APIs/types/functions: `mce_register_notifier`; `save_mce_event`; `get_mce_event`; `release_mce_event`; `machine_check_queue_event`; `mce_common_process_ue`; `mce_run_irq_context_handlers`; `machine_check_print_event_info`; `machine_check_early`; `hmi_handle_debugtrig`; `hmi_exception_realmode`; `mce_init`; per-PACA `mce_info`, queue counters, and `mce_pending_irq_work`.

Control flow: early machine-check handlers call platform-specific real-mode decode, which eventually saves an event into the current CPU's PACA `mce_info`. Unrecovered events schedule irq work. UE events with physical addresses are copied to a UE queue for later notifier and `memory_failure` handling. `machine_check_queue_event` releases the current nested event into a print/log queue. IRQ-context processing calls platform log hooks, prints queued events, schedules UE work, and clears pending status. Printing decodes severity, initiator, class, subtype, effective address, physical address, guest/user context, and SLB dumps. HMI handling detects POWER9 debug trigger functions from device tree or PVR and either handles vector CI emulation or falls back to platform HMI code.

State and persistence: transient event state lives per CPU in PACA-allocated `struct mce_info` buffers, counters, and pending flags. Events can lead to tainting, notifier callbacks, memory failure isolation, and platform/NVRAM logging through `ppc_md.machine_check_log_err`, but this file itself does not persist records.

Dependencies and integration: relies on PACA allocation, NMI interrupt wrappers, `ppc_md` machine hooks, exception tables, device tree CPU properties, `memory_failure`, notifier chains, and platform HMI synchronization helpers.

Risks: queue overflow silently drops events; real-mode paths must avoid unsafe operations; nested count handling must match release calls; ignored UE events depend on exception-table fixups; HMI debug-trigger interpretation differs by CPU revision and firmware properties.

Test signals: inject recoverable and unrecoverable MCEs, verify event printing and taint, exercise UE memory failure with and without physical address, test KVM guest MCE pass-through, and validate POWER9 HMI debug-trigger paths on affected revisions.
