# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_cs42l42.c

Purpose: SOF machine driver for Intel platforms with a Cirrus CS42L42 headset codec and optional Maxim MAX98357A/MAX98360A speaker amplifier.

Important APIs, types, and functions: `sof_cs42l42_init()` creates headset jack pins, maps four buttons to input keys, and registers the jack with the codec component. `sof_cs42l42_exit()` clears jack state. `sof_cs42l42_hw_params()` derives BCLK via `sof_dai_get_bclk()` and programs codec sysclk. `sof_card_dai_links_create()` calls the common board helper, then patches the headset codec link with `cs42l42_component`, init/exit callbacks, and ops; it patches the amp link through Maxim helpers. The `GLK_LINK_ORDER` override handles Gemini Lake topology order.

Control flow and integration: Probe applies platform id quirks, gets a shared SOF context, reduces GLK DMIC links to one and overrides link order when necessary, sets iDisp codec presence, builds links, fixes platform names, binds drvdata, and registers the static card.

State and persistence: Uses static card and component arrays plus devm-managed `sof_card_private`. No persistent state.

Dependencies: SOF board helpers, CS42L42 codec component, Maxim common helpers, ASoC jack/input APIs, and ACPI mach params.

Risks: Platform id names include `cs4242` spellings while the codec is CS42L42, so matching depends on existing platform-device ids. Only two Maxim amp types are accepted. Test signals include jack/button events, sysclk setup from topology BCLK, GLK/JSL/ADL/RPL/MTL link order, optional HDMI controls, and speaker playback.
