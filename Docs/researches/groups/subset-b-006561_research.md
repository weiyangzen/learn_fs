# subset-b-006561 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/playback.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/playback.c

## Purpose
`playback.c` implements the Line 6 USB driver's ALSA playback side: it allocates isochronous output URBs, fills them from the ALSA ring buffer, applies optional software playback volume, mixes software monitor/capture feedback when hardware monitoring is unavailable, and resubmits URBs from completion callbacks. It is tightly coupled to `struct snd_line6_pcm` from the Line 6 PCM core.

## Important APIs, Types, And Functions
The externally used functions are `line6_create_audio_out_urbs()` and `line6_submit_audio_out_all_urbs()`, plus the exported `snd_line6_playback_ops` PCM callback table. Internal helpers include `submit_audio_out_urb()`, `audio_out_callback()`, `change_volume()`, `create_impulse_test_signal()`, and `add_monitor_signal()`. The code operates on `line6pcm->out` stream state, `line6pcm->volume_playback`, `line6pcm->volume_monitor`, `line6pcm->prev_fbuf`, and `line6pcm->prev_fsize`.

## Control Flow And State
`line6_create_audio_out_urbs()` allocates `line6->iso_buffers` URBs, binds them to the device audio-out endpoint, sets `URB_ISO_ASAP`, one or more iso packet descriptors, interval, and `audio_out_callback()`. `line6_submit_audio_out_all_urbs()` repeatedly calls `submit_audio_out_urb()` while holding the output lock in the caller.

`submit_audio_out_urb()` finds an inactive URB bit, computes packet sizes from the device rate numerator/denominator and `intervals_per_second`, copies playback frames from the ALSA DMA ring with wraparound handling, then advances `out.pos`. If PCM playback is not running or playback is paused, it sends silence. It then takes the input lock, consumes `prev_fbuf`/`prev_fsize` from the capture side, optionally creates an impulse-test stream or mixes the captured signal into playback for software monitoring, clears the previous capture buffer pointer, submits the URB, and marks the active bit on success.

`audio_out_callback()` maps the completed URB back to its array index, updates `out.pos_done`, clears the active bit, detects shutdown from iso `-EXDEV` or explicit unlink bits, and resubmits another URB unless shutdown is requested. When enough playback bytes accumulate to cross `out.period`, it calls `snd_pcm_period_elapsed()` outside the spinlock.

## State And Persistence
There is no persistent storage. Runtime state lives in bitmaps (`active_urbs`, `unlink_urbs`, `running`), ALSA ring positions (`out.pos`, `out.pos_done`), byte counters (`out.bytes`, `out.period`, `out.count`), and temporary capture feedback (`prev_fbuf`, `prev_fsize`). Impulse test state is maintained in `impulse_count`, `impulse_period`, and `impulse_volume`.

## Dependencies And Integration Points
This file depends on ALSA PCM callbacks, USB isochronous URBs, Line 6 PCM helpers (`snd_line6_hw_params()`, `snd_line6_prepare()`, `snd_line6_trigger()`, `snd_line6_pointer()`), capture helpers (`line6_capture_copy()`, `line6_capture_check_period()`), and Line 6 device properties such as endpoint numbers, capabilities, sample size, channel count, and supported rates.

## Risks And Edge Cases
URB size calculation assumes `LINE6_ISO_PACKETS == 1` despite looping over packets. Incorrect rate factors, zero URB size, or mismatched frame sizes can break scheduling. `submit_audio_out_urb()` logs submit failures but returns zero, so callers cannot always distinguish a failed USB submission. Software volume handles only 16-bit stereo and packed 24-bit stereo frames. Software monitoring is intentionally skipped for 6-byte frames because those devices are assumed to have hardware monitoring. The capture feedback pointer is consumed under the input lock, so misuse by capture-side code could drop monitor data.

## Test Signals
Useful tests include playback open constraint negotiation, URB allocation against valid/invalid endpoints, ring-buffer wrap copies, period elapsed cadence, pause/silence behavior, volume clamp behavior for 16-bit and 24-bit samples, monitor mixing when `LINE6_CAP_HWMON` is absent, impulse stream capture loopback, URB unlink/shutdown paths, and no-free-URB handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/playback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/playback.h -->
# sources/distributed-fs/ceph-client/sound/usb/line6/playback.h

## Purpose
`playback.h` is the Line 6 playback interface header. It declares the playback PCM operation table and the two output-URB management functions used by the Line 6 PCM core.

## Important APIs, Types, And Macros
The header exposes `snd_line6_playback_ops`, `line6_create_audio_out_urbs()`, and `line6_submit_audio_out_all_urbs()`. It includes ALSA PCM definitions and `driver.h` for `struct snd_line6_pcm`. `USE_CLEAR_BUFFER_WORKAROUND` enables a TonePort full-duplex monitor workaround that clears transfer buffers in the playback completion path.

## Control Flow And State
No runtime control flow is implemented here. The declarations allow the PCM setup code to install playback callbacks and create/submit output URBs. The workaround macro is compile-time state that changes the behavior of `audio_out_callback()` in `playback.c`.

## State And Persistence
There is no persistent state. The main state implication is the global compile-time workaround for output buffer clearing, motivated by TonePort jack full-duplex noise when software monitoring repeats stale output data.

## Dependencies And Integration Points
This header is consumed by Line 6 PCM and device drivers that need playback operations. It depends on ALSA PCM declarations and the Line 6 driver structures.

## Risks And Edge Cases
The workaround is broad: enabling it affects every playback URB completion compiled with this header, not only the TonePort scenario described in the comment. Changing it can alter software-monitor behavior and stale-buffer exposure.

## Test Signals
Build coverage should confirm all Line 6 playback users see the declarations. Runtime regression tests should focus on TonePort full-duplex monitoring with the workaround enabled and disabled, plus playback on devices that do not need software monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/playback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/pod.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/pod.c

## Purpose
`pod.c` is the USB driver for older Line 6 POD-family devices. It registers supported USB IDs, defines device capabilities and endpoints, initializes PCM and control/MIDI support through the common Line 6 core, exposes POD sysfs metadata, parses firmware/system messages, and provides an ALSA mixer control for hardware monitor playback volume.

## Important APIs, Types, And Functions
The main private type is `struct usb_line6_pod`, which embeds `struct usb_line6` and stores `monitor_level`, `startup_progress`, `serial_number`, `firmware_version`, and `device_id`. The USB entry point is `pod_probe()`, which delegates to `line6_probe()`. Initialization is in `pod_init()`. Message handling is in `line6_pod_process_message()`. Startup sequencing is in `pod_startup()`. Mixer callbacks are `snd_pod_control_monitor_info()`, `snd_pod_control_monitor_get()`, and `snd_pod_control_monitor_put()`. Sysfs attributes are `device_id`, `firmware_version`, and `serial_number`.

## Control Flow And State
During probe, `line6_probe()` allocates the device object and calls `pod_init()`. `pod_init()` installs `process_message` and `startup` callbacks, adds the `pod` sysfs attribute group, initializes PCM with fixed 24-bit packed stereo parameters near 39.0625 kHz, and registers the monitor control. For control-capable devices it initializes `monitor_level` to `POD_SYSTEM_INVALID` and schedules delayed startup.

Startup begins with `POD_STARTUP_VERSIONREQ`, sends an async version request, and waits for `line6_pod_process_message()` to parse the identity response. The message parser recognizes the universal version header, fills firmware version and device ID from fixed offsets, advances startup to setup, and schedules startup work immediately. Setup reads the serial number and registers the ALSA card. System sysex messages for `POD_MONITOR_LEVEL` update cached monitor state. Mixer writes call `pod_set_system_param_int()`, which builds a Line 6 sysex system message with a 16-bit nibble-encoded value.

## State And Persistence
All state is volatile. The device itself persists monitor and firmware state; the driver caches monitor level, firmware version, serial number, and device ID. ALSA card registration is deliberately delayed until after version/setup to avoid PODxt Live device errors.

## Dependencies And Integration Points
The driver integrates with `line6_probe()`, `line6_disconnect()`, PM callbacks, Line 6 sysex helpers, `line6_init_pcm()`, ALSA controls, and ALSA card sysfs device attributes. Device capabilities include combinations of `LINE6_CAP_CONTROL`, `LINE6_CAP_CONTROL_MIDI`, `LINE6_CAP_PCM`, and `LINE6_CAP_HWMON`.

## Risks And Edge Cases
Message parsing uses fixed offsets in firmware responses and sysex payloads, so malformed or short messages could be hazardous if the common message layer does not validate length. Mixer put updates local state before confirming USB delivery. Card registration errors are logged but not propagated from startup work. Devices without `LINE6_CAP_CONTROL` do not run the delayed startup path here, so registration behavior relies on the common probe flow.

## Test Signals
Test signals include matching every ID table entry to the correct property entry, delayed startup ordering, firmware/device ID parsing, sysfs formatting, monitor mixer get/put and sysex encoding, PCM constraints for 24-bit packed stereo, control-only Pocket POD behavior, and disconnect/PM callback integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/pod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/podhd.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/podhd.c

## Purpose
`podhd.c` supports Line 6 POD HD and POD X3-generation USB devices. It defines device-specific PCM formats, startup handshakes, optional control-interface claiming, sysfs metadata, and an ALSA monitor-volume control for models with hardware-monitor control support.

## Important APIs, Types, And Functions
`struct usb_line6_podhd` embeds `struct usb_line6` and caches `serial_number`, `firmware_version`, and `monitor_level`. Important functions are `podhd_probe()`, `podhd_init()`, `podhd_startup()`, `podhd_dev_start()`, `podhd_disconnect()`, `podhd_set_monitor_level()`, and the `snd_podhd_control_monitor_*()` ALSA control callbacks. The USB ID table maps device products to `podhd_properties_table`.

## Control Flow And State
Probe delegates to `line6_probe()` with a PODHD property entry. `podhd_init()` installs disconnect/startup callbacks. For devices with a separate control interface, it finds and claims `ctrl_if` with `usb_driver_claim_interface()`. Devices with `LINE6_CAP_CONTROL_INFO` get a `podhd` sysfs group for firmware and serial number and delay card registration until startup work completes. PCM devices call `line6_init_pcm()` with either standard 2-in/2-out 48 kHz 24-bit packed properties or POD X3 8-channel capture properties.

`podhd_dev_start()` performs a vendor request sequence, reads three firmware bytes, reads a small range of device memory with `line6_read_data()`, then sends a standard `SET_FEATURE`. `podhd_startup()` calls that handshake, reads the serial number, and registers the ALSA card. Hardware monitor control uses a static 101-entry lookup table of little-endian IEEE float encodings for 0.0 through 1.0. `podhd_set_monitor_level()` clamps user values to 0..100, patches the raw command payload, sends it with `line6_send_raw_message()`, and updates cached state.

## State And Persistence
Driver state is volatile: claimed-interface ownership, cached firmware/serial/monitor values, PCM stream state held in the common Line 6 PCM layer, and ALSA card registration status. Device-side firmware and monitor settings persist according to device behavior, not this code.

## Dependencies And Integration Points
This file depends on the common Line 6 driver and PCM core, ALSA controls/sysfs, USB interface claiming/release, vendor control transfers, and model capabilities such as `LINE6_CAP_PCM`, `LINE6_CAP_CONTROL`, `LINE6_CAP_CONTROL_INFO`, `LINE6_CAP_HWMON`, `LINE6_CAP_HWMON_CTL`, and `LINE6_CAP_IN_NEEDS_OUT`.

## Risks And Edge Cases
Control interface claiming must be paired with release in `podhd_disconnect()`; errors after claiming can leak ownership unless common cleanup calls the disconnect hook. The monitor command is mostly magic constants, so device firmware changes could break it silently. `podhd_dev_start()` logs some failures but startup still attempts registration through `podhd_startup()`. The code assumes MIDI 2.0-style UMP is irrelevant and uses Line 6-specific raw/control paths.

## Test Signals
Tests should cover ID/property alignment, control-interface claim and release, POD X3 8-channel capture constraints, 48 kHz 24-bit PCM setup, sysfs formatting, startup vendor request sequencing, monitor clamping and payload bytes, direct registration path for devices without control-info, and suspend/resume/disconnect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/podhd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/toneport.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/toneport.c

## Purpose
`toneport.c` supports Line 6 GuitarPort, TonePort, and POD Studio USB audio devices. It initializes fixed 44.1 kHz 16-bit stereo PCM, implements software monitor volume acquisition, optional capture-source selection, device setup commands, and LED class devices for models with red/green LEDs.

## Important APIs, Types, And Functions
The private type is `struct usb_line6_toneport`, embedding `struct usb_line6` and storing `source`, `serial_number`, `firmware_version`, `type`, and two `toneport_led` instances. The USB entry point is `toneport_probe()`. Setup flows through `toneport_init()`, `toneport_setup()`, `toneport_startup()`, and optional PM `toneport_reset_resume()`. User-facing controls are `toneport_control_monitor`, `toneport_control_source`, and LED class callbacks.

## Control Flow And State
Probe delegates to `line6_probe()` with a property row. `toneport_init()` records the model type, installs disconnect/startup hooks, initializes PCM, adds the monitor mixer control, conditionally adds the enumerated `PCM Capture Source` control, reads serial/firmware bytes, registers LEDs when supported, performs setup, and registers the ALSA card.

`toneport_setup()` writes the current host time to device address `0x80c6`, sends an enable command, applies source selection for UX models, updates LEDs for GuitarPort/TonePort GX, and schedules delayed startup. `toneport_startup()` acquires the monitor stream. The monitor mixer stores its value in `line6pcm->volume_monitor`; nonzero values acquire `LINE6_STREAM_MONITOR`, zero releases it. Source selection maps enum values to fixed command words and sends them via a vendor control request. LED brightness changes send a combined red/green command.

## State And Persistence
State is volatile in the driver except any settings the device firmware retains. The source selector, firmware byte, serial number, LED brightness, and monitor volume are cached in memory. LED registration state prevents unregistering unregistered class devices.

## Dependencies And Integration Points
The file integrates ALSA PCM/control APIs, the LED subsystem, USB vendor control messages, Line 6 PCM acquisition/release, common Line 6 probe/disconnect/PM hooks, and device property tables. It depends on `playback.c` for software monitoring because these devices lack hardware monitoring capability bits.

## Risks And Edge Cases
`toneport_send_cmd()` failures are often ignored by callers, so source or LED state can be cached as changed even when the USB command failed. The 32-bit timestamp comment notes overflow in year 2106. LED support is model-gated and must be extended manually for new devices. Monitor acquisition failure rolls the monitor volume back to zero, but source/LED paths do not similarly roll back.

## Test Signals
Coverage should include monitor volume transitions and stream acquisition/release, source enum bounds and command encoding, LED registration/unregistration and brightness commands, reset-resume setup replay, device ID/property consistency, card registration, and PCM constraints for 44.1 kHz signed 16-bit stereo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/toneport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/variax.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/variax.c

## Purpose
`variax.c` supports Line 6 Variax Workbench and the Variax interface of PODxt Live devices. It is primarily a control/MIDI driver: it performs a staged activation handshake, reacts to initialization sysex messages, and registers the ALSA card once the device is ready.

## Important APIs, Types, And Functions
`struct usb_line6_variax` embeds `struct usb_line6`, stores an allocated activation buffer, and tracks `startup_progress`. Key functions are `variax_probe()`, `variax_init()`, `variax_startup()`, `line6_variax_process_message()`, `variax_activate_async()`, and `line6_variax_disconnect()`.

## Control Flow And State
`variax_init()` installs message, disconnect, and startup callbacks, duplicates the static activation sysex payload, and schedules delayed startup. The startup state machine starts in `VARIAX_STARTUP_VERSIONREQ`, repeatedly schedules itself, and sends async firmware version requests until the expected version sysex is received. `line6_variax_process_message()` recognizes reset messages, the Variax init-version sysex, and the init-done sysex. Version reception advances to `VARIAX_STARTUP_ACTIVATE`; startup then sends the activation sysex with byte 7 set to one and advances to setup. Setup registers the ALSA card.

## State And Persistence
State is volatile and limited to startup progress plus the activation message buffer. The device state changes when activation is sent, but the driver does not persist settings. The activation buffer is freed through the Line 6 disconnect hook.

## Dependencies And Integration Points
The file depends on the common Line 6 driver for USB probe/disconnect/PM, raw async message sending, version requests, and control MIDI capability setup. Device properties describe control endpoints and no standalone audio channel for the Workbench model.

## Risks And Edge Cases
The version request loops until a matching sysex arrives, so devices that never answer rely on delayed work cancellation during disconnect. Message matching uses fixed byte arrays and assumes the common layer supplies complete messages. `snd_card_register()` return value in setup is ignored. Activation buffer allocation failure prevents initialization cleanly.

## Test Signals
Tests should cover startup transitions on init-version and init-done messages, repeated version request scheduling, activation payload mutation, disconnect freeing while delayed work may be pending, reset logging, PODxt Live interface-number matching, and control-only Variax behavior without PCM setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/variax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/media.c -->
# sources/distributed-fs/ceph-client/sound/usb/media.c

## Purpose
`media.c` adds Linux Media Controller graph integration to selected ALSA USB-audio devices. It creates media devices, mixer entities, PCM stream entities, interface links to ALSA control/PCM device nodes, and pipeline start/stop hooks so tuner-like USB devices can be shared with DVB/V4L2 users.

## Important APIs, Types, And Functions
Public functions are `snd_media_device_create()`, `snd_media_device_delete()`, `snd_media_stream_init()`, `snd_media_stream_delete()`, `snd_media_start_pipeline()`, and `snd_media_stop_pipeline()`. Internal helpers are `snd_media_mixer_init()` and `snd_media_mixer_delete()`. The data structures are defined in `media.h`: `struct media_ctl` for PCM streams and `struct media_mixer_ctl` for mixer entities.

## Control Flow And State
`snd_media_device_create()` either reuses `chip->media_dev` or allocates one with `media_device_usb_allocate()`, then initializes mixer/control entities and registers the media device if needed. Mixer initialization creates a media devnode for the ALSA control device, then creates an `MEDIA_ENT_F_AUDIO_MIXER` entity per USB mixer interface, with sink/source pads and an enabled interface link.

`snd_media_stream_init()` creates one media entity per ALSA PCM stream. Playback streams are `MEDIA_ENT_F_AUDIO_PLAYBACK` with an ALSA playback interface type and a source pad; capture streams are `MEDIA_ENT_F_AUDIO_CAPTURE` with an ALSA capture interface type and a sink pad. It links the stream entity to mixer pad 1 for playback or pad 2 for capture. Start/stop pipeline functions lock `media_dev->graph_mutex` and call optional `enable_source`/`disable_source` callbacks.

Deletion walks PCM streams and mixers, removes devnodes/entities when the media devnode is registered, deletes the media device, and clears pointers in `snd_usb_audio` and mixer/substream objects.

## State And Persistence
There is no persistence. Runtime ownership is stored in `chip->media_dev`, `chip->ctl_intf_media_devnode`, `mixer->media_mixer_ctl`, and `subs->media_ctl`. `media_pipeline` state is held per stream entity.

## Dependencies And Integration Points
The file depends on the Media Controller core, ALSA USB card/mixer/substream structures, USB device allocation helpers, and PCM/control devnodes. It is gated by `CONFIG_SND_USB_AUDIO_USE_MEDIA_CONTROLLER` through `media.h`.

## Risks And Edge Cases
Partial failure cleanup is delicate because entity registration, devnode creation, interface links, and pad links happen in sequence. `snd_media_mixer_init()` can return after allocating the shared control devnode but before all mixers are initialized. `snd_media_stream_delete()` removes interface devnodes and entities but does not explicitly remove pad links; this relies on entity cleanup/unregister semantics. Pipeline callbacks are optional and must be called with graph locking.

## Test Signals
Test with devices that opt into media-controller quirks: creation idempotence across multiple USB interfaces, mixer and stream entity/pad/link topology, failure injection for each allocation/register step, pipeline enable/disable callback invocation, stream delete before/after media device registration, and full device delete after PCM/mixer creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/media.h -->
# sources/distributed-fs/ceph-client/sound/usb/media.h

## Purpose
`media.h` declares the USB-audio Media Controller integration API and provides no-op stubs when media-controller support is disabled.

## Important APIs, Types, And Macros
When `CONFIG_SND_USB_AUDIO_USE_MEDIA_CONTROLLER` is enabled, it defines `struct media_ctl`, `struct media_mixer_ctl`, `MEDIA_MIXER_PAD_MAX`, and prototypes for device, stream, and pipeline lifecycle functions. When disabled, equivalent static inline stubs return success or do nothing.

## Control Flow And State
The header itself has no runtime flow. It controls whether callers compile against real media graph creation/deletion or no-op functions. `struct media_ctl` stores a media device, stream entity, interface devnode/link, single pad, and pipeline. `struct media_mixer_ctl` stores a mixer entity with pads for sink, playback source, and capture source.

## State And Persistence
No persistent state exists. The structures define runtime graph ownership used by `media.c`; in the disabled configuration no state is allocated.

## Dependencies And Integration Points
Enabled builds include Linux media headers and ALSA asound constants. Callers in USB-audio core can invoke the functions unconditionally because stubs preserve the same signatures.

## Risks And Edge Cases
The include guard is `#ifndef __MEDIA_H` without an immediate `#define __MEDIA_H`, so it does not actually prevent repeated inclusion. That is low risk in current usage because the content is mostly declarations/static inlines, but it is an unusual header defect. Configuration stubs make it easy for callers to miss that media graph features are compiled out.

## Test Signals
Build both enabled and disabled configurations. Enabled builds should validate struct users and media API linkage; disabled builds should verify no unresolved media symbols and unchanged USB-audio behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi.c -->
# sources/distributed-fs/ceph-client/sound/usb/midi.c

## Purpose
`midi.c` is the legacy ALSA USB MIDI 1.0 helper driver. It discovers MIDIStreaming endpoints or applies quirk metadata, creates ALSA rawmidi ports, translates between ALSA byte streams and USB MIDI event packets, handles many vendor-specific protocols, manages input/output URBs, and provides suspend/resume/disconnect helpers for USB-audio users.

## Important APIs, Types, And Functions
The exported entry point is `__snd_usbmidi_create()`, wrapped by `snd_usbmidi_create()` in `midi.h`. Exported lifecycle helpers are `snd_usbmidi_disconnect()`, `snd_usbmidi_input_stop()`, `snd_usbmidi_input_start()`, `snd_usbmidi_suspend()`, and `snd_usbmidi_resume()`.

Core types are `struct snd_usb_midi`, `struct snd_usb_midi_out_endpoint`, `struct snd_usb_midi_in_endpoint`, `struct usbmidi_out_port`, and `struct usb_protocol_ops`. Protocol operations cover standard USB MIDI, Midiman, broken M-Audio running status, CME, CH345 broken sysex, Akai, Novation, raw bytes, FTDI, Tascam US-122L, and Emagic.

## Control Flow And State
`__snd_usbmidi_create()` allocates `snd_usb_midi`, initializes locks/timer, selects protocol operations and endpoint detection based on quirk type, counts input/output cables, creates an ALSA rawmidi device, creates endpoints/ports, takes an autosuspend reference, and links the instance into the caller's MIDI list.

Input endpoints allocate seven URBs and coherent buffers. Completion calls the selected protocol parser, which eventually calls `snd_usbmidi_input_data()` for a cable/port if the ALSA input substream is triggered, then resubmits the URB. Recoverable USB errors defer resubmission via `error_timer`.

Output endpoints allocate seven URBs and coherent buffers. ALSA output trigger marks a port active and queues high-priority work. `snd_usbmidi_do_output()` picks free URBs round-robin, asks the protocol formatter to fill the transfer buffer from rawmidi substreams, submits non-empty URBs, and tracks active bits. Completion clears active/drain bits, wakes drain waiters, and refills output. Standard output uses a MIDI byte state machine to assemble CIN packets, including sysex states and running channel messages.

Rawmidi open/close updates `opened[]`, starts input when an input stream opens, stops it when all input streams close, and handles Roland alternate-setting control in a mutex. Disconnect sets `disconnected` under rwsem/spinlock, shuts down the error timer, cancels work, kills all URBs, runs protocol finish hooks, clears buffers, wakes drains, and frees input endpoints.

## State And Persistence
State is entirely runtime: endpoint objects, URB bitmaps, rawmidi substream bindings, protocol parser state (`running_status_length`, `in_sysex`, `seen_f5`, current port), open counts, trigger bits, Roland load control value, and disconnect/input-running flags. No settings are persisted by the driver.

## Dependencies And Integration Points
The file integrates USB core bulk/interrupt transfers, ALSA rawmidi and sequencer port metadata, USB-audio quirk definitions, autosuspend power management, helper descriptor accessors, and optional vendor controls. It is used by generic USB-audio and by specialized drivers such as UA-101.

## Risks And Edge Cases
The risk surface is broad: malformed descriptors, devices with incorrect endpoint packet sizes, quirk-specific packet formats, URB completion races with disconnect/timer/work, drain waits, and alternate-setting changes while ports are open. Some endpoint detection paths trust quirk-provided cable masks. The standard output state machine must not overrun `max_transfer`; vendor parsers must handle short packets and malformed sysex. Cleanup frees input endpoints during disconnect and later frees output endpoint containers during rawmidi free, so ordering is important.

## Test Signals
Test standard MIDI event packet encode/decode, sysex fragmentation, realtime interleaving, every quirk protocol parser/formatter, descriptor discovery for standard/Yamaha/Roland/Midiman paths, rawmidi open/close/trigger/drain behavior, input stop/start around suspend and Roland altsetting changes, disconnect races with active URBs and error timer, low-speed interrupt fallback, fixed packet-size device exceptions, and port naming/sequence flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi.h -->
# sources/distributed-fs/ceph-client/sound/usb/midi.h

## Purpose
`midi.h` is the public internal header for the USB-audio legacy MIDI 1.0 helper. It defines endpoint quirk metadata and declares creation/lifecycle functions used by USB-audio and specialized USB sound drivers.

## Important APIs, Types, And Macros
`MIDI_MAX_ENDPOINTS` limits a MIDI interface to two endpoint groups. `struct snd_usb_midi_endpoint_info` describes fixed endpoint numbers, interrupt intervals, cable bitmasks, and associated jack IDs for quirks. `__snd_usbmidi_create()` allows callers to pass an explicit USB ID and rawmidi device counter; `snd_usbmidi_create()` is the common wrapper. Lifecycle declarations cover input stop/start, disconnect, suspend, and resume.

## Control Flow And State
The header provides no implementation except the wrapper that calls `__snd_usbmidi_create(card, iface, midi_list, quirk, 0, NULL)`. Its comments document the expected `quirk->data` shape for standard, fixed endpoint, Yamaha, Midiman, composite, raw, Emagic, CME, and Akai-style quirk types.

## State And Persistence
No persistent state exists. The endpoint info structure is copied by `midi.c` during creation and drives runtime endpoint/cable construction.

## Dependencies And Integration Points
The header is consumed by USB-audio card setup and miscellaneous drivers such as UA-101. It relies on ALSA card/list types and quirk definitions from the surrounding USB-audio code.

## Risks And Edge Cases
Incorrect quirk data layout can misconfigure endpoint direction, intervals, or cable masks. The two-endpoint limit is baked into structure arrays and creation logic. Associated jack IDs use signed 16-bit values, with `-1` used internally to avoid jack-name lookup.

## Test Signals
Compile users with fixed and standard MIDI creation paths. Validate quirk structures for endpoint masks, intervals, and jack IDs; ensure rawmidi numbering works for callers using `__snd_usbmidi_create()` with a shared counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi2.c -->
# sources/distributed-fs/ceph-client/sound/usb/midi2.c

## Purpose
`midi2.c` implements USB MIDI 2.0 support for ALSA USB-audio. It detects MIDI 2.0 alternate settings, creates UMP rawmidi endpoints, pairs USB input/output endpoints using group terminal block IDs, parses group terminal block descriptors, starts input UMP traffic, optionally probes UMP endpoint/function-block information, attaches legacy rawmidi views, and falls back to MIDI 1.0 when MIDI 2.0 is disabled or unavailable.

## Important APIs, Types, And Functions
Public functions are `snd_usb_midi_v2_create()`, `snd_usb_midi_v2_suspend_all()`, `snd_usb_midi_v2_resume_all()`, `snd_usb_midi_v2_disconnect_all()`, and `snd_usb_midi_v2_free_all()`. Module parameters are `midi2_enable` and `midi2_ump_probe`.

Core private types are `struct snd_usb_midi2_interface`, `struct snd_usb_midi2_endpoint`, `struct snd_usb_midi2_ump`, and `struct snd_usb_midi2_urb`. UMP callbacks are `snd_usb_midi_v2_open()`, `snd_usb_midi_v2_close()`, `snd_usb_midi_v2_trigger()`, and `snd_usb_midi_v2_drain()`.

## Control Flow And State
`snd_usb_midi_v2_create()` first checks module options, quirk type, alternate-setting count, MIDI 2.0 class header, and endpoint presence. If any condition fails, it calls `__snd_usbmidi_create()` for legacy MIDI 1.0. Otherwise it allocates a MIDI 2.0 interface object, switches to altsetting 1, parses MIDI 2.0 endpoint descriptors, pairs input and output endpoints that share group terminal block IDs, creates unidirectional UMP endpoints for remaining groups, fetches and parses GTB descriptors, allocates and submits input URBs, optionally runs `snd_ump_parse_endpoint()`, creates UMP blocks from GTB fallback data, fills endpoint names/product IDs, and optionally attaches legacy rawmidi devices.

Input endpoints allocate eight URBs at interface creation and keep them running. Completion aligns actual length to 32-bit UMP words, converts little-endian words to CPU order, calls `snd_ump_receive()`, marks the URB free, and resubmits. Output URBs are allocated on UMP open, filled from `snd_ump_transmit()`, converted to little-endian, and submitted while the endpoint running flag is set. Drain waits for all URBs to return or disconnect.

Suspend kills URBs while saving running state; resume restores altsetting, restores running state, and resubmits input or active output. Disconnect marks interface and endpoints disconnected, kills URBs, and drains queues. Free removes endpoint/UMP lists and GTB descriptor storage.

## State And Persistence
All state is runtime: endpoint lists, UMP rawmidi list, GTB descriptor copy, URB free bitmaps, running/suspended atomics, pair links, parsed UMP flags, and `chip->num_rawmidis`. The only module-level state is configuration parameters.

## Dependencies And Integration Points
This file depends on ALSA UMP core, optional legacy UMP rawmidi support, USB MIDI 2.0 descriptor definitions, USB-audio card lists, and the legacy MIDI 1.0 helper for fallback. It uses control transfers to fetch `USB_DT_CS_GR_TRM_BLOCK` descriptors and USB altsetting management for MIDI 2.0 operation.

## Risks And Edge Cases
The code assumes MIDI 2.0 is on altsetting 1. Descriptor parsing must reject malformed endpoint and GTB lengths. Pairing by GTB ID can create only one UMP per ID; devices with unusual block mappings may fall back to unidirectional objects. Input URBs are started during creation before user open, so disconnect/suspend ordering is critical. Output close kills and frees URBs, while input URBs persist until interface free. Errors after adding the interface to `chip->midi_v2_list` rely on `snd_usb_midi_v2_free()` cleanup.

## Test Signals
Test fallback matrix for disabled MIDI2, quirks, missing altsetting, non-MIDI2 headers, and no endpoints. Test descriptor parsing, GTB fetch errors, endpoint pairing/unidirectional creation, UMP open/trigger/drain/close, endian conversion, input always-on delivery, UMP probe fallback to GTB blocks, legacy rawmidi attachment, suspend/resume altsetting restore, disconnect with active URBs, and malformed descriptor length handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi2.h -->
# sources/distributed-fs/ceph-client/sound/usb/midi2.h

## Purpose
`midi2.h` declares USB MIDI 2.0 integration points for USB-audio and provides legacy MIDI 1.0 fallback stubs when `CONFIG_SND_USB_AUDIO_MIDI_V2` is disabled.

## Important APIs, Types, And Macros
When MIDI 2.0 is enabled, it declares `snd_usb_midi_v2_create()`, suspend/resume, disconnect, and free helpers. When disabled, `snd_usb_midi_v2_create()` is an inline wrapper around `__snd_usbmidi_create()` using `chip->midi_list` and `chip->num_rawmidis`; the lifecycle helpers become no-ops.

## Control Flow And State
The header selects compile-time behavior. Enabled builds route USB MIDI interface creation through `midi2.c`, which can still fall back dynamically. Disabled builds always create legacy MIDI 1.0 rawmidi devices and maintain no MIDI 2.0 list state.

## State And Persistence
No state is stored in this header. It affects whether runtime state is stored in `chip->midi_v2_list` or the legacy `chip->midi_list`.

## Dependencies And Integration Points
The header depends on `midi.h` for the legacy fallback and on USB-audio structures supplied by callers. It lets USB-audio core call the same symbol names regardless of configuration.

## Risks And Edge Cases
In disabled builds, suspend/resume/disconnect/free operations for MIDI 2.0 are no-ops by design; callers must still run legacy MIDI lifecycle on `chip->midi_list`. The inline fallback ignores MIDI 2.0 descriptors completely.

## Test Signals
Build both `CONFIG_SND_USB_AUDIO_MIDI_V2=y/m` and disabled configurations. Verify dynamic fallback in enabled builds and direct legacy creation in disabled builds, including rawmidi numbering through `chip->num_rawmidis`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/midi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/misc/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/misc/Makefile

## Purpose
This Makefile builds the miscellaneous USB sound driver module for Edirol UA-101/UA-1000 devices.

## Important APIs, Types, And Functions
It declares `snd-ua101-y := ua101.o`, making `ua101.c` the object linked into the `snd-ua101` module. `obj-$(CONFIG_SND_USB_UA101) += snd-ua101.o` ties module compilation to the kernel configuration option.

## Control Flow And State
There is no runtime control flow. Kbuild uses the config symbol to decide whether to compile/link the UA-101 driver.

## State And Persistence
No runtime state or persistence exists.

## Dependencies And Integration Points
This file integrates with Kbuild and `CONFIG_SND_USB_UA101`. The resulting module depends on ALSA core, USB core, and the implementation in `ua101.c`.

## Risks And Edge Cases
If `CONFIG_SND_USB_UA101` is not selected, `ua101.c` is not built and matching hardware will not bind to this driver. Any future split of UA-101 sources must update `snd-ua101-y`.

## Test Signals
Build tests should cover `CONFIG_SND_USB_UA101=m`, `y`, and unset. Module output should contain `snd-ua101` with `ua101.o` linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/misc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/misc/ua101.c -->
# sources/distributed-fs/ceph-client/sound/usb/misc/ua101.c

## Purpose
`ua101.c` is a dedicated ALSA USB driver for Edirol UA-101 and UA-1000 interfaces. It handles devices whose playback rate must be synchronized to capture packet timing, creates one duplex PCM device plus legacy USB MIDI, manages multiple USB interfaces, and implements its own isochronous URB queues instead of the generic USB-audio PCM engine.

## Important APIs, Types, And Functions
The private `struct ua101` stores USB device/interfaces, ALSA card/PCM, MIDI list, detected sample format/rate, stream state, synchronization FIFOs, locks, wait queues, and nested `ua101_stream` objects for capture/playback. Module parameters are `index`, `id`, `enable`, and `queue_length`.

Key functions include `ua101_probe()`, `ua101_disconnect()`, `detect_usb_format()`, `alloc_stream_buffers()`, `alloc_stream_urbs()`, `start_usb_capture()`, `start_usb_playback()`, `stop_usb_capture()`, `stop_usb_playback()`, `capture_urb_complete()`, `playback_urb_complete()`, `playback_work()`, PCM callbacks for open/close/hw_params/prepare/trigger/pointer, and cleanup helpers.

## Control Flow And State
Probe accepts only the first relevant interface, allocates an ALSA card, claims the additional playback/capture/MIDI interfaces according to UA-101 versus UA-1000 numbering, validates descriptors, derives sample width/rate/channel counts/endpoints, allocates page-subdivided coherent buffers and one-packet isochronous URBs, creates a duplex PCM device, creates fixed-endpoint legacy MIDI, registers the card, and records the used card index.

Capture starts independently and is required before playback. Capture URB completion copies samples into the ALSA capture ring when running, resubmits the URB, and appends the observed frame count to a rate-feedback FIFO. Playback start waits until that FIFO contains one full playback queue. Initial playback URBs send silence using those captured packet sizes. Later playback URBs complete into a ready list; `playback_work()` consumes both a ready playback URB and one capture-derived frame count, fills the URB from the playback ALSA ring or silence, submits it, and updates runtime delay. This keeps playback packet sizing locked to capture timing.

PCM open starts USB capture for capture streams and both capture/playback for playback streams. Prepare waits until the first USB URB completes so ALSA does not start against a scheduled-but-not-yet-active EHCI stream. Trigger only toggles ALSA running bits; USB streams may already be running to maintain timing. Disconnect marks the device disconnected, wakes waiters, disconnects the card, stops MIDI and PCM activity, frees USB resources, releases claimed interfaces, clears the card slot, and defers final card free until userspace closes handles.

## State And Persistence
State is volatile. `states` bit flags track USB running, ALSA open/running, first URB completion, and disconnect. `rate_feedback_start/count` plus `rate_feedback[]` synchronize playback packet sizes. Stream state tracks period and ring buffer positions, queue length, coherent buffer chunks, and URB pointers. No device settings are persisted by the driver.

## Dependencies And Integration Points
The driver depends on ALSA card/PCM/initval APIs, USB core interface claiming and isochronous URBs, USB Audio Class descriptors, the legacy USB MIDI helper, and Kbuild's `CONFIG_SND_USB_UA101`. It uses `snd_pcm_set_managed_buffer_all()` with vmalloc ALSA buffers and its own coherent USB buffers.

## Risks And Edge Cases
Synchronization is timing-sensitive: playback cannot start if capture is not producing feedback, and feedback FIFO overflow discards oldest sizes when playback is idle. The `queue_length` module parameter is clamped, but memory sizing depends on endpoint max packet bytes and page subdivision. Cleanup must handle partially claimed interfaces and partially allocated buffers/URBs. `do_period_elapsed` in `capture_urb_complete()` is set only when frames are copied; this depends on the local branch. Suspend/resume is disabled in `#if 0`. Descriptor validation is strict and rejects unexpected altsetting/endpoint/format layouts.

## Test Signals
Test descriptor detection for UA-101 high/full speed and UA-1000, queue length clamping, buffer subdivision for packet sizes, capture-only open/prepare/trigger, playback open waiting for capture feedback, initial silence packets, period elapsed cadence, runtime delay updates, feedback FIFO overflow while playback is stopped, USB submit failures, disconnect during waits and active URBs, MIDI fixed-endpoint creation, interface release on probe failure, and build/module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/misc/ua101.c -->
