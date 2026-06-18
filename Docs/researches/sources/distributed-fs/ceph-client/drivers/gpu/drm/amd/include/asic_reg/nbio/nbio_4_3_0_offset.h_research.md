# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002953`: lines 1-2670, `Docs/researches/chunks/subset-b-002953_research.md`
- `subset-b-002954`: lines 2671-4989, `Docs/researches/chunks/subset-b-002954_research.md`
- `subset-b-002955`: lines 4990-7548, `Docs/researches/chunks/subset-b-002955_research.md`
- `subset-b-002956`: lines 7549-10000, `Docs/researches/chunks/subset-b-002956_research.md`
- `subset-b-002957`: lines 10001-12430, `Docs/researches/chunks/subset-b-002957_research.md`
- `subset-b-002958`: lines 12431-14904, `Docs/researches/chunks/subset-b-002958_research.md`
- `subset-b-002959`: lines 14905-17348, `Docs/researches/chunks/subset-b-002959_research.md`
- `subset-b-002960`: lines 17349-17381, `Docs/researches/chunks/subset-b-002960_research.md`

## Chunk Research

### subset-b-002953: lines 1-2670

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 1-2670

## Scope

This chunk is the opening section of the generated AMD NBIO 4.3.0 offset header. It covers the license/header guard and the first 69 `addressBlock` groups, from `nbio_nbif0_bif_bx_SYSDEC` through the start of `nbio_pcie0_pswuscfg0_cfgdecp`. Within lines 1-2670 there are 2,338 preprocessor definitions: 1,225 register/config address macros and 1,113 matching `_BASE_IDX` macros. The base-index distribution is 57 macros for base index 0, 90 for index 1, 677 for index 2, and 289 for index 3.

The file is data-only C preprocessor material. It defines no functions, structs, enums, storage, locks, allocation behavior, or direct MMIO operations. Its public interface is the generated offset convention:

- `reg<NAME>` or `cfg<NAME>` gives a register or PCI configuration-space offset/address.
- `reg<NAME>_BASE_IDX` identifies which NBIO base segment is combined with the offset by `NBIO_BASE()`, `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and related helpers.

## Purpose

This header is the NBIO 4.3.0 register-address ABI for AMDGPU, display, and SMU code. NBIO covers PCIe/NBIF-facing control surfaces such as indirect PCIe access, firmware/driver/BIOS scratch registers, interrupt control, doorbell aperture routing, HDP coherency flushes, host memory access, PCIe link and ASPM/LTR programming, SR-IOV/PF/VF windows, MSI-X tables, mailbox registers, and PCIe configuration-space capabilities.

The companion `nbio_4_3_0_sh_mask.h` supplies bitfield shifts and masks for many of these addresses. Code normally uses this offset header with generated bitfield macros and AMDGPU helper APIs rather than hard-coded numeric offsets.

## Important Macro Families

### BIF_BX0 System Decode

The first block, `nbio_nbif0_bif_bx_SYSDEC`, defines the low-level NBIO/BIF system decode registers:

- `regBIF_BX0_PCIE_INDEX`, `regBIF_BX0_PCIE_DATA`, `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, and high-index variants expose indirect PCIe register access windows.
- `regBIF_BX0_SBIOS_SCRATCH_*`, `regBIF_BX0_BIOS_SCRATCH_*`, `regBIF_BX0_DRIVER_SCRATCH_*`, and `regBIF_BX0_FW_SCRATCH_*` define shared scratch register slots used for firmware, BIOS, driver, and display handoff state.
- `regBIF_BX0_BIF_RLC_INTR_CNTL`, `regBIF_BX0_BIF_VCE_INTR_CNTL`, and `regBIF_BX0_BIF_UVD_INTR_CNTL` expose engine interrupt controls.
- `regBIF_BX0_GFX_MMIOREG_CAM_ADDR*`, matching remap addresses, and CAM control/completion registers describe a GFX MMIO register remap/CAM aperture.

These early macros are especially visible to display resource code. `dcn32_resource.c` and `dcn321_resource.c` include this header and build `NBIO_SR()` entries from `regBIF_BX0_BIOS_SCRATCH_3`, `regBIF_BX0_BIOS_SCRATCH_6`, and their base-index macros.

### RCC Downstream, Endpoint, and Root-Complex Controls

The `rcc_dwn`, `rcc_dwnp`, `rcc_ep`, and `rcc_dev0` blocks define PCIe-facing control/status surfaces:

- Downstream and downstream-port blocks include PCIe reserved/scratch/control/config/RX/bus/strap registers, link-speed controls, LTR message state, and error controls.
- Endpoint block macros include endpoint PCIe scratch/control/interrupt/status, bus/config controls, transmit LTR control, DPA capabilities and substate power-allocation aliases, PME control, TX requester ID, error/RX controls, and link-speed control.
- Root-complex device macros include RAS/error interrupt control, BACO, reset enable, vendor-defined-message support, margining parameters, GPU IOV region and HostVM enable, console IOV mode and VF layout, peer register ranges, bus/config aperture sizing, XDMA ranges, feature controls, bus number lists, captured host bus number, peer framebuffer offsets, device/function lists, link controls, endpoint requester-ID restore, LTR switch control, and multi-host arbitration.

`nbio_v4_3.c` uses these address definitions to read strap revision ID, program LTR and ASPM paths, control memory access, and initialize NBIO state.

### PF, VF, and Indirect Access Windows

`nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and each VF `SYSPFVFDEC` block define `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` style indirect MMIO access windows. The PF block also defines `RSMU_INDEX`, `RSMU_DATA`, and `RSMU_INDEX_HI`, which `nbio_v4_3_get_pcie_index_offset()` and `nbio_v4_3_get_pcie_data_offset()` expose through the NBIO function table.

The presence of both PF and per-VF indirect windows is important for SR-IOV. It lets PF-owned and VF-owned code paths address different windows while still sharing the same generated macro naming convention.

### BIF_BX0 Core BIF Controls

The `nbio_nbif0_bif_bx_BIFDEC1` block defines core NBIO/BIF controls:

- Strap and pinstrap registers such as `regBIF_BX0_CC_BIF_BX_STRAP0` and `regBIF_BX0_CC_BIF_BX_PINSTRAP0`.
- Indirect access and bus controls such as `regBIF_BX0_BIF_MM_INDACCESS_CNTL`, `regBIF_BX0_BUS_CNTL`, and BIF scratch registers.
- Reset and interrupt controls including `regBIF_BX0_BX_RESET_EN`, `regBIF_BX0_BX_RESET_CNTL`, `regBIF_BX0_INTERRUPT_CNTL`, and `regBIF_BX0_INTERRUPT_CNTL2`.
- Doorbell and framebuffer enable registers such as `regBIF_BX0_BIF_DOORBELL_CNTL`, `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, and `regBIF_BX0_BIF_FB_EN`.
- Transaction pending, memory type, NBIF GFX address LUT, HDP remap flush controls, BIF ring-buffer pointers, and MP1 interrupt control.

`nbio_v4_3.c` uses this family for HDP remap programming, MC framebuffer access enable/disable, IH interrupt setup, and register-remap base selection.

### MSI-X, Strap, GDC, and PF BIFPFVF Blocks

`nbio_nbif0_rcc_dev0_epf0_BIFDEC2` defines four GFX MSI-X vector table entries, each with low/high address, message data, and control registers, plus an MSI-X pending-bit array (`GFXMSIX_PBA`). The same table shape reappears for each VF.

`nbio_nbif0_rcc_strap_BIFDEC1` lists BIF, port, and endpoint-function strap registers. These are persistent hardware configuration inputs or latched strap states. Driver code reads selected strap fields to derive revision, link, or power-management policy.

`nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` defines PF-visible BME status, atomic error logging, self-ring doorbell aperture base/control, HDP coherency flush and invalidate controls, GPU HDP flush request/done, transaction-pending, and NBIF GFX address LUT bypass registers. `nbio_v4_3_get_hdp_flush_req_offset()`, `nbio_v4_3_get_hdp_flush_done_offset()`, and `nbio_v4_3_enable_doorbell_selfring_aperture()` are direct consumers of this surface.

`nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]` defines EPF0 RCC error log, doorbell aperture enable, config memory size, config reserved, and IOV function identifier registers. `nbio_v4_3_get_memsize()` reads `regRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`, and `nbio_v4_3_enable_doorbell_aperture()` uses the associated doorbell aperture enable field.

`nbio_nbif0_gdc_GDCDEC` contributes a smaller GDC group: SHUB interface control, NBIF GFX doorbell status, ATDMA miscellaneous control, and S2A miscellaneous control.

### VF0 Through VF15 Repeated Register Windows

The largest portion of this chunk is the repeated VF0 through VF15 layout. Each VF has three block shapes:

- `bif_bx_dev0_epf0_vfN_BIFPFVFDEC1` with BME status, atomic error log, self-ring doorbell aperture base/control, HDP register/memory coherency flush controls, flush-only and invalidate-only controls, GPU HDP flush request/done, transaction-pending status, NBIF GFX address LUT bypass, transmit and receive mailbox data dwords, mailbox control, mailbox interrupt control, and `BIF_VMHV_MAILBOX`.
- `bif_bx_dev0_epf0_vfN_SYSPFVFDEC` with VF indirect MM index/data/high-index registers.
- `rcc_dev0_epf0_vfN_BIFPFVFDEC1` and `rcc_dev0_epf0_vfN_BIFDEC2` with VF RCC error/config/doorbell/IOV identity registers and four MSI-X vector entries plus PBA.

The repeated offsets are intentionally identical across VFs while the macro names encode the VF number. This provides compile-time names for per-VF management without requiring callers to hand-calculate register names. The pattern also means mechanical generator errors can affect all VFs in the same way.

### PCIe Config-Space Block Start

The final covered block starts `nbio_pcie0_pswuscfg0_cfgdecp` at base address `0xfffe00000000`. Unlike the earlier `reg*` macros, this block uses `cfgPSWUSCFG0_0_*` macros with absolute-looking PCIe configuration-space addresses. Covered entries include:

- Standard config header fields: vendor/device ID, command/status, revision/class, cache line, latency, header type, BIST, bus-number windows, IO/memory/prefetchable base/limit registers, ROM base, and interrupt line/pin.
- Capability registers for vendor-specific, power-management, PCIe, MSI, SSID, virtual channel, device serial number, advanced error reporting, secondary PCIe, ACS, and multicast capability structures.
- Link, device, lane equalization, AER header/TLP-prefix log, and multicast address registers.

The chunk ends in this PCIe config block at `cfgPSWUSCFG0_0_PCIE_MC_ADDR1`; later config entries continue outside the requested range.

## Control Flow and State Behavior

There is no executable control flow in this header. All behavior is compile-time name binding: C code includes the header, picks a generated macro, combines it with a base index, and issues reads/writes through AMDGPU MMIO or config-space helpers.

The state described by this chunk is persistent hardware state, not in-memory driver state. Examples include BIOS/driver/firmware scratch contents, PCIe link and endpoint state, interrupt routing, BIF reset state, doorbell aperture bases and enables, HDP flush request/done state, transaction-pending bits, VF mailbox contents, MSI-X vector programming, strap-derived configuration, PCIe capability registers, and config-space error/status latches.

Several registers are command-like or status-like rather than durable configuration. HDP flush request/done, coherency flush-only/invalidate-only controls, interrupt status/control, transaction-pending, mailbox valid/ack state, MSI-X PBA bits, AER status/log fields, and scratch registers need ordering and polling discipline from the owning driver code. The offset header does not encode those semantics.

## Dependencies and Integration Points

This chunk depends on the broader generated NBIO 4.3.0 header set:

- `nbio_4_3_0_sh_mask.h` supplies field shifts and masks for many registers named here.
- SOC15/NBIO helper macros such as `NBIO_BASE()`, `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_FIELD15_PREREG()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()` consume the generated names.
- `amdgpu/nbio_v4_3.c` is the direct NBIO implementation consumer. It reads/writes registers for HDP remap, revision ID, framebuffer access, memory size, SDMA/VCN/IH/GC doorbell windows, self-ring doorbell aperture, interrupt control, clock gating, light sleep, HDP flush offsets, RSMU indirect access offsets, register remap, ASPM/LTR, and SR-IOV function-table variants.
- `amdgpu_discovery.c` selects `nbio_v4_3_funcs`, `nbio_v4_3_sriov_funcs`, and `nbio_v4_3_hdp_flush_reg` for matching hardware, so these offsets are part of runtime ASIC discovery wiring.
- `gmc_v11_0.c`, `gfx_v11_0.c`, `sdma_v6_0.c`, `sdma_v7_0.c`, and `sdma_v7_1.c` include `nbio_v4_3.h` and indirectly rely on the NBIO function table backed by these offsets.
- `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c` include this offset/mask pair for SMU power-management policy.
- `display/dc/resource/dcn32/dcn32_resource.c` and `dcn321_resource.c` include this header to populate NBIO scratch-register addresses used by display resource code.

## Risks

- Offset drift is high impact. A wrong numeric value or `_BASE_IDX` can direct reads/writes to a different NBIO aperture, corrupting PCIe, doorbell, interrupt, HDP flush, or VF state.
- The PF/VF repetition is vulnerable to mechanical mistakes. VF0-VF15 blocks have near-identical offset values with different macro names; a missing VF, swapped suffix, or wrong base index could break SR-IOV isolation or VF interrupt/mailbox routing.
- Doorbell aperture and self-ring doorbell registers are security and stability sensitive. Wrong base, size, mode, or enable values can expose an incorrect GPA window or make ring doorbells stop working.
- HDP coherency and flush registers are ordering-sensitive. Incorrect request/done offsets or coherency flush controls can leave CPU-visible or GPU-visible memory stale.
- Mailbox and VM/HV registers are protocol-sensitive. Offsets alone do not express valid/ack sequencing, interrupt enables, or ownership; misuse can wedge PF/VF communication.
- MSI-X table and PBA offsets must match PCIe expectations. Incorrect vector address/data/control mapping can break interrupts or leave vectors masked/pending incorrectly.
- PCIe ASPM/LTR and link-control registers interact with platform policy. Bad offsets or field pairing can cause link instability, resume failures, or poor power behavior.
- Scratch registers are shared with firmware/BIOS/display paths. Treating them as private storage risks clobbering handoff state.
- The final PCIe config block is partial in this chunk. File-level conclusions about `cfgPSWUSCFG0_0_*` must be reconciled with later chunks.

## Test and Validation Signals

Useful validation signals are mostly compile-time integration and hardware bring-up:

- Build AMDGPU, SMU13, and DCN32/DCN321 code paths that include `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`; this catches missing or renamed generated macros.
- Exercise `nbio_v4_3_funcs` on matching ASICs through discovery, probing, suspend/resume, and remove paths.
- Verify HDP flush request/done offsets by running graphics, compute, SDMA, and KFD workloads that depend on CPU/GPU coherency.
- Test doorbell programming for SDMA, VCN, IH, GC, and self-ring apertures; confirm rings advance and interrupts are delivered.
- In SR-IOV environments, validate VF0-VF15 mailbox, MSI-X, doorbell, and HDP flush paths with multiple VFs active.
- Check display initialization on DCN32/DCN321 systems, especially BIOS scratch register use for display handoff.
- Exercise SMU13 power-management flows that include this NBIO header, including ASPM/LTR, clock gating, and light sleep transitions.
- Validate PCIe error and capability handling through AER/status inspection and link retraining or ASPM test coverage.

## Cross-Chunk Notes

The requested range starts at the file header and ends inside the `cfgPSWUSCFG0_0_*` PCIe configuration-space block. Earlier sections are complete enough to describe the BIF/RCC/PF/VF groups, but the PCIe config block continues beyond line 2670. The final per-file reconciliation should merge this chunk with later chunks before making source-file-level claims about the full NBIO 4.3.0 config-space map.

### subset-b-002954: lines 2671-4989

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 2671-4989

## Scope

This chunk is part of AMDGPU's generated NBIO 4.3.0 register offset header. It contains C preprocessor `#define` constants for NBIF/BIF PCIe configuration-space and NBIO decoder MMIO addresses. It is declarative hardware metadata: there are no C functions, structs, enums, variables, locks, allocation paths, executable control flow, or software persistence routines.

The covered range starts in the tail of the `cfgPSWUSCFG0_0_*` PCIe capability/configuration window, then contains:

- The complete root-complex config-space block `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` at base `0xfffe10100000`.
- Endpoint physical-function config-space blocks for `EPF0`, `EPF1`, `EPF2`, and `EPF3` at bases `0xfffe10200000`, `0xfffe10201000`, `0xfffe10202000`, and `0xfffe10203000`.
- NBIF/BIF system, downstream, endpoint, PF/VF, RCC, strap, GDC, SUM, and shadow-register decoder blocks around `0x30200000`, `0x100000`, and `0xfffe30000000`.
- Complete SR-IOV virtual-function config-space offset blocks for `EPF0_VF0` through `EPF0_VF10` at bases `0xfffe10300000` through `0xfffe1030a000`.
- The beginning of `EPF0_VF11`, ending at `cfgBIF_CFG_DEV0_EPF0_VF11_0_BASE_ADDR_4`.

Although this repository path is under a local `ceph-client` source mirror, this file is AMD GPU PCIe/NBIO register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The header gives symbolic names to absolute or bus-relative NBIO 4.3.0 register addresses so AMDGPU code can avoid hard-coded magic offsets when accessing PCIe configuration registers, NBIF control/status registers, MSI-X tables, strap registers, doorbell apertures, mailbox registers, scratch registers, and virtualization-related decoder windows.

The macro families in this chunk follow a hardware-address map pattern:

- `cfgPSWUSCFG0_0_*` covers PCIe switch/upstream-style capability registers such as multicast, LTR, ARI, data-link feature, 16 GT/s PHY, lane equalization, lane margining, and 32 GT/s link registers.
- `cfgBIF_CFG_DEV0_RC0_*` covers a root-complex PCI bridge configuration image, including standard PCI header fields, bridge windows, PCIe capabilities, MSI, vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe, ACS/PASID/MC/LTR/ARI, data-link feature, 16 GT/s, lane margining, and 32 GT/s registers.
- `cfgBIF_CFG_DEV0_EPF<n>_0_*` covers endpoint physical-function config spaces. `EPF0` is the richest block in this range and includes SR-IOV, resizable VF BAR, ACS, PASID, multicast, LTR, ARI, power budgeting, dynamic power allocation, lane equalization, lane margining, and 16/32 GT/s offsets. `EPF1` through `EPF3` expose smaller repeated endpoint function layouts with PCI/PCIe, MSI/MSI-X, vendor-specific, AER, BAR, power/DPA, ACS/PASID, and ARI subsets.
- `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` covers per-virtual-function PCI configuration windows for SR-IOV VFs. Each full VF block in this chunk has 78 offsets, from standard identity/header/BAR registers through PCIe capability, MSI/MSI-X, vendor-specific extended capability, AER logs, and ARI capability/control registers.
- `cfgPCIE_*`, `cfgBIF_*`, `cfgRCC_*`, `cfgDN_PCIE_*`, `cfgEP_PCIE_*`, `cfgNGDC_*`, `cfgSUM_*`, `cfgSHADOW_*`, and related names cover direct NBIF/RCC/GDC/SUM decoder registers used for indirect access, scratch state, link control, resets, interrupts, doorbells, HDP coherency flush/invalidate, mailbox transport, GPUIOV regions, peer address ranges, bus numbering, MSI-X vectors, strap configuration, and shadowed bridge/window state.

These constants are the address side of the generated register contract. Companion `*_sh_mask.h` headers define bit positions and masks for fields inside the registers named here.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The interface is the macro namespace itself.

Important offset groups:

- PCI/PCIe config header offsets: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class-code bytes, cache line, latency, header, BIST, BARs, ROM BAR, capability pointer, interrupt line/pin, bridge bus/window registers for `RC0`, and endpoint/VF BAR/config fields.
- PCIe capability offsets: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, version-2 device/link capability/control/status registers, and root/slot-specific registers where present.
- Interrupt offsets: MSI and MSI-X capability registers in config space, plus RCC GFX MSI-X vector registers `cfgRCC_DEV0_EPF0_GFXMSIX_VECT[0-3]_*` and `cfgRCC_DEV0_EPF0_GFXMSIX_PBA`.
- Error/reporting offsets: PCIe AER uncorrectable/correctable status, masks, severity, capability/control, header logs, TLP prefix logs, `cfgBIF_BX_PF_BIF_ATOMIC_ERR_LOG`, `cfgRCC_ERR_INT_CNTL`, and `cfgRCC_DEV0_EPF0_RCC_ERR_LOG`.
- Link and PHY offsets: data-link feature registers, 16 GT/s and 32 GT/s link capability/control/status, lane equalization and margining registers, endpoint/downstream link control registers, speed controls, and LTR controls.
- Virtualization and isolation offsets: SR-IOV capability/control/status and VF BAR registers in `EPF0`, ACS/PASID/ARI registers, GPUIOV region and function identifier registers, VF config-space windows, BME status, PF/VF transaction-pending registers, and PF/VF mailbox registers.
- Addressing, aperture, and coherency offsets: NBIF GFX address LUTs, peer FB offsets, config aperture sizing, XDMA address registers, doorbell aperture registers, HDP coherency flush/invalidate controls, and shadowed PCI bridge window registers.
- Firmware/driver communication offsets: SBIOS, BIOS, driver, and firmware scratch registers, mailbox transmit/receive dwords, mailbox control/interrupt registers, and `cfgBIF_BX_PF_BIF_VMHV_MAILBOX`.

Consumers normally combine these offsets with AMDGPU register-access helpers and generated shift/mask macros. The file itself does not prescribe access width, ordering, read/write permissions, or side-effect behavior.

## Control Flow

This chunk has no runtime control flow. Inclusion is governed by the full file's header guard outside this slice. At compile time, any source file that includes `nbio_4_3_0_offset.h` receives these macro constants.

The runtime flow is implemented by consuming driver code:

1. Select an NBIO 4.3.0 offset macro for the relevant PCIe config, NBIF, RCC, GDC, SUM, shadow, PF, or VF register.
2. Read or write through AMDGPU's SOC15, PCIe, indirect-index, or MMIO helper path.
3. Use companion shift/mask definitions when decoding or composing register values.
4. Poll hardware-owned status, program config/control bits, clear sticky errors according to register semantics, or expose decoded state to PCIe, interrupt, reset, virtualization, or RAS paths.

The repeated endpoint and VF blocks imply table-like hardware layout, but this header does not implement iteration. Any loop over functions or VFs is performed by higher-level code that selects the correct generated symbol or computes the appropriate config-space access path.

## State and Persistence Behavior

This header stores no software state and persists nothing to disk. The state represented by these offsets lives in GPU NBIO hardware registers, PCI/PCIe configuration space, firmware-programmed straps/scratch registers, and host/guest PCI configuration policy.

Configuration state represented in this range can persist until reset, function-level reset, hot reset, suspend/resume, GPU power transition, or explicit driver/firmware reprogramming. Examples include PCI command bits, BARs and bridge windows, MSI/MSI-X programming, link controls, DPA/power-budget controls, ACS/PASID/ARI/SR-IOV controls, doorbell aperture setup, HDP coherency controls, config aperture sizing, peer FB offsets, bus-number lists, and address LUT entries.

Other represented registers are volatile status, diagnostic, or mailbox state: link status, AER status and logs, transaction-pending indicators, interrupt status, scratch registers, mailbox buffers, MSI pending bits, lane error/equalization/margining status, GPUIOV identifiers, and reset-related state. The offset header does not encode whether individual fields are read-only, write-one-to-clear, self-clearing, sticky, firmware-owned, guest-owned, or power-gated; callers must rely on the hardware programming guide, PCIe specification semantics, and companion field metadata.

The VF config-space blocks are especially tied to SR-IOV lifecycle. PF setup, VF enable/disable, guest driver programming, FLR, host PCI core policy, IOMMU/ATS state, and virtualization firmware can all change the underlying registers independently of this header.

## Dependencies and Integration Points

The direct dependency is AMD's generated NBIO 4.3.0 register database. This offset header must remain synchronized with sibling NBIO generated headers, especially `nbio_4_3_0_sh_mask.h`, where per-register field shifts and masks are defined.

Known source integration includes SMU 13 power-management code that includes `nbio/nbio_4_3_0_offset.h`. Broader AMDGPU integration points include:

- NBIO and PCIe register access paths that use `cfg*` constants for config-space and MMIO-style register addressing.
- Linux PCI/PCIe enumeration and capability handling for standard config header, bridge window, PCIe capability, MSI/MSI-X, AER, ACS, PASID, LTR, ARI, DLF, 16/32 GT/s, and lane margining/equalization registers.
- SR-IOV and virtualization paths that expose or manage PF/VF config windows, VF BAR sizing, VF device IDs, function identifiers, GPUIOV regions, BME/transaction status, guest/host isolation controls, and PF/VF mailbox traffic.
- Interrupt delivery paths using MSI/MSI-X config-space offsets, RCC GFX MSI-X vector tables, interrupt control/status registers, and mailbox interrupt controls.
- Reset, power, and link-management paths using link controls, speed controls, BACO controls, reset enable/control registers, DPA/power-budget offsets, CLKREQ/PERST/WAKE/VAUX pad controls, and LTR controls.
- RAS/error-handling and diagnostics using AER status/log offsets, atomic error logs, RCC error logs, lane error status, TLP prefix/header logs, and scratch/mailbox registers.
- Address translation and coherency paths using PASID/ACS/ARI/SR-IOV offsets, NBIF address LUTs, peer FB offsets, XDMA registers, doorbell apertures, and HDP flush/invalidate controls.

Because the constants are untyped integer literals, missing or renamed macros typically produce build failures, while incorrect numeric addresses can compile cleanly and cause accesses to the wrong hardware register.

## Risks and Edge Cases

- Chunk boundaries are partial. The first line is already inside the `cfgPSWUSCFG0_0` block, and the last line stops early in `EPF0_VF11`. Adjacent chunks are required before making complete-file or complete-block claims for those two blocks.
- Generated address drift is the primary risk. If an offset diverges from the NBIO 4.3.0 register source, downstream code may read or write a valid but wrong hardware register.
- The range mixes config-space-like absolute addresses such as `0xfffe10200000`, normal MMIO-style addresses around `0x30200000`, SUM indirect access offsets around `0x1000e0`, and small PF1 index/data offsets at `0x0`, `0x4`, and `0x18`. Consumers must use the correct access path for each address space.
- Repeated PF and VF blocks are hard to audit manually. Off-by-one function numbers, base-address strides, or copy-generation mistakes may only appear when the affected function or VF is instantiated.
- Some symbols intentionally alias the same address because PCI layouts overlay 32-bit and 64-bit forms, for example MSI message data and MSI address/high or MSI mask/pending aliases. Consumers must interpret the alias according to capability state and access width.
- Link-control, lane-margining, equalization, 16/32 GT/s, DPA, power-budget, reset, and BACO registers are hardware-state sensitive. Incorrect writes can cause link retraining failures, enumeration failures, hangs, or power-management regressions.
- Error and AER registers can be sticky or write-one-to-clear. Reading or writing through the wrong offset can lose diagnostic evidence or mask serious PCIe errors.
- SR-IOV, ACS, PASID, ARI, GPUIOV, and mailbox registers are isolation-sensitive. Wrong offsets can break VF discovery, DMA address translation, guest interrupt delivery, or host/guest isolation.
- Scratch, strap, and shadow registers may be firmware-owned or latched from boot-time configuration. Treating them as ordinary driver-owned storage can conflict with firmware expectations.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU configurations that include `nbio_4_3_0_offset.h`, especially SMU 13 and NBIO/PCIe paths; missing macro names or duplicate definitions should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database, including address-block base checks, monotonic-offset checks, expected PF/VF stride checks, and offset-to-shift/mask pairing checks against `nbio_4_3_0_sh_mask.h`.
- Compare repeated endpoint and VF config-space blocks for expected structural identity and expected differences: `EPF0` has SR-IOV/VF-resize/multicast/LTR/lane-margining breadth, while `EPF1` through `EPF3` and VF blocks are smaller repeated images.
- Boot affected AMD hardware and verify PCI enumeration, bridge/window setup, BAR sizing, MSI/MSI-X capability traversal, AER capability traversal, and PCIe link capability/status reporting.
- Exercise SR-IOV configurations that instantiate VFs 0 through 11; validate VF config-space reads, BAR sizing, VF device IDs, bus mastering/memory enable behavior, FLR/reset, ARI routing, and isolation-relevant ACS/PASID behavior.
- Exercise interrupt delivery through MSI/MSI-X and RCC GFX MSI-X vector registers; lost interrupts, stuck pending bits, or unexpected masking can indicate offset mismatches.
- Run PCIe link and power-management tests covering ASPM/LTR, DPA/power-budget, 16 GT/s and 32 GT/s capability/status, lane equalization, lane margining, BACO/reset, and suspend/resume transitions.
- Use AER fault observation or injection where available to validate correctable/uncorrectable status, masks, severity, header logs, TLP prefix logs, and recovery behavior.
- Validate mailbox, doorbell, HDP coherency, peer-address, address-LUT, and GPUIOV paths under virtualization or multi-function workloads, since these registers are concentrated in the NBIF/RCC decoder portion of the chunk.

## Chunk-Specific Notes for Merge

This chunk should be merged with adjacent chunks for the final per-file report. Preserve that this slice covers the tail of `cfgPSWUSCFG0_0`, complete `RC0`, complete `EPF0` through `EPF3`, the NBIF/RCC/GDC/SUM/shadow decoder middle section, complete `EPF0_VF0` through `EPF0_VF10`, and the beginning of `EPF0_VF11` through `BASE_ADDR_4`.

### subset-b-002955: lines 4990-7548

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 4990-7548

## Purpose

This chunk is a generated AMD NBIO 4.3.0 register-offset header segment. It has no executable code; it exports C preprocessor constants that map NBIO/PCIe/NBIF register names to numeric hardware offsets. The chunk is hardware metadata used by AMDGPU code together with `nbio_4_3_0_sh_mask.h` and SOC15 register-access helpers.

The assigned range starts inside the `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp` PCI configuration-space block at the tail of VF11's standard header and capability offsets. It then covers complete config-space offset blocks for `VF12` through `VF15`, full per-VF BIF/RCC decode windows for `VF0` through `VF15`, PCIe link/controller register windows, the root/endpoint direct configuration-space register views, and the beginning of the direct `VF0` configuration-space register view. The range ends at `regBIF_CFG_DEV0_EPF0_VF0_DEVICE_CNTL`; the rest of direct VF0 and later VFs continue after this chunk.

## Exported API Surface

The only API surface is macro definitions:

- `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` constants are byte-addressed PCI configuration-space offsets for SR-IOV-style virtual functions under device 0, endpoint function 0.
- `cfgBIF_BX_DEV0_EPF0_VF<n>_*` constants are per-VF BIF decode-window addresses for BME status, atomic-error logging, doorbell self-ring apertures, HDP coherency flush controls, transaction-pending status, address-LUT bypass, and mailbox registers.
- `cfgRCC_DEV0_EPF0_VF<n>_*` constants are per-VF RCC decode-window addresses for error logging, doorbell aperture enablement, memory-size reporting, IOV function identity, and GFX MSI-X vector table/PBA registers.
- `reg*` constants are SOC15-style register indices. Each one is paired with a `*_BASE_IDX` macro, and callers must preserve that base-index association when resolving a physical MMIO address.

There are no functions, structs, enums, callbacks, globals, storage declarations, or inline helpers in this source range.

## Register Groups Covered

The opening lines complete VF11 config-space offsets from `BASE_ADDR_5` through `PCIE_ARI_CNTL`. Complete `cfgBIF_CFG_DEV0_EPF0_VF12_0_*`, `VF13_0_*`, `VF14_0_*`, and `VF15_0_*` blocks follow. Each full VF block repeats the standard PCI header, BARs, adapter/ROM/capability pointer, PCIe device/link capability and control registers, MSI/MSI-X capability registers, vendor-specific enhanced capability, AER status/mask/severity/header/TLP-prefix logs, and ARI enhanced capability/control offsets. These high-address `0xfffe1030c000` through `0xfffe1030f000` values are the config-address view, not the later direct `reg...` register-index view.

For `VF0` through `VF15`, the chunk defines four generated decode groups per VF:

- `BIFPFVFDEC1` BIF registers at bases `0xd0000000`, `0xd0080000`, and so on, advancing by `0x80000` per VF. These include `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, doorbell self-ring GPA aperture base/control, HDP register/memory coherency flush controls, flush-only/invalidate-only controls, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`, four transmit mailbox dwords, four receive mailbox dwords, mailbox control/interrupt control, and `BIF_VMHV_MAILBOX`.
- `SYSPFVFDEC` registers exposing `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` for per-VF indirect MMIO access.
- RCC `BIFPFVFDEC1` registers exposing `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`.
- RCC `BIFDEC2` GFX MSI-X windows exposing four vector entries (`ADDR_LO`, `ADDR_HI`, `MSG_DATA`, `CONTROL`) and a pending-bit array register.

The PCIe controller portions begin at `nbio_pcie0_pswusp0_pciedir_p` and `nbio_pcie0_pciedir`. They cover port/controller scratch and control registers, requester ID, lane status, error controls and injection registers, RX/TX credit accounting, NAK counters, link-control and link-training controls, link state/status registers, L1 PM substates, fine-grain clock-gating overrides, equalization coefficient controls, replay/sequence/ack-latency controls, flow-control registers, common AER masking, I2C expand/data registers, PCIe configuration control, performance counters, and additional PHY/link management surfaces.

`nbio_pcie0_pswuscfg0_cfgdecp` defines a small bridge-style config-space block beginning at base `0x1a300000`, including `cfgPSWUSCFG0_0_VENDOR_ID`, command/status/class/header/BIST fields, and `IRQ_BRIDGE_CNTL`. `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` maps the root-complex direct `regIRQ_BRIDGE_CNTL` register at base `0x10100000`.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block is the direct SOC15 register-index view of EPF0 PCI configuration space at base `0x10140000`. It starts at `regBIF_CFG_DEV0_EPF0_VENDOR_ID` index `0x10000` and reaches through PCIe 32 GT/s link capability/control/status registers. It includes endpoint identity, BARs, PM capability, PCIe device/link capability and control, MSI/MSI-X, vendor-specific and virtual-channel capabilities, device serial number, AER logs, BAR enhanced capability, power budget, DPA, secondary PCIe, per-lane equalization, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s and 32 GT/s link registers, lane margining, and VF resize BAR capability/control registers. Packed PCI fields intentionally share register indices, for example vendor/device IDs at `0x10000`, command/status at `0x10001`, and control/status halves in several capability registers.

The final block starts direct `regBIF_CFG_DEV0_EPF0_VF0_*` configuration-space registers at base `0x10160000`, from `VENDOR_ID` through `DEVICE_CNTL`. It is only a prefix of the direct VF0 block; subsequent VF0 status/link/MSI/MSI-X/AER/ARI offsets are outside this work item.

## Control Flow

There is no local control flow. Runtime control flow lives in AMDGPU callers:

1. The device's NBIO implementation selects this generated header for NBIO 4.3.0 hardware.
2. Driver code names a `cfg...` or `reg...` macro for the desired PCIe/NBIO register.
3. SOC15 helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG` combine the register index with the matching `*_BASE_IDX` and hardware instance.
4. Field-safe updates then use masks/shifts from `nbio_4_3_0_sh_mask.h`, commonly via `REG_SET_FIELD` and `REG_GET_FIELD`.

The `cfg...` constants and `reg...` constants are related but not interchangeable. `cfg...` names are config-space style byte addresses or decode-window addresses, while `reg...` names are register indices used by the SOC15 MMIO framework.

## State and Persistence Behavior

The header itself has no state and persists nothing. It names hardware state stored in the GPU/NBIO register file and PCI configuration surfaces. Writes through these offsets persist only until reset, FLR, power-state transition, firmware ownership changes, SR-IOV VF reset, or explicit driver/hypervisor writes.

Important state represented in this chunk includes VF PCI identity/capability presentation, BARs, MSI/MSI-X programming, AER status and log registers, ARI/ATS-related capability surfaces, per-VF doorbell aperture state, HDP coherency flush request/done state, BIF transaction-pending state, VF mailbox contents/control, RCC memory-size and IOV function identity, PCIe link training/equalization/margining state, ASPM/LTR-related link control, SR-IOV capability/control registers in the EPF0 direct view, and 16 GT/s/32 GT/s link capability registers.

## Dependencies and Integration Points

The direct include users in this tree are `amdgpu/nbio_v4_3.c`, the SMU 13.0.0 and 13.0.7 PPT files, and DCN32/DCN321 resource files. The most concrete runtime integration is `amdgpu/nbio_v4_3.c`, which includes both `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`.

Relevant `nbio_v4_3.c` uses tied to this chunk include:

- `nbio_v4_3_set_reg_remap()` uses `regBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` with `SOC15_REG_OFFSET(...) << 2` for the SR-IOV/VF-oriented HDP flush remap path.
- `nbio_v4_3_remap_hdp_registers()` programs remap registers so KFD-visible HDP flush offsets point at the selected NBIO flush controls.
- `nbio_v4_3_program_ltr()` and `nbio_v4_3_program_aspm()` read/write `regBIF_CFG_DEV0_EPF0_DEVICE_CNTL2`, `regBIF_CFG_DEV0_EPF0_PCIE_LTR_CAP`, `regPSWUSP0_PCIE_LC_CNTL2`, `regPCIE_LC_CNTL*`, and related strap/link-control registers, using masks from the sibling sh/mask header.
- Doorbell setup code uses NBIO/RCC/S2A doorbell registers from the same generated offset family to route IH, SDMA, VCN, GC, and self-ring doorbells.
- RAS interrupt handling uses BIF doorbell interrupt control registers in the broader file to enable, clear, and process ATHUB error events.

The SMU and DC resource includes are broader integration points: they bring the same NBIO register constants into power-management and display-resource compilation units so generated register-list and platform code can resolve NBIO 4.3.0 symbols.

## Risks and Maintenance Notes

The main risk is silent hardware misaddressing. These macros encode a hardware ABI; a stale generated value, wrong IP-version include, wrong VF number, or wrong base index can compile cleanly while driving a different register.

The chunk has several intentional overlaps. PCI config-space fields smaller than 32 bits share direct register indices, and MSI layouts overlap depending on 32-bit versus 64-bit MSI format. Consumers must use the matching mask/shift definitions and access width assumptions rather than treating every macro name as a distinct DWORD.

The per-VF decode windows are repetitive and easy to misuse. BIF/RCC bases advance by `0x80000` per VF in this range, while the RCC GFX MSI-X table window for each VF is offset into a neighboring `BIFDEC2` range. Copying a VF0 macro where a VF-specific macro is required can affect the wrong function's doorbell, HDP flush, mailbox, or MSI-X state.

The `cfg...` high-address view, per-VF BIF/RCC decode windows, and direct `reg...` SOC15 config views represent different access paths. Code must not substitute `cfgBIF_CFG_DEV0_EPF0_VF12_0_DEVICE_CNTL` for `regBIF_CFG_DEV0_EPF0_DEVICE_CNTL` or vice versa; the prefixes indicate different addressing domains.

This work item has artificial boundaries. It starts in the middle of the VF11 config block and ends in the early direct VF0 block. The final per-file report should reconcile adjacent chunks before making complete statements about VF11 or direct VF0 coverage.

## Test Signals

There are no unit-testable functions in the header. Useful validation signals are build and hardware integration checks:

- Kernel build coverage for `amdgpu/nbio_v4_3.c`, SMU 13 PPT files, and DCN32/DCN321 resource files confirms referenced generated symbols and `_BASE_IDX` macros still resolve.
- NBIO 4.3.0 probe should read revision and memory-size registers correctly, program HDP flush remaps, and avoid hangs in `RREG32_SOC15`/`WREG32_SOC15` accesses using these offsets.
- SR-IOV/VF tests should verify VF enumeration, VF BARs, MSI/MSI-X programming, AER visibility, ARI capability behavior, VF mailbox communication, and VF doorbell aperture routing.
- KFD/graphics workloads should validate HDP coherency flush request/done behavior after `regBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` is used as the remap target.
- PCIe power-management tests should exercise ASPM/LTR programming, link-state transitions, 16 GT/s and 32 GT/s capability reporting, lane equalization, and lane margining status without AER regressions.
- Error-injection or stress tests should watch AER status/log registers, BIF transaction-pending state, mailbox interrupt status, and doorbell interrupt clear/status paths for stuck bits or misrouted interrupts.

### subset-b-002956: lines 7549-10000

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 7549-10000

## Scope

This chunk is part of AMDGPU's generated NBIO 4.3.0 register-offset header. It contains C preprocessor constants that map NBIO/NBIF PCI configuration decoder register names to numeric register offsets, plus paired `_BASE_IDX` selectors for the SOC15/NBIO base-address table.

The covered range starts mid-block in the SR-IOV virtual-function 0 PCIe capability area and ends mid-block in virtual-function 15. It contains 2,392 `#define` lines: 1,196 register-offset constants and 1,196 base-index constants within the requested range, although the final visible `VF15_MSIX_PBA` offset at line 10000 has its `_BASE_IDX` pair just outside this chunk at line 10001. The chunk is declarative hardware metadata; it defines no functions, structs, enums, storage, branches, locks, allocations, or direct MMIO operations.

## Purpose

The purpose of this slice is to publish symbolic addresses for the NBIO 4.3.0 PCI/PCIe configuration-space windows for device 0, endpoint function 0 SR-IOV virtual functions. Driver code and generated register tables can use these `regBIF_CFG_DEV0_EPF0_VF<n>_*` names instead of embedding raw offsets such as `0x18400` or `0x1bc30`.

The repeated macro schema is:

- `regBIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>` for the register offset.
- `regBIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>_BASE_IDX` for the NBIO base selector, which is consistently `5` in this range.

For the complete VF blocks in this chunk, each VF advances by `0x400` in register-offset space. For example, `VF1_VENDOR_ID` is `0x18400`, `VF2_VENDOR_ID` is `0x18800`, and `VF15_VENDOR_ID` is `0x1bc00`. The address-block comments report matching decoded hardware base addresses from `0x10161000` through `0x1016f000`.

## Address Blocks and Register Coverage

The chunk begins in the tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`. Lines 7549-7645 cover the later `VF0` PCIe capability registers from `DEVICE_CNTL`'s base-index pair through link, MSI/MSI-X, vendor-specific, AER, and ARI offsets.

Complete visible address-block starts are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, base address `0x10161000`, starting at line 7648.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf2_bifcfgdecp`, base address `0x10162000`, starting at line 7808.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf3_bifcfgdecp`, base address `0x10163000`, starting at line 7968.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp`, base address `0x10164000`, starting at line 8128.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`, base address `0x10165000`, starting at line 8288.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`, base address `0x10166000`, starting at line 8448.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf7_bifcfgdecp`, base address `0x10167000`, starting at line 8608.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, base address `0x10168000`, starting at line 8768.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf9_bifcfgdecp`, base address `0x10169000`, starting at line 8928.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf10_bifcfgdecp`, base address `0x1016a000`, starting at line 9088.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp`, base address `0x1016b000`, starting at line 9248.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`, base address `0x1016c000`, starting at line 9408.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp`, base address `0x1016d000`, starting at line 9568.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp`, base address `0x1016e000`, starting at line 9728.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp`, base address `0x1016f000`, starting at line 9888.

For complete `VF1` through `VF14`, the repeated register families include:

- Standard PCI header identity/configuration: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, cache-line/latency/header/BIST fields, BARs `BASE_ADDR_1` through `BASE_ADDR_6`, CardBus CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X capability: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI message address/data/mask/pending forms, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- PCIe vendor-specific extended capability: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.
- PCIe Advanced Error Reporting: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable error status/mask/severity registers, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3`, and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`.
- ARI capability: `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

The `VF15` block is partial in this chunk. It starts at `VENDOR_ID` and reaches `MSIX_PBA` at line 10000; vendor-specific, AER, and ARI `VF15` offsets continue immediately after the requested range.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or executable functions in this chunk. The interface is the macro namespace itself.

Important macro families are the `regBIF_CFG_DEV0_EPF0_VF<n>_*` offsets and their `_BASE_IDX` partners. Consumers normally pair these offsets with field definitions in `nbio_4_3_0_sh_mask.h`, where matching names such as `BIF_CFG_DEV0_EPF0_VF0_DEVICE_CNTL` and `BIF_CFG_DEV0_EPF0_VF15_MSIX_PBA` define bit shifts and masks.

The header-level dependency is the include guard established earlier in the file. No local macro in this range computes an address by itself; runtime code must combine the offset with the correct NBIO base/instance mechanism, such as SOC15 register helpers or display `NBIO_BASE(...)` table construction.

## Control Flow

This chunk has no runtime control flow. Compile-time behavior is limited to making the register symbols available to translation units that include `nbio_4_3_0_offset.h`.

The inferred runtime flow for any consumer of these VF offsets is:

1. Select an NBIO 4.3.0 target and include the offset header with the matching shift/mask header.
2. Choose the VF-specific config register symbol for the PCI/PCIe capability being read or programmed.
3. Combine `reg..._BASE_IDX` and `reg...` with the driver register-address helper.
4. Read, write, or update the hardware register using the companion field masks where bit-level access is needed.

In this repository snapshot, direct users of `nbio_4_3_0_offset.h` include `amdgpu/nbio_v4_3.c`, SMU 13.0.0/13.0.7 power-management tables, and DCN 3.2/3.2.1 resource code. The directly inspected implementation code mostly uses non-VF NBIO registers for HDP flush, doorbells, LTR, ASPM, interrupt control, and display NBIO-base table setup; the VF config-space offsets in this chunk are generated address metadata available to SR-IOV, diagnostics, and config-space decode paths rather than obvious direct call-site references in the inspected files.

## State and Persistence Behavior

The header stores no software state and performs no persistence. The state represented by these offsets lives in NBIO hardware and PCIe configuration registers for SR-IOV virtual functions.

Some referenced registers hold configuration that can persist until reset, function-level reset, PF-controlled VF teardown, or guest/host PCI core reprogramming: command bits, BARs, ROM BAR, MSI/MSI-X enable and table/PBA pointers, PCIe device control, link control, completion timeout controls, and ARI controls. Others are status or diagnostic registers, such as device/link status, AER correctable/uncorrectable status, header logs, and TLP prefix logs. The offset header does not encode access policy, read-clear/write-one-to-clear semantics, reset values, privilege restrictions, or PF/VF ownership rules.

Because this is VF config-space address metadata, runtime state can be affected by SR-IOV lifecycle events outside the code that includes this header: PF driver VF enablement, guest driver enumeration, PCI core capability negotiation, FLR, GPU reset, suspend/resume, and virtualization policy.

## Dependencies and Integration Points

The immediate dependency is the C preprocessor. Semantically, this generated file must match AMD's NBIO 4.3.0 register database and the companion `nbio_4_3_0_sh_mask.h` field layout header.

Integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which includes the NBIO 4.3.0 offset/mask pair and uses nearby NBIO registers through `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `WREG32_FIELD15_PREREG`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the same NBIO 4.3.0 headers for SMU-side power-management programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c` and `dcn321_resource.c`, which include `nbio_4_3_0_offset.h` and construct NBIO register addresses with `NBIO_BASE(regBIF_BX0_*_BASE_IDX) + regBIF_BX0_*`.
- Linux PCIe/SR-IOV infrastructure, because these names mirror standard PCI header, PCIe capability, MSI/MSI-X, AER, and ARI register layouts for virtual functions.
- Interrupt routing and virtualization paths through MSI/MSI-X capability offsets and per-VF table/PBA pointers.
- PCIe error handling and diagnostics through AER status/mask/severity and log registers.

## Risks and Edge Cases

- Generated-header drift is the main risk. If an offset or `_BASE_IDX` differs from the NBIO 4.3.0 hardware database, code can compile cleanly while reading or writing the wrong hardware register.
- The chunk boundaries are partial. `VF0_DEVICE_CNTL`'s offset is immediately before this range while its `_BASE_IDX` is inside it, and `VF15_MSIX_PBA`'s `_BASE_IDX` is immediately after this range. The final per-file report should reconcile adjacent chunks before making completeness claims.
- The VF blocks are highly repetitive. A copy-generation error in a VF number, offset stride, or base index would be difficult to detect visually.
- Several registers share the same offset because PCI config registers expose multiple named fields in the same dword, such as `COMMAND`/`STATUS`, `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, MSI address/data aliases, and ARI capability/control aliases. Consumers must use the correct companion masks and preserve unrelated fields.
- The all-`5` base-index pattern is part of the address contract. Accidentally using a PF, non-VF, or different-generation base index would address a different NBIO window.
- Registers named as control fields may trigger visible hardware behavior if written incorrectly, including VF FLR, MSI/MSI-X masking, link retraining/disable behavior, completion-timeout handling, AER masking/severity, and ARI routing.
- The header does not specify access type, privilege, ordering, reset value, or guest/PF ownership. SR-IOV code must respect the PCIe spec, AMD hardware rules, and Linux PCI core ownership.

## Test Signals

Useful validation signals for this chunk are primarily generated-header and integration checks:

- Compile coverage for AMDGPU configurations that include `nbio_4_3_0_offset.h`, especially `nbio_v4_3.c`, SMU 13.0.0/13.0.7, and DCN 3.2/3.2.1 resource code.
- Static consistency checks that every offset macro in the full file has the intended `_BASE_IDX` partner and that every consumed offset has a matching field group in `nbio_4_3_0_sh_mask.h`.
- Pattern checks across `VF1` through `VF14` confirming the expected `0x400` stride, identical register-family ordering, and base index `5`.
- Boundary checks during merge: pair line 7549 with the preceding `VF0_DEVICE_CNTL` offset and line 10000 with the following `VF15_MSIX_PBA_BASE_IDX`.
- Runtime SR-IOV smoke tests on NBIO 4.3.0 hardware: enable VFs, enumerate them, assign or bind drivers, verify BAR sizing, program MSI/MSI-X, and confirm interrupts and reset behavior.
- PCIe capability inspection through kernel logs, debugfs dumps, or tools such as `lspci -vv` to confirm VF PCIe, MSI/MSI-X, AER, and ARI capabilities decode as expected.
- Error-path validation that PCIe AER status/mask/severity and header-log offsets are decoded correctly when errors are injected or observed.

## Chunk Notes

This is only the source-tree-aligned chunk report for `subset-b-002956`. It intentionally does not create a final per-file research document for `nbio_4_3_0_offset.h`; the merge/reconciliation lane should combine this report with adjacent chunks before making complete-file statements.

### subset-b-002957: lines 10001-12430

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 10001-12430

## Scope

This chunk is generated AMD NBIO 4.3.0 register offset metadata. It contains C preprocessor constants only: each `reg*` macro gives a SOC15-style register/config-space index and each matching `*_BASE_IDX` macro gives the base aperture index, which is `5` throughout this range. There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches here.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata, not Ceph filesystem code.

The selected lines cover 2,399 `#define` entries:

- The tail of `BIF_CFG_DEV0_EPF0_VF15`, starting at the MSI-X PBA base-index line and continuing through vendor-specific, AER, TLP prefix log, and ARI capability offsets for virtual function 15.
- The complete visible `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` block at base address `0x10141000`, including normal PCI configuration header registers, MSI/MSI-X, PCIe capability, AER, device serial number, ACS, PASID, ARI, ATS, PRI, LTR, SR-IOV, resize-BAR, and VF resize-BAR capability offsets.
- The `EPF2` block at `0x10142000` and `EPF3` block at `0x10143000`, each with a PCI configuration header, MSI/MSI-X, PCIe capability, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, and ARI offsets.
- RCC port decode blocks for `DEV0_1` at base `0x10131000`, split across common RCC, endpoint, downstream, and downstream-port register groups.
- The beginning of the PCIe MSI-X vector table at base `0x10170000`, defining vectors 0 through 172. Each complete vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` offsets. The file continues with vector 173 after this chunk.

## Purpose

`nbio_4_3_0_offset.h` supplies symbolic register offsets for the NBIO/NBIF/PCIe portion of AMD GPUs using the NBIO 4.3.0 IP. AMDGPU code pairs these offsets with `nbio_4_3_0_sh_mask.h` field macros and SOC15 access helpers so driver code can name hardware registers without embedding raw offsets.

This chunk focuses on the PCIe configuration and interrupt-delivery surface for additional endpoint functions and virtual functions:

- `BIF_CFG_DEV0_EPF*` macros model PCI-compatible configuration-space registers for device 0 endpoint functions 1 through 3 and the tail of physical function 0 virtual function 15.
- MSI and MSI-X capability offsets expose interrupt address/data/mask/pending control for each function.
- AER, device serial, ACS, PASID, ATS, PRI, ARI, LTR, SR-IOV, resize-BAR, power-budget, and DPA capability offsets describe PCIe feature and error-reporting state.
- RCC register offsets expose root-complex/endpoint/downstream-port controls around VDM support, bus/link control, requester-ID restore, LTR, margining, DPA, PME, error control, RX/TX control, link speed, and strap registers for the `DEV0_1` port view.
- `PCIEMSIX_VECTn_*` offsets describe the hardware MSI-X table entries used to route interrupt vectors by programming a message address, message data, and vector control word.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `regBIF_CFG_DEV0_EPF1_*`, `regBIF_CFG_DEV0_EPF2_*`, and `regBIF_CFG_DEV0_EPF3_*` name PCI configuration registers for endpoint functions 1, 2, and 3.
- `regBIF_CFG_DEV0_EPF0_VF15_*` names the final PCIe capability registers for virtual function 15 of endpoint function 0. This chunk starts mid-family, so earlier VF15 header/MSI fields are in the previous chunk.
- `regRCC_DEV0_1_*`, `regRCC_EP_DEV0_1_*`, `regRCC_DWN_DEV0_1_*`, and `regRCC_DWNP_DEV0_1_*` name RCC and PCIe port-control registers for the device 1/port 1 view.
- `regPCIEMSIX_VECT0_*` through `regPCIEMSIX_VECT172_*` name MSI-X vector-table entries. The vector stride is regular: vector `n` starts at `0x1c000 + 4*n`, with address low/high, message data, and control at consecutive DWORD offsets.
- `*_BASE_IDX` is always `5` in this range and must be preserved by SOC15 addressing code.

AMDGPU consumers normally use these offset macros through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and register-table macros. Bit packing and extraction come from the sibling `nbio_4_3_0_sh_mask.h` header, not from this offset file.

High-signal register groups include:

- PCI config header fields: vendor/device ID, command/status, revision/class codes, BARs, ROM BAR, capability pointer, interrupt line/pin, and adapter/vendor capability registers.
- PCIe core capability fields: `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and their PCIe capability 2 variants.
- Interrupt capability fields: MSI capability/control/address/data/mask/pending registers, MSI-X capability/control/table/PBA offsets, and the separate physical MSI-X vector-table offsets.
- Error and logging fields: AER capability list, uncorrectable/correctable error status/mask/severity, AER control, header logs, and TLP prefix logs.
- Virtualization and isolation fields: SR-IOV, VF BAR/VF resize BAR, ATS, PRI, PASID, ACS, and ARI capability/control registers.
- Power-management fields: PMI, LTR, DPA, power-budget, and RCC LTR/PME controls.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU and kernel PCI/interrupt paths:

1. NBIO 4.3.0-specific code includes this offset header and usually `nbio_4_3_0_sh_mask.h`.
2. The driver selects the NBIO hardware block and instance, then passes a `reg*` macro and its base-index information through SOC15 helpers.
3. Runtime code reads or writes the selected NBIO register to initialize PCIe/NBIO features, control doorbells and interrupts, program ASPM/LTR behavior, perform reset/resume setup, or inspect status/error state.
4. For MSI-X delivery, platform and driver code program PCI/MSI-X config state and vector table entries so interrupts target the intended CPU interrupt remapping address/data. The macros in this slice name that hardware table, but do not define the allocation policy or interrupt handling logic.

Concrete integration in this tree includes `amdgpu/nbio_v4_3.c`, which includes this header and uses nearby NBIO offsets for revision ID, memory-size reads, doorbell ranges, interrupt control, clock gating, HDP flush offsets, PCIe index/data access, ROM offset, ASPM/LTR programming, and NBIO initialization. Within this exact chunk, `nbio_v4_3_init_registers()` reads and writes `regRCC_DEV0_EPF2_STRAP2` to clear the `STRAP_NO_SOFT_RESET_DEV0_F2` bit for NBIO 4.3.0 hardware. Other code paths include the same header from SMU 13 PPT files and DCN32/DCN321 resource code, tying these offsets to power-management and display-resource bring-up.

The header does not encode access ordering, config-space side effects, write-one-to-clear rules, interrupt masking semantics, reset persistence, privilege restrictions, or whether a register is firmware-, platform-, or OS-owned. Those rules live in the consuming driver code, PCIe specification behavior, firmware protocols, and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware state in NBIO/NBIF PCIe configuration, RCC port-control, and MSI-X table blocks.

The represented hardware state falls into several categories:

- PCI configuration state that is visible to or coordinated with the OS PCI core: command/status, BARs, ROM BAR, capability lists, device/link controls, MSI/MSI-X controls, AER status/mask/severity, ACS/PASID/ARI/ATS/PRI, SR-IOV, and resize-BAR controls.
- Interrupt routing state: MSI address/data/mask/pending registers, MSI-X table and PBA offsets in config space, and the physical `PCIEMSIX_VECTn_*` table entries. These persist until reprogrammed, function reset, device reset, suspend/resume restore, virtualization handoff, or platform/firmware intervention.
- Link and power state: LTR, DPA, power budget, PME, link speed/control, ASPM-related RCC controls, and strap/margining registers. Some are latched from straps or only valid under specific link/reset states.
- Error and diagnostic state: AER status and log registers, RCC error controls/status, scratch registers, requester-ID restore, RX/TX controls, and link margining/status fields. Some status bits may be sticky or clear-on-write depending on the register definition.
- Virtualization state: VF capability/register windows and SR-IOV/VF BAR controls are sensitive to PF/VF ownership and hypervisor-mediated restore. The chunk starts in the middle of VF15 and covers function-level SR-IOV controls for EPF1.

Persistence is hardware-defined. Configuration and vector-table entries can survive across normal driver operations but are commonly reinitialized during probe, function-level reset, GPU reset, suspend/resume, or SR-IOV transitions. The file does not distinguish read-only, read/write, write-trigger, sticky-status, strap-latched, or reserved registers, so consumers must not infer write safety from the existence of an offset macro.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register family remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h` supplies bitfield masks and shifts for the registers named here.
- Other chunks of `nbio_4_3_0_offset.h` define the rest of EPF0, VF windows, NBIO control/status, doorbell, HDP, interrupt, and remaining MSI-X vector offsets.
- SOC15 helper macros translate `(NBIO block, instance, reg macro)` pairs into actual MMIO/config aperture addresses.
- Linux PCI/MSI-X infrastructure owns parts of config-space and vector programming, while AMDGPU NBIO code programs device-specific controls around it.

Primary integration points are:

- `amdgpu/nbio_v4_3.c`: NBIO initialization, revision/memsize reads, MC access enable, doorbell range programming, interrupt control, HDP flush remapping, clock gating, ASPM/LTR programming, ROM offset reads, and SR-IOV-specific register remap behavior.
- SMU 13 PPT code (`smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`): includes NBIO 4.3.0 offsets for power-management and PCIe/NBIO coordination.
- Display resource code (`dcn32_resource.c` and `dcn321_resource.c`): includes this register family for display/NBIO interaction on matching ASICs.
- Interrupt handling and resume paths: MSI/MSI-X capability and table state interacts with `amdgpu_irq.c`, PCI core MSI-X enable/disable behavior, and SR-IOV/QEMU restore paths.
- Virtualization and reset paths: EPF/VF config registers, SR-IOV capabilities, VF BARs, and `RCC_DEV0_EPF2_STRAP2` affect function reset and VF/PF behavior.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong offset or base index compiles cleanly but sends reads/writes to the wrong PCIe/NBIO register.
- This chunk has artificial boundaries. It starts mid-VF15 and ends mid-MSI-X vector table after vector 172, so the final per-file research must merge adjacent chunks to complete those families.
- All entries here use base index `5`. Code that drops or substitutes the base index can address another SOC15 aperture even if the offset value looks correct.
- Many names are PCI-standard concepts but are exposed through AMD's NBIO MMIO/config aperture. Confusing Linux PCI config-space access with SOC15 NBIO register access can bypass expected ownership or locking.
- MSI-X table entries are high risk. Stale or wrong `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, or `CONTROL` values can lose interrupts, target the wrong interrupt remapping entry, or break resume/SR-IOV interrupt delivery.
- AER status/log registers may be sticky or clear-on-write. Blind writes during diagnostics or reset can lose error evidence.
- SR-IOV, ATS, PRI, PASID, ACS, ARI, and VF BAR registers are isolation-critical. Wrong offsets or unsafe writes can expose DMA isolation bugs, bad requester IDs, broken PASID routing, or incorrect VF memory windows.
- Link-power controls such as LTR, DPA, power budget, PME, link speed, ASPM-related RCC controls, and strap registers are topology- and firmware-sensitive. Incorrect programming may cause link instability, performance loss, or resume failures.
- Repeated EPF2/EPF3 and MSI-X vector layouts invite generator or manual copy errors. Static checks should verify regular spacing and structurally identical families where the hardware requires that.
- Some registers are strap-latched or reset-sensitive. Writing them after boot may not have the intended effect, and some writes may require link quiescence, function reset, or firmware coordination.

## Test Signals

Useful validation signals include:

- Kernel build coverage for AMDGPU paths that include `nbio_4_3_0_offset.h`, especially `nbio_v4_3.c`, SMU 13 PPT files, and DCN32/DCN321 resource code.
- Generated-data comparison against AMD's authoritative NBIO 4.3.0 register database, checking every `reg*` value and `*_BASE_IDX` in this slice.
- Static consistency checks that every offset macro has a matching base-index macro, all entries in this chunk use base index `5`, EPF2 and EPF3 capability layouts stay aligned, and `PCIEMSIX_VECTn_*` offsets keep the regular 4-DWORD stride.
- Cross-checks with `nbio_4_3_0_sh_mask.h` to ensure field masks exist for registers that consumers modify, such as RCC straps, PCIe capability controls, AER fields, and MSI/MSI-X control registers.
- Boot/probe tests on NBIO 4.3.0 hardware confirming PCI enumeration, BAR sizing, MSI/MSI-X enablement, interrupt delivery, doorbells, HDP flush, ROM offset, and memory-size reporting.
- Suspend/resume and GPU reset tests, including SR-IOV VF scenarios, that verify MSI-X vectors are restored and function/config-space state remains consistent.
- PCIe error-injection or AER tests that verify correct uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs.
- Virtualization tests for SR-IOV, VF BAR sizing, PASID/ATS/PRI/ACS/ARI behavior, and guest interrupt delivery.
- Link-power tests for ASPM/LTR/DPA/PME behavior, including high-load PCIe traffic, idle transitions, and resume from low-power states.
- Regression indicators include missing interrupts, MSI-X vectors targeting stale addresses, PCIe AER storms or missing error logs, failed function reset, VF enumeration failures, bad BAR sizing, link retraining instability, resume hangs, or NBIO register access warnings.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002957`. It covers lines 10001-12430 of `nbio_4_3_0_offset.h`. Adjacent chunks are required to complete the preceding `BIF_CFG_DEV0_EPF0_VF15` family and the following `PCIEMSIX_VECT173+` table, and the final per-file document should reconcile this PCIe/config/MSI-X slice with the rest of the NBIO 4.3.0 register map.

### subset-b-002958: lines 12431-14904

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 12431-14904

## Scope

This chunk is a generated AMD NBIO 4.3.0 register offset header segment. It contains only C preprocessor constants: one `reg...` address macro and one matching `reg..._BASE_IDX` macro per visible register. There are no functions, structs, enums, variables, executable branches, loops, locks, allocation paths, or direct MMIO accesses in this range.

The assigned range contains 2,396 `#define` lines: 1,198 register-offset macros and 1,198 base-index macros. It starts in the middle of the PCIe MSI-X table, at `regPCIEMSIX_VECT173_ADDR_LO`, runs through vectors 173-255 and pending-bit-array registers `regPCIEMSIX_PBA_0` through `regPCIEMSIX_PBA_7`, then covers RCC shadow/strap, BIF reset/misc/RAS/RCC/BX, and GDC SION/doorbell offset blocks. The last line is only the next address-block marker, `nbio_nbif0_gdc_GDCDEC`; the `GDCDEC` registers themselves continue after this chunk.

Although this file is under a local `ceph-client` source mirror, the content in this chunk is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish symbolic register addresses for NBIO 4.3.0 blocks so AMDGPU code can use named constants instead of raw MMIO offsets. Each register appears in the generated pattern:

- `reg<NAME>`, the register offset value used by SOC15/NBIO register access helpers.
- `reg<NAME>_BASE_IDX`, the AMDGPU register-base index used to select the correct register aperture for that offset.

Most early NBIF/BIF/RCC registers in this chunk use base index `5`, while the GDC SION and S2A doorbell registers use base index `3`. Runtime code combines these offsets with field definitions from the matching shift/mask header and with generated default-value data where available.

## Important Macro Families

The opening `PCIEMSIX` fragment completes the MSI-X table area that began in an earlier chunk. It defines vector-table entries 173 through 255. Each vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` registers, followed by `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` for the MSI-X pending-bit array at base address `0x10171000`. These symbols are relevant to interrupt-vector programming, vector masking, and pending-bit observation.

The `nbio_nbif0_rcc_shadow_reg_shadowdec` block at base address `0x10130000` defines shadow PCI configuration registers such as `SHADOW_COMMAND`, `SHADOW_BASE_ADDR_1`, `SHADOW_BASE_ADDR_2`, bus-number/latency fields, memory and I/O base/limit registers, and interrupt/pin/cacheline-style shadow fields. These offsets describe the NBIO/RCC shadow image used when hardware or firmware exposes, mirrors, or restores PCI configuration state.

The `nbio_nbif0_bif_swus_SUMDEC` block defines the small SWUS/SUM indirect register window: `SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI`. This is an indirect access surface, so the address constants are only the visible index/data registers; actual target state is selected through values written by consuming code.

The large `nbio_nbif0_rcc_strap_rcc_strap_internal` block at base address `0x10100000` defines many `RCC_STRAP1_*` registers for device, port, and endpoint-function strap state. The visible families include `RCC_DEV0_PORT_STRAP*`, `RCC_DEV0_EPF0_STRAP*`, `RCC_DEV0_EPF1_STRAP*`, and additional `DEV1`/`DEV2` endpoint-function strap registers. These are boot/configuration strap offsets that influence PCIe/NBIO identity, capability, link, function, and virtualization-related hardware behavior.

The `nbio_nbif0_bif_rst_bif_rst_regblk` block defines reset and power-state offsets: hard reset, self soft reset, BIF/GFX/VPU reset controls, reset miscellaneous controls, PF FLR reset controls for device 0 PF0-PF3, reset/power/D3hot interrupt status and mask registers, PF FLR reset request state, per-PF D-state values, D3hot-to-D0 reset controls, and port D-state state. These constants are consumed by reset, FLR, suspend/resume, and power-management paths.

The `nbio_nbif0_bif_misc_bif_misc_regblk` block defines miscellaneous BIF/NBIF control and observation offsets. It includes ROM-offset and BIOS strap control, scratch registers, interrupt line polarity/enable, outstanding VC allocation, `BIFC_MISC_CTRL*`, BME error logs, link-control timers, DMA attribute override registers, SMN master endpoint controls, disconnect hysteresis controls, SHUB sync-flood controls, and BIFC performance counter/latency/debug registers. The adjacent `bif_misc_pfvf` block is present as an address-block marker but has no register macros in this slice.

The `nbio_nbif0_bif_ras_bif_ras_regblk` block defines BIF RAS central control/status, leaf control/status registers, IOHUB RAS interrupt handling, and view-from-IOHUB offsets. These are reliability, availability, and serviceability diagnostic/control registers rather than general data-path registers.

The RCC `BIFDEC1` blocks at base address `0x10120000` define downstream, downstream-port, endpoint, and core RCC PCIe controls. The visible names cover endpoint/downstream scratch/control/config registers, RX/link-speed/link-control registers, LTR message/control offsets, DPA capability/control/substate allocation aliases, PME control, requester ID restore, VDM support, margining parameters, GPU IOV and host-VM enablement, console IOV mode/first-VF/stride fields, peer register ranges, bus/config control, and reset-enablement controls. Several DPA-related symbols intentionally share the same offset because different fields or conceptual registers are packed into the same hardware dword.

The `nbio_nbif0_bif_bx_SYSDEC` block defines the BIF BX1 system register aperture. It starts with PCIE indirect index/data pairs, then defines SBIOS/BIOS/driver/firmware scratch registers, interrupt controls for RLC/VCE/UVD, GFX MMIO register CAM address/remap/control registers, mailbox and scratch-style state, BIF control/status/debug registers, pad controls, save/restore controls, and S5 memory-power controls. These offsets are integration points between firmware, driver, PCIe fabric control, and graphics IP blocks behind NBIO.

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` blocks define PF1-scoped BIF/BX offsets. They include PF MM index/data windows, BME status and atomic error log state, doorbell self-ring GPA aperture high/low/control registers, HDP coherency flush/invalidate controls, GPU HDP flush request/done registers, transaction-pending observation, NBIF/GFX address LUT bypass, and mailbox transmit/receive/control/interrupt registers including `BIF_VMHV_MAILBOX`.

The `nbio_nbif0_rcc_strap_BIFDEC1:1` block defines `RCC_STRAP2_*` BIF/port/EPF strap offsets at the `0x10120000` base, complementing the earlier `RCC_STRAP1_*` internal strap block. It includes BIF strap registers, device 0 port straps, and endpoint-function strap registers for EPF0 and EPF1.

The `nbio_nbif0_gdc_dma_sion_SIONDEC` and `nbio_nbif0_gdc_hst_sion_SIONDEC` blocks define GDC DMA-side and host-side SION quality-of-service/credit programming registers. They repeat per-client-lane (`CL0` through `CL3` for DMA, `CL0` through `CL2` for host in this slice) patterns for read-response, write-response, and request burst targets, time slots, request/data/read-response/write-response pool credit allocation, plus control registers. These constants are likely used when programming NBIO/GDC arbitration, traffic shaping, or fabric credit behavior.

The closing `S2A_DOORBELL` registers define doorbell entry control offsets `S2A_DOORBELL_ENTRY_0_CTRL` through `S2A_DOORBELL_ENTRY_15_CTRL` and `S2A_DOORBELL_COMMON_CTRL_REG`. The next `nbio_nbif0_gdc_GDCDEC` address-block marker appears at the final assigned line, but its register definitions are outside this work item.

## Control Flow

There is no local control flow in this chunk. Runtime behavior appears only in code that includes the generated constants:

1. Driver code selects a `reg...` macro for an NBIO/BIF/RCC/GDC register.
2. It combines the offset with the paired `_BASE_IDX` value through AMDGPU register-address helpers, commonly via `SOC15_REG_OFFSET`-style address construction or generated register accessor macros.
3. It reads, writes, polls, or read-modify-writes the hardware register through AMDGPU MMIO/PCIE access helpers.
4. It applies bit positions and masks from the companion `nbio_4_3_0_sh_mask.h` header when manipulating individual fields.

Typical higher-level flows using these offsets include MSI-X programming, PF/VF reset and FLR handling, PCIe link/power policy, strap interpretation, indirect-register access, RAS status handling, mailbox communication, doorbell aperture configuration, HDP coherency flushes, virtualization/IOV setup, and GDC SION arbitration tuning.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed state in NBIO, BIF, RCC, PCIe, and GDC register blocks. The represented state includes MSI-X vector address/data/control registers, pending interrupt bits, shadow PCI configuration state, strap-derived configuration, reset controls and reset interrupt state, D-state and power-transition state, RAS control/status, PCIe endpoint/downstream/link-control state, scratch and firmware/driver communication registers, mailbox buffers, doorbell controls, HDP flush state, and SION credit/time-slot/traffic-shaping registers.

Some represented registers are static or strap-derived, some are firmware-owned scratch/configuration values, some are driver-programmed controls, some are hardware-updated status, and some may be sticky, write-one-to-clear, or side-effectful. The offset header does not encode access width, reset defaults, required sequencing, locking, ownership boundaries, timeout requirements, or field-level side effects.

## Dependencies And Integration Points

The immediate dependency is the generated NBIO 4.3.0 register database. This header must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h`, which supplies bit shifts and masks for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_default.h`, where generated reset/default values exist for corresponding registers.
- AMDGPU SOC15/NBIO register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Important integration surfaces are AMDGPU NBIO 4.3 support code, PCIe/BIF initialization, MSI-X interrupt setup, SR-IOV and PF/VF virtualization code, reset/FLR and D-state transitions, runtime power management, RAS diagnostics, mailbox paths used by virtualization or firmware coordination, doorbell routing, HDP coherency operations, and GDC/NBIO fabric scheduling. Firmware and platform PCIe policy also intersect with the shadow, strap, scratch, link, LTR, DPA, PME, and BIOS/SBIOS scratch registers.

## Risks And Edge Cases

- The chunk boundaries are artificial. The MSI-X table begins before line 12431, and the `GDCDEC` block begins at the last assigned line but has no register content inside this chunk.
- These are untyped preprocessor constants. A stale or misgenerated offset compiles cleanly but can redirect MMIO to the wrong hardware register.
- The paired `_BASE_IDX` values are as important as the offsets. Using a base index `5` NBIF/BIF/RCC offset through the base index `3` GDC aperture, or the inverse, can access unrelated hardware state.
- Repeated generated families are easy to misuse. MSI-X vector numbers, PF numbers, EPF strap suffixes, client-lane suffixes, and `REG0`/`REG1` SION pairs must be kept aligned with the intended hardware instance.
- Some macros deliberately alias the same offset under different conceptual names, especially DPA substate and control registers. Consumers must use field masks and documented ownership rules rather than assuming one macro name equals one independent dword.
- Reset, FLR, D3hot/D0, power, and link-control registers are sequencing-sensitive. Incorrect writes can wedge PCIe links, interrupt reset flows, or leave functions in inconsistent power states.
- MSI-X vector control and PBA registers affect interrupt delivery. Incorrect vector or PBA handling can lose interrupts, leave vectors masked, or report stale pending state.
- Strap registers may be read-only, latched, firmware-controlled, or only valid at specific phases. Treating strap offsets as normal mutable control registers can produce ineffective writes or undefined behavior.
- RAS status/control registers may be sticky or write-one-to-clear. Generic read/modify/write treatment can clear diagnostic evidence or mask future errors.
- Doorbell, mailbox, HDP flush, and transaction-pending registers cross ownership boundaries between CPU, GPU, firmware, PF, VF, and possibly guests. Missing serialization or timeout handling in consumers can cause lost notifications or hung waits.
- SION credit and time-slot registers influence fabric scheduling. Misprogramming can cause performance regressions, starvation, backpressure, or unstable DMA/host traffic behavior.

## Test Signals

Useful validation is mostly build-time plus hardware integration:

- Build AMDGPU with NBIO 4.3.0 support enabled; missing or renamed macros should surface in NBIO/BIF/GDC/PCIe include paths.
- Compare this offset chunk with `nbio_4_3_0_sh_mask.h` and `nbio_4_3_0_default.h` to confirm register names and generated families remain synchronized.
- On matching hardware, verify MSI-X allocation and interrupt delivery across high vector numbers, including vector masking/unmasking and pending-bit-array behavior.
- Exercise PF FLR, D3hot-to-D0, suspend/resume, runtime power transitions, and PCIe link retraining while checking reset interrupt status/mask handling.
- Validate SR-IOV or virtualization paths that rely on PF1 mailbox registers, VM/HV mailbox state, GPU IOV region controls, first-VF/stride registers, and doorbell aperture programming.
- Run RAS or error-injection diagnostics where available and confirm BIF RAS central/leaf status and IOHUB notification registers map to expected events without clearing evidence prematurely.
- Exercise HDP coherency flush/invalidate paths and confirm `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, and transaction-pending status complete within expected timeouts.
- Run DMA, graphics, compute, and host traffic workloads while changing or validating SION credit/time-slot programming; regressions in throughput, latency, or hangs are signals of GDC SION offset or field drift.
- Validate firmware/BIOS scratch and strap interpretation during boot and resume, especially where SBIOS, firmware, and driver scratch registers are used as handoff state.

## Chunk Notes

- Lines 12431-13113 finish the `PCIEMSIX` vector table from vector 173 through vector 255 and define `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7`.
- Lines 13116-13587 cover RCC shadow, SWUS/SUM, and the large internal `RCC_STRAP1_*` device/port/EPF strap block.
- Lines 13590-13871 cover BIF reset, BIF miscellaneous, an empty PFVF miscellaneous marker, and BIF RAS offsets.
- Lines 13874-14571 cover RCC `BIFDEC1`, BIF BX system/PF/PFVF, and `RCC_STRAP2_*` blocks at base address `0x10120000`.
- Lines 14574-14901 cover GDC DMA SION, GDC host SION, and S2A doorbell control offsets at the `0x1400000` base using base index `3`.
- Line 14904 is only the `nbio_nbif0_gdc_GDCDEC` address-block marker; later chunks must cover that block's actual register offsets.

### subset-b-002959: lines 14905-17348

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 14905-17348

## Scope

This chunk is a generated AMD NBIO 4.3 register-offset header segment. It contains C preprocessor constants only: register/config-space offset macros and matching `_BASE_IDX` macros for selected memory-mapped register blocks. There are no functions, structs, variables, allocations, locks, branches, loops, or direct register reads/writes in this range.

The assigned slice starts at the body of `nbio_nbif0_gdc_GDCDEC` after its address-block label, covers GDC RAS/reset/syshub offsets, then maps a large set of PCIe configuration-space images: the `PSWUSCFG0` upstream bridge, `BIF_CFG_DEV0_RC1`, EPF0 physical function, EPF0 VF0 through VF15, EPF1, EPF2, and the beginning of EPF3. The chunk ends at `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR4_CNTL`, so EPF3 is incomplete here.

Although this source tree is under a local `ceph-client` mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

The purpose of this range is to publish numeric offsets for NBIO 4.3 GDC/NBIF registers and PCIe configuration-space registers. Runtime AMDGPU code uses these constants with generated field masks from the matching `nbio_4_3_0_sh_mask.h` header and with register-access helpers to read, write, decode, or program hardware state.

Two macro forms appear:

- `reg...` macros name memory-mapped NBIO/GDC registers. In this chunk they use base index `3` and offsets under the `0x1400000` NBIO base window.
- `cfg...` macros name PCI/PCIe configuration-space registers. These are offsets inside the corresponding PCI config image and generally do not carry `_BASE_IDX` companions in this slice.

The header provides addresses only. It does not describe bit layouts, reset defaults, access widths, ownership rules, write-one-to-clear behavior, polling requirements, or side effects.

## Important Macro Families

The opening `GDCDEC` tail defines offsets for SHUB/GDC interface and control registers: `regGDC1_SHUB_REGS_IF_CTL`, NGDC memory/clock-gating control, reserved NGDC slots, GFX doorbell status, ATDMA/S2A miscellaneous controls, early wakeup control, and NGDC power-gating master/slave/misc controls. These offsets are integration points for doorbell visibility, data-mover behavior, wakeup, clock gating, and power gating.

The `nbio_nbif0_gdc_ras_gdc_ras_regblk` block defines GDC RAS/error offsets: `regGDCSOC_ERR_RSP_CNTL`, central RAS status, leaf control registers for leaves 0 through 4, leaf 2 misc controls, and leaf status registers. These are used by diagnostics and reliability flows that need to locate error-response control and per-leaf status.

The `nbio_nbif0_gdc_rst_GDCRST_DEC` block maps GDC/SHUB reset controls: PF FLR reset, GFX driver VPU reset, link reset, hard reset, soft reset, SDP port reset, and reset misc trailer. These offsets support reset sequencing and recovery paths, but the header itself does not encode reset ordering or delays.

The `nbio_nbif0_syshub_mmreg_syshubdirect` block contains two host-clock switch/control offsets, `regHST_CLK0_SW0_CL0_CNTL` and `regHST_CLK0_SW1_CL0_CNTL`, for direct syshub host-clock control.

The `nbio_pcie0_pswuscfg0_cfgdecp` block maps a PCIe upstream bridge-style configuration image. It includes standard identity/header fields, bus number and bridge window registers, capability pointers, power-management capability, PCIe capability, device/link capability/control/status registers, MSI registers, subsystem/vendor-specific capability entries, virtual channel and multicast capability registers, device serial number, AER status/mask/severity/logging, secondary PCIe capability, lane error/equalization controls, ACS, and MC registers.

The `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` block maps the root-complex function config image as `cfgBIF_CFG_DEV0_RC1_*`. It contains standard PCI config header fields, bridge window registers, PCIe capability, slot capability/control/status including second-generation slot registers, MSI fields, vendor-specific and AER extended capability registers, VC/MC/ACS/PASID/ARI registers, and several PCIe 16 GT/s extended capability regions such as PL16, link 16 GT, lane equalization, and lane margining.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block maps endpoint physical function 0. It includes Type 0 header fields, BAR1 through BAR6, ROM and capability pointers, PM/PCIe/MSI/MSI-X capabilities, vendor-specific and AER logs, BAR enhanced capability registers, power budget, DPA substate power allocation registers, ACS, PASID, LTR, ARI, SR-IOV capability/control/status and VF resource registers, lane margining, VF resizable BAR registers, and 32 GT/s link registers. This is the richest complete physical-function block in the assigned slice.

The EPF0 VF0 through VF15 blocks are repetitive virtual-function config-space maps. Each VF block covers a compact VF PCIe image: identity/header bytes, BAR1 through BAR6, ROM/capability/interrupt fields, PCIe capability and device/link controls, MSI/MSI-X capability registers, vendor-specific capability registers, AER status/mask/severity and header/TLP prefix logs, and ARI capability/control registers. Each VF block has 78 defines in this slice and uses the same register ordering with a different VF suffix.

The EPF1 physical-function block resembles EPF0 but is smaller in this slice. It covers standard endpoint header fields, PM/PCIe/MSI/MSI-X, vendor-specific and AER logs, BAR enhanced capability, power budget, DPA, ACS, PASID, LTR, ARI, SR-IOV control/status/VF resource registers, and VF resizable BAR registers. It does not include the EPF0-only 16 GT/s/32 GT/s and lane-margining tail visible earlier in the chunk.

The EPF2 physical-function block maps standard endpoint header fields, PM/PCIe/MSI/MSI-X, vendor-specific and AER logs, BAR enhanced capability, power budget, DPA, ACS, PASID, and ARI. It does not include the SR-IOV, LTR, VF resizable BAR, or high-speed link extension coverage present in EPF0/EPF1 within this slice.

The EPF3 physical-function block begins at the end of the chunk and is incomplete. Covered offsets run from vendor/device ID through standard header, PM/PCIe capability, MSI/MSI-X, vendor-specific capability, AER logs, TLP prefix logs, and BAR enhanced capability registers through `PCIE_BAR4_CNTL`. EPF3 BAR5/BAR6, power/DPA, ACS/PASID/ARI, and any later capability offsets are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes and applies the generated constants:

1. AMDGPU selects a macro such as `regGDC1_NGDC_PG_MISC_CTRL`, `cfgBIF_CFG_DEV0_EPF0_1_PCIE_SRIOV_CONTROL`, or `cfgBIF_CFG_DEV0_EPF0_VF15_1_MSI_MSG_DATA`.
2. The selected offset is combined with the correct hardware access path, such as SOC15/NBIO MMIO access for `reg...` offsets or PCIe/config-space access for `cfg...` offsets.
3. Code pairs this offset with bit masks/shifts from generated `*_sh_mask.h` headers, often through helper macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
4. Higher-level flows then program controls, inspect hardware status, poll reset/link bits, set up MSI/MSI-X, expose SR-IOV VFs, decode AER diagnostics, or manage PCIe capabilities.

Typical consumers are NBIO initialization, PCIe link setup and reporting, reset/FLR recovery, RAS/error handling, SR-IOV/MxGPU virtualization, interrupt delivery setup, power-management policy, and display or SMU code that needs NBIO 4.3 register locations.

## State And Persistence Behavior

This file stores no software state and persists nothing. It is generated address metadata for hardware-owned or firmware/platform-owned state.

The represented state includes GDC control/status, NGDC clock/power-gating control, doorbell status, ATDMA/S2A controls, RAS leaf control/status, reset controls, syshub clock controls, bridge and endpoint PCI configuration fields, BAR/resource windows, PM capability state, PCIe link/device capability and control state, MSI/MSI-X address/data/mask/pending registers, vendor-specific capability payloads, AER status/mask/severity/log fields, VC/MC/ACS/PASID/LTR/ARI controls, SR-IOV VF counts/strides/BARs, DPA power allocation, lane equalization/margining, and higher-speed link capability registers.

Some of those hardware fields are static capabilities, some are software-programmed controls, some are live hardware status, and some are sticky diagnostic values. The offset header alone cannot tell whether a register is safe for read/modify/write, whether a status bit is write-one-to-clear, or whether firmware, PCI core, guests, or the PF driver owns a field at a given time.

## Dependencies And Integration Points

This chunk depends on the NBIO 4.3 generated register database staying internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h` supplies the bitfield shifts and masks for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_default.h`, where present for these names, supplies reset/default values.
- AMDGPU register access wrappers and SOC15 register macros supply the actual MMIO/config-space access mechanism and base-index handling.

Direct include points found in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, and `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`.

The most important integration surfaces are the Linux PCI core, AMDGPU NBIO/BIF code, SMU13 power-management code, DCN32/DCN321 display resource code, SR-IOV virtualization paths, MSI/MSI-X interrupt setup, AER reporting, reset and FLR handlers, suspend/resume, runtime power management, and platform firmware that may preconfigure parts of PCIe config space before the driver runs.

## Risks And Edge Cases

- The chunk boundaries are artificial. The assigned range starts immediately after the `nbio_nbif0_gdc_GDCDEC` address-block label and ends in the middle of EPF3's BAR enhanced capability map, so adjacent chunks are required for full GDCDEC and EPF3 analysis.
- These are untyped preprocessor constants. A stale or duplicated offset can compile successfully while sending register traffic to the wrong hardware location.
- The PCIe config-space blocks are highly repetitive. Suffix mistakes among `RC1`, `EPF0_1`, `EPF0_VF*_1`, `EPF1_1`, `EPF2_1`, and `EPF3_1` can silently target the wrong function or virtual function.
- `reg...` offsets use NBIO base-index semantics, while `cfg...` offsets are config-space offsets. Mixing the access paths can produce plausible-looking constants with incorrect hardware effects.
- Reset-related offsets are hazardous if used without the hardware sequence from driver code or firmware documentation. Wrong ordering around PF FLR, hard reset, soft reset, link reset, or SDP port reset can strand devices or lose diagnostic evidence.
- RAS/AER registers may contain sticky or write-one-to-clear fields. Generic read/modify/write code can clear error evidence, leave errors masked, or report the wrong severity.
- MSI/MSI-X offsets include aliases for 32-bit and 64-bit MSI layouts. Incorrect width assumptions can misprogram interrupt address/data, masks, or pending bits.
- BAR, VF BAR, and SR-IOV offsets affect resource exposure and guest-visible virtual functions. Incorrect offsets can break enumeration, isolate resources incorrectly, or expose invalid apertures.
- PCIe link, equalization, margining, power budget, DPA, LTR, ACS, PASID, and ARI controls are platform-sensitive. Bad programming can cause link instability, DMA ordering/security issues, IOMMU/ATS problems, poor power behavior, or virtualization isolation failures.
- EPF3 is only partially visible in this chunk; claims about EPF3's complete capability chain require the next chunk.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3 support enabled; missing or renamed macros should surface in `nbio_v4_3.c`, SMU13, or DCN32/DCN321 include paths.
- Compare generated `nbio_4_3_0_offset.h`, `nbio_4_3_0_sh_mask.h`, and `nbio_4_3_0_default.h` for the same register names so offsets, masks, and defaults remain aligned.
- Boot affected NBIO 4.3 ASICs and verify PCI enumeration: bridge windows, endpoint BARs, capability lists, MSI/MSI-X, AER, ACS/PASID/ARI, SR-IOV, and VF resource fields should decode consistently.
- Exercise SR-IOV creation/removal across EPF0 VF0 through VF15 and validate VF config access, VF BAR sizing, MSI/MSI-X delivery, ARI behavior, FLR, and guest bind/unbind paths.
- Run reset and recovery tests covering PF FLR, link reset, hard reset, soft reset, and suspend/resume while checking that devices re-enumerate and that RAS/AER state is not lost unexpectedly.
- Run graphics, display, compute, and DMA workloads with interrupt traffic enabled; lost interrupts or stuck pending bits can indicate MSI/MSI-X offset or alias mistakes.
- Use PCIe diagnostics or error injection where available to verify AER status, masks, severity, header logs, TLP prefix logs, and GDC RAS leaf status reporting.
- Exercise link retraining, high-speed link modes, equalization, and lane margining on hardware paths that expose the EPF0/RC extended capability offsets in this chunk.

## Chunk Notes

- Lines 14905-14927 cover the in-progress `nbio_nbif0_gdc_GDCDEC` block body, including 11 value macros and 11 `_BASE_IDX` macros.
- Lines 14930-14987 cover complete GDC RAS, GDC reset, and syshub-direct mini-blocks.
- Lines 14988-15177 cover the complete `PSWUSCFG0` upstream bridge config image visible in this file segment.
- Lines 15178-15359 cover the `BIF_CFG_DEV0_RC1` root-complex config image.
- Lines 15360-15625 cover the EPF0 physical-function config image, including SR-IOV, VF resizable BAR, margining, and 32 GT/s link offsets.
- Lines 15626-16937 cover complete repeated EPF0 VF0 through VF15 config images.
- Lines 16938-17128 cover the EPF1 physical-function config image through VF resizable BAR offsets.
- Lines 17129-17254 cover the EPF2 physical-function config image through ARI offsets.
- Lines 17255-17348 begin EPF3 and stop at `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR4_CNTL`; later EPF3 offsets are outside this chunk.

### subset-b-002960: lines 17349-17381

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 17349-17381

## Scope

This chunk is the final 33-line tail of the generated AMDGPU NBIO 4.3.0 offset header. It contains C preprocessor constants only, followed by the closing `#endif` for `_nbio_4_3_0_OFFSET_HEADER`. There are no C functions, structs, enums, variables, locks, allocations, loops, or executable statements in this range.

The range starts in the middle of the `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR*` extended-capability block, covering BAR5/BAR6, power-budgeting, Dynamic Power Allocation, ACS, PASID, and ARI offsets for `BIF_CFG_DEV0_EPF3_1`. The immediately preceding lines contain the start of the same endpoint-function PCIe capability sequence, including BAR1-BAR4 and AER/TLP diagnostic offsets.

Although this repository path is under a `ceph-client` mirror, this file is AMD GPU register metadata for DRM/AMDGPU. It has no direct Ceph distributed-filesystem behavior.

## Purpose

`nbio_4_3_0_offset.h` publishes generated register/configuration-space addresses for the NBIO 4.3.0 IP block. This chunk supplies the tail of the PCIe extended-capability offset map for device 0, endpoint function 3, instance 1:

- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR5_CAP` through `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR6_CNTL` identify BAR sizing and BAR-control capability registers at offsets `0x0224` through `0x0230`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_PWR_BUDGET_*` identifies the PCIe power-budgeting extended capability at `0x0240` through `0x024c`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_DPA_*` identifies Dynamic Power Allocation capability, status/control, and per-substate power-allocation bytes at `0x0250` through `0x0267`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_ACS_*` identifies Access Control Services capability and control offsets at `0x02a0` through `0x02a6`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_PASID_*` identifies PASID capability and control offsets at `0x02d0` through `0x02d6`.
- `cfgBIF_CFG_DEV0_EPF3_1_PCIE_ARI_*` identifies Alternative Routing-ID Interpretation capability and control offsets at `0x0328` through `0x032e`.

The matching field layouts live in `nbio_4_3_0_sh_mask.h`. Runtime consumers combine these offset macros with shift/mask macros and AMDGPU register/config access helpers. This offset header does not define register field width, access permissions, reset values, side effects, or ordering requirements.

## Important APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace itself. Consumers use the constants as hardware ABI names.

The source tree includes `nbio_4_3_0_offset.h` together with `nbio_4_3_0_sh_mask.h` in NBIO, SMU, and display code, including:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which uses NBIO 4.3.0 register definitions with helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and `REG_SET_FIELD`.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the NBIO 4.3.0 register headers for power-management integration.
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c` and `dcn321_resource.c`, which include the same offset header for display-resource code on matching ASICs.

The exact macros in this slice are not directly referenced by non-generated C code in the observed tree, but they remain part of the generated ASIC register contract. They may be consumed by generic register helpers, debug tooling, generated tables, or downstream code that programs or decodes endpoint-function PCIe config space.

## Control Flow

This header has no local control flow. The effective runtime pattern is external:

1. ASIC-specific AMDGPU code includes the NBIO 4.3.0 offset and shift/mask headers.
2. A caller selects one of these `cfgBIF_CFG_DEV0_EPF3_1_*` offsets when it needs to read, write, expose, or decode PCIe configuration space for endpoint function 3.
3. The caller applies companion shift/mask macros from `nbio_4_3_0_sh_mask.h`, or a PCI/NBIO accessor, to extract fields, compose values, clear sticky bits, or program controls.
4. Hardware, firmware, PCI core, IOMMU, virtualization, or power-management logic observes the resulting PCIe capability state.

The ordering and safety rules are determined by the consuming driver path and the PCIe/NBIO hardware specification, not by this generated header.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It names hardware-visible configuration and capability registers. Persistence is therefore governed by GPU reset domains, PCI config-space save/restore, firmware initialization, suspend/resume, function-level reset, hot reset, and explicit driver or firmware writes.

The represented hardware state includes BAR capability/control metadata, power-budget selection/data, DPA capability and substate allocation state, ACS isolation controls, PASID enablement, and ARI function-routing controls. Some registers are static capability descriptors, some are host- or firmware-programmed controls, and some may be hardware-updated status. The offset macros do not distinguish read-only capability fields from read/write controls, sticky status, or command fields.

## Dependencies And Integration Points

The direct dependencies are the sibling generated NBIO 4.3.0 headers:

- `nbio_4_3_0_sh_mask.h` supplies field shifts and masks for these register names. For example, the companion masks define BAR size-supported fields, power-budget data fields, DPA substate and latency fields, ACS capability/control bits, PASID controls, and ARI controls.
- Other generated NBIO 4.3.0 headers, where present, provide related defaults or register metadata outside this offset-only file.

The broader integration points are AMDGPU NBIO initialization, SMU power-management code, PCIe capability exposure, PCI resource/BAR handling, AER and RAS diagnostics in adjacent lines, IOMMU/PASID integration, SR-IOV or multi-function routing, and isolation features such as ACS. These offsets are tied to the NBIO 4.3.0 generation; similar names exist in NBIO 2.3, 7.x, and other generated headers, but their offset encoding and base-index model can differ.

## Risks And Edge Cases

- Generated offset drift can compile cleanly if macro names remain stable but values change incorrectly. The driver would then access the wrong PCIe config register.
- This chunk starts inside a capability sequence. BAR1-BAR4 and prior AER/TLP-prefix offsets are in the preceding chunk, so the final per-file report should merge adjacent chunks before describing the complete `EPF3_1` endpoint-function layout.
- The offsets are byte-oriented PCIe config offsets, including halfword and byte registers such as DPA control and substate allocation entries. Consumers must use access sizes and alignment rules appropriate to PCI configuration space.
- BAR capability/control offsets affect resource sizing and aperture exposure. Incorrect use can corrupt enumeration, BAR sizing, or resource assignment.
- Power-budget and DPA registers affect power management and platform power reporting. Wrong offsets or field interpretation can cause misleading power capability data or incorrect substate control.
- ACS, PASID, and ARI are isolation and routing sensitive. Misprogramming these registers can affect peer-to-peer forwarding, IOMMU translation tagging, process address-space IDs, function enumeration, and virtualization boundaries.
- The closing `#endif` means this is the physical end of the generated header. Any accidental truncation before this point would break the include guard and likely fail compilation; accidental edits after it might be ignored or create duplicate-definition hazards.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with NBIO 4.3.0 support enabled. Include-guard damage, missing macros, or syntax drift should surface at compile time.
- Run generated-register consistency checks against the authoritative NBIO 4.3.0 register database, verifying the offset sequence from BAR5/BAR6 through ARI and the closing header structure.
- Boot affected AMD GPUs and confirm PCI config-space enumeration, capability-chain traversal, BAR sizing, and endpoint-function resource reporting remain stable.
- Exercise SMU and power-management paths on matching ASICs, checking that PCIe power budgeting and DPA-related reporting do not regress.
- Validate IOMMU/PASID and ACS behavior under workloads that use process address spaces, peer-to-peer traffic restrictions, or virtualization-sensitive routing.
- Check ARI and multi-function enumeration paths where endpoint function 3 is visible, especially after suspend/resume and function reset.

## Chunk-Specific Notes For Merge

Merge this chunk with the preceding `nbio_4_3_0_offset.h` chunks before producing the final per-file research document. Preserve that this slice covers only the tail of `cfgBIF_CFG_DEV0_EPF3_1` PCIe extended-capability offsets, from BAR5 capability at `0x0224` through ARI control at `0x032e`, and the file-closing `#endif`.
