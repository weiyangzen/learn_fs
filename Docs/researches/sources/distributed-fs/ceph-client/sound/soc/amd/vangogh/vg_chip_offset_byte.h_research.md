# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/vg_chip_offset_byte.h

## Purpose
This header is a register-offset catalog for AMD ACP 5.x Vangogh audio hardware. It has no executable code; it gives symbolic byte offsets for ACP DMA channels, AXI-to-AXI ATU page tables, clock/reset, miscellaneous interrupt/error registers, power-gating/AON controls, scratch SRAM/PTE storage, audio ring buffers, I2S/TDM, Bluetooth TDM, and headset TDM blocks.

## Important APIs, Types, And Functions
The public surface is the set of `#define` register names such as `ACP_DMA_CNTL_0`, `ACP_SOFT_RESET`, `ACP_EXTERNAL_INTR_CNTL`, `ACP_SCRATCH_REG_0`, `ACP_I2S_RX_RINGBUFADDR`, and `ACP_I2STDM_IER`. Consumers include MMIO helpers in AMD ACP drivers that add these offsets to an ACP base address. There are no structs, functions, module hooks, or inline helpers here.

## Control Flow
None. The include guard `_acp_ip_OFFSET_HEADER` prevents duplicate inclusion.

## State And Persistence
The file describes volatile hardware state only. Persistence is external in ACP registers, DMA descriptors, scratch/PTE SRAM, interrupt status bits, and ring-buffer position counters.

## Dependencies And Integration Points
It integrates with AMD SoC audio drivers that need ACP 5.x register offsets. Its naming closely mirrors `acp6x_chip_offset_byte.h` but lacks newer ACP6x WOV/P1 ranges. Correctness depends on the register map matching the SoC generation and the driver's base-address arithmetic.

## Risks And Test Signals
The main risk is silent hardware misprogramming from stale or wrong offsets. Test signals are boot/probe success on Vangogh ACP hardware, working I2S/TDM DMA, sane ring-buffer counters, and absence of ACP interrupt/error-status storms.
