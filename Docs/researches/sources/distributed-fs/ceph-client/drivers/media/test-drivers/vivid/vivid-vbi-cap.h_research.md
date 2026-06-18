# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.h

Purpose: declares Vivid VBI capture processing, sliced VBI output processing shared capability helper, VBI format ioctls, service-line helper, and queue operations.

Important APIs and types: declarations include raw/sliced capture processors, `vivid_sliced_vbi_out_process`, raw and sliced get/set/try format handlers, sliced VBI capability handler, `vivid_fill_service_lines`, and `vivid_vbi_cap_qops`.

Control flow: capture kthread and VBI queue/ioctl tables use these declarations; VBI output code also includes this header for shared service-line and capability behavior.

State and persistence: no header-owned state. Implementations use `struct vivid_dev` service-set and VBI generator state.

Dependencies and integration points: requires V4L2 VBI/vb2/file types and Vivid device/buffer declarations.

Risks: declaring `vivid_sliced_vbi_out_process` here as well as in the output header creates cross-header coupling and can obscure ownership.

Test signals: compile coverage of both capture and output VBI modules and VBI ioctl tests validate the boundary.
