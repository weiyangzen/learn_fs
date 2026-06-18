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
