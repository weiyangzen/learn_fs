## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.c

Purpose: Implements core Gen4 hardware operations: BAR selection, counts, admin/arbiter offsets, heartbeat clock, PM power-up, error/interrupt setup, ring-pair reset/drain/quiesce, firmware-thread-to-arbiter mapping, ring-to-service mapping, compression request template construction, and rate-limiting slice helpers.

Important APIs/functions: Exported helpers include `adf_gen4_init_device()`, `adf_gen4_enable_ints()`, `adf_gen4_ring_pair_reset()`, `adf_gen4_init_thd2arb_map()`, `adf_gen4_get_ring_to_svc_map()`, `adf_gen4_bank_quiesce_coal_timer()`, `adf_gen4_bank_drain_start()/finish()`, `adf_gen4_services_supported()`, `adf_gen4_init_dc_ops()`, `adf_gen4_init_num_svc_aes()`, and `adf_gen4_get_svc_slice_cnt()`.

Control flow and state: `adf_gen4_init_device()` masks PM interrupt, asserts `DRV_ACTIVE`, and polls `PM_STATUS` for `INIT_STATE`. Ring reset/drain writes WQM reset control and polls reset status. Thread-to-arbiter mapping is computed from loaded firmware object AE masks, thread masks, ring-pair groups, and service mode, then stored in `hw_data->thd_to_arb_map`. Ring-to-service mapping is derived from firmware object type per RP group. Compression template ops fill firmware header command ids and hardware config words for DEFLATE and LZ4S.

Dependencies/integration: Depends on Gen4 hardware constants, PM constants, firmware config introspection callbacks, config service ids, compression firmware structs, CSR ops, and rate-limiting data. It is central to Gen4 product driver hardware setup.

Risks and test signals: Important risks are PM power-up timeout, invalid firmware object callbacks, DCC map special casing, unsupported service combinations, and ring drain/reset timeouts. Tests should cover service-mask validation, DCC versus mixed-service arb maps, ring-pair reset timeout, coalesced timer quiesce math, DEFLATE/LZ4S template generation, and slice-count reporting.
