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
