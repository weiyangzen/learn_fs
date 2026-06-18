# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_dqo.h

## Purpose

`gve_dqo.h` is the DQO datapath interface header. It declares the DQO TX/RX entry points used by `gve_main.c`, exposes DQO interrupt coalescing helpers, and defines DQO-specific timing constants.

## Important APIs, types, and constants

- Interrupt constants: `GVE_ITR_ENABLE_BIT_DQO`, `GVE_ITR_CLEAR_PBA_BIT_DQO`, `GVE_ITR_NO_UPDATE_DQO`, `GVE_ITR_INTERVAL_DQO_SHIFT`, and `GVE_ITR_INTERVAL_DQO_MASK`.
- Defaults: `GVE_TX_IRQ_RATELIMIT_US_DQO`, `GVE_RX_IRQ_RATELIMIT_US_DQO`, `GVE_MAX_ITR_INTERVAL_DQO`.
- Completion timeout constants for DQO TX miss/reinjection and delayed deallocation: `GVE_REINJECT_COMPL_TIMEOUT`, `GVE_DEALLOCATE_COMPL_TIMEOUT`.
- DQO TX API: `gve_tx_dqo`, `gve_features_check_dqo`, `gve_tx_poll_dqo`, `gve_xdp_poll_dqo`, `gve_xsk_tx_poll_dqo`, ring alloc/free/start/stop, completion cleaner, and XDP TX flush.
- DQO RX API: `gve_rx_poll_dqo`, ring alloc/free/start/stop, `gve_rx_post_buffers_dqo`, `gve_rx_write_doorbell_dqo`, and XDP metadata timestamp hook.
- Inline MMIO helpers: `gve_tx_put_doorbell_dqo`, `gve_setup_itr_interval_dqo`, `gve_write_irq_doorbell_dqo`, and `gve_set_itr_coalesce_usecs_dqo`.

## Control flow and state

The header has no owned state. It encodes DQO interrupt throttle values by converting microseconds to the hardware two-microsecond granularity and writing BAR2 doorbells using admin-provided doorbell indexes. `gve_main.c` selects these APIs whenever the queue format is not GQI.

## Dependencies and integration points

It depends on `gve_adminq.h` and the common ring/private structures from `gve.h` through includers. `gve_ethtool.c` uses `GVE_MAX_ITR_INTERVAL_DQO` and `gve_set_itr_coalesce_usecs_dqo()` for coalescing. `gve_main.c` uses DQO poll functions for NAPI and DQO alloc/start/stop paths for queue lifecycle.

## Risks and test signals

Risks are incorrect BAR2 index conversion, ITR interval truncation/masking, unsupported coalescing values, and inconsistent DQO API behavior relative to GQI. Tests should check ethtool coalesce bounds, interrupt re-enable behavior after NAPI completion, DQO queue start/stop paths, and TX/RX doorbell updates under wraparound.
