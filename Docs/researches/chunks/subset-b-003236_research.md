# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 24526-26923

## Scope

This chunk covers generated shift and mask macros from the NBIO 7.4 AMD GPU register mask header. It starts in the middle of the `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` mask definitions and ends at the `BIF_CFG_DEV0_EPF0_0_PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` register comment, before that register's field definitions in the next chunk.

The covered range includes:

- DMA transaction attribute override masks for device 0 functions F0-F7, including ID-based ordering, relaxed ordering, no-snoop, and block-level controls for posted and non-posted traffic.
- BIF client controls for BME dummy responses, transaction credit thresholds, host/slave arbitration, GSI request/completion arbitration, PCIe function control, PASID checking/status, ATHUB activity, performance counters, MMIO/DMA counter values, and register-interface error injection/logging.
- SMN master endpoint control, self-ring buffer/vector controls, INTx/D-state pending controls, GMI weighted round-robin weights, and power-break request fields.
- Per-function atomic unsupported-request error logs, DMA MP4/PASID error logging and clearing, NBIF virtual-wire control, virtual-wire change disable/reset/trigger registers, and LCLK clock/power-gating controls.
- RCC PFC blocks for AMDGFX and AMDGFXAZ latency tolerance reporting, PME restore, sticky restore state, and auxiliary power control.
- BIF reset block masks for hard/soft reset, graphics/VPU reset, PF function-level reset, D3hot-to-D0 reset, reset/power/D-state interrupt status and masks, and PF/VF FLR reset strobes.
- BIF RAS central/leaf control and status registers, IOHUB RAS interrupt handling, and RAS virtual-wire state from IOHUB.
- SUM indexed register access fields.
- The start of the PF0 PCI configuration-space bitfield map, from vendor/device IDs through base address registers, ROM BAR, capability pointers, power-management capability, PCIe device/link capability and control/status registers, MSI/MSI-X capability registers, vendor-specific enhanced capability registers, and virtual-channel capability/resource registers. The final line is the serial-number enhanced capability comment only.

This header chunk is generated data: it defines preprocessor constants only. It contains no functions, structs, runtime variables, locks, storage objects, or executable control flow.

## Purpose

The purpose of this section is to provide the bit-level ABI used by AMDGPU NBIO 7.4 code when composing and decoding MMIO and PCI configuration register values. Each hardware field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or place that field.

Driver code combines these constants with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The sibling NBIO offset/default headers supply register addresses and reset values; this file supplies the field layout for those addresses.

## Important Macro Families

### DMA, Ordering, and BME Controls

The `BIFC_DMA_ATTR_OVERRIDE_DEV0_F*_F*` registers pack two functions per register. Each function gets 2-bit fields for posted and non-posted IDO override, relaxed-ordering override, no-snoop override, and block-level selection for IDO/non-IDO traffic. The chunk begins after the F0/F1 shifts and includes the F0/F1 masks plus complete F2/F3, F4/F5, and F6/F7 shift/mask groups.

`BIFC_DMA_ATTR_CNTL2_DEV0` adds per-function `BLKLVL_BYPASS_PCIE_IDO_CONTROL` bits for F0-F7. `BME_DUMMY_CNTL_0` carries per-function dummy response status fields used when bus mastering is disabled or being handled defensively. These fields sit directly on PCIe transaction attribute behavior, so consumers must preserve function-specific packing and avoid applying a PF0 mask to another function's bit positions.

### Arbitration, GSI, PASID, and Performance Counters

`BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, and `BIFC_GSI_CNTL` describe credit-allocation thresholds and arbitration modes for read/write virtual channels, host/slave arbitration, SDP/SMN request arbitration, completion response arbitration, completion interleaving, and unsupported-request generation for several completion sources.

`BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, `BIFC_PASID_STS`, and `BIFC_ATHUB_ACT_CNTL` expose PCIe function controls, PASID check bypass/status, SDP disconnect hysteresis/disable policy, and ATHUB activity status. These definitions are integration points for address-translation, KFD/PASID, virtualization, and link-idle policy code.

`BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the four `BIFC_PERF_CNT_*` data registers define enable, reset, selector, and 32-bit count fields for MMIO read/write and DMA read/write counters. The enable/reset bits are command-like controls around hardware counters; the count registers expose observed hardware state.

### Error Logging, Virtual Wires, and Power/Clock Controls

The chunk defines per-function `BIF_ATOMIC_ERR_LOG_DEV0_F0` through `_F7` fields for unsupported atomic opcode, request-enable-low, length, and non-relaxed request conditions. Each log has matching clear bits in the upper half of the register. `BIF_DMA_MP4_ERR_LOG`, `BIF_PASID_ERR_LOG`, and `BIF_PASID_ERR_CLR` provide additional DMA/PASID error capture and clearing.

`NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_*`, and `NBIF_SDP_VWR_*` define virtual-wire control, virtual-wire change disable bits, reset controls, trigger controls, and write-trigger behavior. These are used around low-power state signaling and sideband state propagation.

`NBIF_MGCG_CTRL_LCLK`, `NBIF_DS_CTRL_LCLK`, `SMN_MST_CNTL0`, and `SMN_MST_EP_CNTL1/2/3/4/5` describe LCLK medium-grain clock gating, deep-sleep controls, and SMN master endpoint behavior. These fields are power-management sensitive and generally need to be programmed in the sequencing expected by the NBIO initialization and suspend/resume paths.

### RCC PFC, Reset, and RAS Blocks

The `RCC_PFC_AMDGFX_*` and `RCC_PFC_AMDGFXAZ_*` groups cover latency tolerance reporting controls, PME restore fields, sticky restore registers, and auxiliary power controls for two RCC PFC address blocks. These fields persist or restore PCIe/power-management-facing state across power transitions.

The `nbio_nbif0_bif_rst_bif_rst_regblk` portion covers reset control and interrupt state: `HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, `SELF_SOFT_RST`, `BIF_GFX_DRV_VPU_RST`, `BIF_RST_MISC_CTRL*`, per-PF FLR and D3hot/D0 reset controls, interrupt status/mask registers for instance reset, PF FLR, D3hot/D0, power, PF D-state, and PF0 VF FLR, plus PF/PF0-VF reset strobe registers and per-PF D-state value registers.

The `nbio_nbif0_bif_ras_bif_ras_regblk` portion defines BIF RAS central control/status, leaf control/status registers, IOHUB RAS interrupt handling, and RAS virtual-wire state from IOHUB. These masks back reliability diagnostics and error-signaling code rather than normal data-path configuration.

### PF0 PCI Configuration Space

The chunk begins the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block for device 0 endpoint PF0 PCI configuration space. It includes:

- Standard header fields such as vendor ID, device ID, command/status, revision/class codes, cache line, latency, header, BIST, BAR1-BAR6, adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- Power-management capability fields such as PME support, D-state support, PME enable/status, data select/scale, and power-management state.
- PCIe capability fields for device type, slot/interrupt message number, device capability/control/status, link capability/control/status, and second-generation device/link capability/control/status.
- MSI and MSI-X capability fields for capability lists, enable bits, vector count/control, message address/data, mask/pending state, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields and scratch registers.
- PCIe virtual-channel enhanced capability, port VC capability/control/status, and VC0/VC1 resource capability/control/status fields.

The range ends on the `BIF_CFG_DEV0_EPF0_0_PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` comment. Its actual `CAP_ID`, `CAP_VER`, and `NEXT_PTR` field macros are outside this chunk.

## Control Flow and State Behavior

There is no runtime control flow in this file. The header influences compiled driver behavior by defining how other C code shifts, masks, sets, clears, and reads hardware register fields.

The persistent state described here lives in hardware registers, not in this header. Important state includes per-function DMA transaction attribute policy, PASID checking state, SDP disconnect policy, performance counter enables/selectors/counts, sticky error-log bits, virtual-wire change state, clock/power gating policy, reset and interrupt mask/status bits, RAS status bits, and PF0 PCI configuration/capability state.

Several fields are not ordinary durable configuration values. Error-log clear bits, PASID error clear bits, reset strobes, virtual-wire triggers, performance-counter resets, FLR/D3hot reset controls, interrupt clear/status bits, and PCIe control bits such as `INITIATE_FLR` have command or side-effect semantics. Callers must use the sequencing, polling, and timeout rules implemented by the owning NBIO/PCIe/AMDGPU paths; the macros alone do not encode ordering.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_4_offset.h` provides register offsets and base-index definitions corresponding to these field names.
- `nbio_7_4_default.h` provides reset/default values where generated.
- Common AMDGPU bitfield helpers consume the `__SHIFT` and `_MASK` names to avoid hard-coded bit positions.

Likely integration points in the driver tree include:

- NBIO 7.4 initialization, suspend/resume, reset, and interrupt code that programs BIF reset, D-state, power, clock-gating, virtual-wire, and RCC PFC state.
- PCIe capability and error-handling paths that inspect or update PF0 command/status, link status, MSI/MSI-X, virtual-channel, advanced capability, and FLR-related fields through MMIO or PCI config access helpers.
- PASID/KFD/IOMMU integration paths that depend on PASID check/status and PASID error log/clear fields.
- RAS and diagnostics paths that consume BIF RAS central/leaf status and atomic/DMA/PASID error logs.
- Performance/debug paths that enable, reset, select, and read the BIFC MMIO/DMA counters.
- Virtualization/SR-IOV-adjacent flows that must keep per-function masks, PF/VF reset status, and PCIe function-specific state separated.

## Risks

- The chunk starts mid-register: `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` shift macros are in the previous chunk, while its masks begin here. Any generated documentation or tooling must merge adjacent chunks before treating that register as complete.
- The chunk ends at a register comment. `BIF_CFG_DEV0_EPF0_0_PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` is mentioned but its fields are not included in this range.
- Many groups repeat nearly identical layouts across functions F0-F7. Copying a mask between functions without preserving the encoded bit positions can silently target the wrong PCIe function.
- Clear, reset, trigger, and strobe fields have side effects. Read-modify-write code must not accidentally set upper-half clear bits or reset bits while updating unrelated fields.
- PCIe configuration fields mirror standardized PCI/PCIe capability layout, but this generated header is ASIC-specific. Cross-generation NBIO headers can expose similar names with different offsets, defaults, or supported bits.
- Some fields touch low-level ordering, no-snoop, relaxed-ordering, PASID, VC, MSI/MSI-X, link, reset, and power behavior. Incorrect programming can cause data ordering bugs, lost interrupts, failed FLR/D-state transitions, link errors, or hidden RAS diagnostics.

## Test Signals

Useful validation for code using these macros includes:

- Compile coverage for NBIO 7.4 sources that include `nbio_7_4_sh_mask.h`, especially code using `REG_SET_FIELD`/`REG_GET_FIELD` with fields in this chunk.
- Boot and GPU probe logs showing successful NBIO discovery, PCIe capability setup, MSI/MSI-X enablement, and absence of unexpected BIF reset, D-state, or power interrupt status.
- Suspend/resume and runtime power-management tests that preserve RCC PFC sticky restore state, virtual-wire behavior, LCLK clock-gating/deep-sleep settings, and PF D-state values.
- FLR and PCI reset tests that exercise per-PF FLR/D3hot-D0 reset controls and verify matching interrupt status/mask behavior.
- RAS/error-injection or fault-observation tests that confirm atomic, DMA MP4, PASID, and BIF RAS status bits latch and clear as expected.
- PASID/KFD workload tests that run with PASID checking enabled and verify no unexpected PASID status/error logs.
- Performance/debug tests that enable and reset BIFC MMIO/DMA counters, then confirm counter registers increment for matching traffic.
- PCIe link and capability inspection through kernel logs or config-space reads, checking device/link capability/control/status, MSI/MSI-X table/PBA fields, and VC resource negotiation where supported.
