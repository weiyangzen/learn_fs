# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_d.h

## Purpose

`uvd_4_0_d.h` is the generated register-address header for UVD 4.0. It exports MMIO and indexed offsets for the video decode engine's firmware communication, memory-interface configuration, clock/power management, ring-buffer command processor, semaphore handling, and status/control registers.

## Important APIs, Types, And Macros

The macro set largely mirrors UVD 3.x but is ordered differently and includes `mmUVD_GP_SCRATCH4`. Important groups include `ixUVD_CGC_*`, `ixUVD_LMI_*`, and `ixUVD_MIF_*` indexed registers; `mmUVD_CGC_*`; context index/data; `mmUVD_ENGINE_CNTL`; GPCOM command/data; LMI control/status/swap/address-extension; master interrupt enable; MPC setup; PGFSM and power status; RBC IB/RB base, pointer, writeback, control, and size-update registers; semaphore address/command/control and timeout registers; soft reset; UDEC address configuration; VCPU cache windows; and `mmUVD_VCPU_CNTL`.

## Control Flow And Data Flow

The driver programs UVD memory format and cache controls, loads and starts firmware, configures clock/power gating, initializes the RBC ring, and submits decode commands through write-pointer updates. Status and completion flow through interrupts, firmware/VCPU status fields, semaphore status, and ring read pointers.

## State And Persistence Behavior

The header is stateless. The hardware registers it names hold persistent engine configuration: ring locations, cache windows, command state, clock-gating masks, low-power memory controls, semaphore state, and reset status.

## Dependencies And Integration Points

It should be paired with `uvd_4_0_sh_mask.h`. It integrates with AMDGPU UVD 4.0 ASIC support, firmware boot, ring testing, decode scheduling, interrupt handling, and power/reset code.

## Risks And Test Signals

Risks include confusing UVD 4.0 VCPU cache offsets with the UVD 3.1/4.2 layout, mixing indexed and MMIO access, and accidentally reusing UVD 4.2 masks for fields that differ. Tests should boot firmware, run decode and ring tests, verify clock-gating transitions, handle semaphore faults, and compare generated offsets against the hardware register source.
