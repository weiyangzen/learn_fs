# Research: subset-b-004535

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xdp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xdp.h

Purpose: declares mlx5e XDP transmit/receive helpers shared by regular XDP, AF_XDP/XSK, and completion cleanup. It defines the completion FIFO payload contract for frame/page/XSK transmit modes and the inline MPWQE helpers used by the XDP SQ fast path.

Important APIs/types/functions: `enum mlx5e_xdp_xmit_mode`, `union mlx5e_xdp_info`, `struct mlx5e_xdp_wqe_info`, `mlx5e_xdp_tx_enable/disable/is_enabled/is_active`, `mlx5e_xmit_xdp_doorbell`, `mlx5e_xdp_get_inline_state`, `mlx5e_xdp_mpwqe_is_full`, `mlx5e_xdp_mpwqe_add_dseg`, and `mlx5e_xdpi_fifo_push/pop`. External entry points include `mlx5e_xdp_handle`, `mlx5e_poll_xdpsq_cq`, `mlx5e_xdp_xmit`, metadata ops, and indirect-call transmit implementations.

Control flow and state: enable/disable toggles `MLX5E_STATE_XDP_TX_ENABLED` and `MLX5E_STATE_XDP_ACTIVE`, with `synchronize_net()` on disable so remote NAPI/XSK wakeups observe the new state. Doorbells are deferred through `sq->doorbell_cseg`. Inline MPWQE mode uses FIFO outstanding depth hysteresis to move small packets inline only under HCA pressure. Completion state is stored in `sq->db.xdpi_fifo`, driven by producer/consumer counters and mode-specific trailing entries.

Dependencies and integration: depends on mlx5e channel/SQ/RQ structures, XDP core, XSK metadata, mlx5 WQE layout, and indirect-call wrappers. XSK TX and XDP CQ polling must push/pop FIFO entries in the exact documented order.

Risks and test signals: incorrect FIFO accounting causes bad unmap/free or UMEM completion; bad inline size calculations can corrupt WQEs; missing `synchronize_net()` would race with NAPI. Exercise XDP_TX, XDP_REDIRECT, AF_XDP TX with metadata, MPWQE/non-MPWQE modes, MTU boundary checks, and disable while wakeups are in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.c

Purpose: implements AF_XDP pool bind/unbind for mlx5e queues. It maps UMEM DMA, tracks per-channel pool pointers, validates XSK geometry, and opens/closes live XSK RQ/SQ objects when the netdev is opened with XDP active.

Important APIs/types/functions: `mlx5e_xsk_setup_pool` is the `.ndo_bpf` callback. Internals include `mlx5e_xsk_map_pool`, `mlx5e_xsk_get_pools/put_pools`, `mlx5e_xsk_add_pool/remove_pool`, `mlx5e_xsk_is_pool_sane`, `mlx5e_build_xsk_param`, `mlx5e_xsk_enable_locked`, and `mlx5e_xsk_disable_locked`.

Control flow and state: public enable/disable wrappers hold `priv->state_lock`. Enable rejects duplicate pool binding and headroom/chunk sizes above 16 bits, allocates channel params, DMA maps the pool, stores it in `priv->xsk.pools[ix]`, builds XSK channel params, validates closed configurations, or opens `c->xskrq`/`c->xsksq` live. Live enable activates XSK, triggers ICOSQ/NAPI, updates RX resource steering, deactivates the regular RQ, and flushes it. Disable reverses by reactivating regular RQ, waiting for WQEs, updating RX steering, deactivating/closing XSK, removing pool, and unmapping DMA.

Dependencies and integration: uses `net/xdp_sock_drv.h`, mlx5e params/setup helpers, subdevice DMA lookup, RX resource updates, RQ state transitions, and XSK open/close from `setup.c`.

Risks and test signals: DMA map/unmap must balance all error paths; opened/no-XDP and closed validation paths must not leave stale pools; queue IDs must respect `num_channels`. Test bind/unbind closed, opened without XDP, opened with XDP, duplicate bind, invalid chunk/headroom, striding RQ oversized warning, and failure injection in map/open paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.h

Purpose: exposes the small XSK pool lookup and bind API used by mlx5e setup and BPF callbacks.

Important APIs/types/functions: `mlx5e_xsk_get_pool` safely returns a queue pool only when the XSK container, pool array, and queue index are valid. It also declares `mlx5e_build_xsk_param` and `.ndo_bpf` entry `mlx5e_xsk_setup_pool`.

Control flow and state: no ownership changes occur in the header. Lookup reads `xsk->pools[ix]` after guarding null and `ix >= params->num_channels`; allocation/refcounting lives in `pool.c`.

Dependencies and integration: includes `en.h` for `mlx5e_params`/`mlx5e_xsk`. Callers rely on the null return for "no AF_XDP pool on this queue."

Risks and test signals: callers must hold or otherwise synchronize with `state_lock` when binding/unbinding. Test invalid qid, missing `xsk->pools`, and queue reopen paths that consult the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.c

Purpose: implements AF_XDP RX buffer allocation and CQE-to-SKB/XDP handling for both striding MPWQE and legacy cyclic RQ modes.

Important APIs/types/functions: `mlx5e_xsk_alloc_rx_mpwqe`, `mlx5e_xsk_alloc_rx_wqes_batched`, `mlx5e_xsk_alloc_rx_wqes`, `mlx5e_xsk_skb_from_cqe_mpwrq_linear`, and `mlx5e_xsk_skb_from_cqe_linear`. Local helper `xsk_buff_to_mxbuf` relies on mlx5e private fields fitting in `xdp_buff_xsk->cb`; `mlx5e_xsk_construct_skb` copies UMEM data for XDP_PASS.

Control flow and state: MPWQE allocation reserves a full batch of XSK frames, builds an ICOSQ UMR WQE according to aligned/unaligned/triple/oversized mapping mode, sets `mxbuf->rq`, clears release skip bitmap, records WQE info, and arms the doorbell. Cyclic allocation fills WQE DMA addresses from XSK frames either batched or one by one. CQE handlers set packet size, sync DMA for CPU, run the current XDP program, mark release skip when XDP consumed the frame, or copy `data_meta..data_end` into a new SKB for XDP_PASS.

Dependencies and integration: depends on xsk allocator/DMA APIs, mlx5e ICOSQ/UMR, RQ fragment metadata, XDP program execution in `xdp.h`, and RX WQE free paths honoring skip bits.

Risks and test signals: allocation shortfall paths must free partially allocated XSK buffers; UMR offset math differs by mode; metadata copy must preserve `skb_metadata_set`; oversize MPWQE packets are software dropped. Test aligned/unaligned/triple/oversized MPWQE, cyclic batched wraparound, invalid descriptors, XDP_DROP/TX/REDIRECT/PASS, metadata, and SKB allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.h

Purpose: declares the XSK RX allocation and CQE conversion entry points consumed by mlx5e RX handlers.

Important APIs/types/functions: prototypes cover MPWQE allocation, batched and scalar cyclic WQE allocation, and MPWQE/cyclic `sk_buff` construction from CQEs.

Control flow and state: the header does not store state; it defines the boundary where common RX code delegates to AF_XDP-specific buffer ownership logic.

Dependencies and integration: includes `en.h` for RQ, WQE, CQE, and mlx5e MPWQE types. Callers must pass queue-local `rq`, WQE indices, CQE byte counts, and fragment/page references from the active XSK RQ.

Risks and test signals: mismatched prototypes or wrong caller assumptions about ownership can leak UMEM frames. Build with AF_XDP enabled and exercise both striding and cyclic RQ receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/setup.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/setup.c

Purpose: builds, opens, closes, activates, and deactivates the dedicated AF_XDP receive and transmit queues for a channel.

Important APIs/types/functions: `mlx5e_validate_xsk_param`, `mlx5e_open_xsk`, `mlx5e_close_xsk`, `mlx5e_activate_xsk`, and `mlx5e_deactivate_xsk`. Local helpers validate legacy linear mode, initialize XSK RQ fields, and open the XSK RQ.

Control flow and state: validation enforces chunk size bounds and linear SKB feasibility for striding/cyclic RQs. `mlx5e_open_xsk` validates params, opens RX CQ, opens XSK RQ, opens TX CQ, then opens a separate XSK XDPSQ so pool disable can stop old CQEs cleanly. Close clears channel XSK state, synchronizes with NAPI, closes RQ/SQ/CQs, and zeroes the embedded structs. Activate/deactivate manipulate `MLX5E_RQ_STATE_ENABLED` while suspending ICOSQ recovery to avoid recovery races.

Dependencies and integration: uses mlx5e CQ/RQ/XDPSQ open helpers, XDP RXQ registration, health reporter recovery gates, and XSK pool params from `pool.c`.

Risks and test signals: open error unwinding must close CQs/RQ in reverse order; activation must not race ICOSQ recovery; separate SQ cleanup prevents stale pool completions. Test open failure injection at each step, channel reopen with XDP, XSK activate/deactivate under traffic, and close during NAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/setup.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/setup.h

Purpose: declares the XSK queue setup lifecycle used by pool binding and channel open code.

Important APIs/types/functions: `mlx5e_validate_xsk_param`, `mlx5e_open_xsk`, `mlx5e_close_xsk`, `mlx5e_activate_xsk`, and `mlx5e_deactivate_xsk`.

Control flow and state: the lifecycle is validate before create, open RQ/SQ/CQs, activate RQ, deactivate with NAPI synchronization, then close and clear state.

Dependencies and integration: exposes `struct mlx5e_channel_param` and XSK pool-backed queue setup to the rest of mlx5e.

Risks and test signals: callers must follow open/activate/deactivate/close ordering and hold broader channel state locks where required. Compile and run AF_XDP queue open/close coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.c

Purpose: implements AF_XDP TX wakeup and descriptor draining into mlx5e XDP SQ WQEs.

Important APIs/types/functions: `mlx5e_xsk_wakeup`, `mlx5e_xsk_tx`, and local `mlx5e_xsk_tx_post_err`.

Control flow and state: wakeup rejects inactive XDP or invalid qid, marks NAPI missed when scheduled, or posts an async ICOSQ trigger with `MLX5E_SQ_STATE_PENDING_XSK_TX`. TX loops over budget, checks SQ space through indirect-call check functions, peeks an XSK TX descriptor, builds `mlx5e_xmit_data`, syncs DMA for device, transmits through MPWQE/non-MPWQE indirect call, and pushes XSK completion metadata into the XDP info FIFO. Failed packet size/transmit posts a NOP so completions stay ordered. Flush completes MPWQE, rings the doorbell, and releases consumed TX descriptors.

Dependencies and integration: uses XSK descriptor APIs, XDP transmit functions from `xdp.h`, NAPI/ICOSQ trigger paths, and XSK TX metadata completion support.

Risks and test signals: completion FIFO order must match CQ cleanup; NOP error path must release descriptors exactly once; TX can stall if userspace does not send wakeups for consumed-but-uncompleted frames. Test wakeup inactive/active, CQ completion ordering on oversize errors, metadata-enabled TX, MPWQE and regular SQ modes, and full SQ backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.h

Purpose: declares the AF_XDP TX data path entry points.

Important APIs/types/functions: `mlx5e_xsk_wakeup` implements netdev wakeup from AF_XDP userspace; `mlx5e_xsk_tx` drains descriptors on the XSK XDPSQ.

Control flow and state: no state lives here; the declarations expose queue wake and NAPI TX work to the broader mlx5e channel code.

Dependencies and integration: includes `en.h` for netdev/channel/SQ types. Used when NAPI handles pending `MLX5E_SQ_STATE_PENDING_XSK_TX`.

Risks and test signals: build coverage with XSK enabled and functional AF_XDP TX wakeups are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/en_accel.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/en_accel.h

Purpose: central inline composition layer for mlx5e transmit/receive accelerations, including kTLS, IPsec, PSP, MACsec, and Geneve software parser offload fields.

Important APIs/types/functions: `mlx5_geneve_tx_allowed`, `mlx5e_tx_tunnel_accel`, `struct mlx5e_accel_tx_state`, `mlx5e_accel_tx_begin`, `mlx5e_accel_tx_ids_len`, `mlx5e_accel_tx_eseg`, `mlx5e_accel_tx_finish`, `mlx5e_accel_init_rx/cleanup_rx`, and `mlx5e_accel_init_tx/cleanup_tx`.

Control flow and state: TX begin may emit preparatory WQEs and can drop/fail the SKB when an acceleration-specific handler cannot prepare state. ID length is selected from active PSP/IPsec state. ESEG build adds protocol-specific metadata/checksum/trailer fields before the WQE is posted. TX finish writes final WQE fields such as TLS TIS or IPsec inline trailer. Init/cleanup orders PSP flow steering and kTLS setup/teardown.

Dependencies and integration: compile-time gated by feature configs; depends on TLS/IPsec/PSP/MACsec helpers, `xfrm_offload`, TLS offload markers, and mlx5e TX WQE layout. Geneve handling depends on SWP support and packet header parsing.

Risks and test signals: ordering matters when several offloads are present; incorrect ESEG metadata breaks hardware parsing. Test each feature enabled/disabled, mixed tunnel checksum cases, IPsec with GSO/checksum, TLS TX, PSP, MACsec, and Geneve encapsulation with VLAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/en_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.c

Purpose: builds accelerated TCP flow-steering tables used primarily by kTLS RX to direct selected TCP sockets to dedicated TIRs before default TTC handling.

Important APIs/types/functions: `mlx5e_accel_fs_tcp_create`, `mlx5e_accel_fs_tcp_destroy`, `mlx5e_accel_fs_add_sk`, and `mlx5e_accel_fs_del_sk`. Internals include IPv4/IPv6 match builders, default rule creation, grouped flow table creation, TTC enable/disable, and table destroy helpers.

Control flow and state: create allocates `struct mlx5e_accel_fs_tcp`, builds IPv4 and IPv6 TCP tables with a large exact-match group and one default group, inserts default rules forwarding to TTC defaults, then modifies TTC TCP traffic types to point at acceleration tables. Per-socket add builds a flow spec from socket local/remote addresses and ports, selects IPv4 or IPv6 table including v4-mapped IPv6 handling, sets optional flow tag, and forwards to the socket TIR. Destroy disables TTC redirection, deletes default rules/tables, and clears the fs pointer.

Dependencies and integration: depends on mlx5 flow steering core, TTC tables, `mlx5e_flow_steering` accel TCP storage, Linux socket address state, and kTLS RX rule work.

Risks and test signals: address/port direction is easy to invert because RX matching uses remote source to local destination; TTC must be restored on destroy; IPv6 support is conditional. Test create without outer IP version capability, add IPv4/IPv6/v4-mapped socket rules, default fallthrough, destroy during active TLS contexts, and rule add failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.h

Purpose: declares the accelerated TCP flow-steering API with no-op stubs when TLS support is disabled.

Important APIs/types/functions: `mlx5e_accel_fs_tcp_create/destroy`, `mlx5e_accel_fs_add_sk`, and `mlx5e_accel_fs_del_sk`.

Control flow and state: with `CONFIG_MLX5_EN_TLS`, callers create tables, add per-socket TIR rules, delete rules, and destroy tables. Without it, create/destroy are harmless and add returns `-EOPNOTSUPP`.

Dependencies and integration: includes `en/fs.h`; used by kTLS RX init and RX context rule work.

Risks and test signals: feature gating must keep non-TLS builds link-clean. Build both TLS-enabled and disabled configurations and exercise kTLS RX feature toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.c

Purpose: integrates mlx5e with Linux XFRM device offload for IPsec ESP. It validates XFRM states/policies, translates them into driver attributes, owns SA/policy lifecycle, handles ESN/lifetime/neighbour work, and publishes netdev offload features.

Important APIs/types/functions: exported `mlx5e_ipsec_init`, `mlx5e_ipsec_cleanup`, `mlx5e_ipsec_build_netdev`, and `mlx5e_ipsec_build_accel_xfrm_attrs`. XFRM callbacks include state add/delete/free/advance ESN/update stats and policy add/delete/free. Helpers manage ESN state, packet lifetime math, MAC resolution for tunnel packet offload, validation, delayed software limit checks, and neighbour events.

Control flow and state: init allocates `struct mlx5e_ipsec`, initializes SADB xarray/workqueue/completion, optional ASO and netevent notifier, flow steering, and attaches it to `priv`. State add allocates `mlx5e_ipsec_sa_entry`, validates AES-GCM ESP constraints, blocks eswitch conflicts, checks tunnel permission, initializes ESN and attrs, creates optional work/dwork, creates HW SA context, installs flow rules, inserts into SADB, and stores `xso.offload_handle`. Delete erases from SADB; free cancels work, deletes flow rules, frees HW context, unblocks eswitch, and frees memory. Policy add builds masked selector attrs and installs flow rules similarly.

Dependencies and integration: relies on XFRM core, Linux crypto AEAD/geniv, neighbour/FIB lookup, eswitch block APIs, mlx5 IPsec hardware context creation, IPsec flow steering, and ASO event support.

Risks and test signals: validation must reject unsupported algorithms, replay windows, limits, encap, and policies; resource unwinding has many partial states; tunnel MAC resolution can temporarily mark SAs drop until neighbour update. Test crypto and packet offload, IPv4/IPv6 transport/tunnel, ESN rollover, lifetime soft/hard expiration, neighbour updates, policy priorities, acquire states, stats update, and cleanup with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.h

Purpose: defines the IPsec offload data model and public mlx5e IPsec API.

Important APIs/types/functions: key structs include `aes_gcm_keymat`, `mlx5_accel_esp_xfrm_attrs`, `mlx5_accel_pol_xfrm_attrs`, `mlx5e_ipsec`, `mlx5e_ipsec_sa_entry`, `mlx5e_ipsec_pol_entry`, `mlx5e_ipsec_rule`, `mlx5e_ipsec_ft`, `mlx5e_ipsec_aso`, HW/SW stats, ESN/lifetime state, and flow table create attrs. It declares lifecycle, flow steering, SA context, ASO, stats, attrs, and devcom event APIs plus disabled stubs.

Control flow and state: persistent state is rooted at `priv->ipsec`, with SADB xarray mapping hardware object IDs to SAs, optional object-ID mapping for uplink reps, refcounted flow-table groups, ASO DMA context protected by spinlock, and workqueue/completion for async events.

Dependencies and integration: includes mlx5 device, XFRM, ID/xarray-related state, ASO, and devcom. It is consumed by IPsec core, flow steering, rxtx, offload, stats, and netdev build code.

Risks and test signals: bitfield attrs and metadata handle widths must stay aligned with hardware and `ipsec_rxtx.h`; disabled stubs must preserve non-IPsec builds. Build with and without `CONFIG_MLX5_EN_IPSEC`, and test object ID limits, stats layout, and uplink rep paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_fs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_fs.c

Purpose: constructs and manages the mlx5 flow-steering graph for IPsec crypto and packet offload on RX/TX, including policies, SAs, status checks, packet reformat, counters, RoCE bypass, switchdev/uplink representative handling, and devcom multi-port events.

Important APIs/types/functions: exported APIs are `mlx5e_accel_ipsec_fs_init/cleanup`, `mlx5e_accel_ipsec_fs_add_rule/del_rule`, `mlx5e_accel_ipsec_fs_add_pol/del_pol`, `mlx5e_accel_ipsec_fs_modify`, `mlx5e_ipsec_fs_tunnel_allowed`, stats read, and MPV event helpers. Key local flows include `rx_create/destroy/get/put`, `tx_create/destroy/get/put`, address/SPI/proto match builders, `setup_modify_header`, packet transport/tunnel reformat builders, `rx_add_rule`, `tx_add_rule`, `rx_add_policy`, and `tx_add_policy`.

Control flow and state: init allocates TX, RX IPv4, RX IPv6, optional ESW TX/RX contexts, counters, mutexes, namespaces, and optional RoCE steering. RX creation builds SA decrypt, status, SA selector, policy, miss, and RoCE tables, then connects TTC/default destinations. TX creation builds status counter, SA encrypt, policy/chains, miss handling, and RoCE TX tables. Table contexts are refcounted under `ft.mutex`; add-rule obtains the right RX/TX context, installs rule/counter/reformat/modify-header resources, and blocks TC for packet offload. Delete removes rules and puts the table ref. Modify installs a shadow rule before deleting the old one to reduce traffic interruption.

Dependencies and integration: depends on mlx5 flow table/chains APIs, TTC, eswitch, FDB switchdev helpers, packet reformat hardware capabilities, IPsec attrs from `ipsec.c`, ASO status metadata, RoCE IPsec FS library, and hardware counters.

Risks and test signals: many error paths must free counters, rules, modify headers, packet reformats, chain tables, and eswitch blocks in reverse order; IPv6 mask setup is subtle; packet offload blocks TC and encap modes; status rules must classify auth/trailer/replay drops correctly. Test add/delete/modify RX/TX SAs and policies for crypto/packet offload, block/allow policies, priorities with chains, transport/tunnel, UDP encap, ESW uplink rep, RoCE events, stats counters, and failure injection at every flow-resource allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_offload.c

Purpose: owns IPsec hardware capability discovery, encryption key/general-object creation, object modification, ASO query/update plumbing, and hardware event handling for ESN and lifetime events.

Important APIs/types/functions: `mlx5_ipsec_device_caps`, `mlx5_ipsec_create_sa_ctx`, `mlx5_ipsec_free_sa_ctx`, `mlx5_accel_esp_modify_xfrm`, `mlx5e_ipsec_aso_init/cleanup`, and `mlx5e_ipsec_aso_query`. Internals include packet ASO setup, create/destroy/modify IPsec object commands, ASO soft/hard lifetime updates, ESN event update, notifier callback, and event work handler.

Control flow and state: capability probing checks global IPsec support, DEK, general object types, flow-table crypto capabilities, AES-GCM support, packet/crypto/tunnel/ESP-in-UDP/priority/RoCE/ESN features. SA context creation first creates a crypto key, then a general IPsec object; packet offload embeds ASO context, PD, return register, replay/lifetime settings, and increment/replay modes. ASO init maps a DMA buffer, creates a global ASO SQ, registers object-change notifier, and serializes ASO WQ access with a spinlock. Events query ASO state under XFRM lock, handle lifetime expiration rounds, and modify object attrs on ESN changes.

Dependencies and integration: uses mlx5 command interface, crypto key pool, ASO library, notifier, device caps, flow steering object IDs, XFRM locks, and attrs from `ipsec.c`.

Risks and test signals: capability bits gate user-visible features; key/object creation must unwind cleanly; ASO polling timeout or event ordering can miss ESN/lifetime transitions; object modify requires firmware support bits. Test devices with partial caps, 128/256-bit keys, packet lifetime soft/hard limits, ESN inbound/outbound rollover, ASO query failure, notifier cleanup, and SA create failure after key creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.c

Purpose: handles per-packet IPsec TX/RX data path transformations around mlx5e WQE construction and CQE receive completion.

Important APIs/types/functions: `mlx5e_ipsec_set_iv_esn`, `mlx5e_ipsec_set_iv`, `mlx5e_ipsec_handle_tx_wqe`, `mlx5e_ipsec_tx_build_eseg`, `mlx5e_ipsec_handle_tx_skb`, `mlx5e_ipsec_offload_handle_rx_skb`, and `mlx5_esw_ipsec_rx_make_metadata`. Local helpers remove ESP trailer, set SWP offsets, and calculate TX inline trailer state.

Control flow and state: TX validates single-SA secpath, offload handle, and IP/IPv6 protocol; non-GSO packets have software trailer removed before hardware insertion; IV bytes are written from XFRM sequence, with ESN handling for GSO mid-scope wrap; state records trailer length and protocol; ESEG gets IPsec metadata, trailer insertion flags, SWP parser offsets, and checksum associations. RX reads metadata handle, allocates secpath, looks up SA in SADB under RCU, holds the XFRM state, appends it to secpath, and marks `xfrm_offload` as crypto done/success.

Dependencies and integration: depends on XFRM secpath/offload state, Linux ESP helpers, mlx5 ESEG fields, IPsec SADB from `ipsec.h`, eswitch IPsec object ID mapping, and stats counters.

Risks and test signals: bad trailer trimming corrupts SKBs; secpath allocation or SADB miss must not leave invalid XFRM references; SWP offsets vary by tunnel/transport/encap. Test TX drop counters for bundles/no-state/not-IP/trailer errors, GSO ESN wrap, checksum offload paths, RX SADB miss, secpath allocation failure, and switchdev metadata lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.h

Purpose: declares IPsec packet data path helpers and metadata interpretation macros for mlx5e TX/RX.

Important APIs/types/functions: metadata macros extract marker, syndrome, and handle from CQE FT metadata; `struct mlx5e_accel_tx_ipsec_state` stores active TX XFRM offload, state, trailer length, and padding length. Declares TX/RX handlers, IV setters, ESW metadata lookup, ESEG build, feature check, checksum ESEG helper, and disabled stubs.

Control flow and state: inline feature check disables checksum/GSO for software IPsec or unsupported L4 protocols. `mlx5e_ipsec_txwqe_build_eseg_csum` only acts when ESEG IPsec metadata is present, then configures outer/inner checksum flags from XFRM offload protocol fields.

Dependencies and integration: includes XFRM, SKB, mlx5e TX/RX structures, and is included by `en_accel.h` and RX completion code.

Risks and test signals: metadata bit layout must match flow steering; feature fallback must prevent software IPsec checksum/GSO misuse. Build with/without IPsec and test feature negotiation, checksum flags for transport/tunnel, and metadata handle decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_stats.c

Purpose: exposes IPsec hardware and software counters to the mlx5e ethtool stats framework.

Important APIs/types/functions: static counter descriptor arrays for HW/SW IPsec stats, `MLX5E_READ_CTR_ATOMIC64`, and generated stats group ops for num stats, strings, and values. Defines `MLX5E_DEFINE_STATS_GRP(ipsec_hw, 0)` and `ipsec_sw`.

Control flow and state: HW fill path calls `mlx5e_accel_ipsec_fs_read_stats` to refresh `priv->ipsec->hw_stats` from flow counters, then emits descriptor offsets. SW fill path reads atomic64 counters directly from `priv->ipsec->sw_stats`. Both report zero stats if IPsec is not initialized.

Dependencies and integration: depends on ethtool helpers, mlx5e stats group macros, `ipsec.h` stats structs, and flow-steering stats read.

Risks and test signals: descriptor order must match userspace expectations; atomic offset reads assume descriptor type alignment. Test ethtool stats with IPsec absent/present, traffic/drop counter increments, and uplink representative aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.c

Purpose: top-level kTLS device integration for mlx5e: key creation, TLS device ops, netdev feature publication, RX feature toggling, RX/TX init hooks, and debugfs root management.

Important APIs/types/functions: `mlx5_ktls_create_key`, `mlx5_ktls_destroy_key`, `mlx5e_ktls_build_netdev`, `mlx5e_ktls_set_feature_rx`, `mlx5e_ktls_init_rx/cleanup_rx`, `mlx5e_ktls_init/cleanup`, and TLS dev ops add/delete/resync dispatchers.

Control flow and state: add checks cipher/version/device support and dispatches by TX/RX direction. RX resync is only supported for RX. kTLS RX capability requires non-kdump, TLS RX cap, no subdevice, and enough ICOSQ WQE size for static/progress/get-PSV WQEs. Build netdev sets HW TLS TX/RX features and `tlsdev_ops`. RX feature enable creates TCP accel flow tables and reopens channels the first time RX is enabled; init creates RX workqueue and tables if feature already active. Top-level init allocates `priv->tls`, records mdev, and creates debugfs.

Dependencies and integration: uses Linux TLS offload ops, mlx5 crypto DEK pool helpers, TCP acceleration FS, channel reopen, debugfs, and TX/RX kTLS implementation files.

Risks and test signals: feature toggling under `state_lock` must coordinate with channel state; RX workqueue/table cleanup must match feature state; unsupported cipher handling must be strict. Test TLS 1.2 AES-GCM-128/256, unsupported ciphers, RX feature toggle on open netdev, init cleanup with feature enabled, and resync direction rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.h

Purpose: defines the kTLS capability checks, shared TLS state, stats structs, and public kTLS lifecycle/stat APIs.

Important APIs/types/functions: `mlx5e_is_ktls_device`, `mlx5e_ktls_type_check`, `mlx5e_is_ktls_tx`, `mlx5e_is_ktls_rx`, `struct mlx5e_tls_sw_stats`, `struct mlx5e_tls_debugfs`, `struct mlx5e_tls`, key helpers, TX/RX init/cleanup, RX feature setter, resync response-list helpers, and stats getters.

Control flow and state: `struct mlx5e_tls` is rooted at `priv->tls` and holds mdev, atomic SW stats, RX workqueue, TX pool, DEK pool, and debugfs dentries. Disabled builds provide no-op stubs and `-EOPNOTSUPP` for RX feature enable.

Dependencies and integration: includes Linux TLS headers, mlx5 crypto/lib helpers, and mlx5e core structures. Shared by kTLS TX, RX, stats, and netdev feature setup.

Risks and test signals: capability checks must reject kdump/subdevice/unsupported TLS versions; stats layout must remain stable. Build with/without `CONFIG_MLX5_EN_TLS`, test feature bits on devices with only TX/RX caps, and verify stats count/string/value consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_rx.c

Purpose: implements kTLS RX offload contexts, hardware TIR/key setup, TCP acceleration rules, RX CQE handling, and asynchronous resync with GET_PSV/progress WQEs.

Important APIs/types/functions: `mlx5e_ktls_add_rx`, `mlx5e_ktls_del_rx`, `mlx5e_ktls_handle_rx_skb`, `mlx5e_ktls_handle_ctx_completion`, `mlx5e_ktls_handle_get_psv_completion`, `mlx5e_ktls_rx_resync`, `mlx5e_ktls_rx_resync_async_request_cancel`, `mlx5e_ktls_rx_handle_resync_list`, and response-list create/destroy. Key local structs are `mlx5e_ktls_offload_context_rx`, `mlx5e_ktls_rx_resync_ctx`, `mlx5e_ktls_rx_resync_buf`, and `accel_rule`.

Control flow and state: add allocates private RX context, copies crypto info, creates DEK, selects socket RX queue, stores context in TLS driver state, creates TLS TIR, initializes completion/work/refcount/resync state, points TLS async resync at driver context, posts static and progress WQEs, and increments stats. Context completion queues TCP flow rule installation to RX workqueue. RX CQE handling marks decrypted packets or starts resync on RESYNC CQEs. Resync requests lookup socket, queue GET_PSV work, compare hardware tracker/auth state, end or cancel TLS async request, and later post static params with software record sequence via NAPI list handling. Delete marks deleting, clears TLS ctx, synchronizes NAPI, cancels work, deletes rule/TIR/key, and refcounts delayed free if GET_PSV is in flight.

Dependencies and integration: depends on TLS core async resync API, mlx5 ICOSQ WQE builders from `ktls_utils.h`, TCP accel FS, RX resource TLS TIRs, socket lookup, NAPI async ICOSQ, DMA mapping, and per-channel resync response lists.

Risks and test signals: refcounting protects in-flight GET_PSV and delete races; list handling must requeue on ICOSQ full; socket lookup and TCP state checks must avoid stale references; progress state validation gates resync success. Test RX add/delete while WQEs complete, flow rule add work cancellation, decrypted/error/resync CQEs, IPv4/IPv6 socket lookup, ICOSQ full retry, GET_PSV DMA failure, and async resync cancel/end paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_stats.c

Purpose: publishes mlx5e kTLS software counters through the driver stats interface.

Important APIs/types/functions: counter descriptor array for `tx_tls_ctx`, `tx_tls_del`, `tx_tls_pool_alloc`, `tx_tls_pool_free`, `rx_tls_ctx`, `rx_tls_del`; `mlx5e_ktls_get_count`, `mlx5e_ktls_get_strings`, and `mlx5e_ktls_get_stats`.

Control flow and state: functions no-op when `priv->tls` is absent. Otherwise, count returns descriptor count, strings emit ethtool names, and stats read atomic64 fields from `priv->tls->sw_stats`.

Dependencies and integration: depends on ethtool helpers, mlx5e stat emit helpers, and `struct mlx5e_tls_sw_stats` from `ktls.h`.

Risks and test signals: descriptor offsets must match stats struct; stats must disappear cleanly when TLS unsupported. Test ethtool stats before/after kTLS init, TX/RX context add/delete increments, and TLS-disabled build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_stats.c -->
