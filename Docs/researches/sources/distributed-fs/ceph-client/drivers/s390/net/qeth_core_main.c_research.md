# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_main.c

## Purpose

`qeth_core_main.c` implements the shared core of the s390 qeth network driver. It owns module initialization, CCW/CCWGROUP registration, card allocation/removal, online/offline and recovery sequencing, MPC/IPA control-command transport, QDIO queue setup and teardown, RX/TX data paths, feature negotiation, ioctl handling, debug infrastructure, and exported services used by the qeth layer 2 and layer 3 discipline modules.

## Important APIs and functions

- Module and bus registration: `qeth_core_init()`, `qeth_core_exit()`, `qeth_ccw_driver`, `qeth_core_ccwgroup_driver`, and the `qeth_ids` table register the qeth CCW device IDs and grouped three-device model.
- Card lifecycle: `qeth_core_probe_device()`, `qeth_core_remove_device()`, `qeth_alloc_card()`, `qeth_core_free_card()`, `qeth_setup_card()`, `qeth_alloc_netdev()`, `qeth_clone_netdev()`, `qeth_core_set_online()`, and `qeth_core_set_offline()`.
- Discipline management: `qeth_setup_discipline()` and `qeth_remove_discipline()` load/use `qeth_l2_discipline` or `qeth_l3_discipline` symbols and call the discipline setup/remove hooks.
- Channel and command transport: `qeth_start_channel()`, `qeth_stop_channel()`, `qeth_clear_channel()`, `qeth_halt_channel()`, `qeth_irq()`, `qeth_alloc_cmd()`, `qeth_send_control_data()`, `qeth_issue_next_read()`, and `qeth_issue_next_read_cb()`.
- MPC initialization: `qeth_idx_init()`, `qeth_idx_activate_read_channel()`, `qeth_idx_activate_write_channel()`, `qeth_cm_enable()`, `qeth_cm_setup()`, `qeth_ulp_enable()`, `qeth_ulp_setup()`, `qeth_dm_act()`, and `qeth_mpc_initialize()`.
- IPA helpers: `qeth_ipa_alloc_cmd()`, `qeth_send_ipa_cmd()`, `qeth_get_adapter_cmd()`, `qeth_get_setassparms_cmd()`, `qeth_send_simple_setassparms_prot()`, `qeth_get_diag_cmd()`, `qeth_query_ipassists()`, `qeth_query_setadapterparms()`, and `qeth_query_setdiagass()`.
- QDIO setup: `qeth_alloc_qdio_queues()`, `qeth_free_qdio_queues()`, `qeth_qdio_establish()`, `qeth_qdio_activate()`, `qeth_init_qdio_queues()`, `qeth_alloc_buffer_pool()`, `qeth_resize_buffer_pool()`, and completion-queue helpers.
- TX data path: `qeth_xmit()`, `qeth_add_hw_header()`, `qeth_fill_buffer()`, `__qeth_xmit()` for IQD, `qeth_do_send_packet()` for non-IQD packing, `qeth_flush_buffers()`, `qeth_tx_poll()`, `qeth_iqd_tx_complete()`, and `qeth_tx_timeout()`.
- RX data path: `qeth_poll()`, `qeth_rx_poll()`, `qeth_extract_skb()`, `qeth_extract_skbs()`, `qeth_l3_rebuild_skb()`, `qeth_receive_skb()`, and `qeth_rx_refill_queue()`.
- Feature/control APIs: `qeth_set_features()`, `qeth_fix_features()`, `qeth_features_check()`, `qeth_enable_hw_features()`, `qeth_setadp_promisc_mode()`, `qeth_setadpparms_change_macaddr()`, `qeth_setadpparms_set_access_ctrl()`, `qeth_hw_trap()`, `qeth_query_switch_attributes()`, `qeth_vm_request_mac()`, and `qeth_get_stats64()`.

## Control flow

Probe starts when the CCWGROUP driver receives a three-device group. `qeth_core_probe_device()` allocates `struct qeth_card`, creates debugfs/debug entries, initializes locks/workqueues/options, allocates a netdev and inbound QDIO queue, reads device capabilities, and enforces an L2/L3 discipline when the hardware or VM NIC mode requires one.

Bringing a card online flows through `qeth_core_set_online()` and `qeth_set_online()`. If no discipline is attached, a default is selected (`L3` for IQD, `L2` otherwise). `qeth_hardsetup_card()` performs the hardware sequence: clear old QDIO/channel state, start read/write/data channels, determine capabilities and CCW config, initialize sequence numbers/tokens, activate read/write IDX channels, run MPC CM/ULP setup, allocate/establish/activate QDIO, send STARTLAN, query IP assists and adapter parameters, arm diagnostics, apply isolation, initialize link info, and seed QDIO input/output queues. The discipline’s `set_online()` hook then registers/activates the netdev-facing behavior.

Control commands use a two-channel pattern. Writes are sent on the write or data channel with a `qeth_cmd_buffer`; reads are kept continuously outstanding on the read channel. `qeth_irq()` completes CCWs, handles channel status and unit-check conditions, retries CC1 starts, invokes command callbacks, and schedules recovery on unrecoverable conditions. `qeth_issue_next_read_cb()` validates IDX frames, parses IPA replies, dispatches unsolicited IPA events, matches replies to `cmd_waiter_list`, and reissues the next read.

The TX path starts in layer-specific code, which builds protocol headers through a callback into `qeth_xmit()`. The core ensures headroom, places or allocates a qeth hardware header, counts SBAL elements, linearizes oversized fragmented SKBs if possible, fills QDIO buffer elements, stops/wakes netdev queues on full conditions, and rings QDIO. IQD uses bulk/coalescing and optional QAOB completion tracking; OSA-style queues use packing mode controlled by low/high watermarks and PCI requests.

The RX path is NAPI-driven. `qeth_poll()` inspects QDIO input buffers, calls `qeth_extract_skb()` repeatedly until budget or buffer end, rebuilds L3 Ethernet headers when needed, marks checksum state, passes packets to GRO, returns consumed pages to the pool, refills input buffers at a threshold, polls completion queues, and restarts QDIO IRQs when NAPI completes.

Recovery is scheduled via `qeth_schedule_recovery()`, which starts `qeth_do_reset()` through a work item and kthread. Recovery takes the current discipline offline, attempts online setup again, and if that fails sets the CCWGROUP offline.

## State and persistence behavior

State is runtime-only. The driver rebuilds card tokens, sequence numbers, QDIO queues, negotiated capabilities, local-address hashes, link data, feature state, and debugfs state after probe or recovery. No file-backed persistence is implemented.

Key state is held in `struct qeth_card`: channel state, qdio state, command waiters, tokens, sequence numbers, local address hash tables, capability bitmasks, discipline pointer, workqueues, thread masks, netdev pointer, statistics, diagnostic flags, and link information. QDIO ownership is tracked through atomics on queue and buffer state. Command lifetime is protected by refcounts and completions. Online/offline transitions are serialized by `conf_mutex`; discipline changes by `discipline_mutex`; module symbol loading by `qeth_mod_mutex`; command queues and local address tables by spinlocks; local-address lookups by RCU.

## Dependencies and integration points

The file integrates with Linux module infrastructure, CCW and CCWGROUP buses, QDIO allocation/establish/activate/shutdown APIs, NAPI, netdev features and stats, debugfs, the s390 debug feature, service-level reporting, s390 diagnostics (`diag26c`, `stsi`, `cpcmd`), ethtool operations, MII ioctl emulation, user-copy ioctl handlers for SNMP/OAT, IUCV TX notification, VLAN/GRO/checksum/GSO helpers, and the `qeth_l2`/`qeth_l3` discipline modules.

It depends on `qeth_core.h` for shared state and `qeth_core_mpc.h`/`qeth_core_mpc.c` for protocol templates, packed IPA/MPC layouts, command codes, offsets, and return-code strings.

## Risks and edge cases

- The online path is a long hardware negotiation sequence with retries only around selected channel/IDX failures; partial setup requires careful unwind of QDIO queues, channels, reads, and buffer pools.
- IRQ, callback, and waiter interactions are sensitive. Late replies can race with timeout/cancel paths, so the `iob->lock`, refcount, and `iob->rc` checks are critical.
- RX parsing trusts qeth headers for packet lengths but must walk SBAL element boundaries correctly. Bad lengths can otherwise leak SKBs, overrun elements, or desynchronize buffer processing.
- TX header placement has alignment/page-boundary constraints. Incorrect element counts or header-cache cleanup can cause QDIO mapping corruption or leaks.
- IQD QAOB handling creates a pending-buffer path where the queue slot is replaced before final completion; allocation failure or state mismatch triggers recovery.
- Feature changes perform hardware IPA sequences. Partial failure intentionally mutates `dev->features` back, so callers and tests must verify rollback behavior.
- Local-address caches gate offload eligibility. Missed register/unregister events can leave checksum/TSO enabled for local next-hop traffic that hardware cannot handle.
- Several paths copy variable-length user data for SNMP and OAT. The code bounds request sizes and response buffers, but these are high-value fuzz targets.

## Test signals

Validation should include build coverage for qeth core with L2/L3 modules, module load/unload, CCWGROUP group creation/removal, online/offline for IQD and OSD-style devices, recovery from simulated IRQ/QDIO/channel errors, STARTLAN offline/restore events, IPA timeout recovery, checksum and TSO enable/disable including rollback, MTU negotiation and IQD RX buffer resizing, RX GRO with linear and fragmented packets, L3 header rebuild, TX packing and IQD bulk/coalescing, completion queue QAOB pending/done paths, SNMP/OAT ioctl bounds, VM NIC MAC/layer detection, and stats/debugfs output.
