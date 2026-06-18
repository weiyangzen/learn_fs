# Research: subset-b-006456

This grouped report covers Realtek ASoC codec drivers under `sources/distributed-fs/ceph-client/sound/soc/codecs/`. Each section is bounded for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt274.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt274.c

## Purpose
`rt274.c` is the Linux ASoC component and I2C driver for the Realtek RT274 audio codec. The device is controlled through HDA-style verb command addresses transported through `rl6347a_hw_read()`/`rl6347a_hw_write()` over I2C and exposed to ALSA as one bidirectional DAI named `rt274-aif1`.

## Important APIs, Types, And Functions
- `struct rt274_priv` owns the regmap, component pointer, I2C client, jack pointer, delayed jack work, system clock configuration, BCLK ratio, and master/slave state.
- `rt274_volatile_register()` and `rt274_readable_register()` define the regmap contract for encoded HDA verbs plus vendor index registers.
- `rt274_jack_detect()`, `rt274_jack_detect_work()`, `rt274_mic_detect()`, and `rt274_irq()` implement headphone/microphone reporting through `snd_soc_jack_report()`.
- `rt274_hw_params()`, `rt274_set_dai_fmt()`, `rt274_set_dai_sysclk()`, `rt274_set_dai_pll()`, `rt274_set_bclk_ratio()`, and `rt274_set_tdm_slot()` are the DAI operations.
- `rt274_set_bias_level()`, `rt274_suspend()`, and `rt274_resume()` manage power-state verbs and regcache restoration.
- `rt274_i2c_probe()` allocates state, verifies `RT274_VENDOR_ID`, resets and calibrates the codec, programs pins/unsolicited jack events, requests IRQ, and registers the component.

## Control Flow
Probe initializes an uncached HDA-verb regmap, checks the vendor ID through `RT274_GET_PARAM()`, copies default vendor-index cache values, resets the codec, applies pad, coefficient, combo-jack, HP DC calibration, pin widget, I2S, and IRQ setup writes, then registers the ASoC component. Component probe stores the component pointer and schedules an initial jack-detect work item if an IRQ exists. Runtime PCM setup validates 44.1/48 kHz rates against the selected system clock family, encodes channel count and sample width into DAC/ADC stream format verbs, and updates I2S data and channel length fields. Jack IRQ clears the IRQ bit, reads HP and MIC pin sense verbs, reports ALSA jack status, and triggers a short wakeup event.

## State And Persistence
Persistent runtime state is in `rt274_priv`: `sys_clk`, `clk_id`, `fs`, and `master` affect later format/PLL choices; `jack` controls reporting; `index_cache` mirrors vendor index defaults. On suspend the driver switches regmap to cache-only and marks it dirty. Resume disables cache-only mode, writes each index-cache entry back with `rt274_index_sync()`, then syncs the regmap defaults.

## Dependencies And Integration Points
The driver integrates with ASoC component, DAI, DAPM, TLV controls, I2C, ACPI/OF matching, IRQ threading, workqueues, PM regcache, and Realtek `rl6347a` HDA-verb transport. DAPM exposes DMIC, MIC/LINE inputs, ADC muxes, two DAC paths, headphone output, line out, and SPDIF-related pin nodes.

## Risks
- Most hardware setup is magic-register sequencing; mistakes in undocumented coefficients, sleep timing, or pin setup can break jack detection or produce pops.
- `rt274_set_dai_pll()` depends on `rt274->fs` previously set by `set_bclk_ratio()`; missing machine-driver calls can select fallback values.
- Only 44.1/48 kHz rates are accepted, and clock/rate families must match exactly.
- IRQ handling assumes `rt274->jack` has been set before reports; platform wiring without jack registration may produce lost status updates.

## Test Signals
Useful tests include I2C probe/vendor-ID success, component registration, `aplay`/`arecord` at 44.1 and 48 kHz with all supported sample widths, DAPM path toggling for HP/line/DMIC/MIC routes, suspend/resume with regcache sync, IRQ-driven jack plug/unplug reports, TDM 2/4-slot setup, and failure-path checks for invalid sysclk, rate, channel count, and sample width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt274.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt274.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt274.h

## Purpose
`rt274.h` defines the RT274 register vocabulary used by `rt274.c`: HDA node IDs, verb-construction macros, encoded register addresses, vendor index registers, bit masks, clock selectors, PLL selectors, and DAI IDs.

## Important APIs, Types, And Functions
- `VERB_CMD(V, N, D)` encodes an HDA verb, node ID, and payload into the 32-bit regmap address space.
- `RT274_*` node constants describe audio function group, DACs, ADCs, DMICs, analog pins, line out, SPDIF, HP out, mixers, vendor registers, and inline command node.
- Encoded verb macros such as `RT274_SET_AUDIO_POWER`, `RT274_DAC_FORMAT`, `RT274_ADC_FORMAT`, `RT274_GET_HP_SENSE`, and `RT274_UNSOLICITED_HP_OUT` are the symbolic API consumed by the C driver.
- Index register constants (`RT274_I2S_CTRL1`, `RT274_MCLK_CTRL`, `RT274_PLL2_CTRL`, etc.) and masks define the vendor coefficient window used by regmap updates.
- Enumerations identify `RT274_AIF1` and clock/PLL source IDs.

## Control Flow
The header itself has no executable control flow; its macros determine how the C driver maps ALSA operations to register writes. DAI format, clock, PLL, TDM, jack, pin-power, and stream-format operations all flow through these symbolic constants.

## State And Persistence
There is no storage in the header. Persistence concerns are indirect: the defined index registers are cached in `rt274_index_def` and restored on resume, while verb macros are used as regmap keys for cached/default HDA verb state.

## Dependencies And Integration Points
The macros depend on HDA verb constants such as `AC_VERB_SET_POWER_STATE`, `AC_VERB_SET_STREAM_FORMAT`, and `AC_VERB_GET_PIN_SENSE` being available through the included sound headers in the C file. The DAI ID enum must match the DAI array in `rt274.c`.

## Risks
- Because `VERB_CMD()` is purely arithmetic, wrong node IDs or payload bits silently target different hardware functions.
- Several constants encode hardware policy, including pin default and unsolicited response programming; reuse across variants would be risky.
- Bit masks such as TDM and clock-source fields must stay aligned with the vendor index register definitions in the datasheet.

## Test Signals
Compile coverage is the primary signal: every macro referenced by `rt274.c` must resolve. Runtime tests should verify each macro-backed path: power state, HP/MIC sense, stream format, I2S format, TDM, and PLL/BCLK source selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt274.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt286.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt286.c

## Purpose
`rt286.c` is the ASoC I2C codec driver for Realtek RT286/RT288. Like RT274, it uses HDA-style encoded verbs over the `rl6347a` transport, but it exposes two DAIs, speaker/headphone paths, analog input mixing, platform-data/DMI-driven combo-jack handling, and special Dell RT288 GPIO handling.

## Important APIs, Types, And Functions
- `struct rt286_priv` stores regmap/component/I2C pointers, `struct rt286_platform_data`, jack state, delayed work, and clock state.
- `rt286_jack_detect()` is the central control path for HP/MIC detection. It supports plain pin-sense mode and combo-jack impedance-detect mode.
- DAPM events `rt286_spk_event()`, `rt286_set_dmic1_event()`, `rt286_ldo2_event()`, and `rt286_mic1_event()` sequence EAPD, DMIC pins, LDO2, and microphone bias.
- DAI operations set sample format/rate, master/slave mode, I2S/DSP framing, sysclk, and BCLK ratio.
- `rt286_i2c_probe()` verifies RT286 or RT288 vendor IDs, restores defaults, applies quirks, configures power, combo jack, DMIC/GPIO2 behavior, depop values, optional Dell GPIO, IRQ, and component registration.

## Control Flow
Probe allocates state and regmap, reads vendor ID, copies and writes vendor index defaults plus HDA verb defaults, imports platform data, applies DMI combo-jack overrides, powers the function group down to D3 while setting individual nodes to D1, programs combo-jack or discrete mic detection, configures DMIC2/GPIO2, depop, and optional RT288 Dell GPIO registers, then requests an IRQ and registers two DAI instances. At component probe it schedules a short delayed jack-detect pass. ALSA set-jack enables or disables IRQ reporting and may force `LDO1` when HP is already present. DAI `hw_params` validates 44.1/48 kHz, sysclk family, channels up to 16, and supported sample widths, then writes stream format and I2S length fields.

## State And Persistence
State persists in platform data flags (`cbj_en`, `gpio2_en`), current sysclk/clock source, the jack pointer, and DAPM forced pins during combo-jack detection. PM uses cache-only regmap mode during suspend and replays `index_cache` plus regcache on resume. Probe resets hardware to driver defaults, so no user-space mixer state survives a full reprobe except through ALSA restore tooling.

## Dependencies And Integration Points
The driver depends on ASoC component/DAI/DAPM APIs, `sound/rt286.h` platform data, I2C, ACPI matching (`10EC0286`, `INT343A`), DMI quirk tables, Realtek `rl6347a` register transport, threaded IRQ, workqueues, and PM regcache. It integrates with machine drivers through `set_jack`, two DAIs (`rt286-aif1`, `rt286-aif2`), and platform data or DMI for combo-jack policy.

## Risks
- Combo-jack detection is timing-sensitive and forces DAPM supplies while probing CBJ registers; race or sleep-time changes can misclassify headset microphones.
- Quirk coverage is platform-specific. Missing DMI or platform data can choose the wrong jack mode or GPIO2/DMIC2 behavior.
- PLL/sysclk support is constrained to 19.2/24/11.2896/12.288/22.5792/24.576 MHz families and 44.1/48 kHz rates.
- `rt286_mic_detect()` sends an initial report using existing jack status, not a fresh hardware read.

## Test Signals
Test vendor-ID matching for RT286 and RT288, both DAI playback/capture paths, HP and speaker DAPM routes, discrete and combo-jack detection, DMI quirk platforms, suspend/resume register restoration, GPIO2/DMIC2 variants, invalid clock/rate cases, and speaker EAPD transition on DAPM power changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt286.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt286.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt286.h

## Purpose
`rt286.h` defines RT286/RT288 HDA node IDs, encoded verb registers, vendor index registers, bit fields, clock source values, and DAI IDs used by the RT286 codec driver.

## Important APIs, Types, And Functions
- `VERB_CMD()` maps HDA verb/node/data tuples into regmap keys.
- Verb macros cover audio power, node power, speaker/headphone muxes, ADC muxes, pin widgets, EAPD, amplifier gains, GPIO access, stream formats, coefficient index/data, and jack sense.
- Index register definitions cover analog bias, power, I2S, clock divider, DC gain, mic detect, GPIO, IRQ, PLL, combo-jack, and depop controls.
- Bit-field macros define SPDIF selection, record/front mixer mute bits, HP/SPK mux selection, ADC mux values, and sysclk source IDs.
- The enum declares `RT286_AIF1`, `RT286_AIF2`, and sentinel `RT286_AIFS`.

## Control Flow
No code executes here. The C driver uses these definitions to implement probe defaults, DAPM routing, jack detection, DAI format setup, clock setup, and PM register replay.

## State And Persistence
The header stores no runtime state. It defines the register addresses whose values are cached by regmap defaults and by `rt286_index_def`, which is replayed after suspend.

## Dependencies And Integration Points
The constants integrate with Linux HDA verb definitions, ASoC DAI IDs, and machine-driver clock selectors. GPIO verb macros are used only in the RT288 Dell quirk path.

## Risks
- Misencoded verb constants can affect unrelated HDA widgets.
- ADC mux value names in the header are broader than the subset exposed by the C driver's value enum; extending controls requires checking hardware values.
- Shared-looking RT286/RT298 constants are not guaranteed interchangeable.

## Test Signals
Compile the driver with all macro references, exercise DAI IDs through machine driver links, validate GPIO quirk writes on RT288/Dell hardware, and test each mux/volume path exposed through ALSA controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt286.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt298.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt298.c

## Purpose
`rt298.c` is the ASoC I2C driver for Realtek RT298. It is another HDA-verb-based codec driver using `rl6347a`, with two DAIs, speaker/headphone outputs, ADC/record mixers, combo-jack support, unsolicited response programming, and additional analog supply/filter handling compared with RT286.

## Important APIs, Types, And Functions
- `struct rt298_priv` stores regmap/component/platform-data/I2C/jack/work state, sysclk/clk ID, and `is_hp_in` cache for duplicate jack-event suppression.
- `rt298_jack_detect()` handles discrete pin sense or combo-jack detection, powers HV/VREF/LDO supplies during detection, and suppresses unchanged combo HP events.
- `rt298_adc_event()` unmutes/mutes ADC gain and resets ADC digital filters when MCLK is absent.
- `rt298_mic_detect()`, `rt298_irq()`, and delayed work connect hardware IRQs to ALSA jack reports.
- `rt298_i2c_probe()` verifies `RT298_VENDOR_ID`, restores defaults, applies platform/ACPI/DMI combo-jack data, programs VREF, DMIC/GPIO behavior, wind filter, unsolicited responses, IRQ flags, and registers the component.

## Control Flow
Probe initializes regmap, verifies vendor ID, writes both index and verb defaults, imports platform or ACPI driver data, forces combo-jack mode for selected Intel reference platforms, applies VREF charging and power-state setup, configures combo or discrete mic detection, sets DMIC2 default according to GPIO2, enables wind filter and unsolicited responses, and requests a threaded IRQ. Component probe schedules an initial delayed detection after 1250 ms. DAI operations mirror RT286: 44.1/48 kHz only, channel count up to 16, 8/16/20/24/32-bit stream-width encoding, I2S/left-justified/DSP A/B modes, sysclk source selection, and BCLK ratio handling.

## State And Persistence
`is_hp_in` persists last combo-jack HP state and is reset on suspend. `pdata.cbj_en` and `pdata.gpio2_en` select jack and pin behavior. Regcache is marked dirty during suspend; resume replays `rt298_index_def` and cached regmap values. Jack detection temporarily forces DAPM supplies and releases them based on detected HP/MIC state.

## Dependencies And Integration Points
The driver integrates with ASoC controls/DAPM/two DAIs, `sound/rt298.h` platform data, ACPI IDs `10EC0298` and `INT343A`, DMI quirk tables, I2C, threaded IRQ, wakeup events, regcache PM, and `rl6347a` transport. Machine drivers provide jack registration and DAI clock/format configuration.

## Risks
- Combo-jack detection has long sleeps and state suppression; stale `is_hp_in` can hide reports if not reset after suspend or reconfiguration.
- `rt298_i2c_probe()` stores `regmap_read()` data in `ret` and does not separately check I2C read failure before comparing the vendor value.
- ADC filter reset is conditional on `RT298_VAD_CTRL` MCLK state and uses fixed delays.
- Platform-specific combo-jack and GPIO2 policy may be wrong without DMI/ACPI data.

## Test Signals
Test vendor-ID probe, two-DAI playback/capture, speaker EAPD, HP and MIC combo detection with repeated plug/unplug cycles, unsolicited IRQ handling, suspend/resume jack re-detection, MCLK-absent ADC filter reset, DMI-forced combo mode, and invalid sysclk/rate/format cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt298.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt298.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt298.h

## Purpose
`rt298.h` provides symbolic register definitions for the RT298 codec driver: HDA node IDs, encoded verbs, vendor index registers, masks, mux values, clock source IDs, and DAI identifiers.

## Important APIs, Types, And Functions
- `VERB_CMD()` creates the 32-bit HDA-verb regmap addresses used by the driver.
- Verb macros include power, pin widgets, SPDIF/digital converter, EAPD, amp gains, ADC/DAC formats, coefficient access, jack sense, and unsolicited response enable commands.
- Index register constants include digital filter, power, I2S, clock divider, DC gain, mic detect, IRQ, wind filter, VAD, combo-jack, PLL, depop, and IRQ flag controls.
- Bit masks define record/front mixer routes, HP/SPK muxes, ADC source values, and system clock selection.
- DAI enum declares `RT298_AIF1`, `RT298_AIF2`, and `RT298_AIFS`.

## Control Flow
The header defines the register map consumed by `rt298.c`; DAPM widgets, jack detection, DAI setup, and probe defaults all depend on these constants.

## State And Persistence
There is no header-local state. Constants identify registers that are either in regmap defaults or in the vendor index cache restored after PM resume.

## Dependencies And Integration Points
The constants depend on Linux HDA verb definitions available through sound headers in the C file. They align with `sound/rt298.h` platform data and with the RT298 DAI array.

## Risks
- RT298 resembles RT286, but additional registers like `RT298_VAD_CTRL`, `RT298_WIND_FILTER_CTRL`, and unsolicited response controls make blind sharing unsafe.
- The header exposes many hardware mux values that the C driver only partly surfaces.
- Any wrong bit shift in clock or mux fields changes hardware routing silently.

## Test Signals
Compile all macro references, validate ALSA controls using the encoded gain and mux registers, exercise unsolicited jack enable paths, and verify DAI IDs and clock selectors from machine-driver configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt298.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.c

## Purpose
`rt5514-spi.c` is the SPI-side companion driver for RT5514. It exports burst SPI read/write helpers used by the RT5514 I2C codec driver to load DSP firmware and read calibration data, and it registers a simple ASoC CPU DAI/component that captures mono 16 kHz DSP voice-buffer audio by periodically copying from the DSP ring buffer over SPI.

## Important APIs, Types, And Functions
- Global `static struct spi_device *rt5514_spi` is the transport target for exported helpers.
- `struct rt5514_dsp` stores the component device, delayed copy work, DMA mutex, current PCM substream, DSP ring addresses, byte counters, and DMA offset.
- `rt5514_spi_burst_read()` and `rt5514_spi_burst_write()` are exported GPL symbols for the I2C codec driver and firmware loader paths.
- `rt5514_schedule_copy()`, `rt5514_spi_copy_work()`, and `rt5514_spi_irq()` implement the DSP-buffer-to-PCM flow.
- ASoC callbacks `open`, `hw_params`, `hw_free`, `pointer`, `pcm_new`, and component probe expose the vmalloc-backed capture PCM.

## Control Flow
SPI probe records the SPI device globally and registers an ASoC component and CPU DAI named `rt5514-dsp-cpu-dai`. Component probe allocates `rt5514_dsp`, initializes work and mutex, and requests an optional rising-edge threaded IRQ. When IRQ fires or `hw_params` notices a pending IRQ status bit, `rt5514_schedule_copy()` reads DSP voice buffer base/limit/write pointer, aligns the read pointer, computes buffer size, and schedules copy work. Copy work waits until enough DSP data is available, reads one ALSA period over SPI, handles ring wrap, advances DMA offset, calls `snd_pcm_period_elapsed()`, and reschedules itself every 5 jiffies.

## State And Persistence
The SPI driver keeps global device state in `rt5514_spi` and per-component stream state in `rt5514_dsp`. The DSP ring read pointer is host-maintained in `buf_rp`; the write pointer is read from DSP memory. Suspend enables IRQ wake if allowed; resume disables IRQ wake and restarts copying if a substream is active and IRQ status is pending. No firmware is stored here, but write helpers transfer firmware bytes supplied by `rt5514.c`.

## Dependencies And Integration Points
The driver depends on SPI core, ASoC component/PCM/DAI APIs, delayed work, mutexes, IRQ wake, and the address/command definitions in `rt5514-spi.h`. It integrates with `rt5514.c` through exported burst helpers and with a machine driver through the `rt5514-dsp-cpu-dai` capture DAI.

## Risks
- `rt5514_spi` is a single global pointer; multiple devices are not supported safely.
- Burst helpers assume `len` is a multiple of 8, but callers are responsible for padding. RT5514 firmware writes round up in the caller.
- `rt5514_spi_burst_write()` ignores `spi_write()` return values and still returns 0 after transfer attempts.
- Copy work uses periodic polling and host-side ring bookkeeping, so underrun/overrun behavior depends on IRQ timing, period size, and SPI throughput.
- `rt5514_spi_burst_read()` returns `false` on SPI error despite `int` return type.

## Test Signals
Test SPI probe and component registration, exported burst read/write with 8-byte-aligned lengths, firmware loading from the I2C driver, IRQ-triggered and `hw_params`-triggered capture start, ring wrap copying, ALSA pointer movement, `snd_pcm_period_elapsed()` cadence, suspend/resume wake behavior, and negative SPI-transfer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.h

## Purpose
`rt5514-spi.h` defines the SPI command constants, DSP buffer addresses, IRQ bit, transfer chunk size, and exported burst helper prototypes for the RT5514 SPI companion driver.

## Important APIs, Types, And Functions
- `RT5514_SPI_BUF_LEN` caps SPI burst chunks at 240 bytes.
- `RT5514_BUFFER_VOICE_BASE`, `RT5514_BUFFER_VOICE_LIMIT`, and `RT5514_BUFFER_VOICE_WP` identify DSP memory locations used to stream captured voice data.
- `RT5514_IRQ_CTRL` and `RT5514_IRQ_STATUS_BIT` identify the DSP IRQ status register/bit.
- The SPI command enum includes 16-bit, 32-bit, burst read, and burst write command IDs.
- `rt5514_spi_burst_read()` and `rt5514_spi_burst_write()` are the cross-file API consumed by `rt5514.c`.

## Control Flow
No executable flow exists in the header. The constants drive firmware writes, calibration reads, IRQ-status reads, and DSP capture ring-buffer reads.

## State And Persistence
The header has no storage. Its buffer-address constants point to persistent DSP-side state used while firmware is running.

## Dependencies And Integration Points
The API requires the SPI driver to be built when `rt5514.c` enables DSP firmware loading. The prototypes are guarded only by the header; availability at link time depends on `CONFIG_SND_SOC_RT5514_SPI`.

## Risks
- Callers must honor the documented 8-byte multiple requirement; the header does not encode that in types.
- Address constants are tightly coupled to the RT5514 DSP firmware ABI.
- `RT5514_SPI_BUF_LEN` must match what the SPI master and device protocol tolerate.

## Test Signals
Compile/link tests with and without `CONFIG_SND_SOC_RT5514_SPI`, firmware load tests that call both exported helpers, and DSP capture tests that validate the voice buffer addresses and IRQ status bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514.c

## Purpose
`rt5514.c` is the main ASoC I2C codec driver for Realtek RT5514, a capture-oriented codec/DSP device. It exposes a four-channel capture DAI, analog/DMIC capture paths, optional PLL and TDM support, and a user control that loads/runs DSP voice-wake firmware using the SPI companion driver when available.

## Important APIs, Types, And Functions
- `struct rt5514_priv` is defined in `rt5514.h` and stores platform data, component, raw I2C regmap, cached component regmap, clocks, sysclk/lrck/bclk/PLL state, DSP enable state, and PLL3 calibration value.
- `rt5514_i2c_read()`/`rt5514_i2c_write()` implement a cached 16-bit component regmap by forwarding to the 32-bit raw I2C map with `RT5514_DSP_MAPPING`.
- `rt5514_dsp_voice_wake_up_get()`/`put()` expose the `DSP Voice Wake Up` ALSA control and run the firmware/calibration sequence.
- `rt5514_calibration()` and `rt5514_enable_dsp_prepare()` sequence PLL3 calibration and DSP preparation registers.
- `rt5514_calc_dmic_clk()` and `rt5514_set_dmic_clk()` choose a DMIC divider that keeps DMIC clock between roughly 1 and 3.072 MHz.
- DAI operations cover `hw_params`, DAI format, sysclk, PLL, and TDM slot setup.
- `rt5514_i2c_probe()` verifies device ID, applies raw I2C patches and regmap patches, and registers the component.

## Control Flow
I2C probe allocates state, imports platform data or device properties, creates a raw 32-bit I2C regmap and a cached 16-bit component regmap, retries device-ID read once for possible I2C-glitch recovery, applies an I2C patch sequence, registers a normal regmap patch, and registers the capture component. Component probe obtains optional `mclk` and optional DSP calibration clock and initializes `pll3_cal_value`. Runtime DAPM routes select DMIC or AMIC input paths into stereo ADC mixers and AIF1 capture. DAI `hw_params` computes pre-divider from sysclk/lrck, computes BCLK from frame size, sets sample length, ADC clock divider, system divider, and OSR. DSP wake-up can only change while DAPM bias is off; enabling may calibrate PLL3, load two firmware blobs over SPI, start DSP run, and write calibration; disabling reapplies the normal patch and syncs regcache.

## State And Persistence
Clock state (`sysclk`, `sysclk_src`, `pll_*`, `lrck`, `bclk`) persists across DAI callbacks. `dsp_enabled` gates the firmware mode and is forcibly cleared in `set_bias_level()` when moving from OFF to STANDBY before normal recording. `pll3_cal_value` persists the measured calibration value with a default fallback. The component regmap is cached; the raw I2C regmap is not cached. Resume performs a bogus vendor-ID read to recover from possible I2C bus glitch confusion.

## Dependencies And Integration Points
The driver depends on I2C, regmap, ASoC component/DAI/DAPM/TLV APIs, firmware loading, optional clocks, device properties (`realtek,dmic-init-delay-ms`, `realtek,dsp-calib-clk-name`, `realtek,dsp-calib-clk-rate`), OF/ACPI matching, `rl6231` PLL/clock helpers, and optional `rt5514-spi` exported helpers. It exposes one capture DAI, `rt5514-aif1`.

## Risks
- DSP firmware loading silently continues if firmware blobs are missing; wake-up control still returns changed state after partial paths unless hardware behavior fails later.
- SPI support is conditional. Without `CONFIG_SND_SOC_RT5514_SPI`, DSP loading/calibration paths log errors and cannot actually transfer firmware.
- The DSP enable/disable path only acts when bias is OFF, so user-space control changes during active capture do not reprogram hardware immediately.
- TDM slot handling accepts unspecified/default masks and slot widths without rejecting all invalid combinations.
- The I2C patch includes sentinel-looking register `0xfafafafa` for bypass mode; incorrect ordering can break access mode.

## Test Signals
Test I2C probe with first-read failure retry, device property parsing, regmap patch application, AMIC/DMIC capture routing, 8 kHz to 192 kHz capture rates, DAI format and PLL sources, TDM masks/slots, DMIC clock divider bounds, DSP voice wake-up enable/disable with firmware present and absent, SPI-enabled and SPI-disabled builds, bias transitions that clear DSP mode, and suspend/resume I2C recovery read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514.h

## Purpose
`rt5514.h` defines the register map, bit fields, firmware names, clock/PLL enums, and private driver state for the RT5514 codec/DSP driver.

## Important APIs, Types, And Functions
- Register constants cover reset, analog/digital power, I2S, VAD, DMIC, digital sources, sample-rate conversion, PLL, delay buffer, ADC downfilters, analog controls, DSP controls, and vendor IDs.
- `RT5514_DSP_MAPPING` is the high-address offset used to access codec registers through the raw I2C map.
- Bit masks define analog power supplies, I2S/TDM format, docking slots, DMIC input selection, PLL source and coefficients, clock dividers, ADC mixer bits, gains, and PLL bypass bits.
- `RT5514_FIRMWARE1` and `RT5514_FIRMWARE2` name firmware blobs requested by `rt5514.c`.
- Enums define system clock sources (`MCLK`, `PLL1`) and PLL1 sources (`MCLK`, `BCLK`).
- `struct rt5514_priv` is the central state object for platform data, component, regmaps, clocks, clock rates, PLL state, DSP state, and PLL3 calibration.

## Control Flow
There is no executable control flow in the header. Its constants determine how DAPM events, DAI callbacks, firmware loading, calibration, and regmap access are encoded in `rt5514.c`.

## State And Persistence
The header defines `struct rt5514_priv`; the fields persist runtime clock, PLL, and DSP settings across callbacks. Register constants identify values cached in `rt5514_reg` and restored by regcache.

## Dependencies And Integration Points
The header includes `<linux/clk.h>` and `<sound/rt5514.h>` for clock handles and platform data. Its firmware names must match files installed in the kernel firmware search path. Its enums are used by machine drivers through DAI ops.

## Risks
- The register map mixes normal 16-bit component addresses with raw mapped addresses; forgetting `RT5514_DSP_MAPPING` in raw access paths would hit wrong locations.
- Firmware filenames are fixed ABI with user-space firmware packaging.
- The private struct couples codec and DSP state, so power-management and voice-wake changes can affect normal capture paths.

## Test Signals
Compile coverage for all register constants, firmware-load tests confirming both firmware names, DAI sysclk/PLL enum use from machine drivers, and regmap read/write tests through both normal and `RT5514_DSP_MAPPING` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.c

## Purpose
`rt5575-spi.c` is a minimal SPI firmware-loader helper for the Realtek ALC5575/RT5575 DSP codec. It discovers or creates an SPI device from the I2C device-tree node, then loads four firmware images to fixed DSP memory addresses using a packed burst-write protocol.

## Important APIs, Types, And Functions
- `struct rt5575_spi_burst_write` describes the packed SPI write frame: command byte, little-endian address, 240-byte payload, and dummy byte.
- `rt5575_spi_get_device()` parses `spi-parent` phandle and optional chip-select index from the codec node, finds the SPI controller, validates chip select, and creates a new SPI device with modalias `rt5575`.
- `rt5575_spi_burst_write()` chunks firmware into 240-byte writes and sends each frame with `spi_write()`.
- `rt5575_spi_fw_load()` requests four firmware files and writes them to fixed addresses.

## Control Flow
The I2C driver calls `rt5575_spi_get_device()` when the boot register reports SPI boot mode. After obtaining a device, it calls `rt5575_spi_fw_load()`. Firmware load iterates over four path/address pairs, requests each blob, burst-writes it, and releases it before moving to the next blob.

## State And Persistence
This file has no long-lived private state. It dynamically creates an SPI device and transfers firmware; firmware execution state is controlled by `rt5575.c` through DSP/I2C registers after loading.

## Dependencies And Integration Points
The helper depends on firmware loader, OF device-tree APIs, SPI core, and `rt5575-spi.h`. It is called by `rt5575.c` only when `CONFIG_SND_SOC_RT5575_SPI` is enabled through the header stubs.

## Risks
- `rt5575_spi_burst_write()` always writes `sizeof(buf)`, so the last short chunk sends stale/zero-padded bytes for the unused payload portion.
- `spi_write()` return values are ignored; firmware load can report success despite SPI transfer failures.
- `spi_new_device()` creates a device but no local cleanup path is visible here if later firmware loading fails.
- The `spi-parent` property uses phandle index 0 and chip-select index 1, which is unusual and must be documented in bindings elsewhere.

## Test Signals
Test device-tree parsing with and without explicit chip select, invalid chip-select rejection, missing SPI controller, missing firmware files, all four firmware writes to expected addresses, SPI write failure injection, and integration with `rt5575_i2c_probe()` in SPI boot mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.h

## Purpose
`rt5575-spi.h` declares the optional RT5575 SPI firmware-loading API and provides stubs when the SPI helper is not built.

## Important APIs, Types, And Functions
- When `CONFIG_SND_SOC_RT5575_SPI` is enabled, it declares `rt5575_spi_get_device()` and `rt5575_spi_fw_load()`.
- When disabled, inline stubs return `NULL` and `-EINVAL`, allowing `rt5575.c` to compile while reporting unsupported SPI boot mode.

## Control Flow
The header selects real functions or stubs at compile time. `rt5575.c` first checks `IS_ENABLED(CONFIG_SND_SOC_RT5575_SPI)` before using the helper, then still calls through this API.

## State And Persistence
The header owns no state. It controls whether SPI firmware loading can be reached.

## Dependencies And Integration Points
The declarations require `struct device` and `struct spi_device` types from included kernel headers in users of the header. It is the integration seam between the I2C codec driver and SPI firmware loader.

## Risks
- Because the disabled stubs compile, runtime SPI boot support depends on the explicit config check in `rt5575.c`.
- No ownership contract for the returned `spi_device` is documented in the header.

## Test Signals
Build with `CONFIG_SND_SOC_RT5575_SPI=y/m` and disabled, verify `rt5575.c` compiles in both cases, and test SPI-boot probe behavior for both real and stubbed helper paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575.c

## Purpose
`rt5575.c` is the ASoC I2C component driver for Realtek ALC5575/RT5575. It exposes four symmetric AIFs with simple input/output DAPM routes and mixer/volume controls, verifies the device ID, optionally loads DSP firmware over SPI when the boot mode requires it, and reports a private EFUSE ID at component probe.

## Important APIs, Types, And Functions
- `struct rt5575_priv` stores I2C client, ASoC component, raw DSP regmap, and component regmap.
- `rt5575_readable_register()` whitelists visible component registers.
- `rt5575_get_priv_id()` reads EFUSE private ID words by programming `RT5575_EFUSE_PID`.
- `rt5575_i2c_read()`/`rt5575_i2c_write()` forward 16-bit component regmap accesses to the 32-bit DSP regmap with `RT5575_DSP_MAPPING`.
- `rt5575_fw_load_by_spi()` sets DSP bus/boot registers, calls the SPI helper to load firmware, releases reset, triggers `RT5575_SW_INT`, and polls for completion.
- `rt5575_i2c_probe()` allocates regmaps, validates `RT5575_DEVICE_ID`, handles SPI boot mode, and registers the component.

## Control Flow
Probe creates a raw 32-bit `dsp_regmap` and a 16-bit logical regmap, reads `RT5575_ID`, then reads `RT5575_BOOT`. If boot bits equal `RT5575_BOOT_SPI`, it requires `CONFIG_SND_SOC_RT5575_SPI` and performs the SPI firmware sequence. After firmware is running or when SPI boot is not required, it registers the component with four DAIs. Component probe saves the component pointer and logs EFUSE private ID. DAPM routes all four AIF captures from `INPUT` and all four AIF playbacks to `OUTPUT`; no complex power graph is modeled.

## State And Persistence
Runtime state is limited to regmap pointers and component pointer. Firmware execution state is in the DSP and controlled through registers. Mixer and volume values are direct DSP/component registers. No suspend/resume callbacks or regcache persistence are defined in this file.

## Dependencies And Integration Points
The driver depends on I2C, regmap, ASoC component/DAI/DAPM/TLV APIs, OF matching (`realtek,rt5575`), and the optional SPI helper. It expects firmware paths and SPI topology to be provided outside this file when SPI boot is selected.

## Risks
- SPI firmware load failure collapses to `-ENODEV`, obscuring the original error.
- `regmap_read_poll_timeout()` return is stored in `ret`, which also receives register values during polling; behavior depends on macro semantics and should be reviewed carefully.
- The DAPM graph is intentionally generic, so it may not model actual internal power sequencing.
- No PM hooks are present; low-power and firmware-state recovery depend on wider system behavior.

## Test Signals
Test I2C ID verification, non-SPI boot registration, SPI boot with helper enabled/disabled, four firmware blobs loaded and `SW_INT` clearing, EFUSE private ID logging, all four DAIs at 8 kHz to 192 kHz and supported sample widths, ALSA volume/switch controls, and missing/invalid firmware failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575.h

## Purpose
`rt5575.h` defines the RT5575 device ID, DSP mapping offset, logical register addresses, boot-mode bits, DAI IDs, and private state structure used by `rt5575.c`.

## Important APIs, Types, And Functions
- `RT5575_DEVICE_ID` is the expected ID read during probe.
- `RT5575_DSP_MAPPING` offsets logical accesses into DSP address space.
- Register constants cover boot, IDs, mixer/prompt/speaker/mic volumes, WNC/mode/I2S/sleep/algorithm/pinmux/GPIO/DSP bus, software interrupt, boot error, DSP ready/command, and EFUSE registers.
- `RT5575_BOOT_MASK` and `RT5575_BOOT_SPI` select firmware-loading behavior.
- DAI enum defines `RT5575_AIF1` through `RT5575_AIF4` plus sentinel.
- `struct rt5575_priv` holds the I2C client, component pointer, and two regmaps.

## Control Flow
The header itself does not execute. Probe, firmware loading, EFUSE reads, controls, and DAI registration in `rt5575.c` depend on these constants.

## State And Persistence
The private struct fields persist per-device driver state. Register constants identify DSP-side persistent state such as boot mode, firmware readiness, and volume controls.

## Dependencies And Integration Points
The DAI IDs must match the four-entry DAI array in `rt5575.c`. `RT5575_DSP_MAPPING` must match the address protocol used by both I2C and SPI firmware loading.

## Risks
- Register names are sparse and high-level; missing bit masks can encourage open-coded magic values in the C file.
- Boot mode only defines the SPI case, so future boot modes need explicit constants before safe handling.
- The private struct has no locking fields, so concurrent future operations would need additional synchronization.

## Test Signals
Compile all users, verify ID and boot register constants against hardware, confirm DAI enum alignment, and test mapped regmap reads/writes for volume and firmware-control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5616.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5616.c

## Purpose
`rt5616.c` is the ASoC I2C codec driver for Realtek RT5616, a stereo analog codec with microphone inputs, ADC/DAC paths, headphone and line outputs, private-register paging, PLL support, depop sequencing, and one bidirectional DAI.

## Important APIs, Types, And Functions
- `struct rt5616_priv` stores component/regmap, optional MCLK, sysclk source/rate, per-DAI LRCK/BCLK/master state, and PLL source/input/output state.
- `rt5616_ranges` maps private registers through `RT5616_PRIV_INDEX`/`RT5616_PRIV_DATA` into regmap range space.
- `rt5616_volatile_register()` and `rt5616_readable_register()` define cached register behavior including private ranges.
- DAPM events `rt5616_adc_event()`, `rt5616_charge_pump_event()`, `rt5616_hp_event()`, `rt5616_lout_event()`, `rt5616_bst1_event()`, and `rt5616_bst2_event()` sequence mute, depop, charge pump, amps, and boost op stages.
- DAI ops `rt5616_hw_params()`, `rt5616_set_dai_fmt()`, `rt5616_set_dai_sysclk()`, and `rt5616_set_dai_pll()` configure sample format and clocks using `rl6231` helpers.
- `rt5616_i2c_probe()` verifies ID, resets hardware, powers reference blocks, applies a private-register init patch, sets LDO voltage, and registers the component.
- `rt5616_i2c_shutdown()` mutes HP and line outputs.

## Control Flow
Probe allocates state, creates an 8-bit/16-bit regmap with private-register range support, validates device ID `0x6281`, resets the codec, powers VREF/MB/BG blocks, applies `init_list` private-register patch, sets LDO output to 1.2 V, and registers the ASoC component. Component probe obtains optional `mclk`. DAPM describes input boosts, record mixers, ADCs, digital interface, DAC mixers, output mixers, headphone/line amps, charge pump, and outputs. Bias transitions enable MCLK while preparing for ON, disable it when leaving ON, power reference blocks when entering standby from off, and clear power registers when going off. `hw_params` computes clock divider from sysclk and LRCK, validates frame size and format, and programs I2S data length and ADDA clock divider. PLL setup calculates Realtek PLL codes from MCLK or BCLK.

## State And Persistence
Regcache is maple-backed and includes private-register ranges. Suspend sets cache-only and marks dirty; resume syncs regcache. Runtime clock and PLL state avoid redundant programming. Bias-off writes zero to digital, volume, mixer, and analog power registers. Shutdown mutes HP and line out to reduce pop/noise on system poweroff.

## Dependencies And Integration Points
The driver depends on I2C, regmap range windows, ASoC controls/DAPM/DAI APIs, optional `mclk`, OF matching (`realtek,rt5616`), and `rl6231_get_clk_info()`/`rl6231_pll_calc()`. It exposes one DAI named `rt5616-aif1` for stereo playback/capture at 8 kHz to 192 kHz.

## Risks
- Depop and headphone sequences contain many ordered writes and sleeps; changes can cause audible artifacts or hardware stress.
- `rt5616_set_dai_fmt()` only accepts normal frame polarity and inverted bit clock without inverted frame variants.
- PLL source `RT5616_PLL1_S_BCLK2` is treated like BCLK1 in register programming, which may be intentional but should be verified for multi-DAI reuse.
- Bias-level clock enable/disable assumes balanced transitions and optional `mclk` availability.
- Empty remove callback is harmless but provides no explicit cleanup beyond devm.

## Test Signals
Test I2C probe and ID rejection, private-register patch writes, playback/capture at supported rates/formats, MCLK and PLL sysclk paths, invalid format/polarity/source rejection, DAPM input/output routing, headphone and line-out depop events with pop/noise checks, suspend/resume regcache sync, bias-off power clearing, and shutdown mute writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5616.c -->
