# sources/distributed-fs/ceph-client/sound/pci/rme9652/hdsp.c

## Purpose

`hdsp.c` is the ALSA PCI driver for RME Hammerfall DSP family audio interfaces backed by the Xilinx Hammerfall DSP PCI device. It supports Digiface, Multiface, RPM, HDSP 9652, and HDSP 9632 variants. The driver owns PCI discovery, MMIO register access, DMA buffer setup, firmware loading for external I/O box devices, PCM playback/capture, raw MIDI ports, ALSA mixer/control elements, hwdep ioctls, `/proc` diagnostics, interrupt handling, and device teardown.

The file is hardware-facing and stateful. It translates ALSA PCM/control/rawmidi/hwdep callbacks into MMIO writes to HDSP control, FIFO, MIDI, meter, and DMA address registers. It also maintains software mirrors of hardware settings so ALSA controls can expose stable values while writes are serialized with spinlocks.

## Important APIs, Types, and Data

- Module and PCI entry points: `module_pci_driver(hdsp_driver)`, `snd_hdsp_probe()`, `snd_hdsp_create()`, and `snd_hdsp_card_free()`.
- ALSA objects: `struct snd_card`, `struct snd_pcm`, `struct snd_pcm_ops`, `struct snd_rawmidi`, `struct snd_rawmidi_ops`, `struct snd_kcontrol_new`, `struct snd_hwdep`, and `struct snd_info_entry`.
- Public UAPI from `include/uapi/sound/hdsp.h`: `enum HDSP_IO_Type`, `HDSP_MATRIX_MIXER_SIZE`, `struct hdsp_peak_rms`, `struct hdsp_config_info`, `struct hdsp_firmware`, `struct hdsp_version`, `struct hdsp_mixer`, `struct hdsp_9632_aeb`, and `SNDRV_HDSP_IOCTL_*`.
- Internal state: `struct hdsp` stores the card lock, PCM substreams, two `struct hdsp_midi` ports, deferred MIDI work, cached control registers, cached S/PDIF flags, I/O type, firmware revision/state, DMA buffers and aligned CPU/bus addresses, stream owner PIDs, current sample rate, current channel map, loopback bitmask, mixer matrix cache, hwdep/PCM/card pointers, PCI resources, and last DDS value.
- MIDI state: `struct hdsp_midi` stores rawmidi object pointers, active input/output substreams, an output polling timer, a MIDI spinlock, and pending flags for workqueue-based input draining.
- Register definitions cover write offsets (`HDSP_controlRegister`, `HDSP_control2Reg`, `HDSP_fifoData`, `HDSP_inputEnable`, `HDSP_outputEnable`, MIDI data, DMA address registers), read offsets (`HDSP_statusRegister`, `HDSP_status2Register`, MIDI status/data, FIFO status), meter regions, and many bit masks for clocks, S/PDIF, sync, latency, MIDI IRQs, H9632 gains, RPM controls, and firmware/programming modes.
- Channel maps (`channel_map_df_ss`, `channel_map_mf_ss`, `channel_map_ds`, `channel_map_H9632_*`) translate logical ALSA channels into hardware DMA channel slots for single-, double-, and quad-speed modes.

## Initialization and Control Flow

`snd_hdsp_probe()` allocates an ALSA card with `snd_devm_card_new()`, stores PCI/card context in `struct hdsp`, calls `snd_hdsp_create()`, registers the card, and attaches it to PCI driver data. Module parameters `index`, `id`, and `enable` control card slot allocation.

`snd_hdsp_create()` initializes software state, reads the PCI revision to identify legacy DSP, HDSP 9652, or HDSP 9632 cards, sets the PCI latency timer, enables the PCI device, requests PCI BARs, maps MMIO, requests a shared IRQ, initializes DMA memory, and then branches by hardware type:

- HDSP 9652 and 9632 are internal PCI cards. They skip external I/O box firmware upload, set `io_type`, create hwdep, initialize channels, mark firmware loaded, create ALSA devices, and set defaults.
- Digiface, Multiface, and RPM require an external I/O box and firmware. The driver waits for the box, attempts hotplug firmware loading, or defers full ALSA-device creation behind a hwdep firmware-upload path when firmware is not yet available.

`hdsp_request_fw_loader()` chooses one of the declared firmware names (`rpm_firmware.bin`, `multiface_firmware*.bin`, `digiface_firmware*.bin`) based on `io_type` and firmware revision, calls `request_firmware()`, verifies size, caches the firmware pointer, programs it through the FIFO, enables I/O, creates hwdep if needed, initializes channels/MIDI, and creates/registers ALSA devices when initialization was deferred.

`snd_hdsp_create_alsa_devices()` creates the PCM device, rawmidi ports, control elements, and `/proc` reader, initializes stream pointers/PIDs, calls `snd_hdsp_set_defaults()`, and registers the card if this is the deferred initialization path.

## Firmware, I/O Box, and Hardware Programming

Firmware loading is coordinated by `hdsp_check_for_firmware()`, `hdsp_request_fw_loader()`, `snd_hdsp_load_firmware_from_cache()`, and `SNDRV_HDSP_IOCTL_UPLOAD_FIRMWARE`.

`snd_hdsp_load_firmware_from_cache()` writes programming/load control bits, streams `HDSP_FIRMWARE_SIZE` words to `HDSP_fifoData`, waits on FIFO availability with `hdsp_fifo_wait()`, restores endian/control2 state, and sets `HDSP_FirmwareLoaded`. If initialization was already complete, it reacquires the card lock and restores default hardware settings.

`hdsp_get_iobox_version()` probes external box type by toggling programming modes and reading status bits; if firmware is already loaded it decodes `HDSP_status2Register`. `hdsp_check_for_iobox()` and `hdsp_wait_for_iobox()` treat `HDSP_ConfigError` as a missing I/O box for non-9652/non-9632 devices.

Low-level MMIO helpers are intentionally thin: `hdsp_write()` wraps `writel()`, and `hdsp_read()` wraps `readl()`. Most hardware sequencing is explicit in the caller, so ordering and register bit composition are major maintenance concerns.

## PCM Runtime Behavior

The driver exposes one playback and one capture PCM device with non-interleaved, 32-bit samples, two periods, mmap support, sync-start support, and hardware-specific channel/rate constraints. Playback also supports `SNDRV_PCM_INFO_DOUBLE`.

Open paths (`snd_hdsp_playback_open()`, `snd_hdsp_capture_open()`) check I/O box and firmware readiness, bind runtime hardware descriptors to the aligned DMA buffer, save the caller PID and substream pointer, install period-size and channel/rate constraint rules, and adjust H9632 support up to 192 kHz. Playback open also activates the IEC958 stream control.

`snd_hdsp_hw_params()` serializes important runtime changes under `hdsp->lock`. It enforces matching rate and period size when capture and playback are open by different PIDs, applies the IEC958 stream bits for playback, calls `hdsp_set_rate()` unless clock-source locking is enabled, and updates the hardware interrupt interval with `hdsp_set_interrupt_interval()`.

`hdsp_set_rate()` validates the requested rate against clock mode and hardware type, rejects speed-mode changes while streams are open, updates frequency bits, writes DDS values for newer H9632 firmware, selects the correct channel map, and updates `system_sample_rate`. External AutoSync mode accepts a requested PCM rate only when it matches the detected external rate or recognized ADAT double/quad-speed relationships.

`snd_hdsp_trigger()` starts/stops capture and playback as a synchronized pair where appropriate. It mirrors the running streams in `hdsp->running`, silences playback when capture runs without active playback, calls `hdsp_start_audio()` on the transition from stopped to running, and calls `hdsp_stop_audio()` on the transition back to idle.

`snd_hdsp_hw_pointer()` returns either a coarse period boundary based on `HDSP_BufferID` or a precise pointer based on `HDSP_BufferPositionMask`, depending on the `Precise Pointer` control. `snd_hdsp_reset()` aligns grouped substream software pointers. `snd_hdsp_playback_copy()`, `snd_hdsp_capture_copy()`, `snd_hdsp_hw_silence()`, and `snd_hdsp_channel_info()` map ALSA channel indices through `hdsp->channel_map` into the card's per-channel DMA buffers.

## Controls, Mixer, MIDI, and Hwdep

The control surface is built from `snd_hdsp_controls`, `snd_hdsp_9632_controls`, `snd_hdsp_rpm_controls`, dynamically indexed ADAT sync checks, the H96xx AEB toggle, and H9632 output loopback controls. Controls expose IEC958 status/masks, S/PDIF input/output flags, sample clock source, clock-source locking, clock status, preferred sync reference, AutoSync reference/rate, line out, precise pointer mode, MIDI workqueue mode, mixer gains, H9632 DA/AD/phone gains and DDS offset, RPM input/bypass/disconnect options, sync checks, and H9632 loopback.

Mixer writes use `hdsp_write_gain()`. H9652/H9632 mixer memory is dword-addressed with two 16-bit gains packed together and mirrored in `mixer_matrix`; external-box variants send packed address/value words through the FIFO. Address key helpers distinguish input-to-output and playback-to-output matrix slots and vary by firmware revision and card type.

MIDI support creates one port for Multiface/RPM/H9632 and two ports for Digiface/H9652. Input can be drained in IRQ context or via `system_highpri_wq` depending on `use_midi_work`; output is timer-polled because it is not interrupt-driven. MIDI input IRQs are disabled while deferred work is pending and re-enabled after `snd_hdsp_midi_input_read()`.

The hwdep interface implements:

- `SNDRV_HDSP_IOCTL_GET_PEAK_RMS`: reads card-specific peak/RMS meter regions and copies them to userspace.
- `SNDRV_HDSP_IOCTL_GET_CONFIG_INFO`: snapshots sync, clock, S/PDIF, gain, line-out, AEB, and RPM/H9632-specific settings.
- `SNDRV_HDSP_IOCTL_GET_9632_AEB`: reports H9632 extension-board channel counts.
- `SNDRV_HDSP_IOCTL_GET_VERSION`: reports external-box I/O type and firmware revision.
- `SNDRV_HDSP_IOCTL_UPLOAD_FIRMWARE`: accepts userspace firmware, caches it in `fw_uploaded`, loads it, and completes deferred device creation.
- `SNDRV_HDSP_IOCTL_GET_MIXER`: copies the cached mixer matrix to userspace.

`snd_hdsp_proc_read()` provides a diagnostic `/proc/asound/.../hdsp` view. It reads live status registers, may trigger firmware loading if firmware is cached or available, and prints buffer, IRQ, control/status, MIDI, clock, sync, S/PDIF, RPM, H9632, and AEB information.

## State and Persistence

Persistent driver state is in memory only; no settings are written to disk by this file. Hardware state is reconstructed at probe, after firmware load, and on default reset. Firmware can be cached either as a kernel firmware pointer (`hdsp->firmware`) or a vmalloc copy uploaded through hwdep (`hdsp->fw_uploaded`) and is released/freed in `snd_hdsp_card_free()`.

Important cached fields include:

- `control_register` and `control2_register`, the software mirrors for hardware register writes.
- `creg_spdif` and `creg_spdif_stream`, default and active IEC958 stream status bits.
- `mixer_matrix`, the software copy used for reads and packed H96xx writes.
- `system_sample_rate`, `dds_value`, `channel_map`, and channel-count fields, which drive PCM constraints and buffer mapping.
- `playback_pid`, `capture_pid`, `playback_substream`, `capture_substream`, and `running`, which enforce shared-device semantics and synchronize triggers.
- `state` flags for initialization completion, firmware loaded, and firmware cached.
- `io_loopback`, used to mirror H9632 output loopback toggles.

The code uses spinlocks around most control-register, stream, MIDI, and mixer state mutations. Several functions document that callers must already hold `hdsp->lock` or be in initialization paths where serialization is unnecessary.

## Dependencies and Integration Points

- Linux PCI/device-managed resource APIs: `pcim_enable_device()`, `pcim_request_all_regions()`, `pci_set_master()`, `pci_read_config_word()`, `pci_write_config_byte()`, `devm_ioremap()`, `devm_request_irq()`, `pci_set_drvdata()`.
- Firmware loader: `request_firmware()`/`release_firmware()` plus `MODULE_FIRMWARE()` declarations.
- ALSA core: card allocation/registration, PCM, rawmidi, control, hwdep, proc/info, DMA page allocation, runtime constraints, IEC958 helpers, and PCM period notification.
- Kernel memory/copy helpers: `vmalloc()`, `vfree()`, `copy_to_user()`, `copy_from_user()`, `copy_to_iter()`, `copy_from_iter()`.
- Kernel concurrency/timing: IRQ handler, spinlocks, timers, workqueues, `msleep()`, `ssleep()`, `udelay()`, and guarded cleanup helpers.
- Public userspace integration is through ALSA PCM devices, ALSA mixer controls, rawmidi devices, hwdep ioctls from `sound/hdsp.h`, firmware files in the firmware search path, and `/proc` diagnostics.

## Risks and Edge Cases

- Firmware sequencing is fragile: FIFO waits, programming-mode toggles, firmware-size assumptions, and the external I/O box version probe are all hardware-protocol dependent. Bad ordering can leave deferred initialization incomplete.
- `HDSP_resetPointer` and `HDSP_freqReg` share an offset, so H9632 firmware revision >= 152 requires rewriting `dds_value` after pointer reset. Regressions here can affect clock accuracy after prepare/reset.
- Rate/channel constraints are tightly coupled to speed mode and card type. Incorrect `hdsp_set_rate()` or channel-map changes can expose invalid ALSA channel counts or map channels to nonexistent DMA buffers.
- Mixer addressing differs between H96xx and external-box devices, with firmware-revision-dependent matrix widths. Bounds checks prevent some overflows, but incorrect address-key math can route audio unexpectedly.
- Concurrency is mixed across IRQ, workqueue, timer, PCM callbacks, control callbacks, and hwdep ioctls. The code relies on `hdsp->lock` and per-MIDI locks, but some live register reads are intentionally unlocked.
- `snd_hdsp_use_is_exclusive()` blocks many control changes when playback and capture are owned by different PIDs, but same-PID duplex operation can still combine control, PCM, and firmware actions in sensitive ways.
- Meter ioctls read hardware registers directly to userspace and differ by card type and speed mode; mistakes can produce stale, shifted, or partial metering data.
- Deferred firmware initialization means probe can succeed with only hwdep available. Tests and userspace tools must handle the card transitioning from firmware-needed to full ALSA-device availability.
- H9632 AEB detection uses active-low status bits and changes available channels; hardware without extension boards is an important compatibility path.

## Test Signals

Useful validation signals include:

- PCI probe logs identify the card type, map registers, request IRQ, allocate aligned DMA buffers, and either complete initialization or explicitly defer for firmware.
- Firmware paths load the expected firmware filename, reject too-short firmware, complete FIFO transfer without timeout, set `HDSP_FirmwareLoaded`, and create ALSA devices after deferred upload.
- ALSA PCM open/hw_params/prepare/trigger on playback and capture accepts valid rates/channels/period sizes for each card type and rejects invalid speed-mode transitions while streams are open.
- Duplex tests verify same-rate/same-period enforcement across separate capture/playback PIDs and sync-start behavior for grouped streams.
- MIDI input/output works on the correct number of ports per card, with both direct IRQ processing and `Use Midi Tasklet` enabled.
- Mixer tests read/write matrix entries through ALSA controls and `SNDRV_HDSP_IOCTL_GET_MIXER`, including H9652/H9632 packed mixer writes.
- Clock and sync controls report expected transitions for master/internal rates, AutoSync, S/PDIF, Word Clock, ADAT Sync, and ADAT lock status.
- H9632-specific tests cover 128/176.4/192 kHz operation, DDS offset, DA/AD/phone gains, XLR breakout, AEB channel counts, and output loopback.
- RPM-specific tests cover input 1/2 and 3/4 modes, bypass, disconnect, and the reduced channel counts.
- Hwdep ioctls return coherent config/version/meter data and fail with appropriate errors when firmware or I/O box state is invalid.
- Teardown stops audio/MIDI interrupts, cancels MIDI work, releases firmware, and frees uploaded firmware without use-after-free during active timer/workqueue paths.
