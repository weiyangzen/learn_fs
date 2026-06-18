# Research: subset-b-006396

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/es1938.c -->
# sources/distributed-fs/ceph-client/sound/pci/es1938.c

## Purpose

This file is the ALSA PCI driver for ESS Solo-1 compatible chips, matching PCI vendor ESS device `0x1969`. It exposes one ALSA card with two playback substreams, one capture substream, mixer controls, optional OPL3 and MPU-401 devices, optional gameport support, interrupt handling, and suspend/resume restoration. The implementation is centered on direct I/O to the Solo-1 PCI, SoundBlaster-compatible mixer, and distributed DMA register windows.

## Important APIs, Types, and Functions

- `struct es1938` is the card-private state. It stores I/O base addresses, IRQ, PCI/card/PCM/rawmidi pointers, active stream flags, DMA start/size/shift values, substream pointers, spinlocks, optional gameport, and mixer register save state for PM.
- Module parameters are `index`, `id`, and `enable`.
- Register access helpers include `snd_es1938_mixer_write/read/bits()`, `snd_es1938_write_cmd()`, `snd_es1938_get_byte()`, `snd_es1938_write/read/bits()`, and `snd_es1938_reg_read/bits()`.
- PCM callbacks are split by hardware engine: `snd_es1938_capture_*`, `snd_es1938_playback1_*` for Audio2, and `snd_es1938_playback2_*` for Audio1/DDMA. The public ALSA ops dispatch through `snd_es1938_playback_prepare/trigger/pointer()`.
- Mixer callbacks are generated around `ES1938_SINGLE*` and `ES1938_DOUBLE*` macros plus special handlers for capture source, spatializer, and hardware volume button state.
- Device lifecycle is handled by `snd_es1938_create()`, `snd_es1938_new_pcm()`, `snd_es1938_mixer()`, `__snd_es1938_probe()`, `snd_es1938_free()`, and `module_pci_driver()`.
- PM entry points are `es1938_suspend()` and `es1938_resume()` through `DEFINE_SIMPLE_DEV_PM_OPS`.

## Control Flow

Probe allocates an ALSA card, verifies all five PCI I/O BARs, enables the PCI device, enforces a 24-bit DMA mask, requests regions and IRQ, records BAR addresses, sets `ddma_port`, and calls `snd_es1938_chip_init()`. Initialization resets the chip, enables PCI bus mastering, disables legacy audio, configures DDMA and IRQ policy, enables Audio1/Audio2/MPU/hardware-volume interrupts, and clears DMA. Probe then creates the PCM device, adds mixer controls, attempts OPL3 and MPU-401 setup, registers the gameport if configured, registers the card, and stores the card in PCI drvdata.

PCM open records the relevant substream pointer. Capture and playback substream 1 cannot coexist with playback substream 2 because capture and the second playback path both use the Audio1/DDMA engine. Prepare computes byte counts, format flags, DMA shifts, clock divisors, reload counters, format registers, and DMA registers. Trigger toggles `chip->active` bits and writes either Audio2 mixer/IO registers or Audio1 controller registers. Pointer callbacks read the corresponding DMA counters, with extra stability checks for capture and playback2 because the hardware can return transient garbage.

The interrupt handler reads `IRQCONTROL`. Audio1 interrupts acknowledge via SB status and dispatch to capture or playback2 depending on `chip->active`; Audio2 interrupts clear the mixer IRQ bit and dispatch to playback1. Hardware-volume IRQs notify ALSA controls for hardware and master controls, then acknowledge through mixer register `0x66`. MPU IRQs are delegated to `snd_mpu401_uart_interrupt()` when rawmidi exists.

Suspend saves selected mixer/controller registers, disables IRQ generation, frees the IRQ, and marks the card D3hot. Resume reacquires the IRQ, reinitializes the chip, replays saved register values through mixer or controller paths, and marks D0.

## State and Persistence Behavior

Runtime state is almost entirely in `struct es1938`: stream ownership, active engine bits, DMA addresses, last valid capture pointer, mixer-control pointers for notifications, and saved PM registers. Hardware mixer state is mirrored only during suspend by `chip->saved_regs`; normal control reads query device registers. Capture intentionally disables mmap and uses `.copy` because captured data starts at `dma_area + 1` and wraps by one byte. ALSA-managed PCM buffers are allocated with a fixed 64 KiB size and constrained below `0xff00`.

## Dependencies and Integration Points

The driver integrates with ALSA core (`snd_card`, `snd_pcm`, `snd_ctl`, TLV controls), PCI managed resource APIs, raw MIDI MPU-401 support, OPL3 hwdep/timer support, gameport when reachable, Linux IRQ and PM frameworks, and low-level `inb/outb/outw/outl` I/O. It depends on ESS Solo-1 register semantics and on a 24-bit coherent DMA mask.

## Risks and Edge Cases

- The source comments document known playback IRQ timing failures and occasional spurious interrupts.
- Capture pointer logic works around invalid DMA address/count reads; regressions here can cause period drift or underruns.
- Capture and playback2 share Audio1/DDMA and are mutually exclusive; open/close paths must keep substream pointers consistent.
- The hardware-volume IRQ assumes the four stored `snd_kcontrol` pointers are valid until controls are freed.
- PM frees and reacquires a non-managed IRQ, so suspend/resume error handling must keep `chip->irq` and `card->sync_irq` coherent.
- DMA is limited to 24-bit addressing and small buffers.

## Test Signals

Useful validation includes PCI probe and remove, playback on both substreams, capture with wraparound periods, simultaneous playback1 plus capture, rejection of capture plus playback2, ALSA mixer get/put coverage, OPL3/MPU availability, hardware volume button notifications, suspend/resume with mixer state retention, and stress loops with small periods to exercise the documented IRQ timing quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/es1938.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/es1968.c -->
# sources/distributed-fs/ceph-client/sound/pci/es1968.c

## Purpose

This file implements the ALSA PCI driver for ESS Maestro 1, Maestro 2, and Maestro 2E audio devices. It drives the Maestro APU and wavecache hardware as PCM playback/capture engines, exposes an AC97 mixer, optional MPU-401, optional gameport, optional hardware-volume input events, and optional TEA575x radio support.

## Important APIs, Types, and Functions

- `struct es1968` is the card state, including module configuration, chip type, clock, DMA arena, AC97/rawmidi handles, indirect register caches, APU allocation map, active substream list, Bob timer state, PM state, optional gameport/input/radio fields, and work item for hardware volume.
- `struct esschan` is per-open PCM state. It stores assigned APUs, APU modes, DMA/mix buffers, format flags, current pointers, period accounting, Bob timer frequency, and list linkage.
- `struct esm_memory` describes carved chunks from one preallocated DMA arena.
- Low-level register helpers are `maestro_write/read()`, `apu_set/get_register()`, `wave_set/get_register()`, and AC97 bus callbacks `snd_es1968_ac97_write/read()`.
- PCM setup flows through `snd_es1968_playback_setup()`, `snd_es1968_capture_setup()`, `snd_es1968_pcm_prepare()`, `snd_es1968_pcm_trigger()`, and `snd_es1968_pcm_pointer()`.
- DMA arena management is provided by `snd_es1968_init_dmabuf()`, `snd_es1968_new_memory()`, `snd_es1968_free_memory()`, and `snd_es1968_hw_params/free()`.
- Lifecycle functions include `snd_es1968_create()`, `snd_es1968_chip_init()`, `snd_es1968_pcm()`, `snd_es1968_mixer()`, `__snd_es1968_probe()`, and `snd_es1968_free()`.

## Control Flow

Probe validates the module slot, creates the ALSA card, clamps `total_bufsize`, enables the PCI device, enforces a 28-bit DMA mask, requests I/O regions and IRQ, initializes locks/lists/APU maps, applies PM allowlist policy, initializes hardware, optionally sets up radio support, and then creates PCM and AC97 mixer devices. It conditionally enables MPU-401 after checking a denylist, may create a gameport and input device, starts IRQs, measures the chip clock when no module clock is supplied, registers the card, and stores drvdata.

The PCM creation path allocates one low DMA arena, writes the wavecache PCMBAR registers, and creates a PCM device with configurable playback and capture substream counts. Open allocates APU pairs: playback needs one pair, capture needs one input-mixer pair plus one sample-rate-converter pair and a 1 KiB mix buffer. `hw_params` carves a stream buffer from the shared DMA arena. Prepare computes format flags, wave shifts, period sizes, Bob timer frequency, and programs the APUs and wavecache. Trigger starts or stops the assigned APUs under `substream_lock` and increments/decrements the Bob timer client count.

The Bob timer is a hardware timer programmed by `snd_es1968_bob_start()` and shared by all running streams. Its interrupt drives `snd_es1968_update_pcm()`, which calculates hardware-pointer deltas, accumulates bytes, and calls `snd_pcm_period_elapsed()` when enough bytes have advanced. The IRQ handler also handles MPU events and schedules `hwvol_work` for hardware-volume interrupts. During clock measurement, sound IRQs track APU wrap counts.

Capture is more involved than playback: input mixer APUs route codec input into a temporary mix buffer, then SRC APUs move samples into the real PCM buffer. Playback programs linear or stereo APUs and routes them through the wavecache.

## State and Persistence Behavior

The driver persists stream runtime in `esschan` instances linked from `chip->substream_list`. DMA memory is a single contiguous allocation split into aligned chunks and coalesced on free; the hardware requires the arena to remain under the 28-bit boundary. APU register values and Maestro indirect registers are cached in `apu_map` and `maestro_map`. AC97 mixer state is owned by ALSA AC97 code. PM is enabled only according to module policy and subsystem allowlist; suspend stops Bob and suspends AC97, while resume reinitializes the chip, restores PCMBAR, restarts IRQs, resumes AC97, reprograms existing stream APUs, and restarts Bob if clients remain.

## Dependencies and Integration Points

The driver integrates with PCI, ALSA PCM and AC97 layers, MPU-401 UART, optional gameport, optional Linux input device for hardware keys, optional V4L2/TEA575x radio support, DMA allocation APIs, workqueues, mutex/spinlock primitives, and low-level I/O port access. It depends on Maestro APU/wavecache indirect register behavior, a constrained DMA address range, and AC97 codec presence.

## Risks and Edge Cases

- The shared DMA arena and chunk splitter are fragile: fragmentation or size miscalculation can reject opens despite total memory being sufficient.
- APU pair allocation is not protected by a dedicated lock, so the open/close call context relies on ALSA serialization.
- The hardware can address only low 28-bit PCI memory, and all allocations must fit the wavecache model.
- Bob timer period accounting is software-derived and sensitive to pointer wrap, jitter suppression, and rate measurement.
- PM is deliberately allowlisted because earlier generic PM caused machine-specific failures.
- Radio support returns early in `snd_es1968_create()` for non-ESS subsystem vendors under `CONFIG_SND_ES1968_RADIO`, which changes the normal initialization path.
- Hardware-volume work reads raw I/O state and either mutates AC97 master controls or reports input events depending on configuration.

## Test Signals

Validation should include probe on all three supported PCI IDs, AC97 mixer reads/writes, playback and capture stream allocation counts, concurrent stream starts/stops, DMA arena exhaustion and reuse, Bob timer period callbacks, clock measurement logging, suspend/resume on allowlisted systems, MPU denylist behavior, optional hardware-volume input/control paths, and TEA575x GPIO radio detection when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/es1968.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/fm801.c -->
# sources/distributed-fs/ceph-client/sound/pci/fm801.c

## Purpose

This file is the ALSA PCI driver for ForteMedia FM801-based sound cards, including Gallant Odyssey Sound 4 IDs. It exposes PCM playback/capture, AC97 mixer and optional secondary codec support, MPU-401 MIDI, OPL3 FM, optional multichannel playback, suspend/resume state, and optional TEA575x radio support including tuner-only boards.

## Important APIs, Types, and Functions

- `struct fm801` stores I/O base, IRQ, multichannel/secondary codec state, tuner flags, playback and capture ping-pong DMA state, AC97/card/PCM/rawmidi pointers, current substream pointers, spinlock, optional V4L2/TEA575x state, and saved PM registers.
- Module parameters are `index`, `id`, `enable`, `tea575x_tuner`, and `radio_nr`.
- AC97 helpers are `fm801_ac97_is_ready()`, `fm801_ac97_is_valid()`, `snd_fm801_codec_write()`, and `snd_fm801_codec_read()`.
- PCM callbacks are `snd_fm801_playback_prepare/trigger/pointer/open/close()` and their capture equivalents. `snd_fm801_interrupt()` owns ping-pong buffer advancement.
- Mixer controls use `FM801_SINGLE`, `FM801_DOUBLE`, and `FM801_DOUBLE_TLV` helpers plus a digital capture source enum.
- Device lifecycle is handled by `snd_fm801_create()`, `snd_fm801_chip_init()`, `snd_fm801_pcm()`, `snd_fm801_mixer()`, `__snd_card_fm801_probe()`, and `snd_fm801_free()`.
- PM callbacks are `snd_fm801_suspend()` and `snd_fm801_resume()`.

## Control Flow

Probe allocates an ALSA card, enables PCI resources, initializes driver state, detects FM801-AU multichannel capability from revision `>= 0xb1`, resets the primary codec unless tuner-only mode is requested, probes secondary AC97 codec addresses for multichannel cards, requests IRQ and bus mastering for normal audio cards, initializes registers, sets up optional TEA575x support, and returns. The higher-level probe then fills card names. If tuner-only is set it skips PCM, mixer, MIDI, and OPL3 creation; otherwise it creates the PCM device, AC97 mixer plus FM801 controls, MPU-401 UART, and OPL3 hwdep, then registers the card.

PCM prepare programs playback or capture control bits, sample-rate index, format bits, channel mode, period count, initial DMA base addresses for buffer 1 and buffer 2, and cached positions. Trigger sets/clears `START`, `PAUSE`, and `IMMED_STOP` bits. The IRQ handler acknowledges status first, updates the completed buffer index and logical position, programs the just-freed hardware buffer to the next period address, and calls `snd_pcm_period_elapsed()`. Pointer callbacks combine the cached period position with the live down counter and compensate if an IRQ is pending but not yet processed.

Mixer setup creates a normal AC97 bus and primary codec, optionally adds a secondary codec, then appends FM801-native mixer controls and multichannel/S/PDIF controls. TEA575x support bit-bangs GPIO pins through board-specific maps and may autodetect tuner wiring.

## State and Persistence Behavior

Playback and capture each maintain a two-buffer queue in cached fields (`ply_buf`, `ply_pos`, `ply_count`, `ply_size`, `cap_*`). ALSA-managed DMA buffers are allocated per PCM device, with larger minimum for multichannel. Register state is mostly hardware-owned, but selected FM801 registers are saved on suspend into `saved_regs[]` and replayed on resume. AC97 state is suspended/resumed through ALSA AC97 helpers unless the board is tuner-only. TEA575x frequency is restored on resume when enabled.

## Dependencies and Integration Points

The driver depends on ALSA core, PCM, AC97, TLV, MPU-401, OPL3, PCI resource management, DMA buffer helpers, low-level I/O ports, optional V4L2/TEA575x radio APIs, and Linux PM. It integrates channel maps via `snd_pcm_add_chmap_ctls()` for playback.

## Risks and Edge Cases

- Tuner-only detection changes the device into a radio-only card when AC97 reset fails.
- Secondary codec probing deliberately performs a recovery wait on codec 0 because probing absent codecs may cause timeout problems.
- The two-buffer IRQ model requires correct period-size programming and address wrap; off-by-one errors affect both pointer reporting and period callbacks.
- `FM801_IRQ_VOLUME` is acknowledged but has no implemented behavior.
- PM calls `snd_ac97_suspend/resume()` on `ac97_sec` even when it may be absent; this relies on AC97 helpers tolerating NULL or the path being avoided.
- Multichannel controls and channel constraints are only enabled for detected FM801-AU revisions.

## Test Signals

Useful tests include normal audio probe, tuner-only probe, AC97 reset and secondary codec detection, PCM playback/capture with multiple period sizes, pause/resume triggers, multichannel playback constraints and chmap creation, MPU and OPL3 creation, TEA575x GPIO autodetection, suspend/resume with register and radio frequency restoration, and IRQ handling under wraparound conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/fm801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/Makefile

## Purpose

This makefile defines ALSA object composition for the ICE1712 and ICE1724 PCI sound-card drivers. It builds common AK4xxx codec glue and aggregates many board-specific source files into the `snd-ice1712` and `snd-ice1724` modules.

## Important APIs, Types, and Functions

- `snd-ice17xx-ak4xxx-y := ak4xxx.o` builds the shared AK4xxx support object.
- `snd-ice1712-y` lists the Envy24 module core and supported ICE1712 board files.
- `snd-ice1724-y` lists the Envy24HT module core plus board files including `amp.o` and `aureon.o`.
- `obj-$(CONFIG_SND_ICE1712)` and `obj-$(CONFIG_SND_ICE1724)` include the appropriate module objects and shared AK4xxx object based on kernel config.

## Control Flow

There is no runtime control flow. Kbuild uses these variable assignments to decide which object files are linked into each ALSA module when the corresponding config symbol is enabled.

## State and Persistence Behavior

The file has no runtime state. Its persistent effect is build-time linkage: adding or removing board object names changes which card-info tables and initialization functions are available to the driver modules.

## Dependencies and Integration Points

It integrates with Linux Kbuild and the ALSA PCI driver tree. `amp.o` and `aureon.o` are part of `snd-ice1724`; `ak4xxx.o` is built for both ICE1712 and ICE1724 configurations.

## Risks and Edge Cases

Build regressions here usually appear as missing board descriptors, unresolved symbols, or accidentally omitted shared codec support. Because `snd-ice17xx-ak4xxx.o` is included for both config paths, changes must avoid duplicate or missing symbol expectations.

## Test Signals

Build both `CONFIG_SND_ICE1712` and `CONFIG_SND_ICE1724` configurations, verify module link succeeds, and verify board descriptor symbols from files such as `amp.o` and `aureon.o` are reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ak4xxx.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/ak4xxx.c

## Purpose

This file provides shared ALSA glue between ICE1712/ICE1724 cards and AK4xxx-family ADC/DAC codecs. It supplies GPIO bit-banged register writes, optional codec lock/unlock hooks that preserve ICE GPIO state, initialization of `snd_akm4xxx` descriptors from board templates, cleanup, control construction, and exported symbols for board drivers.

## Important APIs, Types, and Functions

- `snd_ice1712_akm4xxx_lock()` and `snd_ice1712_akm4xxx_unlock()` save and restore ICE GPIO status around codec access.
- `snd_ice1712_akm4xxx_write()` sends a 16-bit address/data command over GPIO using board-specific masks from `struct snd_ak4xxx_private`.
- `snd_ice1712_akm4xxx_init()` copies a codec template, attaches the ALSA card and ICE private data, optionally copies private GPIO metadata, supplies default ops, and calls `snd_akm4xxx_init()`.
- `snd_ice1712_akm4xxx_free()` releases per-codec private metadata and the codec array stored on `ice`.
- `snd_ice1712_akm4xxx_build_controls()` asks ALSA AKM helpers to create controls for each codec.

## Control Flow

Board code calls `snd_ice1712_akm4xxx_init()` with a template and GPIO private data. The helper copies inputs, installs default lock/unlock/write callbacks when the template did not supply them, then initializes the codec. Later, control construction iterates `ice->akm_codecs`. During register writes, the helper reads current GPIO state, applies add/mask flags, asserts chip select according to `cs_mask/cs_addr/cs_none` and `cif`, clocks out the codec address and data bits MSB-first through `data_mask` and `clk_mask`, then deasserts chip select.

## State and Persistence Behavior

The function stores a heap copy of `struct snd_ak4xxx_private` in `ak->private_value[0]` and stores the owning `struct snd_ice1712 *` in `ak->private_data[0]`. Hardware register state is managed by the ALSA AKM layer and board-specific initialization. GPIO status is preserved around operations to avoid corrupting unrelated board controls.

## Dependencies and Integration Points

The file depends on `ice1712.h` for `struct snd_ice1712` and GPIO helpers, ALSA AKM codec support, Linux delay and allocation APIs, and ALSA card/control layers. It exports three symbols consumed by ICE1712/ICE1724 board files.

## Risks and Edge Cases

- `snd_ice1712_akm4xxx_write()` only accepts codec indices 0 through 3 and returns on invalid indices.
- Board-specific GPIO masks must be correct; wrong `cs_mask`, `clk_mask`, or `data_mask` can disturb unrelated hardware.
- The code notes that one chip-select addressing case does not handle `cif=1` yet.
- Cleanup assumes `ice->akm` and `ice->akm_codecs` were initialized consistently.

## Test Signals

Build with both ICE1712 and ICE1724 modules, initialize a board using AK4xxx codecs, verify codec register writes on GPIO traces or by audible/mixer behavior, build ALSA codec controls, unload/reload to exercise cleanup, and test boards with multiple codec descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ak4xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.c

## Purpose

This file provides VT1724 board support for Advanced Micro Peripherals AUDIO2000 and Chaintech AV-710 class cards. It supplies card descriptors and minimal chip/control initialization for the shared Envy24HT driver, including optional WM8728 programming on AV-710.

## Important APIs, Types, and Functions

- `wm_put()` writes a WM8728 register over VT1724 I2C using `snd_vt1724_write_i2c()`.
- `snd_vt1724_amp_init()` sets total DAC/ADC counts for the board family and initializes AV-710's extra WM8728 codec when detected.
- `snd_vt1724_amp_add_controls()` adjusts a VT1616 AC97 register bit for output routing when AC97 exists.
- `snd_vt1724_amp_cards[]` exports two `struct snd_ice1712_card_info` descriptors: Chaintech AV-710 and AMP Ltd AUDIO2000.

## Control Flow

The main ICE1724 driver selects an entry from `snd_vt1724_amp_cards[]` by subvendor, then calls `chip_init` and `build_controls`. Initialization sets the board to six DACs and two ADCs, and for AV-710 writes the WM8728 attenuation and I2S format registers. Control-build adjustment clears bit `0x8000` in AC97 register `0x5a` via cached AC97 write.

## State and Persistence Behavior

The file does not allocate private state. It mutates `ice->num_total_dacs`, `ice->num_total_adcs`, external WM8728 register state on AV-710, and an AC97 cache register. The card descriptor table is static module state consumed by the parent driver.

## Dependencies and Integration Points

It depends on `ice1712.h`, `envy24ht.h`, `amp.h`, ALSA core, AC97 helpers via the parent headers, Linux delay/interrupt/init headers, and the VT1724 I2C helper.

## Risks and Edge Cases

- AV-710 and AUDIO2000 share the same real subdevice ID; the header uses a dummy ID for AUDIO2000 to distinguish descriptors.
- The comment states the AV-710 extra WM8728 mixer control is not supported.
- `snd_vt1724_amp_add_controls()` silently does nothing without AC97.

## Test Signals

Verify card descriptor matching, DAC/ADC counts, AV-710 WM8728 I2C writes, AC97 register `0x5a` cache update, playback over VT1616 packed mode, and absence of regressions on cards without the extra WM8728 path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.h

## Purpose

This header declares identifiers and register constants for the VT1724 AMP AUDIO2000 and Chaintech AV-710 board support implemented in `amp.c`.

## Important APIs, Types, and Functions

- `AMP_AUDIO2000_DEVICE_DESC` contributes textual device descriptors for the parent driver.
- `VT1724_SUBDEVICE_AUDIO2000` and `VT1724_SUBDEVICE_AV710` define subvendor IDs. AUDIO2000 is currently a dummy ID while AV-710 uses `0x12142417`.
- `WM_DEV`, `WM_ATTEN_L`, `WM_ATTEN_R`, `WM_DAC_CTRL`, and `WM_INT_CTRL` describe the AV-710 WM8728 I2C address and registers.
- `extern struct snd_ice1712_card_info snd_vt1724_amp_cards[]` exposes the board descriptor table.

## Control Flow

There is no runtime control flow. The header is included by `amp.c` and by parent discovery code that needs board descriptions and card-info table declarations.

## State and Persistence Behavior

The header has no state. Its constants drive matching and external codec programming in `amp.c`.

## Dependencies and Integration Points

It depends on `struct snd_ice1712_card_info` being declared by included parent headers in C files. It integrates with the Envy24HT board table and VT1724 model description strings.

## Risks and Edge Cases

The duplicate real subdevice ID for AV-710 and AUDIO2000 is explicitly handled by using a dummy AUDIO2000 ID. Any matching logic assuming one physical ID per board could misidentify these cards.

## Test Signals

Compile `amp.c` and the parent ICE1724 driver, verify descriptor strings include both boards, and confirm card-info symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.c

## Purpose

This file implements VT1724 Envy24HT board support for Terratec Aureon 5.1 Sky, Aureon 7.1 Space, Aureon 7.1 Universe, and Audiotrak Prodigy 7.1/LT/XT cards. It handles board-specific GPIO protocols, WM8770 codec setup and mixer controls, STAC9744 AC97 emulation/cache over a Xilinx GPIO bridge, CS8415A S/PDIF receiver controls, Aureon Universe PCA9554 input mux controls, headphone amplifier control, suspend/resume restoration, EEPROM override data, and card descriptor registration.

## Important APIs, Types, and Functions

- `struct aureon_spec` stores board-private state: cached STAC9744 AC97 registers, CS8415 mux selection, master and per-DAC WM volume/mute state, and PCA9554 output state.
- GPIO/I2C/SPI helpers include `aureon_pca9554_write()`, `aureon_ac97_write/read/init()`, `aureon_spi_write/read()`, `aureon_cs8415_get/read/put()`, `wm_get()`, `wm_put_nocache()`, and `wm_put()`.
- WM8770 mixer callbacks cover master/DAC volume and mute, PCM digital volume/mute, ADC gain/mute/source, deemphasis, oversampling, and AC97 monitor mute.
- AC97-style controls are implemented against the local STAC9744 cache using `aureon_ac97_vol_*`, `aureon_ac97_mute_*`, and `aureon_ac97_micboost_*`.
- CS8415 controls expose S/PDIF capture mute, source, Q-subcode, channel-status mask/default, and incoming rate.
- Board lifecycle functions are `aureon_add_controls()`, `aureon_reset()`, `aureon_resume()`, and `aureon_init()`.
- `snd_vt1724_aureon_cards[]` exports the parent driver card-info descriptors.

## Control Flow

The parent ICE1724 driver selects a card-info entry and calls `aureon_init()`. Initialization allocates `aureon_spec`, sets DAC/ADC counts according to board model, allocates one `snd_akm4xxx` record as a convenient WM8770 register-image cache, calls `aureon_reset()`, initializes all master and per-DAC volumes as muted, writes those mutes to hardware, and installs PM resume hooks when enabled.

`aureon_reset()` initializes the STAC9744 cache and GPIO AC97 bridge, configures GPIO direction/masks, toggles WM8770 reset, writes either Aureon or Prodigy WM8770 initialization tables, optionally initializes CS8415A and headphone amp for non-LT/XT boards, restores GPIO state, and initializes the PCA9554 direction/output for Universe-style mux support. `aureon_add_controls()` adds DAC controls, common WM controls, AC97 controls with Universe-specific label mapping when needed, skips AC97 and CS8415 paths for Prodigy LT/XT where appropriate, probes CS8415 ID `0x41`, and only registers S/PDIF receiver controls when present.

Mixer get paths generally read cached state under `ice->gpio_mutex` or through `wm_get()`. Put paths save GPIO state, compute masked register updates, write via GPIO/SPI bit-banged helpers, update caches, and restore GPIO state. Master and per-DAC volumes combine two levels of mute/attenuation in `wm_set_vol()` and use a two-write latch pattern for WM analog attenuation.

Resume calls `aureon_reset()` and then replays cached volume state to work around post-resume mixer pokes.

## State and Persistence Behavior

The file maintains explicit software caches for registers that are not normally readable through the GPIO bridge: `spec->stac9744`, `ice->akm[0].images` for WM8770, `spec->master`, `spec->vol`, `spec->cs8415_mux`, and `spec->pca9554_out`. EEPROM override arrays persist board configuration constants used by the parent driver. PM resume rebuilds hardware state from these caches and reset tables. GPIO state is protected by `snd_ice1712_save_gpio_status()`/`restore_gpio_status()` around bit-banged transactions.

## Dependencies and Integration Points

The file depends on ALSA control/TLV infrastructure, `ice1712.h` and `envy24ht.h` GPIO and parent-card APIs, `aureon.h` subvendor and GPIO bit definitions, AC97 register constants, Linux allocation/delay/mutex support, and the parent ICE1724 card-info discovery mechanism. It integrates with the parent PCM device when assigning IEC958 control device IDs.

## Risks and Edge Cases

- Many protocols are bit-banged over shared GPIO lines; failing to save/restore GPIO state can corrupt other board functions.
- The STAC9744 path is write-only from hardware's perspective, so software cache correctness is essential.
- Board variants use different GPIO pins for Prodigy LT/XT versus Aureon/Prodigy 7.1; wrong subvendor handling breaks SPI and headphone control.
- CS8415 controls are conditional on a runtime ID read and skipped when absent.
- `aureon_get_headphone_amp()` checks `AUREON_HP_SEL` even though LT/XT use `PRODIGY_HP_SEL`; current code also skips some non-LT/XT paths, but variant-specific control behavior should be checked carefully.
- `aureon_init()` leaks the allocated `spec` if later allocation of `ice->akm` fails unless the parent cleanup path handles it.
- `wm_mute_put()` writes `wm_set_vol(ice, ofs + i, ...)` while other volume paths write `WM_DAC_ATTEN + ofs + i`; this is equivalent only because `WM_DAC_ATTEN` is zero.

## Test Signals

Test each card descriptor path, especially Aureon 5.1 side-control omission, Universe AC97 label/PCA9554 mux behavior, Prodigy LT/XT GPIO pin paths, CS8415 detection and S/PDIF controls, WM8770 volume/mute/PCM/ADC/deemphasis/oversampling controls, headphone amplifier switching, AC97 cache-backed controls, suspend/resume register replay, and build/link integration with `snd-ice1724`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.h

## Purpose

This header declares device descriptor strings, VT1724 subdevice IDs, the Aureon/Prodigy card-info table, and board-specific GPIO bit assignments used by `aureon.c`.

## Important APIs, Types, and Functions

- `AUREON_DEVICE_DESC` lists Terratec Aureon and Audiotrak Prodigy model descriptors for the parent driver.
- `VT1724_SUBDEVICE_*` constants identify Aureon 5.1 Sky, Aureon 7.1 Space, Aureon 7.1 Universe, Prodigy 7.1, Prodigy 7.1 LT, and Prodigy 7.1 XT boards.
- `extern struct snd_ice1712_card_info snd_vt1724_aureon_cards[]` exposes the descriptor table implemented in `aureon.c`.
- `AUREON_*` GPIO masks define shared SPI, WM reset/chip-select, CS8415 chip-select, AC97 bridge, digital select, and headphone amplifier lines.
- `PRODIGY_*` GPIO masks define alternate WM SPI and headphone amplifier pins for Prodigy LT/XT variants.

## Control Flow

There is no runtime control flow in the header. Its constants drive board matching, GPIO direction/mask programming, SPI transactions, AC97 bridge writes, and control behavior in `aureon.c`.

## State and Persistence Behavior

The header has no state. Its bit masks and IDs are persistent compile-time contracts between the board file and the parent ICE1724 driver.

## Dependencies and Integration Points

The declaration assumes `struct snd_ice1712_card_info` is visible to C files including the header through parent driver headers. It integrates directly with the Envy24HT board table and GPIO helpers.

## Risks and Edge Cases

The GPIO bit layout differs between Aureon/Prodigy 7.1 and Prodigy LT/XT variants. Any new board ID or control path must use the correct mask family. Descriptor strings are concatenated macros, so syntax errors here can affect parent module device descriptions.

## Test Signals

Build the ICE1724 module, verify all descriptor strings and subdevice IDs are included, and exercise GPIO-dependent controls on both standard Aureon/Prodigy and LT/XT pin layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.h -->
