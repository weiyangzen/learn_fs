# sources/distributed-fs/ceph-client/sound/hda/codecs/ca0132.c lines 9231-10093

## Scope

This chunk covers the final initialization, configuration, teardown, and registration section of the Creative CA0132 HD-audio codec driver. The selected range begins inside `ca0132_mmio_init_sbz()` after it has selected the first quirk-specific MMIO values, then continues through AE-5/AE-7 register programming, quirk-specific alternate initialization, the main codec init path, DBPro-specific init/free dispatch, per-quirk pin and converter topology setup, runtime verb allocation, Sound Blaster Z versus ZxR detection, codec operation callbacks, HDA device ID registration, and module declaration.

The file is located under a Ceph client source snapshot, but this chunk is Linux ALSA HDA codec code. It does not implement CephFS behavior or distributed-filesystem state.

## Purpose

The code binds the generic ALSA HDA codec lifecycle to CA0132 and related Creative Sound Core3D hardware variants. It turns a detected HDA codec and optional PCI subsystem quirk into concrete driver state: pin configuration, DAC/ADC node arrays, mixer/control selection, PCI region 2 MMIO availability, DSP download state, delayed jack work, init and exit verb sequences, and the callback table exported to the HDA codec core.

The most important purpose of the chunk is to sequence hardware initialization safely. Desktop cards such as Sound Blaster Z, ZxR, Recon3D, AE-5, and AE-7 need extra GPIO, 8051, PLL/PMU, chipio, and MMIO writes around the standard HDA verb sequences and DSP download. Integrated or non-desktop codecs use a simpler path. The ZxR DBPro daughter board is treated as a special reduced-function codec path with separate init, control, PCM, and free dispatch.

The range also defines the final module boundary. `ca0132_codec_ops` exposes probe/remove/build/init/suspend callbacks, `snd_hda_id_ca0132` matches codec ID `0x11020011`, and `module_hda_codec_driver(ca0132_driver)` registers the driver with the HDA codec framework.

## Important APIs, Types, And Functions

- `ca0132_mmio_init_sbz()` finishes Sound Blaster Z / ZxR / Recon3D PCI region 2 programming. The chunk starts after the initial zeroing and first quirk switch; it writes two selected values to `spec->mem_base + addr[cur_addr + i]`, then selects either `ca0113_mmio_init_data_zxr` or `ca0113_mmio_init_data_sbz` and writes the remaining MMIO data.
- `ca0132_mmio_init_ae5()` writes the AE-5 MMIO initialization table and has AE-7-specific branches for the `0x1c` preamble and the `0x20c` value at table index 21.
- `ca0132_mmio_init()` dispatches MMIO initialization by quirk. It routes `QUIRK_R3D`, `QUIRK_SBZ`, and `QUIRK_ZXR` to the SBZ-style table and `QUIRK_AE5` to the AE-5 table.
- `ca0132_ae5_register_set_addresses` and `ca0132_ae5_register_set_data` are small register scripts used by `ae5_register_set()`.
- `ae5_register_set()` performs additional AE-5/AE-7 register setup with mixed byte and dword MMIO writes, 8051 direct and PLL/PMU writes, and `ca0113_mmio_command_set*()` commands. It uses different initial byte values and command IDs for AE-7.
- `ca0132_alt_init()` centralizes quirk-specific pre-DSP setup for desktop/alternate-function codecs. It calls `ca0132_alt_vol_setup()` first, then performs SBZ, R3DI, R3D, AE-5, AE-7, and ZxR-specific GPIO, chipio, PLL/PMU, desktop verb, and pre-DSP setup.
- `ca0132_init()` is the main runtime init callback for all non-DBPro variants. It handles DSP reload detection, MMIO initialization, power management, AE register setup, parameter/flag reset, base and quirk-specific verb sequences, DSP download, widget capability refresh, defaults, pin initialization, input/output selection, jack sync, and PlayEnhancement restoration after resume.
- `dbpro_init()` initializes only DBPro digital output/input and configured analog input paths.
- `ca0132_free()` cancels delayed jack work, powers the codec, performs quirk-specific chip shutdown, writes base exit verbs, resets the DSP if loaded through `ca0132_exit_chip()`, unmaps PCI MMIO when present, and frees dynamic verb and spec allocations.
- `dbpro_free()` performs DBPro power-state shutdown and frees the same dynamic allocations.
- `ca0132_config()` configures the codec topology. It sets default DACs, `struct hda_multi_out` state, applies quirk-specific pin configuration tables, fills output pins, input pins, ADCs, digital NIDs, unsolicited event tags, shared mic/output NIDs, and default headphone auto-switch state.
- `ca0132_prepare_verbs()` assigns static init verb arrays, conditionally assigns desktop init verbs for PCI MMIO cards, allocates `spec->spec_init_verbs`, and installs an EAPD-related verb.
- `sbz_detect_quirk()` refines `QUIRK_SBZ` into `QUIRK_ZXR` or `QUIRK_ZXR_DBPRO` based on HDA codec subsystem ID.
- `ca0132_codec_probe()` allocates and initializes `struct ca0132_spec`, detects quirks, selects mixer tables and codec names, enables alternate controls/functions/MMIO flags, maps PCI region 2, initializes the chip and topology, prepares verbs, parses autoconfig pins, and registers unsolicited jack handling.
- `ca0132_codec_remove()`, `ca0132_codec_build_controls()`, `ca0132_codec_build_pcms()`, and `ca0132_codec_init()` are thin dispatchers that route DBPro to DBPro-specific implementations and all other quirks to the normal CA0132 paths.
- `ca0132_codec_suspend()` cancels pending delayed headphone work.
- `ca0132_codec_ops`, `snd_hda_id_ca0132`, and `ca0132_driver` connect the static functions in this file to the HDA codec driver core.

Relevant local state comes from `struct ca0132_spec`: quirk access via `codec->fixup_id`, `base_init_verbs`, `base_exit_verbs`, `chip_init_verbs`, `desktop_init_verbs`, dynamically allocated `spec_init_verbs`, `autocfg`, `multiout`, `out_pins`, `dacs`, `input_pins`, `adcs`, `dig_out`, `dig_in`, unsolicited event tags, `curr_chip_addx`, DSP state flags, current mixer/effect values, `unsol_hp_work`, `use_pci_mmio`, `mem_base`, `use_alt_functions`, and `use_alt_controls`.

## Control Flow

Probe is the construction path. `ca0132_codec_probe()` allocates `struct ca0132_spec`, stores it in `codec->spec`, and points `spec->codec` back to the HDA codec. It calls `snd_hda_pick_fixup()` with the CA0132 quirk tables. If the result is initially `QUIRK_SBZ`, `sbz_detect_quirk()` further distinguishes regular Sound Blaster Z, ZxR, and ZxR DBPro by `codec->core.subsystem_id`.

After quirk detection, probe sets HDA core behavior flags (`pcm_format_first` and `no_sticky_stream`), initializes `spec->dsp_state` to `DSP_DOWNLOAD_INIT`, and chooses one mixer table. Desktop cards use `desktop_mixer`; R3DI uses `r3di_mixer`; default CA0132 uses `ca0132_mixer`; DBPro intentionally skips normal mixer assignment in this switch. A second switch enables `use_alt_controls`, `use_alt_functions`, and `use_pci_mmio` for desktop PCI variants, enables alternate controls/functions without PCI MMIO for R3DI, and clears all three for the default path.

If PCI support is compiled and the quirk requested PCI MMIO, probe maps BAR/region 2 with `pci_iomap(codec->bus->pci, 2, 0xC20)`. Mapping failure logs a warning and changes the fixup to `QUIRK_NONE`, but it does not recompute the earlier `use_alt_controls`, `use_alt_functions`, or `use_pci_mmio` booleans. Probe then assigns base init/exit verb arrays, initializes `unsol_hp_work`, calls `ca0132_init_chip()`, configures pins/topology with `ca0132_config()`, allocates and fills dynamic verbs through `ca0132_prepare_verbs()`, parses HDA pin defaults into `spec->autocfg`, and calls `ca0132_setup_unsol()`. Any error after dynamic setup falls through to `ca0132_codec_remove()` for cleanup.

Runtime initialization enters through `ca0132_codec_init()`. DBPro takes `dbpro_init()`, which only initializes the configured digital and analog input/output widgets. Other variants enter `ca0132_init()`. If the driver believes the DSP is already downloaded, `ca0132_init()` queries hardware with `dspload_is_loaded()`. A missing DSP marks `dsp_reload` and returns the state to `DSP_DOWNLOAD_INIT`; a still-loaded DSP short-circuits init and, for SBZ, runs `sbz_dsp_startup_check()` before returning.

For a full normal init, `ca0132_init()` resets `dsp_state` to `DSP_DOWNLOAD_INIT` unless it is already `DSP_DOWNLOAD_FAILED`, invalidates `curr_chip_addx`, runs PCI MMIO init if `use_pci_mmio` is set, enters a scoped HDA power-management context, performs AE-5/AE-7 register setup, initializes driver parameters and flags, writes base init verbs, and runs `ca0132_alt_init()` for alternate-function codecs. It then downloads DSP firmware with `ca0132_download_dsp()`, refreshes widget capabilities, applies quirk-specific default controls, initializes every configured output and input pin, writes non-alt chip verbs and vendor parameter verbs for simple codecs, does SBZ GPIO setup, writes `spec_init_verbs`, selects current input/output routing through either alt or normal selectors, syncs jack reports, and restores the PlayEnhancement switch after a resume-triggered DSP reload.

Alternate initialization is table-driven by quirk. SBZ initializes GPIO, performs SBZ pre-DSP setup, then writes chip and desktop verb sequences. R3DI initializes and sets GPIO state, marks DSP status as downloading, performs R3DI pre-DSP setup, writes chip verbs, and sends a `0x6ff` vendor write. R3D performs its pre-DSP setup and writes chip/desktop verbs. AE-5 and AE-7 initialize GPIO and PLL/PMU state, write chip and desktop verbs, perform model-specific chipio writes, and send an MMIO command. ZxR writes PLL/PMU state, writes chip/desktop verbs, then performs ZxR surround-DAC setup.

Teardown enters through `ca0132_codec_remove()`. DBPro calls `dbpro_free()`. Other variants call `ca0132_free()`, which cancels delayed headphone work, powers up the codec, runs a quirk-specific exit path, writes base exit verbs, resets the DSP if `dspload_is_loaded()` reports it loaded, powers down the codec, unmaps PCI MMIO if present, and frees both dynamic verb storage and the spec object. Suspend is lighter: it only cancels delayed headphone work and leaves hardware restoration to the later init/resume path.

The final static registration path is straightforward. The HDA core matches codec ID `0x11020011`, then calls the callback table in `ca0132_codec_ops`; module metadata advertises GPL licensing and the Creative Sound Core3D codec description.

## State And Persistence Behavior

This chunk persists no filesystem data. All state is volatile kernel driver state attached to `codec->spec`, the HDA codec object, PCI MMIO mappings, ALSA control state, and hardware registers.

Persistent-for-device-lifetime state created in probe includes:

- `codec->spec` and `spec->codec`, which bind all later callbacks to `struct ca0132_spec`.
- Quirk-derived flags `use_alt_controls`, `use_alt_functions`, and `use_pci_mmio`.
- Mixer table selection in `spec->mixers[0]` and `spec->num_mixers`.
- `spec->mem_base`, an `__iomem` mapping of PCI region 2 for desktop cards when available.
- Base/chip/desktop/spec init verb pointers and dynamic `spec_init_verbs`.
- Topology arrays and fields: DACs, ADCs, output pins, input pins, digital in/out NIDs, `multiout`, shared NIDs, unsolicited tags, and headphone auto-select default.
- `unsol_hp_work`, initialized once in probe and canceled on suspend/remove.
- DSP control state such as `dsp_state`, `dsp_reload`, `startup_check_entered`, and `curr_chip_addx`.

Runtime initialization mutates hardware and in-memory state. `ca0132_init()` resets `curr_chip_addx`, may reset `dsp_state`, downloads firmware, restores control defaults, initializes pins, and may restore the PlayEnhancement switch when `dsp_reload` was set. It deliberately skips most work when the DSP is already confirmed loaded, preventing duplicate hardware setup during startup-triggered suspend/resume loops.

Teardown frees the lifetime allocations and reverses hardware state. `ca0132_free()` and `dbpro_free()` both free `spec_init_verbs` and `codec->spec`; the normal free path additionally cancels work, writes exit verbs, resets the DSP if needed, and unmaps PCI MMIO. Probe error handling relies on this same remove/free dispatch, so partially initialized state must be safe for the selected quirk path.

The code also writes persistent hardware state outside regular HDA verbs. `writel()` and `writeb()` calls program PCI region 2; `chipio_write()`, `chipio_8051_write_direct()`, `chipio_8051_write_pll_pmu()`, and `snd_hda_codec_write()` alter chip-internal, 8051, PLL/PMU, GPIO, and HDA widget registers. These settings last until reset, shutdown, suspend, or later driver writes.

## Dependencies And Integration Points

This code depends on ALSA HDA codec infrastructure:

- `struct hda_codec`, `struct hda_codec_ops`, `struct hda_codec_driver`, `struct hda_device_id`, `struct hda_verb`, `struct auto_pin_cfg`, `struct hda_multi_out`, and `hda_nid_t`.
- HDA helpers such as `snd_hda_pick_fixup()`, `snd_hda_apply_pincfgs()`, `snd_hda_sequence_write()`, `snd_hda_codec_write()`, `snd_hda_codec_set_name()`, `snd_hda_parse_pin_def_config()`, `snd_hda_query_pin_caps()`, `snd_hda_codec_get_pincfg()`, `snd_hda_jack_report_sync()`, `snd_hda_jack_unsol_event()`, `snd_hda_power_up()`, and `snd_hda_power_down()`.
- HDA constants such as `AC_PINCAP_PRES_DETECT`, `AC_DEFCFG_MISC_NO_PRESENCE`, `AC_VERB_SET_PIN_WIDGET_CONTROL`, and vendor-specific CA0132 verbs and widget IDs from earlier in the file and `ca0132_regs.h`.

It integrates with Linux PCI and MMIO only when `CONFIG_PCI` is available. `pci_iomap()` maps PCI region 2 for desktop cards; `pci_iounmap()` releases it; `writeb()` and `writel()` program offsets below the requested `0xC20` mapping size. Without PCI support, `ca0132_quirk()` and the `ca0132_use_*()` macros collapse to default non-alt behavior.

It depends on many local CA0132 helper functions defined earlier in the file: `ca0132_init_chip()`, `ca0132_init_params()`, `ca0132_init_flags()`, `ca0132_download_dsp()`, `ca0132_refresh_widget_caps()`, `ca0132_setup_unsol()`, `init_output()`, `init_input()`, output/input selection helpers, setup-default helpers, DBPro build/init/free helpers, quirk-specific pre-DSP and exit helpers, DSP load/reset helpers, chipio helpers, GPIO helpers, and MMIO command helpers.

It integrates with firmware loading indirectly through `ca0132_download_dsp()`, which uses the DSP state fields and firmware names defined earlier in the file. The covered chunk decides when the DSP download path runs, when it is skipped, and when resume should restore control state after a reload.

## Risks And Edge Cases

- `ca0132_mmio_init()` dispatches `QUIRK_AE5` to `ca0132_mmio_init_ae5()` but does not include `QUIRK_AE7`, even though `ca0132_mmio_init_ae5()` contains AE-7-specific behavior and probe marks `QUIRK_AE7` as `use_pci_mmio = true`. If this is not compensated elsewhere, AE-7 may skip the intended MMIO table during `ca0132_init()`.
- Probe changes `codec->fixup_id` to `QUIRK_NONE` if `pci_iomap()` fails, but it does not clear the already-computed `spec->use_pci_mmio`, `spec->use_alt_functions`, or `spec->use_alt_controls` flags. Because `ca0132_use_pci_mmio(spec)` reads `spec->use_pci_mmio`, later init can still call MMIO paths with `spec->mem_base == NULL`. That is a high-risk error path for desktop quirks.
- `ca0132_mmio_init_sbz()` and `ca0132_mmio_init_ae5()` assume that address and data tables have compatible lengths and ordering. The SBZ/ZxR path uses an address table larger than the selected data table and starts writing the selected data at the current address index; accidental table edits can silently retarget register writes.
- `ae5_register_set()` writes the first 12 entries as bytes and remaining entries as dwords while sharing the same address table and byte-sized data array. This relies on exact table indexes and data promotion; off-by-one changes would be hardware-visible.
- The main init path does not propagate failure from `ca0132_download_dsp()` directly; it continues into widget refresh, default setup, and pin routing. The DSP state machine likely records failure internally, but callers still receive `0` from `ca0132_init()`.
- `ca0132_config()` sets `num_outputs = 2` for desktop quirks while also filling four `out_pins`. Later initialization loops only over `num_outputs`, so extra pins are probably used by surround selection code rather than generic output init. Changes to `num_outputs` would alter which pins get initialized by the common loop.
- DBPro dispatch bypasses most normal init/free behavior. Any shared state added to probe must either be safe for DBPro cleanup or added to `dbpro_free()`.
- Probe error cleanup calls `ca0132_codec_remove()` even if failure occurs before all fields are populated. Current ordering initializes `unsol_hp_work`, base verbs, chip/topology, and dynamic verbs before the two possible failure points, but future insertions must preserve cleanup safety.
- `ca0132_free()` powers up the codec before running shutdown actions and powers it down afterward. Missing or failed power transitions could leave exit verbs, DSP reset, or quirk-specific chip shutdown incomplete.
- The code has many model-specific magic constants for HDA verbs, chipio addresses, MMIO offsets, subsystem IDs, and PLL/PMU values. Hardware coverage is essential because most of these values are not self-describing and are only partly documented by comments.

## Test Signals

Useful build-time and static signals:

- Compile this file with `CONFIG_SND_HDA_CODEC_CA0132` and `CONFIG_PCI` enabled to cover PCI MMIO desktop paths, and also with PCI disabled or unavailable to cover the macro fallback behavior.
- Enable warnings/static analysis for null `__iomem` use after the `pci_iomap()` failure path, especially calls gated by `spec->use_pci_mmio`.
- Check that each static MMIO address/data table pair has the intended length relationship and that `ca0132_mmio_init()` dispatch covers every quirk that has data in the target init helper.
- Verify that all probe error exits free `spec_init_verbs`, cancel initialized work safely, and do not double-free `codec->spec`.

Useful runtime signals:

- Kernel logs from `codec_dbg()`, `codec_warn()`, and `codec_info()` should show the selected quirk and codec name for SBZ, ZxR, DBPro, R3D, R3DI, AE-5, AE-7, Alienware, and default CA0132 paths.
- On desktop cards, successful init should show working DSP-dependent controls, surround output where supported, headphone/speaker switching, and no MMIO fault or null pointer access during boot or resume.
- Suspend/resume should exercise the early DSP-loaded short-circuit and the `dsp_reload` path. After resume-triggered reload, PlayEnhancement state should be restored by `ca0132_pe_switch_set()`.
- SBZ startup should exercise `sbz_dsp_startup_check()` when init is reentered with a loaded DSP; failure logs should show reload attempts and either "DSP fixed" or a persistent initialization warning.
- Jack insertion/removal should continue to work after init and after suspend because `ca0132_setup_unsol()`, `unsol_hp_work`, `snd_hda_jack_report_sync()`, and suspend cancellation all interact here.
- DBPro hardware should build controls/PCMs through the DBPro dispatchers and should remove cleanly through `dbpro_free()` without normal DSP/MMIO shutdown assumptions.
- ALSA userspace smoke tests should cover playback, capture, SPDIF output/input where configured, mixer enumeration, output source changes, input source changes, and quirk-specific controls for AE-5/AE-7/ZxR/R3DI.
