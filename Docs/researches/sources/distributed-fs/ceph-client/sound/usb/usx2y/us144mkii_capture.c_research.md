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
