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
