# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/stm32mp25_vpu_hw.c

## Purpose
Defines STM32MP25 Hantro decoder and encoder variants. The decoder exposes G1 VP8/H.264 decode, while the encoder exposes H1 JPEG encode with STM32-specific reset and IRQ handling.

## Important APIs, Types, And Functions
- Exports `stm32mp25_vdec_variant` and `stm32mp25_venc_variant`.
- Defines decoder and encoder format tables, `stm32mp25_vdec_codec_ops`, `stm32mp25_venc_codec_ops`, `stm32mp25_venc_irq()`, and `stm32mp25_venc_reset()`.
- Uses generic `hantro_g1_*` decoder operations and `hantro_h1_jpeg_enc_*` encoder operations.

## Control Flow
The decoder variant advertises NV12 output plus VP8 and H.264 coded formats up to FHD and dispatches to generic G1 run/reset/init/exit functions. The encoder variant advertises YUV input formats and JPEG output up to 4K, dispatches JPEG jobs to H1 helpers, resets with `reset_control_reset(vpu->resets)`, and marks job state from `H1_REG_INTERRUPT_FRAME_RDY`.

## State And Persistence
The file stores static variant data only. Runtime state lives in Hantro core, vb2 queues, and hardware registers. Reset changes transient hardware state but no durable storage.

## Dependencies And Integration Points
Depends on `hantro.h`, `hantro_jpeg.h`, `hantro_h1_regs.h`, reset-controller support through `vpu->resets`, and platform resources named `vdec-clk`, `venc-clk`, `vdec`, and `venc`.

## Risks And Edge Cases
The encoder IRQ clears only `H1_REG_INTERRUPT_BIT`, unlike some Rockchip handlers that clear broader state; error handling depends on the hardware status convention. Reset requires a valid reset control. Separate decoder/encoder variants must match platform compatible/resource wiring.

## Test Signals
Probe both VDEC and VENC instances, verify clock/reset/IRQ names, run VP8/H.264 decode and JPEG encode, force encoder error statuses, and confirm stream restart after reset.
