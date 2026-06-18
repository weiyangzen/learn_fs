# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_1_d.h

## Purpose

`oss_3_0_1_d.h` is a generated AMDGPU OSS 3.0.1 register-address header. It gives stable symbolic `mm...` names for memory-mapped registers in the OSS block used by the interrupt handler, semaphore/virtualization logic, SRBM routing/control, SDMA engines, and HDP/XDP host path. The file contains no executable code; its purpose is to let ASIC-specific driver code use named register addresses with `RREG32`, `WREG32`, and related register helpers instead of embedding raw offsets.

The header is paired with `oss_3_0_1_sh_mask.h`, which defines fields and masks for these addresses. In this tree, `amdgpu/cz_ih.c` directly includes this file and the companion mask header to initialize, enable, disable, and service the interrupt-handler ring on Carrizo/VI-era hardware.

## Important APIs, Types, And Macros

The file exports preprocessor constants only. There are no functions, structs, enums, inline helpers, or storage definitions.

Important register families:

- `mmIH_VMID_0_LUT` through `mmIH_VMID_15_LUT` map interrupt handler VMID lookup entries at `0xe00` through `0xe0f`.
- `mmIH_RB_CNTL`, `mmIH_RB_BASE`, `mmIH_RB_RPTR`, `mmIH_RB_WPTR`, `mmIH_RB_WPTR_ADDR_HI`, and `mmIH_RB_WPTR_ADDR_LO` define the interrupt ring buffer control, base, read/write pointers, and writeback address registers.
- `mmIH_CNTL`, `mmIH_LEVEL_STATUS`, `mmIH_STATUS`, `mmIH_PERFMON_CNTL`, `mmIH_PERFCOUNTER*_RESULT`, `mmIH_DSM_MATCH_*`, and `mmIH_VERSION` cover interrupt enablement, status, performance counters, debug state-machine match registers, and version reporting.
- `mmSEM_*` registers cover semaphore MCIF/perfmon state, virtualization function enable and reset request state, mailbox registers, EDC, status, and chicken bits.
- `mmSRBM_*` registers cover SRBM control, GFX routing, read control/error reporting, status registers, soft reset, debug snapshots, chip revision, backend disable, clock gating for multiple blocks, interrupt status/ack, firewall error source/address, debug trigger controls, performance counters, CAM access, domain address windows, GRBM/GFX select/data windows, and virtualization control.
- `mmSDMA0_*` and `mmSDMA1_*` define two SDMA engine register maps. Each engine has microcode address/data, power and clock controls, main control/status registers, tiling/hash/timer registers, perfmon result registers, freeze and phase quantum controls, EDC/version/ID registers, VM/virtualization/atomic/ATCL1 registers, register-type classification registers, public register-type registers, and three queue families: `GFX`, `RLC0`, and `RLC1`.
- `mmSDMA0_GFX_*`, `mmSDMA0_RLC0_*`, `mmSDMA0_RLC1_*`, and equivalent `SDMA1` names define ring buffer control/base/pointers, write-pointer polling, read-pointer writeback, indirect-buffer control and addresses, context status, doorbell, virtual address, APE1, watermark, context-save address, preempt, dummy, and mid-command state registers.
- `mmHDP_*` and `mmHDP_XDP_*` define host data path nonsurface, debug, tiling, outstanding-request, address-config, memory-power, MEMIO, VF, direct-to-HDP, peer-to-peer mailbox/BAR, flush-status, busy/sticky, and debug-address/data/mask registers.

The address values are raw register indices in the older pre-SOC15 `mm...` convention. Unlike newer `*_offset.h` files, this header does not provide per-register `_BASE_IDX` macros.

## Control Flow

There is no local control flow. Runtime behavior occurs in consumers:

- `cz_ih.c` reads and writes `mmIH_CNTL`, `mmIH_RB_CNTL`, `mmIH_RB_BASE`, `mmIH_RB_RPTR`, `mmIH_RB_WPTR`, and `mmIH_RB_WPTR_ADDR_*` while bringing up the IH ring. Its flow disables interrupts, programs the dummy page and ring base, computes the ring size, enables overflow handling and write-pointer writeback, clears pointers, sets VMID/rearm fields, enables PCI bus mastering, and then enables the IH control and ring-buffer enable bits.
- `cz_ih_get_wptr()` uses the same IH register addresses with field masks from `oss_3_0_1_sh_mask.h` to detect write-pointer overflow, repair the software read pointer, set and clear the hardware overflow-clear bit, and return the masked write pointer.
- Other AMDGPU generations use matching `mm...` register names from sibling OSS headers for SDMA and HDP setup. For example, CIK SDMA code uses `mmSDMA0_GFX_RB_CNTL + sdma_offsets[i]` and companion masks to disable/enable rings, program read/write pointers, set writeback addresses, and enable indirect buffers. That is the integration pattern expected for the `SDMA0` and `SDMA1` blocks defined here.

## State And Persistence Behavior

The header itself is stateless and compile-time only. The named registers represent live GPU hardware state:

- IH ring registers persist the interrupt ring base, rptr/wptr, writeback address, overflow status, and interrupt enable bits until reset or reprogramming.
- SRBM registers control routing, reset, clock gating, debug capture, virtualization, firewall error reporting, and selected GFX context targeting. These values can affect broad driver access paths, not just one local block.
- SDMA registers hold engine firmware/microcode access state, queue ring bases and pointers, IB state, VM context settings, doorbells, preemption state, context-save addresses, and ATCL1/atomic behavior. They are stateful across ring start/stop and may be lost or reset during GPU reset, suspend/resume, or power transitions.
- HDP/XDP registers hold host-data-path, flush, MEMIO, peer-to-peer BAR, mailbox, VF, busy, and debug state used by CPU/GPU coherency and host access flows.

The driver must provide ordering, locking, polling, and reset sequencing. This header only defines numeric addresses.

## Dependencies

Primary dependencies are the AMDGPU register access layer and companion generated field headers:

- `oss_3_0_1_sh_mask.h` supplies `*_SHIFT` and `*_MASK` values for fields inside the registers named here.
- `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD` are the common access and field-update helpers used by direct consumers.
- `amdgpu_ih`, ring-buffer allocation, writeback memory, PCI bus mastering, MSI state, and device reset/resume code provide the runtime context for IH register programming.
- SDMA consumers rely on engine-instance offsets such as `sdma_offsets[i]` to derive SDMA1-style addresses from SDMA0 base symbols when the hardware layout is contiguous by instance.

## Integration Points

Direct integration found in this source tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c` includes `oss/oss_3_0_1_d.h` and uses its IH register constants throughout interrupt ring initialization, enable/disable, pointer management, overflow recovery, and interrupt vector decode/set-rptr flow.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_1_sh_mask.h` is the field-level companion and must match this address header.
- Sibling OSS headers such as `oss_3_0_d.h` and newer `osssys_*_offset.h` represent adjacent ASIC generations. Driver code must include the generation-matched header selected for the ASIC path.

## Risks

- Register-address drift is high impact. A wrong `mm...` value can cause writes to the wrong hardware register, corrupting interrupt routing, SDMA queues, reset controls, clock gating, or host-data-path state.
- Version confusion is plausible because OSS 3.0, OSS 3.0.1, and newer OSSSYS headers share many names with different packaging. Consumers must include the header matching the ASIC generation and access convention.
- The file provides no field masks. Using it without the matching `oss_3_0_1_sh_mask.h` risks hand-coded shifts or masks that do not match the hardware.
- SDMA instance arithmetic must be checked carefully. Code that adds an instance offset to `mmSDMA0_*` symbols assumes the SDMA0/SDMA1 layout spacing matches the selected ASIC.
- IH overflow handling is sensitive to pointer units and masks. In `cz_ih.c`, rptr/wptr are byte pointers, while ring storage is dword-addressed; wrong units can skip or reread interrupt vectors.
- Many registers control virtualization (`VF_ENABLE`, `VIRT_CNTL`, `VIRT_RESET_REQ`, `ACTIVE_FCN_ID`) or firewall/debug state. Incorrect writes can affect isolation or make later debug/error reporting misleading.

## Test Signals

- Compile coverage of `cz_ih.c` with this header catches missing or renamed IH register constants and mask names.
- Interrupt bring-up tests should confirm IH ring base, rptr/wptr, writeback address, overflow enable/clear, `RB_ENABLE`, and `ENABLE_INTR` are programmed as expected.
- Runtime interrupt tests should exercise MSI and non-MSI paths, write-pointer writeback, overflow recovery, and read-pointer update behavior.
- SDMA ring tests on matching hardware should confirm the `SDMA0`/`SDMA1` register spacing used by instance offsets, ring enable/disable, pointer writeback, IB enablement, and fence interrupt generation.
- Suspend/resume and GPU reset tests should verify IH, SRBM, SDMA, and HDP state is reinitialized from these register definitions without stale pointer or enable bits.
- Register traces or debugfs dumps can compare programmed offsets against OSS 3.0.1 hardware documentation for IH, SRBM, SDMA, SEM, and HDP blocks.
