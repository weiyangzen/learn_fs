# subset-b-006371 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc662.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc662.c

## Purpose
`alc662.c` is the Realtek HD-audio codec driver for ALC662 and compatible codecs, including ALC272/663/665/667/668/670/671/891/892/897. It layers model-specific pin fixes, GPIO behavior, headset handling, and beep routing on top of the shared Realtek helper in `realtek.c` and the generic HDA parser.

## APIs, Types, and Functions
The file exports no public symbols; its module entry is `alc662_driver` through `module_hda_codec_driver()`. Important functions are `alc662_probe()`, `alc662_parse_auto_config()`, `alc272_fixup_mario()`, `alc662_fixup_led_gpio1()`, `alc662_fixup_usi_headset_mic()`, `alc662_fixup_aspire_ethos_hp()`, `alc671_fixup_hp_headset_mic2()`, `alc897_fixup_lenovo_headset_mic()`, `alc897_fixup_lenovo_headset_mode()`, `alc_fixup_headset_mode_alc662()`, `alc_fixup_headset_mode_alc668()`, and `alc662_fixup_csl_amp()`. The main tables are `alc662_fixups[]`, `alc662_fixup_tbl[]`, `alc662_fixup_models[]`, `alc662_pin_fixup_tbl[]`, and `snd_hda_id_alc662[]`.

## Control Flow
Probe allocates `struct alc_spec` with mixer node `0x0b`, installs `alc_eapd_shutup`, sets `HDA_PINCFG_NO_HP_FIXUP`, applies a PLL workaround, optionally installs the ALC668 coefficient restore hook, calls `alc_pre_init()`, selects model/PCI/pin fixups, runs `PRE_PROBE`, parses Realtek SKU data, enables PC beep when allowed, optionally renames Acer ALC272X, parses BIOS pin configuration through `alc_parse_auto_config()`, adds the correct beep amp route, and finally runs `PROBE` fixups. Runtime operations are inherited from `alc_build_controls()`, `snd_hda_gen_build_pcms()`, `alc_init()`, `snd_hda_jack_unsol_event()`, `alc_resume()`, and `alc_suspend()`.

## State and Persistence Behavior
Persistent state lives in `struct alc_spec`: parse flags, GPIO mask/dir/data, headset hooks, init hooks, beep node, PLL fields, and generic parser state. GPIO LED machines can force AFG power to D0 while GPIO data is asserted. Coefficient and pin-control changes are cached where the shared helpers use HDA cache APIs; fixup-selected flags persist through generic parser output and init/resume.

## Dependencies and Integration Points
The file depends on `realtek.h`, ALSA HDA core, generic parser, jack callbacks, fixup tables, PCI subsystem quirks, and Realtek coefficient/GPIO helpers. It integrates with board-specific policy through PCI quirks, model strings, and pin quirk signatures.

## Risks
Most risk is quirk ordering and hard-coded NID accuracy. Incorrect pin tables can disable speakers or expose nonexistent inputs. Headset-mode fixups touch VREF, input amp caps, automute hooks, and pin caching; regressions can cause missing mic detection, pops, or stuck headphone routing. GPIO LED power filtering can affect runtime power if GPIO state is stale.

## Test Signals
Validate successful binding for every `snd_hda_id_alc662[]` ID, expected controls/PCMs after generic parsing, beep controls on allowed systems, headset CTIA/OMTP and headphone-mic switching, GPIO mute LEDs, suspend/resume with EAPD shutup, and the listed Acer/ASUS/Dell/HP/Lenovo/Clevo/Zotac/ASRock quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc662.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc680.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc680.c

## Purpose
`alc680.c` is a compact Realtek ALC680 HD-audio codec module. It provides the codec ID match, probe routine, and standard operation table needed to bind ALC680 hardware to the shared Realtek/generic HDA implementation.

## APIs, Types, and Functions
The local functions are `alc680_parse_auto_config()` and `alc680_probe()`. `alc680_codec_ops` wires probe/remove/control/PCM/init/jack/resume/suspend/power callbacks to shared Realtek and generic HDA helpers. `snd_hda_id_alc680[]` contains the single codec ID `0x10ec0680`.

## Control Flow
Probe calls `alc_alloc_spec(codec, 0)` because ALC680 has no analog loopback mixer, then runs `alc_parse_auto_config(codec, NULL, NULL)` via `alc680_parse_auto_config()`. If parsing fails, `snd_hda_gen_remove()` tears down the partially allocated generic state. All later control flow is delegated to shared helpers: `alc_build_controls()`, `snd_hda_gen_build_pcms()`, `alc_init()`, `snd_hda_jack_unsol_event()`, `alc_resume()`, and `alc_suspend()`.

## State and Persistence Behavior
State is the shared `struct alc_spec` allocated by `alc_alloc_spec()`. With no local fixups, persistence is limited to generic parser state, cached HDA verbs managed by shared helpers, and any state initialized by `alc_init()` or runtime power callbacks.

## Dependencies and Integration Points
The file depends only on Linux module infrastructure and `realtek.h`. Its integration point is the HDA codec bus via `module_hda_codec_driver()` and the Realtek namespace import.

## Risks
The file is intentionally minimal, so the main risks are generic parser assumptions for a codec with no AA-loopback mixer and regression in shared Realtek helpers. A wrong mixer node would create invalid controls; here `0` explicitly suppresses that route.

## Test Signals
Useful signals are successful module binding to ALC680, clean auto-configuration from BIOS pins, no AA-loopback controls, expected playback/capture PCM creation, jack unsolicited event handling, and suspend/resume without leaked codec state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc680.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc861.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc861.c

## Purpose
`alc861.c` supports Realtek ALC861 and ALC660-revision HD-audio codecs. It wraps the shared Realtek parser with ALC861-specific SSID pin ordering, beep setup, EAPD power handling, and a small set of laptop/desktop quirks.

## APIs, Types, and Functions
Key functions are `alc861_parse_auto_config()`, `alc861_fixup_asus_amp_vref_0f()`, and `alc861_probe()`. The fixup enum and tables `alc861_fixups[]` and `alc861_fixup_tbl[]` cover FSC Amilo, ASUS W7J/Z35HL/A6Rp/vendor laptops, HP DX2200, and Haier/Uniwill systems. `alc861_codec_ops` and `snd_hda_id_alc861[]` register ALC660 rev `0x100340` and ALC861.

## Control Flow
Probe allocates `alc_spec` with mixer node `0x15`, enables beep NID `0x23` when Realtek custom defines allow PC beep, installs `alc_power_eapd`, runs `alc_pre_init()`, selects PCI fixups, applies `PRE_PROBE`, parses pins with ignored NID `0x1d` and SSID ports `{0x0e,0x0f,0x0b}`, configures beep amp `0x23` output when analog is present, then applies `PROBE` fixups. `alc861_fixup_asus_amp_vref_0f()` runs at init and forces pin `0x0f` VREF50 because some ASUS laptops use that pin to control the amplifier.

## State and Persistence Behavior
State is in `struct alc_spec`, especially `gen.beep_nid`, `power_hook`, `gen.keep_vref_in_automute`, parsed autocfg, and fixup-selected global codec flags such as `no_jack_detect`. Pin and EAPD changes are replayed by shared init/power hooks.

## Dependencies and Integration Points
The file depends on `realtek.h`, shared Realtek coefficient/GPIO/EAPD/beep helpers, the generic parser, PCI quirk matching, and HDA jack events. It imports namespace `SND_HDA_CODEC_REALTEK`.

## Risks
The VREF amplifier quirk is hardware-specific and can break capture or speaker power if applied too broadly. Disabling jack detect for HP DX2200/ASUS chains affects automute behavior. Beep routing depends on correct NID and amp direction.

## Test Signals
Validate ALC660/861 binding, generated playback/capture controls, EAPD power-off on suspend, beep controls on cdefine-enabled systems, ASUS VREF amplifier behavior, FSC pin override routing, no-jack-detect systems, and error cleanup through `snd_hda_gen_remove()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc861.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc861vd.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc861vd.c

## Purpose
`alc861vd.c` supports Realtek ALC660-VD and ALC861-VD codecs, which are related to ALC882 and add an independent DAC. It supplies VD-specific ignored pins, SSID ports, shutdown behavior, beep routing, and board quirks.

## APIs, Types, and Functions
Important functions are `alc861vd_parse_auto_config()`, `alc861vd_fixup_dallas()`, `alc660vd_fixup_asus_gpio1()`, and `alc861vd_probe()`. `alc861vd_fixups[]` contains Dallas pin-cap overrides and ASUS GPIO1 reset behavior. `alc861vd_fixup_tbl[]` maps HP TX1000, ASUS A7-K, and Toshiba L30-149. `snd_hda_id_alc861vd[]` matches ALC660-VD and ALC861-VD.

## Control Flow
Probe allocates `alc_spec` with mixer node `0x0b`, enables cdefine beep NID `0x23`, sets `spec->shutup = alc_eapd_shutup`, runs `alc_pre_init()`, selects and applies `PRE_PROBE` fixups, parses auto config with ignored NID `0x1d` and SSID ports `{0x15,0x1b,0x14}`, configures beep through input index `0x05` on node `0x0b`, and applies `PROBE` fixups. Dallas fixups override caps for pins `0x18` and `0x19` to exclude VREF80 before parsing.

## State and Persistence Behavior
State lives in `struct alc_spec`: shutup callback, beep NID, GPIO masks, parsed routes, and fixup modifications. GPIO setup happens at pre-probe and is later written by shared init. EAPD shutup persists as the suspend/remove policy.

## Dependencies and Integration Points
The file depends on the shared Realtek helper API, generic HDA parser/control/PCM lifecycle, HDA fixup framework, jack event handling, and PCI subsystem quirk matching.

## Risks
Pin capability overrides must match hardware exactly; removing VREF80 changes microphone bias options. ASUS GPIO1 handling mutates both `gpio_mask` and GPIO data via common helpers. A wrong beep amp index or mixer node can create silent or invalid beep controls.

## Test Signals
Check codec binding for both IDs, BIOS pin parsing with the VD SSID order, EAPD shutup on suspend, beep controls when analog is present, HP/Toshiba Dallas mic bias behavior, ASUS GPIO1 reset behavior, and normal jack unsolicited events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc861vd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc880.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc880.c

## Purpose
`alc880.c` is the Realtek ALC880 codec driver. It combines the shared Realtek generic-parser path with legacy ALC880 quirk compatibility for old laptops, desktops, and multi-stack board layouts.

## APIs, Types, and Functions
Important functions are `alc880_unsol_event()`, `alc880_parse_auto_config()`, `alc880_fixup_vol_knob()`, and `alc880_probe()`. The fixup tables `alc880_fixups[]`, `alc880_fixup_tbl[]`, and `alc880_fixup_models[]` describe GPIO1/GPIO2, EAPD coefficient, volume-knob, ASUS/LG/Uniwill/Fujitsu/Medion/TCL, and 3/5/6-stack pin-layout policies. `snd_hda_id_alc880[]` matches codec ID `0x10ec0880`.

## Control Flow
Probe allocates an `alc_spec` using mixer node `0x0b`, sets `need_dac_fix` and beep NID `0x01`, runs `alc_pre_init()`, selects model or PCI fixup, applies `PRE_PROBE`, parses auto config with ignored NID `0x1d` and SSID ports `{0x15,0x1b,0x14}`, sets beep amp on node `0x0b` input index `0x05` when analog output exists, and applies `PROBE`. Runtime operations use the shared Realtek lifecycle except unsolicited events are shifted right by two before dispatch because ALC880 reports broken event values.

## State and Persistence Behavior
State is held in shared `struct alc_spec`, notably DAC fix policy, beep NID, GPIO masks, and fixup-applied pin defaults. Volume-knob support registers a jack callback on NID `0x21`; pin and coefficient fixups persist through HDA init verb replay and shared `alc_init()`.

## Dependencies and Integration Points
The driver depends on `realtek.h`, generic parser/build helpers, HDA fixup tables, PCI quirks, and ALSA control callbacks. Model strings expose old static layouts like `3stack`, `5stack-digout`, and `6stack-automute`.

## Risks
This file has high legacy compatibility risk. Many fixups override complete pin tables because firmware was broken; changing order or defaults can remove speakers, SPDIF, surround, or automute. The unsolicited-event shift is codec-specific and must not leak to other models.

## Test Signals
Validate ALC880 binding, corrected jack events, 3/5/6-stack model overrides, GPIO/EAPD systems, volume knob updates to Master Playback Volume, beep controls, multi-channel line-out routing, SPDIF layouts, and suspend/resume without pops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc880.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc882.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc882.c

## Purpose
`alc882.c` supports the ALC882 family and compatible codecs, including ALC883/885/887/888/889/898/1150/S1200A/1220 and ALC662 rev2. It provides extensive quirk coverage for flexible DAC routing, EAPD/GPIO setup, Mac VREF behavior, headset/bass handling, and dual-codec boards.

## APIs, Types, and Functions
Key functions are `alc889_fixup_coef()`, `alc885_fixup_macpro_gpio()`, `alc889_fixup_dac_route()`, Mac VREF helpers, `alc882_fixup_no_primary_hp()`, `alc1220_fixup_gb_x570()`, `alc1220_fixup_clevo_p950()`, `alc1220_fixup_clevo_pb51ed()`, `alc887_fixup_asus_jack()`, `alc882_parse_auto_config()`, and `alc882_probe()`. Important tables are `alc882_fixups[]`, `alc882_fixup_tbl[]`, `alc882_fixup_models[]`, `alc882_pin_fixup_tbl[]`, and `snd_hda_id_alc882[]`.

## Control Flow
Probe allocates `alc_spec` with mixer node `0x0b`, applies PLL init to ALC883-like variants, runs `alc_pre_init()`, selects model/PCI/pin fixups, applies `PRE_PROBE`, parses Realtek custom defines, enables PC beep when allowed, parses BIOS pins using ignored NID `0x1d` and SSID ports `{0x15,0x1b,0x14}`, adds beep amp routing, then applies `PROBE`. Several fixups act in multiple phases: DAC route overrides fake connection lists during parse and restore them after probe; Mac VREF/GPIO and coefficient writes run at init; build-phase dual-codec helpers rename controls.

## State and Persistence Behavior
State is shared `struct alc_spec`: PLL configuration, beep node, GPIO masks, parser flags, generated routes, and build/init hooks. Connection-list overrides alter parser-visible topology. Coefficients, VREF pin targets, and GPIO values are re-applied through cached verbs and `alc_init()`.

## Dependencies and Integration Points
The file depends on shared Realtek helpers, HDA generic parser, fixup framework, PCI and pin-quirk matching, ALSA channel maps, and codec namespace exports for dual-codec helper reuse.

## Risks
Risks concentrate in hard-coded NIDs and multi-phase topology overrides. Wrong DAC routing can silently break speakers or headphones. Apple and Clevo/Gigabyte VREF/GPIO/coefficient changes are platform-specific. Dual-codec suppression avoids control conflicts but can remove automute/auto-mic features.

## Test Signals
Test binding for every ID, Acer DAC-route recovery, Apple VREF models, ALC1220 Gigabyte/Clevo dual-codec naming/control behavior, ASUS bass channel maps, EAPD/GPIO quirks, front headphone no-presence systems, beep controls, and suspend/resume with parser routes intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc882.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/realtek.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/realtek.c

## Purpose
`realtek.c` is the shared implementation used by Realtek HD-audio codec family modules. It provides coefficient access, GPIO and LED helpers, EAPD and amplifier initialization, SKU/subsystem parsing, generic parser integration, beep controls, codec renaming, headset-mode state machines, dual-codec helpers, and suspend/resume behavior.

## APIs, Types, and Functions
Exported APIs include `alc_read/write/update_coefex_idx()`, `alc_get_coef0()`, `alc_process_coef_fw()`, GPIO helpers and fixups, `alc_fix_pll*()`, `alc_fill_eapd_coef()`, `alc_auto_setup_eapd()`, `alc_find_ext_mic_pin()`, `alc_shutup_pins()`, `alc_eapd_shutup()`, `alc_auto_init_amp()`, `alc_get_hp_pin()`, SKU helpers, `alc_build_controls()`, `alc_init()`, `alc_suspend()`, `alc_resume()`, `alc_parse_auto_config()`, `alc_alloc_spec()`, dual-codec and bass/headset/LED fixups. Internal helpers implement rename tables, beep controls, Dell XPS13 shutdown, CTIA/OMTP detection, and headset mode transitions.

## Control Flow
Codec modules call `alc_alloc_spec()` during probe, then usually `alc_pre_init()`, fixup selection, `alc_auto_parse_customize_define()`, `alc_parse_auto_config()`, and phase-specific fixups. `alc_init()` optionally re-runs EAPD coefficient setup after hibernation, calls any codec init hook, invokes generic init with deferred verbs, applies PLL/EAPD/GPIO/amp setup, applies stored verbs, and runs init fixups. Headset callbacks derive a new mode from jack presence and capture mux selection, run codec-specific coefficient sequences, update pin controls, then refresh generic outputs.

## State and Persistence Behavior
The persistent state is `struct alc_spec` from `realtek.h`: generic parser state, SKU fields, GPIO masks/data, LED state, coefficient mutex, headset pins/current mode/type, hooks, PLL fields, cached coef0, component parent, and flags. Coefficient access is serialized and power-managed by the `coef_mutex` guard. HDA cached writes and regmap sync handle resume persistence; some cached state, such as `coef0` and GPIO data, is held in memory.

## Dependencies and Integration Points
Dependencies include ALSA HDA core, generic parser, jack framework, HDA beep, LED class devices, PCI/DMI/ACPI-visible subsystem data, side-codec component namespace, and Cirrus/TI-style HDA component integration via headers. Other Realtek codec modules import this namespace.

## Risks
The file centralizes many hardware-specific sequences. Incorrect coefficient masks, missing locks, or wrong fixup phase can break entire codec families. Headset detection includes long sleeps and codec-specific magic values; race or resume mistakes can produce pops, wrong mic standard, or muted headphones. SKU parsing and dual-codec control renaming affect user-visible control names and UCM profiles.

## Test Signals
Static signals include exported symbol coverage, locked coefficient accesses, error cleanup in `alc_alloc_spec()` and parser paths, and correct fixup phase use. Runtime signals include parser success, expected controls/PCMs, EAPD/GPIO behavior, LED brightness hooks, beep allow/deny behavior, headset mode transitions, Dell/dual-codec quirks, and suspend/resume including hibernation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/realtek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/realtek.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/realtek.h

## Purpose
`realtek.h` defines the shared interface and private state contract for Realtek HD-audio codec modules. It is the bridge between per-codec files, ALSA HDA generic parser infrastructure, Realtek coefficient/GPIO/headset helpers, and side-codec component support.

## APIs, Types, and Functions
Important types are `struct alc_customize_define`, `struct alc_coef_led`, `struct alc_spec`, and `struct coef_fw`. `struct alc_spec` embeds `struct hda_gen_spec` as its first field and stores Realtek SKU fields, parse flags, GPIO and LED state, coefficient mutex, headset pin/mode/type state, init/power/shutup hooks, PLL fix data, optional keyboard input state, and HDA component parent state. The header declares coefficient helpers, GPIO helpers, common init/power/parser/build APIs, beep helpers under `CONFIG_SND_HDA_INPUT_BEEP`, common fixups, and device-specific cross-codec fixups.

## Control Flow
Per-codec modules include this header, allocate `alc_spec` with `alc_alloc_spec()`, manipulate fields before parser execution, and then call shared lifecycle functions. Inline `alc_pre_init()` maps to `alc_fill_eapd_coef()`. Inline coefficient locking helpers power up the codec, lock `spec->coef_mutex`, and power down after unlock.

## State and Persistence Behavior
The header defines all persistent in-memory Realtek state. `coef0` is cached after first read. GPIO data and LED masks persist across init callbacks. Headset mode/type fields prevent redundant coefficient changes and are reset by fixups on resume. Hook function pointers allow codec modules to persist custom init, suspend, or power actions.

## Dependencies and Integration Points
Includes cover Linux ACPI/PCI/DMI/I2C/SPI/input/LED infrastructure, ALSA core/jack/HDA APIs, local HDA parser headers, generic codec code, and side-codec component headers. Export declarations in `realtek.c` use the `SND_HDA_CODEC_REALTEK` namespace consumed by codec modules.

## Risks
Because `hda_gen_spec` must remain first in `alc_spec`, layout changes are risky. Missing initialization of new fields in `alc_alloc_spec()` can affect every Realtek codec. The header exposes many low-level helpers, so misuse of NIDs, coefficient masks, or fixup phases by codec modules can cause hardware regressions.

## Test Signals
Compile coverage across all Realtek modules, namespace import/export consistency, `CONFIG_SND_HDA_INPUT_BEEP` on/off builds, lockdep around coefficient access, and successful generic parser use through embedded `hda_gen_spec` are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/realtek.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/senarytech.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/senarytech.c

## Purpose
`senarytech.c` is the HD-audio codec driver for Senarytech SN6186. It is a generic-parser-based codec driver with vendor initialization verbs, default pin fixups, optional beep controls, EAPD management, GPIO LED support fields, and a communication-stability workaround.

## APIs, Types, and Functions
The private type is `struct senary_spec`, embedding `hda_gen_spec` and storing EAPD pins, dynamic EAPD mode, parse flags, and GPIO LED masks/polarity. Important functions include `senary_auto_parse_beep()`, `senary_auto_parse_eapd()`, `senary_init_verb()`, `senary_auto_turn_eapd()`, `senary_auto_vmaster_hook()`, `senary_init_gpio_led()`, `senary_init()`, `senary_shutdown()`, `senary_remove()`, `senary_suspend()`, and `senary_probe()`. Tables include default pin config, fixups, empty quirk table, and `snd_hda_id_senary[]`.

## Control Flow
Probe allocates `senary_spec`, initializes generic parser state, scans EAPD-capable pin widgets, sets `own_eapd_ctl`, chooses SN6186 defaults and mixer node `0x15`, applies default pin fixup when no quirk matches, runs vendor init verbs, installs a vmaster hook, parses pin defaults, optionally adds beep controls from the first beep widget with output amp support, runs generic auto-config parsing, enables synchronous bus writes and bus reset for resume stability, then runs `PROBE` fixups. Init runs generic init, GPIO LED setup, vendor verbs, static EAPD enable, and init fixups.

## State and Persistence Behavior
State persists in `senary_spec`: up to four EAPD pins, dynamic-EAPD policy, GPIO LED values, parse flags, and generated routes. Vendor verbs and pin-cap overrides are reissued during init. Shutdown/suspend always turn EAPD off to avoid speaker noise.

## Dependencies and Integration Points
Dependencies include ALSA HDA core, generic parser, auto parser, jack support, optional HDA beep, module infrastructure, and SN6186 codec ID `0x1fa86186`. It integrates with generic HDA controls/PCMs and vmaster mute hooks.

## Risks
Vendor-specific writes to NID `0x1b` and pin-cap override for `0x19` are opaque hardware sequences. Enabling `sync_write` and bus reset changes bus behavior globally for stability. The EAPD scan stops at four pins, so codecs with more EAPD pins would be partially controlled.

## Test Signals
Check SN6186 binding, default pin override, generic controls/PCMs, beep controls when configured, EAPD vmaster toggling, suspend/remove speaker silence, resume without single-command stalls, and no regressions from forced sync writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/senarytech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/si3054.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/si3054.c

## Purpose
`si3054.c` is the ALSA HD-audio driver for Silicon Labs 3054/3055 modem codecs and compatible modem codec IDs. Unlike speaker codecs, it exposes a modem PCM and two modem control switches over vendor register-node verbs.

## APIs, Types, and Functions
The private type is `struct si3054_spec`, storing the international chip flag. Register access is abstracted by `GET_REG`, `SET_REG`, and `SET_REG_CACHE` over SI3054 vendor verbs. Important functions are `si3054_switch_get()`, `si3054_switch_put()`, `si3054_build_controls()`, `si3054_pcm_open()`, `si3054_pcm_prepare()`, `si3054_build_pcms()`, `si3054_init()`, `si3054_probe()`, and `si3054_remove()`. `si3054_modem_mixer[]` exposes Off-hook and Caller ID switches.

## Control Flow
Probe only allocates `si3054_spec`. Build-controls registers modem switches. Build-PCMs creates a `HDA_PCM_TYPE_MODEM` PCM with mono playback and capture streams. PCM open constrains rates to 8000, 9600, and 16000 Hz and sets a minimum period size. Prepare writes line rate and stream tags into modem registers, then programs the HDA stream. Init registers the vendor write verb with hdac regmap, resets the codec, initializes stream format/rate/levels, waits briefly for MEI ready, configures GPIO polarity and line registers, logs line-frame readiness, and records chip international status.

## State and Persistence Behavior
Persistent driver state is minimal. Switch writes use `SET_REG_CACHE`, so GPIO control state is cached for replay. Runtime PCM prepare writes line-rate and stream-tag state directly for each stream. `spec->international` records chip ID capabilities after init.

## Dependencies and Integration Points
The file depends on ALSA HDA core, `hda_local.h`, PCM constraints, vendor verbs, and HDA modem PCM type. It integrates with several vendor IDs for SI3054-compatible modem devices.

## Risks
Register access uses codec-specific node verbs; wrong register values can break modem line state. Init tolerates MEI-not-ready and FDT-not-ready conditions, so degraded hardware can continue with warnings. PCM rates are narrow and must match modem expectations.

## Test Signals
Validate binding for all listed modem IDs, creation of `Si3054 Modem` PCM as modem type, rate constraint enforcement, off-hook/caller-ID switch persistence, successful MEI-ready polling, line-frame diagnostics, and correct stream setup for playback and capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/si3054.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Kconfig

## Purpose
`side-codecs/Kconfig` declares build configuration for HD-audio side-codec support. It covers shared Cirrus side-codec library/test options plus CS35L41, CS35L56, and TAS2781 amplifier support over I2C or SPI.

## APIs, Types, and Functions
This is Kconfig metadata, not C API. Symbols include `SND_HDA_CIRRUS_SCODEC`, `SND_HDA_CIRRUS_SCODEC_KUNIT_TEST`, `SND_HDA_SCODEC_CS35L41`, bus-specific `SND_HDA_SCODEC_CS35L41_I2C/SPI`, `SND_HDA_SCODEC_COMPONENT`, CS35L56 symbols and calibration debugfs option, and TAS2781 I2C/SPI symbols.

## Control Flow
User-visible bus options select hidden core objects and their dependencies. CS35L41 bus drivers depend on ACPI, EFI, SND_SOC, and I2C or SPI, then select the shared CS35L41 HDA core, SND_SOC CS35L41 library, and CS amp library. CS35L56 options select FW CS DSP, generic HDA, shared CS35L56 support, Cirrus side-codec library, and amp library. TAS2781 options select the matching comms/firmware libraries and CRC support.

## State and Persistence Behavior
Kconfig state is build-time configuration. Tristate selections determine which modules are built in, loadable, or absent. Comments warn that module autoloading may require enabling side-codec drivers when core HDA is built in.

## Dependencies and Integration Points
The file integrates the side-codec directory with kernel configuration, ALSA HDA generic support, ACPI, EFI, SND_SOC, I2C/SPI buses, firmware DSP support, debugfs, and vendor codec libraries.

## Risks
Incorrect dependencies can create link failures or runtime probe paths without required bus, ACPI, firmware, or calibration support. Hidden tristate cores selected by bus options must match Makefile object names.

## Test Signals
Build matrix coverage for built-in and module combinations, KUnit enabling for Cirrus side-codec tests, I2C/SPI variants, CS35L56 debugfs on/off, and no unmet-symbol warnings are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Makefile

## Purpose
`side-codecs/Makefile` maps side-codec Kconfig symbols to kernel objects for shared libraries, component glue, and vendor amplifier drivers under the HD-audio codec tree.

## APIs, Types, and Functions
This file defines object composition rather than functions. It adds `-I$(src)/../../common` to subdirectory CFLAGS and defines object lists such as `snd-hda-cirrus-scodec-y`, `snd-hda-scodec-cs35l41-y`, `snd-hda-scodec-cs35l41-i2c-y`, `snd-hda-scodec-cs35l56-y`, `snd-hda-scodec-component-y`, and TAS2781 variants.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` lines to include the selected side-codec objects. Core drivers such as CS35L41 and CS35L56 are built from common HDA implementation files plus property/shared files, while I2C/SPI wrappers build bus-specific probe modules. The component glue is controlled by `CONFIG_SND_HDA_SCODEC_COMPONENT`.

## State and Persistence Behavior
The Makefile has build-time state only. Object membership determines module names, link boundaries, exported namespace availability, and which side-codec code can bind at runtime.

## Dependencies and Integration Points
It integrates with the `Kconfig` symbols in the same directory and with source files such as `cirrus_scodec.c`, `cs35l41_hda.c`, `hda_component.c`, `cs35l56_hda.c`, and `tas2781_hda.c`. The include path supports shared common headers.

## Risks
Kconfig/Makefile symbol drift causes selected features not to build or missing objects at link time. Core/bus object splits must preserve exported symbols and namespaces. Tests depend on `snd-hda-cirrus-scodec-test-y` matching the KUnit source.

## Test Signals
Run representative `allyesconfig`/module builds for side-codec symbols, verify generated module names, ensure no missing exported symbols, and confirm KUnit test object inclusion when `SND_HDA_CIRRUS_SCODEC_KUNIT_TEST` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.c

## Purpose
`cirrus_scodec.c` is a small shared library for Cirrus HD-audio side codecs. It currently provides speaker-ID GPIO decoding used to select tuning or calibration variants for multi-amp systems.

## APIs, Types, and Functions
The exported API is `cirrus_scodec_get_speaker_id(struct device *dev, int amp_index, int num_amps, int fixed_gpio_id)`, exported in namespace `SND_HDA_CIRRUS_SCODEC`. It uses GPIO descriptor APIs: `gpiod_get_index()`, `gpiod_count()`, `gpiod_get_value_cansleep()`, and `gpiod_put()`.

## Control Flow
If `fixed_gpio_id >= 0`, the function reads one unnamed GPIO index and returns that value. Otherwise it counts `spk-id-gpios`, divides them evenly across `num_amps`, computes the current amp's base index, validates divisibility, then reads each GPIO bit for that amp and assembles the speaker ID as a little-endian bitfield. If no GPIOs are present it returns `-ENOENT`.

## State and Persistence Behavior
The function is stateless. GPIO descriptors are acquired, read, and released during each call. The only persistence is external firmware/device-tree/ACPI property state that defines GPIO descriptors.

## Dependencies and Integration Points
Dependencies are Linux device logging, GPIO consumer APIs, module infrastructure, and `cirrus_scodec.h`. It integrates with side-codec drivers that need speaker IDs for firmware file naming or hardware configuration.

## Risks
The function assumes `gpiod_count()` is divisible by `num_amps`; malformed firmware returns `-EINVAL`. Bit ordering is implicit and must match board design. A failing GPIO read aborts with the first error and may prevent firmware selection.

## Test Signals
KUnit coverage in `cirrus_scodec_test.c`, fixed-GPIO and named-array paths, no-GPIO `-ENOENT`, invalid divisibility `-EINVAL`, multiple amps with shared/non-shared GPIO sets, and correct descriptor release are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.h

## Purpose
`cirrus_scodec.h` declares the public helper API for the Cirrus side-codec library.

## APIs, Types, and Functions
The sole declaration is `cirrus_scodec_get_speaker_id(struct device *dev, int amp_index, int num_amps, int fixed_gpio_id)`. It returns a non-negative speaker ID or a negative errno. The header uses include guards and leaves `struct device` as an externally visible kernel type expected from including code.

## Control Flow
There is no control flow in the header. Consumers include it to call the GPIO speaker-ID helper implemented in `cirrus_scodec.c`.

## State and Persistence Behavior
The header defines no state. It documents the call boundary for stateless speaker-ID lookup.

## Dependencies and Integration Points
It integrates `cirrus_scodec.c` with side-codec drivers and KUnit tests. The corresponding implementation exports the function in namespace `SND_HDA_CIRRUS_SCODEC`, so module users must import that namespace.

## Risks
The small surface is low risk, but signature changes would require synchronized updates to tests and every side-codec caller. Since `struct device` is not forward-declared here, consumers must include headers that define it before or indirectly through this header path.

## Test Signals
Compile all consumers, verify namespace imports, and run the Cirrus side-codec KUnit suite to confirm the declared function contract remains stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec_test.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec_test.c

## Purpose
`cirrus_scodec_test.c` is a KUnit suite for the Cirrus side-codec speaker-ID helper. It builds faux GPIO and amplifier devices, attaches software-node GPIO references, and verifies speaker-ID parsing over many amp/GPIO sharing layouts.

## APIs, Types, and Functions
Test state is held in `struct cirrus_scodec_test_gpio` and `struct cirrus_scodec_test_priv`. GPIO shim callbacks implement input-only behavior: get direction, direction input, get value, reject output/set operations, and accept non-output pin configs. Helpers include `cirrus_scodec_test_create_gpio()`, `cirrus_scodec_test_set_gpio_ref_arg()`, `cirrus_scodec_test_set_spkid_swnode()`, `cirrus_scodec_test_spkid_parse()`, `cirrus_scodec_test_no_spkid()`, and `cirrus_scodec_test_case_init()`.

## Control Flow
Each test creates a faux GPIO device and faux amp device. Parameterized cases build `spk-id-gpios` references for `num_amps * gpios_per_amp`, optionally reusing GPIO indices for shared groups. For every amp and every possible bit pattern, the test sets fake GPIO pin state and asserts that `cirrus_scodec_get_speaker_id()` returns the expected value. A separate case confirms that a device without speaker-ID GPIOs returns `-ENOENT`.

## State and Persistence Behavior
State is per-test KUnit allocation and faux-device devres. Cleanup actions destroy faux devices and remove software nodes. GPIO pin state is an in-memory bitmask on the fake gpiochip.

## Dependencies and Integration Points
Dependencies include KUnit resources, faux devices, software nodes, GPIO driver APIs, pinconf helpers, and `cirrus_scodec.h`. The module imports namespace `SND_HDA_CIRRUS_SCODEC`.

## Risks
The test focuses on named `spk-id-gpios`; it does not cover the fixed unnamed GPIO path or malformed counts returning `-EINVAL`. Shared-GPIO logic is subtle and could miss invalid firmware layouts outside the parameter matrix.

## Test Signals
Passing `snd-hda-cirrus-scodec-test`, all parameter descriptions, all amp counts from two to four, one to four GPIOs per amp, all-shared and pair-shared cases, and the no-GPIO negative case are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.c

## Purpose
`cs35l41_hda.c` is the common Cirrus Logic CS35L41 smart-amplifier side-codec driver for HD-audio systems. It handles ACPI/property discovery, reset/OTP/errata setup, boost and GPIO configuration, speaker-ID and calibration data, DSP firmware loading, ALSA controls, HDA component binding, playback hooks, IRQ recovery, and runtime/system power management.

## APIs, Types, and Functions
Exported APIs are `cs35l41_hda_probe()`, `cs35l41_hda_remove()`, `cs35l41_hda_pm_ops`, `cs35l41_get_speaker_id()`, and `cs35l41_hda_parse_acpi()`. Major internal areas include firmware filename search (`cs35l41_request_firmware_*()`), tuning params, calibration, DSP init/shutdown, playback hooks, channel mapping, ID verification, suspend/resume, ALSA controls, ACPI DSM mute notifications, component bind/unbind, IRQ handlers, property application, and ACPI reading.

## Control Flow
Probe allocates `struct cs35l41_hda`, reads ACPI or extra DSD properties, handles reset GPIO, software-resets the device, waits for OTP boot, verifies chip ID/revision, applies errata and OTP unpack, reads EFI calibration, mutes, initializes work/mutex/runtime PM, applies boost/GPIO/channel properties, then registers as an HDA component. Bind connects to the parent HDA codec, sets firmware type, optionally autoloads DSP firmware, creates ALSA controls, installs pre/main/post playback hooks and ACPI notification handling, and creates a device link. Playback open resumes runtime PM; prepare configures mixer and starts amp/DSP; post-prepare globally enables and unmutes; cleanup pauses/mutes/releases errors; close schedules deferred firmware load if needed and autosuspends.

## State and Persistence Behavior
Persistent state is `struct cs35l41_hda`: regmap, GPIOs, hardware config, codec/component linkage, ACPI subsystem ID, firmware type, speaker ID, DSP state, work flags, playback flag, mute override, tuning gain, calibration data, IRQ errors, and runtime PM state. Regmap cache is marked dirty around reset/hibernate and synced on resume. Firmware request/load state is protected by `fw_mutex` and deferred work.

## Dependencies and Integration Points
Dependencies include ALSA HDA/generic/component glue, ASoC CS35L41 library, CS DSP firmware framework, Cirrus amp calibration library, ACPI/EFI, GPIO, regmap IRQ, runtime PM, SPI/I2C bus wrappers, and firmware files under `cirrus/cs35l41-*.wmfw` and `.bin`.

## Risks
Firmware filename fallback order, ACPI property indexing, reset sharing, SPI speed gating, and runtime PM all affect whether speakers work. Loading/unloading firmware during playback is blocked but deferred work races must stay locked. External-boost systems without VSPK switch do not support suspend. IRQ setup failures leave amp errors unrecoverable without reboot.

## Test Signals
Validate probe on I2C/SPI variants, property parsing for multi-amp arrays, speaker-ID selection, firmware autostart on/off, fallback firmware names, tuning parameter validation, calibration application, ALSA DSP controls, ACPI mute notifications, playback hook ordering, runtime/system suspend/resume, IRQ fault release, and cleanup on every probe error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.h

## Purpose
`cs35l41_hda.h` defines the public state and function interface for the CS35L41 HD-audio side-codec core used by bus-specific I2C/SPI wrappers and the common HDA component code.

## APIs, Types, and Functions
Important constants are `CS35L41_MAX_ACCEPTABLE_SPI_SPEED_HZ`, `DEFAULT_AMP_GAIN_PCM`, and `DEFAULT_AMP_GAIN_PDM`. Types include packed calibration structures `cs35l41_amp_cal_data` and `cs35l41_amp_efi_data`, speaker-position enum, GPIO-function enum, `enum control_bus`, main `struct cs35l41_hda`, and `enum halo_state`. Declared APIs are `cs35l41_hda_probe()`, `cs35l41_hda_remove()`, `cs35l41_get_speaker_id()`, `cs35l41_hda_parse_acpi()`, and exported PM ops.

## Control Flow
Bus wrappers call `cs35l41_hda_probe()` with device name, instance id, IRQ, regmap, and control bus. The common driver stores runtime state in `struct cs35l41_hda`; remove and PM callbacks consume the same state. The ACPI parse and speaker-ID helpers are exposed for reuse and testing.

## State and Persistence Behavior
`struct cs35l41_hda` persists the device, regmap, reset/chip-select GPIOs, hardware config, parent HDA codec, IRQ/index/channel fields, firmware and DSP state, ACPI data, mute override, bus type, bypass flag, tuning gain, calibration data, and validity flags. This state coordinates firmware work, playback hooks, PM, and component binding.

## Dependencies and Integration Points
The header depends on ACPI, EFI, regulator/GPIO/device APIs, CS35L41 sound definitions, Cirrus amp library, CS DSP firmware headers, and WMFW definitions. It integrates with I2C/SPI side-codec modules and namespace exports from `cs35l41_hda.c`.

## Risks
The main risk is shared-structure drift: adding fields requires correct initialization, locking, cleanup, and PM handling in the implementation. Packed EFI calibration layout must match firmware data exactly. GPIO function enum spelling and values must match ACPI property expectations.

## Test Signals
Compile I2C/SPI wrappers, verify PM ops export, exercise ACPI parser and speaker-ID helper, validate calibration structure size/packing, and run probe/remove suspend/resume tests using both control buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.h -->
