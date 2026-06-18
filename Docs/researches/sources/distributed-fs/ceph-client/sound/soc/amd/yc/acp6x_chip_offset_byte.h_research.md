# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x_chip_offset_byte.h

## Purpose
This header is the ACP 6.x Yellow Carp register-offset map. It expands the ACP 5.x-style map with ACP6x-specific P1 misc/audio-buffer ranges and WOV PDM registers used by the PDM DMA driver.

## Important APIs, Types, And Functions
Its exported surface is symbolic `#define` offsets: DMA channel registers, ATU groups 1-16, clock/reset and power-gating registers, AON pin/wake registers, P1 interrupt/error/position registers, classic audio buffers, I2S/Bluetooth/headset TDM registers, WOV PDM registers (`ACP_WOV_PDM_ENABLE`, `ACP_WOV_RX_RINGBUFSIZE`, `ACP_WOV_CLK_CTRL`), P1 audio buffers, and scratch registers.

## Control Flow
None. The include guard `_acp6x_OFFSET_HEADER` prevents duplicate definitions.

## State And Persistence
The file identifies volatile MMIO state. WOV registers hold active PDM DMA enablement, ring-buffer configuration, linear position counters, FIFO flush state, channel count, decimation, clock/gain controls, and error status.

## Dependencies And Integration Points
It is included by `acp6x.h` and indirectly used by both the PCI and PDM DMA drivers. Integration correctness depends on the ACP6x physical register window matching `ACP6x_REG_START`/`ACP6x_REG_END` and the subtract-base helper in `acp6x.h`.

## Risks And Test Signals
Wrong offsets can cause hard-to-debug audio or interrupt failures. Test signals include successful ACP reset/power transitions, correct PDM DMA period interrupts, stable capture position counters, and no writes outside the mapped ACP resource.
