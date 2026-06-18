# Research Group: subset-b-006516

This grouped report covers the assigned ASoC source files under Intel, Ingenic JZ4740, Kirkwood/MVEBU, Loongson, and MediaTek. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ssp-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ssp-common.c

## Purpose
Provides Intel ACPI SSP machine-driver helper routines for detecting board codec and amplifier parts by ACPI HID and mapping those parts to topology filename suffixes and printable names.

## Important APIs, Types, And Functions
The private `struct codec_map` binds user-visible part names, topology suffixes, ACPI HIDs, and `enum snd_soc_acpi_intel_codec` values. `snd_soc_acpi_intel_detect_codec_type()` scans the `codecs[]` table with `acpi_dev_present()`. `snd_soc_acpi_intel_detect_amp_type()` does the same for `amps[]`. `snd_soc_acpi_intel_get_codec_name()`, `snd_soc_acpi_intel_get_codec_tplg_suffix()`, and `snd_soc_acpi_intel_get_amp_tplg_suffix()` provide reverse lookups. All helpers are exported in the `SND_SOC_ACPI_INTEL_MATCH` namespace.

## Control Flow, State, And Persistence
The file is table-driven and keeps no persistent runtime state. Detection is first-match-wins, so table ordering matters. The amp table intentionally places monolithic codec/amp-capable parts after dedicated amp parts to avoid selecting a codec as an amp too early.

## Dependencies And Integration Points
Depends on ACPI enumeration, `sound/soc-acpi.h`, and Intel SSP ACPI HID definitions from `sound/soc-acpi-intel-ssp-common.h`. SOF and machine matching code use the exported helpers while completing topology filenames and choosing machine quirks.

## Risks And Test Signals
Risks are stale HID/suffix mappings, duplicate enum entries across codec and amp lists, and unexpected selection caused by table ordering. Test signals include ACPI mock systems with each HID, topology-name completion tests for codec plus amp combinations, and kernel logs showing the detected part names through `dev_dbg()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ssp-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-tgl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-tgl-match.c

## Purpose
Defines Tiger Lake ACPI and SoundWire machine-match tables used by Intel ASoC/SOF enumeration to select the correct machine driver, topology file, SoundWire link layout, codec endpoint aggregation, and codec-specific quirk handling.

## Important APIs, Types, And Functions
The file exports `snd_soc_acpi_intel_tgl_machines[]` for non-SoundWire ACPI codec matching and `snd_soc_acpi_intel_tgl_sdw_machines[]` for SoundWire-only layouts. Most content is static `snd_soc_acpi_endpoint`, `snd_soc_acpi_adr_device`, `snd_soc_acpi_link_adr`, and `snd_soc_acpi_codecs` data. It covers Realtek RT711/RT1308/RT715/RT5682, RT711/RT1316/RT714 SDCA, RT712 combinations, Cirrus CS42L43/CS35L56 combinations, Maxim MX8373, ESSX83x6, LT6911 HDMI, and mockup links.

## Control Flow, State, And Persistence
There is no executable control flow beyond module export. Runtime behavior comes from the core ACPI/SoundWire matcher traversing the arrays in order. Earlier entries have priority, so mockups and more-specific four-link layouts are placed before generic or fallback layouts. Endpoint fields such as `aggregated`, `group_position`, and `group_id` persist only as static description data consumed by the SoundWire machine driver.

## Dependencies And Integration Points
Depends on `sound/soc-acpi.h`, `sound/soc-acpi-intel-match.h`, Intel SSP common IDs, and `soc-acpi-intel-sdw-mockup-match.h`. The arrays integrate with SOF `sof_sdw` and TGL-specific machine drivers through `drv_name`, `sof_tplg_filename`, `link_mask`, `links`, `machine_quirk`, and `quirk_data`.

## Risks And Test Signals
Risks include match-order regressions, wrong SoundWire ADR values, endpoint aggregation mistakes, and topology filename drift. The local source also shows syntax-looking damage in the CS35L56 right feedback endpoint block, which would be a compile-time failure if present in a build path. Test signals are compile coverage, ACPI/SoundWire enumeration logs, topology load success for each `sof_tplg_filename`, and mockup table selection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-tgl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-intel-quirks.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-intel-quirks.h

## Purpose
Provides a shared inline Bay Trail CR platform-detection helper for Intel SST and SOF drivers, allowing both stacks to handle legacy Bay Trail interrupt-resource quirks consistently.

## Important APIs, Types, And Functions
`soc_intel_is_byt_cr(struct platform_device *pdev)` is the only exported header API. When `CONFIG_IOSF_MBI` is reachable, it checks SoC family, a DMI force table for Lenovo Yoga Tablet 2 systems, IOSF PUNIT `BIOS_CONFIG` PMIC bits, and a fallback IRQ-resource layout check. Without IOSF MBI support it compiles to `false`.

## Control Flow, State, And Persistence
The helper is inline and stateless. It returns early on non-Bay Trail systems, forced DMI matches, successful PMIC-bit detection, and missing IRQ index 5. It logs detection or fallback decisions through the platform device.

## Dependencies And Integration Points
Depends on `linux/platform_data/x86/soc.h`, DMI, IOSF MBI, and platform IRQ resources. Integration is by including the header from SST/SOF platform drivers that need to know whether IPC IRQ index 0 should be used as on Bay Trail CR.

## Risks And Test Signals
Risks are false positives from the IRQ-resource fallback, unavailable IOSF MBI on systems that need precise detection, and stale DMI exceptions. Test signals include Bay Trail CR and non-CR boot logs, IPC IRQ selection, and compile coverage with and without `CONFIG_IOSF_MBI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-intel-quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.c

## Purpose
Builds a list of separated SOF SoundWire function topology files based on the card's DAI links, then validates that each firmware topology file exists before returning the list.

## Important APIs, Types, And Functions
`sof_sdw_get_tplg_files()` is exported with GPL visibility. The private `enum tplg_device_id` tracks SDCA jack, SDCA amp, SDCA mic, Intel PCH DMIC, HDMI, and maximum IDs. The helper parses the platform name from `mach->sof_tplg_filename`, scans `card` prelinks, maps DAI-link names such as `SimpleJack`, `SmartAmp`, `SmartMic`, `dmic`, and `iDisp` to function topology filenames, suppresses duplicates with `tplg_mask`, and calls `firmware_request_nowarn()` for existence checks.

## Control Flow, State, And Persistence
The function is request-scoped. It copies `mach_params`, fills caller-provided `tplg_files`, and uses `devm_kasprintf()` so filename memory is device-managed. Unsupported links either abort separated-topology use by returning `0` or are skipped in `best_effort` mode. Missing firmware also returns `0`, signaling fallback to the monolithic topology path rather than a hard probe failure.

## Dependencies And Integration Points
Depends on ASoC card/prelink iteration, firmware loader APIs, SOF machine descriptors, and naming conventions under the topology firmware search path. DMIC filenames include the parsed platform because NHLT blobs vary by platform.

## Risks And Test Signals
Risks include fragile DAI-link substring matching, unsupported DMIC counts other than two or four, the fixed three-character platform parse, and `tplg_files` capacity assumptions owned by the caller. Test signals include machines with mixed SDCA/DMIC/HDMI links, missing firmware fallback logs, and successful topology componentization with `best_effort` both true and false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.h

## Purpose
Declares the Intel SOF separated-function topology helper used by SoundWire-capable machine code.

## Important APIs, Types, And Functions
The header exposes `sof_sdw_get_tplg_files(struct snd_soc_card *card, const struct snd_soc_acpi_mach *mach, const char *prefix, const char ***tplg_files, bool best_effort)`. It includes only the declaration and include guard.

## Control Flow, State, And Persistence
The header has no state or control flow. It defines the ABI contract for callers that allocate or pass a topology filename array and decide whether unsupported links should be skipped.

## Dependencies And Integration Points
Consumers must already have ASoC and ACPI machine types visible through their includes. The implementation depends on firmware loading and card prelink traversal.

## Risks And Test Signals
Risks are declaration drift from the implementation and ambiguous ownership/capacity of `tplg_files`. Test signals are compile coverage for all users and runtime validation that callers size the returned filename array for the number of card prelinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/keembay/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/keembay/Makefile

## Purpose
Builds the Intel Keem Bay ASoC platform driver object when `CONFIG_SND_SOC_INTEL_KEEMBAY` is enabled.

## Important APIs, Types, And Functions
Defines `snd-soc-kmb_platform-y := kmb_platform.o` and adds `snd-soc-kmb_platform.o` to `obj-$(CONFIG_SND_SOC_INTEL_KEEMBAY)`.

## Control Flow, State, And Persistence
There is no runtime state. The file controls kernel build composition for the Keem Bay audio platform module.

## Dependencies And Integration Points
Integrates with the sound/soc/intel Kbuild hierarchy and the Kconfig symbol that selects Keem Bay support.

## Risks And Test Signals
Risks are stale object names or mismatched Kconfig symbols. Test signals are `make M=sound/soc/intel/keembay` and full kernel builds with the config enabled as built-in and module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/keembay/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.c

## Purpose
Implements the Intel Keem Bay I2S/HDMI-I2S/TDM ASoC CPU DAI and platform component, supporting DMA operation when DT `dmas` are present and interrupt-driven PIO operation otherwise.

## Important APIs, Types, And Functions
Key routines include PIO transfer helpers `kmb_pcm_tx_fn()`, `kmb_pcm_rx_fn()`, HDMI IEC958 conversion `hdmi_reformat_iec958()`, IRQ handler `kmb_i2s_irq_handler()`, DAI ops `kmb_set_dai_fmt()`, `kmb_dai_trigger()`, `kmb_dai_hw_params()`, `kmb_dai_prepare()`, `kmb_dai_startup()`, and `kmb_dai_hw_free()`, plus probe `kmb_plat_dai_probe()`. It registers DAI variants `intel_kmb_hdmi_dai`, `intel_kmb_i2s_dai`, and `intel_kmb_tdm_dai`.

## Control Flow, State, And Persistence
Probe maps I2S and PSS registers, prepares APB/osc clocks, reads FIFO depth, chooses PIO vs DMA, registers the component, and disables channels at boot. Runtime state lives in `struct kmb_i2s_info`: active stream count, configured channel count/rate/width, FIFO threshold, DMA addresses, PIO substream pointers, buffer positions, and IEC958 mode. `hw_params` programs data width, transfer resolution, channel mode, clock-provider limits, PSS config, and optional bit clock rate. Trigger starts/stops I2S, IRQs, or DMA handshakes.

## Dependencies And Integration Points
Depends on DT compatible strings `intel,keembay-i2s`, `intel,keembay-hdmi-i2s`, and `intel,keembay-tdm`, MMIO resources, `apb_clk`, `osc`, optional IRQ, optional DMA channels, ASoC, and dmaengine PCM.

## Risks And Test Signals
Risks include active-count imbalance, PIO pointer races, 2-channel master-only restrictions, multi-channel capture requiring clock-consumer mode, IEC958 in-place buffer mutation, optional IRQ with PIO mode, and DMA stop split between trigger and `hw_free`. Test signals include playback/capture for S16/S24/S32/IEC958, DMA and PIO paths, two/four/eight channel cases, clock-provider format combinations, underrun/overrun logs, and suspend/remove clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.h

## Purpose
Defines Keem Bay I2S register offsets, bit fields, capabilities, DMA registers, clock configuration data, and the driver-private runtime state structure.

## Important APIs, Types, And Functions
Macros cover common I2S control registers, per-channel FIFO/enable/config registers, component-parameter field extractors, PSS reset/clock registers, interrupt masks, DMA handshake registers, supported channel constants, and capability bits. `struct i2s_clk_config_data` stores channels, data width, and sample rate. `struct kmb_i2s_info` stores MMIO bases, clocks, active stream state, capabilities, clock mode, DMA data, PIO substreams and pointers, and IEC958 state.

## Control Flow, State, And Persistence
The header has no control flow, but its structure layout is the persistent in-memory state for the platform driver from probe through stream operations.

## Dependencies And Integration Points
Used by `kmb_platform.c`; depends on Linux bitfield helpers, types, clocks through opaque pointers, and ASoC dmaengine data.

## Risks And Test Signals
Risks are incorrect register offsets or field definitions against the Keem Bay databook, mismatch between FIFO-depth extraction and hardware, and structure fields unused or inconsistently updated by DMA vs PIO paths. Test signals are register trace validation, PIO IRQ behavior, DMA handshake behavior, and all compatible variants probing correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/jz4740/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/jz4740/Kconfig

## Purpose
Defines the build-time option for the Ingenic JZ4740-family I2S ASoC CPU DAI driver.

## Important APIs, Types, And Functions
`config SND_JZ4740_SOC_I2S` is a tristate option depending on `MIPS || COMPILE_TEST` and `HAS_IOMEM`, selecting `REGMAP_MMIO` and `SND_SOC_GENERIC_DMAENGINE_PCM`.

## Control Flow, State, And Persistence
No runtime state exists. The symbol controls whether the JZ4740 I2S platform driver participates in the build.

## Dependencies And Integration Points
Integrates with the sound SoC Kconfig menu and the matching Makefile object rule. The selects align with the driver's regmap MMIO and dmaengine PCM usage.

## Risks And Test Signals
Risks are missing dependencies for OF, clock, or DMA APIs if build coverage changes. Test signals are allmodconfig and COMPILE_TEST builds for non-MIPS architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/jz4740/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/jz4740/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/jz4740/Makefile

## Purpose
Builds the Ingenic JZ4740 I2S ASoC driver object.

## Important APIs, Types, And Functions
Defines `snd-soc-jz4740-i2s-y := jz4740-i2s.o` and adds the composite object to `obj-$(CONFIG_SND_JZ4740_SOC_I2S)`.

## Control Flow, State, And Persistence
No runtime state; this is build graph metadata.

## Dependencies And Integration Points
Consumes the Kconfig symbol from `Kconfig` and integrates with the ALSA SoC directory build.

## Risks And Test Signals
Risks are object naming drift. Test signals are module and built-in builds of `CONFIG_SND_JZ4740_SOC_I2S`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/jz4740/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/jz4740/jz4740-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/jz4740/jz4740-i2s.c

## Purpose
Implements the Ingenic JZ4740/JZ4760/JZ4770/JZ4780/X1000 I2S ASoC CPU DAI using MMIO regmap fields and generic dmaengine PCM.

## Important APIs, Types, And Functions
`struct i2s_soc_info` describes per-SoC DAI and register-field layout. `struct jz4740_i2s` stores regmap fields, clocks, DMA data, and selected SoC data. DAI ops include `jz4740_i2s_startup()`, `shutdown()`, `trigger()`, `set_fmt()`, and `hw_params()`. Component callbacks handle probe/remove/suspend/resume. `jz4740_i2s_dev_probe()` maps resources, creates regmap fields, registers the component, and registers dmaengine PCM.

## Control Flow, State, And Persistence
Probe stores the SoC match data, maps the AIC register block, sets FIFO DMA addresses, gets `aic` and `i2s` clocks, and allocates field accessors. Startup flushes FIFOs carefully depending on whether the SoC has a shared flush bit, enables `clk_i2s`, and enables the AIC only for the first active stream. `hw_params` sets sample size, mono playback expansion, and clock divider if the CPU supplies bit or frame clock. Suspend saves active state by disabling clocks and AIC, while resume restores clocks and enable state.

## Dependencies And Integration Points
Depends on DT compatibles for multiple Ingenic SoCs, regmap MMIO, ASoC DAI/component APIs, clocks, and generic dmaengine PCM. DMA uses the shared AIC FIFO address with maxburst 16.

## Risks And Test Signals
Risks include divider error rejection above 5 percent, different FIFO flush semantics across SoCs, capture only supporting stereo, and rate constraints being continuous but constrained by clock divider accuracy. Test signals are playback and capture across all supported formats/rates, master/slave clock format permutations, suspend/resume with active streams, and SoC-specific field layout validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/jz4740/jz4740-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/kirkwood/Kconfig

## Purpose
Defines build options for Marvell Kirkwood/Dove/MVEBU audio and the Armada 370 DB machine driver.

## Important APIs, Types, And Functions
`SND_KIRKWOOD_SOC` enables the core I2S/SPDIF controller support for `ARCH_DOVE`, `ARCH_MVEBU`, or `COMPILE_TEST`. `SND_KIRKWOOD_SOC_ARMADA370_DB` depends on the core driver, MVEBU/COMPILE_TEST, and I2C, selecting CS42L51 and SPDIF codec support.

## Control Flow, State, And Persistence
No runtime state exists. The symbols select which controller and board glue objects are built.

## Dependencies And Integration Points
Matches the Kirkwood Makefile and the `armada-370-db.c` codec requirements.

## Risks And Test Signals
Risks are missing dependencies for OF, clocks, or MBUS APIs under COMPILE_TEST. Test signals are compile coverage for both core and board symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/kirkwood/Makefile

## Purpose
Builds the Kirkwood/MVEBU audio controller module and the Armada 370 DB machine module.

## Important APIs, Types, And Functions
`snd-soc-kirkwood-y` combines `kirkwood-dma.o` and `kirkwood-i2s.o`; `snd-soc-armada-370-db-y` builds `armada-370-db.o`.

## Control Flow, State, And Persistence
This is build metadata only.

## Dependencies And Integration Points
Integrates with `CONFIG_SND_KIRKWOOD_SOC` and `CONFIG_SND_KIRKWOOD_SOC_ARMADA370_DB`.

## Risks And Test Signals
Risks are symbol/object mismatches. Test signals are module builds of both composite objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/armada-370-db.c -->
# sources/distributed-fs/ceph-client/sound/soc/kirkwood/armada-370-db.c

## Purpose
Implements the Armada 370 Development Board ASoC machine driver, connecting the MVEBU audio controller to a CS42L51 analog codec plus SPDIF input/output codec endpoints.

## Important APIs, Types, And Functions
`a370db_hw_params()` sets the CS42L51 sysclk based on sample rate. Static DAI links define `analog`, `spdif_out`, and `spdif_in`; DAPM widgets/routes expose output and input jacks. `a370db_probe()` resolves DT phandles `marvell,audio-controller` and `marvell,audio-codec` and registers the `snd_soc_card`.

## Control Flow, State, And Persistence
The static card and DAI-link arrays are patched at probe time with OF nodes. The analog link applies `a370db_ops`; SPDIF links are direct. There is no dynamic state beyond the registered card.

## Dependencies And Integration Points
Depends on DT compatible `marvell,a370db-audio`, CS42L51 codec DAI `cs42l51-hifi`, generic SPDIF DIT/DIR DAIs, and the Kirkwood controller DAIs named `i2s` and `spdif`.

## Risks And Test Signals
Risks include duplicated `AIN1L` route that may be intended as left/right input, phandle ordering assumptions for three codecs, and fixed sysclk mapping only for 44.1/48/96 kHz families. Test signals are card registration, DAPM route visibility, analog playback/capture, SPDIF in/out, and codec sysclk programming on each supported rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/armada-370-db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-dma.c

## Purpose
Provides the PCM/DMA component for Kirkwood/MVEBU audio, programming hardware buffer registers, MBUS windows, interrupts, and PCM buffer constraints.

## Important APIs, Types, And Functions
`kirkwood_priv()` fetches controller private data from the CPU DAI. `kirkwood_dma_irq()` handles byte-count and error interrupts. `kirkwood_dma_conf_mbus_windows()` configures MBUS DRAM windows. Component ops implement `open`, `close`, `hw_params`, `prepare`, `pointer`, and `pcm_new`; exported component driver is `kirkwood_soc_component`.

## Control Flow, State, And Persistence
Open applies PCM constraints tied to burst size and requests a shared IRQ only when the first stream opens. It stores active playback/capture substreams in `kirkwood_dma_data`. `hw_params` sets MBUS windows for the DMA buffer. `prepare` writes byte interrupt count, DMA address, and size registers. Close clears substream pointers and frees the IRQ when the last stream closes.

## Dependencies And Integration Points
Depends on `struct kirkwood_dma_data` from `kirkwood.h`, MVEBU MBUS DRAM info, raw MMIO registers, ALSA PCM core, and the I2S driver that registers this component together with DAIs.

## Risks And Test Signals
Risks include MBUS window matching using coarse high address comparisons, IRQ sharing with substream pointers that must be valid for period callbacks, `NO_PERIOD_WAKEUP` interactions, and byte-count wrap handling in `pointer()`. Test signals include period interrupts for playback/capture, error interrupt logging, buffer alignment enforcement by burst size, and DMA operation on systems with multiple DRAM chip-select windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-i2s.c

## Purpose
Implements the Kirkwood/Dove/Armada I2S and SPDIF CPU DAIs, including rate-source selection, Armada 38x PLL quirks, stream format setup, and trigger control.

## Important APIs, Types, And Functions
Important routines include `armada_38x_i2s_init_quirk()`, `armada_38x_set_pll()`, `kirkwood_i2s_set_fmt()`, `kirkwood_set_dco()`, `kirkwood_set_rate()`, `kirkwood_i2s_hw_params()`, playback/capture trigger helpers, `kirkwood_i2s_init()`, and `kirkwood_i2s_dev_probe()`. It registers two DAIs, `i2s` and `spdif`, with either fixed-rate or external-clock continuous-rate capabilities.

## Control Flow, State, And Persistence
Probe maps registers, gets IRQ and clocks, applies Armada 380 named-resource quirks, chooses burst size, optionally enables an external clock, initializes cached playback/record control words, registers the shared PCM component, and places hardware into a safe state. `hw_params` sets PLL/DCO/extclk rate, word-size bits, mono behavior, and I2S/SPDIF enable bits cached in `ctl_play` and `ctl_rec`. Trigger handlers write pause/mute/enable and interrupt mask bits.

## Dependencies And Integration Points
Depends on DT compatibles `marvell,kirkwood-audio`, `marvell,dove-audio`, `marvell,armada370-audio`, and `marvell,armada-380-audio`, optional platform data, internal/ext clocks, MBUS-era MMIO layout, and `kirkwood_soc_component` from `kirkwood-dma.c`.

## Risks And Test Signals
Risks include an unbounded busy wait in DCO lock, fixed magic initialization of register `0x1200`, external-clock rate failures not propagated, Armada 38x named resource requirements, and distinct I2S/SPDIF enable masking on shared control registers. Test signals include I2S and SPDIF playback/capture, 44.1/48/96/192 kHz rates, external-clock and internal DCO paths, Armada 380 SPDIF-mode DT property, and trigger stop/start without DMA underruns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood.h -->
# sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood.h

## Purpose
Defines register offsets, bit fields, PCM limits, and shared private data for the Kirkwood/MVEBU audio controller.

## Important APIs, Types, And Functions
Macros describe DMA windows, playback/record control registers, buffer registers, DCO and clock source registers, interrupt and error registers, I2S format registers, and PCM buffer constraints. `struct kirkwood_dma_data` holds mapped register bases, clocks, cached playback/record control words, active substreams, IRQ, and burst size. It declares `kirkwood_soc_component`.

## Control Flow, State, And Persistence
No direct control flow. The structure is the persistent state shared by the I2S DAI and DMA component.

## Dependencies And Integration Points
Included by both `kirkwood-dma.c` and `kirkwood-i2s.c`. The constants encode the hardware ABI for the MVEBU audio block.

## Risks And Test Signals
Risks are incorrect register definitions, stale comments about Marvell ALSA-derived limits, and shared control bits being misused by either DAI or DMA code. Test signals include register dumps matching expected offsets and successful operation across playback/record, I2S/SPDIF, and burst sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/Kconfig

## Purpose
Defines build options for Loongson ASoC machine, I2S PCI, I2S platform, and Loongson1 AC97 drivers.

## Important APIs, Types, And Functions
`SND_SOC_LOONGSON_CARD` selects PCI or platform I2S support depending on available buses. `SND_SOC_LOONGSON_I2S_PCI` depends on PCI and selects `REGMAP_MMIO`; `SND_SOC_LOONGSON_I2S_PLATFORM` selects regmap and generic dmaengine PCM. `SND_LOONGSON1_AC97` depends on `LOONGSON1_APB_DMA` and selects AC97 codec, generic dmaengine PCM, and regmap MMIO.

## Control Flow, State, And Persistence
No runtime state. The symbols shape which Loongson audio layers are built.

## Dependencies And Integration Points
Matches the Loongson Makefile and separates LoongArch I2S support from Loongson1 APB DMA AC97 support.

## Risks And Test Signals
Risks include automatically selecting both I2S front ends when the card driver is enabled, and compile gaps for AC97 on non-Loongson1 configurations. Test signals are COMPILE_TEST/allmodconfig and real LoongArch PCI/OF build configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/Makefile

## Purpose
Builds Loongson I2S PCI, I2S platform, common I2S, AC97, and sound-card modules.

## Important APIs, Types, And Functions
The PCI composite object includes `loongson_i2s_pci.o` and `loongson_dma.o`, and additionally links the common `snd-soc-loongson-i2s.o`. The platform object includes `loongson_i2s_plat.o` and common I2S. The AC97 object is standalone. The card object builds from `loongson_card.o`.

## Control Flow, State, And Persistence
No runtime behavior; this describes module composition.

## Dependencies And Integration Points
Integrates with Loongson Kconfig symbols and ensures both PCI and platform front ends reuse `loongson_i2s.c`.

## Risks And Test Signals
Risks include double-linking the common I2S module if symbols are configured unexpectedly, and stale composite names. Test signals are separate module builds for PCI, platform, card, and AC97 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson1_ac97.c -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson1_ac97.c

## Purpose
Implements the Loongson-1 AC97 controller driver, including AC97 bus operations, DMA setup, channel/sample-format programming, and suspend/resume handling.

## Important APIs, Types, And Functions
`struct ls1x_ac97` stores register base, regmap, mapped TX/RX DMA base addresses, and DAI DMA data. AC97 bus ops are `ls1x_ac97_reset()`, `write()`, `read()`, and `init()`. DAI ops are `ls1x_ac97_dai_probe()` and `ls1x_ac97_hw_params()`. Probe maps resources including named `audio-tx` and `audio-rx`, registers dmaengine PCM and the ASoC component, and installs global AC97 ops with `snd_soc_set_ac97_ops()`.

## Control Flow, State, And Persistence
The driver uses a file-scope `ls1x_ac97` pointer for AC97 bus callbacks. Reset and codec register access poll raw interrupt bits. Init programs output and input channel FIFO thresholds and VRA bits. `hw_params` modifies DMA address flags for mono/stereo and programs 8-bit or 16-bit sample width. Suspend clears DMA/channel enable bits and asserts resume; resume re-enables channels and waits for resume completion.

## Dependencies And Integration Points
Depends on DT compatible `loongson,ls1b-ac97`, regmap MMIO, Loongson1 APB DMA resources, ASoC AC97 codec support, and generic dmaengine PCM.

## Risks And Test Signals
Risks include the global singleton pointer limiting multiple instances, returning negative error codes as unsigned codec reads on timeout, DMA address flag packing into `addr`, missing `dma_unmap_resource()` cleanup, and poll-timeout behavior during BT/sleep-like low power states. Test signals include AC97 codec enumeration, register read/write timeout logs, mono/stereo 8/16-bit playback/capture, suspend/resume, and resource leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson1_ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_card.c -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_card.c

## Purpose
Implements the Loongson generic ASoC machine driver that binds a Loongson I2S CPU DAI to a codec described by ACPI or devicetree.

## Important APIs, Types, And Functions
`struct loongson_card_data` embeds `snd_soc_card` and stores `mclk_fs`. `loongson_card_hw_params()` programs CPU and codec sysclks from sample rate times `mclk_fs`. `loongson_card_parse_acpi()` resolves `cpu` and `codec` ACPI property references and builds an I2C codec name. `loongson_card_parse_of()` reads `cpu` and `codec` child nodes with `snd_soc_of_get_dlc()`. `loongson_asoc_card_probe()` assembles and registers the card.

## Control Flow, State, And Persistence
Probe allocates card data, reads required `model` and `mclk-fs`, selects ACPI or OF parsing, patches the static DAI link, and registers the card. Runtime state is limited to `mclk_fs` and the static `codec_name` buffer.

## Dependencies And Integration Points
Depends on CPU DAI `loongson-i2s`, codec DAI names from firmware, ACPI property references or OF child nodes, ASoC card registration, and sysclk support on both CPU and codec DAIs.

## Risks And Test Signals
Risks include static global `codec_name` not supporting multiple cards, required `mclk-fs` even when zero might be desirable, ACPI physical-node deferral, and DAI format fixed to I2S inverted bit clock/non-inverted frame with codec/provider clocking. Test signals include ACPI and OF card registration, sysclk calls at several rates, deferred probe of CPU/codec, and multiple-card compile/runtime review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.c

## Purpose
Provides a custom PCM DMA component for Loongson PCI I2S, programming ring descriptors directly through Loongson DMA order registers instead of using generic dmaengine.

## Important APIs, Types, And Functions
`struct loongson_dma_desc` models hardware descriptors. `struct loongson_runtime_data` owns coherent descriptor arrays and a position descriptor. Component ops implement `open`, `close`, `hw_params`, `trigger`, `pointer`, `mmap`, and `pcm_new`. `dma_desc_save()` asks hardware to copy current descriptor state into the position descriptor. `loongson_pcm_dma_irq()` reports periods elapsed.

## Control Flow, State, And Persistence
Open applies 128-byte period/buffer alignment, allocates a descriptor page and a position descriptor, and stores CPU DAI DMA data. `hw_params` validates period division, populates a circular descriptor chain, and sets runtime buffer metadata. Trigger writes the current descriptor address plus start/stop control bits into the order register and busy-waits for start clear. Pointer asks hardware to save descriptor state and calculates frames from current source address.

## Dependencies And Integration Points
Depends on `loongson_i2s.h` DMA data, PCI front-end-provided order registers and IRQs, coherent DMA allocation, fixed PCM buffers, and ASoC component registration by `loongson_i2s_pci.c`.

## Risks And Test Signals
Risks include busy waits without timeout in DMA order operations, descriptor count limited to one page, pointer math assuming source address tracks memory position, manual mmap with `remap_pfn_range()`, and IRQ request per PCM stream. Test signals include PCI playback/capture interrupts, 64-bit and 32-bit DMA masks, pause/resume, pointer wrap, period sizes at alignment limits, and xrun behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.h -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.h

## Purpose
Declares the Loongson PCI I2S custom PCM component shared between the PCI front end and DMA implementation.

## Important APIs, Types, And Functions
The header includes ASoC and declares `extern const struct snd_soc_component_driver loongson_i2s_component`.

## Control Flow, State, And Persistence
No control flow or state exists in the header.

## Dependencies And Integration Points
Included by `loongson_i2s_pci.c` to register the component implemented in `loongson_dma.c`.

## Risks And Test Signals
Risks are declaration/definition drift and name collision with the platform front-end component driver. Test signals are PCI I2S builds and successful component registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s.c

## Purpose
Implements common Loongson I2S DAI operations shared by PCI and platform front ends.

## Important APIs, Types, And Functions
Exports `loongson_i2s_dai` and `loongson_i2s_pm`. DAI ops include `loongson_i2s_trigger()`, `loongson_i2s_hw_params()`, `loongson_i2s_set_dai_sysclk()`, `loongson_i2s_set_fmt()`, and `loongson_i2s_dai_probe()`. Helpers enable MCLK/BCLK and poll ready bits for revision 1 hardware.

## Control Flow, State, And Persistence
Trigger toggles TX/RX and DMA enable bits. `hw_params` computes BCLK and MCLK divisors differently for revision 0 and revision 1, writing `LS_I2S_CFG` and `LS_I2S_CFG1`. `set_sysclk` stores the requested system clock in `i2s->sysclk`. `set_fmt` sets I2S/right-justified format, master mode, and MCLK/BCLK enablement according to provider flags. PM suspend switches regmap to cache-only; resume marks it dirty and syncs.

## Dependencies And Integration Points
Depends on `loongson_i2s.h`, regmap, ASoC, and front-end-provided `struct loongson_i2s` with `clk_rate`, `sysclk`, DMA data, and revision ID initialized.

## Risks And Test Signals
Risks include `sysclk` being zero if the machine driver does not call `set_sysclk`, divisor overflow or bad rounding, warnings but no hard failure on ready poll timeouts, and stale bits retained in `LS_I2S_CFG` for revision 1 because the register is read/ORed. Test signals include both revisions, all supported formats/rates/channels, master/slave clock modes, suspend/resume regcache sync, and sysclk interaction with `loongson_card.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s.h

## Purpose
Defines Loongson I2S register offsets, control bits, DMA data structures, and shared private device state.

## Important APIs, Types, And Functions
Macros describe common registers (`LS_I2S_VER`, `CFG`, `CTRL`, RX/TX data), revision-specific `CFG1`, PCI DMA order registers, and I2S control bits. `struct loongson_dma_data` stores direct DMA device address, order register, and IRQ. `struct loongson_i2s` stores device, DMA data unions for dmaengine or custom DMA, regmap, MMIO base, revision, clock rate, and sysclk. It declares `loongson_i2s_pm` and `loongson_i2s_dai`.

## Control Flow, State, And Persistence
No control flow. The structures persist across probe and stream operations in both PCI and platform front ends.

## Dependencies And Integration Points
Used by `loongson_i2s.c`, `loongson_i2s_pci.c`, `loongson_i2s_plat.c`, and `loongson_dma.c`. The unions allow one common DAI to serve generic dmaengine and custom descriptor DMA paths.

## Risks And Test Signals
Risks include union misuse between front ends, register max ranges that differ by front end, and ABI dependence on specific hardware bit positions. Test signals are builds and runtime tests for both PCI and platform drivers, including DMA data correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s_pci.c -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s_pci.c

## Purpose
Implements the PCI front end for Loongson I2S hardware, registering the common I2S DAI with the custom Loongson DMA PCM component.

## Important APIs, Types, And Functions
Regmap callbacks restrict readable/writeable/volatile registers. `loongson_i2s_pci_probe()` enables the PCI device, maps BAR 0, initializes regmap, fills TX/RX `loongson_dma_data` with data register addresses and order registers, fetches named TX/RX IRQs from firmware, reads `clock-frequency`, sets a 64-bit DMA mask, optionally resets revision 1 hardware, and registers `loongson_i2s_component` plus `loongson_i2s_dai`.

## Control Flow, State, And Persistence
Probe creates and stores `struct loongson_i2s` as PCI driver data. DMA state is kept in the embedded custom DMA data unions and later consumed by `loongson_dma.c` through the common DAI probe.

## Dependencies And Integration Points
Depends on PCI device ID vendor Loongson device `0x7a27`, ACPI/fwnode named IRQs `tx` and `rx`, `clock-frequency`, regmap MMIO, the common DAI, and custom PCM component from `loongson_dma.c`.

## Risks And Test Signals
Risks include ignored return from `dma_set_mask_and_coherent()`, required named IRQs, register map not including DMA order registers, revision-dependent reset assumptions, and custom DMA descriptor behavior. Test signals are PCI probe, BAR mapping, IRQ acquisition, playback/capture with 64-bit DMA, and revision 0/1 hardware coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s_plat.c -->
# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s_plat.c

## Purpose
Implements the platform-device front end for Loongson I2S, using generic dmaengine PCM and the common Loongson I2S DAI.

## Important APIs, Types, And Functions
`loongson_pcm_open()` adjusts PCM info flags for special device-number modes and applies 128-byte constraints. `loongson_i2s_apbdma_config()` programs APB DMA channel mapping in a second MMIO resource. `loongson_i2s_plat_probe()` maps I2S registers, initializes regmap, fills dmaengine DAI DMA data, enables the clock, sets DMA mask, names the device `loongson-i2s`, registers the component and common DAI, and registers dmaengine PCM.

## Control Flow, State, And Persistence
Probe creates `struct loongson_i2s`, configures APB DMA once, and persists DMA addresses, regmap, clock rate, and device data. Runtime PCM behavior is split between the simple platform component open callback, dmaengine PCM, and common DAI ops.

## Dependencies And Integration Points
Depends on DT compatible `loongson,ls2k1000-i2s`, two MMIO resources, a clock, generic dmaengine PCM, `snd_dmaengine_pcm_prepare_slave_config`, and `loongson_i2s_dai`.

## Risks And Test Signals
Risks include APB DMA hard-coded channel assignments, `dev_set_name()` side effects on device identity, unconditional 64-bit DMA mask without error handling, and PCM device-number feature flags that need card-level coordination. Test signals include OF probe, APB DMA register programming, dmaengine playback/capture, noninterleaved/no-mmap device modes, and suspend/resume through common PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s_plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/Kconfig

## Purpose
Defines the MediaTek ASoC Kconfig hierarchy for common AFE support, SoC platform drivers, machine drivers, and BTCVSD Bluetooth SCO audio.

## Important APIs, Types, And Functions
`SND_SOC_MEDIATEK` selects `REGMAP_MMIO` and is selected by SoC-specific symbols. The file declares MT2701, MT6797, MT7986, MT8173, MT8183, MT8186, MT8188, MT8189, MT8192, MT8195, MT8365 platform support and many board-level codec combinations. `SND_SOC_MTK_BTCVSD` enables the software BTCVSD/MSBC transfer driver.

## Control Flow, State, And Persistence
No runtime state; this controls build inclusion and codec dependency selection.

## Dependencies And Integration Points
Integrates with the MediaTek Makefile and codec subsystem symbols such as MT635x PMIC codecs, HDMI codec, DMIC, BT SCO, and external I2C codec drivers.

## Risks And Test Signals
Risks include stale codec selects, incomplete COMPILE_TEST dependencies, and machine-driver symbols that select many optional codecs. Test signals are randconfig/allmodconfig builds and dependency validation for each SoC machine symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/Makefile

## Purpose
Routes MediaTek ASoC build symbols into common code and per-SoC subdirectories.

## Important APIs, Types, And Functions
Adds `common/` for `CONFIG_SND_SOC_MEDIATEK` and subdirectories for MT2701, MT6797, MT7986, MT8173, MT8183, MT8186, MT8188, MT8192, MT8195, MT8365, and MT8189.

## Control Flow, State, And Persistence
No runtime behavior; it is directory-level Kbuild metadata.

## Dependencies And Integration Points
The per-SoC Kconfig symbols decide which subdirectory Makefiles are entered.

## Risks And Test Signals
Risks are missing new SoC directories or symbol ordering drift. Test signals are per-symbol builds and allmodconfig traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/Makefile

## Purpose
Builds MediaTek shared AFE, SOF, sound-card, ADDA helper, and BTCVSD objects.

## Important APIs, Types, And Functions
`snd-soc-mtk-common-y` combines `mtk-afe-platform-driver.o`, `mtk-afe-fe-dai.o`, `mtk-dsp-sof-common.o`, `mtk-soundcard-driver.o`, and `mtk-dai-adda-common.o`. `mtk-btcvsd.o` is built for `CONFIG_SND_SOC_MTK_BTCVSD`.

## Control Flow, State, And Persistence
No runtime state. This file controls which shared helpers are linked into the common module.

## Dependencies And Integration Points
Integrates with `CONFIG_SND_SOC_MEDIATEK` and `CONFIG_SND_SOC_MTK_BTCVSD`.

## Risks And Test Signals
Risks include common helper exports being unavailable if a SoC driver selects the wrong symbol. Test signals are build/link coverage for all MediaTek ASoC users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-fe-dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-fe-dai.c

## Purpose
Provides shared MediaTek AFE front-end DAI operations and memif register programming helpers used by multiple MediaTek SoC audio drivers.

## Important APIs, Types, And Functions
Exports `mtk_afe_fe_ops`, startup/shutdown/hw_params/hw_free/prepare/trigger callbacks, dynamic IRQ allocation helpers, suspend/resume helpers, and memif setters for enable, address, channel, rate, format, and playback buffer size. Private wrappers skip negative register offsets and centralize shifted regmap updates.

## Control Flow, State, And Persistence
Startup links the ALSA substream to the memif, enables its agent, applies PCM constraints, and acquires a dynamic IRQ when needed. `hw_params` optionally requests DRAM resources, clears the DMA buffer, writes base/end/MSB addresses, channel mode, sample-rate code, and format. Trigger enables memif, programs IRQ period count and sample-rate code, enables/clears interrupts, and disables memif on stop. Suspend backs up selected registers, calls platform runtime suspend, and marks state; resume restores registers after runtime resume.

## Dependencies And Integration Points
Depends on `struct mtk_base_afe` and per-SoC memif/IRQ data, ASoC FE DAI callbacks, regmap, PM runtime, and platform callbacks such as `memif_fs`, `irq_fs`, `request_dram_resource`, and `get_memif_pbuf_size`.

## Risks And Test Signals
Risks include dynamic IRQ leaks, negative register offsets silently doing nothing, 33-bit/upper-32 address handling errors, `memset_io()` over DMA memory assumptions, unsupported formats logging but still returning success, and suspend backup allocation failures being tolerated. Test signals include concurrent FE streams, capture period constraints, DMA address above 4 GiB, S16/S24/S32 formats, suspend/resume register restore, and IRQ enable/clear traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-fe-dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-fe-dai.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-fe-dai.h

## Purpose
Declares shared MediaTek AFE FE DAI operations and memif helper APIs.

## Important APIs, Types, And Functions
The header declares the FE lifecycle callbacks, `extern const struct snd_soc_dai_ops mtk_afe_fe_ops`, dynamic IRQ acquire/release, AFE suspend/resume, and memif setters for enable, address, channel, rate, format, and pbuf size.

## Control Flow, State, And Persistence
No direct control flow or state. The declarations expose the shared implementation for SoC-specific DAI tables and platform code.

## Dependencies And Integration Points
Uses forward declarations for ASoC and MediaTek base types, allowing SoC drivers to include the header without pulling in all definitions.

## Risks And Test Signals
Risks are prototype drift and missing includes for `snd_pcm_format_t`, `dma_addr_t`, or `size_t` when include order changes. Test signals are compile coverage across all MediaTek SoC users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-fe-dai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.c

## Purpose
Provides the shared MediaTek AFE PCM platform component, including DAI aggregation, DAPM/control aggregation, PCM pointer calculation, and buffer preallocation.

## Important APIs, Types, And Functions
`mtk_afe_combine_sub_dai()` flattens registered sub-DAI driver arrays into `afe->dai_drivers`. `mtk_afe_add_sub_dai_control()` adds controls, widgets, and routes from each sub-DAI. `mtk_afe_pcm_pointer()` reads memif current/base registers and returns the PCM hardware pointer. `mtk_afe_pcm_new()` sets managed buffers. `mtk_afe_pcm_platform` is the exported component driver.

## Control Flow, State, And Persistence
Component probe initializes the regmap on the component and adds sub-DAI controls if the list is initialized. Pointer reads hardware registers per call and falls back to zero on read errors or zero addresses. Buffer sizing comes from `afe->mtk_afe_hardware` and `afe->preallocate_buffers`.

## Dependencies And Integration Points
Depends on `struct mtk_base_afe`, regmap, ASoC component/DAPM APIs, and SoC-specific setup of the `sub_dais` list and memif data.

## Risks And Test Signals
Risks include pointer underflow if current address is below base, no wrap adjustment, uninitialized `sub_dais` checks by raw list pointers, and DAPM route failures not checked. Test signals include pointer accuracy during playback/capture, sub-DAI controls/routes appearing once, and buffer preallocation size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.h

## Purpose
Declares the shared MediaTek AFE PCM platform component and helper APIs.

## Important APIs, Types, And Functions
Defines `AFE_PCM_NAME` as `"mtk-afe-pcm"`, declares `mtk_afe_pcm_platform`, and exposes `mtk_afe_pcm_pointer()`, `mtk_afe_pcm_new()`, `mtk_afe_combine_sub_dai()`, and `mtk_afe_add_sub_dai_control()`.

## Control Flow, State, And Persistence
No control flow or state. It is the contract used by SoC-specific platform drivers and FE DAI helpers.

## Dependencies And Integration Points
Uses forward declarations for ASoC and MediaTek base structures. `AFE_PCM_NAME` is also used for runtime component lookup by FE helpers.

## Risks And Test Signals
Risks are string-name mismatch with component registration and prototype drift. Test signals are SoC driver compile/link coverage and successful `snd_soc_rtdcom_lookup()` for `AFE_PCM_NAME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-base-afe.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-base-afe.h

## Purpose
Defines the core MediaTek AFE data model shared by SoC platform drivers, FE DAI helpers, IRQ logic, memif programming, sub-DAI aggregation, and secure monitor operations.

## Important APIs, Types, And Functions
Defines `MTK_STREAM_NUM`, `MTK_SIP_AUDIO_CONTROL`, `enum mtk_audio_smc_call_op`, `struct mtk_base_memif_data`, `struct mtk_base_irq_data`, `struct mtk_base_afe`, `struct mtk_base_afe_memif`, `struct mtk_base_afe_irq`, and `struct mtk_base_afe_dai`.

## Control Flow, State, And Persistence
The header has no execution, but its structs are the persistent runtime state for MediaTek AFE devices. `mtk_base_afe` owns MMIO/regmap, runtime PM callbacks, register backup arrays, memif and IRQ arrays, sub-DAI lists, hardware constraints, rate conversion callbacks, DRAM resource callbacks, and private SoC data.

## Dependencies And Integration Points
Depends on MediaTek SIP service definitions and ASoC/PCM types through include order. It is consumed by common helpers and SoC-specific drivers that populate the register maps and callback tables.

## Risks And Test Signals
Risks include negative register sentinel handling being implicit, many SoC-populated fields without compile-time validation, callback nullability, and secure monitor operation enum drift. Test signals are per-SoC initialization audits, runtime PM suspend/resume, dynamic IRQ allocation, 64-bit DMA address fields, and static checks for uninitialized memif/IRQ fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-base-afe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-btcvsd.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-btcvsd.c

## Purpose
Implements MediaTek BTCVSD/MSBC ALSA PCM support, bridging PCM read/write operations to Bluetooth firmware SRAM packet buffers for SCO audio.

## Important APIs, Types, And Functions
Core state is `struct mtk_btcvsd_snd` with TX/RX stream objects, IRQ, infra regmap, BT packet/control register pointers, SRAM bases, locks, wait queues, and packet buffers. Important functions include state control `mtk_btcvsd_snd_set_state()`, transfer helpers, SRAM read/write functions, IRQ handler `mtk_btcvsd_snd_irq_handler()`, wait helper `wait_for_bt_irq()`, PCM copy/read/write/pointer/open/close/hw_params/hw_free/prepare/trigger callbacks, kcontrols for band/loopback/mute/IRQ/timeout/timestamps, and probe/remove.

## Control Flow, State, And Persistence
Probe allocates TX/RX streams, initializes locks and queues, requests the IRQ, maps BT packet and SRAM regions with `of_iomap()`, reads infra and offset properties, derives packet register pointers, disables IRQs while idle, and registers a component without DAIs. Playback writes packetized user data into a circular TX buffer; interrupts move packets to BT SRAM when firmware requests them. Capture interrupts read BT SRAM into a circular RX buffer, and userspace reads from it. State transitions enable or disable IRQs depending on TX/RX activity.

## Dependencies And Integration Points
Depends on DT compatible `mediatek,mtk-btcvsd-snd`, `mediatek,infracfg`, `mediatek,offset`, low-trigger IRQ, BT firmware SRAM layout, ASoC component PCM callbacks, and ALSA controls.

## Risks And Test Signals
Risks include direct `u32 *` MMIO access instead of readl/writel, pointer casts to SRAM addresses, packet counter wrap arithmetic, unbounded `num_valid_addr` growth versus fixed 20-entry array, wait timeouts returning partial transfers, lock coverage around shared counters, and manual iounmap paths. Test signals include NB/WB SCO loopback, TX mute cleaning, RX overflow/TX underflow logs, timeout controls, timestamp controls, suspend-like BT sleep returning `0xdeadfeed`, and stress with concurrent playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-btcvsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.c

## Purpose
Provides common MediaTek ADDA downlink and uplink sample-rate-to-register-code conversion helpers.

## Important APIs, Types, And Functions
Exports `mtk_adda_dl_rate_transform()` and `mtk_adda_ul_rate_transform()`. The downlink helper maps 8 kHz through 192 kHz including 11.025/22.05/44.1 kHz rates. The uplink helper maps 8/16/32/48/96/192 kHz. Unknown rates log and fall back to 48 kHz codes.

## Control Flow, State, And Persistence
Both functions are stateless switch statements. They use `afe->dev` only for logging invalid rates.

## Dependencies And Integration Points
Depends on `mtk-base-afe.h` for the device pointer and `mtk-dai-adda-common.h` enums. SoC ADDA DAI drivers call these when programming codec/AFE rate fields.

## Risks And Test Signals
Risks include silent 48 kHz fallback after an invalid-rate log and mismatched enum values against SoC register definitions. Test signals are rate-programming tests for every supported rate and negative tests for unsupported rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.h

## Purpose
Declares MediaTek ADDA rate-code enums and conversion helpers.

## Important APIs, Types, And Functions
Defines `enum adda_input_mode_rate`, `enum adda_voice_mode_rate`, and `enum adda_rxif_delay_data`, plus prototypes for `mtk_adda_dl_rate_transform()` and `mtk_adda_ul_rate_transform()`.

## Control Flow, State, And Persistence
No control flow or state. The enum constants are shared ABI between common helpers and SoC-specific register programming.

## Dependencies And Integration Points
Forward-declares `struct mtk_base_afe` and is included by ADDA DAI implementations.

## Risks And Test Signals
Risks are enum value drift relative to hardware manuals and duplicate delay enum values that must be intentional for SoC compatibility. Test signals are compile coverage and register-value validation for ADDA paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.c

## Purpose
Provides MediaTek common helpers for integrating ASoC machine drivers with SOF topology back-end links, fixup callbacks, DAPM route insertion, and devicetree-selected DAI link lists.

## Important APIs, Types, And Functions
Exports `mtk_sof_dai_link_fixup()`, `mtk_sof_card_probe()`, `mtk_sof_card_late_probe()`, and `mtk_sof_dailink_parse_of()`. Private helpers find topology BEs through DPCM relationships and choose the correct stored or SOF-provided `be_hw_params_fixup`.

## Control Flow, State, And Persistence
Card probe initializes a list and gives unnamed BE streams names. Late probe finds the SOF component, backs up existing BE fixups into `soc_card_data->sof_dai_link_list`, replaces BE fixups with a wrapper, adds DAPM routes between normal widgets and SOF DMA widgets, and installs the SOF component fixup on SOF BE links. The parse helper copies requested predeclared DAI links into a device-managed array based on `mediatek,dai-link`.

## Dependencies And Integration Points
Depends on `mtk_soc_card_data`, `mtk_sof_priv`, ASoC DPCM traversal, SOF component name `sof-audio-component`, card prelinks/rtds, and DT properties for DAI-link selection.

## Risks And Test Signals
Risks include name-based link matching, route insertion without duplicate handling, dynamic DAI link arrays copied by value, fallback behavior when no SOF component is present, and fixup wrapping order. Test signals include cards with and without ADSP nodes, playback/capture through SOF DMA, BE hw_params fixup propagation, DAPM route graph inspection, and invalid `mediatek,dai-link` lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.h

## Purpose
Declares MediaTek SOF integration structures and helper functions for machine drivers.

## Important APIs, Types, And Functions
`struct sof_conn_stream` maps normal links to SOF links, SOF DMA widget names, and stream direction. `struct mtk_dai_link` stores saved BE fixups in a list. `struct mtk_sof_priv` supplies connection streams and optional SOF fixup callback. The header declares card probe, late probe, fixup, and DT DAI-link parse helpers.

## Control Flow, State, And Persistence
No direct control flow. The structures become persistent card-private metadata while SOF routes and fixups are active.

## Dependencies And Integration Points
Includes ASoC and is used by MediaTek machine drivers plus `mtk-soundcard-driver.c`.

## Risks And Test Signals
Risks include name-string ABI dependence and list ownership assumptions for saved fixups. Test signals are compile coverage and SOF/non-SOF machine probe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soc-card.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soc-card.h

## Purpose
Defines shared MediaTek machine-card private data used by common sound-card and SOF helper code.

## Important APIs, Types, And Functions
`struct mtk_soc_card_data` stores optional SOF private data, a list of saved SOF DAI-link fixups, platform card data, optional accessory-detect component, and machine-private data.

## Control Flow, State, And Persistence
No control flow. Instances are allocated during machine-driver probe and attached to `snd_soc_card` drvdata.

## Dependencies And Integration Points
Forward-declares `mtk_platform_card_data` and `mtk_sof_priv`. Used by `mtk-soundcard-driver.c` and `mtk-dsp-sof-common.c`.

## Risks And Test Signals
Risks are uninitialized list fields when SOF helpers are skipped and lifetime coupling between card drvdata and devm allocations. Test signals are probe paths with and without SOF and accessory detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soc-card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.c

## Purpose
Provides common MediaTek machine-driver probe and DAI-link parsing logic, including codec binding, DAI format parsing, PCM constraints, accessory-detect lookup, platform/ADSP node assignment, and SOF setup.

## Important APIs, Types, And Functions
Exports `parse_dai_link_info()`, `clean_card_reference()`, `mtk_soundcard_startup()`, `mtk_soundcard_common_playback_ops`, `mtk_soundcard_common_capture_ops`, and `mtk_soundcard_common_probe()`. Private helpers parse codec child nodes and DAI formats including `mediatek,clk-provider`.

## Control Flow, State, And Persistence
Common probe obtains platform data from match data, sets the card device/name, chooses legacy or audio-routing mode, allocates `mtk_soc_card_data` and jack storage, optionally locates an accdet component, resolves `mediatek,platform`, optionally parses ADSP/SOF configuration and selected DAI links, assigns platform nodes to links, parses per-link codec/format data, invokes optional SoC-specific probe, attaches card drvdata, registers the card, and restores DAI arrays on errors.

## Dependencies And Integration Points
Depends on MediaTek machine pdata definitions from `mtk-soundcard-driver.h`, OF graph/child-node conventions, ASoC codec parsing, SOF helpers, and optional accessory-detect components referenced by `mediatek,accdet`.

## Risks And Test Signals
Risks include static card templates being mutated and restored on error, codec references cleaned immediately after card registration, legacy probe dependence on SoC callbacks, `unlikely(!mpc)` on an address that is normally non-null, name-based DAI-link lookup, and platform-node ownership. Test signals include DTs with and without `audio-routing`, codec-less dummy links, multiple `mediatek,dai-link` selections, ADSP/SOF and non-SOF cards, accdet phandle resolution, and startup rate/channel constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.c -->
