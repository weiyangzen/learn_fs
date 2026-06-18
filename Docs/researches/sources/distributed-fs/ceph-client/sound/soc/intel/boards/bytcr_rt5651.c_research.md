# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_rt5651.c

## Purpose
This Baytrail/Baytrail-CR RT5651 machine driver is derived from the RT5640 driver and handles Realtek RT5651 board routing variations. It covers internal mic mapping, jack-detect properties, external amplifier GPIOs, SSP/AIF selection, MCLK handling, and UCM component metadata.

## Important APIs, Types, and Functions
`struct byt_rt5651_private` owns MCLK, external amp GPIO, optional HP-detect GPIO, headset jack, and codec-device reference. Quirk bits encode mic map, jack detect source, over-current settings, DMIC enable, MCLK frequency, SSP/AIF route, headphone LR swap, mono speaker, and non-inverted jack detect. `byt_rt5651_prepare_and_enable_pll1()` sets RT5651 PLL/sysclk from MCLK or BCLK. `platform_clock_control()` turns MCLK/PLL on for DAPM and returns to RC clock on power-down. `rt5651_ext_amp_power_event()` toggles the external amp supply. `byt_rt5651_add_codec_device_props()` injects Realtek codec properties. `byt_rt5651_init()` adds mic and SSP/AIF routes, card controls, MCLK rate setup, headset jack creation, and codec jack binding.

## Control Flow and Integration
Probe discovers the ACPI codec, rewrites codec names, gets the physical codec device, detects BYTCR and optional ACPI CHAN routing, applies DMI callback quirks and module override, adds codec software-node properties, obtains board-specific or Cherrytrail external amp/HP GPIOs, logs quirks, mutates DAI names for AIF2 or SSP0, gets optional `pmc_plt_clk_3`, builds component and long-name strings, fixes platform names, applies SOF card naming/PM ops, registers the card, and stores platform data. Remove removes the software node and releases the codec device reference.

## State, Persistence, and Dependencies
State includes global quirk and GPIO mapping pointers, mutable DAI definitions, card component strings, codec software-node properties, MCLK/GPIO descriptors, and headset jack state. Dependencies include RT5651 codec APIs, ACPI CHAN parsing, DMI matching, common clock, GPIO descriptor APIs, Atom SST DPCM IDs, and SOF parent detection.

## Risks and Test Signals
Risks include global mutable quirk state, external amp GPIO lookup depending on ACPI resource ordering, runtime behavior differences when MCLK is unavailable, and DMI callbacks that change global GPIO mapping for specific devices. Test signals include correct `cfg-spk`/`cfg-mic`/`cfg-hp` components, jack detection through codec or HP GPIO, external amp DAPM toggles, SSP0 or SSP2 format selection, 48 kHz-only FE startup, and clean software-node cleanup on driver removal.
