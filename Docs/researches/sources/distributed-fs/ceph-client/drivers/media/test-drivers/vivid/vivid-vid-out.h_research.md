# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-out.h

Purpose: declaration header for Vivid video output support. It exposes output queue ops, output format reset, mplane and single-plane output format handlers, selection/pixel-aspect operations, overlay and framebuffer controls, output/audio routing, TV standard/DV timing setters, and output stream parameter getter.

It owns no persistent state. Its functions operate on `struct vivid_dev` through V4L2 `file`/`priv` plumbing and use V4L2 buffer, format, selection, framebuffer, audioout, timing, and stream parameter types. Integration points are the Vivid video output ioctl table, vb2 queue setup, and output kthread paths.

Risks are declaration drift and forgetting to expose new output ioctls here when adding implementation in `vivid-vid-out.c`. Test signals are compile coverage and V4L2 output ioctl registration paths, particularly single-planar wrappers that call common SP-to-MP conversion.
