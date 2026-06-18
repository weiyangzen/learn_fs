# subset-b-006301

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-core.c -->
# sources/distributed-fs/ceph-client/net/wireless/wext-core.c

Purpose: implements the Wireless Extensions core: standard ioctl metadata, rtnetlink wireless event emission, handler lookup, userspace copy wrappers, compat ioctl translation, and stream helpers used by scan/range formatters.

Important APIs/functions: exported `wireless_send_event()`, `wireless_nlevent_flush()`, `get_wireless_stats()`, `wext_handle_ioctl()`, compat `compat_wext_handle_ioctl()`, and `iwe_stream_add_event/point/value()` are the main public surfaces. Internal dispatch pivots through `standard_ioctl[]`, `standard_event[]`, `get_handler()`, `ioctl_standard_iw_point()`, `ioctl_standard_call()`, `wireless_process_ioctl()`, and `wext_ioctl_dispatch()`.

Control flow: event senders validate the command against standard ioctl/event descriptions, size variable payloads, package `IFLA_WIRELESS` into an `RTM_NEWLINK` skb, add a 32-bit compat skb as `frag_list` when needed, enqueue on `net->wext_nlevents`, and schedule work to flush via rtnetlink. Ioctls copy an `iwreq`, check CAP_NET_ADMIN for setters and key reads, resolve the netdev under RTNL, handle stats/private special cases, find cfg80211 or legacy handlers, marshal fixed or point payloads, call handlers, optionally call commit, send events for mutating commands, and copy GET results back.

State and persistence: state is per-net pending event queues plus transient ioctl buffers. Driver/cfg80211 state is reached through handler callbacks. Stats reads may clear `IW_QUAL_*_UPDATED`. WEXT is deliberately disabled for MLO or `WIPHY_FLAG_DISABLE_WEXT` devices, and cfg80211 users receive a one-time deprecation warning.

Dependencies and integration: integrates netdevice notifier ordering, pernet lifecycle, rtnetlink, cfg80211 WEXT compatibility, legacy `iw_handler_def`, Linux capabilities, usercopy, and compat ABI layouts. Stream helpers are consumed by drivers/cfg80211 when composing Wireless Extension result buffers.

Risks and test signals: variable-length `iw_point` paths carry the most risk: ESSID NUL compatibility, NOMAX allocation, encode-ext key length checks, restricted event payload suppression, and 32/64-bit layout differences. Tests should cover invalid token counts, SET/GET copy faults, CAP_NET_ADMIN denial, cfg80211 disabled/MLO rejection, event queue flushing across netdevice state changes, compat event consumers, and scan/stats/range commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-priv.c -->
# sources/distributed-fs/ceph-client/net/wireless/wext-priv.c

Purpose: implements Wireless Extensions private ioctl support for legacy drivers, including private command discovery, argument sizing, userspace copy wrappers, and compat `iw_point` translation.

Important APIs/functions: `iw_handler_get_private()` returns the driver `iw_priv_args` table for `SIOCGIWPRIV`; `ioctl_private_call()` and `compat_private_call()` invoke private handlers. Helpers `get_priv_size()`, `adjust_priv_size()`, `get_priv_descr_and_size()`, and `ioctl_private_iw_point()` compute inline versus extra-buffer payload handling.

Control flow: `SIOCGIWPRIV` validates that private metadata exists and either returns `-E2BIG` with the needed count or copies the table into the core-allocated extra buffer. Private dispatch searches the driver private descriptor matching the command, derives SET or GET payload size, treats fixed arguments fitting in `ifr_name` as inline, otherwise allocates an extra buffer, copies SET data from userspace, calls the driver handler, adjusts variable GET return size, and copies results back.

State and persistence: no durable state is owned here. The code reads driver-provided private descriptor arrays and may trigger `call_commit_handler()` when a private handler returns `-EIWCOMMIT`.

Dependencies and integration: called from `wext-core.c` under RTNL and permission checks. It depends on `net_device->wireless_handlers`, `struct iw_priv_args` encoding, WEXT private ioctl numbering, usercopy helpers, and optional compat support.

Risks and test signals: the private ABI is descriptor-driven and fragile when drivers misdeclare fixed/variable sizes or sub-ioctl names. Tests should cover `SIOCGIWPRIV` sizing hints, inline fixed arguments, pointer payload SET/GET, variable-length GET truncation, invalid or missing descriptors, compat pointer conversion, and commit-handler propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-priv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-proc.c -->
# sources/distributed-fs/ceph-client/net/wireless/wext-proc.c

Purpose: exposes `/proc/net/wireless`, a seq_file view of Wireless Extensions statistics for each wireless-capable network device in a network namespace.

Important APIs/functions: `wext_proc_init()` creates the proc entry, `wext_proc_exit()` removes it, and seq callbacks `wireless_dev_seq_start/next/stop/show()` walk netdevices under RTNL. `wireless_seq_printf_stats()` formats `struct iw_statistics`.

Control flow: opening the proc file uses the net namespace embedded by `proc_create_net()`. The seq iterator locks RTNL, emits a fixed header at `SEQ_START_TOKEN`, then visits each netdev. For each device, it asks `get_wireless_stats()` for live stats; if unavailable but the device advertises wireless handlers or an `ieee80211_ptr`, it prints a zeroed row so wireless devices remain visible.

State and persistence: proc output is generated on demand. A successful live stats read clears `IW_QUAL_ALL_UPDATED`; the static null stats row is never used to mutate driver state.

Dependencies and integration: depends on procfs, seq_file, per-net proc directories, netdevice iteration, and the WEXT stats helper in `wext-core.c`.

Risks and test signals: this is mostly diagnostic, but locking and side effects matter. Tests should validate namespace-specific `/proc/net/wireless`, header formatting, wireless devices with missing stats, clearing updated flags, RTNL-protected device removal during reads, and builds without legacy WEXT or cfg80211 stats providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-sme.c -->
# sources/distributed-fs/ceph-client/net/wireless/wext-sme.c

Purpose: provides cfg80211 managed-mode compatibility handlers for WEXT station operations: connect, channel/frequency, ESSID, BSSID/AP, generic IE, and MLME deauth/disassoc.

Important APIs/functions: `cfg80211_mgd_wext_connect()` builds a cfg80211 connect request from cached WEXT state. Setter/getters include `cfg80211_mgd_wext_siwfreq/giwfreq()`, `cfg80211_mgd_wext_siwessid/giwessid()`, `cfg80211_mgd_wext_siwap/giwap()`, `cfg80211_wext_siwgenie()`, and `cfg80211_wext_siwmlme()`.

Control flow: setters validate station interface type, translate WEXT values, disconnect an existing connection when changing channel/SSID/BSSID/IE, update `wdev->wext.connect`, and call `cfg80211_connect()` when there is a non-empty SSID and the netdev is running. Connect duplicates cached keys when a default key implies privacy, preserves previous BSSID when valid, sets default background scan period, and transfers the cached IE pointer/length.

State and persistence: WEXT compatibility state lives in `wireless_dev->wext`: SSID, BSSID, IE, cached keys, previous BSSID, default key, and connect parameters. No durable persistence exists beyond the in-memory wireless device. Multi-link connections are rejected for legacy getters.

Dependencies and integration: bridges WEXT handlers into cfg80211/nl80211 station management and uses cfg80211 connect/disconnect APIs, wiphy locking, RCU BSS element access, Ethernet address helpers, and ARPHRD_ETHER validation.

Risks and test signals: correctness depends on keeping WEXT state synchronized with cfg80211 connection state and avoiding misleading events during immediate reconnects. Tests should cover station-only enforcement, disabled channels, NUL-terminated SSIDs, automatic versus fixed BSSID, IE replacement/freeing, connection while netdev down, cached WEP keys, MLO getter rejection, and MLME reason-code disconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/wext-sme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/Kconfig -->
# sources/distributed-fs/ceph-client/net/x25/Kconfig

Purpose: defines `CONFIG_X25`, the build-time option for the Linux CCITT X.25 Packet Layer Protocol implementation.

Important symbols: `X25` is a tristate option named "CCITT X.25 Packet Layer". Its help text explains virtual circuits, PLP versus LAPB, WAN use cases, and the module name `x25`.

Control flow: Kconfig selection determines whether the `net/x25` packet-layer objects are built into the kernel, built as a module, or excluded. There are no subordinate options in this file; optional sysctl support is controlled by global `CONFIG_SYSCTL` in the Makefile.

State and persistence: the selected value persists in the kernel configuration and controls protocol availability, module packaging, and whether AF_X25 can be registered at runtime.

Dependencies and integration: integrates with the networking Kconfig tree and relies on related lower-layer choices such as LAPB and X.25 async or LAPB-over-Ethernet drivers, documented in `Documentation/networking/x25*.rst`.

Risks and test signals: the main risk is discoverability or build mismatch with the Makefile/module help. Test signals are `all{yes,mod,no}config`, randconfig builds with and without LAPB drivers, and confirming `CONFIG_X25=m` produces module `x25`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/Makefile -->
# sources/distributed-fs/ceph-client/net/x25/Makefile

Purpose: maps `CONFIG_X25` to the packet-layer object set and conditionally includes sysctl support.

Important build mappings: `obj-$(CONFIG_X25) += x25.o`; `x25-y` aggregates `af_x25.o`, device, facilities, input, link, output, route, subroutine, timer, proc, and forwarding files. `x25-$(CONFIG_SYSCTL)` adds `sysctl_net_x25.o`.

Control flow: kbuild links all listed `x25-y` objects into the built-in or modular `x25.o` target. The sysctl object is included only when both X.25 and generic sysctl support are enabled.

State and persistence: no runtime state is managed here. The file is the persistent build contract for module contents and must remain synchronized with code references and Kconfig help.

Dependencies and integration: aligns with the AF_X25 module initialization in `af_x25.c`, optional `/proc/sys/net/x25` registration in `sysctl_net_x25.c`, and proc diagnostics in `x25_proc.c`.

Risks and test signals: missing objects cause unresolved symbols or silently absent features. Tests should include `CONFIG_X25=y/m`, `CONFIG_SYSCTL=y/n`, module load/unload, and symbol resolution for route/link/proc/forwarding helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/af_x25.c -->
# sources/distributed-fs/ceph-client/net/x25/af_x25.c

Purpose: implements the AF_X25 `SOCK_SEQPACKET` socket family, global socket list, address conversion, call setup/acceptance, userspace send/receive, X.25 ioctls, netdevice integration, and module lifecycle.

Important APIs/functions: externally used helpers include `x25_parse_address_block()`, `x25_addr_ntoa()`, `x25_addr_aton()`, `x25_find_socket()`, `x25_rx_call_request()`, `x25_destroy_socket_from_timer()`, and `x25_kill_by_neigh()`. Socket operations include `x25_create()`, `x25_bind()`, `x25_connect()`, `x25_listen()`, `x25_accept()`, `x25_release()`, `x25_sendmsg()`, `x25_recvmsg()`, `x25_ioctl()`, and compat ioctl support.

Control flow: outbound sockets must bind, route a destination, get a neighbour, choose an LCI, send `X25_CALL_REQUEST`, and wait for state 3/TCP_ESTABLISHED unless nonblocking. Incoming call requests parse addresses, facilities, and call user data, find a listener by address/CUD, optionally forward, negotiate facilities, create a child socket, optionally send `CALL_ACCEPTED`, queue it for `accept()`, and start heartbeat. Send builds data or interrupt packets, handles optional Q-bit-included payloads, queues through `x25_output()`, and kicks transmit. Receive strips PLP headers, restores optional Q-bit byte, and returns record-oriented data.

State and persistence: global `x25_list` tracks bound/connected sockets under `x25_list_lock`. Per-socket state includes addresses, neighbour reference, LCI, PLP state, timers, facilities, DTE facilities, call user data, cause/diagnostic, queues, sequence variables, and flags. Runtime sysctl defaults seed new sockets; no durable persistence exists.

Dependencies and integration: integrates Linux proto registration, `sock_register(AF_X25)`, packet type `ETH_P_X25`, netdevice notifier events, route/neighbour/facilities/timer/proc/sysctl helpers, capabilities for route/subscription ioctls, and init_net-only operation.

Risks and test signals: important risks are reference lifetime for neighbours/routes/sockets, partial usercopy paths, listen queue ownership via `skb->sk`, state transitions during signals/nonblocking connect, and ioctl validation for facilities and CUD matching. Tests should cover bind validation, route lookup, connect timeout/refusal, incoming call accept approval, forwarding fallback, Q-bit send/recv, OOB interrupts, clear/reset races, device down cleanup, compat ioctls, and module unload with live references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/af_x25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/sysctl_net_x25.c -->
# sources/distributed-fs/ceph-client/net/x25/sysctl_net_x25.c

Purpose: registers `/proc/sys/net/x25` runtime tunables for X.25 packet-layer timers and forwarding.

Important APIs/functions: `x25_register_sysctl()` registers the table under `init_net`; `x25_unregister_sysctl()` unregisters it. Table entries back `sysctl_x25_restart_request_timeout`, call/reset/clear request timeouts, ack holdback timeout, and `sysctl_x25_forward`.

Control flow: module init calls registration after netdevice notifier setup; module exit unregisters. Timer entries use `proc_dointvec_minmax` with 1 second to 300 second jiffy bounds; forwarding uses `proc_dointvec` without min/max.

State and persistence: sysctl writes mutate global integers used by new sockets/neighbours and forwarding decisions. Values are runtime-only and not persisted by this file.

Dependencies and integration: depends on Linux sysctl infrastructure and globals defined in `af_x25.c`. The forwarding flag gates `x25_forward_call()` use in incoming call handling.

Risks and test signals: `x25_forward` accepts any integer, so callers treat nonzero as enabled. Tests should cover table presence with `CONFIG_SYSCTL`, boundary rejection for timer values, module unload cleanup, and behavior changes for new sockets after sysctl writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/sysctl_net_x25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_dev.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_dev.c

Purpose: bridges X.25 Packet Layer Protocol frames to and from X.25 netdevices and LAPB-style interface messages.

Important APIs/functions: `x25_lapb_receive_frame()` is the packet-type receive hook. Helpers `x25_receive_data()`, `x25_establish_link()`, and `x25_send_frame()` dispatch PLP frames, request lower-layer connection, and transmit frames with the one-byte X.25 interface prefix.

Control flow: receive copies the incoming skb, rejects non-init_net devices, locates an `x25_neigh`, strips interface type, and routes `DATA`, `CONNECT`, and `DISCONNECT` indications. PLP data with LCI 0 goes to link control; known LCI frames go to the socket state machine or backlog; call requests go to `x25_rx_call_request()`; otherwise forwarding is attempted and clear confirmations tear down forwarding entries.

State and persistence: this file owns no durable state; it mutates skb ownership and consumes or forwards frames. Neighbour state is updated through `x25_link_established()` and `x25_link_terminated()`.

Dependencies and integration: depends on packet type registration in `af_x25.c`, neighbour lookup in `x25_link.c`, socket lookup/state processing, forwarding, and netdevice transmit via `dev_queue_xmit()`.

Risks and test signals: skb ownership is subtle because successful socket processing keeps the skb while failures must free it. Tests should cover unknown devices, short frames, link connect/disconnect indications, LCI 0 restart/diagnostic frames, incoming call requests, forwarding paths, and malformed frame drops without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_facilities.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_facilities.c

Purpose: parses, creates, negotiates, and link-limits X.25 facilities, including reverse charging, throughput, packet/window size, and DTE address-extension facilities.

Important APIs/functions: `x25_parse_facilities()`, `x25_create_facilities()`, `x25_negotiate_facilities()`, and `x25_limit_facilities()` are used by call request/accept and connection setup.

Control flow: parsing validates the declared facilities length, walks class A/B/C/D encodings, updates regular and DTE facility structs, and records a VC facility mask. Creation emits a length-prefixed facility block based on a mask and current socket values, including DTE marker/service encodings. Negotiation copies local defaults, parses peer requests, rejects unacceptable reverse charging, negotiates throughput and packet/window values downward, then returns the consumed facility length.

State and persistence: functions mutate caller-provided `x25_facilities`, `x25_dte_facilities`, and VC mask fields. Per-socket accepted values persist in `x25_sock`; no global state is owned.

Dependencies and integration: used by `af_x25.c` for incoming calls, by `x25_in.c` for call accepted frames, and by `x25_subr.c` when generating call packets. It relies on X.25 constants and skb pull validation.

Risks and test signals: malformed length fields and variable class-D encodings are high-risk. Tests should cover empty facilities, all known classes, unknown facility logging, too-short class encodings, DTE AE length limits, reverse charging rejection, extended versus standard window clamping, and generated facility byte-for-byte round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_facilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_forward.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_forward.c

Purpose: implements simple X.25 call/data forwarding between devices when no local listener accepts an incoming call.

Important APIs/functions: `x25_forward_call()` routes and records a forwarded LCI pair, `x25_forward_data()` forwards later packets by LCI, and `x25_clear_forward_by_lci()` / `x25_clear_forward_by_dev()` remove forwarding state.

Control flow: call forwarding finds a route for the destination, gets the outgoing neighbour, rejects loops where the route returns to the ingress device, checks for duplicate LCI entries, records device pairs in `x25_forward_list`, clones the call skb, and transmits it on the new neighbour. Data forwarding finds the opposite device for the LCI, gets its neighbour, copies the skb, and sends it.

State and persistence: forwarding state is a runtime global list of `x25_forward` entries protected by `x25_forward_list_lock`; entries are removed on clear confirmation, device removal, or neighbour kill.

Dependencies and integration: called from `x25_dev.c` and `af_x25.c`, gated by `sysctl_x25_forward`, and depends on route and neighbour lookup plus `x25_transmit_link()`.

Risks and test signals: forwarding keys only on LCI and device pair, so duplicate LCIs and loop avoidance are important. Tests should cover no-route, same-device route, allocation/clone failures, bidirectional data forwarding, clear-confirmation cleanup, device down cleanup, and proc display of active forwards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_forward.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_in.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_in.c

Purpose: implements the X.25 Packet Layer receive state machine for connection establishment, connected data transfer, reset, clear, interrupt handling, and accept-approval pending state.

Important APIs/functions: `x25_process_rx_frame()` is the main receive dispatcher and `x25_backlog_rcv()` is the socket backlog callback. Internal state handlers cover states 1 through 5, and `x25_queue_rx_frame()` handles M-bit fragmentation reassembly.

Control flow: receive decodes frame type/sequence bits with `x25_decode()`, dispatches by `x25->state`, then calls `x25_kick()`. State 1 processes call accepted, call collision, and clear. State 2 waits for clear confirmation. State 3 handles reset, clear, RR/RNR acknowledgements, DATA sequence validation and receive queuing, delayed acknowledgements, and interrupts. State 4 waits for reset confirmation. State 5 waits for explicit call-accepted approval while accepting clear requests.

State and persistence: mutates PLP state, `vs/vr/va/vl`, condition flags, socket state/error, receive and fragment queues, interrupt queues, timers, facilities, call user data, and cause/diagnostic fields. Reassembled records persist on `sk_receive_queue` until userspace receives them.

Dependencies and integration: depends on subroutines for frame decoding, queue clearing, acknowledgement, reset/clear generation, and disconnect; on timers for T2/T22/T23; and on `x25_out.c` for kick/enquiry response.

Risks and test signals: sequence-number validation and fragment reassembly are critical. Tests should cover standard and extended modulus, out-of-order DATA triggering reset, invalid `nr`, full receive buffer setting RNR, fragmented packets over USHRT_MAX, interrupt inline and out-of-band modes, clear/reset races in every state, and malformed short frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_in.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_link.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_link.c

Purpose: manages X.25 neighbours and link-level restart/control behavior for X.25 netdevices.

Important APIs/functions: `x25_link_control()`, `x25_transmit_link()`, `x25_link_established()`, `x25_link_terminated()`, `x25_link_device_up()`, `x25_link_device_down()`, `x25_get_neigh()`, `x25_subscr_ioctl()`, and `x25_link_free()` are the main surfaces.

Control flow: neighbour creation initializes link queue, T20 timer, default facility mask, standard sequencing, and device reference. `x25_transmit_link()` queues frames while link state is down/restarting and starts lower-layer establishment; link establishment sends restart request and starts T20; restart confirmations transition to state 3 and flush queued frames; restart requests in established state kill existing virtual calls and reply. Link termination purges queued frames, stops T20, and kills dependent sockets.

State and persistence: global `x25_neigh_list` is protected by `x25_neigh_list_lock`; each neighbour stores device reference, link state, queue, extended-mode flag, global facility mask, T20, timer, and refcount.

Dependencies and integration: integrates netdevice notifier callbacks from `af_x25.c`, device transmit helpers in `x25_dev.c`, socket cleanup via `x25_kill_by_neigh()`, subscriptions ioctls, and sysctl default T20.

Risks and test signals: link state and refcounting interact with device unregister. Tests should cover device up/down, duplicate device registration assumptions, restart request/confirmation state transitions, T20 retransmission, queued-frame flushing, subscription get/set including extended flag validation, and teardown with active sockets/routes/forwards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_out.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_out.c

Purpose: handles outbound X.25 data fragmentation, transmit window scheduling, interrupt transmission, and acknowledgement/enquiry responses.

Important APIs/functions: `x25_output()` queues user data frames and fragments by negotiated packet size; `x25_kick()` transmits queued data subject to peer busy and window limits; `x25_enquiry_response()` sends RR/RNR based on receive-buffer state.

Control flow: `x25_output()` compares user data length to negotiated packet size, preserves the header, splits data into packet-size chunks, sets the M bit on all but the final fragment, and queues frames on `sk_write_queue`. `x25_kick()` sends one pending interrupt if allowed, skips data when peer RNR is set, computes the send window from `va`, `vs`, and `winsize_out`, clones each queued skb for transmission, updates `vs`, and moves originals to `ack_queue` for retransmission until acknowledged.

State and persistence: mutates write queue, ack queue, interrupt queue, sequence variables, `X25_INTERRUPT_FLAG`, and ACK pending condition. Unacknowledged frames persist in `ack_queue` until `x25_frames_acked()` frees them.

Dependencies and integration: used by `af_x25.c` sendmsg and `x25_in.c` receive processing. Relies on link transmit, socket memory ownership, negotiated facilities, timers, and subroutine acknowledgement helpers.

Risks and test signals: fragmentation and window accounting are high-risk, especially nonblocking allocation returning partial bytes sent. Tests should cover standard/extended headers, M-bit fragmentation, pacsize defaults, peer busy suppression, interrupt confirmation gating, clone failure requeue, ACK queue retransmission after reset, and delayed ACK clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_proc.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_proc.c

Purpose: exposes X.25 diagnostic procfs files for routes, sockets, and forwarding entries.

Important APIs/functions: `x25_proc_init()` creates `/proc/net/x25/{route,socket,forward}` and `x25_proc_exit()` removes them. Seq operations walk `x25_route_list`, `x25_list`, and `x25_forward_list`.

Control flow: when `CONFIG_PROC_FS` is enabled, init creates the directory and three seq files, rolling back the subtree on failure. Route output shows address prefix, significant digits, and device. Socket output shows addresses, device, LCI, state, sequence variables, timers, send/receive memory, and inode. Forward output shows LCI and paired devices.

State and persistence: no state is owned; output is a snapshot under the corresponding read lock. Without procfs, init/exit are stubs.

Dependencies and integration: depends on global lists from route, socket, and forwarding modules, timer display helper, seq_file, procfs, and init_net proc directory.

Risks and test signals: diagnostics must hold the right locks while tolerating missing device/socket pointers. Tests should cover partial init rollback, concurrent route/socket/forward deletion during reads, disabled `CONFIG_PROC_FS`, and formatting for sockets without neighbours or socket inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_route.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_route.c

Purpose: manages the global X.25 address-prefix route table and route ioctl handling.

Important APIs/functions: `x25_get_route()` performs longest-prefix route lookup; `x25_route_ioctl()` handles `SIOCADDRT` and `SIOCDELRT`; `x25_route_device_down()` removes routes for a disappearing device; `x25_dev_get()` validates X.25 netdevices; and `x25_route_free()` releases all routes on module exit.

Control flow: add-route rejects duplicate prefix/device-length pairs, pads address strings with zeros, stores significant digit count and device pointer, and inserts under write lock. Delete-route finds an exact prefix/significant-digits/device match and removes it. Lookup scans all routes and returns a refcounted longest prefix match.

State and persistence: runtime global `x25_route_list` is protected by `x25_route_list_lock`; each route has address prefix, significant digit count, device pointer, and refcount. No durable persistence exists beyond ioctl-created runtime state.

Dependencies and integration: called by AF_X25 connect and forwarding, controlled by privileged socket ioctls, and cleaned from netdevice notifier paths.

Risks and test signals: route lifetime and prefix matching are central. Tests should cover invalid significant digits, down or non-ARPHRD_X25 device rejection, duplicate add, longest-prefix selection, route deletion while referenced, device down cleanup, and CAP_NET_ADMIN enforcement in caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_subr.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_subr.c

Purpose: contains shared X.25 protocol subroutines for queue cleanup, acknowledgement accounting, retransmission requeue, frame generation, frame decoding, disconnect, and receive-buffer recovery.

Important APIs/functions: `x25_clear_queues()`, `x25_frames_acked()`, `x25_requeue_frames()`, `x25_validate_nr()`, `x25_write_internal()`, `x25_decode()`, `x25_disconnect()`, and `x25_check_rbuf()` are used across input, output, timers, and socket teardown.

Control flow: acknowledgement helpers remove or requeue frames based on `va/vs` and modulus. Internal frame writing sizes an skb for the requested control frame, writes GFI/LCI, emits call request/accepted facilities and CUD, clear/reset cause bytes, RR/RNR/REJ sequence fields, or confirmations, then sends through the link. Decode validates skb length and returns frame type plus parsed sequence, Q/D/M bits. Disconnect clears queues/timer, resets state, records cause, shuts down socket, wakes waiters, marks dead, and drops neighbour reference.

State and persistence: mutates all per-socket packet-layer queues, sequence variables, condition flags, LCI, state, error/shutdown, cause/diagnostic, call user data length, and neighbour reference.

Dependencies and integration: depends on facilities/address helpers, link transmit, timers, socket memory queues, and constants for standard versus extended sequence encodings.

Risks and test signals: frame encoding/decoding bugs can desynchronize peers. Tests should cover every control frame type, standard/extended RR/RNR/DATA sequence fields, invalid PLP frames, ACK wraparound, reset requeue ordering, disconnect neighbour put, receive-buffer busy clearing, and generated call request/accepted contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_timer.c -->
# sources/distributed-fs/ceph-client/net/x25/x25_timer.c

Purpose: owns per-socket X.25 timers: heartbeat, T2 acknowledgement holdback, T21 call request, T22 reset request, and T23 clear request.

Important APIs/functions: `x25_init_timers()`, `x25_start_heartbeat()`, `x25_stop_heartbeat()`, `x25_start_t2timer()`, `x25_start_t21timer()`, `x25_start_t22timer()`, `x25_start_t23timer()`, `x25_stop_timer()`, and `x25_display_timer()` are used by socket and state-machine code.

Control flow: heartbeat runs every five seconds, destroys dead listen children in state 0, and in connected state calls `x25_check_rbuf()` when the socket is not owned by userspace. The protocol timer interprets expiry by current X.25 state: T2 sends a pending RR/RNR enquiry response, T21/T22 send clear request and enter state 2 with T23 running, and T23 disconnects with `ETIMEDOUT`. If the socket is user-owned in state 3, T2 is restarted.

State and persistence: timers are in `x25_sock->timer` and `sk->sk_timer`; they mutate state, condition flags, queues, and socket errors indirectly through helper calls.

Dependencies and integration: integrates Linux timer APIs, socket BH locking, input/output/subroutine helpers, and sysctl-seeded timer durations.

Risks and test signals: timer expiry races with userspace socket locks and teardown. Tests should cover each state-specific expiry, heartbeat destruction of unaccepted dead sockets, user-owned restart behavior, timer display, stopping timers on disconnect/release, and no use-after-free during delayed destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/x25/x25_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/Kconfig -->
# sources/distributed-fs/ceph-client/net/xdp/Kconfig

Purpose: defines AF_XDP socket and diagnostic monitoring build options.

Important symbols: `XDP_SOCKETS` is a bool depending on `BPF_SYSCALL` and enables channels between XDP programs and userspace. `XDP_SOCKETS_DIAG` is a tristate depending on `XDP_SOCKETS` and enables SOCK_DIAG monitoring used by `ss`.

Control flow: Kconfig selection decides whether core AF_XDP socket, UMEM, queue, buffer-pool, and XSKMAP objects are compiled and whether the diagnostic module/object is available.

State and persistence: build configuration persists in `.config`; no runtime state is directly managed here.

Dependencies and integration: aligns with BPF redirect map support, AF_XDP socket registration, and the Makefile object list under `net/xdp`.

Risks and test signals: dependency mistakes could expose AF_XDP without BPF syscall support or diag without sockets. Tests should include `CONFIG_BPF_SYSCALL=n`, `XDP_SOCKETS=y`, diag as built-in/module, and AF_XDP selftests matching selected features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/Makefile -->
# sources/distributed-fs/ceph-client/net/xdp/Makefile

Purpose: maps AF_XDP Kconfig symbols to the core and diagnostic object files.

Important build mappings: `CONFIG_XDP_SOCKETS` builds `xsk.o`, `xdp_umem.o`, `xsk_queue.o`, `xskmap.o`, and `xsk_buff_pool.o`; `CONFIG_XDP_SOCKETS_DIAG` builds `xsk_diag.o`.

Control flow: kbuild includes objects in the built-in image or module set according to the symbol values. Core AF_XDP is built as a group, while diag can be a separate loadable module.

State and persistence: no runtime state is owned; this is the persistent build contract for AF_XDP.

Dependencies and integration: must stay synchronized with exports used by drivers (`xsk_*`, `xp_*`), BPF map registration, socket registration, and diag module aliases.

Risks and test signals: missing an object breaks link-time symbol resolution or runtime feature availability. Tests should cover core-only builds, diag module builds, and AF_XDP selftests that exercise UMEM, queue, map, and socket paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xdp_umem.c -->
# sources/distributed-fs/ceph-client/net/xdp/xdp_umem.c

Purpose: creates, pins, accounts, maps, refcounts, and releases AF_XDP UMEM regions used as packet buffer memory shared with userspace.

Important APIs/functions: `xdp_umem_create()` validates and creates a UMEM; `xdp_get_umem()` and `xdp_put_umem()` manage references. Internal helpers account locked pages, long-term pin user pages, vmap page arrays, unmap/unpin/unaccount, and optionally defer release via workqueue.

Control flow: registration validates chunk size, flags, page alignment, length overflow, page/chunk counts, power-of-two aligned mode, headroom, and TX metadata length. It sets UMEM geometry, initializes DMA map list and refcount, charges `RLIMIT_MEMLOCK` unless privileged, pins user pages with `FOLL_LONGTERM|FOLL_WRITE`, and vmaps them into `umem->addrs`. Creation allocates an IDA id before registration and cleans up on failure.

State and persistence: per-UMEM state includes ID, user page array, vmap address, size/chunks/pages, flags, headroom, chunk size, optional TX metadata length, user locked-vm accounting, DMA map list, zero-copy flag, and refcount.

Dependencies and integration: used by `xsk.c` socket `XDP_UMEM_REG`, shared by buffer pools in `xsk_buff_pool.c`, and integrates MM long-term pinning, UID accounting, vmalloc/vmap, IDA, and workqueues.

Risks and test signals: pin/account unwind paths and integer validation are critical. Tests should cover invalid flags/chunk/headroom/metadata, aligned versus unaligned chunk geometry, memlock exhaustion, partial pin failures, vmap failure, shared UMEM refcounts, deferred cleanup, and dirty unpin on release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xdp_umem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xdp_umem.h -->
# sources/distributed-fs/ceph-client/net/xdp/xdp_umem.h

Purpose: declares the internal AF_XDP UMEM lifecycle API shared between socket and buffer-pool implementation files.

Important APIs/types: includes `<net/xdp_sock_drv.h>` for `struct xdp_umem` and declares `xdp_get_umem()`, `xdp_put_umem()`, and `xdp_umem_create()`.

Control flow: this header has no executable flow; callers use it to create a UMEM from `struct xdp_umem_reg`, hold references while sharing pools/sockets, and release references with optional deferred cleanup.

State and persistence: no state is owned here. The declared APIs manipulate `struct xdp_umem` state in `xdp_umem.c`.

Dependencies and integration: included by `xsk.c` and `xsk_buff_pool.c`, and indirectly ties internal code to driver-facing XDP socket structures.

Risks and test signals: risks are ABI/internal declaration drift with `xdp_umem.c` or `net/xdp_sock_drv.h`. Build tests should compile all AF_XDP configurations and verify no stale prototypes or missing includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xdp_umem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk.c -->
# sources/distributed-fs/ceph-client/net/xdp/xsk.c

Purpose: implements PF_XDP sockets, including socket creation/release, bind to netdev queue and UMEM, ring setup/mmap, Rx redirect delivery, Tx wakeup/generic transmit, poll/sendmsg/recvmsg, netdevice teardown, and module/pernet registration.

Important APIs/functions: exported driver helpers include `xsk_set/clear_rx_need_wakeup()`, `xsk_set/clear_tx_need_wakeup()`, `xsk_uses_need_wakeup()`, `xsk_get_pool_from_qid()`, `xsk_clear_pool_at_qid()`, `xsk_reg_pool_at_qid()`, `xsk_generic_rcv()`, `__xsk_map_redirect()`, `__xsk_map_flush()`, `xsk_tx_completed()`, `xsk_tx_release()`, `xsk_tx_peek_desc()`, and `xsk_tx_peek_release_desc_batch()`. Socket ops include bind, setsockopt, getsockopt, mmap, poll, sendmsg, recvmsg, and release.

Control flow: userspace creates a raw PF_XDP socket, configures RX/TX/FILL/COMPLETION rings and UMEM, then binds to a device queue with own or shared UMEM. Bind creates/assigns a buffer pool, registers it at the queue, optionally enables driver zero-copy, records device/queue, and publishes `XSK_BOUND` with memory ordering. XDP redirect Rx validates binding and queue, then either zero-copy publishes descriptors or copies packets/fragments into UMEM-backed buffers and flushes ring updates. Tx send/poll wakes zero-copy drivers or generic-SKB transmit; generic transmit consumes TX descriptors, reserves completion entries, builds linear/fraged skb(s), handles metadata, direct-xmits, and completes/cancels descriptors.

State and persistence: per-socket `xdp_sock` state includes readiness/bound state, rx/tx queues, temporary or pool-owned fill/completion queues, UMEM, pool, netdev, queue id, zero-copy/scatter-gather flags, map membership, pending multi-buffer skb, stats, and mutex. Per-net state tracks PF_XDP sockets in `net->xdp.list`.

Dependencies and integration: integrates socket/proto registration, BPF XSKMAP redirects, netdevice queue pool slots and queue leases, NAPI busy poll, XDP buffer pool APIs, UMEM lifecycle, ring memory ordering, netdevice notifier cleanup, skb metadata/checksum/timestamp support, and CAP_NET_RAW.

Risks and test signals: risks include bind-time lifetime/unwind, memory ordering for state/ring publication, shared UMEM ownership, queue lease handling, zero-copy fallback, multi-buffer TX overflow, completion-ring backpressure, and map deletion deadlock avoidance. Tests should cover AF_XDP selftests for copy/zero-copy/shared UMEM, invalid descriptors, need-wakeup, mmap offsets, device unregister, busy-poll, TX metadata, SG packets, queue leases, and concurrent map/socket release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk.h -->
# sources/distributed-fs/ceph-client/net/xdp/xsk.h

Purpose: provides internal AF_XDP declarations for mmap offset v1 compatibility, XSKMAP membership nodes, socket casting, and queue pool registration helpers.

Important APIs/types: defines `struct xdp_ring_offset_v1`, `struct xdp_mmap_offsets_v1`, `struct xsk_map_node`, inline `xdp_sk()`, and prototypes for `xsk_map_try_sock_delete()`, `xsk_clear_pool_at_qid()`, and `xsk_reg_pool_at_qid()`.

Control flow: no executable flow beyond `xdp_sk()` casting a `struct sock *` to `struct xdp_sock *`. The structures are consumed by getsockopt compatibility and XSKMAP/socket cleanup paths.

State and persistence: no state is owned here. `xsk_map_node` instances persist on each socket map-list while a socket is stored in BPF XSKMAP entries.

Dependencies and integration: shared by `xsk.c`, `xskmap.c`, `xsk_queue.h`, and buffer-pool code; it ties BPF map entries back to PF_XDP socket state and netdevice queue pool operations.

Risks and test signals: declaration drift would break map cleanup or mmap offset compatibility. Tests should include old userspace offset structure reads, map update/delete while sockets close, and builds across AF_XDP core/map configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_buff_pool.c -->
# sources/distributed-fs/ceph-client/net/xdp/xsk_buff_pool.c

Purpose: implements AF_XDP buffer pools that bind UMEM, fill/completion rings, netdev queues, DMA mappings, free buffer heads, and driver-facing allocation/free helpers.

Important APIs/functions: `xp_create_and_assign_umem()`, `xp_assign_dev()`, `xp_assign_dev_shared()`, `xp_clear_dev()`, `xp_get_pool()`, `xp_put_pool()`, `xp_dma_map()`, `xp_dma_unmap()`, `xp_alloc()`, `xp_alloc_batch()`, `xp_can_alloc()`, `xp_free()`, `xp_raw_get_data()`, `xp_raw_get_dma()`, and `xp_raw_get_ctx()` are the main surfaces, with several exported for drivers.

Control flow: pool creation allocates buffer heads, TX descriptor cache, geometry, ring pointers, locks, and free lists from a UMEM. Device assignment registers the pool at a queue, sets need-wakeup/copy/zerocopy/SG policy, checks MTU and XDP feature support, calls driver `ndo_bpf(XDP_SETUP_XSK_POOL)`, and falls back to copy unless zero-copy was forced. Allocation consumes valid fill-ring addresses or reused heads, initializes XDP buffer pointers/DMA, and returns buffers to drivers; free returns heads to a pool free list. DMA mapping is shared per UMEM/netdev through `xsk_dma_list` and refcounted maps.

State and persistence: pool state includes UMEM reference, rings, netdev/device pointers, queue id, zero-copy capability, DMA pages, TX descriptors, buffer heads/free lists, frame geometry, need-wakeup cache, xsk TX list, and refcount. Cleanup is deferred through workqueue so RTNL/device teardown happens safely.

Dependencies and integration: used by PF_XDP bind, driver zero-copy paths, DMA APIs, netdevice queue registration, XDP buffer helpers, UMEM lifecycle, and queue descriptor validation.

Risks and test signals: high-risk areas are fallback cleanup after failed zero-copy setup, shared DMA-map refcounts, unaligned address validation across non-contiguous pages, fill-ring invalid descriptor accounting, and deferred pool destruction with device unregister. Tests should cover copy and forced zero-copy, SG MTU limits, TX software checksum incompatibility, shared UMEM across devices/queues, DMA map reuse/unmap, fill-ring exhaustion, invalid aligned/unaligned addresses, and driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_buff_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_diag.c -->
# sources/distributed-fs/ceph-client/net/xdp/xsk_diag.c

Purpose: implements SOCK_DIAG dumping for PF_XDP sockets so monitoring tools can inspect AF_XDP socket, ring, UMEM, memory, and statistics state.

Important APIs/functions: `xsk_diag_init()` registers the AF_XDP diag handler; `xsk_diag_exit()` unregisters it. `xsk_diag_handler_dump()`, `xsk_diag_dump()`, and `xsk_diag_fill()` serve dump requests, while helpers put info, ring config, UMEM, and stats attributes.

Control flow: a netlink dump request must be `NLM_F_DUMP` and at least `struct xdp_diag_req`. The dump walks `net->xdp.list` under lock, resumes from callback state, and fills each socket if it fits. Per socket, the code locks the xsk mutex, skips unbound sockets, conditionally emits requested attributes, ends the message, or cancels on size failure.

State and persistence: no persistent state is owned. Output snapshots socket state, queue entry counts, UMEM id/geometry/refcount/zero-copy flag, pool queue/device, sock memory info, and descriptor/stat counters.

Dependencies and integration: depends on PF_XDP per-net socket list from `xsk.c`, queue counter helpers, Linux sock_diag/netlink APIs, and module aliasing for AF_XDP diagnostics.

Risks and test signals: diagnostic dumps must avoid racing socket teardown and must handle absent queues/pools. Tests should cover all `xdiag_show` masks, small skb/EMSGSIZE resume, unbound socket skip, namespace filtering, module load/unload, and `ss` output for copy/zero-copy/shared UMEM sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_queue.c -->
# sources/distributed-fs/ceph-client/net/xdp/xsk_queue.c

Purpose: allocates and frees the vmalloc-backed ring structures shared between AF_XDP kernel code and userspace.

Important APIs/functions: `xskq_create()` allocates an `xsk_queue` and the corresponding RX/TX or UMEM ring memory; `xskq_destroy()` frees it. `xskq_get_ring_size()` chooses between `struct xdp_rxtx_ring` and `struct xdp_umem_ring` sizing.

Control flow: creation allocates the queue object, records power-of-two entry count and mask, computes flexible-array ring size, page-aligns it, allocates user-mappable zeroed memory with `vmalloc_user()`, records the vmalloc size, and returns the queue. Destruction vfree's the ring and frees the queue.

State and persistence: each queue stores cached producer/consumer indices, ring mask, entry count, ring pointer, invalid/empty counters, vmalloc size, and a completion-ring producer lock initialized elsewhere when used by pools.

Dependencies and integration: called by PF_XDP setsockopt queue initialization and later mmap'd by `xsk_mmap()`. The inline producer/consumer operations live in `xsk_queue.h`.

Risks and test signals: sizing and mmap safety are primary concerns. Tests should cover RX/TX and fill/completion ring allocation, huge entry counts near overflow, vmalloc failure, mmap size bounds, and destroy of partially initialized or NULL queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_queue.h -->
# sources/distributed-fs/ceph-client/net/xdp/xsk_queue.h

Purpose: defines AF_XDP shared ring layouts and inline producer/consumer operations, including descriptor validation and memory-ordering rules for userspace/kernel rings.

Important APIs/types: defines `xdp_ring`, `xdp_rxtx_ring`, `xdp_umem_ring`, `xsk_queue`, and helpers for consumer read/peek/release, producer reserve/write/submit, descriptor validation, batch TX descriptor reads, queue counters, and declarations for `xskq_create/destroy()`.

Control flow: rings follow circular-buffer semantics. Consumers acquire-load producer, read descriptors, validate them, and release consumer with store-release when needed. Producers check free space using cached indices, write descriptors or addresses, and store-release producer on submit. Descriptor validation enforces nonzero length, chunk bounds, TX metadata space, supported options, aligned/unaligned address extraction, and non-contiguous page restrictions. Batch TX reads stop on invalid descriptors or SG segment limits and release consumed entries.

State and persistence: queue state is shared with userspace ring pointers plus kernel cached indices and stats counters for invalid and empty descriptors. No durable persistence exists.

Dependencies and integration: used by `xsk.c`, `xsk_buff_pool.c`, `xsk_diag.c`, and drivers through AF_XDP pool APIs. Depends on `if_xdp.h`, `xdp_sock`, and `xsk_buff_pool` helpers.

Risks and test signals: memory barriers are correctness-critical; descriptor validation protects UMEM bounds and DMA safety. Tests should cover producer/consumer wraparound, invalid descriptor accounting, aligned and unaligned address edge cases, TX metadata underflow, unsupported options, multi-buffer descriptor batches, completion-ring sharing locks, and weak-memory stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xsk_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xskmap.c -->
# sources/distributed-fs/ceph-client/net/xdp/xskmap.c

Purpose: implements the BPF `BPF_MAP_TYPE_XSKMAP` used by XDP programs to redirect packets into AF_XDP sockets.

Important APIs/functions: `xsk_map_ops` provides allocation, free, lookup, JIT lookup generation, update, delete, redirect, BTF, memory usage, and metadata comparison methods. Helpers manage per-socket `xsk_map_node` membership and `xsk_map_try_sock_delete()` removes sockets during release.

Control flow: map allocation validates key/value sizes, entry count, and flags, then allocates a flexible `xsk_map`. Updates look up a PF_XDP fd, require an RX ring, allocate a membership node, lock the map, enforce `BPF_NOEXIST`/`BPF_EXIST`, add the socket to its map list, publish the entry with RCU, and remove any old socket membership. Deletes exchange the entry with NULL and unlink the old socket node. Redirect uses `__bpf_xdp_redirect_map()` with the XSK lookup callback.

State and persistence: map state includes RCU socket pointer array, lock, and node count. Each socket tracks map entries it occupies via `xsk_map_node` on `xs->map_list`; node allocation holds a BPF map ref and count.

Dependencies and integration: integrates BPF map infrastructure, AF_XDP sockets, RCU/BH lookup contexts, generated BPF lookup instructions, BTF IDs, and socket release cleanup in `xsk.c`.

Risks and test signals: lock ordering between map lock and socket map-list lock is crucial to avoid deadlock during socket release and map update/delete. Tests should cover invalid attr sizes/flags, update with non-XDP fd, update without RX ring, map flag semantics, concurrent update/delete/close, redirect to bound/unbound sockets, RCU grace-period free, and map memory accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xdp/xskmap.c -->
