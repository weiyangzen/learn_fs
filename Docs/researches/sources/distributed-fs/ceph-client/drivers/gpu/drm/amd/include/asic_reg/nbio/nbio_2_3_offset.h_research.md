# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002898`: lines 1-2466, `Docs/researches/chunks/subset-b-002898_research.md`
- `subset-b-002899`: lines 2467-4944, `Docs/researches/chunks/subset-b-002899_research.md`
- `subset-b-002900`: lines 4945-7706, `Docs/researches/chunks/subset-b-002900_research.md`
- `subset-b-002901`: lines 7707-10473, `Docs/researches/chunks/subset-b-002901_research.md`
- `subset-b-002902`: lines 10474-12730, `Docs/researches/chunks/subset-b-002902_research.md`
- `subset-b-002903`: lines 12731-14663, `Docs/researches/chunks/subset-b-002903_research.md`

## Chunk Research

### subset-b-002898: lines 1-2466

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

### subset-b-002899: lines 2467-4944

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 2467-4944

## Scope

This chunk covers a generated NBIO 2.3 register-offset header slice. It starts in the tail of the `nbio_nbif0_bif_cfg_dev0_epf0_vf2_bifcfgdecp` address block, covering VF2 PCIe AER log, ATS, and ARI config-space offsets, then contains the complete PCI configuration-space offset maps for `DEV0_EPF0` virtual functions VF3 through VF30. The final portion begins the per-VF MMIO/RCC/BIF register maps for VF0 and VF1:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf3_bifcfgdecp` through `vf30_bifcfgdecp`
- `nbio_nbif0_bif_bx_dev0_epf0_vf0_SYSPFVFDEC`
- `nbio_nbif0_rcc_dev0_epf0_vf0_BIFPFVFDEC1`
- `nbio_nbif0_bif_bx_dev0_epf0_vf0_BIFPFVFDEC1`
- `nbio_nbif0_rcc_dev0_epf0_vf0_BIFDEC2`
- the start of the same `SYSPFVFDEC`, `BIFPFVFDEC1`, and BIF register families for VF1

The source is a hardware register map: it defines preprocessor constants only. There are no C functions, structs, variables, dynamic allocation, locks, or executable control flow in this range.

## Purpose

`nbio_2_3_offset.h` provides the numeric register offsets used by AMDGPU NBIO 2.3 code and shared SOC15 register helpers. This chunk specifically describes the SR-IOV virtual-function-facing PCI configuration and BIF/RCC register windows for the NBIO northbridge I/O block.

The `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` macros map PCI/PCIe configuration-space offsets relative to base address `0x0` for virtual functions. These cover standard PCI header fields, PCIe capability fields, MSI/MSI-X capability offsets, vendor-specific extended capability offsets, advanced error reporting offsets, ATS capability offsets, and ARI capability offsets.

The `mmBIF_BX_DEV0_EPF0_VF*_*` and `mmRCC_DEV0_EPF0_VF*_*` macros map memory-mapped NBIO/BIF/RCC registers for virtual functions. Each `mm*` register is accompanied by a `*_BASE_IDX` macro that selects the SOC15 register-base segment used by `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.

## Important Macro Families

### VF PCI Configuration Offsets

The dominant pattern is one repeated config-space map per VF. VF3 through VF30 each define the same offset names and values:

- PCI identity and command/status fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Standard header fields: cache line, latency, header type, BIST, BARs `BASE_ADDR_1` through `BASE_ADDR_6`, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus the second-generation `*_CAP2`, `*_CNTL2`, and `*_STATUS2` fields.
- MSI/MSI-X capability fields: `MSI_CAP_LIST`, message control/address/data/mask/pending offsets, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Extended capability fields: vendor-specific capability at `0x0100`, AER at `0x0150`, TLP header/prefix logs, ATS at `0x02b0`, and ARI at `0x0328`.

The chunk begins just before VF3, with the tail of the VF2 map from `PCIE_UNCORR_ERR_STATUS` through `PCIE_ARI_CNTL`. That means the chunk document must be reconciled with the previous chunk for the full VF2 map.

### VF MMIO Index/Data Apertures

`nbio_nbif0_bif_bx_dev0_epf0_vf0_SYSPFVFDEC` and the start of the VF1 equivalent define:

- `mmBIF_BX_DEV0_EPF0_VF*_MM_INDEX`
- `mmBIF_BX_DEV0_EPF0_VF*_MM_DATA`
- `mmBIF_BX_DEV0_EPF0_VF*_MM_INDEX_HI`

These are indirect index/data apertures for VF-addressed MMIO access. The base index is `0`, distinguishing this decode space from the BIF/RCC register windows later in the chunk.

### VF RCC Configuration and Doorbell Aperture

The `mmRCC_DEV0_EPF0_VF*_RCC_*` families in `BIFPFVFDEC1` provide per-VF RCC offsets:

- `RCC_ERR_LOG`
- `RCC_DOORBELL_APER_EN`
- `RCC_CONFIG_MEMSIZE`
- `RCC_CONFIG_RESERVED`
- `RCC_IOV_FUNC_IDENTIFIER`

These expose virtual-function error logging, doorbell aperture enablement, memory-size reporting, reserved configuration, and SR-IOV function identity. Their `*_BASE_IDX` values are `2`, so callers must route them through the correct NBIO register base.

### VF BIF Doorbell, HDP Flush, Transaction, and Mailbox Registers

The VF0 `nbio_nbif0_bif_bx_dev0_epf0_vf0_BIFPFVFDEC1` block, continued for VF1 at the end of this chunk, includes:

- `BIF_BME_STATUS` and `BIF_ATOMIC_ERR_LOG`
- self-ring doorbell GPA aperture base high/low and control registers
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL`
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE`
- `BIF_TRANS_PENDING`
- `NBIF_GFX_ADDR_LUT_BYPASS`
- transmit and receive mailbox message buffers `MAILBOX_MSGBUF_TRN_DW0..3` and `MAILBOX_MSGBUF_RCV_DW0..3`
- `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`

These registers are the VF-side control surface for host/device coherency flushes, doorbell self-ring setup, outstanding BIF transaction status, and VM/hypervisor mailbox exchange.

### VF0 MSI-X Table Window

`nbio_nbif0_rcc_dev0_epf0_vf0_BIFDEC2` defines a small GFX MSI-X table for VF0:

- `GFXMSIX_VECT0_ADDR_LO/HI`, `MSG_DATA`, and `CONTROL`
- the same four-register layout for vectors 1 through 3
- `GFXMSIX_PBA`

These offsets use base index `3`. They are separate from the PCI config-space `MSIX_TABLE` and `MSIX_PBA` capability offsets; this block maps the actual register-window representation of the MSI-X vector table and pending-bit array.

## Integration Points

`drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this header along with `nbio_2_3_default.h` and `nbio_2_3_sh_mask.h`. Most driver code works through SOC15 helpers that combine a block ID, instance, register offset, and base index into an MMIO address. Examples in that file include `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`.

The most direct consumer in the inspected code is `nbio_v2_3_init_registers()`, which computes `adev->rmmio_remap.reg_offset` from `SOC15_REG_OFFSET(NBIO, 0, mmBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL) << 2` for ASICs that do not use the generic MMIO hole. That value is later used by `nbio_v2_3_remap_hdp_registers()` to program `mmREMAP_HDP_MEM_FLUSH_CNTL` and `mmREMAP_HDP_REG_FLUSH_CNTL`, allowing KFD/user-visible remapped HDP flush offsets to hit the correct NBIO register.

The `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` macros also align with sibling generated defaults in `nbio_2_3_default.h`. The offset header supplies the byte offsets; the default header supplies reset values for the same register names. Bit-level interpretation, where available, lives in `nbio_2_3_sh_mask.h`.

## Control Flow

There is no local control flow in this chunk. Runtime control flow is external:

1. AMDGPU selects NBIO 2.3 support during device bring-up.
2. NBIO helper code includes this generated offset header.
3. Register helper macros resolve `mm*` constants and `*_BASE_IDX` constants into physical MMIO addresses.
4. Driver code reads, writes, or remaps those addresses to configure doorbells, HDP flushes, interrupts, memory-size visibility, PCIe behavior, and virtualization-facing register access.

For PCI config-space macros, the flow is generally indirect through PCIe configuration access or SMN/PCIE index-data paths rather than ordinary C calls inside this header.

## State and Persistence Behavior

The header itself has no persistent state. It names hardware state that persists in the GPU/NBIO registers across driver operations until reset, power-state transition, FLR, VF reset, or explicit driver/firmware writes.

Important state represented by this chunk includes per-VF PCI identity and capability presentation, MSI/MSI-X programming state, AER status and log registers, ATS/ARI capability control, doorbell aperture enablement, HDP coherency flush request/done state, BIF transaction pending status, mailbox contents/control, and VF MSI-X vector table contents.

Because these are VF-specific registers, persistence and visibility are affected by SR-IOV mode. PF, VF, firmware, hypervisor, and guest driver paths may see different access permissions or reset domains for the same logical register family.

## Dependencies

This chunk depends on the AMDGPU SOC15 register access framework and the surrounding generated NBIO register headers:

- `nbio_2_3_offset.h` for register offsets and base indices.
- `nbio_2_3_sh_mask.h` for field masks and shifts used with the offsets.
- `nbio_2_3_default.h` for reset/default values matching many of the same names.
- AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and `WREG32_FIELD15`.
- PCIe/SR-IOV conventions for VF configuration space, MSI/MSI-X, ATS, ARI, and AER capability layout.

The offset values are hardware ABI data. They must match the NBIO 2.3 register specification and the firmware/hypervisor view of PF/VF register decode windows.

## Risks

- Off-by-one or wrong-VF macro use can address a different VF's PCI config or BIF/RCC state. This is especially risky because VF3 through VF30 repeat identical offset values with only the VF number changing.
- Using a correct offset with the wrong `*_BASE_IDX` resolves to the wrong SOC15 register segment. The VF0/VF1 `SYSPFVFDEC` entries use base index `0`, `BIFPFVFDEC1` entries use `2`, and the VF0 MSI-X table block uses `3`.
- PCI config-space offsets are byte offsets, while many MMIO register offsets are dword-oriented and are commonly shifted by `<< 2` when forming byte addresses. The HDP remap path in `nbio_v2_3.c` is an example where this distinction matters.
- MSI and MSI-X fields intentionally overlap in config space depending on 32-bit versus 64-bit MSI layout, such as `MSI_MSG_ADDR_HI` sharing `0x00a8` with `MSI_MSG_DATA` and `MSI_MASK_64` sharing `0x00b0` with `MSI_PENDING`. Consumers must interpret those offsets according to the active capability format.
- AER, mailbox, HDP flush, and doorbell registers can be shared with firmware, PF, hypervisor, or guest VF code. Uncoordinated writes can lose diagnostics, break coherency flush completion, misroute interrupts, or disrupt VF communication.
- Generated headers are not self-validating. A typo or stale hardware drop can compile cleanly but produce incorrect MMIO traffic only visible on affected ASICs.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware bring-up oriented:

- Build coverage for AMDGPU NBIO 2.3 code proves all referenced macros remain defined and compatible with the SOC15 helper interfaces.
- SR-IOV VF boot and teardown should expose sane PCI IDs, BARs, MSI/MSI-X capabilities, ATS/ARI capabilities, and AER capability chains for VF3 through VF30 when those functions are enabled.
- KFD and graphics workloads should continue to complete HDP flushes after `nbio_v2_3_init_registers()` remaps the VF0 `HDP_MEM_COHERENCY_FLUSH_CNTL` register. Failures would appear as coherency bugs, stuck flush waits, or user-mode queue hangs.
- Doorbell tests should verify VF doorbell aperture enablement and self-ring aperture programming without spurious BIF doorbell interrupts.
- Interrupt tests should validate MSI/MSI-X vector programming and pending-bit behavior for the VF0 `GFXMSIX` table.
- Error-injection or PCIe AER diagnostics should confirm correct AER status, mask, severity, header log, and TLP prefix log visibility.
- Static checks can compare the repeated VF3-VF30 config maps against neighboring chunks and against `nbio_2_3_default.h` to detect missing or drifted generated entries.

### subset-b-002900: lines 4945-7706

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 4945-7706

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-offset header segment. It contains preprocessor constants only: 1,181 register offset macros and 1,181 matching `_BASE_IDX` macros for SR-IOV virtual-function register windows in `DEV0_EPF0`. There are no C functions, structs, enums, or executable control flow in the chunk.

The line range starts in the middle of VF1's BIF PF/VF decode block, contains VF1's MSI-X decode block, contains complete VF2 through VF25 register families, and ends in the early VF26 BIF PF/VF decode block before VF26's MSI-X block is complete.

## Purpose

The constants map NBIO/NBIF register names to SOC15 MMIO register offsets for Navi-era AMD GPUs using NBIO IP version 2.3. The register names describe the address block, PCIe endpoint/function, virtual-function number, and register role. Driver code includes this header to convert symbolic register names into numeric addresses through helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and the lower-level `RREG32_NO_KIQ()`/`WREG32_NO_KIQ()` mailbox accesses.

The chunk is specifically about SR-IOV virtual functions. The repeated `VF<n>` macro sets expose per-VF views of:

- indexed MMIO windows (`MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`);
- RCC PF/VF control/status registers (`RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`);
- BIF PF/VF status, atomics, doorbell self-ring aperture, HDP coherency flush, transaction-pending, address-LUT bypass, and VM/HV mailbox registers;
- MSI-X vector table and pending-bit-array offsets for four graphics MSI-X vectors.

## Important Macro Families

Each register is defined as a dword offset plus a matching base index. The offset names are not arrays; every VF instance is emitted as a separate macro.

The repeated complete VF2-VF25 layout is:

- `*_SYSPFVFDEC`: `MM_INDEX` at `0x0000`, `MM_DATA` at `0x0001`, and `MM_INDEX_HI` at `0x0006`, all with base index `0`.
- `RCC_*_BIFPFVFDEC1`: `RCC_ERR_LOG` at `0x0085`, `RCC_DOORBELL_APER_EN` at `0x00c0`, `RCC_CONFIG_MEMSIZE` at `0x00c3`, `RCC_CONFIG_RESERVED` at `0x00c4`, and `RCC_IOV_FUNC_IDENTIFIER` at `0x00c5`, all with base index `2`.
- `BIF_BX_*_BIFPFVFDEC1`: `BIF_BME_STATUS` at `0x00eb`, `BIF_ATOMIC_ERR_LOG` at `0x00ec`, doorbell self-ring base/control registers at `0x00f3`-`0x00f5`, HDP coherency flush control at `0x00f6`-`0x00f7`, GPU HDP flush request/done at `0x0106`-`0x0107`, `BIF_TRANS_PENDING` at `0x0108`, `NBIF_GFX_ADDR_LUT_BYPASS` at `0x0112`, mailbox transmit/receive dwords and control/interrupt registers at `0x0136`-`0x0140`, all with base index `2`.
- `RCC_*_BIFDEC2`: four MSI-X vector entries, each with low address, high address, message data, and control registers at `0x0400`-`0x040f`, plus `GFXMSIX_PBA` at `0x0800`, all with base index `3`.

The partial boundaries matter:

- Lines 4945-4985 are the tail of `VF1_BIFPFVFDEC1`, beginning after the VF1 `BIF_ATOMIC_ERR_LOG` offset and covering doorbell self-ring, HDP flush, transaction pending, address LUT bypass, mailbox, and VM/HV mailbox macros.
- Lines 4988-5021 cover `VF1_BIFDEC2` MSI-X vector and PBA macros.
- Lines 7666-7706 cover `VF26_SYSPFVFDEC`, `VF26_RCC_BIFPFVFDEC1`, and the first eight VF26 `BIF_BX_*_BIFPFVFDEC1` register offsets through `HDP_MEM_COHERENCY_FLUSH_CNTL`; the remaining VF26 registers continue after this chunk.

## Control Flow

There is no runtime control flow in this header. Runtime behavior appears in include consumers:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this header with the matching `nbio_2_3_sh_mask.h` masks. It programs PF-facing NBIO registers for memory-controller access, doorbell aperture enablement, doorbell ranges, HDP flush offsets, interrupt control, ASPM/LTR settings, and register remapping.
- `nbio_v2_3_set_reg_remap()` uses `mmBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` as the SR-IOV VF fallback remap anchor. This chunk does not contain VF0, but its VF1-VF26 HDP-flush constants follow the same generated layout.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header and uses mailbox registers (`mmMAILBOX_MSGBUF_*` aliases from the same generated register map) to exchange VF/PF messages, poll acknowledgements, and handle GPU access requests.
- SMU Navi10/Sienna Cichlid PPT code includes the header for NBIO register definitions, though this chunk's per-VF macro names are not directly referenced in the inspected SMU source.

## State and Persistence

The header itself stores no state. The macros address persistent hardware register state in the NBIO block:

- Doorbell aperture and self-ring registers persist hardware aperture base/control programming until reset or reprogramming.
- HDP coherency flush request/done and HDP flush-control registers represent hardware synchronization state used to make host/device memory ordering visible.
- `BIF_TRANS_PENDING`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, and `RCC_ERR_LOG` expose live bus/device status or diagnostic state.
- Mailbox transmit/receive dwords and control bits are transient PF/VF communication state. In `mxgpu_nv.c`, software explicitly clears valid bits, writes transmit dwords, polls ACK bits, and reads receive dwords.
- MSI-X vector address/data/control and PBA registers persist interrupt-routing configuration for each VF until changed by the OS, hypervisor, or device reset.

Because these are register offsets, the persistence boundary is hardware/firmware state rather than kernel memory. Incorrect constants can persistently program the wrong register until the affected GPU function is reset.

## Dependencies

This file depends on the SOC15 register-access model used by AMDGPU:

- `SOC15_REG_OFFSET(hwip, inst, reg)` combines the macro's dword offset with IP discovery base data and the associated `_BASE_IDX`.
- `RREG32_SOC15()` and `WREG32_SOC15()` use those offsets for normal MMIO register reads/writes.
- `nbio_2_3_sh_mask.h` provides the bit masks and shifts for fields within the registers defined here.
- `nbio_2_3_default.h` provides reset/default values for the same IP generation.
- The generated macro names must remain synchronized with the ASIC register database, firmware expectations, and virtualization model for NBIO 2.3.

## Integration Points

The main integration surface is the AMDGPU NBIO layer:

- `amdgpu_nbio_funcs` in `nbio_v2_3.c` publishes callbacks for HDP flush offsets, doorbell programming, interrupt setup, clock-gating state, ASPM handling, and remapping. These callbacks rely on this header's offsets to reach the correct NBIO registers.
- The SR-IOV path uses VF-specific windows to avoid direct PF-only register access from guest contexts. `nbio_v2_3_get_rev_id()` explicitly returns a safe rev ID for VFs because a guest reading a PF strap register can see `0xffffffff`.
- The MxGPU mailbox path uses NBIO mailbox registers as the synchronization channel between a guest VF and PF/hypervisor services for GPU init/fini/reset access, RAS requests, and error notification.
- The MSI-X offsets integrate with PCI interrupt routing for virtual functions: vector table registers at `0x0400`-`0x040f` and PBA at `0x0800` describe the per-VF interrupt-programming surface.

## Risks

- Generated-offset drift: these constants are hardware contracts. A wrong dword offset or `_BASE_IDX` can make the driver read/write a different NBIO register, which can break SR-IOV isolation, doorbell routing, HDP coherency, interrupts, or VF/PF mailbox handshakes.
- Boundary errors in chunking: this work item begins and ends inside larger generated VF blocks. Any merge/reconciliation step must combine adjacent chunks before drawing per-file conclusions about complete VF1 or VF26 coverage.
- Copy/paste pattern risk: the VF2-VF25 blocks are highly repetitive. A single malformed VF number, endpoint/function prefix, or base index can be hard to spot by inspection and would not necessarily be caught by C compilation if the macro is unused.
- Sparse direct references: many generated per-VF macros may not be referenced by current source, but they are still ABI-like register definitions for debug, future enablement, or indirect access. Removing apparently unused macros can break out-of-tree tooling or future ASIC paths.
- Virtualization sensitivity: mailbox and doorbell registers participate in PF/VF trust boundaries. Misprogrammed apertures or mailbox control bits can cause denial of service, stuck access requests, lost reset coordination, or writes outside the intended VF aperture.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/runtime oriented:

- Compile coverage: AMDGPU builds that include `nbio_v2_3.c`, `mxgpu_nv.c`, and Navi/Sienna SMU PPT files should compile without undefined NBIO 2.3 macros.
- Generated-header consistency checks: compare VF2-VF25 blocks for identical offsets/base indices modulo the VF number, and compare VF1/VF26 fragments against neighboring chunks to ensure no missing or duplicated register definitions.
- SR-IOV smoke tests: VF probe, GPU init/fini/reset access requests, and PF/VF mailbox ACK/valid polling should complete without timeouts or unrecoverable-state notifications.
- Doorbell tests: SDMA/IH/VCN doorbell programming and ring submission should succeed for PF and VF modes, with no doorbell interrupt status left uncleared.
- HDP coherency tests: command submission paths that request HDP flushes should observe matching flush-done bits and no stale memory visibility across CPU/GPU boundaries.
- Interrupt tests: MSI-X interrupt delivery for VF graphics vectors should work after vector address/data/control programming, and PBA status should reflect pending interrupts correctly.

### subset-b-002901: lines 7707-10473

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 7707-10473

## Chunk Scope

This chunk is a generated register-offset slice from AMDGPU's NBIO 2.3 ASIC register header. It covers 2,187 preprocessor definitions from the middle of the `VF26` virtual-function register block through the start of the `SWDS1` PCI bridge configuration block. The content is data, not executable logic: C code includes this header to name NBIO, BIF, RCC, PCIe, MSI-X, doorbell, mailbox, HDP flush, and PCI configuration register addresses without embedding numeric constants at call sites.

The mapped source range begins inside `nbio_nbif0_bif_bx_dev0_epf0_vf26_BIFPFVFDEC1`, at `mmBIF_BX_DEV0_EPF0_VF26_GPU_HDP_FLUSH_REQ_BASE_IDX`, and ends inside `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp`, at `cfgBIF_CFG_DEV0_SWDS1_SLOT_CAP`. Because this is a chunk of a larger generated header, both ends have cross-chunk continuity: earlier lines define the first half of VF26, and later lines continue the SWDS1 bridge capability table.

## Purpose

The chunk supplies symbolic register names for NBIO/BIF PCIe virtualization plumbing on AMD GPUs. It has two related address forms:

- `mm*` macros define register offsets and matching `*_BASE_IDX` selector values. These are typically consumed by AMDGPU register access macros that combine a block base index with an offset.
- `cfg*` macros define absolute configuration-space addresses for PCIe/NBIO configuration registers, including per-virtual-function windows and higher-level PCIe capability structures.

Most of the chunk is a repeated per-VF template. Virtual functions expose the same register names at different bases, so the generator emits families such as `VF0` through `VF30` with predictable address strides. That regularity is important for SR-IOV and virtualization code that may address individual VFs explicitly.

## Important Macro Families

The chunk contains these major groups:

- `mmBIF_BX_DEV0_EPF0_VF26` through `mmBIF_BX_DEV0_EPF0_VF30`: offset-based definitions for late virtual functions. Each VF has indirect MMIO index/data registers, RCC error and doorbell/config status registers, BIF bus-master/atomic/doorbell/HDP/mailbox registers, and a four-vector GFX MSI-X table plus PBA.
- `cfgBIF_BX_DEV0_EPF0_VF0` through `cfgBIF_BX_DEV0_EPF0_VF30`: absolute configuration addresses for per-VF BIF register windows. Each VF base advances by `0x80000`, from `0xd0000000` for `VF0` through `0xd0f00000` for `VF30`.
- `cfgRCC_DEV0_EPF0_VF*`: absolute addresses for RCC-side VF registers such as `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`, and each VF's GFX MSI-X vectors.
- `cfgPSWUSCFG0_1_*`: PCIe upstream switch/root-port style configuration registers at base `0xfffe00000000`. This includes conventional PCI config header fields, power-management capability, MSI, PCIe device/link/slot capabilities, SR-IOV, ATS, PASID, PRI, ARI, L1 PM substate, ESM, data-link feature, 16 GT/s PHY, margining, and CCIX capability registers.
- `cfgBIF_BX_PF0_*` and `cfgSUM_*`: a small physical-function indirect-index block and summary index/data registers.
- `cfgBIF_CFG_DEV0_SWDS1_*`: the start of a downstream bridge/device configuration block at `0xfffe10100000`, covering the conventional PCI header and initial PCIe capability registers through `SLOT_CAP` in this chunk.

Representative per-VF register categories include:

- indirect access: `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`;
- error/status: `RCC_ERR_LOG`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `BIF_TRANS_PENDING`;
- aperture and address control: `RCC_DOORBELL_APER_EN`, `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `DOORBELL_SELFRING_GPA_APER_BASE_LOW`, `DOORBELL_SELFRING_GPA_APER_CNTL`, `NBIF_GFX_ADDR_LUT_BYPASS`;
- coherency and flushing: `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`;
- virtualization mailbox: `MAILBOX_MSGBUF_TRN_DW0` through `DW3`, `MAILBOX_MSGBUF_RCV_DW0` through `DW3`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, `BIF_VMHV_MAILBOX`;
- interrupts: `GFXMSIX_VECT0` through `GFXMSIX_VECT3` address/data/control registers and `GFXMSIX_PBA`.

## APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this range. The public interface is the macro namespace itself. Consumers depend on these names being present at compile time and on the numeric values matching the hardware register map.

The `*_BASE_IDX` macros for `mm*` definitions are part of the access contract. In this chunk the MMIO index registers use base index `0`, the BIF/RCC VF functional registers use base index `2`, and GFX MSI-X registers use base index `3`. Driver code that uses AMDGPU's generated register accessor macros must pair the offset macro with the correct base-index macro; mixing base indices can target the wrong register block even when the offset looks valid.

## Control Flow

This header has no local control flow. Its control-flow effect is indirect:

- compile-time preprocessing substitutes symbolic register names into AMDGPU C code;
- call sites choose runtime ordering for operations such as writing mailbox transmit dwords, enabling doorbell apertures, requesting HDP flushes, polling `GPU_HDP_FLUSH_DONE` or `BIF_TRANS_PENDING`, and programming MSI-X vectors;
- SR-IOV or virtual-function management code can choose the target VF by selecting the macro family for a specific `VF<n>`.

For the per-VF families, the generated layout is intentionally uniform. The same semantic operation on a different VF is represented by the same suffix under another `VF<n>` prefix.

## State And Persistence

The file itself stores no runtime state. The macros identify hardware registers whose state is owned by the GPU/NBIO block and, for config-space registers, by PCIe configuration mechanisms. Persistence and reset behavior are therefore hardware-defined:

- doorbell aperture registers and GPA base registers control per-VF doorbell exposure;
- HDP coherency and flush registers coordinate CPU/GPU-visible memory ordering;
- mailbox registers carry VM/hypervisor or PF/VF control messages;
- MSI-X table/PBA and PCIe capability registers affect interrupt routing and PCIe feature negotiation;
- status/error registers retain hardware-observed conditions until cleared according to register-specific semantics from the corresponding mask/shift headers and hardware documentation.

Because this chunk contains offsets only, bit definitions, clear-on-read behavior, reset values, and access restrictions must be obtained from companion headers or register specs.

## Dependencies And Integration Points

This header is integrated by AMDGPU ASIC-specific code under the DRM driver tree. It is normally included with related generated NBIO 2.3 headers that provide masks, shifts, and possibly block base arrays. The macros in this chunk depend on:

- AMDGPU register access helpers that understand the `mm*` plus `*_BASE_IDX` convention;
- PCIe/NBIO initialization and SR-IOV paths that configure per-VF doorbells, mailboxes, BAR/config windows, MSI-X, and PCIe capabilities;
- interrupt setup code that programs `GFXMSIX_VECT*` and observes `GFXMSIX_PBA`;
- memory-management and synchronization code that requests/polls HDP flush registers;
- virtualization control paths that use mailbox and `RCC_IOV_FUNC_IDENTIFIER` registers to coordinate PF/VF or VM/hypervisor behavior.

The `cfgPSWUSCFG0_1_*` and `cfgBIF_CFG_DEV0_SWDS1_*` tables align with PCI/PCIe configuration-space layouts. They are likely consumed by low-level NBIO/PCIe code rather than generic Linux PCI core helpers, because the constants are GPU-internal config aperture addresses rather than normal bus/device/function offsets.

## Risks And Edge Cases

- The chunk starts and ends inside generated address blocks. Any human review or merge step must avoid treating this chunk as a complete standalone register map.
- The `VF*` definitions are repetitive but not disposable. A single wrong digit in a VF number, stride, or suffix would silently point code at another function's register window.
- `mm*` offset constants and `cfg*` absolute address constants have different units and access paths. Using a `cfg*` address with an accessor expecting an `mm*` offset, or vice versa, would be a serious register access bug.
- `*_BASE_IDX` values are as important as offsets for MMIO access. Copying only the offset macro can lose the register block selector.
- Some PCIe configuration entries are byte- or word-sized fields at odd offsets, while many GPU register accesses are dword-oriented. Consumers must use access widths compatible with the register field, especially for config header fields such as revision, class code bytes, status/control words, and MSI/PCIe capability fields.
- The `cfgBIF_CFG_DEV0_SWDS1_MSI_MSG_DATA` address is outside this mapped range's end but visible just after the boundary and shares an address with `MSI_MSG_ADDR_HI`; this is a common 32-bit versus 64-bit MSI layout ambiguity and should be handled by capability format, not by assuming every macro maps to a unique dword.
- Hardware availability may depend on ASIC revision, fusing, SR-IOV mode, and virtualization enablement. The header's presence does not prove every register is valid in every runtime configuration.

## Test Signals

Useful validation signals for changes touching this generated map include:

- build coverage for AMDGPU with NBIO 2.3 headers included, catching missing or renamed macros;
- generated-header consistency checks against AMD's source register database, especially per-VF stride checks from `VF0` to `VF30`;
- static checks that every `mm*` macro with a `*_BASE_IDX` suffix has the expected paired offset macro and base index;
- SR-IOV smoke tests that create or manage VFs and exercise mailbox, doorbell aperture, BME status, and VF identification paths;
- interrupt tests that program and deliver MSI-X vectors through the GFX MSI-X table;
- HDP flush tests that write `GPU_HDP_FLUSH_REQ`, observe `GPU_HDP_FLUSH_DONE`, and ensure no hangs while `BIF_TRANS_PENDING` is active;
- PCIe link capability/status validation for the `cfgPSWUSCFG0_1_*` block, including L1 PM substate, link speed capability, margining, ARI/SR-IOV/PASID/PRI/ATS exposure, and CCIX/ESM capability presence when supported.

## Cross-Chunk Notes

The preceding chunk is needed for the beginning of `VF26` offset definitions and earlier VF offset families. The following chunk is needed for the continuation of `cfgBIF_CFG_DEV0_SWDS1_*` after `SLOT_CAP` and any remaining PCIe downstream-device capability definitions. The final per-file research report should merge this chunk with neighboring chunks to present the complete generated register namespace for `nbio_2_3_offset.h`.

### subset-b-002902: lines 10474-12730

# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 10474-12730

## Scope

This chunk covers the middle of AMDGPU's generated NBIO 2.3 register offset header. It contains 2,189 preprocessor constants mapping NBIO/BIF PCIe configuration-space register names to absolute config aperture addresses from `0xfffe10100070` through `0xfffe1030c03f`. The chunk is data-only: no functions, structs, control statements, or storage objects are defined here.

The chunk starts inside `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp`, whose base is declared just before the chunk at `0xfffe10100000`, then defines full or partial address blocks for physical endpoint functions and SR-IOV virtual functions:

- `cfgBIF_CFG_DEV0_SWDS1_*`, continuing the downstream/switch-device PCIe configuration block from slot control/status through PCIe 16 GT/s and lane margining registers.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` at `0xfffe10200000`, with a large endpoint function 0 config-space window.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` at `0xfffe10201000`, also large and feature-rich.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and `epf3` at `0xfffe10202000` and `0xfffe10203000`, with smaller but still extended endpoint-function windows.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` through `vf11`, each with 79 repeated virtual-function config registers at `0xfffe10300000` plus a `0x1000` stride per VF.
- The beginning of `vf12`, from standard PCI config header registers through `MAX_LATENCY`.

## Purpose

`nbio_2_3_offset.h` is generated hardware metadata for the Navi-era NBIO 2.3 block. This chunk gives AMDGPU and display/power-management code stable symbolic names for PCIe configuration and extended-capability registers exposed through NBIO's BIF config decode path. Consumers can use these constants, usually with the companion shift/mask header, instead of open-coded addresses when programming PCIe capabilities, SR-IOV virtualization state, error reporting, power management, interrupts, and link behavior.

The `cfgBIF_CFG_*` names are especially important because they describe PCI-compatible configuration-space layout rather than ordinary MMIO registers. The low offsets within each base mirror conventional PCI/PCIe config offsets: vendor/device IDs at `+0x00`, command/status at `+0x04/+0x06`, BARs at `+0x10` and onward, capability pointers around `+0x34`, MSI/MSI-X around `+0xa0`/`+0xc0`, AER around `+0x150`, ATS/PASID/SR-IOV/LTR/ARI in extended-capability regions, and lane/equalization or margining controls in later PCIe extended space.

## Important APIs, Types, And Register Families

This header does not define C APIs or types. Its public surface is the set of `#define` register-address constants. The important register families in this chunk are:

- `cfgBIF_CFG_DEV0_SWDS1_*`: downstream port/bridge-style config registers, including slot control/status, MSI, subsystem ID, virtual channel, device serial number, AER status/masks/header logs, secondary PCIe capability, lane equalization, ACS, data-link feature, 16 GT/s capability, and per-lane margining controls.
- `cfgBIF_CFG_DEV0_EPF[0-3]_1_*`: physical endpoint function config windows. Common fields cover PCI header registers, BARs, ROM/capability pointers, MSI/MSI-X, PCIe device/link capability/control/status, AER, ACS/ATS/PASID/LTR/ARI, SR-IOV capability/control/VF BARs, and vendor-specific GPU IOV scheduler controls. EPF0 and EPF1 include broad virtualization and GPU IOV capability ranges; EPF2 and EPF3 are narrower and include dense TPH steering-table entries.
- `cfgBIF_CFG_DEV0_EPF0_VF[0-12]_1_*`: repeated SR-IOV virtual-function config windows. VF0 through VF11 each expose the standard PCI header, selected PCIe capability registers, MSI/MSI-X, vendor-specific registers, AER logs, ATS, and ARI. VF12 begins at the end of the chunk.

Companion generated headers in the same directory are part of the effective API:

- `nbio_2_3_sh_mask.h` supplies field shifts and masks for register names used by NBIO code.
- `nbio_2_3_default.h` supplies reset/default values for many of the same generated register symbols, including the VF ranges represented here.

## Control Flow

There is no local control flow in this chunk. At compile time, C preprocessor expansion substitutes these names into register access macros and address calculations. Runtime control flow is in the consumers:

- `amdgpu/nbio_v2_3.c` includes this offset header with the matching default and shift/mask headers, then programs NBIO and PCIe state via `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- `amdgpu/mxgpu_nv.c` includes the same NBIO generated headers for SR-IOV mailbox and virtualization paths, using NBIO/BIF mailbox registers and BIF interrupt IDs to coordinate PF/VF events.
- SMU power-management files for Navi10 and Sienna Cichlid include the NBIO 2.3 headers when reading BIF/PCIe strap and power-management state.
- DCN resource files include the offset header so display code can share generation-correct NBIO register names when building resource tables.

The chunk's physical-function and VF config windows are usually reached through the driver's PCIe/NBIO access helpers rather than by branching inside the header. The repeated `0x1000` VF stride and matching register offsets give callers a predictable map if they need to target a specific function or virtual function.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes hardware-backed PCIe/NBIO configuration state. Reads from addresses named here observe live device configuration, link state, error logs, MSI/MSI-X programming, SR-IOV VF configuration, and capability structures. Writes to writable registers can persist in hardware until reset, power transition, driver reinitialization, or PF/VF management action.

State represented by these constants includes:

- Link and slot state: device/link/slot control and status, link capability 2, lane error/equalization status, 16 GT/s fields, and margining status.
- Interrupt and message state: MSI/MSI-X message control, address/data, masks, pending bits, tables, and PBAs.
- Error state: AER uncorrectable/correctable error status, masks, severity, capability control, header logs, and TLP prefix logs.
- Virtualization state: SR-IOV capability/control/status, VF counts, VF stride, VF device IDs, supported/system page size, VF BARs, and GPUIOV vendor-specific scheduler regions for physical functions; repeated VF config windows for guest-visible functions.
- Addressing resources: endpoint BARs, ROM BARs, capability pointers, ARI/ATS/PASID capability controls, and LTR capability for power-management interactions.

Because these registers model PCI configuration space, some values may be owned by firmware, host PCI core, PF management firmware, or the hypervisor in SR-IOV mode. Driver writes must respect ownership and access restrictions.

## Dependencies And Integration Points

The chunk depends on AMD's generated ASIC register database staying in sync with the NBIO 2.3 hardware specification. It is guarded by the file-level `_nbio_2_3_OFFSET_HEADER` include guard and is compiled only as part of the larger header.

Primary integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which is the main generation-specific NBIO implementation. It programs PCIe config controls such as LTR, ASPM, link-width workarounds, clock gating, doorbells, HDP flush, and remap behavior using NBIO 2.3 register metadata.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which handles SR-IOV mailbox communication and interrupt setup for Navi virtualized GPUs.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which use NBIO 2.3 constants while deriving PCIe/power features and reading PCIe-related state.
- `drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c` and `dcn303_resource.c`, which include the generation-specific NBIO offset header as part of display resource integration.
- The matching `nbio_2_3_sh_mask.h` and `nbio_2_3_default.h` headers, which must describe fields and defaults for the same register names and addresses.

## Risks

- Address drift is high impact. If any generated constant maps to the wrong config-space address, the driver can read stale state or write a different PCIe/SR-IOV control register than intended.
- The chunk mixes physical-function, downstream-port, and virtual-function config spaces. Confusing `SWDS1`, `EPF*`, and `EPF0_VF*` symbols can cause writes to the wrong function class.
- Several symbols intentionally alias the same address for PCI layout variants, such as MSI high-address/data and mask/pending fields. Consumers must choose the symbol matching 32-bit vs 64-bit MSI interpretation rather than assuming each name is a distinct storage location.
- SR-IOV VF windows are repetitive and easy to update inconsistently. Missing or mis-strided VF entries would mainly surface under virtualization, where PF/VF ownership restrictions can make failures hard to reproduce on bare metal.
- Some config fields are controlled by platform firmware, the Linux PCI core, or the PF/hypervisor. Direct AMDGPU writes outside the expected init/reset paths can fight those owners.
- Build success only proves symbol availability. It does not prove that the generated address map matches silicon or that accesses are allowed in a particular PF/VF mode.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware tests:

- Compile coverage for all current include sites: `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, the SMU11 PPT files, and DCN resource files. Missing or renamed constants should fail at build time.
- Boot an NBIO 2.3 GPU and confirm AMDGPU initializes NBIO without PCIe config access faults, incorrect link setup, or doorbell/HDP remap failures.
- Exercise PCIe power-management paths: ASPM/LTR programming, clock gating/light-sleep toggles, suspend/resume, and link retraining or width reporting.
- Exercise SR-IOV PF and VF environments. Check VF enumeration, mailbox interrupts, MSI/MSI-X setup, VF BAR sizing, and guest-visible PCIe capability reads.
- Inspect PCIe AER and capability behavior with `lspci -vv` and kernel logs, looking for malformed capability chains, unexpected AER errors, or inconsistent MSI/MSI-X state.
- Compare generated offset/default/mask headers against the authoritative ASIC register database when regenerating NBIO 2.3 headers, especially around repeated EPF and VF ranges.

### subset-b-002903: lines 12731-14663

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 12731-14663

## Scope

This chunk is the final large slice of the generated AMD NBIO 2.3 register offset header. It contains C preprocessor address constants only: no functions, structs, variables, allocation, locking, branching, loops, or direct MMIO access. The range starts inside the virtual-function 12 PCIe config-space block, covers full VF13 through VF30 config-space blocks, then defines later NBIF/RCC/BIF/GDC config and MMIO blocks through the file end and closing include guard.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The range contains 1803 `#define` offset constants. Major address blocks in scope are:

- Tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`: 53 PCIe capability and extended-capability config-space offsets.
- Full `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp` through `vf30_bifcfgdecp`: 18 complete virtual-function PCIe config-space windows, 79 constants each.
- `nbio_nbif0_rcc_shadow_reg_shadowdec`: bridge shadow command/base/limit/IRQ and SUC index/data offsets.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`, `nbio_nbif0_bif_bx_SYSDEC`, and `nbio_nbif0_syshub_mmreg_syshubdec`: PF MMIO index/data windows, PCIe/SYSHUB indirect windows, BIOS/SBIOS scratch registers, interrupt controls, and GFX MMIO CAM remap offsets.
- RCC strap, endpoint, downstream, downstream-port, and PF/VF blocks: strap registers, endpoint PCIe controls, downstream link control, root-complex config, doorbell aperture, memory size, and IOV function identifier offsets.
- `nbio_nbif0_rcc_dev0_BIFDEC1`: RCC error, reset, VDM, margining, GPUIOV, peer, bus-number, XDMA, requester-ID, LTR, and arbitration offsets.
- `nbio_nbif0_bif_bx_BIFDEC1` and `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`: BIF reset/interrupt/doorbell/framebuffer/BACO/LUT/HDP flush/ring/mailbox/pad offsets and PF-specific coherency, HDP flush, atomic, BME, self-ring, and mailbox offsets.
- `nbio_nbif0_gdc_GDCDEC`: A2S/S2A, SDP, SHUB, clock/power, and doorbell range offsets for SDMA, IH, MMSCH0, and ACV.
- `nbio_nbif0_rcc_dev0_epf0_BIFDEC2`: four GFX MSI-X vector table entries and PBA offsets.

## Purpose

The purpose of this header section is to publish the NBIO 2.3 address ABI used by AMDGPU code when it programs or reads GPU northbridge I/O, PCIe, root-complex, doorbell, HDP flush, SR-IOV, mailbox, and GDC registers. Each macro names a hardware register or PCI config-space location and expands to the numeric address used by the driver-side access helpers.

This is the companion to generated field/default headers:

- `nbio_2_3_sh_mask.h` supplies the bit masks and shifts for fields inside these registers.
- `nbio_2_3_default.h` supplies generated default values where available.
- This `nbio_2_3_offset.h` file supplies `mm*`, `smn*`, and `cfg*` addresses/base indices. The assigned range is almost entirely `cfg*` addresses, with full physical-looking config addresses such as `0xfffe1030d000` for VF13 config space and `0x30303870` for `cfgBIF_DOORBELL_CNTL`.

Because the file is generated register metadata, exact numeric values are the main contract. A wrong constant often still compiles but points the driver or diagnostic tooling at the wrong hardware register.

## Important Macro Families

### VF PCIe Config-Space Windows

The first line is already inside VF12 and begins at `cfgBIF_CFG_DEV0_EPF0_VF12_1_PCIE_CAP_LIST`. The remainder of VF12 in this chunk covers standard PCIe capability offsets, MSI/MSI-X offsets, vendor-specific enhanced capability offsets, AER status/mask/severity/header-log/TLP-prefix-log offsets, ATS capability/control offsets, and ARI capability/control offsets.

VF13 through VF30 are complete repeated blocks. Each block starts on a 0x1000 boundary:

- VF13 base: `0xfffe1030d000`
- VF14 base: `0xfffe1030e000`
- VF15 base: `0xfffe1030f000`
- VF16 base: `0xfffe10310000`
- ...
- VF30 base: `0xfffe1031e000`

Every full VF block includes the Type 0 config header fields (`VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class/cache/latency/header/BIST, BARs 1-6, CIS pointer, adapter ID, ROM base, capability pointer, interrupt line/pin, and min/max latency), PCIe capability registers (`DEVICE_CAP`, `DEVICE_CNTL`, `LINK_CAP`, `LINK_CNTL`, `DEVICE_CAP2`, `LINK_CNTL2`, etc.), MSI/MSI-X layout, vendor-specific enhanced capability, AER logging/masks, ATS, and ARI. The repeated layout is part of the SR-IOV VF presentation for device 0 endpoint function 0.

The repeated MSI offsets intentionally contain aliases reflecting 32-bit versus 64-bit MSI layouts. For example, within each VF block `MSI_MSG_ADDR_HI` and `MSI_MSG_DATA` share the same numeric address, `MSI_MASK` and `MSI_MSG_DATA_64` share the next address, and `MSI_MASK_64` and `MSI_PENDING` share the following address. Consumers must interpret these according to the MSI capability format, not as independent storage.

### Shadow, Indirect Access, Scratch, and CAM Registers

`nbio_nbif0_rcc_shadow_reg_shadowdec` exposes bridge-shadow config state: command, base address, bus/latency, I/O and memory limit windows, prefetchable limit windows, IRQ bridge control, and SUC index/data. These are shadowed configuration surfaces rather than ordinary C state.

`nbio_nbif0_bif_bx_pf_SYSPFVFDEC` exposes PF MMIO index/data registers (`cfgBIF_BX_PF1_MM_INDEX`, `cfgBIF_BX_PF1_MM_DATA`, and high index). `nbio_nbif0_bif_bx_SYSDEC` exposes indirect SYSHUB and PCIe index/data windows, BIOS/SBIOS scratch registers 0-15, BIF interrupt control registers, and eight GFX MMIO register CAM address/remap pairs plus CAM control/completion registers. `nbio_nbif0_syshub_mmreg_syshubdec` aliases the SYSHUB index/data window.

These constants integrate with indirect register access and firmware/BIOS/driver coordination. Scratch registers and CAM remap registers can carry persistent coordination or address translation state until reset or reprogramming.

### RCC Strap, Endpoint, Downstream, and PF/VF Blocks

The RCC strap block defines `cfgRCC_BIF_STRAP0..6`, several `cfgRCC_BIF_STRAP_F0_*` registers, EOI/interrupt strap state, and sideband/CC register state. Endpoint and downstream blocks define endpoint PCIe controls, debug/status, DPA, LTR, replay/transaction control, unsupported-request response, error-reporting control, link speed, link bandwidth, bus/device/function, and port controls.

The `nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]` block supplies PF/VF-facing root-complex endpoint function 0 offsets:

- `cfgRCC_DEV0_EPF0_RCC_DOORBELL_APER_EN`
- `cfgRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`
- `cfgRCC_DEV0_EPF0_RCC_CONFIG_RESERVED`
- `cfgRCC_DEV0_EPF0_RCC_IOV_FUNC_IDENTIFIER`

`nbio_v2_3.c` directly reads `mmRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE` for memory-size reporting and writes the doorbell aperture enable field through the corresponding register-field helper. The `cfg*` aliases in this chunk are the config-address form of the same generated register database.

### RCC Device 0 Runtime Control

`nbio_nbif0_rcc_dev0_BIFDEC1` contains offsets for root-complex error interrupt control, BACO miscellaneous control, reset enable, VDM support, margining parameters, GPUIOV region, peer register ranges, bus control, config aperture sizing, XDMA lower/upper apertures, feature controls, bus-number capture/list registers, host bus-number registers, peer framebuffer offsets 0-3, device/function number lists, link controls, requester-ID restore, LTR switch control, and multi-host arbitration.

These addresses are relevant to PCIe/root-complex bring-up, virtualization, peer aperture programming, XDMA exposure, reset sequencing, and link management. The header does not encode which values are safe; it only exposes where those values live.

### BIF BX, Doorbells, HDP Flush, BACO, Mailbox, and Pads

`nbio_nbif0_bif_bx_BIFDEC1` defines BIF-side control and status offsets: straps, indirect MM access, bus control, scratch registers, reset control, interrupt control, CLKREQ pad control, feature control, doorbell control/interrupt control, framebuffer enable, BIF interrupt control, VF master/slave transaction pending status, BACO control and exit timers, memory type control, NBIF GFX address LUT control and 16 LUT entries, HDP remap flush controls, BIF ring-buffer controls/pointers/writeback address, mailbox index, MP1 interrupt control, GPU IOV config sizes for UVD/VCE/GFX SDMA, and PCIe pad controls for PERST, PX enable, reference clock, CLKREQ, PWRBRK, WAKE, and VAUX.

`nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` provides PF-specific offsets for BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP register/memory coherency flush, GPU HDP flush request/done, BIF transaction pending, LUT bypass, mailbox transmit/receive dwords, mailbox control, mailbox interrupt control, and VM/hypervisor mailbox.

These constants are directly aligned with `nbio_v2_3.c` behavior. That file writes remap HDP flush registers, enables/disables framebuffer access through `mmBIF_FB_EN`, programs SDMA/VCN/IH doorbell ranges, enables doorbell and self-ring apertures, writes `mmINTERRUPT_CNTL2` and fields in `mmINTERRUPT_CNTL`, returns HDP flush request/done offsets, clears doorbell interrupt status, and sets register remap addresses through versioned NBIO helpers.

### GDC and GFX MSI-X Blocks

The GDC block defines A2S control registers for client and switch paths, completion-buffer and tag allocation, A2S/S2A miscellaneous controls, NGDC SDP port and clock/power controls, SHUB register interface control, doorbell ranges for SDMA0, SDMA1, IH, MMSCH0, and ACV, doorbell fence control, and NGDC power-gating master/slave controls. The SDMA/IH/MMSCH doorbell range addresses are integration points for engine doorbell setup.

The final BIFDEC2 block defines four GFX MSI-X vector entries, each with address low, address high, message data, and control, plus `cfgRCC_DEV0_EPF0_GFXMSIX_PBA`. These offsets describe the GPU-facing MSI-X table/PBA storage for graphics interrupts.

## Control Flow

There is no executable control flow in this chunk. Runtime sequencing is supplied by AMDGPU code that includes this generated header:

1. Versioned NBIO, SMU, MXGPU, or display code selects a generated offset macro.
2. SOC15 or PCIe access helpers combine the offset with IP-instance/base information, or access an SMN/config-space address directly.
3. Generated field macros from `nbio_2_3_sh_mask.h` are used through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, or `WREG32_FIELD15` when only part of a register changes.
4. The driver writes, reads, polls, or returns the offset as part of hardware setup, power management, interrupt setup, doorbell setup, virtualization, or diagnostics.

Observed local include points for `nbio_2_3_offset.h` include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, SMU11 PPT files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`, and display resource files for DCN20/DCN303. The most direct runtime consumer is `nbio_v2_3.c`.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It names hardware-backed register state whose lifetime is controlled by GPU reset, PCIe reset/FLR, BACO, suspend/resume, firmware initialization, SR-IOV PF/VF policy, and driver programming.

The represented hardware state includes:

- PCIe VF config headers and capabilities, including BARs, command/status, MSI/MSI-X, AER, ATS, and ARI state.
- Shadow bridge config, indirect access windows, BIOS/SBIOS scratch state, and GFX MMIO CAM remap state.
- RCC straps, endpoint/downstream/root-complex configuration, bus numbering, peer apertures, XDMA aperture state, requester ID restore, and LTR/link controls.
- Doorbell aperture enablement, doorbell range assignments, self-ring aperture base/control, doorbell interrupt state, and doorbell fence control.
- Framebuffer access enablement, transaction-pending status, HDP coherency and flush request/done state, and remap flush controls.
- BACO/power/clock/pad state, NGDC power controls, BIF ring-buffer pointers/writeback address, and PF/VF mailbox buffers/control.
- GFX MSI-X vector table and pending-bit array state.

Some of these registers are persistent configuration until reset or reprogramming; others are status, command, interrupt-clear, pending, table, pointer, or log locations with hardware side effects. The header itself does not mark access width or side effects, so callers must rely on the ASIC register specification and existing AMDGPU access patterns.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`
- AMDGPU SOC15 and PCIe register helpers, including `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.

Concrete integration points visible in this source tree include:

- `nbio_v2_3_remap_hdp_registers()`, which writes remapped HDP memory/register flush controls.
- `nbio_v2_3_mc_access_enable()`, which toggles BIF framebuffer read/write enablement.
- `nbio_v2_3_get_memsize()`, which reads the RCC config memory-size register.
- `nbio_v2_3_sdma_doorbell_range()`, `nbio_v2_3_vcn_doorbell_range()`, and `nbio_v2_3_ih_doorbell_range()`, which program engine doorbell range registers.
- `nbio_v2_3_enable_doorbell_aperture()` and `nbio_v2_3_enable_doorbell_selfring_aperture()`, which program root-complex and PF self-ring doorbell aperture registers.
- `nbio_v2_3_ih_control()`, which writes interrupt control and dummy-read behavior.
- `nbio_v2_3_get_hdp_flush_req_offset()` and `nbio_v2_3_get_hdp_flush_done_offset()`, which provide higher-level HDP flush code with the relevant BIF PF flush request/done offsets.
- Clock-gating, ASPM, LTR, link-width workaround, and PCIe programming paths in `nbio_v2_3.c`, which use adjacent NBIO 2.3 PCIe/strap/link macros from the same generated header set.
- SMU and display resource code that includes this offset header for ASIC-specific register naming.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line starts midway through VF12, while the file-level report must merge adjacent chunks to describe the full VF12 block.
- The generated `cfg*` constants are untyped numeric addresses. A wrong value can compile cleanly and only fail as hardware misprogramming, bad diagnostics, timeouts, or missing interrupts.
- VF config blocks are highly repetitive. Off-by-one VF numbering or 0x1000-base drift can target the wrong virtual function, which is especially risky for SR-IOV isolation, MSI/MSI-X programming, AER status, ATS, and ARI controls.
- MSI 32-bit/64-bit alias offsets reuse numeric addresses by design. Code must interpret them based on capability mode rather than treating every macro as unique storage.
- Doorbell and self-ring aperture offsets are security- and isolation-sensitive. Incorrect aperture enable/base/size programming can expose the wrong doorbell range or break engine notification.
- HDP flush and coherency offsets are ordering-sensitive. Wrong request/done/remap addresses can leave CPU-visible GPU memory stale or cause waits for acknowledgments that never arrive.
- Scratch, mailbox, and CAM registers may be shared with firmware, BIOS, PSP/SMU, hypervisor, or PF/VF coordination paths. Writing the wrong full-width offset can corrupt coordination state without a type-system warning.
- Power, BACO, pad, reset, link, and clock-related offsets can affect register accessibility and PCIe stability. Register writes around these areas need hardware-sequenced ordering and ASIC-specific guards.

## Test Signals

Useful validation for this chunk is mostly build-time plus hardware integration:

- Build AMDGPU for ASICs using NBIO 2.3 headers; missing or renamed macros should fail in `nbio_v2_3.c`, SMU PPT, MXGPU, or display resource include paths.
- Exercise NBIO bring-up, reset, suspend/resume, BACO, ASPM/LTR, and clock-gating flows; link drops, register-access failures, or power-management regressions can indicate offset/header drift.
- Run doorbell-backed workloads for SDMA, IH interrupt handling, VCN/MMSCH, and ACV where applicable; missed interrupts or engines not waking point at doorbell range/aperture issues.
- Exercise HDP flush paths through graphics and SDMA workloads; stale CPU-visible memory, coherency failures, or timeout waiting for flush done are strong signals for BIF/HDP offset problems.
- In SR-IOV configurations, validate PF and VF isolation, VF config-space enumeration, MSI/MSI-X delivery, ATS/ARI behavior, and AER reporting across VFs near the covered VF12-VF30 range.
- Validate mailbox and MXGPU paths under virtualization; lost PF/VF messages, interrupt storms, or stale message buffers can indicate mailbox or interrupt-control drift.
- Use PCIe error-injection or diagnostics where available to confirm AER status/mask/log offsets and root-complex error controls behave as expected.
