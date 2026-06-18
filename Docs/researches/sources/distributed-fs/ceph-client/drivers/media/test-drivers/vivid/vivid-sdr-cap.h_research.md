# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.h

Purpose: declares Vivid SDR capture queue operations, tuner/frequency ioctls, format ioctls, and sample-buffer generation helper.

Important APIs and types: declarations cover frequency bands, get/set frequency, get/set tuner, enum/get/set/try SDR format, `vivid_sdr_cap_process`, and `vivid_sdr_cap_qops`.

Control flow: Vivid SDR video_device ioctl and queue setup tables reference these functions.

State and persistence: no header-owned state. Implementations mutate SDR fields in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 SDR/tuner/frequency/file types and Vivid buffer/device types from including code.

Risks: adding SDR formats requires keeping the implementation's format table and users of `sdr_buffersize` aligned with this header's operation surface.

Test signals: compile coverage and SDR ioctl/streaming tests validate the declarations.
