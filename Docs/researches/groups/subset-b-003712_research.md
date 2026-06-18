# Research: subset-b-003712

Grouped source research for subset B work item `subset-b-003712`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btc_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btc_dpm.c

## Purpose
This file implements dynamic power management for AMD Radeon BTC-era ASICs, covering Barts, Turks, and Caicos. It programs static clock-gating/light-sleep register sequences, initializes and controls the SMC DPM state table, adjusts requested power states against clock, voltage, display, PCIe, UVD, and memory-timing constraints, and exposes the BTC DPM hooks used by the Radeon ASIC table.

## Important APIs, Types, and Functions
Public driver hooks include `btc_dpm_init`, `btc_dpm_setup_asic`, `btc_dpm_enable`, `btc_dpm_disable`, `btc_dpm_pre_set_power_state`, `btc_dpm_set_power_state`, `btc_dpm_post_set_power_state`, `btc_dpm_fini`, `btc_dpm_vblank_too_short`, `btc_dpm_get_current_sclk`, `btc_dpm_get_current_mclk`, `btc_dpm_get_sclk`, `btc_dpm_get_mclk`, and `btc_dpm_debugfs_print_current_performance_level`. Shared helper APIs declared in `btc_dpm.h` include `btc_read_arb_registers`, `btc_program_mgcg_hw_sequence`, `btc_skip_blacklist_clocks`, `btc_adjust_clock_combinations`, `btc_apply_voltage_dependency_rules`, `btc_get_max_clock_from_voltage_dependency_table`, `btc_apply_voltage_delta_rules`, `btc_dpm_enabled`, `btc_reset_to_default`, and `btc_notify_uvd_to_smc`.

The file is built around `struct evergreen_power_info`, its embedded `struct rv7xx_power_info`, `struct radeon_ps`, `struct rv7xx_ps`, `struct rv7xx_pl`, `RV770_SMC_STATETABLE`, and Evergreen memory-controller register table structures. Large static triplet arrays hold register, value, and mask sequences for CGCG/CGLS, MGCG, and SYSLS defaults/enables/disables for Barts, Turks, and Caicos.

## Control Flow
Initialization allocates `evergreen_power_info`, parses ATOMBIOS power tables, creates a display-clock voltage dependency table, establishes default response times, thresholds, arbitration timing defaults, clock-gating capability flags, PCIe Gen2 policy, thermal policy, ULV defaults, valid SCLK values, and DC clock limits. `btc_dpm_setup_asic` loads memory-controller firmware, discovers memory and PCIe state, reads boot clock and voltage registers, snapshots memory arbitration registers, advertises PCIe Gen2 if ACPI supports performance requests, and enables ACPI PM.

Enable flow applies default clock-gating sequences, rejects an already running SMC, enables voltage/MVDD/backbias/spread-spectrum/thermal controls as configured, optionally builds dynamic AC memory timing tables, programs RV770/Cypress DPM timing and throttling parameters, enables dynamic PCIe Gen2, uploads firmware, locates SMC tables, builds the BTC SMC state table, uploads MC timing tables, starts SMC/DPM, enables SCLK and optional MCLK control, applies clock-gating enable sequences, enables thermal auto-throttle, initializes stutter mode, and snapshots the boot power state as current.

Power-state transition flow copies the requested state, applies adjustment rules, disables ULV, restores boot arbitration timing, restricts performance levels before switching, performs optional PCIe link-speed notifications, coordinates UVD clocks, halts the SMC, updates activity thresholds/UVD soft registers, uploads the software state and optional MC timing table, programs memory timing parameters, resumes SMC, requests the software state, restores UVD clocks, performs post PCIe notifications, and conditionally re-enables ULV when the low state matches the ULV memory/VDDCI requirements. Post-transition commits requested state into current state.

Disable flow clears voltage controller setup, disables thermal protection and dynamic PCIe Gen2, disables thermal IRQ delivery, disables clock-gating sequences, stops DPM, sends SMC reset-to-defaults, waits for display reset state to clear before stopping the SMC, disables spread spectrum, and restores current state to the boot state.

## State and Persistence Behavior
Persistent runtime state is stored in `rdev->pm.dpm.priv` as `evergreen_power_info`, in `rdev->pm.dpm.dyn_state`, in SMC SRAM tables, and in hardware registers. Current and requested Radeon power states are copied into `eg_pi->current_rps/current_ps` and `eg_pi->requested_rps/requested_ps` with corrected `ps_priv` pointers. The SMC table persists in SRAM until reset/disable, while clock-gating and memory-timing register programming persists in hardware until explicitly changed or reset.

Dynamic AC timing state is initialized from ATOMBIOS memory-controller tables, expanded with LP/S0 register aliases and special MRS/EMRS registers, marked with valid flags only where entries differ, and uploaded during state changes. ULV state persists as SMC state and selected hardware timing until disabled or replaced by another transition. `btc_dpm_fini` frees per-power-state private data, power-state arrays, the private power-info block, the display-clock voltage dependency table, and extended power-table allocations.

## Dependencies and Integration Points
This file depends on Radeon register macros, ATOMBIOS parsers, RV770 and Cypress DPM helpers, Evergreen power structures, SMC message and SRAM copy helpers, PCIe port register access, ACPI PCIe performance requests, UVD state classification, thermal IRQ handling, memory-controller firmware loading, and debugfs `seq_file` output. `radeon_asic.c` wires its DPM hooks into the BTC ASIC entry, while `ni_dpm.c` and `si_dpm.c` reuse several BTC helper functions for later ASIC families.

The register names and bitfields come from `btcd.h` and related Radeon headers. The public helper surface is declared by `btc_dpm.h`, and defaults such as UVD activity thresholds and CG ULV constants also come from that header.

## Risks
The file directly programs power, voltage, memory, and PCIe hardware registers, so ordering mistakes can hang the GPU, corrupt display output, or cause unstable voltage/clock combinations. VBIOS MC timing table bounds are checked, but malformed firmware still disables dynamic AC timing or returns errors. Clock and voltage adjustment is heavily policy-based; regressions can appear only under multi-monitor, short-vblank, UVD, DC power, or Gen2 PCIe cases. `btc_valid_sclk` contains a suspicious `11500` entry among otherwise 5,000-step values, which may be intentional legacy data but looks like a potential typo for `115000`.

ULV programming is especially sensitive because it rewrites ARB[0] timing and requires low-state memory/VDDCI compatibility. The recursive blacklist skipper only changes SCLK upward and relies on the valid clock table to terminate. Error paths in enable can leave some hardware features enabled after a later step fails because cleanup is handled by higher-level DPM teardown rather than local unwinding.

## Test Signals
Useful signals include kernel build coverage for BTC, NI, and SI DPM users; boot and module load on Barts/Turks/Caicos boards; suspend/resume and DPM enable/disable cycles; AC/DC transitions; multi-monitor modes with short vblank intervals; UVD playback power-state transitions; PCIe Gen1/Gen2 link speed changes; thermal throttle and IRQ tests; debugfs current performance level reporting; memory clock switching with GDDR5 and non-GDDR5 memory; and fault injection for SMC message failures, firmware load failure, and malformed ATOMBIOS MC timing tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btc_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btc_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btc_dpm.h

## Purpose
This header declares the BTC DPM helper interface and BTC-specific default constants used by Radeon dynamic power management code. It is the small public surface shared between `btc_dpm.c`, later Northern Islands/Southern Islands DPM implementations, and Radeon ASIC hook declarations.

## Important APIs, Types, and Functions
It includes `radeon.h` and `rv770_dpm.h` for the core device, power-state, and RV770 power-level types. Constants define default UVD activity thresholds (`BTC_RLP_UVD_DFLT`, `BTC_RMP_UVD_DFLT`, `BTC_LHP_UVD_DFLT`, `BTC_LMP_UVD_DFLT`), per-family MGCG control defaults for Barts, Turks, and Caicos, and CG ULV register defaults.

The exported data and helpers are `btc_valid_sclk`, `btc_read_arb_registers`, `btc_program_mgcg_hw_sequence`, `btc_skip_blacklist_clocks`, `btc_adjust_clock_combinations`, `btc_apply_voltage_dependency_rules`, `btc_get_max_clock_from_voltage_dependency_table`, `btc_apply_voltage_delta_rules`, `btc_dpm_enabled`, `btc_reset_to_default`, and `btc_notify_uvd_to_smc`.

## Control Flow
The header has no executable control flow. It lets BTC implementation code expose reusable policy helpers for clock validation, voltage dependency enforcement, hardware register-sequence programming, SMC status/reset, arbitration register capture, and UVD state notification.

## State and Persistence Behavior
The header itself stores no state, but it exposes `btc_valid_sclk` as a global valid clock table and declares functions that mutate hardware registers, SMC soft registers, memory arbitration snapshots, and `rdev->pm.dpm` power-state data. The constants are compile-time policy inputs used to initialize persistent runtime power-management state.

## Dependencies and Integration Points
This header is included by `btc_dpm.c` and `ni_dpm.h`; BTC helper declarations are also referenced by NI and SI DPM code for shared clock and voltage rules. Consumers must already use Radeon DPM structures from `radeon.h` and `rv770_dpm.h`.

## Risks
Any signature drift here breaks cross-family DPM builds. Because helpers declared here are shared with later ASICs, BTC-specific assumptions in clock or voltage rules can have broader impact. The global `btc_valid_sclk` table is mutable because it is declared as `u32[]`, so accidental writes by a consumer would affect all later clock validation.

## Test Signals
Build coverage across BTC, NI, and SI DPM code is the first signal. Runtime coverage should include clock/voltage adjustment paths, UVD enable/disable notification, SMC reset/default paths, and register-sequence programming on supported BTC hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btc_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btcd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btcd.h

## Purpose
This header defines BTC-family power-management, memory-controller, clock-gating, and PCIe register offsets and bitfields used by Radeon DPM code. It is a register map fragment for Barts/Turks/Caicos rather than an executable module.

## Important APIs, Types, and Functions
The file exposes macros for `GENERAL_PWRMGT`, `TARGET_AND_CURRENT_PROFILE_INDEX`, `CG_BIF_REQ_AND_RSP`, `SCLK_PSKIP_CNTL`, `CG_ULV_CONTROL`, `CG_ULV_PARAMETER`, memory arbitration registers such as `MC_ARB_DRAM_TIMING`, `MC_ARB_RFSH_RATE`, and `MC_ARB_BURST_TIME`, memory sequencer timing and LP registers, clock-gating handshake register `MC_SEQ_CG`, display reset selector `LB_SYNC_RESET_SEL`, and PCIe link control register `PCIE_LC_SPEED_CNTL`.

Bitfield helpers follow the common Radeon style: value constructors like `POWERMODE0(x)`, masks like `POWERMODE0_MASK`, and shifts like `POWERMODE0_SHIFT`. They cover global DPM enable bits, AC/DC state, voltage control, Gen2 PCIe enablement, client clock-gating handshakes, memory power-mode fields, memory burst states, GDDR5 detection, and PCIe speed/voltage override fields.

## Control Flow
There is no runtime flow in this header. Its macros are consumed by `btc_dpm.c` and related DPM code to read-modify-write registers, extract current DPM profile indices, mirror normal memory timing into low-power timing registers, program ULV timing, manage clock-gating request/response bits, and control dynamic PCIe Gen2 transitions.

## State and Persistence Behavior
The header stores no C state. The registers it names are persistent hardware state while the device is powered: DPM enablement, thermal protection, voltage management, memory timing, refresh/burst timing, clock-gating handshakes, low-power memory sequencer copies, and PCIe link-speed configuration.

## Dependencies and Integration Points
The macros are used with Radeon register accessors such as `RREG32`, `WREG32`, `WREG32_P`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`. They integrate tightly with BTC DPM, RV770/Cypress helper code, ATOMBIOS timing data, and SMC-managed power-state transitions.

## Risks
Incorrect offsets or masks would cause writes to the wrong hardware registers or preserve the wrong bits during read-modify-write operations. Some fields are reused in tight transition sequences, such as PCIe Gen2 enable/disable and memory LP timing setup, where a bad bit definition can produce hangs or link instability. Because these are preprocessor macros, type checking and range checking are minimal.

## Test Signals
Signals are primarily build coverage plus hardware runtime validation: DPM enable/disable, current profile index reads, ULV entry/exit, dynamic memory clock switching, clock-gating enable/disable, thermal protection toggles, and PCIe Gen2 link transitions on BTC boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cayman_blit_shaders.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cayman_blit_shaders.h

## Purpose
This header provides a statically generated Cayman/Evergreen 3D engine default state stream used by the Radeon DRM driver for blit operations. It avoids embedding the full Mesa/3D state generator in the kernel by supplying precomputed packet/register data for the CP clear-context preamble.

## Important APIs, Types, and Functions
The key objects are `static const u32 cayman_default_state[]` and `static const u32 cayman_default_size = ARRAY_SIZE(cayman_default_state)`. The array contains packetized register writes for depth buffer state, scissor and viewport state, shader input/output state, color blend and shader masks, primitive assembly state, streamout state, antialiasing defaults, and other 3D pipeline defaults needed before kernel blits.

## Control Flow
The header has no functions. `ni.c` includes it and, during Cayman CP initialization, locks the ring, emits `PACKET3_PREAMBLE_BEGIN_CLEAR_STATE`, writes every dword in `cayman_default_state`, emits `PACKET3_PREAMBLE_END_CLEAR_STATE`, then issues `PACKET3_CLEAR_STATE`. Subsequent blit setup can assume this known baseline 3D state.

## State and Persistence Behavior
The C array is immutable static data in the compiled driver. When emitted to the command processor, it establishes persistent GPU context clear-state until replaced by later ring commands or reset. `cayman_default_size` tracks the number of dwords so the ring lock reservation and emission loop stay synchronized with the table.

## Dependencies and Integration Points
The file depends on `u32` and `ARRAY_SIZE` definitions from the including Radeon kernel context. It is included by `ni.c`, which provides packet macros, ring locking, and command submission. It integrates with the Radeon blit path and Cayman command processor initialization rather than DPM.

## Risks
The table is hand generated, so register ordering, packet counts, and data values must match Cayman hardware expectations exactly. A wrong dword can corrupt the clear-state preamble, break accelerated blits, hang the CP, or produce rendering/copy corruption. Because the table is opaque packet data, normal compiler checks cannot validate register semantics; review depends on comments, hardware documentation, and runtime testing.

## Test Signals
Build coverage confirms the array and `ARRAY_SIZE` use compile. Runtime signals include Cayman/NI CP initialization, ring tests, GPU reset recovery, framebuffer console and modeset operations, accelerated BO moves and clears, blit correctness tests, and absence of CP hangs after `PACKET3_CLEAR_STATE` on Cayman-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cayman_blit_shaders.h -->
