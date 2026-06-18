# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 17791-20320

## Scope

This chunk covers lines 17791-20320 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only. There are no functions, structs, enums, inline helpers, storage objects, allocation paths, locks, or executable control flow in this range.

The range starts in the middle of the `AID0_XCC1_VF5_BASE_ADDR` field definitions, continues through VF5/VF6/VF7 and PF base-address fields, then covers a broad NBIF/BIFC/RCC/BIF_BX1 register-field surface. It ends in the middle of `BIF_BX1_NBIF_GFX_ADDR_LUT_12`, with only the `ADDR` shift visible in this chunk and the matching mask outside the requested line range.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU driver register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-layout companion for NBIO 7.9.0 hardware registers. Each generated macro names either:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask inside the containing register.

Driver code combines these constants with matching register offsets from `nbio_7_9_0_offset.h` and common AMDGPU register helpers to read, decode, and update NBIO, NBIF, BIFC, RCC, and BIF_BX register state without hard-coded bit numbers.

This chunk is focused on PCIe/NBIO virtualization, doorbell access, DMA/MMIO attribute policy, error logging, power management, virtual-wire triggers, root-complex controls, indirect PCIe/BIF access, scratch registers, reset/interrupt controls, BACO controls, and GFX address lookup-table fields.

## Important Definitions

The opening base-address section names PF/VF routing fields:

- The first line is the trailing mask for `AID0_XCC1_VF5_BASE_ADDR`.
- `AID*_XCC*_VF5_BASE_ADDR`, `AID*_VF6_BASE_ADDR`, `AID*_XCC*_VF6_BASE_ADDR`, `AID*_VF7_BASE_ADDR`, `AID*_XCC*_VF7_BASE_ADDR`, and `AID0_NBIF/ATHUB/IH/HDP_VF*` define base-address field geometry for virtual functions across AID and XCC instances.
- `AID*_PF_BASE_ADDR` and `AID*_XCC*_PF_BASE_ADDR` define the corresponding physical-function base-address fields.
- Most base-address masks are 16-bit (`0x0000FFFFL`); `AID0_XCC0_VF6_BASE_ADDR` and `AID0_XCC0_VF7_BASE_ADDR` use a wider 17-bit mask (`0x0001FFFFL`), which is a field-width detail consumers must preserve.

NBIF/BIFC control and accounting registers include:

- `NBIF_RRMT_CNTL`: partition mode, AID die ID, RRMT enable, and invalid-address high bits.
- `BIFC_DOORBELL_ACCESS_EN_PF` and `BIFC_DOORBELL_ACCESS_EN_VF0` through `VF7`: per-function doorbell access enable masks.
- `MISC_SCRATCH`, `INTR_LINE_POLARITY`, and `INTR_LINE_ENABLE`: scratch and interrupt-line polarity/enable fields.
- `OUTSTANDING_VC_ALLOC`: DMA and host outstanding virtual-channel allocation and threshold fields.
- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1`: control bits for virtual-wire unit ID checking, active vlink behavior, DMA VC status, DMA chain break, host/GSI arbitration, split read stalls, atomic checks, SR-IOV/PF-VF handling, page/PH behavior, reset and ATS-message blocking, PCIe capability protection, D-state/PME behavior, HDP P2P adjustment, FLR/pending controls, ATS/atomic request disable, BME disable, and extended cache/host behavior.
- `BIFC_BME_ERR_LOG_LB`, `BIFC_RCCBIH_BME_ERR_LOG0`, `BIF_ATOMIC_ERR_LOG_DEV0_F0`, `BIF_ATOMIC_ERR_LOG_DEV0_F1`, `BIF_DMA_MP4_ERR_LOG`, and `BIF_PASID_ERR_LOG`: error-log field definitions for bus-master-enable, atomic, DMA, and PASID-related diagnostics.
- `BIF_PASID_ERR_CLR`: control fields to clear PASID error state.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`, `_F2_F3`, `_F4_F5`, and `_F6_F7`: per-function DMA attribute override fields for no-snoop, RO, ID-based ordering, PASID, ATS, privilege, and related request attributes.
- `BIFC_DMA_ATTR_CNTL2_DEV0`: additional DMA attribute controls for PASID/ATS and default attributes.
- `BME_DUMMY_CNTL_0`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_SDP_CNTL_0/1/2`, `BIFC_PASID_STS`, `BIFC_ATHUB_ACT_CNTL`, `BIFC_PGMST_CTRL`, `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL`: throttling, host arbitration, GSI/SDP routing, PASID checking/status, ATHUB activity, and NBIF power-gating master/slave policy fields.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the low/high halves of MMIO/DMA read/write performance counters: performance counter selection/control and counter-value field geometry.

SMN, self-ring, strap, power, and virtual-wire groups include:

- `SMN_MST_CNTL0/1` and `SMN_MST_EP_CNTL1` through `EP_CNTL5`: SMN master and endpoint controls, including IDs, ordering, timeout, credit, and request behavior fields.
- `BIF_SELFRING_BUFFER_VID` and `BIF_SELFRING_VECTOR_CNTL`: self-ring buffer/vector controls.
- `NBIF_STRAP_WRITE_CTRL`, `NBIF_INTX_DSTATE_MISC_CNTL`, and `NBIF_PENDING_MISC_CNTL`: strap-write and D-state/pending behavior controls.
- `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3`: weighted round-robin fields for GMI traffic classes.
- `NBIF_PWRBRK_REQUEST`: power-brake request field.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL_1`, and the matching `NBIF_SDP_VWR_*` controls: virtual-wire value-change disable, reset, trigger, and write-trigger controls for SMN/SDP paths.
- `NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK`: LCLK clock-gating and deep-sleep controls.
- `NBIF_SHUB_TODET_*`: timeout-detection client control/status and sync-flood behavior fields.
- `BIFC_HRP_SDP_WRRSP_POOLCRED_ALLOC`, `BIFC_HRP_SDP_RDRSP_POOLCRED_ALLOC`, `BIFC_GMI_SDP_REQ_POOLCRED_ALLOC`, and `BIFC_GMI_SDP_DAT_POOLCRED_ALLOC`: response/request/data pool-credit allocation fields.
- `DISCON_HYSTERESIS_HEAD_CTRL`, `BIFC_EARLY_WAKEUP_CNTL`, `BIFC_A2S_SDP_PORT_CTRL`, `BIFC_A2S_CNTL_SW0`, `BIFC_A2S_MISC_CNTL`, `BIFC_A2S_TAG_ALLOC_0`, `BIFC_A2S_TAG_ALLOC_1`, and `BIFC_A2S_CNTL_CL0`: disconnect hysteresis, early wakeup, A2S port, tag allocation, and client/software control fields.

The middle of the chunk crosses generated address-block boundaries:

- `addressBlock: aid_nbio_nbif0_rcc_dwn_dev0_BIFDEC1` covers downstream PCIe reserved/scratch/control/config/RX/bus/strap fields.
- `addressBlock: aid_nbio_nbif0_rcc_dwnp_dev0_BIFDEC1` covers downstream-port error, RX, link-speed, link-control, strap, and LTR-message fields.
- `addressBlock: aid_nbio_nbif0_rcc_ep_dev0_BIFDEC1` covers endpoint PCIe scratch/control/interrupt/status/RX/bus/config/TX/LTR, DPA, PME, error, and link-speed fields.
- `addressBlock: aid_nbio_nbif0_rcc_dev0_BIFDEC1` covers root-complex controller error interrupt, BACO/reset, VDM support, lane margining parameters, GPU IOV/host-VM/console IOV, peer register ranges, bus controls, configuration aperture, XDMA, features, bus-number lists, host-bus capture, peer framebuffer offsets, device/function lists, link controls, requester-ID restore, LTR switch, and multi-host arbitration fields.

The closing `BIF_BX1` sections describe the BIF bridge/system decode block:

- `BIF_BX1_PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, `PCIE_DATA2`, and high-index registers expose indirect PCIe access fields.
- `BIF_BX1_SBIOS_SCRATCH_*`, `BIF_BX1_BIOS_SCRATCH_*`, `BIF_BX1_DRIVER_SCRATCH_*`, and `BIF_BX1_FW_SCRATCH_*` expose firmware, BIOS, driver, and SBIOS scratch dwords.
- `BIF_BX1_GFX_MMIOREG_CAM_ADDR0` through `ADDR7`, matching `REMAP_ADDR0` through `REMAP_ADDR7`, and CAM completion/control registers define GFX MMIO register remap CAM fields.
- `BIF_BX_PF1_MM_INDEX`, `BIF_BX_PF1_MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI` define PF1 indirect MMIO index/data fields.
- `BIF_BX1_CC_BIF_BX_STRAP0`, `BIF_BX1_CC_BIF_BX_PINSTRAP0`, `BIF_BX1_BIF_MM_INDACCESS_CNTL`, `BIF_BX1_BUS_CNTL`, `BIF_BX1_BIF_SCRATCH0/1`, `BIF_BX1_BX_RESET_EN`, `BIF_BX1_MM_CFGREGS_CNTL`, `BIF_BX1_BX_RESET_CNTL`, `BIF_BX1_INTERRUPT_CNTL`, `BIF_BX1_INTERRUPT_CNTL2`, and `BIF_BX1_CLKREQB_PAD_CNTL` define strap, bus, reset, interrupt, MMIO-indirect, and clock-request pad controls.
- `BIF_BX1_BIF_FEATURES_CONTROL_MISC`, `BIF_BX1_HDP_ATOMIC_CONTROL_MISC`, `BIF_BX1_BIF_DOORBELL_CNTL`, `BIF_BX1_BIF_DOORBELL_INT_CNTL`, `BIF_BX1_BIF_FB_EN`, `BIF_BX1_BIF_INTR_CNTL`, `BIF_BX1_BIF_MST_TRANS_PENDING_VF`, `BIF_BX1_BIF_SLV_TRANS_PENDING_VF`, `BIF_BX1_BACO_CNTL`, `BIF_BX1_BIF_BACO_EXIT_TIME0`, `BIF_BX1_BIF_BACO_EXIT_TIMER1` through `TIMER4`, and `BIF_BX1_MEM_TYPE_CNTL` define feature gating, HDP atomic outstanding limit, doorbell monitor/interrupt behavior, framebuffer read/write enables, transaction-pending status, BACO entry/exit timers, and memory PHY mode fields.
- `BIF_BX1_NBIF_GFX_ADDR_LUT_CNTL` and `BIF_BX1_NBIF_GFX_ADDR_LUT_0` through the beginning of `_12` define the GFX address LUT enable/mode bits and 24-bit address entries.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace. Consumers normally pair these symbols with register address macros from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`.

The repository shows direct NBIO 7.9.0 consumers in:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`

Those source files include both `nbio_7_9_0_offset.h` and `nbio_7_9_0_sh_mask.h`, making this header part of the AMDGPU NBIO/RAS register-access ABI for this ASIC generation.

The macros encode only bit geometry. They do not encode reset values, read/write permissions, access width, side effects, sticky/write-one-to-clear behavior, firmware ownership, or sequencing requirements.

## Control Flow

This header contributes no local runtime control flow. Runtime behavior appears at call sites that:

1. Select a matching `reg*` address from `nbio_7_9_0_offset.h`.
2. Read or compose a 32-bit register value through AMDGPU register access helpers.
3. Use the `__SHIFT` and `_MASK` macros to extract, set, preserve, or clear a field.
4. Let hardware apply the NBIO/BIFC/RCC/BIF_BX side effect, such as changing access policy, recording status, gating traffic, enabling interrupts, controlling BACO, or steering address decode.

The order in this generated file is a register-database order, not an execution sequence. Address-block comments mark hardware decode regions rather than software control-flow boundaries.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names state that lives in NBIO 7.9.0 hardware registers and related PCIe/root-complex decode blocks.

Represented state includes:

- PF/VF/AID/XCC base-address state for virtualization and per-function register aperture routing.
- Doorbell access-enable state for PF and VF0-VF7, plus BIF_BX1 doorbell monitor and interrupt status/clear/disable bits.
- NBIF partition/RRMT state, invalid-address high bits, and AID die identity fields.
- DMA/MMIO request policy state: no-snoop, relaxed ordering, PASID, ATS, privilege, ID-based ordering, attribute override, and outstanding virtual-channel allocation.
- Error and diagnostic state: BME error logs, RCCBIH BME logs, atomic error logs, DMA/PASID error logs and clears, timeout-detection status, transaction-pending status, interrupt status, and scratch registers.
- Power/reset/clock state: NBIF power-gating master/slave controls, LCLK MGCG/deep-sleep controls, D-state/PME controls, reset enables, BACO control and exit timers, clock-request pad controls, early wakeup, and disconnect hysteresis.
- Root-complex and PCIe decode state: downstream, downstream-port, endpoint, and root-complex controller fields for RX/TX, link speed, link control, error handling, LTR, DPA, PME, VDM, bus numbers, requester ID, peer FB offsets, XDMA, console IOV, GPU IOV, and host-VM behavior.
- BIF_BX1 indirect access, scratch, GFX MMIO CAM/remap, MM index/data, framebuffer enable, interrupt, BACO, and GFX address LUT state.

Persistence of these hardware fields is governed by GPU reset domains, PCIe/function-level reset, BACO entry/exit, runtime power management, firmware/SBIOS initialization, driver reinitialization, and explicit writes. This header does not tell callers which fields survive which reset or power transition.

## Dependencies And Integration Points

The primary dependency is the matching generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`

This repository does not show a sibling `nbio_7_9_0_default.h` in the same directory, so reset/default metadata may be absent or supplied through another generated source for this ASIC family.

Integration points include:

- AMDGPU NBIO 7.9 initialization and runtime code in `amdgpu/nbio_v7_9.c`.
- AMDGPU RAS NBIO 7.9 code in `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which can decode or program RAS/error-reporting registers using these symbols.
- Common AMDGPU register helper macros that expect generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming.
- PCIe/SR-IOV and virtualization paths that rely on PF/VF base-address, doorbell, PASID, ATS, host-VM, console-IOV, and register-write/access-control fields.
- Power-management and reset paths that touch NBIF power gating, D-state/PME, BACO, LCLK gating, reset enables, and transaction-pending fields.
- Diagnostics, RAS, and recovery paths that decode BME, atomic, DMA, PASID, timeout, interrupt, and transaction-pending status.
- Firmware/SBIOS/driver coordination via scratch registers and strap/pinstrap fields.
- GFX/MMIO routing and debug paths that program indirect PCIE/MMIO access, GFX MMIO CAM entries, and the NBIF GFX address LUT.

## Risks And Edge Cases

- The chunk starts and ends inside register definitions. `AID0_XCC1_VF5_BASE_ADDR` is missing its comment and shift in this range, while `BIF_BX1_NBIF_GFX_ADDR_LUT_12` is missing its mask. The final merge pass must reconcile adjacent chunks before treating those registers as complete.
- A wrong mask or shift can compile cleanly while targeting adjacent hardware bits. For this chunk, the blast radius includes PF/VF routing, doorbell permissions, DMA attributes, interrupt state, power management, reset behavior, PCIe link/root-complex controls, and error reporting.
- Similar PF/VF/AID/XCC names are easy to confuse. Some fields differ subtly in width, such as 17-bit `AID0_XCC0_VF6/VF7_BASE_ADDR` masks versus mostly 16-bit base-address masks.
- Doorbell access and BIF doorbell interrupt fields affect isolation and event delivery. Incorrect enable/disable/clear handling can expose doorbells to the wrong function, lose interrupts, or create spurious interrupt status.
- Status and clear registers may be write-one-to-clear or otherwise write-sensitive. The availability of a mask does not imply a generic read-modify-write is safe for PASID errors, BME errors, atomic errors, interrupt status, timeout status, or transaction-pending diagnostics.
- DMA attribute override fields can change ordering, snooping, PASID, ATS, and privilege semantics. Misprogramming can break coherency, IOMMU translations, virtualization isolation, or peer-to-peer DMA assumptions.
- NBIF power gating, LCLK gating, D-state, BACO, reset, and pending-transaction fields require sequencing with active traffic. Changing them without draining or checking pending state can hang, drop requests, or corrupt recovery.
- Root-complex and endpoint PCIe fields include link speed/control, requester ID, bus numbers, peer FB offsets, XDMA, and LTR behavior. Copying field names across ASICs or address blocks can target the wrong port or root-complex instance.
- Scratch registers are shared coordination surfaces. Their presence in the mask header does not establish ownership between firmware, SBIOS, driver, and diagnostics.
- The header is generated hardware metadata. Manual edits should be treated as high risk unless regenerated from the authoritative register database and checked against matching offsets.

## Test Signals

Useful verification signals for this chunk are mostly compile-time, generated-header consistency, and hardware runtime checks:

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed macro names and missing offset/mask users.
- Run generated-header consistency checks: every complete field in this chunk should have both a `__SHIFT` and `_MASK`, masks should align with their shifts, and every named register should have a matching `reg*` entry in `nbio_7_9_0_offset.h`.
- Explicitly account for boundary exceptions: `AID0_XCC1_VF5_BASE_ADDR` is partial at the start and `BIF_BX1_NBIF_GFX_ADDR_LUT_12` is partial at the end.
- Compare repeated register families against the authoritative NBIO 7.9.0 register database: PF/VF base-address matrices, `BIFC_DMA_ATTR_OVERRIDE_DEV0_F*` groups, virtual-wire SMN/SDP groups, `RCC_*` address blocks, scratch-register sequences, GFX CAM entries, and GFX address LUT entries should be structurally consistent where expected.
- Boot and probe matching hardware to exercise NBIO 7.9 register access through `nbio_v7_9.c`.
- Exercise SR-IOV or virtualization configurations if available: PF/VF base apertures, doorbell access, PASID/ATS behavior, host-VM/console-IOV settings, and isolation should match expectations.
- Exercise interrupts, RAS, and recovery: doorbell interrupt status/clear/disable behavior, BME/atomic/DMA/PASID error logging, timeout detection, sync-flood policy, and RAS NBIO decoding should report coherent fields.
- Exercise suspend/resume, BACO entry/exit, runtime power management, GPU reset, and function-level reset to verify that power, reset, pending, scratch, and restore-sensitive fields are initialized or restored correctly.
- Validate PCIe link/root-complex behavior on supported platforms: bus numbers, requester ID, LTR, DPA/PME, link speed/control, peer FB offsets, XDMA, and error-control fields should remain coherent after enumeration and recovery.
