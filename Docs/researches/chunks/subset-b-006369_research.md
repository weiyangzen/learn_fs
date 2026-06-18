# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc269.c lines 1-7514

## Scope

This chunk covers the front and middle of the Realtek HD-audio codec driver for ALC269-family codecs. It starts at the file header and includes:

- ALC269-family variant constants, BIOS auto-configuration parsing, and standard 44.1 kHz stream descriptors.
- Codec-specific init/shutdown/depop sequences for ALC269VB, ALC282, ALC283, ALC256, ALC225/ALC287/ALC245, ALC222, ALC294, and the default path.
- ALC5505 DSP coefficient access, boot/halt/resume handling, and integration into codec suspend/resume.
- Headset button, headset jack, mute LED, mic-mute LED, GPIO, VREF, coefficient-bit LED, and input hotkey fixups.
- Large sets of model-specific `struct hda_fixup` implementations and the `alc269_fixups[]` dispatch table.
- The start of the subsystem-id quirk table `alc269_fixup_tbl[]`, ending mid-table around HP, ASUS, Sony, Lifebook, Realtek reference, Samsung, and related platform entries.

The source path is under a Ceph client snapshot, but this file is Linux ALSA HDA Realtek codec support. It does not implement CephFS or distributed-filesystem behavior.

## Purpose

`alc269.c` supplies the Realtek ALC269-family specialization layer used by the shared Realtek HDA parser in `realtek.c`/`realtek.h`. The code adapts the generic HD-audio codec model to many laptop, AIO, desktop, and handheld designs where BIOS pin defaults, amplifier wiring, jack-detection behavior, LEDs, companion speaker amplifiers, or power sequencing are wrong or incomplete.

The first part of the chunk defines the common behavior for codec bring-up and shutdown. It selects SSID pins for auto-configuration, handles headset button events on a vendor-specific jack NID, performs jack-presence-dependent headphone depop sequences, restores Realtek coefficient defaults on some codecs, toggles low-power/high-power amp modes, and preserves pop-noise-sensitive ordering around mute, pin control, EAPD, GPIO, and coefficient writes.

The middle of the chunk is a quirk library. Each fixup is a small function or static pin/verb table that changes parser input or runtime behavior for a known board. These fixups correct headset mic wiring, internal/dock mic defaults, speaker DAC routing, mute and mic-mute LED wiring, companion amp registration, input hotkeys, jack-detect restarts, external amp GPIO pulses, and vendor-specific coefficient sequences.

The end of the chunk maps quirk IDs to `struct hda_fixup` entries and begins mapping PCI subsystem IDs to those fixup IDs. Later code outside this chunk completes the quirk tables and probe path, but the material here defines most of the behavior that later lookup tables select.

## Important APIs, Types, And Functions

Core setup and shutdown:

- `alc269_parse_auto_config()` chooses the SSID pin list based on `spec->codec_variant`, ignores NID `0x1d`, and delegates parsing to `alc_parse_auto_config()`.
- `alc269_44k_pcm_analog_playback` and `alc269_44k_pcm_analog_capture` override analog streams to fixed 44.1 kHz for specific Lenovo hardware via `alc269_fixup_pcm_44k()`.
- `alc269vb_toggle_power_output()`, `alc269_shutup()`, `alc282_shutup()`, `alc283_shutup()`, `alc256_shutup()`, `alc225_shutup()`, `alc222_shutup()`, and `alc_default_shutup()` implement variant-specific suspend/shutdown ordering.
- `alc282_init()`, `alc283_init()`, `alc256_init()`, `alc225_init()`, `alc222_init()`, `alc_default_init()`, and `alc294_init()` restore coefficients and bring headphone/speaker paths up with jack-sensitive sleeps and amp/pin control writes.
- `alc285_hp_init()` and `alc294_hp_init()` run longer headphone depop procedures, polling coefficient state with bounded retry loops.

Headset, jack, and hotkey handling:

- `alc_headset_btn_keymap[]` maps headset button bits to play/pause, voice command, volume up, and volume down.
- `alc_headset_btn_callback()` decodes unsolicited response bits and reports button state through `snd_hda_jack_set_button_state()`.
- `alc_enable_headset_jack_key()` and `alc_disable_headset_jack_key()` program codec-dependent coefficients that enable or disable headset key detection.
- `alc_fixup_headset_jack()` enables the headset button callback during `HDA_FIXUP_ACT_PRE_PROBE`, binds the keymap or creates a jack kcontrol during build, and turns key detection on.
- `gpio2_mic_hotkey_event()` reports a synthetic press/release for mic mute hotkeys that arrive as GPIO or line unsolicited events.
- `alc_register_micmute_input_device()` allocates and registers an input device named `Microphone Mute Button`; the HP and Lenovo hotkey fixups unregister it on `HDA_FIXUP_ACT_FREE`.

LED and GPIO support:

- `alc_update_vref_led()`, `vref_mute_led_set()`, and `vref_micmute_led_set()` drive mute LEDs by changing a mic pin VREF between Hi-Z and 80%.
- `led_power_filter()` keeps LED VREF pins programmed even when runtime power management puts the node in D3.
- `alc_update_coef_led()`, `coef_mute_led_set()`, and `coef_micmute_led_set()` drive LEDs by changing Realtek coefficient bits.
- HP-family helpers such as `alc269_fixup_hp_mute_led*()`, `alc236_fixup_hp_gpio_led()`, `alc285_fixup_hp_mute_led_coefbit()`, `alc245_fixup_hp_mute_led_*_coefbit()`, and `alc285_fixup_hp_coef_micmute_led()` populate `struct alc_spec` LED fields and register ALSA HDA generic LED class devices.
- GPIO-related fixups configure `spec->gpio_mask`, `spec->gpio_dir`, `spec->gpio_data`, and playback/automute hooks for external speaker amps and LED polarity.

DSP and power management:

- `alc5505_coef_set()` and `alc5505_coef_get()` access 32-bit ALC5505 DSP registers through HDA coefficient verbs on NID `0x51`.
- `alc5505_dsp_halt()`, `alc5505_dsp_back_from_halt()`, and `alc5505_dsp_init()` stop/start DSP CPU, PLL, DRAM, clock, and ringbuffer state. With `HALT_REALTEK_ALC5505` defined, suspend/resume hooks are NOPs because init leaves the DSP halted for power saving.
- `alc269_suspend()` runs DSP suspend if present and then delegates to `alc_suspend()`.
- `alc269_resume()` handles ALC269VB power-output sequencing, calls `snd_hda_codec_init()`, syncs the regmap, updates power status, and resumes the ALC5505 DSP if required.

Companion amplifier integration:

- `comp_generic_fixup()` initializes an HDA component manager, installs `comp_generic_playback_hook()`, and frees the component manager on fixup free.
- `find_cirrus_companion_amps()` probes ACPI for Cirrus CSC3554/CSC3556/CSC3557 devices, detects I2C or SPI resources, derives the component match string, and initializes the component manager with the discovered amp count.
- `cs35l41_fixup_i2c_*()`, `cs35l41_fixup_spi_*()`, `tas2781_fixup_*()`, and `yoga7_14arb7_fixup_i2c()` are small wrappers selecting bus, HID, match string, and amplifier count.
- Samsung and LG Gram ALC298 helpers program vendor coefficient sequences and install playback hooks that enable speaker amps on stream open and disable them on close.

Fixup tables:

- The large enum beginning at `ALC269_FIXUP_GPIO2` assigns stable indexes for every fixup entry.
- `alc269_fixups[]` maps each ID to a `HDA_FIXUP_FUNC`, `HDA_FIXUP_PINS`, `HDA_FIXUP_PINCTLS`, or `HDA_FIXUP_VERBS` entry and uses `.chained`, `.chained_before`, and `.chain_id` to compose board-specific behavior.
- `alc269_fixup_tbl[]` starts mapping vendor/subsystem IDs to fixups using `SND_PCI_QUIRK()` and `HDA_CODEC_QUIRK()`. In this chunk it covers many Acer, Dell, HP, ASUS, Sony, Fujitsu Lifebook, Realtek reference, Samsung, and other entries; the table continues after line 7514.

## Control Flow

Normal codec initialization starts later in the probe path outside this chunk, but the flow defined here is clear. Probe allocates an `alc_spec`, identifies a codec variant, applies matching fixups by model, SSID, vendor, or pin table, and then runs the generic Realtek parser. `alc269_parse_auto_config()` supplies the ALC269-family pin interpretation rules to that parser. Fixups marked for `HDA_FIXUP_ACT_PRE_PROBE` modify parser inputs before auto-config, for example by applying pin tables, setting parser flags, overriding DAC connection lists, suppressing auto-mute/auto-mic, setting LED fields, or registering jack callbacks.

After parser setup, `HDA_FIXUP_ACT_PROBE` fixups install behavior that depends on parsed state: PCM playback hooks, automute hooks, preferred DAC choices, hotkey input devices, component-manager amp binding, and amp sequence initialization. `HDA_FIXUP_ACT_INIT` fixups then run whenever the codec is initialized or resumed. These init actions program volatile coefficients, restart combo-jack detection, pulse GPIOs for amps, restore external-speaker routing, or reset vendor-specific state that firmware or another OS may leave behind.

The headset-button path is event-driven. `alc_fixup_headset_jack()` enables unsolicited events on NID `0x55`; `alc_headset_btn_callback()` decodes the unsolicited response and reports ALSA jack button states. The build phase either binds the keymap to the detected headphone pin or creates a `Headset Jack` kcontrol.

Shutdown and suspend flows are deliberately ordered around jack sense. Variant shutdown functions first select an HP pin, often defaulting to `0x21` when parser output is missing. If the HP jack is present, they switch internal amp coefficients to low- or high-power depop mode, mute amp output, delay, optionally clear the pin widget control, delay again, then disable EAPD and call `alc_shutup_pins()`. Several paths skip clearing pins when `spec->no_shutup_pins` is set because some platforms click or lose function if pins are forced down.

Resume flow in `alc269_resume()` handles ALC269VB quirks before and after `snd_hda_codec_init()`, syncs cached writes with `snd_hda_regmap_sync()`, calls `hda_call_check_power_status()`, and then handles any ALC5505 DSP resume path. Individual `HDA_FIXUP_ACT_INIT` callbacks may run during `snd_hda_codec_init()`.

Companion amp flow is split between setup and playback. ACPI/I2C/SPI fixups initialize `spec->comps` and set a playback hook. During stream actions, hooks call either generic component-manager playback notifications or model-specific coefficient enable/disable sequences. Some fixups also disable amps before programming them to avoid unsafe speaker output during initialization.

The quirk-table flow is data-driven. A selected entry in `alc269_fixups[]` may run a function, apply pin defaults, send verbs, and then chain to another entry. This lets a board combine, for example, headset mic pin correction, Dell/HP LED wiring, DAC routing, and CS35L41/TAS2781 speaker amp registration without duplicating complete fixup functions.

## State And Persistence Behavior

This chunk maintains in-memory codec state only. There is no filesystem persistence.

Key state lives in `struct alc_spec`, which is assigned to `codec->spec`. The code reads or writes fields including:

- `codec_variant`, selecting variant-specific pin SSID handling and init/shutdown behavior.
- `has_hs_key`, `no_shutup_pins`, `ultra_low_power`, `en_3kpull_low`, `done_hp_init`, `has_alc5505_dsp`, and `num_speaker_amps`.
- Generic parser state under `spec->gen`, including stream descriptors, `pcm_playback_hook`, `automute_hook`, `hp_automute_hook`, preferred DAC pairs, auto-mute flags, input mux state, vmaster mute LED hooks, and parsed auto pin config.
- LED state such as `mute_led_nid`, `cap_mute_led_nid`, `mute_led_polarity`, `micmute_led_polarity`, `mute_led_coef`, and `mic_led_coef`.
- GPIO state in `gpio_mask`, `gpio_dir`, and `gpio_data`.
- Hotkey state in `kb_dev` and `alc_mute_keycode_map`.
- Component-manager state in `spec->comps`.

Hardware state is primarily volatile codec register/coefficient state. Fixups write HDA verbs such as `AC_VERB_SET_PIN_WIDGET_CONTROL`, `AC_VERB_SET_AMP_GAIN_MUTE`, `AC_VERB_SET_EAPD_BTLENABLE`, GPIO unsolicited masks, coefficient index/proc-coef pairs, and Realtek coefficient-extension registers. Many comments note that another OS, BIOS, cold boot, warm reboot, S3, or S4 can leave these coefficients in different states, so init/resume fixups explicitly restore defaults or clear known-bad bits.

Some state persists across runtime suspend through cached HDA pin targets and `codec->power_filter`. LED VREF updates temporarily power nodes and then rely on cached pin controls being restored when D3 transitions would otherwise clear them.

Resource lifetime is action-driven. Fixups that allocate input devices do so during pre-probe and release them on `HDA_FIXUP_ACT_FREE`. Component-manager fixups allocate at pre-probe and free on fixup free. LED class devices are registered through generic HDA helpers and tied to codec lifetime. Playback hooks do not allocate persistent stream state; they use action callbacks to toggle amps/GPIO/coefficients.

## Dependencies And Integration Points

This code depends on ALSA HDA core and the shared Realtek codec layer:

- `struct hda_codec`, `struct hda_fixup`, `struct hda_verb`, `struct hda_pintbl`, `struct hda_jack_callback`, `struct hda_jack_keymap`, `struct hda_pcm_stream`, and HDA verb constants come from ALSA HDA headers included through `realtek.h`.
- Generic Realtek helpers such as `alc_parse_auto_config()`, `alc_get_hp_pin()`, `alc_shutup_pins()`, `alc_auto_setup_eapd()`, `alc_suspend()`, `alc_write_coef_idx()`, `alc_read_coef_idx()`, `alc_update_coef_idx()`, `alc_update_coefex_idx()`, `alc_process_coef_fw()`, `alc_fixup_headset_mode()`, `alc_fixup_headset_mic()`, `alc_fixup_hp_gpio_led()`, `alc_fixup_inv_dmic()`, and many more are defined in shared Realtek code.
- ALSA jack, control, stream, and parser helpers include `snd_hda_jack_detect()`, `snd_hda_jack_detect_enable_callback()`, `snd_hda_jack_bind_keymap()`, `snd_hda_jack_add_kctl()`, `snd_hda_gen_update_outputs()`, `snd_hda_gen_hp_automute()`, `snd_hda_gen_add_mute_led_cdev()`, and `snd_hda_gen_add_micmute_led_cdev()`.
- ACPI/DMI integration appears through `dmi_find_device()`, `acpi_dev_get_first_match_dev()`, `i2c_acpi_client_count()`, `acpi_spi_count_resources()`, fwnode property reads, and HDA component-manager APIs.
- Linux input integration appears through `input_allocate_device()`, `input_register_device()`, `input_report_key()`, `input_sync()`, and `input_unregister_device()`.
- The file includes helper snippets `../helpers/thinkpad.c`, `../helpers/ideapad_hotkey_led.c`, `../helpers/hp_x360.c`, and `../helpers/ideapad_s740.c`, so some fixup functions called in `alc269_fixups[]` are compiled into this translation unit from those helper files.

Integration points with user-visible behavior include ALSA mixer control names, jack controls, LED class devices, keyboard mic-mute events, PulseAudio/PipeWire-visible input/output routing, speaker/headphone automute, and suspend/resume audio reliability.

## Risks And Edge Cases

The highest-risk area is sequencing around analog output depop. Many init and shutdown paths depend on exact ordering and sleeps between coefficient writes, amp mute/unmute, pin widget changes, and jack-sense checks. Reordering these steps can introduce loud pops, no output after resume, or codec stalls; the ALC256 shutdown comment explicitly warns that 3k pulldown handling must happen before clearing the pin.

Fixup chaining is powerful but fragile. A later chain can override parser flags, pin configs, DAC preferences, or hooks set by an earlier fixup. When adding entries, the order of `.chained`, `.chained_before`, and `.chain_id` matters for whether parser inputs are visible before auto-config and whether final hook pointers are overwritten.

Many platform fixes use undocumented Realtek coefficient values. These are hard to validate statically and may differ between close codec IDs. Vendor-ID checks in headset-key enable/disable and codec-ID checks in shared-SSID fixups are important because programming the wrong coefficient register can break jack detection, speakers, or microphone routing.

Hardware ID reuse is common. The chunk contains explicit split fixups such as Lenovo C940 vs Yoga Duet 7 and Yoga Book 9i vs Yoga 9i, plus ASUS GA403U logic that depends on codec vendor ID. Broad SSID entries risk applying the wrong amp, DAC, or mic workaround on a reused board ID.

External amplifier integration can fail silently if ACPI HID, bus type, fwnode properties, or component match strings do not match the actual device. Playback hooks may then toggle no amp, too few amps, or the wrong bus component. The Samsung/LG Gram sequences also intentionally disable amps before init to reduce physical risk.

LED and hotkey support crosses power-management boundaries. VREF-driven LEDs need `led_power_filter()` because runtime D3 can reset pin controls. Input devices allocated by hotkey fixups must be unregistered exactly once on free. GPIO unsolicited masks and callback registration must target the correct node, usually the AFG or a line pin.

DAC routing fixes must avoid DACs without amp volume control. Several fixups explicitly remove DAC `0x06` or force speakers/headphones to DAC `0x02`/`0x03`. Incorrect preferred pairs can produce too-low audio, missing volume controls, or confusing userspace mixer names.

`snd_hda_override_amp_caps()` in `alc256_decrease_headphone_amp_val()` subtracts from the queried step count and offset. It assumes the original capabilities are large enough; if used on an incompatible node, underflowed values would corrupt exposed volume ranges.

The `alc269_fixup_tbl[]` in this chunk is only the beginning of hardware matching. Because the table continues later, research or audits must not treat line 7514 as the complete matching surface for this driver.

## Test Signals

Useful validation signals for this chunk are mostly hardware and kernel-log based:

- Driver probe should identify the expected codec variant and apply the intended fixup for the platform SSID or codec quirk without fallback surprises.
- `dmesg` should be free of codec warnings such as failed amp-cap overrides, component bind failures, missing ACPI amp buses, input device registration failures, or codec verb timeouts.
- Headphone plug/unplug should update jack state, switch speaker/headphone outputs correctly, avoid pops on boot, suspend, resume, and shutdown, and preserve headset mic routing.
- Headset buttons should emit the mapped input events when `ALC225_FIXUP_HEADSET_JACK` or related headset-key fixups are active.
- Speaker playback should enable companion amps only while streams are active for Samsung/LG/component-manager paths, and speakers should remain muted or powered down on stream close where hooks require that.
- Mute and mic-mute LEDs should track ALSA master/capture mute state across runtime suspend, S3, and S4.
- Mic-mute hotkey platforms should expose a `Microphone Mute Button` input device and generate `KEY_MICMUTE` press/release events.
- Internal mic boost-limiting fixups should expose reduced noisy boost levels only on internal microphone pins.
- Model-specific DAC-routing fixes should expose working speaker/headphone volume controls and avoid controls tied to unused or no-amp DAC nodes.
- Regression checks should cover cold boot after Windows or firmware because several coefficient-reset fixups exist specifically for state that survives warm reboot.
