# sources/distributed-fs/ceph-client/sound/soc/amd/acp/chip_offset_byte.h

## Purpose
`chip_offset_byte.h` defines ACP MMIO register offsets and address macros for ATU, power/reset, external interrupts, I2S/BT/HS DMA buffer registers, I2S/TDM control blocks, PDM/WOV registers, and master-clock generators.

## Important APIs, Types, and Functions
Important macros include `ACP_EXTERNAL_INTR_ENB()`, `ACP_EXTERNAL_INTR_CNTL()`, `ACP_EXTERNAL_INTR_STAT()`, `ACP_I2S_REG_ADDR()`, many `ACP_I2S_*`, `ACP_BT_*`, `ACP_HS_*`, `ACP_WOV_*` offsets, ATU group registers, `ACP_SOFT_RESET`, `ACP_CONTROL`, and TDM master clock registers.

## Control Flow
There is no function flow. Runtime code uses these macros to calculate register addresses from `chip->base`, resource offsets, interrupt-controller index, and generation-specific resource fields.

## State and Persistence
The header owns no state. It names hardware state accessed by ACP init/deinit, interrupt handlers, I2S/PDM trigger/prepare, DMA configuration, and pointer logic.

## Dependencies and Integration Points
It is included by `amd.h`, and therefore used throughout ACP common, platform, PDM, I2S, PCI, and SoC-specific code. Register offsets must align with ACP hardware documentation for each generation.

## Risks
Offset mistakes can corrupt unrelated ACP registers. Macros that depend on `rsrc->irqp_used`, `irq_reg_offset`, and `no_of_ctrls` are sensitive to resource-table correctness. HS offsets are direct constants while SP/BT use macros, so generation coverage differs.

## Test Signals
Hardware smoke tests for interrupt enable/status/clear, I2S SP/BT/HS playback/capture, PDM capture, ATU page programming, and suspend/resume register restoration are the primary validation signals.
