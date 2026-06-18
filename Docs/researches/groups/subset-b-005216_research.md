# subset-b-005216 research

Grouped research for the s390 qeth core files. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core.h

## Purpose

`qeth_core.h` is the shared internal interface for the IBM s390 qeth network driver core and its layer-specific discipline modules. It defines the central device model (`struct qeth_card`), QDIO queue/buffer objects, control-command wrappers, card/channel state machines, network-header formats, capability state, and exported helper APIs used by `qeth_core_main.c`, `qeth_l2`, `qeth_l3`, ethtool, sysfs, and ioctl-facing code.

## Important APIs, types, and constants

- Debug infrastructure: `enum qeth_dbf_names`, `struct qeth_dbf_info`, `QETH_DBF_*`, and `QETH_CARD_*` macros wrap the s390 debug feature and per-card debug areas.
- Device/channel identity macros: `CARD_RDEV`, `CARD_WDEV`, `CARD_DDEV`, `CARD_BUS_ID`, and `CARD_DEVID` normalize access to the grouped read/write/data CCW devices.
- Wire and queue sizing constants: `QETH_BUFSIZE`, `QETH_MAX_OUT_QUEUES`, `QETH_MAX_IN_QUEUES`, `QETH_IN_BUF_*`, `QETH_TX_TIMEOUT`, `QETH_RCD_TIMEOUT`, and packing watermarks define hard limits used during allocation and transmit scheduling.
- Hardware headers: `struct qeth_hdr_layer2`, `struct qeth_hdr_layer3`, `struct qeth_hdr`, `struct qeth_hdr_tso`, header IDs, cast flags, VLAN/checksum flags, and TSO extension fields describe the qeth-specific per-packet prefix used on QDIO buffers.
- QDIO data model: `struct qeth_qdio_q`, `struct qeth_qdio_buffer_pool`, `struct qeth_qdio_buffer`, `struct qeth_qdio_out_buffer`, `struct qeth_qdio_out_q`, and `struct qeth_qdio_info` model inbound buffer pools, outbound SBALs, completion queue state, packing, coalescing, and per-queue statistics.
- Control command model: `struct qeth_channel`, `struct qeth_cmd_buffer`, and `struct qeth_reply` represent CCW-backed control commands, matching, callbacks, refcounting, and command completion.
- Card state: `enum qeth_channel_states`, `enum qeth_card_states`, `struct qeth_card_info`, `struct qeth_card_options`, `struct qeth_priv`, and `struct qeth_card` hold the long-lived runtime configuration and negotiated capabilities.
- Discipline interface: `struct qeth_discipline` provides `setup`, `remove`, `set_online`, `set_offline`, and `control_event_handler` hooks implemented by layer 2 and layer 3 modules.
- Exported APIs include `qeth_setup_discipline()`, `qeth_set_offline()`, `qeth_send_ipa_cmd()`, `qeth_ipa_alloc_cmd()`, `qeth_get_setassparms_cmd()`, `qeth_get_diag_cmd()`, `qeth_poll()`, `qeth_xmit()`, `qeth_open()`, `qeth_stop()`, feature-management helpers, queue-selection helpers, ioctl helpers, and card-info/query helpers.

## Control flow and integration

The header is arranged around the qeth lifecycle. Probe code allocates a `qeth_card`, initializes its `qeth_qdio_info`, attaches a layer discipline, and later moves the card online. Online setup negotiates MPC/IPA state and QDIO queues, after which the netdev operations call into `qeth_open()`, `qeth_xmit()`, `qeth_poll()`, and `qeth_stop()`. Control commands are allocated as `qeth_cmd_buffer` objects, finalized into CCWs, sent on a `qeth_channel`, matched against replies, and completed through `struct qeth_reply`.

The layer-specific modules are expected to consume this API rather than duplicate core behavior. They provide protocol-specific header filling for `qeth_xmit()`, handle selected unsolicited IPA events through `control_event_handler`, and call the exported IPA/SETASSPARMS helpers to program IPs, MACs, VLANs, routing, and offloads.

## State and persistence behavior

All state in this header is runtime kernel state. There is no disk persistence. Persistent-looking fields, such as IP assist capabilities, bridgeport/VNICC settings, local-address caches, queue sizes, offload flags, tokens, and sequence numbers, live in `struct qeth_card` and are rebuilt during probe, online setup, recovery, or feature re-enable.

The main state machines are:

- Channel state: `CH_STATE_DOWN`, `CH_STATE_UP`, `CH_STATE_HALTED`, `CH_STATE_STOPPED`.
- Card state: `CARD_STATE_DOWN` and `CARD_STATE_SOFTSETUP`.
- QDIO state: `QETH_QDIO_UNINITIALIZED`, `QETH_QDIO_ALLOCATED`, `QETH_QDIO_ESTABLISHED`, and `QETH_QDIO_CLEANING`.
- Output buffer state: driver-owned `QETH_QDIO_BUF_EMPTY` versus hardware-owned `QETH_QDIO_BUF_PRIMED`.
- QAOB state: `QETH_QAOB_ISSUED`, `QETH_QAOB_PENDING`, and `QETH_QAOB_DONE` for IQD completion queue handling.

Synchronization is explicit: spinlocks guard command lists, thread masks, and local-address hash updates; mutexes guard configuration, discipline changes, and bridgeport configuration; RCU protects local-address lookups from transmit feature checks; refcounts keep command buffers alive across IRQ callbacks and waiters.

## Dependencies and integration points

This file depends heavily on Linux networking (`net_device`, `sk_buff`, IPv4/IPv6 routing helpers, VLAN helpers, NAPI, ethtool, traffic classes), s390 channel I/O (`ccw_device`, `ccwgroup_device`, `qdio`, debug feature, STSI/diag structures), and qeth MPC protocol definitions from `qeth_core_mpc.h`.

Important external integration points are the CCW/CCWGROUP bus, QDIO queues, NAPI, netdev feature negotiation, debugfs, the s390 debug facility, IUCV TX notifications, and module symbols from `qeth_l2`/`qeth_l3`.

## Risks and edge cases

- Many structures mirror hardware wire formats and QDIO descriptors, so packing, alignment, endian, and offset assumptions are high risk.
- Command lifetime is callback/refcount based. Missed `qeth_get_cmd()` or `qeth_put_cmd()` pairing would cause use-after-free or leaks.
- RX/TX buffer ownership crosses driver, QDIO, and hardware boundaries; incorrect state transitions can corrupt SBAL reuse or leak SKBs/pages.
- `qeth_dst_check_rcu()`, local-address lookup, and offload restriction checks require correct RCU context.
- The header exposes a broad internal API to multiple modules, so changes to `struct qeth_card`, `struct qeth_discipline`, or exported helpers can break layer-specific drivers.
- Queue-count helpers encode IQD multicast queue translation and traffic-class assumptions that must stay consistent with `qeth_core_main.c`.

## Test signals

Useful validation signals include successful qeth module load/unload, CCWGROUP probe/remove, online/offline transitions for OSD/IQD/OSM devices, recovery after forced channel or QDIO errors, NAPI RX/TX operation, queue-count changes, IQD multicast/unicast queue selection, checksum/TSO feature toggles, local-address registration events, and debugfs `local_addrs` output. Static build coverage should include configurations with and without `CONFIG_QETH_L3` and `CONFIG_QETH_OSX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.c

## Purpose

`qeth_core_mpc.c` supplies static MPC/IPA protocol templates and human-readable IPA diagnostics for the qeth core. It is data-oriented: immutable byte arrays provide the base frames for IDX activation, CM enable/setup, ULP enable/setup, DM activation, and IPA PDU headers; lookup tables map IPA command/return-code pairs to stable messages used by debug logging.

## Important APIs and data

- Exported command templates: `IDX_ACTIVATE_READ`, `IDX_ACTIVATE_WRITE`, `CM_ENABLE`, `CM_SETUP`, `ULP_ENABLE`, `ULP_SETUP`, `DM_ACT`, and `IPA_PDU_HEADER`.
- Return-code message tables: default IPA messages plus command-specific maps for adapter parameters, diagnostic assist, create/destroy address, VNICC, bridgeport IQD/OSA, MAC operations, IP/multicast operations, LAN state, VLAN, and routing.
- `qeth_get_ipa_msg(enum qeth_ipa_cmds cmd, enum qeth_ipa_return_codes rc)` first checks the command-specific table, then falls back to the default table, and finally returns the default unknown-error string.
- `qeth_get_ipa_cmd_name(enum qeth_ipa_cmds cmd)` maps IPA command numbers to compact names used in debug output.

## Control flow and integration

The byte-array templates are copied by `qeth_core_main.c` into command buffers and then patched with runtime tokens, device addresses, sequence numbers, protocol types, lengths, and port numbers before the CCW is issued. The return-code helpers are called when IPA replies arrive, especially through `qeth_issue_ipa_msg()`, so hardware status can be logged as meaningful text rather than raw numeric codes.

This file has no complex runtime control flow beyond table lookup. The message mapping order matters: command-specific meanings override generic return-code meanings, because some numeric return codes are reused by different IPA command families.

## State and persistence behavior

There is no mutable persistent state. All templates and lookup tables are static constants in kernel text/rodata. Runtime state is created elsewhere by copying and patching these templates into `struct qeth_cmd_buffer` instances.

## Dependencies and integration points

The file includes `linux/module.h`, `asm/cio.h`, and `qeth_core_mpc.h`. Its constants are consumed by the MPC and IPA setup paths in `qeth_core_main.c`; its string helpers support qeth debug facility logging. The contents must stay synchronized with the packed structures, offsets, sizes, and enum values in `qeth_core_mpc.h`.

## Risks and edge cases

- The templates are opaque hardware frames. A single byte, size constant, or offset mismatch can break device bring-up.
- Return-code values are reused across command families; placing a code in the wrong table can produce misleading diagnostics.
- `qeth_get_ipa_cmd_name()` depends on the final `IPA_CMD_UNKNOWN` entry as fallback by iterating to `ARRAY_SIZE(...) - 1`.
- Adding a new IPA command in the header without updating the command-name or return-code map reduces observability and can hide hardware-specific failures.

## Test signals

Relevant signals include successful MPC initialization through all template-backed commands, correct debug messages for known and unknown IPA return codes, command-name fallback for unknown commands, and compile-time consistency with `qeth_core_mpc.h` enum names and template size macros. Hardware or emulator tests that exercise negative IPA replies are especially useful because they validate command-specific message precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.h

## Purpose

`qeth_core_mpc.h` defines the qeth MPC and IPA protocol contract. It provides command codes, return codes, feature bits, packed request/reply structures, protocol constants, byte-offset macros into MPC frames, and declarations for the immutable command templates implemented in `qeth_core_mpc.c`. It is the wire-format authority used by the qeth core and layer-specific modules.

## Important APIs, types, and constants

- Template declarations and sizes: `IPA_PDU_HEADER`, `CM_ENABLE`, `CM_SETUP`, `ULP_ENABLE`, `ULP_SETUP`, `DM_ACT`, `IDX_ACTIVATE_READ`, `IDX_ACTIVATE_WRITE`, and their `*_SIZE` constants.
- Offset macros: `QETH_IPA_PDU_LEN_*`, `QETH_IPA_CMD_DEST_ADDR`, `QETH_*_TOKEN`, `QETH_*_RESP_*`, `QETH_TRANSPORT_HEADER_SEQ_NO`, `QETH_PDU_HEADER_SEQ_NO`, and IDX activation accessors are used to patch or parse raw MPC buffers.
- Capability representation: `struct qeth_ipa_caps` and helpers `qeth_ipa_caps_supported()`, `qeth_ipa_caps_enabled()`, `qeth_adp_supported()`, `qeth_is_supported()`, `qeth_is_supported6()`, and `qeth_is_ipafunc_supported()`.
- Hardware/device enums: `enum qeth_card_types`, link types, routing types, IPA commands, IPA return codes, IPA assist flags, adapter-parameter commands, MAC/address ops, isolation modes, card-info values, diagnostic-assist commands, VNICC flags/commands, bridgeport commands, and address-change event codes.
- Packed IPA structures: SET/DEL IP and multicast payloads, L2 MAC/VLAN commands, SETASSPARMS, SETADAPTERPARMS, SNMP, QUERY OAT, QUERY CARD INFO, QUERY SWITCH ATTRIBUTES, diagnostic assist, VNICC, SETBRIDGEPORT, address-change notification, local-address notifications, and top-level `struct qeth_ipa_cmd`.
- Parser helpers: `IS_IPA_REPLY`, `PDU_ENCAPSULATION(buffer)`, and `IS_IPA(buffer)`.
- Diagnostic APIs: `qeth_get_ipa_msg()` and `qeth_get_ipa_cmd_name()` are declared here and implemented in `qeth_core_mpc.c`.

## Control flow and integration

The header is consumed in two directions. For outbound commands, `qeth_core_main.c` allocates a command buffer, copies a template, uses offset macros to patch tokens/lengths/protocol information, then overlays `struct qeth_ipa_cmd` payloads for IPA commands. For inbound data, the read callback uses `IS_IPA()` and `PDU_ENCAPSULATION()` to locate the IPA command inside a raw MPC buffer, then interprets the packed union according to `hdr.command` and `hdr.prot_version`.

Layer-specific qeth code also relies on these definitions for IP/MAC/VLAN/routing operations, offload negotiation, bridgeport/VNICC management, and event handling. The `SETASS_DATA_SIZEOF`, `SETADP_DATA_SIZEOF`, `VNICC_DATA_SIZEOF`, `SBP_DATA_SIZEOF`, and `IPA_DATA_SIZEOF` macros help callers size IPA payloads without open-coding union offsets.

## State and persistence behavior

The file defines protocol data shapes, not live state. Mutable capability and feature state is stored by callers in `struct qeth_card_options` and `struct qeth_card_info`; command instances live in transient `qeth_cmd_buffer` allocations. There is no persistence outside the active kernel driver instance and hardware state negotiated through IPA commands.

## Dependencies and integration points

This header depends on s390 qeth UAPI types from `asm/qeth.h`, Ethernet constants from `uapi/linux/if_ether.h`, IPv6 address structures, and compiler packing/offset helpers. It must remain consistent with the actual IBM OSA/IQD MPC and IPA hardware protocol, `qeth_core_mpc.c` templates, and all call sites that cast raw bytes to these packed structures.

## Risks and edge cases

- Most structures are `packed` wire layouts. Reordering fields, changing types, or removing packing can silently break hardware protocol compatibility.
- Offset macros perform byte arithmetic on raw buffers. They assume the template layout and response encapsulation remain fixed.
- `PDU_ENCAPSULATION()` and `IS_IPA()` use raw offsets from a buffer; callers must only use them with sufficiently sized MPC frames.
- Numeric return codes are reused across command families; interpretation requires both command and return code.
- Feature flags distinguish IPv4, IPv6, adapter, VNICC, and bridgeport capabilities. Mixing supported and enabled masks can lead to advertising unavailable netdev features.
- Conditional `IS_OSX()` depends on `CONFIG_QETH_OSX`, so code must compile and behave correctly when OSX support is disabled.

## Test signals

Tests should cover compile-time structure sizes/offsets where possible, successful construction of IPA SETASSPARMS/SETADAPTERPARMS/DIAG/VNICC/SBP payloads, parsing of IPA replies and unsolicited events, fallback behavior for unknown command names and return-code messages, feature negotiation for IPv4/IPv6 assists, bridgeport and VNICC command sizing, and configurations with `CONFIG_QETH_OSX` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.h -->
