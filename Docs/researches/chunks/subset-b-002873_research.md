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
