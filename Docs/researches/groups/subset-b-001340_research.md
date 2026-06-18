# subset-b-001340 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.h

## Purpose

This header is the public local interface for the main GFX 9.0 AMDGPU block implementation. It exposes the GFX 9.0 IP block descriptor and the shader-engine/shader-array selection helper that later GFX 9.x support files reuse when programming GRBM indexed registers.

## Important APIs, types, and functions

- `extern const struct amdgpu_ip_block_version gfx_v9_0_ip_block`: exported IP block descriptor consumed by the AMDGPU device bring-up path to register the GFX 9.0 hardware block callbacks.
- `gfx_v9_0_select_se_sh(struct amdgpu_device *adev, u32 se_num, u32 sh_num, u32 instance, int xcc_id)`: selects a shader engine, shader array, and instance for subsequent register access, with broadcast sentinel values used by callers that need all instances selected.

## Control flow and integration

The header has no executable control flow. It allows `gfx_v9_4_2.c` to call `gfx_v9_0_select_se_sh()` for power-brake setup, and allows broader AMDGPU initialization code to refer to the GFX 9.0 IP block. The concrete implementation in `gfx_v9_0.c` writes GRBM index state and is also wired through the GFX function table as `.select_se_sh`.

## State and persistence behavior

No state is stored here. The declared selector mutates hardware register selection state in the implementation, so callers must pair it with appropriate locking and restore broadcast selection when done.

## Dependencies

The declarations depend on AMDGPU core types such as `struct amdgpu_device` and `struct amdgpu_ip_block_version`, plus kernel fixed-width aliases like `u32`. Those are expected to be available through including translation units rather than this minimal header including them directly.

## Risks

The main risk is misuse of `gfx_v9_0_select_se_sh()` without holding the relevant GRBM mutex or without restoring broadcast selection. Because the header does not encode locking requirements, correctness relies on call-site discipline.

## Test signals

Useful validation signals are successful GFX 9.0 device probe, no register programming races during RAS scans or power-management paths, and no build regressions in translation units including this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0_cleaner_shader.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0_cleaner_shader.h

## Purpose

This header embeds GFX 9 cleaner shader machine code as static `u32` arrays. The active payload is `gfx_9_4_2_cleaner_shader_hex`, used by the GFX 9.0 implementation for GFX 9.4.2 and related Aldebaran paths that need to clear GPU execution state.

## Important APIs, types, and data

- `gfx_9_0_cleaner_shader_hex[]`: an empty, `__maybe_unused` placeholder for a generic GFX 9.0 cleaner shader.
- `gfx_9_4_2_cleaner_shader_hex[]`: a compiled shader blob containing instructions to clear VGPRs, SGPRs, LDS, `vcc`, flat scratch, and temporary registers. `gfx_v9_0.c` assigns this pointer and size into `adev->gfx.cleaner_shader_ptr` and `adev->gfx.cleaner_shader_size`.

## Control flow and integration

The header itself is data-only. Runtime control flow happens when GFX initialization or reset code chooses the blob, uploads it as a compute program, and dispatches it through the GFX clean-up flow. The blob begins with branch and barrier logic, then clears vector registers via indexed VGPR writes, conditionally clears LDS from the first wave, clears scalar registers through `s_movreld_b32`, and ends the program. A later path halts waves before clearing another SGPR allocation range.

## State and persistence behavior

The shader deliberately overwrites volatile GPU execution state. It does not persist driver-visible state, but it is part of security and RAS hygiene because stale register or LDS contents should not survive across contexts, reset paths, or special clean-up dispatches.

## Dependencies

The blob depends on exact GFX 9.4.2 ISA encoding, wave size assumptions, register allocation assumptions, and dispatch state programmed by `gfx_v9_0.c`. It also depends on consumers using `sizeof(gfx_9_4_2_cleaner_shader_hex)` rather than hard-coded instruction counts.

## Risks

The highest risk is mismatch between the machine-code blob and the dispatch resource registers. If wave size, SGPR/VGPR allocation, LDS size, or halt/barrier sequencing changes, the shader may leave state uncleared or hang. The empty GFX 9.0 placeholder is safe only while no consumer selects it for a required clean-up path.

## Test signals

Signals include successful clean shader dispatch during GPU reset or context cleanup, no timeout on the compute ring, no residual GPR/LDS RAS errors after clean-up, and static build coverage showing that the selected ASIC paths bind to the non-empty GFX 9.4.2 blob.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0_cleaner_shader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.c

## Purpose

This file implements the GFX 9.4 RAS hardware operations for Arcturus-like GC 9.4.1 devices. It enumerates EDC counter registers, maps register bitfields to human-readable GFX sub-block names, queries and resets SRAM and UTC error counters, and reports fatal EA error status before reset.

## Important APIs, types, and functions

- `gfx_v9_4_edc_counter_regs[]`: table of GC EDC counter registers with per-register shader-engine count and instance count.
- `gfx_v9_4_ras_fields[]`: maps each EDC register to SEC and DED masks/shifts and diagnostic names for CPC, CPF, GDS, SPI, SQ, SQC, TA, TCA, TCC, TCI, TCP, TD, EA, GCEA, and RLC memories.
- `gfx_v9_4_select_se_sh()`: local GRBM index helper for selecting SE/SH/instance before indexed register reads.
- `gfx_v9_4_query_utc_edc_status()`: walks UTC/VML2/UTCL2/ATC indexed ECC counters and accumulates corrected and uncorrected counts into `struct ras_err_data`.
- `gfx_v9_4_query_ras_error_count()`: main `.query_ras_error_count` implementation. It scans SRAM EDC counters under `adev->grbm_idx_mutex`, restores broadcast selection, then queries UTC counters.
- `gfx_v9_4_reset_ras_error_count()`: clears counters mostly by reading them, plus writes UTC/ATC index and control registers to reset indexed counter state.
- `gfx_v9_4_query_ras_error_status()`: reads `mmGCEA_ERR_STATUS` across EA instances and logs SDP read/write response or parity errors.
- `gfx_v9_4_ras_ops` and `gfx_v9_4_ras`: exported RAS ops attached by `gfx_v9_0.c` for matching ASICs.

## Control flow

RAS query entry first checks `amdgpu_ras_is_supported(adev, AMDGPU_RAS_BLOCK__GFX)`. Count query zeroes caller-visible counts, iterates every table row, selects each SE and instance, reads the register, and if non-zero decodes every matching field entry. After accumulating SRAM counters it restores GRBM broadcast selection and calls the UTC indexed-counter query. Reset follows the same table scan but reads counters for clear-on-read behavior, then walks every UTC indexed instance to clear those counters as well. Error-status query is separate and only reports EA fatal-status bits.

## State and persistence behavior

This code reads and clears persistent hardware error counters. Querying SRAM counters in `gfx_v9_4_query_ras_error_count()` appears read-only, while reset explicitly consumes counters through read side effects. UTC reset writes ECC index and control registers, walks indexed memories, then restores index registers to `255`. The file mutates global hardware index state and therefore protects GRBM selection with `adev->grbm_idx_mutex`.

## Dependencies and integration points

The file depends on GC 9.4.1 register offset and mask headers, SOC15 register access macros, `amdgpu_ras` infrastructure, `struct ras_err_data`, and AMDGPU device logging. `gfx_v9_0.c` chooses `gfx_v9_4_ras` for relevant devices, so these callbacks run through the generic AMDGPU RAS block interface rather than direct external calls.

## Risks

The counter tables encode topology assumptions such as eight SQ/SQC shader engines, 16 TCC instances, and 72 TCI instances. A wrong count can miss counters or select invalid instances. Several UTC setup lines write `mmATC_L2_CACHE_2M_DSM_CNTL` while preparing 4K state, which should be reviewed against hardware docs because it may be intentional aliasing or a copy/paste hazard. Since query and reset paths clear some indexed counters, diagnostics can be lost if called unexpectedly.

## Test signals

Good signals are RAS injection tests that produce expected CE/UE totals, dmesg lines naming the correct GFX sub-block and instance, no lockdep warnings around GRBM index access, reset tests showing counters return to zero, and fatal EA error paths logging status before GPU reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.h

## Purpose

This header exposes the GFX 9.4 RAS descriptor implemented in `gfx_v9_4.c` so the broader GFX 9.0 initialization code can attach the correct RAS operations for supported ASICs.

## Important APIs, types, and functions

- `extern struct amdgpu_gfx_ras gfx_v9_4_ras`: descriptor containing `struct amdgpu_ras_block_hw_ops` callbacks for GFX 9.4 error-count query, counter reset, and error-status query.

## Control flow and integration

There is no executable control flow. `gfx_v9_0.c` includes this header and assigns `adev->gfx.ras = &gfx_v9_4_ras` for matching devices. After that, generic AMDGPU RAS flows call through the ops table in the descriptor.

## State and persistence behavior

The header stores no state. The exported object it declares owns callback wiring only; the callbacks mutate or read hardware RAS counters in `gfx_v9_4.c`.

## Dependencies

The declaration depends on `struct amdgpu_gfx_ras` being defined by included AMDGPU headers in the consumer. The header is intentionally minimal and uses include guards to avoid duplicate declarations.

## Risks

Because the exported descriptor is mutable rather than `const`, accidental writes from another translation unit are possible in C, although current code treats it as static driver wiring. Any mismatch between this declaration and the definition would be caught at build or link time.

## Test signals

Build coverage, successful GFX 9.4 RAS registration, and runtime RAS sysfs/debugfs operations reaching `gfx_v9_4.c` callbacks validate this header's integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c

## Purpose

This file implements Aldebaran/GC 9.4.2 specific GFX support layered under the GFX 9.0 driver. It provides golden-register programming, SQ setup, debug trap setup, power-brake sequencing, EDC GPR workarounds using compute shader dispatches, RAS counter and status handling, UTC indexed ECC accounting, and SQ watchdog timeout diagnostics.

## Important APIs, types, and functions

- `enum gfx_v9_4_2_utc_type` and `struct gfx_v9_4_2_utc_block`: describe UTC/VML2/ATC indexed ECC counter blocks, index/data registers, count fields, and clear values.
- Golden setting tables: `golden_settings_gc_9_4_2_alde`, plus die-specific channel steering tables for die 0 and die 1.
- Shader blobs and register tables: `vgpr_init_compute_shader_aldebaran`, `sgpr112_init_compute_shader_aldebaran`, `sgpr96_init_compute_shader_aldebaran`, `sgpr64_init_compute_shader_aldebaran`, with matching `*_init_regs_aldebaran` dispatch state.
- `gfx_v9_4_2_run_shader()`: builds an IB containing SET_SH_REG packets, shader code, user-data writeback address, and `PACKET3_DISPATCH_DIRECT`, then schedules it on a compute ring.
- `gfx_v9_4_2_do_sgprs_init()` and `gfx_v9_4_2_do_vgprs_init()`: dispatch shader workarounds and verify SIMD/wave coverage through an IB-backed writeback buffer.
- Public helpers: `gfx_v9_4_2_do_edc_gpr_workarounds()`, `gfx_v9_4_2_init_golden_registers()`, `gfx_v9_4_2_init_sq()`, `gfx_v9_4_2_debug_trap_config_init()`, and `gfx_v9_4_2_set_power_brake_sequence()`.
- RAS callbacks: `gfx_v9_4_2_query_ras_error_count()`, `gfx_v9_4_2_reset_ras_error_count()`, `gfx_v9_4_2_query_ras_error_status()`, `gfx_v9_4_2_reset_ras_error_status()`, and `gfx_v9_4_2_enable_watchdog_timer()`.

## Control flow

Initialization callers from `gfx_v9_0.c` invoke golden-register programming during GC setup, SQ setup when MEC firmware supports chained XNACK behavior, power-brake setup during power-management configuration, debug trap setup for VMID ranges, and EDC GPR workarounds during late init. The GPR workaround path skips if GFX RAS is unsupported or the device is in reset, then runs SGPR and VGPR initialization shaders. The SGPR flow launches dispatch 0 and dispatch 1 on two compute rings, waits until writeback patterns prove expected wave coverage, releases halted waves by writing `0xdeadbeaf`, waits on fences, and then runs a third dispatch for remaining SGPR holes.

RAS count flow checks GFX RAS support, zeroes the caller's `ras_err_data`, queries SRAM EDC counters under `adev->grbm_idx_mutex`, clears counters after reading, then walks UTC indexed blocks and clears those counters after reading. Error-status flow logs and clears EA status, logs and clears UTC ECC status, and queries SQ timeout status, where each selected CU's timeout register can trigger per-wave indirect reads for PC, EXEC, instruction, and IB state.

## State and persistence behavior

This file heavily mutates hardware state. Golden settings persist in GC registers until reset or reprogramming. Debug trap setup writes per-VMID trap control and clears trap data registers. Power-brake setup programs throttle and CAC indirect registers. GPR workaround shaders clear physical SGPR/VGPR/LDS state and use temporary IB allocations plus fences. RAS query and reset consume hardware error counters by writing zero or block-specific clear values after reads. SQ timeout status is cleared after query/reset.

## Dependencies and integration points

The code depends on GC 9.4.2 register headers, SOC15 access macros, AMDGPU IB and ring scheduling, DMA fences, `amdgpu_ras`, `amdgpu_gfx`, `adev->gfx.config`, `adev->gfx.cu_info`, and the global `amdgpu_watchdog_timer`. It calls `gfx_v9_0_select_se_sh()` from `gfx_v9_0.h` in the power-brake path. `gfx_v9_0.c` wires `gfx_v9_4_2_ras`, the cleaner shader, golden-register init, SQ init, power-brake setup, EDC GPR workaround, and debug trap initialization into the overall GFX lifecycle.

## Risks

The shader workaround code is sensitive to compute ring readiness, CU topology, wave assignment, fence completion, and exact shader resource register values. `gfx_v9_4_2_do_edc_gpr_workarounds()` ignores the return values from the SGPR and VGPR helpers and always returns zero, so failures are logged but not propagated. RAS tables encode many topology counts and field masks; mismatches can miss errors or access invalid instances. `gfx_v9_4_2_log_cu_timeout_status()` uses `if (!((i << 1) & status))`, which may deserve scrutiny because bit testing is unusual compared with `(1u << i)`. The watchdog period validation only clamps when fatal disable is set.

## Test signals

Strong signals include successful boot on Aldebaran variants, golden register readback for both dies, RAS injection producing expected CE/UE totals and clearing behavior, EDC GPR workaround logs showing SGPR/VGPR success with no ring timeout, debug trap tests across requested VMIDs, watchdog timeout tests that log wave PC/EXEC/instruction state and clear status, and suspend/reset tests confirming no stale GRBM/SRBM selection leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.h

## Purpose

This header exposes the GC 9.4.2/Aldebaran helper functions and RAS descriptor implemented in `gfx_v9_4_2.c` for use by the main GFX 9.0 driver.

## Important APIs, types, and functions

- `gfx_v9_4_2_debug_trap_config_init()`: programs per-VMID trap controls for a VMID range.
- `gfx_v9_4_2_init_golden_registers()`: applies common and die-specific GC golden register settings.
- `gfx_v9_4_2_init_sq()`: configures SQ behavior, including XNACK chain handling when MEC firmware supports it.
- `gfx_v9_4_2_set_power_brake_sequence()`: programs GFX throttle and power-brake stall pattern registers.
- `gfx_v9_4_2_do_edc_gpr_workarounds()`: runs GPR/LDS clearing workarounds when RAS is enabled and the device is not in reset.
- `extern struct amdgpu_gfx_ras gfx_v9_4_2_ras`: RAS descriptor with GFX 9.4.2 counter, status, reset, and watchdog callbacks.

## Control flow and integration

The header has no executable control flow. `gfx_v9_0.c` includes it and calls the helpers from GFX initialization, power-management, RAS, and debug-trap paths. The exported RAS descriptor is assigned to `adev->gfx.ras` for supported ASICs.

## State and persistence behavior

The declarations represent functions that program persistent hardware registers, dispatch compute cleanup shaders, and clear RAS counters/status registers. The header itself stores no state.

## Dependencies

Consumers need AMDGPU core type definitions for `struct amdgpu_device` and `struct amdgpu_gfx_ras`, plus standard fixed-width integer types. The header intentionally does not include those dependencies itself.

## Risks

The prototypes expose low-level hardware programming helpers without documenting locking or ordering requirements. Callers must invoke them in the correct phase of the GFX lifecycle, after rings/register windows are ready and before dependent features are enabled.

## Test signals

Build/link coverage confirms the declarations match `gfx_v9_4_2.c`. Runtime signals include correct Aldebaran initialization, RAS callback registration, debug trap programming for VMIDs, and absence of GPU hangs from the EDC workaround entry point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2_cleaner_shader.asm -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2_cleaner_shader.asm

## Purpose

This assembly source documents the intended GFX 9.4.2 cleaner shader for MI200/Aldebaran. It explains and encodes a compute shader that clears LDS, VGPRs, SGPRs, flat scratch, `vcc`, and temporary registers. The compiled form appears in `gfx_v9_0_cleaner_shader.h` as `gfx_9_4_2_cleaner_shader_hex`.

## Important APIs, types, and instructions

This is not C API surface, but its labels and instruction sequences define the behavior of the embedded shader blob:

- `shader main asic(MI200) type(CS) wave_size(64)`: declares the target shader type.
- Initial branch on `s0 == 1`: selects the VGPR/LDS/lower-SGPR cleaning path versus the remaining-SGPR path.
- `S_BARRIER`: ensures all workgroup waves have launched before lower-SGPR cleaning can finish.
- `s_set_gpr_idx_on`, repeated `v_mov_b32`, and indexed SGPR moves: clear vector and scalar register ranges.
- LDS clearing loop: first wave writes zeroed vector pairs across the 64 KiB LDS region using `ds_write2_b64`.
- `s_sethalt 1`: halts the second kernel path until CP releases all waves, enabling high SGPR coverage when barriers are unsuitable for the larger wave count.

## Control flow

The shader has two main paths. When `s0` marks the VGPR/LDS path, waves synchronize, clear VGPRs in an indexed loop, let the first wave clear LDS, then clear SGPRs and special registers before ending. Otherwise, the shader halts first, waits for CP unhalt after all waves are launched, clears another SGPR allocation range, clears selected special registers, and exits.

## State and persistence behavior

The shader intentionally destroys transient compute-unit state. It writes zeros into VGPRs, SGPRs, LDS, flat scratch, `vcc`, and selected `ttmp` registers. The only intended persistent effect is removal of stale execution data; it should not update driver memory except through normal dispatch machinery in the caller.

## Dependencies and integration points

The comments describe required CP/SPI launch behavior: one kernel launches one workgroup per CU with four wave64 waves per SIMD, and another launches 24 waves per workgroup with resource-reserve registers preventing lower SGPR allocation. The machine-code version is included by `gfx_v9_0_cleaner_shader.h` and selected in `gfx_v9_0.c` for GFX 9.4.2 cleaner shader setup.

## Risks

This file contains hand-sensitive ISA and scheduling assumptions. A typo in assembly, mismatch between this source and the hex header, changed wave allocation policy, or incorrect CP resource-reserve setup can leave registers uncleared or hang halted waves. The comments contain spelling errors but the technical risk is the exact launch contract, not prose.

## Test signals

Useful signals are assembler-to-hex reproducibility, successful dispatch on MI200/Aldebaran without hangs, hardware validation that all expected SGPR/VGPR/LDS ranges are zeroed, and reset/context-cleanup tests showing no stale state leakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2_cleaner_shader.asm -->
