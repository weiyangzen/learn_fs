# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_param.h` is BNLM ISP parameter layouts for the AtomISP CSS kernel host layer. defines VMEM LUT/array layouts and DMEM scalar denoise parameters.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct bnlm_lut`, `struct bnlm_vmem_params`, `struct bnlm_lut mu_root_lut;`, `struct bnlm_lut sad_norm_lut;`, `struct bnlm_lut sig_detail_lut;`, `struct bnlm_lut sig_rad_lut;`, `struct bnlm_lut rad_pow_lut;`, `struct bnlm_lut nl_0_lut;`, `struct bnlm_lut nl_1_lut;`, `struct bnlm_lut nl_2_lut;`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_BNLM_PARAM_H`.

defines VMEM LUT/array layouts and DMEM scalar denoise parameters. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The VMEM arrays depend on `ISP_VEC_NELEMS` and vector element width. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 56 lines, 1387 bytes.
