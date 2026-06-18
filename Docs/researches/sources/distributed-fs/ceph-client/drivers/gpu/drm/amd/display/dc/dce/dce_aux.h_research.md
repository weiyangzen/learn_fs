# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.h

Purpose: defines the DCE AUX engine object, register tables, mask/shift field lists, timeout constants, construction data, public native/DMUB transfer entry points, and small AUX function table used by higher-level DDC service code.

Important APIs and types: `AUX_COMMON_REG_LIST0()` and `AUX_COMMON_REG_LIST()` enumerate per-engine AUX registers and optional impedance calibration registers. `DCE_AUX_REG_FIELD_LIST()` plus DCE10/DCE/DCE12/DCN mask-list macros generate field metadata for multiple register namespaces. `struct dce_aux` stores instance, current DDC, context, delay/defer tuning, acquire-reset flag, and `struct dce_aux_funcs`. `struct aux_engine_dce110` embeds `dce_aux` and adds register/mask/shift tables plus cached register addresses and `polling_timeout_period`. Public functions include constructor/destructor/acquire, `dce_aux_transfer_raw()`, `dce_aux_transfer_dmub_raw()`, and `dce_aux_transfer_with_retries()`.

Control flow and integration: the header provides the contract used by resource pools to create AUX engines and by DDC service/link code to issue AUX payloads. Optional `configure_timeout` is installed only when the ASIC supports external AUX timeout configuration; otherwise callers must use default timing.

State and persistence: no external persistence. State is per-engine in memory and in AUX hardware registers. The register lists must match the generated ASIC register definitions, especially the presence or absence of `AUX_RESET`, `AUX_DPHY_RX_CONTROL1`, and impedance calibration fields.

Dependencies and risks: depends on GPIO service and `inc/hw/aux_engine.h`. Risks include mask-list duplication across DCE12/DCN variants, optional fields being zero on older hardware, and timeout constants being used as both hardware and software poll budgets. Test signals include successful compile/resource construction for all supported ASIC families, correct callback installation for timeout-configurable AUX engines, and validation that native/DMUB transfer entry points are reachable from DDC service.
