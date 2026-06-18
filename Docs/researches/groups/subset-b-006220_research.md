# Research: subset-b-006220

Grouped research report for the subset B work item. Each section preserves the original source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_ppp.c -->
# sources/distributed-fs/ceph-client/net/l2tp/l2tp_ppp.c

## Purpose
`l2tp_ppp.c` implements the PPPoX protocol endpoint for PPP over L2TP. It exposes `PX_PROTO_OL2TP` sockets, binds those sockets to L2TP tunnel/session objects, registers PPP channels for data sessions, supports special session-id-zero tunnel-management sockets, and wires the module into per-net proc output, L2TP netlink session creation, and PPP/L2TP statistics.

## Important APIs, Types, and Functions
The main private type is `struct pppol2tp_session`, stored in `l2tp_session->priv[]`, containing the owning pid plus an RCU-protected PPPoX socket pointer guarded by `sk_lock`. `pppol2tp_create()`, `pppol2tp_connect()`, `pppol2tp_release()`, `pppol2tp_sendmsg()`, `pppol2tp_recvmsg()`, `pppol2tp_setsockopt()`, `pppol2tp_getsockopt()`, and `pppol2tp_ioctl()` implement the socket API. `pppol2tp_xmit()` is the PPP channel transmit callback, while `pppol2tp_recv()` is installed as the L2TP session receive callback. The module registers `struct pppox_proto`, `struct proto_ops`, `struct proto`, and, when L2TPv3 is enabled, `struct l2tp_nl_cmd_ops`.

## Control Flow
Socket creation allocates a `struct pppox_sock`, sets `SOCK_RCU_FREE`, installs backlog receive through `l2tp_udp_encap_recv()`, and leaves the socket unconnected. `connect()` parses one of the IPv4/IPv6 L2TPv2/L2TPv3 sockaddr layouts into `l2tp_connect_info`, resolves or creates a tunnel, resolves or creates a PPP pseudowire session, then either registers a PPP channel or attaches a tunnel-management socket for id-zero sessions. User `sendmsg()` allocates a fresh skb with IP/UDP/L2TP/PPP headroom and calls `l2tp_xmit_skb()`. PPP core transmit uses `skb_cow_head()`, prepends PPP address/control bytes, and also calls `l2tp_xmit_skb()`. Receive strips optional PPP address/control bytes, then either feeds `ppp_input()` for bound PPP channels or queues the skb to the socket receive queue.

## State and Persistence
State is volatile kernel state: socket state bits, `sk_user_data`, L2TP tunnel/session refcounts, session sequence options, reorder timeout, statistics counters, and optional proc/debugfs views. Lifetime depends on RCU and refcounts: `pppol2tp_sock_to_session()` grabs a session reference, `pppol2tp_session_close()` clears `ps->sk`, clears socket user data, and drops the socket-held session reference, and `pppol2tp_release()` deletes the L2TP session before final socket put.

## Dependencies and Integration Points
This file sits between PPP (`ppp_register_net_channel()`, `ppp_input()`), PPPoX, L2TP core (`l2tp_tunnel_*`, `l2tp_session_*`, `l2tp_xmit_skb()`), UDP/IP sockets, net namespaces, procfs, and optional L2TPv3 netlink creation. Userspace interacts through AF_PPPOX sockets, ioctls such as `PPPIOCGL2TPSTATS`, and `SOL_PPPOL2TP` socket options.

## Risks and Edge Cases
The highest-risk areas are lifetime races between socket close, L2TP session deletion, PPP unbind, and RCU socket lookup. Headroom sizing must remain consistent with L2TP header length changes caused by send-sequence settings. The id-zero management socket path deliberately bypasses PPP registration and should stay isolated from data-session operations. Stats and proc paths read shared tunnel/session objects and must keep reference discipline. IPv6 conditional branches in `getname()` are another compatibility-sensitive area.

## Test Signals
Useful signals include AF_PPPOX connect/send/recv tests for L2TPv2 and L2TPv3, PPP channel attach/detach tests, id-zero management socket ioctl/sockopt tests, namespace proc visibility, stats copy correctness, receive of PPP frames with and without `0xff03`, close/unregister race tests under KASAN/KCSAN, and L2TPv3 netlink session-create/delete coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/l2tp_ppp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/trace.h -->
# sources/distributed-fs/ceph-client/net/l2tp/trace.h

## Purpose
`trace.h` defines the L2TP tracepoint surface. It gives tracing consumers stable events for tunnel/session registration and deletion, session sequence-number changes, and packet discard cases without embedding ad hoc debug logging in the hot paths.

## Important APIs, Types, and Functions
The file uses Linux tracepoint macros: `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT`. Shared event classes include `tunnel_only_evt`, `session_only_evt`, `session_seqnum_evt`, and `session_pkt_discard_evt`. Symbol formatting helpers map `enum l2tp_encap_type` and `enum l2tp_pwtype` values to readable names with `__print_symbolic()`.

## Control Flow
There is no runtime control flow beyond generated tracepoint code. L2TP core code includes this header and calls generated `trace_*` sites. `register_tunnel` captures tunnel identity, fd, ids, version, and encapsulation. `register_session` captures session/tunnel ids and pseudowire type. Delete/free events share name-only classes. Sequence and discard events capture `ns`, `nr`, packet sequence, expected receive sequence, and reorder queue length.

## State and Persistence
Trace events snapshot volatile L2TP state into the tracing ring buffer. They do not own tunnel/session references or persist configuration. String arrays copy fixed-size tunnel/session names into trace entries, avoiding pointer lifetime issues after free events.

## Dependencies and Integration Points
The header depends on `linux/tracepoint.h`, public `linux/l2tp.h`, and local `l2tp_core.h`. The `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and final `trace/define_trace.h` include integrate with the kernel trace generation model.

## Risks and Edge Cases
Trace formats become user-observable ABI for tooling, so field meaning and print format changes can break scripts. The `register_session` print format appears to print `sid`/`psid` in the final `tid`/`ptid` slots, which is a diagnostic accuracy risk. Event handlers must avoid dereferencing nullable tunnel pointers; the session registration event already falls back to zero ids when `session->tunnel` is absent.

## Test Signals
Enable L2TP trace events with ftrace/perf, create/delete tunnels and sessions, trigger sequence-number updates and reorder discards, and verify emitted fields match the live L2TP objects. A targeted test should validate the `register_session` printed tunnel ids because the format arguments are suspicious.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l2tp/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l3mdev/Kconfig -->
# sources/distributed-fs/ceph-client/net/l3mdev/Kconfig

## Purpose
This Kconfig entry exposes `NET_L3_MASTER_DEV`, the core networking glue needed by L3 master devices such as VRF. It controls whether the l3mdev API is available to route lookup code and device drivers.

## Important APIs, Types, and Functions
The file defines one bool symbol, `NET_L3_MASTER_DEV`, with prompt `L3 Master device support`. It depends on `INET || IPV6`, so it is only meaningful when IPv4 or IPv6 networking is present.

## Control Flow
Kconfig selection is compile-time only. If enabled, the l3mdev object is built by the directory Makefile and the exported l3mdev helpers become available to other networking code.

## State and Persistence
No runtime state is stored here. The selected value persists only through kernel configuration and determines compilation of the related object.

## Dependencies and Integration Points
The dependency on `INET || IPV6` aligns l3mdev support with IP routing consumers. VRF and similar drivers rely on the symbol to access L3 master lookup, FIB table, and flow update helpers.

## Risks and Edge Cases
If code assumes l3mdev helpers exist without the symbol dependency, build failures or missing route isolation support can result. The help text is intentionally broad and does not select a concrete VRF driver.

## Test Signals
Build matrix coverage should include IPv4-only, IPv6-only, dual-stack, and neither-stack configurations to confirm the symbol appears and l3mdev users compile as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l3mdev/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l3mdev/Makefile -->
# sources/distributed-fs/ceph-client/net/l3mdev/Makefile

## Purpose
The Makefile builds the L3 master device API implementation.

## Important APIs, Types, and Functions
It contains a single object rule, `obj-y += l3mdev.o`, so `l3mdev.c` is built into the networking core when the directory is included by the parent build.

## Control Flow
There is no runtime control flow. The parent networking build and Kconfig determine whether this directory participates, and this file contributes `l3mdev.o`.

## State and Persistence
No state is persisted here. The rule only affects build composition.

## Dependencies and Integration Points
The object exports GPL symbols used by routing, FIB rule, and device-driver code. Because it is `obj-y`, consumers expect the helper symbols to be present whenever the containing build path is enabled.

## Risks and Edge Cases
Changing `obj-y` to conditional or modular output would affect exported-symbol availability and could break built-in callers. The file deliberately has no additional object list.

## Test Signals
Build tests should ensure `l3mdev.o` is linked when `NET_L3_MASTER_DEV` support is configured and that no missing-symbol errors appear for l3mdev consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l3mdev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l3mdev/l3mdev.c -->
# sources/distributed-fs/ceph-client/net/l3mdev/l3mdev.c

## Purpose
`l3mdev.c` implements core helpers for devices that act as L3 routing masters, especially VRF-style devices. It lets drivers register table-id lookup callbacks, derives a flow's L3 master device, and dispatches route-table and IPv6 link-scope lookups through device-provided `l3mdev_ops`.

## Important APIs, Types, and Functions
`struct l3mdev_handler` stores a `lookup_by_table_id_t` callback per `enum l3mdev_type`. Exported functions include `l3mdev_table_lookup_register()`, `l3mdev_table_lookup_unregister()`, `l3mdev_ifindex_lookup_by_table_id()`, `l3mdev_master_ifindex_rcu()`, `l3mdev_master_upper_ifindex_by_index_rcu()`, `l3mdev_fib_table_rcu()`, `l3mdev_fib_table_by_index()`, `l3mdev_link_scope_lookup()`, `l3mdev_fib_rule_match()`, and `l3mdev_update_flow()`.

## Control Flow
Handler registration validates the l3mdev type and installs one callback under `l3mdev_lock`, rejecting duplicates with `-EBUSY`. Lookups copy the registered callback under the same lock and call it to map table ids to ifindexes. Device helpers use RCU lookup of net devices, climb upper-device links for slaves, and call master `l3mdev_ops` for FIB table or link-scope route lookups. `l3mdev_update_flow()` fills `flowi_l3mdev` from output or input interface and clears `flowi_oif` when the output interface itself is an L3 master so FIB lookup uses the master table instead of an oif match.

## State and Persistence
Runtime state consists of the global handler array protected by `l3mdev_lock`; per-device state lives in `net_device` flags and `l3mdev_ops`. Flow updates mutate `struct flowi` fields transiently during route lookup.

## Dependencies and Integration Points
The implementation depends on netdevice master/slave relationships, RCU device lookup, `net/l3mdev.h`, and FIB rule plumbing. It is used by VRF drivers and by IPv4/IPv6 route lookup paths to enforce per-L3-domain routing tables.

## Risks and Edge Cases
Several helpers require callers to hold RCU, and `l3mdev_link_scope_lookup()` warns if they do not. `l3mdev_ifindex_lookup_by_table_id()` calls driver callbacks while holding a spinlock, so callbacks must not sleep or re-enter registration. Const casts are used only to call upper-device RCU helpers, but changes to netdevice APIs could affect those assumptions. Incorrect `flowi_oif` clearing can route traffic through the wrong table.

## Test Signals
VRF route lookup tests should validate table selection for master and slave devices, link-local IPv6 lookup, FIB rule matching, and flow update behavior for input and output interfaces. Concurrency tests should cover handler register/unregister while route lookups run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/l3mdev/l3mdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/Kconfig -->
# sources/distributed-fs/ceph-client/net/lapb/Kconfig

## Purpose
This Kconfig entry exposes the LAPB data link driver used for reliable Link Access Procedure Balanced service, primarily as the lower data-link layer for X.25.

## Important APIs, Types, and Functions
The file defines the tristate symbol `LAPB`. Its help text describes LAPB as a reliable point-to-point data-link service and notes that Linux support is currently oriented around LAPB over Ethernet.

## Control Flow
The symbol controls whether the LAPB module is compiled. When enabled, the directory Makefile links the protocol implementation into `lapb.o`.

## State and Persistence
No runtime state exists in the Kconfig file. Its selected value persists as kernel configuration and determines whether the exported LAPB API is present.

## Dependencies and Integration Points
The symbol is intended for users of X.25/LAPB-over-Ethernet drivers and references `Documentation/networking/lapb-module.rst` for operational details.

## Risks and Edge Cases
Because the symbol is tristate and exports functions to device drivers, mismatched module/built-in configurations can affect link dependencies. Users may assume support for specialized X.21 hardware despite the help text noting Linux's Ethernet-oriented support.

## Test Signals
Build tests should cover `LAPB=n`, built-in, and module modes, plus dependent LAPB-over-Ethernet/X.25 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/Makefile -->
# sources/distributed-fs/ceph-client/net/lapb/Makefile

## Purpose
The Makefile builds the Linux LAPB layer as a single module/object from the protocol's state-machine components.

## Important APIs, Types, and Functions
`obj-$(CONFIG_LAPB) += lapb.o` ties the object to the Kconfig symbol. `lapb-y` lists `lapb_in.o`, `lapb_out.o`, `lapb_subr.o`, `lapb_timer.o`, and `lapb_iface.o`.

## Control Flow
There is no runtime flow. The object order groups input state-machine handling, output construction, helpers, timers, and exported interface code into one LAPB unit.

## State and Persistence
No state exists in the Makefile. It defines build composition only.

## Dependencies and Integration Points
All listed objects share `struct lapb_cb` and helper declarations from `net/lapb.h`, and the combined object exports LAPB registration/data APIs to network device code.

## Risks and Edge Cases
Omitting any listed object breaks cross-file references in the state machine. Adding objects should preserve protocol initialization and module ownership expectations.

## Test Signals
Build with `CONFIG_LAPB=m` and `CONFIG_LAPB=y` to catch unresolved LAPB symbols and module packaging regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_iface.c -->
# sources/distributed-fs/ceph-client/net/lapb/lapb_iface.c

## Purpose
`lapb_iface.c` is the public interface and lifetime manager for the LAPB protocol. It lets network devices register callbacks, controls LAPB parameters, handles connect/disconnect/data requests, dispatches inbound data to the state machine, and reacts to netdevice carrier/up/down events.

## Important APIs, Types, and Functions
Exported APIs include `lapb_register()`, `lapb_unregister()`, `lapb_getparms()`, `lapb_setparms()`, `lapb_connect_request()`, `lapb_disconnect_request()`, `lapb_data_request()`, and `lapb_data_received()`. Callback dispatch helpers include `lapb_connect_confirmation()`, `lapb_connect_indication()`, `lapb_disconnect_confirmation()`, `lapb_disconnect_indication()`, `lapb_data_indication()`, and `lapb_data_transmit()`. The file owns the global `lapb_list` protected by `lapb_list_lock`.

## Control Flow
Registration creates and initializes a `struct lapb_cb`, inserts it into `lapb_list`, starts T1, and associates it with a net device and callback table. Public operations find the control block by device, take its spinlock, then either mutate state or call cross-file helpers. Connect from state 0 starts link establishment and moves to state 1. Disconnect clears queues and sends DISC when connected. Data requests enqueue skb data to `write_queue` and call `lapb_kick()`. Received data is passed to `lapb_data_input()`. Netdevice notifier events start establishment on carrier-up for DTE mode, start T1 for DCE mode, disconnect before going down, and clear state/timers on down or carrier loss.

## State and Persistence
State is held in `struct lapb_cb`: device pointer, callbacks, T1/T2 timers, mode, window, state, sequence variables, queues, conditions, and refcount. The global list keeps one LAPB control block per device. There is no persistent storage beyond in-kernel protocol state.

## Dependencies and Integration Points
This file integrates with `net/lapb.h`, skbuff queues, kernel timers, netdevice notifier infrastructure, and device callbacks supplied by LAPB consumers. It only handles devices in `init_net` with `ARPHRD_X25` in its notifier path.

## Risks and Edge Cases
Unregister waits for references to drain while holding the list write lock, then synchronously deletes timers, so lifetime ordering matters. Parameter changes to mode/window are only allowed in state 0; timer values can change while active. Callback implementations own transmitted or indicated skb handling, making ownership semantics important. Device events are ignored outside `init_net`.

## Test Signals
Tests should register/unregister repeatedly under traffic, verify duplicate registration returns `LAPB_BADTOKEN`, exercise state transitions from connect/disconnect APIs and carrier changes, validate parameter bounds for normal and extended windows, and run with lockdep/KASAN to catch timer/refcount races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_iface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_in.c -->
# sources/distributed-fs/ceph-client/net/lapb/lapb_in.c

## Purpose
`lapb_in.c` implements the LAPB receive-side state machine. It decodes an incoming frame and dispatches it to one of five state handlers: disconnected, awaiting connection, awaiting release, connected, or frame-reject.

## Important APIs, Types, and Functions
The externally called entry point is `lapb_data_input()`. Internal handlers are `lapb_state0_machine()`, `lapb_state1_machine()`, `lapb_state2_machine()`, `lapb_state3_machine()`, and `lapb_state4_machine()`. They operate on `struct lapb_cb`, `struct sk_buff`, and decoded `struct lapb_frame` produced by `lapb_decode()`.

## Control Flow
State 0 responds to SABM/SABME only when the configured normal/extended mode matches, otherwise DM is sent; successful establishment resets sequence variables and raises connect indication. State 1 processes UA/DM responses to an outgoing SABM(E), confirming connection or refusal. State 2 processes release completion through UA/DM and rejects unexpected traffic. State 3 is data transfer: it handles reset SABM(E), DISC/DM disconnects, supervisory RR/RNR/REJ acknowledgments, I-frame receive/ack/reject behavior, FRMR reset, and illegal-frame transition to state 4. State 4 handles reset SABM(E) from frame-reject state. Each path frees or transfers skb ownership and calls `lapb_kick()` afterward to continue output.

## State and Persistence
The handler mutates LAPB state number, condition flags, retry count, sequence variables `vs`, `vr`, `va`, frame-reject metadata, and timers. The only durable effect is in-memory control block state and queued skb ownership.

## Dependencies and Integration Points
It relies on helpers from `lapb_subr.c` for decode, validation, queue management, control transmission, and FRMR generation; `lapb_out.c` for establishment, response, and retransmission; and `lapb_timer.c` for timer control. Upper-layer callbacks are reached through `lapb_data_indication()` and connection/disconnection indication helpers.

## Risks and Edge Cases
Frame ownership is subtle: I-frames successfully delivered to the upper layer are marked queued and not freed locally, while dropped indications intentionally skip protocol advancement so the peer retransmits. Sequence-number validation failure drives FRMR/state 4 behavior. Mode mismatch between SABM and SABME must not establish the wrong modulus. Missing `pskb_may_pull()` coverage is delegated to decode.

## Test Signals
Protocol tests should replay valid and invalid SABM/SABME, DISC, UA, DM, RR/RNR/REJ, I, FRMR, and illegal frames across all states. Include congestion/drop return from `data_indication`, normal vs extended modulus wrapping, reject-condition behavior, and timer interaction after state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_in.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_out.c -->
# sources/distributed-fs/ceph-client/net/lapb/lapb_out.c

## Purpose
`lapb_out.c` builds and transmits outbound LAPB I-frames and selected control responses. It moves queued user data into the transmit window, assigns sequence numbers, and starts retransmission timers.

## Important APIs, Types, and Functions
Key functions are `lapb_kick()`, `lapb_transmit_buffer()`, `lapb_establish_data_link()`, `lapb_enquiry_response()`, `lapb_timeout_response()`, `lapb_check_iframes_acked()`, and `lapb_check_need_response()`. The internal `lapb_send_iframe()` formats normal or extended I-frame control fields.

## Control Flow
`lapb_kick()` checks peer busy state, transmit window availability, and `write_queue` contents. It copies each original skb for transmission, sends the copy as an I-frame, advances `vs`, and queues the original skb on `ack_queue` until acknowledged. `lapb_transmit_buffer()` prepends the LAPB address byte according to DCE/DTE and MLP modes, then calls the registered `data_transmit` callback. Establishment sends SABM or SABME with poll set and starts T1. Enquiry and timeout responses send RR responses and clear pending-ack state.

## State and Persistence
This file mutates `vs`, condition flags, the write and ack queues, and T1 state. It does not persist data beyond skb queues and LAPB control block fields.

## Dependencies and Integration Points
It depends on skbuff queue APIs, callback dispatch through `lapb_data_transmit()`, control generation in `lapb_subr.c`, and timer helpers. The upper network device driver is responsible for actual frame transmission once the callback is invoked.

## Risks and Edge Cases
`skb_copy()` failure requeues the original skb and stalls additional sends. Transmit window arithmetic must match the selected modulus. Address-byte selection changes with DCE and MLP mode. Timer startup happens only when outstanding data exists and T1 is not already running; mistakes here affect retransmission.

## Test Signals
Validate window fill behavior, retransmit queue ordering, normal and extended header bytes, DCE/DTE address selection, MLP address selection, callback failure skb free behavior, and T1 startup when the first unacknowledged I-frame is sent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_subr.c -->
# sources/distributed-fs/ceph-client/net/lapb/lapb_subr.c

## Purpose
`lapb_subr.c` contains shared LAPB helpers for queue cleanup, acknowledgement processing, sequence validation, frame decoding, control-frame construction, and FRMR generation.

## Important APIs, Types, and Functions
Important helpers include `lapb_clear_queues()`, `lapb_frames_acked()`, `lapb_requeue_frames()`, `lapb_validate_nr()`, `lapb_decode()`, `lapb_send_control()`, and `lapb_transmit_frmr()`.

## Control Flow
Acknowledgment helpers remove acked skbs from `ack_queue` while advancing `va`, or requeue all unacknowledged frames back to `write_queue` in order for retransmission. `lapb_validate_nr()` walks the circular sequence interval from `va` to `vs`. `lapb_decode()` pulls address and control bytes from the skb, determines command/response direction based on DCE/DTE and MLP modes, and fills `struct lapb_frame` for normal or extended I/S/U formats. Control send helpers allocate small skbs, encode S/U control fields, and pass them to `lapb_transmit_buffer()`.

## State and Persistence
State changes are limited to queue contents, `va`, and skb data pointers. FRMR construction uses `lapb->frmr_data`, `frmr_type`, `vs`, and `vr` captured by the input state machine.

## Dependencies and Integration Points
The file underpins both receive and timer paths. It depends on `pskb_may_pull()` for safe header access, skbuff queue operations, LAPB constants from `net/lapb.h`, and `lapb_transmit_buffer()` from the output path.

## Risks and Edge Cases
Decode must not read beyond skb linear data, and it must pull the correct number of bytes for normal versus extended formats. Command/response derivation is mode-sensitive and affects protocol legality. Circular sequence validation is central to avoiding false FRMR or missed acknowledgments. Requeue ordering must preserve retransmit order.

## Test Signals
Unit-style frame decode tests should cover all address modes, normal/extended I/S/U frames, short skbs, invalid controls, and command/response classification. Queue tests should validate ack removal and retransmit requeue order across sequence wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_timer.c -->
# sources/distributed-fs/ceph-client/net/lapb/lapb_timer.c

## Purpose
`lapb_timer.c` implements LAPB T1 and T2 timer management. T1 handles establishment, release, retransmission, and frame-reject retry. T2 delays receive acknowledgments so RR responses can be coalesced.

## Important APIs, Types, and Functions
Externally used helpers are `lapb_start_t1timer()`, `lapb_start_t2timer()`, `lapb_stop_t1timer()`, `lapb_stop_t2timer()`, and `lapb_t1timer_running()`. Internal callbacks are `lapb_t1timer_expiry()` and `lapb_t2timer_expiry()`.

## Control Flow
Start helpers delete any existing timer instance, install the callback, set expiry relative to `jiffies`, mark the running flag, and add the timer. T2 expiry checks that it is still the active timer and, if an ACK is pending, clears the flag and sends `lapb_timeout_response()`. T1 expiry switches on LAPB state: state 0 DCE may send DM before establishing; state 1 resends SABM(E) or times out; state 2 resends DISC or confirms timeout; state 3 requeues and retransmits I-frames or disconnects on retry exhaustion; state 4 retransmits FRMR or disconnects on retry exhaustion. Most non-terminal paths restart T1.

## State and Persistence
The file mutates timer running flags, retry count, state, queues, and condition flags indirectly through helper calls. All state is in-memory within `struct lapb_cb`.

## Dependencies and Integration Points
Timer callbacks lock `lapb->lock` with bottom halves disabled and call helpers from interface, output, and subroutine files. The unregister path synchronizes timer deletion to prevent callbacks from using freed control blocks.

## Risks and Edge Cases
Running flags are separate from kernel timer pending state; both are checked to avoid handling stale callbacks. Retry exhaustion semantics differ by state and must match LAPB expectations. Timer callbacks can race with stop/start paths and unregister, making lock and `timer_delete_sync()` usage important.

## Test Signals
Tests should simulate T1/T2 expiry in every LAPB state, verify N2 retry boundaries, assert correct indications/confirmations on timeout, check stale timer callbacks are ignored after stop/restart, and use lockdep/KASAN during unregister with timers active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/lapb/lapb_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/Kconfig -->
# sources/distributed-fs/ceph-client/net/llc/Kconfig

## Purpose
This Kconfig file defines the base LLC support symbol and the user-visible LLC type 2 socket support symbol.

## Important APIs, Types, and Functions
`LLC` is a tristate base symbol without a prompt. `LLC2` is a tristate prompt for ANSI/IEEE 802.2 LLC type 2 support and selects `LLC`.

## Control Flow
The configuration controls compilation of the base LLC object and the LLC2 connection-oriented/socket object. Selecting LLC2 makes PF_LLC sockets available through the corresponding source files.

## State and Persistence
No runtime state exists here. Kconfig state determines build output and module availability.

## Dependencies and Integration Points
`LLC2` integrates with PF_LLC sockets, LLC station/SAP/connection code, procfs, and sysctl support depending on other kernel symbols.

## Risks and Edge Cases
Because `LLC` is selected by `LLC2`, base LLC may be built without a direct prompt. Build and packaging logic should not assume LLC2 is always present when LLC core exists.

## Test Signals
Build tests should cover LLC core only where selected by other users, LLC2 as built-in, LLC2 as module, and proc/sysctl combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/Makefile -->
# sources/distributed-fs/ceph-client/net/llc/Makefile

## Purpose
The LLC Makefile composes the base 802.2 LLC layer and the connection-oriented LLC2 support object.

## Important APIs, Types, and Functions
`obj-$(CONFIG_LLC) += llc.o` builds core LLC from `llc_core.o`, `llc_input.o`, and `llc_output.o`. `obj-$(CONFIG_LLC2) += llc2.o` builds LLC2 from interface, event, action, connection, state-table, PDU, SAP, station, and socket files. Optional `llc_proc.o` and `sysctl_net_llc.o` are included under `CONFIG_PROC_FS` and `CONFIG_SYSCTL`.

## Control Flow
No runtime flow exists. The object lists determine which implementation pieces are linked into the LLC and LLC2 modules/objects.

## State and Persistence
No state is stored here. It affects build-time composition only.

## Dependencies and Integration Points
The Makefile ties together the state machine files (`llc_c_ev.o`, `llc_c_ac.o`, `llc_c_st.o`), PF_LLC socket API (`af_llc.o`), SAP/station support, PDU helpers, and optional observability/control files.

## Risks and Edge Cases
The LLC2 state machine relies on all listed objects; omitting one produces unresolved symbols or runtime feature gaps. Optional proc/sysctl objects must remain conditional to avoid build failures when those subsystems are disabled.

## Test Signals
Compile with LLC/LLC2 as built-in and modules, and with procfs/sysctl enabled and disabled, to catch object-list regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/af_llc.c -->
# sources/distributed-fs/ceph-client/net/llc/af_llc.c

## Purpose
`af_llc.c` implements the PF_LLC socket user interface. It supports connectionless LLC class 1 through `SOCK_DGRAM` and connection-oriented LLC2 through `SOCK_STREAM`, including bind, autobind, connect, listen, accept, send, receive, shutdown, and socket options.

## Important APIs, Types, and Functions
The file defines `llc_proto`, `llc_ui_family_ops`, and `llc_ui_ops`. Major functions include `llc_ui_create()`, `llc_ui_release()`, `llc_ui_bind()`, `llc_ui_autobind()`, `llc_ui_connect()`, `llc_ui_listen()`, `llc_ui_accept()`, `llc_ui_sendmsg()`, `llc_ui_recvmsg()`, `llc_ui_shutdown()`, `llc_ui_setsockopt()`, and `llc_ui_getsockopt()`. Helpers manage dynamic SAP allocation, link numbers, waits for connection/disconnect/busy conditions, packet-info control messages, and LLC header sizing.

## Control Flow
Create checks `CAP_NET_RAW`, rejects non-init network namespaces, and allocates an `llc_sock`. Bind resolves an Ethernet device and SAP, opens or finds the SAP, checks address conflicts, stores device/local address, and inserts the socket into the SAP. Connect requires stream sockets, autobinds if needed, stores destination address, sends SABME through `llc_establish_connection()`, and optionally waits for state to leave `TCP_SYN_SENT`. Listen marks a bound stream socket as `TCP_LISTEN`. Accept dequeues child sockets from the listener receive queue and grafts them to the new socket. Send builds an skb sized to device MTU and dispatches UI, TEST, XID, or LLC2 data. Receive implements stream-style byte consumption or datagram one-packet delivery with optional source address and packet-info cmsg.

## State and Persistence
State lives in `struct llc_sock` and `struct sock`: SAP pointer, device and netdev tracker, local/destination LLC addresses, copied receive sequence, LLC2 timers/options, socket state, and receive queues. Dynamic SAP and link counters are static process-wide kernel state.

## Dependencies and Integration Points
The file integrates with LLC SAP/connection handlers, PDU builders, netdevice lookup, socket core, proc/sysctl initialization, and packet dispatch registration through `llc_add_pack()`. It restricts operation to `init_net`.

## Risks and Edge Cases
Socket lifetime is complex: release may send DISC, wait, remove from SAP, hold SAP across `release_sock()`, drop netdev references, orphan, and free the LLC socket. Send temporarily drops the socket lock while allocating skb and revalidates device/header/MTU assumptions afterward. Autobind modifies the user-provided sockaddr. Namespace restriction and CAP_NET_RAW checks are intentional security boundaries.

## Test Signals
Exercise bind/autobind with fixed and dynamic SAPs, address conflict detection, datagram UI/TEST/XID send, stream connect/listen/accept/send/recv/shutdown, nonblocking connect and send-busy waits, cmsg packet-info, release during active connection, and init_net/CAP_NET_RAW rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/af_llc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_c_ac.c -->
# sources/distributed-fs/ceph-client/net/llc/llc_c_ac.c

## Purpose
`llc_c_ac.c` implements LLC2 connection-component actions executed by the connection state table. Each action takes a socket and event skb, mutates connection state, emits PDUs, starts/stops timers, or reports primitives back to upper layers.

## Important APIs, Types, and Functions
The file exports many `llc_conn_ac_*` action functions plus timer callbacks `llc_conn_pf_cycle_tmr_cb()`, `llc_conn_busy_tmr_cb()`, `llc_conn_ack_tmr_cb()`, and `llc_conn_rej_tmr_cb()`. Important categories include primitive indication/confirmation (`conn`, `data`, `disc`, `rst`), PDU send helpers for DISC/DM/FRMR/I/REJ/RNR/RR/SABME/UA, busy and poll flag manipulation, ack aggregation (`ack_must_be_send`, `ack_pf`, `npta`), transmit window adjustments, sequence updates (`vS`, `vR`, `last_nr`, `X`), and timer control.

## Control Flow
State-table matches call these actions in configured order. PDU actions allocate frames with `llc_alloc_frame()`, initialize LLC headers and PDU-specific fields, build MAC headers, then send through `llc_conn_send_pdu()`. Data I-frame sends increment `vS` and hold an skb reference for transmit/accounting. Ack-update paths remove acknowledged PDUs, restart or stop ack timers, and emit data confirmations when a previously failed data request becomes sendable. Timer callbacks allocate zero-length event skbs, set the event type, and either process the event immediately or queue it to socket backlog if userspace owns the socket lock.

## State and Persistence
All state is in `struct llc_sock`: sequence numbers, retry count, busy flag, poll flag, send-state flags, cause/data flags, transmit window `k`, receive window `rw`, unacknowledged queue, timers, stored rejected header, and socket wakeups. No persistent storage is used.

## Dependencies and Integration Points
The action layer depends on `llc_conn_state_process()`, LLC PDU helpers, SAP state, socket wakeups, skbuff queues, timers, and netdevice MAC header creation. It is tightly coupled to `llc_c_st.c` state tables and `llc_c_ev.c` event predicates.

## Risks and Edge Cases
Many functions allocate skb frames in atomic contexts and must free on MAC-header failure. Timer event processing must not run state transitions while userspace owns the socket, hence backlog queuing. Sequence/window math is modulo `LLC_2_SEQ_NBR_MODULO`. Some functions return `0` despite internal send failures or contain legacy comments, so callers rely on state-table semantics rather than strict errno propagation.

## Test Signals
State-machine tests should cover every PDU action, timer callback, retry-count boundary, p/f flag clearing and socket wakeup, remote-busy handling, ack aggregation thresholds, transmit window increase/decrease, FRMR resend, loopback behavior, and allocation-failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_c_ac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_c_ev.c -->
# sources/distributed-fs/ceph-client/net/llc/llc_c_ev.c

## Purpose
`llc_c_ev.c` implements LLC2 connection event matchers and qualifiers used by the connection state machine. Matchers identify primitives, timer events, PDU types, sequence-number conditions, and generic command/response classes; qualifiers check connection flags and set status values.

## Important APIs, Types, and Functions
Primitive matchers include `llc_conn_ev_conn_req()`, `llc_conn_ev_data_req()`, `llc_conn_ev_disc_req()`, and `llc_conn_ev_rst_req()`. PDU matchers cover DISC, DM, FRMR, I command/response variants, REJ/RNR/RR supervisory variants, SABME, UA, generic command/response, and invalid N(R)/N(S) cases. Timer matchers include `llc_conn_ev_p_tmr_exp()`, `llc_conn_ev_ack_tmr_exp()`, `llc_conn_ev_rej_tmr_exp()`, and `llc_conn_ev_busy_tmr_exp()`. Qualifiers check `data_flag`, `p_flag`, `remote_busy_flag`, retry count vs `n2`, `s_flag`, `cause_flag`, transmit-window last-frame conditions, and set status codes.

## Control Flow
The state machine passes an event skb to matcher functions until one returns `0`. PDU matchers inspect LLC headers through `llc_pdu_*` helpers and compare command/response bits, PDU type, poll/final bits, sequence numbers, and receive-space availability. Invalid sequence helpers use circular-window checks to distinguish unexpected-but-in-window from invalid/out-of-window cases. Qualifiers run after a match to enforce flag conditions or annotate the event with a status used by confirmation actions.

## State and Persistence
The file mostly reads state from `struct llc_sock`: `vR`, `vS`, receive window `rw`, transmit window `k`, unacknowledged queue, flags, retry count, and device flags. Qualifier status setters mutate only the transient `llc_conn_state_ev` embedded in the event skb.

## Dependencies and Integration Points
It depends on LLC PDU header accessors, `llc_circular_between()` from the action file, connection-space checks, skbuff queues, and the generated/static LLC connection state tables. Debug prints expose matched invalid sequence cases.

## Risks and Edge Cases
Return convention is inverted from typical predicates: `0` means matched/success and `1` means no match/failure. The receive-window helper also returns negated circular-check results, so maintainers must be careful when changing sequence logic. Loopback skips transmit-window validation in `llc_util_nr_inside_tx_window()`. Matchers assume the skb contains the correct PDU header type for the state-table context.

## Test Signals
Tests should feed crafted LLC PDUs to every matcher, especially boundary sequence numbers around modulo wrap, invalid N(R)/N(S), poll/final bit variants, full receive-space behavior, loopback transmit-window behavior, and all qualifier status-setting functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_c_ev.c -->
