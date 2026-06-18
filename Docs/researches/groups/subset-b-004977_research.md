# Research: subset-b-004977

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.c

Purpose: implements the Intel IOSM IPC protocol operations that manipulate AP/CP shared-memory message rings and pipe transfer descriptor rings. It is the operational companion to `iosm_ipc_protocol_ops.h`, translating higher-level pipe, sleep, and feature requests into shared-memory messages and moving SKBs through UL/DL TD rings.

Important APIs and functions: `ipc_protocol_msg_prep()` dispatches message preparation for sleep, pipe open/close, and feature-set requests. `ipc_protocol_msg_hp_update()` advances the AP message head and rings the HPDA doorbell through `ipc_pm_signal_hpda_doorbell()`. `ipc_protocol_msg_process()` consumes CP-completed message entries, updates `struct ipc_rsp`, and completes waiters. `ipc_protocol_ul_td_send()` enqueues mapped uplink SKBs into a pipe TD ring, while `ipc_protocol_ul_td_process()` reclaims completed UL buffers. `ipc_protocol_dl_td_prepare()` allocates DMA-capable SKBs for modem downlink, and `ipc_protocol_dl_td_process()` validates completion status, mapping, and length before returning an SKB to the caller.

Control flow and state: pipe open allocates `pipe->skbr_start` and coherent `pipe->tdr_start`, resets pipe counters, writes `head_array[pipe_nr]`, and publishes an `IPC_MEM_MSG_OPEN_PIPE`. Message completions are tracked by `old_msg_tail` and `rsp_ring[]`. Data rings keep AP head in shared memory and keep local `old_head`, `old_tail`, and `nr_of_queued_entries` in `struct ipc_pipe`.

Dependencies and integration points: depends on IOSM protocol state, PCIe DMA helpers (`ipc_pcie_alloc_skb()`, `ipc_pcie_kfree_skb()`), IPC PM doorbells, little-endian shared-memory fields, and SKB DMA metadata in `IPC_CB(skb)`.

Risks and test signals: ring-full handling, off-by-one free-space math, DMA mapping mismatch, invalid CP length/status, and cleanup while descriptors are outstanding are the main risks. Useful tests are pipe open/close stress, UL queue saturation, DL abort/overflow completions, message response timeout paths, and suspend/resume doorbell behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.h

Purpose: defines the IOSM protocol wire structures, completion enums, TD format, message preparation arguments, and public protocol operation prototypes used by the IOSM shared-memory transport layer.

Important APIs/types: `enum ipc_mem_td_cs` documents TD completion states, including partial, end, overflow, abort, and error. `enum ipc_mem_msg_cs` represents message completion. `union ipc_msg_prep_args` groups pipe, sleep, feature, map, and unmap request arguments; map/unmap are declared even though this protocol implementation rejects them. `enum ipc_mem_msg` assigns shared-memory message type values. Message structures such as `ipc_mem_msg_open_pipe`, `ipc_mem_msg_close_pipe`, `ipc_mem_msg_host_sleep`, and `ipc_mem_msg_feature_set` mirror the AP-to-CP ring layout. `struct ipc_protocol_td` is packed and carries a DMA buffer address, size/completion-status word, and chained-descriptor count.

Control flow and state: the header establishes the contract for the implementation in `iosm_ipc_protocol_ops.c`: callers prepare messages, advance message head pointers, process completions, enqueue/reclaim UL descriptors, provision/process DL descriptors, query shared IPC status, and clean pipe resources. `SIZE_MASK`, `COMPLETION_STATUS`, and `RESET_BIT` encode bitfield assumptions shared with CP firmware.

Dependencies and integration points: includes forward dependencies on `struct iosm_imem`, `struct iosm_protocol`, `struct ipc_pipe`, `struct sk_buff`, completions, DMA addresses, and shared IPC state enums from the broader IOSM protocol headers.

Risks and test signals: all structs are ABI-like shared-memory layouts, so packing, endian conversion, size fields, and bit shifts are high-risk. Build tests should catch prototype drift; runtime tests should validate that CP firmware accepts open/close/sleep/feature messages and that TD status bits are interpreted correctly on 32/64-bit DMA platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_task_queue.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_task_queue.c

Purpose: implements a small serialized tasklet-backed queue for IOSM IPC callbacks that need to be invoked outside interrupt or caller context while preserving ordering.

Important APIs/functions: `ipc_task_init()` allocates and initializes the tasklet and queue lock. `ipc_task_queue_send_task()` optionally copies a message payload with `kmemdup(..., GFP_ATOMIC)`, queues a function call, and optionally waits for completion. `ipc_task_queue_add_task()` is the core producer path, filling one `ipc_task_queue_args` slot under `q_lock`, issuing `smp_wmb()`, advancing `q_wpos`, and scheduling the tasklet. `ipc_task_queue_handler()` drains queued entries, calls the function pointer, completes synchronous requests, frees copied payloads, and clears the slot. `ipc_task_deinit()` kills the tasklet and completes/frees queued-but-unprocessed entries through `ipc_task_queue_cleanup()`.

Control flow and state: state is a fixed-size circular queue with volatile read/write positions and per-slot function/message/completion data. Synchronous calls use a stack completion object and read the response from the same queued slot after completion.

Dependencies and integration points: integrates with `struct iosm_imem` and its `ipc_task` member, kernel tasklets, spinlocks, completions, atomic GFP allocations, and IOSM callback functions with signature `int (*)(struct iosm_imem *, int, void *, size_t)`.

Risks and test signals: queue full paths, synchronous wait lifetime, copied message ownership, and deinit races are the main risks. Tests should stress task submission from interrupt-like context, mixed sync/async calls, queue saturation at 256 entries, and teardown while requests are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_task_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_task_queue.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_task_queue.h

Purpose: declares the IOSM task queue data structures and entry points used to serialize IPC work in tasklet context.

Important APIs/types: `IPC_THREAD_QUEUE_SIZE` fixes the queue at 256 entries. `struct ipc_task_queue_args` stores the target `iosm_imem`, message pointer, optional completion, callback function pointer, integer argument, message size, response, and ownership bit `is_copy`. `struct ipc_task_queue` contains the spinlock, queue slots, read position, and write position. `struct ipc_task` packages the owning device, tasklet pointer, and queue. Public functions are `ipc_task_init()`, `ipc_task_deinit()`, and `ipc_task_queue_send_task()`.

Control flow and state: producers fill `ipc_task_queue_args`; the tasklet consumer clears entries after execution. `is_copy` controls whether the tasklet or cleanup path frees the message. Completion is optional, so the same structure supports asynchronous fire-and-forget events and synchronous calls returning callback status.

Dependencies and integration points: depends on kernel tasklet, completion, spinlock, and device types, plus IOSM `struct iosm_imem`. The header is consumed by IOSM memory/control paths that need ordered deferred execution.

Risks and test signals: consumers must respect the callback signature and message ownership rules. ABI-like risks are low, but concurrency risks are significant around queue wrap, stale slot reuse, and teardown. Build coverage plus runtime stress of sync/async calls provides the strongest signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_task_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.c

Purpose: provides IOSM modem trace capture through debugfs and relayfs. It opens a dedicated IOSM control channel on demand and writes incoming trace SKBs to a relay channel.

Important APIs/functions: `ipc_trace_init()` initializes IPC control channel 3, allocates `struct iosm_trace`, creates `trace_ctrl` debugfs control file, and opens the relay channel named `trace`. `ipc_trace_ctrl_file_write()` parses `0`/`1` user input and opens or closes the system port with `ipc_imem_sys_port_open()`/`ipc_imem_sys_port_close()`. `ipc_trace_ctrl_file_read()` exposes current mode. `ipc_trace_port_rx()` writes trace payloads to relayfs and frees SKBs. Relay callbacks create/remove buffer files and drop data when relay buffers are full. `ipc_trace_deinit()` removes debugfs, closes relay, destroys mutex, and frees state.

Control flow and state: `mode`, `channel`, and relay state are protected by `trc_mutex` for user control operations. RX path is simple and assumes `ipc_imem->trace` is valid when trace channel traffic is routed here.

Dependencies and integration points: depends on `CONFIG_WWAN_DEBUGFS`, debugfs, relayfs, IOSM channel config, and IMEM system port operations. It integrates with IOSM RX dispatch through `ipc_is_trace_channel()` in the header.

Risks and test signals: trace enable/disable races, relay full drops, channel-open failure, and deinit while userspace has debugfs files open are key risks. Tests should cover repeated toggles, reading mode, receiving trace traffic while disabled/enabled, and module/device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.h

Purpose: declares the IOSM trace debugfs/relayfs interface and provides no-op fallbacks when WWAN debugfs support is disabled.

Important APIs/types: `enum trace_ctrl_mode` defines disabled/enabled states. `struct iosm_trace` stores relay channel, debugfs control dentry, IMEM pointer, device pointer, opened IPC channel, trace channel ID, mutex, and mode. When `CONFIG_WWAN_DEBUGFS` is enabled, `ipc_is_trace_channel()` checks whether an incoming channel ID is the trace channel, and the init/deinit/RX functions are exported. When disabled, `ipc_is_trace_channel()` always returns false and `ipc_trace_port_rx()` just frees the SKB.

Control flow and state: the header controls compile-time feature presence and prevents non-debugfs builds from carrying relay/debugfs behavior while keeping callers simple.

Dependencies and integration points: includes debugfs, relayfs, IOSM channel config, and IMEM ops. It is integrated into IOSM receive demultiplexing so trace SKBs are diverted away from normal control or WWAN paths.

Risks and test signals: conditional compilation is the main risk. Build both `CONFIG_WWAN_DEBUGFS=y` and disabled configurations. Runtime signals include successful debugfs file creation, correct channel identification, and safe SKB freeing in the disabled stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.c

Purpose: sends IOSM modem state notifications to userspace as environment-bearing `KOBJ_CHANGE` uevents from process context.

Important APIs/functions: `ipc_uevent_send()` allocates `struct ipc_uevent_info` with `GFP_ATOMIC`, initializes a work item, stores the target device, formats `IOSM_EVENT=<event>` into a fixed buffer, and schedules the work. `ipc_uevent_work()` builds the `envp` array, calls `kobject_uevent_env()`, logs failure, and frees the work object.

Control flow and state: no persistent state is kept. Each event is a self-contained work item, making the function safe to call from atomic contexts and deferring uevent emission to the system workqueue.

Dependencies and integration points: depends on device/kobject infrastructure, slab allocation, workqueues, and event-string constants from `iosm_ipc_uevent.h`. It is used by IOSM modem state code to notify userspace about readiness, crash, coredump, and timeout states.

Risks and test signals: allocation failure silently drops events; long event strings are truncated to `MAX_UEVENT_LEN`; there is no device lifetime reference beyond the raw pointer stored in work. Tests should trigger each event string, monitor udev/netlink delivery, and exercise teardown-adjacent event sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.h

Purpose: defines IOSM userspace event names and the work item structure used to send modem state uevents.

Important APIs/types: constants include `UEVENT_MDM_NOT_READY`, `UEVENT_ROM_READY`, `UEVENT_MDM_READY`, `UEVENT_CRASH`, `UEVENT_CD_READY`, `UEVENT_CD_READY_LINK_DOWN`, and `UEVENT_MDM_TIMEOUT`. `MAX_UEVENT_LEN` caps the formatted `IOSM_EVENT=` string at 64 bytes. `struct ipc_uevent_info` stores the target device, formatted event buffer, and work item. `ipc_uevent_send()` is the public sender.

Control flow and state: callers pass a device and one of the event strings; implementation allocates a transient work item and emits one uevent. There is no durable state or retry.

Dependencies and integration points: tied to Linux workqueues and kobject uevents. It is part of the IOSM modem lifecycle notification surface consumed by userspace modem-management services.

Risks and test signals: event spelling is externally visible, so renames are compatibility risks. The fixed buffer requires guarding new event names against truncation. Test by observing generated environment variables for every constant and by checking behavior under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.c

Purpose: adapts IOSM IP MUX sessions to Linux WWAN raw network devices. It registers WWAN link operations, opens/closes IOSM WWAN channels per session, transmits SKBs to IMEM, and delivers downlink SKBs to the network stack.

Important APIs/functions: `ipc_wwan_init()` allocates `struct iosm_wwan` and registers `wwan_ops` with default IP MUX session. `ipc_wwan_newlink()` initializes `iosm_netdev_priv`, registers a netdev, and stores it in an RCU session array. `ipc_wwan_link_open()` calls `ipc_imem_sys_wwan_open()` and starts the netdev queue. `ipc_wwan_link_transmit()` calls `ipc_imem_sys_wwan_transmit()` and updates TX stats or drops. `ipc_wwan_receive()` identifies IPv4/IPv6, looks up the session under RCU, updates RX stats, and calls `netif_rx()`. `ipc_wwan_tx_flowctrl()` stops or wakes per-session queues.

Control flow and state: `struct iosm_wwan` owns `sub_netlist[]`, an RCU-indexed table keyed by IP MUX session ID. Per-netdev state records IF ID and IPC channel ID. Netdev deletion clears the RCU slot before queued unregister.

Dependencies and integration points: uses WWAN core, rtnetlink-created links, IOSM IMEM WWAN open/close/transmit APIs, raw-IP netdev conventions (`ARPHRD_NONE`, no header), and Linux netdev stats.

Risks and test signals: session ID bounds, RCU lifetime, TX error handling, queue flow control, and packet protocol sniffing are the main risks. Test with default and additional sessions, open/stop cycles, `-EBUSY` TX backpressure, IPv4/IPv6 RX, and link deletion while RX is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.h

Purpose: declares the public IOSM WWAN adapter interface used by the IMEM layer and device lifecycle code.

Important APIs/types: `ipc_wwan_init()` registers WWAN operations and returns an opaque `struct iosm_wwan`. `ipc_wwan_deinit()` unregisters WWAN operations and frees the object. `ipc_wwan_receive()` is the downlink entry point from IOSM channel handling, taking an SKB, DSS flag, and interface/session ID. `ipc_wwan_tx_flowctrl()` toggles network queue flow control for a session.

Control flow and state: the header intentionally keeps `struct iosm_wwan` opaque. The implementation owns all per-session netdev state and RCU mapping. Callers only initialize/deinitialize, pass received SKBs, and signal modem TX backpressure.

Dependencies and integration points: depends on IOSM IMEM and Linux SKB types through forward declarations from included compilation context. It bridges low-level IOSM IPC data path and Linux WWAN/netdev users.

Risks and test signals: API misuse risks include passing invalid session IDs, calling receive after deinit, or toggling flow control before link creation. Build tests catch prototype drift; runtime tests should pair IMEM channel lifecycle with WWAN link creation and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_ctrl.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_ctrl.c

Purpose: exposes MHI control channels such as DUN, MBIM control, QMI, DIAG, FIREHOSE, and NMEA as WWAN character ports.

Important APIs/functions: `mhi_wwan_ctrl_probe()` allocates `struct mhi_wwan_dev`, records UL/DL capabilities from MHI channels, and creates a WWAN port of the type stored in the MHI ID table. `mhi_wwan_ctrl_start()` prepares MHI transfers, initializes RX budget from free DL descriptors, and refills RX buffers. `mhi_wwan_ctrl_tx()` queues outgoing SKBs with `mhi_queue_skb()` and turns TX off when the MHI queue is full. `mhi_ul_xfer_cb()` frees completed TX SKBs and re-enables WWAN TX. `mhi_dl_xfer_cb()` sets received SKB length and forwards it to `wwan_port_rx()`. RX refill is budgeted by `mhi_wwan_rx_budget_dec/inc()` and an SKB destructor.

Control flow and state: `flags` track channel capability and refill state. `rx_budget` limits outstanding RX buffers to descriptor capacity and is replenished only when WWAN core releases an SKB. `tx_lock` serializes TX queue state with callbacks; `rx_lock` protects budget and refill scheduling.

Dependencies and integration points: depends on MHI bus APIs and WWAN port core. The MHI channel-name table maps firmware channels to WWAN port types.

Risks and test signals: RX buffer lifetime relies on the SKB destructor, so leaks or missing destructor calls stall refill. Test start/stop, full TX queue backpressure, DL overflow tolerance, all listed channel names, and remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_mbim.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_mbim.c

Purpose: implements raw-IP network links carrying MBIM/NCM-framed traffic over an MHI data channel, primarily `IP_HW0_MBIM`.

Important APIs/functions: `mhi_mbim_probe()` prepares MHI transfer, records RX queue size, initializes delayed RX refill, and registers WWAN netdev ops. `mhi_mbim_newlink()` creates per-session links in an RCU hlist; some Foxconn controllers offset sessions using mux ID 112. `mhi_mbim_ndo_xmit()` wraps an IP packet with `mbim_tx_fixup()` into an NTH16/NDP16 header and queues it to MHI. `mhi_mbim_dl_callback()` handles MHI RX completion, including `-EOVERFLOW` aggregation through `frag_list`, then calls `mhi_mbim_rx()`. `mhi_mbim_rx()` validates NTH16/NDP16 headers, iterates NDPs and datagram entries, finds the session link, classifies IPv4/IPv6, accounts stats, and calls `netif_rx()`.

Control flow and state: `struct mhi_mbim_context` owns MHI device, RX aggregation head/tail, MRU, RX queue size, sequence counters, delayed refill work, TX lock, and link hash table. Per-link `u64_stats` provide lockless netdev stats. Netdev open schedules refill and starts queue; stop disables carrier/queue.

Dependencies and integration points: depends on MHI, WWAN core, USB CDC NCM/MBIM header definitions, raw-IP netdev semantics, RCU, and `u64_stats_sync`.

Risks and test signals: validate MBIM offsets/lengths, sequence wrap, multi-fragment MHI aggregation, RCU link deletion, TX queue wake, and controller-specific mux IDs. Test with malformed NTBs, multiple sessions, queue-full TX, and remove with partial aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_mbim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/qcom_bam_dmux.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/qcom_bam_dmux.c

Purpose: implements Qualcomm BAM-DMUX WWAN raw-IP network devices over DMAengine RX/TX channels and Qualcomm SMEM power-control handshakes.

Important APIs/functions: `bam_dmux_probe()` obtains IRQs and SMEM state handles, initializes runtime PM, requests threaded PC/PC-ACK IRQs, and powers on if the remote side is already active. `bam_dmux_runtime_resume()` votes for power, waits for ACK and remote `pc_state`, verifies RX DMA initialization, and requests TX DMA. `bam_dmux_rx_callback()` validates DMUX headers and dispatches DATA/OPEN/CLOSE commands. OPEN schedules netdev registration; CLOSE detaches a channel. `bam_dmux_netdev_start_xmit()` queues an SKB in a fixed TX ring, prepends `bam_dmux_hdr`, maps for DMA, and either submits immediately or defers until runtime resume completes. `bam_dmux_power_on()` requests RX DMA and posts 32 RX buffers.

Control flow and state: `struct bam_dmux` owns SMEM PC state, completions/waitqueues, RX/TX DMA channels, fixed arrays of 32 DMA SKBs, a TX ring index, deferred TX bitmap, remote channel bitmap, and per-channel netdevs. Remote channel state drives dynamic `wwan%d` device creation.

Dependencies and integration points: depends on platform device probing, OF compatible `qcom,bam-dmux`, DMAengine, runtime PM, SMEM state, netdev core, and raw-IP/QMAP protocol handling.

Risks and test signals: power handshake timeout, deferred TX during resume, DMA mapping cleanup, remote open/close races, and header validation are key risks. Test runtime suspend/resume under traffic, channel churn, malformed headers, full TX ring, remove while remote PC is asserted, and QMAP/non-IP packet delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/qcom_bam_dmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/rpmsg_wwan_ctrl.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/rpmsg_wwan_ctrl.c

Purpose: adapts Qualcomm-style RPMSG control channels to WWAN ports for QMI and AT traffic.

Important APIs/functions: `rpmsg_wwan_ctrl_probe()` finds the first platform-device ancestor as the WWAN parent, allocates `struct rpmsg_wwan_dev`, and creates a WWAN port of the type from the RPMSG ID table. `rpmsg_wwan_ctrl_start()` creates a dedicated RPMSG endpoint using the RPMSG device source address and channel name. `rpmsg_wwan_ctrl_callback()` copies inbound RPMSG payloads into SKBs and forwards them with `wwan_port_rx()`. TX is provided by nonblocking `rpmsg_wwan_ctrl_tx()`, blocking `rpmsg_wwan_ctrl_tx_blocking()`, and `rpmsg_wwan_ctrl_tx_poll()`.

Control flow and state: state is minimal: RPMSG device, WWAN port, and endpoint pointer. Endpoint lifetime is tied to WWAN port start/stop. Remove unregisters the WWAN port; devm allocation handles memory.

Dependencies and integration points: depends on RPMSG core, platform-device ancestry for WWAN device grouping, and WWAN port core. Supported RPMSG channel names include `DATA5_CNTL` as QMI and `DATA4`/`DATA1` as AT.

Risks and test signals: endpoint creation failure, parent selection assumptions, TX before start, and callback allocation failure are main risks. Test open/close, poll behavior, blocking/nonblocking TX, inbound RX, and remove with a live port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/rpmsg_wwan_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/Makefile

Purpose: defines the object composition for the MediaTek/Intel t7xx WWAN PCIe modem driver module.

Important build behavior: `obj-${CONFIG_MTK_T7XX} := mtk_t7xx.o` builds a single composite module when the Kconfig symbol is enabled. The module links PCIe probing, PCIe MAC, MHCCIF, state monitor, modem ops, CLDMA, CLDMA HIF, port proxy/control, WWAN port, DPMAIF HIF/TX/RX, DPMAIF register layer, and t7xx netdev support. `t7xx_port_trace.o` is added only under `CONFIG_WWAN_DEBUGFS`.

Control flow and state: this file has no runtime state, but it determines which translation units are compiled into the single driver. That ordering captures the intended layering: bus and modem lifecycle, control path, port layer, data path, and netdev layer.

Dependencies and integration points: depends on kernel kbuild syntax and the `CONFIG_MTK_T7XX`/`CONFIG_WWAN_DEBUGFS` configuration symbols. It integrates every t7xx file in this research subset with neighboring files not individually researched here, such as `t7xx_hif_dpmaif_tx.c`, `t7xx_netdev.c`, and `t7xx_port_proxy.c`.

Risks and test signals: build omissions are the primary risk. Test with `CONFIG_MTK_T7XX=m/y`, with and without `CONFIG_WWAN_DEBUGFS`, and ensure all referenced object files compile and link into `mtk_t7xx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.c

Purpose: provides low-level CLDMA register operations for the t7xx control DMA engines, including queue start/stop, interrupt mask/unmask, reset, address programming, and address-mode restoration.

Important APIs/functions: `t7xx_cldma_hw_init()` configures UL/DL address mode, disables invalid address checks, sets busy masks, and clears interrupt mask. `t7xx_cldma_hw_restore()` reapplies UL settings after resume. `t7xx_cldma_hw_set_start_addr()` programs 64-bit GPD ring start addresses. `t7xx_cldma_hw_start_queue()`, `t7xx_cldma_hw_resume_queue()`, and `t7xx_cldma_hw_stop_all_qs()` control queue execution. `t7xx_cldma_hw_irq_en/dis_txrx()` and `_eq()` manipulate L2 masks. `t7xx_cldma_hw_tx_done()`/`rx_done()` clear interrupt status. `t7xx_cldma_hw_reset()` toggles infrastructure reset bits.

Control flow and state: state lives in `struct t7xx_cldma_hw`, especially AP AO/PDN register bases, hardware mode, and physical interrupt ID. Functions directly read/write MMIO and assume callers serialize higher-level queue state.

Dependencies and integration points: used by `t7xx_hif_cldma.c`; depends on register constants in `t7xx_cldma.h`, Linux MMIO helpers, 64-bit lo/hi IO helpers, and delay primitives.

Risks and test signals: incorrect base selection, interrupt mask polarity, reset timing, and address-mode mismatch can break all control channels. Test start/stop, resume, queue active polling, interrupt clear/mask behavior, and 64-bit DMA addressing on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.h

Purpose: defines CLDMA hardware constants, register offsets, interrupt masks, reset bits, queue counts, hardware mode enums, and public low-level CLDMA operations.

Important APIs/types: `CLDMA_TXQ_NUM`/`CLDMA_RXQ_NUM` define eight TX and RX queues. Interrupt masks distinguish TX/RX done bits, empty queue bits, TX/RX error bits, and active-start errors. Register macros cover CLDMA0/1 AO/PD bases, UL/DL start/current/status/control registers, L2/L3 interrupt registers, busy masks, and infra reset bits. `enum mtk_txrx` identifies TX vs RX, `enum t7xx_hw_mode` captures DMA address width, and `struct t7xx_cldma_hw` stores mode, mapped bases, and interrupt ID.

Control flow and state: this header is the register contract consumed by `t7xx_cldma.c` and higher CLDMA HIF code. Queue operations are expressed by queue number or `CLDMA_ALL_Q`.

Dependencies and integration points: depends on Linux bit macros and types. It is included by `t7xx_hif_cldma.h` and low-level CLDMA implementation.

Risks and test signals: register definitions are hardware ABI. Wrong masks or offsets cause hard-to-debug interrupt storms, stalled queues, or reset failures. Test by reading known hardware status, exercising all queues, and validating suspend/resume on both CLDMA MD and AP instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.c

Purpose: implements the DPMAIF hardware register layer for t7xx data path queues, covering initialization, interrupt decoding, DL BAT/PIT/fragment setup, UL DRB setup, queue enable/disable, and hardware index updates.

Important APIs/functions: `t7xx_dpmaif_hw_init()` resets/configures DPMAIF, initializes interrupts, stores queue properties, configures DL and UL queues, and marks UL/DL init done. `t7xx_dpmaif_hw_get_intr_cnt()` reads UL/DL interrupt status, masks queue-done interrupts before bottom halves, clears status, and fills `dpmaif_hw_intr_st_para`. `t7xx_dpmaif_ul_update_hw_drb_cnt()` notifies hardware of new TX descriptors. `t7xx_dpmaif_dl_snd_hw_bat_cnt()`, `_frg_cnt()`, and `t7xx_dpmaif_dlq_add_pit_remain_cnt()` return released DL buffers/PIT entries to hardware. Stop functions disable UL/DL queues and poll idle/sync.

Control flow and state: `struct dpmaif_hw_info` holds MMIO base, per-queue base addresses/counts, and interrupt enable masks. Initialization programs shared BAT/frag BAT and per-DLQ PIT tables, then UL DRB queues. Interrupt handling classifies status into semantic events consumed by `t7xx_hif_dpmaif.c`.

Dependencies and integration points: depends on `t7xx_reg.h`, `t7xx_dpmaif.h`, bitfield helpers, IO polling, and the HIF DPMAIF layer.

Risks and test signals: readiness polling timeouts, interrupt mask polarity, shared BAT assumptions, hardware/software index mismatch, and queue stop loops are key risks. Test modem boot data-path init, RX/TX interrupt delivery, PIT/BAT refill, suspend/resume, and error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.h

Purpose: declares DPMAIF hardware-facing constants, queue counts, interrupt enums, queue property structures, initialization parameters, and exported register-layer APIs.

Important APIs/types: `DPMAIF_RXQ_NUM` is 2 and `DPMAIF_TXQ_NUM` is 5. `struct dpmaif_isr_en_mask` tracks enabled interrupt masks. `struct dpmaif_ul` and `struct dpmaif_dl` store hardware queue state and DMA base/counts. `struct dpmaif_hw_info` owns device pointer, PCIe register base, queue arrays, and masks. `struct dpmaif_hw_params` passes software-allocated DRB/BAT/frag/PIT DMA addresses into hardware init. `enum dpmaif_hw_intr_type` gives HIF code semantic interrupt types.

Control flow and state: this header forms the boundary between DPMAIF HIF code and low-level MMIO implementation. HIF allocates rings, fills `dpmaif_hw_params`, calls hardware init, and later uses exported functions to add/release descriptors and unmask interrupts.

Dependencies and integration points: depends on Linux bit/type macros and `t7xx_reg.h` constants indirectly through implementation. It is included by HIF DPMAIF TX/RX and orchestration code.

Risks and test signals: queue-count mismatches, interrupt type mismatches, and constants like PIT sequence value or DRB word size can break datapath operation. Build all DPMAIF users and test queue init, interrupt decoding, and descriptor-count updates on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.c

Purpose: implements the high-level CLDMA host interface for t7xx control channels, managing GPD rings, TX/RX workqueues, runtime PM, PCIe sleep locks, CLDMA interrupts, and modem PM callbacks.

Important APIs/functions: `t7xx_cldma_init()` registers PM entity, creates ordered workqueues, and hooks the PCIe interrupt. `t7xx_cldma_switch_cfg()` configures shared or dedicated queue sizing and performs late ring allocation. `t7xx_cldma_start()` programs TX/RX ring start addresses, starts RX queues, and enables interrupts. `t7xx_cldma_send_skb()` maps an outgoing SKB to a TX GPD, waits for budget if needed, disables PCIe sleep, and starts/resumes hardware. RX is drained by `t7xx_cldma_gpd_rx_collect()` and delivered through `t7xx_port_proxy_recv_skb()` callbacks. TX completions are reclaimed by `t7xx_cldma_gpd_tx_collect()`. PM callbacks split suspend/resume into TX and RX phases.

Control flow and state: `struct cldma_ctrl` owns eight TX/RX queues, queue active bitmaps, DMA pool, rings, hardware info, PM entity, and init state. Each queue has ring pointers (`tr_done`, `tx_next`, `rx_refill`), budget, waitqueue, lock, and ordered worker. GPD HWO bits synchronize ownership with hardware.

Dependencies and integration points: depends on low-level CLDMA ops, t7xx PCIe MAC interrupts, MHCCIF masking, port proxy receive callbacks, runtime PM, DMA pools, and PCIe sleep-lock helpers.

Risks and test signals: GPD ownership races, runtime PM failures, TX budget waits, RX refill allocation, PCIe disconnect handling, and suspend/resume ordering are high risk. Test heavy control traffic, queue-full TX, dedicated dump queue config, modem reset, PCIe link loss, and PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.h

Purpose: declares high-level CLDMA HIF structures and APIs used by t7xx modem control and port layers.

Important APIs/types: `enum cldma_id` distinguishes MD and AP CLDMA instances. `struct cldma_gpd` defines the DMA descriptor layout with flags, allowed/data lengths, next pointer, and data pointer. `struct cldma_request` binds one GPD, DMA address, SKB, mapped buffer, and list node. `struct cldma_ring` owns request lists and packet size. `struct cldma_queue` tracks queue direction, ring pointers, budget, locks, workqueue, waitqueue, and RX callback. `struct cldma_ctrl` owns all queues, rings, active bitmaps, DMA pool, PM entity, and hardware info.

Control flow and state: public functions allocate/init/exit CLDMA, switch queue configuration, start/stop/reset, send SKBs, and clear queues. Queue state is shared between HIF workers, interrupt handlers, PM callbacks, and port proxy users.

Dependencies and integration points: includes low-level CLDMA definitions, PCI device types, DMA pool, SKBs, workqueues, and t7xx PCI state. It is consumed by modem ops and port proxy layers.

Risks and test signals: descriptor layout and queue pointer invariants are critical. Tests should cover both CLDMA instances, all queues, shared/dedicated configs, TX send API return codes, reset cleanup, and build compatibility across PM/debug configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.c

Purpose: orchestrates the t7xx DPMAIF data path above the register layer, tying RX/TX software resources, hardware initialization, PCIe interrupts, modem state callbacks, and PM callbacks together.

Important APIs/functions: `t7xx_dpmaif_hif_init()` allocates `dpmaif_ctrl`, registers PM entity, registers PCIe IRQ handlers, allocates RX/TX software rings/workers, and returns the controller. `t7xx_dpmaif_start()` builds `dpmaif_hw_params` from allocated queues, allocates initial BAT/frag buffers, initializes hardware, gives BAT counts to hardware, clears interrupts, marks state `PWRON`, enables IRQs, and wakes TX. `t7xx_dpmaif_irq_cb()` converts hardware interrupt events into TX done or RX NAPI scheduling and error logging/unmasking. `t7xx_dpmaif_md_state_callback()` starts or stops DPMAIF based on modem state. Suspend/resume callbacks stop/start queues and interrupts.

Control flow and state: `dpmaif_ctrl->state` gates interrupts and lifecycle. `dpmaif_sw_init_done` gates exit. RX queues use `DPMAIF_INT`/`DPMAIF2_INT`; IRQ top halves mask PCIe INT and threaded handlers do decode/unmask. Software allocation creates shared BAT resources, RX queues, TX queues, TX thread, and BAT release workqueue.

Dependencies and integration points: depends on DPMAIF hardware layer, DPMAIF RX/TX helpers, t7xx PCIe MAC interrupt plumbing, t7xx PM entity registration, state monitor, and network callbacks.

Risks and test signals: error unwinding around shared BAT freeing, interrupt state before `PWRON`, modem exception/stop races, and suspend/resume queue state are key risks. Test modem boot/exception/stop, IRQ storms, PM cycles, and allocation-failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.h

Purpose: defines the DPMAIF HIF software data structures shared by RX, TX, orchestration, and netdev layers.

Important APIs/types: `struct t7xx_skb_cb` stores netif index, TX queue, and RX packet type in SKB control buffer. BAT structures model hardware BAT entries plus software SKB/page tracking. `struct dpmaif_bat_request` owns coherent BAT table, bus address, write/release indexes, software buffer table, bitmap, refcount, lock, and type. `struct dpmaif_rx_queue` owns PIT table/indexes, shared BAT refs, NAPI, current RX assembly state, and processing flags. `struct dpmaif_tx_queue` owns DRB table/indexes, TX budget, workqueue, lock, waitqueue, and queued SKBs. `struct dpmaif_ctrl` owns hardware info, queues, shared BATs, interrupts, PM entity, TX thread, callbacks, and state.

Control flow and state: RX consumes PIT descriptors to pull normal BAT SKBs and fragment BAT pages; TX queues DRBs. `t7xx_ring_buf_*` helpers provide common ring math. `dpmaif_callbacks` integrate state notifications and SKB delivery with the network layer.

Dependencies and integration points: includes DPMAIF hardware definitions, t7xx PCI, state monitor, SKBs, NAPI, workqueues, and netdevice types.

Risks and test signals: shared BAT refcounts, bitmap/index consistency, SKB control-buffer use, and NAPI/sleep-lock state need careful validation. Test RX fragmentation, TX queue full, multi-netif delivery, and teardown with pending NAPI/work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_rx.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_rx.c

Purpose: implements the DPMAIF receive path for t7xx, including BAT/PIT allocation, RX buffer provisioning, PIT parsing, fragmented packet assembly, NAPI polling, BAT/PIT release back to hardware, and RX shutdown cleanup.

Important APIs/functions: `t7xx_dpmaif_bat_alloc()` allocates coherent BAT rings plus software SKB/page tables and bitmaps. `t7xx_dpmaif_rx_buf_alloc()` fills normal BAT entries with DMA-mapped SKBs and optionally notifies hardware. `t7xx_dpmaif_rx_frag_alloc()` fills fragment BAT entries with page fragments. `t7xx_dpmaif_napi_rx_poll()` acquires PCIe sleep lock, drains PIT entries within budget, completes/unmasks RX interrupts, and releases PM references. `t7xx_dpmaif_rx_start()` walks PIT descriptors, parses MSG PIT metadata, consumes PD PIT payload/fragment descriptors, assembles SKBs, and delivers them through `callbacks->recv_skb()`. `t7xx_dpmaif_bat_release_work()` releases consumed BAT entries and allocates replacements.

Control flow and state: RX queues track PIT read/write/release indexes and expected PIT sequence. Normal BAT SKBs and fragment BAT pages are marked consumed in bitmaps, then batch-released when thresholds are reached. Current packet assembly lives in `rx_data_info` until a non-continuation PIT completes the packet.

Dependencies and integration points: depends on DPMAIF hardware index APIs, t7xx PCI sleep-lock/runtime PM, NAPI/GRO, DMA mapping, page fragments, and netdev callbacks in `t7xx_netdev`.

Risks and test signals: PIT sequence polling, fragment bounds, SKB tailroom, BAT bitmap/index mismatch, sleep-lock retry, and shutdown while NAPI runs are high risk. Test fragmented and non-fragmented RX, checksum flags, multi-queue interrupts, malformed PITs, BAT refill thresholds, PM suspend, and modem stop/exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_rx.c -->
