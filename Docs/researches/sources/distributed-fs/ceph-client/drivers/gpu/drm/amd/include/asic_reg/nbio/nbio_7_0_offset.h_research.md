# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003066`: lines 1-2428, `Docs/researches/chunks/subset-b-003066_research.md`
- `subset-b-003067`: lines 2429-4642, `Docs/researches/chunks/subset-b-003067_research.md`

## Chunk Research

### subset-b-003066: lines 1-2428

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h lines 1-2428

## Purpose

This chunk is the first half of AMDGPU's generated NBIO 7.0 register-offset header. It maps symbolic PCI/NBIO configuration-register names to byte offsets within multiple NBIO address blocks. The file is hardware metadata, not executable driver logic: callers include it so SOC15/NBIO register access macros can use stable names instead of literal offsets.

The covered range starts with the AMD/MIT license and include guard, then defines address blocks for the NB northbridge config space, IOMMU L2 config space, NBIF root-complex config spaces, dummy PCIe config functions, GPU endpoint-function config spaces, and the start of the `nbio_pcie0_bifplr0_cfgdecp` block. The chunk ends inside the `cfgBIFPLR0_0` PCIe root/bridge-like block at `cfgBIFPLR0_0_PCIE_TLP_PREFIX_LOG2`; later chunks own the rest of that block and the final include guard close.

All address-block comments in this chunk list base address `0x0`. The constants therefore represent offsets relative to the access aperture or base chosen by the caller, not standalone CPU physical addresses.

## Important APIs, Types, and Macros

There are no C functions, structs, typedefs, or enums in this range. The public interface is a large set of `#define` constants whose names encode the hardware function and register, with values such as `0x0000`, `0x00a0`, or `0x0400`.

Important macro families and address blocks in lines 1-2428 are:

- Include guard: `_nbio_7_0_OFFSET_HEADER`.
- `nbio_iohub_nb_nbcfg_nb_cfgdec` / `cfgNB_NBCFG0_*` at lines 26-76: NB PCI config identity/status, adapter ID, SMN index/data windows, scratch registers, DRAM slot bounds, mutexes, and a performance counter control offset.
- `nbio_iohub_iommu_l2_iommul2cfg` / `cfgIOMMU_L2_0_*` at lines 77-125: IOMMU PCI config identity, capability pointers, MSI fields, MMIO control/range fields, poison/stall controls, and SMMU ID registers.
- `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and `dev1_rc` / `cfgBIF_CFG_DEV{0,1}_RC0_*` at lines 126-377: two root-complex-style PCIe config layouts. They cover standard PCI header fields, bridge windows, PM/PCIe/MSI/SSID/MSI-map capabilities, vendor-specific capability offsets, VC capability offsets, AER registers, secondary capability offsets, lane equalization controls for lanes 0-15, and ACS capability/control.
- `nbio_iohub_nb_pciedummy{0,1}_pciedummy_cfgdec` / `cfgNB_PCIEDUMMY{0,1}_0_*` at lines 378-395: tiny dummy PCIe config functions with vendor/device, status/command, class/revision, and header-type offsets.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` at lines 396-901: endpoint function 0 exposed mostly through generic `cfg*` names such as `cfgVENDOR_ID`, `cfgDEVICE_ID`, `cfgPCIE_*`, and `cfgPCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*`. This block includes the richest endpoint layout in the chunk: BARs, ROM, PM, PCIe, MSI/MSI-X, AER, BAR enhanced capability, power budget, DPA, secondary/link/lane controls, ACS, ATS, PRI, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, and GPU IOV vendor-specific mailbox/frame-buffer/scheduler offsets. It also contains a commented-out duplicate set of `cfgBIF_CFG_DEV0_EPF0_*` aliases, so those commented rows do not create macros.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` / `cfgBIF_CFG_DEV0_EPF1_0_*` at lines 902-1156: a named copy of the endpoint function layout with the same broad PCIe/SR-IOV/GPU-IOV coverage as EPF0.
- `nbio_nbif0_bif_cfg_dev0_epf2` through `epf7` / `cfgBIF_CFG_DEV0_EPF{2..7}_0_*` at lines 1157-1918: six smaller endpoint-function maps. They include the standard PCI header, BARs, PM, USB/SATA-like capability offsets (`SBRN`, `FLADJ`, `DBESL_DBESLD`, `SATA_*`, `SATA_IDP_*`), PCIe, MSI/MSI-X, AER, BAR enhanced capability, power budget, DPA, ACS, and ARI.
- `nbio_nbif0_bif_cfg_dev1_epf0` / `cfgBIF_CFG_DEV1_EPF0_0_*` at lines 1919-2074: endpoint function 0 for device 1. It includes standard endpoint fields, MSI/MSI-X, AER, BAR capability, DPA/power-budget controls, and PCIe secondary/lane equalization fields through lane 15 plus ACS/ARI.
- `nbio_nbif0_bif_cfg_dev1_epf1` and `epf2` / `cfgBIF_CFG_DEV1_EPF{1,2}_0_*` at lines 2075-2328: smaller device 1 endpoint-function maps similar to device 0 EPF2-EPF7.
- `nbio_pcie0_bifplr0_cfgdecp` / `cfgBIFPLR0_0_*` at lines 2329-2428: the beginning of a bridge/root-port-like PCIe config block. This chunk covers identity, bridge windows, PM/PCIe/MSI/SSID/MSI-map/vendor-specific/VC/AER fields, and ends in the AER TLP prefix log offsets.

The constants are normally paired with companion generated headers:

- `nbio_7_0_sh_mask.h` supplies field masks and shifts for bit manipulation.
- `nbio_7_0_default.h` supplies default/reset values for many registers.
- `nbio_7_0_smn.h` supplies SMN register identifiers for non-config-space NBIO access.
- ASIC IP offset headers such as `vega10_ip_offset.h` define NBIO/NBIF base segments consumed by access macros.

## Control Flow and Runtime Behavior

This chunk has no branches, loops, function calls, or direct runtime behavior. Its "control flow" is compile-time symbol substitution: when a driver source refers to one of these macros, the preprocessor replaces it with a numeric offset.

The runtime behavior is in callers that combine these offsets with the correct base and access path. In this tree, the header is included by `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, `pm/powerplay/hwmgr/smu10_inc.h`, and `display/dc/resource/dcn10/dcn10_resource.c`. Those consumers use AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and display register macros. The offsets here influence NBIO/PCIe features such as doorbell apertures, HDP flush remapping, interrupt setup, memory-size reads, clock gating, PCIe performance counters, reset handling, display NBIO register addressing, and SMU10 register definitions.

For the PCIe configuration layouts, the implied hardware access sequence is:

1. Select the correct NBIO instance/function/base through the SOC15/NBIO/NBIF access layer.
2. Add the generated byte offset for the target config register.
3. Read or write through the driver helper.
4. Use the companion shift/mask header to preserve unrelated bits or decode fields where needed.

The repeated root-complex and endpoint-function blocks do not call each other. Their shared structure reflects multiple PCI functions with similar config-space layouts.

## State and Persistence

The header owns no memory, allocates nothing, performs no I/O, and persists no software state. The state represented by its constants lives in NBIO/PCIe/IOMMU hardware registers.

State classes represented in this chunk include:

- PCI identity and enumeration state: vendor/device IDs, class/revision, header type, BARs, ROM BAR, capability pointers, bus numbers, bridge memory/IO/prefetchable windows, and subsystem/adapter IDs.
- Control and enable state: command/status registers, PM control/status, PCIe device/link/slot/root controls, MSI/MSI-X controls, MSI-map controls, ACS/ATS/PRI/PASID/ARI/SR-IOV controls, BAR enhanced controls, DPA controls, GPU-IOV interrupt/reset/mailbox/context controls, and SMN index/data windows.
- Status and diagnostic state: PCI/PCIe status, secondary status, AER corrected/uncorrected error status/masks/severity, header/TLP prefix logs, lane error/equalization registers, root error status/source ID, IOMMU/SMMU ID registers, and scratch registers.
- Virtualization state: SR-IOV VF counts/stride/device IDs/page sizes/VF BAR offsets plus GPU-IOV frame-buffer and scheduler partition offsets for up to 16 virtual functions in the richer EPF0/EPF1 maps.

Reset values, retention across suspend/resume, and write-one-to-clear behavior are not specified here. Those details come from hardware documentation, companion default/mask headers, and AMDGPU code that sequences NBIO initialization and reset.

## Dependencies and Integration Points

This header is tightly coupled to the rest of the generated NBIO 7.0 register set. It should be treated as one member of a generated family rather than edited independently.

Primary dependencies and consumers:

- `amdgpu/nbio_v7_0.c` includes this header with `nbio_7_0_default.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h`; it implements NBIO 7.0 operations for HDP flush remap, revision ID, framebuffer access enable, doorbell ranges, interrupt control, indirect SYSHUB access, clock gating/light sleep, and offset-return helpers.
- `amdgpu/soc15.c` includes this header as part of SOC15 common initialization and register access infrastructure for Vega/Raven/Arcturus-era ASICs.
- `pm/powerplay/hwmgr/smu10_inc.h` includes NBIO 7.0 offsets/defaults/masks alongside MP and THM register headers so SMU10 power-management code can use the same generated symbols.
- `display/dc/resource/dcn10/dcn10_resource.c` includes the header and uses NBIO/NBIF base-segment macros when defining display-resource register addresses.
- IP base headers such as `vega10_ip_offset.h` provide `NBIF_BASE`/`NBIO_BASE` segment constants that turn these relative offsets into register addresses for a specific ASIC.

The chunk is also integrated by naming convention. Code generation and callers expect prefix families (`cfgNB_NBCFG0`, `cfgIOMMU_L2_0`, `cfgBIF_CFG_DEV*_RC0`, generic `cfg*`, `cfgBIF_CFG_DEV*_EPF*_0`, and `cfgBIFPLR0_0`) to match hardware address-block names and companion mask/default symbols.

## Risks

- Offset drift is the main risk. A single wrong numeric offset can redirect a read/write to a different PCI config register or capability field while still compiling cleanly.
- The constants are byte offsets in PCI/config-space style blocks. Mixing them with MMIO dword offsets or SMN addresses without the correct access helper would produce wrong addresses.
- Several macros intentionally share an offset because PCI config layouts overlap 32-bit and 64-bit forms, for example MSI address/data/mask/pending aliases. Callers must use the layout appropriate to the enabled capability mode.
- `cfgBIF_CFG_DEV0_EPF0_*` aliases are present only as commented-out rows in this chunk. Code cannot rely on those names unless they are defined elsewhere; the live EPF0 names are the generic `cfgVENDOR_ID`, `cfgPCIE_*`, and related macros.
- The chunk ends inside `cfgBIFPLR0_0_*`, so whole-block assertions about `nbio_pcie0_bifplr0_cfgdecp` require the continuation chunk.
- Repeated endpoint blocks invite copy/paste or generator mistakes. EPF0/EPF1 have rich SR-IOV/GPU-IOV capability coverage, while EPF2-EPF7 and some device 1 functions are intentionally smaller; validation should not assume every EPF has identical register coverage.
- PCIe capability offsets control error reporting, lane equalization, ACS/ATS/PRI/PASID/SR-IOV, and virtualization paths. Bad offsets can surface as link-training failures, broken IOMMU translation, incorrect VF provisioning, interrupt failures, or hard-to-debug reset/resume issues.
- The header has no type safety. Any macro can be passed to the wrong register helper unless surrounding code enforces the correct NBIO block/access path.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware smoke coverage:

- Build AMDGPU with SOC15/NBIO 7.0, SMU10, and DCN10 paths enabled. This catches syntax errors and missing macro names referenced by C code.
- Compare all live `#define` names in this chunk against the generator source or hardware register database for NBIO 7.0. The 18 address-block ranges in lines 26-2428 should stay aligned with the documented block names and base address `0x0`.
- Cross-check companion headers so each register family that needs masks/defaults has corresponding entries in `nbio_7_0_sh_mask.h` and `nbio_7_0_default.h`, and SMN-only registers are not confused with config offsets.
- Mechanically verify repeated root-complex blocks `cfgBIF_CFG_DEV0_RC0_*` and `cfgBIF_CFG_DEV1_RC0_*` have matching offsets for equivalent names.
- Mechanically verify repeated endpoint-function blocks preserve intended symmetry: device 0 EPF2-EPF7 and device 1 EPF1-EPF2 should match their common subset, while EPF0/EPF1 rich blocks should include the SR-IOV/GPU-IOV ranges through `0x04f0`.
- Validate that intentionally overlapping offsets, such as MSI 32-bit/64-bit aliases, are documented or expected by the PCIe capability layout.
- On affected hardware, smoke-test GPU probe, PCI enumeration, BAR sizing, IOMMU setup, doorbell programming, MSI/MSI-X interrupt delivery, AER handling, PCIe link training/equalization, suspend/resume, GPU reset, SR-IOV/VF setup when supported, and display bring-up for DCN10 users.
- Runtime debug signals include successful `amdgpu` probe, correct reported memory size and revision ID, working HDP flush and doorbells, absence of PCIe AER spam, stable link speed/width, successful interrupt handling, and correct VF/resource partition reporting under virtualization.

## Chunk Boundary Notes

This chunk covers lines 1-2428 of a 4642-line header. It begins at the license/include guard and ends mid-address-block at `cfgBIFPLR0_0_PCIE_TLP_PREFIX_LOG2`. The final per-file research document should merge this with later chunks before claiming complete coverage for `nbio_7_0_offset.h`, especially for the remainder of `cfgBIFPLR0_0_*`, later PCIe blocks, and the closing `#endif`.

### subset-b-003067: lines 2429-4642

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h lines 2429-4642

## Purpose

This chunk is generated AMD NBIO 7.0 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic NBIO, BIF, PCIe, IOMMU, GDC, RCC, Syshub, and MSI-X register names to numeric offsets. Most `mm...` register offsets have a matching `mm..._BASE_IDX` selector, which is consumed by SOC15 register helpers to choose the correct base-address segment before adding the offset.

The requested range starts at the tail of `cfgBIFPLR0_0` PCIe capability offsets, then covers complete repeated PCIe root-port configuration blocks `cfgBIFPLR1_0` through `cfgBIFPLR6_0`, debug-port windows, IOMMU L2 MMIO registers, NBIF/SYS decode windows, RCC/PCIe endpoint and downstream control registers, BIF mailbox and doorbell registers, GDC registers, graphics MSI-X table offsets, and Syshub indirect-register offsets. It ends at the file's `#endif`.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or runtime branches in this range. The exported interface is the generated macro namespace:

- `cfg...`: PCI configuration-space offsets for NBIO PCIe root-port/root-complex style functions. These are byte offsets within configuration-space-like decode blocks and generally do not have `_BASE_IDX` companions in this chunk.
- `mm...`: MMIO register offsets for NBIO/BIF/IOMMU/RCC/GDC blocks.
- `mm..._BASE_IDX`: base-table selector paired with an `mm...` offset. SOC15 helpers use it as `adev->reg_offset[NBIO_HWIP][inst][reg_BASE_IDX] + reg`.
- `ix...`: indirect Syshub register indices written through `mmSYSHUB_INDEX` and read or written through `mmSYSHUB_DATA`.

The requested lines contain 2,122 `#define` entries: 1,085 `cfg...` macros, 968 `mm...` or `mm..._BASE_IDX` macros, 69 `ix...` macros, and 484 `_BASE_IDX` definitions.

Major address blocks in the chunk:

- `nbio_pcie0_bifplr1_cfgdecp` through `nbio_pcie0_bifplr6_cfgdecp`: six repeated PCIe port configuration maps. Each complete block has 169 offsets, from vendor/device/command/status fields through PCIe, MSI, SSID, MSI-map, vendor-specific, virtual-channel, serial-number, AER, lane equalization, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM capability areas.
- `nbio_dbgu0_dbgudec`: debug port address/data windows for ports A through D, including low/high address and data halves.
- `nbio_iohub_iommu_l2mmio_l2mmiocfg`: IOMMU L2 MMIO control, command, event, PPR, GA-log, device-table, completion-wait, MSI, error log, interrupt status, perf counter, and counter reporting offsets.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`, `SYSDEC`, and `syshubdec`: MM index/data windows, Syshub index/data windows, scratch, protection-fault aperture, remap, coherency-flush, interrupt, KIQ, semaphore, scratch, and MMIO-reg CAM offsets.
- `nbio_nbif0_rcc_*`: RCC strap, endpoint PCIe scratch/status/control, downstream PCIe error/LTR/control, function identifier, error interrupt, doorbell aperture, MSI-X, memory size, BIF framebuffer enable, PCIe index/data, and memory-hub arbitration offsets.
- `nbio_nbif0_bif_bx_pf_BIFDEC1` and `BIFPFVFDEC1`: BIF indirect access, doorbell aperture and range, remap HDP flush controls, interrupt controls, VM-ID request, ring-buffer, mailbox, GPUIOV configuration-size, pad-control, BME/atomic error, self-ring GPA aperture, HDP coherency flush, GPU HDP flush request/done, transaction-pending, mailbox buffer/control/interrupt, and VM/hypervisor mailbox offsets.
- `nbio_nbif0_gdc_GDCDEC`: NGDC/SHUB interface controls, SDMA/IH/MMSCH doorbell ranges, ATDMA/S2A/GDC miscellaneous and power-gating controls.
- `nbio_nbif0_rcc_dev0_BIFDEC2`: graphics MSI-X vector table entries and pending-bit array offsets.
- `syshub_mmreg_ind_syshubind`: indirect Syshub indices for SOC/shub clock domains, QoS/class controls, clock gating, idle/status, scratch/mask, and NIC400 fabric function-modifier registers.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMDGPU consumers:

1. ASIC-specific code includes `nbio_7_0_offset.h` with `nbio_7_0_sh_mask.h`, `nbio_7_0_default.h`, and `nbio_7_0_smn.h`.
2. Code calls helpers such as `SOC15_REG_OFFSET(NBIO, 0, mmBIF_SDMA0_DOORBELL_RANGE)`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG32_NO_KIQ`, and `WREG32_NO_KIQ`.
3. The helper combines the generated offset with `adev->reg_offset[NBIO_HWIP][instance][*_BASE_IDX]`.
4. Driver logic then performs read-modify-write, polling, or command submission against the resulting MMIO address.

The most direct in-tree consumer is `amdgpu/nbio_v7_0.c`. It uses offsets from this chunk to program SDMA, VCN/MMSCH, and IH doorbell ranges; expose HDP flush request/done offsets to GFX and SDMA command streams; read/write Syshub indirect registers for medium-grain clock gating; configure HDP remap registers; set interrupt controls; and derive the PCIe index/data offsets.

SR-IOV mailbox paths are another integration point. `amdgpu/mxgpu_ai.c` and `amdgpu/mxgpu_ai.h` use NBIO mailbox offsets such as `mmBIF_BX_PF0_MAILBOX_MSGBUF_TRN_DW*`, `mmBIF_BX_PF0_MAILBOX_MSGBUF_RCV_DW*`, and `mmBIF_BX_PF0_MAILBOX_CONTROL` through `SOC15_REG_OFFSET` and no-KIQ MMIO access to exchange requests, acknowledgements, initialization data, reset notifications, and checksum keys between VF and PF.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware-backed state:

- PCIe configuration and capability state for repeated NBIO PCIe port instances, including link/device status, MSI/MSI-map state, AER logs, lane equalization, ACS, multicast, L1 PM substates, DPC status, RP PIO logs, and ESM registers.
- IOMMU L2 state for device-table and command buffers, event/PPR/GA logs, MSI addresses/data, completion-wait behavior, error logging, invalidation, page-request handling, and performance counters.
- BIF/NBIO apertures and coherency controls, including doorbell apertures/ranges, self-ring GPA aperture, HDP memory/register coherency flush controls, GPU HDP flush request/done bits, transaction-pending status, and framebuffer access enablement.
- Interrupt and IH-related state, including interrupt dummy-read controls, MSI-X table entries, graphics MSI-X pending bits, BIF/RCC error interrupt controls, and mailbox interrupt controls.
- SR-IOV and PF/VF communication state in BIF mailbox transmit/receive buffers, mailbox valid/ack control bits, VM/hypervisor mailbox, BME status, GPUIOV configuration-size registers, and function-identifier registers.
- Syshub fabric, QoS, clock-gating, idle, scratch, class-mask, and NIC400 function-modifier state addressed indirectly through `mmSYSHUB_INDEX`/`mmSYSHUB_DATA`.

Persistence is hardware-defined. Configuration fields generally last until reset, suspend/resume reinitialization, power-gating loss, or driver reprogramming. Status, interrupt, error-log, flush, mailbox valid/ack, and transaction-pending registers may be sticky, self-clearing, write-one-to-clear, read-only, or command-like. This offset header does not encode those access semantics; the companion shift/mask/default headers and consuming driver code provide the operational behavior.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h`, which provides field shifts and masks for many offsets in this range.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`, which provides reset/default values for the same register namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`, which supplies related SMN addresses.
- SOC15 base-address setup in `adev->reg_offset`, consumed by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and related macros in `amdgpu/soc15_common.h`.

Important in-tree consumers and behavioral links include:

- `amdgpu/nbio_v7_0.c`: NBIO 7.0 operation table, doorbell ranges, HDP flush offsets, Syshub indirect read/write, clock gating, light sleep, IH controls, HDP remap, memory-controller access, and revision/memory-size reads.
- `amdgpu/soc15.c`: includes the NBIO 7.0 generated headers during SOC15 initialization and IP setup.
- `amdgpu/mxgpu_ai.c` and `amdgpu/mxgpu_ai.h`: SR-IOV VF/PF mailbox protocol over BIF mailbox registers.
- GFX and SDMA ring code: indirectly consumes `nbio_v7_0_get_hdp_flush_req_offset`, `nbio_v7_0_get_hdp_flush_done_offset`, and `nbio_v7_0_hdp_flush_reg` to emit HDP flush commands.
- SDMA, VCN/JPEG, UMSCH/MMSCH, and IH setup paths: call `adev->nbio.funcs->sdma_doorbell_range`, `vcn_doorbell_range`, and `ih_doorbell_range`, which rely on `mmBIF_SDMA0_DOORBELL_RANGE`, `mmBIF_SDMA1_DOORBELL_RANGE`, `mmBIF_MMSCH0_DOORBELL_RANGE`, and `mmBIF_IH_DOORBELL_RANGE`.

## Risks And Edge Cases

- Offset or `_BASE_IDX` drift is the central risk. These are untyped preprocessor constants, so a wrong numeric value can compile cleanly while targeting the wrong NBIO segment or register.
- The chunk contains highly repeated PCIe root-port config blocks. A generator or manual-edit error in only one `cfgBIFPLR<n>_0_*` family may surface only on one port, link width, hotplug path, AER/DPC event, or SR-IOV/IOMMU topology.
- `cfg...` offsets and `mm...` offsets are different addressing domains. Treating configuration-space-style offsets like SOC15 MMIO offsets, or vice versa, can silently address the wrong hardware path.
- Doorbell range registers are security- and routing-sensitive. Incorrect offset/base selection can assign SDMA, IH, or MMSCH doorbells to the wrong aperture, break queue notification, or expose a VF/PF isolation issue.
- HDP flush registers are ordering-sensitive. Wrong `mmGPU_HDP_FLUSH_REQ` or `mmGPU_HDP_FLUSH_DONE` offsets can leave CPU-visible memory stale, hang ring flush waits, or cause intermittent coherency bugs.
- SR-IOV mailbox offsets are protocol-sensitive. Misaddressed mailbox transmit/receive/control registers can cause lost PF/VF acknowledgements, failed GPU init/fini/reset access, stale checksum data, or FLR/reset timeouts.
- Syshub indirect offsets are used through an index/data window. Code must not treat `ixSYSHUB_MMREG_IND_*` values as direct SOC15 MMIO offsets; they are payloads written to `mmSYSHUB_INDEX`.
- IOMMU L2, interrupt, and error-log offsets touch platform-visible isolation and fault-reporting state. Incorrect values can mask translation faults, misroute MSI/PPR/event logs, or make page-request/error paths appear healthy when they are not.
- The range begins in the middle of `cfgBIFPLR0_0` and ends at the file terminator. Adjacent earlier chunks are required for the complete NBIO 7.0 offset map.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU with SOC15/NBIO 7.0 support enabled. Missing or renamed macros should fail in `nbio_v7_0.c`, `soc15.c`, MXGPU AI mailbox code, and ring/doorbell setup paths.
- Mechanically verify that every `mm...` register macro in lines 2429-4642 has the expected `_BASE_IDX` companion where this generated namespace requires one, and that the paired base-index values match AMD's authoritative NBIO 7.0 register database.
- Diff the repeated `cfgBIFPLR1_0` through `cfgBIFPLR6_0` blocks for structural consistency against each other and against the adjacent `cfgBIFPLR0_0` block from the previous chunk.
- Exercise SDMA, VCN/MMSCH, and IH doorbells: queue submission, interrupt delivery, ring idle/drain, suspend/resume, reset recovery, and doorbell disable/re-enable paths.
- Validate HDP flush behavior through GFX and SDMA rings: CPU/GPU memory coherency tests, command-stream flush waits, reset recovery, and workloads that rely on host reads after GPU writes.
- On SR-IOV-capable hardware, test VF init/fini/reset access requests, PF/VF mailbox acknowledgements, FLR notifications, checksum retrieval, mailbox interrupts, and timeout/error logging.
- Exercise IOMMU and PCIe error paths where possible: AER/DPC reporting, PPR/event-log traffic, MSI/MSI-X programming, link retraining/equalization diagnostics, and hotplug or link-state transitions.
- Toggle clock-gating/light-sleep policy and verify Syshub MGCG register updates through `mmSYSHUB_INDEX`/`mmSYSHUB_DATA`, idle-state reporting, and resume behavior.
- Watch kernel logs for doorbell misrouting, HDP flush timeouts, mailbox timeout messages, IOMMU fault-log anomalies, AER/DPC storms, interrupt delivery failures, and resume/reset regressions.

## Cross-Chunk Notes

This is a late chunk of `nbio_7_0_offset.h`. Earlier chunks cover the header opening and the beginning of NBIO, IOMMU configuration-space, and `cfgBIFPLR0_0` definitions. The final per-file research document should merge this chunk with adjacent chunks before making complete claims about all NBIO 7.0 address blocks or the full PCIe/IOMMU/NBIO register namespace.
