# subset-b-006419 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-pcm-whistler.c -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-pcm-whistler.c

Purpose: Broadcom BCM63xx Whistler ASoC PCM platform support. It exposes ALSA PCM operations for the companion I2S controller, allocates a fixed write-combined DMA buffer, feeds I2S descriptor FIFOs, and reports period progress from a shared I2S DMA interrupt.

Important APIs, types, and functions: `struct i2s_dma_desc` tracks the current DMA area/address/length programmed into hardware; `struct bcm63xx_runtime_data` tracks the current and next DMA addresses for ALSA pointer reporting. `bcm63xx_pcm_open`, `close`, `hw_params`, `hw_free`, `prepare`, `trigger`, and `pointer` populate `struct snd_soc_component_driver bcm63xx_soc_platform`. `i2s_dma_isr()` handles both RX and TX descriptor completion paths. `bcm63xx_soc_pcm_new()` configures DMA masks, stores playback/capture substreams in `struct bcm_i2s_priv`, and sets the fixed buffer. `bcm63xx_soc_platform_probe()` requests the platform IRQ and registers the component; remove is a no-op.

Control flow: open installs the S32_LE-only hardware constraints, enforces 32-byte period/buffer alignment and integer periods, then allocates runtime-private state. `hw_params` allocates a per-substream descriptor and attaches it as CPU DAI DMA data. `prepare` seeds descriptor length/address registers for TX or RX. `trigger` enables or disables I2S IRQ and stream-enable bits. On interrupt, RX/TX status is read, completed OFF descriptors update `dma_addr_next`, available IFF depth is refilled one period at a time with wraparound, ALSA is notified with `snd_pcm_period_elapsed()`, and interrupt bits are cleared.

State and persistence: persistent runtime state is in ALSA runtime private data, CPU DAI DMA data, and `bcm_i2s_priv` substream pointers. Hardware state lives in I2S regmap registers such as IRQ enables, stream config, and descriptor FIFO address/length registers. No on-disk state exists.

Dependencies and integration: depends on ALSA SoC component callbacks, `bcm63xx-i2s.h` register definitions and `struct bcm_i2s_priv`, Linux regmap, platform IRQs, OF DMA configuration, and coherent DMA mask setup. It is integrated by the BCM63xx I2S driver calling the exported probe/remove helpers.

Risks: ISR assumes `play_substream` or `capture_substream` is valid when the matching interrupt is set; stale or spurious interrupts could dereference NULL. The pointer uses the last completed descriptor address, so underrun/overrun behavior depends on hardware status accuracy. `GFP_NOWAIT` in `hw_params` can fail under memory pressure. Only S32_LE is advertised, which must match the I2S DAI and machine driver. There is no explicit synchronization around descriptor fields shared between trigger/ISR/pointer paths.

Test signals: build with the BCM63xx Whistler audio config enabled; boot/probe should request `i2s_dma` and register a PCM component. Playback and capture tests should verify 32-byte-aligned periods, wraparound at 128 KiB, monotonic ALSA pointers, period interrupts, STOP/SUSPEND/PAUSE cleanup, and no IRQs after stream stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-pcm-whistler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-pcm.c

Purpose: Cygnus ASoC PCM platform driver for Broadcom Cygnus audio. It maps ALSA PCM buffers onto hardware source/destination ring-buffer registers and uses ESR/R5 interrupt status to advance periods for playback and capture.

Important APIs, types, and functions: `cygnus_pcm_hw` defines S16/S32 interleaved mmap PCM constraints with 256-byte period granularity. Ring-buffer register selection is done through `configure_ringbuf_regs()` and `RINGBUF_REG_PLAYBACK/CAPTURE` macros from `cygnus-ssp.h`. `ringbuf_set_initial()` programs start/end/free/full marks and initial read/write pointers. `enable_intr()` and `disable_intr()` manage ESR masks. `cygnus_dma_irq()`, `handle_playback_irq()`, and `handle_capture_irq()` dispatch ESR status. `cygnus_pcm_open`, `close`, `prepare`, `trigger`, `pointer`, and `cygnus_dma_new` form `cygnus_soc_platform`. `cygnus_soc_platform_register()` requests the shared IRQ and registers the component.

Control flow: the SSP DAI startup sets a `cygnus_aio_port` as DMA data; PCM open fetches it, applies hardware constraints, and stores the substream on the port. Prepare maps the port to a hardware ring buffer, computes buffer and period sizes, and programs base/end/mark and initial pointers. Trigger START/RESUME unmasks ESR interrupts; STOP/SUSPEND masks them. The IRQ handler reads R5 status, handles playback ESR0/1/3 and capture ESR2/4, calls `snd_pcm_period_elapsed()` on freemark/fullmark events, adjusts ring-buffer pointers to full or empty, clears ESR bits, and rearms mark logic. Pointer reads the hardware read pointer for playback or write pointer for capture and converts the offset from base to frames.

State and persistence: `cygnus_aio_port` keeps substream pointers and selected ring-buffer register offsets. Ring-buffer base/end/read/write/mark registers and ESR mask/status registers are the active state. DMA buffers are managed by ALSA with a 32-bit DMA mask. There is no persistence beyond device runtime.

Dependencies and integration: integrated by `cygnus-ssp.c`, which passes `struct cygnus_audio` to `cygnus_soc_platform_register()`. Uses `writel/readl` MMIO, `snd_pcm_set_managed_buffer_all`, ALSA component PCM ops, and shared IRQ handling.

Risks: IRQ handlers call `cygnus_pcm_period_elapsed()` using per-port substream pointers and do not visibly guard against NULL if an enabled ESR bit arrives after close/disable. The port-to-ring-buffer mapping skips ring buffers in pairs and must stay aligned with hardware channel layout. Pointer arithmetic masks the MSB but otherwise trusts hardware addresses. Interrupt mark programming assumes periods are multiples of 256 bytes.

Test signals: validate playback and capture with each TDM port and SPDIF playback, period sizes at 256-byte boundaries, ESR underflow/overflow debug paths, pointer movement, stream close clearing substream pointers, and no duplicate/lost period notifications during START/STOP and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-ssp.c -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-ssp.c

Purpose: Broadcom Cygnus SSP/I2S/SPDIF CPU DAI driver. It parses device-tree child ports, configures audio fabric, source/destination channels, I2S/SPDIF stream registers, PLL-derived audio clocks, DAI format, TDM slots, stream enable/disable, and registers the Cygnus PCM platform.

Important APIs, types, and functions: register offset and bit macros describe audio fabric, I2S input/output, SPDIF, PLL, and pin-output-enable blocks. `pll_predef_mclk[]` maps supported MCLK frequencies to PLL channels. `audio_ssp_init_portregs()` initializes source/destination routing and pins. `audio_ssp_in_enable/disable()` and `audio_ssp_out_enable/disable()` start and stop capture/playback paths. `pll_configure_mclk()` and `cygnus_ssp_set_clocks()` program clock channels and MCLK/BCLK ratios. DAI callbacks include `cygnus_ssp_startup`, `shutdown`, `hw_params`, `set_sysclk`, `set_fmt`, `trigger`, and `cygnus_set_dai_tdm_slot`. `cygnus_ssp_set_custom_fsync_width()` is exported for machine drivers. Probe parses child nodes and registers active DAIs plus the PCM platform.

Control flow: probe allocates `struct cygnus_audio`, maps `aud` and `i2s_in`, tristates controllable pins, validates 1..4 child ports, parses each available child `reg`, fills `cygnus_aio_port`, initializes port registers, registers the component with active DAIs, obtains IRQ and clocks, then calls `cygnus_soc_platform_register()`. Startup attaches the port as DMA data and applies rate constraints. Machine-driver format/sysclk/TDM calls select master/slave, I2S/DSP mode, frame width, slots, MCLK source, and bit clocks. Runtime trigger toggles hardware stream blocks and active-port count. Suspend/resume disables/re-enables selected PLL clocks for active non-slave DAIs.

State and persistence: `struct cygnus_audio` persists as platform drvdata and owns portinfo, MMIO bases, clocks, IRQ, active port count, and VCO rate. Each `cygnus_aio_port` stores mode, slave/master state, clocks, frame bits, stream bitmap, fsync width, register offsets, substreams, and clock trace flags. Hardware configuration is held in MMIO registers. No nonvolatile persistence.

Dependencies and integration: depends on OF child nodes using `reg` values 0..3, named resources `aud` and `i2s_in`, clocks `ch0_audio`..`ch2_audio`, ALSA SoC DAI/component APIs, Linux clk framework, and `cygnus-pcm.c` registration helpers. Exports custom fsync width for board-specific machine code.

Risks: `active_ports` is incremented/decremented without checks and can drift on repeated or failed trigger paths. `audio_ssp_out_enable()` return values are ignored by trigger. Clock enable tracking can enable the same PLL channel for capture and playback and relies on matched shutdown/suspend paths. `cygnus_ssp_set_fmt()` appears to retain bits with `cfg & UPDATE_MASK`, so mask semantics must be verified against intended "retain vs update" behavior. Unsupported MCLK/BCLK ratios reject hw_params. Child-node parsing treats all available children as active and does not implement the documented disabled return value.

Test signals: probe with DT ports 0, 1, 2, and 3; verify DAI names and resource/clock failures. Exercise I2S, DSP_A, DSP_B, master/slave, valid and invalid TDM slot masks/frame sizes, all predefined MCLKs, invalid MCLK/BCLK ratios, playback/capture triggers, SPDIF playback, custom fsync width, and CONFIG_PM_SLEEP suspend/resume with active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-ssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-ssp.h -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-ssp.h

Purpose: shared Cygnus audio definitions for the SSP CPU DAI driver and PCM platform. It defines port limits, operating modes, ring-buffer register descriptors, per-port state, global audio device state, and exported helper prototypes.

Important APIs, types, and functions: `CYGNUS_MAX_PLAYBACK_PORTS`, `CYGNUS_MAX_CAPTURE_PORTS`, `CYGNUS_MAX_I2S_PORTS`, and `CYGNUS_MAX_PORTS` define the three I2S/TDM ports plus one playback-only SPDIF port. `struct ringbuf_regs` describes MMIO offsets and runtime period/buffer metadata for a source or destination ring buffer. `RINGBUF_REG_PLAYBACK()` and `RINGBUF_REG_CAPTURE()` construct those descriptors from register-offset macros supplied by `cygnus-pcm.c`. `struct cygnus_ssp_regs` bundles per-port I2S and buffer-fabric offsets. `struct cygnus_track_clk`, `struct cygnus_aio_port`, and `struct cygnus_audio` hold stream, clock, MMIO, and substream state. Prototypes expose custom fsync width and PCM registration helpers.

Control flow: the header has no executable control flow; it is the contract used by `cygnus-ssp.c` to populate ports and by `cygnus-pcm.c` to look up ring-buffer and substream data.

State and persistence: all state is in in-memory structs attached to the platform device. `cygnus_aio_port` is the per-DAI state object; `cygnus_audio` is the aggregate device object. No persistent storage exists.

Dependencies and integration: requires the C files to define ring-buffer offset macros before using the ring-buffer constructor macros. Its exported prototypes are consumed inside the Broadcom Cygnus audio driver set and by possible machine drivers.

Risks: `CYGNUS_AUIDO_MAX_NUM_CLKS` is misspelled but consistently used. The header declares `cygnus_ssp_set_custom_fsync_width()` twice. Comments contain minor spelling errors but do not alter behavior. Structural contracts are tightly coupled to hardware register layout and array bounds.

Test signals: compile both `cygnus-pcm.c` and `cygnus-ssp.c` together with sparse/W=1 to catch duplicate prototype or type issues; run DT configurations for all allowed port counts and validate array bounds for `portinfo` and `audio_clk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-ssp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/cirrus/Kconfig

Purpose: Kconfig menu for Cirrus Logic EP93xx ASoC support. It gates the EP93xx platform PCM layer, the EP93xx I2S controller, and an optional watchdog workaround for transmit FIFO underflow.

Important APIs, types, and functions: declares `SND_EP93XX_SOC`, `SND_EP93XX_SOC_I2S`, and `SND_EP93XX_SOC_I2S_WATCHDOG`. `SND_EP93XX_SOC` is tristate, depends on `ARCH_EP93XX || COMPILE_TEST`, and selects `SND_SOC_GENERIC_DMAENGINE_PCM`. `SND_EP93XX_SOC_I2S` depends on the platform option. The watchdog is a bool under `if SND_EP93XX_SOC_I2S`, defaults to yes, and documents a hardware underflow workaround.

Control flow: Kconfig selection flows from platform support to I2S support to the optional watchdog. Enabling watchdog compiles IRQ-based recovery code in `ep93xx-i2s.c`.

State and persistence: build-time configuration only; no runtime state.

Dependencies and integration: integrates with the kernel sound/soc Kconfig tree and the local Cirrus Makefile. `select SND_SOC_GENERIC_DMAENGINE_PCM` matches the `ep93xx-pcm.c` use of dmaengine PCM registration.

Risks: watchdog defaults to enabled because the hardware issue is severe, so platform descriptions must provide a valid IRQ when the I2S controller is enabled. Disabling watchdog may allow byte-shifted streams after FIFO underflow.

Test signals: run Kconfig builds for `ARCH_EP93XX`, `COMPILE_TEST`, module and built-in combinations, with watchdog enabled and disabled. Confirm Makefile object selection matches the chosen symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/cirrus/Makefile

Purpose: build glue for Cirrus EP93xx ASoC objects. It maps Kconfig symbols to the PCM platform object and I2S controller object.

Important APIs, types, and functions: `snd-soc-ep93xx-y := ep93xx-pcm.o` builds the PCM helper module; `snd-soc-ep93xx-i2s-y := ep93xx-i2s.o` builds the I2S controller module. `obj-$(CONFIG_SND_EP93XX_SOC)` and `obj-$(CONFIG_SND_EP93XX_SOC_I2S)` add those modules to the kernel build.

Control flow: Kbuild first expands composite object variables, then links the selected `snd-soc-ep93xx.o` and `snd-soc-ep93xx-i2s.o` depending on configuration.

State and persistence: build-time only.

Dependencies and integration: depends on the local Kconfig symbols and source filenames. The I2S object calls the exported PCM registration function from `ep93xx-pcm.c`, so module dependency/order must keep `SND_EP93XX_SOC` available when I2S is enabled.

Risks: object names must remain synchronized with Kconfig and exported symbol names. Since `SND_EP93XX_SOC_I2S` depends on `SND_EP93XX_SOC`, broken dependency edits could cause unresolved `devm_ep93xx_pcm_platform_register`.

Test signals: `make sound/soc/cirrus/` for built-in and module configs, and `modpost` should show the I2S module depending on the PCM helper when modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-i2s.c

Purpose: EP93xx I2S CPU DAI driver. It manages I2S MMIO registers, mclk/sclk/lrclk clocks, FIFO enable/disable, optional IRQ watchdog recovery, DAI format and hw_params programming, and registration of the EP93xx dmaengine PCM platform.

Important APIs, types, and functions: `struct ep93xx_i2s_info` owns three clocks, MMIO base, and dmaengine DAI data. `ep93xx_i2s_enable()` and `disable()` gate clocks and TX/RX FIFOs. `ep93xx_i2s_interrupt()` resets and refills TX FIFO on underflow when the watchdog option is enabled. DAI ops include `ep93xx_i2s_dai_probe`, `startup`, `shutdown`, `set_dai_fmt`, `hw_params`, and `set_sysclk`. Component PM hooks disable/enable active streams. Probe maps registers, optionally requests IRQ, obtains clocks, registers the DAI/component, and registers PCM.

Control flow: startup enables shared clocks and global I2S if both FIFOs were previously disabled, then enables the requested FIFO and optional TX IRQs. Format setup writes RX/TX clock config and line-control registers for I2S/left/right justified, master/slave, and polarity modes. Hw_params chooses 16/24/32-bit word-length register values, computes clock divisors from MCLK and sample rate, and sets SCLK/LRCLK rates. Shutdown disables IRQs and FIFO, and if both directions are off disables global I2S and clocks.

State and persistence: runtime state is `ep93xx_i2s_info` in device drvdata plus hardware register state. Clock rates persist in clk framework state while the device is active. No storage outside runtime.

Dependencies and integration: uses ALSA SoC DAI/component APIs, dmaengine PCM support via `devm_ep93xx_pcm_platform_register()`, OF compatible `cirrus,ep9301-i2s`, platform MMIO/IRQ resources, and Cirrus EP93xx clock names `mclk`, `sclk`, `lrclk`.

Risks: DAI advertises only S32_LE via `EP93XX_I2S_FORMATS`, while hw_params has code for S16/S24/S32; that mismatch may be intentional to force 32-bit slots but should be tested. Probe uses manual `clk_get/clk_put` instead of devm clocks, so all error/remove paths must stay correct. Watchdog-enabled builds require an IRQ resource. Resume enables both playback and capture when component active, regardless of which streams were active before suspend.

Test signals: probe with and without watchdog, playback/capture at 8 kHz through 192 kHz, all supported DAI formats/polarities, sysclk changes, underflow interrupt recovery, suspend/resume with one or both directions active, and module unload to verify clocks are put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.c

Purpose: EP93xx ALSA SoC PCM platform helper built on generic dmaengine PCM. It defines EP93xx PCM hardware limits and exports a devm registration function for CPU DAI drivers.

Important APIs, types, and functions: `ep93xx_pcm_hardware` advertises mmap, interleaved, block-transfer PCM with 128 KiB max buffer, 32..32768 byte periods, 1..32 periods, and FIFO size 32. `ep93xx_dmaengine_pcm_config` references those limits and preallocates 128 KiB. `devm_ep93xx_pcm_platform_register()` wraps `devm_snd_dmaengine_pcm_register()` and is exported GPL.

Control flow: the only runtime function is called by an EP93xx controller probe, registers a managed dmaengine PCM component for the device, and lets generic dmaengine callbacks handle PCM operation.

State and persistence: static hardware/config structs plus managed ALSA/dmaengine allocations. No driver-private persistent runtime state.

Dependencies and integration: depends on Linux dmaengine and ALSA generic dmaengine PCM. Used by `ep93xx-i2s.c` after DAI registration.

Risks: correctness depends on DAI drivers supplying valid `snd_dmaengine_dai_dma_data`. The static limits must match EP93xx DMA capabilities. The exported helper can create module dependencies if Kconfig/Makefile constraints are weakened.

Test signals: compile as built-in and module, call from EP93xx I2S probe, run playback/capture DMA with minimum and maximum period sizes, and verify preallocated buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.h

Purpose: local Cirrus EP93xx PCM header exposing the dmaengine PCM registration helper.

Important APIs, types, and functions: declares `int devm_ep93xx_pcm_platform_register(struct device *dev);` with an include guard.

Control flow: none; compile-time declaration only.

State and persistence: none.

Dependencies and integration: included by `ep93xx-pcm.c` and `ep93xx-i2s.c`. It relies on callers having `struct device` visible through included kernel headers.

Risks: if included without a prior `struct device` declaration, future cleanup could require an explicit forward declaration. Otherwise the header is intentionally minimal.

Test signals: compile `ep93xx-i2s.c` and `ep93xx-pcm.c` together and as modules to verify exported symbol and prototype consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.c

Purpose: ASoC codec driver for Marvell 88PM860x PMIC audio. It exposes PCM and I2S codec DAIs, mixer controls, DAPM widgets/routes, bias sequencing, mute and hw_params programming, and headset/microphone/short jack detection through the parent MFD IRQ resources.

Important APIs, types, and functions: `struct pm860x_priv` stores sysclk/dir/filter, component, I2C/regmap handles, MFD chip, detection state, IRQs, and names. `struct pm860x_det` stores jack pointers and report masks. Custom controls include sidetone get/put through `st_table` and inverted output gain handlers. DAPM event handlers `pm860x_rsync_event()` and `pm860x_dac_event()` coordinate RSYNC and DAC mute/modulator bits. DAI ops cover mute, PCM/I2S hw_params, set_fmt, and set_sysclk. Exported `pm860x_hs_jack_detect()` and `pm860x_mic_jack_detect()` configure detection and synchronize jack state. Probe registers component, DAIs, and IRQ handlers.

Control flow: platform probe obtains the parent `pm860x_chip`, selects primary or companion I2C/regmap, reads four IRQ resources, and registers the component with two DAIs. Component probe initializes the regmap and requests four threaded IRQs. Bias STANDBY powers the audio PLL/section and reset sequence; OFF clears those bits. DAI hw_params writes word length and rate codes into PCM or I2S interface registers. Set_fmt validates master/slave direction against `pm860x->dir` and supports I2S mode. Jack IRQ handling reads status and shorts registers, builds headphone/mic/hook/short reports, and calls `snd_soc_jack_report()`.

State and persistence: runtime state is in `pm860x_priv`, ASoC regmap cache/registers, DAPM power state, IRQ registration, and jack report masks. Hardware state persists while the PMIC is powered but there is no filesystem persistence.

Dependencies and integration: depends on the 88PM860x MFD core (`linux/mfd/88pm860x.h`), PM860x register helpers, ALSA SoC component/DAI/DAPM/jack APIs, regmap, platform IRQ resources, and Kconfig symbol `SND_SOC_88PM860X`.

Risks: `pm860x_set_dai_sysclk()` only accepts `PM860X_CLK_DIR_OUT`, while I2S set_fmt has a path for clock input; machine drivers must call sysclk consistently or set_fmt fails. PCM supports only 8/16/32/48 kHz and I2S only common 8..48 kHz rates. Component probe uses non-devm `request_threaded_irq()` and frees on remove; partial failure cleanup is present. Jack handler only reports when a bit is present, so absence transitions rely on `snd_soc_jack_report()` masks during sync paths and should be tested. Register writes mix regmap via component and MFD helper I2C writes.

Test signals: build with `MFD_88PM860X`; probe via MFD child with four IRQ resources; enumerate two DAIs and mixer controls; run PCM/I2S playback/capture at accepted and rejected rates/widths; verify DAPM power sequencing, mute/RSYNC behavior, bias transitions, headset/mic/hook/short IRQ reporting, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.h

Purpose: register and public-helper header for the 88PM860x ASoC codec driver. It provides symbolic register addresses, clock direction constants, detection mask constants, and jack-detection helper prototypes for machine drivers.

Important APIs, types, and functions: defines audio interface, gain, ADC/DAC, analog, supply, calibration, and input-select register addresses from `PM860X_PCM_IFACE_1` through `PM860X_I2S_IFACE_5`, plus `PM860X_SHORTS` and PLL adjustment registers. Defines `PM860X_CLK_DIR_IN/OUT`, detection bits `PM860X_DET_HEADSET`, `PM860X_DET_MIC`, `PM860X_DET_HOOK`, `PM860X_SHORT_HEADSET`, `PM860X_SHORT_LINEOUT`, and `PM860X_DET_MASK`. Declares `pm860x_hs_jack_detect()` and `pm860x_mic_jack_detect()`.

Control flow: none; the header is a compile-time contract.

State and persistence: no state in the header. Constants map to hardware state managed by `88pm860x-codec.c`.

Dependencies and integration: included by codec implementation and by board/machine drivers that need jack detection helpers or PM860x constants. Depends on ALSA `struct snd_soc_component` and `struct snd_soc_jack` declarations being visible at use sites.

Risks: the include guard name starts with digits after the double underscore prefix, which is tolerated by preprocessors but is not a style ideal. Register constants must remain synchronized with PMIC documentation and MFD regmap coverage.

Test signals: compile codec and any machine driver using jack helpers; verify exported symbols resolve and detection masks match ALSA jack report expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/Kconfig

Purpose: central Kconfig catalog for ASoC codec drivers. It defines shared bus helper symbols, an all-codecs compile-test option, individual codec symbols, dependencies, selects, defaults, and nested options such as KUnit/debug/test hooks.

Important APIs, types, and functions: `SND_SOC_I2C_AND_SPI` resolves mixed I2C/SPI tristate availability. `SND_SOC_ALL_CODECS` depends on `COMPILE_TEST` and `imply`s a broad list of codec symbols for build coverage without requiring machine drivers. The researched `SND_SOC_88PM860X` is a hidden tristate depending on `MFD_88PM860X`. The file also defines many vendor codec options such as Cirrus/Wolfson, Analog Devices, Realtek, Qualcomm WCD, TI, Nuvoton, MediaTek, and SoundWire variants. Some options select support libraries such as `FW_CS_DSP`, `SND_SOC_COMPRESS`, `REGMAP`, bus-specific children, or KUnit tests.

Control flow: Kconfig dependency resolution determines which codec drivers can be built. Users normally select machine drivers, while `SND_SOC_ALL_CODECS` implies codecs for compile testing. Hidden aggregate symbols such as `SND_SOC_ARIZONA`, `SND_SOC_WM_HUBS`, and library/test symbols follow defaults from concrete codec selections.

State and persistence: build-time configuration only.

Dependencies and integration: consumed by the parent ASoC Kconfig tree and paired with `sound/soc/codecs/Makefile`. Its symbols directly control the object mappings in that Makefile, including `CONFIG_SND_SOC_88PM860X` to `snd-soc-88pm860x.o`.

Risks: large files like this are prone to drift between symbol names and Makefile object mappings. `imply` under all-codecs does not force bus dependencies, so coverage still depends on I2C/SPI/SoundWire/MFD prerequisites. Hidden symbols can be difficult to discover without a machine driver or compile-test option.

Test signals: run `allmodconfig`, `allyesconfig`, targeted `COMPILE_TEST`, and specific codec configs; verify there are no unmet direct dependencies, circular selects, or objects missing from Makefile mappings. For this subset, enable `MFD_88PM860X` and confirm `SND_SOC_88PM860X` can produce `88pm860x-codec.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/Makefile

Purpose: Kbuild mapping for the ASoC codec directory. It defines composite object names for codec drivers and maps `CONFIG_SND_SOC_*` symbols to the corresponding `snd-soc-*` objects.

Important APIs, types, and functions: the researched `snd-soc-88pm860x-y := 88pm860x-codec.o` and `obj-$(CONFIG_SND_SOC_88PM860X) += snd-soc-88pm860x.o` connect the 88PM860x Kconfig symbol to its codec source. The file contains many one-to-one mappings and several composites, for example multi-file codec cores, bus wrappers, shared libraries, SoundWire variants, and test modules.

Control flow: Kbuild expands `snd-soc-*-y` composite variables, then includes objects whose `obj-$(CONFIG_...)` expression is non-empty. This allows codec cores, bus frontends, helper libraries, and test objects to be compiled independently according to Kconfig.

State and persistence: build-time only.

Dependencies and integration: tightly coupled to `codecs/Kconfig`, source filenames, module aliases, and exported symbols. Composite libraries such as `snd-soc-aw88395-lib`, `snd-soc-cs35l56-shared`, `snd-soc-wm-adsp`, and bus-specific wrappers must align with symbol dependencies.

Risks: duplicate or stale mappings can cause missing modules, duplicate object linkage, or unresolved symbols. Some sections contain separate mappings for core and transport-specific modules, so Kconfig changes must preserve dependency order. Large repetitive mappings increase review risk when adding/removing codecs.

Test signals: build `sound/soc/codecs/` under `allmodconfig` and targeted single-codec configs, run `modpost` for unresolved exports, and verify new codec additions update both the composite variable and `obj-$(CONFIG_...)` line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/Makefile -->
