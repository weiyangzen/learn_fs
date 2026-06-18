# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h lines 7388-10021

## Scope

This chunk covers a generated AMD NBIF 6.3.1 register-offset header segment. It contains 2,366 preprocessor definitions: 1,183 register offset macros and 1,183 matching `*_BASE_IDX` macros. The file has no executable functions or data structures in this range; its API surface is the macro namespace consumed by AMDGPU and display register access helpers.

The chunk starts in the middle of a BIFC/NBIF register block, then covers whole address blocks for BIF RAS, RCC, BIF BX, GDC, Syshub, and SR-IOV virtual-function register windows through part of VF12. Each register macro gives a register-relative offset, while the companion `*_BASE_IDX` macro selects the base segment used by SOC15/DC address calculation.

## Purpose

The purpose of this header segment is to provide compile-time register addresses for NBIF/NBIO-facing driver code on ASICs using the NBIF 6.3.1 register map. Callers combine these offsets with per-IP base arrays to compute MMIO addresses for PCIe/NBIF configuration, doorbell routing, HDP flush control, RAS status, performance counters, link/strap state, GDC doorbell translation, MSI-X tables, and SR-IOV virtual-function control surfaces.

This chunk is especially important for:

- global BIFC/NBIF control and diagnostics such as performance counters, PASID error logging, power-gating controls, virtual-wire controls, SMN/SDP controls, timeout detection, pool credit allocation, and A2S controls;
- RAS surfaces under `nbif_bif_ras_bif_ras_regblk`;
- RCC downstream, downstream-port, endpoint, strap, and device blocks;
- BIF BX system and PF/PF-VF decode blocks;
- GDC DMA/HST/S2A/A2S doorbell and system-interconnect decode registers;
- virtual-function register templates for `DEV0_EPF0_VF0` through `DEV0_EPF0_VF11`, plus the beginning of `VF12`.

## Macro Families And Address Blocks

Important block inventory in this chunk:

- Lines 7388-7541: tail of a BIFC/NBIF block at base-index 5, including `regBIFC_PERF_CNTL_1`, low/high MMIO and DMA performance counters, `regNBIF_REGIF_ERRSET_CTRL`, `regBIFC_SDP_CNTL_*`, `regNBIF_PGMST_CTRL`, `regNBIF_PGSLV_CTRL`, `regNBIF_PG_MISC_CTRL`, SMN master endpoint controls, selfring vector controls, strap write controls, INTx/D-state pending controls, GMI WRR weights, atomic/PASID error logs, virtual-wire controls, LCLK clock/power controls, SHUB timeout detection, credit allocation, and A2S tag/control registers.
- Lines 7543-7570: `nbif_bif_ras_bif_ras_regblk` at base address `0x10100000`, with central/leaf RAS control and status registers plus IOHUB RAS interrupt/virtual-wire hooks.
- Lines 7571-7774: RCC downstream, downstream-port, endpoint, and device blocks at base address `0x10120000`, including PCIe scratch/control, miscellaneous memory power controls, endpoint PCIe transmit/LTR controls, link feature capability, secondary bus/security state, BAR controls, ATR translation, ROM/BIOS offset controls, SMN base addresses, requester ID mappings, subsystem IDs, configuration memory size, doorbell aperture enable, and IOV function identifier registers.
- Lines 7775-7964: `nbif_bif_bx_SYSDEC`, including root `MM_INDEX/MM_DATA`, RSMU index/data, indirect PCIE index/data, scratch, clock gating, interrupt and retry controls, HDP flush and invalidate controls, BIU/BIF interrupt handling, error logging, decode timer, CBB request attributes, BIF FB enable, power-control, remap controls, and BME/doorbell interrupt signals.
- Lines 7965-8140: physical-function system and BIF PF/PF-VF decode registers, including `regBIF_BX_PF0_*` doorbell selfring aperture, coherency flush, GPU HDP flush request/done, transaction pending, mailbox message buffers, and mailbox interrupt controls.
- Lines 8141-8234: RCC strap registers, including BIF strap groups, device/function strap sets, subvendor/subsystem IDs, port link controls, HDP clocks, and IOAPIC ID.
- Lines 8235-8616: GDC decode windows at base address `0x1400000`, including DMA SION, HST SION, GDC control/status, GDC RAS central/leaf controls, reset scratch/status, S2A doorbell entries, and A2S controls.
- Lines 8617-8630: Syshub direct MMIO registers for GART aperture high/low, dummy page, and system aperture default address.
- Lines 8631-10021: repeated SR-IOV VF blocks for `DEV0_EPF0_VF0` through `DEV0_EPF0_VF11`, plus the initial `BIFPFVFDEC1` surface for `VF12`. Each full VF template provides BIF BME status, atomic error log, doorbell selfring aperture base/control, HDP coherency flush/invalidate controls, GPU HDP flush request/done, transaction pending, mailbox transmit/receive buffers, mailbox controls, `MM_INDEX/MM_DATA/MM_INDEX_HI`, RCC error/doorbell/config/IOV identifiers, and four GFX MSI-X vector entries plus pending-bit array.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or runtime objects in this chunk. The important API is the macro contract:

- `reg<NAME>` macros map a symbolic hardware register name to a numeric register offset.
- `reg<NAME>_BASE_IDX` macros map the same symbolic register to a base table index.
- Consumers pass these macros to register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `WREG32_FIELD15_PREREG`, and display resource macros that calculate `BASE(reg..._BASE_IDX) + reg...`.

The companion bitfield header `nbif_6_3_1_sh_mask.h` supplies masks and shifts for many registers named here. This offset header alone intentionally does not define bit layout; it only locates the registers.

## Control Flow

This chunk has no runtime control flow. Its compile-time control flow is macro expansion:

1. A consumer includes `nbif/nbif_6_3_1_offset.h`.
2. The consumer names a register macro in a SOC15/DC helper.
3. The helper uses the register offset and `*_BASE_IDX` to select the proper base from the NBIO/NBIF base-address table.
4. The resulting MMIO address is used for register reads, writes, field updates, or storage in hardware register tables.

The direct include sites found in this source tree are `drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c` and `drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`. The AMDGPU NBIF implementation uses these offsets to program doorbells, HDP flush paths, memory-controller access, revision/config straps, interrupts, and low-power PCIe/NBIF controls. The DCN401 resource code includes the header so display register-table construction can resolve NBIF register addresses through its `SR`, `SRI`, and related register-list macros.

## State And Persistence Behavior

The header itself stores no mutable state and persists nothing. It describes persistent hardware register locations. Driver writes through these offsets can change durable device state until reset, power transition, or later driver reprogramming. In this chunk, state-sensitive register groups include:

- performance counter control/value registers and common count enable state;
- error log and clear registers for atomic, DMA, PASID, BME, RCC, GDC, and RAS paths;
- strap and configuration registers that expose or influence device identity and link behavior;
- doorbell aperture, selfring, GDC S2A/A2S, and MSI-X registers that affect interrupt and work-submission routing;
- HDP coherency flush/invalidate and transaction-pending state used around GPU/CPU memory visibility;
- virtual-function mailbox, MSI-X, BME, and doorbell windows used by SR-IOV isolation.

Because all values are hard-coded constants, the source of truth is the generated ASIC register specification. Any mismatch between the header and hardware silently redirects MMIO access to the wrong address.

## Dependencies And Integration Points

This chunk depends on the broader AMD register-access infrastructure rather than normal library calls:

- `amdgpu` SOC15 helpers use `reg...` plus `reg..._BASE_IDX` to calculate NBIO/NBIF MMIO offsets.
- `nbif_6_3_1_sh_mask.h` supplies field masks and shifts for the same register names.
- `pcie_6_1_0_offset.h` and related PCIE masks are used beside this header in `nbif_v6_3_1.c` for link-control programming.
- DC resource code uses `ctx->dcn_reg_offsets` and register-list expansion macros to convert offset/header symbols into display engine register tables.
- SR-IOV and virtualization code can rely on the repeated VF macro names to access per-VF BIF/RCC/MSI-X/mailbox/HDP surfaces.
- RAS, interrupt, doorbell, KFD/HSA, and memory-controller flows depend on the specific addresses represented by the BIFC, BIF BX, RCC, and GDC macro groups.

The `*_BASE_IDX` values are part of the ABI between this generated header and the base-address table for the ASIC. In this chunk, commonly visible base selectors include 5 for many global NBIF/RCC/BIFC blocks, 2 for PF/VF BIF and RCC PF-VF decode windows, 3 for MSI-X/GDC-style decode windows, and 0 for indirect `MM_INDEX/MM_DATA` windows.

## Risks

- Wrong offset or base-index constants can cause the driver to read or write an unrelated hardware register, which may break boot, display bring-up, doorbells, PCIe behavior, interrupt routing, or virtualization isolation.
- The repeated VF blocks are mechanically similar; copy-generation mistakes may affect only one VF and can be hard to catch without SR-IOV coverage across all exposed VFs.
- The chunk ends inside the VF12 sequence, so whole-file analysis must merge with the next chunk before drawing conclusions about complete VF12 and later VF coverage.
- Several registers are write-sensitive, including clears, strap writes, aperture controls, flush/invalidate controls, and interrupt controls. A valid address with an invalid field value can still create hardware hangs or lost interrupts.
- Base-index mismatches are as risky as offset mismatches because the same small offsets are reused under different decode windows.
- Some direct use sites include ASIC-version exceptions, such as local replacement offsets in `nbif_v6_3_1.c` for IP version `7.11.4`; generated constants may need hardware-family-specific overrides when the register map diverges.

## Test Signals

Useful signals for validating this chunk are mostly build-time and hardware-integration signals:

- Successful compilation of consumers including `nbif_v6_3_1_offset.h`, especially `amdgpu/nbif_v6_3_1.c` and `display/dc/resource/dcn401/dcn401_resource.c`.
- No undefined `reg...` or `reg..._BASE_IDX` symbols when NBIF 6.3.1 and DCN401 code paths are enabled.
- Register smoke tests on matching hardware that verify NBIF revision/config reads, memory size reads, MC access enable/disable, HDP flush request/done offsets, RSMU indirect register offsets, and PCIe low-power control paths.
- Doorbell tests for SDMA, VCN, IH, GC, selfring, and KFD paths, since this chunk includes the GDC S2A and BIF doorbell aperture definitions used by NBIF setup.
- SR-IOV tests that exercise VF0-VF12 mailbox, MSI-X, BME, HDP flush, and doorbell aperture registers, with attention to per-VF isolation.
- RAS/error-injection or diagnostic tests that confirm BIFL/GDC/RCC/BIF atomic and PASID error log offsets map to expected status and clear behavior.
- Cross-checking this generated header against the authoritative AMD register database for NBIF 6.3.1, including both offset values and base-index values.

## Chunk Notes For Merge

This chunk is a partial view of `nbif_6_3_1_offset.h`. It should be merged with earlier and later chunk reports before producing the final per-file research document. The final file report should treat this range as the late global NBIF/RCC/GDC block plus the first large run of SR-IOV VF register templates, and should reconcile the incomplete start and end boundaries with adjacent chunks.
