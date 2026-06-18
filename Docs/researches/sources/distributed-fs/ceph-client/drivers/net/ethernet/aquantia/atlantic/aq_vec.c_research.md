<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.c

Purpose: implements per-interrupt-vector/NAPI aggregation for one TX/RX ring pair per active traffic class.

Important APIs/functions: `aq_vec_alloc`, `aq_vec_ring_alloc`, `aq_vec_init`, `aq_vec_start`, `aq_vec_stop`, `aq_vec_deinit`, `aq_vec_free`, `aq_vec_ring_free`, `aq_vec_isr`, `aq_vec_isr_legacy`, `aq_vec_get_affinity_mask`, `aq_vec_is_valid_tc`, and `aq_vec_get_sw_stats`. Internal `aq_vec_poll` is the NAPI poll routine.

Control flow: allocation creates the vector object and registers NAPI. Ring allocation creates TX/RX rings for each TC and registers RX XDP queue metadata. Init calls generic ring init, hardware ring init, RX fill, and hardware RX tail programming. Start enables hardware rings then NAPI. ISR schedules NAPI; legacy ISR reads/disables IRQ status before scheduling. Poll updates TX heads, cleans TX, receives RX heads, cleans RX, refills RX, updates hardware tails, and reenables the vector interrupt after NAPI completion.

State and persistence: `struct aq_vec_s` stores ops, hardware pointer, NIC pointer, ring counts, ring param/affinity, NAPI object, and a fixed `[AQ_CFG_TCS_MAX][2]` ring array. Runtime only.

Dependencies and integration: bridges `aq_nic`, `aq_ring`, hardware ops, Linux NAPI, IRQ affinity, and XDP RXQ registration.

Risks: TX and RX ring counts must remain aligned per TC; NAPI completion must only reenable IRQs when below budget; legacy INTx masking differs from MSI-X; XDP RXQ unregister must match allocation failures. Test signals include MSI-X and INTx interrupt modes, multitraffic-class polling, NAPI budget exhaustion, queue stats, and XDP-enabled ring allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.c -->
