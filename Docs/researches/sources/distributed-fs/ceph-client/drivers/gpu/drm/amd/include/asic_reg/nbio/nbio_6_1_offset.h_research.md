# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003003`: lines 1-2481, `Docs/researches/chunks/subset-b-003003_research.md`
- `subset-b-003004`: lines 2482-3651, `Docs/researches/chunks/subset-b-003004_research.md`

## Chunk Research

### subset-b-003003: lines 1-2481

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h lines 1-2481

## Scope

This chunk is the opening portion of a generated AMD NBIO 6.1 register-offset header. It contains C preprocessor constants only: include guard, license text, address-block comments, `cfg*` PCI configuration-space offsets, `mm*` MMIO register offsets, and matching `*_BASE_IDX` selector constants. There are no C functions, structs, enums, variables, branches, loops, allocation paths, locking paths, or direct register reads/writes in this range.

The source path is under a local `ceph-client` source mirror, but this file is AMDGPU hardware metadata for the Linux DRM AMD driver. It is not Ceph filesystem logic.

The assigned range covers lines 1-2481 of a 3651-line file. The range contains 2339 `#define` lines across these address blocks:

- `nbio_pcie_pswuscfg0_cfgdecp`, an upstream/switch PCIe configuration-space image.
- `nbio_nbif_bif_cfg_dev0_epf0_bifcfgdecp` and `nbio_nbif_bif_cfg_dev0_epf1_bifcfgdecp`, physical-function endpoint function 0 and function 1 PCIe configuration spaces.
- `nbio_nbif_bif_cfg_dev0_swds_bifcfgdecp`, a downstream/switch-style PCIe configuration-space image.
- `nbio_nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp` through `vf15`, 16 virtual-function PCIe configuration-space images for SR-IOV.
- `nbio_nbif_bif_bx_pf_SYSPFVFDEC[0..767]`, `SYSDEC[0..767]`, `syshub_mmreg_ind_syshubdec[32..39]`, and several `BIFDEC1` / `BIFPFVFDEC1` blocks that define MMIO register offsets and base-index selectors for NBIO system, RCC, endpoint, downstream, PF, BIF, interrupt, doorbell, scratch, and reset registers.

The chunk ends at `mmBACO_CNTL_BASE_IDX`. Later NBIO 6.1 offset definitions, including additional BIF mailbox, remap, HDP flush, doorbell, SMU, and other register blocks, are outside this work item and must be covered by later chunks.

## Purpose

The purpose of this header segment is to publish symbolic offsets for NBIO 6.1 hardware registers. AMDGPU runtime code uses these constants to compute register addresses, select indirect access windows, and pair offsets with field masks from `nbio_6_1_sh_mask.h`.

The `cfg*` constants are byte offsets into PCI/PCIe configuration-space images. They describe conventional PCI header fields, standard PCIe capabilities, and PCIe extended capabilities for upstream/switch, physical-function endpoint, downstream/switch, and SR-IOV virtual-function views.

The `mm*` constants are register indices within SOC15/NBIO register spaces. Most MMIO definitions in this chunk also have a companion `<REG>_BASE_IDX` macro. AMDGPU register helpers combine the register index with the base index through macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `NBIO_BASE`, and display-resource register-offset tables.

## Important Macro Families

The `cfgPSWUSCFG0_*` block defines an upstream/switch PCIe configuration map. It begins with identity and class-code fields such as vendor/device ID, command/status, revision, class, cache-line, latency, header, and BIST. It then covers bridge-style bus numbering, I/O and memory base/limit windows, capability pointers, interrupt fields, power-management capability, PCIe device/link capability and control/status registers, MSI, subsystem ID, MSI map, vendor-specific extended capability, virtual channels, device serial number, AER, TLP header and prefix logs, secondary PCIe capability, lane 0-15 equalization controls, ACS, multicast, LTR, ARI, L1 PM substate, and ESM capability/status/control registers.

The `cfgBIF_CFG_DEV0_EPF0_0_*` and `cfgBIF_CFG_DEV0_EPF1_0_*` blocks define physical endpoint function 0 and function 1 configuration spaces. They include standard endpoint header fields and BARs, ROM BAR, interrupt fields, PM capability, PCIe capability, MSI/MSI-X, vendor-specific and VC capabilities, serial number, AER, BAR enhanced capability, power budget, dynamic power allocation, secondary PCIe link training, ACS, ATS, page request interface, PASID, TPH requester, multicast, LTR, ARI, and SR-IOV capability registers.

The physical-function endpoint blocks also include AMD GPU IOV vendor-specific offsets. The `GPUIOV` subsection covers SR-IOV shadowing, interrupt enable/status, reset control, hypervisor-to-VM mailbox dwords, context, total frame-buffer sizing, per-VF frame-buffer allocations for VF0 through VF15, and scheduler configuration dwords for UVD, VCE, and GFX. These offsets are important to virtualization and partitioning code because they expose GPU-specific PF/VF management state through PCIe extended configuration space.

The `cfgBIF_CFG_DEV0_SWDS0_*` block is a downstream/switch-style configuration image. It mirrors bridge-oriented PCI header fields, bridge windows, PM and PCIe capabilities, slot capability/control/status, MSI, subsystem ID, vendor-specific/VC/serial-number/AER/secondary-PCIe/lane-equalization/ACS fields. Unlike the endpoint PF blocks, this block is not the full GPU IOV PF capability map.

The `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` through `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` blocks are repeated SR-IOV virtual-function configuration images. Each VF block has 79 offsets and covers identity/class/header fields, VF BARs, ROM, capability pointer, interrupt line/pin, PCIe capability, Device/Link Capability 2 and Control/Status 2, MSI/MSI-X, vendor-specific capability, AER status/mask/severity/logs, ATS, and ARI. These blocks intentionally omit the PF-only power budget, DPA, page-request, PASID, TPH, multicast, LTR, and SR-IOV management capability groups present in the PF maps.

The first MMIO address blocks provide indirect register-window offsets. `mmMM_INDEX`, `mmMM_DATA`, and `mmMM_INDEX_HI` are in the `SYSPFVFDEC` block. `mmSYSHUB_INDEX_OVLP`, `mmSYSHUB_DATA_OVLP`, `mmPCIE_INDEX`, `mmPCIE_DATA`, `mmPCIE_INDEX2`, and `mmPCIE_DATA2` are in the `SYSDEC` block. In `nbio_v6_1.c`, the NBIO function table exposes `SOC15_REG_OFFSET(NBIO, 0, mmPCIE_INDEX2)` and `mmPCIE_DATA2` as the PCIe indirect index/data offsets.

The `SYSDEC` block also defines `mmSBIOS_SCRATCH_0..3` and `mmBIOS_SCRATCH_0..15`, BIF interrupt controls for RLC/VCE/UVD, and `mmGFX_MMIOREG_CAM_*` mapping/remap/completion controls. Display code includes this offset header and maps BIOS scratch registers into a DCE 12.0 register table by adding `NBIO_BASE(mmBIOS_SCRATCH_*_BASE_IDX)`.

The `syshub_mmreg_ind_syshubdec` block provides non-overlap `mmSYSHUB_INDEX` and `mmSYSHUB_DATA` offsets. These pair with the overlap syshub index/data macros above and indicate separate indirect access routes into Syshub registers.

The `RCC` and `BIFDEC1` blocks define strap, endpoint, downstream, PF, bus, reset, interrupt, doorbell, and BACO-related MMIO offsets. Notable constants include `mmRCC_BIF_STRAP0`, `mmRCC_DEV0_EPF0_STRAP0`, `mmEP_PCIE_*`, `mmDN_PCIE_*`, `mmPCIE_ERR_CNTL`, `mmPCIE_RX_CNTL`, `mmPCIE_LC_SPEED_CNTL`, `mmRCC_PF_0_0_RCC_CONFIG_MEMSIZE`, `mmRCC_PF_0_0_RCC_DOORBELL_APER_EN`, `mmRCC_ERR_INT_CNTL`, `mmRCC_RESET_EN`, peer FB offset registers, bus-number capture/list registers, `mmBIF_MM_INDACCESS_CNTL`, `mmBUS_CNTL`, `mmBIF_SCRATCH0/1`, `mmBX_RESET_EN`, `mmMM_CFGREGS_CNTL`, `mmBX_RESET_CNTL`, `mmINTERRUPT_CNTL`, `mmINTERRUPT_CNTL2`, `mmCLKREQB_PAD_CNTL`, `mmBIF_DOORBELL_CNTL`, `mmBIF_FB_EN`, transaction-pending VF status, and `mmBACO_CNTL`.

## APIs, Types, And Functions

This chunk exports no typed APIs. Its public interface is the set of macro names made visible by including `nbio_6_1_offset.h`.

The practical API contract is naming consistency across generated AMDGPU hardware headers:

- `nbio_6_1_offset.h` provides register offsets.
- `nbio_6_1_sh_mask.h` provides field shifts and masks for those register names.
- `nbio_6_1_default.h` provides reset/default values for selected registers.
- `nbio_6_1_smn.h` provides SMN addresses for registers accessed through SMN/PCIe paths.

Consumers are normal AMDGPU register helper code, not functions in this header. Direct includes observed in this tree include `amdgpu/nbio_v6_1.c`, `amdgpu/mxgpu_ai.c`, `amdgpu/psp_v3_1.c`, powerplay Vega include files, and DCE 12.0 display resource code.

## Control Flow

There is no executable control flow in this header. Runtime control flow occurs in including code:

1. Driver code selects an offset macro from this file.
2. It combines the offset with an NBIO instance and base index, commonly through `SOC15_REG_OFFSET(NBIO, 0, <mmREG>)` or by adding `NBIO_BASE(<mmREG>_BASE_IDX)`.
3. It reads, writes, or read-modify-writes the register through AMDGPU accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_NO_KIQ`, or `WREG32_NO_KIQ`.
4. It uses masks/shifts from `nbio_6_1_sh_mask.h` with helpers such as `REG_SET_FIELD` or `REG_GET_FIELD` to update specific bitfields.

Concrete integration examples from `nbio_v6_1.c` include reading `mmRCC_DEV0_EPF0_STRAP0` to derive the revision ID, writing `mmBIF_FB_EN` to enable or disable memory-controller access, reading `mmRCC_PF_0_0_RCC_CONFIG_MEMSIZE` for memory size, programming `mmRCC_PF_0_0_RCC_DOORBELL_APER_EN` and BIF doorbell registers for doorbell aperture control, configuring `mmINTERRUPT_CNTL` and `mmINTERRUPT_CNTL2` for IH behavior, and exposing `mmPCIE_INDEX2` / `mmPCIE_DATA2` as PCIe indirect access registers.

Virtualization control flow in `mxgpu_ai.c` uses later BIF mailbox registers from the same generated NBIO 6.1 header family for PF/VF mailbox handshakes. The PF/VF PCI config-space and GPUIOV offsets in this chunk are part of that same virtualization-facing hardware model even when specific mailbox dword offsets are outside this assigned range.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It is compile-time metadata for hardware-backed state.

The represented hardware state includes PCI identity and class fields, bridge resource windows, BARs, ROM BARs, capability-list pointers, power-management state, PCIe device/link/slot controls and statuses, MSI/MSI-X programming, AER status and diagnostic logs, ACS routing controls, ARI and ATS configuration, SR-IOV PF and VF configuration state, GPUIOV partitioning/mailbox/scheduler state, BIOS/SBIOS scratch registers, GFX MMIO remap CAM state, interrupt-control registers, doorbell apertures, reset controls, BACO controls, frame-buffer enablement, transaction-pending status, bus numbering, and peer frame-buffer offsets.

Ownership of that state is mixed. Some fields are firmware- or hardware-initialized capabilities; some are Linux PCI core managed config-space fields; some are AMDGPU-owned controls; some are PF-owned virtualization controls; and some are sticky or hardware-updated status registers. The offset header does not encode reset defaults, access permissions, write-one-to-clear behavior, side effects, ordering requirements, or whether a PF, VF, firmware component, PCI core, display code, PSP path, or NBIO code owns a field at a given time.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 6.1 register database staying internally synchronized. Offset names here must match field-mask names in `nbio_6_1_sh_mask.h`, defaults in `nbio_6_1_default.h`, and any SMN aliases in `nbio_6_1_smn.h`. A mismatch can compile if the wrong macro is still defined, but the driver may read or write the wrong hardware register or field.

AMDGPU NBIO setup is the primary integration point. The `nbio_v6_1_funcs` implementation uses constants from this generated header for revision detection, memory access enablement, memory-size discovery, doorbell setup, IH interrupt behavior, PCIe indirect register access, HDP remap setup, and register-remap selection.

Display integrates through BIOS scratch register offsets. The DCE 12.0 resource code maps `mmBIOS_SCRATCH_0`, `mmBIOS_SCRATCH_3`, and `mmBIOS_SCRATCH_6` with the corresponding NBIO base index for display BIOS scratch access.

Virtualization integrates through both config-space and MMIO surfaces. The PF endpoint blocks expose SR-IOV capability and AMD GPUIOV management offsets. The VF endpoint blocks describe each VF's visible PCIe configuration image. MXGPU/AI mailbox code includes this header family to talk to PF/VF mailbox registers and manage access handshakes, while this chunk supplies the surrounding PF/VF configuration and RCC/BIF register offsets.

Power management and PCIe link policy integrate through PCIe, RCC, LTR, DPA, L1 PM substate, BACO, CLKREQ, ASPM, and link-control-related registers. Some direct SMN constants for ASPM/LTR programming are defined in `nbio_v6_1.c`, but they target the same NBIO/PCIe register domain described by this generated metadata.

The Linux PCI core is an implicit integration point for all `cfg*` fields. BARs, bus windows, command/status, PM state, MSI/MSI-X, ACS, ATS, ARI, SR-IOV, AER, and link capability fields overlap generic PCIe enumeration and policy. AMDGPU code must avoid fighting PCI core ownership unless the field is explicitly hardware-private or device-specific.

## Risks And Edge Cases

- These are untyped preprocessor constants. A stale, duplicated, or shifted offset can compile cleanly while causing runtime access to the wrong register.
- The file is generated and highly repetitive. The PF0/PF1 blocks and the 16 VF blocks are vulnerable to generation drift, copy errors, lane/function/VF number mismatch, or missing offsets that only appear under specific hardware or SR-IOV configurations.
- `cfg*` offsets are byte offsets in PCI configuration space, while `mm*` offsets are MMIO register indices with base-index selectors. Mixing these addressing models would be a serious bug.
- `_BASE_IDX` values are part of the address computation contract. Using an `mm*` register without the correct base index, or with the wrong SOC15 instance, can target a different NBIO aperture.
- Some macros intentionally share the same numeric offset because the hardware overlays meanings by access width, mode, or capability layout. Examples in this chunk include MSI data/mask/pending aliases and DPA substate allocation offsets. A naive uniqueness check would report false positives, while a naive consumer could still choose the wrong semantic alias.
- PCIe control fields are interoperability-sensitive. Incorrect BAR/window, command/status, bridge bus-numbering, completion-timeout, read-request, relaxed-ordering, no-snoop, ASPM, LTR, DPA, ARI, ATS, PASID, PRI, TPH, VC, or link-training programming can break enumeration, DMA ordering, reset, suspend/resume, or link stability.
- MSI and MSI-X offsets carry interrupt-delivery side effects. Width, address/data, mask, pending, table, and PBA mistakes can cause lost or misrouted interrupts.
- AER and TLP log registers may be sticky or write-one-to-clear in hardware. Generic read/modify/write patterns can lose diagnostics or leave errors masked incorrectly.
- ACS, ARI, ATS, PRI, PASID, SR-IOV, and GPUIOV fields affect isolation and address translation. Incorrect offsets or ownership assumptions can compromise VF isolation, PF/VF reset behavior, DMA translation, or peer-to-peer routing policy.
- Doorbell, frame-buffer enable, transaction-pending, reset, BACO, and interrupt-control registers are stateful hardware controls. Incorrect use can cause hangs, inaccessible VRAM, lost interrupts, failed low-power transitions, or reset failures.
- Chunk boundaries are artificial. The header guard opens in this chunk, but the closing `#endif` is outside it. Several related NBIO 6.1 BIF and mailbox offsets used by integration code are also outside this chunk.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware integration:

- Build AMDGPU configurations that include NBIO 6.1 support. Missing or renamed macros should surface in `nbio_v6_1.c`, `mxgpu_ai.c`, `psp_v3_1.c`, Vega powerplay includes, or display resource code.
- Compare this offset header against `nbio_6_1_sh_mask.h`, `nbio_6_1_default.h`, and `nbio_6_1_smn.h` to confirm matching register names and address-block boundaries.
- Exercise basic bring-up on NBIO 6.1 ASICs: revision ID read from `mmRCC_DEV0_EPF0_STRAP0`, memory-size read from `mmRCC_PF_0_0_RCC_CONFIG_MEMSIZE`, memory access enable/disable via `mmBIF_FB_EN`, IH interrupt setup through `mmINTERRUPT_CNTL*`, and PCIe indirect access through `mmPCIE_INDEX2` / `mmPCIE_DATA2`.
- Validate display paths that use BIOS scratch offsets, especially resume, display detection, and firmware/driver handoff flows that depend on scratch-register state.
- Run SR-IOV and MXGPU scenarios with PF and VF enumeration, VF BAR exposure, MSI/MSI-X delivery, PF/VF reset, mailbox access handshakes, GPUIOV frame-buffer partitioning, and VF transaction-pending checks.
- Exercise PCIe link and power-management paths: ASPM, LTR, DPA, L1 PM substate, link retraining, suspend/resume, runtime power management, BACO entry/exit, and CLKREQ behavior.
- Use AER injection or platform diagnostics where available to verify AER status/mask/severity/log offsets for PF, VF, switch/upstream, and downstream views.
- Test ACS, ATS, PASID, PRI, ARI, SR-IOV, and peer-to-peer DMA behavior on hardware and platforms that expose those capabilities, watching for isolation failures, translation failures, or unexpected routing changes.

## Chunk Notes

- Lines 1-25 contain license and include guard material.
- Lines 26-2127 are almost entirely PCI/PCIe configuration-space offset maps: upstream/switch, PF0, PF1, downstream/switch, and VF0-VF15.
- Lines 2128-2481 switch to MMIO-style `mm*` offsets and `_BASE_IDX` selectors for NBIO indirect windows, BIOS scratch registers, GFX MMIO remap CAM, Syshub access, RCC, endpoint/downstream PCIe controls, PF controls, BIF controls, interrupt controls, doorbell controls, frame-buffer enable, transaction-pending status, and BACO.
- The source file continues after this chunk; final per-file research should merge this report with later chunk reports before drawing whole-file conclusions.

### subset-b-003004: lines 2482-3651

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h lines 2482-3651

## Scope And Purpose

This chunk is the final portion of the generated NBIO 6.1 register offset header. It contains preprocessor constants for AMDGPU NBIO/BIF, GDC, RCC/MSI-X, SR-IOV virtual-function, and Syshub indirect register addresses. The file does not implement executable logic; it gives driver code stable symbolic names for hardware register offsets and base-index selectors.

The chunk defines 536 register-name constants and 477 `_BASE_IDX` constants. Most direct MMIO-style names use the `mm` prefix, while the tail Syshub entries use `ix` names for indexed indirect registers. Runtime code combines these offsets with matching shift/mask headers and AMDGPU register access helpers to read, write, poll, and update NBIO state.

## Register Families Covered

The opening block continues NBIF BIF offsets from the previous chunk. It covers BACO exit timing registers, memory type control, SMU/BIF VDDGFX power-status and per-GFX power-window registers, VDDGFX reserved window pairs, VDDGFX framebuffer compare, doorbell global aperture pairs, HDP flush remap controls, a BIF ring-buffer control/base/read/write-pointer group, mailbox index, GPU IOV config-size registers for UVD/VCE/GFX/SDMA, and PCIe pad-control registers for reset, power-enable, reference clock, and clock-request pins.

`nbio_nbif_bif_bx_pf_BIFPFVFDEC1` defines physical-function BIF/PF-visible offsets for bus-master-enable status, atomic error logging, doorbell self-ring GPA aperture base/control, HDP register and memory coherency flush controls, GPU HDP flush request/done registers, BIF transaction-pending status, four transmit and four receive mailbox dwords, mailbox control, mailbox interrupt control, and the VM/HV mailbox.

`nbio_nbif_gdc_GDCDEC[14976..15487]` defines GDC and doorbell-related offsets. The named registers include NGDC SDP port controls, SHUB register interface control, reserved NGDC slots, SDMA0/SDMA1/IH/MMSCH0 doorbell ranges, doorbell fence control, and S2A miscellaneous control.

`nbio_nbif_rcc_pf_0_BIFDEC2` defines the physical-function RCC MSI-X table offsets for graphics vectors 0 through 2. Each vector has low/high address, message data, and control offsets, followed by the graphics MSI-X pending-bit array. These offsets use base index 3 rather than the common NBIF base index 2.

The generated `nbio_nbif_bif_bx_pf_SYSPFVFDEC[0..255]` block is present only as commented-out PF index/data/index-high names. The active equivalents in this chunk are the per-VF `SYSPFVFDEC` blocks for VF0 through VF15, each with `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` at base index 0.

For each VF0 through VF15, the chunk then repeats the same `BIFPFVFDEC1` register pattern: BME status, atomic error log, doorbell self-ring GPA aperture high/low/control, HDP register and memory coherency flush controls, GPU HDP flush request/done, BIF transaction-pending status, mailbox transmit and receive dwords, mailbox control, mailbox interrupt control, and VM/HV mailbox. The register offsets are the same across VFs; the macro name encodes the function instance.

The final `syshub_mmreg_ind_syshubind` block defines indirect Syshub offsets for SOC clock and SHUB clock domains. It includes deep-sleep control, enhancement bypass/immediate enable controls, DMA and host clock QoS/class controls, Syshub clock-gating and transaction-idle status, high-priority timer, MGCG controls, scratch/class-mask registers, and NIC400 ASIB/AMIB function-modifier offsets.

## APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. Its exported interface is the set of generated `#define` names:

- `mm...` register-offset macros for NBIO direct register access.
- Matching `mm..._BASE_IDX` macros that select the AMDGPU register base array entry used by SOC15 register helpers.
- `ixSYSHUB_MMREG_IND_...` indirect-register offset macros for Syshub indexed access.

Important consumers are expected to be AMDGPU NBIO, PCIe, SR-IOV, interrupt, mailbox, power-management, HDP flush, and doorbell code paths that include this header through the ASIC-specific register set. Typical access patterns in AMDGPU code combine the offset with helper macros or functions such as SOC15 register-offset construction, indexed MMIO helpers, and register-field helpers from the corresponding shift/mask header.

## Control Flow

This header has no control flow. It influences runtime behavior only by resolving symbolic register names at compile time.

The runtime control flow lives in the consuming driver code. For example, a mailbox or HDP flush path may write a request register, poll a done/status register, and then clear or acknowledge state. A SR-IOV management path may select a VF-specific `MM_INDEX`/`MM_DATA` aperture and then operate on the matching VF BIF registers. A Syshub clock or QoS path may use the `ixSYSHUB_MMREG_IND_*` offsets through an indirect register interface. Those sequences are not encoded here; this chunk only supplies the addresses.

## State And Persistence Behavior

The persistent state represented by this chunk is hardware state in the NBIO, BIF, GDC, RCC, virtual-function, and Syshub blocks. The header itself stores no software state and performs no persistence.

Notable hardware state categories include BACO exit timers, VDDGFX power-window ranges, memory-type and pad controls, doorbell aperture and per-engine doorbell range state, HDP coherency flush request/done state, BIF transaction-pending status, mailbox payload/control/interrupt state, MSI-X vector address/data/control state, per-VF MMIO index/data aperture state, and Syshub QoS, clock-gating, idle, scratch, and interconnect function-modifier state.

Several registers are naturally sequencing-sensitive even though the header does not express the sequencing. Flush request/done pairs, transaction-pending status, mailbox transmit/receive dwords, MSI-X vector controls, BACO timing registers, and per-VF indirect index/data registers require consumer code to respect hardware ordering, timeout, and privilege rules.

## Dependencies And Integration Points

This chunk depends on the rest of the generated NBIO 6.1 register package:

- Earlier portions of `nbio_6_1_offset.h`, which define adjacent NBIO offsets not visible in this chunk.
- The matching `nbio_6_1_sh_mask.h` file, which provides field shifts and masks for many of these registers.
- Any matching default-value header for reset/default metadata where generated.
- AMDGPU SOC15 register-base metadata, which interprets `_BASE_IDX` values such as 0, 2, and 3.
- AMDGPU register access helpers for direct MMIO, PCIe/NBIO access, indexed Syshub access, polling, and field packing/extraction.

Integration points are hardware-facing rather than source-level call sites. The BIF and PF/VF blocks integrate with PCIe/NBIO initialization, SR-IOV virtualization, PF/VF mailbox communication, HDP flush handling, doorbell routing, GPU IOV config sizing, BACO/power management, and interrupt/MSI-X programming. The GDC block integrates with engine doorbell range assignment and SHUB register access. The Syshub indirect block integrates with clock-gating, QoS/class-limiter, idle detection, and NIC400 interconnect configuration.

## Risks And Edge Cases

Generated offset headers are easy to treat as inert data, but mistakes here have high blast radius. A wrong offset or base index can redirect a write to an unrelated hardware register, break boot-time initialization, wedge a flush or mailbox protocol, or corrupt privilege-sensitive SR-IOV state.

The repeated VF0 through VF15 blocks are especially sensitive. Their offsets intentionally match across virtual functions while the macro names distinguish the VF instance. Consumers must use the correct VF-specific symbol or an equivalent generated lookup pattern; mixing PF and VF names can break isolation, mailbox routing, or HDP flush ownership.

The `_BASE_IDX` values are part of the address contract. Most NBIF/GDC/PF/VF BIF registers in this chunk use base index 2, VF `MM_INDEX`/`MM_DATA` apertures use base index 0, and RCC MSI-X registers use base index 3. Treating all offsets as belonging to one base would produce incorrect MMIO addresses.

The PF `SYSPFVFDEC[0..255]` symbols are commented out while the VF-specific `SYSPFVFDEC` symbols are active. Code expecting generic `mmBIF_BX_PF_MM_INDEX` names from another generation would not compile against this header and should use the generation-appropriate names.

The Syshub block uses `ix` indirect offsets, not `mm` direct offsets with `_BASE_IDX` companions. Consuming code must use the correct indirect access mechanism and should not treat those numeric values as ordinary direct MMIO offsets.

## Test Signals

The header itself is normally validated through build coverage and hardware or simulator execution rather than unit tests. Useful signals include:

- Successful compilation of NBIO 6.1 AMDGPU code that references the `mm...`, `_BASE_IDX`, and `ix...` names.
- Register access traces showing expected base-index expansion for base indices 0, 2, and 3.
- BACO and power-management tests that exercise BACO exit timing and VDDGFX status/window registers without timeout regressions.
- Doorbell and HDP flush tests that verify doorbell ranges, aperture programming, flush request/done handshakes, and transaction-pending polling.
- SR-IOV validation with VF0 through VF15 covering per-VF MMIO index/data access, mailbox transmit/receive paths, VM/HV mailbox signaling, and isolation from PF state.
- Interrupt tests that program RCC graphics MSI-X vector address/data/control registers and observe expected interrupt delivery and pending-bit behavior.
- Syshub clock-gating/QoS/idle tests or hardware bring-up logs that confirm indirect Syshub offsets are reached through the right access path.

Because this chunk ends the header, merged research should connect it with earlier chunks for the full NBIO 6.1 register map and with the matching shift/mask file for bit-level semantics.
