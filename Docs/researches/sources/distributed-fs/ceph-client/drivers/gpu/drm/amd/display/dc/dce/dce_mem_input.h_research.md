# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_mem_input.h

## Purpose
This header defines the DCE memory input object and its register/field metadata. It maps DCP graphics, DMIF pipe arbitration/watermark, VM PTE, DCHUB, and MC_HUB fields used by `dce_mem_input.c`.

## Important APIs, Types, and Macros
`TO_DCE_MEM_INPUT()` casts from `struct mem_input`. Register lists include `MI_DCE_BASE_REG_LIST()`, `MI_DCE_PTE_REG_LIST()`, optional `MI_DCE6_REG_LIST()`, `MI_DCE8_REG_LIST()`, `MI_DCE11_2_REG_LIST()`, `MI_DCE11_REG_LIST()`, and `MI_DCE12_REG_LIST()`. Field list macros cover DCP surface control/address/update, GFX6/GFX8/GFX9 tiling, PTE control, DMIF watermarks, DCE12 low-power controls, and DCHUB aperture fields. `struct dce_mem_input_registers`, `struct dce_mem_input_shift`, and `struct dce_mem_input_mask` store resolved MMIO metadata. `struct dce_mem_input_wa` currently carries `single_head_rdreq_dmif_limit`.

## Control Flow and State
The header defines no executable control flow, but it determines which register fields can be used by each generation-specific constructor. State is the base `mem_input`, immutable register metadata pointers, and a small workaround state object.

## Dependencies and Integration Points
It depends on `dc_hw_types.h`, `mem_input.h`, generated register macros (`SRI`, `SR`, `SF`), and optional `CONFIG_DRM_AMD_DC_SI`. Resource construction code instantiates these macros and then calls the constructors declared here.

## Risks and Test Signals
The broad macro surface is easy to desynchronize from generated register headers or ASIC capabilities. DCE12 uses prefixed `DCP0_` and `DMIF_PG0_` names and adds DCHUB aperture registers, while older paths use DCP/DMIF local fields. Compile tests for every enabled DCE generation, plus runtime plane programming across linear/tiled scanout, are the key signals.
