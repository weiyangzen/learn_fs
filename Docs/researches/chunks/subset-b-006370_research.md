# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc269.c lines 7515-8869

## Scope

This chunk covers the tail of the Realtek ALC269-family HD-audio codec driver. It starts in the main PCI subsystem quirk table at the Samsung Galaxy Book5/Clevo/Lenovo-heavy entries, continues through vendor/model/pin fixup lookup tables, defines the fallback pin quirk table, and ends with the ALC269-family codec probe/remove operations, codec ops, device-id table, module metadata, and `module_hda_codec_driver()` registration.

The earlier chunks define the actual fixup implementations, fixup enum values, `alc269_fixups[]`, suspend/resume hooks, parser helpers, and variant-specific init/shutup routines. This chunk wires those earlier definitions into runtime selection for concrete machines and codec IDs.

## Purpose

The code maps real-world ALC269-compatible systems to the correct fixup IDs and then initializes the codec-specific `alc_spec` state used by the generic HD-audio parser and Realtek helper layer.

The quirk tables solve board integration mismatches that BIOS pin defaults or generic parsing cannot express reliably. Examples in this range include Samsung laptop headphone/amp quirks, extensive Clevo/System76 microphone-presence quirks, Lenovo ThinkPad/Yoga/Legion/ThinkBook amplifier and speaker-routing quirks, Dell/HP/ASUS pin-pattern quirks, and fallback matches for machines where only disabled external pins identify the desired headset behavior.

The probe path is the driver entry point for all IDs listed in `snd_hda_id_alc269[]`. It allocates Realtek private state, classifies the codec variant, installs variant-specific hooks, selects quirk/fixup data from the tables, checks for companion amplifier integration, parses BIOS pin configuration, and applies fixups around auto-configuration.

## Important APIs, Types, and Tables

Core types in this chunk are `struct hda_codec`, `struct alc_spec`, `struct hda_quirk`, `struct hda_model_fixup`, `struct snd_hda_pin_quirk`, `struct hda_codec_ops`, `struct hda_device_id`, and `struct hda_codec_driver`.

The platform quirk tail of `alc269_fixup_tbl[]` maps subsystem vendor/device IDs to fixup IDs through `SND_PCI_QUIRK()` and sometimes `HDA_CODEC_QUIRK()`. This range includes subsystem entries for Samsung, Gigabyte, MSI, Clevo, Lenovo, ASRock, LG, Huawei, TongFang, Xiaomi/Redmi, Framework, Intel NUC, VAIO, and other vendors. `HDA_CODEC_QUIRK()` entries are used where codec SSID is needed to distinguish machines that share a PCI SSID, such as Lenovo Yoga/Legion cases.

`alc269_fixup_vendor_tbl[]` provides coarse vendor-wide fallbacks for Acer, HP, Sony VAIO, Lenovo XPAD, and Huawei Matebook systems. These are picked after the explicit platform and pin tables, so they cover broader families that lack exact IDs.

`alc269_fixup_models[]` exposes user-selectable model names for `model=` override paths. Each string maps to a fixup ID, including generic choices such as `laptop-amic`, `headset-mic`, and `limit-mic-boost`, plus device-specific choices like `tpt440`, `tpt470-dock`, `alc298-samsung-amp`, `alc287-yoga9-bass-spk-pin`, and `alc2xx-fixup-headset-mic`.

The standard pin macros, `ALC225_STANDARD_PINS`, `ALC256_STANDARD_PINS`, `ALC282_STANDARD_PINS`, `ALC290_STANDARD_PINS`, `ALC292_STANDARD_PINS`, `ALC295_STANDARD_PINS`, and `ALC298_STANDARD_PINS`, compress repeated `nid, cfg` tuples in the pin quirk table.

`alc269_pin_fixup_tbl[]` matches exact codec vendor IDs, subsystem vendors, and pin configuration tuples to fixup IDs. It covers common HP/Dell/ASUS/Acer/Lenovo patterns for mic presence, headset wiring, mute LEDs, speaker routing, and disabled lineouts.

`alc269_fallback_pin_fixup_tbl[]` deliberately matches partial pin sets. Its comment documents the key limitation: because partial pin matching can match more than one machine, at most one fallback entry should exist for the same vendor and codec.

Important functions in this chunk are:

- `alc269_fill_coef()`: applies ALC269VB coefficient programming based on `coef0` revision bits.
- `alc269_remove()`: frees component-manager state and delegates generic Realtek removal.
- `alc269_probe()`: allocates and initializes `alc_spec`, classifies codec variants, selects and applies fixups, parses auto configuration, and finalizes probe.
- `alc269_codec_ops`: connects probe/remove/build/init/event/power callbacks to the HDA core.
- `snd_hda_id_alc269[]`, `alc269_driver`, and `module_hda_codec_driver()`: register all supported ALC269-compatible codec IDs with the HDA codec bus.

## Control Flow

At module binding time, the HDA codec core matches a codec vendor ID against `snd_hda_id_alc269[]` and calls `alc269_probe()` through `alc269_codec_ops`.

`alc269_probe()` first calls `alc_alloc_spec(codec, 0x0b)`. On success it sets baseline Realtek state: shared mic VREF pin `0x18`, disables codec node power-save by setting `codec->power_save_node = 0`, enables `en_3kpull_low`, and installs default `shutup` and `init_hook` callbacks.

The vendor-ID switch then classifies many compatible codecs into internal `ALC269_TYPE_*` variants. For base ALC269 (`0x10ec0269`), `alc_get_coef0()` further distinguishes VA/VB/VC/VD revisions, optionally renames some Acer and Lenovo devices to `ALC271X` or `ALC3202`, initializes PLL fallback for unknown revision groups, installs `alc269_shutup`, installs `alc269_fill_coef`, and immediately fills coefficients. Other branches group related codec IDs: ALC280/290, ALC282, ALC283, ALC284/292, ALC293, ALC286/288, ALC298, ALC255, ALC256/HW8326, ALC257, ALC215/245/285/289, ALC225/295/299, ALC287, ALC294-family, ALC300, ALC623, and ALC700-family.

Several variant branches also set behavior flags. ALC256/257/225/287/294/300/700 variants clear `spec->gen.mixer_nid` because those codecs lack the generic analog loopback mixer path. ALC236 disables `en_3kpull_low` on non-AMD PCI systems. ALC294-family and ALC700-family branches write coefficient bits controlling UAJ mic VREF or combo jack auto-trigger behavior.

After variant selection, probe checks node `0x51` parameters for `0x10ec5505`. If found, it marks `spec->has_alc5505_dsp` and switches initialization to `alc5505_dsp_init`.

Fixup selection runs in layers. First `snd_hda_pick_fixup()` considers user model names, explicit PCI/codec quirks, and the full `alc269_fixups[]` table. A special guard clears `ALC282_FIXUP_ASUS_TX300` on ALC294 because ASUS TX300 and ROG Strix G17 share an SSID and that quirk is known to break the latter. Next, exact pin quirks and fallback pin quirks are picked with `snd_hda_pick_pin_fixup()`, followed by vendor-wide fixups. `find_cirrus_companion_amps()` then checks ACPI-described companion amplifiers before pre-probe fixups run.

The remaining probe sequence applies `HDA_FIXUP_ACT_PRE_PROBE`, parses customization defines, enables beep node `0x01` when requested by custom defines, runs `alc269_parse_auto_config()` against BIOS pin data, configures beep amplification when analog output, beep node, and mixer are present, and finally applies `HDA_FIXUP_ACT_PROBE`. Any error after allocation jumps to `alc269_remove()` and returns the failing status.

Removal is short: `alc269_remove()` releases component-manager bindings through `hda_component_manager_free(&spec->comps, &comp_master_ops)` if `spec` exists, then delegates to `snd_hda_gen_remove()`.

## State and Persistence Behavior

Most persistent state lives in `struct alc_spec` attached to `codec->spec`. This chunk initializes `codec_variant`, `shutup`, `init_hook`, `gen.shared_mic_vref_pin`, `gen.mixer_nid`, `gen.beep_nid`, `en_3kpull_low`, and `has_alc5505_dsp`. Those fields affect later init, suspend/resume, jack behavior, analog mixer exposure, beep routing, and power-down behavior.

Hardware state is also changed during probe. `alc269_fill_coef()` writes Realtek coefficient indexes for ALC269VB revisions, including coefficient `0xf`, `0xe`, `0x04`, `0x0d`, and `0x17` depending on `coef0` revision bits. The ALC294 and ALC700 branches also update coefficients `0x6b` and `0x4a`. These writes persist in the codec hardware until reset or later reinitialization and are also reachable through the installed init hooks.

Fixup state is stored in `codec->fixup_id` and in data structures modified by the selected fixup callbacks. The selected fixup can affect parser pin configuration, jack detect behavior, GPIO LED control, companion amp binding, stream caps, and generated controls. `snd_hda_apply_fixup()` runs the selected fixup actions at both pre-probe and probe phases.

The quirk and device-id tables are static read-only module data. They do not mutate at runtime, but their ordering matters because the first matching explicit quirk or pin quirk can decide the selected fixup.

## Dependencies and Integration Points

This chunk depends on the ALSA HDA codec core, the Realtek codec helper layer, generic parser helpers, PCI subsystem metadata, ACPI companion amplifier discovery, and component binding infrastructure.

Important integration points include:

- HDA core matching via `MODULE_DEVICE_TABLE(hdaudio, snd_hda_id_alc269)` and `module_hda_codec_driver(alc269_driver)`.
- Generic parser callbacks through `snd_hda_gen_build_pcms`, `snd_hda_gen_check_power_status`, `snd_hda_gen_stream_pm`, and `snd_hda_gen_remove`.
- Realtek common callbacks such as `alc_build_controls`, `alc_init`, `alc_default_init`, `alc_default_shutup`, `alc269_suspend`, and `alc269_resume`.
- Variant-specific hooks defined earlier in the file: `alc282_init`, `alc283_init`, `alc256_init`, `alc225_init`, `alc294_init`, `alc222_init`, and their matching shutup functions.
- Fixup infrastructure through `snd_hda_pick_fixup()`, `snd_hda_pick_pin_fixup()`, `snd_hda_apply_fixup()`, `alc269_fixups[]`, and model strings.
- Component amplifier support through `find_cirrus_companion_amps()` and `hda_component_manager_free()`, with namespace imports for `SND_HDA_CODEC_REALTEK` and `SND_HDA_SCODEC_COMPONENT`.

## Risks

Quirk ordering is high risk. Some machines share PCI subsystem IDs, and the chunk already has comments documenting Lenovo Yoga/Legion SSID collisions and the ASUS TX300/ROG Strix G17 conflict. Adding a broad `SND_PCI_QUIRK()` before a needed `HDA_CODEC_QUIRK()` or exact entry can select the wrong fixup and break speakers, microphones, or amplifiers on unrelated hardware.

Fallback pin quirks are intentionally partial matches. The table comment warns that multiple partial matches can be possible, so duplicate fallback entries for the same vendor and codec can create ambiguous behavior. New fallback entries need stricter review than exact pin quirks.

Codec variant classification assumes specific Realtek vendor IDs and `coef0` bit meanings. A wrong variant can install the wrong init/shutup function, expose nonexistent loopback mixers, miss required coefficient writes, or disable `en_3kpull_low` incorrectly.

Probe dereferences `codec->bus->pci` in most places only after checking it, but the ALC236 `codec->bus->pci->vendor` test is not locally guarded in this branch. The surrounding HDA Realtek PCI context likely makes this valid, but it is a notable assumption if reused for non-PCI buses.

Coefficient writes are hardware-sensitive. The ALC269VB, ALC294, and ALC700 coefficient updates alter power, ramp, class-D, UAJ, and combo-jack behavior. Incorrect masks or revision checks can cause pops, missing output, unreliable jack detection, or resume-only failures.

Component amplifier detection and cleanup must stay paired. Probe may discover companion amps, while remove frees `spec->comps`; missing cleanup or double cleanup would affect systems with Cirrus or other smart amplifier components.

The device ID table lists many related codecs under the same driver. Adding an ID without a matching variant branch may leave the codec on default Realtek hooks and generic parsing, which can appear to work while missing required power or jack behavior.

## Test and Validation Signals

Useful validation starts with boot-time binding: `dmesg` should show the expected codec name, no probe errors, no component binding failures, and any intended rename such as `ALC271X` or `ALC3202` on matching systems.

Quirk validation should compare `/proc/asound/card*/codec#*`, PCI subsystem IDs, codec SSIDs, and generated ALSA controls against the intended table entry. Systems with shared SSIDs need explicit regression checks that the codec-SSID entry wins over the broader PCI entry.

Audio behavior tests should cover internal speakers, headphones, headset microphones, internal digital/analog mics, mute LEDs, mic-mute LEDs, docking audio, bass speakers, and smart amplifier playback on representative Samsung, Clevo/System76, Lenovo, Dell, HP, ASUS, Framework, and Intel NUC systems touched by these tables.

Power-management tests should cover cold boot, suspend/resume, runtime PM, jack insertion after resume, and shutdown/poweroff pop behavior, especially for variants that install non-default `shutup` or `init_hook` callbacks.

Pin-quirk tests should verify that exact pin configurations match only the intended machines and that fallback entries do not catch unrelated boards from the same vendor/codec pair. A useful negative signal is an unexpected `fixup_id` on a similar but unsupported machine.

Build validation should compile this driver with the HDA Realtek and component namespaces enabled, catching missing fixup enum references, stale model names, malformed quirk macros, or missing module imports.
