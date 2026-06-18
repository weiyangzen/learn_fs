# sources/distributed-fs/ceph-client/drivers/acpi/arm64/dma.c

## Purpose
Applies ARM64 ACPI DMA addressing limits and DMA range maps to devices.

## Important APIs, Types, And Functions
Defines `acpi_arch_dma_setup(struct device *dev)`.

## Control Flow
The helper ensures `dev->dma_mask` exists, picks a default limit from `coherent_dma_mask` or 32-bit fallback, skips devices with an existing range map, queries `_DMA` ranges through `acpi_dma_get_range()`, falls back to IORT limits when no ACPI range exists, then constrains `bus_dma_limit`, `coherent_dma_mask`, and `dma_mask`.

## State And Persistence
Mutates per-device DMA fields and may attach `dev->dma_range_map`.

## Dependencies And Integration Points
Depends on ACPI DMA range parsing, IORT DMA limits, dma-direct helpers, and generic device DMA masks.

## Risks
Missing initial `dma_mask` is tolerated with a warning. Incorrect firmware limits can unnecessarily constrain devices or allow unreachable DMA.

## Test Signals
Exercise devices with `_DMA` ranges, IORT fallback, no range information, preexisting range maps, zero coherent masks, and mask clamping boundaries.
