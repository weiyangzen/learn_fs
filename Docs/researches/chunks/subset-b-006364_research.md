# sources/distributed-fs/ceph-client/sound/hda/codecs/ca0132.c lines 1-9230

## Purpose

This chunk contains most of the Creative CA0132/Core3D HD-audio codec driver: codec-specific data models, quirk tables, low-level vendor verb accessors, DSP firmware download, ALSA PCM callbacks, mixer/control implementations, jack handling, quirk-specific startup/shutdown sequencing, and the beginning of PCI region2 MMIO initialization.

The driver targets laptop CA0132 implementations and multiple desktop/PCIe products using CA0113/Core3D-style glue, including Sound Blaster Z/ZxR, Recon3D/Recon3Di, AE-5, and AE-7. The code maps ALSA HDA codec operations onto a mix of standard HDA verbs, Creative vendor verbs through `WIDGET_CHIP_CTRL` and `WIDGET_DSP_CTRL`, DSP SCP messages, 8051 controller memory writes, firmware loading through HDA DMA, optional PCI MMIO register writes, and quirk-specific GPIO/stream routing.

The chunk ends at line 9230 inside `ca0132_mmio_init_sbz()`, so the rest of that function and the final codec operation/probe tail are outside this chunk.

## Important Types And Static Data

- `struct ca0132_spec` is the main per-codec state. It stores mixer tables, init/exit verbs, parsed pin configuration, DAC/ADC and pin NIDs, unsolicited jack tags, ChipIO mutex and cached address, DSP download/SCP response state, current output/input/effect/mic-boost/volume selections, delayed headphone work, optional tuning values, PCI MMIO mapping state, and quirk feature flags.
- `struct ct_effect`, `struct ct_tuning_ctl`, `struct ct_voicefx`, `struct ct_voicefx_preset`, `struct ct_eq`, and `struct ct_eq_preset` describe DSP modules, SCP request IDs, default floating-point bit patterns, and user-visible preset/control names.
- `struct ca0132_alt_out_set_info` and `struct ca0132_alt_out_set_quirk_data` encode per-card output switching actions: HDA GPIO writes, PCI MMIO GPIO writes, DSP SCP commands, DAC-to-port parameters, ChipIO writes, and headphone gain behavior.
- `struct chipio_stream_remap_data` encodes manual audio-router remapping tables for DAC/DSP streams.
- `struct dma_engine` wraps the temporary HDA DMA buffer used to transfer DSP firmware segments.
- `struct dsp_image_seg` is the variable-length firmware segment format: magic, chip address, word count, and payload words.
- Static pin config tables (`alienware_pincfgs`, `sbz_pincfgs`, `zxr_pincfgs`, `r3d_pincfgs`, `ae5_pincfgs`, `r3di_pincfgs`, `ae7_pincfgs`) and quirk tables (`ca0132_quirks`, `ca0132_quirk_models`) drive model-specific topology.
- Lookup tables convert integer ALSA control values to DSP IEEE-754 bit patterns for volume, 0..1 sliders, X-Bass/bass redirection crossover, voice focus, mic SVM, and EQ gain.
- Mixer tables (`ca0132_mixer`, `desktop_mixer`, `r3di_mixer`) define standard and alternative ALSA controls. Alt mixers use extra surround controls and DSP-volume-aware volume put handlers.

## Low-Level Codec, ChipIO, DSPIO, And MMIO APIs

- `codec_send_command()`, `codec_set_converter_format()`, and `codec_set_converter_stream_channel()` wrap HDA codec read/write command patterns for converter setup.
- `chipio_send()` polls `WIDGET_CHIP_CTRL` vendor verb status for up to one second. Higher-level helpers write cached chip addresses, read/write 32-bit data, and write multiple words. Public-looking internal wrappers such as `chipio_write()`, `chipio_read()`, and `chipio_write_multiple()` serialize through `spec->chipio_mutex`.
- `chipio_set_control_flag()` and `chipio_set_control_param()` program Creative control flags and parameters. The parameter path uses compact encoding for small IDs/values and extended ID/value verbs for larger values.
- Stream helpers set stream source/destination, channel count, enable state, and connection-point sample rates.
- 8051 helpers (`chipio_8051_write_direct()`, `chipio_8051_write_exram()`, `chipio_8051_read_exram()`, `chipio_8051_write_pll_pmu()`) manipulate the embedded controller's direct, EXRAM, and PLL/PMU address spaces.
- `dspio_send()`, `dspio_write_wait()`, `dspio_write()`, and `dspio_read()` operate on `WIDGET_DSP_CTRL`, including busy/status polling and response queue reads.
- SCP support (`make_scp_header()`, `extract_scp_header()`, `dspio_send_scp_message()`, `dspio_scp()`, `dspio_set_param()`, `dspio_set_uint_param()`) builds module/request messages, optionally waits for asynchronous unsolicited DSP responses, validates reply headers, and copies returned words.
- `ca0113_mmio_gpio_set()`, `ca0113_mmio_command_set()`, and `ca0113_mmio_command_set_type2()` write PCI region2 registers for desktop cards. These routines include required readbacks and sleeps to avoid lockups or inconsistent AE-series behavior.

## DSP Firmware Download And DMA Flow

Firmware files are selected by quirk in `ca0132_download_dsp_images()`: desktop cards may use `ctefx-desktop.bin`, Recon3Di may use `ctefx-r3di.bin`, and the fallback is `ctefx.bin`. Loading is compiled out when `CONFIG_SND_HDA_CODEC_CA0132_DSP` is disabled.

The firmware transfer path is:

1. `ca0132_download_dsp()` enables clocks, sets `spec->dsp_state` to downloading, requests firmware, and calls `dspload_image()`.
2. `dspload_image()` optionally resets the DSP, chooses sample rate/channel parameters for the HDA DMA stream, then calls `dspxfr_image()`.
3. `dspxfr_image()` allocates a temporary `dma_engine`, prepares an HDA DSP-load stream with `snd_hda_codec_load_dsp_prepare()`, optionally allocates a DSP DMA channel for overlays, allocates router ports, assigns the converter stream/channel, and iterates all firmware segments.
4. `dspxfr_one_seg()` validates chip address ranges, aligns transfer size to HDA frame size, uses HDA DMA for bulk words, uses ChipIO writes for remainder words, handles HCI address/data-pair segments, starts/stops DSP DMA, waits for completion, and resets the DMA buffer between runs.
5. On success, `dspload_post_setup()` programs non-alt speaker defaults, `dsp_set_run_state()` starts the DSP, and `dspload_wait_loaded()` polls a ChipIO memory flag.

Important risks in this path are strict firmware segment validation, byte/word/count alignment, timeout behavior, shared `spec->dsp_stream_id`, and cleanup of DMA buffers/router ports/DSP DMA channels on error paths.

## PCM And ALSA Control Integration

Analog playback uses `ca0132_playback_pcm_prepare()` and cleanup on `spec->dacs[0]`; analog capture uses `hinfo->nid`. Digital playback delegates to `snd_hda_multi_out_dig_*`. Playback and capture delay callbacks report DSP-added latency when firmware is loaded and relevant effects are enabled.

`ca0132_build_pcms()` creates analog, optional Analog Mic-In2, What U Hear, and digital PCMs. Alt cards can expose up to six playback channels and custom channel maps (`ca0132_alt_chmaps`). `dbpro_build_pcms()` creates a reduced analog capture and optional digital PCMs for the ZxR daughter-board style codec.

Control creation in `ca0132_build_controls()` adds base mixers, optional vmaster/follower controls, output/input DSP effect switches, alt-only sliders/presets/enums, VoiceFX, jack controls, S/PDIF controls, and channel maps. It skips Echo Cancellation on PCI MMIO desktop cards because comments indicate those cards break if it is used.

Most control `put` handlers do two things: update cached state in `struct ca0132_spec`, then immediately program the active hardware path if the relevant output/input/effect is active.

## Output, Input, Effects, And Volume Control Flow

Output selection has two implementations:

- `ca0132_select_out()` is the original laptop-style path. It chooses speakers or headphones from auto-detect state or manual vnode state, toggles DSP speaker/headphone parameters, speaker EQ, EAPD, and pin widget control.
- `ca0132_alt_select_out()` is the desktop/surround path. It can use manual `Output Select` when HP auto-detect is disabled, detects rear/front headphone jacks when enabled, mutes DSP speaker tuning during transition, applies quirk-specific GPIO/MMIO/SCP/ChipIO operations through `ca0132_alt_select_out_quirk_set()`, programs pin controls for front/surround/center/LFE/headphone nodes, sets DSP output mode, reapplies X-Bass when needed, handles speaker EQ/bass redirection/full-range speaker settings, then unmutes DSP.

Input selection is similarly split:

- `ca0132_select_mic()` switches between digital mic and analog mic based on auto-detect/manual vnode state, toggles DMIC setup, mic boost, and Voice Focus.
- `ca0132_alt_select_in()` supports rear mic, rear line-in, and front mic. It disables streams during switching, performs quirk-specific GPIO/MMIO routing, sets connection rates, DSP input mode, ChipIO routing registers, mic boost, and CrystalVoice/VIP source state.

Effects are controlled through `ca0132_effects_set()`, `ca0132_pe_switch_set()`, `ca0132_cvoice_switch_set()`, `ca0132_voicefx_set()`, and preset/slider handlers. Output effects are gated by PlayEnhancement. Input effects are gated by CrystalVoice. Voice Focus is forced off for non-digital mic paths, line-in disables input effects on alt cards, and X-Bass is disabled for speaker configurations with LFE-style bass redirection.

Virtual node volume and mute controls use VNID state arrays and redirect to shared physical NIDs when effective. Alt volume writes additionally mirror left/right dB values into DSP modules through `ca0132_alt_dsp_volume_put()`. The comments note this separate alt volume path was added to avoid noticeable lag from conditionals in the generic path.

## Initialization, Defaults, Jack Handling, And Shutdown

`ca0132_init_chip()` initializes the ChipIO mutex, optionally resets alt codecs twice to clear previous OS state, sets current output/input defaults, initializes virtual node volumes/mutes, effects, alt sliders/full-range defaults, VoiceFX, CrystalVoice/PlayEnhancement defaults, and tuning defaults.

`ca0132_setup_unsol()` registers jack callbacks for headphone, analog mic, DSP unsolicited response, and front headphone on alt cards. `hp_callback()` blocks immediate reporting and schedules `ca0132_unsol_hp_delayed()` after 500 ms so output switching happens after the mic-detection state machine settles. `ca0132_process_dsp_response()` clears `spec->wait_scp` when the expected SCP response arrives and then drains the response queue.

Default programming is quirk-specific:

- `ca0132_setup_defaults()` is the base/laptop DSP default path.
- `r3d_setup_defaults()` initializes alt mics, DSP streams, What U Hear, speaker source, R3Di GPIO DSP status, R3D GPIOs, and effects.
- `sbz_setup_defaults()` additionally connects/remaps streams, disables internal loopback, initializes mic routing, and programs speaker tuning.
- `ae5_setup_defaults()` and `ae7_setup_defaults()` add extensive CA0113 MMIO, ASI, PLL/PMU, stream, GPIO, and register sequences matching observed Windows behavior.

`ca0132_alt_start_dsp_audio_streams()` is a key startup stabilizer. It disables default DSP streams, frees any active DSP DMA channels, then starts stream `0x0c` and mic streams `0x03`/`0x04` with delays so the DSP configures DMA channels in a known order. Comments identify this as a workaround for intermittent no-audio caused by broken DSP DMA setup after firmware download.

Shutdown helpers are per-quirk: `sbz_exit_chip()`, `r3d_exit_chip()`, `ae5_exit_chip()`, `ae7_exit_chip()`, `zxr_exit_chip()`, `r3di_gpio_shutdown()`, and `zxr_dbpro_power_state_shutdown()` stop streams, reset rates/routes, clear unsolicited events, power down pins, set GPIO/MMIO state, and disable EAPD. `ca0132_exit_chip()` resets the DSP if it is loaded.

## State And Persistence Behavior

All runtime user selections are stored in `struct ca0132_spec`, not persistent storage. Examples include virtual node volumes/switches, effect switches, VoiceFX preset, current mic boost, alt input/output enum values, speaker channel configuration, full-range/bass-redirection values, crossover frequencies, smart-volume setting, EQ preset, AE-5 headphone gain/filter, and ZxR gain. These values survive while the codec object lives and are re-applied by control handlers and init/default paths, but they are not written to disk by this driver.

Hardware state is cached only selectively. `spec->curr_chip_addx` avoids redundant ChipIO address writes and is invalidated on errors. `spec->dsp_state` prevents repeated failed firmware downloads and records init/downloading/downloaded status. `spec->wait_scp`, `wait_scp_header`, `wait_num_data`, and response buffers coordinate synchronous SCP commands with asynchronous DSP unsolicited callbacks.

Synchronization is centered on `spec->chipio_mutex` for ChipIO/DSP/8051 register sequences and `codec->control_mutex` when temporarily rewriting mixer private values to delegate to shared HDA amp helpers. Several `_no_mutex` helpers assume the caller already holds `chipio_mutex`.

## Dependencies And Integration Points

- Linux HDA codec APIs: `snd_hda_codec_read/write`, `snd_hda_set_pin_ctl`, `snd_hda_codec_setup_stream`, `snd_hda_codec_cleanup_stream`, `snd_hda_codec_pcm_new`, mixer amp helpers, vmaster helpers, jack callbacks, parser/config types, and S/PDIF helper controls.
- DSP firmware loader APIs: `request_firmware()`, `release_firmware()`, `snd_hda_codec_load_dsp_prepare()`, `snd_hda_codec_load_dsp_trigger()`, and `snd_hda_codec_load_dsp_cleanup()`.
- Kernel timing/synchronization: `jiffies`, `msecs_to_jiffies()`, `time_before()`, `msleep()`, `mutex`, `guard()`/`scoped_guard()` cleanup helpers, and delayed work.
- PCI/MMIO APIs: `readl`, `writel`, `writeb`, `writew`, and `void __iomem *mem_base` for region2 commands on supported desktop cards.
- Hardware register definitions from `ca0132_regs.h`, especially DSP DMA register offsets/ranges and address conversion macros.
- Firmware files declared through `MODULE_FIRMWARE()` when DSP support is enabled.

## Risks And Edge Cases

- Many magic constants are hardware/Windows-driver-derived with partial comments. Reordering, shortening delays, or changing readbacks can regress specific Creative card variants.
- `dspio_scp()` validates `len > SCP_MAX_DATA_WORDS`, but `len` is in bytes while `SCP_MAX_DATA_WORDS` is a word count. Existing callers mostly pass small `sizeof(unsigned int)` payloads, but this boundary is easy to misuse.
- SCP response waiting depends on unsolicited DSP callbacks clearing `spec->wait_scp`; missing unsolicited setup or power-state issues can turn GET requests into one-second timeouts.
- `sbz_dsp_startup_check()` tries to reload by calling `snd_hda_codec_init(codec)` after detecting `0xa1a2a3a4` patterns, but in the loop the check address is not reset before re-reading. That may reduce the effectiveness of retries or inspect unintended addresses.
- `dspxfr_one_seg()` mixes DMA and ChipIO remainder writes and relies on frame-size alignment. Firmware format errors, incorrect address range macros, or DMA timeouts can leave partial DSP state.
- Several control handlers return `0` even after programming hardware changes, which may suppress userspace change notifications for some controls.
- Alt output/input paths assume `mem_base` is valid when `ca0132_use_pci_mmio()` or quirk data requires MMIO. Probe/init code outside this chunk must guarantee mapping before these handlers run.
- Desktop stream remapping waits only briefly for 8051 allocation table entries to become valid; slow hardware can leave no-audio until later reinitialization.
- The chunk ends mid-`ca0132_mmio_init_sbz()`, so final behavior of SBZ/ZxR/R3D MMIO initialization and subsequent codec lifecycle functions must be reconciled with the next chunk.

## Test Signals

Useful validation signals for this chunk are mostly integration/hardware oriented:

- Kernel logs show firmware selection, `ca0132 DSP downloaded and running`, and no `ca0132 failed to download DSP`, `DSP not initialized properly`, DMA timeout, or stream remap failure messages.
- ALSA exposes the expected controls for the selected quirk: base mixers, effect switches, VoiceFX, alt output/input enum, surround channel config, EQ/SVM/sliders, AE-5 filter/gain, or ZxR gain as appropriate.
- Playback works on speakers, rear headphone, front headphone, surround channels, S/PDIF, and What U Hear where supported; custom channel maps match the physical speaker layout.
- Jack insertion/removal changes output after the delayed HP callback and reports jack state to userspace after `block_report` is cleared.
- Capture works for digital mic, rear mic, rear line-in, and front mic where present; CrystalVoice, Voice Focus, Noise Reduction, mic boost, and VIP source changes do not break active capture streams.
- Suspend/resume or reboot after Windows does not leave no-audio, stale GPIO, stale DSP DMA channels, or uninitialized `0xa1a2a3a4` DSP memory patterns.
- Module unload/shutdown does not pop loudly and leaves GPIO, streams, EAPD, unsolicited events, and power states in quirk-appropriate safe states.
