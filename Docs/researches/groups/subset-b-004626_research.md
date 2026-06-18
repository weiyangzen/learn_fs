# subset-b-004626 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/rx.c

## Purpose
Implements the Falcon-era EF4 receive data path: RX descriptor allocation, page DMA mapping/recycling, packet completion handling, GRO/SKB delivery, queue lifecycle, optional RFS acceleration, and multicast-recipient filter classification.

## Important APIs, types, and functions
- Public queue/data-path entry points: `ef4_rx_config_page_split`, `ef4_fast_push_rx_descriptors`, `ef4_rx_slow_fill`, `ef4_rx_packet`, `__ef4_rx_packet`, `ef4_probe_rx_queue`, `ef4_init_rx_queue`, `ef4_fini_rx_queue`, `ef4_remove_rx_queue`.
- Optional RFS APIs under `CONFIG_RFS_ACCEL`: `ef4_filter_rfs` and `__ef4_filter_rfs_expire`.
- Filter utility: `ef4_filter_is_mc_recipient`.
- Internal helpers manage page layout and DMA state: `ef4_init_rx_buffers`, `ef4_reuse_page`, `ef4_recycle_rx_page(s)`, `ef4_unmap_rx_buffer`, `ef4_free_rx_buffers`, `ef4_rx_packet_gro`, and `ef4_rx_mk_skb`.

## Control flow
Queue setup computes a power-of-two software ring, probes the NIC RX ring, initializes page recycling, and programs the hardware descriptor ring. Refill runs from NAPI or disabled-NAPI context and keeps the descriptor fill level above `fast_fill_trigger`; allocation failures schedule a slow-fill event so the queue is not left empty. Completion enters `ef4_rx_packet`, validates fragment count and length, DMA-syncs the buffers, skips the hardware prefix, recycles pages, flushes the previous prefetched packet, and stores the current packet in `channel->rx_pkt_*`. The second half, `__ef4_rx_packet`, reads prefix length if needed, diverts packets to loopback self-test when active, strips checksum flags if RX checksum offload is disabled, and delivers through GRO for TCP packets without a channel interception hook or through `netif_receive_skb`.

## State and persistence behavior
The file maintains per-queue counters (`added_count`, `removed_count`, `notified_count`, recycle counters, min fill, slow fill count) and a per-queue page recycle ring. DMA mapping state is stored in `struct ef4_rx_page_state` at the start of each page and per-buffer `dma_addr`, `page`, `page_offset`, `len`, and flags. Page reuse is allowed only when the page refcount proves the driver holds the only reference; otherwise the page is unmapped and released. No durable persistence exists; all state is in kernel memory and hardware DMA rings.

## Dependencies and integration points
Depends on Linux DMA, page, SKB, NAPI, GRO, RFS, flow dissector, checksum, IPv4/IPv6 helpers, and netdevice features. Driver dependencies include `net_driver.h`, `efx.h`, `filter.h`, `nic.h`, `selftest.h`, and `workarounds.h`. It calls NIC-type operations for descriptor notification and RFS filters, integrates with `ef4_loopback_rx_packet`, and schedules resets for hardware workaround paths.

## Risks and test signals
Key risks are DMA lifetime mistakes, page-recycle refcount races, fragment length validation errors, and missed queue refill causing RX starvation. Workaround `EF4_WORKAROUND_8071` intentionally leaks seriously overlength packets and schedules RX recovery, so reset and leak behavior should be monitored. Test signals include RX packet/drop/overlength counters, recycle success/fail/full counters, loopback self-test receive counts, GRO delivery, RFS insertion/expiration logs, and queue teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.c

## Purpose
Provides EF4/Falcon online and offline self-tests for PHY liveness, NVRAM, interrupts, event queues, PHY-specific BIST, MAC/PHY loopback traffic, and asynchronous event interrupt diagnostics.

## Important APIs, types, and functions
- Public APIs: `ef4_selftest`, `ef4_loopback_rx_packet`, `ef4_selftest_async_start`, `ef4_selftest_async_cancel`, and `ef4_selftest_async_work`.
- Internal loopback model: `struct ef4_loopback_payload` and `struct ef4_loopback_state`.
- Online tests: `ef4_test_phy_alive`, `ef4_test_nvram`, `ef4_test_interrupts`, `ef4_test_eventq_irq`, and `ef4_test_phy`.
- Offline loopback flow: `ef4_test_loopbacks`, `ef4_wait_for_link`, `ef4_test_loopback`, `ef4_begin_loopback`, `ef4_poll_loopback`, and `ef4_end_loopback`.

## Control flow
`ef4_selftest` first cancels pending async diagnostics, runs online PHY/NVRAM/IRQ/eventq tests, and returns early on online failure. Without `ETH_TEST_FL_OFFLINE`, it runs PHY tests only. Offline tests detach the netdev, optionally run chip tests, force the PHY out of low power and loopback, run PHY tests, then test all supported loopback modes and enabled TX queue types. Loopback testing installs `efx->loopback_selftest`, reconfigures the port for each mode, waits for stable link, sends controlled UDP/IP payload bursts through specific TX queues, and validates returned packets in the RX path callback.

## State and persistence behavior
Self-test results are accumulated in `struct ef4_self_tests`, where non-counter tests use `1` for pass, `-1` for failure, and `0` for unavailable. Loopback uses transient heap state stored in `efx->loopback_selftest`, atomic RX good/bad counters, a payload iteration counter, and an SKB pointer array used to count TX completions. The original `phy_mode` and `loopback_mode` are restored before reattaching the device. No persistent storage is changed.

## Dependencies and integration points
Uses netdevice locking/detach, ethtool test flags, delayed work, jiffies timeouts, PCI/netif logging, and driver operations from `efx->type`, `efx->phy_op`, TX queue enqueue, RX loopback diversion, MAC lock protected reconfiguration, and NIC event/IRQ test hooks.

## Risks and test signals
Risks include false interrupt failures under high IRQ latency, disruptive offline tests affecting link traffic, loopback packet races during flush, and TX completion counting relying on SKB reference state. Strong test signals are per-channel event DMA/interrupt arrays, loopback `tx_sent`, `tx_done`, `rx_good`, `rx_bad`, PHY test names/results, timeout logs, and restoration of netdev attachment and original PHY state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.h

## Purpose
Declares the Falcon EF4 self-test result structures and exported self-test entry points consumed by ethtool-facing code and the RX loopback path.

## Important APIs, types, and functions
- `struct ef4_loopback_self_tests` stores per-TXQ sent/completed counts plus aggregate good/bad RX loopback counts.
- `struct ef4_self_tests` stores online test results, per-channel event queue results, offline memory/register results, PHY extended test results, and loopback results indexed by loopback mode.
- `EF4_MAX_PHY_TESTS` bounds PHY-specific results.
- Function declarations cover loopback RX packet inspection and synchronous/asynchronous self-test execution.

## Control flow
The header itself has no runtime control flow. It defines the data contract used by `selftest.c` and by consumers that display or interpret the test matrix.

## State and persistence behavior
The structures are caller-owned result containers. They do not persist beyond the caller's lifetime and do not own dynamic memory.

## Dependencies and integration points
Includes `net_driver.h` for EF4 constants such as `EF4_TXQ_TYPES`, `EF4_MAX_CHANNELS`, and loopback mode bounds. `ef4_loopback_rx_packet` is called from the receive path when `efx->loopback_selftest` is active.

## Risks and test signals
Risk is mainly ABI/contract drift between result arrays and the number of channels, TX queue types, loopback modes, or PHY tests. Test signals are successful compilation across all self-test consumers and correctly bounded ethtool output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tenxpress.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tenxpress.c

## Purpose
Implements the SFX7101/TenXpress 10GBASE-T PHY driver for Falcon boards, including MDIO probing, PHY initialization, reset sequencing, loopback, low-power control, link polling, LED control, BIST, and ethtool link settings.

## Important APIs, types, and functions
- Exports `falcon_sfx7101_phy_ops` and `tenxpress_set_id_led`.
- Private state is `struct tenxpress_phy_data`, tracking previous loopback mode, PHY mode, and bad link-partner tries.
- Core operations: `tenxpress_phy_probe`, `tenxpress_phy_init`, `tenxpress_phy_reconfigure`, `tenxpress_phy_poll`, `sfx7101_phy_fini`, `tenxpress_phy_remove`, `sfx7101_run_tests`, `tenxpress_get_link_ksettings`, and `tenxpress_set_link_ksettings`.
- Hardware helpers: `tenxpress_init`, `tenxpress_special_reset`, `sfx7101_check_bad_lp`, `tenxpress_ext_loopback`, and `tenxpress_low_power`.

## Control flow
Probe allocates private state, advertises Clause 45 MDIO support, declares required MMDs, loopback modes, and default 10GBASE-T advertisement. Init delegates board PHY setup, waits for required MMD reset/check unless in special mode, initializes clocks and LEDs, reconfigures flow control/autoneg, waits briefly, and resets XAUI. Reconfigure skips off/special modes, performs a special reset when leaving non-normal modes or changing external loopback, applies low power and transmit-disable state, reconfigures MDIO PHY/autoneg, sets PHYXS loopback, and snapshots state. Poll reads link from PMA/PCS/PHYXS, forces 10G full duplex, reads pause state, and flags bad non-10G link partners through logging and red LED flashing.

## State and persistence behavior
The only persistent driver state is heap-allocated `efx->phy_data` and `efx->link_state`. Hardware state is held in MDIO registers for LEDs, power, autonegotiation, loopback, and reset status. Fini powers down the LNPGA and waits before board power removal.

## Dependencies and integration points
Depends on Linux delay/rtnetlink/seq/slab support and driver MDIO helpers from `mdio_10g.h`, board hooks from `falcon_board(efx)`, XAUI reset/stat control from Falcon NIC code, and ethtool link-ksettings helpers.

## Risks and test signals
Risks include reset sequences glitching XGMAC stats, races in autoneg status sampling, link-partner false positives, and LED override state not being restored after errors. Test signals include PHY alive test, offline BIST after special reset, stable link polling, autoneg advertisement/lpa reporting, loopback self-tests, LED behavior, and bad link-partner logs after `MAX_BAD_LP_TRIES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tenxpress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.c

## Purpose
Implements the Falcon EF4 transmit path: SKB DMA mapping or copy-buffer coalescing, descriptor production, hardware doorbell pushes, completion processing, Linux netdev queue flow control, traffic class setup, and TX queue lifecycle.

## Important APIs, types, and functions
- Public transmit entry points: `ef4_hard_start_xmit`, `ef4_enqueue_skb`, `ef4_xmit_done`, `ef4_setup_tc`, `ef4_init_tx_queue_core_txq`, `ef4_probe_tx_queue`, `ef4_init_tx_queue`, `ef4_fini_tx_queue`, and `ef4_remove_tx_queue`.
- Sizing API: `ef4_tx_max_skb_descs`.
- Internal helpers: `ef4_tx_get_copy_buffer`, `ef4_enqueue_skb_copy`, `ef4_tx_map_data`, `ef4_tx_map_chunk`, `ef4_enqueue_unwind`, `ef4_dequeue_buffer(s)`, and `ef4_tx_maybe_stop_queue`.

## Control flow
`ef4_hard_start_xmit` chooses a channel and TX queue type from SKB queue mapping and checksum state, then delegates to `ef4_enqueue_skb`. Enqueue copies short or small fragmented packets into per-queue copy-buffer pages, otherwise maps SKB head/frags for DMA and creates one or more NIC-limited descriptors. It updates BQL, pushes descriptors immediately unless `xmit_more` can batch them, and may push a partner queue to avoid watchdog stalls. Completion calls `ef4_xmit_done`, dequeues through the completion index, unmaps DMA, consumes SKBs, updates completion counters, wakes stopped queues when paired fill levels fall below the wake threshold, and records empty queue state.

## State and persistence behavior
Per-queue state includes software descriptor buffers, copy-buffer pages, insert/write/read counts, stale read/write snapshots, BQL state, queue stop/wake thresholds from `efx`, and stats such as `tx_packets`, `pkts_compl`, `bytes_compl`, `merge_events`, and `cb_packets`. DMA mappings are owned by the final descriptor for each mapped fragment. No durable persistence exists.

## Dependencies and integration points
Uses Linux PCI DMA, SKB fragments, BQL, netdev TX queues, traffic-control mqprio setup, cache/page helpers, and driver NIC operations `ef4_nic_probe_tx`, `ef4_nic_init_tx`, `ef4_nic_push_buffers`, and `ef4_nic_remove_tx`. Hardware workaround macros from `workarounds.h` affect descriptor bounds and minimum transmit size.

## Risks and test signals
Risks include DMA unwind leaks after partial mapping failure, queue stop/wake races, partner queue batching leaving descriptors unpushed, and spurious completions causing reset. Test signals are TX completion counters, BQL behavior, netdev watchdog absence, mqprio queue count changes, loopback self-test TX completion counts, DMA mapping error paths, and reset logs for `RESET_TYPE_TX_SKIP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.h

## Purpose
Declares internal EF4 transmit helpers related to descriptor length limiting and TSO enqueue support.

## Important APIs, types, and functions
- `ef4_tx_limit_len(struct ef4_tx_queue *, dma_addr_t, unsigned int)` lets NIC-specific code cap a DMA segment length, typically for page or hardware boundary constraints.
- `ef4_enqueue_skb_tso(struct ef4_tx_queue *, struct sk_buff *, bool *)` declares a TSO enqueue path, although the researched `tx.c` comments indicate current Falcon code no longer uses software TSO there.

## Control flow
No runtime control flow is implemented in this header. It provides cross-file declarations for TX implementation units and NIC-specific helpers.

## State and persistence behavior
No state is stored here.

## Dependencies and integration points
Includes `<linux/types.h>` and depends on EF4 TX queue and SKB types from including translation units. The declarations integrate TX data-path code with NIC descriptor constraints and any TSO implementation compiled elsewhere.

## Risks and test signals
Risks are declaration drift if the TSO implementation is removed or signatures change. Test signals are build coverage of all TX translation units and descriptor-boundary tests for `ef4_tx_limit_len` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/txc43128_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/txc43128_phy.c

## Purpose
Implements the Falcon driver for the TranSwitch/Mysticom TXC-43128 CX4 retimer PHY, including reset, BIST, default analog tuning, GPIO helpers, power management, loopback reconfiguration, polling, and ethtool operations.

## Important APIs, types, and functions
- Exports `falcon_txc_phy_ops`, `falcon_txc_set_gpio_val`, and `falcon_txc_set_gpio_dir`.
- Private state is `struct txc43128_data`, tracking bug-reset timer, PHY mode, and loopback mode.
- Core PHY operations: `txc43128_phy_probe`, `txc43128_phy_init`, `txc43128_phy_reconfigure`, `txc43128_phy_poll`, `txc43128_phy_fini`, `txc43128_phy_remove`, `txc43128_run_tests`, and `txc43128_get_link_ksettings`.
- Hardware helpers: `txc_reset_phy`, `txc_bist_one`, `txc_bist`, `txc_apply_defaults`, `txc_set_power`, `txc_reset_logic`, and lane power helpers.

## Control flow
Probe allocates private state, declares required MMDs and Clause 45 plus emulated Clause 22 support, and publishes supported loopbacks. Init resets the PMA/PMD MMD, checks required MMDs, runs BIST, and reapplies board and analog defaults. Reconfigure performs a full reset/default/XAUI reset when transmit-disabled mode changes, updates transmit-disable and MDIO PHY configuration, applies low-power lane settings, and runs a limited logic reset only when loopback or mode changes. Poll reads aggregate MDIO link state, sets fixed 10G full-duplex flow-control state, and periodically performs logic reset every five seconds while link remains down outside loopback.

## State and persistence behavior
Driver state lives in `efx->phy_data` and `efx->link_state`; hardware state persists in vendor MDIO registers for amplitude, preemphasis, LEDs, BIST, low power, and GPIO. Removal frees private state; fini disables LASI link events.

## Dependencies and integration points
Uses MDIO helpers, Falcon board initialization, Falcon XAUI reset, Linux delay/slab support, and ethtool link setting helpers. It participates in `selftest.c` through `run_tests` and `test_name`.

## Risks and test signals
Risks include infinite waiting if the BIST STOP bit never clears, repeated reset storms while link is down, incorrect analog defaults after reset, and missing cleanup of LASI/event state. Test signals include BIST lane frame/error counts, link polling transitions, five-second bug workaround resets, GPIO register reads/writes on board users, and offline ethtool test result `bist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/txc43128_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/workarounds.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/workarounds.h

## Purpose
Centralizes Falcon EF4 hardware workaround predicates, keyed by NIC revision or general 10G capability, so RX/TX/NIC code can gate erratum-specific behavior.

## Important APIs, types, and functions
- Revision predicates: `EF4_WORKAROUND_FALCON_A`, `EF4_WORKAROUND_FALCON_AB`, and `EF4_WORKAROUND_10G`.
- Named workaround macros include bug IDs 7884, 15592, 5129, 5391, 5583, 5676, 6555, 7244, 7803, and 8071.

## Control flow
No control flow is implemented here. Callers expand macros to conditional logic based on `ef4_nic_rev(efx)`.

## State and persistence behavior
No state is stored. Workaround decisions are derived from the NIC revision at runtime.

## Dependencies and integration points
Used by Falcon RX and TX paths and likely NIC-specific code to handle descriptor sizing, overlength RX recovery, TX minimum size, flush behavior, and other errata.

## Risks and test signals
Risk is incorrect revision gating, which can either miss required erratum handling or apply legacy behavior to newer chips. Test signals are hardware-revision-specific RX/TX stress tests, flush/reset tests, overlength RX handling, and descriptor alignment/page-boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/workarounds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/filter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/filter.h

## Purpose
Defines the generic SFC hardware filter specification used by RX/TX filtering, RFS steering, default unicast/multicast filters, virtual ports, and tunnel encapsulation matching.

## Important APIs, types, and functions
- Enums: `efx_filter_match_flags`, `efx_filter_priority`, `efx_filter_flags`, and `efx_encap_type`.
- Main data type: `struct efx_filter_spec`, a compact match/action target structure carrying priority, flags, queue ID, RSS context, vport ID, VLANs, MACs, EtherType, IP protocol, hosts, ports, and encap type.
- Initializers: `efx_filter_init_rx` and `efx_filter_init_tx`.
- Match setters: IPv4/IPv6 local/full helpers, Ethernet local/default unicast/default multicast helpers, vport setter, and encap type getter/setter.

## Control flow
All code is inline initialization and field-setting. Callers zero the spec through the init helpers, then OR match flags and set associated fields through typed setters. Invalid Ethernet local filters with neither VID nor MAC return `-EINVAL`.

## State and persistence behavior
Filter specs are caller-owned transient values submitted to NIC-specific filter tables. The header stores no global state and performs no hardware I/O.

## Dependencies and integration points
Depends on Linux Ethernet, IPv6 address, byte-order types, and is consumed by driver filter implementations plus Falcon RFS code. Encapsulation values connect legacy filter handling with EF100 tunnel offload capability checks.

## Risks and test signals
Risks include unsupported match flag combinations per NIC type, bitfield size limits (`match_flags`, `flags`, `dmaq_id`, `encap_type`), and host/network byte-order mistakes. Test signals include filter insertion/removal tests for IPv4, IPv6, MAC/VLAN, default UC/MC, vport, encap filters, and RFS steering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/fw_formats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/fw_formats.h

## Purpose
Defines firmware image header/trailer offsets, lengths, magic values, versions, CRC positions, and payload metadata for SFC/AMD firmware update formats recognized by the driver.

## Important APIs, types, and functions
- EF10 reflash header/trailer constants for magic, version, firmware type/subtype, payload size, header length, and trailer CRC.
- EF100 SmartNIC image constants for magic, version, header length, partition type/subtype, payload size, CRC, and minimum length.
- EF100 SmartNIC bundle constants for magic, version, bundle type/subtype, header length, CRC, and total fixed header length.

## Control flow
No executable control flow exists. Consumers use constants to scan firmware byte streams, identify candidate headers, and validate checksums before issuing firmware update operations.

## State and persistence behavior
No state is stored. The constants describe on-disk or in-memory firmware blob layouts.

## Dependencies and integration points
Designed for firmware update parsing code in the SFC driver. Comments explain that recognition must validate checksum fields because magic values are at differing offsets and signed/package headers may prepend data.

## Risks and test signals
Risks include stale offsets relative to firmware packaging changes, false-positive header detection if CRC validation is incomplete, and endian/length mistakes. Test signals are firmware parser unit tests with EF10 reflash, EF100 image, EF100 bundle, signed/prepended payloads, bad CRC, bad version, and truncated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/fw_formats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/io.h

## Purpose
Provides low-level MMIO register access helpers for SFC NICs, including 32-bit and 128-bit CSR reads/writes, table access, page-mapped VI register access, architecture-specific 64-bit I/O, and PIO capability selection.

## Important APIs, types, and functions
- Raw helpers: `_efx_writed`, `_efx_readd`, and optional `_efx_writeq`/`_efx_readq`.
- CSR helpers: `efx_writeo`, `efx_writed`, `efx_reado`, `efx_readd`, `efx_writeo_table`, and `efx_reado_table`.
- VI/page helpers: `efx_paged_reg`, `efx_writeo_page`, and `efx_writed_page`.
- Constants: `EFX_DEFAULT_VI_STRIDE` and `EF100_DEFAULT_VI_STRIDE`.

## Control flow
The helpers calculate offsets from `efx->membase`, `efx->reg_base`, and `efx->vi_stride`, emit verbose hardware traces, and use `efx->biu_lock` around normal 128-bit CSR accesses. Page-mapped write macros use `BUILD_BUG_ON_ZERO` to restrict allowed registers at compile time.

## State and persistence behavior
No persistent state is owned here. The helpers mutate device MMIO state and rely on `efx->biu_lock`, register base, memory base, and VI stride stored in the NIC structure.

## Dependencies and integration points
Depends on Linux `io.h` and spinlocks plus SFC register word types/macros. It is foundational for NIC register programming, descriptor doorbells, event queue pointers, and SRAM/CSR access across EF10/EF100 code.

## Risks and test signals
Risks include incorrect locking around latching 128-bit registers, architecture-specific write-combining assumptions, raw I/O ordering surprises, and invalid page register offsets. Test signals are register read/write smoke tests, descriptor doorbell operation, lockdep coverage, compile-time macro failures for invalid page registers, and platform coverage on 32-bit vs 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.c

## Purpose
Implements the EF100 Match-Action Engine MCDI interface for mports, counter streams, firmware table descriptors, capability validation, counters, encapsulation metadata, pedit MAC resources, action sets/lists, outer/action rules, conntrack table entries, and MAE init/fini.

## Important APIs, types, and functions
- Mport APIs: allocation/free, selector construction, firmware lookup, rhashtable enumeration, local VF lookup, and `efx_mae_remove_mport`.
- Counter APIs: `efx_mae_start_counters`, `efx_mae_stop_counters`, `efx_mae_counters_grant_credits`, counter allocate/free.
- Capability/table APIs: `efx_mae_get_tables`, `efx_mae_free_tables`, `efx_mae_get_caps`, match/encap capability checks, table descriptor hooks.
- Resource APIs: encap header allocate/update/free, pedit MAC allocate/free, action set/list allocate/free.
- Rule APIs: encap match register/unregister, LHS rule insert/remove, CT insert/remove, action rule insert/update/delete.
- Lifecycle: `efx_init_mae` and `efx_fini_mae`.

## Control flow
Most public operations build fixed or variable MCDI buffers, populate protocol fields, call `efx_mcdi_rpc`, validate output lengths, store firmware IDs, and verify returned IDs on free/delete. Startup allocates an `efx_mae`, initializes an mport rhashtable, and later enumerates mports from the firmware journal. Capability discovery reads base MAE caps and AR/OR field flags; match checks classify masks as zero, all-ones, prefix, or arbitrary and reject masks unsupported by firmware. Rule insertion populates either outer-rule or action-rule match criteria, assigns action-set or action-set-list responses, and stores returned firmware IDs. Conntrack support first discovers and hooks table descriptors, then packs key/response rows according to firmware-provided field positions before table insert/delete.

## State and persistence behavior
Driver state lives in `efx->mae`, `efx->mae->mports_ht`, `efx->tc->caps`, `efx->tc->meta_ct`, counter flush generations, RX queue credit counters, and firmware IDs stored in TC objects. Hardware/firmware owns allocated mports, counters, encap headers, MAC address entries, action sets, action set lists, outer rules, action rules, and table rows until explicit free/delete calls. Many free paths clear local IDs after successful deletion to reduce stale-ID reuse.

## Dependencies and integration points
Depends on `ef100_nic.h`, MAE and MCDI protocol headers, TC offload objects, tunnel encap action objects, conntrack objects, rhashtable, devlink port descriptors, wait queues, and RX queues for counter streaming. It is the firmware boundary for TC flower/conntrack/tunnel offload on EF100.

## Risks and test signals
High-risk areas are firmware ABI length checks, resource lifetime rollback after partial allocation, ID namespace confusion between AS and ASL high-bit encodings, CT table packing from dynamic descriptors, counter stream drain timeouts, and mport journal duplicate handling. The encap match population should be reviewed carefully because the code writes the L4 destination-port field for both destination and source UDP port values, which may be intentional protocol aliasing or a field-name bug. Test signals include TC offload add/update/delete, tunnel encap/decap, counter packet drain and credit behavior, conntrack insert/delete for IPv4 and IPv6, firmware ID mismatch warnings, unsupported mask extack messages, and unload with all resources freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.h

## Purpose
Declares the EF100 MAE driver interface used by TC offload, counter streaming, mport management, conntrack offload, and MAE lifecycle code.

## Important APIs, types, and functions
- Public mport APIs and `struct mae_mport_desc`, including net-port, alias, and VNIC descriptors plus rhashtable linkage and devlink port storage.
- `struct efx_mae` owns the NIC pointer and mport rhashtable.
- Counter stream APIs, table/capability APIs, match capability validators, counter resource APIs, encap metadata APIs, pedit MAC APIs, action set/list APIs, encap match APIs, LHS rule APIs, CT APIs, action rule APIs, and lifecycle APIs.
- `struct mae_caps` stores match field count, supported encap types, action priorities, and per-field AR/OR support arrays.

## Control flow
The header has no executable flow. It defines the call graph boundary between TC/offload code and the MAE MCDI implementation in `mae.c`.

## State and persistence behavior
Types declared here describe in-memory MAE state and firmware-backed resource identifiers. Runtime ownership is implemented in `mae.c`; the header itself does not allocate or free state.

## Dependencies and integration points
Includes devlink, core net driver definitions, TC definitions, and `mcdi_pcol.h` for firmware NULL constants. It is consumed by EF100 NIC initialization, TC offload, conntrack, counter RX, and cleanup paths.

## Risks and test signals
The header contains two declarations named `efx_mae_lookup_mport` with identical C types but different parameter names/semantics (`selector` near the top and `vf` near the bottom), while `mae.c` separately implements `efx_mae_fw_lookup_mport` for selector lookup. This is legal but confusing and is a contract-drift risk. Test signals are build coverage, sparse/prototype checks, MAE init/enumeration, VF mport lookup, and TC offload resource operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae_counter_format.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae_counter_format.h

## Purpose
Defines the version 2 EF100 MAE counter packet layout used to parse streamed action-rule, conntrack, and outer-rule counter updates.

## Important APIs, types, and functions
- Header word constants define a 160-bit header with version, identifier, header/payload offsets, index, count, and reserved fields.
- Payload word constants define a 128-bit entry with counter index, packet count, and byte count.
- Identifier values distinguish AR, CT, and OR counter packet types.

## Control flow
No executable code is present. Consumers use bit offsets, widths, byte offsets, and sizes to extract counter stream fields from RX packet data.

## State and persistence behavior
No state is stored. The constants describe wire-format packet contents delivered by firmware/hardware.

## Dependencies and integration points
Integrated with MAE counter streaming in `mae.c` and RX-side counter packet parsing elsewhere in the driver. The version constant must match firmware output from `MC_CMD_MAE_COUNTERS_STREAM_START`.

## Risks and test signals
Risks include format drift with firmware, incorrect 48-bit counter extraction, endian mistakes, or accepting unknown identifiers/versions. Test signals are parser tests with AR/CT/OR samples, wrap/large 48-bit counts, malformed offsets/counts, and mixed counter stream packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae_counter_format.h -->
