# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 17882-18521

## Scope

This chunk is the final slice of AMD's generated NBIO 2.3 default-register header. It contains 604 preprocessor constants and the closing `#endif`; there are no C functions, structs, enums, variables, includes, locks, allocations, or direct MMIO reads/writes in this range.

The covered lines begin in the tail of the `nbio_nbif0_bif_cfg_dev0_epf0_vf27_bifcfgdecp` block, define the full default PCIe configuration spaces for VFs 28, 29, and 30, then cover default values for shadow config registers, BIF/SYSHUB windows, RCC straps and endpoint/downstream PCIe blocks, RCC and BIF core control blocks, PF mailbox and doorbell registers, GDC doorbell/power-gating registers, and four GFX MSI-X vector-table defaults.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU/NBIO hardware metadata, not distributed filesystem code.

## Purpose

`nbio_2_3_default.h` publishes reset/default values for NBIO 2.3 registers. The companion `nbio_2_3_offset.h` provides the matching register addresses, and `nbio_2_3_sh_mask.h` provides field masks and shifts for code that needs to compose or decode register values.

This exact chunk describes default state for several integration surfaces:

- SR-IOV VF PCIe config defaults for `cfgBIF_CFG_DEV0_EPF0_VF28_1_*`, `VF29_1_*`, and `VF30_1_*`, plus the ending AER/ATS/ARI defaults for `VF27_1`.
- Host-visible config shadow and system access portals, including `cfgSHADOW_*`, `cfgSUC_*`, `cfgBIF_BX_PF1_MM_*`, `cfgPCIE_INDEX*`, `cfgPCIE_DATA*`, BIOS/SBIOS scratch registers, and GFX MMIO register CAM defaults.
- RCC strap and endpoint defaults that seed PCIe link identity, requestor behavior, dynamic power allocation, LTR, PME, error-control, and lane-speed-related state.
- Core RCC/BIF defaults for reset enables, peer ranges, host bus-number capture, peer framebuffer offsets, HDP coherency flush remaps, BACO exit timers, NBIF GFX address LUT entries, BIF ring registers, interrupts, pad controls, and GPU IOV config sizes.
- PF-only doorbell, HDP flush, transaction-pending, mailbox, and VM/HV mailbox defaults used by bare-metal and SR-IOV paths.
- GDC defaults for A2S/S2A control, SDP ports, clock/power gating, doorbell ranges for SDMA/IH/MMSCH/ACV, and doorbell fencing.
- RCC GFX MSI-X vector-table defaults for four vectors plus the PBA register, with vector control defaults set to `0x00000001`.

The generated constants are compile-time data. They do not enforce reset sequencing or access permissions; the owning AMDGPU code and hardware specification determine when these defaults are used as reset baselines, comparison values, or documentation of hardware reset state.

## Important Macros And Register Groups

The public interface is the generated `<register>_DEFAULT` macro namespace. Important groups in this range are:

- `cfgBIF_CFG_DEV0_EPF0_VF27_1_PCIE_*_DEFAULT`: final VF27 PCIe vendor-specific, AER, header-log, TLP-prefix-log, ATS, and ARI defaults at the chunk boundary.
- `cfgBIF_CFG_DEV0_EPF0_VF28_1_*_DEFAULT`, `cfgBIF_CFG_DEV0_EPF0_VF29_1_*_DEFAULT`, and `cfgBIF_CFG_DEV0_EPF0_VF30_1_*_DEFAULT`: complete repeated VF PCIe config-space default sets. Each includes vendor/device/class/header/BAR/capability-pointer defaults, PCIe capability defaults, link capability defaults (`LINK_CAP_DEFAULT` `0x00000d04`, `LINK_CAP2_DEFAULT` `0x0000001e`), MSI defaults (`MSI_MSG_CNTL_DEFAULT` `0x00000082`), empty MSI-X capability defaults, AER defaults, ATS enhanced capability list default `0x2c000000`, and empty ARI defaults. The adapter ID default is `0x73101002`.
- `cfgSHADOW_*_DEFAULT` and `cfgSUC_*_DEFAULT`: bridge/config shadow and sideband/user-config access defaults, all zero in this chunk.
- `cfgBIF_BX_PF1_MM_INDEX_DEFAULT`, `cfgBIF_BX_PF1_MM_DATA_DEFAULT`, and `cfgBIF_BX_PF1_MM_INDEX_HI_DEFAULT`: PF1 indirect MMIO access defaults.
- `cfgSYSHUB_*`, `cfgPCIE_INDEX*`, `cfgPCIE_DATA*`, `cfgSBIOS_SCRATCH_*`, `cfgBIOS_SCRATCH_*`, `cfgBIF_*_INTR_CNTL`, and `cfgGFX_MMIOREG_CAM_*`: system hub, PCIe indirect access, scratch, interrupt, and MMIO remap/CAM defaults.
- `cfgRCC_BIF_STRAP*`, `cfgRCC_DEV0_PORT_STRAP*`, and `cfgRCC_DEV0_EPF[01]_STRAP*`: RCC strap defaults that encode device/port/function identity and link capabilities. These are nonzero and topology-sensitive.
- `cfgEP_PCIE_*` and `cfgPCIE_F[01]_DPA_*`: endpoint PCIe defaults for scratch/control, bus control, LTR transmit control, dynamic power allocation capability/latency/control, DPA substate power allocations, PME, error control, RX control, and link-speed control.
- `cfgDN_PCIE_*` and `cfgPCIE_*` downstream/downstream-port defaults: downstream-side control, config, strap, error, RX, link-speed, link-control, and LTR-message defaults.
- `cfgRCC_DEV0_EPF0_RCC_*`: PF/VF decode defaults for RCC error logging, doorbell aperture enablement, memory-size configuration, reserved config, and IOV function identifier.
- `cfgRCC_*`: RCC core defaults for BACO, reset, margining parameters, peer register ranges, bus/config aperture, XDMA address, bus-number lists, peer framebuffer offsets, device/function lists, link controls, LTR low-switch control, and MH arbitration.
- `cfgBIF_*`, `cfgBX_*`, `cfgINTERRUPT_*`, `cfgBACO_*`, `cfgNBIF_GFX_ADDR_LUT_*`, and pad-control defaults: BIF core control, reset, interrupt, FB enable, pending-transaction, BACO timing, address LUT, HDP flush remap, ring buffer, MP1 interrupt, GPU IOV config-size, and physical pad defaults.
- `cfgBIF_BX_PF_*`: PF-only BIF status, atomic error log, self-ring doorbell GPA aperture, HDP coherency flush, GPU HDP flush request/done, transaction pending, LUT bypass, PF mailbox message buffers, mailbox control/interrupt, and VM/HV mailbox defaults.
- `cfgA2S_*`, `cfgNGDC_*`, `cfgBIF_*_DOORBELL_RANGE`, `cfgBIF_DOORBELL_FENCE_CNTL`, and `cfgS2A_MISC_CNTL`: GDC bridge, SDP, clock/power-gating, and engine doorbell range defaults.
- `cfgRCC_DEV0_EPF0_GFXMSIX_VECT[0-3]_*` and `cfgRCC_DEV0_EPF0_GFXMSIX_PBA_DEFAULT`: MSI-X table/PBA defaults for the graphics function. Address and data defaults are zero; each vector control default is `0x00000001`, which conventionally corresponds to a masked vector.

## Control Flow

There is no executable control flow in this header. Runtime behavior comes from consumers that include the generated NBIO 2.3 headers:

1. AMDGPU NBIO 2.3 code includes this file with `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h`.
2. Register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `REG_SET_FIELD`, and `SOC15_REG_OFFSET` use the offset and shift/mask headers to access actual hardware registers.
3. Default macros can be used as reset baselines, initial values, or generated metadata for bring-up and diagnostics. In this source tree, `amdgpu/nbio_v2_3.c` is the direct include site for `nbio_2_3_default.h`; it programs related NBIO surfaces such as HDP flush remaps, framebuffer access, SDMA/VCN/IH doorbell ranges, doorbell apertures, interrupt control, clock gating, and PCIe state.
4. SR-IOV paths such as `amdgpu/mxgpu_nv.c` use the matching NBIO offset and shift/mask headers for PF/VF mailbox message buffers and mailbox control registers whose defaults are listed in this chunk.
5. Power-management paths for Navi10/Sienna Cichlid include the NBIO 2.3 offset and shift/mask headers when integrating PCIe/link/power behavior with SMU policy.

The defaults do not encode the order for reset, SR-IOV handshakes, mailbox ACK/valid transitions, HDP flush polling, doorbell aperture setup, BACO exit, power-gating, or MSI-X programming. Those rules live in the driver code and hardware documentation.

## State And Persistence Behavior

This chunk stores no software state. It describes hardware reset/default state for NBIO 2.3 registers.

State represented here includes:

- VF PCIe configuration space defaults for identity, BARs, PCIe capabilities, MSI/MSI-X capability tables, AER status/mask/severity/log registers, ATS, and ARI.
- Shadow config and system-hub portal defaults used to access or mirror configuration registers.
- BIOS/SBIOS scratch and GFX MMIO remap/CAM defaults, which can be used by firmware, boot, or driver handoff paths.
- Strap-derived state for device/function identity, revision/device IDs, link capability, and endpoint behavior.
- Endpoint and downstream PCIe control state for LTR, DPA, PME, error control, RX control, link speed, and bus/config controls.
- RCC/BIF state for memory sizing, doorbell aperture enablement, peer access, host bus numbering, XDMA addresses, link control, reset enables, BACO exit timing, framebuffer access, pending transactions, and HDP flush remap addresses.
- PF/VF mailbox message buffer and control defaults used by SR-IOV virtualization protocol paths.
- Doorbell range defaults for SDMA, IH, MMSCH, and ACV engines, plus self-ring doorbell aperture defaults.
- GDC bridge and power/clock gating defaults.
- MSI-X vector table defaults for graphics interrupt delivery.

Persistence is hardware-defined. Configuration defaults are reset baselines and may be overwritten by firmware, PCI enumeration, SR-IOV setup, AMDGPU initialization, runtime power management, suspend/resume restore, BACO transitions, GPU reset, or guest/host virtualization flows. Status and log registers may be read-only, sticky, write-one-to-clear, self-clearing, or undefined while their clock/power domains are gated; this default header does not describe those access semantics.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 header set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` supplies the matching addresses for every register named here. For example, `cfgBIF_CFG_DEV0_EPF0_VF28_1_*` starts at base address `0xfffe1031c000`, the RCC/BIF/GDC groups sit under `0x30300000`, and GFX MSI-X vector registers start at `0x30342000`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h` supplies bitfield layouts used to modify the same registers safely.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` directly includes this default header and uses the sibling headers for NBIO operations such as HDP remapping, memory-controller access gating, doorbell ranges, doorbell self-ring aperture programming, interrupt setup, clock gating, PCIe link handling, and revision/memsize reads.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` integrates with PF/VF mailbox registers from the same NBIO 2.3 register map for SR-IOV host/guest messaging.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include NBIO 2.3 offset and shift/mask headers for SMU/PCIe link and power-management integration.
- Display resource files include the NBIO 2.3 offset header where display code needs SOC15 register addresses for NBIO-adjacent resources.

The most important integration surfaces from this chunk are PCIe enumeration and capabilities, SR-IOV VF config spaces, doorbell aperture/range setup, PF/VF mailbox protocol, HDP flush/coherency plumbing, BACO/reset/power transitions, and graphics MSI-X interrupt delivery.

## Risks And Edge Cases

- Generated default drift can be subtle. A wrong `_DEFAULT` value can compile cleanly while misleading reset comparison logic, documentation, or bring-up assumptions.
- The VF PCIe config blocks are highly repetitive. A single VF instance can diverge from neighboring VFs without obvious compile-time failures, causing one SR-IOV virtual function to expose different capabilities, AER defaults, MSI capability defaults, ATS pointers, or BAR/reset behavior.
- The chunk starts mid-block for VF27 and ends at the file footer. Whole-file reconciliation must merge the previous chunk before treating the VF27 PCIe config block as complete.
- PCIe capability list and enhanced capability pointer defaults are topology-sensitive. Incorrect values such as `CAP_PTR`, PCIe capability headers, AER capability list entries, or ATS/ARI entries can break host PCI enumeration or hide capabilities from guest VFs.
- MSI/MSI-X defaults are interrupt-sensitive. Incorrect MSI message-control defaults or MSI-X vector-control defaults can cause masked interrupts, unexpected interrupt enablement, or host/guest interrupt routing failures.
- Strap and reset-enable defaults are silicon- and board-sensitive. Hand-editing `cfgRCC_*_STRAP*`, `cfgRCC_RESET_EN_DEFAULT`, or `cfgBX_RESET_EN_DEFAULT` risks mismatching firmware straps, ASIC revisions, and board wiring.
- Doorbell range and self-ring aperture defaults interact with engine submission paths. Wrong range defaults, size fields, or aperture defaults can make SDMA/IH/VCN/MMSCH/ACV doorbells inaccessible or overlap another engine's doorbell window.
- PF/VF mailbox registers are protocol-sensitive. Incorrect defaults or offsets around message buffers, valid/ACK control, and mailbox interrupts can lead to SR-IOV timeouts or failed host/guest state transitions.
- HDP flush and coherency defaults are ordering-sensitive. Bad flush remap defaults or coherency defaults can produce stale CPU/GPU memory visibility, especially around KFD, VM, and interrupt handling.
- BACO, power-gating, clock-gating, and pad-control defaults can affect low-power transitions and resume reliability. Values that work at cold boot may still be wrong across BACO exit, suspend/resume, or GPU reset.
- Default headers do not carry read/write semantics. Some named registers are status, clear, sticky, strap, reserved, or firmware-owned; software should not infer writability from the presence of a `_DEFAULT` macro.

## Test Signals

Useful validation combines generated-header checks with hardware and driver behavior:

- Build AMDGPU with NBIO 2.3 support enabled. Missing or renamed macros should be caught by `amdgpu/nbio_v2_3.c` and related users of the sibling offset/shift-mask headers.
- Mechanically compare this range against the authoritative AMD NBIO 2.3 register database and against `nbio_2_3_offset.h` to confirm that every `_DEFAULT` macro has a matching offset macro where expected.
- Run PCI enumeration checks on Navi10-family NBIO 2.3 hardware and SR-IOV VFs, verifying VF28-VF30 capability list layout, MSI/MSI-X visibility, AER/ATS/ARI capability presence, BAR defaults, and class/device identity.
- Exercise SR-IOV mailbox flows in `mxgpu_nv.c`: guest init/fini/reset access requests, mailbox ACK/valid polling, RAS request/response paths, timeout handling, and unrecoverable-state notification.
- Validate doorbell setup for SDMA, IH, VCN/MMSCH, and ACV paths by checking ring submission, interrupt delivery, and no overlap in allocated doorbell ranges.
- Validate HDP flush and coherency behavior through KFD/AMDGPU memory-visibility tests, especially after remapping `REMAP_HDP_MEM_FLUSH_CNTL` and `REMAP_HDP_REG_FLUSH_CNTL`.
- Test BACO, suspend/resume, GPU reset, PCIe link retraining, and clock/power-gating transitions while watching for link errors, mailbox timeouts, stuck pending-transaction bits, and lost interrupts.
- Confirm MSI/MSI-X behavior by checking interrupt allocation, vector masking/unmasking, graphics interrupt delivery, and PBA behavior on bare metal and under virtualization.
- Monitor kernel logs for AER reports, PCI config-space read failures, SR-IOV VF access failures, doorbell faults, HDP flush timeouts, BACO exit failures, and resume-only PCIe/link regressions.

## Cross-Chunk Notes

Lines 17882-17903 are only the tail of the VF27 PCIe config default block; earlier VF27 identity, BAR, link, and MSI defaults are in the previous chunk. Lines 18502-18519 complete the final generated register block, and line 18521 closes the header guard. The merge lane should stitch this final chunk with the preceding chunks before making file-level claims about all NBIO 2.3 default registers or all SR-IOV VF instances.
