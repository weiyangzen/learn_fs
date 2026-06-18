# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.h

Purpose: defines DCN1.0 MPC register lists, field metadata, object layout, and exported base MPCC tree operations.

Important APIs/types: `TO_DCN10_MPC`, `MPC_COMMON_REG_LIST_DCN1_0`, `MPC_OUT_MUX_COMMON_REG_LIST_DCN1_0`, `MPC_COMMON_REG_VARIABLE_LIST`, `MPC_COMMON_MASK_SH_LIST_DCN1_0`, and `MPC_REG_FIELD_LIST`. Defines `struct dcn_mpc_registers`, `dcn_mpc_shift`, `dcn_mpc_mask`, and `struct dcn10_mpc`.

Control flow/integration: resource code instantiates register/mask/shift data and calls `dcn10_mpc_construct`; later generations can reuse exported `mpc1_*` functions for tree management.

State/persistence: object state includes generic `struct mpc`, `mpcc_in_use_mask`, `num_mpcc`, and register metadata pointers.

Dependencies: includes `mpc.h`, which defines generic MPC/MPCC trees, blending config, stereo config, and function table contracts.

Risks: generation-specific derived structs often rely on DCN10 layout compatibility. Register array sizes must match `MAX_MPCC`/`MAX_OPP`, and callers must not use unavailable mux registers.

Test signals: compile-time register list generation, DCN10 construction, and reuse by DCN20+ implementations.
