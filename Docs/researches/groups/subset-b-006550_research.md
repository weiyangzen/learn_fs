# subset-b-006550 research

Grouped research for Linux ASoC platform files under `sources/distributed-fs/ceph-client/sound/soc/{sprd,starfive,sti,stm}`. Each section preserves the source path and is split into the mapped per-file reports by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-mcdt.c -->
# sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-mcdt.c

Purpose: implements the Spreadtrum Multi-Channel Data Transfer controller as a platform driver and exports a small in-kernel channel API for ASoC users that need FIFO, interrupt, or DMA access to ten ADC and ten DAC MCDT channels. The hardware surface is register-centric: channel data windows, watermarks, interrupt enable/clear/status registers, FIFO address/status registers, DMA channel selection, DMA ACK selection, and FIFO clear registers.

Important APIs and types: `struct sprd_mcdt_dev` owns the mapped register base, device pointer, spinlock, and fixed channel array. The exported API is `sprd_mcdt_request_chan()`, `sprd_mcdt_free_chan()`, `sprd_mcdt_chan_write()`, `sprd_mcdt_chan_read()`, `sprd_mcdt_chan_int_enable()`, `sprd_mcdt_chan_int_disable()`, `sprd_mcdt_chan_dma_enable()`, and `sprd_mcdt_chan_dma_disable()`. Internal helpers program DAC/ADC watermarks, DMA enable bits, DMA channel and ACK routing, FIFO status, FIFO availability, and interrupt masks.

Control flow: probe allocates `sprd_mcdt_dev`, maps MMIO, requests one IRQ, initializes the lock, then populates all channels into a global available-channel list. Clients remove a channel from that list by ID/type. FIFO read/write paths reject operation while DMA mode is active, check real empty/full status, compute FIFO availability from ring read/write addresses, and move 32-bit words. Interrupt mode clears the FIFO, sets an almost-full ADC or almost-empty DAC watermark, enables the channel interrupt plus AP interrupt forwarding, stores the callback, and flips `int_enable`. DMA mode similarly clears and watermarks the FIFO, enables the channel DMA request, maps MCDT channel to one of five DMA channels, maps DMA ACK routing, and flips `dma_enable`. The IRQ handler scans all ADC channels for almost-full and all DAC channels for almost-empty, clears active sources, and calls any registered callback under the controller spinlock.

State and persistence: runtime state is in `sprd_mcdt_chan` flags, callback pointers, FIFO physical addresses, and the global availability list protected by `sprd_mcdt_list_mutex`. Hardware state persists in MMIO until disabled or reset. There is no suspend/resume context save; correctness depends on platform reset and clients reprogramming mode after rebind.

Dependencies and integration points: depends on platform device resources, `sprd,sc9860-mcdt` device-tree compatible, Linux IRQ/MMIO helpers, exported symbols consumed by other Spreadtrum audio components, and the DMA engine via `fifo_phys`/MCDT DMA request routing.

Risks: global list removal assumes list traversal state is valid even if no match; test the no-match path carefully. `sprd_mcdt_update()` is read-modify-write without its own lock and relies on callers holding `mcdt->lock` for shared registers. FIFO sizes are word-based and callers must pass sizes divisible by 4. Callback execution occurs under the spinlock, so callbacks must not sleep or reenter locking paths. Remove deletes only list entries, not outstanding client references.

Test signals: boot with the compatible node, request/free every ADC/DAC channel, verify duplicate request returns NULL, exercise interrupt callbacks with FIFO watermark stimuli, verify DMA enable rejects invalid channels and mutual exclusion with interrupt mode, and run playback/capture clients through suspend/rebind scenarios to expose missing context restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-mcdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-mcdt.h -->
# sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-mcdt.h

Purpose: public header for the Spreadtrum MCDT controller API. It defines channel types, DMA request IDs, callback shape, the opaque-to-users `sprd_mcdt_chan` carrier, and stubs for builds where `CONFIG_SND_SOC_SPRD_MCDT` is disabled.

Important APIs and types: `enum sprd_mcdt_channel_type` distinguishes DAC, ADC, and unknown channels. `enum sprd_mcdt_dma_chan` exposes five MCDT DMA request lanes. `struct sprd_mcdt_chan_callback` carries a `notify(void *data)` hook. `struct sprd_mcdt_chan` records controller pointer, channel ID, FIFO physical address, type, DMA channel, callback, mode flags, and list linkage. API declarations mirror the exported symbols in `sprd-mcdt.c`: request/free, FIFO read/write, interrupt enable/disable, and DMA enable/disable.

Control flow and integration: users include this header to request an ADC or DAC channel, inspect `fifo_phys` for DMA slave configuration, and select manual FIFO, interrupt-driven FIFO, or DMA-driven transfer. The compile-time guard provides callable fallback stubs so dependent drivers can build without hard dependency; most stubs fail with `-EINVAL`, `sprd_mcdt_request_chan()` returns NULL, and `sprd_mcdt_chan_read()` returns 0.

State and persistence: the header intentionally warns users not to modify `struct sprd_mcdt_chan` members, but the structure is not fully opaque. Its fields are shared with the controller implementation and client drivers, so ABI-like field assumptions can leak between modules.

Dependencies: requires Linux list and scalar types through surrounding kernel includes. Real function bodies depend on `CONFIG_SND_SOC_SPRD_MCDT`; otherwise static inline-looking non-static stubs are emitted from the header.

Risks: the disabled-config stub functions are defined in the header without `static inline`, which can create multiple-definition risk if included in multiple translation units in configurations where the real driver is off. Exposed mutable state lets clients accidentally corrupt mode flags or list linkage. The `dma_chan` member is declared but the implementation primarily uses local DMA selection and does not consistently update this field.

Test signals: build both with and without `CONFIG_SND_SOC_SPRD_MCDT`, including multiple includers in the disabled configuration; run sparse/modpost for duplicate symbol issues; validate client drivers do not write to `sprd_mcdt_chan` internals; confirm disabled stubs make dependent modules degrade cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-mcdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-compress.c -->
# sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-compress.c

Purpose: provides Spreadtrum ASoC compressed-offload platform operations for playback, exported as `sprd_platform_compress_ops` and attached by the PCM DMA component. It implements a two-stage DMA design: userspace fills a DDR compressed buffer, DMA channel 1 moves DDR to always-on IRAM, and DMA channel 0 moves IRAM to the DSP/MCDT FIFO.

Important APIs and types: `struct sprd_compr_stream` tracks the ALSA compressed stream, DSP operation callbacks, two DMA channels, IRAM and DDR buffers, DSP play-info area, copied/received counters, and stage pointers. `struct sprd_compr_dma` carries dmaengine channel, descriptor, cookie, link-list memory, and transfer length. The ops implement open, free, set_params, trigger, pointer, copy, get_caps, and get_codec_caps.

Control flow: open coerces a 32-bit DMA mask, allocates stream state, allocates an IRAM block and a DDR block, derives link-list and DSP info subregions, registers a drain callback with DSP ops, and stores private data. `set_params()` configures stage 1 then stage 0 DMA with Spreadtrum link-list flags and sends compressed parameters to DSP firmware via `compr_ops->set_params()`. Trigger START submits both descriptors in reverse order, issues pending transactions, then starts DSP playback. STOP terminates DMA, resets counters/pointers, and stops DSP. PAUSE/RESUME map to dmaengine pause/resume plus DSP pause callbacks. DRAIN delegates to DSP and uses `sprd_platform_compr_drain_notify()` to clear info and notify ALSA.

State and persistence: stream state is per compressed runtime. The IRAM play-info block persists while stream is open and is read by `pointer()` for `pcm_io_frames`. `copy()` updates `received_total`, `received_stage0`, `received_stage1`, `copied_total`, and a wrapping DDR stage pointer. No explicit locking protects copy, trigger, and DMA callback counters, so ALSA sequencing is assumed.

Dependencies and integration points: depends on `snd_compress_ops`, `sprd_compr_ops` supplied by the CPU DAI driver data, Spreadtrum DMA flags/link-list ABI, `snd_dma_alloc_pages()` IRAM support, MP3/AAC compressed codec IDs, and shared declarations in `sprd-pcm-dma.h`.

Risks: the IRAM subregion arithmetic uses `SPRD_COMPR_IRAM_SIZE` as the offset into an allocation of exactly that size, which appears to place link-list/info pointers just past the allocated IRAM block rather than inside it; this deserves close review. DMA scatterlist addresses in `sprd_platform_compr_dma_config()` are set to `dst_addr` for both entries, which may be intentional hardware trigger behavior but is surprising. Codec caps fill descriptor index 1 for AAC without populating descriptor 0. Counters can race with callbacks and userspace copy. Only playback is accepted in trigger, but open/caps expose direction fields.

Test signals: run compressed playback for MP3 and AAC with default and boundary fragment sizes; verify IRAM/DDR DMA addresses with DMA API debugging; check drain callback and `copied_total`/`pcm_io_frames`; stress stop during DMA callback; run KASAN/KMSAN for out-of-bounds subregion access; test pause/resume and wraparound copy into the 2 MiB DDR buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-dma.c

Purpose: implements the Spreadtrum ASoC PCM platform using dmaengine and Spreadtrum DMA link-list mode. It registers PCM component callbacks and wires in compressed-offload ops from `sprd-pcm-compress.c`.

Important APIs and types: `struct sprd_pcm_dma_private` tracks a substream, DAI-provided DMA parameters, per-channel DMA state, hardware channel count, and per-channel buffer offset. `struct sprd_pcm_dma_data` holds dmaengine channel, descriptor, cookie, link-list coherent memory, and previous pointer. The component callbacks implement open, close, hw_params, hw_free, trigger, pointer, and pcm_new.

Control flow: open sets fixed hardware constraints, period/buffer step constraints of 640 bytes, integer periods, allocates private state, and allocates coherent link-list memory for two channels. `hw_params()` retrieves `sprd_pcm_dma_params` from the CPU DAI, lazily requests as many slave DMA channels as the stream has audio channels, builds one scatterlist per period per channel, configures source/destination addresses depending on playback/capture, configures Spreadtrum DMA link-list mode, and assigns period callbacks unless no-period-wakeup is set. Trigger START submits and issues each prepared descriptor; PAUSE/RESUME call dmaengine pause/resume; STOP terminates channels asynchronously. Pointer queries each channel status and derives a combined interleaved frame position.

State and persistence: per-open coherent link-list memory is freed on close. DMA channels are requested at first hw_params and released on hw_free/error. `pre_pointer` is used to detect wrap and combine positions across split channel buffers. Fixed PCM buffers are allocated by `snd_pcm_set_fixed_buffer_all()`.

Dependencies and integration points: consumes CPU DAI DMA data containing device FIFO physical addresses, burst widths, fragment lengths, and DMA channel names. Depends on Spreadtrum DMA custom `SPRD_DMA_FLAGS()` and `struct sprd_dma_linklist`, dmaengine slave SG APIs, `of_reserved_mem_device_init_by_idx()`, and ASoC component registration for compatible `sprd,pcm-platform`.

Risks: pointer math subtracts `runtime->dma_addr` from `state.residue`, although dmaengine residue is normally remaining bytes, not current DMA address; if this DMA driver returns residue conventionally the pointer will be wrong. A single `sg` allocation is reused for all channels before freeing; descriptors must copy it synchronously. The channel count is assumed to match audio channels and capped at two, so multichannel interleaving support is limited. `devm_kzalloc()` plus manual `devm_kfree()` in close works but ties allocations to device lifetime as well as stream lifetime.

Test signals: playback and capture with one and two channels, 16/24-bit formats, periods at 640-byte multiples, no-period-wakeup mode, pause/resume/stop races, pointer monotonicity across wrap, and reserved-memory versus no-reserved-memory boot paths. Use DMAengine tracepoints to confirm link-list descriptors use intended source/destination addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-dma.h -->
# sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-dma.h

Purpose: shared Spreadtrum PCM/compress header. It defines the PCM DMA parameter contract that CPU DAIs provide to the platform driver, and the DSP compressed-offload callback/operation contract consumed by `sprd-pcm-compress.c`.

Important APIs and types: `SPRD_PCM_CHANNEL_MAX` caps PCM DMA at two hardware channels. `struct sprd_pcm_dma_params` supplies per-channel device FIFO physical addresses, data widths, fragment lengths, and dmaengine channel names. `struct sprd_compr_playinfo` is the DSP-visible progress block with total/current time, data length, and current data offset. `struct sprd_compr_params` packages direction, bit/sample rate, channels, format, period layout, and DSP info-buffer location. `struct sprd_compr_callback` carries a drain notification hook. `struct sprd_compr_ops` abstracts firmware-side stream lifecycle and parameter operations. `struct sprd_compr_data` groups ops and DMA params as DAI driver data.

Control flow and integration: PCM code retrieves `sprd_pcm_dma_params` with `snd_soc_dai_get_dma_data()`. Compressed code retrieves `sprd_compr_data` with `snd_soc_dai_get_drvdata()`, then uses `ops` for DSP lifecycle and `dma_params` for two-stage DMA routing. The external symbol `sprd_platform_compress_ops` is attached to the Spreadtrum component driver.

State and persistence: this header does not own state directly, but it defines state copied between AP, DMA engine, and DSP firmware. `sprd_compr_playinfo` is shared through DMA/IRAM memory and therefore must remain layout-stable for firmware.

Dependencies: Linux DMA address types and ALSA compressed ops declarations are expected through includers. The contract assumes Spreadtrum DMA can address the supplied physical FIFOs and memory blocks.

Risks: no versioning or size negotiation exists for the DSP-facing structures. `info_phys` is `u32`, so systems with physical addresses above 4 GiB need constraints or truncation protection. `fragment_len` and `datawidth` are trusted by the platform driver; invalid DAI data can misprogram DMA bursts. The compressed ops use `int str_id`, with current users passing stream direction as the ID, which couples firmware stream numbering to ALSA constants.

Test signals: compile both PCM and compress objects with this header, inspect structure sizes against firmware ABI expectations, test >32-bit DMA address configurations, and validate each DAI supplies two channel names/addresses before compressed playback is opened.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/starfive/Kconfig

Purpose: declares build-time configuration for StarFive JH7110 ASoC platform drivers. The menu is enabled for `ARCH_STARFIVE` or compile-test builds and requires common clock support.

Important entries: `SND_SOC_JH7110_PWMDAC` builds the PWM-DAC DAI driver and selects generic dmaengine PCM plus S/PDIF support. `SND_SOC_JH7110_TDM` builds the TDM DAI driver and selects generic dmaengine PCM. Both are tristate options so they can be built-in or modules.

Control flow and integration: these symbols control object inclusion in the sibling Makefile and expose user-visible configuration prompts. They also pull in core ASoC DMA helpers required by the drivers.

State and persistence: Kconfig has no runtime state, but it constrains which runtime integration points exist in a kernel image. Missing selections would surface as unresolved driver helpers or unavailable PCM registration.

Dependencies: `COMPILE_TEST || ARCH_STARFIVE`, `HAVE_CLK`, ASoC core, generic dmaengine PCM, and S/PDIF for the PWM-DAC option.

Risks: the menu-level dependencies do not explicitly depend on `SND_SOC`; these files live under sound/soc, but direct dependency clarity may matter for randconfig. `SND_SOC_JH7110_PWMDAC` selects `SND_SOC_SPDIF` even though the driver itself exposes S16 playback to PWM-DAC, so verify that dependency is intentional rather than inherited from an older design.

Test signals: run `make ARCH=riscv menuconfig` visibility checks, randconfig with `COMPILE_TEST`, module builds for both options, and dependency audit for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/starfive/Makefile

Purpose: maps StarFive ASoC Kconfig symbols to build objects.

Important entries: `obj-$(CONFIG_SND_SOC_JH7110_PWMDAC) += jh7110_pwmdac.o` and `obj-$(CONFIG_SND_SOC_JH7110_TDM) += jh7110_tdm.o`.

Control flow and integration: when a symbol is `y`, the object links built-in; when `m`, it becomes part of a module for the corresponding driver. There are no composite objects or shared helpers in this directory.

State and persistence: no runtime state. The Makefile simply defines compilation inclusion for the two platform drivers.

Dependencies: paired with sibling Kconfig and the top-level sound/soc build traversal.

Risks: because each driver is a standalone object, any future shared StarFive audio helper would need explicit composite object handling. Current simplicity is low risk.

Test signals: build each Kconfig option as `y` and `m`, confirm the expected module/object names, and run `make M=sound/soc/starfive` style partial builds where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_pwmdac.c -->
# sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_pwmdac.c

Purpose: StarFive JH7110 PWM-DAC ASoC DAI driver. It exposes a playback-only CPU DAI backed by a PWM-DAC FIFO register and generic dmaengine PCM.

Important APIs and types: `struct jh7110_pwmdac_dev` owns MMIO base, physical base, configuration fields, APB/core clocks, APB reset, DMA playback data, and saved CTRL register. Configuration enums represent PWM shift width, duty-cycle alignment, sample count, data-change behavior, data mode, and data shift. DAI ops cover probe, startup, hw_params, and trigger.

Control flow: probe maps the register resource, gets `apb` and `core` clocks, gets reset, initializes default PWM/DMA parameters, registers the component/DAI, registers dmaengine PCM, and enables runtime PM. `hw_params()` maps supported sample rates to `cnt_n` and core clock rates, validates mono/stereo, sets DMA bus width, programs PWM control fields, then sets the core clock rate with a small rounding margin. Trigger start/resume/pause-release reprograms and enables the PWM-DAC; stop/suspend/pause disables it. Runtime PM toggles clocks and reset deassertion. System sleep saves/restores CTRL around forced runtime suspend/resume.

State and persistence: `dev->cfg` holds desired programming, `saved_ctrl` persists CTRL over system sleep, and DMA data persists for DAI probe. The hardware CTRL register is restored on system resume, but only one register is saved.

Dependencies and integration points: device tree compatible `starfive,jh7110-pwmdac`, clock/reset framework, ASoC DAI/component APIs, generic dmaengine PCM, and DMA FIFO address at `mapbase + JH7110_PWMDAC_WDATA`.

Risks: `jh7110_pwmdac_crg_enable(false)` disables clocks but does not assert reset, so hardware state may persist differently across low-power states. `hw_params()` calls `jh7110_pwmdac_set()` before `clk_set_rate()`, so a failed clock set leaves the PWM-DAC programmed/enabled. Rate support is hand-coded; unsupported but ALSA-advertised rates in `SNDRV_PCM_RATE_8000_48000` must be checked by hw_params failures. Only CTRL is restored, not WDATA or clock rate.

Test signals: playback at 8k, 11.025k, 16k, 22.05k, 32k, 44.1k, 48k; mono versus stereo DMA widths; trigger pause/resume; runtime PM autosuspend; system suspend while configured; clock rounding validation on the target clock tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_pwmdac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_tdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_tdm.c

Purpose: StarFive JH7110 TDM ASoC DAI driver with playback and capture support through one FIFO address and generic dmaengine PCM.

Important APIs and types: `struct jh7110_tdm_dev` stores MMIO base, six clocks, reset array, format polarity/sync/master settings, TX/RX channel config, sample rate/PCM clock, playback/capture DMA data, and saved registers. Enums describe master/slave, clock polarity, frame sync timing, FIFO threshold, word length, slot length, and justification. DAI ops cover probe, startup, hw_params, trigger, and set_fmt.

Control flow: probe maps MMIO, gets clock/reset resources, initializes default TDM and DMA parameters, registers component/DAI and dmaengine PCM, then enables runtime PM. `set_fmt()` accepts CPU-master (`BP_FP`) or codec-master (`BC_FC`) modes and writes global control. `hw_params()` validates 16- or 32-bit samples and 1/2/4/6/8 channels, calculates `pcmclk = channels * rate * width`, updates TX or RX slot/word/channel scaling, sets DMA width, writes stream-specific config, validates/writes sync divider, and saves context. Trigger start enables global block and stream TX/RX enable bit from saved context; stop clears the relevant stream enable bit. Runtime PM enables/disables all clocks and reset, selecting `tdm_ext` as parent for `tdm`.

State and persistence: TX and RX configurations are independent. `saved_pcmtxcr`/`saved_pcmrxcr` are stream contexts restored at trigger start; `saved_pcmgbcr` and `saved_pcmdiv` are system sleep contexts. Runtime PM does not itself save stream config.

Dependencies and integration points: compatible `starfive,jh7110-tdm`, clock names `mclk_inner`, `tdm_ahb`, `tdm_apb`, `tdm_internal`, `tdm_ext`, `tdm`, reset array, ASoC dmaengine PCM, and fixed FIFO physical address `0x170c0000`.

Risks: FIFO DMA address is hard-coded rather than derived from the mapped resource, so SoC variants or remapped resources can break. System resume writes saved registers before `pm_runtime_force_resume()`, which may access MMIO while clocks are off depending on PM state. `syncdiv` validation uses enum slot-length values, not bit counts, so confirm hardware encoding math. Full-duplex concurrent hw_params can overwrite shared `pcmclk`/divider assumptions.

Test signals: playback and capture at all advertised rates with 1/2/4/6/8 channels, 16- and 32-bit formats, master and slave format modes, full-duplex start/stop ordering, runtime/system suspend, and DMA FIFO address verification against device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_tdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sti/Kconfig

Purpose: defines the STi ASoC platform support switch.

Important entry: `menuconfig SND_SOC_STI` is a tristate gated by `SND_SOC` and `ARCH_STI || COMPILE_TEST`, selecting `SND_SOC_GENERIC_DMAENGINE_PCM`.

Control flow and integration: enabling the symbol builds the composite STi uniperipheral DAI driver from the sibling Makefile. The menu text identifies STIH416-class platforms and covers all STi uniplayer/unireader instances.

State and persistence: no runtime state. The symbol controls whether the STi platform DAI and DMA PCM registration code exists in the kernel.

Dependencies: ASoC core, STi architecture or compile-test, and generic dmaengine PCM. The C files also depend on syscon/regmap, pinctrl, clocks, IRQs, and ALSA IEC958 controls, but those are not explicit Kconfig dependencies here.

Risks: hidden dependencies may surface in unusual randconfig builds if selected helpers are not otherwise enabled. The single symbol builds all supported player/reader variants, so it cannot trim unused variants by compatible.

Test signals: run randconfig with `COMPILE_TEST`, build as module and built-in, and verify top-level sound/soc Kconfig includes the STi menu only in intended contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sti/Makefile

Purpose: builds the STi ASoC support as one composite object.

Important entries: `snd-soc-sti-y := sti_uniperif.o uniperif_player.o uniperif_reader.o` and `obj-$(CONFIG_SND_SOC_STI) += snd-soc-sti.o`.

Control flow and integration: when `SND_SOC_STI` is enabled, common probe code, player code, and reader code are linked into one module/object, allowing internal shared symbols and exported init helpers to resolve together.

State and persistence: no runtime state; build grouping determines module lifetime for all STi uniperipheral DAIs.

Dependencies: sibling Kconfig, common Linux kbuild composite-object conventions, and top-level ASoC build traversal.

Risks: all player and reader code is included even for systems using only one direction. Future split modules would need symbol export and init ordering review.

Test signals: module build confirms `snd-soc-sti.o` contains all three translation units; boot with each compatible string to ensure shared module autoload covers all variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/sti_uniperif.c -->
# sources/distributed-fs/ceph-client/sound/soc/sti/sti_uniperif.c

Purpose: common STi uniperipheral platform/DAI glue. It maps device-tree compatibles to player/reader capabilities, allocates a `struct uniperif`, initializes the proper direction-specific implementation, registers one ASoC DAI, and registers generic dmaengine PCM.

Important APIs and types: `struct sti_uniperiph_dev_data` describes instance ID, IP version, stream direction, DAI name, and type. Exported common helpers include `sti_uniperiph_reset()`, `sti_uniperiph_set_tdm_slot()`, `sti_uniperiph_fix_tdm_chan()`, `sti_uniperiph_fix_tdm_format()`, `sti_uniperiph_get_tdm_word_pos()`, `sti_uniperiph_dai_probe()`, `sti_uniperiph_dai_set_fmt()`, and `sti_uniperiph_dai_hw_params()`.

Control flow: probe allocates private data and one DAI descriptor, then `sti_uniperiph_cpu_dai_of()` matches DT data, maps MMIO, calculates FIFO physical address, gets IRQ, chooses TDM or PCM mode based on `st,tdm-mode`, calls `uni_player_init()` or `uni_reader_init()`, and fills stream capabilities from `uni->hw`. DAI probe sets playback or capture DMA data to the FIFO address and 32-bit bus width, then creates controls. Common hw_params adjusts DMA maxburst based on user frame size for TDM or channel count for PCM.

State and persistence: `struct uniperif` stores type, version, MMIO, IRQ, clock/control fields, state, substream, IEC958 settings, controls, DAI format, and TDM slot settings. Suspend requires the uniperipheral to be stopped and switches pinctrl sleep/default states.

Dependencies and integration points: DT compatibles for STi players/readers, `uniperif.h` register macros, direction-specific init in `uniperif_player.c`/`uniperif_reader.c`, ASoC DAI/component APIs, pinctrl PM, dmaengine PCM, and optional syscon setup in player init.

Risks: TDM frame-size validation uses a bitmask-style allowed set on byte sizes; verify intended acceptance of 8/16/24/32 bytes. `sti_uniperiph_get_tdm_word_pos()` has no explicit failure when more slots are requested than `WORD_MAX` can represent. Suspend returns busy unless state is stopped, so system suspend can fail during active playback/capture. The code accepts multiple controls with the same name by indexing them to instance ID.

Test signals: bind every compatible, TDM and non-TDM DT modes, set TDM slots for legal and illegal frame sizes, exercise suspend while stopped and while streaming, verify DMA maxburst for PCM/TDM, and inspect ALSA controls per instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/sti_uniperif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/uniperif.h -->
# sources/distributed-fs/ceph-client/sound/soc/sti/uniperif.h

Purpose: shared STi uniperipheral hardware and driver contract header. It contains register access helpers and generated-style macros for soft reset, FIFO data, interrupt status/masks, configuration, control, I2S format, status, channel status, validity, and TDM registers, plus core state structures and common prototypes.

Important APIs and types: generic macros `GET_UNIPERIF_REG()`, `SET_UNIPERIF_REG()`, and `SET_UNIPERIF_BIT_REG()` implement read-modify-write and write-one bit operations. `enum uniperif_version`, `enum uniperif_type`, and `enum uniperif_state` describe IP capabilities and runtime state. `struct uniperif` is the central object shared by common, player, and reader code. `uni_tdm_hw` defines TDM PCM constraints. Prototypes expose player/reader init, DAI callbacks, reset, TDM slot helpers, and frame-size helpers.

Control flow and integration: C files program hardware almost entirely through macros from this header. Version-dependent macros return invalid shifts or zero masks for unsupported registers, so callers must only use them in compatible version paths. `struct uniperif` ties MMIO, IRQ, clock, state, substream, controls, IEC958 status, TDM slots, and DAI ops into one object.

State and persistence: the header defines state fields but does not manage lifetime. Runtime state lives in `state`, `substream`, `stream_settings`, `tdm_slot`, `daifmt`, `mclk`, and `clk_adj`; hardware state lives in MMIO registers modified through macros.

Dependencies: Linux regmap fields, dmaengine PCM, ALSA IEC958 and PCM types through includers, and version-specific STi hardware register semantics.

Risks: many macros perform read-modify-write without locking; callers must serialize concurrent control/trigger/IRQ paths. Several unsupported-version macros encode shift `-1`; accidental use can produce undefined bit operations or invalid MMIO offsets. `GET_UNIPERIF_CHANNEL_STA_REGN(ip)` references `n` despite not taking it as a macro parameter in one definition. `UNIPERIF_I2S_FMT_PADDING_MASK` is duplicated. The large macro surface makes static analysis harder than typed regmap fields.

Test signals: compile with sparse/W=1 to catch macro issues, run Coccinelle for negative shift uses, exercise each player/reader type and IP version path, validate TDM register programming on hardware, and use lockdep/KCSAN around control updates versus IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/uniperif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_player.c -->
# sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_player.c

Purpose: STi uniperipheral playback implementation for PCM, HDMI/SPDIF IEC958, and TDM player modes. It provides DAI operations and initialization consumed by common probe code.

Important APIs and types: exported `uni_player_init()` and `uni_player_resume()`; internal IRQ handler, clock adjustment, IEC958 channel-status controls, prepare functions for IEC958/PCM/TDM, start/stop/trigger/shutdown, set_sysclk, and DT audio-glue parsing. ALSA controls expose IEC958 status and playback oversampling frequency adjustment.

Control flow: init sets stopped state and DAI ops, parses syscon audio glue fields, enables underflow recovery on newer IP, chooses hardware constraints, gets the clock, selects frequency synthesizer, optionally connects I2S/TDM TX bus, requests IRQ, initializes locks, disables idle/back-stall/rounding/SPDIF latency defaults, and installs controls. Startup stores the substream and adds TDM hw rules when needed. Prepare validates stopped state, computes DMA trigger limit, dispatches to IEC958/PCM/TDM format setup, applies DAI inversion/format, resets hardware, and leaves it ready. Start enables the clock, clears/masks interrupts, resets hardware, sets PCM data operation, applies channel status update, and marks started. Stop sets operation off, resets, masks interrupts, disables clock, and marks stopped. IRQ handles underflow, DMA errors, and underflow recovery events, stopping the PCM stream on unrecovered XRUNs.

State and persistence: `player->state`, `substream`, `mclk`, `clk_adj`, `stream_settings`, `underflow_enabled`, and control locks persist while device is bound. IEC958 status is kept in memory and programmed to channel status registers during prepare/control updates. Clock adjustment mutates the requested clock rate in ppm.

Dependencies and integration points: common `sti_uniperif.c`, `uniperif.h`, syscon `st,syscfg`, regmap fields, IRQF_SHARED, ALSA controls, clock framework, and ASoC DAI callbacks.

Risks: trigger limit validation uses `!trigger_limit % 2`, which due to precedence tests `(!trigger_limit) % 2` rather than evenness; the same pattern exists in reader. The IRQ handler assigns `ret = -EPERM` to an `irqreturn_t`. Control update calls channel-status programming under both mutex and IRQ spinlock; ensure no sleeping operations are introduced there. Stop from shutdown occurs under `irq_lock` and calls functions that may touch clocks/MMIO. TDM clock setup bypasses `set_sysclk`.

Test signals: playback in PCM, HDMI, SPDIF, and TDM modes; IEC958 control updates before/during stream; underflow recovery done/failed interrupts; invalid trigger-limit cases; clock adjustment extremes; suspend/resume; shutdown while active; TDM slot constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_player.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_reader.c -->
# sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_reader.c

Purpose: STi uniperipheral capture implementation for PCM and TDM reader modes. It provides DAI ops and initialization used by common probe code for reader-compatible nodes.

Important APIs and types: exported `uni_reader_init()`; internal IRQ handler, PCM/TDM prepare helpers, prepare/start/stop/trigger/startup/shutdown functions, and reader DAI ops. Hardware constraints support 2-8 channel PCM capture up to 96 kHz or shared `uni_tdm_hw` for TDM.

Control flow: init sets device/state/ops, picks PCM or TDM hardware constraints, requests a shared IRQ, and initializes the IRQ lock. Startup stores the substream and adds TDM constraints when applicable. Prepare requires stopped state, computes transfer size and DMA trigger limit, configures FIFO trigger limit, programs TDM or PCM data format, applies DAI format and clock inversion, clears interrupts, enables DMA/FIFO/memory-block interrupt masks, optionally enables underflow recovery interrupts, and resets hardware. Start clears/enables FIFO errors, sets operation to PCM data, and marks started. Stop sets operation off, masks interrupts, and marks stopped. IRQ clears status and stops the PCM stream with XRUN on FIFO overflow/error.

State and persistence: state is minimal: `reader->state`, `substream`, `type`, `daifmt`, `tdm_slot`, IRQ lock, and shared MMIO state. Unlike player, no clock or IEC958 control state is owned here.

Dependencies and integration points: common `sti_uniperif.c` for resource setup and DAI registration, `uniperif.h` macros, dmaengine PCM, shared IRQ, ALSA PCM stream locking, and TDM slot helper rules.

Risks: trigger limit validation has the same `!trigger_limit % 2` precedence issue as player. The prepare path enables `MEM_BLK_READ` and DMA error interrupt masks, but the IRQ handler only handles FIFO error, so other enabled status bits may be ignored. Underflow recovery naming appears playback-oriented but is referenced in reader. Stop does not reset hardware, unlike player stop. TDM reader documents a hardware word-position limitation that must be handled by userspace for some layouts.

Test signals: capture PCM and TDM, invalid channel/format/slot masks, FIFO overflow interrupt causing XRUN, ignored interrupt status bits, repeated prepare/start/stop cycles, shutdown while active, and TDM word-position layouts with 16- and 32-bit slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_reader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/stm/Kconfig

Purpose: declares STM32 ASoC driver configuration for SAI, I2S, SPDIFRX, and DFSDM audio capture.

Important entries: `SND_SOC_STM32_SAI` selects generic dmaengine PCM, regmap MMIO, and IEC958 PCM support. `SND_SOC_STM32_I2S` selects generic dmaengine PCM and regmap MMIO. `SND_SOC_STM32_SPDIFRX` selects generic dmaengine PCM, regmap MMIO, and S/PDIF codec support. `SND_SOC_STM32_DFSDM` depends on `STM32_DFSDM_ADC` and selects generic dmaengine PCM, DMIC codec, and IIO callback buffers.

Control flow and integration: these symbols are consumed by the sibling Makefile to include controller and sub-block objects. Architecture dependency is `(ARCH_STM32 && OF) || COMPILE_TEST` for register DAIs and `ARCH_STM32 || COMPILE_TEST` for DFSDM.

State and persistence: no runtime state; symbols determine which platform drivers and helper objects are built.

Dependencies: ASoC core, common clock where required, regmap, generic dmaengine PCM, S/PDIF/IEC958 helpers, STM32 DFSDM ADC, and IIO buffer callbacks.

Risks: DFSDM requires IIO callback plumbing; missing or mismatched IIO symbols will break link/build. `COMPILE_TEST` coverage is useful but may mask runtime-only clock/reset/device-tree requirements.

Test signals: randconfig for each symbol, module and built-in builds, dependency closure checks, and DT binding tests for the corresponding compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/stm/Makefile

Purpose: maps STM32 ASoC Kconfig symbols to controller objects.

Important entries: SAI builds both `stm32_sai_sub.o` as `snd-soc-stm32-sai-sub.o` and `stm32_sai.o` as `snd-soc-stm32-sai.o`. I2S builds `snd-soc-stm32-i2s.o`. SPDIFRX builds `snd-soc-stm32-spdifrx.o`. DFSDM builds `stm32_adfsdm.o`.

Control flow and integration: enabled symbols produce standalone modules/objects per controller. SAI is split into parent controller and sub-block implementations.

State and persistence: no runtime state. The object layout controls module boundaries and autoload names.

Dependencies: sibling Kconfig and top-level ASoC build traversal.

Risks: SAI uses two objects under one Kconfig symbol; both must be present for a functional SAI hierarchy. The Makefile includes SPDIFRX and SAI sub files outside this research subset, so changes to those files can affect build of researched symbols.

Test signals: build each symbol as `m` and `y`, verify module names and dependencies, and ensure SAI parent/sub-device autoload works with device-tree population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_adfsdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_adfsdm.c

Purpose: bridges STM32 DFSDM IIO ADC data into an ASoC capture DAI/PCM platform, mainly for digital microphone capture.

Important APIs and types: `struct stm32_adfsdm_priv` owns a DAI driver copy, substream pointer, IIO channel/callback buffer state, ALSA PCM buffer pointer/position, and a mutex for IIO active state. DAI ops implement shutdown, prepare, and set_sysclk. Component ops implement PCM open/close/hw_params/trigger/pointer/pcm_new. `stm32_afsdm_pcm_cb()` is the data path callback from DFSDM/IIO into the ALSA ring buffer.

Control flow: probe registers the DAI component, obtains all IIO channels, obtains an IIO callback buffer with a dummy callback, registers cleanup, manually initializes/adds a second component for PCM platform ops, and enables runtime PM. PCM open sets hardware constraints and stores the substream. hw_params stores the DMA-area pointer and sets IIO watermark to ALSA period size. DAI prepare stops any active callback, writes sample frequency to the IIO channel, and starts callbacks. Trigger START/RESUME resets position and registers the optimized DFSDM buffer callback; STOP/SUSPEND releases it. The callback copies 32-bit DFSDM samples directly for S32 or decimates 32-to-16 for S16, wraps in the ALSA buffer, advances position, and calls `snd_pcm_period_elapsed()` when a period boundary is crossed.

State and persistence: `iio_active` is protected by a mutex in DAI prepare/shutdown. `pos` and `pcm_buff` are stream state used by callback and pointer without explicit locking. The IIO channel persists for device lifetime and is released via devm action.

Dependencies and integration points: compatible `st,stm32h7-dfsdm-dai`, IIO consumer and STM32 DFSDM ADC APIs, IIO callback buffers, ASoC DAI/component APIs, managed PCM buffers, and DMIC codec selection from Kconfig.

Risks: callback position updates can race with pointer/trigger stop unless upper layers serialize sufficiently. `stm32_memcpy_32to16()` treats source as `u16 *` and skips every other halfword, so endian/sample alignment assumptions are critical. Period elapsed detection compares `old_pos % period_size < size`, using original callback `size` rather than adjusted `src_size` in S16 mode. Manual component allocation/addition is less common than devm registration and remove unregisters all components for the device.

Test signals: capture S16 and S32 at 8 kHz through 192 kHz, period sizes near max and wrap boundaries, trigger stop while callback is active, sample-rate programming failures from IIO, set_sysclk `spi_clk_freq` writes, and period-elapsed cadence under ftrace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_adfsdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_i2s.c

Purpose: STM32 SPI/I2S block ASoC DAI driver with full-duplex playback/capture, dmaengine PCM, regmap-backed MMIO, optional MCLK provider, and clock-parent management for 8 kHz and 11.025 kHz rate families.

Important APIs and types: `struct stm32_i2s_data` stores regmap, clocks, DMA data, substream, MMIO/physical address, full-duplex and IRQ locks, MCLK/divider state, format/master flags, refcount, and clock-rate strategy hooks. `struct stm32_i2s_conf` supplies regmap config and optional parent-clock lookup. DAI ops implement probe, set_sysclk, set_fmt, startup, hw_params, trigger, and shutdown. MCLK `clk_ops` derive and program I2S prescalers.

Control flow: probe parses DT, maps MMIO, gets clocks, optional reset and IRQ, optionally registers an MCLK provider, initializes regmap, registers dmaengine PCM and ASoC component, enables I2S mode, checks hardware capability/version, and enables PM. `set_fmt()` programs protocol, inversion, and master/slave mode. `set_sysclk()` handles MCLK output in master mode, requesting exclusive clock rates and enabling MCK output. `hw_params()` configures data length/channel length/master/slave mode and, in master mode, calculates/programs clock dividers. Trigger start enables DMA bits, SPE/CSTART, clears interrupts, increments full-duplex refcount, and enables underrun/overrun/frame-error interrupts. Trigger stop disables the stream interrupt, decrements refcount, and only disables I2S/DMA when the last full-duplex stream stops. IRQ clears active flags and stops the stream on overrun/underrun.

State and persistence: regmap cache is used over system sleep. `refcount` protects full-duplex shared hardware enable. `i2s_clk_flg` tracks exclusive parent clock ownership. `mclk_rate`, `div`, `odd`, and `divider` store prescaler state.

Dependencies and integration points: compatibles `st,stm32h7-i2s` and `st,stm32mp25-i2s`, clocks `pclk`, `i2sclk`, optional `x8k`/`x11k`, optional `#clock-cells`, reset, IRQ, dmaengine PCM, regmap MMIO, and ASoC DAI machine-driver format/sysclk calls.

Risks: stop paths use `regmap_update_bits(..., mask, (unsigned int)~mask)` when clearing interrupt bits; update_bits masks the value, but this is non-obvious and fragile. In full-duplex, one `substream` pointer is shared for IRQ XRUN reporting, so the last startup wins. Clock exclusivity must be released on all failure/shutdown paths. MCLK name construction strips after `_` and may collide. Slave mode still uses shared full-duplex mode settings.

Test signals: master/slave I2S, left/right justified and DSP_A formats, 16/32-bit, playback/capture/full-duplex, MCLK provider consumers, 8k and 11.025k families, clock failure unwinding, IRQ overrun/underrun, suspend/resume regcache sync, and repeated start/stop refcount balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.c -->
# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.c

Purpose: STM32 SAI parent platform driver. It owns the common SAI global register block, discovers SoC capabilities, configures synchronization between SAI sub-blocks, and populates child platform devices that implement the audio sub-block DAIs.

Important APIs and types: uses `struct stm32_sai_data` and `struct stm32_sai_conf` from `stm32_sai.h`. SoC configs describe version, FIFO size, S/PDIF/PDM support, no-DMA-burst behavior, and optional parent-clock lookup. Core helpers include `stm32_sai_pclk_enable/disable()`, sync client/provider configuration, `stm32_sai_set_sync()`, parent clock acquisition, probe, suspend, and resume.

Control flow: probe allocates state, maps MMIO, copies match-data config, gets bus clock for non-F4 variants, optionally gets `x8k` and `x11k` parent clocks, gets IRQ and optional reset, enables pclk to read hardware capability registers, overrides FIFO/SPDIF/version fields when hardware ID matches, disables pclk, stores `set_sync`, and calls `devm_of_platform_populate()` to create child subdevices. Sync configuration locates the provider platform device from a phandle node, writes client `SYNCIN`, then writes provider `SYNCOUT` while rejecting conflicting provider assignments. Suspend saves the global control register and selects sleep pins; resume restores it and selects default pins.

State and persistence: parent state includes base, pclk, optional parent clocks, IRQ, SoC config, saved global control register, and sync callback. Sub-block runtime state lives in `stm32_sai_sub.c`, outside this subset. The GCR is saved/restored across system sleep.

Dependencies and integration points: compatibles `st,stm32f4-sai`, `st,stm32h7-sai`, `st,stm32mp25-sai`; clock names `pclk`, `x8k`, `x11k`; optional reset; pinctrl sleep/default; child nodes populated by OF; and synchronization contracts with SAI sub-block drivers.

Risks: F4 config does not require pclk, but probe unconditionally calls `clk_prepare_enable(sai->pclk)` later; verify `pclk` is valid or optional for F4 in the shared header expectations. Sync provider lookup depends on provider driver data already being set, creating probe-order sensitivity. A provider already set to A or B rejects conflicting sync but does not reference count clients. Suspend assumes pclk can be enabled during system sleep callbacks.

Test signals: boot all supported compatibles, child population, hardware capability register detection, sync provider/client phandle order, conflicting sync output requests, suspend/resume GCR and pinctrl restoration, and parent clock acquisition for 8k/11k families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.c -->
