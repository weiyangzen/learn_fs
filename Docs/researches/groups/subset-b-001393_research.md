# subset-b-001393 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn31/dcn31_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn31/dcn31_dccg.c

Purpose: this file implements the DCN 3.1 Display Clock Generator (DCCG) backend. It creates a `struct dccg` object backed by `struct dcn_dccg`, wires the DC-wide `dccg_funcs` table, and programs DPP clock DTOs, DP stream clocks, HPO symbol clocks, PHY symbol clocks, DTB/audio DTOs, DSC clock DTOs, OTG pixel add/drop controls, DISPCLK change mode, and DCCG register-state capture.

Important APIs and functions: `dccg31_create()` allocates and initializes the object. `dccg31_update_dpp_dto()` derives DPP DTO phase/modulo from `dccg->ref_dppclk` and requested DPP clock, while respecting `dccg->dpp_clock_gated[]`. `dccg31_set_dpstreamclk()` selects refclock versus a live DP stream clock by calling private enable/disable helpers. `dccg31_enable_symclk32_se()`, `dccg31_disable_symclk32_se()`, `dccg31_enable_symclk32_le()`, and `dccg31_disable_symclk32_le()` route HPO stream/link encoder `SYMCLK32` sources. `dccg31_set_physymclk()` forces PHY symbol clocks on or releases them. `dccg31_set_dtbclk_dto()` handles OTG pixel-valid DTO generation, including ODM and YCbCr/DSC divisors. `dccg31_set_audio_dtbclk_dto()` programs the audio DTB DTO. `dccg31_disable_dscclk()` and `dccg31_enable_dscclk()` use DTO programming to gate or restore DSC clocks. `dccg31_read_reg_state()` snapshots a broad set of DCCG registers for diagnostics.

Control flow: mode programming enters through the `dccg31_funcs` callbacks. DPP DTO updates skip stopped DPP pipes, compute an 8-bit phase over `0xff` modulo, clamp overflows, write `DPPCLK_DTO_PARAM[dpp_inst]`, and toggle `DPPCLK_DTO_ENABLE`. DP stream clock setup treats `REFCLK` as disabled and any other stream source as enabled for the OTG pipe. HPO SE/LE and PHY routines use switch statements over instance numbers and trip `BREAK_TO_DEBUGGER()` for invalid instances. DTB DTO enable computes the required DTB rate based on ODM and pixel encoding, writes modulo/phase, enables the DTO, waits for `DTBCLKDTO_ENABLE_STATUS`, then selects DTO as the pipe source; disable clears the source and DTO registers.

State and persistence: all state is volatile kernel/device state. The file mutates DCCG MMIO registers through `REG_*` macros, updates `dccg->pipe_dppclk_khz[]`, and reads debug gating bits from `dccg->ctx->dc->debug.root_clock_optimization`. It has no on-disk persistence. Hardware state is expected to be recreated by DC resource creation and init paths after reset/resume.

Dependencies and integration: the implementation depends on `reg_helper.h`, `core_types.h`, `dcn31_dccg.h`, older `dcn20` helper callbacks, Yellow Carp ASIC IDs for a PHY clock mux workaround, DCCG register/shift/mask tables supplied by resource construction, and common DC timing structures such as `dtbclk_dto_params`. Integration is via `dccg31_create()` returning a `struct dccg *` with `base->funcs = &dccg31_funcs`.

Risks: several callbacks assume validated instance indices and only debug-break on invalid input, so production behavior can become a silent no-op after the break path. DTB/DSC programming order is hardware-sensitive, especially the wait for DTO enable before selecting the pipe DTO source. `get_phy_mux_symclk()` remaps Yellow Carp B0 PHY C/D sources to F/G; removing it could regress that ASIC. `dccg31_read_reg_state()` reads many registers unconditionally, so register-list mismatches in later ASIC tables can turn diagnostics into invalid reads.

Test signals: validate DPP DTO phase/modulo for normal, zero, and over-reference requests; root-clock-optimization toggles for DP stream, HPO SE/LE, PHY, and DSC clocks; DTB DTO selection for ODM 4:1, ODM 2:1, YCbCr420, DSC 422, and ordinary modes; Yellow Carp B0 PHY source remapping; OTG add/drop pixel writes; DISPCLK ramping versus non-ramping mode writes; and register-state capture on supported DCN 3.1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn31/dcn31_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn31/dcn31_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn31/dcn31_dccg.h

Purpose: this header declares the DCN 3.1 DCCG register surface and exported helpers used by DCN 3.1 and later DCCG variants. It defines the register list macro, the shift/mask list macro, and the public function prototypes implemented in `dcn31_dccg.c`.

Important APIs and types: `DCCG_REG_LIST_DCN31()` enumerates DPP DTO, HDMI character clock, PHY symbol clock, DP stream clock, HPO `SYMCLK32`, OTG pixel rate, DTB DTO, audio DTO, dentist DISPCLK, DSC DTO, gate-disable, memory power, and time-base registers. `DCCG_MASK_SH_LIST_DCN31(mask_sh)` enumerates fields for those registers, including array-style fields for DPP and OTG instances. Public prototypes expose create/init, DPP DTO, DP stream, HPO SE/LE, PHY, DTB/audio DTO, OTG pixel add/drop, DISPCLK mode, DSC clock, and register-state callbacks.

Control flow: the header is declarative, but it drives control flow by determining which register addresses and fields are available to `REG_UPDATE`, `REG_SET`, `REG_WAIT`, and `REG_READ` calls in the C file. Later headers include it and reuse many of its function declarations and callbacks.

State and persistence: the header owns no runtime state. Its macros populate constant `dccg_registers`, `dccg_shift`, and `dccg_mask` tables elsewhere in the display driver; those tables are then referenced by live `struct dcn_dccg` objects.

Dependencies and integration: it includes `dcn30/dcn30_dccg.h`, so it builds on common DCCG structures and enums such as `streamclk_source`, `phyd32clk_clock_source`, `physymclk_clock_source`, `dtbclk_dto_params`, and `dcn_dccg_reg_state`. It is a compatibility layer for `dcn314`, `dcn32`, `dcn35`, `dcn401`, and `dcn42` code that imports DCN 3.1 helpers.

Risks: register and field macro names must match generated ASIC headers exactly; small naming drift breaks compilation or, worse, wires a field to the wrong bit. The register list omits DCN 3.5/4.x additions, so later variants must extend rather than blindly reuse it. Several prototypes are reused across ASIC generations, so signature changes have broad blast radius.

Test signals: compile coverage should instantiate `DCCG_REG_LIST_DCN31()` and `DCCG_MASK_SH_LIST_DCN31()` in a real resource table, link all declared functions, and boot a DCN 3.1 path that exercises DPP, DP stream, HPO, PHY, DTB/audio, DSC, and diagnostic callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn31/dcn31_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn314/dcn314_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn314/dcn314_dccg.c

Purpose: this file implements the DCN 3.1.4 DCCG variant by reusing most DCN 3.1 callbacks and overriding the paths where DCN 3.1.4 differs: DIO FIFO resync, OTG pixel-rate divisors, DTBCLK_P source selection, DTBCLK DTO programming, DP stream clock routing, valid-pixel-rate setup, and DPP root clock control.

Important APIs and functions: `dccg314_create()` constructs the object and installs `dccg314_funcs`. `dccg314_trigger_dio_fifo_resync()` copies `DENTIST_DISPCLK_RDIVIDER` to `DENTIST_DISPCLK_WDIVIDER`. `dccg314_get_pixel_rate_div()` and `dccg314_set_pixel_rate_div()` read/program per-OTG K1/K2 pixel-rate divider fields. `dccg314_set_dtbclk_p_src()` selects DPREFCLK or DTBCLK0 into `DTBCLK_P#` and toggles `DTBCLK_P#_EN`. `dccg314_set_dtbclk_dto()` programs the HPO DTB DTO at one quarter of pixel clock. `dccg314_set_dpstreamclk()` routes each HPO DP stream clock from an OTG instance. `dccg314_dpp_root_clock_control()` turns DPP clocks on/off using DTO phase/modulo and `DPPCLK_DTO_ENABLE`.

Control flow: init disables all four HPO SE `SYMCLK32` sources, optionally disables two LE clocks, disables DP stream clocks by routing them to `REFCLK`, and releases PHY symbol clocks. DTB DTO enable writes modulo as `ref_dtbclk_khz * 1000`, phase as `(pixclk_khz / 4) * 1000`, enables the DTO, waits for enable status, sets pixel dividers to 1:1, then selects DTO source `2`. Disable clears the DTO and selects source `1`. DPP root-clock control checks `dccg->dpp_clock_gated[]` to avoid duplicate work, then either leaves phase/modulo at `0xff/0xff` with DTO disabled for live clocking or enables a zero-Hz DTO with phase `0`, modulo `1` for gated clocks.

State and persistence: state lives in hardware registers and `dccg->dpp_clock_gated[]`. The file records no persistent configuration and relies on display resource construction to provide the DCN 3.1.4 register/field tables.

Dependencies and integration: it includes `dcn31_dccg.h` for shared callbacks, `dcn314_dccg.h` for DCN 3.1.4 register definitions, and `dcn20_dccg.h` for older common helpers. The callback table combines local overrides with `dccg31_*` and `dccg2_*` functions, so integration depends on those cross-generation functions preserving semantics.

Risks: `dccg314_set_dtbclk_dto()` assumes DTO output is always pixel rate divided by four; modes needing other divisors rely on separate pixel-rate programming. Pixel divider `PIXEL_RATE_DIV_NA` is explicitly rejected because the register fields cannot hold it. Resync writes WDIVIDER even if RDIVIDER is zero, unlike DCN 3.2, which may be hardware-specific. DP stream source selection uses `dp_hpo_inst` rather than OTG as the register instance, so caller instance mapping must be correct.

Test signals: exercise DP HPO stream clock enable/disable for all four instances, DTBCLK_P source selection for `REFCLK` and `DTBCLK0`, DTB DTO enable/disable and enable-status wait, K1/K2 divider reads and writes, DIO FIFO resync, DPP root gating state transitions, and the inherited DCN 3.1 HPO/PHY/DSC/audio callbacks on DCN 3.1.4 register tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn314/dcn314_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn314/dcn314_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn314/dcn314_dccg.h

Purpose: this header defines the DCN 3.1.4 DCCG register and field macros and declares the DCN 3.1.4 creation and DP stream clock entry points.

Important APIs and types: `DCCG_REG_LIST_DCN314()` extends the DCN 3.1 register set with `DSCCLK3_DTO_PARAM`, `OTG_PIXEL_RATE_DIV`, and `DTBCLK_P_CNTL`. `DCCG_MASK_SH_LIST_DCN314_COMMON(mask_sh)` defines shared field mappings for DPP DTO DB enable, DP stream clock enable/source, `SYMCLK32`, OTG DTO, pixel dividers, DTBCLK_P, audio DTO source, dentist controls, DSC DTO parameters, and root-gating fields. `DCCG_MASK_SH_LIST_DCN314(mask_sh)` adds DPP DTO enable, PHY force fields, HDMI stream DTO force disable, DSC DTO enable, PHY gate-disable, and dentist read/write divider fields. It declares `dccg314_create()` and `dccg314_set_dpstreamclk()`.

Control flow: the macro tables are consumed by resource files to populate register/shift/mask structures used by `dcn314_dccg.c`. The C implementation then selects local or inherited callbacks based on the `dccg314_funcs` table.

State and persistence: no runtime state is owned here. The macros produce static register metadata; live state remains in hardware registers and `struct dccg`.

Dependencies and integration: the header includes `dcn31/dcn31_dccg.h` and redefines `DCCG_SFII` for instance field expansion. It is part of the resource-construction contract for DCN 3.1.4 display hardware and depends on generated register-field names matching the macro concatenations.

Risks: the mask list contains a duplicate `OTG3_PIXEL_RATE_DIVK2` entry; while likely harmless in generated initializer ordering, it is a maintenance hazard. Field-list omissions will surface as callback failures when the shared DCN 3.1 functions access registers that the DCN 3.1.4 tables did not define. Because this header pulls in DCN 3.1 declarations, incompatible enum or callback changes propagate here.

Test signals: compile a DCN 3.1.4 resource table using the register and mask macros, verify the resulting DCCG object can call `dccg314_set_dpstreamclk()`, and boot-test pixel divider, DTBCLK_P, DSC3, and dentist divider fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn314/dcn314_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.c

Purpose: this file implements the DCN 3.2 DCCG variant. It is structurally close to DCN 3.1.4 but chooses DCN 2 DPP DTO behavior, adds a guarded DIO FIFO resync, treats HDMI idle pixel DTO source specially, and always sources DTBCLK_P from DTBCLK0 for DP stream clock setup.

Important APIs and functions: `dccg32_create()` installs `dccg32_funcs`. Local helpers cover DIO FIFO resync, K1/K2 pixel-rate divider read/write, DTBCLK_P source selection, DTBCLK DTO programming, valid pixel rate setup, DCCG reference frequency, DP stream clock routing, and OTG add/drop pixel writes. The callback table uses `dccg2_update_dpp_dto`, `dccg31_init`, `dccg31_*` HPO/PHY/audio helpers, and `dccg2_*` compatibility callbacks.

Control flow: `dccg32_trigger_dio_fifo_resync()` reads `DENTIST_DISPCLK_RDIVIDER` and writes it to `WDIVIDER` only when nonzero. DTB DTO enable mirrors DCN 3.1.4: program quarter pixel rate, enable DTO, wait for status, set K1/K2 to 1:1, then set pipe DTO source `2`. Disable clears modulo/phase and selects source `0` for HDMI or `1` otherwise. `dccg32_set_valid_pixel_rate()` sets `is_hdmi = true` to select the HDMI-specific idle source. `dccg32_set_dpstreamclk()` always calls `dccg32_set_dtbclk_p_src(dccg, DTBCLK0, otg_inst)` before toggling a DP stream clock, independent of the requested `src` except for enable state.

State and persistence: mutable state is limited to hardware registers and inherited `struct dccg` fields. The code updates no persistent storage.

Dependencies and integration: it depends on `dcn32_dccg.h`, `dcn20_dccg.h`, and DCN 3.1 helpers declared by `dcn32_dccg.h`. It integrates by returning a `struct dccg` with a local function table assembled from DCN 3.2 and inherited callbacks.

Risks: always programming DTBCLK_P to DTBCLK0 in `set_dpstreamclk` means callers cannot use DPREFCLK there despite the lower helper supporting it. The quarter-rate DTO assumption is inherited from DCN 3.1.4. Invalid OTG/HPO instances only debug-break and return. `get_dccg_ref_freq()` comments expect 100 MHz but still returns `xtalin_freq_inKhz`, so callers must supply the correct board value.

Test signals: validate FIFO resync skips zero RDIVIDER, HDMI versus non-HDMI DTO-source selection on disable, DP stream clock routing for all HPO instances, K1/K2 divider programming, inherited HPO/PHY/DSC behavior on DCN 3.2 tables, and DPP DTO behavior through the older `dccg2_update_dpp_dto` callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.h

Purpose: this header declares the DCN 3.2 DCCG field map and create function. It reuses DCN 3.1 declarations while defining DCN 3.2-specific masks for DP stream clock source fields, OTG pixel-rate controls, DTBCLK_P controls, and dentist change-done/read/write divider fields.

Important APIs and types: `DCCG_MASK_SH_LIST_DCN32(mask_sh)` defines field mappings for DPP DTO enable/DB enable, DPP DTO phase/modulo, HDMI character/stream controls, PHY force controls, DP stream enable/source fields, `SYMCLK32` SE/LE controls, OTG DTO enable/status/source/add pixel fields, K1/K2 pixel-rate dividers, DTBCLK_P source/enables, audio DTO source, and dentist `CHG_DONE`, `RDIVIDER`, and `WDIVIDER`. The public symbol is `dccg32_create()`.

Control flow: resource construction expands this macro into `dccg_shift` and `dccg_mask` tables. Runtime behavior comes from `dcn32_dccg.c`, which relies on these fields being present for `REG_GET`, `REG_UPDATE`, `REG_WRITE`, and `REG_WAIT`.

State and persistence: the header has no mutable state. Its macro expansions become static metadata used by each `struct dcn_dccg` instance.

Dependencies and integration: it includes `dcn31/dcn31_dccg.h` and therefore inherits DCN 3.1 callback prototypes and common DCCG types. ASIC-specific resource files include this header to instantiate the register metadata for DCN 3.2 hardware.

Risks: the macro list includes a duplicate `OTG3_PIXEL_RATE_DIVK2` mapping. Missing DSCCLK fields here are deliberate because the DCN 3.2 C callback table does not expose local DSC DTO callbacks, but inherited callbacks still require compatible registers when used. Macro name concatenation is brittle against generated register-header changes.

Test signals: compile-time initialization of a DCN 3.2 DCCG table, successful `dccg32_create()` link, and runtime register writes for DP stream, DTBCLK_P, pixel divider, and dentist resync fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.c

Purpose: this file implements the DCN 3.5 DCCG backend and carries both the active DCN 3.5 function table and a newer, currently unused callback implementation. It expands DCCG control from DTO programming into explicit root-clock-gating management for DPP, DSC, DP stream, DTBCLK_P, PHY symbol clocks, HPO `SYMCLK32`, and the `SYMCLK[A-E]` frontend/backend clock network.

Important APIs and functions: `dccg35_create()` installs the active `dccg35_funcs`. Active exported helpers include `dccg35_update_dpp_dto()`, `dccg35_dpp_root_clock_control()`, `dccg35_trigger_dio_fifo_resync()`, `dccg35_enable_global_fgcg_rep()`, `dccg35_enable_dscclk()`, `dccg35_disable_dscclk()`, `dccg35_enable_symclk_se()`, `dccg35_disable_symclk_se()`, `dccg35_set_dpstreamclk_root_clock_gating()`, and `dccg35_root_gate_disable_control()`. Static helpers program root gates, DPP enables, pixel-rate dividers, DTBCLK_P, DTB DTO, DP stream clock source, PHY symbol clocks, and `SYMCLK` frontend/backend routing. The inactive `dccg35_funcs_new` path wraps a cleaner source/RCG split for DPP, DSC, DTBCLK_P, DP stream, PHY, `SYMCLK32`, and `SYMCLK` networks.

Control flow: active DPP DTO updates ungate the DPP root clock, compute phase/modulo, program `DPPCLK_DTO_PARAM`, enable `DPPCLK#_EN`, or disable the DPP clock and allow root gating when requested frequency is zero. DTB DTO enable gates DTBCLK_P for the selected OTG, programs quarter-rate modulo/phase, enables the DTO, waits for status, and sets K1/K2 to 1:1 without changing `PIPE_DTO_SRC_SEL` because pixel clock programming handles that later. DTB DTO disable clears the DTO only when both reference and requested rates are zero and ungates DTBCLK_P. DP stream clock setup toggles `DPSTREAMCLK#_EN`, source select, and root gate disables. DPP, DSC, and DP stream root-control functions add `udelay(10)` waits when clocks are ramped or ungated.

State and persistence: runtime state is volatile. The file updates DCCG gate-disable registers, clock-enable registers, DTO parameter registers, pixel-rate divider registers, `dccg->pipe_dppclk_khz[]`, and `dccg->dpp_clock_gated[]`. It also reads DC debug flags such as `root_clock_optimization` and emits debug logs. There is no persistent storage.

Dependencies and integration: it depends on DCN 3.5 register metadata from `dcn35_dccg.h`, DCN 3.1 helpers for audio, HPO, OTG, DISPCLK, and register-state capture, and DCN 2 compatibility helpers. `resource.h` is included for display resource context. The active callback table deliberately reuses several older callbacks while adding DCN 3.5-specific gate control.

Risks: the file contains two full callback styles, but `dccg35_create()` installs only `dccg35_funcs`; `dccg35_funcs_new` and a few helpers are referenced only through `(void)&...` statements to suppress unused warnings. This makes maintenance error-prone because fixes may land in the inactive table. Several root-gate helper names use inverted booleans (`enable`, `allow_rcg`, `disallow_rcg`, `power_on`), increasing regression risk. `dccg35_disable_symclk32_le_new()` calls a helper that currently reads only `SYMCLK32_SE3` regardless of the `symclk_32_se_inst` argument, which is suspicious even though the new path is inactive. Some root-gating updates are commented out in active `SYMCLK` disable paths, leaving behavior dependent on hardware/firmware sequencing.

Test signals: validate active function-table selection; DPP DTO update and root-control on/off sequences; DP stream enable/disable and root gate bits; DTB DTO enable/disable without programming `PIPE_DTO_SRC_SEL`; DIO FIFO resync with nonzero RDIVIDER; DSC enable/disable and root gates; `SYMCLK` backend sharing for MST-like multiple frontends; global fine-grain clock gating; and low-power/root-clock-optimization debug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.h

Purpose: this header defines the DCN 3.5 DCCG register and field contract. It extends DCN 3.1.4 with DPP clock control, additional gate-disable registers, global FCG control, `SYMCLK[A-E]` clock-enable registers, and PSP symbol-clock control.

Important APIs and types: `DCCG_REG_LIST_DCN35()` includes `DCCG_REG_LIST_DCN314()` and adds `DPPCLK_CTRL`, `DCCG_GATE_DISABLE_CNTL4/5/6`, `DCCG_GLOBAL_FGCG_REP_CNTL`, `SYMCLKA` through `SYMCLKE_CLOCK_ENABLE`, and `SYMCLK_PSP_CNTL`. `DCCG_MASK_SH_LIST_DCN35(mask_sh)` maps DPP enables, PHY `*_EN` and source fields, DP stream source/enables, DSC enables and DTO fields, `SYMCLK32`, OTG DTO/add/drop, DTBCLK_P, DENTIST, fine-grain clock gating, frontend/backend `SYMCLK` fields, root gates, FIFO error-detection fields, and DISPCLK ramp fields. Prototypes expose creation, init, DPP DTO/root control, global FCG, DP stream root gating, HDMI stream root gating declaration, DSC, HPO SE disable, and `SYMCLK` SE enable/disable.

Control flow: the header drives the C file by supplying all fields needed for active root-gating and clock-source updates. It inherits DCN 3.1.4 definitions and adds the DCN 3.5 fields required by `dccg35_funcs`.

State and persistence: no mutable state is stored here. The macros initialize static register/shift/mask data used by `struct dcn_dccg` instances.

Dependencies and integration: it includes `dcn314/dcn314_dccg.h`, so it inherits DCN 3.1.4 and DCN 3.1 declarations. Resource files for DCN 3.5 ASICs must instantiate both register and mask lists to make all active callbacks safe.

Risks: there is a prototype for `dccg35_set_hdmistreamclk_root_clock_gating()` but no implementation in the researched C file, so consumers must not call it unless another compilation unit supplies it. The field list is large and manually maintained, making omissions likely when hardware registers evolve. Duplicate or repeated field mappings inherited from earlier headers remain present. Because the C file also contains an inactive new callback table, this header supports more fields than the active table uses.

Test signals: compile/link the declared functions, instantiate the register/mask macros in a DCN 3.5 resource table, and runtime-test DPP/DSC/DPSTREAM/DTBCLK/SYMCLK/PHY root-gate fields plus FIFO error-detection and global FCG controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn401/dcn401_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn401/dcn401_dccg.c

Purpose: this file implements the DCN 4.0.1 DCCG backend. It retains the general DCCG object/callback pattern but moves DP pixel clock handling to a DCN4-style DP DTO with integer, phase, and modulo programming, expands `SYMCLK32_LE` to four instances, changes TMDS pixel-rate divider encoding, and intentionally leaves legacy DTBCLK DTO/audio DTO callbacks unset.

Important APIs and functions: `dccg401_create()` installs `dccg401_funcs`. `dccg401_update_dpp_dto()` programs DPP DTO phase/modulo and `DPPCLK#_EN`. `dccg401_get_pixel_rate_div()` and `dccg401_set_pixel_rate_div()` read/write TMDS divider fields and DP DTO integer fields. `dccg401_set_dtbclk_p_src()` selects DPREFCLK or DTBCLK0 per OTG. `dccg401_set_physymclk()` controls four PHY symbol clocks plus root gates. `dccg401_enable_symclk32_le()` and `dccg401_disable_symclk32_le()` support LE0-LE3. `dccg401_set_dpstreamclk()` toggles HPO DP stream clocks. `dccg401_set_dp_dto()` programs non-TMDS DP DTO integer/phase/modulo and selects DTO source. DSC helpers are `dccg401_set_dto_dscclk()` and `dccg401_set_ref_dscclk()`. `dccg401_enable_symclk_se()` and `dccg401_disable_symclk_se()` control stream-encoder frontend clocks.

Control flow: DPP DTO setup computes the familiar `phase / 0xff` ratio and toggles `DPPCLK#_EN` rather than `DPPCLK_DTO_ENABLE`. Pixel-rate divider programming accepts only divide-by-2 and divide-by-4, encodes them as one bit, writes the OTG field, and waits for dentist change done. DP DTO setup is skipped for TMDS signals. For non-TMDS signals, it validates `refclk_hz`, computes integer and fractional phase against reference modulo, gates required DTBCLK and `SYMCLK32` roots, sets DTBCLK_P source, writes `DP_DTO_PHASE/MODULO`, writes the `DPDTO#_INT` field, and toggles `DP_DTO_ENABLE` plus `PIPE_DTO_SRC_SEL`.

State and persistence: mutable state is hardware register state plus `dccg->pipe_dppclk_khz[]`. The callback table sets `set_dtbclk_dto = NULL`, `set_valid_pixel_rate = NULL`, and `set_audio_dtbclk_dto = NULL`, making capability absence explicit. There is no persistence outside MMIO state.

Dependencies and integration: it depends on `dcn401_dccg.h`, DCN 3.1 helpers for HPO SE and register-state reads, and DCN 2 helpers for clock-gating compatibility. It calls `dc_is_tmds_signal()` to decide whether DP DTO programming is needed. Display resource code must provide DCN 4.0.1 register/shift/mask tables with the new TMDS and DP DTO fields.

Risks: `dccg401_set_dp_dto()` toggles root gates and source selection only for non-TMDS; TMDS path depends on separate TMDS divider/stream clock programming. Invalid or zero `refclk_hz` debug-breaks and returns without DTO setup. `dccg401_set_pixel_rate_div()` silently returns for unsupported dividers instead of asserting. LE instance support now spans four entries, so any caller assuming two LE clocks will under-initialize DCN4 hardware. `dccg401_set_src_sel()` is declared in the header but not implemented here.

Test signals: validate TMDS divide-by-2/divide-by-4 encoding, non-TMDS DP DTO integer/phase/modulo math, DP DTO enable/source toggling, DTBCLK_P source selection, four LE clock enable/disable paths, DSC DTO/ref toggles, DPP DTO enable/disable, PHY root-gating, and header/C prototype consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn401/dcn401_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn401/dcn401_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn401/dcn401_dccg.h

Purpose: this header defines the DCN 4.0.1 DCCG field map and public functions. It adapts the DCN 3.2/3.5 register contract to DCN4 pixel clock handling, including DP DTO integer fields, TMDS divider fields, four `SYMCLK32_LE` instances, and DCN4 gate-disable fields.

Important APIs and types: `DCCG_MASK_SH_LIST_DCN401(mask_sh)` maps DPP clock enables, HDMI/PHY/DP stream fields, `SYMCLK32` SE/LE controls, OTG pipe DTO source/add pixel fields, `OTG#_TMDS_PIXEL_RATE_DIV`, `DPDTO#_INT`, DTBCLK_P source/enables, audio DTO fields, dentist change done, DP DTO enable fields, DSC enables and DTO params, root-gating fields, and `SYMCLK[A-D]` frontend/backend fields. Prototypes declare create/init, DPP DTO, ref frequency, DP stream clock, LE clock enable/disable, DP stream disable, DSC DTO/ref, pixel-rate divider get/set, DP DTO, `SYMCLK` SE control, DTBCLK_P source, and PHY symbol clock control.

Control flow: the C file's callback table consumes this header's fields to drive register updates. DCN4 DP pixel clocks use `set_dp_dto` rather than the older `set_dtbclk_dto`, and the header reflects that by including `DP_DTO_ENABLE` and `DPDTO#_INT` fields.

State and persistence: no state is stored in the header. It defines compile-time metadata used by live DCCG objects.

Dependencies and integration: it includes `dcn32/dcn32_dccg.h` and reuses shared enums and function signatures. DCN4 resource files must instantiate this field list and pass it into `dccg401_create()`.

Risks: `dccg401_set_src_sel()` is declared but absent from the researched implementation, so callers would fail to link unless another file provides it. The mask list includes many inherited fields that may not be used by the active DCN4 callback table, and any mismatch between field names and generated ASIC headers breaks resource construction. Four LE fields are required here where older headers define only two.

Test signals: build a DCN 4.0.1 resource table, link all prototypes, validate DP DTO and TMDS divider fields, four `SYMCLK32_LE` fields, DPP/DSC/PHY root gates, and `SYMCLK[A-D]` frontend/backend fields on real or register-simulated hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn401/dcn401_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.c

Purpose: this file implements the DCN 4.2 DCCG variant by combining DCN 3.5 clock-gating behavior with DCN 4.0.1 DP DTO/stream clock behavior and DCN 4.2-specific pixel add/drop and FIFO resync registers. It constructs the DCCG object and installs `dccg42_funcs`.

Important APIs and functions: `dccg42_create()` allocates the object. `dccg42_otg_add_pixel()` and `dccg42_otg_drop_pixel()` write add/drop bits in `OTG_ADD_DROP_PIXEL_CNTL` rather than per-OTG pixel-rate registers. `dccg42_enable_global_fgcg()` controls global fine-grain clock gating and honors `debug.disable_clock_gate`. `dccg42_set_physymclk()` controls five PHY symbol clocks and root gates with DCN 4.2 gating semantics. `dccg42_set_pixel_rate_div()` writes TMDS divide-by-2/divide-by-4 fields without the DCN401 dentist wait. `dccg42_trigger_dio_fifo_resync()` toggles `RESYNC_FIFO_LEVEL_ADJUST_EN` and waits for `DISPCLK_FREQ_RAMP_DONE`. `dccg42_init()` disables HPO SE/LE clocks, DP stream clocks, and optionally forces PHY root gates disabled when physymclk optimization is off.

Control flow: init loops over four SE instances with `dccg35_disable_symclk32_se()`, optionally disables four LE and four DP stream instances through DCN401 helpers, and programs all five PHY root gates to disabled if physymclk root-clock optimization is not enabled. Pixel add/drop switch over OTG0-3 and assert on invalid instances. Pixel divider programming reuses DCN401 get logic, accepts only divide-by-2 or divide-by-4, writes the encoded TMDS field, and returns without waiting for dentist change done. The callback table reuses DCN35 DPP/DSC/root-gate/SYMCLK functions and DCN401 ref-frequency, DP stream, DP DTO, DSC DTO/ref, LE, and DTBCLK_P helpers.

State and persistence: state is volatile hardware register state and inherited `struct dccg` fields. `dccg42_create()` uses `kzalloc(sizeof(*dccg_dcn), GFP_KERNEL)` rather than the `kzalloc_obj` helper used in older variants. No state persists outside driver-managed hardware programming.

Dependencies and integration: it includes `dcn35_dccg.h` and `dcn42_dccg.h`, and relies heavily on exported callbacks from `dcn31`, `dcn35`, and `dcn401`. Resource code must provide DCN 4.2 register/shift/mask tables including `OTG_ADD_DROP_PIXEL_CNTL` and `RESYNC_FIFO_LEVEL_ADJUST_EN`.

Risks: the comment in `dccg42_set_pixel_rate_div()` still says "only 2 and 4 are valid on dcn401", which is inherited wording and can confuse maintenance. Unlike DCN401, pixel divider updates do not wait for dentist change done, so hardware sequencing must justify the difference. The function table leaves `set_dtbclk_dto`, `set_valid_pixel_rate`, and `set_audio_dtbclk_dto` as `NULL`. `set_symclk32_le_root_clock_gating` points to the DCN31 helper, which only switches instances 0 and 1, while DCN42 LE has four instances; callers must not use that callback for LE2/LE3 unless this is intentional.

Test signals: validate OTG add/drop through `OTG_ADD_DROP_PIXEL_CNTL`, FIFO resync toggle and ramp-done wait, global FCG with `disable_clock_gate`, PHY root gate behavior with physymclk optimization on/off, TMDS dividers, DCN401 DP DTO paths, inherited DCN35 DPP/DSC/SYMCLK behavior, and LE2/LE3 clock disable during init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.h

Purpose: this header defines the DCN 4.2 DCCG field contract and public DCN 4.2 helpers. It builds on DCN 4.0.1 while adding DCN 4.2-specific OTG add/drop and FIFO resync fields and preserving five-PHY/four-LE support.

Important APIs and types: `DCCG_MASK_SH_LIST_DCN42_COMMON(mask_sh)` maps common DCN 4.2 fields for DPP, DISPCLK frequency change and FIFO error detection, HDMI/PHY/DP stream, `SYMCLK32`, pipe DTO source, OTG add/drop pixel control, TMDS and DP DTO fields, DTBCLK_P, audio DTO, dentist, gate-disable, `SYMCLK[A-D]`, and root gates. `DCCG_MASK_SH_LIST_DCN42(mask_sh)` extends the common list with PHYE, DSC3, `SYMCLKE`, and `RESYNC_FIFO_LEVEL_ADJUST_EN`. Prototypes declare DCN 4.2 OTG add/drop, global FCG, PHY symbol clock, pixel divider, FIFO resync, and create functions.

Control flow: resource files expand the mask macros to supply the fields used by `dcn42_dccg.c` and inherited DCN35/DCN401 callbacks. The C file then chooses a mixed callback table that relies on these fields being present.

State and persistence: the header owns no mutable state. It defines static register-field metadata.

Dependencies and integration: it includes `dcn401/dcn401_dccg.h`, inheriting DCN4 signatures and common DCCG types. It must stay synchronized with generated DCN 4.2 register headers and with inherited callback field requirements.

Risks: the common and extended field lists are long and partially overlapping; duplicate fields such as PHYE root gate are easy to introduce. The header exposes four `SYMCLK32_LE` fields, while one inherited root-gating callback in the C table only handles two instances. Any mismatch between `OTG_ADD_DROP_PIXEL_CNTL` field names and generated headers breaks the DCN42-specific add/drop callbacks.

Test signals: compile a DCN 4.2 resource table, link `dccg42_create()`, and runtime-test OTG add/drop, FIFO resync, PHYE/DSC3/SYMCLKE fields, DP DTO/TMDS divider fields, and inherited DCN35/DCN401 root-gate paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/Makefile

Purpose: this Makefile declares the object files that make up the common AMD Display Core DCE hardware-programming layer and appends them to the global AMD display build list.

Important APIs and variables: `DCE` is the local object list and includes audio, stream encoder, link encoder, memory input, clock source, scaler filters, transform, output pixel processor, DMCU, ABM, input pixel processor, AUX, I2C hardware/software, DMUB PSR/ABM/replay/outbox/hardware-lock-manager, and panel control objects. `AMD_DAL_DCE = $(addprefix $(AMDDALPATH)/dc/dce/,$(DCE))` converts local object names into display-tree-relative paths. `AMD_DISPLAY_FILES += $(AMD_DAL_DCE)` appends them to the larger display driver build.

Control flow: Kbuild includes this fragment from the AMD display build. The object list controls which C files are compiled and linked into the AMDGPU display stack. It does not execute runtime logic.

State and persistence: there is no runtime state. Build state is the generated object list consumed by Kbuild.

Dependencies and integration: the file assumes `AMDDALPATH` and `AMD_DISPLAY_FILES` are defined by parent Makefiles. The included objects implement common DCE/DCN services used by display resource construction and hardware sequencing. `dce_abm.o` is the researched ABM implementation in this subset.

Risks: missing an object silently removes a hardware block implementation from the display build and may surface as link failures or disabled functionality. Adding an object without corresponding source or configuration support breaks Kbuild. The comment says register offsets/shifts/masks are stored in a `dec_hw`/`dce_hw` struct pattern, which matches the register-helper style used by these files.

Test signals: build AMD display with this Makefile included, verify every object in `DCE` has a source file, and check link coverage for DCE services such as ABM, DMCU, DMUB ABM, PSR, AUX, I2C, and panel control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.c

Purpose: this file implements the legacy DCE Adaptive Backlight Management (ABM) object. It initializes ABM hardware registers, sends ABM/backlight/pipe commands to DMCU through master communication registers, exposes current/target backlight reads, and constructs/destroys `struct abm` instances with `dce_funcs`.

Important APIs and functions: `dce_abm_create()` allocates and constructs the object; `dce_abm_destroy()` frees it. The callback table includes `dce_abm_init()`, `dce_abm_set_level()`, `dce_abm_set_pipe()`, `dce_abm_set_backlight_level_pwm()`, `dce_abm_get_current_backlight()`, `dce_abm_get_target_backlight()`, and `dce_abm_immediate_disable()`. Private `dmcu_set_backlight_level()` converts a U16.16 PWM value to BIOS scratch 8-bit backlight state, selects the pipe, writes ramp/user-level data, sends a DMCU command, and waits for completion.

Control flow: callers create an ABM object with register/shift/mask tables. `dce_abm_init()` programs histogram, luma, coefficient, backlight current/target/user, threshold, and missed-frame-clear registers. Runtime DMCU commands first check `abm->dmcu_is_running`; if false, operations return success without MMIO command handoff. Pipe, ABM level, and backlight commands wait for `MASTER_COMM_INTERRUPT` to clear, write parameters into `MASTER_COMM_DATA_REG1`, `BL1_PWM_USER_LEVEL`, or `MASTER_COMM_CMD_REG`, set `MASTER_COMM_INTERRUPT` to notify DMCU, and usually wait for it to clear again. Immediate disable uses pipe command byte1 value `255`.

State and persistence: the object stores `ctx`, function table, `dmcu_is_running`, and pointers to register/shift/mask tables. Hardware state includes ABM sample rates, histogram configuration, PWM current/target/user levels, DMCU command registers, and `BIOS_SCRATCH_2` current backlight bits. There is no file or NVRAM persistence; BIOS scratch updates are firmware/driver-visible runtime state.

Dependencies and integration: it depends on Linux allocation, `dce_abm.h`, DC services, `reg_helper.h`, fixed-point/DC headers, and ATOM BIOS scratch bit definitions. It integrates through the generic `struct abm` interface; display resource code creates this object for DCE/DCN generations that still use DMCU ABM rather than DMUB-only ABM paths.

Risks: all DMCU waits use a large fixed retry count (`80000` with 1-unit delay), so a stuck DMCU can cause long blocking waits. When `dmcu_is_running` is false, set operations report success without programming hardware, which is intentional but can hide missing firmware startup. `controller_id == 0` forces `frame_ramp = 0`, so ramp behavior differs by controller. `dce_abm_destroy()` assumes `*abm` is non-NULL and a DCE ABM object. BIOS scratch backlight conversion saturates only on bit `0x10000`; unusual U16.16 values above that bit may be truncated.

Test signals: validate ABM register initialization values, DMCU command sequencing for pipe/level/backlight, immediate-disable command value, current/target backlight reads in U1.16 hardware format, BIOS scratch backlight update, behavior when `dmcu_is_running` is false, timeout handling when `MASTER_COMM_INTERRUPT` never clears, and create/destroy allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h

Purpose: this header defines the DCE/DCN ABM register metadata contract and the concrete `struct dce_abm` type used by `dce_abm.c`. It provides register lists and mask/shift lists for multiple generations, including DCE110, DCN1.0, DCN2.0, DCN3.0/3.01/3.02, DCN3.2, DCN3.5, DCN4.0.1, and DCN4.2 ABM layouts.

Important APIs and types: register-list macros include `ABM_COMMON_REG_LIST_DCE_BASE()`, `ABM_DCE110_COMMON_REG_LIST()`, `ABM_DCN10_REG_LIST(id)`, `ABM_DCN20_REG_LIST()`, `ABM_DCN301_REG_LIST(id)`, `ABM_DCN302_REG_LIST(id)`, and `ABM_DCN30_REG_LIST(id)`. Mask/shift macros include `ABM_COMMON_MASK_SH_LIST_DCE_COMMON_BASE`, `ABM_MASK_SH_LIST_DCE110`, `ABM_MASK_SH_LIST_DCN10`, `ABM_MASK_SH_LIST_DCN20`, `ABM_MASK_SH_LIST_DCN30`, `ABM_MASK_SH_LIST_DCN35`, `ABM_MASK_SH_LIST_DCN32`, `ABM_MASK_SH_LIST_DCN401`, and `ABM_MASK_SH_LIST_DCN42`. `ABM_REG_FIELD_LIST(type)` defines fields shared by `struct dce_abm_shift` and `struct dce_abm_mask`. `struct dce_abm_registers` stores ABM and DMCU register offsets. `struct dce_abm` embeds `struct abm` plus register metadata pointers. Public functions are `dce_abm_create()` and `dce_abm_destroy()`.

Control flow: resource files expand the generation-specific register and mask macros to create metadata tables. `dce_abm.c` uses those tables through `REG_*`/`FN` macros when it initializes ABM and sends DMCU commands.

State and persistence: the header has no runtime state. The structs it defines hold per-object pointers to immutable register metadata and the inherited mutable `struct abm` runtime state.

Dependencies and integration: it includes `abm.h` for the base object and callback interface. NBIO scratch register macros appear in DCN register lists where BIOS scratch access is routed through NBIO. The newer DCN401/DCN42 mask lists include ACE piecewise-linear and histogram readback fields used by newer ABM/DMUB paths even though `dce_abm.c` itself programs only the older subset.

Risks: the header supports many hardware generations with macro concatenation, so generated register-name drift can break only one ASIC path. Some newer mask lists include fields not present in older register lists, requiring resource definitions to pair the right macro set. `ABM_MASK_SH_LIST_DCN35` maps only the DCN10 common fields, omitting master communication fields, which is only safe if that generation's ABM path does not use the DCE DMCU command helpers. Macro growth increases the chance of fields being present in masks but absent from `struct dce_abm_registers` or vice versa.

Test signals: compile resource tables for each ABM generation macro, verify `struct dce_abm_shift` and `struct dce_abm_mask` cover every field used by `dce_abm.c`, boot-test DCE/DCN ABM initialization and DMCU command paths, and validate newer DCN401/DCN42 ACE/histogram field mappings with their consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h -->
