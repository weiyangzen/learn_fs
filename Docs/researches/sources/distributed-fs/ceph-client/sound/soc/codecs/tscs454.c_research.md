# sources/distributed-fs/ceph-client/sound/soc/codecs/tscs454.c

## Purpose

`tscs454.c` is the Linux ALSA SoC codec driver for the Tempo Semiconductor TSCS454 audio codec. It registers an I2C-backed ASoC component with three DAIs, a large mixer-control surface, a DAPM routing graph, regmap paging support, PLL setup, stream parameter programming, and software caches for DAC, speaker, and subwoofer coefficient RAM.

The driver turns board-level I2C and clock resources into ALSA playback/capture interfaces named `tscs454-dai1`, `tscs454-dai2`, and `tscs454-dai3`. DAI1 supports up to six channels, while DAI2 and DAI3 support up to two channels. Supported PCM rates are 8 kHz through 96 kHz and supported sample formats are 16-bit, 20-bit packed, 24-bit packed, 24-bit, and 32-bit little-endian.

## Important APIs, Types, and Functions

Core private state is `struct tscs454`, which stores the `regmap`, three `struct aif` entries, active-stream bit state and mutex, two `struct pll` instances, an internal-rate PLL selection, three `struct coeff_ram` caches, the selected sysclk, sysclk source ID, and BCLK frequency. `struct pll` tracks an ID, user count, and lock. `struct aif` tracks DAI ID, provider/consumer mode, and selected PLL. `struct coeff_ram` stores a 618-byte cache (`COEFF_RAM_SIZE`), a synced flag, and a mutex.

Regmap integration is defined by `tscs454_regmap_cfg` and `tscs454_regmap_range_cfg`. The chip has a paged register map expressed through `VIRT_ADDR()` macros in `tscs454.h`; regmap writes page selection through `R_PAGESEL`. `tscs454_volatile()`, `tscs454_writable()`, `tscs454_readable()`, and `tscs454_precious()` protect coefficient RAM data windows and status registers from unsafe cache behavior.

Probe and registration APIs are `tscs454_i2c_probe()`, `tscs454_probe()`, `soc_component_dev_tscs454`, `tscs454_dais[]`, `tscs454_i2c_driver`, `MODULE_DEVICE_TABLE(i2c/of)`, and `module_i2c_driver()`. The I2C probe allocates state, initializes regmap and private locks, discovers an optional `xtal`, `mclk1`, or `mclk2` clock, resets the chip, applies `tscs454_patch`, syncs the page register, and calls `devm_snd_soc_register_component()`.

DAI operations are collected in `tscs454_dai1_ops` and `tscs454_dai23_ops`: `tscs454_set_sysclk()`, `tscs454_set_bclk_ratio()`, `tscs454_set_dai_fmt()`, `tscs454_dai1_set_tdm_slot()` or `tscs454_dai23_set_tdm_slot()`, `tscs454_hw_params()`, `tscs454_hw_free()`, and `tscs454_prepare()`. Helper functions translate ASoC format/provider flags into TSCS454 register fields: `set_aif_provider_from_fmt()`, `set_aif_format_from_fmt()`, `set_aif_clock_format_from_fmt()`, `set_aif_tdm_delay()`, `set_aif_fs()`, and `set_aif_sample_format()`.

PLL functions include `get_pll_ctl()`, `set_sysclk()`, `reserve_pll()`, `free_pll()`, `pll_connected()`, and `pll_power_event()`. `pll_ctls[]` contains fixed register programming sequences for recognized PLL input rates. `pll_power_event()` enables/disables PLL clock bits through DAPM and flushes coefficient RAM after lock delay on power-up.

Coefficient RAM support uses `init_coeff_ram_cache()`, `coeff_ram_init()`, `bytes_info_ext()`, `coeff_ram_get()`, `coeff_ram_put()`, `write_coeff_ram()`, `coeff_ram_sync()`, and `COEFF_RAM_CTL()`. The driver exposes many byte-array ALSA controls for DAC, Speaker, and Sub filter blocks; each control edits a section of a software cache and writes it to hardware immediately when PLLs are locked.

The large `tscs454_snd_controls[]` array exposes enumerated and TLV controls for PLL BCLK input, internal rate, modular rate, I2S data controls, ASRC routing, headset detection, input boost/PGA/input processor controls, mic bias, ALC/noise gate, digital mic, DAC/speaker/sub polarity, mute, de-emphasis, DC removal, volumes, EQ, MBC, compressor, limiter, expander, bass/treble/3D effects, and coefficient RAM byte blobs.

`tscs454_dapm_widgets[]` and `tscs454_intercon[]` describe power widgets, AIF in/out widgets, input and output muxes, ADC/DAC/ClassD/Sub blocks, PLL supplies, physical inputs, and physical outputs. These arrays are the main integration between ALSA route selection and hardware power sequencing.

## Control Flow

Driver load starts at `tscs454_i2c_probe()`. It allocates `struct tscs454`, initializes regmap and private objects in `tscs454_data_init()`, records client data, selects the first available named clock from `xtal`, `mclk1`, or `mclk2` and otherwise falls back to BCLK, resets the codec with `R_RESET`, marks the regcache dirty, applies startup routing defaults in `tscs454_patch`, writes `R_PAGESEL` to keep the physical page selector aligned, and registers the ASoC component and DAIs.

When the ASoC component probes, `tscs454_probe()` maps `sysclk_src_id` to `R_PLLCTL` input bits. If the PLL source is a real external clock rather than BCLK, it immediately calls `set_sysclk()` to find a matching `pll_ctls[]` entry by `clk_get_rate()` and writes all PLL control registers plus `R_TIMEBASE`. If BCLK is the source, `tscs454_set_sysclk()` later records the DAI-provided BCLK frequency only when the DAI matches the current `PLL BCLK Input` mixer selection.

During stream setup, machine drivers call `.set_fmt`, `.set_bclk_ratio`, and optionally `.set_tdm_slot`. `tscs454_set_dai_fmt()` records whether the codec should be clock provider or consumer, configures I2S/left/right/TDM data format, sets DSP_A/DSP_B delay for TDM modes, and sets BCLK/LRCLK polarity. `tscs454_set_bclk_ratio()` maps ratios 32, 40, and 64 to per-DAI bit-clock multiplier fields. TDM slot setup validates masks against slot count and programs DAI1 for 2/4/6 slots or DAI2/3 for 1/2 slots.

`tscs454_hw_params()` is the main runtime state transition. Under `aifs_status_lock`, it selects a PLL for the DAI based on whether the sample rate divides the 44.1 kHz-family `PLL_44_1K_RATE`, reserves that PLL if this DAI was idle, reserves the internal-rate PLL on the first active stream according to `R_ISRC`, programs sample rate and sample width, and marks the playback or capture bit active in `aifs_status.streams`. `tscs454_prepare()` applies provider/consumer mode immediately before stream start. `tscs454_hw_free()` calls `aif_free()` to clear the stream bit, return the DAI to slave mode when both directions are inactive, and release DAI/internal-rate PLL references when no longer needed.

DAPM evaluates `pll_connected()` to power only PLLs with nonzero users. On `SND_SOC_DAPM_POST_PMU`, `pll_power_event()` enables the relevant PLL clock, sleeps 20 ms for lock, and calls `coeff_ram_sync()` so all dirty coefficient caches are written after the clocks are stable. On `SND_SOC_DAPM_PRE_PMD`, it disables the PLL clock bit before power-down.

Mixer coefficient writes flow through `coeff_ram_put()`. The function chooses DAC, Speaker, or Sub RAM by substring matching the ALSA control name, locks the selected RAM, marks it unsynced, copies user bytes into the cache, locks both PLLs, and if `R_PLLSTAT` is nonzero writes the affected coefficients via `write_coeff_ram()`. `write_coeff_ram()` polls the block status register up to ten times per coefficient address, writes the coefficient address, then bulk-writes three bytes of coefficient data.

## State and Persistence Behavior

Persistent runtime state lives in `struct tscs454`, regmap cache, and the physical codec registers. The driver tracks active streams as two bits per DAI, with `aif_id * 2 + !playback` placing playback and capture into separate bits. This controls PLL user counts and provider reset behavior when the last stream on a DAI closes.

PLL state is reference-counted in software through `users` fields on `pll1` and `pll2`, then projected into DAPM through `pll_connected()`. Hardware PLL programming is static-table driven and depends on the discovered external clock rate or selected BCLK frequency. Coefficient RAM state is intentionally software-cached because the hardware uses indirect write/read windows. The cache starts with normalization values at known addresses, becomes dirty on byte-control writes, and is synced either immediately when PLLs are locked or later at PLL power-up.

The regmap uses `REGCACHE_RBTREE`, volatile declarations for status/read windows, precious declarations for coefficient data windows, and a range config for page selection. Probe reset marks the cache dirty and applies a small patch that assigns default ASRC/audio mux routing, TDM mode, and one virtual page register value. There is no explicit suspend/resume path in this file; persistence across runtime PM would rely on generic regcache behavior and the component/DAPM lifecycle.

## Dependencies and Integration Points

The driver depends on Linux kernel I2C, regmap, clk, mutex, delay, and module infrastructure, plus ALSA SoC headers for component, DAI, DAPM, controls, TLV scales, and PCM parameter helpers. It includes `tscs454.h` for the paged TSCS454 register map and field definitions.

Build integration is through `CONFIG_SND_SOC_TSCS454`, which depends on I2C and selects `REGMAP_I2C`; `Makefile` builds `snd-soc-tscs454.o` from `tscs454.o`. Device binding is via I2C ID `"tscs454"` or device tree compatible `"tempo,tscs454"`. Board integration should provide one of the optional clocks named `xtal`, `mclk1`, or `mclk2`, or configure the codec to use BCLK and call `.set_sysclk` with a supported frequency.

ASoC machine drivers integrate through the three DAI names, stream names, DAI format calls, BCLK ratio and TDM slot calls, and DAPM routes to physical endpoints such as headphones, speakers, line out, line in, digital mics, and sub output. Userspace integration appears as ALSA mixer controls for the large control table and byte controls for DSP/filter coefficient RAM.

## Risks and Edge Cases

`coeff_ram_get()` and `coeff_ram_put()` choose the target RAM by substring matching `kcontrol->id.name` for `"DAC"`, `"Speaker"`, or `"Sub"`. This is fragile: control renames, translated names, or future names containing multiple keywords could route data to the wrong cache. A typed private value would be safer than parsing the display name.

`tscs454_hw_params()` reserves PLL references before all later register writes succeed. If `set_aif_fs()` or `set_aif_sample_format()` fails on a newly inactive DAI or first active stream, the function exits without freeing the PLL reference it just reserved and without marking the stream active. This can leave DAPM seeing phantom PLL users. The valid rate/format constraints make failure uncommon through normal ALSA negotiation, but regmap write failures can still trigger it.

`free_pll()` blindly decrements an unsigned user count. If call ordering becomes unbalanced, underflow would make `pll_connected()` keep a PLL permanently powered. The current call path tries to pair reservations with `hw_free`, but the lack of guards amplifies the partial-failure risk above.

`tscs454_i2c_probe()` falls through to `PLL_INPUT_BCLK` when no named external clock is present and logs `src_names[src]`; `src_names` includes `"bclk"`, so this is intentional. However, BCLK-based PLL programming depends on a later `.set_sysclk` call and a supported BCLK rate. Boards that do not provide either a named clock or a correct BCLK setup will fail when `set_sysclk()` cannot find a PLL table entry.

`write_coeff_ram()` busy-polls with no sleep or timeout based on time; it retries only ten immediate reads. Slow hardware or bus latency could produce false `-EIO` failures. The status test treats any nonzero status as busy and any zero as ready, so it assumes no other status bits are meaningful.

The coefficient RAM `synced` flag is never set true in `coeff_ram_sync()` after a successful full-cache write, unlike the immediate-write path in `coeff_ram_put()`. That means later PLL power-up events may rewrite the full RAM repeatedly. This is safe for correctness but can add avoidable I2C traffic and power-up latency.

The module author string is missing a closing `>` in `MODULE_AUTHOR("Tempo Semiconductor <steven.eckhoff.opensource@gmail.com");`, which is cosmetic but visible in module metadata. Comments also contain minor typos, but they do not affect behavior.

## Test Signals

Build tests should enable `CONFIG_SND_SOC_TSCS454=m` or `y` with I2C and regmap, and should compile with `W=1` to catch signature drift against current ASoC APIs. A probe smoke test should instantiate an I2C device with compatible `"tempo,tscs454"`, verify regmap initialization, reset and patch success, component registration, and presence of the three DAIs and expected mixer controls.

Runtime stream tests should cover playback and capture on all three DAIs, rates 8 kHz, 44.1 kHz, 48 kHz, 88.2 kHz, and 96 kHz, all advertised sample widths, BCLK ratios 32/40/64, DAI provider and consumer modes, polarity combinations, and TDM slot configurations for DAI1 and DAI2/3. Tests should verify PLL user counts return to zero after `hw_free`, especially after injected regmap failures in `hw_params()`.

DAPM tests should route headphone, line out, speaker/ClassD, sub, analog inputs, digital mic, and DAI loop paths, checking that PLL supplies power only when active and coefficient RAM sync occurs after PLL lock. Mixer tests should exercise representative TLV controls and byte coefficient controls for DAC, Speaker, and Sub, then read back software cache contents through the ALSA controls. Fault-injection tests around coefficient RAM status polling, missing clocks, unsupported sysclk/BCLK rates, and regmap write failures would give the strongest signal for the driver’s risk areas.
