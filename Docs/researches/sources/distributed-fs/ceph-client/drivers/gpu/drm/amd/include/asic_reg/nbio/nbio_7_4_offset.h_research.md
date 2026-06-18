# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003224`: lines 1-2439, `Docs/researches/chunks/subset-b-003224_research.md`
- `subset-b-003225`: lines 2440-4631, `Docs/researches/chunks/subset-b-003225_research.md`

## Chunk Research

### subset-b-003224: lines 1-2439

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h lines 1-2439

## Purpose

This chunk is the first half of the generated AMD NBIO 7.4 register offset header. It contains compile-time `#define` constants for PCI/PCIe configuration-space offsets exposed by NBIO/BIF blocks on AMD GPUs. There is no executable driver logic in this range; its purpose is to give other AMDGPU power-management, NBIO, virtualization, and register-access code stable symbolic names for byte offsets inside PCI configuration and extended-capability spaces.

The assigned range starts with the license and include guard, then covers the `nbio_pcie0_pswuscfg0_cfgdecp` upstream/switch-style PCIe config block, physical-function config blocks for `EPF0` and `EPF1`, a downstream switch/device block named `SWDS0`, and SR-IOV virtual-function config templates from `VF0` through the start of `VF15`. The chunk stops at line 2439 inside the `VF15` block, so later NBIO decoder/MMIO offsets and the end of the include guard are intentionally outside this work item.

## Public Surface In This Chunk

The public surface is 2,337 preprocessor constants in the assigned line range. They use generated `cfg...` names and hexadecimal byte offsets, for example:

- `cfgPSWUSCFG0_*` for the PCIe upstream/switch configuration block.
- `cfgBIF_CFG_DEV0_EPF0_0_*` and `cfgBIF_CFG_DEV0_EPF1_0_*` for physical functions.
- `cfgBIF_CFG_DEV0_SWDS0_*` for the downstream switch/device configuration block.
- `cfgBIF_CFG_DEV0_EPF0_VF<N>_0_*` for SR-IOV virtual functions `0` through `15`, with `VF15` incomplete in this chunk.

There are no functions, structs, enums, storage objects, inline helpers, or local state. The API contract is the exact macro spelling and numeric offset. These offsets must be paired with the matching NBIO 7.4 shift/mask header and with the register access mechanism that selects the correct PCIe configuration aperture or indirect register decode path.

## Register Coverage

The `PSWUSCFG0` block covers a bridge/upstream-port style PCI config layout: vendor/device IDs, command/status, revision/class bytes, bridge bus numbering, I/O and memory windows, interrupt pins, PM capability, PCIe device/link capability/control/status, MSI, SSID, MSI mapping, vendor-specific capability, virtual-channel capability, AER, secondary PCIe capability, per-lane equalization controls, ACS, multicast, LTR, ARI, L1 PM substates, ESM, data-link feature, 16 GT PHY/link registers, parity mismatch status, and lane margining controls/status for lanes 0-15.

The `EPF0` and `EPF1` physical-function blocks are much larger endpoint-style PCIe config maps. They include conventional endpoint BARs and ROM BARs, PM, PCIe device/link and slot capability blocks, MSI and MSI-X, vendor-specific and virtual-channel capabilities, AER logs, resizeable BAR capability/control for PF and VF BARs, power budget and DPA controls, secondary PCIe/equalization/ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV capability and VF BAR layout, TPH requester, data-link feature, 16 GT PHY/link/equalization, margining, and an AMD GPU IOV vendor-specific block.

The GPU IOV vendor-specific block in both PFs is notable because it describes virtualization management registers: SR-IOV shadow, interrupt enable/status, reset control, hypervisor/VM mailbox dwords, context, total framebuffer, per-VF framebuffer allocation from `VF0_FB` through `VF30_FB`, peer-to-peer over XGMI enable, and scheduler dword windows for UVD, VCE, GFX, and UVD1 engines. These are offsets only; behavior and access rules live in the hardware specification and consuming driver code.

The `SWDS0` block is a bridge/switch-downstream style layout. It has bridge windows, PM, PCIe device/link/slot capability registers, MSI, SSID, vendor-specific capability, VC, AER, secondary PCIe/lane equalization, ACS, data-link feature, 16 GT PHY/link registers, and margining controls/status. Compared with the PF blocks it does not carry the endpoint BAR set, ATS/PASID/page-request, SR-IOV, or GPU IOV scheduling windows.

The `VF0` through `VF14` blocks are repetitive SR-IOV VF endpoint config templates. Each complete VF block includes conventional IDs/class/header/BAR/ROM/CAP fields, PCIe device/link and slot-capability registers, MSI and MSI-X, vendor-specific capability, AER status/mask/severity and logs, ATS, and ARI capability/control. The assigned range then begins `VF15` and covers it only through `PCIE_TLP_PREFIX_LOG3`.

## Control Flow And State

This header has no runtime control flow. Its effective flow is compile-time substitution:

1. A consumer includes `nbio/nbio_7_4_offset.h`, either directly or via another generated AMDGPU register header.
2. The consumer uses a `cfg...` macro as a byte offset for a selected NBIO/BIF PCI configuration-space target.
3. Register helpers or device-specific code combine that offset with the appropriate config-access path, instance, function, or VF selection.
4. Actual reads and writes happen outside this header through PCI config-space accessors, AMDGPU MMIO/indirect access paths, or firmware/SMU-facing routines.

The header stores no software state and persists nothing. Persistent or latched state is in hardware registers: PCI command bits, BAR/window programming, PM/ASPM controls, MSI/MSI-X setup, AER status/logs, link/equalization state, SR-IOV configuration, and GPU IOV resource allocation. Some registers are read-only identity/status, some are configuration controls, and others are sticky or write-one-to-clear error/log registers; this file does not encode those access semantics.

## Dependencies And Integration Points

The semantic dependency is the NBIO 7.4 hardware register database plus the PCI and PCI Express configuration-space specifications. Names and offsets in this file mirror PCI capability chains, PCIe extended capabilities, SR-IOV, ATS, PASID, PRI, ACS, AER, VC, LTR, TPH, lane equalization, margining, and AMD GPU IOV vendor extensions.

Direct source-tree includes for this NBIO 7.4 offset header appear in AMDGPU power-management paths such as `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, and the older PowerPlay include `pm/powerplay/hwmgr/vega20_inc.h`. Those users depend on the generated constants remaining aligned with the target ASIC generation.

The most important pairing is with the same-generation NBIO 7.4 shift/mask definitions. Offset macros identify register locations; shift/mask macros identify fields inside those registers. Mixing offsets from this header with another NBIO generation's masks is a high-risk integration error because many names and offsets repeat across generations while field layouts can differ.

## Risks And Maintenance Notes

- This is generated hardware-interface data. Hand editing individual constants is risky unless synchronized with AMD's authoritative register source.
- Repeated PF/VF blocks make copy/paste or review mistakes hard to spot. A wrong function prefix, VF number, or `_0` instance suffix can direct code at the wrong config-space function.
- Several names intentionally alias the same offset for 32-bit and 64-bit MSI layouts, such as message data, mask, and pending registers. Consumers must choose the layout based on MSI capability state, not merely by distinct macro names.
- Endpoint, bridge, PF, and VF blocks share many PCIe capability names but are not interchangeable. For example, PF blocks include SR-IOV, ATS/PASID/PRI, resizeable BAR, and GPU IOV controls that the bridge/downstream block lacks.
- GPU IOV offsets describe privileged virtualization controls and resource partitioning. Misprogramming them can affect VF reset, mailbox signaling, framebuffer partition visibility, interrupt routing, or engine scheduler assignment.
- Link-training and diagnostics offsets are protocol-sensitive. Incorrect use of equalization, 16 GT, margining, parity-mismatch, AER, ACS, or data-link feature offsets can cause link instability, broken error reporting, or isolation failures.
- This chunk ends mid-`VF15`; any per-file analysis must reconcile the continuation in the next chunk before making complete statements about all VF and later decoder blocks.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for translation units that include `nbio_7_4_offset.h`, especially Arcturus/Aldebaran/SMU13 power-management and NBIO-related AMDGPU paths.
- Generated-header comparison against AMD's NBIO 7.4 register database to confirm every macro name and hex offset.
- Cross-header checks that these `cfg...` offsets have compatible NBIO 7.4 shift/mask definitions for fields used by driver code.
- Static checks for duplicated offsets that are expected aliases, such as MSI 32-bit versus 64-bit layouts, and unexpected duplicates across unrelated registers.
- PCI config-space dumps on NBIO 7.4 hardware compared with decoded `lspci -vvxxx` output for PM, PCIe, MSI/MSI-X, AER, ACS, ATS/PASID/PRI, SR-IOV, resizeable BAR, LTR, TPH, and margining capability chains.
- SR-IOV validation that enables PFs and VFs, enumerates VF0-VF15 config spaces, checks MSI/MSI-X and ARI/ATS capability offsets, and verifies VF BAR layout against the PF SR-IOV capability.
- Error-injection or hardware error observation for AER status/mask/severity/header/TLP-prefix logs using the offsets in PF, VF, and switch/downstream blocks.
- Link-training and signal-integrity tests that exercise equalization, 16 GT status, parity mismatch, and per-lane margining offsets without unexpected retrains or malformed lane status.

### subset-b-003225: lines 2440-4631

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
