<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb_regs.h

## Purpose
This header defines the MMIO register map and bitfields for per-pipe DSB engines.

## Important APIs, Types, and Functions
The central macros are `DSBSL_INSTANCE(pipe, id)` and registers such as `DSB_HEAD`, `DSB_TAIL`, `DSB_CTRL`, `DSB_MMIOCTRL`, `DSB_POLLFUNC`, `DSB_POLLMASK`, `DSB_STATUS`, `DSB_INTERRUPT`, `DSB_CURRENT_HEAD`, `DSB_RM_TIMEOUT`, `DSB_PMCTRL`, `DSB_PMCTRL_2`, `DSB_PF_LN_LOWER`, `DSB_PF_LN_UPPER`, `DSB_BUFRPT_CNT`, and `DSB_CHICKEN`.

Bitfields cover enable/halt/busy control, wait-for-vblank/line-in modes, non-posted writes, poll timing/count, internal state-machine status, program and error interrupts, ATS/GTT/poll/timeout/GOSUB faults, DEwake scanlines, force-dewake, DC-state overrides, and DSB chicken workarounds.

## Control Flow
There is no control flow. `intel_dsb.c` writes these registers to arm command buffers, configure polling, manage power/dewake, acknowledge interrupts, and decode errors.

## State and Persistence Behavior
The macros describe hardware-visible state. DSB head/tail/current-head hold GGTT command-buffer pointers; control and interrupt registers retain state until the driver writes them. PMCTRL and PMCTRL_2 influence display power/dewake behavior during execution.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` register helpers and is consumed by DSB execution and interrupt code. It must match the platform hardware spec for display versions that expose DSB.

## Risks
Register bit typos can have wide impact. Two macros appear suspicious by name, `DSB_MMIO_DEAD_CLOCKS_COUNT()` using `DSB_MMIO_DEAD_CLOCK_COUNT_MASK` and `DSB_RM_READY_TIMEOUT_VALUE()` using itself instead of the mask, so compile-time coverage or existing definitions must catch any mismatch. Version-specific bits must not be cleared or enabled on unsupported platforms.

## Test Signals
Signals include successful compile of all macros, DSB command execution, correct interrupt acknowledgement, register dumps matching hardware docs, and targeted tests that enable newer ATS/GOSUB bits only on supported display versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb_regs.h -->
