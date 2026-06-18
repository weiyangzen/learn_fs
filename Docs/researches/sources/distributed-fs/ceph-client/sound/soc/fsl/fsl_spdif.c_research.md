# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.c

## Purpose
`fsl_spdif.c` is the Freescale/NXP S/PDIF ASoC CPU DAI driver. It exposes stereo S/PDIF playback/capture, configures transmitter and receiver clocks, handles DPLL lock and user/channel-status interrupts, provides IEC958 ALSA controls, supports raw capture and bypass on selected SoCs, and manages runtime PM clock/regcache state.

## Important APIs, Types, And Functions
The platform driver is `fsl_spdif_driver`, matched by `fsl_spdif_dt_ids`. The ASoC component is `fsl_spdif_component`; the DAI template is copied into `fsl_spdif_priv.cpu_dai_drv` and uses `fsl_spdif_dai_ops`.

Important types are `struct fsl_spdif_soc_data`, `struct spdif_mixer_control`, and `struct fsl_spdif_priv`. Key functions include `fsl_spdif_probe`, `fsl_spdif_dai_probe`, `fsl_spdif_startup`, `fsl_spdif_hw_params`, `fsl_spdif_trigger`, `fsl_spdif_shutdown`, `fsl_spdif_runtime_suspend`, `fsl_spdif_runtime_resume`, `spdif_softreset`, `spdif_set_sample_rate`, `fsl_spdif_probe_txclk`, `fsl_spdif_txclk_caldiv`, and `spdif_get_rxclk_rate`.

ALSA controls are implemented by `fsl_spdif_pb_get/put`, `fsl_spdif_capture_get`, `fsl_spdif_subcode_get`, `fsl_spdif_qget`, `fsl_spdif_rx_vbit_get`, `fsl_spdif_tx_vbit_get/put`, `fsl_spdif_rx_rcm_get/put`, `fsl_spdif_bypass_get/put`, `fsl_spdif_rxrate_get`, and `fsl_spdif_usync_get/put`.

## Control Flow
Probe allocates private data, copies the DAI template, maps registers, initializes regmap, requests one or two IRQs depending on SoC data, gets all `rxtx0..7` clocks, treats `rxtx5` as sysclk and `rxtx1` as the default RX clock, acquires core/spba clocks, initializes IEC958 channel status defaults, sets DMA addresses to STL/SRL, enables runtime PM, switches regmap to cache-only, initializes the i.MX PCM DMA platform, and registers the component.

Startup soft-resets the module on first active stream, disables interrupts, configures TX or RX FIFO modes in SCR, and powers up the block. Playback `hw_params` reparents the root clock when allowed, selects a usable TX clock/divider for the requested sample rate, updates channel-status sample-frequency bits, writes channel status registers, and sets clock accuracy. Capture `hw_params` configures SRPC receive clock source and gain. Trigger enables/disables stream-specific interrupts and DMA bits and clears TX data registers on stop. Shutdown disables FIFO modes or TX clock and powers down the module when both directions are inactive.

The IRQ path reads SIS and SIE, writes SIC to clear enabled pending bits, updates DPLL lock state and notifies the RX sample-rate kcontrol, captures U/Q subcode bytes into double buffers, marks ready buffers on sync, drops buffers on framing error, and logs FIFO, parity, validity, and lock events.

## State And Persistence
`fsl_spdif_priv` holds SoC capabilities, the mixer/control buffers, DAI template copy, card/kcontrol pointers, regmap, DPLL lock flag, per-rate clock source/divider caches, clock handles, DMA data, cached SRPC value, bypass state, and PLL clocks. `spdif_mixer_control` holds transmit channel status, U/Q buffers, buffer positions, and a spinlock for userspace reads racing with IRQ updates. Runtime suspend disables interrupts, caches SRPC, puts regmap in cache-only mode, disables all TX/RX clocks plus SPBA/core clocks, and resume reenables clocks, restores SRPC, and syncs regcache.

## Dependencies And Integration Points
The driver depends on ALSA ASoC, IEC958 definitions, DMAEngine PCM, i.MX PCM DMA, regmap, runtime PM, Linux clocks, firmware-independent clock tree behavior, and `fsl_utils` PLL reparenting. It uses the macros and rate/format masks from `fsl_spdif.h`.

## Risks And Edge Cases
TX clock calculation searches multiple clocks and dividers with a 0.1 percent quick-exit threshold, so bad clock tree rates can produce approximate output or zero divider failures. Bypass mode rewrites PCM substream counts and is blocked while streams are active; incorrect card/runtime assumptions can affect availability. U/Q buffer handling stores both U and Q data into `subcode` in the shared helper even when `qget` reads `qsub`, so this path is worth close validation. DPLL unlock disables symbol-error interrupt noise. Raw capture mutates the DAI capture format mask at runtime. Runtime PM must preserve SRPC because it is volatile and used for RX rate measurement.

## Test Signals
Test with playback rates 22.05 kHz through 192 kHz, capture DPLL lock/unlock and RX sample-rate kcontrol notifications, IEC958 playback channel-status writes, capture channel status after `INT_CNEW`, U/Q subcode reads after sync, raw capture toggle on i.MX8MM, bypass enable/disable with no active stream, suspend/resume after configured clocks, and IRQ logging for lock loss, FIFO resync, and validity errors.
