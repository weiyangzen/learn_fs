# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 9851-12254

## Scope And Purpose

This chunk is a middle range of the generated NBIF 6.3.1 shift/mask header. It contains no executable C code, functions, structs, or storage. Its job is to publish C preprocessor constants for hardware register bit positions and masks. Consumers combine these constants with register offsets from `nbif_6_3_1_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG`.

The range starts in the `nbif_rcc_dev0_BIFDEC1` register block with root-complex/device control fields, continues through the `nbif_rcc_dev0_epf0_BIFDEC2` MSI-X vector table, the large `nbif_rcc_strap_BIFDEC1` strap register block, the `nbif_bif_bx_pf_BIFPFVFDEC1` PF/VF-facing BIF control block, the `nbif_rcc_dev0_epf0_BIFPFVFDEC1` EPF0 runtime fields, GDC and GDC S2A doorbell control blocks, and ends partway through the `nbif_bif_cfg_dev0_epf2_bifcfgdecp` PCI configuration-space field map at `BIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_MASK`.

The primary purpose of this chunk is to make NBIF PCIe/root-complex, strap, power-management, doorbell, HDP flush, mailbox, SR-IOV, and PCI config-space fields addressable by name in the AMDGPU driver. The directly relevant in-tree implementation is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes this header and uses several field families from this exact range for ASIC revision discovery, ASPM/LTR strap programming, doorbell routing, doorbell self-ring aperture setup, HDP flush masks, and memory-size reporting.

## Important APIs, Types, And Macro Families

The `RCC_DEV0_0_RCC_*` family describes NBIF root-complex/device behavior for device 0. It includes SR-IOV invalid-register interrupt enablement, BACO request disables, reset enablement, VDM support, PCIe margining parameter discovery, GPUIOV and GPU host-VM enablement, console IOV mode, VF offset/stride, peer register ranges, bus-control policy, configuration aperture sizing, XDMA aperture bounds, feature-control "misc" bits, bus-number and dev/function ID lists, host bus number capture, peer framebuffer offset registers, link-down entry/exit controls, LTR switch latency, and memory-hub arbitration controls.

The root-complex bus and feature fields are broad control surfaces. `RCC_DEV0_0_RCC_BUS_CNTL` covers PMI IO/memory/bus-master disable controls, root error logging, poisoned completion behavior, downstream completion-abort/unsupported-request signaling, and private max-payload/max-read-request sizing. `RCC_DEV0_0_RCC_FEATURES_CONTROL_MISC` covers CRS return, ATC/PASID unsupported-request behavior, ignoring specific translated request classes, MSI/MSI-X pending clearing behavior, BME checks, poison checks, and ECRC device-error reporting.

The `RCC_DEV0_EPF0_GFXMSIX_*` macros describe four EPF0 graphics MSI-X vectors plus the pending-bit array. For each vector the fields cover low/high message address, message data, and vector-mask control. These constants are not heavily used in `nbif_v6_3_1.c`, but they define the local register view for interrupt table programming and diagnostics.

The `RCC_STRAP0_RCC_BIF_STRAP*` family is a large fuse/ROM/software strap surface for BIF/NBIF behavior. It includes generation enables/disables, VGA and ROM strap bits, aperture sizing, GPUIOV, error-ignore policy, AP/SWUS/SUC/SUM access policy, margining readiness, DLF/PHY capabilities, LTR and ASPM strap policy, power-break debounce/timer settings, VLINK timers, register-protection behavior, emergency power reduction, and register-aperture remapping. In `nbif_v6_3_1_program_ltr()` and `nbif_v6_3_1_program_aspm()`, `RCC_STRAP0_RCC_BIF_STRAP2`, `STRAP3`, and `STRAP5` masks/shifts are used to clear and then program LTR/ASPM-related strap fields.

The `RCC_STRAP0_RCC_DEV0_PORT_STRAP*` family describes the port-level PCIe capability straps for device 0. It includes link capabilities, maximum link speed/width, ASPM support, L1 acceptable latency, port type/number, slot and surprise-down capability, DRS, completion-timeout ranges, LTR support, OBFF, TPH, L1 PM substates, DPC, lane margining, lane equalization behavior, DLF, emergency power reduction, and other port feature advertisement knobs. These straps feed the PCIe capability values exposed by the device and must match platform policy and silicon support.

The `RCC_STRAP0_RCC_DEV0_EPF0_STRAP*` and `RCC_STRAP0_RCC_DEV0_EPF1_STRAP*` families describe endpoint-function identity and capability straps. EPF0 fields include device/revision IDs, function enablement, legacy device type, D-state support, soft-reset behavior, resize BAR, PASID width/capabilities, MSI/MSI-X, AER/ACS/ATS/DPA/DSN, subsystem IDs, PME, FLR, atomic operation support, doorbell/ROM/IO/memory/register BAR aperture sizing, VF aperture sizing, VGA disable, SR-IOV VF mapping mode, GPUIOV VSEC revision, and related VF protection. EPF1 has a similar but smaller set for the second function. `nbif_v6_3_1_get_rev_id()` reads `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and extracts `STRAP_ATI_REV_ID_DEV0_F0` through this header's mask/shift pair.

The `BIF_BX_PF0_*` family covers PF-facing BIF status and service registers. It includes BME-low DMA status, unsupported atomic error logging and clear bits, doorbell self-ring GPA aperture base high/low/control, HDP coherency flush control registers, GPU HDP flush request/done bitmaps for CP0-CP9 and SDMA0-SDMA1, BIF transaction-pending bits, four transmit and receive mailbox data words, mailbox valid/ack controls, mailbox interrupt enables, and a compact VM/HV mailbox. `nbif_v6_3_1_enable_doorbell_selfring_aperture()` programs the self-ring aperture base/control fields, and the exported `nbif_v6_3_1_hdp_flush_reg` structure uses `BIF_BX_PF0_GPU_HDP_FLUSH_DONE__CP*` and `__SDMA*` masks from this range.

The `RCC_DEV0_EPF0_RCC_*` family covers runtime EPF0 sideband fields. It includes invalid SR-IOV access and doorbell-read error status, the global doorbell aperture enable bit, configured memory size, a reserved config register, and the IOV function identifier plus IOV enable bit. `nbif_v6_3_1_get_memsize()` reads `RCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`; `nbif_v6_3_1_enable_doorbell_aperture()` writes `RCC_DEV0_EPF0_RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN`.

The `GDC0_*` family describes general GDC controls, including SHUB register request protection, A2S FIFO arbitration, medium-grain clock-gating controls, S2A arbitration/performance behavior, power-gating misc/master/slave controls, and ATDMA arbitration weights. The clock-gating hooks in `nbif_v6_3_1.c` are currently empty, but these fields are the register surface that future NBIF/GDC clock-gating or power-gating code would use.

The `GDC_S2A0_S2A_DOORBELL_ENTRY_0_CTRL` through `GDC_S2A0_S2A_DOORBELL_ENTRY_15_CTRL` macros are a repeated 16-port doorbell routing table. Each entry has an enable bit, AWID field, fence enable, range offset, range size, 64-bit support disable, range-offset deduction, drop enable, and high address nibble. `nbif_v6_3_1_sdma_doorbell_range()` uses entry 2 for SDMA, `nbif_v6_3_1_ih_doorbell_range()` uses entry 1 for IH, `nbif_v6_3_1_vcn_doorbell_range()` uses entries 4/5 for VCN instances, and `nbif_v6_3_1_gc_doorbell_init()` writes fixed values to entries 0 and 3 for graphics command processor routing. The chunk also defines common doorbell fence controls and a GFX doorbell status/all-clear register.

The `BIF_CFG_DEV0_EPF2_*` family is the EPF2 PCI configuration-space field map. It includes standard PCI header registers, command/status bits, revision/class/prog-interface, BARs, ROM BAR, interrupt line/pin, capability-list pointers, vendor-specific capability fields, power-management capability/control fields, PCIe capability/device/link controls and status, MSI/MSI-X capabilities, MSI address/data/mask/pending registers, VSEC headers/scratch registers, AER enhanced-capability headers, uncorrectable error status, and the start of uncorrectable error mask fields. This range stops before the matching severity and correctable-error/AER tail, which begins in the next chunk.

## Control Flow And Runtime Use

There is no runtime control flow in this header. Inclusion and macro expansion happen at compile time. Runtime behavior is in C files that use these names to preserve or update individual hardware register fields.

`nbif_v6_3_1_get_rev_id()` reads the EPF0 strap register, chooses an alternate offset for IP version `7.11.4`, then masks and shifts the `STRAP_ATI_REV_ID_DEV0_F0` field. That path depends on this chunk's EPF0 strap field layout while the actual register address comes either from `nbif_6_3_1_offset.h` or a locally defined NBIF 4.10 compatibility offset.

Doorbell configuration is the most active direct use of this chunk. SDMA instance 0 reads doorbell entry 2, sets enable/AWID/range offset/range size/address-high-nibble fields when doorbells are enabled, or clears the range size when disabled, and writes the register back. IH does the same with entry 1. VCN uses entry 4 or 5 depending on instance and programs AWID/address-high values differently for each instance. Graphics doorbell initialization writes fixed values to entries 0 and 3. The helper paths also switch to locally defined NBIF 4.10 offsets on IP version `7.11.4`, while still using this chunk's field masks.

Doorbell aperture control has two layers. `nbif_v6_3_1_enable_doorbell_aperture()` toggles the EPF0 `BIF_DOORBELL_APER_EN` bit. `nbif_v6_3_1_enable_doorbell_selfring_aperture()` builds a PF0 self-ring aperture control value from enable/mode/size fields and writes low/high base registers from `adev->doorbell.base`. The field masks in this chunk therefore gate both external doorbell BAR exposure and the internal self-ring GPA aperture.

HDP coherency integration uses this chunk in two ways. `nbif_v6_3_1_get_hdp_flush_req_offset()` and `nbif_v6_3_1_get_hdp_flush_done_offset()` return SOC15 offsets for the request/done registers defined alongside these masks. The exported `nbif_v6_3_1_hdp_flush_reg` maps CP and SDMA done masks to the common NBIO HDP flush machinery, so command processor and SDMA clients can wait on the correct hardware acknowledgement bits after cache/coherency flush requests.

ASPM and LTR setup uses several strap masks/shifts from this chunk. Under `CONFIG_PCIEASPM`, `nbif_v6_3_1_program_ltr()` clears `RCC_STRAP0_RCC_BIF_STRAP2__STRAP_LTR_IN_ASPML1_DIS` and then updates Linux PCIe capability state. `nbif_v6_3_1_program_aspm()` clears VLINK ASPM and LDN timer fields, coordinates with PCIE block registers from the separate `pcie_6_1_0_sh_mask.h` header, programs PCI config LTR values through Linux PCI helpers, then writes timed values back through `RCC_STRAP0_RCC_BIF_STRAP3` and `STRAP5` shifts.

PCI configuration-space macros in the EPF2 section are mostly register-interface surface in this driver slice. They mirror the layout of standard PCI/PCIe fields and can be used by lower-level debug, RAS, firmware, virtualization, or capability setup code. Their correctness is still important because the offset/default headers expose the matching register addresses and because the same naming convention is used across AMD generated register headers.

## State And Persistence Behavior

The header itself has no storage, allocation, locking, persistence, or side effects. It only contributes constants to compiled C objects.

The described registers are persistent hardware state until reset, power transition, firmware reinitialization, or explicit driver writes. Important persistent state includes BIF strap policy, device/function identity, PCIe capability advertisement, doorbell aperture enablement, doorbell routing ranges, self-ring doorbell GPA base/control, HDP flush request/done state, mailbox valid/ack/data state, BME and transaction-pending status, SR-IOV/IOV function identifiers, GDC clock/power gating controls, and PCI config capability/status/error registers.

Several fields are status or latch-and-clear by convention. Examples include BME-low status with a clear bit, unsupported atomic error status with separate clear bits, HDP flush done masks, BIF transaction-pending bits, mailbox valid/ack handshakes, invalid SR-IOV access status, doorbell-read access status, GFX doorbell status/all-clear state, PCI status error bits, MSI/MSI-X pending state, and AER uncorrectable error status. The masks do not encode access type, so callers must know whether a field is read-only, write-one-to-clear, sticky across reset domains, strap-derived, or ordinary read/write.

Strap registers deserve special care because they bridge persistent platform/fuse/ROM policy and runtime writes. Some strap bits are read as capabilities or identity; others are modified at runtime by ASPM/LTR setup. Incorrect writes can change advertised PCIe capabilities, power behavior, reset behavior, access protection, or SR-IOV aperture layout until the next hardware reset or reinitialization.

Doorbell routing state is persistent and directly affects command submission paths. If range offset/size or AWID values are stale or wrong, CPU writes to doorbell pages can be dropped, routed to the wrong engine, or accepted for an unintended function. Disabling a doorbell range is represented by setting the range-size field to zero in the current NBIF code, not by clearing every field in the entry.

HDP flush request/done registers are synchronization state between GPU engines and host-visible memory/coherency paths. The common AMDGPU HDP flush code relies on stable engine-specific mask values for CP0-CP9 and SDMA0-SDMA1; a wrong bit mapping would cause waits on the wrong engine's completion bit or premature completion.

## Dependencies And Integration Points

The closest sibling dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`, which supplies register addresses and base indices. This shift/mask file only supplies field layouts. There is no `nbif_6_3_1_default.h` in the immediate direct include path observed for `nbif_v6_3_1.c`; defaults, where needed, are hard-coded, read from hardware, or controlled by firmware/platform straps.

The main C integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`. It includes this header and `nbif_6_3_1_offset.h`, then exposes `nbif_v6_3_1_funcs` as the NBIO function table for this generation. The function table plugs into AMDGPU's broader NBIO abstraction for HDP flush offsets, PCIe indirect offsets, revision ID, memory-controller access, memory-size reporting, SDMA/VCN/IH/GC doorbell setup, doorbell aperture controls, clock-gating hooks, interrupt control, register remapping, ROM offset reporting, ASPM programming, and RAS interrupt setup.

The macros integrate with standard AMDGPU register helper conventions. `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. `REG_GET_FIELD(value, REGISTER, FIELD)` expects the same pair. Any spelling or mask drift from the generated naming contract becomes either a compile-time error or, worse, a build-clean wrong bit manipulation.

PCIe integration crosses subsystem boundaries. `nbif_v6_3_1_program_aspm()` combines NBIF strap fields from this chunk, PCIE block fields from `pcie_6_1_0_sh_mask.h`, and Linux PCI helpers such as `pcie_capability_read_word`, `pcie_capability_set_word`, `pcie_capability_clear_word`, `pci_find_ext_capability`, and `pci_write_config_dword`. The NBIF strap fields must stay consistent with what Linux sees in PCI capability space.

Display integration is indirect. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes `nbif_6_3_1_offset.h` but not this shift/mask header in the inspected include region. That means display code may need NBIF register offsets for resource setup, while field-level manipulation for this ASIC generation is concentrated in AMDGPU NBIF/NBIO code.

Firmware and virtualization integration is implied by several field families. BACO, GPUIOV, SR-IOV invalid-access status, VF aperture sizing, IOV function identifiers, VM/HV mailbox fields, doorbell protection controls, PASID/ATS/ACS straps, and VSEC/AER fields all describe interfaces that may be coordinated with PSP/firmware, hypervisor flows, PF/VF isolation, or platform policy even when only a subset is actively touched by the visible driver code.

## Risks And Edge Cases

Manual edits are high risk because this is generated register metadata. A single incorrect shift or mask can compile cleanly while programming a neighboring field in hardware.

Doorbell entry fields are dense and repeated. Entries 0-15 share the same layout but different port-numbered macro names. Reusing the wrong register name in `REG_SET_FIELD` can set the wrong bit positions if a future ASIC changes a single entry layout, and using the wrong offset can route doorbells to the wrong hardware port. Existing code also uses entry 4 field names while writing either entry 4 or entry 5 for VCN, relying on identical layouts.

Range values for doorbell entries are packed into limited-width fields. `S2A_DOORBELL_PORT*_RANGE_OFFSET` is masked by `0x0001FF80`, and range size by `0x01FE0000`. Oversized or unvalidated `doorbell_index` or `doorbell_size` values are truncated by `REG_SET_FIELD`, which can create a plausible but incorrect route. Tests should cover high doorbell indices and disabled ranges.

The IP version `7.11.4` special case uses local NBIF 4.10 offset constants while keeping NBIF 6.3.1 field masks. That works only if the relevant register bit layouts are identical across those register address variants. Any future change to layout compatibility needs explicit review rather than assuming the offset alias is enough.

Strap fields mix static identity/capability bits with runtime policy bits. Clearing or setting the wrong strap field can change PCIe capability advertisement, reset behavior, access protection, ASPM/LTR timing, emergency power behavior, or SR-IOV layout. Runtime writes should preserve unrelated strap fields through read-modify-write and should be guarded by hardware generation and platform policy.

ASPM/LTR programming crosses NBIF straps, PCIE link-control registers, and Linux PCI config space. A mismatch can lead to link instability, missing LTR enablement, higher idle power, resume failures, or latency regressions. The driver clears some fields first and then writes timed values; interrupted or partial programming could leave conservative or inconsistent link-policy state.

HDP flush bit mappings are synchronization-critical. If a CP or SDMA done mask is wrong, clients may wait forever, skip a required memory flush, or observe stale memory. Because the register exposes many reserved engine bits as well, accidental use of reserved masks could hide a real completion failure.

SR-IOV and GPUIOV fields are security-sensitive. Invalid register access status, VF aperture sizing, VF mapping mode, IOV function identifier, doorbell aperture enablement, and VM/HV mailbox fields all affect isolation or PF/VF communication. Wrong masks can expose doorbells or BAR apertures to the wrong function, fail to report invalid access, or corrupt mailbox handshakes.

PCI config-space fields must match standard PCI/PCIe semantics. Misdescribing `COMMAND`, `STATUS`, MSI/MSI-X, device/link capability, or AER fields can break enumeration, interrupt delivery, link diagnostics, or error containment. This chunk ends in the middle of the AER uncorrectable mask family, so reconciliation with the following chunk is necessary for a complete EPF2 error-reporting picture.

## Test Signals

Build coverage should compile the AMDGPU NBIF implementation that includes `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`. Macro naming or missing field pairs generally show up as compile errors in `REG_SET_FIELD`, `REG_GET_FIELD`, or direct mask references.

Generated-header validation should compare this file against the authoritative ASIC register source and `nbif_6_3_1_offset.h`. Useful local checks include verifying every field has both `__SHIFT` and `_MASK`, masks align with shifts and expected widths, and repeated families such as `GDC_S2A0_S2A_DOORBELL_ENTRY_0_CTRL` through `_15_CTRL` remain layout-identical.

Doorbell runtime tests should exercise GC, IH, SDMA, and VCN doorbells on supported hardware. Confirm that enabled ranges accept doorbell writes, disabled ranges stop routing, high range offsets do not truncate unexpectedly, and the IP version `7.11.4` alternate offsets produce the same behavior as the normal offsets on their target hardware.

HDP flush tests should issue CP and SDMA work that requires host-data-path coherency, request flushes, and verify the matching done bits for CP0-CP9 and SDMA0-SDMA1 are observed through the common NBIO flush path. Timeouts or stale memory after a flush are strong signals of wrong offset or mask mapping.

ASPM/LTR tests should boot with `CONFIG_PCIEASPM`, inspect PCIe capability state before and after `program_aspm`, exercise suspend/resume and idle transitions, and confirm that `RCC_STRAP0_RCC_BIF_STRAP2`, `STRAP3`, and `STRAP5` fields match expected policy without disturbing unrelated strap bits. Link retraining errors, LTR disablement, or elevated idle power are useful failure signals.

Revision and identity tests should verify that `nbif_v6_3_1_get_rev_id()` returns the expected value from EPF0 strap fields on both standard NBIF 6.3.1 offsets and the `7.11.4` alternate-offset path. PCI enumeration should expose the expected vendor/device/class/subsystem/capability values for EPF2 if that function is present and enabled.

SR-IOV and isolation tests should cover PF and VF configurations. They should validate invalid-access status reporting, VF aperture sizing, VF mapping mode, doorbell aperture access, IOV function identifiers, and VM/HV mailbox handshakes. The expected signal is that VFs can access only their intended BAR/doorbell resources and that invalid access does not silently pass.

PCIe error-reporting tests should inject or observe AER conditions where possible and confirm `BIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_STATUS` and mask fields decode DLP, surprise down, poison, flow-control, completion timeout/abort, unexpected completion, overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal, blocked TLP, and related error bits consistently with the PCIe specification and the next chunk's continuation fields.
