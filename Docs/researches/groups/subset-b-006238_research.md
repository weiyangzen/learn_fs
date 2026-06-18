<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/subflow.c -->
# sources/distributed-fs/ceph-client/net/mptcp/subflow.c

## Purpose
This file is the core MPTCP subflow glue between ordinary TCP sockets and an owning `struct mptcp_sock`. It overrides TCP request, address-family, protocol, and ULP callbacks so MP_CAPABLE and MP_JOIN handshakes can create or attach subflows, then validates DSS mappings on the receive path before data is exposed to the MPTCP-level socket.

## APIs, Types, and Functions
Exported or externally used entry points include `mptcp_subflow_init_cookie_req()`, `mptcp_subflow_reset()`, `__mptcp_sync_state()`, `mptcp_subflow_reqsk_alloc()`, `mptcp_subflow_drop_ctx()`, `__mptcp_subflow_fully_established()`, `mptcp_subflow_data_available()`, `mptcp_space()`, `mptcpv6_handle_mapped()`, `mptcp_info2sockaddr()`, `__mptcp_subflow_connect()`, cgroup inheritance helpers, `mptcp_subflow_create_socket()`, `mptcp_subflow_queue_clean()`, `mptcp_subflow_init()`, and `mptcp_subflow_v6_init()`. Important callback families are `subflow_v4_route_req()`/`subflow_v6_route_req()`, `subflow_*_send_synack()`, `subflow_syn_recv_sock()`, `subflow_finish_connect()`, `subflow_data_ready()`, `subflow_state_change()`, `subflow_ulp_init()`, `subflow_ulp_clone()`, and `subflow_ulp_release()`. `enum mapping_status` classifies receive-side mapping outcomes as OK, invalid, empty, DATA_FIN, fallback dummy, bad checksum, or missing DSS.

## Control Flow
Passive opens start with TCP request allocation redirected to MPTCP-sized request sockets. `subflow_check_req()` parses MPTCP SYN options, rejects prohibited endpoint-manager listener attempts, allocates MP_CAPABLE tokens, resolves MP_JOIN tokens to an existing MPTCP socket, records nonces and local IDs, and stores syncookie JOIN state when needed. ACK processing enters `subflow_syn_recv_sock()`, which clones a TCP child, either creates a new MPTCP parent for MP_CAPABLE or attaches the child to an existing MPTCP socket for MP_JOIN after HMAC and policy checks, and falls back or sends resets for invalid cases.

Active opens complete through `subflow_finish_connect()`. MP_CAPABLE SYN/ACKs establish keys, checksum policy, remote join-id policy, and parent socket state. MP_JOIN SYN/ACKs verify truncated HMAC, record remote nonce/id/backup status, call `mptcp_finish_join()`, and prepare the final HMAC for the third ACK. Additional subflows are opened by `__mptcp_subflow_connect()`, which creates a kernel TCP socket, attaches the MPTCP ULP, syncs sockopts, binds the local address, sends an MP_JOIN connect, and grafts the subflow into the parent socket.

The receive path is driven by `subflow_data_ready()`, `subflow_state_change()`, and `mptcp_subflow_data_available()`. `get_mapping_status()` reads MPTCP skb extensions, installs DSS mapping state, handles DATA_FIN, rejects infinite or mismatched mappings, verifies TCP subflow sequence coverage, and optionally validates DSS checksums across queued skbs. `subflow_check_data_avail()` advances duplicate data, marks data available, enters RFC 8684 checksum failure handling via MP_FAIL when possible, or tries TCP fallback/reset on middlebox-like corruption.

## State and Persistence
Runtime state lives in `struct mptcp_subflow_context` attached as TCP ULP data, in request-sock `struct mptcp_subflow_request_sock`, in parent `struct mptcp_sock`, and in TCP socket queues. Persistent per-subflow fields include local/remote keys, token, nonces, subflow IDs, backup/request flags, local and remote IDs, sequence offsets, current DSS map, checksum accumulator, fallback/failure flags, delegated work state, and saved TCP callbacks. Init functions build alternate request-sock caches and AF/proto callback tables marked `__ro_after_init`; ULP registration is process-wide.

## Dependencies and Integration
The file depends heavily on TCP core request handling, inet/IPv6 AF ops, `tcp_set_ulp()`, MPTCP crypto/token/path-manager helpers, MPTCP work scheduling, MIB counters, tracepoints, cgroup and memcg socket inheritance, LSM `security_mptcp_add_subflow()`, and optional IPv6 and BPF config paths. It is the integration point where Linux TCP sockets become MPTCP subflows and where receive-side TCP data is promoted to MPTCP data.

## Risks
The highest-risk areas are handshake fallback versus fatal reset decisions, ownership transfer of `subflow_req->msk`, lock ordering around listener accept queues and parent sockets, checksum validation across multiple queued skbs, syncookie JOIN reconstruction, and callback/proto restoration during fallback or release. Mapping validation has little tolerance for middlebox-dropped DSS options and can close sockets with `EBADMSG`. Request and child disposal paths rely on exact refcount and list semantics.

## Test Signals
Signals include MPTCP selftests covering MP_CAPABLE, MP_JOIN, backup subflows, port mismatch, fallback, DSS checksum, DATA_FIN, IPv6/v4-mapped behavior, reset reasons, and path-manager policy. Runtime counters such as `MPTCP_MIB_JOIN*`, `MPTCP_MIB_DSS*`, `MPTCP_MIB_DATACSUMERR`, and tracepoints (`trace_get_mapping_status`, `trace_subflow_check_data_avail`) are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/subflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/syncookies.c -->
# sources/distributed-fs/ceph-client/net/mptcp/syncookies.c

## Purpose
This file provides best-effort server-side state recovery for MP_JOIN requests when TCP syncookies are used. MP_CAPABLE cookie ACKs carry enough MPTCP material to rebuild request state, but MP_JOIN cookie ACKs do not carry the original token or server nonce, so this file stores a small hash-indexed side table for later reconstruction.

## APIs, Types, and Functions
`struct join_entry` stores token, remote nonce, local nonce, remote join ID, local ID, backup bit, and a valid flag. `COOKIE_JOIN_SLOTS` fixes the table at 1024 entries. Public functions are `subflow_init_req_cookie_join_save()`, `mptcp_token_join_cookie_init_state()`, and `mptcp_join_cookie_init()`. Helpers include `mptcp_join_entry_hash()` and `mptcp_join_store_state()`.

## Control Flow
On an MP_JOIN SYN that has passed token lookup and policy checks but is handled through syncookies, `subflow_init_req_cookie_join_save()` hashes the skb tuple, sequence, net namespace mix, and a random secret to pick a table slot, then stores the request's JOIN state under that slot lock. Later, after TCP validates the cookie ACK, `mptcp_token_join_cookie_init_state()` hashes the ACK in the same way, consumes the slot by clearing `valid`, looks up the saved token with `mptcp_token_get_sock()`, and repopulates the new request socket before later HMAC validation in `subflow.c`.

## State and Persistence
State is only the global `join_entries[]` table and one spinlock per slot. Entries have no timeout and are invalidated only when a matching cookie ACK consumes them or another SYN overwrites the slot. The socket reference returned by `mptcp_token_get_sock()` is stored into `subflow_req->msk` for the normal subflow accept path.

## Dependencies and Integration
The file depends on TCP skb sequence metadata, TCP headers, `jhash_3words()`, `net_hash_mix()`, per-net randomization, MPTCP request context definitions, and token lookup. It is called by `subflow_check_req()` while preparing syncookie MP_JOIN SYN/ACKs and by `mptcp_subflow_init_cookie_req()` while rebuilding request state from the cookie ACK.

## Risks
The table is intentionally lossy: slot collisions, cross-CPU races, ACKs arriving after overwrite, or any mismatch in SYN/ACK hash inputs cause JOIN failure. There is no expiration or namespace-specific table separation beyond the hash input. A valid slot is cleared before token lookup completes, so a racing duplicate ACK will not reuse it.

## Test Signals
Useful tests force TCP syncookie mode and attempt MP_JOIN joins, including collision-like high-rate joins, invalid token joins, backup/id propagation, and namespace isolation. Failure should appear as refused MP_JOIN rather than memory corruption or stale socket attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/syncookies.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/token.c -->
# sources/distributed-fs/ceph-client/net/mptcp/token.c

## Purpose
This file owns the global MPTCP token registry. It maps 32-bit tokens to either pending passive MP_CAPABLE requests or established `struct mptcp_sock` objects so MP_JOIN SYNs and diagnostic iteration can locate the correct MPTCP connection.

## APIs, Types, and Functions
The central type is `struct token_bucket`, containing a spinlock, bounded chain length, a request chain, and a socket chain. Public APIs are `mptcp_token_new_request()`, `mptcp_token_new_connect()`, `mptcp_token_accept()`, `mptcp_token_exists()`, `mptcp_token_get_sock()`, `mptcp_token_iter_next()`, `mptcp_token_destroy_request()`, `mptcp_token_destroy()`, and `mptcp_token_init()`. Helpers `__token_lookup_req()`, `__token_lookup_msk()`, `__token_bucket_busy()`, and `mptcp_crypto_key_gen_sha()` implement hashing and collision checks.

## Control Flow
Passive MP_CAPABLE handling calculates token and IDSN from a previously generated local key and inserts the request into the bucket's request hlist if the token is nonzero, unique, and the bucket chain has fewer than `TOKEN_MAX_CHAIN_LEN` entries. Active MP_CAPABLE handling generates random keys until a usable token is found, stores the token into the parent MPTCP socket, links the socket in the msk chain, and increments protocol in-use accounting. On accept, `mptcp_token_accept()` removes the request node and inserts the fully cloned MPTCP socket under the same token.

Lookup uses RCU and nulls hlist traversal. `mptcp_token_get_sock()` restricts matches to the caller's network namespace and takes a reference only if `sk_refcnt` is nonzero, then revalidates token and namespace after acquiring the ref. Iteration walks buckets and per-bucket positions for proc/diagnostic style consumers. Destroy paths remove either request nodes or socket nodes under bucket lock and maintain chain length and protocol accounting.

## State and Persistence
The registry is a boot-time `alloc_large_system_hash()` allocation sized roughly by memory and capped at 64K buckets. Each bucket stores pending requests and established MPTCP sockets until request destruction, accept transition, or MPTCP socket teardown. Per-socket token fields are cleared on destroy.

## Dependencies and Integration
Dependencies include MPTCP crypto key hashing, request and socket context accessors from `protocol.h`, RCU nulls lists, spinlocks, network namespace checks, random bytes, and socket protocol accounting. `subflow.c` uses this file for MP_CAPABLE token creation, MP_JOIN token lookup, syncookie uniqueness checks, and request cleanup.

## Risks
Token collisions intentionally fail after bounded retries or trigger TCP fallback on passive open. Chain length limiting can reject connections under adversarial token distribution. Lookup correctness depends on RCU/nulls retry semantics and reference revalidation. Destroy paths warn if registry state does not match expected ownership, which would imply a token lifecycle bug.

## Test Signals
`token_test.c` covers request insertion, active connect insertion, accept transition, destroy no-op behavior after accept, and zero-ref lookup races. Broader signals include MP_JOIN success under concurrent connects, namespace isolation, collision retry behavior, and absence of leaked protocol in-use counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/token_test.c -->
# sources/distributed-fs/ceph-client/net/mptcp/token_test.c

## Purpose
This file is the KUnit suite for MPTCP token management. It builds minimal fake request sockets, TCP inet connection sockets, subflow contexts, and MPTCP sockets to validate token registry lifecycle behavior without a real network handshake.

## APIs, Types, and Functions
Helpers are `build_req_sock()`, `build_icsk()`, `build_ctx()`, and `build_msk()`. Test cases are `mptcp_token_test_req_basic()`, `mptcp_token_test_msk_basic()`, `mptcp_token_test_accept()`, and `mptcp_token_test_destroyed()`. The suite is registered as `mptcp-token` with `kunit_test_suite()`.

## Control Flow
The request test initializes a fake `mptcp_subflow_request_sock`, creates a request token, checks that the token is nonzero but not visible as an established socket, then destroys the request. The active socket test attaches a fake subflow context to an `inet_connection_sock`, creates a token for the MPTCP socket, checks lookup and refcount behavior, destroys the token, and verifies lookup failure. The accept test transitions a request token into a full MPTCP socket and verifies request destroy becomes a no-op after the move. The destroyed test simulates a race by setting the socket refcount to zero before lookup and expects no socket to be returned.

## State and Persistence
All objects are KUnit-managed heap allocations, but they interact with the real global token hash initialized by the MPTCP token subsystem. Fake sockets set `sk_refcnt`, net namespace, `sk_prot`, and protocol fields only as far as token helpers require.

## Dependencies and Integration
The file depends on KUnit, `protocol.h`, `init_net`, `tcp_prot`, and token helper exports available under `CONFIG_MPTCP_KUNIT_TEST` when built as a module. It directly tests the code in `token.c`.

## Risks
The suite intentionally avoids full TCP/MPTCP socket initialization, so it does not cover RCU grace periods, real request destruction, concurrent bucket mutation, namespace mismatches, token collision retry loops, or protocol accounting in an integrated stack. Fake objects must stay consistent with what token helpers dereference.

## Test Signals
Strong signals are nonzero token creation, expected lookup visibility before and after accept, refcount increments on successful lookup, no-op request destroy after accept, and refusal to return a zero-ref socket.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/token_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/Kconfig -->
# sources/distributed-fs/ceph-client/net/ncsi/Kconfig

## Purpose
This Kconfig file exposes build-time options for Linux NCSI support and optional vendor OEM commands. NCSI is used by systems where a host network controller communicates with a management controller over the Network Controller Sideband Interface.

## APIs, Types, and Functions
The symbols are `NET_NCSI`, `NCSI_OEM_CMD_GET_MAC`, and `NCSI_OEM_CMD_KEEP_PHY`. `NET_NCSI` is a boolean depending on `INET`. The two OEM options depend on `NET_NCSI`; one enables retrieving MAC addresses from NCSI firmware and applying them to the controller, and the other enables Intel keep-PHY-link behavior during host load.

## Control Flow
There is no runtime control flow here. The selected symbols determine whether the NCSI object files are built and whether conditional branches in `ncsi-manage.c` issue OEM Get MAC Address or Keep PHY commands during probe/configuration.

## State and Persistence
The file contributes static kernel configuration state. Once built, these booleans shape compiled code paths and cannot change at runtime.

## Dependencies and Integration
`NET_NCSI` integrates with the networking stack and Ethernet drivers that explicitly register an NCSI device through the public NCSI API. The OEM symbols gate code paths using vendor IDs and command payload definitions from `internal.h`.

## Risks
Because NCSI is board/platform specific, enabling it without driver support has no useful effect. Enabling OEM commands on unsupported firmware should degrade through command failure paths, but vendor payload format mistakes can affect MAC assignment or PHY reset behavior.

## Test Signals
Build matrix coverage should include `NET_NCSI=n`, `NET_NCSI=y` without OEM options, and each OEM option enabled. Runtime signals are successful NCSI probing, MAC assignment when Get MAC is enabled, and absence of undesired PHY resets when Keep PHY is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/Makefile -->
# sources/distributed-fs/ceph-client/net/ncsi/Makefile

## Purpose
This Makefile wires the NCSI implementation into the kernel build when `CONFIG_NET_NCSI` is enabled.

## APIs, Types, and Functions
It appends `ncsi-cmd.o`, `ncsi-rsp.o`, `ncsi-aen.o`, `ncsi-manage.o`, and `ncsi-netlink.o` to `obj-$(CONFIG_NET_NCSI)`.

## Control Flow
There is no runtime logic. The object list defines the implementation units for command construction, response parsing, asynchronous event handling, device/channel management, and generic netlink control.

## State and Persistence
The only state is build-system state. If `CONFIG_NET_NCSI` is disabled, none of these translation units are built.

## Dependencies and Integration
The object grouping must stay aligned with declarations in `internal.h`, packet definitions in `ncsi-pkt.h`, public UAPI netlink definitions, and callers from NCSI-aware Ethernet drivers.

## Risks
Missing any listed object would leave unresolved symbols or a partially functional subsystem. Adding new NCSI implementation files requires this Makefile to be updated under the same config symbol.

## Test Signals
Build tests with `CONFIG_NET_NCSI=y` should link all NCSI symbols, including netlink registration, exported device lifecycle APIs, packet TX/RX handlers, and AEN handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/internal.h -->
# sources/distributed-fs/ceph-client/net/ncsi/internal.h

## Purpose
This header defines the private NCSI subsystem model: package/channel topology, capabilities, modes, statistics, request tracking, state-machine values, OEM constants, and internal function prototypes shared by the NCSI implementation files.

## APIs, Types, and Functions
Important enums define capability indexes and bit masks (`NCSI_CAP_*`), mode indexes (`NCSI_MODE_*`), Mellanox media bits, and `ncsi_dev_state_*` probe/config/suspend states. OEM constants cover Mellanox, Broadcom, and Intel manufacturer IDs, command IDs, payload lengths, and MAC offsets. Core structs include `ncsi_channel_version`, `ncsi_channel_cap`, `ncsi_channel_mode`, MAC/VLAN filter structs, `ncsi_channel_stats`, `ncsi_channel`, `ncsi_package`, `ncsi_request`, `vlan_vid`, `ncsi_dev_priv`, and `ncsi_cmd_arg`. Prototypes cover device reset, monitor control, topology lookup/allocation, request allocation, command transmission, response receipt, and AEN handling.

## Control Flow
The header has no executable flow, but it encodes the state machine used by `ncsi-manage.c`: probe states enumerate packages/channels and gather version/capability/link data; config states select packages, clear state, program filters, enable TX/channel/AEN, and read link status; suspend states disable TX/channel and optionally deselect packages. The `ncsi_request` flags distinguish event-driven management commands from netlink-driven user commands.

## State and Persistence
`ncsi_dev_priv` is the persistent per-netdev private object. It tracks global flags (`PROBED`, `HWA`, `RESHUFFLE`, `RESET`), discovered packages, active package/channel, pending request count, request ID cursor, queue of channels awaiting config/suspend, packet receive registration, VLAN list, whitelist/multi-package settings, and Mellanox multi-host state. `ncsi_package` persists channel lists, whitelists, preferred channel, UUID, and multi-channel mode. `ncsi_channel` persists capabilities, modes, filters, statistics, monitor timer state, and active/inactive/invisible state.

## Dependencies and Integration
The header depends on kernel networking types, generic netlink request metadata, timers, spinlocks, lists, and the public `struct ncsi_dev`. It is included by command, response, AEN, management, and netlink code and forms their shared ABI boundary inside `net/ncsi`.

## Risks
Many fields are shared across IRQ, timer, workqueue, packet receive, and netlink contexts. Correct lock use around `ndp->lock`, package locks, channel locks, RCU list traversal, and request timer state is critical. OEM constants and packet offsets must match vendor firmware formats. State enum values are used by bitmasking major/minor state, so accidental renumbering can break dispatch.

## Test Signals
Compile-time consumers exercise structure visibility. Runtime signals are successful discovery of packages/channels, correct channel state transitions, stable request allocation/freeing, VLAN and MAC filter persistence, and netlink reporting matching internal topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-aen.c -->
# sources/distributed-fs/ceph-client/net/ncsi/ncsi-aen.c

## Purpose
This file handles NCSI asynchronous event notification packets. It validates AEN packet headers/checksums, updates channel state for link and host-driver events, and triggers failover or reconfiguration when firmware reports link or configuration changes.

## APIs, Types, and Functions
The exported internal entry point is `ncsi_aen_handler()`. Helpers include `ncsi_validate_aen_pkt()`, `ncsi_aen_handler_lsc()` for link status change, `ncsi_aen_handler_cr()` for configuration required, and `ncsi_aen_handler_hncdsc()` for host network controller driver status changes. `ncsi_aen_handlers[]` maps AEN types to expected payload lengths and handlers.

## Control Flow
`ncsi_aen_handler()` reads the skb network header, finds a handler by AEN type, validates revision, length, and checksum, runs the handler, logs errors, and consumes the skb. Link status change handling finds the channel, updates link and OEM status fields, compares previous and new link bits, and then either reshuffles a single-channel setup or updates TX enablement in multi-package/multi-channel setups. Configuration-required handling marks an active, unqueued channel inactive, disables TX mode, queues it, and starts `ncsi_process_next_channel()`. Host-driver-status handling records the firmware status bit and logs whether the host driver is running.

## State and Persistence
AENs mutate `ncsi_channel.modes[NCSI_MODE_LINK]`, `NCSI_MODE_TX_ENABLE`, channel `state`, `link` queue membership, `ndp->flags` such as `NCSI_DEV_RESHUFFLE`, and monitor timers. These changes persist in the per-device topology until later management work reconfigures or suspends channels.

## Dependencies and Integration
The file depends on `internal.h`, `ncsi-pkt.h`, `ncsi_calculate_checksum()`, topology lookup, channel monitors, reset/process helpers, and TX channel update logic in `ncsi-manage.c`. It is called from `ncsi_rcv_rsp()` when a packet type is `NCSI_PKT_AEN`.

## Risks
Failover decisions depend on consistent channel lock and queue state. AENs from inactive channels are only warned about, which is appropriate for firmware noise but can mask sequencing issues. Checksum zero is accepted per spec, so corrupted packets from devices that omit checksums rely on length/revision/type only. Multi-channel update loops must not enable TX on a down or non-whitelisted channel.

## Test Signals
Tests should inject LSC, CR, and HNCDSC packets with good and bad checksums/lengths; verify link mode updates, reshuffle flag behavior, monitor stop/start, queue insertion, reset on last-link loss, and TX channel failover/return-to-preferred behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-aen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-cmd.c -->
# sources/distributed-fs/ceph-client/net/ncsi/ncsi-cmd.c

## Purpose
This file builds and transmits NCSI command packets. It converts `struct ncsi_cmd_arg` requests into correctly sized skb payloads, fills NCSI and Ethernet headers, calculates checksums, allocates request tracking slots, and starts response timers.

## APIs, Types, and Functions
Public internal APIs are `ncsi_calculate_checksum()` and `ncsi_xmit_cmd()`. Static helpers include `ncsi_cmd_build_header()`, one command-specific builder per payload shape (`sp`, `dc`, `rc`, `ae`, `sl`, `svf`, `ev`, `sma`, `ebf`, `egmf`, `snfc`, `oem`, and default), `ncsi_cmd_handlers[]`, and `ncsi_alloc_command()`.

## Control Flow
`ncsi_xmit_cmd()` chooses a handler by command type, forcing the OEM builder for netlink-driven raw commands, derives fixed payload sizes unless the handler declares variable payload, allocates an `ncsi_request`, records netlink reply metadata when needed, builds the packet, prepends an Ethernet header, starts a one-second timer, and queues the skb with `dev_queue_xmit()`. `ncsi_alloc_command()` reserves link-layer headroom and tailroom, sizes the skb for NCSI header, aligned payload, checksum, and minimum Ethernet padding, then associates it with a request slot.

## State and Persistence
State is persisted in the allocated `ncsi_request`: command skb pointer, request ID, flags, timer enabled bit, and optional netlink sequence/port/header. The skb carries the NCSI command until response receipt or timeout frees the request.

## Dependencies and Integration
The file depends on `internal.h`, `ncsi-pkt.h`, Ethernet device properties, generic netlink metadata, `ncsi_alloc_request()`/`ncsi_free_request()`, and device transmit. Command builders are driven by `ncsi-manage.c` state machines and by raw netlink command requests from `ncsi-netlink.c`.

## Risks
Packet sizing and checksum offset must match the NCSI spec, especially for variable-length OEM payloads and 32-bit alignment padding. `unsafe_memcpy()` in the OEM builder assumes prior allocation accounted for caller-provided payload length. Timer/request state must be freed exactly once on TX error, timeout, or response. Broadcast source MAC is used until GMA succeeds, which may matter for devices with stricter filtering.

## Test Signals
Useful signals are byte-for-byte command packet tests for each handler, checksum verification, minimum-frame padding, variable OEM payload alignment, netlink-driven command replies/timeouts, timer cleanup on TX failure, and integration tests that probe/configure real or emulated NCSI channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-manage.c -->
# sources/distributed-fs/ceph-client/net/ncsi/ncsi-manage.c

## Purpose
This file is the NCSI device manager. It owns package/channel discovery, request allocation, link monitoring, channel selection, VLAN/filter programming, OEM command sequencing, reset/suspend/configure state machines, public device lifecycle APIs, and VLAN notifier entry points.

## APIs, Types, and Functions
Externally visible functions include `ncsi_channel_has_link()`, `ncsi_channel_is_last()`, monitor start/stop, topology lookup/add/remove helpers, request allocation/freeing, `ncsi_find_dev()`, `ncsi_process_next_channel()`, `ncsi_update_tx_channel()`, VLAN add/kill exports, `ncsi_register_dev()`, `ncsi_start_dev()`, `ncsi_stop_dev()`, `ncsi_reset_dev()`, and `ncsi_unregister_dev()`. Major static subsystems are `ncsi_channel_monitor()`, `ncsi_request_timeout()`, `ncsi_suspend_channel()`, VLAN filter helpers, OEM GMA/keep-PHY/SMAF helpers, `ncsi_configure_channel()`, `ncsi_choose_active_channel()`, `ncsi_check_hwa()`, `ncsi_probe_channel()`, `ncsi_dev_work()`, and `ncsi_kick_channels()`.

## Control Flow
Drivers call `ncsi_register_dev()` to allocate `ncsi_dev_priv`, initialize requests/timers/work, add the device to the global list, and register an `ETH_P_NCSI` packet handler. `ncsi_start_dev()` launches probing if topology has not been discovered. Probe flow deselects all packages, selects each package, discovers channels with CIS/GVI/GC/GLS, optionally sends Mellanox or Intel OEM commands, deselects packages, then checks hardware arbitration and chooses active channels.

Configuration flow selects a package, clears initial state, optionally retrieves/applies firmware MAC, clears and sets VLAN filters, enables/disables VLAN mode, programs MAC, broadcast and multicast filters, enables TX if selected, enables channel and AEN, reads link status, marks the channel active, starts the monitor, and moves to the next queued channel. Suspend flow selects the package, optionally refreshes link status, disables TX, disables channel, optionally deselects the package, marks the channel inactive, and resumes reset or queue processing. Link monitors periodically send GLS and force reshuffle if a channel stops responding.

## State and Persistence
Persistent state is in `ncsi_dev_priv`, global `ncsi_dev_list`, package/channel lists, request table, VLAN list, active package/channel pointers, `hot_channel`, whitelists, multi-package/channel flags, reset/reshuffle flags, and per-channel filters/modes/monitor timers. Requests persist from command transmit until response or timeout; event-driven request completion decrements `pending_req_num` and schedules the workqueue when a state step is complete.

## Dependencies and Integration
The file integrates with Ethernet drivers through exported NCSI lifecycle APIs, with packet RX through `ncsi_rcv_rsp`, with command TX through `ncsi_xmit_cmd`, with netlink through shared topology and reset helpers, with device tree for Mellanox multi-host detection, and with rtnetlink for MAC assignment. It uses spinlocks, RCU lists, timers, workqueues, skb packet handlers, and VLAN callbacks.

## Risks
This is the highest-risk NCSI file because it combines asynchronous timers, response callbacks, workqueue state machines, netlink mutations, and driver lifecycle. Race-prone areas include request timeout versus response receipt, resetting while config/suspend is in progress, queueing channels under different locks, VLAN list updates while configuration reads it, and unregister while work/timers/packet handlers are active. OEM stack-local payload buffers are safe only because transmission copies synchronously into skb before returning.

## Test Signals
Strong signals include emulated NCSI devices for successful and partial probe, request timeout handling, reset during config, AEN-triggered reshuffle, multi-package hardware-arbitration mode, preferred channel and mask changes through netlink, VLAN add/remove reconfiguration, MAC retrieval/application, channel monitor timeout, and clean unregister with no live timers or work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-manage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.c -->
# sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.c

## Purpose
This file exposes NCSI status and control through generic netlink. It lets users query package/channel topology, choose preferred package/channel, clear preferences, send raw NCSI commands, configure package/channel masks, and receive command responses, timeouts, or errors.

## APIs, Types, and Functions
The generic netlink family is `NCSI`. Policy entries validate ifindex, package/channel IDs, binary command data, multi flags, and masks. Static handlers include `ndp_from_ifindex()`, `ncsi_write_channel_info()`, `ncsi_write_package_info()`, `ncsi_pkg_info_nl()`, `ncsi_pkg_info_all_nl()`, `ncsi_set_interface_nl()`, `ncsi_clear_interface_nl()`, `ncsi_send_cmd_nl()`, `ncsi_set_package_mask_nl()`, and `ncsi_set_channel_mask_nl()`. Exported internal response helpers are `ncsi_send_netlink_rsp()`, `ncsi_send_netlink_timeout()`, and `ncsi_send_netlink_err()`.

## Control Flow
Query handlers resolve an NCSI device by network namespace and ifindex, then serialize package/channel data into nested attributes. Set-interface and clear-interface handlers mutate package/channel whitelists, preferred channel pointers, multi-mode flags, and trigger `ncsi_reset_dev()` to reconfigure hardware. Raw command handling validates package/channel bounds and a minimum NCSI header, derives type and payload from user data, sends the command as netlink-driven, and reports immediate send errors through netlink. Response and timeout helpers construct replies using saved request sequence and port IDs.

## State and Persistence
Netlink commands persist changes in `ncsi_dev_priv.package_whitelist`, `multi_package`, per-package `channel_whitelist`, `multi_channel`, and `preferred_channel`. Raw command requests persist reply routing metadata in `struct ncsi_request` until response/timeout. The generic netlink family is registered at `subsys_initcall` time.

## Dependencies and Integration
The file depends on generic netlink, public `uapi/linux/ncsi.h` attributes/commands, internal topology structures, command TX, response timeout/error paths, and device reset logic. It is the administrative interface for `ncsi-manage.c` state.

## Risks
Topology is walked with RCU-style macros but without a single high-level snapshot lock during serialization, so users can observe concurrent changes. `ndp_from_ifindex()` gets and puts the netdev but returns an internal pointer whose lifetime depends on NCSI unregister synchronization. Mask operations can disable all channels or request multi-package mode without HWA, which is guarded only in package-mask handling. Raw command payloads are bounded to 2048 bytes but still depend on lower command-builder sizing.

## Test Signals
Netlink tests should query single and all packages, force preferred package/channel, clear preferences, set masks and multi flags, send raw commands with success, timeout, unsupported command, and malformed payload cases, and verify that management reset/reconfiguration follows persistent setting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.h -->
# sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.h

## Purpose
This private header declares the netlink response helpers used outside `ncsi-netlink.c`, mainly by response and timeout paths.

## APIs, Types, and Functions
It declares `ncsi_send_netlink_rsp()`, `ncsi_send_netlink_timeout()`, and `ncsi_send_netlink_err()`. These functions send a successful raw-command response, a timeout notification, or an `NLMSG_ERROR` response to the saved generic netlink sender.

## Control Flow
There is no executable flow. `ncsi-rsp.c` calls the response helper for netlink-driven requests after command response processing, and `ncsi-manage.c` calls the timeout helper from `ncsi_request_timeout()`. Error reporting is used by bad response validation and immediate raw command send failures.

## State and Persistence
The functions operate on `struct ncsi_request` metadata (`snd_seq`, `snd_portid`, `nlhdr`, command/rsp skbs) and package/channel lookup results. The header itself holds no state.

## Dependencies and Integration
The header depends on `linux/netdevice.h` and `internal.h` for NCSI request, package, and channel types. It connects `ncsi-netlink.c` to `ncsi-rsp.c` and `ncsi-manage.c`.

## Risks
Prototype drift would break cross-file integration. Callers must pass valid request skb pointers because response helpers derive net namespace and ifindex from command or response skbs.

## Test Signals
Build coverage plus raw netlink command success, timeout, and validation-error tests exercise all three declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-pkt.h -->
# sources/distributed-fs/ceph-client/net/ncsi/ncsi-pkt.h

## Purpose
This header defines the wire-format packet structures and constants for NCSI commands, responses, OEM payloads, statistics, MAC address retrieval, and asynchronous event notifications.

## APIs, Types, and Functions
Common packet headers are `ncsi_pkt_hdr`, `ncsi_cmd_pkt_hdr`, `ncsi_rsp_pkt_hdr`, and `ncsi_aen_pkt_hdr`. Command structs cover default commands plus SP, DC, RC, AE, SL, SVF, EV, SMA, EBF, EGMF, SNFC, and OEM. Response structs cover OEM vendor layouts, GLS, GVI, GC, GP, GCPS, GNS, GNPTS, GPS, GPUUID, GMCMA, and AEN packet forms for LSC, CR, and HNCDSC. Constants define packet revision, command opcodes, response opcodes, response code/reason values, and AEN types.

## Control Flow
There is no executable control flow. `ncsi-cmd.c` writes these layouts into skbs, `ncsi-rsp.c` casts received skbs to these layouts and extracts fields, and `ncsi-aen.c` validates and consumes AEN layouts.

## State and Persistence
The structures describe transient on-wire data. Values decoded from them persist in `ncsi_channel` capabilities, modes, filters, statistics, package UUIDs, pending MAC address, and management state.

## Dependencies and Integration
The header depends on kernel fixed-width endian types and Ethernet address length. It must match DMTF NCSI packet layout, including padding, checksum positions, payload lengths, and packed/aligned statistics fields.

## Risks
Incorrect structure layout, missing packing where required, or wrong payload length constants can corrupt command generation or response parsing. Flexible array OEM and GMCMA payloads require callers to validate lengths before accessing variable data. Endianness conversions are handled by consumers, so fields must be declared with the correct endian type.

## Test Signals
Packet encode/decode tests should verify sizeof/offset expectations, command/response opcode correspondence, checksum placement, statistics layout, OEM response offsets, and AEN payload sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-pkt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-rsp.c -->
# sources/distributed-fs/ceph-client/net/ncsi/ncsi-rsp.c

## Purpose
This file receives NCSI response packets, validates common response metadata and checksums, dispatches to type-specific handlers, updates package/channel state, reports netlink-driven command results, and frees request tracking.

## APIs, Types, and Functions
The public internal entry point is `ncsi_rcv_rsp()`. Helpers include `decode_bcd_u8()`, `ncsi_validate_rsp_pkt()`, handlers for all standard response types (`cis`, `sp`, `dp`, `ec`, `dc`, `rc`, `ecnt`, `dcnt`, `ae`, `sl`, `gls`, `svf`, `ev`, `dv`, `sma`, `ebf`, `dbf`, `egmf`, `dgmf`, `snfc`, `gvi`, `gc`, `gp`, `gcps`, `gns`, `gnpts`, `gps`, `gpuuid`, `pldm`, `gmcma`), OEM helpers for Mellanox/Broadcom/Intel Get MAC, `ncsi_rsp_handler_netlink()`, and the `ncsi_rsp_handlers[]` dispatch table.

## Control Flow
`ncsi_rcv_rsp()` resolves the `ncsi_dev_priv` from the original netdev, diverts AEN packets to `ncsi_aen_handler()`, finds a response handler by packet type, associates the skb with the request ID, validates revision, payload length, response code/reason, and checksum, then invokes the handler. Netlink-driven requests additionally send success or error replies. Finally it calls `ncsi_free_request()`, which may schedule management work when event-driven pending requests reach zero.

## State and Persistence
Handlers mutate the persistent NCSI topology: package/channel creation, channel active/inactive modes, TX enable state, AEN/link/VLAN/MAC/broadcast/multicast/flow-control modes, link status, version info, capability masks, allocated MAC/VLAN filter tables, channel count, statistics, package UUID, pending MAC address, and `gma_flag`. The request's response skb is owned until `ncsi_free_request()`.

## Dependencies and Integration
The file depends on packet definitions, command skb contents for state echoing, command checksum helper, topology allocation helpers, netlink response helpers, Ethernet address validation, and management request completion. It is registered as the packet handler target by `ncsi_register_dev()`.

## Risks
Variable-length handlers (`GP`, `OEM`, `PLDM`, `GMCMA`) rely on the received payload length and must avoid overreading flexible data. `ncsi_rsp_handler_gc()` allocates filter arrays and can leak or overwrite expectations if capabilities are refreshed unexpectedly. Netlink errors for nonzero response codes intentionally still send the raw response after `out_netlink`. Request ID reuse and timeout races are sensitive to `nr->used`, `nr->enabled`, and `nr->rsp` ordering.

## Test Signals
Tests should inject every response type with valid/invalid revision, length, code/reason, and checksum; verify state mutations for capabilities, filters, link, stats, UUID and MAC retrieval; cover timeout races and duplicate responses; and validate netlink raw-command success and error reply behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ncsi/ncsi-rsp.c -->
