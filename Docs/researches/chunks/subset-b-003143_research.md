# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 51625-54019

## Scope

This chunk covers generated shift and mask macros for AMD NBIO 7.11.0 register fields. The range starts in the middle of `DEV2_PF2_FLR_RST_CTRL` and continues through the end of `RCC_EP_DEV0_1_EP_PCIE_CNTL`; the following `RCC_EP_DEV0_1_EP_PCIE_INT_CNTL` register belongs to the next chunk.

The covered area is concentrated around these address blocks and register families:

- Device 2 function reset and power-state controls: `DEV2_PF*_FLR_RST_CTRL`, `BIF_DEV2_PF*_DSTATE_VALUE`, `DEV2_PF*_D3HOTD0_RST_CTRL`, and port-level `BIF_PORT*_DSTATE_VALUE`.
- `nbio_nbif0_bif_misc_bif_misc_regblk`, including scratch registers, interrupt line polarity/enable, outstanding VC allocation, BIFC miscellaneous controls, BME error logs, DMA attribute override controls, PASID checks/status, SDP controls, performance counters, power-gating controls, SMN master controls, virtual-wire change controls, timeout detection, credit allocation, Z10 status, BDF controls, and common performance counter state.
- `nbio_nbif0_nbif_sion_SIONDEC`, covering SION client burst targets, time slots, pool-credit allocations, and global SION control.
- `nbio_nbif0_bif_ras_bif_ras_regblk`, covering central and leaf RAS controls/status plus RAS interrupt/vwire handoff fields.
- Initial RCC PCIe decode blocks for downstream, downstream-port, and endpoint device 0: `RCC_DWN_DEV0_1_*`, `RCC_DWNP_DEV0_1_*`, and `RCC_EP_DEV0_1_EP_PCIE_CNTL`.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only. It contains no C functions, structs, global variables, allocations, locks, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and NBIO 7.11.0 hardware registers. Each field is represented by the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, or compose that field.

The sibling `nbio_7_11_0_offset.h` header supplies register addresses and base indices. This file supplies the field layout used by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. The direct source-tree consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both the offset and mask headers for NBIO 7.11 register programming.

## Important Macro Families

### Device 2 Reset and D-State Controls

The chunk begins inside `DEV2_PF2_FLR_RST_CTRL` and then covers `DEV2_PF3_FLR_RST_CTRL` through `DEV2_PF6_FLR_RST_CTRL`. These registers expose per-PCI-function function-level reset policy bits:

- `PF_CFG_EN`, `PF_CFG_FLR_EXC_EN`, and `PF_CFG_STICKY_EN` describe configuration-space reset participation and sticky behavior.
- `PF_PRV_EN` and `PF_PRV_STICKY_EN` describe private register reset behavior.
- `FLR_GRACE_MODE`, `FLR_GRACE_TIMEOUT`, `FLR_DMA_DUMMY_RSPSTS`, and `FLR_HST_DUMMY_RSPSTS` describe reset grace handling and dummy response status behavior.

`BIF_DEV2_PF0_DSTATE_VALUE` through `BIF_DEV2_PF6_DSTATE_VALUE` expose target and acknowledged PCI power-state values for device 2 functions, plus `NEED_D3TOD0_RESET` bits that indicate whether a D3hot-to-D0 transition requires reset handling.

`DEV2_PF0_D3HOTD0_RST_CTRL` through `DEV2_PF6_D3HOTD0_RST_CTRL` provide a parallel reset-control family for D3hot-to-D0 transitions. These fields are narrower than the FLR reset controls and only cover config/private reset enables and sticky bits. `BIF_PORT0_DSTATE_VALUE`, `BIF_PORT1_DSTATE_VALUE`, and `BIF_PORT2_DSTATE_VALUE` expose target D-state and reset-needed bits at the port level.

### BIF Miscellaneous Control and Error Logging

The `nbio_nbif0_bif_misc_bif_misc_regblk` portion starts with simple scratch and interrupt-line controls:

- `MISC_SCRATCH` exposes a full 32-bit scratch field.
- `INTR_LINE_POLARITY` and `INTR_LINE_ENABLE` provide per-line control for interrupt line polarity and enable state.
- `OUTSTANDING_VC_ALLOC` records virtual-channel allocation limits and current outstanding count fields.

`BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` are dense policy registers. They include fields for client response mode, FLR response behavior, reset clock gating, soft reset, GMI request class selection, pass-through behavior, read request ID selection, flush-on-reset behavior, interrupt acknowledgement, and GFX/VCN/SDMA display-related overrides. These fields are broad integration points because they influence how NBIF responds to PCIe, internal fabric, and reset events.

`BIFC_LC_TIMER_CTRL` provides a link-control timer field. `BIFC_RCCBIH_BME_ERR_LOG0` and `BIFC_RCCBIH_BME_ERR_LOG1` define captured Bus Master Enable error information, including error-valid, requester ID, client ID, subclient ID, attribute fields, address, and VF-related identifiers. These are diagnostic state registers used to identify illegal or unexpected DMA/BME activity.

### DMA Attributes, PASID, SDP, and Activity Controls

The chunk defines a large matrix of DMA attribute override registers:

- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `DEV2_F6_F7` cover device/function pairs across devices 0, 1, and 2.
- Each register carries per-function override enables and replacement values for traffic class, snoop, relaxed ordering, PASID transaction attribute, and function ID.
- `BIFC_DMA_ATTR_CNTL2_DEV0`, `DEV1`, and `DEV2` add per-device default and override controls for destination indication, SP, PRIV, SEC, PASID address, and process address space behavior.

These macros are especially sensitive because DMA attributes affect PCIe ordering, snooping, security tagging, and PASID-based address translation.

`BIFC_PASID_CHECK_DIS`, `BIFC_PASID_STS`, `BIFC_ATHUB_ACT_CNTL`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, and `BIFC_SDP_CNTL_2` cover PASID validation controls/status, ATHUB activity gating or status policy, and SDP flow-control or response behavior. `BIF_PASID_ERR_LOG` has no field definitions in this slice, while `BIF_PASID_ERR_CLR` defines a broad set of clear bits for PASID error categories across clients and traffic types.

### Performance, Power, Clock, and Interrupt-Related Controls

Several small families expose NBIF telemetry and low-power behavior:

- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the low/high MMIO/DMA read/write counter registers define event selection, enable/clear bits, and split counter values.
- `NBIF_PERF_COM_COUNT_ENABLE`, `NBIF_BX_PERF_CNT_FSM`, and `NBIF_COM_COUNT_VALUE` expose common performance counting enable, FSM state, and count value fields.
- `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` cover power-gating master/slave handshakes, reset select, clock request overrides, and status selection.
- `NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK` cover medium-grain clock gating and light/deep sleep controls on LCLK-related logic.
- `NBIF_INTX_DSTATE_MISC_CNTL`, `NBIF_PENDING_MISC_CNTL`, `EP0_INTR_URGENT_CAP`, `EP1_INTR_URGENT_CAP`, `EP2_INTR_URGENT_CAP`, and `EP_PEND_BLOCK_MSK` describe interrupt/D-state wake behavior, pending-state handling, urgency capabilities, and endpoint pending-block masks.
- `NBIF_PWRBRK_REQUEST`, `OBFF_EMU_CFG`, `NBIF_VWIRE_CTRL`, `NBIF_SDP_VWR_VCHG_*`, and `NBIF_SHUB_TODET_*` support power-break requests, OBFF emulation, virtual-wire control/change/reset/trigger, and system hub timeout detection or sync-flood signaling.

The local `nbio_v7_11.c` driver code does not directly reference most names in this chunk, but it uses the same mask-header convention for NBIO initialization, doorbells, interrupt handling, memory access enablement, clock-gating, light-sleep, register remap, and PCIe-port access. These fields are available for the same NBIO 7.11 hardware block when future code or firmware-facing paths need them.

### SMN Master and GMI/SST/SDP Credit Controls

`SMN_MST_CNTL0`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL1` through `SMN_MST_EP_CNTL5` define System Management Network master behavior and endpoint attributes. They include fields for request attributes, PASID, function ID, destination, address windowing, security/privilege attributes, poison/response handling, and endpoint-specific request shaping.

`BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3` expose weighted round-robin values. `BIFC_HRP_SDP_*`, `BIFC_GMI_SDP_*`, and `BIFC_GMI_SST_*` pool-credit allocation registers define request, data, read-response, and write-response credit counts. `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, and `BIFC_GSI_CNTL` add threshold, host arbitration, and global status interrupt policy fields.

These are hardware flow-control knobs. Incorrect programming can starve traffic, overrun pool credits, or perturb ordering/latency between PCIe, GMI, SDP, SST, and internal hub clients.

### SION Arbitration and Credit Shaping

The `nbio_nbif0_nbif_sion_SIONDEC` block is highly regular. For clients `CL0`, `CL1`, and `CL2`, it defines full-width fields for:

- Read-response burst target and time slot registers.
- Write-response burst target and time slot registers.
- Request burst target and time slot registers.
- Request, data, read-response, and write-response pool-credit allocation registers.

`SION_CNTL_REG0` contains many control fields: arbitration enablement, time-slot quantum, weight, client limit, response ordering, starvation-related controls, request/response gating, and debug/status selector fields. `SION_CNTL_REG1` adds a smaller set of control/status fields.

These masks describe the programmable arbitration contract for SION traffic. They are persistent hardware policy until reset or rewritten.

### BIF RAS Controls and Status

The `nbio_nbif0_bif_ras_bif_ras_regblk` section defines central and leaf reliability, availability, and serviceability controls:

- `BIFL_RAS_CENTRAL_CNTL` includes interrupt/event enable and propagation/stall controls.
- `BIFL_RAS_CENTRAL_STATUS` exposes event receive, fatal/nonfatal/correctable/error status, poison, parity, and propagation/stall status bits.
- `BIFL_RAS_LEAF0_CTRL`, `BIFL_RAS_LEAF1_CTRL`, and `BIFL_RAS_LEAF2_CTRL` each define error detection, poison/parity/receiver-error event enablement, stall enablement, generated and propagated error-event controls, debug enables, and RAS interrupt enablement.
- `BIFL_RAS_LEAF0_STATUS`, `LEAF1_STATUS`, and `LEAF2_STATUS` expose received error events, poison/parity detection, generated event status, egress stalled status, propagated event status, and propagated egress stalled status.
- `BIFL_IOHUB_RAS_IH_CNTL` and `BIFL_RAS_VWR_FROM_IOHUB` connect BIF RAS state to interrupt-handler and virtual-wire signaling.

RAS status fields are diagnostic and may be sticky or clear-on-write according to hardware behavior outside this header. The masks alone do not document the clear sequence, interrupt routing policy, or error containment rules.

### RCC PCIe Decode Blocks

The chunk ends with the first RCC PCIe decode blocks:

- `RCC_DWN_DEV0_1_DN_PCIE_RESERVED`, `SCRATCH`, `CNTL`, `CONFIG_CNTL`, `RX_CNTL2`, `BUS_CNTL`, and `CFG_CNTL` cover downstream decode behavior, hidden-register decode enables for PCIe generations 2 through 5, unsupported-request reporting, immediate PMI disable, AER completion timeout read-only behavior, LTR message UR behavior, and FLR extend mode.
- `RCC_DWNP_DEV0_1_PCIE_ERR_CNTL`, `RX_CNTL`, `LC_CNTL2`, and `LTR_MSG_INFO_FROM_EP` cover downstream-port error reporting, immediate error-message behavior, received-error clear bits, max-payload/traffic-class/short-prefix ignore controls, completion timeout disable, RCB FLR timeout disable, link-state and link-bandwidth notification disable, and captured LTR message information.
- `RCC_EP_DEV0_1_EP_PCIE_SCRATCH` and `RCC_EP_DEV0_1_EP_PCIE_CNTL` cover endpoint scratch, unsupported-request reporting disable, malformed atomic operations, and LTR-message unsupported-request ignore behavior.

The next chunk continues the endpoint PCIe interrupt, status, RX, bus, config, and LTR controls.

## Control Flow and State Behavior

This header chunk has no software control flow. It affects driver behavior at compile time by deciding which bits are read or written when code uses generated register helpers.

The state described by the macros is hardware state in the NBIO block. It includes reset policy, PCI power-state target/acknowledgement values, D3hot-to-D0 reset requirements, DMA attribute overrides, PASID validation and error clears, BME error logs, performance counter selection and split counter values, power-gating and clock-gating controls, SMN request attributes, virtual-wire triggers, timeout detection, arbitration weights, SION credit limits, RAS event controls/status, and RCC PCIe error/link/decode policy.

Some fields are durable configuration until reset or rewrite, such as DMA attribute overrides, SION arbitration limits, RAS event enables, hidden-register decode enables, and PCIe RX ignore controls. Other fields are status or diagnostic captures, such as D-state ack values, BME error logs, PASID status, performance counter values, RAS status, and LTR message information. A third class is command-like or clear-like, such as PASID error clear bits and downstream-port received-error clear bits. Code that writes these fields must respect hardware sequencing and avoid treating all masks as ordinary read-modify-write configuration.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_11_0_offset.h` provides the matching register addresses and base-index macros.
- `nbio_7_11_0_default.h`, where present for a register, provides reset/default values.
- AMDGPU helper macros compose and decode fields by naming the register and field, deriving the `__SHIFT` and `_MASK` constants from this header.

Observed source-tree integration:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` directly includes `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h`. It uses the same generated masks to implement NBIO 7.11 operations: revision readout, memory-controller access enable/disable, doorbell ranges, interrupt-handler setup, HDP flush register offsets, clock-gating and light-sleep controls, register remap, and initial PCIe/NBIO tuning.
- `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c` and `dcn351_resource.c` include the NBIO 7.11 offset header, so display resource code is aware of NBIO register addresses even though this mask chunk is not directly included there.
- Cross-generation NBIO and NBIF headers contain similarly named families for RCC PCIe, RAS, and device reset/D-state controls, but layouts are not guaranteed identical. Consumers must use the mask header matching the active IP version selected by the driver.

## Risks

- Bitfield drift is high impact. These macros encode a hardware contract; a wrong shift or mask can silently write the wrong bit in PCIe, reset, DMA, RAS, or power-management registers.
- Reset and D-state fields can affect FLR and D3hot-to-D0 recovery. Misprogramming can leave PCI functions partially reset, fail to preserve sticky state, or produce dummy responses in the wrong reset phase.
- DMA attribute and PASID override fields affect transaction ordering, snooping, privilege/security attributes, destination indications, and address-space semantics. Incorrect settings can cause data corruption, isolation failures, or hard-to-debug IOMMU/PASID faults.
- RAS enable/status fields interact with error containment and interrupt signaling. Enabling stalls or propagation incorrectly can turn recoverable fabric errors into hangs; disabling events can hide real hardware failures.
- SION, WRR, and credit allocation fields can perturb internal traffic fairness and liveness. Overly aggressive limits or weights can starve clients or trigger timeout paths.
- RCC PCIe controls can mask protocol errors, alter FLR timeout behavior, disable notifications, or expose hidden config spaces. These should be changed only when the matching hardware specification and platform policy require it.
- Many status/clear fields likely have special write semantics. Generic read-modify-write code can accidentally clear diagnostic state or fail to clear latched status if the field is write-one-to-clear.

## Test Signals

Useful validation for changes involving this chunk is mostly integration and hardware oriented:

- Build coverage: compile AMDGPU with NBIO 7.11 support to catch missing or misspelled generated macros in `nbio_v7_11.c` or other consumers.
- Header consistency: compare every touched register against the matching `nbio_7_11_0_offset.h` register names and any available default-header names; regenerated headers should preserve paired `__SHIFT` and `_MASK` definitions.
- Boot/probe smoke tests on NBIO 7.11 hardware: confirm AMDGPU probes, reads revision and memory size, enables MC access, configures doorbells, and initializes interrupt handling without PCIe AER regressions.
- Runtime reset tests: exercise FLR, suspend/resume, and D3hot-to-D0 transitions for affected device/function paths while watching for PCIe timeouts, dummy response errors, and device recovery failures.
- DMA/PASID tests: run KFD/ROCm or IOMMU/PASID workloads and monitor for PASID error logs, BME error logs, transaction faults, and data corruption.
- RAS tests: inject or observe correctable/nonfatal/fatal error paths if platform support exists, verifying RAS interrupt delivery and status reporting without unexpected fabric stalls.
- Performance/power tests: check NBIF performance counter readability, clock-gating/light-sleep behavior, and wake/pending interrupt behavior across idle, load, and resume.
