# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-cap.h

Purpose: declares the shared video/VBI/meta capture generation thread lifecycle.

Important APIs and types: `vivid_start_generating_vid_cap(struct vivid_dev *dev, bool *pstreaming)` starts or joins the capture kthread for the stream represented by `pstreaming`; `vivid_stop_generating_vid_cap` stops one stream and tears down the kthread when the last dependent stream stops.

Control flow: capture queue operations in video, VBI, and metadata modules call these helpers from their `start_streaming` and `stop_streaming` callbacks.

State and persistence: the header owns no state. The implementation mutates stream flags, kthread pointer, active buffer lists, and sequence counters in `struct vivid_dev`.

Dependencies and integration points: included by capture queue modules and the control path that needs to coordinate stream generation.

Risks: the `bool *pstreaming` argument is a stream identity token, so callers must pass exactly the address of the matching `struct vivid_dev` streaming flag.

Test signals: compile coverage and streaming video, VBI, and metadata independently and concurrently validate the interface.
