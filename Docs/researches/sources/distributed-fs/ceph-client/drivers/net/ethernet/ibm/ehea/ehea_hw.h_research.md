# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_hw.h

Purpose: Defines eHEA hardware register-map layouts for queue pairs, memory regions, queue-pair event data, completion queues, and event queues, plus low-level MMIO access helpers and queue/CQ doorbell helpers.

Important APIs and types: `struct ehea_qptemm`, `ehea_mrmwmm`, `ehea_qpedmm`, `ehea_cqtemm`, and `ehea_eqtemm` describe firmware-provided resource pages. Offset macros such as `QPTEMM_OFFSET()`, `MRMWMM_OFFSET()`, `QPEDMM_OFFSET()`, `CQTEMM_OFFSET()`, and `EQTEMM_OFFSET()` produce byte offsets for MMIO access. `epa_load()`, `epa_store()`, and `epa_store_acc()` wrap raw 64-bit MMIO reads/writes. `ehea_update_sqa()`, `ehea_update_rq1a()`, `ehea_update_rq2a()`, `ehea_update_rq3a()`, `ehea_update_feca()`, `ehea_reset_cq_n1()`, and `ehea_reset_cq_ep()` ring hardware queues or reset completion notification state.

Control flow: QMR allocation maps EPAs through PHYP. Runtime TX posts an SWQE then calls `ehea_update_sqa()`. RX refill paths post RWQEs and call the RQ adder helpers. NAPI completion calls CQ reset helpers to re-enable completion events. Completion processing calls `ehea_update_feca()` after consuming CQEs.

State and persistence: The structs represent hardware/firmware state in MMIO pages, not regular kernel-owned persistent state. The helper writes update producer/consumer accounting and event state inside eHEA resources. `epa_store()` does a readback to synchronize writes to eHEA; `epa_store_acc()` skips that synchronization for accumulator-style writes.

Dependencies and integration: Depends on `struct h_epa`, `struct ehea_qp`, and `struct ehea_cq` from `ehea.h`, and on raw Power I/O helpers. It is included by both PHYP and QMR code and is central to queue doorbell interaction.

Risks: Register layouts are fixed hardware ABI. Wrong offsets or bit masks can write the wrong MMIO location. The RQ helper names and masks must match hardware queue fields; subtle mismatches would show as lost RX refills. MMIO ordering is critical: `epa_store_acc()` assumes accumulator writes do not need readback, while `ehea_post_swqe()` separately issues `iosync()`.

Test signals: TX completion under load, RX refill on RQ1/RQ2/RQ3, NAPI completion rearming interrupts, CQ event pending behavior, and debug instrumentation confirming expected MMIO offsets against firmware documentation.
