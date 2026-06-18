# sources/distributed-fs/ceph-client/sound/soc/meson/axg-pdm.c

Purpose: Implements the AXG PDM capture DAI, including PDM clocking, channel enable/reset masks, HCIC/LPF/HPF filter programming, default FIR coefficient loading, sample-pointer timing, trigger enable, and platform probe.

Important APIs and functions: Runtime ops are `axg_pdm_dai_probe()`, `axg_pdm_dai_remove()`, `axg_pdm_startup()`, `axg_pdm_shutdown()`, `axg_pdm_hw_params()`, and `axg_pdm_trigger()`. Hardware helpers include `axg_pdm_enable()`, `axg_pdm_disable()`, `axg_pdm_filters_enable()`, `axg_pdm_get_os()`, `axg_pdm_set_sysclk()`, `axg_pdm_set_sample_pointer()`, `axg_pdm_set_channel_mask()`, and filter programming helpers for HCIC, LPF, and HPF.

Control flow: Probe maps registers, gets `pclk`, `dclk`, and `sysclk`, and registers the component. DAI probe enables pclk, sets/enables sysclk to the configured maximum, disables the device, clears filter bypass, programs HCIC/HPF controls, and writes all LPF coefficient taps through coefficient address/data registers. Startup enables dclk and filter blocks. `hw_params` accepts only 24- or 32-bit samples, computes oversampling from HCIC and three LPF downsample factors, sets sysclk and dclk, calculates sample-pointer capture position at 75 percent of the half dclk period, and enables the requested channel count. Trigger resets the AFIFO and toggles PDM enable.

State and persistence: `struct axg_pdm` stores config, regmap, and clocks. Static default filter coefficient tables persist in driver text and are loaded into hardware coefficient memory during DAI probe. Channel masks and filter settings persist in hardware until reprogrammed or reset.

Dependencies and integration points: Integrates with AXG sound card capture routes, `SND_SOC_DMIC` implied Kconfig support, regmap MMIO, Common Clock, and ALSA capture DAI negotiation.

Risks: Filter coefficients are fixed defaults with a TODO for firmware-configurable alternatives, so microphone-specific tuning is not represented. Accessing registers requires sysclk as well as pclk; missing clock sequencing can bus fault. The LPF tap count must fit below `PDM_LPF_MAX_STAGE`. Sample-pointer calculation warns and fails if sysclk/dclk ratios exceed the hardware pointer width.

Test signals: PDM capture at rates up to 48 kHz, 1-8 channel masks, S24/S32 captures, clock-rate traces for sysclk/dclk, coefficient memory loading, trigger start/stop AFIFO reset behavior, and capture quality/latency checks against expected filter response.
