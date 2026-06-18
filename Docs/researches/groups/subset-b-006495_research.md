<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8978.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8978.c

## Purpose

This file implements the ALSA SoC codec driver for the Wolfson WM8978 stereo codec. It exposes a single `wm8978-hifi` DAI with playback and capture, codec mixer/volume/ALC/EQ controls, DAPM routes for input, boost, output, headphone, speaker, and mic-bias paths, and an I2C-only component registration path using regmap caching.

## Important APIs, types, and functions

`struct wm8978_priv` keeps the regmap and clock-planning state: external MCLK, PLL output, requested 256fs codec clock, optional OPCLK, cached MCLK divider index, and selected system clock source. Register defaults and `wm8978_volatile()` define a 7-bit register, 9-bit value regmap with only the reset register volatile. The main DAI callbacks are `wm8978_set_dai_clkdiv()`, `wm8978_set_dai_sysclk()`, `wm8978_set_dai_fmt()`, `wm8978_hw_params()`, and `wm8978_mute()`. Clock helpers include `pll_factors()`, `wm8978_enum_mclk()`, and `wm8978_configure_pll()`. Component lifecycle hooks are `wm8978_probe()`, `wm8978_set_bias_level()`, `wm8978_suspend()`, and `wm8978_resume()`. Bus integration is handled by `wm8978_i2c_probe()` and `module_i2c_driver()`.

## Control flow

I2C probe allocates private state, creates the regmap, resets the codec by writing `WM8978_RESET`, and registers the ASoC component plus DAI. Component probe defaults the system clock source to PLL and sets bit 8 on all paired volume/update registers so future ALSA control writes take effect synchronously.

DAI format configuration reads and rewrites the audio-interface and clocking registers for master/slave mode, I2S/right-justified/left-justified/DSP_A format, and bit/frame clock polarity. `set_sysclk()` records the MCLK frequency, optionally configures the PLL immediately when OPCLK was requested, and can switch from PLL back to direct MCLK while disabling PLL and GPIO1 OPCLK output. `set_clkdiv()` accepts `WM8978_OPCLKRATE` as a requested OPCLK frequency and `WM8978_BCLKDIV` as a raw BCLK divider field.

`hw_params()` programs word length, ADC/DAC filter-rate bits, computes the 256fs target from the PCM rate, then either uses direct MCLK or configures/uses PLL output. It searches the MCLK divider table for the best divisor, warns on imprecise rates, writes the MCLK divisor, audio-interface, and additional-control registers, and updates the clock source select bit if the selected source changed. `wm8978_mute()` only toggles the DAC soft-mute bit.

## State and persistence behavior

The driver persists clock intent in `wm8978_priv`; register programming is otherwise represented in the regmap cache and hardware. Bias transitions manage VMID and bias timing: standby from off briefly charges caps at low VMID impedance, then moves to a high impedance standby state; off clears power management 2 and 3 and clears most of power management 1 while deliberately preserving the PLL bit because OPCLK might be in use externally. Suspend forces bias off, fully clears power management 1 including PLL, and marks regcache dirty. Resume syncs the cache, returns to standby, and re-enables PLL if `f_pllout` records a previous PLL configuration.

## Dependencies and integration points

The file depends on Linux I2C, regmap, ASoC component/DAI/DAPM/control APIs, TLV control helpers, and `asm/div64.h` for PLL factor math. It matches I2C id `wm8978` and OF compatible `wlf,wm8978`. Machine drivers integrate through the `wm8978-hifi` DAI, `set_sysclk()`, `set_clkdiv()`, and `set_fmt()` calls; board routing uses the DAPM endpoint names such as `LMICN`, `LMICP`, `RMICN`, `RMICP`, `LAUX`, `RAUX`, `L2`, `R2`, `LHP`, `RHP`, `LSPK`, and `RSPK`.

## Risks and test signals

Clocking is the main risk area: OPCLK requests can force early PLL programming and later `hw_params()` avoids reconfiguring PLL to protect OPCLK, so unusual OPCLK/sample-rate combinations can produce imprecise sample rates. `wm8978_hw_params()` does not reject unsupported sample widths outside the handled cases before continuing with the default 16-bit setting. PLL range checks warn or fail depending on the path, and direct MCLK operation can warn about imprecision instead of failing. Power-off preserves PLL for OPCLK in normal bias-off but suspend clears it, which is a behavioral distinction to test. Test signals include I2C probe/reset, control enumeration visibility, DAPM route power-up for capture and playback, supported 8-48 kHz rates and 16/20/24/32-bit formats, direct MCLK versus PLL clocking, OPCLK output on GPIO1, mute/unmute, suspend/resume with regcache sync, and bias transition pop/noise behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8978.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8978.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8978.h

## Purpose

This header defines the WM8978 register addresses and the small public clock-id enums used by `wm8978.c`. It is the driver's register map contract for ASoC controls, DAPM widgets, PLL programming, power management, and bus reset.

## Important APIs, types, and functions

The header exports register address macros from `WM8978_RESET` through `WM8978_OUT4_MIXER_CONTROL`, plus `WM8978_MAX_REGISTER` and `WM8978_CACHEREGNUM`. `enum wm8978_clk_id` defines `WM8978_OPCLKRATE` and `WM8978_BCLKDIV` for the DAI `.set_clkdiv()` callback. `enum wm8978_sysclk_src` defines `WM8978_MCLK` and `WM8978_PLL` for `.set_sysclk()` and internal clock source state.

## Control flow

There is no executable control flow. The C file uses these constants as stable indexes into regmap and ASoC helper macros. Clock IDs flow from machine driver calls to `wm8978_set_dai_clkdiv()`, while system clock values flow into `wm8978_set_dai_sysclk()` and are stored in `struct wm8978_priv`.

## State and persistence behavior

The header does not store state. Its address definitions determine what the regmap can cache and what registers are reset or rewritten across probe, suspend, resume, control changes, and DAPM power transitions.

## Dependencies and integration points

The file is private to the WM8978 codec driver and guarded by `__WM8978_H__`. Its constants are consumed by `wm8978.c`; machine drivers indirectly depend on the enum values only when calling ASoC DAI clock APIs for this codec.

## Risks and test signals

Because the header mostly contains raw addresses rather than field masks, bit positions remain embedded in `wm8978.c`, making register-review mistakes harder to localize. `WM8978_CACHEREGNUM` is legacy-style metadata and the active regmap actually uses `WM8978_MAX_REGISTER` plus defaults. Test signals are compile-time: all register names must resolve, max register must cover the highest default/control register, and clock enum values must match `wm8978_set_dai_clkdiv()` and `wm8978_set_dai_sysclk()` switch cases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8978.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8983.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8983.c

## Purpose

This file implements the ALSA SoC driver for the WM8983 codec. It provides a stereo-only `wm8983-hifi` DAI, a large set of mixer/volume/ALC/EQ/3D controls, DAPM widgets and routes for input, boost, output, OUT3, and OUT4 paths, PLL and clock divider programming, and both I2C and SPI bus registration.

## Important APIs, types, and functions

`struct wm8983_priv` stores the regmap, selected `sysclk`, and computed `bclk`. `wm8983_defaults` seeds the regcache, while `wm8983_writeable()` restricts writeable register ranges. The control surface is built from TLV scales, enum declarations, `wm8983_snd_controls`, DAPM mixer controls, `wm8983_dapm_widgets`, and `wm8983_audio_map`. Special EQ mode handling uses `eqmode_get()` and `eqmode_put()`. DAI callbacks are `wm8983_dac_mute()`, `wm8983_set_fmt()`, `wm8983_hw_params()`, `wm8983_set_pll()`, and `wm8983_set_sysclk()`. Lifecycle and registration functions include `wm8983_set_bias_level()`, `wm8983_probe()`, `wm8983_i2c_probe()`, `wm8983_spi_probe()`, `wm8983_modinit()`, and `wm8983_exit()`.

## Control flow

Module init registers the I2C driver when I2C is enabled and the SPI driver when SPI master support is built. Bus probe allocates private state, initializes the bus-specific regmap, stores driver data, and registers the ASoC component and DAI.

Component probe issues a software reset, sets update bits on paired volume/gain registers, mutes all analog outputs by setting bit 6 across the output-control register range, enables DAC soft mute, and enables `BIASCUT`. Bias transitions sync the regcache when moving from off to standby, enable anti-pop and thermal shutdown, enable bias and VMID, delay for startup, disable anti-pop, then move VMID to a 500k standby value. Bias off disables thermal shutdown, clears VMID and bias, waits for discharge, and clears all power-management registers.

DAI format setup writes the format field, master/slave bit, and clock polarity bits. Although DSP_A/DSP_B are initially mapped to the DSP format field, a later switch rejects both with "DSP A/B modes are not supported." `hw_params()` computes BCLK from PCM parameters, programs word length, chooses the closest filter sample-rate code from the fixed `srates` table, requires `sysclk / rate` to exactly match one of the supported fs ratios, and requires BCLK to exactly match a generated value after applying one of the supported BCLK divisors. `set_pll()` disables PLL if either frequency is zero; otherwise it computes N/K/prescale for `freq_out * 8`, disables PLL, writes PLL registers, and enables PLL. `set_sysclk()` selects MCLK or PLL in the clock generator and records the frequency.

## State and persistence behavior

Runtime state is limited to regmap cache plus `sysclk` and `bclk` fields. There is no explicit suspend/resume callback; the component sets `suspend_bias_off`, so ASoC bias management and regcache synchronization handle power transitions. EQ mode changes preserve and restore power-management 2 and 3 around a temporary ADC/DAC power-down to avoid changing EQ capture/playback mode while converters are active.

## Dependencies and integration points

The driver depends on Linux I2C, SPI, regmap, ASoC DAI/component/control/DAPM APIs, TLV helpers, delay APIs, and `wm8983.h` bit definitions. It integrates through I2C id `wm8983`, SPI modalias `wm8983`, and the `wm8983-hifi` DAI. Machine drivers must call `set_sysclk()` with a rate that makes `sysclk / sample_rate` equal to one of 128/192/256/384/512/768/1024/1536, and must configure PLL externally through `.set_pll()` if PLL is used as the selected source.

## Risks and test signals

The strict BCLK divider check can reject otherwise common hardware configurations if `snd_soc_params_to_bclk()` does not match the generated divider exactly. `wm8983_set_fmt()` advertises DSP format encoding briefly but then rejects DSP_A/B, so machine drivers using DSP modes will fail. `eqmode_put()` toggles ADC/DAC enable bits directly and depends on restoring old power registers correctly. Module init can overwrite `ret` with SPI registration status after I2C registration, and partial registration cleanup is only done in module exit. Test signals include I2C and SPI probe, reset and regcache defaults, all visible controls, EQ mode switching during idle and active paths, supported sample rates and MCLK ratios, PLL enable/disable and N/K programming, exact BCLK divider acceptance, DAPM route power for OUT3/OUT4 and capture/playback, mute/unmute, and bias off/standby pop behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8983.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8983.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8983.h

## Purpose

This header provides the WM8983 register address map and generated-style bit, mask, shift, and width definitions used by the WM8983 codec driver. It also defines the clock-source enum used by the DAI `.set_sysclk()` path.

## Important APIs, types, and functions

The header defines register macros from `WM8983_SOFTWARE_RESET` through `WM8983_BIAS_CTRL`, `WM8983_REGISTER_COUNT`, and `WM8983_MAX_REGISTER`. It then enumerates field definitions for power management, audio interface, companding, clock generation, GPIO, jack detect, DAC/ADC control, digital volumes, EQ, limiter, notch filter, ALC, PLL, 3D, output, input, boost, mixer, OUT3/OUT4, and bias-control registers. `enum clk_src` exposes `WM8983_CLKSRC_MCLK` and `WM8983_CLKSRC_PLL`.

## Control flow

The header has no runtime control flow. Its masks and shifts feed `snd_soc_component_update_bits()` calls in `wm8983.c`, especially the DAI format, PLL, MCLK/BCLK divider, bias, EQ mode, and power-management paths.

## State and persistence behavior

No state is stored here. The definitions determine which bits the C driver can preserve, clear, or update when regmap cache entries are synchronized, power states change, or ALSA controls are written.

## Dependencies and integration points

The header is private to `wm8983.c` and guarded by `_WM8983_H`. Its clock-source enum is part of the codec-specific DAI API expected by machine drivers. Its register constants must stay aligned with the `wm8983_defaults` table and `wm8983_writeable()` ranges in the C file.

## Risks and test signals

The file contains repeated macro names for update bits such as `WM8983_DACVU`, `WM8983_ADCVU`, `WM8983_NFU`, `WM8983_INPGAVU`, `WM8983_OUT1VU`, and `WM8983_OUT2VU` across left/right register sections. They resolve to the same bit values, so compilation succeeds, but edits can be confusing. The generated-style field inventory is broad, while `wm8983.c` uses only a subset of fields; unused macros may drift unnoticed. Test signals are build coverage, sparse/preprocessor sanity, and driver tests that exercise every mask used in `wm8983.c`: format, polarity, clock source, PLL, bias, ADC/DAC enable, soft mute, thermal shutdown, and EQ mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8983.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8985.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8985.c

## Purpose

This file implements the ALSA SoC driver for WM8985 and WM8758 codecs. It exposes one stereo `wm8985-hifi` DAI, common mixer/volume/ALC/EQ/3D controls, WM8985-only AUX and speaker-mode controls, variant-specific DAPM widgets/routes, PLL and clock divider programming, regulator-managed power supplies, and both I2C and SPI registration.

## Important APIs, types, and functions

`struct wm8985_priv` stores the regmap, four regulators (`DCVDD`, `DBVDD`, `AVDD1`, `AVDD2`), device type (`WM8985` or `WM8758`), selected `sysclk`, and computed `bclk`. `wm8985_writeable()` lists writeable registers. Common and device-specific controls live in `wm8985_common_snd_controls` and `wm8985_specific_snd_controls`; common and variant DAPM widgets/routes are split across `wm8985_common_dapm_widgets`, `wm8985_dapm_widgets`, `wm8758_dapm_widgets`, `wm8985_common_dapm_routes`, and `wm8985_aux_dapm_routes`. Key functions are `wm8985_add_widgets()`, `eqmode_get()`, `eqmode_put()`, `wm8985_reset()`, `wm8985_dac_mute()`, `wm8985_set_fmt()`, `wm8985_hw_params()`, `wm8985_set_pll()`, `wm8985_set_sysclk()`, `wm8985_set_bias_level()`, and `wm8985_probe()`.

## Control flow

Module init registers I2C and/or SPI bus drivers based on kernel config. SPI probe always sets `dev_type` to `WM8985`; I2C probe derives `dev_type` from the id table, supporting both `wm8985` and `wm8758`. Bus probe allocates private state, initializes the regmap, and registers the component.

Component probe names and requests the four supplies, enables them, resets the codec, latches volume update bits, enables `BIASCUT`, and calls `wm8985_add_widgets()`. That helper adds WM8758-specific reduced mixer widgets or WM8985-specific controls, AUX widgets, and AUX routes. Bias standby from off enables regulators, syncs regcache, enables anti-pop and thermal shutdown controls, enables bias and VMID, delays 500 ms, then clears anti-pop and moves VMID to 300k. Bias off disables thermal controls, clears VMID/bias and power registers, marks regcache dirty, and disables regulators.

DAI format setup maps I2S/right-justified/left-justified/DSP formats, master/slave mode, and polarity bits, but rejects frame inversion for DSP_A/DSP_B. `hw_params()` computes BCLK, programs word length, picks nearest filter sample-rate code, requires an exact supported MCLK-to-rate ratio, and requires an exact BCLK divider. `set_pll()` disables PLL when frequencies are zero; otherwise it computes PLL factors for `freq_out * 8`, writes PLL registers, selects PLL as clock source, and enables PLL. `set_sysclk()` selects direct MCLK and disables PLL, or selects PLL, then records the supplied frequency.

## State and persistence behavior

The driver persists device variant, regulator handles, and clock values in private state. Register state is cached by regmap and explicitly marked dirty when supplies are disabled. The component uses `suspend_bias_off`, so suspend enters bias-off behavior and regulator disable. EQ mode changes temporarily disable ADCs and DACs, set `M128ENB`, change the EQ mode bit, and restore previous converter power registers.

## Dependencies and integration points

Dependencies include I2C, SPI, regmap, regulator bulk APIs, ASoC controls/DAPM/DAI APIs, delay APIs, and `wm8985.h`. Integration points are I2C ids `wm8985` and `wm8758`, SPI modalias `wm8985`, regulator names required from board/DT/regulator configuration, and the `wm8985-hifi` DAI. WM8758 support is implemented by suppressing WM8985-only AUX mixer controls/routes rather than by a separate component driver.

## Risks and test signals

Power sequencing has higher risk than WM8983 because regulators are enabled in probe and again on standby-from-off; failure paths only disable supplies after reset failure, while later probe failures are limited. Exact MCLK/BCLK divider matching can reject valid board configurations if sysclk or slot format differs from the hard-coded ratios. Variant behavior is subtle: SPI cannot instantiate WM8758, and WM8758 removes the last entries of shared mixer arrays by array-size subtraction. EQ mode directly powers down converters and sets `M128ENB`, so active stream changes need testing. Test signals include regulator acquisition/enable/disable, probe reset, WM8985 and WM8758 control/DAPM differences, I2C and SPI registration, PLL programming, direct MCLK and PLL sysclk paths, all supported PCM widths/rates, exact BCLK divider behavior, mute/unmute, EQ mode switching, bias transitions with regcache sync, and suspend/resume through bias-off.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8985.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8985.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8985.h

## Purpose

This header defines the WM8985 and WM8758 register map, bitfields, clock-source identifiers, and PLL id used by `wm8985.c`. It is the shared register contract for both codec variants.

## Important APIs, types, and functions

The header defines register addresses from `WM8985_SOFTWARE_RESET` through `WM8985_BIAS_CTRL`, `WM8985_REGISTER_COUNT`, and `WM8985_MAX_REGISTER`. It provides field macros for power, interface, companding, clock generation, GPIO, jack detect, DAC/ADC controls, digital volumes, EQ, limiter, notch filter, ALC, PLL, 3D, OUT4-to-ADC, beep, input, boost, output, mixer, OUT3/OUT4, output control 1, and bias control. It includes WM8758-specific fields such as `WM8758_OPCLKDIV_*`, `WM8758_JD_VMID*`, `WM8758_VMIDTOG`, `WM8758_OUT2DEL`, `WM8758_DELEN2`, `WM8758_HP_COM`, `WM8758_LINE_COM`, and output-enable delay bits. `enum clk_src` defines `WM8985_CLKSRC_MCLK` and `WM8985_CLKSRC_PLL`; `WM8985_PLL` is defined as PLL id 0.

## Control flow

There is no executable control flow. `wm8985.c` uses the field masks and shifts to build ALSA controls and update registers in DAI, PLL, EQ, bias, mute, and DAPM paths. Machine drivers indirectly use the clock-source enum and PLL id through ASoC DAI operations.

## State and persistence behavior

The header stores no runtime state. It shapes the driver's state transitions by defining which bits can be preserved or rewritten during regcache sync, regulator power cycling, PLL selection, and variant-specific widget/control registration.

## Dependencies and integration points

The header is private to the WM8985/WM8758 driver and guarded by `_WM8985_H`. Register constants must align with `wm8985_reg_defaults`, `wm8985_writeable()`, and the variant-specific control logic. The mixed WM8985 and WM8758 definitions document the overlapping but not identical register semantics used by the combined driver.

## Risks and test signals

The header repeats same-valued update-bit macro names across left/right registers and mixes WM8758-specific fields into the WM8985 register layout, which can make future edits error-prone. Some macros describe fields not used by the current C driver, so build coverage alone will not validate them. Test signals include successful compilation of both `wm8985` and `wm8758` id paths, control tests touching masks used by the driver, PLL/source selection using `WM8985_PLL`, and variant tests ensuring WM8758-only fields do not accidentally enable WM8985-only AUX paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8985.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8988.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8988.c

## Purpose

This file implements the ALSA SoC driver for the WM8988 codec. It exposes one `wm8988-hifi` DAI with playback and capture, software register caching for write-only two-wire control, a broad analog/digital control set, DAPM muxes and mixers for line/PGA/differential input routing and output routing, fixed SYSCLK-to-rate constraints, and I2C/SPI registration.

## Important APIs, types, and functions

`struct wm8988_priv` stores the regmap, configured SYSCLK frequency, and a pointer to the sample-rate constraint list derived from that SYSCLK. `wm8988_reg_defaults` provides cache defaults and `wm8988_writeable()` lists registers that can be written. Controls are defined in `wm8988_snd_controls`; DAPM behavior is defined through route enums, mixer controls, `wm8988_dapm_widgets`, and `wm8988_dapm_routes`. Clock/rate selection uses `struct _coeff_div`, `coeff_div`, `get_coeff()`, and SYSCLK-specific constraint lists. DAI callbacks are `wm8988_pcm_startup()`, `wm8988_pcm_hw_params()`, `wm8988_set_dai_fmt()`, `wm8988_set_dai_sysclk()`, and `wm8988_mute()`. Lifecycle and bus functions are `wm8988_probe()`, `wm8988_set_bias_level()`, `wm8988_i2c_probe()`, `wm8988_spi_probe()`, `wm8988_modinit()`, and `wm8988_exit()`.

## Control flow

Module init registers I2C and/or SPI drivers. Bus probe allocates private state, initializes the bus-specific regmap, stores driver data, and registers the component/DAI. Component probe resets the codec and sets update bits for right-side ADC, DAC, output, and input volume registers, relying on the driver to update left then right for synchronized volume changes.

Machine driver initialization is expected to call `set_sysclk()` before stream startup. That function accepts fixed MCLK families and assigns one of three rate constraint lists. PCM startup rejects operation if no SYSCLK was configured and then constrains the runtime sample-rate parameter. `hw_params()` finds a coefficient matching SYSCLK/rate, retries with SYSCLK divided by two by setting the divide bit, programs word length, and writes the sample-rate coefficient and USB-mode bit. Format setup writes the entire interface register for master/slave mode, I2S/right/left/DSP_A/DSP_B format, and polarity. Mute toggles the ADCDAC soft-mute bit.

DAPM route changes run `wm8988_lrc_control()` as a post event. It reads DAC power bits and selects whether LRC gating follows DAC activity or ADC activity by updating `WM8988_ADCTL2`.

## State and persistence behavior

The driver keeps only SYSCLK-related state outside the regcache. Bias standby syncs regcache when coming from off, charges VMID/VREF for 100 ms, then moves to low-power standby with digital stopped. Prepare enables VREF/VMID and digital logic; off clears `PWR1`. With `suspend_bias_off`, suspend enters the bias-off path and relies on regcache sync on return. The regmap cache is important because the device register space cannot be read in two-wire control mode.

## Dependencies and integration points

Dependencies include Linux I2C, SPI, regmap, ASoC component/DAI/DAPM/control APIs, TLV helpers, PCM constraint APIs, and `wm8988.h`. Integration points are I2C id `wm8988`, SPI modalias `wm8988`, and the `wm8988-hifi` DAI. Board drivers must supply one of the supported SYSCLK frequencies before stream startup; supported rates differ by SYSCLK family.

## Risks and test signals

The static rate table includes unusual entries in the 12 MHz constraint list, including `41100`, duplicate `48000`, and `88235`, while the coefficient table uses 44.1 kHz and 88.2 kHz style rates. That mismatch is a strong test target. The driver has no PLL setup; unsupported SYSCLK/rate pairs fail at startup or `hw_params()`. `set_dai_fmt()` rewrites the full interface register rather than preserving unrelated bits beyond the encoded format fields. DAPM routes contain duplicated line mux route blocks, which is harmless but worth noticing in route dumps. Test signals include SYSCLK constraint behavior for each supported clock family, 8-96 kHz playback/capture where coefficients exist, 16/20/24-bit formats, I2S/right/left/DSP_A/DSP_B formats, mute/unmute, DAPM input mux/mixer routes including differential and mono modes, LRC gating after DAC/ADC power changes, I2C/SPI probe, regcache sync after bias off, and two-wire write-only operation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8988.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8988.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8988.h

## Purpose

This compact header defines the WM8988 register address space and the codec-specific SYSCLK id used by `wm8988.c`.

## Important APIs, types, and functions

The header provides register address macros for input volumes, output volumes, ADCDAC, interface, sample-rate control, DAC/ADC volumes, tone controls, reset, 3D, ALC/noise gate, additional controls, power registers, ADC input muxes, output mixers, low-power playback bypass, and `WM8988_NUM_REG`. `WM8988_SYSCLK` defines the clock id accepted by the codec-specific sysclk API.

## Control flow

There is no runtime control flow. The C driver uses these constants in regmap defaults, writeability checks, control definitions, DAPM widgets/routes, reset, clock/rate setup, mute, and bias transitions.

## State and persistence behavior

The header stores no state. Its register address list defines the cacheable/writeable surface that lets `wm8988.c` operate when hardware registers cannot be read over two-wire control.

## Dependencies and integration points

The file is private to the WM8988 driver and guarded by `_WM8988_H`. Machine drivers indirectly use `WM8988_SYSCLK` when configuring the DAI clock source; all other definitions are consumed by `wm8988.c`.

## Risks and test signals

The header defines only addresses, not field masks, so bit-level meaning is embedded as literals in the C file. `WM8988_NUM_REG` covers the sparse address space up to `WM8988_LPPB`, while regmap uses `WM8988_LPPB` as `max_register`; these should stay aligned. Test signals are compilation, regmap max-register coverage, reset and update-bit writes to the expected addresses, and successful use of `WM8988_SYSCLK` through machine-driver sysclk setup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8988.h -->
