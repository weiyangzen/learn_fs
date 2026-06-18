# subset-b-004536 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_tx.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_tx.c

Purpose: implements mlx5 kTLS TX offload setup, teardown, send-queue programming, and out-of-order record resynchronization. It bridges Linux TLS device offload callbacks to mlx5 TIS objects, DEK keys, UMR/SET_PSV TLS parameter WQEs, DUMP WQEs, and TX completion cleanup.

Important APIs, types, and functions: `mlx5e_ktls_get_stop_room()` reserves SQ space for static/progress params, worst-case DUMP WQEs, and a fence NOP. `mlx5e_ktls_add_tx()` copies AES-GCM-128/256 crypto info, creates a DEK from the TLS key pool, stores the private context in `tls_context`, and marks the context params pending. `mlx5e_ktls_del_tx()` destroys the DEK and returns the offload context to a TIS pool. `mlx5e_ktls_handle_tx_skb()` is the TX datapath hook. `mlx5e_ktls_tx_handle_resync_dump_comp()` unmaps DUMP DMA and drops page refs. `mlx5e_ktls_init_tx()`/`mlx5e_ktls_cleanup_tx()` own the DEK pool, TX context pool, and debugfs. Main private state is `struct mlx5e_ktls_offload_context_tx`, carrying expected TCP sequence, TIS number, pending-post bit, copied crypto info, TLS TX context pointer, mlx5 device, stats, and DEK.

Control flow: TX initialization creates a shared TLS DEK pool for kTLS-capable devices and a preallocated TIS context pool for TX-capable devices. Add-TX pops a context, validates cipher type, creates the hardware key, stores start TCP sequence, and defers hardware parameter WQE posting until the first SKB. The first offloaded SKB forces MPWQE completion, posts static and progress params, then stores `tls_tisn` in the accel state for the normal TX WQE builder. If packet sequence differs from `expected_seq`, the code consults kernel TLS record metadata under `tx_ctx->lock`, posts resync params, and emits DUMP WQEs containing already-sent record bytes up to the retransmission point. Unsupported or stale record cases either bypass no-data start markers or drop the SKB.

State and persistence: offload state persists in the kernel TLS driver context and in the driver's TIS pool until TLS teardown. The pool is protected by a mutex and asynchronously grows/shrinks in 16-object batches between low/high watermarks. DUMP WQEs pin record pages until completion; completion uses `resync_dump_frag_page` in WQE info to release DMA and page references. `expected_seq`, `ctx_post_pending`, copied record sequence, stats, and debugfs `pool_size` are volatile runtime state only.

Dependencies and integration points: depends on Linux kTLS record APIs, mlx5 command async context, crypto DEK pool, mlx5e SQ/WQE helpers, DMA mapping, debugfs, and stats. It integrates with normal TX through `mlx5e_accel_tx_tls_state` and `mlx5e_ktls_handle_tx_wqe()` in the header.

Risks: sequence arithmetic and record lifetime are fragile around retransmissions after ACKed record release. DMA/page-ref balancing in DUMP splitting must stay exact across partial failures and queue teardown. Pool cleanup depends on asynchronous TIS destroy callbacks freeing contexts; create errors take a separate free path. Stop-room underestimation can deadlock SQ posting. Only TLS 1.2 AES-GCM 128/256 are handled.

Test signals: exercise TLS TX add/delete, AES-GCM-128 and 256 paths, first-packet param posting, in-order and out-of-order retransmissions, start-marker bypass, stale-record drops, DMA mapping failure, pool empty/refill/shrink paths, debugfs pool size, and stats such as `tls_ooo`, `tls_dump_packets`, `tls_drop_no_sync_data`, and pool alloc/free counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.c

Purpose: shared kTLS TX/RX WQE construction for static TLS crypto parameters and progress parameters. It converts Linux TLS crypto structs into mlx5 hardware context fields.

Important APIs, types, and functions: `mlx5e_ktls_build_static_params()` fills a UMR WQE using `MLX5_OPC_MOD_TLS_TIS_STATIC_PARAMS` for TX or `MLX5_OPC_MOD_TLS_TIR_STATIC_PARAMS` for RX. `mlx5e_ktls_build_progress_params()` fills a SET_PSV WQE using TIS/TIR progress opmods. Internal `fill_static_params()` extracts salt and record sequence from `union mlx5e_crypto_info`, sets TLS 1.2, GCM IV, initial record number, DEK index, and resync TCP sequence. `fill_progress_params()` initializes next-record TCP sequence, tracker state, and auth state.

Control flow: callers allocate/fetch a WQE from an SQ, then pass queue producer counter, SQ number, key id, TIS/TIR number, fence mode, and direction. Static params choose AES-GCM-128 or AES-GCM-256 layouts, warn on unsupported ciphers, and encode inline context bytes. Progress params are shorter and set hardware record tracking to start with auth not yet offloaded.

State and persistence: the file does not own long-lived state. It writes WQE memory supplied by callers. Persistent effects occur only after callers ring the SQ and hardware consumes the WQEs.

Dependencies and integration points: depends on `ktls_utils.h` WQE layouts, Linux TLS crypto structs, mlx5 IFC field macros, and TLS offload direction enum. Used by TX (`ktls_tx.c`) and RX kTLS code to post the same hardware context classes.

Risks: wrong opmod/direction pairing would program a TIS as a TIR or vice versa. Record sequence and salt copying assumes TLS 1.2 AES-GCM struct layouts. Unsupported cipher handling is only a warning and early return from fill helper, so callers must already validate ciphers. Fence selection affects ordering with data and DUMP WQEs.

Test signals: inspect generated WQEs for AES-GCM-128/256, TX and RX directions, fenced and unfenced posts, nonzero resync TCP sequence, and correct DEK/TIS/TIR fields. Negative tests should reject unsupported cipher types before these builders are reached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.h

Purpose: public kTLS datapath interface between mlx5e TX/RX core and the kTLS acceleration implementation, with compile-time no-op fallbacks when `CONFIG_MLX5_EN_TLS` is disabled.

Important APIs, types, and functions: `struct mlx5e_accel_tx_tls_state` carries the selected TIS number into normal TX WQE construction. Declarations cover TX stop-room sizing, TX SKB handling, RX SKB handling, kTLS ICO SQ completions, GET_PSV completions, TX resync DUMP completions, RX resync cancellation, and RX resync-list processing. Inline helpers include `mlx5e_ktls_tx_try_handle_resync_dump_comp()`, `mlx5e_ktls_rx_pending_resync_list()`, and `mlx5e_ktls_handle_tx_wqe()`.

Control flow: TX code first calls `mlx5e_ktls_handle_tx_skb()` to validate/update TLS state and fill `tls_tisn`; later WQE build code calls `mlx5e_ktls_handle_tx_wqe()` to write that TIS into the control segment. Completion code can call the try-handle helper, which detects DUMP completions using `wi->resync_dump_frag_page`. RX polling can detect pending async resync work through a channel state bit and budget.

State and persistence: the header owns no storage beyond the transient TX accel state. It exposes state-bit checks and WQE-info flags owned by queue structures.

Dependencies and integration points: includes net TLS, mlx5e `en.h`, and TX/RX queue declarations. It is included by mlx5e datapath files that must compile regardless of TLS acceleration support.

Risks: fallback stubs must preserve caller expectations when TLS is disabled: no stop room, no RX processing, no DUMP completions. The inline TX WQE helper assumes the state was initialized by the kTLS SKB hook before use.

Test signals: build with and without `CONFIG_MLX5_EN_TLS`, verify no unresolved symbols in disabled builds, and validate that enabled builds set `cseg->tis_tir_num` only for TLS-offloaded packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_utils.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_utils.h

Purpose: shared declarations, crypto-info union, hardware WQE structures, size macros, and fetch macros for mlx5e kTLS TX/RX offload.

Important APIs, types, and functions: declares kTLS add/delete/resync entry points for TX and RX. `union mlx5e_crypto_info` provides one storage object that can be interpreted as generic TLS crypto or AES-GCM-128/256 TLS 1.2 structs. WQE structures are `mlx5e_set_tls_static_params_wqe`, `mlx5e_set_tls_progress_params_wqe`, and `mlx5e_get_tls_progress_params_wqe`. Size macros compute WQEBB consumption for stop-room calculations. Fetch macros retrieve typed WQEs from cyclic work queues, including DUMP WQEs declared in TX code. Builder prototypes are exported from `ktls_txrx.c`.

Control flow: this header is used by TX/RX add paths for crypto storage, by SQ posting paths for WQE sizing and typed access, and by completion/resync paths for shared progress-state constants.

State and persistence: no independent state. The struct definitions describe in-ring WQE state that persists until hardware completion. The crypto union is embedded in private TLS offload contexts.

Dependencies and integration points: depends on Linux TLS headers and mlx5e queue helpers from `en.h`. It connects TLS offload control-plane functions with low-level WQE builders.

Risks: WQE layout drift must match firmware IFC definitions and `MLX5_SEND_WQE_BB` sizing. The DUMP fetch macro references `struct mlx5e_dump_wqe`, which is defined in `ktls_tx.c`; include ordering must only use it where that type is visible. Cipher support is intentionally narrow.

Test signals: compile all TLS-enabled objects, verify WQEBB sizes against expected hardware descriptors, and run TX/RX TLS offload tests across AES-GCM-128 and 256.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec.c

Purpose: implements mlx5e MACsec hardware offload for Linux MACsec netdevices. It maps SecY, TX/RX secure channels, and secure associations to mlx5 MACsec general objects, crypto keys, flow-steering rules, ASO state, RX metadata, and EPN event handling.

Important APIs, types, and functions: exported entry points are `mlx5e_macsec_build_netdev()`, `mlx5e_macsec_init()`, `mlx5e_macsec_cleanup()`, `mlx5e_macsec_handle_tx_skb()`, `mlx5e_macsec_tx_build_eseg()`, and `mlx5e_macsec_offload_handle_rx_skb()`. `macsec_offload_ops` wires the Linux MACsec callbacks for add/update/delete of SecY, TXSA, RXSC, and RXSA. Core state includes `struct mlx5e_macsec`, `mlx5e_macsec_device`, `mlx5e_macsec_sa`, `mlx5e_macsec_rx_sc`, xarray elements mapping RX flow-steering ids to RX SCs, and ASO/UMR objects for hardware state access.

Control flow: initialization verifies device support, allocates ASO PD/MR, creates an ordered workqueue, initializes the RX SC xarray, creates MACsec flow steering, and registers a notifier for MACsec object-change events. Adding a SecY validates strict frame validation, default ICV length, protected frames, and encryption, then stores a per-MACsec-device context. Adding TX/RX SAs creates encryption keys and, when active and operational, creates mlx5 MACsec objects plus steering rules. RX SCs allocate an xarray fs id and metadata destination for marking decrypted packets. Update paths toggle active state by adding/removing rules or rebuilding rules after address/SecY changes. Delete paths remove rules, destroy objects/keys, erase xarray entries, and free contexts with RCU where datapath readers exist.

State and persistence: MACsec state persists under `priv->macsec` until cleanup. A mutex protects control-plane lists, SAs, SCs, ASO operations, and device contexts. RX datapath uses RCU/xarray to map CQE metadata to `metadata_dst`. Hardware persists MACsec general objects, encryption keys, ASO state, and flow rules until explicit cleanup. EPN state persists per SA as `epn_msb` and overlap and is modified after hardware object-change events.

Dependencies and integration points: depends on Linux MACsec core, mlx5 general object commands, mlx5 crypto key APIs, `lib/macsec_fs`, ASO helpers, RCU, xarray, metadata dst, notifier events, and mlx5e TX/RX datapaths. TX sets flow-table metadata based on SCI; RX attaches metadata dst so the MACsec stack can identify the secure channel.

Risks: lifetime ordering across flow rules, xarray erasure, RCU readers, and metadata dst references is critical. `mlx5e_macsec_offload_handle_rx_skb()` assumes `xa_load()` succeeds before dereferencing the element, so corrupted/missing metadata would be hazardous. EPN update depends on async ASO query and object modifiability. PN update is explicitly unsupported. Address/SecY update logic is subtle and can temporarily remove/recreate rules.

Test signals: add/update/delete SecY, TXSA, RXSC, RXSA; validate rejection of unsupported SecY settings; exercise active/inactive SA transitions, XPN/EPN wrap events, MAC address changes, netdevice cleanup, RX metadata mapping, TX metadata insertion, and ethtool counters. Stress tests should include concurrent RX while deleting RX SCs and object-change events during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec.h

Purpose: mlx5e MACsec acceleration interface and disabled-build stubs.

Important APIs, types, and functions: declares initialization, cleanup, netdev setup, TX SKB validation, TX Ethernet segment metadata build, and RX offload handling. `mlx5e_macsec_skb_is_offload()` recognizes SKBs with `METADATA_MACSEC` destinations. `mlx5e_macsec_is_rx_flow()` checks CQE flow-table metadata for the MACsec marker.

Control flow: the main netdevice setup path calls `mlx5e_macsec_build_netdev()` to attach `macsec_ops` and feature bits when supported. TX checks metadata dst before invoking MACsec-specific validation and metadata insertion. RX checks CQE metadata marker before attaching MACsec metadata to the SKB.

State and persistence: the header owns no state. It exposes `struct mlx5e_macsec` as opaque to callers and relies on `priv->macsec` allocated in the implementation.

Dependencies and integration points: depends on Linux MACsec, destination metadata, mlx5 driver headers, and `lib/macsec_fs` metadata marker helpers. It lets generic mlx5e datapath code compile with or without MACsec offload.

Risks: disabled stubs must make callers behave as if no offload exists. Metadata marker interpretation must stay aligned with `lib/macsec_fs`. Callers must not dereference the opaque MACsec pointer when the feature is unavailable.

Test signals: build with `CONFIG_MLX5_MACSEC` on/off, verify MACsec feature flags only on capable devices, and validate TX/RX marker checks against actual CQE/SKB metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec_stats.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec_stats.c

Purpose: exposes MACsec hardware offload counters through the mlx5e ethtool statistics framework.

Important APIs, types, and functions: `mlx5e_macsec_hw_stats_desc` lists RX/TX packet, byte, and drop counters in `struct mlx5_macsec_stats`. The generated stats-group operations report count, fill strings, and fill values. `MLX5E_DEFINE_STATS_GRP(macsec_hw, 0)` registers the group.

Control flow: stats are hidden unless `priv->macsec` exists and the device reports MACsec support. Filling values obtains `priv->mdev->macsec_fs`, refreshes stats through `mlx5_macsec_fs_get_stats_fill()`, then reads each counter descriptor into ethtool data.

State and persistence: no local persistent state. It reads counters stored by MACsec flow steering and hardware counter snapshots.

Dependencies and integration points: depends on ethtool stats helpers, mlx5e stats macros, `priv->macsec`, and `mlx5_macsec_fs` counter accessors.

Risks: stats callbacks assume `mdev->macsec_fs` is valid when `priv->macsec` exists. Cleanup ordering must prevent ethtool reads from racing freed MACsec FS state. Counter descriptor order must match user-visible string order.

Test signals: ethtool `-S` on MACsec-capable and non-capable devices, packet/drop counter increments for encrypted/decrypted/drop flows, and cleanup/reload with repeated stats reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.c

Purpose: implements mlx5e PSP offload control plane, flow steering, counters, key/SPI operations, and registration with the kernel PSP device API.

Important APIs, types, and functions: public functions initialize/cleanup RX and TX PSP tables, register/unregister the PSP device, and initialize/cleanup `priv->psp`. `struct mlx5e_psp_fs` holds TX and RX flow-steering state. TX state is `struct mlx5e_psp_tx`; RX protocol state is `mlx5e_accel_fs_psp_prot` for IPv4 and IPv6 UDP PSP. PSP dev ops include config, RX SPI allocation, TX key add/delete, key rotation, and stats. `mlx5e_accel_psp_fs_get_stats_fill()` queries mlx5 flow counters.

Control flow: init first checks PSP, SWP, checksum, partial L4 checksum, and LSO capabilities. It allocates PSP state, initializes TX egress namespace state and RX counters/protocol mutexes, then stores `priv->psp`. RX table activation creates an error table that copies PSP syndrome into metadata for OK packets and drops/counts auth fail, bad trailer, and other errors. The main RX table matches UDP PSP default port, marks metadata reg B with PSP marker bits, performs crypto decrypt, and forwards to the error table. TX table activation creates an egress IPsec namespace rule matching UDP PSP default port, performing crypto encrypt and counting. Registration creates a `psp_dev` with supported AES-GCM versions based on firmware caps.

State and persistence: PSP state persists in `priv->psp`; flow tables are refcounted under mutexes. Flow counters persist until PSP FS cleanup. TX key count and TX drops are atomic. Per-association driver data stores the mlx5 encryption-key id. Hardware key rotation resets PSP generation to zero and sends `MLX5_CMD_OP_PSP_ROTATE_KEY`.

Dependencies and integration points: depends on kernel PSP APIs, mlx5 flow steering, TTC redirection, egress IPsec namespace, crypto key APIs, flow counters, and firmware PSP commands. Datapath files consume key ids in association driver data and CQE metadata created by these flow tables.

Risks: RX error table `max_fte` appears smaller than the number of rules installed, so table sizing should be checked against firmware behavior. Refcounted table get/put must be balanced by netdev open/close paths. Capability checks silently disable PSP, so tests must distinguish unsupported from failed initialization. Association driver storage is sized as `sizeof(u32)` but cast to a local `struct psp_key`.

Test signals: capability-gated init, register/unregister, RX/TX table get/put balance, IPv4 and IPv6 PSP traffic, auth-fail/bad-trailer drops, SPI generation for 128/256-bit keys, association add/delete key count, key rotation, stats query, and teardown with nonzero key count warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.h

Purpose: PSP offload public definitions, capability gate, lifecycle declarations, and disabled-build stubs.

Important APIs, types, and functions: `struct mlx5e_psp_stats` mirrors PSP hardware/software stats for RX/TX packets, bytes, auth failures, frame errors, and drops. `struct mlx5e_psp` stores the kernel `psp_dev`, caps, flow-steering state, TX key count, and TX drop counter. `mlx5_is_psp_device()` checks generic PSP support plus AES-GCM-128 encrypt/decrypt firmware capabilities. Declarations cover PSP flow-table init/cleanup, register/unregister, and overall init/cleanup.

Control flow: callers use `mlx5_is_psp_device()` before allocating PSP resources. Netdev lifecycle invokes init/cleanup and register/unregister if PSP state exists. RX/TX table helpers are called as queues/flow steering become active.

State and persistence: the header describes state allocated in `psp.c` and attached to `priv->psp`. Atomic counters persist until cleanup.

Dependencies and integration points: depends on kernel PSP types and mlx5e private structures. Disabled stubs keep non-PSP builds compiling and returning no-op success.

Risks: the capability helper requires AES-GCM-128 support but AES-GCM-256 is optional and added later in registration. Callers must not assume `priv->psp` exists merely because the kernel config includes PSP.

Test signals: build with PSP enabled/disabled, probe devices with missing individual caps, verify no-op table functions without PSP, and check capability-driven registration versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.c

Purpose: PSP datapath handling for TX encapsulation/WQE metadata and RX decrypted-packet validation.

Important APIs, types, and functions: `mlx5e_psp_handle_tx_skb()` obtains PSP association state and calls `psp_dev_encapsulate()`. `mlx5e_psp_tx_build_eseg()` programs SW parser offsets, metadata key id, and trailer insertion flags in the Ethernet segment. `mlx5e_psp_handle_tx_wqe()` sets inline trailer length. `mlx5e_psp_offload_handle_rx_skb()` validates CQE metadata syndrome and hands decrypted packets to `psp_dev_rcv()`. Internal helpers are `mlx5e_psp_set_state()` and `mlx5e_psp_set_swp()`.

Control flow: TX first looks up a PSP association under RCU. If absent, the packet continues as normal. If present, it records trailer length, SPI, version, and driver key id, then encapsulates the packet through the kernel PSP stack. For GSO packets it rewrites the inner TCP checksum seed. WQE build later sets SWP offsets/flags, applies a ConnectX-7 PSP LSO workaround by zeroing L3 offsets, writes key id into flow metadata, and asks hardware to insert the trailer. RX checks the PSP metadata marker/syndrome installed by flow steering; only decrypted syndrome is accepted, then `psp_dev_rcv()` strips/validates and `skb->decrypted` is set.

State and persistence: per-packet state is stored in `struct mlx5e_accel_tx_psp_state`. Persistent association/key state lives in the kernel PSP association and `pas->drv_data` created by `psp.c`. TX drop count is incremented in `priv->psp`.

Dependencies and integration points: depends on Linux SKB, IPv4/IPv6, UDP/TCP checksum helpers, kernel PSP APIs, and mlx5e TX WQE builders. It relies on PSP flow tables to interpret `keyid` metadata and RX syndrome bits.

Risks: packet parsing for inner protocols must match SKB encapsulation metadata. GSO checksum repair assumes TCP inner header. `*(u32 *)pas->drv_data` must match PSP association driver storage layout. RX currently uses fixed generation zero and drops all non-decrypted syndromes.

Test signals: TX with no association, TX association for IPv4/IPv6, transport and tunneled payloads, GSO TCP checksum correctness, encapsulation failure drop reason/counter, RX decrypted packets, RX auth/frame errors, and disabled PSP paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.h

Purpose: PSP datapath interface, metadata decoding macros, TX state carrier, checksum helper, and disabled-build fallbacks.

Important APIs, types, and functions: metadata macros decode marker bits, syndrome, and handle from CQE `ft_metadata`. `struct mlx5e_accel_tx_psp_state` carries trailer length, key id, SPI, inner protocol, and PSP version. Inline helpers detect offload state, detect SKB association, compute ID/trailer length, test RX flow metadata, and set checksum flags in TX WQE Ethernet segment.

Control flow: TX classification calls `mlx5e_psp_is_offload()`; SKB processing fills state; WQE build uses `mlx5e_psp_txwqe_build_eseg_csum()` to set outer L3 and inner L3/L4 checksum flags depending on inner protocol. RX uses `mlx5e_psp_is_rx_flow()` before invoking the RX handler.

State and persistence: only transient per-packet TX state is defined here. All persistent PSP state is in `priv->psp` and kernel PSP associations.

Dependencies and integration points: depends on SKB, XFRM/PSP headers, mlx5e TX/RX queues, and IP protocol constants. It provides no-op behavior when PSP is not compiled.

Risks: checksum flag choices are tightly coupled to `psp_rxtx.c` SWP offset parsing. Metadata bit positions must match flow-steering actions in `psp.c`. Disabled fallback omits declarations for some TX functions, so callers must be config-gated.

Test signals: compile PSP enabled/disabled, validate metadata decoding with synthetic values, and inspect checksum flags for transport and tunneled PSP packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp_rxtx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_arfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_arfs.c

Purpose: implements accelerated Receive Flow Steering for mlx5e by translating kernel RPS flow-steering requests into mlx5 flow-table rules targeting direct TIRs for specific RX queues.

Important APIs, types, and functions: public entry points are `mlx5e_arfs_create_tables()`, `mlx5e_arfs_destroy_tables()`, `mlx5e_arfs_enable()`, `mlx5e_arfs_disable()`, and `mlx5e_rx_flow_steer()`. `struct mlx5e_arfs_tables` owns four protocol tables, a spinlock, workqueue, state bit, and filter-id counter. `struct arfs_rule` stores the flow tuple, target RX queue, filter id, flow id, async work item, and hardware rule pointer.

Control flow: table creation allocates IPv4/IPv6 TCP/UDP flow tables with two groups: a large exact-match group and a default group forwarding to RSS TIRs. Enabling redirects TTC traffic types to aRFS tables and sets the enabled bit. `ndo_rx_flow_steer` dissects SKB flow keys, rejects unsupported protocols or encapsulation, finds/allocates a hashed rule under spinlock, updates queue accounting, and queues work. Work creates a flow rule or modifies an existing rule destination to the new direct TIR, then opportunistically expires old flows via `rps_may_expire_flow()`.

State and persistence: rules persist in hash buckets until explicit disable/destroy or RPS expiry. Hardware flow rules persist in mlx5 flow tables. `last_filter_id` wraps modulo `RPS_NO_FILTER`. The enabled bit gates work execution and new steering requests.

Dependencies and integration points: depends on Linux flow dissector/RPS, mlx5 flow steering, TTC table redirection, RX resource direct/RSS TIRs, workqueues, and per-channel RQ stats.

Risks: work is asynchronous, so rule targets can change before hardware creation. Disable must cancel all pending work and delete rules safely. Filter-id wrap can collide after many flows but follows RPS expectations. Table defaults cannot use TTC default dest at creation because TTC is not ready, so RSS TIR lookup is duplicated.

Test signals: ntuple on/off creation, enable/disable, IPv4/IPv6 TCP/UDP steering, unsupported encapsulated SKBs, queue migration modifying existing rule, expiry counters, destroy while work pending, and switchdev transition with `fs->arfs` already NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_arfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_common.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_common.c

Purpose: owns mlx5e global NIC resources shared by all mlx5e netdevices on a core device: protection domain, transport domain, mkey, BlueFlame doorbells, TIS objects, crypto DEK private state, and TIR loopback refresh.

Important APIs, types, and functions: `mlx5e_mkey_set_relaxed_ordering()` encodes relaxed ordering bits from device and PCI capabilities. `mlx5e_create_mkey()` creates a physical-address-mode mkey with local read/write. `mlx5e_create_tis()` wraps core TIS creation with transport domain and LACP affinity. `mlx5e_create_mdev_resources()` allocates the shared resource bundle. `mlx5e_destroy_mdev_resources()` tears it down. `mlx5e_modify_tirs_lb()` and `mlx5e_refresh_tirs()` update self-loopback behavior for all TIRs in the transport domain list.

Control flow: resource creation allocates PD, TD, mkey, doorbell records up to the devlink configured count and max channels, optional per-port/per-TC TISes, initializes the TD TIR list lock, and initializes crypto DEK support. Failure unwinds in reverse order. Destruction cleans crypto, TISes, bfregs, mkey, TD, PD, and clears the resource struct.

State and persistence: resources persist in `mdev->mlx5e_res.hw_objs` for the device lifetime. TIRs are tracked in a list under `td.list_lock`. `tisn_valid`, `num_bfregs`, and `dek_priv` record which optional resources were created.

Dependencies and integration points: depends on devlink params, mlx5 core PD/TD/mkey/TIS/bfreg APIs, LAG helpers, crypto DEK init/cleanup, and TIR builder/modify helpers. kTLS, MACsec, PSP, queues, and TIR/TIS users rely on these shared objects.

Risks: partial doorbell allocation is tolerated, so later code must respect `num_bfregs`. DEK init failure is logged but not fatal, which can disable crypto offloads later. TIS affinity logic depends on LAG port count and capabilities. TIR refresh is skipped when firmware supports TIS/TIR TD ordering.

Test signals: probe/remove resource lifecycle, devlink num-doorbells variation, LAG affinity, TIS creation failure unwind, DEK init failure, TIR loopback modification, and repeated reloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dcbnl.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dcbnl.c

Purpose: implements mlx5e DCB netlink operations for IEEE and CEE DCBX, ETS, PFC, DSCP app mappings, max-rate, and port buffer configuration.

Important APIs, types, and functions: `mlx5e_dcbnl_build_netdev()` attaches `dcbnl_ops`. IEEE ops include get/set ETS, PFC, APP, maxrate, and buffer. CEE ops include setall, PG/PFC config, capability queries, and state. Initialization functions are `mlx5e_dcbnl_initialize()`, `mlx5e_dcbnl_init_app()`, and `mlx5e_dcbnl_delete_app()`. Internal helpers build TC groups and bandwidth arrays, validate ETS, switch DCBX host/auto mode, change trust state, set DSCP-to-priority, initialize ETS defaults, and query buffer cell size.

Control flow: initialization reads trust state and DSCP mappings, normalizes stale DSCP app state, computes inline mode constraints, reads DCBX mode, sets capability flags, computes max-rate limits, and initializes ETS to vendor TSA defaults. Set-ETS validates priority mappings and ETS bandwidth sum, translates IEEE TSA into mlx5 TC groups and bandwidth, and writes port registers. Set-PFC writes PFC enable bits, toggles link, and may recompute manual port buffers. DSCP app set switches trust to DSCP, writes firmware mapping, updates dcb app table and counters; delete restores mapping and trust to PCP when no DSCP apps remain. Trust-state changes may safely switch channel params if TX min inline mode changes.

State and persistence: driver state lives in `priv->dcbx`, `priv->dcbx_dp`, and CEE config arrays. Firmware persists ETS/PFC/rate/trust/DSCP mappings. DCB app entries are registered with the kernel DCB subsystem and mirrored by `dscp_app_cnt`.

Dependencies and integration points: depends on mlx5 port register helpers, port buffer management, netdevice DCBNL ops, devlink/firmware capabilities, channel safe-switch params, and pport stats.

Risks: DCB changes can require channel reset due to inline mode changes. ETS zero-bandwidth handling maps Linux semantics onto mlx5 group semantics and is easy to regress. DSCP app error paths try to restore PCP trust but can leave kernel app entries and firmware mappings temporarily inconsistent. Manual buffer updates depend on buffer ownership and MTU.

Test signals: get/set ETS with strict/vendor/ETS and zero bandwidth, PFC enable and cable length, DSCP app add/delete and trust transitions, host/auto DCBX mode, maxrate unit conversion and limits, buffer get/set with SW ownership, CEE setall, and devices lacking individual capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dcbnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dim.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dim.c

Purpose: enables and disables dynamic interrupt moderation (DIM) for mlx5e RX and TX completion queues.

Important APIs, types, and functions: `mlx5e_rx_dim_work()` and `mlx5e_tx_dim_work()` apply net-DIM-selected moderation profiles to RX RQ and TX SQ CQs. `mlx5e_dim_rx_change()` and `mlx5e_dim_tx_change()` toggle DIM on queues. Internal `mlx5e_dim_enable()` allocates and initializes `struct dim`, sets CQ period mode, and binds queue private data. `mlx5e_complete_dim_work()` calls `mlx5e_modify_cq_moderation()` and resets DIM state to `DIM_START_MEASURE`.

Control flow: enabling allocates DIM on the queue CPU node, initializes work, sets the CQ period mode in hardware, stores the dim pointer on the queue, and sets the queue DIM state bit. Disabling clears the state bit, waits for datapath quiescence with `synchronize_net()`, cancels pending work, frees DIM, and clears the pointer. Work functions obtain the current profile from net-DIM and program CQ moderation.

State and persistence: per-queue `struct dim` persists while DIM is enabled. Queue state bits advertise DIM to datapath. Hardware CQ moderation persists until changed by DIM or queue teardown.

Dependencies and integration points: depends on Linux net-DIM, mlx5 CQ moderation helpers, queue/channel structs, workqueues, and NAPI/datapath synchronization.

Risks: disable ordering must prevent datapath from scheduling work after `dim` is freed. CQ period mode programming failure aborts enable. Work assumes queue private pointer remains valid until work cancellation.

Test signals: enable/disable RX and TX DIM repeatedly, validate CQ moderation changes under traffic, inject CQ period mode failures, and teardown queues while DIM work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dim.c -->
