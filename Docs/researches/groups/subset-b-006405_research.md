# Research Report: subset-b-006405

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/Makefile

Purpose: kernel Kbuild manifest for the Oxygen/CMI878x ALSA PCI driver family. It builds `snd-oxygen-lib` from shared bus, PCI, mixer, and PCM code; `snd-oxygen` from the C-Media reference/Xonar DG entry code; `snd-se6x` for Studio Evolution SE6X; and `snd-virtuoso` for Asus Xonar Virtuoso boards.

Important APIs and integration points: the file maps `CONFIG_SND_OXYGEN_LIB`, `CONFIG_SND_OXYGEN`, `CONFIG_SND_SE6X`, and `CONFIG_SND_VIRTUOSO` to loadable objects. The Virtuoso object explicitly pulls `xonar_lib.o`, PCM179x, CS43xx, WM87x6, and HDMI support, while `snd-oxygen` includes `xonar_dg_mixer.o` and `xonar_dg.o`.

Control flow/state: no runtime state, but link composition controls which `oxygen_model` providers are present in each module. Dependency risks are mostly missing object linkage: moving a board callback without updating this file causes unresolved symbols or unsupported PCI IDs. Test signals are kernel build coverage for all four configs and module load/probe smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/ak4396.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/ak4396.h

Purpose: register and bit-field definitions for AK4396 DACs used by generic CMI8788, Meridian, Claro, and stereo-output models in `oxygen.c`.

Important API surface: defines the write command prefix, registers `CONTROL_1..3`, left/right attenuation, digital interface formats, reset, soft mute, de-emphasis, DFS single/double/quad speed, slow rolloff, zero-detect, and PCM/DSD selection bits.

Integration points: `oxygen.c` uses these constants in `ak4396_write`, `ak4396_registers_init`, `set_ak4396_params`, `update_ak4396_volume`, `update_ak4396_mute`, and rolloff mixer controls. State is persisted in `generic_data.ak4396_regs`, then replayed on resume.

Risks: incorrect bit masks can leave DACs muted, misclocked, or using the wrong serial format. Tests should exercise sample rates across 44.1/48, 96, and 192 kHz, mixer rolloff, mute, volume, suspend/resume, and proc register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/ak4396.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cm9780.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/cm9780.h

Purpose: C-Media CM9780 AC97 codec private register map used by generic Oxygen and Xonar cards for jack routing, capture source control, mixer routing, and GPIO.

Important definitions: private registers `JACK`, `MIXER`, `GPIO_SETUP`, and `GPIO_STATUS`; jack routing bits for rear/center/surround/front outputs and mic/line/front-mic routes; mixer bits for boost, stereo mic, SPDIF-to-output expansion, mix routing, and PCB switch; GPIO input/output/status bits.

Integration points: `oxygen_lib.c` initializes CM9780 AC97 routing and powers down unused blocks; `oxygen_mixer.c` switches AC97 capture paths and front-panel mic selection; Xonar D1/D2/PCM179x code uses AC97 line/mic callbacks to toggle external GPIO input routing.

Risks: AC97 access is unreliable in this driver, so incorrect routing bits can appear intermittently. Test signals include AC97 capture source switching, front mic, line/CD/aux mutual exclusion, resume restore, and `oxygen_proc_read` AC97 dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cm9780.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs2000.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/cs2000.h

Purpose: register/bit definitions for Cirrus CS2000 clock generator used by Xonar ST and Xense variants in `xonar_pcm179x.c`.

Important API surface: device/config/global/function registers, 32-bit ratio registers, freeze/unfreeze, clock output disable, ratio modifier/selector fields, lock clock selector, static/dynamic fractional-N source, reference clock dividers, clock skip, and clock input bandwidth fields.

Integration points: `cs2000_registers_init` writes a fixed 1.0 ratio and `CS2000_FUN_CFG_1`; `update_cs2000_rate` changes Oxygen I2S MCLK and CS2000 reference divider for sample-rate families. State is cached in `xonar_pcm179x.cs2000_regs` for write suppression and diagnostics.

Risks: clock register errors can break DAC lock across ST/Xense playback, especially 44.1 vs 48 kHz families and high rates. Test signals: playback at 32/44.1/48/96/192 kHz, PLL-lock delay behavior, resume, and proc register dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs2000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4245.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4245.h

Purpose: CS4245 codec register map for Xonar DG/DGX capture/playback codec control.

Important definitions: power, DAC/ADC control, MCLK frequency selectors, signal selection, PGA controls, analog input mux, DAC channel volumes, interrupt bits, SPI address/read/write values, DAC/ADC single/double/quad modes, left-justified/I2S formats, soft ramp/zero cross, mute, HPF freeze, and aux output routing.

Integration points: `xonar_dg.c` stores the whole register space in `dg.cs4245_shadow`, writes it via SPI, sets DAC/ADC rate modes, and dumps it. `xonar_dg_mixer.c` updates output source, headphone volume/mute, PGA capture volumes, source mux, and ADC high-pass filter through these constants.

Risks: all DG analog routing depends on shadow/register agreement; failed SPI writes or bad masks can leave outputs muted or route the wrong input. Test signals include DG/DGX output mode changes, capture source/volume, headphone mute, rate changes, resume reload, and proc dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4245.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4362a.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4362a.h

Purpose: CS4362A multichannel DAC bit definitions for Xonar D1/DX and some PCM179x-family daughterboards.

Important API surface: power/control-port mode, interface format, mute control polarity/auto mute/ramp/zero-cross, de-emphasis/filter, invert bits, per-pair functional mode, ATAPI channel mapping, volume/mute bits, and part/revision masks.

Integration points: `xonar_cs43xx.c` initializes CS4362A over I2C, updates six surround/center/back volumes and mutes, changes functional mode by rate, and toggles center/LFE upmix mapping. It also shares rolloff with CS4398.

Risks: channel-pair register layout is non-linear (`7 + i + i / 2`), making off-by-one errors likely. Tests should verify 8-channel routing, center/LFE upmix, mute/volume, sample-rate mode switching, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4362a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4398.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4398.h

Purpose: CS4398 stereo DAC register definitions for Xonar D1/DX front-channel DAC management.

Important definitions: part/revision masks, functional modes, de-emphasis, interface formats, ATAPI routing, invert/equal-volume bits, mute polarity/auto mute, soft/zero ramping, filter selection, volume/mute registers, and power/control-port mode bits.

Integration points: `xonar_cs43xx.c` caches `cs4398_regs`, initializes the chip in control-port mode, adjusts rate mode, controls front volume/mute, implements DAC filter mixer control, and includes CS4398 state in proc dumps.

Risks: CS4398 front DAC state must remain aligned with CS4362A multichannel state; mismatched filter/rate/mute behavior causes front-only regressions. Test signals include D1/DX front playback, IEC958 coexistence, rolloff, volume/mute, high sample rates, resume, and dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/cs4398.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.c

Purpose: module entry and model selection for generic C-Media CMI8788/CMI8787 boards plus Xonar DG/DGX. It defines PCI IDs, board-specific `oxygen_model` variants, codec setup for AK4396/WM8785/AK5385, and ALSA controls unique to these reference-style cards.

Important functions/types: `generic_data` caches AK4396 and WM8785 registers. `ak4396_write*`, `wm8785_write`, register init/resume helpers, `set_ak4396_params`, `set_wm8785_params`, and `set_ak5385_params` implement codec programming. Mixer hooks add DAC rolloff, ADC HPF, and Meridian/Claro digital-source controls. `get_oxygen_model` clones `model_generic` then patches callbacks, device_config, clocks, names, and channel counts by PCI `driver_data`. `generic_oxygen_probe` delegates to `oxygen_pci_probe`.

Control flow: PCI probe checks module slot enablement, calls shared library probe, which invokes `get_oxygen_model`; shared init then calls this file's model callbacks. Playback/capture hw_params later call the model rate-setting callbacks; mixer writes update cached register state; resume replays codec registers.

State/persistence: AK4396/WM8785 shadow arrays store mutable codec state and support cached writes and resume. GPIO state is manipulated for digital source selection and Claro headphone amplifier enable/disable.

Dependencies/integration: depends on `oxygen_lib.c`, `oxygen_io.c`, `oxygen_mixer.c`, `oxygen_pcm.c`, AK4396/WM8785 headers, and `model_xonar_dg`. Risks include wrong PCI subdevice mapping, SPI codec index mismatches, long anti-pop delays, and sample-rate DFS/MCLK mismatches. Test signals: probe each model, ALSA mixer controls, 2/8-channel playback, SPDIF input source controls, suspend/resume, proc codec dumps, and DG fallback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.h

Purpose: central internal ABI for the Oxygen driver family. It defines PCM channel IDs, device configuration flags, control IDs, PCI ID helpers, the `oxygen_model` callback table, the runtime `oxygen` device state, and exported helper prototypes.

Important types/APIs: `struct oxygen_model` supplies board callbacks for init, mixer filtering/init, cleanup, PM, PCM hardware filtering, DAC/ADC params, volume/mute/routing, GPIO/UART/AC97 handling, proc dumps, and static capabilities. `struct oxygen` stores I/O base, locks, ALSA objects, model data, interrupt mask, DAC/SPDIF/PCM state, control pointers, work items, AC97 waitqueue, saved MMIO/AC97 registers, UART buffer, and active model.

Control/state: model flags (`PLAYBACK_*`, `CAPTURE_*`, MIDI, AC97) drive PCM and mixer creation. `saved_registers` and `saved_ac97_registers` are maintained by I/O helpers for suspend/resume.

Risks: this header is the contract between all board files and shared code; changing enum order, bit mappings, or callback semantics can silently route DMA or mixers incorrectly. Test signals include full-module build, all model probes, PM restore, PCM open/hw_params/trigger, mixer add/filter paths, and exported symbol users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_io.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_io.c

Purpose: low-level register, AC97, SPI, I2C, UART, and EEPROM I/O helpers exported to all Oxygen modules.

Important functions: `oxygen_read/write{8,16,32}` wrap port I/O and persist writes into `saved_registers`; masked variants do read-modify-write with saved-state updates. `oxygen_write_ac97`, `oxygen_read_ac97`, and masked AC97 writes implement retry/verification around unreliable AC97 transactions. `oxygen_write_spi`, `oxygen_write_i2c`, UART reset/write, and EEPROM read/write provide board-code transport primitives.

Control flow: AC97 waits on `ac97_waitqueue` but also polls status because interrupts may be disabled. Writes require two completions; reads require two equal values with inversion between attempts. SPI writes data bytes then triggers and waits for not-busy. I2C uses a conservative sleep before writing bus registers.

State/persistence: MMIO writes update `saved_registers`; successful AC97 writes update `saved_ac97_registers`. These are consumed by `oxygen_pci_resume`.

Risks: timing-sensitive hardware access, port-I/O ordering, and cached state consistency. Tests should stress AC97 read/write retries, SPI/I2C codec programming, suspend/resume register restore, EEPROM repair path, and error logging on timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_lib.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_lib.c

Purpose: shared PCI/ALSA driver core for Oxygen cards. It owns interrupt handling, card probe/init, AC97 codec setup, proc diagnostics, PM suspend/resume, shutdown, and bridge quirks.

Important functions: `oxygen_interrupt` acknowledges DMA/SPDIF/GPIO/AC97/MIDI events and schedules work; SPDIF work toggles input clock when sense exists without lock; GPIO work delegates to model callback. `oxygen_search_pci_id` reads EEPROM subdevice IDs; `oxygen_restore_eeprom` repairs broken EEPROM PCI subsystem words. `oxygen_init` programs default chip registers and AC97 codecs. `__oxygen_pci_probe` allocates ALSA card, enables PCI, selects model, initializes hardware, requests IRQ, creates PCM/mixer/MIDI/proc, enables interrupts, and registers the card. PM helpers save/restore selected registers and AC97 state.

State/persistence: shared `oxygen` state tracks active/running streams, interrupt mask, saved MMIO/AC97 registers, UART buffer, work items, and model data. Resume restores only bitmap-selected registers plus AC97 register subsets, then calls model resume.

Dependencies/integration: called by `oxygen.c`, `se6x.c`, and `virtuoso.c`; depends on `oxygen_io`, PCM/mixer init, ALSA core, PCI, MPU401, and CM9780 constants.

Risks: interrupt races, stale work items during suspend/free, EEPROM repair side effects, AC97 unreliable transactions, and model callback assumptions during init/cleanup. Test signals: IRQ period elapsed, SPDIF lock/rate changes, GPIO power events, MIDI input, probe/remove, PM cycles, proc output, and broken-EEPROM matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_mixer.c

Purpose: shared ALSA mixer/control implementation for Oxygen models, including DAC volume/mute, stereo upmixing, SPDIF playback/capture controls, input monitoring, and AC97 capture/front-panel controls.

Important APIs: control callbacks for DAC volume/mute call model `update_dac_*`; `oxygen_update_dac_routing` maps stereo/multichannel routing and lets models adjust it; `oxygen_update_spdif_source` switches SPDIF between dedicated PCM and mirrored multichannel; IEC958 conversion helpers map ALSA status bytes to Oxygen bits. AC97 switch/volume controls manage CM9780 routing and mutual exclusion between line and mic/CD/aux capture.

Control flow: `oxygen_mixer_init` conditionally adds control arrays based on `device_config`, AC97 presence, model filter, and model mixer init. `add_controls` stores known controls for later notifications and inactive toggling.

State/persistence: shared state lives in `chip->dac_volume`, `dac_mute`, `dac_routing`, `spdif_bits`, `spdif_pcm_bits`, `spdif_playback_enable`, `controls`, and AC97 registers.

Risks: mixer names and private_value encodings are ABI-visible; control_filter can remove or mutate controls; SPDIF and routing updates run under mixed mutex/spinlock contexts. Test signals: `amixer` get/put for all generated controls, SPDIF PCM inactive state during stream open/close, upmix routing by channel count, AC97 capture source exclusivity, and TLV ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_pcm.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_pcm.c

Purpose: shared ALSA PCM implementation for Oxygen DMA channels: analog capture A/B/C, SPDIF playback/capture, multichannel playback, and AC97/front-panel playback/capture.

Important functions: `oxygen_open/close` assign channel runtime state and active bits; `oxygen_hw_params` writes DMA base/count/period registers; channel-specific hw_params program formats, I2S rate/MCLK/bits, SPDIF rate/source, and model DAC/ADC params; `oxygen_prepare`, `oxygen_trigger`, `oxygen_pointer`, and hw_free control DMA interrupts, status, pause, flush, and pointer reporting. `oxygen_pcm_init` creates ALSA PCM devices based on model `device_config`.

Control flow: open applies hardware constraints and notifies SPDIF PCM control activation. hw_params programs hardware and model codecs. trigger groups synchronized substreams, updating `pcm_running` and DMA status/pause registers. interrupts in `oxygen_lib.c` call `snd_pcm_period_elapsed`.

State/persistence: active/running stream masks and `streams[]` link ALSA substreams to IRQ handling; DMA registers are saved through write helpers.

Risks: DMA count units are dwords, multichannel uses 24-bit counters, pointer arithmetic assumes 32-bit DMA address behavior, and lock ordering with mixer/SPDIF state matters. Test signals: playback/capture at all rates/formats/channel counts, no-period-wakeup, pause/resume, sync-start groups, hw_free flush, and SPDIF/multichannel source interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_regs.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_regs.h

Purpose: complete CMI8786/8787/8788 register map and bit definitions for DMA, interrupts, formats, clocks, SPDIF, EEPROM, I2C/SPI, MIDI, GPIO/GPI, routing, AC97, diagnostics, and revision fields.

Important groups: DMA base/count/tcount registers per channel; channel masks matching `PCM_*`; interrupt masks/status; misc/function reset and bus-mode bits; I2S rate/format/MCLK/BCLK/bits; SPDIF input/output status and IEC958 bit fields; EEPROM and 2-wire/SPI controls; GPIO/GPI and device sense; playback/record routing and monitor routing; AC97 control/status/config/register windows.

Integration: every shared C file and board driver uses these definitions to program hardware. `oxygen.h` relies on channel-mask alignment. `oxygen_io.c` uses offsets for saved register cache and transports; PCM/mixer/lib use DMA, interrupt, routing, and PM restore maps.

Risks: this is hardware ABI. Any incorrect offset, mask, or read/write-clear interpretation can cause broken DMA, stuck interrupts, wrong clocks, or unsafe output routing. Test signals are broad hardware smoke tests: probe, DMA on every channel, interrupt ack, I2C/SPI transactions, SPDIF in/out, AC97, GPIO events, EEPROM reads, and resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/pcm1796.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/pcm1796.h

Purpose: PCM1796/PCM1792A DAC register bit definitions for Xonar D2/D2X/HDAV/ST/STX/Xense models.

Important definitions: attenuation load, mute, DAC format selection, mono/stereo, phase, de-emphasis enable/mode, oversampling ratio, filter rolloff, attenuator speed, and stereo/mono format variants.

Integration points: `xonar_pcm179x.c` programs registers 16-21 by SPI or I2C, caches five registers per DAC, implements volume/mute, rolloff, de-emphasis, oversampling, headphone gain offsets, and resume replay.

State/persistence: mutable DAC configuration is cached in `xonar_pcm179x.pcm1796_regs`; active volume also comes from shared `chip->dac_volume`.

Risks: ST H6 has broken I2C constraints, so controls may be filtered away. Test signals include all PCM179x boards, mute/volume/de-emphasis/rolloff, headphone impedance offsets, H6 variants, rate changes, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/pcm1796.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/se6x.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/se6x.c

Purpose: standalone PCI module for Studio Evolution SE6X built on the shared Oxygen core with a minimal custom `oxygen_model`.

Important functions: `se6x_init` configures GPIO outputs and registers PCM1792A/PCM1804 components; `se6x_control_filter` removes generic master playback volume/mute controls; `set_pcm1792a_params`/`set_pcm1804_params` are no-ops because external hardware/microcontroller handles clocks; `se6x_adjust_dac_routing` mirrors one stereo pair to both DAC0 and DAC1; `se6x_probe` delegates to `oxygen_pci_probe`.

Control flow/state: module parameters follow ALSA card slot conventions. Probe selects `model_se6x`; shared code creates PCM/mixer using device_config for I2S playback and three capture inputs.

Dependencies/integration: depends on `oxygen_lib`, `oxygen_pcm`, `oxygen_mixer`, and register helpers. No persistent private model_data is used.

Risks: broad PCI subdevice ID overlaps generic CMI8788 ID; module selection/config must avoid conflicts. Tests: module probe, no generic DAC master controls, stereo playback routing, three analog capture PCMs, suspend/resume via shared PM, and GPIO setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/se6x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/virtuoso.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/virtuoso.c

Purpose: PCI module entry for Asus Xonar Virtuoso cards, delegating board identification to PCM179x, CS43xx, and WM87x6 model providers.

Important functions/data: `xonar_ids` lists Asus subsystem IDs plus broken-EEPROM fallback. `get_xonar_model` tries `get_xonar_pcm179x_model`, then `get_xonar_cs43xx_model`, then `get_xonar_wm87x6_model`. `xonar_probe` handles ALSA module slot arrays and calls shared `oxygen_pci_probe`. Driver uses shared PM and shutdown.

Control flow/state: no board private state here; it selects the model provider, then `oxygen_lib.c` allocates model_data and initializes the selected board.

Dependencies: `xonar.h`, shared Oxygen core, and linked board objects from Makefile. Risks include provider ordering, duplicate subsystem IDs, and broken EEPROM fallback selecting the wrong model. Test signals: probe every listed Xonar ID, broken EEPROM matching, module parameter enable/index behavior, PM, shutdown cleanup, and ensuring all provider objects link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/virtuoso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8766.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8766.h

Purpose: Wolfson WM8766 DAC register definitions used by the Xonar WM87x6 board implementation linked into `snd-virtuoso`.

Important definitions: DAC volume registers, interface control, DAC control, mute control, powerdown, reset, attenuation update/mute bits, format bits, phase/clock/polarity flags, de-emphasis, zero-cross, soft mute, and per-DAC mute/powerdown fields.

Integration points: although the required C file using it is outside this work item, Makefile links `xonar_wm87x6.o` with Virtuoso. That code initializes WM8766, caches registers, updates volume/mute, and handles center/LFE mixing using these constants.

Risks: constants affect multichannel output mute/power behavior and audio format. Test signals: Virtuoso DS/HDAV Slim playback, volume/mute, de-emphasis/format changes, center/LFE mix, powerdown/resume, and proc register dump from the WM87x6 implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8766.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8776.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8776.h

Purpose: Wolfson WM8776 codec register and bit definitions for Xonar DS/HDAV Slim style capture/playback codec control.

Important API surface: DAC/ADC/headphone/output mixer volumes, DAC/ADC interface/control, mute, output mux, powerdown, ADC mux, high-pass filter, limiter/ALC/noise-gate controls, reset, update bits, format/master/clock flags, polarity, deemphasis, zero-cross, and limiter/ALC field masks.

Integration points: consumed by `xonar_wm87x6.c` for SPI/I2C register writes, cached controls, ADC input mux, HP volume, level control, high-pass filter, DAC mute/volume, and proc dumps. It integrates with generic Oxygen mixer through model callbacks and additional ALSA controls.

Risks: many fields are packed into ALSA private values; wrong masks can corrupt adjacent limiter/ALC fields. Tests should cover WM8776 controls, capture mux and volumes, HP output, limiter/ALC controls, hpf, suspend/resume, and all supported board variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8776.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8785.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8785.h

Purpose: WM8785 ADC register bit definitions used by generic Oxygen cards in `oxygen.c`.

Important definitions: reset register, master/slave mode, OSR single/double/quad, serial format left/right/I2S/DSP, LR polarity, bit clock mode, high-pass filter bits, and device ID/revision masks.

Integration points: `wm8785_init` seeds default register cache; `set_wm8785_params` selects OSR by sample rate; generic mixer exposes ADC high-pass filter using `WM8785_HPFR/HPFL`; resume replays cached values.

State/persistence: `generic_data.wm8785_regs` holds registers 0 and 2 plus reset behavior. Risks: ADC clock/rate mismatch and HPF control desynchronization. Test signals: analog capture at low/double/quad rates, ADC filter mixer, suspend/resume, and proc WM8785 dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/wm8785.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar.h

Purpose: shared header for Asus Xonar Virtuoso board support and HDMI helpers.

Important types/APIs: `struct xonar_generic` stores anti-pop delay, output-enable GPIO, external power interrupt/register fields, and cached power state. `struct xonar_hdmi` stores five UART command parameters. Prototypes cover output enable/disable, external power monitoring, CS53x1 ADC GPIO setup/rate control, generic GPIO-backed mixer switches, model-provider selectors, and HDMI init/cleanup/resume/PCM params/UART input.

Integration: used by `virtuoso.c`, `xonar_lib.c`, `xonar_cs43xx.c`, `xonar_pcm179x.c`, `xonar_hdmi.c`, and WM87x6 support. It bridges shared Oxygen model callbacks to board-specific model data.

Risks: `xonar_generic` must be first in model-specific structures where helpers cast `chip->model_data`; layout changes can break all helpers. Test signals include output anti-pop sequencing, external power GPIO interrupts, GPIO mixer controls with invert flag, CS53x1 rate changes, and HDMI UART messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_cs43xx.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_cs43xx.c

Purpose: board support for Xonar D1/DX cards using CS4398 front DAC, CS4362A multichannel DAC, CS5361 ADC, and CM9780 AC97 routing.

Important functions/types: `struct xonar_cs43xx` embeds `xonar_generic` and codec register caches. `cs4398_write*` and `cs4362a_write*` perform I2C writes and cache values. `cs43xx_registers_init` powers down, configures, and powers up both DACs. D1/DX init sets I2C speed, GPIO output/front-panel/input routes, CS53x1 ADC GPIOs, external power for DX, and component strings. Rate, volume, mute, center/LFE mix, front-panel switch, DAC rolloff, AC97 line/mic routing, and proc dump callbacks fill `model_xonar_d1`.

Control flow/state: Virtuoso model selection calls `get_xonar_cs43xx_model`; shared probe allocates model_data and calls init. Mixer operations update cached codec registers and GPIO. Resume resets codecs, replays caches, and enables output after delay.

Dependencies: Oxygen I2C/GPIO/AC97 helpers, Xonar generic helpers, CS4398/CS4362A/CM9780 constants, ALSA controls.

Risks: front and multichannel DACs must remain synchronized for rate/mute/filter; DX external power loss only logs TODO for stopping PCMs. Test signals: D1/DX probe, power event, 8-channel playback, front panel switch, rolloff, volume/mute, line/mic switching, capture, resume, and proc dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_cs43xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.c

Purpose: low-level Xonar DG/DGX board support around CS4245 SPI codec, GPIO output routing, and model callbacks.

Important functions: `cs4245_write_spi`, `cs4245_read_spi`, and `cs4245_shadow_control` maintain the CS4245 shadow register array. `cs4245_init` saves initial state, programs power, async mode, DAC/ADC formats, PGA behavior, and headphone volume. `dg_init/cleanup/suspend/resume` manage output GPIO and anti-pop delay. `set_cs4245_dac_params` and `set_cs4245_adc_params` update functional mode and MCLK ratio by sample rate. `adjust_dg_dac_routing` swaps Oxygen DAC pair mapping and mutes inactive groups by selected output. `dump_cs4245_registers` refreshes interrupt status and prints cached registers.

State/persistence: `struct dg` owns CS4245 shadow state, output selection, input volumes, and input selection; resume reloads the shadow.

Dependencies/integration: used by `model_xonar_dg` in `xonar_dg_mixer.c`, selected from `oxygen.c` for DG/DGX PCI IDs. Risks include long 2.5-second output enable, SPI failures causing shadow/device mismatch, and non-obvious channel remapping. Test signals: DG/DGX probe, output modes, playback channel routing, capture rates, resume, and proc dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.h -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.h

Purpose: internal header for Xonar DG/DGX support shared between low-level codec code and mixer/model definition.

Important definitions: GPIO masks for magic/HP detect/input route/HP rear/output enable; capture source enum values for mic/front mic/line/aux; playback destination enum values for headphones/front-panel headphones/multichannel; CS4245 shadow operation enum; `struct dg` model data with CS4245 shadow, output selection, per-source input volumes, and selected input.

Integration: `xonar_dg.c` provides codec/routing operations, `xonar_dg_mixer.c` defines controls and `model_xonar_dg`, and `oxygen.c` selects that model. The model_data layout is the persistence boundary for controls and resume.

Risks: enum values are directly stored in mixer state and used for routing decisions; changing them can break userspace-visible control values. Test signals include compile linkage, all DG ALSA controls, GPIO routing, shadow save/load, and model selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg_mixer.c

Purpose: ALSA mixer controls and `oxygen_model` definition for Xonar DG/DGX.

Important functions: output select control applies CS4245 aux/DAC output and GPIO rear-jack relay; headphone volume/mute controls write CS4245 DAC volume/control registers; capture volume controls store per-source PGA values and apply current source; capture source selects CS4245 analog input; ADC HPF control toggles HPF freeze. `dg_control_filter` removes generic master playback controls. `dg_mixer_init` initializes routing and adds DG controls. `model_xonar_dg` wires all callbacks and capabilities.

Control flow/state: mixer callbacks lock `chip->mutex`, update `struct dg`, write CS4245 via helpers, and call shared `oxygen_update_dac_routing` for output changes. Shared mixer still adds SPDIF and monitor controls based on model device_config.

Dependencies: `xonar_dg.c`, CS4245 constants, Oxygen mixer/PCM core. Risks: several controls return negative SPI errors as changed values; headphone volume uses bitwise complement storage; output mode affects both CS4245 and Oxygen routing. Test signals: `amixer` control validation/range errors, output transition audio routing, capture source/volume persistence, HPF, SPDIF coexistence, resume shadow reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_hdmi.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_hdmi.c

Purpose: HDMI helper for Xonar HDAV models, communicating with an HDMI controller over Oxygen UART.

Important functions: `hdmi_write_command` frames commands with magic bytes, command, count, params, and checksum. `xonar_hdmi_init_commands` resets UART, sends setup commands, and writes audio params. Public init/cleanup/resume manage HDMI enable state. `xonar_hdmi_pcm_hardware_filter` restricts multichannel playback rates to 44.1/48/96/192 kHz. `xonar_set_hdmi_params` maps ALSA params to IEC958 sample-rate code, channel-pair count, sample width, and sends command 0x54. `xonar_hdmi_uart_input` logs received OK messages.

State/persistence: `xonar_hdmi.params[5]` persists last HDMI audio format for resume. UART input is buffered in shared `oxygen.uart_input`.

Dependencies: `oxygen_write_uart/reset_uart`, ALSA PCM params, IEC958 constants, Xonar PCM179x HDAV model. Risks: checksum/protocol regressions are hard to see without hardware; UART input buffer wraps at 32 bytes. Test signals: HDAV probe, HDMI switch, multichannel hw constraints, playback at supported rates/channel counts/formats, resume, cleanup mute, and debug logs for OK responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_lib.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_lib.c

Purpose: shared helper implementation for Xonar board drivers.

Important functions: `xonar_enable_output` configures output-enable GPIO, waits anti-pop delay, then enables output; `xonar_disable_output` clears the output GPIO. `xonar_init_ext_power` enables GPI/GPIO interrupt masks, installs `gpio_changed`, and snapshots power state; `xonar_ext_power_gpio_changed` logs restore/loss events. `xonar_init_cs53x1` and `xonar_set_cs53x1_params` configure CS53x1 ADC mode GPIOs by sample rate. `xonar_gpio_bit_switch_get/put` expose GPIO bits as ALSA boolean controls with optional inversion.

State/persistence: uses `xonar_generic` fields inside model_data and shared `chip->interrupt_mask`; GPIO writes are saved by Oxygen I/O helpers. External power state is cached in `has_power`.

Dependencies: Oxygen GPIO/register helpers, ALSA control framework, and model_data layout convention.

Risks: helper assumes `xonar_generic` is at offset zero in model data; external power loss currently does not stop active PCMs. Test signals: output enable delay, power cable interrupt logging, GPIO mixer controls, inverted HDMI switch, CS53x1 rate-family changes, and resume output sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_pcm179x.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_pcm179x.c

Purpose: largest Xonar board provider, covering PCM1796/PCM1792A-based D2/D2X/HDAV1.3/ST/STX/STX II/Xense boards, optional H6 daughterboards, CS2000 clocking, HDMI, GPIO output routing, and AC97 input routing.

Important types/functions: `struct xonar_pcm179x` embeds `xonar_generic`, DAC count, PCM1796 register cache, current rate, H6/headphone/CS2000 flags, HP gain offset, CS2000 cache, and broken-I2C flag. `struct xonar_hdav` adds HDMI state. PCM1796 write paths select SPI or I2C by model function flags; caches suppress redundant writes. Init functions configure per-board I2C/SPI, external power, CS53x1, CS2000, GPIOs, DAC count, H6 detection, HDMI, and output enable. Runtime callbacks update oversampling/de-emphasis by rate, CS2000 rate/MCLK, volume/mute, headphone routing/gain, HDMI params, rolloff/de-emphasis controls, and proc dumps.

Control flow: `get_xonar_pcm179x_model` matches subsystem IDs and may read GPIO daughterboard bits to mutate model channel counts, clocks, control filters, and shortnames. Shared probe then allocates model data and calls selected init. PCM hw_params calls model `set_dac_params`; mixers modify cached DAC/GPIO state.

State/persistence: codec caches, `current_rate`, H6/headphone flags, CS2000 cache, and HDMI params survive for resume replay. Shared DAC volume/mute state is combined with HP gain offset.

Dependencies: Oxygen SPI/I2C/GPIO/AC97/UART helpers, `xonar_lib`, `xonar_hdmi`, CM9780, PCM1796, CS2000, ALSA controls. Risks include board-variant branching, H6 detection, broken ST I2C filtering, CS2000 PLL timing, output GPIO safety, and HP gain offsets affecting only first DAC. Test signals: all supported subsystem IDs, H6 and non-H6 variants, playback rates, HDMI constraints, SPDIF, AC97 input switch, rolloff/deemphasis, headphone impedance/output controls, external power events, suspend/resume, and proc dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_pcm179x.c -->
