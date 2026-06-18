# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_sh_mask.h

## Purpose

`uvd_5_0_sh_mask.h` is a generated AMDGPU hardware register field-layout header for the UVD 5.0 video decode block. It contains no executable code; it exports preprocessor constants that describe masks and shifts for the fields inside UVD semaphore, firmware command, tiling/address-configuration, clock/power, local-memory-interface, ring-buffer, VCPU, reset, status, and SUVD/JPEG registers.

The include guard is `UVD_5_0_SH_MASK_H`. The public API is the AMD register convention where `REGISTER__FIELD_MASK` is the already-positioned bit mask and `REGISTER__FIELD__SHIFT` is the matching right-shift amount. The file has 1,019 `#define`s and no functions, structs, enums, or variables.

## Important APIs, Types, And Macros

Important macro families include `UVD_SEMA_*` semaphore fields, `UVD_GPCOM_VCPU_*` firmware mailbox fields, `UVD_UDEC_*`/`UVD_MIF_*`/`UVD_JPEG_ADDR_CONFIG` tiling geometry fields, `UVD_CGC_*` and `UVD_PGFSM_*` clock and power fields, `UVD_LMI_*` BAR/coherency/swap/VMID fields, `UVD_MPC_*` media pipeline controls, `UVD_VCPU_*` cache and VCPU controls, `UVD_SOFT_RESET` per-subblock reset bits, `UVD_RBC_*` ring-buffer controller fields, `UVD_STATUS` busy/report bits, and `UVD_SUVD_CGC_*` H.264/HEVC clock-gating fields. UVD 5.0 includes `SCLR` and `UVD_SC` SUVD fields that are absent from the UVD 6.0 mask header in this work item.

## Control Flow And Data Flow

This header has no control flow. Driver code selects a matching UVD 5.0 register address, composes or decodes values with the `*_MASK` and `*__SHIFT` constants, and reads or writes the hardware through AMDGPU MMIO/indexed helpers. Typical flows include semaphore setup, firmware mailbox submission, VCPU cache programming, ring setup, VMID routing, LMI coherency/swap programming, clock and power changes, block reset, and status polling.

## State And Persistence Behavior

The header stores no software state. The constants describe persistent GPU state such as ring bases/pointers, VCPU cache layout, LMI VMID/cache/coherency state, semaphore timeout latches, clock-gating and memory light-sleep configuration, power-gating FSM state, and reset/status bits. Wrong masks or shifts can leave hardware misconfigured until another write or reset.

## Dependencies And Integration Points

It depends only on the C preprocessor and is paired with a compatible UVD 5.0 address header and AMDGPU register helpers. Integration points include UVD initialization, firmware boot, decode ring submission, semaphore synchronization, power management, reset paths, LMI coherency, VMID routing, JPEG/SUVD decode support, and generated-register sync tooling.

## Risks And Edge Cases

Manual edits are risky because bitfield errors rarely fail at compile time. 64-bit BAR and address fields require correct high/low ordering and alignment. Reset, clock, power, and cache fields have sequencing rules not encoded here. Timeout and clear fields may have latch or write-one-to-clear semantics. Similarity with UVD 6.0 makes accidental cross-generation use plausible.

## Test Signals

Use AMDGPU builds, generated-register diffs, boot/probe on UVD 5.0 GPUs, firmware loading, decode ring submission, semaphore timeout tests, suspend/resume, reset recovery, clock/power-gating transitions, LMI coherency tests, JPEG/SUVD paths, and VMID isolation checks.
