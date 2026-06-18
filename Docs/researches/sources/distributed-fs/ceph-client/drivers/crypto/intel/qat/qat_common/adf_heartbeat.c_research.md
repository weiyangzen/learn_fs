# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.c

Purpose: implements QAT heartbeat health monitoring. It allocates DMA memory for firmware heartbeat counters, configures firmware heartbeat timer ticks, compares live and previous counters, tracks failures, and triggers fatal-error notification when firmware appears unresponsive.

Important APIs: `adf_heartbeat_init`, `adf_heartbeat_start`, `adf_heartbeat_shutdown`, `adf_heartbeat_status`, `adf_heartbeat_check_ctrs`, `adf_heartbeat_ms_to_ticks`, and `adf_heartbeat_save_cfg_param`. Key helpers include `check_ae`, `adf_hb_get_status`, `get_timer_ticks`, and `adf_heartbeat_reset`.

Control flow and state: init allocates `struct adf_heartbeat` plus one page of coherent DMA. Start validates platform-specific counter count, computes timer ticks from config/defaults, and sends admin timer setup. Status reads are rate-limited by `hb_timer`, increment sent/failed counters, compare each active AE/thread, and throttle fatal reset notification to `ADF_CFG_HB_RESET_MS`.

Dependencies and integration: uses admin commands, config keys, device clock callbacks, AE masks, optional `adf_timer`, and `adf_notify_fatal_error`. Debugfs reads invoke status checks.

Risks and test signals: DMA layout assumes enough page space for live/last/failure arrays; too-frequent polling returns unsupported; counter-count adaptation mutates `hw_device->num_hb_ctrs`. Test normal alive reads, stalled-counter threshold, minimum timer validation, restart handling, and fatal-error reset notification.
