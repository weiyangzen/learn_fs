# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 19462-21877

## Chunk Scope

- Work item: `subset-b-003154`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, lines 19462-21877
- Parent file role: generated AMDGPU NBIO 7.2.0 register offset map used by SOC15 register access macros.
- Chunk shape: 2,348 preprocessor definitions, representing 1,174 register symbols plus one paired `*_BASE_IDX` definition for each symbol. Every `*_BASE_IDX` in this span is `5`.

## Purpose

This chunk contributes register-offset constants for the NBIO 7.2.0 block used by AMD GPU kernel code. It does not implement runtime behavior directly. Its job is to provide stable symbolic register names and base-index metadata for code that calls macros such as `SOC15_REG_OFFSET(NBIO, instance, reg...)`, `RREG32_SOC15(...)`, `WREG32_SOC15(...)`, and PCIe-port register helpers.

The covered registers are concentrated in debug/trap access, RAS and parity handling, NBIF/BIF/RCC virtualization and doorbell routing, GDC doorbell ranges, and two PCIe logical-root-port configuration spaces (`BIFPLR0_1` and `BIFPLR1_1`). These definitions are consumed indirectly by NBIO support code such as `amdgpu/nbio_v7_2.c` and display resource files that include this header for NBIO 7.2.0 hardware.

## Major Register Families In This Chunk

- Lines 19462-19812 continue a previous address block and define `SCRATCH_4`, `SCRATCH_5`, trap request/response registers, `TRAP0` through `TRAP15` match registers, bridge/security status registers, sideband bridge controls, and MCA SMN interrupt request registers. The chunk begins after the address-block marker from the prior chunk, so the merge pass should retain the previous block context.
- Lines 19814-19815 mark `nbio_iohub_nb_security_security_cfgdec` at base `0x13b18000`, but this chunk shows only the marker and no register macros under it before the next block.
- Lines 19818-20115 define `nbio_iohub_nb_rascfg_ras_cfgdec` at base `0x13b20000`. This section includes parity controls, global RAS status, uncorrectable/correctable/UCP parity status and counters for groups 0-7, miscellaneous RAS controls, per-event action-control registers for parity and PCIe/NBIF port error classes, sync flood/NMI status, poison status/masks/severity, and APML status/control/trigger registers.
- Lines 20118-20125 define PF2 indexed MMIO registers for `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`, including `BIF_BX_PF2_MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- Lines 20128-20223 define `nbio_nbif0_bif_bx_SYSDEC`, including PF2 PCIe index/data windows and SBIOS/BIOS scratch registers.
- Lines 20226-20227 mark `nbio_nbif0_syshub_mmreg_syshubdec`, but no register macros appear in this chunk under that marker.
- Lines 20230-20425 cover several RCC strap, endpoint, downstream, and downstream-port decode blocks. These include reset, PLL, hotplug, slot capability, link control, lane count, transmitter/rx, strap, LTR, and PCIe error-control registers for device 0 pathing.
- Lines 20428-20547 cover RCC endpoint PF/VF decode and device decode registers. Important groups include duplicated PF/VF aliases for error logs, doorbell aperture enable, configured memory size, IOV function identifiers, GPU IOV region/HostVM controls, console IOV controls, peer register and framebuffer offsets, bus-number lists, requester-id restore, LTR switch controls, and multi-host arbitration.
- Lines 20550-20695 define `nbio_nbif0_bif_bx_BIFDEC1`. This is a dense NBIF/BIF control group: straps, indirect-access control, bus and reset controls, interrupts, doorbell and framebuffer enables, BACO timing controls, NBIF graphics address LUT entries 0-15, VF register-write/doorbell/framebuffer enable and status registers, HDP flush remap controls, BIF ring-buffer controls, mailbox index, GPUIOV config sizes, pad controls, PCIe parameter save/restore, and S5 memory power controls.
- Lines 20698-20751 define PF2-specific BIF/PF/VF registers, including BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate controls, GPU HDP request/done registers, transaction-pending status, graphics address LUT bypass, mailbox transfer/receive buffers, mailbox control/interrupt control, and VM/HV mailbox.
- Lines 20754-20817 define GDC1 registers. They include SDP/SHUB/MP4SDP controls, MGCG controls, doorbell status, and doorbell range registers for SDMA, IH, VCN, RLC, UVD, VCE, ACP, and DSC engines.
- Lines 20820-20923 define a second RCC endpoint PF/VF decode set, including `RCC_DEV0_EPF0_2_*` error logs, command memory region, more IOV region/HostVM controls, and per-function doorbell aperture config/memory size/function identifier aliases.
- Lines 20926-21471 define `nbio_pcie0_bifplr0_cfgdecp`, the first large PCIe logical-root-port configuration group. It maps standard and extended PCIe config-space-like registers: device/vendor IDs, command/status, BARs, capabilities, link control/status, bridge controls, MSI/MSI-X, PCIe capability fields, AER status/masks/severity/logs, root error command/status, secondary capabilities, lane equalization, ACS, multicast, L1 PM substates, DPC, RP PIO error reporting/logging, ESM, data-link feature, 16 GT PHY/link status/equalization, margining, CCIX/ESM capabilities, and 20 GT ESM lane equalization.
- Lines 21474-21877 begin `nbio_pcie0_bifplr1_cfgdecp`, a second PCIe logical-root-port configuration group with the same general structure as `BIFPLR0_1`. This chunk covers the first part through 16 GT link/equalization and the start of PCIe margining lane controls. It ends mid-table at `BIFPLR1_1_LANE_1_MARGINING_LANE_CNTL_BASE_IDX`; remaining lane margining status/control definitions continue in chunk 10.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage definitions in this chunk. The public interface is entirely preprocessor symbols:

- Register-offset macros such as `regTRAP_STATUS`, `regRAS_GLOBAL_STATUS_LO`, `regBIF_BX2_BIF_DOORBELL_CNTL`, `regBIF_BX_PF2_GPU_HDP_FLUSH_REQ`, `regGDC1_BIF_IH_DOORBELL_RANGE`, `regBIFPLR0_1_PCIE_UNCORR_ERR_STATUS`, and `regBIFPLR1_1_LINK_STATUS_16GT`.
- Paired base-index macros such as `regTRAP_STATUS_BASE_IDX` and `regBIFPLR1_1_LINK_STATUS_16GT_BASE_IDX`, all set to `5` in this chunk. SOC15 access code uses the base index to select the proper register base for the IP block/version.
- Indexed/indirect access registers (`*_MM_INDEX`, `*_MM_DATA`, `*_PCIE_INDEX`, `*_PCIE_DATA`) that let runtime code reach subregister spaces through index/data windows.
- Doorbell routing and virtualization registers (`*_DOORBELL_*`, `*_GPUIOV_*`, `*_VF_*`, `*_MAILBOX_*`) that are central to queue notification, SR-IOV/MxGPU-style partitioning, and PF/VF communication.
- PCIe configuration-space aliases under `BIFPLR0_1` and `BIFPLR1_1`, which expose link training, AER, DPC, ACS, L1 PM substates, multicast, ESM, PHY 16 GT, 20 GT, and margining features.

## Control Flow

This header has no executable control flow. Runtime flow is created by users of the symbols:

1. Driver code selects a symbolic register name for a particular NBIO operation.
2. SOC15 helper macros combine the register offset macro, the corresponding `*_BASE_IDX`, IP block identity, and instance number into an MMIO address.
3. The driver reads, writes, or polls that address through AMDGPU register access helpers.

The chunk's control-flow significance is therefore data-driven. For example, NBIO code that configures HDP flush, doorbell range, interrupt routing, or PCIe link behavior depends on these offset values resolving to the intended hardware registers.

## State And Persistence Behavior

The file itself has no mutable process state and does not persist data. The registers it names are hardware state:

- Trap, scratch, mailbox, and response registers can hold transient debug or firmware/driver communication state.
- RAS/parity/poison/AER/DPC/RP PIO status registers reflect hardware error state and may be sticky until cleared by driver policy.
- Doorbell aperture/range, VF enable, GPUIOV, HostVM, peer offset, and mailbox-control registers affect live device routing and virtualization state.
- PCIe link, lane equalization, L1 PM substate, 16 GT/20 GT, and margining registers reflect or influence physical/link-layer state.
- BACO, S5 memory power, reset, pad, and save/restore controls participate in power-management and reset persistence across low-power or resume paths.

Because this is a generated offset header, persistence risk is not in the source file itself. Risk lies in stale or mismatched offsets causing the driver to mutate the wrong hardware state.

## Dependencies And Integration Points

- Included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, where NBIO 7.2.0-specific helper functions use SOC15 read/write macros for doorbells, HDP flush, interrupts, PCIe controls, and related operations.
- Included by display resource code under `drivers/gpu/drm/amd/display/dc/resource/dcn301/` and `dcn31/`, giving display code access to NBIO 7.2.0 offsets when resource logic needs NBIO registers.
- Depends on the AMDGPU SOC15 register-base machinery outside this file. The numeric `*_BASE_IDX` values are meaningful only when paired with the generated IP-base tables and access macros.
- Integrates with adjacent generated headers for bitfield masks/shifts. Offset headers identify register locations; field headers are needed to safely manipulate individual bits.
- Related NBIO offset headers, such as `nbio_7_7_0_offset.h`, `nbio_7_9_0_offset.h`, and `nbio_7_11_0_offset.h`, define similar names with different offsets or base indices. Porting code across ASIC generations must use the matching header/version.

## Risks And Edge Cases

- The chunk starts in an already-open address block and ends mid-way through the `BIFPLR1_1` margining lane definitions. The merge lane must preserve cross-chunk continuity rather than treating these as independent complete blocks.
- All base indices are `5` here, but similar names in nearby NBIO versions can use different base indices or numeric offsets. Accidental include/version drift can compile cleanly while targeting the wrong MMIO address.
- Several names intentionally alias the same offset, such as capability/control pairs, per-lane grouped equalization registers, PF/VF duplicate aliases, and status/control pairs sharing DWORDs. Automated de-duplication would be unsafe because the aliases document different field views of the same register.
- PCIe logical-root-port groups `BIFPLR0_1` and `BIFPLR1_1` are large and repetitive. Copy/paste or generation errors in lane numbering, offset progression, or base index would affect link training, AER/DPC reporting, margining, and power-management behavior.
- RAS and poison registers are error-handling critical. Wrong offsets could mask, misclassify, or fail to clear hardware errors, leading to missed fatal events or noisy false positives.
- Doorbell and GPUIOV registers affect queue notification and virtualization isolation. Wrong offsets can break PF/VF separation, mailbox communication, or doorbell routing.
- Some address-block comments have no visible register definitions in this exact chunk. That is expected for generated files but matters for documentation synthesis so empty markers are not overinterpreted as implemented control paths.

## Test And Validation Signals

- Build coverage: compiling AMDGPU with NBIO 7.2.0 support verifies that all referenced symbols from this header resolve and that include ordering is intact.
- Static consistency checks: generated offset validation should confirm every `reg*` symbol has a matching `reg*_BASE_IDX`, every base index in this span is expected to be `5`, and aliased offsets are intentional rather than accidental duplicates.
- Runtime smoke tests on matching ASICs: driver probe, suspend/resume, BACO entry/exit, reset handling, and display bring-up exercise many NBIO register paths.
- Doorbell tests: SDMA/IH/VCN/RLC queue operation, interrupt delivery, and VF/PF mailbox paths exercise GDC/BIF/RCC doorbell and mailbox registers.
- Error-path tests: PCIe AER/DPC injection, poison propagation, parity/RAS event handling, and NMI/sync-flood reporting validate that status, mask, severity, and action-control offsets match hardware.
- PCIe link tests: link speed negotiation, L1 PM substates, 16 GT status, lane equalization, and margining diagnostics are useful signals for the `BIFPLR0_1` and `BIFPLR1_1` register groups.
- Cross-version regression checks: compare generated values for shared symbol families across NBIO 7.2.0, 7.7.0, 7.9.0, and 7.11.0 to catch accidental use of another ASIC generation's offsets.

## Notes For Merge/Reconciliation

- This is chunk 9 of 14 for `nbio_7_2_0_offset.h`.
- The chunk begins at line 19462 with `SCRATCH_4` and `SCRATCH_5`, continuing a block whose address-block comment appears in the previous chunk.
- The chunk ends at line 21877 before the `BIFPLR1_1` PCIe margining lane table is complete; chunk 10 should continue with lane 1 status and subsequent lane margining definitions.
- No final per-file report should be produced from this chunk alone. The later merge lane should synthesize the whole `nbio_7_2_0_offset.h` report from all 14 chunk reports.
