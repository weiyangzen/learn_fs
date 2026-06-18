# Research: subset-b-004644

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.c

Purpose: wires the SFC `ndo_setup_tc` and indirect TC callbacks into the driver flower offload engine. It owns `struct efx_tc_block_binding`, which records the NIC, optional representor, target netdev, and flow block used to route TC flower changes to `efx_tc_flower()`.

Important APIs and control flow: `efx_tc_setup()` rejects VFs and non-TC NIC state, then dispatches direct `TC_SETUP_CLSFLOWER` or `TC_SETUP_BLOCK`. `efx_tc_setup_block()` accepts only ingress clsact blocks, creates a binding on bind, allocates a `flow_block_cb`, and removes it on unbind. `efx_tc_indr_setup_cb()` is the indirect block path; it handles supported ingress blocks and rejects OVS internal/egress cases currently not offloaded. `efx_tc_netdev_event()` forwards unregister events to `efx_tc_unregister_egdev()` for tunnel egress cleanup.

State and dependencies: state is in `efx->tc->block_list`; RTNL is assumed for lookup. Dependencies include Linux flow block APIs, `tc.h` for flower programming, and encap-action egress-device teardown. Persistence is runtime-only; bindings are freed through the flow-block callback release path.

Integration, risks, and tests: this file is the entry point from netdev TC into MAE offload, so duplicate bind/unbind handling and teardown ordering are the main risks. Test signals are TC flower add/delete/stats on PFs and representors, indirect block registration through tunnel/bridge devices, netdev unregister while offloads exist, and driver teardown with already-unbound blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.h

Purpose: declares the SFC TC binding interface used by netdev setup, representors, indirect block registration, and netdev notifiers. It is compiled only when `CONFIG_SFC_SRIOV` is enabled.

Important APIs/types: exports `efx_tc_setup_block()`, `efx_tc_setup()`, `efx_tc_indr_setup_cb()`, `efx_tc_netdev_event()`, and `efx_tc_block_unbind()`. It forward-declares `struct efx_rep` and includes `net_driver.h`; with SR-IOV disabled it provides a no-op `efx_tc_netdev_event()` returning `NOTIFY_DONE`.

State and integration: this header creates the compile-time boundary between the core driver and SR-IOV/representor TC code. No state is persisted here.

Risks and tests: call sites must be guarded by the same config assumptions, because most declarations disappear when SR-IOV is disabled. Build coverage should include `CONFIG_SFC_SRIOV=y/m` and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_conntrack.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_conntrack.c

Purpose: offloads netfilter flowtable conntrack entries into SFC MAE connection-tracking tables. It manages CT zones, CT entries, NAT metadata, hardware counters, and callbacks from `nf_flow_table_offload_add_cb()`.

Important APIs and functions: `efx_tc_init_conntrack()`, `efx_tc_destroy_conntrack()`, and `efx_tc_fini_conntrack()` manage two rhashtables: `ct_zone_ht` keyed by zone and `ct_ht` keyed by cookie-sized CT entry fields. `efx_tc_ct_register_zone()` reference-counts zones and registers `efx_tc_flow_block()` with netfilter; `efx_tc_ct_unregister_zone()` removes the callback, tears down hardware CT entries, waits for RCU, frees counters, and destroys the zone. `efx_tc_ct_replace()`, `efx_tc_ct_destroy()`, and `efx_tc_ct_stats()` implement flower replace/destroy/stats for CT entries.

Control flow: replace allocates a zeroed `efx_tc_ct_entry`, inserts it by cookie to prevent duplicates, parses exact-match IPv4/IPv6 TCP/UDP five-tuple fields, parses `FLOW_ACTION_CT_METADATA` and supported IPv4 NAT `FLOW_ACTION_MANGLE` edits, fills default NAT fields, allocates a CT counter, inserts the CT into MAE, then links it under the zone mutex. Destroy finds the entry, removes it from the zone list and hardware, removes the rhashtable entry, waits for RCU readers, releases the counter, and frees memory. Stats reports delayed last-use time from the CT counter.

State and dependencies: state is split between per-NIC rhashtables, per-zone linked lists protected by `ct_zone->mutex`, MAE firmware CT state, netfilter callbacks, and TC counter objects. RCU protects stats readers from concurrent removal. The parser depends on flow dissector exact masks and only supports IPv4 NAT; IPv6 NAT and labels are rejected.

Risks and test signals: high-risk areas are duplicate cookie races, cleanup ordering when callbacks and driver teardown overlap, RCU/counter lifetime, and NAT direction consistency across multiple mangle actions. Test with add/delete/stats for IPv4/IPv6 TCP/UDP CT, unsupported masks/actions returning `-EOPNOTSUPP`, NAT source/dest combinations, repeated zone registration, netfilter flowtable removal, and driver unload with live entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_conntrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_conntrack.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_conntrack.h

Purpose: defines conntrack offload state shared between the SFC TC parser, MAE programming layer, and netfilter flowtable callback code.

Important types/APIs: `struct efx_tc_ct_zone` stores zone id, rhashtable linkage, refcount, `nf_flowtable`, owning NIC, a mutex, and the list of CT entries in that zone. `struct efx_tc_ct_entry` stores cookie, protocol tuple, NAT direction and translated fields, zone pointer, CT mark, attached counter, and zone-list linkage. Public functions initialize/finalize tables and register/unregister CT zones.

State and integration: the header exists only under `CONFIG_SFC_SRIOV` and includes `nf_flow_table.h` and refcount support. The structures are runtime-only and are mirrored into firmware by `tc_conntrack.c` and MAE helpers.

Risks and tests: structure fields are key material for rhashtable lookup, so changes must stay consistent with `efx_tc_ct_ht_params`. Build and runtime tests need SR-IOV-enabled TC CT coverage plus teardown with non-empty zone lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.c

Purpose: manages MAE counters used by SFC TC offload and receives firmware counter-update packets on a dedicated channel. It supports action-rule, conntrack, and outer-rule counter types.

Important APIs and functions: `efx_tc_init_counters()`, `efx_tc_destroy_counters()`, and `efx_tc_fini_counters()` manage counter-id and firmware-id rhashtables. `efx_tc_flower_allocate_counter()` allocates a firmware MAE counter and inserts it into `counter_ht`; `efx_tc_flower_release_counter()` removes it, frees firmware state, waits for RCU, flushes work, and frees memory. `efx_tc_flower_get_counter_index()` maps TC cookies to refcounted counter objects. `efx_tc_channel_type` describes the MAE counter RX channel.

Control flow: counter updates arrive through `efx_tc_rx()`, which decodes v1 or v2 packet formats, converts little-endian packed fields, validates identifiers, and calls `efx_tc_counter_update()`. Updates use a generation mark to ignore stale packets after firmware ID reuse, add packet/byte deltas, update `touched`, and schedule work. The work function walks action-set users and refreshes neighbour entries for encap actions that have seen traffic.

State and dependencies: persistent runtime state is in `efx->tc->counter_ht`, `counter_id_ht`, `seen_gen[]`, `flush_gen[]`, and wait queues. Each counter has a spinlock, generation, packet/byte totals, old user-reported totals, touched jiffies, work item, and user list. Dependencies include MAE firmware APIs, RX buffer handling, neighbour tables, and `mae_counter_format.h` packet layouts.

Risks and test signals: risks include firmware counter ID reuse, delayed packets racing with free, work item/list lifetime, malformed counter packet parsing, and CT one-bit counter semantics. Test with counter allocate/release loops, stats reads while deleting rules, v1/v2 update packets, flush wait wakeups, no extra interrupt vector path, and encap neighbour refresh after traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.h

Purpose: declares the SFC TC counter model and public counter-management functions.

Important types/APIs: `enum efx_tc_counter_type` aliases MAE counter types for action rules, conntrack, and outer rules. `struct efx_tc_counter` stores firmware id, type, rhashtable linkage, update lock, generation, packet/byte accounting, touched time, work item, and action-set users. `struct efx_tc_counter_index` maps a TC cookie to a refcounted counter. The header exports allocation, release, get/put/find-by-cookie helpers and `efx_tc_channel_type`.

State and integration: fields are consumed by `tc.c`, `tc_conntrack.c`, `tc_encap_actions.c`, and MAE channel setup. The rhashtable key layout depends on field ordering before `linkage`.

Risks and tests: changes need ABI-like coordination with rhashtable params and MAE counter formats. Compile SR-IOV TC and run offload add/delete/stats with counter streaming enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_encap_actions.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_encap_actions.c

Purpose: implements SFC TC tunnel encapsulation metadata, neighbour binding, generated VXLAN/Geneve headers, and rule readiness updates when neighbour state changes.

Important APIs and functions: `efx_tc_init_encap_actions()`, `efx_tc_destroy_encap_actions()`, and `efx_tc_fini_encap_actions()` manage neighbour and encap rhashtables. `efx_tc_flower_create_encap_md()` validates tunnel info, binds the route/neighbour, checks that the egress device is on the switch, generates the outer header, and allocates MAE encap metadata. `efx_tc_flower_release_encap_md()` releases the refcounted encap object. `efx_tc_netevent_event()` handles neighbour updates; `efx_tc_unregister_egdev()` invalidates encap users when an egress netdev unregisters.

Control flow: creating encap metadata identifies VXLAN/Geneve and IPv4/IPv6 mode, rejects options, deduplicates by rhashtable key, binds a neighbour with route lookup, links encap users to the neighbour, resolves destination m-port, generates Ethernet/IP/UDP/tunnel headers, and writes them to firmware. Neighbour events update cached hardware address and validity, schedule work, switch user rules to fallback while headers change, update MAE encap metadata, then switch ready rules back to the primary action set.

State and dependencies: `struct efx_neigh_binder` holds net namespace, destination key, cached MAC, TTL, egdev reference, refcount, user list, RCU-visible rhashtable linkage, and work item. `struct efx_tc_encap_action` holds tunnel key, generated header, neighbour pointer, refcount, users, firmware id, and destination m-port. Dependencies include route lookup, ARP/ND tables, netevent notifier, tunnel-key actions, MAE encap APIs, representor lookup, and the TC mutex.

Risks and test signals: risks are route/neighbour lifetime, refcount failures during scheduled work, egress device unregister races, leaking stale Ethernet headers, unsupported tunnel options, and IPv6-disabled builds. Test VXLAN and Geneve over IPv4/IPv6, unresolved then resolved neighbours, neighbour MAC change, egress device removal, fallback rule updates, repeated shared encap references, and module teardown with live encap entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_encap_actions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_encap_actions.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_encap_actions.h

Purpose: defines tunnel encap and neighbour-binding state for SFC TC offload.

Important types/APIs: `struct efx_neigh_binder` tracks the route/neighbour backing one or more encap actions, including namespace, IPv4/IPv6 key, hardware address, validity, TTL, egdev references, refcount, users, work, and owning NIC. `EFX_TC_MAX_ENCAP_HDR` caps generated headers at 126 bytes. `struct efx_tc_encap_action` stores type, `ip_tunnel_key`, destination m-port, header bytes, neighbour pointer, user lists, rhashtable linkage, refcount, and firmware id. Public functions initialize/finalize, create/release encap metadata, check rule readiness, unregister egress devices, and receive netevents.

State and integration: compiled under `CONFIG_SFC_SRIOV`, includes tunnel-key action definitions, and is consumed by flower parsing and counter work. Runtime state is firmware-backed but not persisted across driver reload.

Risks and tests: structure layout participates in rhashtable keys and list ownership; changes need careful lifetime tests. Build with IPv6 enabled/disabled and test tunnel offload with neighbour churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_encap_actions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.c

Purpose: implements the main SFC transmit path for SKBs and XDP frames, including queue selection, checksum-type selection integration, copybreak/PIO paths, descriptor push batching, and single-completion handling.

Important functions: `__efx_enqueue_skb()` maps or copies one skb to a TX queue, handling TSOv1, TSOv2, software TSO fallback, PIO, copybreak, DMA mapping, timestamps, queue stopping, and doorbells. `efx_hard_start_xmit()` is the netdev transmit entry point and diverts PTP timestamp packets. `efx_xdp_tx_buffers()` maps XDP frames on per-CPU XDP TX queues. `efx_xmit_done_single()` completes one packet by walking descriptors until the SKB-final buffer. `efx_init_tx_queue_core_txq()` binds a driver TX queue to the core netdev queue.

Control flow: normal SKB TX computes `segments`, attempts hardware TSO when needed, falls back to software GSO only for queue restrictions, otherwise may use PIO or copybreak for short/fragmented packets, then maps remaining data through `efx_tx_map_data()`. It records timestamps, pessimistically stops queues near thresholds, marks `xmit_pending`, and pushes all channel queues when xmit-more batching ends. Error unwind frees partially enqueued buffers and consumes the skb.

State and dependencies: uses per-queue insert/read/write counters, copy-buffer pages, optional PIO buffer, XDP queue arrays, netdev queue state, PTP helpers, NIC-specific descriptor push functions, and thresholds from `efx`. State is volatile queue state only.

Risks and test signals: risks include queue stop/wake races, partial DMA mapping unwind, PIO alignment assumptions, XDP queue mode locking, and PTP packets bypassing pending doorbells. Test high-rate TX with `xmit_more`, GSO/TSO on and off, copybreak fragmented packets, PTP timestamp TX, XDP_TX/redirect in dedicated and borrowed queue modes, DMA mapping failures, and reset on spurious completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.h

Purpose: provides internal TX declarations and checksum queue-type selection for SFC.

Important APIs: declares `efx_tx_limit_len()` and defines `efx_tx_csum_type_skb()`. The inline helper maps `CHECKSUM_PARTIAL` SKBs to no checksum, outer checksum, inner checksum, or combined inner/outer checksum queue types depending on encapsulation and GSO tunnel checksum requirements.

State and integration: no local state. It integrates `tx.c`, NIC-specific TX queue lookup, and advertised offload features by selecting a queue type matching what the skb requires.

Risks and tests: if feature advertising and this helper diverge, `efx_hard_start_xmit()` may not find a suitable queue. Test encapsulated and non-encapsulated checksum SKBs, UDP tunnel checksum GSO, and no-offload SKBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.c

Purpose: contains shared SFC TX queue allocation, initialization, teardown, descriptor cleanup, DMA mapping, and software TSO fallback helpers used by multiple NIC generations.

Important functions: `efx_probe_tx_queue()` allocates software rings, copy-buffer page metadata, and NIC hardware TX rings. `efx_init_tx_queue()`, `efx_fini_tx_queue()`, and `efx_remove_tx_queue()` reset counters, initialize hardware, drain outstanding buffers, and free resources. `efx_dequeue_buffer()` unmaps DMA and consumes SKBs/XDP frames. `efx_xmit_done()` handles completion ranges and queue wakeups. `efx_tx_map_chunk()` splits DMA ranges by NIC limits. `efx_tx_map_data()` maps skb head/frags and records the final buffer as the completion owner. `efx_tx_tso_fallback()` software-segments and re-enqueues.

Control flow: probing sets a power-of-two descriptor mask and registers the queue by type. Completion walks buffers up to the hardware index, detects spurious completions, updates packet/byte counters, wakes stopped queues when fill falls below the wake threshold, and publishes empty state with barriers. Mapping records unmap ownership only on the final descriptor for each mapped region and tags the last buffer with `EFX_TX_BUF_SKB`.

State and dependencies: queue state includes buffers, copy pages, descriptor counts, completion counters, timestamp state, XDP flags, and per-type channel lookup. Dependencies include NIC-specific `efx_nic_*` operations, DMA APIs, GSO, and PTP timestamp conversion.

Risks and test signals: risks include DMA leak on mid-fragment mapping failure before caller unwind, incorrect final-buffer ownership, stale queue-empty publication, and software TSO recursion/backpressure. Test probe/remove failures, forced DMA mapping errors, completion of merged descriptors, XDP completion accounting, queue wake thresholds, and GSO fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.h

Purpose: declares shared SFC TX queue lifecycle, completion, mapping, and TSO fallback helpers.

Important APIs: exposes queue probe/init/fini/remove, buffer dequeue, completion functions, enqueue unwind, DMA chunk/data mapping, TSO header-length calculation, maximum descriptor estimation, and software TSO fallback. `efx_tx_buffer_in_use()` treats nonzero length or option descriptors as active.

State and integration: no independent state; it is included by `tx.c`, TSO paths, and NIC-specific TX code. External `efx_separate_tx_channels` is declared for channel topology decisions elsewhere.

Risks and tests: callers must obey ownership rules documented in `efx_enqueue_unwind()` and must pass appropriate completion counters. Build-test with all SFC NIC generations and runtime-test TX queue teardown with outstanding buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_tso.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_tso.c

Purpose: implements legacy SFC TSOv1 segmentation using firmware TSO option descriptors, predating the newer EF10 TSOv2 descriptor path.

Important types/functions: `struct tso_state` tracks output sequence/IP ID, packet space, current input DMA mapping, header offsets/lengths, and header DMA ownership. `efx_enqueue_skb_tso()` is the exported enqueue path. Helpers validate protocol, map headers/fragments, build TSO option descriptors, split payload into MSS-sized packets, and attach skb/DMA ownership to final descriptors.

Control flow: the path verifies TCP over IPv4/IPv6, maps the linear header area, starts the first output packet, then repeatedly fills packet payload from skb head or page frags. At each segment boundary it emits a TSO option descriptor and header descriptor using original headers plus updated sequence/IP ID values. The final payload descriptor owns the skb; the last header descriptor owns the header DMA unmap. Failure unmaps the active fragment and header mapping and returns an error so the caller can unwind descriptors.

State and dependencies: uses queue insert counters and NIC-specific `tx_limit_len()`, DMA mapping APIs, TCP/IP header helpers, and EF10 descriptor bit definitions. It has no persistent state beyond descriptors enqueued to the TX ring.

Risks and test signals: risks are header DMA ownership across multiple segments, fragment boundary handling, TCP flag masking on non-final segments, IPv4 ID progression, and queue overflow assumptions. Test IPv4/IPv6 GSO with payload in head and frags, boundary-crossing fragments, single-segment fallback avoidance, induced DMA failure, and comparison with software GSO packet counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_tso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/workarounds.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/workarounds.h

Purpose: centralizes SFC hardware workaround predicates for EF10-era NIC revisions.

Important macros: `EFX_WORKAROUND_EF10()` checks Hunt A0 or newer. `EFX_EF10_WORKAROUND_35388()` and `EFX_WORKAROUND_35388()` gate the event-block register lockup workaround for Hunt A0 when the NIC-data flag is set. `EFX_EF10_WORKAROUND_61265()` exposes the moderation timer MCDI-access workaround flag.

State and dependencies: macros depend on `efx_nic_rev()` and `struct efx_ef10_nic_data` fields populated by NIC probing. There is no state in the header.

Risks and tests: incorrect revision predicates can enable slow paths unnecessarily or skip required hardware safety behavior. Test with NIC-data quirk flags for Hunt A0 and later revisions, especially event queue and interrupt moderation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/workarounds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Kconfig

Purpose: defines configuration prompts for SGI Ethernet drivers.

Important symbols: `NET_VENDOR_SGI` gates the vendor menu and depends on either PCI IOC3 MFD support or SGI IP32. `SGI_IOC3_ETH` is a built-in boolean for IOC3 Ethernet, depending on `PCI && SGI_MFD_IOC3` and selecting CRC16, CRC32, and MII. `SGI_O2MACE_ETH` is tristate O2 MACE support and depends on `SGI_IP32=y`.

Integration and state: Kconfig controls whether `ioc3-eth.o` and `meth.o` are reachable from the SGI Makefile. It has no runtime state.

Risks and tests: dependency mistakes break architecture-specific builds. Test `olddefconfig`/build combinations for SGI IP32, SGI_MFD_IOC3, and generic PCI-disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Makefile

Purpose: maps SGI Ethernet Kconfig symbols to object files.

Important entries: `obj-$(CONFIG_SGI_O2MACE_ETH) += meth.o` and `obj-$(CONFIG_SGI_IOC3_ETH) += ioc3-eth.o`.

Integration and state: participates in kernel kbuild only. No runtime state.

Risks and tests: object-name drift or wrong symbol names would silently omit drivers. Test by building both SGI symbols as enabled/module where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/ioc3-eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/ioc3-eth.c

Purpose: SGI IOC3 Ethernet platform driver for IOC3 ASIC-based Ethernet cards. It manages IOC3 RX/TX rings, MII PHY, NVMEM MAC retrieval, multicast filtering, checksum assist, interrupts, and netdev/ethtool operations.

Important types/functions: `struct ioc3_private` stores MMIO registers, DMA device, SSRAM, RX/TX rings and DMA addresses, skb arrays, producer/consumer indices, cached EMCR/multicast registers, lock, MII state, and media timer. `ioc3eth_probe()` allocates the netdev, maps resources, reads MAC from one-wire NVMEM, requests IRQ, allocates coherent rings, initializes MII and SSRAM, and registers the netdev. `ioc3_open()`/`ioc3_close()` initialize, allocate/free RX buffers, start/stop hardware, and manage the timer. `ioc3_start_xmit()`, `ioc3_rx()`, `ioc3_tx()`, and `ioc3_interrupt()` are the datapath.

Control flow: RX uses a fixed hardware RX ring with a smaller active buffer pool; valid descriptors are converted to SKBs, optionally marked checksum-unnecessary for IPv4 TCP/UDP, replaced with fresh mapped buffers, and the hardware producer pointer is armed. TX either copies short packets into descriptors or DMA maps one/two buffers for larger packets, handles the IOC3 16K split constraint, updates producer pointer, and stops the queue near full. Interrupts acknowledge status, run fatal-error recovery, then RX and TX cleanup. Error/timeout paths stop hardware, free RX buffers, clean TX ring, reinitialize, and wake the queue.

State and dependencies: runtime state is in coherent rings, mapped RX SKBs, pending TX SKBs, MII timer, and hardware registers. Dependencies include SGI IOC3 headers, PCI bridge mapping attributes, NVMEM consumer API, MII helpers, CRC16/CRC32, DMA APIs, and platform-device resources.

Risks and test signals: notable risks include NVMEM probe deferral, DMA address mapping on PCI-Xtalk bridges, ring pointer alignment, a likely-sensitive TX split path, timer/remove ordering, and recovery after fatal IOC3 errors. Test probe/remove, NVMEM absent/deferred/invalid CRC, RX checksum on/off, multicast/promiscuous filters, MII ethtool changes, TX timeout reset, and interrupt storms/fatal error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/ioc3-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.c

Purpose: SGI O2 MACE Fast Ethernet platform driver. It controls the IP32 MACE Ethernet block, MII PHY probing, DMA rings, interrupt handling, multicast filtering, and netdev operations.

Important types/functions: `struct meth_private` caches MAC/DMA control registers, PHY address, TX ring and skb tracking, RX buffers, multicast filter, and lock. `meth_probe()` allocates/registers the netdev using the global `o2meth_eaddr`. `meth_open()` resets hardware, allocates rings, requests IRQ, enables DMA, and starts the queue. `meth_release()` disables DMA/interrupts and frees rings. Datapath functions are `meth_tx()`, `meth_add_to_tx_ring()`, `meth_rx()`, `meth_tx_cleanup()`, and `meth_interrupt()`.

Control flow: reset toggles MAC reset, loads the MAC, probes MII, configures MAC filtering and DMA offsets, and checks link. RX disables RX interrupts, processes FIFO entries up to the hardware read pointer, validates status/length, replaces or recycles SKBs, remaps buffers, pushes packets to `netif_rx()`, and re-enables RX. TX prepares descriptors differently for short packets, one-page DMA, or two-page DMA, writes the hardware producer pointer, and enables TX interrupts. Completion consumes SKBs and updates counters. Timeout resets hardware, frees/reallocates rings, restarts DMA, and wakes the queue.

State and dependencies: state lives in MACE MMIO globals, DMA coherent TX ring, per-RX SKBs and DMA mappings, and software ring indices. Dependencies include SGI IP32 MACE headers, MII register definitions, CRC32 for multicast hash, DMA APIs, and platform driver registration.

Risks and test signals: risks include old-style global hardware access, RX allocation without explicit NULL checks in ring init, DMA map error handling gaps in TX prep, multicast hash correctness, and timeout reset while interrupts race. Test open/close, link negotiation, RX underflow/overflow, short/one-page/two-page TX, multicast/promiscuous mode, tx timeout, and IRQ cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.h

Purpose: hardware layout and bit definitions for the SGI O2 MACE Ethernet driver.

Important types/macros: defines TX/RX ring sizes and buffer offsets, `tx_status_vector`, `tx_packet_hdr`, `tx_cat_ptr`, `tx_packet`, `rx_status_vector`, and `rx_packet`. It enumerates MAC control bits, DMA control bits, RX FIFO pointer extraction, RX status/error masks, interrupt bits, TX status bits, TX command flags, MDIO busy/data masks, known PHY IDs, and `ADVANCE_RX_PTR()`.

State and integration: this header is consumed by `meth.c` to format descriptors and parse hardware status. It has no runtime state but its bitfields describe hardware-visible memory layout.

Risks and tests: C bitfield layout and endian assumptions are sensitive; descriptor definitions must match the MACE block. Test with real hardware or emulator RX/TX descriptor completion, plus build coverage on the SGI IP32 architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Kconfig

Purpose: defines configuration entries for Silan Ethernet devices.

Important symbols: `NET_VENDOR_SILAN` gates the vendor menu and depends on PCI. `SC92031` is a tristate Silan SC92031 PCI Fast Ethernet driver that depends on PCI and selects CRC32.

Integration and state: controls compilation of `sc92031.o` through the Silan Makefile. No runtime state.

Risks and tests: incorrect dependencies can expose the driver on unsupported systems or miss CRC helpers. Test PCI-enabled and disabled config builds and module build for `SC92031=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Makefile

Purpose: maps the Silan SC92031 Kconfig symbol to its object file.

Important entry: `obj-$(CONFIG_SC92031) += sc92031.o`.

Integration and state: kbuild-only file with no runtime behavior.

Risks and tests: symbol/object mismatch would omit the driver. Build-test `CONFIG_SC92031=y` and `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/sc92031.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/sc92031.c

Purpose: PCI Fast Ethernet driver for Silan SC92031/Rsltek 8139D-like devices. It uses a large coherent RX ring, four TX bounce buffers, tasklet-based interrupt processing, MII/PHY control, ethtool link/WOL/stat hooks, and PCI PM suspend/resume.

Important types/functions: `struct sc92031_priv` stores lock, MMIO base, PCI device, tasklet, RX ring DMA, TX head/tail and coherent bounce buffers, interrupt mask/status, cached RX/TX/PM configs, multicast flags, private stats, and netdev pointer. `sc92031_probe()` enables PCI, maps BAR, reads MAC registers, configures netdev features, tasklet, PM wake, and registers. `sc92031_open()` allocates rings, requests IRQ, resets hardware, enables interrupts, and starts/stops queue based on carrier. `sc92031_start_xmit()` copies and checksums SKBs into TX bounce buffers. `sc92031_tasklet()` handles TX/RX/link work after the IRQ masks interrupts.

Control flow: reset disables PM, soft-resets, clears interrupt and multicast registers, writes RX buffer base, clears TX state, configures RX buffer size, resets PHY according to module `media`, checks link, restores PM config, and clears status. IRQ masks device interrupts, reads and filters status, stores it, and schedules a tasklet. The tasklet drains TX completions, copies RX packets from the circular ring to new SKBs, handles overflow/timeout/link events, and restores the interrupt mask. Link checks program RX/TX configuration, duplex, flow control, multicast filters, and carrier state.

State and dependencies: runtime state includes coherent RX/TX buffers, monotonic TX head/tail counters, atomic interrupt mask, cached register copies, tasklet state, PM config, and netdev stats. Dependencies include PCI DMA/I/O APIs, MII register definitions, CRC32 multicast hashing, ethtool legacy link-mode conversion, and netpoll optional hooks.

Risks and test signals: risks include ring wrap parsing, missing DMA mapping because TX uses coherent bounce buffers, tasklet/IRQ masking races, guessed ethtool/WOL behavior noted by FIXME comments, link configuration correctness, and suspend/resume preserving PM state. Test probe/remove, open/stop, link up/down interrupts, RX wrap and malformed frames, TX ring full/wake, tx timeout reset, multicast/promiscuous filters, WOL get/set, netpoll, and suspend/resume with interface running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/sc92031.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Kconfig

Purpose: defines configuration entries for Silicon Integrated Systems Ethernet drivers.

Important symbols: `NET_VENDOR_SIS` gates the vendor menu and depends on PCI. `SIS900` builds SiS 900/7016 Fast Ethernet support, depends on `PCI && HAS_IOPORT`, and selects CRC32 and MII. `SIS190` builds SiS190/SiS191 gigabit support with the same dependency and helper selections.

Integration and state: controls the SiS Makefile entries for `sis900.o` and `sis190.o`. It has no runtime state.

Risks and tests: drivers require I/O port support, so dependency coverage matters on architectures without PIO. Build-test `SIS900` and `SIS190` as built-in and module where PCI/HAS_IOPORT are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Makefile

Purpose: maps SiS Ethernet Kconfig symbols to object files.

Important entries: `obj-$(CONFIG_SIS190) += sis190.o` and `obj-$(CONFIG_SIS900) += sis900.o`.

Integration and state: kbuild-only; no runtime state or driver logic appears here.

Risks and tests: object mapping must stay aligned with Kconfig symbol names and source files. Test module and built-in builds for both SiS drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Makefile -->
