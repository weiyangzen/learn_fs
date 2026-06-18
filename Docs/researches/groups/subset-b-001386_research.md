# subset-b-001386 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.c

## Purpose
Implements the DCN 3.1.4 display clock manager for AMD display hardware. It owns boot-time clock manager construction, runtime clock updates for DISPCLK/DPPCLK/DCFCLK/deep-sleep DCFCLK/DTBCLK, SMU watermark/DPM table exchange, spread-spectrum handling, and low-power/zstate transitions for display-off and mission-mode operation.

## Important APIs, Types, And Functions
- `dcn314_clk_mgr_construct` initializes `struct clk_mgr_dcn314`, hooks `dcn314_funcs`, allocates GPU-visible watermark and DPM buffers, queries SMU version, selects DDR5/LPDDR5 watermark defaults, reads spread-spectrum state, and optionally replaces default bandwidth parameters from SMU DPM data.
- `dcn314_update_clocks` is the runtime clock transition entry point used by DC. It compares requested `dc_state` clocks against persisted `clk_mgr_base->clks`, calls DCN314 SMU helpers, updates DPP DTOs, applies OTG-disable workarounds, and notifies DMCUB.
- `dcn314_init_clocks`, `dcn314_are_clock_states_equal`, `dcn314_is_spll_ssc_enabled`, and `dcn314_clk_mgr_destroy` provide lifecycle and comparison support.
- Internal helpers build watermark ranges, transfer watermark/DPM tables via SMU DRAM address messages, derive VCO frequency from PLL registers, and populate `clk_bw_params` from `DpmClocks314_t`.

## Control Flow
Construction sets static defaults first, then allocates a framebuffer watermark table and a temporary DPM table. If PMFW responds to `dcn314_smu_get_smu_version`, the manager treats SMU as present and can exchange tables. Runtime updates branch on `safe_to_lower`: lowering may allow zstates, disable DTBCLK, and enter display-off low power when the active-display workaround count is zero; raising disallows zstates when requested, enables DTBCLK, exits idle optimization, and returns to mission mode. Clock requests are then ordered so DCF hard-mins and deep-sleep minima are sent before DISPCLK/DPPCLK changes. DPP DTOs are updated before lowering global DPPCLK and after raising it.

## State And Persistence
Persistent state is in `clk_mgr->base.base.clks`, `dentist_vco_freq_khz`, `dprefclk_khz`, `dp_dto_source_clock_in_khz`, SMU presence/version fields, bandwidth tables, and the GPU allocation tracked by `smu_wm_set.mc_address`. The static `dcn314_bw_params` and watermark tables are shared configuration templates. The current power state, zstate allowance, DTBCLK enablement, and last programmed clock values are used to suppress redundant PMFW messages.

## Dependencies And Integration Points
This file integrates DC clock policy with DCCG DTO programming, DMCUB clock notifications, link encoder state, BIOS integrated memory info, spread-spectrum BIOS tables, and the DCN314 SMU mailbox layer in `dcn314_smu.c`. It reuses DCN20 DPP DTO update logic, DCN31 DTB reference helpers, DCE DP reference helpers, and common `clk_mgr_internal` helpers such as `should_set_clock`.

## Risks And Edge Cases
The active-display workaround intentionally counts enabled DIG/PHY state and forces one display for TMDS display-off cases to avoid HDMI resume hangs. The DISPCLK path temporarily disables OTGs for DPMS-off or virtual streams, so incorrect pipe selection can cause visible glitches. PMFW DPM tables are trusted enough to populate bandwidth limits but guarded by validity checks and fallback defaults; malformed level counts or zero clocks can distort watermarks and mode validation. Mutating `new_clocks->dppclk_khz` to enforce the 100 MHz floor is a side effect visible to later code in the same state transition.

## Test Signals
Useful signals include boot with and without SMU response, pstate-enabled versus disabled runs, DDR5 and LPDDR5 integrated info, display-off/restore over HDMI and DP, DTBCLK enable/disable transitions, zstate allow/disallow transitions, DPPCLK lowering and raising with DTO ordering, successful DMCUB notify commands, and watermark table transfers with nonzero GPU addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.h

## Purpose
Declares the DCN314 clock-manager object shape and public lifecycle/update entry points used by the display core and ASIC construction code.

## Important APIs, Types, And Functions
- `struct clk_mgr_dcn314` embeds `struct clk_mgr_internal` and owns the DCN314 SMU watermark allocation descriptor.
- `struct dcn314_smu_watermark_set` pairs a CPU pointer to `struct dcn314_watermarks` with the GPU memory controller address passed to PMFW.
- `struct dcn314_ss_info_table` stores spread-spectrum percentages by clock source for local LUT-based DP reference adjustment.
- Public declarations expose clock-state comparison, SPLL SSC detection, clock initialization/update, construction, and destruction.

## Control Flow
The header itself has no executable control flow. Its declarations define the handoff between the DCN ASIC factory, the generic `clk_mgr` function table, and the DCN314 implementation file.

## State And Persistence
The persistent state introduced here is the `smu_wm_set` member. It persists from construction until destroy and determines whether watermark transfers use a GPU allocation or a dummy fallback.

## Dependencies And Integration Points
It depends on `clk_mgr_internal.h` for base clock-manager types, `union large_integer`, `struct dc_clocks`, `struct dc_state`, `struct dc_context`, `struct pp_smu_funcs`, and `struct dccg`. It is consumed by DCN314 construction and SMU code.

## Risks And Edge Cases
The forward declaration of `struct dcn314_watermarks` keeps the ABI opaque, so the `.c` file and SMU header must remain consistent about allocation size and table layout. Any mismatch between `DCN314_NUM_CLOCK_SOURCES` and the LUT in the `.c` file would affect spread-spectrum source indexing.

## Test Signals
Build coverage should catch type drift. Runtime coverage is visible through successful DCN314 construction, non-null watermark table allocation, clean destroy, and correct dispatch through `clk_mgr->funcs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.c

## Purpose
Implements the DCN314 VBIOS/PMFW SMU mailbox adapter. It translates display clock-manager requests into MP1 C2P message transactions for clock hard-mins, display idle optimization, table transfers, zstate policy, DTBCLK control, and PMFW version queries.

## Important APIs, Types, And Functions
- `dcn314_smu_send_msg_with_param` is the central transaction helper: wait for response ready, clear response, write parameter, write message ID, wait for completion, handle known failures, and return the SMU output parameter.
- `dcn314_smu_wait_for_response` polls `MP1_SMN_C2PMSG_91` until the response is no longer busy.
- Public wrappers include `dcn314_smu_set_dispclk`, `dcn314_smu_set_dppclk`, `dcn314_smu_set_hard_min_dcfclk`, `dcn314_smu_set_min_deep_sleep_dcfclk`, table DRAM address/transfer calls, `dcn314_smu_set_zstate_support`, and `dcn314_smu_set_dtbclk`.

## Control Flow
Every public call first checks `smu_present` where appropriate; DCFCLK and idle-optimization requests also honor `debug.pstate_enabled`. The mailbox sequence always waits for PMFW readiness before clearing the response and issuing a new message. On failed watermark-table transfers or disabled DCFCLK DPM, it logs nonfatal diagnostics; other failed messages assert. Zstate support maps DC policy enums to a bitmask sent through `VBIOSSMC_MSG_AllowZstatesEntry`.

## State And Persistence
The file does not own long-lived allocations. It mutates PMFW state through messages and relies on `clk_mgr_internal` for `smu_present`, context, and logging. Mailbox state persists in MP1 C2P registers across individual transactions until overwritten.

## Dependencies And Integration Points
Depends on MP1 register offsets, `reg_helper` accessors, DC logging, timeout reporting through `dm_helpers_smu_timeout`, and table IDs from `dcn314_smu.h`. It is called exclusively by the DCN314 clock manager and participates in PMFW's VBIOSSMC contract.

## Risks And Edge Cases
Timeouts can stall clock updates for up to the full polling budget. Some failures are tolerated, but unexpected failures assert and can expose PMFW/BIOS mismatches. All frequency parameters are rounded up from kHz to MHz; callers must account for returned values being MHz-derived. If `smu_present` is false, wrappers return requested values without programming hardware.

## Test Signals
Test with PMFW present/absent, forced SMU timeouts, disabled DCFCLK DPM, watermark table transfer failure, zstate enum variants, DTBCLK toggle, and returned actual clock values from DISPCLK/DPPCLK/DCFCLK messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.h

## Purpose
Defines the DCN314 display SMU ABI data structures and function prototypes used by the clock manager to exchange DPM and watermark tables with PMFW.

## Important APIs, Types, And Functions
- `DpmClocks314_t` describes PMFW-reported DCF/DISP/DPP/SOC/VCN clocks, SOC voltages, DF pstate data, enabled level counts, and GFX clock limits.
- `DfPstateTable314_t` includes FCLK, memory clock, voltage, and WCK ratio.
- `struct dcn314_watermarks` mirrors PMFW's two-dimensional watermark rows plus MMHUB padding.
- `struct dcn314_smu_dpm_clks`, `struct display_idle_optimization`, and `union display_idle_optimization_u` define GPU table addressing and idle bit packing.

## Control Flow
The header has no executable flow, but the table IDs and prototypes define which operations the `.c` mailbox layer can issue: version query, clock requests, table transfers, idle optimization, zstate policy, and DTBCLK control.

## State And Persistence
DPM and watermark structures are copied through GPU-visible memory shared with PMFW. The idle optimization union persists only as a packed message argument. WCK ratios become persisted bandwidth-table fields after construction.

## Dependencies And Integration Points
It includes `smu13_driver_if_v13_0_4.h` for common PMFW constants such as clock-level counts and watermark row definitions. It is tightly coupled to the DCN314 clock-manager bandwidth-population logic.

## Risks And Edge Cases
ABI layout drift between driver and PMFW would corrupt DPM or watermark interpretation. The code assumes enabled counts do not exceed fixed array lengths and that at least one valid memory/FCLK entry exists when constructing bandwidth limits.

## Test Signals
Compile-time structure compatibility, successful DPM table transfer, correct WCK ratio conversion, valid watermark row upload, and sane enabled-level counts from PMFW are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.c

## Purpose
Implements the DCN315 clock-manager variant. It programs display clocks through DCN315 SMU messages, builds watermark ranges, imports PMFW DPM tables into bandwidth parameters, and handles display-off low-power transitions and OTG workarounds.

## Important APIs, Types, And Functions
- `dcn315_update_clocks` is the active runtime updater for DCFCLK, deep-sleep DCFCLK, DISPCLK, DPPCLK, DTBCLK, and display idle optimization.
- `dcn315_clk_mgr_construct` initializes function pointers, GPU-visible watermark/DPM tables, SMU version state, memory-specific watermark defaults, DPREF/DTB reference clocks, spread-spectrum adjustment, and optional PMFW-derived bandwidth data.
- `dcn315_clk_mgr_helper_populate_bw_params` maps `DpmClocks_315_t` voltage and pstate data into `clk_bw_params`.
- `dcn315_build_watermark_ranges` and `dcn315_notify_wm_ranges` prepare PMFW watermark ranges and transfer them through DRAM.

## Control Flow
Runtime updates skip entirely under `skip_clock_update`. The active-display workaround counts enabled link encoders and keeps TMDS display-off as one active display. On lowering, DTBCLK may be disabled and idle optimization entered. On raising, DTBCLK and mission mode are restored. A DCN315-specific pstate lock requests an unsupported 10 GHz DCFCLK when `p_state_change_support` is false. DISPCLK changes wrap SMU programming with the OTG workaround, while DPPCLK changes preserve DTO ordering around lowering or raising.

## State And Persistence
State persists in `clk_mgr_base->clks`, `smu_present`, `smu_ver`, the static `dcn315_bw_params`, and `smu_wm_set`. Constructor-allocated DPM memory is temporary and freed after import; the watermark buffer persists until destroy. `pwr_state`, `zstate_support`, `dtbclk_en`, and last clock values suppress redundant PMFW updates.

## Dependencies And Integration Points
The file uses DCN315 SMU wrappers, DCE DP ref clock helpers, DCN31 init/equality helpers, DCN20 DPP DTO updates, DCCG state, DMCUB notify commands, link encoder state, and BIOS integrated memory info.

## Risks And Edge Cases
The unsupported-DCFCLK pstate lock relies on PMFW behavior and can be fragile if PMFW clamps or rejects it. `should_disable_otg` must avoid disabling an active DIG path. DPM table population assumes DF pstate sorting and matching voltage/count arrays. Zero or inconsistent PMFW clocks fall back to defaults but can reduce power optimization quality.

## Test Signals
Exercise pstate supported/unsupported transitions, TMDS display-off restore, DIG-active OTG bypass, DPREF query through SMU, DPM import with mismatched DCF/SOC levels, DPPCLK 100 MHz floor, watermark transfer, and DMCUB clock notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.h

## Purpose
Declares the DCN315 clock-manager wrapper type and constructor/destructor entry points.

## Important APIs, Types, And Functions
- `struct clk_mgr_dcn315` embeds the generic internal clock manager and a DCN315 SMU watermark set.
- `struct dcn315_smu_watermark_set` stores the CPU pointer and GPU address for PMFW watermark upload.
- `dcn315_clk_mgr_construct` and `dcn315_clk_mgr_destroy` are the externally visible lifecycle functions.

## Control Flow
There is no executable control flow. The header defines the type boundary consumed by ASIC initialization and implemented in `dcn315_clk_mgr.c`.

## State And Persistence
The watermark allocation descriptor persists for the clock manager lifetime. All other clock state lives in the embedded `clk_mgr_internal`.

## Dependencies And Integration Points
Depends on `clk_mgr_internal.h` for generic clock manager infrastructure and GPU address types. The opaque `struct dcn315_watermarks` comes from the SMU ABI header at implementation time.

## Risks And Edge Cases
Because the watermark type is opaque here, allocation and free code must use the matching DCN315 SMU header layout. Constructor/destructor callers must pass the concrete `struct clk_mgr_dcn315`, not just the embedded base.

## Test Signals
Build-time type checks, successful clock manager allocation, and clean destruction of the watermark GPU buffer validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.c

## Purpose
Provides DCN315 PMFW mailbox operations for display clock programming, watermark/DPM table transfer, DPREF/DTB clock queries, idle optimization, and PME workaround messages.

## Important APIs, Types, And Functions
- `dcn315_smu_send_msg_with_param` performs the mailbox transaction using MP1 C2P response/argument registers and an indexed write/readback path for the message ID.
- `dcn315_smu_wait_for_response` polls `MP1_SMN_C2PMSG_38` until PMFW leaves busy state.
- Public wrappers set DISPCLK, DPPCLK, hard-min DCFCLK, minimum deep-sleep DCFCLK, display idle optimization, PHY refclk powerdown, DRAM table addresses, table transfers, DPREF/DTB queries, DTBCLK enablement, and PME workaround.

## Control Flow
The transaction helper waits for ready, clears the response, writes the argument, retries the message-ID write up to five times until readback matches, then waits for completion. Wrappers short-circuit when SMU is not present; DCFCLK and idle optimization also short-circuit when pstate is disabled.

## State And Persistence
The file owns no heap state. It changes PMFW state and reads/writes MP1 mailbox registers. Returned clock frequencies are converted from MHz to kHz by wrappers before returning to callers.

## Dependencies And Integration Points
Uses MP 13.0.5 register offsets, `IX_REG_SET_SYNC`/`IX_REG_GET_SYNC` for the special C2PMSG_3 path, DC logging, and timeout reporting. It is the SMU backend for `dcn315_clk_mgr.c`.

## Risks And Edge Cases
Message-ID write failures are retried but not fatal unless PMFW later times out. Unlike DCN314, this helper does not special-case `Result_Failed`, so failed responses can still produce register return values. Frequency precision is MHz-based. A stale or missing SMU presence flag turns programming calls into no-ops.

## Test Signals
Observe successful readback of message IDs, timeout handling, DPREF/DTB query values, pstate-disabled DCFCLK short-circuiting, display-off idle optimization, and table transfers with valid GPU addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.h

## Purpose
Defines the DCN315 PMFW display clock ABI: DPM clock table format, watermark table format, table IDs, idle optimization bits, and SMU helper prototypes.

## Important APIs, Types, And Functions
- `DpmClocks_315_t` holds four-level DCF/DISP/DPP/SOC/VCN clock arrays, SOC voltages, DF pstate entries, enabled counts, and GFX limits.
- `WatermarkRowGeneric_t`, `WM_CLOCK_e`, and `struct dcn315_watermarks` describe PMFW watermark rows for SOC and DCF clocks.
- `struct dcn315_smu_dpm_clks` stores the PMFW-transfer table pointer and GPU address.
- Prototypes expose clock set/query, table transfer, idle optimization, voltage request declaration, PME workaround, and DTBCLK control.

## Control Flow
There is no executable flow. The constants and types constrain how `dcn315_smu.c` and `dcn315_clk_mgr.c` pack messages and interpret transferred tables.

## State And Persistence
DPM and watermark data persist in GPU-visible temporary or long-lived allocations owned by the clock manager. The idle optimization union is packed into a 32-bit PMFW argument.

## Dependencies And Integration Points
Includes `os_types.h` for fixed-width types and depends on `clk_mgr_internal` declarations supplied by includers. It is coupled to PMFW driver interface version 4.

## Risks And Edge Cases
The header declares `dcn315_smu_request_voltage_via_phyclk`, but the implementation in this subset does not define it, so callers must not rely on it unless another translation unit supplies it. Fixed array sizes mean PMFW enabled counts must be validated by consumers.

## Test Signals
Compile/link coverage for declared functions, DPM table import with four levels, watermark upload, and pstate table sanity checks are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_clk_mgr.c

## Purpose
Implements the DCN316 clock-manager variant, including SMU-backed clock changes, watermark upload, DPM table import, DTBCLK handling, and low-power transitions.

## Important APIs, Types, And Functions
- `dcn316_update_clocks` performs live clock transitions and DMCUB notification.
- `dcn316_clk_mgr_construct` initializes the manager, allocates PMFW tables, queries SMU, selects watermarks, sets DPREF/DTB reference defaults, and optionally imports SMU DPM data.
- `dcn316_clk_mgr_helper_populate_bw_params` derives bandwidth entries from `DpmClocks_316_t` using DF pstate voltage matching, WCK ratios, and max DISP/DPP levels.
- `find_clk_for_voltage`, `find_max_clk_value`, `dcn316_build_watermark_ranges`, and `dcn316_notify_wm_ranges` support table construction and upload.

## Control Flow
Clock updates follow the DCN315 shape but without the unsupported-DCFCLK pstate lock. Display count is computed only when needed for low-power entry. DTBCLK is toggled through SMU, DCF clocks are hard-minned, DPPCLK is floored at 100 MHz, DISPCLK updates run inside an OTG disable/enable workaround, and DPP DTO ordering depends on whether DPPCLK is being lowered.

## State And Persistence
Persistent state includes the embedded `clk_mgr_internal`, `smu_wm_set`, static `dcn316_bw_params`, current clock values, DTBCLK enablement, power state, and SMU version/presence. DPM transfer memory is temporary and freed at the end of construction. The dentist VCO is currently forced to a 2.5 GHz fallback.

## Dependencies And Integration Points
Uses DCN316 SMU helpers, DCE/ DCN31 clock helpers, DCCG DPP DTO programming, DMCUB clock notification, BIOS memory info, and DC debug flags. Register definitions are present for PLL/VCO work even though the VCO read path is disabled during bring-up.

## Risks And Edge Cases
The fixed dentist VCO fallback may be wrong for future hardware revisions if the commented register read remains disabled. `find_clk_for_voltage` asserts if no matching or lower voltage clock is found. PMFW table counts must not exceed fixed arrays. OTG workaround behavior differs from DCN315 and includes missing link encoder handling.

## Test Signals
Test SMU present/absent construction, DDR4 versus LPDDR5 watermark selection, DPM import with eight DCF/SOC/DISP levels and four DF pstates, DTBCLK enable/disable, display-off entry, DISPCLK/DPPCLK transition ordering, and clean GPU memory free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_clk_mgr.h

## Purpose
Declares the concrete DCN316 clock manager and its lifecycle functions.

## Important APIs, Types, And Functions
- `struct clk_mgr_dcn316` embeds the internal clock manager and a DCN316 SMU watermark set.
- `struct dcn316_smu_watermark_set` records the watermark table pointer and GPU memory address.
- `dcn316_clk_mgr_construct` and `dcn316_clk_mgr_destroy` are the integration entry points.

## Control Flow
No executable flow is present; this file defines the object and call boundary for DCN316 clock-manager construction.

## State And Persistence
The only DCN316-specific persistent state declared here is the watermark table allocation descriptor.

## Dependencies And Integration Points
Depends on `clk_mgr_internal.h` and the opaque `struct dcn316_watermarks` supplied by the SMU header in implementation files.

## Risks And Edge Cases
The embedded-base/container relationship means casts through `container_of` must use the exact concrete type. Watermark layout must remain consistent with the SMU ABI.

## Test Signals
Successful ASIC construction, function table dispatch, watermark allocation, and destroy-time GPU memory release validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.c

## Purpose
Implements DCN316 PMFW mailbox communication for display clock and table operations.

## Important APIs, Types, And Functions
- `dcn316_smu_send_msg_with_param` serializes PMFW transactions through MP1 response, argument, and message registers.
- `dcn316_smu_wait_for_response` polls `MP1_SMN_C2PMSG_91`.
- Public wrappers program DISPCLK, DPPCLK, DCFCLK hard-mins, deep-sleep DCFCLK, display idle optimization, PHY refclk powerdown, DRAM table addresses, DPM/watermark transfers, PME workaround, DTBCLK, DPREF query, and FCLK query.

## Control Flow
The send helper waits for not-busy, clears the response, writes the parameter to C2PMSG_83, writes the message ID to C2PMSG_67, then waits for completion. Wrappers skip when SMU is absent; pstate-dependent requests also require `debug.pstate_enabled`.

## State And Persistence
No memory is owned here. PMFW and MP1 mailbox registers hold the externally persistent state. Return values are converted from MHz to kHz by clock query/set wrappers.

## Dependencies And Integration Points
Uses MP 13.0.8 offsets/masks, common register helpers, DC logging, and `dm_helpers_smu_timeout`. It is the low-level backend for `dcn316_clk_mgr.c`.

## Risks And Edge Cases
The helper asserts on busy timeout but otherwise does not distinguish failed/unknown/rejected responses from successful parameter reads. `dcn316_smu_set_dtbclk` uses `VBIOSSMC_MSG_SetDtbclkFreq`, whose semantics are on/off despite a frequency-like name. Pstate-disabled paths intentionally skip DCF/idle messages.

## Test Signals
PMFW version query, DISP/DPP/DCF programming, DTBCLK toggle, DPREF/FCLK reads, timeout path, pstate-disabled no-op behavior, and table-transfer messages are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.h

## Purpose
Defines the DCN316 PMFW ABI for DPM clocks, watermarks, table transfers, idle optimization, and SMU helper calls.

## Important APIs, Types, And Functions
- `DpmClocks_316_t` expands clock and voltage arrays to eight DCF/DISP/DPP/SOC/VCN levels while retaining four DF pstates.
- `DfPstateTable_t` includes FCLK, memory clock, voltage, and WCK ratio.
- `WatermarkRowGeneric_t`, `WM_CLOCK_e`, `struct dcn316_watermarks`, and table ID macros describe PMFW table layout.
- Function prototypes cover clock programming, table transfer, PMFW clock queries, PME workaround, and DTBCLK control.

## Control Flow
The header is declarative. Its array sizes and prototypes drive validation and message packing in the `.c` implementation and bandwidth construction in the clock manager.

## State And Persistence
The structures are persisted in GPU-visible memory during SMU table exchange. Idle optimization is encoded as a 32-bit transient message argument.

## Dependencies And Integration Points
Includes `os_types.h` and is consumed by both DCN316 SMU and clock-manager files. It declares PMFW driver interface version 4.

## Risks And Edge Cases
As with DCN315, `dcn316_smu_request_voltage_via_phyclk` is declared but not implemented in the corresponding `.c` file in this subset. ABI drift or invalid enabled counts can break DPM import and watermark uploads.

## Test Signals
Compile/link checks, PMFW DPM transfer with eight clock levels, WCK ratio conversion, DTBCLK and FCLK query coverage, and watermark upload validate this ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dalsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dalsmc.h

## Purpose
Defines the DALSMC message IDs, response codes, hard-min status bits, and FCLK switch enum used by DCN32 display-to-SMU mailbox calls.

## Important APIs, Types, And Functions
- `DALSMC_Result_*` constants define PMFW response values.
- `DALSMC_MSG_*` constants enumerate the DAL message contract, including SMU version queries, DRAM table address/transfer, hard min/max clock requests, DPM frequency queries, display count, FCLK switch allowance, CAB for UCLK pstate, DMCUB wait policy, and hard-min status.
- `CHECK_HARD_MIN_CLK_*` bit masks describe which clocks PMFW reports as having fulfilled DAL hard-min arbitration.
- `FclkSwitchAllow_e` names allow/disallow states.

## Control Flow
This header has no executable control flow. It is consumed by mailbox helpers that write these IDs to DAL message registers and interpret response/status bits.

## State And Persistence
The constants map to PMFW state transitions; no C state is allocated. Hard-min status bits reflect PMFW's persisted arbiter state after clock requests.

## Dependencies And Integration Points
Used by `dcn32_clk_mgr_smu_msg.c` and shared conceptually with DCN30 SMU message helpers. It defines the PMFW protocol surface for DCN32 clock management.

## Risks And Edge Cases
Message ID drift between driver and PMFW would send the wrong command. Hard-min status polling depends on version gating in the caller because older PMFW may not support `ReturnHardMinStatus`.

## Test Signals
Successful version negotiation, table transfer, DPM queries, hard-min requests, FCLK switch allow/disallow, CAB messages, and hard-min status polling validate these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dalsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c

## Purpose
Implements the DCN32/DCN321 clock manager. It discovers SMU DPM levels, builds bandwidth and watermark tables, sequences live clock updates across SMU hard-min requests and DCCG DTO programming, manages UCLK/FCLK pstate policy, handles DTBCLK switching, and exposes memory-clock control hooks.

## Important APIs, Types, And Functions
- `dcn32_clk_mgr_construct` selects register tables for DCN32 versus DCN321, reads dentist VCO/boot clocks/spread-spectrum state, allocates bandwidth params and a GART watermark table.
- `dcn32_init_clocks` queries SMU for DCF/SOC/DTB/DISP/DPP/UCLK/FCLK DPM levels, applies debug floors and 1950 MHz display clock caps, marks DPM presence, and builds watermark ranges through FPU helpers.
- `dcn32_update_clocks` is the main runtime transition path for DCFCLK, deep-sleep DCFCLK, UCLK, FCLK pstate permission, DISPCLK, DPPCLK, DTBCLK, CAB, and DMCU PSR wait-loop updates.
- `dcn32_update_clocks_update_dpp_dto`, `dcn32_update_clocks_update_dtb_dto`, and `dcn32_update_clocks_update_dentist` sequence DCCG and dentist divider programming.
- Memory hooks include `dcn32_set_hard_min_memclk`, `dcn32_set_hard_max_memclk`, `dcn32_get_memclk_states_from_smu`, `dcn32_set_max_memclk`, and `dcn32_set_min_memclk`.

## Control Flow
Initialization starts with a SMU presence/version check, then queries each PPCLK with `dcn32_init_single_clock`; a fine-grained DPM response becomes two levels, while discrete DPM reports a fixed count. Runtime updates first handle boot/resume force-reset, active display count, display count notification, FCLK pstate support messages, DCFCLK/deep-sleep hard-mins, UCLK pstate lock/unlock, DMCUB MCLK-ack policy, dramclk hard-mins, and CAB num-ways messages. It then rounds DISPCLK/DPPCLK to dentist-realizable values and sequences dentist/DTO updates differently for clock lowering versus raising.

## State And Persistence
Persistent state includes `clk_mgr->base.bw_params`, `wm_range_table`/address, `smu_present`, `dpm_present`, SMU version, `dentist_vco_freq_khz`, boot snapshot, spread-spectrum fields, current `dc_clocks`, and DCCG per-pipe DTO state. UCLK/FCLK pstate support, `num_ways`, and `dc_mode_softmax_memclk` are carried across updates.

## Dependencies And Integration Points
Integrates with DCN30 SMU helpers, DCN32-specific SMU messages, DCCG, DMCU, DML FPU watermark construction, BIOS spread-spectrum tables, link/service helpers, resource-pool bounding-box updates, and ASIC revision macros for DCN321 register layout.

## Risks And Edge Cases
Clock sequencing is order-sensitive: lowering DPPCLK requires DTO changes before refclk lowering, while raising requires refclk first. Dentist divider transitions to/from DID 127 need FIFO pixel add/drop workarounds. UCLK hard-min policy depends on pstate support and dc-mode softmax configuration. If DPM levels are missing, the code patches defaults and updates the bounding box. Several debug masks can suppress individual clock updates, making state comparisons harder.

## Test Signals
Test SMU version/header negotiation, fine-grained and discrete DPM queries, DPM-absent fallback patching, DCN32 versus DCN321 register paths, pstate lock/unlock for UCLK and FCLK, SubVP CAB num-ways changes, MCLK DMCUB ack enable/disable, DTBCLK switching, dentist override programming, auto-DPM logs, and memory-clock set/get hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.h

## Purpose
Declares the DCN32 clock-manager lifecycle and the DPP DTO update helper shared with related code.

## Important APIs, Types, And Functions
- `dcn32_init_clocks` initializes SMU/DPM-derived clock tables and current clock state.
- `dcn32_clk_mgr_construct` and `dcn32_clk_mgr_destroy` allocate and release the DCN32 clock-manager backing state.
- `dcn32_update_clocks_update_dpp_dto` is exported so other DCN variants can reuse the per-DPP DTO update behavior.

## Control Flow
No executable flow is present. The prototypes define the integration boundary between ASIC construction, generic clock-manager function tables, and helper reuse.

## State And Persistence
State is owned by `struct clk_mgr_internal` in the implementation; this header does not declare a DCN32-specific wrapper.

## Dependencies And Integration Points
The prototypes reference `struct clk_mgr`, `struct clk_mgr_internal`, `struct dc_context`, `struct pp_smu_funcs`, `struct dccg`, and `struct dc_state` from broader display headers included by callers.

## Risks And Edge Cases
Because this header does not include the type definitions itself, include order matters for translation units using it. Exporting the DTO helper means callers must obey the same safe-to-lower semantics as DCN32.

## Test Signals
Build coverage and successful construction/init/update/destroy dispatch through the generic clock manager validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.c

## Purpose
Implements DCN32-specific DALSMC mailbox helpers on top of DAL message, argument, and response registers.

## Important APIs, Types, And Functions
- `dcn32_smu_send_msg_with_param` sends ordinary DALSMC transactions and optionally returns the output argument.
- Delay-aware variants aggregate polling time for hard-min status diagnostics.
- `dcn32_smu_set_hard_min_by_freq` issues hard-min clock requests and, on supporting PMFW versions, polls `ReturnHardMinStatus`.
- Other public helpers send FCLK pstate support, CAB num-ways for UCLK pstate, watermark table transfer, PME workaround, and DMCUB MCLK ack wait policy.

## Control Flow
Transactions wait for a nonzero response, clear it, write the argument, write the message ID, trace the message, then wait for `DALSMC_Result_OK`. Hard-min status support is gated by ASIC revision and SMU version. When supported, the helper repeatedly queries hard-min status until the requested clock bit appears or a two-second total delay budget expires.

## State And Persistence
The file has no heap state. It mutates PMFW policy and uses static counters to track maximum hard-min wait time and timeout count for diagnostics. PMFW keeps the effective hard-min, FCLK switch, CAB, and DMCUB wait states.

## Dependencies And Integration Points
Uses DALSMC constants, DCN32 SMU13 table IDs, register helpers, SMU trace macros, and `clk_mgr_internal` context. It is called by `dcn32_clk_mgr.c` alongside common DCN30 SMU helpers.

## Risks And Edge Cases
The base send helper ignores the initial wait result and proceeds to clear/send, so a wedged response register can still lead to a failed transaction after the second wait. Hard-min status polling only works on specific PMFW versions. The DMCUB wait helper uses literal message ID `0x14`, matching `SetAlwaysWaitDmcubResp`; future constant changes would be easy to miss.

## Test Signals
Trace logs for SMU messages and delays, hard-min status success and timeout paths, FCLK pstate toggles, CAB changes, watermark transfer, PME workaround, and DMCUB MCLK ack toggles provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.h

## Purpose
Declares DCN32-specific SMU message helpers and small protocol constants not fully covered by common DCN30 headers.

## Important APIs, Types, And Functions
- `FCLK_PSTATE_NOTSUPPORTED` and `FCLK_PSTATE_SUPPORTED` encode the PMFW argument for FCLK switch allowance.
- `dcn32_smu_send_fclk_pstate_message`, `dcn32_smu_send_cab_for_uclk_message`, `dcn32_smu_transfer_wm_table_dram_2_smu`, `dcn32_smu_set_pme_workaround`, `dcn32_smu_set_hard_min_by_freq`, and `dcn32_smu_wait_for_dmub_ack_mclk` are the exported helpers.
- The header temporarily defines `DALSMC_MSG_SetCabForUclkPstate` and `DALSMC_Result_OK` for local availability.

## Control Flow
No executable flow. The prototypes define which DCN32-only mailbox operations are available to the clock manager.

## State And Persistence
No state is declared. Callers change PMFW state through the declared functions.

## Dependencies And Integration Points
Includes `core_types.h` and `dcn30/dcn30_clk_mgr_smu_msg.h` so DCN32 helpers can coexist with common SMU helpers.

## Risks And Edge Cases
Duplicate local definitions can drift from `dalsmc.h`; this is explicitly marked as temporary. Consumers need to pass PPCLK IDs and MHz frequencies consistent with the PMFW hard-min contract.

## Test Signals
Build coverage, successful hard-min programming, FCLK pstate messaging, CAB messaging, and watermark transfer validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_smu13_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_smu13_driver_if.h

## Purpose
Defines the SMU13 driver-interface subset needed by the DCN32 clock manager: PPCLK identifiers, external watermark table layout, and PMFW table IDs.

## Important APIs, Types, And Functions
- `PPCLK_e` enumerates clock domains used by DPM and hard-min messages, including DISPCLK, DPPCLK, DPREFCLK, DCFCLK, DTBCLK, UCLK, FCLK, SOC, GFX, and media clocks.
- `WatermarkRowGeneric_t`, `Watermarks_t`, and `WatermarksExternal_t` describe the PMFW watermark upload format.
- `WATERMARKS_FLAGS_e` names watermark row meanings.
- `TABLE_*` constants identify SMU table types; DCN32 uses `TABLE_WATERMARKS`.

## Control Flow
This is a pure ABI header. Control flow appears in callers that use `PPCLK_e` values in SMU messages or fill `WatermarksExternal_t`.

## State And Persistence
Watermark tables are persisted in GPU memory before transfer to PMFW. PPCLK IDs and table IDs become encoded message arguments but allocate no state.

## Dependencies And Integration Points
Used by `dcn32_clk_mgr.c` and `dcn32_clk_mgr_smu_msg.c` to query DPM levels, set hard-min clocks, and transfer watermark tables.

## Risks And Edge Cases
ABI layout and enum ordering must match PMFW. `WatermarksExternal_t` includes spare and MMHUB padding fields that must be preserved even though the driver fills only a small row subset.

## Test Signals
Correct DPM responses per PPCLK, successful watermark table transfer, and PMFW driver interface version checks are the primary validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_smu13_driver_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn351_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn351_clk_mgr.c

## Purpose
Specializes DCN35 clock-manager construction for DCN351 register offsets and masks before delegating to the shared DCN35 implementation.

## Important APIs, Types, And Functions
- `clk_mgr_regs_dcn351`, `clk_mgr_shift_dcn351`, and `clk_mgr_mask_dcn351` define the DCN351-specific register access table using `CLK_REG_LIST_DCN35` and DCN32-style masks.
- `dcn351_clk_mgr_construct` installs those register tables into the embedded `clk_mgr_internal`, then calls `dcn35_clk_mgr_construct`.

## Control Flow
Construction is a two-step wrapper: preseed DCN351 register metadata, then reuse the generic DCN35 constructor. The shared constructor preserves these tables when `ctx->dce_version == DCN_VERSION_3_51`.

## State And Persistence
The only persistent state set here is the register/shift/mask pointer trio in `clk_mgr->base`, which all later `REG_*` helpers use for clock register access.

## Dependencies And Integration Points
Depends on `dcn35_clk_mgr.h`, DCN35 register-list macros, DCN32 common mask-list macros, and the shared `dcn35_clk_mgr_construct` path. It integrates DCN351 ASIC setup with the DCN35 clock-manager code.

## Risks And Edge Cases
Wrong register offsets would corrupt all subsequent clock reads/writes. The wrapper relies on the shared constructor not overwriting register tables for DCN_VERSION_3_51. Any new DCN351-only registers must be reflected here before construction.

## Test Signals
DCN351 boot should show correct boot snapshot/current clock reads, successful SMU DPM import using DCN351 translation, and no fallback to DCN35 register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn351_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c

## Purpose
Implements the shared DCN35/DCN351 display clock manager. It manages SMU-backed clock programming, DTBCLK/DPP DTOs, watermark and DPM table exchange, spread-spectrum handling, low-power/IPS integration, DPIA host-router bandwidth notification, boot clock snapshots, and FPGA fallback behavior.

## Important APIs, Types, And Functions
- `dcn35_clk_mgr_construct` initializes the manager, allocates GART watermark and DPM buffers, handles DCN351 table translation, imports PMFW DPM data into bandwidth params, configures IPS capability flags, and sets function pointers.
- `dcn35_update_clocks` handles live DCFCLK, deep-sleep DCFCLK, DISPCLK, DPPCLK, DTBCLK, zstate, display idle, DPIA bandwidth, and DMCUB notification transitions.
- `dcn35_init_clocks`, `dcn35_are_clock_states_equal`, `dcn35_notify_wm_ranges`, `dcn35_set_low_power_state`, `dcn35_exit_low_power_state`, `dcn35_is_ips_supported`, and `dcn35_get_max_clock_khz` provide function-table operations.
- Internal helpers manage OTG-disable workarounds, DTB/DPP DTO programming, host-router bandwidth aggregation, VCO and clock register snapshots, spread-spectrum LUT reads, watermark construction, DPM import, and DCN351-to-DCN35 table translation.

## Control Flow
Construction sets default register tables unless DCN351 preseeded them, allocates PMFW-visible buffers, queries SMU, reads VCO and boot clocks, chooses DDR5/LPDDR5 watermarks, reads DPREF spread-spectrum state, imports a DPM table when pstate is enabled, and adjusts IPS config based on PMFW support/version. Runtime updates normalize DTBCLK requests, branch on `safe_to_lower` for zstate/DTB/mission-mode behavior, apply force-min DCFCLK, program hard-min DCFCLK and deep-sleep DCFCLK, floor DPPCLK, wrap DISPCLK changes with the OTG workaround, update DTB DTOs, sequence DPP DTO versus SMU DPPCLK according to lowering/raising, optionally notify host-router bandwidth per DPIA tunnel, and notify DMCUB.

## State And Persistence
Persistent state includes current clocks, `smu_present`, `smu_ver`, static `dcn35_bw_params`, `smu_wm_set`, boot snapshots, spread-spectrum fields, DTBCLK enable/ref frequency, IPS-related DC config changes, and DCCG DTO state. Temporary DPM buffers are freed after construction, while the watermark buffer persists until destruction.

## Dependencies And Integration Points
Integrates with DCN35 SMU helpers, DCCG DTO programming, DMCUB command submission, link service for 128b/132b and DPIA bandwidth, BIOS integrated memory info, DC debug/config flags, DCE/ DCN31 clock helpers, and DC resource-pool bandwidth bounding behavior through populated `clk_bw_params`.

## Risks And Edge Cases
OTG disable logic has several guards for diagnostic mode, HPO/128b132b links, stream changes with active DIG/FIFO, virtual signals, and missing link encoders; mistakes can cause blanking or underflow. DTBCLK disable can be gated by `allow_0_dtb_clk`, while enabling verifies a current-count register before persisting state. DPM import assumes valid memory pstate, FCLK, DCF, SOC, DISP, and DPP counts. The destroy path frees the watermark allocation as `FRAME_BUFFER` even construction used `GART`, which is a notable allocation-type consistency risk. DCN351 translation must stay aligned with both PMFW table layouts.

## Test Signals
Test DCN35 and DCN351 construction, SMU present/absent, DPM import and DCN351 translation, IPS supported/unsupported and old-PMFW config fallback, DDR5 versus LPDDR5 watermarks, DTBCLK zero/nonzero transitions, OTG workaround cases including HPO and virtual streams, DPIA host-router bandwidth notifications, DPPCLK lowering/raising order, DMCUB clock notify, and destroy-time memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c -->
