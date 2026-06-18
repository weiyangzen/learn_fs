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
