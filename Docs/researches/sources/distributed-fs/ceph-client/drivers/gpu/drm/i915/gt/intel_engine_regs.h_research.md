<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_regs.h

## Purpose
`intel_engine_regs.h` defines engine-relative MMIO register offsets and bitfields used by i915 command streamer, execlist, context, power, predicate, nonprivileged access, SFC, and media clock-gating code.

## Important APIs, Types, and Functions
The header is macro-only. Major register groups include ring head/tail/start/control, sync registers, PSMI/max-idle, ACTHD/DMA_FADD/IPEIR/IPEHR/INSTDONE, HW status page, HWSTAM, MI_MODE, interrupt mask/error/status registers, RPCS fields, reset control, batch-buffer state/address, context control, PDP registers, execlist status/control, timestamps, force-to-nonprivileged slots, CS GPRs, SFC lock/status registers, and VDBOX clock-gating controls.

## Control Flow
There is no C control flow. Other code passes these macros to engine-relative accessors such as `ENGINE_READ(engine, RING_HEAD)` or `ENGINE_WRITE(engine, RING_MI_MODE, value)`, where the engine MMIO base is supplied at call time.

## State and Persistence
The header owns no runtime state. It defines the address/bit layout for persistent hardware registers. Writes to these registers configure engine execution, context save/restore, reset, interrupts, PPGTT, scheduling, MOCS overrides, and media units.

## Dependencies and Integration Points
It depends on `i915_reg_defs.h` for `_MMIO`, `REG_BIT`, `REG_GENMASK`, and field helpers. It is included by engine setup, command emission, reset, PM, workarounds, context SSEU, diagnostics, and media/video code.

## Risks and Edge Cases
Incorrect offsets or bit masks can program the wrong hardware register. Several offsets alias across generations, such as `ACTHD`/`GEN8_R_PWR_CLK_STATE`, so callers must select by platform. Engine-relative macros require a base-aware register accessor; direct uncore use without supplying the correct base would be wrong.

## Test Signals
Signals include register dump sanity, engine bring-up on every class, reset and stop-ring behavior, context switch and PPGTT enablement, SFC lock tests, workarounds using force-to-nonprivileged slots, and platform-specific MMIO validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_regs.h -->
