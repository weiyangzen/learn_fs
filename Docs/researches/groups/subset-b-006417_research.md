# Research: subset-b-006417

This grouped report covers AMD Vangogh/Yellow Carp, Apple MCA, and Atmel ASoC source files under `sources/distributed-fs/ceph-client/sound/soc/`. Each section is source-tree-aligned and wrapped for reconciliation into the matching per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/vg_chip_offset_byte.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/vg_chip_offset_byte.h

## Purpose
This header is a register-offset catalog for AMD ACP 5.x Vangogh audio hardware. It has no executable code; it gives symbolic byte offsets for ACP DMA channels, AXI-to-AXI ATU page tables, clock/reset, miscellaneous interrupt/error registers, power-gating/AON controls, scratch SRAM/PTE storage, audio ring buffers, I2S/TDM, Bluetooth TDM, and headset TDM blocks.

## Important APIs, Types, And Functions
The public surface is the set of `#define` register names such as `ACP_DMA_CNTL_0`, `ACP_SOFT_RESET`, `ACP_EXTERNAL_INTR_CNTL`, `ACP_SCRATCH_REG_0`, `ACP_I2S_RX_RINGBUFADDR`, and `ACP_I2STDM_IER`. Consumers include MMIO helpers in AMD ACP drivers that add these offsets to an ACP base address. There are no structs, functions, module hooks, or inline helpers here.

## Control Flow
None. The include guard `_acp_ip_OFFSET_HEADER` prevents duplicate inclusion.

## State And Persistence
The file describes volatile hardware state only. Persistence is external in ACP registers, DMA descriptors, scratch/PTE SRAM, interrupt status bits, and ring-buffer position counters.

## Dependencies And Integration Points
It integrates with AMD SoC audio drivers that need ACP 5.x register offsets. Its naming closely mirrors `acp6x_chip_offset_byte.h` but lacks newer ACP6x WOV/P1 ranges. Correctness depends on the register map matching the SoC generation and the driver's base-address arithmetic.

## Risks And Test Signals
The main risk is silent hardware misprogramming from stale or wrong offsets. Test signals are boot/probe success on Vangogh ACP hardware, working I2S/TDM DMA, sane ring-buffer counters, and absence of ACP interrupt/error-status storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/vg_chip_offset_byte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/amd/yc/Makefile

## Purpose
This Kbuild file wires the AMD Yellow Carp ASoC objects into kernel configuration symbols. It builds the PCI ACP parent driver, the PDM DMA component, and the machine card driver.

## Important APIs, Types, And Functions
The important build targets are `snd-pci-acp6x-y := pci-acp6x.o`, `snd-acp6x-pdm-dma-y := acp6x-pdm-dma.o`, and `snd-soc-acp6x-mach-y := acp6x-mach.o`. Objects are selected by `CONFIG_SND_SOC_AMD_ACP6x` and `CONFIG_SND_SOC_AMD_YC_MACH`.

## Control Flow
Build-time only. Enabling `CONFIG_SND_SOC_AMD_ACP6x` includes both the PCI parent and PDM DMA platform component; enabling `CONFIG_SND_SOC_AMD_YC_MACH` includes the DMIC machine driver.

## State And Persistence
No runtime state. It controls which modules or built-in objects exist.

## Dependencies And Integration Points
The Makefile depends on Kconfig symbols defined elsewhere in the AMD ASoC tree. Runtime integration assumes `pci-acp6x.c` registers platform devices named `acp_yc_pdm_dma`, `dmic-codec`, and `acp_yc_mach`, matching the component names used by the machine driver.

## Risks And Test Signals
Misconfigured symbols can build a parent without a machine card, or vice versa. Test signals are successful `make sound/soc/amd/yc/`, module autoload for the AMD ACP PCI ID, and creation of the expected ASoC card when hardware/firmware gates allow it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-mach.c

## Purpose
This is the AMD Yellow Carp machine driver for systems using the ACP6x PDM digital microphone path. It registers a single capture-only ASoC card named `acp6x` that connects the CPU DAI `acp_yc_pdm_dma.0`, the generic `dmic-codec.0` codec DAI `dmic-hifi`, and the ACP PDM platform component.

## Important APIs, Types, And Functions
Key data is `acp6x_dai_pdm[]`, `acp6x_card`, and the large `yc_acp_quirk_table[]`. `acp6x_probe()` is the main entry point. It checks ACPI `AcpDmicConnected`, evaluates `_WOV`, applies DMI overrides via `dmi_first_match()`, attaches the card to the platform device, and calls `devm_snd_soc_register_card()`. The platform driver is registered with `module_platform_driver()` and has alias `platform:acp_yc_mach`.

## Control Flow
Probe first initializes local defaults, reads the parent ACPI companion property, then evaluates `_WOV`. `_WOV == 0` rejects the device with `-ENODEV`; ACPI read failure falls through to DMI matching. If ACPI explicitly enables a DMIC, probe stores `&acp6x_card` as driver data. A DMI match can also store the card. If neither path supplies a card, probe returns `-ENODEV`; otherwise it registers the card.

## State And Persistence
The driver has static card and DAI-link objects. Per-device state is minimal; `machine` is currently `NULL` and stored as card driver data. Long-lived activation state lives in ASoC core objects after card registration.

## Dependencies And Integration Points
It depends on the `acp_yc_pdm_dma.0` platform component from `acp6x-pdm-dma.c`, the `dmic-codec` platform device from `pci-acp6x.c`, ACPI firmware properties/methods, and DMI board identifiers. It also uses common ASoC PM ops.

## Risks And Test Signals
The DMI table is large and contains duplicate entries, so regression risk is mostly false positive or false negative enablement on laptops. Firmware behavior around `_WOV` and `AcpDmicConnected` is a compatibility risk. Test signals include card creation only on intended machines, `arecord -l` exposing DMIC capture, suspend/resume retaining capture, and no card registration on systems without a supported DMIC path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-mach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-pdm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-pdm-dma.c

## Purpose
This file implements the Yellow Carp ACP6x PDM DMA ASoC component and CPU DAI for two-channel, 48 kHz, 32-bit digital microphone capture. It programs ACP WOV/PDM registers, maps ALSA buffers through the ACP ATU/PTE scratch area, handles position reporting, and participates in runtime/system PM.

## Important APIs, Types, And Functions
The hardware contract is `acp6x_pdm_hardware_capture`. Core helpers include `acp6x_init_pdm_ring_buffer()`, `acp6x_enable_pdm_clock()`, `acp6x_start_pdm_dma()`, `acp6x_stop_pdm_dma()`, `acp6x_config_dma()`, and `acp6x_pdm_get_byte_count()`. ASoC component callbacks are `open`, `close`, `hw_params`, `pointer`, and `pcm_new`; the DAI operation is `acp6x_pdm_dai_trigger()`. Probe maps MMIO and registers `acp6x_pdm_component` plus `acp6x_pdm_dai_driver`. Module parameter `pdm_gain` controls `ACP_WOV_GAIN_CONTROL`.

## Control Flow
Probe maps the parent-provided ACP memory resource, stores `pdm_dev_data`, registers the component, then enables autosuspend. On PCM open it allocates a `pdm_stream_instance`, constrains periods, enables PDM interrupts, and stores the capture substream. `hw_params` configures page-table entries and ring-buffer/watermark registers. Trigger start sets channel count and decimation, snapshots the byte counter, and starts PDM DMA if not already active. Trigger stop stops DMA and flushes the FIFO. Pointer reads the hardware linear position counter and wraps it by buffer size.

## State And Persistence
Persistent driver state is `pdm_dev_data` with MMIO base and active capture stream. Per-stream state is allocated in `runtime->private_data` and stores page count, DMA address, starting byte counter, and MMIO base. Hardware state spans ACP WOV enable bits, ring-buffer registers, PDM clock/gain, ATU page tables in scratch registers, and interrupt masks.

## Dependencies And Integration Points
It depends on `acp6x.h` constants and MMIO helpers, platform resources from `pci-acp6x.c`, the PCI parent IRQ path that calls `snd_pcm_period_elapsed()`, ASoC component registration, and managed DMA buffers from the parent device.

## Risks And Test Signals
Risk areas include timeout polling, pointer wrap arithmetic, missing `kfree()` in close for `pdm_stream_instance`, global `pdm_gain`, and resume reprogramming while a stream is active. Test signals are successful capture at 48 kHz S32_LE stereo, stable period interrupts, correct `aplay/arecord` pointer movement, clean runtime suspend/resume, and no DMA timeouts or ACP error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-pdm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x.h

## Purpose
This header centralizes Yellow Carp ACP6x constants, data structures, and MMIO helpers used by the PCI parent, PDM DMA component, and machine support. It imports the ACP6x register-offset header and defines hardware limits, mode IDs, power/reset masks, PDM parameters, buffer sizes, and runtime PM delay.

## Important APIs, Types, And Functions
Important types are `struct pdm_dev_data`, `struct pdm_stream_instance`, and `union acp_pdm_dma_count`. Inline helpers `acp6x_readl()` and `acp6x_writel()` convert physical ACP register offsets into offsets from the mapped base by subtracting `ACP6x_PHY_BASE_ADDRESS`. It declares `snd_amd_acp_find_config(struct pci_dev *pci)`.

## Control Flow
The header has no control flow besides inline MMIO reads/writes. Its constants drive polling loops, PDM trigger decisions, and DMA buffer constraints in other files.

## State And Persistence
State definitions describe both software state (`capture_stream`, per-stream `bytescount`, DMA page count) and hardware state (power-gating status, interrupt bits, WOV/PDM enable bits). Actual persistence is owned by callers and hardware registers.

## Dependencies And Integration Points
It depends on `acp6x_chip_offset_byte.h`, Linux MMIO accessors, DMA address types, and PCI type declarations. It is shared between `pci-acp6x.c` and `acp6x-pdm-dma.c`, so register-base arithmetic changes affect both.

## Risks And Test Signals
The most important risk is the nonstandard `base_addr - ACP6x_PHY_BASE_ADDRESS` addressing contract: callers must pass `mapped_base + physical_offset`, not a normal offset. Test signals are correct register reads during PCI probe, successful power/reset sequencing, and DMA component operation without bogus MMIO accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x_chip_offset_byte.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x_chip_offset_byte.h

## Purpose
This header is the ACP 6.x Yellow Carp register-offset map. It expands the ACP 5.x-style map with ACP6x-specific P1 misc/audio-buffer ranges and WOV PDM registers used by the PDM DMA driver.

## Important APIs, Types, And Functions
Its exported surface is symbolic `#define` offsets: DMA channel registers, ATU groups 1-16, clock/reset and power-gating registers, AON pin/wake registers, P1 interrupt/error/position registers, classic audio buffers, I2S/Bluetooth/headset TDM registers, WOV PDM registers (`ACP_WOV_PDM_ENABLE`, `ACP_WOV_RX_RINGBUFSIZE`, `ACP_WOV_CLK_CTRL`), P1 audio buffers, and scratch registers.

## Control Flow
None. The include guard `_acp6x_OFFSET_HEADER` prevents duplicate definitions.

## State And Persistence
The file identifies volatile MMIO state. WOV registers hold active PDM DMA enablement, ring-buffer configuration, linear position counters, FIFO flush state, channel count, decimation, clock/gain controls, and error status.

## Dependencies And Integration Points
It is included by `acp6x.h` and indirectly used by both the PCI and PDM DMA drivers. Integration correctness depends on the ACP6x physical register window matching `ACP6x_REG_START`/`ACP6x_REG_END` and the subtract-base helper in `acp6x.h`.

## Risks And Test Signals
Wrong offsets can cause hard-to-debug audio or interrupt failures. Test signals include successful ACP reset/power transitions, correct PDM DMA period interrupts, stable capture position counters, and no writes outside the mapped ACP resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x_chip_offset_byte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/pci-acp6x.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/yc/pci-acp6x.c

## Purpose
This is the AMD Yellow Carp ACP PCI parent driver. It owns PCI enablement, ACP power/reset/interrupt setup, platform-device creation for PDM DMA, DMIC codec, and machine driver, IRQ fanout to ALSA period notifications, and ACP runtime/system PM.

## Important APIs, Types, And Functions
`struct acp6x_dev_data` stores MMIO base, resource, audio mode, and child platform devices. Important helpers are `acp6x_power_on()`, `acp6x_reset()`, `acp6x_enable_interrupts()`, `acp6x_disable_interrupts()`, `acp6x_init()`, `acp6x_deinit()`, and `acp6x_irq_handler()`. `snd_acp6x_probe()` is the PCI probe path; `snd_acp6x_suspend()`, `snd_acp6x_resume()`, and `snd_acp6x_remove()` manage lifecycle. The PCI ID table matches AMD device `0x15E2` with multimedia-other class.

## Control Flow
Probe first calls external `snd_amd_acp_find_config()` and rejects handled configurations. It filters PCI revisions, enables the PCI device, requests BAR regions, maps BAR0, initializes ACP power/reset/clock/interrupts, then reads `ACP_PIN_CONFIG`. For reserved/non-I2S configurations it creates three child platform devices: `acp_yc_pdm_dma`, `dmic-codec`, and `acp_yc_mach`. It then requests the shared PCI IRQ and enables runtime PM. The IRQ handler checks `ACP_EXTERNAL_INTR_STAT` for `PDM_DMA_STAT`, clears it, and calls `snd_pcm_period_elapsed()` on the child PDM capture stream.

## State And Persistence
Software state persists in `acp6x_dev_data` and registered child devices. Hardware state includes ACP power-gating, reset, clock mux, external interrupt masks/status, pin configuration, and PDM DMA interrupt state. PM suspend deinitializes ACP; resume reinitializes it.

## Dependencies And Integration Points
It depends on PCI core, platform-device core, ASoC PDM and machine drivers, generic `dmic-codec`, `acp6x.h`, and the external AMD ACP configuration detector. It is the integration point that supplies the memory resource consumed by `acp6x-pdm-dma.c`.

## Risks And Test Signals
Risk areas include revision/pin-config gating, shared IRQ handling assuming `pdev[0]` exists when interrupts fire, and cleanup ordering across registered children. Test signals are correct child platform-device registration, valid IRQ period callbacks during capture, runtime suspend/resume survival, and clean removal without leaked children or enabled ACP interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/yc/pci-acp6x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/apple/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/apple/Kconfig

## Purpose
This Kconfig fragment exposes the Apple Silicon MCA ASoC platform driver under the `Apple` menu.

## Important APIs, Types, And Functions
The key symbol is `SND_SOC_APPLE_MCA`, a tristate option labeled "Apple Silicon MCA driver". It depends on `ARCH_APPLE || COMPILE_TEST` and selects `SND_DMAENGINE_PCM`.

## Control Flow
Build-time only. Selecting the symbol permits the `apple/mca.c` driver to be built as built-in or module.

## State And Persistence
No runtime state. It influences kernel configuration and build artifacts.

## Dependencies And Integration Points
It integrates with ASoC Kconfig and the generic DMAengine PCM layer. Device matching at runtime is handled by the OF match table in `mca.c`.

## Risks And Test Signals
The risk is dependency under-selection if MCA requires additional Apple platform services not expressed here. Test signals include successful compile under `ARCH_APPLE` and `COMPILE_TEST`, and module availability when devicetree advertises `apple,mca`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/apple/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/apple/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/apple/Makefile

## Purpose
This Makefile maps `CONFIG_SND_SOC_APPLE_MCA` to the Apple MCA driver object.

## Important APIs, Types, And Functions
`snd-soc-apple-mca-y := mca.o` names the composite object, and `obj-$(CONFIG_SND_SOC_APPLE_MCA) += snd-soc-apple-mca.o` attaches it to the build.

## Control Flow
Build-time only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It depends on the Kconfig symbol in the same directory. Runtime behavior is entirely in `mca.c`.

## Risks And Test Signals
Test with `make sound/soc/apple/` or full kernel builds for built-in and module configurations. A mismatch between object name and module alias would prevent loading, but this file is straightforward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/apple/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/apple/mca.c -->
# sources/distributed-fs/ceph-client/sound/soc/apple/mca.c

## Purpose
This is the Apple Silicon MCA ASoC platform driver. MCA hardware is organized as clusters containing clock/sync generation, SERDES units, DMA adapters, and I2S ports. The driver models cluster internals as front-end DAIs and physical I2S ports as back-end DAIs, letting machine-driver DAPM routes dynamically connect FEs to BEs through ASoC DPCM.

## Important APIs, Types, And Functions
Core state is `struct mca_data` and `struct mca_cluster`. Important DAI helpers include `mca_fe_startup()`, `mca_fe_set_tdm_slot()`, `mca_fe_set_fmt()`, `mca_fe_hw_params()`, `mca_fe_trigger()`, `mca_be_startup()`, `mca_be_prepare()`, `mca_be_hw_free()`, and `mca_be_shutdown()`. PCM component callbacks wrap DMAengine via `mca_pcm_open()`, `mca_hw_params()`, `mca_trigger()`, `mca_pointer()`, `mca_pcm_new()`, and `mca_pcm_free()`. Probe dynamically allocates `2 * nclusters` DAI drivers from MMIO resource size, attaches power domains, resets hardware, obtains per-cluster clocks, and registers the component.

## Control Flow
Probe maps cluster and switch resources, counts clusters, attaches global and per-cluster power domains, resets the block, and creates FE/BE DAI descriptors. FE hw_params computes/refines TDM slots, configures SERDES and DMA adapter padding/channel fields, and sets clock rates when the FE clock is idle. BE startup enforces one FE driving a port, programs port clock/data muxes, and records `port_driver`. BE prepare enables the driving FE's clock/power domain before codec unmute or DAPM power-up. PCM trigger calls `mca_fe_early_trigger()` before DMAengine trigger to reset/resync SERDES, and FE trigger then enables/disables SERDES.

## State And Persistence
State is per device and per cluster: port routing, started stream directions, clocks in use, power-domain links, TDM masks/widths, BCLK ratio, and DMA channels. Hardware state includes SERDES configs, slot masks, syncgen periods, MCLK settings, port muxes, and DMA adapter registers. Remove unregisters the component, releases clocks/domains, deletes links, and rearms reset.

## Dependencies And Integration Points
The driver depends on OF resources, OF DMA channel names (`tx%da`, `rx%db` when RXB capture is enabled), clocks indexed by cluster, power domains, reset controls, regmap-like raw MMIO, ASoC DPCM, and DMAengine PCM. Machine drivers provide routes and DAI references to backend ports.

## Risks And Test Signals
Risk areas include dynamic FE/BE ID mapping, one-FE-per-BE enforcement, clock/power ordering, undocumented SERDES bits, RXB-vs-RXA compile-time choice, and DMA channel naming. Test signals are successful probe on Apple DTs, DPCM routing between expected FE/BE pairs, playback/capture in I2S and TDM slot configurations, clean underrun-free DMAengine operation, and suspend/remove paths releasing power-domain links and DMA channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/apple/mca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/Kconfig

## Purpose
This Kconfig fragment describes Atmel/Microchip ASoC platform, PCM transport, and machine-driver options.

## Important APIs, Types, And Functions
Transport symbols include `SND_ATMEL_SOC_PDC`, `SND_ATMEL_SOC_DMA`, `SND_ATMEL_SOC_SSC`, `SND_ATMEL_SOC_SSC_PDC`, and `SND_ATMEL_SOC_SSC_DMA`. Platform/machine symbols include `SND_ATMEL_SOC_CLASSD`, `SND_ATMEL_SOC_PDMIC`, `SND_ATMEL_SOC_I2S`, `SND_ATMEL_SOC_WM8904`, legacy WM8731 boards, TSE850, Mikroe PROTO, and Microchip I2S MCC/SPDIF/PDMC drivers.

## Control Flow
Build-time only. The symbols select lower-level PCM transports and codec dependencies so machine drivers build with their CPU DAI and codec support.

## State And Persistence
No runtime state. It determines which drivers are compiled.

## Dependencies And Integration Points
It depends on `HAS_IOMEM`, `ARCH_AT91 || COMPILE_TEST`, `OF`, `ATMEL_SSC`, `I2C`, `COMMON_CLK`, and codec symbols. It integrates with the Atmel Makefile for object selection.

## Risks And Test Signals
Risks are missing selects that lead to link failures or runtime absent components. Test signals are allmodconfig/COMPILE_TEST coverage, DT board configs selecting the expected transport, and no duplicate/unsatisfied symbol dependency warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/Makefile

## Purpose
This Kbuild file maps Atmel/Microchip ASoC Kconfig symbols to platform, PCM, and machine-driver objects.

## Important APIs, Types, And Functions
It defines object groups for PDC PCM, DMA PCM, SSC DAI, Atmel I2S, Microchip I2S MCC/SPDIF/PDMC, and machine drivers such as WM8904, CLASSD, PDMIC, TSE850, and Mikroe PROTO. Conditional `ifdef CONFIG_SND_ATMEL_SOC_PDC/DMA` ensures SSC users get built-in-compatible PCM support.

## Control Flow
Build-time only. `obj-$(CONFIG_...)` lines include drivers according to selected symbols.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It depends on the Kconfig fragment and source object names in the folder. The PDC/DMA built-in handling is an integration point for SSC users because SSC can select both transports but choose one at runtime from `ssc->pdata->use_dma`.

## Risks And Test Signals
Risk is build/link failure if Kconfig enables an object without its transport dependencies. Test signals include Atmel/Microchip `allyesconfig` and mixed built-in/module builds for SSC PDC and DMA variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.c

## Purpose
This driver exposes the Atmel SAMA5D2 CLASSD amplifier as both an ASoC CPU DAI/component and a simple self-contained sound card using the dummy codec. It supports playback through DMAengine to the CLASSD transmit holding register and configures PWM, non-overlap timing, sample-rate clocks, mute, volume, mono, swap, deemphasis, and EQ controls.

## Important APIs, Types, And Functions
State is `struct atmel_classd` and DT platform data `struct atmel_classd_pdata`. Important callbacks are `atmel_classd_cpu_dai_startup()`, `atmel_classd_platform_configure_dma()`, `atmel_classd_component_probe()`, `atmel_classd_cpu_dai_hw_params()`, `atmel_classd_cpu_dai_prepare()`, `atmel_classd_cpu_dai_trigger()`, and `atmel_classd_probe()`. The component registers ALSA controls with TLV volume and enum EQ/mono options.

## Control Flow
Probe reads DT properties (`atmel,pwm-type`, `atmel,non-overlap-time`, `atmel,model`), maps MMIO into a cached regmap, gets `pclk`/`gclk`, registers the CPU DAI and DMAengine PCM, builds a one-link card, and registers it. Startup clears `CLASSD_THR` and enables clocks. `hw_params` selects the closest supported sample-rate entry, reprograms `gclk`, and updates `CLASSD_INTPMR`. Trigger enables/disables left/right output bits. Shutdown disables `gclk`.

## State And Persistence
Software state stores regmap, physical base for DMA, clocks, IRQ number, device pointer, and pdata. Hardware state includes CLASSD mode, interpolation/sample-rate register, transmit holding register, mute/output enable bits, and cached defaults. `regcache_sync()` restores cached values on resume.

## Dependencies And Integration Points
It depends on OF, clocks named `pclk` and `gclk`, regmap MMIO, generic DMAengine PCM, dummy codec, ASoC card registration, and register definitions in `atmel-classd.h`.

## Risks And Test Signals
Risk areas include clock-rate selection by nearest match, only accepting 16-bit physical audio, no explicit IRQ use despite requesting an IRQ number, and DT property validation. Test signals are successful card registration, playback at all supported rates, correct DMA slave address/width for mono vs stereo, controls changing registers, and resume restoring regmap state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.h -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.h

## Purpose
This header defines the SAMA5D2 CLASSD amplifier register map and bit fields used by `atmel-classd.c`.

## Important APIs, Types, And Functions
It exports offsets for `CLASSD_CR`, `CLASSD_MR`, `CLASSD_INTPMR`, `CLASSD_THR`, interrupt registers, and write-protect register. It also defines masks/shifts/values for left/right enable and mute, PWM type, non-overlap timing, attenuation, DSP clock family, deemphasis, swap, frame/sample-rate selection, EQ configuration, mono mode, and reset.

## Control Flow
None.

## State And Persistence
The definitions address volatile MMIO state. `CLASSD_INTPMR` has a default in the driver's regmap cache, so its fields persist across suspend through regcache.

## Dependencies And Integration Points
The header is tightly coupled to `atmel-classd.c` and the hardware manual. It uses plain macros rather than `GENMASK`, so callers must combine masks and shifts carefully.

## Risks And Test Signals
Wrong masks or shifts can invert channels, leave outputs muted, or select bad clock/sample-rate/EQ values. Test signals are register dumps matching expected mode fields after probe and `hw_params`, audible playback, and ALSA controls mapping to documented dB/EQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-i2s.c

## Purpose
This is the Atmel SAMA5D2 I2S controller ASoC CPU DAI driver. It supports playback and capture through DMAengine PCM, handles I2S master/slave clocking, configures sample formats and mono mode, reports underrun/overrun interrupts, and registers DMA addresses for transmit/receive holding registers.

## Important APIs, Types, And Functions
Core state is `struct atmel_i2s_dev`, `struct atmel_i2s_gck_param`, and optional capability hooks in `struct atmel_i2s_caps`. Important functions are `atmel_i2s_interrupt()`, `atmel_i2s_set_dai_fmt()`, `atmel_i2s_get_gck_param()`, `atmel_i2s_hw_params()`, `atmel_i2s_switch_mck_generator()`, `atmel_i2s_trigger()`, `atmel_i2s_dai_probe()`, `atmel_i2s_sama5d2_mck_init()`, and `atmel_i2s_probe()`.

## Control Flow
Probe maps registers, initializes regmap, requests IRQ, gets `pclk` and optional `gclk`, applies clock mux capability, enables `pclk`, enables error interrupts, registers the DAI/component, fills DMA addresses, and registers DMAengine PCM. `set_fmt` records the DAI format. `hw_params` validates I2S format, master/slave mode, channel count, and PCM format, then updates `ATMEL_I2SC_MR`. Trigger starts/stops RX or TX and reference-counts master-clock generator enablement in master mode.

## State And Persistence
Persistent state includes regmap, clocks, DMA data, saved DAI format, selected GCK parameters, capabilities, and `clk_use_no`. Hardware state includes mode register fields, control register commands, interrupt masks/status, holding registers, and version register.

## Dependencies And Integration Points
It depends on OF compatible `atmel,sama5d2-i2s`, clocks `pclk`, `gclk`, optional `muxclk`, regmap MMIO, DMAengine PCM, and `dma-names`; a `rx-tx` DMA name marks half-duplex operation.

## Risks And Test Signals
Risks include only supporting I2S format, clock generator reference counting across simultaneous streams, nearest GCK rate selection, and cleanup after component registration failures. Test signals are probe version logging, playback/capture for all listed formats/rates, overrun/underrun interrupt logs when forced, master and slave clock modes, and half-duplex behavior when DT requests it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-dma.c

## Purpose
This file provides the DMAengine PCM platform registration used by Atmel SSC audio when the SSC platform data selects DMA instead of PDC. It supplies generic PCM hardware constraints and DMA slave configuration for SSC transmit and receive registers.

## Important APIs, Types, And Functions
The exported API is `atmel_pcm_dma_platform_register(struct device *dev)`. `atmel_pcm_dma_irq()` is an SSC error handler installed into `atmel_pcm_dma_params`; `atmel_pcm_configure_dma()` prepares `dma_slave_config` and sets the handler. `atmel_dmaengine_pcm_config` ties these to `devm_snd_dmaengine_pcm_register()`.

## Control Flow
Registration installs a generic DMAengine PCM component. During `hw_params`, `atmel_pcm_configure_dma()` converts ALSA params to DMA slave config, points DMA to `SSC_THR` and `SSC_RHR`, sets bursts to one, and arms the SSC error callback. When SSC interrupt code reports an overrun/underrun, `atmel_pcm_dma_irq()` disables the direction, stops the stream with xrun, and drains status.

## State And Persistence
No private platform state is allocated here. It mutates shared `struct atmel_pcm_dma_params` owned by the SSC DAI by setting `dma_intr_handler`.

## Dependencies And Integration Points
It depends on `atmel-pcm.h`, `linux/atmel-ssc.h`, DMAengine PCM helpers, and the SSC DAI interrupt fanout. It is selected by `CONFIG_SND_ATMEL_SOC_DMA`.

## Risks And Test Signals
Risk is that the shared handler pointer must be cleared by the caller's stream lifecycle, and xrun recovery must leave SSC status clean. Test signals are DMAengine PCM registration, valid DMA slave addresses, expected xrun logs on injected SSC errors, and successful playback/capture with SSC DMA mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-pdc.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-pdc.c

## Purpose
This file implements the legacy Atmel PDC-backed PCM component for SSC audio. It manually programs PDC current and next pointer/count registers, manages period rotation, reports period elapsed from SSC interrupts, and exposes PCM operations for open/close/hw_params/hw_free/prepare/trigger/pointer.

## Important APIs, Types, And Functions
The exported API is `atmel_pcm_pdc_platform_register(struct device *dev)`. State is `struct atmel_runtime_data`. Important callbacks are `atmel_pcm_new()`, `atmel_pcm_hw_params()`, `atmel_pcm_hw_free()`, `atmel_pcm_prepare()`, `atmel_pcm_trigger()`, `atmel_pcm_pointer()`, `atmel_pcm_open()`, `atmel_pcm_close()`, and interrupt helper `atmel_pcm_dma_irq()`.

## Control Flow
Open installs hardware constraints and allocates runtime data. `hw_params` binds stream DMA params from the SSC DAI, records buffer bounds and period size, and sets the interrupt handler. Prepare disables PDC and SSC end interrupts. Trigger start loads current and next period registers, enables SSC end interrupts, then enables PDC. End-of-transfer interrupts advance and reload the next pointer; end-buffer interrupts recover by restarting the PDC. Pointer reads the current PDC pointer and converts it to frames.

## State And Persistence
Runtime state stores DMA buffer start/end, period size, next period pointer, and a pointer to shared SSC DMA params. Hardware state lives in SSC/PDC pointer, counter, PTCR, IER/IDR, and status registers.

## Dependencies And Integration Points
It depends on `atmel-pcm.h`, `linux/atmel_pdc.h`, `linux/atmel-ssc.h`, and `atmel_ssc_dai.c` to allocate SSC DMA params and fan out interrupts.

## Risks And Test Signals
Risk areas include manual circular-buffer bookkeeping, static warning counter in the interrupt helper, pointer races with hardware, and 32-bit DMA mask assumptions. Test signals are stable period interrupts, correct ALSA pointer wrap, xrun recovery on end-buffer events, and no stale handler after `hw_free`/close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-pdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm.h

## Purpose
This header defines the shared contract between Atmel SSC DAI code and the two PCM transport implementations, PDC and DMAengine.

## Important APIs, Types, And Functions
Important types are `struct atmel_pdc_regs`, `struct atmel_ssc_mask`, and `struct atmel_pcm_dma_params`. It defines `ATMEL_SSC_DMABUF_SIZE`, raw SSC access macros `ssc_readx()`/`ssc_writex()`, and conditional declarations/stubs for `atmel_pcm_pdc_platform_register()` and `atmel_pcm_dma_platform_register()`.

## Control Flow
No runtime control flow in the header. Conditional compilation selects real registration functions when the corresponding config is enabled, otherwise stubs return success.

## State And Persistence
The structures describe persistent per-stream integration state: SSC device, PDC register offsets, status masks, substream pointer, transfer size, and interrupt callback. Actual lifetime is managed by SSC DAI and PCM callbacks.

## Dependencies And Integration Points
It depends on `linux/atmel-ssc.h` and is included by SSC DAI plus both PCM implementations. It is the main ABI-like internal bridge between the DAI's SSC register programming and the PCM transport's buffer movement.

## Risks And Test Signals
Risk is stale or inconsistent mask/register definitions causing one transport to disable or acknowledge the wrong hardware state. Test signals are both PDC and DMA variants building, SSC streams setting/clearing `dma_intr_handler` correctly, and injected overrun/underrun handling through the shared callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.c

## Purpose
This driver exposes the Atmel SAMA5D2 PDMIC as a capture-only ASoC component and simple sound card using the dummy codec. It configures PDM microphone clocking, oversampling, sample size, gain, offset, filters, DMAengine capture, and overrun interrupt handling.

## Important APIs, Types, And Functions
State is `struct atmel_pdmic` and DT-derived `struct atmel_pdmic_pdata`. Important functions are `atmel_pdmic_dt_init()`, `atmel_pdmic_cpu_dai_startup()`, `atmel_pdmic_cpu_dai_prepare()`, `atmel_pdmic_platform_configure_dma()`, `pdmic_get_mic_volsw()`, `pdmic_put_mic_volsw()`, `atmel_pdmic_component_probe()`, `atmel_pdmic_cpu_dai_hw_params()`, `atmel_pdmic_cpu_dai_trigger()`, `atmel_pdmic_get_sample_rate()`, `atmel_pdmic_interrupt()`, and `atmel_pdmic_probe()`.

## Control Flow
Probe parses required mic frequency bounds and optional card name/offset, gets clocks, sets `gclk` to one third of `pclk`, maps regmap, requests IRQ, computes supported sample-rate bounds, registers the capture DAI, DMAengine PCM, and a one-link card. Startup enables clocks, clears control state, stores the active substream, and enables overrun interrupts. `hw_params` enforces mono, 16/32-bit formats, chooses OSR 64 or 128, selects pclk or gclk prescaler, and updates mode/DSPR registers. Trigger enables/disables PDM capture. Interrupt on overrun disables capture and stops the substream with xrun.

## State And Persistence
Software state includes clocks, regmap, active substream, physical DMA source, IRQ, and pdata. Hardware state includes PDM enable, clock source/prescaler, converted data register, DSP filter/gain/offset registers, and overrun interrupt state.

## Dependencies And Integration Points
It depends on OF properties `atmel,mic-min-freq`, `atmel,mic-max-freq`, optional `atmel,mic-offset` and `atmel,model`, clocks `pclk`/`gclk`, regmap MMIO, DMAengine PCM, dummy codec, and register definitions in `atmel-pdmic.h`.

## Risks And Test Signals
Risk areas include prescaler division assumptions, global static DAI rate fields modified at probe, substream pointer validity in IRQ, and gain table mapping. Test signals are card registration, mono capture at min/max computed rates, gain/filter controls updating registers, DMA source address correctness, and clean xrun handling on forced overrun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.h -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.h

## Purpose
This header defines PDMIC register offsets and bit fields used by the Atmel PDM microphone controller driver.

## Important APIs, Types, And Functions
It defines `PDMIC_CR`, `PDMIC_MR`, `PDMIC_CDR`, interrupt registers, `PDMIC_DSPR0`, `PDMIC_DSPR1`, write-protect registers, and masks/shifts for software reset, PDM enable, clock source, prescaler, overrun interrupt, high-pass and SINCC filter bypass, sample size, oversampling ratio, gain scale, shift, digital gain, and offset.

## Control Flow
None.

## State And Persistence
The macros describe volatile PDMIC MMIO state. Gain/offset/filter fields are user-visible through ALSA controls and component probe initialization.

## Dependencies And Integration Points
It depends on Linux bit helpers and is included by `atmel-pdmic.c`. Correct mask definitions are required for clock, DMA, gain, and interrupt handling.

## Risks And Test Signals
Wrong fields could disable capture, select incorrect sample width, or corrupt gain/offset. Test signals are register dumps after probe and `hw_params`, ALSA control round trips for gain/filter switches, and capture data with expected word size and level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.c

## Purpose
This file implements the Atmel SSC ASoC CPU DAI. It configures SSC serial audio timing for I2S, left-justified, and DSP_A formats, coordinates playback/capture direction ownership, supplies DMA/PDC parameters to PCM transports, handles SSC interrupts, and exports `atmel_ssc_set_audio()` for machine drivers.

## Important APIs, Types, And Functions
Key static data includes PDC register descriptors, TX/RX masks, `ssc_dma_params[NUM_SSC_DEVICES][2]`, and `ssc_info[NUM_SSC_DEVICES]`. Important functions are `atmel_ssc_interrupt()`, `atmel_ssc_hw_rule_rate()`, `atmel_ssc_startup()`, `atmel_ssc_shutdown()`, `atmel_ssc_set_dai_fmt()`, `atmel_ssc_set_dai_clkdiv()`, `atmel_ssc_hw_params()`, `atmel_ssc_prepare()`, `atmel_ssc_trigger()`, `atmel_ssc_suspend()`, `atmel_ssc_resume()`, `asoc_ssc_init()`, `atmel_ssc_set_audio()`, and `atmel_ssc_put_audio()`.

## Control Flow
Machine drivers call `atmel_ssc_set_audio(id)`, which requests an SSC device and registers the DAI plus either DMAengine or PDC PCM based on `ssc->pdata->use_dma`. Startup enables the SSC clock, resets hardware if needed, installs a rate hw-rule, assigns per-direction DMA params, and enforces one substream per direction. `hw_params` computes BCLK/frame dividers, sample size, PDC transfer size, clock/frame mode registers, and format registers; it requests the SSC IRQ on first initialization and writes CMR/RCMR/RFMR/TCMR/TFMR. Trigger writes SSC enable/disable commands. The IRQ handler masks status with IMR and calls the PCM transport's registered `dma_intr_handler` for endx/endbuf events.

## State And Persistence
Persistent state is global per SSC ID: requested SSC device, direction mask, initialized flag, DAI format, dividers, forced-divider bitmap, DMA params, saved suspend registers, and master clock rate. Hardware state includes SSC clock mode, receive/transmit clock and frame mode registers, interrupt masks, PDC registers, and CR enable/disable state.

## Dependencies And Integration Points
It depends on `linux/atmel-ssc.h`, `linux/atmel_pdc.h`, `atmel-pcm.h`, and machine drivers such as `atmel_wm8904.c`. It exports symbols to allow board drivers to allocate/release SSC audio use.

## Risks And Test Signals
Risk areas include global arrays limited to three SSC devices, divider conflicts between simultaneous playback/capture, request/free IRQ lifecycle, uncommon slave-clock rate rules, and format limitations. Test signals are machine-driver probe with each SSC ID, I2S/LJ/DSP_A playback and capture, suspend/resume restoring registers, PDC and DMA modes receiving interrupts, and correct `-EBUSY` for direction conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.h -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.h

## Purpose
This header declares the internal Atmel SSC ASoC interface shared with machine drivers and the SSC DAI implementation.

## Important APIs, Types, And Functions
It defines SSC clock-divider IDs `ATMEL_SSC_CMR_DIV`, `ATMEL_SSC_TCMR_PERIOD`, and `ATMEL_SSC_RCMR_PERIOD`; direction masks; SSC bit-field values missing from the generic SSC header; `struct atmel_ssc_state`; `struct atmel_ssc_info`; and exported functions `atmel_ssc_set_audio(int ssc_id)` / `atmel_ssc_put_audio(int ssc_id)`.

## Control Flow
No executable control flow in the header. Machine drivers call the exported functions to allocate and release SSC audio ownership.

## State And Persistence
`struct atmel_ssc_info` describes persistent per-SSC runtime state: ownership mask, initialization state, DAI format, dividers, DMA params, saved registers, and clock rate. `struct atmel_ssc_state` is used across suspend/resume.

## Dependencies And Integration Points
It depends on `linux/atmel-ssc.h` and `atmel-pcm.h`. It is included by `atmel_ssc_dai.c` and board drivers such as `atmel_wm8904.c`.

## Risks And Test Signals
Risk is ABI drift between the header's fields and implementation assumptions, especially divider IDs and saved register fields. Test signals are successful compilation of machine drivers using the exported functions and runtime suspend/resume restoring SSC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_wm8904.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_wm8904.c

## Purpose
This is an Atmel machine driver for boards using an SSC controller with a WM8904 codec. It parses devicetree, allocates SSC audio support, configures the codec FLL/sysclk during `hw_params`, and registers a one-link ASoC card with DAPM widgets and DT-provided routing.

## Important APIs, Types, And Functions
Important data includes DAPM widgets, `atmel_asoc_wm8904_dailink`, and `atmel_asoc_wm8904_card`. Key functions are `atmel_asoc_wm8904_hw_params()`, `atmel_asoc_wm8904_dt_init()`, `atmel_asoc_wm8904_probe()`, and `atmel_asoc_wm8904_remove()`. It uses `SND_SOC_DAILINK_DEFS()` with empty CPU/platform components filled from DT and a WM8904 codec DAI named `wm8904-hifi`.

## Control Flow
Probe sets the card device, parses `atmel,model` and `atmel,audio-routing`, resolves `atmel,ssc-controller` and `atmel,audio-codec`, obtains the SSC alias ID, calls `atmel_ssc_set_audio(id)`, and registers the card. `hw_params` programs the WM8904 FLL from a 32.768 kHz MCLK to `sample_rate * 256`, then selects FLL as the codec system clock. Remove unregisters the card and releases the SSC.

## State And Persistence
State is mostly static card/dailink data updated with DT nodes. Runtime codec clock state is programmed per stream. SSC ownership persists from probe until remove through `atmel_ssc_set_audio()`/`put_audio()`.

## Dependencies And Integration Points
It depends on OF properties, WM8904 codec support, `atmel_ssc_dai.h`, and the SSC DAI/PCM stack. DAI format is I2S, normal bit/frame polarity, codec bit/frame provider (`SND_SOC_DAIFMT_CBP_CFP`).

## Risks And Test Signals
Risk areas include static global card data for multiple instances, alias ID errors, fixed 32.768 kHz FLL input assumption, and cleanup if card registration fails. Test signals are successful DT parsing, SSC allocation, WM8904 PLL/sysclk programming at stream start, DAPM routes matching board audio, and clean remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_wm8904.c -->
