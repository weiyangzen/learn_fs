# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic3x.c

## Purpose
Implements the ASoC codec core for TLV320AIC3x/AIC33/AIC3007/AIC3104/AIC3106 devices, including mixer controls, model-specific DAPM graphs, PLL/sample-rate setup, TDM slot handling, regulator/reset power management, and DT/platform configuration.

## Important APIs, Types, and Functions
`struct aic3x_priv` stores component/regmap, bulk supplies, regulator notifiers, setup GPIO functions, sysclk, DAI format, TDM delay/slot width, master flag, reset GPIO sharing, power state, model, micbias voltage, and output common-mode voltage. Key callbacks are `aic3x_hw_params()`, `aic3x_prepare()`, `aic3x_mute()`, `aic3x_set_dai_sysclk()`, `aic3x_set_dai_fmt()`, `aic3x_set_dai_tdm_slot()`, `aic3x_set_power()`, `aic3x_set_bias_level()`, `aic3x_component_probe()`, `aic3x_init()`, exported `aic3x_probe()`, and `aic3x_remove()`.

## Control Flow
Probe allocates private data, starts regmap in cache-only mode, parses DT GPIO/micbias options, obtains reset GPIO including a nonexclusive fallback for shared reset lines, requests four supplies, computes output common-mode voltage from DT or regulator voltages, and registers the component/DAI. Component probe installs regulator-disable notifiers, marks regcache dirty, initializes default routes/volumes, applies optional GPIO functions, adds model-specific controls and DAPM widgets, sets micbias, and adds routes. Bias STANDBY powers supplies and syncs cache; OFF soft-resets, marks cache dirty, switches cache-only, and disables regulators. `hw_params()` sets word length, tries PLL bypass via Q divider, otherwise searches PLL P/R/J/D values, sets fsref and sample-rate divisors, and writes PLL registers. `prepare()` programs TDM data delay for DSP_A/B.

## State and Persistence
Runtime state includes sysclk source/frequency, DAI format, TDM slot geometry, master mode, power flag, reset ownership, model, micbias voltage, and OCMV. Regmap RBTREE cache persists register settings while supplies are off. Regulator notifiers force reset and mark cache dirty if a supply is disabled externally.

## Dependencies and Integration Points
Depends on ASoC component/DAI/DAPM, regmap cache, regulator bulk APIs, optional reset GPIO, OF properties `ai3x-gpio-func`, `ai3x-micbias-vg`, and `ai3x-ocmv`, and bus wrappers. Machine drivers integrate via `tlv320aic3x-hifi`, sysclk, DAI format, TDM slots, and DAPM pins.

## Risks
OF match tables in wrappers do not encode model data, risking fallback to model 0 on some enumeration paths. PLL search uses integer approximations and may silently choose closest settings rather than exact. Shared reset fallback is explicitly uncertain because resetting one chip may disturb others. Many component writes during initialization ignore return values. Bias transitions and regulator notifiers depend on regcache correctness after resets and external supply events.

## Test Signals
Cover all model IDs for extra/mono/class-D/3104 widget differences, regulator disable notifier paths, shared and exclusive reset GPIOs, 44.1/48 kHz PLL families, bypass PLL and programmed PLL cases, all supported formats and TDM slot widths, DAPM micbias transitions, OCMV computation from regulator voltages, and suspend-like OFF/STANDBY cache sync cycles.
