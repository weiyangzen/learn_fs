# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.c` is BNLM host encoders for the AtomISP CSS kernel host layer. builds replicated VMEM LUT blocks, fixed division/intercept/power tables, and DMEM scalar fields for Bayer Non-Linear Mean denoise.

## Important APIs, Types, and Functions

Visible functions: `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`. Visible structs: `struct bnlm_vmem_params *to,`, `struct bnlm_dmem_params *to,`. Visible enums: none visible in this file. Important macros/constants: `BNLM_DIV_LUT_SIZE`.

builds replicated VMEM LUT blocks, fixed division/intercept/power tables, and DMEM scalar fields for Bayer Non-Linear Mean denoise. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The LUT helper asserts monotonic thresholds and 2..16 entry counts. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 188 lines, 6155 bytes.
