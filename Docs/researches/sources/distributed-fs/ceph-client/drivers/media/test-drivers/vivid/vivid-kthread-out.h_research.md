# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.h

Purpose: declares the shared output generation lifecycle for video, VBI, and metadata output streams.

Important APIs and types: `vivid_start_generating_vid_out(struct vivid_dev *dev, bool *pstreaming)` and `vivid_stop_generating_vid_out(struct vivid_dev *dev, bool *pstreaming)`.

Control flow: output queue operations call these helpers from `start_streaming` and `stop_streaming`; the boolean pointer identifies which output stream is joining or leaving the shared kthread.

State and persistence: no header-owned state. The implementation mutates `struct vivid_dev` output flags, active buffer lists, and kthread state.

Dependencies and integration points: used by video output, VBI output, and metadata output modules.

Risks: callers must pass the correct stream flag address; otherwise sequence starts and shutdown decisions can affect the wrong stream class.

Test signals: compile coverage plus concurrent video/VBI/meta output streaming validates this interface.
