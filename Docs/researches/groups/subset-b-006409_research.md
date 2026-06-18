# subset-b-006409 RME9652 Driver Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme9652/hdspm.c -->
# sources/distributed-fs/ceph-client/sound/pci/rme9652/hdspm.c

## Purpose

`hdspm.c` is the ALSA PCI driver for RME Hammerfall DSP/HDSPe-class MADI-family cards in this source tree. It supports multiple hardware personalities behind the Xilinx Hammerfall DSP MADI PCI ID: MADI, MADIface, AES32, RayDAT, and AIO. The driver owns PCI probe, MMIO register access, ALSA card/PCM/rawmidi/control/hwdep/proc registration, audio DMA setup, interrupt handling, MIDI FIFO servicing, clock and sync controls, TCO timecode option controls, and the hardware matrix mixer cache.

This file is not related to Ceph logic despite living under the distributed-fs source snapshot. It is a low-level sound driver whose main contracts are ALSA kernel APIs and the userspace ABI from `include/uapi/sound/hdspm.h`.

## Important APIs, Types, and Functions

Core state and hardware description:

- Module parameters `index[]`, `id[]`, and `enable[]` control ALSA card numbering and per-card enablement.
- Register macros define MMIO offsets for control, status, MIDI FIFOs, TCO, page-address tables, channel DMA enables, meters, and the MADI mixer memory window.
- `struct hdspm` is the central per-card object stored in `snd_card->private_data`. It caches `control_register`, `control2_register`, and `settings_register`, tracks stream substreams/PIDs/running bits, channel maps, port names, sample rates, MMIO base, IRQ, MIDI ports, mixer cache, optional `struct hdspm_tco`, and ALSA device pointers.
- `struct hdspm_midi` tracks each rawmidi port, FIFO register offsets, interrupt enable/pending bits, timer state, and input/output substreams.
- `struct hdspm_tco` stores software state for optional Time Code Option settings such as input, frame rate, wordclock conversion, sample rate, pull, and termination.
- Channel maps and port-name tables translate logical ALSA channel numbers into hardware DMA channel slots for MADI/AES32/RayDAT/AIO and for single, double, and quad speed modes.

PCI and ALSA setup:

- `snd_hdspm_probe()` allocates an ALSA card with `snd_devm_card_new()`, calls `snd_hdspm_create()`, fills short/long names, registers the card, and stores drvdata.
- `snd_hdspm_create()` identifies the card by PCI revision/firmware, enables the PCI device, maps BAR0 via `pcim_iomap_region()`, requests a shared IRQ, allocates the mixer cache, detects AEB/TCO add-ons, configures channel maps/text tables, derives serial-based card IDs, and calls `snd_hdspm_create_alsa_devices()`.
- `snd_hdspm_create_alsa_devices()` creates PCM, rawmidi ports, mixer controls, hwdep device, proc entries, initializes default runtime state, applies defaults, updates mixer control visibility, and registers the ALSA card.
- `snd_hdspm_card_free()` cancels MIDI work and clears audio/MIDI interrupt enable bits during card teardown.

PCM and DMA:

- `snd_hdspm_ops` provides `.open`, `.close`, `.ioctl`, `.hw_params`, `.hw_free`, `.prepare`, `.trigger`, and `.pointer`.
- `snd_hdspm_open()` installs PCM hardware capabilities, marks playback/capture substreams, applies channel/rate/period constraints, and accounts for RayDAT/AIO fixed 16384-sample channel buffers.
- `snd_hdspm_hw_params()` validates duplex compatibility, sets the hardware sample rate and period size, allocates SG DMA pages, writes per-channel page addresses with `hdspm_set_channel_dma_addr()`, enables selected input/output channel DMA, caches `playback_buffer` or `capture_buffer`, and toggles native float format for non-AES32 cards.
- `snd_hdspm_hw_free()` disables all channel DMA for the stream direction, clears cached stream buffer pointers, and frees PCM pages.
- `snd_hdspm_trigger()` maintains the combined playback/capture `running` bitmask, honors ALSA sync-start groups, silences playback when capture starts without active playback, and starts/stops the hardware engine only on aggregate transitions.
- `hdspm_hw_pointer()` reads hardware position. RayDAT/AIO use the precise buffer-position bits; other types mostly expose period boundary 0/period based on `HDSPM_BufferID`.
- `snd_hdspm_channel_info()` reports noninterleaved mmap channel offsets after validating logical channels through current speed-dependent channel maps.

Clock, sync, and mixer controls:

- `hdspm_set_rate()` maps requested rates from 32 kHz to 192 kHz onto control bits, validates AutoSync when not master, prevents speed-mode changes while either stream is open, writes DDS frequency values, updates AES32 EEPROM trigger, and swaps channel maps/port names/max channel counts for the target speed range.
- `hdspm_external_sample_rate()`, `hdspm_get_system_sample_rate()`, `hdspm_get_wc_sample_rate()`, `hdspm_get_tco_sample_rate()`, `hdspm_get_sync_in_sample_rate()`, `hdspm_get_aes_sample_rate()`, and `hdspm_get_s1_sample_rate()` decode clock-source status registers.
- `hdspm_system_clock_mode()`, `hdspm_set_system_clock_mode()`, `hdspm_clock_source()`, `hdspm_set_clock_source()`, `hdspm_pref_sync_ref()`, `hdspm_set_pref_sync_ref()`, and `hdspm_autosync_ref()` back the ALSA clock and sync controls.
- `hdspm_wc_sync_check()`, `hdspm_madi_sync_check()`, `hdspm_s1_sync_check()`, `hdspm_sync_in_sync_check()`, `hdspm_aes_sync_check()`, and `hdspm_tco_sync_check()` normalize card-specific status bits into No Lock/Lock/Sync/N-A values.
- `hdspm_write_in_gain()` and `hdspm_write_pb_gain()` write the hardware matrix mixer and update `hdspm->mixer`, which is required because the hardware mixer is write-only.
- `snd_hdspm_get_mixer()`, `snd_hdspm_put_mixer()`, and the simple per-channel playback mixer controls expose full matrix and 1:1 playback-to-output gain paths.
- Control arrays `snd_hdspm_controls_madi`, `snd_hdspm_controls_madiface`, `snd_hdspm_controls_aio`, `snd_hdspm_controls_raydat`, `snd_hdspm_controls_aes32`, and `snd_hdspm_controls_tco` define the card-specific ALSA control surface.

MIDI, TCO, hwdep, and proc:

- `snd_hdspm_create_midi()` creates duplex or input-only rawmidi devices for physical MIDI, MIDI-over-MADI, and optional TCO MTC ports.
- MIDI receive is interrupt initiated: `snd_hdspm_interrupt()` disables the relevant MIDI IRQ, marks the port pending, and queues `hdspm_midi_work()` on `system_highpri_wq`; `snd_hdspm_midi_input_read()` drains/forwards bytes and reenables the port IRQ.
- MIDI transmit is timer driven through `snd_hdspm_midi_output_timer()` because output is not interrupt driven.
- `hdspm_tco_write()` encodes software TCO settings to the four TCO write registers. TCO controls expose sample rate, pull, WCK conversion, frame rate, sync source, word termination, LTC validity/frame rate, and video input format.
- `snd_hdspm_hwdep_ioctl()` implements the HDSPM UAPI ioctls: peak/RMS meter reads, LTC status, config snapshot, status snapshot, version/add-on data, and mixer-copy-out through an indirect userspace pointer.
- Proc readers report card-specific debug/status pages and generated `ports.in`/`ports.out` maps.

## Control Flow

Probe starts in `snd_hdspm_probe()`. After module-card slot checks, the driver allocates `struct snd_card` plus embedded `struct hdspm`, sets `private_free`, and enters `snd_hdspm_create()`. Creation classifies firmware revision into an `io_type`, enables PCI, maps BAR0, requests IRQ, allocates mixer storage, configures channel topology for the selected card and add-ons, detects optional TCO, sets control text tables, reads serial information, creates ALSA-facing devices, flushes MIDI input FIFOs, and registers the card.

Default setup flows through `snd_hdspm_set_defaults()`: it seeds control/settings registers by card type, writes control/control2/settings registers, computes period size, zeros the entire matrix mixer by writing all input/playback faders, and calls `hdspm_set_rate(..., 48000, 1)` so speed-dependent maps and channel counts are initialized.

PCM open records the active PID/substream and installs constraints. Hardware-params then serializes against existing duplex users, applies sample rate and period settings, allocates the full channel DMA area, programs 16 page-table entries per enabled logical channel, enables per-channel DMA, and records runtime DMA memory. Trigger start/stop updates aggregate running state; the hardware engine is only started when the first stream starts and stopped when the last stream stops. IRQs acknowledge the device, call `snd_pcm_period_elapsed()` for active audio streams, and schedule MIDI work if any MIDI FIFO interrupt is pending.

Clock control flows differ by master/slave state. In master mode, requested rates directly update control bits and DDS registers. In AutoSync mode, user-facing clock changes can be remembered internally, but PCM `hw_params` verifies that the requested rate matches the detected external source. Speed-mode transitions update logical channel maps and are refused while playback or capture is open.

Mixer writes flow through cached software state. Full matrix controls take source/destination/gain triples, validate bounds, compare against `hdspm->mixer`, then write the matching mixer register. Simple playback controls target the 1:1 playback-to-output fader and are made inactive when the current speed makes those output channels unavailable.

## State and Persistence Behavior

Hardware register state is cached in `control_register`, `control2_register`, and `settings_register`, then pushed to MMIO. These caches are the authoritative software view for many controls, so stale updates or missing locking can overwrite unrelated bits.

The current sample rate persists in `system_sample_rate`; current channel maps, port-name arrays, and max channel counts are derived from it. `last_external_sample_rate` and `last_internal_sample_rate` are initialized but are not central in the shown data path. Stream ownership persists through `playback_pid`, `capture_pid`, `playback_substream`, `capture_substream`, and `running`.

DMA memory is per-PCM-runtime SG memory allocated in `snd_hdspm_hw_params()` and released in `snd_hdspm_hw_free()`. The driver programs hardware page tables for 64 possible channels, with each channel represented by 16 4 KiB pages. Playback/capture buffer pointers are cached for silence paths and cleared on free.

The matrix mixer cache persists for the card lifetime in devm-allocated `hdspm->mixer`. Hardware faders are write-only, so readback uses only this cache. Peak/RMS data is read live from meter registers into `hdspm->peak_rms` before copying to userspace.

MIDI input state uses `pending` flags plus workqueue rescheduling. Output timer state persists in `hmidi->istimer` and each port's `timer_list`. TCO settings persist in the heap-allocated `hdspm->tco` object for detected modules and are rewritten to hardware on control changes.

Most core state is protected with `hdspm->lock` or per-MIDI-port locks, but the hwdep read paths often take snapshots without full serialization because they report status/debug information.

## Dependencies and Integration Points

Kernel and ALSA dependencies include PCI managed resources, MMIO helpers, IRQ handling, workqueues, timers, spinlocks, SG DMA PCM helpers, rawmidi, hwdep, controls, proc info, and `copy_to_user()`/`copy_from_user()`.

Primary integration points:

- PCI binding uses the Xilinx Hammerfall DSP MADI device ID and firmware revision to distinguish supported RME cards.
- ALSA PCM integration exposes one playback and one capture device with noninterleaved mmap-capable channels and joint duplex behavior.
- ALSA rawmidi integration exposes physical MIDI, MIDI-over-MADI, and TCO MTC ports depending on card/add-on detection.
- ALSA control integration exposes card-specific clock, sync, format, level, TCO, and mixer controls.
- ALSA hwdep integration exposes the stable userspace structs and ioctls from `include/uapi/sound/hdspm.h`.
- Proc integration publishes `hdspm`, `ports.in`, `ports.out`, and optional debug register dumps.

## Risks and Edge Cases

- Register bit reuse across card families is dense. AES32, MADI, RayDAT, and AIO interpret some bit positions differently; changing shared helpers can silently corrupt unrelated controls.
- Speed changes are high risk because channel maps, channel counts, period constraints, DMA page tables, and mixer control visibility all depend on single/double/quad speed. The driver correctly rejects speed-mode changes while streams are open, but externally driven rate changes remain inherently hard to reconcile.
- The hardware mixer is write-only. Any path that writes mixer registers without updating `hdspm->mixer`, or any missed initialization, makes user-visible mixer reads incorrect.
- `snd_hdspm_hwdep_ioctl(SNDRV_HDSPM_IOCTL_GET_MIXER)` copies a userspace-provided nested pointer destination from `struct hdspm_mixer_ioctl`. This is the intended historical ABI but is sensitive to compat, pointer validation, and very large copy size.
- TCO objects are allocated with plain `kzalloc_obj()` while much of the rest of the driver uses devm-managed resources. Teardown relies on card/device lifetime cleanup patterns and should be checked when touching TCO allocation.
- MIDI IRQ handling disables per-port interrupts until workqueue processing reenables them. Races between trigger close, pending work, and card teardown are mitigated by locks and `cancel_work_sync()`, but changes around those paths can lose MIDI bytes or leave interrupts disabled.
- `snd_hdspm_proc_init()` can call `snd_card_ro_proc_new()` with a NULL read callback for MADIface/AIO, depending on ALSA helper tolerance. This is an existing behavior worth preserving or explicitly fixing with targeted testing.
- Peak registers are reset-on-read per comments; monitoring tools and tests should expect reads to have side effects.
- Several legacy comments note uncertain hardware documentation. Register offsets and magic defaults should be treated as hardware contracts even if they look arbitrary.

## Test Signals

Useful validation signals include:

- Build coverage for `CONFIG_SND_HDSPM`, `CONFIG_SND_DEBUG`, big-endian variants, and 32-bit compat ioctl paths.
- PCI probe smoke on each firmware-revision class: MADI, MADIface, AES32, RayDAT, and AIO, including serial-based card ID generation.
- ALSA PCM open/hw_params/trigger tests across 32/44.1/48/64/88.2/96/128/176.4/192 kHz, verifying channel constraints and current port names for SS/DS/QS.
- Duplex tests where playback and capture are opened by same and different PIDs, ensuring shared rate/period enforcement and sync-start behavior.
- Runtime checks of `/proc/asound/card*/hdspm`, `ports.in`, and `ports.out` for card-specific status and channel maps.
- `amixer`/control tests for clock source, preferred sync, sync checks, input/source controls, level controls, and mixer read/write coherency.
- RawMIDI loop or FIFO tests for physical MIDI, MIDI-over-MADI, and TCO MTC ports, including open/close while interrupts are pending.
- hwdep userspace tests for `GET_PEAK_RMS`, `GET_LTC`, `GET_CONFIG`, `GET_STATUS`, `GET_VERSION`, and `GET_MIXER`, with invalid userspace pointers to confirm `-EFAULT`.
- Hardware meter and TCO tests that account for reset-on-read peak registers and optional add-on detection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme9652/hdspm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme9652/rme9652.c -->
# sources/distributed-fs/ceph-client/sound/pci/rme9652/rme9652.c

## Purpose

`rme9652.c` is the ALSA PCI driver for the older RME Digi9652/Digi9636 Hammerfall audio interfaces. It supports the full Hammerfall with 24 ADAT plus 2 S/PDIF channels and the Hammerfall Light with 16 ADAT plus 2 S/PDIF channels. The file handles PCI setup, MMIO register access, aligned DMA buffer allocation, ALSA PCM/control/proc registration, clock and S/PDIF controls, ADAT sync status, passthrough/thru routing, interrupt-driven period notification, and noninterleaved PCM copy/mmap support.

Like `hdspm.c`, this is sound-driver code within the source snapshot, not distributed filesystem logic.

## Important APIs, Types, and Functions

Core state and hardware definitions:

- Module parameters `index[]`, `id[]`, `enable[]`, and `precise_ptr[]` control ALSA card numbering, card enablement, and optional precise hardware pointer behavior.
- Register and bit macros describe status, control, buffer-address, IRQ clear, timecode, thru, latency, S/PDIF, sync, and channel-buffer layout.
- `struct snd_rme9652` is the per-card state: lock, IRQ/MMIO fields, cached `control_register`, `thru_bits`, S/PDIF control cache, card name, hardware pointer smoothing state, DMA buffer objects, aligned playback/capture buffer pointers, stream PIDs/substreams, running bitmask, passthru flag, hardware revision, last detected rates, channel map, ALSA card/PCM/control pointers, and PCI device.
- Channel maps translate logical ALSA channels into hardware DMA channel slots for Digi9652/Digi9636 and single/double speed. Missing channels are marked `-1`.

PCI, memory, and ALSA setup:

- `snd_rme9652_probe()` allocates an ALSA card with embedded `struct snd_rme9652`, runs `snd_rme9652_create()`, fills names, registers the card, and stores PCI drvdata.
- `snd_rme9652_create()` validates supported EEPROM revisions, enables PCI, maps BAR0 with `devm_ioremap()`, requests a shared IRQ, detects hardware revision and card model, sets channel counts, enables PCI bus mastering, initializes DMA memory, creates PCM and controls, creates proc status, initializes runtime state, applies defaults, and initializes the S/PDIF receiver for rev 1.5 cards.
- `snd_rme9652_initialize_memory()` allocates devres-managed DMA pages for capture and playback, copies the DMA buffer descriptors into driver-owned fields, aligns bus addresses to 64 KiB boundaries, writes capture/playback base addresses to hardware, adjusts CPU pointers by the same offset, and caches `capture_buffer`/`playback_buffer`.
- `snd_rme9652_create_pcm()` registers one playback and one capture PCM device with separate operation tables.
- `snd_rme9652_create_controls()` adds IEC958 controls, S/PDIF input/output, sync mode/source, thru, sample-rate, ADAT sync, passthru, optional ADAT3 sync for full cards, and optional ADAT1 input-source control for newer revisions.

PCM and hardware operation:

- Playback ops use `snd_rme9652_playback_open()`, `snd_rme9652_playback_release()`, `snd_rme9652_hw_params()`, `snd_rme9652_trigger()`, `snd_rme9652_hw_pointer()`, `snd_rme9652_playback_copy()`, and `snd_rme9652_hw_silence()`.
- Capture ops mirror playback with `snd_rme9652_capture_open()`, `snd_rme9652_capture_release()`, and `snd_rme9652_capture_copy()`.
- `rme9652_set_rate()` accepts 44.1/48/88.2/96 kHz, rejects non-exclusive or unsafe speed-mode changes while streams are open, updates frequency/double-speed bits, restarts if necessary, and swaps the active channel map.
- `rme9652_set_interrupt_interval()` encodes the requested period size into latency bits, optionally stopping/restarting the engine, then recomputes `period_bytes`, pointer mask, and jitter tolerance.
- `rme9652_hw_pointer()` returns either coarse 0/period positions or, when `precise_ptr` is enabled, decodes buffer-position bits with an 80-frame jitter guard.
- `rme9652_channel_buffer_location()` maps logical channel to playback/capture buffer base and rejects invalid or unavailable channels. Copy and silence callbacks operate directly on per-channel noninterleaved buffers.
- `snd_rme9652_trigger()` maintains aggregate running state for playback/capture, coordinates ALSA sync groups, silences playback when capture runs without playback data, and starts/stops the hardware only at aggregate transitions.

Controls and status:

- IEC958 helpers convert between ALSA `struct snd_aes_iec958` status bits and cached hardware control bits for professional/non-audio/emphasis state.
- `rme9652_set_spdif_input()`, `rme9652_set_spdif_output()`, `rme9652_set_sync_mode()`, `rme9652_set_sync_pref()`, `rme9652_set_thru()`, and `rme9652_set_passthru()` update cached control state and write MMIO registers.
- `rme9652_spdif_write_byte()`, `rme9652_spdif_read_byte()`, `rme9652_write_spdif_codec()`, `rme9652_spdif_read_codec()`, and `rme9652_initialize_spdif_receiver()` bit-bang the rev 1.5 hardware S/PDIF receiver.
- `rme9652_spdif_sample_rate()` decodes S/PDIF sample rate from either receiver codec data or status bits; `rme9652_adat_sample_rate()` derives ADAT rate from current speed and status.
- `snd_rme9652_proc_read()` exports a detailed `/proc/asound/.../rme9652` status page with buffer addresses, IRQ/MMIO, latency, hardware pointer, clock mode, S/PDIF settings, ADAT rates/sync, timecode validity, and thru status.

## Control Flow

The driver enters through `snd_rme9652_probe()`. It checks the module card slot and enable flag, allocates `snd_card`, binds the embedded private state to the PCI device, and delegates all hardware setup to `snd_rme9652_create()`. Creation validates the revision, enables and maps PCI resources, requests IRQ, detects the specific Digi9652/Digi9636 variant, allocates aligned DMA buffers, creates ALSA-visible devices, initializes stream ownership to idle, writes defaults, and optionally programs the S/PDIF receiver.

Default setup sets S/PDIF input to coaxial, AutoSync clock mode, maximum latency, resets hardware pointers by writing zero to FIFO pointer registers, clears all thru routes, and calls `rme9652_set_rate(..., 48000)` to establish a valid channel map.

On playback or capture open, the driver sets the ALSA runtime hardware description, attaches the preallocated aligned DMA buffer, stops the engine if this is the first stream, clears thru routing, stores the current PID/substream, and installs constraints. Hardware-params enforces compatible rate and period when the opposite stream is open by another process. Otherwise, it programs sample rate and interrupt interval. Trigger start/stop then transitions the aggregate engine, with silence fill safeguards for capture-only or playback-stop-while-capture-runs cases.

Interrupt handling is compact: `snd_rme9652_interrupt()` checks the IRQ pending bit, writes the IRQ clear register, and calls `snd_pcm_period_elapsed()` for active capture and playback streams. Hardware pointer reads are used by ALSA pointer and reset ioctl handling.

Control writes are generally protected by `rme9652->lock`, check exclusive use for settings that can disrupt stream layout or signal routing, update cached register bits, write the control register, and stop/restart the engine when the setting is expected to affect live routing.

## State and Persistence Behavior

`control_register` is the persistent cached software view of hardware control state. It stores start/IRQ enable, latency, clock mode, rate, S/PDIF mode, input routing, sync preference, and rev 1.5 receiver bits. Control handlers and PCM paths mutate this field under the card spinlock before writing MMIO.

`creg_spdif` stores the default IEC958 playback status, while `creg_spdif_stream` stores the active PCM stream status. Playback open copies the default into stream state and activates the stream control; playback close marks the stream control inactive again.

DMA memory persists for the card lifetime through devres-managed allocations copied into `playback_dma_buf` and `capture_dma_buf`. The driver adjusts the copied bus address and CPU area to meet the hardware 64 KiB alignment requirement and writes the aligned bus addresses to hardware once during initialization.

Stream ownership persists in `playback_pid`, `capture_pid`, `playback_substream`, `capture_substream`, and the `running` bitmask. These fields gate exclusive use and duplex compatibility. `period_bytes`, `hw_offsetmask`, `prev_hw_offset`, and `max_jitter` persist the current pointer/latency model.

`thru_bits` and `passthru` persist hardware routing state. Passthru mode directly starts the engine without interrupts after enabling all thru channels; normal stream open disables thru routing.

No on-disk persistence is present. All state is per-device runtime state recreated at probe.

## Dependencies and Integration Points

Core dependencies include Linux PCI managed resource APIs, MMIO helpers, IRQ handling, spinlocks, `array_index_nospec()`, devres DMA page allocation, and ALSA core/control/PCM/proc/asoundef APIs.

Major integration points:

- PCI binding uses vendor `0x10ee` and device `0x3fc4`, then disambiguates hardware by PCI revision and status register probing.
- ALSA PCM exposes noninterleaved S32_LE capture/playback with mmap support, two-period hardware operation, and channel/rate constraints tied to single/double speed.
- ALSA controls expose IEC958 status, S/PDIF connectors, sync clocking, thru/passthru routing, sample-rate status, ADAT lock/sync checks, and optional rev/model controls.
- ALSA proc provides user-visible diagnostics under the card's proc tree.
- The interrupt handler feeds ALSA period elapsed notifications and shares the IRQ line.

## Risks and Edge Cases

- The DMA alignment strategy copies devres DMA descriptors and advances address/area pointers. Any change to allocation size, alignment arithmetic, or buffer lifetime can break hardware DMA or free accounting.
- Speed changes alter channel maps and available channel counts. The driver blocks single/double speed changes while streams are open, but externally induced ADAT rate changes are explicitly noted as difficult to solve.
- `precise_ptr` is exposed as unreliable by the module parameter description. The jitter filter prevents small backward pointer movement, but false pointer reports can still disrupt ALSA timing.
- `rme9652_set_thru()` maps a logical channel through `channel_map` without checking for `-1` in the single-channel case. Existing callers usually bound channels by current visible channel count, but this is a risk if new callers pass unavailable logical channels.
- Some control put paths clamp with modulo rather than rejecting out-of-range enum values, preserving historical behavior but potentially surprising callers.
- The rev 1.5 S/PDIF receiver is bit-banged through control bits. Timing or locking changes around S/PDIF codec access can affect receiver programming.
- Passthru mode starts hardware without interrupts and rewrites a custom control register value. Normal PCM open paths must clear passthru/thru state before audio streaming.
- Proc and status reads are live MMIO snapshots and can race with control changes; they are diagnostic rather than strongly consistent.

## Test Signals

Useful validation signals include:

- Build coverage for `CONFIG_SND_RME9652` and standard ALSA PCI sound configurations.
- Probe smoke on supported revisions: Digi9636 original/Rev G and Digi9652 original/Rev G, including rev 1.5 S/PDIF receiver paths.
- ALSA PCM tests for playback, capture, and duplex with S32_LE noninterleaved channels at 44.1/48/88.2/96 kHz and legal period sizes.
- Same-PID and different-PID duplex tests to verify rate/period compatibility enforcement.
- `precise_ptr=0` and `precise_ptr=1` timing checks with `aplay`/`arecord` or ALSA latency tools, watching for hw pointer underrun/overrun messages.
- Control tests through `amixer` for IEC958 status, S/PDIF input/output, sync mode/source, thru, passthru, and ADAT1 input source where available.
- `/proc/asound/card*/rme9652` checks for expected card model, latency, clock, S/PDIF, ADAT lock/sync, timecode, and thru status.
- IRQ/period tests confirming shared IRQ returns `IRQ_NONE` when not pending and delivers period elapsed callbacks only for active substreams.
- Negative tests for invalid channel info and unavailable channel mappings in single/double speed modes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme9652/rme9652.c -->
