# Research: subset-b-006389

This grouped report covers ALSA PCI driver sources under `sources/distributed-fs/ceph-client/sound/pci`. Each file section is bounded by the required reconciliation markers and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.c -->
# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.c

## Purpose

`ca_midi.c` implements the raw MIDI UART glue used by the Creative CA0106 ALSA driver. It is not a standalone PCI driver; instead it exposes `ca_midi_init()` and a `struct snd_ca_midi` callback contract supplied by the CA0106 core. The file adapts hardware-specific read/write, interrupt-enable, interrupt-disable, and device-lookup callbacks into ALSA `snd_rawmidi` input/output substreams.

## Important APIs, Types, and Functions

- `ca_midi_init(void *dev_id, struct snd_ca_midi *midi, int device, char *name)` creates the ALSA rawmidi device, initializes locks, assigns rawmidi ops, and stores `midi->interrupt = ca_midi_interrupt`.
- `ca_midi_interrupt(struct snd_ca_midi *midi, unsigned int status)` is called by the parent CA0106 interrupt handler. It drains or receives input bytes and transmits pending output bytes when the relevant interrupt bits are set.
- `ca_midi_input_open()` / `ca_midi_output_open()` mark input or output mode, bind substreams, and issue reset plus UART-enter commands when the first side opens.
- `ca_midi_input_close()` / `ca_midi_output_close()` disable the relevant interrupt, clear mode/substream state, and reset the UART when the last side closes.
- `ca_midi_input_trigger()` and `ca_midi_output_trigger()` gate RX/TX interrupts. Output trigger also primes up to four bytes before enabling TX interrupts.
- `ca_midi_cmd()` writes an MPU-401-style command and optionally waits for an ACK byte.
- `ca_midi_clear_rx()` drains pending receive bytes with a bounded timeout.

The file relies on the data type declared in `ca_midi.h`: `struct snd_ca_midi`, which contains hardware callback pointers, interrupt masks, ACK/reset/enter-UART command bytes, lock fields, rawmidi pointers, and mode flags.

## Control Flow

Initialization starts in `ca_midi_init()`: the parent has already filled the hardware-specific callbacks and constants, then this function creates a duplex rawmidi instance with one input and one output stream. ALSA later calls the rawmidi open/close/trigger handlers. The first input or output open resets the UART and sends the enter-UART command. If the second half opens while the first is active, it only updates state and avoids resetting an already active MIDI session.

Runtime input flow is interrupt-driven. The parent interrupt handler passes hardware status into `ca_midi_interrupt()`. Under `input_lock`, the code checks the RX interrupt bit and hardware availability flag. If ALSA input mode is not enabled, it drains the hardware FIFO; otherwise it reads one byte and passes it to `snd_rawmidi_receive()` when an input substream exists.

Runtime output flow is also interrupt-driven. `ca_midi_output_trigger(..., up=1)` sends a small burst synchronously while the output register is ready, then enables TX interrupts. Later, `ca_midi_interrupt()` checks output readiness, pulls one byte from ALSA through `snd_rawmidi_transmit()`, writes it to hardware, or disables TX interrupts when no data remains.

## State and Persistence Behavior

The persistent state is in the caller-owned `struct snd_ca_midi`. Important fields include `midi_mode`, `substream_input`, `substream_output`, `rmidi`, callback pointers, `dev_id`, and lock instances. No state is written to disk. Hardware state is transient register state controlled through the callback methods. Cleanup via `ca_rmidi_free()` nulls callback pointers and rawmidi references so stale callbacks are less likely after device teardown.

Locking is split by purpose: `open_lock` protects open/close mode transitions, `input_lock` protects RX command/read paths, and `output_lock` protects TX paths. Command ACK polling uses `spinlock_irqsave` on `input_lock`, because command response bytes share the receive path.

## Dependencies and Integration Points

The file depends on Linux spinlock helpers, ALSA core/rawmidi, and the local `ca_midi.h` contract. It expects the CA0106 parent driver to provide `read`, `write`, `interrupt_enable`, `interrupt_disable`, `get_dev_id_card`, and `get_dev_id_port`, plus hardware bit definitions such as `ipr_rx`, `ipr_tx`, `input_avail`, and `output_ready`. ALSA integration is through `snd_rawmidi_new()`, `snd_rawmidi_set_ops()`, `snd_rawmidi_receive()`, and `snd_rawmidi_transmit()`.

## Risks and Edge Cases

- `ca_midi_cmd()` polls for ACK while reading from the MIDI receive path. Unexpected input data during command setup could be consumed as part of ACK handling.
- `ca_midi_interrupt()` reads at most one input byte per interrupt; correctness depends on the parent interrupt cadence or hardware reassertion.
- If `rmidi` is NULL in the interrupt path, both RX and TX interrupts are disabled, which is appropriate for teardown but could hide earlier initialization ordering mistakes.
- Open/close paths return early from inside guarded regions when the opposite direction is still open. This preserves the active UART but makes lock-scope clarity important.
- Debug-only timeout logging in `ca_midi_clear_rx()` helps detect a stuck input-ready status bit.

## Test Signals

Useful validation includes loading the CA0106 driver with MIDI hardware present, confirming a duplex rawmidi device is registered, opening input and output concurrently, sending and receiving MIDI bytes, and checking that TX interrupts stop when output buffers drain. Kernel logs should be checked for `ca_midi_cmd` ACK failures or clear-RX timeouts. Race-sensitive testing should exercise open/close while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.h -->
# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.h

## Purpose

`ca_midi.h` declares the CA0106 MIDI adapter contract used by `ca_midi.c` and the parent CA0106 hardware driver. It maps CA0106 MIDI mode constants to MPU-401 mode bits, defines the per-MIDI-port state structure, and exports `ca_midi_init()`.

## Important APIs, Types, and Fields

- `CA_MIDI_MODE_INPUT` and `CA_MIDI_MODE_OUTPUT` alias `MPU401_MODE_INPUT` and `MPU401_MODE_OUTPUT`, keeping raw MIDI mode semantics compatible with ALSA MPU-401 conventions.
- `struct snd_ca_midi` is the central integration type. It contains:
  - ALSA rawmidi objects: `rmidi`, `substream_input`, and `substream_output`.
  - Parent device identity: `void *dev_id`, `channel`, and `port`.
  - Synchronization: `input_lock`, `output_lock`, and `open_lock`.
  - Runtime mode: `midi_mode`.
  - Hardware constants: interrupt enable masks, interrupt pending bits, status masks, and MPU command bytes (`ack`, `reset`, `enter_uart`).
  - Callback hooks: parent interrupt callback, interrupt enable/disable functions, byte read/write functions, and helpers to derive `struct snd_card *` and port number from `dev_id`.
- `ca_midi_init(void *card, struct snd_ca_midi *midi, int device, char *name)` is the exported initializer implemented in `ca_midi.c`.

## Control Flow and Integration

The parent CA0106 driver allocates or embeds `struct snd_ca_midi`, fills the hardware-specific masks and callbacks, then calls `ca_midi_init()`. After initialization, ALSA owns rawmidi stream dispatch while the CA0106 parent owns PCI interrupt dispatch and calls `midi->interrupt()` with hardware interrupt status.

The read/write callbacks are indexed by `idx`: `0` for MIDI data and `1` for command/status in `ca_midi.c`'s macros. That index convention is an implicit API between this header's callback signatures and the implementation.

## State and Persistence Behavior

The structure is persistent for the lifetime of the sound card and is mutable at runtime. It stores substream pointers, mode flags, and function pointers. There is no disk persistence. Hardware state is represented by callback-accessed registers rather than cached directly, except for mode and substream state.

## Dependencies

The header includes Linux spinlocks, ALSA rawmidi, and ALSA MPU-401 definitions. It intentionally avoids including CA0106 core headers by using `void *dev_id` and callback accessors, keeping the MIDI helper generic across parent implementations that satisfy the same contract.

## Risks and Edge Cases

- The header does not validate callback initialization. `ca_midi_init()` assumes `get_dev_id_card()` is already valid before it assigns `midi->dev_id = dev_id`, so callers must initialize both `midi->dev_id` and callback pointers consistently before calling.
- Status-mask semantics are inverted by `ca_midi.c`: input/output availability macros test for cleared bits after applying `input_avail` or `output_ready`. Parent-provided masks must match that convention.
- The `char *name` parameter is mutable in the prototype even though the initializer only copies it; a `const char *` would describe usage more accurately but would change the exported signature.

## Test Signals

Compile coverage should verify all parent users populate the struct fields expected by `ca_midi.c`. Runtime validation comes from successful rawmidi registration, stable interrupt handling, and absence of NULL callback crashes when probing or removing CA0106 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cmipci.c -->
# sources/distributed-fs/ceph-client/sound/pci/cmipci.c

## Purpose

`cmipci.c` is the complete ALSA PCI driver for C-Media CMI8338/CMI8738-family sound cards, including later multichannel CMI8768/8769/8770-style variants. It handles PCI probe, register I/O, PCM playback/capture, second DAC/multichannel playback, IEC958/SPDIF playback and capture, AC3 mode handling, mixer controls, OPL3/FM, MPU-401 MIDI, optional gameport support, proc diagnostics, interrupt handling, and suspend/resume.

## Important APIs, Types, and Functions

- Module parameters: `index`, `id`, `enable`, `mpu_port`, `fm_port`, `soft_ac3`, and optional `joystick_port` configure card creation and legacy resources.
- `struct cmipci` is the device state: ALSA card/PCM/rawmidi pointers, PCI device, I/O base, IRQ, register shadow `ctrl`, chip capability flags, IEC958 status, open-mode tracking, mixer restore state, two DMA channel descriptors, gameport pointer, lock state, and suspend caches.
- `struct cmipci_pcm` stores one hardware channel's substream, running flag, format bits, DAC/capture role, DMA size, sample shift, channel index, and buffer address.
- `snd_cmipci_create()` performs PCI enablement, I/O region request, IRQ registration, chip detection, hardware reset, feature setup, FM/MIDI/gameport setup, PCM device creation, and mixer creation.
- `snd_cmipci_probe()` allocates the ALSA card and registers it with the PCI core through `module_pci_driver()`.
- PCM paths are implemented through `snd_cmipci_*_open()`, `snd_cmipci_pcm_prepare()`, `snd_cmipci_pcm_trigger()`, `snd_cmipci_pcm_pointer()`, and close/hw_free functions.
- SPDIF and AC3 handling is centered in `setup_spdif_playback()`, `setup_ac3()`, IEC958 control callbacks, and mixer auto-save/restore helpers.
- Mixer creation is handled by `snd_cmipci_mixer_new()` using SB-compatible register controls plus native CMI controls.
- Power management is implemented by `snd_cmipci_suspend()` and `snd_cmipci_resume()`.

## Control Flow

Probe begins in `snd_cmipci_probe()`, which selects a driver name based on PCI device ID and calls `snd_cmipci_create()`. Creation enables the PCI device, requests I/O regions, installs a shared IRQ handler, initializes locks and default channel state, queries chip capabilities, resets codec/channel registers, enables bus mastering, configures chip-specific quirks, sets card names, and then builds optional FM, proc, PCM, mixer, MIDI, and gameport interfaces.

PCM open uses `open_device_check()` to reserve channel A or B. Channel A is the primary DAC/playback path; channel B is capture or second DAC/multichannel playback depending on mode. Prepare computes sample format bits, frame-to-hardware shifts, DMA buffer and period counts, channel direction, rate selector fields, format register fields, and multichannel routing. Trigger starts, stops, pauses, or resumes by updating interrupt enable bits and `CM_REG_FUNCTRL0` channel enable/pause/reset bits. Pointer reads hardware remaining count and converts it back to ALSA frames.

IEC958 playback is enabled conditionally for normal playback when stream properties are compatible, and unconditionally for the dedicated SPDIF PCM. `setup_spdif_playback()` updates SPDIF routing bits, sample-rate bits, double-speed flags, and AC3 mode. During AC3 playback, `save_mixer_state()` disables or freezes selected mixer controls and `restore_mixer_state()` later restores them.

Interrupt handling first checks `CM_REG_INT_STATUS` for a real CMI interrupt. It acknowledges channel interrupts by toggling hold/clear bits, dispatches MPU-401 UART interrupts when present, and calls `snd_pcm_period_elapsed()` for running channel substreams. Mixer controls read and write either SB-compatible mixer ports or native CMI registers under `reg_lock`.

## State and Persistence Behavior

All runtime state is in memory and hardware registers. `cm->ctrl` shadows `CM_REG_FUNCTRL0` so channel enable, pause, and direction bits remain coherent across trigger operations. `opened[2]` serializes channel ownership and prevents incompatible playback/capture/multichannel combinations. `dig_status` and `dig_pcm_status` persist IEC958 default and stream status while the module is loaded. `mixer_res_status[]` stores mixer values temporarily while AC3 mode marks controls inactive.

Suspend saves selected dword registers and mixer registers into `saved_regs[]` and `saved_mixers[]`, disables interrupts, and resumes by resetting channels/mixer then restoring saved values. No persistent storage survives module unload or reboot.

## Dependencies and Integration Points

The driver integrates with ALSA core, control, PCM, rawmidi, MPU-401 UART, OPL3, SB mixer definitions, proc info, PCI, IRQ, gameport, and Linux module/PM infrastructure. Hardware access uses port I/O (`inb/outb/inw/outw/inl/outl`) rather than MMIO. The PCI ID table includes C-Media and ALi aliases for CM8338/CM8738 devices.

## Risks and Edge Cases

- Channel sharing is complex: channel B can be capture, second DAC, or multichannel output, so `opened[]` and `is_dac` transitions are critical.
- Multichannel setup only supports stereo 16-bit hardware format internally and rejects incompatible formats.
- SPDIF/AC3 mode changes temporarily alter mixer controls; failed allocation in `save_mixer_state()` can abort setup.
- Pointer reads retry only a few times before reporting `SNDRV_PCM_POS_XRUN` on invalid remaining counts.
- Several chip-version paths depend on undocumented or partly guessed register behavior, especially legacy AC3 and model detection.
- The silence hack writes zeros through an existing DMA buffer to avoid residual channel-A data contaminating rear DAC output.
- Optional legacy FM, MIDI, and joystick resources can fail independently; creation paths often disable the feature and continue.

## Test Signals

Validation should cover PCI probe and card registration across representative chip versions, duplex PCM playback/capture, second DAC and 4/6/8-channel modes, SPDIF PCM open/prepare/hw_free, AC3 non-audio stream handling, mixer control read/write and inactive behavior during AC3, MPU-401 interrupt traffic, optional FM/gameport registration, suspend/resume restoration, and shared IRQ behavior. Kernel logs for invalid PCM pointers, missing legacy ports, and chip-detection names are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cmipci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs4281.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs4281.c

## Purpose

`cs4281.c` is the complete ALSA PCI driver for Cirrus Logic CS4281 sound cards. It manages memory-mapped BA0/BA1 register regions, AC97 codec access, PCM playback/capture through CS4281 DMA/FIFO engines, integrated MIDI UART, OPL3 FM synthesis, gameport support, proc diagnostics, PCI probing, interrupt handling, and suspend/resume.

## Important APIs, Types, and Functions

- Module parameters `index`, `id`, `enable`, and `dual_codec` configure ALSA card slots and optional secondary AC97 codec access.
- `struct cs4281` stores IRQ, BA0/BA1 mappings and physical addresses, AC97 bus/codecs, ALSA card/PCM/rawmidi pointers, four DMA descriptors, slot routing, spurious IRQ counters, locks, MIDI control shadows, gameport pointer, and suspend register cache.
- `struct cs4281_dma` describes each DMA/FIFO engine: register offsets, mode/control/FIFO values, FIFO offset, AC97 slot mapping, substream, and period-fragment workaround state.
- `snd_cs4281_create()` enables PCI, maps BARs, requests IRQ, calls `snd_cs4281_chip_init()`, and registers proc entries.
- `snd_cs4281_chip_init()` is the hardware bring-up sequence for clocking, serial AC97 link setup, codec readiness, slot validity, DMA/FIFO initialization, volume defaults, and IRQ unmasking.
- `snd_cs4281_ac97_write()` and `snd_cs4281_ac97_read()` implement ALSA AC97 bus operations through BA0 command/status registers.
- PCM paths use `snd_cs4281_mode()`, prepare/trigger/pointer callbacks, and one playback plus one capture ALSA PCM.
- MIDI paths use rawmidi ops around BA0 MIDI control/status/data registers.
- `snd_cs4281_interrupt()` handles DMA and MIDI interrupts.
- `cs4281_suspend()` and `cs4281_resume()` implement device PM.

## Control Flow

Probe enters `snd_cs4281_probe()`, which wraps `__snd_cs4281_probe()` in `snd_card_free_on_error()`. The inner probe allocates the ALSA card, creates and initializes the chip, builds the AC97 mixer, PCM, rawmidi, OPL3 hwdep, optional gameport, sets card identity strings, registers the card, and stores PCI driver data.

Chip initialization is a staged hardware state machine. It clears full-power-down, validates or writes configuration-load state, unlocks vendor configuration writes, verifies AC97 serial port format, enables sound-system power blocks, resets clocks and serial ports, toggles AC97 reset, optionally enables the secondary input, configures serial timing, starts the DLL clock, waits for DLL-ready and codec-ready bits, enables valid AC97 frames, waits for input slots 3/4, initializes four DMA/FIFO descriptor structures, assigns playback/capture slots, enables the wave FIFO for FM playback, initializes digital volumes, and unmasks MIDI/DMA interrupts.

PCM open binds playback to DMA engine 0 and capture to DMA engine 1, sets slot numbers, stores the descriptor in `runtime->private_data`, applies hardware format constraints, and exposes continuous rates. Prepare builds DMA mode bits from ALSA format, writes DMA base/count, updates source slot assignments, writes DAC/ADC sample-rate converter values, and programs FIFO slot/size/offset. Trigger masks/unmasks DMA and FIFO enable bits for start, stop, suspend, resume, and pause. Pointer computes position from the current DMA count register.

Interrupt handling reads `BA0_HISR`, ignores empty shared IRQs after EOI, processes DMA bits for up to four engines, filters duplicate half/end interrupts using `frag` parity and spurious counters, calls `snd_pcm_period_elapsed()`, then handles MIDI RX/TX FIFO movement under the register lock and sends an EOI.

## State and Persistence Behavior

The driver persists runtime state in `struct cs4281` for the module/card lifetime. DMA descriptor values mirror programmed hardware state and are reused by trigger paths. `midcr` and `uartm` shadow MIDI control and open-mode state. `src_*_slot` fields define AC97 slot routing. `spurious_dhtc_irq` and `spurious_dtc_irq` are counters exposed through proc.

Suspend saves selected BA0 registers, suspends AC97 codecs, disables interrupts, powers down serial ports, sound-system blocks, DLL, and AC link. Resume reruns chip initialization, restores saved registers, resumes AC97 codecs, and returns the ALSA power state to D0. State does not persist beyond driver unload.

## Dependencies and Integration Points

The file integrates with ALSA core, PCM, control, AC97 codec bus, rawmidi, TLV controls, OPL3, proc info, PCI, MMIO helpers, IRQ handling, gameport, and Linux PM/module infrastructure. Hardware register access is through `readl()`/`writel()` to BA0/BA1 regions mapped with `pcim_iomap_region()`.

## Risks and Edge Cases

- Hardware initialization relies on multiple timed waits; failures return `-EIO` after logging which readiness bit failed.
- AC97 read/write operations poll command-valid and status-valid bits; timeouts return `0xffff` for reads.
- DMA interrupt handling intentionally suppresses duplicate half/end interrupts; bugs in the parity workaround could drop real period notifications.
- MIDI interrupt receive path assumes `midi_input` is valid when RIE is set, and output assumes `midi_output` is valid when TIE is set.
- `dual_codec` is sanitized to 0..3, and the secondary codec is disabled if it fails readiness during init.
- Proc BA0/BA1 binary reads expose raw device memory to ALSA proc readers, useful for diagnostics but sensitive to correct size handling.

## Test Signals

Useful signals include successful PCI probe with BA0/BA1 mapped, AC97 mixer creation, playback/capture at several formats and continuous rates, correct period notifications without spurious counter growth, MIDI duplex traffic, OPL3 hwdep creation and command writes, gameport registration when configured, proc output readability, dual-codec fallback, and suspend/resume with restored mixer/PCM/MIDI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs4281.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/Makefile

## Purpose

This Makefile defines how the ALSA CS46xx PCI driver module is built. It composes the `snd-cs46xx` object from the core wrapper and implementation library, and conditionally includes new-DSP support objects when `CONFIG_SND_CS46XX_NEW_DSP` is enabled.

## Important Build Rules

- `snd-cs46xx-y := cs46xx.o cs46xx_lib.o` always includes the PCI module entry/probe wrapper and the core implementation library.
- `snd-cs46xx-$(CONFIG_SND_CS46XX_NEW_DSP) += dsp_spos.o dsp_spos_scb_lib.o` adds DSP SPOS support when the Kconfig option is enabled.
- `obj-$(CONFIG_SND_CS46XX) += snd-cs46xx.o` connects the composite object to the kernel build when the CS46xx driver is selected.

## Control Flow and Integration

There is no runtime control flow in this file. Build-time control flow is driven by Kbuild variable expansion. When `CONFIG_SND_CS46XX=m`, the composite object becomes a module; when built in, it becomes part of the kernel image. The optional DSP files affect which functions and structure fields in `cs46xx.h` are active.

## State and Persistence Behavior

The file has no runtime state. Its build decisions persist only in generated build artifacts and are controlled by kernel configuration.

## Dependencies and Integration Points

The rule depends on Kbuild conventions and on adjacent sources: `cs46xx.c`, `cs46xx_lib.c`, and optional `dsp_spos.c` and `dsp_spos_scb_lib.c`. It integrates with the top-level ALSA PCI sound Kconfig through `CONFIG_SND_CS46XX` and `CONFIG_SND_CS46XX_NEW_DSP`.

## Risks and Edge Cases

- If `CONFIG_SND_CS46XX_NEW_DSP` is enabled without the DSP source files present or compiling, the whole module build fails.
- The Makefile does not list headers directly; dependency discovery relies on Kbuild's compiler-generated dependency tracking.
- Runtime feature availability changes substantially with `CONFIG_SND_CS46XX_NEW_DSP`, so tests must cover both build variants where supported.

## Test Signals

Build validation should compile `CONFIG_SND_CS46XX` both with and without `CONFIG_SND_CS46XX_NEW_DSP`. The resulting module should contain `cs46xx.o` and `cs46xx_lib.o` always, and DSP symbols only in the new-DSP configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.c

## Purpose

`cs46xx.c` is the top-level PCI module wrapper for Cirrus Logic Sound Fusion CS46xx-based sound cards. It provides module parameters, PCI device matching, ALSA card allocation, high-level device construction order, optional new-DSP PCM devices, MIDI/gameport startup, card naming, registration, and PCI driver binding. Most hardware logic is delegated to functions declared in `cs46xx.h` and implemented in the companion library/DSP files.

## Important APIs, Types, and Functions

- Module parameters: `index`, `id`, `enable`, `external_amp`, `thinkpad`, and `mmap_valid` configure each ALSA card slot.
- `snd_cs46xx_ids[]` matches Cirrus PCI device IDs 0x6001, 0x6003, and 0x6004, corresponding to CS4280, CS4612, and CS4615 families.
- `snd_card_cs46xx_probe()` is the PCI probe function. It allocates an ALSA card with embedded `struct snd_cs46xx`, calls the lower-level create/mixer/PCM/MIDI/DSP functions, and registers the card.
- `cs46xx_driver` wires the probe, ID table, and optional `snd_cs46xx_pm` power-management operations into the PCI core.
- `module_pci_driver(cs46xx_driver)` supplies module init/exit boilerplate.

## Control Flow

On PCI probe, the static `dev` index selects the current module-parameter slot. Disabled slots are skipped with `-ENOENT`; too many devices return `-ENODEV`. The function allocates a managed ALSA card, obtains the embedded `struct snd_cs46xx`, and calls `snd_cs46xx_create(card, pci, external_amp[dev], thinkpad[dev])` for low-level PCI/hardware initialization.

After hardware creation, probe sets `chip->accept_valid` from `mmap_valid[dev]`, creates the primary PCM device, conditionally creates rear and IEC958 PCM devices when `CONFIG_SND_CS46XX_NEW_DSP` is enabled, builds mixer controls, optionally creates center/LFE PCM when two AC97 codecs are present, creates MIDI, starts the DSP, starts gameport support, sets user-visible card strings, registers the ALSA card, stores PCI driver data, and advances `dev`.

Error handling uses a common `error:` label to free the ALSA card. Because card allocation is devres-managed through `snd_devm_card_new()`, teardown integrates with device lifecycle, but explicit `snd_card_free(card)` is still used on probe failure before registration.

## State and Persistence Behavior

This file maintains only the static `dev` probe index and module-parameter arrays. The meaningful runtime state is stored in `struct snd_cs46xx` allocated as card private data and initialized by lower-level functions. `mmap_valid` is copied into `chip->accept_valid` and affects OSS mmap-valid reporting. No persistent storage is used.

## Dependencies and Integration Points

The wrapper depends on Linux PCI/module/init headers, ALSA core/initval, and the local `cs46xx.h` declarations. It is tightly coupled to `cs46xx_lib.c` for `snd_cs46xx_create()`, PCM, mixer, MIDI, DSP start, and gameport implementations, and to optional DSP objects under `CONFIG_SND_CS46XX_NEW_DSP`. Power management is provided externally through `snd_cs46xx_pm`.

## Risks and Edge Cases

- The static `dev` counter is incremented only on disabled slots and successful registration; repeated probe failures before increment can reuse the same module-parameter slot.
- Optional new-DSP paths add several device creation steps and a dependency on `chip->nr_ac97_codecs` for center/LFE PCM creation.
- `card->private_data` is assigned to `chip` after `snd_cs46xx_create()`, although it already came from card private storage; this is redundant but harmless if lower-level code does not replace private data.
- DSP startup occurs after MIDI creation and mixer/PCM creation; failures late in probe tear down the whole card.

## Test Signals

Validation should include probe and removal for supported PCI IDs, module-parameter slot behavior with multiple cards, `enable=false` handling, primary PCM creation, new-DSP build behavior with rear/IEC958/center-LFE devices, MIDI creation, DSP start failure unwinding, gameport setup, card longname formatting, and suspend/resume callback registration when PM sleep is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.h -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.h

## Purpose

`cs46xx.h` is the main private hardware contract for the ALSA CS46xx driver. It declares register offsets, bit definitions, DMA descriptor fields, MIDI/gameport/AC97/DSP constants, core runtime structures, and function prototypes shared by `cs46xx.c`, `cs46xx_lib.c`, and optional DSP SPOS sources.

## Important APIs, Types, and Definitions

The header is dominated by hardware definitions:

- BA0 direct register offsets cover host interrupt/status/control, host DMA, PCI config mirrors, clocks/PLL, serial ports, AC97 command/status, joystick, MIDI, GPIO, extended GPIO, I/O trap, PC/PCI, and power-management registers.
- BA1 offsets cover DSP memories (`SP_DMEM0`, `SP_DMEM1`, `SP_PMEM`, `SP_REG`), DSP control/debug registers, Omni memory, and legacy playback/capture parameter areas.
- Bit masks define host interrupt bits (`HISR_*`), host signal bits, DMA status/control bits, clock/PLL fields, feature reporting, serial/AC97 slots, joystick bits, MIDI bits, DSP control/debug state, scatter/gather descriptor fields, and generic DMA requestor fields.
- MIDI mode constants `CS46XX_MODE_OUTPUT` and `CS46XX_MODE_INPUT` track UART open state.
- AC97 limits and indices define up to four codecs, primary/secondary slots, and secondary offset.
- Mixer constants identify SPDIF input/output element indices.

Core structures:

- `struct snd_cs46xx_pcm` stores DMA buffer metadata, control value, frame/byte shift, ALSA indirect PCM state, substream pointer, optional DSP channel descriptor, and PCM channel ID.
- `struct snd_cs46xx_region` describes one mapped hardware region with name, physical base, remapped address, and size.
- `struct snd_cs46xx` is the central device state. It stores IRQ, BA0/BA1 physical addresses, named/array region mappings, mode, capture state, AC97 bus/codecs, PCI/card/PCM/rawmidi pointers, MIDI substreams, locks, MIDI control shadows, amplifier/active/mixer callbacks, ACPI port, EAPD control, mmap-valid flag, suspend flag, optional gameport, optional new-DSP SPOS state/modules, fallback old-DSP playback state, and PM saved registers.

Exported prototypes include creation, PM ops, primary/rear/IEC958/center-LFE PCM creation, mixer creation, MIDI creation, DSP startup, and gameport setup.

## Control Flow and Integration

The header itself has no executable control flow, but it defines the register and structure vocabulary used by the implementation. `cs46xx.c` includes this header and calls the declared construction functions in probe order. The implementation library uses the BA0/BA1 constants to initialize hardware, service interrupts, program AC97/MIDI/DSP state, and build ALSA devices.

Conditional compilation around `CONFIG_SND_CS46XX_NEW_DSP` changes the shape of `struct snd_cs46xx`: new-DSP builds include an SPOS mutex, DSP SPOS instance, rear/center-LFE/IEC958 PCM devices, and module descriptors; compatibility builds include older playback PCM and BA1 state. The Makefile mirrors this by adding DSP source objects only for new-DSP builds.

## State and Persistence Behavior

`struct snd_cs46xx` holds all per-card runtime state for the driver lifetime. It includes both software state (substream pointers, codec pointers, flags, callback hooks) and hardware shadows (MIDI control, mode, saved PM registers). The header defines `SAVE_REG_MAX` and `POWER_DOWN_ALL` for suspend/power handling. No on-disk persistence is represented.

## Dependencies and Integration Points

The header depends on ALSA PCM, PCM indirect helpers, rawmidi, AC97 codec support, and local DSP SPOS declarations from `cs46xx_dsp_spos.h`. It is a private driver header, not a stable userspace ABI. It integrates CS46xx hardware logic with ALSA subsystems for PCM, mixer/AC97, rawmidi, gameport, and optional DSP routing.

## Risks and Edge Cases

- Because the header encodes large numbers of hardware bitfields, incorrect masks or shifts can cause silent hardware misprogramming.
- Several definitions are conditional on `NO_CS4612`, `NO_CS4610`, or `NO_CS4615`; build configurations must keep implementation assumptions aligned with those conditionals.
- `CS46XX_DSP_CAPTURE_CHANNEL` is defined twice with the same value, which is harmless but signals historical duplication.
- `struct snd_cs46xx` layout changes with `CONFIG_SND_CS46XX_NEW_DSP`, so implementation files must guard field access consistently.
- The function prototypes expose a broad internal API; mismatches between `cs46xx.c`, `cs46xx_lib.c`, and DSP objects are compile-time failures.

## Test Signals

Build tests should cover configurations with and without `CONFIG_SND_CS46XX_NEW_DSP` and any supported CS461x feature macros. Runtime tests should validate that register definitions support successful hardware init, PCM routing, AC97 codec enumeration, MIDI traffic, DSP startup, gameport behavior, suspend/resume saved-register restoration, and mixer/SPDIF controls. Static analysis should watch for conditional field access and duplicated or inconsistent masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.h -->
