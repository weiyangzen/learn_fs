# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_es8336.c

Purpose: SOF machine driver for Intel platforms using Everest ESSX8336/ES8316/ES8326 style codecs, optional DMICs, HDMI playback, HDMI capture SSPs, and board-specific speaker/headphone GPIO quirks.

Important APIs, types, and functions: Quirk macros encode codec SSP, speaker GPIO selection, DMIC, inverted jack detect, headphone GPIO, headset mic port, and HDMI capture SSPs. `struct sof_es8336_private` stores codec device, speaker/headphone GPIOs, jack, HDMI list, speaker state, and delayed pop-suppression work. `sof_es8316_init()` configures mic routing, creates the headset jack, and registers the codec jack. `sof_es8316_speaker_power_event()` and `pcm_pop_work_events()` coordinate delayed GPIO toggling for speaker/headphone mux behavior. `sof_8336_trigger()` mitigates pop noise on playback stop. `sof_card_dai_links_create()` dynamically builds codec, DMIC, HDMI playback, and optional HDMI capture links.

Control flow and integration: Probe combines platform driver_data, DMI quirks, NHLT-derived SSP info, DMIC counts, and module `quirk` override. It resolves the ACPI codec device, fixes component and DAI names, adds a software node for inverted jack detect, maps ACPI GPIOs according to quirk bits, initializes work/list state, sets component strings, and registers the card. Remove cancels work, releases GPIOs, removes the software node, and drops the codec device reference.

State and persistence: Mutable module-global `quirk`, static card/link fields, devm private data, manually acquired GPIO/device references, and a delayed work item. No disk persistence.

Dependencies: ASoC, HDA DSP HDMI helper, ACPI/DMI, GPIO consumer and ACPI GPIO mapping, software nodes, input jack APIs, and topology platform naming.

Risks: The module quirk override can produce topology-incompatible SSP/DMIC selections. Manual `gpiod_get_optional()` resources require remove/error cleanup. Late HDMI probe assumes HDMI list exists. Test signals include DMI/module quirk logs, GPIO polarity/mux behavior, pop-noise regression, jack detect including inverted property, DMIC/HDMI/HDMI-in link counts, ES8326 DAI-name fixup, and remove cleanup.
