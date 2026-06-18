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
