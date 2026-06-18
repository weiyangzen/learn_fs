# subset-b-004409 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.c

## Purpose
`enic_res.c` is the Cisco ENIC resource orchestration layer. It reads firmware-provided vNIC configuration, issues ENIC-specific device commands for VLAN/RSS/NIC settings, counts and allocates hardware resources, initializes WQ/RQ/CQ/interrupt MMIO blocks, and negotiates extended receive completion queue entry size.

## Important APIs, types, and functions
- `enic_get_vnic_config()` fetches MAC address and selected `struct vnic_enet_config` fields with `vnic_dev_get_mac_addr()` and `vnic_dev_spec()`, clamps queue lengths/MTU/coalescing values, aligns WQ/RQ descriptors to 32-entry groups, and logs the effective feature set.
- `enic_add_vlan()` / `enic_del_vlan()` wrap `CMD_VLAN_ADD` and `CMD_VLAN_DEL`.
- `enic_set_nic_cfg()` builds the NIC config word via `vnic_set_nic_cfg()` and uses `CMD_NIC_CFG_CHK` when UDP RSS hash bits are requested.
- `enic_set_rss_key()` and `enic_set_rss_cpu()` pass DMA buffers to `CMD_RSS_KEY` and `CMD_RSS_CPU`.
- `enic_get_res_counts()` reads firmware BAR resource counts and detects an admin channel by checking admin WQ/RQ/CQ plus SR-IOV interrupt availability.
- `enic_alloc_vnic_resources()` allocates ENIC WQs, RQs, CQs, interrupt controls, and legacy PBA resources.
- `enic_init_vnic_resources()` programs queues and CQs with CQ and interrupt indices based on interrupt mode.
- `enic_ext_cq()` uses `CMD_CAPABILITY` and `CMD_CQ_ENTRY_SIZE_SET` under `devcmd_lock` to select 16/32/64 byte RQ CQ entries.

## Control flow and state
Configuration flow is firmware-first: the driver asks the vNIC firmware for MAC/config fields, applies kernel-side defaults and bounds, then later uses those values to size descriptor rings. Allocation flow is WQ, RQ, CQ, interrupt, then optional legacy PBA. Any allocation error jumps to cleanup through `enic_free_vnic_resources()`. Initialization flow maps RQs to early CQs and WQs to later CQs, then maps CQs to interrupt vector 0 for INTx/MSI or per-CQ MSI-X vectors. Error interrupt wiring is enabled for INTx and MSI-X but not MSI.

State is mostly in `struct enic`: effective config, resource counts, `ext_cq`, ring objects, interrupt objects, `legacy_pba`, and admin-channel availability. Persistent hardware state is written through vNIC MMIO registers by the lower-level `vnic_*_init()` helpers and firmware devcmds.

## Dependencies and integration points
This file depends on the ENIC top-level `struct enic` and on descriptor, vNIC resource, device-command, queue, CQ, interrupt, RSS, NIC config, and stats headers. It is used during probe/open/reset paths to establish the ENIC hardware datapath before TX/RX NAPI begins. Firmware capability behavior in `vnic_dev.c` determines whether newer features such as extended CQ entries are available.

## Risks and test signals
Key risks are resource-count mismatches, invalid `ext_cq` selection, incorrect CQ-to-queue mapping, unsupported firmware commands, and missing legacy PBA in INTx mode. Useful test signals include probe logs for effective WQ/RQ/CQ/intr counts, VLAN add/delete errors, RSS programming success, interrupt-mode-specific packet I/O, and fallback logging when `CMD_CQ_ENTRY_SIZE_SET` is unavailable or fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.h

## Purpose
`enic_res.h` defines ENIC resource limits, feature access macros, TX/RX descriptor-posting inline helpers, and prototypes for the resource routines implemented in `enic_res.c`.

## Important APIs, types, and functions
- `ENIC_MIN_WQ_DESCS`, `ENIC_MAX_WQ_DESCS_DEFAULT`, `ENIC_MAX_WQ_DESCS`, `ENIC_MIN_RQ_DESCS`, `ENIC_MAX_RQ_DESCS`, and `ENIC_MAX_CQ_DESCS_DEFAULT` bound ring sizing.
- `ENIC_MIN_MTU` and `ENIC_MAX_MTU` bound MTU configuration.
- `ENIC_SETTING(enic, f)` checks `VENETF_*` feature bits in `enic->config.flags`.
- `enic_queue_wq_desc_ex()` is the common encoder/poster for ENIC TX descriptors. It calls `wq_enet_desc_enc()` then `vnic_wq_post()`.
- Wrapper helpers select offload modes: plain checksum (`enic_queue_wq_desc()`), explicit checksum flags (`enic_queue_wq_desc_csum()`), L4 checksum offset (`enic_queue_wq_desc_csum_l4()`), TSO (`enic_queue_wq_desc_tso()`), and continuation descriptors (`enic_queue_wq_desc_cont()`).
- `enic_queue_rq_desc()` encodes an RX descriptor with `rq_enet_desc_enc()` and posts it to the RQ software ring.

## Control flow and state
The inline helpers are on the datapath. TX helpers write hardware descriptor fields first, then update software WQ bookkeeping through `vnic_wq_post()`. RX posting selects descriptor type from `os_buf_index`, encodes DMA address/length, and calls `vnic_rq_post()`, which advances the posted index at its own return rate.

The helpers mutate software queue buffer state and hardware-visible descriptor memory but do not directly ring doorbells except through lower-level queue helpers. The caller owns DMA mapping lifetime and later cleanup.

## Dependencies and integration points
The header binds ENIC code to `wq_enet_desc.h`, `rq_enet_desc.h`, `vnic_wq.h`, `vnic_rq.h`, and the `struct vnic_enet_config` flags from `vnic_enet.h`. It is consumed by ENIC TX/RX paths that need compact descriptor posting.

## Risks and test signals
Descriptor field packing mistakes produce silent packet corruption or stuck queues. The `len`, `mss`, checksum offset, VLAN tag, SOP/EOP, and loopback arguments must fit hardware field widths. Tests should exercise checksum offload, TSO, VLAN insertion, multi-fragment TX, and RX refill under ring wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.c

## Purpose
`enic_rq.c` implements the ENIC receive completion path and receive buffer refill. It decodes hardware CQ entries, validates RX metadata, constructs GRO frags-backed SKBs from page-pool pages, applies RSS/checksum/VLAN metadata, updates RX statistics, and advances RQ/CQ software cursors.

## Important APIs, types, and functions
- `enic_rq_alloc_buf()` fills one RQ descriptor from a page-pool page or reposts an existing buffer.
- `enic_free_rq_buf()` returns an outstanding page to the page pool.
- `enic_rq_cq_service()` polls a receive CQ up to a budget and dispatches completions.
- `enic_rq_cq_desc_dec()` decodes 16/32/64 byte CQ header variants and extracts type, color, queue number, and completed index.
- `cq_enet_rq_desc_dec()` decodes common 16-byte receive completion fields: SOP/EOP, RSS, byte count, VLAN, FCoE, checksums, protocol flags, FCS, and errors.
- `enic_rq_set_skb_flags()` maps hardware metadata to `skb_set_hash()`, `CHECKSUM_UNNECESSARY`, encapsulation checksum level, and VLAN tag insertion.
- `enic_rq_service()` walks skipped RQ buffers until the completed descriptor is reached.

## Control flow and state
Refill flow allocates a page from `erq->pool`, records offset and truesize in the current `vnic_rq_buf`, obtains the DMA address from the page pool, then queues the descriptor with `enic_queue_rq_desc()`. Completion flow starts with `vnic_cq_to_clean()`, decodes the CQ color bit, and loops while color differs from `cq->last_color`. Each CQ entry points at an RQ and completed descriptor index. The RQ service loop advances `vrq->to_clean` and returns descriptors, accounting skipped descriptors until the target index is reached.

For good single-buffer completions, `enic_rq_indicate_buf()` obtains an skb with `napi_get_frags()`, syncs DMA for CPU, appends the page as an RX frag, records the RX queue, applies checksum/RSS/VLAN flags, marks the skb for page recycling, and submits it through `napi_gro_frags()`. It then clears the buffer ownership so the page is not freed twice. Packet errors and truncation update stats and drop the buffer.

## Dependencies and integration points
This file depends on the ENIC private state, page pool, NAPI GRO, VLAN helpers, busy-poll include, `cq_enet_desc.h`, `enic_res.h`, and `vnic_rq`/`vnic_cq` cursor helpers. Adaptive RX coalescing reads packet byte categories into `vnic_cq.pkt_size_counter`.

## Risks and test signals
Critical risks include stale CQ reads without the `rmb()`, wrong extended CQ completed-index reconstruction, page reference/lifetime mistakes, checksum metadata misinterpretation for VXLAN/FCoE repurposed fields, and skipped descriptor accounting. Test with RX checksum on/off, RSS hash reporting, VLAN-stripped packets, jumbo MTU, VXLAN offload patch levels, descriptor wrap, page-pool allocation failures, and truncated/FCS-error packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.h

## Purpose
`enic_rq.h` is the small public header for ENIC receive-queue service routines.

## Important APIs, types, and functions
- `enic_rq_cq_service()` polls receive completions for a CQ and budget.
- `enic_rq_alloc_buf()` refills one receive descriptor.
- `enic_free_rq_buf()` releases an RQ buffer page.

## Control flow and state
The header only declares entry points. State is carried by `struct enic`, `struct vnic_rq`, and `struct vnic_rq_buf` supplied by callers and defined elsewhere.

## Dependencies and integration points
Consumers are ENIC open/NAPI/refill paths that need RX service and cleanup callbacks. It relies on declarations of `struct enic`, `struct vnic_rq`, and `struct vnic_rq_buf` being visible through surrounding includes.

## Risks and test signals
Risk is minimal in the header itself; ABI drift between declarations and implementation would break builds. Compile coverage and RX NAPI functional tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.c

## Purpose
`enic_wq.c` implements ENIC transmit completion servicing. It decodes WQ completion CQ entries, frees DMA-mapped SKBs, updates TX completion stats, returns WQ descriptors, and wakes stopped TX subqueues when space is available.

## Important APIs, types, and functions
- `enic_wq_cq_service()` polls a TX completion CQ up to a budget.
- `enic_wq_cq_desc_dec()` decodes generic CQ descriptors and handles extended WQ completion index width for large WQ rings.
- `enic_wq_service()` serializes a WQ with `enic->wq[q_number].lock`, calls `vnic_wq_service()`, and wakes the corresponding netdev TX queue when descriptor availability is sufficient.
- `enic_free_wq_buf()` unmaps single or page DMA depending on SOP and frees `skb` only from the buffer that owns it.
- `enic_wq_free_buf()` is the completion callback that updates `cq_work`/`cq_bytes` and delegates buffer release.

## Control flow and state
The CQ poller reads `cq->to_clean`, decodes color/type/queue/completed index, and loops while the hardware color differs from `cq->last_color`. For each completion, it invokes WQ service, then advances the CQ cursor with wrap/color toggling. The WQ service callback walks from `to_clean` through the completed index, freeing each descriptor buffer and returning descriptor availability.

State changes include WQ software cursor and descriptor availability updates, SKB/DMA ownership release, TX stats increments, and netdev queue wakeups.

## Dependencies and integration points
The file depends on ENIC WQ state, `vnic_wq`, `vnic_cq`, netdev TX queue APIs, and CQ descriptor format. It is called from ENIC NAPI/interrupt completion paths for transmit queues.

## Risks and test signals
Important risks include incorrect extended completion-index masking for rings larger than the default, double-unmap/free if SOP/EOP ownership is wrong, missed queue wakeups causing TX stalls, and lock ordering around TX enqueue/completion. Tests should include multi-fragment TX, ring wrap, queue stop/wake behavior, large WQ ring configurations, and TX timeout absence under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.h

## Purpose
`enic_wq.h` declares the ENIC transmit completion helper APIs.

## Important APIs, types, and functions
- `enic_free_wq_buf()` releases a single WQ buffer's DMA mapping and SKB ownership.
- `enic_wq_cq_service()` services TX completions for a CQ and budget.

## Control flow and state
The header carries no logic. Callers pass ENIC and WQ objects whose runtime state is mutated by the implementation.

## Dependencies and integration points
This header is used by ENIC TX setup/cleanup and completion code. It assumes `struct enic`, `struct vnic_wq`, and `struct vnic_wq_buf` are available from included ENIC headers.

## Risks and test signals
The header's main risks are declaration drift and missing includes. Build coverage and TX completion path tests cover it indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/rq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/rq_enet_desc.h

## Purpose
`rq_enet_desc.h` defines the 16-byte ENIC Ethernet receive descriptor format and inline encoder/decoder helpers.

## Important APIs, types, and functions
- `struct rq_enet_desc` contains a little-endian DMA address and packed length/type field.
- `enum rq_enet_type_types` defines `ONLY_SOP` and `NOT_SOP` descriptor type values.
- `rq_enet_desc_enc()` writes DMA address, 14-bit length, and 2-bit type in little-endian hardware format.
- `rq_enet_desc_dec()` reverses the packed fields for diagnostics or tests.

## Control flow and state
There is no standalone control flow. The helpers are called during RQ descriptor posting, after DMA buffer preparation and before the RQ posted-index update.

## Dependencies and integration points
The header is used by `enic_res.h` and receive-queue code. It depends on Linux endian types and the ENIC hardware descriptor ABI.

## Risks and test signals
Lengths beyond 14 bits are masked, so callers must provide hardware-valid buffer sizes. Test signals include RX buffer posting correctness, endian-safe descriptor inspection, and hardware acceptance of posted RQ descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/rq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.c

## Purpose
`vnic_cq.c` provides low-level allocation, initialization, cleanup, and free routines for Cisco vNIC completion queues.

## Important APIs, types, and functions
- `vnic_cq_alloc_with_type()` binds a `struct vnic_cq` to an MMIO resource and allocates a coherent descriptor ring.
- `vnic_cq_alloc()` is the normal `RES_TYPE_CQ` wrapper.
- `vnic_cq_init()` writes ring base, size, head/tail/color, interrupt enable, interrupt offset, and optional message address into CQ control registers.
- `vnic_cq_clean()` resets software cursor/color and hardware CQ pointers, then clears descriptor memory.
- `vnic_cq_free()` frees the coherent descriptor ring and drops the MMIO control pointer.

## Control flow and state
Allocation first hooks the resource using `vnic_dev_get_res()` and then allocates the descriptor ring. Initialization writes hardware-visible state in one sequence. Cleanup resets both software state (`to_clean`, `last_color`) and hardware head/tail/tail-color state to the initial empty ring convention.

## Dependencies and integration points
It depends on `vnic_dev` ring allocation and resource discovery. ENIC resource setup uses it after RQ/WQ allocation, and RX/TX completion paths rely on the cursors initialized here.

## Risks and test signals
Risks include missing resource mapping, wrong descriptor size for RQ extended CQ mode, stale color state after reset, and interrupt offset mismatch. Test signals are successful probe allocation, correct interrupt delivery per CQ, ring wrap behavior, and no stale completions after queue reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.h

## Purpose
`vnic_cq.h` defines the completion queue MMIO control layout, software CQ object, cursor helpers, and exported CQ management prototypes.

## Important APIs, types, and functions
- `struct vnic_cq_ctrl` mirrors hardware CQ control registers.
- `struct vnic_rx_bytes_counter` supports adaptive RX coalescing by separating small and large packet byte counts.
- `struct vnic_cq` stores index, vdev, control pointer, descriptor ring, software clean cursor, color bit, interrupt offset, and adaptive coalescing fields.
- `vnic_cq_to_clean()` returns the current descriptor pointer.
- `vnic_cq_inc_to_clean()` advances the cursor and toggles `last_color` on wrap.

## Control flow and state
The important state machine is color-based CQ traversal: consumers compare descriptor color with `last_color`, process entries until they match, and use `vnic_cq_inc_to_clean()` to wrap and toggle expected color.

## Dependencies and integration points
The header depends on `cq_desc.h` and `vnic_dev.h`. It is shared by ENIC resource allocation, RX/TX CQ service, and interrupt/coalescing code.

## Risks and test signals
An incorrect color convention or descriptor-size calculation leads to missed or duplicate completions. Test with high packet rates, ring wrap, CQ clean/reset, and interrupt offset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.c

## Purpose
`vnic_dev.c` is the core Cisco vNIC device abstraction. It discovers BAR resources, allocates descriptor rings, implements firmware device-command transports, caches firmware/stats/notify buffers, manages link/config commands, and exposes helper APIs used by ENIC and related Cisco vNIC drivers.

## Important APIs, types, and functions
- Resource discovery: `vnic_dev_discover_res()`, `vnic_dev_get_res_count()`, `vnic_dev_get_res()`.
- Ring memory: `vnic_dev_alloc_desc_ring()`, `vnic_dev_free_desc_ring()`, `vnic_dev_clear_desc_ring()`.
- Command transports: `_vnic_dev_cmd()` for legacy MMIO devcmd, `_vnic_dev_cmd2()` for WQ/result-ring devcmd2, `vnic_devcmd_init()` for devcmd2-first fallback to devcmd1.
- Command routing: `vnic_dev_cmd()`, `vnic_dev_cmd_proxy_by_index_start()`, `vnic_dev_cmd_proxy_end()`, and proxy/no-proxy helpers.
- Firmware/config/state commands: `vnic_dev_fw_info()`, `vnic_dev_spec()`, `vnic_dev_stats_dump()`, open/close/init/deinit/enable/disable/reset/status helpers, MAC/filter/VLAN-related helpers, `vnic_dev_classifier()`, overlay offload controls, and RSS capability query.
- Notify buffer support: `vnic_dev_notify_set()`, `vnic_dev_notify_unset()`, `vnic_dev_notify_ready()`, `vnic_dev_link_status()`, `vnic_dev_port_speed()`, `vnic_dev_msg_lvl()`, `vnic_dev_mtu()`.
- Lifecycle: `vnic_dev_register()`, `vnic_dev_unregister()`, `vnic_dev_get_pdev()`.

## Control flow and state
Registration stores `priv`/`pdev` and walks the BAR resource table, accepting normal and management-vNIC headers. Queue resources use a fixed stride, while singleton resources point at one MMIO region. Descriptor ring allocation aligns descriptor count, descriptor size, and base address before allocating coherent memory and setting `desc_avail` to `count - 1`.

Firmware command flow writes arguments before the command register for write commands and reads results after `STAT_BUSY` clears for read commands. It detects surprise removal by status/fetch index `0xFFFFFFFF`. Devcmd2 allocates a WQ for commands and a result ring, posts command descriptors with a write barrier, tracks posted index, result index, and color, and falls back to devcmd1 on setup failure. Proxy mode wraps commands for SR-IOV/subordinate vNIC targets.

Persistent driver state includes cached coherent firmware info, stats, and notify buffers; interrupt coalescing conversion factors; resource table; proxy mode/index; command args; and optional devcmd2 controller. Hardware state is persistent until reset/deinit through devcmds and MMIO queue setup.

## Dependencies and integration points
The file integrates PCI DMA APIs, BAR MMIO, ENIC WQ allocation for devcmd2, vNIC resource and devcmd ABIs, netdev logging, and firmware-provided capability negotiation. Higher-level ENIC code relies on these routines for every device configuration, queue resource, and firmware operation.

## Risks and test signals
High-risk areas include resource-table bounds checking, command timeout/error handling, devcmd2 ring full/color handling, coherent buffer lifetime, proxy error sign conventions, and fallback compatibility with old firmware. Test signals include probe on old/new firmware, devcmd2 fallback logs, MAC/filter/RSS/offload command success, surprise-removal paths returning `-ENODEV`, stats/notify checksums, reset/open/enable status commands, and no DMA leaks on unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.h

## Purpose
`vnic_dev.h` defines the software representation of a Cisco vNIC device, descriptor ring metadata, BAR/resource containers, interrupt mode enum, proxy type enum, and public vNIC device APIs.

## Important APIs, types, and functions
- `struct vnic_dev_bar` describes an MMIO BAR mapping.
- `struct vnic_dev_ring` tracks coherent descriptor memory, aligned base address, descriptor sizing, and software availability.
- `struct vnic_res` stores discovered MMIO resource base/count.
- `struct vnic_intr_coal_timer_info` stores firmware conversion factors.
- `struct vnic_dev` stores private driver pointer, PCI device, resources, interrupt mode, devcmd transport, notify/stats/fw coherent buffers, proxy state, command args, coalescing info, and devcmd2 controller.
- Fallback `readq()` / `writeq()` helpers provide 64-bit MMIO access where unavailable.

## Control flow and state
The header declares the vNIC API surface and describes the long-lived state allocated by `vnic_dev_register()` and freed by `vnic_dev_unregister()`. Ring state is mutated by queue allocation and service helpers; command state is mutated by `vnic_dev_cmd()` and transport-specific implementations.

## Dependencies and integration points
It includes `vnic_resource.h` and `vnic_devcmd.h`, and is included by nearly every ENIC vNIC subsystem. It bridges PCI BAR discovery, firmware commands, queue management, and netdev-facing ENIC code.

## Risks and test signals
ABI risks include 64-bit MMIO ordering on 32-bit systems, descriptor alignment assumptions, and stale declarations for command helpers. Build coverage across architectures and runtime tests on INTx/MSI/MSI-X modes cover the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_devcmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_devcmd.h

## Purpose
`vnic_devcmd.h` defines the Cisco vNIC firmware command ABI: command encoding macros, command IDs, status/error values, firmware info and notify structures, filter TLVs, devcmd/devcmd2 register/ring formats, overlay feature constants, and feature-version enums.

## Important APIs, types, and functions
- `_CMDC*` macros pack command number, vNIC type, flags, and host-visible direction into `enum vnic_devcmd_cmd` values.
- Command IDs cover firmware info, device-specific config, stats, packet filters, MAC/VLAN, RSS, reset/open/init/enable/deinit, capability, proxy, provisioning, devcmd2 initialization, filters, queue-pair commands, feature versions, overlay offloads, and CQ entry size selection.
- `enum vnic_devcmd_status` and `enum vnic_devcmd_error` define firmware completion state and firmware errno values.
- `struct vnic_devcmd_fw_info` and `struct vnic_devcmd_notify` define coherent command data shared with firmware.
- Filter structures (`struct filter`, `filter_tlv`, `filter_action`) define classifier command payloads.
- `struct vnic_devcmd` is the legacy MMIO command block; `struct vnic_devcmd2` and `struct devcmd2_result` are the ring-based transport descriptors.

## Control flow and state
The header has no executable logic but encodes command semantics that control `vnic_dev.c`. Direction bits drive whether host writes args, reads results, or both. `NOWAIT` flags allow asynchronous/no-result operation. Devcmd2 result color and completed index are part of the transport state machine.

## Dependencies and integration points
Firmware, `vnic_dev.c`, and ENIC resource/configuration code must agree on these packed values and structures. This file also feeds `vnic_nic.h` capability use through `CMD_NIC_CFG` and ENIC extended CQ negotiation through `CMD_CQ_ENTRY_SIZE_SET`.

## Risks and test signals
This is a hardware/firmware ABI header, so any command-number, direction, struct layout, endian, or packed-size change can break device initialization. Test signals include command capability negotiation, devcmd1/devcmd2 interoperability, classifier add/delete, overlay offload setup, RSS and CQ entry-size capability handling, and compatibility with older firmware command variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_devcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_enet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_enet.h

## Purpose
`vnic_enet.h` defines the firmware-provided ENIC Ethernet configuration region and feature/interrupt constants.

## Important APIs, types, and functions
- `struct vnic_enet_config` contains flags, WQ/RQ descriptor counts, MTU, interrupt timer/mode/type fields, device name, loop tag, VF RQ count, aRFS count, maximum RQ/WQ/CQ ring sizes, and reserved RDMA LKey.
- `VENETF_*` feature bits advertise TSO, LRO, RX/TX checksum, RSS hash types, loopback, and VXLAN.
- `VENET_INTR_TYPE_*` and `VENET_INTR_MODE_*` encode firmware interrupt preferences.

## Control flow and state
The structure is read field-by-field through `CMD_DEV_SPEC` in `enic_get_vnic_config()`. Its values seed persistent ENIC configuration state and constrain resource allocation and netdev feature setup.

## Dependencies and integration points
It integrates firmware configuration with `enic_res.c`, `enic.h`, and netdev feature decisions. The `ENIC_SETTING()` macro in `enic_res.h` consumes the flags defined here.

## Risks and test signals
Layout drift is the core risk because offsets are used for firmware reads. Test with devices reporting default/zero ring maxima, unusual MTUs, RSS/VXLAN flags, and different interrupt-mode requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.c

## Purpose
`vnic_intr.c` implements low-level allocation, initialization, coalescing timer programming, cleanup, and free routines for Cisco vNIC interrupt control resources.

## Important APIs, types, and functions
- `vnic_intr_alloc_with_type()` binds a `struct vnic_intr` to an interrupt-control MMIO resource.
- `vnic_intr_alloc()` uses the normal `RES_TYPE_INTR_CTRL` resource.
- `vnic_intr_init()` programs coalescing timer, coalescing type, mask-on-assertion, and clears credits.
- `vnic_intr_coalescing_timer_set()` converts microseconds to hardware cycles via `vnic_dev_intr_coal_timer_usec_to_hw()` before writing the control register.
- `vnic_intr_clean()` clears interrupt credits.
- `vnic_intr_free()` drops the MMIO control pointer.

## Control flow and state
Allocation only hooks MMIO resources; no coherent ring is allocated. Initialization writes hardware interrupt policy. Runtime credit return/masking logic is mostly inline in `vnic_intr.h`.

## Dependencies and integration points
It depends on resource discovery and interrupt coalescing conversion from `vnic_dev.c`. ENIC resource initialization configures one `vnic_intr` per firmware interrupt resource.

## Risks and test signals
Risks include wrong coalescing conversion factors, resource absence, and stale credits after reset. Test with coalescing timer changes, INTx/MSI/MSI-X interrupt delivery, mask/unmask behavior, and interrupt credit accounting under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.h

## Purpose
`vnic_intr.h` defines the vNIC interrupt-control MMIO layout, software interrupt object, inline mask/credit helpers, and interrupt management prototypes.

## Important APIs, types, and functions
- `struct vnic_intr_ctrl` mirrors coalescing, mask, credit, and credit-return registers.
- `struct vnic_intr` stores index, vNIC device pointer, and MMIO control pointer.
- Inline helpers: `vnic_intr_unmask()`, `vnic_intr_mask()`, `vnic_intr_masked()`, `vnic_intr_return_credits()`, `vnic_intr_credits()`, `vnic_intr_return_all_credits()`, and `vnic_intr_legacy_pba()`.
- Constants define absolute and quiet coalescing timer modes.

## Control flow and state
The credit-return helper packs credit count, unmask, and reset-timer bits into one register write. Mask helpers write direct MMIO bits. The legacy PBA helper reads pending state without clearing.

## Dependencies and integration points
This header is used by ENIC interrupt handlers and resource initialization. It depends on `vnic_dev.h` for conversion and vdev references.

## Risks and test signals
Wrong bit packing can lose interrupts or leave vectors masked. Test interrupt moderation, credit return after NAPI, MSI-X vector masking, and INTx legacy pending-bit reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_nic.h

## Purpose
`vnic_nic.h` defines the packed NIC configuration word used by Cisco vNIC firmware for RSS, TSO IP ID splitting, and ingress VLAN stripping.

## Important APIs, types, and functions
- Field masks/shifts cover RSS default CPU, RSS hash type, RSS hash bits, RSS base CPU, RSS enable, TSO IPID split enable, and ingress VLAN strip enable.
- `NIC_CFG_RSS_HASH_TYPE_*` values enumerate UDP/IP/TCP IPv4/IPv6 hash type bits.
- `vnic_set_nic_cfg()` packs caller-supplied values into a `u32` command argument.

## Control flow and state
The inline function is used before issuing `CMD_NIC_CFG` or `CMD_NIC_CFG_CHK`. It does not retain state; the resulting word becomes firmware state after a successful devcmd.

## Dependencies and integration points
`enic_set_nic_cfg()` in `enic_res.c` uses this helper. Firmware capability reporting for `CMD_NIC_CFG` determines which hash-type bits are legal.

## Risks and test signals
Mask/shift errors change RSS behavior or VLAN stripping. Test RSS indirection behavior, UDP RSS capability fallback, checksum/offload interactions, and firmware rejection through `CMD_NIC_CFG_CHK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_resource.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_resource.h

## Purpose
`vnic_resource.h` defines the Cisco vNIC BAR resource table ABI, including magic/version values, resource type IDs, and resource table/header structures.

## Important APIs, types, and functions
- `VNIC_RES_MAGIC`, `VNIC_RES_VERSION`, `MGMTVNIC_MAGIC`, and `MGMTVNIC_VERSION` identify normal and management vNIC BAR maps.
- `enum vnic_res_type` enumerates WQ/RQ/CQ, interrupt, devcmd, devcmd2, SR-IOV, and admin channel resource types.
- `struct vnic_resource_header`, `struct mgmt_barmap_hdr`, and `struct vnic_resource` define BAR0 resource discovery records.

## Control flow and state
`vnic_dev_discover_res()` consumes these definitions to populate `vdev->res[]`. Queue-like resources use `count` and fixed stride; singleton resources expose the mapped address directly.

## Dependencies and integration points
This header is shared by `vnic_dev.c`, queue allocators, ENIC resource counting, and admin-channel detection.

## Risks and test signals
Resource ID or structure layout errors break device probe. Test signals include successful resource discovery logs, resource count sanity for all queue types, devcmd2 resource detection, and management-vNIC BAR compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.c

## Purpose
`vnic_rq.c` manages low-level Cisco vNIC receive queues: software buffer ring allocation, resource binding, MMIO initialization, enable/disable, error status, and cleaning.

## Important APIs, types, and functions
- `vnic_rq_alloc_bufs()` allocates block-based `struct vnic_rq_buf` arrays and links them into a circular ring.
- `vnic_rq_alloc_with_type()` hooks the RQ control resource, disables the queue, allocates the coherent descriptor ring, and allocates software buffers.
- `vnic_rq_alloc()` selects `RES_TYPE_RQ`.
- `vnic_rq_init()` writes ring base/size, CQ index, error interrupt settings, fetch/post indices, and resets dropped/error status.
- `vnic_rq_enable()` / `vnic_rq_disable()` control hardware running state.
- `vnic_rq_clean()` invokes a caller cleanup callback for every buffer, resets descriptor availability, repositions cursors from hardware `fetch_index`, syncs posted index, writes enable 0 to resync internal VIC state, and clears descriptor memory.

## Control flow and state
The software buffer ring is circular and tracks `to_use` and `to_clean`. Disable writes enable 0 twice and waits for `running` to clear each time because of a hardware mini-cache race. Clean handles surprise removal by treating `fetch_index == 0xFFFFFFFF` as zero.

## Dependencies and integration points
This file depends on `vnic_dev` resource/ring helpers and is used by ENIC receive setup and teardown. Higher-level `enic_rq.c` owns actual page allocation and packet indication callbacks.

## Risks and test signals
Risks include partial buffer allocation cleanup, RQ disable timeout, fetch-index wrap or surprise removal, descriptor availability reset to `count - 1`, and hardware stale mini-cache behavior. Test probe/remove, RQ reset, repeated up/down, RX ring wrap, and fault injection for allocation failure and disable timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.h

## Purpose
`vnic_rq.h` defines the vNIC receive queue MMIO layout, software RQ/ring buffer structures, cursor/posting inline helpers, and RQ management prototypes.

## Important APIs, types, and functions
- `struct vnic_rq_ctrl` mirrors hardware RQ control registers.
- `struct vnic_rq_buf` stores per-descriptor OS buffer pointer, DMA address, length, index, descriptor pointer, write ID, page offset, and truesize.
- `struct vnic_rq` stores index, vdev, control pointer, descriptor ring, block-allocated buffer arrays, `to_use`, `to_clean`, and packet accounting.
- `vnic_rq_desc_avail()`, `vnic_rq_desc_used()`, `vnic_rq_next_desc()`, and `vnic_rq_next_index()` expose queue state.
- `vnic_rq_post()` records buffer metadata, advances `to_use`, decrements `desc_avail`, and periodically writes `posted_index` after a write memory barrier.
- `vnic_rq_service()` walks cleaned buffers until a completed index is reached.
- `vnic_rq_fill()` calls a refill callback while descriptors are available.

## Control flow and state
RQ software ownership is tracked by descriptor availability and the `to_use`/`to_clean` circular buffer pointers. Hardware ownership is communicated by writing `posted_index` every `VNIC_RQ_RETURN_RATE` descriptors after descriptors have been initialized.

## Dependencies and integration points
ENIC RX refill and completion code uses these helpers. The header depends on `vnic_dev.h`, `vnic_cq.h`, PCI, and netdevice declarations.

## Risks and test signals
Incorrect availability math or missing write barrier can let hardware fetch stale descriptors. Test with RX refill pressure, ring wrap, skipped completions, and queue reset while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rss.h

## Purpose
`vnic_rss.h` defines the memory layouts for Cisco ENIC RSS key and RSS CPU indirection data passed to firmware.

## Important APIs, types, and functions
- `ENIC_RSS_BYTES_PER_KEY`, `ENIC_RSS_KEYS`, and `ENIC_RSS_LEN` define a 40-byte key split across four padded key entries.
- `union vnic_rss_key` provides structured byte access and raw 64-bit access.
- `union vnic_rss_cpu` provides 32 padded CPU entries and raw 64-bit access.

## Control flow and state
The unions are filled by ENIC RSS setup code and passed as coherent DMA buffers to `CMD_RSS_KEY` and `CMD_RSS_CPU`. Firmware persists the resulting RSS state.

## Dependencies and integration points
`enic_set_rss_key()` and `enic_set_rss_cpu()` use these layouts through `vnic_dev_cmd()`. The NIC config command controls whether RSS is enabled and which hash types are used.

## Risks and test signals
Layout/padding mistakes would corrupt firmware RSS programming. Test RSS hash distribution, indirection table changes, and capability-limited hash type programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_stats.h

## Purpose
`vnic_stats.h` defines the firmware statistics block returned by Cisco vNIC stats dump commands.

## Important APIs, types, and functions
- `struct vnic_tx_stats` contains TX frame/byte counters, drops, errors, and TSO count.
- `struct vnic_rx_stats` contains RX frame/byte counters, drops/no-buffer/errors/RSS/CRC, and size-bucket counters.
- `struct vnic_gen_stats` defines a generic DMA map error counter but is not included in `struct vnic_stats` here.
- `struct vnic_stats` combines TX and RX stats.

## Control flow and state
`vnic_dev_stats_dump()` allocates a coherent `struct vnic_stats` and passes its DMA address to firmware. Firmware writes this structure; the driver reads counters later.

## Dependencies and integration points
ENIC ethtool/statistics paths depend on this ABI. It is tied to `CMD_STATS_DUMP` and firmware counter layout.

## Risks and test signals
Struct layout drift or wrong size in devcmd corrupts stats reporting. Test with ethtool stats under traffic, counter rollover expectations, and firmware stats dump failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.c

## Purpose
`vnic_vic.c` builds Cisco VIC provisioning information blobs containing network-order TLVs for firmware provisioning commands.

## Important APIs, types, and functions
- `vic_provinfo_alloc()` allocates a zeroed maximum-size provisioning buffer, copies OUI/type, and initializes length to include `num_tlvs`.
- `vic_provinfo_add_tlv()` appends a TLV with network-order type/length, copies its value, increments TLV count, and updates total length.
- `vic_provinfo_size()` returns the actual serialized provisioning buffer size.
- `vic_provinfo_free()` frees the buffer.

## Control flow and state
Provisioning state grows monotonically as TLVs are appended. Length and TLV count are stored in network byte order in the buffer, so callers and firmware share a serialized representation. Bounds checks prevent writes past `VIC_PROVINFO_MAX_TLV_DATA`.

## Dependencies and integration points
It depends on `vnic_vic.h`, slab allocation, endian helpers, and `unsafe_memcpy()` for flexible-array TLV payloads. The resulting buffer can be supplied to vNIC provisioning devcmds such as `CMD_INIT_PROV_INFO2`.

## Risks and test signals
Risks include length accounting errors, misuse of flexible array storage, NULL value handling, and endian mistakes. Test with multiple TLVs, maximum-size rejection, NULL inputs, and firmware acceptance of serialized provisioning data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.h

## Purpose
`vnic_vic.h` defines Cisco VIC generic provisioning TLV constants, serialized provisioning structures, maximum sizes, and helper prototypes.

## Important APIs, types, and functions
- `VIC_PROVINFO_CISCO_OUI` and `VIC_PROVINFO_GENERIC_TYPE` identify Cisco generic provisioning data.
- `enum vic_generic_prov_tlv_type` enumerates port profile, client, cluster, host, incarnation, OS, and client-type TLVs.
- `enum vic_generic_prov_os_type` defines OS IDs.
- `struct vic_provinfo` and nested `vic_provinfo_tlv` define the packed network-order wire format.
- `VIC_PROVINFO_ADD_TLV` is a convenience macro that jumps to `add_tlv_failure` on append error.

## Control flow and state
The packed provisioning object is mutable until sent to firmware. Its length and TLV count are network-order fields; callers must use helper functions to maintain them.

## Dependencies and integration points
It is consumed by `vnic_vic.c` and any ENIC provisioning path that sends VIC metadata to firmware.

## Risks and test signals
Risks include macro-imposed label naming, packed layout compatibility, and maximum size constraints. Compile coverage plus provisioning command tests with representative TLV sets are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.c

## Purpose
`vnic_wq.c` manages low-level Cisco vNIC work queues: software buffer ring allocation, resource binding, devcmd2 WQ allocation, MMIO initialization, enable/disable, error status, and cleanup.

## Important APIs, types, and functions
- `vnic_wq_alloc_bufs()` allocates block-based `struct vnic_wq_buf` arrays and links them into a circular doubly linked ring.
- `vnic_wq_alloc_with_type()` hooks a WQ control resource, disables the queue, allocates coherent descriptors, and allocates software buffers.
- `vnic_wq_alloc()` selects `RES_TYPE_WQ`.
- `enic_wq_devcmd2_alloc()` allocates a WQ backed by `RES_TYPE_DEVCMD2` for firmware command transport.
- `enic_wq_init_start()` writes ring base/size, fetch/post indices, CQ index, error interrupt settings, and error status.
- `vnic_wq_enable()` / `vnic_wq_disable()` control hardware running state.
- `vnic_wq_clean()` frees used buffers with a callback, resets cursors and hardware fetch/post/error registers, and clears descriptor memory.

## Control flow and state
Allocation mirrors RQ setup but WQ buffers include SOP/EOP completion ownership metadata and a `prev` pointer. Disable writes enable 0 and polls `running` with 10 microsecond delays. Clean walks only descriptors still used by hardware/software accounting, returns descriptor availability, then resets both hardware and software queue pointers.

## Dependencies and integration points
This file depends on `vnic_dev` ring/resource helpers and is used by ENIC TX resource allocation plus devcmd2 initialization in `vnic_dev.c`. Higher-level ENIC TX code encodes Ethernet descriptors before calling `vnic_wq_post()`.

## Risks and test signals
Risks include WQ disable timeout, incomplete cleanup on allocation failure, descriptor availability inconsistency, and devcmd2 WQ resource confusion with regular TX WQ resources. Test TX setup/teardown, devcmd2 command operation, repeated reset, TX ring wrap, and allocation-failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.h

## Purpose
`vnic_wq.h` defines the vNIC work queue MMIO layout, software WQ/ring buffer structures, devcmd2 controller structure, inline posting/service helpers, and WQ management prototypes.

## Important APIs, types, and functions
- `struct vnic_wq_ctrl` mirrors WQ hardware registers.
- `struct vnic_wq_buf` stores per-descriptor OS buffer, DMA address, length, index, SOP, descriptor pointer, write ID, completion request, skip count, compressed-send flag, and previous pointer.
- `struct vnic_wq` stores queue index, vdev, control pointer, descriptor ring, buffer blocks, `to_use`, `to_clean`, and packet accounting.
- `struct devcmd2_controller` stores devcmd2 command WQ state, result ring, posted/result/color cursors, and result size.
- `vnic_wq_doorbell()` writes the posted index after a write barrier.
- `vnic_wq_post()` records buffer metadata and advances `to_use`/availability.
- `vnic_wq_service()` walks buffers until the completed index is reached and calls a completion callback.

## Control flow and state
WQ posting is split between descriptor encoding by callers, software buffer metadata update, and explicit doorbell write. Completion service returns one descriptor at a time until the completion index is reached. Devcmd2 reuses the same WQ hardware format for firmware commands.

## Dependencies and integration points
The header is used by ENIC TX, `vnic_wq.c`, and `vnic_dev.c` devcmd2. It depends on `vnic_dev.h`, `vnic_cq.h`, and PCI declarations.

## Risks and test signals
Missing doorbells, wrong skip-count accounting, or completion callback ownership mistakes can stall TX or leak SKBs. Test TX with SG/TSO, queue stop/wake, devcmd2 command ring operation, and ring wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/wq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/wq_enet_desc.h

## Purpose
`wq_enet_desc.h` defines the 16-byte ENIC Ethernet transmit descriptor format and inline encoder/decoder helpers.

## Important APIs, types, and functions
- `struct wq_enet_desc` stores DMA address, length, MSS/loopback, header/offload flags, and VLAN tag.
- Field masks and shifts define address, 14-bit length, 14-bit MSS, loopback, 10-bit header length, offload mode, EOP, CQ entry, FCoE encapsulation, VLAN insert, and VLAN tag fields.
- Offload modes include checksum, checksum-L4, and TSO.
- `wq_enet_desc_enc()` writes the hardware descriptor in little-endian packed format.
- `wq_enet_desc_dec()` decodes fields for diagnostics/tests.

## Control flow and state
Descriptor encoding is performed by ENIC TX queue helpers before `vnic_wq_post()` advances software queue state. The descriptor itself carries hardware offload instructions for the packet or segment.

## Dependencies and integration points
`enic_res.h` uses this header to implement TX descriptor posting variants. The ENIC transmit path must supply correct DMA address, offload, VLAN, SOP/EOP, and completion flags.

## Risks and test signals
Field-width masking can hide caller errors. Risks include wrong checksum/TSO mode, header length/MSS mismatch, VLAN insertion mistakes, and missing completion entries. Tests should cover checksum offload, TSO, VLAN-tag insertion, multi-fragment TX, loopback, and descriptor decode self-tests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/wq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Kconfig

## Purpose
`cortina/Kconfig` exposes the Cortina Ethernet vendor menu and the Gemini Ethernet driver option.

## Important APIs, types, and functions
- `NET_VENDOR_CORTINA` is a vendor gate boolean defaulting to `y`.
- `GEMINI_ETHERNET` is a tristate for StorLink/Cortina Gemini dual Gigabit Ethernet.
- Dependencies: `OF` and `HAS_IOMEM`.
- Selected subsystems: `PHYLIB` and `CRC32`.

## Control flow and state
The Kconfig state controls whether `gemini.o` is built into the kernel, as a module, or not built. The vendor gate hides or shows the driver option but does not itself add code.

## Dependencies and integration points
The Gemini platform driver needs device tree probing, MMIO register access, PHY library support, and CRC32 for multicast filter hashing.

## Risks and test signals
Incorrect dependencies would allow impossible builds or hide valid configurations. Test with `COMPILE_TEST`-style configs where appropriate, built-in/module builds, and OF platform boot with PHYLIB enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Makefile

## Purpose
`cortina/Makefile` maps the Gemini Ethernet Kconfig symbol to its object file.

## Important APIs, types, and functions
- `obj-$(CONFIG_GEMINI_ETHERNET) += gemini.o` builds the Gemini driver when selected.

## Control flow and state
Kbuild expands the object list based on `CONFIG_GEMINI_ETHERNET`. No runtime state exists.

## Dependencies and integration points
It integrates the Cortina vendor directory with the kernel build system and the `GEMINI_ETHERNET` Kconfig option.

## Risks and test signals
The main risk is object name drift if the source file is renamed. Test with `CONFIG_GEMINI_ETHERNET=y` and `m` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.c

## Purpose
`gemini.c` is the Ethernet driver for the Cortina/StorLink Gemini SL351x dual-GMAC SoC. It manages a shared hardware free queue, per-port RX/TX DMA rings, PHY/link configuration, interrupts, NAPI receive processing, TX offloads, multicast filtering, ethtool controls, and platform-device probe/remove.

## Important APIs, types, and functions
- Core state: `struct gemini_ethernet` holds global registers, two ports, shared free queue, and IRQ/freeq locks. `struct gemini_ethernet_port` holds per-port netdev, MMIO bases, clock/reset, IRQ, RX/TX queues, NAPI, coalescing timer, stats, and MAC state.
- Initialization/probe: `gemini_ethernet_probe()`, `gemini_ethernet_init()`, `gemini_ethernet_port_probe()`, and module init/register functions.
- PHY/link: `gmac_setup_phy()`, `gmac_adjust_link()`, `gmac_set_flow_control()`, `gmac_enable_tx_rx()`, `gmac_disable_tx_rx()`.
- Queue setup: `gmac_setup_txqs()`, `gmac_setup_rxq()`, `geth_setup_freeq()`, `geth_resize_freeq()`, `geth_fill_freeq()`, and cleanup counterparts.
- TX path: `gmac_start_xmit()`, `gmac_map_tx_bufs()`, `gmac_clean_txq()`, `gmac_tx_irq_enable()`, `gmac_tx_irq()`, and `gmac_tx_timeout()`.
- RX path: `gmac_rx()`, `gmac_skb_if_good_frame()`, `gmac_napi_poll()`, and `gmac_coalesce_delay_expired()`.
- Interrupts: `gmac_irq()` handles per-port netdev IRQs; `gemini_port_irq()` and `gemini_port_irq_thread()` handle shared freeq refill IRQs.
- Netdev/ethtool: `gmac_351x_ops`, `gmac_351x_ethtool_ops`, stats, ringparam, coalesce, pause, ksettings, features, MTU, MAC address, and RX mode handlers.

## Control flow and state
Global probe maps common registers and populates child port devices from device tree. Each port probe maps DMA/GMAC registers, enables the port clock, resets the port, stores the port pointer into the global object, performs common interrupt/freeq initialization once both ports are present, sets netdev ops/features/MTU, obtains MAC address from device tree or hardware/random fallback, requests the threaded freeq IRQ, connects PHY, and registers the netdev.

Open flow requests the netdev IRQ, starts PHY, resizes or reuses the shared free queue, allocates per-port RX and TX rings, enables NAPI, starts DMA, enables interrupts and TX/RX, and starts queues. Stop reverses that by cancelling coalescing, stopping queues and DMA, disabling NAPI/IRQs, cleaning RX/TX rings, stopping PHY, freeing IRQ, and refreshing stats.

TX flow checks descriptor space from hardware read/write pointers, cleans completed descriptors if needed, stops the netdev queue and enables an EOF interrupt when space is still insufficient, maps the SKB head/frags into descriptors, sets TOE/TSO/checksum/bypass flags, writes the new write pointer, and cleans completions. RX flow masks/acks RX interrupt, walks RX descriptors until budget or empty, maps each DMA address back to a shared freeq page, builds frag-list SKBs through NAPI, validates hardware status/checksum metadata, performs GRO on EOF, tracks partial packets in `port->rx_skb`/`rx_frag_nr`, and returns pages/references on drops.

The shared free queue persists across both ports and is resized only when the other port is not running. Its page table maps DMA fragments back to pages and uses page references to decide when a page is reusable or must be replaced.

## Dependencies and integration points
The driver integrates platform devices and child OF devices, clocks, reset controls, MMIO, DMA coherent and streaming APIs, PHYLIB, ethtool, NAPI/GRO, netdev queueing, CRC32 multicast hashing, hrtimers, and u64 stats synchronization. It is enabled by `CONFIG_GEMINI_ETHERNET` and uses register/descriptor definitions from `gemini.h`.

## Risks and test signals
High-risk areas include shared freeq lifetime across two ports, page reference accounting, DMA mapping/unmapping on TX and RX, RX partial-frame cleanup, interrupt masking/acking races, queue resize while another port is running, hardcoded device-name-to-port-ID mapping, and TX offload behavior on large non-TCP frames. Test signals include dual-port probe/order, link changes across MII/GMII/RGMII speeds, traffic under GRO/TSO/checksum offloads, jumbo MTU bounds, multicast/promiscuous mode, ethtool ring/coalesce changes while down, freeq refill interrupts, port open/close cycles, TX queue stop/wake, and DMA state dumps on injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.h

## Purpose
`gemini.h` defines the register map, queue IDs, descriptor formats, bit masks, and packed union views used by the Cortina/StorLink Gemini GMAC driver.

## Important APIs, types, and functions
- Queue/register constants define TOE/non-TOE queue headers, software/hardware free queues, per-GMAC TX/default queues, global interrupt/status/enable/select registers, DMA registers, GMAC registers, and queue pointer helpers.
- `GET_WPTR()`, `GET_RPTR()`, `SET_WPTR()`, `SET_RPTR()`, and `RWPTR_*` macros manipulate packed ring pointers.
- Interrupt bit macros cover TX/RX data/protocol errors, TX EOF/FIN, default queues, TOE/class queues, MIB, pause, overrun, and freeq-empty events.
- Descriptor unions and structs define `gmac_txdesc` and `gmac_rxdesc` word layouts, including buffer size, status, checksum status, byte count, DMA address, SOF/EOF, TSO/MTU/checksum bits, RX offsets, and error bits.
- Config/status unions define DMA control, TX weights, queue thresholds, RX filter, GMAC config0-3, and PHY link status.
- Error/status helper macros classify RX length, overrun, CRC, and frame errors.
- Queue header structures define non-TOE queue base/size and read/write pointer words.

## Control flow and state
The header has no executable driver lifecycle, but its unions are used as typed register/descriptor snapshots throughout `gemini.c`. Hardware and software state are encoded in ring pointer registers, descriptor SOF/EOF bits, interrupt status/enable registers, and GMAC config/status registers.

## Dependencies and integration points
It depends on Linux bitops and is tightly coupled to the Gemini hardware manual and `gemini.c`. The Kconfig-selected driver uses these constants for all MMIO programming and descriptor parsing.

## Risks and test signals
Risks are register offset errors, bitfield layout/compiler assumptions, pointer wrap mistakes, and descriptor status interpretation bugs. Runtime tests should cover RX/TX descriptor dumps, interrupt routing, checksum status classification, multicast filter programming, MTU/config0 max-length selection, and ring wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Kconfig

## Purpose
`davicom/Kconfig` exposes Davicom Ethernet driver configuration options for DM9000 parallel-bus and DM9051 SPI Ethernet controllers.

## Important APIs, types, and functions
- `NET_VENDOR_DAVICOM` is the vendor menu gate boolean defaulting to `y`.
- `DM9000` is a tristate driver option depending on `ARM || MIPS || COLDFIRE || NIOS2 || COMPILE_TEST`, selecting `CRC32` and `MII`.
- `DM9000_FORCE_SIMPLE_PHY_POLL` is a boolean under `DM9000` that forces NSR LinkStatus polling instead of MII PHY reads.
- `DM9051` is a tristate SPI driver option depending on `SPI`, selecting `CRC32`, `MDIO`, `PHYLIB`, and `REGMAP_SPI`.

## Control flow and state
Kconfig symbols determine whether `dm9000.o` and `dm9051.o` are built. The simple PHY polling option changes DM9000 runtime link-detection behavior at compile time.

## Dependencies and integration points
This file integrates Davicom drivers with architecture, SPI, MDIO/PHYLIB, MII, regmap, and CRC32 subsystems. Build output is wired by the Davicom Makefile.

## Risks and test signals
Risks include insufficient dependencies for buildability and compile-time PHY polling option misuse on external PHY designs. Test signals are allmodconfig/COMPILE_TEST builds, architecture-specific DM9000 builds, SPI DM9051 module builds, and link detection validation with and without simple polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Makefile

## Purpose
`davicom/Makefile` maps Davicom Ethernet Kconfig symbols to their driver object files.

## Important APIs, types, and functions
- `obj-$(CONFIG_DM9000) += dm9000.o` builds the DM9000 driver when selected.
- `obj-$(CONFIG_DM9051) += dm9051.o` builds the DM9051 SPI driver when selected.

## Control flow and state
Kbuild expands object lists according to the selected Kconfig symbols. No runtime state exists in this file.

## Dependencies and integration points
It connects `davicom/Kconfig` options to the kernel build system and source files in the same directory.

## Risks and test signals
The main risks are stale object names or missing Kconfig wiring. Test by building `CONFIG_DM9000=y/m` and `CONFIG_DM9051=y/m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Makefile -->
