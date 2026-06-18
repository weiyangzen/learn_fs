# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_common.h

## Purpose
This is the central shared contract for the MFC driver. It defines codec ids, interrupt ids, instance and queue states, buffer wrappers, PM and variant data, device and context state structures, encoder parameter structures, pixel format descriptors, control descriptors, hardware-call helpers, version predicates, and common helper prototypes.

## Important APIs, Types, and Constants
Major types include `struct s5p_mfc_dev`, `struct s5p_mfc_ctx`, `struct s5p_mfc_buf`, `struct s5p_mfc_pm`, `struct s5p_mfc_variant`, `struct s5p_mfc_priv_buf`, per-version buffer-size structs, `struct s5p_mfc_enc_params` and codec-specific parameter structs, `struct s5p_mfc_codec_ops`, `struct s5p_mfc_fmt`, and `struct mfc_control`. Important macros include `mfc_read`, `mfc_write`, `s5p_mfc_hw_call`, `file_to_ctx`, `ctrl_to_ctx`, version predicates, version bit masks, limits such as `MFC_NUM_CONTEXTS`, `MFC_MAX_BUFFERS`, `MFC_INT_TIMEOUT`, and interrupt/code constants.

## Control Flow and State
There is no executable implementation except small inline accessors/macros. It defines the state machine used throughout the driver: `MFCINST_INIT`, `GOT_INST`, `HEAD_PARSED`, `BUFS_SET`, `RUNNING`, `FINISHING`, `FINISHED`, `RETURN_INST`, `ERROR`, `ABORT`, `FLUSH`, and resolution-change states. It also defines per-queue state transitions from free to requested, queried, and mmaped.

## Dependencies and Integration Points
It includes V4L2, vb2, platform-device, register headers, and DMA-contig definitions. Every MFC source file in this subset relies on these structures. Hardware operation and command tables attach to `struct s5p_mfc_dev`, while decoder/encoder ioctl and queue code attach to `struct s5p_mfc_ctx`.

## Risks
This header has high blast radius. Structure field changes can break locking, vb2 callback assumptions, firmware ABI programming, and PM paths. The `s5p_mfc_hw_call()` macro derives a fallback type from `f->op(args)`, so it depends on valid function-pointer expressions at compile time. Version predicates assume `dev->variant` is valid.

## Test Signals
Build coverage across all MFC objects is essential. Runtime signals include stable context lifecycle, state-machine transitions under decode/encode/EOS/resolution-change, correct version-gated format exposure, control propagation into context fields, and no lockdep issues around `mfc_mutex`, `irqlock`, and `condlock`.
