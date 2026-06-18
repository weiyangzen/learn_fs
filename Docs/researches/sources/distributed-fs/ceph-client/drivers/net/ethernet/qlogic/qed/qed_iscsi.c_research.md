# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.c

## Purpose
`qed_iscsi.c` implements the QED iSCSI/TCP offload interface. It manages iSCSI function start/stop ramrods, connection resource allocation and hashing, TCP/iSCSI connection offload/update/termination ramrods, BDQ producer address exposure, async event delivery, firmware statistics collection, and the exported `qed_iscsi_ops` table.

## Important APIs, Types, and Functions
- `struct qed_iscsi_conn` stores connection identity, firmware CIDs, queue chains, DMA buffers, TCP offload state, MAC/IP/port tuples, timers, sequence/window state, iSCSI update fields, physical queues, and abortive disconnect state.
- `qed_sp_iscsi_func_start()` and `qed_sp_iscsi_func_stop()` issue function init/destroy ramrods and register/unregister async callbacks for `PROTOCOLID_TCP_ULP`.
- `qed_sp_iscsi_conn_offload()`, `qed_sp_iscsi_conn_update()`, `qed_sp_iscsi_mac_update()`, `qed_sp_iscsi_conn_terminate()`, and `qed_sp_iscsi_conn_clear_sq()` build SPQ ramrods for connection lifecycle operations.
- `qed_iscsi_allocate_connection()`, `qed_iscsi_acquire_connection()`, `qed_iscsi_release_connection()`, and `qed_iscsi_free_connection()` manage connection memory, chains, CIDs, and the free list.
- Stats helpers read T/M/U/X/Y/P storm iSCSI stats from IRO offsets using `qed_memcpy_from()`.
- Public facade functions implement `start`, `stop`, `acquire_conn`, `release_conn`, `offload_conn`, `update_conn`, `destroy_conn`, `clear_sq`, `get_stats`, and `change_mac`.
- `qed_get_iscsi_ops()` and `qed_put_iscsi_ops()` are exported symbols.

## Control Flow
The upper iSCSI client obtains `qed_iscsi_ops`, fills device info, starts storage, acquires connection handles, offloads connection state, updates or changes MAC as needed, destroys/clears connections, releases handles, and finally stops storage. Start posts an init ramrod, sets `QED_FLAG_STORAGE_STARTED`, initializes the connection hash, and optionally returns TID block information. Acquire allocates a hash node, obtains a TCP_ULP CID, allocates or reuses a connection, zeros DMA/query queues, stores handle/fw CID, hashes it, and returns the doorbell address. Offload copies user-supplied TCP/IP/iSCSI parameters into `qed_iscsi_conn`, selects OFLD and ACK physical queues, writes PBL addresses and TCP state into the ramrod, and posts it synchronously. Destroy posts termination and writes upload/query DMA addresses so firmware can return final TCP state and queue counters.

Stats acquisition gets a PTT in atomic or sleeping mode, reads per-storm stats blocks at `BAR0_MAP_REG_*SDM_RAM + *_ISCSI_*_STATS_OFFSET(rel_pf_id)`, converts little-endian register pairs, and releases the PTT. MCP protocol stats are a reduced translation to rx/tx PDUs and bytes.

## State and Persistence
State is stored in `p_hwfn->p_iscsi_info`, its spinlock and free connection list, each connection's coherent DMA buffers/chains, `cdev->connections` hash table, `QED_FLAG_STORAGE_STARTED`, protocol callback pointers, event context/callback, and firmware state created by SPQ ramrods. No disk persistence is used.

## Dependencies and Integration Points
The file depends on QED context CID allocation, SPQ ramrod infrastructure, LL2 operations, interrupt SB id lookup, QED chain allocation, DMA coherent memory, IRO offsets, hardware register access, SR-IOV/resource macros, and the public Linux `qed_iscsi_if.h` API. It integrates with firmware through TCP_ULP/iSCSI ramrods and with management firmware through `qed_get_protocol_stats_iscsi()`.

## Risks
- Stop refuses to proceed while the connection hash is non-empty; leaked handles block shutdown.
- The free-list reuse path returns an existing connection without reallocating chains, so `qed_iscsi_setup_connection()` must reset all reusable firmware-visible memory.
- Several public operations depend on `QED_FLAG_STORAGE_STARTED`; calling them before start yields lookup failure.
- `qed_iscsi_change_mac()` finds the connection but currently posts the existing `con->remote_mac`; it does not copy the `mac` argument into the connection before issuing the ramrod.
- `qed_iscsi_alloc()` initializes the list but `qed_iscsi_setup()` must be called to initialize the spinlock before concurrent use.
- Offload parameter copying is large and field-by-field; missed endian conversion or duplicate source fields can be hard to detect.

## Test Signals
Validation includes function start/stop ramrod success, async event callback delivery, acquire/offload/update/terminate/release cycles under load, no connection hash leaks on stop, correct doorbell and BDQ producer addresses, iSCSI traffic success for IPv4/IPv6/VLAN paths, stats increasing in the expected storm counters, and targeted testing of MAC update behavior.
