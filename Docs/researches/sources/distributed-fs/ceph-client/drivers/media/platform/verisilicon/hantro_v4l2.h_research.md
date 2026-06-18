# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.h

## Purpose
`hantro_v4l2.h` declares the public V4L2-facing helpers and operation tables implemented by `hantro_v4l2.c`. It is the small interface used by the Hantro core and codec setup code to reset default formats, query bit depth, and bind ioctl/vb2 operations to video devices.

## Important APIs, Types, And Functions
The header defines `HANTRO_FORCE_POSTPROC` and `HANTRO_AUTO_POSTPROC` as boolean policy values passed into raw-format selection. It declares `hantro_ioctl_ops`, `hantro_queue_ops`, `hantro_reset_raw_fmt`, `hantro_reset_fmts`, `hantro_get_format_depth`, and `hantro_get_default_fmt`.

## Control Flow
Driver initialization uses the exported operation tables when registering the V4L2 mem2mem video device. Context setup and format reset paths call `hantro_reset_fmts` or `hantro_reset_raw_fmt`; codec-specific or postprocessor-aware paths use `hantro_get_default_fmt` and `hantro_get_format_depth` to select compatible raw formats.

## State And Persistence
The header defines no storage. It exposes functions that mutate per-context format state in `struct hantro_ctx`, including source/destination formats, bit depth, and postprocessing flags.

## Dependencies And Integration Points
It includes `hantro.h` for `struct hantro_ctx` and `struct hantro_fmt`, and relies on V4L2/vb2 operation types made visible through that driver context. It is included by Hantro core files that need to wire device operations or reset format state.

## Risks
Because the postprocessor policy macros are plain booleans, callers must pass them in the intended semantic position; swapping them with unrelated boolean arguments would be easy during refactors. Any signature change here affects multiple driver registration and context setup paths.

## Test Signals
Build coverage is the main direct signal. Runtime validation comes from successful V4L2 device registration and format reset behavior on open, `S_FMT`, and codec changes.
