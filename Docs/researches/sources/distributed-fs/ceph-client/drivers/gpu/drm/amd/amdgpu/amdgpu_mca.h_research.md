## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.h

Purpose: declares MCA register field helpers, MCA IP/error enums, bank data structures, RAS wrapper structures, SMU callback interface, and exported MCA/RAS functions.

Important APIs/types: `MCA_REG_FIELD()` and `MCA_REG__*` macros decode status, misc, and syndrome fields. `enum amdgpu_mca_ip` identifies PSP, SDMA, GC, SMU, MP5, UMC, and XGMI PCS sources. `enum amdgpu_mca_error_type` separates UE, CE, and deferred errors. `struct mca_bank_entry` stores bank index, type, IP, topology info, and up to 16 registers. `struct amdgpu_mca_smu_funcs` defines SMU hooks for debug mode, valid counts, bank reads, and count parsing.

Control flow contract: ASIC/SMU code installs `amdgpu_mca_smu_funcs`; RAS query paths call `amdgpu_mca_smu_log_ras_error()` or lower-level query helpers. RAS block init functions attach MP0/MP1/MPIO blocks to the RAS framework.

State and persistence: `struct amdgpu_mca` holds block interfaces, SMU funcs, caches for UE/CE classes, and `ue_update_flag`. The cache is volatile runtime state used to bridge asynchronous parsing/accounting.

Dependencies/integration: includes `amdgpu_ras.h`; expects `ras_err_data`, `ras_query_context`, `dentry`, and device definitions from broader AMDGPU/RAS code.

Risks: field macros depend on stable MCA register layouts. `AMDGPU_MCA_ERROR_TYPE_DE` is used as an array bound for caches, so enum ordering matters. SMU callback max counts must match firmware-provided bank arrays.

Test signals: compile coverage for SMU providers, field decode unit checks, RAS block registration, and MCA error accounting tests across CE/UE/deferred types.
