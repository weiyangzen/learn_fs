# Research Report: subset-b-006414

This grouped report covers the AMD ACP ASoC PCI, PCM, PDM, machine-driver, ACPI-match, SoundWire, and board-specific source files assigned to work item `subset-b-006414`. Each file section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach-common.c

## Purpose
`acp-mach-common.c` is the shared machine-driver construction layer for AMD ACP legacy and SOF cards. It translates `struct acp_card_drvdata` endpoint and codec selections into ASoC DAI links, widgets, controls, routes, jack setup, clocking, and codec-specific `hw_params` handling for RT5682/RT5682S, RT1019, MAX98360A, MAX98388, NAU8825, NAU8821, DMIC, and ES83xx-extension cards.

## Important APIs, Types, and Functions
The exported entry points are `acp_sofdsp_dai_links_create()` and `acp_legacy_dai_links_create()`, plus exported DMI quirk table `acp_quirk_table`. Important local callbacks include codec init functions such as `acp_card_rt5682_init()`, `acp_card_rt5682s_init()`, `acp_card_rt1019_init()`, `acp_card_maxim_init()`, `acp_card_max98388_init()`, `acp_card_nau8825_init()`, and `acp_8821_init()`, and runtime ops such as `acp_card_rt5682_hw_params()`, `acp_card_rt5682s_hw_params()`, `acp_card_rt1019_hw_params()`, `acp_card_maxim_hw_params()`, `acp_max98388_hw_params()`, `acp_nau8825_hw_params()`, and `acp_nau8821_hw_params()`. `acp_rtk_set_bias_level()` manages Realtek bit-clock enable ordering.

## Control Flow
Machine probe code in companion files fills `acp_card_drvdata`, then calls one of the two DAI-link creation functions. Both count enabled endpoints, allocate `snd_soc_dai_link` arrays with devm allocation, and then append headset, amplifier, Bluetooth, and DMIC links based on CPU endpoint IDs. The SOF path uses `acp-sof-*` CPU DAIs and the PCI SOF component, while the legacy path uses ACP I2S/PDM CPU DAIs and SoC-revision-specific platform component names. Per-link codec IDs select the codec component array, init callback, ops table, playback/capture flags, and codec-conf name prefixes.

Runtime control flows through ASoC callbacks. Startup constrains channels/rates and sets codec DAI formats. `hw_params` programs PLLs, sysclks, BCLK ratios, TDM slots, and optional ACP-supplied word/bit clocks. DMI quirks can enable TDM mode or remap SOF BT/DMIC backend IDs. Jack init creates ALSA jack pins and button mappings and registers codec jack callbacks. DAPM routes and card controls are added during codec init.

## State and Persistence
State is volatile kernel/device-managed memory attached to the `snd_soc_card` and `acp_card_drvdata`. Clock handles, `tdm_mode`, `soc_mclk`, codec IDs, and codec-conf pointers persist for the card lifetime. Static jack objects are module-global. No disk persistence exists; DMI and ACPI matching drive runtime topology.

## Dependencies and Integration Points
The file depends on ASoC card, DAI, DAPM, jack, and codec APIs; Realtek/Nuvoton/Maxim codec headers; `acp-mach.h`; DMI matching; and ACP platform component names created by PCI/SoC drivers. It integrates with `acp-sof-mach.c`, legacy machine drivers, ES83xx ops, SOF topology BE IDs, and ACP platform DMA/I2S/PDM drivers.

## Risks
DAI-link selection is table-like but hand-coded; new boards can silently get dummy codecs, wrong platform components, or wrong BE IDs if `acp_card_drvdata` is inconsistent. Clock enable/disable is split across startup, `hw_params`, shutdown, and bias transitions, so imbalance can cause audio pops or leaks. TDM slot masks are codec-specific and fragile. Static jack objects limit assumptions about multiple simultaneous cards.

## Test Signals
Useful signals are successful card registration for each board ID, visible ALSA links/widgets/routes, jack button reporting, 48 kHz constraints, TDM-mode playback/capture on Google Skyrim-like systems, BT/DMIC remap on Steam Deck OLED, and suspend/resume with Realtek clock bias transitions. Runtime tests should exercise headset, speaker, DMIC, Bluetooth, and no-codec/dummy-codec link combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach.h

## Purpose
`acp-mach.h` declares the common machine-driver contract used by AMD ACP legacy, SOF, ES83xx, and shared machine files. It centralizes endpoint IDs, codec IDs, quirk bits, per-card driver data, optional machine callbacks, and the exported DAI-link creation APIs.

## Important APIs, Types, and Functions
Key definitions are `enum be_id`, `enum cpu_endpoints`, `enum codec_endpoints`, `struct acp_mach_ops`, and `struct acp_card_drvdata`. The header declares `acp_sofdsp_dai_links_create()`, `acp_legacy_dai_links_create()`, and `acp_quirk_table`. Inline helpers `acp_ops_probe()`, `acp_ops_configure_link()`, `acp_ops_configure_widgets()`, `acp_ops_suspend_pre()`, and `acp_ops_resume_post()` dispatch optional board-specific callbacks.

## Control Flow
Machine drivers store an `acp_card_drvdata` pointer in `card->drvdata`. Shared creation code reads endpoint and codec IDs to generate DAI links. Specialized drivers, especially ES83xx, install callbacks in `acp_mach_ops`; the inline wrappers call those callbacks only if present and otherwise return a nonzero default value.

## State and Persistence
The header owns no runtime state. It defines the card-lifetime state held in `acp_card_drvdata`: CPU and codec endpoint IDs, DAI format, ACP revision, clock handles, ACPI machine pointer, private machine data, and flags for SoC MCLK and TDM mode.

## Dependencies and Integration Points
It includes ALSA core, jack, PCM params, DAPM, input, module, ASoC, and `acp_common.h`. It is included by SOF/legacy machine drivers, ACP platform files, and ES83xx support. The enum values must match the assumptions in `acp-mach-common.c` and board data tables.

## Risks
The default inline return value is `1`, not `0`, so callers must treat a missing optional callback carefully. Endpoint and codec enum changes are ABI-like within this driver family; mismatches can produce wrong DAI links. `acp_get_drvdata()` assumes `card->drvdata` has the expected type.

## Test Signals
Build coverage should catch missing prototypes and enum users. Runtime smoke tests should verify that board IDs using each endpoint/codec combination still produce the expected DAI links and that optional ES83xx ops are invoked only for ES83xx cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-mach.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pci.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pci.c

## Purpose
`acp-pci.c` is the generic PCI front end for legacy AMD ACP audio. It binds the AMD ACP PCI function, selects revision-specific resources and machines, maps ACP registers, initializes hardware, requests IRQs, creates child platform devices, and wires runtime/system PM.

## Important APIs, Types, and Functions
The main functions are `acp_pci_probe()`, `acp_pci_remove()`, `snd_acp_suspend()`, `snd_acp_resume()`, `create_acp_platform_devs()`, `acp_fill_platform_dev_info()`, and the wrapper `irq_handler()`. It consumes `struct acp_chip_info`, `struct acp_resource`, `snd_soc_acpi_mach` tables, and revision-specific `*_hw_ops_init()` functions.

## Control Flow
Probe first calls `snd_amd_acp_find_config()` and accepts only legacy or legacy-DMIC modes. It enables the PCI device, requests regions, sets bus mastering, chooses revision-specific names/resources/hardware ops/ACPI machine tables, maps BAR0, initializes ACP hardware, requests the shared IRQ, and calls `check_acp_config()` to detect I2S/PDM configuration. If an I2S or PDM controller is usable, it registers the revision-named ACP platform device and optional `dmic-codec`, saves platform device references, selects the machine device, initializes stream list/lock, and enables autosuspend.

## State and Persistence
`struct acp_chip_info` is devm-allocated and stored as PCI drvdata. It holds register base, revision, machine table, child platform devices, stream list, resource pointer, flags, and configuration booleans. Child devices persist until PCI remove. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on PCI, platform-device, IRQ, PM runtime, ACP common hardware ops, `mach-config.h`, revision resources, and ACPI machine tables. It creates the platform devices that `acp-renoir.c`, `acp-rembrandt.c`, `acp63.c`, `acp70.c`, `acp-platform.c`, `acp-pdm.c`, and machine drivers bind to.

## Risks
Probe has many staged resources; incorrect unwind can leave hardware enabled or child devices registered. `chip->acp_hw_ops_init(chip)` is not checked for failure. Platform device creation can proceed with `chip->res` only when configuration says I2S/PDM exists. Suspend/resume assumes `dev_get_drvdata()` is valid and re-enables interrupts after `acp_hw_init()`.

## Test Signals
Test signals include correct probe by PCI revision `0x01`, `0x6f`, `0x63`, `0x70-0x72`, successful child platform creation, IRQ activity through revision IRQ handlers, runtime suspend/resume, no child devices on unsupported BIOS configs, and clean remove with no registered-device leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pdm.c

## Purpose
`acp-pdm.c` implements the ACP PDM/DMIC CPU DAI operations. It configures PDM clocks, channel count, ring buffer registers, interrupts, and start/stop control for digital microphone capture.

## Important APIs, Types, and Functions
The exported object is `acp_dmic_dai_ops` with `.prepare`, `.hw_params`, `.trigger`, `.startup`, and `.shutdown`. Important helpers are `acp_dmic_prepare()`, `acp_dmic_hwparams()`, `acp_dmic_dai_trigger()`, `acp_dmic_dai_startup()`, and `acp_dmic_dai_shutdown()`.

## Control Flow
Startup marks the runtime stream as DMIC, fills IRQ/PTE/register offsets, and enables the PDM DMA interrupt bit. `hw_params` validates channels as 2, 4, or 6, requires `S32_LE`, writes channel mask and decimation factor, and stores `chip->ch_mask`. Prepare enables default PDM clocking, calculates period and buffer sizes, picks the DMIC memory window based on ACP revision, writes ring buffer address/size/watermark, and enables ATU. Trigger start/resume/pause-release enables PDM and DMA and polls for the DMA enable bit; stop/suspend/pause-push disables both and polls for clear.

## State and Persistence
State lives in the PCM runtime private `struct acp_stream` and shared `struct acp_chip_info`. Register programming persists until stream shutdown, trigger stop, suspend, or hardware reset. No software state is persisted beyond runtime fields and `chip->ch_mask`.

## Dependencies and Integration Points
It depends on ACP register offsets from `amd.h`/`chip_offset_byte.h`, Linux `readl_poll_timeout_atomic()`, ASoC DAI callbacks, and the platform PCM open path that allocates `struct acp_stream`. It is referenced by revision DAI driver arrays in Renoir, Rembrandt, ACP63, and ACP70 platform drivers.

## Risks
Only `S32_LE` is accepted, so machine constraints must agree. Incorrect memory-window selection for ACP7x versus older revisions would break capture DMA. Polling is atomic and timeout-sensitive. Interrupt enable/disable must match stream lifetime or capture period notifications can be lost or noisy.

## Test Signals
Validate 2/4/6-channel DMIC capture, rejection of invalid formats/channels, DMA enable/disable timeout handling, period interrupts, suspend/resume restoration, and ACP70 memory-window capture. ALSA capture should show stable positions and no underrun-like stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-platform.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-platform.c

## Purpose
`acp-platform.c` is the common ACP PCM component/DMA platform layer. It exposes ALSA PCM hardware capabilities, allocates per-stream state, programs ACP page tables and DMA descriptors, reports stream pointers from ACP byte counters, and registers the SoC component/DAIs selected by revision drivers.

## Important APIs, Types, and Functions
Exports are `config_pte_for_stream()`, `config_acp_dma()`, `acp_platform_register()`, and `acp_platform_unregister()`. Component callbacks are `acp_dma_open()`, `acp_dma_close()`, `acp_dma_hw_params()`, `acp_dma_pointer()`, and `acp_dma_new()`. It defines legacy and ACP6x/7x `snd_pcm_hardware` capabilities.

## Control Flow
On PCM open, the driver allocates `struct acp_stream`, selects hardware limits by ACP revision, installs DMA-size alignment and integer-period constraints, stores the stream in runtime private data, enables external interrupts, and adds the stream to `chip->stream_list` under `acp_lock`. `hw_params` calls `config_pte_for_stream()` and `config_acp_dma()` to map DMA pages into ACP SRAM scratch/PTE registers. Pointer reads ACP byte counters and converts the modulo buffer position to frames. Close removes the stream from the list and frees it.

## State and Persistence
Per-stream state records substream, DAI ID, IRQ bit, direction, register/PTE/FIFO offsets, and last byte counter. `chip->stream_list` tracks live streams for IRQ handling and resume restoration. Hardware register state lasts until stream reconfiguration or ACP reset; all memory is volatile.

## Dependencies and Integration Points
The file depends on ASoC component registration, ALSA managed buffers, DMA buffer addresses, ACP register definitions, common byte-count helpers, and revision DAI arrays passed through `chip->dai_driver`. Resume paths in revision drivers iterate `stream_list` and reuse `config_pte_for_stream()`/`config_acp_dma()`.

## Risks
DMA page programming assumes the ALSA buffer is represented by contiguous DMA addresses page by page. ACP70/71/72 use hard-coded PTE windows by DAI/direction; wrong `stream->dai_id` or direction maps audio to the wrong memory window. `acp_dma_pointer()` uses `stream->bytescount` as a baseline and depends on correct byte-counter restoration. Open error paths must free `stream`.

## Test Signals
Exercise playback/capture open/close, period/buffer alignment constraints, mmap and managed buffers, pointer monotonicity/wraparound, ACP70 SP/BT/HS/DMIC streams, concurrent streams in `stream_list`, and resume restoring all active streams without distorted audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-rembrandt.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-rembrandt.c

## Purpose
`acp-rembrandt.c` is the ACP 6.x/Rembrandt platform driver. It defines Rembrandt I2S/PDM CPU DAIs, generates SoC master clock when needed, enables ACP interrupts, registers the common PCM component, and restores stream programming after system sleep.

## Important APIs, Types, and Functions
Key objects are `acp_rmb_dai[]` and platform driver `rembrandt_driver`. Important functions are `acp6x_master_clock_generate()`, `rembrandt_audio_probe()`, `rembrandt_audio_remove()`, and `rmb_pcm_resume()`.

## Control Flow
Probe validates platform data and ACP revision `ACP_RMB_PCI_ID`, assigns the Rembrandt DAI array to `chip`, optionally sends SMN messages to generate the SoC MCLK for I2S configs, enables ACP interrupts, registers the common ACP platform component, and enables runtime PM autosuspend. Resume regenerates MCLK when needed, walks `chip->stream_list`, reprograms PTE/DMA, and restores either I2S or PDM parameters for each active stream.

## State and Persistence
The file stores no private state outside `struct acp_chip_info`. Active streams persist in the common `stream_list`. SMN clock state and ACP DMA registers must be restored after sleep.

## Dependencies and Integration Points
It depends on AMD SMN access, ASoC platform registration, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, and common restoration helpers. It is instantiated by `acp-pci.c` as platform name `acp_asoc_rembrandt`.

## Risks
SMN register programming is hardware-specific and timeout-sensitive. Probe ignores the return value from `acp_platform_register()`. Resume holds `acp_lock` while calling register programming helpers, so helper behavior must remain non-sleeping. Missing MCLK generation can prevent codecs using SoC MCLK from working.

## Test Signals
Validate Rembrandt SP/BT/HS I2S and PDM DAI registration, SoC MCLK generation, runtime/system PM, suspend/resume playback/capture continuity, and clean removal with interrupts disabled and PM disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-rembrandt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-renoir.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-renoir.c

## Purpose
`acp-renoir.c` is the ACP 3.x/Renoir platform driver. It defines Renoir SP/BT I2S and PDM CPU DAIs, enables interrupts, registers the shared PCM component, and restores ACP stream register state after system resume.

## Important APIs, Types, and Functions
Important objects are `acp_renoir_dai[]` and platform driver `renoir_driver`. Main functions are `renoir_audio_probe()`, `renoir_audio_remove()`, and `rn_pcm_resume()`.

## Control Flow
Probe validates platform data and revision `ACP_RN_PCI_ID`, assigns the DAI driver array/count, enables ACP interrupts, registers the common platform component, and enables runtime PM. Remove disables interrupts and unregisters the platform component. Resume iterates active streams under `acp_lock`, reconfigures PTEs/DMA for the ALSA buffer, and restores I2S or PDM parameters depending on `stream->dai_id`.

## State and Persistence
State is held in shared `struct acp_chip_info` and stream objects allocated by `acp-platform.c`. Renoir-specific DAI definitions are static module data. Hardware register state is volatile across sleep and restored from stream/runtime parameters.

## Dependencies and Integration Points
It integrates with platform devices named `acp_asoc_renoir`, common ACP hardware ops, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, and machine drivers that reference Renoir platform component names.

## Risks
`acp_platform_register()` return is not checked, so later failures could leave probe appearing successful. Resume assumes active stream runtime data is valid. Renoir capture capabilities differ from later ACP revisions, so machine constraints must avoid unsupported channel/rate formats.

## Test Signals
Test Renoir SP/BT playback and capture, DMIC capture, interrupt delivery, suspend/resume during active streams, unsupported-revision rejection, and removal after active card registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-renoir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-legacy-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-legacy-mach.c

## Purpose
`acp-sdw-legacy-mach.c` is the generic non-SOF AMD SoundWire machine driver. It parses ACPI SoundWire endpoint descriptions, applies DMI/module quirks, creates backend DAI links for SoundWire devices and optional ACP DMIC, and registers the ASoC card named `amd-soundwire`.

## Important APIs, Types, and Functions
Main functions are `mc_probe()`, `mc_remove()`, `soc_card_dai_links_create()`, `create_sdw_dailinks()`, `create_sdw_dailink()`, `create_dmic_dailinks()`, `log_quirks()`, and `soc_sdw_quirk_cb()`. It uses `struct asoc_sdw_mc_private`, `struct amd_mc_ctx`, `struct asoc_sdw_dailink`, `struct asoc_sdw_endpoint`, and SoundWire utility callbacks in `sdw_ops`.

## Control Flow
Probe allocates AMD and generic SoundWire machine contexts, records ACP revision from `mach_params.subsystem_rev`, sets card metadata, copies PCI SSID when present, applies DMI quirks and optional `quirk=` override, resets codec amp counters, and calls `soc_card_dai_links_create()`. That function counts and parses SoundWire endpoints, determines whether an ACP DMIC link is required, allocates codec-conf/aux/dai-link arrays, creates one or more SoundWire links with CPU pin IDs derived from ACP revision and link/backend ID, then optionally creates a PDM DMIC link. Finally, probe builds a component string with amp and mic counts and registers the card.

## State and Persistence
Quirk state is module-global (`soc_sdw_quirk`) but can be overridden at load time. Card, context, DAI links, codec confs, and aux devices are devm-managed for the platform device. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on SoundWire ASoC utilities, codec information lists, ACPI mach tables, DMI, `get_acp63_cpu_pin_id()`/`get_acp70_cpu_pin_id()`, ACP PDM platform names, and `snd_soc_pm_ops`. It binds platform ID `amd_sdw` from ACP63/ACP70 ACPI match tables.

## Risks
The CPU pin mapping expression must identify the correct SoundWire link; wrong link/backend mapping yields unusable DAIs. The code assumes parsed endpoint counts and allocated config counts stay synchronized and warns if iterators do not land at expected ends. Global quirk state can affect multiple probes. Internal DMIC can be ignored by utility context, reducing available capture unexpectedly.

## Test Signals
Validate systems with RT722-only, RT711/RT1316/RT714, Cirrus, Realtek, and TAS combinations; DMI quirks for ACP DMIC and codec speaker; module quirk override; generated DAI link names such as `SDW0-PIN*-PLAYBACK`; jack/speaker/DMIC operation; and clean `asoc_sdw_mc_dailink_exit_loop()` on remove/register failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-legacy-mach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-mach-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-mach-common.c

## Purpose
`acp-sdw-mach-common.c` maps SoundWire backend DAI IDs and SoundWire link IDs to AMD ACP CPU pin IDs for both legacy and SOF SoundWire machine drivers.

## Important APIs, Types, and Functions
The exported helpers are `get_acp63_cpu_pin_id()` and `get_acp70_cpu_pin_id()`. They consume SoundWire utility backend IDs such as `SOC_SDW_JACK_OUT_DAI_ID`, `SOC_SDW_AMP_OUT_DAI_ID`, and `SOC_SDW_DMIC_DAI_ID`, plus ACP pin constants from `soc_amd_sdw_common.h`.

## Control Flow
For ACP63, link 0 has separate TX/RX pins for audio0, audio1, and audio2, while link 1 maps jack/amp output to `ACP63_SW1_AUDIO0_TX` and capture/DMIC to `ACP63_SW1_AUDIO0_RX`. For ACP70/71/72, both supported links use the same audio0/audio1/audio2 TX/RX pin numbering. Invalid link or backend IDs log errors and return `-EINVAL`.

## State and Persistence
The file has no mutable state. It is pure mapping logic with debug/error logging.

## Dependencies and Integration Points
Both `acp-sdw-legacy-mach.c` and `acp-sdw-sof-mach.c` call these helpers while creating SoundWire DAI links. The constants must match CPU DAI names exposed by the AMD SoundWire DMA controller.

## Risks
Incorrect mappings break stream routing without necessarily failing card registration. ACP63 link 1 has fewer pins than link 0, so adding endpoints without updating the mapping can fail or collapse streams onto the wrong pin.

## Test Signals
Exercise all jack, amp, and DMIC playback/capture DAI IDs on ACP63 and ACP70-class systems, including invalid ACPI table cases that should return `-EINVAL` with clear logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-mach-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-sof-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-sof-mach.c

## Purpose
`acp-sdw-sof-mach.c` is the SOF-backed AMD SoundWire machine driver. It builds SoundWire and optional DMIC backend links for `amd_sof_sdw` ACPI machine entries and registers an ASoC card that uses SOF platform components.

## Important APIs, Types, and Functions
Main functions mirror the legacy driver: `mc_probe()`, `mc_remove()`, `sof_card_dai_links_create()`, `create_sdw_dailinks()`, `create_sdw_dailink()`, `create_dmic_dailinks()`, `log_quirks()`, and `sof_sdw_quirk_cb()`. It uses `platform_component[]`, `sdw_ops`, `asoc_sdw_*` utility functions, `struct amd_mc_ctx`, and SoundWire codec info lists.

## Control Flow
Probe allocates contexts, stores ACP revision, initializes the card, applies DMI/module quirks, resets codec amp counters, then creates DAI links. Endpoint parsing determines SoundWire backend count and auxiliary devices. For each stream direction with devices, it maps ACP revision/link/backend to a CPU pin ID, builds a stream name, allocates CPU/codec/ch-map arrays, calls `asoc_sdw_init_dai_link()` with `no_pcm` set for SOF backend links, marks links nonatomic, and runs endpoint-specific init. Optional DMIC is created when a quirk or `mach_params->dmic_num` requests it, using CPU `acp-sof-dmic` and the SOF platform component.

## State and Persistence
Quirk state is module-global and load-time overrideable. Card and DAI-link state is devm-managed per platform device. SOF topology and firmware filenames are supplied by the ACPI match table, not persisted here.

## Dependencies and Integration Points
It depends on SOF platform component naming, SoundWire utility parsing/init helpers, ACP CPU pin mapping helpers, `snd_soc_pm_ops`, and ACPI match tables exporting `amd_sof_sdw` entries. It imports `SND_SOC_SDW_UTILS` and `SND_SOC_AMD_SDW_MACH`.

## Risks
The same SoundWire endpoint parsing/count synchronization risks apply as in the legacy driver. The static SOF platform component name may need overriding by platform data in broader SOF code; if mismatched, card registration or PCM routing fails. DMIC `no_pcm` differs from legacy and must match topology expectations.

## Test Signals
Validate ACP63/ACP70 SOF SoundWire cards, SOF topology loading, RT711 jack detect quirk, optional DMIC from quirk and `dmic_num`, DAI link names and pin numbers, suspend/resume through `snd_soc_pm_ops`, and cleanup on card registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-sof-mach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sof-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sof-mach.c

## Purpose
`acp-sof-mach.c` is the machine-driver entry point for non-SoundWire AMD ACP SOF boards. It maps platform device IDs to predefined `acp_card_drvdata` topologies, applies DMI TDM quirks, delegates DAI-link creation to the shared machine layer, and registers the ASoC card.

## Important APIs, Types, and Functions
Static topology records include `sof_rt5682_rt1019_data`, `sof_rt5682_max_data`, `sof_rt5682s_rt1019_data`, `sof_rt5682s_max_data`, `sof_nau8825_data`, `sof_rt5682s_hs_rt1019_data`, and `sof_nau8821_max98388_data`. The main function is `acp_sof_probe()`, and `board_ids[]` maps platform names to those records.

## Control Flow
Probe requires a platform ID entry, allocates `snd_soc_card`, assigns card name and driver data from the ID table, applies the `QUIRK_TDM_MODE_ENABLE` DMI quirk by setting `tdm_mode`, stores ACP revision from ACPI mach params, calls `acp_sofdsp_dai_links_create()`, and registers the card with device-managed ASoC registration.

## State and Persistence
The topology records are static module data and are mutated for fields such as `tdm_mode` and `acp_rev`; this persists for the module lifetime. Card allocations are devm-managed. No persistent storage exists.

## Dependencies and Integration Points
It depends on `acp-mach-common.c` for all link/widget/codec setup, `snd_soc_acpi_mach` platform data for ACP revision, `acp_quirk_table`, and platform IDs created by ACPI machine selection.

## Risks
Static `acp_card_drvdata` mutation can carry state across multiple probes of the same board ID. Missing or wrong platform data can dereference invalid `mach` fields. Any new board must express its complete endpoint/codec topology in the static table or shared link creation will produce incomplete cards.

## Test Signals
Test all `board_ids` names, TDM quirk systems, SOF headset/speaker/DMIC operation, card registration failures with missing codecs, and repeated probe/remove if supported by the platform-device lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sof-mach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp3x-es83xx/acp3x-es83xx.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp3x-es83xx/acp3x-es83xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp3x-es83xx/acp3x-es83xx.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp3x-es83xx/acp3x-es83xx.h

## Purpose
`acp3x-es83xx.h` declares the ES83xx machine-ops initializer used by ACP legacy machine data.

## Important APIs, Types, and Functions
The single exported declaration is `acp3x_es83xx_init_ops(struct acp_mach_ops *ops)`, which fills optional callbacks for probe, widget configuration, link configuration, suspend, and resume.

## Control Flow
Including code calls the initializer when it wants the generic ACP machine path to delegate ES83xx-specific behavior through `struct acp_mach_ops`.

## State and Persistence
The header owns no state. It depends on `struct acp_mach_ops` being visible from `acp-mach.h` before use.

## Dependencies and Integration Points
It is included by ES83xx-related machine selection code and implemented by `acp3x-es83xx.c`.

## Risks
The header does not include `acp-mach.h` itself, so include ordering matters. Prototype drift would break board-specific op installation at build time.

## Test Signals
Build coverage for ES83xx support and runtime confirmation that ES83xx callbacks are installed and invoked for `ESSX8336` systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp3x-es83xx/acp3x-es83xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp63.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp63.c

## Purpose
`acp63.c` is the ACP 6.3 platform driver. It defines SP/BT/HS I2S and PDM DAIs, programs ACP63 master clock PLL/DFS registers through AMD SMN, enables interrupts, registers the shared PCM component, and restores active streams after resume.

## Important APIs, Types, and Functions
Important objects/functions are `acp63_dai[]`, `union clk_pll_req_no`, `acp63_i2s_master_clock_generate()`, `acp63_audio_probe()`, `acp63_audio_remove()`, `acp63_pcm_resume()`, and platform driver `acp63_driver`.

## Control Flow
Probe validates revision `ACP63_PCI_ID`, sets DAI array/count, optionally programs I2S master clock when BIOS selected I2S and the resource requires SoC MCLK, enables ACP interrupts, registers the common platform component, and starts runtime PM. Resume regenerates MCLK when needed, then restores PTE/DMA and I2S/PDM stream parameters for every active stream in `chip->stream_list`.

## State and Persistence
No private state is allocated here. PLL/DFS hardware state and ACP stream registers are volatile and reprogrammed on probe/resume. Stream state is owned by the common platform layer.

## Dependencies and Integration Points
The file depends on AMD SMN read/write helpers, common ACP hardware ops, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, `config_pte_for_stream()`, `config_acp_dma()`, and restore helpers. `acp-pci.c` creates the `acp_asoc_acp63` platform device.

## Risks
Clock register programming is sequence-sensitive and has minimal polling compared with Rembrandt. One branch writes `data | PLL_FRANCE_EN` only when the bit is already set, which is hardware-specific and should be verified against clock specs. Probe does not check `acp_platform_register()` return.

## Test Signals
Test ACP63 SP/BT/HS playback/capture, PDM capture, SoC MCLK boards, suspend/resume with active I2S and DMIC streams, unsupported revision rejection, and interrupt disable on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp63.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp70.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp70.c

## Purpose
`acp70.c` is the ACP 7.0/7.1/7.2 platform driver. It defines high-channel-count SP/BT/HS I2S and PDM DAIs, sets the ACP7x master clock divider, enables interrupts, registers the shared PCM component, and restores stream configuration on resume.

## Important APIs, Types, and Functions
Key objects/functions are `acp70_dai[]`, `acp_acp70_audio_probe()`, `acp_acp70_audio_remove()`, `acp70_pcm_resume()`, `acp70_dma_pm_ops`, and platform driver `acp70_driver`.

## Control Flow
Probe accepts ACP revisions `0x70`, `0x71`, and `0x72`, assigns the DAI array/count, writes `CLK7_CLK0_DFS_CNTL_N1` to set the I2S master clock near 196.608 MHz, enables ACP interrupts, registers the common PCM platform, and enables runtime PM. Resume walks live streams and restores PTE/DMA plus I2S/PDM parameters.

## State and Persistence
All runtime state lives in shared `struct acp_chip_info` and common `struct acp_stream` objects. ACP7x clock/divider and DMA registers are volatile across reset/sleep and restored by probe/resume paths.

## Dependencies and Integration Points
The driver depends on AMD SMN write support, common ACP platform registration, common CPU/PDM DAI ops, and ACP7x-specific DMA PTE mapping in `acp-platform.c`. It is instantiated as `acp_asoc_acp70`.

## Risks
The divider is programmed unconditionally for all accepted ACP7x revisions; board-specific clock exceptions would require additional gating. `acp_platform_register()` return is ignored. ACP70 allows up to 32 channels and 192 kHz, so machine/codec constraints must narrow unsupported external codecs.

## Test Signals
Validate ACP70/71/72 probe, SP/BT/HS 2-32 channel playback/capture, PDM capture, master-clock divider programming errors, suspend/resume with active streams, and removal with PM disabled and interrupts off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp70.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp_common.h

## Purpose
`acp_common.h` centralizes numeric AMD ACP PCI revision IDs used across PCI, platform, machine, and SoundWire code.

## Important APIs, Types, and Functions
It defines `ACP_RN_PCI_ID`, `ACP_VANGOGH_PCI_ID`, `ACP_RMB_PCI_ID`, `ACP63_PCI_ID`, `ACP70_PCI_ID`, `ACP71_PCI_ID`, and `ACP72_PCI_ID`.

## Control Flow
There is no executable control flow. Other files switch on these constants to select resources, DAI arrays, clock programming, platform component names, and DMA window mappings.

## State and Persistence
The header owns no state.

## Dependencies and Integration Points
It is included by `amd.h`, `acp-mach.h`, and revision-specific platform drivers. The values must match PCI revision values observed in `struct pci_dev->revision` and SoundWire mach params.

## Risks
A wrong constant cascades through platform matching, DMA mapping, and machine selection. Adding a new ACP revision requires updating switch statements and ACPI tables beyond this header.

## Test Signals
Build and runtime probe for each known revision are the main signals. Unsupported-revision logs in PCI/platform drivers help detect missing additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp63-acpi-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp63-acpi-match.c

## Purpose
`amd-acp63-acpi-match.c` defines ACPI SoundWire machine tables for ACP 6.3 platforms. It enumerates supported SoundWire address/link layouts and maps them to either legacy `amd_sdw` or SOF `amd_sof_sdw` machine drivers with topology/firmware metadata where needed.

## Important APIs, Types, and Functions
The exported arrays are `snd_soc_acpi_amd_acp63_sof_sdw_machines[]` and `snd_soc_acpi_amd_acp63_sdw_machines[]`. The file defines many `snd_soc_acpi_endpoint`, `snd_soc_acpi_adr_device`, and `snd_soc_acpi_link_adr` tables for Realtek RT711/RT1316/RT714/RT722 and Cirrus CS42L43/CS42L45/CS35L56/CS35L63 combinations.

## Control Flow
There is no runtime function flow in this file. ACPI machine selection code scans the exported arrays, matches `link_mask` and address tables against discovered SoundWire peripherals, and instantiates the named machine driver. Endpoint metadata describes aggregation, group positions, and endpoint numbers consumed by SoundWire utility parsing.

## State and Persistence
All tables are static constant data except exported machine arrays. They persist for module lifetime and do not change at runtime.

## Dependencies and Integration Points
It depends on `sound/soc-acpi.h` and `mach-config.h`. The `drv_name` values must correspond to platform drivers in `acp-sdw-legacy-mach.c` and `acp-sdw-sof-mach.c`; topology and firmware filenames must exist for SOF entries.

## Risks
Address constants are exact hardware IDs; a transposed link/user/instance value can prevent matching or route endpoints incorrectly. Aggregated speaker group positions must align with codec driver channel maps. Table order can matter when multiple entries share link masks.

## Test Signals
Boot-time ACPI matching on each supported ACP63 design, successful machine driver instantiation, generated DAI links for jack/amp/DMIC endpoints, four-speaker aggregation channel mapping, and SOF topology load for the RT711/RT1316/RT714 entry are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp63-acpi-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp70-acpi-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp70-acpi-match.c

## Purpose
`amd-acp70-acpi-match.c` defines ACPI SoundWire machine tables for ACP 7.0/7.1 platforms. It extends ACP63-style layouts with newer Realtek, Cirrus, TI, and SDCA/RT712 VB-specific match cases, and provides both legacy and SOF SoundWire machine entries.

## Important APIs, Types, and Functions
The exported arrays are `snd_soc_acpi_amd_acp70_sdw_machines[]` and `snd_soc_acpi_amd_acp70_sof_sdw_machines[]`. It defines endpoint/address/link tables for RT711/RT1316/RT714, RT722, RT1320, RT721 with TAS2783 amps, RT712 VB, CS42L43/CS42L45, CS35L56, and CS35L63 layouts. One machine entry uses `snd_soc_acpi_amd_sdca_is_device_rt712_vb()` as `machine_check`.

## Control Flow
Runtime ACPI/SoundWire matching scans these tables and instantiates `amd_sdw` or `amd_sof_sdw` when link masks and address descriptors match. The RT712 VB entry adds a machine-check callback that inspects discovered SDCA peripheral quirks before accepting the entry.

## State and Persistence
The file is static table data only. Machine arrays persist for module lifetime.

## Dependencies and Integration Points
It depends on `soc-acpi-amd-sdca-quirks.h`, `sound/soc-acpi.h`, and `mach-config.h`. `drv_name`, topology filenames, and firmware filenames must align with the AMD SoundWire machine drivers and SOF firmware packaging.

## Risks
Because many entries share identical link masks, ordering and machine-check specificity are important. Endpoint numbers document codec-specific functions such as RT721/RT722 DMIC versus amp paths; wrong endpoint counts can create missing or extra DAI links. Conditional namespace import must match the SDCA quirk config.

## Test Signals
Validate ACP70/71 systems for all listed layouts, especially RT1320/RT722 link-order variants, RT712 VB machine-check filtering, RT721 plus TAS2783 speaker aggregation, SOF RT722 topology loading, and generated component strings showing expected amp/mic counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp70-acpi-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acpi-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acpi-mach.c

## Purpose
`amd-acpi-mach.c` provides non-SoundWire ACP ACPI machine match tables for Renoir, Rembrandt, ACP63, and ACP70 legacy ACP configurations.

## Important APIs, Types, and Functions
It exports `snd_soc_acpi_amd_acp_machines[]`, `snd_soc_acpi_amd_rmb_acp_machines[]`, `snd_soc_acpi_amd_acp63_acp_machines[]`, and `snd_soc_acpi_amd_acp70_acp_machines[]`. It also defines codec-list quirk descriptors for RT1019 and MAX98360A amplifiers.

## Control Flow
ACPI machine selection code scans the revision-appropriate exported array. Entries match primary codec/device IDs and optional secondary codec lists through `snd_soc_acpi_codec_list`, then instantiate the named machine driver such as `acp3xalc56821019`, `rembrandt-acp`, `acp63-acp`, or `acp70-acp`.

## State and Persistence
Only static table data is present. The tables are exported for other modules and remain constant for module lifetime.

## Dependencies and Integration Points
The file depends on `sound/soc-acpi.h` and the platform/machine drivers named in `.drv_name`. `acp-pci.c` points `chip->machines` at these arrays based on PCI revision.

## Risks
Overlapping IDs such as `RTL5682` rely on codec-list quirks to distinguish amplifier combinations. A wrong `drv_name` breaks platform-driver binding. New ACPI IDs need matching board data in machine drivers, not just table entries.

## Test Signals
Boot ACPI matching for Renoir/Rembrandt/ACP63/ACP70, correct machine driver names, secondary amplifier detection for RT1019/MAX98360A, and fallback termination at empty array entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acpi-mach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-sdw-acpi.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-sdw-acpi.c

## Purpose
`amd-sdw-acpi.c` provides a small ACPI helper for AMD SoundWire controller discovery. It reads the firmware-reported SoundWire manager bitmap and stores the active link mask in caller-supplied context.

## Important APIs, Types, and Functions
The exported function is `amd_sdw_scan_controller(struct sdw_amd_acpi_info *info)`.

## Control Flow
The helper fetches the ACPI device from `info->handle`, reads `mipi-sdw-manager-list` as a `u32`, counts enabled bits, validates the count against `info->count`, rejects zero-manager systems, logs discovery, and stores the bitmap in `info->link_mask`.

## State and Persistence
The function owns no persistent state. It writes discovery output into the caller's `sdw_amd_acpi_info` object.

## Dependencies and Integration Points
It depends on ACPI fwnode property APIs, bit counting, and SoundWire AMD data structures. It is exported under namespace `SND_AMD_SOUNDWIRE_ACPI` for AMD SoundWire controller/ACPI selection code.

## Risks
Firmware property absence, zero bitmap, or count overflow all return `-EINVAL`; caller code must distinguish unsupported from malformed firmware only through logs. The helper assumes a single `u32` property value.

## Test Signals
Test ACPI devices with no property, zero managers, one/two managers, and a bitmap exceeding caller capacity. Logs should show discovered manager count and link mask consumers should instantiate matching ACPI machine tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-sdw-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd.h

## Purpose
`amd.h` is the core private header for AMD ACP legacy drivers. It defines ACP instance IDs, memory windows, FIFO/PTE offsets, PCM limits, PDM constants, power/reset constants, common data structures, external resources, DAI ops, and helper prototypes.

## Important APIs, Types, and Functions
Important types are `struct acp_chip_info`, `struct acp_stream`, `struct acp_resource`, `struct snd_acp_hw_ops`, and `enum acp_config`. Important declarations include revision resources `rn_rsrc`, `rmb_rsrc`, `acp63_rsrc`, `acp70_rsrc`, machine tables, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, platform register/unregister helpers, machine selection, hardware init/deinit, interrupt helpers, config helpers, parameter restore helpers, DMA/PTE helpers, byte-count access, and hardware-op wrappers.

## Control Flow
There is no executable flow in the header, but it defines the contract used by PCI probe, platform drivers, PCM open/hw_params/pointer, I2S/PDM DAI callbacks, IRQ handlers, and suspend/resume restore flows.

## State and Persistence
The header defines all major volatile state containers. `acp_chip_info` is per PCI/platform device; `acp_stream` is per PCM stream; `acp_resource` is per ACP revision. Register constants describe hardware state that must be initialized and restored.

## Dependencies and Integration Points
It includes ALSA PCM/ASoC headers, `soc-acpi`, `soc-dai`, `acp_common.h`, and `chip_offset_byte.h`. It is the integration header across nearly all ACP legacy files in this subset and companion files such as I2S and legacy common code.

## Risks
This header is broad and tightly couples files through shared mutable structures. Changes to `struct acp_chip_info` or `struct acp_stream` can affect PCI, PCM, IRQ, PM, and DAI code. Register and memory-window constants must match hardware generations.

## Test Signals
Build coverage across all ACP drivers is essential. Runtime signals include correct revision-specific resource selection, stream list handling, DMA mapping, IRQ processing, and suspend/resume restoration across Renoir, Rembrandt, ACP63, and ACP70.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/chip_offset_byte.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/chip_offset_byte.h

## Purpose
`chip_offset_byte.h` defines ACP MMIO register offsets and address macros for ATU, power/reset, external interrupts, I2S/BT/HS DMA buffer registers, I2S/TDM control blocks, PDM/WOV registers, and master-clock generators.

## Important APIs, Types, and Functions
Important macros include `ACP_EXTERNAL_INTR_ENB()`, `ACP_EXTERNAL_INTR_CNTL()`, `ACP_EXTERNAL_INTR_STAT()`, `ACP_I2S_REG_ADDR()`, many `ACP_I2S_*`, `ACP_BT_*`, `ACP_HS_*`, `ACP_WOV_*` offsets, ATU group registers, `ACP_SOFT_RESET`, `ACP_CONTROL`, and TDM master clock registers.

## Control Flow
There is no function flow. Runtime code uses these macros to calculate register addresses from `chip->base`, resource offsets, interrupt-controller index, and generation-specific resource fields.

## State and Persistence
The header owns no state. It names hardware state accessed by ACP init/deinit, interrupt handlers, I2S/PDM trigger/prepare, DMA configuration, and pointer logic.

## Dependencies and Integration Points
It is included by `amd.h`, and therefore used throughout ACP common, platform, PDM, I2S, PCI, and SoC-specific code. Register offsets must align with ACP hardware documentation for each generation.

## Risks
Offset mistakes can corrupt unrelated ACP registers. Macros that depend on `rsrc->irqp_used`, `irq_reg_offset`, and `no_of_ctrls` are sensitive to resource-table correctness. HS offsets are direct constants while SP/BT use macros, so generation coverage differs.

## Test Signals
Hardware smoke tests for interrupt enable/status/clear, I2S SP/BT/HS playback/capture, PDM capture, ATU page programming, and suspend/resume register restoration are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/chip_offset_byte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.c

## Purpose
`soc-acpi-amd-sdca-quirks.c` implements an AMD SoundWire/SDCA machine-check helper used to filter ACPI machine entries for RT712 VB-style devices.

## Important APIs, Types, and Functions
The exported function is `snd_soc_acpi_amd_sdca_is_device_rt712_vb(void *arg)`.

## Control Flow
The helper treats `arg` as `struct sdw_amd_ctx`, rejects null context, iterates discovered SoundWire peripherals, and returns true if any peripheral matches `SDCA_QUIRKS_RT712_VB` through `sdca_device_quirk_match()`.

## State and Persistence
The file has no mutable state. It reads the caller's discovery context and peripheral array.

## Dependencies and Integration Points
It depends on AMD SoundWire context definitions, SDCA quirk matching, and ASoC ACPI machine matching. `amd-acp70-acpi-match.c` uses it as a `machine_check` callback for the RT712 VB entry.

## Risks
The callback argument is not a traditional `snd_soc_acpi_mach` pointer, so callers must pass the AMD SoundWire context documented in the comment. A false result skips the machine entry, which can hide hardware if peripheral quirk detection is incomplete.

## Test Signals
Validate machine selection with RT712 VB peripherals present and absent, null-context behavior, and namespace import/export under `CONFIG_SND_SOC_ACPI_AMD_SDCA_QUIRKS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.h

## Purpose
`soc-acpi-amd-sdca-quirks.h` declares the optional SDCA machine-check helper and provides a false-returning stub when the quirk helper is not enabled.

## Important APIs, Types, and Functions
The key API is `snd_soc_acpi_amd_sdca_is_device_rt712_vb(void *arg)`, either as an external declaration or static inline stub depending on `CONFIG_SND_SOC_ACPI_AMD_SDCA_QUIRKS`.

## Control Flow
Including ACPI match tables can call the helper unconditionally. With the config disabled, the inline stub always rejects the special machine entry.

## State and Persistence
The header owns no state.

## Dependencies and Integration Points
It is included by `amd-acp70-acpi-match.c`. The enabled implementation is in `soc-acpi-amd-sdca-quirks.c`.

## Risks
When the config is disabled, RT712 VB-specific entries are never selected. Function signature uses `void *`, so type mismatches are only caught by runtime behavior.

## Test Signals
Build both enabled and disabled configurations. Runtime matching should select RT712 VB only when the config and peripheral quirk detection are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc_amd_sdw_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc_amd_sdw_common.h

## Purpose
`soc_amd_sdw_common.h` defines shared constants and context for AMD ACP SoundWire machine drivers.

## Important APIs, Types, and Functions
Key definitions include max link/group constants, ACP revision IDs for SoundWire matching, quirk bits `SOC_JACK_JDSRC()`, `ASOC_SDW_FOUR_SPK`, `ASOC_SDW_ACP_DMIC`, and `ASOC_SDW_CODEC_SPKR`, SoundWire link IDs, ACP63/ACP70 CPU pin IDs, `ACP_DMIC_BE_ID`, `struct amd_mc_ctx`, and prototypes for `get_acp63_cpu_pin_id()` and `get_acp70_cpu_pin_id()`.

## Control Flow
There is no executable flow. Legacy and SOF SoundWire machine drivers use these constants while parsing ACPI SoundWire endpoints and creating DAI links.

## State and Persistence
The header owns no state. `struct amd_mc_ctx` defines per-card context fields for ACP revision and maximum SoundWire links.

## Dependencies and Integration Points
It includes Linux bits/types, ASoC, and SoundWire utility headers. It is included by SoundWire machine-common, legacy machine, and SOF machine files.

## Risks
Quirk bit allocation and CPU pin values are shared contracts; changes must stay synchronized with machine drivers, codec utility expectations, and CPU DAI naming. Duplicated ACP revision constants overlap with `acp_common.h` and must remain consistent.

## Test Signals
Build SoundWire drivers and validate generated DAI names/pin IDs for ACP63 and ACP70-class hardware, plus DMI quirk behavior for jack source, codec speakers, and ACP DMIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc_amd_sdw_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp3x-rt5682-max9836.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp3x-rt5682-max9836.c

## Purpose
`acp3x-rt5682-max9836.c` is an older ACP3x board machine driver for RT5682 headset codec with MAX98357/RT1015/RT1015P speakers and optional Chrome EC DMIC capture. It declares static cards, DAI links, widgets, routes, controls, clock handling, jack handling, and ACPI matching.

## Important APIs, Types, and Functions
Main functions are `acp3x_probe()`, `soc_is_rltk_max()`, `card_spk_dai_link_present()`, `acp3x_5682_init()`, `rt5682_clk_enable()`, `rt5682_clk_disable()`, `acp3x_5682_startup()`, `acp3x_max_startup()`, `acp3x_ec_dmic0_startup()`, `acp3x_1015_hw_params()`, `dmic_get()`, `dmic_set()`, and `rt5682_shutdown()`. Static cards are `acp3x_5682`, `acp3x_1015`, and `acp3x_1015p`.

## Control Flow
ACPI match data points probe at one of the static card definitions. Probe allocates `acp3x_platform_info`, adjusts the speaker DAI link codec based on selected card, stores card drvdata, acquires a `dmic` GPIO, and registers the card. RT5682 init sets codec DAI format, PLL, sysclk, BCLK ratio, clock handles, and headset jack. Startup callbacks set ACP I2S instance fields, constrain rates/channels to stereo 48 kHz, and enable RT5682 word clock. Speaker `hw_params` programs RT1015 PLL/sysclk when present. The DMIC mux control toggles the `dmic` GPIO.

## State and Persistence
The driver uses static card and DAI-link objects that are modified at probe time, module-global RT5682 clock pointers, module-global jack object, module-global DMIC GPIO and switch state, and per-card `acp3x_platform_info`. This state persists for module lifetime or platform-device lifetime.

## Dependencies and Integration Points
It depends on legacy Raven ACP3x platform definitions, RT5682 and RT1015 codec APIs, ACPI IDs `AMDI5682`, `AMDI1015`, and `10021015`, `snd_soc_pm_ops`, GPIO consumer APIs, and ACP3x I2S/DMA platform component names.

## Risks
Static mutable cards and links make multiple-instance behavior fragile. Clock enable is shared across links; overlapping headset/speaker/EC streams can imbalance enable/disable. `dmic_sel` is mandatory even for routes that may not need it. The filename says max9836 while code uses MAX98357-style codec IDs, which can confuse maintenance.

## Test Signals
Validate all three ACPI IDs, headset jack/buttons, 48 kHz stereo constraints, speaker playback through MAX98357/RT1015/RT1015P, Chrome EC DMIC capture, DMIC mux GPIO changes, suspend/resume via `snd_soc_pm_ops`, and repeated stream open/close clock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp3x-rt5682-max9836.c -->
