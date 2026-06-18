# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp3x-es83xx/acp3x-es83xx.c

## Purpose
`acp3x-es83xx.c` provides board-specific machine operations for AMD ACP3x systems with ESS ES8336/ES8316-style codecs. It plugs into the generic ACP legacy machine flow through `acp_mach_ops`, adding DMI-gated probing, codec link setup, widgets/routes, jack handling, GPIO-controlled speaker/headphone power, microphone routing, and suspend/resume jack management.

## Important APIs, Types, and Functions
The exported initializer is `acp3x_es83xx_init_ops()`. The private state is `struct acp3x_es83xx_private`. Important functions include `acp3x_es83xx_probe()`, `acp3x_es83xx_configure_link()`, `acp3x_es83xx_configure_widgets()`, `acp3x_es83xx_init()`, `acp3x_es83xx_codec_startup()`, `acp3x_es83xx_configure_gpios()`, `acp3x_es83xx_configure_mics()`, power event callbacks, and suspend/resume callbacks.

## Control Flow
Generic machine probe calls `acp3x_es83xx_probe()` through `acp_ops_probe()`. The ES83xx probe only accepts DMI-listed systems, finds the ACPI codec device matching `acpi_mach->id`, obtains its physical device, allocates private state, and stores it in `acp_card_drvdata->mach_priv`. Link configuration installs the ES8336 codec component, init callback, ops, and I2S codec-master DAI format. Runtime init creates a headset jack, registers codec jack callback, installs ACPI GPIO mappings, acquires speaker/headphone enable GPIOs, and adds mic routes based on DMI quirk bits. Startup selects 12.288 MHz or 48 MHz codec sysclk and constrains channels to stereo.

## State and Persistence
Private state tracks quirk bits, codec device/component, GPIO descriptors, current speaker/headphone DAPM state, ACPI GPIO mapping, and mic routes. It is device-managed for the card lifetime, except the codec physical device reference is acquired and stored. Hardware GPIO output state follows DAPM events.

## Dependencies and Integration Points
It depends on ACPI, DMI, GPIO consumer APIs, ES8316/ES8336 codec naming, ASoC jack/DAPM APIs, and `acp-mach.h` callback dispatch. It is selected by ACPI match entry `ESSX8336` and legacy machine data that sets `hs_codec_id = ES83XX`.

## Risks
Systems with ES83xx in ACPI but missing from the DMI table are deliberately rejected. GPIO mapping assumes CRS entry indexes 0 and 1. Codec device reference handling is delicate; deferred probe and error paths must avoid leaks. Speaker/headphone power shares HP outputs, so DAPM route mistakes can mute or wrongly power outputs.

## Test Signals
Validate each DMI-listed Huawei system, 12.288 MHz versus 48 MHz MCLK, headset jack and play/pause button, internal DMIC versus analog mic routing, speaker/headphone GPIO transitions on DAPM events, suspend/resume jack reattachment, and rejection of unknown ES83xx systems.
