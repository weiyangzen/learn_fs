# Research Group: subset-b-006381

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_synth.c -->
# sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_synth.c

Purpose: Implements the ALSA hwdep-facing control path for Turtle Beach WaveFront ICS2115 wavetable synth hardware. It probes raw/running firmware state, optionally downloads `wavefront.os`, resets/configures the board, exposes raw WaveFront commands through `WFCTL_WFCMD`, and loads samples, aliases, multisamples, patches, programs, and enhanced drum programs through `WFCTL_LOAD_SPP`.

Important APIs/types/functions: `snd_wavefront_cmd()` is the central command dispatcher around `wavefront_commands[]`; `wavefront_read()`, `wavefront_write()`, and `wavefront_wait()` perform status-polled port I/O. Patch/sample helpers include `wavefront_send_sample()`, `wavefront_send_alias()`, `wavefront_send_multisample()`, `wavefront_send_patch()`, `wavefront_send_program()`, `wavefront_load_patch()`, and `wavefront_synth_control()`. Lifecycle entry points are `snd_wavefront_detect()`, `snd_wavefront_start()`, `snd_wavefront_synth_open()`, `snd_wavefront_synth_release()`, and `snd_wavefront_synth_ioctl()`.

Control flow: Detection first tries `WFC_FIRMWARE_VERSION` and `WFC_HARDWARE_VERSION`; failure marks the board raw. Start optionally runs `wavefront_do_reset()`, which resets IRQ/control state, downloads firmware by request_firmware section records, waits for OS NOOP interrupts, sets MPU emulation and voice count, detects FX support, then inventories samples/programs/patches. IOCTL loading copies a small user header, copies the referenced payload header by type, and streams sample data to the 16-bit block port with a special final-word port and DMA-style ACK checks.

State and persistence: Runtime state is in `snd_wavefront_t`: sample/patch/program status arrays, free memory, firmware/hardware versions, interrupt counters, `israw`, `has_fx`, debug flags, and ROM write-protect policy. Hardware state persists on the card until reset; firmware is external and named by module parameter `ospath`.

Dependencies/integration: Uses Linux ISA port I/O, ALSA hwdep/card plumbing, `sound/snd_wavefront.h`, firmware loader, wait queues, module params, and sibling WaveFront MIDI/FX functions. Risks include many hardware protocol special cases, pointer casts into packed patch structures, user-pointer sample streaming, mutable command table `write_cnt` for multisample downloads, timeout tuning, and partial status-cache updates on failed hardware commands. Test signals are successful firmware probe/download logs, available DRAM report, correct `WFCTL_*` ioctl round trips, sample-memory exhaustion and ROM-protection errors, interrupt wait behavior, and playback-visible patch/program inventory consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wss/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/wss/Makefile

Purpose: Builds the ALSA Windows Sound System support library as `snd-wss-lib.o` from `wss_lib.o` when `CONFIG_SND_WSS_LIB` is enabled. It is a small kbuild aggregation file for ISA WSS-compatible codec support shared by multiple card drivers.

Important APIs/types/functions: No C APIs are defined here. The important kbuild variables are `snd-wss-lib-y := wss_lib.o`, which names the object list for the composite module, and `obj-$(CONFIG_SND_WSS_LIB) += snd-wss-lib.o`, which connects the module/library to the kernel configuration symbol.

Control flow: During kbuild, enabling `CONFIG_SND_WSS_LIB` causes `wss_lib.c` to compile into `wss_lib.o`, then link into the composite `snd-wss-lib.o` target. Other drivers can select or depend on the config symbol and link against the exported symbols in `wss_lib.c`.

State and persistence: The file carries no runtime state. Its build state determines whether WSS helper symbols such as `snd_wss_create()`, `snd_wss_pcm()`, `snd_wss_mixer()`, and codec register access helpers are available.

Dependencies/integration: Depends on the sound/isa/wss directory kbuild context and `CONFIG_SND_WSS_LIB`. Integration risk is mostly build-time: missed object membership or config mismatch would break downstream WSS-compatible card drivers at link or module-load time. Test signals are successful `CONFIG_SND_WSS_LIB` builds, presence of `snd-wss-lib.o`, and link success of drivers that call exported WSS library symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wss/wss_lib.c -->
# sources/distributed-fs/ceph-client/sound/isa/wss/wss_lib.c

Purpose: Provides the shared ALSA low-level library for CS4231/CS4232/CS4236/AD1848/AD1845/InterWave/OPTi WSS-compatible ISA codecs. It handles codec detection, register image management, MCE calibration sequencing, ISA DMA playback/capture, timer support, mixer controls, suspend/resume, and exported construction helpers.

Important APIs/types/functions: Exported APIs include `snd_wss_out()`, `snd_wss_in()`, `snd_cs4236_ext_out()`, `snd_cs4236_ext_in()`, `snd_wss_mce_up()`, `snd_wss_mce_down()`, `snd_wss_interrupt()`, `snd_wss_create()`, `snd_wss_pcm()`, `snd_wss_timer()`, `snd_wss_mixer()`, `snd_wss_chip_id()`, control helpers, and PCM ops access. Internal control centers are `snd_wss_probe()`, `snd_wss_init()`, `snd_wss_trigger()`, `snd_wss_playback_prepare()`, and `snd_wss_capture_prepare()`.

Control flow: Creation allocates a managed `struct snd_wss`, requests I/O regions/IRQ/DMA, detects hardware by probing codec registers, initializes the register image, and runs calibration. PCM open limits formats by hardware quirks and claims DMA, hw_params programs format/rate under MCE, prepare programs ISA DMA and period counts, trigger toggles playback/capture enable bits, and the IRQ handler acknowledges timer/playback/record interrupts and reports period elapsed.

State and persistence: `struct snd_wss` persists register mirrors in `image[]`/`eimage[]`, hardware type, port/IRQ/DMA resources, open mode, substream pointers, timer pointer, DMA sizes, callbacks, and PM hooks. Hardware registers are restored on resume from the image cache.

Dependencies/integration: Uses ALSA PCM/timer/control core, ISA DMA helpers, port I/O, IRQs, `sound/wss.h`, and devm resource management. Risks include hardware-specific calibration timing, shared/single DMA half-duplex constraints, register-image drift if direct I/O bypasses helpers, interrupt status quirks for AD1848, and many chip-specific format/rate limitations. Test signals include codec detection logs, PCM open/prepare/trigger/pointer behavior, timer ticks, mixer control read/write parity with image registers, suspend/resume restore, and simultaneous playback/capture on dual-DMA devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wss/wss_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/last.c -->
# sources/distributed-fs/ceph-client/sound/last.c

Purpose: Provides a late boot diagnostic for ALSA by printing the final list of registered sound cards. It is intentionally small and runs after normal sound-card initialization so boot logs show whether ALSA found cards.

Important APIs/types/functions: The single function `alsa_sound_last_init()` uses `snd_card_ref(idx)` and `snd_card_unref(card)` over `SNDRV_CARDS`, printing each card's `longname`. It is registered with `late_initcall_sync()`.

Control flow: At late initcall time, it prints `ALSA device list:`, iterates all card slots, references live cards, prints `#idx: longname`, unreferences them, and counts successes. If no card exists, it prints `No soundcards found.`

State and persistence: It owns no persistent state. It temporarily holds card references during enumeration and only emits kernel log messages.

Dependencies/integration: Depends on ALSA core card registry and Linux initcall ordering. Risks are minimal; the main behavioral dependency is that card `longname` fields must be initialized before this late call. Test signals are boot log lines with the expected card list or the no-card fallback, plus absence of leaked references or initcall failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/last.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/Kconfig -->
# sources/distributed-fs/ceph-client/sound/mips/Kconfig

Purpose: Defines the ALSA MIPS sound-device configuration menu and three platform driver symbols: SGI O2 Audio, SGI HAL2 Audio, and Nintendo 64 Audio.

Important APIs/types/functions: Kconfig symbols are `SND_MIPS`, `SND_SGI_O2`, `SND_SGI_HAL2`, and `SND_N64`. `SND_SGI_O2` depends on `SGI_IP32` and selects `SND_PCM`; `SND_SGI_HAL2` depends on `SGI_HAS_HAL2` and selects `SND_PCM`; `SND_N64` is built-in only, depends on `MACH_NINTENDO64 && SND=y`, and selects `SND_PCM`.

Control flow: `menuconfig SND_MIPS` appears under MIPS and defaults to `y`. If enabled, the nested config entries become visible and govern whether the corresponding objects in `sound/mips/Makefile` are built.

State and persistence: No runtime state exists here. Persistent effects are build configuration choices that decide driver availability and whether modules or built-ins are produced.

Dependencies/integration: Integrates architecture platform symbols with ALSA PCM support. Risks are build-coverage gaps if platform dependencies are wrong, especially `SND_N64` requiring built-in ALSA due its `bool` and `SND=y` dependency. Test signals are Kconfig visibility on the intended MIPS platforms, expected object selection in generated `.config`, and successful builds for enabled SGI/N64 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/Makefile -->
# sources/distributed-fs/ceph-client/sound/mips/Makefile

Purpose: Connects MIPS ALSA platform-driver config symbols to their objects. It also defines composite modules for SGI O2 and HAL2 audio.

Important APIs/types/functions: `snd-sgi-o2-y := sgio2audio.o ad1843.o` links the O2 platform driver with the shared AD1843 codec helper. `snd-sgi-hal2-y := hal2.o` defines the HAL2 module. `obj-$(CONFIG_SND_SGI_O2)`, `obj-$(CONFIG_SND_SGI_HAL2)`, and `obj-$(CONFIG_SND_N64)` select the final build targets.

Control flow: Kbuild evaluates each `obj-*` line from the active `.config`. SGI O2 builds as a composite module/built-in containing both `sgio2audio.o` and `ad1843.o`; N64 builds directly from `snd-n64.o`.

State and persistence: No runtime state. Build output shape matters because `sgio2audio.c` depends on functions implemented in `ad1843.c`.

Dependencies/integration: Integrates with `sound/mips/Kconfig` and top-level ALSA kbuild. Risks include link failures if `ad1843.o` is omitted from SGI O2, stale object names after source renames, or module naming mismatches. Test signals are successful `CONFIG_SND_SGI_O2`, `CONFIG_SND_SGI_HAL2`, and `CONFIG_SND_N64` builds and expected module/object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/ad1843.c -->
# sources/distributed-fs/ceph-client/sound/mips/ad1843.c

Purpose: Implements a low-level AD1843 codec helper used by SGI O2 audio. It abstracts AD1843 register bitfields, mixer gain formats, recording source selection, DAC/ADC format setup, shutdown stubs, and codec startup sequencing behind caller-provided register read/write callbacks.

Important APIs/types/functions: Public functions are `ad1843_get_gain_max()`, `ad1843_get_gain()`, `ad1843_set_gain()`, `ad1843_get_recsrc()`, `ad1843_set_recsrc()`, `ad1843_setup_dac()`, `ad1843_shutdown_dac()`, `ad1843_setup_adc()`, `ad1843_shutdown_adc()`, and `ad1843_init()`. Internal helpers `ad1843_read_bits()`, `ad1843_write_bits()`, `ad1843_read_multi()`, and `ad1843_write_multi()` operate on `struct ad1843_bitfield`.

Control flow: Callers initialize `struct snd_ad1843` with bus-specific read/write functions. `ad1843_init()` checks the INIT bit, selects serial clocking, powers converters up, waits for power-up completion, enables clocks, assigns DAC/ADC clock sources, enables analog/digital resources, zeroes gains, unmutes DACs, selects line-in capture, enables mic gain, and unmutes outputs. Mixer calls translate ALSA stereo values into AD1843 gain and mute bitfields.

State and persistence: The helper itself has no private allocation; state persists in hardware registers accessed through `snd_ad1843`. Gain IDs map to static descriptors, and all configuration persists in the codec until rewritten or reset.

Dependencies/integration: Depends on `sound/ad1843.h`, ALSA PCM format constants, jiffies/time helpers, and the caller's serialized bus access. Risks include trusting gain IDs as array indexes, format defaults silently falling through to AD1843 format 0, timeout behavior during power-up, and multi-field helpers assuming same-register groupings. Test signals are codec init success, mixer read-back matching writes, capture-source validation, DAC/ADC setup for S16_LE stereo at requested rates, and SGI O2 probe using this helper successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/ad1843.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/hal2.c -->
# sources/distributed-fs/ceph-client/sound/mips/hal2.c

Purpose: Implements the ALSA platform driver for SGI HAL2 audio on Indy/Indigo2-class MIPS systems. It drives HAL2 indirect registers, HPC3 PBUS DMA, playback/capture PCM streams, mixer controls, detection/reset, and ALSA card registration.

Important APIs/types/functions: Core structures are `struct snd_hal2`, `struct hal2_codec`, `struct hal2_pbus`, and `struct hal2_desc`. Hardware helpers include `hal2_i_read32()`, `hal2_i_write16()`, `hal2_i_write32()`, bit set/clear helpers, `hal2_compute_rate()`, `hal2_setup_dac()`, `hal2_setup_adc()`, start/stop functions, and DMA buffer allocation. ALSA callbacks are `hal2_*_open/close/prepare/trigger/pointer/ack`, `hal2_interrupt()`, `hal2_pcm_create()`, and `hal2_mixer_create()`.

Control flow: Probe creates a card, allocates/initializes `snd_hal2`, requests shared HPC DMA IRQ, maps HAL2 register blocks through HPC3 extregs, resets and detects the chip, binds PBUS DMA channels, programs PBUS timing, registers low-level cleanup, creates PCM and mixer controls, then registers the card. PCM open allocates noncoherent circular hardware buffers and descriptor rings; prepare computes Bresenham clock values and configures DAC/ADC FIFO/PBUS/HAL2 registers; trigger starts/stops PBUS DMA; ack copies between ALSA buffers and the hardware buffer using ALSA indirect helpers.

State and persistence: Runtime state sits in `snd_hal2`, per-codec indirect PCM tracking, DMA buffers/descriptors, PBUS control snapshots, sample-rate parameters, and current mixer values in HAL2 registers. Cleanup frees IRQ and low-level allocation through ALSA device teardown.

Dependencies/integration: Depends on SGI HPC3/IP22 platform globals, HAL2 register definitions, ALSA PCM indirect helpers, noncoherent DMA APIs, and platform driver binding name `sgihal2`. Risks include busy-waiting indirect register access with no timeout, hard-coded real-world PBUS config, noncoherent DMA sync correctness, IRQ handler dereferencing substreams when interrupts arrive outside active streams, and resource leak risk in `hal2_detect()` failure after IRQ request. Test signals are HAL2 revision print, PCM playback/capture period interrupts, mixer get/put read-back, DMA descriptor wrap behavior, and probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/hal2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/hal2.h -->
# sources/distributed-fs/ceph-client/sound/mips/hal2.h

Purpose: Defines HAL2 hardware register constants and memory-mapped register layouts used by the SGI HAL2 ALSA driver. It covers indirect control/status registers, revision fields, DMA-port controls, Bresenham clock generators, codec control fields, AES windows, volume registers, and synth-register layout.

Important APIs/types/functions: No functions are defined. Important types are `struct hal2_ctl_regs`, `struct hal2_aes_regs`, `struct hal2_vol_regs`, and `struct hal2_syn_regs`. Important macro groups include `H2_ISR_*`, `H2_REV_*`, `H2I_DMA_PORT_EN*`, `H2I_DMA_END*`, `H2I_DAC_C*`, `H2I_ADC_C*`, `H2I_C1_*`, `H2I_C2_*`, and `H2I_BRES*`.

Control flow: `hal2.c` uses these definitions to compose indirect register addresses and bitfields for reset, detect, mixer, DMA-port enable, endian selection, DAC/ADC setup, and clock programming. The struct layouts determine offsets when casting HPC3 external register windows.

State and persistence: The header owns no state, but its bit definitions describe persistent HAL2 hardware state: reset lines, DMA enables, endian flags, attenuation/gain/mute fields, clock-generator controls, and status bits.

Dependencies/integration: Depends only on `linux/types.h` but is tightly coupled to SGI HAL2 hardware and `hal2.c`. Risks include inaccurate bit masks causing register corruption, layout padding assumptions for memory-mapped registers, and comments indicating large indirect registers while helpers only actively use 16/32-bit cases. Test signals are successful HAL2 detection, correct mixer attenuation/gain programming, proper DAC/ADC data type setup, and no register bus hangs during indirect access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/hal2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/sgio2audio.c -->
# sources/distributed-fs/ceph-client/sound/mips/sgio2audio.c

Purpose: Implements the ALSA platform driver for SGI O2 A/V board audio using the MACE audio interface and AD1843 codec. It exposes two playback PCM devices, one capture stream, AD1843-backed mixer controls, coherent MACE ring buffers, and per-channel IRQ handling.

Important APIs/types/functions: Core structures are `struct snd_sgio2audio` and `struct snd_sgio2audio_chan`. Codec callbacks `read_ad1843_reg()` and `write_ad1843_reg()` connect `ad1843.c` to MACE registers. Mixer callbacks wrap AD1843 gain/source APIs. DMA movement is handled by `snd_sgio2audio_dma_pull_frag()`, `snd_sgio2audio_dma_push_frag()`, `snd_sgio2audio_dma_start()`, `snd_sgio2audio_dma_stop()`, and three ISR functions. Lifecycle functions include `snd_sgio2audio_create()`, `snd_sgio2audio_probe()`, and remove/free helpers.

Control flow: Probe creates a card, verifies codec presence, allocates a contiguous MACE ring-buffer region, requests six channel/error IRQs, resets the audio interface, sets the ring base, initializes AD1843, creates PCM devices and mixer controls, and registers the card. PCM open assigns channel 1 or 2 for playback or channel 0 for capture. Prepare resets software positions and programs AD1843. Trigger starts/stops MACE DMA. DMA IRQs copy between MACE ring slots and vmalloc ALSA buffers, reporting period elapsed when enough frames moved.

State and persistence: Persistent driver state includes the card pointer, AD1843 object, codec lock, three channel locks/positions/substreams, coherent ring base, and mixer state in codec registers. MACE hardware stores ring base, channel read/write pointers, depth, and control bits.

Dependencies/integration: Depends on SGI IP32 MACE globals/IRQ numbers, ALSA PCM/control core, `ad1843.c`, coherent DMA allocation, and platform driver name `sgio2audio`. Risks include manual 64-bit ring packing/unpacking, count calculations assuming 32-byte multiples, ISR use of `chan->substream`, restart-on-error without surfacing xrun details, and failure cleanup that frees all IRQs even only some were requested. Test signals are successful codec-present probe, AD1843 mixer read/write, simultaneous DAC1/DAC2/capture operation, period interrupts, pointer monotonicity, and overflow/memory-error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/sgio2audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/snd-n64.c -->
# sources/distributed-fs/ceph-client/sound/mips/snd-n64.c

Purpose: Implements built-in ALSA playback support for Nintendo 64 audio hardware. It programs AI and MI MMIO registers, uses a private coherent buffer to satisfy AI double-buffering behavior, and exposes one S16_BE stereo playback PCM device.

Important APIs/types/functions: `struct n64audio` stores AI/MI register bases, coherent ring buffer, ALSA card, and channel state. Core functions are `n64audio_push()`, `n64audio_isr()`, `hw_rule_period_size()`, `n64audio_pcm_open()`, `n64audio_pcm_prepare()`, `n64audio_pcm_trigger()`, `n64audio_pcm_pointer()`, `n64audio_probe()`, and `n64audio_init()`.

Control flow: Init uses `platform_driver_probe()` so probe code can be discarded. Probe allocates an ALSA card with private state, allocates a 32 KiB coherent ring buffer, maps MI and AI resources, creates one playback PCM, requests the platform IRQ, and registers the card. Open applies integer periods, even period size, and a custom period-size rule to avoid DMA errata. Prepare sets AI rate/bitclock and resets software pointers. Trigger pushes the first period, enables AI and MI interrupts; the ISR acknowledges AI interrupt, advances position, reports elapsed period, and queues the next period if still running.

State and persistence: State is card-private and not module-unloadable. Channel fields `pos`, `nextpos`, `writesize`, `bufsize`, and `substream` track software copy progress. Hardware state is AI control/rate/bitclock/address/length plus MI interrupt mask.

Dependencies/integration: Depends on platform resources for MI/AI MMIO, coherent DMA under 32-bit/GFP_DMA constraints, ALSA PCM core, and MIPS/N64 platform support. Risks include no remove path, substream pointer races at close/ISR boundaries, reliance on runtime delay as one period, period constraint logic needing to avoid empty intervals, and only NTSC DAC clock support. Test signals are successful built-in probe, accepted hw_params avoiding power-of-two period sizes, correct sample rate register values, continuous period interrupts, and clean stop masking AI interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/mips/snd-n64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/Kconfig -->
# sources/distributed-fs/ceph-client/sound/oss/dmasound/Kconfig

Purpose: Defines legacy OSS `dmasound` platform-driver configuration for Atari, Amiga Paula, and Q40 sound, plus the internal `DMASOUND` core symbol.

Important APIs/types/functions: Config entries are `DMASOUND_ATARI`, `DMASOUND_PAULA`, `DMASOUND_Q40`, and hidden `DMASOUND`. Each platform option is `tristate`, depends on the matching architecture/platform plus `SOUND`, and selects `DMASOUND`; `DMASOUND` selects `SOUND_OSS_CORE`.

Control flow: Enabling a platform option causes the matching objects in `sound/oss/dmasound/Makefile` to build with `dmasound_core.o`. User help describes `/dev/audio` and Linux/i386 OSS compatibility plus module availability.

State and persistence: No runtime state. Build configuration controls whether the legacy OSS device implementation and its platform backend are present.

Dependencies/integration: Integrates platform architecture symbols with the OSS sound core. Risks are mostly configurational: these legacy drivers depend on obsolete OSS interfaces and architecture-specific hardware symbols, so accidental enablement on unsupported platforms should be prevented by dependencies. Test signals are correct Kconfig visibility per architecture, `SOUND_OSS_CORE` selection, and successful module/built-in builds for each platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/Makefile -->
# sources/distributed-fs/ceph-client/sound/oss/dmasound/Makefile

Purpose: Builds legacy OSS dmasound core plus the selected platform backend. It wires Atari, Amiga Paula, and Q40 config symbols to object lists.

Important APIs/types/functions: The three kbuild lines append `dmasound_core.o` plus `dmasound_atari.o`, `dmasound_paula.o`, or `dmasound_q40.o` according to `CONFIG_DMASOUND_ATARI`, `CONFIG_DMASOUND_PAULA`, or `CONFIG_DMASOUND_Q40`.

Control flow: Kbuild evaluates enabled `obj-*` entries. Each platform build includes its backend and a copy/link of the shared core object, producing the relevant built-in or module target under the OSS sound tree.

State and persistence: No runtime state. The build state determines which platform machine table implementation is linked with the dmasound core.

Dependencies/integration: Tied to `sound/oss/dmasound/Kconfig` and source files in the same directory. Risks include duplicate core linkage if multiple platform symbols are enabled in one build context, stale backend object names, and dependency drift between Kconfig and Makefile. Test signals are successful platform builds and resulting objects containing both core and backend symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound.h -->
# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound.h

Purpose: Provides shared definitions for the legacy OSS dmasound core and platform backends. It defines minor-device constants, endian conversion macros, ioctl helpers, buffer sizing policy, machine callback interface, translation callback table, global sound settings, and shared write queue state.

Important APIs/types/functions: Key types are `SETTINGS`, `MACHINE`, `TRANS`, `struct sound_settings`, and `struct sound_queue`. Key helpers/macros are `IOCTL_IN`, `IOCTL_OUT`, `ioctl_return()`, `dmasound_set_volume()`, `dmasound_set_bass()`, `dmasound_set_treble()`, `dmasound_set_gain()`, `WAKE_UP`, `write_sq`, and `catchRadius`. It declares `dmasound_init()`, `dmasound_deinit()`, global `dmasound`, conversion tables, and `dmasound_write_sq`.

Control flow: Platform backends fill a `MACHINE` struct with callbacks for allocation, IRQ setup, init/silence, format/mixer controls, playback, queue setup, and state reporting. The core calls these callbacks and uses `TRANS` conversion routines to copy userspace audio into DMA-ready queue buffers.

State and persistence: Global runtime state is in `struct sound_settings dmasound` and `struct sound_queue dmasound_write_sq`, including hardware/soft format settings, mixer values, current minor device, queue fragments, active buffer counts, wait queues, and xrun/died flags.

Dependencies/integration: Depends on Linux types, OSS `soundcard.h` users in C files, platform-defined conversion tables, and dmasound core implementation. Risks include global mutable state, callback nullability, legacy ioctl semantics, queue concurrency around non-volatile counters, fixed buffer limits, and platform-specific assumptions in shared macros. Test signals are OSS device open/write/sync behavior, mixer ioctl round trips, queue wakeups, format conversion correctness, and platform backend init/deinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_atari.c -->
# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_atari.c

Purpose: Implements the Atari TT/Falcon backend for the legacy OSS dmasound core. It handles Atari STRAM allocation, Timer A IRQ setup, TT/Falcon DMA sound hardware programming, sample-format conversion/resampling into queue buffers, playback queue feeding, mixer ioctls, state reporting, and backend registration.

Important APIs/types/functions: Translation functions `ata_ct_*` copy/convert userspace audio directly; `ata_ctx_*` also expand/resample using `expand_bal` and `expand_data`. Hardware functions include `AtaAlloc()`, `AtaIrqInit()`, `AtaSetBass()`, `AtaSetTreble()`, `TTInit()`, `TTSetFormat()`, `TTSetVolume()`, `TTSetGain()`, `FalconInit()`, `FalconSetFormat()`, `FalconSetVolume()`, `AtaPlayNextFrame()`, `AtaPlay()`, and `AtaInterrupt()`. Machine tables `machTT` and `machFalcon` plug into dmasound core.

Control flow: Module init checks Atari hardware, chooses Falcon when CODEC is present or TT when MICROWIRE is present, fills `dmasound.mach` defaults, and calls `dmasound_init()` if Timer A is free. Format/rate changes run TT/Falcon init, choose exact-rate or expanding translators, program DMA mode/dividers/matrix, and reset expansion balance. Writes fill `write_sq`; `AtaPlay()` disables Timer A IRQ, preloads one or two frames, and starts repeat DMA. `AtaInterrupt()` advances queue counts, wakes writers/sync waiters, and refills DMA when possible.

State and persistence: Static state includes `is_falcon`, `write_sq_ignore_int`, `expand_bal`, and `expand_data`. Shared persistent state lives in `dmasound` and `write_sq`. Hardware state persists in Atari `tt_dmasnd`, YM speaker bits, LM1992 microwire mixer, Timer A registers, and STRAM buffers.

Dependencies/integration: Depends on Atari machine macros/registers, `atari_microwire_cmd()`, STRAM allocation, OSS dmasound core, and user access helpers. Risks include many hand-rolled conversion loops with endian/sign/stereo duplication cases, queue state updated under interrupt constraints, Timer A ownership conflicts, virtual-to-physical DMA address use, first Falcon interrupt suppression, and legacy OSS ioctl semantics. Test signals are TT/Falcon hardware detection, Timer A IRQ acquisition/release, audible playback at supported and expanded rates, mixer ioctl read/write values, `/dev/dsp` format negotiation, sync drain wakeups, and absence of underrun repeats under interrupt delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_atari.c -->
