# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_sh_mask.h

## Purpose

`uvd_4_2_sh_mask.h` is the generated field-layout header for UVD 4.2. It provides masks and shifts for semaphore, command, memory-interface, clock-gating, ring-buffer, reset, status, and power-management registers.

## Important APIs, Types, And Macros

The public macro families cover semaphore address/command/VMID and timeout controls; GPCOM VCPU command/data; engine start; UDEC/MIF address-configuration geometry; LMI extended addressing, coherency, urgent, clean/idle, swap, and cache controls; context index/data; CGC gate/status/control for the main UVD and UDEC subdomains; master interrupt enable/overrun; MPC mux/ALU/debug controls; VCPU cache window fields; VCPU control; soft resets for RBC, LBSI, LMI, VCPU, UDEC, CSM, CXW, TAP, MPC, FWV, IH, MPRD, IDCT, LMI_UMC, SPH, MIF, and LCM; RBC ring/IB fields; PGFSM and power status.

## Control Flow And Data Flow

Consumers use these fields to bring the engine out of reset, program memory layout, load firmware cache ranges, enable clocks and interrupts, submit ring work, and wait for idle or clean status. Data moves from software command buffers to RBC/IB registers and from hardware back through status, timeout, interrupt, and read-pointer fields.

## State And Persistence Behavior

The macros are stateless. Underlying fields affect persistent video-engine behavior, including power/clock state, cache coherency, firmware command state, ring fetch state, semaphore timeout latches, and reset state. Some fields are status or clear-style and require semantics from the hardware guide or driver code.

## Dependencies And Integration Points

It pairs with `uvd_4_2_d.h` and integrates with AMDGPU UVD 4.2 firmware, ring, interrupt, power, LMI, and reset paths. It is close to UVD 3.1 but should remain generation-specific.

## Risks And Test Signals

Risks include truncating split address fields, writing reserved/RFU fields, enabling ring fetch before ring base and firmware windows are valid, and missing generation deltas from UVD 4.0. Test signals include UVD ring tests, decode validation, LMI clean/idle polling, semaphore timeout injection, suspend/resume, and generated header diffing.
