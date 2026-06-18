# Research: subset-b-005936

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/mgmt.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/mgmt.h

## Purpose
This header is the kernel/userspace Bluetooth management protocol contract used by BlueZ management sockets. It defines the common management packet header, status codes, controller indices, command opcodes, event opcodes, packed command parameter and response records, fixed payload size constants, and feature/setting bit masks. It is ABI-like: layout, endian annotations, packing, and flexible-array tails must stay stable because implementation code in `net/bluetooth/mgmt.c` and management clients serialize these records directly.

## Important APIs, Types, And Constants
- `struct mgmt_hdr` is the outer wire header with little-endian `opcode`, controller `index`, and payload `len`.
- `struct mgmt_tlv` and `struct mgmt_tlv_hdr` define typed variable-length configuration elements and include a `static_assert` protecting the flexible payload offset.
- `struct mgmt_addr_info` is the common Bluetooth address plus address-type tuple reused by connection, pairing, discovery, key, device-flag, and mesh commands.
- `MGMT_STATUS_*` constants are command status values returned in command-complete/status events.
- `MGMT_SETTING_*` and `MGMT_PHY_*` bit masks report and configure controller capabilities and selected PHYs.
- `MGMT_OP_*` command definitions cover controller discovery, power/connectability/discoverability, class/name/UUID management, BR/EDR and LE key loading, pairing replies, OOB data, discovery, blocked devices, identity configuration, advertising, PHY configuration, experimental features, default config TLVs, device flags, advertisement monitors, mesh receiver/send, and synchronized HCI command execution.
- `MGMT_EV_*` event definitions cover command completion/status, controller add/remove/error, setting/name/class changes, key notifications, connection and pairing prompts, discovery, device block/unblock/unpair/add/remove, connection parameters, extended index/config/OOB/advertising/PHY/experimental changes, suspend/resume, advertisement monitor reports, and mesh events.

## Control Flow And State
The file itself has no executable control flow; it defines the on-wire state transitions consumed by the Bluetooth management implementation. A command is received as `mgmt_hdr`, decoded by `opcode`, validated against the matching `MGMT_*_SIZE` constant or flexible-array length, then answered through `MGMT_EV_CMD_COMPLETE` or `MGMT_EV_CMD_STATUS`. Long-running procedures such as discovery, pairing, advertising, mesh send, and monitor registration subsequently produce asynchronous `MGMT_EV_*` records. Controller state is represented by `supported_settings`, `current_settings`, selected PHY masks, advertising instance lists, monitor handles, controller indices, and per-device flags.

## State And Persistence Behavior
The records describe persistent and runtime state but do not store it. Persistent inputs include loaded BR/EDR link keys, LE LTKs, IRKs, blocked keys, configured identity/public/static addresses, device flags, and default system/runtime configuration TLVs. Runtime state includes powered/connectable/discoverable modes, advertising instances, discovery state, monitor handles, mesh handles, pending authentication prompts, controller suspend/resume data, and connection telemetry. All multi-byte values are explicitly little-endian and most structs are `__packed`, so padding cannot be relied on for forward compatibility.

## Dependencies And Integration Points
The header depends on Bluetooth core types such as `bdaddr_t`, HCI name length and advertising length constants, Linux integer/endian types, `BIT()`, `__packed`, `__counted_by`, and `__struct_group`. It integrates with `net/bluetooth/mgmt.c`, `net/bluetooth/mgmt_util.h`, HCI controller code, BlueZ userspace, and any tests that exercise management socket ABI compatibility. Variable-tail arrays such as `opcodes[]`, `keys[]`, `uuids[][16]`, `eir[]`, `instance[]`, `handles[]`, and `adv_data[]` are length-governed by adjacent count or length fields.

## Risks
- Any reorder, type-width change, missing `__packed`, endian annotation change, or size constant mismatch can break the management ABI.
- Flexible arrays require strict length validation before dereference; malformed userspace payloads can otherwise cause overread/overwrite bugs in implementation code.
- The file contains many similar opcode/size definitions, so off-by-one or wrong-size constants are a realistic regression risk.
- New settings or event bits must preserve compatibility with older userspace that ignores unknown bits.
- The TLV helper intentionally groups the header members; moving fields outside the group would violate hardened layout assumptions.

## Test Signals
- Build coverage for `net/bluetooth` and management socket users catches layout/name regressions.
- Bluetooth management selftests or BlueZ mgmt tests should cover command-size validation, unknown command/status behavior, key loading, pairing prompt flows, discovery events, advertising instances, and monitor/mesh commands.
- ABI tests should assert `sizeof()` and `offsetof()` for packed public records, especially `mgmt_hdr`, `mgmt_tlv`, address/key records, advertising payload records, and event flexible-array offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/rfcomm.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/rfcomm.h

## Purpose
This header defines the Linux Bluetooth RFCOMM protocol interface: wire-frame constants, multiplexer command records, core session and DLC state, socket address/options, TTY ioctl ABI, and exported RFCOMM core/socket/TTY entry points. It bridges the RFCOMM core implementation, Bluetooth sockets, and optional RFCOMM TTY devices.

## Important APIs, Types, And Constants
- Frame and MCC constants include `RFCOMM_SABM`, `DISC`, `UA`, `DM`, `UIH`, `PN`, `MSC`, `RPN`, `RLS`, `FCON`, `FCOFF`, `TEST`, and `NSC`.
- `struct rfcomm_hdr`, `rfcomm_cmd`, `rfcomm_mcc`, `rfcomm_pn`, `rfcomm_rpn`, `rfcomm_rls`, and `rfcomm_msc` model RFCOMM control frames and parameter negotiation.
- `struct rfcomm_session` holds the underlying L2CAP socket, session timer, state/flags, initiator role, default credit-flow-control state, MTU, and DLC list.
- `struct rfcomm_dlc` is the channel object with queue, timer, mutex, state/flags, refcount, DLCI/address/priority, V.24 modem status, security/deferred setup fields, MTU, credit counters, owner pointer, and callbacks for data, state, and modem-status events.
- Exported functions manage DLC allocation/free/open/close/send, modem status, accept/deferred setup, duplicate lookup, session address extraction, socket lifecycle, connection indications, TTY initialization, and RFCOMM device ioctl handling.
- `struct sockaddr_rc`, `struct rfcomm_conninfo`, `struct rfcomm_pinfo`, and `RFCOMM_LM_*` define the socket-facing ABI.
- RFCOMM TTY ioctls and records (`RFCOMMCREATEDEV`, `RFCOMMRELEASEDEV`, `RFCOMMGETDEVLIST`, `RFCOMMGETDEVINFO`, `RFCOMMSTEALDLC`) expose device creation and introspection.

## Control Flow And State
DLC users allocate a `rfcomm_dlc`, set callbacks/security policy, then call `rfcomm_dlc_open()` with source/destination addresses and channel. The core creates or finds a session, negotiates PN and security, exchanges SABM/UA, manages credit-based flow control, and moves the DLC through connection states. Transmit paths queue `sk_buff`s through `rfcomm_dlc_send()` and use `tx_credits`, `RFCOMM_TX_THROTTLED`, and MTU fragmentation. Receive paths invoke the `data_ready` callback and can call `rfcomm_dlc_throttle()` or `rfcomm_dlc_unthrottle()`, which atomically gate calls to `__rfcomm_dlc_throttle()` and `__rfcomm_dlc_unthrottle()`. Close paths send DISC or tear down immediately depending on state and error.

## State And Persistence Behavior
RFCOMM state is runtime-only in this header. Sessions and DLCs are list-linked and timer-driven. DLC lifetime is governed by `refcount_t` through `rfcomm_dlc_hold()` and `rfcomm_dlc_put()`, with final release calling `rfcomm_dlc_free()`. Synchronization is per-DLC mutex plus bit flags. TTY device data exposed through ioctl persists only while the RFCOMM module/device exists; no durable storage is defined here.

## Dependencies And Integration Points
The header depends on Bluetooth address types, socket/sk_buff/list/timer/mutex/refcount infrastructure, ioctl encoding, and optional `CONFIG_BT_RFCOMM_TTY`. Implementations are in `net/bluetooth/rfcomm/core.c`, `sock.c`, and TTY code. Socket protocol setup calls `rfcomm_init_sockets()` and cleanup calls `rfcomm_cleanup_sockets()`. TTY support compiles to no-op inline functions when disabled.

## Risks
- Incorrect refcounting or callback invocation after `rfcomm_dlc_put()` can create use-after-free bugs.
- Credit-flow-control bookkeeping can stall data if `rx_credits`/`tx_credits` and throttle bits diverge.
- RFCOMM wire structs are packed and sometimes variable-length; parsers must validate lengths before interpreting `rfcomm_hdr.len`.
- Deferred setup and security flags (`RFCOMM_SEC_PENDING`, `AUTH_PENDING`, `AUTH_ACCEPT`, `AUTH_REJECT`, `DEFER_SETUP`) are sensitive to races between socket user actions and core timers.
- TTY ioctls are userspace ABI and must retain structure sizes and visible flag meanings.

## Test Signals
- RFCOMM socket tests should cover connect, accept, deferred setup, close during negotiation, send fragmentation, credit exhaustion/replenishment, and modem-status exchange.
- TTY tests should cover create/release/list/info/steal ioctl behavior with and without `CONFIG_BT_RFCOMM_TTY`.
- Fault-injection around timers, security rejection, malformed PN/RPN/MSC frames, and concurrent close/send is valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/rfcomm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/sco.h -->
# sources/distributed-fs/ceph-client/include/net/bluetooth/sco.h

## Purpose
This header defines the minimal SCO Bluetooth socket ABI used for synchronous audio links. It provides the default SCO MTU, socket address format, and socket option payloads for MTU and connection metadata.

## Important APIs, Types, And Constants
- `SCO_DEFAULT_MTU` is the default payload size.
- `struct sockaddr_sco` carries the address family and peer Bluetooth address.
- `SCO_OPTIONS` with `struct sco_options` exposes the negotiated MTU.
- `SCO_CONNINFO` with `struct sco_conninfo` exposes HCI handle and remote class-of-device bytes.

## Control Flow And State
There is no executable flow here. SCO socket implementation code uses these records in bind/connect/getsockopt/setsockopt paths. A userspace socket addresses a peer with `sockaddr_sco`; once connected, getsockopt-style queries return MTU and HCI connection identity.

## State And Persistence Behavior
The header defines transient socket-visible state only. MTU, HCI handle, and device class are derived from the live SCO/HCI connection and are not persisted by this file.

## Dependencies And Integration Points
The file depends on `sa_family_t`, `bdaddr_t`, and fixed-width Linux integer aliases. It integrates with the Bluetooth SCO protocol implementation and HCI connection layer.

## Risks
- These structs are userspace ABI; field order and width must remain stable.
- SCO code must ensure `sco_conninfo` reflects a valid live HCI connection and does not expose stale handle data after disconnect.

## Test Signals
- SCO socket ABI tests should validate address sizes and `SCO_OPTIONS`/`SCO_CONNINFO` getsockopt payload lengths.
- Audio/SCO integration tests should cover default MTU, connect/disconnect, and HCI handle reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bluetooth/sco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bond_3ad.h -->
# sources/distributed-fs/ceph-client/include/net/bond_3ad.h

## Purpose
This header defines the IEEE 802.3ad/LACP mode contract for the bonding driver. It includes LACP and marker PDU wire formats, state-machine enums, per-bond and per-slave 802.3ad state records, statistics, and exported hooks used by common bonding code.

## Important APIs, Types, And Constants
- `PKT_TYPE_LACPDU`, `AD_TIMER_INTERVAL`, `AD_LACP_SLOW`, and `AD_LACP_FAST` define slow-protocol packet type and timer cadence.
- State enums model the 802.3ad receive, periodic, mux, transmit, and churn machines.
- `lacpdu_t` and `bond_marker_t` are packed wire records; `lacpdu_header_t` and `bond_marker_header_t` include Ethernet headers.
- `struct bond_3ad_stats` tracks LACPDU and marker receive/transmit/error counters with `atomic64_t`.
- `aggregator_t` represents a link aggregation group with actor/partner keys, system identifiers, active status, and linked ports.
- `port_t` represents a slave port with actor/partner admin and operational parameters, all state-machine state/timers, churn counters, RCU pointer to the aggregator, and prepared outbound LACPDU.
- `struct ad_bond_info` and `struct ad_slave_info` embed 802.3ad state into `struct bonding` and `struct slave`.
- Exported functions initialize/bind/unbind, run the state-machine work handler, trigger aggregator selection, handle speed/duplex and link changes, receive LACPDUs, update LACP settings, fill stats, and set carrier.

## Control Flow And State
Common bonding code initializes 802.3ad state with `bond_3ad_initialize()` when the bond enters mode 4. Each slave is bound with `bond_3ad_bind_slave()`, which populates the per-slave aggregator and port. Periodic work calls `bond_3ad_state_machine_handler()` at the LACP cadence to advance receive, periodic, mux, transmit, and churn machines, update timers, send LACPDUs or markers, and select an active aggregator. Packet receive paths call `bond_3ad_lacpdu_recv()` after slow-protocol classification. Link, speed, duplex, LACP rate, active/passive mode, and actor setting changes feed back into port state and may initiate aggregator reselection.

## State And Persistence Behavior
State is held in memory in `ad_bond_info` and `ad_slave_info`. The bond-level system identity and aggregator identifier persist while the bond exists. Per-port state includes actor/partner operational parameters, state-machine timers, churn counts, aggregator linkage, and the last composed LACPDU. RCU protects the port-to-aggregator pointer, while the bonding `mode_lock` is documented in `bonding.h` as protecting 3ad state against concurrent unbind and state-machine work. Statistics are atomic and exported through netlink/stat paths.

## Dependencies And Integration Points
The header depends on Ethernet, sk_buff, netdevice, byteorder, and common bonding declarations. It is included by `bonding.h` and implemented by `drivers/net/bonding/bond_3ad.c`. It integrates with bond options for LACP rate, active mode, actor system/priority/key, aggregator selection policy, carrier computation, and netlink stats.

## Risks
- Wire PDU structs are packed and protocol-specified; layout drift breaks interop with switches.
- State-machine timers are interdependent; wrong cadence or missed locking can cause churn, duplicate aggregation, or traffic blackholing.
- RCU aggregator pointer updates must coordinate with slave unbind and state-machine traversal.
- Speed/duplex changes affect aggregator eligibility and must be propagated promptly.
- Stats and LACP settings exposed through user interfaces must remain consistent with packet processing.

## Test Signals
- LACP tests should cover active/passive negotiation, fast/slow rates, partner default/expired/current transitions, link down/up, aggregator selection policies, and carrier/min-links behavior.
- Packet tests should validate LACPDU and marker parsing, illegal/unknown counters, and marker responses.
- Concurrency tests should stress slave removal while 3ad work and receive paths are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bond_3ad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bond_alb.h -->
# sources/distributed-fs/ceph-client/include/net/bond_alb.h

## Purpose
This header defines adaptive load balancing support for bonding modes TLB and ALB. It provides timer constants, hash table sizes and sentinel values, transmit-load-balancing and receive-load-balancing client records, per-slave load state, per-bond ALB state, and exported functions for initialization, link/active changes, transmit selection, monitoring, MAC changes, and VLAN cleanup.

## Important APIs, Types, And Constants
- `ALB_TIMER_TICKS_PER_SEC`, `BOND_TLB_REBALANCE_INTERVAL`, `BOND_ALB_DEFAULT_LP_INTERVAL`, `BOND_TLB_REBALANCE_TICKS`, and `BOND_ALB_LP_TICKS()` define monitor timing.
- `TLB_HASH_TABLE_SIZE` and `RLB_HASH_TABLE_SIZE` are fixed at 256 and tied to byte-wide hash keys.
- `struct tlb_client_info` maps transmit clients to slaves and tracks transmitted bytes, previous load history, and per-slave linked-list indices.
- `struct rlb_client_info` maps ARP/IP client relationships to receive slaves and tracks MACs, VLAN ID, update-needed state, and used/source-hash list membership.
- `struct tlb_slave_info` tracks each slave's assigned TLB client list head and aggregate load.
- `struct alb_bond_info` owns dynamic TLB/RLB tables, rebalance counters, learning-packet counter, RLB flags, active receive slave, promisc timeout state, and retry/update counters.
- Exported functions include `bond_alb_initialize()`, `bond_alb_deinitialize()`, per-slave init/deinit, link/active-change handlers, `bond_alb_xmit()`, `bond_tlb_xmit()`, slave-selection helpers, monitor work, MAC address update, and VLAN cleanup.

## Control Flow And State
Mode setup calls `bond_alb_initialize()` before ALB monitor work starts, optionally enabling RLB for ALB mode. Each slave gets TLB state through `bond_alb_init_slave()`. Transmit paths call `bond_tlb_xmit()` or `bond_alb_xmit()`, which select slaves through hash/client tables and current `bond_slave_can_tx()` status. Periodic `bond_alb_monitor()` updates load histories, rebalances client assignments, sends learning packets, manages RLB ARP updates, and handles failover/promiscuous windows. Link and active slave changes update client assignments and may trigger learning/update bursts.

## State And Persistence Behavior
ALB/TLB state is runtime and dynamically allocated per bond. TLB entries accumulate byte counters between rebalance intervals and retain client-to-slave assignment until rebalanced or invalidated. RLB entries cache IP/MAC/VLAN associations and update-needed flags so the monitor can send corrective ARP traffic. Per-slave `tlb_slave_info` is embedded in `struct slave`. The common bond `mode_lock` protects ALB/TLB hash table access according to `bonding.h`.

## Dependencies And Integration Points
The header depends on Ethernet constants, `struct bonding`, `struct slave`, sk_buff/netdevice types supplied by implementation includes, and bond parameters such as `lp_interval` and `tlb_dynamic_lb`. It integrates with `drivers/net/bonding/bond_alb.c`, `bond_main.c` mode setup/transmit paths, VLAN handling, failover MAC handling, and ARP-based receive balancing.

## Risks
- Hash collisions intentionally replace older RLB entries; stale IP/MAC associations can cause wrong ARP updates if cleanup paths fail.
- Fixed-size tables and index sentinels require careful bounds checks around `next`/`prev` list manipulation.
- Rebalance timing constants are used in divisions and retry windows; invalid values can destabilize periodic work.
- MAC/VLAN changes must clear or update RLB entries to avoid directing peers to the wrong slave.
- Concurrent transmit and monitor updates require correct `mode_lock` use.

## Test Signals
- TLB/ALB tests should cover client assignment, byte accounting, periodic rebalancing, disabled dynamic LB, link failure, active slave change, and no-transmit-slave cases.
- RLB tests should cover ARP learning/update bursts, VLAN cleanup, failover promisc timeout, hash collision replacement, and MAC address changes.
- Stress tests should run concurrent xmit and monitor work while adding/removing slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bond_alb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bond_options.h -->
# sources/distributed-fs/ceph-client/include/net/bond_options.h

## Purpose
This header defines the bonding driver's option metadata and parsing interface. It enumerates all supported bond options, option/value flags, the generic value carrier used by sysfs/netlink/module parameter paths, and helper initializers used before setting or parsing options.

## Important APIs, Types, And Constants
- `BOND_OPT_MAX_NAMELEN`, `BOND_OPT_VALID()`, and `BOND_MODE_ALL_EX()` support option table validation and mode masks.
- `BOND_OPTFLAG_NOSLAVES`, `BOND_OPTFLAG_IFDOWN`, and `BOND_OPTFLAG_RAWVAL` describe setter preconditions and raw parsing behavior.
- `BOND_VALFLAG_DEFAULT`, `MIN`, and `MAX` mark special values in option value tables.
- `enum BOND_OPT_*` assigns stable IDs for mode, transmit hash policy, ARP/NS targets, delays, LACP options, peer notifications, primary/active slave, queue IDs, TLB/ALB controls, actor settings, broadcast-neighbor behavior, and port priority.
- `struct bond_opt_value` carries either a numeric value, string, small raw `extra` buffer, or `slave_dev` pointer.
- `struct bond_option` names an option, describes unsupported modes, valid values, flags, and the setter callback.
- Public helpers set options with or without notification, parse values, look up options by ID/name/value, and clear ARP/NS targets or update slave multicast addresses.
- Inline initializers `bond_opt_initval`, `bond_opt_initstr`, `bond_opt_initextra`, and `bond_opt_slave_initval` enforce the string-vs-value convention.

## Control Flow And State
Callers prepare a `bond_opt_value`, then pass it to `__bond_opt_set()` or `__bond_opt_set_notify()`. The option layer locates metadata by ID, validates mode/precondition flags, parses numeric/string/raw values through `bond_opt_parse()`, and invokes the option-specific setter. Sysfs uses `bond_opt_get_by_name()`, netlink uses option IDs and `nlattr` error reporting, and module parameter initialization parses defaults with the same tables.

## State And Persistence Behavior
This header does not store option state. Successful setters mutate `struct bonding.params`, slave state, ARP/NS target arrays, active slave references, or mode-specific settings in implementation code. Options persist for the lifetime of the bond device and may be surfaced through sysfs/proc/netlink.

## Dependencies And Integration Points
The header depends on Linux bit, limits, type, string, netlink, and netdevice declarations. Implementations live in `drivers/net/bonding/bond_options.c`, with callers in `bond_sysfs.c`, `bond_netlink.c`, `bond_procfs.c`, and `bond_main.c`. IPv6 NS target helpers are gated by `CONFIG_IPV6`.

## Risks
- Option enum order is used as bit positions and table IDs; insertion/reordering must match implementation tables.
- `__bond_opt_init()` copies raw extra data only up to `BOND_OPT_EXTRA_MAXLEN`; callers must not pass oversized or pointer-lifetime-sensitive raw data except through the dedicated slave helper.
- Mode/precondition flags must be kept synchronized with setters, or users can change unsafe options while slaves are present or the device is up.
- String/numeric ambiguity is resolved by `ULLONG_MAX`; callers must use the right initializer.

## Test Signals
- Option tests should cover sysfs, netlink, and module-parameter parse paths for every option ID.
- Boundary tests should validate min/max/default values, unsupported modes, no-slaves and interface-down restrictions, raw-value parsing, ARP/NS target clearing, and bad netlink extack reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bond_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bonding.h -->
# sources/distributed-fs/ceph-client/include/net/bonding.h

## Purpose
This is the common internal header for the Linux bonding driver. It defines the bond/slave core data structures, parameters, list traversal primitives, locking expectations, inline state transitions, monitoring helpers, transmit helpers, sysfs/proc/debug/netlink hooks, and mode integration points for 802.3ad, TLB, and ALB.

## Important APIs, Types, And Constants
- Slave list macros wrap lower-device adjacency lists and provide RTNL and RCU traversal variants.
- Netpoll helpers optionally block or query netpoll transmit under `CONFIG_NET_POLL_CONTROLLER`.
- `struct bond_params` stores user-configured mode, monitoring intervals, ARP/NS targets, LACP/ALB options, primary and failover behavior, peer notifications, transmit queue/hash parameters, and actor settings.
- `struct slave` stores the lower netdevice, parent bond, link timing, ARP receive timestamps, link state, active/backup/inactive/RX-disabled flags, speed/duplex, queue ID, permanent MAC, priority, 3ad/ALB per-slave state, netpoll, sysfs object, delayed notification work, and cached stats.
- `struct bonding` stores the master netdevice, active/current/primary slave RCU pointers, usable/all slave arrays, mode-specific locks, counters, work items, mode-specific state, params, debug/proc/sysfs hooks, IPsec state, and XDP program pointer.
- Inline helpers classify modes, read active slave, test link/transmit eligibility, set active/backup/inactive/RX-disabled flags, stage/commit link states, validate ARP/NS targets, read/write last TX/RX timestamps, propagate NAPI/netpoll data, and search slave MACs or target arrays.
- Exported functions cover enslave/release, transmit hashing, carrier updates, active slave selection, sysfs/debug/proc creation, XDP checks, netlink lifecycle, work initialization/cancel, VLAN path verification, slave array updates, and work rearming.

## Control Flow And State
Bond creation initializes `struct bonding`, parameters, work items, and mode-specific substructures. Enslaving attaches a lower netdevice, creates a `struct slave`, links it into lower adjacency lists, initializes mode-specific state, and exposes sysfs. Monitor work (`mii_work`, `arp_work`, `alb_work`, `ad_work`, multicast and notification work) updates link state and mode behavior. Inline state helpers queue lower-state and slave events immediately or defer notification by setting `should_notify`/`should_notify_link`. Transmit paths use mode-specific hash/selection functions and `bond_slave_can_tx()` to choose a usable slave or drop through `bond_tx_drop()`.

## State And Persistence Behavior
Bond and slave state is in-memory per net namespace. `bond_net` tracks namespace-level device lists and proc/sysfs roots. RCU protects active/current/primary slave pointers and slave arrays for read-side packet paths; RTNL protects slave-list mutation; `mode_lock` protects 3ad/TLB/ALB mode-specific state; `stats_lock` protects aggregate stats; optional `ipsec_lock` protects offload state. Parameters persist while the bond netdevice exists and are visible through sysfs/proc/netlink.

## Dependencies And Integration Points
The header depends on netdevice, timers, procfs, if_bonding UAPI, cpumask, IPv6, netpoll, inetdevice, etherdevice, reciprocal division, link attributes, bonding mode headers, XDP/BPF, and optional XFRM/debug/proc/netpoll features. It is included across `drivers/net/bonding/*` and exposes hooks to rtnetlink, sysfs, procfs, debugfs, XDP feature negotiation, netpoll, IPsec offload, IPv4 ARP, and IPv6 neighbor solicitation.

## Risks
- Locking rules are central: RCU reads, RTNL writes, and mode-specific spinlocks must be respected to avoid races in packet paths and workqueues.
- Inline state helpers both mutate flags and trigger notifications; incorrect `notify` usage can suppress or duplicate userspace/lower-state events.
- `bond_is_active_slave_dev()` assumes a valid slave pointer from `rx_handler_data`; callers must ensure the device is enslaved or guard against NULL in surrounding code.
- Link and active/backup flags drive transmit eligibility; divergence can cause traffic on down/inactive slaves or unnecessary drops.
- Parameters such as ARP/NS targets have fixed array limits and sentinel zero/any values that must be preserved.

## Test Signals
- Bonding tests should exercise enslave/release, all modes, active slave changes, carrier/min-links, ARP and NS monitoring, failover MAC policies, primary reselection, peer notifications, queue IDs, and transmit hashing.
- Concurrency tests should stress slave removal, work cancellation, RCU readers, netpoll, XDP program changes, and mode changes.
- ABI tests should cover sysfs/proc/netlink exposure of parameters and slave state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bonding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bpf_sk_storage.h -->
# sources/distributed-fs/ceph-client/include/net/bpf_sk_storage.h

## Purpose
This header declares BPF socket-local storage integration for `struct sock`. It exposes helper prototypes for BPF programs, lifecycle hooks for socket clone/free, and inet_diag serialization helpers, with no-op fallbacks when `CONFIG_BPF_SYSCALL` is disabled.

## Important APIs, Types, And Constants
- `bpf_sk_storage_free(struct sock *sk)` releases local storage attached to a socket during destruction.
- `bpf_sk_storage_get_proto`, `bpf_sk_storage_delete_proto`, and tracing variants expose BPF helper function metadata.
- `bpf_sk_storage_clone()` copies inheritable socket storage from a listener/parent to a new socket.
- `struct bpf_sk_storage_diag` is an opaque diagnostic context allocated from netlink attributes.
- `bpf_sk_storage_diag_alloc()`, `bpf_sk_storage_diag_free()`, and `bpf_sk_storage_diag_put()` support inet_diag dumping of selected or all socket storage values.
- When `CONFIG_BPF_SYSCALL` is off, clone and diag-put return success and allocation returns NULL, keeping callers buildable without BPF syscall support.

## Control Flow And State
Socket creation/destruction paths call clone/free hooks from core socket code. BPF programs use helper prototypes selected by verifier/program type to get or delete per-socket storage. Diagnostic dump paths allocate a `bpf_sk_storage_diag` from request attributes, iterate sockets, append storage data to sk_buffs through `bpf_sk_storage_diag_put()`, and free the diag context when the dump completes.

## State And Persistence Behavior
The actual storage is per-socket runtime state owned by BPF local-storage maps. It follows socket lifetime, may be cloned to accepted child sockets, and is released at socket destruction. No durable persistence exists. The header intentionally hides internal element/layout details behind opaque declarations.

## Dependencies And Integration Points
The header depends on BPF map/helper infrastructure, local storage support, RCU/list/hash/spinlock types, sockets, sock_diag UAPI, BTF UAPI, sk_buffs, and netlink attributes. Implementations are in `net/core/bpf_sk_storage.c`; socket lifecycle calls are in `net/core/sock.c`; inet_diag integration appears in `net/ipv4/inet_diag.c`; BPF program helper selection occurs in networking BPF code.

## Risks
- Callers must invoke `bpf_sk_storage_free()` on all destruction paths or storage leaks and stale map references can result.
- Clone failures must be handled by socket creation paths; partially cloned storage must be unwound correctly in implementation.
- Diagnostic dump sizing is error-prone because values are serialized into sk_buffs under netlink size limits.
- Config-disabled stubs silently skip diagnostic content, so tests must cover both enabled and disabled builds.

## Test Signals
- BPF selftests should cover helper get/delete from socket and tracing contexts, clone inheritance on accepted sockets, deletion/free on close, and map iteration.
- inet_diag tests should cover requested storage IDs, duplicate requests, large value payloads, and disabled `CONFIG_BPF_SYSCALL` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/bpf_sk_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/busy_poll.h -->
# sources/distributed-fs/ceph-client/include/net/busy_poll.h

## Purpose
This header defines network busy-poll support helpers. It provides NAPI ID validation, sysctl and socket busy-loop gates, busy-loop timeout helpers, wrappers around NAPI busy-loop execution, interrupt suspend/resume declarations, and inline propagation of NAPI IDs from receive packets to sockets.

## Important APIs, Types, And Constants
- `MIN_NAPI_ID` reserves `0` for unset and `1..NR_CPUS` for sender CPU values; valid NAPI IDs start at `NR_CPUS + 1`.
- `napi_id_valid()` checks that an ID can be used for busy polling.
- `BUSY_POLL_BUDGET` is the default per-loop budget when a socket-specific budget is not set.
- Under `CONFIG_NET_RX_BUSY_POLL`, `sysctl_net_busy_read` and `sysctl_net_busy_poll` control socket and poll/select busy-poll duration.
- `net_busy_loop_on()`, `sk_can_busy_loop()`, `busy_loop_current_time()`, `busy_loop_timeout()`, and `sk_busy_loop_timeout()` gate and time busy loops.
- `napi_busy_loop()` and `napi_busy_loop_rcu()` perform the polling; `napi_suspend_irqs()` and `napi_resume_irqs()` coordinate IRQ behavior.
- `sk_busy_loop()` invokes busy polling for a socket's cached NAPI ID.
- `skb_mark_napi_id()`, `sk_mark_napi_id()`, `sk_mark_napi_id_set()`, and once-only variants propagate receive queue/NAPI identity to packets and sockets.

## Control Flow And State
NIC receive/GRO code marks sk_buffs with the cached NAPI ID. Protocol handlers call `sk_mark_napi_id()` or setup variants to copy that ID and RX queue mapping to the socket. A blocking socket read or poll path can then call `sk_busy_loop()`; if the socket has a valid NAPI ID, enabled low-latency timeout, no pending signal, and optional nonblocking behavior, the code runs `napi_busy_loop()` with a loop-end callback and budget. Timeout helpers compare microsecond-shifted `ktime_get_ns()` values against sysctl or socket time limits.

## State And Persistence Behavior
State is runtime-only. NAPI identity is cached in `skb->napi_id`, `napi->gro.cached_napi_id`, and `sk->sk_napi_id`; receive queue mapping is updated through `sk_rx_queue_update()` or `sk_rx_queue_set()`. Busy-poll enablement comes from global sysctls and per-socket fields (`sk_ll_usec`, `sk_prefer_busy_poll`, `sk_busy_poll_budget`). Config-disabled builds compile most helpers to false/zero/no-op behavior.

## Dependencies And Integration Points
The header depends on netdevice, scheduler clock/signal state, IP/socket helpers, and XDP headers. Integration points include NIC receive handlers, GRO, TCP/UDP protocol receive paths, TCP child socket setup, poll/select/read paths, and sysctl configuration.

## Risks
- NAPI ID validity is subtle because low values overlap sender CPU reservations; treating any nonzero ID as valid can busy-poll the wrong target.
- Busy polling trades latency for CPU burn; timeout and signal checks must remain correct.
- Socket fields are accessed with `READ_ONCE`/`WRITE_ONCE`; removing those could introduce races with sysctl/socket option updates and receive paths.
- Config stubs must preserve type compatibility for builds without busy-poll support.

## Test Signals
- Networking tests should verify NAPI ID marking on receive, socket NAPI propagation for TCP/UDP and passive opens, busy-poll timeout behavior, signal interruption, per-socket budgets, and disabled-config no-op behavior.
- Performance tests should measure latency and CPU cost with busy polling enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/busy_poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/calipso.h -->
# sources/distributed-fs/ceph-client/include/net/calipso.h

## Purpose
This header declares CALIPSO support for IPv6 security labels as specified by RFC 5570. It defines DOI mapping constants, the DOI object used by NetLabel, cache sysctls, and config-gated initialization, cleanup, and option validation hooks.

## Important APIs, Types, And Constants
- `CALIPSO_DOI_UNKNOWN`, `CALIPSO_MAP_UNKNOWN`, and `CALIPSO_MAP_PASS` define known DOI/mapping values.
- `struct calipso_doi` stores DOI number, mapping type, refcount, list linkage, and RCU callback state.
- `calipso_cache_enabled` and `calipso_cache_bucketsize` are external sysctl variables.
- With `CONFIG_NETLABEL`, `calipso_init()`, `calipso_exit()`, and `calipso_validate()` are implemented by CALIPSO/NetLabel code.
- Without `CONFIG_NETLABEL`, init succeeds, exit is empty, and validation returns true.

## Control Flow And State
At network label subsystem initialization, `calipso_init()` registers CALIPSO support and cache state; shutdown calls `calipso_exit()`. IPv6 option processing can call `calipso_validate()` with the skb and raw option pointer to check option correctness. DOI objects are refcounted and RCU-freed as policy mappings are added and removed by implementation code.

## State And Persistence Behavior
DOI mappings live in kernel memory, are list-linked, and use `refcount_t` plus RCU for lifetime safety. Cache behavior is controlled by sysctls. The header itself provides no persistence; userspace policy loaders are responsible for installing DOI mappings after boot.

## Dependencies And Integration Points
The header depends on Linux types, RCU/list/net/skbuff infrastructure, NetLabel, request sockets, refcounts, and unaligned access helpers. It integrates with IPv6 option parsing, NetLabel policy management, and security-label enforcement.

## Risks
- The disabled-config validation stub returns true, so callers must rely on build configuration for enforcement expectations.
- CALIPSO options are parsed from packet bytes; implementation must handle alignment, length, and malformed options defensively.
- DOI lifetime requires correct refcount and RCU discipline to avoid stale label-policy references.

## Test Signals
- NetLabel/CALIPSO tests should cover DOI add/remove, validation of well-formed and malformed IPv6 CALIPSO options, cache sysctl behavior, and concurrent policy removal while packets are processed.
- Disabled `CONFIG_NETLABEL` builds should verify init/exit stubs and permissive validation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/calipso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/can.h -->
# sources/distributed-fs/ceph-client/include/net/can.h

## Purpose
This header defines CAN-specific sk_buff extension data. It gives SocketCAN code a compact place to preserve ingress interface, frame length, gateway hop count, and extension flags across skb processing.

## Important APIs, Types, And Constants
- `struct can_skb_ext` contains `can_iif` for the first interface index where the CAN frame appeared, `can_framelen` for cached echo frame length used by BQL, `can_gw_hops` as a CAN gateway TTL/hop counter, and `can_ext_flags` for CAN extension flags.

## Control Flow And State
The header contains no functions. CAN receive, echo, and gateway paths attach or read the `SKB_EXT_CAN` extension. `net/core/skbuff.c` sizes the extension using this struct, so CAN code can carry metadata without changing the base `sk_buff`.

## State And Persistence Behavior
State is per-packet and lives only as long as the skb and its extensions. It is not persisted beyond packet processing. The ingress interface and gateway hop fields are used to prevent metadata loss during forwarding or echo handling.

## Dependencies And Integration Points
The header depends on fixed-width kernel integer types being available from surrounding includes. It integrates with SocketCAN protocol/gateway/echo code and the generic skb extension registry in `net/core/skbuff.c`.

## Risks
- Any struct growth changes per-skb extension memory cost and must stay synchronized with `SKB_EXT_CAN` users.
- Gateway hop accounting must be updated consistently to avoid loops.
- Echo frame length must match the transmitted CAN frame or byte queue limit accounting can become inaccurate.

## Test Signals
- SocketCAN tests should cover skb extension allocation, preservation across gateway forwarding, hop limit behavior, echo/BQL length accounting, and mixed CAN/CAN-FD traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/can.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cfg80211-wext.h -->
# sources/distributed-fs/ceph-client/include/net/cfg80211-wext.h

## Purpose
This header declares transitional Wireless Extensions handlers implemented on top of cfg80211. It supports drivers that have not fully converted away from WEXT by exposing standard iw_handler-compatible callbacks for name, mode, scanning, range, RTS, fragmentation, and retry queries/settings.

## Important APIs, Types, And Constants
- `cfg80211_wext_giwname()` reports the wireless protocol/name.
- `cfg80211_wext_siwmode()` and `cfg80211_wext_giwmode()` set/get interface mode.
- `cfg80211_wext_siwscan()` and `cfg80211_wext_giwscan()` trigger and retrieve scans.
- `cfg80211_wext_giwrange()` reports supported ranges/capabilities.
- `cfg80211_wext_siwrts()`/`giwrts()` set/get RTS threshold.
- `cfg80211_wext_siwfrag()`/`giwfrag()` set/get fragmentation threshold.
- `cfg80211_wext_giwretry()` reports retry settings.
All functions use the WEXT callback signature: `struct net_device *`, `struct iw_request_info *`, `union iwreq_data *`, and extra buffer.

## Control Flow And State
Legacy WEXT ioctl dispatch invokes these handlers through a driver's iw_handler table. The handler translates WEXT requests into cfg80211 operations or cfg80211-maintained state, fills `iwreq_data` and optional extra buffers, and returns a Linux errno. Scan flow is asynchronous at the device layer: set-scan starts work, while get-scan serializes cached scan results.

## State And Persistence Behavior
The header stores no state. Mode, scan results, RTS/fragmentation thresholds, and retry data are held by cfg80211/wireless driver state. WEXT callers see a compatibility projection of that state.

## Dependencies And Integration Points
The header depends on netdevice, `linux/wireless.h`, and `net/iw_handler.h`. It integrates with cfg80211, legacy wireless ioctl handling, and partially converted wireless drivers.

## Risks
- WEXT and cfg80211 semantics do not always map one-to-one; translation can lose detail or expose stale cached scan results.
- Extra buffer sizing for scan/range results must be validated by implementation code to avoid truncation or overflow.
- These handlers are explicitly transitional, so new driver work should avoid expanding WEXT-only behavior.

## Test Signals
- Wireless compatibility tests should cover WEXT mode get/set, scan trigger/result retrieval, range reporting, RTS/fragmentation threshold set/get, retry reporting, and buffer-too-small behavior.
- Driver integration tests should confirm cfg80211-native state and WEXT views remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cfg80211-wext.h -->
