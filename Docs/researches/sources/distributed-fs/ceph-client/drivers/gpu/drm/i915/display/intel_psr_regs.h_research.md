<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr_regs.h

## Purpose
`intel_psr_regs.h` centralizes MMIO register addresses and bitfield definitions for PSR1, PSR2, selective update tracking, Panel Replay/ALPM controls, PSR events, status registers, and port ALPM LFPS programming.

## Important APIs, Types, And Functions
This is a macro-only register definition header. Important register families include `TRANS_EXITLINE()`, `EDP_PSR_CTL()`, `TRANS_PSR_IMR()`, `TRANS_PSR_IIR()`, `EDP_PSR_AUX_CTL()`, `EDP_PSR_STATUS()`, `EDP_PSR_DEBUG()`, `EDP_PSR2_CTL()`, `PSR_EVENT()`, `EDP_PSR2_STATUS()`, `PSR2_MAN_TRK_CTL()`, `LNL_SFF_CTL()`, `LNL_CFF_CTL()`, `PIPE_SRCSZ_ERLY_TPT()`, `PR_ALPM_CTL()`, `ALPM_CTL()`, `ALPM_CTL2()`, `PORT_ALPM_CTL()`, and `PORT_ALPM_LFPS_CTL()`.

## Control Flow
The header has no executable flow. Runtime code uses these macros to pick platform/transcoder-specific registers and compose RMW masks for enabling PSR, selecting idle frames and training-pattern timing, reporting events, programming selective update regions, and configuring ALPM wake/sleep behavior.

## State And Persistence Behavior
The macros describe hardware state stored in display MMIO registers. Values programmed with these masks persist in hardware until later MMIO writes, power transitions, or reset. Several definitions distinguish legacy fixed registers from transcoder-relative registers.

## Dependencies And Integration Points
It includes `intel_display_reg_defs.h` and `intel_dp_aux_regs.h`. Users include `intel_psr.c`, ALPM code, display IRQ/debugfs paths, cursor/plane code, GVT MMIO tables, and virtualization handlers that need register knowledge.

## Risks
Bitfield accuracy is critical. A wrong mask, shift, or generation-specific address can silently program incorrect hardware state, causing display hangs, under-updates, failed low-power entry, or interrupt storms. The macro `EDP_MAX_SU_DISABLE_TIME(t)` appears to use `EDP_MAX_SU_DISABLE_TIME` instead of its mask name and should be treated carefully if used. Platform split points such as display version 20 and 30 require explicit auditing when adding new hardware.

## Test Signals
Signals include register readback through debugfs, PSR status transitions, IRQ mask behavior, selective update correctness, ALPM entry/exit, GVT register coverage, and hardware validation on each supported display generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr_regs.h -->
