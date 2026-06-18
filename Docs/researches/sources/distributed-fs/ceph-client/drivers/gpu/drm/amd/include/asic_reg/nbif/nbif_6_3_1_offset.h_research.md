# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002872`: lines 1-2492, `Docs/researches/chunks/subset-b-002872_research.md`
- `subset-b-002873`: lines 2493-4953, `Docs/researches/chunks/subset-b-002873_research.md`
- `subset-b-002874`: lines 4954-7387, `Docs/researches/chunks/subset-b-002874_research.md`
- `subset-b-002875`: lines 7388-10021, `Docs/researches/chunks/subset-b-002875_research.md`
- `subset-b-002876`: lines 10022-11287, `Docs/researches/chunks/subset-b-002876_research.md`

## Chunk Research

### subset-b-002872: lines 1-2492

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h lines 1-2492

## Purpose

This chunk is the opening generated register-offset header for AMD NBIF/NBIO version 6.3.1. It has no executable logic; it exports preprocessor constants that map PCI configuration-space fields and NBIF/RCC/GDC MMIO register names to numeric offsets. The sibling `nbif_6_3_1_sh_mask.h` supplies the bit masks and shifts for these names, while driver code such as `amdgpu/nbif_v6_3_1.c` combines these offsets with SOC15 access macros (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`) to read and program the NBIF block.

The file starts with AMD's MIT-style license and an include guard (`_nbif_6_3_1_OFFSET_HEADER`). Within this chunk, the definitions are organized by generated `addressBlock` comments. The early half uses `cfg...` byte offsets for PCI config-space layouts, and the later half begins the `reg...` MMIO/indexed-register view with matching `_BASE_IDX` constants.

## Exported API Surface

The only API is macro definitions:

- `cfg...` constants: byte offsets inside PCI configuration-space capability layouts. Examples include `cfgBIF_CFG_DEV0_EPF0_VENDOR_ID` at `0x0000`, `cfgBIF_CFG_DEV0_EPF0_COMMAND` at `0x0004`, PCIe capability offsets, MSI/MSI-X offsets, AER offsets, SR-IOV offsets, DPA offsets, ACS/PASID/LTR/ARI offsets, and BAR/resize-BAR capability offsets.
- `reg...` constants: register indexes used by AMD's generated SOC15 register-access helpers. These are paired with `reg..._BASE_IDX` macros that select a base segment from the NBIO/NBIF register-base table.
- `_BASE_IDX` constants: base selector metadata required by macros that compute `base[BASE_IDX] + reg`. In the visible chunk, base indices include `0` and `1` for indexed PF/SYS windows, `2` for many BIFDEC/RCC/GDC windows, `3` for the GFX MSI-X table window, and `5` for direct config-space MMIO apertures starting at `0x10100000`, `0x10140000`, and `0x10160000`.

There are no types, functions, structures, inline helpers, global variables, or callbacks in this chunk.

## Register Groups Covered

Lines 27-35 define the root-complex config block `nbif_bif_cfg_dev0_rc_bifcfgdecp`, currently just `cfgIRQ_BRIDGE_CNTL` at config offset `0x003e`.

Lines 32-286 define the PF0 endpoint-function config layout. This is a broad PCI/PCIe config map covering standard header registers, BARs, ROM base, interrupt line/pin, vendor/PM capability, PCIe capability, MSI/MSI-X, vendor-specific enhanced capability, virtual channel capability, device serial number, AER header/status/log registers, BAR enhanced capability, power budget, DPA, secondary PCIe capability, per-lane equalization, ACS, PASID, LTR, ARI, SR-IOV, data-link feature, 16 GT/s PHY/equalization, lane margining, VF resize BAR, and 32 GT/s link registers. This PF0 block is the richest config definition in the chunk and establishes the pattern repeated later in direct-MMIO form.

Lines 287-942 define virtual-function config layouts for `VF0` through `VF7` under `EPF0`. These VF blocks repeat the standard config header, PCIe capability, MSI/MSI-X, vendor-specific capability, AER status/logging, TLP prefix logs, and ARI capability. They are intentionally smaller than the PF block: PF-only capabilities such as SR-IOV setup and many power/budget/resize resources are absent from these early `cfg...` VF maps.

Lines 943-1122 define `EPF1` config offsets. This mirrors much of PF0's endpoint function layout, including standard header, PM/PCIe capabilities, MSI/MSI-X, vendor-specific capability, device serial number, AER, BAR controls, power budget, DPA, secondary PCIe, lane equalization, ACS, PASID, LTR, ARI, SR-IOV, and VF resize BAR registers.

Lines 1123-1137 define PF indirect MMIO/RSMU index/data registers (`regBIF_BX_PF0_MM_INDEX`, `regBIF_BX_PF0_MM_DATA`, `regBIF_BX_PF0_MM_INDEX_HI`, plus RSMU equivalents). These are the register-entry points for indirect accesses rather than PCI config bytes.

Lines 1139-1328 define the `nbif_bif_bx_SYSDEC` register set. It includes PCIe index/data windows, SBIOS/BIOS scratch registers, RLC/VCE/UVD interrupt controls, GFX MMIO register CAM address/remap pairs, doorbell and MMIO remap support, interrupt/SMN client error controls, static arbiter settings, and interrupt counter/endpoint interrupt source registers. Driver code can use these to expose firmware scratch state, program remap windows, or route NBIF-generated interrupts.

Lines 1329-1367 define downstream RCC/NBIF control registers such as EP-to-RCC transfer pending, master/slave stop requests, clock request gating, and EDB write response/send controls.

Lines 1369-1443 define endpoint RCC/PCIe controls for device 0. These include PCIe scratch/control/status, RX/TX controls, bus/config controls, LTR control, F1 and F0 DPA substate power allocation fields, strap misc registers, PME control, requester ID, error control, and link speed control.

Lines 1445-1531 define the main BIF block controls. Important offsets include strap/pinstrap, indirect MMIO access control, bus control, BIF scratch registers, reset enable/control, interrupt control, CLKREQ/PERST/PX/refclk/power-break pad controls, feature/misc control, HDP atomic misc control, doorbell control and interrupt control, framebuffer read/write enable, BACO control and exit timers, memory type control, HDP flush remap registers, a BIF ring-buffer window, mailbox index, MP1 interrupt control, and VF master/slave pending state.

Lines 1533-1620 define RCC device-level controls: error interrupt control, BACO/reset/VDM/margining/GPUIOV/HostVM/console IOV controls, peer register ranges, config aperture registers, XDMA address registers, bus number capture/list controls, peer FB offsets, device/function number lists, common/dev0 link controls, requester ID restore, LTR switch control, and memory-hub arbitration.

Lines 1621-1657 define the EPF0 GFX MSI-X table window. It exposes four vector entries (`ADDR_LO`, `ADDR_HI`, `MSG_DATA`, `CONTROL`) and a PBA register. These are `reg...` offsets with base index `3`, distinct from the main BIFDEC base-index `2` registers.

Lines 1659-1751 define RCC strap registers for global BIF straps, device-port straps, and EPF0/EPF1 straps. `nbif_v6_3_1.c` reads `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and masks it with fields from the sibling mask header to derive the ATI revision ID.

Lines 1753-1815 define PF/VF-facing BIF controls: BME status, PF/VF mailbox message registers, FLR request/response controls, host reset select, doorbell self-ring GPA aperture registers, and VF doorbell BAR aperture controls.

Lines 1817-1875 define GDC and GDC S2A doorbell controls. The S2A block has 16 `S2A_DOORBELL_ENTRY_*_CTRL` registers plus common/status registers. `nbif_v6_3_1.c` uses these offsets for GC, SDMA, and VCN doorbell range programming.

Lines 1877-2492 start the direct MMIO config-space view. The root bridge gets `regIRQ_BRIDGE_CNTL` at base address `0x10100000`. EPF0 then starts at base address `0x10140000`, represented by `regBIF_CFG_DEV0_EPF0_*` constants beginning at register index `0x10000` with base index `5`. This direct view packs byte-sized and word-sized PCI config fields into DWORD register indexes, so multiple logical fields can share one register index; for example vendor/device IDs share `0x10000`, command/status share `0x10001`, DPA substate allocations are grouped four per DWORD, lane equalization pairs share DWORDs, and several status/control halves share the same register index. The visible direct EPF0 range reaches 32 GT/s link status by line 2387 and then begins the direct `VF0` config view at base address `0x10160000`, with VF0 register indices beginning at `0x18000`.

## Control Flow and State Behavior

There is no runtime control flow in this file. Control flow is external: AMDGPU code chooses a register constant, passes it through SOC15 access macros with the NBIO hardware instance, and the macro combines the register offset with an IP-version-specific base table. In this pattern, the `_BASE_IDX` constants are as important as the offset values because the same logical register name can land in different address segments.

The header itself holds no mutable state and performs no persistence. The state represented by these macros is hardware state: PCI configuration registers, doorbell aperture controls, scratch registers, reset controls, interrupt controls, SR-IOV/VF configuration, BACO power-state controls, and per-lane PCIe training/margining status. Writes through these offsets persist only in the device register file until hardware reset, power-state transition, FLR, driver reinitialization, or firmware/hardware ownership changes.

## Dependencies and Integration Points

This header depends only on the C preprocessor and its include guard. The effective dependency pair is `nbif_6_3_1_offset.h` plus `nbif_6_3_1_sh_mask.h`; offsets without matching masks are useful for raw reads/writes but not for field-safe programming.

Direct include users found in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes both offset and mask headers and uses visible chunk macros for revision-id detection, framebuffer access enable, memory-size reads, HDP flush remap setup, doorbell aperture/range setup, GDC S2A doorbell programming, BIF reset/interrupt/power controls, and other NBIF operations.
- `drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`, which includes this offset header alongside DCN register headers. The DC resource code uses register-list expansion macros that rely on the `reg...`/`reg..._BASE_IDX` convention.

The generated names also align with nearby NBIO-generation headers (`nbio_4_3_0_offset.h`, `nbio_7_2_0_offset.h`, `nbio_7_7_0_offset.h`, `nbio_7_9_0_offset.h`, `nbio_7_11_0_offset.h`), but values can differ by generation. Consumers should include the IP-specific header selected by the owning implementation, not hard-code cross-generation assumptions.

## Risks and Maintenance Notes

The main risk is silent hardware misprogramming from stale or wrong offsets. These values describe register contracts, so a wrong number can redirect a read/write to a different hardware register with symptoms ranging from feature disablement to device hangs.

The chunk contains overlapping logical fields at the same offset/register index. This is expected for PCI config fields smaller than 32 bits and for packed capabilities, but it means consumers must use the correct mask/shift definitions and access width assumptions. Treating every macro as a unique DWORD register would be incorrect.

The `cfg...` byte-offset view and `reg...` direct register-index view are related but not interchangeable. For example, config byte offset `0x0000` becomes direct register index `0x10000` in the EPF0 MMIO view, while fields at byte offsets `0x0000` and `0x0002` share that DWORD register. Code must use the access path expected by the macro prefix and local AMDGPU helper.

Version-specific deltas are visible in consumers: `nbif_v6_3_1.c` has local `_nbif_4_10` override definitions for some doorbell and strap offsets when `NBIO_HWIP` is `IP_VERSION(7, 11, 4)`. That indicates these generated constants are not universally correct for all closely related hardware revisions and that runtime version checks may be required around sensitive offsets.

The line range ends in the middle of the direct VF0 config block. Later chunks must continue VF0 and the remaining VF/direct config blocks before a whole-file report can make complete statements about all exported macros in the header.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are integration and hardware-facing:

- Build coverage for `amdgpu/nbif_v6_3_1.c` and DCN401 resource code, ensuring all referenced `reg...`, `_BASE_IDX`, mask, and shift macros resolve.
- Compile-time detection of missing or renamed generated macros when regenerating ASIC headers.
- Runtime smoke tests on matching AMD hardware: probe succeeds, NBIF revision ID is read correctly from `RCC_DEV0_EPF0_STRAP0`, framebuffer access can be enabled/disabled through `BIF_FB_EN`, memory size reads from `RCC_CONFIG_MEMSIZE`, doorbell aperture/range setup works for GC/SDMA/VCN, and no unexpected PCIe/AER errors appear during initialization.
- SR-IOV-specific validation for PF/VF config offsets: VFs enumerate with the expected IDs/capabilities, VF BAR/resize-BAR/SR-IOV configuration is coherent, FLR mailbox paths function, and VF doorbell BAR apertures are correctly routed.
- Power-management and reset validation around BACO, FLR, PME, DPA, LTR, and link-speed/equalization registers, since many visible offsets participate in low-power and PCIe link-state transitions.

### subset-b-002873: lines 2493-4953

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h lines 2493-4953

## Scope

This chunk covers a generated AMD NBIF 6.3.1 register-offset header section. It starts in the tail of the `nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp` block at the VF0 MSI/MSI-X, vendor-specific, AER, TLP-prefix, and ARI capability offsets. It then covers full SR-IOV VF1 through VF7 PCI configuration-space register windows, endpoint-function blocks EPF1 through EPF3, root-complex control blocks, power-function-control blocks for `AMDGFX` and `AMDGFXAZ`, and the first 33 entries of the PCIe MSI-X table block.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct MMIO operations. Its interface is the generated offset pair convention:

- `reg<REGISTER_NAME>` gives a SOC15-style register index.
- `reg<REGISTER_NAME>_BASE_IDX` gives the base index, `5` for every register in this chunk.

The chunk contains 1,197 register-name macros, or 2,394 `#define` lines when including the matching `_BASE_IDX` definitions.

## Purpose

`nbif_6_3_1_offset.h` is the address side of the NBIF 6.3.1 hardware ABI. NBIF/NBIO code uses these symbols with SOC15 register helpers to address PCIe/NBIF registers without open-coded offsets. This chunk is centered on PCI configuration and PCIe control surfaces for physical and virtual endpoint functions:

- SR-IOV virtual functions under EPF0, especially VF1 through VF7.
- Additional endpoint functions EPF1 through EPF3.
- RCC endpoint/downstream/root-complex controls for bus, link, LTR, requester ID, strap, DPA, PME, RX/TX, and error-control state.
- RCC power-function-controller restore/LTR/aux-power registers for graphics functions.
- MSI-X table entries for interrupt message address, data, and vector control.

Consumers pair these offsets with `nbif_6_3_1_sh_mask.h` field definitions and generic AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

## Important Macro Families

### VF0 Tail and VF1-VF7 SR-IOV Config Blocks

The opening lines complete the VF0 capability area from `regBIF_CFG_DEV0_EPF0_VF0_MSI_PENDING_64` through `regBIF_CFG_DEV0_EPF0_VF0_PCIE_ARI_CNTL`. This is a boundary fragment; the standard/header and early capability offsets for VF0 are in the previous chunk.

The full VF1 through VF7 blocks are regular repeated config-space maps with 0x400 spacing:

- VF1: `regBIF_CFG_DEV0_EPF0_VF1_VENDOR_ID` at `0x18400` through `regBIF_CFG_DEV0_EPF0_VF1_PCIE_ARI_CNTL` at `0x184cb`.
- VF2: `0x18800` through `0x188cb`.
- VF3: `0x18c00` through `0x18ccb`.
- VF4: `0x19000` through `0x190cb`.
- VF5: `0x19400` through `0x194cb`.
- VF6: `0x19800` through `0x198cb`.
- VF7: `0x19c00` through `0x19ccb`.

Each VF block exposes the expected PCI config registers: vendor/device ID, command/status, class and revision IDs, cache-line/latency/header/BIST, BAR1-BAR6, CIS pointer, subsystem/adapter ID, ROM base, capability pointer, interrupt line/pin/min-grant/max-latency, PCIe capability, device/link cap/control/status, MSI, MSI-X, vendor-specific extended capability, AER status/mask/severity/header logs, TLP-prefix logs, and ARI capability/control. These are offsets only; bit meanings live in the matching shift/mask header and PCIe specs.

### EPF1-EPF3 Endpoint Function Config Blocks

The chunk covers three physical endpoint-function config blocks:

- EPF1 under `nbif_bif_cfg_dev0_epf1_bifcfgdecp`, base address `0x10141000`, with register indices `0x10400` through `0x1053c`.
- EPF2 under base `0x10142000`, with register indices `0x10800` through `0x108cb`.
- EPF3 under base `0x10143000`, with register indices `0x10c00` through `0x10ccb`.

EPF1 is larger than EPF2 and EPF3. In addition to common PCI/PCIe config registers, it includes vendor capability, PMI/PME controls, device serial number capability, BAR enhanced capability, power budget, dynamic power allocation, ACS, PASID, ARI, SR-IOV standard fields (`PCIE_SRIOV_*`), and VF BAR/resize BAR control registers. EPF2 and EPF3 cover the common PCI/PCIe, MSI/MSI-X, vendor-specific, AER, BAR, power budget, DPA, ACS, PASID, and ARI register families but do not include the SR-IOV VF management tail present in EPF1 in this range.

### RCC Root/Endpoint/Downstream Control Blocks

The root-complex control region begins at `nbif_rcc_dev0_RCCPORTDEC`, base `0x10131000`, and includes `regRCC_DEV0_1_RCC_VDM_SUPPORT` through `regRCC_DEV0_1_RCC_MARGIN_PARAM_CNTL1`. These offsets cover RCC VDM support, bus control, feature control, device/common link control, endpoint requester-ID restore, LTR switch control, multi-host arbitration, and link-margining parameters.

The `nbif_rcc_ep_dev0_RCCPORTDEC` block maps endpoint-side PCIe controls from `regRCC_EP_DEV0_1_EP_PCIE_SCRATCH` through `regRCC_EP_DEV0_1_EP_PCIE_LC_SPEED_CNTL`. It includes scratch/control/status, interrupt control/status, RX/TX controls, bus/config controls, TX LTR control, strap state, DPA capability/control/substate allocation, PME control, requester ID, and error control.

The downstream blocks map `regRCC_DWN_DEV0_1_*` and `regRCC_DWNP_DEV0_1_*` registers for downstream PCIe scratch/control/config/RX/bus/strap state plus downstream-port error, link speed/control, strap, and LTR-message state.

### RCC Power Function Controller Blocks

Two similar PFC blocks are present:

- `nbif_rcc_pfc_amdgfx_RCCPFCDEC`, base `0x10134000`, `regRCC_PFC_AMDGFX_RCC_PFC_LTR_CNTL` through `regRCC_PFC_AMDGFX_RCC_PFC_AUXPWR_CNTL`.
- `nbif_rcc_pfc_amdgfxaz_RCCPFCDEC`, base `0x10134200`, `regRCC_PFC_AMDGFXAZ_RCC_PFC_LTR_CNTL` through `regRCC_PFC_AMDGFXAZ_RCC_PFC_AUXPWR_CNTL`.

Both contain LTR control, PME restore, six sticky-restore registers, and auxiliary-power control. These registers are persistence-sensitive because they represent state that may need to survive or be restored across PCIe power-management transitions.

### PCIe MSI-X Table Entries

The final block, `nbif_pciemsix_0_usb_MSIXTDEC` at base `0x10178000`, starts the MSI-X table with repeated vector entries:

- `regPCIEMSIX_VECT<n>_ADDR_LO`
- `regPCIEMSIX_VECT<n>_ADDR_HI`
- `regPCIEMSIX_VECT<n>_MSG_DATA`
- `regPCIEMSIX_VECT<n>_CONTROL`

This chunk covers complete vectors 0 through 31 and ends at `regPCIEMSIX_VECT32_CONTROL` at `0x1e083`. The next chunk must be consulted before making a complete table-size claim.

## Control Flow and State Behavior

There is no executable control flow in this header. Its effect is compile-time substitution of hardware register indices used by driver code. Runtime behavior is created by the code that reads or writes these offsets through SOC15 helpers.

The represented state is hardware register state, not software-owned persistent data. Important state classes include:

- PCI config-space identity and enumeration state for VFs and endpoint functions.
- BAR layout, ROM base, capability list pointers, interrupt routing, MSI/MSI-X programming, and ARI/SR-IOV capability/control state.
- PCIe device/link status, control, power management, AER status/masks/severity/header logs, and TLP-prefix logs.
- RCC root-complex, endpoint, and downstream control state for link management, LTR, requester IDs, DPA, PME, RX/TX behavior, straps, and error handling.
- PFC restore and auxiliary-power state.
- MSI-X table entries that persist interrupt target address/data/masking until reprogrammed by the OS, firmware, reset, or power-management flows.

Some registers are status or latch-like rather than durable configuration, notably AER status/log registers, PCIe link status, interrupt status, error-control/status, and MSI-X vector control masking. Correct sequencing, clearing, and polling rules are determined by PCIe/NBIF hardware behavior and the owning driver paths, not by this offset header.

## Dependencies and Integration Points

The direct companion header is `nbif_6_3_1_sh_mask.h`, which supplies field masks and shifts for the same NBIF generation. `nbif_v6_3_1.c` includes both headers and performs active NBIF programming with `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `REG_SET_FIELD`. The specific macros used most visibly in that C file are in adjacent RCC and doorbell regions, but this chunk follows the same generated naming and base-index contract.

Display code also includes this offset header in `display/dc/resource/dcn401/dcn401_resource.c`, where register-list helpers build addresses as `BASE(reg..._BASE_IDX) + reg...`. That makes the `_BASE_IDX` definitions as important as the raw offsets; a wrong base index can point the display or NBIF code at the wrong register aperture.

The VF, EPF, RCC, PFC, and MSI-X names mirror families in other NBIO/NBIF generations. Those nearby implementations are useful validation references, but their offsets are not interchangeable with NBIF 6.3.1.

## Risks

- Offset drift is high impact. A one-word error can make driver code touch the wrong PCI config, PCIe control, MSI-X, or root-complex register.
- The repeated VF blocks are easy to damage mechanically. VF1 through VF7 differ mainly by the 0x400 window stride, so copy/paste or generator errors can silently alias two VFs or skip one.
- EPF1 has extra SR-IOV and VF BAR/resize BAR controls not present in the same form in EPF2/EPF3 in this chunk. Treating all endpoint-function blocks as identical would miss those registers.
- MSI-X table registers are interrupt-critical. Wrong address/data/control offsets can misroute interrupts, leave vectors masked, or corrupt adjacent MSI-X entries.
- AER and TLP-prefix log offsets are reliability/debug sensitive. Incorrect status or log addresses can make error reporting misleading and can hide real PCIe faults.
- RCC link, LTR, DPA, PME, requester-ID, and strap-related offsets participate in power management and link bring-up. Wrong accesses can cause resume failures, link training issues, or broken low-power behavior.
- All macros in this chunk use base index `5`; code that assumes a different base or byte-address form would compute invalid MMIO addresses.
- The chunk starts and ends inside larger generated families. The final per-file merge must reconcile the VF0 prelude and the remaining MSI-X table entries from adjacent chunks.

## Test and Validation Signals

Useful validation is mostly build, enumeration, and hardware bring-up coverage:

- Build AMDGPU and DCN401 display code that includes `nbif_6_3_1_offset.h`; this catches missing or renamed macros and broken `_BASE_IDX` pairs.
- Boot on NBIF 6.3.1 hardware and verify PCI enumeration of EPF1-EPF3 and SR-IOV VF1-VF7 config-space identity, BARs, capability lists, and ARI/SR-IOV capabilities.
- Enable SR-IOV where supported and confirm each VF window is distinct and follows the expected 0x400 stride.
- Exercise MSI and MSI-X interrupt setup, vector masking/unmasking, and interrupt delivery, especially vectors 0-32 covered here.
- Run PCIe link/power-management suspend-resume tests to validate RCC LTR, PME, DPA, requester-ID restore, and sticky-restore behavior.
- Inject or observe PCIe AER conditions, then confirm status, severity, mask, header log, and TLP-prefix log paths report the expected registers.
- Use register dumps from firmware or hardware diagnostics to compare `BASE_IDX 5 + offset` calculations against documented NBIF 6.3.1 addresses.

## Unresolved Cross-Chunk References

Line 2493 starts after the beginning of the VF0 config-space register window; earlier VF0 standard, PCIe, MSI, and capability offsets belong to the previous chunk. Line 4953 ends at `regPCIEMSIX_VECT32_CONTROL` and does not establish the full MSI-X table extent; later vector entries, if present, belong to the next chunk.

### subset-b-002874: lines 4954-7387

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h lines 4954-7387

## Scope

This chunk covers a generated AMD NBIF 6.3.1 register-offset header section. It starts at the tail of the MSI-X vector table with `regPCIEMSIX_VECT32_CONTROL_BASE_IDX`, then defines complete MSI-X vector entries for vectors 33 through 255. The later lines switch through several NBIF address blocks: RCC PFC USB and PD-controller restore registers, the MSI-X pending-bit array, RCC shadow and BIF SWUS indirect-access registers, RCC strap registers, BIF reset controls, and the first part of the BIF miscellaneous block.

The file is data-only C preprocessor material. It defines no functions, structs, variables, runtime control flow, locks, memory allocations, or direct MMIO operations. Its public interface is the generated register-address convention:

- `reg<REGISTER>` expands to the register offset used by AMDGPU register access helpers.
- `reg<REGISTER>_BASE_IDX` expands to the SOC15 base-index selector for the IP/register aperture. In this chunk every visible base index is `5`.

## Purpose

This header is part of the generated NBIF register ABI for ASIC version 6.3.1. NBIF is the northbridge/PCIe-facing block used by the AMD GPU driver for PCIe function control, MSI-X interrupt programming, reset and function-level-reset handling, power-state transitions, strap-derived configuration, and miscellaneous BIF controls.

Consumers include the matching NBIF 6.3.1 shift/mask header and AMDGPU/SOC15 register helpers that combine a base index, register offset, and field definitions into MMIO accesses. This chunk supplies addresses only; bit layout and semantics are provided by companion `*_sh_mask.h` files and by the owning driver code.

## Important Macro Families

### PCIe MSI-X Vector Table

The chunk begins in the `nbif_pciemsix_0_usb_MSIXTDEC` table. Line 4954 is only `regPCIEMSIX_VECT32_CONTROL_BASE_IDX`, so the vector-32 address macros themselves belong to the previous chunk. Complete definitions then cover vectors 33 through 255:

- `regPCIEMSIX_VECTn_ADDR_LO` and `regPCIEMSIX_VECTn_ADDR_HI` define the low and high message-address dwords.
- `regPCIEMSIX_VECTn_MSG_DATA` defines the message data register.
- `regPCIEMSIX_VECTn_CONTROL` defines the vector control register.

The offsets are contiguous four-dword records. Vector 33 starts at `0x1e084` and vector 255 ends at `0x1e3ff`; for each vector the fields appear as address-low, address-high, message-data, and control. These addresses are used when the driver or PCI/MSI-X infrastructure programs interrupt delivery for GPU functions exposed through this NBIF instance.

### RCC PFC Restore Blocks

Two short `RCCPFCDEC` blocks follow:

- `nbif_rcc_pfc_usb_RCCPFCDEC`, base address `0x10134400`, provides `regRCC_PFC_USB_RCC_PFC_LTR_CNTL`, `PME_RESTORE`, `STICKY_RESTORE_0` through `STICKY_RESTORE_5`, and `AUXPWR_CNTL` at offsets `0xd140` through `0xd148`.
- `nbif_rcc_pfc_pd_controller_RCCPFCDEC`, base address `0x10134600`, mirrors the same LTR, PME restore, sticky restore, and auxiliary-power control pattern at offsets `0xd1c0` through `0xd1c8`.

These macros name registers that preserve or restore PCIe/power-management state across low-power or reset transitions.

### MSI-X Pending-Bit Array

The `nbif_pciemsix_0_usb_MSIXPDEC` block, base address `0x10179000`, defines `regPCIEMSIX_PBA_0` through `regPCIEMSIX_PBA_7` at offsets `0x1e400` through `0x1e407`. These are the MSI-X pending-bit array registers paired with the vector-table region above. Software should treat them as interrupt pending/status storage rather than ordinary policy configuration.

### Shadow and SWUS Indirect Access

The `nbif_rcc_shadow_reg_shadowdec` block, base address `0x10130000`, defines:

- `regSHADOW_COMMAND`
- `regSHADOW_BASE_ADDR_1`
- `regSHADOW_BASE_ADDR_2`
- `regSHADOW_IRQ_BRIDGE_CNTL`
- `regSUC_INDEX`
- `regSUC_DATA`

The `nbif_bif_swus_SUMDEC` block, base address `0x1013b000`, defines `regSUM_INDEX`, `regSUM_DATA`, and `regSUM_INDEX_HI`. The index/data naming indicates indirect register windows: users select an internal index and then read or write data through a companion data register. Correct sequencing is controlled by driver code and hardware rules, not by this header.

### RCC Strap Registers

The `nbif_rcc_strap_rcc_strap_internal` block, base address `0x10100000`, occupies the largest non-MSI-X part of this chunk. It defines strap offsets for:

- Device-port straps for device 0, device 1, and device 2: `PORT_STRAP0` through `PORT_STRAP14` at `0xc400`, `0xc480`, and `0xc500` ranges.
- BIF-level straps: `regRCC_STRAP1_RCC_BIF_STRAP0` through `STRAP6` at `0xc600` through `0xc606`.
- Endpoint-function straps for device 0 EPF0 through EPF7, device 1 EPF0 through EPF5, and device 2 EPF0 through EPF2, using sparse offset groups from `0xd000` through `0xd90e`.

These registers expose strap-latched hardware configuration for PCIe/device/function behavior. The sparse numbering is intentional: not every possible strap index is represented for every EPF group in this chunk.

### BIF Reset and Power-State Registers

The `nbif_bif_rst_bif_rst_regblk` block, base address `0x10100000`, defines reset, interrupt, and power-state offsets:

- Global and self reset controls: `regHARD_RST_CTRL`, `regRSMU_SOFT_RST_CTRL`, `regSELF_SOFT_RST`, `regSELF_SOFT_RST_2`, plus `regBIF_GFX_DRV_VPU_RST`.
- Miscellaneous reset controls: `regBIF_RST_MISC_CTRL`, `regBIF_RST_MISC_CTRL2`, and `regBIF_RST_MISC_CTRL3`.
- Per-function FLR reset controls for device 0 PF0 through PF6.
- Reset/power interrupt status and mask registers for instance reset, PF FLR, D3hot-to-D0, generic power, and PF D-state events.
- `regBIF_PF_FLR_RST`, per-PF D-state value registers for device 0 PF0 through PF6, per-PF D3hot-to-D0 reset controls, `regBIF_PORT0_DSTATE_VALUE`, and `regBIF_USB_SHUB_RS_RESET_CNTL`.

These addresses are integration points for device reset, suspend/resume, function-level reset, and power-management paths.

### BIF Miscellaneous Registers

The chunk ends in the `nbif_bif_misc_bif_misc_regblk` block, base address `0x10100000`. Visible macros include:

- ROM/BIOS and scratch/control registers: `regREGS_ROM_OFFSET_CTRL`, `regNBIF_STRAP_BIOS_CNTL`, `regMISC_SCRATCH`, `regINTR_LINE_POLARITY`, `regINTR_LINE_ENABLE`, and `regOUTSTANDING_VC_ALLOC`.
- BIFC controls and logs: `regBIFC_MISC_CTRL0`, `regBIFC_MISC_CTRL1`, `regBIFC_BME_ERR_LOG_LB`, `regBIFC_LC_TIMER_CTRL`, `regBIFC_RCCBIH_BME_ERR_LOG0`, and DMA attribute override/control registers for device 0 functions.
- Miscellaneous BIFC controls for throttling, host arbitration, GSI, PCIe function behavior, PASID checking/status, SDP controls, ATHUB activity, and the start of performance controls at `regBIFC_PERF_CNTL_0`.

The line range ends at `regBIFC_PERF_CNTL_0 0xe830`; the matching base-index macro and remaining BIF miscellaneous definitions continue in a later chunk.

## Control Flow and State Behavior

There is no executable control flow in this chunk. Its behavior is compile-time symbol substitution for register offsets and base indices. Runtime ordering, locking, polling, interrupt masking, reset sequencing, and error handling all live in the AMDGPU/NBIF code that consumes these macros.

The state represented by these offsets is hardware state. Some registers are persistent configuration or restore state, such as straps, PFC sticky restore registers, DMA attribute controls, PASID controls, interrupt-line settings, and miscellaneous BIFC policy controls. Others are status or command-like, including MSI-X PBA registers, reset interrupt status/mask registers, FLR/D3hot reset controls, scratch registers, and performance-control registers.

The MSI-X vector table is especially stateful: each vector has address, data, and control registers that determine interrupt delivery. Incorrect writes can redirect interrupts, mask vectors unexpectedly, or leave pending bits uncleared. The reset and D-state registers also carry sequencing-sensitive state where write order and acknowledgement polling matter.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register-header ecosystem:

- Companion NBIF 6.3.1 shift/mask headers provide field positions and masks for many of these offsets.
- AMDGPU SOC15 helpers use base index `5` together with the `reg...` offsets to access the correct NBIF aperture.
- PCI/MSI-X setup, interrupt handling, reset, suspend/resume, FLR, RAS/error logging, and PCIe link/device-function management are the likely consumers of the address families visible here.

The generated names are version-specific. Similar register names in other NBIF versions should not be assumed to have identical offsets, base-index values, or field layouts.

## Risks

- Offset drift is high impact. A wrong MSI-X vector-table address can program the wrong vector's message address, message data, or mask/control word.
- The line-range boundary is mid-family at both ends: vector 32 is only represented by one base-index macro here, and BIF miscellaneous performance-control definitions continue after the chunk. Per-file reconciliation must merge neighboring chunks before making whole-file coverage claims.
- The MSI-X vector table is mechanically repetitive. Insertions, deletions, or off-by-one vector numbering errors can silently remap hundreds of interrupt registers.
- All visible macros use `_BASE_IDX 5`; changing any one base index would redirect SOC15 access to the wrong register aperture even if the offset value looked correct.
- Strap and restore registers represent hardware-latched or power-management state. Treating them as ordinary mutable configuration can break PCIe enumeration, resume, or endpoint-function behavior.
- Reset and D-state registers are sequencing-sensitive. Incorrect ordering around FLR, D3hot-to-D0, soft reset, or interrupt status/mask handling can hang the device or lose reset-completion events.
- Indirect index/data registers such as `SUC_INDEX`/`SUC_DATA` and `SUM_INDEX`/`SUM_DATA` are prone to races if consumers do not serialize index selection and data access.
- PASID, DMA attribute, BME error-log, and ATHUB activity controls affect isolation, error reporting, and memory-transaction behavior. Bad field definitions or wrong offsets can create security, reliability, or performance regressions.

## Test and Validation Signals

Useful validation is mostly compile, integration, and hardware bring-up coverage:

- Build AMDGPU code paths that include `nbif_6_3_1_offset.h` and the matching NBIF shift/mask header; this catches missing or renamed generated macros.
- Exercise MSI-X interrupt allocation and interrupt delivery on ASICs using NBIF 6.3.1, including vector masking/unmasking and pending-bit behavior.
- Run suspend/resume and runtime power-management tests that cover RCC PFC restore/sticky state and auxiliary-power controls.
- Run PCIe FLR, soft reset, D3hot-to-D0, and device reset tests for device 0 PF0 through PF6 paths, verifying reset status/mask interrupts and D-state value registers.
- Validate strap-derived configuration against expected PCIe/device/function enumeration, especially for sparse EPF strap groups.
- Check indirect-access users for serialized `INDEX`/`DATA` sequences around `SUC_*` and `SUM_*` registers.
- Run error-reporting and stress tests that touch BIFC BME logs, DMA attribute overrides, PASID controls/status, ATHUB activity controls, and BIFC performance controls.

## Unresolved Cross-Chunk References

The previous chunk contains the address macros for MSI-X vector 32 and probably the earlier vectors in the same table. This chunk only contains `regPCIEMSIX_VECT32_CONTROL_BASE_IDX` before continuing with vector 33. The next chunk is needed to complete the BIF miscellaneous block because this range ends at `regBIFC_PERF_CNTL_0` without the corresponding `_BASE_IDX` line or later miscellaneous registers.

### subset-b-002875: lines 7388-10021

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

### subset-b-002876: lines 10022-11287

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
