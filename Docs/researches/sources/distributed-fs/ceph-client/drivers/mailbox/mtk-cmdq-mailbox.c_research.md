# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-cmdq-mailbox.c

Purpose: implements the MediaTek GCE/CMDQ mailbox controller, where each mailbox channel represents a hardware command-queue thread executing DMA-backed `cmdq_pkt` command buffers for display/media clients.

Important APIs/types/functions: `struct cmdq`, `struct cmdq_thread`, `struct cmdq_task`, and `struct gce_plat` model controller, thread state, queued tasks, and SoC quirks. Exported helpers `cmdq_get_mbox_priv` and `cmdq_get_shift_pa` expose address conversion data. Key routines handle VM init, GCE control, thread suspend/resume/reset/disable, task chaining, IRQ completion, runtime PM, send, shutdown, flush, and xlate.

Control flow: probe maps GCE registers, gets clocks for one or more GCE blocks, initializes sync tokens, allocates thread/channel arrays, requests the shared IRQ, enables runtime PM, and registers a controller using client ACK txdone semantics. Xlate assigns thread priority from DT. Send allocates a `cmdq_task`, starts an idle thread with current/end addresses or suspends a busy thread and chains the new packet by rewriting the previous packet's final jump. IRQ handling finds threads with pending status, maps current GCE address back to DMA address, completes finished tasks via `mbox_chan_received_data` carrying `cmdq_cb_data`, handles errors, and disables empty threads.

State and persistence: task queues are per-thread `task_busy_list` entries protected by the channel lock; command buffers are DMA-synced and patched in memory. Runtime PM toggles GCE clocks and control bits; suspend records only a suspended flag and warns about live tasks.

Dependencies and integration: depends on DMA APIs, PM runtime, MediaTek CMDQ client packet format, GCE clocks, SoC match data for thread counts/address shifts/VM, and mailbox clients.

Risks: incorrect DMA address conversion or jump patching can execute wrong commands. Shutdown/flush must abort queued tasks exactly once. PM transitions with live tasks are risky and only warned.

Test signals: command completion/error IRQ tests, chained packet execution, flush while waiting in WFE, runtime suspend/resume, multi-GCE clock discovery, and SoC-specific address-shift validation.
