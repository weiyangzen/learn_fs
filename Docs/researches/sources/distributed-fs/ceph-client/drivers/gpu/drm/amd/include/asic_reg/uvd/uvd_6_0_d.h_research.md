# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_d.h

## Purpose

`uvd_6_0_d.h` is a generated AMDGPU register-address header for the UVD 6.0 video decode block. It exports symbolic MMIO offsets (`mmUVD_*`) and indexed-register offsets (`ixUVD_*`) for semaphores, firmware mailboxes, rings, local memory interface, clock/power management, VCPU cache, resets, status, and JPEG/SUVD address configuration. It has 107 `#define`s, the include guard `UVD_6_0_D_H`, and no executable logic.

## Important APIs, Types, And Macros

The address API covers semaphore and mailbox registers (`mmUVD_SEMA_*`, `mmUVD_GPCOM_VCPU_*`), core control and address configuration (`mmUVD_ENGINE_CNTL`, `mmUVD_UDEC_*_ADDR_CONFIG`, `mmUVD_JPEG_ADDR_CONFIG`, MIF address config registers), ring and BAR registers (`mmUVD_RB_*`, `mmUVD_LMI_RBC_*_64BIT_BAR_*`, VCPU cache BARs), clock/power registers (`mmUVD_CGC_*`, `mmUVD_SUVD_CGC_*`, `mmUVD_PGFSM_*`, `mmUVD_POWER_STATUS*`), LMI routing/swap/status registers, VCPU cache/control registers, soft reset, status, context ID, and semaphore timeout registers. `ixUVD_*` entries identify indexed-register space for internal VMID, cache, swap, memory power, and address-extension controls.

## Control Flow And Data Flow

The file has no runtime control flow. Consumers choose an `mmUVD_*` or `ixUVD_*` offset, combine it with masks from `uvd_6_0_sh_mask.h`, access the register through the correct MMIO or indexed helper, and then poll, submit, reset, or power-manage UVD. The register order supports typical init: configure address swizzles and semaphores, set rings/BARs/cache windows, program LMI/VMID routing, enable clocks/power, boot or command VCPU, then monitor status and timeouts.

## State And Persistence Behavior

The header stores no state. It names hardware registers whose contents persist in the device until changed by software, firmware, reset, or power management. Persistent state includes mailbox contents, ring bases/sizes/pointers, VCPU cache windows, LMI coherency and VMID routing, clock/power state, context IDs, timeout latches, and reset/status bits.

## Dependencies And Integration Points

It depends only on the preprocessor and integrates with `uvd_6_0_sh_mask.h`, `uvd_6_0_enum.h`, AMDGPU MMIO/indexed helpers, firmware loading and command submission, decode ring management, power management, reset code, and memory/VMID setup.

## Risks And Edge Cases

Offsets must match UVD 6.0. Mixing `mm*` and `ix*` accessors can access the wrong space. The header does not encode read-only, write-only, clear-on-write, latch, ordering, or delay semantics. Ring and BAR registers need correct split-word ordering and alignment. Power/reset registers can disrupt active decode work.

## Test Signals

Use compile coverage, generated-register diffs, UVD firmware boot, decode submission through supported rings, semaphore timeout checks, suspend/resume and power-gating tests, GPU reset recovery, LMI coherency checks, and tests that cover both MMIO and indexed register access.
