# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.h` is the generated parameter id and memory-offset contract in the Intel AtomISP CSS driver. It defines `enum ia_css_parameter_ids`, `struct ia_css_memory_offsets`, and, when `IA_CSS_INCLUDE_PARAMETERS` is set, declarations for the process table plus generated config setters.

## Important APIs, Types, and Functions

Visible functions: `ia_css_set_dp_config`, `ia_css_set_wb_config`, `ia_css_set_tnr_config`, `ia_css_set_ob_config`, `ia_css_set_de_config`, `ia_css_set_anr_config`, `ia_css_set_anr2_config`, `ia_css_set_ce_config`, `ia_css_set_ecd_config`, `ia_css_set_ynr_config`. Visible structs: `struct ia_css_memory_offsets`, `struct`, `struct ia_css_isp_parameter aa;`, `struct ia_css_isp_parameter anr;`, `struct ia_css_isp_parameter bh;`, `struct ia_css_isp_parameter cnr;`, `struct ia_css_isp_parameter crop;`, `struct ia_css_isp_parameter csc;`, `struct ia_css_isp_parameter dp;`, `struct ia_css_isp_parameter bnr;`. Visible enums: `enum ia_css_parameter_ids`. Important macros/constants: `_IA_CSS_ISP_PARAM_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Control flow is indirect: pipeline code indexes `ia_css_kernel_process_param[id]`, and each function uses the matching member in `mem_offsets.offsets.param` to locate the kernel's parameter block in the binary memory images.

## State and Persistence Behavior

No runtime state is stored here, but the header fixes the ABI between generated binary metadata, host parameter cache, and kernel-specific encoders.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

The main risk is generated-order mismatch. Adding or reordering ids requires regenerating the process table, offset structs, and every binary metadata producer in lockstep.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 383 lines, 10960 bytes.
