# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_types.h` is ANR2 public threshold type for the AtomISP CSS kernel host layer. defines `ANR_PARAM_SIZE` and `struct ia_css_anr_thres` with `s16 data[13 * 64]`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_anr_thres`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR2_TYPES_H`, `ANR_PARAM_SIZE`.

defines `ANR_PARAM_SIZE` and `struct ia_css_anr_thres` with `s16 data[13 * 64]`. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The size is assumed by VMEM encoding loops. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 23 lines, 471 bytes.
