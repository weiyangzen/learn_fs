# subset-b-004391 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_iq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_iq.h

Purpose: Defines the LiquidIO input queue, which is the host-to-Octeon transmit/instruction ring abstraction. It also defines instruction formats and the soft-command buffer model used for firmware control requests.

Important APIs, types, and functions: `struct octeon_instr_queue` holds DMA ring addresses, host/read/flush indexes, pending instruction accounting, doorbell state, locks, stats, queue metadata, and request tracking. `struct octeon_request_list` links each descriptor slot to a host buffer and `REQTYPE_*` cleanup class. `struct octeon_instr_32B`, `struct octeon_instr2_64B`, `struct octeon_instr3_64B`, and `union octeon_instr_64B` describe chip-generation-specific command layouts. `struct octeon_soft_command` adds response DMA buffers, status words, completion, callbacks, expiry, and caller lifetime state. Exported declarations cover queue setup/delete, command posting, flush, soft-command preparation/sending, and soft-command pool management.

Control flow: Other LiquidIO files allocate a queue with `octeon_setup_iq()`, post descriptors with `octeon_send_command()` or `octeon_send_soft_command()`, then reclaim slots through `octeon_flush_iq()` and `lio_process_iq_request_list()`. Soft commands flow through IQ 0 because only that queue sets `allow_soft_cmds`.

State and persistence: State is in kernel memory, coherent DMA rings, atomics, and hardware doorbell/count registers. It is not persistent across driver unload or reset. Concurrency is managed by `lock`, `post_lock`, and `iq_flush_running_lock`.

Dependencies and integration: Depends on `liquidio_common.h` instruction bitfields, `octeon_device` chip hooks, response-manager status codes, and netdev/BQL cleanup helpers in `octeon_main.h`. The request type enum must stay aligned with registered free callbacks.

Risks: Incorrect descriptor sizing, 32B/64B format mismatch, missing memory barriers, or reqtype/free callback mismatches can corrupt DMA, leak SKBs, or stall TX. Soft-command status lifetime is race-sensitive because callers and response polling both observe `caller_is_done`.

Test signals: Exercise queue full/stop/failed statuses, BQL completion accounting, IQ flush under NAPI budget and shutdown, soft-command timeout/zombie handling, and both CN6XXX and CN23XX command layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_iq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.c

Purpose: Implements LiquidIO PF/VF mailbox transfers over paired 64-bit registers. It assembles multiword request/response messages, drives the register ACK/signature protocol, and handles a small set of PF/VF control commands.

Important APIs, types, and functions: `octeon_mbox_read()` consumes one 64-bit mailbox word, advances request or response receive state, and writes `OCTEON_PFVFACK` or `OCTEON_PFVFERR`. `octeon_mbox_write()` serializes `struct octeon_mbox_cmd` after waiting for `OCTEON_PFVFSIG` and per-word ACKs. `octeon_mbox_process_message()` dispatches complete responses to callbacks or complete requests to `octeon_mbox_process_cmd()`. `get_vf_stats()` aggregates IQ and DROQ counters for `OCTEON_GET_VF_STATS`. `octeon_mbox_cancel()` aborts a pending request.

Control flow: Read-side interrupts or pollers call `octeon_mbox_read()` until a full command is received. `octeon_mbox_process_message()` then either invokes a saved response callback, resets error state, or handles commands such as VF active handshake, FLR request, PF-changed MAC propagation, and VF stats response. Writes are synchronous polling loops with 1 ms sleeps and a 1000-iteration cap.

State and persistence: Mailbox state lives in `struct octeon_mbox`: IDLE, REQUEST_RECEIVING, REQUEST_RECEIVED, RESPONSE_PENDING, RESPONSE_RECEIVING, RESPONSE_RECEIVED, and ERROR bits plus saved request/response command buffers. No state persists beyond the driver instance; hardware register contents are used only as a handshake surface.

Dependencies and integration: Includes LiquidIO device, IQ, response, main, and CN23XX PF definitions. It calls `pcie_flr()`, `octeon_pf_changed_vf_macaddr()`, and stats fields from instruction/output queues. It assumes callers hold mailbox objects set up with correct PF/VF read/write register addresses.

Risks: The protocol is sensitive to stale signatures, partial multiword transfers, and concurrent state changes. Long synchronous waits can delay callers. Invalid state transitions write `OCTEON_PFVFERR`; recovery depends on later process/cancel paths. Stats are read without global queue teardown protection.

Test signals: Cover multiword request/response sequences, busy mailbox returns, timeout/failure exits, error-state callback delivery, VF active version handshake, FLR dispatch, stats response length, and cancellation of pending requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.h

Purpose: Declares the LiquidIO mailbox protocol shared by PF and VF code.

Important APIs, types, and functions: The header defines mailbox command IDs (`OCTEON_VF_ACTIVE`, `OCTEON_VF_FLR_REQUEST`, `OCTEON_PF_CHANGED_VF_MACADDR`, `OCTEON_GET_VF_STATS`), handshake sentinels (`OCTEON_PFVFACK`, `OCTEON_PFVFSIG`, `OCTEON_PFVFERR`), transfer limits, and wait constants. `union octeon_mbox_message` packs type, response-needed bit, command, length, and six parameter bytes into a 64-bit first word. `struct octeon_mbox_cmd` stores header, up to 32 data words, queue number, receive length/status, and callback. `struct octeon_mbox` owns the lock, queue number, state, hardware register pointers, and in-flight request/response buffers.

Control flow: Users build `struct octeon_mbox_cmd`, call `octeon_mbox_write()`, and later process completed responses through `octeon_mbox_read()` plus `octeon_mbox_process_message()`. Request handlers reuse the same command object to send responses when needed.

State and persistence: State is explicit bitmask state in `enum octeon_mbox_state`. It is volatile driver state backed by memory-mapped mailbox registers.

Dependencies and integration: Depends on `struct octeon_device`, `struct cavium_wk`, and `struct oct_vf_stats` from surrounding LiquidIO headers. It forms the PF/VF control plane used by CN23XX SR-IOV support.

Risks: Message `len` must be bounded to `OCTEON_MBOX_DATA_MAX`; callers must respect request vs response state rules. Bitfield layout and endian assumptions matter because the first word is exchanged with firmware/peer function.

Test signals: Validate packed header fields, max-length transfers, request-without-response cleanup, response callback status, and state transitions after error and cancel paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_main.h

Purpose: Provides common LiquidIO driver definitions used across host driver files: device-private tasklet data, TX buffer free metadata, BAR mapping helpers, endian helpers, soft-command wait semantics, and rounding macros.

Important APIs, types, and functions: `struct octeon_device_priv` ties a device to DROQ tasklet/NAPI state. `struct octnet_buf_free_info` stores the `lio`, `skb`, gather list, DMA pointer, and optional piggybacked soft command needed when TX descriptors are reclaimed. BQL hooks are declared for sent/completed byte accounting. `octeon_swap_8B_data()` converts 64-bit blocks to big endian. `octeon_map_pci_barx()` and `octeon_unmap_pci_barx()` request/release PCI BAR regions and ioremap/iounmap them. `wait_for_sc_completion_timeout()` centralizes blocking wait and timeout/error translation for soft commands.

Control flow: Probe/setup code maps BARs through the inline helpers. Control-command senders wait on `sc->complete`; response-manager code completes the soft command or marks timeout, while this helper sets `caller_is_done` when wait exits abnormally.

State and persistence: The file manipulates volatile PCI BAR mappings, soft-command lifetime flags, and netdev/BQL state. No durable storage is involved.

Dependencies and integration: Includes Linux signal scheduling, PCI/netdev structures, LiquidIO `struct lio`, `octeon_soft_command`, and response status codes. It is included widely and therefore defines cross-module contracts.

Risks: BAR index multiplication assumes LiquidIO BAR layout. Soft-command waiting is race-sensitive: callers must set `caller_is_done` after consuming successful responses so response cleanup can safely free buffers.

Test signals: Probe failure paths for BAR request/ioremap, soft-command wait timeout/interruption/fatal timeout, BQL accounting on TX reclaim, and big/little endian command preparation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.c

Purpose: Implements host access to Octeon core memory through PCI BAR1 mappings, including byte-range reads/writes and 32/64-bit accessors.

Important APIs, types, and functions: `octeon_pci_fastread()` and `octeon_pci_fastwrite()` copy unaligned leading/trailing bytes with byte I/O and aligned bodies with 64-bit I/O, toggling BAR1 swap mode on big-endian hosts. `__octeon_pci_rw_core_mem()` selects an existing console static mapping when possible, otherwise locks `mem_access_lock`, programs the dynamic BAR1 index, splits transfers at 4 MB BAR1 entry boundaries, copies data, restores the original index register, and unlocks. Public exports are `octeon_pci_read_core_mem()`, `octeon_pci_write_core_mem()`, `octeon_read_device_mem64()`, `octeon_read_device_mem32()`, and `octeon_write_device_mem32()`.

Control flow: Callers pass a core address and host buffer. The helper maps the address through BAR1 index `BAR1_INDEX_DYNAMIC_MAP`, performs the transfer, and advances address/buffer pointers until complete.

State and persistence: It temporarily modifies BAR1 index registers and possibly swap mode. The only persistent effect is the requested device-memory write; software state is restored after dynamic access.

Dependencies and integration: Depends on chip-specific `fn_list.bar1_idx_read/write/setup`, `oct->mmio[1]`, `console_nb_info`, and `mem_access_lock`. Exported symbols are used by console, diagnostics, and firmware interaction code.

Risks: The boundary calculation is delicate; incorrect copy length can overrun BAR1 windows. Locking protects the shared dynamic mapping, so bypassing it elsewhere can corrupt accesses. Endianness handling must match hardware expectations.

Test signals: Read/write across unaligned addresses, BAR1 4 MB boundaries, static console mapping hit, dynamic mapping restore, big-endian swap-mode behavior, and concurrent memory operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.h

Purpose: Declares LiquidIO Octeon core-memory access routines.

Important APIs, types, and functions: `octeon_read_device_mem64()` and `octeon_read_device_mem32()` read a single big-endian value from a core address and return host-endian data. `octeon_write_device_mem32()` writes a host-endian 32-bit value after conversion. `octeon_pci_read_core_mem()` and `octeon_pci_write_core_mem()` transfer arbitrary byte ranges between host buffers and Octeon memory.

Control flow: Higher-level code uses these APIs when it needs direct access to firmware/device memory rather than queue-based command submission. The C implementation handles BAR1 mapping and alignment details.

State and persistence: Function calls can read or mutate device memory. The header itself defines no state, but its APIs imply side effects on device memory and BAR1 registers.

Dependencies and integration: Requires `struct octeon_device` and the BAR1 mapping machinery from `octeon_device` function hooks. Used by diagnostics, console paths, and other low-level driver setup code.

Risks: These are low-level MMIO memory primitives; callers must pass valid core addresses, lengths, and live device pointers. They bypass command queue ordering, so use during reset or concurrent firmware access needs care.

Test signals: Compile coverage for all declarations, value endian round trips, partial buffer transfers, invalid/reset-device call avoidance, and callers that cross BAR1 entry boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_network.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_network.h

Purpose: Defines the LiquidIO per-netdev state, RX/TX buffer helpers, queue state helpers, and external network-facing function contracts.

Important APIs, types, and functions: `struct lio` is the central per-interface private structure: interface state, IQ/OQ indexes, gather-list pools, Octeon device pointer, link info, queue sizes, capabilities, PTP state, workqueues, and stats work. `struct octnic_gather` describes DMA gather components. Inline RX helpers allocate SKBs/pages, map pages, recycle page halves, reuse buffers, destroy/free buffers, and map ring buffer addresses. TX queue helpers stop, wake, and start netdev subqueues. `wait_for_pending_requests()` waits for ordered soft-command drain. Declarations expose feature, queue setup, interrupt, ethtool, stats, speed/FEC, and MTU operations.

Control flow: Main LiquidIO netdev code uses this header to allocate receive buffers for DROQs, map DMA addresses into rings, reclaim buffers, and coordinate queue start/stop with link state and IQ pressure.

State and persistence: State is volatile per-interface and per-buffer state in atomics, workqueues, DMA mappings, SKB control blocks, PTP fields, and linked lists. It is rebuilt at probe/open.

Dependencies and integration: Depends on netdevice, PTP, LiquidIO common protocol types, `octeon_droq`, `octeon_iq`, and response-manager constants. It bridges the generic Linux network stack to LiquidIO queue machinery.

Risks: SKB control block reuse requires consistent `struct octeon_skb_page_info` layout. DMA mapping failures, NUMA page mismatch, page refcount checks, and queue-index modulo logic are key correctness points. Atomic ifstate helpers are simple read-modify-write sequences, not compare-and-swap loops.

Test signals: RX allocation failure and recycle fallback, DMA map/unmap balance, page reuse across NUMA nodes, TX subqueue wake accounting, pending request drain on shutdown, MTU bounds, and PTP timestamp receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_network.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.c

Purpose: Provides LiquidIO NIC-facing helpers that convert network data and control operations into Octeon instruction queue submissions.

Important APIs, types, and functions: `octeon_alloc_soft_command_resp()` wraps a prebuilt `union octeon_instr_64B` in a soft command, adds response metadata (`rflag`, RDP, response pointer, status word), and sets expiry. `octnet_send_nic_data_pkt()` posts a data command with optional doorbell suppression for `xmit_more`. `octnic_alloc_ctrl_pkt_sc()` allocates a soft command for NIC control commands, copies/swaps the command payload, appends user-defined data, prepares an OPCODE_NIC control instruction, and initializes completion. `octnet_send_nic_ctrl_pkt()` gates control commands while offline, sends the soft command, optionally returns immediately for no-sleep multicast/devflags commands, otherwise waits for completion and runs a callback.

Control flow: Data packets are already encoded by `octeon_nic.h` helpers and go straight to `octeon_send_command()`. Control packets allocate from the soft-command pool, enter IQ 0, move through ordered response processing, then complete or time out.

State and persistence: Uses transient soft-command DMA buffers, command response lock/state, completion status, and caller-done lifetime markers. No durable persistence.

Dependencies and integration: Integrates `octeon_iq`, `response_manager`, `octeon_main` wait helpers, and LiquidIO firmware opcodes. It is called by netdev setup, ethtool, link, multicast, and feature-control code.

Risks: Offline gating permits only RX control, so callers must handle failures. Immediate-return control commands rely on response-manager cleanup after `caller_is_done`. Endian swapping of command and UDD payloads must match firmware contract.

Test signals: Control send success/failure, offline rejection, no-sleep command lifetime, response timeout, callback invocation, xmit_more doorbell behavior, and CN23XX vs CN6XXX response field placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.h

Purpose: Declares NIC data/control packet structures and inline command builders for LiquidIO host-to-firmware network operations.

Important APIs, types, and functions: `struct octnic_ctrl_pkt` carries firmware control command, optional data/response buffers, UDD words, IQ selection, originating netdev, callback, and status. `struct octnic_data_pkt` carries host buffer cleanup type, byte count, prepared instruction, and IQ. `union octnic_cmd_setup` captures IQ, gather flag, timestamp flag, checksum offload bits, and data/gather count. `octnet_iq_is_full()` reports IQ pressure. `octnet_prepare_pci_cmd_o2()` and `_o3()` build CN6XXX and CN23XX data instructions, respectively, setting front-size, tag, group/QPG, raw/gather bits, data length, opcode/subcode, and packet parameter OSSP. `octnet_prepare_pci_cmd()` selects layout by chip.

Control flow: TX paths fill `octnic_cmd_setup`, call the prepare helper, then submit with `octnet_send_nic_data_pkt()`. Control paths use `octnet_send_nic_ctrl_pkt()` and soft-command response support.

State and persistence: The header builds transient command descriptors and inspects live IQ occupancy. It defines no durable state.

Dependencies and integration: Depends on LiquidIO firmware command formats in `liquidio_common.h`, `octeon_iq.h`, and queue metadata in `octeon_device`. It bridges netdev TX features to firmware instruction fields.

Risks: Incorrect chip detection or bitfield packing breaks packet delivery. Gather count vs data length must be correct. Timestamp and checksum flags are passed to firmware in `packet_params`, so feature negotiation must be consistent.

Test signals: Generated command fields for CN6XXX and CN23XX, scatter-gather vs linear packets, checksum/tunnel/timestamp flags, queue full threshold, and control command callback/status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/request_manager.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/request_manager.c

Purpose: Implements LiquidIO instruction queue lifecycle, command posting, descriptor reclaim, doorbell timeout handling, and soft-command buffer pool management.

Important APIs, types, and functions: `octeon_setup_iq()` and `octeon_init_instr_queue()` allocate queue objects, coherent DMA rings, request lists, locks, queue masks, chip register setup, and per-IQ delayed doorbell-check workqueues. `octeon_send_command()` posts one descriptor through `__post_command2()`, records request cleanup metadata, updates stats/BQL, and rings the doorbell when thresholds or force conditions require it. `octeon_flush_iq()` updates Octeon read index, processes fetched requests, decrements pending instructions, and honors NAPI budget. `lio_process_iq_request_list()` frees no-response network buffers or moves response-bearing soft commands to `OCTEON_ORDERED_SC_LIST`. Soft-command APIs allocate fixed 2048-byte coherent buffers, align context/data/response regions, prepare chip-specific control instructions, send them, and return buffers to pool/done/zombie lists.

Control flow: TX/control producers post commands to IQs; hardware fetches descriptors; interrupts, NAPI, or delayed work call flush; request-list entries are freed or enqueued for ordered response polling. Doorbell timeout work periodically flushes stale queues and reenables IRQs.

State and persistence: State includes DMA rings, request lists, queue indexes, pending atomics, stats, workqueues, global reqtype cleanup callbacks, and soft-command pool/done/zombie lists. All are volatile.

Dependencies and integration: Uses chip config for instruction size/db thresholds, `fn_list` queue operations, BQL helpers, response-manager lists, and netdev buffer cleanup callbacks.

Risks: Queue wrap protection leaves one slot free; bugs around pending counts, flush indexes, or barriers can corrupt the ring. The global `reqtype_free_fn` table must be registered before reclaim. Soft-command pool exhaustion returns NULL; zombie cleanup handles late firmware writes.

Test signals: IQ allocation failure unwind, descriptor full/stop behavior, doorbell batching/timeout, concurrent flush exclusion, NAPI budget partial reclaim, soft-command pool exhaustion, response vs no-response cleanup, and shutdown drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/request_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.c

Purpose: Manages LiquidIO soft-command response lists and ordered response completion polling.

Important APIs, types, and functions: `octeon_setup_response_list()` initializes all response list heads, locks, pending counters, command response lock, and the `dma-comp` workqueue. `lio_process_ordered_list()` first frees caller-finished done-list entries, then inspects the head of `OCTEON_ORDERED_SC_LIST`, reads the DMA status word, validates that the full 64-bit firmware status has been written, translates firmware status, handles timeouts/force quit, moves commands to done or zombie lists, completes waiters, or invokes callbacks. `oct_poll_req_completion()` is delayed-work polling that reschedules while ordered responses remain.

Control flow: Request reclaim code adds response-bearing soft commands to the ordered list once Octeon has fetched the instruction. This file preserves ordered semantics by processing only from the head until it finds a pending entry or reaches `MAX_ORD_REQS_TO_PROCESS`.

State and persistence: Response state is in list heads, locks, pending counters, soft-command status fields, completion objects, and the workqueue. No state persists after delete.

Dependencies and integration: Depends on `octeon_iq.h` soft-command layout and `octeon_main.h` byte swapping. It cooperates with request-manager done/zombie/free functions and control senders waiting on completions.

Risks: Status-word validation is intentionally conservative; wrong endian handling or premature status use can report false completion. Callbacks free their own commands, while non-callback commands are freed via done-list cleanup, so lifetime rules differ. A pending head blocks later ordered responses.

Test signals: Successful firmware completion, nonzero firmware status translation, timeout path, callback vs completion path, zombie movement, done-list cleanup, reschedule behavior, and processing cap enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.h

Purpose: Defines LiquidIO response list structures, response ordering classes, and host/firmware request status codes.

Important APIs, types, and functions: `struct octeon_response_list` is a locked list with a pending counter. Response list IDs include ordered, unordered, ordered soft-command, done soft-command, and zombie soft-command lists. Response-order enum values describe ordered, unordered, and no-response requests. Driver and firmware status macros encode major/minor error namespaces, and `FIRMWARE_STATUS_CODE()` maps firmware 16-bit statuses into the host-visible status space. Public functions initialize/delete response lists and process the ordered list.

Control flow: Request-manager code moves fetched soft commands into `OCTEON_ORDERED_SC_LIST`; response-manager code moves them to done/zombie or invokes callbacks; callers interpret `OCTEON_REQUEST_*` values.

State and persistence: The header defines volatile list state only. Status values are protocol-level constants shared with firmware-facing logic.

Dependencies and integration: Requires Linux list, spinlock, atomic primitives, and `struct octeon_device`. It is included by request, response, NIC control, mailbox, and memory-operation files.

Risks: Adding/removing list types or changing status codes would affect cleanup and user-visible control command results. The processing cap protects CPU time but can delay large bursts.

Test signals: Initialization of all list heads/counters, status-code mapping, timeout and interrupted status propagation, and no leak between done/zombie/ordered lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/Makefile

Purpose: Build glue for Cavium Octeon management Ethernet support.

Important APIs, types, and functions: The file contains a single Kbuild rule: `obj-$(CONFIG_OCTEON_MGMT_ETHERNET) += octeon_mgmt.o`.

Control flow: During kernel build, enabling `CONFIG_OCTEON_MGMT_ETHERNET` compiles and links `octeon_mgmt.c` into the relevant built-in or module object according to the parent networking driver build.

State and persistence: No runtime state. It controls compilation only.

Dependencies and integration: Depends on the Kconfig symbol being selected in the Cavium network driver configuration. It integrates with parent `drivers/net/ethernet/cavium/Makefile`.

Risks: If the symbol is unset, the platform driver and management Ethernet support are absent. If object naming changes, this Makefile must track it.

Test signals: Kernel build with `CONFIG_OCTEON_MGMT_ETHERNET=y/m`, object presence in build logs, and no stale references after renaming source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/octeon_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/octeon_mgmt.c

Purpose: Implements the Cavium Octeon MII management-port netdev driver for platform devices compatible with `cavium,octeon-5750-mix`.

Important APIs, types, and functions: `struct octeon_mgmt` stores MIX/AGL register bases, port/IRQ, TX/RX DMA rings, SKB queues, NAPI, tasklet, PHY node, link cache, and resource metadata. RX helpers fill the input ring with DMA-mapped SKBs, dequeue completed ring entries, handle split packets, process optional RX timestamps, and run under NAPI. TX helpers map SKBs into output ring entries, request TX timestamps, ring hardware, and clean completions in a tasklet. `octeon_mgmt_open()` allocates rings, resets/configures hardware, initializes PHY, requests IRQ, enables interrupts/NAPI, and starts queues. `octeon_mgmt_stop()` reverses that. Probe maps resources, sets netdev ops/ethtool ops, configures MTU bounds, MAC, PHY, DMA mask, and registers the netdev.

Control flow: IRQ reads and clears MIX ISR, disables RX/TX interrupt sources, schedules NAPI or TX cleanup, then each bottom half reenables its interrupt source. Link changes reprogram AGL GMX speed/duplex/clocking under lock.

State and persistence: Runtime state is in netdev stats, SKB queues, DMA rings, hardware CSRs, PHY state, and timestamp flags. No persistent storage.

Dependencies and integration: Uses Octeon CSR accessors, OF platform resources, PHY framework, netdev/NAPI/tasklet APIs, hardware timestamping, and ethtool link operations.

Risks: DMA ring fill/clean counters must match SKB queues. RX split-packet assembly can fail under memory pressure. Hardware timestamp support is CN6XXX-specific. Open error unwinding returns `-ENOMEM` for several failure classes, which may hide root cause.

Test signals: Probe/remove with missing resources, open/stop leak checks, RX packet and split-packet receive, TX queue stop/wake, IRQ/NAPI/tasklet interaction, PHY link changes, MTU changes, multicast/promisc filtering, and hwtstamp set/get.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/octeon_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/Makefile

Purpose: Build glue for Cavium Thunder Ethernet drivers.

Important APIs, types, and functions: Kbuild rules include `thunder_xcv.o` under `CONFIG_THUNDER_NIC_RGX`, `thunder_bgx.o` under `CONFIG_THUNDER_NIC_BGX`, `nicpf.o` under `CONFIG_THUNDER_NIC_PF`, and `nicvf.o` under `CONFIG_THUNDER_NIC_VF`. Composite objects map `nicpf-y := nic_main.o` and `nicvf-y := nicvf_main.o nicvf_queues.o nicvf_ethtool.o`.

Control flow: Enabling PF builds `nic_main.c`; enabling VF links main, queues, and ethtool support into the VF driver object.

State and persistence: No runtime state. It controls build composition.

Dependencies and integration: Depends on Thunder Kconfig symbols and source files in the same directory. It expresses the separation between PF mailbox/global hardware driver and VF netdev/queue/ethtool driver.

Risks: Omitting `nicvf_ethtool.o` removes user-visible diagnostics and configuration. PF/VF symbols can be built independently, but runtime SR-IOV requires both sides where VFs are used.

Test signals: Matrix builds for each `CONFIG_THUNDER_NIC_*` symbol, module object composition, and link success after symbol changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic.h

Purpose: Defines the shared Thunder NIC PF/VF protocol, device constants, VF private state, statistics structures, RSS state, mailbox messages, and helper declarations.

Important APIs, types, and functions: Constants cover PCI IDs, BARs, VF/MSI-X counts, frame-size bounds, queue counts, interrupt masks, RSS sizes, timeout values, and silicon revision helpers. `struct nicvf` is the VF netdev state with queue sets, XDP, secondary queue sets, link, RSS, pause, workqueues, timestamping, stats, NAPI, MSI-X, and mailbox state. `struct nicvf_hw_stats` and `struct nicvf_drv_stats` back ethtool counters. Mailbox message structs encode PF/VF operations for queue setup, RSS, MAC, FRS, BGX stats/link, secondary queue sets, loopback, stats reset, pause, PTP, and multicast filtering. `union nic_mbx` is the fixed two-word shared mailbox payload.

Control flow: VF code sends `union nic_mbx` commands to PF; `nic_main.c` interprets them and writes hardware registers or calls BGX helpers. VF ethtool and netdev paths use declarations here to reconfigure queues, RSS, stats, and timestamps.

State and persistence: State is volatile in PF/VF driver memory, hardware registers, and mailbox registers. No persistent configuration is stored here.

Dependencies and integration: Includes netdevice, interrupt, PCI, and `thunder_bgx.h`. It is shared by `nic_main.c`, `nicvf_main.c`, `nicvf_queues.c`, and `nicvf_ethtool.c`.

Risks: `BUILD_BUG_ON(sizeof(union nic_mbx) > 16)` in PF enforces the mailbox size; adding fields can break ABI. Bitfield and packed message changes must remain synchronized across PF and VF.

Test signals: Mailbox ABI size, every message type ACK/NACK path, VF queue count and SQS topology, RSS key/table updates, PTP single-packet TX timestamp constraints, and pass1/pass2 silicon feature gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_main.c

Purpose: Implements the Thunder NIC physical-function PCI driver. It initializes global NIC hardware, enables SR-IOV, handles PF mailbox interrupts from VFs, programs PF-owned queue/RSS/scheduler/BGX registers, and arbitrates resources.

Important APIs, types, and functions: `struct nicpf` stores PCI device, hardware capability table, node, flags, enabled VFs, register base, secondary qset maps, VF-to-LMAC map, CPI/RSSI bases, and MSI-X IRQ state. `nic_get_hw_info()` derives chip-specific capacities from subsystem IDs. `nic_init_hw()` enables the block, configures backpressure, TNS bypass, PKIND, timer, VLAN parsing, and CQM drop level. `nic_set_lmac_vf_mapping()` maps LMACs to primary VFs and programs credits. Mailbox handlers configure qsets, RQs/SQs, RSS, CPI, FRS, loopback, pause, PTP timestamping, multicast filters, BGX link/stats, SQS allocation, and VF shutdown. Probe enables PCI, maps BAR0, initializes hardware, registers MSI-X mailbox interrupts, and enables SR-IOV.

Control flow: VF writes a mailbox message; PF mailbox IRQ reads the two-word payload, dispatches by message ID, writes hardware or calls BGX helpers, then sends ACK/NACK or a data response. Shutdown disables VF/BGX LMAC paths and frees SQS allocations.

State and persistence: State is PF driver memory plus NIC/BGX CSRs and SR-IOV enablement. It is recreated on probe and removed on PCI remove.

Dependencies and integration: Uses `nic_reg.h`, `nic.h`, `q_struct.h`, `thunder_bgx.h`, PCI SR-IOV/MSI-X APIs, and relaxed MMIO accesses justified by ThunderX ordering.

Risks: PF trusts many VF-provided indexes after limited validation. Resource maps for SQS and VF/LMAC must stay consistent across VF reset/shutdown. Hardware revision branches change mailbox write order and register programming.

Test signals: Probe/remove unwind, SR-IOV VF count limits, mailbox ACK/NACK for every message, pass1/pass2 behavior, RSS/CPI/scheduler register programming, SQS allocation/free, BGX link and MAC operations, and reset/shutdown races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_reg.h

Purpose: Defines Thunder NIC PF/VF register offsets, register counts, bit shifts, tunnel constants, and the PKIND configuration bitfield.

Important APIs, types, and functions: PF offsets cover global config/status, interrupt timers, mailbox interrupt registers, VLAN/tunnel parser definitions, ECC/BIST, interfaces, MCAM, CPI/MPI/RSSI tables, LMAC credits/config, channel config, RX sync, transmit scheduler TL2/TL3/TL4, VF mailboxes, per-VNIC stats, qset config, and PF MSI-X. VF offsets cover VNIC config, PF mailbox registers, interrupts, RSS config/key, VNIC stats, queue set CQ/RQ/SQ/RBDR registers, and VF MSI-X. Shifts define queue number, queue set ID, VF number, and MSI-X vector layout. `struct pkind_cfg` models min/max length, length-error enable, receive header mode, and header skip.

Control flow: PF and VF drivers compose register addresses by ORing base offsets with shifted VF/qset/queue indexes, then read/write through their MMIO helpers.

State and persistence: The header has no state, but every constant maps to hardware state whose values persist until reset or reprogramming.

Dependencies and integration: Used by Thunder PF main, VF main, queues, and ethtool register dump. Tunnel constants are consumed when PF enables Geneve/NVGRE/VXLAN parsing.

Risks: A wrong offset or shift corrupts unrelated hardware state. `nicvf_get_regs()` depends on register count matching the dump sequence. Bitfield layout in `pkind_cfg` must match endian-specific hardware format.

Test signals: Register dump length/indexing, qset address construction, PF mailbox interrupt masks for 128 VFs, PKIND programming under PTP enable/disable, and tunnel parsing register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nic_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_ethtool.c

Purpose: Implements ethtool operations for the Thunder NIC virtual-function netdev.

Important APIs, types, and functions: Stat descriptor arrays expose hardware, driver, queue, and BGX stats. Link helpers report speed/duplex/port capabilities from PF-provided link state. Stats functions update VF and LMAC stats, aggregate per-CPU driver stats, and append primary/secondary qset queue counters. Register dump functions read VF mailbox, interrupt, RSS, stats, CQ/RQ/SQ/RBDR registers while avoiding a known bus-error register. Ring parameter setters clamp to supported powers of two and restart the interface when running. RSS functions get/set hash fields, indirection table, key, and hash function. Channel setters adjust RX/TX/XDP queue counts and secondary qset count, restart when needed, and update XDP feature flags. Pause operations use PF mailbox `NIC_MBOX_MSG_PFC`. Timestamp info reports Cavium PTP hardware clock support.

Control flow: Users invoke ethtool; operations read cached VF state, MMIO registers, or send mailbox commands to PF for BGX/PFC-backed settings. Some mutating operations stop/open the netdev to rebuild queues.

State and persistence: Updates volatile VF fields such as message level, queue lengths/counts, RSS config/key/table, pause config, and XDP feature flags. Hardware register writes and PF mailbox changes last until reconfiguration/reset.

Dependencies and integration: Depends on `nic.h`, `nic_reg.h`, `nicvf_queues.h`, queue stats helpers, `thunder_bgx.h`, and Cavium PTP common code.

Risks: `nicvf_get_regs()` has a likely typo in the RX stats loop using `stat` instead of `i` for offset construction. Queue/channel changes can fail during reopen, leaving partially updated software counts. RSS changes require RSS enabled and valid hash field combinations.

Test signals: `ethtool -S`, `-d`, `-g/-G`, `-x/-X`, `-l/-L`, `-a/-A`, timestamp info, pass1 ringparam rejection, XDP queue constraints, secondary qset stats, and PF mailbox timeout on pause operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_ethtool.c -->
