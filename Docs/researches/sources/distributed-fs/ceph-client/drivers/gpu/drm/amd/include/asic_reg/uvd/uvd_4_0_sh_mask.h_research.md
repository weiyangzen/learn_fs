# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_sh_mask.h

## Purpose

`uvd_4_0_sh_mask.h` defines the UVD 4.0 register field masks and shifts used with `uvd_4_0_d.h`. The file is generated C preprocessor data and has no functions, structs, or runtime control flow.

## Important APIs, Types, And Macros

Field groups include CGC dynamic clock/ramp controls, clock gates, clock status, UDEC subblock status, and low-power memory controls; context and GPCOM command/data fields; LMI address extension, cache control, coherency, urgent, clean/idle, and byte-swap controls; semaphore address/command/enable and timeout fields; master interrupt enable/overrun fields; UDEC/MIF tiling geometry fields; MPC mux/ALU and debug fields; PGFSM power-control/readback and power-status fields; RBC ring and IB base/size/pointer/control fields; UVD soft-reset bits; UVD status; and VCPU control fields.

## Control Flow And Data Flow

Consumers encode register writes for firmware startup, ring initialization, clock/power configuration, LMI cache and coherency setup, and semaphore timeout control. Runtime status is decoded from clock-status bits, LMI clean/idle fields, `UVD_STATUS`, semaphore timeout status, and ring read pointers.

## State And Persistence Behavior

The macros are stateless, but the fields describe persistent hardware state. Clock-gate and memory-light-sleep fields influence power behavior across idle intervals; LMI fields control cache/coherency behavior; ring fields determine command fetch; reset fields alter subblock state; timeout fields latch error conditions.

## Dependencies And Integration Points

It pairs with `uvd_4_0_d.h` and is consumed by AMDGPU UVD 4.0 firmware, ring, interrupt, LMI, power-management, and reset code. The `L` suffix on many masks makes the constants suitable for the generated C macro style, but consumers still need correct register width handling.

## Risks And Test Signals

Risks include reserved-bit writes, generation drift from UVD 4.2, wrong VCPU cache-field assumptions, and sequencing errors around ring fetch, clock gating, or reset. Tests should include UVD ring tests, decode playback, interrupt and semaphore timeout paths, LMI cache flush/coherency checks, suspend/resume, and generated mask/shift diffing.
