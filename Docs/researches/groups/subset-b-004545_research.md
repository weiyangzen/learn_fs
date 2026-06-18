# subset-b-004545 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.c

Purpose: Implements mlx5 LAG multipath offload driven by IPv4 FIB notifications. It activates `MLX5_LAG_MODE_MULTIPATH` when suitable two-port routes appear, tracks the selected `fib_info`, and adjusts port affinity as nexthops are added or removed.

Important APIs and flow: `mlx5_lag_mp_init()` creates a single-thread workqueue and registers a FIB notifier; `mlx5_lag_fib_event()` filters AF_INET route/nexthop events and queues `mlx5_lag_fib_update()`; route handling chooses one or two LAG netdev nexthops, activates LAG on first multipath route, and calls `mlx5_lag_set_port_affinity()` for normal, P1-only, or P2-only forwarding. `mlx5_lag_is_multipath()`, `mlx5_lag_mp_reset()`, and `mlx5_lag_mp_cleanup()` expose mode state and lifecycle.

State and dependencies: `ldev->lag_mp.fib` stores a borrowed/staleness-prone route identity, priority, destination, and prefix length; FIB work takes explicit `fib_info_hold()` references until processed under RTNL. It depends on eswitch multipath prerequisites, LAG mode helpers, netdev-to-LAG index mapping, notifier chains for port-affinity events, and `mlx5_modify_lag()`.

Risks and test signals: Race handling relies on workqueue flush during notifier unregister and RTNL during updates. Watch route delete/missed-event paths, stale `mfi` reset on reinit, duplicate nexthops on one device, priority/prefix comparisons, and only-two-port support. Useful tests are IPv4 ECMP add/replace/delete, nexthop add/delete, single-nexthop fallback affinity, cleanup while events are queued, and unsupported eswitch/port-count configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.h

Purpose: Declares the multipath LAG control state and public lifecycle helpers used by the mlx5 LAG core.

Important APIs and types: `enum mlx5_lag_port_affinity` encodes normal, port 1, and port 2 affinity. `struct lag_mp` embeds a FIB notifier, route tracking tuple (`mfi`, priority, destination, prefix length), and the workqueue used by `mp.c`. Exports are `mlx5_lag_mp_init()`, `mlx5_lag_mp_cleanup()`, `mlx5_lag_mp_reset()`, and `mlx5_lag_is_multipath()`.

State and dependencies: The header includes `lag.h` and `mlx5_core.h`, and it is feature-gated by `CONFIG_MLX5_ESWITCH`. Without eswitch support, all functions become no-op or false inline stubs, so callers can remain unconditional.

Risks and test signals: The `mfi` pointer is intentionally stored as `const void *` for identity tracking, so implementation code must own lifetime with FIB references before dereference. Build coverage should include both eswitch-enabled and eswitch-disabled configurations, plus callers that assume init/cleanup idempotency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.c

Purpose: Implements multiport e-switch LAG mode. MPESW lets multiple PFs share eswitch/offloads behavior by allocating per-uplink metadata, creating LAG in `MLX5_LAG_MODE_MPESW`, reloading IB representatives, and updating aggregate vport speed.

Important APIs and flow: `mlx5_lag_mpesw_enable()` and `mlx5_lag_mpesw_disable()` queue synchronous work on the LAG workqueue. The worker serializes against devcom and `ldev->lock`, rejects mode changes in progress, then calls `mlx5_lag_enable_mpesw()` or `mlx5_lag_disable_mpesw()`. Enable validates offloads mode, port-selection FT support, non-master-up capability, normal LAG prerequisites, and shared FDB support; it sets metadata with `mlx5_esw_match_metadata_alloc()` and ingress ACL updates, removes devices, activates LAG, rescans drivers, reloads IB reps, and updates aggregate speeds. `mlx5_lag_mpesw_do_mirred()` blocks forwarding to a bond in MPESW mode.

State and dependencies: `ldev->lag_mpesw.pf_metadata[]` persists firmware metadata IDs until cleanup. MPESW integrates with eswitch ACLs, devcom locking, LAG activation/deactivation, notifier chains (`MLX5_DEV_EVENT_MULTIPORT_ESW`), IB auxiliary-device rescans, and port-change events.

Risks and test signals: Enable has multi-step rollback across metadata, devices, drivers, eswitch reps, and LAG state; failures must leave devices re-added and metadata freed. Tests should cover unsupported caps, queue-work failure, concurrent mode changes returning `-EAGAIN`, port up/down speed updates, TC mirred rejection, and disable from active MPESW.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.h

Purpose: Declares MPESW state and entry points for enabling/disabling multiport e-switch LAG and reacting to related events.

Important APIs and types: `struct lag_mpesw` stores pending work and per-port PF metadata IDs. `enum mpesw_op` distinguishes enable and disable requests. `struct mlx5_mpesw_work_st` carries queued work, completion, operation, target LAG, and result. Public APIs include `mlx5_lag_mpesw_enable()`, `mlx5_lag_mpesw_disable()`, `mlx5_lag_is_mpesw()`, `mlx5_lag_mpesw_do_mirred()`, plus eswitch-gated `mlx5_lag_disable_mpesw()`, `mlx5_mpesw_speed_update_work()`, and `mlx5_lag_mpesw_port_change_event()`.

State and dependencies: Includes LAG and mlx5 core definitions; event helpers compile to no-ops when `CONFIG_MLX5_ESWITCH` is disabled. The work-state struct makes the public enable/disable calls synchronous over an internal LAG workqueue.

Risks and test signals: Callers must not assume MPESW support when the eswitch feature is absent; build tests need both config branches. Runtime tests should verify that completion result propagation and metadata array cleanup match the implementation contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.c

Purpose: Builds hardware port-selection steering for mlx5 LAG. It creates match definers and hash-split flow tables so traffic buckets can forward to chosen uplink VHCA IDs, with optional inner-tunnel classification.

Important APIs and flow: `mlx5_lag_port_sel_create()` maps the requested `netdev_lag_hash` to traffic types, creates outer and optional inner definers for each TTC type, then creates inner and outer TTC tables. Definer setup chooses firmware match-definer formats for IPv4/IPv6, L4, MAC, VLAN, and inner/outer header fields. `mlx5_lag_create_port_sel_table()` creates a port-selection table, hash flow group, and one rule per LAG port/bucket with destination VHCA ID from the `ports[]` map. `mlx5_lag_port_sel_modify()` updates rule destinations for changed bucket mappings; `mlx5_lag_port_sel_destroy()` tears down TTCs, groups, tables, rules, and definers.

State and dependencies: `ldev->port_sel` owns the traffic-type bitmap, tunnel flag, outer/inner TTC handles, and definer arrays. The code depends on firmware port-selection namespace, match definers, TTC helpers from `lib/fs_ttc`, LAG bucket/v2p maps, VHCA IDs, and eswitch-enabled builds.

Risks and test signals: Error unwinding is nested across definer creation, tables, flow groups, and hundreds of rules; partial cleanup must preserve index math. Tests should exercise hash modes `L23`, `L34`, `E23`, `E34`, VLAN+src MAC, unsupported namespace/caps, tunnel inner TTC support, bucket remap modifications, and destroy after partial create failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.h

Purpose: Declares data structures and lifecycle functions for LAG port-selection flow steering.

Important APIs and types: `struct mlx5_lag_definer` groups a firmware match definer, flow table, flow group, and rule array sized by `MLX5_MAX_PORTS * MLX5_LAG_MAX_HASH_BUCKETS`. `struct mlx5_lag_ttc` pairs a TTC table with per-traffic-type definers. `struct mlx5_lag_port_sel` stores the selected traffic-type bitmap, tunnel flag, and outer/inner TTC state. Public calls are create, modify, and destroy.

State and dependencies: The header depends on `lib/fs_ttc.h` for traffic type constants and TTC table declarations. Under non-eswitch builds, port-selection APIs are no-op stubs returning success.

Risks and test signals: The rule array relies on stable LAG bucket limits and one-indexed `ports[]` values from implementation code. Compile coverage should include `CONFIG_MLX5_ESWITCH` on/off, and runtime validation should confirm create/modify/destroy calls are balanced by LAG mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.c

Purpose: Provides an ASO (accelerated steering object) send queue and completion queue abstraction used by mlx5 features such as IPsec, flow meters, and MACsec to post ACCESS_ASO WQEs.

Important APIs and flow: `mlx5_aso_create()` allocates an ASO object, creates a CQ, creates an SQ, and moves the SQ to RDY. CQ creation allocates a cyclic CQ WQ, initializes CQEs, fills PAS, assigns EQ/UAR/doorbell fields, and calls core CQ creation. SQ creation allocates cyclic WQ memory, sets PD, CQ number, UAR, page info, timestamp format from `clock.h`, and calls core SQ create/modify. Data path helpers are `mlx5_aso_get_wqe()`, `mlx5_aso_build_wqe()`, `mlx5_aso_post_wqe()`, and `mlx5_aso_poll_cq()`.

State and dependencies: `struct mlx5_aso` tracks producer/consumer counters, SQ number, WQ control, UAR mapping, CQ, and doorbell state. The implementation depends on mlx5 workqueue helpers, transport object commands, BFREG/UAR resources, DMA barriers, CQ polling helpers, and timestamp format decisions from the clock library.

Risks and test signals: Correct ordering depends on `dma_wmb()`, DB record update, `wmb()`, and UAR write order. Polling returns `-ETIMEDOUT` for no CQE and logs bad CQE syndromes. Tests should cover create/destroy error paths, WQE with and without data segment, CQ overrun prevention through `cc` updates, real-time/free-running timestamp formats, and ASO command failure diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.h

Purpose: Defines the wire-format WQE structures and exported helper API for mlx5 ASO operations.

Important APIs and types: Defines ASO WQEBB sizes, control flags, opcode modifier shift, MACsec DS count, ASO control/data segment structs, WQE structs with and without 64-byte data, logical/conditional/data-mask enums, and opcode modifiers for IPsec, flow meter, and MACsec. Exports create/destroy and WQE get/build/post/poll helpers.

State and dependencies: The header forward-declares `struct mlx5_aso`; callers operate on opaque ASO queues while filling WQE fields defined here. It depends on mlx5 QP/core definitions and firmware-compatible big-endian segment layout.

Risks and test signals: Layout and constants must remain ABI-compatible with firmware. Tests should verify WQE sizes/DS counts, opcode modifiers, read-enable semantics, and users that choose bytewise versus bitwise mask modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/clock.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/clock.c

Purpose: Implements mlx5 PTP hardware clock support, timestamp conversion, PPS input/output, cross timestamping, real-time clock programming, and shared-clock registration across functions.

Important APIs and flow: `mlx5_init_clock()` allocates per-device clock state, optionally registers a shared clock through devcom using firmware real-time clock identity, or allocates a per-function clock. `mlx5_init_clock_dev()` initializes the cyclecounter/timecounter, clock info page, overflow period, PPS pin config, and registers `ptp_clock_info`. PTP callbacks support get/set time, adjtime, adjfine, adjphase, max phase, auxiliary overflow work, external timestamp, periodic output, PPS, and optional PTM-based cross timestamp/cross cycles. `mlx5_clock_load()` registers PPS EQ notifications and arms PPS input; `mlx5_clock_unload()` unregisters and migrates shared event ownership; cleanup unregisters the PTP clock and frees shared/per-function state.

State and dependencies: `struct mlx5_clock_priv` wraps `struct mlx5_clock`, owner `mdev`, mutex for shared clocks, and event-owner device. The implementation uses seqlocks for timecounter state, firmware registers `MTPPS`, `MTUTC`, `MTCTR`, `MTPTM`, `MRTCQ`, devcom shared clock components, EQ notifiers, PTP kernel APIs, and optional x86 ART/ARM arch timer cross timestamping.

Risks and test signals: High-risk areas are shared-clock owner migration, PPS event delivery when `clock->ptp` registration fails, real-time versus free-running conversion, MTUTC range fallback to settime, overflow scheduling, pin capability verification, and concurrent load/unload. Tests should cover no device frequency fallback, real-time mode, cross timestamp availability, PPS in/out, NPPS duty cycle bounds, shared multi-function registration/unregistration, and internal error handling in overflow work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/clock.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/clock.h

Purpose: Declares mlx5 clock, timer, and PPS state plus timestamp conversion helpers and PTP lifecycle APIs.

Important APIs and types: `struct mlx5_pps` stores pin capabilities, scheduled output starts, enable state, minimum NPPS parameters, and armed pins. `struct mlx5_timer` stores cyclecounter/timecounter conversion data and overflow period. `struct mlx5_clock` contains a seqlock, PTP handle/info, PPS info, timer, and shared-clock flag. Public APIs include init/cleanup/load/unload, PTP index lookup, `mlx5_timecounter_cyc2time()`, `mlx5_real_time_cyc2time()`, and RQ/SQ timestamp translator selectors.

State and dependencies: The header depends on `CONFIG_PTP_1588_CLOCK`; without it, APIs are stubs. Real-time support is inferred from device timestamp format capabilities for RQ/SQ and `REAL_TIME_TO_NS` maps firmware high/low fields to nanoseconds.

Risks and test signals: Consumers must choose the correct translator for real-time versus free-running CQE timestamps. Build tests need PTP enabled/disabled, and runtime tests should verify seqlock conversion stability and `ptp_clock_index()` behavior when registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.c

Purpose: Manages mlx5 encryption key objects, including direct one-key creation and pooled bulk DEK allocation for TLS/IPsec/MACsec/PSP offloads.

Important APIs and flow: `mlx5_create_encryption_key()` and `mlx5_destroy_encryption_key()` wrap direct firmware general-object create/destroy. `mlx5_crypto_dek_init()` enables bulk DEK support when crypto caps expose `log_dek_max_alloc`, runs `SYNC_CRYPTO`, and stores the bulk object range. `mlx5_crypto_dek_pool_create()` initializes per-purpose pool lists/work. `mlx5_crypto_dek_create()` either creates a direct key or pops a free object offset from a bulk and modifies it with key material. `mlx5_crypto_dek_destroy()` returns pooled keys; a sync work item revalidates freed keys and a destroy work item frees excess idle bulks.

State and dependencies: Pools track total, available, and in-use counts plus partial/full/available/sync/wait/destroy lists. Bulks track base object ID, bitmaps for `in_use` and `need_sync`, and availability cursor. Locks are a mutex for pool lists and a spinlock for destroy-list transfer. The code depends on mlx5 command execution, encryption key object layout, PDN from `mlx5e_res`, workqueues, bitmaps, and secure stack zeroing of key material.

Risks and test signals: Key size is limited to 128 or 256 bits; 128-bit keys are placed in the second key slot. Pool correctness depends on bitmap state transitions and `SYNC_CRYPTO` thresholds. Tests should cover direct and pooled modes, invalid key sizes, command failures, pool exhaustion/add bulk, sync threshold behavior, destroy during pending work, wait-for-free handling, and no key leakage after modify/create commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.h

Purpose: Declares mlx5 crypto key-purpose constants and APIs for encryption key creation, pooled DEK allocation, and bulk DEK subsystem lifecycle.

Important APIs and types: Enumerates accelerator key purposes for TLS, IPsec, MACsec, PSP, and count sentinel. Forward-declares `mlx5_crypto_dek_pool`, `mlx5_crypto_dek`, and `mlx5_crypto_dek_priv`. Exports direct key create/destroy, pool create/destroy, DEK create/destroy/get-id, and init/cleanup for bulk DEK support.

State and dependencies: The API hides pool internals from feature users; consumers receive `struct mlx5_crypto_dek *` and use `mlx5_crypto_dek_get_id()` for firmware object references. It depends on mlx5 core device definitions and general object key purpose constants.

Risks and test signals: Callers must pair create/destroy with the same pool and not retain IDs after destroy. Build users should validate all four key purposes and both direct and pooled feature availability paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.c

Purpose: Implements a device-component communication registry that groups related mlx5 devices by component ID and match key, allows peer iteration, readiness gating, and event broadcast with rollback.

Important APIs and flow: Devices register with `mlx5_devcom_register_device()` and unregister by kref. Components register through `mlx5_devcom_register_component()`, which finds or creates a component matching ID/key/net namespace and handler, increments component refs, and attaches per-device data under the component rwsem. `mlx5_devcom_send_event()` calls the component handler on peers and rolls back earlier peers on error. Peer iteration is available under read lock or RCU. Lock helpers expose component write locking and trylock.

State and dependencies: Global `devcom_dev_list` and `devcom_comp_list` are protected by mutexes; each component owns a peer list, kref, ready flag, rwsem with lockdep class, match key, optional namespace, and event handler. `data` pointers are RCU-assigned for lockless peer lookup.

Risks and test signals: Handler mismatch for an existing component is rejected. Correctness depends on kref/lifetime pairing, rwsem use during ready changes, RCU read-side protection for RCU iteration, and rollback ordering. Tests should cover duplicate device registration, component sharing by key/ns, unregister while peers iterate, readiness false blocking iteration, event rollback, and lock/trylock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.h

Purpose: Declares the devcom registry API used by mlx5 subsystems that coordinate across peer devices.

Important APIs and types: Defines match flags, 32-byte match-key union, match attributes, component IDs (`ESW_OFFLOADS`, `MPV`, `HCA_PORTS`, `SD_GROUP`, `SHARED_CLOCK`), and event handler signature. Exposes device/component registration, event send, component size, ready state, peer iteration macros for locked and RCU contexts, and component lock helpers.

State and dependencies: Opaque `mlx5_devcom_dev` and `mlx5_devcom_comp_dev` handles isolate users from global registry internals. Match attributes optionally include a `struct net *` when namespace matching is requested.

Risks and test signals: Consumers must bracket peer iteration with begin/end or an RCU section as appropriate, and must not change ready state without holding the component lock. Compile and integration tests should cover each component ID user and namespace-key matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/dm.c

Purpose: Manages software-owned ICM device memory regions for steering, header modify, header modify pattern, and indirect encapsulation objects.

Important APIs and flow: `mlx5_dm_create()` checks SW ICM object support and allocates bitmaps for each firmware-advertised memory range, including v2 header modify pattern support. `mlx5_dm_sw_icm_alloc()` validates power-of-two block-aligned length, selects the memory range for the requested `enum mlx5_sw_icm_type`, finds aligned free blocks in the bitmap, creates a SW ICM general object, and returns physical address plus object ID. `mlx5_dm_sw_icm_dealloc()` destroys the object and clears the bitmap range. `mlx5_dm_cleanup()` warns on nonempty allocation bitmaps and frees them.

State and dependencies: `struct mlx5_dm` stores per-type allocation bitmaps protected by a spinlock. Size and base addresses come from device memory capabilities and `MLX5_LOG_SW_ICM_BLOCK_SIZE()`. The object command path uses `CREATE_GENERAL_OBJECT`/`DESTROY_GENERAL_OBJECT` with optional UID.

Risks and test signals: Address arithmetic must match firmware log sizes and alignment masks; command failure must clear pre-reserved bitmap bits. Tests should cover unsupported types/caps, invalid length/alignment, full-range exhaustion, allocation/deallocation symmetry, UID propagation, cleanup leak warnings, and v1/v2 capability combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/eq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/eq.h

Purpose: Defines core event queue structures and helper APIs for mlx5 asynchronous and completion EQ handling.

Important APIs and types: Declares tasklet context, CQ radix table, base `mlx5_eq`, async EQ, and completion EQ structures. Inline helpers compute EQ size, locate EQEs in fragmented buffers, check the next software-owned EQE by owner bit, and update the consumer index doorbell. Public APIs cover EQ table lifecycle, CQ add/delete, EQ lookup, IRQ-disabled polling, command recovery, IRQ synchronization, debugfs hooks, IRQ freeing, RFS CPU rmap, and completion IRQ number lookup.

State and dependencies: EQ state includes fragment buffer control, core device, CQ table, MMIO doorbell, consumer index, vector/IRQ numbers, EQ number, debug resource, and IRQ object. Doorbell writes are big-endian raw MMIO followed by `wmb()`.

Risks and test signals: Owner-bit handling and consumer-index doorbells are data-path critical. Tests should cover wraparound, arm versus no-arm doorbell offsets, CQ registration races, IRQ synchronization paths, debugfs lifecycle, and RFS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/eq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/events.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/events.h

Purpose: Declares mlx5 event utility types for port-module events and the driver notifier chain.

Important APIs and types: Defines masks for module status/error fields, enumerates module plugged/unplugged/error/disabled statuses and detailed module error causes, and defines `struct mlx5_pme_stats` counters indexed by those enums. Exports `mlx5_get_pme_stats()` and `mlx5_notifier_call_chain()`.

State and dependencies: The header depends on `mlx5_core.h` and is consumed by LAG/MPESW and other event producers to notify device subsystems.

Risks and test signals: Counter arrays are sized by enum sentinels, so new statuses/errors must update bounds consistently. Tests should check notifier fanout, PME counter indexing, and masks used when decoding raw module events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.c

Purpose: Implements dynamic flow-steering chains for TC/offload pipelines, mapping `(chain, priority, level)` to flow tables connected by explicit miss rules.

Important APIs and flow: `mlx5_chains_create()` initializes rhashtables, ranges, namespace, default/end flow tables, flags, and optional mapping context. `mlx5_chains_get_table()` validates ranges, recursively creates earlier levels, then creates or refs a `prio` object. Chain creation optionally allocates a chain mapping, restore rule, and modify-header action so miss-to-end can preserve chain identity. Prio creation builds a flow table, miss group, miss rule to the next level-0 table/end/default table, inserts it into sorted chain order, and rewires previous priority miss rules through `mlx5_chains_update_prio_prevs()`. Put/destroy reverses refs and rewiring.

State and dependencies: `struct mlx5_fs_chains` owns chain/prio rhashtables and mutex. `struct fs_chain` owns mapping/restore state and sorted prio list; `struct prio` owns FT, miss group, miss rule, next FT, and refcount. Dependencies include flow table pools/core, eswitch restore rules, TC register mappings, mapping contexts, and namespace-specific FDB/NIC RX behavior.

Risks and test signals: Rewiring miss rules in reverse order is delicate, especially on create failure and destroy. Range behavior changes with `MLX5_CHAINS_AND_PRIOS_SUPPORTED` and `IGNORE_FLOW_LEVEL`. Tests should cover sorted insertion, multi-level recursion unwinding, NF chain special case, global table creation, mapping default-flow-tag collision, FDB versus kernel namespace, tunnel flags, and unbalanced put warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.h

Purpose: Declares the flow-steering chains API for TC classifier/action users.

Important APIs and types: `enum mlx5_chains_flags` advertises chain/prio support, ignore-flow-level support, and tunnel table support. `struct mlx5_chains_attr` carries namespace, base priority/level, flags, group count, default table, and optional mapping context. Exports feature queries, range queries, table get/put, TC end table access, global table create/destroy, chain mapping get/put, lifecycle create/destroy, end table setter, and debug info.

State and dependencies: The API is available when `CONFIG_MLX5_CLS_ACT` is enabled; otherwise many calls are stubs returning unsupported or no-op. It depends on mlx5 flow table types and the mapping context type from implementation users.

Risks and test signals: Callers must balance table get/put for all implicit lower levels and handle `ERR_PTR(-EOPNOTSUPP)` in non-CLS_ACT builds. Build tests should cover both config branches and users of all exported flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.c

Purpose: Implements TTC (traffic type classifier) flow tables that classify RX traffic by IP version, L4 protocol/type, tunnel protocol, and IPsec decrypted ESP attributes, then forward to caller-provided destinations.

Important APIs and flow: `mlx5_create_ttc_table()` selects outer L4-type matching support, chooses group layout including optional IPsec RSS groups, creates the flow table/groups, and generates rules for each non-ignored traffic type and optional tunnel destination. `mlx5_create_inner_ttc_table()` builds equivalent inner-header tables. `mlx5_ttc_fwd_dest()` and `mlx5_ttc_fwd_default_dest()` update destinations after creation. IPsec helpers create/destroy decrypted ESP outer and inner rules with refcounting. Support helpers expose traffic names, table handle, tunnel inner-FT support, ESP group presence, and tunnel protocol mapping.

State and dependencies: `struct mlx5_ttc_table` stores group layout, core device, FT/groups, per-TT rule/default destination, tunnel rules, IPsec refcount, and mutex. It depends on mlx5 flow namespaces, firmware field support (`outer_ip_version`, `outer_l4_type`, inner variants), Linux IP protocol constants, and caller-provided `ttc_params` destinations/ignore bitmaps.

Risks and test signals: Group sizes/order must match generated rules and decrypted ESP ranges. Destroy assumes initialized mutex and group arrays; creation error paths call full destroy. Tests should cover outer and inner TTC, L4-type supported/unsupported, IPv4/IPv6 ethertype versus ip_version matching, tunnel support matrix, ignored destinations, destination modification, IPsec RSS refcounting, and create failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.h

Purpose: Declares TTC traffic types, tunnel types, parameter structure, and classifier table APIs.

Important APIs and types: `enum mlx5_traffic_types` includes IPv4/IPv6 TCP/UDP, AH/ESP, generic IPv4/IPv6/ANY, and decrypted ESP outer/inner L4 variants. `enum mlx5_tunnel_types` covers GRE, IPIP, and IPv4/IPv6-over-IPv4/IPv6. `struct ttc_params` supplies namespace, flow table attributes, per-traffic destinations, ignore bitmaps, inner TTC tunnel destinations, and IPsec RSS flag. Exports create/destroy, destination forwarding, tunnel support, IPsec rule creation/destruction, and decrypted ESP predicate.

State and dependencies: `struct mlx5_ttc_table` is opaque; callers own destination objects and table lifecycle through this API. Depends on mlx5 flow steering definitions.

Risks and test signals: Traffic-type enum order is used for array indexing and decrypted ESP range checks. Tests should validate enum additions against arrays in `fs_ttc.c`, ignore bitmap bounds, and callers that assume `MLX5_NUM_INDIR_TIRS = MLX5_TT_ANY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_ttc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.c

Purpose: Manages one firmware Geneve TLV option object for mlx5 offload users, with reference counting for repeated requests for the same option class/type.

Important APIs and flow: `mlx5_geneve_create()` allocates state and initializes a mutex. `mlx5_geneve_tlv_option_add()` validates the object manager, then either increments the refcount for matching class/type or creates a firmware `GENEVE_TLV_OPT` general object and records class/type/object ID. A different class/type while an object exists is rejected with `-EOPNOTSUPP`. `mlx5_geneve_tlv_option_del()` decrements refcount and destroys the firmware object on the final user. `mlx5_geneve_destroy()` frees any still-live object during unload.

State and dependencies: `struct mlx5_geneve` stores core device, option class/type, object ID, mutex, and refcount. It depends on Geneve option layout, mlx5 general object caps, and mlx5 command execution.

Risks and test signals: Only one TLV option object is supported at a time, and `del()` assumes a prior add because it pre-decrements refcount. Tests should cover unsupported caps, duplicate matching add/del, conflicting option add, destroy with nonzero refcount, and command failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.h

Purpose: Declares the mlx5 Geneve TLV option object API.

Important APIs and types: Forward-declares opaque `struct mlx5_geneve` and exports create/destroy plus TLV option add/delete when `CONFIG_MLX5_ESWITCH` is enabled. Without eswitch support, create returns NULL, destroy/delete are no-ops, and add returns success.

State and dependencies: Depends on `<net/geneve.h>` for `struct geneve_opt` and mlx5 driver types. The API hides firmware object ID and refcount details.

Risks and test signals: Stub behavior means callers must not treat a NULL object as fatal in non-eswitch builds. Build tests should cover both branches and ensure add/delete pairing in offload users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/gid.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/gid.c

Purpose: Manages reserved RoCE GID table indices and programs RoCE address entries into mlx5 firmware.

Important APIs and flow: `mlx5_init_reserved_gids()` initializes an IDA and positions the reserved range at the end of the firmware GID table. `mlx5_core_reserve_gids()` moves the reserved start downward and increases count with exhaustion checks; `mlx5_core_unreserve_gids()` reverses it. `mlx5_core_reserved_gid_alloc()` allocates a concrete index from the reserved range; `mlx5_core_reserved_gid_free()` releases it. `mlx5_core_roce_gid_set()` builds and sends `SET_ROCE_ADDRESS`, optionally filling VLAN, MAC, GID, RoCE version/L3 type, and VHCA port number.

State and dependencies: State lives in `dev->roce.reserved_gids` (`ida`, start, count). Dependencies include RoCE capabilities, Ethernet port type, Linux IDA, ether address helpers, mlx5 command layout, and exported symbols for RDMA users.

Risks and test signals: Reserve/unreserve is not internally locked here, so callers must serialize if needed. Tests should cover table exhaustion, max reserved limit, alloc/free range bounds, cleanup warning on leaked IDs, clearing a GID by passing NULL, VLAN programming, non-Ethernet rejection, and multi-vHCA port programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/gid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.c

Purpose: Wraps Hyper-V PCI config block access for mlx5 devices and exposes invalidate callback registration.

Important APIs and flow: `mlx5_hv_read_config()` and `mlx5_hv_write_config()` call a shared validator that requires block-aligned offsets and exact `HV_CONFIG_BLOCK_SIZE_MAX` length, computes block ID, invokes Hyper-V read/write helpers, verifies read byte count, and logs failures. `mlx5_hv_register_invalidate()` registers a block invalidate callback; unregister clears it.

State and dependencies: No persistent state is stored here; operations are immediate calls against `dev->pdev`. Depends on `CONFIG_PCI_HYPERV_INTERFACE`, Linux Hyper-V PCI helpers, and mlx5 logging.

Risks and test signals: Partial reads become `-EIO`, and invalid sizes/offsets return `-EINVAL`. Tests should cover alignment, block ID mapping, read byte count mismatch, callback register/unregister, and Hyper-V-disabled builds via the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.h

Purpose: Declares Hyper-V config block access functions for mlx5 when the PCI Hyper-V interface is enabled.

Important APIs and types: Exports read/write config helpers and invalidate callback registration/unregistration under `CONFIG_PCI_HYPERV_INTERFACE`. The callback reports a block mask to a caller-provided context.

State and dependencies: Includes Hyper-V and mlx5 driver headers only in the enabled branch, leaving no declarations otherwise.

Risks and test signals: Users must guard calls by config availability or include paths that only compile when declarations exist. Build tests should include Hyper-V interface enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.c

Purpose: Implements a Hyper-V vHCA agent framework where mlx5 subagents advertise capabilities, react to host control blocks, handle invalidations asynchronously, and write agent data blocks to Hyper-V config space.

Important APIs and flow: `mlx5_hv_vhca_create()` allocates state and a single-thread workqueue; `mlx5_hv_vhca_init()` registers the Hyper-V invalidate callback and creates the control agent. Invalidations allocate work in atomic context and later dispatch to matching agents under `agents_lock`. The control agent reads block 0, computes capability bits from registered agents, rejects unsupported controls, calls agent control callbacks, and writes command acknowledgements. `mlx5_hv_vhca_agent_create()` registers a typed agent and triggers capability update; destroy removes it, calls cleanup, frees it, and updates capabilities. `mlx5_hv_vhca_agent_write()` fragments payloads into fixed config blocks with sequence and offset.

State and dependencies: `struct mlx5_hv_vhca` stores core device, workqueue, agent array, and mutex. Agents store type, callbacks, private pointer, and sequence. It depends on `hv.c` config helpers, Hyper-V invalidation, fixed block size, and agent type bit masks.

Risks and test signals: The control-agent bit mapping uses `AGENT_MASK(type)` where control type maps to zero; capability/control semantics depend on host agreement. Tests should cover duplicate/out-of-range agent types, invalidate allocation failure, create/init cleanup failures, control block with unsupported bits, write fragmentation/sequence increments, cleanup with live agents warnings, and concurrent agent create/destroy versus invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.h

Purpose: Declares the Hyper-V vHCA object and agent API.

Important APIs and types: Defines agent types for control and stats with a 32-slot maximum, and the Hyper-V control block layout (`capabilities`, `control`, `command`, `command_ack`, `version`, `rings`). Exports create/destroy/init/cleanup, invalidate callback, agent create/destroy/write, and private-data access when Hyper-V PCI support is enabled; otherwise provides stubs.

State and dependencies: Includes mlx5 ethernet and Hyper-V helper headers. Opaque structs keep implementation state private while callbacks receive agent handles and control blocks.

Risks and test signals: Stub paths return NULL or zero, so consumers must handle absent Hyper-V support. ABI-sensitive control block fields and agent type bit positions need compatibility tests with host-side expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.c

Purpose: Builds RoCE-specific IPsec flow steering for RX and TX, including MPV slave/master alias flow-table support for cross-vHCA forwarding.

Important APIs and flow: `mlx5_ipsec_fs_roce_init()` discovers RDMA RX/TX IPsec namespaces and stores devcom access. RX create builds a NIC table with RoCE UDP dport rule and miss rule, creates RDMA destination table, and in MPV slave mode creates master-side NIC/RDMA tables plus an alias/goto table. TX create builds an RDMA TX table forwarding to the policy table, or in MPV slave mode creates an alias to the master policy table and matches source VHCA port. Destroy functions remove rules, groups, tables, and aliases. Support helpers include `mlx5_ipsec_fs_roce_ft_get()` and `mlx5_ipsec_fs_is_mpv_roce_supported()`.

State and dependencies: `struct mlx5_ipsec_fs` owns IPv4 RX, IPv6 RX, TX, and a devcom pointer. RX/TX state holds flow tables, groups, rules, alias IDs, access keys, namespaces, and master-side tables. Dependencies include flow steering core/cmds, RDMA and NIC IPsec namespaces, devcom peer iteration, MPV core helpers, random access key generation, and firmware cross-vHCA alias commands.

Risks and test signals: Alias creation is cross-device and has asymmetric allow/create/destroy ownership. MPV event recreation passes `from_event` to reuse alias keys. Tests should cover non-MPV and MPV RX/TX, missing peer or peer IPsec, alias capability failures, IPv4/IPv6 level differences, default destination as flow table with ignore-flow-level, partial create cleanup, double destroy after event cleanup, and support predicate behavior when MP is enabled without alias caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.h

Purpose: Declares RoCE IPsec flow-steering lifecycle and table access APIs.

Important APIs and types: Forward-declares `struct mlx5_ipsec_fs`. Exports RX/TX create/destroy, RX flow-table getter by address family, init/cleanup, and MPV RoCE support check. Create calls require core device, namespace or policy/default destinations, family/level/prio arguments, and optional devcom pointer from init.

State and dependencies: The header includes devcom declarations because MPV alias flows need peer-device coordination. Implementation state remains opaque to consumers.

Risks and test signals: Callers must pass matching family to RX get/destroy and must call cleanup after RX/TX teardown. Tests should validate NULL `ipsec_roce` no-op behavior and MPV support checks before enabling RoCE IPsec in multiport mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.h -->
