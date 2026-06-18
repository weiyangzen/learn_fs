# sources/distributed-fs/ceph-client/net/smc/smc_wr.h

Purpose: Declares SMC-R work-request constants, callback types, inline helpers, and public WR lifecycle/TX/RX APIs.

Important APIs/types/functions: Defines `SMC_WR_TX_WAIT_FREE_SLOT_TIME`, `SMC_WR_TX_SIZE`, and `SMC_WR_TX_PEND_PRIV_SIZE`. `struct smc_wr_tx_pend_priv` is opaque completion context storage. Callback typedefs cover TX completion, filtering, and dismissal. `struct smc_wr_rx_handler` maps receive message types to handlers. Inline helpers generate WR IDs, manage link percpu references, wake/drain wait queues, and post receive WRs by WR ID modulo queue size.

Control flow: Callers allocate/create link WR resources, reserve TX slots, send WRs, optionally wait for completion, register RX handlers, post initial receives, and free resources at teardown. `smc_wr_rx_post()` increments the tasklet-context RX ID and posts the next receive buffer to the QP.

State and persistence behavior: No standalone state is owned by the header. Its helpers mutate per-link WR IDs, references, waits, and IB receive WR descriptors.

Dependencies and integration points: Depends on RDMA ib verbs, SMC core structures, and `smc.h`. It is used by CDC, LLC, TX, link setup, and device lifecycle code.

Risks and test signals: Risks include using `smc_wr_rx_post()` outside its expected serialization, failing to hold `wr_tx_refs` around sends, and mismatching pending private storage size with users. Test compile-time users, RX queue wrap, reference kill/drain during teardown, WR slot reservation/release, and SMC-Rv2 slot usage.
