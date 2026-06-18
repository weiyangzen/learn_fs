# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_ipp.h

## Purpose
This header defines the DCE input pixel processor wrapper used by the AMD DC hardware abstraction. The IPP block owns cursor registers, graphics prescale controls, input gamma LUT programming fields, degamma mode fields, and the LUT memory power-control field for DCE generations that expose it. It does not implement behavior directly; it supplies register lists, shift/mask layouts, the concrete `struct dce_ipp`, and constructor/destructor prototypes consumed by generation-specific resource creation code.

## Important APIs, Types, and Macros
`TO_DCE_IPP()` casts the abstract `struct input_pixel_processor` to `struct dce_ipp`. `IPP_COMMON_REG_LIST_DCE_BASE()`, `IPP_DCE100_REG_LIST_DCE_BASE()`, and `IPP_DCE110_REG_LIST_DCE_BASE()` enumerate per-instance DCP/DCFE/CRTC registers. `IPP_COMMON_MASK_SH_LIST_DCE_COMMON_BASE()`, `IPP_DCE100_MASK_SH_LIST_DCE_COMMON_BASE()`, `IPP_DCE120_MASK_SH_LIST_SOC_BASE()`, and optional `IPP_DCE60_MASK_SH_LIST_DCE_COMMON_BASE()` generate field shift/mask initializers. `struct dce_ipp_registers`, `struct dce_ipp_shift`, and `struct dce_ipp_mask` carry the resolved MMIO addresses and field metadata. `dce_ipp_construct()`, optional `dce60_ipp_construct()`, and `dce_ipp_destroy()` are the public lifecycle hooks.

## Control Flow and State
The control path is indirect: resource builders instantiate a `dce_ipp`, pass generation-specific register tables and masks into the constructor, and later IPP operations use the stored metadata to program cursor, prescale, gamma, and degamma registers. Persistent state is limited to pointers to immutable register metadata plus the embedded base object and DC context inherited through the base.

## Dependencies and Integration Points
The file depends on `ipp.h`, Linux `container_of`, register table macros such as `SRI`, and generated ASIC register definitions included by the translation units that instantiate these macros. It integrates with the DC resource pool and the `input_pixel_processor` vtable implemented elsewhere.

## Risks and Test Signals
The main risk is register-table skew across DCE6, DCE10/11, and DCE12: a missing or mismatched field silently breaks cursor, LUT, or degamma programming. DCE12 uses SoC-style prefixed field names such as `DCP0_`, while older paths use block-local names. Useful tests are compile coverage for all enabled ASIC configs, cursor enable/address updates, LUT load/regamma smoke tests, and display validation on DCE6 and DCE12 hardware or emulation.
