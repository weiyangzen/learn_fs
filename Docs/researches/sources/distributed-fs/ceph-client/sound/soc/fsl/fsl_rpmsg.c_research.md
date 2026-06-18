# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.c` implements an ASoC CPU DAI facade for NXP RPMsg audio channels. It presents playback/capture capabilities to ALSA, sizes DMA buffers for normal or low-power-audio operation, switches audio PLL parents based on sample-rate family, manages optional clocks, and customizes DAI names/caps from device tree and SoC data. The source was read as a complete 353-line file.

## Important APIs, Types, and Functions

Important functions are `fsl_rpmsg_hw_params`, `fsl_rpmsg_hw_free`, `fsl_rpmsg_startup`, `fsl_rpmsg_probe`, `fsl_rpmsg_remove`, and runtime suspend/resume. Static data includes `fsl_rpmsg_rates`, the rate constraint list, the base `fsl_rpmsg_dai`, the ASoC component, and SoC capability tables for i.MX7ULP, i.MX8MM, i.MX8MN, i.MX8MP, i.MX93, and i.MX95. Constants define large low-power playback/capture buffer sizes.

## Control Flow

Startup constrains PCM rates to a broad explicit list. `hw_params` walks up from `mclk` to find a parent matching `pll8k` or `pll11k`; if found, it selects the 8 kHz-family PLL when the requested rate is divisible by 8000, otherwise the 11.025 kHz-family PLL, and enables `mclk` once per active stream direction. `hw_free` disables `mclk` for that stream. Probe copies the base DAI, applies SoC-specific rates/formats, chooses the DAI name from `fsl,rpmsg-channel-name` or a default, special-cases `rpmsg-micfil-channel` capture capabilities, sets LPA or default DMA buffer sizes, obtains optional clocks, enables runtime PM, and registers the component. Runtime resume enables `ipg` and `dma`; suspend disables them.

## State and Persistence Behavior

Per-device state is `struct fsl_rpmsg`, holding optional clocks, optional child card device, SoC data, active `mclk_streams` bitmask, low-power flags, and per-direction buffer sizes. Stream clock state persists across `hw_params`/`hw_free` through the bitmask. No register cache or file-backed persistence is present.

## Dependencies and Integration Points

The file depends on Linux clk, runtime PM, OF, RPMsg headers, ALSA ASoC/PCM, DMAengine PCM, `fsl_rpmsg.h`, and `imx-pcm.h` for default DMA buffer sizing. It integrates with remote-processor audio through named RPMsg channels, though this file itself is the CPU DAI-facing side rather than the RPMsg message transport implementation.

## Risks and Edge Cases

`clk_prepare_enable` is called on optional clocks that may be NULL depending on clock API behavior, so platform coverage matters. PLL parent switching mutates `rate` via `do_div`; the divisibility test is concise but easy to misread. `fsl,rpmsg-channel-name` changes DAI identity and caps, so machine-driver and remote firmware names must match. LPA buffer sizes are large and affect memory pressure.

## Test Signals

Build with RPMsg audio, probe every compatible data path, verify DAI names from device tree, open normal and `rpmsg-micfil-channel` capture streams, test 8 kHz-family and 44.1 kHz-family PLL switching, ensure `mclk_streams` balances across playback/capture hw_params/free, and verify runtime PM clock enable/disable on platforms with absent optional clocks.
