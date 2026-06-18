# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h

Purpose: Declares DCN3.1 HPO DP link encoder register lists, field tables, concrete object layout, constructor, and exported helper functions.

Important APIs and types: `struct dcn31_hpo_dp_link_encoder` embeds `hpo_dp_link_encoder` and stores register, shift, and mask tables. `DCN3_1_HPO_DP_LINK_ENC_REG_LIST`, `REGS`, `MASK_SH_LIST`, and field-list macros define all DPHY/SAT/VC/test-pattern/RDPCSTX registers used by the implementation. Function declarations expose PHY control, test patterns, SAT updates, VCP size, state readback, FFE, and allocation-row fill.

Control flow: resource construction code expands the macros to create per-instance register tables, then calls `hpo_dp_link_encoder31_construct`. Runtime callers access behavior through the base vtable while generation-specific code can call helpers directly.

State and persistence: the struct stores immutable register metadata after construction and mutable base state for instance/transmitter/HPD. Register values persist in hardware.

Dependencies and integration: includes `link_encoder.h` and is consumed by DCN31 resources plus DCN32/DCN42 implementations that reuse the same concrete struct and many functions.

Risks and test signals: register/field macro drift can break multiple generations. Compile-time generated tables are the main guard; runtime state readback should be compared against writes for SAT, VC rate, link mode, and lane count.
