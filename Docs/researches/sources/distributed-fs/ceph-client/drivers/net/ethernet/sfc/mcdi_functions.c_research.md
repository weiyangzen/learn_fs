# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.c

## Purpose
`mcdi_functions.c` adapts MCDI commands for hardware resource lifecycle: VI allocation, event queue initialization/finalization, TX/RX queue initialization/finalization, DMA queue draining, VI window stride selection, and PF index lookup.

## Important APIs And Functions
`efx_mcdi_alloc_vis()` and `efx_mcdi_free_vis()` manage firmware VI allocation. `efx_mcdi_ev_probe/init/fini/remove()` allocate host event queue DMA memory and configure/free firmware EVQs. `efx_mcdi_tx_init/fini/remove()` configure/free firmware TXQs and host TX descriptor buffers. `efx_mcdi_rx_probe/init/fini/remove()` do the same for RX queues. `efx_fini_dmaq()` finalizes queues and waits for firmware flush completion. `efx_mcdi_window_mode_to_stride()` maps firmware VI window mode to byte stride, and `efx_get_pf_index()` reads `GET_FUNCTION_INFO`.

## Control Flow
Bring-up allocates VIs, allocates DMA buffers, initializes event queues, then initializes TX/RX queues with per-page DMA addresses. Event queue init fills the event ring with empty events and selects v1 or v2 event queue flags. TX init programs queue size, target EVQ, label, instance, owner, vport, descriptor pages, checksum flags, timestamping, and TSOv2. If TSOv2 resources are exhausted, it disables TSOv2 and retries. RX init programs queue size, target EVQ, labels, prefix/timestamp flags, vport, optional EF100 buffer size, and descriptor pages.

Teardown separates firmware `FINI_*` from host DMA free. `efx_fini_dmaq()` skips writes during EEH recovery, zeros `active_queues` after MC reboot requiring VI reallocation, otherwise finalizes every RX/TX queue and waits for active queue drain events.

## State And Persistence Behavior
Firmware VI/EVQ/TXQ/RXQ resources are runtime allocations and are lost on reset. Host DMA buffers are stored in queue/channel objects until removed. `tx_queue->tso_version` may be downgraded if TSOv2 context allocation fails. `efx->vi_stride` is set from firmware capability state, and `efx->active_queues` is used as the teardown drain counter.

## Dependencies And Integration Points
The file depends on `net_driver.h`, `efx.h`, `nic.h`, `mcdi_functions.h`, `mcdi.h`, `mcdi_pcol.h`, queue/channel iteration helpers, `efx_nic_alloc_buffer()`, `efx_nic_free_buffer()`, and core MCDI RPC functions. It integrates with probe, reset, datapath queue setup, interrupt/event queue setup, TSO/checksum offload, timestamping, EF100 RX buffering, and MCDI flush events.

## Risks And Edge Cases
Queue init is sensitive to DMA address arrays and variable MCDI input lengths; mismatches can make firmware access invalid memory. TSOv2 fallback changes datapath performance and offload semantics. `efx_fini_dmaq()` depends on correct flush event accounting; missing events lead to timeout. RX init logs failure but has no return code, so callers must tolerate that design.

## Test Signals
Exercise normal probe/remove, reset, MC reboot, and EEH recovery; TSOv2 success and `-ENOSPC` fallback; timestamping queues; EF100 buffer sizing; multiple queue sizes; and missing flush events. Logs to watch include `INIT_*`/`FINI_*` failures, TSOv2 fallback, unrecognized VI window mode, and failed queue flush counts.
