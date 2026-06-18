# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 78894-81346

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, dynamic allocations, locks, loops, branches, or direct register reads/writes in this range.

The assigned lines contain 2,128 `#define` entries across 319 commented register blocks plus two generated address-block markers. The slice starts in the middle of `BIF_CFG_DEV0_EPF1_1_LINK_CAP`, continues through the remaining `BIF_CFG_DEV0_EPF1_1` PCIe capability and extended-capability field definitions, covers a broad `BIF_CFG_DEV0_EPF2_1` function configuration image, and ends inside `BIF_CFG_DEV0_EPF3_1_LINK_CNTL`.

Although this file is under a `ceph-client` source mirror, the content is AMDGPU hardware metadata for GPU NBIO/BIF PCIe configuration space. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions for NBIO 4.3.0 PCIe endpoint-function configuration and extended-capability registers. Each hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or update that field.

Consumers pair these field macros with matching register offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` and, where defaults are needed, related generated default headers for other NBIO versions. Runtime AMDGPU code normally reaches these constants through register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The `EPF1_1` portion starts at the tail of `LINK_CAP`: link speed, width, ASPM/power-management support, latency, surprise-down reporting, data-link active reporting, bandwidth notification, ASPM optionality, and port number. It then covers PCIe link control/status, device/link capability 2 controls/status, MSI and MSI-X capability programming, vendor-specific enhanced capability fields, device serial number fields, AER enhanced capability fields, resizable BAR controls, power budget, dynamic power allocation, secondary PCIe capability, per-lane equalization controls, ACS, PASID, multicast, LTR, ARI, SR-IOV, VF resizable BAR, and route-through-router fields.

The `EPF2_1` address block begins at `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`. It defines a Type 0 PCI configuration image for endpoint function 2: vendor/device identity, command/status, revision/class bytes, cache line and latency, header/BIST, six BARs, CardBus CIS pointer, subsystem IDs, ROM base address, capability pointer, interrupt line/pin, min-grant/max-latency, vendor capability, PM capability/status, serial-bus release number, frame length adjustment, DBESL/DBESLD, PCIe capability, device/link control/status, MSI/MSI-X, vendor-specific capability, AER, BAR capability/control groups, power budget, DPA, ACS, PASID, ARI, and route-through-router data.

The `EPF3_1` address block begins at `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`. This chunk covers its identity/header fields, BAR and ROM resource fields, capability pointers, vendor and PM capability fields, PCIe capability, device capability/control/status, link capability, and the beginning of `LINK_CNTL`. The range stops at `BIF_CFG_DEV0_EPF3_1_LINK_CNTL__DRS_SIGNALING_CONTROL__SHIFT`, so the corresponding `LINK_CNTL` masks and all later EPF3 registers continue in the next chunk.

Notable field categories include PCI command/status bits, BAR aperture encodings, MSI address/data/mask/pending state, MSI-X table and pending-bit-array locations, AER uncorrectable/correctable error status/mask/severity and header/TLP prefix logs, resizable BAR sizing and control, PCIe power budget and DPA substate allocation, secondary capability equalization controls for lanes 0-15, ACS controls, PASID enablement and width, multicast filtering/blocking controls, LTR latency values, ARI next-function/function-group controls, SR-IOV VF counts/stride/page size/VF BARs, and opaque router payload registers.

## APIs, Types, And Functions

There are no C APIs, callable functions, or types in this chunk. The exported interface is the generated macro namespace itself:

- `BIF_CFG_DEV0_EPF1_1_*__SHIFT` and `BIF_CFG_DEV0_EPF1_1_*_MASK` for endpoint function 1 field layouts.
- `BIF_CFG_DEV0_EPF2_1_*__SHIFT` and `BIF_CFG_DEV0_EPF2_1_*_MASK` for endpoint function 2 field layouts.
- `BIF_CFG_DEV0_EPF3_1_*__SHIFT` and `BIF_CFG_DEV0_EPF3_1_*_MASK` for the beginning of endpoint function 3 field layouts.

The constants are untyped preprocessor values, mostly 16-bit or 32-bit field masks with `L` suffixes. Callers must supply the correct register offset, access method, access width, and access semantics; the macros only describe bit positions.

## Control Flow

This header has no executable control flow. Runtime behavior appears only in code that includes the generated header:

1. AMDGPU/NBIO code chooses a matching `regBIF_CFG_DEV0_EPF*_1_*` offset from the companion offset header.
2. The driver reads or composes a PCIe configuration-space dword through the PCIe or SOC15 register access layer.
3. It applies this header's shift/mask constants directly or via field helpers.
4. It writes control state, decodes capability/status state, clears sticky diagnostics, polls hardware-owned state, or exposes decoded values to PCIe, SR-IOV, interrupt, reset, power-management, or RAS flows.

Typical consuming flows include endpoint-function configuration, SR-IOV PF/VF setup, VF BAR/resource publication, MSI/MSI-X interrupt routing, PCIe link and power policy, DPA/LTR/ASPM decisions, AER/RAS diagnostics, ARI enumeration, ACS/PASID-related isolation controls, resizable BAR handling, and suspend/resume restore paths.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, platform PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SR-IOV management code.

The represented state spans static capabilities, software-programmed controls, hardware-updated status, and diagnostic logs. Identity, class, BAR, capability-list, SR-IOV, and VF BAR fields describe how functions and virtual functions are presented to the host. Link, LTR, DPA, power budget, and equalization fields describe power and signal behavior. MSI/MSI-X fields affect interrupt delivery state. AER fields can be sticky and may use write-one-to-clear behavior depending on the hardware register. ACS, PASID, ARI, multicast, and router fields affect enumeration, isolation, routing, and peer-to-peer behavior.

The generated shift/mask macros do not encode reset defaults, read-only versus writable ownership, write-one-to-clear behavior, polling requirements, firmware ownership, or required ordering around reads and writes.

## Dependencies And Integration Points

The immediate dependency is the generated NBIO 4.3.0 register database. This chunk must remain synchronized with `nbio_4_3_0_offset.h`, which supplies the matching register offsets and base indices. It also overlaps generated default-value data in newer NBIO headers such as `nbio_6_1_default.h`, which contains similarly named `EPF1_1`, `EPF2_1`, and `EPF3_1` default macros and is useful as a comparison point but not an authoritative default source for NBIO 4.3.0.

Direct in-tree includes of `nbio_4_3_0_sh_mask.h` appear in `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. `amdgpu_discovery.c` selects NBIO v4.3 operation tables, and `nbio_v4_3.c` provides integration for PCIe index/data access, HDP flush offsets, memory access enablement, doorbell range programming, interrupt handler control, clock gating/light sleep, LTR/ASPM programming, register remapping, and RAS error-event handling.

The important external integration surfaces are the Linux PCI core, platform firmware, IOMMU/virtualization policy, SR-IOV PF/VF lifecycle code, guest drivers, MSI/MSI-X interrupt delivery, PCIe AER handling, runtime power management, suspend/resume, reset/FLR handling, and diagnostic tools that dump PCIe configuration space.

## Risks And Edge Cases

- The chunk boundaries are artificial. It begins after most of `EPF1_1_LINK_CAP` shifts and ends before the `EPF3_1_LINK_CNTL` masks; adjacent chunks are required for complete per-register and per-function analysis.
- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can program or decode the wrong PCIe bit.
- The EPF1/EPF2/EPF3 blocks are highly repetitive. Suffix drift between endpoint functions can silently target the wrong function and affect isolation, interrupts, BAR resources, or diagnostics.
- Offset/header drift is dangerous: a valid-looking mask from this header applied to a mismatched register offset from another function or NBIO version can corrupt unrelated configuration state.
- PCIe link and device-control fields are platform-sensitive. Incorrect max payload, max read request, relaxed ordering, no-snoop, completion timeout, FLR, target speed, link disable, retrain, LTR, DPA, or ASPM-related programming can cause DMA ordering bugs, enumeration failures, reset hangs, or link instability.
- MSI/MSI-X fields have interrupt-delivery side effects. Mistakes in enable bits, message address/data, table BIR/offset, mask, pending, or 64-bit aliases can cause lost, misrouted, or unexpectedly unmasked interrupts.
- AER fields may be sticky or write-one-to-clear. Generic read/modify/write treatment can erase diagnostic evidence or leave errors masked with the wrong severity.
- SR-IOV and VF resizable BAR fields affect resource exposure and virtualization. Incorrect VF count, stride, page size, VF BAR, migration-state offset, or resize encoding can break VF enumeration or guest isolation.
- ACS, PASID, ARI, multicast, and router controls affect isolation and routing semantics. Misprogramming them can cause peer-to-peer access surprises, bad function enumeration, or IOMMU/guest-visible inconsistencies.
- Lane equalization and per-lane error fields depend on negotiated link width. Assuming all 16 lanes are active can misinterpret inactive-lane status or hide signal-integrity problems.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU with NBIO 4.3 support enabled so renamed, missing, or malformed macros surface in NBIO v4.3 and SMU13 users.
- Compare `EPF1_1`, `EPF2_1`, and `EPF3_1` register names against `nbio_4_3_0_offset.h` to confirm field blocks have matching offsets and base indices.
- Dump PCIe config space on affected hardware and verify identity, command/status, BARs, capability lists, PCIe capability, MSI/MSI-X, AER, ARI, SR-IOV, ACS, PASID, LTR, and router registers decode consistently with these masks.
- Enable SR-IOV where supported, create/remove VFs, bind guest drivers, exercise VF BAR sizing and VF migration-state exposure, and verify PF-visible VF counts, stride, page-size, and resource fields.
- Exercise MSI/MSI-X interrupt delivery under graphics, compute, and DMA workloads; watch for lost vectors, stuck pending bits, or unexpected masking.
- Run suspend/resume, runtime power transitions, PCIe link retraining, ASPM/LTR policy changes, DPA/power-budget queries, and FLR/reset paths while monitoring link speed/width, equalization state, and completion timeout behavior.
- Use AER/error-injection or platform diagnostics where available to verify correctable and uncorrectable status, masks, severity, header logs, and TLP prefix logs map to expected PCIe errors without losing diagnostic state.
- In ARI/ACS/PASID-capable configurations, verify function enumeration, isolation policy, PASID controls, multicast fields, and peer-to-peer behavior before and after VF lifecycle and reset operations.

## Chunk Notes

- Lines 78894-79047 start inside `BIF_CFG_DEV0_EPF1_1_LINK_CAP` and then define `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Lines 79048-80221 continue `EPF1_1` through MSI/MSI-X, vendor-specific capabilities, device serial number, AER, resizable BAR, power budget, DPA, secondary capability, lane equalization, ACS, PASID, multicast, LTR, ARI, SR-IOV, VF resizable BAR, and router data.
- Lines 80222-81210 define the `BIF_CFG_DEV0_EPF2_1` address block from identity/header registers through router data.
- Lines 81211-81346 begin the `BIF_CFG_DEV0_EPF3_1` address block and stop inside `LINK_CNTL`; the rest of EPF3 link control/status and later capabilities continue after this chunk.
