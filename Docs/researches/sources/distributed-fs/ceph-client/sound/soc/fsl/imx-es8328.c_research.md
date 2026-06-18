# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-es8328.c

## Purpose
Board/machine driver for i.MX systems using an ES8328 codec over an SSI interface with AUDMUX routing and optional headset GPIO detection.

## APIs, Types, and Functions
`struct imx_es8328_data` stores the card, single DAI link, component name buffers, and optional jack GPIO. `imx_es8328_dai_init()` creates a headset jack and attaches GPIO detection. `imx_es8328_probe()` validates mux ports, configures AUDMUX, resolves SSI and codec phandles, builds the DAI link, parses card name/routing, and registers the card.

## Control Flow, State, and Persistence
Probe reads `mux-int-port` and `mux-ext-port`, validates 1..7 values, converts them to zero-based AUDMUX API indexes, programs internal and external ports, finds `ssi-controller` and `audio-codec`, and registers an I2S codec-provider link with CPU/platform on SSI and codec DAI `es8328-hifi-analog`. Jack state is stored in static `headset_jack` structures and the optional GPIO descriptor in card private data.

## Dependencies and Integration
Depends on `imx-audmux.h`, OF phandles, GPIO descriptors, ASoC jack/DAPM APIs, and the ES8328 codec driver. It integrates with device-tree `fsl,imx-audio-es8328`, `model`, and `audio-routing`.

## Risks and Test Signals
Risks include static jack objects shared across potential instances, hard-coded codec DAI name, AUDMUX configuration before confirming all phandles are present, and no runtime PM ops beyond component defaults. Test signals are probe on a valid DT, correct AUDMUX register programming, card routing with Headphone/Mic/Speaker/audio-amp widgets, jack GPIO events, and I2S playback/capture through ES8328.
