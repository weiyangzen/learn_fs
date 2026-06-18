# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.h` is BH host declarations for the AtomISP CSS kernel host layer. declares histogram decode and parameter encode helpers.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_3a_rgby_output *out_ptr,`, `struct sh_css_isp_bh_params *to,`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_BH_HOST_H`.

declares histogram decode and parameter encode helpers. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Generated params code marks BH DMEM/HMEM dirty and calls the encode helper. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 24 lines, 542 bytes.
