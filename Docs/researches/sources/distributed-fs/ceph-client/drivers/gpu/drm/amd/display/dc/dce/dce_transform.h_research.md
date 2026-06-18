# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_transform.h

Purpose: declares the DCE transform private object, scaler/filter register maps, field metadata, helper structs, filter-type enum, and OPP/transform entry points used by DCE transform implementations.

Important types and APIs: `struct dce_transform` embeds `struct transform` and adds register/shift/mask pointers, cached filter pointers, line-buffer depth support, memory size, entry width, and `prescaler_on`. `struct dce_transform_registers` enumerates LB, SCL, DCP, CSC, gamut, regamma, memory-power, and DCE6-specific registers. `struct dce_transform_shift` and `struct dce_transform_mask` are generated from `XFM_REG_FIELD_LIST()`. API declarations include `dce_transform_construct()`, optional `dce60_transform_construct()`, `dce_transform_get_optimal_number_of_taps()`, CSC default/adjustment functions, and regamma controls.

Control flow role: generation resource files use macros such as `XFM_COMMON_REG_LIST_DCE80/100/110()` and `XFM_COMMON_MASK_SH_LIST_DCE110()` to build static descriptors, then pass them into constructors. Implementation code dereferences only those descriptor pointers via `REG()`/`FN()` helper macros.

State and persistence: persistent software state is small and per-transform: descriptor pointers, filter cache pointers, LB capacity, and capability flags. Persistent display behavior lives in hardware registers. Constants `LB_TOTAL_NUMBER_OF_ENTRIES` and `LB_BITS_PER_ENTRY` define DCE line-buffer capacity used for tap validation.

Dependencies and integration: depends on `transform.h`, AMD register macro naming, OPP/regamma enums, scaling data structures, fixed-point-derived filter tables, and conditional `CONFIG_DRM_AMD_DC_SI` for DCE6. It integrates into the broader DC resource model as the hardware-specific backing for the abstract transform interface.

Risks: the macro field list is long and shared by multiple generations, so missing or mismatched fields break register programming at compile or runtime. DCE6 variants omit some DCE110 fields, making conditional build coverage important. Test signals include compile coverage for all generation macro expansions, constructor initialization of LB constants, field/mask table completeness, and transform callers seeing the correct function table for DCE versus DCE6.
