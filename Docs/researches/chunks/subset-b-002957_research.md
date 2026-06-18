# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 10001-12430

## Scope

This chunk is generated AMD NBIO 4.3.0 register offset metadata. It contains C preprocessor constants only: each `reg*` macro gives a SOC15-style register/config-space index and each matching `*_BASE_IDX` macro gives the base aperture index, which is `5` throughout this range. There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches here.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata, not Ceph filesystem code.

The selected lines cover 2,399 `#define` entries:

- The tail of `BIF_CFG_DEV0_EPF0_VF15`, starting at the MSI-X PBA base-index line and continuing through vendor-specific, AER, TLP prefix log, and ARI capability offsets for virtual function 15.
- The complete visible `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` block at base address `0x10141000`, including normal PCI configuration header registers, MSI/MSI-X, PCIe capability, AER, device serial number, ACS, PASID, ARI, ATS, PRI, LTR, SR-IOV, resize-BAR, and VF resize-BAR capability offsets.
- The `EPF2` block at `0x10142000` and `EPF3` block at `0x10143000`, each with a PCI configuration header, MSI/MSI-X, PCIe capability, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, and ARI offsets.
- RCC port decode blocks for `DEV0_1` at base `0x10131000`, split across common RCC, endpoint, downstream, and downstream-port register groups.
- The beginning of the PCIe MSI-X vector table at base `0x10170000`, defining vectors 0 through 172. Each complete vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` offsets. The file continues with vector 173 after this chunk.

## Purpose

`nbio_4_3_0_offset.h` supplies symbolic register offsets for the NBIO/NBIF/PCIe portion of AMD GPUs using the NBIO 4.3.0 IP. AMDGPU code pairs these offsets with `nbio_4_3_0_sh_mask.h` field macros and SOC15 access helpers so driver code can name hardware registers without embedding raw offsets.

This chunk focuses on the PCIe configuration and interrupt-delivery surface for additional endpoint functions and virtual functions:

- `BIF_CFG_DEV0_EPF*` macros model PCI-compatible configuration-space registers for device 0 endpoint functions 1 through 3 and the tail of physical function 0 virtual function 15.
- MSI and MSI-X capability offsets expose interrupt address/data/mask/pending control for each function.
- AER, device serial, ACS, PASID, ATS, PRI, ARI, LTR, SR-IOV, resize-BAR, power-budget, and DPA capability offsets describe PCIe feature and error-reporting state.
- RCC register offsets expose root-complex/endpoint/downstream-port controls around VDM support, bus/link control, requester-ID restore, LTR, margining, DPA, PME, error control, RX/TX control, link speed, and strap registers for the `DEV0_1` port view.
- `PCIEMSIX_VECTn_*` offsets describe the hardware MSI-X table entries used to route interrupt vectors by programming a message address, message data, and vector control word.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `regBIF_CFG_DEV0_EPF1_*`, `regBIF_CFG_DEV0_EPF2_*`, and `regBIF_CFG_DEV0_EPF3_*` name PCI configuration registers for endpoint functions 1, 2, and 3.
- `regBIF_CFG_DEV0_EPF0_VF15_*` names the final PCIe capability registers for virtual function 15 of endpoint function 0. This chunk starts mid-family, so earlier VF15 header/MSI fields are in the previous chunk.
- `regRCC_DEV0_1_*`, `regRCC_EP_DEV0_1_*`, `regRCC_DWN_DEV0_1_*`, and `regRCC_DWNP_DEV0_1_*` name RCC and PCIe port-control registers for the device 1/port 1 view.
- `regPCIEMSIX_VECT0_*` through `regPCIEMSIX_VECT172_*` name MSI-X vector-table entries. The vector stride is regular: vector `n` starts at `0x1c000 + 4*n`, with address low/high, message data, and control at consecutive DWORD offsets.
- `*_BASE_IDX` is always `5` in this range and must be preserved by SOC15 addressing code.

AMDGPU consumers normally use these offset macros through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and register-table macros. Bit packing and extraction come from the sibling `nbio_4_3_0_sh_mask.h` header, not from this offset file.

High-signal register groups include:

- PCI config header fields: vendor/device ID, command/status, revision/class codes, BARs, ROM BAR, capability pointer, interrupt line/pin, and adapter/vendor capability registers.
- PCIe core capability fields: `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and their PCIe capability 2 variants.
- Interrupt capability fields: MSI capability/control/address/data/mask/pending registers, MSI-X capability/control/table/PBA offsets, and the separate physical MSI-X vector-table offsets.
- Error and logging fields: AER capability list, uncorrectable/correctable error status/mask/severity, AER control, header logs, and TLP prefix logs.
- Virtualization and isolation fields: SR-IOV, VF BAR/VF resize BAR, ATS, PRI, PASID, ACS, and ARI capability/control registers.
- Power-management fields: PMI, LTR, DPA, power-budget, and RCC LTR/PME controls.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU and kernel PCI/interrupt paths:

1. NBIO 4.3.0-specific code includes this offset header and usually `nbio_4_3_0_sh_mask.h`.
2. The driver selects the NBIO hardware block and instance, then passes a `reg*` macro and its base-index information through SOC15 helpers.
3. Runtime code reads or writes the selected NBIO register to initialize PCIe/NBIO features, control doorbells and interrupts, program ASPM/LTR behavior, perform reset/resume setup, or inspect status/error state.
4. For MSI-X delivery, platform and driver code program PCI/MSI-X config state and vector table entries so interrupts target the intended CPU interrupt remapping address/data. The macros in this slice name that hardware table, but do not define the allocation policy or interrupt handling logic.

Concrete integration in this tree includes `amdgpu/nbio_v4_3.c`, which includes this header and uses nearby NBIO offsets for revision ID, memory-size reads, doorbell ranges, interrupt control, clock gating, HDP flush offsets, PCIe index/data access, ROM offset, ASPM/LTR programming, and NBIO initialization. Within this exact chunk, `nbio_v4_3_init_registers()` reads and writes `regRCC_DEV0_EPF2_STRAP2` to clear the `STRAP_NO_SOFT_RESET_DEV0_F2` bit for NBIO 4.3.0 hardware. Other code paths include the same header from SMU 13 PPT files and DCN32/DCN321 resource code, tying these offsets to power-management and display-resource bring-up.

The header does not encode access ordering, config-space side effects, write-one-to-clear rules, interrupt masking semantics, reset persistence, privilege restrictions, or whether a register is firmware-, platform-, or OS-owned. Those rules live in the consuming driver code, PCIe specification behavior, firmware protocols, and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware state in NBIO/NBIF PCIe configuration, RCC port-control, and MSI-X table blocks.

The represented hardware state falls into several categories:

- PCI configuration state that is visible to or coordinated with the OS PCI core: command/status, BARs, ROM BAR, capability lists, device/link controls, MSI/MSI-X controls, AER status/mask/severity, ACS/PASID/ARI/ATS/PRI, SR-IOV, and resize-BAR controls.
- Interrupt routing state: MSI address/data/mask/pending registers, MSI-X table and PBA offsets in config space, and the physical `PCIEMSIX_VECTn_*` table entries. These persist until reprogrammed, function reset, device reset, suspend/resume restore, virtualization handoff, or platform/firmware intervention.
- Link and power state: LTR, DPA, power budget, PME, link speed/control, ASPM-related RCC controls, and strap/margining registers. Some are latched from straps or only valid under specific link/reset states.
- Error and diagnostic state: AER status and log registers, RCC error controls/status, scratch registers, requester-ID restore, RX/TX controls, and link margining/status fields. Some status bits may be sticky or clear-on-write depending on the register definition.
- Virtualization state: VF capability/register windows and SR-IOV/VF BAR controls are sensitive to PF/VF ownership and hypervisor-mediated restore. The chunk starts in the middle of VF15 and covers function-level SR-IOV controls for EPF1.

Persistence is hardware-defined. Configuration and vector-table entries can survive across normal driver operations but are commonly reinitialized during probe, function-level reset, GPU reset, suspend/resume, or SR-IOV transitions. The file does not distinguish read-only, read/write, write-trigger, sticky-status, strap-latched, or reserved registers, so consumers must not infer write safety from the existence of an offset macro.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register family remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h` supplies bitfield masks and shifts for the registers named here.
- Other chunks of `nbio_4_3_0_offset.h` define the rest of EPF0, VF windows, NBIO control/status, doorbell, HDP, interrupt, and remaining MSI-X vector offsets.
- SOC15 helper macros translate `(NBIO block, instance, reg macro)` pairs into actual MMIO/config aperture addresses.
- Linux PCI/MSI-X infrastructure owns parts of config-space and vector programming, while AMDGPU NBIO code programs device-specific controls around it.

Primary integration points are:

- `amdgpu/nbio_v4_3.c`: NBIO initialization, revision/memsize reads, MC access enable, doorbell range programming, interrupt control, HDP flush remapping, clock gating, ASPM/LTR programming, ROM offset reads, and SR-IOV-specific register remap behavior.
- SMU 13 PPT code (`smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`): includes NBIO 4.3.0 offsets for power-management and PCIe/NBIO coordination.
- Display resource code (`dcn32_resource.c` and `dcn321_resource.c`): includes this register family for display/NBIO interaction on matching ASICs.
- Interrupt handling and resume paths: MSI/MSI-X capability and table state interacts with `amdgpu_irq.c`, PCI core MSI-X enable/disable behavior, and SR-IOV/QEMU restore paths.
- Virtualization and reset paths: EPF/VF config registers, SR-IOV capabilities, VF BARs, and `RCC_DEV0_EPF2_STRAP2` affect function reset and VF/PF behavior.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong offset or base index compiles cleanly but sends reads/writes to the wrong PCIe/NBIO register.
- This chunk has artificial boundaries. It starts mid-VF15 and ends mid-MSI-X vector table after vector 172, so the final per-file research must merge adjacent chunks to complete those families.
- All entries here use base index `5`. Code that drops or substitutes the base index can address another SOC15 aperture even if the offset value looks correct.
- Many names are PCI-standard concepts but are exposed through AMD's NBIO MMIO/config aperture. Confusing Linux PCI config-space access with SOC15 NBIO register access can bypass expected ownership or locking.
- MSI-X table entries are high risk. Stale or wrong `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, or `CONTROL` values can lose interrupts, target the wrong interrupt remapping entry, or break resume/SR-IOV interrupt delivery.
- AER status/log registers may be sticky or clear-on-write. Blind writes during diagnostics or reset can lose error evidence.
- SR-IOV, ATS, PRI, PASID, ACS, ARI, and VF BAR registers are isolation-critical. Wrong offsets or unsafe writes can expose DMA isolation bugs, bad requester IDs, broken PASID routing, or incorrect VF memory windows.
- Link-power controls such as LTR, DPA, power budget, PME, link speed, ASPM-related RCC controls, and strap registers are topology- and firmware-sensitive. Incorrect programming may cause link instability, performance loss, or resume failures.
- Repeated EPF2/EPF3 and MSI-X vector layouts invite generator or manual copy errors. Static checks should verify regular spacing and structurally identical families where the hardware requires that.
- Some registers are strap-latched or reset-sensitive. Writing them after boot may not have the intended effect, and some writes may require link quiescence, function reset, or firmware coordination.

## Test Signals

Useful validation signals include:

- Kernel build coverage for AMDGPU paths that include `nbio_4_3_0_offset.h`, especially `nbio_v4_3.c`, SMU 13 PPT files, and DCN32/DCN321 resource code.
- Generated-data comparison against AMD's authoritative NBIO 4.3.0 register database, checking every `reg*` value and `*_BASE_IDX` in this slice.
- Static consistency checks that every offset macro has a matching base-index macro, all entries in this chunk use base index `5`, EPF2 and EPF3 capability layouts stay aligned, and `PCIEMSIX_VECTn_*` offsets keep the regular 4-DWORD stride.
- Cross-checks with `nbio_4_3_0_sh_mask.h` to ensure field masks exist for registers that consumers modify, such as RCC straps, PCIe capability controls, AER fields, and MSI/MSI-X control registers.
- Boot/probe tests on NBIO 4.3.0 hardware confirming PCI enumeration, BAR sizing, MSI/MSI-X enablement, interrupt delivery, doorbells, HDP flush, ROM offset, and memory-size reporting.
- Suspend/resume and GPU reset tests, including SR-IOV VF scenarios, that verify MSI-X vectors are restored and function/config-space state remains consistent.
- PCIe error-injection or AER tests that verify correct uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs.
- Virtualization tests for SR-IOV, VF BAR sizing, PASID/ATS/PRI/ACS/ARI behavior, and guest interrupt delivery.
- Link-power tests for ASPM/LTR/DPA/PME behavior, including high-load PCIe traffic, idle transitions, and resume from low-power states.
- Regression indicators include missing interrupts, MSI-X vectors targeting stale addresses, PCIe AER storms or missing error logs, failed function reset, VF enumeration failures, bad BAR sizing, link retraining instability, resume hangs, or NBIO register access warnings.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002957`. It covers lines 10001-12430 of `nbio_4_3_0_offset.h`. Adjacent chunks are required to complete the preceding `BIF_CFG_DEV0_EPF0_VF15` family and the following `PCIEMSIX_VECT173+` table, and the final per-file document should reconcile this PCIe/config/MSI-X slice with the rest of the NBIO 4.3.0 register map.
