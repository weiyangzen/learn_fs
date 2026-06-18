# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.h

Purpose: defines the public cxgb4 ULD contract, TID/resource tables, WR initialization macros, offload send/filter APIs, and low-level information passed to upper-layer drivers.

Important APIs/types: WR macros `INIT_TP_WR`, `INIT_TP_WR_CPL`, `INIT_ULPTX_WR`; `struct tid_info`, TID lookup/allocation helpers, EOTID helpers, `struct filter_ctx`, `enum cxgb4_uld`, `enum cxgb4_state`, `enum cxgb4_control`, `struct cxgb4_virt_res`, `struct cxgb4_lld_info`, and `struct cxgb4_uld_info`; prototypes for ULD registration, offload sends, server/filter operations, stats, BAR2 queue register lookup, and hardware reads.

Control flow/state: inline TID helpers update pointer tables and atomic usage counters for regular, hash, connection, and ETHOFLD TIDs. `cxgb4_lld_info` is the snapshot of adapter resources handed to a ULD at attach time; `cxgb4_uld_info` is the callback table registered by a ULD.

Dependencies/integration: includes core cxgb4 definitions, skb, inetdevice, TLS, and spinlock/atomic headers. Used by RDMA/iSCSI/crypto/TLS consumers and by internal TC/filter code needing TID and filter APIs.

Risks: many helpers are inline and assume caller-side locking around bitmaps and tables. Resource ranges and queue counts must match firmware initialization. Optional structs under TLS/IPsec config guards change compiled surface. `set_wr_txq` encodes priority and queue into skb queue mapping, so users must preserve that convention.

Test signals: compile matrix for TLS/IPsec configs, TID/EOTID allocation under contention, ULD callback ABI changes, filter completion paths using `filter_ctx`, and offload send queue mapping.
