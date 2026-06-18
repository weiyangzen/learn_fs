# subset-b-006368 HDA HDMI, helper, and Realtek codec research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi.c

## Purpose

This is the generic ALSA HDA HDMI/DisplayPort codec implementation. It discovers digital audio converters and HDMI/DP pins, builds playback PCM devices, exposes ELD and channel-map controls, handles jack and DRM audio-component notifications, programs HDMI/DP audio infoframes, and manages converter/pin assignment across hotplug and suspend/resume.

## Important APIs, types, and functions

Exported entry points include `snd_hda_hdmi_generic_alloc`, `snd_hda_hdmi_parse_codec`, `snd_hda_hdmi_generic_probe`, `snd_hda_hdmi_generic_build_pcms`, `snd_hda_hdmi_generic_build_controls`, `snd_hda_hdmi_generic_init`, `snd_hda_hdmi_generic_suspend`, `snd_hda_hdmi_generic_resume`, `snd_hda_hdmi_generic_remove`, `snd_hda_hdmi_setup_stream`, `snd_hda_hdmi_setup_audio_infoframe`, `snd_hda_hdmi_generic_pcm_prepare`, `snd_hda_hdmi_generic_pcm_cleanup`, `snd_hda_hdmi_check_presence_and_report`, and the audio-component helpers. The core state is `struct hdmi_spec`, `struct hdmi_spec_per_pin`, `struct hdmi_spec_per_cvt`, and `struct hdmi_pcm` from `hdmi_local.h`.

## Control flow

Probe allocates `codec->spec`, registers channel-map ops, parses AFG child nodes by collecting converters before pins, initializes per-pin locks/work/proc entries, and later builds PCMs and controls. PCM open chooses a free converter, binds it to the pin mux, assigns SPDIF controls, and narrows capabilities from ELD unless `static_hdmi_pcm` is set. Prepare revalidates routing, syncs display audio rate for audio-component users, writes channel mapping and infoframes, enables dynamic pin output, and programs stream format. Hotplug uses unsolicited events or DRM callbacks to refresh ELD, attach or detach PCMs, update controls, and report jack state. Suspend cancels repoll work; resume reinitializes codec state and senses each pin.

## State and persistence behavior

State is per-codec and in-memory: dynamic arrays of pins/converters, `pcm_bitmap`, `pcm_in_use`, ELD buffers, channel maps, pin setup flags, converter assignment flags, delayed repoll work, and audio-component registration flags. Module parameters control static PCM capability policy, audio-component binding, and forced pin connectivity. No disk persistence exists except optional procfs ELD visibility.

## Dependencies and integration points

The file integrates ALSA HDA core, HDA jack tables, HDA controller stream data, HDMI ELD parsing, IEC958/SPDIF controls, `hdac_chmap`, PM runtime, PCI quirks, and DRM audio components through `snd_hdac_acomp_*`. Vendor modules override `hdmi_ops` for Intel, NVIDIA, and Tegra behavior.

## Risks and test signals

Risks include converter sharing races, stale ELD data, MST device-entry mismatches, incorrect infoframe size/checksum, HBR setup regressions, suspend/resume routing loss, silent-stream conflicts, and audio-component notifier lifetime errors. Test signals are HDMI/DP hotplug, DP MST displays, ELD control content, channel-map controls, non-PCM/HBR playback, S3/runtime PM resume, dynamic PCM attach/detach, and systems in the force-connect quirk list.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi_local.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi_local.h

## Purpose

This private header defines the shared HDMI codec data model and exported helper APIs used by generic HDMI, simple HDMI, Intel, NVIDIA, and Tegra codec drivers.

## Important APIs, types, and functions

`struct hdmi_spec_per_cvt` tracks converter NID, assignment, silent-stream ownership, and PCM capability limits. `struct hdmi_spec_per_pin` tracks virtual pin identity, MST device id, mux list, attached PCM, ELD, delayed work, channel-map override, setup state, and non-PCM status. `struct hdmi_ops` is the vendor override table for ELD reads, infoframe programming, HBR setup, stream setup, pin/converter fixups, and silent-stream control. `struct hdmi_spec` is the codec-wide state container. The header also defines HDMI and DP audio infoframe layouts, supported PCM capability macros, array access macros, and prototypes for generic/simple HDMI helpers.

## Control flow

The header has no runtime flow, but it defines the callback boundaries that `hdmi.c` calls during parse, open, prepare, hotplug, and component binding. Vendor modules populate selected `hdmi_ops` entries after `snd_hda_hdmi_generic_alloc`.

## State and persistence behavior

All state described here is runtime codec state attached to `codec->spec`. It persists for the lifetime of the bound HDA codec driver and is freed by generic or simple remove paths.

## Dependencies and integration points

It includes ALSA core, jack, HDA codec, HDA i915, and HDA channel-map headers, plus local HDA helpers. It is the ABI within the HDMI codec module namespace, with symbols exported under `SND_HDA_CODEC_HDMI`.

## Risks and test signals

Risks are layout and contract drift between generic and vendor files, especially around `pcm_rec[8]`, MST `dev_num`, `port_map`, and optional `CONFIG_SND_HDA_COMPONENT` behavior. Build coverage across all HDMI codec modules and runtime tests on generic, Intel, NVIDIA, and Tegra devices are the main signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/intelhdmi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/intelhdmi.c

## Purpose

This file specializes generic HDMI support for Intel display audio codecs. It requires i915 audio-component binding, maps HDA pins to display ports, enables Intel vendor features, fixes shared converter routing, and implements Intel silent-stream behavior.

## Important APIs, types, and functions

Key functions are `intelhdmi_probe`, `alloc_intel_hdmi`, `parse_intel_hdmi`, `intel_hsw_common_init`, platform probes for HSW/GLK/ICL/TGL/ADLP/BYT/CPT, `intel_pin2port`, `intel_port2pin`, `intel_pin_eld_notify`, `register_i915_notifier`, `i915_hsw_setup_stream`, `i915_pin_cvt_fixup`, `i915_hdmi_suspend`, `i915_hdmi_resume`, and `haswell_set_power_state`. Module parameter `enable_silent_stream` controls Kconfig-backed silent stream activation.

## Control flow

Probe first refuses binding without `codec->bus->core.audio_component`, preventing generic fallback. Platform-specific init sets `dp_mst`, vendor NID, port map, device count, power flags, and generic `hdmi_ops` overrides, then parses the codec and registers the i915 notifier. Hotplug arrives through i915 `pin_eld_notify`, which maps port/pipe to pin/device entry and calls generic presence reporting. HSW+ stream setup verifies D0, temporarily disables KAE around real stream programming if needed, and delegates to generic stream setup.

## State and persistence behavior

State is stored in `hdmi_spec`: vendor NID, port map, `intel_hsw_fixup`, `silent_stream_type`, and overridden ops. Suspend records whether KAE silent streams require preserved stream IDs and forced resume; resume restores stream format and DIG3 KAE if hardware lost them.

## Dependencies and integration points

The driver integrates with `sound/hda_i915.h`, DRM audio-component callbacks, Intel vendor verbs `0xf81/0x781`, HDA power management, and generic HDMI helpers. The HDA device table maps many Intel display codec IDs to platform models.

## Risks and test signals

Risks include i915 binding absence, deadlocks around silent streams, port-map errors on newer display generations, converter sharing after resume, vendor verb failures, and KAE power-reference leaks. Test with i915-bound HDMI/DP, DP MST, ADL-P KAE, GLK silent-stream-disabled path, runtime PM, S3 resume, and port-to-pin ELD notifications.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/intelhdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi-mcp.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi-mcp.c

## Purpose

This is the legacy NVIDIA MCP HDMI codec driver for older two-channel and multi-channel NVIDIA HDMI codecs that do not fit the fully generic HDMI parser.

## Important APIs, types, and functions

It uses `snd_hda_hdmi_simple_probe` with fixed master converter and pin NIDs, then overrides init, PCM, controls, and 8-channel stream programming. Important functions are `nvhdmi_mcp_probe`, `nvhdmi_mcp_init`, `nvhdmi_8ch_7x_pcm_prepare`, `nvhdmi_8ch_7x_pcm_close`, `nvhdmi_8ch_7x_set_info_frame_parameters`, `nvhdmi_mcp_build_pcms`, and `nvhdmi_mcp_build_controls`.

## Control flow

Probe builds simple HDMI state around NIDs `0x04` and `0x05`, overrides PCM capabilities because the codec does not report a complete list, and for 8-channel models replaces the playback stream with a custom stream. Prepare writes stream id and format to the master converter and four paired converter NIDs, temporarily toggling SPDIF enable when needed so IEC958 status updates stick. Close clears all stream ids and formats, then restores a valid 8-channel infoframe mask.

## State and persistence behavior

The driver uses `hdmi_spec.multiout`, `pcm_playback`, `hw_constraints_channels`, and `nv_dp_workaround`. Hardware state persists in vendor-specific infoframe channel allocation/checksum verbs and in converter stream programming until cleanup/close.

## Dependencies and integration points

It depends on simple HDMI helpers, HDA multi-out digital helpers, SPDIF state, channel-map controls, and NVIDIA vendor verbs for channel allocation, checksum, and audio protection. Device IDs distinguish two-channel and eight-channel legacy models.

## Risks and test signals

Risks include incorrect manual stream-id/channel-id mapping, broken IEC958 status propagation, invalid channel allocation checksum, and model-specific channel constraints. Test two-channel and 8-channel playback, 2/6/8 channel constraints by vendor ID, IEC958 non-audio status changes, channel-map control masks, close/reopen, and jack unsolicited reporting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi-mcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi.c

## Purpose

This file binds modern and transitional NVIDIA HDMI/DP codecs to the generic HDMI implementation, adding NVIDIA-specific channel-map validation, DisplayPort infoframe workaround behavior, audio-component integration, and model selection.

## Important APIs, types, and functions

Key functions are `nvhdmi_probe`, `probe_generic`, `probe_legacy`, `nvhdmi_chmap_cea_alloc_validate_get_type`, `nvhdmi_chmap_validate`, `nvhdmi_pin2port`, and `nvhdmi_port2pin`. `nvhdmi_audio_ops` wires generic audio-component bind/unbind and ELD notify callbacks.

## Control flow

Generic models allocate generic HDMI state, enable `dp_mst`, parse the codec, initialize pins, set dynamic pin output, install NVIDIA channel-map callbacks, enable the DP infoframe layout workaround, mark link-down-at-suspend, and initialize DRM audio-component binding. Legacy models use `snd_hda_hdmi_generic_probe` and the same NVIDIA post-configuration except audio-component setup.

## State and persistence behavior

Runtime state lives in `hdmi_spec`: `dyn_pin_out`, `nv_dp_workaround`, channel-map callbacks, `port2pin`, and audio-component registration for generic models. No persistent storage is used.

## Dependencies and integration points

It relies on `hdmi.c` generic exports, HDA channel-map APIs, DRM audio-component callbacks, and a large NVIDIA HDA device ID table. Pin-to-port mapping assumes contiguous pin NIDs beginning at 4.

## Risks and test signals

Risks include the contiguous pin mapping assumption, channel-map rejection for CA 0x00 stereo, DP infoframe compatibility, and generic-vs-legacy model classification. Test modern NVIDIA HDMI/DP hotplug, audio-component ELD callbacks, stereo and multi-channel channel-map controls, DP MST, suspend link-down behavior, and representative IDs from both model classes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/simplehdmi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/simplehdmi.c

## Purpose

This file provides a compact non-generic HDMI helper path for codecs with one fixed converter and one fixed pin, and registers VIA VX900 HDMI/DP codecs through that path.

## Important APIs, types, and functions

Exported helpers include `snd_hda_hdmi_simple_probe`, `snd_hda_hdmi_simple_build_pcms`, `snd_hda_hdmi_simple_build_controls`, `snd_hda_hdmi_simple_init`, `snd_hda_hdmi_simple_remove`, `snd_hda_hdmi_simple_pcm_open`, and `snd_hda_hdmi_simple_unsol_event`. Internal helpers build one jack and provide simple playback open/close/prepare callbacks.

## Control flow

Probe allocates `hdmi_spec`, initializes one pin and one converter array entry, sets `multiout.dig_out_nid`, and stores a default 2-channel playback template. Build PCMs creates one HDMI PCM and copies the playback template, adjusting maximum channels from converter capabilities. Build controls creates digital output controls and an AV jack. Init enables pin output, unmutes pin output amp if present, and enables jack detection. PCM open applies channel constraints and delegates to HDA multi-out digital open.

## State and persistence behavior

State is minimal and in-memory: one converter, one pin, one `multiout`, one PCM record, optional channel constraint list, and jack pointer. Remove frees arrays and `spec`.

## Dependencies and integration points

It depends on `hdmi_local.h`, HDA jack helpers, HDA multi-out digital helpers, and the HDA codec driver table. Legacy NVIDIA MCP reuses these helpers and overrides selected pieces.

## Risks and test signals

Risks include assuming exactly one converter/pin, missing ELD/control sophistication from the generic path, and channel capability mismatch on reused simple helpers. Test VIA VX900 probe/init, jack reporting, PCM open/prepare/close, SPDIF control creation, and simple helper reuse by `nvhdmi-mcp.c`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/simplehdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/tegrahdmi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/tegrahdmi.c

## Purpose

This file adapts generic HDMI support for NVIDIA Tegra SoC display audio codecs. Its main addition is notifying the Tegra HDMI driver of active HDA audio format through NVIDIA scratch-register vendor verbs.

## Important APIs, types, and functions

Key functions are `tegrahdmi_probe`, `tegra_hdmi_init`, `tegra_hdmi_build_pcms`, `tegra_hdmi_pcm_prepare`, `tegra_hdmi_pcm_cleanup`, and `tegra_hdmi_set_format`. It also reuses NVIDIA channel-map validation helpers and generic HDMI ops.

## Control flow

Probe allocates generic HDMI state. Tegra234-and-newer models enable DP MST, dynamic pin output, and host interrupt trigger control. Init parses converters and pins, enables digital converters, initializes per-pin state, sets depop delay, installs NVIDIA-style channel-map validation, and enables the DP infoframe workaround. PCM build calls generic PCM build and overrides playback prepare/cleanup so prepare programs generic stream/infoframe state then writes scratch format, while cleanup invalidates scratch format before generic cleanup.

## State and persistence behavior

State is in `hdmi_spec`, especially `hdmi_intr_trig_ctrl`, `dyn_pin_out`, `nv_dp_workaround`, and `dp_mst`. Hardware-visible state is persisted in scratch register bytes until updated: format bits, valid bit, and either toggled trigger bit or host interrupt verb.

## Dependencies and integration points

It depends on generic HDMI exports, NVIDIA vendor-defined scratch verbs, HDA converter control, and the external Tegra HDMI driver that consumes scratch-register/interrupt updates. Device IDs cover Tegra30 through Tegra264 and related SoCs.

## Risks and test signals

Risks include using the wrong NID for scratch access on MST vs non-MST hardware, missed interrupts when trigger semantics differ, stale valid bits after cleanup, duplicate channel-map assignment, and only overriding the first HDMI PCM. Test format changes, stream cleanup, Tegra234+ MST, old trigger-bit SoCs, DP/HDMI infoframes, and suspend/resume playback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/tegrahdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/hp_x360.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/hp_x360.c

## Purpose

This include-style Realtek helper applies HP x360 top-speaker routing and coefficient programming for ALC295 systems with top Bang & Olufsen speakers.

## Important APIs, types, and functions

The only function is `alc295_fixup_hp_top_speakers`. It contains a pin table for NID `0x17`, a large `coef_fw` sequence, calls `alc295_fixup_disable_dac3`, and uses `alc_process_coef_fw`.

## Control flow

On `HDA_FIXUP_ACT_PRE_PROBE`, it applies the top-speaker pin config and disables DAC3 through the existing ALC295 helper. On `HDA_FIXUP_ACT_INIT`, it writes the coefficient firmware sequence to configure speaker processing/routing.

## State and persistence behavior

The helper mutates codec pin configuration before parser setup and writes volatile vendor coefficient state during init. The settings persist only in codec hardware until reset or reinit.

## Dependencies and integration points

It is meant to be included by a Realtek codec source that provides `struct hda_codec`, fixup action constants, `WRITE_COEF`, `alc295_fixup_disable_dac3`, `snd_hda_apply_pincfgs`, and `alc_process_coef_fw`.

## Risks and test signals

Risks include coefficient sequence drift, wrong action ordering, and applying HP-specific routing to the wrong subsystem. Test on matching HP x360 models for top-speaker output, speaker/headphone switching, suspend/resume reinit, and absence of regressions on non-matching Realtek systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/hp_x360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/ideapad_hotkey_led.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/ideapad_hotkey_led.c

## Purpose

This include-style helper wires Lenovo Ideapad mute and mic-mute LEDs into generic HDA LED class device support when the platform ACPI driver is enabled.

## Important APIs, types, and functions

With `CONFIG_IDEAPAD_LAPTOP`, `is_ideapad` checks Lenovo subsystem vendor `0x17aa` and ACPI IDs `LHK2019` or `VPC2004`. `hda_fixup_ideapad_acpi` adds mute and micmute LED cdevs during `HDA_FIXUP_ACT_PRE_PROBE`. Without the config, the fixup is an empty stub.

## Control flow

The codec fixup table calls `hda_fixup_ideapad_acpi`. During pre-probe the helper validates platform identity, then registers both LED class devices through `snd_hda_gen_add_mute_led_cdev` and `snd_hda_gen_add_micmute_led_cdev`.

## State and persistence behavior

It adds runtime LED class device integration to the codec generic spec. No file or firmware persistence is used.

## Dependencies and integration points

It depends on ACPI device discovery, `CONFIG_IDEAPAD_LAPTOP`, Linux LED class support, and generic HDA LED helpers.

## Risks and test signals

Risks include false-positive Lenovo matching, missing LEDs when ACPI IDs change, and build coverage for both config branches. Test Ideapad mute/micmute hotkeys, LED state changes from mixer controls, and no-op behavior when `CONFIG_IDEAPAD_LAPTOP` is disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/ideapad_hotkey_led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/ideapad_s740.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/ideapad_s740.c

## Purpose

This include-style helper applies a large Realtek coefficient verb sequence for Lenovo Ideapad S740 ALC285 audio behavior.

## Important APIs, types, and functions

`alc285_ideapad_s740_coefs` is a long `struct hda_verb` table targeting NID `0x20` coefficient index and processing coefficient verbs. `alc285_fixup_ideapad_s740_coef` installs the verb table.

## Control flow

When called with `HDA_FIXUP_ACT_PRE_PROBE`, the helper adds the coefficient verbs to the codec init verb list via `snd_hda_add_verbs`. No other actions perform work.

## State and persistence behavior

The file stores no runtime state of its own. It appends an initialization sequence that programs codec vendor coefficients whenever the codec init verbs are executed.

## Dependencies and integration points

It depends on Realtek codec fixup infrastructure, HDA verb execution, and a parent codec file that includes this helper for the appropriate Ideapad S740 model quirk.

## Risks and test signals

Risks include opaque coefficient values, duplicated or order-sensitive coefficient writes, applying the table to the wrong ALC285 subsystem, and regressions after runtime reset/resume. Test internal speakers, headphone and mic behavior on Ideapad S740, suspend/resume, cold boot, and model-quirk selection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/ideapad_s740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/thinkpad.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/thinkpad.c

## Purpose

This include-style helper connects ThinkPad mute and mic-mute LEDs to generic HDA LED controls when ThinkPad ACPI support is available.

## Important APIs, types, and functions

With `CONFIG_THINKPAD_ACPI`, `is_thinkpad` checks Lenovo subsystem vendor `0x17aa` plus ACPI IDs `LEN0068`, `LEN0268`, or `IBM0068`. `hda_fixup_thinkpad_acpi` registers mute and micmute LED cdevs during pre-probe. Without the config, it compiles to a no-op.

## Control flow

The helper is invoked from a codec fixup. It only acts during `HDA_FIXUP_ACT_PRE_PROBE`, validates the platform, then adds LED devices to the generic HDA codec state.

## State and persistence behavior

It creates runtime LED class device integration and does not persist data. LED state follows generic HDA mixer/micmute state.

## Dependencies and integration points

It depends on ThinkPad ACPI, ACPI discovery, LED class APIs, and generic HDA LED helpers. It is included by Realtek codec sources rather than built as a standalone module.

## Risks and test signals

Risks include ACPI ID coverage gaps, false positives on Lenovo non-ThinkPad machines, and config-dependent build regressions. Test ThinkPad mute/micmute LEDs, hotkey interaction, mixer state sync, and no-op builds without `CONFIG_THINKPAD_ACPI`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/thinkpad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/Kconfig

## Purpose

This Kconfig file defines build-time configuration for the Realtek HDA codec family and its per-codec modules.

## Important APIs, types, and functions

`SND_HDA_CODEC_REALTEK` is the menuconfig gate. `SND_HDA_CODEC_REALTEK_LIB` selects shared dependencies `SND_HDA_GENERIC`, `SND_HDA_GENERIC_LEDS`, and `SND_HDA_SCODEC_COMPONENT`. Per-codec tristates cover ALC260, ALC262, ALC268, ALC269, ALC662, ALC680, ALC861, ALC861VD, ALC880, and ALC882.

## Control flow

When Realtek support is enabled, each codec option defaults to `y` and is only individually prompted under `EXPERT`. Most per-codec options depend on `INPUT` and select the shared Realtek library.

## State and persistence behavior

This file persists kernel build configuration only. It has no runtime state.

## Dependencies and integration points

It drives the `realtek/Makefile`, shared Realtek codec library availability, generic HDA parser support, LED integration, and smart-codec component support.

## Risks and test signals

Risks include missing dependency/select relationships, modules unexpectedly hidden without `EXPERT`, and per-codec defaults bloating or omitting builds. Test with built-in and module configurations, `EXPERT=n/y`, allmodconfig, allyesconfig, and minimal configs with Realtek disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/Makefile

## Purpose

This Makefile maps Realtek HDA codec Kconfig symbols to kernel objects and declares the source object composition for each Realtek codec module.

## Important APIs, types, and functions

It adds `-I$(src)/../../common`, defines `snd-hda-codec-realtek-lib-y := realtek.o`, maps each codec module name to its source object, and uses `obj-$(CONFIG_...)` to include the library and per-codec modules.

## Control flow

Kbuild expands the `obj-*` assignments according to `.config`, producing built-in or loadable Realtek codec objects. The shared library object is built when `CONFIG_SND_HDA_CODEC_REALTEK_LIB` is enabled.

## State and persistence behavior

No runtime state exists. The file controls build artifacts and module composition.

## Dependencies and integration points

It is paired with `Kconfig` and the individual `alc*.c` sources. The include path lets Realtek sources use shared common codec headers.

## Risks and test signals

Risks include mismatched Kconfig/object names, missing new codec sources, and include path regressions. Test all Realtek codec configs as built-in and modules, clean incremental builds, and namespace imports in each generated module.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc260.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc260.c

## Purpose

This is the Realtek ALC260 HDA codec driver. It allocates Realtek codec state, applies model and PCI fixups, parses BIOS auto configuration, configures beep handling, and registers standard generic HDA codec operations.

## Important APIs, types, and functions

Important functions are `alc260_probe`, `alc260_parse_auto_config`, `alc260_fixup_gpio1_toggle`, `alc260_gpio1_automute`, `alc260_fixup_kn1`, `alc260_fixup_fsc_s7020`, and `alc260_fixup_fsc_s7020_jwse`. Fixup tables cover HP dc5750/B1900, Acer, Sony VAIO, Fujitsu, Quanta KN1, Replacer, Packard Bell, and model strings such as `gpio1`, `coef`, and `fujitsu`.

## Control flow

Probe allocates `alc_spec` with mixer NID `0x07`, enables preferred HP amp and beep NID, sets EAPD shutup, performs Realtek pre-init, selects and applies pre-probe fixups, parses auto config while ignoring NID `0x17` and considering SSID pins, configures beep amp when analog is present, then applies probe-stage fixups. Errors remove generic state.

## State and persistence behavior

Runtime state lives in `alc_spec` and generic parser state: `prefer_hp_amp`, `beep_nid`, automute hooks, GPIO data, jack detection flags, pin configs, and init amp policy. Hardware pin/coefficient/GPIO state is re-established by init paths after reset.

## Dependencies and integration points

It depends on `realtek.h`, Realtek shared helpers, generic HDA parser/build/init operations, HDA jack callbacks, PCI/model fixup selection, and module namespace `SND_HDA_CODEC_REALTEK`.

## Risks and test signals

Risks include quirk misselection, GPIO1 automute polarity/state bugs, VAIO missing pin configs, beep amp setup failures, and incorrect ignored/SSID NIDs. Test listed quirks, headphone automute, speaker output, beep mixer, suspend/resume EAPD shutup, and generic auto-parser behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc262.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc262.c

## Purpose

This is the Realtek ALC262 codec driver, using the shared Realtek/generic parser with ALC262-specific PLL, fixups, beep handling, and quirk tables.

## Important APIs, types, and functions

Important functions are `alc262_probe` and `alc262_parse_auto_config`. Fixups cover Fujitsu H270/S7110, HP Z200, Tyan, Lenovo 3000, BenQ variants, inverted digital mic, and Intel BayleyBay no-depop-delay behavior.

## Control flow

Probe allocates `alc_spec` with mixer NID `0x0b`, sets shared mic VREF pin `0x18`, installs EAPD shutup, initializes PLL through `alc_fix_pll_init`, runs pre-init, picks and applies pre-probe fixups, parses customize defines, conditionally enables beep NID from codec defines, parses auto config while ignoring NID `0x1d`, configures beep amp if analog is available, and applies probe-stage fixups. Generic HDA ops handle controls, PCMs, init, PM, stream PM, and unsolicited jack events.

## State and persistence behavior

State is runtime `alc_spec` and generic parser state: shared mic VREF, beep NID, selected fixup, pin controls, coefficient verbs, depop policy, and auto config. Hardware coefficient and pin state is restored through codec init.

## Dependencies and integration points

It depends on Realtek shared helpers, model/PCI quirk selection, generic HDA parser operations, input/jack support from Kconfig, and the Realtek codec namespace.

## Risks and test signals

Risks include PLL setup regressions, shared mic VREF behavior, model fixup chaining, beep conditional handling, and BayleyBay depop behavior. Test listed systems, analog playback/capture, internal/external mic switching, beep controls, suspend/resume, and jack unsolicited events.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc262.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc268.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc268.c

## Purpose

This driver supports Realtek ALC267/ALC268 codecs. It uses generic Realtek auto parsing plus ALC268-specific beep mixer handling and a small fixup set for inverted DMIC, HP EAPD, and SPDIF.

## Important APIs, types, and functions

Important functions are `alc268_probe`, `alc268_parse_auto_config`, and `alc268_beep_switch_put`. `alc268_beep_mixer` defines beep volume and switch controls, and `alc268_beep_init_verbs` initializes beep routing by unmuting NID `0x1d` and muting inputs on NIDs `0x0f` and `0x10`.

## Control flow

Probe allocates an `alc_spec` without aa-loopback mixer, optionally sets beep NID from codec defines, installs EAPD shutup, runs pre-init, selects and applies pre-probe fixups, parses auto config, then if analog output exists and speaker pin is not `0x1d`, adds custom beep controls and init verbs. It overrides beep amp caps if the codec does not report them. Probe-stage fixups run last.

## State and persistence behavior

Runtime state includes generic Realtek parser state, added mixer controls, beep init verbs, selected fixup, and overridden amp caps. `alc268_beep_switch_put` temporarily rewrites control private value under `control_mutex` to apply switch changes to both NIDs.

## Dependencies and integration points

It depends on Realtek shared helpers, ALSA mixer control APIs, generic HDA parser/init/PM operations, PCI/model quirk selection, and module IDs for ALC267 and ALC268.

## Risks and test signals

Risks include the dual-NID beep switch leaving private value corrupted on errors, incorrect amp-cap override, unwanted beep controls when speaker pin uses `0x1d`, and quirk-specific EAPD/SPDIF behavior. Test beep volume/switch, analog speaker/headphone output, SPDIF quirk, Toshiba HP EAPD quirk, inverted DMIC quirk, and resume reinitialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc268.c -->
