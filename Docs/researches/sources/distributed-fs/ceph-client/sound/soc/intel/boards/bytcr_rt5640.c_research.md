# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_rt5640.c

## Purpose
This is the large Baytrail/Baytrail-CR RT5640 machine driver. It compensates for many tablet and mini-PC firmware variants by deriving routing, jack-detect, microphone, speaker, MCLK, and SSP/AIF behavior from DMI tables, ACPI CHAN packages, module-parameter overrides, and Android-tablet fallback device discovery.

## Important APIs, Types, and Functions
`struct byt_rt5640_private` stores headset jacks, RT5640 jack data, optional second-headset GPIO, MCLK, and codec-device reference. Quirk bits encode internal mic maps, jack detect source and over-current parameters, inverted detect, speaker modes, differential mic wiring, SSP0/SSP2 AIF choice, MCLK selection, lineout/headset2 behavior, AMCR0F28 usage, and swapped speakers. `byt_rt5640_prepare_and_enable_pll1()` chooses MCLK or BCLK as PLL input and sets codec sysclk. `platform_clock_control()` enables MCLK and PLL during DAPM use, then falls back to RT5640 RC clock for jack detect before disabling MCLK. `byt_rt5640_add_codec_device_props()` injects Realtek software-node properties before codec probe. `byt_rt5640_init()` adds quirk-specific DAPM routes, configures MCLK, creates jack devices, handles AMCR0F28 IRQ/GPIO overrides, and supports the HP ElitePad dual-jack special case.

## Control Flow and Integration
Probe finds and rewrites the codec name from ACPI, or falls back to `i2c-rt5640` for broken Android DSDTs. It detects BYTCR by `acpi_ipc_irq_index`, reads ACPI `CHAN` when possible, applies defaults, then overrides with DMI or module `quirk`. It optionally installs HP ElitePad GPIO mappings, injects codec properties, logs quirks, changes codec DAI name or CPU DAI to SSP0/AIF2 as needed, gets optional `pmc_plt_clk_3`, builds component and long-name strings, fixes platform names, sets SOF naming/PM ops, and registers the card. Remove tears down software nodes, GPIO mappings, and device references.

## State, Persistence, and Dependencies
State is significant: global `byt_rt5640_quirk`, global `is_bytcr`, mutable static DAI links, codec software-node properties, card components/long_name strings, MCLK state, jack state, and optional GPIO descriptors. Dependencies include RT5640 codec helpers, ACPI packages/GPIOs, DMI, I2C bus lookup, common clock framework, Atom SST/SOF platform links, `soc_intel_is_byt()`, and `sst-mfld-platform`.

## Risks and Test Signals
Risks include global quirk/link mutation across reprobe, complex error unwinding, silent invalid route combinations logged but not always fatal, mismatches between DMI quirks and actual wiring, fallback codec device lifetime handling, and jack-detect property timing before codec probe. Test signals include component strings (`cfg-spk`, `cfg-mic`, `aif`) matching expected UCM, correct DAPM routes for each DMI target, jack/headset button detection including AMCR0F28 and ElitePad paths, SSP0 16-bit or SSP2 24-bit operation as selected, MCLK fallback to BCLK when unavailable, and no leaked software nodes after remove or failed probe.
