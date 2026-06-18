# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.h

Purpose: this header defines the DCN 3.5 DCCG register and field contract. It extends DCN 3.1.4 with DPP clock control, additional gate-disable registers, global FCG control, `SYMCLK[A-E]` clock-enable registers, and PSP symbol-clock control.

Important APIs and types: `DCCG_REG_LIST_DCN35()` includes `DCCG_REG_LIST_DCN314()` and adds `DPPCLK_CTRL`, `DCCG_GATE_DISABLE_CNTL4/5/6`, `DCCG_GLOBAL_FGCG_REP_CNTL`, `SYMCLKA` through `SYMCLKE_CLOCK_ENABLE`, and `SYMCLK_PSP_CNTL`. `DCCG_MASK_SH_LIST_DCN35(mask_sh)` maps DPP enables, PHY `*_EN` and source fields, DP stream source/enables, DSC enables and DTO fields, `SYMCLK32`, OTG DTO/add/drop, DTBCLK_P, DENTIST, fine-grain clock gating, frontend/backend `SYMCLK` fields, root gates, FIFO error-detection fields, and DISPCLK ramp fields. Prototypes expose creation, init, DPP DTO/root control, global FCG, DP stream root gating, HDMI stream root gating declaration, DSC, HPO SE disable, and `SYMCLK` SE enable/disable.

Control flow: the header drives the C file by supplying all fields needed for active root-gating and clock-source updates. It inherits DCN 3.1.4 definitions and adds the DCN 3.5 fields required by `dccg35_funcs`.

State and persistence: no mutable state is stored here. The macros initialize static register/shift/mask data used by `struct dcn_dccg` instances.

Dependencies and integration: it includes `dcn314/dcn314_dccg.h`, so it inherits DCN 3.1.4 and DCN 3.1 declarations. Resource files for DCN 3.5 ASICs must instantiate both register and mask lists to make all active callbacks safe.

Risks: there is a prototype for `dccg35_set_hdmistreamclk_root_clock_gating()` but no implementation in the researched C file, so consumers must not call it unless another compilation unit supplies it. The field list is large and manually maintained, making omissions likely when hardware registers evolve. Duplicate or repeated field mappings inherited from earlier headers remain present. Because the C file also contains an inactive new callback table, this header supports more fields than the active table uses.

Test signals: compile/link the declared functions, instantiate the register/mask macros in a DCN 3.5 resource table, and runtime-test DPP/DSC/DPSTREAM/DTBCLK/SYMCLK/PHY root-gate fields plus FIFO error-detection and global FCG controls.
