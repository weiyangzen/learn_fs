# subset-b-006513 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/Kconfig

## Purpose
This Kconfig file defines the configuration surface for Intel ASoC machine drivers under `sound/soc/intel/boards`. It gates legacy SST/Catpt, Baytrail/Cherrytrail/Braswell, Broadwell, SOF HDA/I2S, and SoundWire board drivers behind `SND_SOC_INTEL_MACH`, then selects codec, ACPI, GPIO, SoundWire, and helper dependencies needed by each board module.

## Important APIs, Types, and Symbols
The primary exported symbols are tristate machine options such as `SND_SOC_INTEL_BDW_RT5650_MACH`, `SND_SOC_INTEL_BDW_RT5677_MACH`, `SND_SOC_INTEL_BROADWELL_MACH`, `SND_SOC_INTEL_BYTCR_RT5640_MACH`, `SND_SOC_INTEL_BYTCR_RT5651_MACH`, `SND_SOC_INTEL_BYTCR_WM5102_MACH`, `SND_SOC_INTEL_CHT_BSW_RT5645_MACH`, `SND_SOC_INTEL_CHT_BSW_MAX98090_TI_MACH`, `SND_SOC_INTEL_CHT_BSW_NAU8824_MACH`, `SND_SOC_INTEL_BYT_CHT_CX2072X_MACH`, `SND_SOC_INTEL_BYT_CHT_DA7213_MACH`, `SND_SOC_INTEL_BYT_CHT_ES8316_MACH`, and `SND_SOC_INTEL_BYT_CHT_NOCODEC_MACH`. It also defines common helper symbols including `SND_SOC_INTEL_USER_FRIENDLY_LONG_NAMES`, `SND_SOC_INTEL_HDA_DSP_COMMON`, `SND_SOC_INTEL_SOF_*_COMMON`, and `SND_SOC_INTEL_SOF_BOARD_HELPERS`.

## Control Flow and Integration
Menu visibility starts at `menuconfig SND_SOC_INTEL_MACH`, which depends on either the SST or SOF Intel top-level families. Nested `if` blocks partition options by runtime family: Catpt/Haswell, Catpt or SOF Broadwell, Atom/SOF Baytrail, SOF Apollo Lake/Gemini Lake/HDA, and SoundWire. Each board symbol constrains hardware prerequisites with `depends on` and pulls codec drivers with `select`. The Makefile consumes these symbols to build matching machine modules.

## State, Persistence, and Dependencies
There is no runtime state. The persistent effect is kernel configuration state, which controls object inclusion, module availability, and transitive codec/helper selection. Dependencies are mostly compile/link dependencies (`I2C`, `ACPI`, `SPI_MASTER`, `GPIOLIB`, `MFD_*`, `SOUNDWIRE`, `SND_HDA_CODEC_HDMI`) plus codec selections such as `SND_SOC_RT5640`, `SND_SOC_RT5645`, `SND_SOC_RT5677`, `SND_SOC_ES8316`, `SND_SOC_NAU8824`, `SND_SOC_MAX98090`, and `SND_SOC_WM5102`.

## Risks and Test Signals
The main risk is dependency drift: missing `select` or `depends on` clauses can produce link failures, missing probe-time helpers, or unbuildable `COMPILE_TEST` configurations. Another risk is overly broad `select` usage increasing kernel footprint for distro configs. Test signals include `olddefconfig` visibility, `allyesconfig` and `allmodconfig` build coverage, `COMPILE_TEST` builds without target hardware, and verifying that every Kconfig symbol used in the Makefile has a matching config block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/Makefile

## Purpose
This Makefile maps Intel ASoC board Kconfig symbols to kernel module objects. It names the module-level objects, assigns each module its source object list, and wires common SOF helper modules into the build.

## Important APIs, Types, and Symbols
The file uses standard kbuild variables: `snd-soc-*-y := file.o` defines object composition for a module, and `obj-$(CONFIG_*) += module.o` includes that module when the Kconfig symbol is built in or as a module. Relevant entries in this subset include `snd-soc-sst-bdw-rt5650-mach-y := bdw-rt5650.o`, `snd-soc-sst-bdw-rt5677-mach-y := bdw-rt5677.o`, `snd-soc-bdw-rt286-y := bdw_rt286.o`, `snd-soc-sst-bytcr-rt5640-y := bytcr_rt5640.o`, `snd-soc-sst-bytcr-rt5651-y := bytcr_rt5651.o`, `snd-soc-sst-bytcr-wm5102-y := bytcr_wm5102.o`, and the Cherrytrail/Braswell and BYT/CHT codec module mappings.

## Control Flow and Integration
kbuild evaluates each `obj-$(CONFIG_...)` assignment after configuration. The module names must match module aliases and platform-driver expectations used by ACPI machine matching. Common helpers such as `snd-soc-intel-hda-dsp-common`, `snd-soc-intel-sof-maxim-common`, `snd-soc-intel-sof-realtek-common`, `snd-soc-intel-sof-cirrus-common`, `snd-soc-intel-sof-nuvoton-common`, `snd-soc-intel-sof-ti-common`, and `snd-soc-intel-sof-board-helpers` are built from their helper C files when selected by Kconfig.

## State, Persistence, and Dependencies
The Makefile has no runtime state. It persists build structure: a Kconfig symbol becomes either no object, a built-in object, or a loadable module. It depends on object filenames staying synchronized with source files and Kconfig symbols.

## Risks and Test Signals
Risks include stale object names after source renames, Kconfig symbols with no corresponding `obj-*` entry, and module names that diverge from packaging expectations. Test signals are full tree builds with the listed configs enabled, `make M=sound/soc/intel/boards`, `modinfo` for module aliases, and comparing this Makefile against Kconfig symbol definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5650.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5650.c

## Purpose
This is the Intel Broadwell machine driver for boards using the Realtek RT5650 codec. It describes the ASoC card, DAPM topology, DPCM FE/BE links, jack handling, and codec clock/TDM setup for the Broadwell DSP connected to the codec through SSP0.

## Important APIs, Types, and Functions
`struct bdw_rt5650_priv` stores private card data, mainly the codec component pointer. Static DAPM widgets/routes expose `Headphone`, `Speaker`, `Headset Mic`, and two DMIC pairs. `broadwell_ssp0_fixup()` forces the back end to 48 kHz, 2 to 4 channels, and S24_LE. `bdw_rt5650_hw_params()` programs RT5645 PLL/sysclk from MCLK. `bdw_rt5650_fe_startup()` constrains capture to stereo or quad. `bdw_rt5650_init()` enables RT5645 ASRC filters, sets four 24-bit TDM slots, creates headphone and mic jacks, and calls `rt5645_set_jack_detect()`.

## Control Flow and Integration
Probe receives `struct snd_soc_acpi_mach` platform data, patches DAI platform names with `snd_soc_fixup_dai_links_platform_name()`, selects SOF or legacy card names through `snd_soc_acpi_sof_parent()`, stores private data with `snd_soc_card_set_drvdata()`, and registers the card with `devm_snd_soc_register_card()`. The card has one dynamic FE (`System PCM`) and one no-PCM BE (`Codec`) connected to `haswell-pcm-audio`, `ssp0-port`, and `i2c-10EC5650:00`/`rt5645-aif1`.

## State, Persistence, and Dependencies
Runtime state is limited to private card data and static jack objects. Persistent hardware state includes codec PLL/sysclk, ASRC source selection, TDM slot configuration, and jack detect registration. Dependencies include ASoC core, DPCM, ACPI machine data, `haswell-pcm-audio`, RT5645 codec helpers, and Broadwell/SOF platform matching.

## Risks and Test Signals
Risks include hard-coded codec ACPI name, incorrect 24 MHz versus 24.576 MHz clock assumptions, global jack objects if multiple cards were ever instantiated, and failures when `mach->mach_params.platform` is missing. Test signals include successful card registration, visible DAPM pins, jack events, 48 kHz playback/capture through SSP0, four-channel capture constraints, and suspend/resume without codec clock or jack regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5677.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5677.c

## Purpose
This Broadwell machine driver supports RT5677 codec designs, including speaker/headphone routing, GPIO-based jack and headphone amplifier control, SSP0 audio, and a non-DPCM SPI wake-on-voice DSP capture path.

## Important APIs, Types, and Functions
`struct bdw_rt5677_priv` holds the headphone-enable GPIO and codec component. `bdw_rt5677_event_hp()` delays on headphone power-up and toggles the external headphone amplifier GPIO. `bdw_rt5677_init()` installs ACPI GPIO mappings, selects ASRC clocks with `rt5677_sel_asrc_clk_src()`, requests `headphone-enable`, creates headphone and mic jacks, attaches GPIO detection through `snd_soc_jack_add_gpios()`, and force-enables `MICBIAS1`. `bdw_rt5677_dsp_hw_params()` configures PLL/sysclk for the wake-on-voice link. Suspend/resume callbacks disable and re-enable `MICBIAS1`.

## Control Flow and Integration
The card defines a DPCM FE (`System PCM`), a capture-only `Codec DSP` link using `spi-RT5677AA:00` and `rt5677-dspbuffer`, and an SSP0 BE using `i2c-RT5677CE:00`/`rt5677-aif1`. `broadwell_ssp0_fixup()` forces 48 kHz stereo S16_LE. Probe mirrors the Broadwell pattern: fix platform names, choose SOF or legacy naming, set driver data, and register the card.

## State, Persistence, and Dependencies
State includes jack objects, GPIO descriptors, codec component pointer, and DAPM MICBIAS state. Persistent hardware effects are ACPI GPIO mappings, headphone amp GPIO state, codec ASRC/sysclk/PLL setup, and jack GPIO registration. Dependencies include RT5677 codec helpers, GPIOLIB/ACPI GPIO resources, SPI RT5677 DSP support, ASoC DPCM, and Broadwell platform audio.

## Risks and Test Signals
Risks include fragile GPIO index assumptions, leaking or double-freeing GPIOs if `.exit()` paths change, MICBIAS staying enabled across suspend transitions, and wake-on-voice SPI path dependency on a separate platform device. Test signals include both jack GPIOs reporting correctly, headphone amp toggling with DAPM, wake-on-voice capture device registration, SSP0 48 kHz stereo operation, and clean suspend/resume with MICBIAS restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5677.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw_rt286.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw_rt286.c

## Purpose
This is the Broadwell Wildcat Point machine driver for Realtek RT286. It defines a richer Broadwell DPCM card with system, offload, and loopback FEs plus one SSP0 codec BE.

## Important APIs, Types, and Functions
The driver defines static DAPM pins for speaker, headphone, headset mic, line jack, and two DMICs. `codec_link_init()` creates a headset jack supporting microphone, headphone, and button 0, then passes it to the RT286 component with `snd_soc_component_set_jack()`. `codec_link_exit()` clears jack detection. `codec_link_hw_params_fixup()` enforces 48 kHz stereo S16_LE on SSP0. `codec_link_hw_params()` sets codec sysclk to RT286 PLL at 24 MHz. Card suspend/resume callbacks detach and restore jack detection.

## Control Flow and Integration
DAI links include dynamic FE links for `System Pin`, `Offload0 Pin`, `Offload1 Pin`, and `Loopback Pin`, all using `haswell-pcm-audio`, plus a no-PCM BE from `ssp0-port` to `i2c-INT343A:00`/`rt286-aif1`. Probe fixes platform names from ACPI machine data, switches to SOF names when applicable, and registers the card.

## State, Persistence, and Dependencies
State is mostly static: the global `card_headset` jack and the card definition. Runtime persistent effects are codec jack registration and RT286 sysclk setup. Dependencies include ASoC DPCM, Broadwell/Haswell PCM platform support, RT286 codec support, and ACPI machine data.

## Risks and Test Signals
Risks include global jack state, hard-coded codec HID, and loss of offload/loopback routes if DAI names drift. The suspend callbacks tolerate missing codec DAI, but that also hides registration defects. Test signals include all four FE PCMs appearing, headset events through the codec, 48 kHz stereo BE constraints, offload playback working, loopback capture working, and suspend/resume maintaining jack reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw_rt286.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_cx2072x.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_cx2072x.c

## Purpose
This Baytrail/Cherrytrail DPCM machine driver supports Conexant CX2072X codecs on Atom SST or SOF platforms. It describes headset, internal mic, speaker, SSP2 routing, and codec clock setup.

## Important APIs, Types, and Functions
DAPM widgets/routes connect `Headphone`, `Headset Mic`, `Int Mic`, and `Ext Spk` to CX2072X ports and SSP2. `byt_cht_cx2072x_init()` installs ACPI GPIO mapping for headset detection, disables idle bias, sets codec sysclk to `CX2072X_MCLK_EXTERNAL_PLL` at 19.2 MHz, creates a headset jack with button 0, calls `snd_soc_component_set_jack()`, and sets a BCLK ratio of 50. `byt_cht_cx2072x_fixup()` enforces 48 kHz stereo S24_LE and programs the CPU DAI to I2S, bit/provider frame/provider mode, two slots, 24-bit.

## Control Flow and Integration
The card has two FEs indexed by `MERR_DPCM_AUDIO` and `MERR_DPCM_DEEP_BUFFER`, plus an SSP2 BE to `cx2072x-hifi`. Probe locates the ACPI codec device using `mach->id`, rewrites the codec component name to the actual `i2c-<ACPI name>`, fixes platform names, chooses SOF or legacy card identity, optionally assigns `snd_soc_pm_ops`, and registers the card.

## State, Persistence, and Dependencies
Static state includes the headset jack and `codec_name` buffer. Hardware state includes CX2072X sysclk, BCLK ratio, jack binding, and SSP2 CPU DAI format. Dependencies include `sst-mfld-platform`, Atom DPCM indices, ACPI HID discovery, GPIO mapping, and the CX2072X codec driver.

## Risks and Test Signals
Risks include assuming one codec DAI match, failing probe if ACPI lookup misses `mach->id`, and global mutable DAI/link state after codec-name rewrite. Test signals include probe deferral or success based on ACPI codec presence, FE and deep-buffer PCM creation, 48 kHz-only stream startup, headset button events, and correct SSP2 I2S signal shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_cx2072x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_da7213.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_da7213.c

## Purpose
This machine driver supports Baytrail/Cherrytrail boards with Dialog DA7212/DA7213 codecs. It provides the DPCM card layout, SSP2 I2S setup, DA7213 clock/PLL programming, and ACPI codec-name fixups.

## Important APIs, Types, and Functions
`codec_fixup()` forces 48 kHz stereo S24_LE and configures the CPU SSP2 port as two-slot 24-bit I2S. `aif1_startup()` limits FEs to 48 kHz. `aif1_hw_params()` sets DA7213 sysclk from 19.2 MHz MCLK and starts the codec PLL in SRM mode to `DA7213_PLL_FREQ_OUT_98304000`. `aif1_hw_free()` stops the PLL by switching to MCLK/zero configuration. DAPM controls expose headphone, headset mic, onboard mic, and aux input.

## Control Flow and Integration
The DAI layout is two dynamic FEs (`media-cpu-dai`, `deepbuffer-cpu-dai`) plus one no-PCM `SSP2-Codec` BE to `da7213-hifi`. Probe finds the ACPI codec instance from `mach->id`, rewrites the codec name, applies platform-name fixups, switches naming for SOF parent devices, sets SOF PM ops when needed, registers the card, and stores it as platform data.

## State, Persistence, and Dependencies
Static mutable state includes the codec name buffer and DAI link codec pointer. Runtime hardware state is the DA7213 sysclk/PLL state and SSP2 format. Dependencies include ACPI, `sst-mfld-platform`, Dialog DA7213 codec APIs, and Atom DPCM link indices.

## Risks and Test Signals
Risks include PLL start/stop imbalance if stream teardown paths change, hard failure when ACPI codec lookup fails, and global link mutation limiting multi-instance safety. Test signals include successful `devm_snd_soc_register_card()`, FE/deep-buffer playback at 48 kHz, DA7213 PLL programming messages only on real errors, audio capture/playback through SSP2, and clean PLL shutdown on stream free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_da7213.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_es8316.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_es8316.c

## Purpose
This Baytrail/Cherrytrail machine driver supports Everest ES8316 codec boards. It handles highly variable board wiring through DMI and ACPI DSM-derived quirks, selects SSP0 or SSP2 routing, controls an external speaker-enable GPIO, and exposes card component metadata for UCM.

## Important APIs, Types, and Functions
`struct byt_cht_es8316_private` owns the MCLK, headset jack, optional speaker GPIO, codec device reference, and cached speaker-enable state. Quirk flags select internal mic mapping, SSP0, mono speaker, and inverted jack detect. `byt_cht_es8316_init()` adds DAPM routes based on quirks, configures `pmc_plt_clk_3` to 19.2 MHz, sets codec sysclk, creates a headset jack, maps button 0 to `KEY_PLAYPAUSE`, and binds jack detection. `byt_cht_es8316_get_quirks_from_dsm()` reads ES83xx DSM mic, speaker, and HP detect settings. Suspend/resume detach and restore jack detection, and resume reasserts the speaker GPIO to work around buggy touchscreen ACPI methods.

## Control Flow and Integration
Probe rewrites the codec name from ACPI, gets a physical codec device reference, applies platform-name fixups, dumps DSM info, chooses quirks in order: DMI, DSM, BYTCR defaults, or generic defaults. It may add a software node property for inverted jack detect before the codec consumes properties. It maps the speaker GPIO on the codec device, builds `components` and possibly `long_name`, switches to SOF naming/PM ops, sets drvdata, and registers the card. Remove releases the GPIO, software node, and codec reference.

## State, Persistence, and Dependencies
Persistent state includes global `quirk`, mutable DAI CPU name for SSP0, codec software-node properties, card component strings, and hardware MCLK/GPIO/jack state. Dependencies include ES83xx DSM helper APIs, ACPI, DMI, GPIO, common clock framework, Atom SST platform, SOF parent detection, and `soc_intel_is_byt()`.

## Risks and Test Signals
Risks include stale global quirk/link mutation, missed `put_device()` or software-node cleanup on probe errors, DSM values that do not match expected enums, and nonexclusive GPIO sharing with touchscreen firmware. Test signals include component strings matching hardware, correct internal/headset mic routing, speaker GPIO transitions during DAPM and resume, jack detect inversion on affected DMI/DSM systems, and working SSP0 BYTCR and SSP2 non-BYTCR playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_es8316.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_nocodec.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_nocodec.c

## Purpose
This minimal Baytrail/Cherrytrail machine driver exposes SSP2 I2S signals on MinnowBoard Max/Up low-speed connectors without managing a real codec. It creates dummy codec routes and pins so raw I2S playback/capture can be used.

## Important APIs, Types, and Functions
DAPM widgets define a dummy `Mic` and `Speaker`; controls expose pin switches. `codec_fixup()` fixes the back end to 48 kHz stereo S24_LE and programs SSP2 as two-slot 24-bit I2S. `aif1_startup()` constrains FE rates through a `snd_pcm_hw_constraint_list` containing only 48000. The DAI links use dummy codecs for the FE links and the SSP2 BE.

## Control Flow and Integration
The card contains two dynamic FEs (`Audio Port`, `Deep-Buffer Audio Port`) and one no-PCM BE named `SSP2-LowSpeed Connector`, all with `ignore_suspend = 1`. Probe sets the card device, registers it with `devm_snd_soc_register_card()`, and stores the card in platform driver data.

## State, Persistence, and Dependencies
There is no codec state, no jack state, and no external GPIO or clock ownership. Persistent hardware state is limited to CPU DAI format and TDM-slot setup when streams are active. Dependencies are the ASoC core, Atom SST DPCM platform, and DAI names from `sst-atom-controls.h`.

## Risks and Test Signals
Risks are mostly misuse risks: no codec power management, no external amplifier control, and no board-specific electrical safety beyond SSP2 configuration. Test signals include card registration on supported boards, visible 48 kHz FE PCMs, correct SSP2 waveform on the connector, and no suspend blocking because links intentionally ignore suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_nocodec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_rt5640.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_rt5640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_rt5651.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_rt5651.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_wm5102.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_wm5102.c

## Purpose
This machine driver supports Baytrail/Cherrytrail boards with a Wolfson/Cirrus WM5102 codec. It handles FLL/sysclk setup, SSP0 versus SSP2 routing, speaker VDD GPIO control, jack detection, and board-specific input/output maps.

## Important APIs, Types, and Functions
`struct byt_wm5102_private` stores headset jack, MCLK, speaker-VDD GPIO, and selected MCLK frequency. Quirk fields select internal/headset mic input map, speaker output map, SSP2 use, and 19.2 MHz MCLK. `byt_wm5102_prepare_and_enable_pll1()` resets/configures WM5102 FLL1, sets component sysclk from FLL1, and sets DAI sysclk. `platform_clock_control()` enables MCLK/FLL on DAPM power-up and disables FLL/MCLK on power-down. `byt_wm5102_spkvdd_power_event()` toggles speaker supply GPIO. `byt_wm5102_init()` adds quirk-selected DAPM routes, sets MCLK rate, creates an Arizona jack with headset, lineout, and four button bits, and binds jack detection.

## Control Flow and Integration
Probe gets `pmc_plt_clk_3`, finds the SPI codec device by ACPI name or fallback `spi-wm5102`, requests `wlf,spkvdd-ena` from the codec device, applies Cherrytrail defaults when `soc_intel_is_cht()`, applies module quirk override, builds component strings, fixes platform names, optionally switches the BE CPU DAI to `ssp2-port`, selects SOF/legacy names and PM ops, registers the card, and releases the speaker GPIO on error/remove.

## State, Persistence, and Dependencies
State includes global `quirk`, mutable DAI CPU name, card component string, MCLK frequency, speaker GPIO, and jack binding. Dependencies include WM5102/Arizona codec APIs, SPI bus device discovery, ACPI machine data, GPIO lookup provided by the Arizona SPI MFD driver, common clock, Atom SST DPCM, and SOF parent detection.

## Risks and Test Signals
Risks include probe deferral when the SPI codec or GPIO lookup is not ready, global quirk mutation, keeping the DAI link name `SSP2-Codec` even for SSP0 because SOF topology expects it, and FLL/sysclk mistakes across sample-rate families. Test signals include speaker VDD transitions, headset/lineout jack events, 48 kHz FE constraints, SSP0 16-bit or SSP2 24-bit BE format, correct component string maps, and no GPIO leaks after failed registration or remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_wm5102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_max98090_ti.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_max98090_ti.c

## Purpose
This Cherrytrail/Braswell machine driver supports MAX98090 codec boards and optional TI TS3A227E headset detection. It manages platform MCLK behavior, headset GPIO fallback, TI jack notifier behavior, SSP2 DPCM routing, and Chromebook clock quirks.

## Important APIs, Types, and Functions
`struct cht_mc_private` stores MCLK, jack state, TS3A227E presence, and quirk flags. `platform_clock_control()` enables or disables MCLK for normal boards but does nothing for `QUIRK_PMC_PLT_CLK_0` boards. `cht_aif1_hw_params()` sets MAX98090 sysclk to 19.2 MHz. `cht_ti_jack_event()` force-enables or disables TS3A227E `SHDN` and `MICBIAS` pins on microphone events. `cht_codec_init()` either registers the TI notifier after aux-device jack creation or creates a GPIO-backed headset jack. `cht_max98090_headset_init()` creates a four-button jack and calls `ts3a227e_enable_jack_detect()`.

## Control Flow and Integration
Probe allocates private state, applies DMI quirks for Chromebook models using `pmc_plt_clk_0`, detects whether `104C227E` exists, disables aux-device registration and installs ACPI GPIO mappings when absent, fixes platform names, gets the selected MCLK, optionally enables clk0 permanently to avoid MAX98090 PLL unlocks, applies SOF naming/PM ops, and registers the card. Remove disables the always-on clk0 quirk clock.

## State, Persistence, and Dependencies
State includes MCLK enable state, jack object, aux-device presence, and quirk bit. Persistent hardware effects include MCLK rate/enable behavior, MAX98090 sysclk, TI jack-detect registration, and DAPM MICBIAS/SHDN pin state. Dependencies include MAX98090, TS3A227E, ACPI GPIO mapping, DMI, common clock, Atom SST DPCM links, and SOF parent detection.

## Risks and Test Signals
Risks include wrong clock choice for Chromebook variants, aux-device removal changing jack creation order, leaving `pmc_plt_clk_0` enabled on probe error paths, and GPIO-only jack detection being degraded but non-fatal. Test signals include MAX98090 sysclk programming, four-button TI headset events when present, fallback HP/mic GPIO events when TI absent, no PLL unlock messages on clk0 boards, and 48 kHz SSP2 playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_max98090_ti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_nau8824.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_nau8824.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5645.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5645.c

## Purpose
This Cherrytrail/Braswell machine driver supports RT5645 and RT5650 codec variants. It selects the correct card based on ACPI HID, handles SSP0/SSP2 and AIF1/AIF2 routing quirks, configures codec PLL/sysclk and ASRC, creates headset jack detection, and exposes codec-specific component metadata.

## Important APIs, Types, and Functions
`struct cht_acpi_card` maps codec HIDs to codec type and card definition. `struct cht_mc_private` stores the headset jack, selected ACPI card, and MCLK. Quirk bits select SSP2 AIF2, SSP0 AIF1, SSP0 AIF2, and `pmc_plt_clk_0`. `platform_clock_control()` enables MCLK for active paths and switches the codec to RC clock before disabling MCLK. `cht_aif1_hw_params()` programs RT5645 PLL from 19.2 MHz MCLK. `cht_codec_init()` selects ASRC clock source, adds DAPM routes for selected SSP/AIF, creates the headset jack, calls `rt5645_set_jack_detect()`, and sets MCLK rate. `cht_codec_fixup()` configures 48 kHz stereo and chooses SSP0 16-bit I2S or SSP2 24-bit DSP/TDM behavior.

## Control Flow and Integration
Probe finds a supported Realtek ACPI HID, chooses RT5645 or RT5650 card, rewrites the codec component name, gets the physical codec device, fills component metadata from `rt5645_components()`, detects BYTCR and reads ACPI CHAN routing, applies DMI quirks, mutates codec/CPU DAI names for AIF2 or SSP0, fixes platform names, gets `pmc_plt_clk_0` or `_3`, sets SOF or legacy names, installs SOF PM ops when needed, and registers the chosen card.

## State, Persistence, and Dependencies
State includes global `cht_rt5645_quirk`, shared mutable `cht_dailink`, two static card objects, card component strings from codec properties, MCLK, and jack state. Dependencies include RT5645 codec helpers, ACPI HID/package lookup, DMI, common clock, Atom SST DPCM, `soc_intel_is_byt()`, and SOF parent detection.

## Risks and Test Signals
Risks include shared DAI link mutation across variants, missed edge cases in ACPI HID matching, quirk combinations selecting impossible SSP/AIF routes, and MCLK clock-source handling on Strago-family systems. Test signals include correct card name for RT5645 versus RT5650, component metadata from codec device, jack detection and buttons on RT5650 paths, SSP0 16-bit or SSP2 24-bit stream format, ASRC source selection matching AIF route, and stable audio across suspend/resume and runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5645.c -->
