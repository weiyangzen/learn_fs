# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_7_0_offset.h

## Purpose

`uvd_7_0_offset.h` is a generated UVD 7.0 register-offset header. It uses offset plus base-index pairs: each `mm*` register macro is paired with `mm*_BASE_IDX`, allowing AMDGPU helpers to combine a block-relative offset with the correct register base. It has 187 macros, the include guard `_uvd_7_0_OFFSET_HEADER`, and no executable logic. Comments identify `uvd0_uvd_pg_dec` at base `0x1fb00`, `uvd0_uvdnpdec` at base `0x20000`, and `uvd0_uvddec` at base `0x20c00`.

## Important APIs, Types, And Macros

The `uvd0_uvd_pg_dec` group covers power status and DPG ring/cache setup (`mmUVD_DPG_RBC_*`, DPG VCPU cache BARs, DPG cache offset). The `uvd0_uvdnpdec` group covers JPEG/UDEC address config, firmware mailbox registers, SUVD clock-gating controls, VCPU cache BARs, power status, no-op, scratch, primary/secondary rings, JRBC read pointer, and LMI RBC/IB BARs. The `uvd0_uvddec` group covers semaphore control, JRBC BAR/write pointer, third ring, JPEG/UVD clock gating, context index/data, LMI controls, interrupts, firmware status, VM control, swap controls, MPC controls, VCPU cache/control, soft reset, RBC controls, status, semaphore timeouts, and context IDs. Every register has a `_BASE_IDX` value, all `1` here.

## Control Flow And Data Flow

The header has no runtime control flow. Consumers select an offset and its base index, use register helpers that understand base-index addressing, combine with companion UVD 7.0 field masks, and program DPG state, firmware mailboxes, rings, LMI, clocks, interrupts, reset, and status polling. The block split matters because DPG registers, non-power-gated decode registers, and decode-core registers participate in different parts of init and power-management flow.

## State And Persistence Behavior

The header stores no software state. It names persistent hardware registers for DPG ring pointers/bases, VCPU cache BARs and offsets, firmware mailbox data, UDEC/JPEG address geometry, LMI and VM controls, clock-gating configuration, interrupt enables, VCPU control, soft reset, RBC ring state, context IDs, firmware status, and semaphore timeout latches.

## Dependencies And Integration Points

It depends only on the preprocessor and integrates with AMDGPU helpers that use `mmREG` plus `mmREG_BASE_IDX`, UVD 7.0 mask headers, firmware loading, mailbox code, decode ring management, dynamic power gating, LMI/VM setup, interrupt handling, JPEG/SUVD paths, reset recovery, and generated ASIC register databases.

## Risks And Edge Cases

The base-index contract is part of the API; mismatching `_BASE_IDX` can access the wrong aperture. UVD 7.0 splits registers across address blocks, so UVD 6.0 flat-offset assumptions are unsafe. DPG power and ring registers require sequencing not encoded here. High/low BARs require correct split programming. Interrupt, reset, timeout, and firmware status registers can have side effects not visible in offset definitions. New UVD 7.0 registers such as `mmUVD_FW_STATUS`, `mmUVD_LMI_VM_CTRL`, `mmUVD_CONTEXT_ID2`, and DPG RBC registers need generation-specific handling.

## Test Signals

Use AMDGPU compile coverage for UVD 7.0, generated-register diffing, hardware probe, firmware boot and `mmUVD_FW_STATUS` checks, DPG ring setup and pause/resume tests, decode and JPEG submission, interrupt delivery, LMI/VM coherency checks, suspend/resume with power gating, GPU reset recovery, and register-access tests that verify base-index addressing.
