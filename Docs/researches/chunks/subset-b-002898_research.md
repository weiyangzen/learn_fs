# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 1-2466

## Scope

This chunk covers the opening 2,466 lines of the generated AMD NBIO 2.3 register-offset header. It begins with the license and include guard, then defines NBIO/NBIF/BIF/RCC/GDC/PCIe configuration-space offsets for Navi-era AMDGPU hardware. The range contains 2,356 preprocessor definitions: 2,041 register or PCI config symbols and 315 matching `_BASE_IDX` selector helpers.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or executable MMIO operations. Its public interface is a set of generated constants:

- `mm...` symbols name MMIO-style NBIO/NBIF registers consumed through SOC15 register helpers.
- `cfg...` symbols name PCI configuration-space offsets for endpoint, switch downstream-port, and virtual-function config blocks.
- `<symbol>_BASE_IDX` selects the register-base table entry used by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and related AMDGPU helpers.

## Purpose

`nbio_2_3_offset.h` is the address side of the NBIO 2.3 hardware ABI. Companion files such as `nbio_2_3_sh_mask.h` provide bit shifts and masks, while `nbio_2_3_default.h` provides reset/default values. Runtime AMDGPU code combines these generated offsets with helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD` to read or program PCIe/NBIO hardware.

In this source tree, direct consumers include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, and display resource code for DCN generations. The constants in this first chunk are especially tied to memory-controller access enablement, revision and strap reads, doorbell aperture setup, HDP flush remapping, interrupt setup, SR-IOV mailbox traffic, PCIe link capabilities, and PCI config-space capability discovery.

## Important Macro Families

### Header and Indirect Index Registers

The first block defines `mmBIF_BX_PF_MM_INDEX`, `mmBIF_BX_PF_MM_DATA`, and `mmBIF_BX_PF_MM_INDEX_HI` for the PF system/PF-VF decode path. These are the classic indirect MMIO index/data window registers. The chunk also defines system-hub and PCIe indirect access windows such as `mmSYSHUB_INDEX_OVLP`, `mmSYSHUB_DATA_OVLP`, `mmPCIE_INDEX`, `mmPCIE_DATA`, `mmPCIE_INDEX2`, `mmPCIE_DATA2`, plus the non-overlap `mmSYSHUB_INDEX` and `mmSYSHUB_DATA` pair.

These registers are integration points for code that must reach internal NBIO/PCIe registers through an indexed aperture rather than direct MMIO addresses.

### BIOS Scratch, Interrupt, and MMIO CAM Registers

The `SYSDEC` area exposes `mmSBIOS_SCRATCH_0..3` and `mmBIOS_SCRATCH_0..15`, which are firmware/driver scratch registers. It also defines interrupt-control registers for RLC, VCE, and UVD via `mmBIF_RLC_INTR_CNTL`, `mmBIF_VCE_INTR_CNTL`, and `mmBIF_UVD_INTR_CNTL`.

The `mmGFX_MMIOREG_CAM_ADDR0..7`, `mmGFX_MMIOREG_CAM_REMAP_ADDR0..7`, `mmGFX_MMIOREG_CAM_CNTL`, and completion-value registers describe a GFX MMIO remap/CAM facility. These offsets are persistent hardware configuration surfaces; incorrect programming can remap GPU register access unexpectedly.

### RCC Strap and Endpoint/Downstream Port Controls

The `nbio_nbif0_rcc_strap_BIFDEC1` block defines BIF, device-port, and endpoint-function strap registers including `mmRCC_BIF_STRAP0..6`, `mmRCC_DEV0_PORT_STRAP0..9`, and endpoint-function strap groups for EPF0, EPF1, EPF2, and EPF3. Active code reads `mmRCC_BIF_STRAP0` in power-management paths to infer platform/link properties, and `nbio_v2_3_get_rev_id()` reads `mmRCC_DEV0_EPF0_STRAP0` unless running as an SR-IOV VF.

The endpoint and downstream blocks add PCIe endpoint/downstream link controls such as `mmEP_PCIE_*`, `mmDN_PCIE_*`, `mmPCIE_ERR_CNTL`, `mmPCIE_RX_CNTL`, `mmPCIE_LC_SPEED_CNTL`, `mmPCIE_LC_CNTL2`, `mmPCIEP_STRAP_MISC`, and `mmLTR_MSG_INFO_FROM_EP`. These register families feed PCIe link training, error control, latency tolerance reporting, straps, and bus/config behavior.

### RCC PF/VF, Memory Size, Peer, Bus, and BACO Control

The PF/VF RCC section includes `mmRCC_DEV0_EPF0_RCC_ERR_LOG`, `mmRCC_DEV0_EPF0_RCC_DOORBELL_APER_EN`, `mmRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`, `mmRCC_DEV0_EPF0_RCC_CONFIG_RESERVED`, and `mmRCC_DEV0_EPF0_RCC_IOV_FUNC_IDENTIFIER`. `nbio_v2_3.c` uses these offsets to enable the doorbell aperture and report configured memory size.

The broader `mmRCC_*` group includes reset, VDM, margining, GPUIOV region, peer register ranges, bus/config aperture size, XDMA addresses, host-bus capture, peer FB offsets, device/function lists, link controls, requester-ID restore, LTR local-switch control, and multi-host arbitration. These registers represent topology, virtualization, peer-to-peer, reset, and bus-number state.

### BIF Core, Doorbells, HDP Flush, Ring Buffer, and Interrupts

The `nbio_nbif0_bif_bx_BIFDEC1` and PF BIF blocks provide many of the offsets most visible to AMDGPU runtime code:

- `mmBIF_MM_INDACCESS_CNTL`, `mmBUS_CNTL`, `mmMM_CFGREGS_CNTL`, `mmBX_RESET_EN`, and `mmBX_RESET_CNTL` cover BIF access and reset controls.
- `mmINTERRUPT_CNTL` and `mmINTERRUPT_CNTL2` are programmed by `nbio_v2_3_ih_control()` for interrupt-hub behavior and dummy-page addressing.
- `mmBIF_FB_EN` is used by `nbio_v2_3_mc_access_enable()` to enable or disable framebuffer read/write access.
- `mmBIF_INTR_CNTL`, `mmBIF_MST_TRANS_PENDING_VF`, `mmBIF_SLV_TRANS_PENDING_VF`, and `mmBIF_BX_PF_BIF_TRANS_PENDING` expose interrupt and transaction-pending state.
- `mmBACO_CNTL` and `mmBIF_BACO_EXIT_TIME0/TIMER1..4` support BACO low-power entry/exit timing.
- `mmNBIF_GFX_ADDR_LUT_CNTL`, `mmNBIF_GFX_ADDR_LUT_0..15`, and `mmBIF_BX_PF_NBIF_GFX_ADDR_LUT_BYPASS` define graphics-address lookup controls.
- `mmREMAP_HDP_MEM_FLUSH_CNTL` and `mmREMAP_HDP_REG_FLUSH_CNTL` are written by `nbio_v2_3_remap_hdp_registers()` to remap KFD HDP flush registers.
- `mmBIF_RB_CNTL`, `mmBIF_RB_BASE`, `mmBIF_RB_RPTR`, `mmBIF_RB_WPTR`, and write-pointer address registers describe a BIF ring-buffer interface.
- `mmBIF_SDMA0_DOORBELL_RANGE`, `mmBIF_SDMA1_DOORBELL_RANGE`, `mmBIF_IH_DOORBELL_RANGE`, `mmBIF_MMSCH0_DOORBELL_RANGE`, and `mmBIF_ACV_DOORBELL_RANGE` configure hardware doorbell windows. `nbio_v2_3.c` uses these to assign SDMA, interrupt-handler, and multimedia scheduler doorbell ranges.
- `mmBIF_BX_PF_DOORBELL_SELFRING_GPA_APER_BASE_HIGH/LOW/CNTL` set the self-ring doorbell aperture base and mode.
- `mmBIF_BX_PF_GPU_HDP_FLUSH_REQ` and `mmBIF_BX_PF_GPU_HDP_FLUSH_DONE` provide flush request/done signaling.
- `mmBIF_BX_PF_MAILBOX_MSGBUF_TRN_DW0..3`, `mmBIF_BX_PF_MAILBOX_MSGBUF_RCV_DW0..3`, `mmBIF_BX_PF_MAILBOX_CONTROL`, `mmBIF_BX_PF_MAILBOX_INT_CNTL`, and `mmBIF_BX_PF_BIF_VMHV_MAILBOX` back SR-IOV PF/VF mailbox communication; `mxgpu_nv.c` uses the equivalent mailbox names for host/VF message exchange.

### GDC/A2S/S2A and NBIO Power Management

The GDC block includes A2S/S2A controls (`mmA2S_CNTL_*`, `mmA2S_CNTL3_*`, `mmA2S_CNTL_SW*`, `mmS2A_MISC_CNTL`), completion-buffer and tag allocation (`mmA2S_CPLBUF_ALLOC_CNTL`, `mmA2S_TAG_ALLOC_0/1`), SDP port controls, `mmSHUB_REGS_IF_CTL`, NBIO GDC clock-gating `mmNGDC_MGCG_CTRL`, and power-gating controls `mmNGDC_PG_MISC_CTRL`, `mmNGDC_PGMST_CTRL`, and `mmNGDC_PGSLV_CTRL`.

These constants are part of the path between the host interface, system hub, and internal fabric. They are power/performance sensitive and should be treated as ASIC-specific register ABI rather than generic PCIe configuration.

### MSI-X Vector Table Offsets

The `nbio_nbif0_rcc_dev0_epf0_BIFDEC2` section starts a GFX MSI-X table for EPF0, defining vector 0 through vector 8 address-low, address-high, message-data, and control offsets. This is hardware interrupt delivery state. The offset series follows the standard four-dword pattern per vector, but it is still ASIC-generated and must match the NBIO register map.

### PCIe Switch/Port Config Space

The `cfgPSWUSCFG0_0_*` group models a PCIe switch upstream config block. It includes standard config header fields, power-management and PCIe capability registers, MSI registers, vendor-specific capabilities, virtual-channel capability registers, device serial number, advanced error reporting, BAR capability controls, power budget/DPA controls, secondary PCIe capability, ACS, multicast, LTR, ARI, L1 PM substates, ESM/CCIX fields, data-link feature capability, 16 GT/s PHY/link/equalization fields, lane margining fields for lanes 0-15, and CCIX/ESM equalization controls at 20 GT/s and 25 GT/s.

These `cfg...` constants are byte offsets within PCI config space, not SOC15 MMIO offsets with `_BASE_IDX` entries.

### Endpoint Function Config Blocks

The chunk defines large PCI config-space layouts for device 0 endpoint functions:

- `cfgBIF_CFG_DEV0_EPF0_0_*` covers EPF0, including standard PCI header, PM/PCIe/MSI/MSI-X capabilities, vendor-specific and virtual-channel capabilities, serial number, AER logs, BAR capabilities, power budget and DPA controls, secondary PCIe, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s link/equalization, lane margining, CCIX, and GPUIOV vendor-specific capability fields.
- `cfgBIF_CFG_DEV0_EPF1_0_*` mirrors much of EPF0 and adds a large GPUIOV capability region with VF framebuffer partition offsets (`VF0_FB` through `VF30_FB`) and scheduler/mailbox dwords for UVD, VCE, GFX, and UVD1.
- `cfgBIF_CFG_DEV0_EPF2_0_*` is shorter in this range but includes standard endpoint config, MSI/MSI-X, AER, BAR/power/DPA controls, ACS/PASID/ARI, TPH requester controls, and the full `PCIE_TPH_ST_TABLE_0..63`.
- `cfgBIF_CFG_DEV0_EPF3_0_*` includes endpoint config plus SATA-specific fields (`SBRN`, `FLADJ`, `DBESL_DBESLD`, `SATA_CAP_*`, `SATA_IDP_INDEX`, `SATA_IDP_DATA`) and TPH steering-table offsets through `PCIE_TPH_ST_TABLE_63`.

The repetition is intentional: each endpoint function gets its own generated namespace even when standard capability offsets match.

### Switch Downstream Port and VF Config Blocks

`cfgBIF_CFG_DEV0_SWDS0_*` defines a switch downstream-port config layout, including bridge header fields, secondary/subordinate bus windows, IO/memory/prefetchable limits, slot capability/control/status fields, MSI, subsystem-ID capability, vendor-specific capability, virtual-channel capability, AER, secondary PCIe, ACS, and 16 GT/s/equalization registers.

The chunk then starts `cfgBIF_CFG_DEV0_EPF0_VF0_0_*`, `VF1_0_*`, and `VF2_0_*` config blocks for SR-IOV virtual functions of EPF0. The covered VF blocks include standard endpoint header fields, PCIe capabilities, MSI/MSI-X, vendor-specific capability, AER, ATS, and ARI. The range ends while still inside the VF2 block at `cfgBIF_CFG_DEV0_EPF0_VF2_0_PCIE_HDR_LOG0`; later VF2 fields and further VF blocks continue in later chunks.

## Control Flow and State Behavior

There is no executable control flow in this header. All behavior is compile-time symbol substitution: C files include the header, pass a generated symbol to a register helper, and the helper combines the offset with an IP block/base-instance mapping.

The state represented by this chunk lives in hardware and firmware-visible registers. Some families are durable configuration while the GPU is powered, such as doorbell aperture bases, FB access enablement, PCIe config capabilities, BAR controls, SR-IOV resource configuration, peer address ranges, host-bus numbers, GPUIOV region assignments, and address-LUT setup. Other families are status, handshake, or command-like state, such as transaction-pending bits, mailbox valid/ack/data registers, HDP flush request/done registers, interrupt controls, AER/error logs, MSI/MSI-X vector entries, and scratch registers.

Correct sequencing is not encoded in the header. For example, `mxgpu_nv.c` clears mailbox valid, waits for ACK deassertion, writes transmit dwords, sets valid, polls for ACK, then clears valid again. `nbio_v2_3.c` writes doorbell base registers before enabling the self-ring aperture. Those ordering rules come from owning driver code and hardware specifications, not from the generated offsets.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 header set:

- `nbio_2_3_sh_mask.h` gives bitfield names used with these offsets.
- `nbio_2_3_default.h` gives default/reset values for matching registers.
- `soc15.h` and AMDGPU register helpers interpret `_BASE_IDX` and `mm...` symbols.
- PCI and DRM/AMDGPU code consume `cfg...` symbols as configuration-space offsets where applicable.

Observed integration in this source tree includes:

- `amdgpu/nbio_v2_3.c` includes the offset, default, and shift/mask headers and uses this chunk's offsets for HDP remap, revision strap reads, framebuffer access enablement, memory-size reads, doorbell aperture setup, interrupt setup, and doorbell range programming.
- `amdgpu/mxgpu_nv.c` includes the offset and shift/mask headers and uses mailbox offsets for SR-IOV VF/PF message passing.
- SMU 11 power-management files include this header and read `mmRCC_BIF_STRAP0` for platform/link-state decisions.
- Display resource files include NBIO 2.3 offsets so generated register lists can reference the correct NBIO register names for DCN hardware.

## Risks

- Register-offset drift is high impact. A wrong `mm...` value or `_BASE_IDX` can redirect `RREG32_SOC15`/`WREG32_SOC15` to the wrong NBIO register, causing hangs, incorrect PCIe setup, broken interrupts, mailbox failure, or invalid memory access policy.
- `cfg...` offsets are byte-oriented PCI config offsets, while `mm...` offsets are SOC15 register offsets. Mixing the two access models would target the wrong address space.
- Doorbell registers are security and isolation sensitive. Incorrect aperture base, range, or size programming can expose queues across engines or SR-IOV functions.
- SR-IOV mailbox offsets are synchronization sensitive. Changing message-buffer or control offsets can break host/VF handshakes and timeout recovery paths.
- Strap and config-read registers may not be valid in every execution mode. `nbio_v2_3_get_rev_id()` explicitly avoids reading `mmRCC_DEV0_EPF0_STRAP0` for SR-IOV VFs because the guest can receive `0xffffffff`.
- Interrupt and MSI/MSI-X offsets are boot/runtime critical. Corrupt vector, dummy-read, or interrupt-control programming can drop interrupts or generate spurious interrupts.
- PCIe capability offsets repeat across EPF0-EPF3, switch downstream, and VF blocks. Mechanical edits can silently update one function namespace but not the others.
- Many config blocks include advanced PCIe features such as ATS, PASID, PRI/page request, ARI, ACS, SR-IOV, TPH, LTR, AER, DPA, L1 PM substates, and high-speed equalization/margining. Wrong offsets can disable isolation, degrade link stability, or misreport error state.
- The chunk boundary is mid-VF2 config block, so a final file-level report must merge later chunks before making complete claims about EPF0 VF coverage.

## Test and Validation Signals

Useful validation is primarily build, bring-up, and hardware integration coverage:

- Build AMDGPU, display, and SMU paths that include `nbio/nbio_2_3_offset.h`; this catches missing or renamed generated symbols.
- Exercise `nbio_v2_3.c` initialization paths: framebuffer access enable/disable, memory-size query, HDP flush remap, interrupt setup, and doorbell range programming for SDMA, IH, and multimedia scheduler engines.
- Run SR-IOV VF/PF mailbox tests that send requests, receive events, poll ACK/valid bits, and handle timeout/unrecoverable notifications.
- Validate doorbell isolation under bare-metal and SR-IOV configurations by checking that each engine and VF receives only its assigned range.
- Run PCIe link and power-management tests that cover strap reads, link speed/width, LTR, DPA/power budget, L1 substates, and BACO entry/exit paths.
- Confirm PCI config-space enumeration exposes expected vendor/device IDs, BARs, MSI/MSI-X, AER, ACS/ATS/PASID/ARI/SR-IOV, TPH, and data-link/16 GT/s capabilities for EPF and VF functions.
- Test interrupt delivery and recovery, including MSI/MSI-X vector programming and dummy-read behavior configured through `mmINTERRUPT_CNTL*`.
- Use AER/error-injection or link-error tests where available to verify that config-space AER status/log offsets match the hardware-reported errors.

## Unresolved Cross-Chunk References

This is the first chunk of a 14,663-line generated header. Later chunks continue the EPF0 VF2 config block, additional VFs/functions, and remaining NBIO 2.3 register-offset families. The final per-file reconciliation should treat this document as covering only lines 1-2466 and should stitch the incomplete VF2 block with the next chunk before summarizing full VF coverage.
