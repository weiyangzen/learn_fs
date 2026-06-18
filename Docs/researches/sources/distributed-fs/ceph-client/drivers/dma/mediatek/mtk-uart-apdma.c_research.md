<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-uart-apdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-uart-apdma.c

## Purpose
DMAEngine slave driver for MediaTek UART APDMA virtual FIFO channels. It supports one-scatterlist UART TX or RX transfers for the MediaTek 8250 UART driver.

## Important APIs, Types, And Functions
`struct mtk_uart_apdmadev` owns the DMA device, clock, address-width capability, and channel count. `struct mtk_chan` holds a virt-dma channel, slave config, active descriptor, direction, MMIO base, IRQ, and RX residue. `mtk_uart_apdma_start_tx` and `mtk_uart_apdma_start_rx` program VFF ring registers. `mtk_uart_apdma_irq_handler` dispatches TX/RX completion handlers and calls `vchan_cookie_complete`. DMAEngine hooks include resource allocation/free, `prep_slave_sg`, `slave_config`, `issue_pending`, `pause`, `terminate_all`, and `tx_status`. Runtime/system PM callbacks gate the APDMA clock.

## Control Flow
Probe gets the clock, derives DMA mask width from compatible data, creates one channel per `dma-requests` resource, maps each channel base, records IRQs, enables runtime PM, registers DMAEngine, and registers OF DMA xlate by channel id. Allocating a channel resumes the device, clears VFF registers, warm-resets the FIFO, requests the channel IRQ, clears high address state if supported, then drops the runtime PM reference without fully suspending. A slave SG prep accepts exactly one SG entry and stores address/length/direction. Issue-pending starts TX or RX if no descriptor is active. TX initializes the VFF address/length/threshold, advances WPT by available length, enables interrupts, and kicks flush when needed. RX configures the VFF receive ring and enables interrupts. IRQ clears/halts the relevant direction, computes RX residual bytes from read/write pointers, completes the descriptor, and clears `c->desc`. Terminate flushes, stops, clears IRQ state, synchronizes IRQ, and frees all descriptors.

## State And Persistence
State includes per-channel VFF registers, the active descriptor pointer, saved slave config, direction, RX status/residue, runtime PM clock state, and virt-dma lists. No persistent storage exists.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, OF DMA, MediaTek 8250 UART clients, clocks, runtime PM, platform resources, and compatible data indicating 32- to 35-bit DMA addressing. It advertises one-byte slave bus widths, device-to-memory and memory-to-device directions, and segment residue granularity.

## Risks And Edge Cases
`tx_status` always reports `c->rx_status`, which is meaningful for RX but questionable for TX. `alloc_chan_resources` calls `pm_runtime_resume_and_get` and then `pm_runtime_put_noidle`, while `free_chan_resources` calls `pm_runtime_put_sync`, so runtime PM reference symmetry deserves scrutiny. The driver supports only `sglen == 1`; callers expecting multi-SG UART DMA are rejected. RX residue depends on wrap-bit pointer math and the configured port window size. Stop/flush polling failures are logged but termination still frees descriptors.

## Test Signals
Test with the MediaTek 8250 UART driver for TX and RX DMA, especially ring wrap, high DMA addresses on compatibles with `support_ext_addr`, pause/terminate during active UART I/O, runtime suspend/resume, and tx_status residue for RX. Missing or mismatched per-channel resources should fail probe cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-uart-apdma.c -->
