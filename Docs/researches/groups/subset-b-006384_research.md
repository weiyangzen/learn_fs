# Research: subset-b-006384

This grouped report covers the exact subset-b-006384 source list. Each file section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ali5451/ali5451.c -->
# sources/distributed-fs/ceph-client/sound/pci/ali5451/ali5451.c

## Purpose

`ali5451.c` is the ALSA PCI driver for the ALi M5451 AC97 audio controller. It registers a single PCI driver for `PCI_VENDOR_ID_AL` / `PCI_DEVICE_ID_AL_M5451`, exposes PCM playback/capture, optional S/PDIF controls, optional modem PCM when a secondary AC97 codec is present, a proc register dump, interrupt handling, and suspend/resume image save/restore.

The driver is hardware-register heavy. It programs the M5451 direct registers, channel register window, AC97 access ports, legacy PCI config bits, and ALi companion devices M1533 and M7101. Runtime persistence is in kernel memory and hardware registers only; there is no filesystem persistence.

## Important APIs, Types, and Functions

- Module parameters: `index`, `id`, `pcm_channels`, `spdif`, and legacy `enable`.
- Core device state: `struct snd_ali` tracks PCI devices, I/O base, IRQ, AC97 bus/codecs, PCM devices, S/PDIF mask, channel-control register mapping, spinlocks, and a suspend image.
- Voice/channel state: `struct snd_ali_voice` describes one hardware channel, its ALSA substream, optional extra voice, final ESO, period count, and ownership flags. `struct snd_alidev` keeps the 32 voice array plus allocation bitmap/counts.
- Register helpers: `snd_ali_5451_peek()` / `snd_ali_5451_poke()` wrap `inl`/`outl`; `snd_ali_codec_peek()` / `snd_ali_codec_poke()` implement AC97 read/write transactions.
- PCM operations: `snd_ali_open()`, `snd_ali_playback_prepare()`, `snd_ali_prepare()` for capture/modem, `snd_ali_trigger()`, `snd_ali_playback_pointer()`, `snd_ali_pointer()`, and close/free helpers.
- Channel allocation: `snd_ali_alloc_voice()`, `snd_ali_find_free_channel()`, `snd_ali_free_voice()`, `snd_ali_clear_voices()`.
- S/PDIF: `snd_ali_enable_spdif_in/out()`, `snd_ali_disable_spdif_in/out()`, `snd_ali_set_spdif_out_rate()`, `snd_ali_get_spdif_in_rate()`, and mixer callbacks `snd_ali5451_spdif_get/put()`.
- Initialization and registration: `snd_ali_create()`, `snd_ali_chip_init()`, `snd_ali_mixer()`, `snd_ali_build_pcms()`, `__snd_ali_probe()`, and `module_pci_driver(ali5451_driver)`.
- Power management: `ali_suspend()` and `ali_resume()` are wired through `DEFINE_SIMPLE_DEV_PM_OPS`.

## Control Flow

Probe allocates a devm-managed ALSA card, initializes the private `snd_ali`, enables the PCI function, sets a 31-bit coherent DMA mask, requests all PCI I/O regions, requests a shared IRQ, finds companion ALi M1533 and M7101 devices, initializes the 32 voice records, resets the AC97 codec path, initializes controller registers, enables address interrupts, builds AC97 mixers, creates the PCM devices, registers the proc dump, names the card, and finally registers it with ALSA.

AC97 access first waits for the controller ready bit and sample timer movement. Read and write commands are built into the AC97 read/write register, with secondary-codec and revision-specific flags. `AC97_GPIO_STATUS` writes are special-cased to the GPIO register.

PCM open allocates a hardware channel under `voice_alloc`, stores the voice in `runtime->private_data`, copies the playback/capture/modem hardware constraints, and sets buffer constraints. Playback may allocate an extra voice in `hw_params` when buffer and period layout requires it. Prepare writes channel registers: loop buffer address, current sample offset, end sample offset, rate delta, data format control, pan, volume, and envelope fields. Trigger walks linked ALSA substreams for this chip, marks voices running or stopped, updates interrupt-enable bits, then writes `ALI_START` or `ALI_STOP`.

Interrupt handling reads `ALI_MISCINT`, filters shared IRQs, reads per-channel `ALI_AINT` when address IRQ is set, iterates all 32 channels through `snd_ali_update_ptr()`, calls `snd_pcm_period_elapsed()` for active PCM voices, stops unexpected/stale voices, acknowledges channel bits, and clears miscellaneous target/mixer status bits.

Suspend switches ALSA power state, suspends AC97 codecs, snapshots global and per-channel registers into `struct snd_ali_image`, disables interrupts, and stops all channels. Resume restores channel and global registers, restarts the saved channel mask, restores interrupt state, resumes AC97 codecs, and marks D0.

## State and Persistence Behavior

Persistent runtime state is split between `struct snd_ali` and the hardware. `synth.chmap` and `synth.chcnt` are the software ownership source of truth for the 32 hardware voices. `spdif_mask` tracks ALSA mixer-selected S/PDIF enable bits and is mirrored to controller and southbridge registers. PCM runtime state lives in `struct snd_ali_voice` and ALSA runtime fields; channel positions come from hardware CSO registers. Suspend state is volatile in `struct snd_ali_image` and is not saved across module unload.

## Dependencies and Integration Points

This file integrates with ALSA core (`snd_card`, `snd_pcm`, `snd_ctl`, proc info), ALSA AC97 (`snd_ac97_bus`, `snd_ac97_mixer`, suspend/resume), Linux PCI/devres/resource/IRQ/DMA APIs, low-level x86-style port I/O accessors, and ALi southbridge/power-management companion PCI devices. It exposes normal ALSA PCM devices, modem-class PCM when a secondary codec exists, mixer controls, and `/proc/asound/.../ali5451` register dumps.

## Risks and Edge Cases

- Register polling waits up to 250 ms and clears busy bits on timeout; broken hardware can lead to failed AC97 operations or long probe/runtime stalls.
- Channel allocation relies on a 32-bit bitmap and hard-coded special channel IDs for PCM input, S/PDIF, surround, and modem paths.
- Playback with an extra voice has subtle trigger and interrupt behavior because interrupt enable may target either primary or extra voice.
- S/PDIF enablement touches M1533 config registers and M5451 SCTRL/SPDIF/global-control bits; incorrect state can reroute playback or leave special channels enabled.
- `snd_ali_pcm()` assigns `codec->pcm[0] = pcm` even when `device` is nonzero, which is notable when reasoning about modem PCM bookkeeping.
- IRQ sharing is filtered by `ALI_MISCINT`, but all channel interrupts are scanned when address IRQ is present.
- The suspend image covers fixed register windows; register layout assumptions are central to resume correctness.

## Test Signals

Useful validation is mostly hardware or emulation based: successful module load/probe, ALSA card registration, AC97 mixer creation, playback/capture open/prepare/trigger/pointer cycles, period interrupts, modem PCM creation on secondary codec hardware, S/PDIF mixer toggles, proc register dump readability, suspend/resume with active and idle streams, and no IRQ storms on shared lines. Static checks should cover lock usage, DMA mask/resource request errors, and unchecked HPI-like hardware return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ali5451/ali5451.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/als300.c -->
# sources/distributed-fs/ceph-client/sound/pci/als300.c

## Purpose

`als300.c` is the ALSA PCI driver for Avance Logic ALS300 and ALS300+ sound cards. It exposes one stereo 48 kHz AC97 PCM playback stream and one stereo 48 kHz AC97 capture stream, creates an AC97 mixer, handles chip-specific interrupt status registers for ALS300 versus ALS300+, and restores basic chip state after resume.

## Important APIs, Types, and Functions

- Module parameters: per-card `index`, `id`, and `enable` arrays.
- `struct snd_als300`: private card/chip state, including PCI device, I/O port, IRQ, AC97 codec, OPL3 pointer placeholder, PCM substream pointers, spinlock, chip type, and revision.
- `struct snd_als300_substream_data`: per-open stream state for the two-period pointer workaround, control register, and block-counter register.
- GCR helpers: `snd_als300_gcr_read()` and `snd_als300_gcr_write()`.
- Interrupt setup/control: `snd_als300_set_irq_flag()`, `snd_als300_interrupt()`, and `snd_als300plus_interrupt()`.
- AC97 bus callbacks: `snd_als300_ac97_read()`, `snd_als300_ac97_write()`, and `snd_als300_ac97()`.
- PCM ops: stream open/close, `snd_als300_playback_prepare()`, `snd_als300_capture_prepare()`, `snd_als300_trigger()`, and `snd_als300_pointer()`.
- Device lifecycle: `snd_als300_init()`, `snd_als300_create()`, `snd_als300_probe()`, PM callbacks, and `module_pci_driver(als300_driver)`.

## Control Flow

Probe uses a static ALSA card index cursor, honors `enable[dev]`, allocates a devm ALSA card, then calls `snd_als300_create()`. Creation enables PCI, sets a 28-bit coherent DMA mask, requests all regions, records BAR0 as the I/O base, chooses the ALS300 or ALS300+ interrupt handler from PCI `driver_data`, requests a shared IRQ, initializes registers, builds AC97, and creates the PCM device.

`snd_als300_init()` reads the revision from `MISC_CONTROL`, sets DRAM mode, enables IRQ output with revision-specific polarity handling, unmutes hardware routes, zeros volume, and ensures playback is stopped. Resume reuses this initializer and resumes AC97.

Open allocates small per-stream private data and records the active playback or capture substream pointer. Prepare stops transfer start, writes period size minus one into the stream control register, and programs start/end DMA addresses. Trigger toggles `TRANSFER_START` for start/stop and `FIFO_PAUSE` for pause/release. Pointer reads the hardware block counter, inverts the remaining-in-period value into a current byte position, and uses `period_flipflop` to choose first versus second half of the two-period buffer.

Interrupts acknowledge chip status quickly, flip `period_flipflop`, and call `snd_pcm_period_elapsed()` for the active substream. ALS300+ uses separate general, MPU, and DRAM interrupt status registers and only acknowledges playback/capture status currently.

## State and Persistence Behavior

The driver keeps only volatile in-kernel and hardware state. `period_flipflop` is the key runtime state used to compensate for hardware block counters reporting position within the current period rather than whole-buffer position. Active substream pointers are stored on the chip object and cleared on close. Suspend does not snapshot PCM registers; resume reinitializes the chip and AC97 codec, so active streams depend on ALSA PM sequencing.

## Dependencies and Integration Points

The driver integrates with Linux PCI/resource/IRQ/DMA APIs, ALSA card/PCM/control/initval frameworks, ALSA AC97 mixer support, and low-level port I/O. It uses managed PCM buffers with `SNDRV_DMA_TYPE_DEV`. OPL3/gameport/MPU401 are listed as TODOs and not integrated in this file.

## Risks and Edge Cases

- Pointer accuracy depends on always using exactly two periods and correctly flipping on each interrupt.
- ALS300 interrupt polarity differs by revision and ALS300+ status layout; `snd_als300_set_irq_flag()` encodes this compatibility rule.
- AC97 read/write polling loops do not return timeout errors; a failed codec transaction may yield stale/default read values.
- ALS300+ handler leaves non-playback/capture interrupt sources mostly unacknowledged because those devices are not enabled.
- Fixed 48 kHz, 16-bit stereo constraints reflect hardware AC97 mode and may surprise callers expecting flexible ALSA conversion in hardware.

## Test Signals

Expected signals are probe success for both PCI IDs, correct card shortname revision formatting, AC97 mixer creation, one playback and one capture PCM, exactly two periods enforced by runtime hardware constraints, playback/capture IRQs advancing periods, pause/resume toggling FIFO state, shared IRQ returning `IRQ_NONE` when status is clear, and suspend/resume reinitializing mixer and interrupt state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/als300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/als4000.c -->
# sources/distributed-fs/ceph-client/sound/pci/als4000.c

## Purpose

`als4000.c` is the ALSA PCI driver for Avance Logic ALS4000 sound cards. The ALS4000 is treated as a PCI SoundBlaster-like device with an SB DSP/mixer, OPL3 synth, MPU-401 UART, optional gameport, and PCI-managed DMA/IRQ support. The driver creates a full-duplex PCM device with separate playback and capture paths, plus SB mixer, raw MIDI, OPL3 hwdep, and optional gameport integration.

## Important APIs, Types, and Functions

- Module parameters: per-card `index`, `id`, `enable`, and optional `joystick_port`.
- `struct snd_card_als4000`: card-private wrapper holding PCI device, base I/O address, created `struct snd_sb`, and optional gameport.
- Register enums describe PCI I/O BAR offsets, GCR registers, and SB control-register aliases.
- Low-level helpers: `snd_als4k_iobase_readb/writel()`, `snd_als4k_gcr_read/write()`, and `snd_als4_cr_read/write()`.
- DMA/rate/format setup: `snd_als4000_set_rate()`, `snd_als4000_set_capture_dma()`, `snd_als4000_set_playback_dma()`, `snd_als4000_get_format()`, playback/capture command tables.
- PCM ops: `snd_als4000_playback_prepare()`, `snd_als4000_capture_prepare()`, playback/capture triggers, pointers, opens, and closes.
- Interrupt handler: `snd_als4000_interrupt()`.
- Device setup: `snd_als4000_set_addr()`, `snd_als4000_configure()`, `__snd_card_als4000_probe()`, PM callbacks, and `module_pci_driver(als4000_driver)`.

## Control Flow

Probe honors the module `enable` array, enables the PCI device, sets a 24-bit coherent DMA mask, requests all BAR regions, enables I/O decoding and bus mastering, allocates an ALSA card, disables legacy ISA address mappings, creates an ALSA SB DSP instance with the ALS4000 interrupt handler, stores the PCI device and alternate I/O base on `struct snd_sb`, configures control registers and GCR DMA state, creates MPU-401 UART, PCM, SB mixer, OPL3 hwdep if present, optional gameport, and registers the card.

Playback prepare computes ALS4000 format flags from ALSA runtime format/channels, programs sample rate through SB DSP commands, writes PCI DMA address/count to GCR DMA0 registers, sends the appropriate DSP auto-init output command and format/count bytes, then sends the DMA-off command so trigger can start cleanly. Capture prepare similarly sets the sample rate and FIFO2 PCI address/count, then writes FIFO2 block length through ALS4K control registers under the mixer lock.

Playback trigger sends DSP DMA on/off commands and maintains SB rate-lock bits. Capture trigger writes FIFO2 control values and maintains the capture rate-lock bit. Pointers read current PCI FIFO addresses from GCR registers and convert low 16 bits to frames.

The interrupt handler reads PCI interrupt source bits for SB DMA, CR1E capture FIFO, and MPU. It calls `snd_pcm_period_elapsed()` for active playback/capture substreams, dispatches MPU interrupts to `snd_mpu401_uart_interrupt()`, acknowledges the PCI IRQ register, reads SB IRQ status under the mixer lock, acknowledges 8-bit/16-bit/MPU/CR1E status paths, and returns `IRQ_RETVAL()` based on handled bits.

## State and Persistence Behavior

Runtime state lives mostly in ALSA's `struct snd_sb`: current playback/capture substreams, `playback_format`, `capture_format`, mode/rate-lock bits, raw MIDI, mixer, and I/O ports. `struct snd_card_als4000` keeps card-level I/O and gameport state. No on-disk persistence exists. Suspend only suspends the SB mixer; resume reconfigures hardware, resets DSP, resumes mixer, and restores gameport mapping if registered.

## Dependencies and Integration Points

The file depends on ALSA core PCM/rawmidi/SB/MPU401/OPL3 helpers, Linux PCI/resource/DMA APIs, optional Linux gameport support, and direct port I/O. The driver reuses generic ALSA SB infrastructure while adding ALS4000-specific PCI DMA, interrupt, and capture FIFO handling.

## Risks and Edge Cases

- Comments explicitly flag uncertainty around IRQ sharing, PCI versus SB IRQ acknowledgement order, and whether some status can be optimized or read safely without locks.
- Hardware was historically reverse engineered; several setup sequences depend on datasheet-specific register magic.
- Playback prepare notes audible clicks/pops after subsequent playback starts, suggesting incomplete hardware quiescing.
- DMA mask is only 24-bit, so high memory systems rely on ALSA/DMA constraints.
- Capture control uses SB mixer-register locking plus PCI GCR locking; lock ordering is important.
- Optional gameport maps legacy I/O addresses and must reserve/disarm them correctly.

## Test Signals

Probe should create ALS4000 card, PCM, SB mixer, MPU401, optional OPL3, and optional gameport. Playback/capture should support 8/16-bit signed/unsigned mono/stereo at 4-48 kHz, period interrupts should arrive from the correct PCI/SB bits, raw MIDI interrupts should dispatch, shared IRQs should return false when no relevant bits are set, suspend/resume should restore mixer/DSP/configuration, and joystick configuration should reserve and release requested legacy I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/als4000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/Makefile

## Purpose

This Makefile declares the ALSA AudioScience HPI PCI driver module composition. When `CONFIG_SND_ASIHPI` is enabled, Kbuild links `snd-asihpi.o` from the ASI ALSA wrapper, HPI ioctl bridge, message helpers, common HPI code, debug/firmware/OS support, and hardware-family backends for ASI6000 and ASI6205-era devices.

## Important APIs, Types, and Functions

- `snd-asihpi-y` lists the object files that make one module: `asihpi.o`, `hpioctl.o`, `hpimsginit.o`, `hpicmn.o`, `hpifunc.o`, `hpidebug.o`, `hpidspcd.o`, `hpios.o`, `hpi6000.o`, `hpi6205.o`, and `hpimsgx.o`.
- `obj-$(CONFIG_SND_ASIHPI) += snd-asihpi.o` binds module build to the kernel configuration option.

## Control Flow

There is no runtime control flow in the Makefile. Build flow is Kbuild-driven: if the config symbol is built-in or module-enabled, the listed objects are compiled and linked into `snd-asihpi`.

## State and Persistence Behavior

The file has no runtime state. Its persistent effect is the build graph: adding or removing source files here changes which HPI implementation pieces are present in the resulting module.

## Dependencies and Integration Points

It integrates with Linux kernel Kbuild and the surrounding `sound/pci/asihpi` source set. `asihpi.o` provides the ALSA-facing PCI driver, while the remaining objects provide HPI message dispatch, ioctl/hwdep handling, DSP code loading, OS services, and adapter-family implementations.

## Risks and Edge Cases

- Missing an object here can produce link failures or a module that lacks a needed HPI backend.
- The object list makes the ALSA wrapper tightly coupled to internal HPI layers, so build-time ordering and symbol availability matter.
- Only `CONFIG_SND_ASIHPI` gates the module in this file; lower-level dependencies must be expressed in Kconfig.

## Test Signals

Kbuild should compile all listed objects and link `snd-asihpi.o` without unresolved symbols when `CONFIG_SND_ASIHPI=m` or `y`. Runtime smoke tests should confirm `asihpi.c` can call into HPI initialization, ioctl, and adapter-probe functions supplied by these companion objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/asihpi.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/asihpi.c

## Purpose

`asihpi.c` is the ALSA PCI wrapper for AudioScience ASI5xxx, ASI6xxx, ASI87xx, and ASI89xx adapters using the AudioScience Hardware Programming Interface. It bridges HPI streams and mixer controls into ALSA PCM, mixer, proc, and hwdep devices. Low-level adapter discovery, DSP communication, and ioctl handling are delegated to companion HPI files built into `snd-asihpi`.

## Important APIs, Types, and Functions

- Module parameters: per-card `index`, `id`, `enable`, dynamic `enable_hpi_hwdep`, and `build_info`.
- `struct snd_card_asihpi`: ALSA card private state, PCI and HPI adapter pointers, low-latency stream pointer, PCM start/stop function pointers, mixer handle, sample-clock cache, capability flags, update interval, and channel limits.
- `struct snd_card_asihpi_pcm`: per-stream timer, HPI stream handle, attached host-buffer state, byte offsets, period/buffer sizing, data rate, drained counter, substream pointer, and HPI format.
- HPI stream shims: `hpi_stream_host_buffer_attach()`, `hpi_stream_host_buffer_detach()`, `hpi_stream_start/stop()`, `hpi_stream_get_info_ex()`, and grouping wrappers choose in-stream or out-stream APIs based on HPI handle object type.
- PCM setup: `snd_card_asihpi_format_alsa2hpi()`, `snd_card_asihpi_pcm_samplerates()`, `snd_card_asihpi_pcm_hw_params()`, `snd_card_asihpi_hw_free()`, open/close/prepare/pointer callbacks for playback and capture, and `snd_card_asihpi_pcm_new()`.
- Completion engines: `snd_card_asihpi_pcm_timer_start/stop()`, `snd_card_asihpi_pcm_int_start/stop()`, `snd_card_asihpi_timer_function()`, and `snd_card_asihpi_isr()`.
- Mixer controls: `struct hpi_control`, `asihpi_ctl_init()`, `ctl_add()`, volume, mute, level, AES/EBU, tuner, meter, mux, channel-mode, and sample-clock control callbacks.
- Card lifecycle: `snd_asihpi_probe()`, `snd_asihpi_remove()`, HPI hwdep callbacks, proc info callbacks, PCI table, module init/exit.

## Control Flow

Module init calls `asihpi_init()` then registers a PCI driver for supported AudioScience/TI adapter PCI IDs. Probe first calls low-level `asihpi_adapter_probe()`, retrieves the `struct hpi_adapter` from PCI drvdata, and tries to allocate the ALSA card at the hardware adapter index before falling back to the configured ALSA index. It stores reciprocal ALSA/HPI pointers, queries adapter properties for grouping, MRX/sample-rate conversion, update interval, host-buffer DMA support, and current channel counts, selects timer or interrupt completion mode, creates PCM and mixer devices, sets the default local sample rate where a sample-clock control exists, creates proc and hwdep endpoints, names/registers the card, and increments the device cursor.

PCM open allocates per-stream state, opens an HPI in-stream or out-stream handle, sets up a timer, builds dynamic ALSA hardware constraints from adapter capabilities, queries HPI-supported formats/rates, and applies period-size/update-interval constraints. `hw_params` creates the HPI format, resets/configures capture streams immediately, optionally grants the adapter the ALSA DMA buffer through an internal HPI host-buffer command, and records byte-rate, period, and buffer sizes.

Trigger start walks linked ALSA substreams for the same card and stream direction. Playback preloads one period into each HPI outstream, optionally groups streams through HPI, starts the selected timer or interrupt engine, then starts the master stream when capture or non-DMA playback requires it. Stop halts the completion engine, forces linked streams back to setup, stops/resets HPI streams, and resets HPI grouping. Pause release/push starts or stops both the completion engine and HPI stream.

`snd_card_asihpi_timer_function()` is the shared polling/IRQ bottom-half equivalent. It reads HPI stream state and buffer counters for all linked same-direction streams, computes a modulo minimum buffer position and transferable byte count, schedules the next timer expiry, transfers whole periods between ALSA DMA buffers and HPI streams when software copying is needed, updates host/read/write offsets, stores DMA offsets for ALSA pointer callbacks, detects playback drain/xrun, and calls `snd_pcm_period_elapsed()`.

Mixer creation opens an HPI mixer, enumerates up to 2000 HPI controls by index, skips disabled controls, maps HPI node IDs to ALSA-friendly names, assigns subindices for duplicated controls, and creates ALSA controls for volume, level, mux, channel mode, meter, sample clock, tuner, AES/EBU transmitter, and AES/EBU receiver. Unsupported control types are skipped unless mixer dumping is enabled.

Removal disables low-latency IRQ callbacks and adapter IRQ rate, frees the ALSA card, clears `hpi->snd_card`, and calls `asihpi_adapter_remove()`.

## State and Persistence Behavior

The driver maintains volatile ALSA/HPI session state only. `struct snd_card_asihpi` caches adapter capabilities and sample-clock source enumeration. `struct snd_card_asihpi_pcm` tracks ring-buffer offsets independently from HPI counters, including host read/write offset, adapter DMA offset, elapsed DMA offset, and drain count. Host-buffer attachment state is cleared in `hw_free`. Mixer values are read/written directly through HPI calls; any nonvolatile mixer storage is an HPI/adapter feature, not implemented in this wrapper. The default local sample rate is set during probe from `adapter_fs`.

## Dependencies and Integration Points

This file depends on internal HPI headers and companion objects (`hpi_internal.h`, `hpimsginit.h`, `hpioctl.h`, `hpicmn.h`), ALSA core PCM/control/proc/hwdep APIs, Linux PCI/module/timer/wait/slab APIs, and HPI public APIs from `hpi.h`. User space sees ALSA PCM devices, ALSA mixer controls, `/proc/asound/.../info`, and an optional `/dev/snd/hwC#D0` HPI hwdep ioctl bridge.

## Risks and Edge Cases

- Timer-based ring accounting is complex and sensitive to modulo arithmetic, linked stream grouping, playback preload size, and HPI-reported byte counters.
- Low-latency interrupt mode keeps only one `llmode_streampriv` pointer per card; the code assumes the hardware mode has a single stream shape.
- `hw_params` returns `-ENOMEM` for host-buffer attach failure even when the root cause is an HPI error; diagnostics rely on debug logs.
- Several mixer callbacks always report change as true and do not cache old values.
- Mixer enumeration silently skips many HPI control types, so adapter features may not be visible through ALSA controls.
- Sample-clock source/name tables rely on compile-time assertions matching HPI enum ranges.
- Error conversions are uneven: some HPI errors are logged but not propagated, while probe/setup paths treat others as fatal.
- The hwdep ioctl bridge is dynamically gated by `enable_hpi_hwdep`; open/ioctl/release can return `-ENODEV` after device creation.

## Test Signals

Important tests include PCI probe/remove with HPI adapter backends, successful ALSA card index fallback, PCM open/close for all HPI streams, format/rate enumeration with and without MRX, DMA host-buffer attach/detach, playback/capture start/stop/pause in timer and interrupt modes, linked stream grouping, xrun detection on drained playback, mixer enumeration across representative adapter topologies, sample-clock source/rate controls, hwdep enable/disable behavior, proc output, and module unload with active or recently stopped streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/asihpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi.h

## Purpose

`hpi.h` defines the public AudioScience Hardware Programming Interface used by the ASI driver stack. It is a low-level adapter abstraction for digital audio hardware, describing public constants, enum values, packed data structures, and function prototypes for subsystem discovery, adapter management, streams, mixers, controls, and format creation. `asihpi.c` consumes these definitions to map HPI capabilities to ALSA devices and controls.

## Important APIs, Types, and Functions

- Format and stream enums: `enum HPI_FORMATS`, `enum HPI_STREAM_STATES`, MPEG ancillary/mode enums, and `struct hpi_format`.
- Mixer graph enums: `enum HPI_SOURCENODES`, `enum HPI_DESTNODES`, and `enum HPI_CONTROLS` define node/control identifiers used to enumerate mixer topology.
- Adapter properties and modes: `enum HPI_ADAPTER_PROPERTIES`, `enum HPI_ADAPTER_MODE_CMDS`, `enum HPI_ADAPTER_MODES`, and capability macros.
- Control attributes: volume units and sentinels, AES/EBU formats/errors, tuner bands/modes/status, channel modes, sample-clock sources, filter types, async event sources, and PAD string lengths.
- Errors and limits: `enum HPI_ERROR_CODES`, `HPI_MAX_ADAPTERS`, `HPI_MAX_STREAMS`, `HPI_MAX_CHANNELS`, `HPI_MAX_ANC_BYTES_PER_FRAME`, and related constants.
- Packed structures: `struct hpi_format`, `struct hpi_anc_frame`, and `struct hpi_async_event`.
- Public functions: subsystem discovery (`hpi_subsys_*`), adapter open/close/info/property/mode APIs, outstream/instream open/read/write/start/stop/reset/query/group/host-buffer APIs, mixer open/get-control/store APIs, and control-specific volume, meter, tuner, AES/EBU, mux, sample-clock, microphone, EQ, compander, Cobranet, tone/silence detector, and `hpi_format_create()` APIs.

## Control Flow

The header has no executable control flow, but it defines the command surface used by HPI implementations and clients. Typical control flow begins with subsystem/adapter discovery, opening an adapter, querying adapter info/properties, opening streams or the mixer, querying formats or controls, then issuing stream data movement or control get/set commands. Stream operations are handle-based: outstream and instream handles are opened by adapter index/stream index and later passed to read/write/start/stop/reset/group/host-buffer functions. Mixer control flow is mixer-handle based and then control-handle based.

## State and Persistence Behavior

The header defines state identifiers but stores no state. Persistent or nonvolatile behavior appears only as API contracts, notably adapter mode/SSX2 settings, mixer store commands, nonvolatile memory error codes, firmware update capability, and adapter properties. Runtime state such as stream stopped/playing/recording/drained, async event sequence, mixer control values, and sample clock source is maintained by HPI implementation code and hardware.

## Dependencies and Integration Points

`hpi.h` includes Linux integer types and defines `HPI_BUILD_KERNEL_MODE`, making it a kernel-mode HPI API header. It integrates with internal HPI implementation files (`hpifunc`, message dispatch, adapter backends) and ALSA-facing code. It also carries comments about Windows equivalents for formats, indicating the API is cross-platform in origin even though this copy is kernel-facing.

## Risks and Edge Cases

- Enum values are ABI-like: comments warn that adding source/destination/control types requires updating debug tables and that control types above 255 affect DSP bit packing.
- Packed structure layout matters for message compatibility.
- Some names contain historical spellings or aliases; callers must use numeric values consistently.
- Error-code ranges are constrained: driver errors, adapter errors, stream errors, mixer/control errors, ioctl mutex timeout, and backend compatibility all share one enum.
- Many APIs accept raw pointers and fixed-size arrays, so callers must ensure buffer sizes and channel counts match HPI expectations.
- HPI supports both local and networked adapters; adapter indexes >= 100 are reserved for networked adapters.

## Test Signals

Compile-time validation should confirm all users see matching enum ranges and structure layouts. Functional tests should exercise `hpi_format_create()`, adapter property queries used by `asihpi.c`, stream open/read/write/start/stop/reset/group/host-buffer calls, mixer enumeration/control get-set paths, sample-clock source/rate queries, error-code translation, and async event structures where supported by backend hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi.h -->
