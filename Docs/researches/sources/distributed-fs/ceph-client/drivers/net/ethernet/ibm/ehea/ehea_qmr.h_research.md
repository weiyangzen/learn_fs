# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_qmr.h

Purpose: Defines eHEA queue/memory-region constants, WQE/CQE/EQE formats, work-request ID encoding, error masks, queue iterator helpers, and QMR public prototypes.

Important APIs and types: Page and section constants include `EHEA_PAGESIZE`, `EHEA_SECTSIZE`, `EHEA_PAGES_PER_SECTION`, `EHEA_HUGEPAGE_SIZE`, and a compile-time assertion that kernel section size is large enough. `struct ehea_vsgentry`, `ehea_swqe`, `ehea_rwqe`, `ehea_cqe`, and `ehea_eqe` describe send, receive, completion, and event entries. `EHEA_WR_ID_*` encodes completion type, index, count, and refill credits. TX flags include checksum, TSO, VLAN insert, immediate data, descriptors, and purge. Inline queue helpers calculate current entries, increment with toggle-state wrap, validate CQ/EQ entries, fetch SWQEs/RWQEs, post SWQEs, and poll RQ1/CQs.

Control flow: `ehea_main.c` uses `ehea_get_swqe()` and `ehea_post_swqe()` in TX, `ehea_get_next_rwqe()` in RX refill, `ehea_poll_rq1()`/`ehea_inc_rq1()` in RX completion, and `ehea_poll_cq()`/`ehea_inc_cq()` in send completion. `ehea_qmr.c` implements the resource and MR prototypes declared here.

State and persistence: Queue state is held in `struct hw_queue` from `ehea.h`; inline helpers mutate `current_q_offset` and `toggle_state`. WQE `wr_id` carries software state through hardware completions, tying CQEs back to skb arrays and refill credit accounting. No persistent storage.

Dependencies and integration: Depends on Linux prefetch helpers, `ehea.h`, and `ehea_hw.h`. It bridges hardware entry formats to the netdev data path in `ehea_main.c`.

Risks: Queue toggle validation is central to detecting valid CQEs/EQEs; off-by-one or wrong entry size causes missed or repeated completions. `ehea_get_swqe()` computes indices from queue offset and SG encoding, so it must match `sq_skba` sizing. WR_ID field packing must remain consistent across TX post, RX refill, and completion processing. Error masks decide whether RX/TX errors trigger port resets.

Test signals: Queue wrap at ring boundaries, valid-bit toggle transitions, SWQE2/SWQE3 completion handling, RX RQ2/RQ3 skb-index recovery, refill credit accounting, fatal CQE reset paths, and compile-time section-size assertion on target configs.
