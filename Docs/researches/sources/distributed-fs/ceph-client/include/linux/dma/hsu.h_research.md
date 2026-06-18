<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/hsu.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/hsu.h

## Purpose
Declares the Intel High Speed UART DMA platform interface.

## Important APIs, Types, And Functions
`struct hsu_dma_chip` carries device, IRQ, MMIO base, register length, register offset, and core private pointer. APIs are `hsu_dma_get_status()`, `hsu_dma_do_irq()`, `hsu_dma_probe()`, and `hsu_dma_remove()`, with no-op or disabled stubs when `CONFIG_HSU_DMA` is off.

## Control Flow
Platform glue fills the chip descriptor, calls probe, forwards hardware interrupt status through `hsu_dma_do_irq()`, and can query per-channel status. Remove tears down DMAengine state.

## State And Persistence
Runtime state is the chip descriptor, MMIO range, channel status, and core private `struct hsu_dma`. No persistence exists.

## Dependencies And Integration Points
Depends on platform data, device/MMIO infrastructure, IRQ handling, and DMAengine core.

## Risks And Edge Cases
Status helper stubs return success when disabled, so callers must not assume real hardware handling unless probe succeeded. Register offset/length mistakes can read wrong status bits. IRQ forwarding must match channel numbers.

## Test Signals
Tests should cover build stubs, probe/remove, status query for valid and invalid channels, IRQ dispatch, register offset handling, and teardown with pending transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/hsu.h -->
