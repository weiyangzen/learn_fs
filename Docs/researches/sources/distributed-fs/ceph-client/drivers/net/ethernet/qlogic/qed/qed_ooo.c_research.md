# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.c

Purpose: Manages software bookkeeping for TCP out-of-order packet buffers. It groups buffers into per-connection ordered "isles", tracks ready/free buffers, records recent OOO CQEs, and supports iSCSI, NVMe/TCP, and iWARP personalities.

Important APIs/types/functions: Allocation/setup/free are `qed_ooo_alloc()`, `qed_ooo_setup()`, and `qed_ooo_free()`. Lookup helpers map CID to an archipelago and numbered isle. Buffer movement APIs include `qed_ooo_put/get_free_buffer()`, `qed_ooo_put/get_ready_buffer()`, `qed_ooo_add_new_isle()`, `qed_ooo_add_new_buffer()`, `qed_ooo_join_isles()`, `qed_ooo_delete_isles()`, `qed_ooo_release_connection_isles()`, and `qed_ooo_release_all_isles()`. `qed_ooo_save_history_entry()` stores a circular history of firmware OOO opaque records.

Control flow: Allocation chooses protocol by PCI personality, sizes archipelagos from protocol CID count, allocates isle entries as `QED_MAX_NUM_ISLES + max_connections`, initializes free lists, allocates archipelago array and history storage, and attaches state to `p_hwfn`. Runtime operations locate the per-CID archipelago by `(cid & 0xffff) - cid_base`, splice buffers between isle, ready, and free lists, and recycle isle descriptors. Joining isle zero moves the right isle into the global ready list; joining a nonzero left isle appends into that left isle.

State and persistence: `p_hwfn->p_ooo_info` owns free/ready/isle lists, archipelago array, isle array, circular history, and counters for current/max/generated isles. Packet buffers own DMA-coherent receive storage and are freed only from the free list during `qed_ooo_free()`.

Dependencies/integration: Depends on QED context manager CID ranges, protocol personality selection, Linux list API, DMA coherent allocation/free, and OOO CQE definitions from the storage/iWARP HSI.

Risks: Most list manipulation has no local locking; callers must serialize access. Isle numbering is one-based in firmware events but implemented through list traversal, so invalid or stale isle numbers just log and return. `qed_ooo_add_new_isle()` initializes an archipelago without validating the computed CID index after failed lookup for isle one. Freeing assumes all buffers eventually return to `free_buffers_list`.

Test signals: Cover allocation for iSCSI, NVMe/TCP, iWARP, and unsupported personalities; add left/right buffers, join isles to ready and to another isle, delete ranges, release one connection/all connections, circular history wrap, and teardown with allocated DMA buffers.
