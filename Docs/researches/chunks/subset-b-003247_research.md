# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 2423-4876

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 register-offset header segment. It contains preprocessor constants only: no functions, structs, enums, executable statements, locks, allocations, or software-owned storage. The range defines 2,382 macros over 2,454 source lines; 734 of those are companion `_BASE_IDX` constants used by SOC15 register helpers to select the NBIO base aperture.

The range starts in the tail of the `nbio_pcie0_bifplr2_cfgdecp` PCIe configuration-space block, covers full `cfgBIFPLR3`, `cfgBIFPLR4`, and `cfgBIFPLR5` PCIe config-space windows, then covers NBIF/BIF/RCC/GDC register blocks and the beginning of the `BIF_CFG_DEV2_RC0` config-space window. Adjacent chunks are needed for the beginning of `cfgBIFPLR2` and the remainder of `BIF_CFG_DEV2_RC0`.

## Purpose

`nbio_7_7_0_offset.h` is the address half of AMD's generated NBIO 7.7.0 register interface. It gives C code stable macro names for NBIO, BIF, RCC, GDC, and PCIe configuration registers so call sites do not hard-code numeric offsets. The matching `nbio_7_7_0_sh_mask.h` supplies field shifts and masks; this file supplies register locations and base-index metadata.

This chunk maps several classes of hardware-visible state:

- PCIe root-port or link-register config spaces (`cfgBIFPLR2` tail plus full `cfgBIFPLR3/4/5`) with standard PCI config header fields, PCIe capabilities, AER, ACS, multicast, L1 PM substates, DPC, ESM, DLF, 16 GT/s and 32 GT/s link capability registers, CCIX capability registers, equalization controls, and per-lane margining controls.
- NBIF/BIF indexed access, scratch, interrupt, MMIO remap, HDP flush, doorbell, ring buffer, mailbox, GPU IOV, address-LUT, and pad-control registers.
- RCC strap, endpoint, downstream-port, downstream-path, PF/VF, and MSIX register blocks used for revision straps, config/memory sizing, PCIe behavior, error logging, bus numbering, requester ID, peer apertures, doorbell aperture enablement, and interrupt vector programming.
- GDC doorbell and clock/power/control registers, including SDMA, CSDMA, IH, VCN, RLC, ATDMA, SDP, and NGDC power-gating controls.
- Root-complex config decode registers for `DEV0`, `DEV1`, and the beginning of `DEV2`, with 32-bit register offsets and shared base index 5.

Although this repository path is under a `ceph-client` source mirror, the file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The `cfgBIFPLR*` families describe byte offsets in PCIe configuration space. `cfgBIFPLR2` is only the high tail in this chunk: 16 GT/s lane equalization lanes 5-15, PCIe margining enhanced capability and per-lane control/status registers, CCIX/ESM capability and control registers, 20 GT/s and 25 GT/s ESM equalization registers, and 32 GT/s link capability/control/status. `cfgBIFPLR3`, `cfgBIFPLR4`, and `cfgBIFPLR5` repeat the full root-port-style layout from vendor/device IDs through extended PCIe capabilities, AER logs, lane equalization, ACS, multicast, L1 PM substates, DPC/PIO logs, ESM/DLF, 16 GT/s and 32 GT/s capability sets, CCIX, and lane margining.

The `regBIF_BX_PF0_MM_*` and `regBIF_BX_PF0_RSMU_*` constants expose PF-scoped indirect index/data windows. In `nbio_v7_7.c`, these become `get_pcie_port_index_offset` and `get_pcie_port_data_offset`, so higher AMDGPU code can reach PCIe-port/RSMU-style register spaces through the NBIO function table.

The `regBIF_BX0_*` SYSDEC block contains PCIe index/data windows, SBIOS/BIOS scratch registers, RLC/VCE/UVD interrupt controls, MMIO register CAM and remap tables, bus and interrupt controls, feature controls, BIF framebuffer enable, address LUTs, HDP remap controls, ring buffer registers, mailbox index, GPU IOV sizing, and external pad controls. `nbio_v7_7.c` directly uses `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, `regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL`, and `regBIF_BX0_REMAP_HDP_REG_FLUSH_CNTL`.

The `regRCC_STRAP0_*` block records BIF, port, and endpoint-function strap registers for dev0. The NBIO 7.7 implementation reads `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and uses a matching shift/mask macro to derive the GPU revision ID. These strap values are also natural integration points for link policy, device identity, and firmware/BIOS-programmed hardware configuration.

The RCC endpoint/downstream blocks (`regRCC_EP_DEV0_0_*`, `regRCC_DWN_DEV0_0_*`, `regRCC_DWNP_DEV0_0_*`, `regRCC_DEV0_EPF0_0_*`, and `regRCC_DEV0_0_*`) map PCIe endpoint and root-complex control state: PCIe scratch/config/error/interrupt controls, DPA power allocation, downstream link/config straps, LTR message info, function identifiers, doorbell aperture enable, config memory size, RCC error logs, bus-number lists, requester-ID restore, peer framebuffer offsets, GPU host-VM enablement, GPUIOV region, margin parameters, and reset enablement.

The BIF BIFDEC and PF blocks (`regBIF_BX0_*` and `regBIF_BX_PF0_*`) are high-value runtime integration points. They include BME and atomic error logs, doorbell self-ring GPA aperture base/control registers, HDP coherency flush and invalidate controls, GPU HDP flush request/done registers, transaction-pending status, address-LUT bypass, mailbox message buffers, mailbox interrupt control, and VM/HV mailbox registers. `nbio_v7_7.c` uses the doorbell self-ring aperture registers, HDP flush request/done offsets, HDP coherency flush remap fallback, and transaction-related flush masks from the same register family.

The `regRCC_DEV0_EPF0_0_GFXMSIX_*` block maps four graphics MSI-X vectors and the pending-bit array, including address low/high, message data, and vector control offsets. This block is register-address metadata for interrupt routing and GPU interrupt table programming.

The `regGDC0_*` block maps GDC and doorbell registers at base address `0x1400000`: SDP port controls, medium-grain clock gating, SOCCLK SDP controls, doorbell status, SDMA0/SDMA1/IH/VCN0/RLC/CSDMA doorbell ranges, ATDMA miscellaneous control, doorbell fence control, S2A miscellaneous control, and NGDC power-gating controls. `nbio_v7_7.c` programs CSDMA, VCN0, and IH doorbell ranges through these offsets.

The `regBIF_CFG_DEV0_RC0_*`, `regBIF_CFG_DEV1_RC0_*`, and partial `regBIF_CFG_DEV2_RC0_*` families are dword-addressed config decode windows at base addresses `0x10100000`, `0x10101000`, and `0x10102000`. They mirror standard PCI/PCIe config fields but collapse byte/word fields onto 32-bit register offsets. DEV0 and DEV1 are complete through lane 15 margining status in this chunk; DEV2 begins at vendor/device IDs and stops at `SLOT_CNTL2`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `cfgBIFPLR*_*` constants are PCI configuration-space byte offsets for BIF PCIe logical root-port windows.
- `reg...` constants are SOC15/NBIO register offsets.
- `reg..._BASE_IDX` constants select the base entry used by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and display `NBIO_BASE(...)` style helper macros.

The macros are untyped integer literals. They do not encode access permissions, reset values, read/write width, side effects, field layout, write-one-to-clear behavior, or sequencing rules. Consumers must combine them with the matching shift/mask header and AMDGPU register access helpers.

## Control Flow

This header has no local runtime control flow. Runtime flow is imposed by AMDGPU call sites:

1. ASIC-specific code includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. Code chooses a macro from this header and resolves it into an MMIO address through `SOC15_REG_OFFSET`, direct SOC15 read/write helpers, PCIe-port helpers, or generated display-resource base macros.
3. For field updates, code reads a register, uses the sibling shift/mask macros through `REG_SET_FIELD` or `REG_GET_FIELD`, then writes the register back while preserving unrelated bits.
4. For doorbell, HDP flush, interrupt, PCIe config, strap, reset, or error-log state, hardware sequencing and polling behavior are owned by the consuming driver code and the NBIO hardware specification, not by this header.

Concrete NBIO 7.7 flows in this tree include HDP flush remapping, revision-ID extraction from RCC straps, MC framebuffer access enablement, memory-size reads, CSDMA/VCN/IH doorbell range programming, doorbell aperture enablement, self-ring doorbell aperture programming, IH interrupt control, PCIE index/data offset publication, HDP flush request/done offset publication, clock/power register initialization, and MMIO remap setup.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names MMIO-backed hardware state in NBIO 7.7.

State represented by this chunk includes PCIe config-space identity/capability/error/status registers, link equalization and margining controls, CCIX/ESM/DLF/DPC/ACS capability state, BIOS scratch and mailbox registers, MMIO remap windows, address LUTs, HDP coherency and flush state, doorbell aperture and range state, GPU IOV sizing, strap-derived device/link policy, PCIe/RCC error logs, bus-number and requester-ID routing state, peer aperture offsets, GDC clock/power controls, and MSI-X vector table/PBA state.

Persistence is hardware-defined. Some values are strap or firmware initialized, some are operating-system PCI config state, some are live status latches, and some are ordinary writable MMIO controls. Values may be reset or retained differently across function-level reset, BACO, PCIe hot/warm reset, GPU reset, suspend/resume, power gating, driver reinitialization, or host firmware handoff. Error logs, pending bits, HDP flush request/done registers, doorbell ranges, and MSI/MSI-X programming are especially sensitive to reset/resume ordering.

## Dependencies And Integration Points

The direct sibling dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, which provides field geometry for many registers named here. Other generated NBIO 7.7 headers provide related registers outside this chunk.

The main direct consumer in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`. It includes this header and exports `nbio_v7_7_funcs`, which wires offsets from this chunk into the common `amdgpu_nbio_funcs` interface. Important direct uses include:

- `regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL` and `regBIF_BX0_REMAP_HDP_REG_FLUSH_CNTL` for HDP remap setup.
- `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` for revision ID extraction.
- `regGDC0_BIF_CSDMA_DOORBELL_RANGE`, `regGDC0_BIF_VCN0_DOORBELL_RANGE`, and `regGDC0_BIF_IH_DOORBELL_RANGE` for doorbell aperture assignment.
- `regRCC_DEV0_EPF0_0_RCC_DOORBELL_APER_EN` for global doorbell aperture enablement.
- `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_LOW`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, and `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL` for self-ring doorbell setup.
- `regBIF_BX_PF0_GPU_HDP_FLUSH_REQ`, `regBIF_BX_PF0_GPU_HDP_FLUSH_DONE`, and `regBIF_BX_PF0_HDP_MEM_COHERENCY_FLUSH_CNTL` for HDP flush and MMIO remap behavior.
- `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, `regBIF_BX_PF0_RSMU_INDEX`, and `regBIF_BX_PF0_RSMU_DATA` for PCIe/indexed register access.

Display resource files in nearby DCN families also use the broader `regBIF_BX0_*` macro pattern through `NBIO_BASE(regBIF_BX0_*_BASE_IDX) + regBIF_BX0_*`, so base-index drift in this generated header can affect display-side register address construction even when the NBIO core file is not the direct caller.

## Risks And Edge Cases

- Offset drift is silent at compile time when macro names remain stable. A wrong numeric offset or base index can read or write the wrong MMIO register while all C code still builds.
- The chunk begins and ends mid-address-space coverage. `cfgBIFPLR2` and `BIF_CFG_DEV2_RC0` are incomplete here; whole-file research must merge adjacent chunks before making complete claims about those register families.
- PCIe config offsets mix byte-addressed `cfgBIFPLR*` names with dword-style `regBIF_CFG_DEV*_RC0_*` decode windows. Consumers must use the access path expected by the macro family.
- Several macro names intentionally share the same numeric offset because multiple fields reside in the same dword, for example vendor/device ID or command/status. This is normal for register-address metadata but can look like duplication in mechanical checks.
- Doorbell and HDP registers are performance and correctness sensitive. Incorrect doorbell range size/offset, aperture base, or HDP flush request/done address can cause missed interrupts, hung queues, stale CPU/GPU memory visibility, or broken KFD interactions.
- Strap and PCIe policy registers are firmware/hardware-contract sensitive. Reprogramming them outside documented initialization paths can alter device identity, link behavior, bus numbering, requester IDs, or virtualization behavior.
- Error-log, BME, atomic, transaction-pending, MSI-X, and mailbox registers can be live or write-sensitive. Read/modify/write code must preserve reserved bits and handle clear-on-write or hardware-updated state correctly.
- GDC clock/power and doorbell registers can interact with runtime power management. Writes during power transitions or without required clock domains may fail or create resume-only bugs.
- Repeated DEV0/DEV1/DEV2 and BIFPLR3/4/5 layouts are copy/generation sensitive. A one-lane or one-device offset error can surface only on specific PCIe port, function, or lane configurations.

## Test Signals

Useful validation combines generated-header checks with hardware-oriented AMDGPU tests:

- Build AMDGPU with NBIO 7.7 support enabled. Direct macro consumers in `nbio_v7_7.c` should catch missing or renamed symbols.
- Mechanically verify that each `reg...` symbol in this chunk has the expected `_BASE_IDX` companion where SOC15 access requires one, and that base indices match the address block: PF MMIO/RSMU windows use 0/1, RCC/BIFDEC blocks mostly use 2, MSIX/GDC blocks use 3, and `BIF_CFG_DEV*_RC0` uses 5.
- Cross-check the generated offsets against AMD's authoritative NBIO 7.7.0 register database and the sibling shift/mask header so every active field layout maps to a valid address.
- Exercise boot, GPU reset, suspend/resume, runtime power management, PCIe link retraining, FLR, and AER/error paths on NBIO 7.7 hardware.
- Validate doorbell users by running SDMA, CSDMA, VCN, IH interrupt, RLC, and KFD/compute workloads; watch for missed doorbells, queue hangs, interrupt storms, or incorrect doorbell status.
- Validate HDP coherency by running CPU/GPU shared-memory and KFD workloads that require HDP flush/invalidate ordering; stale reads or hangs point at remap/flush offset problems.
- Check PCIe config-visible behavior with `lspci`, AER logs, MSI/MSI-X operation, link speed/width, L1 PM substates, DPC, ACS, and lane margining/equalization diagnostics where available.
- For virtualization/SR-IOV scenarios, test PF/VF isolation, doorbell self-ring aperture behavior, BME/atomic error handling, mailbox messaging, and FLR/recovery behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of `cfgBIFPLR2`, including the standard header and earlier PCIe capability offsets. The next chunk owns the remainder of `BIF_CFG_DEV2_RC0` after `SLOT_CNTL2`, including DEV2 MSI, PCIe extended capabilities, AER, lane equalization, margining, and higher-speed link registers. The final per-file report should reconcile those boundaries before summarizing complete NBIO 7.7 PCIe config-space coverage.
