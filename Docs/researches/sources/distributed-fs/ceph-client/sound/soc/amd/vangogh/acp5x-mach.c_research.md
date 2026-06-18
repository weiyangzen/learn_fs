# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-mach.c

## Purpose
This Vangogh machine driver registers Valve-platform sound cards using NAU8821 headset codec with either CS35L41 or MAX98388 stereo speaker amplifiers. It defines DAI links, DAPM widgets/routes, headset jack detection, codec clock setup, constraints, and DMI-based card selection.

## Important APIs, Types, And Functions
Key functions are `platform_clock_control()`, `acp5x_8821_init()`, `acp5x_8821_startup()`, `acp5x_nau8821_hw_params()`, `acp5x_cs35l41_startup()`, `acp5x_cs35l41_hw_params()`, `acp5x_max98388_startup()`, and platform probe `acp5x_probe()`. It defines two cards: `acp5x_8821_35l41_card` and `acp5x_8821_98388_card`.

## Control Flow
Probe looks up DMI entries: Valve Jupiter selects the NAU8821+CS35L41 card, and Valve Galileo selects the NAU8821+MAX98388 card. It allocates `struct acp5x_platform_info`, attaches the selected static card to the platform device, and registers it. NAU8821 startup selects SP I2S for playback/capture and constrains streams to 48 kHz, two channels, and 32-bit samples. Speaker amplifier startup selects HS I2S for playback and constrains to 48 kHz stereo. Codec `hw_params` programs NAU8821 FLL from BCLK or sets CS35L41 SYSCLK for 48 kHz.

## State And Persistence Behavior
Persistent state includes static DAI-link/card descriptions, static headset jack `vg_headset`, and per-device `acp5x_platform_info` stored as card driver data. DAPM supply `Platform Clock` switches NAU8821 clocking between internal clock off-state and FLL/BCLK active-state. Jack detection is enabled through `nau8821_enable_jack_detect()`.

## Dependencies And Integration Points
It depends on codec drivers for NAU8821, CS35L41, and MAX98388; ACPI/I2C/SPI component names such as `i2c-NVTN2020:00`, `spi-VLV1776:00/01`, and `i2c-ADS8388:00/01`; CPU DAIs `acp5x_i2s_playcap.0/1`; and platform component `acp5x_i2s_dma.0`. It uses `acp5x.h` for instance identifiers.

## Risks And Edge Cases
Only two DMI products are supported; other Vangogh boards return `-ENODEV`. Static card objects are mutated with `card->dev`, so multiple instances are not expected. Codec component names are firmware-enumeration sensitive. MAX98388 path lacks a custom `hw_params` clock setup unlike CS35L41, relying on codec defaults or other configuration. Constraint lists force 48 kHz stereo, which may reject otherwise hardware-supported rates.

## Test Signals
On Valve Jupiter and Galileo, verify the expected card name, two DAI links, headset jack events, button media key mapping, speaker playback, headset playback/capture, DAPM clock transitions, and codec sysclk/FLL programming. DMI-negative systems should not register a card.
