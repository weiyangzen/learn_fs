# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.h

Purpose: declares Vivid VBI output processing, raw/sliced VBI output format handlers, and queue operations.

Important APIs and types: declarations include `vivid_sliced_vbi_out_process`, raw VBI get/set format handlers, sliced VBI get/try/set format handlers, and `vivid_vbi_out_qops`.

Control flow: VBI output queue/ioctl tables use these functions, and the shared output kthread calls the process helper for sliced output buffers.

State and persistence: no header-owned state. Implementations cache WSS/CC loopback state in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 file/format/vb2 types and Vivid device/buffer declarations.

Risks: the processing declaration overlaps with `vivid-vbi-cap.h`; ownership is split because capture uses output-derived data for loopback.

Test signals: compile coverage and VBI output ioctl/streaming tests validate this boundary.
