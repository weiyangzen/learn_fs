# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_sh_mask.h

## Purpose

`uvd_3_1_sh_mask.h` is the generated UVD 3.1 field-layout header. It supplies masks and shifts for the register addresses in `uvd_3_1_d.h`; it implements no executable logic.

## Important APIs, Types, And Macros

The exported fields cover semaphore address/command/VMID control; GPCOM VCPU command and data payloads; engine start bits; UDEC and MIF tiling geometry; semaphore enable and timeout counters; LMI extended addressing, coherency, urgent, clean/idle status, swap controls, and cache flush/enable bits; context index/data; CGC gate/status/control for SYS, UDEC, MPEG2, RE/CM/IT/DB/MP, RBC, LMI, MPC, WCB, VCPU, and SCPU domains; master interrupt enables and overrun status; MPC mux/ALU/debug controls; VCPU cache windows and `UVD_VCPU_CNTL`; soft-reset bits for many UVD subblocks; RBC ring/IB base, size, read/write pointer, and control fields; PGFSM power-control/readback fields; power status; and firmware status masks such as busy, active, done, pass, fail, and invalid firmware metadata.

## Control Flow And Data Flow

Consumer code encodes startup, clock-gating, firmware, ring, and semaphore values with these masks. Decode submission data flows from software-managed ring buffers through RBC fields to the UVD VCPU. Status data flows back through `UVD_STATUS`, LMI clean/idle bits, interrupt enables/overruns, semaphore timeout latches, and firmware status bits.

## State And Persistence Behavior

The macros are stateless. The underlying fields control persistent engine state: clocks, power, reset, firmware validation, memory coherency, ring fetch behavior, timeout counters, and address-extension settings. Many fields must be preserved or updated in a defined sequence.

## Dependencies And Integration Points

This file must match `uvd_3_1_d.h`. It integrates with AMDGPU UVD firmware loading, ring tests, IB submission, interrupt handling, LMI cache maintenance, clock/power gating, and reset logic.

## Risks And Test Signals

Risks include unmasked writes to reserved/RFU bits, 64-bit address truncation through split address fields, incorrect ring alignment, enabling clocks or ring fetch before firmware/memory windows are valid, and treating timeout/status bits as ordinary writable state. Test signals include firmware-auth status checks, UVD ring tests, decode conformance, interrupt overrun tests, LMI clean/idle polling, and suspend/resume power-gating validation.
