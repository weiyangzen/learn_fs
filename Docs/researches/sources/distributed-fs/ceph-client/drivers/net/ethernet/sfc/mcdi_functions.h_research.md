# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.h

## Purpose
`mcdi_functions.h` declares the MCDI-backed resource lifecycle functions for VI allocation, event queues, TX/RX queues, DMA queue finalization, VI window stride derivation, and PF index lookup.

## Important APIs
The header declares `efx_mcdi_alloc_vis()`, `efx_mcdi_free_vis()`, event queue `probe/init/remove/fini`, TX queue `init/remove/fini`, RX queue `probe/init/remove/fini`, `efx_fini_dmaq()`, `efx_mcdi_window_mode_to_stride()`, and `efx_get_pf_index()`.

## Control Flow Role
It lets NIC type code and probe/reset paths bind resource operations to the MCDI implementation. The naming split is meaningful: `probe/remove` manage host DMA memory, while `init/fini` manage firmware queue state. Callers must order these phases so firmware never references freed DMA memory.

## State And Persistence Behavior
The declarations affect runtime firmware allocations and host DMA buffers through their implementation. No header state persists. Implementation updates include `efx->vi_stride`, queue descriptor state, TSO mode, active queue counters, and firmware resources.

## Dependencies And Integration Points
Includers need SFC driver types such as `struct efx_nic`, `struct efx_channel`, `struct efx_tx_queue`, and `struct efx_rx_queue`. The API integrates with the MCDI core, queue/channel management, reset recovery, and function capability discovery.

## Risks And Edge Cases
Some operations return `int`, while RX init is `void` even though it can log firmware failure. `efx_fini_dmaq()` returns errors and must be checked. New callers must respect probe/init/fini/remove ordering and recovery-mode exceptions.

## Test Signals
Compile NIC operation tables against these prototypes. Runtime tests should cover allocation/free idempotence, queue init/fini ordering, reset-time DMAQ finalization, and PF index query on PF/VF configurations.
