# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_fdma.c

## Purpose
This file implements the common Sparx5 FDMA extraction and injection path for non-LAN969x operation. It allocates descriptor/buffer memory, configures FDMA hardware channels, handles FDMA interrupts, performs NAPI RX processing, injects TX frames with IFH, and starts/stops FDMA.

## Important APIs, Types, And Functions
Exports include `sparx5_fdma_init()`, `sparx5_fdma_deinit()`, `sparx5_fdma_start()`, `sparx5_fdma_stop()`, `sparx5_fdma_handler()`, `sparx5_fdma_reload()`, `sparx5_fdma_injection_mode()`, `sparx5_fdma_napi_callback()`, and `sparx5_fdma_xmit()`. Internal helpers provide dataptr callbacks, channel activation/deactivation, RX frame processing, and RX/TX allocation.

## Control Flow
Initialization resets FDMA, configures CPU ACP caching, programs QS extraction/injection mode and CPU port behavior, initializes RX/TX FDMA structures, and allocates physical FDMA memory. Start adds and enables NAPI using the family `fdma_poll` op, activates RX/TX channels, and enables interrupts. The IRQ handler masks DB interrupts, clears interrupt status, schedules NAPI, and logs/clears FDMA errors. NAPI consumes completed RX descriptors, parses IFH, maps source port to netdev, trims FCS, timestamps PTP, updates stats, sends skbs up the stack, replenishes descriptors, reloads FDMA, and re-enables interrupts. TX copies IFH and skb data into the next descriptor buffer and reloads FDMA.

## State And Persistence
State lives in `sparx5->rx.fdma`, `sparx5->tx.fdma`, RX skb arrays, descriptor indices, physical/coherent FDMA buffers, NAPI state, netdev stats, and FDMA/QS/ASM/QFWD/DSM/HSCH hardware registers. Nothing persists beyond runtime hardware state.

## Dependencies And Integration Points
The file depends on common FDMA helpers, Sparx5 register accessors, IFH parsing, PTP RX timestamping, netdev/NAPI/IRQ APIs, DMA/physical allocation helpers, CPU internal port mapping, and family ops for NAPI poll selection.

## Risks And Edge Cases
RX dataptr uses `virt_to_phys()` on skb data, which relies on platform DMA assumptions compared with DMA mapping APIs. `sparx5_fdma_init()` does not free RX allocation if TX allocation fails. `sparx5_fdma_xmit()` advances the DCB before checking descriptor done and can return `-EINVAL` under descriptor pressure. RX inactive-port data flushes the extraction queue and returns false, potentially ending the poll early. The stop wait condition checks buffer-empty semantics and should be validated against hardware docs.

## Test Signals
Test FDMA start/stop during interface open/close, RX and TX traffic, inactive source-port handling, bridge offload marks, PTP RX timestamps, FDMA error interrupts, descriptor pressure, unload cleanup, and fallback to LAN969x-specific FDMA ops when selected.
