# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.h

## Purpose

`qed_l2.h` declares the internal L2/Ethernet slowpath contract used by QED. It defines RSS, TPA/GRO, filter, accept-mode, vport update, aRFS, queue CID, and VF queue parameter structures, plus the internal functions used to allocate L2 state, start/stop vports and queues, program filters, collect stats, configure aRFS, and read/write queue coalescing.

The header sits between the public `linux/qed/qed_eth_if.h` interface and the driver implementation in `qed_l2.c`. It also exposes selected helpers to other QED modules such as SR-IOV and device setup.

## Important APIs, types, and constants

- `struct qed_rss_params` carries RSS update flags, engine ID, capabilities, indirection table of RX queue handles, table size log, and RSS key.
- `struct qed_sge_tpa_params` describes TPA/GRO enable flags and aggregation sizing.
- `enum qed_filter_opcode` defines add, remove, move, replace, and flush semantics.
- `enum qed_filter_ucast_type` covers MAC, VLAN, MAC/VLAN, inner variants, MAC/VNI, inner MAC/VNI, and VNI filters.
- `struct qed_filter_ucast` and `struct qed_filter_mcast` are firmware-facing filter command inputs.
- `enum qed_tpa_mode` defines no TPA, unused, GRO, and max values.
- `struct qed_sp_vport_start_params` and `struct qed_sp_vport_update_params` are the internal vport ramrod input structures.
- `struct qed_filter_accept_flags` defines RX/TX accept-mode update flags and bitmasks for matched/unmatched unicast, multicast, broadcast, any VNI, and accept-none behavior.
- `struct qed_arfs_config_params` carries aRFS protocol-family and mode configuration.
- `MAX_QUEUES_PER_QZONE` and `QED_QUEUE_CID_SELF` define queue-zone usage indexing and self-owned queue identity.
- `struct qed_queue_cid_vf_params` carries PF-side metadata needed when opening queues for VFs, including legacy behavior flags.
- `struct qed_queue_cid` is the queue handle returned to callers and passed back for queue stop, coalescing, RSS indirection, and ramrod programming.

Declared functions include L2 lifecycle (`qed_l2_alloc/setup/free`), queue CID conversion and release, vport start/update/stop, queue start/stop ramrods, unicast filtering, RX queue update, stats get/reset, aRFS mode and ntuple configuration, multicast bin hashing, and coalescing get/set helpers.

## Control flow represented by the header

The header's data model makes queue setup a two-step operation: first convert common queue parameters into a `qed_queue_cid`, then issue RX or TX queue start ramrods using that handle. The same handle is later supplied to stop and coalescing helpers and is also used in RSS indirection tables.

Vport control flows are represented by start/update/stop parameter structs. A vport can be started with MTU, VLAN stripping, TPA mode, PTP handling, TTL0 drop, TX switching, and control-frame checks. Later updates can independently change active flags, VLAN behavior, default VLAN, TX switching, multicast bins, anti-spoofing, accept-any-VLAN, RSS, accept flags, SGE/TPA parameters, and control-frame checks.

Filter flow is split between generic accept-mode flags, exact unicast-style filter commands, and approximate multicast bin vectors. aRFS flow is represented by a mode configuration struct plus ntuple filter parameters from the public Ethernet interface.

## State and persistence behavior

The header defines transient runtime structures. `struct qed_queue_cid` is the most important ownership object: it stores relative and absolute vport/queue/stats IDs, status-block identity, firmware CID, opaque FID, RX/TX direction, VF identity, queue-zone usage index, legacy VF flags, and owning hwfn. The queue handle persists while a queue is started and is released by queue stop or explicit release on failure.

RSS indirection state stores queue handles rather than queue numbers, so callers must keep those queue handles alive while RSS updates are built. Vport and filter structs are command payloads, not persistent owners. Accept/filter constants encode desired firmware state and are not durable outside device configuration.

## Dependencies and integration points

The header includes Linux type and IO headers, `linux/qed/qed_eth_if.h`, and QED core headers for `struct qed_hwfn`, hardware access, and SPQ completion types. It depends on public Ethernet constants such as `QED_RSS_IND_TABLE_SIZE`, `QED_RSS_KEY_SIZE`, `QED_MAX_MC_ADDRS` behavior, `struct qed_eth_stats`, and `struct qed_ntuple_filter_params`.

Other modules use this header when they need direct L2 queue/vport/filter helpers, especially PF-side SR-IOV code that constructs queue CIDs for VF queues and non-Linux VF support that updates RX queues.

## Risks and edge cases

- `struct qed_rss_params` stores `void *` queue handles, so type safety depends on callers passing valid `struct qed_queue_cid` handles.
- `MAX_QUEUES_PER_QZONE` is tied to one `unsigned long` worth of bits; queue-zone sharing behavior changes if firmware or platform expectations exceed that.
- VF queue CID fields are meaningful only on PF-created queue handles for VF queues, which can be misused if callers treat them as normal VF-local state.
- Filter opcode support differs by filter type; multicast explicitly does not support MOVE, while unicast supports richer move/replace behavior.
- Coalescing setters are declared here but implemented elsewhere in the QED L2/coalescing path, so users of the header must link the complete driver objects.
- Vport update uses many independent `update_*` flags; missing a flag can make a populated value a no-op, while setting an update flag with stale values can unintentionally change firmware state.

## Test signals

Header-driven integration tests should compile PF, VF, SR-IOV, DCB, and PTP configurations; validate that queue handles flow correctly through start, RSS update, coalescing, and stop; exercise vport update combinations with and without update flags; verify filter opcode/type combinations; validate multicast maximum address limits; cover legacy VF queue flags; and ensure all prototypes match the implementations used by `qed_eth_ops_pass`.
