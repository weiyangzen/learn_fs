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
