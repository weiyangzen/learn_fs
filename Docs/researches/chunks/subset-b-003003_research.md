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
