# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.c

Purpose: implements the shared output-side kernel thread for Vivid video output, VBI output, and metadata output. It advances output sequence counters, completes queued output buffers at the configured frame cadence, processes sliced VBI and metadata payloads, and holds the latest video output buffer available for loopback capture.

Important APIs and functions: exported APIs are `vivid_start_generating_vid_out` and `vivid_stop_generating_vid_out`. Internal functions are `vivid_thread_vid_out_tick`, `vivid_thread_vid_out`, and `vivid_grab_controls`.

Control flow: starting an output stream starts `vivid_thread_vid_out` if no output thread exists, or records a per-stream sequence start if one does. The thread calculates elapsed buffers from `jiffies`, applies resync and timestamp wrap offsets, updates per-stream sequence counts, ticks the active lists, then sleeps until the next output deadline. Ticks optionally drop buffers, dequeue video buffers only when more than one is queued so loopback can keep using the last buffer, dequeue eligible VBI and metadata buffers, run request setup/complete, process VBI/meta payloads, stamp sequence/timestamp fields, complete buffers, and clear `dqbuf_error`.

State and persistence: state is volatile in `struct vivid_dev`: `kthread_vid_out`, stream flags, output sequence counters/offsets, active buffer lists, `jiffies_vid_out`, timestamp wrap offset, VBI output cached WSS/CC flags, and controls grabbed while streaming. Stop completes remaining active buffers with error for the stream being stopped and stops the kthread only after video, VBI, and metadata output streams are all inactive.

Dependencies and integration points: depends on Linux kthreads/freezer/jiffies/random, videobuf2, V4L2 request controls, Vivid core/video/radio/SDR/VBI/OSD/control headers, and metadata output processing. Capture loopback depends on this file leaving the newest video output buffer on `vid_out_active`.

Risks: the deliberate "keep one video output buffer pending" behavior is important for loopback but can surprise output-only tests expecting every queued buffer to complete immediately. Shared `dqbuf_error` affects any output stream tick. The control grab set must stay in sync with output controls created in `vivid-ctrls.c`. Timing depends on `timeperframe_vid_out` and field mode, so resync math and alternate-field sequence handling are sensitive.

Test signals: output stream cadence, streamoff buffer cleanup, video loopback stability, VBI output-to-capture WSS/CC propagation, metadata output control updates, queue error injection, sequence/time wrap controls, and `v4l2-compliance` output streaming are the main validation signals.
