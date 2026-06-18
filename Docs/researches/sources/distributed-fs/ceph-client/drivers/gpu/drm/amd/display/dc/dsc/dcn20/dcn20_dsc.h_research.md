# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h

## Purpose

`dcn20_dsc.h` defines the DCN2.0 DSC hardware abstraction: register lists, shift/mask field lists, register address containers, encoded pixel formats, cached register values, the `struct dcn20_dsc` object, and exported helper prototypes shared by later DSC generations.

## Important APIs, Types, And Functions

Important definitions include `TO_DCN20_DSC`, `DSC_REG_LIST_DCN20`, `DSC_REG_LIST_SH_MASK_DCN20`, `DSC_FIELD_LIST_DCN20`, `struct dcn20_dsc_registers`, `struct dcn20_dsc_shift`, `struct dcn20_dsc_mask`, `enum dsc_pixel_format`, `struct dsc_reg_values`, and `struct dcn20_dsc`. It declares the DCN20 implementation functions and shared helpers such as `dsc_prepare_config`, `dsc_log_pps`, and `dsc_override_rc_params`.

## Control Flow

This header drives register access but has no runtime logic. Source files include it, instantiate ASIC-specific register tables from the macros, and use the shift/mask structs through register helper macros. Later generations cast or extend the DCN20 field list to reuse common DSC programming code.

## State, Dependencies, Risks, And Test Signals

The header defines in-memory and hardware-facing state: cached `dsc_reg_values`, register address tables, field masks/shifts, and the base DSC object. It depends on `dsc.h`, `dscc_types.h`, and DRM DSC types. Risks include field-list drift, duplicate field-name handling through `DSC2_SF`, and coupling between `struct dsc_reg_values` and register writers. Build coverage and register tests for PPS, interrupt, memory power, DSCCIF, and DSCRM fields are the main signals.
