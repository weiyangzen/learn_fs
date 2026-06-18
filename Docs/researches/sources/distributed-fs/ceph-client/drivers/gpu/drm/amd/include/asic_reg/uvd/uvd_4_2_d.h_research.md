# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_d.h

## Purpose

`uvd_4_2_d.h` is the generated UVD 4.2 register-address header. It exposes the MMIO and indexed offsets needed by AMDGPU to initialize, command, monitor, power-manage, and reset the UVD video decode engine.

## Important APIs, Types, And Macros

The header includes semaphore registers; GPCOM VCPU command/data; engine control; UDEC address configuration; context index/data; CGC gate/status/control and UDEC status; LMI control/status/swap/address-extension; master interrupt enable; MPC mux/ALU controls; VCPU cache offsets/sizes at the `0x3d82` style locations; VCPU control; soft reset; RBC IB/RB base, size, read/write pointers, writeback, and controls; status and semaphore timeout registers; `UVD_RBC_IB_SIZE_UPDATE`; indexed LMI/CGC/MIF registers; PGFSM power registers; and power status.

## Control Flow And Data Flow

Driver control flow follows the standard UVD path: configure memory tiling and LMI behavior, prepare firmware cache windows, start the VCPU/engine, initialize the RBC ring, submit decode work through ring write pointers or IBs, service interrupts, and poll status/idle/timeout registers during teardown or recovery.

## State And Persistence Behavior

The header does not store state. The addressed registers persist engine configuration and event state: firmware/VCPU state, ring pointers, cache-window addresses, context ID, interrupt enablement, semaphore latches, clock/power state, and reset state.

## Dependencies And Integration Points

It should be used with `uvd_4_2_sh_mask.h`. Integration points are AMDGPU UVD 4.2 ASIC support, firmware loading, video decode scheduling, ring tests, LMI cache/coherency handling, interrupts, power gating, and GPU reset.

## Risks And Test Signals

Risks include assuming UVD 4.0's VCPU cache offset layout, mixing `ix*` and `mm*` access paths, and using masks from a nearby generation that has extra fields. Tests should run firmware boot, ring submission, decode workloads, semaphore fault paths, power-gating transitions, and generation-register diffs.
