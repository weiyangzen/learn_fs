# subset-b-004586 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm_mbox.c

## Purpose
This file implements the Netronome NFP control-channel-message transport over the device mailbox. Callers provide a CCM packet in an skb, and this layer serializes one or more queued packets into mailbox TLVs, runs the mailbox reconfiguration command, copies replies back into the original skb for synchronous callers, and wakes waiters. It is the shared transport used by higher-level features such as kTLS crypto control messages.

## Important APIs, types, and functions
- `struct nfp_ccm_mbox_cmsg_cb` overlays `skb->cb` and tracks per-message state, error, maximum request/reply size, expected reply length, and whether the message is posted/asynchronous.
- `nfp_ccm_mbox_msg_alloc()`, `nfp_ccm_mbox_fits()`, `nfp_ccm_mbox_communicate()`, `__nfp_ccm_mbox_communicate()`, and `nfp_ccm_mbox_post()` are the external send/allocation surface.
- `nfp_ccm_mbox_copy_in()` writes request TLVs plus optional reservation TLVs into the BAR mailbox. `nfp_ccm_mbox_copy_out()` parses reply TLVs, validates tag/type/length, and updates skb contents or posted-message state.
- `nfp_ccm_mbox_run_queue_unlock()` owns a batch, copies up to `NFP_CCM_MBOX_BATCH_LIMIT` messages while respecting mailbox space, executes `nfp_net_mbox_reconfig()`, and completes the batch.
- `nfp_ccm_mbox_alloc()`, `nfp_ccm_mbox_clean()`, and `nfp_ccm_mbox_free()` initialize, drain, and destroy the queue/workqueue backing the transport.

## Control flow
The synchronous path prepares the skb, assigns CCM header version/type/tag under `nn->mbox_cmsg.queue.lock`, and queues it. If the skb is not first, the caller sleeps until either its message is done or it becomes the next runner. The first/next runner builds a batch, marks subsequent skbs busy, drops the queue lock, locks the control BAR, writes TLVs, triggers `NFP_NET_CFG_MBOX_CMD_TLV_CMSG`, reads replies, completes/dequeues all batched skbs, marks the next queued skb runnable, unlocks the BAR, and wakes all waiters. The asynchronous `nfp_ccm_mbox_post()` path marks the skb posted, tries to start the mailbox transaction immediately with `nn_ctrl_bar_trylock()`, and uses workqueue jobs to wait for posted completion or to run a posted next runner.

## State and persistence
State is volatile driver state: the skb queue, per-skb control buffer state, monotonic mailbox tag, wait queue, and workqueue. No persistent on-disk state exists. Ordering is enforced with `smp_wmb()` before marking messages done and `smp_rmb()` in waiters before reading copied reply data or errors. Posted messages are consumed internally; synchronous messages are returned to callers unless an error forces skb free.

## Dependencies and integration points
The file depends on NFP mailbox BAR helpers (`nn_readl`, `nn_writel`, `nn_ctrl_bar_lock`, `nfp_net_mbox_reconfig*`), CCM header helpers from `ccm.h`, skb queue primitives, workqueues, and wait queues. Feature drivers rely on this to send firmware CCM operations, especially `crypto/tls.c`.

## Risks
Risks center on concurrency and firmware ABI validation. A missed state transition can strand waiters; incorrect memory barriers can expose stale skb data; malformed firmware TLVs are guarded but cause all remaining batched requests to complete with errors. Queue length is capped for non-critical messages, but critical callers can bypass the cap. Posted messages have no caller-visible completion beyond warnings.

## Test signals
Useful signals include forced mailbox-full and reply-too-large paths, unsupported CCM type validation, timeout behavior for queued and busy skbs, batching boundaries at 64 messages and mailbox-size limits, posted-message workqueue paths, and kTLS add/delete/update operations that exercise synchronous, critical, and posted CCM sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/crypto.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/crypto.h

## Purpose
This header declares the NFP network-driver crypto offload interface shared by TLS and IPsec code. It provides minimal cross-file types for per-connection TLS firmware handles and per-packet IPsec metadata, plus configuration-dependent stubs so the rest of the driver can call into crypto support without scattering preprocessor checks.

## Important APIs, types, and functions
- `struct nfp_net_tls_offload_ctx` stores the two-word firmware handle returned by the TLS firmware and, for TX only, the next TCP sequence. The zero-length `rx_end` marker documents the split between RX-sized driver state and TX-only fields.
- `nfp_net_tls_init()` enables/registers TLS device offload when `CONFIG_TLS_DEVICE` is built; the stub returns success when disabled.
- `nfp_net_tls_rx_resync_req()` handles firmware RX resync requests when TLS device offload exists; the stub returns `-EOPNOTSUPP`.
- `struct nfp_ipsec_offload` carries high/low packet sequence and offload handle for TX descriptors.
- `nfp_net_ipsec_init()`, `nfp_net_ipsec_clean()`, `nfp_net_ipsec_tx_prep()`, and `nfp_net_ipsec_rx()` are exported only when `CONFIG_NFP_NET_IPSEC` is enabled.

## Control flow
The file has no runtime control flow beyond inline stubs. It shapes compile-time routing: callers can invoke TLS/IPsec init and packet helpers from common paths, while the compiler either links real implementations from `tls.c`/`ipsec.c` or substitutes no-op/unsupported behavior.

## State and persistence
The TLS context embeds firmware handle state in the kernel TLS driver context associated with a socket. The IPsec offload struct is transient per-packet/descriptor metadata. No persistent storage is managed here.

## Dependencies and integration points
This header is included by crypto implementation files and by NFP netdev data paths that need to initialize crypto offloads or attach crypto metadata to packets. It forward-declares `struct nfp_net`, `struct net_device`, and `struct nfp_net_tls_resync_req` to avoid dragging firmware-layout headers into every consumer.

## Risks
The layout of `struct nfp_net_tls_offload_ctx` is ABI-sensitive against `TLS_DRIVER_STATE_SIZE_TX/RX` checks in `tls.c`. Any new RX fields before `rx_end` could exceed kernel TLS RX driver state. Stub behavior must stay compatible with callers that treat init as optional but data-path helpers as feature-gated.

## Test signals
Build coverage should include TLS enabled/disabled and IPsec enabled/disabled configurations. Runtime signals are TLS offload setup reaching `nfp_net_tls_init()`, RX resync requests returning supported/unsupported as expected, and IPsec init attaching `xfrmdev_ops` only when hardware capability and build config allow it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/fw.h

## Purpose
This header defines the firmware ABI structures and constants used for NFP TLS crypto CCM messages. It describes request/reply packet layouts for reset, add, delete, update, and RX resync operations and the opcode values for TLS 1.2 AES-GCM-128 encrypt/decrypt.

## Important APIs, types, and functions
- `NFP_NET_CRYPTO_OP_TLS_1_2_AES_GCM_128_ENC/DEC` identify firmware crypto operation bits.
- `struct nfp_net_tls_resync_req` is sent from firmware to host and carries a TLS handle, TCP sequence, and packet L3/L4 offsets.
- `struct nfp_crypto_reply_simple` and `struct nfp_crypto_reply_add` are CCM replies with firmware error and, for add, a two-word handle.
- `struct nfp_crypto_req_add_front`, `_back`, `_v4`, and `_v6` define the variable add request. The `struct_group_tagged` and `static_assert` protect the variable-address layout.
- `struct nfp_crypto_req_del`, `struct nfp_crypto_req_update`, and `struct nfp_crypto_req_reset` define delete/update/reset requests.

## Control flow
There is no executable control flow. The structures are filled by `tls.c`, passed through the CCM mailbox transport, and interpreted by firmware. The front/back split lets the same add code support IPv4 and IPv6 by changing the address span between fixed header and crypto material.

## State and persistence
State represented here is firmware session state: add requests create firmware handles, update requests advance record/TCP sequence, delete requests invalidate handles, and reset clears endpoint state. The header itself stores nothing.

## Dependencies and integration points
The header depends on `../ccm.h` for `struct nfp_ccm_hdr`. It is tightly coupled to `crypto/tls.c` and to firmware TLV/CCM ABI expectations, including byte order, packed VLAN/IP version field masks, key material sizes, and operation bits exported in `nn->tlv_caps.crypto_ops`.

## Risks
The request structures carry key material and are ABI-sensitive. Field order, padding, and endian conversions must remain exactly compatible with firmware. The `struct_group_tagged` comment is important: adding fields outside the grouped front header would silently corrupt variable-length address handling. Key zeroization in `tls.c` depends on these layout boundaries.

## Test signals
Compile-time layout assertions are the first signal. Runtime validation includes successful TLS reset/add/update/delete CCM transactions for IPv4 and IPv6 sockets, correct rejection when firmware returns nonzero error, and RX resync requests being parsed from `struct nfp_net_tls_resync_req` offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/ipsec.c

## Purpose
This file implements NFP IPsec/XFRM crypto offload support. It translates Linux `xfrm_state` objects into firmware SA configuration messages, registers `xfrmdev_ops`, tracks offloaded SAs in an xarray, and attaches offload metadata to TX/RX packets.

## Important APIs, types, and functions
- Firmware command/reply enums describe add/invalidate SA requests and response codes.
- `struct nfp_ipsec_cfg_add_sa` and `struct nfp_ipsec_cfg_mssg` are the 64-word mailbox ABI used for SA configuration.
- `nfp_net_ipsec_cfg()` writes the full message to the simple mailbox, runs `NFP_NET_CFG_MBOX_CMD_IPSEC`, reads the reply back, and maps firmware response codes to Linux errors.
- `nfp_net_xfrm_add_state()` validates XFRM mode/protocol/offload type/algorithms, fills keys, salt, SPI, address family, direction, PMTU, and SA index, sends the add command, and stores `xso.offload_handle = saidx + 1`.
- `nfp_net_xfrm_del_state()` invalidates an SA and erases its xarray entry.
- `nfp_net_ipsec_tx_prep()` exports sequence and handle metadata for TX; `nfp_net_ipsec_rx()` maps firmware SA index metadata back to an `xfrm_state` in the skb secpath.

## Control flow
Initialization checks `NFP_NET_CFG_CTRL_IPSEC`, initializes `nn->xa_ipsec`, and assigns `netdev->xfrmdev_ops`. XFRM add allocates a bounded SA index, then schedules a mailbox async-message work item with `nfp_net_sched_mbox_amsg_work()`. On command failure it erases the index. Delete sends invalidate and erases regardless after warning on firmware failure. RX subtracts one from firmware SA index, validates range, creates/extends `sec_path`, looks up and holds the xfrm state, and marks `xfrm_offload` as crypto done/success.

## State and persistence
The xarray `nn->xa_ipsec` is the live SA table mapping hardware SA indices to kernel `xfrm_state` pointers. The kernel-visible offload handle is one-based because zero is invalid to XFRM. There is no persistent state across driver reload. Cleanup warns if the xarray is not empty, then destroys it.

## Dependencies and integration points
The file integrates with Linux XFRM (`xfrmdev_ops`, `secpath_set`, `xfrm_offload`), the NFP mailbox scheduler, PCI device IDs for feature differences, and NFP RX metadata (`meta->ipsec_saidx`). It uses unaligned big-endian key loads and Netlink extack messages for user-visible offload rejection reasons.

## Risks
Algorithm support is hardware-specific and easy to regress: NFP3800 disallows MD5/3DES but allows CHACHA20-POLY1305, while other devices reject CHACHA20. Key length and ICV checks must match XFRM conventions where AEAD key length includes salt. Bitfield layout in the firmware message is ABI-sensitive. RX depends on firmware providing a valid one-based SA index; stale or missing xarray entries lead to packet failure.

## Test signals
Exercise XFRM add/delete for tunnel and transport ESP/AH, AES-CBC, AES-GCM/GMAC, null auth/encryption, CHACHA20-POLY1305 on NFP3800, unsupported ESN, bad key lengths, and RX packets with valid/invalid SA indices. Cleanup should not warn after all states are deleted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/tls.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/tls.c

## Purpose
This file implements NFP kernel TLS device offload for TLS 1.2 AES-GCM-128. It negotiates firmware crypto operation bits, sends CCM mailbox commands to add/delete/update TLS contexts, manages per-direction enable counts, registers `tlsdev_ops`, and handles firmware-originated RX resync requests.

## Important APIs, types, and functions
- `nfp_net_tls_init()` validates firmware op bits and CCM message support, resets firmware TLS state, disables crypto ops initially, enables netdev TLS feature flags, and assigns `netdev->tlsdev_ops`.
- `nfp_net_tls_add()` validates cipher/socket family, enables the per-direction crypto opcode on first connection, builds IPv4/IPv6 add requests, copies key/IV/salt/record sequence, sends `NFP_CCM_TYPE_CRYPTO_ADD`, zeroes key material, stores firmware handle in TLS driver context, and sets RX resync mode when needed.
- `nfp_net_tls_del()` decrements connection count and sends delete by firmware handle.
- `nfp_net_tls_resync()` sends synchronous TX updates or posted/asynchronous RX resync/update messages.
- `nfp_net_tls_rx_resync_req()` maps firmware packet offsets to a socket lookup and asks the kernel TLS core to resync RX.

## Control flow
Connection add increments direction count under the control BAR lock; 0-to-1 transitions toggle the firmware opcode bit and run `NFP_NET_CFG_UPDATE_CRYPTO`. The add request uses synthetic connection IDs for TX because TX firmware matching does not need original 5-tuple, while RX uses reversed socket tuple fields for lookup. After mailbox add, nonzero firmware errors unwind the count and optionally log table-full once. RX resync requests validate header bounds, identify IPv4/IPv6, look up an established socket, verify it is RX device-offloaded and not shut down, optionally compare firmware handle, then calls `tls_offload_rx_resync_request()`.

## State and persistence
Persistent live state is in memory only: `ktls_tx_conn_cnt`, `ktls_rx_conn_cnt`, `dp.ktls_tx`, `ktls_conn_id_gen`, no-space/resync counters, and per-socket `nfp_net_tls_offload_ctx` firmware handles. Key material is transient in the request skb and is explicitly zeroed after the CCM transaction while holding an extra skb reference.

## Dependencies and integration points
This file depends on the CCM mailbox transport in `ccm_mbox.c`, firmware ABI structures in `fw.h`, Linux kTLS (`tlsdev_ops`, driver contexts, resync APIs), IPv4/IPv6 established socket lookup, and NFP TLV capability fields (`crypto_ops`, `crypto_enable_off`, `mbox_cmsg_types`, `tls_resync_ss`).

## Risks
The main risks are key handling, request layout, and async RX resync lifetime. The code assumes CCM does not reallocate the skb so key material can be zeroed in place. RX resync posting uses `GFP_ATOMIC` and does not wait for firmware completion. Connection counts are protected by the BAR lock, and failed reconfig must accurately undo count/opcode changes. Socket lookup from firmware-provided offsets must reject malformed packets.

## Test signals
Signals include TLS add/delete for IPv4, IPv4-mapped IPv6, native IPv6, unsupported ciphers, table-full firmware replies, TX resync sequence updates, RX resync request success/ignore counters, first/last connection crypto enable transitions, and firmware capability combinations that should leave TLS disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/tls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/devlink_param.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/devlink_param.c

## Purpose
This file exposes selected NFP persistent hardware-info settings as generic devlink parameters. It maps devlink firmware-load-policy and reset-on-driver-probe values to NSP hwinfo keys and registers the parameters only when the NSP supports hwinfo lookup and set.

## Important APIs, types, and functions
- `struct nfp_devlink_param_u8_arg` describes one u8 parameter mapping: hwinfo key/default, invalid devlink value, bidirectional value maps, and valid ranges.
- `nfp_devlink_u8_args[]` defines mappings for `DEVLINK_PARAM_GENERIC_ID_FW_LOAD_POLICY` and `DEVLINK_PARAM_GENERIC_ID_RESET_DEV_ON_DRV_PROBE`.
- `nfp_devlink_param_u8_get()` opens NSP, looks up hwinfo with a default, parses and validates the hardware value, and returns the mapped devlink value or an unknown value.
- `nfp_devlink_param_u8_set()` maps a validated devlink value back to `key=value` and writes it through NSP hwinfo set.
- `nfp_devlink_param_u8_validate()` rejects out-of-range and unknown/invalid devlink values.
- `nfp_devlink_params_register()` and `_unregister()` gate registration on NSP capability.

## Control flow
Registration probes NSP support. If `nfp_nsp_open()` fails, registration returns the error; if lookup/set capabilities are absent, registration returns 0 and no params are registered. Get/set operations independently open and close NSP, so they do not persist NSP handles. Invalid stored hwinfo values are converted to devlink "unknown" when the param supports that, or to the configured negative error otherwise.

## State and persistence
The persistent state lives in device hwinfo, not in this driver. Devlink get reads current hwinfo; devlink set writes a permanent hwinfo setting because the parameters are registered with `DEVLINK_PARAM_CMODE_PERMANENT`.

## Dependencies and integration points
The file integrates Linux devlink params with NFP NSP APIs (`nfp_nsp_hwinfo_lookup_optional`, `nfp_nsp_hwinfo_set`) and constants from `nfp_nsp.h`. It uses `priv_to_devlink(pf)` and `devlink_priv()` to bridge PF and devlink objects.

## Risks
The mapping arrays assume devlink IDs index directly into `nfp_devlink_u8_args`; unsupported IDs are rejected by array bounds. Range constants must stay consistent with both devlink generic enums and NSP hwinfo values. Unregistration repeats the support probe; if NSP access changes between register and unregister, params could be skipped or errors hidden, although that mirrors the current gating model.

## Test signals
Test devlink get/set for both params, invalid user values, invalid stored hwinfo values, missing hwinfo falling back to defaults, NSP open failures, and devices whose NSP lacks lookup/set support. Verify values persist across driver reload according to device hwinfo behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/devlink_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/action.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/action.c

## Purpose
This file compiles Linux TC flower action lists into the NFP Flower firmware action bytecode stored in `nfp_fl_payload->action_data`. It supports output/mirror/redirect, VLAN/MPLS push/pop/mangle, tunnel encap/decap, packet edits, checksum validation, LAG pre-actions, pre-tunnel actions, ptype handling, and QoS meter actions.

## Important APIs, types, and functions
- `nfp_flower_compile_action()` is the exported compiler entry point. It validates delayed hardware stats, iterates TC actions, accumulates NFP actions, and records final action length/shortcut.
- Action encoders include `nfp_fl_push_mpls()`, `nfp_fl_pop_mpls()`, `nfp_fl_set_mpls()`, `nfp_fl_push_vlan()`, `nfp_fl_pop_vlan()`, `nfp_fl_output()`, `nfp_fl_set_tun()`, and `nfp_fl_meter()`.
- Pedit support is split across `nfp_fl_set_eth()`, `nfp_fl_set_ip4()`, `nfp_fl_set_ip6()`, `nfp_fl_set_tport()`, accumulated in `struct nfp_flower_pedit_acts`, and emitted by `nfp_fl_commit_mangle()`.
- `nfp_flower_loop_action()` is the per-action dispatcher and enforces feature/size/order constraints.
- `nfp_fl_push_geneve_options()` emits Geneve options in reverse order for hardware.

## Control flow
The compiler zeros the action buffer, initializes tunnel/output/checksum state, and walks actions. Consecutive mangle actions are accumulated so multiple pedit operations on the same hardware action can be merged before emission. Output actions validate the egress netdev, representor parent, tunnel type, LAG support, internal-port/pre-tunnel constraints, and last/mirror flags. Tunnel encap inserts a pre-tunnel action at the beginning of the list, optional Geneve option pushes, then a set-tunnel action. Checksum actions are accepted only if prior mangle actions caused hardware-supported checksum updates and consume the pending checksum flags.

## State and persistence
State is per compilation: `action_data`, `meta.shortcut`, `meta.act_len`, tunnel type, output counts, pedit accumulator, checksum flags, and ptype-host marker. It persists only as part of an offloaded flow payload in memory and firmware after the caller transmits the flow.

## Dependencies and integration points
This compiler uses TC action APIs, flow dissector data, NFP Flower firmware ABI structs from `cmsg.h`, LAG helpers from `lag_conf.c`, internal-port helpers from `main.c`, tunnel feature flags from `main.h`, and meter lookup helpers. The resulting action buffer is sent by flow offload paths outside this file.

## Risks
Most risks are ABI and validation risks. `NFP_FL_MAX_A_SIZ` must be enforced for every inserted action, especially pre-actions that memmove existing data. Pedit endian/mask handling must match TC semantics and firmware. Tunnel flag constants deliberately guard against kernel ABI drift with `BUILD_BUG_ON`. The helper `nfp_fl_check_mangle_end()` compares `current_act_idx == num_entries`, which looks suspicious because the last valid index is `num_entries - 1`; tests should confirm final mangle groups are committed.

## Test signals
Exercise each action type, maximum action length failures, multiple output/tunnel rejection, LAG as last action, pre-tunnel internal-port ptype requirements, Geneve option limits, IPv4/IPv6/tport/eth pedit plus csum ordering, unsupported stats mode, and mixed action lists where shortcut must fall back to null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/action.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.c

## Purpose
This file allocates, sends, queues, and dispatches NFP Flower control messages between host driver and firmware. It covers representor port modification/reification, MAC representor advertisement, firmware control-message RX dispatch, MTU acknowledgement handling, merge hints, tunnel neighbor events, QoS stats, and LAG retransmission handling.

## Important APIs, types, and functions
- `nfp_flower_cmsg_alloc()` creates a control skb with `struct nfp_flower_cmsg_hdr`.
- `nfp_flower_cmsg_mac_repr_start()` and `nfp_flower_cmsg_mac_repr_add()` build the physical MAC representor advertisement.
- `nfp_flower_cmsg_portmod()` notifies firmware of link/MTU state; `nfp_flower_cmsg_portreify()` asks firmware to create/destroy a port representation.
- `nfp_flower_cmsg_rx()` is the immediate RX entry from `app_flower.ctrl_msg_rx`.
- `nfp_flower_cmsg_process_rx()` drains high-priority then low-priority queues and dispatches each deferred message.
- Internal handlers process MTU ACKs, portmod link updates, portreify ACKs, and merge hints.

## Control flow
Outgoing messages allocate an skb, fill the Flower header and type-specific payload, then call `nfp_ctrl_tx()`. Incoming messages first validate version. Flow stats, MTU ACKs, tunnel-neighbor ACKs, and port reify ACKs are handled immediately because they are urgent or avoid RTNL/workqueue deadlocks. Other messages are queued into high priority (`PORT_MOD`) or low priority queues with a hard length cap and processed by `cmsg_work`. The work item splices both queues locally before dispatch, so producers can continue queuing while processing runs.

## State and persistence
The file manages in-memory skb queues, wait/ack state in `priv->mtu_conf`, and counters such as `reify_replies`. Messages may be consumed, freed, or stored by the LAG layer for retransmission. No persistent state is written.

## Dependencies and integration points
It integrates with `nfp_app_ctrl_msg_alloc()`, `nfp_ctrl_tx()`, representor lookup, RTNL/RCU netdev handling, tunnel route/keepalive helpers, Flower stats and QoS handlers, flow merge, LAG, and the structures/constants in `cmsg.h`.

## Risks
Queue overload drops control messages after `NFP_FLOWER_WORKQ_MAX_SKBS`, which protects memory but may delay firmware synchronization until higher-level recovery. Portmod RX takes RTNL and changes carrier/MTU, so immediate MTU ACK handling is intentionally separate. Merge hints are advisory but must hold `nfp_fl_lock` while looking up subflows. LAG may retain skbs, so ownership is conditional via `skb_stored`.

## Test signals
Test valid/invalid cmsg versions, high-priority portmod ordering, MTU ACK wait wakeup, reify wait wakeup, queue overflow warnings, merge-hint validation for wrong flow counts/lengths, tunnel request dispatch, and LAG data/XON/SYNC messages retaining or consuming skbs correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.h

## Purpose
This header defines the NFP Flower firmware control-message ABI and flow key/action wire structures. It is shared by action compilation, match compilation, representor management, tunnel handling, LAG, stats, and control-message dispatch.

## Important APIs, types, and functions
- Layer bit definitions (`NFP_FLOWER_LAYER_*`, `NFP_FLOWER_LAYER2_*`) describe which key blocks are present in a flow payload.
- Action opcodes and structs (`nfp_fl_output`, VLAN/MPLS/set-field/tunnel/pre-LAG/pre-tunnel/meter/Geneve structs) are the firmware action-list format.
- Key structs (`nfp_flower_meta_tci`, `ext_meta`, `in_port`, `mac_mpls`, VLAN, L4, IPv4/IPv6, UDP/GRE tunnel, Geneve options) define packed match/mask layout.
- `struct nfp_flower_cmsg_hdr` and `enum nfp_flower_cmsg_type_port` define control-message envelope and message types.
- Port ID helpers encode internal, physical, and PCIe representor ports. Inline netdev helpers recognize offloadable tunnel/internal netdevs.
- Function prototypes expose cmsg allocation/RX and representor messages.

## Control flow
The header has no standalone execution, but its inline helpers are used throughout the Flower app. Port encoding helpers compose bitfields consumed by firmware and decoded in `main.c`; tunnel type helpers are used by action validation; data pointer helpers strip the fixed cmsg header for typed payload access.

## State and persistence
The header defines in-memory and firmware-wire state layouts. Offloaded flow keys/actions persist in firmware after flow add messages; cmsg payloads are transient skbs. The port-id bit layout persists as the contract between host and firmware.

## Dependencies and integration points
It depends on Linux bitfield, skb, Geneve/GRE/VXLAN netdev helpers, NFP app/CPP types, and Ethernet/IP structs. It is central to `action.c`, `cmsg.c`, `conntrack.c`, `lag_conf.c`, `main.c`, tunnel code, and match compiler code not in this subset.

## Risks
This is ABI-critical. Changing struct sizes, alignment, action opcodes, layer bits, or port-id bitfields can break firmware. Max constants such as `NFP_FL_MAX_A_SIZ`, Geneve option limits, and workqueue queue length define enforcement points in C files. Inline `nfp_fl_is_netdev_to_offload()` uses string comparison for openvswitch kind plus tunnel helpers; new netdev kinds need explicit support.

## Test signals
Compile-time users should validate struct sizes through flow offload tests. Runtime signals include successful offload for each key/action layer, representor port ID round trips, tunnel netdev recognition, cmsg type dispatch coverage, and firmware acceptance/rejection of flow add payloads built from these layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.c

## Purpose
This file implements conntrack-aware TC Flower offload merging for the NFP Flower app. It recognizes pre-CT and post-CT TC rules, registers nft flow-table callbacks per zone, stores copied flow rules, merges compatible pre/post/nft rules into a single hardware flow, manages recursive multi-zone NAT/CT chains, and reports merged stats back to the original software flows.

## Important APIs, types, and functions
- `is_pre_ct_flow()` and `is_post_ct_flow()` classify TC flower rules around conntrack.
- `nfp_fl_ct_handle_pre_ct()` and `nfp_fl_ct_handle_post_ct()` add TC CT entries to zone tables and attempt TC merges.
- `nfp_fl_ct_handle_nft_flow()` handles netfilter flow-table replace/destroy/stats callbacks.
- `nfp_ct_merge_check()`, `nfp_ct_merge_act_check()`, `nfp_ct_check_meta()`, and helpers validate that overlapping masks/actions/metadata are compatible.
- `nfp_ct_do_tc_merge()` combines pre and post TC entries; `nfp_ct_do_nft_merge()` adds an nft entry and either creates a next pre-CT rule for recirculation or calls `nfp_fl_ct_add_offload()`.
- `nfp_fl_ct_add_offload()` builds the merged key/mask/action payload, adds tunnel offload references, installs metadata, inserts the flow table entry, and sends `FLOW_ADD`.
- `nfp_fl_ct_del_flow()` and cleanup helpers unwind map entries, merge entries, generated pre-CT entries, hardware offloads, copied rules, and tunnel allocations.
- `nfp_fl_ct_stats()` aggregates hardware stats from merged flows into pre/post/nft flow stats.

## Control flow
Pre-CT rules must be chain 0, contain CT/NAT action without commit, and have a goto. The first pre-CT in a zone registers an nft callback. Post-CT rules either match established CT state or represent NAT post rules with ct clear on a nonzero chain. Adding either side triggers merge attempts with the opposite side in the zone and, for wildcard post-CT zones, across all concrete zones. TC merge checks chain/goto compatibility and overlapping match fields, considering pre-CT mangle effects. NFT merge then checks action conflicts, metadata labels/mark, multi-zone compatibility, creates a three-cookie merge entry, and offloads when no further goto chain is needed.

## State and persistence
State is fully in-memory: zone rhashtable plus wildcard zone pointer, per-zone pre/post/nft lists, TC and NFT merge rhashtables, global CT cookie map, copied `flow_rule` objects, child lists linking entries to merges, cached stats, tunnel allocations, generated next-zone pre-CT entries, and hardware `nfp_fl_payload` pointers. No state persists across reload; firmware state is deleted when merge entries are cleaned.

## Dependencies and integration points
The file depends on Linux TC action/dissector APIs, netfilter flow table callbacks, rhashtable/list primitives, Flower match/action compiler helpers, metadata allocation, tunnel offload reference helpers, NFP flow xmit/delete paths, representor port accounting, and `conntrack.h` data structures.

## Risks
This is high-risk logic: it copies short-lived nft flow rules, translates nft mangle endian/order, and recursively creates pre-CT entries up to `NFP_MAX_RECIRC_CT_ZONES`. Merge correctness depends on comparing only overlapping cared bits and on accounting for NAT mangle changes. Cleanup must remove hardware flows before freeing copied rules and must avoid deadlocks when unregistering nft callbacks. Stats aggregation resets per-context counters and can double count if merge-child traversal is wrong.

## Test signals
Test pre/post classification, zone-specific and wildcard-zone merges, NAT IPv4/IPv6/tport mangles, VLAN/MPLS rejection paths, tunnel encap copied action lifetime, multi-zone recirculation limit, nft duplicate replace suppression, destroy ordering for pre/post/nft flows, hardware add/delete error unwinds, and stats requests for all three original flow types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.h

## Purpose
This header declares the data model and public API for NFP Flower conntrack offload merging. It defines zone, flow-entry, TC-merge, nft-merge, and cookie-map structures used by `conntrack.c`, along with comparison macros and function prototypes used by the broader Flower classifier path.

## Important APIs, types, and functions
- `COMPARE_UNMASKED_FIELDS()` compares two flow match structures on bits cared about by both masks.
- `struct nfp_fl_ct_zone_entry` owns one CT zone's pre/post/nft flow lists and merge tables.
- `enum ct_entry_type` distinguishes pre-CT, nft, and post-CT entries.
- `struct nfp_fl_ct_flow_entry` stores a copied flow rule, cookie, netdev, chain/goto indices, stats cache, child merge links, tunnel action offset, flags, and previous recursive merge entries.
- `struct nfp_fl_ct_tc_merge` represents a compatible pre/post TC pair.
- `struct nfp_fl_nft_tc_merge` represents a TC pair plus nft flow and points at any generated hardware flow or next pre-CT entry.
- Prototypes expose CT classification, add/delete/stats handling, cleanup, nft callback handling, and recursive pre-CT creation.

## Control flow
There is no direct runtime flow in the header. It establishes the contracts used by the Flower setup path: classify a flow, route it to pre/post/nft handling, store an entry, merge compatible children, and later delete or collect stats through the cookie map.

## State and persistence
All structs describe volatile kernel state. Zone entries contain rhashtables/lists that must be initialized and destroyed by `conntrack.c`. `NFP_MAX_RECIRC_CT_ZONES` and `NFP_MAX_ENTRY_RULES` bound recursive merge state and merged-rule arrays.

## Dependencies and integration points
The header includes Linux netfilter flow-table declarations and `main.h` for Flower private types. Its extern rhashtable parameters are defined in this file's implementation or related Flower code. It is consumed by Flower classifier code to decide whether normal flow offload should be replaced by CT merge handling.

## Risks
The macro compares raw bytes of typed match structs and relies on `.key`/`.mask` pointers and structure sizes being valid. The list topology is complex: one entry may be on a zone list and also parent multiple merge lists. Incorrect initialization or cleanup order can corrupt lists. Recursive arrays are fixed-size and must be bounded by implementation checks.

## Test signals
Compile coverage should catch structure/prototype drift. Runtime signals are correct classification into CT handlers, stable add/delete under list/rhashtable debug options, recursive CT zone limit handling, and stats/delete callbacks finding the expected `nfp_fl_ct_map_entry` by cookie.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/lag_conf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/lag_conf.c

## Purpose
This file synchronizes Linux bonding/LAG state to NFP Flower firmware and provides LAG action metadata to the action compiler and tunnel neighbor code. It tracks offloadable bond groups, assigns firmware group IDs/instances, batches configuration control messages, handles firmware retransmission/sync requests, and reacts to netdev LAG events.

## Important APIs, types, and functions
- `struct nfp_flower_cmsg_lag_config` is the firmware control payload containing flags, packet number, batch version, group ID/instance, and active member port IDs.
- `struct nfp_fl_lag_group` tracks one bond master, group ID/instance, dirty/offloaded/remove/destroy flags, and slave count.
- `nfp_flower_lag_populate_pre_action()`, `nfp_flower_lag_get_info_from_netdev()`, and `nfp_flower_lag_get_output_id()` expose group metadata to action/tunnel code.
- `nfp_fl_lag_do_work()` builds batched config/delete messages from dirty groups.
- `nfp_flower_lag_unprocessed_msg()` handles firmware DATA/XON/SYNC retransmission protocol.
- `nfp_flower_lag_netdev_event()` dispatches `NETDEV_CHANGEUPPER`, `NETDEV_CHANGELOWERSTATE`, and `NETDEV_UNREGISTER`.
- `nfp_flower_lag_reset()`, `_init()`, and `_cleanup()` manage LAG subsystem lifecycle.

## Control flow
Change-upper events verify the upper is a LAG master, all slaves are NFP representors from the same app, and firmware-supported bond mode/hash is used. They create or update a group, mark it dirty, and schedule delayed work. Lower-state events update per-representor link/tx flags and mark the group dirty. The work item walks groups under lock, sends delete messages for removals, computes active members for dirty valid groups, sends one message per group, then sends a batch-end sync message if any group was configured. Firmware can ask the host to store unprocessed DATA messages, flush them with XON, or perform a full SYNC reset/resend.

## State and persistence
State is volatile in `struct nfp_fl_lag`: delayed work, group list, mutex, IDA allocator, retransmission skb queue, packet number, batch version, global instance, and reset flag. Group IDs 1-31 are allocated with IDA; group 0 is reserved for sync. Batch version skips zero and increments by two because firmware ignores the LSB.

## Dependencies and integration points
The file depends on Flower cmsg allocation/transmit, representor port IDs, Linux bonding/LAG notifier data, delayed work, IDA, skb queues, and action structs from `cmsg.h`. `action.c` uses pre-LAG data for LAG output actions, while `main.c` calls LAG init/reset/event/cleanup based on firmware feature negotiation.

## Risks
LAG correctness depends on netdev notifier ordering and deferred work. If slave count changes while work runs, the group is skipped until later notifications. Retransmission storage is capped at 100 skbs and drops excess, relying on firmware to request a full resync. Group removal/destroy must not free IDs while firmware still references stale groups. Unsupported bond modes must fall back cleanly.

## Test signals
Test active-backup and supported hash modes, unsupported tx/hash rejection, adding/removing representor slaves, mixed-device bonds, lower-state link/tx changes, group ID exhaustion, delete and unregister paths, firmware DATA/XON/SYNC messages, reset on app start, and LAG action compilation requiring an existing group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/lag_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.c

## Purpose
This file is the NFP Flower app lifecycle and representor-management implementation. It validates Flower firmware requirements, allocates app-private state, negotiates feature bits, creates physical/PF/VF representors, maps firmware port IDs to netdevs and back, handles internal offload ports, starts/stops indirect TC and tunnel configuration, propagates MTU/link/reify messages, and registers the `app_flower` operations table.

## Important APIs, types, and functions
- `app_flower` is the exported `struct nfp_app_type` binding init/clean/vNIC/repr/start/stop/netdev/TC callbacks.
- `nfp_flower_init()` validates required PF resources and firmware symbols, initializes metadata, control-message queues, MTU/reify wait state, feature flags, LAG/flow-merge/internal-port support, QoS, and private lists.
- `nfp_flower_vnic_init()` creates physical, PF, and optional VF representors; `_clean()` removes them.
- `nfp_flower_spawn_phy_reprs()` and `nfp_flower_spawn_vnic_reprs()` allocate representor netdevs/ports, initialize NFP port IDs, publish repr arrays, reify with firmware, and advertise MAC representors.
- `nfp_flower_get_port_id_from_netdev()` and `nfp_flower_dev_get()` translate between netdevs and firmware port IDs, including internal ports and LAG tunnel-neighbor output.
- `nfp_flower_repr_change_mtu()` sends physical-port MTU changes and waits for firmware ACK.
- `nfp_flower_start()`/`stop()` manage LAG reset, indirect TC registration, and tunnel config.

## Control flow
Init fails early if eth table, MAC stats BAR, VF config BAR, firmware version, or host-context sizing is invalid. After private allocation and metadata init, it reads extra firmware features, writes host feature masks, optionally enables LAG and flow merge, and initializes optional QoS. vNIC init stores `priv->nn`, then creates physical reprs, PF repr, and VF reprs with unwind on each failure. Representor creation sends reify messages and waits up to `NFP_FL_REPLY_TIMEOUT`. Start resets LAG if enabled, registers indirect flow callbacks, then starts tunnel configuration. Stop reverses tunnel and indirect callback setup.

## State and persistence
State is in `struct nfp_flower_priv`: app pointer, vNIC pointer, metadata/stat sizing, cmsg queues/work, reify wait/counter, MTU config wait/ack, feature masks, LAG state, internal-port IDR, non-representor private list, QoS, pre-tunnel count, and stats metadata managed by helper modules. No host state persists across reload; firmware feature symbols and hw state are re-read each init.

## Dependencies and integration points
This file ties together NFP core/PF resources, runtime symbols, representor infrastructure, devlink switchdev mode, Flower cmsgs, metadata, tunnel configuration, LAG, QoS, internal ports, indirect TC offload, SR-IOV, and netdev notifier dispatch.

## Risks
Failure unwinds must match partially created representors and private state. Reify/MTU waits can timeout if firmware drops replies. Internal-port IDs are allocated under spinlock but looked up under RCU; unregister events must remove IDs. Feature negotiation writes runtime symbols and assumes firmware acknowledges host bits promptly. `nfp_flower_dev_get()` must decode port IDs consistently with `cmsg.h` or RX/control paths will target wrong netdevs.

## Test signals
Test firmware-resource/version failures, feature-symbol absence, representor creation/reify success and timeout, SR-IOV enable/disable, physical MTU ACK success/failure, internal OVS/tunnel port ID allocation and unregister cleanup, start/stop unwind when tunnel config fails, LAG and flow-merge feature gating, and devlink eswitch mode reporting switchdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.c -->
