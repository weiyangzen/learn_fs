# Research: subset-b-004622

Grouped source research for the SFC EF10/EF100 driver subset. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.c

Purpose: Implements EF100 receive event handling, RX descriptor doorbells, packet prefix decoding, checksum extraction, FCS/drop accounting, and MAE representor steering for packets received on non-base mports.

Important APIs and functions: `ef100_rx_buf_hash_valid()` reads the EF100 RX prefix RSS validity bit. `efx_ef100_ev_rx()` consumes RX completion events and advances `removed_count`. `ef100_rx_write()` writes DMA buffer addresses into RX descriptors and rings `ER_GZ_RX_RING_DOORBELL`. `__ef100_rx_packet()` is the packet finalizer reached through `efx_rx_flush_packet()`. Static helpers decode prefix fields and detect FCS errors.

Control flow: RX events report a packet count. For each packet, the code syncs the DMA buffer, skips the EF100 prefix by advancing `page_offset`, recycles page ownership, flushes any previous packet, then records one fragment in the channel. Finalization reads the prefix before the Ethernet header, optionally lets raw channel handlers consume the packet, drops FCS errors unless `NETIF_F_RXALL` is enabled, validates minimum Ethernet length, handles ingress mport routing, populates checksum state, updates queue byte/packet counters, and passes the skb through GRO.

State and persistence: It mutates per-channel counters such as `n_rx_eth_crc_err`, `n_rx_frm_trunc`, `n_rx_mport_bad`, `n_rx_merge_events`, and `irq_mod_score`; per-queue counters such as `removed_count`, `notified_count`, `rx_packets`, and `rx_bytes`; and RX buffer fields `len` and `page_offset`. No durable persistence exists, but queue indices must remain consistent across interrupt/NAPI processing.

Dependencies and integration points: Depends on EF100 register layout macros from `ef100_regs.h`, queue helpers from `rx_common.h`, NIC data from `ef100_nic.h`, generic flush path from `efx.h`, MCDI common definitions, and optional `CONFIG_SFC_SRIOV` representor functions. It integrates with `efx_channels.c` NAPI polling, RX refill, GRO, netdev feature flags, and MAE mport identity.

Risks: Prefix field decoding is bit-offset sensitive. Bad `removed_count` or descriptor mask handling can desynchronize completions. Mport handling drops unrecognized traffic and representor copies depend on RCU protection. Memory barriers in `ef100_rx_write()` are required before doorbells and before grant-credit work. RXALL changes security/error visibility by accepting FCS-bad frames.

Test signals: Exercise single and merged RX events, short frames, FCS-bad frames with and without RXALL, checksum valid/error paths, representor RX by mport, unknown mport drops, RX refill/doorbell updates, and GRO delivery under NAPI budget.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.h

Purpose: Declares the EF100 RX entry points consumed by the generic SFC channel, RX, and NIC-type dispatch layers.

Important APIs and types: Exports `ef100_rx_buf_hash_valid()`, `efx_ef100_ev_rx()`, `ef100_rx_write()`, and `__ef100_rx_packet()`. It includes `net_driver.h` for `struct efx_channel`, `struct efx_rx_queue`, and `efx_qword_t`.

Control flow and integration: These prototypes bind EF100-specific RX behavior into generic indirect calls in `efx.h` and event dispatch from NIC-specific event processing. `ef100_rx_write()` is used when refilling descriptors; `efx_ef100_ev_rx()` is used when event queues produce RX completions; `__ef100_rx_packet()` is the flush/finalize hook.

State and persistence: The header owns no state. Its ABI shape determines how EF100 RX code is called from shared queue and event code.

Dependencies: Depends on shared SFC data structures from `net_driver.h` and on matching implementations in `ef100_rx.c`.

Risks: Prototype drift would break indirect-call targets or NIC type tables. Including this header in `efx.h` makes circular dependency hygiene important.

Test signals: Compile coverage for EF100 NIC type setup, RX event handling, RX refill, and generic `efx_rx_flush_packet()` indirect calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.c

Purpose: Provides EF100 PCI SR-IOV enable/disable plumbing and representor creation for MAE-capable EF100 PFs.

Important APIs and functions: `efx_ef100_sriov_configure()` is the PF `sriov_configure` callback. `efx_ef100_pci_sriov_disable()` disables VFs and tears down VF representors. Static `efx_ef100_pci_sriov_enable()` sets `efx->vf_count`, calls `pci_enable_sriov()`, and creates one VF representor per VF when `nic_data->grp_mae` is present.

Control flow: Enabling stores the requested VF count, enables PCI SR-IOV, returns immediately when MAE groups are absent, otherwise creates representors in order. If any representor creation fails, it destroys all created reps, disables SR-IOV, logs a probe error, clears `vf_count`, and returns the failure. Disabling refuses assigned VFs unless forced, finalizes representors, disables PCI SR-IOV when no VFs are assigned, and returns success.

State and persistence: Mutates `efx->vf_count` and the `efx->vf_reps` list through representor helpers. PCI SR-IOV state persists in the PCI core until disabled. Representor netdev state is runtime-only and must be reconciled on failure.

Dependencies and integration points: Depends on `ef100_nic.h` for EF100 private data, `ef100_rep.h` for representor lifecycle, PCI SR-IOV core APIs, and the generic `efx.c` `sriov_configure` dispatch. It complements EF100 RX/TX mport and representor paths.

Risks: Assigned VFs prevent normal disable. A partial enable must destroy all representors to avoid stale netdevs. The function does not clear `vf_count` on successful disable, relying on broader lifecycle assumptions. Representor behavior exists only when MAE grouping is available.

Test signals: Enable zero and nonzero VF counts, force and non-force disable with assigned VFs, inject representor creation failure, verify representor list cleanup, and validate PCI SR-IOV state after error unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.h

Purpose: Declares EF100 SR-IOV configuration and disable entry points for NIC type and PCI integration.

Important APIs: `efx_ef100_sriov_configure()` handles Linux PCI SR-IOV configure requests. `efx_ef100_pci_sriov_disable()` is exposed for forced teardown paths. The header includes `net_driver.h` for `struct efx_nic`.

Control flow and integration: Used by EF100 NIC-type registration and teardown code to bridge kernel PCI SR-IOV callbacks to EF100-specific representor and MAE behavior.

State and persistence: No direct state. It exposes functions that mutate PCI VF state and `efx->vf_count`.

Dependencies: Requires matching `ef100_sriov.c` implementation, PCI SR-IOV availability, and representor support when `CONFIG_SFC_SRIOV` is active.

Risks: No include guard is present in the file as read, so repeated inclusion relies on build usage not producing conflicts. Prototype visibility should stay aligned with EF100 NIC type callbacks.

Test signals: Build with EF100 SR-IOV support and call through the PCI `.sriov_configure` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.c

Purpose: Implements EF100 transmit queue allocation/init, descriptor construction, TX completions, skb enqueue, TSOv3, checksum and VLAN offload descriptors, doorbells, and representor egress override descriptors.

Important APIs and functions: `ef100_tx_probe()` allocates descriptor storage with an extra QMDA completion entry. `ef100_tx_init()` binds the core netdev TX queue and initializes hardware TXQ via MCDI. `ef100_tx_write()` pushes raw queued buffers. `ef100_ev_tx()` handles TX completion events. `ef100_enqueue_skb()` and `__ef100_enqueue_skb()` are the main transmit entry points. Static helpers validate TSO (`ef100_tx_can_tso()`), compose SEND/SEG/TSO/PREFIX descriptors, set partial checksum and VLAN insertion, and ring doorbells.

Control flow: Enqueue validates queue availability, computes GSO segment count, reserves a TSO metadata buffer when EF100 TSOv3 can handle the skb, or falls back to software TSO. Representor sends reserve an option buffer for an egress mport override and reject traffic that would stop the parent PF queue. Data is DMA mapped through common TX helpers, descriptors are written in ring order, `write_count` is published with barriers, BQL and fill-level thresholds decide queue stop/start, and a doorbell is pushed unless `xmit_more` can batch safely. Completion events map descriptor counts to a TX index and call common completion cleanup.

State and persistence: Mutates `insert_count`, `write_count`, `notify_count`, `packet_write_count`, `xmit_pending`, per-buffer flags, TX statistics (`tx_packets`, `tso_bursts`, `tso_packets`, fallback counters), BQL completions, and representor error counters. No durable persistence exists, but descriptor ring state and memory ordering are critical.

Dependencies and integration points: Uses common TX mapping/unwind/completion helpers, EF100 register fields from `ef100_regs.h`, MCDI TX initialization, netdev BQL APIs, checksum helpers, VLAN tag APIs, XDP/raw TX path conventions, and `ef100_rep.h` for VF representor traffic.

Risks: Descriptor count accounting is complex for TSO, raw writes, and representor prefix descriptors. The code modifies the TCP checksum field for TSO metadata, so skb ownership expectations matter. Queue stop thresholds must leave a descriptor unused. Memory barriers before doorbells and after `write_count` publication protect against hardware and completion races. Representor traffic intentionally drops rather than backpressuring, which can surprise callers.

Test signals: Cover normal skb TX, `xmit_more` batching, doorbell after >255 descriptors, TSOv3 accepted and fallback paths, GSO partial/encapsulated variants, VLAN and checksum offloads, queue stop/wake behavior, TX completion indexing, XDP/raw TX, representor mport override sends, and enqueue error unwind freeing skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.h

Purpose: Declares EF100 TX queue, completion, descriptor-limit, and skb enqueue entry points.

Important APIs: Exposes `ef100_tx_probe()`, `ef100_tx_init()`, `ef100_tx_write()`, `ef100_tx_max_skb_descs()`, `ef100_ev_tx()`, `ef100_enqueue_skb()`, and `__ef100_enqueue_skb()`. It includes `ef100_rep.h` because internal enqueue can target a representor.

Control flow and integration: The generic `efx_enqueue_skb()` wrapper in `efx.h` uses an indirect call to `ef100_enqueue_skb()` for EF100 NICs. Event dispatch uses `ef100_ev_tx()`, and queue probe/init paths use the queue setup declarations.

State and persistence: Header owns no state, but its APIs mutate TX rings, netdev queues, and representor statistics.

Dependencies: Requires `net_driver.h` types, EF100 representor declarations, and implementation in `ef100_tx.c`.

Risks: `__ef100_enqueue_skb()` is intentionally lower-level and accepts an optional representor; misuse from non-representor paths could bypass normal backpressure assumptions.

Test signals: Compile coverage of EF100 NIC-type TX callbacks, generic hard-start-xmit dispatch, and representor TX callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_regs.h

Purpose: Defines EF10 architecture MMIO register offsets, descriptor/event bitfields, enumerators, workaround addresses, PIO aperture layout, and RX prefix offsets.

Important APIs and definitions: Includes register offsets such as `ER_DZ_EVQ_RPTR`, `ER_DZ_EVQ_TMR`, `ER_DZ_RX_DESC_UPD`, `ER_DZ_TX_DESC_UPD`, and `ER_DZ_TX_PIOBUF`; event fields for driver, MCDI, RX, and TX events; RX/TX descriptor bitfields for kernel descriptors, TX checksum/timestamp options, PIO, and TSO; indirect EVQ update definitions for bug 35388; and `ES_DZ_RX_PREFIX_*` offsets and size.

Control flow and integration: This header is consumed by low-level IO, event, RX, and TX code to pack/unpack hardware-visible qwords and owords with shared `EFX_POPULATE_*` and `EFX_*FIELD` macros. It has no executable flow.

State and persistence: No runtime state. The constants encode the hardware ABI and therefore form persistent compatibility with EF10 firmware and silicon revisions.

Dependencies: No external implementation, but naming conventions depend on SFC bitfield helpers and EF10 architecture semantics. Workaround constants are used by hardware-specific IO paths.

Risks: Any incorrect bit position, width, step, or row count corrupts hardware interaction. Duplicate field macro names across descriptor variants are intentional but can confuse readers. RX/TX queue sizing and event parsing depend on these constants matching hardware revision expectations.

Test signals: Hardware bring-up, descriptor DMA tests, event queue processing, TX/RX traffic, TSO/checksum offload validation, interrupt moderation, PIO TX, and regression tests on EF10 revisions affected by the indirect EVQ update workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.c

Purpose: Implements EF10 PF/VF SR-IOV support, firmware vSwitch/vPort/vAdaptor management, VF MAC/VLAN/spoof-check/link-state configuration, VF config reporting, and restore/remove paths across resets and unload.

Important APIs and functions: Public entry points include `efx_ef10_sriov_configure()`, `efx_ef10_sriov_init()`, `efx_ef10_sriov_fini()`, VF setters/getters, `efx_ef10_vswitching_probe_*()`, `efx_ef10_vswitching_restore_*()`, and `efx_ef10_vswitching_remove_*()`. Static helpers allocate/free VSWITCHes, VPORTs, VADAPTORs, assign EVB ports, assign VF vports, and manipulate privilege masks through MCDI.

Control flow: PF probe creates a VEB vswitch and PF vport when VFs exist, attaches the PF MAC, then allocates a vAdaptor and records fixed VLAN-filter capabilities. SR-IOV enable allocates per-VF `ef10_vf` state, generates random MACs, creates vports, adds MAC filters, assigns EVB ports, and finally enables PCI SR-IOV. Disable refuses assigned VFs unless forced, disables PCI SR-IOV when possible, frees vport/vswitching state, and clears `vf_count`. MAC/VLAN changes detach active VF netdevs, remove filters and vAdaptors, unassign EVB ports, mutate vport resources, then restore in reverse order or schedule a VF reset on restoration failure.

State and persistence: Maintains `nic_data->vf` array, each VF's `efx`, `pci_dev`, `vport_id`, `vport_assigned`, `mac`, and `vlan`; PF `efx->vf_count`, `efx->vport_id`, `nic_data->vport_mac`, `fixed_features`, and `must_probe_vswitching`. Firmware vSwitch/vPort/vAdaptor state persists in NIC firmware until explicitly freed or reset.

Dependencies and integration points: Uses MCDI commands for EVB, VSWITCH, VPORT, VADAPTOR, privilege mask, and link state; PCI SR-IOV core; generic `efx_net_open/stop`, reset scheduling, filters, and device attach/detach helpers; and netlink VF config structs. It is called from NIC type callbacks and netdev SR-IOV ndo handlers via the generic SR-IOV wrapper.

Risks: Error unwinds must avoid leaking firmware resources or leaving VF drivers attached to invalid vports. Assigned VFs limit cleanup and can leave orphaned VFs until a later unload. VLAN changes have multi-stage restore logic with `rc` and `rc2` interactions. The code assumes QoS 0 only. Spoof-check depends on firmware capability. `efx_ef10_vswitching_remove_pf()` sets `efx->vport_id` to assigned before freeing the vswitch, so correctness relies on firmware semantics and assigned-VF checks.

Test signals: Enable/disable SR-IOV with no assigned VFs, assigned VFs, and forced unload; set VF MAC, VLAN, spoof-check, and link state; query VF config; inject MCDI failures at each vport/vadaptor step; reset PF and verify restore; bind a VF driver while changing VF state; verify fixed VLAN filter features after vAdaptor query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.h

Purpose: Defines EF10 VF bookkeeping and declares EF10 SR-IOV/vswitching/vport/vAdaptor control APIs.

Important APIs and types: `struct ef10_vf` stores a VF's active `efx_nic`, `pci_dev`, firmware `vport_id`, `vport_assigned` flag, MAC, and default VLAN. `EFX_EF10_NO_VLAN` encodes no VLAN. Prototypes cover SR-IOV configure/init/fini, VF MAC/VLAN/spoof-check/link-state/config, PF/VF vswitching probe/restore/remove, vport MAC add/delete, and vAdaptor alloc/query/free.

Control flow and integration: Used by EF10 NIC type callbacks and generic SR-IOV ndo wrappers to manage firmware switching resources and per-VF policy.

State and persistence: Header defines the shape of runtime VF state stored under EF10 NIC private data. Firmware resources referenced by IDs persist outside the C struct and must be freed explicitly.

Dependencies: Includes `net_driver.h`, PCI types, and netlink VF configuration types through shared headers. Implementations are split across this file's matching C code and EF10 NIC MCDI support.

Risks: `efx_ef10_sriov_wanted()` currently returns false inline, affecting RSS channel limiting unless overridden by type behavior elsewhere. Public vport/vAdaptor helpers expose firmware-resource operations that require strict call ordering.

Test signals: Compile SR-IOV builds, validate ABI between EF10 NIC private data and this struct, and exercise all declared callbacks via netdev SR-IOV operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.c

Purpose: Main SFC PCI/netdev driver entry for non-EF100 PCI IDs, plus shared module initialization that registers both legacy SFC and EF100 PCI drivers. It orchestrates NIC probe/remove, netdev operations, port lifecycle, XDP attachment, stats, PM, SR-IOV configure dispatch, and device association.

Important APIs and functions: Exports `efx_net_open()`, `efx_net_stop()`, and `efx_update_sw_stats()`. Defines `efx_netdev_ops`, queue stat ops, PCI probe/remove, PM callbacks, PCI device table, module init/exit, port/NIC probe/remove helpers, XDP setup/xmit helpers, netdev registration, and SR-IOV PCI configure bridge.

Control flow: PCI probe allocates `efx_probe_data` and `net_device`, initializes common struct and IO mappings, runs `efx_pci_probe_post_io()` with retries, registers devlink/netdev, probes optional MTDs, and pushes UDP tunnel ports. Main probe creates NIC resources, port, vswitching, filters, channels, NAPI, hardware init, port init, interrupts, and affinity. Open checks disabled/special/reboot states, reports link, starts all datapath components, and marks NET_UP. Stop calls `efx_stop_all()`. Remove dissociates, closes the netdev, disables interrupts, finalizes SR-IOV/devlink/netdev/MTD, removes all resources, unmaps IO, and frees memory.

State and persistence: Manages `efx->state`, channel counts, VPD serial, primary/secondary association lists, netdev feature flags, carrier, XDP program pointer, MTD names, PCI drvdata, and PM freeze/thaw state. Hardware, PCI, and netdev registrations persist until explicit unregister/remove.

Dependencies and integration points: Integrates with `efx_common.c` for reset/start/stop/io/common ops, `efx_channels.c` for interrupts and queues, RX/TX common code, NIC-type callbacks, MCDI port/common code, selftests, SR-IOV wrappers, devlink, PTP, filters, ethtool, and Linux PCI/netdev/PM frameworks.

Risks: Probe has many staged resources and must unwind in reverse order. Reset scheduling during probe aborts netdev registration. XDP MTU constraints and program lifetime require RTNL/RCU discipline. Association lists depend on VPD serial matching. PM thaw/resume must re-enable interrupts and hardware in the right order. SR-IOV configure is available only when the NIC type supplies it.

Test signals: PCI probe/remove, probe retry after reset, module load/unload, netdev open/close, PM suspend/resume/freeze/thaw, XDP attach/xmit, device rename, MTD creation failure tolerance, SR-IOV configure dispatch, queue stat reporting, and error unwinds at every probe stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.h

Purpose: Central shared header for SFC netdev datapath APIs, indirect EF100/common RX/TX dispatch, filter wrappers, RSS helpers, queue size limits, ethtool declaration, MTD stubs, SR-IOV VF sizing, device attach/detach helpers, and XDP TX.

Important APIs and definitions: Declares `efx_net_open()`, `efx_net_stop()`, TX queue/xmit helpers, RX packet helpers, `efx_enqueue_skb()` and `efx_rx_flush_packet()` indirect-call wrappers, TSO/RX/TX queue limits, filter insert/remove/get/count wrappers, `efx_rss_active()`, `efx_ethtool_ops`, IRQ moderation helpers, stats update, MTD helpers, `efx_device_detach_sync()`, `efx_device_attach_if_not_resetting()`, and `efx_xdp_tx_buffers()`.

Control flow: Inline wrappers route generic callers to EF100-specific or common implementations based on NIC type callbacks. Device detach stops representors before detaching the PF netdev and freezing TX queues; attach restores PF netdev presence and wakes reps when the device is NET_UP and not resetting.

State and persistence: Header does not own state but manipulates netdev present state, representor carrier/TX queues, filter tables through type callbacks, RSS context IDs, and queue sizing constants used at runtime.

Dependencies and integration points: Includes EF100 RX/TX headers, `efx_common.h`, filters, and `net_driver.h`. It is a high-fanout dependency for TX, RX, ethtool, core, and NIC-specific files.

Risks: Indirect call target lists must match actual function signatures. Queue limit macros combine generic limits with EF10 workarounds, so misuse can under-size or overrun rings. Attach/detach ordering matters for representors that transmit through PF queues.

Test signals: Build all NIC variants, verify hard-start-xmit dispatch for EF100 and common TX, RX flush dispatch, filter ioctl/ethtool flows, queue-size ethtool bounds, reset attach/detach behavior with representors, and XDP TX queue access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.c

Purpose: Manages SFC interrupt mode selection, channel topology, event queue lifecycle, TX/RX queue probing/removal, XDP TX queue assignment, channel resize, interrupt enable/disable, channel start/stop, and NAPI polling.

Important APIs and functions: Public functions include `efx_probe_interrupts()`, affinity setters, eventq probe/init/start/stop/fini/remove, channel init/probe/remove/realloc, `efx_set_channels()`, interrupt enable/disable pairs, `efx_start_channels()`, `efx_stop_channels()`, and NAPI init/fini. Static helpers compute RSS parallelism, allocate MSI-X channels, allocate/copy channels, assign XDP TX queues, process NAPI events, and adapt IRQ moderation.

Control flow: Probe chooses MSI-X, MSI, or legacy interrupt mode, sizes RX/TX/extra/XDP channels, requests vectors, records IRQs, assigns RSS spread, and sets real netdev queue counts. Channel probe allocates event queues then TX/RX queues. Start initializes TX/RX queues, pushes RX descriptors, and starts event queues. NAPI polling processes events, flushes pending RX packets, refills RX descriptors, updates BQL completion counters, delivers skb lists, adapts RX IRQ moderation, and acknowledges event queue reads. Resize clones channels, swaps queue sizes, probes replacements, and rolls back on failure.

State and persistence: Mutates global module parameters `efx_interrupt_mode` and `rss_cpus`; NIC fields for channel counts, offsets, XDP queue mode/counts, IRQ mode, RSS spread, and `irq_soft_enabled`; per-channel eventq state, IRQ moderation, NAPI state, and stats baselines; and queue arrays. All state is runtime and reconstructed on probe/reset.

Dependencies and integration points: Uses PCI MSI/MSI-X APIs, CPU topology, NAPI, RX/TX common queue code, NIC type eventq and IRQ callbacks, MCDI event/poll modes, RFS acceleration, workarounds, SR-IOV VF sizing, PTP channel update, and XDP flush.

Risks: Channel count math must satisfy vector, VI, XDP, RSS, SR-IOV, and separate-TX constraints. Resize rollback must preserve PTP channel and free only copied resources. Interrupt soft/hard enable ordering and memory barriers protect NAPI/event processing. Borrowed XDP queues can reduce performance and must select checksum-compatible queues. NAPI budget and RX flush behavior can affect packet latency and drops.

Test signals: MSI-X/MSI/legacy fallback, RSS CPU limiting, SR-IOV VF-size RSS limiting, separate TX channel mode, XDP dedicated/shared/borrowed queue modes, channel resize success and rollback, NAPI poll under budget/exhaustion, IRQ moderation adaptation, RFS expiry, and interrupt disable during reset/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.h

Purpose: Declares channel, interrupt, event queue, NAPI, and queue-stat helper APIs shared between core probe/reset code and datapath code.

Important APIs: Exposes interrupt probe/remove/enable/disable, affinity helpers, eventq lifecycle, channel allocation/probe/remove/reallocation/start/stop, NAPI lifecycle, `efx_get_queue_stat_rx_hw_drops()`, and `efx_channel_dummy_op_void()`. Declares module parameters `efx_interrupt_mode` and `rss_cpus`.

Control flow and integration: Core `efx.c` and `efx_common.c` call these functions during probe, open, stop, reset, PM, and removal. The inline RX hardware-drop helper sums channel drop/error counters for stats.

State and persistence: Header owns no state but exposes operations that mutate NIC channel topology, IRQ mode, NAPI state, and queue stats.

Dependencies: Requires `struct efx_nic` and `struct efx_channel` from shared driver headers and implementation in `efx_channels.c`.

Risks: Callers must respect lifecycle ordering: probe before init/start, stop before remove, disable interrupts before teardown. Drop counter composition must stay aligned with RX paths that increment those counters.

Test signals: Compile lifecycle users, verify stats include CRC, truncation, overlength, nodesc, and bad-mport drops, and exercise reset/open/close paths that call channel start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_common.c

Purpose: Implements shared SFC lifecycle utilities: reset workqueue, MAC reconfiguration, netdev feature changes, link status, MTU/XDP constraints, datapath start/stop, port start/stop, stats, reset down/up/work scheduling, common struct and IO setup, MCDI logging sysfs, PCI error recovery, encapsulated offload feature checks, physical port naming, and representor attach/detach.

Important APIs and functions: Public functions include `efx_create_reset_workqueue()`, `efx_mac_reconfigure()`, `efx_set_mac_address()`, `efx_set_rx_mode()`, `efx_set_features()`, `efx_link_status_changed()`, `efx_xdp_max_mtu()`, `efx_change_mtu()`, `efx_start_all()`, `efx_stop_all()`, `efx_net_stats()`, `__efx_reconfigure_port()`, `efx_reset_down()`, `efx_reset_up()`, `efx_reset()`, `efx_schedule_reset()`, `efx_init_struct()`, `efx_init_io()`, PCI error handlers, `efx_features_check()`, and representor attach/detach helpers.

Control flow: `efx_start_all()` checks state and reset flags, enables port/MAC, sizes RX buffers, starts channels/PTP/queues, starts monitor/selftest/stats, and polls link. `efx_stop_all()` updates stats, stops monitor/MAC work, disables TX queues, stops PTP/channels, and leaves link state controlled by callers. Reset scheduling sets a bit in `reset_pending`, switches MCDI to polled mode, and queues a single-threaded reset worker. Reset execution detaches netdev, tears down datapath/interrupts/hardware state, calls NIC-type reset/init, restores interrupts, vswitching, RSS/filter state, and restarts datapath or disables the NIC.

State and persistence: Manages global `reset_workqueue`; NIC state fields including `state`, `reset_pending`, `port_enabled`, `port_initialized`, `phy_mode`, RX buffer sizing/scatter, queue thresholds, workqueues, locks, RSS context ID, vport ID, stats locks, representor list, and IO BAR mappings. PCI BAR mapping and sysfs attributes persist until finalization.

Dependencies and integration points: Uses NIC type callbacks extensively, `efx_channels.c`, RX/TX common code, MCDI, port/PHY, filters, PTP, selftests, devlink-adjacent reflash mutex initialization, PCI EEH/error handlers, netdev feature APIs, GRE/UDP tunnel parsing, and EF100 representor helpers.

Risks: Reset lock ordering (`mac_lock`, `filter_sem`, RSS lock) must match down/up paths. EF100 reset is special-cased because its NIC-type reset handles locking differently. MTU changes with XDP must enforce page-size limits. Feature changes are asynchronous through MAC work. IO cleanup avoids disabling PCI while VFs are assigned. Encapsulation feature checks are conservative and can disable offloads unexpectedly for unsupported GRE/UDP tunnel shapes.

Test signals: Reset reasons and mapping, TX watchdog reset, MCDI timeout FLR path, probe/remove workqueue cleanup, MTU changes with/without XDP, RX buffer scatter sizing, feature toggles for RX VLAN/RXFCS/ntuple, PCI EEH recovery, encap offload filtering, sysfs MCDI logging, representor detach/attach during resets, and IO map/unmap failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_common.h

Purpose: Declares shared lifecycle, IO, reset, MAC, netdev, feature, stats, PCI error, and representor helper APIs for the SFC driver.

Important APIs and definitions: Defines queue-size constants `EFX_MAX_DMAQ_SIZE`, `EFX_DEFAULT_DMAQ_SIZE`, `EFX_MIN_DMAQ_SIZE`, `EFX_MAX_EVQ_SIZE`, and `EFX_MIN_EVQ_SIZE`; declares IO/struct init/fini, start/stop, reset workqueue, monitor, reset down/up/schedule, MAC and feature handlers, MTU/XDP max, PCI error handlers, features check, physical port helpers, and representor attach/detach. Inline helpers include `EFX_ASSERT_RESET_SERIALISED()`, `efx_check_disabled()`, `efx_schedule_channel()`, and `efx_schedule_channel_irq()`.

Control flow and integration: Used by core PCI/netdev code, channel code, ethtool, SR-IOV, and NIC-specific modules to share reset/start/stop and netdev operations. The channel scheduling helpers bridge interrupt handlers to NAPI.

State and persistence: Header owns no state. Constants determine default queue allocations and ring bounds. Inline helpers inspect or mutate NAPI scheduling and disabled/recovering device state.

Dependencies: Relies on shared driver types and Linux netdev/NAPI/PCI types. Optional MCDI logging declarations depend on `CONFIG_SFC_MCDI_LOGGING`.

Risks: Reset serialization macro assumes RTNL for active states; callers outside expected contexts can race resets. Queue constants must remain compatible with hardware descriptor limits. Disabled-state checks prevent operations after serious errors but can expose user-visible `-EIO`.

Test signals: Compile all users, reset paths under RTNL, interrupt scheduling from IRQ context, queue-size ethtool operations, MCDI logging builds enabled/disabled, and operations on disabled or recovering devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.c

Purpose: Implements devlink registration, info reporting, flash update dispatch, and EF100 MAE devlink port registration/MAC operations for PF and VF representor ports.

Important APIs and functions: Public lifecycle functions are `efx_probe_devlink_and_lock()`, `efx_probe_devlink_unlock()`, `efx_fini_devlink_lock()`, and `efx_fini_devlink_and_unlock()`. EF100 SR-IOV helpers include PF/representor set/unset devlink port functions. Devlink ops include `.info_get` and `.flash_update`. Static info helpers report stored NVRAM versions and running MC/FPGA/datapath/SoC/board versions across GET_VERSION output revisions.

Control flow: Probe skips VFs, allocates devlink private storage, locks and registers devlink, and stores `efx`. Info requests query board config, NVRAM partition metadata, and running versions, reporting errors via extack while returning devlink info fields. Flash update passes firmware to `efx_reflash_flash_firmware()`. Under SR-IOV, mport descriptors are converted to devlink PCI PF/VF port attrs; VF port MAC get/set looks up firmware client IDs and uses MCDI MAC commands.

State and persistence: Maintains `efx->devlink`, devlink private `efx`, `efx->dl_port`, and `efx_rep->dl_port`. Firmware/NVRAM versions and MACs are persistent device state queried or modified through MCDI.

Dependencies and integration points: Uses Linux devlink APIs, MCDI version/NVRAM/board/MAC commands, EF100 MAE mport lookup, EF100 representor structs, and reflash code. Called from PCI probe/remove and representor lifecycle.

Risks: Devlink lock/unlock ordering spans netdev registration; failures after devlink registration need balanced cleanup. Info reporting ORs errors and emits a generic extack while individual helpers log details. MAC set is restricted to VF mports. Port registration silently ignores alias/undefined mports. Version parsing depends on output length and flags matching firmware command versions.

Test signals: PF devlink registration/unregistration, VF probe skipping devlink, `devlink info` on firmware with V1 through V5 GET_VERSION layouts, missing NVRAM partitions, flash update dispatch, MAE PF/VF devlink ports, VF MAC get/set success/failure, and cleanup on representor removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.h

Purpose: Declares SFC devlink lifecycle functions, EF100 devlink port helpers, and custom devlink info version-name constants.

Important APIs and definitions: Defines names such as `fw.mgmt.suc`, `fw.mgmt.cmc`, `fpga.rev`, `fpga.app`, `coproc.boot`, `coproc.uboot`, `coproc.main`, `coproc.recovery`, `fw.exprom`, and `fw.uefi`, plus `EFX_MAX_VERSION_INFO_LEN`. Declares probe/unlock/fini functions and, under `CONFIG_SFC_SRIOV`, PF and representor devlink port set/unset helpers.

Control flow and integration: Included by PCI core and representor code to bracket devlink registration with devl locking and to associate devlink ports with MAE mports.

State and persistence: Header owns no state. Constants define the stable names users see through `devlink info`.

Dependencies: Includes `net_driver.h` and `<net/devlink.h>`, with optional forward declaration of `struct efx_rep`.

Risks: Renaming version keys changes user-facing devlink ABI. Lifecycle callers must pair lock/unlock and free paths exactly.

Test signals: Build with and without `CONFIG_SFC_SRIOV`, verify `devlink info` key names, and probe/remove PF devices under devlink enabled kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.c

Purpose: Implements devlink flash-update backend for SFC/AMD adapters, including firmware image format detection, CRC validation, NVRAM partition selection, erase/write chunking, update finish/abort, and user progress reporting.

Important APIs and functions: Public `efx_reflash_flash_firmware()` performs the update. Static parsers recognize Reflash headers, SmartNIC image headers, and SmartNIC bundle headers. Helper `efx_reflash_partition_type()` maps firmware type/subtype to NVRAM partition type/subtype. Erase/write helpers split NVRAM operations into aligned chunks and report devlink status.

Control flow: The flash path checks firmware capability `BUNDLE_UPDATE`, serializes on `efx->reflash_mutex`, reports "Checking update", either selects AUTO partition or scans the firmware byte-by-byte for the first valid supported image header, verifies NVRAM subtype compatibility, queries partition info, rejects protected/unwritable/bad-size images, starts an NVRAM update, erases as needed, writes aligned chunks with padding for the final partial chunk, finishes with polled update completion, or aborts on failure. It reports final success/failure through devlink.

State and persistence: Mutates persistent NVRAM contents on the adapter. Runtime state is limited to the reflash mutex, temporary buffers, MCDI update transaction state, and devlink progress notifications.

Dependencies and integration points: Uses `fw_formats.h` header offsets/magic values, Linux firmware blobs, CRC32 helpers, devlink flash APIs, MCDI NVRAM metadata/info/erase/write/update commands, NIC type capabilities such as `flash_auto_partition` and `mcdi_max_ver`, and extack for user errors. Called from `efx_devlink.c`.

Risks: Firmware scanning is intentionally permissive and stops at the first candidate, even if unsupported. CRC and overflow checks protect parsing but final compatibility is delegated to running firmware. Erase/write alignment must match partition metadata. Failed writes must call update-finish abort without masking original errors. Updating NVRAM is destructive and persistent, so subtype/protection checks are critical.

Test signals: Valid and invalid Reflash/SmartNIC/bundle images, prepended signed-container data, CRC mismatch, unsupported firmware type, subtype mismatch, auto partition devices, protected/unwritable partitions, image too large, erase/write MCDI failures, final update timeout, concurrent update attempts, and devlink status progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.h

Purpose: Declares the SFC devlink firmware reflash entry point.

Important APIs: `efx_reflash_flash_firmware(struct efx_nic *efx, const struct firmware *fw, struct netlink_ext_ack *extack)` updates adapter NVRAM from a firmware blob and reports user-visible errors.

Control flow and integration: Included by `efx_devlink.c`, which calls the function from the devlink `.flash_update` operation.

State and persistence: The header owns no state. Its function mutates persistent NVRAM on success.

Dependencies: Includes `net_driver.h` and `<linux/firmware.h>`; extack type is available through netlink/devlink includes in users.

Risks: This API is high impact because it can rewrite firmware partitions. Callers must pass a valid devlink-provided firmware object and extack context.

Test signals: Build devlink flash update path and run firmware update negative tests for parse, metadata, protection, size, erase, write, and finish failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/enum.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/enum.h

Purpose: Defines shared enumerations and masks for loopback modes and reset types used across SFC PHY, selftest, ethtool, reset, and port code.

Important APIs and definitions: `enum efx_loopback_mode` lists controller, PHY, external, and wireside loopbacks. Macros define internal/wireside/external masks and predicates such as `LOOPBACK_INTERNAL()`, `LOOPBACK_EXTERNAL()`, `LOOPBACK_CHANGED()`, and `LOOPBACK_OUT_OF()`. `enum reset_type` distinguishes reset methods/scopes from reset reasons, including MCDI timeout as a special method outside the normal scope hierarchy.

Control flow and integration: Loopback predicates drive port reconfiguration, PHY transmit disable decisions, and test selection. Reset type ordering is used by `efx_schedule_reset()` and `efx_reset()` to select and clear pending reset scopes.

State and persistence: No state. The numeric values are semantically important because reset methods are ordered by increasing scope and loopback modes index name tables and masks.

Dependencies: Standalone include guard; consumed by shared driver headers and implementation files.

Risks: Reordering enum values breaks masks, string tables, reset scope clearing, and user-visible diagnostics. The comment typo for `RESET_TYPE_INVISIBLE` does not affect behavior but can mislead documentation readers.

Test signals: Selftest loopback enumeration, ethtool loopback configuration, port reconfiguration for internal/external transitions, reset scheduling for each reason/method, and string-table bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool.c

Purpose: Provides the main `ethtool_ops` table and local SFC implementations for LED identification, register dumps, interrupt coalescing, ring sizing, Wake-on-LAN, FEC stats, timestamp info, and integration with common ethtool helpers.

Important APIs and functions: `efx_ethtool_ops` is exported through `efx.h`. Local helpers include `efx_ethtool_phys_id()`, `efx_ethtool_get_regs_len()`, `efx_ethtool_get_regs()`, coalesce get/set, ringparam get/set, WOL get/set, FEC stats, and timestamp info. Many operations delegate to `ethtool_common.h`, filters, RSS, module EEPROM, link settings, selftest, and stats helpers.

Control flow: Coalesce get reads current IRQ moderation; set interprets standard and legacy irq fields, allows RX to override TX only when TX was unchanged on shared channels, calls `efx_init_irq_moderation()`, then pushes moderation to every channel. Ringparam set validates RX/TX bounds, raises TX size to `EFX_TXQ_MIN_ENT()` if needed, and calls `efx_realloc_channels()` to rebuild queues. LED identify maps ethtool states to MCDI LED modes. Timestamp info defaults to TX software timestamping then augments via PTP helper.

State and persistence: Mutates IRQ moderation fields, channel hardware timer state, queue entry counts through channel reallocation, WOL configuration through NIC type callbacks, and LED state. Settings are runtime or firmware-backed depending on callback.

Dependencies and integration points: Uses `efx_channels.c` for moderation and channel reallocation, `efx_common.c` for feature/MTU interactions indirectly, NIC type callbacks for registers/WOL/FEC, MCDI LED control, PTP timestamp helpers, RSS/filter ethtool common code, and Linux ethtool ABI.

Risks: Shared RX/TX channels cannot support independent moderation unless RX override is allowed. Ring resize stops datapath and can fail or roll back. TX maximum depends on EF10 workaround-adjusted limits. Unsupported ethtool fields are intentionally ignored for compatibility, which may surprise tools expecting strict validation.

Test signals: `ethtool -c/-C`, shared vs separate TX channels, invalid coalesce/ring values, ring resize under traffic, register dump length/content, LED identify states, WOL get/set, timestamp info with PTP, FEC stats, RSS context operations, and selftest/stat string coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool.c -->
