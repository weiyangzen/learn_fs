# subset-b-006294 research

Work item `subset-b-006294` covers VMCI/vsock notification helpers plus the opening cfg80211 wireless core files. Each section below preserves the original source path and is wrapped for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.c

## Purpose
This file implements the packet-based VMCI vsock stream notification strategy exported as `vmci_transport_notify_pkt_ops`. It coordinates wakeups between peers by sending and consuming VMCI transport control packets such as `READ`, `WROTE`, `WAITING_READ`, and `WAITING_WRITE`. The code optimizes stream blocking behavior with optional waiting notifications and flow control, using queue-pair occupancy to avoid excessive wakeups while still notifying a peer when reads free space or writes make data available.

## Important APIs, types, and functions
The file is driven through `struct vmci_transport_notify_ops` from `vmci_transport_notify.h`. Its callback table includes socket lifecycle hooks, poll hooks, receive/send pre/post hooks, packet dispatch, and negotiation hooks. `PKT_FIELD(vsk, name)` maps notification state into `vmci_trans(vsk)->notify.pkt`.

Important helpers include `vmci_transport_notify_waiting_write()`, which decides whether a blocked peer writer should be notified based on `peer_waiting_write`, consume queue free space, and the adaptive `write_notify_window`; `vmci_transport_notify_waiting_read()`, which checks whether the peer is waiting to read and whether the produce queue has data; `send_waiting_read()` and `send_waiting_write()`, which build `struct vmci_transport_waiting_info` from qpair indexes and generation counters; and `vmci_transport_send_read_notification()`, which retries `vmci_transport_send_read()` up to `VMCI_TRANSPORT_MAX_DGRAM_RESENDS`.

Packet handlers `vmci_transport_handle_wrote()`, `vmci_transport_handle_read()`, `vmci_transport_handle_waiting_read()`, and `vmci_transport_handle_waiting_write()` update waiting flags and call socket wakeups such as `vsock_data_ready()` or `sk->sk_write_space()`.

## Control flow
Socket initialization resets all notification fields, waiting flags, queue generations, and waiting-info snapshots. Poll-in first checks `vsock_stream_has_data(vsk) >= target`; if not ready on an established socket, it sends `WAITING_READ`. Poll-out checks `vsock_stream_has_space(vsk)`; if full, it sends `WAITING_WRITE`.

On receive, `recv_init()` may grow `write_notify_min_window` to fit the caller target and request a notification if the new minimum exposes sender throttling. `recv_pre_block()` sends `WAITING_READ` and may emit a read notification before sleeping. `recv_pre_dequeue()` snapshots consume indexes; `recv_post_dequeue()` detects consume queue generation wrap and sends `READ` if bytes were consumed. On send, `send_pre_enqueue()` snapshots produce indexes and `send_post_enqueue()` updates produce generation, then sends `WROTE` if the peer is waiting to read.

Incoming notify packets are dispatched by `vmci_transport_notify_pkt_handle_pkt()`. `WROTE` clears `sent_waiting_read` and wakes readers. `READ` clears `sent_waiting_write` and wakes writers. `WAITING_*` records peer wait state and may immediately reply with `WROTE` or `READ` if qpair state already satisfies the wait.

## State and persistence
All state is per socket and in memory under `vmci_trans(vsk)->notify.pkt`: waiting flags, sent-waiting suppression flags, adaptive windows, queue generation counters, and peer waiting information. There is no durable persistence. Correctness depends on socket locking across qpair index snapshots and enqueue/dequeue operations.

## Dependencies and integration points
The file depends on VMCI qpair primitives, VMCI transport send helpers, `struct vsock_sock`, Linux socket callbacks, and packet definitions from `vmci_transport.h`. It is selected by the VMCI transport negotiation path as one possible notify implementation. `process_request()` and `process_negotiate()` initialize window values to the negotiated consume size.

## Risks
Generation and offset math must remain paired with qpair wrap behavior, otherwise waiting notifications can target the wrong queue generation. Retry failure currently logs an error but does not schedule durable resend work. The adaptive window decreases when a peer blocks and increases on local blocking, so regressions can cause either high wakeup traffic or throughput loss. Build-time macros hide alternate behavior, so both optimized and fallback configurations need coverage.

## Test signals
Useful tests include stream send/recv blocking tests across full and empty queue transitions, poll readiness tests, wrap-around queue tests, mixed endpoint compatibility tests, retry-failure injection, and throughput/latency checks with `VSOCK_OPTIMIZATION_FLOW_CONTROL` enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.h -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.h

## Purpose
This header defines the VMCI vsock notification abstraction used by the stream send, receive, poll, and control-packet paths. It lets the transport plug in either packet-based waiting notifications or queue-state notifications without changing the higher-level socket code.

## Important APIs, types, and functions
`VSOCK_OPTIMIZATION_WAITING_NOTIFY` enables explicit waiting notification packets, and `VSOCK_OPTIMIZATION_FLOW_CONTROL` enables adaptive read-notification windowing. `VMCI_TRANSPORT_MAX_DGRAM_RESENDS` caps notify datagram retries at 10.

`struct vmci_transport_recv_notify_data` stores per-receive temporary state: `consume_head`, `produce_tail`, and `notify_on_block`. `struct vmci_transport_send_notify_data` stores per-send queue-index snapshots. `struct vmci_transport_notify_ops` is the central callback contract, covering socket init/destruct, poll readiness, notify-packet handling, receive/send lifecycle hooks, and connection request/negotiate handling. The header declares `vmci_transport_notify_pkt_ops` and `vmci_transport_notify_pkt_q_state_ops`.

## Control flow
The VMCI transport allocates per-call notify data, invokes the selected ops around blocking and queue operations, and lets the strategy emit or consume control packets. The callback shape enforces a stable sequence: initialize call data, optionally notify before blocking, snapshot before enqueue/dequeue, update state and notify after data movement, then process any incoming notify packets through the strategy.

## State and persistence
The header itself owns no storage. It defines transient per-call structures and the function-pointer contract used to reach per-socket state in `vmci_transport` private data. There is no persistent state beyond the in-memory socket transport object.

## Dependencies and integration points
It includes VMCI definitions and `vmci_transport.h`, so it is specific to the VMware VMCI vsock transport. Its ops are used by both `vmci_transport_notify.c` and `vmci_transport_notify_qstate.c` and by surrounding VMCI stream send/receive code.

## Risks
Any callback signature change must be propagated through every implementation and caller. Compile-time optimization macros can change struct field usage expectations, so layout and initialization paths need to stay synchronized with the private notify structs in `vmci_transport.h`.

## Test signals
Build tests should cover both notify implementations. Runtime tests should verify that each callback is called in the intended order around poll, blocking reads, blocking writes, socket teardown, and negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify_qstate.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify_qstate.c

## Purpose
This file implements the queue-state VMCI vsock notification strategy exported as `vmci_transport_notify_pkt_q_state_ops`. Unlike the explicit waiting-notify strategy, it infers whether notifications are needed from queue transitions such as full-to-not-full and empty-to-not-empty, while still using `READ` and `WROTE` notify packets for wakeups.

## Important APIs, types, and functions
`PKT_FIELD(vsk, name)` maps into `vmci_trans(vsk)->notify.pkt_q_state`. `vmci_transport_notify_waiting_write()` applies adaptive flow-control window logic and checks consume queue free space. `vsock_block_update_write_window()` grows the write notification window when a local receive path blocks. `vmci_transport_send_read_notification()` retries `READ` notifications and clears `peer_waiting_write` on success. Send/receive hooks mirror the generic ops contract but many waiting-packet hooks are NOPs because qstate does not send `WAITING_READ` or `WAITING_WRITE`.

## Control flow
Initialization sets `write_notify_window`, `write_notify_min_window`, and peer-waiting state. Poll-in reports readiness if enough stream data exists; otherwise it grows the write window for established sockets. Poll-out reports available space but does not send a waiting write packet.

On receive, `recv_init()` raises the minimum write notify window to `target + 1` and records `notify_on_block` when the current window must be reevaluated. `recv_pre_block()` grows the window and optionally sends a read notification. `recv_post_dequeue()` uses `smp_mb()` before reading qpair free space; if `free_space == copied`, the queue was full before the read, so it marks `peer_waiting_write` and sends `READ`. It also calls `vsock_data_ready()` as a local wakeup compensation noted by the in-code comment.

On send, `send_post_enqueue()` uses `smp_mb()` and checks whether the produce buffer ready count equals bytes written, meaning the queue was empty before this enqueue. If so, it retries `WROTE` notifications. Incoming notify packet dispatch only consumes `WROTE` and `READ`.

## State and persistence
State is per socket and in memory: write windows, `peer_waiting_write`, and `peer_waiting_write_detected`. There are no explicit waiting-info offsets or generation counters in this strategy. Memory barriers protect qpair state observations around enqueue/dequeue effects.

## Dependencies and integration points
The implementation depends on VMCI qpair counters, VMCI notify send helpers, Linux socket wakeup callbacks, and the common notify ops contract. It integrates as an alternate notification mode for VMCI stream sockets.

## Risks
The transition inference is sensitive to stale qpair counters and memory ordering. If `was_full` or `was_empty` is misdetected, peers can miss wakeups or receive redundant notifications. The adaptive window has the same throughput versus wakeup-frequency tradeoff as the packet strategy.

## Test signals
Exercise full queue reads, empty queue writes, concurrent poll/read/write paths, teardown while notifications are pending, and failure injection for `vmci_transport_send_read()` and `vmci_transport_send_wrote()`. Lockdep/KCSAN-style checks are useful because correctness depends on socket locking and barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify_qstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_addr.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_addr.c

## Purpose
This file provides small exported helpers for initializing, validating, comparing, binding, unbinding, and casting AF_VSOCK socket addresses.

## Important APIs, types, and functions
`vsock_addr_init()` clears a `struct sockaddr_vm` and sets family, CID, and port. `vsock_addr_validate()` rejects null pointers, non-`AF_VSOCK` families, and unsupported `svm_flags` values, currently allowing only `VMADDR_FLAG_TO_HOST`. `vsock_addr_bound()` tests whether the port is not `VMADDR_PORT_ANY`; `vsock_addr_unbind()` resets to `VMADDR_CID_ANY` and `VMADDR_PORT_ANY`. `vsock_addr_equals_addr()` compares CID and port. `vsock_addr_cast()` validates a generic `sockaddr_unsized` buffer length, casts it to `sockaddr_vm`, and validates the result.

## Control flow
The helpers are direct and side-effect-free except for address initialization/reset. Cast validation first checks the user-provided length to avoid short-address access, then delegates to `vsock_addr_validate()`.

## State and persistence
No global state is stored. The only mutations are to caller-provided `sockaddr_vm` objects.

## Dependencies and integration points
The functions are exported with `EXPORT_SYMBOL_GPL` and used by AF_VSOCK core and transports for bind, connect, address comparison, and userspace address parsing. They depend on `net/vsock_addr.h`, VMADDR constants, and Linux socket address conventions.

## Risks
Flag validation must remain aligned with the AF_VSOCK ABI; accepting unknown flags can alter routing semantics, while rejecting newly valid flags without updating this helper can block new features. The cast helper relies on callers passing the true userspace sockaddr length.

## Test signals
Unit tests or syscall-level tests should cover null input, wrong family, unsupported flags, short lengths, wildcard unbind state, equality behavior, and valid `VMADDR_FLAG_TO_HOST` addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_bpf.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_bpf.c

## Purpose
This file integrates AF_VSOCK sockets with BPF sockmap/sk_msg redirection. It swaps the socket protocol callbacks so BPF can intercept receive paths while preserving normal vsock receive behavior when BPF queues are empty or unsupported.

## Important APIs, types, and functions
`vsock_sk_has_data` checks the normal receive queue plus psock ingress skb and message queues. `vsock_has_data()` combines transport-level `vsock_connectible_has_data()` with BPF ingress state. `vsock_msg_wait_data()` waits on `sk_sleep(sk)` with `SOCKWQ_ASYNC_WAITDATA` set until normal or BPF data arrives. `__vsock_recvmsg()` dispatches to stream/seqpacket or datagram receive implementations based on `sk_type`.

`vsock_bpf_recvmsg()` is the replacement `recvmsg` callback. It obtains the `sk_psock`, locks the socket, falls back to native vsock receive when BPF queues are empty and normal data is present, otherwise drains BPF messages with `sk_msg_recvmsg()` and waits if necessary. `vsock_bpf_rebuild_protos()` copies a base `struct proto` and overrides `close`, `recvmsg`, and `sock_is_readable`. `vsock_bpf_update_proto()` installs or restores the protocol under sockmap control.

## Control flow
On BPF attach, `vsock_bpf_update_proto(..., restore=false)` checks that a transport exists and supports `read_skb`, rebuilds the cached BPF proto if the base proto changed, and calls `sock_replace_proto()`. On detach, it restores saved write-space and protocol pointers from `sk_psock`.

During receive, the BPF path first handles no-psock fallback. With psock present, it locks the socket and checks transport validity. If normal vsock data is present and the BPF queue is empty, it releases the lock and calls native receive. Otherwise it drains sk_msg data, waiting according to `sock_rcvtimeo()` when a zero-length read result means no message data is currently available.

## State and persistence
Global in-memory state includes `vsock_prot_saved`, `vsock_prot_lock`, and `vsock_bpf_prot`. Release/acquire ordering protects publication of rebuilt proto function pointers. Per-socket state lives in `sk_psock` and the socket proto pointer.

## Dependencies and integration points
This code depends on `linux/skmsg.h`, sockmap psock APIs, BPF infrastructure, and AF_VSOCK internal receive helpers. It integrates with transports that implement `read_skb`; transports without that callback return `-EOPNOTSUPP`.

## Risks
Incorrect proto rebuild ordering could publish stale callback pointers. Receive fallback must avoid holding the socket lock across native receive in cases where the native path expects to lock. Waiting behavior must correctly handle shutdown, nonblocking flags, and mixed normal/BPF ingress queues.

## Test signals
Sockmap tests should cover stream, seqpacket, datagram rejection/fallback, attach/detach restore, transport without `read_skb`, blocking and nonblocking receives, shutdown wakeups, and simultaneous native plus BPF queued data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_loopback.c -->
# sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_loopback.c

## Purpose
This file implements the local loopback vsock transport using virtio-vsock common transport operations. It registers a `VSOCK_TRANSPORT_F_LOCAL` transport that reports CID `VMADDR_CID_LOCAL` and feeds transmitted packets back into the virtio-vsock receive path.

## Important APIs, types, and functions
`struct vsock_loopback` stores the workqueue, packet queue, and worker. `vsock_loopback_get_local_cid()` returns the local CID. `vsock_loopback_send_pkt()` queues an skb with `virtio_vsock_skb_queue_tail()` and schedules worker processing. `vsock_loopback_cancel_pkt()` purges queued packets for a socket. The `loopback_transport` object wires AF_VSOCK transport callbacks to `virtio_transport_*` helpers and its `send_pkt` method to `vsock_loopback_send_pkt()`.

`vsock_loopback_work()` splices the packet queue into a local queue, marks bytes as sent with `virtio_transport_consume_skb_sent(skb, false)`, delivers tap visibility, and calls `virtio_transport_recv_pkt()` using the skb socket namespace. Module init allocates the workqueue and registers with vsock core; exit unregisters, flushes work, purges queued skbs, and destroys the workqueue.

## Control flow
Send is asynchronous: enqueue skb, queue work, then the worker drains all queued packets. The worker owns receiver delivery and skb lifetime transfer. Cancellation purges outstanding queue entries for a closing socket. Init and exit pair transport registration with workqueue lifetime.

## State and persistence
All state is global module memory in `the_vsock_loopback`: one workqueue and one skb queue. There is no durable persistence. Queue locking uses the skb queue spinlock and bottom-half-safe operations.

## Dependencies and integration points
The file depends on virtio-vsock common APIs and vsock core registration. It exposes loopback support to AF_VSOCK users and advertises `MODULE_ALIAS_NETPROTO(PF_VSOCK)`. It integrates with BPF through `read_skb = virtio_transport_read_skb` and allows message zero-copy.

## Risks
Packet lifetime is delicate because the worker decrements unsent bytes without freeing the skb, leaving the receiver path to free it. Exit must unregister before purging to prevent new sends. Namespace delivery uses `sock_net(skb->sk)`, so skb socket association must remain valid.

## Test signals
Use local CID stream, seqpacket, and datagram traffic; cancellation during close; module unload with queued packets; tap visibility; zero-copy capability checks; and concurrent send stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_loopback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/Kconfig -->
# sources/distributed-fs/ceph-client/net/wireless/Kconfig

## Purpose
This Kconfig file defines the wireless configuration feature set for cfg80211 and wireless extensions compatibility. It controls whether cfg80211 is built, how regulatory database verification works, whether debug/test/developer paths are included, and whether old WEXT interfaces are exposed.

## Important options
`CFG80211` is the primary tristate and selects firmware loading and CRC32, plus SHA256 when kernel regulatory DB keys are used. `NL80211_TESTMODE`, `CFG80211_DEVELOPER_WARNINGS`, and `CFG80211_KUNIT_TEST` enable test and developer-only paths. Regulatory options include `CFG80211_CERTIFICATION_ONUS`, `CFG80211_REQUIRE_SIGNED_REGDB`, `CFG80211_USE_KERNEL_REGDB_KEYS`, `CFG80211_EXTRA_REGDB_KEYDIR`, `CFG80211_REG_CELLULAR_HINTS`, and `CFG80211_REG_RELAX_NO_IR`. `CFG80211_DEBUGFS` gates debugfs files. `CFG80211_WEXT` selects WEXT compatibility. `CFG80211_DEFAULT_PS` enables default powersave.

## Control flow
Kconfig dependency flow places most options under `if CFG80211`. Certification-sensitive regulatory relaxations depend on `CFG80211_CERTIFICATION_ONUS`, and signature verification can select `SYSTEM_DATA_VERIFICATION`. WEXT support selects `WEXT_CORE`; proc and private WEXT helpers are controlled separately.

## State and persistence
This file does not store runtime state. It persists build-time configuration that determines compiled code paths and available kernel APIs.

## Dependencies and integration points
The options affect files in `net/wireless`, nl80211 userspace API availability, regulatory firmware loading, debugfs exposure, WEXT compatibility files, and test compilation.

## Risks
Regulatory options are high risk because enabling relaxations or disabling signature requirements can change compliance guarantees. Testmode should not be enabled in production kernels. WEXT compatibility increases legacy API surface.

## Test signals
Build matrix coverage should include cfg80211 built-in, module, disabled; signed regdb on/off; debugfs on/off; WEXT on/off; KUnit enabled; and certification-only regulatory relaxations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/Makefile -->
# sources/distributed-fs/ceph-client/net/wireless/Makefile

## Purpose
This Makefile composes the cfg80211 module/object set and generates regulatory certificate source files when configured.

## Important build targets and variables
`obj-$(CONFIG_CFG80211) += cfg80211.o` builds cfg80211. Core objects include `core.o`, `sysfs.o`, `radiotap.o`, `util.o`, `reg.o`, `scan.o`, `nl80211.o`, `mlme.o`, `ibss.o`, `sme.o`, `chan.o`, `ethtool.o`, `mesh.o`, `ap.o`, `trace.o`, `ocb.o`, `michael-mic.o`, and `pmsr.o`. Optional objects include `of.o`, `debugfs.o`, WEXT compatibility, `shipped-certs.o`, and `extra-certs.o`. WEXT core/proc/private objects are built independently from cfg80211.

Generated targets `shipped-certs.c` and `extra-certs.c` produce byte arrays for regulatory DB certificates using shell pipelines over `.hex` or `.x509` files. `clean-files` removes generated certificate sources.

## Control flow
Kbuild aggregates `cfg80211-y` and feature-specific fragments into `cfg80211.o`. Certificate generation writes C files including `reg.h` and defining `shipped_regdb_certs` or `extra_regdb_certs` plus length symbols.

## State and persistence
No runtime state exists. Generated C files are build artifacts, removed by clean rules.

## Dependencies and integration points
The file integrates with Kbuild, Kconfig options, trace include flags, regulatory certificate directories, and optional WEXT/debugfs code.

## Risks
Certificate generation depends on shell tools and correct input formatting; empty or malformed generated arrays would break regulatory DB verification. Object ordering must include symbols used by nl80211, regulatory, and cfg80211 core initialization.

## Test signals
Build tests should cover all optional configs, especially extra certificate directories, generated-file clean behavior, WEXT-only helpers, and debugfs inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ap.c -->
# sources/distributed-fs/ceph-client/net/wireless/ap.c

## Purpose
This file implements cfg80211 access point stop handling for AP and P2P GO interfaces, including multi-link stop support.

## Important APIs, types, and functions
`___cfg80211_stop_ap()` stops one link after validating driver support, interface type, and active beacon state. It calls `rdev_stop_ap()`, clears ownership and AP state, resets QoS map, optionally sends `nl80211_send_ap_stopped()`, schedules DFS channel updates, and queues disconnect work. `cfg80211_stop_ap()` is the public wrapper that stops either a specified link or all valid links.

## Control flow
For a specific link, the wrapper delegates directly. For all links, it iterates `for_each_valid_link()` and attempts each stop even if earlier links fail, preserving the last error. The internal helper returns `-EOPNOTSUPP` for missing ops or wrong iftype and `-ENOENT` when the link is not beaconing.

## State and persistence
AP state is in `wireless_dev`: `conn_owner_nlportid`, per-link `ap.beacon_interval`, per-link chandef, and shared AP SSID length. State is cleared only after the driver stop succeeds. There is no durable persistence.

## Dependencies and integration points
The file depends on cfg80211 core structures, nl80211 notifications, `rdev-ops.h`, QoS map operations, DFS scheduling, and global `cfg80211_disconnect_work`.

## Risks
Multi-link stop must not leave partially stopped state hidden from userspace. The helper clears shared `wdev->u.ap.ssid_len` on each successful link stop, which is correct for current semantics but should be reviewed for future per-link SSID state. DFS updates must happen after beaconing state changes.

## Test signals
Tests should cover stop without driver op, stop on non-AP iftypes, inactive link, successful single-link stop, all-links stop with mixed failures, nl80211 notification behavior, and DFS update scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/chan.c -->
# sources/distributed-fs/ceph-client/net/wireless/chan.c

## Purpose
This file implements cfg80211 channel definition construction, validation, compatibility checks, DFS/CAC state helpers, regulatory beacon checks, and channel usability decisions across legacy, HT/VHT/EHT, 6 GHz, 60 GHz EDMG, and S1G modes.

## Important APIs, types, and functions
Key exports include `cfg80211_chandef_create()`, `nl80211_chan_width_to_mhz()`, `cfg80211_chandef_valid()`, `cfg80211_chandef_primary()`, `cfg80211_chandef_compatible()`, `cfg80211_set_dfs_state()`, `cfg80211_set_cac_state()`, `cfg80211_chandef_dfs_required()`, `cfg80211_chandef_dfs_usable()`, `cfg80211_chandef_dfs_cac_time()`, `cfg80211_chandef_usable()`, `cfg80211_reg_check_beaconing()`, `cfg80211_any_usable_channels()`, and `wdev_chandef()`.

Internal helpers validate puncturing bitmaps for 80/160/320 MHz, strict 6 GHz center frequencies, control-channel placement, EDMG bandwidth/channel combinations, S1G subchannels and primary siblings, DFS permissive P2P GO operation, NO_IR relaxations, and active beaconing interfaces.

## Control flow
Validation starts with structural checks: non-null channel, frequency offset below 1000 kHz, width family compatibility, center frequency rules, channel 14 restrictions, EDMG validity, S1G fields, and puncturing bitmap validity. Usability then overlays wiphy capabilities and channel flags: HT/VHT/EHT capability checks, 6 GHz special handling, 320 MHz EHT iftype data, prohibited flags such as disabled/no-OFDM/no-width, and per-subchannel availability.

DFS flow checks every non-punctured subchannel. `cfg80211_chandef_dfs_required()` returns a bit for the chandef width when AP-like iftypes need CAC. `cfg80211_chandef_dfs_available()` verifies radar channels are already available or usable with DFS offload. Beaconing checks first ensure the chandef is usable, then consider DFS availability and regulatory NO_IR relaxations before returning permission.

## State and persistence
The file mutates per-channel in-memory state: `dfs_state`, `dfs_state_entered`, and `cac_start_time`. It reads live `wiphy->wdev_list` state to decide if interfaces are beaconing or if concurrent DFS/IR relaxations are valid. No durable storage exists.

## Dependencies and integration points
It depends on cfg80211 public structures, regulatory helpers, `rdev_get_channel()`, wiphy feature bits, netdev/wdev mode state, and tracepoints. It feeds nl80211 validation, AP/mesh/IBSS channel setup, radar handling, and monitor-channel operations.

## Risks
Regulatory correctness is the main risk: invalid center frequencies, puncturing masks, DFS transitions, or NO_IR relaxations can permit illegal operation or reject valid channels. Multi-link and multi-radio state increases the chance of stale `wdev` assumptions. S1G, EDMG, and EHT 320 MHz rules are specialized and need targeted tests.

## Test signals
KUnit tests should cover every width, 6 GHz alignment, 80+80 adjacency rejection, puncturing validity, primary channel extraction, chandef compatibility, S1G/EDMG usable checks, DFS required/usable/available states, beacon relaxations, and active-interface subchannel detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/core.c -->
# sources/distributed-fs/ceph-client/net/wireless/core.c

## Purpose
This file is the central cfg80211 lifecycle and registration implementation. It creates and registers wiphy devices, validates driver capabilities, manages global registered-device lists, handles rfkill and network namespace changes, registers wireless netdevices, runs cfg80211 work queues, and initializes/exits the cfg80211 subsystem.

## Important APIs, types, and functions
Global state includes RCU-protected `cfg80211_rdev_list`, `cfg80211_rdev_list_generation`, `cfg80211_wq`, and the top debugfs directory. Public APIs include `wiphy_new_nm()`, `wiphy_register()`, `wiphy_unregister()`, `wiphy_free()`, `cfg80211_register_netdevice()`, `cfg80211_unregister_wdev()`, `cfg80211_shutdown_all_interfaces()`, `cfg80211_leave()`, `cfg80211_stop_link()`, and work helpers such as `wiphy_work_queue()`, delayed work, and hrtimer work variants.

Validation helpers enforce driver operation pairs, interface combinations, NAN/P2P/mesh/AP constraints, supported bands, rates, 6 GHz HE/EHT rules, vendor command policies, WoWLAN settings, regulatory flag combinations, AKM limits, and multi-radio allocation.

## Control flow
`wiphy_new_nm()` allocates `struct cfg80211_registered_device`, assigns a `phy%d` or requested name, initializes locks/lists/work items/rfkill/default parameters, and returns the embedded `struct wiphy`. `wiphy_register()` performs extensive sanity checks, initializes channel original flags, sets bitrate flags, allocates radio config, adds the device, links it into `cfg80211_rdev_list`, creates debugfs, notifies nl80211, registers regulatory state, marks registered, and registers rfkill. On failure it unwinds through the caller-visible lifecycle.

`wiphy_unregister()` waits for open interfaces to close, unregisters rfkill, removes the wiphy from userspace visibility, deletes debugfs and the RCU list entry, deregisters regulatory state, deletes the device, drains work, and frees auxiliary cfg80211 state. The netdevice notifier initializes wdevs on post-init, registers/unregisters interfaces, handles going-down leave/disconnect/scan cancellation, updates running counters on up/down, rejects pre-up when iftype or rfkill constraints fail, and handles WEXT or mesh compatibility starts.

Module init registers pernet operations, sysfs, netdevice notifier, nl80211, debugfs, regulatory support, and the ordered cfg80211 workqueue. Exit reverses those registrations.

## State and persistence
State is in memory: registered wiphys, wdev lists, opencounts, scan and scheduled scan requests, rfkill state, BSS lists, work queues, management registrations, DFS background work, and per-wdev event lists. There is no persistent storage, but sysfs/debugfs/netlink expose live state.

## Dependencies and integration points
This file integrates with nl80211, sysfs, debugfs, rfkill, regulatory core, netdevice notifier, pernet operations, WEXT compatibility, driver `cfg80211_ops`, and all mode-specific helpers. RTNL, wiphy mutexes, RCU, spinlocks, workqueues, delayed work, and hrtimers are central synchronization primitives.

## Risks
Registration ordering is high risk because userspace visibility must not occur before validation and initialization are complete. Unregister must drain work after removing discoverability to prevent use-after-free. Netdev notifier paths must balance opencount and running interface counters and must cancel scans, scheduled scans, CAC, PMSR, and disconnect work. Multi-radio and MLO paths add validation complexity.

## Test signals
Coverage should include wiphy registration failure injection, invalid capability matrices, namespace switching rollback, rfkill shutdown, netdev up/down/unregister, pending scan cancellation, workqueue cancellation/flush, module init failure unwinds, and debugfs/regulatory/nl80211 notification ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/core.h -->
# sources/distributed-fs/ceph-client/net/wireless/core.h

## Purpose
This header defines cfg80211 internal data structures and function prototypes shared by wireless core files. It is the private contract between cfg80211 lifecycle, scan, MLME, SME, regulatory, channel, mesh, IBSS, PMSR, and debugfs code.

## Important APIs, types, and functions
`struct cfg80211_registered_device` wraps driver ops, global list linkage, rfkill, regulatory state, wiphy index, opencount, beacon registrations, scan/BSS state, scheduled scans, current command info, connection/event work, DFS/background CAC work, management registration lock/work, wiphy work queue, suspend state, and the embedded `struct wiphy`.

Other key structures include `cfg80211_scan_request_int`, `cfg80211_internal_bss`, `cfg80211_event`, `cfg80211_cached_keys`, `cfg80211_beacon_registration`, `cfg80211_cqm_config`, and `cfg80211_colocated_ap`. Inline helpers include `wiphy_to_rdev()`, `cfg80211_rdev_free_wowlan()`, `cfg80211_assign_cookie()`, `cfg80211_hold_bss()`, `cfg80211_unhold_bss()`, `cfg80211_has_monitors_only()`, and `elapsed_jiffies_msecs()`.

The header declares internal APIs for wiphy lookup, netns switching, wdev registration, IBSS, mesh, AP stop, MLME auth/assoc/deauth/disassoc/mgmt TX, SME events, scan, scheduled scan, DFS, CAC, monitor channels, interface counts, leave paths, NAN/P2P stop, PMSR, MLO link removal/reconfiguration, and colocated AP parsing under KUnit.

## Control flow
The header does not execute runtime flow, but it defines the shared state machine vocabulary. Registered devices own wdevs, BSS entries, work items, and driver ops. Mode-specific code updates pieces of `wireless_dev` state and calls prototypes declared here while core code handles registration, locking, and teardown.

## State and persistence
All state described here is in-kernel memory. RCU, spinlocks, RTNL, and the wiphy mutex protect different fields. No durable persistence exists.

## Dependencies and integration points
It depends on kernel networking headers, debugfs, rfkill, generic netlink, public cfg80211 headers, and `reg.h`. Every cfg80211 internal source file relies on this header for type layout and prototypes.

## Risks
Because this is a private central header, struct layout or locking-contract changes have broad blast radius. Misdocumented ownership of BSS refs, wdev lists, or work items can create leaks or use-after-free bugs. KUnit-only exports must stay aligned with test configuration.

## Test signals
Compile coverage across config variants is essential. Runtime signals include lockdep, KASAN/KCSAN, BSS refcount assertions, wiphy work cancellation tests, WoWLAN cleanup, and MLO link state tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/debugfs.c -->
# sources/distributed-fs/ceph-client/net/wireless/debugfs.c

## Purpose
This file creates cfg80211 debugfs entries for wiphy and per-radio parameters and provides helper wrappers for debugfs read/write handlers that must run under the wiphy lock.

## Important APIs, types, and functions
Readonly debugfs macros generate files for `rts_threshold`, `fragmentation_threshold`, `short_retry_limit`, `long_retry_limit`, and per-radio `radio_rts_threshold`. `ht40allow_map_read()` emits per-channel HT40 plus/minus availability or disabled state. `cfg80211_debugfs_rdev_add()` creates the files under the wiphy debugfs directory and per-radio directories.

`wiphy_locked_debugfs_read()` and `wiphy_locked_debugfs_write()` allocate on-stack work descriptors, queue a `wiphy_work`, enter debugfs cancellation, wait for completion, and then copy results to/from userspace. Their worker functions call caller-supplied handlers while the wiphy work context holds the lock.

## Control flow
Registration-time setup calls `cfg80211_debugfs_rdev_add()`. Simple readonly files directly format current wiphy fields. Locked helper reads zero the output buffer, queue work, wait, validate handler length, and return through `simple_read_from_buffer()`. Locked writes enforce NUL-terminated input by requiring `count < bufsize`, copy from userspace, queue work, and return the handler result.

## State and persistence
Debugfs exposes live in-memory cfg80211 state. The helpers use temporary stack work structures and completions; no persistent file-local state is stored.

## Dependencies and integration points
The file depends on debugfs, cfg80211 wiphy work helpers, and registered-device debugfs directories created by `core.c`. It is compiled only when `CONFIG_CFG80211_DEBUGFS` is enabled.

## Risks
Handlers must not return more bytes than the provided buffer. Cancellation must complete pending work to avoid a hung debugfs file operation. The HT40 map is bounded to one page, so very large channel lists may truncate output by construction.

## Test signals
Debugfs tests should read all generated files, exercise locked read/write cancellation during device removal, verify permission modes, and run lockdep while handlers access wiphy state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/debugfs.h -->
# sources/distributed-fs/ceph-client/net/wireless/debugfs.h

## Purpose
This header gates cfg80211 debugfs registration behind `CONFIG_CFG80211_DEBUGFS`.

## Important APIs, types, and functions
When debugfs is enabled, it declares `cfg80211_debugfs_rdev_add(struct cfg80211_registered_device *rdev)`. Otherwise it provides an empty inline function with the same name.

## Control flow
Callers can unconditionally call `cfg80211_debugfs_rdev_add()` from registration code. The preprocessor selects either the real implementation or the no-op.

## State and persistence
The header stores no state and creates no files by itself.

## Dependencies and integration points
It depends on `struct cfg80211_registered_device` from cfg80211 internals and is included by `core.c`.

## Risks
The no-op must remain signature-compatible with the real function. Missing the config guard would either break builds without debugfs or accidentally expose debugfs code.

## Test signals
Build cfg80211 with `CONFIG_CFG80211_DEBUGFS=y` and without it, verifying that registration compiles and works in both cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ethtool.c -->
# sources/distributed-fs/ceph-client/net/wireless/ethtool.c

## Purpose
This file fills ethtool driver information for wireless netdevices backed by cfg80211.

## Important APIs, types, and functions
`cfg80211_get_drvinfo()` reads `dev->ieee80211_ptr`, finds the parent `wiphy` device, and fills `struct ethtool_drvinfo` fields: driver name from the parent device driver or `"N/A"`, kernel release as version, wiphy firmware version or `"N/A"`, and bus info from `dev_name(pdev)`.

## Control flow
The function performs straightforward field population with `strscpy()` and is exported for wireless drivers or netdev ethtool ops to reuse.

## State and persistence
It reads live device and wiphy metadata only. No state is changed.

## Dependencies and integration points
It depends on `linux/utsname.h`, public cfg80211 structures, and device model metadata. It integrates cfg80211 devices with ethtool `get_drvinfo`.

## Risks
The function assumes `dev->ieee80211_ptr` and its wiphy are valid for the caller. Driver and firmware strings must be bounded by `strscpy()` sizes, which the code does.

## Test signals
Call ethtool on devices with and without parent driver names and with empty/non-empty `fw_version`, verifying returned strings and bus info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ibss.c -->
# sources/distributed-fs/ceph-client/net/wireless/ibss.c

## Purpose
This file implements cfg80211 IBSS/ad-hoc join, joined notification, leave, cleanup, and WEXT compatibility operations.

## Important APIs, types, and functions
`__cfg80211_join_ibss()` validates state, derives default basic rates, stores cached WEP keys, records the chandef, and calls `rdev_join_ibss()`. `__cfg80211_ibss_joined()` updates the current BSS reference, uploads cached keys, and notifies nl80211/WEXT. `cfg80211_ibss_joined()` queues that event through the wdev event list. `cfg80211_clear_ibss()` releases keys, QoS map, default keys, BSS refs, SSID/chandef state, and schedules DFS update. `cfg80211_leave_ibss()` calls `rdev_leave_ibss()` and clears state.

WEXT helpers support automatic channel selection, frequency get/set, ESSID get/set, and AP/BSSID get/set.

## Control flow
Join rejects active CAC, already joined state, invalid cached keys, or missing driver support. If no basic rates were configured, it selects mandatory 11a rates for 5/6 GHz or 11b rates otherwise. On successful driver join, it copies SSID state. Joined events later resolve the BSS from scan cache and transfer the active BSS reference into `wdev->u.ibss.current_bss`.

Leave requires an active SSID, delegates to the driver, clears connection owner, and resets IBSS state. WEXT setters leave an existing IBSS before changing channel, SSID, or fixed BSSID, then attempt a new join if enough state and netdev running state are present.

## State and persistence
IBSS state lives in `wdev->u.ibss`, `wdev->connect_keys`, WEXT compatibility fields, and held BSS references. There is no durable persistence.

## Dependencies and integration points
The file depends on nl80211 notifications, WEXT compatibility when enabled, scan/BSS helpers, DFS scheduling, QoS map operations, and driver ops from `rdev-ops.h`.

## Risks
BSS reference ownership is critical during joined and clear paths. WEXT automatic channel selection must avoid disabled and NO_IR channels. Cached key memory contains sensitive material and must be freed with `kfree_sensitive()`. DFS updates must follow leave/clear.

## Test signals
Tests should cover join defaults by band, missing driver ops, CAC busy rejection, duplicate join, joined event without BSS, leave without connection, WEXT channel/SSID/BSSID changes, key cleanup, and BSS refcount balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ibss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/mesh.c -->
# sources/distributed-fs/ceph-client/net/wireless/mesh.c

## Purpose
This file provides cfg80211 mesh defaults and join/leave/channel setup helpers for mesh point interfaces.

## Important APIs, types, and functions
`default_mesh_config` and `default_mesh_setup` define HWMP, TTL, retry, peer link, power mode, beacon interval, DTIM, and security defaults. `__cfg80211_join_mesh()` validates mesh interface state, security support, mesh ID, driver support, CAC state, channel selection, basic rates, DFS requirements, regulatory beacon permission, then calls `rdev_join_mesh()`. `cfg80211_set_mesh_channel()` either invokes a legacy libertas driver hook or stores a preset chandef before join. `cfg80211_leave_mesh()` delegates to the driver and clears mesh state.

## Control flow
Join uses an explicitly supplied channel, then a preset channel, then the first usable non-NO_IR, non-disabled, non-radar channel. If no basic rates are set, 2.4 GHz uses 1 Mbps compatibility behavior while other bands use mandatory rates. DFS-required channels are rejected unless userspace handles DFS. Regulatory beacon permission is checked before driver join.

## State and persistence
Mesh state is stored in `wdev->u.mesh`: mesh ID, chandef, beacon interval, and preset chandef. Leave clears active ID and chandef and resets QoS map. Defaults are static const data.

## Dependencies and integration points
The file depends on channel/regulatory helpers, DFS scheduling, nl80211 mesh types, and driver `join_mesh`, `leave_mesh`, or legacy `libertas_set_mesh_channel` ops.

## Risks
Automatic channel selection must not choose radar/NO_IR/disabled channels. DFS userspace-handling requirements must be enforced before beaconing. The libertas workaround is intentionally nonstandard and should remain isolated.

## Test signals
Cover join with explicit, preset, and automatic channels; secure mesh without auth support; missing mesh ID; CAC busy; DFS-required rejection/acceptance with userspace DFS; leave cleanup; and libertas channel restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/mesh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/michael-mic.c -->
# sources/distributed-fs/ceph-client/net/wireless/michael-mic.c

## Purpose
This file implements the TKIP Michael MIC algorithm used for IEEE 802.11 data integrity compatibility.

## Important APIs, types, and functions
`struct michael_mic_ctx` stores the two 32-bit state words. `michael_block()` applies the Michael mixing function over one little-endian 32-bit word. `michael_mic_hdr()` initializes the context from the 8-byte key and folds in the pseudo-header: destination address, source address, QoS TID or zero, and padding. `michael_mic()` processes payload blocks, appends the 0x5a padding block and final zero block, and writes the 8-byte MIC.

## Control flow
The exported function initializes header state, processes each full 4-byte payload block, constructs the partial tail block in Michael padding order, mixes the tail and zero block, then emits little-endian `l` and `r`.

## State and persistence
All state is stack-local. The function reads the key, header, and payload and writes the caller-provided MIC buffer. No persistent state exists.

## Dependencies and integration points
It depends on IEEE 802.11 header helpers, unaligned little-endian accessors, and bit rotations. It is exported with `EXPORT_SYMBOL_GPL` for wireless encryption/TKIP users.

## Risks
Michael MIC is cryptographically weak but required for TKIP compatibility. Correct byte ordering and padding are essential for interoperability. Callers must supply valid key, header, data, and output buffers.

## Test signals
Use known TKIP Michael MIC test vectors, QoS and non-QoS frames, payload lengths 0 through multiple block boundaries, unaligned data buffers, and endian-sensitive checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/michael-mic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/mlme.c -->
# sources/distributed-fs/ceph-client/net/wireless/mlme.c

## Purpose
This file implements cfg80211 MLME service access helpers: association response processing, auth/deauth/disassoc event handling, userspace SME auth/assoc requests, management frame registration and TX/RX dispatch, Michael MIC failure reporting, DFS channel timers, radar/CAC events, background CAC, and MLO reconfiguration completion.

## Important APIs, types, and functions
Event ingress includes `cfg80211_rx_assoc_resp()`, `cfg80211_rx_mlme_mgmt()`, `cfg80211_auth_timeout()`, `cfg80211_assoc_failure()`, `cfg80211_tx_mlme_mgmt()`, and `cfg80211_michael_mic_failure()`. Userspace SME requests include `cfg80211_mlme_auth()`, `cfg80211_mlme_assoc()`, `cfg80211_mlme_deauth()`, `cfg80211_mlme_disassoc()`, and `cfg80211_mlme_down()`.

Management frame state uses `struct cfg80211_mgmt_registration`, `cfg80211_mlme_register_mgmt()`, `cfg80211_mlme_unregister_socket()`, `cfg80211_mlme_purge_registrations()`, `cfg80211_mlme_mgmt_tx()`, and `cfg80211_rx_mgmt_ext()`. DFS/radar functions include `cfg80211_sched_dfs_chan_update()`, `cfg80211_dfs_channels_update_work()`, `__cfg80211_radar_event()`, `cfg80211_cac_event()`, background CAC helpers, and stop functions. MLO helpers include `cfg80211_mlme_check_mlo()`, `cfg80211_assoc_ml_reconf()`, and `cfg80211_mlo_reconf_add_done()`.

## Control flow
Association responses are converted into `cfg80211_connect_resp_params`, including per-link BSS/address/status data for MLO, sent to userspace, then consumed by the SME connection-result path unless SME retry logic suppresses a reassoc rejection. Auth/deauth/disassoc frames are classified by frame control and routed to nl80211 notifications plus SME state updates. Auth and association requests validate BSS presence, MLO link compatibility, local address conflicts, shared-key requirements, connected state, and capability masks before calling driver ops.

Management registration validates frame type, supported stypes, station auth match specificity, and duplicate matches under `mgmt_registrations_lock`, then updates driver registration bitmasks. RX matching compares frame type and match bytes after the 802.11 header and sends matching frames to the owning netlink port. TX validates frame class, supported TX stypes, interface-mode addressing rules, random transmitter-address feature bits, and driver support before `rdev_mgmt_tx()`.

DFS work scans all channels for NOP expiry or pre-CAC expiry, updates states to usable, notifies nl80211, propagates regulatory state, and reschedules for the next timeout. Radar detection marks affected channels unavailable, aborts offchannel CAC if needed, schedules DFS updates, notifies userspace, and propagates state. CAC start/finish/abort updates per-link CAC flags and channel CAC timestamps. Background CAC owns one offchannel chain per rdev and schedules delayed completion.

## State and persistence
State is in memory: wdev connection flags and current BSS refs, management registration lists, `crit_proto_nlportid`, `unexpected_nlportid`, per-channel DFS/CAC state, per-link CAC fields, background radar owner/chandef, delayed work, and MLO valid link masks. No durable persistence exists.

## Dependencies and integration points
The file integrates with nl80211 notifications, SME helpers, scan/BSS refcounting, driver ops, regulatory propagation, channel helpers, WEXT notifications, cfg80211 workqueue, wiphy locking, RTNL in DFS work, and MLO IEEE 802.11 element parsing.

## Risks
BSS reference ownership across assoc success/failure and MLO link addition is high risk. Management registration matching can leak or stale-program driver filters if socket unregister and purge paths miss updates. DFS timers and background CAC must avoid legal-state regressions and races with interface shutdown. Address validation for management TX must remain aligned with new MLO addressing rules.

## Test signals
Cover association success/reject/failure, MLO link mismatch extack paths, auth/deauth/disassoc local and AP-originated flows, management registration duplicates and socket cleanup, management TX per iftype, DFS NOP/pre-CAC expiry, radar during background CAC, CAC start/finish/abort, interface shutdown during CAC, and BSS refcount balance under KASAN/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/mlme.c -->
