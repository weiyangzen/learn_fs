# sources/distributed-fs/ceph-client/net/bluetooth/iso.c

## Purpose

`iso.c` implements the kernel Bluetooth ISO socket protocol (`BTPROTO_ISO`) and bridges user-space `SOCK_SEQPACKET` ISO sockets to HCI Connected Isochronous Stream (CIS), Broadcast Isochronous Stream (BIS), and Periodic Advertising (PA) synchronization connections. It owns ISO socket allocation, bind/connect/listen/accept/send/recv/shutdown operations, socket option handling for ISO QoS and BASE data, HCI connection callbacks, ISO packet reassembly, and debug/procfs registration.

The file supports both unicast CIS paths and broadcast BIS/PA-sync paths. A socket connected to a normal peer address uses CIS; a socket whose connect address is `BDADDR_ANY` uses BIS broadcast behavior, with listening sockets able to synchronize to PA, parse BASE data from periodic advertising reports, and create or defer BIG synchronization.

## Important APIs, types, and functions

The central private types are `struct iso_conn` and `struct iso_pinfo`. `iso_conn` wraps an `hci_conn`, a back pointer to the attached socket, delayed timeout work, ISO RX reassembly state (`rx_skb`, `rx_len`), a transmit sequence number, and a `kref`. `iso_pinfo` is the protocol-private socket payload exposed by `iso_pi(sk)`; it stores source/destination Bluetooth addresses and address types, broadcast SID/BIS selection, sync handle, socket-local flags (`BT_SK_BIG_SYNC`, `BT_SK_PA_SYNC`), `bt_iso_qos`, BASE payload bytes, and the attached `iso_conn`.

The socket protocol entry points are registered through `iso_sock_ops`: `iso_sock_create`, `iso_sock_bind`, `iso_sock_connect`, `iso_sock_listen`, `iso_sock_accept`, `iso_sock_getname`, `iso_sock_sendmsg`, `iso_sock_recvmsg`, `iso_sock_shutdown`, `iso_sock_release`, `iso_sock_setsockopt`, and `iso_sock_getsockopt`. `iso_init` registers the protocol, Bluetooth socket family, procfs file, debugfs file, and HCI callback block; `iso_exit` unregisters them.

Connection management centers on `iso_conn_add`, `iso_chan_add`, `iso_chan_del`, `iso_conn_del`, `iso_sock_disconn`, `iso_sock_close`, and `iso_sock_kill`. These functions manage the `hci_conn->iso_data` association, socket back pointers, reference counts, accept queue interactions, state transitions, and delayed timeout cancellation.

The main active connection functions are `iso_connect_cis` for unicast CIS, `iso_connect_bis` for broadcast BIS source/sink setup, `iso_listen_cis` for address-bound incoming CIS listeners, and `iso_listen_bis` for PA-sync based broadcast listeners. Deferred setup is handled by `BT_SK_DEFER_SETUP`, `iso_conn_defer_accept`, `iso_conn_big_sync`, and special branches in `iso_sock_recvmsg`.

QoS and control-plane validation is in `check_io_qos`, `check_ucast_qos`, and `check_bcast_qos`; socket options expose `BT_DEFER_SETUP`, `BT_PKT_STATUS`, `BT_PKT_SEQNUM`, `BT_ISO_QOS`, and `BT_ISO_BASE`. `iso_sock_get_qos` returns live HCI QoS for connected sockets and socket-local QoS otherwise.

HCI integration uses the `iso_cb` callback block with `iso_connect_cfm` and `iso_disconn_cfm`, plus exported lower-layer entry points `iso_connect_ind` and `iso_recv`. `iso_connect_ind` inspects recent HCI LE PA/BIG events via `hci_recv_event_data`, matches listeners with `iso_get_sock`, updates PA sync handles/SIDs/BASE data, and decides whether HCI should accept or defer. `iso_recv` reassembles HCI ISO fragments and delivers complete SDUs to `iso_recv_frame`.

## Control flow

Socket creation requires `SOCK_SEQPACKET`, allocates `struct iso_pinfo` through `bt_sock_alloc`, installs defaults, links the socket into `iso_sk_list`, and starts in `BT_OPEN`. Bind validates `AF_BLUETOOTH`, LE address type, socket state, and optional broadcast address extension. Broadcast bind additionally validates SID, BIS count, and BIS indices, then stores them on `iso_pinfo`.

Connect first records the destination. If the destination is not `BDADDR_ANY`, `iso_connect_cis` routes to an HCI device, validates central CIS capability and unicast QoS, optionally binds instead of connects for deferred setup, creates or reuses an `hci_conn`, attaches an `iso_conn`, updates the source address, and moves the socket to `BT_CONNECT` or `BT_CONNECTED`. If the destination is `BDADDR_ANY`, `iso_connect_bis` performs the analogous BIS path with broadcast QoS, BASE, SID handling, and `hci_bind_bis` or `hci_connect_bis`.

Listen distinguishes CIS and BIS by whether `iso_pi(sk)->dst` is `BDADDR_ANY`. CIS listen only checks for duplicate listeners by address. BIS listen also resolves an HCI route, validates broadcast QoS, calls `hci_pa_create_sync`, attaches the resulting PA `hci_conn`, and later uses PA and BIG HCI events to create accepted child sockets.

Incoming connection readiness enters through HCI callbacks. `iso_connect_cfm` handles CIS/BIS/PA link completion, LE parent failure, and pending CIS creation on LE links. For ISO links it creates/looks up `iso_conn` and calls `iso_conn_ready` on success or special PA/BIG failure events, otherwise it tears down the socket. `iso_conn_ready` either marks an already attached socket connected or finds a listening parent, allocates a child socket, copies address/QoS/BASE/sync state, enqueues it on the parent's accept queue, and wakes the parent. Broadcast listeners may transition between `BT_LISTEN`, `BT_CONNECTED`, and `BT_CONNECT2` depending on PA sync, BIG sync, and deferred setup.

The receive path starts at `iso_recv`, which looks up the HCI handle, holds `hcon->iso_data`, parses ISO packet boundary flags and optional timestamp headers, allocates `conn->rx_skb` for fragmented SDUs, validates lengths, stores packet status and sequence number metadata, and passes complete frames to `iso_recv_frame`. `iso_recv_frame` only queues to the socket receive queue when the socket is still `BT_CONNECTED`; otherwise it drops.

The transmit path starts at `iso_sock_sendmsg`, rejects OOB data, processes control messages for TX timestamps, checks `BT_CONNECTED`, builds an skb plus continuation fragments bounded by HCI MTU, then calls `iso_send_frame`. `iso_send_frame` validates against the outgoing QoS SDU size, prepends an HCI ISO data header with a monotonically incremented sequence number and valid status, applies TX timestamp setup, and calls `hci_send_iso`.

Shutdown and release paths clear timers, close according to socket state, optionally drop or preserve shared BIG HCI connections, wait for linger if requested, orphan the socket, unlink from `iso_sk_list`, and drop references. The broadcast disconnect path has special handling for multiple sockets bound to the same BIG: it can detach one socket and leave the BIS HCI connection open if another socket is still using the BIG.

## State and persistence behavior

There is no on-disk persistence. Runtime state lives in sockets, HCI connection objects, debugfs/procfs views, delayed work, and Bluetooth core lists.

Global state is `iso_sk_list`, `default_qos`, `iso_debugfs`, and the `inited` flag. Socket state is split between generic `sk_state`, generic `bt_sk` flags such as `BT_SK_DEFER_SETUP`, and ISO-private fields in `iso_pinfo`. `iso_conn` state is reference-counted with `kref`; its `lock` protects `hcon` and `sk` pointer changes, while socket-level operations use `lock_sock`.

Timers use `iso_conn.timeout_work` for connection and disconnection timeouts. `iso_sock_set_timer` schedules this work based on `sk_sndtimeo`; the handler marks the socket `ETIMEDOUT` and signals state change if it can safely hold the socket. `iso_conn_free` disables pending delayed work after dropping the HCI connection, clears back pointers, frees any partial RX skb, and releases memory.

RX reassembly state is stored per `iso_conn`, not per socket, which matches the one-socket-per-ISO-HCI-link model enforced by `conn->sk`. Packet status and sequence number are saved in skb control metadata for upper layers when enabled.

## Dependencies and integration points

This file depends heavily on the Bluetooth core socket, HCI, and LE advertising APIs: `bt_sock_alloc/link/unlink`, `bt_accept_enqueue/dequeue/unlink`, `bt_sock_wait_state`, `bt_sock_recvmsg`, `bt_procfs_init/cleanup`, `hci_get_route`, `hci_connect_cis`, `hci_bind_cis`, `hci_connect_bis`, `hci_bind_bis`, `hci_pa_create_sync`, `hci_conn_big_create_sync`, `hci_past_bis`, `hci_send_iso`, `hci_recv_event_data`, `hci_register_cb`, and HCI capability predicates such as `cis_central_capable` and `bis_capable`.

It integrates with user space through PF_BLUETOOTH sockets using `struct sockaddr_iso` and `struct sockaddr_iso_bc`, ISO socket options from `<net/bluetooth/iso.h>`, normal `sendmsg`/`recvmsg`, accept queues, error queues, timestamp control messages, procfs, and debugfs. It also integrates with the Extended Inquiry Response parser through `eir_get_service_data` to extract Broadcast Audio Announcement BASE data from periodic advertising payloads.

## Risks and edge cases

Reference and lifetime correctness is critical. `iso_sock_hold`, `iso_conn_hold_unless_zero`, `sock_hold`, and lock ordering are used to avoid races between HCI callbacks, delayed timeout work, socket release, and connection deletion. Regressions can become use-after-free bugs because `hci_conn->iso_data`, `iso_conn->sk`, and `iso_pi(sk)->conn` are bidirectional pointers.

Lock ordering is delicate. Several paths intentionally release `lock_sock` before taking `hci_dev_lock` or vice versa to avoid deadlocks, especially `iso_sock_rebind_bc` and BIS/PA sync creation. Any new call path that mixes HCI device locking, socket locking, and `iso_conn.lock` needs the same ordering discipline.

Broadcast behavior has complex multi-stage state. PA sync establishment, PAST reception, BIG info reports, periodic advertising reports, BASE extraction, deferred BIG create sync, and repeated BIS accept cycles all share parent socket state. Off-by-one mistakes in `bc_num_bis` mutation during accept, SID wildcard handling, or sync-handle matching would surface as missed accepts, stale listeners, or wrong BIG synchronization.

Length validation protects HCI ISO reassembly. `iso_recv` drops malformed start/single/continuation frames, but the `ISO_END` branch assumes a partial `rx_skb` exists and appends without its own null guard. The surrounding HCI fragment ordering should prevent this, but malformed or reordered fragments are high-risk test inputs.

QoS validation is stateful: `check_bcast_qos` fills default sync fields while validating. There is a suspicious assignment in the timeout default path, where an unset `qos->bcast.timeout` sets `sync_timeout` rather than `timeout`. Tests should cover defaulting and boundary values to catch unintended behavior.

Shared BIG disconnect handling is subtle. `iso_sock_disconn` can detach one socket while preserving an HCI BIG connection for another socket. This depends on matching source, destination, and BIG handle correctly and clearing `hcon->iso_data`/`conn->hcon` without leaving stale references.

## Test signals

Useful test signals include ISO socket creation rejecting non-`SOCK_SEQPACKET` types; bind rejecting non-LE address types, invalid broadcast SID, too many BIS entries, and out-of-range BIS indexes; connect returning `-EHOSTUNREACH`, `-EOPNOTSUPP`, `-EINVAL`, `-ENOBUFS`, or successful `BT_CONNECTED` transitions under mocked HCI capabilities and buffer counts.

Coverage should exercise `BT_DEFER_SETUP` for both CIS and BIS: connect/listen should stop in deferred states, `recvmsg` should trigger CIS accept or BIG create sync, and accept should receive child sockets with expected state and copied address/QoS/BASE fields. PA-sync tests should feed `HCI_EV_LE_PA_SYNC_ESTABLISHED`, `HCI_EV_LE_PAST_RECEIVED`, `HCI_EVT_LE_BIG_INFO_ADV_REPORT`, and `HCI_EV_LE_PER_ADV_REPORT` paths and verify SID/sync-handle/BASE updates.

RX tests should cover single-frame ISO SDUs, timestamped frames, fragmented start/continue/end sequences, malformed single frames, unexpected starts, unexpected continuations, overlong fragments, socket-not-connected drops, and metadata propagation for packet status/sequence number. TX tests should cover SDU size enforcement against QoS, header sequence incrementing, continuation-fragment building, timestamp control messages, and send after disconnect.

Lifecycle tests should cover release/shutdown from every `BT_*` state, listener cleanup of unaccepted children, timeout work racing with close, HCI disconnect confirmation, failed connect confirmation, debugfs/procfs presence after init, and clean unregister through `iso_exit`.
