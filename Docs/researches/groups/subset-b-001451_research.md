# subset-b-001451 MPC research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h

## Purpose
This header defines the DCN2.0 Multiple Plane Compositor register interface and public helper surface. It extends the DCN1 MPC base with MPCC blend gain, output gamma, output CSC, denormalization, and MPCC OGAM memory power control registers. The file is mostly macro infrastructure that feeds generated register, shift, and mask tables for ASIC-specific compilation units.

## Important APIs, types, and functions
The main type is `struct dcn20_mpc`, which embeds `struct mpc` and stores `mpcc_in_use_mask`, `num_mpcc`, and pointers to DCN2 register, shift, and mask tables. `struct dcn20_mpc_registers`, `struct dcn20_mpc_shift`, and `struct dcn20_mpc_mask` are produced from `MPC_REG_VARIABLE_LIST_DCN2_0` and `MPC_REG_FIELD_LIST_DCN2_0`. Public entry points include `dcn20_mpc_construct`, `mpc2_update_blending`, `mpc2_set_denorm`, `mpc2_set_denorm_clamp`, `mpc2_set_output_csc`, `mpc2_set_ocsc_default`, `mpc2_set_output_gamma`, `mpc2_assert_idle_mpcc`, `mpc2_assert_mpcc_idle_before_connect`, and `mpc20_power_on_ogam_lut`.

## Control flow and state
The header does not implement control flow itself; it declares operations used by DCN2 and inherited by later generations. The macros enumerate per-MPCC registers for OGAM RAM A/B region metadata, LUT index/data writes, blend gains, memory power, and per-OPP CSC/denorm controls. Runtime state is split between software bookkeeping in `struct dcn20_mpc` and hardware state in indexed MPC/MPCC/OGAM registers. There is no disk persistence; state survives only as driver memory plus programmed hardware registers.

## Dependencies and integration points
The file depends on `dcn10/dcn10_mpc.h`, AMD DC register helper conventions (`SRII`, `SR`, `SF`), `MAX_MPCC`, `MAX_OPP`, and common color-management types such as `pwl_params`, `mpc_denorm_clamp`, and `mpc_output_csc_mode`. It is an integration layer for display core resource construction and for later DCN30/DCN32/DCN401 headers that reuse or extend DCN2 field lists.

## Risks
The macro lists must match hardware register naming exactly; missing or misordered fields silently corrupt generated register tables. OGAM LUT programming is banked, so mismatched A/B register groups can update the inactive or wrong RAM. Power control fields must be valid before LUT writes or gamma programming can fail on powered-down memory. Bounds are implied by callers and array sizes, so invalid MPCC or OPP indices are a high-impact risk.

## Test signals
Useful signals are successful DC bring-up, no register access faults during `dcn20_mpc_construct`, correct blend gain changes, color-depth denorm behavior across 6/8/10/12 bpc modes, default and coefficient CSC programming, output gamma enable/disable, and debug/assert coverage for MPCC idle transitions before connect/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.c

## Purpose
This implementation provides the DCN3 MPC function table and the programming sequences for output gamma, denorm, output CSC, gamut remap, DWB muxing, output rate control disablement, RMU shaper LUTs, and RMU 3D LUTs. It composes older DCN1 plane topology helpers and DCN2 blending helpers with DCN3 color-management hardware.

## Important APIs, types, and functions
Constructor `dcn30_mpc_construct` initializes `struct dcn30_mpc`, assigns `dcn30_mpc_funcs`, stores register tables, records `num_mpcc` and `num_rmu`, and initializes every `mpcc` with `mpc3_init_mpcc`. Exported operations include `mpc3_mpc_init`, `mpc3_mpc_init_single_inst`, `mpc3_set_output_gamma`, `mpc3_program_shaper`, `mpc3_program_3dlut`, `mpcc3_acquire_rmu`, `mpc3_set_gamut_remap`, `mpc3_get_gamut_remap`, `mpc3_set_output_csc`, `mpc3_set_ocsc_default`, DWB helpers, and `mpc3_read_reg_state`.

## Control flow and state
Initialization first calls DCN1 MPC init, then disables MPC output rate and flow control for each valid OPP mux. OGAM programming checks debug color-management bypass, disables on `NULL` params, otherwise enables OGAM, chooses the inactive RAM bank from current hardware status, powers memory, writes region metadata and LUT samples, then switches bank select. Shaper and 3D LUT programming follow the same double-buffering pattern for RMU resources. 3D LUT data is split across four tetrahedral RAM masks and can be programmed as 12-bit paired values or packed 30-bit values. RMU acquisition reads mux status, returns an already-connected RMU, connects an idle one, or returns `-1`.

## Dependencies and integration points
The file depends on `reg_helper.h`, `dcn30_cm_common.h`, `dcn10_cm_common.h`, `basics/conversion.h`, `dc.h`, inherited MPC helpers (`mpc1_*`, `mpc2_*`), color helpers (`cm_helper_program_gamcor_xfer_func`, `cm_helper_program_color_matrices`, `cm_helper_read_color_matrices`), and matrix conversion helpers. It plugs into `struct mpc_funcs`, which higher display core code calls through the generic MPC interface.

## State and persistence behavior
Software state is held in `base.mpcc_array`, `num_mpcc`, `num_rmu`, and register table pointers. Hardware state lives in MPCC, OPP, DWB, OGAM, RMU mux, shaper, and 3D LUT registers. There is no durable persistence. Low-power state is controlled by debug flags and memory power registers; programming sequences temporarily force memory active and may restore low-power allowance afterward.

## Risks
RMU handling only explicitly covers RMU 0 and 1 in several helpers despite `MAX_RMU` being 3. Some invalid inputs trigger `BREAK_TO_DEBUGGER` rather than clean error propagation. LUT programming assumes entry counts and array layouts match hardware expectations, including even counts for 12-bit paired writes. Register waits have bounded retries, so power sequencing failures can leave partially programmed color blocks. Gamut remap double-buffering depends on correct `*_MODE_CURRENT` reads.

## Test signals
Important signals include no underflow or blanking during init, DWB mux idle status returning `0xf` when disabled, output gamma bank flips without visible artifacts, shaper and 3D LUT enable/disable paths with low-power enabled and disabled, RMU acquisition/release under multi-plane use, CSC defaults for multiple color spaces, gamut remap readback matching programmed matrices, and register-state dumps showing expected MPCC topology and color block modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h

## Purpose
This header declares the DCN3 MPC register schema and public interface. It builds on DCN2, adds DWB mux registers, RMU global and per-RMU registers, shaper LUT registers, 3D LUT registers, gamut remap controls, output rate/flow-control fields, and DCN3.2-compatible movable color-management register variables.

## Important APIs, types, and functions
`struct dcn30_mpc` embeds `struct mpc` and carries MPCC/RMU counts plus register, shift, and mask tables. `MAX_RMU` is defined as 3. `MPC_REG_LIST_DCN3_0`, `MPC_RMU_REG_LIST_DCN3AG`, `MPC_REG_VARIABLE_LIST_DCN3_0`, `MPC_REG_VARIABLE_LIST_DCN32`, `MPC_COMMON_MASK_SH_LIST_DCN3_0`, and variant lists for DCN30/DCN303 generate ASIC register bindings. Declared APIs include construction, MPC init, shaper and 3D LUT programming, RMU mux acquisition/status, denorm, output CSC, output gamma, gamut remap set/get, DWB mux, rate control, OGAM power, and register-state readback.

## Control flow and state
The header defines the shape consumed by `dcn30_mpc.c`; actual control flow is table-driven through `struct mpc_funcs`. The register lists describe three major state domains: MPCC plane composition, OPP output formatting, and color-management LUT/matrix hardware. RMU state is separate from MPCC state and is multiplexed to an MPCC through `MPC_RMU_CONTROL`.

## Dependencies and integration points
It includes `dcn20/dcn20_mpc.h` and depends on AMD register-generation macros and common display color types. Later DCN32, DCN401, and DCN42 code reuse the DCN30 structure layout and many function prototypes, so this header is a compatibility hinge between shared DCN3 behavior and later per-MPCC MCM implementations.

## State and persistence behavior
State is either software bookkeeping in `struct dcn30_mpc` or volatile hardware register contents. The large register variable and mask lists are compile-time descriptions, not runtime storage for values. No file or firmware persistence is provided by this layer.

## Risks
The header has multiple similar mask-list variants for DCN3.0 and DCN3.03, with some fields intentionally commented out in one variant; picking the wrong list can expose unavailable status fields. `SRII_MPC_RMU` is conditionally redefined, so macro conflicts can break register addresses. The register variable list includes DCN32 additions, making structure consumers sensitive to assumed layout. RMU count and `MAX_RMU` must match the actual ASIC tables.

## Test signals
Compile-time signals are successful register table construction for each ASIC include path. Runtime signals include correct function-table hookup, valid DWB and RMU mux fields, gamut remap mode current reads, memory power status fields, and successful color-management operations on both DCN3.0 and DCN3.03 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c

## Purpose
This file implements the DCN3.2 MPC variant. It keeps DCN3 plane, DWB, CSC, denorm, OGAM, and gamut-remap behavior, but moves shaper and 3D LUT programming from shared RMU units into per-MPCC movable color-management (`MPCC_MCM`) blocks and adds a post-blend 1D LUT programming path.

## Important APIs, types, and functions
Key functions include `mpc32_mpc_init`, `mpc32_power_on_blnd_lut`, `mpc32_program_post1dlut`, `mpc32_program_shaper`, `mpc32_program_3dlut`, all supporting RAM A/B settings and PWL data writers, `mpc32_set_3dlut_mode`, and `dcn32_mpc_construct`. The `dcn32_mpc_funcs` table points generic MPC operations to inherited DCN1/DCN2/DCN3 helpers while overriding `program_shaper`, `program_3dlut`, and `program_1dlut`.

## Control flow and state
Initialization calls `mpc3_mpc_init` and configures MCM and OGAM memory low-power mode when debug flags allow it. Post-1D LUT programming selects the inactive bank, powers memory, writes transfer-function region registers and PWL entries, appends a final base value, then enables mode 2 and selects RAM A or B. Shaper programming is similar but targets `MPCC_MCM_SHAPER_*` registers. 3D LUT programming chooses the inactive 3D LUT RAM bank, writes four tetrahedral RAM sections using write masks, programs the LUT size, and may power memory back down.

## Dependencies and integration points
Dependencies include DCN30 headers and color helpers, conversion utilities, register helpers, and inherited MPC functions. The implementation is used through the generic MPC interface and is also reused by DCN401 for the low-level MCM memory-population routines.

## State and persistence behavior
DCN3.2 removes RMU acquisition/release from the function table because MCM state is per MPCC. Runtime state is in MPCC_MCM mode, select, memory power, LUT index/data, and movable location registers, plus software MPCC structures initialized with `mpc3_init_mpcc`. There is no persistent storage beyond hardware state across modesets or driver lifetime.

## Risks
The shaper settings guard region programming with `if (curve)`, but still assumes valid corner points and LUT data arrays. 12-bit 3D LUT programming reads pairs, so odd entry counts would be unsafe. Power-on helpers break into the debugger on memory state failures but do not return errors. `mpc32_set_3dlut_mode` hardcodes movable CM location to pre-blend and has a TODO for true movable support.

## Test signals
Useful validation includes post-1D LUT enable/disable with both banks, shaper and 3D LUT programming while toggling memory low-power flags, visual color transform correctness for 9-cube and 17-cube LUTs, no corruption when programming multiple MPCCs independently, and function-table checks confirming RMU callbacks are intentionally `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h

## Purpose
This header declares the DCN3.2 MPC register list and helper prototypes. It extends DCN3 with per-MPCC movable color-management registers for shaper LUT, 3D LUT, post-1D LUT, and their memory power controls.

## Important APIs, types, and functions
`MPC_REG_LIST_DCN3_2` adds `MPCC_MOVABLE_CM_LOCATION_CONTROL`, `MPCC_MCM_SHAPER_*`, `MPCC_MCM_3DLUT_*`, `MPCC_MCM_1DLUT_*`, and `MPCC_MCM_MEM_PWR_CTRL` registers. `MPC_COMMON_MASK_SH_LIST_DCN32` maps fields for blend, denorm, OGAM, MCM shaper, MCM 3D LUT, MCM 1D LUT, and memory power state. `struct dcn32_mpc_registers` reuses `MPC_REG_VARIABLE_LIST_DCN3_0` and `MPC_REG_VARIABLE_LIST_DCN32`. Prototypes expose DCN3.2 construction, init, shaper, 3D LUT, post-1D LUT, memory power, configuration, and low-level LUT RAM writers.

## Control flow and state
The header does not implement behavior, but it defines the state topology used by `dcn32_mpc.c`: each MPCC owns its MCM shaper, 3D LUT, and 1D LUT state. This contrasts with DCN3 RMU mux state and simplifies per-plane color programming at the cost of a much larger per-MPCC register surface.

## Dependencies and integration points
It includes both DCN20 and DCN30 MPC headers and is consumed by DCN32 implementation plus later DCN401 code that reuses DCN32 MCM programming helpers. The exposed functions are also referenced through `struct mpc_funcs` callbacks for generic display color management.

## State and persistence behavior
All register lists describe volatile hardware state. Bank selection, mode current, LUT indices, LUT data, and memory power fields are held in hardware. The software side is inherited from `struct dcn30_mpc`; no durable persistence exists.

## Risks
This header is highly sensitive to register macro coverage. Missing one channel-specific field can break only one color component, making failures visually subtle. Several helpers are declared for reuse by later files, so signature changes have broad impact. The DCN32 register structure type is effectively a DCN30-compatible layout with extra variables, which requires careful casting and constructor use.

## Test signals
Compile and link tests should cover all declared helpers. Runtime signals include valid register table generation for every MCM block, successful banked post-1D/shaper/3D LUT programming, memory power state transitions, and absence of RMU dependencies in DCN3.2 color-management paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.c

## Purpose
This file implements the DCN4.01 MPC function table and newer color-management controls. It reuses DCN32 MCM LUT writers, adds generic LUT populate/mode/read-write-control callbacks, adds movable color-management location selection, supports 3D LUT fast-load status/select, and expands gamut remap to OGAM plus first and second MCM gamut-remap blocks.

## Important APIs, types, and functions
Important functions are `mpc401_update_3dlut_fast_load_select`, `mpc401_get_3dlut_fast_load_status`, `mpc401_set_movable_cm_location`, `mpc401_populate_lut`, `mpc401_program_lut_mode`, `mpc401_program_lut_read_write_control`, `mpc_program_gamut_remap`, `mpc_read_gamut_remap`, `mpc401_set_gamut_remap`, `mpc401_get_gamut_remap`, `mpc401_get_lut_mode`, and `dcn401_mpc_construct`. The `dcn401_mpc_funcs` table adds the new generic LUT and fast-load callbacks while retaining DCN32 shaper, 3D LUT, and 1D LUT operations.

## Control flow and state
`mpc401_populate_lut` separates memory population from mode selection. For 1D and shaper LUTs it powers/configures the target RAM bank and delegates to DCN32 helpers; for 3D LUT it writes the four tetrahedral RAM partitions without selecting the active mode. `mpc401_program_lut_mode` enables or disables one MCM LUT class and switches RAM bank or size. `mpc401_program_lut_read_write_control` prepares the selected bank and bit depth for host writes. Gamut remap programming chooses the relevant block, writes coefficient set A or B, then updates that block's mode selector.

## Dependencies and integration points
The file depends on `dcn401_mpc.h`, `mpc.h`, conversion helpers, DCN10 color matrix helpers, and DCN32 LUT helper routines. It integrates with newer display color-management code through generic `populate_lut`, `program_lut_mode`, `program_lut_read_write_control`, and `get_lut_mode` callbacks rather than only the legacy `program_3dlut` style.

## State and persistence behavior
Software state is initialized in `struct dcn401_mpc` and MPCC arrays. Hardware state includes MCM LUT mode/current fields, bank selects, 3D LUT size, fast-load select/status, movable location, OGAM gamut remap, and two MCM gamut remap blocks. State is volatile and coordinated by double-buffered A/B coefficient and LUT banks.

## Risks
The 3D LUT populate path assumes that read/write control and bank selection have been prepared by the caller; wrong sequencing can write the wrong bank. Fast-load status exposes underflow flags but does not itself recover. `mpc401_cm_lut_size_to_3dlut_size` asserts on unsupported sizes. Gamut remap switch statements initialize only fields relevant to supported mode selections, so invalid enum values can lead to no-op programming with limited diagnostics.

## Test signals
Useful tests include generic LUT populate followed by explicit mode switch, `get_lut_mode` readback for shaper/1D/3D LUTs, fast-load select and done/underflow status reads, movable CM before/after selection, gamut remap set/get for all three block IDs, and regression checks that DCN32 inherited programming still works through the DCN4.01 function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.h

## Purpose
This header defines the DCN4.01 MPC register schema and public API. It extends DCN30/DCN32 register coverage with two MCM gamut-remap blocks, fast-load controls for MCM 3D LUT, and DCN4.01-specific shift/mask/register structures.

## Important APIs, types, and functions
`MPC_REG_VARIABLE_LIST_DCN4_01` combines DCN3.0 and DCN3.2 variables with first and second MCM gamut-remap coefficient registers and 3D LUT fast-load select/status registers. `MPC_COMMON_MASK_SH_LIST_DCN4_01` maps fields for MCM gamut-remap modes/current modes, coefficient components, and fast-load done and underflow flags. `struct dcn401_mpc_registers`, `struct dcn401_mpc_shift`, `struct dcn401_mpc_mask`, and `struct dcn401_mpc` define the concrete DCN4.01 object. Public prototypes cover construction, movable CM location, LUT population, LUT mode/read-write controls, gamut remap set/get/read/program, and fast-load status/select.

## Control flow and state
The header declares a more command-oriented interface than DCN32: callers can separately populate a LUT bank, configure read/write control, program active mode, and query mode. It also exposes block-specific gamut remap operations so color-management code can target OGAM, first MCM, or second MCM remap stages.

## Dependencies and integration points
It includes `dcn30/dcn30_mpc.h` and `dcn32/dcn32_mpc.h`, making DCN4.01 a layered extension rather than a separate MPC implementation. It depends on shared enums such as `MCM_LUT_ID`, `dc_cm_lut_size`, `mpcc_gamut_remap_id`, and `mpcc_movable_cm_location`, plus generic `struct mpc`.

## State and persistence behavior
State is volatile register state for coefficient sets, modes, fast-load status, LUT banks, and MPCC bookkeeping. The structure mirrors earlier MPC state with `mpcc_in_use_mask`, `num_mpcc`, `num_rmu`, and register metadata pointers.

## Risks
The register list adds many paired A/B coefficient registers; mapping only C11/C12 and C33/C34 into helper structs may hide assumptions about helper support for full 3x4 matrices. Duplicate prototype declaration for `mpc401_update_3dlut_fast_load_select` is harmless but noisy. Type compatibility with DCN32 helper functions depends on shared leading structure layout and matching register variable lists.

## Test signals
Compile-time tests should validate register table generation for all new fields. Runtime signals include mode/current readback for both MCM gamut-remap blocks, fast-load status flag reads, LUT bank population and activation, and construction of a `dcn401_mpc` with correct callback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn401/dcn401_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c

## Purpose
This file implements the DCN4.2 MPC function table and RMCM-specific operations. It inherits most DCN4.01 and DCN3.2 behavior but adds DCN4.2 blend defaults, wider alpha/gain programming through `MPCC_CONTROL2`, RMCM shaper/3D LUT fast-load control, RMCM 3D LUT size, bias/scale, bit-depth configuration, and enhanced MPCC state readback for RMCM debugging.

## Important APIs, types, and functions
Key functions are `mpc42_init_mpcc`, `mpc42_update_blending`, `mpc42_power_on_rmcm_shaper_3dlut`, `mpc42_configure_rmcm_shaper_lut`, `mpc42_program_rmcm_shaper_luta_settings`, `mpc42_program_rmcm_shaper_lutb_settings`, `mpc42_program_rmcm_shaper_lut`, `mpc42_enable_3dlut_fl`, `mpc42_update_3dlut_fast_load_select`, `mpc42_populate_rmcm_lut`, `mpc42_program_rmcm_lut_read_write_control`, `mpc42_program_lut_mode`, `mpc42_program_rmcm_3dlut_size`, `mpc42_program_rmcm_3dlut_fast_load_bias_scale`, `mpc42_program_rmcm_bit_depth`, `mpc42_set_fl_config`, `mpc42_read_mpcc_state`, and `dcn42_mpc_construct`.

## Control flow and state
Construction initializes `struct dcn42_mpc`, assigns `dcn42_mpc_funcs`, and seeds MPCC defaults with 12-bit global alpha/gain. Blending writes mode fields to `MPCC_CONTROL`, alpha/gain to `MPCC_CONTROL2`, and per-plane gain registers, then mirrors the config in software. RMCM shaper programming powers memory, selects RAM A/B, writes region metadata if present, streams packed PWL samples, then powers memory down. Fast-load setup disconnects, prepares write masks, programs bit depth, RAM bank, bias/scale, 3D LUT size/mode, connects to a HUBP, and enables RMCM routing.

## Dependencies and integration points
The file depends on `dcn42_mpc.h`, `dcn401_mpc` helpers through the function table, generic `mpc.h`, register helpers, and common color conversion support. It fills the nested `.rmcm` callback table inside `struct mpc_funcs`, while retaining DCN401 generic MCM callbacks for the existing MCM path.

## State and persistence behavior
State spans software MPCC blend config, legacy MCM registers, and RMCM registers. `mpc42_read_mpcc_state` extends base MPCC readback with RMCM 3D LUT memory power, mode, read/write control, norm factor, fast-load select/status, bias/scale, shaper power/mode/write state, offsets/scales, region fields, and RMCM routing control. No durable persistence is provided.

## Risks
Only MPCC instances below 2 get RMCM state readback. Fast-load control has sequencing comments documenting required clock and memory behavior, but this file does not manage external pipe clock gating itself. `mpc42_enable_3dlut_fl` hardcodes RMCM connection value 0 when enabled and 0xf when disabled. RMCM LUT population currently covers shaper PWL, while 3D LUT content is expected through fast-load/config paths. Power status failures break to debugger instead of returning an error.

## Test signals
Strong validation signals include blend alpha/gain correctness at 12-bit values, RMCM memory power wait success, shaper bank switching, fast-load enable/disable and HUBP select, 3D LUT size for 17x17x17 and 33x33x33-style enum paths, bias/scale and 10-bit/12-bit bit-depth programming, RMCM state dump accuracy, and no underflow flags during fast-load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c -->
