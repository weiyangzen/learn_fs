# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ll2.h

## Purpose

`qed_ll2.h` is the internal header for the QED light-L2 implementation. It defines the per-connection data structures used by `qed_ll2.c`, declares the low-level LL2 lifecycle/data-path/stat APIs, and exposes the public `qed_ll2_ops_pass` vtable for protocol-facing code.

The header is not the external consumer ABI; it includes `linux/qed/qed_ll2_if.h` for public parameter/callback/stat types and then defines driver-private queue and descriptor state around those public types.

## Important APIs, types, and constants

Connection capacity constants define a small fixed table:

- `QED_MAX_NUM_OF_LL2_CONNECTIONS` is 4.
- `QED_MAX_NUM_OF_LL2_CONNS_PF` is 4.
- `QED_MAX_NUM_OF_LEGACY_LL2_CONNS_PF` is 3.
- `QED_MAX_NUM_OF_CTX_LL2_CONNS_PF` is one context-based queue.
- `QED_LL2_LEGACY_CONN_BASE_PF` starts at 0.
- `QED_LL2_CTX_CONN_BASE_PF` starts after the legacy region.

`struct qed_ll2_rx_packet` is the software descriptor corresponding to an RX BD. It stores list linkage, the produced RX BD pointer, DMA address, buffer length, callback cookie, placement offset, parse flags, packet length, VLAN, and two opaque data words copied from firmware CQEs.

`struct qed_ll2_tx_packet` is the software descriptor corresponding to a TX packet. It has list linkage, BD count, a notify flag, a callback cookie, and a flexible array `bds_set[]` sized at allocation time by `tx_max_bds_per_packet`; each fragment slot stores a TX BD pointer, DMA address, and length.

`struct qed_ll2_rx_queue` owns RX queue synchronization and hardware state:

- `lock` protects RX chain and descriptor-list mutation.
- `rxq_chain` is the produced RX BD chain.
- `rcq_chain` is the consumed RX completion chain.
- `rx_sb_index` and `p_fw_cons` are assigned by interrupt callback registration.
- `ctx_based` selects context-doorbell vs legacy producer-register notification.
- `b_cb_registered` gates completion processing.
- `active_descq`, `free_descq`, and `posting_descq` represent buffers owned by firmware, available to software, and staged for later notification.
- `set_prod_addr` and `db_data` carry producer notification target/state.

`struct qed_ll2_tx_queue` owns TX queue synchronization and hardware state:

- `lock` protects TX chain, descriptor lists, and partial packet construction.
- `txq_chain` is the TX BD chain.
- `tx_sb_index`, `p_fw_cons`, `doorbell_addr`, and `db_msg` connect to interrupt and doorbell hardware.
- `active_descq`, `free_descq`, and `sending_descq` represent packet descriptors visible to firmware, reusable by software, and complete-but-not-yet-doorbelled.
- `cur_send_packet`/`cur_send_frag_num` track a partially filled multi-BD packet.
- `cur_completing_packet`/`cur_completing_bd_idx`/`cur_completing_frag_num`/`b_completing_packet` track completion progress.
- `descq_mem` stores the contiguous variable-sized `qed_ll2_tx_packet` descriptor pool.

`struct qed_ll2_info` is the per-connection slot:

- `mutex` protects active state changes.
- `input` preserves `struct qed_ll2_acquire_data_inputs` for later queue start and behavior decisions.
- `cid`, `my_id`, `queue_id`, `tx_stats_id`, `tx_dest`, `tx_stats_en`, and `main_func_queue` mirror firmware context/queue identity.
- `b_active` marks slot ownership.
- `cbs` stores required completion/release callbacks.
- `rx_queue` and `tx_queue` contain the queue state.

Declared functions cover lifecycle (`qed_ll2_alloc`, `qed_ll2_setup`, `qed_ll2_free`, `qed_ll2_acquire_connection`, `qed_ll2_establish_connection`, `qed_ll2_terminate_connection`, `qed_ll2_release_connection`), datapath (`qed_ll2_post_rx_buffer`, `qed_ll2_prepare_tx_packet`, `qed_ll2_set_fragment_of_tx_packet`), and stats (`qed_ll2_get_stats`).

## Control flow encoded by the API shape

The API enforces a two-phase connection setup. Callers first call `qed_ll2_acquire_connection()` to reserve a handle and allocate queues, then `qed_ll2_establish_connection()` to start firmware queues. RX buffers can be posted only after establish has built `set_prod_addr`; TX packets can be prepared only once TX chains and doorbells are initialized. Teardown is also two-phase: `qed_ll2_terminate_connection()` stops firmware-visible queues and flushes descriptors, then `qed_ll2_release_connection()` frees allocations and marks the handle inactive.

The TX API models multi-fragment packets explicitly. The first fragment and packet-level metadata are submitted with `qed_ll2_prepare_tx_packet()`, and additional fragments are appended by repeated `qed_ll2_set_fragment_of_tx_packet()` calls until `num_of_bds` is satisfied. This is why `struct qed_ll2_tx_queue` stores a current send packet and fragment cursor.

The RX API leaves buffer allocation to the caller. `qed_ll2_post_rx_buffer()` accepts a DMA address, length, cookie, and a `notify_fw` flag. The cookie is returned through completion/release callbacks so higher layers can own SKBs, OOO buffers, or protocol-specific buffer objects.

## State and persistence behavior

All declarations describe volatile driver state. The structures persist only for the lifetime of a `struct qed_hwfn`, `struct qed_dev`, or active LL2 connection. No disk persistence is defined. Hardware/firmware state associated with these structures is managed by implementation functions in `qed_ll2.c`.

Ownership is split deliberately:

- The connection table is stored on `struct qed_hwfn` as `p_ll2_info`.
- Public LL2 wrapper state is stored on `struct qed_dev` as `cdev->ll2` and is allocated/deallocated by `qed_ll2_alloc_if()`/`qed_ll2_dealloc_if()` in the implementation.
- External protocol callbacks and public parameter structures come from `qed_ll2_if.h`; this header stores them internally but does not define their public ABI.

## Dependencies and integration points

The header includes Linux core types, list, mutex, slab, spinlock, `qed_chain`, and public LL2 interface definitions. It also includes `qed.h`, `qed_hsi.h`, and `qed_sp.h`, binding the LL2 interface to QED hardware/software queue formats and slowpath request infrastructure.

`qed_main.c` includes this header so slowpath startup can allocate the public LL2 interface and so the core common ops can coexist with LL2 support. `qed_ll2.c` is the primary implementation consumer. Other QED protocol code interacts mostly through the external `qed_ll2_ops_pass` and public `qed_ll2_if.h` types.

## Risks and edge cases

- The header fixes maximum LL2 connection count at four and partitions only one context-based queue. New firmware queue types or additional context queues would require coordinated constant and mapping changes.
- `struct qed_ll2_tx_packet` uses a flexible array and is allocated as a custom stride in `qed_ll2.c`; any copy, stack allocation, or `sizeof` misuse would be wrong.
- Queue list fields require strict initialization before use. The header alone does not encode which lists are valid before establish.
- `p_fw_cons` is a pointer filled by interrupt registration; completion functions require it to be valid when `b_cb_registered` is true.
- `ctx_based` changes the producer notification width and recovery registration behavior. Tests should exercise both legacy and context-based RX queues.

## Test signals

Compile-time signals include structure layout compatibility with firmware BD/CQE definitions and successful build under configurations with LL2, storage, RDMA, and SR-IOV enabled. Runtime signals include successful handle allocation across legacy/context ranges, correct behavior at connection-table exhaustion, queue start with RX-only or TX-only descriptor counts, and safe teardown with active descriptors. Static-analysis focus should include flexible-array allocation arithmetic, list ownership, callback pointer validation, and locking expectations around the queue structs.
