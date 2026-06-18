# sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_nau8824.c

## Purpose
This Cherrytrail/Braswell machine driver supports Nuvoton NAU88L24/NAU8824 codec boards. It defines the DPCM topology, codec clock/FLL setup, headset button mapping, and TDM-style SSP2 back-end constraints.

## Important APIs, Types, and Functions
`struct cht_mc_private` holds the headset jack. DAPM routes connect speakers, headphones, headset mic, internal mic, and SSP2 codec paths. `cht_aif1_hw_params()` selects NAU8824 FLL frame-sync clock and sets the codec PLL from the stream rate to `rate * 256`. `cht_codec_init()` creates a headset jack supporting headphone, mic, and four buttons; maps buttons to play/pause, voice command, volume up, and volume down; and calls `nau8824_enable_jack_detect()`. `cht_codec_fixup()` fixes BE rate/channels to 48 kHz stereo S24_LE and sets codec TDM slots.

## Control Flow and Integration
The card uses two dynamic FEs and one no-PCM SSP2 BE with `SND_SOC_DAIFMT_DSP_B | SND_SOC_DAIFMT_IB_NF | SND_SOC_DAIFMT_CBC_CFC`. Probe allocates private data, fixes platform names from ACPI machine data, applies SOF/legacy card naming, sets components from `nau8824_components()`, installs SOF PM ops when needed, and registers the card.

## State, Persistence, and Dependencies
State is limited to the headset jack and card component metadata. Hardware state includes NAU8824 FLL/sysclk, jack detection, and TDM slot configuration. Dependencies include NAU8824 codec helpers, Atom SST platform links, ACPI machine data, and SOF parent detection.

## Risks and Test Signals
Risks include fixed TDM parameters not matching board wiring, hard-coded codec ACPI name `i2c-10508824:00`, and missing cleanup if codec jack APIs change. Test signals include card registration, NAU8824 component string exposure, four-button headset events, 48 kHz-only FEs, working SSP2 DSP_B BE audio, and FLL setup errors only on real codec failures.
