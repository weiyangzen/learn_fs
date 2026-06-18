# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.h

Purpose: declares the touch capture generation thread lifecycle.

Important APIs and types: `vivid_start_generating_touch_cap(struct vivid_dev *dev)` starts touch generation, and `vivid_stop_generating_touch_cap(struct vivid_dev *dev)` stops it and drains queued buffers.

Control flow: touch capture queue operations call these helpers from `start_streaming` and `stop_streaming`.

State and persistence: no header-owned state. Implementation state is in `struct vivid_dev`.

Dependencies and integration points: included by the touch capture module and implementation.

Risks: the include guard and comment use `_VIVID_KTHREAD_CAP_H_` / "vivid-kthread-cap.h", duplicating the video capture kthread header guard name. If both headers are included in one translation unit in the wrong order, the touch declarations can be skipped.

Test signals: compile coverage of translation units including both kthread headers and touch streaming tests validate this header.
