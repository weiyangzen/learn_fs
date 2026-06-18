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
