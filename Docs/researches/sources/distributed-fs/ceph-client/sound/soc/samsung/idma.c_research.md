# sources/distributed-fs/ceph-client/sound/soc/samsung/idma.c

## Purpose
Implements the Samsung I2S0 internal DMA PCM component for low-power audio memory playback, used with I2S variants that support IDMA.

## Important APIs, Types, And Functions
- `struct idma_ctrl` stores per-substream state, ring addresses, period size/count, callback, and token.
- Static `idma` holds global register base and LP audio memory transmit address.
- `idma_reg_addr_init()` initializes the global MMIO base and low-power TX address; exported for `i2s.c`.
- `idma_hw_params()`, `idma_prepare()`, `idma_trigger()`, `idma_pointer()`, `idma_mmap()`, `idma_open()`, and `idma_close()` implement PCM component callbacks.
- `iis_irq()` handles I2S AHB level interrupts, advances the level interrupt address around the ring, and calls the period callback.

## Control Flow
The platform driver obtains an IRQ and registers an ASoC component. On PCM open it allocates `idma_ctrl` and requests the shared I2S IRQ. `hw_params` enables IDMA mode in `I2SMOD`, configures AHB reload/mask, sets runtime DMA buffer metadata, and stores ring boundaries. `prepare` stops DMA and enqueues initial start/level/size registers. Trigger start/stop toggles `ST_RUNNING` and AHB DMA enable. IRQ clears level interrupt, advances the next interrupt address modulo the buffer, and calls `snd_pcm_period_elapsed()` through `idma_done()`. `pcm_new` maps the fixed low-power memory region as a continuous DMA buffer.

## State And Persistence
Global static state stores the IDMA register base, low-power TX physical address, and IRQ number. Per-open state is allocated in `runtime->private_data`. DMA ring position is hardware-derived from `I2STRNCNT`. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S register definitions, ASoC PCM component callbacks, IRQ APIs, DMA mask APIs, and `idma.h`. `i2s.c` calls `idma_reg_addr_init()` when the hardware supports IDMA and passes the secondary DAI's `idma_playback.addr`.

## Risks And Edge Cases
- Static global IDMA state prevents clean multi-controller support.
- `idma_close()` calls `free_irq(idma_irq, prtd)` before checking `prtd`, so a corrupt NULL private_data would be unsafe.
- The buffer is mapped with `ioremap()` from a fixed physical address; platform memory reservation must be correct.
- Only playback is handled.
- Period callback receives `prtd->period` rather than byte count naming, but callback ignores bytes except for signature.

## Test Signals
IDMA playback on supported I2S0 hardware, mmap playback, period interrupt cadence, pointer progression and wraparound, trigger pause/resume, and open/close IRQ lifecycle tests.
