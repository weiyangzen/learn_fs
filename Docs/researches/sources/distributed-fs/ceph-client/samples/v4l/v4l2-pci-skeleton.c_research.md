# sources/distributed-fs/ceph-client/samples/v4l/v4l2-pci-skeleton.c

## Purpose

This is a V4L2 PCI capture-driver skeleton. It shows the structure of a PCI video receiver with one S-Video input, one HDMI input, V4L2 controls, format/timing negotiation, and videobuf2 capture queue integration.

## Important APIs, Types, and Functions

Core types are `struct skeleton`, holding PCI, V4L2 device/video_device, control handler, queue, format, input, standard, timings, and buffer list state, plus `struct skel_buffer`. Important functions include `queue_setup()`, `buffer_prepare()`, `buffer_queue()`, `return_all_buffers()`, `start_streaming()`, `stop_streaming()`, format/std/timings/input ioctls, `skeleton_s_ctrl()`, `skeleton_probe()`, and `skeleton_remove()`. It uses `vb2_queue`, `vb2_dma_contig_memops`, and V4L2 ioctl/file helpers.

## Control Flow

Probe enables PCI, sets a 32-bit DMA mask, allocates state, requests IRQ, initializes default 720p60 timings and PAL-ish SD standard, registers the V4L2 device, creates controls, initializes the vb2 queue, initializes buffer lists/spinlock, fills `video_device`, and registers a video node. User ioctls query/set formats, standards, timings, and inputs; streaming ioctls are delegated to vb2 callbacks. Remove unregisters video/V4L2 resources and disables PCI.

## State and Persistence Behavior

Per-device state persists in `struct skeleton`. Buffer queue state is protected by `qlock`; ioctl and streaming serialization uses `lock`. Current input controls whether SDTV or HDMI timing APIs are valid. Sequence and field state update during streaming.

## Dependencies and Integration Points

It integrates with PCI driver registration, V4L2 core, vb2, DMA-contig memory, controls, events, and media user APIs.

## Risks and Edge Cases

Many hardware operations are TODO stubs, including IRQ frame completion, DMA start/stop, std/timing hardware programming, and controls. The PCI id table is empty, so it will not bind without editing. `skeleton_remove()` expects `pci_get_drvdata()` to return `v4l2_dev`, but probe does not set PCI drvdata explicitly in the shown code, which is a notable skeleton gap.

## Test Signals

Compile-test the module, add a PCI id for experimentation, run `v4l2-compliance`, exercise format/input/timing ioctls, and verify vb2 buffer setup paths reject busy/invalid state correctly.
