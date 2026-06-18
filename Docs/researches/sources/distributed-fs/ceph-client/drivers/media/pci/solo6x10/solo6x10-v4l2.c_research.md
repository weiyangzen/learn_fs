<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2.c

## Purpose
`solo6x10-v4l2.c` implements the live/raw V4L2 display capture node for SOLO6x10 cards, returning UYVY frames from the display SDRAM page ring and allowing users to select camera or multi-view inputs.

## Important APIs, Types, and Functions
Display window helpers include `solo_win_setup()`, `solo_v4l2_ch()`, and `solo_v4l2_set_ch()`. Buffer flow is `solo_video_in_isr()`, `solo_thread()`, `solo_thread_try()`, and `solo_fillbuf()`. V4L2 ioctls cover querycap, input enumeration/selection, format get/try/set, standard get/set, and motion trace control. `solo_set_video_type()` coordinates global PAL/NTSC reconfiguration across display, encoder, TW28, and encoder V4L2 modes.

## Control Flow
Initialization allocates a video device, creates a V4L2 control handler, initializes a contiguous-DMA vb2 queue, cycles through all channels to erase stale display content, selects input 0, and registers the display node. Streaming starts a display thread and enables video-input IRQ. The thread wakes on IRQs or timeout, checks whether the hardware display write page changed, dequeues a vb2 buffer, and either fills blank erase frames or performs a repeated P2M DMA from display SDRAM to the buffer. Input changes temporarily enable display erase, disable the old channel/multiview window, enable the new layout, and wait through erase frames.

## State and Persistence
Display state in `struct solo_dev` includes current input, erasing counters, old write page, sequence counter, active vb2 list, queue lock, display thread wait queue, and video geometry/standard fields. It is runtime-only and rebuilt during probe or standard changes.

## Dependencies and Integration Points
The file depends on V4L2/vb2 DMA-contig APIs, P2M DMA, TW28 video status, display/encoder/TW28 reinit functions, and SOLO video input/output registers. It is the standard-changing coordinator for encoder nodes.

## Risks and Edge Cases
`solo_set_video_type()` reinitializes multiple subsystems after only checking vb2 busy state; failures from `solo_disp_init()`, `solo_enc_init()`, and `solo_tw28_init()` are not propagated. Input switching busy-waits through erase frames. The display thread uses page changes as the only new-frame signal, so missed or repeated page values affect capture cadence.

## Test Signals
Check `/dev/video` registration, UYVY format reporting, camera and 4-up/16-up input enumeration, video-loss status, streaming with mmap/userptr/read, PAL/NTSC switching while idle and rejection while busy, motion trace register updates, frame blanking after input changes, and clean streamoff buffer return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2.c -->
