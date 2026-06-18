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
