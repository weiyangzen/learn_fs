# subset-b-006551 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.h -->
# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.h

## Purpose
`stm32_sai.h` is the shared register and parent-state contract for the STM32 SAI ASoC drivers. It names the global SAI register bank, sub-block A/B register offsets, hardware capability registers, bit fields for clocking/frame/slot/DMA/PDM/error handling, and the parent `struct stm32_sai_data` consumed by the sub-block implementation in `stm32_sai_sub.c`.

## Important APIs, Types, And Functions
The file exports register offsets such as `STM_SAI_GCR`, `STM_SAI_CR1_REGX`, `STM_SAI_FRCR_REGX`, `STM_SAI_SLOTR_REGX`, `STM_SAI_SR_REGX`, `STM_SAI_PDMCR_REGX`, and hardware identity registers. Bitfield helpers cover synchronization (`SAI_GCR_SYNCIN_MASK`, `SAI_XCR1_SYNCEN_MASK`), data size (`SAI_XCR1_DS_*`), master clock division (`SAI_XCR1_MCKDIV_*`), FIFO threshold/flush, frame length and active frame-sync length, slot enable masks, interrupt/status/clear bits, and PDM microphone delay fields. `enum stm32_sai_syncout` identifies no sync, sub-block A, or sub-block B sync output. `struct stm32_sai_conf` carries version, FIFO size, SPDIF/PDM support, DMA-burst limits, and an optional callback for parent clock selection. `struct stm32_sai_data` stores the parent platform device, MMIO base, bus and parent clocks, hardware config, IRQ, synchronization callback, and cached global configuration register.

## Control Flow
This header has no executable control flow. Its definitions drive the parent SAI instance and sub-block driver: probe code determines version/capabilities, sub-block callbacks use the CR1/CR2/FRCR/SLOTR fields to program PCM formats and clocks, IRQ paths use SR/IMR/CLRFR masks, and PDM/SPDIF support is gated by `STM_SAI_HAS_SPDIF_PDM()`.

## State And Persistence
The persistent state modeled here is hardware state in SAI registers plus the parent driver's `stm32_sai_data`. Register cache behavior is implemented in the C files; this header defines which bits are meaningful and how hardware variants change divider width or feature availability.

## Dependencies And Integration Points
The header depends on Linux bitfield helpers and is included by STM32 SAI implementation files. It integrates with platform-device state, the common clock framework, STM32 device-tree synchronization, regmap/MMIO access in the C files, and ASoC DMA/DAI code that ultimately programs these fields.

## Risks And Edge Cases
Divider masks depend on `STM_SAI_STM32F4` versus H7-style versions; using the wrong `version` yields invalid MCKDIV programming. PDM registers are present only on newer hardware and only for sub-block A in the sub-driver. The sync input max helper is tied to the two-bit GCR field and constrains device-tree `st,sync` indices. This header has no include guard, so it relies on normal one-time inclusion patterns.

## Test Signals
Useful validation is mostly indirect: build both F4 and H7 SAI drivers, probe SAI nodes with and without PDM/SPDIF, exercise internal and external synchronization properties, verify divider masks written for F4 versus H7, and check IRQ status/clear handling with overrun, underrun, frame sync, and clock-configuration error conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai_sub.c -->
# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai_sub.c

## Purpose
`stm32_sai_sub.c` implements each STM32 SAI sub-block, A or B, as an ASoC CPU DAI with DMAengine PCM support. It configures TDM/I2S/left/right-justified/DSP formats, optional IEC60958 S/PDIF playback, SAI kernel/master clock routing, sub-block synchronization, DMA FIFO access, and runtime register cache handling.

## Important APIs, Types, And Functions
The central state is `struct stm32_sai_sub_data`, which keeps the sub-block regmap, DMA parameters, DAI driver copy, active substream, parent `stm32_sai_data`, sync provider node, SAI clocks, physical register base, direction, master/slave mode, S/PDIF mode, slot/frame/data sizes, IEC958 status bytes, and locks. Important DAI callbacks are `stm32_sai_dai_probe()`, `stm32_sai_set_sysclk()`, `stm32_sai_set_dai_fmt()`, `stm32_sai_set_dai_tdm_slot()`, `stm32_sai_startup()`, `stm32_sai_hw_params()`, `stm32_sai_trigger()`, `stm32_sai_shutdown()`, and `stm32_sai_pcm_new()`. Clock helpers include `stm32_sai_set_parent_clk()`, `stm32_sai_set_parent_rate()`, `stm32_sai_configure_clock()`, and the local mclk provider callbacks. S/PDIF support is handled through IEC958 controls and `stm32_sai_pcm_process_spdif()`.

## Control Flow
Probe allocates sub-block state, derives A/B id from OF match data, gets parent SAI data, selects the clock-rate strategy, parses MMIO/regmap/direction/SPDIF/sync/clock properties, requests the shared parent IRQ, registers DMAengine PCM, registers the component/DAI, and enables PM runtime. DAI probe fills DMA FIFO address and maxburst, then programs RX/TX direction and sync mode. Startup records the active substream, constrains S/PDIF streams to stereo S32_LE, enables the SAI kernel clock, clears pending flags, and enables error IRQs appropriate to master or slave mode. `hw_params()` computes slot/frame layout or S/PDIF status, programs data size/FIFO threshold, and configures clocks when the SAI is master. Trigger enables or disables DMA and SAI bits. Shutdown masks IRQs, disables the SAI clock, releases exclusive clock rates when appropriate, and clears the active substream under the IRQ lock. Suspend/resume switches regcache cache-only mode and syncs registers through the parent peripheral clock.

## State And Persistence
The driver persists register configuration in regmap cache and hardware registers. Runtime stream state is `sai->substream`, `sai->data_size`, slot/frame fields, clock exclusivity (`sai_ck_used`, `mclk_rate`), and the IEC958 channel-status buffer. `ctrl_lock` protects IEC958 control bytes, while `irq_lock` protects substream stop races. Device-managed allocations handle most lifetime, but `np_sync_provider` is explicitly `of_node_put()` on error/remove.

## Dependencies And Integration Points
The file integrates with the STM32 parent SAI platform device through `stm32_sai_data`, OF compatibles `st,stm32-sai-sub-a` and `st,stm32-sai-sub-b`, `dma-names` for `tx` or `rx`, optional `st,iec60958`, optional `st,sync`, `sai_ck` and optional/exported MCLK clocks, the common clock framework, regmap, DMAengine PCM, ASoC component/DAI registration, and shared parent IRQ delivery.

## Risks And Edge Cases
Clock configuration is sensitive to active streams sharing the same SAI kernel clock; `clk_rate_exclusive_get()`/`put()` balance and set_sysclk shutdown paths need coverage. S/PDIF is playback-only and disallows mmap because the PCM process hook rewrites DMA buffer samples to inject IEC958 status bits. Divider calculations can reject valid-looking rates when the parent clock cannot produce an accurate frequency within tolerance. Sync setup rejects self-references and unsupported external sync on F4. DMA maxburst falls back to 1 for small FIFOs or `no_dma_burst`. The stop path writes bitwise negated masks as values for `regmap_update_bits()`, which works because the mask limits affected bits but is easy to misread or break during refactoring.

## Test Signals
Test regular playback and capture, S/PDIF playback, mono-in-stereo-slot behavior, TDM slot masks, all supported DAI formats and clock polarities, master and slave configurations, internal and external sync, MCLK provider and consumer modes, F4 versus H7 divider widths, DMA burst fallback, overrun/underrun/frame-sync IRQs, IEC958 control get/put and sample-rate status updates, suspend/resume regcache sync, and probe failures for missing `dma-names`, `sai_ck`, invalid sync indices, and unsupported S/PDIF capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai_sub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_spdifrx.c -->
# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_spdifrx.c

## Purpose
`stm32_spdifrx.c` is an ASoC CPU DAI driver for the STM32H7 SPDIF receiver. It captures IEC60958 audio over DMA, synchronizes the hardware receiver to incoming S/PDIF activity, exposes input/channel-status controls, retrieves channel-status and user bits using a secondary DMA channel, and handles receiver error IRQs.

## Important APIs, Types, And Functions
`struct stm32_spdifrx_data` stores platform/MMIO/regmap state, a completion for channel-status retrieval, the kernel clock, capture DMA parameters, active substream, a separate control DMA channel and buffer, slave DMA config, spinlocks, cached CS/UB arrays, IRQ, and a receiver refcount. Key routines are `stm32_spdifrx_start_sync()`, `stm32_spdifrx_stop()`, `stm32_spdifrx_isr()`, `stm32_spdifrx_startup()`, `stm32_spdifrx_hw_params()`, `stm32_spdifrx_trigger()`, `stm32_spdifrx_shutdown()`, `stm32_spdifrx_get_ctrl_data()`, `stm32_spdifrx_dma_complete()`, `stm32_spdifrx_dai_probe()`, `stm32_spdifrx_probe()`, and PM suspend/resume helpers.

## Control Flow
Probe allocates state, maps registers, gets `kclk`, requests the IRQ, optionally resets the block, registers DMAengine PCM, registers the ASoC component/DAI, configures the `rx-ctrl` DMA channel for CSR reads, checks the hardware ID/version, and enables PM runtime. DAI probe sets the regular capture FIFO DMA address and registers IEC958/input/channel controls. PCM startup stores the active substream and enables `kclk`. `hw_params()` selects packed 16-bit or left-aligned 32-bit data format and forces 4-byte DMA bus width. Trigger start enables overrun IRQ and RX DMA, then calls `stm32_spdifrx_start_sync()`, which enables sync/error IRQs, increments a refcount, and starts synchronization if the receiver is idle. The ISR clears flags, enables full receive mode when sync completes, stops PCM on xrun-level errors, and disconnects the stream on frame/sync/timeout errors after attempting a retry if still in sync state. Stop decrements the shared refcount, disables receive/DMA/IRQs at zero, clears flags, and dummy-reads DR/CSR. Control reads start the control DMA, enable CSR DMA and sync, wait up to 100 ms for completion, copy CS/UB bytes, then stop sync and DMA.

## State And Persistence
Persistent state includes regmap-cached control registers, DMA channel configuration, the CS/UB arrays returned to ALSA controls, the active substream pointer, and the `refcount` shared between PCM capture and control-data retrieval. `lock` serializes enable/disable and refcount transitions; `irq_lock` protects substream stop races.

## Dependencies And Integration Points
The driver binds `st,stm32h7-spdifrx`, uses MMIO resources, the `kclk` clock, an IRQ, optional reset control, regular RX DMA plus an `rx-ctrl` DMA channel, regmap, DMAengine PCM, ASoC controls/DAI/component APIs, and ALSA IEC958 control conventions. Runtime consumers see a capture-only DAI supporting one or two channels, 8 kHz to 192 kHz, S16_LE and S32_LE.

## Risks And Edge Cases
Two local macros appear misspelled in this snapshot: `SPDIFRX_CR_INSEL_MASK` references `PDIFRX_CR_INSEL_SHIFT`, and `SPDIFRX_SR_WIDTH5_MASK` references `PDIFRX_SR_WIDTH5_SHIFT`; as written, those are compile-time failures if the macros are used by the preprocessor. `sync_state = FIELD_GET(...) && SPDIFRX_SPDIFEN_SYNC` is a boolean expression rather than an equality check, so any nonzero state is treated as sync for retry decisions. Control reads ignore the return from `stm32_spdifrx_get_ctrl_data()` in the get callbacks and can expose stale zeroed data after timeout. `reinit_completion()` is not called before each control DMA request, so repeated reads rely on completion state behavior that should be audited. Probe error cleanup calls `stm32_spdifrx_remove()` after partial initialization, so channel/buffer NULL/error states need to stay safe.

## Test Signals
Build this file with the target config to catch macro typos, probe with missing `kclk`, missing IRQ, missing `rx-ctrl` DMA, and reset errors, run S16_LE and S32_LE capture at standard rates, test absent S/PDIF signal and synchronization timeout, inject parity/overrun/frame/sync/timeout IRQs, verify refcount behavior when IEC958 controls are read during active capture, validate CS/UB extraction around start-of-block detection, and run suspend/resume with cached register sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_spdifrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/Kconfig

## Purpose
`sound/soc/sunxi/Kconfig` defines the build-time configuration menu for Allwinner ASoC drivers. It exposes codec, I2S, SPDIF, DMIC, and analog-control options under an `Allwinner` menu gated by `ARCH_SUNXI` or `COMPILE_TEST`.

## Important APIs, Types, And Functions
The file declares `SND_SUN4I_CODEC`, `SND_SUN8I_CODEC`, `SND_SUN8I_CODEC_ANALOG`, `SND_SUN50I_CODEC_ANALOG`, `SND_SUN4I_I2S`, `SND_SUN4I_SPDIF`, `SND_SUN50I_DMIC`, and hidden helper `SND_SUN8I_ADDA_PR_REGMAP`. User-visible options select shared dependencies such as `SND_SOC_GENERIC_DMAENGINE_PCM`, `REGMAP_MMIO`, and the private ADDA PR regmap helper.

## Control Flow
There is no runtime control flow. Kconfig dependency evaluation decides whether options can be enabled and which helper symbols are selected. The resulting symbols drive object inclusion in the sibling Makefile.

## State And Persistence
Persistent state is the kernel configuration. Choices here determine whether driver objects are built in, built as modules, or omitted.

## Dependencies And Integration Points
The menu integrates with the ALSA SoC subsystem, Allwinner architecture symbols, OF/Common Clock dependencies for newer codec blocks, regmap, generic DMAengine PCM, and the `sun8i-adda-pr-regmap` helper shared by sun8i/sun50i analog drivers.

## Risks And Edge Cases
Some drivers can be compiled under `COMPILE_TEST`, so missing architecture-only assumptions should be caught by build bots. `SND_SUN8I_CODEC_ANALOG` and `SND_SUN50I_CODEC_ANALOG` select the hidden regmap helper but still require device-tree pairing with digital codec nodes at runtime. Incorrect dependencies can silently hide drivers from valid platforms or expose them without required framework support.

## Test Signals
Run `olddefconfig`/menuconfig combinations for ARM sunxi, ARM64 sunxi, and `COMPILE_TEST`; verify selected symbols pull the expected helper symbols; build each tristate as built-in and module; and confirm the Makefile object list matches each config symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/Makefile

## Purpose
`sound/soc/sunxi/Makefile` maps Allwinner ASoC Kconfig symbols to the driver objects built for this directory.

## Important APIs, Types, And Functions
The build rules include `sun4i-codec.o`, `sun4i-i2s.o`, `sun4i-spdif.o`, `sun8i-codec-analog.o`, `sun50i-codec-analog.o`, `sun8i-codec.o`, `sun8i-adda-pr-regmap.o`, and `sun50i-dmic.o` under their corresponding `CONFIG_SND_*` symbols.

## Control Flow
There is no runtime control flow. Kbuild expands `obj-$(CONFIG_...)` entries according to whether each symbol is `y`, `m`, or unset.

## State And Persistence
Persistent state is the generated build graph. A built-in symbol links the object into the kernel image; a module symbol builds a loadable module.

## Dependencies And Integration Points
The file integrates directly with `Kconfig` symbols in the same directory and with the top-level ALSA SoC build. It is the final step that turns selected Sunxi audio support into compiled object files.

## Risks And Edge Cases
Any mismatch between Kconfig symbols and object names causes selected drivers to disappear from builds. The helper `sun8i-adda-pr-regmap.o` is hidden behind a selected symbol and must remain available to analog drivers.

## Test Signals
Build all Sunxi audio symbols as modules and built-ins, inspect `modules.order` for expected object modules, and run targeted incremental builds after changing Kconfig names or adding/removing driver files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-codec.c

## Purpose
`sun4i-codec.c` is the main Allwinner internal codec driver for many SoC generations. It combines digital codec FIFO/DMA programming, analog DAPM controls for older integrated codecs, a dummy CPU DAI for DMAengine PCM, and simple-card creation for SoC-specific routing and external analog-control auxiliary devices.

## Important APIs, Types, And Functions
`struct sun4i_codec` stores device, regmap, APB/module clocks, optional reset and GPIOs, regmap fields for variant-specific ADC/DAC FIFOC offsets, and DMA parameters. `struct sun4i_codec_quirks` selects the regmap config, codec component, card factory, FIFO field locations, TX/RX data register offsets, reset requirement, playback-only mode, and DMA maxburst. Core stream callbacks are `sun4i_codec_startup()`, `sun4i_codec_shutdown()`, `sun4i_codec_prepare()`, `sun4i_codec_hw_params()`, and `sun4i_codec_trigger()`. The file defines many ASoC controls, TLV scales, DAPM widgets/routes, card factories such as `sun4i_codec_create_card()`, `sun6i_codec_create_card()`, `sun8i_*_codec_create_card()`, `sun50i_h616_codec_create_card()`, and probe/remove.

## Control Flow
Probe maps registers, fetches quirks from OF compatible data, creates the regmap, enables APB clock, gets the module clock and optional reset, obtains optional speaker/headphone GPIOs, allocates FIFOC regmap fields, fills playback and capture DMA addresses from resource base plus quirk offsets, registers the SoC-specific codec component, registers a dummy CPU DAI component, registers DMAengine PCM, creates a SoC-specific card, stores driver data in the card, and registers the card. PCM startup sets DRQ clear behavior and enables the module clock. `hw_params()` chooses 22.5792 MHz or 24.576 MHz module clock families, maps sample rates to hardware rate codes, programs ADC/DAC sample rate, mono mode, sample-bit mode, FIFO packing, and DMA bus width. Prepare flushes FIFOs and programs trigger levels plus some undocumented SoC tuning. Trigger toggles ADC/DAC DRQ enables. Card initialization can set up headphone jack GPIO reporting, speaker PA GPIO DAPM events, auxiliary analog controls, and device-tree audio routing.

## State And Persistence
State persists in codec registers, regmap fields, DMA parameter structs, clocks, reset line, optional GPIO descriptors, ASoC card/component registration, and DAPM route/control state. Stream state is mostly in ALSA runtime; the driver mutates FIFO mode and DMA width per `hw_params()`. Device-managed resources cover most cleanup, while remove unregisters the card.

## Dependencies And Integration Points
The driver binds many compatibles from `allwinner,sun4i-a10-codec` through `allwinner,sun50i-h616-codec` and `allwinner,suniv-f1c100s-codec`. It depends on MMIO regmap, `apb` and `codec` clocks, optional resets, optional GPIOs `allwinner,pa` and `hp-det`, DMAengine PCM, ASoC component/card APIs, OF audio-routing, and for some sun8i variants the `allwinner,codec-analog-controls` phandle consumed as an auxiliary component.

## Risks And Edge Cases
The static global `aux_dev` is mutated by multiple card factory functions, which risks cross-instance state leakage on systems with more than one matching codec. `sun50i_h616_codec_quirks` sets `reg_adc_fifoc` and `reg_adc_rxdata` absent while `playback_only` is not set in the initializer, so probe still tries to allocate an ADC FIFOC field and configure capture DMA from zeroed fields; this should be verified against the intended local tree state. Several prepare paths program undocumented bits, making regression testing hardware-dependent. Supported rates are explicit, and clock selection rejects unknown rates. Card creation and component registration are tightly coupled; a missing analog-control phandle prevents sun8i cards from probing.

## Test Signals
Build all OF-compatible variants, probe each with valid clocks/resets/DMA, test playback and capture where supported, verify H616 playback-only behavior, exercise S16_LE and S32_LE DMA widths, mono/stereo paths, rate-code mapping for every supported rate, FIFO flush/DRQ trigger behavior, speaker PA and headphone-detect GPIOs, OF audio-routing parsing, auxiliary analog-control binding, and remove/unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-i2s.c

## Purpose
`sun4i-i2s.c` implements the Allwinner I2S/TDM CPU DAI driver across multiple register-layout generations. It programs clocks, serial formats, channel maps, FIFO/DMA controls, runtime PM, and DMAengine PCM integration for playback and capture.

## Important APIs, Types, And Functions
`struct sun4i_i2s` stores bus/module clocks, regmap, optional reset, selected DAI format, MCLK frequency, TDM slots/slot width, DMA data, regmap fields, and variant quirks. `struct sun4i_i2s_quirks` captures reset needs, supported PCM formats, TX FIFO offset, regmap config, bitfield locations, DIN/DOUT pin counts, clock divider tables, and callbacks for BCLK parent rate, sample resolution, word-select size, channel configuration, and format programming. Key functions are `sun4i_i2s_set_clk_rate()`, `sun4i_i2s_hw_params()`, `sun4i_i2s_set_fmt()`, `sun4i_i2s_set_sysclk()`, `sun4i_i2s_set_tdm_slot()`, `sun4i_i2s_trigger()`, runtime PM callbacks, regmap field initialization, and probe/remove.

## Control Flow
Probe allocates state, maps registers, gets IRQ, loads variant data, gets bus and module clocks, initializes regmap, optionally deasserts reset, sets playback/capture DMA FIFO addresses, enables runtime PM or manually resumes, initializes regmap fields, registers DMAengine PCM, and registers the DAI component. Runtime resume enables the bus clock, turns regcache back on, syncs defaults, globally enables the hardware, enables the first SDO line, and enables the module clock. Runtime suspend disables the module clock, output lines, global enable, regcache access, and bus clock. `set_sysclk()` records the desired MCLK. `set_fmt()` delegates to old or new register-layout format callbacks. `hw_params()` applies optional TDM slots, maps playback/capture channels, sets FIFO packing, DMA bus width, sample resolution, word-select size, and clock dividers based on sample rate, MCLK, BCLK, slots, and slot width. Trigger flushes FIFOs, clears counters, toggles TX/RX enables, and toggles DMA request bits.

## State And Persistence
Persistent state is held in regmap cache/defaults, clock rates, reset state, DMA parameters, format/slot fields, and runtime PM state. The DAI is symmetric-rate and supports up to eight channels. Capture DMA uses the fixed RX FIFO offset, while playback TX FIFO offset varies by SoC.

## Dependencies And Integration Points
The driver binds compatibles for A10, A31, A83T, H3, A64 codec I2S, H6, and R329. It depends on MMIO resources, `apb` and `mod` clocks, optional reset control, regmap, runtime PM, ASoC DAI/component APIs, DMAengine PCM, and machine drivers that set sysclk, DAI format, and optional TDM slots.

## Risks And Edge Cases
`sun4i_i2s_set_clk_rate()` derives oversample rate from `i2s->mclk_freq`; if a machine driver never calls `set_sysclk()` or passes an unsupported MCLK ratio, `hw_params()` fails. Divider lookup requires exact integer dividers and rejects otherwise plausible clock rates. The TDM slot API accepts only up to eight slots and ignores tx/rx masks. Only playback DMA bus width is updated in `hw_params()`, so capture width behavior relies on DMA framework defaults or prior configuration. Newer multi-pin R329 channel maps are handled, but `num_dout_pins` is documented as currently unused.

## Test Signals
Test each compatible's probe/reset/runtime PM path, all supported DAI formats and polarity combinations, master and slave clock modes, MCLK/BCLK divider combinations for 44.1 kHz and 48 kHz families, invalid `set_sysclk()` ratios, S16/S20/S24/S32 format constraints, TDM slot overrides, channel counts from 1 to 8, trigger start/stop register bits, suspend/resume regcache sync, and DMA FIFO addresses for old/new TX offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-spdif.c

## Purpose
`sun4i-spdif.c` implements the Allwinner S/PDIF transmit CPU DAI. It programs S/PDIF TX format, IEC958 channel status, clocks, FIFO/DMA controls, runtime PM, and SoC-specific FIFO/clock/reset differences.

## Important APIs, Types, And Functions
`struct sun4i_spdif_dev` stores platform device, S/PDIF TX clock, APB clock, optional reset, a per-instance DAI-driver copy, regmap, TX DMA parameters, quirks, and a spinlock for IEC958 status registers. `struct sun4i_spdif_quirks` selects TX FIFO offset, reset requirement, TX FIFO flush bit, MCLK multiplier, and optional TX clock name. Main functions include `sun4i_spdif_configure()`, `sun4i_spdif_startup()`, `sun4i_spdif_hw_params()`, `sun4i_spdif_trigger()`, IEC958 control get/put helpers, runtime suspend/resume, and probe/remove.

## Control Flow
Probe allocates state, copies the static DAI driver to set a per-device name, maps registers, loads quirks, initializes regmap, gets APB and S/PDIF/TX clocks, fills TX DMA FIFO address and default width, optionally deasserts reset, registers the component/DAI, enables runtime PM or resumes manually, and registers DMAengine PCM. Startup rejects capture streams and soft-resets/configures the transmitter. `hw_params()` validates one/two-channel PCM or four-channel raw mode, selects 16/20/24-bit S/PDIF formatting and DMA width, chooses the clock family for the requested sample rate, applies the SoC MCLK multiplier, sets the TX clock rate, computes the hardware TX ratio, and writes TX configuration including channel-status mode. Trigger start enables single-channel mode if needed, TX, TX DRQ, and global enable; trigger stop disables them. IEC958 controls read/write channel-status registers under the spinlock and set the non-audio TX bit from status byte 0.

## State And Persistence
The driver persists TX configuration, channel-status registers, clock enable state, DMA parameters, runtime PM state, and optional reset state. The channel-status control state lives directly in hardware registers rather than a separate software cache.

## Dependencies And Integration Points
The driver binds A10, A31, H3, H6, H616, and A523 S/PDIF compatibles. It depends on MMIO regmap, `apb` and `spdif` or variant `tx` clocks, optional reset control, DMAengine PCM, ASoC DAI/component APIs, ALSA IEC958 controls, and machine drivers that connect the playback-only DAI.

## Risks And Edge Cases
Although RX registers and bits are defined, the DAI and startup path are playback-only. Rate support is limited to explicit 22.05/44.1/88.2/176.4 and 24/32/48/96/192 kHz families; 8/11.025/16 kHz are advertised via `SNDRV_PCM_RATE_8000_192000` but rejected by `hw_params()`, which is an important contract mismatch to test. Mono mode is only set on start and is not explicitly cleared for later stereo streams unless TXCFG is rewritten by `hw_params()`. H3 multiplies MCLK by four and A523 uses a different TX clock name, so clock-tree regressions are easy to introduce.

## Test Signals
Validate probe for every compatible, missing clocks/reset failures, runtime PM resume/suspend clock balance, S16_LE/S20_3LE/S24_LE/S32_LE playback, one/two/four-channel behavior, accepted and rejected sample rates, IEC958 mask/default get/put and non-audio bit updates, FIFO flush and TX counter clear on startup, trigger enable/disable bits, and DMA address selection for old versus sun8i TX FIFO offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun50i-codec-analog.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun50i-codec-analog.c

## Purpose
`sun50i-codec-analog.c` provides the ASoC component for Allwinner A64 internal codec analog controls. It models headphone, line-out, earpiece, microphone, line-in, mixer, ADC, bias, and jack/mic-detect controls that pair with a separate digital codec component.

## Important APIs, Types, And Functions
The file defines 8-bit ADDA register offsets and bit positions, ASoC mixer controls, TLV gain ranges, DAPM widgets/routes, and one component driver. Important routines are `sun50i_codec_hbias_event()`, which toggles microphone ADC support with headset bias power, `sun50i_a64_codec_set_bias_level()`, which gates jack detection, mic ADC, and headphone PA clocking across OFF/STANDBY, and `sun50i_codec_analog_probe()`, which creates the ADDA PR regmap, applies device-property defaults, and registers the component.

## Control Flow
Probe maps the analog register resource, initializes an ADDA PR regmap through `sun8i_adda_pr_regmap_init()`, reads `allwinner,internal-bias-resistor` to set the internal jack/mic bias resistor, programs mic-detect ADC sample interval/filter defaults, and registers the component with controls and DAPM topology. During DAPM operation, widgets route DACs, ADCs, line inputs, mic amps, headphone and line-out muxes, earpiece muxes, and mixers. Bias transitions clear jack-detect/mic-ADC bits and gate the headphone PA clock in OFF, then ungate the PA clock and restore jack detection plus mic ADC based on HBIAS pin state in STANDBY.

## State And Persistence
Persistent state is entirely in the analog ADDA regmap and ASoC DAPM/control state. There is no private driver struct. The component uses `idle_bias_on` and `suspend_bias_off`, so bias level changes are part of power-management behavior.

## Dependencies And Integration Points
The driver binds `allwinner,sun50i-a64-codec-analog`, depends on the shared `sun8i-adda-pr-regmap` helper, ASoC component/DAPM/TLV APIs, device properties, and a digital codec/card that references this analog component as an auxiliary device and connects card-level stream widgets to analog DAC/ADC widgets.

## Risks And Edge Cases
Because this analog component lives in a separate DAPM context from the digital codec, card-level routes must bridge the stream widgets; missing routes can leave valid controls with no powered audio path. Bias handling depends on the DAPM pin status for `HBIAS`; routing or pin naming mistakes can leave `MICADCEN` disabled. The file directly programs mic-detect defaults at probe and does not expose all detection timing knobs as controls. There is no explicit remove path beyond devm cleanup.

## Test Signals
Probe with and without `allwinner,internal-bias-resistor`, verify ADDA PR regmap access, inspect all mixer/mux/volume controls with `amixer`, test DAPM paths for headphone, line-out, earpiece, mic, line-in, and ADC capture, validate OFF/STANDBY bias register changes, test HBIAS DAPM events and mic ADC enable, and suspend/resume with `suspend_bias_off`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun50i-codec-analog.c -->
