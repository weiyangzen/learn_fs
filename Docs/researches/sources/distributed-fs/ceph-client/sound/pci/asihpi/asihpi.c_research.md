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
