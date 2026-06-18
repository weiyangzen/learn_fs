# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe.h` is the private CSS pipe runtime state definition in the Intel AtomISP CSS driver. It defines mode-specific pipe settings for preview, video, capture, and YUV post-processing plus the central `struct ia_css_pipe` with public config/info, binaries, frames, continuous buffers, metadata buffers, pipeline, stream backpointer, and pipe number.

## Important APIs, Types, and Functions

Visible functions: `sh_css_param_update_isp_params`. Visible structs: `struct ia_css_preview_settings`, `struct ia_css_binary copy_binary;`, `struct ia_css_binary preview_binary;`, `struct ia_css_binary vf_pp_binary;`, `struct ia_css_frame *delay_frames[MAX_NUM_VIDEO_DELAY_FRAMES];`, `struct ia_css_frame *tnr_frames[NUM_VIDEO_TNR_FRAMES];`, `struct ia_css_pipe *copy_pipe;`, `struct ia_css_pipe *capture_pipe;`, `struct ia_css_capture_settings`, `struct ia_css_binary copy_binary;`. Visible enums: `enum ia_css_pipe_id		mode;`. Important macros/constants: `__IA_CSS_PIPE_H__`, `PIPE_ENTRY_EMPTY_TOKEN`, `PIPE_ENTRY_RESERVED_TOKEN`, `IA_CSS_DEFAULT_PREVIEW_SETTINGS`, `IA_CSS_DEFAULT_CAPTURE_SETTINGS`, `IA_CSS_DEFAULT_VIDEO_SETTINGS`, `IA_CSS_DEFAULT_YUVPP_SETTINGS`, `IA_CSS_DEFAULT_PIPE`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Control flow starts from public pipe creation, fills this private structure, maps queues, builds binary pipelines, updates ISP params through `sh_css_param_update_isp_params()`, and links the pipe into streams.

## State and Persistence Behavior

State is long-lived per pipe: selected binaries, owned frame structures, continuous capture frames, metadata buffers, shading/scaler resources, and SP thread mapping token.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are lifecycle leaks across mode-specific unions, stale pipe numbers, and accidental use of uninitialized union members when pipe mode changes.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 173 lines, 5957 bytes.
