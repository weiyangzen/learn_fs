# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1.c

## Purpose
Provides common G1 decoder interrupt and reset handling used by G1 codec backends.

## Important APIs, Types, And Functions
`hantro_g1_irq` reads `G1_REG_INTERRUPT`, classifies completion as `VB2_BUF_STATE_DONE` when `DEC_RDY_INT` is set and error otherwise, clears the interrupt register, gates the decoder clock, and calls `hantro_irq_done`. `hantro_g1_reset` disables decoder IRQs, gates the clock, and writes the soft-reset register.

## Control Flow And State
The file has no persistent state of its own. It operates on `struct hantro_dev` register state and delegates job state transitions to the core driver. Reset is intended for watchdog or backend recovery paths via `ctx->codec_ops->reset`.

## Dependencies And Integration Points
Depends on `hantro.h` for register access and driver types and on `hantro_g1_regs.h` for bit definitions. Variants bind this IRQ handler through `struct hantro_irq`.

## Risks And Test Signals
All non-ready interrupts are collapsed to buffer error; this is simple but loses hardware status detail. Test signals include successful IRQ completion, error IRQ completion, watchdog-triggered reset, and ensuring clock gate writes do not race with the core completion path.
