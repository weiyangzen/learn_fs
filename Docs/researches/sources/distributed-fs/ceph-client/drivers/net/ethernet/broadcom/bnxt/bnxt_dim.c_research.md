# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dim.c

Purpose: Applies Linux net DIM workqueue decisions to bnxt RX interrupt coalescing. It is the small bridge from generic DIM profile selection to the driver's HWRM ring coalescing command.

Important APIs, types, and functions: The only function is `bnxt_dim_work(struct work_struct *work)`. It derives `struct dim`, containing `bnxt_cp_ring_info`, containing `bnxt_napi`, then calls `net_dim_get_rx_moderation()` and `bnxt_hwrm_set_ring_coal()`.

Control flow: When DIM schedules work, this function obtains the current RX moderation profile for `dim->mode` and `dim->profile_ix`, writes the selected usec and packet thresholds into `cpr->rx_ring_coal`, sends the updated coalescing configuration to firmware for that NAPI/ring, and resets DIM state to `DIM_START_MEASURE`.

State and persistence behavior: It mutates per-completion-ring runtime coalescing fields (`coal_ticks`, `coal_bufs`) and DIM state. Firmware receives the new ring coalescing values through HWRM, but no persistent NVM setting is changed.

Dependencies and integration points: It depends on `<linux/dim.h>`, `struct bnxt_cp_ring_info` and `struct bnxt_napi` from `bnxt.h`, and the HWRM coalescing function implemented elsewhere. Debugfs reads the same `struct dim` state exposed by this work item.

Risks: The nested `container_of()` chain assumes `dim` is embedded in `bnxt_cp_ring_info`, which is embedded as `bnxt_napi.cp_ring`; this helper is not valid for non-primary completion rings unless the layout matches. HWRM failures are not checked here, so failed coalescing updates may silently leave firmware using old values while DIM restarts measurement.

Test signals: Enable DIM, generate RX traffic with varying packet rates, observe profile changes through debugfs, verify HWRM coalescing commands are issued per RX ring, and inject `bnxt_hwrm_set_ring_coal()` failures to confirm the driver remains stable.
