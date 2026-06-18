
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.c

## Purpose

This file initializes HIBMCGE MSI/MSI-X interrupts, defines IRQ metadata, dispatches TX/RX/error handlers, tracks per-IRQ counters, and schedules recovery work for reset-worthy errors.

## Important APIs, Types, and Functions

- `hbg_irqs[]` maps interrupt names to masks, re-enable behavior, logging, reset requirement, and handler function.
- `hbg_irq_handle()` is the shared IRQ handler for requested vectors.
- `hbg_irq_handle_tx()` and `hbg_irq_handle_rx()` schedule the TX and RX NAPI instances.
- `hbg_irq_handle_err()` logs configured errors and schedules reset when needed.
- `hbg_irq_init()` allocates four PCI vectors, requests three IRQs (`tx`, `rx`, `err`), and allocates stats storage.

## Control Flow

Initialization allocates exactly `HBG_VECTOR_NUM` vectors but intentionally does not request the MDIO vector. The shared handler reads combined hardware status, walks all metadata entries, skips disabled interrupts, disables and clears the current interrupt, increments its counter, invokes the handler, and reenables only entries marked `re_enable`.

## State and Persistence

IRQ metadata is static. Per-device IRQ names, metadata pointers, metadata length, and counters live in `priv->vectors`. Hardware interrupt mask registers persist until changed. Error handlers set service-task state bits for reset.

## Dependencies and Integration Points

The file depends on PCI MSI/MSI-X allocation, devm IRQ requests, hardware IRQ helpers, NAPI in `hbg_ring`, and reset scheduling in `hbg_common.h`. It feeds debugfs and diagnostics through `priv->vectors`.

## Risks and Edge Cases

The driver requires exactly four allocated vectors; systems that can allocate fewer fail probe. All requested vectors use the same handler and scan all interrupt status bits, so hardware vector routing must match expectations. Error interrupts that are not `re_enable` remain disabled after one occurrence unless reset/rebuild reenables them. RX buffer-available immediately reenables itself and increments a software counter.

## Test Signals

Signals include successful allocation of four vectors, requested `tx`, `rx`, and `err` IRQ names, TX/RX NAPI scheduling on interrupts, error logging and reset scheduling for configured bits, accurate debugfs/diagnostic IRQ counters, and clean operation with the unused MDIO vector.
