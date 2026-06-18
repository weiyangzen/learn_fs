# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-pdc.c

## Purpose
This file implements the legacy Atmel PDC-backed PCM component for SSC audio. It manually programs PDC current and next pointer/count registers, manages period rotation, reports period elapsed from SSC interrupts, and exposes PCM operations for open/close/hw_params/hw_free/prepare/trigger/pointer.

## Important APIs, Types, And Functions
The exported API is `atmel_pcm_pdc_platform_register(struct device *dev)`. State is `struct atmel_runtime_data`. Important callbacks are `atmel_pcm_new()`, `atmel_pcm_hw_params()`, `atmel_pcm_hw_free()`, `atmel_pcm_prepare()`, `atmel_pcm_trigger()`, `atmel_pcm_pointer()`, `atmel_pcm_open()`, `atmel_pcm_close()`, and interrupt helper `atmel_pcm_dma_irq()`.

## Control Flow
Open installs hardware constraints and allocates runtime data. `hw_params` binds stream DMA params from the SSC DAI, records buffer bounds and period size, and sets the interrupt handler. Prepare disables PDC and SSC end interrupts. Trigger start loads current and next period registers, enables SSC end interrupts, then enables PDC. End-of-transfer interrupts advance and reload the next pointer; end-buffer interrupts recover by restarting the PDC. Pointer reads the current PDC pointer and converts it to frames.

## State And Persistence
Runtime state stores DMA buffer start/end, period size, next period pointer, and a pointer to shared SSC DMA params. Hardware state lives in SSC/PDC pointer, counter, PTCR, IER/IDR, and status registers.

## Dependencies And Integration Points
It depends on `atmel-pcm.h`, `linux/atmel_pdc.h`, `linux/atmel-ssc.h`, and `atmel_ssc_dai.c` to allocate SSC DMA params and fan out interrupts.

## Risks And Test Signals
Risk areas include manual circular-buffer bookkeeping, static warning counter in the interrupt helper, pointer races with hardware, and 32-bit DMA mask assumptions. Test signals are stable period interrupts, correct ALSA pointer wrap, xrun recovery on end-buffer events, and no stale handler after `hw_free`/close.
