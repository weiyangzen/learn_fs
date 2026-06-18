# subset-b-004016 research

This grouped report covers mailbox controller drivers under `sources/distributed-fs/ceph-client/drivers/mailbox`. Each section preserves the original source path so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv3.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv3.c

## Purpose
`arm_mhuv3.c` implements the ARM Message Handling Unit v3 mailbox controller. It discovers whether the mapped frame is a PBX sender or MBX receiver, validates the architectural revision, discovers supported extensions, and currently exposes the Doorbell Extension (DBE) as Linux mailbox channels.

## Important APIs, Types, and Functions
The main private types are `struct mhuv3`, `struct mhuv3_extension`, `struct mhuv3_mbox_chan_priv`, and `struct mhuv3_protocol_ops`. Register layouts are represented with packed structs for the control page and PBX/MBX doorbell channel windows. Core entry points are `mhuv3_probe()`, `mhuv3_frame_init()`, `mhuv3_irqs_init()`, `mhuv3_initialize_channels()`, and `mhuv3_mbox_of_xlate()`. Doorbell behavior is implemented by `mhuv3_doorbell_send_data()`, `mhuv3_doorbell_last_tx_done()`, startup/shutdown helpers, and the combined IRQ lookup helpers.

## Control Flow
Probe maps the MMIO resource, reads `blk_id` to select PBX or MBX mode, verifies the MHU major version, optionally requests AutoOp full mode, initializes supported extensions, sets IRQ behavior, allocates mailbox channels, and registers the controller. DBE initialization creates one Linux channel for every hardware doorbell bit in every DB channel window. PBX frames send by setting a doorbell bit, then either poll or receive a combined transfer-ack interrupt. MBX frames require a combined IRQ, inspect combined DBCH status, deliver optional data, call `mbox_chan_received_data()`, and clear the doorbell to acknowledge.

## State and Persistence
State is devm-managed and lasts for the platform-device lifetime. `pending_db[]` tracks in-flight PBX doorbells and is protected by `pending_lock`; it is cleared on TX shutdown and when completions are observed. AutoOp full mode is undone by a devm cleanup action that clears `op_req`. There is no persistent storage across probe/remove.

## Dependencies and Integration Points
The driver integrates with platform devices, OF mailbox specifiers with three cells `(extension type, channel window, parameter)`, MMIO register access, Linux mailbox core, IRQ handling, spinlocks, and ARM MHUv3 hardware. It only implements DBE; FCE and FE support is detected but logged as unsupported by this driver.

## Risks and Edge Cases
The channel count can grow to `num_dbch * 32`, so DT specifier validation and channel allocation must stay consistent. PBX operation without a combined IRQ relies on polling and accurate `last_tx_done()`. MBX operation fails probe if the combined IRQ is missing. The source contains duplicated local declarations/comments in a few places, which should be caught by compile coverage. Interrupt lookup reports spurious status when pending doorbell state and hardware status disagree.

## Test Signals
Useful signals include OF probing for `arm,mhuv3`, compile coverage for packed register access, successful PBX polling and IRQ modes, MBX combined IRQ delivery, `mbox_chan_txdone()` on TX ack, `mbox_chan_received_data()` on RX doorbells, bad phandle-cell rejection, and suspend/remove cleanup that clears AutoOp state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/armada-37xx-rwtm-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/armada-37xx-rwtm-mailbox.c

## Purpose
`armada-37xx-rwtm-mailbox.c` provides a single-channel mailbox for the Armada 37xx rWTM BIU secure processor interface. It writes command arguments to mailbox parameter registers and reports secure processor return/status words to clients.

## Important APIs, Types, and Functions
`struct a37xx_mbox` stores the device, mailbox controller, MMIO base, and IRQ. `a37xx_mbox_send_data()` accepts `struct armada_37xx_rwtm_tx_msg`, writes 16 argument words and a command word, and checks FIFO readiness/fullness. `a37xx_mbox_receive()` builds `struct armada_37xx_rwtm_rx_msg` from return/status registers. `a37xx_mbox_irq_handler()`, `a37xx_mbox_startup()`, and `a37xx_mbox_shutdown()` manage completion interrupts.

## Control Flow
Probe allocates one channel, maps the register resource, obtains the IRQ, initializes mailbox core state with `txdone_irq = true`, and registers the controller. Startup requests the IRQ and unmasks command-complete and queue-full interrupts. Send checks for null data, warns if the secure processor is not ready, rejects a full FIFO with `-EBUSY`, writes arguments, and posts the command. The IRQ handler reads interrupt status, receives response data on `SP_CMD_COMPLETE`, logs queue-full errors, clears status by writing it back, and reports TX completion.

## State and Persistence
All driver state is devm-managed per platform device. Runtime interrupt mask state is enabled on startup and disabled on shutdown. No command queue is mirrored in software; clients are expected to serialize through the mailbox framework and hardware FIFO status.

## Dependencies and Integration Points
The driver depends on the Linux mailbox core, platform MMIO/IRQ helpers, OF compatible `marvell,armada-3700-rwtm-mailbox`, and the public message structs from `include/linux/armada-37xx-rwtm-mailbox.h`.

## Risks and Edge Cases
The hardware has only one channel and a small FIFO depth, so clients must handle `-EBUSY`. Startup uses devm IRQ request/free on channel open/close, so repeated open/close paths should be tested. Queue-full interrupt bits are logged but do not synthesize a data response. Secure processor "not ready" is only a warning before attempting the command.

## Test Signals
Test signals include command/response round trips with all 16 argument/status words, queue-full handling, IRQ mask toggling on startup/shutdown, no IRQ behavior after shutdown, and DT probe failures for missing MMIO or IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/armada-37xx-rwtm-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/ast2700-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/ast2700-mailbox.c

## Purpose
`ast2700-mailbox.c` implements the ASPEED AST2700 IPC mailbox with four fixed channels and 32-byte messages. It exposes RX interrupt delivery and TX polling completion through the mailbox framework.

## Important APIs, Types, and Functions
`struct ast2700_mbox_data` describes channel count and message size. `struct ast2700_mbox` holds the controller, TX/RX MMIO regions, message size, and an RX-enable spinlock. `ast2700_mbox_irq()` receives messages, `ast2700_mbox_send_data()` writes data and triggers TX, and `ast2700_mbox_startup()`/`shutdown()` update per-channel RX enable bits.

## Control Flow
Probe reads match data, allocates channels and a per-channel receive buffer stored in `chan->con_priv`, maps named `tx` and `rx` resources, requests the shared IRQ, enables TX-done polling, and registers the controller. Startup sets the channel bit in RX `IPCR_ENABLE`; shutdown clears it. Send checks that the TX channel is enabled, verifies the previous TX is done by testing `IPCR_STATUS`, writes eight 32-bit words into the channel data window, and writes `IPCR_TX_TRIG`. The IRQ path masks status with enabled channels, copies each pending channel's data into its private buffer, calls `mbox_chan_received_data()`, and clears the status bit after the FIFO is empty.

## State and Persistence
The only persistent runtime state is the per-channel receive buffer, MMIO enable bits, and the lock protecting read-modify-write updates to `IPCR_ENABLE`. No messages are queued in software.

## Dependencies and Integration Points
The driver integrates with OF compatible `aspeed,ast2700-mailbox`, named MMIO resources, platform IRQs, and the mailbox core. It uses poll-based TX completion (`txpoll_period = 5`) rather than TX interrupts.

## Risks and Edge Cases
`send_data()` assumes the caller supplies at least `msg_size` bytes. RX status is limited by `RX_IRQ_MASK`, so data and hardware match data must agree on the number of channels. Clients must handle `-ENODEV` for disabled channels and `-EBUSY` while previous TX data is still pending. IRQ clearing depends on the FIFO-empty condition described in the source comment.

## Test Signals
Validate all four channels independently, concurrent startup/shutdown RMW locking, fixed 32-byte payload transfer, TX busy behavior, RX IRQ handling only for enabled channels, and DT/resource failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/ast2700-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-flexrm-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm-flexrm-mailbox.c

## Purpose
`bcm-flexrm-mailbox.c` turns Broadcom FlexRM hardware rings into mailbox channels for FlexSparx4 offload engines. Each ring is a channel that accepts Broadcom mailbox messages and writes FlexRM descriptor packets, with completions reported through MSI-backed ring completion queues.

## Important APIs, Types, and Functions
`struct flexrm_mbox` owns mapped ring registers, ring array, DMA pools, debugfs entries, and the mailbox controller. `struct flexrm_ring` tracks one ring's registers, IRQ, descriptor and completion buffers, request bitmap, in-flight messages, and counters. Descriptor helpers build header, null, next-table, SRC/DST/MSRC/MDST/IMM/TLAST descriptors. Message paths include `flexrm_sanity_check()`, `flexrm_dma_map()`, `flexrm_write_descs()`, `flexrm_new_request()`, `flexrm_process_completions()`, and mailbox callbacks `flexrm_send_data()`, `flexrm_startup()`, `flexrm_shutdown()`, and `flexrm_peek_data()`.

## Control Flow
Probe maps the register range, scans for rings by `RING_VER_MAGIC`, allocates ring state, sets a 40-bit or fallback 32-bit DMA mask, creates DMA pools, allocates platform MSIs, optionally creates debugfs `config` and `stats`, and registers one mailbox channel per ring. Startup allocates descriptor and completion rings, seeds next-table/null descriptors, requests the ring IRQ, programs ring base addresses/MSI settings, clears counters, and activates the ring. Send validates `brcm_message` content, allocates a request ID, DMA maps SPU scatterlists when needed, checks descriptor space against the hardware read pointer, writes descriptors, flips the first header toggle after a write barrier, and advances the software write offset. Completion processing reads the completion write pointer, decodes error status and request ID, unmaps DMA, releases the bitmap slot, returns the original message with `msg->error`, and updates stats.

## State and Persistence
Ring state is volatile and is rebuilt on channel startup. In-flight request pointers live in `ring->requests[]`, with allocation tracked by `requests_bmap`. Descriptor memory and completion memory are allocated from DMA pools per startup and freed on shutdown. Debugfs stats are runtime counters only.

## Dependencies and Integration Points
The driver depends on `linux/mailbox/brcm-message.h` message formats, DMA mapping and pools, platform MSI allocation, debugfs, OF compatible `brcm,iproc-flexrm-mbox`, and Linux mailbox callbacks. DT mailbox args select ring index, MSI count threshold, and MSI timer value.

## Risks and Edge Cases
Descriptor accounting is the main risk: packet extension headers, next-table descriptors, toggle bits, and wraparound must remain consistent. Completion descriptors with bad DME/RM status translate to `-EIO` or `-ETIMEDOUT`. Shutdown aborts in-flight messages with `-EIO`. The source contains duplicated declarations/log calls in a few locations that should be caught by compile testing. Batch messages can partially queue and return an error with `msgs_queued` updated.

## Test Signals
Test SPU and SBA message sanity checks, scatterlist DMA map/unmap, descriptor wraparound, MSI completion processing, batch partial failure, debugfs output, ring startup/shutdown/flush, invalid DT args, and error completion descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-flexrm-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-pdc-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm-pdc-mailbox.c

## Purpose
`bcm-pdc-mailbox.c` implements the Broadcom PDC/MDE/FA2 mailbox controller for SPU offload engines. It maps `BRCM_MESSAGE_SPU` scatterlists into paired TX and RX DMA descriptor rings and reports responses back through the mailbox framework.

## Important APIs, Types, and Functions
`struct pdc_state` is the central state object, holding platform state, DMA registers, descriptor rings, ring indexes, response metadata buffers, mailbox controller, work item, counters, and hardware type. Important functions include `pdc_probe()`, `pdc_hw_init()`, `pdc_ring_init()`, `pdc_send_data()`, `pdc_rx_list_init()`, `pdc_rx_list_sg_add()`, `pdc_tx_list_sg_add()`, `pdc_tx_list_final()`, `pdc_irq_handler()`, `pdc_work_cb()`, `pdc_receive()`, and `pdc_receive_one()`.

## Control Flow
Probe allocates state, sets a 39-bit DMA mask, creates DMA pools, reads DT properties (`brcm,rx-status-len`, optional `brcm,use-bcm-hdr`, compatible-selected hardware type), maps registers, creates response-header buffers, initializes DMA control registers, sets up bottom-half work and interrupts, registers a one-channel mailbox, and creates debugfs stats. Channel startup allocates and programs TX/RX descriptor rings for ringset 0. Send only accepts SPU messages, DMA maps source and destination scatterlists, checks ring capacity, posts a receive metadata descriptor plus destination descriptors, posts source descriptors, then writes RX and TX hardware pointer registers to start transfer. The hard IRQ disables and clears device interrupts, queues work, and the work callback reclaims available response frames and reenables interrupts.

## State and Persistence
Ring indexes (`txin`, `txout`, `rxin`, `rxout`, `last_rx_curr`) and per-message descriptor counts persist while the channel is active. `rx_ctx[]`, `src_sg[]`, and `txin_numd[]` tie completions to original scatterlists and opaque client context. Debugfs counters persist for the device lifetime but not across driver reload.

## Dependencies and Integration Points
The driver depends on Broadcom SPU message definitions, scatterlist DMA mapping, DMA pools, workqueues, debugfs, OF IRQ/resource APIs, and mailbox polling for backpressure (`last_tx_done()` checks descriptor headroom). Compatibles are `brcm,iproc-pdc-mbox` and `brcm,iproc-fa2-mbox`.

## Risks and Edge Cases
Ring-space checks must prevent partial descriptor sequences; however, several send-error paths after DMA mapping require careful unmap review. Response length/overflow handling differs for SPU-M headers. `last_tx_done()` uses conservative free-space thresholds and increments statistics when rings are low. The global debugfs root is shared across instances. Multiple descriptor splitting for buffers over 16 KiB must keep EOT/SOF/EOF/IOC flags correct.

## Test Signals
Exercise SPU request/reply with multi-entry scatterlists, buffers larger than `PDC_DMA_BUF_MAX`, RX overflow/zero-length responses, FA2 versus PDC lazy interrupt offsets, backpressure via `last_tx_done()`, channel startup/shutdown ring allocation, debugfs counters, and removal while deferred work may be queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-pdc-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm2835-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm2835-mailbox.c

## Purpose
`bcm2835-mailbox.c` implements the Raspberry Pi/BCM2835 ARM-to-VideoCore mailbox channel. It exposes one mailbox channel that writes requests to mailbox 1 and receives replies from mailbox 0.

## Important APIs, Types, and Functions
`struct bcm2835_mbox` contains the MMIO base, a spinlock, and the controller. `bcm2835_send_data()` writes a 32-bit request, `bcm2835_mbox_irq()` drains received replies, `bcm2835_last_tx_done()` checks the TX FIFO-full bit, and startup/shutdown enable or disable receive interrupts.

## Control Flow
Probe allocates state, requests the DT IRQ with `IRQF_NO_SUSPEND`, maps registers, configures polling TX completion, allocates one channel, registers the mailbox controller, and logs that the mailbox is enabled. Startup writes `ARM_MC_IHAVEDATAIRQEN` to enable data interrupts. Send locks around the mailbox write and logs the request. The IRQ handler loops while the receive FIFO is not empty, reads each 32-bit word, and passes it to `mbox_chan_received_data()`. Shutdown clears interrupt enable.

## State and Persistence
The driver keeps no software queue. The spinlock serializes writes and TX status checks against concurrent clients. Hardware FIFO state is the source of truth for completion readiness.

## Dependencies and Integration Points
The driver uses OF IRQ/address helpers, platform MMIO mapping, the mailbox core, and compatible `brcm,bcm2835-mbox`. Clients typically use the firmware property interface format carried in the 32-bit mailbox word.

## Risks and Edge Cases
`send_data()` does not itself test FIFO fullness; the mailbox core is expected to call `last_tx_done()` and clients must tolerate busy behavior. IRQ request uses `irq_of_parse_and_map()` directly. Only one channel is exposed, and the OF xlate rejects any phandle arguments.

## Test Signals
Validate firmware property round trips, repeated IRQ draining of multiple replies, TX polling under full FIFO, startup/shutdown interrupt enable bits, no-suspend IRQ behavior, and invalid phandle argument rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm2835-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm74110-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm74110-mailbox.c

## Purpose
`bcm74110-mailbox.c` implements a Broadcom BCM74110 mailbox with an initialization service, link-training handshake, shared-memory setup, and service channels for PMC, SCMI, and DPFE notifications.

## Important APIs, Types, and Functions
Message layout is encoded by `struct bcm74110_mbox_msg` and `BCM_MSG_*` field macros. `struct bcm74110_mbox` stores TX/RX channel numbers, IRQ, init-message list, controller, and per-channel state. Key functions are `bcm74110_mbox_init()`, `bcm74110_mbox_link_training()`, `bcm74110_mbox_shmem_init()`, `bcm74110_mbox_tx_msg_and_wait_ack()`, `bcm74110_rx_process_msg()`, `bcm74110_mbox_send_data()`, and `bcm74110_mbox_of_xlate()`.

## Control Flow
Probe maps registers, reads `brcm,tx` and `brcm,rx`, masks and clears IRQs, requests the RX IRQ, creates four service-indexed channels, registers the controller, then initializes hardware. Initialization resets/enables the TX queue, unmasks not-empty IRQ, performs a three-code link-training sequence, and negotiates shared-memory TX/RX windows through synchronous INIT messages. Runtime RX interrupts clear IRQ status and drain RX FIFO messages. INIT messages are queued on a spinlock-protected list for synchronous waiters; PMC/SCMI/DPFE messages notify enabled mailbox channels. Sending on service channels writes a request message carrying service type and slot.

## State and Persistence
The init-message list persists queued handshake responses until consumed or flushed. Per-channel `en`, `slot`, and `type` track client startup and DT xlate state. Shutdown sends link-stop, masks/clears IRQs, disables queues, and frees any queued init messages.

## Dependencies and Integration Points
The driver depends on platform MMIO/IRQ, OF properties, Linux lists/spinlocks, mailbox core service channels, and compatible `brcm,bcm74110-mbox`. Client channels are selected by two-cell phandles `(service type, shared-memory slot)`.

## Risks and Edge Cases
Synchronous INIT waits poll for up to roughly 30 ms and can race with asynchronous RX delivery if message fields are unexpected. Slot validation currently compares against `BCM_MBOX_HAB_MEM_IDX_SIZE`, which is zero, so only slot 0 is accepted. RX service messages deliver `NULL` data and rely on shared memory outside this driver. Link training retries on malformed/missing responses, and shutdown proceeds even if link-stop ack fails.

## Test Signals
Test link-training success/failure, INIT message queuing and flushing, PMC/SCMI/DPFE channel enable gates, invalid phandle services/slots, FIFO-full transmit rejection, shutdown link-stop behavior, and IRQ drain of multiple messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm74110-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cix-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/cix-mailbox.c

## Purpose
`cix-mailbox.c` implements the CIX Sky1 mailbox controller. It supports four transfer types: doorbell, register-window messages, FIFO messages, and eight fast channels, with instances configured as either TX or RX side by device property.

## Important APIs, Types, and Functions
`struct cix_mbox_priv` holds device state, direction, MMIO base, channel array, and shared-memory offset mode. `struct cix_mbox_con_priv` records channel type and index. Send helpers are `cix_mbox_send_data_db()`, `_reg()`, `_fifo()`, and `_fast()`. ISR helpers mirror those channel types. Startup/shutdown functions request/free the shared IRQ and enable/disable the relevant interrupt bits.

## Control Flow
Probe maps the resource, detects whether the first `0x80` bytes are reserved as shared memory based on the resource start offset, reads `cix,mbox-dir` as `tx` or `rx`, initializes 11 channels by index, and registers the mailbox controller with IRQ-based TX completion. TX instances accept send requests and dispatch by channel type: doorbell writes the DB bit, register writes up to 32 words then rings the doorbell, FIFO writes words and enables empty interrupt, and fast writes one word to the fast register. RX and TX ack interrupts are handled by the same IRQ handler and dispatch to type-specific routines.

## State and Persistence
Runtime state is mostly hardware interrupt-enable bits plus per-channel type/index metadata. There is no software queue. FIFO startup resets FIFO state and sets the default watermark. `use_shmem` changes all register offsets for devices whose first register window is client shared memory.

## Dependencies and Integration Points
The driver uses platform MMIO/IRQ, device properties, mailbox core, and compatible `cix,sky1-mbox`. It currently relies on default mailbox channel indexing rather than an explicit OF xlate function.

## Risks and Edge Cases
All channels request the same IRQ independently, so multiple active channels rely on request/free semantics and unique dev_id values. Stack-allocated receive arrays are passed to mailbox clients synchronously; clients must not retain pointers. `cix_mbox_send_data()` ignores return values from type-specific helpers and returns success after some helper failures. FIFO overflow/underflow are logged and cleared but do not propagate mailbox errors.

## Test Signals
Validate TX and RX instances separately, all four channel types, shared-memory offset mode, FIFO watermark and empty completion, fast-channel interrupts, invalid direction strings, invalid fast indexes, and multi-channel startup/shutdown sharing one IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cix-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cv1800-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/cv1800-mailbox.c

## Purpose
`cv1800-mailbox.c` implements the Sophgo CV1800B mailbox. It exposes eight fixed channels carrying 8-byte messages through per-channel context memory and interrupt bits.

## Important APIs, Types, and Functions
`struct cv1800_mbox` stores the controller, channel-private array, channel array, pending content pointers, base MMIO address, and receiver ID. `cv1800_mbox_send_data()` writes a message and triggers a remote CPU interrupt. `cv1800_mbox_irq()` is the top-half interrupt handler, and `cv1800_mbox_isr()` is the threaded handler that copies message data to clients. `cv1800_mbox_xlate()` maps two-cell phandles to channel index and target CPU.

## Control Flow
Probe maps registers, configures mailbox core with polling TX completion, requests a threaded IRQ, initializes channel private indexes, stores drvdata, and registers the controller. Sending copies eight bytes to the channel context, clears/sets remote CPU bits, enables the channel bit, and writes the global set register. The hard IRQ reads set-interrupt bits for `RECV_CPU`, records context pointers for active channels, clears the interrupt, disables the channel bit, and wakes the thread. The thread copies each pending 64-bit message and calls `mbox_chan_received_data()`.

## State and Persistence
`content[]` is a transient handoff from top half to thread. Channel private state stores the channel index and target CPU selected by xlate. Hardware enable bits represent TX completion for `last_tx_done()`.

## Dependencies and Integration Points
The driver uses platform MMIO, threaded IRQs, mailbox core, OF compatible `sophgo,cv1800b-mailbox`, and two-cell mailbox specifiers `(channel, cpu)`.

## Risks and Edge Cases
`cv1800_mbox_xlate()` does not validate `args_count` or CPU range. The threaded handler sends a pointer to a stack `u64`; mailbox callbacks must consume it synchronously. Interrupt handling disables each channel by writing `~valid` as a byte, which is hardware-specific and sensitive to bit semantics. Only fixed 8-byte payloads are supported.

## Test Signals
Validate all eight channels, remote CPU phandle values, 8-byte payload integrity, hard/threaded IRQ handoff, TX completion polling, invalid channel rejection, and no lost messages when several channel bits arrive in one interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cv1800-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/exynos-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/exynos-mailbox.c

## Purpose
`exynos-mailbox.c` implements a simple Samsung/Google Exynos mailbox, currently for GS101 ACPM doorbell sends. It exposes virtual mailbox channels and expects the data payload to identify the hardware doorbell channel.

## Important APIs, Types, and Functions
`struct exynos_mbox` holds the MMIO base and controller pointer. `exynos_mbox_send_data()` accepts `struct exynos_mbox_msg`, validates channel ID and type, and writes the interrupt generation bit. `exynos_mbox_of_xlate()` returns the first free virtual channel. Probe enables the peripheral clock and masks supported interrupts.

## Control Flow
Probe allocates state, controller, and 16 channels derived from `EXYNOS_MBOX_INTGR1_MASK`, maps registers, enables `pclk`, initializes mailbox ops/xlate, masks interrupt register 0, and registers the controller. DT phandles carry no args; xlate just reserves an unused mailbox channel. Send validates that `chan_type` is `EXYNOS_MBOX_CHAN_TYPE_DOORBELL` and that `chan_id` is in range, then writes `BIT(chan_id)` to `EXYNOS_MBOX_INTGR1`.

## State and Persistence
There is no receive path and no software queue. Runtime state is the clock-enabled device and mailbox channel client ownership tracked by the mailbox core.

## Dependencies and Integration Points
The driver depends on `linux/mailbox/exynos-message.h`, the clock framework, platform MMIO, OF compatible `google,gs101-mbox`, and mailbox clients that pass `struct exynos_mbox_msg` in `send_data()`.

## Risks and Edge Cases
Because channel ID comes from the payload rather than the mailbox phandle, client misuse can send on a different hardware doorbell than the virtual channel suggests. There is no TX done callback or RX support. Interrupts are masked because only polling/doorbell send is supported for now.

## Test Signals
Compile with Exynos message header, probe with enabled `pclk`, validate invalid channel IDs/types, confirm writes to the expected `INTGR1` bit, and ensure phandle allocation fails when all virtual channels are already bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/exynos-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi3660-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/hi3660-mailbox.c

## Purpose
`hi3660-mailbox.c` implements the HiSilicon Hi3660 mailbox controller with up to 32 channels. It is primarily a TX-oriented mailbox that writes eight-word messages and triggers a destination interrupt vector.

## Important APIs, Types, and Functions
`struct hi3660_mbox` owns the register base, channel array, per-channel IRQ vectors, and controller. `struct hi3660_chan_info` stores destination and acknowledge IRQ bits. Key routines are `hi3660_mbox_unlock()`, `hi3660_mbox_acquire_channel()`, `hi3660_mbox_check_state()`, `hi3660_mbox_startup()`, `hi3660_mbox_send_data()`, and `hi3660_mbox_xlate()`.

## Control Flow
Probe maps the MMIO region, configures 32 channels with their index stored in `con_priv`, sets mailbox ops/xlate, registers the controller, and runs at `core_initcall`. Xlate takes three cells `(channel, dst_irq, ack_irq)` and stores vectors in `mchan`. Startup unlocks IPC registers and acquires the channel by waiting for idle state and setting the ack IRQ in `SRC`. Send waits for ready or an ACK state, clears the destination interrupt mask, writes destination and automatic-ack mode, fills eight data registers, and writes `SEND` with the ack IRQ bit.

## State and Persistence
Per-channel destination/ack vector selections persist in `mchan[]` after xlate. The hardware channel state machine is polled on each send. There is no explicit shutdown operation and no software queue.

## Dependencies and Integration Points
The driver integrates with the mailbox core, platform MMIO, OF compatible `hisilicon,hi3660-mbox`, delay/poll helpers, and early platform driver registration.

## Risks and Edge Cases
`hi3660_mbox_xlate()` validates only the channel index, not dst/ack IRQ ranges. Channel acquisition uses a short retry loop without delay. Send assumes the payload contains eight `u32` words. ACK polling can block up to 300 ms and returns timeout errors on stuck hardware.

## Test Signals
Test unlock and acquire success/failure, all 32 channel xlate values, eight-word data transfer, ACK timeout handling, invalid channel rejection, and early boot client availability due to `core_initcall`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi3660-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi6220-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/hi6220-mailbox.c

## Purpose
`hi6220-mailbox.c` implements the HiSilicon Hi6220 mailbox with 32 channels, supporting TX and RX semantics through shared slot data registers and ACK interrupt vectors.

## Important APIs, Types, and Functions
`struct hi6220_mbox` stores IPC registers, mailbox buffer registers, IRQ mapping, controller, channel count, and flexible per-channel state. `struct hi6220_mbox_chan` stores direction, destination IRQ, ack IRQ, slot, and parent. Important functions are `hi6220_mbox_send_data()`, `hi6220_mbox_interrupt()`, `hi6220_mbox_startup()`, `hi6220_mbox_shutdown()`, `hi6220_mbox_last_tx_done()`, and `hi6220_mbox_xlate()`.

## Control Flow
Probe maps IPC and buffer resources, requests the shared IRQ, initializes controller/channels, clears interrupt state, selects IRQ-based or polling TX completion based on `hi6220,mbox-tx-noirq`, registers the controller, and runs at `core_initcall`. Xlate takes `(slot, dst_irq, ack_irq)`, validates all against channel count, prevents duplicate ack IRQ mapping, and returns the slot channel. Startup enables the ack interrupt. Send marks the channel TX, sets slot state to TX, selects ACK IRQ or automatic mode, writes eight words, and triggers the remote destination IRQ. The ISR reads ACK status bits, maps them to channels, completes TX channels or reads eight-word RX data for non-TX channels, clears the ack IRQ, and returns the slot to idle.

## State and Persistence
`irq_map_chan[]` ties ack interrupt vectors to channels until shutdown. Each `mchan` persists current direction and slot configuration. Hardware slot state is actively rewritten to idle after interrupts.

## Dependencies and Integration Points
The driver depends on platform MMIO/IRQ, OF compatible `hisilicon,hi6220-mbox`, optional DT property `hi6220,mbox-tx-noirq`, mailbox core, and early registration.

## Risks and Edge Cases
`last_tx_done()` has a `BUG_ON()` if called in IRQ mode, so mailbox configuration must match the selected completion mode. RX uses stack message storage for synchronous delivery. Direction is set to TX on send and reset to 0 on startup, making mixed client behavior sensitive to open/send ordering. Duplicate ack IRQ detection only rejects the same channel pointer case.

## Test Signals
Validate TX IRQ and polling modes, ACK vector mapping and cleanup, eight-word RX/TX payloads, unexpected IRQ vector warnings, invalid xlate arguments, slot idle completion, and suspend/resume users that depend on early mailbox registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/hi6220-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/imx-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/imx-mailbox.c

## Purpose
`imx-mailbox.c` implements NXP i.MX Message Unit mailbox controllers across several SoC generations and firmware protocols. It supports generic TX/RX registers, doorbells, reset channels, SCU/S4 multiword RPC, and SECO-style doorbell RPC.

## Important APIs, Types, and Functions
`struct imx_mu_priv` holds MMIO base, controller, channels, config, clock, IRQs, saved control registers, TR/RR counts, and PM state. `struct imx_mu_con_priv` describes each channel's index/type and deferred TX doorbell work. SoC-specific `struct imx_mu_dcfg` instances provide register offsets, type flags, and tx/rx/init callbacks. Key functions include generic/specific/SECO TX/RX helpers, `imx_mu_isr()`, `imx_mu_startup()`, `imx_mu_shutdown()`, xlate variants, init variants, PM callbacks, and `imx_mu_probe()`.

## Control Flow
Probe maps registers, selects match data, obtains shared or named TX/RX IRQs, allocates a maximum RPC receive buffer, enables the optional clock, discovers TR/RR counts, detects side B, initializes channels through the selected config, registers the mailbox controller, populates child devices, enables runtime PM, performs an initial resume/put cycle, then disables the clock until clients start. Startup resumes runtime PM, initializes doorbell work or requests an IRQ, and enables RX/RXDB interrupt bits. Send dispatches to config TX callbacks: generic single-word TX writes TR and enables TX interrupt; doorbells set GIR bits; specific SCU/S4 TX streams a bounded RPC message through available TR registers; SECO TX sends header, signals, and waits for remote reads. The ISR filters status by enabled bits and channel type, then completes TX or calls RX/RXDB callbacks.

## State and Persistence
Runtime PM gates the clock around active channels. `xcr_lock` protects control-register RMW operations. `priv->msg` is a reusable receive buffer for specific protocols. Suspend-noirq optionally saves control registers when no clock provider exists and restores only if context appears lost. `suspend` flags wakeup behavior for interrupts during system sleep.

## Dependencies and Integration Points
The driver integrates with firmware headers `linux/firmware/imx/ipc.h` and `s4.h`, platform IRQ/MMIO/clock/runtime PM, OF child population, mailbox core, and compatibles for `fsl,imx6sx-mu`, `imx7ulp`, `imx8ulp`, `imx8ulp-mu-s4`, `imx93-mu-s4`, `imx95` variants, `imx8-mu-scu`, and `imx8-mu-seco`.

## Risks and Edge Cases
This is a high-variance driver: channel numbering and IRQ semantics differ by SoC type. Message size fields are validated, but clients must supply the correct RPC struct. Some TXDB paths synthesize completion through work because hardware lacks ACK support. The source contains a duplicated line in `imx_mu_seco_tx()` that compile testing should catch. Runtime PM error paths and IRQ request failures must not leak clocks or active PM references.

## Test Signals
Test each compatible configuration, generic and specific xlate validation, single-word TX/RX, TXDB and RXDB, SCU/S4/SECO max-size rejection, timeout paths for full/empty TR/RR, runtime PM clock balancing, suspend/resume register save/restore, named IRQ mode, and side-B initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/imx-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-altera.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-altera.c

## Purpose
`mailbox-altera.c` implements the Altera mailbox IP as a one-channel mailbox that can be detected as either sender or receiver. It supports interrupt or polling operation depending on IRQ availability and direction.

## Important APIs, Types, and Functions
`struct altera_mbox` stores direction, interrupt mode, IRQ, MMIO base, controller, optional RX polling timer, and active channel. Helpers include `altera_mbox_is_sender()`, `altera_mbox_full()`, `altera_mbox_pending()`, RX/TX interrupt mask helpers, `altera_mbox_rx_data()`, `altera_mbox_send_data()`, `altera_mbox_startup()`, `altera_mbox_shutdown()`, `last_tx_done()`, and `peek_data()`.

## Control Flow
Probe maps registers, determines sender mode by writing a magic value to the pointer register and reading it back, optionally obtains an IRQ, configures one channel, enables TX IRQ or TX polling for sender instances, and registers the controller. Sender startup requests a TX-space interrupt if in interrupt mode. Receiver startup requests an RX-pending interrupt or falls back to a 5 ms polling timer. Send validates direction and non-null data, rejects a full mailbox, enables TX interrupt before sending if needed, writes pointer first and command second. RX reads pointer and command when pending and reports a two-word array.

## State and Persistence
Direction is determined once at probe. `intr_mode` may be downgraded to polling if RX IRQ request fails. The RX polling timer persists only while a receiver channel is active. There is no message queue outside the hardware registers.

## Dependencies and Integration Points
The driver depends on platform MMIO/IRQ, OF compatible `altr,mailbox-1.0`, Linux timers, and mailbox core operations including `peek_data()`.

## Risks and Edge Cases
Direction detection mutates the pointer register with a magic value. Receiver polling uses a timer and stack-local data for synchronous delivery. Shutdown masks all interrupts and frees the IRQ in interrupt mode. Send must preserve pointer-before-command ordering because command write likely triggers delivery.

## Test Signals
Test sender and receiver hardware variants, IRQ and polling receiver paths, failed IRQ fallback, pointer/command ordering, full and pending status handling, timer cancellation on shutdown, and `peek_data()` correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-altera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mchp-ipc-sbi.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mchp-ipc-sbi.c

## Purpose
`mailbox-mchp-ipc-sbi.c` implements a Microchip IPC mailbox that delegates hardware operations to a vendor SBI extension. It discovers IPC channels, initializes per-channel buffers, sends messages by physical address, and handles cluster aggregate IRQs for receive and clear notifications.

## Important APIs, Types, and Functions
SBI payload formats are `struct mchp_ipc_mbox_info`, `mchp_ipc_init`, `mchp_ipc_status`, and `mchp_ipc_sbi_msg`. `struct mchp_ipc_sbi_mbox` stores device, channels, cluster IRQ config, controller, and hardware type. Key functions are `mchp_ipc_sbi_send()`, `mchp_ipc_sbi_chan_send()`, `mchp_ipc_probe()`, `mchp_ipc_startup()`, `mchp_ipc_send_data()`, `mchp_ipc_cluster_aggr_isr()`, and `mchp_ipc_mbox_xlate()`.

## Control Flow
Probe verifies the Microchip vendor SBI extension, allocates a probe buffer, calls `SBI_EXT_IPC_PROBE`, creates the discovered number of channels, allocates per-channel private structs with IDs, requests per-online-CPU aggregate IRQs named by hart ID for MIV IHC hardware, and registers an IRQ-completion mailbox controller. Startup allocates TX/RX SBI payload buffers, calls channel init to learn max message size, then allocates max-size TX/RX data buffers. Send copies client data into the TX buffer, writes an SBI payload pointing to it, and calls `SBI_EXT_IPC_SEND`. The aggregate ISR identifies the source hart, asks SBI for status, maps status bits to channel IDs, performs receive SBI calls for message-present bits, and calls `mbox_chan_received_data()` or `mbox_chan_txdone()` for clear bits.

## State and Persistence
Per-channel buffers are allocated on startup and freed on shutdown. Cluster status buffers are devm-managed per online CPU. Channel IDs are stable for the controller lifetime. No software queue is maintained beyond buffers holding the latest send/receive payload.

## Dependencies and Integration Points
The driver depends on RISC-V SBI, Microchip vendor ID, hart/CPU mapping, platform IRQ names, DMA-addressable physical memory via `__pa()`, mailbox core, public `linux/mailbox/mchp-ipc.h`, and compatible `microchip,sbi-ipc`.

## Risks and Edge Cases
The channel ID computation in the ISR is subtle and tied to cluster topology and no-loopback assumptions. Buffers are allocated with `kmalloc()` and converted with `__pa()`, so platform memory mapping expectations matter. CPU hotplug after probe is not reflected in `cluster_cfg`. Send does not validate client `msg->size` against `max_msg_size` before copying.

## Test Signals
Test SBI extension absence, probe/channel-init failures, per-hart IRQ discovery, send/receive/clear interrupts, max message size enforcement by clients, shutdown buffer freeing, invalid phandle channel IDs, and multi-hart channel mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mchp-ipc-sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mpfs.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mpfs.c

## Purpose
`mailbox-mpfs.c` implements the Microchip PolarFire SoC system-controller mailbox. It sends service requests through MSS system controller registers or syscon regmaps and returns service responses from a mailbox data window.

## Important APIs, Types, and Functions
`struct mpfs_mbox` stores controller state, IRQ, control/mailbox bases, optional syscon regmaps, current response pointer, and response offset. Core functions are `mpfs_mbox_busy()`, `mpfs_mbox_last_tx_done()`, `mpfs_mbox_send_data()`, `mpfs_mbox_rx_data()`, `mpfs_mbox_inbox_isr()`, startup/shutdown, and probe helpers for new syscon and old DT formats.

## Control Flow
Probe first tries syscon lookup for `microchip,mpfs-control-scb` and `microchip,mpfs-sysreg-scb`; if that fails it falls back to old-format direct MMIO resources. It obtains an IRQ, configures one polling-completion mailbox channel, and registers the controller. Startup requests the inbox IRQ. Send stores the response pointer and response offset from `struct mpfs_mss_msg`, checks the system controller busy bit, writes optional command data into the mailbox window with byte handling for non-word tails, composes the option select from mailbox offset and opcode, and writes service control request/notify bits. The IRQ clears the message interrupt and reads the response window into the client response buffer. `last_tx_done()` also extracts failed service status from the status register after busy clears.

## State and Persistence
The active response pointer and response offset are stored in the controller state for the single outstanding request. Register access mode (`regmap` versus direct MMIO) is selected at probe and remains fixed. There is no persistent queue.

## Dependencies and Integration Points
The driver depends on mailbox core, platform IRQ/MMIO, regmap/syscon, MFD syscon lookup, and public Microchip service message types in `soc/microchip/mpfs.h`. Compatible is `microchip,mpfs-mailbox`.

## Risks and Edge Cases
Only one channel and one saved response pointer are supported, so concurrent clients must rely on mailbox serialization. Failed services may not interrupt, so `last_tx_done()` reads status as a workaround. Old DT fallback maps resources differently and may derive mailbox base from control base plus offset. Non-word command tails require careful read-modify-write.

## Test Signals
Test syscon and old-format probe paths, busy rejection, command data writes with unaligned byte counts, interrupt response reads, service failure status via polling, null response buffer error logging, and startup/shutdown IRQ lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mpfs.c -->
