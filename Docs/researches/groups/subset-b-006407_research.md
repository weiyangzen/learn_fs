# subset-b-006407 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/riptide/riptide.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/riptide/riptide.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme32.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme96.c -->
# sources/distributed-fs/ceph-client/sound/pci/rme96.c Research

## Purpose

`rme96.c` is the ALSA PCI driver for the RME Digi96 family: Digi96, Digi96/8, Digi96/8 PRO, Digi96/8 PAD, and Digi96/8 PST. Unlike `rme32.c`, this hardware exposes separate playback and capture buffers, separate DMA pointers, separate start bits, and separate playback/capture IRQ acknowledgements. The driver therefore supports duplex operation through normal independent playback and capture paths while still coordinating synchronized ALSA trigger groups.

The file supports S/PDIF and, except on the base Digi96, ADAT PCM devices. It also supports model-specific analog input/output controls, DAC volume programming through a bit-banged SPI-like interface, clock/input selection, IEC958 status controls, loopback, monitor tracks, attenuation, proc diagnostics, and PM sleep buffer/register restoration.

## Important APIs, Types, and Functions

The main state object is `struct rme96`. It holds PCI/ALSA objects, spinlock, I/O mapping, cached write-control register `wcreg`, cached additional register `areg`, cached read register `rcreg`, default and active IEC958 bits, analog volume cache, revision, suspend buffers and saved pointers, open substream pointers, frame-size shifts, and configured period sizes.

Hardware capability macros identify feature variants: `RME96_HAS_ANALOG_IN`, `RME96_HAS_ANALOG_OUT`, `RME96_DAC_IS_1852`, `RME96_DAC_IS_1855`, `RME96_ISPLAYING`, and `RME96_ISRECORDING`. Register-bit definitions cover playback/capture start bits, sample width bits, ADAT mode, clocking, input selection, monitor selection, non-audio Dolby bit, word clock, analog mode, ADC/DAC power, and DAC serial data pins.

Important functions:

- `snd_rme96_playback_ptr()` and `snd_rme96_capture_ptr()` read independent hardware positions and convert bytes to frames using `playback_frlog` and `capture_frlog`.
- `snd_rme96_write_SPI()` bit-bangs `CDAT`, `CCLK`, and `CLATCH` in `areg` to program AD1852/AD1855 DACs.
- `snd_rme96_apply_dac_volume()` writes cached left/right volumes in the format required by the detected DAC.
- `snd_rme96_capture_getrate()` decodes analog, ADAT, and S/PDIF input rates from `areg`/`rcreg`.
- `snd_rme96_playback_getrate()` and `snd_rme96_playback_setrate()` implement internal or slave playback clock selection and double-speed rate bits.
- `snd_rme96_capture_analog_setrate()` configures analog input rates, including revision restrictions for 64/88.2 kHz.
- `snd_rme96_setclockmode()`, `snd_rme96_setinputtype()`, `snd_rme96_setattenuation()`, `snd_rme96_setmontracks()`, and related getters back ALSA controls.
- `snd_rme96_playback_hw_params()` and `snd_rme96_capture_hw_params()` bind runtime DMA to the playback or capture I/O buffer, validate clock/rate/channel compatibility, set sample width, enforce shared period size for synced duplex, program interrupt block size, and apply IEC958 stream bits.
- `snd_rme96_trigger()` is the low-level register operation helper for start/stop/reset/IRQ-clear combinations.
- `snd_rme96_playback_trigger()` and `snd_rme96_capture_trigger()` translate ALSA trigger commands into per-direction or synchronized both-direction operations.
- `rme96_suspend()` and `rme96_resume()` save and restore DMA pointers, copy both hardware buffers to vmalloc memory, disable/enable DAC, reset ADC/DAC, and restore analog volume.

PCM ops use direct I/O-memory copy and mmap callbacks: playback writes to `RME96_IO_PLAY_BUFFER`, capture reads from `RME96_IO_REC_BUFFER`, and ALSA mmap uses `snd_pcm_lib_mmap_iomem`.

## Control Flow

Probe starts in `snd_rme96_probe()` and `__snd_rme96_probe()`. The driver allocates a managed ALSA card, initializes `struct rme96`, and calls `snd_rme96_create()`. Creation enables PCI, claims regions, maps the `RME96_IO_SIZE` window, requests the IRQ, reads the revision, creates the S/PDIF PCM, optionally creates the ADAT PCM, stops both engines, initializes `wcreg` and `areg` defaults, resets ADC/DAC, enables DAC, resets playback and capture positions, initializes analog volume, creates controls, and registers proc diagnostics. Probe allocates suspend buffers when PM sleep is enabled, names the card based on PCI ID and revision, registers the ALSA card, and stores driver data.

Open paths enforce one playback and one capture substream at a time. S/PDIF playback clears ADAT mode and activates the IEC958 stream control. ADAT playback sets ADAT mode. Capture open rejects invalid source/channel combinations, such as ADAT capture while analog input is selected or S/PDIF capture when the locked input is ADAT. Playback open narrows rates to a locked external rate when in slave clock mode and not using analog input.

`hw_params` sets the runtime DMA view directly to the device buffer, configures rate and format, computes frame shifts, and forces playback/capture period bytes to match when the opposite direction is already configured. `snd_rme96_set_period_properties()` maps 2048- or 8192-byte periods into the interrupt select bit and enables interrupts. S/PDIF playback applies the per-stream AES bits to the control register.

Trigger handling supports ALSA sync groups. Each trigger callback marks all substreams in the group done, detects whether playback and capture belong to the same group, and then starts/stops/resumes either the requested direction or both directions with one low-level register update. IRQ handling checks both playback and capture IRQ bits, calls `snd_pcm_period_elapsed()` on the matching active substream, and acknowledges each IRQ independently.

## State and Persistence

`wcreg` and `areg` are the driver's cached hardware-control state. `wcreg` stores playback/capture start bits, format bits, ADAT mode, playback frequency, clock mode, input selection, monitor bits, IEC958 professional/emphasis/non-audio bits, and interrupt period selection. `areg` stores analog mode, analog sample frequency, word-clock select, DAC enable, ADC/DAC reset bits, and DAC serial programming pins.

The two hardware audio buffers are persistent only while powered. For PM sleep, the driver allocates `RME96_BUFFER_SIZE` vmalloc buffers per direction, saves the current playback/capture hardware pointers and buffer contents, disables the DAC, and on resume restores positions and buffer contents before resetting ADC/DAC and reapplying analog volume.

Substream pointers and period sizes are active-open state and are cleared on close. The analog output volume is cached in `vol[2]` and reapplied after DAC resets or double-speed transitions.

## Dependencies and Integration Points

This file integrates with PCI managed resources, shared IRQs, ALSA core/PCM/control/proc APIs, PM sleep ops, vmalloc suspend buffers, I/O-memory copy/mmap helpers, IEC958 AES status bits, and low-level `writel`/`readl` register access.

ALSA devices are `"Digi96 IEC958"` at PCM device 0 and `"Digi96 ADAT"` at PCM device 1 when the model supports ADAT. Controls include IEC958 default/stream/masks, `"Input Connector"`, `"Loopback Input"`, `"Sample Clock Source"`, and, on analog-output capable models, `"Monitor Tracks"`, `"Attenuation"`, and `"DAC Playback Volume"`.

## Risks and Edge Cases

The analog and revision-specific paths are dense. PAD/PST device IDs overlap and are distinguished by revision; XLR versus analog enumeration changes for PST revisions greater than 4. Wrong revision interpretation can expose invalid inputs or hide real ones.

`snd_rme96_capture_getrate()` appears to test `rme96->areg & RME96_AR_BITPOS_F2` instead of the `RME96_AR_FREQPAD_2` bit when deciding analog double-speed. Since `RME96_AR_BITPOS_F2` is a bit position constant, this is a suspicious area for rate decoding.

The IRQ handler assumes `playback_substream` exists when playback IRQ is set and `capture_substream` exists when capture IRQ is set. Close paths stop active engines before clearing pointers, but interrupt races remain important when modifying locking or teardown.

Rate and channel validation depends on live receiver status. If input lock changes after open/hw_params, ALSA constraints may not follow the hardware. Playback in slave mode uses capture rate unless analog input is selected; analog input forces different clock assumptions.

DAC programming is bit-banged under the same cached `areg` used for other analog/clock controls. Any concurrent `areg` updates must preserve serial bits and hardware timing. Double-speed playback changes reset the DAC and delay/reapply volume outside the main lock, so ordering with user volume changes matters.

Suspend/resume copies the entire I/O buffer while streams may conceptually exist. It restores buffer content and pointers but does not explicitly restart streams; ALSA PM sequencing must quiesce streams correctly. Failure to allocate either suspend buffer aborts probe when PM sleep is enabled.

## Test Signals

Validation should cover each PCI ID and revision-sensitive shortname, S/PDIF playback/capture, ADAT availability only on non-base models, analog input on PAD/PST, analog output controls on PRO/PAD/PST, IEC958 status bits including non-audio, direct mmap/copy operation, and `/proc/asound/card*/rme96` state reporting.

Runtime tests should exercise 2048- and 8192-byte periods, synced playback/capture trigger groups, independent start/stop/pause/resume in each direction, clock modes AutoSync/Internal/Word, S/PDIF rates through 96 kHz, ADAT 44.1/48 kHz, analog capture rates including revision-limited double-speed modes, DAC volume persistence after sample-rate changes, and suspend/resume buffer restoration. Stress tests should monitor for missed period interrupts, stale substream pointers in IRQ, and wrong channel/rate acceptance when input lock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme96.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme9652/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/rme9652/Makefile Research

## Purpose

This Makefile declares the ALSA PCI module objects for the RME9652-family directory. It builds three independent kernel modules from single C translation units: `snd-rme9652.o` from `rme9652.o`, `snd-hdsp.o` from `hdsp.o`, and `snd-hdspm.o` from `hdspm.o`.

## Important APIs, Types, and Functions

There are no C APIs, types, or functions in this file. The important Kbuild variables are:

- `snd-rme9652-y := rme9652.o`
- `snd-hdsp-y := hdsp.o`
- `snd-hdspm-y := hdspm.o`
- `obj-$(CONFIG_SND_RME9652) += snd-rme9652.o`
- `obj-$(CONFIG_SND_HDSP) += snd-hdsp.o`
- `obj-$(CONFIG_SND_HDSPM) +=snd-hdspm.o`

The `*-y` assignments define each composite module's object list. The `obj-$(CONFIG_...)` assignments include the modules when the corresponding ALSA PCI configuration symbols are enabled as built-in or module.

## Control Flow

Kbuild evaluates this file when descending into `sound/pci/rme9652`. If a configuration symbol is `y`, the corresponding `snd-*` object is linked into the built-in kernel object for that directory. If it is `m`, Kbuild emits a loadable module. If it is unset, that driver is not built.

## State and Persistence

The file has no runtime state. Its persistent behavior is build graph configuration: it maps Kconfig symbols to module targets and maps module targets to object files.

## Dependencies and Integration Points

This file integrates with the kernel Kbuild system and depends on Kconfig symbols `CONFIG_SND_RME9652`, `CONFIG_SND_HDSP`, and `CONFIG_SND_HDSPM` being defined elsewhere. The source files `rme9652.c`, `hdsp.c`, and `hdspm.c` must exist in the same directory for enabled builds.

## Risks and Edge Cases

The last line lacks a space after `+=` (`+=snd-hdspm.o`). Kbuild syntax accepts this form, but it is visually inconsistent and easy to misread. Any future split into multi-object modules must update the matching `snd-*-y` variable rather than only the `obj-*` line.

Because this Makefile only maps configuration to objects, build failures for enabled symbols usually indicate missing source files, renamed targets, or Kconfig/Makefile drift.

## Test Signals

Build validation is the main signal: enable each of `CONFIG_SND_RME9652`, `CONFIG_SND_HDSP`, and `CONFIG_SND_HDSPM` as `m` and confirm `snd-rme9652.ko`, `snd-hdsp.ko`, and `snd-hdspm.ko` are produced. A built-in configuration should include the corresponding objects in the directory's built-in archive. Static inspection should also confirm `modules.order` and `modinfo` names match the intended ALSA driver modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/rme9652/Makefile -->
