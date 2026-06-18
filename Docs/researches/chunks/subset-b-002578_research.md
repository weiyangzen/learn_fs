# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 22794-25201

## Scope

This chunk is a generated AMD GC 12.0.0 register shift/mask header segment. It contains C preprocessor constants only: register fields are represented by `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for packing and decoding 32-bit hardware register values. There are no functions, structs, enums, variables, allocation paths, locks, callbacks, persistence code, or executable branches in this range.

The selected lines begin in the middle of the `GFX_ICG_GL2C_CTRL` mask family and then cover `GFX_ICG_GL2C_CTRL1`. The chunk continues through CP/PSP decode, CH power/clock control, GFX IMU, GRBMH, PA, SQ, SX, SPI, and the beginning of TD/TA texture-pipe fields. It ends inside `TA_CNTL_AUX`; the remaining fields for that register and later TPDEC registers are outside this chunk. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP, not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. AMDGPU code pairs these macros with matching register addresses from `gc_12_0_0_offset.h` and uses common helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to compose writes or decode readbacks without duplicating literal bit positions.

This chunk focuses on engine security/debug control, firmware/IMU RAM access, graphics-block busy/status reporting, shader processor controls, shader export/SPI debug state, wavefront counters, trap-screen configuration, and texture-address/texture-data controls:

- GL2C and channel clock-gating override fields for fine-grained clock-control bring-up, debug, and golden-setting programming.
- CP/PSP and GC EA security fields covering indexed debug-memory address/data windows, PSP debug override bits, trusted memory zone control, client security-level maps, GRBM CAM remapping, firewall violation status, and UTC bypass control.
- GFX IMU message, access-control, scratch, RLC RAM, bootloader, instruction/data RAM, core control, and reset-control fields.
- GRBMH fields for read timeouts, interface path disables, aggregate busy/clean status, fine-grained clock-gating targets, soft reset, read-error attribution, invalid pipe, sync, and unit-disable masks.
- PA/GE fields for shader-array disable/rate configuration, geometry-engine busy state, GE/SPI and GE/PA safe-register routing, clipper setup, setup/scan-converter/debug FIFO controls, and NGG-related PA behavior.
- SQ/SQC/LDS fields for shader queue configuration, cache sizing, instruction/data cache behavior, LDS/SQ/SP DSM and error-injection controls, thread trace, arbitration, dynamic VGPR allocation, GL1X status, perf snapshots, interrupt masking, watchpoint registers, indirect register access, and SQ command control.
- SX debug-busy fields for color/export/output buffer internals, request queues, blend/position/index valid queues, and scoreboard state.
- SPI fields for wave IDs, scratch overflow status, debug controls, DSM and EDC counters, debug-busy status, per-stage CU masks, lifetime counters/status, WGP work-pending state, load-balancer counter controls, GDS credits, export/scoreboard buffer sizing, active wavefront counters, trap-screen base/mask/GPR-min registers, and crawler-depth configuration.
- TD/TA fields for texture-data control, status, power control, LDS return credits, scratch, texture-address credits, XNACK clock-gating behavior, and the first `TA_CNTL_AUX` bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The interface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address symbols for the same names live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h`.
- AMDGPU consumers use the macros through register helpers and SOC15 MMIO accessors, command-packet register programming, golden-setting tables, debugfs/perf paths, KFD debug/trap setup, reset handling, virtualization paths, and hang diagnostics.

The main macro families in this range are:

- `GFX_ICG_GL2C_CTRL*`, `CHI_CHR_MGCG_OVERRIDE`, `ICG_CHA_CTRL`, and `ICG_CHC_CLK_CTRL`: clock-gating and clock-override fields for GL2C/channel logic.
- `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, and `CP_GFX_RS64_DM_INDEX_*`: full-width indexed address/data windows for command-processor and RS64 debug-memory access.
- `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GC_EA_CPWD_SECURE_CTRL`, `GC_EA_CPWD_SDP_SECLEVEL_*`, `GRBM_SEC_CNTL`, `GRBM_CAM_*`, `RLC_REG_SEC_INT_STATUS`, and `RLC_UTC_BYPASS_CNTL`: PSP/security, firewall/violation, client security-level, remapping, and bypass controls.
- `GFX_IMU_*`: IMU mailbox, scratch, access permission, RLC RAM index/address/data, core reset/stall/debug, graphics reset, bootloader address/size, instruction RAM, and data RAM fields.
- `GRBMH_*`: graphics register bus manager hub control/status, interface, fine-grained clock-gating target, soft reset, read-error, clock enable, invalid-pipe, sync, and unit-disable fields.
- `GE_*`, `CC_GC_*`, and `PA_*`: shader-array enablement, graphics-engine busy state, safe-register data paths, setup/clipper/raster/debug controls, and PA FIFO/debug fields.
- `SQ_*`, `SQC_*`, `LDS_CONFIG`, and `SP_CONFIG`: shader queue and cache configuration, DSM/error-injection controls, watch registers, indirect register indexing, GL1X status, perf snapshots, interrupt masking, and command-control macros.
- `SX_DEBUG_BUSY*`: dense one-bit status maps for SX color/export, scoreboard, blend, position, and index internal busy/valid signals.
- `SPI_*`, `SPIS_DEBUG_READ`, and `BCI_DEBUG_READ`: shader processor input/debug state, CU masks for graphics/HP3D/compute queues, wave lifetime counters, load-balancer counters, GDS credits, export buffer sizes, wavefront active counters, trap-screen ranges, and crawler configuration.
- `TD_*` and `TA_*`: texture-data and texture-address control/status/power/scratch/credit fields, ending at the first `TA_CNTL_AUX` shift definitions.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register header for the active ASIC generation.
2. Select the matching `reg...` address macro from `gc_12_0_0_offset.h`.
3. Read an existing register value, build an MMIO write value, build a command-packet register write, or decode status/debug output.
4. Use the `__SHIFT`/`__MASK` pair, usually via `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract a field.
5. Apply the value in initialization, power/clock setup, secure/PSP access configuration, IMU firmware/RLC RAM handling, reset, graphics pipeline setup, shader/debug/trap setup, perf/debug capture, or hang recovery.

For security and PSP registers, driver and firmware setup code writes privilege, secure-register, client-ID, and bypass fields before protected register access or secure memory traffic is expected. For IMU registers, code programs address/index/data windows and reset/core-control fields around bootloader, instruction RAM, data RAM, and RLC RAM interactions. For status/debug families such as `GRBMH_STATUS`, `SX_DEBUG_BUSY*`, and `SPI_DEBUG_BUSY`, runtime code reads and decodes bitmaps during idle waits, reset diagnosis, hang dumps, or hardware validation. For SQ/SPI/TD/TA configuration registers, programming is part of engine bring-up, shader/debug feature setup, wavefront scheduling, and graphics/compute pipeline behavior.

The header does not describe ordering constraints, polling loops, clear-on-read behavior, sticky-bit clearing, privilege checks, firmware handshakes, or reset sequencing. Those rules live in AMDGPU engine code, firmware contracts, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register fields whose state is owned by the GPU, firmware, and AMDGPU runtime programming.

Clock-gating override and power-control fields persist as hardware configuration until reprogrammed, reset, or lost during power transitions. Mispacked override fields can leave clocks forced on/off, masking power bugs or causing hangs if a block is gated while active. Security and PSP fields are especially sensitive: `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GC_EA_CPWD_SECURE_CTRL`, client security maps, GRBM CAM remap fields, and UTC bypass controls can change access policy, attribution, and translation behavior. Full-register writes must preserve reserved bits unless the hardware sequence requires a complete write.

IMU RAM index/address/data fields are transient access windows, but the data they program can affect persistent firmware/RLC behavior until reset or replacement. Core-control and reset fields can stop, reset, or debug the IMU and graphics-related blocks. Bootloader address/size fields must match firmware memory layout and alignment.

GRBMH, PA, SQ, SX, SPI, TD, and TA fields mix persistent configuration with live status. Configuration fields such as SQ cache behavior, LDS and DSM controls, PA clip/raster behavior, SPI CU masks, wave lifetime limits, GDS credits, trap-screen ranges, texture-data controls, and texture-address credits remain active until overwritten. Status and debug fields can be sampled live, can be sticky, or can require clear/acknowledge sequences defined outside this header. Counter/status families can race with hardware activity if sampled without the documented snapshot or idle sequence.

Trap-screen base/mask registers and watch/interrupt fields influence debug and exception handling for waves. Incorrect values can suppress expected traps, trap the wrong address range, or make diagnostics misleading. CU mask and WGP mask fields affect work distribution; bad masks can silently reduce available compute/graphics capacity or target disabled hardware.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses and base indices.
- Common AMDGPU helpers and SOC15 accessors provide field packing/extraction and MMIO access.
- `gfx_v12_0.c`, `gfx_v12_1.c`, IMU code, KFD debug code, reset/hang-dump paths, golden-setting tables, and performance/debug tooling are representative consumers of these register families.

Important integration points include PSP/secure register access setup, IMU boot and RAM programming, RLC interaction, secure/firewall violation diagnostics, clock-gating override programming, GRBM/GRBMH idle waits and reset diagnosis, PA/GE graphics pipeline initialization, SQ/SQC/LDS shader engine setup, KFD and shader trap/watchpoint handling, SPI CU masking and wavefront accounting, wave lifetime tracking, load-balancer/per-WGP counters, GDS credit configuration, SX/SPI/TD/TA debug capture, and texture unit configuration.

The companion offset header has GC 12.0.0 address symbols for registers such as `regCPG_PSP_DEBUG` and `regTD_CNTL`. A matching `gc_12_0_0_default.h` file was not present in the local `asic_reg/gc` directory, so validation for defaults must come from another generated source or AMD's register database if needed.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Wrong shifts or masks compile successfully but program or decode the wrong hardware bits.
- This chunk begins and ends mid-family: `GFX_ICG_GL2C_CTRL` shift/comment context is before the range, and `TA_CNTL_AUX` continues after the range. File-level research must merge adjacent chunks before drawing complete-family conclusions.
- Security and bypass fields can affect isolation and privileged access. `GPA_OVERRIDE`, `UCODE_VF_OVERRIDE`, `SECURE_REG_OVERRIDE`, trusted memory zone, security-level maps, GRBM CAM remap, and UTC bypass fields should be changed only under documented sequences.
- Indexed address/data windows are easy to misuse. CP debug-memory, IMU RLC RAM, instruction RAM, and data RAM windows require correct address alignment, valid bits, and access ordering not encoded in the masks.
- Reset and core-control bits have side effects. `GFX_IMU_CORE_CTRL`, `GFX_IMU_GFX_RESET_CTRL`, `GRBMH_SOFT_RESET`, and related clock/power controls can stop or reset active hardware if written at the wrong time.
- Busy/status bitmaps are dense and similar across registers. Mislabeling `GRBMH_STATUS`, `SX_DEBUG_BUSY*`, or `SPI_DEBUG_BUSY` fields can lead to incorrect hang attribution.
- Repeated CU/WGP mask families are structurally similar but target different graphics, HP3D, and compute paths. Copy/paste mistakes can disable the wrong queue class or shader array.
- DSM/error-injection and debug-clear fields can perturb hardware state. Test-only fields in SQ, PA, SC, PH, SPI, TD, and related blocks should not be enabled by production paths accidentally.
- Counter and lifetime-status fields may require snapshot, reset, or latch handling. The shift/mask header cannot express atomicity, overflow, or clear timing.
- Reserved fields appear in many registers. Read-modify-write callers should preserve reserved bits unless the hardware specification says otherwise.

## Test Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GFX 12, IMU, KFD debug, reset, hang-dump, power/clock, and perf/debug paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database for every `__SHIFT` and `__MASK` value in this range.
- Cross-check that every register comment in this chunk has a matching `reg...` address macro in `gc_12_0_0_offset.h` with the expected base index.
- Static sanity checks that masks align with shifts, full-width data fields use `0xFFFFFFFFL`, repeated client/CU/WGP/status families remain structurally consistent, and bitmaps do not overlap unless documented.
- Bring-up tests that apply clock-gating and golden-setting programming, then verify idle, suspend/resume, and reset behavior on GC 12.0.0 hardware.
- PSP/security tests that exercise secure register access, VF/VMID violation handling, firewall violation counters, client security-level maps, GRBM CAM remapping, and UTC bypass behavior with expected fault attribution.
- IMU tests that boot firmware, program RLC/I/D RAM windows, exercise core reset/stall/debug paths, and confirm no invalid RAM index/address behavior.
- Graphics and compute workload tests that validate PA/GE/SQ/SPI/TD/TA configuration under draw, dispatch, trap/debug, wave lifetime, CU mask, and texture-heavy workloads.
- Hang/debug dump tests that decode `GRBMH_STATUS`, `SX_DEBUG_BUSY*`, `SPI_DEBUG_BUSY`, `SQG_STATUS`, `TD_STATUS`, wavefront counters, trap-screen state, and error-injection/debug registers coherently.
- Perf/counter tests that reset, select, and read SPI load-balancer, wavefront, lifetime, GDS credit, and debug counters under controlled workload activity.
- Runtime warning signals include unexpected VM/security faults, failed PSP/IMU access, firmware boot failures, GPU reset loops, engines that never become idle, wrong busy-block attribution, missing shader traps, disabled CUs/WGPs, bad wavefront counts, texture unit hangs, or power regressions after clock-gating changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002578`. It covers lines 22794-25201 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `GFX_ICG_GL2C_CTRL` and `TA_CNTL_AUX` families and to place these CP/PSP, IMU, GRBMH, PA, SQ, SX, SPI, TD, and TA definitions in the full GC 12.0.0 register map.
