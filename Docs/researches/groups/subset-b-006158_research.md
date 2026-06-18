# subset-b-006158 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tvlv.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/tvlv.c

## Purpose
This file implements the batman-adv TVLV API: registration of locally advertised type-version-length-value containers, registration of handlers for received TVLVs, appending TVLVs to outgoing OGMs, parsing received TVLV buffers, and sending unicast TVLV packets to originators.

## Important APIs, Types, And Functions
`batadv_tvlv_container_register()` and `batadv_tvlv_container_unregister()` manage advertised containers stored in `bat_priv->tvlv.container_list`. `batadv_tvlv_container_ogm_append()` resizes an OGM buffer and serializes all current containers after the base OGM header. `batadv_tvlv_handler_register()` and `batadv_tvlv_handler_unregister()` manage callbacks in `bat_priv->tvlv.handler_list`. `batadv_tvlv_containers_process()` parses a received TLV stream and dispatches to OGM, unicast, or multicast callbacks. `batadv_tvlv_ogm_receive()` extracts the OGM TVLV area, and `batadv_tvlv_unicast_send()` builds and sends a `BATADV_UNICAST_TVLV` skb through `batadv_send_skb_to_orig()`.

## Control Flow
Container registration allocates one object containing `struct batadv_tvlv_hdr` plus optional payload, removes any existing type/version match, and inserts the replacement under `container_list_lock`. OGM append first computes total advertised length under the same lock, reallocates the packet buffer, then copies each header and payload in wire order. Receive-side processing walks the buffer while complete headers and payload lengths remain, looks up a matching handler by type/version, calls the protocol-specific callback, and releases the handler reference. After OGM processing, handlers with `BATADV_TVLV_HANDLER_OGM_CIFNOTFND` are called with empty data when they were not seen in the OGM interval. Unicast send resolves an originator by destination MAC, constructs a control-priority skb, embeds one TVLV header and payload, and hands the skb to the originator send path.

## State, Persistence, And Dependencies
State is per mesh interface in `bat_priv->tvlv`. Containers are protected by `container_list_lock`; handlers are inserted and removed under `handler_list_lock` but are traversed with RCU and refcounted with `kref`. Handler objects are freed by `kfree_rcu()`, while container objects are freed after list removal and reference release. There is no disk persistence; advertised TVLVs live until replacement, unregistration, or mesh teardown.

## Integration Points
The file depends on packet definitions from `uapi/linux/batadv_packet.h`, originator lookup in `originator.h`, and the transmit path in `send.h`. Feature modules such as gateway, multicast, translation table, DAT, and algorithm code register TVLV containers or handlers through this API. OGM code calls `batadv_tvlv_container_ogm_append()` for outbound advertisements and `batadv_tvlv_ogm_receive()` for inbound OGMs.

## Risks
Correctness depends on lock discipline: container lookup/removal requires `container_list_lock`, while handlers require RCU-safe lookup and paired `batadv_tvlv_handler_put()`. `batadv_tvlv_container_ogm_append()` returns the desired TVLV length even if packet-buffer reallocation fails, so callers must treat the actual packet buffer length carefully. Handler `flags` are modified while processing OGMs from RCU traversal, so missed or concurrent updates could affect CIFNOTFND notifications. Packet parsing stops silently on malformed truncated TVLV lengths, which is robust for forwarding but can hide peer bugs.

## Test Signals
Useful signals include OGM packets containing all registered containers with correct network-order lengths, replacement/unregistration removing stale TVLVs, malformed TVLV buffers not overrunning, CIFNOTFND callbacks firing exactly once per absent OGM TVLV, unicast TVLV routing only when an originator exists, and KASAN/lockdep coverage for handler/container lifetime races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tvlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tvlv.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/tvlv.h

## Purpose
This header exposes the batman-adv TVLV subsystem interface to the rest of the mesh implementation.

## Important APIs, Types, And Functions
It declares container registration, unregistration, and OGM append helpers; receive-side OGM and generic TVLV processing helpers; handler registration/unregistration with OGM, unicast, and multicast callbacks; and `batadv_tvlv_unicast_send()`.

## Control Flow
There is no executable control flow in the header. It defines the public call surface used by feature modules to advertise local capabilities and consume peer-advertised TVLVs.

## State, Persistence, And Dependencies
The functions operate on `struct batadv_priv`, `struct batadv_orig_node`, `struct sk_buff`, and packet structures from `uapi/linux/batadv_packet.h`. State storage is declared in `types.h` as `batadv_priv_tvlv`; this header only publishes entry points.

## Integration Points
TVLV producers such as translation table, gateway, multicast, and DAT code use these declarations to attach data to OGMs. Packet receive paths call `batadv_tvlv_containers_process()` or `batadv_tvlv_ogm_receive()` after validating outer packet formats.

## Risks
Callback prototypes require callers to preserve payload lifetime only for the duration of the call. Type/version uniqueness is enforced by the implementation, so duplicate registration silently keeps the first handler and replaces containers.

## Test Signals
Compile coverage should catch signature drift between TVLV users and `tvlv.c`. Runtime test signals are the same as implementation users: advertised containers visible in OGMs and handlers invoked on matching inbound TVLVs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/tvlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/types.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/types.h

## Purpose
This header is the central private data model for batman-adv. It declares per-interface, per-originator, per-neighbor, TVLV, translation table, gateway, multicast, DAT, bridge-loop-avoidance, fragmentation, forwarding, throughput-meter, and algorithm callback structures.

## Important APIs, Types, And Functions
Key structures include `batadv_priv`, `batadv_hard_iface`, `batadv_orig_node`, `batadv_neigh_node`, `batadv_priv_tvlv`, `batadv_tvlv_container`, `batadv_tvlv_handler`, `batadv_priv_tt`, `batadv_tt_*` entries, `batadv_priv_gw`, optional `batadv_priv_mcast`, optional `batadv_priv_dat`, optional BLA types, `batadv_forw_packet`, and `batadv_algo_ops` with nested interface, neighbor, originator, and gateway operation tables. Important enums include DHCP direction, traffic counters, originator capabilities, throughput meter role, and TVLV handler flags.

## Control Flow
The file does not implement behavior, but it encodes control-flow contracts through callbacks and ownership fields. Routing algorithms plug in via `batadv_algo_ops`; TVLV callbacks are stored in `batadv_tvlv_handler`; delayed work fields drive OGM transmission, ELP transmission, translation-table purging, multicast updates, DAT purging, BLA work, originator purging, throughput-meter completion, and forwarding queues.

## State, Persistence, And Dependencies
Most state is runtime-only and tied to net_device lifetime. Lifetimes are governed by `kref`, RCU heads, spinlocks, mutexes, atomics, delayed work, hlist/list membership, and per-CPU counters. `batadv_priv` is the root per mesh interface object and embeds feature-private substructures. Conditional blocks depend on kernel config options such as `CONFIG_BATMAN_ADV_DAT`, `CONFIG_BATMAN_ADV_MCAST`, `CONFIG_BATMAN_ADV_BLA`, `CONFIG_BATMAN_ADV_BATMAN_V`, and `CONFIG_BATMAN_ADV_DEBUG`.

## Integration Points
All batman-adv modules include this indirectly through `main.h`. Packet formats come from `uapi/linux/batadv_packet.h` and netlink/user ABI from `uapi/linux/batman_adv.h`. `tvlv.c` specifically uses `batadv_priv_tvlv`, `batadv_tvlv_container`, `batadv_tvlv_handler`, and `batadv_tvlv_handler_flags`.

## Risks
This header concentrates cross-module concurrency contracts, so field misuse can produce races even if individual modules compile. Several comments specify locks that must protect list or metadata updates; bypassing those locks can corrupt routing, TT, TVLV, or multicast state. Conditional compilation changes structure layouts and available counters, which makes feature combinations important. Some comments in the BLA claim structure appear swapped between `refcount` and `rcu`, so maintainers should verify semantics from usage rather than relying only on the comment text.

## Test Signals
Useful signals include lockdep on all list mutations, RCU stall/KASAN coverage during teardown, feature matrix builds across optional configs, route/TT/multicast/gateway behavior under interface churn, and netlink/debugfs dumps that agree with the embedded counters and lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/6lowpan.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/6lowpan.c

## Purpose
This module implements IPv6 6LoWPAN over Bluetooth Low Energy L2CAP IPSP. It creates virtual `bt%d` 6LoWPAN net_devices, maps BLE peers to IPv6 link-layer addresses, compresses/decompresses IPv6 packets, and exposes debugfs controls for enabling, connecting, and disconnecting peers.

## Important APIs, Types, And Functions
Important state types are `lowpan_btle_dev` for one virtual 6LoWPAN device per HCI controller, `lowpan_peer` for one L2CAP peer, and `skb_cb` for transmit routing metadata in `skb->cb`. The main data paths are `chan_recv_cb()`, `recv_pkt()`, `iphc_decompress()`, `bt_xmit()`, `setup_header()`, `send_pkt()`, and `send_mcast_pkt()`. Control and lifecycle functions include `bt_6lowpan_connect()`, `bt_6lowpan_disconnect()`, `bt_6lowpan_listen()`, `chan_ready_cb()`, `chan_close_cb()`, `setup_netdev()`, `disconnect_all_peers()`, debugfs handlers, and module init/exit.

## Control Flow
When enabled through debugfs, work in `do_enable_set()` toggles `enable_6lowpan`, closes any old listener, optionally disconnects existing peers, and creates a listening LE credit-flow L2CAP channel on IPSP. A new connection allocates or finds the HCI-scoped virtual netdev, adds a peer derived from the channel destination address, schedules neighbor notification, and opens the netdev. RX packets arrive from L2CAP, locate the peer and device, validate 6LoWPAN type, decompress IPHC or strip uncompressed IPv6 dispatch, and feed an aligned copy into `netif_rx()`. TX packets are unshared, compressed with `lowpan_header_compress()`, mapped to a peer by route/gateway/neighbour cache for unicast or cloned to all peers for multicast, and sent through `l2cap_chan_send()`.

## State, Persistence, And Dependencies
Global runtime state consists of `bt_6lowpan_devices`, `devices_lock`, `enable_6lowpan`, `listen_chan`, and `set_lock`. Peer objects are RCU-list entries freed by `kfree_rcu()` and hold L2CAP channel references plus derived EUI-48 and IPv6 addresses. Device objects live in lowpan netdev private data and are removed through unregister paths or delayed work. There is no persistent storage; debugfs state and connections are runtime-only.

## Integration Points
The module integrates with Bluetooth HCI/L2CAP, Linux 6LoWPAN compression, IPv6 routing and neighbor lookup, net_device registration, debugfs under `bt_debugfs`, and the netdevice notifier chain. It depends on `CONFIG_BT_LE` and generic `6LOWPAN` support through Kconfig.

## Risks
The code mixes RCU iteration, `devices_lock`, L2CAP channel locking, module reference counting, and asynchronous work, so teardown ordering is the main risk. `send_mcast_pkt()` clones and immediately frees clones after `send_pkt()`, relying on L2CAP send behavior and `chan->data` use. Debugfs parsing preserves a historical address-type mismatch for disconnect commands, which can surprise users. TX route selection uses cached gateway information in `skb->cb`, so missing routes or stale neighbours can drop packets.

## Test Signals
Test signals include creating and removing `bt%d` devices on connect/disconnect, correct debugfs enable/listen behavior, IPv6 ping over BLE with compressed and uncompressed packets, multicast neighbor discovery reaching all peers, queue stop/wake on L2CAP suspend/resume, netdev unregister cleanup without leaks, and lockdep/KASAN under repeated enable/disable and peer churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/6lowpan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/Kconfig -->
# sources/distributed-fs/ceph-client/net/bluetooth/Kconfig

## Purpose
This Kconfig file defines top-level Bluetooth subsystem options and includes subordinate protocol and driver configuration menus.

## Important APIs, Types, And Functions
Main symbols are `BT`, `BT_BREDR`, `BT_LE`, `BT_LE_L2CAP_ECRED`, `BT_6LOWPAN`, `BT_LEDS`, `BT_MSFTEXT`, `BT_AOSPEXT`, `BT_DEBUGFS`, `BT_SELFTEST`, `BT_SELFTEST_ECDH`, `BT_SELFTEST_SMP`, and `BT_FEATURE_DEBUG`. It also sources RFCOMM, BNEP, HIDP, and drivers Bluetooth Kconfigs.

## Control Flow
Kconfig selection determines which object files and feature paths are compiled. `BT` selects core crypto primitives used by pairing and management; `BT_BREDR` and `BT_LE` gate classic and LE protocol families; `BT_6LOWPAN` depends on LE and generic 6LoWPAN; extension and debug options enable optional source files in the Makefile.

## State, Persistence, And Dependencies
The file has no runtime state. It encodes build-time dependencies on RFKILL, CRC16, crypto algorithms, debugfs, LED triggers, LE support, and debug kernel support for selftests.

## Integration Points
`net/bluetooth/Makefile` consumes these symbols to build `bluetooth.o`, `bluetooth_6lowpan.o`, optional extension modules, and subdirectories. User-visible configuration controls which socket protocols, HCI features, debugfs entries, and selftests exist.

## Risks
Incorrect dependency changes can create link failures or expose runtime code without required crypto or transport support. Enabling selftests can delay boot or module load. Feature combinations such as `BT_AOSPEXT`, `BT_MSFTEXT`, `BT_LE`, and `BT_BREDR` should be tested both built-in and modular.

## Test Signals
Important signals are successful allmodconfig/allyesconfig/minimal builds, expected module lists for selected options, crypto dependencies present when `BT` is enabled, and runtime feature availability matching selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/Makefile -->
# sources/distributed-fs/ceph-client/net/bluetooth/Makefile

## Purpose
This Makefile maps Bluetooth Kconfig symbols to built objects and protocol subdirectories.

## Important APIs, Types, And Functions
It builds `bluetooth.o` from core objects such as `af_bluetooth.o`, HCI core/conn/event/socket/sysfs/sync/driver code, L2CAP, SMP, management, ECDH helper, codec, EIR, and utility files. It adds optional objects for coredumps, SCO, ISO, LEDs, Microsoft extensions, AOSP extensions, debugfs, and selftests. It also builds RFCOMM, BNEP, HIDP, and `bluetooth_6lowpan.o` when enabled.

## Control Flow
There is no runtime control flow. Build-time object inclusion follows `obj-$(CONFIG_...)` and `bluetooth-$(CONFIG_...)` assignments.

## State, Persistence, And Dependencies
The file has build-system state only. It depends on Kconfig symbols defined in the Bluetooth tree and driver/device-coredump configs.

## Integration Points
The top-level kernel build consumes this file. Its object grouping must stay aligned with exported symbols and init/exit ordering in source files such as `af_bluetooth.c`, `6lowpan.c`, `bnep/core.c`, and optional extension helpers.

## Risks
Missing an object here can produce unresolved symbols for headers that compile fine. Adding optional objects to the wrong aggregate can make disabled features link into the core unexpectedly. Ordering within `bluetooth-y` matters when initcall dependencies or duplicate symbols appear.

## Test Signals
Build tests across config matrices should verify expected objects appear, modules load, and optional files such as `coredump.o`, `aosp.o`, `hci_codec.o`, and `6lowpan.o` are only present for matching symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/af_bluetooth.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/af_bluetooth.c

## Purpose
This file implements the PF_BLUETOOTH address-family core: protocol registration, socket allocation and common socket helpers, accept-queue handling, shared recv/poll/ioctl/wait utilities, procfs socket listing, debugfs root creation, and subsystem init/exit orchestration.

## Important APIs, Types, And Functions
Exported protocol APIs include `bt_sock_register()`, `bt_sock_unregister()`, `bt_sock_alloc()`, `bt_sock_link()`, `bt_sock_unlink()`, `bt_sock_linked()`, `bt_accept_enqueue()`, `bt_accept_unlink()`, `bt_accept_dequeue()`, `bt_sock_recvmsg()`, `bt_sock_stream_recvmsg()`, `bt_sock_poll()`, `bt_sock_ioctl()`, `bt_sock_wait_state()`, `bt_sock_wait_ready()`, `bt_procfs_init()`, and `bt_procfs_cleanup()`. `bt_init()` registers the address family and initializes HCI sockets, L2CAP, SCO, and management; `bt_exit()` unwinds them and removes debugfs/sysfs/LED resources.

## Control Flow
`bt_sock_create()` validates init_net and protocol number, autoloads `bt-proto-%d` if needed, pins the protocol module, calls its create callback, and reclassifies socket locks for lockdep. Accept-queue helpers hold socket references, copy peer credentials from parent sockets, and safely dequeue connected or deferred-setup children. Datagram and stream recv helpers consume skb queues with truncation, ancillary HCI status/sequence cmsgs, MSG_PEEK support, and blocking waits. Poll combines state, shutdown, queue, error, suspend, and writeability conditions. Init follows selftest, debugfs, LEDs, sysfs, address-family registration, HCI socket, L2CAP, SCO, and management setup with reverse cleanup labels.

## State, Persistence, And Dependencies
The core protocol table `bt_proto[]` is protected by `bt_proto_lock`. Per-protocol lock-class arrays make lockdep distinguish Bluetooth protocols. Socket lists are maintained by protocol modules using `bt_sock_list`. `bt_debugfs` is an exported root dentry. Runtime state is in sockets, queues, procfs entries, sysfs, and debugfs; there is no persistent storage.

## Integration Points
Protocol modules such as BNEP, RFCOMM, HIDP, SCO, L2CAP, HCI, and ISO register through this file. It integrates with Linux sockets, procfs, debugfs, sysfs, LED triggers, ethtool timestamp queries via HCI, module autoloading, and BlueZ userspace-visible AF_BLUETOOTH sockets.

## Risks
The protocol dispatch table must be accessed under the rwlock; create callbacks are invoked while the read lock is held, so deadlocks are possible if protocol create paths re-enter registration. Accept dequeuing restarts after concurrent unlink to avoid unsafe list traversal, but socket lifetime depends on precise `sock_hold()`/`sock_put()` pairing. Stream receive mutates skb fragments manually; partial pulls must preserve skb length invariants. `bt_init()` does not initialize ISO but `bt_exit()` calls `iso_exit()`, which relies on the called function being safe for the selected build/config state.

## Test Signals
Signals include successful protocol module autoload, AF_BLUETOOTH socket creation per protocol, accept/defer setup behavior, recvmsg ancillary data, poll state transitions, ethtool timestamp ioctl on `hciX`, `/proc/net` protocol listings, debugfs root creation/removal, and fault-injection coverage for each init cleanup label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/af_bluetooth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/aosp.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/aosp.c

## Purpose
This file implements support for Android Open Source Project Bluetooth vendor extensions, currently focused on discovering vendor capabilities and enabling/disabling Bluetooth Quality Report events.

## Important APIs, Types, And Functions
`aosp_do_open()` queries vendor capabilities with OGF 0x3f/OCF 0x153 and records quality-report support. `aosp_do_close()` is a cleanup hook. `aosp_has_quality_report()` exposes capability state. `aosp_set_quality_report()` selects `enable_quality_report()` or `disable_quality_report()`, which send the BQR vendor command OGF 0x3f/OCF 0x015e using `struct aosp_bqr_cp`.

## Control Flow
On HCI open, the file first checks `hdev->aosp_capable`, sends the get-capabilities command synchronously, validates the returned buffer size against versioned layouts, logs the vendor capability version, rejects versions below 0.95, requires v0.98 for quality reports, and sets `hdev->aosp_quality_report` when the controller reports support. Enabling BQR sends an ADD action with default event mask and interval; disabling sends a CLEAR action.

## State, Persistence, And Dependencies
State is stored on `struct hci_dev` as `aosp_capable` and `aosp_quality_report`. There is no persistence beyond the HCI device lifetime. The file depends on synchronous HCI command helpers, Bluetooth device logging, little-endian conversions, and vendor command semantics.

## Integration Points
The Makefile includes this object under `CONFIG_BT_AOSPEXT`. HCI core open/close and management paths call the declared hooks through `aosp.h`, and users of quality reporting call `aosp_set_quality_report()` after capability discovery.

## Risks
Vendor response layout grows over time, so length checks must stay version-aware. The code initializes `event_mask` and `min_report_interval` in host-endian fields inside a packed command struct; this relies on the expected command endianness and could be fragile across architecture review. A typo in macro names does not affect behavior but makes audits harder. Synchronous command failures only log and leave the feature disabled.

## Test Signals
Signals include HCI open on AOSP-capable controllers logging version, controllers below v0.98 not exposing BQR, BQR enable/disable sending the expected vendor command, malformed short capability responses logging length errors without memory access, and `aosp_has_quality_report()` matching controller support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/aosp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/aosp.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/aosp.h

## Purpose
This header provides the AOSP extension interface and no-op stubs when `CONFIG_BT_AOSPEXT` is disabled.

## Important APIs, Types, And Functions
It declares `aosp_do_open()`, `aosp_do_close()`, `aosp_has_quality_report()`, and `aosp_set_quality_report()` for enabled builds. Disabled builds inline no-op open/close, return `false` for quality-report support, and return `-EOPNOTSUPP` for quality-report configuration.

## Control Flow
There is no runtime control flow beyond inline stubs. The header lets core HCI code call AOSP hooks unconditionally without preprocessor branches at each call site.

## State, Persistence, And Dependencies
The functions operate on `struct hci_dev`. State is owned by HCI device fields and the implementation in `aosp.c`.

## Integration Points
HCI core and management code include this header to initialize and configure vendor extension behavior. The Makefile includes `aosp.o` only when `CONFIG_BT_AOSPEXT` is enabled.

## Risks
Callers must tolerate `-EOPNOTSUPP` in disabled builds. The header assumes `struct hci_dev` is visible from includers through surrounding HCI headers.

## Test Signals
Builds with and without `CONFIG_BT_AOSPEXT` should both compile, and disabled builds should expose no runtime BQR capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/aosp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/Kconfig -->
# sources/distributed-fs/ceph-client/net/bluetooth/bnep/Kconfig

## Purpose
This Kconfig file defines build options for the Bluetooth Network Encapsulation Protocol layer.

## Important APIs, Types, And Functions
Symbols are `BT_BNEP`, `BT_BNEP_MC_FILTER`, and `BT_BNEP_PROTO_FILTER`. `BT_BNEP` is a tristate that depends on classic Bluetooth BR/EDR and selects CRC32. The filter options are bool features gated by `BT_BNEP`.

## Control Flow
The selections determine whether the BNEP module is built and whether multicast and protocol filter code is compiled in `core.c` and `netdev.c`.

## State, Persistence, And Dependencies
There is no runtime state. Build dependencies ensure the classic Bluetooth transport and CRC32 helper are present for PAN Ethernet emulation.

## Integration Points
`net/bluetooth/Kconfig` sources this file, and `bnep/Makefile` builds `bnep.o` when `BT_BNEP` is enabled.

## Risks
Disabling filter options changes control-message behavior: peers receive unsupported-filter responses and local netdev filtering is absent. Dependency mistakes could build PAN support without classic Bluetooth L2CAP support.

## Test Signals
Build and runtime signals include presence or absence of `bnep.ko`, `bt-proto-4` alias registration, and filter control responses matching selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/Makefile -->
# sources/distributed-fs/ceph-client/net/bluetooth/bnep/Makefile

## Purpose
This Makefile builds the BNEP protocol module from its core, socket, and netdevice components.

## Important APIs, Types, And Functions
`obj-$(CONFIG_BT_BNEP) += bnep.o` creates the module or built-in object. `bnep-objs := core.o sock.o netdev.o` groups the implementation.

## Control Flow
There is no runtime control flow. Build inclusion is controlled entirely by `CONFIG_BT_BNEP`.

## State, Persistence, And Dependencies
The file has build-system state only. It depends on symbols declared by `bnep/Kconfig`.

## Integration Points
The parent Bluetooth Makefile descends into `bnep/`, and the resulting object registers the BNEP socket protocol and PAN netdev support.

## Risks
If any of the three component objects are omitted, exported BNEP control or netdev functions will be unresolved or the module will lack its expected data path.

## Test Signals
Kernel build output should include `core.o`, `sock.o`, and `netdev.o` in `bnep.o` whenever `CONFIG_BT_BNEP` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/bnep.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/bnep/bnep.h

## Purpose
This header defines the BNEP protocol constants, packet/control structures, ioctl ABI structures, session state, and shared functions for BNEP core, socket, and netdev code.

## Important APIs, Types, And Functions
It defines BNEP packet types, control types, extension types, response codes, service UUIDs, PSM/MTU/timeouts, ioctl numbers, feature flags, `struct bnep_setup_conn_req`, `struct bnep_set_filter_req`, `struct bnep_control_rsp`, `struct bnep_ext_hdr`, ioctl request/response structures, `struct bnep_proto_filter`, and `struct bnep_session`. It declares `bnep_add_connection()`, `bnep_del_connection()`, `bnep_get_connlist()`, `bnep_get_conninfo()`, `bnep_net_setup()`, `bnep_sock_init()`, and `bnep_sock_cleanup()`. `bnep_mc_hash()` computes the multicast hash bit.

## Control Flow
No executable control flow exists except the inline multicast hash. The layout encodes the contract used by the session thread, virtual Ethernet device, and control socket ioctl path.

## State, Persistence, And Dependencies
`struct bnep_session` is the central runtime state: role, state bits, flags, termination atomic, thread pointer, cached Ethernet header, outgoing `msghdr`, optional filters, socket, and net_device. There is no persistence beyond active PAN sessions.

## Integration Points
`core.c` owns sessions and packet translation, `netdev.c` owns net_device operations and filtering, and `sock.c` exposes user-space ioctls for BlueZ/network setup. The header depends on Bluetooth core headers, Ethernet sizes, CRC32, and user-copy ioctl conventions.

## Risks
The ioctl structures are user ABI and should not be changed casually. Filter limits bound kernel memory and parsing; increasing them affects control message size and CPU cost. `bnep_session` contains both socket and netdev lifetime pointers, so ownership must remain consistent across all users.

## Test Signals
Signals include ABI-compatible ioctl behavior, correct BNEP control packet layout on the wire, session state visible through connection-list ioctls, and multicast hash filtering matching peer requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/bnep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/core.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/bnep/core.c

## Purpose
This file implements the BNEP session engine: PAN session creation/deletion, packet header compression/decompression, BNEP control handling, optional filters, the per-session kernel thread, and module init/exit.

## Important APIs, Types, And Functions
Public functions are `bnep_add_connection()`, `bnep_del_connection()`, `bnep_get_connlist()`, and `bnep_get_conninfo()`. Internal core functions include `bnep_rx_frame()`, `bnep_tx_frame()`, `bnep_rx_control()`, `bnep_rx_extension()`, `bnep_ctrl_set_netfilter()`, `bnep_ctrl_set_mcfilter()`, `bnep_session()`, session list helpers, and `bnep_send_rsp()`. Module parameters `compress_src` and `compress_dst` control transmit header compression.

## Control Flow
Adding a connection validates the socket is L2CAP and connected, derives local/remote Ethernet addresses from L2CAP addresses, allocates a net_device with `bnep_session` private data, registers it, links the session under `bnep_session_sem`, pins the module, and starts `kbnepd`. The session thread drains the socket receive queue into `bnep_rx_frame()`, drains the socket write queue into `bnep_tx_frame()`, wakes the netdev queue, and sleeps on the socket waitqueue until termination or disconnect. RX validates BNEP type, handles control frames, parses extensions, decompresses Ethernet headers, strips VLAN tag metadata when needed, builds an aligned Ethernet skb, and injects it via `netif_rx()`. TX chooses compressed header type based on cached peer addresses, sends via `kernel_sendmsg()`, updates stats, and frees the skb. Deleting a connection sets `terminate` and wakes the thread; thread cleanup unregisters the netdev, signals socket error, releases the socket file, unlinks the session, frees the netdev, and exits with module put.

## State, Persistence, And Dependencies
The global `bnep_session_list` is protected by `bnep_session_sem`. Each session persists while its kernel thread and netdev are alive and owns a referenced userspace-provided L2CAP socket file. Optional filter state lives in `proto_filter` and `mc_filter`. State is runtime-only and disappears on session teardown or module unload.

## Integration Points
The file integrates with L2CAP sockets, virtual Ethernet netdev setup from `netdev.c`, user ioctls from `sock.c`, the Bluetooth core module alias `bt-proto-4`, and BlueZ PAN setup. It uses `register_netdev()`, socket queues, kernel threads, `kernel_sendmsg()`, and Ethernet helpers.

## Risks
BNEP parsing is byte-sensitive and must reject truncated frames; several branches rely on `skb_pull()`/`skb_pull_data()` checks to avoid overruns. The session thread owns cleanup, so failed kthread creation and unregister paths must avoid double-freeing the netdev. User-supplied socket FDs are held until thread cleanup; error paths must `sockfd_put()` in `sock.c` or `fput()` in the thread. Filter parsing accepts ranges and can be CPU-heavy for large multicast ranges, bounded by filter limits and a 64-bit hash saturation check.

## Test Signals
Signals include creating a `bnep%d` netdev from a connected L2CAP socket, duplicate destination rejection, Ethernet frames passing both directions, compressed and uncompressed header formats decoding correctly, control filter requests producing expected responses, connection list/info ioctls reflecting state, and teardown releasing socket/netdev/module refs under disconnect and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/netdev.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/bnep/netdev.c

## Purpose
This file implements the virtual Ethernet net_device operations for BNEP PAN sessions.

## Important APIs, Types, And Functions
`bnep_net_setup()` initializes a BNEP net_device. Netdev operations include open/close, transmit, multicast-list update, MAC-address handling, timeout recovery, and validation. Optional helpers are `bnep_net_mc_filter()`, `bnep_net_proto_filter()`, and `bnep_net_eth_proto()`.

## Control Flow
Opening starts the netdev queue and closing stops it. TX optionally drops packets rejected by multicast or protocol filters, queues accepted skbs on the underlying Bluetooth socket write queue, wakes the BNEP session thread, and stops the netdev queue once `BNEP_TX_QUEUE_LEN` is reached. Multicast-list updates build and queue a BNEP filter control request based on promiscuous/allmulti/broadcast/multicast address state. TX timeout simply wakes the queue.

## State, Persistence, And Dependencies
Per-netdev state is `struct bnep_session` stored in netdev private data. Filter state is shared with `core.c`. The socket write queue buffers outbound Ethernet frames and locally generated control packets until `kbnepd` sends them. There is no persistent storage.

## Integration Points
`core.c` allocates the netdev and calls `bnep_net_setup()`. Linux networking calls these `net_device_ops`. The session thread in `core.c` consumes the sk_write_queue that TX and multicast filter updates populate.

## Risks
TX runs in contexts where L2CAP send is unsafe, so all direct send attempts must stay in the session thread. Queue pressure is managed by skb count, not byte size. Optional filters can silently drop traffic by design; default protocol filter ranges should match BNEP expectations. `bnep_net_set_mac_addr()` returns success without changing the address, so user attempts to set MAC may appear accepted but have no effect.

## Test Signals
Signals include queue stop/wake when write queue reaches threshold and drains, multicast filter control packets on address-list changes, protocol/multicast drops when options are enabled, no direct L2CAP send from hard-xmit context, and normal Ethernet traffic over the PAN netdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/sock.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/bnep/sock.c

## Purpose
This file exposes the BNEP control socket protocol under PF_BLUETOOTH, handling raw socket creation, ioctls for PAN session management, procfs listing, and protocol registration.

## Important APIs, Types, And Functions
Key functions are `bnep_sock_create()`, `bnep_sock_release()`, `bnep_sock_ioctl()`, `bnep_sock_compat_ioctl()`, `do_bnep_sock_ioctl()`, `bnep_sock_init()`, and `bnep_sock_cleanup()`. The socket operations table supports release and ioctl only; normal bind/connect/send/recv/listen operations use `sock_no_*` stubs.

## Control Flow
Creating a BNEP socket requires `SOCK_RAW`, allocates a Bluetooth socket with `bt_sock_alloc()`, assigns BNEP proto ops, marks it unconnected, and links it into `bnep_sk_list`. Ioctl handling gates add/delete operations on `CAP_NET_ADMIN`, copies request structures from userspace, resolves a provided connected L2CAP socket FD for `BNEPCONNADD`, delegates session work to `core.c`, copies updated data back to userspace, and supports connection list/info and supported-feature queries. Compat ioctl repacks the connection-list pointer for 32-bit userspace. Init registers the proto, registers `BTPROTO_BNEP` with the Bluetooth core, and creates `/proc/net/bnep`.

## State, Persistence, And Dependencies
The file maintains `bnep_sk_list` for procfs reporting. Active session state is owned by `core.c`; this socket layer only brokers user requests and references. There is no persistence beyond open sockets and active sessions.

## Integration Points
It uses common Bluetooth socket helpers from `af_bluetooth.c`, BNEP session functions from `core.c`, L2CAP sockets passed from userspace, Linux capabilities, file descriptor lookup, compat user pointers, and procfs.

## Risks
File descriptor ownership is split: on successful add, the session thread later releases the socket file; on failure, this layer must put it immediately. Ioctl structs are UAPI-like and require careful copy_to/from_user handling. Only raw sockets are supported, so wrong socket types must fail cleanly. Capability checks must remain on mutating operations.

## Test Signals
Signals include raw BNEP socket creation, non-raw rejection, permission failures for unprivileged add/delete, successful `BNEPCONNADD` returning the created device name, `BNEPCONNDEL` terminating sessions, compat `BNEPGETCONNLIST` working from 32-bit userspace, and `/proc/net/bnep` appearing and disappearing with module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/bnep/sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/coredump.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/coredump.c

## Purpose
This file implements the Bluetooth HCI devcoredump state machine used by drivers to collect controller/firmware dumps, mirror them to HCI diagnostics, and publish them through the kernel devcoredump facility.

## Important APIs, Types, And Functions
Exported APIs are `hci_devcd_register()`, `hci_devcd_init()`, `hci_devcd_append()`, `hci_devcd_append_pattern()`, `hci_devcd_complete()`, `hci_devcd_abort()`, `hci_devcd_rx()`, and `hci_devcd_timeout()`. Internal helpers allocate/copy/memset dump buffers, build headers, update state, notify drivers, emit dumps, and reset/free state.

## Control Flow
Drivers register coredump, header, and optional notification callbacks. Public append/init/complete/abort APIs package requests as typed skbs on `hdev->dump.dump_q` and queue `dump_rx` work. The worker processes packets sequentially under `hci_dev_lock()`: INIT allocates a vmalloc buffer containing the generic and driver header, switches to ACTIVE, and starts a timeout; SKB and PATTERN append data while ACTIVE; COMPLETE and ABORT switch to terminal states and emit a dump. After terminal states, the worker notifies state changes and resets the state machine. Timeout work notifies the driver, cancels pending RX work, marks TIMEOUT, emits available data, resets, and unlocks.

## State, Persistence, And Dependencies
State is stored in `hdev->dump`: head/tail/end pointers, allocation size, current state, work items, skb queue, timeout, callbacks, and support flag. Dump memory is vmalloc'd per active dump and handed to `dev_coredumpv()`, transferring ownership to the devcoredump core. Runtime state is not persisted by this module.

## Integration Points
Bluetooth HCI drivers call the exported APIs. The file integrates with `linux/devcoredump.h`, HCI diagnostic receive (`hci_recv_diag()`), HCI workqueues, device logging, skb queues, unaligned little-endian helpers, and optional driver callbacks.

## Risks
The state machine is strict; packets in unexpected states are logged and ignored, so driver ordering bugs can lose dump data. Size accounting prevents writes past the allocated buffer, but failed append attempts only log debug messages. Timeout cancels RX work while queued skbs may remain until reset purges the queue. Header size is capped at 512 bytes, so oversized driver headers can overflow the temporary skb if not controlled by driver callback behavior.

## Test Signals
Signals include successful init/append/complete producing a devcoredump and diagnostic skb, abort producing a partial dump, timeout producing a partial dump and notifying the driver, pattern append filling expected bytes, invalid state transitions not crashing, and reset freeing/purging all dump resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.c

## Purpose
This file wraps the kernel KPP/ECDH crypto API for Bluetooth LE Secure Connections key generation and shared-secret computation, including Bluetooth-required endian conversion.

## Important APIs, Types, And Functions
Exported helpers are `compute_ecdh_secret()`, `set_ecdh_privkey()`, `generate_ecdh_public_key()`, and `generate_ecdh_keys()`. `swap_digits()` reverses and byte-swaps 64-bit limbs between Bluetooth little-endian key format and crypto API representation.

## Control Flow
`set_ecdh_privkey()` optionally converts a provided 32-byte private key, encodes an ECDH key blob, and calls `crypto_kpp_set_secret()`, generating a private key when input is NULL. `generate_ecdh_public_key()` submits a KPP public-key request, waits for completion, then converts the 64-byte X/Y point back to Bluetooth little-endian order. `compute_ecdh_secret()` converts peer public key coordinates, submits a shared-secret request, waits, converts the 32-byte secret back, and clears sensitive temporary buffers. `generate_ecdh_keys()` sets/generates a private key then computes the public key.

## State, Persistence, And Dependencies
The caller owns the `struct crypto_kpp *tfm` and key material buffers. This file allocates temporary buffers and KPP requests per call and uses `DECLARE_CRYPTO_WAIT` for asynchronous completion. No state persists beyond the crypto transform's secret.

## Integration Points
SMP/Secure Connections code calls these helpers after allocating an ECDH KPP transform. Kconfig `BT` selects `CRYPTO_ECDH`, and `BT_SELFTEST_ECDH` can exercise these helpers.

## Risks
The code casts byte buffers to `u64 *` in `swap_digits()`, so alignment assumptions should be considered on strict-alignment architectures even though kernel allocations are aligned and caller arrays may be stack or struct fields. Sensitive buffers are cleared with `kfree_sensitive()`, but the public-key temporary buffer is freed normally. Incorrect endian conversion would silently break pairing interoperability.

## Test Signals
Signals include known-answer ECDH selftests, generated public keys accepted by peer SMP, shared secrets matching test vectors, allocation-failure injection returning `-ENOMEM`, crypto request errors propagating, and KMSAN/KASAN coverage of key-buffer access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.h

## Purpose
This header declares Bluetooth ECDH helper functions built on the kernel KPP crypto API.

## Important APIs, Types, And Functions
It declares `compute_ecdh_secret()`, `set_ecdh_privkey()`, `generate_ecdh_public_key()`, and `generate_ecdh_keys()`, all operating on `struct crypto_kpp` and fixed-size Bluetooth P-256 key buffers.

## Control Flow
There is no executable control flow. The declarations define the SMP-facing crypto helper contract.

## State, Persistence, And Dependencies
The header depends on `<crypto/kpp.h>` and Linux integer types. State is carried by the caller's crypto transform and buffers.

## Integration Points
Bluetooth SMP and selftest code include this header to perform LE Secure Connections ECDH operations without duplicating KPP request plumbing.

## Risks
The API exposes fixed-size arrays by pointer convention; callers must provide correctly sized 32-byte private/secret and 64-byte public-key buffers. The header has no include guard, so duplicate inclusion relies on declarations being identical and harmless.

## Test Signals
Compile tests should catch signature drift. Runtime signals come from SMP pairing and ECDH selftests using the helper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/eir.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/eir.c

## Purpose
This file constructs and parses Bluetooth Extended Inquiry Response and LE advertising data, including local names, appearance, service UUID lists, service data, advertising payloads, scan responses, and periodic advertising data.

## Important APIs, Types, And Functions
Public functions include `eir_create()`, `eir_create_adv_data()`, `eir_create_scan_rsp()`, `eir_create_per_adv_data()`, `eir_append_local_name()`, `eir_append_appearance()`, `eir_append_service_data()`, and `eir_get_service_data()`. Internal helpers create 16-bit, 32-bit, and 128-bit UUID lists from `hdev->uuids`.

## Control Flow
Classic EIR creation appends a complete or shortened device name, inquiry TX power, device ID, and UUID lists until `HCI_MAX_EIR_LENGTH` space runs out. Advertising creation locates an optional advertising instance, conditionally adds flags based on instance and global discoverability, copies user-provided advertising data, and optionally appends TX power. Scan response creation either builds a default appearance/name response or combines instance scan response data with managed appearance/local-name fields. Service-data lookup iterates AD elements of type `EIR_SERVICE_DATA` and returns the matching UUID payload.

## State, Persistence, And Dependencies
The file reads state from `struct hci_dev`, `struct adv_info`, management advertising flags, UUID lists, names, appearance, power values, and device ID fields. It writes only caller-provided output buffers and has no persistent state.

## Integration Points
HCI setup and management advertising code use these helpers when programming controller EIR/advertising/scan-response data. It integrates with `hci_find_adv_instance()`, `hci_adv_instance_flags()`, `mgmt_get_adv_discov_flags()`, and EIR constants from Bluetooth headers.

## Risks
Most append helpers assume the caller has already reserved enough space; only selected paths check remaining size. Instance advertising data is memcpy'd using stored lengths, so earlier validation in management paths is required. UUID list truncation correctly changes the type from ALL to SOME, but boundary tests are important. Service-data parsing must avoid underflow when malformed fields have less than UUID length.

## Test Signals
Signals include generated EIR/AD bytes matching expected length/type/value encoding, truncation switching UUID list types to SOME, advertising flags respecting managed/discoverable/no-BR-EDR rules, scan responses containing requested appearance/name data, and malformed EIR data not causing out-of-bounds access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/eir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/eir.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/eir.h

## Purpose
This header declares EIR/advertising construction helpers and provides inline routines for common AD element encoding and lookup.

## Important APIs, Types, And Functions
It declares the public functions implemented in `eir.c`. Inline helpers are `eir_precalc_len()`, `eir_append_data()`, `eir_append_le16()`, `eir_skb_put_data()`, and `eir_get_data()`.

## Control Flow
Append helpers encode length, type, and payload into a caller-owned buffer or skb. `eir_get_data()` walks AD elements until it finds a requested type, a zero-length terminator, or malformed/truncated data.

## State, Persistence, And Dependencies
There is no persistent state. The header depends on unaligned little-endian helpers, skbuff APIs for `eir_skb_put_data()`, and visible HCI/Bluetooth types from includers.

## Integration Points
HCI, management, advertising, and EIR parsing code include this header to build payloads consistently. `eir.c` uses the same inline helpers for local-name, appearance, and service-data work.

## Risks
Append helpers do not check destination capacity; callers must perform size accounting. `eir_skb_put_data()` warns if the AD field length would exceed `u8` capacity but still writes based on inputs. `eir_get_data()` returns NULL for zero-length data fields, so callers must distinguish absent data from present empty data if that ever matters.

## Test Signals
Signals include correct AD length calculation, little-endian 16-bit fields, skb tailroom usage under normal callers, and parser behavior on empty, zero-terminated, exact-fit, and truncated advertising buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/eir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.c

## Purpose
This file discovers local Bluetooth controller codec support and codec capabilities through HCI commands and stores the results in the HCI device codec list.

## Important APIs, Types, And Functions
Public functions are `hci_read_supported_codecs()`, `hci_read_supported_codecs_v2()`, and `hci_codec_list_clear()`. Internal helpers are `hci_codec_list_add()` and `hci_read_codec_capabilities()`. The code populates `struct codec_list` entries in `hdev->local_codecs`.

## Control Flow
The v1 and v2 entry points send synchronous Read Local Supported Codecs commands, validate response sizes, parse standard and vendor codec arrays, and request capabilities for each supported transport. `hci_read_codec_capabilities()` iterates transport bits, falls back to adding codecs without caps if the controller lacks the Read Codec Capabilities command, otherwise sends the command, validates status and variable-length capability records, and appends a codec-list entry under `hci_dev_lock()`. Clearing walks and frees all list entries.

## State, Persistence, And Dependencies
State persists in `hdev->local_codecs` until cleared, typically across HCI device setup lifetime. Each list entry stores codec ID, optional company/vendor IDs, transport, capability count, and variable-length capability bytes. The file depends on synchronous HCI command helpers, HCI command bitmasks, flexible-array response structs, and HCI device locking.

## Integration Points
HCI initialization/setup code calls these functions after reading controller features. Management or debug paths can later report `hdev->local_codecs` to userspace. The header declares these functions for HCI core users.

## Risks
All parsing is from controller-provided variable-length data; missed length validation could overrun. Current code validates aggregate codec arrays and each capability record before copying. Capability command failures skip that codec/transport rather than aborting discovery. If list clearing is omitted during device reset, stale codec entries could be reported.

## Test Signals
Signals include correctly populated standard and vendor codec entries for v1/v2 responses, no-cap fallback when command bit is absent, rejection of short or malformed responses, no leaks after `hci_codec_list_clear()`, and management output matching controller-advertised codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.h

## Purpose
This header declares the HCI codec discovery and cleanup helpers.

## Important APIs, Types, And Functions
It declares `hci_read_supported_codecs()`, `hci_read_supported_codecs_v2()`, and `hci_codec_list_clear()`.

## Control Flow
There is no executable control flow. The declarations let HCI setup code select the correct discovery command version and clear codec state during teardown or reset.

## State, Persistence, And Dependencies
State is owned by the caller-provided `struct hci_dev` and its codec list. The header assumes `struct hci_dev` and `struct list_head` are visible to includers.

## Integration Points
HCI core includes this header for controller codec enumeration, especially for SCO/ISO/audio capability reporting paths.

## Risks
Because the header is intentionally small and lacks include guards, it depends on identical repeated declarations being harmless. Callers must hold any required HCI device context expected by the implementation.

## Test Signals
Compile coverage catches signature drift; runtime discovery tests are in `hci_codec.c` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.h -->
