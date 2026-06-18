# sources/distributed-fs/ceph-client/sound/pci/rme32.c Research

## Purpose

`rme32.c` is the ALSA PCI driver for RME Digi32, Digi32/8, and Digi32 PRO cards, including Sek'd-branded equivalents. It exposes S/PDIF PCM on all supported cards and ADAT PCM on Digi32/8. The hardware has one shared audio buffer and one start/interrupt mechanism, so the driver defaults to half-duplex and optionally offers a software-assisted full-duplex mode through the `fullduplex` module parameter.

The driver maps the device I/O memory window, directly uses it as ALSA mmap/copy storage in half-duplex mode, maintains a cached write-control register, exposes mixer controls for input/loopback/clock/S/PDIF status bits, and reports card state through proc.

## Important APIs, Types, and Functions

Module parameters are `index`, `id`, `enable`, and `fullduplex`. `fullduplex` changes the PCM ops and buffer model from direct I/O-memory mmap to intermediate system memory with `snd_pcm_indirect`.

The core state is `struct rme32`, which contains the spinlock, IRQ, physical port, `iobase`, cached `wcreg`, S/PDIF defaults and stream status bits, cached read register `rcreg`, revision, currently open playback/capture substreams, frame-size logs, byte period sizes, full-duplex mode flag, running stream bitmap, two `struct snd_pcm_indirect` records, ALSA card/PCM objects, PCI device, and the active S/PDIF control pointer.

Important helpers:

- `snd_rme32_pcm_byteptr()` reads the low hardware DMA byte pointer from the control register.
- `snd_rme32_playback_getrate()` and `snd_rme32_playback_setrate()` map control-register frequency and double-speed bits to 32/44.1/48 kHz and PRO-only 64/88.2/96 kHz modes.
- `snd_rme32_capture_getrate()` decodes receiver lock/error/frequency bits, with different mappings for CS8412 versus CS8414 receivers.
- `snd_rme32_setclockmode()`, `snd_rme32_getclockmode()`, `snd_rme32_setinputtype()`, and `snd_rme32_getinputtype()` implement ALSA mixer enumerations.
- `snd_rme32_setformat()` and `snd_rme32_setframelog()` configure sample width and frame-byte shifts.
- `snd_rme32_playback_hw_params()` and `snd_rme32_capture_hw_params()` validate rates, format, S/PDIF/ADAT compatibility, and matching playback/capture period byte sizes.
- `snd_rme32_pcm_start()`, `snd_rme32_pcm_stop()`, and `snd_rme32_pcm_trigger()` coordinate the single hardware start bit across grouped playback/capture streams.
- Full-duplex helpers `snd_rme32_playback_fd_ack()`, `snd_rme32_capture_fd_ack()`, `snd_rme32_playback_fd_pointer()`, and `snd_rme32_capture_fd_pointer()` use ALSA indirect-transfer helpers to copy between software buffers and the shared hardware buffer.

PCM capability tables distinguish S/PDIF versus ADAT and half-duplex versus full-duplex. Half-duplex uses `SNDRV_PCM_INFO_MMAP_IOMEM` with fixed `RME32_BUFFER_SIZE` and `RME32_BLOCK_SIZE`; full-duplex uses normal mmap with a larger `RME32_MID_BUFFER_SIZE` software buffer and fixed 8192-byte periods.

## Control Flow

Probe enters `snd_rme32_probe()`, which wraps `__snd_rme32_probe()`. The inner probe claims an ALSA card slot, allocates a card-private `struct rme32`, copies the requested full-duplex parameter, and calls `snd_rme32_create()`. Creation enables the PCI device, claims regions, maps `RME32_IO_SIZE`, requests the shared IRQ, reads revision byte 8, creates the S/PDIF PCM, optionally creates the ADAT PCM, assigns either half-duplex or full-duplex ops, stops the device, resets the DAC and DMA pointer, initializes the cached write-control register to normal muted playback with a default input, creates controls, and creates proc output. Probe then names and registers the card.

Open paths enforce one playback and one capture substream at a time. S/PDIF playback clears ADAT mode and activates the IEC958 stream control. ADAT playback sets ADAT mode. Capture opens check the current receiver signal: S/PDIF capture rejects ADAT input and ADAT capture rejects non-ADAT input when a valid rate is present. If AutoSync provides a valid input rate, runtime capabilities are narrowed to that single rate.

`hw_params` is where hardware mode is committed. In half-duplex mode, runtime DMA points directly at `RME32_IO_DATA_BUFFER`; copy/silence/mmap callbacks operate on I/O memory. In full-duplex mode, managed continuous system memory backs ALSA buffers and ack callbacks shuttle data. Both playback and capture require period byte sizes to match when the opposite direction is already configured, because the hardware has one interrupt cadence.

Triggering walks the ALSA sync group and updates `rme32->running` for playback and capture. The actual hardware start bit is set when any stream is running and cleared only after all streams stop. Pause push/release stops and restarts the hardware without resetting the DMA pointer. The IRQ handler checks `RME32_RCR_IRQ`, notifies both active substreams, and confirms the action IRQ.

## State and Persistence

The cached `wcreg` is authoritative for output format, sample clock, input select, ADAT mode, mute, professional/consumer bits, double-speed/block-mode, and start state. `wcreg_spdif` stores the default IEC958 status, while `wcreg_spdif_stream` stores the active per-stream status and is made inactive when no S/PDIF playback stream is open.

Half-duplex has no separate software audio persistence; ALSA maps or copies directly to the hardware buffer window. Full-duplex uses per-direction `snd_pcm_indirect` state to remember hardware/software offsets and queue readiness in RAM. The driver does not implement PM suspend/resume callbacks, so register and buffer state are not restored by this file.

Period byte sizes are stored separately for playback and capture and reset on close. This is used to force duplex directions to share an interrupt/block size.

## Dependencies and Integration Points

The driver depends on PCI managed device enable/region APIs, `devm_ioremap`, shared IRQs, ALSA card/PCM/control/proc APIs, `sound/pcm-indirect.h`, IEC958 AES status helpers from `asoundef.h`, and low-level I/O memory copy helpers such as `copy_from_iter_toio`, `copy_to_iter_fromio`, `memset_io`, and `snd_pcm_lib_mmap_iomem`.

It exposes two ALSA PCM devices when available: `"Digi32 IEC958"` at device 0 and `"Digi32 ADAT"` at device 1. Mixer/control integration includes IEC958 default, stream, consumer mask, professional mask, `"Input Connector"`, `"Loopback Input"`, and `"Sample Clock Source"`.

## Risks and Edge Cases

The full-duplex implementation is inherently risky because the hardware buffer is shared by playback and capture. The software splits behavior around the DMA pointer and relies on `snd_pcm_indirect` queue accounting. Any mistake in `hw_queue_size`, pointer initialization, or period matching can cause overwrite, stale capture data, or underrun-like playback corruption.

`snd_rme32_capture_hw_params()` temporarily enables AutoSync and then disables it for recording. Error exits before the disable write can leave `RME32_WCR_AUTOSYNC` set. Several control writes update `wcreg` immediately, even while streams may be configured, so control changes during active streams deserve scrutiny.

Clock/rate validation is dependent on receiver status bits. If the hardware reports no valid signal, playback may choose an internal rate; if a signal appears later, the runtime constraints may no longer reflect the actual clock relationship. PRO-only double-speed rates are guarded for playback, but capture-rate decoding depends on revision/receiver detection.

The IRQ handler calls `snd_pcm_period_elapsed()` for both active substreams whenever the single IRQ fires. That matches the paired hardware model, but it means inactive or mismatched stream state can produce misleading ALSA progress if substream pointers are stale. Close paths clear pointers under lock, but interrupt ordering should still be considered in changes.

`snd_rme32_put_clockmode_control()` uses modulo 3 even though the info callback exposes four enum items, making the `"Internal 48.0kHz"` item unreachable through put. That looks like a possible existing bug or intentional compatibility quirk requiring care before modification.

## Test Signals

Useful tests include loading each supported PCI ID, verifying `/proc/asound/card*/rme32`, opening S/PDIF playback/capture, opening ADAT on Digi32/8 only, validating runtime rate narrowing when an external signal is locked, and checking IEC958 controls activate only while S/PDIF playback is open.

Half-duplex tests should confirm direct mmap/copy paths, fixed 128 KiB buffer, fixed 8192-byte periods, loopback control, input connector selection, and interrupt cadence. Full-duplex tests should use synchronized playback/capture, mismatched-period rejection, simultaneous stop/start/pause, and long-running data-integrity checks to detect shared-buffer corruption. Hardware-clock tests should cover AutoSync, internal 32/44.1/48 kHz, PRO double-speed rates, invalid receiver signals, and ADAT versus S/PDIF channel mismatches.
