# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.h

## Purpose
This header declares the decoder module's integration points for the MFC core open path.

## Important APIs, Types, and Functions
It declares `get_dec_codec_ops()`, `get_dec_queue_ops()`, `get_dec_v4l2_ioctl_ops()`, `s5p_mfc_dec_ctrls_setup()`, `s5p_mfc_dec_ctrls_delete()`, and `s5p_mfc_dec_init()`.

## Control Flow and State
There is no implementation flow. The core calls these functions when opening a decoder video node: initialize default decode formats, attach decoder controls, and install decoder vb2 and ioctl operations.

## Dependencies and Integration Points
The declarations rely on types from `s5p_mfc_common.h`, included by users before this header in the current source arrangement. It connects `s5p_mfc.c` to `s5p_mfc_dec.c`.

## Risks
Because this header does not include `s5p_mfc_common.h` itself, it assumes include ordering provides `struct s5p_mfc_ctx`, `struct s5p_mfc_codec_ops`, `struct vb2_ops`, and `struct v4l2_ioctl_ops`. That is true in current users but could be fragile for new include sites.

## Test Signals
Compile coverage validates include ordering. Runtime decoder open should call init/control setup successfully and use returned ioctl/queue ops for all decode operations.
