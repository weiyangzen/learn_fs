# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.c

## Purpose

This file implements SMU7 BACO/BAMACO support detection and state dispatch. BACO is the bus-active, chip-off low-power state used by supported AMD GPUs.

## Important APIs, Types, and Functions

`smu7_get_bamaco_support()` checks both the PowerPlay BACO platform capability and the BIF fuse strap before returning `BACO_SUPPORT`. `smu7_baco_get_state()` reads `mmBACO_CNTL` and maps `BACO_MODE` to `BACO_STATE_IN` or `BACO_STATE_OUT`. `smu7_baco_set_state()` dispatches to ASIC-specific implementations for Tonga, Fiji, Polaris, VegaM, and optionally CIK Bonaire/Hawaii.

## Control Flow and State

The file does not allocate memory or maintain driver-owned state. Runtime state lives in hardware registers and in ASIC-specific BACO implementation files. The set-state function is a switch on `adev->asic_type`.

## Dependencies and Integration

It depends on `amdgpu.h`, `common_baco.h` through the header, ASIC BACO helpers (`tonga_baco.h`, `fiji_baco.h`, `polaris_baco.h`, `ci_baco.h`), and BIF/SMU register masks. It integrates with the hwmgr BACO hooks selected for SMU7-class GPUs.

## Risks and Test Signals

Support is gated by both firmware platform caps and fuses; a mismatch can disable BACO even when an ASIC path exists. Unsupported ASICs return `-EINVAL`. Test signals include BACO capability reporting, register-observed state changes, suspend/runtime power transitions, and ASIC-specific BACO enter/exit validation.
