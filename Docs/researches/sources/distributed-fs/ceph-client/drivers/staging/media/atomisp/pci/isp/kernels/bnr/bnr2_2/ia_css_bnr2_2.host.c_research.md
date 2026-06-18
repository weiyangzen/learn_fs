# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.c` is BNR2.2 host encoder for the AtomISP CSS kernel host layer. defines default BNR2.2 tuning, copies all public gain/threshold/detail fields into DMEM, and traces each field when debug is enabled.

## Important APIs, Types, and Functions

Visible functions: `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`. Visible structs: `struct sh_css_isp_bnr2_2_params *to,`. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

defines default BNR2.2 tuning, copies all public gain/threshold/detail fields into DMEM, and traces each field when debug is enabled. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

It ignores `size`, so correctness depends on generated offsets selecting the right parameter block. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 123 lines, 3937 bytes.
