# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 7346-9406

## Scope

This chunk is the tail of AMDGPU's generated NBIO 7.11.0 register-offset header. It contains 1,891 preprocessor definitions: 948 register-address macros and 943 companion `_BASE_IDX` macros. There are no functions, structs, typedefs, enums, variables, locks, allocations, or executable statements.

The range starts in the middle of the `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC` address block with endpoint PCIe control/status offsets for `regRCC_EP_DEV0_0_*`. It then covers RCC downstream/downstream-port/endpoint windows for devices 1 and 2, internal strap registers, BIF reset and miscellaneous blocks, SION scheduling offsets, BIF RAS offsets, BIFDEC1 and BIFPFVFDEC1 views for `BIF_BX0`, `BIF_BX1`, and `BIF_BX2`, GDC doorbell blocks, and finally closes the header with `#endif`.

## Purpose

`nbio_7_11_0_offset.h` provides symbolic register addresses for the NBIO 7.11 hardware block used by AMDGPU and display code. This line range describes the lower-level PCIe/NBIO address map for reset, function-level reset, D-state and D3hot/D0 reset tracking, interrupt routing, DMA attribute override, NBIF performance counters, SION credit/scheduling registers, RAS status/control, BIF_BX system and PF/VF windows, HDP coherency flush registers, GPU address LUTs, mailbox buffers, doorbell aperture controls, and per-engine doorbell range registers.

The macros are not a standalone API. They are the address half of a generated register interface. Callers pair these `reg...` offsets and `_BASE_IDX` values with sibling shift/mask definitions from `nbio_7_11_0_sh_mask.h`, AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and display register-list expansion macros that add `ctx->nbio_reg_offsets[base_idx]`.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro convention:

- `reg<REGISTER_NAME>`: a register offset or encoded address used by SOC15/NBIO access helpers.
- `reg<REGISTER_NAME>_BASE_IDX`: an index into the relevant NBIO base-address table. Most macros in this chunk use base index `5`; some BIF/GDC windows use indices `0`, `2`, or `3`.

Major macro families in this chunk are:

- `regRCC_EP_DEV0_0_*`, `regRCC_EP_DEV1_*`, and `regRCC_EP_DEV2_*`: endpoint PCIe scratch, control, interrupt, RX/TX, bus/config, LTR, PME, error-control, link-speed, and Dynamic Power Allocation offsets. DEV1 and DEV2 include repeated F0 DPA capability, latency indicator, control, and substate power allocation offsets.
- `regRCC_DWN_DEV*_*` and `regRCC_DWNP_DEV*_*`: downstream and downstream-port PCIe reserved/scratch/control/config/RX/bus/Cfg offsets plus downstream-port error, RX, link-speed, link-control, and LTR-message offsets.
- `regRCC_STRAP*` and `regRCC_DEV0_EPF*`: strap and endpoint-function offsets, including doorbell aperture enable and configured memory size registers. These are used by NBIO setup to read revision IDs, memory size, and doorbell aperture state.
- `regHARD_RST_CTRL`, `regSELF_SOFT_RST*`, `regBIF_RST_MISC_CTRL*`, `regDEV*_PF*_FLR_RST_CTRL`, `regBIF_*_INTR_STS`, `regBIF_*_INTR_MASK`, `regBIF_PF_FLR_RST`, `regBIF_DEV*_PF*_DSTATE_VALUE`, and `regDEV*_PF*_D3HOTD0_RST_CTRL`: reset, function-level reset, D-state, D3hot/D0, and reset interrupt surfaces for devices 0, 1, and 2.
- `regMISC_SCRATCH`, `regINTR_LINE_*`, `regOUTSTANDING_VC_ALLOC`, and the `regBIFC_*` family: miscellaneous BIF control, BME error logging, per-device DMA attribute overrides, PASID status/control, SDP controls, ATHUB action control, performance counter controls and low/high counter pieces, page-gating controls, SMN master controls, SDP voltage-change reset controls, SHUB timeout detection controls, pool-credit allocation, Z10 state, BDF control, early wakeup, and common-count status.
- `regSION_CL[0-2]_*` and `regSION_CNTL_REG*`: SION client scheduling and credit allocation offsets for read response, write response, request, data, and pool-credit registers.
- `regBIFL_RAS_*`: BIF leaf/central RAS control and status offsets plus IOHUB RAS interrupt/control and VWR-from-IOHUB offsets.
- `regBIF_BX0_*`, `regBIF_BX1_*`, and `regBIF_BX2_*`: BIF_BX system windows for PCIe indirect index/data, SBIOS/BIOS scratch registers, RLC/VCE/UVD interrupt controls, GFX MMIO CAM remap entries, reset controls, interrupt controls, doorbell controls, frame-buffer enables, transaction-pending status, BACO controls and exit timers, memory type control, NBIF GFX address LUT entries 0-15, GFX reset control, HDP remap flush controls, BIF ring-buffer pointers, mailbox index, GPUIOV config size, and pad controls.
- `regBIF_BX_PF0_*`, `regBIF_BX_PF1_*`, and `regBIF_BX_PF2_*`: PF/VF-facing BIF BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate controls, GPU HDP flush request/done registers, transaction-pending status, address-LUT bypass, mailbox transmit/receive dwords, mailbox control/interrupt, and VM/HV mailbox offsets.
- `regGDC0_*`, `regGDC1_*`, and `regGDC2_*`: GDC doorbell and queue-control offsets, including A2S queue FIFO arbitration, NBIF GFX doorbell status, SDMA/IH/VCN/RLC/CSDMA/VPE doorbell ranges, ATDMA misc control, and doorbell fence control. GDC0 additionally has `VPE1` and `S2A_MISC_CNTL` entries, while the tail-end GDC2 block ends at `regGDC2_BIF_DOORBELL_FENCE_CNTL`.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior is created by code that includes it and uses the offsets to access hardware registers.

Observed direct integration includes `amdgpu/nbio_v7_11.c`, which includes this offset header and the matching shift/mask header. That file uses offsets from this range to remap HDP flush registers, read the revision strap, enable/disable frame-buffer access, read configured memory size, program CSDMA/VPE/VCN/IH doorbell ranges, enable the doorbell aperture and self-ring aperture, program interrupt control, and return HDP flush and PCIe index/data offsets to generic AMDGPU code.

Display resource files for DCN 3.5 and DCN 3.5.1 also include this header. Their NBIO register-list macros expand selected `regBIF_BX1_BIOS_SCRATCH_*` offsets with `ctx->nbio_reg_offsets[...]` to populate BIOS scratch register tables used by display resource initialization.

The implied external flows are:

1. NBIO initialization selects a generated register macro and adds the corresponding base-index entry through `SOC15_REG_OFFSET` or display `NBIO_BASE`.
2. Driver code reads, writes, or read-modify-writes the hardware register using the computed address and field definitions from `nbio_7_11_0_sh_mask.h`.
3. Hardware performs the requested operation: reset sequencing, FLR/D-state transition observation, doorbell range routing, interrupt delivery, HDP flush synchronization, mailbox exchange, address-LUT translation, RAS reporting, SION credit scheduling, or PCIe indirect access.
4. Status and done registers are polled or sampled by higher-level AMDGPU paths; this header only names those registers and does not encode ordering, timeout, clear-on-write, or ownership rules.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state in NBIO 7.11 registers.

The represented state includes PCIe endpoint/downstream control, LTR and PME state, DPA state, reset and FLR command/status state, D-state and D3hot/D0 transition state, interrupt masks/status, BIF miscellaneous controls, BME and atomic error logs, DMA/PASID/SDP attributes, performance counters, page-gating and low-power controls, SION traffic scheduling and credit allocation, BIF RAS central/leaf controls and status, BIOS/SBIOS scratch registers, MMIO CAM remap state, doorbell aperture/range state, HDP coherency flush request/done state, BIF transaction-pending status, BACO controls and timers, NBIF GFX address LUTs, mailbox buffers, and pad controls.

Persistence across GPU reset, PCIe hot reset, FLR, BACO, suspend/resume, runtime power transitions, or firmware handoff is not specified here. Some scratch and strap registers may be firmware- or boot-initialized, and some status registers may be sticky or clear-on-write, but those semantics must come from hardware documentation and the matching shift/mask/default/access metadata.

## Dependencies And Integration Points

Primary source dependencies are the adjacent generated NBIO 7.11 headers:

- `nbio_7_11_0_sh_mask.h` for bit positions and masks inside the registers named here.
- Any generated default or SMN metadata for NBIO 7.11 where present in the same ASIC register tree.
- SOC15 register access infrastructure that interprets `_BASE_IDX` values and adds the correct per-IP base address.

Important integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, the direct NBIO 7.11 consumer for HDP remap, revision strap, memory size, doorbells, interrupt setup, PCIe indirect offsets, and doorbell apertures.
- AMDGPU doorbell allocation and per-engine setup for SDMA, CSDMA, VPE, VCN, IH, RLC, and other engines routed through GDC doorbell range registers.
- AMDGPU reset and power-management flows that may interact with BIF reset, FLR, D-state, D3hot/D0, BACO, page-gating, Z10, and early-wakeup registers.
- HDP flush and coherency paths that use PF/VF BIF registers for GPU HDP flush request/done and remapped HDP flush controls.
- Display DCN 3.5/3.51 resource initialization, which uses NBIO BIOS scratch offsets via display register-list macros.
- Virtualization and firmware/hypervisor paths suggested by GPUIOV config-size registers, VM/HV mailbox registers, mailbox message buffers, BIF ring-buffer registers, and PF/VF-specific address windows.
- RAS and diagnostics paths for BIF leaf/central status, BME/atomic logs, performance counters, SION scheduling, and timeout/sync-flood controls.

## Risks And Edge Cases

- Generated address drift can compile cleanly while sending reads or writes to the wrong NBIO register. In this chunk that can break doorbell routing, HDP flush completion, reset handling, display BIOS scratch reads, RAS reporting, or virtualization mailbox traffic.
- The same logical register families appear through multiple address windows: `BIF_BX0`, `BIF_BX1`, and `BIF_BX2`; PF0/PF1/PF2; GDC0/GDC1/GDC2; and RCC device/function variants. Using the wrong instance can affect a different BIF, PF/VF, or doorbell aperture than intended.
- `_BASE_IDX` values are part of the ABI with SOC15 base tables. A correct offset with the wrong base index is still a bad final address.
- Several register names are intentionally aliased to the same offset, especially DPA capability/control/substate fields. Callers must use the matching shift/mask fields and avoid assuming one macro name means a unique 32-bit location.
- Reset, FLR, D-state, D3hot/D0, BACO, and page-gating registers interact with live hardware state machines. Bad ordering or missing polling can leave the GPU partially reset, power-gated, or inaccessible.
- Doorbell aperture and doorbell range programming affects command submission and interrupt delivery. A wrong offset, size, or engine instance can cause lost work submissions, spurious interrupts, or writes into the wrong doorbell range.
- HDP flush request/done and coherency-flush registers are synchronization points. Misaddressing them can cause stale CPU/GPU-visible memory or hangs in code waiting for completion.
- Mailbox and VM/HV registers imply firmware or hypervisor ownership. Writes without ownership coordination can corrupt messages or interfere with virtualization flows.
- The chunk starts in the middle of an RCC endpoint block inherited from prior lines, so whole-file reconciliation should combine this with the preceding chunk before treating the DEV0_0 endpoint family as complete.

## Test Signals

Useful validation combines generated-header checks with hardware-oriented AMDGPU coverage:

- Build AMDGPU configurations that include NBIO 7.11 and DCN 3.5/3.51 support to catch missing, renamed, or malformed macros.
- Run generated-header consistency checks to ensure each register macro has the expected `_BASE_IDX` companion, repeated device/PF/GDC families have coherent offsets, and all references in `nbio_v7_11.c` and DCN resource files resolve.
- Cross-check final computed addresses from `SOC15_REG_OFFSET(NBIO, 0, reg...)` against the ASIC register database for representative RCC, BIF reset/misc, BIF_BX, PF/VF, and GDC entries.
- On NBIO 7.11 hardware, validate doorbell setup for CSDMA, VPE, VCN, IH, SDMA, RLC, and related engines by confirming command submission, interrupts, and doorbell status after programming the listed range registers.
- Validate HDP coherency by exercising GPU/CPU memory-visible operations that require HDP flush request/done registers and remapped HDP flush controls.
- Exercise reset, FLR, D-state, D3hot/D0, suspend/resume, BACO, and runtime power paths while checking the related BIF status/mask/control registers for expected transitions and recovery.
- Confirm display initialization on DCN 3.5/3.51 ASICs can read expected BIOS scratch values through the `regBIF_BX1_BIOS_SCRATCH_3` and `regBIF_BX1_BIOS_SCRATCH_6` paths.
- For RAS and diagnostics, sample BIF RAS central/leaf status, BME/atomic logs, performance counters, and transaction-pending status before and after controlled events where platform validation permits.

## Chunk Boundary Notes

This is the final chunk of `nbio_7_11_0_offset.h`: line 9406 is the closing `#endif`. The range begins after the start of `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`, so the initial `regRCC_EP_DEV0_0_*` macros here are a continuation of a logical address block that starts in the previous chunk. Merge/reconciliation should join that preceding endpoint context with this tail section.
