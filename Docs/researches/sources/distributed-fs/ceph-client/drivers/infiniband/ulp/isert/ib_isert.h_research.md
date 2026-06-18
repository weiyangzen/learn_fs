# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/ib_isert.h

Purpose: Defines private structures, constants, inline buffer helpers, connection states, descriptor types, and debug macros for the iSER target implementation.

Important APIs/types/functions: Major types are `iser_rx_desc`, `iser_tx_desc`, `isert_cmd`, `isert_conn`, `isert_device`, and `isert_np`. Inline helpers convert CQEs to descriptors (`cqe_to_rx_desc()`, `cqe_to_tx_desc()`), recover `isert_cmd` from TX descriptors, and compute aligned iSER/iSCSI header/data offsets in RX buffers (`isert_get_iser_hdr()`, `isert_get_hdr_offset()`, `isert_get_iscsi_hdr()`, `isert_get_data()`). Constants define PDU sizes, QP send/recv DTO budgets, minimum posted RX threshold, and SG table limits.

Control flow: RX buffers allocate extra space so the data payload can be 512-byte aligned after iSER and iSCSI headers. TX descriptors carry a control or Data-IN response header plus optional second payload SGE. `isert_cmd` links target-core command state to one RX descriptor, one TX descriptor, remote keys/addresses, and an RDMA RW context. `isert_conn` models state transitions from INIT through UP, BOUND, FULL_FEATURE, TERMINATING, and DOWN.

State and persistence: Header structs define all persistent runtime state for the target transport: listener accepted/pending lists, per-device PD/refcount, per-connection login/RX/QP/CQ/kref/work state, and per-command RDMA state. `in_use` on RX descriptors prevents double reposting.

Dependencies and integration: Includes RDMA verbs/CM/RW helpers and the shared iSER protocol header. It is consumed only by `ib_isert.c` and matches target-core private command allocation through `priv_size = sizeof(struct isert_cmd)`.

Risks: RX header/data alignment math is critical; any change to `ISER_RX_SIZE`, `ISER_HEADERS_LEN`, or descriptor layout can break 512-byte payload alignment. QP constants assume `ISCSI_DEF_XMIT_CMDS_MAX` is a power of two and that send/recv WR budgets match implementation behavior. Test signals include build coverage, alignment assertions from `isert_get_data()`, RX repost idempotence, PI and non-PI command struct paths, and state-machine transition coverage.
