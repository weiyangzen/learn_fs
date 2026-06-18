# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.h

## Purpose
This header exposes AtomISP file-operation and vb2-operation entry points to the rest of the PCI driver.

## Important APIs and Types
It declares `atomisp_qbuffers_to_css()`, exports `atomisp_vb2_ops`, and exports `atomisp_fops`.

## Control Flow
`atomisp_subdev.c` installs `atomisp_vb2_ops` into the video pipe queue, and video-device setup uses `atomisp_fops`. Runtime paths call `atomisp_qbuffers_to_css()` after buffers or parameters become available.

## State and Persistence
No state is defined here. The declarations operate on subdevice, video pipe, and vb2 queue state defined elsewhere.

## Dependencies and Integration Points
Includes `atomisp_subdev.h` and is included by file ops, ioctl, and CSS compatibility code.

## Risks
The operation table declarations tightly bind queue initialization and video registration. `atomisp_qbuffers_to_css()` assumes CSS streams and locks are already prepared.

## Test Signals
Build/link validation, video-node registration, vb2 queue initialization, and runtime queueing after `buf_queue` or parameter pairing validate this header.
