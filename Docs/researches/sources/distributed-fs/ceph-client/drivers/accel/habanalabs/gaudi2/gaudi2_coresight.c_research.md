# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight.c

## Purpose
This file implements Gaudi2 CoreSight debug support. It maps user-visible debug component IDs to hardware base addresses, configures STM, ETF, ETR, funnel, bus monitor, and SPMU blocks, halts trace collection, and masks out CoreSight components for binned or disabled hardware units at initialization.

## Important APIs, types, and functions
- `debug_stm_regs`, `debug_etf_regs`, `debug_funnel_regs`, `debug_bmon_regs`, and `debug_spmu_regs` are static ID-to-base-address tables indexed by Gaudi2 CoreSight enums from the public Gaudi2 CoreSight include.
- `struct component_config_offsets` describes which funnel, ETF, STM, SPMU, and BMON IDs belong to one logical unit.
- Binning tables cover XBAR edge, HMMU, HBM MC0/MC1, decoders, EDMA, and TPC units. They let init-time code zero all CoreSight base-table entries associated with disabled hardware instances.
- `gaudi2_coresight_timeout` polls a register bit until it becomes set or clear, using an extended timeout under PLDM.
- `gaudi2_unlock_coresight_unit` writes the CoreSight unlock value and waits for the lock-status bit to clear.
- `gaudi2_config_stm`, `gaudi2_config_etf`, `gaudi2_config_etr`, `gaudi2_config_funnel`, `gaudi2_config_bmon`, and `gaudi2_config_spmu` implement individual debug operations.
- `gaudi2_debug_coresight` dispatches `HL_DEBUG_OP_*` requests to those configuration helpers.
- `gaudi2_halt_coresight` disables ETFs and ETR for context teardown or debug stop.
- `gaudi2_coresight_set_disabled_components` mutates static base-address tables to zero out disabled units.
- `gaudi2_coresight_init` applies binning masks from `hdev->asic_prop`.

## Control flow
User debug requests enter through `gaudi2_debug_coresight`, which interprets `struct hl_debug_params::op`. For component-local operations, helpers validate `reg_idx` against the corresponding static table, fetch the base address, treat base address zero as a successful no-op, and, for PLDM, read an identifying/status register to skip stubbed components. STM, ETF, ETR, and funnel paths unlock CoreSight before programming. Missing input payloads for enable operations return `-EINVAL`; unlock or hardware timeout failures return `-EIO` or the poll error.

STM enable programs trace control, hardware event masks, stimulus port masks, ATB ID, timestamp frequency, synchronization, and final enable bits. Disable clears event/stimulus/timestamp registers, waits for the busy bit to clear, and leaves the block in a minimal disabled control state. ETF and ETR share a flush-and-wait sequence: assert FFCR bits, wait for flush completion and empty status, disable CTL, then either program sink mode/buffer settings and re-enable or clear settings. Funnel simply writes all input enables (`0xFFF`) or zero to the funnel control base.

BMON enable resets the monitor, programs up to four address windows, clears ID filters, programs bandwidth/window capture/reduction/STM trace ID settings, and writes the caller-supplied control word. Disable clears address windows and programs a disabled/reset trace state. SPMU enable validates at most six event types, resets PMCR, writes event selectors and trace controls, enables the cycle counter plus selected events, and starts collection. Disable stops PMCR, optionally copies event counters, overflow, and cycle counter into the caller output buffer, clears overflow state, and resets PMTRC.

Initialization calls `gaudi2_coresight_set_disabled_components` once per binned family. That helper computes `disabled_mask = ~enabled_mask & full_mask`, walks each disabled component, and writes `0x0` into every associated global CoreSight base-address table entry. Later configuration requests to those IDs become no-ops.

## State and persistence behavior
The file has no heap-backed private state, but it maintains process-global static base-address tables. `gaudi2_coresight_init` permanently mutates those tables for the lifetime of the loaded driver image by setting disabled component entries to zero. That design makes per-device binning state global to the module, which is acceptable only if all active devices share compatible masks or initialization ordering is constrained elsewhere. Runtime configuration writes directly to device registers and leaves hardware state in trace-enabled or trace-disabled mode until a matching disable, halt, reset, or device teardown path runs. ETR disable can persist the final trace write pointer to `params->output`.

## Dependencies and integration points
The implementation depends on `gaudi2_coresight_regs.h` for register offsets, `gaudi2_masks.h` for MMU/ASID masks, Gaudi2 generated register bases, UAPI debug operation and payload structs, common register access macros (`RREG32`, `WREG32`, `RMWREG32`), `hl_poll_timeout`, `hl_mem_area_inside_range`, and `hdev->asic_prop` masks and address ranges. It integrates with the user debug ioctl path through `gaudi2_debug_coresight`, with context memory ownership through ETR ASID programming, with PLDM by detecting stub components and stretching timeouts, and with ASIC initialization through `gaudi2_coresight_init`.

## Risks and edge cases
- Static table mutation during binning is global, so mixed devices or re-probe sequences with different masks could inherit zeros from an earlier device.
- Zero base addresses serve both as unsupported component sentinels and binned/stub markers; callers receive success instead of an explicit "unavailable" result.
- ETR address validation returns `int` but uses boolean semantics and has an overflow check `addr > addr + size`; edge cases around zero size and wraparound rely on the prior size check in `gaudi2_config_etr`.
- SPMU disable computes `events_num = output_arr_len - 2` before checking `output_arr_len > 2`; unsigned underflow is harmless because it is only used under the guarded branch, but the pattern is fragile.
- ETR programming writes trace AWUSER/ARUSER from `ctx->asid`; incorrect context or stale ASID would route trace writes into the wrong address space.
- PLDM stub detection depends on specific registers returning zero; a real component returning zero during reset could be skipped.
- Many magic register values encode hardware programming sequences without named bitfields, making regressions hard to review.

## Test signals
Signals include successful debug ioctl enable/disable for all operation types, invalid `reg_idx` returning `-EINVAL`, enable without input returning `-EINVAL`, timeouts producing device errors, PLDM stubs being skipped without crashes, binned component requests becoming no-ops, ETR rejecting buffers outside allowed SRAM/DRAM/MMU ranges, ETR output pointer matching hardware write pointer after disable, SPMU counter output length validation, and full reset/halt paths leaving ETF/ETR disabled.
