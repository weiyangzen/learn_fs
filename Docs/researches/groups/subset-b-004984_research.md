# Research: subset-b-004984

This grouped report covers the requested NTB, NuBus, and NVDIMM source files. Each file section is bounded by reconciliation markers so it can be split into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/ntb_hw_switchtec.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/ntb_hw_switchtec.c

## Purpose
Implements the Microsemi/Microchip Switchtec NTB hardware provider. It binds to `switchtec_class` devices, identifies a peer partition, exports `struct ntb_dev_ops`, configures direct and LUT memory windows, manages shared link state, scratchpads, doorbells, messages, and crosslink operation. It is the low-level driver that higher NTB clients such as transport, test, perf, and tool drivers consume through the generic NTB API.

## Important APIs, Types, And Functions
- `struct shared_mw` is the 64 KiB shared control window format. It stores `SWITCHTEC_NTB_MAGIC`, software link state, partition id, advertised memory-window sizes, and 128 scratchpads.
- `struct switchtec_ntb` is the full provider state: embedded `struct ntb_dev`, Switchtec device pointer, partition ids, MMIO register blocks, shared MW mappings, doorbell masks/shifts, direct/LUT MW counts, link status, and async link work.
- `switchtec_ntb_ops` wires the provider to the generic NTB core: MW count/alignment/translation, peer MW address, link up/down, doorbells, scratchpads, and peer address helpers.
- `switchtec_ntb_part_op()` serializes Switchtec partition operations by writing `partition_op` and polling `partition_status` for lock/config/reset transitions.
- `switchtec_ntb_mw_set_trans()` validates peer index, window index, size and address alignment, locks peer control registers, programs direct BAR or LUT translation, commits config, and cleans up on hardware-reported errors.
- `switchtec_ntb_init_crosslink()` handles special crosslink topology by enumerating the virtual peer partition BARs, reserving LUT windows, mirroring requester IDs, mapping peer DB/message registers through a local window, and changing topology to `NTB_TOPO_CROSSLINK`.
- `switchtec_ntb_init_shared_mw()` allocates coherent memory for local shared state, reserves peer LUT entry 0 to expose it, and maps the peer shared window through BAR0.
- `switchtec_ntb_init_db_msg_irq()` assigns Switchtec vectors for doorbells and messages and registers `switchtec_ntb_doorbell_isr()` / `switchtec_ntb_message_isr()`.

## Control Flow
Module init registers a class interface on `switchtec_class`. `switchtec_ntb_add()` filters Switchtec bridge devices, allocates `switchtec_ntb`, initializes partition/MMIO pointers, discovers MW capabilities, programs requester IDs, optionally initializes crosslink, initializes doorbell/message mappings, allocates and maps the shared MW, requests IRQs, sends `MSG_LINK_FORCE_DOWN` to stale peers, and registers the NTB device.

Link enable writes local `self_shared->link_sta`, sends a link message, and recomputes link status. Link status is considered up only when local software state is set and the peer shared MW contains the Switchtec magic plus its high 32-bit link flag. Link and forced-down messages schedule `check_link_status_work`, which either reinitializes the peer shared MW or runs normal link status update and emits `ntb_link_event()`.

Memory-window setup is peer-control-register driven. Direct windows program BAR control/size/translation registers; LUT windows program LUT entries. Direct BAR0 has special layout because LUT regions consume the front of the BAR and the direct shared area starts after `LUT_SIZE * nr_lut_mw`. The driver advertises local MW sizes in the shared page and uses the peer shared page for inbound alignment/size queries.

Doorbells use either split halves of a shared DBMSG block or all bits in crosslink mode. The driver shifts local and peer bits according to partition ordering, masks/unmasks with a spinlock-protected cached mask, clears by writing IDB bits, and rings the peer by writing ODB bits. Message IRQs inspect each inbound message slot, clear status, and treat slot 0 as link-control traffic.

Removal clears the Switchtec notifier, unregisters the NTB device, frees IRQs, unmaps/free shared MW resources, unmaps crosslink windows, cancels work, and frees provider state.

## State And Persistence
Persistent hardware-facing state lives in Switchtec NTB control registers, DBMSG registers, BAR/LUT configuration, requester-ID tables, and the coherent shared MW. In-memory state caches partition ids, masks, MW maps, and link status. Scratchpad values are stored in `self_shared->spad[]` and exposed to peers via the reserved shared window. Link status persists across host crashes from the peer perspective, hence probe sends `MSG_LINK_FORCE_DOWN` to force stale software state down.

## Dependencies And Integration Points
Depends on `linux/switchtec.h` register definitions, PCI resource/iomap APIs, coherent DMA allocation, interrupts, workqueues, and the generic NTB core. It integrates with Switchtec core through `stdev->sndev` and `stdev->link_notifier`, and with NTB clients through `ntb_register_device()`. Upper layers rely on correct MW alignment, peer DB addressing, scratchpad storage, and link event notifications.

## Risks And Edge Cases
- MW translation requires size-power alignment of the DMA address; CMA or large coherent allocations can violate this and return `-EINVAL`.
- `switchtec_ntb_spad_read()` and peer helpers compute `ARRAY_SIZE(sndev->peer_shared->spad)` before null checks; normal initialization sets mappings first, but failures or unexpected calls before mapping would be risky.
- Crosslink setup relies on enumerating virtual BARs and mapping peer DBMSG through a reserved LUT; failures leave partial hardware state unless later cleanup handles it.
- `config_req_id_table()` logs `-EIO` errors but returns `0`, which could hide requester-ID programming failures.
- Doorbell vector mask accepts `db_vector > 1` as invalid, so vector `1` still returns a mask despite `db_vector_count()` returning one vector; consumers normally query vector 0.
- Shared MW and register operations are hardware-coordination sensitive; link churn, peer reset, or stale peer shared data can produce transient false-down or forced-down events.

## Test Signals
Useful validation comes from loading the provider on Switchtec NTB hardware, checking `ntb_transport` link creation, exercising doorbells/scratchpads with `ntb_pingpong` and `ntb_tool`, running `ntb_perf` across direct/LUT windows, and testing crosslink hardware if available. Build coverage should include `CONFIG_NTB`, Switchtec support, and optional clients. Runtime logs around `failed to register ntb device`, `Error setting up reserved lut window`, `Hardware reported an error configuring mw`, and `ntb link up/down` are strong diagnostic signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/ntb_hw_switchtec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/msi.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/msi.c

## Purpose
Provides a generic NTB MSI helper library. It reserves peer and inbound memory windows so a peer can trigger local MSI interrupts by writing the MSI data value into an NTB-mapped address, and it exposes helpers for clients to allocate IRQs, exchange descriptors, and trigger peer interrupts.

## Important APIs, Types, And Functions
- `struct ntb_msi` holds the mapped peer MSI windows, local accepted MSI address range, and an optional descriptor-change callback.
- `ntb_msi_init()` allocates `ntb->msi`, stores the callback, and maps the last peer MW for each peer.
- `ntb_msi_setup_mws()` reserves the highest inbound MW for every peer, aligns the first local MSI descriptor address to all peer MW constraints, programs translations, and records `[base_addr, end_addr)`.
- `ntb_msi_clear_mws()` clears those reserved inbound translations.
- `ntbm_msi_request_threaded_irq()` finds an unused PCI MSI descriptor, requests a managed IRQ, fills `struct ntb_msi_desc`, and installs a `write_msi_msg` hook to update the descriptor if the PCI MSI message changes.
- `ntb_msi_peer_trigger()` writes descriptor data into the mapped peer MSI window at `addr_offset / sizeof(u32)`.

## Control Flow
A client first calls `ntb_msi_init()`. On link up or after MSI allocation is valid, it calls `ntb_msi_setup_mws()` to make local MSI target addresses reachable from peers. The helper reads the first associated MSI descriptor under the MSI descriptor lock, aligns it for all peer highest-MW constraints, then programs each peer's highest inbound MW. Clients then allocate one or more IRQs through `ntbm_msi_request_threaded_irq()`, exchange the generated `ntb_msi_desc` out of band, and call `ntb_msi_peer_trigger()` with a peer descriptor to raise a remote interrupt.

If the PCI core rewrites an MSI message, `ntb_msi_write_msg()` refreshes the exported descriptor and calls the client's `desc_changed` callback, allowing the new descriptor to be sent to peers.

## State And Persistence
The library attaches transient state to `ntb->msi` using devm allocation. It persists peer MW ioremaps and the local MSI address window while the NTB device is alive. IRQ requests and callback resources are devres-managed. Descriptor contents are volatile and must be re-exchanged after setup, message changes, or link reset.

## Dependencies And Integration Points
Depends on the generic NTB MW APIs, PCI MSI descriptors, managed IRQ allocation, and `linux/msi.h`. It is used by `ntb_transport.c` when `CONFIG_NTB_MSI` and `use_msi` are enabled, and by `ntb_msi_test.c`.

## Risks And Edge Cases
- `ntb_msi_setup_mws()` assumes at least one associated MSI descriptor exists; a missing descriptor would make `msi_first_desc()` unsafe.
- The error unwind loop uses `ntb_peer_highest_mw_idx(ntb, peer)` while iterating `i`, which appears suspicious because `peer` is the failed peer value, not the cleanup index.
- `ntb_msi_peer_trigger()` does not range-check `peer`, descriptor offset, or peer window mapping; clients must validate exchanged descriptors.
- Stale descriptors after PCI MSI rewrites can trigger the wrong address/data unless the client handles `desc_changed`.
- The helper reserves highest MWs, so clients must subtract or avoid those MWs.

## Test Signals
`ntb_msi_test` is the direct functional test: peers should exchange descriptors through scratchpads and debugfs `trigger` should increment peer interrupt occurrence counters. `ntb_transport` with `use_msi=1` validates integration with queue interrupts. Build coverage needs `CONFIG_NTB_MSI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/ntb_transport.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/ntb_transport.c

## Purpose
Implements the software queue-pair transport layer over NTB. It registers an `ntb_transport` bus for higher-level clients, negotiates MW and queue parameters through scratchpads, creates queue pairs, copies TX payloads into peer-visible MWs by CPU or DMA, receives payloads from local MW buffers, and signals peers with doorbells or optional NTB MSI.

## Important APIs, Types, And Functions
- `struct ntb_transport_ctx` is per-NTB-device state: MW vector, QP vector, queue bitmap, MSI settings, link work, client devices, and debugfs node.
- `struct ntb_transport_qp` is a queue pair with TX/RX rings, free/pending/post lists, DMA channels, MSI descriptors, tasklet, delayed link work, callbacks, stats, and optional TX-copy kthread.
- `struct ntb_transport_mw` tracks peer-visible outbound mapping plus local coherent inbound buffer and translation.
- `ntb_transport_register_client_dev()` / `ntb_transport_unregister_client_dev()` create/remove transport client devices across all active NTB transports.
- `ntb_transport_register_client()` registers a transport client driver on the custom bus.
- `ntb_transport_create_queue()` allocates a free QP, installs callbacks, optional DMA channels, RX/TX entries, unmasks DB, and returns the QP.
- `ntb_transport_tx_enqueue()` and `ntb_transport_rx_enqueue()` are the core data-plane APIs for clients.
- `ntb_transport_link_up()` / `ntb_transport_link_down()` mark client readiness and coordinate QP link bits.

## Control Flow
Probe requires inbound MW translation support, optionally reserves the last MW for MSI, checks scratchpad capacity, maps peer MW BARs, derives QP count from doorbell bits/MW count/client limit, initializes QPs, registers the NTB context, joins the transport bus list, enables the NTB link, and triggers a link event.

The device-level link work writes local MW sizes, QP count, MW count, and protocol version to peer scratchpads, reads the peer's matching values, programs local inbound MW translations sized from the peer's advertised MWs, partitions each MW among QPs, and schedules QP link work for ready clients. QP link work sets the local QP ready bit in the peer scratchpad and waits until the peer also advertises the bit, then marks the QP active and schedules receive processing.

TX enqueue removes a free TX entry, stores callback/data/length, checks frame size and ring space, writes length and version into the peer-visible header, copies payload by DMA if configured and aligned or by `memcpy_toio()`, marks `DESC_DONE_FLAG`, orders/flushes the posted write, rings the peer by MSI or doorbell, calls the TX completion callback, and returns the entry to the TX free list.

RX processing runs in a tasklet after doorbell/MSI. It checks the local RX header's done/link-down flags and version, moves a pending client buffer to the post queue, copies payload by DMA or CPU, marks the entry done, clears the header, updates remote RX index (`qp->rx_info->entry`) for peer flow control, invokes the RX callback, and continues until the ring is empty or a fairness limit is hit.

Teardown cleans link state, sends link-down messages when clients request link down, masks DB, kills tasklets, stops optional TX-copy threads, waits/terminates DMA, frees all queue entries, clears MW translations, unmaps peer BARs, unregisters transport bus devices, and frees state.

## State And Persistence
State is volatile in memory, scratchpads, doorbells/MSI descriptors, and MW translations. Scratchpads are explicitly cleared during link cleanup because hardware may retain values across remote resets. The queue protocol persists ring indices in shared MW headers and `struct ntb_rx_info`, while QP ownership is tracked by `qp_bitmap_free`. Debugfs stats expose byte/packet/error counters while the QP is active.

## Dependencies And Integration Points
Depends on generic NTB APIs, DMAengine, PCI/ioremap, debugfs, tasklets, kthreads, workqueues, and optional NTB MSI helper. It is a middle layer between NTB providers such as Switchtec and consumers that register `struct ntb_transport_client`.

## Risks And Edge Cases
- Only two-port NTB devices are supported (`PIDX` fixed to default peer), despite warnings for multi-port devices.
- Queue state is split across spinlocks, tasklets, work items, DMA callbacks, and optional kthreads; teardown ordering is critical.
- `last_cookie` is shared for TX/RX DMA waits, so concurrent channel use may make termination diagnostics less precise.
- `ntb_transport_tx_free_entry()` trusts `remote_rx_info`; stale or unmapped MW state can corrupt flow-control decisions.
- Link negotiation depends on both sides using the exact protocol version, QP count, and MW count.
- Optional MSI consumes a doorbell bit and the highest MW; incorrect accounting breaks QP or MW count.
- CPU copy to WC/I/O memory relies on barriers and posted-write flushes before interrupting the peer.

## Test Signals
Build with NTB core, DMAengine, optional MSI, and transport clients. Runtime validation includes transport client probe/remove, link-up/down churn, ping tests over QPs, DMA and CPU copy modes, `use_msi=1`, `tx_memcpy_offload=1`, and debugfs `stats` counters. Watch for RX version mismatches, ring-full/no-buffer counters, stale scratchpad values after reset, and clean queue free without warnings about non-empty queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/ntb_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/test/Kconfig

## Purpose
Defines Kconfig entries for NTB test/debug clients: ping-pong, manual debug tool, raw performance tool, and MSI test.

## Important APIs, Types, And Functions
This file has no C APIs. It declares:
- `NTB_PINGPONG`: simple scratchpad/doorbell test client.
- `NTB_TOOL`: debugfs-driven NTB operation exerciser.
- `NTB_PERF`: raw MW transfer performance tool.
- `NTB_MSI_TEST`: MSI-over-NTB test client, depending on `NTB_MSI`.

## Control Flow
Kconfig selection controls which test modules are compiled. The `tristate` entries permit built-in or module builds and default to off by user choice.

## State And Persistence
No runtime state. It affects build configuration only.

## Dependencies And Integration Points
Integrates with the NTB test Makefile and NTB subsystem menu. `NTB_MSI_TEST` correctly guards itself behind the MSI helper.

## Risks And Edge Cases
The test clients expose low-level hardware access and should remain opt-in. Dependency declarations are minimal; build errors in optional APIs may surface only when selected.

## Test Signals
Menuconfig should show all four entries. `NTB_MSI_TEST` should be unavailable unless `NTB_MSI` is enabled. Module builds should produce corresponding objects through the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/test/Makefile

## Purpose
Maps NTB test Kconfig symbols to module objects.

## Important APIs, Types, And Functions
No runtime APIs. It builds:
- `ntb_pingpong.o` for `CONFIG_NTB_PINGPONG`
- `ntb_tool.o` for `CONFIG_NTB_TOOL`
- `ntb_perf.o` for `CONFIG_NTB_PERF`
- `ntb_msi_test.o` for `CONFIG_NTB_MSI_TEST`

## Control Flow
The kernel build system includes each object when its config symbol is `y` or `m`.

## State And Persistence
Build-only state. No runtime persistence.

## Dependencies And Integration Points
Relies on the sibling Kconfig symbols and the broader NTB build hierarchy.

## Risks And Edge Cases
No complex logic. The main risk is config/object name drift if source files or symbols are renamed.

## Test Signals
Selecting each config should produce the matching built-in object or module without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_msi_test.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_msi_test.c

## Purpose
Provides a debugfs test client for the NTB MSI helper. It allocates local MSI IRQs, shares their trigger descriptors through scratchpads, learns peer descriptors after doorbell notifications, and exposes debugfs knobs to trigger peer interrupts and read occurrence counts.

## Important APIs, Types, And Functions
- `struct ntb_msit_ctx` stores the NTB device, setup work, local ISR contexts, and flexible peer array.
- `struct ntb_msit_isr_ctx` tracks an allocated IRQ, descriptor, and occurrence count.
- `struct ntb_msit_peer` tracks peer index, descriptor array, IRQ count, and completion.
- `ntb_msit_setup_work()` sets MSI MWs, requests up to `num_irqs` MSI IRQs, writes descriptors to scratchpads, publishes count in scratchpad 0, and rings peers.
- `ntb_msit_db_event()` reads peer descriptor counts and descriptor scratchpads after doorbell events.
- Debugfs files expose peer `trigger`, `ready`, `count`, `port`, local `port`, and per-IRQ occurrence counters.

## Control Flow
Probe validates peer count and scratchpad capacity, initializes scratchpad 0 to `-1`, unmasks peer doorbells, initializes the MSI helper, allocates context, creates debugfs, sets NTB context callbacks, and enables link. Link-up schedules setup work. Setup work programs MSI MWs and publishes descriptors. Doorbell events copy peer descriptors and complete peer readiness. Writing a peer `trigger` debugfs file calls `ntb_msi_peer_trigger()` with the selected descriptor.

## State And Persistence
Local IRQ descriptors live in `isr_ctx`. Peer descriptors are heap allocated and replaced on each doorbell event. Scratchpads persist the descriptor exchange protocol: count in slot 0, then address offset/data pairs. Occurrence counts are volatile counters incremented by the ISR.

## Dependencies And Integration Points
Depends on `ntb_msi_init()`, `ntb_msi_setup_mws()`, `ntbm_msi_request_irq()`, scratchpads, doorbells, debugfs, and NTB link callbacks.

## Risks And Edge Cases
- Uses scratchpad indices `2 * i + 1/2`; `num_irqs` must fit `2 * num_irqs + 1`.
- `ntb_msit_db_event()` iterates over all bits in a 64-bit mask and indexes `peers[peer]`; valid doorbell masks must match actual peer count.
- Descriptor updates are not separately synchronized with debugfs trigger reads; stale descriptor arrays are possible during link churn.
- Probe contains a redundant `if (!nm->isr_ctx)` after allocation already succeeded.

## Test Signals
After link-up, debugfs peer `ready` should complete, `count` should equal published IRQ count, writing `trigger` should increment the peer's `irqN_occurrences`, and descriptor-change logs should be followed by successful peer triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_msi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_perf.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_perf.c

## Purpose
Implements an NTB raw performance measuring client. It negotiates inbound/outbound memory windows with peers, maps peer windows, then copies configurable amounts of data to the peer window using CPU MMIO writes or DMA to report throughput through debugfs.

## Important APIs, Types, And Functions
- `enum perf_cmd` defines the control protocol for exchanging sizes, translation addresses, clear events, done status, and link state.
- `struct perf_ctx` is per-device state, including peer descriptors, command transport callbacks, test threads, debugfs, and synchronization.
- `struct perf_peer` stores per-peer inbound/outbound MW mappings, translation addresses, service work, status bits, and init completion.
- `struct perf_thread` is a worker that copies data, tracks DMA synchronization, copied bytes, duration, and status.
- `perf_init_service()` selects message-register command transport when available, otherwise scratchpad/doorbell transport.
- `perf_service_work()` executes the command state machine: send size, setup inbound buffer, send xlat, setup outbound translation, or clear.
- `perf_submit_test()` launches worker threads against a selected peer and waits for completion.
- Debugfs files `info`, `run`, and `threads_count` expose configuration, status, execution, and results.

## Control Flow
Probe allocates context, derives global peer indices, maps each outbound peer MW, initializes work threads, selects command service, sets NTB callbacks, unmasks either message or doorbell events, enables link, and creates debugfs. Link events mark peers up/down and enqueue size or clear commands. Command receive decodes peer messages/scratchpads and schedules service work to allocate inbound buffers and program MW translations. Once both sides exchange size and translation, the peer completion is signaled.

Writing a peer index to `run` waits for peer init, marks the test busy, initializes per-thread state, queues copy workers, and waits until the atomic thread counter reaches zero. Workers allocate random source buffers, optionally request DMA channels and map peer MMIO resources, loop until `1 << total_order` bytes are copied in chunks up to `1 << chunk_order`, then synchronize DMA and record duration. Reading `run` formats per-thread throughput or error status.

## State And Persistence
State is volatile in peer status bits, completions, scratchpad/message command slots, MW translations, DMA mappings, worker state, and debugfs. Link-down clear commands free inbound/outbound translations and abort active tests. Module parameters `max_mw_size`, `chunk_order`, `total_order`, and `use_dma` influence runtime behavior.

## Dependencies And Integration Points
Depends on NTB peer MW APIs, inbound MW translation, doorbells, scratchpads or messages, DMAengine, workqueues, waitqueues, debugfs, and PCI DMA mapping. It is a consumer of hardware providers and a validation tool for MW throughput.

## Risks And Edge Cases
- Global-index calculation and scratchpad layout are subtle for multi-port NTB topologies.
- Command transport assumes single in-flight message slots and retry loops; busy or stale status can return `-EAGAIN`.
- DMA mapping of peer MMIO resources and source pages is sensitive to DMA alignment and NUMA channel selection.
- `perf_set_tcnt()` and result reads serialize with `busy_flag`; interruptions must terminate all workers and DMA waits.
- Link-down while a test is active frees MWs and terminates work, so cleanup ordering is important.
- Large `total_order`/thread counts can allocate substantial memory and run long tests.

## Test Signals
Functional tests include loading with CPU copy and DMA modes, checking debugfs `info` for peer mappings, writing peer index to `run`, reading throughput results, changing `threads_count`, and bouncing links during tests. Logs for command service selection, `Failed to set inbuf/outbuf translation`, DMA map failures, or `Freeing while test on-fly` identify integration issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_pingpong.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_pingpong.c

## Purpose
Implements a simple NTB ping-pong client that exercises link events, doorbells, scratchpads, and message registers. It selects an active peer, periodically writes a counter to peer scratchpad/message register, rings a peer doorbell, and counts received responses.

## Important APIs, Types, And Functions
- `struct pp_ctx` stores NTB device, timer, inbound/outbound doorbell masks, selected peer, peer masks, count, lock, and debugfs dir.
- `pp_check_ntb()` validates doorbell safety, scratchpad/message availability, and doorbell bit layout.
- `pp_find_next_peer()` selects a linked peer, preferring next peers then previous peers.
- `pp_ping()` writes counter to peer scratchpad/message and rings peer DB.
- `pp_pong()` reads received scratchpad/message values, increments count, clears/remasks inbound DB, and restarts timer.
- `pp_setup()` and `pp_clear()` arm/cancel the timer and mask DBs.

## Control Flow
Probe validates the NTB device, allocates context, computes local inbound DB and peer masks, masks events, sets NTB callbacks, enables link, triggers a link event, and creates debugfs. On link events, setup masks inbound DB, selects a linked peer, and starts a timer. Timer expiry sends a ping. Doorbell events call `pp_pong()`, which observes received data, increments the counter, clears/masks DB state, and schedules the next ping.

## State And Persistence
Only volatile kernel state is used. The peer-visible counter is stored transiently in scratchpad/message registers. Debugfs exposes `count`. Module parameters are `unsafe` and `delay_ms`.

## Dependencies And Integration Points
Depends on NTB link, doorbell, scratchpad, optional message APIs, hrtimer, debugfs, and atomic counters. It is a quick provider sanity test rather than a data transport.

## Risks And Edge Cases
- Uses port numbers as doorbell bit numbers; hardware must expose a matching valid mask.
- Message and scratchpad values can differ because message status must be cleared before rewriting.
- If all peers are down, setup cancels the ping-pong loop.
- `unsafe=1` is required to run on providers marking DB/SPAD unsafe; otherwise probe fails.

## Test Signals
`/sys/kernel/debug/ntb_pingpong/<dev>/count` should increase while both peers are loaded and linked. Link drops should stop and link returns should resume. Debug logs should show ping/pong counter values and selected peer ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_pingpong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_tool.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_tool.c

## Purpose
Provides a comprehensive debugfs NTB exerciser. It exposes local and peer ports, link control, doorbells, scratchpads, messages, inbound MW allocation, outbound MW translation/mapping, and raw MW read/write operations to user space.

## Important APIs, Types, And Functions
- `struct tool_ctx` is per-device state containing waitqueues, peer descriptors, local message/scratchpad descriptors, outbound MW descriptors, and debugfs root.
- `struct tool_peer` holds per-peer inbound MW descriptors, outbound MW wrappers, outgoing messages/scratchpads, and peer debugfs directory.
- `struct tool_mw` represents either an inbound coherent buffer or an outbound ioremapped peer window depending on union member use.
- `tool_ops` handles link, DB, and message events by waking waitqueues.
- `tool_setup_mw()` allocates coherent inbound MW memory, validates alignment, programs inbound translation, and creates an `mwN` data file.
- `tool_setup_peer_mw()` programs peer outbound translation, maps the peer MW BAR, and creates a `peer_mwN` data file.
- `tool_setup_dbgfs()` creates the full debugfs file hierarchy.

## Control Flow
Probe allocates context and peer arrays, initializes inbound/outbound MW metadata, scratchpad metadata, message metadata, sets NTB callbacks, and creates debugfs. Link writes call `ntb_link_enable()` or disable. Doorbell/message/link event files block on waitqueues until the requested state/status appears. MW translation files allocate/free mappings on writes, while MW data files read/write memory buffers or MMIO mappings. Remove tears down debugfs, clears NTB context, disables link, frees MWs, and wakes waiters.

## State And Persistence
State is debugfs-driven and volatile. Inbound MW buffers are coherent DMA allocations until the corresponding translation is cleared or the module is removed. Outbound mappings remain until freed. Waitqueues track asynchronous hardware events. Hardware register state may persist outside the module unless explicitly cleared through the exposed operations.

## Dependencies And Integration Points
Depends on nearly all generic NTB provider operations, debugfs, coherent DMA allocation, ioremap WC, user copy helpers, waitqueues, and PCI DMA resources. It is a manual integration and debugging tool for NTB providers.

## Risks And Edge Cases
- Exposes raw low-level hardware operations to privileged user space; misuse can program bad translations or write arbitrary peer-visible memory.
- `tool_setup_peer_mw()` stores outbound windows globally by `widx`, so a window can be attached to only one peer at a time.
- Several files call provider ops only after checking pointer presence for some APIs, but not all optional APIs are guarded uniformly.
- Event waits compare exact DB/message status values; unrelated bits can keep waits blocked.
- Memory-window size/address inputs come from userspace and rely on provider validation for correctness.

## Test Signals
Debugfs hierarchy should reflect provider capabilities: ports, DB masks, SPADs, messages, and per-peer MW translation files. Manual tests can enable link, block on link events, ring/clear DBs, write/read SPADs/messages, allocate inbound MWs, map outbound MWs, and verify data across peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_tool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nubus/Makefile

## Purpose
Builds the NuBus core objects and optional procfs support.

## Important APIs, Types, And Functions
No runtime APIs. It always builds `nubus.o` and `bus.o`; it builds `proc.o` when `CONFIG_PROC_FS` is enabled.

## Control Flow
The kernel build system includes core NuBus scanning/resource code and bus registration code unconditionally for this directory, plus procfs helpers when configured.

## State And Persistence
Build-only state.

## Dependencies And Integration Points
Integrates with NuBus source files and `CONFIG_PROC_FS`.

## Risks And Edge Cases
No complex logic. Procfs resource exposure is compile-time optional.

## Test Signals
NuBus builds should include core bus support, and procfs symbols should resolve only when `CONFIG_PROC_FS=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/bus.c -->
# sources/distributed-fs/ceph-client/drivers/nubus/bus.c

## Purpose
Implements the Linux driver-model bus layer for NuBus boards. It registers the `nubus` bus type, exposes driver register/unregister helpers, registers scanned board devices, releases associated resources, and provides a proc summary callback.

## Important APIs, Types, And Functions
- `nubus_bus_type` defines bus name, probe, and remove callbacks.
- `nubus_driver_register()` / `nubus_driver_unregister()` export driver-model registration for `struct nubus_driver`.
- `nubus_device_register()` initializes `struct nubus_board.dev`, names it `slot.X`, sets DMA mask, and registers it.
- `nubus_device_release()` frees functional resources associated with a board and then the board.
- `nubus_proc_show()` iterates devices and prints slot/name summaries.

## Control Flow
`postcore_initcall(nubus_bus_register)` registers the bus early. Scanning code later calls `nubus_device_register()` for each discovered board. Driver binding calls the optional NuBus driver `probe()` and `remove()` methods through bus callbacks.

## State And Persistence
Device-model state persists while board devices are registered. Functional resources are globally listed in `nubus_func_rsrcs` and removed when the board device is released.

## Dependencies And Integration Points
Depends on `linux/nubus.h`, driver core, DMA mask helpers, global NuBus resource list from `nubus.c`, and procfs sequence output.

## Risks And Edge Cases
- Release walks and mutates the global functional resource list without an explicit lock; this is acceptable for early/static NuBus lifecycle but would matter if hotplug existed.
- Device names are slot-based; duplicate registration for a slot would conflict.
- `dma_set_mask()` return value is ignored.

## Test Signals
On Macintosh NuBus systems, board devices should appear on the `nubus` bus as `slot.X`, drivers should bind via `nubus_driver_register()`, and `/proc/nubus` should list slot names when procfs is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/nubus.c -->
# sources/distributed-fs/ceph-client/drivers/nubus/nubus.c

## Purpose
Scans Macintosh NuBus slots, reads card ROMs through bytelane-aware accessors, parses board and functional sResource directories, populates kernel NuBus resource structures, optionally mirrors resources into procfs, and registers board devices with the NuBus bus.

## Important APIs, Types, And Functions
- `nubus_get_rom()`, `nubus_advance()`, `nubus_rewind()`, and `nubus_move()` implement bytelane-aware ROM traversal.
- `nubus_dirptr()`, `nubus_get_rsrc_mem()`, `nubus_get_rsrc_str()`, and `nubus_seq_write_rsrc_mem()` read resource data blocks/strings.
- `nubus_get_root_dir()`, `nubus_get_board_dir()`, `nubus_get_func_dir()`, `nubus_get_subdir()`, `nubus_readdir()`, and `nubus_find_rsrc()` expose directory traversal to other NuBus code and drivers.
- `nubus_first_rsrc_or_null()` / `nubus_next_rsrc_or_null()` iterate the global functional resource list.
- `nubus_get_board_resource()` and `nubus_get_functional_resource()` parse the board and function resource directories.
- `nubus_probe_slot()` detects valid format block bytelanes; `nubus_add_board()` builds board state; `nubus_scan_bus()` scans slots 9 through 14.

## Control Flow
`subsys_initcall(nubus_init)` exits unless running on Macintosh hardware. It initializes procfs, registers the parent `nubus` device, and scans slots. Slot probing checks possible bytelanes at the end of each slot address space using `hwreg_present()` and the mirrored nybble format-block marker. A valid slot is parsed by rewinding to the format block, reading ROM metadata, computing the directory pointer from signed 24-bit offset data, parsing the first board resource, then parsing remaining functional resources.

Functional resource parsing fills category/type/software/hardware ids, names, driver directory information, memory offset/length, flags, and private resources for display/network/CPU categories. Valid resources are inserted in ascending ID order into `nubus_func_rsrcs`. The completed board is registered as a device.

## State And Persistence
Global state includes `nubus_populate_procfs`, `LIST_HEAD(nubus_func_rsrcs)`, and the static parent device. Allocated `struct nubus_board` and `struct nubus_rsrc` objects persist until device release. Procfs resource trees are optional and disabled by default through the `nubus.populate_procfs` module parameter.

## Dependencies And Integration Points
Depends on Macintosh architecture setup (`MACH_IS_MAC`), fixed NuBus slot address space assumptions, `hwreg_present()`, `linux/nubus.h` resource ids, proc helper functions, and `nubus_device_register()` from `bus.c`. Exported directory/resource helpers are used by NuBus drivers.

## Risks And Edge Cases
- ROM traversal must respect bytelanes; incorrect mask handling reads bogus resources.
- Pointer movement logs when it leaves slot address space but does not hard fail.
- Many allocations use atomic context during init; failures skip resources or boards.
- Resource order sanity check drops duplicate or non-ascending functional resource ids.
- Procfs population can be expensive for some ROMs and is disabled by default.
- The code assumes classic Macintosh NuBus physical address layout.

## Test Signals
On supported Macintosh hardware, boot logs should show NuBus slot scanning and resource debug output. `/proc/nubus` should list boards, and `/proc/bus/nubus/devices` should list functional resources. Driver resource lookup through exported helpers should find expected category/type ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/nubus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/proc.c -->
# sources/distributed-fs/ceph-client/drivers/nubus/proc.c

## Purpose
Implements procfs views for NuBus board and resource information. It provides `/proc/nubus`, `/proc/bus/nubus/devices`, and optional per-board resource trees that mirror NuBus ROM resource directories.

## Important APIs, Types, And Functions
- `nubus_devices_proc_show()` prints each functional resource's slot, category/type/software/hardware ids, and slot address.
- `nubus_proc_add_board()` creates a board slot directory if resource procfs population is enabled.
- `nubus_proc_add_rsrc_dir()` creates resource subdirectories and stores bytelane data as parent private data.
- `struct nubus_proc_pde_data` records resource pointer and size, or a small inline integer resource.
- `nubus_proc_rsrc_show()` emits resource memory through `nubus_seq_write_rsrc_mem()` or emits a 3-byte integer resource.
- `nubus_proc_add_rsrc_mem()` / `nubus_proc_add_rsrc()` create per-resource proc files.
- `nubus_proc_init()` creates the top-level proc entries.

## Control Flow
NuBus init calls `nubus_proc_init()`. During ROM parsing, `nubus.c` calls the add helpers as it discovers boards, directories, and resources. The helpers no-op unless `/proc/bus/nubus` exists and `nubus_populate_procfs` is enabled. Reads dispatch through `single_open()` and `seq_read()`.

## State And Persistence
Proc directory pointer `proc_bus_nubus_dir` persists after init. Per-resource proc entries store heap-allocated `nubus_proc_pde_data`, but this file does not define an explicit release callback for that private data. Resource data points into slot ROM addresses or stores small integer values in the pointer field.

## Dependencies And Integration Points
Depends on procfs, seq_file, NuBus resource traversal helpers from `nubus.c`, and `nubus_populate_procfs`. It also uses parent proc private data to recover bytelanes for resource memory reads.

## Risks And Edge Cases
- Per-resource `nubus_proc_pde_data` allocations may not be explicitly freed when proc entries are removed.
- `nubus_proc_rsrc_show()` returns `-EFBIG` if the resource size exceeds the current seq buffer, so large resources may not be readable.
- Integer resources are emitted as raw bytes, not formatted text.
- The proc resource tree is deprecated/disabled by default because some ROMs make it expensive.

## Test Signals
With procfs enabled, `/proc/nubus` and `/proc/bus/nubus/devices` should exist. With `nubus.populate_procfs=1`, per-slot resource directories and files should appear and resource reads should match ROM data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nubus/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/Kconfig

## Purpose
Defines build configuration for the libnvdimm subsystem, persistent memory block devices, BTT, PFN, DAX, device-tree PMEM, RAMDAX, key/security support, KMSAN interaction, and unit-test build helpers.

## Important APIs, Types, And Functions
No runtime APIs. Key symbols:
- `LIBNVDIMM`: top-level NVDIMM support, requiring 64-bit physical addresses, I/O memory, and block layer.
- `BLK_DEV_PMEM`: PMEM block device and DAX-capable namespace support.
- `BTT` / `ND_BTT`: block translation table support for atomic sector semantics.
- `NVDIMM_PFN` / `ND_PFN`: struct-page support for persistent memory.
- `NVDIMM_DAX`: raw device-DAX namespace access.
- `OF_PMEM` and `RAMDAX`: non-ACPI persistent memory descriptions.
- `NVDIMM_KEYS`, `NVDIMM_KMSAN`, `NVDIMM_TEST_BUILD`, and `NVDIMM_SECURITY_TEST`: security/debug/test integration.

## Control Flow
Kconfig dependency and select relationships determine which object groups the Makefile builds and which features are reachable. Most feature symbols live under `if LIBNVDIMM`.

## State And Persistence
Build-time configuration only. Runtime persistent-memory behavior is determined by selected symbols.

## Dependencies And Integration Points
Integrates with block, DAX, ZONE_DEVICE, encrypted keys, KMSAN, OF, e820/legacy PMEM, and compile-test infrastructure.

## Risks And Edge Cases
- `NVDIMM_KMSAN` warns about permanent capacity impact because `struct page` metadata stored in pmem can grow with memory-debug options.
- Security-test options alter cache-maintenance behavior for unit tests and should stay off for normal systems.
- Defaults choose many features when `LIBNVDIMM` is enabled, so minimal builds must opt out deliberately.

## Test Signals
Configuration tests should verify symbol visibility under dependencies, default selections, and module/built-in combinations. Compile tests should cover `NVDIMM_TEST_BUILD` on x86_64 `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/Makefile

## Purpose
Maps NVDIMM Kconfig symbols to built objects and composes the `libnvdimm` aggregate module/object.

## Important APIs, Types, And Functions
No runtime APIs. It builds top-level objects for `libnvdimm`, `nd_pmem`, `nd_btt`, legacy e820 PMEM, OF PMEM, virtio PMEM, and RAMDAX. `libnvdimm-y` includes core, bus, DIMM, region, namespace, label, badrange, and optional perf, claim, BTT, PFN, DAX, and security files.

## Control Flow
The kernel build system includes object fragments according to `CONFIG_*` values. `TOOLS` and `TEST_SRC` locate the nvdimm unit-test `iomap.o` when `CONFIG_NVDIMM_TEST_BUILD` is enabled.

## State And Persistence
Build-only state.

## Dependencies And Integration Points
Integrates directly with `drivers/nvdimm/Kconfig`, PMEM/BTT/DAX/security source files, virtio PMEM helpers, and the tools testing source tree.

## Risks And Edge Cases
Object list drift can cause unresolved symbols or missing feature code. The test-build object path reaches outside the driver directory into `tools/testing/nvdimm/test`, so source tree layout matters.

## Test Signals
Build matrix should cover `LIBNVDIMM`, `BLK_DEV_PMEM`, `ND_BTT`, `NVDIMM_PFN`, `NVDIMM_DAX`, `NVDIMM_KEYS`, `VIRTIO_PMEM`, and `NVDIMM_TEST_BUILD` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/badrange.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/badrange.c

## Purpose
Maintains NVDIMM bad physical address ranges and converts them into namespace-relative `badblocks` entries for pmem regions. This supports persistent-memory error tracking discovered during bus initialization or ARS processing.

## Important APIs, Types, And Functions
- `badrange_init()` initializes the badrange list and spinlock.
- `badrange_add()` adds or updates a physical bad range; duplicates by start address update length.
- `badrange_forget()` removes a cleared physical interval from the badrange list, deleting, trimming, or splitting entries.
- `__add_badblock_range()` converts byte offsets and lengths to 512-byte sectors and handles ranges larger than `INT_MAX` sectors.
- `badblocks_populate()` intersects global bad ranges with a namespace resource range and adds matching sector ranges.
- `nvdimm_badblocks_populate()` validates the region is pmem, locks the NVDIMM bus, and populates a supplied `struct badblocks`.

## Control Flow
NVDIMM bus setup initializes and adds ranges as they are discovered. When errors are cleared, `badrange_forget()` walks all list entries under spinlock and mutates the list based on overlap with the clear interval. When a namespace/region needs badblocks, `nvdimm_badblocks_populate()` finds the parent bus, takes the bus guard, and calls `badblocks_populate()` to translate physical address intersections into namespace-relative sector entries.

## State And Persistence
The main state is the `struct badrange` list of `struct badrange_entry { start, length }`, protected by `badrange->lock`. Entries persist for the lifetime of the bus or until forgotten. The derived `badblocks` state is populated separately for block-layer consumers.

## Dependencies And Integration Points
Depends on libnvdimm bus/region structures, `badblocks`, block-sector conventions, `struct range`, device guards, and internal `nd-core.h` / `nd.h` helpers such as `walk_to_nvdimm_bus()` and `is_memory()`.

## Risks And Edge Cases
- `add_badrange()` drops the spinlock for allocation and reacquires it; concurrent additions are handled by duplicate search after reacquire, but ordering remains append-only.
- `badrange_forget()` split path ignores allocation failure from `alloc_and_append_badrange_entry(..., GFP_NOWAIT)`, so clearing the middle of a range can lose the right half if allocation fails.
- Address arithmetic uses inclusive end values (`start + len - 1`); zero lengths would underflow and should not be passed.
- Overlapping ranges are intentionally not normalized on insertion; consumers must tolerate overlap when converting to badblocks.
- `nvdimm_badblocks_populate()` is only valid for pmem regions and warns otherwise.

## Test Signals
Unit tests should add duplicate, overlapping, adjacent, and very large ranges; forget intervals covering head, tail, full, and middle splits; and populate namespaces with ranges inside, outside, and straddling the namespace. Runtime logs from `set_badblock()` and `badblocks_set()` failures help validate conversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/badrange.c -->
