
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-hmi.c

Purpose: handles OPAL Hypervisor Maintenance Interrupt event messages, logs detailed checkstop/recovery information, and triggers platform reboot on unrecoverable events.

Important APIs/types/functions: `struct OpalHmiEvtNode` queues copied HMI events. `print_hmi_event_info()` formats severity, disposition, HMER/TFMR, and event detail. `print_core_checkstop_reason()`, `print_nx_checkstop_reason()`, and `print_npu_checkstop_reason()` decode malfunction alert reason fields. `opal_handle_hmi_event()` is the OPAL message notifier. `hmi_event_handler()` processes queued work. `opal_hmi_handler_init()` registers the notifier.

Control flow: init registers for `OPAL_MSG_HMI_EVT` once. The notifier runs in message context, copies event data into a GFP_ATOMIC node, appends it to a spinlock-protected list, and schedules work. The workqueue drains events, prints details, remembers whether any disposition is unrecovered, and if so drains additional HMI messages directly from OPAL before calling `pnv_platform_error_reboot()`.

State and persistence: global queue `opal_hmi_evt_list`, spinlock, work item, and init guard are runtime-only. No persistent state is written.

Dependencies and integration points: depends on OPAL message notifier infrastructure, OPAL HMI event ABI, ratelimited printk, PowerNV platform reboot/error handling, and checkstop reason constants from OPAL headers.

Risks: unrecovered HMI events intentionally lead to platform error reboot. Event copies assume OPAL message parameters contain a complete `struct OpalHMIEvent`. Logging is ratelimited for harmless events but fatal paths drain all queued firmware messages before reboot. Allocation failure drops event detail.

Test signals: notifier registration, recovered and unrecovered HMI injection, checkstop reason decoding for core/NX/NPU, ratelimit behavior for harmless events, workqueue ordering, and reboot path on unrecovered disposition.
