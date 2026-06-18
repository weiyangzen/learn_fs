# sources/distributed-fs/ceph-client/sound/pci/riptide/riptide.c Research

## Purpose

`riptide.c` is the ALSA PCI driver for Conexant Riptide audio devices. It binds PCI device IDs `0x127a:4310/4320/4330/4340`, loads `riptide.hex` firmware when the on-card firmware does not match the expected version, exposes one PCM device with three playback substreams and one capture substream, creates an AC97 mixer, and optionally wires MPU-401 MIDI, OPL3 FM, and gameport legacy functions through PCI configuration registers.

The driver is not a generic DMA engine wrapper. Most hardware behavior is hidden behind an on-chip ARM command interface. PCM setup, firmware download, AC97 access, sample-rate conversion, mixer gain, stream start/stop, and internal LBUS routing are all implemented as commands sent through two mailbox-style command ports.

## Important APIs, Types, and Functions

Key module parameters are `index`, `id`, `enable`, `mpu_port`, `opl3_port`, and, when gameport support is reachable, `joystick_port`. They control ALSA card numbering and legacy I/O addresses.

Important hardware abstractions:

- `struct riptideport` models the I/O BAR register layout: audio control/status and two `struct cmdport` command ports.
- `struct cmdif` owns the command-interface lock, command statistics, error count, and reset state.
- `struct snd_riptide` is the card state: ALSA objects, PCI device, firmware pointer, command interface, substream pointers, legacy addresses, IRQ counters, and suspend flag.
- `struct pcmhw` is per-substream runtime state: LBUS route, FIFO/source identifiers, stream id, current state, rate/channels/format cache, scatter-gather descriptor buffer, byte counters, and software pointer tracking.
- `struct sgd` is the little-endian hardware scatter-gather descriptor with next-link, physical segment pointer, length, and status/control bits.

Command macros such as `SEND_SSTR`, `SEND_KSTR`, `SEND_GPOS`, `SEND_SETF`, `SEND_SSRC`, `SEND_SACR`, and `SEND_RACR` wrap `sendcmd()` with the right flags and command words. `sendcmd()` is the central serialized hardware transaction routine; it waits for device readiness, selects an empty command port, writes optional parameters, reads optional responses, updates timing counters, and triggers reset logic after repeated failures.

Firmware and reset functions:

- `atoh()`, `senddata()`, and `loadfirmware()` parse Intel HEX records and write firmware words to device memory.
- `try_to_load_firmware()` performs global reset, checks the live firmware version with `SEND_GETV`, requests `riptide.hex` if needed, and downloads it.
- `riptide_reset()` resets command statistics, reloads firmware, resets AC97, clears path lists and DMA, configures modem/FM/I2S paths, enables interrupts, and marks the command interface usable.
- `snd_riptide_initialize()` allocates `struct cmdif` on first use, resets the device, applies device-specific DPLL setup, and enables MPU IRQs when MIDI is registered.

PCM path:

- `snd_riptide_pcm()` creates the ALSA PCM with three playback and one capture substream, assigns playback/capture ops, and installs managed SG DMA buffers.
- `snd_riptide_playback_open()` and `snd_riptide_capture_open()` allocate `struct pcmhw` and assign stream ids, sources, and route templates.
- `snd_riptide_hw_params()` allocates the SGD descriptor array.
- `snd_riptide_prepare()` chooses the LBUS path for channel/rate/format, builds a cyclic SGD list, allocates/frees internal routes, and writes sample format/rate commands.
- `snd_riptide_trigger()` sends stream start, stop, and pause commands while updating stream state and open stream count.
- `snd_riptide_pointer()` reads hardware position with `SEND_GPOS` and converts it to frames.
- `snd_riptide_interrupt()` is the hard IRQ handler that acknowledges device IRQs, forwards MPU IRQs, and wakes `riptide_handleirq()` for PCM period accounting.
- `riptide_handleirq()` scans every active playback/capture descriptor, consumes EOB/EOC/EOS status bits, accumulates elapsed bytes, and calls `snd_pcm_period_elapsed()`.

Control and integration functions include `snd_riptide_codec_read()`/`snd_riptide_codec_write()` for AC97 bus ops, `snd_riptide_mixer()` for AC97 mixer creation, `snd_riptide_proc_read()` for `/proc/asound` diagnostics, `__snd_card_riptide_probe()` for full card setup, and `alsa_card_riptide_init()`/`alsa_card_riptide_exit()` for registering the audio and optional joystick PCI drivers.

## Control Flow

Probe starts in `snd_card_riptide_probe()`, which wraps `__snd_card_riptide_probe()` in ALSA managed error cleanup. The inner probe claims a card slot, allocates the ALSA card, calls `snd_riptide_create()` to enable PCI, request BARs, request a threaded IRQ, set bus mastering, and initialize firmware/hardware. It then creates PCM and AC97 mixer devices, configures legacy PCI registers for MPU/OPL3/gameport addresses, optionally creates MPU-401 and OPL3 ALSA devices, initializes proc output, registers the card, stores driver data, and advances the static card index.

Normal playback or capture flow is ALSA open -> hw_params -> prepare -> trigger. Open assigns the substream slot and allocates `pcmhw`. `hw_params` allocates an SGD descriptor list separate from ALSA's managed sample buffer. `prepare` builds a cyclic descriptor chain and configures internal LBUS conversion/routing. `trigger(START)` sends `SSTR` with the descriptor-list DMA address, enables audio interrupts, unmutes the relevant digital mixer, resets software counters, and marks the stream playing. IRQ handling then derives period completion from descriptor status bits and notifies ALSA. Stop and suspend mute the mixer, send `KSTR`, mark the stream stopped, and poll the hardware position until stable.

Suspend is shallow: `riptide_suspend()` marks D3hot power state and suspends AC97. Resume re-runs `snd_riptide_initialize()`, resumes AC97, and returns to D0. Firmware may be reloaded during this path.

## State and Persistence

Persistent runtime state lives in `struct snd_riptide`, `struct cmdif`, and per-open `struct pcmhw`. Hardware state is cached only partially: firmware version, IRQ counters, open stream count, stream pointers, LBUS path selections, and command statistics are kept in RAM. AC97 and command-interface state are restored by reinitialization rather than by a full saved register image.

The firmware blob is requested through the kernel firmware API and retained in `chip->fw_entry` until card free, where `release_firmware()` runs. Per-substream DMA descriptor memory is allocated in `hw_params()` and released by `hw_free()`. ALSA managed buffers back actual audio data.

The device's own registers, LBUS routes, stream states, AC97 codec, and mixers are volatile. `riptide_reset()` rebuilds a baseline graph for modem/FM/I2S and output paths. User-selected PCM stream parameters are reapplied on prepare.

## Dependencies and Integration Points

This file integrates with PCI (`pcim_enable_device`, BAR requests, PCI config-space legacy registers, `pci_register_driver`), ALSA core (`snd_devm_card_new`, `snd_card_register`), ALSA PCM, AC97, raw MIDI MPU-401, OPL3 hwdep, proc info, firmware loading, threaded IRQs, optional gameport support, and PM sleep through `DEFINE_SIMPLE_DEV_PM_OPS`.

The driver assumes port-I/O BAR access using `inl`/`outl`; `chip->port` is cast to `struct riptideport *` and command macros take addresses of fields as I/O port offsets. The optional joystick path is a separate PCI driver matching companion device IDs and manually requests the legacy gameport I/O region.

## Risks and Edge Cases

The command interface is the primary risk. `sendcmd()` busy-waits with microsecond delays under a spinlock and can return several hardware-specific errors. Repeated command failures trigger reset only when `is_reset` is set, and failed reset paths can leave initialization aborted. Because many higher-level helpers retry by issuing the same command twice, hardware hangs can amplify latency.

Firmware parsing trusts Intel HEX structure enough to index fixed positions in each line. Malformed firmware should not normally be user-controlled, but the parser does not deeply validate checksums or line length. Firmware version assignment also stores the old probed version after download rather than re-reading a new version, so proc reporting may be stale after a load.

DMA descriptor construction is subtle. The code computes segment sizes to align period boundaries, builds a cyclic list, but writes `data->sgdbuf[i].dwSegLen` after a loop that already used `i == pages`; this relies on the allocated `DESC_MAX_MASK + 1` entries and is a fragile area for bounds reasoning. IRQ period accounting depends on hardware setting and clearing descriptor status bits correctly.

`snd_riptide_trigger()` calls `setmixer(cif, data->mixer, 0, 0)` even after an `if (data->mixer != 0xff)` block, so a `0xff` mixer id can still be passed on stop. State counters such as `openstreams` are updated under `chip->lock`, but command-interface operations use a separate lock, so ordering between stream state, command completion, and threaded IRQ processing should be treated carefully.

Suspend/resume does not save active stream buffers or restart streams. Runtime users should expect streams to be re-prepared after resume. The legacy MPU/OPL3/gameport configuration touches fixed I/O ports and can fail when regions are unavailable.

## Test Signals

Useful validation signals are successful `modprobe` with `riptide.hex` available, `dmesg` showing firmware readiness without command errors, ALSA card registration with PCM, AC97 mixer controls, optional MIDI/OPL3 devices, and `/proc/asound/card*/riptide` showing sane firmware, mixer, IRQ, and route data.

Runtime tests should cover playback on all three playback substreams, capture, non-48 kHz conversion paths, mono/stereo and 8/16-bit formats, stop/pause/resume triggers, period interrupt cadence, AC97 mixer read/write, firmware reload after cold reset, suspend/resume, and behavior when MPU/OPL3/gameport ports are disabled or unavailable. Fault-oriented tests should watch for command timeouts, unexpected `EOS_STATUS`, missing period interrupts, and DMA pointer regressions.
