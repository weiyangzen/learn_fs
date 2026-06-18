# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 114772-117356

## Scope

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask register header. It contains 2,100 `#define` constants: 1,050 `__SHIFT` values and 1,050 `_MASK` values. There are no functions, structs, enums, global variables, allocations, locks, sysfs/debugfs handlers, or executable control-flow statements in this range.

The slice starts in the tail of the `BIF_CFG_DEV1_EPF1_2` PCIe Dynamic Power Allocation and ACS/ARI definitions, then covers a full `BIF_CFG_DEV1_EPF2_2` endpoint-function PCI configuration-space block. It continues through PF1 BIF/NBIO access windows, scratch registers, interrupt/reset/doorbell/power/BACO/HDP/mailbox controls, GDC1 doorbell and misc controls, and then repeats unprefixed PF1/SYSDEC/RCC endpoint field families. It ends inside `DN_PCIE_CNTL`; the remaining downstream-device control fields are in the following chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield-description layer for NBIO 7.0 registers. For each hardware field, this file exposes:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode that field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve that field in a register value.

This chunk describes PCIe endpoint configuration and NBIF/PF control state for AMD GPU hardware, despite the broader repository path being under a Ceph-client source tree. Runtime AMDGPU code combines these macros with companion register address headers and register helpers to read, update, or decode NBIO PCIe/NBIF hardware registers.

The covered hardware roles are:

- PCIe endpoint function 2 config-space identity, BARs, power management, PCIe link/device capabilities, MSI/MSI-X, AER, enhanced BAR, power budget, DPA, ACS, and ARI fields.
- PF1 MMIO, SYSHUB, and PCIe indirect-index/data windows.
- SBIOS/BIOS scratch registers used for firmware-driver handoff or diagnostics.
- RLC, VCE, and UVD interrupt-control bits related to command completion, hang recovery, FLR needs, and VM-busy transitions.
- GFX MMIO register CAM address/remap controls and completion policy registers.
- RCC strap, endpoint, and downstream PCIe controls, including AER interrupt/status bits, LTR/DPA, requester ID, TPH disable controls, completion/error ignore policy, and link-speed straps.
- BIF PF1 bus, reset, interrupt, clock-request pad, feature, doorbell, framebuffer, busy-delay, transaction-pending, BACO, voltage/power status, HDP flush, ring-buffer, mailbox, VM/HV mailbox, and GPUIOV sizing fields.
- GDC1 doorbell range and misc controls for SDMA, IH, MMSCH, ATDMA, SDP/GDC power gating, and doorbell fences.

## Important Macro Families

The opening `BIF_CFG_DEV1_EPF1_2_*` fragment completes part of the preceding endpoint-function block. It includes PCIe DPA latency/status/control and substate power-allocation fields, ACS enhanced capability/header/capability/control bits, and ARI enhanced capability/capability/control bits. These are virtualization, peer-to-peer routing, and PCIe power-management fields; this chunk only owns their tail because the corresponding endpoint-function block starts in the previous chunk.

`BIF_CFG_DEV1_EPF2_2_*` is the largest complete family in this range. It mirrors PCI/PCIe config-space layout for device 1 endpoint function 2. It includes vendor/device IDs, command/status, revision/class, BAR1-BAR6, ROM BAR, capability pointer, interrupt line/pin, adapter IDs, vendor capability, power-management capability/status-control, USB-related SBRN/FLADJ/DBESL, PCIe capability/device/link fields, device/link second-generation fields, MSI/MSI-X capability structures, SATA capability/index/data registers, vendor-specific enhanced capabilities, AER status/mask/severity/capability/header log/TLP prefix log registers, BAR enhanced capabilities, power-budget fields, DPA fields, ACS fields, and ARI fields.

Within the `BIF_CFG_DEV1_EPF2_2_*` block, AER macros deserve special attention. `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` expose data-link protocol, poisoned TLP, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned Egress Blocked status/policy bits. `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header log overflow bits. `PCIE_ADV_ERR_CAP_CNTL` and the header/TLP prefix log fields describe diagnostics and ECRC policy.

The `BIF_BX_PF1_MM_INDEX`, `BIF_BX_PF1_MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI` fields define PF1 indirect MMIO access windows. The `BIF_BX_PF1_SYSHUB_INDEX_OVLP`, `BIF_BX_PF1_SYSHUB_DATA_OVLP`, `BIF_BX_PF1_PCIE_INDEX`, `BIF_BX_PF1_PCIE_DATA`, `BIF_BX_PF1_PCIE_INDEX2`, and `BIF_BX_PF1_PCIE_DATA2` fields describe overlapping indirect access paths for SYSHUB and PCIe register spaces. These are integration points for code that must sequence index/data accesses correctly.

The SBIOS and BIOS scratch register families are full-width 32-bit fields. They do not define protocol semantics by themselves, but they provide preserved or firmware-owned storage locations that AMDGPU, BIOS, SMU, or diagnostics can use for state handoff depending on the platform flow.

`BIF_BX_PF1_BIF_RLC_INTR_CNTL`, `BIF_BX_PF1_BIF_VCE_INTR_CNTL`, and `BIF_BX_PF1_BIF_UVD_INTR_CNTL` expose four repeated interrupt conditions per block: command complete, hang self-recovered, hang needs FLR, and VM busy transition. The unprefixed `BIF_RLC_INTR_CNTL`, `BIF_VCE_INTR_CNTL`, and `BIF_UVD_INTR_CNTL` repeat the same field layout later in the chunk.

The GFX MMIOREG CAM families provide eight address/remap pairs, an enable byte, and completion-response programming fields. These fields let hardware remap selected GFX MMIO register windows or choose completion behavior. The prefixed `BIF_BX_PF1_GFX_MMIOREG_CAM_*` and later unprefixed `GFX_MMIOREG_CAM_*` groups have the same schema.

`RCC_STRAP2_RCC_DEV0_EPF0_STRAP0` and `RCC_DEV0_EPF0_STRAP0` define strap-derived device ID, revision, function enable, legacy device type, and D1/D2 support bits for device 0 function 0. These are configuration-source fields rather than ordinary driver-owned runtime policy bits.

`RCC_EP_DEV0_2_EP_PCIE_*` and later unprefixed `EP_PCIE_*` groups describe endpoint PCIe-side controls. They include scratch storage, unsupported-request reporting suppression, AER/error interrupt enables and statuses, invalid PASID handling, immediate PMI disable, hidden-register decode enables, LTR private snoop/non-snoop values and requirements, DPA substate power allocation for F1/F0, F0 DPA capability/control, PME service timer, TX relaxed/no-snoop override, TPH disable bits, requester ID, AER header-log timeout and per-function timer-expired bits, RX error-ignore policy, completion-timeout disable, PASID/prefix ignore policy, and Gen2/Gen3 link-speed strap bits.

`RCC_DWN_DEV0_2_DN_PCIE_*` and the final unprefixed `DN_PCIE_*` fragment define downstream-side scratch/control fields, including hardware-init write lock, downstream unsupported-request reporting suppression, and ignoring LTR-message unsupported requests. The chunk ends before the unprefixed `DN_PCIE_CNTL` masks are complete.

`BIF_BX_PF1_BUS_CNTL` is a broad PF1 bus-policy register. It covers PMI interrupt disables across endpoint/downstream/SWUS paths, VGA coherency disables, AZ/MC traffic-class selection, zero-byte-enable read/write enables, read-stall/write behavior, INTx deassertion behavior across D-state changes, unsupported-request override for ECRC, preceding-write stall flush policy, GSI split-read stall policy, HDP register flush VF mask enable, and VGA framebuffer zero-byte-enable policy.

PF1 reset and interrupt macros include `BIF_BX_PF1_BX_RESET_EN`, `BIF_BX_PF1_MM_CFGREGS_CNTL`, `BIF_BX_PF1_BX_RESET_CNTL`, `BIF_BX_PF1_INTERRUPT_CNTL`, and `BIF_BX_PF1_INTERRUPT_CNTL2`. These define COR/REG/STY reset enables, FLR-twice and VF-enable-low reset behavior, MM config access selection, link training enable, IH dummy-read behavior, interrupt delay, generated IH interrupts, non-snoop request policy, and dummy-read address.

PF1 doorbell and transaction fields include `BIF_BX_PF1_BIF_DOORBELL_CNTL`, `BIF_BX_PF1_BIF_DOORBELL_INT_CNTL`, `BIF_BX_PF1_BIF_FB_EN`, `BIF_BX_PF1_BIF_MST_TRANS_PENDING_VF`, `BIF_BX_PF1_BIF_SLV_TRANS_PENDING_VF`, and `BIF_BX_PF1_BIF_TRANS_PENDING`. These macros affect self-ring behavior, translation checks, doorbell monitor interrupts, framebuffer read/write enable, and pending master/slave transaction status for PF/VF traffic.

The BACO and power/voltage families include `BIF_BX_PF1_BACO_CNTL`, `BIF_BX_PF1_BIF_BACO_EXIT_TIME0`, `BIF_BX_PF1_BIF_BACO_EXIT_TIMER1..4`, `BIF_BX_PF1_MEM_TYPE_CNTL`, `BIF_BX_PF1_SMU_BIF_VDDGFX_PWR_STATUS`, and `BIF_BX_PF1_BIF_VDDGFX_*` threshold registers. These describe bus active/chip off policy, BACO exit timing, memory-type control, and SMU/BIF VDDGFX threshold/status fields used by power-management flows.

`BIF_BX_PF1_BIF_DOORBELL_GBLAPER1_*` and `BIF_BX_PF1_BIF_DOORBELL_GBLAPER2_*` define global doorbell aperture bounds. `BIF_BX_PF1_DOORBELL_SELFRING_GPA_APER_*` defines GPA aperture base and enable/mode/size for doorbell self-ring. These are address-range definitions for doorbell routing and virtualization-sensitive aperture control.

`BIF_BX_PF1_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` expose one bit each for CP0-CP9 and SDMA0-SDMA1 flush request/done. `BIF_BX_PF1_REMAP_HDP_MEM_FLUSH_CNTL`, `BIF_BX_PF1_REMAP_HDP_REG_FLUSH_CNTL`, `BIF_BX_PF1_HDP_REG_COHERENCY_FLUSH_CNTL`, and `BIF_BX_PF1_HDP_MEM_COHERENCY_FLUSH_CNTL` identify flush-remap or coherency flush controls. These macros are directly relevant to cache/coherency barriers around GPU command processors and SDMA.

The `BIF_BX_PF1_BIF_RB_*` group defines a BIF ring-buffer base, read pointer, write pointer, write-pointer address, and overflow indication. The mailbox groups define transmit and receive message-buffer dwords, valid/ack control bits, interrupt enables, and a compact VM/HV mailbox with 4-bit data fields and valid/ack/intr bits. These are hardware communication primitives rather than software queues owned by the header.

`BIF_BX_PF1_BIF_BME_STATUS` and `BIF_BX_PF1_BIF_ATOMIC_ERR_LOG` cover DMA-on-BME-low and unsupported atomic-operation diagnostics with explicit clear bits. The GPUIOV sizing macros for UVD, VCE, and GFX/SDMA expose per-block configuration sizing fields used by GPU virtualization support.

The `GDC1_*` block covers GDC1 SDP disconnect hysteresis, non-PF MMREG request set-error suppression, SDMA0/SDMA1/IH/MMSCH doorbell range offset and size, ATDMA weighted arbitration and read insertion, doorbell fence enable, S2A doorbell 64-bit support disables, AXI host completion endpoint disable, and GDC power-gating reset selection.

## APIs, Types, And Functions

This chunk exports only C preprocessor constants. There are no callable APIs and no C types. The practical interface is the generated macro namespace used by AMDGPU register helpers.

Consumers generally pair these constants with:

- Register address symbols from `nbio_7_0_offset.h`.
- Reset/default symbols from `nbio_7_0_default.h`.
- SMN address symbols from `nbio_7_0_smn.h` where applicable.
- AMDGPU register helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indirect-index/data helpers, or direct bit masking and shifting.

The macros do not encode register access type, reset value, reserved-bit policy, side-effect semantics, timing requirements, or hardware ownership. A caller must know whether a field is read-only, write-one-to-clear, sticky, strap-derived, firmware-owned, reset-sensitive, or safe for read/modify/write.

## Control Flow

There is no local software control flow in this header. Runtime flow is external:

1. AMDGPU or related code chooses a register address from the companion NBIO 7.0 address metadata.
2. The code reads or composes a 32-bit register value through MMIO, PCIe config, SMN, SYSHUB, or indirect index/data access.
3. It extracts or updates fields using the `__SHIFT` and `_MASK` values in this chunk.
4. Hardware state machines then act on the resulting field values.

The implicit hardware workflows represented here include PCIe enumeration and capability reporting, endpoint power management, DPA substate accounting, ACS/ARI virtualization behavior, AER error logging and masking, MSI/MSI-X programming, PF1 reset and FLR-related behavior, GPU hang/VM-busy interrupt signaling, doorbell aperture routing, HDP coherency flush request/done handshakes, BACO entry/exit timing, endpoint/downstream PCIe RX/TX error policy, link-speed strap interpretation, mailbox valid/ack handshakes, and GDC1 doorbell range setup.

Indirect access windows have sequencing constraints even though the macros are static. Index registers must be programmed before reading or writing their paired data registers, and concurrent or stale index use can target the wrong hardware register. The header does not provide locking or ordering.

## State And Persistence Behavior

The file itself owns no software state and persists nothing. It describes hardware-visible state in NBIO/NBIF/PCIe/GDC registers.

Represented state categories include:

- PCI config-space identity, capability, BAR, interrupt, and power-management fields.
- PCIe AER, ACS, ARI, DPA, MSI, MSI-X, link, and device control/status bits.
- Strap-derived device ID, revision, function-enable, and power-state support fields.
- Scratch registers and BIOS/SBIOS handoff fields.
- Interrupt enable/status bits for PCIe/AER, RLC, VCE, UVD, doorbell monitor, IOHC RAS, mailbox, and VM/HV mailbox paths.
- Reset, FLR, link-training, and D-state sensitive control fields.
- Doorbell ranges and apertures, including self-ring and global aperture bases.
- HDP flush request/done and coherency flush controls.
- BACO, VDDGFX, memory-type, and power-status fields.
- Ring-buffer, mailbox, transaction-pending, atomic-error, BME, and GPUIOV state.
- GDC1 doorbell, SDP, ATDMA arbitration, and power-gating controls.

Persistence depends on hardware reset domain, PCIe hot/cold reset, FLR, BACO, suspend/resume, power gating, firmware initialization, BIOS handoff, and explicit driver writes. Many status and diagnostic fields are likely sticky or clear-on-write according to hardware semantics, but this shift/mask header does not declare those semantics. Full-width masks such as `0xFFFFFFFFL` identify field width only; they are not evidence that arbitrary writes are safe.

## Dependencies And Integration Points

The direct dependency is the generated AMD NBIO 7.0 register database. This header must remain synchronized with the companion NBIO 7.0 offset, default, and SMN headers. In this tree, `nbio_v7_0.c`, `soc15.c`, and PowerPlay's `smu10_inc.h` include `nbio_7_0_sh_mask.h` with the adjacent NBIO 7.0 generated headers.

Important AMDGPU integration points include:

- NBIO v7.0 initialization, memory-controller access enabling, and register remapping.
- Doorbell setup for SDMA, VCN/MMSCH, IH, self-ring, and global aperture routing.
- HDP flush register discovery and request/done polling for CP and SDMA engines.
- PCIe capability, AER, MSI/MSI-X, power-management, and link-management handling around Linux PCI core interactions.
- GPU reset, FLR, hang recovery, transaction-pending, and D-state/BACO flows.
- Runtime power management, LTR/DPA/PME, VDDGFX threshold/status, and GDC power-gating behavior.
- Virtualization and isolation paths involving ACS/ARI, GPUIOV sizing, PF/VF doorbell apertures, BME status, atomic error logging, VM/HV mailbox, and indirect MMIO/SYSHUB/PCIe register access.
- Firmware and BIOS handoff through strap and scratch registers.

The repeated prefixed and unprefixed families are a generated-addressing detail: both sets describe similar PF1/SYSDEC/RCC/GDC register schemas in different address blocks or access paths. Consumers must use the macro family that matches the selected register address.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting unrelated hardware bits. In this chunk that can affect PCIe enumeration, BAR reporting, AER policy, ACS/ARI isolation, MSI/MSI-X interrupt delivery, doorbell routing, HDP flush handshakes, BACO timing, or reset behavior.
- The chunk begins and ends on logical block boundaries that are incomplete. The `BIF_CFG_DEV1_EPF1_2` DPA/ACS/ARI block starts in the previous chunk, and the unprefixed `DN_PCIE_CNTL` masks continue in the next chunk.
- Status, enable, mask, and clear bits often share similar names. Using a status mask against a control register, or treating clear bits as persistent status, can drop diagnostics or create interrupt storms.
- AER and atomic/BME error-log fields may have sticky or write-one-to-clear semantics. Software must preserve evidence long enough for diagnostics while also clearing conditions according to the hardware contract.
- Indirect MMIO/SYSHUB/PCIe index/data windows are shared access mechanisms. Missing synchronization or stale indexes can read or write the wrong register.
- Doorbell aperture and self-ring GPA fields are security- and virtualization-sensitive because they define address windows for queue signaling. Bad aperture size/base/mode values can route doorbells incorrectly or expose guest/host signaling paths.
- HDP flush request/done bits are synchronization primitives for command processors and SDMA engines. Polling the wrong bit, failing to wait, or misprogramming remap/coherency controls can leave stale CPU/GPU-visible data.
- BACO, DPA, LTR, PME, D-state, VDDGFX, and power-gating fields intersect with suspend/resume and runtime power management. Incorrect programming can produce devices that enumerate but fail during resume, link power transitions, or reset recovery.
- Generated families are highly repetitive. Copy or generation drift across `BIF_CFG_DEV1_EPF2_2`, `RCC_EP_DEV0_2_EP_PCIE_*`, unprefixed `EP_PCIE_*`, and prefixed/unprefixed PF1 blocks can be hard to catch by review alone.

## Test And Validation Signals

- Build AMDGPU with NBIO 7.0 support enabled. Missing or renamed symbols referenced by `nbio_v7_0.c`, `soc15.c`, PowerPlay, or related register code should fail at compile time.
- Run generated-header consistency checks: every field should have one `__SHIFT` and one `_MASK`, masks should align with shifts and width expectations, full-width fields should be intentional, and repeated prefixed/unprefixed register schemas should match where hardware expects them to.
- Cross-check this chunk against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so every register family has a matching address/default entry and no field stems drift from the generated database.
- On NBIO 7.0 hardware, validate PCIe enumeration for endpoint function 2: IDs, class/revision, BAR sizing, capability list traversal, MSI/MSI-X capability behavior, AER capability data, ACS/ARI exposure, DPA/power budget fields, and link/device capability/status reports.
- Exercise GPU reset, PF/VF FLR, suspend/resume, BACO entry/exit, D3/D0 transitions, and runtime power management while checking transaction-pending bits, reset/link-training behavior, PME/LTR/DPA status, and post-reset PCIe responsiveness.
- Stress command processors and SDMA while tracing HDP flush request/done bits for CP0-CP9 and SDMA0-SDMA1. Flush done bits should correspond to the intended request bits and no stale-data symptoms should appear.
- Validate doorbell programming for SDMA, IH, MMSCH/VCN, self-ring, and global apertures. Doorbell ranges should match expected offsets/sizes and guest/host isolation should hold under SR-IOV or GPUIOV scenarios.
- Inject or observe PCIe/AER/RAS-like errors where supported and verify interrupt enable/status bits, correctable/uncorrectable status/mask/severity, header/TLP prefix logging, atomic error logs, BME status, and clear behavior.
- Exercise mailbox and VM/HV mailbox handshakes by checking valid/ack transitions and interrupt enables. Lost valid/ack transitions indicate bad bit definitions or ordering.
- Validate GDC1 doorbell ranges, ATDMA arbitration settings, SDP disconnect hysteresis, and GDC power-gating reset behavior under traffic stress and suspend/resume.

## Cross-Chunk Notes

This report covers only lines 114772-117356. The previous chunk owns the beginning of the `BIF_CFG_DEV1_EPF1_2` DPA/ACS/ARI endpoint-function block. The next chunk owns the rest of unprefixed downstream-device PCIe control fields after `DN_PCIE_CNTL`. The merge/reconciliation lane should combine adjacent chunks before making whole-file claims about either boundary block.
