# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.h

Purpose: declares the DCN 3.0 HUBP interface and register field inventory used by AMDGPU Display Core to program plane fetch, tiling, DCC, VM, cursor, flip, DLG, TTU, and dmdata behavior. It extends DCN 2.0/2.1 HUBP definitions and is the base contract reused by later DCN 3.x HUBP implementations.

Important APIs and types: `HUBP_REG_LIST_DCN30()` appends `DCN_DMDATA_VM_CNTL` to the DCN 2.1 register list. `HUBP_MASK_SH_LIST_DCN30_BASE()` and `HUBP_MASK_SH_LIST_DCN30()` enumerate the register fields expected in generated shift/mask tables, including surface address, meta address, DCC, cursor, VMID, flip, vblank, and TTU fields. Exported function declarations include `hubp3_construct()`, VM aperture programming, surface flip/address programming, surface config, DLG/TTU/RQ setup, tiling, DCC, dmdata, state reads, init, tiling clear, read-line, and underflow status helpers.

Control flow: this header has no runtime flow, but it controls compile-time expansion of register tables and function pointer wiring in ASIC-specific resource code. Implementations in DCN 3.x source files call the declared helpers to update hardware through `reg_helper` macros, usually after resource construction installs a `hubp_funcs` table.

State and persistence: persistent state is hardware register state and cached `struct hubp`/`struct dcn20_hubp` fields updated by the implementations. The header exposes fields for address latching, underflow, outstanding request status, cursor state, VM fault status, and flip pending status, so omissions in the mask list can make apparently valid code write the wrong bits or skip diagnostics.

Dependencies and integration points: depends on `dcn20_hubp.h` and `dcn21_hubp.h`, plus shared DC plane, tiling, DCC, vm aperture, and DML register structs referenced by prototypes. It is consumed by DCN generation resource constructors and later HUBP variants (`dcn31`, `dcn32`, `dcn35`, `dcn42`) that compose its masks or reuse `hubp3_*` helpers.

Risks and test signals: register list drift is the main risk; generated ASIC tables must match the silicon register spec exactly. Fields such as address high/low ordering, TMZ, DCC enable, VMID, and flip/update locks have direct display correctness and hang risk. There are no local unit tests; build coverage, ASIC bring-up, Display Core register readback, underflow counters, flip tests, cursor tests, and DCC/tiling display validation are the useful signals.
