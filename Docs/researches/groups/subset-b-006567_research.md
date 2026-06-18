<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.c

## Purpose
USB ALSA card driver entry point for TASCAM US-144 and US-144MKII devices. It owns module parameters, probe/disconnect, suspend/resume, top-level card construction, URB allocation/freeing, and common cleanup.

## APIs, Types, and Functions
Registers `tascam_alsa_driver` with `module_usb_driver()`. Important functions are `tascam_probe()`, `tascam_disconnect()`, `tascam_suspend()`, `tascam_resume()`, `tascam_alloc_urbs()`, `tascam_free_urbs()`, `tascam_stop_work_handler()`, and `tascam_card_private_free()`. It calls subsystem initializers `tascam_init_pcm()`, `tascam_create_midi()`, and `tascam_create_controls()`.

## Control Flow, State, and Persistence
Probe handles the two-interface device model: interface 1 links back to the interface-0 `struct tascam_card`, while interface 0 performs a vendor handshake, selects alternate setting 1 on both interfaces, creates the ALSA card, initializes anchors, locks, work items, timer, MIDI FIFO, controls, PCM, MIDI, and coherent URB buffers. Runtime state persists in `struct tascam_card`: USB device references, active substreams, URBs, anchors, routing selections, feedback state, capture buffers, and MIDI FIFO/bitmap state. Suspend stops PCM and work, kills anchors, and sends a deep-sleep vendor command; resume restores interface altsettings and reapplies the last sample rate.

## Dependencies and Integration
Depends on USB core, ALSA card/PCM/rawmidi/control APIs, kernel workqueues/timers/kfifo, and local US-144MKII PCM, MIDI, playback, capture, and controls files.

## Risks and Test Signals
Risks include interface-1 probe ordering, `dev_idx` accounting across failed probes/disconnects, start/stop races with anchored URBs, partial allocation cleanup, and vendor handshake value drift. Test signals are hotplug/unplug, suspend/resume, altsetting restoration, ALSA card registration, URB leak checks, and playback/capture/MIDI operation after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.h

## Purpose
Private header for the US-144MKII driver, defining device protocol constants, endpoint layout, audio/MIDI buffer sizing, shared driver state, and cross-file function declarations.

## APIs, Types, and Functions
Defines USB IDs, endpoint numbers, request types, vendor requests, register selectors, URB counts, audio frame constants, MIDI buffer sizes, and capture decode geometry. Key types are `struct us144mkii_frame_pattern_observer` and `struct tascam_card`. It declares allocation, stop-work, MIDI, PCM, and control creation entry points.

## Control Flow, State, and Persistence
The header has no executable flow, but it is the authoritative schema for state shared by probe, PCM callbacks, URB completions, workqueue handlers, mixer controls, and MIDI callbacks. Persistent fields include USB/ALSA handles, URB arrays and anchors, atomic active flags, current sample rate, playback/capture counters, MIDI FIFO/in-flight bitmap, feedback pattern ring, and routing choices.

## Dependencies and Integration
Includes Linux USB, workqueue, timer, kfifo and ALSA core/control/PCM/rawmidi headers. It includes `us144mkii_pcm.h`, making the PCM declarations part of the common include boundary used by all US-144MKII source files.

## Risks and Test Signals
Risks include circular include fragility, stale comments versus actual callback behavior, buffer-size constants that must match device protocol, and unsynchronized access expectations around fields protected by `lock`, `midi_in_lock`, or `midi_out_lock`. Build coverage, sparse/lockdep, and end-to-end stream tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_capture.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_capture.c

## Purpose
ALSA PCM capture implementation for US-144MKII, including capture substream callbacks, raw USB capture buffering, deferred block decoding, channel routing, and capture URB resubmission.

## APIs, Types, and Functions
Exports `tascam_capture_ops`, `tascam_capture_work_handler()`, and `capture_urb_complete()`. Internal helpers include `tascam_capture_open()`, `tascam_capture_close()`, `tascam_capture_prepare()`, `tascam_capture_pointer()`, and `decode_tascam_capture_block()`.

## Control Flow, State, and Persistence
Open installs `tascam_pcm_hw` and stores the active capture substream. Prepare resets capture counters and raw-ring read/write pointers. Bulk capture URB completions copy received bytes into `capture_ring_buffer` under `tascam->lock`, schedule `capture_work`, and resubmit the URB. The work handler drains 512-byte raw blocks from the ring, demultiplexes them into eight 4-channel 24-bit frames in 32-bit containers, applies the current capture routing selection, then copies 3-byte samples into the ALSA DMA ring. Pointer reporting is driven by `capture_frames_processed`, which is advanced from the feedback clock path rather than from decoded bytes.

## Dependencies and Integration
Depends on USB bulk URBs, ALSA PCM runtime helpers, the shared routing helper `process_capture_routing_us144mkii()`, and the top-level `tascam_pcm_trigger()` that starts capture URBs.

## Risks and Test Signals
Risks include ring-buffer overrun with no explicit free-space check, decode format assumptions, period accounting split between feedback and capture workers, and copying `S32_LE` containers as 24-bit samples by offset. Test signals are 4-channel capture at all rates, route-control changes during capture, xrun stress, malformed/short URB handling, and period notifications aligned with playback feedback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_controls.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_controls.c

## Purpose
Creates ALSA mixer controls for US-144MKII software routing and sample-rate reporting.

## APIs, Types, and Functions
Exports `tascam_create_controls()`. It defines enum info/get/put callbacks for line output source, digital output source, capture channels 1/2 source, capture channels 3/4 source, and a read-only integer `Sample Rate` control. Static `snd_kcontrol_new` objects define control names and callbacks.

## Control Flow, State, and Persistence
Routing get/put callbacks read or update `tascam_card` fields under `tascam->lock`. Playback routing selects whether line and digital outputs receive playback channels 1/2 or 3/4; capture routing selects analog or digital input pairs for ALSA capture channels. The sample-rate getter first returns cached `current_rate`; if unknown, it sends a UAC `GET_CUR` request to the audio-in endpoint and decodes the 24-bit little-endian frequency.

## Dependencies and Integration
Depends on ALSA control APIs, USB control transfers, and the routing helpers in `us144mkii_pcm.c` and capture/playback data paths that consume these state fields.

## Risks and Test Signals
Risks include controls changing while URB workers copy audio, sample-rate USB errors being ignored when fewer than three bytes are returned, default route asymmetry from probe initialization, and control names becoming ABI-visible. Test signals are `amixer` enumeration/get/put, live route switching, invalid enum rejection, sample-rate reads before and after stream configuration, and concurrent control updates during playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_controls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_midi.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_midi.c

## Purpose
Implements ALSA rawmidi input/output for US-144MKII over proprietary bulk endpoints with packet padding and deferred processing.

## APIs, Types, and Functions
Exports `tascam_midi_in_urb_complete()`, `tascam_midi_out_urb_complete()`, and `tascam_create_midi()`. Internal callbacks include rawmidi open/close/trigger/drain operations and work handlers `tascam_midi_in_work_handler()` and `tascam_midi_out_work_handler()`.

## Control Flow, State, and Persistence
MIDI input trigger resets the FIFO, submits all IN URBs, and marks `midi_in_active`; completions enqueue raw bytes into `midi_in_fifo`, schedule work, and resubmit. The input worker consumes 9-byte device packets, strips `0xfd` padding from the first eight bytes, and feeds ALSA rawmidi. MIDI output trigger marks active and schedules work. The output worker finds a free URB bit, pulls up to eight bytes from ALSA, pads with `0xfd`, writes a final marker byte, sets the in-flight bit, and submits. Completion clears the bit and reschedules while active. Drain waits for in-flight bits to clear, cancels work, and kills anchored OUT URBs.

## Dependencies and Integration
Depends on ALSA rawmidi, USB bulk URBs, `kfifo`, spinlocks, anchors, and URBs allocated in `tascam_alloc_urbs()`.

## Risks and Test Signals
Risks include FIFO overflow not surfaced, close callbacks not clearing substream pointers, busy-wait style drain using `schedule_timeout_uninterruptible(1)`, output protocol marker/padding assumptions, and lock scope around `snd_rawmidi_transmit()`. Test signals are MIDI loopback, high-rate SysEx-like traffic, trigger stop/start cycles, disconnect during drain, and padding stripping correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_pcm.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_pcm.c

## Purpose
Shared US-144MKII PCM setup, sample-rate programming, playback/capture routing, hardware capabilities, and common trigger logic.

## APIs, Types, and Functions
Exports `tascam_pcm_hw`, `process_playback_routing_us144mkii()`, `process_capture_routing_us144mkii()`, `us144mkii_configure_device_for_rate()`, `tascam_pcm_hw_params()`, `tascam_pcm_hw_free()`, `tascam_pcm_trigger()`, and `tascam_init_pcm()`. Internal `fpo_init_pattern()` builds feedback-driven packet-size patterns.

## Control Flow, State, and Persistence
The hardware definition advertises 4-channel `S24_3LE` at 44.1/48/88.2/96 kHz. `hw_params` initializes playback feedback pattern observer state and sends the vendor/UAC control sequence when the requested rate differs from `current_rate`. Routing helpers duplicate or remap channel pairs according to mixer-control state. Trigger start atomically enables both playback and capture, rejects starts while URBs are active, submits feedback, playback, and capture URBs, and increments `active_urbs`. Trigger stop clears active flags and schedules stop work.

## Dependencies and Integration
Depends on USB control transfers, ALSA PCM helpers, playback/capture callback tables, and URBs allocated by the top-level driver. `tascam_init_pcm()` wires playback and capture ops and creates managed DMA buffers.

## Risks and Test Signals
Risks include no rollback reset of active flags on partial start failure, `active_urbs` accounting inconsistencies, rate programming magic register sequence, and capture always following playback start state. Test signals are all supported rates, start failure injection, simultaneous playback/capture, managed-buffer sizing, route changes, and resume reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_pcm.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_pcm.h

## Purpose
Private PCM interface header for US-144MKII, connecting the core driver with playback, capture, routing, and sample-rate code.

## APIs, Types, and Functions
Declares `tascam_pcm_hw`, `tascam_playback_ops`, `tascam_capture_ops`, URB completions `playback_urb_complete()`, `feedback_urb_complete()`, `capture_urb_complete()`, stop/capture work handlers, `tascam_init_pcm()`, `us144mkii_configure_device_for_rate()`, routing helpers, `tascam_pcm_hw_params()`, `tascam_pcm_hw_free()`, and `tascam_pcm_trigger()`.

## Control Flow, State, and Persistence
The header has no runtime behavior. It defines the cross-file callback contract that ALSA PCM registration, USB URB allocation, and interrupt/workqueue code rely on. Its declared functions operate on persistent `struct tascam_card` fields such as substreams, feedback pattern rings, PCM positions, URB anchors, current rate, and routing selections.

## Dependencies and Integration
Includes `us144mkii.h`, so it inherits Linux USB and ALSA types. It is used by the top-level driver, playback/capture implementation files, and shared PCM code.

## Risks and Test Signals
Risks include circular include layering, prototype drift from implementation, and comments promising behavior such as period elapsed handling that is split across feedback and capture paths. Build tests across all US-144MKII objects are the main signal; runtime tests should verify that registered ops match these exported callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_playback.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_playback.c

## Purpose
ALSA PCM playback implementation for US-144MKII plus asynchronous feedback processing that clocks playback and capture period accounting.

## APIs, Types, and Functions
Exports `tascam_playback_ops`, `playback_urb_complete()`, `feedback_urb_complete()`, and `tascam_stop_pcm_work_handler()`. Internal callbacks include `tascam_playback_open()`, `tascam_playback_close()`, `tascam_playback_prepare()`, and `tascam_playback_pointer()`.

## Control Flow, State, and Persistence
Open records the playback substream and installs shared hardware limits. Prepare resets playback counters, feedback indices, sync flags, skip count, and initializes isochronous feedback and playback URB descriptors to nominal packet sizes. Playback completions choose per-packet frame counts from feedback patterns when synced, copy the corresponding ALSA ring-buffer region into the URB, apply software routing in-place, and resubmit. Feedback completions skip initial packets, derive a pattern index from the device feedback byte, write eight frame counts into the feedback ring, detect sync acquisition/loss, advance playback and capture frame counters, emit period elapsed callbacks, and resubmit the feedback URB.

## Dependencies and Integration
Depends on USB isochronous URBs, ALSA PCM period accounting, shared pattern state initialized by `tascam_pcm_hw_params()`, and stop work used for fatal feedback-sync loss.

## Risks and Test Signals
Risks include using only one feedback byte, assuming eight packets per pattern, subtle ring-index sync detection, `break` inside scoped guard blocks, active-URB count decrements only on some failures, and period accounting based on feedback rather than actual capture decode. Test signals are stable long playback at each rate, feedback-loss injection, period timing drift checks, underrun/xrun handling, route changes, and capture/playback synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_playback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.c

## Purpose
Hardware-dependent ALSA interface for older TASCAM US-X2Y devices. It handles user-space firmware/FPGA loading and exposes shared control memory for US-428 surface controls and lights.

## APIs, Types, and Functions
Exports `usx2y_hwdep_new()`. Important internals are `snd_usx2y_hwdep_dsp_status()`, `snd_usx2y_hwdep_dsp_load()`, `snd_us428ctls_mmap()`, `snd_us428ctls_poll()`, `snd_us428ctls_vm_fault()`, `usx2y_create_usbmidi()`, and `usx2y_create_alsa_devices()`.

## Control Flow, State, and Persistence
`usx2y_hwdep_new()` creates an exclusive hwdep device, attaches DSP status/load, mmap, and poll callbacks, names it after the USB bus path, and allocates `us428ctls_sharedmem`. DSP status reports type, two DSP images, driver version, and readiness. DSP load copies user firmware, sets interface 0 altsetting 1, bulk-sends the image to endpoint 2, and after image index 1 initializes async/control URBs, MIDI, audio, hwdep PCM, registers the card, and marks `USX2Y_STAT_CHIP_INIT`. Mmap faults map pages from the control shared memory; poll signals changed control snapshots or hangup.

## Dependencies and Integration
Depends on ALSA hwdep, USB bulk transfers, snd-usbmidi, US-X2Y audio creation, async pipe-4 setup, and `usbus428ctldefs.h` shared-memory layout.

## Risks and Test Signals
Risks include firmware image trust/size, shared hwdep for firmware and control mmap, mmap size validation comparing bytes to page-aligned size, card registration after staged firmware load, and userspace ABI expectations. Test signals are firmware loader operation, poll/mmap control-surface updates, card creation after DSP image 1, and disconnect during open hwdep mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.h

## Purpose
Tiny private header declaring the US-X2Y hwdep creation entry point.

## APIs, Types, and Functions
Declares `int usx2y_hwdep_new(struct snd_card *card, struct usb_device *device);`.

## Control Flow, State, and Persistence
No runtime state or control flow. The declaration allows `usbusx2y.c` to create the firmware/control hwdep device during probe before firmware has initialized the full ALSA device stack.

## Dependencies and Integration
Relies on forward-visible ALSA `struct snd_card` and USB `struct usb_device` types from including source files. Implemented by `usX2Yhwdep.c`.

## Risks and Test Signals
Risk is limited to prototype drift or missing includes in consumers. Build coverage of `usbusx2y.c` and successful hwdep creation during probe validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.c

## Purpose
Generic low-latency full-duplex USB isochronous streaming helper used by US-X2Y-style mmap/raw USB paths. It allocates shared read/write buffers, packet metadata, URBs, and synchronizes input and output isochronous completions.

## APIs, Types, and Functions
Exports `usb_stream_new()`, `usb_stream_free()`, `usb_stream_start()`, and `usb_stream_stop()`. Key internals include packet-size calculation (`usb_stream_next_packet_size()`, `playback_prep_freqn()`), URB setup (`init_urbs()`), startup/idle completion pairs, `stream_start()`, `stream_idle()`, `usb_stream_prepare_playback()`, and `submit_urbs()`.

## Control Flow, State, and Persistence
Allocation computes packets per period from rate and USB frame rate, allocates one `struct usb_stream` read area with packet descriptors and one write area, initializes four IN and four OUT URBs, and stores rate in Q16.16-style `freqn`. Start submits paired IN/OUT URBs on matching start frames, retries if frames differ, waits for sync states to reach ready, then switches callbacks to idle mode. Completion balancing waits until matching capture/playback URBs have completed, records input packet offsets in shared memory, prepares output packet descriptors either from captured packet lengths or nominal frequency, submits the next pair, increments `periods_done`, and wakes waiters.

## Dependencies and Integration
Depends on USB isochronous APIs and UAPI `sound/usb_stream.h` shared structures that userspace can mmap/read. It is independent of ALSA PCM ops but designed for audio period transport.

## Risks and Test Signals
Risks include fragile sync heuristics, fixed `USB_STREAM_NURBS`/depth assumptions, read/write allocation limits, start-frame retry timing, xrun state on zero-length/status packets, and shared-memory ABI compatibility. Test signals are start/stop at full/high speed, period wakeups, mmap clients reading packet tables, underrun injection, and long-running drift checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.h

## Purpose
Kernel-private interface for the USB stream helper, defining stream URB counts, kernel-side state, and lifecycle functions.

## APIs, Types, and Functions
Defines `USB_STREAM_NURBS` and `USB_STREAM_URBDEPTH`, `struct usb_stream_kernel`, and prototypes for `usb_stream_new()`, `usb_stream_free()`, `usb_stream_start()`, and `usb_stream_stop()`.

## Control Flow, State, and Persistence
The header contains no logic, but `struct usb_stream_kernel` persists the bridge between shared `struct usb_stream` memory, USB device, read/write URBs, idle/completed URB pointers, synchronization balance, wait queue, output phase accumulator, and normalized frequency.

## Dependencies and Integration
Includes `<uapi/sound/usb_stream.h>` for the userspace-visible stream layout. Implemented by `usb_stream.c` and expected to be embedded by device-specific code that owns the USB device and endpoints.

## Risks and Test Signals
Risks include ABI coupling to UAPI structures, assumptions that four URBs and depth four are enough for all supported devices, and state fields being updated from interrupt context. Build coverage plus stress tests around stream start/stop, wait queue wakeups, and high/full-speed rates validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbus428ctldefs.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbus428ctldefs.h

## Purpose
Defines US-428 control-surface data structures shared between the kernel driver and userspace via hwdep mmap.

## APIs, Types, and Functions
Defines control indices (`enum E_IN84`), transport button masks, `struct us428_ctls`, output update structures `us428_set_byte`, `usx2y_volume`, `us428_lights`, `us428_p4out`, buffer counts, and `struct us428ctls_sharedmem`. `US428_SHAREDMEM_PAGES` is the page-aligned mmap allocation size.

## Control Flow, State, and Persistence
No executable flow. Persistent shared state records a ring of control snapshots, the byte offset that differed, reader/writer cursors, a ring of pending pipe-4 output commands, and output sent/last cursors. The interrupt pipe-4 handler in `usbusx2y.c` writes snapshots and drains light/volume output requests.

## Dependencies and Integration
Used by `usX2Yhwdep.c` for mmap/poll sizing and by `usbusx2y.c` for interrupt-pipe control updates. It depends on `PAGE_ALIGN` from kernel headers via including source context.

## Risks and Test Signals
Risks include packed layout assumptions without explicit packing, signed cursor sentinel values in shared memory, loss of output commands when multiple p4out entries arrive, and userspace ABI rigidity. Test signals are US-428 fader/button updates, light/volume writes, wraparound of both rings, and mmap size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbus428ctldefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.c

## Purpose
Main USB driver for older TASCAM US-X2Y devices (US-122, US-224, US-428). It creates the initial ALSA card and hwdep loader, manages interrupt/bulk pipe 4 control traffic, and handles hotplug cleanup.

## APIs, Types, and Functions
Registers `snd_usx2y_usb_driver`. Exports `usx2y_async_seq04_init()` and `usx2y_in04_init()`. Important internals are `snd_usx2y_probe()`, `snd_usx2y_disconnect()`, `usx2y_create_card()`, `snd_usx2y_card_private_free()`, `i_usx2y_in04_int()`, `i_usx2y_out04_int()`, and `usx2y_unlinkseq()`.

## Control Flow, State, and Persistence
Probe validates vendor/product IDs, creates a card with `struct usx2ydev` private data, initializes wait queues, mutex, MIDI list, and card strings, then creates the hwdep loader and registers the card. The real audio/MIDI device stack is created later after firmware load. Pipe-4 input interrupt completions detect changed 21-byte control snapshots, publish them to `us428ctls_sharedmem`, wake pollers, submit queued async output URBs for sample-rate/control sequences or light/volume requests, and resubmit the IN interrupt URB. Disconnect marks hangup, kills async/control URBs, disconnects MIDI children, wakes pollers, and frees when closed.

## Dependencies and Integration
Depends on USB core, ALSA card/rawmidi, `usX2Yhwdep.c` firmware loader, `usbusx2yaudio.c`, and shared control definitions.

## Risks and Test Signals
Risks include staged initialization complexity, pipe-4 output loss noted by FIXME, `dev_set_drvdata()` versus `usb_get_intfdata()` expectations, firmware timing, and hot-unplug while hwdep mmap is active. Test signals are probe for all three product IDs, firmware load, interrupt-control snapshots, p4out light/volume commands, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.h

## Purpose
Private US-X2Y driver header defining URB counts, runtime state structures, module packet-count policy, and cross-file declarations for card/audio/control code.

## APIs, Types, and Functions
Defines `NRURBS`, default and maximum packet counts, optional `nrpacks`, async sequence constants, `struct snd_usx2y_async_seq`, `struct snd_usx2y_urb_seq`, `struct usx2ydev`, and `struct snd_usx2y_substream`. Declares `usx2y_audio_create()`, `usx2y_async_seq04_init()`, `usx2y_in04_init()`, and macro `usx2y(card)`.

## Control Flow, State, and Persistence
No executable logic, but it defines persistent card state used across firmware loading, audio PCM, hwdep PCM, pipe-4 control, and MIDI. `usx2ydev` keeps USB device, card index, stride, control URBs, async sequences, rate/format, chip status, PCM mutex, shared memories, substreams, prepare synchronization, and MIDI list. Substreams track endpoint, state machine, ring pointers, URBs, and playback temp buffer.

## Dependencies and Integration
Includes USB-audio and MIDI headers, US-428 control definitions, and hwdep PCM definitions. Used by all older US-X2Y implementation files.

## Risks and Test Signals
Risks include heavy shared mutable state, volatile/atomic state-machine expectations, compile-time inclusion of hwdep PCM interfaces, and `nrpacks` behavior changing available modes. Test signals include build coverage with `USX2Y_NRPACKS_VARIABLE`, normal PCM and hwdep PCM operation, rate/format consistency checks, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2yaudio.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2yaudio.c

## Purpose
Normal ALSA PCM implementation for older US-X2Y devices. It manages full-duplex synchronized isochronous capture/playback, sample-rate programming, format altsettings, PCM device creation, and period accounting.

## APIs, Types, and Functions
Exports `usx2y_audio_create()` and provides reusable helpers later included by `usx2yhwdeppcm.c`. Key functions are `usx2y_urb_capt_retire()`, `usx2y_urb_play_prepare()`, `usx2y_urb_play_retire()`, `usx2y_urb_submit()`, `usx2y_usbframe_complete()`, `i_usx2y_urb_complete()`, `usx2y_urbs_allocate()`, `usx2y_urbs_start()`, `snd_usx2y_pcm_prepare()`, `snd_usx2y_pcm_trigger()`, `usx2y_rate_set()`, and `usx2y_format_set()`.

## Control Flow, State, and Persistence
Open rejects normal PCM while mmap hwdep mode is active, installs 2-channel S16/S24 hardware constraints, and records runtime private data. `hw_params` enforces one rate/format across all substreams. Prepare resets substream pointers, changes USB altsetting for format, sends pipe-4 sample-rate command sequences, starts capture first for sync, then playback. URB completions pair capture and playback by USB frame; capture actual packet lengths drive playback packet lengths. Retire paths copy capture data into ALSA buffers and advance period counters; playback copies from ALSA or temp buffer around wrap.

## Dependencies and Integration
Depends on ALSA PCM, USB isochronous APIs, pipe-4 control from `usbusx2y.c`, snd-usbmidi input stop/start during altsetting changes, and shared `usx2ydev` state.

## Risks and Test Signals
Risks include strict packet-size range 43-50, synchronization state complexity, inclusion by hwdep PCM source, rate magic tables only for 44.1/48 kHz, MIDI interruption during altsetting, and error paths stopping all clients. Test signals are duplex playback/capture, US-428 second capture PCM, S16/S24 formats, rate switching, xrun behavior, and hot-unplug during active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2yaudio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2y.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2y.h

## Purpose
Common constants for older TASCAM US-X2Y devices: driver version, hwdep IDs, hardware type IDs, USB product IDs, and chip-status flags.

## APIs, Types, and Functions
Defines `USX2Y_DRIVER_VERSION`, hwdep ID strings `SND_USX2Y_LOADER_ID` and `SND_USX2Y_USBPCM_ID`, type enum values for US-122/US-224/US-428, product IDs, and status flags `USX2Y_STAT_CHIP_INIT`, `USX2Y_STAT_CHIP_MMAP_PCM_URBS`, and `USX2Y_STAT_CHIP_HUP`.

## Control Flow, State, and Persistence
No runtime flow. These constants shape card identity, firmware-loader status reporting, PCM mode selection, and disconnect/hangup behavior across the US-X2Y driver.

## Dependencies and Integration
Included by `usbusx2y.c`, `usX2Yhwdep.c`, and audio/hwdep PCM code. It is the small shared identity/status contract for the legacy driver.

## Risks and Test Signals
Risks are ABI/name stability for hwdep IDs and status-bit meaning. Test signals are correct product classification, hwdep userspace discovering expected IDs, normal versus mmap PCM mode switching, and hangup behavior after disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2y.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.c

## Purpose
Alternative "rawusb" hwdep PCM path for US-X2Y devices, optimized for mmaped low-latency JACK operation by sharing USB DMA buffers and isochronous packet metadata with userspace.

## APIs, Types, and Functions
Exports `usx2y_hwdep_pcm_new()` when packet count is one or variable. It includes `usbusx2yaudio.c` to reuse normal PCM helpers. Important functions include `usx2y_usbpcm_urb_capt_retire()`, `usx2y_hwdep_urb_play_prepare()`, `usx2y_usbpcm_urb_capt_iso_advance()`, `usx2y_usbpcm_usbframe_complete()`, `i_usx2y_usbpcm_urb_complete()`, `usx2y_usbpcm_urbs_allocate()`, `snd_usx2y_usbpcm_prepare()`, `snd_usx2y_usbpcm_open()`, hwdep open/release/mmap callbacks, and page-fault mapping.

## Control Flow, State, and Persistence
Opening the hwdep PCM device sets `USX2Y_STAT_CHIP_MMAP_PCM_URBS` if normal PCMs are idle. The PCM open path is only available in that mode. Prepare allocates `hwdep_pcm_shm`, sets rate/format, starts capture, waits until enough captured isochronous frames exist, then starts playback. Capture URBs write directly into shared capture areas and record packet frame/offset/length rings. Playback URBs use captured packet lengths and shared playback buffer offsets, zeroing when not running. Mmap exposes `snd_usx2y_hwdep_pcm_shm` pages to userspace.

## Dependencies and Integration
Depends on ALSA hwdep/PCM, USB isochronous APIs, shared US-X2Y PCM helpers, and `usx2yhwdeppcm.h` shared-memory layout. Created after firmware load by `usX2Yhwdep.c`.

## Risks and Test Signals
Risks include source-level inclusion of another `.c` file, duplicate call to `usx2y_hwdep_urb_play_prepare()`, volatile shared-memory cursors, mmap lifetime, single-packet-mode gating, and tight coupling with JACK userspace. Test signals are hwdep open exclusivity, mmap size/faults, low-latency playback/capture, 4-channel capture on US-428, and switching back to normal PCM after release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.h

## Purpose
Shared-memory layout and creation prototype for US-X2Y hwdep mmap PCM mode.

## APIs, Types, and Functions
Defines `MAXPACK`, `MAXBUFFERMS`, `MAXSTRIDE`, derived shared-section size `SSS`, `struct snd_usx2y_hwdep_pcm_shm`, and `usx2y_hwdep_pcm_new()`.

## Control Flow, State, and Persistence
No executable logic. The shared memory persists three audio buffers (`playback`, `capture0x8`, `capture0xA`), playback/capture isochronous cursor state, an array of 128 captured iso descriptors with frame/offset/length, and counters used by kernel and userspace to synchronize raw USB PCM movement.

## Dependencies and Integration
Included by `usbusx2y.h` and implemented/used by `usx2yhwdeppcm.c`. The layout is exposed through ALSA hwdep mmap and is therefore an ABI with userspace drivers.

## Risks and Test Signals
Risks include volatile fields used as synchronization, no explicit versioning in the shared layout, fixed buffer sizing, and offset arithmetic matching URB descriptor advancement. Test signals are mmap clients reading/writing expected buffers, wraparound of captured iso descriptors, and low-latency JACK workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/validate.c -->
# sources/distributed-fs/ceph-client/sound/usb/validate.c

## Purpose
Validation layer for USB audio and MIDI class-specific descriptors, preventing parsers from reading malformed descriptor bodies unless the global skip-validation quirk is enabled.

## APIs, Types, and Functions
Exports `snd_usb_validate_audio_desc()` and `snd_usb_validate_midi_desc()`. Internal validator functions cover UAC1 headers, mixer units, processing/extension units, selector units, UAC1/2/3 feature units, UAC3 power domains, and MIDI out jacks. Static tables `audio_validators` and `midi_validators` map protocol/type pairs to fixed-size or function checks.

## Control Flow, State, and Persistence
`validate_desc()` ignores non-class-interface descriptors, finds a matching validator by subtype and protocol, then applies either a fixed minimum length or a protocol-aware length calculation. Public functions dump invalid bytes and accept them only when `snd_usb_skip_validation` is set. There is no persistent state beyond static validator tables.

## Dependencies and Integration
Depends on USB audio v1/v2/v3 and MIDI descriptor definitions, ALSA USB-audio module options from `usbaudio.h`, and `print_hex_dump()` for diagnostics. Descriptor parsers call this before consuming variable-length fields.

## Risks and Test Signals
Risks include incomplete validation for some unimplemented descriptor types, complex variable-length calculations based on untrusted fields, accepting unknown subtypes by default, and skip-validation masking real bugs. Test signals are fuzzed descriptors, known quirky devices with skip enabled, UAC1/2/3 mixer/selector/processing descriptors, MIDI jack descriptors, and parser KASAN/UBSAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/validate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/Kconfig -->
# sources/distributed-fs/ceph-client/sound/virtio/Kconfig

## Purpose
Kconfig entry for enabling the virtio sound driver.

## APIs, Types, and Functions
Defines `config SND_VIRTIO` as a tristate option named "Virtio sound driver". It depends on `VIRTIO` and selects `SND_PCM` and `SND_JACK`.

## Control Flow, State, and Persistence
No runtime behavior. The option controls whether the virtio-snd module or built-in object is compiled and ensures required ALSA PCM and jack infrastructure is present.

## Dependencies and Integration
Integrated into the kernel sound Kconfig tree. The corresponding Makefile builds `virtio_snd.o` when `CONFIG_SND_VIRTIO` is enabled.

## Risks and Test Signals
Risks are limited to missing dependencies, especially if future features require controls or channel-map helpers not selected here. Test signals are Kconfig menu visibility, all three build modes (`n`, `m`, `y`), and module autoloading for virtio sound devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/Makefile -->
# sources/distributed-fs/ceph-client/sound/virtio/Makefile

## Purpose
Build recipe for the virtio sound ALSA driver.

## APIs, Types, and Functions
Defines `obj-$(CONFIG_SND_VIRTIO) += virtio_snd.o` and composes `virtio_snd-y` from card, channel-map, control-message, jack, kcontrol, PCM, PCM-message, and PCM-ops objects.

## Control Flow, State, and Persistence
No runtime behavior. It controls object aggregation so all helper modules are linked into one driver object.

## Dependencies and Integration
Depends on Kbuild and the `SND_VIRTIO` Kconfig option. The files listed here provide the symbols referenced by `virtio_card.c` and each other.

## Risks and Test Signals
Risks include omitting a new helper object, stale object names after file renames, or link failures when optional features are not consistently compiled. Test signals are module and built-in builds with `CONFIG_SND_VIRTIO`, link-time symbol resolution, and modpost output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_card.c

## Purpose
Core virtio-snd device driver: validates the virtio device, creates virtqueues, builds ALSA devices from virtio configuration, dispatches async events, and handles remove/suspend/resume.

## APIs, Types, and Functions
Registers `virtsnd_driver` via `module_virtio_driver()`. Important functions are `virtsnd_validate()`, `virtsnd_probe()`, `virtsnd_remove()`, `virtsnd_find_vqs()`, `virtsnd_build_devs()`, event queue helpers, `virtsnd_event_dispatch()`, and PM callbacks `virtsnd_freeze()`/`virtsnd_restore()`.

## Control Flow, State, and Persistence
Probe allocates `struct virtio_snd`, initializes pending-message and PCM lists plus queue locks, finds four virtqueues, populates event buffers, marks the device ready, parses config for jacks, PCMs, channel maps, and optional controls, builds ALSA devices, registers the card, then enables the event queue. Events are recycled back to the event queue after dispatch to jack, PCM, or kcontrol handlers. Remove/freeze disable events, cancel control messages, delete vqs, reset the device, cancel period work, free PCM messages, and release event messages.

## Dependencies and Integration
Depends on virtio core/config APIs, ALSA card APIs, virtio-snd UAPI, and helper files for PCM, jack, channel-map, kcontrol, and control-message management.

## Risks and Test Signals
Risks include failure cleanup after partial parsing/building, event delivery during teardown, timeout module parameter validation, optional controls feature negotiation, and restore not rebuilding ALSA config. Test signals are virtio feature negotiation, card creation, event storms, suspend/resume, remove during pending control messages, and PCM/jack/control configuration permutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.h -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_card.h

## Purpose
Central private header for virtio-snd, defining the card state, queue wrappers, dynamic control state, queue accessors, and helper prototypes.

## APIs, Types, and Functions
Defines card/PCM names, `struct virtio_snd_queue`, `struct virtio_kctl`, and `struct virtio_snd`. Inline helpers return control, event, TX, RX, and PCM-direction queues. Prototypes cover jack, channel-map, and kcontrol parse/build/event functions, and exposes `virtsnd_msg_timeout_ms`.

## Control Flow, State, and Persistence
No executable runtime flow except inline queue selection. `struct virtio_snd` persists the virtio device, four virtqueue wrappers, ALSA card, pending control-message list, event buffers, PCM list, jack array, substream array, channel maps, control metadata, and built controls.

## Dependencies and Integration
Includes virtio, ALSA core, virtio-snd UAPI, `virtio_ctl_msg.h`, and `virtio_pcm.h`. It is included by all virtio-snd helper files.

## Risks and Test Signals
Risks include shared state lifetime across devm-managed arrays and manual frees, queue-selection correctness for playback/capture, and helper prototype drift. Test signals are full-driver builds, probe/remove lifecycle tests, and exercising each helper through config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_chmap.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_chmap.c

## Purpose
Parses virtio channel-map configuration and exposes it as ALSA PCM channel-map controls.

## APIs, Types, and Functions
Exports `virtsnd_chmap_parse_cfg()` and `virtsnd_chmap_build_devs()`. Internal data includes `g_v2a_position_map` converting virtio channel positions to ALSA `SNDRV_CHMAP_*`, and helper `virtsnd_chmap_add_ctls()`.

## Control Flow, State, and Persistence
Parse reads the device `chmaps` count, allocates `snd->chmaps`, queries `VIRTIO_SND_R_CHMAP_INFO`, finds or creates the owning `virtio_pcm` by HDA function node ID, and increments per-stream channel-map counts by direction. Build allocates per-stream `snd_pcm_chmap_elem` arrays, repopulates them from raw virtio map info, clamps channel count to ALSA map capacity, translates positions, then adds ALSA channel-map controls to built PCMs.

## Dependencies and Integration
Depends on virtio config reads, control queries, PCM registry helpers `virtsnd_pcm_find_or_create()`/`virtsnd_pcm_find()`, and ALSA `snd_pcm_add_chmap_ctls()`.

## Risks and Test Signals
Risks include invalid directions, out-of-range position IDs, channel count truncation, channel-map info referencing PCM NIDs that were not otherwise configured, and build ordering requiring PCMs to exist before controls are added. Test signals are playback/capture chmaps for different channel counts, malformed position IDs, devices with no PCM for a chmap, and `alsactl`/`amixer` visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_chmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.c

## Purpose
Virtio-snd synchronous/asynchronous control-message transport over the control virtqueue, including allocation, lifetime management, completion, cancellation, and configuration queries.

## APIs, Types, and Functions
Defines private `struct virtio_snd_msg`. Exports `virtsnd_ctl_msg_ref()`, `virtsnd_ctl_msg_unref()`, request/response accessors, `virtsnd_ctl_msg_alloc()`, `virtsnd_ctl_msg_send()`, `virtsnd_ctl_msg_complete()`, `virtsnd_ctl_msg_cancel_all()`, `virtsnd_ctl_query_info()`, and `virtsnd_ctl_notify_cb()`.

## Control Flow, State, and Persistence
Allocation stores request and response payloads after the message header and initializes scatterlists, completion, list node, and refcount. Send sets default response to IO error, assembles up to four sg entries, adds the message to the control virtqueue under queue lock, records it in `snd->ctl_msgs`, notifies the device, and optionally waits for completion with `virtsnd_msg_timeout_ms`. Completion removes the list entry, completes waiters, and drops the queue-owned reference. Cancellation drains pending messages and completes them with the default error. Query-info sends a standard `virtio_snd_query_info` request with an inbound data sg.

## Dependencies and Integration
Depends on virtqueue scatter-gather APIs, completions, refcounting, module parameter timeout from `virtio_card.c`, and all parsers/control callbacks that issue virtio requests.

## Risks and Test Signals
Risks include timeout races where late device completion may touch still-pending messages, default cancellation status semantics, nowait lifetime expectations, and interrupt callback lock ordering. Test signals are query-info paths, concurrent controls, timeout/cancel injection, remove with pending messages, and response status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.h -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.h

## Purpose
Private virtio-snd control-message API declaration shared by card, config parser, PCM, and kcontrol code.

## APIs, Types, and Functions
Forward-declares `struct virtio_snd` and `struct virtio_snd_msg`; declares ref/unref, request/response accessors, allocation, generic send, sync/async inline send wrappers, cancellation, completion, query-info, and control-virtqueue notification callback.

## Control Flow, State, and Persistence
The header has no state. The sync wrapper sends without extra scatterlists and waits; the async wrapper sends without waiting. Callers must honor the documented ownership rule that messages are normally freed when the final reference drops after completion.

## Dependencies and Integration
Includes Linux atomic and virtio types. Implemented by `virtio_ctl_msg.c` and included by `virtio_card.h`, making it visible throughout the virtio-snd driver.

## Risks and Test Signals
Risks include callers retaining message payloads without taking a reference, using sync sends from atomic context, or expecting async messages to outlive completion. Build coverage and runtime tests of parser queries, control reads/writes, and teardown cancellation validate this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_jack.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_jack.c

## Purpose
Virtio-snd jack detection support. It parses virtio jack configuration, builds ALSA jack controls, labels them from HDA pin default configuration, and handles connected/disconnected events.

## APIs, Types, and Functions
Exports `virtsnd_jack_parse_cfg()`, `virtsnd_jack_build_devs()`, and `virtsnd_jack_event()`. Internal `struct virtio_jack` persists ALSA jack pointer, HDA node ID, feature bits, pin defaults/caps, current connection state, and ALSA jack type. Helpers `virtsnd_jack_get_label()` and `virtsnd_jack_get_type()` map HDA device/location fields to strings and `SND_JACK_*` bits.

## Control Flow, State, and Persistence
Parse reads jack count, allocates `snd->jacks`, queries `VIRTIO_SND_R_JACK_INFO`, and copies endian-converted fields into persistent jack entries. Build creates one ALSA jack per entry and reports initial state. Events validate the jack ID, update the `connected` boolean for connect/disconnect event codes, and call `snd_jack_report()`.

## Dependencies and Integration
Depends on virtio config/control query APIs, ALSA jack layer, HDA verb/default-configuration constants, and event dispatch in `virtio_card.c`.

## Risks and Test Signals
Risks include simplified implementation with no jack remap support, generic labels for unknown HDA defaults, event IDs outside range being silently ignored, and `snd_jack_report()` from interrupt context assumptions. Test signals are initial jack state, connect/disconnect events, HDMI/SPDIF/headphone/mic label mapping, and devices with zero jacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_jack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_kctl.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_kctl.c

## Purpose
Dynamic ALSA mixer-control bridge for virtio-snd. It parses virtio control metadata, creates ALSA kcontrols, translates get/put/TLV operations into virtio control messages, and dispatches control-change events.

## APIs, Types, and Functions
Exports `virtsnd_kctl_parse_cfg()`, `virtsnd_kctl_build_devs()`, and `virtsnd_kctl_event()`. Static maps translate virtio types, access flags, and event masks to ALSA values. Important callbacks are `virtsnd_kctl_info()`, `virtsnd_kctl_get()`, `virtsnd_kctl_put()`, `virtsnd_kctl_tlv_op()`, and `virtsnd_kctl_get_enum_items()`.

## Control Flow, State, and Persistence
Parse runs only when the controls feature is negotiated, reads the control count, allocates metadata and runtime arrays, queries `VIRTIO_SND_R_CTL_INFO`, and for enumerated controls queries item strings. Build constructs `snd_kcontrol_new` records from virtio names, indices, access masks, TLV flags, callbacks, and private control IDs, then adds them to the ALSA card. Get/put allocate virtio messages, convert values by type/endian, and synchronously send read/write requests. TLV read/write/command uses separate user-copy buffers and scatterlists. Events translate virtio masks and notify ALSA for the affected control ID.

## Dependencies and Integration
Depends on ALSA control APIs, virtio control-message transport, virtio-snd UAPI control structs, and event dispatch in `virtio_card.c`.

## Risks and Test Signals
Risks include no explicit bounds checks against ALSA value array capacities for large `count`, type/access map indexing from device-provided values, TLV size trust and allocation pressure, event mask translation, and lifetime of devm item arrays. Test signals are boolean/int/int64/enum/bytes/IEC958 controls, TLV read/write/cmd, invalid metadata fuzzing, control notifications, and timeout/error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_kctl.c -->
