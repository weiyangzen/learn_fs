# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdiftx.c

## Purpose
Microchip S/PDIF transmitter CPU DAI. It provides mono/stereo playback, programs S/PDIF channel status and user data, sets the generated clock to sample-rate times the TX ratio, and registers dmaengine PCM against the common data register.

## Important APIs, Types, And Functions
- `struct mchp_spdiftx_mixer_control` stores 192-bit channel status and user-data arrays protected by a spinlock.
- `struct mchp_spdiftx_dev` stores control state, DMA playback data, regmap, pclk/gclk, DAI format, and suspended IRQ mask.
- `mchp_spdiftx_channel_status_write()` and `mchp_spdiftx_user_data_write()` serialize software arrays into hardware registers.
- IRQ handler writes deferred status/user data at `CSRDY`/`UDRDY` and disables handled error/status interrupts.
- DAI ops: startup reset/FIFO clear, shutdown interrupt disable, trigger TX enable/disable, `hw_params`, and `hw_free`.
- IEC958 controls expose playback default/mask status and subcode read/write.

## Control Flow
Probe maps registers, requests IRQ, gets pclk/gclk, initializes the control lock and default channel status, enables runtime PM, sets DMA address/width, and registers PCM/DAI. Startup resets the IP and clears FIFO. `hw_params` rejects capture and active TX, chooses mono/dual mode, maxburst, byte width, endian, valid bits, AES3 sample frequency code, retunes gclk, writes channel status, and writes MR. Trigger start restores saved IRQ mask and enables underrun/overrun interrupts before enabling TX; stop/suspend saves and disables interrupts and disables TX. IEC958 control writes either update registers immediately or enable ready IRQs if TX is running.

## State And Persistence
Channel-status/user-data arrays persist in driver memory and are pushed to registers during control updates or ready interrupts. Runtime PM uses regcache and clocks; suspend stores the current interrupt mask. No state is persisted outside kernel memory.

## Dependencies And Integration Points
Uses ASoC, dmaengine PCM, regmap MMIO, runtime PM, clk, IRQ, and `sound/asoundef.h` IEC958 definitions. OF compatible is `microchip,sama7g5-spdiftx`.

## Risks
The file contains likely compile-sensitive defects: `GENAMSK` in the multichannel mask macro and a malformed `.access` initializer for the IEC958 playback mask control. Runtime retunes gclk by disabling and re-enabling it, so failures can leave the clock state changed. Deferred control writes depend on hardware ready IRQs while playback is running. Sample-rate mapping accepts some rates as "not indicated" and rejects others.

## Test Signals
Build tests are important for macro and initializer issues. Runtime tests should cover playback at all accepted rates/formats, IEC958 status/subcode writes while stopped and running, underrun/overflow IRQs, runtime suspend/resume, and mono versus stereo DMA burst behavior.
