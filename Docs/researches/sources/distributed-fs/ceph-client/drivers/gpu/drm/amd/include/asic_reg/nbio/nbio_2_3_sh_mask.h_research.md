# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002904`: lines 1-2540, `Docs/researches/chunks/subset-b-002904_research.md`
- `subset-b-002905`: lines 2541-4960, `Docs/researches/chunks/subset-b-002905_research.md`
- `subset-b-002906`: lines 4961-7402, `Docs/researches/chunks/subset-b-002906_research.md`
- `subset-b-002907`: lines 7403-9846, `Docs/researches/chunks/subset-b-002907_research.md`
- `subset-b-002908`: lines 9847-12321, `Docs/researches/chunks/subset-b-002908_research.md`
- `subset-b-002909`: lines 12322-14790, `Docs/researches/chunks/subset-b-002909_research.md`
- `subset-b-002910`: lines 14791-17171, `Docs/researches/chunks/subset-b-002910_research.md`
- `subset-b-002911`: lines 17172-19549, `Docs/researches/chunks/subset-b-002911_research.md`
- `subset-b-002912`: lines 19550-21952, `Docs/researches/chunks/subset-b-002912_research.md`
- `subset-b-002913`: lines 21953-24399, `Docs/researches/chunks/subset-b-002913_research.md`
- `subset-b-002914`: lines 24400-26849, `Docs/researches/chunks/subset-b-002914_research.md`
- `subset-b-002915`: lines 26850-29340, `Docs/researches/chunks/subset-b-002915_research.md`
- `subset-b-002916`: lines 29341-31771, `Docs/researches/chunks/subset-b-002916_research.md`
- `subset-b-002917`: lines 31772-34201, `Docs/researches/chunks/subset-b-002917_research.md`
- `subset-b-002918`: lines 34202-36635, `Docs/researches/chunks/subset-b-002918_research.md`
- `subset-b-002919`: lines 36636-39061, `Docs/researches/chunks/subset-b-002919_research.md`
- `subset-b-002920`: lines 39062-41493, `Docs/researches/chunks/subset-b-002920_research.md`
- `subset-b-002921`: lines 41494-43919, `Docs/researches/chunks/subset-b-002921_research.md`
- `subset-b-002922`: lines 43920-46353, `Docs/researches/chunks/subset-b-002922_research.md`
- `subset-b-002923`: lines 46354-48777, `Docs/researches/chunks/subset-b-002923_research.md`
- `subset-b-002924`: lines 48778-51444, `Docs/researches/chunks/subset-b-002924_research.md`
- `subset-b-002925`: lines 51445-54195, `Docs/researches/chunks/subset-b-002925_research.md`
- `subset-b-002926`: lines 54196-56612, `Docs/researches/chunks/subset-b-002926_research.md`
- `subset-b-002927`: lines 56613-59036, `Docs/researches/chunks/subset-b-002927_research.md`
- `subset-b-002928`: lines 59037-61469, `Docs/researches/chunks/subset-b-002928_research.md`
- `subset-b-002929`: lines 61470-63890, `Docs/researches/chunks/subset-b-002929_research.md`
- `subset-b-002930`: lines 63891-66318, `Docs/researches/chunks/subset-b-002930_research.md`
- `subset-b-002931`: lines 66319-68739, `Docs/researches/chunks/subset-b-002931_research.md`
- `subset-b-002932`: lines 68740-71163, `Docs/researches/chunks/subset-b-002932_research.md`
- `subset-b-002933`: lines 71164-73585, `Docs/researches/chunks/subset-b-002933_research.md`
- `subset-b-002934`: lines 73586-76008, `Docs/researches/chunks/subset-b-002934_research.md`
- `subset-b-002935`: lines 76009-78432, `Docs/researches/chunks/subset-b-002935_research.md`
- `subset-b-002936`: lines 78433-80987, `Docs/researches/chunks/subset-b-002936_research.md`
- `subset-b-002937`: lines 80988-83608, `Docs/researches/chunks/subset-b-002937_research.md`
- `subset-b-002938`: lines 83609-86241, `Docs/researches/chunks/subset-b-002938_research.md`
- `subset-b-002939`: lines 86242-88736, `Docs/researches/chunks/subset-b-002939_research.md`
- `subset-b-002940`: lines 88737-91171, `Docs/researches/chunks/subset-b-002940_research.md`
- `subset-b-002941`: lines 91172-93606, `Docs/researches/chunks/subset-b-002941_research.md`
- `subset-b-002942`: lines 93607-96044, `Docs/researches/chunks/subset-b-002942_research.md`
- `subset-b-002943`: lines 96045-98522, `Docs/researches/chunks/subset-b-002943_research.md`
- `subset-b-002944`: lines 98523-100975, `Docs/researches/chunks/subset-b-002944_research.md`
- `subset-b-002945`: lines 100976-103396, `Docs/researches/chunks/subset-b-002945_research.md`
- `subset-b-002946`: lines 103397-105826, `Docs/researches/chunks/subset-b-002946_research.md`
- `subset-b-002947`: lines 105827-108246, `Docs/researches/chunks/subset-b-002947_research.md`
- `subset-b-002948`: lines 108247-110670, `Docs/researches/chunks/subset-b-002948_research.md`
- `subset-b-002949`: lines 110671-113093, `Docs/researches/chunks/subset-b-002949_research.md`
- `subset-b-002950`: lines 113094-115515, `Docs/researches/chunks/subset-b-002950_research.md`
- `subset-b-002951`: lines 115516-117939, `Docs/researches/chunks/subset-b-002951_research.md`
- `subset-b-002952`: lines 117940-120339, `Docs/researches/chunks/subset-b-002952_research.md`

## Chunk Research

### subset-b-002904: lines 1-2540

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 1-2540

## Scope

This chunk covers the first 2,540 lines of the generated NBIO 2.3 shift/mask header. It defines C preprocessor constants for register field extraction and insertion across early NBIO/BIF/RCC/GDC/PCIe address blocks:

- PF MMIO index/data apertures, SYSDEC PCIE/SYSHUB indirect apertures, BIOS scratch registers, and GFX MMIO remap CAM fields.
- RCC strap fields for BIF-wide capabilities, downstream port strap presentation, and endpoint functions `DEV0_EPF0` and `DEV0_EPF1`.
- Endpoint, downstream, and downstream-port PCIe control/status/error fields.
- PF and function-facing RCC/BIF controls for SR-IOV, doorbells, HDP flushes, mailboxes, BACO, peer apertures, requester IDs, interrupt delivery, and BIF ring-buffer state.
- GDC/A2S/S2A arbitration, clock/power-gating, and doorbell-range fields.
- `DEV0_EPF0` GFX MSI-X vector-table fields.
- The beginning of the `PSWUSCFG0_0` PCI bridge config-space field map through `IRQ_BRIDGE_CNTL` shifts; the remaining masks continue in the next chunk.

The source is a generated hardware ABI header. It contains no C functions, structs, variables, locks, allocation, or executable control flow.

## Purpose

`nbio_2_3_sh_mask.h` provides the bit-level contract for NBIO 2.3 registers. The sibling offset header names register locations; this header names each field's bit shift and mask so AMDGPU can use `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, and direct bit tests without hard-coding bit positions in driver logic.

This range is broad because NBIO sits at the GPU's PCIe/northbridge boundary. The fields describe PCI config presentation, power-management straps, link behavior, virtualization controls, doorbell routing, host data path coherency, BIF ring-buffer interrupts, and GDC request/response arbitration.

## Important Macro Families

### Indirect Apertures and Scratch State

The chunk opens with PF MMIO and system decode fields:

- `BIF_BX_PF_MM_INDEX`, `BIF_BX_PF_MM_DATA`, and `BIF_BX_PF_MM_INDEX_HI` split an indirect MMIO offset across low/high index words and expose the `MM_APER` selector.
- `SYSHUB_INDEX_OVLP`/`SYSHUB_DATA_OVLP`, `SYSHUB_INDEX`/`SYSHUB_DATA`, and `PCIE_INDEX`/`PCIE_DATA` plus `PCIE_INDEX2`/`PCIE_DATA2` define indirect access windows used by NBIO helper code.
- `SBIOS_SCRATCH_0..3` and `BIOS_SCRATCH_0..15` are full-register scratch fields shared with firmware/BIOS conventions.
- `BIF_RLC_INTR_CNTL`, `BIF_VCE_INTR_CNTL`, and `BIF_UVD_INTR_CNTL` expose command-complete, self-recovered hang, FLR-needed hang, and VM-busy transition interrupt bits for firmware/media/gfx-facing engines.
- `GFX_MMIOREG_CAM_ADDR0..7`, matching `REMAP_ADDR0..7`, `GFX_MMIOREG_CAM_CNTL`, and completion-value registers define the CAM used to remap graphics-visible MMIO register accesses.

### RCC Strap and PCI Capability Presentation

`nbio_nbif0_rcc_strap_BIFDEC1` is a large static-configuration section. The `RCC_BIF_STRAP0..6` masks cover global PCIe/BIF capabilities and policy bits such as Gen3/Gen4 disable/kill straps, clock power management, VGA/BIOS ROM exposure, memory aperture size, PX capability, SR-IOV error handling, PME compliance, P2P passing, link-down reset, LTR-in-ASPM-L1 behavior, vlink timers, power-break deglitch timers, emergency power-reduction capability, and S5 access behavior.

The `RCC_DEV0_PORT_STRAP0..9` fields define downstream/root-port style PCIe capability presentation: ARI/ACS/AER enablement, device IDs, interrupt pins, maximum payload and link width, subsystem IDs, ECRC, extended tags, generation support and target link speed, L0s/L1 latency values, LTR/OBFF/PM/atomic support, lane equalization presets, power-budget data, local DLF, ACS capability bits, 10-bit tags, TPH support, and bus/device/function numbering.

`RCC_DEV0_EPF0_STRAP*` and `RCC_DEV0_EPF1_STRAP*` define endpoint-function identity and capabilities. EPF0 includes SR-IOV enablement, total VFs, VF device ID and page size, resize BAR, PASID width and permissions, ATS, ACS, AER, MSI/MSI-X, FLR, DPA, doorbell/memory/register/ROM aperture sizes, VF aperture sizing, VF MSI capability, SR-IOV VF mapping mode, outstanding page request capacity, BAR compliance, and VF register protection. EPF1 repeats the endpoint identity/capability pattern with aperture and resize support for apertures 0 through 3 plus TPH requester fields.

### Endpoint and Downstream PCIe Controls

The endpoint block `nbio_nbif0_rcc_ep_dev0_BIFDEC1` covers PCIe runtime controls:

- `EP_PCIE_CNTL`, `EP_PCIE_RX_CNTL`, and `EP_PCIE_RX_CNTL2` gate unsupported-request reporting and ignore modes for malformed atomics, LTR messages, max payload, traffic class, prefix, PASID, and TPH conditions.
- `EP_PCIE_INT_CNTL` and `EP_PCIE_INT_STATUS` define enables/status for correctable, non-fatal, fatal, user-detected, miscellaneous, and power-state-change events.
- `EP_PCIE_CFG_CNTL` controls access to hidden Gen2/Gen3/Gen4 config registers.
- `EP_PCIE_TX_LTR_CNTL` encodes snoop/non-snoop LTR values, requirements, PM-non-D0 LTR suppression, LTR reset on link down, L1 flow-control checks, and D-state write-data behavior.
- `EP_PCIE_F0_DPA_*`, `PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_0..7`, and `PCIE_F1_DPA_SUBSTATE_PWR_ALLOC_0..7` describe DPA transition latency, power allocation, substate status, and compliance mode.
- `EP_PCIE_TX_CNTL`, `EP_PCIE_TX_REQUESTER_ID`, and `EP_PCIE_ERR_CNTL` cover SNR/RO overrides, per-function TPH disables, requester bus/device/function IDs, AER header-log timeout, immediate error-message send, poisoned advisory non-fatal policy, and per-function AER timer-expired status.
- `EP_PCIE_LC_SPEED_CNTL` exposes Gen2/Gen3/Gen4 strap enable bits.

The downstream blocks `nbio_nbif0_rcc_dwn_dev0_BIFDEC1` and `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1` mirror several controls for downstream-port behavior: hidden config decode, FLR extend mode, PMI behavior, F0 strap enables, clock PM/master-address-64 straps, error reporting, receive ignore modes, link-speed straps, link bandwidth notification, multifunction strap, and LTR message information from the endpoint.

### RCC Runtime Controls

`nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]` defines EPF0 RCC fields visible in the PF/VF decode window:

- `RCC_DEV0_EPF0_RCC_ERR_LOG` records invalid SR-IOV register access and doorbell read access status.
- `RCC_DEV0_EPF0_RCC_DOORBELL_APER_EN` gates the BIF doorbell aperture.
- `RCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width config fields.
- `RCC_DEV0_EPF0_RCC_IOV_FUNC_IDENTIFIER` encodes the function identifier and IOV enable bit.

The broader `nbio_nbif0_rcc_dev0_BIFDEC1` block includes error interrupt enable, BACO misc request disables, reset enable for the doorbell aperture, VDM support routing, PCIe margining parameters, GPUIOV regions, peer register and framebuffer ranges, bus control policy, VGA config, function base/aper sizes, XDMA aperture bounds, unsupported-request policy, bus-number auto-update/list capture, host bus ID, dev/function ID lists, link down entry/exit bits, common link controls, endpoint requester-ID restore, LTR switch latency, and memory-host arbitration.

### BIF Runtime Controls

`nbio_nbif0_bif_bx_BIFDEC1` provides central BIF fields used directly by NBIO helper code:

- `BIF_MM_INDACCESS_CNTL` can disable writes or indirect MMIO access.
- `BUS_CNTL` controls VGA coherency, audio/memory traffic-class settings, zero-byte-enable reads/writes, IO-write stalls, VGA flush stalls, and HDP register-flush VF mask behavior.
- `MM_CFGREGS_CNTL` selects config function/device and enables MMIO writes to config space.
- `INTERRUPT_CNTL` and `INTERRUPT_CNTL2` configure IH dummy-read behavior, non-snoop interrupt-handler requests, interrupt delay, generic IH interrupt enable, BIF ring-buffer request attributes, and dummy-read address.
- `BIF_FEATURES_CONTROL_MISC` gates endpoint request/completion paths, MSI vector-not-enabled mode, ring-buffer overflow interrupt behavior, atomic behavior, bus-master handling, HDP outstanding limits, and 48-bit doorbell GPA aperture checks.
- `BIF_DOORBELL_CNTL` and `BIF_DOORBELL_INT_CNTL` define self-ring, translation checks, monitor enable, interrupt generation modes, status/clear/disable bits, and status-forced-on-ring-buffer-enable behavior.
- `BIF_FB_EN` toggles framebuffer read/write access.
- `BIF_MST_TRANS_PENDING_VF`, `BIF_SLV_TRANS_PENDING_VF`, and `BIF_BX_PF_BIF_TRANS_PENDING` expose outstanding transaction state.
- `BACO_CNTL` plus `BIF_BACO_EXIT_TIME0` and timers 1 through 4 define BACO enable, power-off, D-state bypass, reset interrupt masking, mode, config-done, power-good, auto-exit, and exit timing.
- `NBIF_GFX_ADDR_LUT_CNTL` and `NBIF_GFX_ADDR_LUT_0..15` configure graphics address LUT use and MSI address mode.
- `REMAP_HDP_MEM_FLUSH_CNTL` and `REMAP_HDP_REG_FLUSH_CNTL` name the remapped HDP flush address fields.
- `BIF_RB_CNTL`, `BIF_RB_BASE`, `BIF_RB_RPTR`, `BIF_RB_WPTR`, and writeback address registers define the BIF ring-buffer enable, size, writeback, transport, interrupt arbitration, FLR reset behavior, overflow clear/status, base, read pointer, write pointer, and writeback target.
- Pad controls cover PERSTB, PX_EN, REFPADKIN, CLKREQB, PWRBRK, WAKEB/GPIO33, and VAUX_PRESENT GPIO electrical settings.

### PF Doorbell, HDP Flush, and Mailbox

The PF decode block `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` defines:

- `BIF_BX_PF_BIF_BME_STATUS` for DMA observed while bus mastering is low, with a clear bit.
- `BIF_BX_PF_BIF_ATOMIC_ERR_LOG` for unsupported atomic opcode/request-enable/length/non-relaxed conditions and their clear bits.
- `BIF_BX_PF_DOORBELL_SELFRING_GPA_APER_BASE_HIGH/LOW` and `CNTL` for self-ring GPA aperture base, enable, mode, and size.
- `BIF_BX_PF_HDP_REG_COHERENCY_FLUSH_CNTL` and `BIF_BX_PF_HDP_MEM_COHERENCY_FLUSH_CNTL` for coherency flush address selection.
- `BIF_BX_PF_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF_GPU_HDP_FLUSH_DONE` bits for CP0 through CP9 and SDMA0/SDMA1 flush request/completion.
- `BIF_BX_PF_NBIF_GFX_ADDR_LUT_BYPASS` for bypassing the NBIF graphics address LUT.
- Transmit and receive mailbox data words `DW0..DW3`, `BIF_BX_PF_MAILBOX_CONTROL` valid/ack bits, `BIF_BX_PF_MAILBOX_INT_CNTL` valid/ack interrupt enables, and `BIF_BX_PF_BIF_VMHV_MAILBOX` compact VM/hypervisor mailbox data, valid, ack, and interrupt-enable fields.

### GDC, Doorbell Range, and MSI-X

The `nbio_nbif0_gdc_GDCDEC` block describes GDC bridge behavior:

- `A2S_CNTL_CL0/CL1` map AXI-to-SDP attributes and response/error handling for two client lanes.
- `A2S_CNTL3_CL0/CL1`, `A2S_CNTL_SW0..2`, `A2S_CPLBUF_ALLOC_CNTL`, `A2S_TAG_ALLOC_0/1`, and `A2S_MISC_CNTL` control write steering, weighted round-robin read/write weights, completion buffer reservation, tag allocation, response reorder behavior, and tag-set minima.
- `NGDC_MGCG_CTRL`, `NGDC_PG_MISC_CTRL`, `NGDC_PGMST_CTRL`, and `NGDC_PGSLV_CTRL` configure medium-grain clock gating, power-gating hysteresis, exit overrides, firmware power-gating exits, and idle hysteresis for SHUB/GDC clocks.
- `BIF_SDMA0_DOORBELL_RANGE`, `BIF_SDMA1_DOORBELL_RANGE`, `BIF_IH_DOORBELL_RANGE`, `BIF_MMSCH0_DOORBELL_RANGE`, and `BIF_ACV_DOORBELL_RANGE` define doorbell offset and size fields for clients.
- `BIF_DOORBELL_FENCE_CNTL` gates doorbell fencing for CP, SDMA0, SDMA1, and ACV and controls one-shot trigger behavior.
- `S2A_MISC_CNTL` controls 64-bit doorbell support disables for SDMA/CP/ACV plus AXI host completion and arbitration modes.

`nbio_nbif0_rcc_dev0_epf0_BIFDEC2` defines the register-window view of four GFX MSI-X vectors: each vector has low/high message address, message data, and mask-bit control fields. `RCC_DEV0_EPF0_GFXMSIX_PBA` defines pending bits 0 through 3.

The final block begins `nbio_pcie0_pswuscfg0_cfgdecp`, a PCI bridge configuration-space field map. In this chunk it covers vendor/device ID, command/status, revision/class/header/BIST, bus-number/latency, IO/memory/prefetchable window base/limit registers, capability pointer, ROM base, interrupt line/pin, and the shift side of `IRQ_BRIDGE_CNTL` plus most of its masks.

## Integration Points

The primary direct consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_sh_mask.h` with the matching offset and default headers. That file uses:

- `RCC_DEV0_EPF0_STRAP0__STRAP_ATI_REV_ID_DEV0_F0_*` to extract the revision ID, with a special SR-IOV VF path because guests read `0xffffffff`.
- `BIF_FB_EN__FB_READ_EN_MASK` and `BIF_FB_EN__FB_WRITE_EN_MASK` to enable or disable memory-controller framebuffer access.
- `RCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE` to read configured memory size.
- `BIF_SDMA0_DOORBELL_RANGE`, `BIF_MMSCH0_DOORBELL_RANGE`, and `BIF_IH_DOORBELL_RANGE` field names with `REG_SET_FIELD` to program client doorbell offset/size.
- `RCC_DEV0_EPF0_RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN` via `WREG32_FIELD15` to toggle the doorbell aperture.
- `BIF_BX_PF_DOORBELL_SELFRING_GPA_APER_CNTL` fields to program the self-ring GPA aperture using `adev->doorbell.base`.
- `INTERRUPT_CNTL` fields to set IH dummy-read and non-snoop behavior.
- `BIF_BX_PF_GPU_HDP_FLUSH_REQ/DONE` masks to provide HDP flush request/done offsets and completion masks to the AMDGPU HDP flush framework.
- `RCC_BIF_STRAP2`, `RCC_BIF_STRAP3`, `RCC_BIF_STRAP5`, and `EP_PCIE_TX_LTR_CNTL` masks during ASPM/LTR programming.
- `BIF_RB_CNTL` and `BIF_DOORBELL_INT_CNTL` masks to clear a doorbell interrupt when the BIF ring buffer is disabled.
- `REMAP_HDP_MEM_FLUSH_CNTL` and `REMAP_HDP_REG_FLUSH_CNTL` with the remap offset setup used by KFD-facing MMIO remaps.

Power-management code also consumes this header. SMU11 platform code such as `navi10_ppt.c` reads `RCC_BIF_STRAP0__STRAP_PX_CAPABLE_MASK` to determine BACO/MACO platform support. Older powerplay BACO helpers read `mmBACO_CNTL` and test `BACO_CNTL__BACO_MODE_MASK` to decide whether the GPU is in BACO state.

## Control Flow

There is no local control flow in this header. Runtime flow is external and follows the SOC15 register-access pattern:

1. AMDGPU selects NBIO 2.3 support during ASIC initialization.
2. Code includes `nbio_2_3_offset.h` for register addresses and this file for field definitions.
3. Register helpers read a register, use `REG_SET_FIELD`/`REG_GET_FIELD` or direct masks from this header, and write updated values back through `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or `WREG32_FIELD15`.
4. Hardware then applies the selected policy to PCIe link behavior, doorbell routing, interrupt delivery, coherency flushes, SR-IOV presentation, BACO, or GDC arbitration.

For fields describing status/clear pairs, the flow is write-to-clear or read/modify/write in the caller. Examples include `BIF_DOORBELL_INT_CNTL__DOORBELL_INTERRUPT_CLEAR`, atomic error clear bits, and BME status clear bits.

## State and Persistence Behavior

The header itself stores no state. It names persistent hardware state in NBIO registers. That state typically survives ordinary CPU control flow until an explicit register write, PCI function reset, FLR, BACO entry/exit, ASIC reset, power-state transition, firmware action, or strap reload changes it.

Important state represented here includes BIOS scratch values, strap-derived capability presentation, PCIe error/status bits, interrupt enable/status bits, configured doorbell aperture and range state, self-ring GPA aperture base, HDP flush request/done handshakes, BIF transaction pending indicators, BIF ring-buffer pointers and overflow status, mailbox payload/ack/valid handshakes, BACO mode/timers, peer aperture mappings, GDC arbitration weights, clock/power-gating configuration, and MSI-X vector-table data.

Several fields cross ownership boundaries. Strap and config-presentation fields are influenced by fuses, ROM straps, firmware, and platform setup. Mailbox fields are shared with hypervisor/VM paths. HDP flush bits are consumed by graphics/SDMA engines and AMDGPU synchronization code. Doorbell fields affect CPU-to-GPU command submission for multiple IP blocks.

## Dependencies

This generated header depends on the NBIO 2.3 hardware register specification and must stay synchronized with:

- `nbio_2_3_offset.h` for `mm*` and `cfg*` register names and base indices.
- `nbio_2_3_default.h` for reset/default values.
- AMDGPU SOC15 helpers and field macros: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.
- PCIe, SR-IOV, MSI/MSI-X, ATS, PASID, ACS, AER, LTR, DPA, ASPM, BACO, and doorbell hardware semantics.
- Firmware/SMU/hypervisor contracts for scratch registers, BACO, mailbox, power-management straps, and VF-visible state.

## Risks

- A wrong shift or mask compiles cleanly but silently programs the wrong hardware bits. In this file, many adjacent bits are independent policy controls, so a one-bit error can turn into link instability, lost interrupts, broken doorbells, or incorrect PCI capability exposure.
- Direct bit tests and `REG_SET_FIELD` depend on exact macro naming. Reusing EP masks on downstream-port registers, PF masks on VF registers, or EPF0 masks on EPF1 registers can target similar-looking but different fields.
- Strap fields are not ordinary runtime knobs. Treating fuse/ROM strap state as freely mutable can misrepresent PCI capabilities or fight platform firmware.
- Status/clear fields often share a register. Writing a full literal without preserving unrelated bits can accidentally clear diagnostics, disable interrupts, or acknowledge mailbox events.
- Doorbell range and aperture mistakes affect command submission globally. Incorrect offset/size or 48-bit GPA aperture checking can misroute doorbells or expose invalid guest/host address ranges.
- HDP flush request/done masks are synchronization-critical. Missing a CP/SDMA done bit or using a reserved/firmware-owned bit can cause stale CPU/GPU memory visibility or hangs in flush waits.
- SR-IOV fields have PF, VF, firmware, and hypervisor ownership implications. Guest-visible reads may return sentinel values, as `nbio_v2_3_get_rev_id()` handles for `RCC_DEV0_EPF0_STRAP0`.
- The PSWUS config block is split at the chunk boundary; merge/reconciliation must combine this chunk with the following chunk for the complete `IRQ_BRIDGE_CNTL` and subsequent capability fields.

## Test Signals

Useful validation is mostly build, hardware bring-up, and integration oriented:

- Kernel build coverage for NBIO 2.3 users verifies that generated mask names stay compatible with `nbio_v2_3.c`, SMU11 power code, and BACO helpers.
- Boot on NBIO 2.3 ASICs should report the expected revision ID, memory size, PCI IDs, BARs, class codes, and capability flags.
- SR-IOV PF/VF testing should verify VF strap presentation, protected-register behavior, doorbell aperture enablement, mailbox handshakes, and the guest revision-ID fallback path.
- Doorbell tests for SDMA, IH, VCN/MMSCH, CP, and ACV should confirm offset/size programming and absence of spurious doorbell interrupts.
- HDP coherency tests should exercise CP0..CP9 and SDMA0/SDMA1 flush request/done paths and the KFD MMIO remap path.
- ASPM/LTR validation should cover removable and non-removable PCIe paths, ensuring `RCC_BIF_STRAP2/3/5` and `EP_PCIE_TX_LTR_CNTL` programming does not regress link stability.
- BACO entry/exit tests should observe `BACO_CNTL__BACO_MODE_MASK`, config-done, power-good, auto-exit, and timer behavior.
- Error-injection tests should validate AER/status/clear fields, unsupported atomic logs, BME-low DMA logging, and interrupt enable/status behavior.
- MSI-X tests should program the four GFX MSI-X vectors and confirm message address/data/mask and pending-bit behavior.
- Static generated-header audits can compare every `__SHIFT`/`_MASK` pair against hardware XML or neighboring generated NBIO versions and check split PSWUS config fields across adjacent chunks.

### subset-b-002905: lines 2541-4960

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 2541-4960

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register-field shift/mask catalog. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, runtime branches, or direct register accesses.

The assigned range starts in the middle of `PSWUSCFG0_0_IRQ_BRIDGE_CNTL`, at the remaining bridge-control masks, then covers the rest of the `PSWUSCFG0_0` PCI/PCIe capability and extended-capability field definitions through `PSWUSCFG0_0_PCIE_CCIX_TRANS_CNTL`. It then begins `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, covering the standard endpoint-function config header and early power-management/PCIe capability fields for `BIF_CFG_DEV0_EPF0_0` through `BIF_CFG_DEV0_EPF0_0_LINK_CNTL`. The final line is only the `//BIF_CFG_DEV0_EPF0_0_LINK_STATUS` marker; that register's fields continue in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header slice is to name the bit layout for NBIO 2.3 PCI configuration and PCIe extended capability registers. Consumers combine these constants with addresses from `nbio_2_3_offset.h` and AMDGPU register helpers to pack, extract, set, clear, or test individual fields in 16-bit and 32-bit hardware register words.

The generated convention is:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's encoded mask.

These macros form a compile-time hardware ABI. The same names are consumed by `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask operations, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15/NBIO helpers in AMDGPU.

## Important Macro Families

The `PSWUSCFG0_0` portion describes a PCIe bridge/upstream-port style config space. It includes bridge interrupt/control bits, extended bridge control, vendor capability headers, adapter/subsystem IDs, PCI power-management capability and status/control fields, PCIe capability headers, device/link capability and control/status registers, MSI message control/address/data fields, SSID and MSI mapping capabilities, and vendor-specific capability headers.

The base PCIe capability fields cover payload and read-request sizing, relaxed ordering, no-snoop, extended tags, function-level reset, correctable/non-fatal/fatal/unsupported-request reporting, link speed/width, ASPM/power-management support, common-clock, retrain/link-disable controls, DRS signaling, completion-timeout policy, LTR enablement, OBFF, atomic-op support, target link speed, compliance/speed disable, de-emphasis, transmit margin, equalization status, and downstream component presence.

The AER block includes `PSWUSCFG0_0_PCIE_UNCORR_ERR_STATUS`, `..._MASK`, and `..._SEVERITY` fields for data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked conditions. It also includes correctable error status/mask fields, AER capability/control, header logs, and TLP prefix logs.

The link-training and PCIe extended capability area covers secondary PCIe link control, lane error status, per-lane equalization controls for lanes 0-15, ACS capability/control, multicast capability/control/address/block/overlay BAR fields, LTR capability, ARI capability/control, L1 PM substates capability/control, data-link feature capability/status, 16 GT/s PHY capability/control/status, per-lane 16 GT/s equalization control, and PCIe lane margining control/status for lanes 0-15.

The `PSWUSCFG0_0_PCIE_ESM_*` and CCIX-related families describe extended speed mode and cache-coherent interconnect capability surfaces. They include ESM headers/status/control, large capability bitmaps for supported data-rate/vector combinations, CCIX required/optional ESM capability, CCIX ESM status/control, per-lane 20 GT/s and 25 GT/s equalization controls, and CCIX transport capability/control fields.

The `BIF_CFG_DEV0_EPF0_0` portion begins a physical endpoint function config decoder block. It covers standard PCI config header fields: vendor/device IDs, command and status, revision/class code, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency. It then covers vendor, PM, and PCIe capability headers plus early PCIe device/link capability and control fields. Relative to the bridge-style `PSWUSCFG0_0` device-control fields, the endpoint block's `DEVICE_CNTL` uses `INITIATE_FLR` at bit 15 and `DEVICE_STATUS` includes `EMER_POWER_REDUCTION_DETECTED`.

No callable APIs or C types are declared in this range; the public surface is entirely macro names.

## Control Flow

There is no executable control flow in this header. Runtime behavior appears in AMDGPU code that includes the header:

1. Code selects an address from `nbio_2_3_offset.h` or an SMN/PCIe address literal for the same hardware block.
2. It reads a register value through NBIO/SOC15/PCIe helpers.
3. It uses these `__SHIFT` and `_MASK` constants, usually through `REG_SET_FIELD`, `REG_GET_FIELD`, or direct bitwise operations, to update or decode fields.
4. It writes the resulting value back, polls status, or reports decoded state according to the hardware programming sequence.

`nbio_v2_3.c` is the closest integration example in this source tree. It includes `nbio_2_3_sh_mask.h`, programs PCIe max-read-request policy, ASPM/LTR behavior, light-sleep/clock-gating state, indirect PCIe index/data offsets, and related NBIO registers. Some specific masks used by that file are outside this exact line range, but the access pattern is the same for the capability and endpoint fields defined here.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO/config-space hardware state whose lifetime is controlled by GPU reset, PCIe reset, function-level reset, power transitions, firmware policy, link retraining, suspend/resume, SR-IOV PF/VF policy, and host PCI enumeration.

The represented state includes bridge/device command bits, PCI/PCIe capability-list links, subsystem identity, BAR and ROM aperture fields, MSI routing data, PCIe device and link policy, AER masks/status/severity/logs, lane equalization and margining controls/status, ACS/ARI/multicast/LTR/L1 PM-substate policy, data-link feature status, high-speed PHY training state, ESM/CCIX capability and control, and endpoint function config header fields.

Several fields are status or sticky logs rather than ordinary writable configuration. AER status/log fields, link training/equalization status, lane margining status, emergency power-reduction detection, and pending/error bits are hardware-owned observations. Other fields are command strobes or side-effect controls, such as link retrain, function-level reset, completion-timeout policy, interrupt/message enables, and status clear bits. The header names bit positions but does not encode read/write side effects.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which provides matching `cfgPSWUSCFG0_0_*` and `cfgBIF_CFG_DEV0_EPF0_0_*` offsets for these config-space fields.
- `nbio_2_3_default.h`, where generated defaults exist for the same generation.
- AMDGPU helper macros and accessors such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Observed includes in this tree are `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 power-management files for Navi10/Sienna Cichlid. That places this header on the integration path for NBIO initialization, PCIe power management, ASPM/LTR, link configuration, interrupt setup, SR-IOV mailbox/GPU virtualization support, and GPU power-management policy.

Because the macros are untyped constants, a renamed field normally fails at compile time, but a wrong shift or mask can compile cleanly and corrupt an adjacent PCIe field at runtime.

## Risks And Edge Cases

- Chunk-boundary risk is high. The first lines are only the tail masks of `PSWUSCFG0_0_IRQ_BRIDGE_CNTL`; its shifts and early masks are in the previous chunk. The final line is only the `BIF_CFG_DEV0_EPF0_0_LINK_STATUS` marker; its fields are in the next chunk.
- Width and access-size mismatches matter. This chunk mixes 8-bit, 16-bit, and 32-bit PCI config fields, while the masks are C constants. Consumers must use access widths and offsets matching the generated register definition.
- AER fields are side-effect sensitive. Treating status/log/clear behavior as a normal read-modify-write register can hide errors, clear diagnostic evidence, or leave severity/mask policy inconsistent with the driver.
- PCIe link-control fields can cause interoperability regressions. Incorrect target speed, retrain, common-clock, ASPM, L1 PM-substate, LTR, DRS, equalization, or 16 GT/s settings can produce link instability, bandwidth loss, resume failures, or device disappearance.
- MSI fields affect interrupt routing. Wrong message address/data, multi-message enable, 64-bit address capability, or per-vector behavior can cause lost or spurious interrupts.
- ACS, ARI, multicast, CCIX, ESM, and SR-IOV-adjacent fields affect isolation and topology behavior. Using a bridge/upstream-port macro against endpoint-function offsets, or vice versa, is syntactically valid but semantically wrong.
- Repeated per-lane equalization and margining definitions are prone to off-by-one generation mistakes. A single lane-number shift/mask mismatch can make diagnostics report the wrong lane or train the wrong per-lane control.
- Capability-list pointer fields are structural. Wrong `CAP_ID`, `NEXT_PTR`, `PCIE_CAP_ID`, or capability version masks can break PCI capability traversal and feature detection.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware integration:

- Build AMDGPU configurations that include NBIO 2.3, Navi10/Sienna Cichlid SMU paths, SR-IOV support, PCIe ASPM/LTR, MSI, and AER support.
- Compare the generated `nbio_2_3_sh_mask.h` field names, widths, and masks against the matching AMD register database and `nbio_2_3_offset.h` config offsets.
- Exercise PCI enumeration and capability traversal; malformed capability IDs, next pointers, class/header fields, BAR fields, or MSI/PCIe capability layouts should appear as enumeration or lspci-style decode anomalies.
- Run PCIe link tests covering speed/width negotiation, retraining, ASPM, L1 PM substates, LTR, 16 GT/s status, equalization, lane error status, and lane margining diagnostics.
- Exercise interrupt delivery with MSI enabled and disabled; lost/spurious interrupts can indicate message-control or address/data mask drift.
- Use AER/error-injection or fault-observation paths where available to verify uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs decode correctly.
- In SR-IOV or virtualized environments, test PF/VF mailbox and function reset flows, because endpoint function config, FLR, ARI, ACS, and capability layouts are part of the isolation and reset contract.

## Chunk-Specific Notes For Merge

When the final per-file report is reconciled, this chunk should be merged with adjacent `nbio_2_3_sh_mask.h` chunks. The whole-file report should avoid presenting `PSWUSCFG0_0_IRQ_BRIDGE_CNTL` or `BIF_CFG_DEV0_EPF0_0_LINK_STATUS` as fully covered by this range alone, because both registers cross chunk boundaries.

### subset-b-002906: lines 4961-7402

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 4961-7402

## Scope

This chunk is a slice of AMDGPU's generated NBIO 2.3 shift/mask header. It contains C preprocessor constants only. There are no functions, typedefs, structs, runtime branches, allocation sites, locks, reference counts, or persistent software objects in this range.

The selected lines begin with the field definitions for `BIF_CFG_DEV0_EPF0_0_LINK_STATUS` after the register-name comment at line 4960. The range then covers a large part of the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` PCI configuration-space map: PCIe link/device capability registers, MSI/MSI-X, vendor-specific PCIe capabilities, virtual-channel capabilities, device serial number, Advanced Error Reporting, resizable BAR and power budgeting/DPA metadata, PCIe secondary/equalization/margining capabilities, ACS/ATS/PRI/PASID/multicast/LTR/ARI/SR-IOV/TPH/DLF/16GT PHY capability blocks, VF resizable BARs, and the AMD GPU IOV vendor-specific capability block.

Near the end of the range, the address block switches to `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`. This chunk covers the start of endpoint function 1's standard PCI config header and capability registers through `BIF_CFG_DEV0_EPF1_0_LINK_CAP__L1_EXIT_LATENCY_MASK`. The remaining `EPF1` link-capability masks continue just after the assigned line range, so file-level reconciliation must merge adjacent chunks before making whole-register claims.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

The header publishes the bitfield ABI for NBIO 2.3 PCIe/NBIF configuration registers. The macros are meant to be combined with sibling offset/default headers and AMDGPU register helpers to decode or update hardware register words. Each field usually appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit index for the field.
- `<REGISTER>__<FIELD>_MASK`, the mask for the encoded field in the 16-bit or 32-bit register word.

Examples in this range include `BIF_CFG_DEV0_EPF0_0_LINK_STATUS__CURRENT_LINK_SPEED__SHIFT` with `BIF_CFG_DEV0_EPF0_0_LINK_STATUS__CURRENT_LINK_SPEED_MASK`, AER fields such as `BIF_CFG_DEV0_EPF0_0_PCIE_UNCORR_ERR_STATUS__MALFORMED_TLP_STATUS_MASK`, GPU IOV fields such as `BIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_INTR_ENABLE__VF0_FLR_NOTIFY_MASK`, and the beginning of `EPF1` link capability fields such as `BIF_CFG_DEV0_EPF1_0_LINK_CAP__LINK_WIDTH_MASK`.

The companion `nbio_2_3_offset.h` supplies the matching config offsets for these symbols, for example `cfgBIF_CFG_DEV0_EPF0_0_LINK_STATUS`, `cfgBIF_CFG_DEV0_EPF0_0_LINK_STATUS2`, the `cfgBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` range, and `cfgBIF_CFG_DEV0_EPF1_0_LINK_CAP`. Runtime code includes this header through NBIO and virtualization files such as `amdgpu/nbio_v2_3.c` and `amdgpu/mxgpu_nv.c`.

## Important Macro Families

The first group describes endpoint function 0 PCIe capability state. `BIF_CFG_DEV0_EPF0_0_LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` expose current link speed and width, link training, data-link active status, completion-timeout support/control, ARI and atomic operation capability/control, LTR and OBFF capability/control, target link speed, compliance controls, deemphasis and equalization status, downstream-component presence, DRS, and related PCIe Gen3+ behavior.

The MSI and MSI-X groups define capability-list headers, MSI enable/multiple-message controls, 32-bit and 64-bit message address/data fields, vector masks and pending fields, MSI-X table/PBA BIR and offset fields, table size, function mask, and MSI-X enable. These macros name the PCI interrupt delivery configuration exposed by the endpoint's config space; actual interrupt routing is configured by PCI/MSI code and AMDGPU initialization paths.

The generic PCIe vendor-specific and virtual-channel capability groups expose enhanced capability headers, vendor-specific length/revision/vendor ID, VC capability/control/status registers, and VC0/VC1 resource capability/control/status fields. The VC resource macros cover port arbitration capability, rejected snoop/non-snoop transactions, maximum time slots, arbitration select/table offsets, resource identifiers, traffic-class masks, and negotiation pending/status fields.

The device serial number and Advanced Error Reporting blocks define serial-number dwords, AER capability headers, uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control fields, header logs, and TLP prefix logs. The AER masks name PCIe error conditions such as data-link protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic-op egress blocking, TLP prefix blocking, and poisoned TLP egress blocking.

The resizable BAR, power budgeting, and dynamic power allocation groups name PCIe extended capability registers for BAR1 through BAR6, selected power budget data, power budget capability, DPA substate capacity/status/control, and per-substate power allocation values. The BAR control macros expose BAR size and size-enable fields that must stay aligned with PCIe resource assignment and firmware policy.

The PCIe secondary, lane equalization, and lane margining groups provide link-control-3 equalization settings, lane error status, per-lane equalization controls for lanes 0-15, 16GT capability/control/status/parity mismatch fields, and per-lane margining control/status for lanes 0-15. These definitions support low-level PCIe signal integrity and training diagnostics, not high-level device logic.

The access/isolation capability group includes ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, and SR-IOV macros. Important examples are `BIF_CFG_DEV0_EPF0_0_PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_ATS_CAP`, `PCIE_ATS_CNTL`, `PCIE_PAGE_REQ_CNTL`, `PCIE_PAGE_REQ_STATUS`, `PCIE_PASID_CAP`, `PCIE_PASID_CNTL`, `PCIE_MC_*`, `PCIE_LTR_CAP`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, and `PCIE_SRIOV_*`. These define field layouts for request routing, address translation, PASID width/enablement, page-request status, multicast controls, latency tolerance, alternate routing ID behavior, and virtual-function BAR/page-size/count/stride metadata.

The TPH requester and data-link feature groups expose steering mode, ST table location/size, requester enable mode, local ST table size, and data-link feature exchange/status. The 16GT PHY capability block names Gen4/16GT equalization controls, link status, and parity mismatch status for local/RTM paths plus lane-specific equalization fields.

The GPU IOV vendor-specific capability block is the densest virtualization-oriented family in this chunk. `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV*` cover VSEC identity/length/revision, shadow SR-IOV state, interrupt enable/status bits for command completion and hang/FLR/VM-busy/mailbox events, reset control, hypervisor/VM mailbox dwords, context size/location/offset, total framebuffer accounting, global offsets/regions, peer-to-peer-over-XGMI enablement, per-VF framebuffer size/offset entries for VF0 through VF30, and scheduler dwords for UVD, VCE, GFX, and UVD1. These are PF/hypervisor-facing resource partitioning and mailbox layout definitions.

The final `EPF1` group begins a second endpoint-function config decoder block. It defines standard PCI header fields such as vendor/device ID, command/status, revision/class code, cache line, latency, header/BIST, BAR1-BAR6, CardBus pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, a vendor capability, power-management capability/status/control, PCIe capability header, device capability/control/status, and the first portion of link capability. This mirrors the standard PCI/PCIe config-space layout for function 1, but the assigned range ends before the full `LINK_CAP` field set is present.

## APIs, Types, And Functions

This chunk has no callable APIs, C types, or functions. Its public surface is the macro namespace consumed at compile time.

The practical API contract is the combination of:

- Register-name comments such as `//BIF_CFG_DEV0_EPF0_0_PCIE_UNCORR_ERR_STATUS`.
- `__SHIFT` macros for bit offsets.
- `_MASK` macros for field masks.
- Matching `cfg...` register offsets in `nbio_2_3_offset.h`.
- AMDGPU helper macros/functions outside this file, commonly `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

Because the constants are untyped, the C compiler cannot verify that a mask from one register family is paired with the correct offset. Correctness depends on generated-header consistency and careful use by versioned NBIO/PCIe/virtualization code.

## Control Flow

There is no executable control flow in this header slice. Runtime behavior is supplied by consumers:

1. Driver or firmware-facing code chooses a register offset from `nbio_2_3_offset.h` or from hardcoded SMN/config constants.
2. The code reads a 16-bit or 32-bit register value through PCIe, SOC15, or indirect config-space access helpers.
3. It uses the `__SHIFT` and `_MASK` definitions, often through `REG_GET_FIELD` or `REG_SET_FIELD`, to extract, test, clear, or encode a field.
4. It writes the modified value back, polls a status field, or reports the decoded field through a diagnostic path.

For integration context, `amdgpu/nbio_v2_3.c` includes `nbio_2_3_sh_mask.h` for NBIO 2.3 initialization and register programming. `amdgpu/mxgpu_nv.c` also includes this header and implements SR-IOV mailbox transactions using NBIO 2.3 register definitions and mailbox offsets. The control flow for mailbox valid/ack polling, GPU-access requests, doorbell setup, HDP remapping, link/power handling, and reset policy is in those `.c` files, not in this generated header.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware-visible PCI config and extended capability state whose lifetime is controlled by the GPU, PCIe hierarchy, firmware, PF/hypervisor policy, reset/FLR, suspend/resume, BACO/power transitions, and driver programming.

The represented hardware state includes link status and control, completion timeout configuration, MSI/MSI-X interrupt configuration, VC resource negotiation state, AER status/masks/severity/logs, BAR sizing controls, power budgeting and DPA values, lane equalization and margining diagnostics, ACS/ATS/PRI/PASID controls, multicast filters, LTR/ARI/SR-IOV configuration, TPH/data-link feature state, Gen4/16GT training and parity status, GPU IOV resource/mailbox/interrupt state, and the start of function 1's standard PCI configuration space.

Some fields are persistent configuration until reset or reprogramming, such as BAR sizing, ACS/ATS/PASID enables, SR-IOV page size and VF counts, MSI/MSI-X table configuration, and GPU IOV framebuffer allocation fields. Others are hardware-owned status or logs, such as link training/equalization status, AER status and header/TLP prefix logs, lane error/margining status, SR-IOV status, and mailbox valid/ack/status bits. Some registers have command or write-one-to-clear semantics in the underlying hardware, but this header intentionally only names bit positions and masks.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must remain synchronized with `nbio_2_3_offset.h` and `nbio_2_3_default.h`, which provide the corresponding offsets and reset/default values. For example, the offset header maps the GPU IOV VSEC fields from `cfgBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV` through scheduler dwords, and maps `cfgBIF_CFG_DEV0_EPF1_0_LINK_CAP` for the final partial register family in this chunk.

Runtime integration points include:

- NBIO 2.3 setup in `amdgpu/nbio_v2_3.c`, which includes this header with the offset/default headers and uses NBIO register fields for doorbells, memory access, interrupts, HDP remapping, power/clock behavior, and ASIC-specific setup.
- SR-IOV and GPU virtualization in `amdgpu/mxgpu_nv.c`, which uses NBIO 2.3 register definitions and mailbox offsets for PF/VF message valid/ack handshakes and GPU access requests.
- PCIe interrupt setup using MSI/MSI-X fields and table/PBA locations.
- PCIe link diagnostics and policy code using link speed, width, training, equalization, 16GT, DRS, and lane error/margining fields.
- AER/RAS/error handling paths that decode or mask correctable and uncorrectable PCIe error conditions and consume header/TLP prefix logs.
- Isolation and address-translation policy through ACS, ATS, PRI, PASID, ARI, SR-IOV, and GPU IOV per-VF resource fields.
- Power and resource reporting through power budgeting, DPA, LTR, OBFF, and link power-management fields.

The macros also align structurally with later NBIO/NBIF generations. Similar names appear in NBIO 7.x and NBIF 6.x/7.x headers, but masks should not be copied across generations without checking the exact offset and field definitions.

## Risks And Edge Cases

- The chunk boundary is artificial. The `LINK_STATUS` register-name comment is one line before the assigned start, and the `EPF1 LINK_CAP` register continues after line 7402. Adjacent chunks are required for complete per-register and per-file analysis.
- Generated names are long and repetitive. Register families such as lane 0-15 equalization/margining, VF0-VF30 framebuffer fields, and UVD/VCE/GFX scheduler dwords are vulnerable to index drift, skipped entries, or field-width mistakes if edited by hand.
- Some mask names include repeated words like `...ERR_MASK__..._MASK`, which reflects the generated `register__field_MASK` convention. Renaming these for readability would break consumers.
- Width and access-size assumptions matter. Many PCI capability fields are 16-bit-style masks such as `0xFFFFL` or `0x00FFL`, while AER logs, BAR controls, mailbox dwords, scheduler dwords, and many GPU IOV fields are full 32-bit values. Consumers must use the correct register access width and offset.
- AER status, page-request status, MSI pending, link status, margining status, and mailbox bits may be sticky, hardware-owned, clear-on-write, or handshake-driven. The header does not encode side effects, so generic read-modify-write logic can be unsafe on some fields.
- MSI/MSI-X programming is interrupt-delivery sensitive. Wrong masks for enable/function mask, table BIR/offset, PBA BIR/offset, message address/data, or per-vector masks can cause lost interrupts, spurious interrupts, or broken virtualization interrupt routing.
- ACS/ATS/PRI/PASID/ARI/SR-IOV/GPU IOV fields are isolation-sensitive. Incorrect programming can route requests through the wrong function, enable address translation unexpectedly, expose the wrong VF framebuffer slice, or break PF/VF reset and mailbox ownership.
- Link training, 16GT equalization, and lane margining fields are platform-sensitive. Wrong decode or control writes can misreport link health, force unsuitable compliance/equalization behavior, or hide signal-integrity failures.
- GPU IOV mailbox and interrupt bits are handshake surfaces between PF, VF, hypervisor, firmware, and the guest driver. Misinterpreting valid/ack/interrupt bits can wedge access negotiation or cause a VF to miss reset/hang notifications.
- The final `EPF1` register block is only a prefix in this range. Treating it as complete would omit several `LINK_CAP` masks and later `EPF1` link/control/status/capability families.

## Test Signals

Useful validation signals for any change touching this header area include:

- Build AMDGPU configurations that include NBIO 2.3, SR-IOV, PCIe AER, MSI, MSI-X, ATS, PASID, and virtualization support. Missing or renamed macros should fail at compile time in versioned NBIO or virtualization code.
- Run generated-header consistency checks against the AMD register database or against sibling `nbio_2_3_offset.h`/`nbio_2_3_default.h` so each offset has the expected shift/mask fields and no unintended overlaps.
- Enumerate affected GPUs and verify PCI capability traversal for MSI/MSI-X, PCIe, AER, ACS/ATS/PRI/PASID, ARI, SR-IOV, and vendor-specific GPU IOV capability blocks.
- Exercise MSI/MSI-X interrupt delivery under bare-metal and SR-IOV configurations, including vector masking and pending-bit behavior where available.
- Use PCIe link diagnostics to confirm decoded speed, width, training state, equalization, DRS, 16GT, and lane error/margining status match hardware and platform expectations.
- In SR-IOV deployments, create and destroy VFs, validate VF BAR and framebuffer sizing, exercise PF/VF FLR/reset notifications, and confirm GPU IOV mailbox valid/ack interrupts and per-VF framebuffer fields remain isolated.
- Exercise AER or error-injection diagnostics, where supported, to confirm uncorrectable/correctable error status, masks, severity, header logs, and TLP prefix logs decode to the expected bit names.
- Test suspend/resume, FLR, BACO/power transitions, and reset paths to ensure PCIe config, MSI/MSI-X, link, SR-IOV, and GPU IOV state is restored or renegotiated correctly.

## Chunk Notes For Merge

When creating the final per-file research document, merge this with neighboring chunks for the same `nbio_2_3_sh_mask.h` source. The merged report should preserve that this file is a generated NBIO 2.3 hardware bitfield catalog, while this specific chunk covers late `EPF0` PCIe capability and GPU IOV VSEC definitions plus the beginning of `EPF1` PCI/PCIe configuration definitions.

### subset-b-002907: lines 7403-9846

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 7403-9846

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts in the tail of `BIF_CFG_DEV0_EPF1_0_LINK_CAP`, covers a large PCIe configuration-space and extended-capability block for endpoint function 1 (`BIF_CFG_DEV0_EPF1_0_*`), then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and covers the beginning of endpoint function 2 (`BIF_CFG_DEV0_EPF2_0_*`). It ends inside `BIF_CFG_DEV0_EPF2_0_DEVICE_STATUS`; the remaining status masks continue after this assigned range. Although the repository path is under a local `ceph-client` mirror, this file is AMD GPU PCIe/NBIO hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header chunk is to publish the bit layout contract for NBIO 2.3 PCI/PCIe config decoder registers. Each field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve the field in the register value.

AMDGPU NBIO/BIF code combines these masks with companion register-address headers for the same ASIC generation and register access helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`. The header itself only names fields; it does not define access policy or side-effect semantics.

## Important Macro Families

The first part of the chunk finishes PCIe link capability/control/status coverage for endpoint function 1. It includes link power management, retrain and disable controls, common clock and extended sync, autonomous width/speed controls, bandwidth-management/autonomous-bandwidth interrupt status, data rate signaling, negotiated speed/width, data-link active, Gen2+ link capability/control/status fields, equalization completion and phase status, crosslink/presence reporting, and downstream-component presence.

The function-1 device capability/control block includes PCIe capabilities such as completion timeout support and disable, ARI forwarding, atomic operations, ID-based ordering, latency tolerance reporting, OBFF, end-to-end TLP prefix support/blocking, emergency power reduction, fast role swap, ten-bit tags, max payload/read request sizing, relaxed ordering, no-snoop, auxiliary power management, FLR initiation, and ordinary device status/error bits.

Interrupt capability macros cover MSI and MSI-X for function 1. The MSI block defines capability-list IDs and next pointers, MSI enable and multi-message controls, 32-bit and 64-bit message address/data words, per-vector masks, and pending bits. The MSI-X block defines table size, function mask, enable, table BIR/offset, and PBA BIR/offset fields.

Several PCIe extended-capability families are present for function 1: vendor-specific headers and data dwords, virtual channel capability/control/status and VC0/VC1 resource registers, device serial number dwords, advanced error reporting status/mask/severity/capability/header-log/TLP-prefix-log registers, resizable BAR capability/control for BAR1 through BAR6, power budget data selection/data/capability, dynamic power allocation capability/status/control and substate power allocation registers, secondary PCIe/link-control/lane-error/lane-equalization registers, ACS, ATS, page request interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data link feature, PHY 16 GT/s, lane margining, VF resizable BAR, and AMD vendor-specific GPUIOV blocks.

The GPUIOV vendor-specific region is especially virtualization-oriented. It defines VSEC metadata, an SR-IOV shadow field, interrupt enable/status, reset control, HVVM mailbox dwords, context, total framebuffer and offset/region fields, peer-to-peer over XGMI enable, per-VF framebuffer offset/size fields for VF0 through VF30, and scheduling/resource dwords for UVD, VCE, GFX, and UVD1 engines. These masks are part of the PF-visible contract used to partition or report GPU resources to virtual functions.

The second part of the range begins endpoint function 2. It covers standard PCI header fields: vendor/device IDs, command/status, revision and class codes, cache-line and latency fields, header/BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, a vendor capability list, power-management capability/status-control, USB-related SBRN/FLADJ/DBESL fields, PCIe capability list/header, PCIe device capability/control, and the start of PCIe device status.

## Control Flow

There is no runtime control flow in this chunk. The effective use pattern is driven by consuming driver code:

1. Select the matching register offset from the NBIO 2.3 offset header or an ASIC-specific register table.
2. Read a PCIe config/MMIO register value through AMDGPU register access helpers.
3. Use the `__SHIFT` and `_MASK` constants, commonly through `REG_GET_FIELD` or `REG_SET_FIELD`, to decode or update a field.
4. Write the updated value back, or poll/status-check the decoded bits according to the PCIe/NBIO programming sequence.

The repeated lane, BAR, VF, and capability blocks imply table-like hardware layout, but this header does not implement iteration. Any loop over lanes, BARs, VFs, or functions lives in the AMDGPU NBIO/SR-IOV/PCIe code that selects the corresponding register offset and macro family.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware and PCI configuration state owned by the GPU, PCIe fabric, firmware, and driver.

Some represented fields are configuration that may persist until reset, FLR, suspend/resume, power transition, or explicit reprogramming: PCI command enables, BAR values, MSI/MSI-X message data and masks, link/device controls, AER masks and severity bits, DPA allocations, ACS/ATS/PASID/PRI controls, SR-IOV counts and VF BARs, resizable BAR settings, power-management controls, and GPUIOV framebuffer/resource partitioning.

Other fields are hardware-owned observations, command strobes, sticky logs, or write-one-to-clear status: device/link status, AER error status and header logs, TLP prefix logs, lane error and equalization status, margining status, MSI pending bits, PME status, SR-IOV status, data-link feature status, and GPUIOV interrupt/reset/mailbox status. The macro names do not encode read/write side effects; consumers must use PCIe and AMDGPU programming rules for the actual access semantics.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with the matching offset/default headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`; offsets identify the register addresses while this file identifies the fields within those registers.

Primary integration is with AMDGPU NBIO, PCIe, interrupt, reset, RAS/AER, power-management, and virtualization paths. The function-1 and function-2 PCI config macros are consumed when driver code configures or diagnoses PCI command/status, link training, link speed/width, MSI/MSI-X delivery, AER masking/logging, resizable BARs, DPA and power budgeting, ATS/PRI/PASID address-translation features, ACS isolation, SR-IOV VF enumeration, VF BAR layout, GPUIOV resource accounting, and function-level reset behavior.

The macros are untyped integer constants. A renamed or missing macro generally fails at compile time, but a wrong shift or mask can compile cleanly and cause the driver to program an adjacent field or decode the wrong status bit. Because this is generated ASIC metadata, manual edits should be treated as hardware ABI changes and checked against the authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first line is already inside `BIF_CFG_DEV0_EPF1_0_LINK_CAP`, and the final line stops inside `BIF_CFG_DEV0_EPF2_0_DEVICE_STATUS`. The merge lane must combine adjacent chunks before making whole-register or whole-file coverage claims.
- Width and access-size assumptions matter. The range mixes 8-bit PCI header fields, 16-bit capability/control/status words, and 32-bit extended-capability dwords. Using the wrong access width or offset family can silently corrupt neighboring PCIe fields.
- Status and clear fields are not type-distinguished. AER status, device status, MSI pending, PME status, lane error, and GPUIOV interrupt/status fields may have sticky or write-one-to-clear behavior in hardware; ordinary read-modify-write handling can be unsafe.
- Interrupt definitions are delivery-critical. Incorrect MSI/MSI-X enable, function mask, table/PBA offset, message address/data, or vector mask fields can cause lost interrupts, spurious interrupts, or broken isolation under virtualization.
- Link control and equalization fields are interoperability-sensitive. Incorrect target speed, autonomous speed/width disable, retrain, common clock, DRS, margining, or 16 GT/s equalization masks can cause link training failures, bandwidth regressions, or unstable resume behavior.
- Virtualization blocks are dense and repetitive. Per-VF framebuffer fields, SR-IOV counts/strides/device IDs, VF BAR controls, ACS/ATS/PASID/PRI, and GPUIOV mailbox/resource registers are easy places for off-by-one VF or lane mistakes that grant, deny, or report the wrong resource.
- AER and error-log masks affect diagnostics and recovery. Wrong masks or severities can hide real PCIe errors, trigger unnecessary fatal handling, or make logged headers/TLP prefixes decode incorrectly.
- Full-width fields such as BARs, message addresses, mailbox dwords, scheduler dwords, and log dwords are not self-validating. Pairing a full-width mask with the wrong register offset can overwrite unrelated hardware/firmware coordination state.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers, with PCIe, MSI/MSI-X, AER, SR-IOV, ATS/PRI/PASID, and resizable BAR support enabled; missing macros should surface as compile failures.
- Run generated-header consistency checks against the NBIO 2.3 register database and sibling offset headers, including shift/mask pair width checks and non-overlap checks within each register.
- Boot/enumeration tests confirming the GPU and its endpoint functions expose expected PCI headers, capability-list traversal, BARs, class codes, command/status bits, and power-management capabilities.
- PCIe link tests covering speed/width reporting, retraining, Gen2+/16 GT/s equalization, lane error status, margining, data-link active reporting, DRS, and suspend/resume transitions.
- MSI/MSI-X interrupt tests under physical and virtualized configurations, including vector masking, pending bits, table/PBA placement, and function mask behavior.
- AER/error-injection or fault-observation tests validating uncorrectable/correctable status, mask, severity, header logs, TLP prefix logs, and recovery handling.
- SR-IOV/GPUIOV tests validating VF counts, VF BAR sizing, per-VF framebuffer offset/size assignment, PF-to-HV mailbox behavior, GPUIOV interrupt/reset fields, and scheduler/resource dword programming for every represented VF/resource family.

## Chunk-Specific Notes For Merge

This chunk should be merged with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final source-tree-aligned per-file research document. Preserve that this slice specifically covers the function-1 PCIe capability tail through GPUIOV resource definitions, then the beginning of function-2 PCI/PCIe configuration definitions through the start of device status.

### subset-b-002908: lines 9847-12321

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 9847-12321

## Scope

This chunk is a generated AMD NBIO 2.3 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, allocation, locking, or executable control flow.

The range starts in the middle of `BIF_CFG_DEV0_EPF2_0_DEVICE_CNTL`, after that register's shift definitions and after the first few mask definitions. It then covers the rest of PCI configuration-space and enhanced-capability field layouts for endpoint function 2 (`BIF_CFG_DEV0_EPF2_0_*`), the full standard/header and most extended capability layout for endpoint function 3 (`BIF_CFG_DEV0_EPF3_0_*`), and begins the `nbio_nbif0_syshub_mmreg_syshubdirect` block. The chunk ends mid-register inside `SYSHUB_TRANS_IDLE_SOCCLK` after the first five VF idle masks; the remaining VF/PF idle masks are in the following chunk.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIO 2.3 PCIe endpoint configuration and SYSHUB SOC clock controls. Each named hardware field generally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The matching register address metadata lives in `nbio_2_3_offset.h`, with `cfgBIF_CFG_DEV0_EPF2_0_*`, `cfgBIF_CFG_DEV0_EPF3_0_*`, and SYSHUB symbols mapping these field names to PCI config-space or MMIO offsets. Runtime AMDGPU code includes this header and combines the constants with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The `BIF_CFG_DEV0_EPF2_0_*` portion describes endpoint function 2 PCIe capability registers from device control/status onward. It names the standard PCIe device and link control/status fields: correctable, non-fatal, fatal, unsupported-request, auxiliary-power, pending-transaction, emergency power reduction, negotiated link speed/width, link training, link bandwidth notification, ASPM/clock power management, FLR initiation, max payload size, max read request size, relaxed ordering, no-snoop, extended tags, and completion timeout controls.

The same EPF2 block defines MSI and MSI-X capabilities. These include capability IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector-mask controls, 32-bit and 64-bit MSI address/data/mask/pending fields, MSI-X table size/function mask/enable bits, and table/PBA BIR and offset fields. These constants support interrupt capability exposure and programming through the endpoint's PCI config image.

EPF2 also covers SATA capability and indirect data port registers, vendor-specific PCIe enhanced capability headers and payload words, AER enhanced capability registers, header/TLP-prefix logs, resizable BAR-like BAR capability/control registers for BAR1 through BAR6, power budget data selection/data/capability fields, dynamic power allocation capability/status/control/substate power allocation fields, ACS capability/control fields, PASID capability/control fields, ARI capability/control fields, and TPH requester capability/control plus 64 steering-tag table entries.

The `BIF_CFG_DEV0_EPF3_0_*` block starts at the beginning of endpoint function 3's PCI configuration image. It includes vendor/device ID, command/status, revision/class code bytes, cache line/latency/header/BIST, BAR1-BAR6, CIS pointer, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant/max latency, vendor and power-management capabilities, SATA adjustment registers, PCIe capability registers, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power budget, DPA, ACS, PASID, ARI, and TPH requester fields. Most EPF3 field layouts mirror EPF2, but this chunk carries EPF3 from the standard header rather than beginning mid-capability.

The TPH steering tables are highly repetitive for both EPF2 and EPF3. `BIF_CFG_DEV0_EPF[23]_0_PCIE_TPH_ST_TABLE_0` through `_63` each define lower and upper 8-bit entries. These fields are used to expose or program requester steering-tag mappings, so table index/order correctness matters even though the constants are mechanically regular.

The final SYSHUB block switches from endpoint PCI config space to the `nbio_nbif0_syshub_mmreg_syshubdirect` address block. `SYSHUB_DS_CTRL_SOCCLK` defines host client, DMA client, and top-level SYSHUB SOCCLK deep-sleep allow/enable bits. `SYSHUB_DS_CTRL2_SOCCLK` provides the deep-sleep timer field. The `SYSHUB_BGEN_ENHANCEMENT_*_SOCCLK` registers expose bypass and immediate-enable controls for host and DMA switch clock-generation behavior. `SYSHUB_TRANS_IDLE_SOCCLK` is a one-bit-per-function idle bitmap for VF0 and upward plus PF, but this chunk stops before the full bitmap is present.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing belongs to AMDGPU NBIO, PCIe, SMU, interrupt, SR-IOV, and power-management code that includes it:

1. Driver code selects a register offset from `nbio_2_3_offset.h`.
2. It reads or prepares a 16-bit or 32-bit config/MMIO value with PCIe or SOC15 access helpers.
3. It uses these `__SHIFT` and `_MASK` constants directly or through register helper macros to update or decode individual fields.
4. It writes the value back, polls a status bit, clears sticky status, or leaves hardware/firmware to update status-owned fields.

For this chunk, common runtime flows include PCIe capability enumeration/programming, interrupt capability control, AER status collection/clearing, BAR capability setup, PASID/ACS/ARI/TPH virtualization capability handling, DPA/power-budget reporting, and SYSHUB clock/deep-sleep policy programming.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO and PCI config-space state owned by the GPU, firmware, host PCIe fabric, and driver.

The represented hardware state includes PCI command/status bits, PCIe device and link capabilities, interrupt address/data/mask/pending state, AER error masks/severity/status and logs, BAR sizing/control data, power budget and DPA substate values, ACS/PASID/ARI/TPH enablement, TPH steering-tag table contents, endpoint identity/header fields, and SYSHUB SOCCLK deep-sleep and idle status/control bits. Some fields are static capability descriptions, some are driver-programmed controls, some are hardware-updated status, some are sticky error logs, and some behave as command or write-one-to-clear fields. The generated constants do not encode those side effects.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`. The offset header provides address symbols such as `cfgBIF_CFG_DEV0_EPF2_0_DEVICE_CNTL`, while this shift/mask header provides the field layout for values read from or written to those addresses.

Direct integration is through AMDGPU code that includes `nbio/nbio_2_3_sh_mask.h`, including `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c`. Those consumers rely on the generated names rather than duplicating bit positions.

The EPF2/EPF3 PCI configuration macros integrate with PCIe endpoint exposure, function-level reset, AER/error handling, MSI/MSI-X interrupts, SR-IOV and virtual function capability surfaces, PASID/ACS/ARI isolation and addressing features, TPH steering, resizable BAR/power capability reporting, and power-management policy. The SYSHUB macros integrate with clock gating, deep sleep, transaction-idle detection, and suspend/resume or runtime power paths.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first line is already inside `BIF_CFG_DEV0_EPF2_0_DEVICE_CNTL`, and the final line stops inside `SYSHUB_TRANS_IDLE_SOCCLK`. Adjacent chunks are required before making whole-register claims for those two registers.
- These macros are untyped integer constants. A wrong mask value can compile cleanly while updating the wrong hardware bit; a renamed or missing macro is more likely to fail at build time.
- PCIe control fields such as FLR, max payload, max read request, completion timeout, relaxed ordering, no-snoop, ASPM/link control, ARI, PASID, ACS, TPH, and AER are interoperability-sensitive. Incorrect values can break enumeration, DMA ordering, virtualization isolation, interrupt delivery, error reporting, or link recovery.
- MSI/MSI-X address/data/mask/pending fields have interrupt-delivery side effects. Width or alignment mistakes can cause lost, misrouted, or unexpectedly unmasked interrupts.
- AER status, severity, mask, header log, and TLP-prefix log fields include sticky or clear-on-write behavior. Treating status/clear bits as ordinary retained configuration can hide errors or clear diagnostic evidence.
- BAR capability/control and DPA/power-budget fields can affect resource sizing and power policy. Incorrect masks may expose invalid apertures, wrong BAR sizes, or misleading power capabilities.
- TPH steering tables are dense and repetitive. Off-by-one table indexing or lower/upper-entry confusion can silently steer traffic with the wrong tag.
- SYSHUB SOCCLK deep-sleep and idle bits are power and liveness sensitive. Enabling deep sleep without respecting host/DMA/PF/VF idle state can cause hangs, lost wakeups, or power-management regressions.

## Test Signals

Useful validation is mostly build, boot, and hardware-integration oriented:

- Build AMDGPU for ASICs using NBIO 2.3 headers; direct macro drift should surface as compile failures in NBIO, SMU, MXGPU, PCIe, or interrupt code.
- Boot affected hardware and confirm PCI enumeration shows stable device/function IDs, BARs, PCIe capabilities, MSI/MSI-X capabilities, AER capability, PASID/ACS/ARI/TPH capabilities, and expected link speed/width.
- Exercise MSI and MSI-X interrupt delivery under graphics, compute, display, and reset workloads; lost interrupts or stuck pending bits point to config mask/offset issues.
- Run PCIe error handling and reset paths covering AER status/logging, FLR initiation/completion, completion timeout behavior, link retraining, and suspend/resume.
- In SR-IOV or multi-function configurations, validate EPF2/EPF3 capability exposure, VF isolation features, PASID/ARI/ACS controls, and TPH steering behavior.
- Exercise runtime power management, clock gating, and suspend/resume while monitoring SYSHUB deep-sleep enablement and transaction-idle status; hangs, failed wakeups, or unexpected power use are strong signals of field-layout drift.

### subset-b-002909: lines 12322-14790

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 12322-14790

## Scope

This chunk is a generated AMD NBIO 2.3 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, dynamic allocation, locking, persistence code, or executable control flow.

The range starts in the middle of `SYSHUB_TRANS_IDLE_SOCCLK`: only the masks for VF5 through VF30 and PF are present here, while the matching shifts and early VF masks belong to the previous chunk. It then covers SYSHUB SOCCLK/SHUBCLK/LCLK controls, HST and DMA per-client reset/QoS controls, NIC400 interconnect ordering and QoS registers, the SION arbitration/credit block, SHUB reset controls, GDCL/GDCSOC/GDCSHUB RAS status/control registers, and a large `BIF_CFG_DEV0_SWDS` PCI/PCIe bridge configuration-space decode. The range ends inside `BIF_CFG_DEV0_SWDS_LANE_4_MARGINING_LANE_STATUS`, after the `LANE_4_RECEIVER_NUMBER_STATUS_MASK` definition; the remaining lane-4 status fields and later margining lanes continue in the next chunk.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIO 2.3 registers. Each generated field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or preserve a field in a 16-bit or 32-bit register value.

The companion address metadata lives in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`. Runtime AMDGPU code combines the offset header and this shift/mask header through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_NO_KIQ`, `WREG32_NO_KIQ`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening SYSHUB block names SOCCLK transaction-idle masks for SR-IOV virtual functions and the physical function. These masks let software or firmware observe which VF/PF endpoints are idle before clock, reset, virtualization, or power transitions. The chunk then defines `SYSHUB_HP_TIMER_SOCCLK`, `SYSHUB_MGCG_CTRL_SOCCLK`, `SYSHUB_CPF_DOORBELL_RS_RESET_SOCCLK`, scratch registers, client-mask controls, and hang handling bits for dropping unexpected responses on SW0/SW1 client lanes.

The HST and DMA control families repeat per switch/client lane. `HST_CLK0_SW{0,1}_CL{0,1,2}_CNTL` exposes `FLR_ON_RS_RESET_EN` and `LKRST_ON_RS_RESET_EN` bits. `DMA_CLK0_SW0_SYSHUB_QOS_CNTL` controls QoS mode and min/max QoS values, while `DMA_CLK0_SW0_CL{0,1}_CNTL` adds FLR/link-reset enables, static QoS override, and read/write weighted-round-robin weights. These fields are hardware policy inputs for reset propagation and fabric arbitration.

The SHUBCLK/LCLK SYSHUB block covers deep sleep and clock gating. `SYSHUB_DS_CTRL_SHUBCLK` has deepsleep-allow and deepsleep-enable bits; `SYSHUB_DS_CTRL2_SHUBCLK` provides the deep-sleep timer; `SYSHUB_MGCG_CTRL_SHUBCLK` mirrors the SOCCLK medium-grain clock-gating fields for enable, mode, hysteresis, and host/DMA/register/AER disables; and scratch/select registers expose full-width scratch state plus USB0/USB1 selection bits. The two `SYSHUB_BGEN_ENHANCEMENT_*_SHUBCLK` comment markers have no field macros in this chunk, indicating empty or reserved generated register descriptions.

The NIC400 families describe ARM NIC-400 interconnect behavior for several ASIB, AMIB, and IB ports. Simple `*_FN_MOD` and `*_FN_MOD_BM_ISS` registers expose read/write issuing override bits. The `NIC400_2_ASIB_{0,1}` QoS groups expose rate, flow-control, outstanding-transaction, priority, burst, rate, target-latency, KI flow-control, and QoS-range fields for AW and AR channels. These are low-level fabric tuning knobs where an incorrect mask can alter ordering, throughput, fairness, or forward progress.

The `nbio_nbif0_nbif_sion_SIONDEC` address block contains a dense SION schedule and credit table for client lanes CL0 through CL3. For each client lane, it provides full-width low/high halves for read-response, write-response, and request burst targets, matching time-slot registers, request/data/read-response/write-response pool credit allocation registers, and two SION control registers. `SION_CNTL_REG0` exposes twenty soft override bits for clock-gating control groups, and `SION_CNTL_REG1` contains livelock watchdog threshold and clock-gating-off hysteresis fields.

The `nbio_nbif0_gdc_rst_GDCRST_DEC` block defines SHUB/GDC reset surfaces. It includes PF FLR reset bits for device 0 PF0-PF3, a graphics-driver mode1 reset bit, three link reset bits, a dense PF0 VF FLR reset bitmap for VF0-VF30 plus a soft-PF reset bit, hard and soft reset enable fields for core/register/STY/NIC400/SDP/SION-AON blocks, and SDP port reset bits for A2S, NBIFSION BIF, ATHUB, ATDMA, INT, MP4, GDC, NTB, and SION-AON paths.

The `nbio_nbif0_gdc_ras_gdc_ras_regblk` block covers RAS status and controls for GDC link-to-core and core-to-link paths. Central status registers report egress-stall and error-event detection for GDCL, GDCSOC, and GDCSHUB. `GDCSOC_RAS_LEAF{0..5}_CTRL` registers enable detection, poison/parity/receiver-error handling, generated error events, egress stalls, propagation, and, for leaf2, RAS interrupts. Leaf2 also has miscellaneous control registers for slave access disable, poisoned response generation, egress-stall response enable, and timeout/fatal-error classification. Matching `GDCSOC_RAS_LEAF{0..5}_STATUS` registers report received error events, poison/parity detections, generated status, and propagated status.

The `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` block maps a PCI-to-PCIe bridge-like configuration space for `BIF_CFG_DEV0_SWDS`. It starts with standard PCI IDs, command/status, revision/class/interface, cache line, latency, header/BIST, BARs, bus numbers, I/O and memory windows, prefetchable windows, capability pointer, ROM base, interrupt line/pin, and bridge control. The field widths match PCI configuration-space conventions, including 8-bit class fields, 16-bit status/control fields, and full-width address fields.

The same BIF configuration block then exposes PM, PCIe, MSI, SSID, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, ACS, DLF, 16GT PHY, and PCIe margining capabilities. Important field groups include power-state and PME controls, device/link capability/control/status fields, max payload and max read request size, FLR capability, completion timeout and atomic operation controls, LTR and OBFF controls, target link speed and equalization state, MSI address/data fields, VC0/VC1 resource maps, AER uncorrectable/correctable status/mask/severity and header/TLP-prefix logs, ACS source-validation/translation/blocking/direct-translated/P2P controls, DLF exchange-enable/status fields, 16GT link speed/equalization/parity mismatch state, per-lane 16GT transmit presets for lanes 0-15, and margining capability/status plus margining control/status fields for lanes 0 through the start of lane 4.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing belongs to AMDGPU NBIO, virtualization, SMU, PCIe, power-management, and error-handling code that includes it:

1. Driver code selects an MMIO, SMN, PCIe, mailbox, or configuration-space register offset from `nbio_2_3_offset.h` or a local address define.
2. It reads or prepares a 16-bit or 32-bit value through SOC15, PCIE, or KIQ-safe register helpers.
3. It uses the `__SHIFT` and `_MASK` constants, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to update or decode a specific field.
4. It writes the value back, polls status bits, or records decoded state according to the hardware programming sequence.

Direct include sites in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`. `nbio_v2_3.c` demonstrates the typical pattern by combining this header with `nbio_2_3_offset.h`, reading/writing NBIO registers, and using generated field masks for doorbell ranges, framebuffer access, interrupt control, clock/power controls, strap decoding, and PCIe link behavior. `mxgpu_nv.c` uses the same NBIO 2.3 generated headers around VF/PF mailbox and virtualization flows.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO-backed hardware state whose lifetime is controlled by the GPU, firmware, PCIe link state, driver initialization, runtime power management, SR-IOV PF/VF policy, FLR/link reset, suspend/resume, and fatal error handling.

The represented state includes clock-gating and deep-sleep configuration, scratch registers, VF/PF transaction-idle visibility, reset propagation controls, QoS and WRR arbitration policy, NIC400 outstanding/rate/latency/flow-control limits, SION schedule and pool-credit tables, reset request/status bits, RAS control/status bits, PCI/PCIe configuration-space fields, capability-list linkage, MSI programming state, AER error status/mask/severity/logs, virtual-channel negotiation state, ACS/DLF policy, 16GT link/equalization/parity state, and PCIe margining command/status payloads. Some fields are configuration that persists until reset or reprogramming; others are status, sticky error state, command strobes, write-one-to-clear status, or hardware-owned training/negotiation state. The header names bit positions but does not encode access size, reset defaults, read/write side effects, required ordering, or polling rules.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 2.3 register database. This shift/mask file must stay synchronized with `nbio_2_3_offset.h` and `nbio_2_3_default.h`; offsets identify where a register lives, defaults document reset values, and this file documents how fields are packed inside the register. A correct field name with a stale mask is particularly dangerous because it compiles cleanly while programming the wrong hardware bits.

The integration surface is AMDGPU's NBIO/BIF layer, PCIe link-management code, SR-IOV support, mailbox virtualization paths, RAS/error-reporting paths, SMU power-management code, doorbell setup, reset flows, and low-power clock-gating code. The BIF configuration-space macros also align with generic PCIe concepts managed by the Linux PCI core, but they are accessed here as GPU-internal register definitions rather than as ordinary host PCI config reads.

The macro families in this chunk have strong hardware coupling. SYSHUB and SION fields affect fabric liveness and clocking; NIC400 fields affect interconnect ordering and throughput; SHUB reset fields affect PF/VF isolation and recovery; GDC RAS fields affect whether poison, parity, receiver-error, egress-stall, interrupt, and propagation events are surfaced; and BIF config fields affect PCIe enumeration, link training, error handling, MSI, virtual channels, ACS, DLF, Gen4/16GT PHY behavior, and margining.

## Risks And Edge Cases

- The assigned range has artificial boundaries. It starts mid-register in `SYSHUB_TRANS_IDLE_SOCCLK` and ends mid-register in `BIF_CFG_DEV0_SWDS_LANE_4_MARGINING_LANE_STATUS`. File-level reconciliation must join adjacent chunks before making whole-register claims about those two registers.
- These are untyped preprocessor constants. A typo in a mask value, an offset/mask mismatch, or use with the wrong register can compile successfully and only fail as a hardware behavior regression.
- Reset and FLR bitmaps are dense. Off-by-one errors in `SHUB_PF0_VF_FLR_RST` can reset the wrong VF or fail to reset the intended VF, which is a virtualization isolation and recovery risk.
- Clock-gating and deep-sleep fields can make register paths inaccessible or change wakeup latency. Incorrect `SYSHUB_MGCG_CTRL_*`, `SYSHUB_DS_CTRL*`, SION soft-overrides, or hysteresis programming can cause hangs, missed wakeups, or power regressions.
- NIC400 and SION QoS/credit fields are fabric-liveness-sensitive. Wrong outstanding limits, rate controls, target latencies, time slots, burst targets, or pool credits can cause throughput collapse, starvation, or deadlock-like symptoms.
- RAS control/status fields have side effects outside local status reporting. Incorrect masks can suppress error propagation, create unexpected egress stalls, miss poison/parity errors, or produce interrupt storms.
- PCIe configuration and capability fields have strict protocol meanings. Incorrect command/status, bridge-window, power-management, MSI, max-payload, completion-timeout, atomic, LTR, VC, ACS, AER, DLF, 16GT equalization, or margining values can break enumeration, suspend/resume, link training, hot reset, or interoperability with specific platforms.
- AER status, RAS status, PME status, parity mismatch, equalization, and margining status fields may be sticky or hardware-owned. The header cannot tell callers whether a bit is read-only, write-one-to-clear, self-clearing, or requires a specific sequence.
- Several registers are full-width scratch or address payloads. Using a full-width `0xFFFFFFFF` mask against the wrong offset can silently overwrite firmware/driver coordination state or address programming.

## Test Signals

Useful validation is mostly build, integration, and hardware oriented:

- Build AMDGPU with NBIO 2.3 consumers enabled. Missing or renamed macros should fail in `nbio_v2_3.c`, `mxgpu_nv.c`, and SMU11 files that include `nbio_2_3_sh_mask.h`.
- Exercise NBIO initialization, doorbell setup, interrupt setup, framebuffer access enable/disable, and HDP/PCIe paths on ASICs that use the NBIO 2.3 headers; register access failures, hangs, or stale memory are strong mask/offset drift signals.
- Run clock-gating and runtime power-management tests with BIF/NBIO medium-grain clock gating and light sleep toggled; watch for power regressions, wakeup failures, register read timeouts, and link instability.
- In SR-IOV configurations, validate PF/VF mailbox traffic, VF FLR/reset recovery, VF idle detection, and isolation behavior across all represented VF bits.
- Run PCIe link tests across suspend/resume, hot reset or FLR, link retraining, MSI delivery, AER reporting, ACS policy, and 16GT-capable links. Equalization failures, unexpected completion timeouts, AER storms, or bad max-payload/read-request behavior point to this family.
- Use RAS/error-injection or platform diagnostics, where available, to confirm GDC leaf/central status, error propagation, stall generation, interrupt routing, and clear behavior.
- For platforms exposing PCIe margining or 16GT diagnostics, verify margining ready/software-ready status, lane control/status payload echo, per-lane 16GT preset fields, and parity mismatch reporting.

### subset-b-002910: lines 14791-17171

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 14791-17171

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, dynamic storage, locks, or executable branches. The range covers 2,164 `#define` entries and starts in the middle of the PCIe lane-margining definitions, at the masks for lane 4 status and the complete lane 5-15 control/status pairs. It ends in the middle of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4`, after the `STRAP_ATOMIC_EN_DEV0_F0` shift but before the rest of that register's shifts and masks.

Major covered register families are:

- PCIe lane-margining control/status fields for `BIF_CFG_DEV0_SWDS_LANE_5_MARGINING_LANE_CNTL` through `LANE_15`, plus the tail of lane 4 status from the previous chunk.
- PF system/VF indirect MMIO aperture fields: `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- `RCC_STRAP0` strap registers for global BIF behavior, device 0 downstream port straps, endpoint function 0 straps, and endpoint function 1 straps.
- Runtime RCC endpoint/downstream PCIe controls for device 0: endpoint interrupt/status, DPA, PME, TX/RX controls, link-speed controls, downstream-port controls, VDM support, PCIe margining parameter controls, bus controls, feature-misc controls, link controls, requester-ID restore, LTR switch latency, and multi-host arbitration.
- BIF PF/VF registers for BME-low status, unsupported atomic error logging, self-ring doorbell GPA aperture, HDP coherency flush, GPU HDP flush request/done bits, transaction-pending status, mailbox message buffers, mailbox interrupts, and VM/hypervisor mailbox fields.
- Shadow configuration-space bridge fields: shadow command, BARs, bus numbers, I/O/memory/prefetchable apertures, interrupt/bridge control, and SUC index/data indirect access.
- `RCC_STRAP1` internal strap mirrors for device 0-2 downstream port straps, BIF straps, and the start of device 0 endpoint function 0 straps.

Although this path sits under `sources/distributed-fs/ceph-client`, the file is AMD GPU NBIO PCIe/MMIO metadata, not Ceph or distributed-filesystem logic.

## Purpose

The purpose of this slice is to publish the bit-level ABI for NBIO 2.3 registers. Each register field follows the generated AMD naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for placing or extracting a field value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or clearing that field in a 32-bit register.

The paired `nbio_2_3_offset.h` header supplies the MMIO register offsets such as `mmRCC_BIF_STRAP2`, `mmRCC_DEV0_EPF0_STRAP0`, `mmBIF_BX_PF_GPU_HDP_FLUSH_REQ`, `mmBIF_BX_PF_GPU_HDP_FLUSH_DONE`, `mmMAILBOX_MSGBUF_TRN_DW0`, and `mmMAILBOX_INT_CNTL`. This shift/mask header supplies the field definitions consumed by `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_FIELD_MASK`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_PCIE`, `RREG32_PCIE`, `WREG32_NO_KIQ`, and related AMDGPU register helpers.

Operationally, the slice defines the NBIO register contract for PCIe capability straps, ASPM/LTR timing, SR-IOV capability advertisement, doorbell aperture routing, HDP cache flush signaling, host/VF mailbox transport, shadow PCI bridge state, PCIe lane margining, and low-level error/status handling.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the generated macro namespace.

Important macro groups include:

- `BIF_CFG_DEV0_SWDS_LANE_*_MARGINING_LANE_CNTL` and `*_STATUS`: per-lane receiver number, margin type, usage model, and payload fields for PCIe lane margining. This chunk completes lanes 5-15 and carries the tail of lane 4 status.
- `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`: indirect MMIO index/data fields, including low/high offset and aperture select. These are the field-level contract for accessing an indexed register aperture rather than a direct MMIO register.
- `RCC_STRAP0_RCC_BIF_STRAP0` through `RCC_STRAP0_RCC_BIF_STRAP6`: BIF strap state for link generation disable/kill bits, clock power management, VGA/ROM/memory aperture settings, PX capability, error-ignore policy, fuse/ROM strap validity, software write disable, margining readiness, SWUS aperture sizing and prefetchability, hardware/software revision bits, link-reset behavior, DLF/16GT/margin enablement, LTR in ASPM L1 disable, ASPM/LDN timers, power-brake deglitch/status fields, and reserved strap bits.
- `RCC_STRAP0_RCC_DEV0_PORT_STRAP0` through `PORT_STRAP9`: downstream-port straps for ARI/ACS/AER, completion-abort error handling, device ID, interrupt pin, max payload/link width, dummy endpoint-function enable, port type, reset slot clock, slot power limit/scale/value, ECRC, link bandwidth notification, ASPM support, L0s/L1 latency, MSI/PME/PME-clock behavior, DPA, LTR, OBFF, power indicator/control, attention indicator/button, hotplug, surprise down, MRL sensor, electromechanical interlock, no-command-complete support, component latency, and power budget data.
- `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` through `EPF0_STRAP13`: endpoint function 0 identity and capability straps: device/revision IDs, function enable, D-states, SR-IOV VF device ID and page-size support, SR-IOV enable/total VFs, 64-bit BAR/Resizable BAR, PASID/ATS/ACS/AER/ARI, DPA, DSN, VC, MSI/MSI-X capability, page request, PASID privilege/execute/global invalidate support, subsystem/vendor IDs, power enable, function-level reset, PME support, interrupt pin, auxiliary power support, doorbell/memory/register/ROM aperture sizes, VF aperture sizes, VGA disable, VF MSI multi-capability, SR-IOV VF mapping mode, VM disable, and VF BAR0/2 size fields.
- `RCC_STRAP0_RCC_DEV0_EPF1_STRAP*`: endpoint function 1 straps for a second function, including identity, MSIX table/PBA BIR, ATI capability pointer, SR-IOV window, VC, AER, MSI/MSI-X, PME, FLR, memory aperture, subsystem/vendor IDs, and several reserved fields.
- `RCC_EP_DEV0_0_EP_PCIE_*`: endpoint runtime controls and status for Unsupported Request reporting, malformed atomic ops, interrupt enables/status, bus master/memory enable, non-fatal/fatal/correctable/system-error signaling, LTR message values and requirements, DPA capability/substate power allocation, PME, TX completion/NPH/NPD tuning, requester ID, PCIe error controls, RX ignore policy, and endpoint link-speed strap bits.
- `RCC_DWN_DEV0_0_*` and `RCC_DWNP_DEV0_0_*`: downstream and downstream-port PCIe controls for register access enables, config-RD CRS return, RX ignore behavior, bus master/memory enable, config-control, strap status, link-speed strap bits, link-bandwidth notification disable, multifunction strap, and LTR message information received from the endpoint.
- `RCC_DEV0_0_RCC_MARGIN_PARAM_CNTL0/1`: lane-margining capability description, including voltage/timing support, independent direction/sampler flags, sample-reporting method, number and max offset of timing/voltage steps, sampling rates, max lanes, and sample count.
- `RCC_DEV0_0_RCC_BUS_CNTL`, `RCC_FEATURES_CONTROL_MISC`, `RCC_DEV0_LINK_CNTL`, `RCC_CMN_LINK_CNTL`, `RCC_EP_REQUESTERID_RESTORE`, `RCC_LTR_LSWITCH_CNTL`, and `RCC_MH_ARB_CNTL`: root-complex bus policy, poison/UR/ECRC/MSI behavior, link down entry/exit, L1/L0s/LDN PME blocking, DMA idle checks, requester-ID restore, LTR latency, and arbitration mode/priority fields.
- `BIF_BME_STATUS` and `BIF_ATOMIC_ERR_LOG`: bus-master-enable low-status and unsupported atomic error status/clear bits.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH/LOW` and `DOORBELL_SELFRING_GPA_APER_CNTL`: self-ring doorbell GPA aperture base, enable, mode, and size fields.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, and `GPU_HDP_FLUSH_DONE`: register/memory HDP flush controls and per-engine request/done bits for CP0-CP9 and SDMA0-1.
- `MAILBOX_MSGBUF_TRN_DW0` through `TRN_DW3`, `MAILBOX_MSGBUF_RCV_DW0` through `RCV_DW3`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`: SR-IOV host/VF mailbox payload words, valid/ack handshake bits, interrupt enables, and compact VM/hypervisor mailbox fields.
- `SHADOW_*`, `SUC_INDEX`, and `SUC_DATA`: shadowed PCI bridge command/address/window/IRQ fields and indirect SUC access fields.
- `RCC_STRAP1_*`: an internal strap block that mirrors many `RCC_STRAP0` downstream-port and BIF strap layouts for device 0 and extends to device 1 and device 2 port straps. The chunk ends before `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` is complete.

## Control Flow

The header has no runtime control flow. Runtime sequencing is supplied by the AMDGPU consumers that include it:

1. `nbio_v2_3_get_rev_id()` reads `mmRCC_DEV0_EPF0_STRAP0`, masks with `RCC_DEV0_EPF0_STRAP0__STRAP_ATI_REV_ID_DEV0_F0_MASK`, shifts by `RCC_DEV0_EPF0_STRAP0__STRAP_ATI_REV_ID_DEV0_F0__SHIFT`, and returns a revision ID. It avoids the read for SR-IOV VFs because guest reads can return `0xffffffff`.
2. `nbio_v2_3_enable_doorbell_selfring_aperture()` writes self-ring doorbell aperture base registers and composes `BIF_BX_PF_DOORBELL_SELFRING_GPA_APER_CNTL` fields for enable, mode, and size.
3. `nbio_v2_3_get_hdp_flush_req_offset()` and `nbio_v2_3_get_hdp_flush_done_offset()` expose HDP flush request/done register offsets. The `nbio_v2_3_hdp_flush_reg` table maps engine names to `GPU_HDP_FLUSH_DONE` masks for CP0-CP9 and SDMA0-1 so shared HDP flush code can request and poll per-engine coherency flushes.
4. `nbio_v2_3_program_ltr()` clears `RCC_BIF_STRAP2__STRAP_LTR_IN_ASPML1_DIS_MASK`, writes endpoint TX LTR controls, and enables LTR in the PCIe device control path when the platform advertises LTR support.
5. `nbio_v2_3_program_aspm()` programs ASPM-related fields and timers, including `RCC_BIF_STRAP3__STRAP_VLINK_ASPM_IDLE_TIMER_MASK`, `RCC_BIF_STRAP3__STRAP_VLINK_PM_L1_ENTRY_TIMER_MASK`, and `RCC_BIF_STRAP5__STRAP_VLINK_LDN_ENTRY_TIMER_MASK`.
6. `mxgpu_nv.c` uses the mailbox payload registers and valid/ack control bytes to implement VF-to-PF requests, polling, acknowledgement, interrupt enablement, FLR notification handling, RAS bad-page notification, and GPU access handshakes.
7. SMU power-management files include this header alongside the offset header so NBIO/PCIe fields are available to SMU11 platform code, even though many fields in this exact chunk are not directly referenced in the portions inspected.

Many strap, PCIe error-control, lane-margining, shadow, and diagnostic fields are not actively manipulated by `nbio_v2_3.c` in the inspected tree. They remain part of the generated hardware ABI for firmware, platform initialization, validation tools, debug paths, or future driver code.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes MMIO-backed hardware state in the NBIO/PCIe fabric.

The represented hardware state includes:

- Boot/fuse/ROM strap-derived state: device/function identity, capability advertisement, link generation availability, aperture sizes, SR-IOV topology, D-state support, FLR/PME/MSI/MSI-X, PASID/ATS/ACS/AER/ARI, Resizable BAR, DPA, LTR, OBFF, power budget, slot, hotplug, and endpoint/downstream port behavior.
- Runtime link and power-management state: ASPM timers, L0s/L1/LDN behavior, LTR behavior, link-down entry/exit state, clock/power management enables, and link bandwidth notification controls.
- Error and status state: UR/malformed atomic reporting, ECRC and poisoned completion behavior, BME-low status, unsupported atomic error logs with clear bits, endpoint/downstream interrupt status, transaction-pending bits, and root-complex error logging policy.
- Doorbell and coherency state: self-ring doorbell GPA aperture base/mode/size, HDP register/memory flush controls, and per-engine HDP flush request/done status.
- Virtualization state: SR-IOV capability straps, VF aperture sizing/mapping, mailbox payload and handshake state, VM/hypervisor mailbox fields, and VF/host reset or RAS notification transport state.
- Shadow PCI configuration state: bridge command bits, BAR shadows, subordinate bus numbers, I/O and memory window shadows, prefetchable-memory upper/lower bounds, IRQ/bridge controls, and indirect SUC register access.
- PCIe lane-margining state: per-lane control and status fields for selected receiver, margin type, usage model, payload, and returned status.

Persistence is hardware-defined. Strap values are usually latched from fuses, ROM straps, pins, or firmware-controlled strap sources and can be read-only, write-protected, or only writable before `WRITE_DISABLE`. Runtime control and status registers persist until reset, power-gating loss, suspend/resume reprogramming, FLR, or explicit driver/firmware writes. Handshake, clear, request/done, interrupt, and error-log fields may be transient, write-one-to-clear, or self-clearing depending on the register.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` supplies matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h` supplies generated default values for the same hardware generation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes and consumes this header for revision ID extraction, doorbell self-ring aperture programming, HDP flush register/mask exposure, ASPM/LTR strap programming, and broader NBIO setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header and uses the mailbox offsets and handshake fields for SR-IOV guest/host messaging on Navi-class GPUs.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c` include the NBIO 2.3 offset and shift/mask headers as part of SMU11 power-management platform integration.
- Common AMDGPU register helpers in `amdgpu.h`, `soc15_common.h`, and related SOC15 infrastructure interpret these macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_FIELD_MASK`, `SOC15_REG_OFFSET`, and raw MMIO/PCIE read-write helpers.

Key integration surfaces are:

- PCIe power management and ASPM: `RCC_BIF_STRAP2`, `RCC_BIF_STRAP3`, and `RCC_BIF_STRAP5` fields interact with `nbio_v2_3_program_aspm()` and `nbio_v2_3_program_ltr()`. Wrong masks here can alter LTR behavior, ASPM entry timing, or low-power state transitions.
- HDP coherency: `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` fields are wired into the NBIO HDP flush table. Incorrect engine masks can make the driver poll the wrong done bit or miss a flush completion.
- SR-IOV mailbox: `MAILBOX_MSGBUF_*`, `MAILBOX_CONTROL`, and `MAILBOX_INT_CNTL` define the register-level protocol used by `mxgpu_nv.c` for GPU access, reset, initialization data, RAS bad-page notifications, CPER/RAS requests, and host FLR notifications.
- Device identity and SR-IOV capabilities: `RCC_DEV0_EPF0_STRAP*` and the mirrored `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*` expose fields that determine PCI config-space identity and capabilities; the driver directly uses the ATI revision field and may rely indirectly on the rest through PCI enumeration and firmware setup.
- Doorbell routing: self-ring GPA aperture fields are written during NBIO setup so GPU queues can use the doorbell aperture correctly.
- Shadow config-space and SUC fields: these define internal register views used by firmware/platform code and by any debug/validation paths that inspect or emulate bridge config windows.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently program another PCIe/NBIO field, causing broken enumeration, wrong capabilities, SR-IOV misconfiguration, invalid doorbell routing, HDP flush hangs, link instability, or broken power management.
- The chunk starts and ends mid-register-family. Lane 4 margining status begins in the previous chunk, and `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` is incomplete at the end. The merge lane must reconcile adjacent chunks before making complete file-level claims about those registers.
- Strap registers are not ordinary mutable configuration. Some fields are latched, firmware-owned, fuse/ROM-derived, write-protected, or only valid in privileged PF contexts. Treating every mask as safe to write risks violating platform or SR-IOV ownership.
- SR-IOV behavior is privilege-sensitive. `nbio_v2_3_get_rev_id()` already avoids an endpoint strap read for VFs because it can return `0xffffffff`; similar PF-owned strap, aperture, mailbox, or shadow registers may be inaccessible or virtualized for guests.
- Mailbox valid/ack bits are sequencing-sensitive. `mxgpu_nv.c` clears transmit-valid before sending so stale host ACK state does not make a new request appear acknowledged. Incorrect masks or byte offsets can cause deadlocks, lost messages, or reset/RAS event handling failures.
- HDP flush bits are command/status synchronization points. Polling the wrong done bit or ignoring firmware-reserved bits can leave stale CPU/GPU-visible data after command submission, SDMA, or memory-management activity.
- ASPM/LTR fields interact with platform policy. Timer or disable-bit mistakes can cause link power-state hangs, poor idle power, PCIe timeouts, or regressions that appear only on removable devices, Thunderbolt paths, or systems with different LTR support.
- Error-control and clear fields can change observability. Misprogramming UR/ECRC/poison/malformed-atomic/clear bits can hide real PCIe errors, create false clears, or alter Linux PCIe AER behavior.
- Repeated strap layouts are easy to confuse. `RCC_STRAP0`, `RCC_STRAP1`, `RCC_DEV1`, and `RCC_DEV2` port strap names have similar field layouts but different address blocks and potentially different ownership.
- Lane-margining controls may be used by validation or PCIe service flows. Bad per-lane receiver, margin type, usage model, or payload fields can produce misleading margin data or disturb active links if used without hardware sequencing.

## Test Signals

Useful validation signals for this chunk are generated-header consistency, build coverage, and NBIO/PCIe runtime behavior:

- Build AMDGPU with Navi/NBIO 2.3 support enabled. Direct consumers in `nbio_v2_3.c`, `mxgpu_nv.c`, and SMU11 platform files should compile against the offset and shift/mask macros.
- Compare this header slice against AMD's authoritative NBIO 2.3 register database and the paired `nbio_2_3_offset.h`; every field name must match the correct register offset and bit range.
- Boot supported Navi hardware and confirm PCIe enumeration exposes expected device/revision IDs, BAR apertures, SR-IOV capabilities, MSI/MSI-X, PASID/ATS/ACS/AER/ARI, FLR, PME, and Resizable BAR behavior.
- Exercise `nbio_v2_3_get_rev_id()` on PF and VF configurations. PF should decode the expected ATI revision from `RCC_DEV0_EPF0_STRAP0`; VF should follow the guarded default path rather than trusting a poisoned strap read.
- Validate doorbell setup by enabling self-ring doorbells and running graphics, compute, SDMA, and VCN queues that rely on doorbell writes.
- Stress HDP flush paths with command submission, SDMA copies, CPU/GPU coherency tests, and suspend/resume. Timeouts or stale data point to request/done mask or remap problems.
- Exercise SR-IOV mailbox workflows: GPU init/fini/reset access, init-data exchange, host FLR notification, bad-page notification, RAS error count/CPER/poison paths, and mailbox ACK/valid interrupts.
- Test ASPM/LTR on systems with and without LTR path support, including removable/Thunderbolt devices if available. Watch for link-state transition failures, PCIe AER noise, idle-power regressions, or resume failures.
- Run PCIe error-injection or validation tests for unsupported atomic operations, BME-low status, ECRC/poison behavior, and AER reporting to ensure status/clear bits behave as expected.
- For hardware validation, exercise lane-margining status/control on lanes 5-15 and compare reported receiver/type/usage/payload status against expected PCIe margining behavior. Keep those tests isolated from normal runtime paths.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `BIF_CFG_DEV0_SWDS_LANE_4_MARGINING_LANE_STATUS` register and lanes before 5. This chunk starts with the last lane 4 status masks and then covers lanes 5-15. The next chunk owns the remainder of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` and later NBIO 2.3 registers. The final per-file research document should merge these boundaries before describing complete lane 4 margining or complete `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` semantics.

### subset-b-002911: lines 17172-19549

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 17172-19549

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register shift/mask header segment. It contains preprocessor constants only: 2,170 `#define` macros across 194 register groups, split almost evenly between `__SHIFT` and `_MASK` definitions. There are no functions, types, structs, enums, storage definitions, or executable C control flow in this range.

The line range starts in the tail of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4`, covers a large set of PCIe endpoint strap fields for functions on device 0 and devices 1-2, then covers NBIO/RCC port control, endpoint and downstream PCIe control, BIF miscellaneous controls, DMA attribute overrides, error logs, performance counters, power-gating controls, SMN master controls, virtual-wire controls, and ends in `NBIF_SDP_VWR_VCHG_DIS_CTRL`.

## Purpose

The header provides bit positions and masks for NBIO/NBIF registers used by Navi-era AMD GPUs with NBIO IP version 2.3. The matching offset header names the register addresses; this file names the fields inside those 32-bit registers. Driver code uses these macros with `RREG32_*()` and `WREG32_*()` read/modify/write sequences so it can set or test individual hardware bits without embedding numeric constants in C code.

The chunk's main hardware surfaces are:

- PCIe function straps for endpoint functions: device ID, revision ID, function enablement, power-state support, PASID, ATS, ACS, AER, DPA, VC, MSI/MSI-X, PM, FLR, atomics, class code, subsystem IDs, BAR/aperture sizing, ROM aperture, TPH, resize BAR support, SR-IOV VF aperture sizing, and VF mapping.
- RCC port controls: VDM support, bus/master disable gates, root/error-log handling, max payload/read request sizing, link-down entry/exit, common link PM/LTR controls, endpoint requester ID restore, multi-host arbitration, and PCIe margining capability parameters.
- Endpoint/downstream PCIe controls: interrupt enables/status bits, unsupported-request handling, LTR transmit parameters, DPA capability and power allocation, PME, TX/RX error handling, link speed straps, and downstream strap controls.
- BIF miscellaneous controls: interrupt-line polarity/enable, outstanding virtual-channel allocations, DMA/GMI/GSI behavior toggles, BME and RCC/BIH BME error logs, DMA transaction attribute overrides, PASID checks/status, SDP controls, performance counter controls and values, power-gating and deep-sleep controls, SMN behavior, and virtual-wire trigger/reset controls.

## Important Macro Families

The endpoint strap definitions repeat a common PCIe configuration pattern across physical functions:

- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP5`, `STRAP8`, `STRAP9`, and `STRAP13` finish function 0 fields in this chunk. The key fields include subsystem vendor ID, doorbell/FB/register/ROM/VF aperture sizes, VF MSI capability, SR-IOV VF mapping mode, outstanding page request capability, BAR compliance, ROM BAR chicken bit, VF register protection disable, and class code.
- `RCC_STRAP1_RCC_DEV0_EPF1_STRAP0/2/3/4/5/6/7/10/11/12/13` provide the complete function 1 strap set. This is the fullest strap group in the chunk and includes PASID/ATS/ACS/AER, DPA, MSI/MSI-X, power management, FLR/PME, BAR and ROM apertures, TPH, and resize BAR support for apertures 1-3.
- `RCC_DEV0_EPF2_STRAP*` through `RCC_DEV0_EPF6_STRAP*` define similar strap sets for functions 2-6, with some functions exposing fewer aperture or TPH fields than function 1.
- `RCC_DEV1_EPF0_STRAP*` and `RCC_DEV2_EPF0_STRAP*` repeat the device 1 and device 2 function 0 strap surfaces, including function enablement, PASID capability, interrupts, FLR/PME, apertures, and class code.

The RCC and PCIe port-control blocks are grouped by address block comments:

- `nbio_nbif0_rcc_dev0_RCCPORTDEC` contains `RCC_DEV0_1_RCC_*` fields for VDM support, bus control, feature workaround/compatibility controls, link entry/exit, LTR, multi-host arbitration, and PCIe margining parameters.
- `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC` contains `RCC_EP_DEV0_1_*` endpoint-side PCIe fields: scratch, control, interrupt enable/status, RX/TX controls, LTR fields, DPA capability/latency/control/power allocation, PME, error controls, and link speed.
- `nbio_nbif0_rcc_dwn_dev0_RCCPORTDEC` and `nbio_nbif0_rcc_dwnp_dev0_RCCPORTDEC` contain downstream-side equivalents for reserved/scratch/control/config/RX/bus/cfg/strap/error/link-speed/LTR-message fields.

The BIF miscellaneous block is the densest part:

- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` expose behavior toggles for virtual wire unit-ID checks, DMA/GSI/GMI ordering, atomic checks, SR-IOV VF/PF behavior, PCIe capability protection, D-state/PME behavior, poison/ACS/unsupported-command reporting, BME-drop handling, SDP data forcing, and GMI message block-level selection.
- `BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG0` define per-function status and clear bits for DMA/RCCBIH activity while bus mastering is low.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`, `_F2_F3`, `_F4_F5`, and `_F6_F7` define paired per-function fields for ID-based ordering, relaxed ordering, snoop/no-snoop, and block-level override behavior.
- `BIF_ATOMIC_ERR_LOG_DEV0_F0` through `_F7`, `BIF_DMA_MP4_ERR_LOG`, `BIF_PASID_ERR_LOG`, and `BIF_PASID_ERR_CLR` define latched error and explicit clear bits for atomic and PASID-related failures.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the four `BIFC_PERF_CNT_*` value registers define enable/reset/select fields and counter values for MMIO and DMA read/write performance observations.
- `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, `NBIF_PG_MISC_CTRL`, `NBIF_MGCG_CTRL_LCLK`, and `NBIF_DS_CTRL_LCLK` define NBIF power-gating, medium-grain clock-gating, and LCLK deep-sleep controls.
- `SMN_MST_CNTL0`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL1` through `SMN_MST_EP_CNTL5` define SMN arbitration, zero byte-enable read/write handling, posted-mask behavior, multi-transaction-ID disable bits, and error-response data behavior for upstream, downstream, and endpoint PF paths.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL_1`, and `NBIF_SDP_VWR_VCHG_DIS_CTRL` define SMN/SDP virtual-wire disable, reset-default, trigger, write-trigger, and differential-detect behavior.

## Control Flow

There is no runtime control flow in this header. Runtime control flow is in users that include this generated mask header with `nbio_2_3_offset.h`.

`drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` is the primary in-tree consumer. It includes this header and uses masks from the same generated register family in read/modify/write sequences for NBIO setup. One direct use from this chunk is `NBIF_MGCG_CTRL_LCLK__NBIF_MGCG_REG_DIS_LCLK_MASK` in `nbio_v2_3_program_aspm()`: the code reads `smnNBIF_MGCG_CTRL_LCLK`, sets the register-disable clock-gating bit, and writes the register only if the value changed. The same source also programs PCIe/ASPM/LTR, interrupt, doorbell, HDP flush, and SR-IOV-related NBIO state with other NBIO 2.3 macros from adjacent chunks.

`drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header for the NBIO 2.3 virtualization register surface. Even where this exact chunk is not directly referenced by name, its PASID, doorbell, interrupt, atomic-error, and virtual-wire definitions describe the same PF/VF coordination and error-state hardware used by MxGPU paths.

`drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include the NBIO 2.3 offset and mask headers so SMU power-management code can reference NBIO register definitions. Display resource code includes the offset header but not this mask header.

## State and Persistence

The header itself has no mutable state. Its macros describe hardware register state with different persistence characteristics:

- Strap fields describe boot/configuration state consumed by PCIe configuration and capability presentation. Some strap-write controls, such as `NBIF_STRAP_WRITE_CTRL__NBIF_STRAP_WRITE_ONCE_ENABLE_MASK`, indicate write-once behavior where an incorrect program sequence can survive until reset.
- Interrupt, error-log, PASID, atomic, BME, and performance-counter registers expose live or latched hardware state. Several error-log registers provide separate status bits in the low halfword and clear bits in the high halfword, so software must preserve the status/clear semantics when writing.
- Doorbell, aperture, VF mapping, DMA attribute, SMN, virtual-wire, power-gating, and clock-gating controls persist as programmed hardware configuration until changed by the driver, firmware, PF/hypervisor, or device reset.
- Power-management and clock-gating fields can affect subsequent register access timing and availability, especially `NBIF_PGMST_CTRL`, `NBIF_PG_MISC_CTRL`, `NBIF_MGCG_CTRL_LCLK`, and `NBIF_DS_CTRL_LCLK`.

Because these masks are compile-time constants, any incorrect bit assignment becomes a runtime hardware programming error in every driver build that consumes the generated header.

## Dependencies

This chunk depends on the AMDGPU SOC15/NBIO register-access conventions:

- Matching register offset macros live in `nbio_2_3_offset.h`; this file only supplies field masks and shifts.
- Consumers combine offsets and masks through helpers such as `RREG32_SOC15()`, `WREG32_SOC15()`, `RREG32_PCIE()`, and `WREG32_PCIE()`.
- Register update helpers typically read a 32-bit register, clear a field with `~FIELD_MASK`, set field bits shifted by `FIELD__SHIFT`, and write the result back.
- Field names and bit positions must stay synchronized with AMD's generated ASIC register database, reset/default headers, firmware expectations, PCIe capability layout, and SR-IOV PF/VF model for NBIO 2.3.

The chunk also has cross-generation neighbors. Similar field families appear in `nbif_6_3_1_sh_mask.h` and later `nbio_7_2_0_sh_mask.h`, but field sets and bit positions are not guaranteed identical. Code must include the versioned header matching the ASIC IP block.

## Integration Points

The main integration point is the AMDGPU NBIO layer:

- NBIO bring-up and power-management callbacks in `nbio_v2_3.c` use these masks to program ASPM/LTR behavior, clock gating, doorbell ranges, HDP flush behavior, interrupt handling, and register-remap behavior.
- PCIe capability presentation and SR-IOV behavior depend on the strap masks in this chunk. Misstating PASID, ATS, ACS, AER, MSI/MSI-X, FLR, BAR, or VF aperture fields can change what capabilities the function exposes to the OS or hypervisor.
- Error reporting and RAS/debug paths depend on the BIFC, atomic, PASID, and PCIe error-log masks to distinguish status bits from write-one-clear bits.
- Virtualization integration depends on the per-function fields in `BIFC_DMA_ATTR_OVERRIDE_*`, BME/PASID/atomic logs, doorbell/VF aperture straps, and virtual-wire controls; these fields help separate PF/VF behavior and coordinate PF/VF communication.
- Power-management integration depends on NBIF power-gating, deep-sleep, and LCLK clock-gating fields, including the directly used `NBIF_MGCG_CTRL_LCLK__NBIF_MGCG_REG_DIS_LCLK_MASK`.

## Risks

- Hardware contract drift: this is generated register data. A wrong mask or shift can program the wrong bit while still compiling cleanly.
- Read/modify/write hazards: many registers contain unrelated fields. Using a stale mask, failing to preserve reserved bits, or confusing a mask with a shifted value can alter adjacent hardware behavior.
- Write-one-clear confusion: BME, atomic, DMA, and PASID error-log registers include clear bits separate from status bits. Treating the whole register as ordinary persistent control state can accidentally clear diagnostics or fail to clear latched errors.
- Virtualization sensitivity: SR-IOV VF aperture, doorbell, PASID, BME, and virtual-wire fields sit on PF/VF boundaries. Bad programming can cause guest-visible failures, mailbox timeouts, interrupt loss, or isolation problems.
- Power-state sensitivity: NBIF clock-gating and power-gating bits affect register access and link behavior. Incorrect settings can produce intermittent failures that depend on ASPM, D-state, or idle timing.
- Chunk-boundary risk: this work item begins in the middle of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` and ends before `NBIF_SDP_VWR_VCHG_DIS_CTRL` is complete. The final per-file document must reconcile adjacent chunks before claiming complete coverage of those two register groups.

## Test Signals

Useful validation signals are mostly compile-time, generated-header consistency, and hardware/runtime tests:

- Build AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c`; undefined or conflicting macros catch include/version drift.
- Run generated-header consistency checks: every field should generally have one `__SHIFT` and one `_MASK`, masks should align with shifts and field widths, and repeated per-function blocks should differ only by function/device naming where expected.
- Compare selected fields against the matching NBIO 2.3 register database and `nbio_2_3_offset.h` register names, especially chunk-boundary registers and repeated `DEV0_F0` through `DEV0_F7` error-log/override groups.
- Exercise PCIe probe/resume paths with ASPM enabled and disabled; the direct `NBIF_MGCG_CTRL_LCLK` programming path should not break link entry/exit or register access.
- Exercise SR-IOV PF/VF probe, reset, mailbox/access-request, doorbell, MSI/MSI-X, PASID, and FLR paths. Failures here are strong signals of wrong strap, aperture, interrupt, virtual-wire, or error-clear fields.
- Exercise RAS/debug paths that read and clear BIFC, PASID, atomic, and DMA error logs; expected status bits should latch and clear without disturbing unrelated fields.
- Exercise power-management suspend/resume and idle workloads; NBIF power-gating, deep-sleep, and clock-gating fields should not produce hangs, missing interrupts, or stale HDP/SMN behavior.

### subset-b-002912: lines 19550-21952

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 19550-21952

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register shift/mask header segment. It contains preprocessor constants only: 2,159 `#define` entries over 221 register names, with 1,076 `__SHIFT` macros and 1,083 `_MASK` macros in the requested line range. There are no C functions, structs, enums, executable branches, or storage objects in this chunk.

The range starts in the middle of `NBIF_SDP_VWR_VCHG_DIS_CTRL`: the shift definitions and the register comment are just before line 19550, while this chunk contains only its mask definitions. The range ends in the middle of `BIF_CFG_DEV0_EPF0_PCIE_DPA_ENH_CAP_LIST`: the shifts and `CAP_ID_MASK` are present, but `CAP_VER_MASK` and `NEXT_PTR_MASK` continue after line 21952. The merge lane should combine adjacent chunks before treating either boundary register as complete.

## Purpose

`nbio_2_3_sh_mask.h` supplies bitfield locations for NBIO/NBIF registers on AMD GPUs using the NBIO 2.3 IP block. The matching `nbio_2_3_offset.h` file names the MMIO/config offsets; this file names each register field's bit shift and mask. Driver code uses these macros through AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `WREG32_FIELD15()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `RREG32_PCIE()`, and `WREG32_PCIE()` so code can program PCIe/NBIO hardware without hard-coding raw bit numbers.

This chunk covers several related NBIO surfaces:

- SDP virtual-wire voltage-change and reset controls for endpoint functions and a downstream switch port.
- BIFC A2S credit, tag, response-reorder, and virtual-channel mapping controls.
- RCC PFC blocks for AMDGFX, AMDGFXAZ, USB, and PD controller endpoints, including LTR, PME restore, sticky AER restore, TLP header/prefix restore, and auxiliary-power override fields.
- BIF reset, function-level reset, D3hot-to-D0 reset, instance-reset, interrupt status/mask, and PF/VF reset trigger fields.
- BIF link/RAS leaf control and status fields, plus IOHUB RAS interrupt wiring.
- SWUS SUM index/data fields.
- Device 0 endpoint function 0 PCI configuration-space fields from vendor/device IDs through PCIe, MSI, MSI-X, VC, serial-number, AER, enhanced BAR, power-budget, and the beginning of DPA enhanced capability fields.

## Important Macro Families

The macros follow the generated register-field naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit position used to align a field value.
- `REGISTER__FIELD_MASK` gives the field's already-shifted bit mask.
- One-bit fields use masks such as `0x00000001L`; multi-bit fields use wider masks such as `0x000003FFL`, `0xFFF00000L`, or `0xFFFFFFFFL`.

The chunk's main families are:

- `NBIF_SDP_VWR_VCHG_*`: per-function `F0`-`F7` and `SWDS_P0` disable, reset-override-enable, reset-override-value, and trigger bits. These model sideband virtual-wire voltage-change/reset signaling.
- `BIFC_A2S_*`: SDP disconnect hysteresis, read-response error mapping, response selection, write-chain disable, read/write WRR weights, response reorder controls, write/read tag minimums, VC tag allocations, control-class mappings, and completion-buffer reservations.
- `RCC_PFC_*`: repeated PFC register layouts for AMDGFX, AMDGFXAZ, USB, and PD controller blocks. Each exposes snoop/nonsnoop LTR values and scales, PME restore enable/status, sticky restore status for PCIe errors, restored TLP header dwords, restored TLP prefix, and auxiliary current/power-detected override fields.
- `HARD_RST_CTRL`, `SELF_SOFT_RST`, `SELF_SOFT_RST_2`, and `BIF_RST_MISC_CTRL*`: reset-enable, sticky-reset, privileged-reset, core reset, strap reload, link reset, FLR auto-clear, grace timeout, DMA dummy response, timer scale, and PME turnoff mode fields.
- `DEV0_PF<n>_FLR_RST_CTRL` and `DEV0_PF<n>_D3HOTD0_RST_CTRL`: PF0 has the widest FLR control surface, including VF/soft-PF controls; PF1-PF7 carry PF reset, sticky, privilege, FLR grace, and dummy-response fields. D3hot/D0 reset control repeats across PF0-PF7.
- `BIF_*_INTR_STS`, `BIF_*_INTR_MASK`, `BIF_PF_FLR_RST`, and `BIF_PF0_VF_FLR_*`: status/mask/trigger fields for instance reset, PF FLR, D3hot/D0, power events, PF D-state events, and PF0 VF FLR events for VF0-VF30 plus soft-PF.
- `BIFL_RAS_*`: central RAS controls/status and five leaf control/status pairs for poison, parity, receive-error event detection, error-event generation/propagation, egress-stall generation/propagation, and RAS interrupt enable/status.
- `BIF_CFG_DEV0_EPF0_*`: PCI config-space field masks for the endpoint's base identification, command/status, BARs, PM capability, PCIe capability, device/link control and status, MSI/MSI-X, vendor-specific and VC capabilities, AER status/mask/severity/logging, enhanced BAR sizing, and power-budget metadata.

## Control Flow

This header has no runtime control flow. It is compile-time data consumed by driver code that performs read-modify-write sequences against hardware registers.

Observed integration code includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes this header with `nbio_2_3_offset.h` and programs NBIO doorbell apertures, interrupt control, memory-controller access, HDP flush remapping, clock gating, ASPM, and LTR.
- In `nbio_v2_3_program_ltr()`, the driver sets `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` after programming TX LTR control and clearing the LTR disable strap.
- In `nbio_v2_3_program_aspm()`, the driver clears `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` while staging ASPM programming, writes a raw PCIe LTR capability value, and later re-enables LTR when the PCI path supports it.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes the same header and uses NBIO mailbox register fields indirectly through generated aliases to exchange VF/PF messages, poll acknowledgements, service FLR notifications, and schedule RAS/reset work.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include the header for NBIO register definitions used by SMU power-management paths, though the inspected direct references are concentrated in NBIO and MxGPU code.

## State and Persistence

The macros themselves do not store state. They describe bit positions for state stored in hardware registers:

- Reset/FLR/D3hot fields control or report hardware reset state. Some bits explicitly preserve sticky state across reset classes, and misprogramming them can change what survives FLR, D3hot/D0, link reset, or hard reset.
- Interrupt status and mask registers hold live hardware event state for reset, power, D-state, and PF/VF FLR events. Status handling is typically clear-on-write or hardware-defined, so masks must match the hardware manual exactly.
- AER and RCC PFC sticky-restore fields persist PCIe error state, TLP headers, and TLP prefixes so software or firmware can reconstruct faults after reset or power transitions.
- PCI config fields such as command, status, BARs, PM, PCIe device/link controls, MSI/MSI-X, VC, AER, power-budget, and DPA capabilities represent device-visible PCI state. Some fields are writable by the OS or firmware; others are capability/status surfaces populated by hardware.
- BIFC A2S credit/tag/VC/response controls affect in-flight fabric behavior and arbitration rather than kernel memory. Their effects persist until reset or later reprogramming.
- RAS leaf and central controls/status expose error-detection, poison/parity handling, stall generation, propagation, and interrupt-routing state for the BIF link.

Because this is a register contract, the persistence boundary is the GPU hardware function, not process memory. A wrong mask or shift can make a correct-looking `REG_SET_FIELD()` write alter a different bit until the relevant register is restored or the GPU/function is reset.

## Dependencies

This chunk depends on the AMDGPU SOC15 register model:

- `nbio_2_3_offset.h` provides the `mm*`, `reg*`, and base-index constants for the same register names.
- `nbio_2_3_default.h` provides generated default values for the same IP generation.
- `soc15.h` and AMDGPU register helpers combine offsets, base indices, and masks/shifts into actual MMIO or PCIe config-space reads/writes.
- The register names must stay synchronized with the ASIC register database for NBIO 2.3 and with firmware expectations for reset, RAS, PCIe, and SR-IOV behavior.
- Consumers are mostly in the AMDGPU kernel driver: `nbio_v2_3.c`, `mxgpu_nv.c`, and SMU 11 PPT files for Navi/Sienna-era ASICs.

No external library ABI is defined here. The ABI-like contract is between generated headers, kernel driver code, firmware, and the NBIO hardware layout.

## Integration Points

The key integration surface is the AMDGPU NBIO layer:

- NBIO callback implementations in `nbio_v2_3.c` use this family of masks to set fields while preserving neighboring bits in the same register. This is especially visible in ASPM/LTR programming, doorbell aperture setup, interrupt control, and power/clock-gating flows.
- PCIe capability masks in `BIF_CFG_DEV0_EPF0_*` line up with Linux PCI concepts: command/status, PM capability, device/link capability/control/status, MSI/MSI-X, AER, VC, enhanced BAR, power budget, and DPA. The driver can use either SOC15-style offsets or SMN/PCIE direct addresses for these registers.
- Reset and FLR field definitions align with virtualization flows. `mxgpu_nv.c` handles host FLR notifications, queues reset work, and exchanges VF/PF mailbox messages; the reset/status/mask definitions in this chunk describe the hardware bits behind those events even when direct references are hidden behind generated mailbox aliases or adjacent offset headers.
- RAS field definitions connect NBIO/BIF link errors to AMDGPU RAS handling. MxGPU mailbox code can request bad pages, receive unrecoverable-error notifications, and schedule reset-domain work when the host reports RAS-related events.
- PFC LTR/PME/sticky-restore fields connect PCIe power-management and error-reporting behavior to endpoint-specific blocks for graphics, USB, and PD controller functions.

## Risks

- Generated-header drift is the main risk. A single incorrect shift or mask can make `REG_SET_FIELD()` preserve the wrong bits or write the wrong field, causing PCIe link, reset, RAS, AER, interrupt, or power-management failures.
- Boundary incompleteness matters for this chunk. `NBIF_SDP_VWR_VCHG_DIS_CTRL` and `BIF_CFG_DEV0_EPF0_PCIE_DPA_ENH_CAP_LIST` are partial in this work item; per-file analysis should reconcile adjacent chunks before claiming complete coverage.
- Similar field names in status, mask, and severity registers can be confused. For example, AER has uncorrectable status, mask, severity, correctable status, and correctable mask registers with nearly parallel field names but different semantics.
- PF/VF reset fields are security and availability sensitive under SR-IOV. Incorrect FLR, D3hot/D0, or VF reset masks can leave transactions pending, fail to isolate virtual functions, or trigger broader reset effects than intended.
- PCIe config and BAR enhanced capability fields are OS-visible. Wrong masks for BAR size, MSI/MSI-X, AER, or link-control fields can break enumeration, interrupt delivery, error recovery, or link training.
- RAS leaf controls can amplify or hide hardware faults. Misprogrammed poison/parity/stall/error-event propagation fields can suppress expected interrupts or generate persistent stalls.
- Many macros are not directly referenced in the current source tree. Removing or "simplifying" apparently unused generated definitions would be risky because they serve future ASIC enablement, debug tooling, firmware-aligned register access, and indirect macro expansion.

## Test Signals

Useful validation signals are mainly build-time and hardware/runtime signals:

- Compile AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c`; undefined or renamed field macros should fail at build time where directly referenced.
- Run generated-header consistency checks against `nbio_2_3_offset.h` and the ASIC register database: every field should have the expected shift/mask pair, and every mask should match the documented width at its shift.
- Exercise ASPM/LTR paths on hardware with and without `pdev->ltr_path`; verify link power-management behavior and absence of PCIe AER regressions.
- Test PF and SR-IOV VF reset flows: FLR notifications, reset-domain work scheduling, `IDH_FLR_NOTIFICATION_CMPL` polling, and GPU init/fini/reset mailbox handshakes should complete without timeouts.
- Validate MSI/MSI-X interrupt delivery and masking for the endpoint after programming MSI/MSI-X capability registers.
- Trigger or inject PCIe AER/RAS events where supported and verify status, mask, severity, sticky restore, TLP header/prefix logging, RAS interrupt, and bad-page/unrecoverable-error handling paths report expected state.
- Exercise doorbell, HDP flush, and command submission smoke tests after reset and power transitions to catch NBIO register programming errors that may not appear at compile time.

### subset-b-002913: lines 21953-24399

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 21953-24399

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, storage definitions, or executable control flow in the chunk. The constants describe bit positions and masks for PCIe configuration-space fields under `BIF_CFG_DEV0_EPF0_*` and the beginning of `BIF_CFG_DEV0_EPF1_*`.

The surrounding in-tree consumer for this ASIC generation is `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio/nbio_2_3_sh_mask.h` together with the matching offset/default headers and uses these masks through helpers such as `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15`.

## Purpose

The chunk gives the AMDGPU driver symbolic access to fields in Navi-era NBIO/BIF PCIe registers. It lets driver code compose, extract, enable, disable, or test hardware-defined bitfields without hard-coding raw shifts and masks at each call site.

Major hardware areas covered:

- EPF0 PCIe Dynamic Power Allocation (DPA) capability, status, control, latency, and substate power allocation fields.
- EPF0 PCIe secondary extended capabilities, link equalization, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s PHY, lane margining, VF resizable BAR, and AMD vendor-specific GPUIOV fields.
- EPF0 GPUIOV interrupt, reset, hypervisor/VM mailbox, context, framebuffer partitioning, P2P-over-XGMI enablement, and per-engine scheduler descriptor fields for UVD, VCE, GFX, and UVD1.
- Start of EPF1 PCI configuration-space fields: IDs, command/status, class/revision, BARs, adapter IDs, ROM, interrupt pins, PM capability, PCIe capability, MSI/MSI-X, vendor-specific capability, virtual-channel capability, device serial number, AER, resizable BAR, and power-budget capability list.

## Important APIs, Types, And Constants

This chunk exports macros in the standard generated AMD register naming form:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Register comments such as `//BIF_CFG_DEV0_EPF0_PCIE_SRIOV_CONTROL` group the following shift/mask pairs by hardware register.

Important field families:

- DPA fields: `BIF_CFG_DEV0_EPF0_PCIE_DPA_CAP__SUBSTATE_MAX_MASK`, `TRANS_LAT_UNIT_MASK`, `PWR_ALLOC_SCALE_MASK`, `BIF_CFG_DEV0_EPF0_PCIE_DPA_STATUS__SUBSTATE_STATUS_MASK`, and `BIF_CFG_DEV0_EPF0_PCIE_DPA_CNTL__SUBSTATE_CNTL_MASK`.
- Link equalization fields: per-lane `BIF_CFG_DEV0_EPF0_PCIE_LANE_<0..15>_EQUALIZATION_CNTL__DOWNSTREAM_PORT_TX_PRESET_MASK`, RX preset hint masks, upstream TX preset masks, and upstream RX preset hint masks.
- ACS/ATS/PRI/PASID fields: `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_ATS_CAP`, `PCIE_ATS_CNTL`, `PCIE_PAGE_REQ_CNTL`, `PCIE_PAGE_REQ_STATUS`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL`.
- SR-IOV fields: `BIF_CFG_DEV0_EPF0_PCIE_SRIOV_CONTROL__SRIOV_VF_ENABLE_MASK`, `SRIOV_VF_MSE_MASK`, `SRIOV_ARI_CAP_HIERARCHY_MASK`, VF count/stride/offset/device ID masks, supported/system page-size masks, and VF BAR base address masks.
- Gen4/16 GT/s fields: `BIF_CFG_DEV0_EPF0_LINK_STATUS_16GT__EQUALIZATION_COMPLETE_16GT_MASK`, phase success masks, per-lane 16 GT/s DSP/USP TX preset masks, and parity mismatch status masks.
- Margining fields: `BIF_CFG_DEV0_EPF0_MARGINING_PORT_STATUS__MARGINING_READY_MASK` and per-lane `MARGINING_LANE_CNTL`/`MARGINING_LANE_STATUS` receiver, margin type, usage model, and payload masks.
- VF resize BAR fields: `BIF_CFG_DEV0_EPF0_PCIE_VF_RESIZE_BAR[1-6]_{CAP,CNTL}` masks for supported BAR sizes, selected BAR index, total number, and configured size.
- GPUIOV fields: `BIF_CFG_DEV0_EPF0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_INTR_ENABLE`, `INTR_STATUS`, `RESET_CONTROL`, `HVVM_MBOX_DW0`, `HVVM_MBOX_DW1`, `HVVM_MBOX_DW2`, `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `REGION`, `P2P_OVER_XGMI_ENABLE`, `VF<0..30>_FB`, and scheduler descriptors for UVD/VCE/GFX/UVD1.
- EPF1 PCIe capability fields: `BIF_CFG_DEV0_EPF1_COMMAND`, `STATUS`, `PMI_*`, `DEVICE_CAP`, `DEVICE_CNTL`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, VC, DSN, AER, and BAR enhancement masks.

There are no C types declared in this chunk. Type safety and register width assumptions come from the AMDGPU register helper layer and the C integer constants themselves.

## Control Flow

The header has no runtime control flow. Runtime effects occur only when included driver code passes the constants to register helper macros.

Typical usage pattern in this ASIC generation:

1. Driver code reads a 32-bit register through `RREG32_PCIE`, `RREG32_SOC15`, or `RREG32`.
2. `REG_SET_FIELD` or explicit mask/shift operations update a field using the `__SHIFT` and `_MASK` macros from this header.
3. Driver code writes the modified value back through `WREG32_PCIE`, `WREG32_SOC15`, or `WREG32`.

For example, `nbio_v2_3.c` uses the same header family to program NBIO link/power behavior: it updates `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` when enabling/disabling LTR, programs link-control masks for ASPM, and selects the `mmPCIE_INDEX2`/`mmPCIE_DATA2` indirect PCIe access registers. This chunk extends that same mechanism to later PCIe capability and virtualization registers.

## State And Persistence

The macros are compile-time constants and do not persist state. The state they describe is hardware state in PCIe configuration registers and vendor-specific NBIO/BIF registers.

Persistence characteristics depend on the underlying field:

- Capability fields such as IDs, class codes, supported link speeds, supported page sizes, BAR size support, and DPA capability values are generally hardware/strap/firmware-defined and exposed as read-only or read-mostly PCIe config state.
- Control fields such as DPA substate control, ACS/ATS/PASID enable bits, SR-IOV VF enable/MSE bits, TPH enablement, margining lane controls, VF resize BAR controls, GPUIOV interrupt enables, GPUIOV reset control, and EPF1 device/link/MSI/MSI-X control fields can be software-visible mutable hardware state.
- Status and log fields such as lane error status, 8 GT/s and 16 GT/s equalization status, margining status, GPUIOV interrupt status, AER status, header logs, and TLP prefix logs are transient diagnostic state supplied by hardware.
- GPUIOV framebuffer partition and scheduler fields encode virtualization resource allocation state. Their persistence is tied to PF/hypervisor programming, SR-IOV lifecycle, GPU reset, and firmware/hardware ownership rules.
- Reset, FLR, secondary bus reset, D3/D0 transitions, and GPU reset paths can clear or reinitialize many of these registers. The header itself does not enforce restore ordering.

## Dependencies

Direct dependencies:

- Matching NBIO 2.3 offset/default headers, especially `nbio_2_3_offset.h`, provide register addresses such as `mm...` or `smn...` symbols. This chunk only provides field layout.
- AMDGPU register helpers in the driver provide the access semantics: `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_*`, `WREG32_*`, and `SOC15_REG_OFFSET`.
- Linux PCI/PCIe semantics define many fields mirrored here: PM, PCIe capabilities, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, SR-IOV, TPH, LTR, ARI, VC, DSN, DPA, lane margining, and link equalization.
- AMD virtualization firmware/hypervisor interfaces consume or populate the GPUIOV-specific register blocks.

Implicit dependencies and assumptions:

- The constants must match the NBIO 2.3 hardware register specification exactly.
- The register width is effectively 32 bits for the generated masks in this chunk, even when a hardware register represents a 16-bit PCI config field.
- Callers must pair these masks with the correct register address and access path. A valid mask applied to a different register can silently corrupt unrelated hardware state.

## Integration Points

This chunk integrates with the AMDGPU NBIO and PCIe support in several ways:

- `nbio_v2_3.c` includes this header and uses the same generated constants for NBIO initialization, ASPM/LTR setup, light sleep, clock gating, doorbell aperture setup, HDP flush offset reporting, PCIe index/data offset reporting, and revision-id extraction.
- AMDGPU PCIe register access code can use NBIO-provided index/data offsets to expose or inspect PCIe register state through debug/sysfs paths.
- Linux PCI core and platform firmware interact with overlapping PCI config-space fields, especially command/status, PM, link control/status, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, SR-IOV, and BAR sizing fields. AMDGPU code must avoid racing or overriding policy owned by the PCI core unless an ASIC workaround requires it.
- SR-IOV and GPUIOV integration touches PF/VF lifecycle, mailbox handshakes, interrupt routing, per-VF framebuffer partitions, engine scheduling descriptors, and FLR/reset signaling.
- Power management integration uses DPA, LTR, link-status, link-control, data-link-feature, and ASPM-related fields to coordinate GPU power savings with PCIe link behavior.
- Diagnostics and service paths can use lane error, equalization, margining, AER, header log, and TLP prefix fields to identify PCIe reliability problems.

## Risks

- **Generated-header drift:** If a mask or shift is wrong for NBIO 2.3 silicon, every caller using `REG_SET_FIELD` or `REG_GET_FIELD` will read or write the wrong bits while still compiling cleanly.
- **Register/address mismatch:** This header does not contain register addresses. Using an EPF0 field mask with an EPF1 register, or using an EPF1 mask with EPF0 offsets, can modify unrelated PCI config state.
- **PCI core ownership conflicts:** Fields such as MSI/MSI-X, SR-IOV, AER, ACS, ATS, PASID, BAR sizing, and PM/link control also have Linux PCI subsystem ownership. Direct AMDGPU writes must be constrained to hardware-required paths.
- **Virtualization safety:** GPUIOV fields expose PF/VF resource partitioning, mailbox state, per-VF framebuffer windows, interrupt enables/status, and FLR-like reset controls. Incorrect programming can break VF isolation, lose mailbox messages, or reset active guests.
- **Status clear semantics:** AER, interrupt status, lane error, margining, and log fields may be write-1-to-clear or otherwise side-effectful in hardware. Generic read/modify/write code must understand per-register semantics beyond the masks.
- **Link training sensitivity:** Equalization, margining, target speed, de-emphasis, compliance, and autonomous speed/width controls can destabilize the PCIe link if changed outside the expected link state.
- **Power-management regressions:** DPA, LTR, TPH, ASPM, and link low-power fields can interact with device latency, DMA completion latency, and platform link policy.

## Test Signals

Useful validation signals for changes that touch this chunk or code that uses it:

- Build coverage: the AMDGPU driver should compile with this header included, with no undefined macro or duplicate macro diagnostics.
- Register helper coverage: sites using `REG_SET_FIELD`/`REG_GET_FIELD` with these names should compile and produce expected bit values in simple unit-style checks or debug assertions where available.
- PCIe enumeration: `lspci -vv` should continue to report sane capabilities for the GPU, including link capability/status, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, SR-IOV, and resizable BAR capability where supported.
- Runtime link behavior: link speed/width, ASPM/LTR state, and retraining/equalization status should remain stable across boot, suspend/resume, runtime power transitions, and GPU reset.
- SR-IOV/GPUIOV: PF enablement, VF creation/removal, VF driver load/unload, mailbox handshakes, FLR, per-VF framebuffer partitioning, and VF interrupt delivery should work without stale status bits or resource leaks.
- Error handling: AER injection or observed PCIe errors should map to the expected uncorrectable/correctable status, mask, severity, header log, and TLP prefix fields.
- Diagnostics: lane margining/equalization status and lane error counters should read coherently on hardware that exposes these capabilities.

## Chunk Notes

- The line range begins in the middle of `BIF_CFG_DEV0_EPF0_PCIE_DPA_ENH_CAP_LIST`; earlier lines likely contain the corresponding `CAP_ID__SHIFT`, `CAP_VER__SHIFT`, `NEXT_PTR__SHIFT`, and `CAP_ID_MASK`.
- The line range ends at `BIF_CFG_DEV0_EPF1_PCIE_PWR_BUDGET_ENH_CAP_LIST__CAP_VER_MASK`, so the EPF1 power-budget capability block continues in the next chunk.
- Because this is generated register metadata, the most important maintenance check is cross-file consistency: names in this header, register addresses in `nbio_2_3_offset.h`, and reset/default values in `nbio_2_3_default.h` must describe the same hardware revision.

### subset-b-002914: lines 24400-26849

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 24400-26849

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 2.3 register mask header. The range starts in the `BIF_CFG_DEV0_EPF1` PCIe power-budget extended capability block and continues through the beginning of the `BIF_CFG_DEV0_EPF2` Dynamic Power Allocation capability. It contains preprocessor constants only: no C functions, structs, runtime storage, or executable control flow are defined here.

The covered register families are:

- `BIF_CFG_DEV0_EPF1` PCIe power budget, Dynamic Power Allocation, secondary PCIe, lane equalization, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data link feature, 16 GT/s PHY, lane margining, VF resizable BAR, and AMD GPUIOV vendor-specific capability fields.
- `BIF_CFG_DEV0_EPF2` PCI config header fields, conventional capability list entries, PMI, PCIe capability, MSI/MSI-X, SATA, vendor-specific scratch, Advanced Error Reporting, resizable BAR, power budget, and the opening DPA capability fields.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and NBIO 2.3 PCIe configuration-space registers. Each field is expressed as the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate the field in a 16-bit or 32-bit register image.

The actual register addresses live in the sibling generated offset headers such as `nbio_2_3_offset.h`; this file supplies the field layout. Driver code consumes these definitions through AMD register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG8`, and `WREG8`. Observed include sites for this mask header include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU power-management files under `pm/swsmu/smu11`.

## Important Macro Families

### EPF1 PCIe Power and Link Capabilities

The first part of the chunk completes EPF1 PCIe power-related extended capabilities. `BIF_CFG_DEV0_EPF1_PCIE_PWR_BUDGET_*` defines power-budget data selection, base power, data scale, PM state/substate, type, rail, and system-allocated status. `BIF_CFG_DEV0_EPF1_PCIE_DPA_*` defines Dynamic Power Allocation capability metadata, maximum substates, transition latency units/values, power-allocation scale, current substate status, substate control enablement, and eight substate power allocation bytes.

The secondary PCIe and link-training section defines `PCIE_LINK_CNTL3`, lane error status, and per-lane `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`. Each lane equality-control register repeats downstream/upstream TX preset and RX preset-hint fields, with reserved high bits. These constants support PCIe Gen3-style equalization management and diagnostics.

### EPF1 Isolation, Translation, and Addressing Extensions

The chunk defines several PCIe extended capabilities that are central to IOMMU, virtualization, and peer-to-peer behavior:

- ACS capability/control fields for source validation, translation blocking, request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-vector size.
- ATS capability/control fields for invalidate queue depth, page-aligned request, global invalidate support, smallest translation unit, and ATC enable.
- PRI/page request fields for enable/reset, response failure, unexpected group index, stopped state, PASID-required responses, outstanding capacity, and outstanding allocation.
- PASID capability/control fields for execute permission, privileged mode, maximum PASID width, and enable bits.
- Multicast capability/control, address, receive, block-all, and block-untranslated fields.
- LTR latency value/scale fields for snooped and non-snooped latency tolerance.
- ARI capability/control fields for function-group support, next-function number, ARI group enablement, and function-group selection.

These are hardware-visible policy and capability fields rather than ordinary software state. Incorrect bit positions in these macros would affect PCIe isolation, translation, and function routing.

### EPF1 SR-IOV, VF BAR, and High-Speed Link Features

The EPF1 SR-IOV section maps capability, control, status, VF count, VF offset/stride, VF device ID, supported/system page sizes, six VF BAR base addresses, and migration-state-array offset. The VF resizable BAR section later repeats BAR1 through BAR6 capability/control patterns with supported size, BAR index, BAR total number, and BAR size fields.

The chunk also contains:

- TPH requester capability/control fields, including ST-table location/size and requester enable.
- Data Link Feature capability/status fields for DL feature exchange, remote valid, remote scale, and local/remote DLF support.
- PCIe 16 GT/s PHY extended capability fields for supported 16 GT/s data rate, 16 GT/s enablement, equalization complete/in-progress/failure state, per-lane equalization control, and parity mismatch status.
- PCIe lane margining capability/status and per-lane control/status registers for lanes 0-15. Each lane has receiver number, margin type, usage model, and payload fields, with matching status fields.

These fields are integration points for link training, diagnostics, PCIe speed negotiation, and VF memory exposure.

### EPF1 AMD GPUIOV Vendor-Specific Capability

The most AMD-specific part of the chunk is `BIF_CFG_DEV0_EPF1_PCIE_VENDOR_SPECIFIC_*_GPUIOV`. It describes an AMD vendor-specific extended capability for GPU I/O virtualization:

- Capability and VSEC headers expose capability ID/version/next pointer and VSEC ID/revision/length.
- `SRIOV_SHADOW` mirrors VF enable and VF number state.
- `INTR_ENABLE` and `INTR_STATUS` define per-engine interrupt bits for GFX, UVD, UVD1, and VCE command completion, self-recovered hangs, hangs requiring FLR, VM busy transitions, plus HVVM mailbox transmit-ack and receive-valid interrupts.
- `RESET_CONTROL` exposes a `SOFT_PF_FLR` bit.
- `HVVM_MBOX_DW0` selects a VF index and carries transmit/receive message data plus valid/ack bits.
- `HVVM_MBOX_DW1` maps transmit-ack and receive-valid bits for VF0 through VF15; `HVVM_MBOX_DW2` maps the same state for VF16 through VF30 plus PF transmit-ack and receive-valid bits.
- `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `REGION`, and `P2P_OVER_XGMI_ENABLE` describe context size/location/offset, total frame-buffer availability/consumption, scheduler block offsets, local frame-buffer region limits, and per-VF/PF P2P-over-XGMI enablement.
- `VF0_FB` through `VF30_FB` repeat a 16-bit VF frame-buffer size plus 16-bit offset layout for per-VF memory partitioning.
- Scheduler dword windows for `UVDSCH`, `VCESCH`, `GFXSCH`, and `UVD1SCH` each expose raw `DW0` through `DW8` fields.

This section lines up with the MxGPU virtualization layer. The local source tree's `amdgpu/mxgpu_nv.c` includes this header and implements mailbox send/ack/valid flows using NBIO mailbox-related registers. The exact GPUIOV fields in this chunk are PF/VF coordination surfaces and should be treated as privileged virtualization state.

### EPF2 PCI Config Header and Standard Capabilities

At `// addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, the chunk switches to endpoint function 2. It defines the standard PCI config header fields:

- Vendor/device ID, command, status, revision ID, class-code bytes, cache-line size, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem IDs, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- Command bits for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, fast back-to-back, and interrupt disable.
- Status bits for immediate readiness, interrupt status, capability list, parity and abort status, DEVSEL timing, system error, and detected parity error.

It then defines vendor, power-management, and PCIe capability list entries. The PMI fields cover supported power states, PME, data select/scale, bus power enable, and PMI data. The PCIe capability fields include device/port type, slot, interrupt message number, device capabilities, device control/status, link capabilities/control/status, device capabilities/control/status 2, and link capabilities/control/status 2.

### EPF2 MSI, MSI-X, SATA, AER, BAR, Power Budget, and DPA

The EPF2 interrupt capability section defines MSI and MSI-X capability list metadata, MSI enable/multiple-message/64-bit/per-vector masking fields, MSI address/data/mask/pending fields, MSI-X table size/function mask/enable, and MSI-X table/PBA BAR indicator plus offset.

The SATA capability block defines SATA capability version, BAR location/offset, indirect data port index, and data masks. The EPF2 vendor-specific block exposes a VSEC header plus two 32-bit scratch registers.

The Advanced Error Reporting block defines:

- Extended capability header metadata.
- Uncorrectable error status, mask, and severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, multicast blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.
- Correctable error status/mask bits for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header log overflow.
- AER capability/control fields for first error pointer, ECRC generation/check capabilities/enables, multi-header receive capability/enable, TLP prefix log presence, and completion timeout log capability.
- Header log and TLP prefix log dwords.

The chunk closes with EPF2 resizable BAR1-BAR6 capability/control fields, power budget fields matching EPF1, and the start of EPF2 DPA capability metadata and `DPA_CAP` field definitions.

## Control Flow and State Behavior

This header chunk has no runtime control flow. Its effect is compile-time: it determines how C code composes writes and decodes reads for NBIO PCIe configuration registers.

The persistent state described by the macros is hardware state. Important state includes PCI command/status bits, link speed/width/equalization state, power-management and DPA settings, ACS/ATS/PRI/PASID enablement, SR-IOV VF counts and VF BAR exposure, per-VF framebuffer partitioning, GPUIOV mailbox and interrupt state, MSI/MSI-X address/data/mask state, AER error status/masks/severity, and resizable BAR sizes.

Several fields are status or event latches, not durable configuration. Examples include PCI status errors, EPF1 DPA status, lane error/equalization/margining status, GPUIOV interrupt status, HVVM mailbox ack/valid fields, MSI pending bits, AER status/header logs, and link status. Other fields are command-like or enable bits, such as PCI bus mastering, ATS/PRI/PASID enables, SR-IOV VF enablement, soft PF FLR, link retrain, MSI/MSI-X enable, and AER ECRC enablement. Consumers must follow the owning hardware and driver sequencing; this generated header does not encode ordering, locking, posted-write flushes, or timeout policy.

## Dependencies and Integration Points

The chunk depends on the AMD generated register-header convention:

- `nbio_2_3_offset.h` supplies register offsets and base indices for these field names.
- `nbio_2_3_default.h` supplies generated reset/default values where present.
- AMDGPU helper macros consume these `__SHIFT` and `_MASK` definitions to avoid hard-coded bit positions.

Observed include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes the NBIO 2.3 offset/default/mask headers and configures NBIO memory access, doorbells, interrupt handling, link behavior, and other NBIO state.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes this mask header and implements SR-IOV/MxGPU mailbox request, ack, polling, and reset-access flows.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include this header for NBIO/PCIe-related power-management integration.

The macros are tightly coupled to PCIe core behavior, Linux PCI enumeration and capability handling, AMDGPU PF/VF virtualization, the interrupt subsystem, SMU power policy, and AER diagnostics. Cross-generation headers such as `nbio_7_2_0_sh_mask.h` and `nbif_6_3_1_sh_mask.h` contain similar names but are not guaranteed to have identical layouts or supported fields.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can silently program the wrong PCIe capability bit, changing bus mastering, memory access, interrupts, link training, isolation, or error reporting.
- Virtualization fields are security-sensitive. ACS, ATS, PRI, PASID, SR-IOV, GPUIOV mailbox, per-VF frame-buffer partition, and P2P-over-XGMI fields affect VF isolation and PF/VF coordination.
- Status and write-clear semantics are not visible in the macros. Code using AER, PCI status, interrupt status, mailbox ack/valid, or lane diagnostics must know whether hardware expects write-one-to-clear, polling, or explicit acknowledgement.
- Link-training and margining fields can destabilize PCIe connectivity if programmed outside the intended sequence.
- Cross-generation copy/paste is risky. Similar macro names across NBIO/NBIF generations may hide layout differences, additional reserved bits, or different endpoint/function coverage.
- Raw 32-bit scheduler dword and scratch fields provide little semantic validation in the header. Higher-level code must validate ownership, engine type, VF number, and firmware expectations before writing them.

## Test Signals

Useful validation signals for code that depends on this chunk include:

- Build coverage for all include sites, especially `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 power-management files, to catch renamed or malformed macros.
- PCI enumeration on NBIO 2.3 hardware showing correct vendor/device/class, capability pointer chains, MSI/MSI-X capability state, PCIe link capability/status, and AER capability presence.
- SR-IOV/MxGPU tests that create VFs, verify VF count/stride/BAR sizing, exercise mailbox send/ack/receive-valid paths, and confirm VF framebuffer partitions match expected size/offset values.
- Link diagnostics that confirm negotiated link width/speed, lane equalization, 16 GT/s status, lane margining status, and absence of unexpected lane error bits.
- AER injection or fault-observation tests that validate uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs.
- Power-management tests that cover PMI, power-budget, DPA substate, LTR, and SMU integration without regressions in suspend/resume, runtime power transitions, or link power management.

### subset-b-002915: lines 26850-29340

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 26850-29340

## Purpose

This chunk is part of the generated AMD NBIO 2.3 shift/mask register header. It does not define executable control flow; it defines C preprocessor constants that describe bit positions and bit masks for PCI/PCIe configuration-space registers exposed by the Navi-era NBIO/NBIF block. The paired `nbio_2_3_offset.h` file supplies register addresses, while this file supplies the field layout used by `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask operations, and `WREG32_FIELD15`/`RREG32_SOC15` style AMDGPU register accessors.

The selected lines cover the end of endpoint function 2 (`EPF2`) PCIe extended-capability fields, all of endpoint function 3 (`EPF3`) configuration and PCIe capability fields, and the beginning of virtual function 0 (`EPF0_VF0`) configuration and PCIe capability fields. The last few lines enter the `EPF0_VF1` block but only include its vendor/device ID fields before the chunk boundary.

## Register Families Covered

- `BIF_CFG_DEV0_EPF2_PCIE_DPA_*`: Dynamic Power Allocation latency, status, control, and eight substate power allocation masks. These fields expose DPA substate selection and power allocation values for the previous EPF2 extended-capability block.
- `BIF_CFG_DEV0_EPF2_PCIE_ACS_*`: Access Control Services capability/control masks for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer egress control, direct translated peer-to-peer, and egress vector size.
- `BIF_CFG_DEV0_EPF2_PCIE_PASID_*`: PASID enhanced-capability, capability, and control fields. These describe PASID enablement, execute-permission support, privileged-mode support, and maximum PASID width.
- `BIF_CFG_DEV0_EPF2_PCIE_ARI_*`: Alternative Routing-ID Interpretation capability/control fields for function-group handling and next-function numbering.
- `BIF_CFG_DEV0_EPF2_PCIE_TPH_REQR_*` and `BIF_CFG_DEV0_EPF2_PCIE_TPH_ST_TABLE_0..63`: TPH requester capability/control fields and steering-tag table entries. Each table register has lower and upper 8-bit ST entries.
- `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`: A complete PCI configuration-space-like view for endpoint function 3, from vendor/device IDs through base address registers, PCI PM capability, PCIe capability, MSI/MSI-X, SATA, vendor-specific extended capabilities, AER, BAR sizing, power budget, DPA, ACS, PASID, ARI, TPH, and TPH steering table entries.
- `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`: The beginning and most of the PCIe extended capability view for virtual function 0. It includes standard config header fields, PCIe device/link capabilities, MSI/MSI-X, vendor-specific capability, AER status/mask/severity/logging, ATS capability/control, and ARI capability/control.
- `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp`: The chunk only reaches `VF1_VENDOR_ID` and `VF1_DEVICE_ID`; VF1 command/status and later fields continue in the following chunk.

## Important APIs, Types, and Constants

This header contributes constants, not callable APIs or C types. The important contract is naming and layout:

- Field shift constants follow `<REGISTER>__<FIELD>__SHIFT`.
- Field mask constants follow `<REGISTER>__<FIELD>_MASK`.
- Register scopes encode hardware function identity: `EPF2`, `EPF3`, `EPF0_VF0`, and `EPF0_VF1`.
- Extended-capability list registers consistently expose `CAP_ID`, `CAP_VER`, and `NEXT_PTR` fields at bit ranges 0-15, 16-19, and 20-31.
- Repeated PCI capability groups retain PCIe-defined field naming, making them compatible with generic helper macros and with code that mirrors PCI/PCIe spec terminology.

Consumers include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h` for NBIO initialization, doorbell aperture setup, interrupt handling, clock gating, ASPM/LTR programming, and link-width handling.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes this header for SR-IOV/MxGPU mailbox and virtualized Navi GPU support.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include the same offset/mask pair for SMU power-management code that reads PCIe/NBIO strap and link-related state.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow appears in call sites that:

1. Select a register address from `nbio_2_3_offset.h` or an SMN/mmio literal.
2. Read the register via accessors such as `RREG32_SOC15`, `RREG32_PCIE`, or `RREG32`.
3. Extract or update fields using this header's `__SHIFT` and `_MASK` constants, commonly through `REG_SET_FIELD`, direct `& mask`, and `>> shift`.
4. Write changed values back through `WREG32_SOC15`, `WREG32_PCIE`, `WREG32`, or field-specific helpers.

For this exact range, most names represent PCI configuration capability state rather than the core NBIO doorbell and clock-gating registers used heavily in `nbio_v2_3.c`. The pattern is still the same: the constants are compile-time field descriptions for hardware register transactions performed elsewhere.

## State and Persistence Behavior

The file itself has no state and persists nothing. The constants describe hardware-backed state in PCIe configuration and NBIO register space:

- Capability and identity registers, such as vendor/device/class/header/capability-list fields, generally reflect strap, firmware, or hardware configuration.
- Control registers, such as `COMMAND`, `DEVICE_CNTL`, `LINK_CNTL`, `MSI_MSG_CNTL`, `MSIX_MSG_CNTL`, ACS/PASID/ARI/TPH controls, ATS control, and DPA control, may be programmed by firmware, host PCI configuration logic, the kernel PCI core, or AMDGPU.
- Error-status and logging registers, especially AER uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs, reflect live PCIe error state and may be sticky until cleared according to hardware semantics.
- VF register blocks expose virtual function configuration-space state. In SR-IOV environments, reads or writes may be mediated by the PF/hypervisor; `nbio_v2_3_get_rev_id()` in nearby code explicitly treats some guest reads as unreliable and substitutes defaults.

Persistence is therefore hardware/firmware-defined across reset domains. Driver writes are not persistent across full device reset unless replayed during initialization or restored by PCI/firmware paths.

## Dependencies and Integration Points

- Depends on AMDGPU register-access infrastructure (`RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`) to make these constants useful.
- Depends on `nbio_2_3_offset.h` for the address half of the register contract. Shift/mask constants without matching offsets are not enough to access hardware.
- Integrates with Linux PCI/PCIe concepts: PCI command/status, BARs, MSI/MSI-X, PM capability, PCIe device/link capability and control, AER, ACS, PASID, ARI, ATS, TPH, DPA, and power-budgeting.
- Integrates with SR-IOV through the `EPF0_VF*` register blocks and with MxGPU/Navi virtualization code in `mxgpu_nv.c`.
- Integrates with SMU power-management code through shared NBIO/PCIe strap and link state, even though the specific EPF3/VF0 extended capability fields in this chunk are not directly referenced by a narrow textual search outside generated headers.

## Risks and Maintenance Notes

- The header is generated and very large. Manual edits are high risk because a one-bit shift or mask typo silently changes hardware programming semantics.
- Naming collisions are avoided by long register prefixes. Any rename must be coordinated with generated offset headers and all macro consumers.
- Several repeated capability blocks are structurally similar across EPF2, EPF3, and VF blocks. Copy/paste or generator errors can be hard to spot because the values look plausible.
- AER masks and severity fields directly affect error visibility and classification. Incorrect values could hide PCIe faults, over-report nonfatal faults, or mis-handle fatal conditions.
- ACS/PASID/ATS/ARI fields affect isolation, address translation, and SR-IOV behavior. Bad masks here can create functional regressions in IOMMU, peer-to-peer, or virtualized-device paths.
- TPH steering table fields are repeated 64 times for EPF2 and EPF3. Off-by-one generation mistakes would not necessarily be caught by compilation because each macro remains syntactically valid.
- The chunk boundary splits register families: EPF2 power budget/DPA begins in the prior chunk, and EPF0_VF1 continues in the next chunk. File-level reconciliation should merge adjacent chunk context before drawing final conclusions.

## Test and Validation Signals

- Build coverage: any syntax break or missing macro used by C code should be caught by compiling AMDGPU with Navi/NBIO 2.3 support enabled.
- Include coverage: `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c` should still compile with this header and its paired offset header.
- Runtime smoke signals: successful AMDGPU probe on affected Navi/NBIO 2.3 hardware, correct PCIe link reporting, working MSI/MSI-X interrupt delivery, and no unexpected AER storms in `dmesg`.
- SR-IOV validation: VF bring-up, mailbox communication, guest probe, and VF reset/recovery paths should remain stable because this chunk describes VF0 and starts VF1 config-space fields.
- PCIe capability validation: `lspci -vv` or kernel PCI capability dumps should show coherent ACS, PASID, ARI, ATS, AER, MSI/MSI-X, and link capability/control state when those capabilities are exposed.
- Power-management validation: ASPM/LTR, PCIe DPM, and SMU power-state transitions should not regress on Navi10/Sienna Cichlid paths that include this NBIO header.

### subset-b-002916: lines 29341-31771

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 29341-31771

## Scope

This chunk covers generated NBIO 2.3 shift/mask definitions for SR-IOV virtual-function PCI configuration-space fields. It starts in the `BIF_CFG_DEV0_EPF0_VF1_DEVICE_ID` field definitions, then contains the rest of the VF1 PCI/PCIe capability bitfields, complete VF2 and VF3 PCI configuration bitfields, and the beginning of VF4 through `BIF_CFG_DEV0_EPF0_VF4_LINK_CAP2`.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct MMIO operations. Its public interface is the generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT` for a field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field mask.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield side of the NBIO 2.3 hardware ABI. The companion `nbio_2_3_offset.h` header gives the register/config-space offsets, and `nbio_2_3_default.h` gives reset/default values. AMDGPU code combines these names with register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15`.

This chunk describes how virtual functions VF1, VF2, VF3, and the first part of VF4 expose PCI and PCIe configuration bits: command/status, identity/class/header fields, BARs, PCIe link/device capabilities, MSI/MSI-X, vendor-specific extended capability fields, Advanced Error Reporting, ATS, and ARI. These definitions matter for SR-IOV because PF, VF, firmware, and hypervisor paths need a consistent bit layout when presenting and controlling each virtual function's PCI config space.

## Important Macro Families

### VF1 Configuration and Capability Fields

The range begins after the VF1 `VENDOR_ID` comment and inside `BIF_CFG_DEV0_EPF0_VF1_DEVICE_ID`. It then covers nearly the entire VF1 configuration map:

- PCI command/status fields such as IO and memory access enables, bus mastering, parity/SERR behavior, interrupt disable, readiness, capability-list presence, and abort/parity status bits.
- Class/header fields including revision ID, programming interface, subclass, base class, cache-line size, latency timer, header type, BIST, six BAR-sized base-address masks, CardBus CIS pointer, subsystem/vendor adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability fields: capability-list header, PCIe version/device type, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- MSI and MSI-X fields: message control, 32-bit and 64-bit message address/data registers, mask and pending registers, MSI-X table and pending-bit-array fields.
- Extended capabilities: vendor-specific capability headers/data, AER uncorrectable/correctable status/mask/severity, AER capability/control, header logs, TLP prefix logs, ATS capability/control, and ARI capability/control.

The VF1 PCIe control fields include feature toggles for error reporting, relaxed ordering, payload/read-request size, extended tags, no-snoop, function-level reset, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, emergency power reduction, ten-bit tags, OBFF, and end-to-end TLP prefix blocking. Link fields expose supported/current speed and width, ASPM/power-management controls, retrain/disable/common-clock controls, bandwidth status/interrupt enables, compliance controls, and de-emphasis/margin settings.

### Complete VF2 and VF3 Maps

The chunk then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf2_bifcfgdecp` and later `vf3_bifcfgdecp`. VF2 and VF3 repeat the same register-family layout as VF1, beginning with `VENDOR_ID` and `DEVICE_ID` and continuing through ARI control.

These repeated maps are not abstractions; each VF number has its own generated macro names. That lets driver, firmware, or tooling refer to a specific virtual function's config-space fields without runtime string construction, but it also means mechanical drift between repeated families is a real risk.

### VF4 Partial Map

The final section starts `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp`. It covers VF4 identity, command/status, class/header, BAR, adapter, interrupt, PCIe device/link capability/control/status, device capability/control/status 2, and `LINK_CAP2`.

The chunk ends at `BIF_CFG_DEV0_EPF0_VF4_LINK_CAP2__DRS_SUPPORTEDRESERVED_MASK`. VF4 `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields continue in the next chunk.

## Control Flow

There is no executable control flow in this header. The flow is compile-time and external:

1. AMDGPU NBIO 2.3 or related SR-IOV code includes the generated NBIO offset, mask, and default headers.
2. Code selects the needed VF register/config-space macro.
3. Helper macros shift and mask fields when composing writes or decoding reads.
4. PCIe/NBIO hardware, firmware, or hypervisor state changes according to the resulting register access.

Because these are PCI configuration-space definitions, access may be through PCI config mechanisms, SMN/index-data paths, PF-mediated virtualization code, or firmware/hypervisor interfaces rather than ordinary direct C calls in this header.

## State and Persistence Behavior

The header has no local state. It names hardware-visible state in NBIO PCI configuration registers for virtual functions. That state persists until reset, FLR, VF teardown, power transition, firmware action, hypervisor action, or explicit driver writes.

Important state represented here includes:

- Per-VF PCI identity, class, header, BAR, ROM, subsystem, interrupt, and capability-chain presentation.
- PCI command/status enables and error/status latches.
- PCIe device and link capability/control/status fields, including negotiated link width/speed, payload sizing, read request sizing, relaxed ordering, no-snoop, FLR, completion timeout, LTR, OBFF, and compliance controls.
- MSI/MSI-X programming state for VF1-VF3, including message address/data, masking, pending bits, table location, and PBA location.
- AER status, masks, severity, capability/control, captured header log, and TLP prefix log fields.
- ATS and ARI capability/control state used by address translation and alternative routing ID behavior.

Several fields are command-like or write-one-to-clear style in the PCIe specification, such as status/error bits, FLR initiation, link retraining, AER clear/status fields, and interrupt pending/mask controls. The macros only describe bit positions; ordering, polling, and clear semantics come from the owning PCIe/NBIO code and hardware specification.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 header set:

- `nbio_2_3_offset.h` supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets.
- `nbio_2_3_default.h` supplies reset/default values for related NBIO registers.
- AMDGPU SOC15/register helpers consume the generated `__SHIFT` and `_MASK` names through field composition/extraction macros.

Observed source-tree integration includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_sh_mask.h` with the matching offset/default headers for NBIO 2.3 register programming.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes this mask header in virtualization-oriented AMDGPU code.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include the same generated NBIO headers for NBIO/PCIe-related SMU platform behavior.

The specific `BIF_CFG_DEV0_EPF0_VF*` fields align with the offset-header chunk that maps per-VF PCI configuration offsets. The mask header gives bit-level interpretation for those offsets; it does not by itself identify the access path or access permissions for PF versus VF contexts.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can alter unrelated PCIe configuration bits, break VF enumeration, disable memory/bus-master access, misreport capabilities, or mask real PCIe errors.
- Repeated VF maps are easy to damage mechanically. VF1, VF2, VF3, and VF4 use near-identical families with only the VF number changed; copying a field from the wrong VF macro can compile cleanly while targeting the wrong virtual function.
- PCIe status, AER, MSI/MSI-X, FLR, and link-control fields have side effects. Treating all masks as ordinary read/write configuration can lose error evidence, trigger resets, disrupt interrupts, or retrain/disable links unexpectedly.
- MSI layout aliases must be interpreted according to enabled 32-bit versus 64-bit MSI format. The presence of both normal and `_64` message-data/mask/pending families reflects layout-dependent interpretation, not independent storage for every mode.
- ATS, ARI, LTR, OBFF, atomic operation, ten-bit tag, IDO, and TLP-prefix fields affect host interconnect behavior. Enabling unsupported combinations can create protocol errors or bad performance in SR-IOV guests.
- AER header and TLP prefix log fields are diagnostic state. Incorrect clearing or decoding can hide the first failing transaction and make field failures hard to diagnose.
- VF access rights are virtualization-sensitive. PF, VF guest, hypervisor, and firmware may not all be allowed to program the same fields, even though the bit definitions are visible in a shared header.
- The chunk boundaries are partial: the first VF1 `VENDOR_ID` and the complete VF4 tail are outside this document. File-level conclusions need reconciliation with neighboring chunks.

## Test and Validation Signals

Useful validation is mostly build, SR-IOV, PCIe, and hardware bring-up coverage:

- Build AMDGPU code paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU, and SMU11 platform files.
- SR-IOV VF enumeration should expose correct PCI IDs, class codes, BARs, capability pointers, PCIe capabilities, MSI/MSI-X capabilities, AER, ATS, and ARI structures for VF1-VF4.
- VF reset and teardown tests should verify FLR initiation/status behavior and that command/status bits return to expected defaults.
- MSI/MSI-X interrupt tests should validate message programming, mask/pending behavior, vector delivery, and PBA/table interpretation for VF1-VF3.
- PCIe link and power-management tests should verify payload/read-request sizing, ASPM/LTR/OBFF controls, link retraining, bandwidth status, and compliance bits do not regress.
- AER diagnostics or error-injection tests should verify uncorrectable/correctable status, mask, severity, header log, and TLP prefix log decoding and clearing.
- Static generated-header checks can compare repeated VF1-VF4 field layouts against adjacent chunks and against `nbio_2_3_offset.h` to catch missing fields, mask-width drift, or mid-family truncation.

## Unresolved Cross-Chunk References

Line 29341 is inside `BIF_CFG_DEV0_EPF0_VF1_DEVICE_ID`; the `VF1_VENDOR_ID` field and the comment introducing `VF1_DEVICE_ID` are in the previous chunk. Line 31771 ends at the last visible `VF4_LINK_CAP2` mask; the following VF4 `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields are in the next chunk. The final per-file research document should stitch these boundaries before making complete claims about VF1 or VF4.

### subset-b-002917: lines 31772-34201

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h

Chunk: `subset-b-002917`
Covered source range: lines 31772-34201 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h`

## Purpose

This chunk is a generated AMD NBIO 2.3 register field mask header section. It contains C preprocessor constants for PCI/PCIe configuration-space register fields exposed through the NBIO/NBIF block; it is not executable driver logic.

The covered range contains 2,143 `#define` lines and 281 comment lines. It spans the tail of the `BIF_CFG_DEV0_EPF0_VF4` virtual-function configuration block, complete `BIF_CFG_DEV0_EPF0_VF5` and `BIF_CFG_DEV0_EPF0_VF6` blocks, and nearly all of `BIF_CFG_DEV0_EPF0_VF7` through the first two `PCIE_ARI_CNTL` shift definitions. The `addressBlock` comments identify the covered VF blocks as `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`, `vf6_bifcfgdecp`, and `vf7_bifcfgdecp`; VF4 began in the previous chunk.

The chunk starts mid-register: line 31772 is only the `BIF_CFG_DEV0_EPF0_VF4_LINK_CAP2__DRS_SUPPORTEDRESERVED_MASK`, while the matching register comment and most `LINK_CAP2` fields are in the prior chunk. It also ends mid-register: `BIF_CFG_DEV0_EPF0_VF7_PCIE_ARI_CNTL__ARI_FUNCTION_GROUP__SHIFT` and the three ARI control masks are in the next lines after this chunk. File-level reconciliation should treat both boundaries as expected split points.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The interface is the generated macro contract consumed by AMDGPU register helpers:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift used to encode or decode a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, usually as a 16-bit or 32-bit literal with `L` suffix.
- The matching configuration-space offsets live in companion offset headers, notably `nbio_2_3_offset.h` for this NBIO generation and the closely related `nbif_6_3_1_offset.h` VF configuration-space layout.

Important register families in this chunk include:

- `BIF_CFG_DEV0_EPF0_VF4_LINK_CNTL2` and `LINK_STATUS2`, covering target link speed, compliance entry, autonomous speed disable, de-emphasis, PCIe 8 GT/s equalization phase status, downstream presence, and DRS message status.
- `VF4`, `VF5`, `VF6`, and `VF7` MSI/MSI-X capability fields: capability-list IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector masking fields, message address/data, mask and pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- Complete `VF5`, `VF6`, and `VF7` standard PCI configuration fields: vendor/device IDs, command/status, revision/class code bytes, cache line, latency, header, BIST, six BARs, CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- `VF5`, `VF6`, and `VF7` PCIe capability fields: PCIe capability list/header, device capability/control/status, link capability/control/status, device capability 2/control 2/status 2, and link capability 2/control 2/status 2.
- Vendor-specific enhanced capability fields: VSEC capability ID/version/next pointer, VSEC ID/revision/length, and two 32-bit scratch registers.
- Advanced Error Reporting fields: enhanced capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- ATS fields: capability header, invalidate queue depth, page-aligned request, global invalidate support, smallest translation unit (`STU`), and `ATC_ENABLE`.
- ARI fields: enhanced capability header, MFVC/ACS function group capability bits, next function number, and the beginning of ARI control for MFVC and ACS function group enables.

The repeated VF5/VF6/VF7 blocks each expose 26 basic PCI configuration register comments and 53 PCIe/extended capability register comments in this chunk. The field layouts are intentionally near-identical across those virtual functions; only the VF prefix changes.

## Control Flow

This header has no internal control flow. At compile time, consumers include the header and use the macros in register read/modify/write expressions. Runtime control flow lives in AMDGPU/NBIO code that:

1. Includes `nbio/nbio_2_3_offset.h` and `nbio/nbio_2_3_sh_mask.h`.
2. Reads a 16-bit or 32-bit NBIO/PCIe register through helper APIs such as `RREG32_SOC15`, `RREG32_PCIE`, or `RREG32_NO_KIQ`.
3. Extracts fields by masking and shifting, or constructs values with helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.
4. Writes back via `WREG32_SOC15`, `WREG32_PCIE`, or related helpers when the field is writable.

Direct local include sites for this NBIO mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which programs NBIO doorbell ranges, interrupt controls, memory aperture state, PCIe LTR, link/strap behavior, and HDP remap registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which uses NBIO register definitions while implementing SR-IOV/MxGPU mailbox communication between a VF and PF.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include the header for NBIO/PCIe strap and link-related power-management interactions.

The exact VF4-VF7 macros in this chunk are configuration-space field definitions rather than active logic. They become behaviorally relevant when SR-IOV, virtualization, PCIe capability setup, MSI/MSI-X programming, AER reporting, ATS, or ARI paths address the corresponding virtual-function configuration registers.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, perform I/O, or persist data. Its only persistence is as compile-time constants embedded into object code.

The hardware state described by these macros lives in PCI/PCIe configuration registers for virtual functions under device 0, endpoint function 0. That state persists until changed by the driver, PCI core, host PF/hypervisor, firmware, FLR, bus reset, GPU reset, suspend/resume, or hardware error handling. Important state categories include:

- VF identity and configuration header state, including vendor/device IDs, class code, BAR decode fields, command enables, status flags, capability pointer, ROM BAR, and interrupt pin/line fields.
- PCIe capability state, including max payload/read-request capabilities, relaxed ordering, phantom functions, no-snoop, extended tag, L0s/L1 exit latencies, link width/speed capability, active link status, slot clock, bandwidth management, and autonomous bandwidth status.
- Link-control 2 and link-status 2 state for target speed, compliance mode, de-emphasis, and equalization progress/failure signals.
- MSI/MSI-X state such as enable bits, vector count, message address/data, per-vector mask and pending bits, MSI-X table location, PBA location, and function mask.
- AER state, including uncorrectable/correctable status latches, masks, severity policy, first-error pointer, ECRC controls, multi-header controls, header logs, and TLP prefix logs.
- ATS and ARI state, including ATC enable, STU, invalidate queue depth, page-aligned request support, global invalidate support, next function number, and ARI function group controls.

These macros do not encode access type or ordering. Status fields may be read-only or write-one-to-clear depending on the hardware specification; control fields may be owned by the PF, VF, PCI core, IOMMU setup, or firmware. Consumers must respect the register spec and virtualization ownership model.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor. The practical dependencies are the AMDGPU register helper conventions and the matching offset headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h`

`nbio_2_3_offset.h` contains matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets for VF4-VF7 configuration registers. The related NBIF 6.3.1 offset header exposes similar `cfgBIF_CFG_DEV0_EPF0_VF*_*` names without the `_0` instance suffix. These offset macros pair with this chunk's masks/shifts when code needs to access a VF's config-space fields through NBIO/NBIF register windows.

Integration points in the driver stack include:

- AMDGPU NBIO initialization and management in `amdgpu/nbio_v2_3.c`.
- SR-IOV/MxGPU VF-PF mailbox flows in `amdgpu/mxgpu_nv.c`.
- SMU 11 power-management code for Navi10 and Sienna Cichlid ASICs, which uses NBIO and PCIe-related register definitions while managing DPM, link, and strap-related behavior.
- Linux PCI/MSI/MSI-X/AER/ATS/ARI semantics, because these fields mirror standard and extended PCIe capability layouts.
- GPU virtualization infrastructure, where VF configuration-space fields may be shadowed, trapped, or mediated by a PF driver, hypervisor, or host PCI subsystem.

## Risks And Edge Cases

The main implementation risk is silent hardware misprogramming. These are untyped preprocessor constants, so the compiler cannot verify that a mask belongs to the register being read, that the field value fits the mask, or that a VF5 macro is not accidentally used for VF6/VF7.

Chunk boundaries are a real reconciliation risk. `VF4_LINK_CAP2` is incomplete at the start of this chunk, and `VF7_PCIE_ARI_CNTL` is incomplete at the end. Pair-completeness checks must account for adjacent chunks before reporting missing masks or shifts.

Repeated VF blocks are easy to confuse. VF5, VF6, and VF7 carry identical layouts with only the virtual-function prefix changed. A copy/paste instance error can compile cleanly but address or interpret the wrong VF's configuration state, which is especially dangerous for MSI/MSI-X, AER, ATS, and ARI fields.

Configuration-space width matters. Many fields are 8-bit or 16-bit PCI configuration fields, while others are 32-bit extended capability registers. Using 32-bit helpers against narrower fields or assuming natural alignment without checking the offset header can corrupt neighboring config bytes.

Virtualization ownership matters. A VF driver may not be allowed to write all PCIe capability, AER, ATS, ARI, MSI-X table, or BAR fields directly. Some values may be emulated, filtered, or reset by the PF or hypervisor. Code that treats these masks as normal MMIO ownership can break SR-IOV isolation.

Error-reporting fields have side effects. AER status and header-log registers may latch first-error information; clearing, masking, or changing severity at the wrong time can hide root-cause data or change whether an error is fatal/nonfatal/correctable.

ATS and ARI fields affect IOMMU and PCIe routing behavior. Incorrect `ATC_ENABLE`, `STU`, invalidate queue, ARI next-function, or function-group programming can lead to stale translations, isolation failures, bad requester IDs, or enumeration issues.

High-bit masks such as `0x80000000L` should be handled as unsigned 32-bit quantities by consumers. Ad hoc signed arithmetic or implicit narrowing can produce incorrect comparisons or shifts on some build configurations.

## Test Signals

Useful validation signals include:

- build coverage for translation units that include `nbio_2_3_sh_mask.h`, especially `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, `pm/swsmu/smu11/navi10_ppt.c`, and `pm/swsmu/smu11/sienna_cichlid_ppt.c`;
- generated-header consistency checks across the complete file, verifying that every field has a matching `__SHIFT`/`_MASK` pair after adjacent chunks are merged;
- offset/mask consistency checks against `nbio_2_3_offset.h` and `nbif_6_3_1_offset.h`, especially for VF4-VF7 standard PCI, PCIe capability, MSI/MSI-X, AER, ATS, and ARI registers;
- duplicate-layout checks confirming that VF5, VF6, and VF7 field masks/shifts are identical where expected and differ only by prefix;
- SR-IOV boot and teardown tests with multiple VFs enabled, checking VF enumeration, BAR sizing, class/vendor/device IDs, command/status behavior, and FLR/reset recovery;
- MSI and MSI-X tests for VF interrupt delivery, vector enable/disable, masking, pending bits, function mask behavior, and table/PBA address interpretation;
- PCIe AER injection or fault-observation tests that confirm correct uncorrectable/correctable status bits, masks, severity fields, first-error pointer, and header/TLP-prefix logging;
- ATS/IOMMU validation with VF DMA enabled, including ATC enable/disable, invalidation behavior, page-aligned request handling, and suspend/resume reset behavior;
- ARI/SR-IOV enumeration tests confirming next-function number and function-group controls do not confuse PCI core routing or VF discovery;
- register readback tests using the normal AMDGPU register helpers, confirming that shifted values occupy only the intended masked bits and that no adjacent config fields change unexpectedly.

### subset-b-002918: lines 34202-36635

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 34202-36635

## Scope

This chunk covers a generated AMD NBIO 2.3 register shift/mask header segment for PCIe configuration-space fields on device 0, endpoint function 0 virtual functions. The range begins with the final four macros for `BIF_CFG_DEV0_EPF0_VF7_PCIE_ARI_CNTL`, then contains complete `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, `vf9`, and `vf10` address blocks, and ends partway through `vf11` at `BIF_CFG_DEV0_EPF0_VF11_LINK_CAP2`.

The chunk contains only C preprocessor definitions. There are no functions, structs, enums, variables, executable statements, or in-file storage. In this range there are 2,147 `#define` entries, mostly paired as `__SHIFT` and `_MASK` constants, covering 276 register/comment groups.

## Purpose

The purpose of this header chunk is to encode bit positions and bit masks for NBIO/BIF PCI and PCIe configuration registers exposed for SR-IOV virtual functions. Driver code uses this file together with the corresponding `nbio_2_3_offset.h` register-address header and AMDGPU register helper macros to compose, read, and decode hardware register fields without hard-coding bit constants in C logic.

The macro naming convention is:

- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>__SHIFT` for a field's least-significant bit.
- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>_MASK` for the field mask in the register value.

The repeated virtual-function blocks make the same PCIe capability model available for each VF number. In this chunk, VF8, VF9, and VF10 are complete; VF11 is truncated by the chunk boundary after `LINK_CAP2`; VF7 appears only as the tail of the previous chunk's ARI control register.

## Important Macro Families

### PCI Configuration Header

Each complete VF block starts with PCI configuration header fields:

- `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS` describe device identity and class-code metadata.
- `COMMAND` exposes standard enable/control bits such as I/O access, memory access, bus mastering, SERR, parity response, and interrupt disable.
- `STATUS` exposes readiness, interrupt status, capability-list presence, parity/error reporting, abort status, and DEVSEL timing.
- `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST` encode standard PCI header fields.
- `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, and min/max latency model the rest of the type-0 PCI header layout.

These fields are mostly 8-bit, 16-bit, or 32-bit PCI config-space fields with masks such as `0xFFL`, `0xFFFFL`, and `0xFFFFFFFFL`. Multi-field registers use masks that match standard PCI bit allocation, for example `ADAPTER_ID` splits subsystem vendor ID and subsystem ID into low and high 16-bit halves.

### PCIe Capability Registers

The `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` groups define the PCI Express capability structure for each VF.

Important fields include:

- Device capabilities such as max payload support, phantom functions, extended tags, L0s/L1 acceptable latency, role-based error reporting, slot power fields, and function-level reset capability.
- Device control bits for enabling corrected/non-fatal/fatal/unsupported-request reporting, relaxed ordering, extended tags, no-snoop, maximum payload size, maximum read request size, and initiating FLR.
- Device status bits for corrected, non-fatal, fatal, and unsupported request errors, auxiliary power, pending transactions, and emergency power-reduction detection.
- Link capability, control, and status fields for link speed, link width, ASPM/PM support, exit latencies, clock power management, bandwidth notification, link disable/retrain, common-clock configuration, data link active state, and bandwidth status.

These macros are the bit-level ABI for any NBIO code that needs to inspect or program per-VF PCIe link/device behavior. Many fields are capability or status bits read from hardware, while control fields can trigger visible PCIe behavior such as FLR or link retraining when written through the matching register address.

### PCIe Capability 2 / Link 2

`DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover later PCIe capability extensions.

The chunk includes fields for completion-timeout ranges and disable support, ARI forwarding, atomic operations, ID-based ordering, latency tolerance reporting, ten-bit tags, OBFF, end-to-end TLP prefixes, emergency power reduction, and FRS support. Link 2 fields include supported link speeds, crosslink support, SKP ordered-set generation/receive support, retimer presence-detect support, target link speed, compliance controls, transmit margin, de-emphasis, equalization completion/phase status, and downstream component presence.

The VF11 section ends inside this family. It includes `VF11_LINK_CAP2` definitions in full through `DRS_SUPPORTEDRESERVED_MASK` at the chunk boundary context, while later VF11 Link Control 2, Link Status 2, MSI/MSI-X, AER, ATS, and ARI fields belong to a later chunk.

### MSI and MSI-X

The complete VF8, VF9, and VF10 blocks include MSI and MSI-X capability structures:

- `MSI_CAP_LIST` and `MSI_MSG_CNTL` encode the capability header and MSI enable/control fields, including multiple-message capability, 64-bit address capability, vector mask capability, and pending-enable behavior.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, and their 64-bit layout aliases expose message address, data, mask, and pending bits.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` define MSI-X capability header, table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

These fields are integration points for interrupt routing and virtualization. The header only provides the encodings; actual interrupt enablement, vector allocation, and guest/PF ownership rules are implemented elsewhere in AMDGPU, PCI core, and virtualization code.

### Vendor-Specific and Advanced Error Reporting

For VF8 through VF10, the chunk defines:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`.
- `PCIE_ADV_ERR_CAP_CNTL`.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3`.
- `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`.

The uncorrectable error groups cover data link protocol errors, surprise down, poisoned TLP, flow-control protocol errors, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic egress block, TLP prefix blocked, and poisoned TLP egress block. Correctable error groups cover receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal errors, correctable internal error, and header-log overflow. The `ADV_ERR_CAP_CNTL` fields expose first-error pointer, ECRC capabilities/enables, multi-header recording, TLP prefix log presence, and completion-timeout logging capability.

This is the most diagnostic-heavy area in the complete VF blocks. It supports PCIe AER decoding and masking, but status clear/write-one-to-clear semantics are determined by the hardware register specification and calling code, not by this header.

### ATS and ARI Extended Capabilities

The complete VF8 through VF10 blocks end with Address Translation Service and Alternative Routing-ID Interpretation definitions:

- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` include extended capability header fields, invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` include capability header fields, MFVC/ACS function-group capabilities, next function number, enable bits, and function group selection.

The chunk also starts with the final `VF7_PCIE_ARI_CNTL` masks, confirming this file repeats the same capability model across VF blocks. ATS and ARI fields matter for PCIe virtualization and IOMMU-facing behavior; incorrect enablement can affect DMA address translation and function routing.

## Control Flow

There is no C control flow in this chunk. The effective control flow is external:

1. A driver source includes `nbio_2_3_sh_mask.h`, usually alongside `nbio_2_3_offset.h`.
2. Driver code selects a register address from the offset header or through an AMDGPU NBIO helper.
3. It uses field masks and shifts from this header with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `RREG32_PCIE`, or related SOC15/NBIO access wrappers.
4. The resulting read or write operation affects the NBIO hardware register or PCIe configuration-space shadow for the selected virtual function.

Because this segment is generated constants, correctness depends on exact alignment between the hardware generation scripts, the offset header, and the ASIC register specification. There is no local runtime validation.

## State and Persistence Behavior

The header itself has no mutable state and persists nothing. State lives in NBIO/PCIe hardware registers and in whatever kernel or firmware layers read or write them.

Field semantics vary by register family:

- Identity and capability fields are generally hardware-defined or firmware-populated and read mostly as stable configuration.
- Control fields such as `COMMAND`, `DEVICE_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL`, `LINK_CNTL2`, `MSI_MSG_CNTL`, `MSIX_MSG_CNTL`, `ATS_CNTL`, and `ARI_CNTL` can alter hardware behavior until reset, reinitialization, or another writer changes them.
- Status and error fields such as `STATUS`, `DEVICE_STATUS`, `LINK_STATUS`, `LINK_STATUS2`, AER status, and MSI pending fields reflect transient hardware events and may have clear-on-write or write-one-to-clear behavior outside this header.
- Log registers such as PCIe header and TLP prefix logs persist captured error context until cleared or overwritten according to PCIe AER hardware behavior.

In SR-IOV systems, access policy is also stateful: the PF, guest VF, PCI core, IOMMU, firmware, or hypervisor may own different subsets of these registers.

## Dependencies and Integration Points

Direct dependencies are minimal because this is a header of macros guarded by `_nbio_2_3_SH_MASK_HEADER`. Important surrounding files and users include:

- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies matching register offsets such as the `cfgBIF_CFG_DEV0_EPF0_VF*_...` names. The masks here are not useful without a matching address source.
- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies generated defaults for the same NBIO IP generation.
- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, the primary NBIO 2.3 implementation. It includes this header and provides the `amdgpu_nbio_funcs` implementation for revision ID, memory access, doorbell apertures, interrupt helper setup, clock gating, ASPM/LTR programming, and register remapping. This chunk's VF-specific PCI config macros are not directly referenced in the searched C sources, but they are part of the same generated include surface.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h` for multi-vGPU/SR-IOV support paths.
- SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include NBIO 2.3 generated register headers for platform-specific register access.

The common register helper macros are defined elsewhere in the AMDGPU tree. This file provides only numeric constants, so all type checking, access width selection, locking, reset sequencing, and privilege checks are implemented by callers.

## Risks

- Bitfield drift: if these generated masks do not match the actual NBIO 2.3 hardware register layout, field extraction and writes can silently target the wrong bits.
- Offset/mask mismatch: using masks from this header with an offset from another NBIO version or another VF instance can corrupt unrelated PCIe config state.
- Write-sensitive fields: macros for FLR, link retraining, MSI/MSI-X enable, ATS enable, ARI enable, AER masks, and completion timeout controls describe fields that can have immediate system-visible effects when written.
- Virtualization ownership: per-VF config registers may be visible through PF emulation, guest config access, or hypervisor paths. Using the wrong access path risks breaking isolation or racing guest/host ownership.
- Status clearing semantics: AER and PCI status fields often use write-one-to-clear behavior. Generic read/modify/write code must preserve or clear bits intentionally.
- Chunk boundary risk: this work item ends in the middle of the VF11 capability block. A final per-file report must merge with adjacent chunks before drawing complete conclusions about VF11.
- Generated-code maintenance: manual edits to this file are high risk. Changes should come from the register database/generator or be verified against hardware documentation.

## Test Signals

Since this chunk is a generated macro table, meaningful tests are mostly compile-time, integration, and hardware/VM validation rather than unit tests inside the header.

Useful signals include:

- Kernel build coverage for AMDGPU configurations that include `nbio_v2_3.c`, MXGPU/SR-IOV code, and SMU 11 power-management files.
- Compile-time detection of missing or renamed macros in code that uses `REG_SET_FIELD`/`REG_GET_FIELD` with NBIO 2.3 fields.
- Static comparison against `nbio_2_3_offset.h` to ensure every register family has matching offset and mask definitions for each VF block.
- SR-IOV smoke testing with multiple VFs enabled, confirming guest enumeration, BAR sizing, MSI/MSI-X delivery, FLR, reset recovery, and PF/VF isolation.
- PCIe AER injection or fault-observation tests checking that uncorrectable/correctable error status, mask, severity, header log, and TLP prefix log fields decode as expected.
- ATS/ARI validation under an IOMMU-enabled setup, confirming address translation enablement and function routing remain correct.
- ASPM/link-state diagnostics that read link speed, width, training, equalization, and bandwidth notification fields before and after power-management transitions.

### subset-b-002919: lines 36636-39061

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 36636-39061

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts in the middle of `BIF_CFG_DEV0_EPF0_VF11_LINK_CAP2`, continues through the rest of virtual function 11's PCIe config capability block, then covers nearly complete repeated config-space field definitions for virtual functions 12, 13, and 14. It ends inside the VF14 ARI enhanced-capability list definition, before the VF14 ARI capability/control fields that follow in the next chunk. Although the repository path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header chunk is to publish the bit layout contract for NBIO 2.3 virtual-function PCI/PCIe configuration decoder registers. Each represented field is exposed as one or both of:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update the field.

The companion `nbio_2_3_offset.h` file maps these same `BIF_CFG_DEV0_EPF0_VF*_0_*` register names to PCI configuration offsets. AMDGPU code includes both the offset header and this shift/mask header from NBIO paths such as `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU power-management files. Runtime code then uses AMDGPU register helpers and field helpers such as `RREG32_*`, `WREG32_*`, `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO register-address macros to access the actual hardware fields.

## Important Macro Families

The VF11 portion begins at the tail of second-generation link capability fields. It includes supported link speed masks, crosslink support, lower SKP ordered-set generation/receive support, retimer presence-detect support, DRS reserved/support bit naming, link control 2 fields for target speed, compliance entry, autonomous speed disable, de-emphasis, transmit margin, modified compliance, and compliance SOS. It also defines link status 2 fields for current de-emphasis, 8 GT/s equalization completion and phase success, link equalization request, retimer detection, crosslink resolution, downstream-component presence, and DRS message receipt.

The MSI and MSI-X blocks repeat for VF11 through VF14. MSI definitions cover capability list ID/next pointer, enable, multi-message capability and enable fields, 64-bit support, per-vector masking capability, low/high MSI message address, message data, mask, 64-bit data/mask aliases, and pending bits. MSI-X definitions cover capability list ID/next pointer, table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

The PCIe vendor-specific capability block defines enhanced-capability list metadata, VSEC header fields, and two scratch dwords for each VF. These are generic vendor-specific config-space slots; the macros only describe the field placement and do not define firmware or hypervisor policy for the scratch registers.

The advanced error reporting block is dense and repeated. For VF11 through VF14 it defines AER enhanced-capability list metadata, uncorrectable error status/mask/severity fields, correctable error status/mask fields, advanced error capability/control bits, four TLP header-log dwords, and four TLP-prefix-log dwords. The uncorrectable families include data link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked bits. The correctable families include receiver error, bad TLP, bad DLLP, replay number rollover, replay timer timeout, advisory nonfatal error, correctable internal error, and header-log overflow.

VF12, VF13, and VF14 each start with a full standard PCI header and conventional PCIe capability layout. The standard fields include vendor/device ID, command, status, revision and class-code bytes, cache-line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency. Command/status masks expose ordinary PCI access enables, bus mastering, SERR and interrupt-disable controls, capability-list presence, parity and target/master abort status, DEVSEL timing, and detected parity error.

The PCIe capability and device/link blocks for VF12 through VF14 include PCIe capability list metadata, port type, slot implementation, interrupt message number, max payload support, phantom functions, extended tags, endpoint L0s/L1 acceptable latencies, role-based error reporting, captured slot power limit, FLR support, max payload/read request programming, relaxed ordering, no-snoop, auxiliary power PM, phantom function enable, extended tag enable, error reporting enables, unsupported request reporting, fatal/nonfatal/correctable detected status, transaction pending, link speed/width/aspm capability, L0s/L1 exit latencies, clock power management, surprise down reporting, data link active reporting, link bandwidth notification support, ASPM control, common clock, retrain, link disable, read completion boundary, extended sync, hardware autonomous width disable, link bandwidth interrupt enables/status, target link speed, compliance controls, equalization status, and Gen2+ link capability/status fields.

The second-generation device capability/control fields cover completion timeout support/disable, ARI forwarding, AtomicOp support and request enable, AtomicOp egress blocking, ID-based ordering request/completion enable, latency tolerance reporting, OBFF support/enable, ten-bit tag support/enable, end-to-end TLP prefix support/blocking, emergency power reduction, fast role swap, and reserved device-status 2 words. The ATS blocks define enhanced-capability list metadata, invalidate queue depth, page-aligned request support, global invalidate support, small translation unit, and ATC enable. The chunk ends at the beginning of the VF14 ARI enhanced-capability list, after its `CAP_ID`, `CAP_VER`, `NEXT_PTR`, and `CAP_ID_MASK` definitions.

## Control Flow

There is no runtime control flow in this chunk. The effective use pattern is supplied by consuming driver code:

1. Choose the appropriate virtual-function register offset from `nbio_2_3_offset.h` or another ASIC-specific register-address path.
2. Read the corresponding PCIe config or NBIO register through AMDGPU register access helpers.
3. Decode a field by applying the generated `_MASK` and `__SHIFT` constants directly or through helper macros such as `REG_GET_FIELD`.
4. For writable fields, merge a new field value with preserved register bits, commonly through `REG_SET_FIELD`, then write the value back through the same access path.

The repeated VF12/VF13/VF14 layout is table-like hardware metadata, but the header does not implement iteration over VFs or capabilities. Any loop, VF selection, SR-IOV policy, reset sequencing, interrupt setup, link training, or error-recovery behavior is implemented in AMDGPU/NBIO/PCIe/SR-IOV code outside this generated header.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-visible PCI configuration and PCIe extended capability state owned by the GPU, PCIe fabric, firmware, host kernel, and virtualization stack.

Some represented fields are configuration that can persist until reset, FLR, suspend/resume, power transition, VF teardown, or explicit reprogramming: command access enables, bus mastering, interrupt disable, BAR values, MSI/MSI-X message address/data/masks, device/link controls, completion timeout controls, AER masks and severity bits, ECRC controls, ATS control, ARI capability-list metadata, and vendor-specific scratch dwords.

Other fields are hardware-owned observations, sticky status, logs, pending bits, or write-one-to-clear style status in real PCIe hardware: PCI status errors, device and link status, link equalization state, bandwidth status, AER uncorrectable/correctable error status, first-error pointer, multi-header received state, TLP header logs, TLP prefix logs, MSI pending bits, and MSI-X pending-bit-array state. The macro names do not encode access permissions or clear semantics; consumers must follow PCIe and AMDGPU register programming rules.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with sibling generated headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`, especially `nbio_2_3_offset.h`, because offset macros select the register address while this file selects the fields within the register value.

Primary integration points are AMDGPU NBIO initialization, PCIe configuration, interrupt setup, AER/RAS diagnostics, power-management paths, suspend/resume, reset/FLR handling, and SR-IOV virtualization. `nbio_v2_3.c` and `mxgpu_nv.c` include this header directly, and SMU power-management files include it for ASIC-specific NBIO register programming. The VF-oriented macro families are especially relevant when a PF, host driver, hypervisor, or guest-visible path needs to reason about virtual-function PCI headers, link capability reporting, MSI/MSI-X programming, AER exposure, ATS enablement, or ARI traversal.

Because these are untyped preprocessor constants, missing or renamed macros usually fail at compile time, but incorrect numeric shifts or masks can compile cleanly and produce wrong hardware programming. Manual edits should be treated as changes to an ASIC register ABI and checked against AMD's authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first lines are already inside VF11 `LINK_CAP2`, and the final line stops inside VF14 `PCIE_ARI_ENH_CAP_LIST`; adjacent chunks are needed for whole-register and whole-VF conclusions.
- Access width matters. The range mixes 8-bit PCI config bytes, 16-bit command/status/capability words, and 32-bit dwords. Using a 32-bit read-modify-write against byte/word fields without preserving neighboring bytes can corrupt adjacent PCI config state.
- Status and log fields are not distinguished by type. AER status, PCI status, link status, MSI pending, and log registers may be sticky or write-one-to-clear in hardware; generic read-modify-write treatment is unsafe without the relevant PCIe semantics.
- Interrupt definitions are delivery-critical. Bad MSI/MSI-X enable, function mask, message address/data, table/PBA offset, vector mask, or pending-bit interpretation can cause lost interrupts, spurious interrupts, or incorrect VF isolation.
- Link and equalization fields are interoperability-sensitive. Incorrect target speed, compliance, de-emphasis, autonomous speed disable, equalization, DRS, retimer, or downstream-presence masks can cause link training failures, misleading diagnostics, or resume regressions.
- VF repetition creates off-by-one risk. VF11 through VF14 names are nearly identical; selecting the wrong VF register family or offset can expose, configure, or diagnose the wrong virtual function.
- AER mask/severity mistakes can hide real PCIe faults, escalate recoverable errors as fatal, or make header/TLP-prefix logs decode against the wrong bit layout.
- ATS and ARI fields affect isolation and enumeration. Incorrect ATC enable, translation unit, invalidate capability, or ARI capability-list metadata can break IOMMU-assisted operation or VF function discovery.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers, with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, ARI, reset, and power-management support enabled; missing macros should surface as compile failures.
- Run generated-header consistency checks against the NBIO 2.3 register source and sibling offset headers, including shift/mask pair presence, field width validation, and non-overlap checks within each register.
- Boot and PCI enumeration tests confirming VF12 through VF14 expose expected vendor/device IDs, class codes, BAR layout, command/status bits, capability pointers, PCIe capability structures, MSI/MSI-X capabilities, AER capability, ATS capability, and ARI enhanced-capability links.
- MSI/MSI-X interrupt tests for virtual functions, including enable/disable, function mask, vector mask, pending bits, 32-bit versus 64-bit message address/data handling, and table/PBA placement.
- PCIe link tests covering target speed, negotiated speed/width, retrain, autonomous speed controls, de-emphasis, equalization phase reporting, retimer detection, DRS reporting, bandwidth status, and suspend/resume transitions.
- AER or fault-injection tests validating uncorrectable/correctable status, mask, severity, first-error pointer, ECRC controls, header logs, TLP prefix logs, and recovery paths for each represented VF.
- SR-IOV and IOMMU tests validating that ATS enablement, invalidate capability reporting, ARI capability-list traversal, and per-VF PCI config access affect only the intended VF.

## Chunk-Specific Notes For Merge

Merge this chunk with adjacent `nbio_2_3_sh_mask.h` chunks before producing the final source-tree-aligned per-file research document. Preserve that this slice covers the VF11 PCIe capability tail plus full VF12/VF13 and almost-full VF14 standard PCI, PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and partial ARI field definitions.

### subset-b-002920: lines 39062-41493

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 39062-41493

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocation paths, locks, loops, branches, or direct register accesses in this range.

The slice starts at the tail of `BIF_CFG_DEV0_EPF0_VF14_PCIE_ARI_ENH_CAP_LIST`, covers the ARI capability/control masks for VF14, then defines complete repeated PCIe configuration-space field layouts for `BIF_CFG_DEV0_EPF0_VF15`, `BIF_CFG_DEV0_EPF0_VF16`, and `BIF_CFG_DEV0_EPF0_VF17`. It then begins the `BIF_CFG_DEV0_EPF0_VF18` block and stops inside `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`; the remaining VF18 PCIe extended capability, MSI/MSI-X, AER, ATS, and ARI fields continue after this chunk.

Although this file is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield positions for NBIO 2.3 SR-IOV virtual-function PCI configuration-space images. Each generated hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

The companion address file, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, provides the matching `cfgBIF_CFG_DEV0_EPF0_VF*_*` register locations. Runtime AMDGPU code combines those offsets with this shift/mask header through helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF14 fragment completes the end of a virtual-function extended capability chain. It includes `PCIE_ARI_ENH_CAP_LIST` masks for capability ID/version/next pointer, `PCIE_ARI_CAP` fields for MFVC/ACS function-group capability and next-function number, and `PCIE_ARI_CNTL` fields for enabling MFVC/ACS function groups and selecting an ARI function group. The matching VF14 ATS capability and most of its preceding PCIe block are outside this chunk.

The full VF15 through VF17 blocks repeat a standard SR-IOV VF PCI Type 0 configuration image. Each block starts with identity and header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type/device type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min-grant/max-latency bytes.

The PCIe capability portions for VF15 through VF17 define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, FLR capability/initiation, completion timeout controls, ARI forwarding, atomic operation enables, ID-based ordering, LTR, OBFF, 10-bit tag support, link speed/width, ASPM/power-management controls, link disable/retrain, common clock, autonomous width/speed disables, target link speed, de-emphasis, compliance controls, equalization status, and downstream/component presence status.

The MSI and MSI-X portions of VF15 through VF17 cover capability-list linkage, MSI enable/multiple-message/64-bit/per-vector masking controls, MSI address/data/mask/pending fields, 64-bit MSI aliases, MSI-X table size/function mask/enable fields, MSI-X table BIR/offset, and PBA BIR/offset fields. These constants describe how the VF interrupt capability appears in config space and how address/data/mask/pending state is packed.

The vendor-specific and AER portions define PCIe vendor-specific enhanced capability list/header fields, two vendor-specific payload dwords, AER enhanced capability list fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked conditions.

The ATS and ARI portions at the end of each full VF block define enhanced capability list entries plus ATS capability/control fields and ARI capability/control fields. ATS fields include invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable. ARI fields expose function-group support, next-function number, function-group enable bits, and selected function group.

The VF18 block begins another repeated VF config-space map. This chunk covers VF18 from vendor/device ID through `DEVICE_CNTL2` masks, including the standard header, BARs, PCIe capability, device/link capability and control/status, and the start of PCIe capability 2 control. It does not include VF18 `DEVICE_STATUS2`, link capability 2, MSI/MSI-X, vendor-specific, AER, ATS, or ARI fields.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes the generated constants:

1. AMDGPU code selects a `cfgBIF_CFG_DEV0_EPF0_VF*_*` offset from `nbio_2_3_offset.h`.
2. It reads or composes a 16-bit or 32-bit PCIe config-space value through the AMD register access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or via `REG_SET_FIELD`/`REG_GET_FIELD`.
4. It writes a control value, decodes a capability/status value, polls a hardware-owned bit, clears a sticky status, or exposes decoded state to a higher-level PCIe, SR-IOV, reset, interrupt, or diagnostics path.

Typical flows that can consume these fields include VF PCI capability presentation, VF MSI/MSI-X setup, AER error logging and clearing, function-level reset, PCIe link/power policy, ATS/ARI virtualization support, and PF/hypervisor inspection of VF config state.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU's PF/SR-IOV management code.

The represented state includes identity/header values, BAR and ROM address windows, command/status bits, capability-list pointers, PCIe capability/control/status fields, link capability and link training state, MSI/MSI-X programming state, vendor-specific capability payloads, AER error status/mask/severity/log data, ATS enablement and invalidation capability state, and ARI function-group controls. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The generated masks do not encode access permissions, reset defaults, side effects, polling rules, or ownership boundaries.

VF15 through VF17 are complete within this chunk, so their repeated config-space layout can be reasoned about locally. VF14 and VF18 are boundary fragments and require adjacent chunks before making whole-VF or whole-register claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 2.3 register database. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies the matching config-space addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies reset/default values for the same register families where generated.
- AMDGPU register helper macros and accessors, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Direct in-tree consumers of the NBIO 2.3 generated headers include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`. The most relevant integration surfaces are AMDGPU NBIO/BIF setup, PCIe link control, SR-IOV VF lifecycle, MXGPU virtualization paths, VF interrupt delivery, ATS/ARI capability handling, AER diagnostics, reset/FLR flows, and suspend/resume or runtime power transitions.

These fields also overlap generic PCIe concepts managed by platform firmware and the Linux PCI core: command/status, BARs, MSI/MSI-X, device/link control, AER, ATS, ARI, LTR, OBFF, completion timeout, and FLR. AMDGPU must pair the generated masks with the correct register address and with the ownership rules for the specific hardware access path.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts in the middle of VF14's extended capability tail and stops in the middle of VF18 `DEVICE_CNTL2`; adjacent chunks are required for complete VF14 and VF18 analysis.
- These are untyped preprocessor constants. A stale mask or shift can compile cleanly while decoding or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around VF15, VF16, VF17, and VF18 could silently target the wrong virtual function and break SR-IOV isolation or diagnostics.
- Register-address and field-mask mismatches are easy in generated headers. A valid `VF16_LINK_CNTL` mask applied to a `VF17` or non-VF offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, completion timeout, relaxed-ordering, no-snoop, LTR, OBFF, ARI, ATS, or link-control values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Width, aliasing, table offset/BIR, mask, or pending-bit mistakes can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures or confuse VF resource sizing.
- ATS and ARI fields are virtualization and addressing sensitive. Incorrect ATC enable/STU, invalidate capability interpretation, next-function number, or function-group controls can affect translation caching, VF enumeration, and function isolation.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v2_3.c`, `mxgpu_nv.c`, SMU11 files, or other generated-header include paths.
- Compare the VF15 through VF17 field layouts against `nbio_2_3_offset.h` and `nbio_2_3_default.h` to confirm the register names, order, and repeated VF stride remain synchronized.
- Boot affected hardware and confirm PCIe config exposure remains sane: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, AER, ATS, and ARI should decode consistently.
- In SR-IOV or MXGPU configurations, create and remove VFs around the VF15-VF18 range, bind guest drivers, exercise VF FLR, and verify that VF isolation, config-space access, ATS/ARI behavior, and mailbox/reset flows remain stable.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout behavior, LTR/OBFF state, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.
- For ATS-capable configurations, exercise IOMMU/ATS enablement and invalidation paths; translation faults, stale DMA mappings, or inconsistent ATC behavior can point to ATS control/capability field issues.

## Chunk Notes

- Lines 39062-39079 are only the end of VF14, specifically the ARI enhanced capability and ARI cap/control fields.
- Lines 39080-41167 are complete `BIF_CFG_DEV0_EPF0_VF15`, `VF16`, and `VF17` PCIe VF config-space shift/mask blocks.
- Lines 41168-41493 begin `BIF_CFG_DEV0_EPF0_VF18` and end inside `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`, after the `IDO_COMPLETION_ENABLE_MASK` line in the assigned slice; subsequent VF18 fields are outside this work item.

### subset-b-002921: lines 41494-43919

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 41494-43919

## Scope

This chunk covers a generated AMD NBIO 2.3 register shift/mask header section for PCIe BIF configuration space exposed through SR-IOV virtual functions. It starts in the middle of `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`, covers the rest of VF18's extended PCIe capability fields, all generated field macros for VF19 and VF20, and the front of VF21 through the first two `PCIE_ATS_CAP` shift definitions.

The range is C preprocessor data only. It defines no functions, structs, variables, runtime branches, locks, memory allocations, or direct register accesses. Its interface is the generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field bit mask.

The chunk contains 2,426 source lines and about 2,141 `#define` entries. The visible virtual-function prefixes are `BIF_CFG_DEV0_EPF0_VF18`, `VF19`, `VF20`, and `VF21`.

## Purpose

`nbio_2_3_sh_mask.h` is the field-layout side of the NBIO 2.3 hardware register ABI. Companion headers such as `nbio_2_3_offset.h` provide register offsets, while this file provides the bit positions and masks that software needs to compose or decode PCI configuration registers for AMDGPU NBIO/BIF blocks.

This chunk is focused on repeated PCI configuration-space layouts for endpoint function 0 virtual functions. The fields mirror standard PCI/PCIe configuration concepts: vendor/device IDs, command/status, BARs, PCIe capabilities, link control and status, MSI/MSI-X, vendor-specific capabilities, Advanced Error Reporting, Address Translation Services, and Alternative Routing-ID Interpretation.

Consumers normally use these macros through AMDGPU register helpers and generated idioms such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or NBIO-specific read/write paths. The macros themselves are not policy; they are constants that make driver reads and writes land on the correct hardware bits.

## Important Macro Families

### VF18 Tail

The chunk begins after the first part of `VF18_DEVICE_CNTL2`. Lines 41494-41862 complete VF18's extended PCIe capability layout:

- `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeout, ARI forwarding, atomic operation request/egress control, IDO, LTR, OBFF, end-to-end TLP prefix blocking, supported target link speeds, compliance entry, equalization status, retimer presence, crosslink state, downstream presence, and DRS message state.
- `MSI_*` and `MSIX_*` registers cover MSI enable/multivector/64-bit/per-vector masking, message address/data, mask and pending bitmaps, MSI-X table/PBA BIR and offsets, function mask, and MSI-X enable.
- `PCIE_VENDOR_SPECIFIC_*` exposes VSEC capability header fields and scratch registers.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs, and TLP prefix logs map Advanced Error Reporting state, masks, severity bits, ECRC controls, first-error pointer, and captured TLP diagnostic data.
- `PCIE_ATS_*` and `PCIE_ARI_*` cover ATS capability/control and ARI capability/control fields.

Because the start line is mid-register, the preceding `VF18_DEVICE_CNTL2` shift definitions and early masks are outside this chunk and must be considered during final merge.

### Complete VF19 and VF20 Blocks

Lines 41864-42558 define the complete `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf19_bifcfgdecp`; lines 42560-43254 define the complete equivalent VF20 block. These two blocks have the same generated structure:

- Basic PCI header registers: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, BARs `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, and latency/grant fields.
- PCIe capability registers: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`.
- PCIe 2+ extended device/link registers: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capability families: MSI capability list/control/address/data/mask/pending plus MSI-X capability list/control/table/PBA fields.
- Vendor-specific capability and scratch fields.
- Advanced Error Reporting families for uncorrectable status, mask, severity, correctable status, correctable mask, AER capability/control, header logs, and TLP prefix logs.
- ATS and ARI enhanced capabilities and control registers.

The fields encode standard enable/status/control surfaces: memory and bus-master enable, interrupt disable, error response/status bits, payload/request size, relaxed ordering, no-snoop, AUX power, phantom functions, link speed/width, ASPM, read completion boundary, retrain/link-disable controls, clock power management, and bandwidth/autonomous status.

### VF21 Front

Lines 43256-43919 start the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf21_bifcfgdecp`. The covered portion includes the same PCI header, PCIe capability, MSI/MSI-X, VSEC, and AER families as VF19/VF20, then reaches `PCIE_ATS_ENH_CAP_LIST` and only the first two shift fields of `PCIE_ATS_CAP`:

- Covered `PCIE_ATS_CAP` fields at the chunk end are `INVALIDATE_Q_DEPTH` and `PAGE_ALIGNED_REQUEST` shifts.
- The `GLOBAL_INVALIDATE_SUPPORTED` shift, all `PCIE_ATS_CAP` masks, `PCIE_ATS_CNTL`, `PCIE_ARI_*`, and the transition to VF22 are in the next chunk.

## Control Flow and State Behavior

There is no executable control flow. These definitions affect the build by making symbolic bit positions available to C code that includes the header. Runtime behavior occurs only in the consuming driver paths that read, mask, shift, set, and write PCIe/NBIO registers.

The represented state is hardware PCI configuration state for SR-IOV virtual functions. Some fields are persistent configuration until reset or reprogramming, including command enables, BAR layout, MSI/MSI-X routing, device/link control, ARI/ATS enablement, AER masks, and error severity policy. Other fields are status or latched diagnostic state, including PCI status bits, link status, error status, MSI pending bits, AER header logs, TLP prefix logs, and AER first-error information.

The header does not express sequencing rules. Correct behavior for control-like fields depends on the owning driver and PCIe spec rules: status bits may be write-1-to-clear, link retraining and compliance bits need ordering and polling, MSI/MSI-X changes must coordinate with interrupt setup, and AER/ATS/ARI settings must match platform capabilities and IOMMU policy.

## Dependencies and Integration Points

This chunk depends on the generated NBIO header set:

- `nbio_2_3_offset.h` provides matching register offsets such as VF19/VF20 MSI masks and AER mask/status offsets.
- `nbio_2_3_default.h` provides reset/default values for the same generated register names.
- `nbio_2_3_sh_mask.h` is included by AMDGPU NBIO and virtualization-related code; observed include sites in this tree include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`.

Integration with driver logic is indirect. The AMDGPU NBIO layer can use these macros to inspect or update NBIO PCIe configuration fields for Navi-era ASICs. SR-IOV and virtual-GPU paths are the most relevant higher-level users because the macros are specifically for endpoint virtual functions. Power-management and reliability paths may also decode link state, error-reporting fields, or vendor-specific capability state when coordinating reset, suspend/resume, FLR, AER handling, or virtualization setup.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can write the wrong PCI configuration bit, causing broken BAR decoding, disabled bus mastering, lost interrupts, malformed MSI/MSI-X setup, bad link control, or hidden PCIe errors.
- The VF blocks are highly repetitive. Mechanical generation errors are easy to miss because VF19, VF20, and VF21 should be structurally identical but occupy different address blocks. A copied prefix, missing field, or swapped mask would compile cleanly and fail only on affected virtual functions.
- AER fields are reliability-sensitive. Incorrect uncorrectable/correctable masks, severity bits, ECRC controls, or status-clear handling can hide real PCIe faults or report false fatal/nonfatal events.
- MSI/MSI-X fields are interrupt-sensitive. Bad address/data/mask/table/PBA fields can break interrupt delivery or leave interrupts enabled during teardown.
- Link control/status fields are timing-sensitive. Misprogramming retrain, disable, compliance, ASPM, common-clock, or target-speed fields can destabilize PCIe links.
- ATS and ARI fields interact with IOMMU, requester IDs, and SR-IOV routing. Enabling or decoding them incorrectly can produce address-translation faults or route transactions to the wrong function.
- Chunk boundaries are partial. The VF18 start and VF21 end cannot be treated as complete register families until adjacent chunk reports are merged.

## Test and Validation Signals

Useful validation is mainly build, hardware, and virtualization coverage:

- Build AMDGPU paths that include `nbio/nbio_2_3_sh_mask.h`; this catches renamed, missing, or syntactically invalid generated macros.
- Exercise NBIO 2.3 device initialization, suspend/resume, reset, and FLR paths on affected ASICs to catch bad command, link, BAR, or capability bit definitions.
- Run SR-IOV virtual-function creation, assignment, reset, and teardown tests that instantiate enough VFs to cover VF18 through VF21.
- Validate MSI and MSI-X delivery for these VFs, including masking/unmasking, pending bits, table/PBA BAR selection, and interrupt teardown.
- Check PCIe link status and retraining flows under normal boot, low-power transitions, and error recovery.
- Inject or observe AER correctable and uncorrectable events where supported, then verify status, mask, severity, header-log, TLP-prefix-log, and clear behavior decode correctly.
- Validate ATS/ARI behavior with an IOMMU-enabled SR-IOV configuration, including requester ID routing and translation-cache enable/disable handling.
- Compare generated masks against hardware XML/register specifications or the corresponding `nbio_2_3_offset.h` and `nbio_2_3_default.h` rows for VF19/VF20/VF21.

## Unresolved Cross-Chunk References

Line 41494 begins inside `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`; the `CPL_TIMEOUT_VALUE`, `CPL_TIMEOUT_DIS`, `ARI_FORWARDING_EN`, `ATOMICOP_REQUEST_EN`, `ATOMICOP_EGRESS_BLOCKING`, `IDO_REQUEST_ENABLE`, and `IDO_COMPLETION_ENABLE` masks plus all shift definitions for that register are in the previous chunk. Line 43919 ends inside `BIF_CFG_DEV0_EPF0_VF21_PCIE_ATS_CAP` after `PAGE_ALIGNED_REQUEST__SHIFT`; the remaining `GLOBAL_INVALIDATE_SUPPORTED` shift, all ATS capability masks, ATS control fields, ARI fields, and the next VF block are in the following chunk. The final per-file merge must join those boundaries before making whole-file claims about VF18 or VF21 completeness.

### subset-b-002922: lines 43920-46353

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 43920-46353

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains C preprocessor constants only: no functions, structs, storage, locks, allocation, persistence, or executable control flow.

The range starts in the tail of the `BIF_CFG_DEV0_EPF0_VF21_PCIE_ATS_CAP` field layout, continues through the last VF21 ATS/ARI capability fields, covers complete `BIF_CFG_DEV0_EPF0_VF22_*`, `BIF_CFG_DEV0_EPF0_VF23_*`, and `BIF_CFG_DEV0_EPF0_VF24_*` virtual-function PCI configuration layouts, and then covers the beginning of `BIF_CFG_DEV0_EPF0_VF25_*` through the first fields of `BIF_CFG_DEV0_EPF0_VF25_DEVICE_CNTL2`. Adjacent chunks are required for the full VF21 ATS capability and the remainder of VF25 extended capability, MSI/MSI-X, AER, ATS, and ARI definitions.

Although this path is under a local `ceph-client` source mirror, the content is AMDGPU hardware metadata for NBIO/NBIF PCIe configuration space. It does not implement Ceph or distributed filesystem behavior.

## Purpose

This header publishes bitfield positions for NBIO 2.3 PCIe configuration registers. Each hardware field is represented by a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for preserving, clearing, setting, or decoding the field.

The matching register address/offset constants live in `nbio_2_3_offset.h`, and reset/default values live in `nbio_2_3_default.h`. Runtime AMDGPU code combines these masks with generated offsets and register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and related NBIO accessors.

## Important Macro Families

The small VF21 tail covers PCIe Address Translation Service and Alternative Routing-ID Interpretation fields. `BIF_CFG_DEV0_EPF0_VF21_PCIE_ATS_CAP` contributes ATS queue/page/global-invalidate capability masks, `PCIE_ATS_CNTL` provides small translation unit and ATC enable fields, and `PCIE_ARI_*` provides enhanced capability list metadata plus ARI next-function/function-group capability and control bits.

The complete VF22, VF23, and VF24 blocks are repeated per-virtual-function PCI configuration images under endpoint function 0. Each block begins with conventional PCI header fields: vendor/device ID, command, status, revision, class code bytes, cache line, latency, header type, BIST, six BARs, CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, and min grant/max latency. The command/status fields include I/O, memory, bus mastering, special cycle, memory write invalidate, parity/SERR behavior, interrupt disable, capability-list presence, parity/system/error status, target/master abort, and DEVSEL timing masks.

The VF22-VF24 PCIe capability sections describe device and link capability/control/status. `DEVICE_CAP` and `DEVICE_CNTL` include max payload support/size, phantom functions, extended tags, relaxed ordering, no-snoop, auxiliary power PM, max read request size, role-based error reporting, captured slot power, and FLR capability/initiation. `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe link speed, width, ASPM/PM support, exit latencies, common clock, retrain/link disable, hardware autonomous width disable, bandwidth-management interrupts, DRS signaling, current negotiated speed/width, link training, slot clock, data-link active, and bandwidth status bits. The PCIe capability v2 registers add completion timeout, ARI forwarding, atomic operation, ID-based ordering, LTR, TPH completer, 10-bit tags, OBFF, end-to-end TLP prefix, emergency power reduction, FRS, supported link speeds, equalization/compliance/de-emphasis, crosslink, RTM presence, and DRS message/status fields.

The MSI and MSI-X capability fields in VF22-VF24 define capability IDs/next pointers and interrupt-programming fields. MSI macros include enable, multiple-message capable/enable, 64-bit capable, per-vector masking capable, address low/high, data, mask, 64-bit data/mask, pending, and 64-bit pending fields. MSI-X macros define table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The vendor-specific and AER capability sections expose extended capability list metadata and error reporting fields. `PCIE_VENDOR_SPECIFIC_*` describes the vendor-specific enhanced capability header and two payload words. `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` identifies the AER extended capability. `PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` define the standard uncorrectable error classes, including data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multi-cast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header log overflow. `PCIE_ADV_ERR_CAP_CNTL` covers first-error pointer, ECRC generation/check capability and enable bits, multi-header received capability/enablement, TLP prefix log presence, and completion timeout log capability.

The AER log macros define four 32-bit TLP header log words and four 32-bit TLP prefix log words for each complete VF block. These fields are diagnostic capture surfaces rather than normal configuration values.

The ATS and ARI sections at the end of each complete VF22-VF24 block repeat enhanced capability list metadata, ATS capability/control, and ARI capability/control. ATS fields describe invalidate queue depth, page-aligned request support, global invalidate support, small translation unit, and ATC enable. ARI fields describe MFVC/ACS function group capability, next function number, corresponding enables, and function group selection.

The VF25 section begins another instance of the same per-VF template. In this chunk, VF25 includes the conventional PCI header, PCIe capability, device/link capability/control/status, `DEVICE_CAP2`, and the first `DEVICE_CNTL2` field definitions through `ATOMICOP_EGRESS_BLOCKING__SHIFT`. The remaining `DEVICE_CNTL2` fields and later VF25 registers are outside this chunk.

## Control Flow

There is no control flow in the header itself. A typical runtime path using these constants is:

1. Driver code chooses the generated offset for a PCI config register from `nbio_2_3_offset.h`.
2. It reads or prepares a 16-bit or 32-bit register value through an AMDGPU PCIe/NBIO access helper.
3. It applies these `__SHIFT` and `_MASK` constants directly or via helper macros to extract, set, clear, or preserve individual fields.
4. It writes the value back, polls status, clears sticky error bits, or records hardware-updated diagnostic fields depending on the register's hardware semantics.

Flows that may use these fields include SR-IOV virtual-function config-space exposure, PCI command/status programming, BAR/resource setup, PCIe link/device capability negotiation, function-level reset, MSI/MSI-X interrupt setup, AER status collection and masking, ATS/PASID/IOMMU-related setup, ARI enumeration, and virtualization feature validation. This chunk only supplies bit layouts; ordering, locking, privilege checks, and hardware sequencing live in AMDGPU/NBIO, PCI, IOMMU, SR-IOV, reset, and interrupt code.

## State And Persistence Behavior

This file has no software state and persists nothing. The macros describe externally visible hardware state in PCI configuration space for SR-IOV-style virtual functions under `BIF_CFG_DEV0_EPF0`.

The represented state includes static identity and capability fields, driver-programmed control bits, host PCI configuration state, hardware-updated link and device status, interrupt address/data/mask/pending registers, AER sticky status and severity/mask configuration, captured AER TLP headers/prefixes, ATS translation-control state, and ARI function-routing state. Some fields are read-only capabilities, some are read/write controls, some are write-one-to-clear error status, and some are command bits with side effects such as FLR initiation or link retraining. The generated macro names and masks do not encode those side-effect rules.

No state survives because of this header. Persistence depends on the GPU's PCI config registers, reset domains, firmware initialization, host PCI core save/restore, and AMDGPU suspend/resume or SR-IOV reset paths. Any driver path using these macros must still follow hardware documentation for reset, sticky status clearing, interrupt masking, and capability programming.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus the AMD generated register database that produced `nbio_2_3_sh_mask.h`. The constants must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which maps the same register names to PCI config-space offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which maps the same register names to default values.
- AMDGPU NBIO, PCIe, SR-IOV, interrupt, reset, and power-management code that includes generated NBIO 2.3 headers.

The closest integration pattern in this tree is AMDGPU code such as `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes generated NBIO default, offset, and shift/mask headers and then reads/writes NBIO and PCIe registers through AMDGPU helper macros. Virtualization-related consumers may also include these definitions through MXGPU/SR-IOV code paths. The field families in this chunk integrate with PCI enumeration, virtual-function config-space emulation/exposure, BAR sizing, MSI/MSI-X delivery, AER reporting, IOMMU/ATS translation behavior, ARI routing, link capability negotiation, and function-level reset behavior.

## Risks And Edge Cases

- The range has artificial chunk boundaries. It begins after the first VF21 ATS capability fields and ends before most of VF25 `DEVICE_CNTL2`; adjacent chunks are needed before making complete-register claims for those registers.
- The constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while changing the wrong hardware bit.
- VF22, VF23, and VF24 are mechanically repeated. A single generation skew in one VF block could create subtle per-VF behavior differences that normal single-VF smoke tests may miss.
- PCI command bits such as memory access and bus mastering are security and DMA sensitive. Incorrect masks can leave a VF unable to DMA or able to access resources unexpectedly.
- FLR, link retrain, link disable, ASPM/clock power management, completion timeout, max payload, max read request, relaxed ordering, and no-snoop fields affect PCIe ordering and liveness. Misprogramming can produce hangs, failed resets, data corruption, or poor interoperability with root complexes.
- MSI/MSI-X fields have direct interrupt-delivery side effects. Width, address, mask, pending, or enable mistakes can cause lost, repeated, or misrouted interrupts.
- AER status and log fields are often sticky or clear-on-write. Treating them like ordinary read/write configuration can erase diagnostic evidence or fail to clear real errors.
- ATS and ARI fields affect IOMMU translation, address caching, and function routing. Incorrect capability or enable handling can break isolation, translation invalidation, or VF enumeration.
- VF25 is incomplete in this chunk; tools that compare repeated VF templates must account for the truncated end rather than reporting a false structural mismatch.

## Test Signals

Useful validation is mostly generated-header, kernel-build, and hardware-integration oriented:

- Build AMDGPU code that includes NBIO 2.3 generated headers; missing, duplicate, or renamed macros should surface as compile errors.
- Compare VF22, VF23, and VF24 field sets after replacing the VF number with a placeholder. They should be structurally identical unless the hardware database intentionally differentiates a VF.
- Compare this shift/mask header against `nbio_2_3_offset.h` and `nbio_2_3_default.h` for matching register-name coverage and expected chunk boundary exceptions.
- Boot affected AMDGPU/NBIO 2.3 hardware and verify PCI config-space enumeration for VF22-VF24: vendor/device IDs, BARs, capability pointers, PCIe capability, MSI/MSI-X, AER, ATS, and ARI capability chains.
- Exercise SR-IOV or multi-function setups with multiple VFs enabled; confirm VF22-VF24 expose consistent capabilities and that VF25 behavior is validated using the following chunk as well.
- Exercise FLR, link retraining, suspend/resume, and PCI error recovery; failures in reset completion, link training, AER logging, or completion timeout paths are strong signals of field-layout drift.
- Exercise MSI/MSI-X interrupt delivery and masking under graphics, compute, reset, and error-injection workloads.
- In IOMMU/ATS-capable configurations, validate translation invalidation and ATC enable/disable paths; stale translations or isolation failures point to ATS field or sequencing problems.

### subset-b-002923: lines 46354-48777

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 46354-48777

## Scope

This chunk is a generated AMD NBIO 2.3 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, allocation, locking, or executable control flow.

The range starts inside `BIF_CFG_DEV0_EPF0_VF25_DEVICE_CNTL2`, after several shift definitions for that register already appeared in the previous chunk. It then finishes the VF25 PCIe capability tail, covers complete PCI configuration-space layouts for virtual functions VF26 and VF27, and covers VF28 from the standard PCI header through `BIF_CFG_DEV0_EPF0_VF28_PCIE_TLP_PREFIX_LOG2`. The chunk ends before the mask for VF28 TLP prefix log 2 and before VF28 TLP prefix log 3, ATS, and ARI fields; those are in the following chunk.

Although the repository prefix is `sources/distributed-fs/ceph-client`, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIO 2.3 PCIe virtual-function configuration images. Each register field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when encoding or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The companion address metadata is in `nbio_2_3_offset.h`, where this same virtual-function range maps to config offsets such as `cfgBIF_CFG_DEV0_EPF0_VF25_0_DEVICE_CNTL2`, `cfgBIF_CFG_DEV0_EPF0_VF26_0_VENDOR_ID`, `cfgBIF_CFG_DEV0_EPF0_VF27_0_PCIE_UNCORR_ERR_STATUS`, and `cfgBIF_CFG_DEV0_EPF0_VF28_0_PCIE_TLP_PREFIX_LOG2`. Runtime code combines offset symbols with these field masks through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The VF25 portion completes the second-generation PCIe device/link capability tail. It includes `DEVICE_CNTL2` control bits for completion timeout, ARI forwarding, atomic operation requests, ID-based ordering, LTR, emergency power reduction, 10-bit tags, OBFF, and TLP-prefix blocking. It then defines VF25 status/control fields for `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, covering supported/target link speed, crosslink and SKP ordered-set support, equalization phases, retimer presence, compliance controls, downstream component presence, and DRS message state.

VF25 also includes MSI and MSI-X capability fields: capability IDs, next pointers, MSI enable/multiple-message/64-bit/per-vector masking state, MSI address/data/mask/pending registers, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset. The vendor-specific enhanced capability follows with VSEC capability ID/version/next pointer, VSEC ID/revision/length, and two scratch payload registers.

The VF25 AER section defines advanced error reporting capability header fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control bits, four TLP header log registers, and TLP prefix logs. Error fields include data-link protocol, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, AtomicOp egress blocked, and TLP-prefix blocked state. Correctable fields include receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal, and header-log overflow state. VF25 ends with ATS and ARI enhanced capabilities, including ATS page-size granularity/enable fields and ARI next-function/function-group controls.

The VF26 and VF27 blocks are complete and mechanically parallel. Each begins with standard PCI configuration header fields: vendor/device ID, command, status, revision/class-code bytes, cache-line/latency/header/BIST fields, BAR1 through BAR6, CardBus CIS pointer, adapter ID/subsystem IDs, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. The command and status masks cover I/O, memory, bus master, special cycles, memory-write-invalidate, VGA snoop, parity/error response, SERR, fast back-to-back, interrupt disable, capability-list presence, 66 MHz, user-definable feature, fast back-to-back, master abort/target abort, parity, and detected parity state.

The complete VF26/VF27 PCIe capability groups include PCIe capability list/capability headers, device capability/control/status, link capability/control/status, device capability 2/control 2/status 2, and link capability 2/control 2/status 2. These describe payload size, phantom functions, extended tags, acceptable L0s/L1 latency, attention/power indicators, role-based error reporting, FLR, max payload/read request, relaxed ordering, no-snoop, auxiliary power, unsupported request, link speed/width, ASPM, RCB, common clock, extended sync, link disable/retrain, clock power management, link bandwidth notification, completion timeout ranges, atomic operations, OBFF, LTR, 10-bit tags, equalization phases, compliance controls, retimer presence, crosslink state, and DRS status.

The complete VF26/VF27 interrupt, vendor, AER, ATS, and ARI groups mirror the VF25 tail. They define MSI/MSI-X capability registers, vendor-specific enhanced capability header/payload fields, AER status/mask/severity/control/log fields, ATS enhanced capability/capability/control fields, and ARI enhanced capability/capability/control fields.

The VF28 block is complete from `VENDOR_ID` through the start of AER TLP-prefix logging. It carries the same standard PCI header, PCIe capability, MSI/MSI-X, vendor-specific, and AER register families as VF26/VF27, but this chunk stops immediately after `BIF_CFG_DEV0_EPF0_VF28_PCIE_TLP_PREFIX_LOG2__TLP_PREFIX__SHIFT`. The rest of VF28 TLP prefix logging and the VF28 ATS/ARI tail are outside this chunk.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing is supplied by AMDGPU NBIO, PCIe, SR-IOV, interrupt, reset, and power-management code that includes it:

1. Driver code selects a register offset from `nbio_2_3_offset.h` or an SMN/MMIO constant.
2. It reads or constructs a 16-bit or 32-bit PCI config-space value with PCIe or SOC15 access helpers.
3. It uses these `__SHIFT` and `_MASK` constants directly or through helper macros to update or decode a field.
4. It writes the value back, polls status, clears sticky status, reports capability state, or lets hardware/firmware update status-owned fields.

For this chunk, common runtime flows include SR-IOV virtual function config image exposure, PCIe capability enumeration, VF interrupt capability setup, AER status collection and clearing, link control/status reporting, function reset coordination, ATS/ARI virtualization setup, and guest-visible capability/status emulation or passthrough.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes GPU-owned PCI configuration and enhanced-capability state for virtual functions.

The represented state includes PCI command/status bits, identity/class/header fields, BAR and ROM aperture fields, capability pointers, PCIe device/link capability and control bits, MSI/MSI-X programming state, vendor-specific VSEC payload scratch registers, AER status/mask/severity and logs, ATS translation controls, and ARI next-function/function-group controls. Some fields are static capability descriptions, some are host or guest programmed controls, some are hardware-updated status, and some are sticky error/log fields with clear-on-write behavior. The generated constants do not encode those side effects; consumers must follow PCIe and ASIC-specific semantics.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`. The offset header provides the config-space addresses for VF25 through VF28, while this file provides the bit layouts for values stored at those addresses.

Direct AMDGPU include users of `nbio_2_3_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`. Those files rely on generated masks for NBIO programming, SR-IOV/MXGPU behavior, and power-management interactions rather than duplicating bit positions.

The virtual-function PCI config macros integrate with Linux PCI enumeration, SR-IOV VF creation and teardown, guest passthrough or mediated access paths, function-level reset, interrupt delivery, AER error handling, PCIe link management, ATS address-translation services, and ARI routing/function-number expansion. The standardized field names also make this ASIC revision comparable with other generated AMD register headers.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first line is mid-`DEVICE_CNTL2` for VF25, and the last line is mid-`PCIE_TLP_PREFIX_LOG2` for VF28. Adjacent chunks are needed for complete whole-register analysis at those boundaries.
- These macros are untyped integer constants. Wrong masks or shifts can compile cleanly while targeting the wrong hardware bit.
- VF26 and VF27 are highly repetitive, and VF28 largely repeats them. Copy-generation drift can produce off-by-one VF naming, wrong register prefixes, or mismatched offset/mask pairs that are difficult to notice in review.
- PCIe command, BAR, bus mastering, memory enable, interrupt disable, and ROM base fields are enumeration-sensitive. Bad field definitions can break VF discovery, resource assignment, DMA enablement, or interrupt routing.
- PCIe link, payload, read-request, ordering, no-snoop, completion timeout, atomic operation, LTR, OBFF, and TLP-prefix controls affect host/device interoperability. Incorrect values can cause link instability, ordering violations, timeouts, or performance regressions.
- MSI/MSI-X address, data, mask, pending, table, and PBA fields have interrupt-delivery side effects. Width, alignment, or aliasing mistakes can cause lost, misrouted, masked, or unexpectedly unmasked interrupts.
- AER status and log fields may be sticky or write-one-to-clear. Treating them like ordinary retained configuration can erase diagnostic evidence or leave error state uncleared.
- ATS and ARI controls affect address translation and VF routing/isolation. Wrong masks can expose invalid translation enablement, stale ATC state, or incorrect function-group behavior in SR-IOV environments.
- Some fields represent guest-visible PCI config state. In SR-IOV or virtualization, incorrect exposure can create compatibility failures that are only visible with VFs enabled and guest drivers loaded.

## Test Signals

Useful validation is mostly build, boot, PCIe, and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 support enabled; missing or renamed macros should fail in NBIO, MXGPU, SMU, PCIe, or interrupt code.
- Boot affected ASICs and confirm Linux PCI enumeration shows stable VF vendor/device IDs, class codes, BARs, capability pointers, PCIe capabilities, MSI/MSI-X capabilities, vendor-specific capability, AER capability, ATS capability, and ARI capability.
- Enable SR-IOV with enough VFs to cover VF25 through VF28; inspect `lspci -vv` output for those VFs and compare capability offsets and decoded fields against expected hardware documentation.
- Exercise VF MSI and MSI-X interrupt delivery under graphics, compute, reset, and guest passthrough workloads; lost interrupts or stuck pending/mask state indicate mask/offset problems.
- Trigger or inject PCIe/AER paths where available and verify uncorrectable/correctable status, severity, masks, header logs, and TLP prefix logs are reported and cleared correctly.
- Test VF FLR, suspend/resume, runtime reset, link retraining, and error recovery paths; hangs, failed enumeration, or unexpected link-speed/width changes can reveal incorrect PCIe control/status fields.
- In virtualization runs, validate ATS/ARI behavior and isolation with guest drivers loaded, including DMA translation, function routing, and teardown/recreate cycles for high-numbered VFs.

### subset-b-002924: lines 48778-51444

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 48778-51444

## Scope

This chunk covers generated AMD NBIO 2.3 shift/mask macros. It is data-only C preprocessor material: no functions, structs, variables, allocation, locking, persistence code, or executable control flow live here.

The range starts near the end of the `BIF_CFG_DEV0_EPF0_VF28` PCIe capability block, beginning with `PCIE_TLP_PREFIX_LOG3` and continuing through VF28 ATS and ARI fields. It then covers complete PCI/PCIe configuration-space bitfields for SR-IOV virtual functions `VF29` and `VF30`. The final address block starts `nbio_nbif0_pciemsix_0_usb_MSIXTDEC` and defines MSI-X table entry fields from vector 0 through `PCIEMSIX_VECT102_ADDR_LO`; the range ends on the `PCIEMSIX_VECT102_ADDR_HI` register comment before that register's shift/mask fields.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware register metadata, not Ceph or distributed filesystem code.

## Purpose

The purpose of this header section is to publish the bit-level ABI for NBIO 2.3 PCIe configuration and MSI-X table registers. Each generated field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve the field in a 16-bit or 32-bit register value.

The companion `nbio_2_3_offset.h` header supplies register addresses and base indices. Runtime AMDGPU code combines offsets with these macros through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

## Important Macro Families

### VF28 Capability Tail

The opening lines continue the previous chunk's `BIF_CFG_DEV0_EPF0_VF28` configuration-space description. The covered fields are the tail of Advanced Error Reporting and extended capability state:

- `PCIE_TLP_PREFIX_LOG3`, carrying a full-width TLP prefix log word.
- `PCIE_ATS_ENH_CAP_LIST`, with capability ID, capability version, and next-pointer fields.
- `PCIE_ATS_CAP`, with invalidate queue depth, page-aligned request, and global invalidate support fields.
- `PCIE_ATS_CNTL`, with smallest translation unit and ATC enable fields.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, covering ARI enhanced capability linkage, function group capability, next function number, function group enables, and function group selection.

Because this chunk starts after most of VF28, it should be reconciled with the preceding chunk before making a complete VF28 statement.

### VF29 and VF30 PCI Configuration Space

The `nbio_nbif0_bif_cfg_dev0_epf0_vf29_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf0_vf30_bifcfgdecp` address blocks are structurally parallel. They expose generated bitfields for a virtual PCIe endpoint function:

- Standard PCI header fields: vendor/device IDs, command, status, revision, programming interface, subclass, base class, cache line size, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list linkage, PCIe capability metadata, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- MSI capability fields: MSI capability list linkage, message control, message address low/high, message data, mask, pending, and 64-bit variants.
- MSI-X capability fields: MSI-X capability list linkage, message control, table location/BIR, and pending bit array location/BIR.
- Vendor-specific enhanced capability fields: enhanced capability list metadata, vendor-specific header, and two vendor-specific payload registers.
- Advanced Error Reporting fields: AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ATS and ARI enhanced capability fields: capability list linkage, ATS capability/control, ARI capability/control, and related function group/next-function metadata.

The field names mirror PCIe-defined concepts closely. Examples include command bits for I/O, memory, bus mastering, SERR, and interrupt disable; device control bits for correctable/nonfatal/fatal/unsupported-request reporting, relaxed ordering, max payload, extended tag, phantom functions, aux power PM, no-snoop, max read request, bridge configuration retry, and FLR initiation; link fields for speed, width, ASPM, retrain, common clock, extended sync, hardware autonomous width disable, link bandwidth management interrupt, and automatic bandwidth interrupt; and Device/Link 2 fields for completion timeout, atomic operation support/control, LTR, OBFF, target link speed, equalization, selectable de-emphasis, and current de-emphasis.

The AER uncorrectable status/mask/severity families cover data link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked status. Correctable error fields cover receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, correctable internal error, and header log overflow.

### MSI-X Table Vector Fields

The `nbio_nbif0_pciemsix_0_usb_MSIXTDEC` block defines repeated MSI-X table entries. For each complete vector entry in this chunk, four logical registers are present:

- `PCIEMSIX_VECTn_ADDR_LO`, with `MSG_ADDR_LO` shifted by 2 and masked as `0xFFFFFFFC`, preserving the PCI MSI-X requirement that message addresses are naturally aligned.
- `PCIEMSIX_VECTn_ADDR_HI`, with a full-width high message-address field.
- `PCIEMSIX_VECTn_MSG_DATA`, with a full-width message-data field.
- `PCIEMSIX_VECTn_CONTROL`, with bit 0 as `MASK_BIT`.

The covered complete entries are vectors 0 through 101. The chunk includes `PCIEMSIX_VECT102_ADDR_LO` and the comment for `PCIEMSIX_VECT102_ADDR_HI`, but not the shift/mask definitions for `VECT102_ADDR_HI`, `VECT102_MSG_DATA`, or `VECT102_CONTROL`. Adjacent chunks must be merged to describe the full MSI-X table.

## Control Flow

There is no runtime control flow in this header. The operational flow belongs to AMDGPU NBIO, PCIe, interrupt, SR-IOV, and power-management code that includes the generated header:

1. Code selects a register address from `nbio_2_3_offset.h` or another generated offset header.
2. It reads or prepares a 16-bit or 32-bit register/config-space value through SOC15, PCIe, or KIQ-safe access helpers.
3. It uses the `__SHIFT` and `_MASK` constants, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to update or decode a specific field.
4. It writes the value back, polls hardware status, or records decoded state according to the owning PCIe/NBIO/MSI-X programming sequence.

Direct include sites in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`, and DCN resource files that include the NBIO 2.3 offset namespace. The chunk itself does not decide policy or sequencing.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration, capability, error-reporting, address translation, ARI, and MSI-X state whose lifetime is controlled by PCIe enumeration, driver initialization, guest/PF/VF ownership, FLR, hot reset, suspend/resume, runtime power management, interrupt setup, and hardware error handling.

The VF29/VF30 state represented here includes PCI command/status bits, BAR and ROM address fields, capability-chain pointers, MSI/MSI-X configuration, PCIe device/link negotiated state, AER error status/mask/severity/logs, ATS enablement and translation granularity, and ARI function grouping. Some fields are configuration that remains until reset or reprogramming; others are hardware-owned status, sticky error state, self-clearing command bits, write-one-to-clear bits, or fields owned by host/guest PCI configuration mechanisms. The header names the bits but does not encode access permissions, reset defaults, side effects, ordering, locking, or timeout rules.

The MSI-X table state is interrupt delivery state. Address and data fields are programmed by PCI/MSI-X setup paths, and each vector control field's `MASK_BIT` gates delivery for that vector. Incorrect handling can expose vectors before address/data are valid, leave interrupts masked, or deliver to the wrong CPU interrupt target.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register set staying synchronized:

- `nbio_2_3_offset.h` supplies matching offsets and base indices.
- `nbio_2_3_default.h` supplies reset/default values for related NBIO registers and VF PCI configuration images.
- AMDGPU helper macros consume the generated shift/mask names for typed-looking but preprocessor-only register composition.

The integration surface is AMDGPU's NBIO/BIF layer, SR-IOV PF/VF support, PCIe capability handling, MSI/MSI-X interrupt setup, AER/error-reporting paths, ATS/IOMMU-related enablement, ARI virtualization/function enumeration, and power-management code that reasons about NBIO/PCIe state. Generic Linux PCI code manages the architectural meaning of many of these fields, while AMDGPU uses these generated definitions for GPU-internal register/config-space access.

The MSI-X table fields are also an integration point with interrupt remapping and vector allocation. Address low/high, data, and per-vector mask bits must match PCI MSI-X semantics and the table layout supplied by the matching offset header.

## Risks And Edge Cases

- The assigned range has artificial boundaries. It starts mid-VF28 capability tail and ends mid-MSI-X-vector family at `PCIEMSIX_VECT102_ADDR_HI`; final per-file analysis must join adjacent chunks.
- These are untyped preprocessor constants. A stale mask, wrong shift, typo in a repeated VF name, or use with the wrong offset can compile cleanly while programming the wrong hardware bits.
- VF29 and VF30 are highly repetitive. A one-off mechanical error can affect only one VF's PCI command/status, BAR, MSI, AER, ATS, or ARI behavior and remain hidden unless high-numbered VFs are enumerated and exercised.
- PCIe command, device control, link control, and Device/Link 2 fields are protocol-sensitive. Incorrect masks can break enumeration, bus mastering, memory decoding, max payload/read request programming, FLR, completion timeout policy, ASPM, LTR, OBFF, target link speed, retraining, or equalization state handling.
- AER status/mask/severity fields may be sticky, write-one-to-clear, or hardware-owned. Incorrect use can hide real errors, create interrupt storms, clear forensic logs too early, or misclassify fatal versus nonfatal conditions.
- ATS and ARI fields affect address translation and function enumeration. Incorrect ATC enable/STU, invalidate capability, ARI next-function, or function-group fields can cause DMA translation faults, stale translations, or broken VF discovery/isolation.
- MSI/MSI-X fields are interrupt-delivery-sensitive. Programming address/data/mask fields out of sequence can lose interrupts, deliver them to the wrong target, or unmask vectors before the table entry is valid.
- The MSI-X table has many identical vector entries. Off-by-one vector addressing or copying the wrong vector number can affect a single interrupt source and be difficult to correlate with the generated macro error.

## Test And Validation Signals

Useful validation is mostly build, PCIe integration, interrupt, and SR-IOV hardware coverage:

- Build AMDGPU code that includes `nbio/nbio_2_3_sh_mask.h`; missing or renamed macros should fail in NBIO, SMU11, display, and virtualization consumers.
- Enumerate SR-IOV configurations that expose high-numbered VFs, especially VF29 and VF30, and verify PCI vendor/device IDs, class codes, BARs, capability-chain pointers, MSI/MSI-X capabilities, AER, ATS, and ARI visibility.
- Exercise guest VF bind/unbind, FLR, hot reset, suspend/resume, and bus-master/memory-enable transitions while checking that command/status and capability fields behave as expected.
- Run MSI and MSI-X interrupt tests with multiple vectors, including mask/unmask and pending-bit behavior, to catch table address/data/control regressions and vector-index mistakes.
- Run PCIe link-management tests across retrain, ASPM policy changes, payload/read-request changes, completion-timeout settings, LTR/OBFF paths, and error recovery.
- Use AER injection or platform diagnostics where available to confirm uncorrectable/correctable status, mask, severity, header log, and TLP prefix log behavior.
- Exercise ATS/IOMMU paths for VFs with address translation enabled, including invalidation and reset paths, to detect incorrect STU, ATC enable, or invalidate capability interpretation.
- In virtualization test matrices, validate ARI enumeration/function grouping and isolation for high-numbered VFs so VF29/VF30-specific macro drift is visible.

## Unresolved Cross-Chunk References

The first register family, `BIF_CFG_DEV0_EPF0_VF28_PCIE_TLP_PREFIX_LOG3`, began in the previous chunk with earlier VF28 PCIe/AER fields. The final MSI-X family continues after line 51444 with `PCIEMSIX_VECT102_ADDR_HI` field definitions and later vector entries. The merge/reconciliation lane should stitch those boundaries before producing the final `nbio_2_3_sh_mask.h` report.

### subset-b-002925: lines 51445-54195

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 51445-54195

## Scope

This chunk covers a generated AMD NBIO 2.3 shift/mask header section. It starts in the middle of the `PCIEMSIX_VECT102_ADDR_HI` definitions, continues through the rest of the MSI-X vector table entries for vectors 102 through 255, covers the `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` pending-bit-array masks, and then enters `addressBlock: nbio_pcie0_pswusp0_pciedir_p`.

The PCIe portion covers port control, transmit and receive control, flow-control credits, error control and error injection, SR-IOV private control, NAK counters, link-control/training/link-width/speed state, link-management status, bandwidth-change status, clock/data recovery controls, lane corruption status, and PCIe link equalization controls through the first four `PCIE_LC_CNTL5` mask definitions. The range ends mid-register in `PCIE_LC_CNTL5`; the remaining masks for that register and later PCIe link-control registers are in the next chunk.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or runtime MMIO access. Its exported convention is:

- `<REGISTER>__<FIELD>__SHIFT` for bit offsets.
- `<REGISTER>__<FIELD>_MASK` for 32-bit field masks.

## Purpose

This header is the bitfield side of the NBIO 2.3 register ABI used by AMDGPU and SMU/power-management code. The companion `nbio_2_3_offset.h` header supplies the register addresses and base indices; this file supplies the field positions and masks used to compose and decode register values with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15`.

The two major hardware surfaces in this chunk are MSI-X interrupt-table state and PCIe link/port state. MSI-X definitions describe per-vector message address, message data, and mask bits. PCIe definitions describe how software reads link width/speed, manages ASPM and low-power transitions, tracks link-training state, handles flow-control credits, injects or masks errors, and controls equalization or recovery behavior.

## Important Macro Families

### MSI-X Vector Table and Pending Bit Array

The first part continues the `nbio_nbif0_pciemsix_0_usb_MSIXTBLDEC` table:

- `PCIEMSIX_VECT102_ADDR_HI` starts this chunk at the high address portion of vector 102.
- `PCIEMSIX_VECT102_MSG_DATA` and `PCIEMSIX_VECT102_CONTROL` finish vector 102.
- `PCIEMSIX_VECT103_*` through `PCIEMSIX_VECT255_*` provide the regular four-register pattern for each vector: `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL`.

The field layouts are uniform: low message address fields start at bit 2 with `0xFFFFFFFC`, high address and message data fields are full-width `0xFFFFFFFF`, and control exposes bit 0 as `MASK_BIT`. This is the software-visible MSI-X vector table programming model: each vector carries a message address, message data payload, and a per-vector mask.

`PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` then expose full-width `MSIX_PENDING_BITS` masks. Together these eight 32-bit registers cover the pending state for 256 MSI-X vectors.

### PCIe Port, Transmit Path, and Flow-Control Credits

The `nbio_pcie0_pswusp0_pciedir_p` block begins with basic port registers:

- `PCIEP_RESERVED` and `PCIEP_SCRATCH` are full-width placeholder/scratch fields.
- `PCIEP_PORT_CNTL` controls slave-port request enablement, snoop override, hotplug messages, native PME, power-fault handling, bus-mastering PMI behavior, completion allocation limits, private completion payload sizing, poisoned/UR response mode, and completion-payload mode.

Transmit-side registers include:

- `PCIE_TX_CNTL` for relaxed-ordering/non-snoop overrides, packet packing, TLP flush behavior, posted-pass behavior for CPL/NP traffic, extra PM request cleanup, flow-control update timeout disable, TPH disable per function, and RTRC/BFRC swapping.
- `PCIE_TX_REQUESTER_ID` for function/device/bus requester ID fields.
- `PCIE_TX_VENDOR_SPECIFIC` and `PCIE_TX_NOP_DLLP` for vendor and NOP DLLP data plus send strobes.
- `PCIE_TX_REQUEST_NUM_CNTL` for outstanding NP request limits and enable bits.
- `PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, and `PCIE_TX_ACK_LATENCY_LIMIT` for sequence-number tracking, replay count/timer override, and ACK latency override.
- `PCIE_TX_CNTL_2` for skid credit limit override.

The transmit credit definitions separate advertised, initialized, current/error, and flow-control-update threshold state:

- `PCIE_TX_CREDITS_ADVT_P/NP/CPL` and `PCIE_TX_CREDITS_INIT_P/NP/CPL` define header/data credit fields for posted, non-posted, and completion traffic.
- `PCIE_TX_CREDITS_STATUS` exposes error and current-status bits for all six credit categories.
- `PCIE_TX_CREDITS_FCU_THRESHOLD` defines per-VC threshold fields for posted, non-posted, and completion flow-control updates.

`PCIE_FC_P`, `PCIE_FC_NP`, `PCIE_FC_CPL`, and their `_VC1` variants describe advertised flow-control credit state for VC0 and VC1.

### Receive Path, Error Control, Error Injection, and SR-IOV

`PSWUSP0_PCIE_ERR_CNTL` controls error reporting, ECRC dropping, generated LCRC/ECRC errors, AER header-log timeout and expiry status, slave-buffer halt status/reset, immediate error messages, poisoned advisory behavior, and private AER masks for bad DLLP/TLP.

`PSWUSP0_PCIE_RX_CNTL` is a dense receive-policy register. It can ignore or mask IO, BE, message, CRC, config, completion, poisoned, length mismatch, max payload, traffic class, unsupported request, address translation, prefix, PASID, and CTO-related errors. It also controls NAK generation, RX flow-control initialization from registers, RCB completion timeout behavior, TPH disable, and FLR timeout disable.

`PCIE_RX_CNTL3` adds root-complex/PASID-related unsupported-request ignore bits. `PCIE_RX_EXPECTED_SEQNUM` and `PCIE_RX_VENDOR_SPECIFIC` expose receive sequence/vendor state. `PCIE_RX_CREDITS_ALLOCATED_P/NP/CPL` define allocated receive data/header credits for posted, non-posted, and completion traffic.

The physical and transaction error-injection registers are explicit test/debug surfaces:

- `PCIEP_ERROR_INJECT_PHYSICAL` covers lane, framing, SKP parity/LFSR, loopback underflow/overflow, deskew, 8b/10b disparity/decode, SKP ordered-set, invalid ordered-set identifier, and bad sync-header injection fields.
- `PCIEP_ERROR_INJECT_TRANSACTION` covers flow-control, replay rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout injection fields.

`PCIEP_SRIOV_PRIV_CTRL` defines VF mapping mode and VF-save behavior when VF enable is cleared. `PCIEP_NAK_COUNTER` exposes 16-bit counters for NAKs received and generated by the port.

### Link Control, Training, Width, Speed, and State History

The `PCIE_LC_*` families describe the link controller and are the most directly integrated with power-management and link-management paths:

- `PCIE_LC_CNTL` controls entry into L2/L3 from D0, link reset, x16 TX pipe clearing, L0s/L1 inactivity timers, PMI-to-L1 behavior, idle detection, wake from L2/L3, ASPM-to-L1 disable, L0s/L1 exit delays, L1/L23 escape, and receiver idle gating.
- `PCIE_LC_TRAINING_CNTL` covers training mode, compliance receive, L0s/L1 training enable, power state, CSR-initiated speed change, training-bit behavior, hot-reset quick exit, autonomous change/upconfigure disablement, hardware link-disable state, ASPM L1 NAK timer selection/reset, receiver enable behavior during speed/test states, and equalization timing extension.
- `PCIE_LC_LINK_WIDTH_CNTL` has requested and read-back link width fields, reconfiguration support/control, renegotiation enable, upconfigure support/disable, dynamic lane power state, reversal/equalization helpers, idle/electrical-idle waits, unused-lane shutdown, and RX standby bypass.
- `PCIE_LC_N_FTS_CNTL` controls transmitted FTS counts, override, pre-recovery FTS, EIE selection, 8GT/16GT behavior, FTS limit, and received/negotiated FTS count.
- `PSWUSP0_PCIE_LC_SPEED_CNTL` defines Gen2/Gen3/Gen4 enable straps, target speed override, forced software/hardware speed-change enable/disable, speed-change initiation, allowed attempts, failure/current data-rate status, failed-count clear, peer Gen2/Gen3/Gen4 support/ever-sent indicators, advertised rate, data-rate checking, and speed negotiation from L0s/L1.
- `PCIE_LC_STATE0` through `PCIE_LC_STATE5` expose the current link-controller state plus a rolling history of 23 previous states, six bits per state slot.

`PCIE_LINK_MANAGEMENT_CNTL2` reports quiesce and equalization request send/receive state and defines bandwidth hint mode plus low/high bandwidth thresholds for Gen2, Gen3, and Gen4. `PSWUSP0_PCIE_LC_CNTL2` exposes timed-out/illegal-state status, bandwidth-reduction behavior, TS2 behavior, x12 negotiation disable, link-up reversal, electrical-idle behavior, L1/L23 powerdown permission, lost-symbol-lock behavior, bandwidth notification disable, PMI L1 slave-idle wait, test timer selection, and inferred electrical idle control.

`PCIE_LC_BW_CHANGE_CNTL` provides bandwidth-change interrupt enable and status causes for hardware, software, other, reliability, failed speed negotiation, long/short link-width changes, other/failed link-width changes, notification detect mode, and unsuccessful speed negotiation.

### Equalization, CDR, Lane Status, and Partial CNTL5

The late-link portion includes:

- `PCIE_LC_CDR_CNTL` for CDR test offset, test sets, and set type.
- `PCIE_LC_LANE_CNTL` for a 16-bit corrupted-lane bitmap.
- `PCIE_LC_CNTL3` for de-emphasis selection, received de-emphasis, detect completion, TS counter reset in recovery lock, automatic speed-change attempts/failure/clear, enhanced hotplug, receiver-detect override, link-down speed-change enable, L1 reconfiguration block, automatic speed-support disablement, fast L1 entry/exit, P0 powerdown/refclkack wait, `LC_DSC_DONT_ENTER_L23_AFTER_PME_ACK`, hardware voltage interface, recovery trigger, and automatic recovery disable.
- `PCIE_LC_CNTL4` for TX-enable behavior, ASPM L1 disable during speed changes, Gen3/8GT equalization bypass/redo/search behavior, quiesce set/received state, forced presets and coefficients in EQ request phase, TX swing, wait-for-evaluation-done, skip ordering, and recovery-lock TS wait count.
- `PCIE_LC_CNTL5` begins local equalization settings with rate, preset, pre-cursor, and cursor fields. The chunk stops before the rest of `PCIE_LC_CNTL5` is fully documented in-source.

## Control Flow and State Behavior

There is no executable control flow in this header. Its effect is compile-time: C code includes the header and uses these constants to produce or decode exact 32-bit MMIO bit patterns for NBIO 2.3 hardware.

The represented state is persistent hardware register state, not software-owned storage in this file. MSI-X vector entries persist message address/data/mask configuration and pending bits until programmed or cleared through the PCI/MSI-X path. PCIe port and link registers persist link policy, link-training state, flow-control credit state, error policy, SR-IOV behavior, and debug/error-injection settings across the hardware lifetime defined by reset, power-gating, suspend/resume, and firmware/driver reinitialization.

Several fields are status, sticky status, or command-like strobes rather than ordinary configuration. Examples include MSI-X pending bits, vendor/NOP send bits, generated error controls, slave-buffer halt reset, NAK generation, link reset, reconfiguration-now, initiate-link-speed-change, failed-speed-change clear, bandwidth-change cause bits, quiesce set/received, `LC_GO_TO_RECOVERY`, and error-injection fields. Correct users must follow ordering, polling, timeout, and clear semantics from the AMDGPU code and hardware specification; the masks alone do not express those rules.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 header set:

- `nbio_2_3_offset.h` supplies matching register addresses and base indices.
- `nbio_2_3_default.h` supplies generated defaults where available.
- AMDGPU register helper macros consume the `__SHIFT`/`_MASK` convention for field composition and extraction.

Observed integration in this source tree includes:

- `amdgpu/nbio_v2_3.c` includes `nbio_2_3_offset.h`, `nbio_2_3_default.h`, and this mask header. Its ASPM programming path uses `PCIE_LC_CNTL`, `PCIE_LC_CNTL3`, `PSWUSP0_PCIE_LC_CNTL2`, and `PCIE_LC_LINK_WIDTH_CNTL` masks to disable/restore L0s/L1 timers, prevent L2/L3 entry during PME-ack handling, allow L1/L23 powerdown, and read link width.
- `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c` include the NBIO 2.3 mask header alongside SMU tables, so SMU power-management code can share generated NBIO field definitions.
- `amdgpu/mxgpu_nv.c` includes this header in SR-IOV/MxGPU support, matching the presence of `PCIEP_SRIOV_PRIV_CTRL` and MSI-X/PCIe virtualization-sensitive register state in the chunk.
- Older and related generation code (`cik.c`, `vi.c`, and Vega powerplay hwmgr files) uses the same PCIe link-control field families to read current link speed/width, initiate speed changes, quiesce/re-equalize links, enter recovery, and tune ASPM. This shows the expected usage pattern for the NBIO 2.3 macros even when the exact include file differs by ASIC generation.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write the wrong PCIe control bit, causing link retraining failures, lost interrupts, incorrect power-state behavior, or GPU hangs.
- MSI-X vector definitions are extremely repetitive and mechanically fragile. Off-by-one vector numbering or wrong `MASK_BIT`/message-address masks can route interrupts to the wrong vector, leave interrupts masked, or corrupt the pending-bit mapping.
- PCIe link-control fields affect live bus connectivity. Incorrect use of link reset, speed-change initiation, reconfiguration, quiesce, recovery, dynamic lane power state, or equalization controls can drop the link or leave the GPU unreachable until reset.
- ASPM and L1/L23 powerdown bits are platform-sensitive. Values that work on one board or bridge can regress hotplug, Thunderbolt/removable devices, resume, or idle power on another.
- Error masking and error-injection fields are reliability-sensitive. Accidentally enabling injection, suppressing AER/ECRC/PASID errors, or clearing/ignoring completion timeout behavior can hide real PCIe faults or create false fault reports.
- Flow-control credit masks describe protocol-level resources. Bad advertised/allocated credit values can deadlock traffic, create replay storms, or produce misleading credit-error status.
- SR-IOV private controls and MSI-X state are virtualization-sensitive. Incorrect PF/VF mapping or interrupt masking can break VF isolation, event delivery, or guest-driver behavior.
- The chunk boundary is mid-family: it starts after `PCIEMSIX_VECT102_ADDR_LO` and ends before all of `PCIE_LC_CNTL5` is present. The final per-file merge must reconcile those boundaries before making complete source-file claims.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and link-state testing:

- Build AMDGPU, SMU11, and MxGPU/SR-IOV code that includes `nbio/nbio_2_3_sh_mask.h`; this catches missing or renamed generated macros.
- Boot Navi/NBIO 2.3 hardware through `nbio_v2_3.c` and verify ASPM programming does not regress suspend/resume, hotplug/removable-device behavior, or idle power.
- Read current PCIe link width and speed through power-management paths and compare against `lspci` link status and expected platform capabilities.
- Exercise link retraining and recovery paths where available, checking that `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_GO_TO_RECOVERY`, bandwidth-change status, and state-history fields converge without timeouts.
- Validate MSI-X interrupt delivery across high vector numbers, especially vectors above 102, and verify per-vector masking plus PBA pending bits behave as expected.
- Run PCIe AER/RAS diagnostics or controlled error-injection tests only in a suitable lab environment, confirming injected physical/transaction errors surface through expected AER/status paths and are not left enabled.
- For SR-IOV, create/destroy VFs and verify VF MSI-X delivery, VF mapping state, and PF/VF isolation remain correct across VF enable/disable and reset.

## Unresolved Cross-Chunk References

Line 51445 is the tail of the `PCIEMSIX_VECT102_ADDR_HI` register; the matching `PCIEMSIX_VECT102_ADDR_LO` definition belongs to the previous chunk. Line 54195 ends after `PCIE_LC_CNTL5__LC_LOCAL_CURSOR_MASK`; later `PCIE_LC_CNTL5` fields such as local post-cursor, RX standby, safe recovery, preset acceptance, detect wait, and hold-training masks continue in the next chunk. The merge lane should stitch these partial register families together.

### subset-b-002926: lines 54196-56612

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 54196-56612

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register field shift/mask header slice. It contains preprocessor constants only: no functions, structs, variables, locking, allocation, persistence code, or executable control flow.

The assigned range starts in the mask half of `PCIE_LC_CNTL5`, then covers PCIe link-controller equalization, link management, straps, L1 PM substates, save/restore, the `nbio_pcie0_pciedir` address block, PRBS diagnostics, software reset controls, clock/power-management controls, receive margining, presence-detect/debug controls, and the beginning of the `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` PCI configuration block. It ends inside `BIF_CFG_DEV0_SWDS0_LINK_CNTL`, before that register's later shift and mask definitions in the following chunk.

Although this path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCIe and BIF configuration registers. Each hardware field is represented as one or both of:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for encoding or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating, clearing, or preserving that field.

AMDGPU code combines these constants with register addresses from companion offset headers and with register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`. The header names field positions only; it does not describe access ordering or side effects.

## Important Macro Families

The opening `PCIE_LC_*` portion describes link-controller policy and equalization controls. It includes local equalization presets and coefficients, forced 8 GT/s and 16 GT/s pre/cursor/post-cursor coefficients, best equalization settings and FOM reporting, equalization request coefficients, SRIS/SRNS mode and autodetect controls, EIEOS handling, L1/L0s standby behavior, RX recovery timeout, scheduled RX equalization, ESM/PLL state bits, link management enablement, bandwidth hints, link speed/width updates, and link power state tracking.

The strap and low-power link-controller groups include `PCIEP_STRAP_LC`, `PSWUSP0_PCIEP_STRAP_MISC`, `PCIEP_STRAP_LC2`, `PCIE_LC_L1_PM_SUBSTATE`, `PCIE_LC_L1_PM_SUBSTATE2`, `PCIE_LC_PORT_ORDER`, and `PCIEP_BCH_ECC_CNTL`. These constants describe hardware strap-derived link behavior, PLL lane enables, ASPM/L1.1/L1.2 timeout and enable bits, port ordering, and BCH/ECC control/status.

`PCIE_LC_CNTL8` through `PCIE_LC_CNTL12` and `PCIE_LC_SAVE_RESTORE_1/2` provide later-generation link policy fields: SKP/OS generation controls, lane reversal, receiver-detect behavior, forced coefficient extensions, clock gating overrides, SRIS/RX training behavior, extended sync and EIEOS rules, receive margining mode, lane-marginal status, save/restore state selection and enablement, and OBFF-related bits.

The `nbio_pcie0_pciedir` block exposes internal PCIe directory/MMIO fields. It covers scratch/reserved registers, RX NAK counters, top-level PCIe control/config/debug, TX tracking address and status, bandwidth-by-unit ID, RX/TX/CI/bus control, LC state/status snapshots, TX status and write-posted-request controls, last received/transmitted TLP dwords, I2C register access expansion/data, configuration controls, link power-management control, port-order control, protocol buffer/decoder/misc status, RX AD controls, sideband protocol controls, and performance counter controls for TXCLK and SCLK domains.

Diagnostic and low-level test families in this chunk include `PCIE_PRBS_*` registers for PRBS clear/status/free-run/user-pattern/bit-count/error-count state across lanes 0-15, `PCIE_HIP_REG*` implementation-specific HIP fields, and `PCIE_STRAP_*` strap capture fields. These are primarily bring-up, lab, validation, or low-level debug surfaces rather than normal display/graphics data paths.

The reset and power-management groups include `SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0/1`, `SWRST_CONTROL_0` through `_6`, `SWRST_EP_COMMAND_0`, `SWRST_EP_CONTROL_0`, `CPM_CONTROL`, `CPM_SPLIT_CONTROL`, `LC_CPM_CONTROL_0/1`, `PCIE_PGMST_CNTL`, and `PCIE_PGSLV_CNTL`. These constants describe command/status bits, reset selection, BIF/port/PHY/PCS/AXI/CPM/reset-domain controls, endpoint reset bits, clock power management enables, timers, gating allows, and master/slave power-gating controls.

The final PCI config-space portion begins `addressBlock: nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` and defines standard bridge/downstream-device fields for `BIF_CFG_DEV0_SWDS0_*`: vendor and device IDs, command/status, revision and class code, cache-line/latency/header/BIST, BARs, bus numbering, I/O and memory base/limit registers, bridge secondary status, prefetchable limits, capability pointers, ROM base, interrupt line/pin, bridge control, power-management capability/status-control, PCIe capability, device capability/control/status, link capability, and the first shift definitions for link control.

## Control Flow

There is no runtime control flow in this header. The practical runtime sequence is supplied by consumers:

1. Select a register address from the matching NBIO offset metadata or from a locally defined SMN address.
2. Read a register value through the AMDGPU PCIe/SOC register accessors.
3. Decode or modify fields using these `__SHIFT` and `_MASK` constants, directly or through helper macros.
4. Write the value back, poll status bits, or clear sticky status according to the hardware programming sequence.

One direct consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which defines `smnPCIE_LC_CNTL6`, reads it with `RREG32_PCIE`, sets `PCIE_LC_CNTL6__LC_L1_POWERDOWN_MASK` and `PCIE_LC_CNTL6__LC_RX_L0S_STANDBY_EN_MASK`, and programs `PCIE_LC_CNTL6__LC_SPC_MODE_8GT` by clearing the mask and shifting a new value into place. Other control flows for PRBS, reset, CPM, performance counters, straps, and bridge config are similarly outside this file.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware state held in GPU registers, PCI configuration space, strap capture registers, and firmware/hardware-managed status fields.

The represented state includes link training/equalization coefficients, selected link speed/width and power states, L1 substate timers and enables, link-management event masks and status, strap values, last TLP debug snapshots, PRBS counters and error counters, performance counter configuration/results, reset command/status bits, CPM and clock gating settings, receive margining settings, bridge command/status bits, bus/window configuration, BAR/ROM values, power-management capability/status, and PCIe device/link capability/control/status fields.

Some fields are normal driver-programmed controls, some are strap/capability readouts, some are hardware-updated status, and some may be command or sticky clear-on-write bits. The generated macro names do not encode read/write permissions, volatility, reset domain, or clear semantics.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask file must remain synchronized with sibling address/default headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`; for example `nbio_2_3_offset.h` provides `cfgBIF_CFG_DEV0_SWDS0_LINK_CNTL` at offset `0x0068`, while this chunk provides the early field positions for that register.

Primary integration is with AMDGPU NBIO, PCIe link-management, power-management, reset, diagnostics, SRIS/SRNS, PRBS validation, clock-gating, and PCI configuration paths. The same macro names also appear across later NBIO generations, so code in files such as `amdgpu/nbio_v2_3.c`, `amdgpu/nbio_v6_1.c`, and `amdgpu/nbio_v7_4.c` can share field-level programming patterns where the ASIC layout is compatible.

The bridge-style `BIF_CFG_DEV0_SWDS0_*` definitions integrate with PCI enumeration and configuration surfaces. Consumers rely on these constants when decoding or programming command/status bits, bus numbers, bridge windows, power-management state, PCIe device controls, link capabilities, link retraining, common clock configuration, and ASPM-related controls.

## Risks And Edge Cases

- The chunk boundaries are partial. The first line begins after several `PCIE_LC_CNTL5` shifts and masks already appeared, and the last line stops before `BIF_CFG_DEV0_SWDS0_LINK_CNTL` is complete. Adjacent chunks are required for whole-register conclusions.
- These macros are untyped constants. A missing or renamed macro is likely to fail at build time, but an incorrect shift or mask can compile cleanly and program an adjacent hardware field.
- Link training and equalization fields are interoperability-sensitive. Bad coefficient, SRIS, EIEOS, RX recovery, scheduled RXEQ, ESM, or SPC-mode masks can cause link training failures, bandwidth regressions, resume instability, or marginal signal integrity.
- Power-management fields are liveness-sensitive. Incorrect L1/L1.1/L1.2, standby, CPM, clock-gating, or link power-state fields can produce hangs, failed wakeups, high idle power, or missed bandwidth transitions.
- Reset command/control bits can affect wide hardware domains, including ports, BIF, PHY, PCS, AXI, endpoint config, and clock/reset fabric. Ordinary read-modify-write treatment is risky if bits are command strobes or self-clearing status.
- Diagnostic fields such as PRBS counters, last TLP snapshots, performance counters, and debug/status fields may be volatile. Polling or clearing them without following hardware sequencing can lose evidence or disturb validation flows.
- PCI bridge configuration fields mix 8-bit, 16-bit, and 32-bit PCI config semantics. Wrong access width or offset pairing can corrupt neighboring command/status, bus numbering, window, interrupt, or capability fields.
- Several field names contain repeated `MASK` tokens, such as `PCIE_LINK_MANAGEMENT_MASK__..._MASK_MASK`, because the hardware register itself is a mask register. Tooling and human review should distinguish the register name from the C macro's field-mask suffix.

## Test Signals

Useful validation is mostly build, boot, and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 support enabled; drift in names used by `nbio_v2_3.c` should surface as compile failures around `PCIE_LC_CNTL6` and related masks.
- Run generated-header consistency checks against the NBIO 2.3 source database and sibling offset headers, including shift/mask pair coverage, non-overlap, field-width, and register-boundary checks.
- Boot affected ASICs and confirm stable PCI enumeration, bridge windows, BAR/ROM values, bus numbers, class codes, capability-list traversal, and PCIe link capability/control/status reporting.
- Exercise PCIe link transitions: Gen speed changes, width changes, retraining, ASPM/L1 substates, SRIS/SRNS paths, equalization, EIEOS handling, suspend/resume, runtime power management, and bandwidth-hint flows.
- Validate reset paths that touch NBIO/BIF/port/PHY/PCS/endpoint domains; unexpected hangs, stuck reset status, or failed re-enumeration point to field-layout or sequencing issues.
- Use PRBS, performance counter, last-TLP, and RX margining diagnostics during bring-up or lab validation; lane-specific error-counter mismatches and impossible counter values are strong signals of bad masks or offsets.
- Monitor power and wake behavior under clock gating, CPM, L1 PM substates, and standby settings; regressions include elevated idle power, missed wakeups, link flaps, or display/compute workload stalls.

## Chunk-Specific Notes For Merge

Merge this with adjacent chunks before producing final file-level research for `nbio_2_3_sh_mask.h`. Preserve that this slice transitions from late link-controller definitions into the `nbio_pcie0_pciedir` MMIO block and then into the beginning of the downstream/bridge PCI config decoder block, ending mid-`BIF_CFG_DEV0_SWDS0_LINK_CNTL`.

### subset-b-002927: lines 56613-59036

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 56613-59036

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, dynamic allocation, locking, software persistence, or executable control flow. The macros define bit offsets and bit masks for NBIO/BIF PCIe configuration-space registers.

The range starts in the middle of `BIF_CFG_DEV0_SWDS0_LINK_CNTL`, after the earlier `PM_CONTROL`, `READ_CPL_BOUNDARY`, `LINK_DIS`, `RETRAIN_LINK`, `COMMON_CLOCK_CFG`, and `EXTENDED_SYNC` shift definitions from the previous chunk. It then covers the rest of the `BIF_CFG_DEV0_SWDS0_*` PCIe downstream-switch/device configuration decode, including PCIe capability 2, MSI, SSID, vendor-specific capability, virtual-channel, device serial number, AER, secondary PCIe, ACS, DLF, 16GT PHY, equalization, and PCIe margining definitions.

The chunk then enters two SR-IOV virtual-function address blocks:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, covering a complete `BIF_CFG_DEV0_EPF0_VF0_0_*` PCI config-space image from vendor/device IDs through ATS and ARI enhanced capabilities.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, covering the start of `BIF_CFG_DEV0_EPF0_VF1_0_*` from vendor/device IDs through the first part of `PCIE_UNCORR_ERR_STATUS`.

The range ends at `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_STATUS__ECRC_ERR_STATUS__SHIFT`. The remaining `VF1` uncorrectable-error status masks and following AER/VF1 capability fields continue in the next chunk. In total this slice contains 2,142 `#define` lines: 1,073 `__SHIFT` macros and 1,069 `_MASK` macros.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`nbio_2_3_sh_mask.h` publishes the bitfield ABI for AMD NBIO 2.3 registers. Each register field is represented by generated preprocessor constants:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate or preserve that field.

This chunk focuses on PCIe configuration and capability bitfields for one downstream-switch/device block (`SWDS0`) and the first virtual-function endpoint-function blocks (`EPF0_VF0_0` and part of `EPF0_VF1_0`). Runtime AMDGPU code combines these constants with matching register offsets from `nbio_2_3_offset.h` and reset/default values from `nbio_2_3_default.h`. Callers typically use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

The macros are not policy by themselves. They are the generated contract that lets NBIO, BIF, PCIe, SR-IOV, mailbox, reset, interrupt, and error-handling code address the correct bits when programming or decoding hardware state.

## Important Macro Families

### SWDS0 PCIe Link, Slot, And Device Capability Fields

The opening macros complete `BIF_CFG_DEV0_SWDS0_LINK_CNTL` and then cover `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS`. These fields map standard PCIe link and slot semantics: current link speed, negotiated width, link training, slot clock, data-link active state, bandwidth-management status, hotplug and attention-button controls, power-controller and indicator controls, presence detect, electromechanical interlock state, and data-link state change reporting.

`BIF_CFG_DEV0_SWDS0_DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` expose PCIe Capability 2 fields such as completion timeout support/value/disable, ARI forwarding, AtomicOp routing/request/egress blocking, ID-based ordering, LTR enablement, emergency power reduction, ten-bit tags, OBFF, end-to-end TLP prefix support/blocking, and function readiness support. `DEVICE_STATUS2` is reserved in this generated description.

`BIF_CFG_DEV0_SWDS0_LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover supported link speeds, crosslink support, lower SKP ordered-set generation/receive support, RTM presence detection, DRS-related fields, target link speed, compliance entry, hardware autonomous speed disable, de-emphasis, transmit margin, 8GT equalization phases, link equalization requests, downstream component presence, and DRS message receipt.

The chunk also defines reserved `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` masks, making clear that those register slots exist in the generated config-space layout even though their fields are reserved here.

### SWDS0 MSI, SSID, Vendor-Specific, And Virtual Channel Capabilities

`BIF_CFG_DEV0_SWDS0_MSI_*` defines the MSI capability list entry, message-control bits, low/high message address fields, and 32-bit/64-bit message-data fields. The control field includes MSI enable, multi-message capability, multi-message enable, 64-bit capable indication, and per-vector masking capability.

`BIF_CFG_DEV0_SWDS0_SSID_*` describes subsystem vendor and subsystem ID fields. The vendor-specific enhanced capability macros define the enhanced-capability header, vendor-specific header (`VSEC_ID`, `VSEC_REV`, `VSEC_LENGTH`), and two full-width scratch payload registers.

The virtual-channel block covers `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status, and VC0/VC1 resource capability/control/status. These fields expose extended VC counts, low-priority VC counts, arbitration table entry sizes and offsets, VC arbitration selection/loading, TC-to-VC mapping, port arbitration selection/loading, VC ID, VC enable, and VC negotiation pending. These definitions are relevant to traffic-class and virtual-channel negotiation or diagnostics.

### SWDS0 AER, Secondary PCIe, ACS, DLF, 16GT PHY, And Margining

The AER section starts with `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` and covers uncorrectable error status, mask, and severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.

Correctable error status and mask fields cover receiver errors, bad TLP/DLLP, replay timer timeout, advisory non-fatal, corrected internal error, header-log overflow, and virtual-function AER message number. `PCIE_ADV_ERR_CAP_CNTL` exposes first error pointer, ECRC generation/check capability and enable bits, multiple header recording capability/enable, TLP prefix log presence, and completion timeout logging capability. The header log and TLP prefix log registers are full-width payload fields.

The secondary PCIe section defines the enhanced-capability header, `LINK_CNTL3` perform-equalization/control bits, lane error status, and per-lane 8GT equalization controls for lanes 0-15. Each lane has downstream-port TX preset, downstream-port RX preset hint, upstream-port TX preset, upstream-port RX preset hint, and reserved fields.

The ACS section defines source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-control vector size capability/control fields. These fields are security and isolation sensitive in virtualized or peer-to-peer topologies.

The DLF section defines local/remote Data Link Feature support, exchange-enable, and valid-status fields. The 16GT PHY section defines a PCIe PHY enhanced-capability header, reserved link cap/control fields, 16GT link equalization-complete/phase/request status bits, local/RTM parity mismatch status, and per-lane 16GT downstream/upstream TX preset fields for lanes 0-15.

The PCIe margining section defines the margining enhanced-capability header, port capability/status, and per-lane margining control/status pairs for lanes 0-15. Each lane exposes receiver number, margin type, usage model, and payload fields. These definitions matter for PCIe link diagnostics and margining workflows.

### VF0 PCI Configuration Space

The `BIF_CFG_DEV0_EPF0_VF0_0_*` block defines a full PCI configuration-space bitfield map for virtual function 0 under endpoint function 0. It starts with standard PCI header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache-line size, latency timer, header type/device type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, minimum grant, and maximum latency.

The VF0 command/status fields expose I/O access, memory access, bus master, special cycle, memory write invalidate, PAL snoop, parity error response, stepping, SERR, fast back-to-back, interrupt disable, immediate readiness, interrupt status, capability-list presence, parity and abort status, and DEVSEL timing. `DEVICE_CNTL` includes the normal PCIe error enable bits, relaxed ordering, max payload size, extended tag, phantom function, auxiliary power PM, no-snoop, max read request size, and `INITIATE_FLR`. The associated `DEVICE_CAP` includes FLR capability and payload/latency/power fields.

VF0 then mirrors the PCIe link capability/control/status and capability-2 families seen in SWDS0: link speed/width, ASPM/latency/power/link-bandwidth fields, link disable/retrain/common-clock/extended-sync bits, link status/training fields, completion timeout, ARI, AtomicOp, IDO, LTR, OBFF, ten-bit tag, TLP prefix, emergency power, and 8GT equalization status.

Interrupt-related VF0 definitions cover MSI and MSI-X capability list entries, message-control fields, message address/data fields, MSI mask/pending and 64-bit variants, MSI-X table size, function mask, MSI-X enable, MSI-X table BIR/offset, and MSI-X pending bit array BIR/offset.

VF0 vendor-specific and AER sections define the VSEC header/scratch registers, AER enhanced-capability header, uncorrectable error status/mask/severity, correctable status/mask, AER capability/control, full-width header logs, and TLP prefix logs. The VF0 block ends with ATS and ARI enhanced capabilities: ATS invalidate queue depth, page-aligned request, global invalidate support, STU, ATC enable, ARI MFVC/ACS function group capability and enables, next function number, and function group fields.

### VF1 PCI Configuration Space Start

The `BIF_CFG_DEV0_EPF0_VF1_0_*` block repeats the same generated PCI/VF pattern as VF0 from vendor ID through MSI-X, vendor-specific capability, and the AER enhanced-capability header. The fields covered in this chunk include standard PCI command/status/header/BAR/class/capability fields; PCIe device/link capability/control/status fields; capability-2 fields; MSI/MSI-X programming fields; vendor-specific capability fields; and the first ten uncorrectable-error status shift definitions.

The chunk stops before the matching `VF1` `PCIE_UNCORR_ERR_STATUS` masks and before the `UNSUPP_REQ`, `ACS_VIOLATION`, `UNCORR_INT_ERR`, `MC_BLOCKED_TLP`, `ATOMICOP_EGRESS_BLOCKED`, and `TLP_PREFIX_BLOCKED` status shifts. Any final file-level report must join this chunk with the following one before claiming complete VF1 AER coverage.

## Control Flow

There is no runtime control flow in this header. Runtime control belongs to AMDGPU and Linux PCI/PCIe code that includes the generated NBIO headers. The usual sequence is:

1. Select a register offset from `nbio_2_3_offset.h` or a local NBIO/BIF address table.
2. Read a 16-bit or 32-bit register image through an AMDGPU register helper or prepare a value for writing.
3. Use the `__SHIFT` and `_MASK` constants, usually through `REG_GET_FIELD` or `REG_SET_FIELD`, to decode or update a field.
4. Write the value back, poll status, handle an interrupt/error, or expose decoded state to PCIe, SR-IOV, reset, RAS, or diagnostic logic.

Because these are plain macros, the compiler does not enforce that a field macro is used with the correct register, access width, side-effect model, or PF/VF ownership context.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware register fields whose actual state is maintained by the GPU, PCIe link, firmware, host driver, guest driver, hypervisor, and Linux PCI infrastructure.

The represented state includes PCI command/status bits, link training/status, slot hotplug/status, MSI and MSI-X programming state, subsystem IDs, vendor-specific scratch payloads, virtual-channel arbitration and negotiation state, device serial number payloads, AER status/mask/severity/log state, ACS controls, data-link feature exchange state, PCIe Gen4/16GT equalization and parity state, PCIe margining command/status payloads, ATS/ARI controls, and VF FLR-related command bits.

Some fields are durable configuration until reset or reprogramming, such as max payload size, max read request size, MSI/MSI-X message address/data, ACS controls, VC mappings, ATS enable, and ARI controls. Others are hardware-owned or transient status, such as link training, equalization phase completion, data-link active, AER status/logs, MSI pending bits, margining ready/status, parity mismatch status, and transaction/error flags. The header does not encode read-only/write-only status, write-one-to-clear behavior, self-clearing command bits, polling requirements, reset defaults, ordering constraints, or guest-versus-host ownership rules.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database staying synchronized across companion headers:

- `nbio_2_3_offset.h` maps the same register names to offsets/base indices.
- `nbio_2_3_default.h` maps the same register names to reset/default values.
- `nbio_2_3_sh_mask.h` maps the fields within each register.

AMDGPU NBIO/BIF code, PCIe link management, interrupt setup, SR-IOV virtualization, PF/VF reset handling, AER/RAS handling, mailbox and FLR paths, and diagnostics use these definitions indirectly through register access helpers. Direct include-site families in this tree include NBIO 2.3 driver code such as `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, virtualization support such as `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU/power-management code that includes the same generated register namespace.

The SWDS0 definitions integrate with PCIe downstream-switch/device configuration and diagnostics. The VF0/VF1 definitions integrate with SR-IOV virtual function enumeration, guest-visible PCI capability layout, FLR/reset behavior, interrupt delivery, AER reporting, ATS/ARI negotiation, and hypervisor/PF-mediated policy. Linux PCI core concepts are visible in the field names, but this header is an AMDGPU hardware register map rather than ordinary generic PCI config access code.

## Risks And Edge Cases

- The range has artificial boundaries. It starts mid-`BIF_CFG_DEV0_SWDS0_LINK_CNTL` and ends mid-`BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_STATUS`. Adjacent chunks must be reconciled for whole-register and whole-file conclusions.
- Generated macro drift compiles cleanly when names still exist. A wrong mask or shift can silently program the wrong PCIe capability bit, decode stale status, or corrupt adjacent fields.
- Width mismatches are easy in PCI config space. This chunk mixes 8-bit, 16-bit, and 32-bit logical fields, but all are exposed as untyped C macros.
- PCIe command/status and FLR fields are side-effect sensitive. Incorrect masks around `BUS_MASTER_EN`, `MEM_ACCESS_EN`, error enables, `INT_DIS`, or `INITIATE_FLR` can break enumeration, reset, or guest recovery.
- MSI/MSI-X fields affect interrupt routing. Wrong address/data/control/table/PBA masks can cause lost interrupts, unexpected interrupts, or vectors being exposed before software finishes programming them.
- AER fields are protocol and reliability sensitive. Incorrect status/mask/severity/header-log/TLP-prefix definitions can suppress real errors, misclassify fatal/nonfatal conditions, or produce misleading diagnostics.
- ACS, ATS, ARI, and VC fields are virtualization and isolation sensitive. Wrong masks can alter peer-to-peer routing, translation behavior, function grouping, or traffic-class mapping.
- Link, 8GT/16GT equalization, DLF, and margining fields are hardware-owned or training-sensitive. Treating status bits as ordinary writable configuration can destabilize links or invalidate diagnostics.
- Per-lane generated repetition is vulnerable to mechanical one-off errors. Lanes 0-15 for 8GT equalization, 16GT presets, and margining control/status should remain structurally consistent.
- Full-width address, scratch, log, and payload fields use `0xFFFFFFFF` masks. Reusing those masks against the wrong offset can overwrite unrelated hardware state.

## Test And Validation Signals

Useful validation is mostly build, hardware bring-up, PCIe enumeration, and virtualization coverage:

- Build AMDGPU code paths that include `nbio_2_3_sh_mask.h`; missing or renamed generated macros should fail at compile time in NBIO, SR-IOV, SMU, or PCIe consumers.
- Boot an NBIO 2.3 ASIC and exercise NBIO initialization, PCIe config-space access, doorbell/interrupt setup, HDP/PCIe paths, and link-management paths that rely on the generated register set.
- Enumerate the SWDS0 PCIe capability chain and confirm link, slot, MSI, SSID, vendor-specific, VC, serial-number, AER, secondary PCIe, ACS, DLF, 16GT PHY, and margining capability fields decode correctly.
- Enable SR-IOV and enumerate at least VF0 and VF1, checking standard PCI header fields, capability pointers, PCIe device/link capabilities, MSI/MSI-X visibility, AER capability layout, ATS/ARI visibility, and FLR behavior.
- Run guest VF reset/FLR tests and confirm command/status, link status, MSI/MSI-X state, AER status/logs, ATS/ARI state, and capability layout return to expected hardware defaults.
- Exercise MSI and MSI-X interrupt delivery for PF and VF contexts, including vector programming, vector masking, pending-bit handling, interrupt disable, and reset/re-enable sequences.
- Run PCIe link retraining, suspend/resume, runtime power-management, and error-recovery tests; link training stalls, equalization failures, completion timeouts, AER storms, or bad negotiated width/speed are strong signals of mask/offset drift.
- Use AER or platform error-injection diagnostics, where available, to validate uncorrectable/correctable status, masks, severity bits, first-error pointer, ECRC controls, header logs, and TLP prefix logs.
- In virtualized or peer-to-peer configurations, validate ACS, ATS, ARI, and VC behavior to catch isolation, routing, or translation regressions.
- On platforms exposing PCIe Gen4/16GT diagnostics or margining, verify per-lane equalization presets, parity mismatch reporting, margining ready/software-ready status, and margining control/status payload echo for lanes 0-15.

### subset-b-002928: lines 59037-61469

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 59037-61469

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts inside `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_STATUS`, after the first uncorrectable-error field shifts and before the corresponding masks. It then completes the tail of endpoint PF0 virtual function 1 (`BIF_CFG_DEV0_EPF0_VF1_0_*`) advanced error reporting and ATS/ARI definitions, covers full repeated PCI/PCIe configuration field layouts for virtual functions 2, 3, and 4 (`BIF_CFG_DEV0_EPF0_VF2_0_*`, `BIF_CFG_DEV0_EPF0_VF3_0_*`, `BIF_CFG_DEV0_EPF0_VF4_0_*`), and begins virtual function 5 (`BIF_CFG_DEV0_EPF0_VF5_0_*`) through `PCIE_CAP`. The final line is followed by `BIF_CFG_DEV0_EPF0_VF5_0_DEVICE_CAP` in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCI configuration decoder registers that expose PF0 virtual-function PCI and PCIe capabilities. Each field is represented by generated macros of the form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The matching register offsets live in sibling NBIO generated headers, especially `nbio_2_3_offset.h`, where config-space symbols identify the register address. AMDGPU consumers combine those offsets with these masks through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. This file names bitfields only; it does not define access ordering, read/write permissions, reset values, or side-effect semantics.

## Important Macro Families

The VF1 tail is focused on PCIe Advanced Error Reporting and translation/routing enhanced capabilities. It includes uncorrectable error status/mask/severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, atomic operation egress blocked, and TLP prefix blocked conditions. It also defines correctable error status/mask fields for receiver error, bad TLP/DLLP, replay rollover and timeout, advisory non-fatal error, internal correctable error, and header log overflow. The same VF1 tail carries AER capability/control bits for first error pointer, ECRC generation/checking, multiple-header recording, TLP prefix log presence, completion-timeout log capability, four 32-bit TLP header log words, four 32-bit TLP prefix log words, ATS enhanced capability/capability/control fields, and ARI enhanced capability/capability/control fields.

The VF2, VF3, and VF4 blocks are structurally identical full virtual-function PCI configuration images. Each begins with ordinary PCI header fields: vendor/device ID, command/status, revision and class-code bytes, cache line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. The command/status masks cover I/O, memory, bus mastering, parity/SERR, interrupt disable, immediate readiness, capability-list presence, target/master abort status, system error, and parity detection.

For each full VF block, the PCIe capability section defines capability-list metadata and device/link capability/control/status fields. These include max payload support and size, max read request size, relaxed ordering, no-snoop, extended tags, phantom functions, auxiliary power management, function-level reset initiation/capability, correctable/non-fatal/fatal/unsupported-request reporting enables, transactions pending, link speed and width capability/status, ASPM and clock power management controls, retrain/link disable/common clock/extended sync controls, bandwidth-management and autonomous-bandwidth interrupts, DRS signaling, data-link active status, Gen2+ supported link speeds, compliance and de-emphasis controls, 8 GT/s equalization phase status, crosslink/presence reporting, and downstream-component presence.

The PCIe capability version 2 portions for VF2 through VF4 add completion timeout range/disable, ARI forwarding support and enable, atomic operation routing/request/egress control, ID-based ordering request/completion enables, latency tolerance reporting, OBFF, end-to-end TLP prefix support/blocking, ten-bit tag requester/completer support and enable, emergency power reduction support/request, and fast role swap support. `DEVICE_STATUS2` is represented as a reserved 16-bit field in these VF blocks.

The interrupt capability groups for VF2 through VF4 define MSI and MSI-X layouts. MSI fields cover capability-list metadata, MSI enable, multiple-message capability and enable, 64-bit support, per-vector masking capability, message address low/high, message data, mask, 64-bit data/mask aliases, and pending bits. MSI-X fields cover table size, function mask, MSI-X enable, table BIR and offset, and PBA BIR and offset.

The vendor-specific and AER enhanced-capability groups for VF2 through VF4 include PCIe vendor-specific enhanced capability list fields, vendor-specific header fields, two vendor-specific payload dwords, AER enhanced capability list fields, uncorrectable/correctable error status and masks, uncorrectable severity, AER capability/control, header logs, and TLP prefix logs. These macros are diagnostic and recovery oriented: they identify status bits that may be sticky, masked, severity-classified, or used to preserve error evidence for later decoding.

The ATS and ARI groups for VF2 through VF4 define PCIe enhanced capability headers plus control/capability payloads. ATS fields include invalidate queue depth, page-aligned requests, global invalidate support, STU, and ATC enable. ARI fields include MFVC and ACS function group capability/enable bits, next function number, and function group selection.

The VF5 block in this chunk is only the beginning of the next repeated virtual-function configuration image. It covers the same standard PCI header and BAR-related fields as VF2 through VF4, then reaches `PCIE_CAP_LIST` and `PCIE_CAP` metadata. Its device capability and later PCIe/AER/MSI/ATS/ARI fields are outside this chunk.

## Control Flow

There is no runtime control flow in this header. The effective use pattern in AMDGPU code is:

1. Select the corresponding NBIO 2.3 config-space register offset from the generated offset header or a per-ASIC register table.
2. Read or prepare a PCIe config register value through the driver's PCIe/SOC15 access helpers.
3. Use the `__SHIFT` and `_MASK` constants directly, or through helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, to decode or update a specific field.
4. Write the value back, poll a hardware-owned status bit, clear sticky error state according to PCIe rules, or hand the decoded value to reset, interrupt, virtualization, or RAS/error handling code.

The repeated VF2/VF3/VF4 layout implies table-like hardware, but this header does not implement iteration. Any loop over virtual functions or capability families is implemented by driver code that chooses the matching register offset and macro family.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes GPU PCI configuration and enhanced-capability state owned by hardware, firmware, the PCIe fabric, the host kernel, and the AMDGPU driver.

Some represented fields are configuration that can persist until reset, function-level reset, suspend/resume, power transition, or explicit driver reprogramming: PCI command enables, BAR values, MSI/MSI-X message address/data/mask state, PCIe device/link controls, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR/OBFF controls, ATS ATC enablement, and ARI function grouping.

Other fields are hardware-owned status, command strobes, or sticky diagnostic state: PCI status bits, device and link status, link training/equalization status, transactions pending, MSI pending bits, AER correctable/uncorrectable status, AER header logs, and TLP prefix logs. The masks do not encode whether a bit is read-only, write-one-to-clear, write-one-to-set, self-clearing, firmware-owned, or volatile; callers must follow the hardware programming guide and PCIe specification behavior for each register.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This `*_sh_mask.h` slice must stay synchronized with the companion offset/default headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`; the offset header gives address names while this file gives field positions for values at those addresses.

Primary integration is with AMDGPU NBIO, PCIe, interrupt, reset, RAS/AER, SR-IOV, and virtualization paths. These macros support virtual-function config-space exposure and driver-side interpretation of function identity, BARs, command/status, PCIe device/link capabilities, MSI/MSI-X delivery, AER status/logging/masking/severity, ATS address-translation services, ARI routing/function grouping, and function-level reset behavior.

The macros are untyped integer constants. Missing or renamed macro names usually fail at compile time in consuming code, but an incorrect shift or mask can compile cleanly and cause adjacent PCIe fields to be read, cleared, or programmed incorrectly. Because this file is generated ASIC metadata, manual changes should be treated as hardware ABI changes and checked against the authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first line is already inside VF1 `PCIE_UNCORR_ERR_STATUS`, and the last line stops after VF5 `PCIE_CAP`; adjacent chunks are required before making whole-register or whole-VF claims for VF1 and VF5.
- The range mixes 8-bit PCI header fields, 16-bit PCI/PCIe capability words, and 32-bit enhanced-capability dwords. Wrong access width or offset pairing can corrupt neighboring fields even when a mask is locally correct.
- AER fields are side-effect sensitive. Treating uncorrectable/correctable status bits, severity bits, header logs, or TLP prefix logs as ordinary retained configuration can clear evidence, hide real errors, or misclassify recovery severity.
- Link and device-control fields are interoperability-sensitive. Incorrect max payload/read request, completion timeout, relaxed ordering, no-snoop, FLR, ASPM, retrain, target speed, equalization, or DRS masks can cause enumeration failures, link retraining problems, performance regressions, or reset hangs.
- MSI/MSI-X fields are interrupt-delivery critical. Wrong enable, message address/data, mask, pending, table, PBA, or function-mask fields can cause lost interrupts, spurious interrupts, or poor isolation between virtual functions.
- ATS and ARI fields affect I/O address translation and PCIe function routing. Incorrect STU/ATC enable, queue-depth, global invalidate, ARI forwarding, next-function, or function-group masks can break DMA address translation, virtual-function discovery, or isolation.
- The VF2, VF3, and VF4 blocks are highly repetitive. Off-by-one copy or generation errors are plausible and may only appear on configurations that instantiate or exercise the affected virtual function.
- Full-width BAR, ROM base, CIS pointer, MSI address, AER log, and vendor-specific dword fields are not self-validating. Pairing a correct full-width mask with the wrong offset can overwrite or decode unrelated hardware state.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, and ARI support enabled; missing symbols should surface as compile failures in NBIO/PCIe/interrupt/virtualization code.
- Run generated-header consistency checks against the NBIO register database and sibling offset headers, including shift/mask pair checks, field width checks, non-overlap checks within each register, and repeated VF layout comparison for VF2 through VF4.
- Boot affected hardware and confirm PCI enumeration exposes stable VF vendor/device IDs, class codes, BARs, capability-list traversal, PCIe capability blocks, MSI/MSI-X capability blocks, AER capability blocks, ATS capability blocks, and ARI capability blocks.
- Exercise SR-IOV or other virtual-function configurations that instantiate VF2, VF3, VF4, and VF5; validate VF config-space reads, BAR sizing, bus mastering/memory enable behavior, FLR, and isolation-relevant capabilities.
- Exercise MSI and MSI-X interrupt delivery from virtual functions under graphics, compute, reset, and virtualization workloads; lost, stuck-pending, or unexpectedly masked interrupts point to field-layout or offset mismatches.
- Run PCIe link/reset tests covering link speed/width reporting, retraining, data-link active reporting, completion timeout handling, FLR initiation/completion, suspend/resume, and error recovery.
- Use AER fault observation or injection where available to validate uncorrectable/correctable status bits, masks, severity mapping, header logs, TLP prefix logs, and driver recovery decisions.
- Validate ATS/ARI behavior in IOMMU and virtualization scenarios, including ATC enablement, invalidation-related fields, ARI forwarding, and function-number routing.

## Chunk-Specific Notes For Merge

This chunk should be merged with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final source-tree-aligned per-file research document. Preserve that this slice specifically covers the PF0 VF1 AER/ATS/ARI tail, complete repeated VF2/VF3/VF4 PCIe config masks, and the start of VF5 through `PCIE_CAP`.

### subset-b-002929: lines 61470-63890

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 61470-63890

## Scope And Purpose

This chunk is a generated AMD GPU NBIO 2.3 register shift/mask header slice. It contains C preprocessor constants for bitfield extraction and construction, not executable functions. The slice covers PCI configuration-space fields for SR-IOV virtual functions under `BIF_CFG_DEV0_EPF0_VF*_0`, starting in the middle of the VF5 PCIe capability register definitions and ending after the VF8 vendor-specific scratch registers.

The definitions are part of the AMDGPU driver's hardware register contract for NBIO 2.3 ASICs. They pair with the sibling offset/default headers, especially `nbio_2_3_offset.h`, and are consumed by driver code through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` from `amdgpu.h`. These helpers concatenate names like `BIF_CFG_DEV0_EPF0_VF6_0_COMMAND__BUS_MASTER_EN_MASK` and `...__SHIFT` to modify or decode fields without open-coded bit arithmetic.

Within this chunk there are 2,145 `#define` entries across VF5, VF6, VF7, and VF8. VF6 and VF7 are complete virtual-function register field blocks in this line window. VF5 is a tail block that begins after the VF5 capability-list fields, and VF8 is a head block that ends just before the VF8 advanced-error-reporting fields that continue in the next chunk.

## Covered Register Groups

The repeated naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>_MASK`

The chunk covers these virtual functions and approximate scope:

- `VF5`: PCIe capability, device/link capability and control/status, MSI/MSI-X, vendor-specific, advanced error reporting, ATS, and ARI field masks from lines 61470-62026.
- `VF6`: a full PCI config header and extended capability block from vendor/device IDs through ARI control at lines 62028-62722.
- `VF7`: another full PCI config header and extended capability block from vendor/device IDs through ARI control at lines 62724-63418.
- `VF8`: PCI config header through PCIe vendor-specific scratch fields at lines 63420-63890; AER and later capability masks continue after this chunk.

Important register families represented here include:

- Basic PCI config fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, `MSI_PENDING_64`, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor and PCIe extended capabilities: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, `PCIE_VENDOR_SPECIFIC2`, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable AER status/mask/severity registers, `PCIE_ADV_ERR_CAP_CNTL`, header/TLP-prefix logs, `PCIE_ATS_*`, and `PCIE_ARI_*`.

## Important APIs, Types, And Functions

This header chunk defines no C types, structs, enums, or functions. Its "API" is the exported macro namespace used by AMDGPU source files at compile time.

The most important consumer API shape is:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
- `REG_SET_FIELD(orig_val, reg, field, field_val)` clears the field's mask in `orig_val` and inserts `field_val << SHIFT` masked by `MASK`.
- `REG_GET_FIELD(value, reg, field)` extracts `(value & MASK) >> SHIFT`.

These macros mean a constant pair such as `BIF_CFG_DEV0_EPF0_VF6_0_COMMAND__MEM_ACCESS_EN__SHIFT` and `BIF_CFG_DEV0_EPF0_VF6_0_COMMAND__MEM_ACCESS_EN_MASK` is a compile-time dependency for code that calls:

```c
REG_SET_FIELD(value, BIF_CFG_DEV0_EPF0_VF6_0_COMMAND, MEM_ACCESS_EN, 1)
```

Direct includes found in this tree include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, `pm/swsmu/smu11/navi10_ppt.c`, and `pm/swsmu/smu11/sienna_cichlid_ppt.c`. Those files include `nbio_2_3_sh_mask.h` together with NBIO offset/default headers or other ASIC register headers to compile register access paths for NBIO 2.3 hardware.

## Field Semantics

The basic PCI config fields describe each virtual function's PCI identity and resource aperture:

- `COMMAND` has enable/control bits such as I/O access, memory access, bus mastering, parity-error response, SERR, and interrupt disable.
- `STATUS` has detected-capability and error/status bits such as interrupt status, capability-list presence, master-data parity error, signaled target abort, received target/master abort, signaled system error, detected parity error, and immediate-readiness.
- BAR and ROM fields expose address/memory properties through masks over the full 32-bit register value or low-order type bits.
- `CAP_PTR`, interrupt line/pin, min grant, and max latency preserve legacy PCI capability and interrupt metadata.

The PCIe capability blocks expose negotiated link/device behavior:

- `DEVICE_CAP` and `DEVICE_CNTL` describe and control maximum payload size, relaxed ordering, extended tags, no-snoop, read request size, FLR, and power-management related bits.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover speed, width, ASPM, link retraining/disable, clocking, link-bandwidth interrupts, data-link active state, and training/status indicators.
- `DEVICE_CAP2` and `DEVICE_CNTL2` add completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefix handling, emergency power reduction, and FRS support/control.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover supported link speeds, compliance modes, autonomous speed disable, de-emphasis, equalization status, crosslink resolution, downstream presence, and DRS message status.

The interrupt capability blocks mirror the standard MSI and MSI-X PCI capability layouts:

- `MSI_MSG_CNTL` fields include `MSI_EN`, multi-message capability/enables, 64-bit support, and per-vector masking capability.
- `MSI_MSG_ADDR_*`, `MSI_MSG_DATA*`, `MSI_MASK*`, and `MSI_PENDING*` provide payload and mask/pending fields.
- `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` describe MSI-X table size, function mask, enable bit, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

The AER, ATS, ARI, and vendor-specific groups provide extended capability metadata and error reporting:

- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` define fields for data-link protocol, surprise-down, poisoned TLP, flow-control, completion-timeout, completer-abort, unexpected completion, receiver-overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP-prefix blocked conditions.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` define receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal, header-log overflow, and similar correctable conditions.
- `PCIE_ADV_ERR_CAP_CNTL` defines first-error pointer, ECRC generation/check capability and enable bits, multiple-header recording, TLP prefix log presence, and log size.
- `PCIE_HDR_LOG*` and `PCIE_TLP_PREFIX_LOG*` expose raw logged DWORD fields.
- `PCIE_ATS_*` and `PCIE_ARI_*` expose address-translation-service and alternative routing-ID capability/control fields.
- `PCIE_VENDOR_SPECIFIC*` supplies VSEC capability headers and scratch fields.

## Control Flow And Execution Behavior

There is no runtime control flow in this chunk. The effective flow is compile-time name resolution:

1. A driver file includes `nbio_2_3_sh_mask.h`.
2. The compiler expands a field helper such as `REG_SET_FIELD` or direct bit arithmetic using the `__SHIFT` and `_MASK` constants.
3. Runtime register access code uses the computed value with hardware accessors such as `RREG32*`, `WREG32*`, `RREG32_SOC15`, `WREG32_SOC15`, or PCI/SMN helpers elsewhere in the driver.

Because each macro is a raw literal, the header has no branches, loops, allocation, locking, or function-call side effects. Behavioral changes only happen indirectly when a consumer reads or writes the affected hardware register field.

## State And Persistence Behavior

The file stores no software state and has no persistence layer. Its constants describe persistent or semi-persistent hardware state in the GPU's PCI configuration and NBIO register space:

- Command/control masks may be used to enable memory access, bus mastering, MSI/MSI-X, link retraining, FLR, ARI, ATS, LTR, OBFF, and related VF-visible controls.
- Status masks decode transient hardware state such as link training, pending transactions, MSI pending bits, AER status bits, and equalization/link status.
- Log masks identify AER header/TLP prefix logging registers that may retain hardware error evidence until software clears or hardware overwrites it.

In SR-IOV environments, these fields represent per-virtual-function configuration surfaces. Incorrect masks can cause the host PF/VF boundary to expose, hide, or mutate the wrong bit in a VF's virtual PCI config space.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- `nbio_2_3_offset.h`: supplies register addresses/offsets corresponding to the shift/mask names in this header.
- `nbio_2_3_default.h`: supplies reset/default values for some NBIO 2.3 registers.
- `amdgpu.h`: defines `REG_FIELD_SHIFT`, `REG_FIELD_MASK`, `REG_SET_FIELD`, and `REG_GET_FIELD`, the token-pasting helpers that rely on this naming convention.
- SOC15 and NBIO accessors: code in `nbio_v2_3.c` uses NBIO register constants with `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and related helpers.
- Virtualization paths: `mxgpu_nv.c` includes this header while implementing Navi SR-IOV mailbox interactions between VF and PF, making the NBIO VF register namespace relevant to virtual GPU operation.
- SMU power-management paths: Navi10/Sienna Cichlid SMU tables include this header alongside other register headers for ASIC-specific power, link, and status handling.

The chunk also has structural dependencies on adjacent line ranges of the same file. VF5's basic config fields precede this chunk, and VF8's AER/ATS/ARI fields continue after it. A final per-file merge must preserve that this chunk is one middle segment of a much larger generated register table.

## Risks And Maintenance Notes

The main risk is silent hardware misprogramming from incorrect generated constants. A wrong shift or mask can compile cleanly while causing runtime code to write adjacent control bits or misread status/error state.

Specific risks in this chunk:

- SR-IOV VF replication: VF6, VF7, and VF8 blocks repeat nearly identical layouts. Copy-generation drift in one VF block could affect only that virtual function and may be missed by tests that exercise a smaller VF count.
- PCIe capability correctness: fields such as payload size, read request size, FLR, ARI, ATS, atomic ops, LTR, OBFF, MSI/MSI-X enable/mask, and AER severity directly influence PCIe interoperability and error handling.
- Boundary completeness: this chunk starts inside VF5 and ends inside VF8. Research or validation that treats it as a standalone complete file would miss preceding/following fields required for a full VF definition.
- Token-paste coupling: consumers depend on exact spelling of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Renaming a field or changing one half of a shift/mask pair breaks helper expansion or creates mismatched behavior.
- Width assumptions: most values use `L` suffix literals and are intended for 32-bit register fields. Any consumer using narrower types could truncate masks such as `0xFFFFFFFFL`, `0xFFF00000L`, or `0x80000000L`.

## Test Signals

There are no unit tests for this generated header in the chunk itself. Useful validation signals are compile-time and hardware/driver behavior:

- Build coverage for AMDGPU configurations that include NBIO 2.3 users. Missing or misspelled macros should fail compilation in files that call `REG_SET_FIELD` or `REG_GET_FIELD`.
- Static comparison against AMD's register database or sibling generated headers, especially for repeated VF6/VF7/VF8 layouts, can detect copy-generation drift.
- SR-IOV smoke tests that enumerate multiple VFs and validate PCI config space fields, BARs, MSI/MSI-X capability tables, and ARI/ATS capability chains.
- PCIe link and power-management tests that check advertised link speed/width, ASPM behavior, retraining, LTR/OBFF control, FLR, and completion-timeout behavior.
- RAS/AER tests that inject or observe correctable and uncorrectable PCIe errors and confirm that status, mask, severity, header log, and TLP prefix log fields decode correctly.
- Runtime register tracing around NBIO 2.3 driver paths can confirm that field writes preserve unrelated bits by using the matching mask/shift pairs.

## Chunk Boundary Notes

Line 61470 continues `BIF_CFG_DEV0_EPF0_VF5_0_PCIE_CAP`; the `VERSION__SHIFT` and earlier VF5 base config definitions are above the chunk. Line 63890 ends with `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_VENDOR_SPECIFIC2__SCRATCH_MASK`; the next block, `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, begins after this chunk.

### subset-b-002930: lines 63891-66318

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 63891-66318

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header fragment. It defines C preprocessor constants for PCI/PCIe configuration-space register fields, not executable code. Each field appears as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. These names are meant to be used with the matching offsets from `nbio_2_3_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, and SOC15 accessors.

The range starts at the tail of virtual function 8 (`VF8`) PCIe Advanced Error Reporting, ATS, and ARI field definitions. It then fully covers the generated config-space field masks for `VF9`, `VF10`, and `VF11`, and ends partway through `VF12` at `BIF_CFG_DEV0_EPF0_VF12_0_ROM_BASE_ADDR`.

## Purpose

These macros describe the bit layout of NBIO 2.3 PCIe configuration-space images for SR-IOV virtual functions. The covered register families model standard PCI header fields and extended PCIe capabilities for `BIF_CFG_DEV0_EPF0_VF*` functions:

- Vendor/device identity, command/status, revision/class codes, header/BIST, BARs, subsystem identity, ROM base, capability pointer, interrupt line/pin, and latency/grant fields.
- PCIe capability list, PCIe device/link capability, control, and status registers.
- PCIe 2.0/3.0 capability extensions such as device capability/control/status 2 and link capability/control/status 2.
- MSI and MSI-X capability control, message address/data, mask, pending, table, and PBA fields.
- Vendor-specific enhanced capability headers and payload registers.
- Advanced Error Reporting capability headers, uncorrectable/correctable error status, masks, severities, AER capability/control, header logs, and TLP prefix logs.
- ATS capability/control and ARI capability/control fields for address translation and alternative routing ID support.

Because this file is generated hardware metadata, its main contract is exact symbolic naming, shift values, and masks. Runtime behavior depends on code that uses these masks with the corresponding `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets and with the correct NBIO instance/access path.

## Important Macro Families

VF8 tail:

- Lines 63891-64107 finish `BIF_CFG_DEV0_EPF0_VF8_0` AER, ATS, and ARI masks.
- AER uncorrectable status/mask/severity registers expose the common PCIe AER bits: data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked.
- Correctable AER status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow.
- AER logs use full-width `TLP_HDR` and `TLP_PREFIX` fields across four registers each.
- ATS fields include capability-list metadata, invalidate queue depth, page-aligned request support, global invalidate support, STU, and `ATC_ENABLE`.
- ARI fields include enhanced capability metadata, MFVC/ACS function-group capability bits, next function number, function-group enables, and the function-group selector.

VF9, VF10, and VF11 complete blocks:

- Each complete VF block starts with an address block marker such as `nbio_nbif0_bif_cfg_dev0_epf0_vf9_bifcfgdecp`.
- Standard PCI header fields use narrow masks for identity and class-code registers, byte-wide cache-line/latency/header-type style registers, and full 32-bit masks for BARs and CardBus CIS pointer fields.
- `COMMAND` exposes enable/policy bits for IO access, memory access, bus master, special cycle, memory write invalidate, palette snoop, parity response, SERR, fast back-to-back, and interrupt disable.
- `STATUS` exposes readiness, interrupt status, capability-list availability, PCI 66 MHz and fast back-to-back capability, parity and abort/error indications, and DEVSEL timing.
- `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` define the endpoint's PCIe capability contract, including max payload/read request sizing, phantom functions, extended tags, error reporting enables, relaxed ordering, no-snoop, auxiliary power, link speed/width, ASPM/L0s/L1 exit latencies, clock/power-management bits, retrain/common-clock/link-disable controls, and negotiated link status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover newer PCIe capability fields such as completion timeout ranges and controls, ARI forwarding, AtomicOp support/blocking, LTR, OBFF, EETLP prefix support, target link speeds, equalization controls, de-emphasis, and equalization status phases.
- MSI/MSI-X fields cover capability IDs and next pointers, MSI enable and multiple-message controls, 64-bit MSI address/data aliases, per-vector masking, pending bits, MSI-X table size/enable/mask, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields provide capability ID/version/next-pointer metadata, VSEC ID/revision/length, and two full-width vendor-specific payload registers.
- AER, ATS, and ARI families repeat the same field layout as the VF8 tail.

VF12 partial block:

- Lines 66204-66318 begin the `VF12` address block and define masks from vendor/device ID through `ROM_BASE_ADDR`.
- The rest of `VF12` is outside this chunk, so consumers and final merged documentation must combine this with the following chunk before treating `VF12` as complete.

## APIs, Types, And Data

This chunk defines no functions, structs, enums, storage objects, or callable APIs. Its exported interface is the preprocessor namespace:

- `BIF_CFG_DEV0_EPF0_VF{8,9,10,11,12}_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF{8,9,10,11,12}_0_<REGISTER>__<FIELD>_MASK`

The offset-side companion is `nbio_2_3_offset.h`, which defines matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. Within the checked offset header, representative offsets include standard PCI header locations (`VENDOR_ID` at `0x0000`, `COMMAND` at `0x0004`, `ROM_BASE_ADDR` at `0x0030`), PCIe capability offsets (`PCIE_CAP_LIST` at `0x0064`, `DEVICE_CNTL` at `0x006c`, `LINK_STATUS` at `0x0076`), MSI/MSI-X offsets (`MSI_CAP_LIST` at `0x00a0`, `MSIX_CAP_LIST` at `0x00c0`), AER offsets (`PCIE_ADV_ERR_RPT_ENH_CAP_LIST` at `0x0150`), ATS offsets (`PCIE_ATS_ENH_CAP_LIST` at `0x02b0`), and ARI offsets (`PCIE_ARI_ENH_CAP_LIST` at `0x0328`).

The offsets are config-space offsets within the generated VF config image. They must not be treated as ordinary MMIO register addresses without the correct NBIO/PCIe config access mechanism.

## Control Flow

There is no local control flow. At compile time, the preprocessor substitutes numeric shifts and masks. Runtime control flow is supplied by code that includes the NBIO 2.3 generated headers.

The direct include points found in this repository snapshot are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`

`nbio_v2_3.c` is the central NBIO 2.3 integration file. It uses the same generated header family to program NBIO/PCIe behavior such as memory-controller access, doorbell apertures and ranges, interrupt control, HDP flush/remap registers, PCIe link and ASPM/LTR policy, clock/light-sleep controls, and SR-IOV-aware register access. The specific VF9-VF12 config-space macro names in this chunk do not appear to be directly referenced by current in-tree C code found during this pass; they remain generated register contracts for SR-IOV VF configuration-space decode, firmware/PF management, diagnostics, and future or out-of-tree consumers.

`mxgpu_nv.c` is the Navi SR-IOV/MxGPU communication path. It includes the NBIO 2.3 masks while handling VF/PF runtime service state and message acknowledgement behavior, which is conceptually adjacent to these VF config-space definitions even when it does not directly touch this exact macro range.

The SMU11 PPT files include NBIO 2.3 masks for power-management and PCIe-related policy, such as reading NBIO straps and checking PCIe DPM feature state. Their direct usage is mostly outside the VF config-space names covered here.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe is hardware PCIe configuration-space state associated with SR-IOV virtual functions.

Important persistent or semi-persistent hardware state represented by this chunk includes:

- VF command/status enables and error latches. Access enable bits, bus mastering, interrupt disable, SERR/parity response, and status error bits directly affect VF enumeration, driver binding, DMA permission, and error handling.
- VF BARs and ROM base address fields. These determine the PCI resources exposed to a VF and must align with PF/SR-IOV resource allocation.
- MSI/MSI-X state. Message address/data, masks, pending bits, MSI-X table/PBA layout, and enable bits affect interrupt delivery and can persist until reset, function-level reset, VF reset, or PF reinitialization.
- PCIe device/link controls. Max payload/read request size, relaxed ordering, no-snoop, extended tags, link control, ASPM-related controls, completion timeout, LTR, and target link speed fields influence transaction behavior and link policy.
- AER state. Correctable and uncorrectable error status bits may be sticky until cleared, masks determine whether errors are surfaced, severity bits influence fatal/nonfatal classification, and header/TLP prefix logs capture error context.
- ATS/ATC state. ATS capability and `ATC_ENABLE` describe or control address-translation cache participation; incorrect state can affect IOMMU interaction and memory isolation.
- ARI state. ARI capability/control fields affect function numbering and routing behavior for multifunction or virtualized PCIe layouts.

This state is owned by hardware, firmware, the PF, host PCI core, and VF drivers depending on platform mode. It is not durable file-system state. It can be reset by device reset, FLR/VF reset, hot reset, suspend/resume reinitialization, or PF/firmware reprogramming.

## Dependencies

Generated-register dependencies:

- `nbio_2_3_offset.h` supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` config offsets.
- `nbio_2_3_default.h` supplies default values for other NBIO 2.3 registers, though this VF config-space chunk is primarily a shift/mask contract.
- Other chunks of `nbio_2_3_sh_mask.h` define PF fields, earlier VF blocks, and the rest of `VF8`/`VF12`.
- AMDGPU register helpers provide the actual access semantics and masking helpers. The same mask values are only meaningful when routed through the correct NBIO/PCIe config access path.

Driver and platform dependencies:

- SR-IOV ownership matters. PF, VF, firmware, and host PCI core may each own different parts of VF config-space state.
- Linux PCI and PCIe capability handling may program or validate many standard fields rather than AMDGPU touching every field directly.
- Host IOMMU/ATS policy determines whether ATS/ATC fields are usable for a VF.
- AER support depends on PCIe error reporting being enabled in the platform and kernel.
- MxGPU/SR-IOV paths depend on mailbox/runtime-service behavior outside this header, but the VF config-space layout must remain consistent with those virtualization flows.

## Integration Points

The practical integration point is the AMDGPU NBIO 2.3 register include tree:

- `nbio_v2_3.c` includes this header with the matching offset/default headers and uses the generated NBIO field names in PCIe, doorbell, interrupt, HDP, and power-management setup.
- `mxgpu_nv.c` integrates Navi SR-IOV runtime services and VF/PF communication while including the same generated NBIO 2.3 mask namespace.
- SMU11 power-management files include the NBIO 2.3 masks for NBIO straps and PCIe DPM policy.
- The generated `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets are aligned with this mask namespace and should be considered the authoritative companion data for any VF config-space access.
- Adjacent NBIO generations, including 6.1 and 7.4 in this tree, define very similar VF config-space names and offsets. That makes cross-generation naming familiar but also increases the risk of using the wrong generated header pair.

## Risks And Edge Cases

- Generation mismatch is the primary risk. Similar `BIF_CFG_DEV0_EPF0_VF*_0_*` names exist in other NBIO headers, but masks, offsets, ownership, and supported capabilities can differ by ASIC generation.
- This chunk is not a complete VF range. It starts after the beginning of `VF8` and ends before the end of `VF12`; merged per-file research must combine adjacent chunks before drawing whole-function conclusions for those VFs.
- Config offsets such as `0x006c` and `0x0150` are PCIe config-space offsets, not normal MMIO offsets. Using them with the wrong accessor can touch the wrong register or fail silently.
- MSI 32-bit and 64-bit layouts intentionally alias some offsets, for example message data and mask fields. Code must interpret the fields according to whether 64-bit MSI and per-vector masking are enabled.
- Sticky AER status bits and header logs require careful clear/read sequencing. Clearing too early loses diagnostic evidence; failing to clear can cause repeated error reporting.
- ATS/ATC enablement affects address translation and isolation. Enabling it without host/IOMMU support or PF policy coordination can break VF DMA behavior or isolation assumptions.
- ARI fields affect function routing and numbering. Incorrect ARI forwarding or function group programming can make VFs unreachable or misidentified.
- BAR and ROM base fields expose resources to VFs. Incorrect masks or writes can overlap resources, expose PF-owned apertures, or break VF driver probing.
- Some fields are standard PCIe capability state normally coordinated by the host PCI core. AMDGPU or firmware writes must avoid racing generic PCI config management.
- Hand-editing generated shift/mask headers is risky because build success does not prove hardware bit contracts are correct.

## Test And Verification Signals

Useful validation signals for this chunk are mostly compile coverage, static pairing checks, and SR-IOV/PCIe runtime inspection:

- Build AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, and the SMU11 PPT files against `nbio_2_3_offset.h` plus `nbio_2_3_sh_mask.h`.
- Run a static pairing check that every `BIF_CFG_DEV0_EPF0_VF{8,9,10,11,12}_0_*` register in this chunk has a matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offset where the covered register is complete.
- Validate that `VF9`, `VF10`, and `VF11` each expose the expected standard PCI, PCIe capability, MSI/MSI-X, VSEC, AER, ATS, and ARI register families with identical field layouts.
- Treat `VF8` and `VF12` as partial in chunk-local checks; do not report missing beginning/end registers until adjacent chunks are merged.
- On NBIO 2.3 SR-IOV-capable hardware, enumerate VFs and compare `lspci -vvv` capability decode for VF9-VF11 against the generated capability offsets and field masks.
- Exercise VF reset/FLR and confirm command/status, MSI/MSI-X, AER status/logs, ATS enable, and ARI state return to expected PF/firmware-configured values.
- Inject or observe PCIe AER events where platform support exists, then verify correctable/uncorrectable status, mask, severity, and header-log fields decode according to these masks.
- Enable VF MSI/MSI-X paths and confirm interrupt masking, pending bits, table/PBA offsets, and 64-bit MSI aliases behave as expected.
- If ATS is enabled for VFs, validate host IOMMU integration and DMA correctness before and after VF reset, suspend/resume, and PF-mediated reconfiguration.

### subset-b-002931: lines 66319-68739

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 66319-68739

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register mask header. It contains C preprocessor `#define` constants for bit shifts and masks in the NBIF/BIF PCI configuration decoder for SR-IOV virtual functions on device 0, endpoint function 0. The covered slice starts in the tail of the `VF12` configuration space, contains complete `VF13` and `VF14` address blocks, and ends in the early MSI-X fields of `VF15`.

The chunk is declarative: it defines register field names, bit positions, and masks. It does not define functions, structures, executable control flow, storage, or initialization logic.

## Purpose

The macros provide symbolic field encodings for NBIO PCIe configuration registers so driver code can read, write, compose, and decode MMIO or PCI config-space values without hard-coded bit constants. The repeated prefix layout is:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK`

For this chunk, `<n>` spans `12`, `13`, `14`, and `15`. These map the same PCI/PCIe capability and extended capability fields for multiple virtual functions. The constants are expected to be paired with register offset definitions from the companion NBIO register header, while this file supplies only per-field shifts and masks.

## Address Blocks and Register Coverage

The visible address block markers are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp` beginning at line 66900.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp` beginning at line 67596.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` beginning at line 68292.

The line range begins after the `VF12` block has already started. It includes the tail of `VF12`, beginning with `ROM_BASE_ADDR`/`CAP_PTR`-area fields and continuing through PCIe, MSI/MSI-X, vendor-specific, Advanced Error Reporting, ATS, and ARI capability fields. The line range ends before the `VF15` block reaches the vendor-specific, AER, ATS, and ARI definitions.

Major register groups covered:

- Basic PCI header fields for complete `VF13`, `VF14`, and partial `VF15`: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class-code fields, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability list and capability/control/status fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI and MSI-X capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data fields, mask and pending fields, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific PCIe extended capability fields for `VF12` through `VF14`: enhanced capability list header, vendor-specific header, and scratch registers.
- PCIe Advanced Error Reporting fields for `VF12` through `VF14`: enhanced capability list header, uncorrectable error status/mask/severity, correctable error status/mask, error capability/control, TLP header logs, and TLP prefix logs.
- ATS and ARI extended capability fields for `VF12` through `VF14`: ATS capability/control and ARI capability/control.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The usable interface is the macro namespace itself.

Important macro families:

- `*_COMMAND__*`: standard PCI command bits such as I/O access, memory access, bus mastering, SERR, and interrupt disable.
- `*_STATUS__*`: standard PCI status bits such as interrupt status, capability list support, abort indications, system error, and parity error.
- `*_BASE_ADDR_[1-6]__BASE_ADDR_*` and `*_ROM_BASE_ADDR__BASE_ADDR_*`: BAR/ROM BAR field masks.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*`: PCIe capability fields for payload/read request sizing, FLR, link width/speed, ASPM/PM controls, link retrain/disable, and equalization status.
- `*_MSI_*` and `*_MSIX_*`: interrupt capability programming fields for MSI enablement, 64-bit address support, vector masks/pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*`: AER status, mask, severity, ECRC, multi-header recording, and log-presence fields.
- `*_PCIE_ATS_*` and `*_PCIE_ARI_*`: address translation service and alternative routing-ID interpretation capability/control fields.

All constants use integer literal masks with an `L` suffix and hex shifts. Consumers should use the mask width implied by the register: many fields are 16-bit PCI capability words, while others are 32-bit extended capability or BAR/log registers.

## Control Flow

There is no runtime control flow. Inclusion is controlled by the surrounding header guard in the full file, outside this slice. At compile time, source files that include the generated NBIO headers gain access to these constants. Runtime behavior happens only in code that uses these macros to operate on hardware registers.

Typical consumer flow inferred from the macro design:

1. Read a PCIe config or NBIO register value through AMDGPU's register access helpers.
2. Use `*_MASK` and `*_SHIFT` to extract a field or prepare an updated value.
3. Write the composed value back to the register when enabling or disabling PCI/PCIe features.

## State and Persistence Behavior

This header stores no software state and performs no persistence. The state represented by the macros lives in hardware PCI configuration registers for SR-IOV VFs. Some fields are configuration bits that persist until reset or function-level reset, such as `BUS_MASTER_EN`, `MEM_ACCESS_EN`, MSI/MSI-X enables, ATS enable, ARI controls, completion timeout controls, and link-control bits. Other fields expose hardware status or write-one-to-clear-style error state in the PCIe/AER register model, such as device status, link status, correctable and uncorrectable error status, and header/TLP prefix logs.

Because this slice contains virtual-function config-space fields, state is sensitive to SR-IOV lifecycle events. VF reset, FLR, PF-driven virtualization setup, guest driver programming, and host PCI core policy can all change the underlying register contents independently of this header.

## Dependencies and Integration Points

Dependencies are mostly structural:

- The companion NBIO 2.3 register offset header supplies register addresses; this `_sh_mask.h` file supplies field encodings.
- AMDGPU register access macros and helpers use these constants to build `REG_SET_FIELD`, `REG_GET_FIELD`, or equivalent bitfield operations.
- Linux PCI/PCIe behavior is reflected in the field naming: the register layout follows standard PCI configuration header, PCIe capability, MSI/MSI-X capability, AER extended capability, ATS, and ARI definitions.
- SR-IOV support depends on the PF/VF hardware model. The repeated `VF12`, `VF13`, `VF14`, and `VF15` blocks are integration points for per-VF configuration decode windows.
- Interrupt setup integrates with MSI/MSI-X programming paths through `MSI_MSG_CNTL`, message address/data, mask/pending, MSI-X table, and PBA fields.
- Error handling and diagnostics integrate with PCIe AER paths through uncorrectable/correctable status/mask/severity fields and header/TLP prefix logs.
- IOMMU and address translation integration can use ATS fields: invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.

## Risks and Edge Cases

- Generated macro drift is the primary risk. If masks or shifts do not match the hardware register database for NBIO 2.3, all downstream bitfield reads/writes can silently target the wrong bits.
- The chunk boundaries are partial: `VF12` begins before this range and `VF15` continues after it. A final per-file reconciliation should avoid treating this chunk as a complete view of either VF block.
- The repeated VF blocks are intentionally near-identical. Copy-generation mistakes are hard to detect by review because most lines differ only by VF number.
- Several control bits can affect device availability or PCIe link behavior if used incorrectly, including `INITIATE_FLR`, `LINK_DIS`, `RETRAIN_LINK`, `HW_AUTONOMOUS_WIDTH_DISABLE`, `HW_AUTONOMOUS_SPEED_DISABLE`, MSI/MSI-X enables, ATS `ATC_ENABLE`, and ARI forwarding/function-group controls.
- AER registers include status, mask, and severity fields with similar names. Confusing these families can suppress reporting, misclassify errors, or clear/inspect the wrong status.
- Width handling matters. Some masks cover 8-bit, 16-bit, or 32-bit fields; consumers should avoid truncation or sign-extension assumptions around `L`-suffixed literals.
- BAR and MSI-X table/PBA fields carry address or offset encodings where low bits are either reserved or BIR selectors. Consumers must preserve reserved/selector bits as required by PCIe layout.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/driver integration checks:

- Compile coverage for files including `nbio_2_3_sh_mask.h`; undefined macro or duplicate-name issues should fail normal AMDGPU builds.
- Static consistency checks comparing this `_sh_mask.h` against the corresponding NBIO register-offset header and AMD hardware register database.
- Pattern checks across `VF12`, `VF13`, `VF14`, and `VF15` blocks to confirm that identical register families have identical field shifts/masks, except where the line-range boundary intentionally omits fields.
- Runtime smoke tests on hardware with SR-IOV enabled: enumerate VFs, bind guest/host drivers, enable memory and bus-master access, program MSI/MSI-X, and verify interrupts arrive.
- PCIe capability inspection with tools such as `lspci -vv` or driver debug dumps to confirm exposed payload size, FLR capability, link speed/width, AER, ATS, and ARI values line up with expected hardware behavior.
- Error-path tests that inject or observe PCIe AER conditions and verify correctable/uncorrectable status, masks, severity bits, and header logs decode correctly.
- Reset tests around VF FLR and PF-driven VF teardown/recreation to ensure status and control fields return to expected reset values.

### subset-b-002932: lines 68740-71163

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 68740-71163

## Scope

This chunk covers a generated AMD NBIO 2.3 register shift/mask header segment for PCIe configuration-space registers exposed for SR-IOV virtual functions. The range contains 2,137 `#define` entries across 275 register names. It starts in the middle of the `BIF_CFG_DEV0_EPF0_VF15_0_MSIX_PBA` field definitions, continues through the remaining VF15 PCIe extended capability definitions, covers complete generated PCI configuration bitfields for VF16, VF17, and VF18, and ends at `BIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1`.

The file is data-only C preprocessor material. It defines bit offsets and masks, not executable code. There are no functions, structs, enums, global variables, allocation sites, locks, or direct MMIO operations in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI used by AMDGPU NBIO/PCIe code when composing or decoding NBIO 2.3 BIF configuration registers for virtual functions. Each register field is represented with the usual generated-pair convention:

- `<REGISTER>__<FIELD>__SHIFT`, identifying the field's low bit.
- `<REGISTER>__<FIELD>_MASK`, identifying the field's bit mask in the register value.

The matching `nbio_2_3_offset.h` file supplies configuration offsets such as `cfgBIF_CFG_DEV0_EPF0_VF16_0_COMMAND`, `cfgBIF_CFG_DEV0_EPF0_VF18_0_PCIE_UNCORR_ERR_STATUS`, and `cfgBIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1`. This `*_sh_mask.h` file supplies the field encodings consumed by helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe/SMN register accessors in the AMDGPU tree.

## Important Macro Families

### Cross-Chunk VF15 Tail

The chunk begins after the VF15 MSI-X table fields and includes the tail of `BIF_CFG_DEV0_EPF0_VF15_0_MSIX_PBA`, whose fields describe the MSI-X pending bit array BAR indicator and table offset. It then covers VF15 vendor-specific and advanced PCIe capabilities:

- Vendor-specific enhanced capability list fields: `CAP_ID`, `CAP_VER`, and `NEXT_PTR`.
- Vendor-specific header fields: `VSEC_ID`, `VSEC_REV`, and `VSEC_LENGTH`.
- Two 32-bit vendor-specific scratch registers.
- Advanced Error Reporting (AER) capability list, uncorrectable/correctable error registers, AER capability/control, header log, and TLP prefix log registers.
- Address Translation Services (ATS) capability/control fields.
- Alternative Routing-ID Interpretation (ARI) capability/control fields.

Because the chunk starts mid-register at line 68740, the full VF15 MSI/MSI-X and basic PCIe capability story belongs partly to the previous chunk.

### Complete VF16, VF17, and VF18 PCI Header Fields

For VF16, VF17, and VF18, this chunk repeats a complete Type 0 PCI configuration header field layout. The basic header definitions include:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: `COMMAND` and `STATUS`.
- Header and timing fields: `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `MIN_GRANT`, and `MAX_LATENCY`.
- BAR and pointer fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, and `CAP_PTR`.
- Interrupt routing fields: `INTERRUPT_LINE` and `INTERRUPT_PIN`.

Important command/status bits include IO access, memory access, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, fast back-to-back, interrupt disable, interrupt status, capability-list presence, target/master abort indications, system error, and parity-detected status.

### PCIe Capability and Link Management

For VF16, VF17, and VF18, the `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` families model standard PCIe capability structure fields. The chunk also includes the PCIe 2.0+ companion registers `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.

These definitions cover device capabilities and controls such as payload size, phantom function support, extended tag support, L0s/L1 latency, attention/power indicators, role-based error reporting, FLR support, completion timeout support/control, ARI forwarding support, atomic operation routing/completer support, TPH completer support, end-end TLP prefix support, emergency power reduction fields, IDO request/completion enablement, LTR enablement, OBFF, and atomic operation egress blocking. Link fields cover link speed, width, ASPM, read completion boundary, clock management, retrain/link disable, common clock, extended sync, hardware autonomous width/speed disable, link bandwidth management/status, and current/de-emphasized speed reporting.

### MSI and MSI-X

VF16, VF17, and VF18 each include MSI and MSI-X capability definitions:

- MSI capability list and message control fields such as message enable, multi-message capability/enable, 64-bit address support, per-vector masking, extended data capability, and extended data enable.
- MSI address/data, mask, and pending-register fields for both 32-bit and 64-bit layouts.
- MSI-X capability list and message control fields, including table size, function mask, and MSI-X enable.
- MSI-X table and pending bit array fields, each split into BAR indicator and offset fields.

These are configuration-space definitions for interrupt delivery resources. The actual interrupt setup is implemented elsewhere; this chunk only supplies field positions.

### Vendor-Specific and Advanced Error Reporting

For VF16, VF17, and VF18, and for the VF15 tail, this chunk defines PCIe vendor-specific and AER fields:

- Vendor-specific capability list and header fields for capability ID/version/next pointer, VSEC ID/revision/length, and scratch registers.
- AER capability list fields.
- Uncorrectable error status, mask, and severity fields for data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.
- Correctable error status/mask fields for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.
- AER capability/control fields for first error pointer, ECRC generation/checking capability and enable bits, multiple header recording, TLP prefix log presence, and completion timeout log capability.
- Four 32-bit header-log registers and four 32-bit TLP-prefix-log registers.

The status/mask/severity triad is especially important because the same bit positions are intentionally repeated across status, mask, and severity registers.

### ATS and ARI

The chunk includes ATS and ARI enhanced capability definitions for VF15 through VF18:

- ATS enhanced capability list: capability ID, version, and next pointer.
- ATS capability: invalidate queue depth, page-aligned request support, and global invalidate support.
- ATS control: smallest translation unit (`STU`) and address translation cache enable (`ATC_ENABLE`).
- ARI enhanced capability list: capability ID, version, and next pointer.
- ARI capability: MFVC function group capability, ACS function group capability, and next function number.
- ARI control: MFVC/ACS function group enables and function group selection.

These fields are relevant to IOMMU/translation behavior and PCIe function enumeration in virtualized configurations.

### VF19 Beginning

The final portion starts `nbio_nbif0_bif_cfg_dev0_epf0_vf19_bifcfgdecp` and includes VF19 definitions through `BASE_ADDR_1`. Covered fields include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class fields, cache line, latency, header type/device type, BIST, and the first BAR. The rest of VF19 continues in the next chunk.

## Control Flow and State Behavior

This header has no runtime control flow. It affects generated object code only through C preprocessor constants that become operands to AMDGPU register-helper macros.

The state described by this chunk is hardware PCIe/NBIO configuration state, not persistent software state in the header. Important state categories include VF command enables, error/status bits, class and BAR configuration, interrupt capability state, MSI/MSI-X table/PBA locations, link capability/control/status, AER status/mask/severity/log registers, ATS enablement, and ARI function grouping.

Some defined fields represent writable controls, some represent read-only capabilities, and some represent sticky or clear-on-write hardware status bits depending on the PCIe specification and NBIO implementation. The generated masks do not encode those access semantics. Callers must rely on the surrounding NBIO, PCI core, SR-IOV, and hardware sequencing rules when reading, writing, clearing, or polling these fields.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header set:

- `nbio_2_3_offset.h` provides the matching `cfgBIF_CFG_DEV0_EPF0_VF*` register offsets.
- `nbio_2_3_default.h` provides default values for the same NBIO generation where generated defaults exist.
- AMDGPU register helper macros consume these `__SHIFT` and `_MASK` definitions to avoid hard-coded bit positions.

Observed local include sites for NBIO 2.3 headers include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h` and implements NBIO register access, memory-controller access enablement, doorbell aperture setup, interrupt control, clock gating, link control, and SR-IOV-aware behavior.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes the NBIO 2.3 offset and mask headers for Navi SR-IOV mailbox and virtualization support.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include NBIO 2.3 headers from SMU policy code.
- Display resource files such as `dcn20_resource.c` and `dcn303_resource.c`, which include the matching NBIO offset header where display bring-up needs NBIO register addresses.

Direct textual references to the exact VF15-VF19 field names in this chunk were not found in the nearby AMDGPU, SMU, or display C files during this pass. That is expected for generated config-space VF definitions: they may be used by generic helper code, diagnostics, firmware-facing tooling, out-of-tree consumers, or retained as a complete hardware register map even when a particular in-tree path does not touch every generated field.

## Risks

- Bitfield drift is high impact. An incorrect shift or mask can program the wrong PCIe configuration bits for a VF, affecting bus mastering, memory decoding, interrupts, AER behavior, ATS, ARI, or link controls.
- The repeated VF16/VF17/VF18 blocks are mechanically similar but must remain exactly aligned with their matching offsets. Copy/paste or generator errors can silently make one VF's field constants point at another VF's semantics.
- AER status, mask, and severity registers intentionally share many field positions. Mixing status/mask/severity macro names can hide real errors, over-report errors, or classify fatal/non-fatal conditions incorrectly.
- MSI and MSI-X offsets, table BAR indicators, and PBA fields are sensitive because interrupt routing depends on exact table placement and masking behavior.
- ATS and ARI controls are virtualization- and IOMMU-sensitive. Incorrect `ATC_ENABLE`, `STU`, function group, or next-function-number handling can break address translation, enumeration, or isolation assumptions.
- PCIe capability fields include both capability bits and control bits. Treating read-only capability fields as writable policy fields can result in ineffective writes or confusing diagnostics.
- The chunk starts and ends across register-family boundaries. VF15 is incomplete at the start, and VF19 is incomplete at the end; final analysis must merge adjacent chunks before making per-file completeness claims.

## Test and Validation Signals

Useful validation is mainly build, register-access, and hardware integration coverage:

- Compile AMDGPU with NBIO 2.3 users enabled; this catches missing, renamed, or syntactically malformed generated macros.
- Exercise NBIO v2.3 initialization paths in `nbio_v2_3.c`, including memory access enablement, interrupt setup, doorbell aperture/range programming, clock-gating policy, and PCIe link handling.
- Run SR-IOV VF bring-up and teardown on Navi/NBIO 2.3 hardware, checking that VFs enumerate with expected vendor/device/class fields, command/status behavior, BARs, and capability chains.
- Validate MSI and MSI-X interrupt delivery for VFs, including vector masking, function masking, table/PBA placement, and pending-bit behavior.
- Inject or observe PCIe AER correctable and uncorrectable conditions, then confirm status, mask, severity, header log, and TLP prefix log decoding matches hardware expectations.
- Validate ATS and ARI behavior under an IOMMU with SR-IOV enabled, including ATC enablement, invalidate queue depth reporting, function grouping, and enumeration.
- Compare the generated masks against the vendor register specification or a known-good generated NBIO 2.3 header when updating the file, especially across the repeated VF16-VF18 blocks.

## Unresolved Cross-Chunk References

The first complete comment in this chunk is `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, but the actual line range begins with the final `BIF_CFG_DEV0_EPF0_VF15_0_MSIX_PBA` shift/mask entries. The preceding VF15 header, PCIe, MSI, and MSI-X definitions belong to the previous chunk.

The range ends after `BIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1`. The remaining VF19 BARs, capability lists, PCIe capability fields, MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions continue in the next chunk.

### subset-b-002933: lines 71164-73585

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 71164-73585

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header slice. It contains C preprocessor constants for PCI configuration-space fields, not executable code. Each register field is represented by a `BIF_CFG_DEV0_EPF0_VF*_0_*__FIELD__SHIFT` macro and a matching `BIF_CFG_DEV0_EPF0_VF*_0_*__FIELD_MASK` macro.

The range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF19_0` block at `BASE_ADDR_1`, then covers the rest of VF19, all of VF20 and VF21, and most of VF22 through `PCIE_ARI_CNTL`. The explicit address-block anchors in the chunk are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf20_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf21_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf22_bifcfgdecp`

The chunk includes 2,416 comment or `#define` lines and describes repeated PCIe capability layouts for SR-IOV virtual functions 19-22 on device 0, endpoint function 0.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield contract between AMDGPU/NBIO code and NBIO 2.3 hardware registers. This chunk describes PCI configuration-space fields for late SR-IOV virtual functions. It lets C code, firmware-facing tooling, register decoders, and diagnostics compose or decode config-space dwords without hard-coding bit positions.

The fields cover:

- PCI header identity and class fields: vendor/device ID, command/status, revision, class/subclass/programming interface, cache line, latency, header type, BIST, BARs, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI Express capability fields: capability list, device/link capabilities, device/link control, device/link status, and the PCIe capability version/device type/interrupt-message metadata.
- PCIe capability 2 fields: completion timeout, ARI forwarding, atomic operation support, ID-based ordering, latency tolerance reporting, optimized buffer flush/fill, 10-bit tags, TLP prefix support, emergency power reduction, FRS support, target link speed, compliance, equalization, crosslink, DRS, and RTM presence bits.
- MSI/MSI-X capability fields: MSI enable, multiple-message capability/enable, 64-bit MSI, per-vector masking, MSI address/data/mask/pending registers, MSI-X table size, function mask, enable, table BAR indicator/offset, and PBA BAR indicator/offset.
- Vendor-specific PCIe extended capability fields: extended capability ID/version/next pointer, VSEC ID/revision/length, and two scratch dwords.
- Advanced error reporting fields: uncorrectable and correctable error status/mask/severity bits, ECRC and header-log capability/control bits, first error pointer, TLP header logs, and TLP prefix logs.
- ATS and ARI extended capability fields: ATS capability/control and ARI capability/control, including invalidate queue depth, page-aligned request, global invalidate support, STU, ATC enable, next-function number, function-group capability, and function-group enable.

The macros are generated hardware metadata. Their correctness depends on exact naming, shifts, masks, and pairing with the matching offset/default headers for NBIO 2.3.

## Important API Surface

There are no functions, structs, enums, or local types. The public surface is the preprocessor namespace consumed by AMDGPU register helpers and config-space tooling.

Repeated VF blocks:

- VF19 is boundary-partial in this chunk: its `VENDOR_ID` through the start of `BASE_ADDR_1` appear immediately before the requested range. This chunk covers VF19 BARs, legacy PCI header tail, PCIe capability, MSI/MSI-X, VSEC, AER, ATS, and ARI fields.
- VF20 and VF21 are complete in this range from `VENDOR_ID` through `PCIE_ARI_CNTL`.
- VF22 is complete from `VENDOR_ID` through `PCIE_ARI_CNTL` within the requested range.

Core config header fields:

- `VENDOR_ID` and `DEVICE_ID` expose 16-bit ID fields.
- `COMMAND` includes IO, memory, bus-master, special-cycle, memory-write-invalidate, VGA palette snoop, parity response, SERR, fast back-to-back, interrupt disable, INTx emulation disable, and bus-master P2P disable bits.
- `STATUS` exposes legacy PCI status flags such as interrupt status, capability list, parity, DEVSEL timing, target/master abort, SERR, and parity error detected.
- `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS` encode PCI class identity.
- `HEADER` separates header type from the multifunction/device-type bit, and `BIST` exposes completion/start/capability bits.
- `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, and `ROM_BASE_ADDR` are full-width address fields.
- `ADAPTER_ID` packs subsystem vendor ID and subsystem ID.

PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` define capability ID, next pointer, version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` expose payload size, phantom functions, extended tags, L0s/L1 acceptable latency, role-based error reporting, slot power limit/scale, FLR capability/initiation, error enables/status, relaxed ordering, no-snoop, max read request size, auxiliary power, pending transactions, and emergency power-reduction detection.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` expose link speed/width, ASPM/PM support, exit latencies, clock power management, surprise-down and data-link-layer active reporting, bandwidth notifications, port number, retrain/link-disable/common-clock controls, DRS signaling, current speed/width, training, slot clock, data-link active, and bandwidth status bits.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` cover completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS, and reserved status bits.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover supported/target link speeds, compliance, autonomous speed disable, deemphasis, Gen3 equalization phases, RTM presence, crosslink resolution, downstream component presence, and DRS messages.

Interrupt capability fields:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO/HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, and `MSI_PENDING_64` describe both 32-bit and 64-bit MSI layouts. Notably, the low MSI address field starts at bit 2 and masks with `0xFFFFFFFCL`.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` define MSI-X capability metadata, table size, function mask, enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

Extended capability fields:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` expose VSEC list metadata, VSEC ID/revision/length, and scratch registers.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0-3`, and `PCIE_TLP_PREFIX_LOG0-3` define the AER reporting surface for uncorrectable/correctable PCIe errors and captured packet headers.
- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` define ATS metadata, invalidate queue capability, page-aligned request support, global invalidate support, STU, and ATC enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` define ARI metadata, function-group capabilities, next-function number, and function-group controls.

## Control Flow and Runtime Use

This header has no executable control flow. Runtime behavior is supplied by code that includes the generated NBIO 2.3 headers and performs PCIe/NBIO register access.

The usual flow for these macros is:

1. Select the matching config-space offset from `nbio_2_3_offset.h`, such as `cfgBIF_CFG_DEV0_EPF0_VF20_0_VENDOR_ID` at `0x0000`, `cfgBIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1` at `0x0010`, or `cfgBIF_CFG_DEV0_EPF0_VF22_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST` at `0x0150`.
2. Read a 16-bit or 32-bit config-space value through the appropriate NBIO/PCIe access path.
3. Decode with `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, or update by clearing the mask and shifting the new field value into place.
4. Write the value back only when the field is writable and when PF/VF ownership permits the access.

In this repository snapshot, direct references to the late-VF macro names are not present in the main C consumers. The header is still included by `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`. Those files mostly use NBIO 2.3 register helpers and non-VF or SMN names for PCIe link, LTR, doorbell, HDP flush, clock-gating, and virtualization-related control. The VF19-22 definitions therefore act as generated ABI coverage for register decoders, diagnostics, firmware/PF management paths, and future code rather than as heavily used in-tree C symbols in this snapshot.

## State and Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe is PCI configuration and PCIe extended capability state for SR-IOV virtual functions in NBIO hardware.

Important hardware state represented by this chunk includes:

- BAR and ROM BAR registers, which define MMIO aperture exposure for each VF. These values persist in config space until reset, FLR, PF/firmware reconfiguration, or OS PCI resource assignment changes them.
- Command register bits, which govern memory/IO decode, bus mastering, SERR, parity behavior, interrupt disable, and VF-specific forwarding controls. Incorrect persistence here can make a VF unable to DMA or can leave decode enabled when it should be disabled.
- Device/link control state, including max payload, max read request, relaxed ordering, no-snoop, FLR initiation, link disable/retrain/common-clock/autonomous width/speed controls, target link speed, and compliance settings.
- Device/link status and AER status/log fields, which are live hardware status surfaces. Some error status bits may be write-one-to-clear depending on PCIe semantics, and captured header/TLP prefix logs preserve diagnostic data until cleared or overwritten.
- MSI/MSI-X state, including enable bits, MSI address/data, vector masks, pending bits, MSI-X function mask, table size, table location, and PBA location. These fields coordinate with host interrupt programming and must remain consistent with OS/PCI core ownership.
- ATS and ARI state, which affects address translation services, ATC enablement, STU programming, and function routing/grouping for virtualization.
- VSEC scratch registers, which may be used by firmware, PF management, diagnostics, or virtualization workflows as device-specific coordination state.

`nbio_2_3_default.h` provides reset/default values for these config fields. Examples found near this chunk's companion definitions include default zeroes for VF BAR/ID fields and `0x20020000` for `cfgBIF_CFG_DEV0_EPF0_VF22_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST_DEFAULT`. Any initialization or validation code should use the default header rather than inferring reset values from masks.

## Dependencies and Integration Points

Generated-register dependencies:

- `nbio_2_3_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. Many VF blocks reuse standard PCI config offsets, so the register name and selected VF address block are both part of the identity.
- `nbio_2_3_default.h` supplies matching `cfg..._DEFAULT` reset values.
- Other parts of `nbio_2_3_sh_mask.h` define adjacent VF blocks and the non-VF/PF NBIO fields used by the same include consumers.

Driver and subsystem integration:

- `amdgpu/nbio_v2_3.c` includes this header and implements NBIO 2.3 behavior for doorbell ranges, HDP flush registers, PCIe link controls, LTR controls, medium-grain clock gating, and related NBIO function-table hooks.
- `amdgpu/mxgpu_nv.c` includes the same header for Navi virtualization support, making the SR-IOV VF config-space layout relevant to PF/VF management even when the exact late-VF macros are not referenced by name in this file.
- SMU11 files include NBIO 2.3 masks for platform and power-management interactions with PCIe/NBIO state.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, and SOC15 offset helpers are the normal access style for nearby NBIO fields. Config-space users must still choose the access path that is valid for `cfg...` registers.
- Linux PCI core, SR-IOV enablement, VF assignment, IOMMU/ATS policy, and interrupt setup all interact with the same config-space concepts described by this generated header.

## Risks and Edge Cases

- This chunk starts mid-register-family for VF19. A final per-file report must merge the previous chunk to document VF19 identity, command/status, class, header, and `BASE_ADDR_1` start completely.
- VF20, VF21, and VF22 repeat almost identical field names. Copying a mask from the wrong VF block is compile-time valid if the symbol exists, but semantically points at a different virtual function.
- Offset/mask generation mismatch is high risk. These masks must be paired with `nbio_2_3_offset.h`; using NBIO 2.3 masks with another NBIO generation or a nonmatching offset header can silently decode or program wrong bits.
- PCI config-space fields are not uniformly 32-bit. Some capability registers are byte or word-sized by PCI layout, while the generated macros use C integer masks. Access width and alignment must match the hardware/config mechanism.
- BAR, ROM BAR, MSI/MSI-X, ATS, ARI, and command bits are OS/PF-owned in many configurations. Driver or debug writes outside the owner path can break VF assignment, DMA isolation, or interrupt delivery.
- AER status/log fields are diagnostic state. Clearing status or overwriting masks/severity while error handling is active can hide root-cause data or change whether errors are reported as fatal/nonfatal/correctable.
- `DEVICE_CNTL__INITIATE_FLR` and completion-timeout controls affect reset and transaction behavior. Incorrect programming can strand pending transactions or reset a VF unexpectedly.
- ATS/ATC enablement must be coordinated with IOMMU and host support. Enabling ATS for a VF without the right platform policy can compromise correctness or isolation.
- MSI 32-bit and 64-bit layouts intentionally alias some config offsets in the companion offset header. Code must select fields according to `MSI_64BIT` capability rather than assuming both layouts are independently present.
- Link capability/control/status fields may reflect shared physical link state, not per-VF independent hardware. Treating VF link fields as freely programmable can conflict with PF-controlled link management.

## Test and Verification Signals

- Build AMDGPU configurations that include `nbio_2_3_sh_mask.h` and the NBIO 2.3 consumers to catch missing or renamed generated macros.
- Static generation checks should verify that every `BIF_CFG_DEV0_EPF0_VF19_0` through `VF22_0` shift macro in this range has a matching mask macro and a companion `cfg...` offset in `nbio_2_3_offset.h`.
- Compare defaults in `nbio_2_3_default.h` with readback after cold reset or PF reinitialization on matching Navi/NBIO 2.3 hardware.
- In SR-IOV enablement tests, enumerate VFs and confirm vendor/device/class/capability-list fields decode as expected for VF19-22.
- Validate BAR assignment and command register transitions through the Linux PCI core: memory decode and bus mastering should follow VF bind/unbind and assignment state.
- Exercise MSI and MSI-X enable paths for VFs and confirm message address/data, vector mask, pending bits, MSI-X table/PBA locations, and function mask behavior match the generated masks.
- Trigger or inject PCIe correctable and uncorrectable error paths where supported, then verify AER status, mask, severity, first-error pointer, header log, and TLP prefix log decoding.
- Test VF FLR and reset flows and confirm `DEVICE_STATUS__TRANSACTIONS_PEND`, `DEVICE_CNTL__INITIATE_FLR`, AER logs, MSI state, and BAR/command state return to expected post-reset values.
- Validate ATS and ARI exposure under an IOMMU-enabled SR-IOV setup, including ATS capability/control fields and ARI next-function/function-group fields.
- Run register-decode or golden-register tooling against these macros using the NBIO 2.3 offset/default headers to detect drift from AMD's generated register source.

### subset-b-002934: lines 73586-76008

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 73586-76008

## Scope

This chunk covers a generated NBIO 2.3 shift/mask header range for AMDGPU PCIe/NBIO configuration-space registers. It starts in the middle of the `BIF_CFG_DEV0_EPF0_VF22_0` MSI/MSI-X and PCIe extended capability definitions, covers complete virtual-function configuration mask blocks for `VF23`, `VF24`, and `VF25`, and ends at the `BIF_CFG_DEV0_EPF0_VF26_0_PROG_INTERFACE` comment after defining the first `VF26` standard PCI configuration fields.

The file is a preprocessor-only register bitfield map. This chunk defines constants only: no C functions, structs, variables, storage, or executable control flow are present here.

## Purpose

The purpose of this section is to expose bit positions and masks for NBIO/BIF PCI configuration registers associated with SR-IOV virtual functions. Each field follows the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the mask for extracting or composing that field.

The sibling offset header supplies register addresses; this `*_sh_mask.h` header supplies the field encodings used with AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`. Local includes of `nbio/nbio_2_3_sh_mask.h` appear in `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`, so these macros can be consumed by NBIO control, SR-IOV, and platform/power code that needs SOC15 register field encodings.

## Important Macro Families

### VF22 Tail: MSI-X, Vendor Capability, AER, ATS, and ARI

The chunk begins at line 73586 with the tail of `BIF_CFG_DEV0_EPF0_VF22_0`. Covered `VF22` definitions include:

- MSI pending and 64-bit pending/mask fields.
- MSI-X capability list, message control, table, and pending bit array fields, including table size, function mask, enable bit, BAR indicator register fields, and table/PBA offsets.
- PCIe vendor-specific enhanced capability list/header fields with `CAP_ID`, `CAP_VER`, `NEXT_PTR`, `VSEC_ID`, `VSEC_REV`, and `VSEC_LENGTH`.
- Vendor scratch registers `PCIE_VENDOR_SPECIFIC1` and `PCIE_VENDOR_SPECIFIC2`.
- PCIe Advanced Error Reporting capability list plus uncorrectable status, uncorrectable mask, uncorrectable severity, correctable status, correctable mask, advanced error capability/control, TLP header logs, and TLP prefix logs.
- ATS enhanced capability, ATS capability/control, ARI enhanced capability, ARI capability, and ARI control fields.

The AER groups use the standard PCIe error bit families: data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic operation egress blocked, and TLP prefix blocked. For each field, this header provides the same bit position across status, mask, and severity registers.

### Complete VF23, VF24, and VF25 Blocks

Lines 73860-75947 define full `addressBlock` sections for `nbio_nbif0_bif_cfg_dev0_epf0_vf23_bifcfgdecp`, `vf24_bifcfgdecp`, and `vf25_bifcfgdecp`. These three blocks are structurally repetitive and map a virtual function's PCI/PCIe configuration-space view.

The standard PCI header fields include:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: I/O access, memory access, bus mastering, special cycle, memory write invalidate, palette snoop, parity response, SERR, fast back-to-back, interrupt disable, interrupt status, capability-list presence, target/master abort status, system error, parity error, and DEVSEL timing.
- Header/runtime fields: cache line, latency, header type, BIST, six base address registers, CardBus CIS pointer, adapter/subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.

The PCIe capability portions include:

- `PCIE_CAP_LIST` and `PCIE_CAP`, with capability ID/next pointer, PCIe capability version, device/port type, slot/interrupt-message number, and related capability metadata.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS`, covering max payload, phantom functions, extended tag, endpoint L0s/L1 latency, attention/button/power indicators, role-based error reporting, captured slot power limits, correctable/non-fatal/fatal/unsupported-request error enables, relaxed ordering, max payload/request sizing, no-snoop, auxiliary power, transactions pending, and related status bits.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`, covering supported link speed/width, ASPM and L0s/L1 exit latency, clock power management, surprise-down reporting, data-link active reporting, port number, common clock, retraining, disable, link bandwidth management, negotiated speed/width, training state, slot clock, and bandwidth notification state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, covering completion timeout support/control, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tag support, end-to-end TLP prefixes, emergency power reduction, supported/current/deemphasis link speeds, equalization controls, compliance/SOS vectors, and equalization phase completion bits.

### Interrupt Capability Fields

For `VF23` through `VF25`, the chunk defines MSI and MSI-X register masks:

- MSI capability list and message control fields encode capability ID, next pointer, MSI enable, multi-message capable/enable, 64-bit address capability, per-vector masking capability, and extended message data capability.
- MSI message address low/high, message data, mask, mask64, pending, pending64, and 64-bit message-data fields are represented as full-width payload masks where appropriate.
- MSI-X capability list and message control fields encode table size, function mask, and MSI-X enable.
- MSI-X table and PBA fields split BAR indicator register bits from table/PBA offsets.

These masks are the low-level contract used when driver code reads, mirrors, masks, or composes virtual-function interrupt capability registers. The header does not decide policy such as whether MSI/MSI-X is enabled; it only describes field layout.

### PCIe Advanced Error Reporting

For each complete VF block, the chunk defines:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, with enhanced capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`, sharing the same uncorrectable error bit layout.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`, with receiver, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal, and header-log-overflow fields.
- `PCIE_ADV_ERR_CAP_CNTL`, including first error pointer, ECRC generation/check capability and enable bits, multiple-header recording capability/enable bits, TLP-prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3`, each exposing full 32-bit captured log words.

AER status and log registers are hardware stateful: status bits may be sticky or clear-on-write according to PCIe/NBIO behavior, while log registers capture error context. These macros do not encode clear semantics or ordering; consumers must follow the PCIe/AER handling code and hardware specification.

### ATS and ARI

For `VF23` through `VF25`, ATS definitions include:

- `PCIE_ATS_ENH_CAP_LIST`, with enhanced capability ID/version/next pointer fields.
- `PCIE_ATS_CAP`, with invalidate queue depth, page-aligned request, and global invalidate support.
- `PCIE_ATS_CNTL`, with smallest translation unit and ATC enable.

ARI definitions include:

- `PCIE_ARI_ENH_CAP_LIST`, with enhanced capability ID/version/next pointer fields.
- `PCIE_ARI_CAP`, with MFVC and ACS function-group capability bits plus next function number.
- `PCIE_ARI_CNTL`, with MFVC/ACS function-group enables and function group selection.

These fields integrate NBIO virtual functions with PCIe address translation and alternate routing capabilities. Incorrect interpretation can affect IOMMU/ATS enablement, function enumeration, or virtual-function routing behavior.

### VF26 Prefix

Lines 75948-76008 begin the `VF26` address block and define its first standard configuration fields:

- `VENDOR_ID` and `DEVICE_ID`.
- `COMMAND`, with I/O, memory, bus-master, special-cycle, memory-write-invalidate, palette-snoop, parity-response, SERR, fast-back-to-back, and interrupt-disable fields.
- `STATUS`, with interrupt/status, capability-list, error, abort, DEVSEL, readiness, and parity fields.
- `REVISION_ID`.

The chunk ends at the `PROG_INTERFACE` comment before that field's `SHIFT` and `MASK` definitions, so the remainder of the `VF26` block belongs to the next chunk.

## APIs, Types, and Functions

There are no callable APIs, types, or functions in this chunk. The exported interface is the macro namespace itself. Its naming encodes register ownership:

- `BIF_CFG_DEV0_EPF0` identifies the bus interface configuration space for device 0, endpoint function 0.
- `VF22`, `VF23`, `VF24`, `VF25`, and `VF26` identify SR-IOV virtual-function configuration blocks.
- The trailing register and field names identify the PCI, PCIe, MSI/MSI-X, AER, ATS, ARI, or vendor-specific register field.

The macros are compile-time constants. They are normally paired with register offsets from the matching NBIO 2.3 offset header and with common AMDGPU register manipulation helpers.

## Control Flow and State Behavior

This header section has no runtime control flow. Its effect is indirect: driver C code includes it, then uses the constants to read or write individual bitfields in NBIO/PCIe hardware registers.

The state represented here is hardware or PCI configuration-space state, not persistent software state in the header. Important state classes include:

- VF identity, class, command, status, BAR, ROM, interrupt, and capability-pointer fields.
- PCIe link/device capabilities and controls, including link speed/width, payload sizes, ASPM, retraining, error reporting, ordering, atomics, LTR, OBFF, and equalization.
- MSI/MSI-X address/data/mask/pending/table/PBA configuration.
- AER status, masks, severity, capability control, and captured TLP/prefix logs.
- ATS and ARI capability/control state.
- Vendor-specific capability metadata and scratch fields.

Some fields are ordinary read/write controls, some are read-only capabilities, and some are status/log fields with hardware-defined clear or latch behavior. The macro file does not distinguish access type; that knowledge must come from the hardware specification and the driver paths that use the fields.

## Dependencies and Integration Points

The chunk depends only on the C preprocessor and the broader AMDGPU register-header convention. It has no include dependencies beyond the guard surrounding the full header.

Integration points visible in the tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes the NBIO 2.3 register headers for NBIO programming.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes the same header family for SR-IOV/MxGPU paths.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include NBIO 2.3 masks alongside SMU11 power-management code.
- Matching NBIO offset headers, which provide register addresses for the mask/shift names defined here.
- AMDGPU register helper macros that consume `__SHIFT` and `_MASK` values to compose and extract fields.

Because this range is deeply repetitive across virtual functions, generated consistency with adjacent `VF` blocks is part of the integration contract. A wrong value in one VF block can make code touch or decode a different bit than the same-named field in neighboring VFs.

## Risks

- Generated-header drift is the main risk. If the mask header and matching offset/header generation are out of sync with the ASIC register database, driver code will compile but program the wrong bitfields.
- The chunk starts and ends mid-block. Merge/reconciliation must preserve that `VF22` is partial at the start and `VF26` is partial at the end; whole-file research should not infer that those VF blocks are complete from this chunk alone.
- Many fields describe privileged or virtualized PCIe state. Misprogramming `COMMAND`, bus mastering, BARs, MSI/MSI-X, ATS, ARI, or AER masks can break VF enumeration, interrupt delivery, DMA, IOMMU translation, error handling, or isolation.
- AER and interrupt status fields may have sticky or write-one-to-clear behavior in hardware. The macros alone cannot prevent unsafe read-modify-write sequences.
- Repetition across `VF23`, `VF24`, and `VF25` makes copy/generation errors hard to notice in review; automated comparisons against the source register database or neighboring VF blocks are more reliable than manual inspection.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Kernel/driver build coverage for files including `nbio_2_3_sh_mask.h`; macro spelling or duplicate-definition problems should surface at compile time.
- Static checks or generated-header comparison against AMD's NBIO 2.3 register source data, especially for repeated VF blocks.
- SR-IOV smoke tests that enumerate VFs around this range and verify PCI config space identity, command/status, BARs, MSI/MSI-X capability layout, and capability-list traversal.
- Interrupt tests that exercise MSI and MSI-X enable/mask/pending paths for VFs.
- PCIe AER tests or fault-injection diagnostics that confirm correct decoding of correctable/uncorrectable status, masks, severity, and header-log fields.
- ATS/ARI enablement tests under IOMMU/SR-IOV configurations, checking that ATC enable, STU, next-function, and ARI function-group fields are interpreted consistently.
- Register readback tests comparing `REG_GET_FIELD` extraction against expected raw config-space values for representative `VF23`, `VF24`, and `VF25` registers.

### subset-b-002935: lines 76009-78432

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 76009-78432

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header slice for SR-IOV virtual-function PCI configuration-space fields. It contains C preprocessor constants only. There are no functions, structs, variables, allocations, locks, branches, loops, I/O calls, or direct MMIO transactions in this range.

The source range starts partway through `BIF_CFG_DEV0_EPF0_VF26_0_*`, after the earlier VF26 identity/command/status/revision fields. It then covers the remainder of VF26, complete VF27 and VF28 PCI/PCIe configuration bitfield maps, and the beginning of VF29 through `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL__MSI_MULTI_CAP__SHIFT`. The chunk includes 274 distinct register field groups and 2,415 generated shift/mask definitions across VF26, VF27, VF28, and VF29.

Although this path sits under a `ceph-client` source mirror, the content is AMDGPU hardware metadata. It is not Ceph or distributed filesystem logic.

## Purpose

`nbio_2_3_sh_mask.h` publishes the bitfield layout for NBIO 2.3 registers and PCI configuration-space registers. The paired `nbio_2_3_offset.h` header supplies the register/config-space offsets; this file supplies the `__SHIFT` and `_MASK` constants used to compose writes and decode reads through AMDGPU register helpers.

For this specific chunk, the purpose is to describe PCI/PCIe configuration bit positions for high-numbered SR-IOV virtual functions on device 0 endpoint function 0:

- Tail of VF26 class/header, BAR, capability, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields.
- Full VF27 and VF28 Type 0 PCI header fields, PCIe capability fields, MSI/MSI-X fields, vendor-specific enhanced capability fields, Advanced Error Reporting fields, ATS fields, and ARI fields.
- Beginning of VF29 through PCIe device/link capability and control/status fields and the MSI capability-list header/start of MSI message control.

The public contract is mechanical but important:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted-in-register bit mask.

Wrong values here can compile cleanly while causing runtime code or diagnostic tooling to read, write, clear, or report the wrong PCIe configuration bits.

## Important Macro Families

### VF26 Tail

The first visible lines are already inside `BIF_CFG_DEV0_EPF0_VF26_0_PROG_INTERFACE`, then continue through `SUB_CLASS`, `BASE_CLASS`, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem/vendor adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency. The earlier VF26 `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, and `REVISION_ID` definitions are outside this chunk.

The VF26 PCIe capability group includes:

- `PCIE_CAP_LIST` and `PCIE_CAP` fields for capability ID, next pointer, PCIe version, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` fields for payload size, relaxed ordering, no-snoop, extended tags, FLR capability/initiation, error enables/status, user-detected error, auxiliary power, and pending transactions.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` fields for link speed/width, ASPM/power-management support, exit latencies, common clock, retrain/disable, bandwidth interrupts/status, link training, slot clock, and data-link active state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` fields for completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, TLP prefix behavior, supported link speeds, compliance/de-emphasis controls, 8 GT/s equalization status, RTM presence, crosslink resolution, downstream component presence, and DRS message status.

The VF26 interrupt capability families cover MSI and MSI-X:

- MSI list and message-control fields: enable, multiple-message capability/enable, 64-bit capable flag, and per-vector masking capability.
- MSI address, data, mask, and pending fields, including the `_64` aliases used when interpreting the 64-bit MSI layout.
- MSI-X capability, table, and pending-bit-array fields: table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The VF26 extended capability families cover vendor-specific capability headers/data, AER uncorrectable/correctable status/mask/severity, AER capability/control, header log dwords, TLP prefix log dwords, ATS capability/control, and ARI capability/control.

### Complete VF27 and VF28 Maps

VF27 and VF28 repeat the full generated VF config-space layout from `VENDOR_ID` through `PCIE_ARI_CNTL`. Each VF has its own macro prefix:

- `BIF_CFG_DEV0_EPF0_VF27_0_*`
- `BIF_CFG_DEV0_EPF0_VF28_0_*`

The complete maps include identity and class fields, standard PCI command/status bits, BARs, ROM and subsystem ID state, legacy interrupt fields, PCIe device/link capability/control/status, second-generation PCIe capability fields, MSI/MSI-X, vendor-specific extended capability, AER status/mask/logging, ATS, and ARI.

The repetition is intentional rather than abstracted. It lets generated AMDGPU code, firmware-facing code, debug tooling, or register dumps name a specific VF's config-space field directly. It also means copy/generator drift across adjacent VF blocks is a high-risk maintenance issue because nearly identical names differ only by VF number.

### VF29 Beginning

The VF29 section starts at `VENDOR_ID` and reaches only into `MSI_MSG_CNTL`. Within this chunk VF29 includes its Type 0 PCI header and the PCIe device/link capability groups through `LINK_STATUS2`, plus the MSI capability-list fields and the first two MSI message-control shifts (`MSI_EN` and `MSI_MULTI_CAP`). The rest of VF29 MSI message control, MSI address/data/mask/pending, MSI-X, vendor-specific, AER, ATS, and ARI fields continue in the next chunk.

## Important APIs, Types, and Constants

This chunk defines constants, not callable APIs or C types. Its important interfaces are the generated names consumed by broader AMDGPU register access infrastructure:

- `REG_SET_FIELD` and `REG_GET_FIELD` style helpers depend on the exact `__SHIFT` and `_MASK` pairs.
- Low-level AMDGPU accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and field helpers such as `WREG32_FIELD15` provide the runtime reads and writes outside this header.
- `nbio_2_3_offset.h` provides the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` addresses for these fields.
- `nbio_2_3_default.h` provides generated default values for related NBIO registers where defaults exist.

Field names mirror PCI/PCIe specification concepts: command/status, BARs, PCIe capability, device/link control, MSI, MSI-X, vendor-specific enhanced capability, Advanced Error Reporting, ATS, and ARI. That naming gives call sites and diagnostic tools a direct bridge between generated ASIC metadata and PCIe terminology.

## Control Flow

There is no executable control flow in this header range. Runtime behavior is supplied by code that includes the generated header set:

1. A caller selects a VF register/config-space offset from the NBIO 2.3 offset header or from a higher-level accessor table.
2. The caller reads a value, composes a new value, or decodes an existing value.
3. The shift/mask constants in this file identify the relevant field bits.
4. AMDGPU, PCI core, firmware, PF-mediated SR-IOV code, or hypervisor code performs the actual config-space or register transaction.

For this range, the effective control flow is mostly PCI/SR-IOV configuration and diagnostics rather than ordinary function calls in this file.

## State and Persistence Behavior

The header stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration state for virtual functions. That state can be initialized by hardware straps, firmware, the PF driver, the host PCI core, or a hypervisor, and it can be reset or replayed during FLR, VF teardown, GPU reset, suspend/resume, BACO/power transitions, or SR-IOV reconfiguration.

Important state represented by this chunk includes:

- Per-VF PCI identity, class, revision, header, BAR, ROM, subsystem, capability-pointer, and interrupt presentation.
- PCI command/status enables and sticky status/error bits, including memory access, bus mastering, SERR/parity behavior, interrupt disable, abort status, and parity error detected state.
- PCIe device controls for error reporting, relaxed ordering, payload/read-request sizing, extended tags, no-snoop, auxiliary power management, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, and TLP prefix behavior.
- PCIe link capability/control/status for speed, width, ASPM, exit latency, retrain/disable, common clock, bandwidth notifications, compliance controls, equalization status, and link activity.
- MSI/MSI-X interrupt programming state for VF26-VF28, plus the beginning of VF29 MSI metadata.
- AER status, masks, severity, capability/control, header logs, and TLP prefix logs for VF26-VF28.
- ATS and ARI capability/control state for address translation and alternative routing ID behavior on VF26-VF28.

Several represented bits are not ordinary persistent configuration. Status and AER fields may be sticky and clear-on-write according to PCIe semantics. FLR initiation, link retraining, emergency power reduction, MSI/MSI-X masks, and interrupt pending bits can have immediate hardware side effects. This header only describes bit positions; access permissions, ordering, polling, and clear semantics must come from the PCIe/NBIO specification and owning driver paths.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register database staying internally consistent:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`
- This `nbio_2_3_sh_mask.h` field-layout header.

Observed source-tree integration for the NBIO 2.3 generated headers includes AMDGPU NBIO, MxGPU, and SMU platform code. The most relevant consumers are code paths that include this header and then use the generated field macros through AMDGPU register helpers, including NBIO 2.3 setup, virtualization/MxGPU support, and SMU11 platform behavior.

The specific `BIF_CFG_DEV0_EPF0_VF*_0_*` fields integrate with SR-IOV virtual-function PCI config-space presentation. They are the bit-level companion to the offset-header VF blocks that map each VF's config-space addresses. In a virtualized setup, PF code, VF guest code, host PCI core, firmware, and hypervisor policy may all observe or mediate parts of this state.

## Risks and Edge Cases

- Chunk boundaries split register families. VF26 begins before this range, and VF29 continues after it. The later file-level report must merge neighboring chunks before making complete claims about VF26 or VF29.
- The file is generated and highly repetitive. A single wrong mask, shift, or VF number can compile successfully while targeting the wrong virtual function or corrupting an unrelated field.
- PCI command, status, AER, MSI/MSI-X, FLR, and link-control fields have side effects. Generic read/modify/write treatment can accidentally clear errors, trigger resets, retrain links, mask interrupts, or lose diagnostic logs.
- VF numbering is isolation-sensitive. Cross-wiring VF27/VF28/VF29 field names would be especially hard to catch by compilation and could affect SR-IOV guest isolation or device enumeration.
- MSI 32-bit and 64-bit layouts share conceptual registers and aliases. Consumers must interpret message address/data/mask/pending fields according to the MSI capability format rather than treating all generated names as independent storage.
- AER log, TLP prefix log, ATS, and ARI fields influence error diagnosis, IOMMU/address-translation behavior, and routing-ID handling. Incorrect bit definitions can hide failures or break virtualized PCIe behavior.
- Link capability/control/status fields can influence ASPM, link retraining, compliance, and equalization behavior. Bad masks can appear as intermittent link, power-management, or performance regressions rather than obvious build failures.
- Visibility does not imply write permission. PF, VF, guest, host, firmware, and hypervisor contexts may have different access rights to the same conceptual fields.

## Test and Validation Signals

Useful validation is mostly build-time, generated-header consistency, and hardware/SR-IOV behavior:

- Build AMDGPU code paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MxGPU, and SMU11 platform files.
- Compare repeated VF26-VF29 field layouts against adjacent VF chunks and against the matching `nbio_2_3_offset.h` blocks to catch missing fields, wrong VF prefixes, and mask-width drift.
- SR-IOV enumeration should expose coherent PCI IDs, class codes, BARs, capability pointers, PCIe capability structures, MSI/MSI-X capabilities, AER, ATS, and ARI for VF26-VF29 where these VFs are enabled.
- VF reset and teardown tests should validate FLR initiation/status behavior and restored command/status defaults.
- MSI/MSI-X interrupt tests should verify vector delivery, mask/pending behavior, table/PBA interpretation, and 32-bit versus 64-bit MSI layout handling for covered VFs.
- PCIe link and power-management tests should watch payload/read-request sizing, ASPM/LTR/OBFF behavior, link retraining, bandwidth status, equalization, and compliance bits.
- AER error injection or diagnostics should verify uncorrectable/correctable status, masks, severity, header-log, and TLP-prefix-log decoding and clearing for VF26-VF28.
- Virtualization tests should cover PF/VF policy boundaries, guest config-space access, ATS/ARI enablement, and absence of unexpected AER storms, lost interrupts, or VF isolation failures.

## Unresolved Cross-Chunk References

Line 76009 starts after earlier VF26 fields; the preceding chunk is needed for VF26 `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, and `REVISION_ID`. Line 78432 ends inside VF29 `MSI_MSG_CNTL`; the following chunk is needed for the rest of VF29 MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions.

### subset-b-002936: lines 78433-80987

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 78433-80987

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants and grouping comments; it declares no functions, structs, variables, inline helpers, storage, locks, or executable code.

The line range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL` field set, completes the tail of VF29 PCIe interrupt/error/ATS/ARI capability metadata, defines the complete `BIF_CFG_DEV0_EPF0_VF30_0_*` PCI configuration-space field map, and then switches to repeated per-VF backend register blocks for VF0 through the beginning of VF6 under `BIF_BX_DEV0_EPF0_VF*` and `RCC_DEV0_EPF0_VF*`.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield-layout half of the NBIO 2.3 hardware ABI used by AMDGPU. The companion `nbio_2_3_offset.h` file supplies register/config-space addresses and `nbio_2_3_default.h` supplies reset/default values. This chunk lets driver code and virtualization support use symbolic field names when decoding or programming PCIe and NBIO/BIF virtual-function registers instead of hard-coding raw bit positions.

The major hardware areas represented here are:

- VF29 PCIe MSI/MSI-X, vendor-specific capability, Advanced Error Reporting, header/TLP-prefix logging, Address Translation Services, and Alternative Routing-ID Interpretation fields.
- A complete VF30 PCI configuration map: IDs, command/status, class/header bytes, BAR-like base address fields, subsystem IDs, ROM/capability/interrupt fields, PCIe device and link capabilities/controls/status, MSI/MSI-X, vendor-specific extended capability, AER, ATS, and ARI.
- Per-VF backend/register-control blocks for VF0 through VF5, plus the first VF6 registers: MM index/data windows, RCC SR-IOV error and doorbell/config fields, BIF bus-master/atomic-error logging, doorbell GPA aperture fields, HDP coherency flush request/done controls, BIF transaction pending status, address LUT bypass, mailbox buffers and control bits, VM/hypervisor mailbox bits, and four GFX MSI-X vectors plus a pending-bit array.

## Important APIs, Types, And Constants

The public interface is the generated macro convention used across AMD register headers:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- `// addressBlock: ...` comments identify generated hardware address blocks.
- `//<REGISTER>` comments group subsequent field definitions by register.

There are no C types in this chunk. Integer width and access semantics are supplied by the register helper layer and by the hardware register definition. Important macro families visible in the chunk include:

- VF29 tail fields: `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL`, MSI address/data/mask/pending registers, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, `MSIX_PBA`, vendor-specific capability/header/scratch registers, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, AER uncorrectable/correctable status/mask/severity fields, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG[0-3]`, `PCIE_TLP_PREFIX_LOG[0-3]`, `PCIE_ATS_*`, and `PCIE_ARI_*`.
- VF30 PCI config identity and base fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_[1-6]`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- VF30 PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- VF30 interrupt and extended capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data/mask/pending aliases including 64-bit layout aliases, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, `MSIX_PBA`, vendor-specific extended capability registers, AER status/mask/severity/control/log fields, ATS, and ARI.
- Per-VF system/backend fields for VF0-VF5 and the start of VF6: `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `DOORBELL_SELFRING_GPA_APER_BASE_{HIGH,LOW}`, `DOORBELL_SELFRING_GPA_APER_CNTL`, `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`, mailbox transfer/receive DWORDs, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, `BIF_VMHV_MAILBOX`, `GFXMSIX_VECT[0-3]_*`, and `GFXMSIX_PBA`.

## Control Flow

This header chunk has no runtime control flow. Its control-flow role is compile-time substitution into code that performs register access:

1. AMDGPU source includes the NBIO 2.3 offset/default/sh-mask headers.
2. Caller code selects the correct register address from the offset header and the correct field macro from this header.
3. Helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE` compose, extract, read, and write values.
4. Hardware, firmware, PF/VF, or hypervisor state changes according to the targeted register and the register's side-effect rules.

The repeated VF backend blocks are mechanically similar but target distinct virtual functions. For example, `BIF_BX_DEV0_EPF0_VF0_GPU_HDP_FLUSH_REQ__CP0_MASK` and `BIF_BX_DEV0_EPF0_VF5_GPU_HDP_FLUSH_REQ__CP0_MASK` describe the same bit position in different VF-specific registers. The macro names encode the VF number; no runtime loop or abstraction is present in the header.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist no local state. They describe hardware-visible state in PCIe configuration registers and NBIO/BIF virtualization/backend registers.

State represented by this chunk includes:

- PCI config presentation state for VF29/VF30, including IDs, BAR-like address fields, capability list pointers, PCIe device/link capabilities, MSI/MSI-X capability data, AER capability state, ATS enablement, and ARI group/next-function data.
- Mutable PCIe control state such as command register bits, bus-master and memory-space enables, interrupt disable, payload/read-request sizing, error-reporting enables, relaxed ordering, no-snoop, FLR initiation, completion timeout controls, LTR/OBFF/IDO/atomic-operation controls, link retrain/common-clock/link-disable controls, MSI enable/mask/pending bits, MSI-X function mask/enable, ATS ATC enable, and ARI function group enables.
- Diagnostic and latch state such as PCI status bits, device/link status, AER uncorrectable/correctable status, AER header logs, TLP prefix logs, RCC invalid SR-IOV access status, doorbell read access status, BIF bus-master-low status, unsupported atomic-operation logs, and BIF transaction pending bits.
- Per-VF backend state for register aperture selection, doorbell GPA apertures, HDP coherency flush requests and completions, mailbox transfer/receive buffers, mailbox valid/ack handshake bits, VM/hypervisor mailbox bits, and GFX MSI-X vector address/data/control and pending-bit state.

Persistence depends on hardware ownership. Many capability fields are read-only or read-mostly strap/firmware-defined values. Control and mailbox fields are mutable hardware state controlled by PF, VF, firmware, or hypervisor paths. Error/status bits may be sticky until explicit clear, FLR, VF teardown, GPU reset, power transition, or another hardware-defined reset path.

## Dependencies

Direct dependencies and assumptions:

- The matching `nbio_2_3_offset.h` file must provide the corresponding register/config-space offsets for the same NBIO 2.3 address blocks.
- The matching `nbio_2_3_default.h` file must agree with the same hardware revision's reset/default values.
- AMDGPU register helper macros provide the actual read/modify/write behavior and field extraction/composition.
- Linux PCI/PCIe semantics define many of the capability fields mirrored here: command/status, PCIe device/link capability and control, MSI/MSI-X, AER, ATS, ARI, and function-level reset.
- SR-IOV, PF/VF, hypervisor, and firmware ownership rules determine which agent may program the per-VF config, mailbox, doorbell, and backend registers.

Observed integration in this source tree includes `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 platform files including `navi10_ppt.c` and `sienna_cichlid_ppt.c`, all of which include the NBIO 2.3 sh-mask header. `nbio_v2_3.c` also references NBIO/BIF offset names for HDP flush and PCIe access plumbing, showing how this header family is consumed with the offset definitions.

## Integration Points

This chunk integrates primarily with AMDGPU NBIO, PCIe, and virtualization code:

- NBIO 2.3 setup and service paths use generated field definitions to access PCIe/NBIO registers through SOC15 and PCIe register helpers.
- SR-IOV and MXGPU paths depend on per-VF field names to present, configure, reset, and service virtual functions without confusing VF-specific register instances.
- Linux PCI core and guest drivers interact with overlapping VF PCI configuration state, especially command/status, BARs, capabilities, MSI/MSI-X, AER, ATS, ARI, and FLR.
- Doorbell aperture and mailbox fields connect GPU virtualization resource routing and PF/VF/hypervisor communication.
- HDP coherency flush fields connect VM/VF-visible backend registers with cache/coherency maintenance for command processor and SDMA clients.
- GFX MSI-X vector fields provide per-VF interrupt routing metadata for four graphics MSI-X vectors plus pending bits.

## Risks

- **Generated-header drift:** A wrong shift or mask compiles cleanly but can read or write the wrong hardware bit. For repeated VF families, a single copy-generation error can affect one VF while adjacent VFs appear correct.
- **Register/address mismatch:** This file only defines fields. Pairing a VF30 field with a VF29 offset, or a VF5 backend mask with a VF4 register address, can silently corrupt unrelated state.
- **Partial chunk boundaries:** The range begins after the first VF29 MSI message-control shift definitions and ends at the first VF6 BME status register. The full file-level report must reconcile this document with neighboring chunks before making complete VF29 or VF6 claims.
- **PCI core ownership conflicts:** Command/status, MSI/MSI-X, AER, ATS, ARI, BAR, FLR, and link-control fields overlap with Linux PCI subsystem policy. AMDGPU direct writes need tight ownership and ordering.
- **Virtualization isolation:** Per-VF doorbell apertures, mailbox state, MM index windows, BIF transaction status, interrupt vectors, and function identifiers affect guest isolation. Incorrect programming can expose registers, misroute interrupts, lose mailbox messages, or break VF assignment.
- **Side-effectful status bits:** AER, PCI status, BIF atomic error logs, BME-low clear bits, mailbox ACK/VALID bits, HDP flush request/done bits, and interrupt pending/mask bits are not generic storage. Blind read/modify/write can clear evidence, acknowledge messages, or wedge a flush handshake.
- **MSI layout ambiguity:** MSI address/data/mask/pending registers have normal and `_64` layout aliases. Callers must respect the enabled 32-bit versus 64-bit MSI format.
- **Link and transaction controls:** VF30 link-control and transaction-related fields can affect PCIe training, error reporting, payload sizing, ordering, and completion behavior.

## Test Signals

Useful validation signals for code touching these macros or their generated source:

- Build AMDGPU configurations that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU, and SMU11 paths.
- Compare generated mask/shift names against `nbio_2_3_offset.h` for VF29, VF30, and BIF/RCC VF0-VF6 to catch missing, duplicated, or mis-numbered fields.
- Static consistency checks should verify repeated VF backend blocks have identical layouts where the hardware spec expects only the VF number to vary.
- SR-IOV enumeration should show sane VF29/VF30 PCI IDs, command/status defaults, BAR/capability layout, PCIe capability values, MSI/MSI-X capability data, AER, ATS, and ARI.
- VF lifecycle testing should cover VF creation/removal, FLR, guest driver load/unload, command/status reset, MSI/MSI-X interrupt delivery, and preserved isolation between adjacent VFs.
- Mailbox and doorbell tests should exercise valid/ack handshakes, interrupt enables, GPA aperture programming, and invalid-access logging.
- HDP flush tests should verify request/done bits for CP0-CP9 and SDMA0/SDMA1 are observed correctly across VF0-VF5 paths that use these registers.
- PCIe error diagnostics or injection should map to the expected AER uncorrectable/correctable status, mask, severity, header log, TLP prefix log, RCC error-log, and BIF atomic-error bits.
- Suspend/resume, GPU reset, and VF teardown tests should confirm sticky status/control bits return to expected defaults and do not leak state between VF assignments.

## Chunk Notes

- The chunk starts mid-register: earlier lines likely contain `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL__MSI_EN__SHIFT` and `MSI_MULTI_CAP__SHIFT`.
- The VF30 PCI configuration-space map is complete within this line range.
- The BIF/RCC backend blocks are complete for VF0 through VF5 except that completeness must be confirmed against the offset/default headers; VF6 is only started here and continues in the next chunk.
- Because this is generated register metadata, the most important reconciliation gate is source-family consistency across `nbio_2_3_sh_mask.h`, `nbio_2_3_offset.h`, and `nbio_2_3_default.h`.

### subset-b-002937: lines 80988-83608

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 80988-83608

## Scope

This chunk covers generated NBIO 2.3 shift and mask definitions for SR-IOV virtual-function NBIF/RCC registers. It starts inside the VF6 `BIFPFVFDEC1` block at `BIF_BX_DEV0_EPF0_VF6_BIF_ATOMIC_ERR_LOG`, contains the VF6 mailbox and graphics MSI-X tail, covers complete VF7 through VF15 `SYSPFVFDEC`, `BIFPFVFDEC1`, and `BIFDEC2` field maps, and ends in VF16 after `BIF_BX_DEV0_EPF0_VF16_BIF_TRANS_PENDING`.

The chunk is data-only C preprocessor material. It defines no functions, structs, variables, allocations, locks, or direct MMIO accesses. Its interface is the generated field convention:

- `<REGISTER>__<FIELD>__SHIFT` for the field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field mask.

Within this range there are 2,022 generated macros: 1,011 shift macros and 1,011 matching mask macros, covering 479 register-name families.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield half of the AMD NBIO 2.3 register ABI. The companion offset header names register addresses, while this header tells register helpers how to encode or decode individual fields. For this chunk, the ABI surface is per-virtual-function SR-IOV state for VF6 through VF16 around:

- VF indirect MMIO index/data access.
- RCC error, memory-size, doorbell-aperture, and IOV function-identifier state.
- BIF bus-master, unsupported atomic, doorbell self-ring aperture, HDP coherency flush, transaction-pending, address-LUT bypass, mailbox, and VM-hypervisor mailbox state.
- Per-VF graphics MSI-X vector table and pending-bit-array fields.

These definitions let AMDGPU, firmware-facing code, and virtualization paths compose register values without open-coded bit numbers. They are especially sensitive because each VF has its own generated macro namespace; a valid C identifier can still target the wrong virtual function if the VF number is copied incorrectly.

## Important Macro Families

### Chunk Boundary: VF6 Tail

The first visible VF6 definition is `BIF_BX_DEV0_EPF0_VF6_BIF_ATOMIC_ERR_LOG__UR_ATOMIC_OPCODE__SHIFT`; the VF6 `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, RCC fields, and `BIF_BME_STATUS` begin in the previous chunk. This chunk then covers the rest of VF6 `BIFPFVFDEC1`:

- `BIF_ATOMIC_ERR_LOG` status bits for unsupported atomic opcode, request-enable-low, length, and non-relaxed-request conditions, plus clear bits at positions 16-19.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `LOW`, and `CNTL` fields for the self-ring guest physical address aperture, enable bit, mode bit, and aperture size.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL` one-bit flush-address controls.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bits for CP0 through CP9 and SDMA0 through SDMA1 clients.
- `BIF_TRANS_PENDING` master/slave pending indicators and `NBIF_GFX_ADDR_LUT_BYPASS`.
- Four transmit and four receive mailbox dwords, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`.

The VF6 tail also includes `RCC_DEV0_EPF0_VF6_GFXMSIX_*` definitions for graphics MSI-X vectors 0-3. Each vector has low/high message address, message data, and a one-bit control mask, followed by `GFXMSIX_PBA` pending bits 0-3.

### Complete VF7 Through VF15 Maps

VF7, VF8, VF9, VF10, VF11, VF12, VF13, VF14, and VF15 repeat the same generated layout:

- `SYSPFVFDEC`: `MM_INDEX` with `MM_OFFSET` and `MM_APER`, `MM_DATA`, and `MM_INDEX_HI`.
- RCC `BIFPFVFDEC1`: `RCC_ERR_LOG` for invalid SR-IOV register access and doorbell-read access status, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER` with function identifier and IOV enable.
- BIF `BIFPFVFDEC1`: `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, doorbell self-ring GPA aperture base/control, HDP register and memory flush controls, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`, mailbox dwords/control/interrupts, and `BIF_VMHV_MAILBOX`.
- RCC `BIFDEC2`: graphics MSI-X vector 0-3 address/data/control fields and the four-bit graphics MSI-X PBA.

The fields are mechanically identical across these complete VF blocks except for the `VF<n>` namespace. That repetition is useful for generated hardware coverage, but it makes layout drift, misnumbered names, or copied wrong-VF references high-risk.

### Chunk Boundary: VF16 Head

The final visible section starts VF16 with `SYSPFVFDEC`, RCC `BIFPFVFDEC1`, and BIF `BIFPFVFDEC1` through `BIF_TRANS_PENDING`. VF16 `NBIF_GFX_ADDR_LUT_BYPASS`, mailbox, VMHV mailbox, and graphics MSI-X fields continue in the next chunk. File-level research should merge this document with adjacent chunks before making complete claims about VF6 or VF16.

## Important APIs, Types, and Functions

There are no C APIs, types, or functions in this chunk. The effective public API is the macro naming contract consumed by AMD register helpers. In surrounding AMDGPU code, these generated names are normally paired with:

- Matching offset macros from `nbio_2_3_offset.h`.
- Reset/default values from `nbio_2_3_default.h`.
- Register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`.

Consumers include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 platform files `navi10_ppt.c` and `sienna_cichlid_ppt.c`, all of which include this NBIO 2.3 mask header. The specific VF6-VF16 names in this chunk are hardware ABI definitions; direct runtime use may be concentrated in virtualization, firmware, or generated register-table paths rather than hand-written references to every VF macro.

## Control Flow

The header has no executable control flow. Runtime flow belongs to code that includes it:

1. The driver selects a per-VF register offset from the offset header.
2. The driver uses the matching `__SHIFT` and `_MASK` macro to encode a field for a write or decode a field from a read.
3. The access reaches NBIO/RCC hardware through the SOC15/MMIO/indirect register path selected by the caller.
4. Hardware state changes or status is reported according to the register semantics.

Several hardware workflows are implied by the fields:

- HDP coherency flushing uses `GPU_HDP_FLUSH_REQ` client bits and observes `GPU_HDP_FLUSH_DONE` for CP and SDMA engines.
- Mailbox communication writes transmit dwords, asserts transmit valid bits, observes acknowledge/receive-valid bits, and may use valid/ack interrupt enables.
- VMHV mailbox communication uses compact transmit/receive message-data fields plus valid, ack, and interrupt-enable bits.
- Error/status handling reads `RCC_ERR_LOG`, `BIF_BME_STATUS`, and `BIF_ATOMIC_ERR_LOG`, then uses explicit clear fields where provided.
- MSI-X setup programs vector message address/data/control fields and observes pending bits in `GFXMSIX_PBA`.

The masks do not encode ordering, timeout, locking, or clear-on-write policy. Those details must come from the callers and the NBIO hardware specification.

## State and Persistence Behavior

The header stores no software state. It names hardware-visible state that persists until reset, FLR, VF teardown, power transition, firmware action, hypervisor action, or explicit driver writes.

Important state represented here includes:

- Per-VF indirect MMIO aperture selection through `MM_INDEX`, `MM_INDEX_HI`, and `MM_DATA`.
- SR-IOV access error state in `RCC_ERR_LOG`, including invalid register access and doorbell read access.
- VF resource presentation through `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`.
- Doorbell aperture enablement and self-ring GPA aperture base/mode/size.
- Bus-master-low and unsupported atomic request status, with explicit clear bits.
- HDP register/memory coherency flush triggers and CP/SDMA flush completion state.
- BIF master/slave transaction-pending state and graphics address LUT bypass.
- Mailbox buffers, valid/ack handshake bits, interrupt enables, and VMHV mailbox message/ack state.
- Graphics MSI-X vector message address, message data, vector mask bits, and PBA pending bits.

Many of these registers are stateful control/status registers, not passive storage. Clearing error logs, toggling mailbox valid/ack fields, masking MSI-X vectors, changing doorbell apertures, or issuing HDP flushes can alter device behavior immediately.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register-header set:

- `nbio_2_3_offset.h` supplies the matching register offsets and base indices for the `BIF_BX_DEV0_EPF0_VF*` and `RCC_DEV0_EPF0_VF*` names.
- `nbio_2_3_default.h` supplies reset/default values for related NBIO registers.
- AMDGPU SOC15 and register-field helper macros consume the shift/mask pairs.

Tree-level integration points observed from includes and related references:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` is the primary NBIO 2.3 implementation using this generated header set.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes the same header in virtualization-oriented code.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include NBIO 2.3 masks for platform management interactions.
- Adjacent NBIO generation families use the same HDP flush and VF register layout patterns, so cross-generation comparisons can catch accidental field-width or bit-position drift.

The names in this chunk are part of a broader generated ABI surface for many virtual functions. The hardware access rights for PF, VF guest, hypervisor, and firmware contexts are not represented in the header and must be enforced elsewhere.

## Risks

- Wrong masks or shifts can write unrelated control bits, corrupt per-VF doorbell apertures, break mailbox handshakes, hide SR-IOV access errors, or misprogram MSI-X vectors.
- Wrong VF namespace usage can compile cleanly while targeting another virtual function. This chunk has near-identical VF7-VF15 maps, making copy/paste mistakes hard to detect by type checking.
- Status and clear fields are mixed in the same generated family. Treating `CLEAR_*` fields as ordinary status bits, or writing status masks without preserving unrelated bits, can lose diagnostics or clear evidence prematurely.
- HDP flush request/done fields are synchronization-sensitive. Missing waits, wrong client bits, or stale done-bit interpretation can create memory-coherency bugs between CP/SDMA engines, host memory, and the driver.
- Doorbell aperture and LUT-bypass fields are security-sensitive in SR-IOV. Incorrect aperture base, size, enable, or bypass programming can expose the wrong guest physical address window or route doorbells incorrectly.
- Mailbox valid/ack fields implement hardware handshakes. Races, missing interrupt masking, or wrong clear ordering can deadlock PF/VF or VM/hypervisor communication.
- MSI-X vector address/data/control fields affect interrupt delivery. Bad masks can drop interrupts, deliver them to the wrong target, or leave pending bits uncleared.
- Chunk boundaries are partial for VF6 and VF16. A reconciled file-level document should avoid treating this chunk alone as a complete VF6 or VF16 map.

## Test and Validation Signals

Useful validation is mostly build, generated-header consistency, SR-IOV, and hardware bring-up coverage:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU, and SMU11 platform code.
- Generated-header checks should verify each `__SHIFT` has a matching `_MASK`, each VF7-VF15 block has the same field set, and the mask widths match the documented field widths.
- Cross-check `nbio_2_3_sh_mask.h` against `nbio_2_3_offset.h` so every register family in this chunk has a matching address/base-index definition.
- SR-IOV tests should create multiple VFs beyond VF6 and verify per-VF doorbell aperture setup, config memory-size reporting, IOV function identifiers, and VF isolation.
- HDP coherency tests should issue CP and SDMA flush requests and confirm matching done bits for all represented clients.
- Mailbox tests should exercise transmit/receive valid and ack handshakes, interrupt-enable bits, and VMHV mailbox fields under PF/VF or hypervisor-mediated scenarios.
- Error-injection tests should validate invalid SR-IOV register access, doorbell-read access, bus-master-low, and unsupported atomic logging plus clear behavior.
- MSI-X tests should program graphics vectors 0-3, toggle vector mask bits, deliver interrupts, and verify PBA pending-bit behavior for VFs covered by the complete blocks.

## Unresolved Cross-Chunk References

Line 80988 starts after the VF6 `SYSPFVFDEC`, RCC `BIFPFVFDEC1`, and `BIF_BME_STATUS` definitions, so the full VF6 map requires the previous chunk. Line 83608 ends immediately after VF16 `BIF_TRANS_PENDING`; the remaining VF16 LUT-bypass, mailbox, VMHV mailbox, and graphics MSI-X fields continue in the next chunk. The merge lane should stitch those boundaries before producing the final per-file research document.

### subset-b-002938: lines 83609-86241

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 83609-86241

## Scope

This chunk covers generated NBIO 2.3 shift and mask macros for SR-IOV virtual-function register windows. It starts in the VF16 BIF PF/VF decode block after the VF16 HDP flush-done fields, then covers full repeated field layouts for VF17 through most of VF26, ending at `RCC_DEV0_EPF0_VF26_GFXMSIX_VECT3_ADDR_HI`.

The range contains 2,633 source lines with 2,014 `#define` constants: 1,007 `__SHIFT` values and 1,007 matching `_MASK` values. It has no C functions, structs, variables, allocation, locks, or executable branches. Its purpose is purely ABI description for hardware register fields.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield half of the NBIO 2.3 generated register contract. The matching offset header identifies the register addresses; this header identifies where each field lives inside each register. Driver code can then compose, extract, or test register values with `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, and direct bit masks without duplicating raw bit positions.

This specific chunk describes VF-local views for AMDGPU virtualization and PCIe/NBIO plumbing. The repeated VF blocks expose:

- indirect MMIO aperture index/data fields for each VF;
- RCC error, doorbell-aperture, config-memory, and IOV-identifier fields;
- BIF bus-master/atomic-error status and clear bits;
- self-ring doorbell GPA aperture base/control fields;
- HDP coherency flush request/done fields for CP and SDMA engines;
- transaction-pending indicators;
- VF transmit/receive mailbox data, valid, ack, and interrupt-enable fields;
- compact VM/hypervisor mailbox fields;
- four GFX MSI-X vector-table entries and a pending-bit array for each VF.

## Important Macro Families

### VF16 Tail

The assigned slice begins at the end of the VF16 `BIFPFVFDEC1` block. The covered VF16 fields include:

- `BIF_BX_DEV0_EPF0_VF16_NBIF_GFX_ADDR_LUT_BYPASS`, a single `LUT_BYPASS` bit for bypassing NBIF graphics address translation.
- `BIF_BX_DEV0_EPF0_VF16_MAILBOX_MSGBUF_TRN_DW0..DW3` and `RCV_DW0..DW3`, each exposing full-width `MSGBUF_DATA`.
- `BIF_BX_DEV0_EPF0_VF16_MAILBOX_CONTROL`, with `TRN_MSG_VALID`, `TRN_MSG_ACK`, `RCV_MSG_VALID`, and `RCV_MSG_ACK`.
- `BIF_BX_DEV0_EPF0_VF16_MAILBOX_INT_CNTL`, with valid/ack interrupt enables.
- `BIF_BX_DEV0_EPF0_VF16_BIF_VMHV_MAILBOX`, a compact VM/hypervisor mailbox with transmit and receive data nibbles, valid bits, ack bits, and interrupt enables.

It then defines the VF16 `BIFDEC2` MSI-X view: four `RCC_DEV0_EPF0_VF16_GFXMSIX_VECT*` entries, each with low/high message address, message data, and control mask bit, plus `RCC_DEV0_EPF0_VF16_GFXMSIX_PBA` pending bits 0 through 3.

### VF17-VF26 Repeated Decode Blocks

VF17 through VF26 repeat the same generated register pattern. Each VF has an address-block sequence:

- `nbio_nbif0_bif_bx_dev0_epf0_vf*_SYSPFVFDEC` for `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- `nbio_nbif0_rcc_dev0_epf0_vf*_BIFPFVFDEC1` for RCC error, doorbell aperture enable, config memory size/reserved, and IOV function identifier.
- `nbio_nbif0_bif_bx_dev0_epf0_vf*_BIFPFVFDEC1` for BIF status, atomic-error logging, doorbell self-ring aperture, HDP flush, transaction-pending, address-LUT bypass, and mailbox fields.
- `nbio_nbif0_rcc_dev0_epf0_vf*_BIFDEC2` for GFX MSI-X vector table and pending-bit fields.

The macro names are VF-numbered, but the field layouts are intentionally identical across the VFs in this range. That repetition lets generated code or diagnostics select a VF-specific register name while preserving the same bit semantics.

### MMIO Indirect Aperture Fields

For VF17 through VF26, `BIF_BX_DEV0_EPF0_VF*_MM_INDEX` splits the index register into:

- `MM_OFFSET`, bits 0 through 30, mask `0x7fffffff`;
- `MM_APER`, bit 31, mask `0x80000000`.

`BIF_BX_DEV0_EPF0_VF*_MM_DATA` exposes a full 32-bit `MM_DATA` field, while `MM_INDEX_HI` exposes a full 32-bit `MM_OFFSET_HI`. Together these fields describe the VF-visible indirect MMIO path used by NBIF/BIF decode windows.

### RCC VF State

Each VF has `RCC_DEV0_EPF0_VF*_RCC_ERR_LOG`, with status bits for invalid SR-IOV register access and doorbell read access. `RCC_DOORBELL_APER_EN` gates the BIF doorbell aperture with `BIF_DOORBELL_APER_EN`. `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration fields. `RCC_IOV_FUNC_IDENTIFIER` has a low `FUNC_IDENTIFIER` bit and a high `IOV_ENABLE` bit at bit 31.

These fields mirror the PF/VF RCC controls used elsewhere in NBIO code, but this chunk publishes the per-VF16-through-VF26 macro names rather than the PF or VF0 names used by common runtime paths.

### BIF Status, Doorbell, and Atomic Error Fields

`BIF_BX_DEV0_EPF0_VF*_BIF_BME_STATUS` records `DMA_ON_BME_LOW` and has a high `CLEAR_DMA_ON_BME_LOW` bit. `BIF_ATOMIC_ERR_LOG` has status and clear pairs for unsupported atomic opcode, request-enable-low, length, and non-relaxed/NR conditions. The clear bits live in the high halfword, so callers must preserve unrelated status bits when acknowledging a condition.

The self-ring GPA doorbell aperture is split across:

- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`;
- `DOORBELL_SELFRING_GPA_APER_BASE_LOW`;
- `DOORBELL_SELFRING_GPA_APER_CNTL`, with enable at bit 0, mode at bit 1, and size in bits 8 through 19.

These VF-specific fields match the PF programming pattern in `nbio_v2_3_enable_doorbell_selfring_aperture()`, where the PF aperture base is loaded from `adev->doorbell.base` and the control word is composed with `REG_SET_FIELD`.

### HDP Flush and Transaction State

Each VF block includes register and memory coherency flush selectors:

- `HDP_REG_COHERENCY_FLUSH_CNTL__HDP_REG_FLUSH_ADDR`;
- `HDP_MEM_COHERENCY_FLUSH_CNTL__HDP_MEM_FLUSH_ADDR`.

It then defines `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bits for CP0 through CP9 plus SDMA0 and SDMA1. The bit positions are stable across all VFs in this chunk: CP0 starts at bit 0, CP9 is bit 9, SDMA0 is bit 10, and SDMA1 is bit 11.

`BIF_TRANS_PENDING` exposes master and slave pending bits. Runtime code can use the matching offset/mask pair to determine whether outstanding traffic exists before reset, suspend, FLR, or VF teardown.

### Mailbox and VM/HV Mailbox Fields

Each VF has four transmit message buffer dwords and four receive message buffer dwords. The field name is always `MSGBUF_DATA`, mask `0xffffffff`, shift 0.

`MAILBOX_CONTROL` exposes the handshake state:

- transmit valid at bit 0;
- transmit ack at bit 1;
- receive valid at bit 8;
- receive ack at bit 9.

`MAILBOX_INT_CNTL` enables valid and ack interrupts. `BIF_VMHV_MAILBOX` packs a smaller VM/hypervisor mailbox into one register: interrupt enables at bits 0 and 1, transmit data in bits 8 through 11, transmit valid at bit 15, receive data in bits 16 through 19, receive valid at bit 23, transmit ack at bit 24, and receive ack at bit 25.

The integration model is visible in `amdgpu/mxgpu_nv.c`, which includes the NBIO 2.3 offset and shift/mask headers and implements VF/PF mailbox handshakes by writing transmit dwords, asserting valid, polling ack, reading receive dwords, and acknowledging receive messages.

### GFX MSI-X Vector Fields

For VF16 through the covered part of VF26, each `RCC_DEV0_EPF0_VF*_GFXMSIX_VECT0..3` entry contains:

- `ADDR_LO__MSG_ADDR_LO`, shifted by 2 with mask `0xfffffffc`, reflecting DWORD alignment of the low message address;
- `ADDR_HI__MSG_ADDR_HI`, full 32 bits;
- `MSG_DATA__MSG_DATA`, full 32 bits;
- `CONTROL__MASK_BIT`, bit 0.

Each VF block also has `GFXMSIX_PBA` pending bits 0 through 3. The chunk boundary cuts through the VF26 MSI-X block after `VECT3_ADDR_HI`; `VECT3_MSG_DATA`, `VECT3_CONTROL`, and `GFXMSIX_PBA` continue in the next chunk.

## Control Flow

This header has no local control flow. The runtime control flow is external:

1. AMDGPU selects NBIO 2.3 support for the ASIC and includes `nbio_2_3_offset.h`, `nbio_2_3_sh_mask.h`, and `nbio_2_3_default.h`.
2. Code computes or selects a register address using the offset header and SOC15 helpers.
3. Code reads a register, uses this header's shift/mask macros via `REG_SET_FIELD`, `REG_GET_FIELD`, or direct masking, then writes the result back.
4. Hardware applies the result to VF MMIO decode, doorbell routing, mailbox signaling, HDP coherency, transaction state, MSI-X delivery, or SR-IOV error/status handling.

For mailbox and status registers, the higher-level flow is a hardware handshake rather than a C branch in this file. A producer writes message buffer dwords and sets valid; the peer observes valid, consumes the dwords, and sets ack; the original producer clears valid to complete the exchange. Error-log and BME status fields use status/clear pairs, so callers must use the documented clear bits rather than overwriting the whole register blindly.

## State and Persistence Behavior

The header itself stores no state. It names state held in NBIO/NBIF hardware registers. That state persists until changed by MMIO/config writes, VF FLR, PF-mediated reset, ASIC reset, power transitions, firmware action, or hypervisor/VF management logic.

Persistent hardware state represented in this chunk includes:

- VF indirect MMIO aperture index and data values;
- VF IOV enable/function identifier and configured memory size;
- invalid SR-IOV access and doorbell-read error status;
- bus-master-low DMA and atomic-request error latches;
- doorbell self-ring GPA aperture base, enable, mode, and size;
- HDP flush request/done handshakes for CP and SDMA engines;
- BIF master/slave transaction pending status;
- mailbox payload dwords, valid/ack state, and mailbox interrupt enables;
- VM/hypervisor compact mailbox state;
- GFX MSI-X message addresses, message data, mask bits, and pending bits.

Ownership is shared. PF driver code, VF driver code, firmware, hypervisor logic, and hardware engines can all influence different fields. The generated header does not enforce ownership; it only names the bit locations.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register specification and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies matching `mm*`, `reg*`, and `cfg*` register addresses and base indices;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies reset/default values for the same register families;
- AMDGPU SOC15 access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_NO_KIQ`, `WREG32_NO_KIQ`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`;
- PCIe/SR-IOV, MSI-X, doorbell, HDP coherency, and VM/hypervisor mailbox hardware semantics.

Direct NBIO 2.3 consumers include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes this header and uses related PF field families for memory access, doorbell aperture enablement, self-ring doorbell programming, interrupt setup, HDP flush offsets/masks, and register remapping. `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` also includes the NBIO 2.3 headers and uses the mailbox register interface for VF/PF communication. Power-management code under SMU11 includes this header for NBIO/PCIe strap and policy fields.

The exact VF16-through-VF26 names in this chunk are mostly generated ABI coverage rather than common hand-written C references. Their important integration role is keeping the per-VF register map available to diagnostics, generated code, virtualization paths, and any future code that needs to address a specific high-numbered VF window.

## Risks

- A wrong shift or mask compiles cleanly but changes the wrong hardware bit. In this chunk that can break VF doorbells, mailbox handshakes, MSI-X delivery, HDP flush completion checks, or SR-IOV error reporting.
- The VF blocks are highly repetitive. Copying a macro from the wrong VF number can target a different VF's register window even though the field layout is identical.
- The chunk begins and ends mid-pattern. VF16's earlier BME/atomic/HDP fields are in the previous chunk, and VF26's final MSI-X fields continue in the next chunk. Merge/reconciliation must not treat this slice as a complete source-file summary.
- Status and clear bits share registers. Whole-register writes can clear diagnostics or acknowledge events unintentionally.
- Doorbell aperture mistakes have virtualization security implications because they affect guest/host address routing and command-submission visibility.
- HDP flush bits are synchronization-critical. Missing or mis-numbering a CP/SDMA done bit can produce stale CPU/GPU memory visibility or hangs in code that waits for flush completion.
- Mailbox valid/ack ordering matters. Setting valid before payload dwords are visible, failing to clear valid, or reading receive dwords outside the expected valid state can lose PF/VF messages.
- MSI-X address low fields intentionally mask off low two bits. Treating the field as a full 32-bit low address can misprogram interrupt messages.

## Test Signals

Useful validation is mostly build, hardware, and virtualization oriented:

- Kernel build coverage should compile NBIO 2.3 users without missing or mismatched field macros.
- Generated-header consistency checks should confirm every VF16-VF26 shift has a matching mask and matching register address in the offset header.
- SR-IOV PF/VF bring-up should validate VF enumeration, IOV enable/function identity, config memory size visibility, and protected invalid-access logging.
- VF mailbox tests should verify transmit/receive dword payloads, valid/ack transitions, ack polling, valid clearing, and valid/ack interrupt enable behavior.
- Doorbell tests should confirm per-VF doorbell aperture enablement and self-ring GPA aperture programming do not misroute guest doorbells.
- HDP coherency tests should exercise CP0..CP9 and SDMA0/SDMA1 request/done bits under VF workloads.
- MSI-X tests should verify all four GFX vectors per VF program aligned message addresses, message data, mask bits, and pending-bit behavior.
- Reset/FLR tests should check that BME status, atomic error latches, transaction-pending bits, mailbox state, and MSI-X mask/pending state settle to expected values after VF reset.

### subset-b-002939: lines 86242-88736

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 86242-88736

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 2.3 register mask header. It starts in the tail of the `RCC_DEV0_EPF0_VF26_GFXMSIX_*` MSI-X table definitions, covers the repeated virtual-function register blocks for `VF27` through `VF30`, and then enters the `nbio_pcie0_pswuscfg0_cfgdecp` PCIe upstream-switch configuration space register set through the beginning of `PSWUSCFG0_1_PCIE_ESM_CAP_5`.

The file is generated hardware metadata. It defines preprocessor constants only: no functions, structs, variables, allocation, locking, or executable control flow live in this chunk. Each field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for extracting or composing that field.

## Purpose

The purpose of this section is to provide the bit-level ABI used by AMDGPU/NBIO code when programming NBIO 2.3 hardware registers and PCIe configuration-space views. The matching `nbio_2_3_offset.h` header supplies register offsets such as `mmBIF_BX_DEV0_EPF0_VF27_GPU_HDP_FLUSH_REQ` or PCIe config-space offsets; this header supplies field positions and masks for those register values.

This chunk is particularly focused on two surfaces:

- SR-IOV virtual-function NBIF/RCC state for high-numbered VFs (`VF27` through `VF30`) plus the final MSI-X entries for `VF26`.
- PCIe upstream-port configuration, capability, error-reporting, virtual-channel, ACS, multicast, LTR, ARI, L1 PM substate, and electrical-speed-margining fields under `PSWUSCFG0_1_*`.

Driver code consumes these constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### VF26 Tail MSI-X Fields

The chunk begins mid-family with the tail of the `VF26` graphics MSI-X table:

- `RCC_DEV0_EPF0_VF26_GFXMSIX_VECT3_MSG_DATA`
- `RCC_DEV0_EPF0_VF26_GFXMSIX_VECT3_CONTROL`
- `RCC_DEV0_EPF0_VF26_GFXMSIX_PBA`

These define the message-data dword, vector mask bit, and pending-bit-array bits for vector 3 and the four-vector pending status. The previous chunk contains the earlier `VF26` vector address/control definitions, so this chunk is not a complete `VF26` MSI-X description by itself.

### VF27 Through VF30 System PF/VF Decode Windows

Each of `VF27`, `VF28`, `VF29`, and `VF30` begins with a `SYSPFVFDEC` address block:

- `BIF_BX_DEV0_EPF0_VF*_MM_INDEX`, with `MM_OFFSET` and `MM_APER`.
- `BIF_BX_DEV0_EPF0_VF*_MM_DATA`, with full-width `MM_DATA`.
- `BIF_BX_DEV0_EPF0_VF*_MM_INDEX_HI`, with full-width `MM_OFFSET_HI`.

These macros describe the indirect MMIO index/data window exposed per virtual function. The split low/high offset fields are the register-level encoding used when a VF needs an indirect MMIO aperture rather than direct PF-owned access.

### VF RCC SR-IOV, Doorbell, and Identity Fields

The repeated `RCC_DEV0_EPF0_VF*_BIFPFVFDEC1` blocks expose RCC-side VF status and configuration:

- `RCC_ERR_LOG` contains sticky/status bits for invalid SR-IOV register access and doorbell read access.
- `RCC_DOORBELL_APER_EN` enables the BIF doorbell aperture.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration dwords.
- `RCC_IOV_FUNC_IDENTIFIER` exposes the VF function identifier and an `IOV_ENABLE` bit.

These are virtualization-sensitive fields. They encode whether a VF is allowed to participate in SR-IOV access paths and whether doorbell apertures are visible for that function.

### VF BIF Error, Doorbell, HDP Flush, and Mailbox Fields

The `BIF_BX_DEV0_EPF0_VF*_BIFPFVFDEC1` blocks repeat the same register layout for each VF:

- `BIF_BME_STATUS` tracks DMA activity while bus mastering is low and has a clear bit.
- `BIF_ATOMIC_ERR_LOG` records unsupported-request atomic error classes: opcode, request-enable low, length, and non-relaxed/non-request attributes, with matching clear bits.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `...BASE_LOW`, and `...CNTL` define the self-ring doorbell guest physical address aperture, enable bit, mode bit, and size field.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL` expose flush-address fields for HDP coherency remap/control paths.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` define CP0 through CP9 and SDMA0/SDMA1 request/done bits.
- `BIF_TRANS_PENDING` exposes master and slave transaction-pending status.
- `NBIF_GFX_ADDR_LUT_BYPASS` controls or reports LUT bypass for the VF graphics address path.
- `MAILBOX_MSGBUF_TRN_DW0..3` and `MAILBOX_MSGBUF_RCV_DW0..3` provide four dwords each for transmit and receive message buffers.
- `MAILBOX_CONTROL` defines transmit valid/ack and receive valid/ack handshake bits.
- `MAILBOX_INT_CNTL` enables valid and ack interrupts.
- `BIF_VMHV_MAILBOX` packs hypervisor/VM mailbox interrupt enables, 4-bit transmit/receive data fields, valid bits, and ack bits.

The PF version of similar fields is actively consumed by `amdgpu/nbio_v2_3.c`: for example, the NBIO 2.3 implementation programs doorbell apertures, reports HDP flush request/done offsets, and builds `nbio_v2_3_hdp_flush_reg` from `BIF_BX_PF_GPU_HDP_FLUSH_DONE__CP*` and `__SDMA*` masks. The VF27-VF30 definitions are the per-VF layout equivalents for virtualization and remap paths.

### VF Graphics MSI-X Fields

Each complete `VF27` through `VF30` RCC `BIFDEC2` block defines four graphics MSI-X vectors plus a pending-bit array:

- `GFXMSIX_VECT0..3_ADDR_LO` use `MSG_ADDR_LO` at bit 2 with a `0xFFFFFFFC` mask, preserving PCI MSI/MSI-X address alignment.
- `GFXMSIX_VECT0..3_ADDR_HI` provide the upper 32 bits of the message address.
- `GFXMSIX_VECT0..3_MSG_DATA` provide the interrupt message data.
- `GFXMSIX_VECT0..3_CONTROL` expose each vector's mask bit.
- `GFXMSIX_PBA` exposes pending bits 0 through 3.

This family is tied to VM and SR-IOV interrupt routing. `amdgpu_device.c` has a resume path note that QEMU programming of VF MSI-X tables, specifically `GFXMSIX_VECT0_ADDR_LO`, may be blocked by NBIF protection until VF exclusive access is restored; the driver then disables/enables MSI-X so QEMU reprograms the table.

### PCI/PCIe Type-1 Configuration Header

The `PSWUSCFG0_1_*` block starts at `nbio_pcie0_pswuscfg0_cfgdecp` and maps a PCIe upstream switch/bridge configuration-space view. The first group mirrors conventional PCI/PCIe header fields:

- Identity and class-code fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command and status fields: `COMMAND` bits for IO/memory/bus-master enables, parity/SERR behavior, fast back-to-back, and interrupt disable; `STATUS` and `SECONDARY_STATUS` bits for capability list, interrupt status, target/master aborts, parity, and system errors.
- Bridge topology fields: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, upper prefetchable base/limit, `IO_BASE_LIMIT_HI`, and bridge-control bits in `IRQ_BRIDGE_CNTL`.
- Capability and ROM/interrupt fields: `CAP_PTR`, `ROM_BASE_ADDR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, vendor capability list, adapter ID, and power-management capability/status registers.

These masks describe PCI config-space semantics, but they are still generated into the ASIC register namespace because NBIO exposes the PCIe block through AMD register-access mechanisms.

### PCIe Capability, Link, MSI, and Vendor Capabilities

The chunk includes the PCIe capability and several standard/extended capabilities:

- `PCIE_CAP_LIST` and `PCIE_CAP` describe the PCIe capability ID, next pointer, version, device/port type, slot implementation, and interrupt-message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` cover payload size, phantom functions, extended tags, endpoint L0s/L1 acceptable latency, attention/power indicators, role-based error reporting, error enables, no-snoop, max read request, function-level reset, and error/status bits.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover max speed/width, ASPM, exit latencies, clock power management, bandwidth notifications, active-state link control, retrain/common-clock/extended-synch, negotiated speed/width, training, slot clock, and bandwidth status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeouts, ARI forwarding, atomic ops, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, FRS, supported link speeds, compliance settings, de-emphasis, equalization, crosslink, and downstream-component presence.
- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO/HI`, `MSI_MSG_DATA`, and `MSI_MSG_DATA_64` define MSI capability layout.
- `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, `MSI_MAP_CAP`, and vendor-specific capability/header/scratch fields define subsystem ID, MSI mapping, and vendor-specific extension data.

NBIO 2.3 code directly programs related PCIe/ASPM/LTR state through `RREG32_PCIE` and `WREG32_PCIE` in `amdgpu/nbio_v2_3.c`. Not every `PSWUSCFG0_1_*` macro is referenced by name in the driver, but this generated mask family supplies the same kind of field encodings used by PCIe link-management and power-management code.

### Virtual Channel, Serial Number, AER, and Link Equalization

The virtual-channel and error-reporting portions include:

- `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1/2`, `PCIE_PORT_VC_CNTL`, and `PCIE_PORT_VC_STATUS`.
- `PCIE_VC0_RESOURCE_CAP/CNTL/STATUS` and `PCIE_VC1_RESOURCE_CAP/CNTL/STATUS`, including traffic-class-to-VC mapping, arbitration table load/select/status, VC ID, enable, and negotiation pending.
- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` and serial-number low/high dwords.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, and `PCIE_ADV_ERR_CAP_CNTL`.
- Header and TLP prefix logs: `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3`.
- Secondary PCIe capability fields: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`.

These definitions are important for PCIe reliability and diagnostics. AER status/mask/severity fields cover data-link protocol errors, surprise down, poisoned TLPs, flow-control protocol errors, completion timeout/abort, unexpected completions, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violations, internal errors, multicast blocked TLPs, atomic-op egress blocking, TLP prefix blocking, and poisoned TLP egress blocking. Lane equalization fields provide per-lane downstream/upstream port transmit preset and preset hint encodings.

### ACS, Multicast, LTR, ARI, L1 PM Substates, and ESM

The end of the chunk covers additional PCIe extended capabilities:

- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress control vector size.
- `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0/1`, receive/block-all masks, block-untranslated masks, and overlay BAR fields for PCIe multicast.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP` for maximum snoop and no-snoop latency values and scales.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` for next-function number and function-group behavior.
- `PCIE_L1_PM_SUB_CAP_LIST`, `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2` for PCI-PM L1.1/L1.2, ASPM L1.1/L1.2, L1 PM substate support, common-mode restore time, power-on scale/value, T_POWER_ON programming, and threshold fields.
- `PCIE_ESM_CAP_LIST`, `PCIE_ESM_HEADER_1/2`, `PCIE_ESM_STATUS`, `PCIE_ESM_CTRL`, and `PCIE_ESM_CAP_1..5` for PCIe electrical speed margining presence/status/control and per-speed capability bits.

The ESM capability macros in this chunk enumerate fine-grained supported margining speeds from `ESM_2P5G` upward. `PCIE_ESM_CAP_1` covers 2.5G through 10.9G; `PCIE_ESM_CAP_2` covers 11.0G through 13.9G; `PCIE_ESM_CAP_3` covers 14.0G through 15.9G; `PCIE_ESM_CAP_4` covers 16.0G through 18.9G; and this chunk ends inside `PCIE_ESM_CAP_5`, after defining shift fields through `ESM_21P4G`. The matching masks and any remaining higher ESM fields continue in the next chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header. Its effect is compile-time substitution of constants into register reads, writes, field composition, and field extraction.

The persistent state described by these macros is hardware state:

- VF MMIO indirect-window state for index/data/high-index access.
- VF RCC SR-IOV status, doorbell aperture enablement, memory-size/configuration dwords, and function identity.
- VF BIF error logs, bus-master/DMA state, atomic error state, transaction-pending bits, and address-LUT bypass state.
- VF doorbell self-ring GPA aperture base/mode/size and mailbox valid/ack/message state.
- VF HDP flush request/done state for CP and SDMA engines.
- VF graphics MSI-X table and PBA state.
- PCI/PCIe bridge configuration, command/status, memory and IO windows, power-management state, PCIe link capabilities/control/status, MSI programming, AER logs/masks/severity, lane equalization state, ACS/ARI/LTR/multicast/L1 PM substate state, and ESM capability/control/status state.

Some fields are ordinary configuration bits, some are status bits, and some are clear or handshake bits. Examples include `CLEAR_DMA_ON_BME_LOW`, `CLEAR_UR_ATOMIC_*`, mailbox valid/ack bits, MSI-X mask bits, AER status bits, VC arbitration load/status bits, link retrain/control bits, L1 PM enable fields, and ESM control/status fields. The header does not encode ordering, privilege rules, write-one-to-clear behavior, or required polling loops; those rules must come from the hardware specification and owning AMDGPU/NBIO/PCIe code.

## Dependencies and Integration Points

Direct dependencies are the generated NBIO 2.3 register-header set:

- `nbio_2_3_offset.h` supplies the offsets and base indices for the register names defined here.
- `nbio_2_3_default.h` supplies reset/default values for generated registers where available.
- AMDGPU's register helper macros consume the `__SHIFT` and `_MASK` definitions.

Observed integration points in this source tree include:

- `amdgpu/nbio_v2_3.c`, which includes this header and implements the NBIO 2.3 function table. It programs PF doorbell apertures, HDP flush remap registers, interrupt control, clock gating, ASPM/LTR, and exposes HDP flush offsets and masks. The VF27-VF30 register families in this chunk mirror the PF/VF machinery used by those flows.
- `amdgpu/amdgpu_discovery.c`, which selects `nbio_v2_3_funcs` and `nbio_v2_3_hdp_flush_reg` for matching hardware.
- `amdgpu/mxgpu_nv.c`, which includes the NBIO 2.3 offset and mask headers for SR-IOV/MxGPU flows.
- `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c`, which include the NBIO 2.3 headers for power-management interactions.
- Display resource code for DCN generations that includes NBIO 2.3 offsets, tying display bring-up to the same NBIO register map.
- `amdgpu_device.c` resume handling for SR-IOV VFs, which notes that `GFXMSIX_VECT0_ADDR_LO` programming by QEMU can be blocked by NBIF protection until exclusive VF access is restored.

The `PSWUSCFG0_1_*` PCIe names appear mostly as generated definitions rather than direct high-level driver identifiers. The actual driver code often uses SMN constants, Linux PCI helpers, or related register names for ASPM, LTR, ESM, and link-management behavior, but those code paths rely on the same hardware contract represented here.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write the wrong hardware field, breaking SR-IOV isolation, doorbell routing, HDP coherency flushes, MSI-X delivery, PCIe link training, ASPM/LTR policy, AER handling, or PCI resource-window programming.
- The VF blocks are mechanically repeated for `VF27` through `VF30`. Copy-generation errors are easy to miss because the field layouts are almost identical but the register prefixes and offsets must stay VF-specific.
- Virtualization fields are privilege-sensitive. Incorrect `IOV_ENABLE`, function identifier, MMIO index/data aperture, doorbell aperture, mailbox, MSI-X, or error-clear definitions can let the PF, guest VF, or hypervisor observe or modify the wrong state.
- HDP flush request/done masks are engine-specific. Confusing CP bits with SDMA bits, or using PF masks against VF registers, can cause stale CPU/GPU memory visibility or flush waits that never complete.
- MSI-X table fields affect interrupt routing. Incorrect address-low alignment, message-data, vector mask, or PBA bits can lose interrupts or re-enable masked vectors. This is especially risky around VM resume, where the driver already documents NBIF protection interactions.
- PCIe config and capability fields are standardized but packed densely. Incorrect AER masks/severity, link-control bits, VC arbitration fields, ACS controls, ARI forwarding, L1 PM substate fields, or ESM control bits can cause link instability, incorrect error reporting, or security/isolation regressions.
- L1 PM and ASPM fields interact with platform firmware, Linux PCIe ASPM policy, and device removability. Programming these without path capability checks can create resume failures or poor link power behavior.
- This chunk starts and ends mid-family: it begins after most `VF26` MSI-X vector fields and ends inside `PSWUSCFG0_1_PCIE_ESM_CAP_5`. A merged report must connect adjacent chunks before treating either family as complete.

## Test and Validation Signals

Useful validation is mostly build-time and hardware/integration coverage:

- Build AMDGPU, SW SMU, display, and MxGPU/SR-IOV code that includes `nbio_2_3_sh_mask.h`; this catches missing, renamed, or syntactically invalid macros.
- Exercise NBIO 2.3 initialization through `nbio_v2_3_funcs`: doorbell aperture enable/disable, self-ring aperture programming, IH doorbell range setup, HDP remap setup, memory-size reads, and clock-gating state.
- Validate HDP coherency flush behavior for CP0-CP9 and SDMA0/SDMA1 paths by confirming request/done polling completes and no stale memory is observed across CPU/GPU synchronization.
- Run SR-IOV VF boot, reset, suspend/resume, and exclusive-access transitions with many VFs enabled, specifically covering high-numbered VFs if the platform exposes them.
- Verify VF MSI-X programming and interrupt delivery across VM resume. The expected signal is that MSI-X vectors are reprogrammed after exclusive access and guest interrupts continue arriving.
- Test VF mailbox transmit/receive valid/ack and interrupt enable paths, including hypervisor mailbox data, valid, and ack fields if supported by the platform.
- Run PCIe ASPM/LTR tests on removable and non-removable devices. Link state should enter expected low-power states without training failures or wake/resume regressions.
- Exercise PCIe AER injection or error-reporting diagnostics where available, checking uncorrectable/correctable status, mask, severity, header log, and TLP prefix log decoding.
- Validate PCIe link equalization and link status on different widths/speeds, including x4-specific workarounds in NBIO 2.3 code and downstream component presence/equalization status.
- Confirm ACS, ARI, multicast, VC, and L1 PM substate capability fields match Linux PCI enumeration and do not regress IOMMU/SR-IOV isolation expectations.
- For hardware that exposes electrical speed margining, read ESM capability/status/control and confirm the enumerated speed bits match platform expectations.

## Unresolved Cross-Chunk References

This chunk starts in the middle of the `VF26` MSI-X table and does not include `VF26` vector 0 through most of vector 3 address fields. It also ends inside `PSWUSCFG0_1_PCIE_ESM_CAP_5`, after shift definitions through `ESM_21P4G`; the matching masks and any remaining ESM fields belong to the next chunk. The merge/reconciliation lane should stitch those adjacent chunks before producing the final per-file research report.

### subset-b-002940: lines 88737-91171

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 88737-91171

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header segment. It contains preprocessor constants only: 2,141 `#define` macros in this line range, split into 1,059 `__SHIFT` definitions and 1,082 `_MASK` definitions. There are no C functions, structs, enums, local variables, allocation paths, locks, loops, branches, or direct MMIO accesses in the chunk.

The range starts in the tail of `PSWUSCFG0_1_PCIE_ESM_CAP_5`, covers the remainder of the `PSWUSCFG0_1` PCIe extended capability surface, crosses into the `nbio_nbif0_bif_bx_pf_SYSPFVFDEC:1` indirect PF/VF MMIO window, then covers most of the `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` downstream-port PCI/PCIe configuration-space masks. It ends at the first fields of `BIF_CFG_DEV0_EPF0_1_COMMAND` in the next `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, so both the first and last register groups are chunk-boundary partials.

Although this source path is under a local `ceph-client` mirror, the file is AMDGPU hardware metadata. It describes GPU NBIO/NBIF PCIe register fields, not Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit-level ABI for NBIO 2.3 PCIe configuration, link training, extended speed mode, margining, CCIX, downstream bridge, AER, ACS, data-link feature, and endpoint command fields. Matching offset macros in `nbio_2_3_offset.h` identify register addresses; this file identifies the bit positions and masks inside those registers.

Driver code consumes these macros through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_*`, `WREG32_*`, PCI config access helpers, and SOC15/NBIO-specific wrappers. The macro names are the contract: a typo or stale mask generally still compiles if the macro exists, but it can make the driver program the wrong hardware bit.

The main hardware surfaces in this chunk are:

- `PSWUSCFG0_1` PCIe extended capability fields for ESM capability bitmaps, data-link feature exchange, 16 GT/s PHY status, lane equalization, PCIe receiver margining, CCIX ESM controls/status, 20 GT/s and 25 GT/s lane equalization presets, and CCIX optimized TLP format control.
- `BIF_BX_PF0_MM_INDEX`, `BIF_BX_PF0_MM_DATA`, and `BIF_BX_PF0_MM_INDEX_HI` fields for an indirect PF/VF MMIO index/data aperture.
- `BIF_CFG_DEV0_SWDS1_*` PCI-to-PCI bridge and PCIe downstream-port configuration fields, including standard PCI header fields, bridge base/limit windows, PM capability, PCIe capability, device/link/slot capability and control/status, MSI, SSID, vendor-specific capability, virtual channel resources, device serial number, AER, secondary PCIe capability, per-lane equalization, ACS, data-link feature, 16 GT/s PHY, and lane margining fields.
- A partial `BIF_CFG_DEV0_EPF0_1_*` endpoint config-space start covering vendor ID, device ID, and the beginning of the PCI command register.

## Important Macro Families

### PSWUSCFG0_1 ESM, DLF, PHY, Margining, And CCIX

The first line of the chunk is already inside `PSWUSCFG0_1_PCIE_ESM_CAP_5`, carrying the final shifts and all masks for ESM speed support bits from `ESM_19P0G` through `ESM_21P9G`. The next full groups continue this bitmap pattern:

- `PSWUSCFG0_1_PCIE_ESM_CAP_6` covers `ESM_22P0G` through `ESM_24P9G`.
- `PSWUSCFG0_1_PCIE_ESM_CAP_7` covers `ESM_25P0G` through `ESM_28P0G`.

These are one-bit support masks for extended speed mode data-rate steps. The field names encode decimal speeds using `P` in place of a decimal point, and the masks are sequential single-bit values. This is highly regular generated data, but regularity is also the risk: a one-bit shift or name drift can advertise or control the wrong speed capability.

`PSWUSCFG0_1_PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` define the enhanced capability header fields plus local and remote data-link feature support. The capability/status pair includes `DLF_EXCHANGE_ENABLE` and `REMOTE_DLF_SUPPORTED_VALID`, so users must distinguish advertised capability, exchange enablement, and valid remote status.

`PSWUSCFG0_1_PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT` define the PCIe 16 GT/s PHY extended capability surface. The link status group exposes equalization-complete and phase-success bits plus link-equalization request status. The local/retimer parity status groups expose receiver/transmitter coefficient status mismatch bits.

`PSWUSCFG0_1_LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` repeat the same per-lane fields: downstream-port TX preset, downstream-port RX preset hint, upstream-port TX preset, upstream-port RX preset hint, and a reserved bit. The mask pattern is identical per lane, so generated-header consistency checks should expect only the lane number to change.

`PSWUSCFG0_1_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS` describe PCIe receiver margining support. The port capability fields include whether independent error sampler, voltage offset, timing offset, sample reporting, maximum lanes, and margining-time capabilities exist. The port status fields track ready state, margin software-ready status, margin command complete, margin command status, sampled receivers, and lane margining active.

`PSWUSCFG0_1_LANE_0_MARGINING_LANE_CNTL` through `LANE_15_MARGINING_LANE_STATUS` repeat per-lane margining command/status fields. Control registers carry receiver number, margin type, usage model, and payload; status registers mirror receiver number status, margin type status, usage model status, and payload status.

`PSWUSCFG0_1_PCIE_CCIX_*` groups define the CCIX extended capability header, CCIX-specific header words, ESM capability/status/control, optional/reserved ESM capability, required speed support, per-lane 20 GT/s and 25 GT/s ESM equalization presets, and CCIX transaction capability/control. The `PCIE_CCIX_ESM_CNTL` fields include data-rate selections, perform-calibration, enable, extended equalization phase timeouts, link-reach target, retimer-present, and quick-equalization timeout selection.

### PF/VF Indirect MMIO Window

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC:1` address block in this chunk contains:

- `BIF_BX_PF0_MM_INDEX__BIF_BX_PF_MM_REG_ADDR`
- `BIF_BX_PF0_MM_INDEX__BIF_BX_PF_MM_APER`
- `BIF_BX_PF0_MM_INDEX__BIF_BX_PF_MM_WR_EN`
- `BIF_BX_PF0_MM_DATA__BIF_BX_PF_MM_DATA`
- `BIF_BX_PF0_MM_INDEX_HI__BIF_BX_PF_MM_REG_ADDR`

These macros describe an indirect index/data access mechanism, where software selects a target register address/aperture and write-enable state through index fields, then transfers data through the data field. The macros do not enforce ordering; the runtime code using the register pair must perform index/data sequencing correctly.

### BIF_CFG_DEV0_SWDS1 Standard Bridge Header

The `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` address block begins with the downstream-port bridge's standard PCI configuration header:

- Identity and class fields: vendor ID, device ID, revision ID, programming interface, subclass, and base class.
- Command/status fields: I/O access, memory access, bus master, SERR, interrupt disable, parity/error status, target/master abort status, DEVSEL timing, and capability-list presence.
- Header and BIST fields: cache line size, latency timer, header type, multi-function device, and BIST controls/status.
- Bridge BAR and bus-window fields: base addresses, primary/secondary/subordinate bus numbers, secondary latency, I/O base/limit, memory base/limit, prefetchable base/limit and upper 32-bit windows, high I/O base/limit, ROM base, interrupt line/pin, and IRQ bridge control.

These masks map directly to conventional PCI/PCIe bridge configuration-space fields. Some fields are control bits, some are status or write-one-clear style PCI status bits, and some are base/limit encodings that require PCI bridge window semantics outside this header.

### BIF_CFG_DEV0_SWDS1 Power Management And PCIe Capabilities

The PM capability groups include `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. They define PM capability version, PME support, D1/D2 support, auxiliary current, power state, PME enable/status, data select/scale, and bus power enablement.

The PCIe capability groups include `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.

Notable field families include:

- Device error reporting enables/status bits for correctable, non-fatal, fatal, and unsupported-request conditions.
- Max payload size, max read request size, relaxed ordering, no-snoop, extended tags, atomics, ARI forwarding, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, and completion timeout controls.
- Link speed/width capability and status, ASPM/PM controls, common clock, link retrain/disable, bandwidth notification, DRS signaling, autonomous speed/width controls, equalization status, and retimer presence.
- Slot hot-plug, attention/power indicators, power controller, command complete, presence detect, data-link state change, physical slot number, and slot power limit fields.

### MSI, SSID, Vendor-Specific, VC, Serial Number, AER, Secondary, ACS, DLF, 16GT, And Margining

The SWDS1 MSI groups define the MSI capability list/header, address low/high, message data, 64-bit message data aliasing, mask, 64-bit mask aliasing, and pending fields. The overlapping MSI field names reflect PCI MSI layout variants; consumers must interpret them according to the MSI capability format, not as unique independent storage.

`BIF_CFG_DEV0_SWDS1_SSID_*` exposes subsystem vendor and subsystem IDs. `PCIE_VENDOR_SPECIFIC_*` exposes vendor-specific capability header and data words.

The VC enhanced capability block covers port VC capability/control/status, VC0 and VC1 resource capability/control/status, arbitration capability, TC/VC maps, load-table controls, and VC negotiation pending status. These fields affect virtual channel resource allocation and traffic class routing.

`PCIE_DEV_SERIAL_NUM_*` exposes the device serial number enhanced capability header and two data dwords.

The AER block exposes uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs. The status/mask/severity macros distinguish DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic egress blocked, and TLP prefix blocked conditions.

The secondary PCIe capability block exposes link control 3, lane error status, and lane 0-15 equalization controls. Each lane equalization control repeats downstream TX preset, downstream RX preset hint, upstream TX preset, upstream RX preset hint, and reserved fields.

The ACS enhanced capability block exposes source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer-to-peer egress control, direct translated peer-to-peer, and egress control vector size/control enablement. These fields are especially sensitive for IOMMU, virtualization, and peer-to-peer isolation.

The SWDS1 DLF, 16 GT/s PHY, and margining groups mirror the same concepts as the earlier `PSWUSCFG0_1` groups, but under the downstream-port `BIF_CFG_DEV0_SWDS1_*` namespace. The 16 GT/s status and parity fields describe equalization phase status and coefficient mismatch states. The lane 0-15 margining control/status groups repeat receiver number, margin type, usage model, and payload fields.

### Partial Endpoint Config Start

The chunk ends after entering `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`. It includes complete masks for `BIF_CFG_DEV0_EPF0_1_VENDOR_ID` and `DEVICE_ID`, then starts `BIF_CFG_DEV0_EPF0_1_COMMAND` with shifts for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, palette snoop, parity error response, address/data stepping, SERR, fast back-to-back, and interrupt disable. The corresponding masks for this command register continue in the next chunk.

## Control Flow

There is no executable control flow in this header chunk. The runtime flow is provided by C code that includes the generated NBIO 2.3 headers:

1. A driver path selects an ASIC/IP-version-specific register offset from `nbio_2_3_offset.h`.
2. It selects one or more field masks/shifts from this `nbio_2_3_sh_mask.h` file.
3. It reads or writes the register through PCI config, SMN, SOC15, or NBIO access helpers.
4. For field updates, it uses read/modify/write helpers or explicit mask/shift operations to preserve unrelated fields.
5. Hardware applies the effect as PCIe capability presentation, link training/equalization control, error reporting, margining, CCIX ESM control, bridge-window programming, MSI/VC/ACS setup, or endpoint command behavior.

In-tree include points for `nbio_2_3_sh_mask.h` are `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 PPT files `navi10_ppt.c` and `sienna_cichlid_ppt.c`. A direct symbol search over the main AMDGPU, PM, and display C/H trees did not find references to the exact `PSWUSCFG0_1_*`, `BIF_CFG_DEV0_SWDS1_*`, or `BIF_CFG_DEV0_EPF0_1_*` macro names from this chunk, so the most likely consumers are lower-level config-space tooling, generated-register consistency, hardware diagnostics, or indirect use through versioned include coverage rather than explicit named calls in the checked C files.

## State And Persistence Behavior

This header stores no software state and persists nothing to disk. Its macros describe hardware-backed state whose lifetime is controlled by reset type, PCIe configuration, firmware/BIOS setup, driver programming, power-state transitions, link retraining, hot reset/FLR, and SR-IOV or PF/VF policy where applicable.

The represented hardware state includes:

- ESM and CCIX capability, status, calibration, data-rate, retimer, timeout, and optimized TLP format fields.
- Data-link feature local/remote capability and exchange state.
- 16 GT/s equalization and parity mismatch status for local and retimer paths.
- Per-lane equalization presets and margining command/status payloads for 16 lanes.
- PF/VF indirect MMIO index/data aperture selector and data fields.
- PCI bridge config state: command, status, class, BARs, bus numbers, I/O and memory windows, prefetchable windows, ROM base, interrupts, and bridge control.
- PCIe PM, device, link, slot, MSI, SSID, vendor-specific, VC, serial-number, AER, secondary PCIe, ACS, DLF, PHY, and margining capability state.
- Endpoint vendor/device ID and PCI command state at the chunk tail.

Some fields are persistent configuration until reset or reprogramming, such as command bits, bridge windows, link controls, MSI control, VC resource controls, ACS controls, and CCIX/ESM controls. Other fields are live status, latched error, write-one-clear, log, or capability-reporting fields. The header does not encode those access semantics, so callers must rely on the PCIe specification, AMD's ASIC register database, and existing AMDGPU access patterns.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies generated defaults where available.
- AMDGPU register helper conventions such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and related NBIO/SMN/SOC15 access wrappers.
- PCI and PCIe config-space semantics for standard bridge headers, capabilities, enhanced capabilities, AER, ACS, MSI, VC, DLF, PHY, margining, and CCIX.

Important integration points are:

- NBIO bring-up and link-management code in `nbio_v2_3.c`, which includes this header family and programs PCIe, ASPM/LTR, clock-gating, interrupt, doorbell, and HDP-related NBIO state using adjacent NBIO 2.3 masks.
- MxGPU/virtualization code in `mxgpu_nv.c`, which includes this register family for NBIO state relevant to PF/VF coordination.
- SMU11 power-management code in `navi10_ppt.c` and `sienna_cichlid_ppt.c`, which includes the NBIO 2.3 masks and offsets for ASIC-specific power-management register access.
- Hardware debug or validation tooling that walks PCIe enhanced capabilities, checks lane equalization/margining status, reads AER logs, verifies ACS/VC setup, or inspects CCIX/ESM capability state.

## Risks And Edge Cases

- Generated hardware contract drift is the primary risk. A wrong shift or mask can compile cleanly but program or read the wrong bit in hardware.
- Chunk boundaries are artificial. The range starts mid-`PSWUSCFG0_1_PCIE_ESM_CAP_5` and ends mid-`BIF_CFG_DEV0_EPF0_1_COMMAND`; the final per-file report must merge adjacent chunks before claiming complete coverage of those registers.
- Repeated per-lane blocks are easy to corrupt mechanically. A lane-number mismatch, missing field, or copied mask from the wrong lane can break equalization or margining on one lane while others work.
- ESM speed capability bitmaps are sequential and dense. Off-by-one shifts can advertise unsupported speeds or hide supported speeds, causing link-training, CCIX, or diagnostic confusion.
- PCI status, AER status, slot status, and some error fields can have write-one-clear behavior. Treating all masks as ordinary persistent control bits can accidentally clear diagnostics or fail to clear latched errors.
- Bridge base/limit fields are encoded PCI windows, not raw byte addresses. Consumers must apply PCI bridge sizing/alignment rules when interpreting or programming them.
- MSI fields intentionally alias depending on 32-bit versus 64-bit MSI layout. Code must choose the proper interpretation based on MSI capability state.
- ACS and VC fields affect isolation and routing. Incorrect masks can break peer-to-peer isolation, IOMMU behavior, traffic class routing, or virtualization assumptions.
- Indirect MMIO index/data fields require strict sequencing. Writing data before the correct index/aperture/write-enable fields are set can target the wrong register.
- Link control, equalization, margining, CCIX ESM, and retimer fields are timing-sensitive. Bad field definitions can produce intermittent link training failures, margining timeouts, or speed-dependent behavior rather than immediate deterministic errors.

## Test Signals

Useful validation signals for this chunk are mostly generated-header checks, build coverage, and hardware/runtime PCIe tests:

- Build AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c`; missing renamed macros or include-order problems should surface at compile time.
- Run generated-header consistency checks: each field should usually have a matching `__SHIFT` and `_MASK`, masks should align with the shift and field width, and repeated lane 0-15 blocks should differ only in lane numbering.
- Compare representative fields against the matching `nbio_2_3_offset.h` register groups and AMD NBIO 2.3 register database, especially chunk-boundary groups, ESM capability bitmaps, PCIe AER/ACS groups, and per-lane equalization/margining blocks.
- Exercise PCIe enumeration and config-space reads for the downstream bridge and endpoint surfaces; vendor/device IDs, class code, capability pointers, bridge windows, MSI, AER, ACS, VC, DLF, PHY, and margining capability headers should decode correctly.
- Exercise link training, retraining, ASPM, LTR, and speed changes around 16 GT/s and extended-speed/CCIX capability paths. Failures can show up as bad negotiated speed/width, equalization phase failure, or repeated link retraining.
- Use PCIe AER injection or diagnostics where available; correctable and uncorrectable status/mask/severity fields should latch, report, and clear without disturbing unrelated fields.
- Validate ACS and VC behavior under IOMMU, peer-to-peer, and virtualization scenarios; routing or isolation regressions are strong indicators of mask drift.
- Exercise receiver margining diagnostics across all lanes; per-lane command/status payloads should be lane-correct and should not cross-write adjacent lane fields.
- Validate indirect PF/VF MMIO index/data access in any debug or virtualization path that uses this aperture; wrong register selection, stale data, or unexpected write effects point at index/data field drift.

### subset-b-002941: lines 91172-93606

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 91172-93606

## Scope

This chunk covers generated AMD NBIO 2.3 shift/mask definitions for the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, specifically the `_1` instance of `BIF_CFG_DEV0_EPF0`. It begins inside the `BIF_CFG_DEV0_EPF0_1_COMMAND` field definitions, then covers EPF0_1 PCI configuration header fields, PCI/PCIe capabilities, MSI/MSI-X, extended PCIe capabilities, link equalization and margining, SR-IOV and VF BAR controls, and AMD vendor-specific GPUIOV fields through the first `GPUIOV_UVD1SCH_DW0` shift macro.

The chunk is data-only C preprocessor material. It declares no functions, structs, variables, locks, allocation paths, or direct register accesses. Its interface is the standard generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT` for a field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field mask.

Within this line range there are 2,097 `#define` entries across 339 register groups, nearly all forming shift/mask pairs.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield-layout side of the NBIO 2.3 hardware ABI. The matching `nbio_2_3_offset.h` header supplies the register/config-space addresses, and AMDGPU register helpers combine those offsets with these masks when composing writes or decoding reads.

This chunk describes the PCIe configuration surface for EPF0 function instance 1. It includes conventional PCI fields such as command/status, identity/class/header registers, BARs, ROM BAR, adapter/subsystem ID, interrupt line/pin, and capability pointers. It then describes PCIe capability and extended-capability fields for power management, link/device controls, MSI/MSI-X, virtual channels, device serial number, AER, resizable BARs, power budget, DPA, secondary PCIe, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s PHY, lane margining, VF resizable BAR, and AMD GPUIOV.

These definitions matter because EPF0_1 appears to expose a PCIe endpoint/function configuration image whose bit layout must be shared by the driver, firmware, hardware, PCI core, virtualization paths, and diagnostic tooling. A caller cannot use this header alone to access hardware, but every caller that programs or reports these fields depends on its masks being exact.

## Important Macro Families

### PCI Header and Base Capability Fields

The first portion covers `BIF_CFG_DEV0_EPF0_1_COMMAND` and `STATUS`, revision and class-code fields, cache-line/latency/header/BIST fields, BARs 1-6, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency. Command bits include I/O access, memory access, bus mastering, SERR, parity response, and interrupt disable. Status bits include capability-list presence, interrupt status, target/master abort status, system error, and parity detection.

Power management and PCIe capability fields follow:

- `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define PM capability list linkage, D-state support, PME support/enables/status, data select/scale, bus power, and power-state fields.
- `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` define endpoint type, payload/read-request sizing, error-report enables, relaxed ordering/no-snoop, FLR initiation, AUX power, transaction pending, and related device capabilities.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` define supported/current speed and width, ASPM/L0s/L1 behavior, clock and bandwidth controls, retraining, link disable, common clock, slot clock, compliance, and bandwidth status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` expose PCIe 2+ feature bits such as completion timeout support/control, LTR, atomic operations, ARI forwarding, ID-based ordering, OBFF, emergency power reduction, ten-bit tags, TLP prefix blocking, supported link-speed vector, target speed, equalization controls/status, crosslink, and downconfigure status.

### Interrupt and Vendor/Virtual-Channel Capabilities

MSI and MSI-X definitions include capability-list linkage, message control, 32-bit and 64-bit message address/data layouts, mask and pending registers, MSI-X table fields, and pending-bit-array fields. The presence of both regular and `_64` message-data/mask/pending families reflects layout-dependent interpretation of the MSI capability, not independent interrupt mechanisms.

The non-GPUIOV vendor-specific and virtual-channel sections include `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, `PCIE_VENDOR_SPECIFIC2`, `PCIE_VC_ENH_CAP_LIST`, port VC capabilities/control/status, and VC0/VC1 resource capability/control/status fields. These cover extended capability IDs/versions/next pointers, vendor capability metadata, low-priority and reference-clock VC counts, arbitration table offsets, TC/VC mapping, load table controls, arbitration select, and negotiation status.

### Error Reporting, BAR, Power, and Link Training Extensions

The AER block defines uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control fields, four header-log dwords, and four TLP-prefix-log dwords. Important field families include data link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, receiver error, bad TLP/DLLP, replay rollover, advisory non-fatal, corrected internal error, and header-log overflow.

Resizable BAR, power budget, and DPA definitions cover BAR1-BAR6 capability/control fields, power budget data selection and reporting, DPA capability, DPA latency/status/control, and eight DPA substate power allocation registers.

Secondary PCIe and PHY/link-training definitions include `PCIE_LINK_CNTL3`, lane error status, per-lane 8 GT/s equalization control for lanes 0-15, 16 GT/s enhanced capability linkage, 16 GT/s link capability/control/status, parity mismatch status fields, and per-lane 16 GT/s equalization control for lanes 0-15. These fields describe preset/hint values, equalization phase success, retimer/link-equalization request status, and lane-level training diagnostics.

### Isolation, Address Translation, and Virtualization Fields

ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, and data-link feature blocks define a broad PCIe virtualization and fabric-integration surface:

- `PCIE_ACS_CAP` and `PCIE_ACS_CNTL` expose source validation, translation blocking, peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size/control fields.
- `PCIE_ATS_CAP` and `PCIE_ATS_CNTL` expose invalidation queue depth, page-aligned request support, small-page invalidation, and ATS enable/STU fields.
- `PCIE_PAGE_REQ_*`, outstanding page request capacity/allocation, `PCIE_PASID_*`, multicast, LTR, and ARI blocks describe address-translation participation, PASID width and modes, multicast address/blocking state, snoop/no-snoop latency encoding, and alternative routing ID forwarding/function-group behavior.
- `PCIE_SRIOV_*` fields define SR-IOV capability/control/status, initial/total/current VF counts, dependency link, first VF offset, VF stride, VF device ID, page sizes, VF BAR base-address fields, and migration state array offset.
- `PCIE_TPH_REQR_*` and data-link feature fields define TPH requester capabilities/control and data-link feature exchange support/status.

### Lane Margining and GPUIOV

The PCIe margining block contains a port capability/status pair and per-lane lane-margining control/status pairs for lanes 0-15. Each lane pair has receiver number, margin type, usage model, and payload fields, with status variants reporting the resulting receiver/type/model/payload.

VF resizable BAR definitions cover VF BAR1-BAR6 capability/control fields. The AMD GPUIOV vendor-specific block then exposes a second vendor-specific extended capability header, a GPUIOV-specific header, an SR-IOV shadow field, interrupt enable/status bits for guest/PF/VF FLR and doorbell events, reset control, hypervisor/VM mailbox dwords, context, total framebuffer, offsets, region selection, P2P-over-XGMI enablement, per-VF framebuffer size/offset pairs for VF0 through VF30, and scheduler descriptor dwords for UVD, VCE, and GFX. The chunk ends at `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW0__DW0__SHIFT`; the matching mask and later UVD1 scheduler dwords continue outside this chunk.

## Control Flow

There is no executable control flow in this header. Runtime behavior is entirely external:

1. AMDGPU or related code includes the NBIO 2.3 offset, default, and shift/mask headers.
2. Code chooses a register address from `nbio_2_3_offset.h` and a field mask/shift from this header.
3. Helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_*`, `WREG32_*`, or PCIe index/data accessors shift, mask, read, and write the field.
4. Hardware, firmware, the Linux PCI core, or a virtualization manager observes the resulting PCIe configuration or vendor-specific state.

Because this chunk represents PCIe configuration-space and vendor-specific capability fields, not ordinary driver-owned memory, many side effects are defined by PCIe/NBIO hardware semantics rather than C control flow.

## State and Persistence Behavior

The macros are compile-time constants and have no local persistence. The state they name is hardware-visible NBIO/PCIe configuration state. Persistence depends on the owning register:

- PCI identity, class, header, capability-chain, capability support, BAR capability, supported link speed/width, supported page size, and similar capability fields are generally read-only or read-mostly values established by hardware straps, firmware, or configuration logic.
- Command, PM status/control, device/link control, MSI/MSI-X control, VC control, ACS/ATS/PASID/ARI/SR-IOV control, TPH control, DPA control, margining control, VF resize BAR control, GPUIOV interrupt enable, reset control, framebuffer partitioning, P2P-over-XGMI, and scheduler fields are mutable hardware configuration state.
- Status/log fields such as PCI status, device/link status, AER status, AER header/TLP prefix logs, VC status, DPA status, lane error status, 16 GT/s equalization/parity status, margining status, data-link feature status, SR-IOV status, page request status, and GPUIOV interrupt status are transient diagnostic or event state.
- Reset, FLR, GPU reset, VF teardown, power transitions, firmware ownership changes, and hypervisor actions can clear or reinitialize many fields. The header does not encode save/restore ordering or ownership rules.

Several fields are command-like or write-one-to-clear in PCIe-style hardware, including FLR initiation, link retraining, AER and PCI status bits, interrupt status, page request status, and possibly lane/error logs. The masks only identify bit positions; callers need the hardware specification and owning subsystem policy before writing them.

## Dependencies and Integration Points

Direct dependencies:

- `nbio_2_3_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_1_*` addresses for these field definitions.
- `nbio_2_3_default.h` supplies reset/default values for the same generated hardware family.
- AMDGPU register helpers and SOC15/PCIe accessors supply the actual read/modify/write mechanics.
- Linux PCI/PCIe semantics define many standard fields mirrored here: PM, PCIe capability, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, LTR, ARI, SR-IOV, TPH, VC, DPA, resizable BAR, lane equalization, and margining.

Observed source-tree integration for this header family includes AMDGPU NBIO 2.3 code and virtualization/SMU platform code that include `nbio_2_3_sh_mask.h` alongside offset/default headers. The specific EPF0_1 definitions align with `cfgBIF_CFG_DEV0_EPF0_1_*` entries in `nbio_2_3_offset.h`, including the GPUIOV block beginning around the `0xfffe10200504` configuration-space region.

Integration-sensitive areas include:

- PCI core ownership of command/status, BAR sizing, PM, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, SR-IOV, and link-control policy.
- AMDGPU NBIO initialization and power-management flows that may read or program PCIe link, LTR, ASPM, DPA, and data-link feature state.
- SR-IOV and GPUIOV PF/VF lifecycle code, including VF enumeration, VF BAR exposure, FLR/reset handling, mailbox signaling, interrupt routing, framebuffer partitioning, and per-engine scheduling descriptors.
- Diagnostics and debug tooling that decode AER, lane equalization, lane margining, parity mismatch, data-link feature, and GPUIOV interrupt/status registers.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can silently modify an adjacent PCIe/NBIO bit while compiling cleanly.
- Register/address mismatches are easy. These macros do not carry addresses; callers must pair `BIF_CFG_DEV0_EPF0_1_*` masks with the matching `cfgBIF_CFG_DEV0_EPF0_1_*` offsets.
- EPF/function suffixes matter. `EPF0_1` definitions are mechanically similar to neighboring EPF0, EPF1, and VF blocks; using the wrong suffix can target the wrong endpoint/function image.
- PCI core policy conflicts can occur if AMDGPU directly writes MSI/MSI-X, AER, ACS, ATS, PASID, SR-IOV, BAR, PM, or link-control fields outside a coordinated path.
- Status and log fields can be destructive to write. PCI status, AER status/logs, page request status, GPUIOV interrupt status, and lane diagnostics may use write-one-to-clear or capture-first-error behavior.
- Link training and margining fields are timing-sensitive. Equalization presets, target speed, retraining, compliance, lane margining payloads, and 16 GT/s controls can destabilize the PCIe link if changed outside expected link states.
- Virtualization fields are isolation-sensitive. SR-IOV, ATS/PASID/PRI, ACS, GPUIOV mailbox, framebuffer partitioning, reset, interrupt, P2P-over-XGMI, and scheduler fields can affect guest isolation, DMA translation, and active VF workloads.
- Chunk boundaries are partial. The first `COMMAND` comment and field start are before line 91172, and the UVD1 scheduler block continues after line 93606. File-level conclusions need reconciliation with neighboring chunks.

## Test and Validation Signals

Useful validation for changes touching this chunk or callers of its macros includes:

- Build coverage for AMDGPU code paths that include `nbio_2_3_sh_mask.h` with the matching NBIO 2.3 offset/default headers.
- Static generated-header checks comparing `BIF_CFG_DEV0_EPF0_1_*` field names against `cfgBIF_CFG_DEV0_EPF0_1_*` offsets and neighboring generated NBIO revisions to catch missing fields, suffix drift, and mask-width changes.
- PCIe enumeration checks with `lspci -vv` or equivalent should show sane command/status, BARs, PM, PCIe, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, LTR, ARI, SR-IOV, resizable BAR, and link capability data.
- Link tests should verify negotiated speed/width, ASPM/LTR behavior, retraining, equalization, 16 GT/s status, lane error status, and margining readiness across boot, suspend/resume, runtime power management, and GPU reset.
- SR-IOV/GPUIOV tests should cover VF creation/removal, VF BAR sizing, VF memory-space enablement, FLR/reset handling, mailbox traffic, per-VF framebuffer partition reporting, interrupt enable/status behavior, and guest driver load/unload.
- Error-injection or fault-observation tests should verify AER uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, PCI status bits, and clear behavior.
- Interrupt tests should validate MSI/MSI-X message programming, mask/pending behavior, table/PBA interpretation, and interaction with GPUIOV interrupt status.
- Power-management tests should watch DPA, PM state, LTR, OBFF, ASPM, data-link feature, and link low-power behavior for latency or stability regressions.

## Unresolved Cross-Chunk References

Line 91172 starts after the beginning of the `BIF_CFG_DEV0_EPF0_1_COMMAND` field list, so earlier command fields and the `addressBlock` marker are immediately before this chunk. Line 93606 ends at the `GPUIOV_UVD1SCH_DW0` shift definition; the matching mask and additional UVD1 scheduler dwords continue in the next chunk. The final per-file document should stitch those boundaries before making complete claims about the full EPF0_1 map.

### subset-b-002942: lines 93607-96044

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 93607-96044

## Scope

This chunk covers a generated AMD NBIO 2.3 shift/mask header section for PCIe configuration-space bitfields. It starts in the tail of `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW0`, contains `DW1` through `DW8` for that EPF0 UVD1 GPUIOV scheduler block, then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and defines most of endpoint function 1 instance 1 (`BIF_CFG_DEV0_EPF1_1_*`). The range ends at the comment for `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VCESCH_DW7`; that register's field macros continue in the next chunk.

The file is data-only generated C preprocessor material. It defines no functions, structs, variables, locks, allocations, persistence code, or direct MMIO operations. Its public interface is the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` for the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field's mask.

There are 2097 `#define` entries in this line range.

## Purpose

This header section is the bitfield side of the NBIO 2.3 PCIe configuration ABI used by AMDGPU. The companion `nbio_2_3_offset.h` file supplies matching config-space addresses or offsets, while `nbio_2_3_default.h` supplies reset/default values. Driver code can then compose and decode register values through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, and `WREG32_FIELD15` without hard-coding bit numbers.

Most of the chunk describes how EPF1 exposes normal PCI/PCIe endpoint configuration: command/status, BARs, power management, PCIe link/device controls, MSI/MSI-X, vendor-specific capabilities, virtual channels, AER, resizable BAR, power budgeting, dynamic power allocation, secondary PCIe capability, ACS/ATS/PASID/page request/LTR/ARI/SR-IOV, multicast, TPH, data link features, 16 GT/s PHY controls, lane margining, VF resizable BAR, and AMD GPUIOV vendor-specific state.

## Important Macro Families

### EPF0 GPUIOV UVD1 Tail

Lines 93607-93631 complete the previous endpoint block by defining full-width `DW1` through `DW8` masks for `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_*`. Each covered register is a 32-bit scheduler dword with a `DWn` field at shift `0x0` and mask `0xFFFFFFFFL`. The comment for `DW0` and its shift live in the previous chunk, so this range is only a boundary tail for EPF0.

### EPF1 Standard PCI Header and Power Management

The `BIF_CFG_DEV0_EPF1_1_*` block begins with standard PCI header fields:

- `VENDOR_ID`, `DEVICE_ID`, revision/class/prog-interface fields, cache line, latency, BIST, six BAR registers, CardBus CIS pointer, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max grant fields.
- `COMMAND` exposes IO, memory, bus-master, special-cycle, memory-write-invalidate, snoop, parity response, SERR, fast back-to-back, and interrupt-disable bits.
- `STATUS` exposes readiness, interrupt status, capability-list presence, parity and abort status, SERR, and DEVSEL timing.
- `ADAPTER_ID` and `ADAPTER_ID_W` pack subsystem vendor and subsystem ID as 16-bit fields.

The power-management capability is represented by `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. These define capability-list linkage, PME support, D-state support, auxiliary current, current power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PMI data.

### PCIe Capability, Link, Device, MSI, and MSI-X

The PCIe capability block defines:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for max payload/read-request policy, error reporting enables/status, relaxed ordering, no-snoop, extended tags, auxiliary power, pending transactions, emergency power reduction, and FLR initiation/capability.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for supported/current link speed, link width, ASPM/PM support, exit latencies, retraining, common clock, extended sync, clock power management, link disable, link bandwidth notification, data link active reporting, and training/status bits.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout, ARI forwarding, atomic ops, ID-based ordering, LTR, TPH completer support, 10-bit tags, OBFF, end-to-end TLP prefixes, emergency power reduction, FRS, supported link speeds, compliance controls, de-emphasis, 8 GT/s equalization status, RTM presence, crosslink state, and DRS status.

Interrupt configuration is covered by MSI and MSI-X masks. MSI fields include enable, multi-message capability/enable, 64-bit address capability, per-vector masking, message address/data, mask, and pending bits. MSI-X fields include table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

### Vendor-Specific Capability and Virtual Channels

`PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` describe a conventional VSEC header plus two full-width scratch dwords. These are separate from the later AMD GPUIOV VSEC.

The virtual-channel capability block defines capability-list linkage, port VC capability registers, VC arbitration table load/select/status fields, and resource capability/control/status for VC0 and VC1. Resource controls map traffic classes to VCs, load port arbitration tables, select arbitration policy, set VC ID, and enable a VC. Status bits indicate arbitration-table status and VC negotiation pending.

### Device Serial Number, AER, BAR Resize, Power Budget, and DPA

The device serial number capability exposes two full-width serial dwords.

The AER block defines uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header logs, and TLP prefix logs. Covered fields include data link protocol error, poisoned TLP, flow-control protocol error, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, correctable receiver/bad-TLP/bad-DLLP/replay/Advisory Non-Fatal/internal/header-log-overflow status, ECRC generation/check enables, and multiple-header recording.

Resizable BAR fields cover BAR1 through BAR6 capability/control pairs. Each capability has a supported-size bitmap and each control has BAR index, total BAR count, and selected size.

Power budgeting is represented by capability-list, data select, data payload, and capability registers. DPA fields describe substate maximum count, transition latency unit/value, DPA status, DPA enable, and eight substate power-allocation registers.

### Secondary PCIe Capability and Lane Controls

The secondary PCIe capability block defines `LINK_CNTL3`, lane error status, and per-lane equalization control for lanes 0 through 15. Equalization control fields repeat the same layout per lane: downstream TX preset, downstream RX preset hint, upstream TX preset, upstream RX preset hint, and a reserved bit. The 16 GT/s PHY block later mirrors this idea with link capability/control/status, parity mismatch status, and per-lane 16 GT/s equalization controls.

The PCIe margining capability defines port-level capability/status and per-lane margining control/status for lanes 0 through 15. Per-lane control/status fields carry receiver number, margin type, usage model, and margin payload. These are diagnostic and signal-integrity related rather than ordinary runtime policy fields.

### ACS, ATS, Page Request, PASID, Multicast, LTR, ARI, and SR-IOV

The chunk defines several PCIe extended capabilities that matter for virtualization and IOMMU integration:

- ACS capability/control fields cover source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-control vector size.
- ATS fields expose invalidation queue depth and enable/stall controls.
- Page Request fields expose enable/reset and response-failure status.
- PASID fields expose execute permission, privileged mode support/enable, and PASID width.
- Multicast fields expose max group/window size, ECRC regeneration, enable, group count, base address, receive vectors, block-all vectors, and block-untranslated vectors.
- LTR exposes snoop and no-snoop max latency value/scale.
- ARI exposes function-group capabilities, next function number, enables, and function group.
- SR-IOV exposes VF migration capability/status, ARI hierarchy preservation, VF 10-bit tag requester support/enable, VF enable, VF memory-space enable, initial/total/current VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, six VF BARs, and migration state array offset.

These fields are closely tied to host PCI enumeration, IOMMU behavior, and PF/VF isolation.

### TPH, Data Link Feature, 16 GT/s PHY, and VF Resizable BAR

TPH requester capability/control fields describe supported steering tag modes, extended requester support, steering table location/size, selected steering mode, and TPH enable.

The data link feature capability exposes feature capability and status registers. The covered field names include data-link feature exchange enable/capability style fields and status bits that software may use during link-feature negotiation or diagnostics.

The 16 GT/s PHY capability block includes link capability/control/status, local and retimer parity mismatch status, and lane 0-15 16 GT/s equalization control fields. The 16 GT/s lane controls use downstream/upstream preset and coefficient fields that are more detailed than the older 8 GT/s equalization masks.

The VF resizable BAR capability mirrors the PF BAR resize block for VF BAR1 through VF BAR6, with supported-size bitmaps and controls for VF BAR index, total VF BAR count, and selected VF BAR size.

### GPUIOV Vendor-Specific Region

The AMD GPUIOV VSEC begins with `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV`, then exposes virtualization control and communication fields:

- `SRIOV_SHADOW` carries a shadow VF enable bit and VF count.
- `INTR_ENABLE` and `INTR_STATUS` define GFX, UVD, UVD1, and VCE command-complete, self-recovered hang, need-FLR hang, and VM-busy-transition interrupt bits, plus HVVM mailbox transmit-ack and receive-valid interrupt bits.
- `RESET_CONTROL` defines GFX, UVD, UVD1, and VCE VF FLR controls and per-engine scheduler reset bits.
- `HVVM_MBOX_DW0` through `DW2` expose full-width mailbox dwords for hypervisor/VM communication.
- `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `REGION`, and `P2P_OVER_XGMI_ENABLE` describe GPUIOV context count/size style metadata, total framebuffer partitioning, offsets, region selection, and XGMI peer-to-peer enablement.
- `VF0_FB` through `VF30_FB` each pack a 16-bit VF framebuffer size and a 16-bit VF framebuffer offset.
- `UVDSCH_DW0` through `DW8` and `VCESCH_DW0` through `DW6` are full-width scheduler dwords for video decode and encode scheduling. `VCESCH_DW7` starts at the chunk boundary and is completed by the next chunk.

## Control Flow and State Behavior

There is no executable control flow in this header. It changes behavior only at compile time by giving C code the correct bit positions and masks for hardware-backed PCIe configuration registers.

The state represented here is hardware state exposed through PCI configuration space or AMD vendor-specific configuration windows. Important persistent state includes PCI command enables, BAR and ROM BAR values, power-management state, PCIe link and device control, MSI/MSI-X message routing and masks, VC arbitration/resource state, AER masks/status/severity/logs, resizable BAR selections, DPA allocations, secondary PCIe equalization controls, ACS/ATS/PASID/page-request controls, multicast filters, ARI/SR-IOV configuration, VF BARs, GPUIOV interrupt enables/status, reset controls, mailbox dwords, per-VF framebuffer partitions, and video scheduler dwords.

Several fields are status, sticky status, or command-like rather than ordinary durable configuration. Examples include PCI/AER error status, PME status, link training/equalization status, MSI pending bits, VC negotiation pending, page request response failure, SR-IOV migration status, GPUIOV interrupt status, FLR/reset controls, mailbox handshake bits, and margining status. Correct users need the sequencing and clearing rules from PCIe, hardware documentation, and the owning AMDGPU virtualization paths; the masks alone do not define ordering, polling, or timeout behavior.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register header set:

- `nbio_2_3_offset.h` supplies matching register/config-space offsets and base indices.
- `nbio_2_3_default.h` supplies reset/default values for the same register names.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions to compose and decode fields.

Observed source-tree integration includes `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h` and uses SOC15/PCIe helpers for NBIO programming. Related MXGPU/SR-IOV code paths depend on the same generated definitions for VF enablement, FLR handling, doorbell/interrupt setup, and virtualization-visible PCIe state. The PCI core and host firmware also interact indirectly with these fields through normal PCI configuration-space enumeration and capability negotiation.

Cross-generation similarity is high but not interchangeable. Other NBIO/NBIF headers contain similar EPF, SR-IOV, GPUIOV, AER, and lane-control names with different prefixes, offsets, capability ordering, or field layouts. Consumers must include the matching NBIO 2.3 offset/mask/default set for this ASIC generation.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write an unrelated PCIe field, causing failed enumeration, link instability, lost interrupts, broken BAR sizing, failed FLR, incorrect power policy, or GPU hangs.
- The EPF1 block is large and repetitive. PCIe capability lists, per-lane equalization/margining, BAR resize, VF BAR, VF framebuffer, and scheduler dword families are easy to damage mechanically.
- Virtualization fields are isolation-sensitive. Incorrect ACS, ATS, PASID, ARI, SR-IOV, GPUIOV shadow, VF BAR, VF framebuffer, P2P-over-XGMI, or reset-control masks can break PF/VF isolation or expose the wrong memory aperture.
- Error and interrupt fields include enable, status, mask, and severity variants with similar names. Mixing AER status/mask/severity or GPUIOV interrupt enable/status fields can mask real faults or create spurious interrupts.
- Link training, equalization, 16 GT/s PHY, and margining fields are hardware-timing sensitive. Treating diagnostic or training fields as generic runtime knobs can destabilize PCIe links.
- The chunk has partial boundaries at both ends: EPF0 UVD1 scheduler `DW0` is incomplete at the start, and EPF1 GPUIOV VCE scheduler `DW7` and later fields continue after the end. The merge lane must stitch adjacent chunks before making final file-level completeness claims.

## Test and Validation Signals

Useful validation is primarily compile and hardware integration coverage:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU/SR-IOV, and SMU/platform files, to catch missing or renamed macros.
- PCI enumeration should report stable vendor/device/class IDs, capability chains, BAR sizes, MSI/MSI-X capability state, PCIe link capabilities, and SR-IOV capability contents for NBIO 2.3 hardware.
- Link tests should validate negotiated speed/width, retraining, ASPM/power-management controls, 8 GT/s/16 GT/s equalization status, and lane margining diagnostics where supported.
- Error-handling tests should exercise PCIe/AER status and masks, FLR initiation/completion, GPUIOV need-FLR/self-recovery interrupts, and mailbox transmit/receive interrupt paths.
- SR-IOV tests should create and destroy VFs, verify VF enable/MSE/count/stride/device-ID fields, validate VF BAR and VF resizable BAR sizing, and check per-VF framebuffer size/offset partitioning.
- Virtualization and peer-to-peer tests should cover ACS/ATS/PASID/page-request/ARI/LTR behavior, multicast vectors if enabled, and `P2P_OVER_XGMI_ENABLE` policy.
- Suspend/resume and reset coverage should verify that persistent PCIe, MSI/MSI-X, SR-IOV, GPUIOV, and scheduler dword state is restored or reinitialized consistently.

## Unresolved Cross-Chunk References

The first line is only the mask for `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW0`; the register comment and shift are in the previous chunk. The final line is only the comment for `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VCESCH_DW7`; its shift/mask and later GPUIOV scheduler fields are in the next chunk.

### subset-b-002943: lines 96045-98522

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 96045-98522

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header segment. It contains C preprocessor constants only: no functions, structs, enums, variables, locks, allocations, or direct register accesses are defined here.

The line range starts in the tail of the `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` scheduler descriptor dwords, then covers a full `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` PCI configuration-space map, and then covers most of `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` through `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_18`.

The public interface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.

## Purpose

`nbio_2_3_sh_mask.h` is the bit-layout side of the NBIO 2.3 hardware ABI used by AMDGPU. The matching offset header supplies register addresses/config offsets, and this header supplies the bit positions and masks used by AMDGPU register helpers to compose writes and decode reads.

This chunk focuses on multifunction PCIe endpoint functions `EPF2` and `EPF3`, plus the trailing EPF1 GPU IOV scheduler data. The generated constants describe standard PCI configuration fields, PCIe capability structures, message-signaled interrupt programming, vendor-specific capability dwords, Advanced Error Reporting, resizable/enhanced BAR capabilities, power budgeting, dynamic power allocation, access-control/address-translation capabilities, PASID/ARI, and TPH requester steering tables.

These definitions matter because NBIO/BIF PCIe state is shared between GPU driver policy, Linux PCI core behavior, firmware defaults, hypervisor/SR-IOV handling, and hardware diagnostic paths. A symbolic mask lets code use the correct bitfield without open-coding raw PCIe bit positions at each call site.

## Important Macro Families

### EPF1 GPUIOV Scheduler Tail

The range begins after the comment for `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VCESCH_DW7`; the visible EPF1 portion includes:

- `VCESCH_DW8` for the final visible VCE scheduler descriptor dword.
- `GFXSCH_DW0` through `GFXSCH_DW8`.
- `UVD1SCH_DW0` through `UVD1SCH_DW8`.

Each of these exposes a single full-width field (`DWn`) with shift `0x0` and mask `0xFFFFFFFFL`. The values are opaque AMD vendor-specific GPUIOV scheduler descriptor dwords rather than standard PCIe fields. Their interpretation belongs to the GPUIOV/PF virtualization stack and related firmware/hypervisor contracts.

### EPF2 Base PCI Configuration

The `EPF2` block starts at `BIF_CFG_DEV0_EPF2_1_VENDOR_ID` and defines the normal PCI configuration header:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: IO and memory access enables, bus mastering, parity/SERR behavior, interrupt disable, readiness, capability-list presence, abort reporting, and parity error state.
- Header and BAR fields: cache-line size, latency timer, header type, BIST, `BASE_ADDR_1` through `BASE_ADDR_6`, CardBus CIS pointer, subsystem/vendor adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- Vendor and power-management capability fields: `VENDOR_CAP_LIST`, `ADAPTER_ID_W`, `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- USB-like support registers visible in this generated PCI config map: `SBRN`, `FLADJ`, and `DBESL_DBESLD`.

The command/status fields are especially sensitive because the masks target PCI config control and sticky/error status bits. The header only names the bits; ownership and write-clear behavior are determined by PCIe/NBIO hardware and the caller's access path.

### EPF2 PCIe, MSI, and Vendor Capabilities

The EPF2 PCIe capability block includes:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, version, device/port type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for max payload, phantom functions, extended tag support, endpoint L0s/L1 latency, role-based error reporting, captured slot power, function-level reset, error-reporting enables, relaxed ordering, max payload/read request, no-snoop, auxiliary power, transactions pending, and unsupported request state.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for supported/current link speed and width, ASPM, L0s/L1 exit latency, clock power management, hot-plug/surprise-down reporting, retrain/disable/common-clock controls, bandwidth management, link training, slot clock, data-link active, and autonomous bandwidth state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout ranges, timeout disable, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, TPH completer support, end-to-end TLP prefix controls, emergency power reduction, ten-bit tags, target link speed, compliance/de-emphasis controls, equalization, retimer presence, and link margining status.
- MSI and MSI-X programming fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, 64-bit layout aliases, pending-bit registers, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- SATA/IDP capability fields: `SATA_CAP_0`, `SATA_CAP_1`, `SATA_IDP_INDEX`, and `SATA_IDP_DATA`.
- Vendor-specific extended capability fields: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.

The MSI `_64` fields reflect alternate layout interpretation when 64-bit MSI address support is enabled. They should not be treated as independent storage separate from the underlying PCI capability layout.

### EPF2 Error, BAR, Power, and Translation Capabilities

The EPF2 extended capability area includes:

- Advanced Error Reporting: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four header-log dwords, and four TLP-prefix-log dwords.
- Enhanced BAR controls: `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP`, and `PCIE_BAR1_CNTL` through `PCIE_BAR6_CNTL`.
- Power budgeting: `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP`.
- Dynamic Power Allocation: `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7`.
- Access and routing features: `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, `PCIE_PASID_CNTL`, `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.
- TPH requester fields: `PCIE_TPH_REQR_ENH_CAP_LIST`, `PCIE_TPH_REQR_CAP`, `PCIE_TPH_REQR_CNTL`, and the full `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63`.

The TPH steering-table entries each expose lower and upper 8-bit entries inside a 16-bit mask pair. This is a repeated mechanical family where index drift is easy to miss in review.

### EPF3 PCIe Map Through TPH Table 18

The `EPF3` block repeats the same generated layout as EPF2 from `VENDOR_ID` through `PCIE_TPH_ST_TABLE_18`:

- Complete base PCI header, PM, PCIe device/link, MSI/MSI-X, SATA/IDP, vendor-specific, AER, enhanced BAR, power-budget, DPA, ACS, PASID, ARI, and TPH requester capability fields are present through the visible range.
- The chunk ends at `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_18__TPH_ST_UPPER_ENTRY_MASK`; `PCIE_TPH_ST_TABLE_19` through `_63` continue in the next chunk.

EPF2 and EPF3 are intentionally distinct macro namespaces. A caller can compile successfully while using an EPF2 mask with an EPF3 offset or vice versa, so code review must verify both the register address and the field macro prefix.

## Important APIs, Types, and Functions

There are no C functions or types in this chunk. The important "API" is the preprocessor symbol surface consumed by AMDGPU register-access code.

Typical consumers combine these masks with:

- Matching NBIO 2.3 offset symbols from `nbio_2_3_offset.h`.
- Matching reset/default symbols from `nbio_2_3_default.h`.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`.

The macro values are mostly 8-bit, 16-bit, or 32-bit PCI/PCIe fields represented as C integer constants with an `L` suffix. The generated names imply register width and field semantics, but the header does not enforce access size, read-only/write-only status, write-one-to-clear behavior, or PF/VF permissions.

## Control Flow

This header has no runtime control flow. Runtime behavior occurs in callers:

1. AMDGPU, PCIe, firmware-facing, or virtualization code includes the NBIO 2.3 offset/default/mask headers.
2. The caller selects an EPF1, EPF2, or EPF3 register offset and the corresponding field mask/shift from this header.
3. Helper macros shift and mask values when composing a register write or decoding a register read.
4. PCIe/NBIO hardware, firmware-owned state, or hypervisor-mediated config space observes the resulting read/write.

Because this is PCI configuration-space metadata, the actual access path may be PCI config access, NBIO index/data registers, SMN access, or PF-mediated virtualization control. The header does not decide which path is legal for a given field.

## State and Persistence Behavior

The macros are compile-time constants and hold no software state. They describe hardware-visible PCIe/NBIO state.

State represented by this chunk includes:

- EPF1 GPUIOV scheduler descriptor dwords for VCE, GFX, and UVD1 scheduling/resource descriptors.
- EPF2 and EPF3 identity, class, BAR, ROM, subsystem, interrupt, and capability-chain presentation.
- PCI command/status and PM state, including memory/bus-master enables, interrupt disable, power state, PME controls, and status/error latches.
- PCIe device and link capability/control/status state, including payload size, read request size, relaxed ordering, no-snoop, FLR, completion timeout, LTR, OBFF, target/current link speed, negotiated width, retrain/disable, equalization, retimer, and bandwidth status.
- MSI/MSI-X programming state for EPF2 and EPF3, including message address/data, vector count/enablement, mask/pending bits, MSI-X table location, and PBA location.
- AER diagnostic state: uncorrectable/correctable status, masks, severity, capability/control bits, header logs, and TLP prefix logs.
- Enhanced BAR and power-management state: BAR size/enable controls, power budget data selection and values, DPA capability/status/control, and DPA substate power allocations.
- Interconnect and isolation controls: ACS, PASID, ARI, and TPH requester enablement/steering-table entries.

Persistence is hardware-defined. These fields can be reset or reinitialized by GPU reset, PCI function reset, FLR, secondary bus reset, suspend/resume, power-state transitions, firmware actions, hypervisor operations, or explicit driver writes. Status and log fields may be transient or write-one-to-clear, while capability fields are usually hardware/firmware-defined and read-only or read-mostly.

## Dependencies and Integration Points

Direct dependencies:

- `nbio_2_3_offset.h` supplies the register/config-space offsets that must be paired with these masks.
- `nbio_2_3_default.h` supplies reset/default values for the same NBIO 2.3 register families.
- AMDGPU register helpers provide the C-side read/modify/write and field extraction mechanics.
- Linux PCI/PCIe semantics define the standard capability behavior mirrored by many of these masks: PM, MSI/MSI-X, AER, ACS, PASID, ARI, TPH, BAR sizing, DPA, link control/status, and device control/status.
- AMD GPUIOV/SR-IOV firmware or hypervisor interfaces define the opaque vendor-specific scheduler dwords and function ownership rules.

Observed source-tree integration:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes `nbio/nbio_2_3_sh_mask.h` with the matching generated headers for NBIO 2.3 register programming.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header in virtualization-oriented AMDGPU code.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c` include the same NBIO generated header family for PCIe/NBIO-related SMU platform behavior.

Integration is name-based and compile-time. The generated masks do not identify whether Linux PCI core, AMDGPU, firmware, or a hypervisor owns a field at runtime. Callers must respect subsystem ownership when touching shared PCI config fields such as MSI/MSI-X, AER, ACS/PASID/ARI, link controls, power controls, and BAR controls.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can silently alter adjacent PCIe config bits, misreport a capability, break endpoint enumeration, corrupt MSI/MSI-X setup, or hide PCIe errors.
- EPF namespace drift is easy to introduce. EPF2 and EPF3 have near-identical generated families, so an EPF2 field macro paired with an EPF3 register address can compile while targeting the wrong function layout.
- GPUIOV scheduler dwords are opaque full-width fields. Treating them as generic scratch registers can corrupt virtualization resource/scheduler state owned by firmware, PF management code, or a hypervisor.
- PCI command/status, PM, link control, FLR, AER, MSI/MSI-X, and TPH fields may have side effects. Generic read/modify/write code can clear sticky diagnostics, retrain links, reset a function, disable interrupt delivery, or change DMA permissions.
- MSI and MSI-X state overlaps Linux PCI core ownership. Direct AMDGPU writes must not race PCI core vector allocation, masking, table programming, or teardown.
- AER fields are diagnostic and often write-one-to-clear. Incorrect masks or careless writes can erase first-error evidence or suppress critical/nonfatal/fatal reporting.
- ACS, PASID, ARI, and TPH affect isolation, address tagging, routing, and host interconnect behavior. Enabling unsupported or policy-disallowed combinations can create protocol errors or weaken virtualization isolation.
- Power-budget and DPA controls affect platform power/latency behavior. Incorrect power data or substate allocation can cause performance regressions, latency spikes, or power-policy mismatches.
- The chunk boundaries are partial. The EPF1 scheduler family starts before this range, and the EPF3 TPH steering table continues after this range; file-level conclusions need neighboring chunks.

## Test and Validation Signals

Useful signals for changes touching this chunk or code that consumes it:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially `nbio_v2_3.c`, `mxgpu_nv.c`, and the SMU11 platform files.
- Static generated-header checks should compare `nbio_2_3_sh_mask.h`, `nbio_2_3_offset.h`, and `nbio_2_3_default.h` for matching EPF2/EPF3 register families, mask widths, and repeated table indexes.
- PCIe enumeration should continue to show sane EPF2/EPF3 identity, class, BAR, PM, PCIe, MSI/MSI-X, AER, ACS/PASID/ARI, TPH, power-budget, DPA, and vendor-specific capability structures where exposed.
- Runtime PCIe tests should validate link speed/width reporting, retraining behavior, ASPM/LTR/OBFF policy, payload/read-request sizes, completion timeout settings, and link status/equalization bits.
- MSI/MSI-X tests should validate vector enablement, message address/data programming, mask/pending behavior, MSI-X table/PBA interpretation, interrupt delivery, and teardown.
- AER error-injection or hardware error diagnostics should verify uncorrectable/correctable status, mask, severity, header log, TLP prefix log, and clear semantics.
- SR-IOV/GPUIOV validation should cover PF-managed resource partitioning, scheduler descriptor programming, VF lifecycle, guest load/unload, function reset, and hypervisor mailbox/resource ownership.
- Power-management validation should cover suspend/resume, runtime power transitions, D3/D0 transitions, DPA substate behavior, and power-budget reporting.
- TPH validation should ensure steering-table indexes decode coherently for EPF2 table entries 0-63 and EPF3 entries 0-18 in this chunk, with EPF3 entries 19-63 reconciled against the next chunk.

## Cross-Chunk Notes

- The range begins in the middle of the EPF1 GPUIOV scheduler descriptor area; earlier EPF1 `VCESCH_DW0` through part of `VCESCH_DW7` are outside this chunk.
- The EPF2 address block appears complete in this chunk, including all visible TPH steering-table entries 0-63.
- The EPF3 address block is incomplete at the end of the range. `PCIE_TPH_ST_TABLE_19` through `PCIE_TPH_ST_TABLE_63` continue after line 98522.
- The final per-file research merge should reconcile this chunk with neighboring generated-header chunks before making complete claims about EPF1 GPUIOV scheduler coverage or EPF3 TPH requester coverage.

### subset-b-002944: lines 98523-100975

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 98523-100975

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts in the tail of `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_*`, covering steering table entries 19 through 63. It then enters three complete SR-IOV virtual-function PCI configuration address blocks for `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, `vf1`, and `vf2`, and finally starts the `vf3` block. The VF0, VF1, and VF2 blocks run from standard PCI identity/header fields through PCIe, MSI/MSI-X, AER, ATS, and ARI capability masks. The VF3 block is partial and ends at `BIF_CFG_DEV0_EPF0_VF3_1_PCIE_CAP__VERSION__SHIFT`.

Although the repository path is under a local `ceph-client` mirror, this file is AMD GPU PCIe/NBIO hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCIe configuration-space registers. Each hardware field is represented by generated macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for encoding or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the mask for isolating, preserving, clearing, or updating the field.

Runtime AMDGPU code combines these definitions with the matching NBIO 2.3 offset header and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. This header does not decide access order, read/write permissions, reset behavior, or side-effect semantics; it only names the field positions.

## Important Macro Families

The opening `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_19` through `_63` entries define TPH steering-tag table fields for endpoint function 3 instance 1. Every table register has `TPH_ST_LOWER_ENTRY` at bits 7:0 and `TPH_ST_UPPER_ENTRY` at bits 15:8. These are mechanically regular, but table index and lower/upper half selection are part of the hardware ABI for TPH requester steering.

The `BIF_CFG_DEV0_EPF0_VF0_1_*`, `VF1_1_*`, and `VF2_1_*` blocks each describe a virtual function's PCI-compatible configuration image. Standard header definitions include vendor/device IDs, command and status bits, revision/class code bytes, cache line, latency, header type/device type, BIST controls, BAR1-BAR6, CardBus CIS pointer, subsystem vendor/device IDs, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.

The command/status fields expose common PCI controls and observations: IO and memory access enables, bus master enable, special cycle, memory-write-invalidate, PAL snoop, parity response, SERR, fast back-to-back, interrupt disable, capability-list presence, interrupt status, parity and system-error status, target/master abort status, and DEVSEL timing. These fields are part of how a VF presents itself to host PCI enumeration and guest drivers.

The PCIe capability blocks define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. They cover max payload and max read request size, FLR capability/initiation, relaxed ordering, no-snoop, extended tags, phantom functions, completion timeout controls, ARI forwarding, atomic operation support, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, link speed/width capability and negotiation, ASPM/clock power management, link disable/retrain, common clock, bandwidth-management interrupts, DRS signaling, equalization status, crosslink reporting, and downstream-component presence.

The interrupt capability blocks cover MSI and MSI-X. MSI definitions include capability list IDs and next pointers, MSI enable, multi-message capability/enable, 64-bit support, per-vector masking support, message address/data fields, mask fields, and pending fields for both 32-bit and 64-bit layouts. MSI-X definitions include table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

The vendor-specific and AER families include `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, vendor payload dwords, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable error status and mask fields, uncorrectable severity fields, advanced error capability/control fields, header log dwords, and TLP prefix log dwords. These macros support PCIe RAS/error-reporting paths and diagnostic capture.

The ATS and ARI extended capabilities appear at the end of each complete VF block. ATS fields define enhanced capability list metadata, invalidate queue depth, page-aligned request support, global invalidate support, smallest translation unit (`STU`), and address translation cache enable (`ATC_ENABLE`). ARI fields define enhanced capability list metadata, MFVC/ACS function group capabilities, next-function number, enable bits, and function group selection.

The final `BIF_CFG_DEV0_EPF0_VF3_1_*` subsection only covers the beginning of VF3's config image: vendor/device ID, command/status, revision/class bytes, cache/latency/header/BIST, BAR1-BAR6, CIS pointer, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, `PCIE_CAP_LIST`, and the first shift macro for `PCIE_CAP`. Adjacent chunk `subset-b-002945` is needed for the rest of VF3.

## Control Flow

There is no runtime control flow in this chunk. The effective runtime pattern is supplied by AMDGPU NBIO, PCIe, interrupt, reset, and virtualization code:

1. Select the matching register offset from `nbio_2_3_offset.h` or another ASIC register table.
2. Read or construct the PCI config/MMIO value using AMDGPU register access helpers.
3. Use the `__SHIFT` and `_MASK` constants directly, or through helper macros, to extract or update a field.
4. Write the updated value, poll a status field, clear a sticky status, or pass decoded data to higher-level PCIe/SR-IOV logic.

The repeated VF0/VF1/VF2 blocks imply table-like hardware layout for virtual functions, but the header does not implement iteration. Any loop over VFs, capabilities, BARs, or interrupt vectors lives in consuming driver code that chooses the corresponding register offset and macro names.

## State And Persistence Behavior

This header stores no software state and persists nothing to disk. It describes state owned by the GPU, firmware, PCIe fabric, host kernel, and possibly guest drivers when SR-IOV is active.

Some represented fields are configuration that can remain in hardware until reset, FLR, suspend/resume, power transition, guest reconfiguration, or explicit driver reprogramming: PCI command enables, BAR values, ROM BAR, MSI/MSI-X message address/data and masks, max payload/read request settings, completion timeout controls, ATS `ATC_ENABLE`, ARI controls, link control bits, AER masks/severity, and interrupt masking.

Other represented fields are static capabilities, hardware-updated observations, command strobes, sticky status, or diagnostic logs: vendor/device/class identity, PCIe capability values, link status, device status, AER status, header/TLP prefix logs, MSI pending bits, FLR initiation, ATS invalidate capability, and ARI next-function information. The generated names do not distinguish safe read-modify-write fields from write-one-to-clear or side-effectful fields.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with sibling generated headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`, especially `nbio_2_3_offset.h`, which supplies the register addresses for the field layouts documented here.

Primary integration points are AMDGPU NBIO and PCIe code paths that expose, program, or diagnose PF/VF PCI configuration space. The VF blocks are relevant to SR-IOV and virtualized GPU operation because they describe what each virtual function presents for PCI identity, BARs, interrupts, PCIe capability negotiation, AER reporting, ATS address translation, and ARI routing/function grouping.

Interrupt integration depends on the MSI/MSI-X definitions. Reset and recovery integration depends on PCI command/status, FLR, AER, and link status/control fields. Memory/resource management integration depends on BAR and ROM BAR masks. IOMMU and virtualization integration depends on ATS, ARI, command bus-mastering, memory access enables, and error/isolation fields.

The macros are untyped integer constants. A missing or renamed macro usually fails at compile time, but an incorrect shift or mask can compile cleanly while making the driver read, clear, or program the wrong hardware bit.

## Risks And Edge Cases

- Chunk boundaries are partial. The opening lines continue an EPF3 TPH table sequence from the previous chunk, and the ending line stops inside VF3's `PCIE_CAP` register. Adjacent chunks are required before making complete-register claims for those areas.
- The VF0, VF1, and VF2 blocks are highly repetitive. Copy/paste or generation drift can cause one VF to expose different masks than another, which may only appear under SR-IOV or guest assignment testing.
- PCIe status and error fields can be sticky or write-one-to-clear. Treating AER status, device status, MSI pending, or link status as ordinary configuration can hide faults or erase useful logs.
- MSI/MSI-X fields are interrupt-delivery critical. Wrong enable, function-mask, table/PBA offset, message address/data, vector mask, or pending-bit masks can cause lost, misrouted, or unexpectedly unmasked interrupts.
- BAR fields are full-width and not self-validating in this header. Pairing the right full-width mask with the wrong VF or offset can expose the wrong aperture or corrupt virtual-function resource assignment.
- Link and PCIe capability controls affect enumeration and interoperability. Incorrect max payload/read request, completion timeout, relaxed ordering, no-snoop, FLR, ASPM, retrain, or target-speed masks can cause device resets, DMA ordering issues, or link instability.
- ATS and ARI fields are virtualization-sensitive. Wrong `ATC_ENABLE`, `STU`, function-group, next-function, or forwarding masks can break IOMMU translation behavior, VF routing, or guest isolation.
- TPH steering tables are dense and indexed. Off-by-one table selection or lower/upper entry confusion can silently steer traffic using the wrong tag.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, ARI, and reset support enabled; macro name drift should surface as compile failures.
- Run generated-header consistency checks against the authoritative NBIO 2.3 register source and matching offset header, including shift/mask width, overlap, and per-VF consistency checks.
- Boot hardware using these headers and confirm PCI enumeration for the relevant PF/VF surfaces shows expected vendor/device IDs, class codes, BARs, capability-list traversal, PCIe capability data, and interrupt capability layout.
- Exercise SR-IOV VF creation, assignment, reset, and teardown for VF0 through VF3, checking that each virtual function presents consistent config-space fields.
- Test MSI and MSI-X delivery under physical and virtualized workloads, including vector masking, pending bits, function mask behavior, and table/PBA placement.
- Run PCIe reset and recovery paths covering FLR initiation, command/status changes, link retraining/status, completion timeout behavior, and suspend/resume.
- Use AER/error-injection or fault-observation tests to validate uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, and recovery handling.
- Validate ATS/ARI behavior in IOMMU and virtualization configurations, including address-translation enablement, STU settings, ARI function routing, and guest isolation.

## Chunk-Specific Notes For Merge

Merge this chunk with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final per-file research document. Preserve that this slice covers TPH steering table entries 19-63 for `BIF_CFG_DEV0_EPF3_1`, complete `BIF_CFG_DEV0_EPF0_VF0_1`, `VF1_1`, and `VF2_1` PCIe config-space field masks, and only the beginning of `BIF_CFG_DEV0_EPF0_VF3_1` through the first `PCIE_CAP` shift.

### subset-b-002945: lines 100976-103396

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 100976-103396

## Scope

This chunk covers generated NBIO 2.3 shift and mask macros for PCI configuration-space registers exposed through AMDGPU's NBIF/BIF virtual-function decode blocks. The range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF3_1_PCIE_CAP` family and ends after `BIF_CFG_DEV0_EPF0_VF6_1_PCIE_VENDOR_SPECIFIC2`, immediately before the `VF6_1_PCIE_ADV_ERR_RPT_ENH_CAP_LIST` definitions in the next chunk.

Covered address blocks and register groups include:

- The tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf3_bifcfgdecp`, from PCIe capability/device/link controls through MSI, MSI-X, vendor-specific, AER, ATS, and ARI masks.
- Complete `nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp` mask coverage, including conventional PCI header fields, PCIe capabilities, MSI/MSI-X, vendor-specific capability, advanced error reporting, ATS, and ARI.
- The first part of `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`, from conventional PCI header fields through PCIe capability, MSI/MSI-X, and vendor-specific scratch registers. VF6 AER and later enhanced capabilities are outside this chunk.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only; it contains no C functions, structs, variables, runtime storage, or executable control flow.

## Purpose

The purpose of this section is to provide the bit-level ABI between AMDGPU NBIO/NBIF code and hardware PCI configuration-space registers for SR-IOV virtual functions. Every field is represented by the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating or composing that field.

The sibling NBIO offset header supplies register addresses, while this header supplies field layout. Driver code can then use common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and NBIO-specific indirect accessors without hard-coding bit positions for each virtual function.

## Important Macro Families

### Virtual Function Naming

The dominant prefix is `BIF_CFG_DEV0_EPF0_VF<N>_1`, where `VF<N>` is the virtual function number in the BIF configuration decode space. The chunk contains the end of VF3, complete VF4 and VF5, and the beginning of VF6. Most register definitions are mechanically repeated per VF with identical masks, so their semantic differences come from the addressed VF instance rather than from different bit layouts.

The address-block comments mark the generated source grouping:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`

VF3's address-block comment appears before this range, but the chunk still covers VF3 definitions through ARI control.

### Conventional PCI Header Fields

For VF4, VF5, and VF6 the chunk defines masks for the standard PCI header region:

- Identity and revision fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command and status bits: `COMMAND` fields such as I/O access, memory access, bus mastering, SERR, parity response, fast back-to-back, and interrupt disable; `STATUS` fields such as interrupt status, capability-list presence, DEVSEL timing, target/master aborts, system error, parity error, and immediate readiness.
- Header metadata: `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- BAR and ROM windows: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, and `ROM_BASE_ADDR`.
- Interrupt and legacy timing fields: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.

These definitions mirror PCI configuration-space semantics, but they are exposed as ASIC register fields for the virtualized NBIF decode path.

### PCI Express Capability and Link Control

For VF3 through VF6 this chunk defines PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` expose capability ID, next pointer, PCIe capability version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` encode maximum payload support/size, phantom functions, extended tags, acceptable L0s/L1 latency, role-based error reporting, slot power information, function-level reset capability/initiation, error-reporting enables, no-snoop, read-request size, and pending/error status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` encode supported/current link speed, link width, ASPM and power-management controls, retraining, common clock, link disable, bandwidth interrupt enables/status, data-link active, and training state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` include completion-timeout support/control, ARI forwarding, atomic operation support/control, ID-based ordering, LTR, OBFF, 10-bit tags, TLP prefix handling, emergency power reduction, and FRS support.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` include supported link speed vectors, compliance-mode controls, de-emphasis and transmit margin fields, equalization phase status, crosslink state, RTM presence, downstream component presence, and DRS message state.

These masks are integration points for PCIe link management, error handling, and virtualization policy code. They do not encode the ordering requirements for link retrain, FLR, or capability enablement; users must follow PCIe and AMDGPU sequencing rules around the register writes.

### MSI and MSI-X Configuration

Each covered VF includes MSI and MSI-X capability field masks:

- `MSI_CAP_LIST` and `MSI_MSG_CNTL` encode MSI capability ID, next pointer, MSI enable, multi-message capability/enable, 64-bit capability, and per-vector masking capability.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MSG_DATA_64`, `MSI_MASK`, `MSI_MASK_64`, `MSI_PENDING`, and `MSI_PENDING_64` provide the fields used for MSI target address, data, mask, and pending state.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` encode MSI-X enable/function mask, table size, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

These fields define interrupt-delivery configuration state for each VF. Misprogramming the address/data, mask, or MSI-X table/PBA fields can cause lost interrupts, unexpected interrupt routing, or VF isolation problems.

### Vendor-Specific Capability

For VF3 through VF6, the chunk defines `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.

The enhanced capability list and header fields provide `CAP_ID`, `CAP_VER`, `NEXT_PTR`, `VSEC_ID`, `VSEC_REV`, and `VSEC_LENGTH`. `PCIE_VENDOR_SPECIFIC1` and `PCIE_VENDOR_SPECIFIC2` expose full-width `SCRATCH` fields. These scratch registers are vendor-defined state rather than standard PCIe fields; their meaning is established by AMD hardware/firmware conventions and the code that consumes them.

### Advanced Error Reporting, ATS, and ARI

The chunk fully covers VF3, VF4, and VF5 AER/ATS/ARI masks, while VF6 AER begins in the next chunk.

AER definitions include:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` for AER enhanced capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic operation egress blocked, and TLP prefix blocked errors.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL` for first error pointer, ECRC generation/checking capability and enables, multi-header recording, and TLP prefix log presence.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` full-width capture fields.

ATS and ARI definitions include:

- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL`, covering capability-list metadata, invalidate queue depth, page-aligned requests, global invalidate support, ATC enable, and smallest translation unit.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, covering capability-list metadata, next function number, MFVC/ACS function group capability, function-group selection, and group enables.

These fields tie NBIO register layout to PCIe error reporting and virtualization features used by IOMMU and SR-IOV flows.

## Control Flow and State Behavior

This header has no runtime control flow. Its only effect is at compile time: C code includes the macros and uses them to construct or decode register values. The underlying state is hardware state in NBIO/NBIF PCI configuration-space windows.

Important state described by the chunk includes:

- Per-VF PCI identity, class, command, status, BAR, ROM, capability pointer, and interrupt-line/pin state.
- PCIe capability, device control/status, link control/status, and secondary capability state.
- MSI/MSI-X interrupt address, data, enable, mask, pending, table, and PBA state.
- AER status/mask/severity, header logs, TLP prefix logs, and ECRC controls for VF3 through VF5.
- ATS and ARI capability/control state for VF3 through VF5.
- Vendor-specific capability metadata and scratch fields.

Some fields are durable configuration bits, some are status bits, and some are action-oriented control bits. Examples include `INITIATE_FLR`, `RETRAIN_LINK`, MSI/MSI-X enable bits, error status bits, error masks, and ATC/ARI enables. The mask header does not describe whether a status bit is write-one-to-clear, sticky, read-only, or write-protected for a VF; that behavior comes from PCIe rules, AMD hardware documentation, and the owning driver paths.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header ecosystem:

- The matching `nbio_2_3_offset.h` file supplies register addresses for these names.
- The matching `nbio_2_3_default.h` file supplies reset/default values where generated.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` constants.
- PCI core and AMDGPU SR-IOV/NBIO code determine when the PF, VF, or hypervisor side may read or write each configuration field.

Integration points include:

- NBIO initialization and virtualization code that enumerates or programs per-VF BIF configuration-space state.
- SR-IOV enablement, reset, and VF management paths that need per-VF command/status, BAR, MSI/MSI-X, FLR, ARI, and AER layouts.
- PCIe link and error-handling code that interprets link status, device status, correctable/uncorrectable error status, masks, severities, and header logs.
- IOMMU/ATS related paths that coordinate `ATC_ENABLE`, invalidate capabilities, and STU programming with address translation policy.
- Interrupt setup paths that pair MSI/MSI-X address/data/table/PBA register layouts with Linux IRQ allocation and AMDGPU interrupt routing.

Because the same masks are repeated across VF instances, any generator or hand-editing error in one repeated block can silently affect only a subset of virtual functions. Cross-checking against the offset/default headers and hardware generation source is important when changing these definitions.

## Risks

- **Bitfield drift:** These constants are hardware ABI. A wrong shift or mask can make otherwise-correct driver code read or write the wrong PCIe field.
- **Partial chunk boundaries:** The range starts after the first VF3 PCIe capability fields and ends before VF6 AER. A final file-level report must merge neighboring chunks before drawing conclusions about complete VF3 or VF6 coverage.
- **Repeated-block assumptions:** VF4 and VF5 are complete in this chunk and appear mechanically identical in layout; consumers should not assume all VFs have identical runtime permissions or reset values merely because the mask layout is repeated.
- **Virtualization isolation:** MSI/MSI-X, BAR, command/status, AER, ATS, ARI, and vendor-specific scratch fields are per-VF state. Incorrect writes can leak PF/VF configuration, route interrupts incorrectly, expose memory windows, or break VF reset/error recovery.
- **PCIe sequencing:** Fields such as FLR initiation, link retrain, ARI forwarding, ATS ATC enable, MSI/MSI-X enable, and AER status clearing have ordering and polling requirements outside this header.
- **Generated-file maintenance:** Manual edits are risky. Regeneration from authoritative register descriptions is safer than patching individual masks.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- AMDGPU builds that include `nbio_2_3_sh_mask.h` without macro-name collisions or missing paired `__SHIFT`/`_MASK` definitions.
- Static comparison against the matching generated offset/default headers and AMD register database for NBIO 2.3 VF3/VF4/VF5/VF6 BIF config decode blocks.
- SR-IOV smoke tests with multiple VFs enabled, checking PCI enumeration, class/vendor/device IDs, BAR sizing, command/status behavior, FLR, and VF reset recovery.
- MSI and MSI-X tests on VFs, including interrupt enable/disable, masking, pending state, table/PBA placement, and interrupt delivery under load.
- PCIe AER injection or fault-observation tests for VF3 through VF5, verifying status, mask, severity, header log, and TLP prefix log interpretation.
- ATS/ARI validation in an IOMMU-enabled environment where supported, checking that capability bits and control fields match the advertised VF behavior.
- Link-management diagnostics that compare decoded link capability/control/status fields against `lspci -vv` and platform expectations.

### subset-b-002946: lines 103397-105826

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 103397-105826

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header segment. It contains 2,138 preprocessor field definitions across 2,430 source lines. There are no C functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The line range starts in the late extended-capability area of `BIF_CFG_DEV0_EPF0_VF6_1_*`, covers complete virtual-function PCI configuration bitfield maps for `VF7`, `VF8`, and `VF9`, and then begins the `VF10` address block through the `ROM_BASE_ADDR` field before the `CAP_PTR` fields continue in the next chunk. The source boundary is artificial: VF6 standard PCI/PCIe/MSI/VSEC fields are before this chunk, and most of VF10 is after it.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield half of the generated NBIO 2.3 hardware interface. For each named NBIO/PCI configuration register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve the field.

The matching register addresses live in `nbio_2_3_offset.h`, and reset/default values live in `nbio_2_3_default.h`. Runtime AMDGPU code includes these generated headers and applies the masks through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, PCIe/NBIO config accessors, and lower-level MMIO paths.

This chunk specifically documents SR-IOV virtual-function PCI configuration-space layout for endpoint function 0. The repeated `BIF_CFG_DEV0_EPF0_VF<n>_1_*` names describe how each VF presents PCI identity, BAR/resource, PCIe capability, interrupt, Advanced Error Reporting, Address Translation Service, and Alternative Routing-ID Interpretation fields.

## Important Macro Families

The VF6 tail contains the Advanced Error Reporting, ATS, and ARI portion of a VF config image:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` exposes the AER extended-capability ID, version, and next-pointer fields.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` define uncorrectable PCIe error classes: data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP prefix blocked.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover correctable receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow events.
- `PCIE_ADV_ERR_CAP_CNTL` covers first-error pointer, ECRC generation/check capability and enable bits, multi-header received capability/enablement, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG[0-3]` and `PCIE_TLP_PREFIX_LOG[0-3]` define four 32-bit diagnostic capture words for failed TLP headers and prefixes.
- `PCIE_ATS_*` covers ATS enhanced-capability metadata, invalidate queue depth, page-aligned request support, global invalidate support, small translation unit, and ATC enable.
- `PCIE_ARI_*` covers ARI enhanced-capability metadata, MFVC/ACS function-group capability bits, next-function number, enables, and function-group selection.

The complete `VF7`, `VF8`, and `VF9` blocks repeat the full virtual-function PCI configuration template:

- Conventional PCI header fields: vendor/device ID, command, status, revision, class bytes, cache-line size, latency, header type, BIST, BAR1 through BAR6, CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI command/status fields: I/O access, memory access, bus mastering, special cycle, memory write invalidate, parity response, SERR, interrupt disable, readiness, capability-list presence, DEVSEL timing, target/master abort, system error, and parity error status.
- PCIe capability fields: capability-list header, PCIe version and device type, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Device and link controls: error-report enables, relaxed ordering, max payload size, extended tags, no-snoop, max read request size, FLR initiation, completion timeout, ARI forwarding, atomic operation controls, ID-based ordering, LTR enable, emergency power reduction, ten-bit tag requester enable, OBFF, end-to-end TLP prefix blocking, link disable/retrain, common clock, ASPM/PM control, bandwidth interrupts, DRS signaling, target link speed, compliance controls, de-emphasis, and equalization status.
- MSI/MSI-X fields: capability IDs and next pointers, MSI enable and multiple-message fields, 32-bit and 64-bit message address/data fields, mask and pending fields, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability fields: VSEC capability-list metadata, VSEC ID/revision/length, and two 32-bit scratch payload registers.
- AER, ATS, and ARI fields with the same semantics as the VF6 tail.

The VF10 start covers only the conventional PCI header beginning: identity, command/status, revision/class/header/BIST fields, six BAR-sized base-address fields, CardBus CIS pointer, adapter/subsystem ID, and ROM base address. VF10 capability pointer and later capability sections are outside this chunk.

## APIs, Types, And Functions

There are no runtime APIs or C types here. The public interface is the macro namespace itself. Consumers depend on the generated spelling, bit positions, and masks staying synchronized with companion offset/default headers and the hardware register database.

The masks are untyped integer constants, commonly 8-, 16-, or 32-bit register fields with an `L` suffix. Because the macros do not encode access size or read/write semantics, the caller must already know whether a field belongs to PCI config space, MMIO, an extended capability, a read-only capability field, a read/write control field, a sticky status bit, or a command bit with side effects.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU, firmware-facing, SR-IOV, or PCIe code selects a register offset from `nbio_2_3_offset.h`.
2. The code reads or composes a register value using these `__SHIFT` and `_MASK` constants, directly or through field helper macros.
3. The value is written back, decoded, polled, or reported according to PCIe/NBIO hardware semantics.

Likely flows using these fields include VF config-space exposure, PCI command and BAR/resource programming, PCIe link/device negotiation, function-level reset, MSI/MSI-X interrupt setup, AER status collection and masking, ATS/IOMMU translation enablement, ARI routing, and SR-IOV virtualization validation.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration registers for SR-IOV virtual functions. Persistence is controlled by GPU/NBIO reset domains, PCI config save/restore, firmware initialization, hypervisor or PF management, VF FLR, suspend/resume, and explicit driver writes.

Represented state includes static PCI identity and capability data, host-programmed command bits, BAR and interrupt routing state, device/link control settings, hardware-updated link/device status, MSI/MSI-X message address/data/mask/pending state, AER sticky status/mask/severity and diagnostic logs, ATS translation cache controls, and ARI function-routing state.

Several fields are not ordinary storage bits. Status and AER fields may be sticky or write-one-to-clear, `INITIATE_FLR` starts a function-level reset, link retrain/disable controls affect PCIe link state, MSI/MSI-X enable/mask fields affect interrupt delivery, and ATS/ARI controls affect isolation and enumeration. This generated file only provides bit layout; side-effect ordering and privilege rules are enforced elsewhere.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 header set:

- `nbio_2_3_offset.h` supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` register/config-space addresses.
- `nbio_2_3_default.h` supplies generated defaults for related registers.
- AMDGPU register helper macros consume `__SHIFT` and `_MASK` definitions for field extraction and update.

Observed include-level integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c`, all of which include the NBIO 2.3 generated headers. The per-VF fields integrate with PCI enumeration/configuration, SR-IOV VF presentation, PF/VF or hypervisor-managed virtualization paths, interrupt delivery, AER reporting, IOMMU/ATS behavior, ARI routing, reset handling, and PCIe link management.

Although this source path is under a `ceph-client` mirror, the content is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while making software touch the wrong hardware bit. This is especially risky for command, DMA enable, interrupt, FLR, AER clear, ATS, and ARI fields.
- The range starts and ends inside repeated VF templates. Merge/reconciliation must combine adjacent chunks before making complete claims about VF6 or VF10.
- Repetition across VF7, VF8, and VF9 is intentional. Any per-VF mismatch may indicate generator or register-database drift, but chunk-boundary truncation must not be mistaken for such drift.
- PCI command bits control memory access, bus mastering, SERR, parity behavior, and interrupt disable. Wrong masks can break VF probing or weaken DMA/resource isolation.
- Link controls, completion timeout, payload/read-request sizing, relaxed ordering, no-snoop, ID-based ordering, and atomic operation controls affect PCIe liveness and memory-ordering behavior.
- MSI/MSI-X masks, table offsets, pending bits, and enable fields can cause lost, repeated, or misrouted interrupts if decoded or programmed incorrectly.
- AER logs can be diagnostic evidence; treating status/log fields as normal writable state can clear useful data or fail to clear real errors.
- ATS and ARI controls affect IOMMU translation caching and function routing. Incorrect masks can break invalidation, enumeration, or isolation.

## Test Signals

- Compile AMDGPU with NBIO 2.3/Navi support enabled. Missing or misspelled macros should be caught by users of the generated header set.
- Runtime probe on affected AMD GPUs should show stable PCI config enumeration for SR-IOV virtual functions, valid BAR sizing, and correct capability-chain traversal.
- SR-IOV validation should exercise multiple VFs, not just one, because this chunk has mechanically repeated `VF7`, `VF8`, and `VF9` families.
- Interrupt smoke tests should verify MSI/MSI-X delivery, masking, pending-bit behavior, and absence of spurious interrupts.
- PCIe health signals include expected negotiated link width/speed, successful FLR/retrain paths, no unexpected AER storms in logs, and preserved AER diagnostics when errors are injected.
- ATS/ARI/IOMMU tests should verify VF enumeration, translation enable/disable, invalidation behavior, and isolation under virtualization.

### subset-b-002947: lines 105827-108246

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 105827-108246

## Scope

This chunk is a slice of AMDGPU's generated NBIO 2.3 register-field shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, global variables, allocation, locking, direct MMIO, or runtime branches.

The assigned range covers `BIF_CFG_DEV0_EPF0_*_1` PCI configuration-space field layouts for SR-IOV-style endpoint virtual functions:

- the tail of `VF10_1`, starting at `CAP_PTR` field definitions and continuing through PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and ARI capability fields;
- complete `VF11_1` and `VF12_1` config blocks, from vendor/device ID through ARI control;
- the first part of `VF13_1`, from vendor/device ID through the beginning of `MSIX_PBA`.

The range starts in the middle of the `VF10_1` register block because the `//BIF_CFG_DEV0_EPF0_VF10_1_CAP_PTR` marker is in the previous chunk. It also ends in the middle of `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA`; this chunk contains its two shift definitions, while the corresponding masks continue in the next chunk.

Although the repository path is under a local `ceph-client` tree, this source file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

`nbio_2_3_sh_mask.h` is the bit-layout side of the generated NBIO 2.3 register description. The macros in this chunk give named shift and mask constants for PCI/PCIe configuration registers exposed by AMD NBIF/BIF endpoint virtual functions. Driver code, diagnostics, generated validation tools, and register access helpers can use these names instead of open-coded bit numbers.

The naming convention is consistent across the range:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's encoded bit mask.

This chunk is therefore a compile-time hardware ABI. Consumers combine these field definitions with matching addresses from `nbio_2_3_offset.h` and, where useful, reset values from `nbio_2_3_default.h`. The expected runtime usage pattern is through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and related NBIO/SOC15 accessors.

## Important Macro Families

The `VF10_1` portion starts with capability pointer and interrupt/min-grant/max-latency fields, then defines PCIe capability, device capability/control/status, link capability/control/status, PCIe capability 2 device/link fields, MSI, MSI-X, vendor-specific capability headers, AER, ATS, and ARI fields.

`VF11_1` and `VF12_1` each define a complete endpoint config-space layout:

- standard PCI header identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `HEADER`, and `BIST`;
- command/status control bits: I/O and memory enable, bus mastering, parity/SERR/error reporting, interrupt disable, capability-list presence, 66 MHz capability, fast back-to-back, target/master abort, system error, and parity error status;
- BAR and address-style fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, and `CAP_PTR`;
- legacy interrupt and timing fields: interrupt line/pin, min grant, max latency, cache line size, and latency timer;
- PCIe capability list, PCIe capability header, device capability/control/status, link capability/control/status, device/link capability 2, device/link control 2, and link status 2;
- MSI and MSI-X capability list, message control, message address/data, mask, pending, table, and pending-bit-array fields;
- PCIe vendor-specific extended capability headers and scratch registers;
- AER extended capability fields for uncorrectable/correctable error status, masks, severity, capability/control, header logs, and TLP prefix logs;
- ATS extended capability/list/control fields and ARI extended capability/list/control fields.

The `VF13_1` portion repeats the same endpoint-header and early capability pattern through `MSIX_PBA`, but its vendor-specific, AER, ATS, and ARI families are outside this chunk.

The PCIe device-control fields include error reporting enables (`CORR_ERR_EN`, `NON_FATAL_ERR_EN`, `FATAL_ERR_EN`, `USR_REPORT_EN`), ordering and snoop policy (`RELAXED_ORD_EN`, `NO_SNOOP_EN`), payload/read request sizing, extended tags, phantom functions, AUX power PM, and `INITIATE_FLR`. Device-status fields cover correctable/non-fatal/fatal/unsupported-request observations, AUX power, pending transactions, and emergency power-reduction detection.

The link fields describe negotiated and target link behavior: link speed, width, ASPM/power-management support, L0s/L1 latency, clock power management, surprise-down reporting, data-link active reporting, bandwidth notification, link disable/retrain, common clock, extended sync, autonomous width/speed disable, link bandwidth interrupts, DRS signaling, current speed/width, link training, slot clock, data-link active, equalization status, de-emphasis, crosslink/downstream presence, and related PCIe 2.0+ status/control bits.

The MSI and MSI-X families define interrupt capability wiring for each virtual function. MSI fields include enable, multi-message capability and enablement, 64-bit message support, per-vector masking support, low/high message address, message data, mask, pending, and 64-bit variants. MSI-X fields include table size, function mask, enable, table BAR indicator/offset, and PBA BAR indicator/offset.

The AER families in `VF10_1`, `VF11_1`, and `VF12_1` define uncorrectable error status/mask/severity bits for data-link protocol, surprise-down, poisoned TLP, flow-control protocol, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocking, TLP prefix blocking, and poisoned-TLP egress blocking. Correctable error status/mask fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal error, and header log overflow. AER control fields include first error pointer, ECRC generation/check capability and enable bits, multiple-header recording, TLP prefix log presence, and completion timeout prefix/header log controls.

The ATS and ARI fields define capability IDs, versions, next pointers, invalidation queue depth, page-aligned request support, STU, enable bits, next-function-number fields, function-group capability, and ACS function-group behavior. These are relevant to virtualized PCIe topology and address translation behavior.

No callable APIs or C types are declared here. The public surface is the set of generated macro names.

## Control Flow

There is no executable control flow in this header. At runtime, surrounding AMDGPU code follows the usual generated-register pattern:

1. Select a register offset from `nbio_2_3_offset.h` or a companion generated address macro.
2. Read the corresponding NBIO/BIF/PCIe config register through a SOC15, PCIe, or indirect register accessor.
3. Use `__SHIFT` and `_MASK` constants from this file, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to compose or decode a field.
4. Write the modified register value back, poll a status bit, route an interrupt, log decoded hardware state, or expose a capability result to higher-level driver code.

The chunk itself does not decide whether a field is readable, writable, write-one-to-clear, sticky, reset-only, or firmware-owned. Those semantics come from the AMD register specification and the runtime sequences that consume the generated constants.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-visible PCI/PCIe configuration state for NBIO 2.3 endpoint virtual functions. The underlying state is controlled by GPU reset, PCIe reset, function-level reset, SR-IOV/PF policy, firmware initialization, host PCI enumeration, power transitions, suspend/resume, link retraining, interrupt configuration, and error handling.

The represented state includes:

- identity and enumeration metadata such as vendor ID, device ID, class code, header type, subsystem ID, BARs, ROM BAR, and capability pointers;
- command/status policy such as memory-space enable, bus mastering, interrupt disable, SERR, parity, and abort/error status;
- PCIe capability state such as payload size, maximum read request size, no-snoop, relaxed ordering, extended tags, FLR, LTR, OBFF, completion timeout, emergency power reduction, 10-bit tags, atomic operations, and TLP prefix behavior;
- link capability, control, and status for negotiated width/speed, target speed, retraining, compliance, de-emphasis, equalization, DRS, and data-link presence;
- interrupt-routing state for MSI and MSI-X message control, addresses, data, masks, pending bits, tables, and PBAs;
- error-state and diagnostics for AER status, masks, severity, header logs, TLP prefix logs, and root-error-style control fields where present;
- virtualization/topology capability state for ATS and ARI.

Some fields are pure status, some are policy controls, and some trigger side effects. Examples of side-effect-sensitive fields include `INITIATE_FLR`, link retrain, status bits that may be write-one-to-clear, AER logs, MSI/MSI-X enable and mask controls, completion-timeout controls, and link compliance/speed controls. The macros provide only bit positions; they do not protect callers from using a field with the wrong access semantics.

## Dependencies And Integration Points

The direct dependency is the generated AMD NBIO 2.3 register database. This header must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` offsets;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies reset/default constants for the same register generation where generated;
- AMDGPU register helper macros and accessors, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`;
- PCI core, SR-IOV, AER, MSI/MSI-X, ATS, and ARI expectations, because these generated layouts describe standard PCIe capability structures as implemented by the AMD NBIO block.

The closest source-tree integration path for this generated header is AMDGPU NBIO code such as `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, plus virtualization and power-management paths that include NBIO register headers for PCIe, ASPM/LTR, doorbell, interrupt, SR-IOV, and link policy. Specific `VF10_1` through `VF13_1` symbols may be accessed indirectly or only by tooling, but their correctness is still part of the generated ABI for the NBIO 2.3 register map.

Because the macros are untyped numeric constants, a missing or renamed macro usually fails at compile time, while an incorrect shift or mask can compile cleanly and cause runtime corruption of adjacent PCI/PCIe fields.

## Risks And Edge Cases

- Chunk-boundary risk is explicit. The range starts without the `VF10_1_CAP_PTR` marker and ends before `VF13_1_MSIX_PBA` masks; adjacent chunks are required for full register-family context.
- Width mismatches are easy to miss. The chunk describes 8-bit, 16-bit, and 32-bit PCI config fields using C integer constants. Consumers must pair masks with the matching register offset and access width.
- VF copy/paste drift is high risk. `VF11_1` and `VF12_1` are nearly identical blocks, and `VF10_1`/`VF13_1` are adjacent partial blocks. A wrong VF number, register suffix, or bit mask can silently route a decode or write to the wrong virtual function.
- PCIe link controls can destabilize hardware. Incorrect shifts for target speed, retraining, common clock, ASPM, LTR, OBFF, DRS, equalization, de-emphasis, or autonomous speed/width disable can reduce bandwidth, break resume, or cause link loss.
- MSI/MSI-X fields affect interrupt delivery. Bad message-control, table, PBA, address, data, mask, or pending-bit masks can produce lost interrupts, interrupt storms, or vectors delivered to the wrong target.
- AER fields are side-effect sensitive. Treating status/log fields as ordinary read-modify-write state can clear diagnostic evidence, mask serious errors, or apply wrong severity policy.
- ATS and ARI fields affect virtualization and topology behavior. Wrong queue-depth, page-aligned request, enable, next-function, or function-group masks can break isolation assumptions or PCIe function traversal.
- BAR, ROM, and capability-list fields are structural. Incorrect masks can break enumeration, capability walking, resource sizing, or emulation of VF configuration space.
- Field names are generated and long. Manual references are prone to subtle spelling mistakes; using the wrong `VF*_1` macro may compile if another generated symbol exists with the same field layout.

## Test Signals

Useful validation is mostly build, generated-header consistency, and PCIe/SR-IOV hardware behavior:

- Build AMDGPU configurations that include NBIO 2.3, SR-IOV, PCIe ASPM/LTR, MSI/MSI-X, AER, ATS, and ARI support; missing or renamed macros should be caught by compile failures in consumers.
- Compare `nbio_2_3_sh_mask.h` against the authoritative AMD register database and against `nbio_2_3_offset.h` to ensure every `BIF_CFG_DEV0_EPF0_VF10_1` through `VF13_1` field maps to the intended register and width.
- Run PCI enumeration and capability traversal with SR-IOV enabled; malformed identity, class, BAR, ROM, capability pointer, PCIe capability, MSI/MSI-X, ATS, or ARI layouts should appear as `lspci`/kernel decode anomalies.
- Exercise VF reset and FLR paths. `INITIATE_FLR`, pending transaction status, command/status, MSI/MSI-X masking, and capability restoration are useful signals for bit layout correctness.
- Test MSI and MSI-X interrupt delivery for VFs, including enable/disable, function mask, per-vector masking, pending bits, and table/PBA decode.
- Test PCIe link behavior across speed/width negotiation, retraining, ASPM/LTR, completion-timeout settings, DRS, equalization, suspend/resume, and hot reset where the platform supports it.
- Use AER/error-injection or fault-observation paths when available to confirm uncorrectable/correctable status, mask, severity, header-log, and TLP-prefix-log fields decode correctly for the affected VF config spaces.
- In virtualization environments, validate ATS/ARI behavior, function enumeration, isolation, and VF config-space emulation, since these macros define the field-level contract exposed to guests or PF-managed VFs.

## Chunk-Specific Notes For Merge

When the final per-file report is reconciled, merge this chunk with adjacent `nbio_2_3_sh_mask.h` chunks. Do not present `VF10_1_CAP_PTR` or `VF13_1_MSIX_PBA` as fully covered by this range alone. This range is best summarized as the VF10 tail, full VF11/VF12, and VF13 early endpoint PCIe config-space shift/mask definitions for NBIO 2.3.

### subset-b-002948: lines 108247-110670

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 108247-110670

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header segment for SR-IOV virtual-function PCI configuration-space fields. It starts at the final mask definitions for `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA`, covers the rest of VF13, complete VF14, complete VF15, complete VF16, and ends at the `BIF_CFG_DEV0_EPF0_VF17_1_BASE_ADDR_1__BASE_ADDR__SHIFT` definition. The matching mask for `VF17_1_BASE_ADDR_1` is on the following line outside this chunk.

The file content in this range is C preprocessor data only. It defines no functions, structs, variables, storage, locking, allocation, branching, loops, or direct MMIO operations. Its public interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` for a field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the bit mask used to isolate or compose that field.

## Purpose

`nbio_2_3_sh_mask.h` supplies the bitfield side of the NBIO 2.3 hardware ABI. AMDGPU and related platform code include it with the companion `nbio_2_3_offset.h` address header and `nbio_2_3_default.h` reset/default header. Runtime code then uses register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `WREG32_FIELD15` to build or decode register values without hard-coding bit numbers.

This chunk's specific role is to describe PCI and PCIe configuration fields for NBIO SR-IOV virtual functions. The complete VF14, VF15, and VF16 maps expose standard PCI identity/header fields, BARs, interrupt fields, PCIe device/link capability and control fields, MSI/MSI-X state, vendor-specific extended capability fields, Advanced Error Reporting, header/TLP-prefix logs, ATS, and ARI. The VF13 and VF17 coverage is partial because the assigned line range cuts across repeated VF blocks.

## Important Macro Families

### VF13 Tail

The first two lines complete `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA` by defining `MSIX_PBA_BIR_MASK` and `MSIX_PBA_OFFSET_MASK`. The preceding `VF13_1_MSIX_PBA` comment and shift definitions are in the previous chunk.

The rest of VF13 in this range covers:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`, which describe a vendor-specific enhanced capability header and scratch/data fields.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, AER uncorrectable status/mask/severity, correctable status/mask, AER capability/control, and the four `PCIE_HDR_LOG*` registers.
- Four `PCIE_TLP_PREFIX_LOG*` registers for captured TLP prefix data.
- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL`, including invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, including MFVC/ACS function group capability and enable bits plus next-function/function-group fields.

### Complete VF14, VF15, and VF16 Maps

The chunk contains full repeated address blocks for:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf16_bifcfgdecp`

Each full VF block begins with `VENDOR_ID` and `DEVICE_ID`, then defines the standard PCI configuration header fields: command, status, revision/class fields, cache-line size, latency timer, header type, BIST, six base address registers, CardBus CIS pointer, subsystem/vendor adapter ID, ROM base address, capability pointer, interrupt line/pin, and min/max latency.

For `COMMAND`, the repeated fields include IO and memory access enables, bus-master enable, special-cycle and memory-write-invalidate enables, palette snoop, parity-error response, SERR enable, fast back-to-back enable, and interrupt disable. For `STATUS`, the maps include readiness, interrupt status, capability-list presence, 66 MHz and fast-back capability flags, data parity error, DEVSEL timing, target/master abort status, system error, and parity error detected.

The PCIe capability families include:

- `PCIE_CAP_LIST` and `PCIE_CAP` fields for capability ID, next pointer, PCIe capability version, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` fields for payload sizing, phantom functions, extended tags, endpoint L0s/L1 latency, attention/power indicators, role-based error reporting, captured slot power, FLR capability/control, correctable/nonfatal/fatal/unsupported-request reporting, relaxed ordering, max payload size, extended tag enable, phantom function enable, AUX power PM enable, no-snoop enable, max read request size, bridge configuration retry, and transaction pending/AUX power status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` fields for supported/current speed and width, ASPM/L0s/L1 behavior, clock power management, surprise-down reporting, data-link active reporting, port number, retraining, common clock, extended sync, hardware autonomous width disable, link bandwidth management/status, and autonomous bandwidth status/interrupt controls.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout ranges and controls, ARI and atomic-operation support, 32/64/128-bit CAS capability, no-RO-enabled PR-PR passing, LTR support/enable, TPH completion support, OBFF, emergency power reduction, ID-based ordering, ten-bit tags, end-to-end TLP prefix behavior, target link speed, compliance/deemphasis controls, equalization state, selected deemphasis, transmit margin, and downstream component presence/DRS bits.

The interrupt capability families include `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, `MSI_PENDING_64`, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`. These describe vector enable/count state, 64-bit MSI layout, per-vector masking capability, message address/data, mask and pending bitmaps, MSI-X table size, function mask, MSI-X enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

The diagnostics and extended capability families include vendor-specific headers, AER uncorrectable/correctable status and masks, AER severity, AER capability/control, four header-log dwords, four TLP-prefix log dwords, ATS capability/control, and ARI capability/control.

### VF17 Beginning

The final section begins `nbio_nbif0_bif_cfg_dev0_epf0_vf17_bifcfgdecp`. This chunk covers VF17 `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class/header fields, cache line, latency, `HEADER`, `BIST`, and only the `BASE_ADDR_1__BASE_ADDR__SHIFT` line. VF17's `BASE_ADDR_1` mask and the rest of the VF17 PCI/PCIe map continue in the next chunk.

## Control Flow

There is no executable control flow in this header. The practical flow is external and compile-time driven:

1. AMDGPU NBIO 2.3, virtualization, or platform power-management code includes the generated NBIO offset, shift/mask, and default headers.
2. The code selects a concrete VF register symbol, such as a `BIF_CFG_DEV0_EPF0_VF16_1_*` field and the matching `cfgBIF_CFG_DEV0_EPF0_VF16_1_*` offset.
3. Register helper macros combine masks and shifts to compose writes or extract read fields.
4. PCIe/NBIO hardware, firmware, a PF driver, a VF guest, or a hypervisor observes the resulting register state according to the access path and permissions.

Because this is PCI configuration-space material, the actual access path may be PCI config access, NBIO/SMN indexed register access, PF-mediated SR-IOV handling, firmware mediation, or hypervisor emulation. Those access paths live outside this generated header.

## State and Persistence Behavior

The header has no local state. It names hardware-visible state in NBIO PCI configuration registers for virtual functions. That state can persist until an explicit write, PCI reset, function-level reset, VF teardown, GPU reset, power transition, firmware action, or hypervisor action changes it.

Important represented state includes:

- Per-VF PCI identity, class code, header type, BIST, BAR, ROM BAR, subsystem ID, capability pointer, and interrupt presentation.
- Per-VF command/status state controlling memory access, bus mastering, interrupt disable, parity/SERR policy, and status/error latches.
- PCIe device/link capability, control, and status state for payload/read-request sizing, relaxed ordering, no-snoop, FLR, completion timeouts, ASPM, link retraining, current speed/width, equalization, LTR, OBFF, emergency power reduction, atomic operations, ID-based ordering, ten-bit tags, and TLP prefix behavior.
- MSI and MSI-X programming state, including address/data fields, vector enable/count, mask and pending bitmaps, MSI-X table location, PBA location, and function-level masking.
- AER state for uncorrectable/correctable errors, mask/severity policy, first-error pointer, ECRC generation/checking, multi-header logging, header log capture, and TLP prefix logs.
- ATS and ARI state used for address translation caching and alternative routing ID behavior in virtualized PCIe topologies.

Many PCIe fields have side effects or special write semantics. Examples include status latches, AER clear/status bits, FLR initiation, link retrain controls, interrupt pending/mask fields, and capability-control enables. The macros only describe bit positions and masks; ordering, polling, write-one-to-clear rules, reset timing, and access permissions must come from the owning driver code and the hardware specification.

## Dependencies and Integration Points

The direct dependencies are the generated NBIO 2.3 register headers:

- `nbio_2_3_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` addresses. For example, this source tree maps `cfgBIF_CFG_DEV0_EPF0_VF13_1_VENDOR_ID` at `0xfffe1030d000`, `cfgBIF_CFG_DEV0_EPF0_VF16_1_PCIE_ATS_CAP` at `0xfffe103102b4`, and `cfgBIF_CFG_DEV0_EPF0_VF17_1_BASE_ADDR_1` at `0xfffe10311010`.
- `nbio_2_3_default.h` supplies reset/default values for the same config-space families, including VF13 through VF17 defaults adjacent to this chunk's register names.
- AMDGPU register-helper macros consume the `__SHIFT` and `_MASK` names through field composition and extraction helpers.

Observed source-tree consumers of `nbio_2_3_sh_mask.h` include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, the main NBIO 2.3 implementation using the matching offset, mask, and default headers.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, virtualization-oriented AMDGPU code that includes this NBIO 2.3 mask header.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`, which include the same generated NBIO headers for platform power-management behavior.

The offset-header chunk for the same VF address blocks supplies full physical-looking config addresses on 0x1000 VF boundaries. This shift/mask chunk supplies bit-level interpretation for those offsets; it does not define which actor may legally access each field.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can alter unrelated PCIe configuration bits, break VF enumeration, corrupt BAR presentation, disable memory or bus-master access, disrupt interrupts, or hide protocol errors.
- The VF maps are highly repetitive. VF14, VF15, and VF16 are structurally near-identical, while VF13 and VF17 are partial at chunk boundaries. Copying a macro from the wrong VF can compile cleanly but target the wrong virtual function.
- Chunk-boundary incompleteness matters. This range starts after `VF13_1_MSIX_PBA` shifts and ends before the `VF17_1_BASE_ADDR_1` mask. The final per-file report should reconcile neighboring chunks before making complete claims about VF13 or VF17.
- PCIe status, AER, FLR, MSI/MSI-X, and link-control fields can have side effects. Treating every mask as an ordinary read/write storage bit can clear evidence, trigger a function reset, retrain a link, mask interrupts, or change guest-visible capability state.
- MSI layout is mode-dependent. Normal and `_64` message-data/mask/pending definitions reflect PCI MSI capability layout variants and aliases, not necessarily independent live storage in every configuration.
- ATS, ARI, atomic operations, LTR, OBFF, ten-bit tags, ID-based ordering, and TLP-prefix controls affect host interconnect behavior. Enabling unsupported combinations in an SR-IOV environment can produce PCIe errors or isolation problems.
- AER header and TLP-prefix logs are diagnostic evidence. Incorrect decoding or clearing can obscure the first failing TLP and make hardware or platform failures harder to triage.
- Access policy is virtualization-sensitive. PF, VF guest, hypervisor, and firmware may see the same generated names but have different access rights and side-effect expectations.

## Test and Validation Signals

Useful validation is mostly compile, generated-header consistency, SR-IOV enumeration, PCIe behavior, and hardware diagnostic coverage:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU/SR-IOV, and SMU11 platform code.
- Compare this shift/mask header against `nbio_2_3_offset.h` and `nbio_2_3_default.h` for VF13 through VF17 to catch missing registers, mask-width drift, and repeated-family naming errors.
- SR-IOV VF enumeration should expose expected PCI IDs, class/header fields, BAR sizing, capability pointer chains, PCIe capability values, MSI/MSI-X capabilities, AER structures, ATS, and ARI for VF14 through VF16, with VF13 and VF17 reconciled through adjacent chunks.
- VF reset and teardown tests should verify FLR initiation, command/status defaults, BAR reset behavior, and return to expected PCI config state.
- MSI/MSI-X interrupt tests should validate message address/data programming, vector enable counts, mask/pending behavior, table/PBA decoding, and function-mask behavior.
- PCIe link and power-management tests should cover payload/read-request sizing, relaxed ordering/no-snoop policy, ASPM/LTR/OBFF controls, link retraining, bandwidth-management status, and equalization status.
- AER error-injection or diagnostic tests should validate uncorrectable/correctable status, masks, severity, first-error pointer, header log capture, TLP prefix log capture, and clear behavior.
- Static checks should verify that VF14, VF15, and VF16 remain mechanically consistent with neighboring VF maps except for intentional VF-number and address differences.

## Unresolved Cross-Chunk References

The first two lines belong to `BIF_CFG_DEV0_EPF0_VF13_1_MSIX_PBA`, whose comment and shift definitions are in the previous chunk. The range then completes the late VF13 capability blocks and contains full VF14, VF15, and VF16 maps. The final line is only `BIF_CFG_DEV0_EPF0_VF17_1_BASE_ADDR_1__BASE_ADDR__SHIFT`; the corresponding mask and all subsequent VF17 fields are in the next chunk. The merge/reconciliation lane should stitch these boundaries before producing the final source-file report.

### subset-b-002949: lines 110671-113093

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 110671-113093

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts inside the PF0 virtual-function 17 block (`BIF_CFG_DEV0_EPF0_VF17_1_*`) at the mask for `BASE_ADDR_1`, after the matching register comment and shift definition in the previous chunk. It then covers the rest of VF17 from BAR2 and PCI header tail fields through PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and ARI capability masks. It includes complete repeated PCI/PCIe configuration images for VF18 and VF19 (`BIF_CFG_DEV0_EPF0_VF18_1_*`, `BIF_CFG_DEV0_EPF0_VF19_1_*`). It begins VF20 (`BIF_CFG_DEV0_EPF0_VF20_1_*`) and carries that block through MSI capability address/data/mask fields, ending at the comment for `MSI_PENDING`; the VF20 MSI pending definitions and later VF20 MSI-X/AER/ATS/ARI fields are outside this chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCI configuration decoder registers that expose PF0 virtual-function PCI and PCIe capabilities. Each register field is represented by generated macros of the form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The companion generated offset headers provide the register addresses; this `*_sh_mask.h` file only gives the bit positions and masks within those registers. AMDGPU consumers normally combine these macros with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The header does not define access width, reset values, ownership, read/write permissions, or side-effect behavior.

## Important Macro Families

The VF17 tail starts with standard PCI configuration-space tail fields. It defines BAR2 through BAR6 and carries a dangling `BASE_ADDR_1` mask from the previous chunk, CardBus CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line and pin, min grant, and max latency. These fields use full 32-bit masks for BAR-like registers, 8-bit masks for legacy byte fields, and split 16-bit masks for subsystem vendor/device identifiers.

The VF17 PCIe capability section defines capability-list metadata, PCIe capability version/device-type fields, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and MSI/MSI-X layout fields. Important feature bits include maximum payload and read request sizing, relaxed ordering, no-snoop, extended tags, function-level reset capability/initiation, correctable/non-fatal/fatal/unsupported request reporting enables, transactions pending, link speed and width, ASPM and clock power management, retrain/link disable/common clock/extended sync, bandwidth-management interrupts, data-link active reporting, DRS signaling, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, ten-bit tag support, emergency power reduction, fast role swap, supported link speeds, compliance/de-emphasis controls, 8 GT/s equalization status, crosslink resolution, and downstream-component presence.

The VF17 interrupt groups define MSI and MSI-X capability layouts. MSI fields cover capability-list metadata, MSI enable, multiple-message capability and enable, 64-bit support, per-vector masking capability, message address low/high, message data, mask, 64-bit data/mask aliases, and pending bits. MSI-X fields cover capability-list metadata, table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

The VF17 vendor-specific and PCIe Advanced Error Reporting groups define enhanced-capability list metadata, vendor-specific header and payload dwords, AER uncorrectable error status/mask/severity, AER correctable error status/mask, AER capability/control, four header-log dwords, and four TLP-prefix-log dwords. The represented AER conditions include DLP, surprise-down, poisoned TLP, flow-control protocol, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, atomic operation egress blocking, and TLP prefix blocking. Correctable-error fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable, and header-log overflow.

The VF17 ATS and ARI enhanced-capability groups define capability-list headers plus payload fields for address-translation services and alternative routing-ID interpretation. ATS fields include invalidate queue depth, page-aligned request support, global invalidate support, smallest translation unit, and ATC enable. ARI fields include MFVC and ACS function-group capability/enable bits, next-function number, and selected function group.

The VF18 and VF19 blocks are complete repeated virtual-function PCI configuration images. Each begins with ordinary PCI header fields: vendor/device ID, command/status, revision and class-code bytes, cache line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. Each then repeats the same PCIe device/link capability, MSI/MSI-X, vendor-specific, AER, ATS, and ARI macro families described for VF17.

The VF20 block is partial. It includes the standard PCI header and BAR-related fields, PCIe capability metadata and device/link capability/control/status fields through link status 2, then begins MSI with `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address low/high, message data, mask, 64-bit data alias, and 64-bit mask alias. The chunk stops before the `MSI_PENDING` shift/mask definitions and before VF20 MSI-X, vendor-specific, AER, ATS, and ARI groups.

## Control Flow

There is no runtime control flow in this header. The effective use pattern in AMDGPU code is:

1. Select the corresponding NBIO 2.3 config-space register offset from the generated offset header or a per-ASIC register table.
2. Read or prepare a PCIe config register value through the driver's PCIe/SOC15 access helpers.
3. Use the `__SHIFT` and `_MASK` constants directly, or through helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, to decode or update a specific field.
4. Write the value back, poll a hardware-owned status bit, clear sticky error state according to PCIe rules, or hand the decoded value to reset, interrupt, virtualization, or RAS/error handling code.

The repeated VF17/VF18/VF19/VF20 naming implies a table-like hardware layout, but this header does not implement iteration. Any loop over virtual functions or capability families is implemented by driver code that chooses the matching register offset and macro family.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes GPU PCI configuration and enhanced-capability state owned by hardware, firmware, the PCIe fabric, the host kernel, and the AMDGPU driver.

Some represented fields are configuration state that can remain programmed until reset, function-level reset, suspend/resume, power transition, or explicit driver reprogramming: PCI command enables, BAR values, MSI/MSI-X message address/data/mask state, PCIe device/link controls, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR/OBFF controls, ATS ATC enablement, and ARI function grouping.

Other fields are hardware-owned status, command strobes, or sticky diagnostic state: PCI status bits, BIST start/completion, device/link status, link training and equalization status, transactions pending, MSI pending bits, AER correctable/uncorrectable status, AER header logs, and TLP prefix logs. The masks do not encode whether a bit is read-only, write-one-to-clear, write-one-to-set, self-clearing, firmware-owned, or volatile; callers must follow the hardware programming guide and PCIe specification behavior for each register.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This `*_sh_mask.h` slice must stay synchronized with sibling generated headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`, especially offset headers that give the register addresses for these field names.

Primary integration is with AMDGPU NBIO, PCIe, interrupt, reset, RAS/AER, SR-IOV, and virtualization paths. These macros support virtual-function config-space exposure and driver-side interpretation of function identity, BARs, command/status, PCIe device/link capabilities, MSI/MSI-X delivery, AER status/logging/masking/severity, ATS address-translation services, ARI routing/function grouping, and function-level reset behavior.

The macros are untyped integer constants. Missing or renamed macro names usually fail at compile time in consuming code, but an incorrect shift or mask can compile cleanly and cause adjacent PCIe fields to be read, cleared, or programmed incorrectly. Because this file is generated ASIC metadata, manual changes should be treated as hardware ABI changes and checked against the authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first line is already inside VF17 `BASE_ADDR_1`, and the last line is only the comment for VF20 `MSI_PENDING`; adjacent chunks are required before making whole-register or whole-VF claims for VF17 and VF20.
- The range mixes 8-bit PCI header fields, 16-bit PCI/PCIe capability words, and 32-bit enhanced-capability dwords. Wrong access width or offset pairing can corrupt neighboring fields even when a mask is locally correct.
- Full-width BAR, ROM base, CIS pointer, MSI address, AER log, TLP-prefix log, and vendor-specific dword fields are not self-validating. Pairing a correct full-width mask with the wrong offset can overwrite or decode unrelated hardware state.
- AER fields are side-effect sensitive. Treating uncorrectable/correctable status bits, severity bits, header logs, or TLP prefix logs as ordinary retained configuration can clear evidence, hide real errors, or misclassify recovery severity.
- Link and device-control fields are interoperability-sensitive. Incorrect max payload/read request, completion timeout, relaxed ordering, no-snoop, FLR, ASPM, retrain, target speed, equalization, or DRS masks can cause enumeration failures, link retraining problems, performance regressions, or reset hangs.
- MSI/MSI-X fields are interrupt-delivery critical. Wrong enable, message address/data, mask, pending, table, PBA, or function-mask fields can cause lost interrupts, spurious interrupts, or poor isolation between virtual functions.
- ATS and ARI fields affect I/O address translation and PCIe function routing. Incorrect STU/ATC enable, queue-depth, global invalidate, ARI forwarding, next-function, or function-group masks can break DMA address translation, virtual-function discovery, or isolation.
- The VF18 and VF19 blocks are highly repetitive and VF20 repeats the same pattern until the chunk boundary. Off-by-one copy or generation errors are plausible and may only appear on configurations that instantiate or exercise the affected virtual function.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, and ARI support enabled; missing symbols should surface as compile failures in NBIO/PCIe/interrupt/virtualization code.
- Run generated-header consistency checks against the NBIO register database and sibling offset headers, including shift/mask pair checks, field width checks, non-overlap checks within each register, and repeated VF layout comparison for VF17 through VF20.
- Boot affected hardware and confirm PCI enumeration exposes stable VF vendor/device IDs, class codes, BARs, capability-list traversal, PCIe capability blocks, MSI/MSI-X capability blocks, AER capability blocks, ATS capability blocks, and ARI capability blocks.
- Exercise SR-IOV or other virtual-function configurations that instantiate VF17, VF18, VF19, and VF20; validate VF config-space reads, BAR sizing, bus mastering/memory enable behavior, FLR, and isolation-relevant capabilities.
- Exercise MSI and MSI-X interrupt delivery from virtual functions under graphics, compute, reset, and virtualization workloads; lost, stuck-pending, or unexpectedly masked interrupts point to field-layout or offset mismatches.
- Run PCIe link/reset tests covering link speed/width reporting, retraining, data-link active reporting, completion timeout handling, FLR initiation/completion, suspend/resume, and error recovery.
- Use AER fault observation or injection where available to validate uncorrectable/correctable status bits, masks, severity mapping, header logs, TLP prefix logs, and driver recovery decisions.
- Validate ATS/ARI behavior in IOMMU and virtualization scenarios, including ATC enablement, invalidation-related fields, ARI forwarding, and function-number routing.

## Chunk-Specific Notes For Merge

This chunk should be merged with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final source-tree-aligned per-file research document. Preserve that this slice specifically covers the PF0 VF17 tail from BAR masks through ARI, complete repeated VF18 and VF19 PCIe config masks, and the start of VF20 through the MSI mask aliases with the `MSI_PENDING` comment as the terminal boundary.

### subset-b-002950: lines 113094-115515

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 113094-115515

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register mask header. It contains C preprocessor `#define` constants for field shifts and masks in the NBIF/BIF PCI configuration decoder for SR-IOV virtual functions on device 0, endpoint function 0. The covered slice starts in the tail of the `VF20` configuration-space block, contains complete `VF21`, `VF22`, and `VF23` address blocks, and ends in the first fields of the `VF24` block.

The chunk is declarative. It defines register-field names, bit positions, and bit masks. It does not define functions, structures, executable logic, runtime storage, or initialization code.

## Purpose

The macros provide symbolic encodings for NBIO PCI and PCIe configuration registers so AMDGPU code can compose, update, and decode register values without embedding raw bit constants at call sites. The repeated macro naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>_MASK`

For this chunk, `<n>` spans the tail of `20`, all of `21`, `22`, and `23`, and the beginning of `24`. The `_1_` namespace indicates this portion of the generated NBIO register map belongs to the second numbered instance or aperture in the naming scheme used by the hardware register generator. Register offsets are supplied by companion address headers; this `_sh_mask.h` slice supplies the per-field bit encodings.

## Address Blocks and Register Coverage

Visible address block markers in this range are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf21_bifcfgdecp` beginning at line 113366.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf22_bifcfgdecp` beginning at line 114062.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf23_bifcfgdecp` beginning at line 114758.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf24_bifcfgdecp` beginning at line 115454.

The line range begins after the `VF20` block has already started. It covers `VF20` from `MSI_PENDING` through MSI-X, vendor-specific PCIe extended capability, Advanced Error Reporting, ATS, and ARI fields. It then covers full `VF21`, `VF22`, and `VF23` blocks with standard PCI header fields, PCIe capability/control/status fields, MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions. It ends at `VF24_1_PROG_INTERFACE__PROG_INTERFACE__SHIFT`, before the corresponding mask and the rest of `VF24`.

Major register groups covered:

- Standard PCI header fields for complete `VF21` through `VF23` and partial `VF24`: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class-code fields, cache line, latency, header type, BIST, BARs, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability structures: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI message address and data registers, mask and pending registers, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific PCIe extended capability fields: enhanced capability list headers, vendor-specific headers, and scratch registers.
- PCIe Advanced Error Reporting fields: AER enhanced capability headers, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- ATS and ARI extended capability fields: ATS capability/control and ARI capability/control fields used by address translation and alternative routing-ID interpretation support.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The public interface is the generated macro namespace.

Important macro families include:

- `*_COMMAND__*`: standard PCI command bits for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, snooping, parity response, SERR, fast back-to-back, and interrupt disable.
- `*_STATUS__*`: standard PCI status bits for interrupt status, capability-list presence, DEVSEL timing, aborts, system error, parity error, and readiness.
- `*_BASE_ADDR_[1-6]__BASE_ADDR*` and `*_ROM_BASE_ADDR__BASE_ADDR*`: BAR and ROM BAR field encodings.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*`: PCIe capability fields for payload size, read request size, error enables, relaxed ordering, no-snoop, FLR initiation, link speed/width, ASPM, retraining, link disable, clock configuration, equalization, and autonomous width/speed control.
- `*_MSI_*` and `*_MSIX_*`: interrupt capability encodings for MSI enable, multi-message control, 64-bit addressing, per-vector mask/pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*`: AER status, mask, severity, ECRC controls, multi-header recording, completion-timeout logging, and log-presence fields.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*`: 32-bit log-word fields used to decode captured TLP headers and prefixes after PCIe errors.
- `*_PCIE_ATS_*` and `*_PCIE_ARI_*`: address translation service and alternative routing-ID interpretation capability/control fields, including invalidate queue depth, page-aligned request support, global invalidate support, STU, ATC enable, next function number, and ARI function-group controls.

Consumers should pair each `*_MASK` with its matching `*_SHIFT` through AMDGPU bitfield helpers such as register-field get/set macros. Masks use `L`-suffixed hexadecimal literals and cover a mix of 8-bit, 16-bit, and 32-bit fields.

## Control Flow

There is no runtime control flow in this chunk. The only compile-time behavior is header inclusion through the surrounding include guard in the full file. Runtime behavior is supplied by code that includes this header and uses these constants to access NBIO-backed PCI configuration registers.

Typical consumer flow inferred from the macro design:

1. Select the per-VF register offset from the companion NBIO register header.
2. Read a PCI config or NBIO MMIO register value using AMDGPU register access helpers.
3. Extract a field with the matching `*_MASK` and `*_SHIFT`, or compose an updated value with the same pair.
4. Write the value back when enabling, disabling, clearing, or programming a PCIe feature.

## State and Persistence Behavior

This header stores no software state and performs no persistence. The state described by these constants lives in hardware PCI configuration and PCIe extended capability registers for SR-IOV virtual functions.

Some represented fields are configuration state that can persist until device reset, VF reset, function-level reset, or PF-driven reinitialization. Examples include `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `INT_DIS`, PCIe error-reporting enables, payload/read request sizing, MSI/MSI-X enablement, MSI-X function mask, ATS `ATC_ENABLE`, ARI controls, link-control bits, and completion-timeout settings.

Other fields represent hardware-observed status or error state, such as PCI status abort/parity bits, PCIe device/link status, AER correctable and uncorrectable status, AER first-error pointers, and TLP header/prefix logs. These may be read-only, sticky, or clear-on-write according to the underlying PCIe register semantics; the header only names the bits and does not enforce access policy.

Because this is VF configuration space, the underlying register contents can also be affected by SR-IOV lifecycle events, guest driver behavior, host PCI core policy, PF virtualization setup, FLR, hot reset, and device teardown/recreation.

## Dependencies and Integration Points

Dependencies are structural and generated-header based:

- The companion NBIO 2.3 register-offset header supplies register addresses; this file supplies field shifts and masks.
- AMDGPU register access and bitfield helper macros are the expected consumers for constructing and decoding register values.
- Linux PCI/PCIe enumeration and configuration paths provide the protocol model reflected by the field names: standard PCI header, PCIe capability, MSI/MSI-X, AER, ATS, and ARI.
- SR-IOV support depends on the repeated VF blocks. `VF21`, `VF22`, and `VF23` are complete in this chunk, while `VF20` and `VF24` require neighboring chunks for full per-VF coverage.
- Interrupt setup integrates through MSI and MSI-X fields, especially message address/data, vector mask/pending registers, table/PBA offsets, MSI-X function mask, and enable bits.
- PCIe error handling and diagnostics integrate through AER status/mask/severity fields, ECRC controls, first-error pointer, and captured TLP header/prefix log fields.
- IOMMU and address translation integration can use ATS fields such as invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.
- ARI integration depends on the ARI enhanced capability list, next-function number, and function-group enable fields used to expose or route extended PCIe function numbering.

## Risks and Edge Cases

- Generated macro drift is the main risk. If a shift or mask differs from the NBIO 2.3 hardware register database, downstream reads and writes can silently target the wrong bits.
- The line-range boundaries are partial. `VF20` begins before this chunk and `VF24` continues after it, so final per-file reconciliation should not treat either as complete from this document alone.
- The repeated VF blocks are intentionally near-identical. Generator or copy errors can be difficult to spot because most lines differ only by `VF21`, `VF22`, or `VF23`.
- Several fields can affect VF availability or data movement if programmed incorrectly, including `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `INITIATE_FLR`, `LINK_DIS`, `RETRAIN_LINK`, MSI/MSI-X enables, MSI-X function mask, ATS `ATC_ENABLE`, and ARI controls.
- AER status, mask, and severity fields use very similar names. Mixing the families can suppress reporting, misclassify errors, or inspect/clear the wrong status.
- Width handling matters. Some masks represent 8-bit or 16-bit PCI fields while others represent full 32-bit registers; consumers should avoid implicit truncation and should preserve reserved bits when updating partial fields.
- BAR and MSI-X table/PBA fields carry address-like encodings where low bits may be selectors or reserved bits. Incorrect masking can corrupt BIR selection or offset alignment.
- The final line contains only `VF24_1_PROG_INTERFACE__PROG_INTERFACE__SHIFT`; its mask is outside this chunk. Any automated completeness check must account for the boundary rather than flagging this as a malformed block in the source file.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency checks, and hardware integration tests:

- Normal AMDGPU build coverage for code that includes `nbio_2_3_sh_mask.h`; duplicate macro names, missing dependencies, or syntax errors should fail compilation.
- Static comparison against the companion NBIO register-offset header and the authoritative AMD register database to confirm every field has the expected shift and mask.
- Pattern checks across complete `VF21`, `VF22`, and `VF23` blocks to confirm equivalent register families have identical field encodings, with only the VF number changing.
- Boundary-aware checks that compare the tail of `VF20` and beginning of `VF24` against adjacent chunks before drawing conclusions about completeness.
- Runtime SR-IOV smoke tests on supported AMD hardware: create VFs, enumerate them, bind host/guest drivers, enable memory and bus mastering, and verify configuration-space access behaves as expected.
- Interrupt tests that program MSI and MSI-X for VFs and confirm vectors are delivered, masking/pending state decodes correctly, and MSI-X table/PBA offsets are sane.
- PCIe capability inspection with `lspci -vv`, debugfs, or driver debug dumps to confirm payload, read request, FLR, link, AER, ATS, and ARI values decode as expected.
- Error-path tests that inject or observe PCIe AER events and verify correctable/uncorrectable status, masks, severity fields, first-error pointer, and header/prefix logs decode correctly.
- Reset and lifecycle tests around VF FLR, PF-driven VF teardown/recreation, and hot reset to confirm control and status fields return to expected values.

### subset-b-002951: lines 115516-117939

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 115516-117939

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants for PCI/PCIe configuration-space bitfields; it does not define functions, structs, variables, executable code, locks, allocation paths, or direct register accesses.

The slice starts inside the `BIF_CFG_DEV0_EPF0_VF24_1` virtual-function block at `PROG_INTERFACE`/class-code area, finishes the remainder of VF24, covers complete repeated blocks for `BIF_CFG_DEV0_EPF0_VF25_1` and `BIF_CFG_DEV0_EPF0_VF26_1`, and then begins `BIF_CFG_DEV0_EPF0_VF27_1`, stopping inside `VF27_1_MSI_MSG_CNTL` after the `MSI_MULTI_EN` shift. The source path sits under a `ceph-client` mirror, but this file is AMDGPU hardware metadata and has no Ceph or distributed-filesystem behavior.

## Purpose

The macros provide symbolic bit positions and masks for NBIO 2.3 SR-IOV virtual-function PCI configuration images. Each field is emitted in the generated pattern:

- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>_MASK`

The companion `nbio_2_3_offset.h` file supplies matching `cfgBIF_CFG_DEV0_EPF0_VF<n>_1_*` addresses. Runtime AMDGPU code combines offsets from that file with this shift/mask header and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Register Coverage

The opening VF24 fragment contains the rest of one VF config-space block. It starts after the earlier `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, and `REVISION_ID` definitions and covers class-code bytes, cache line, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, min/max latency, PCIe capability/control/status, MSI/MSI-X, vendor-specific PCIe extended capability, AER, ATS, and ARI fields.

The complete VF25 and VF26 blocks each include:

- Basic PCI header fields: vendor/device ID, command/status, revision and class code fields, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI and MSI-X fields: MSI capability linkage, message control, address/data, mask and pending fields, 64-bit MSI aliases, MSI-X capability linkage/control, table, and PBA encodings.
- Vendor-specific PCIe extended capability fields: enhanced capability header, vendor-specific header, and two vendor-specific data dwords.
- Advanced Error Reporting fields: AER capability header, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- ATS and ARI fields: capability-list headers, ATS capability/control, ARI capability, and ARI control.

The trailing VF27 fragment covers the same layout only from `VENDOR_ID` through the start of `MSI_MSG_CNTL`. It includes PCI header fields, BARs, PCIe capability and device/link control/status groups, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `MSI_CAP_LIST`, and the first three MSI message-control shifts. The VF27 MSI masks, MSI address/data fields, MSI-X, vendor-specific, AER, ATS, and ARI fields continue in the next chunk.

## Important Macro Families

`*_COMMAND__*` and `*_STATUS__*` encode standard PCI command/status bits such as I/O access, memory access, bus mastering, parity/SERR handling, interrupt disable, capability-list presence, abort conditions, system error, and parity error.

`*_BASE_ADDR_[1-6]__BASE_ADDR_*`, `*_ROM_BASE_ADDR__BASE_ADDR_*`, and MSI-X table/PBA fields describe address or offset-bearing registers. These masks do not express all PCI semantics by themselves; consumers still need to preserve reserved bits and interpret BAR sizing, table BIR, and table offset rules correctly.

`*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` cover PCIe device capability and control state such as max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, phantom functions, FLR capability/initiation, completion timeout controls, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tag support, emergency power-reduction bits, and transaction/error status.

`*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` describe link speed/width capability and negotiated status, ASPM/power-management controls, link disable/retrain, common clock, autonomous width/speed controls, target link speed, compliance/de-emphasis controls, link equalization status, DRS, and downstream/component presence state.

`*_MSI_*` and `*_MSIX_*` map interrupt capability programming fields: MSI enable, multiple-message capability and enable, 64-bit capability, per-vector masking, message address/data, mask/pending registers, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and PBA BIR/offset.

`*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, `*_PCIE_ADV_ERR_CAP_CNTL__*`, `*_PCIE_HDR_LOG*`, and `*_PCIE_TLP_PREFIX_LOG*` map AER status, masks, severity, ECRC, multiple-header recording, header logging, and TLP prefix logging. Error families include DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked.

`*_PCIE_ATS_*` and `*_PCIE_ARI_*` provide virtualization and IOMMU-related fields: ATS invalidate queue depth, page-aligned request, global invalidate support, STU, ATC enable, ARI MFVC/ACS function-group support, next-function number, function-group enables, and selected function group.

## Control Flow

There is no runtime control flow in this chunk. The only compile-time behavior is that including translation units receive the generated macro names. Runtime flow is supplied by AMDGPU code that selects a config-space offset, reads a register value, applies these masks and shifts directly or through helper macros, and then writes an updated value or decodes status for higher-level PCIe, SR-IOV, reset, interrupt, power, or diagnostics paths.

Typical consumers include NBIO/BIF initialization, PCIe link policy, SR-IOV VF lifecycle handling, MXGPU virtualization support, MSI/MSI-X programming, AER diagnostics, ATS/ARI setup, FLR/reset paths, and suspend/resume or runtime power transitions.

## State And Persistence Behavior

This header stores no software state and persists nothing. It describes hardware-backed PCI configuration state for NBIO virtual functions. Some represented values are static capabilities or identity fields, some are software-programmed controls, some are hardware-updated status bits, and some are sticky diagnostic or write-one-to-clear style PCIe/AER state.

State represented by these masks may be changed by PF setup code, guest drivers, the Linux PCI core, firmware, hardware link training, VF FLR, PF-driven VF teardown/recreation, interrupt setup, IOMMU/ATS policy, and PCIe error handling. The masks do not encode access permissions, reset defaults, ownership rules, side effects, or polling requirements; those rules come from PCIe/NBIO hardware documentation and the surrounding driver code.

VF25 and VF26 are complete within this chunk and can be compared locally as repeated layouts. VF24 and VF27 are boundary fragments and require adjacent chunks before making whole-VF conclusions.

## Dependencies And Integration Points

This generated header must stay synchronized with the NBIO register database and these companion generated files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` for register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h` for reset/default values where generated.

In-tree translation units that include `nbio_2_3_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`. The relevant integration surfaces are AMDGPU NBIO register access, PCIe link control, SR-IOV/MXGPU VF management, interrupt delivery, AER logging, ATS/ARI exposure, power-management policy, and reset handling.

The register naming mirrors standard PCI and PCIe capability layouts, so generic Linux PCI core policy and platform firmware behavior also matter for command/status, BARs, PCIe capabilities, MSI/MSI-X, AER, ATS, ARI, LTR, OBFF, completion timeout, link status, and FLR semantics.

## Risks And Edge Cases

- Generated macro drift is the main risk. A stale shift or mask can compile cleanly while decoding or modifying the wrong hardware bit.
- The repeated VF blocks are mechanically similar. Off-by-one suffix mistakes around VF24, VF25, VF26, and VF27 can silently point code or diagnostics at the wrong VF config image.
- This chunk has artificial boundaries. It starts after the beginning of VF24 and ends inside VF27 MSI message control, so final file-level research must merge adjacent chunks for complete VF24 and VF27 coverage.
- Untyped `#define` constants make width mistakes easy. Consumers need to respect whether a field belongs to an 8-bit, 16-bit, or 32-bit PCI config register despite many literals using the same `L` suffix style.
- PCIe control fields are sensitive. Incorrect values for FLR, link disable/retrain, max payload, max read request, completion timeout, relaxed ordering, no-snoop, LTR, OBFF, ARI, ATS, autonomous speed/width disable, or target link speed can cause enumeration failures, DMA ordering bugs, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields affect interrupt delivery. Mask, pending, 64-bit alias, table offset/BIR, or message address/data mistakes can cause lost, misrouted, or unexpectedly masked interrupts.
- AER status, mask, severity, header log, and prefix log registers have different semantics despite similar names. Generic read/modify/write handling can clear diagnostic evidence, leave errors masked, or misclassify severity.
- ATS and ARI fields are virtualization-sensitive. Incorrect ATC enable/STU, invalidate capability interpretation, next-function number, or function-group controls can affect IOMMU translation caching, VF enumeration, and function isolation.
- BAR, ROM, MSI-X table, and PBA fields carry address or offset encodings where low bits may be reserved or selectors. Code should preserve reserved/selector bits according to PCIe layout.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 consumers enabled; missing, renamed, or duplicate macros should surface in files including `nbio_2_3_sh_mask.h`.
- Compare VF25 and VF26 layouts against each other, against neighboring VF blocks, and against `nbio_2_3_offset.h` to confirm register names, order, widths, and repeated VF stride stay synchronized.
- Use static generated-header checks against the AMD hardware register database to catch mask/shift drift before runtime.
- Boot affected hardware and inspect PCIe config exposure for VFs in this range: identity/header fields, BARs, capability list, PCIe device/link capabilities, MSI/MSI-X, AER, ATS, and ARI should decode as expected.
- In SR-IOV or MXGPU configurations, create and remove VFs around VF24 through VF27, bind guest drivers, exercise VF FLR, and verify VF isolation, enumeration, reset, ATS/ARI behavior, and interrupt delivery.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI/MSI-X layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout, LTR/OBFF state, and FLR completion.
- Use AER injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs decode to the expected PCIe errors.
- For ATS-capable configurations, exercise IOMMU/ATS enablement and invalidation paths; translation faults, stale DMA mappings, or inconsistent ATC behavior can point to ATS field issues.

## Chunk Notes

- Lines 115516-116149 are the tail of `BIF_CFG_DEV0_EPF0_VF24_1`, beginning in the class/header area and ending at ARI control.
- Lines 116150-116845 are a complete `BIF_CFG_DEV0_EPF0_VF25_1` address block.
- Lines 116846-117541 are a complete `BIF_CFG_DEV0_EPF0_VF26_1` address block.
- Lines 117542-117939 begin `BIF_CFG_DEV0_EPF0_VF27_1` and stop inside `MSI_MSG_CNTL`; remaining VF27 MSI, MSI-X, vendor-specific, AER, ATS, and ARI fields are outside this work item.

### subset-b-002952: lines 117940-120339

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 117940-120339

## Scope

This chunk is the final slice of AMDGPU's generated NBIO 2.3 shift/mask header. It contains C preprocessor constants for bit shifts and masks in NBIF/BIF PCI configuration decode space for SR-IOV virtual functions and ends with the file footer.

The range starts mid-register in the `VF27_1` configuration-space block, immediately after the first MSI message-control shift definitions. It then completes the tail of `VF27_1`, contains full `VF28_1`, `VF29_1`, and `VF30_1` PCI/PCIe capability blocks, and finishes with the `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` `BIF_BX_PF1_MM_INDEX`/`MM_DATA` indirect access registers plus `#endif`.

The chunk is declarative. It defines register-field names, bit positions, and bit masks only; it has no functions, structures, executable statements, allocation, locking, or initialization code.

## Purpose

The macros provide symbolic encodings for NBIO 2.3 PCI configuration and BIF indirect MMIO registers so AMDGPU code can decode and compose hardware register values without embedding raw bit constants. The dominant naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>_MASK`

where `<n>` is `27`, `28`, `29`, or `30` in this range. The companion `nbio_2_3_offset.h` header supplies register addresses, while this file supplies field layouts. The final `BIF_BX_PF1_MM_*` macros define the field layout for an index/data aperture used to address BIF MM registers through `cfgBIF_BX_PF1_MM_INDEX`, `cfgBIF_BX_PF1_MM_DATA`, and `cfgBIF_BX_PF1_MM_INDEX_HI`.

## Address Blocks and Register Coverage

Visible address-block markers in this slice:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf28_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf29_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf30_bifcfgdecp`
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`

The `VF27_1` block begins before this chunk. This range covers its MSI/MSI-X tail, vendor-specific extended capability, Advanced Error Reporting, ATS, and ARI definitions. `VF28_1`, `VF29_1`, and `VF30_1` are complete within the chunk and repeat the same register families:

- Basic PCI header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, programming interface, subclass/base class, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: MSI capability list, message control, low/high address, data, mask, 64-bit data/mask, pending bits, MSI-X capability list, table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific PCIe extended capability fields: enhanced capability list header, vendor-specific header, and two 32-bit scratch registers.
- PCIe Advanced Error Reporting fields: enhanced capability list header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ATS and ARI extended capability fields: ATS enhanced capability list, invalidate queue depth/page-aligned/global-invalidate support, STU, ATC enable, ARI enhanced capability list, ARI capability bits, next function number, function group enables, and function group value.
- PF indirect MM access fields: `BIF_BX_PF1_MM_INDEX__MM_OFFSET`, `BIF_BX_PF1_MM_INDEX__MM_APER`, `BIF_BX_PF1_MM_DATA__MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI__MM_OFFSET_HI`.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The externally consumed interface is the macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` model standard PCI command/status bits such as I/O access, memory access, bus mastering, SERR, interrupt disable, capability-list presence, abort reporting, parity reporting, and PME status.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, and `*_MSIX_TABLE/PBA__*` expose address/offset fields where low bits encode type, prefetchability, BIR, enablement, or reserved state and must be preserved according to PCI layout.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` cover device/port type, slot implementation, interrupt message number, FLR, payload/read request sizing, relaxed ordering, no-snoop, completion timeout, ASPM, link retrain/disable, negotiated link speed/width, equalization status, and link speed vector fields.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability programming, including MSI enablement, multi-message count, 64-bit MSI addressing, per-vector mask capability, vector mask/pending bits, MSI-X table size, function mask, enable bit, table location, and pending-bit-array location.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define AER status, reporting mask, severity classification, ECRC generation/checking support and enablement, multi-header recording, TLP prefix logging, and completion timeout logging capability.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw 32-bit capture words used when diagnosing PCIe errors.
- `*_PCIE_ATS_*` and `*_PCIE_ARI_*` define address-translation and alternate routing-ID capabilities/controls used when a virtual function participates in IOMMU/ATS and ARI-aware PCIe topologies.
- `BIF_BX_PF1_MM_INDEX*` and `BIF_BX_PF1_MM_DATA*` define the index/data aperture fields for indirect BIF MM access: low offset bits, aperture select bit, high offset bits, and full 32-bit data.

## Control Flow

This header chunk has no runtime control flow. Inclusion is controlled only by the enclosing header guard, which terminates at the `#endif` in this range. At compile time, any translation unit that includes the generated NBIO 2.3 headers receives these constants.

Typical consumer flow is inferred from the macro design:

1. Locate a register through the companion offset header, often via `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` or `cfgBIF_BX_PF1_MM_*` definitions.
2. Read the register through AMDGPU PCI config, MMIO, or indirect register access helpers.
3. Use the `*_MASK` and `*_SHIFT` constants with `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent bit operations.
4. Write back a composed value when enabling or disabling PCIe features, interrupt delivery, AER controls, ATS/ARI behavior, or indirect BIF MM access.

## State and Persistence Behavior

The header stores no software state and performs no persistence. It describes state held in hardware registers. For the VF configuration blocks, the represented state is per virtual function and can be changed by guest drivers, host PCI/SR-IOV orchestration, PF-mediated setup, reset paths, and PCI core policy.

Some fields are persistent configuration controls until reset or function-level reset, such as `BUS_MASTER_EN`, `MEM_ACCESS_EN`, `IO_ACCESS_EN`, `INTERRUPT_DIS`, MSI/MSI-X enable bits, MSI-X function mask, AER masks/severity controls, ECRC enables, ATS `ATC_ENABLE`, ARI function-group controls, completion timeout controls, and PCIe link-control fields.

Other fields expose hardware status or diagnostic capture, including PCI status bits, device/link status bits, correctable and uncorrectable AER status, AER first-error pointer, TLP header logs, TLP prefix logs, MSI pending bits, and link equalization indicators. These may be read-only, sticky, clear-on-write, or hardware-updated depending on the PCIe register model and the NBIO implementation.

The `BIF_BX_PF1_MM_INDEX`/`MM_DATA` aperture has implicit state in the selected indirect offset. A write to the index/high-index registers selects the target location; reads or writes through `MM_DATA` then operate on that target. Ordering and preservation of `MM_APER`, high offset, and low offset fields matter for correctness.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_2_3_offset.h`, which maps these field definitions to concrete register addresses and base indices.
- `nbio_2_3_default.h`, which provides reset/default values for related registers, including the final `BIF_BX_PF1_MM_*` aperture.
- AMDGPU register helper macros and generated-register conventions, especially `REG_GET_FIELD`/`REG_SET_FIELD` style accessors that expect matching `__SHIFT` and `_MASK` macro names.
- Linux PCI, PCIe, MSI/MSI-X, SR-IOV, AER, ATS, ARI, and IOMMU subsystems, whose standard capability layouts are mirrored by the generated field names.
- SR-IOV PF/VF management paths. The repeated `VF27_1` through `VF30_1` blocks are per-VF decode windows for high-numbered virtual functions.
- Interrupt setup and teardown paths through MSI/MSI-X address/data, mask, pending, table, and PBA definitions.
- PCIe diagnostics and recovery paths through AER status/mask/severity and TLP log definitions.
- Low-level NBIO/BIF access code through the final PF1 indirect MM index/data aperture.

## Risks and Edge Cases

- The file is generated and highly repetitive. A single generation error in a shift or mask can silently corrupt every consumer that decodes or composes that field.
- The chunk starts in the middle of `VF27_1_MSI_MSG_CNTL`; earlier MSI control shift definitions for `VF27_1` are outside the range. Final reconciliation should avoid treating this chunk as a complete `VF27_1` block.
- `VF28_1`, `VF29_1`, and `VF30_1` should be structurally identical except for the VF number. Copy-generation drift is hard to catch manually because most definitions differ only by that numeric prefix.
- AER field families have very similar names for status, mask, and severity. Mixing them can suppress error reporting, misclassify uncorrectable errors, or inspect/clear the wrong hardware state.
- MSI/MSI-X table/PBA and BAR-like fields include encoded low bits. Consumers must not treat all masked address bits as a plain byte address.
- Link-control fields such as retrain, disable, autonomous width/speed controls, equalization controls, and compliance bits can affect device reachability if written incorrectly.
- ATS and ARI control bits interact with IOMMU and PCIe routing policy. Enabling ATC or ARI behavior without platform support can break DMA translation or function discovery.
- The `BIF_BX_PF1_MM_INDEX` aperture is stateful. Concurrent users or missing serialization around index/data sequences can target the wrong indirect register.
- Literal widths vary between 8-bit, 16-bit, and 32-bit fields while the masks use `L` suffixes. Consumers should avoid implicit truncation or signedness assumptions.

## Test Signals

Useful validation signals for this chunk:

- Compile coverage of AMDGPU code that includes `nbio_2_3_sh_mask.h`; missing, duplicated, or malformed macros should fail normal builds.
- Generated-register consistency checks comparing this `_sh_mask.h` range against `nbio_2_3_offset.h`, `nbio_2_3_default.h`, and the upstream hardware register database.
- Pattern checks across `VF28_1`, `VF29_1`, and `VF30_1` to confirm matching field shifts and masks for the same register families; separately account for the partial `VF27_1` boundary.
- SR-IOV runtime smoke tests with enough VFs enabled to exercise VF27 through VF30: enumerate VFs, bind host/guest drivers, enable memory and bus mastering, and verify config-space decoding.
- MSI/MSI-X tests on high-numbered VFs: program vectors, toggle masks, check pending state, and confirm interrupts are delivered and quiesced as expected.
- PCIe capability inspection using driver debug output or `lspci -vv` to verify payload sizes, link width/speed, FLR, MSI/MSI-X, AER, ATS, and ARI fields match hardware expectations.
- AER injection or observation tests to verify correctable/uncorrectable status, mask, severity, first-error pointer, TLP header logs, and TLP prefix logs decode correctly.
- Reset and lifecycle tests around VF FLR, PF teardown/recreation, and guest detach/attach to confirm status/control fields return to expected defaults.
- Indirect MM aperture tests that write index/high-index/data in controlled sequences and verify `MM_OFFSET`, `MM_APER`, `MM_OFFSET_HI`, and `MM_DATA` select and transfer the expected register contents.
