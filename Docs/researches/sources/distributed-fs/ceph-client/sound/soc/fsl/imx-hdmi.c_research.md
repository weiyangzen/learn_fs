# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-hdmi.c

## Purpose
i.MX HDMI audio machine driver connecting SAI/eARC-style CPU DAIs to the generic HDMI codec. It configures DAI format, TDM slots, and CPU sysclk IDs for HDMI playback and capture-capable links.

## APIs, Types, and Functions
`struct cpu_priv` stores per-direction sysclk IDs and slot width; `struct imx_hdmi_data` stores the card, DAI link, CPU private data, and jack state. Main helpers include HDMI startup/hw_params/init routines, jack status callback wiring, and the platform probe that builds a single card from DT phandles.

## Control Flow, State, and Persistence
Probe allocates card data and link components, resolves CPU and HDMI codec endpoints, parses the card name, initializes HDMI DAPM/jack support, and registers the card. Runtime `hw_params()` derives slots/channels and slot width, programs the CPU DAI format and TDM slots, and sets CPU sysclk using direction-specific IDs. Link and jack state persist in devm card data.

## Dependencies and Integration
Depends on `sound/hdmi-codec.h`, ASoC jack and PCM parameter APIs, `fsl_sai.h`, OF platform helpers, and `snd_soc_pm_ops`. Integrates with the generic HDMI codec and i.MX SAI/HDMI audio DT bindings.

## Risks and Test Signals
Risks include DT-dependent clock ID selection, channel/slot assumptions for HDMI multichannel audio, jack callback behavior depending on the HDMI codec implementation, and possible mismatch between playback-only hardware and bidirectional link configuration. Test signals are card probe, ELD/jack state updates, HDMI sink detection, 2/8-channel playback, correct BCLK/LRCLK with configured slot width, and suspend/resume audio recovery.
