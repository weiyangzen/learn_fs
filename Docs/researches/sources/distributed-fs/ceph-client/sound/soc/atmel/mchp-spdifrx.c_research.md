# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdifrx.c

## Purpose
Microchip S/PDIF receiver CPU DAI. It provides stereo capture from the S/PDIF RX holding register, exports IEC958 channel status, subcode, lock, signal, bad-format, and calculated-rate controls, and uses runtime PM plus regcache around the pclk/gclk-backed hardware block.

## Important APIs, Types, And Functions
- `struct mchp_spdifrx_ch_stat` and `struct mchp_spdifrx_user_data` store 192-bit blocks plus completions.
- `struct mchp_spdifrx_dev` persists DMA data, controls, mutex, regmap, clocks, and `trigger_enabled`.
- Regmap callbacks mark status/RHR as precious or volatile and constrain readable/writeable registers.
- IRQ handler `mchp_spdif_interrupt()` completes channel-status/user-data acquisitions and reports overruns.
- DAI ops are `mchp_spdifrx_dai_probe`, `mchp_spdifrx_dai_remove`, `mchp_spdifrx_trigger`, and `mchp_spdifrx_hw_params`.
- IEC958 controls use `mchp_spdifrx_cs_get`, `mchp_spdifrx_subcode_ch_get`, `mchp_spdifrx_ulock_get`, `mchp_spdifrx_badf_get`, `mchp_spdifrx_signal_get`, and `mchp_spdifrx_rate_get`.

## Control Flow
Probe maps MMIO, initializes regmap and IRQ, gets pclk/gclk, sets a default gclk minimum rate for signal queries before `hw_params`, enables runtime PM, sets capture DMA address/maxburst, and registers PCM/DAI. DAI probe resets the IP, writes default MR behavior, initializes completions, and installs controls. `hw_params` rejects playback and non-stereo capture, maps endian/data width, retunes the gclk minimum to rate times the hardware ratio, and writes MR while holding `mlock` and while not running. Trigger start enables overrun IRQ and RX; stop disables them.

## State And Persistence
Control caches hold last channel status and subcode data, updated either synchronously from registers or through IRQ completions while running. `trigger_enabled` is used to avoid misleading hardware status when clocks are on but receiver is disabled. Regcache preserves configuration through runtime suspend/resume; no user data is persisted across driver reload.

## Dependencies And Integration Points
Depends on ASoC, dmaengine PCM, regmap MMIO, runtime PM, clk, IRQ, and IEC958 ALSA control definitions. Device-tree compatible is `microchip,sama7g5-spdifrx`. Integration with user space is through PCM capture and volatile IEC958 PCM controls.

## Risks
The source contains `GENAMSK` in the validity-bit mask macro, which is a compile-time risk if not hidden by preprocessing context. Control reads can wait up to 100 ms for completions; absent or unstable S/PDIF input returns timeout. Gclk minimum rate must be valid before signal/rate controls are queried. The signal control briefly enables RX when not streaming, so it can perturb hardware state if called frequently.

## Test Signals
Build coverage should catch register-mask typos. Runtime testing should cover control reads with and without an incoming signal, capture format validation, gclk retuning per sample rate, overrun IRQ warnings, and runtime suspend/resume with controls after resume.
