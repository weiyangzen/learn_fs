# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h lines 10022-11287

## Scope

This chunk covers the final 1,266 lines of the generated AMD NBIF 6.3.1 offset header. It starts at the last `BASE_IDX` macro for VF12's `BIF_VMHV_MAILBOX`, then enumerates the remaining VF12 blocks and full VF13 through VF23 register-offset blocks, ending with the header's `#endif`.

The source is not executable code. It is a preprocessor register map: each hardware register gets a `#define` for its offset and a companion `#define` ending in `_BASE_IDX` that selects the SOC15 register base instance used by AMDGPU register access helpers.

## Purpose

The chunk provides symbolic offsets for SR-IOV virtual-function NBIF/RCC registers on AMD GPUs using the NBIF 6.3.1 register layout. These constants allow C code to use named register identifiers instead of literal offsets when accessing per-VF MMIO/configuration spaces.

The visible register families are:

- VF12 trailing mailbox/system/RCC/MSI-X definitions.
- VF13 through VF23 full repeated definitions.
- Per-VF BIF/PF-VF control and status registers for bus-master state, atomic error logging, doorbell self-ring apertures, HDP coherency flush/invalidate, transaction-pending status, PF/VF mailbox buffers and controls, and VM/HV mailbox.
- Per-VF `SYSPFVFDEC` indexed MMIO registers: `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- Per-VF RCC registers: error log, doorbell aperture enable, configured memory size, reserved configuration, and IOV function identifier.
- Per-VF graphics MSI-X table registers for vectors 0 through 3 and the MSI-X pending bit array (`GFXMSIX_PBA`).

## Important Definitions

The chunk contains 1,075 `#define` lines: 537 register offset macros and 538 base-index macros. The extra base-index macro is because the line range begins at `regBIF_BX_DEV0_EPF0_VF12_BIF_VMHV_MAILBOX_BASE_IDX`, whose corresponding offset macro appears immediately before the chunk.

The main macro naming pattern is:

- `regBIF_BX_DEV0_EPF0_VF<N>_<REGISTER>` for BIF virtual-function registers.
- `regRCC_DEV0_EPF0_VF<N>_<REGISTER>` for RCC virtual-function registers.
- `reg..._BASE_IDX` for the SOC15 base index to pair with the offset macro.

Base-index meanings in this chunk are consistent by block:

- `BIFPFVFDEC1` BIF and RCC PF/VF registers use base index `2`.
- `SYSPFVFDEC` indexed MMIO registers use base index `0`.
- `BIFDEC2` MSI-X table and PBA registers use base index `3`.

Representative repeated offsets:

- `BIF_BME_STATUS` at `0x00eb` and `BIF_ATOMIC_ERR_LOG` at `0x00ec`.
- Doorbell self-ring aperture registers at `0x00f3` through `0x00f5`.
- HDP coherency controls at `0x00f6`, `0x00f7`, and for VF12-VF15 also `0x00f9`/`0x00fa`.
- `GPU_HDP_FLUSH_REQ` at `0x0106`, `GPU_HDP_FLUSH_DONE` at `0x0107`, and `BIF_TRANS_PENDING` at `0x0108`.
- Mailbox transmit/receive buffers at `0x0136` through `0x013d`, mailbox control at `0x013e`, interrupt control at `0x013f`, and VM/HV mailbox at `0x0140`.
- `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI` at `0x0000`, `0x0001`, `0x0006`.
- RCC configuration/error registers at `0x0085`, `0x00c0`, `0x00c3`, `0x00c4`, `0x00c5`.
- MSI-X vector entries from `0x0400` through `0x040f`, with `GFXMSIX_PBA` at `0x0800`.

## Control Flow

There is no runtime control flow in this chunk. The C preprocessor substitutes these constants into call sites that use AMDGPU/SOC15 register access helpers.

Practical access flow in the surrounding driver is:

1. `amdgpu/nbif_v6_3_1.c` includes `nbif/nbif_6_3_1_offset.h`.
2. Driver functions use macros from this header with helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `WREG32_FIELD15_PREREG`, and bitfield helpers from the matching `nbif_6_3_1_sh_mask.h`.
3. The helper combines the IP block (`NBIO`), instance, register offset, and `_BASE_IDX` metadata to target the correct MMIO register base.

Within the searched source tree, the exact VF12-VF23 macros from this chunk are not referenced by non-generated C files. They are still part of the generated hardware contract and may be used by future SR-IOV code, debug paths, or out-of-tree users.

## State and Persistence

The header itself stores no state. The named registers represent persistent or semi-persistent device state in hardware:

- Doorbell aperture and self-ring registers configure guest-visible doorbell windows.
- HDP flush request/done and coherency registers synchronize CPU/GPU memory visibility.
- Mailbox transmit/receive buffers and interrupt controls carry PF/VF or VM/hypervisor messages.
- MSI-X address/data/control/PBA registers model interrupt delivery state for each VF.
- RCC memory-size and IOV function identifier registers describe per-function configuration exposed by hardware/firmware.

Incorrect offsets or base indices can persist until a device reset or function-level reset because writes land in hardware registers rather than ordinary process memory.

## Dependencies

This chunk depends on the AMDGPU register access infrastructure and matching generated masks:

- `amdgpu/nbif_v6_3_1.c` includes this offset header and `nbif/nbif_6_3_1_sh_mask.h`.
- SOC15 register helpers rely on the offset macro plus its `_BASE_IDX` companion.
- SR-IOV and virtualization paths depend on these per-VF constants matching silicon/firmware register layout.
- The surrounding driver also includes related generated headers for PCIe and NBIO interrupt source IDs.

The file is guarded by `_nbif_6_3_1_OFFSET_HEADER`; this chunk closes that guard.

## Integration Points

The immediate in-tree integration point is NBIF 6.3.1 support under `drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`. That C file uses this header for NBIO register offsets involved in memory-controller access, HDP flush remapping, doorbell setup, interrupt control, PCIe index/data access, ASPM/LTR programming, and ROM offset handling.

The visible VF-specific definitions are aligned with SR-IOV concepts:

- PF/VF mailbox registers integrate with virtualization management and guest-host communication.
- VF doorbell aperture registers integrate with GPU queue submission paths because doorbells are used to notify hardware engines.
- HDP flush and coherency registers integrate with memory synchronization paths.
- MSI-X vector/PBA registers integrate with interrupt delivery for virtual functions.

## Risks

- Generated-header drift is the primary risk. A single wrong offset or `_BASE_IDX` can redirect MMIO accesses to the wrong hardware register.
- The VF blocks are repetitive, so copy/generation errors can be hard to spot in review.
- VF16-VF23 BIF blocks omit the `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL` and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL` macros that appear for VF12-VF15 in this chunk; this may be intentional hardware-layout variation, but consumers must not assume every VF block has identical register coverage.
- Because the exact VF12-VF23 names are not referenced by non-generated in-tree code, normal compile coverage may not catch bad values unless a build or test path explicitly uses these constants.
- These are hardware-facing constants. Unit tests cannot validate them without a trusted register database or device/emulator access.

## Test Signals

Useful validation signals for this chunk are mostly structural and hardware-integration based:

- Build coverage for AMDGPU with NBIF 6.3.1 enabled verifies header syntax, include guard closure, and macro availability.
- Static checks can verify every register macro has the expected `_BASE_IDX` companion, with the known exception that this chunk begins with a trailing VF12 `_BASE_IDX` for an offset defined just before line 10022.
- Generated-register diffing against AMD's authoritative register database should validate offsets and base indices for VF12-VF23.
- Runtime SR-IOV smoke tests on matching hardware should exercise VF mailbox, doorbell, HDP flush, and MSI-X interrupt behavior.
- Negative symptoms include VF interrupt failures, guest doorbell timeouts, PF/VF mailbox stalls, HDP coherency hangs, or incorrect virtual-function memory-size/function-identifier reporting.

## Open Questions for Merge

- The full-file report should reconcile this chunk with earlier VF0-VF12 and PF definitions to determine whether VF16-VF23 intentionally have fewer HDP coherency-only registers than VF12-VF15.
- The merge lane should note that this final chunk is a generated macro table and that direct consumers may be sparse even though the constants are part of the public internal driver register map.
