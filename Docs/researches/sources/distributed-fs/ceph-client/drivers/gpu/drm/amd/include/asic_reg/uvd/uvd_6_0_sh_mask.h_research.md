# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_sh_mask.h

## Purpose

`uvd_6_0_sh_mask.h` is the generated field mask/shift companion to the UVD 6.0 address header. It describes bit layouts for semaphores, VCPU command mailboxes, decode address configuration, clock and power gating, local memory interface, media pipeline controls, VCPU control, soft reset, ring-buffer controller, status, timeout handling, SUVD/JPEG, VMID routing, cache control, and MIF/JPEG address configuration. It has 1,007 `#define`s and no functions, structs, enums, or variables.

## Important APIs, Types, And Macros

Major macro families include `UVD_SEMA_*` address/command/control/timeout fields, `UVD_GPCOM_VCPU_*` firmware mailbox fields, `UVD_ENGINE_CNTL`, repeated `UVD_UDEC_*`, `UVD_MIF_*`, and `UVD_JPEG_ADDR_CONFIG` tiling fields, `UVD_CGC_*`, `UVD_SUVD_CGC_*`, `UVD_CGC_MEM_CTRL`, `UVD_CGC_CTRL2`, `UVD_PGFSM_*`, and `UVD_POWER_STATUS*` clock/power fields, `UVD_LMI_*` BAR/coherency/swap/cache/VMID fields, `UVD_MPC_*` media pipeline controls, `UVD_VCPU_*` cache/control fields, `UVD_SOFT_RESET`, `UVD_RBC_*`, `UVD_STATUS`, and `UVD_CONTEXT_ID`.

## Control Flow And Data Flow

The header has no executable control flow. Consumers select UVD 6.0 addresses from `uvd_6_0_d.h`, encode values with this header's masks and shifts, access the register through MMIO or indexed helpers, and poll or update hardware. Data flow covers decode-ring setup, mailbox submission, VCPU cache layout, LMI extension/VMID/coherency, cache flushes, clock/power changes, reset sequencing, semaphore waits/signals, and status reporting.

## State And Persistence Behavior

The file stores no software state. It describes stateful hardware fields: ring pointers and sizes, VCPU cache offsets/sizes, BARs, LMI coherency and VMID state, clock-gating modes, power-gating FSM state, timeout latches, reset bits/status, context IDs, firmware mailbox values, and UVD busy/report status. Some fields are latched or clear/ack style, which is not expressible by mask names alone.

## Dependencies And Integration Points

It depends only on the preprocessor and is intended to pair with `uvd_6_0_d.h` and `uvd_6_0_enum.h`. Integration points include UVD init, ring and IB submission, firmware command handling, VMID/memory routing, LMI cache/coherency code, clock/power gating, suspend/resume, GPU reset, JPEG/SUVD codec paths, and generated-register validation.

## Risks And Edge Cases

One-bit mask or shift errors can break decode, coherency, power management, or reset recovery. Repeated address-config fields make plausible wrong-register programming easy. 64-bit BAR and address-extension fields need correct split-word handling and alignment. Reset and power fields need idle polling and sequencing. UVD 5.0 and 6.0 layouts are similar but not identical. VMID/cache fields affect memory isolation and coherency.

## Test Signals

Use compile coverage, canonical register diffs, hardware probe on UVD 6.0 ASICs, firmware boot and mailbox tests, decode ring and IB submission, ring pointer writeback checks, semaphore timeout tests, LMI cache/coherency tests, power and clock gating transitions, suspend/resume, GPU reset recovery, JPEG/SUVD decode coverage, and VMID routing checks.
