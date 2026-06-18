# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h lines 2440-4631

## Scope

This chunk is the final generated offset slice of AMDGPU's NBIO 7.4 register header. It contains preprocessor constants only: 943 register/config offset macros and 937 matching `_BASE_IDX` macros, plus address-block comments and the closing `#endif`. There are no C functions, structs, enums, variables, allocations, locks, loops, or executable statements.

The range starts in the tail of the `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` PCIe configuration-space table with ATS and ARI capability offsets, then switches to MMIO-style `mm...` register offsets for NBIF/BIF/RCC/GDC blocks. The largest portion is a mechanically repeated SR-IOV virtual-function map for `DEV0_EPF0_VF0` through `DEV0_EPF0_VF15`. Because the start point is artificial, the full VF15 PCIe config-space capability map is split with the preceding chunk.

## Purpose

`nbio_7_4_offset.h` publishes generated register and PCI configuration offsets for the NBIO 7.4 block. This chunk gives AMDGPU code symbolic names for NBIF indirect access registers, PCIe/BIF control registers, register-config controller state, doorbell and coherency registers, mailbox registers, GDC doorbell ranges, MSI-X tables, and per-virtual-function BIF/RCC windows.

Each non-`_BASE_IDX` macro names an offset, usually a dword register index such as `mmPCIE_INDEX 0x000c`, `mmRCC_ERR_INT_CNTL 0x0086`, or `mmGFXMSIX_VECT0_ADDR_LO 0x0400`. Each `_BASE_IDX` macro selects the generated address-base slot used by AMDGPU register helpers. The header does not describe bit fields, reset values, access permissions, ordering rules, or side effects; those are provided by companion generated headers and hardware documentation.

Although this repository path is under a `ceph-client` source mirror, the contents are AMDGPU hardware metadata and have no direct distributed-filesystem behavior.

## Important Macro Families

The chunk covers these generated address-block groups:

- Tail PCIe VF15 config offsets: `cfgBIF_CFG_DEV0_EPF0_VF15_0_PCIE_ATS_*` and `cfgBIF_CFG_DEV0_EPF0_VF15_0_PCIE_ARI_*` expose Address Translation Services and Alternative Routing-ID Interpretation capability offsets for the final virtual function's PCI config-space template.
- System/PF-VF indirect access: `mmMM_INDEX`, `mmMM_DATA`, `mmMM_INDEX_HI`, `mmSYSHUB_INDEX_OVLP`, `mmSYSHUB_DATA_OVLP`, `mmPCIE_INDEX`, `mmPCIE_DATA`, `mmPCIE_INDEX2`, and `mmPCIE_DATA2` provide indirect register portals into MM, SYSHUB, and PCIe spaces.
- BIOS and interrupt scratch/control registers: `mmSBIOS_SCRATCH_*`, `mmBIOS_SCRATCH_*`, `mmBIF_RLC_INTR_CNTL`, `mmBIF_VCE_INTR_CNTL`, and `mmBIF_UVD_INTR_CNTL` define firmware scratch locations and legacy engine interrupt controls.
- GFX MMIO remap CAM registers: `mmGFX_MMIOREG_CAM_ADDR0..7`, corresponding `REMAP_ADDR0..7`, `mmGFX_MMIOREG_CAM_CNTL`, and completion-value registers describe the address-remap CAM aperture used by BIF for GPU MMIO access.
- RCC and endpoint/downstream PCIe control blocks: `mmEP_PCIE_*`, `mmDN_PCIE_*`, `mmPCIE_ERR_CNTL`, `mmPCIE_RX_CNTL`, `mmPCIE_LC_SPEED_CNTL`, `mmPCIE_LC_CNTL2`, and `mmLTR_MSG_INFO_FROM_EP` cover endpoint/downstream PCIe control, link-speed, error, and latency-tolerance reporting registers.
- PF BIF/RCC virtualization support: `mmRCC_ERR_LOG`, `mmRCC_DOORBELL_APER_EN`, `mmRCC_CONFIG_MEMSIZE`, `mmRCC_IOV_FUNC_IDENTIFIER`, bus-number capture/list registers, peer FB offset registers, XDMA address registers, and common link/LTR registers support function identity, aperture sizing, peer access, and virtualization control.
- BIF core registers: `mmBIF_MM_INDACCESS_CNTL`, `mmBUS_CNTL`, `mmBIF_SCRATCH*`, `mmBX_RESET_EN`, `mmMM_CFGREGS_CNTL`, `mmBIF_FB_EN`, `mmBIF_FB_RPTR/BASE/END`, BACO entry/exit timers, memory-type control, NBIF GFX address LUT entries, HDP coherency-remap flush controls, ring-buffer registers, mailbox index, MP1 interrupt control, GPUIOV config sizes, and PCIe pad controls.
- PF/VF BIFPFVF registers: the PF aliases and each VF block expose BME status, atomic error log, doorbell GPA aperture base/control, HDP register/memory coherency flush controls, GPU HDP flush request/done, transaction-pending state, NBIF GFX address LUT bypass, mailbox transmit/receive dwords, mailbox control/interrupt control, and VM-HV mailbox.
- GDC registers: `mmNGDC_SDP_PORT_CTRL`, `mmSHUB_REGS_IF_CTL`, `mmNGDC_MGCG_CTRL`, `mmBIF_*_DOORBELL_RANGE`, `mmBIF_DOORBELL_FENCE_CNTL`, and `mmS2A_MISC_CNTL` define global data/doorbell configuration and clock-gating related offsets.
- MSI-X tables: `mmGFXMSIX_VECT0..2_*` and `mmGFXMSIX_PBA` exist for the PF and for every VF0-VF15 block. Each vector has address low/high, message data, and control offsets.

The VF blocks repeat a stable four-block pattern for each virtual function:

1. `*_SYSPFVFDEC`: per-VF indirect MM index/data/index-high registers.
2. `*_BIFPFVFDEC1` under `rcc`: per-VF RCC error log, doorbell aperture enable, memory-size/config reserved, and IOV function identifier.
3. `*_BIFPFVFDEC1` under `bif_bx`: per-VF BME/error, doorbell GPA aperture, HDP coherency flush, transaction state, address-LUT bypass, and mailbox registers.
4. `*_BIFDEC2`: per-VF GFX MSI-X vector table and pending-bit-array offsets.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `cfg...` macros name PCI configuration-space offsets for VF config capability registers.
- `mm...` macros name NBIO/NBIF MMIO register offsets.
- `*_BASE_IDX` macros select the register base index expected by SOC15/NBIO access helpers.

Runtime consumers combine these offsets with `nbio_7_4_sh_mask.h` field masks and AMDGPU access helpers such as `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, indirect-index accessors, or PCI configuration access paths. This header alone does not make an access safe or meaningful.

## Control Flow

The chunk has no local runtime control flow. Effective use is external and follows the generated-register pattern:

1. Driver code includes `nbio_7_4_offset.h` for an NBIO 7.4 ASIC.
2. A call site chooses a symbolic offset and its base index, often together with field definitions from `nbio_7_4_sh_mask.h`.
3. The call site reads, writes, polls, or updates the hardware register through the relevant AMDGPU MMIO, SOC15, indirect MM, PCIe indirect, or PCI config-space helper.
4. Hardware state changes outside this header: link control, interrupt delivery, doorbell routing, HDP flush completion, mailbox exchange, SR-IOV VF behavior, BACO timing, or MSI-X interrupt delivery.

The repeated VF register maps imply external control flows for SR-IOV setup and teardown: PF code can size and enable VF apertures, assign or inspect per-VF identity, route per-VF doorbells, flush per-VF HDP state, exchange mailbox messages with a hypervisor or guest function, and configure MSI-X vectors.

## State And Persistence Behavior

The header owns no memory and persists nothing. It describes offsets for hardware-visible state in the GPU's NBIO/NBIF register space and PCI configuration-space templates.

Represented state includes firmware scratch registers, interrupt enables/status, PCIe link and error controls, LTR message state, function memory-size/aperture configuration, bus-number and peer-address mappings, BIF reset and FB aperture controls, BACO timing registers, address LUTs, HDP coherency flush request/done registers, ring-buffer pointers, per-engine GPUIOV config sizing, doorbell range/fence configuration, mailbox payload and interrupt registers, and MSI-X vector/PBA tables. Persistence of those values depends on GPU reset domains, PCIe reset, BACO/power transitions, firmware/BIOS programming, SR-IOV PF/VF lifecycle, suspend/resume restore, and explicit driver writes.

Some offsets identify status or handshake registers where values may be live, sticky, or side-effectful. The offset macros do not indicate whether reads clear status, writes are write-one-to-clear, fields are firmware-owned, or values survive reset.

## Dependencies And Integration Points

This chunk depends on the AMD generated register-header convention and must remain synchronized with:

- `nbio_7_4_sh_mask.h`, which supplies field shifts and masks for the same register names.
- `nbio_7_4_0_smn.h`, where applicable, for SMN address metadata outside this offset-only namespace.
- AMDGPU register helper infrastructure in the NBIO/SOC15/MMIO/PCIe paths.

Direct include users found in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, PSP files such as `psp_v11_0.c` and `psp_v12_0.c`, SMU/PowerPlay files such as `arcturus_ppt.c`, `aldebaran_ppt.c`, `smu_v13_0_6_ppt.c`, and `vega20_inc.h`, and DCN display files including DCN30 IRQ, GPIO, clock-manager, and resource code. These integrations connect the offsets to GPU reset, power management, display interrupt routing, firmware handoff, SR-IOV virtualization, mailbox communication, doorbell setup, PCIe link/error handling, and interrupt configuration.

The semantic dependencies are AMD's NBIO 7.4 register database and PCI/PCIe/SR-IOV/MSI-X conventions. The generated names encode hardware layout but do not enforce legal sequencing, ownership, or architectural constraints.

## Risks And Edge Cases

- Generated offset drift can compile cleanly while directing reads or writes at the wrong hardware register, causing failures in PCIe link management, doorbell routing, HDP flushing, SR-IOV isolation, mailbox communication, or MSI-X delivery.
- The chunk starts mid-VF15 PCI config-space map. The final per-file document must merge this with earlier chunks before treating VF15 ATS/ARI coverage as complete.
- Many PF and VF blocks share identical offsets with only prefix changes. Reviewers can miss generation errors because the repeated names differ mainly by `VF<N>`.
- The `mmRCC_IOV_FUNC_IDENTIFIER` definition is guarded by `#ifndef`, indicating possible cross-header duplicate names. Include order and duplicate definitions matter for generated ASIC headers.
- Offset macros do not encode side effects. Registers such as error logs, interrupt status/control, HDP flush request/done, transaction-pending state, mailbox control, and MSI-X vector control may require specific read/modify/write, polling, masking, or clearing sequences.
- Per-VF doorbell, mailbox, aperture, and MSI-X registers are isolation-sensitive. A wrong VF prefix or base index could leak interrupts, doorbells, or mailbox traffic across functions.
- Indirect access registers (`MM_INDEX/DATA`, `PCIE_INDEX/DATA`, and high/index2 variants) are sequencing-sensitive and can race with other users if access is not serialized by the caller.
- BACO timers, reset enables, pad controls, link controls, and clock-gating controls can affect low-power entry/exit, resume, hot reset, and PCIe link stability.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU configurations that include NBIO 7.4 paths, especially NBIO, PSP, SMU/PowerPlay, and DCN display translation units that include `nbio_7_4_offset.h`.
- Static generated-header checks that every register macro has the expected `_BASE_IDX`, base-index values match the address-block comments, duplicate macro guards are intentional, and VF0-VF15 repeated blocks are identical except for the VF number.
- Cross-check every register name in this chunk against `nbio_7_4_sh_mask.h` where field definitions exist, and against hardware register-database output used to generate the header.
- Runtime register-dump comparison on NBIO 7.4 hardware: BIOS scratch, PCIe indirect access, RCC/BIF control, doorbell ranges, mailbox registers, HDP flush state, GDC doorbell ranges, and MSI-X table offsets should match expected hardware dumps.
- SR-IOV validation with multiple VFs enabled: per-VF doorbell apertures, function identifiers, mailbox interrupts, HDP flushes, BME status, transaction-pending reporting, and MSI-X vector programming should stay isolated by VF number.
- Power/reset testing across BACO, suspend/resume, GPU reset, and PCIe hot reset should verify that driver restore code uses the correct offsets and does not assume persistence not guaranteed by hardware.
- Error-path testing should cover PCIe/RCC error logging, interrupt controls, mailbox timeouts, HDP flush timeouts, and transaction-pending polling with bounded waits.
