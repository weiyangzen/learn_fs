# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-scd.h

Purpose: Provides inline helpers for programming legacy TX scheduler queue chaining, aggregation selection, FIFO activation, active control, and queue pointer/status register addresses.

Important APIs and functions: `iwl_scd_txq_set_chain()`, `iwl_scd_txq_enable_agg()`, `iwl_scd_txq_disable_agg()`, `iwl_scd_disable_agg()`, `iwl_scd_activate_fifos()`, `iwl_scd_deactivate_fifos()`, `iwl_scd_enable_set_active()`, `SCD_QUEUE_WRPTR()`, `SCD_QUEUE_RDPTR()`, `SCD_QUEUE_STATUS_BITS()`, and `iwl_scd_txq_set_inactive()`.

Control flow: Helpers directly write or update PRPH scheduler registers. Queue address functions select lower register rows for queues below 20 and upper rows for queues 20-31 with warnings for unsupported queue ids.

State and persistence: Mutates scheduler PRPH state controlling queue activity, aggregation, FIFO enablement, and queue status. No durable storage exists.

Dependencies and integration points: Includes transport, IO, and PRPH definitions. Used by PCIe TX queue setup/teardown and aggregation control paths.

Risks: Queue id range and offset math are hardware ABI. `iwl_scd_disable_agg()` calls `iwl_set_bits_prph()` with zero mask, which appears to leave aggregation bits unchanged; behavior should be verified against callers. Active/inactive writes must align with firmware queue ownership.

Test signals: Queue enable/disable on queues below and above 20, aggregation start/stop, FIFO activation around firmware start/stop, warning coverage for invalid queue ids, and register readback after `iwl_scd_disable_agg()`.
