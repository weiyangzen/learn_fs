# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 4945-7706

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-offset header segment. It contains preprocessor constants only: 1,181 register offset macros and 1,181 matching `_BASE_IDX` macros for SR-IOV virtual-function register windows in `DEV0_EPF0`. There are no C functions, structs, enums, or executable control flow in the chunk.

The line range starts in the middle of VF1's BIF PF/VF decode block, contains VF1's MSI-X decode block, contains complete VF2 through VF25 register families, and ends in the early VF26 BIF PF/VF decode block before VF26's MSI-X block is complete.

## Purpose

The constants map NBIO/NBIF register names to SOC15 MMIO register offsets for Navi-era AMD GPUs using NBIO IP version 2.3. The register names describe the address block, PCIe endpoint/function, virtual-function number, and register role. Driver code includes this header to convert symbolic register names into numeric addresses through helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and the lower-level `RREG32_NO_KIQ()`/`WREG32_NO_KIQ()` mailbox accesses.

The chunk is specifically about SR-IOV virtual functions. The repeated `VF<n>` macro sets expose per-VF views of:

- indexed MMIO windows (`MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`);
- RCC PF/VF control/status registers (`RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`);
- BIF PF/VF status, atomics, doorbell self-ring aperture, HDP coherency flush, transaction-pending, address-LUT bypass, and VM/HV mailbox registers;
- MSI-X vector table and pending-bit-array offsets for four graphics MSI-X vectors.

## Important Macro Families

Each register is defined as a dword offset plus a matching base index. The offset names are not arrays; every VF instance is emitted as a separate macro.

The repeated complete VF2-VF25 layout is:

- `*_SYSPFVFDEC`: `MM_INDEX` at `0x0000`, `MM_DATA` at `0x0001`, and `MM_INDEX_HI` at `0x0006`, all with base index `0`.
- `RCC_*_BIFPFVFDEC1`: `RCC_ERR_LOG` at `0x0085`, `RCC_DOORBELL_APER_EN` at `0x00c0`, `RCC_CONFIG_MEMSIZE` at `0x00c3`, `RCC_CONFIG_RESERVED` at `0x00c4`, and `RCC_IOV_FUNC_IDENTIFIER` at `0x00c5`, all with base index `2`.
- `BIF_BX_*_BIFPFVFDEC1`: `BIF_BME_STATUS` at `0x00eb`, `BIF_ATOMIC_ERR_LOG` at `0x00ec`, doorbell self-ring base/control registers at `0x00f3`-`0x00f5`, HDP coherency flush control at `0x00f6`-`0x00f7`, GPU HDP flush request/done at `0x0106`-`0x0107`, `BIF_TRANS_PENDING` at `0x0108`, `NBIF_GFX_ADDR_LUT_BYPASS` at `0x0112`, mailbox transmit/receive dwords and control/interrupt registers at `0x0136`-`0x0140`, all with base index `2`.
- `RCC_*_BIFDEC2`: four MSI-X vector entries, each with low address, high address, message data, and control registers at `0x0400`-`0x040f`, plus `GFXMSIX_PBA` at `0x0800`, all with base index `3`.

The partial boundaries matter:

- Lines 4945-4985 are the tail of `VF1_BIFPFVFDEC1`, beginning after the VF1 `BIF_ATOMIC_ERR_LOG` offset and covering doorbell self-ring, HDP flush, transaction pending, address LUT bypass, mailbox, and VM/HV mailbox macros.
- Lines 4988-5021 cover `VF1_BIFDEC2` MSI-X vector and PBA macros.
- Lines 7666-7706 cover `VF26_SYSPFVFDEC`, `VF26_RCC_BIFPFVFDEC1`, and the first eight VF26 `BIF_BX_*_BIFPFVFDEC1` register offsets through `HDP_MEM_COHERENCY_FLUSH_CNTL`; the remaining VF26 registers continue after this chunk.

## Control Flow

There is no runtime control flow in this header. Runtime behavior appears in include consumers:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this header with the matching `nbio_2_3_sh_mask.h` masks. It programs PF-facing NBIO registers for memory-controller access, doorbell aperture enablement, doorbell ranges, HDP flush offsets, interrupt control, ASPM/LTR settings, and register remapping.
- `nbio_v2_3_set_reg_remap()` uses `mmBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` as the SR-IOV VF fallback remap anchor. This chunk does not contain VF0, but its VF1-VF26 HDP-flush constants follow the same generated layout.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header and uses mailbox registers (`mmMAILBOX_MSGBUF_*` aliases from the same generated register map) to exchange VF/PF messages, poll acknowledgements, and handle GPU access requests.
- SMU Navi10/Sienna Cichlid PPT code includes the header for NBIO register definitions, though this chunk's per-VF macro names are not directly referenced in the inspected SMU source.

## State and Persistence

The header itself stores no state. The macros address persistent hardware register state in the NBIO block:

- Doorbell aperture and self-ring registers persist hardware aperture base/control programming until reset or reprogramming.
- HDP coherency flush request/done and HDP flush-control registers represent hardware synchronization state used to make host/device memory ordering visible.
- `BIF_TRANS_PENDING`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, and `RCC_ERR_LOG` expose live bus/device status or diagnostic state.
- Mailbox transmit/receive dwords and control bits are transient PF/VF communication state. In `mxgpu_nv.c`, software explicitly clears valid bits, writes transmit dwords, polls ACK bits, and reads receive dwords.
- MSI-X vector address/data/control and PBA registers persist interrupt-routing configuration for each VF until changed by the OS, hypervisor, or device reset.

Because these are register offsets, the persistence boundary is hardware/firmware state rather than kernel memory. Incorrect constants can persistently program the wrong register until the affected GPU function is reset.

## Dependencies

This file depends on the SOC15 register-access model used by AMDGPU:

- `SOC15_REG_OFFSET(hwip, inst, reg)` combines the macro's dword offset with IP discovery base data and the associated `_BASE_IDX`.
- `RREG32_SOC15()` and `WREG32_SOC15()` use those offsets for normal MMIO register reads/writes.
- `nbio_2_3_sh_mask.h` provides the bit masks and shifts for fields within the registers defined here.
- `nbio_2_3_default.h` provides reset/default values for the same IP generation.
- The generated macro names must remain synchronized with the ASIC register database, firmware expectations, and virtualization model for NBIO 2.3.

## Integration Points

The main integration surface is the AMDGPU NBIO layer:

- `amdgpu_nbio_funcs` in `nbio_v2_3.c` publishes callbacks for HDP flush offsets, doorbell programming, interrupt setup, clock-gating state, ASPM handling, and remapping. These callbacks rely on this header's offsets to reach the correct NBIO registers.
- The SR-IOV path uses VF-specific windows to avoid direct PF-only register access from guest contexts. `nbio_v2_3_get_rev_id()` explicitly returns a safe rev ID for VFs because a guest reading a PF strap register can see `0xffffffff`.
- The MxGPU mailbox path uses NBIO mailbox registers as the synchronization channel between a guest VF and PF/hypervisor services for GPU init/fini/reset access, RAS requests, and error notification.
- The MSI-X offsets integrate with PCI interrupt routing for virtual functions: vector table registers at `0x0400`-`0x040f` and PBA at `0x0800` describe the per-VF interrupt-programming surface.

## Risks

- Generated-offset drift: these constants are hardware contracts. A wrong dword offset or `_BASE_IDX` can make the driver read/write a different NBIO register, which can break SR-IOV isolation, doorbell routing, HDP coherency, interrupts, or VF/PF mailbox handshakes.
- Boundary errors in chunking: this work item begins and ends inside larger generated VF blocks. Any merge/reconciliation step must combine adjacent chunks before drawing per-file conclusions about complete VF1 or VF26 coverage.
- Copy/paste pattern risk: the VF2-VF25 blocks are highly repetitive. A single malformed VF number, endpoint/function prefix, or base index can be hard to spot by inspection and would not necessarily be caught by C compilation if the macro is unused.
- Sparse direct references: many generated per-VF macros may not be referenced by current source, but they are still ABI-like register definitions for debug, future enablement, or indirect access. Removing apparently unused macros can break out-of-tree tooling or future ASIC paths.
- Virtualization sensitivity: mailbox and doorbell registers participate in PF/VF trust boundaries. Misprogrammed apertures or mailbox control bits can cause denial of service, stuck access requests, lost reset coordination, or writes outside the intended VF aperture.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/runtime oriented:

- Compile coverage: AMDGPU builds that include `nbio_v2_3.c`, `mxgpu_nv.c`, and Navi/Sienna SMU PPT files should compile without undefined NBIO 2.3 macros.
- Generated-header consistency checks: compare VF2-VF25 blocks for identical offsets/base indices modulo the VF number, and compare VF1/VF26 fragments against neighboring chunks to ensure no missing or duplicated register definitions.
- SR-IOV smoke tests: VF probe, GPU init/fini/reset access requests, and PF/VF mailbox ACK/valid polling should complete without timeouts or unrecoverable-state notifications.
- Doorbell tests: SDMA/IH/VCN doorbell programming and ring submission should succeed for PF and VF modes, with no doorbell interrupt status left uncleared.
- HDP coherency tests: command submission paths that request HDP flushes should observe matching flush-done bits and no stale memory visibility across CPU/GPU boundaries.
- Interrupt tests: MSI-X interrupt delivery for VF graphics vectors should work after vector address/data/control programming, and PBA status should reflect pending interrupts correctly.
