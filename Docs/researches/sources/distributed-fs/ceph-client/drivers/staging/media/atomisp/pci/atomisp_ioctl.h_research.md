# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.h

## Purpose
This header exposes the AtomISP ioctl-layer public interface used by video setup, file operations, and CSS/buffer code.

## Important APIs and Types
It declares `atomisp_output_fmts[]`, format bridge lookup helpers, `atomisp_pipe_check()`, `atomisp_alloc_css_stat_bufs()`, vb2 stream callbacks, and `atomisp_ioctl_ops`.

## Control Flow
Video initialization attaches `atomisp_ioctl_ops` to the capture node. File operations call `atomisp_pipe_check()` from buffer queueing and use stream callbacks through vb2. Queue setup calls stat-buffer allocation after CSS frame info is available.

## State and Persistence
No state is defined here. Functions operate on `atomisp_device`, `atomisp_video_pipe`, `atomisp_sub_device`, and vb2 queue state.

## Dependencies and Integration Points
Includes `ia_css.h` and forward-declares AtomISP structs. It binds ioctl, file-op, CSS, and video-node modules.

## Risks
`atomisp_pipe_check()` requires `pipe->isp->mutex` to be held. Start/stop signatures are tied to vb2 APIs.

## Test Signals
Build/link validation, ioctl table registration, vb2 stream callbacks, queue setup stat allocation, and busy settings-change rejection.
