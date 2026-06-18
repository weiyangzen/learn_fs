# Research: subset-b-006382

This grouped report covers the requested sound subsystem files in manifest order. Each source file has its own source-tree-aligned section for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_core.c -->
# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_core.c

## Purpose

`dmasound_core.c` is the machine-independent OSS compatibility core for the legacy DMA sound stack used by Atari, Amiga, and Q40 style low-level drivers. It registers `/dev/dsp` or `/dev/audio`, `/dev/mixer`, and `/dev/sndstat` through the old sound core APIs, owns the playback queue, translates user audio samples through a low-level `TRANS` table, and dispatches hardware operations through the global `dmasound.mach` `MACHINE` callback table.

## Important APIs, Types, and Functions

The public exports are `dmasound`, `dmasound_init()`, `dmasound_deinit()`, `dmasound_write_sq`, `dmasound_catchRadius`, and, when enabled, `dmasound_ulaw2dma8` / `dmasound_alaw2dma8`. Low-level modules fill `dmasound.mach` before calling `dmasound_init()`.

Important internal entry points are `sq_open()`, `sq_write()`, `sq_ioctl()`, `sq_poll()`, `sq_release()`, `mixer_ioctl()`, and `state_open()`/`state_read()`. Queue setup is handled by `sq_allocate_buffers()`, `sq_setup()`, `sq_reset_output()`, `sq_fsync()`, and `set_queue_frags()`. Format/rate/channel settings flow through `sound_set_format()`, `sound_set_speed()`, and `sound_set_stereo()`, while user-copy conversion is centralized in `sound_copy_translate()`.

## Control Flow

Initialization starts in `dmasound_init()`: it registers the DSP file operations, registers the status device, registers the mixer, invokes `dmasound.mach.irqinit()`, and logs the core and machine editions. A low-level driver is responsible for assigning machine callbacks first. Open acquires `dmasound_core_mutex`, takes the low-level module reference with `try_module_get()`, allocates default playback buffers, rejects read mode because this core instance does not implement capture, and resets shared soft/hard settings if no owner exists.

Playback is lazy. `sq_write()`, `SNDCTL_DSP_GETBLKSIZE`, `SNDCTL_DSP_GETOSPACE`, and `poll()` force `sq_setup()` if the queue is not locked. `sq_setup()` calls the hardware `init()` callback, computes internal block sizes from user fragment settings and soft-to-hard sample geometry, resets queue counters, and invokes `write_sq_setup()` if the backend provides it. `sq_write()` appends to a partial rear fragment when possible, waits on `action_queue` when `count >= max_active`, copies/translates user data into DMA buffers, advances queue indices, and calls the backend `play()` callback to start or continue hardware output.

`sq_ioctl()` implements OSS reset, sync, format, channel, speed, fragment, block-size, space, and capability calls. Mixer ioctls first satisfy generic `OSS_GETVERSION` and `SOUND_MIXER_INFO`, then pass unknown mixer commands to `dmasound.mach.mixer_ioctl()`. `/dev/sndstat` snapshots machine revision, low-level status, soft/hard settings, and playback queue counters into a fixed-size buffer.

## State and Persistence

Persistent runtime state is held in global statics and `dmasound`: registered unit numbers, `irq_installed`, module parameters `numWriteBufs`, `writeBufSize`, and `dmasound_catchRadius`, mixer busy/modify counters, status buffer position, `shared_resource_owner`, `shared_resources_initialised`, and the exported `dmasound_write_sq`. There is no disk persistence. Register state is delegated to low-level callbacks; buffer memory is allocated with `dmasound.mach.dma_alloc()` and released on close/deinit.

Concurrency uses `dmasound_core_mutex` around open/release/ioctl/status/mixer state and `dmasound.lock` around queue flags touched by write and interrupt-capable low-level paths. The queue uses `action_queue` for writer space and `sync_queue` for drain completion.

## Dependencies and Integration Points

The file depends on legacy OSS headers, sound core registration (`register_sound_dsp`, `register_sound_mixer`, `register_sound_special`), Linux user-copy helpers, module references, wait queues, mutexes, and the local `dmasound.h` contracts. It integrates with backends through the `MACHINE` callbacks: DMA allocation, IRQ lifecycle, init/silence/play, format/volume/tone setters, mixer hooks, queue setup, and status hooks.

## Risks and Edge Cases

The driver is globally stateful and effectively single-playback-queue. Comments call out race risks when multiple threads share an O_RDWR file descriptor, though read is currently rejected. Queue parameter changes after first write are mostly rejected through `queues_are_quiescent()`, but speed changes can invalidate resources and rely on deferred re-init. `sq_setup()` does integer scaling between soft and hard formats and has several bounds repairs rather than strict validation. `state_open()` uses deterministic lengths but still uses `sprintf()` into a fixed buffer and relies on low-level `state_info()` respecting `LOW_LEVEL_STAT_ALLOC`. `dmasound_setup()` references `catchRadius` via macro and accepts legacy boot parameters without power-of-two buffer enforcement.

## Test Signals

Useful tests are build coverage for all dmasound backends, module load/unload with IRQ init failure paths, OSS open/write/poll/fsync/ioctl smoke tests, `SNDCTL_DSP_SETFRAGMENT` boundary checks, nonblocking writes returning `-EAGAIN`, signal interruption during write and sync, `/dev/sndstat` buffer-length validation, mixer ioctl pass-through, and repeated open/close to catch buffer release and module reference leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_paula.c -->
# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_paula.c

## Purpose

`dmasound_paula.c` is the Amiga Paula low-level backend for the legacy dmasound OSS core. It maps the core's generic queue, mixer, and format requests onto Amiga chip RAM allocation, Paula audio DMA registers, Amiga audio interrupt handling, volume/low-pass-filter control, and sample-layout conversion for 8-bit and pseudo-14-bit playback.

## Important APIs, Types, and Functions

The file defines `machAmiga`, `def_hard`, and `def_soft`, then installs them in `amiga_audio_probe()` before calling `dmasound_init()`. The module is a platform driver named `amiga-audio` via `module_platform_driver_probe()`.

Key callbacks are `AmiAlloc()`, `AmiFree()`, `AmiIrqInit()`, `AmiIrqCleanUp()`, `AmiInit()`, `AmiSilence()`, `AmiSetFormat()`, `AmiSetVolume()`, `AmiSetTreble()`, `AmiPlay()`, `AmiWriteSqSetup()`, `AmiMixerInit()`, `AmiMixerIoctl()`, and `AmiStateInfo()`. Sample translation is represented by `transAmiga`, with direct signed-8 copy and generated converters for mu-law, A-law, unsigned 8-bit, and 16-bit big/little endian signed/unsigned input.

## Control Flow

Probe copies the machine descriptor into `dmasound.mach`, sets defaults, and enters the core init path. IRQ setup stops all Paula audio DMA through `StopDMA()` and requests `IRQ_AMIGA_AUD0`. Core writes call `AmiInit()` during queue setup, which silences DMA, computes an Amiga audio period from `amiga_colorclock / soft.speed - 1`, clamps it to `amiga_audio_min_period..65535`, copies soft settings to hard settings, installs `transAmiga`, writes Paula `audper` for all four channels, and updates `amiga_audio_period`.

`AmiPlay()` controls two-stage frame loading. It disables the Paula audio interrupt while inspecting queue state, refuses to queue a partial fragment unless syncing/posting, and calls `AmiPlayNextFrame()` when enough queued data exists. `AmiPlayNextFrame()` maps a queued buffer into Paula channel addresses and lengths. For 8-bit output it uses channels 0/1. For 16-bit pseudo-14-bit output it splits high and low six-bit data over four channels and only enables channels 2/3 when both volumes are at full scale. `AmiInterrupt()` advances active loaded/playing flags, decrements queue count after a frame completes, wakes writers, queues the next frame if available, stops DMA when drained, and wakes sync waiters.

## State and Persistence

Persistent state is module-global and hardware-register state: `write_sq_block_size_half`, `write_sq_block_size_quarter`, optional `saved_heartbeat`, Paula channel volumes/periods/locations/lengths, `amiga_audio_period`, and `dmasound.volume_left/right` plus `dmasound.treble`. Buffer allocation uses `amiga_chip_alloc()` because Paula DMA requires chip-addressable memory. There is no persistent storage outside hardware and process lifetime.

## Dependencies and Integration Points

This backend depends on Amiga architecture headers, `amiga_custom`, CIA register access for the low-pass filter, `amiga_chip_alloc/free`, `ZTWO_PADDR`, Amiga IRQ numbers, and the machine heartbeat callback when `CONFIG_HEARTBEAT` is enabled. It integrates with the core through `MACHINE` callbacks and consumes the exported mu-law/A-law conversion tables from `dmasound_core.c`.

## Risks and Edge Cases

Heartbeat and Paula low-pass/power LED use the same line, so playback disables heartbeat and restores it on DMA stop. Pseudo-14-bit output only works at maximum volume; lower volume silently disables low-bit channels. The translation functions deliberately operate on complete sample units and may leave trailing bytes for user space to retry. `AmiStateInfo()` guards only after using `sprintf()` and relies on the caller-provided space. Hardware period clamping means requested sample rates above Paula capability are reported through adjusted hard speed, while user-visible soft speed remains request-oriented until core state is refreshed.

## Test Signals

Build-test with Amiga dmasound enabled, platform probe/remove, chip-RAM allocation failure, IRQ request failure, 8-bit mono/stereo playback, 16-bit pseudo-14-bit playback at full and non-full volume, `/dev/mixer` volume/treble reads and writes, `/dev/sndstat` low-level volume output, sync drain wakeups, and heartbeat restore after playback stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_paula.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_q40.c -->
# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_q40.c

## Purpose

`dmasound_q40.c` is the Q40/Q60 low-level backend for the legacy dmasound OSS core. It provides a simple 8-bit DAC playback implementation, software conversion and sample-rate expansion/compression, interrupt-driven sample feeding, and machine registration guarded by `MACH_IS_Q40`.

## Important APIs, Types, and Functions

The machine descriptor `machQ40` supplies DMA allocation (`Q40Alloc`/`Q40Free`), IRQ lifecycle (`Q40IrqInit`, `Q40IrqCleanUp`), silence/init/format/volume/play callbacks, default settings, hardware formats, and capabilities. Translation tables are split into `transQ40Normal`, `transQ40Expanding`, and `transQ40Compressing`; each supports mu-law/A-law, signed 8-bit, and unsigned 8-bit only. Module entry is `dmasound_q40_init()` and exit is `dmasound_q40_cleanup()`.

## Control Flow

Module init checks `MACH_IS_Q40`, installs `machQ40` and defaults into the global core state, then calls `dmasound_init()`. IRQ init registers `Q40StereoInterrupt()` initially on `Q40_IRQ_SAMPLE`.

When the core prepares output, `Q40Init()` chooses hard speed from the two hardware rates, 10000 or 20000 Hz. If the requested soft speed falls within `catchRadius` of a hardware rate it snaps soft speed to that rate and uses direct conversion. If requested speed is too high it selects 20000 Hz and compression; otherwise it uses expansion. It forces 8-bit hard size and resets `expand_bal` for rate conversion.

`Q40Play()` starts playback only when no frame is active and there is either a full fragment or a sync/post condition. `Q40PlayNextFrame()` stores the current buffer pointer and byte count in `q40_pp`/`q40_sc`, advances the queue, derives the hardware speed bit, disables sample IRQs, frees the old handler, installs either mono or stereo IRQ handler based on `dmasound.soft.stereo`, writes sample-rate/clear/enable registers, and returns. The mono/stereo IRQ handlers write one or two bytes into `DAC_LEFT`/`DAC_RIGHT` per interrupt and call `Q40Interrupt()` when the frame is consumed. `Q40Interrupt()` clears active state, decrements queue count, tries to queue another frame, disables sample generation and centers DACs at 127 when empty, and wakes queue waiters.

## State and Persistence

The backend keeps global rate-conversion accumulators `expand_bal` and `expand_data`, plus active IRQ playback cursor `q40_pp` and count `q40_sc`. Hardware state lives in Q40 master/sample registers and DAC memory-mapped symbols. Buffers are allocated with `kmalloc()` through the core. There is no persistent storage.

## Dependencies and Integration Points

Dependencies include Q40 architecture interrupt and master/DAC headers, legacy OSS soundcard constants, and the `dmasound.h` queue/global contracts. It consumes the core's mu-law/A-law tables and calls `dmasound_init()`/`dmasound_deinit()`.

## Risks and Edge Cases

The IRQ handler is freed and re-requested for every frame to switch mono/stereo behavior, which is expensive and risk-prone if an error occurs; failed `request_irq()` is only rate-limited logged, not propagated to the core. `Q40IrqCleanUp()` frees with `Q40Interrupt` as dev_id, matching the request dev_id rather than the function pointer, but this pattern is subtle. Volume is a no-op. Only 8-bit formats are supported, so unsupported 16-bit writes move zero bytes via missing translation callbacks. Rate conversion is nearest-sample style and keeps state across calls, so reset/reinit behavior is important for glitches.

## Test Signals

Build on Q40 or compile-test capable m68k, module init on non-Q40 returning `-ENODEV`, direct 10 kHz and 20 kHz playback, expansion/compression path writes, mono and stereo IRQ handler switching, empty-queue DAC centering, `SNDCTL_DSP_SYNC` drain wakeups, and robustness when IRQ re-request fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_q40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/Kconfig -->
# sources/distributed-fs/ceph-client/sound/parisc/Kconfig

## Purpose

This Kconfig file defines PA-RISC GSC sound-driver configuration. It gates the PA-RISC sound submenu behind GSC bus support and exposes the Harmony/Vivace driver option.

## Important APIs, Types, and Functions

The top-level symbol is `SND_GSC`, a boolean `menuconfig` depending on `GSC` and defaulting to `y`. Inside `if SND_GSC`, `SND_HARMONY` is a tristate option named "Harmony/Vivace sound chip" and selects `SND_PCM`.

## Control Flow

Kconfig evaluation first hides all entries unless `GSC` is available. When `SND_GSC` is enabled, `SND_HARMONY` can be built in, modular, or disabled. Selecting Harmony automatically pulls ALSA PCM support, matching `harmony.c`'s PCM-only runtime interface.

## State and Persistence

The file only defines build-time configuration symbols. Its state persists in kernel `.config` and module build products, not at runtime.

## Dependencies and Integration Points

It integrates with the ALSA PA-RISC Makefile, where `CONFIG_SND_HARMONY` builds `snd-harmony.o`. It also depends on architecture bus discovery through `GSC`.

## Risks and Edge Cases

`SND_GSC` defaults to `y` whenever `GSC` exists, so Harmony can become visible by default on PA-RISC configs. The Harmony option does not explicitly depend on `PARISC`, relying on `GSC` to constrain architecture. Missing `SND_PCM` select would break the driver, but it is present.

## Test Signals

Run Kconfig coverage for PA-RISC/GSC enabled and disabled configs, verify `CONFIG_SND_HARMONY=m` produces `snd-harmony.ko`, and verify `SND_PCM` is selected automatically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/Makefile -->
# sources/distributed-fs/ceph-client/sound/parisc/Makefile

## Purpose

This Makefile wires the PA-RISC ALSA Harmony driver into kbuild.

## Important APIs, Types, and Functions

It defines `snd-harmony-y := harmony.o` and adds `snd-harmony.o` to `obj-$(CONFIG_SND_HARMONY)`.

## Control Flow

When `CONFIG_SND_HARMONY=y`, `harmony.o` is linked into the built-in sound object graph as `snd-harmony.o`. When set to `m`, kbuild emits `snd-harmony.ko`. When disabled, nothing from this directory is built.

## State and Persistence

The file has no runtime state. It affects object composition and module naming.

## Dependencies and Integration Points

It depends on `sound/parisc/Kconfig` for the `CONFIG_SND_HARMONY` symbol and on `harmony.c` as the only object in the module.

## Risks and Edge Cases

The module is single-object, so adding companion files later requires updating `snd-harmony-y`. A mismatched Kconfig symbol would silently omit the driver, but the current symbol matches.

## Test Signals

Kbuild with `CONFIG_SND_HARMONY=y` and `m`, and `make M=sound/parisc` style builds when supported by the tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/harmony.c -->
# sources/distributed-fs/ceph-client/sound/parisc/harmony.c

## Purpose

`harmony.c` is an ALSA driver for the HP Harmony/Vivace audio chipset found in LASI/GSC PA-RISC workstations. It creates one ALSA card with one playback and one capture PCM stream, mixer controls for Harmony gain routing, GSC device binding, DMA buffers, interrupt-driven period advancement, and hardware register programming.

## Important APIs, Types, and Functions

Module parameters are `index` and `id`. Device matching is via `snd_harmony_devtable` and `parisc_driver`. Register access uses `harmony_read()`, `harmony_write()`, `harmony_wait_for_control()`, and `harmony_reset()`. Runtime control uses `harmony_disable_interrupts()`, `harmony_enable_interrupts()`, `harmony_mute()`, `harmony_unmute()`, and `harmony_set_control()`.

PCM callbacks include playback/capture `open`, `close`, `prepare`, `trigger`, and `pointer`, grouped in `snd_harmony_playback_ops` and `snd_harmony_capture_ops`. Card setup flows through `snd_harmony_create()`, `snd_harmony_pcm_init()`, `snd_harmony_mixer_init()`, and `snd_harmony_probe()`. Cleanup is through ALSA device free hooks and `snd_harmony_remove()`.

## Control Flow

`alsa_harmony_init()` registers a PA-RISC driver. Probe allocates an ALSA card, allocates and maps `struct snd_harmony`, requests the hardware IRQ, registers it as a low-level ALSA device, creates PCM, creates mixer controls, sets card names, registers the card, and stores it in `parisc_set_drvdata()`.

The IRQ handler disables Harmony interrupts under lock, reads `HARMONY_DSTATUS`, and responds to playback-next (`PN`) and record-next (`RN`) conditions. If playback is active, it advances `pbuf.buf` by one period, wraps within buffer size, writes the next playback DMA address to `HARMONY_PNXTADD`, increments stats, and calls `snd_pcm_period_elapsed()`. If inactive, it points playback at the silence buffer. Capture mirrors this behavior with `cbuf` and `HARMONY_RNXTADD`, otherwise routing data to the graveyard buffer. Interrupts are re-enabled at the end.

Prepare callbacks reject the opposite active direction, derive buffer and period byte counts from ALSA runtime, translate format/rate/channels to Harmony control bits, write control, and store runtime DMA address. Trigger start writes active DMA and opposite-direction sink/source buffers, unmutes, and enables interrupts. Trigger stop clears playing/capturing, mutes, points hardware to silence/graveyard, and disables interrupts. Pointer callbacks read current hardware addresses and convert byte deltas to ALSA frames.

Mixer controls manipulate the cached `h->st.gain` bitfield and write `HARMONY_GAINCTL`. They expose master playback, capture, monitor, input route, internal speaker, line-out, and headphone controls.

## State and Persistence

`struct snd_harmony` stores IRQ, physical and remapped base address, device pointers, cached hardware state (`gain`, `rate`, `format`, `stereo`, `playing`, `capturing`), DMA buffer descriptors, graveyard/silence DMA buffers, interrupt stats, ALSA card/PCM/substream pointers, and two spinlocks. Graveyard and silence buffers live for driver lifetime; playback/capture DMA is managed by ALSA per stream. There is no persistent storage beyond ALSA card state while loaded.

## Dependencies and Integration Points

The file depends on ALSA core, PCM, control, info, DMA helpers, Linux IRQ/io APIs, and PA-RISC `parisc_device` infrastructure. Hardware register layout and bit definitions come from `harmony.h`. It integrates with kbuild through `snd-harmony.o` and with Kconfig through `SND_HARMONY`.

## Risks and Edge Cases

The PCM hardware info advertises joint duplex, but prepare and trigger paths return `-EBUSY` if the opposite stream is active, so behavior is not actually simultaneous duplex. `harmony_wait_for_control()` busy-waits without timeout, so broken hardware can hang the CPU. Pointer callbacks return zero when the current address appears outside the buffer, which can hide hardware address anomalies. Cleanup calls `iounmap(h->iobase)` unconditionally; creation only reaches normal free paths after map success, but future edits should preserve that invariant. Graveyard/silence DMA allocation failure after the first allocation relies on device-free cleanup.

## Test Signals

Compile with `CONFIG_SND_HARMONY=m/y`, probe on matched PA-RISC IDs, IRQ request failure unwind, ALSA playback and capture open/prepare/start/stop, rejection of simultaneous playback/capture, supported rate constraint validation for the 14 explicit rates, mixer get/put for all gain controls, suspend-style stop/start cycles, and period elapsed accounting under interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/harmony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/harmony.h -->
# sources/distributed-fs/ceph-client/sound/parisc/harmony.h

## Purpose

`harmony.h` provides the private data structures, buffer sizing constants, register offsets, bit masks, gain-field definitions, and sample-rate encoding constants used by the PA-RISC Harmony ALSA driver.

## Important APIs, Types, and Functions

The primary types are `struct harmony_buffer`, describing DMA address, current buffer offset, period count, total size, and coherency flag, and `struct snd_harmony`, the complete per-device driver state. Constants define one PCM device, four substreams maximum, no MIDI devices, 64 bytes of MMIO space, page-sized periods, 16 maximum periods, and one-page graveyard/silence buffers.

Register constants cover `HARMONY_ID`, `RESET`, `CNTL`, `GAINCTL`, next/current playback and record addresses, `DSTATUS`, overflow, PIO, and diagnostic registers. Bitfields define control command/stereo/rate bits, interrupt status and enable bits, data formats, mono/stereo selectors, gain mute/default values, output enable/input select bits, monitor/input/output gain masks, and Harmony sample-rate codes.

## Control Flow

There is no executable control flow. The constants are consumed by `harmony.c` to program control words, interpret interrupt status, configure PCM formats and rates, expose mixer controls, and allocate DMA buffers with constraints that match hardware register behavior.

## State and Persistence

The header defines the shape of runtime state but stores none itself. Its fields persist in each allocated `struct snd_harmony` for the life of a probed device.

## Dependencies and Integration Points

It depends on ALSA and PA-RISC types included by `harmony.c` before this header. Register definitions are tightly coupled to the Harmony/Vivace hardware and to ALSA PCM constraints in the C file.

## Risks and Edge Cases

Register and bit constants have no type safety, so incorrect shifts or masks can affect unrelated gain/control bits. `BUF_SIZE` is fixed at `PAGE_SIZE`, making period size inflexible. The `coherent` field in `struct harmony_buffer` is present but unused in the current C file. Any hardware variant with different MMIO size or rate encodings would need header changes.

## Test Signals

Compile coverage is the main signal. Runtime validation should confirm that each ALSA supported rate maps to the intended `HARMONY_SR_*` code, gain controls affect the expected bits, and period buffer constraints match the hardware DMA address stepping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/parisc/harmony.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/Kconfig -->
# sources/distributed-fs/ceph-client/sound/pci/Kconfig

## Purpose

This Kconfig file defines the ALSA PCI sound-driver menu and the build symbols for many PCI audio, modem, DSP, and professional audio drivers. It provides dependency and `select` wiring for PCM, AC97, raw MIDI, firmware loading, I/O port access, DMA constraints, radio/input subfeatures, and sequencer integration.

## Important APIs, Types, and Functions

The top-level symbol is `SND_PCI`, a boolean `menuconfig` depending on `PCI` and defaulting to `y`. Under `if SND_PCI`, it declares numerous `tristate` driver symbols including `SND_AD1889`, `SND_ALS300`, `SND_ALS4000`, `SND_ALI5451`, `SND_ATIIXP`, `SND_AZT3328`, `SND_BT87X`, `SND_CMIPCI`, `SND_CS4281`, `SND_CS5530`, `SND_EMU10K1`, `SND_ENS1370`, `SND_ES1938`, `SND_FM801`, `SND_ICE1712`, `SND_INTEL8X0`, `SND_MAESTRO3`, `SND_RME32`, `SND_SIS7019`, `SND_SONICVIBES`, `SND_VIA82XX`, `SND_VIRTUOSO`, `SND_YMFPCI`, and many subdirectory-backed drivers. It also defines helper or feature symbols such as `SND_OXYGEN_LIB`, `SND_BT87X_OVERCLOCK`, `SND_CS46XX_NEW_DSP`, `SND_EMU10K1_SEQ`, `SND_ES1968_INPUT`, `SND_ES1968_RADIO`, `SND_FM801_TEA575X_BOOL`, and `SND_MAESTRO3_INPUT`.

## Control Flow

Kconfig resolution exposes PCI sound options only when PCI support exists. Each driver symbol pulls in required ALSA infrastructure with `select`, and some constrain availability with `depends on` expressions such as `HAS_IOPORT`, `ZONE_DMA`, `ISA_DMA_API`, `FW_LOADER`, `X86`, media/radio support, or input support. The resulting `.config` symbols drive object inclusion in `sound/pci/Makefile` and subdirectory Makefiles.

## State and Persistence

The file controls build-time configuration. State persists in kernel configuration and in which built-in objects or modules are produced.

## Dependencies and Integration Points

It integrates directly with `sound/pci/Makefile`, which maps many `CONFIG_SND_*` symbols to module objects and includes subdirectories whenever `CONFIG_SND` is enabled. AC97-dependent controllers select `SND_AC97_CODEC`, tying them to `sound/pci/ac97`.

## Risks and Edge Cases

Because many drivers use `select`, dependencies must be complete at the driver symbol level; otherwise Kconfig can force-enable libraries in unsupported environments. Some drivers rely on broad parent `SND_PCI` gating while adding architecture-specific constraints individually. PCI ID conflicts are handled for `SND_SE6X` with `SND_OXYGEN=n && SND_VIRTUOSO=n`, which is easy to disturb. Help text contains driver-specific operational warnings, for example CS5535 AC97 quirks and AW2 input switching noise.

## Test Signals

Run allmodconfig/allyesconfig across representative architectures, randconfig with `PCI=n`, Kconfig warnings checks, and build verification that every visible module name in help text corresponds to Makefile output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/Makefile

## Purpose

This Makefile maps top-level ALSA PCI Kconfig symbols to kbuild module objects and includes PCI sound subdirectories.

## Important APIs, Types, and Functions

It defines single- or multi-object module composition for legacy PCI drivers, such as `snd-ad1889-y := ad1889.o`, `snd-ens1370-y := ens1370.o ak4531_codec.o`, and similar assignments for ALS300, ALS4000, ATI IXP, AZT3328, Bt87x, CMI, CS4281, CS5530, Ensoniq, ESS, FM801, Intel8x0, Maestro3, RME, SiS, SonicVibes, and VIA. It then adds objects with `obj-$(CONFIG_SND_...) += snd-...o`.

The final `obj-$(CONFIG_SND) +=` list descends into subdirectories: `ac97`, `ali5451`, `asihpi`, `au88x0`, `aw2`, `ctxfi`, `ca0106`, `cs46xx`, `cs5535audio`, `lola`, `lx6464es`, `echoaudio`, `emu10k1`, `ice1712`, `korg1212`, `mixart`, `nm256`, `oxygen`, `pcxhr`, `riptide`, `rme9652`, `trident`, `ymfpci`, and `vx222`.

## Control Flow

For each enabled `CONFIG_SND_*`, kbuild composes the corresponding module from its `snd-*-y` object list. Subdirectories are visited whenever ALSA sound support is enabled, leaving each child directory to decide whether to build objects based on its own config symbols.

## State and Persistence

The file has no runtime state. It determines module names, linked objects, and recursive build traversal.

## Dependencies and Integration Points

It depends on `sound/pci/Kconfig` for symbols and on child Makefiles such as `sound/pci/ac97/Makefile`. It also links shared companion objects, for example `ak4531_codec.o` into `snd-ens1370.o`.

## Risks and Edge Cases

Adding a Kconfig option without a matching Makefile object, or vice versa, causes silent build omission or dead entries. The unconditional subdirectory descent under `CONFIG_SND` means child Makefiles must be correct even when PCI-specific symbols are off. Module names in help text should stay synchronized with `snd-*` object names.

## Test Signals

Build with each listed `CONFIG_SND_*` as `m`, allmodconfig for subdirectory traversal, and targeted dependency checks for multi-object modules like `snd-ens1370`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/ac97/Makefile

## Purpose

This Makefile builds the ALSA AC97 codec support module used by many PCI audio and modem controllers.

## Important APIs, Types, and Functions

It composes `snd-ac97-codec.o` from `ac97_codec.o` and `ac97_pcm.o`, conditionally adding `ac97_proc.o` when `CONFIG_SND_PROC_FS` is enabled. It adds the module with `obj-$(CONFIG_SND_AC97_CODEC) += snd-ac97-codec.o`.

## Control Flow

When `CONFIG_SND_AC97_CODEC=y` or `m`, kbuild links the core codec and PCM helper objects, plus procfs diagnostics when configured. When disabled, no AC97 codec support object is emitted.

## State and Persistence

No runtime state is defined here. The Makefile controls object composition and optional procfs support.

## Dependencies and Integration Points

It is reached by `sound/pci/Makefile` and by controller Kconfig symbols that `select SND_AC97_CODEC`. Runtime APIs are exported from `ac97_codec.c` and companion objects to AC97 controller drivers.

## Risks and Edge Cases

Procfs support changes module contents and enables declarations in `ac97_local.h`; both sides must remain synchronized. Omitting `ac97_pcm.o` would break PCM setup consumers even if codec registration builds.

## Test Signals

Build `CONFIG_SND_AC97_CODEC=m/y` with `CONFIG_SND_PROC_FS=y/n`, and ensure dependent PCI AC97 controller modules link against exported codec symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_codec.c -->
# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_codec.c

## Purpose

`ac97_codec.c` implements ALSA's universal Audio Codec '97 / MC'97 codec layer. It creates AC97 buses and codec instances for controller drivers, probes and names codecs, validates and caches register accesses, builds standard mixer and modem controls, applies codec-specific patches and board quirks, determines supported sample rates, handles suspend/resume and optional power saving, and exports helper APIs to PCI AC97 controller drivers.

## Important APIs, Types, and Functions

Exported APIs include `snd_ac97_write()`, `snd_ac97_read()`, `snd_ac97_write_cache()`, `snd_ac97_update()`, `snd_ac97_update_bits()`, `snd_ac97_get_short_name()`, `snd_ac97_bus()`, `snd_ac97_mixer()`, `snd_ac97_update_power()` when power-save is enabled, `snd_ac97_suspend()` / `snd_ac97_resume()` when PM is enabled, and `snd_ac97_tune_hardware()`.

Important internal structures are `struct ac97_codec_id` tables for vendor and exact codec matching, standard `snd_kcontrol_new` templates, AD18xx private PCM controls, S/PDIF controls, and `power_regs[]`. Codec-specific patch functions are included by textual inclusion of `ac97_patch.c`, and `ac97_id.h` supplies selected ID constants.

## Control Flow

Controller drivers first call `snd_ac97_bus()` with bus callbacks for register I/O. That allocates `struct snd_ac97_bus`, initializes bus lock and default 48 kHz clock, initializes procfs bus support, and registers an ALSA bus device.

`snd_ac97_mixer()` creates a codec from a template. It initializes private pointers, bus slot, mutexes, subsystem IDs, and optional delayed power work. It then uses controller reset/wait callbacks if present; otherwise it writes AC97 audio and modem reset registers and waits for accessible registers with `ac97_reset_wait()`. It reads vendor IDs, rejects invalid all-zero/all-ones IDs unless vendor detection is requested, tests audio and modem capabilities, reads audio caps and extended IDs, and waits for analog/modem readiness. It enables VRA/VRM and surround/center/LFE extended status bits, detects double-rate support, determines supported DAC/ADC/MIC/S/PDIF rates, runs controller `init`, applies codec name lookup and patch hooks, builds audio mixer controls and/or modem controls, updates power registers, initializes procfs codec support, and registers the codec as an ALSA device.

Register I/O helpers gate accesses through `snd_ac97_valid_reg()` for known buggy codecs, then call bus read/write callbacks. Cached writes and updates hold `reg_mutex`; paging helpers hold `page_mutex` for AC97 2.3 paged registers. Mixer construction probes register behavior with writes/reads to decide which controls exist and what volume resolution they support, then adds ALSA controls with TLV dB metadata.

Suspend calls codec patch suspend hooks if present, cancels power work, and powers the chip down. Resume resets or powers up the codec, waits for register access, runs bus init and patch resume hooks, or restores cached registers and S/PDIF state.

## State and Persistence

State is stored in `struct snd_ac97_bus` and `struct snd_ac97`: bus callbacks, clock, codec array, register cache `regs[]`, `reg_accessed` bitmap, mutexes, codec IDs/caps/ext IDs, rates, flags/scaps, build ops, S/PDIF status, subsystem IDs, private data, proc entries, device registration, and optional power-work state. Hardware register state is mirrored in the cache for suspend/resume and control reads. There is no disk persistence.

## Dependencies and Integration Points

The file depends on ALSA core/control/PCM/TLV APIs, Linux PCI and device model APIs, delayed work and mutexes, AC97 public headers, `ac97_id.h`, and `ac97_patch.c`. It integrates with many PCI controller drivers that select `SND_AC97_CODEC` and provide `snd_ac97_bus_ops`. Optional procfs functions come from `ac97_proc.o`, declared in `ac97_local.h`.

## Risks and Edge Cases

Hardware probing intentionally writes to mixer registers to detect capabilities and must restore cache carefully. `snd_ac97_read_cache()` has the `set_bit()` line commented out in the first-read path, so callers rely on later writes/updates for accessed tracking. Some reset failures only warn and proceed because many systems tolerate partial response. Codec-specific register filtering is critical; unsupported reads can hang some hardware. S/PDIF updates temporarily disable S/PDIF and must restore state. Power-down logic changes analog and EAPD bits without changing mixer cache for master/headphone mute, which is intentional for resume but easy to break. Quirk application renames/removes controls and can fail when expected controls were not built.

## Test Signals

Build with AC97 codec as module and built-in, with and without `CONFIG_SND_PROC_FS`, `CONFIG_PM`, and `CONFIG_SND_AC97_POWER_SAVE`. Runtime tests include controller-driven bus creation, codec probe for audio and modem codecs, register cache read/write/update, mixer control enumeration and TLV values, S/PDIF default/status updates, variable-rate detection, suspend/resume restoring cached controls, delayed power-save transitions, and board quirk application by subsystem IDs and override strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_id.h -->
# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_id.h

## Purpose

`ac97_id.h` defines selected AC97 codec vendor/device ID constants used by the AC97 codec core and patch logic.

## Important APIs, Types, and Functions

The file is a macro-only header. It defines IDs for Asahi Kasei (`AK4540`, `AK4542`), Analog Devices (`AD1819`, `AD1881`, `AD1885`, `AD1980`, etc.), TriTech, SigmaTel/STAC, Cirrus Logic, Realtek ALC, Yamaha, VIA/ICEnsemble, C-Media, and STMicroelectronics codecs. It also defines `AC97_ID_CS_MASK` for Cirrus revision masking.

## Control Flow

There is no executable flow. Constants are consumed by conditionals and codec match tables in `ac97_codec.c` and included patch code to validate registers, select patch functions, and handle quirks.

## State and Persistence

No runtime state is stored. The constants become compile-time values in users of the header.

## Dependencies and Integration Points

It is included by `ac97_codec.c` and complements the larger `snd_ac97_codec_ids[]` table there. It must stay synchronized with codec IDs referenced in patch logic and register validation.

## Risks and Edge Cases

An incorrect ID or mask can route a codec to the wrong patch or register filter. The file contains only a subset of IDs from the larger table, so new logic should not assume every supported codec has a macro here. Some IDs encode revision bits, making masks important.

## Test Signals

Compile all AC97 code paths, verify ID macros used in switch/case statements match the table entries, and exercise hardware or emulated probes for representative AD, Realtek, Cirrus, SigmaTel, and C-Media codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_local.h -->
# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_local.h

## Purpose

`ac97_local.h` declares private cross-file helpers for the ALSA AC97 codec module, primarily shared between `ac97_codec.c` and optional procfs support.

## Important APIs, Types, and Functions

It declares `snd_ac97_get_name()` and `snd_ac97_update_bits_nolock()` for internal codec use. Under `CONFIG_SND_PROC_FS`, it declares bus and codec proc init/done helpers: `snd_ac97_bus_proc_init()`, `snd_ac97_bus_proc_done()`, `snd_ac97_proc_init()`, and `snd_ac97_proc_done()`. Without procfs, those helpers become no-op macros.

## Control Flow

There is no runtime control flow in the header. Its conditional declarations decide whether `ac97_codec.c` calls real procfs helpers or compiles calls away.

## State and Persistence

The header stores no state. Procfs helper implementations, when enabled, manage diagnostic entries outside this file.

## Dependencies and Integration Points

It depends on public AC97 types being visible before inclusion. It integrates `ac97_codec.c`, `ac97_proc.c`, and the `CONFIG_SND_PROC_FS` object selection in `sound/pci/ac97/Makefile`.

## Risks and Edge Cases

The no-op macros must match the call signatures of the real helpers. `snd_ac97_update_bits_nolock()` is explicitly lockless and assumes callers already hold `reg_mutex` or otherwise serialize register/cache access. Misuse can corrupt the AC97 register cache.

## Test Signals

Build AC97 with `CONFIG_SND_PROC_FS=y` and `n`, and run lockdep-oriented tests around control writes that call the nolock update helper through already-locked paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_local.h -->
