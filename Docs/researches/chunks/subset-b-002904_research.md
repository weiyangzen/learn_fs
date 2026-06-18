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
