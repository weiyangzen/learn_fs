# subset-b-004017 Research

Grouped research report for the requested mailbox controller subset. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-sti.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-sti.c

Purpose: implements the STMicroelectronics STi mailbox controller, exposing up to 20 dynamic mailbox channels backed by STi hardware instances and per-instance channel bits. It supports TX-only operation when no IRQ is present and TX/RX operation when an IRQ is supplied.

Important APIs/types/functions: `struct sti_mbox_device`, `struct sti_mbox_pdata`, and `struct sti_channel` hold controller, SoC limits, and allocated channel identity. The mailbox ops are `sti_mbox_startup_chan`, `sti_mbox_shutdown_chan`, `sti_mbox_send_data`, and `sti_mbox_tx_is_ready`; `sti_mbox_xlate` maps two-cell DT specifiers to an available `mbox_chan`.

Control flow: probe reads match data, maps registers, allocates channel slots, registers a polling-txdone controller, and optionally installs a threaded IRQ. Startup clears/enables a requested hardware channel. TX writes the channel bit to `STI_IRQ_SET_OFFSET`. The hard IRQ validates enabled channels, disables the interrupt source, and wakes the thread; the thread drains pending instance bits, reports `mbox_chan_received_data(chan, NULL)`, clears the IRQ, and reenables the channel.

State and persistence: state is volatile MMIO plus `enabled[]`, protected by `mdev->lock`, and per-channel `con_priv` allocated during xlate then cleared on shutdown. No data payload is stored by the driver; it signals events only.

Dependencies and integration: depends on DT compatible `st,stih407-mailbox`, `mbox-name`, the generic mailbox framework, platform IRQ/MMIO resources, and `devm_mbox_controller_register`.

Risks: channel allocation is dynamic and must avoid stale `con_priv`; IRQ handling assumes enable state mirrors hardware. TX completion is inferred by polling enable/status bits, so missed clears can stall the mailbox queue.

Test signals: boot/probe with and without IRQ, DT two-cell xlate bounds tests, RX interrupt storm/spurious IRQ tests, and mailbox client TX timeout coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-sti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-test.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-test.c

Purpose: provides a debugfs-based generic mailbox exerciser. It lets developers send short signals/messages through named TX/RX mailbox channels, optionally copy payloads through MMIO windows, and read received data as hexdumps from userspace.

Important APIs/types/functions: `struct mbox_test_device` stores channels, MMIO mappings, buffers, locks, wait queue, async notification, and debugfs root. File operations cover `signal` writes, `message` read/write/poll/fasync, and client callbacks `mbox_test_receive_message`, `mbox_test_prepare_message`, and `mbox_test_message_sent`.

Control flow: probe maps optional TX/RX MMIO resources, requests `tx` and `rx` channels by name, creates debugfs files, and allocates an RX buffer when RX exists. Writing `message` copies userspace data, optionally writes the payload to TX MMIO in `tx_prepare`, and sends either the signal or message through `mbox_send_message`. RX callback copies from RX MMIO or the callback payload, marks `data_ready`, wakes readers, and sends SIGIO. Reads block unless data is ready or `O_NONBLOCK` is set, then emit a fixed-size hexdump and clear the buffer.

State and persistence: runtime state is in-memory only: message/signal scratch buffers, `rx_buffer`, `data_ready`, and async queue. Debugfs entries persist while the platform device is bound.

Dependencies and integration: depends on debugfs, mailbox client API, optional MMIO resources, wait queues, fasync, and DT compatible `mailbox-test`.

Risks: the test client assumes up to 128-byte payloads and can expose hardware-specific mailbox behavior through debugfs. Blocking sends use `tx_block` with a 500 ms timeout; controllers without reliable txdone can make writes fail or hang until timeout.

Test signals: manual debugfs send/read, poll and SIGIO behavior, no-RX/no-TX cases, MMIO and non-MMIO modes, and probe-defer when no channels are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-th1520.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-th1520.c

Purpose: implements the T-Head TH1520 mailbox IPC block for communication from the kernel CPU to three remote ICU CPU targets. It transfers seven 32-bit data words plus a dedicated ACK word and supports IRQ-based txdone.

Important APIs/types/functions: `struct th1520_mbox_priv` owns mapped local/remote ICU windows, clocks, shared IRQ, mailbox controller, and optional suspend context. `struct th1520_mbox_con_priv` binds each channel to local/remote bases and CPU id. Core functions include channel read/write helpers, `th1520_mbox_isr`, `th1520_mbox_send_data`, startup/shutdown, `th1520_mbox_xlate`, and PM callbacks.

Control flow: probe enables four clocks, maps one local and three remote ICU resources, derives per-CPU local windows, initializes four channels, clears/masks hardware, and registers a txdone-IRQ mailbox. Xlate rejects CPU0 because it is the local CPU. Startup clears local/remote data and GEN registers, unmasks the channel bit, and requests the shared IRQ. Send writes INFO0-INFO6 to the remote window and sets the RX-data generate bit. ISR checks the local status map bit, clears it, dispatches incoming data if INFO0 is nonzero, writes the ACK magic to the remote INFO7, optionally generates an ACK interrupt, and calls `mbox_chan_txdone` when local INFO7 contains the magic.

State and persistence: volatile channel registers hold data and ACK state. The driver stores interrupt masks across system sleep; payload registers are explicitly treated as lost during suspend.

Dependencies and integration: depends on named MMIO resources, four named clocks, one shared IRQ, DT `thead,th1520-mbox`, and generic mailbox IRQ txdone semantics.

Risks: the 28-byte payload contract is implicit in callers; CPU1/CPU2 ACK polling differs from CPU3 interrupt behavior. Shared IRQ and per-channel request/free require correct startup/shutdown ordering.

Test signals: multi-channel concurrent client tests, suspend/resume mask restore, busy/ACK timeout tests, and DT resource offset validation, especially the remote-icu0 quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-th1520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-xgene-slimpro.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-xgene-slimpro.c

Purpose: drives the AppliedMicro/APM X-Gene SLIMpro mailbox controller, exposing up to eight doorbell channels with independent register windows and IRQs for firmware communication.

Important APIs/types/functions: `struct slimpro_mbox_chan` stores per-channel MMIO, IRQ, channel pointer, and a three-word RX buffer. `struct slimpro_mbox` owns the mailbox controller and channel arrays. The mailbox ops are `slimpro_mbox_send_data`, `slimpro_mbox_startup`, and `slimpro_mbox_shutdown`; helpers read/write doorbell data and status bits.

Control flow: probe maps the controller window, discovers consecutive IRQs, initializes per-channel register offsets spaced by `MBOX_REG_SET_OFFSET`, and registers a txdone-IRQ controller. Startup requests the channel IRQ, clears/enables ACK and available status, and unmasks interrupts. Sending writes data words 1 and 2 before the doorbell word 0. IRQ handling checks ACK status to call `mbox_chan_txdone`, checks available status to copy three RX words, clears status bits, and calls `mbox_chan_received_data`.

State and persistence: only volatile MMIO and per-channel `rx_msg[3]` are maintained. IRQ resources are requested on channel startup and freed on shutdown through devm helpers.

Dependencies and integration: supports OF `apm,xgene-slimpro-mbox` and ACPI `APMC0D01`, uses the mailbox controller framework, and is registered at `subsys_initcall` so firmware clients can bind early.

Risks: channel count is truncated at the first missing IRQ; clients must use exactly the three-word message format. `devm_request_irq` inside startup paired with `devm_free_irq` is unusual but explicit.

Test signals: ACPI and DT probe, all channel IRQ discovery, ACK-only and RX-only interrupt paths, and firmware echo tests that validate word ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-xgene-slimpro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox.c

Purpose: implements the Linux generic mailbox framework used by controller drivers and mailbox clients. It manages controller registration, channel lookup from firmware descriptions, exclusive client binding, TX queueing, TX completion methods, RX delivery, and managed registration.

Important APIs/types/functions: exported APIs include `mbox_send_message`, `mbox_flush`, `mbox_request_channel`, `mbox_request_channel_byname`, `mbox_bind_client`, `mbox_free_channel`, `mbox_chan_received_data`, `mbox_chan_txdone`, `mbox_client_txdone`, `mbox_client_peek_data`, `mbox_chan_tx_slots_available`, `mbox_controller_register`, `mbox_controller_unregister`, and `devm_mbox_controller_register`. Internal helpers include `add_to_rbuf`, `msg_submit`, `tx_tick`, and the polling hrtimer.

Control flow: clients request channels via fwnode/OF `mboxes` references or bind an existing channel. Binding initializes the ring buffer, active request, completion, and possibly startup. Sending enqueues a message, submits it if no active request exists, and optionally blocks until txdone or timeout. Txdone can be reported by controller IRQ, controller polling through `last_tx_done`, or client ACK. `tx_tick` clears the active request, submits the next queued item, calls client `tx_done`, and completes blocking senders.

State and persistence: global controller list `mbox_cons` is protected by `con_mutex`. Per-channel state includes `cl`, `active_req`, ring-buffer indices/count, `txdone_method`, completion, and spinlock. No state persists beyond runtime binding.

Dependencies and integration: used by all mailbox controllers and clients, integrates with OF/fwnode reference parsing, module reference counting, hrtimers, completions, and devres cleanup.

Risks: callbacks can run in atomic context, so clients and controllers must obey locking constraints. Timeout path calls `tx_tick` and can race with late hardware completion if a controller reports txdone poorly. Message pointers must remain valid until txdone.

Test signals: queue-depth and timeout tests, polling/IRQ/ACK txdone modes, request-by-name parsing, devm unregister cleanup, and races around free while IRQ arrives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-adsp-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-adsp-mailbox.c

Purpose: provides a one-channel MediaTek ADSP mailbox controller for MT8186 and MT8195 style register layouts. It sends one 32-bit command bitfield and reports RX events without an in-band payload.

Important APIs/types/functions: `struct mtk_adsp_mbox_priv` stores the mailbox controller, mapped registers, and SoC config. `struct mtk_adsp_mbox_cfg` supplies set/clear register offsets. Ops are `mtk_adsp_mbox_send_data`, startup/shutdown, and `mtk_adsp_mbox_last_tx_done`; IRQ handling is split into a top half that clears output bits and a thread that reports data.

Control flow: probe allocates one channel, maps registers, selects match config, requests a threaded IRQ, and registers a poll-txdone mailbox. Startup and shutdown clear inbound/outbound command registers. TX writes the caller's `u32` to `set_in`; polling reports complete when `set_in` becomes zero. IRQ top half reads `set_out`, writes the same value to `clr_out`, and wakes the thread; the thread calls `mbox_chan_received_data(chan, NULL)`.

State and persistence: state is volatile MMIO only. The controller does not buffer payloads and has no persistent configuration beyond match offsets.

Dependencies and integration: depends on DT compatibles `mediatek,mt8186-adsp-mbox` and `mediatek,mt8195-adsp-mbox`, a single MMIO resource, one IRQ, and the generic mailbox framework.

Risks: xlate ignores mailbox specifier contents and always returns channel zero. TX done relies on remote firmware clearing `set_in`; broken firmware causes mailbox core timeouts.

Test signals: boot/probe on both register layouts, command clear on startup/shutdown, RX interrupt clear behavior, and timeout behavior when remote does not clear `set_in`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-adsp-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-cmdq-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-cmdq-mailbox.c

Purpose: implements the MediaTek GCE/CMDQ mailbox controller, where each mailbox channel represents a hardware command-queue thread executing DMA-backed `cmdq_pkt` command buffers for display/media clients.

Important APIs/types/functions: `struct cmdq`, `struct cmdq_thread`, `struct cmdq_task`, and `struct gce_plat` model controller, thread state, queued tasks, and SoC quirks. Exported helpers `cmdq_get_mbox_priv` and `cmdq_get_shift_pa` expose address conversion data. Key routines handle VM init, GCE control, thread suspend/resume/reset/disable, task chaining, IRQ completion, runtime PM, send, shutdown, flush, and xlate.

Control flow: probe maps GCE registers, gets clocks for one or more GCE blocks, initializes sync tokens, allocates thread/channel arrays, requests the shared IRQ, enables runtime PM, and registers a controller using client ACK txdone semantics. Xlate assigns thread priority from DT. Send allocates a `cmdq_task`, starts an idle thread with current/end addresses or suspends a busy thread and chains the new packet by rewriting the previous packet's final jump. IRQ handling finds threads with pending status, maps current GCE address back to DMA address, completes finished tasks via `mbox_chan_received_data` carrying `cmdq_cb_data`, handles errors, and disables empty threads.

State and persistence: task queues are per-thread `task_busy_list` entries protected by the channel lock; command buffers are DMA-synced and patched in memory. Runtime PM toggles GCE clocks and control bits; suspend records only a suspended flag and warns about live tasks.

Dependencies and integration: depends on DMA APIs, PM runtime, MediaTek CMDQ client packet format, GCE clocks, SoC match data for thread counts/address shifts/VM, and mailbox clients.

Risks: incorrect DMA address conversion or jump patching can execute wrong commands. Shutdown/flush must abort queued tasks exactly once. PM transitions with live tasks are risky and only warned.

Test signals: command completion/error IRQ tests, chained packet execution, flush while waiting in WFE, runtime suspend/resume, multi-GCE clock discovery, and SoC-specific address-shift validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-cmdq-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-gpueb-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-gpueb-mailbox.c

Purpose: implements the MediaTek GPUEB mailbox for MT8196-class systems, exposing named GPU embedded-controller channels with fixed TX/RX offsets and lengths.

Important APIs/types/functions: `struct mtk_gpueb_mbox`, `struct mtk_gpueb_mbox_chan`, `struct mtk_gpueb_mbox_chan_desc`, and `struct mtk_gpueb_mbox_variant` describe controller resources and channel layouts. Ops are send, startup, shutdown, and `last_tx_done`; IRQ handling uses a shared top half and threaded handler per channel.

Control flow: probe gets the prepared clock, maps data and control register windows, validates per-channel RX sizes, allocates channels, marks each blocked, and registers a poll-txdone controller. Startup clears RX status, enables the clock, clears pending IRQ for the channel, and requests a shared threaded IRQ. The top half checks RX status and atomically transitions the channel to full/blocked before waking the thread. The thread reads the fixed RX buffer into a stack buffer, clears the channel IRQ, calls `mbox_chan_received_data`, and releases the RX status. TX rejects sends while RX status is nonzero, writes 32-bit words to the channel TX window, and sets the IRQ bit. Txdone polls the TX status bit.

State and persistence: per-channel `rx_status` encodes blocked and full states; channel descriptors are static match data. No persistent storage exists.

Dependencies and integration: depends on MT8196 DT match data, two MMIO resources, a shared IRQ, one clock, and mailbox clients using the fixed channel payload sizes.

Risks: TX and RX share an atomic status gate, so long client callbacks can make TX return `-EBUSY`. The driver intentionally avoids bulk IO helpers for TX ordering; changing that can break hardware expectations.

Test signals: per-channel IRQ routing, RX-size validation, TX busy behavior, clock enable/disable on startup/shutdown, and txdone polling against `GPUEB_MBOX_CTL_TX_STS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-gpueb-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-vcp-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mtk-vcp-mailbox.c

Purpose: provides a single-channel MediaTek VCP mailbox controller for MT8196, transferring IPI messages through a fixed-size shared slot window and bit-indexed interrupt registers.

Important APIs/types/functions: `struct mtk_vcp_mbox` holds the controller, one channel, mapped base, config offsets, and an `mtk_ipi_info` receive buffer. `struct mtk_vcp_mbox_cfg` supplies `set_in` and `clr_out`. Ops are `mtk_vcp_mbox_send_data` and `mtk_vcp_mbox_last_tx_done`, with `mtk_vcp_mbox_xlate` enforcing zero cells.

Control flow: probe allocates one channel, an RX message buffer of `MTK_VCP_MBOX_SLOT_MAX_SIZE`, maps registers, gets match data, requests a threaded IRQ, and registers a poll-txdone controller. TX validates `mtk_ipi_info->msg`, checks whether the `set_in` bit for the IPI index is busy, bounds-checks slot offset plus length, copies the payload to IO memory, and sets the bit. The IRQ thread reads `clr_out` status, copies the full slot window into `ipi_recv.msg`, passes `ipi_recv` to the client, and clears the status bits. Txdone polls until the active request's bit in `set_in` clears.

State and persistence: runtime state is the receive scratch `ipi_recv` and active mailbox request pointer held by the core. Hardware slot contents are transient.

Dependencies and integration: depends on `linux/mailbox/mtk-vcp-mailbox.h`, one IRQ, one MMIO window, DT `mediatek,mt8196-vcp-mbox`, and clients that understand `mtk_ipi_info`.

Risks: `last_tx_done` dereferences `chan->active_req` as `mtk_ipi_info`; malformed clients can crash or mispoll. IRQ copies the full slot window regardless of reported status.

Test signals: busy-bit rejection, slot bounds validation, RX status clearing, txdone polling by IPI index, and zero-cell DT xlate checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mtk-vcp-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/omap-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/omap-mailbox.c

Purpose: implements the TI OMAP/K3 mailbox controller, mapping DT child mailbox descriptions to FIFO pairs with interrupt-driven RX and TX-ready completion.

Important APIs/types/functions: `struct omap_mbox_device` stores shared MMIO, IRQ context, user/fifo counts, and SoC interrupt layout. `struct omap_mbox` stores one logical channel's TX/RX FIFO register offsets, IRQ, and `send_no_irq` mode. Core functions read/write FIFOs, enable/disable/ack IRQ bits, handle startup/shutdown, send, suspend/resume, and OF xlate by child phandle.

Control flow: probe reads `ti,mbox-num-users` and `ti,mbox-num-fifos`, parses each child `ti,mbox-tx`/`ti,mbox-rx` tuple into FIFO/IRQ registers, registers a txdone-IRQ controller, and prints the hardware revision under runtime PM. Startup powers the device, requests a threaded shared IRQ, optionally switches the channel to client-ACK txdone for `ti,mbox-send-noirq`, and enables RX IRQ. Normal send writes one 32-bit word if the TX FIFO is not full and enables TX IRQ; TX interrupt disables TX IRQ, acks, and reports txdone. RX interrupt drains all messages and delivers each word to the client.

State and persistence: per-channel FIFO register mapping is built from DT and remains for device lifetime. Runtime PM gates the shared block. System sleep saves IRQ enable registers and can reject suspend if exclusive hardware has unread messages.

Dependencies and integration: depends on OMAP/K3 mailbox DT bindings, runtime PM, generic mailbox framework, and shared IRQ behavior. Supports OMAP2/3/4 and AM64/AM654 interrupt layouts.

Risks: `send_no_irq` path writes then locally reads/acks RX state and changes txdone semantics, so clients must be designed for that mode. Child DT tuple mistakes can route messages to wrong FIFOs.

Test signals: child xlate by phandle, RX FIFO draining, TX FIFO full retry, runtime/system suspend restore, and both interrupt config types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/omap-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/pcc.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/pcc.c

Purpose: implements ACPI Platform Communication Channel as a mailbox controller, allowing clients such as CPPC/RAS/MPST to coordinate with firmware/platform controllers through ACPI-described shared memory and doorbell registers.

Important APIs/types/functions: `struct pcc_chan_info` wraps `struct pcc_mbox_chan`, doorbell/ACK/complete/error registers, IRQ metadata, subspace type, and in-use state. Exported APIs `pcc_mbox_request_channel` and `pcc_mbox_free_channel` map shared memory and bind/free mailbox clients. Internal helpers parse PCCT subspaces, initialize GAS registers, ring doorbells, poll completion, handle IRQs, and acknowledge slave subspace notifications.

Control flow: `pcc_init` checks ACPI PCCT and creates a platform bundle early. Probe walks PCCT entries, allocates channels, configures txdone by global doorbell flag, parses optional platform IRQs, doorbell/complete/update/error registers, and shared-memory metadata, then registers the controller. A client requests a subspace by id, the driver maps the shared memory region, and binds the channel. Send updates command-complete state then rings the doorbell; IRQ acknowledges platform IRQ, validates complete/error state, clears `chan_in_use`, reports RX and txdone, and performs slave-subspace acknowledgement.

State and persistence: global `chan_info` and `pcc_chan_count` describe ACPI subspaces. Shared memory is mapped per requested channel and unmapped on free. Register virtual addresses are cached for performance.

Dependencies and integration: depends on ACPI PCCT, ACPI GAS read/write, GSI mapping, mailbox framework, and `include/acpi/pcc.h` client contracts.

Risks: malformed PCCT register widths, missing ACK registers on level IRQs, or wrong subspace type handling can cause stuck firmware communication. Polling completion without IRQ depends entirely on command-complete semantics.

Test signals: ACPI table parsing for every PCCT type, request/free shared-memory mapping, IRQ and polling completion paths, error-status clear handling, and CPPC/RAS client boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/pcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/pl320-ipc.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/pl320-ipc.c

Purpose: implements legacy ARM PL320 IPC support for Calxeda-style A9/M3 communication. It is not a generic `mbox_controller`; it exports blocking transmit and atomic notifier APIs directly.

Important APIs/types/functions: exported functions are `pl320_ipc_transmit`, `pl320_ipc_register_notifier`, and `pl320_ipc_unregister_notifier`. Static globals hold `ipc_base`, IRQ number, transmit mutex, completion, and `ATOMIC_NOTIFIER_HEAD`. Helpers `__ipc_send` and `__ipc_rcv` move seven 32-bit data registers.

Control flow: AMBA probe maps the PL320 resource, clears TX send state, requests the IRQ, initializes TX mailbox source/destination/mask registers, and initializes RX mailbox routing. `pl320_ipc_transmit` serializes with a mutex, sends seven words through mailbox 1, waits up to 1 second for the IRQ completion, then reads the response and returns `data[1]` as status. The IRQ handler completes TX when mailbox 1 fires and handles RX mailbox 2 by reading data, calling the atomic notifier chain with `data[0]` as event and `data + 1` as payload, then acknowledging.

State and persistence: global singleton state reflects one PL320 block. Runtime state includes a single blocking TX transaction and notifier subscribers; nothing persists after reboot.

Dependencies and integration: depends on AMBA device id `0x00041320`, PL320 register layout, completion/mutex/notifier APIs, and platform code that calls the exported functions.

Risks: singleton globals prevent multiple instances. Blocking transmit is explicitly unusable in interrupt context. No remove path frees IRQ or mapping, matching old init-only usage.

Test signals: AMBA probe, TX timeout and response status, RX notifier ordering, and concurrent transmit serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/pl320-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/platform_mhu.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/platform_mhu.c

Purpose: implements a simple platform ARM MHU-style mailbox for Amlogic Meson GXBB, exposing three channels for secure, low-priority, and high-priority interrupt lines.

Important APIs/types/functions: `struct platform_mhu` contains the MMIO base, three `platform_mhu_link` records, three channels, and controller. Ops are `platform_mhu_send_data`, startup/shutdown, and `platform_mhu_last_tx_done`; `platform_mhu_rx_interrupt` handles incoming data.

Control flow: probe maps the register resource, assigns each channel an IRQ and RX/TX register pair using fixed offsets, then registers a poll-txdone controller. Startup clears any stale TX status and requests the channel IRQ. TX writes the caller's `u32` to `INTR_SET_OFS` in the TX register bank. RX IRQ reads `INTR_STAT_OFS`, reports the status word via `mbox_chan_received_data`, and clears it. Txdone polls the TX status register until zero.

State and persistence: all channel state is in fixed MMIO status bits and per-channel link descriptors. No payload buffering or persistent data exists.

Dependencies and integration: depends on DT compatible `amlogic,meson-gxbb-mhu`, three IRQ resources, one MMIO resource, and mailbox clients that use 32-bit status words.

Risks: fixed three-channel layout assumes register spacing exactly matches the hardware. RX passes a pointer to a stack-local `u32`; clients must consume synchronously inside the callback, as expected by mailbox semantics.

Test signals: probe with all three IRQs, TX status polling, RX clear behavior, shared client callback correctness, and DT binding resource order tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/platform_mhu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/qcom-apcs-ipc-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/qcom-apcs-ipc-mailbox.c

Purpose: implements Qualcomm APCS IPC doorbell mailboxes for many Qualcomm SoCs. It exposes 32 bit-indexed channels that send a single bit to an APCS/global register and optionally registers a related APCS clock-controller child device.

Important APIs/types/functions: `struct qcom_apcs_ipc` stores the mailbox controller, 32 channels, regmap, IPC offset, and optional clock platform device. `struct qcom_apcs_ipc_data` supplies SoC-specific offset and clock-controller name. `qcom_apcs_ipc_send_data` is the only mailbox op.

Control flow: probe maps MMIO, wraps it in a regmap, reads match data, assigns each channel's `con_priv` to its bit index, registers the mailbox controller, and optionally creates a clock-controller platform device using either a child `clock-controller` node or the APCS node fwnode. Sending writes `BIT(index)` to the configured offset. Remove unregisters the optional clock child.

State and persistence: no RX or txdone state is tracked. The only persistent runtime object beyond the controller is the optional clock platform device.

Dependencies and integration: depends on numerous Qualcomm DT compatibles, regmap-mmio, mailbox framework default index xlate, and platform clock-controller drivers that bind to the created child.

Risks: the controller has no completion or RX path; clients must treat sends as fire-and-forget. Match-data offsets are SoC-specific and wrong reuse can ring the wrong doorbell; the source contains an explicit warning not to add more entries using existing data blindly.

Test signals: compatible-specific offset tests, child clock-controller registration, one-shot bit writes for all channel indices, and probe/remove with and without clock child nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/qcom-apcs-ipc-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/qcom-cpucp-mbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/qcom-cpucp-mbox.c

Purpose: implements the Qualcomm APSS CPUCP mailbox for X1E80100, exposing three IPC channels between APSS and CPUCP with separate TX and RX register spaces.

Important APIs/types/functions: `struct qcom_cpucp_mbox` owns three channels, controller, TX base, and RX base. `channel_number` derives the channel index. Ops are startup, shutdown, and send; `qcom_cpucp_mbox_irq_fn` handles RX interrupts.

Control flow: probe maps RX and TX windows, clears RX enable/clear/map registers, requests a high-triggered no-suspend IRQ, enables RX command mapping, and registers the controller. Startup sets the RX enable bit for the channel; shutdown clears it. TX writes one `u32` command to the per-channel TX command register. IRQ reads the 64-bit RX status, iterates supported channel bits, reads each command value, locks the channel to synchronize with `chan->cl`, delivers data only if a client is bound, clears the RX bit, and unlocks.

State and persistence: hardware enable/map/status registers hold live state. The driver stores no per-message data and no persistent settings.

Dependencies and integration: depends on DT `qcom,x1e80100-cpucp-mbox`, two MMIO resources, one IRQ, and the mailbox controller framework.

Risks: RX status is treated as a bitset limited to three channels; wider unexpected bits are ignored. The IRQ passes a stack-local `u32` pointer synchronously. There is no txdone indication, so sends are fire-and-forget.

Test signals: channel enable/disable on request/free, IRQ delivery with and without a bound client, RX clear ordering, and register-window ordering in DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/qcom-cpucp-mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/qcom-ipcc.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/qcom-ipcc.c

Purpose: implements Qualcomm IPCC as both an IRQ controller for received client/signal pairs and an optional mailbox controller for sending IPCC signals described by DT `mboxes` properties.

Important APIs/types/functions: `struct qcom_ipcc` owns MMIO base, IRQ domain, dynamically sized mailbox channels, per-channel client/signal info, and summary IRQ. `qcom_ipcc_get_hwirq` encodes client/signal into a hardware IRQ. Key functions include IRQ domain map/xlate, mask/unmask, summary IRQ dispatch, mailbox send/xlate/shutdown, mbox setup, PM resume, probe/remove.

Control flow: probe maps registers, disables firmware-set clear-on-read mode if present, creates an IRQ domain, scans all available DT nodes with `mboxes` references to count channels targeting this controller, registers a mailbox controller if needed, and requests the summary IRQ. Summary IRQ repeatedly reads `RECV_ID` until no pending IRQ, clears each signal, finds the Linux virq, and calls `generic_handle_irq`. Mailbox xlate allocates a free channel for a unique client/signal pair; send writes the encoded pair to `SEND_ID`.

State and persistence: IRQ domain mappings persist while bound. Mailbox channel `con_priv` is allocated per requested client/signal and cleared on shutdown. Hardware receive enable/disable state is managed by IRQ chip callbacks.

Dependencies and integration: depends on DT interrupt-controller and mailbox bindings, generic IRQ domain APIs, mailbox framework, and early `arch_initcall` registration.

Risks: `generic_handle_irq` is called even if mapping lookup returns zero; valid DT interrupt mappings are required. Mailbox channels are sized by scanning existing DT clients, so late/unusual clients cannot exceed that count.

Test signals: IRQ domain xlate for three-cell specs, mailbox duplicate-pair rejection, summary IRQ dispatch/clear loop, suspend resume pending logging, and no-client mailbox skip path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/qcom-ipcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/riscv-sbi-mpxy-mbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/riscv-sbi-mpxy-mbox.c

Purpose: implements the RISC-V SBI Message Proxy mailbox controller. It discovers SBI MPXY channels, exposes RPMI-compatible channels to Linux mailbox clients, manages per-CPU SBI shared memory, and optionally wires channel notifications through platform MSIs.

Important APIs/types/functions: SBI attribute structures model standard MPXY, MSI, RPMI, channel-id, and notification data. `struct mpxy_local` is per-CPU shared memory state. `struct mpxy_mbox_channel` and `struct mpxy_mbox` hold discovered channel metadata, notification buffers, MSI mappings, and the mailbox controller. Helpers wrap SBI calls for channel IDs, attributes, message send, notifications, and shared-memory setup.

Control flow: probe checks SBI version and MPXY extension, gets shared-memory size, registers a CPU hotplug state to set per-CPU shared memory, discovers channels, reads standard and RPMI attributes, allocates notification buffers, computes max transfer sizes, configures MSI indexes for notification-capable channels, initializes platform MSI IRQs if needed, and registers a firmware-xlate mailbox controller. Send handles RPMI get/set attribute and request/response message types by issuing SBI calls through this CPU's shared memory. `peek_data` drains notification events and converts RPMI events into mailbox RX callbacks. Startup enables per-channel MSI and event state; shutdown disables them.

State and persistence: per-CPU shared memory remains active across CPU power-down by design. Channel attributes cache firmware state and track MSI/event enablement and `started`.

Dependencies and integration: depends on SBI MPXY extension, RPMI mailbox message ABI, CPU hotplug, RISC-V IMSIC/platform MSI domains, OF or ACPI match, and generic mailbox fwnode xlate.

Risks: shared-memory operations are CPU-local and guarded with `get_cpu`; misuse outside that pattern can corrupt SBI buffers. Notification parsing bounds are delicate. MSI domain availability can defer probe.

Test signals: SBI error mapping, channel discovery with multiple pages of IDs, RPMI send-with/without-response, notification draining by MSI and polling, CPU hotplug shared-memory setup, and OF/ACPI xlate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/riscv-sbi-mpxy-mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/rockchip-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/rockchip-mailbox.c

Purpose: implements the Rockchip RK3368 mailbox used for CPU-to-MCU communication, exposing four channels with command/data register pairs and per-channel B2A IRQs.

Important APIs/types/functions: `struct rockchip_mbox_msg` contains command and expected RX size. `struct rockchip_mbox_chan` tracks channel index, IRQ, in-flight message pointer, and parent. `struct rockchip_mbox` owns controller, clock, MMIO base, buffer size, and flexible channel array. Ops are send, startup, and shutdown; IRQ handling is split top/thread.

Control flow: probe allocates controller and channel arrays, maps MMIO, computes per-direction buffer size from resource size, enables `pclk_mailbox`, requests a threaded IRQ per channel, and registers a txdone-IRQ controller. Startup enables all B2A interrupts. Send validates the message and RX size, stores the message pointer in the channel state, writes command and RX size to A2B registers, and returns. Top-half IRQ checks B2A status for the matching channel, clears the bit, and wakes the thread. The threaded handler retrieves the stored message, calls `mbox_chan_received_data` with it, and clears the in-flight pointer.

State and persistence: the current message pointer is stored per channel until the B2A interrupt arrives. Clock enable persists while the device is bound; there is no remove clock-disable path in this file.

Dependencies and integration: depends on DT `rockchip,rk3368-mailbox`, one clock, per-channel IRQ resources, and mailbox clients using `rockchip_mbox_msg`.

Risks: send uses `struct rockchip_mbox_chan *chans = mb->chans` and then `chans->idx`, effectively channel zero, instead of deriving the channel from `chan`; this is a likely multi-channel bug. No txdone callback is issued despite `txdone_irq = true`.

Test signals: multi-channel send/interrupt tests, clock lifecycle checks, RX size validation, and mailbox-core timeout behavior for clients expecting txdone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/rockchip-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/sprd-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/sprd-mailbox.c

Purpose: implements Spreadtrum/Unisoc mailbox controllers with an inbox for TX and one or more outboxes for RX, supporting R1 and R2 FIFO/status layouts and up to 16 channels.

Important APIs/types/functions: `struct sprd_mbox_priv` owns controller, inbox/outbox/supplementary MMIO, FIFO depth, match info, reference count, lock, and channels. `struct sprd_mbox_info` identifies hardware revision and supplementary outbox id. Core functions compute FIFO length, handle outbox/supplementary RX, handle inbox txdone IRQs, send two-word messages, flush by polling busy bits, startup/shutdown shared interrupt masks, and probe.

Control flow: probe maps inbox and outbox resources, enables clock, requests inbox/outbox IRQs and optional supplementary outbox IRQ, reads FIFO depth, initializes channel ids, and registers a txdone-IRQ mailbox. Startup increments a shared refcount and on first user resets/enables outbox and inbox interrupt masks. Sending writes two `u32` words and target id to inbox registers then triggers. Inbox IRQ clears delivery/overflow status, checks busy bits per delivered channel, and calls `mbox_chan_txdone` when the target fetched the message. Outbox IRQ calculates FIFO length, drains messages, routes each by message id to a channel callback if bound, advances the FIFO pointer, and clears IRQ status.

State and persistence: shared interrupt enable state is refcounted across channels. Hardware FIFOs hold transient TX/RX state; no persistent data exists.

Dependencies and integration: depends on Unisoc DT compatibles, named inbox/outbox/supp-outbox IRQs, enabled clock, mailbox framework, and revision-specific register semantics.

Risks: outbox message id directly indexes `priv->chan` without explicit bounds check. R1/R2 status differences make regressions easy. Flush uses jiffies plus microsecond polling and only the R1 busy mask.

Test signals: R1 and R2 hardware coverage, supplementary outbox routing, FIFO wrap/full length computation, txdone IRQ and flush paths, and dropped-message logging when no client is bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/sprd-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/stm32-ipcc.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/stm32-ipcc.c

Purpose: implements the STM32MP1 IPCC mailbox controller for two processors, exposing hardware channels where TX sets a channel occupied bit and RX observes the other processor's occupied state.

Important APIs/types/functions: `struct stm32_ipcc` stores controller, base/proc register pointers, clock, lock, IRQs, processor id, channel count, and suspend register context. Ops are `stm32_ipcc_send_data`, startup, and shutdown. IRQ handlers `stm32_ipcc_rx_irq` and `stm32_ipcc_tx_irq` deliver RX events and txdone.

Control flow: probe reads `st,proc-id`, maps registers, enables the clock, requests threaded RX/TX IRQs, masks all channel IRQs, enables RX/TX output interrupt generation, configures optional wake IRQ, reads hardware channel count, initializes channel ids, registers a txdone-IRQ controller, logs version, and disables the clock until channel startup. Startup enables the clock and unmasks RX occupied IRQ for the channel. Send sets the TX occupied bit and unmasks TX-free IRQ. RX IRQ finds unmasked occupied channels from the other processor, calls `mbox_chan_received_data(chan, NULL)`, then sets the RX clear bit. TX IRQ finds unmasked free channels, masks the TX-free interrupt, and calls `mbox_chan_txdone`.

State and persistence: channel masks and control registers are hardware state; suspend stores/restores `XMR` and `XCR`. Clock is enabled per active channel but without a refcount in this driver.

Dependencies and integration: depends on STM32 DT compatible, `st,proc-id`, RX/TX named IRQs, clock, wakeirq support, and mailbox framework.

Risks: multiple simultaneous channel users call `clk_prepare_enable`/`clk_disable_unprepare` independently without explicit refcounting in driver code. RX carries no payload, so protocol state lives in clients/shared memory.

Test signals: proc-id validation, RX/TX IRQ behavior per channel, wakeup-source suspend/resume, channel count from HWCFGR, and multi-channel clock lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/stm32-ipcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/sun6i-msgbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/sun6i-msgbox.c

Purpose: implements the Allwinner sun6i/sun8i/sun9i/sun50i message box, exposing eight channels whose directions are preconfigured by firmware and whose messages are 32-bit FIFO entries.

Important APIs/types/functions: `struct sun6i_msgbox` owns controller, clock, spinlock, and register base. Ops are send, startup, shutdown, `last_tx_done`, and `peek_data`; `sun6i_msgbox_irq` drains RX FIFOs.

Control flow: probe allocates eight channels, enables the clock, deasserts reset without ever reasserting it, maps MMIO, disables local IRQs, requests the IRQ, and registers a poll-txdone controller. Startup checks if the channel is configured as RX, flushes stale FIFO data, clears IRQ status, and enables the RX IRQ bit under lock. TX validates that hardware marks the channel as TX, writes the 32-bit message to the data register, and relies on remote IRQ status for completion. IRQ intersects enabled and pending local IRQ bits, drains each RX FIFO while `peek_data` reports data, passes each word to the client, and clears the IRQ once the FIFO is empty. Shutdown disables RX IRQ and repeatedly drains/clears until pending status is gone.

State and persistence: channel direction is firmware-owned hardware state. Local IRQ enable is protected by a spinlock. The reset line remains deasserted after probe because firmware may share the block.

Dependencies and integration: depends on DT compatible `allwinner,sun6i-a31-msgbox`, clock, reset, one IRQ, mailbox clients, and firmware channel-direction setup.

Risks: using a channel backwards can put hardware into a bad state; the driver warns and drops TX. Probe uses `irq_of_parse_and_map` directly. Shared firmware ownership makes reset/error recovery intentionally conservative.

Test signals: firmware direction matrix, RX FIFO flush and IRQ clear loops, txdone polling via remote IRQ status, reset failure handling, and concurrent RX IRQ enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/sun6i-msgbox.c -->
