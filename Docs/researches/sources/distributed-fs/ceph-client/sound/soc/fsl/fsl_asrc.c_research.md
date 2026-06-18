# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.c

## Purpose
`fsl_asrc.c` is the core Freescale/NXP ASRC DAI driver. It owns ASRC register programming, pair allocation, sample-rate conversion configuration, clock-source selection, interrupt error accounting, runtime/system power management, SoC variant data, and the callback table used by the DMA and M2M frontends.

## Important APIs, Types, and Functions
- Supported rates are listed in `supported_asrc_rate[]` and exposed as an ALSA hardware constraint.
- Clock map tables translate public `enum asrc_inclk`/`enum asrc_outclk` values into hardware ASRCSR fields for i.MX35, i.MX53, i.MX8QM, i.MX8QXP, and i.MX952 variants.
- `fsl_asrc_request_pair()` and `fsl_asrc_release_pair()` allocate/free ASRC pairs and channel capacity under `asrc->lock`.
- `fsl_asrc_config_pair()` validates channels, formats, rates, ratio limits, clock divisibility, word widths, and writes the ASRC pair registers.
- `fsl_asrc_select_clk()` chooses internal-ratio clocks with exact divisors or falls back to ideal-ratio mode.
- `fsl_asrc_start_pair()` and `fsl_asrc_stop_pair()` enable/disable a pair and prime the input FIFO.
- DAI callbacks `startup`, `hw_params`, `hw_free`, `trigger`, and `probe` integrate conversion with ALSA PCM.
- Regmap callbacks describe readable, writable, and volatile registers plus defaults.
- `fsl_asrc_init()` writes recommended parameter registers, task FIFO base, and 76 kHz/56 kHz period registers from `ipg_clk`.
- `fsl_asrc_isr()` clears overload status and records per-pair task/FIFO errors.
- M2M helpers implement `m2m_prepare`, `m2m_start`, `m2m_stop`, output readiness, output-length calculation, maxburst selection, capabilities, and resume priming.
- `fsl_asrc_probe()` wires platform resources, clocks, regmap, IRQ, DT properties, SoC data, callbacks, runtime PM, ASoC DAI registration, and M2M registration.

## Control Flow
Probe maps MMIO, initializes regmap, requests IRQ, obtains `mem`, `ipg`, optional `spba`, and all sixteen `asrck_N` clocks, then reads SoC match data. It fills shared `struct fsl_asrc` callbacks for DMA and M2M users, picks the appropriate clock map from compatible string plus `fsl,asrc-clk-map` where required, reads default ASRC backend rate/format from DT, enables runtime PM, resumes the device to initialize registers, then registers the ASoC component/DAI and the compressed M2M card.

PCM startup constrains rates and older 3-bit-channel hardware to even channel counts. PCM `hw_params` requests a pair for the stream channel count, fills an `asrc_config` according to playback or capture direction, selects clocks, and programs the pair. Playback converts user input rate/format to fixed ASRC output rate/format; capture reverses that relationship. Trigger starts/stops the pair; `hw_free` releases the pair.

Pair configuration chooses word widths from ALSA formats, validates rates against the supported table and low-output-rate ratio range, maps clock IDs, checks dividers, writes channel count, ratio mode, clock sources, clock divisors, word width, buffer stall, FIFO watermarks, and optionally ideal ratio preprocessing/postprocessing plus fixed-point ratio registers.

Runtime resume enables clocks, temporarily disables all pairs, restores regmap cache, reapplies cached `REG_ASRCFG` fields, restarts previously enabled pairs, and waits for initialization status. Runtime suspend snapshots `REG_ASRCFG`, switches regmap to cache-only, and disables clocks. System suspend/resume wraps runtime PM and calls M2M suspend/resume helpers.

## State and Persistence
Persistent hardware state is represented in regmap cache across runtime suspend. `asrc_priv->regcache_cfg` keeps `REG_ASRCFG` fields that regcache alone does not safely restore. `asrc->pair[]`, `channel_avail`, and each `fsl_asrc_pair` contain live allocation and error state. `asrc->asrc_rate` and `asrc->asrc_format` are DT-derived defaults for ASoC BE conversion. No filesystem persistence is used.

`pair_priv->config` points to a stack `struct asrc_config` during `hw_params`/M2M prepare, so it must not be dereferenced after the configuration function returns. The current code confines use to synchronous configuration.

## Dependencies and Integration Points
This file depends on ALSA SoC DAI/component APIs, DMAengine PCM metadata, regmap MMIO, runtime PM, common ASRC structures from `fsl_asrc_common.h`, ASRC register definitions from `fsl_asrc.h`, and exported component/M2M functions in `fsl_asrc_dma.c` and `fsl_asrc_m2m.c`. It integrates with machine drivers through the DAI stream names `ASRC-Playback` and `ASRC-Capture` and with DT compatibles for SoC-specific behavior.

## Risks and Edge Cases
- `fsl_asrc_dai_hw_params()` requests a pair before full validation; if `fsl_asrc_config_pair()` fails, the function returns without releasing the pair, so error-path changes should be audited.
- Clock map entries can map many unsupported public clock IDs to fallback hardware values; invalid DT or future enum additions can silently choose undesirable clocks.
- Ideal ratio mode avoids exact divider requirements but changes conversion speed and uses `IDEAL_RATIO_RATE` for fast M2M conversions, which can overload hardware.
- Initialization timeouts are warnings, not hard failures, so conversion may continue with latent hardware readiness issues.
- Interrupt handling clears overload broadly and logs at debug level; test setups must inspect `pair->error` or debug logs to see quality issues.
- Runtime resume restarts pairs based on cached ASRCTR state; concurrent stream shutdown around suspend/resume should be treated carefully.
- `fsl_asrc_m2m_calc_out_len()` subtracts `ASRC_OUTPUT_LAST_SAMPLE`; small conversions can underflow if callers do not validate minimum input length.

## Test Signals
- Probe on each compatible verifies all clocks and `fsl,asrc-clk-map` variants bind.
- PCM playback/capture with all supported rates and S8/S16/S24 formats validates constraints, pair allocation, dividers, and DMA integration.
- Runtime suspend/resume during active conversion checks regcache restore and pair restart.
- M2M compressed tasks with varied rates/formats validate ideal-ratio configuration, DMA completion, final FIFO drain, and output-size reporting.
- Error injection or overload stress should update `pair->error` without interrupt storms.
