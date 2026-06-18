# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_d.h

## Purpose

`uvd_3_1_d.h` is a generated register-address header for the AMD UVD 3.1 video decode engine. It defines `mm*` MMIO offsets and `ix*` indexed-register offsets for firmware communication, semaphores, memory-interface setup, clock/power control, ring-buffer command submission, VCPU control, and status reporting.

## Important APIs, Types, And Macros

The public API is a flat macro list. Key groups are `mmUVD_SEMA_*` semaphore registers; `mmUVD_GPCOM_VCPU_*` firmware command/data registers; `mmUVD_ENGINE_CNTL`; UDEC/MIF address-configuration registers; context index/data; CGC gate/status/control; LMI control/status/swap/address-extension registers; master interrupt enable; firmware start/status; MPC mux/ALU controls; VCPU cache offset/size and `mmUVD_VCPU_CNTL`; `mmUVD_SOFT_RESET`; RBC IB/RB base, size, pointers, write-pointer control, read-pointer writeback, and status; semaphore timeout registers; and PGFSM/power-status registers.

## Control Flow And Data Flow

Driver initialization programs memory tiling and LMI settings, configures VCPU firmware cache windows, starts firmware through engine/VCPU controls, enables interrupts and semaphores, and submits decode work through the RBC ring and indirect buffers. Runtime paths update write pointers, read status, handle semaphore timeouts, and use GPCOM data registers for firmware commands.

## State And Persistence Behavior

The header stores no state, but the addressed registers control persistent hardware state: firmware boot state, ring pointers, memory address mappings, cache/swap settings, clock-gating state, power state, soft-reset bits, context ID, and semaphore timeout latches.

## Dependencies And Integration Points

It pairs with `uvd_3_1_sh_mask.h` and integrates with AMDGPU UVD initialization, firmware loading, ring submission, interrupt handling, power management, and reset paths. Indexed `ix*` registers require the correct indexed-register access method, not ordinary MMIO.

## Risks And Test Signals

Risks include address/mask generation mismatch, using an `ix*` offset with an MMIO helper, misprogramming ring pointer alignment, or writing reset/power registers out of sequence. Tests should cover video decode firmware boot, ring submission, interrupt delivery, semaphore timeout handling, suspend/resume, and reset recovery on UVD 3.1 hardware.
