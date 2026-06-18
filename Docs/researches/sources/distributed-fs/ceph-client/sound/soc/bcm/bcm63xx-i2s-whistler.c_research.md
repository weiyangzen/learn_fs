# sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s-whistler.c

## Purpose
Broadcom BCM63XX Whistler I2S CPU DAI. It configures separate TX/RX I2S blocks, coordinates which side generates the shared bus clock, sets sample clock rate, and delegates PCM/DMA registration to the companion BCM63XX PCM implementation.

## Important APIs, Types, And Functions
- Regmap callbacks `brcm_i2s_wr_reg`, `brcm_i2s_rd_reg`, and `brcm_i2s_volatile_reg` constrain register access.
- `bcm63xx_i2s_hw_params()` sets `i2sclk` to the requested sample rate.
- `bcm63xx_i2s_startup()` enables TX or RX data/clock bits, initializes IRQ thresholds, and chooses master/slave mode based on the opposite block.
- `bcm63xx_i2s_shutdown()` disables direction bits, restores IRQ thresholds, and hands master mode back to the other active block if needed.
- Probe maps registers, initializes regmap, disables pad loopback, registers the DAI, stores private state, and calls `bcm63xx_soc_platform_probe`.

## Control Flow
Probe allocates `bcm_i2s_priv`, gets `i2sclk`, maps MMIO, sets up regmap, disables pad loop loopback, registers the DAI, stores state, and registers the PCM platform. Startup is direction-specific: playback enables TX output/data/clock and chooses TX master only if RX is currently slave; capture mirrors the logic for RX. Shutdown disables the direction and may promote the other still-enabled direction to master before putting the stopped side back to slave.

## State And Persistence
State is in `bcm_i2s_priv` plus hardware registers. The header also reserves fields for substreams and DMA descriptors used by the companion PCM file. No persistence beyond device lifetime.

## Dependencies And Integration Points
Depends on regmap, clk, ASoC, `bcm63xx-i2s.h`, and companion functions `bcm63xx_soc_platform_probe/remove` linked from the BCM63XX PCM object. Compatible string is `brcm,bcm63xx-i2s`.

## Risks
`hw_params` sets the clock to the sample rate rather than an obvious bit-clock multiple; this may rely on clock-provider internals and should be checked on hardware. Master/slave arbitration is register-state based and sensitive to simultaneous stream startup/shutdown races. Only S32_LE stereo is advertised. Regmap write ranges include descriptor registers that the PCM side may also manipulate.

## Test Signals
Playback-only, capture-only, and full-duplex stream start/stop ordering; clock rate programming; master/slave handoff when one direction stops; pad loopback disable; and integration with companion PCM descriptor handling.
