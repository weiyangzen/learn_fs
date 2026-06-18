# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.c

## Purpose

This is the main ALSA PCI driver for Digigram PCXHR-compatible cards. It registers supported PCI IDs, maps board parameters, allocates one manager for a physical PCI device, creates one or more ALSA cards for the board's logical chips, implements PCM callbacks, owns sample-clock selection at the stream layer, provides proc diagnostics, and tears down hardware on remove.

## Important APIs, Types, And Functions

- Module parameters `index`, `id`, `enable`, and `mono` control ALSA card registration and mono-capture mode.
- `pcxhr_ids[]` and `pcxhr_board_params[]` map PLX/Digigram device IDs to board names, playback/capture chip counts, firmware sets, and DSP firmware numbers.
- `pcxhr_set_clock()` is the exported clock programming path. It selects generic PCXHR or HR222 clock handling, then sends `CMD_MODIFY_CLOCK` when the hardware control register changed.
- `pcxhr_get_external_clock()` dispatches external clock detection to generic PCXHR or HR222 implementations.
- PCM operations are `pcxhr_open()`, `pcxhr_close()`, `pcxhr_hw_params()`, `pcxhr_prepare()`, `pcxhr_trigger()`, and `pcxhr_stream_pointer()`.
- `pcxhr_create_pcm()` creates ALSA PCM devices and managed DMA buffers.
- `pcxhr_probe()` and `pcxhr_remove()` implement PCI lifecycle through `module_pci_driver()`.

## Control Flow

Probe checks the module enable slot, enables the PCI device, restricts DMA to 32-bit bus-mastering, allocates `pcxhr_mgr`, derives board feature flags, requests PCI regions and a shared threaded IRQ, initializes mutexes and a reusable RMH buffer, then creates ALSA cards for each logical chip. It registers basic proc entries early, allocates the hostport purge DMA buffer, and calls `pcxhr_setup_firmware()`. Firmware setup later creates PCM and mixer devices and re-registers the cards after DSP initialization.

PCM open chooses the `pcxhr_stream` object from playback or capture arrays, applies hardware constraints, rejects already-open streams, disables float format on HR stereo boards, locks the sample rate when another stream or external clock already owns it, sets sync-start behavior, and increments `ref_count_rate`. `hw_params` stores channel count and format. `prepare` programs the card clock once for the first stream and starts the DSP timer. `trigger` either starts a single stream immediately or schedules all linked streams and calls `pcxhr_start_linked_stream()` for synchronized pipe start. Stop marks scheduled stop and sends stop-stream commands. Close releases the sample-rate lock, stops the hardware timer when the last stream closes, and frees the stream slot.

Linked start first stops affected pipes, restores stream formats and ring-buffer addresses, starts each stream, starts all affected pipes together, then marks streams running under the interrupt lock. Runtime pointers are not read directly from DMA hardware on every call; they use timer-maintained period counters updated from the threaded IRQ.

## State And Persistence

`pcxhr_mgr` is the physical-device state: PCI device, IRQ, ports, mutexes, firmware/DSP flags, board feature flags, clock state, timer state, async error counters, cached control registers, and card pointers. `snd_pcxhr` is per logical card and caches PCM pipes, streams, mixer settings, and AES bits. `pcxhr_stream` carries ALSA substream linkage, format/channels, pipe, status, and timer-derived playback/capture position. There is no persistent on-disk state; firmware is requested from the kernel firmware store at probe time.

## Dependencies And Integration Points

The file integrates with ALSA core, PCM, procfs info, PCI, DMA mapping, request-threaded-IRQ, and the rest of the PCXHR driver through `pcxhr_core.h`, `pcxhr_hwdep.h`, `pcxhr_mixer.h`, and `pcxhr_mix22.h`. All hardware programming below stream setup is expressed as `pcxhr_rmh` DSP commands sent through `pcxhr_send_msg()`.

## Risks

- Sample-rate ownership is global per manager; bugs in `ref_count_rate` or close error paths can leave the card stuck at a rate or stop the DSP timer while streams remain active.
- Stream state transitions are strict; unexpected status values cause `-EINVAL` and can leave pipes stopped or stream state inconsistent.
- Linked start intentionally stops and restarts pipes, so failures midway can leave streams scheduled or started but pipes not running.
- Probe registers cards before and after firmware setup; error paths must free all partially created cards and hardware resources.
- Continuous rates use PLL programming and may return a real rate different from the requested rate; userspace and diagnostics must treat `sample_rate_real` separately.

## Test Signals

Test matrix should include all board families where possible, mono and stereo capture module parameters, simultaneous playback/capture, linked sync-start groups, open/close reference-count churn, external clock selection with and without lock, suspend-like remove paths, proc `info/sync/gpio/ltc`, and xrun/error counter visibility.
