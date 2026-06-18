# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 102061-104473

## Scope

This chunk covers a generated portion of the AMD NBIO 7.2.0 register shift/mask header. The range starts in the middle of the `NP_DMA_DROPPED_LOG_LOWER` bit definitions and ends in the middle of the `PARITY_ERROR_STATUS_UCP_GRP2` bit definitions. The covered register families are:

- Non-posted DMA dropped-log bitmaps: tail of `NP_DMA_DROPPED_LOG_LOWER` and full `NP_DMA_DROPPED_LOG_UPPER`.
- PCIe vendor-defined-message controls: `PCIE_VDM_NODE0_CTRL4`, `PCIE_VDM_CNTL2`, and `PCIE_VDM_CNTL3`.
- Crossbar virtual-channel stall controls for XBAR ports 0 through 6, split into request (`*_0`) and response (`*_1`) enable fields.
- Fast register and fast-register-control base address registers: `FASTREG_BASE_ADDR_LO/HI` and `FASTREGCNTL_BASE_ADDR_LO/HI`.
- Scratch, trap request/response, trap data, and 16 trap comparator/programming slots.
- Secondary-bus PCI bridge configuration fields: command, bus numbering, I/O and memory windows, interrupt/bridge controls, power-management status, slot capability, root control, and device control 2.
- MCA SMN interrupt address/control fields.
- RAS/security configuration block markers followed by parity-control, parity-severity, global RAS status, uncorrected parity status, corrected parity status, corrected parity counters, and the beginning of unconsumed-poison parity status groups.

The file is a generated hardware bitfield map. This chunk defines preprocessor constants only: no C functions, structs, variables, runtime storage, or executable control flow are present.

## Purpose

The purpose of this header section is to describe how NBIO 7.2.0 hardware registers pack their fields into 32-bit values. Each field is represented by the standard AMD register-header pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or compose the field.

Driver code pairs these definitions with `nbio_7_2_0_offset.h`, which supplies register addresses such as `regPCIE_VDM_CNTL2`, `regSTALL_CONTROL_XBARPORT0_0`, and `regPARITY_ERROR_STATUS_UCP_GRP0`. AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` then use the shift/mask constants to read, update, and decode NBIO MMIO state without hard-coded bit positions.

## Important Macro Families

### DMA Dropped Logs

The chunk begins in the per-bit definitions for `NP_DMA_DROPPED_LOG_LOWER` and then covers the full `NP_DMA_DROPPED_LOG_UPPER` register. Each register exposes 32 one-bit fields named after its bit index. Together these form a low/high bitmap for non-posted DMA dropped-log state. The lower register definition is partial in this chunk because its first shifts and masks live in the previous chunk; the upper register is complete here with shifts `0x0` through `0x1f` and matching one-bit masks from `0x00000001L` through `0x80000000L`.

These fields are status/logging oriented. Code that consumes them should treat the pair as a bitmap, not as independent configurable knobs, and should preserve ordering with any hardware-specified clear/read semantics.

### PCIe VDM Controls

`PCIE_VDM_NODE0_CTRL4` defines an 8-bit bus range base, an 8-bit bus range limit, and a high `NODE0_PRESENT` bit. This describes PCIe VDM routing or node presence for bus-number ranges.

`PCIE_VDM_CNTL2` and `PCIE_VDM_CNTL3` expose master identity fields for VDM-related protocols. `PCIE_VDM_CNTL2` contains `VdmP2pMode`, `MCTPMasterValid`, and `MCTPMasterID`; `PCIE_VDM_CNTL3` contains `APMTPMasterValid` and `APMTPMasterID`. The master IDs occupy the upper 16 bits, while valid bits are at bit 15. These fields likely integrate with PCIe management-message handling and peer-to-peer VDM routing.

### XBAR Stall Controls

`STALL_CONTROL_XBARPORT0_0` through `STALL_CONTROL_XBARPORT6_1` define repeated control registers for NBIO crossbar ports. The `_0` registers provide `StallVC*ReqEn` fields, and the `_1` registers provide `StallVC*RspEn` fields. Covered virtual channels are VC0, VC1, VC2, VC3, VC4, VC5, and VC7. Each field is two bits wide and spaced on 4-bit boundaries with masks such as `0x00000003L`, `0x00000030L`, and `0x30000000L`.

The repeated layout suggests per-port, per-virtual-channel control over request and response stalling. These fields are debug/flow-control sensitive: changing them can intentionally throttle or block NBIO traffic classes, so consumers must avoid treating similarly named fields across ports as interchangeable if a platform has fewer or differently wired ports.

### Fast Register Base Addresses

`FASTREG_BASE_ADDR_LO` and `FASTREGCNTL_BASE_ADDR_LO` define low address bits in the range covered by mask `0xFFFFFFFCL`, implying alignment on at least a 4-byte boundary. Their corresponding high registers, `FASTREG_BASE_ADDR_HI` and `FASTREGCNTL_BASE_ADDR_HI`, expose 32 high bits. Together these form 64-bit base addresses for a fast-register aperture and its control aperture.

These fields are address-programming state. Incorrect composition of the low and high halves can point NBIO fast-register access at the wrong aperture.

### Scratch and Trap Request/Response Windows

`SCRATCH_4` and `SCRATCH_5` expose full 32-bit scratch values. The trap block then defines a low-level request/response mailbox:

- `TRAP_STATUS` contains `ReqDone`, indicating request completion.
- `TRAP_REQUEST0` through `TRAP_REQUEST5` carry request metadata. Fields include `Valid`, `ID`, `Type`, `Write`, `Address`, `Mask`, `DataSize`, `FirstBe`, `LastBe`, `FuncID`, `VFuncActive`, and `VFunc`.
- `TRAP_REQUEST_DATASTRB0/1` and `TRAP_REQUEST_DATA0` through `TRAP_REQUEST_DATA15` carry byte strobes and 16 words of request data.
- `TRAP_RESPONSE_CONTROL` contains `Valid`, `Error`, and `DWords`.
- `TRAP_RESPONSE0` contains response `ID` and `DataSize`.
- `TRAP_RESPONSE_DATA0` through `TRAP_RESPONSE_DATA15` expose full 32-bit response payload words.

This block is an MMIO-visible trap transaction interface. The fields provide the control plane for constructing a request, providing byte enables and data, polling request completion, and reading a response. The macros alone do not encode required ordering, timeout behavior, or clear semantics; any user must follow the owning NBIO trap protocol in driver code and hardware documentation.

### Trap Comparator Slots

The range includes slots `TRAP0` through `TRAP15`. Each slot has:

- `TRAPn_CONTROL0`, with `TRAP_ENABLE` and `TRAP_RESPONSE` fields.
- `TRAPn_ADDRESS_LO` and `TRAPn_ADDRESS_HI`, each full-width address halves.
- `TRAPn_COMMAND`, with a `TRAP_COMMAND` field.
- `TRAPn_ADDRESS_LO_MASK`, `TRAPn_ADDRESS_HI_MASK`, and `TRAPn_COMMAND_MASK`, each full-width masks.

These slots are likely address/command match rules for trapping specific NBIO transactions and defining whether/how a response is generated. The full-width address and mask fields indicate programmable comparators rather than simple enumerated status registers. Misprogramming a slot can trap the wrong traffic or fail to trap intended traffic.

### Secondary-Bus PCI Bridge Fields

The `SB_*` macros mirror standard PCI/PCIe bridge configuration fields:

- `SB_COMMAND` includes I/O space, memory space, bus master, special cycle, memory write/invalidate, VGA palette snoop, parity-error response, SERR, fast back-to-back, interrupt-disable, and capability-list bits.
- `SB_SUB_BUS_NUMBER_LATENCY` packs primary, secondary, subordinate bus numbers, and secondary latency timer.
- `SB_IO_BASE_LIMIT`, `SB_MEM_BASE_LIMIT`, `SB_PREF_BASE_LIMIT`, `SB_PREF_BASE_UPPER`, `SB_PREF_LIMIT_UPPER`, and `SB_IO_BASE_LIMIT_HI` define downstream bridge windows.
- `SB_IRQ_BRIDGE_CNTL`, `SB_EXT_BRIDGE_CNTL`, `SB_PMI_STATUS_CNTL`, `SB_SLOT_CAP`, `SB_ROOT_CNTL`, and `SB_DEVICE_CNTL2` define interrupt, bridge, power-management, hotplug/slot, root, and device-control behavior.

These definitions let NBIO code decode or program the emulated/internal bridge-facing configuration space. They are integration points with PCI enumeration, bridge window setup, hotplug signaling, power management, and error-reporting behavior.

### MCA SMN Interrupt Fields

`MCA_SMN_INT_REQ_ADDR`, `MCA_SMN_INT_MCM_ADDR`, and `MCA_SMN_INT_APERTUREID` are full-width address/aperture fields. `MCA_SMN_INT_CONTROL` exposes at least an interrupt-enable bit. These fields define how NBIO routes MCA-related SMN interrupt requests, and they connect the NBIO I/O hub path to machine-check/error signaling infrastructure.

### RAS Parity Control, Severity, and Status

The chunk enters the RAS and security configuration decoder area and covers:

- `PARITY_CONTROL_0`, with `ParityEnable`, `ParityErrorInjectionEnable`, and `ParityErrorInjectionGroup`.
- `PARITY_CONTROL_1`, with 16 `ParityErrGenId*` bits used to target error generation/injection IDs.
- Severity controls for uncorrected, corrected, and unconsumed-poison parity reporting: `PARITY_SEVERITY_CONTROL_UNCORR_0`, `PARITY_SEVERITY_CONTROL_CORR_0`, and `PARITY_SEVERITY_CONTROL_UCP_0`, each with a common enable bit and per-group severity/enable bits for groups 0 through 7.
- `RAS_GLOBAL_STATUS_LO` and `RAS_GLOBAL_STATUS_HI`, which expose aggregate parity status, fatal/non-fatal/corrected poison and non-poison error flags, parity interrupt flags, multiple-error flags, and other global RAS status indicators.
- `PARITY_ERROR_STATUS_UNCORR_GRP0` through `GRP7`, each a 32-bit bitmap of `ParityErrDetected_Id0` through `Id31`.
- `PARITY_ERROR_STATUS_CORR_GRP0` through `GRP7`, with the same 32-ID bitmap structure for corrected parity errors.
- `PARITY_COUNTER_CORR_GRP0` through `GRP7`, each exposing an 8-bit `ParityErrCount`.
- `PARITY_ERROR_STATUS_UCP_GRP0`, `GRP1`, and the start of `GRP2`, again using one-bit status fields for detected IDs.

This RAS section is the most stateful part of the chunk. It defines enablement, error injection, severity routing, aggregate status, per-group/per-ID status bitmaps, and corrected-error counters. The naming implies integration with AMDGPU RAS collection, MCA reporting, and diagnostic injection paths.

## Control Flow and State Behavior

There is no runtime control flow in this header. It influences compiled driver behavior by determining how register helper macros compose and decode NBIO register values.

The durable or latched state described here lives in hardware registers. Examples include PCIe VDM routing state, XBAR stall enable state, fast-register base addresses, scratch/trap mailbox payloads, trap comparator configuration, PCI bridge configuration windows, MCA interrupt routing, parity control/severity policy, RAS aggregate status, per-ID parity error status, and corrected-error counters.

Several fields are status or command-like rather than ordinary persistent configuration. `TRAP_STATUS__ReqDone`, `TRAP_RESPONSE_CONTROL__Valid`, RAS global status bits, parity error-detected bitmaps, and corrected counters are observed hardware state. `PARITY_CONTROL_0__ParityErrorInjectionEnable`, `PARITY_CONTROL_1__ParityErrGenId*`, trap request `Valid`, and trap slot enable fields can cause hardware actions or alter transaction interception. Correct consumers need protocol-specific read/modify/write, poll, and clear ordering that this generated header does not express.

## Dependencies and Integration Points

This chunk depends on the generated AMDGPU register-header convention:

- `nbio_7_2_0_offset.h` provides the actual NBIO register offsets and base indices for the register names defined here.
- Adjacent `nbio_7_2_0_sh_mask.h` chunks provide families that start before or continue after this range, including the beginning of `NP_DMA_DROPPED_LOG_LOWER` and the remainder of `PARITY_ERROR_STATUS_UCP_GRP2` and later RAS groups.
- AMDGPU register helpers consume the `__SHIFT` and `_MASK` macros when reading or writing NBIO registers.

Observed in-tree search shows these exact symbol names are primarily generated header definitions rather than broadly referenced by C code in this checkout. Their integration is therefore mostly through version-matched NBIO support code that includes the 7.2.0 offset/mask/default headers and through common AMDGPU SOC15 register access patterns.

Likely subsystem integration points are:

- NBIO and PCIe initialization, which may program VDM, bridge, and bus/window fields.
- Debug, service, or firmware-facing paths that use fast-register apertures or trap request/response windows.
- PCIe/internal bridge configuration flows that must keep `SB_*` field layouts aligned with PCI config-space expectations.
- RAS/MCA error handling and injection paths that read global RAS status, per-group parity status, corrected counters, and severity controls.
- Low-level debug or hang-analysis flows that intentionally manipulate XBAR stalls or inspect DMA dropped-log bitmaps.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write adjacent NBIO control bits, corrupt bridge windows, misroute VDM messages, block crossbar traffic, or misreport RAS state.
- The chunk starts and ends mid-family. Any merged per-file report must join this chunk with adjacent chunks before treating `NP_DMA_DROPPED_LOG_LOWER` or `PARITY_ERROR_STATUS_UCP_GRP2` as fully documented.
- Repeated XBAR and parity status families are mechanically regular but easy to damage during regeneration. Port numbers, request/response suffixes, group numbers, and ID numbers must stay aligned.
- Trap request/response fields are protocol-sensitive. Setting `Valid`, `Write`, byte enables, masks, data size, or virtual-function fields in the wrong sequence can leave requests stuck, target the wrong address, or produce misleading responses.
- Trap comparator slots can intercept transactions. Incorrect address or command masks can trap unintended traffic or silently miss the desired traffic.
- Secondary-bus bridge fields affect enumeration and resource routing. Bad I/O, memory, prefetchable, bus-number, interrupt, or device-control fields can break PCIe hierarchy behavior.
- RAS parity controls include error injection and severity routing. Incorrect writes may inject unintended errors, suppress required reporting, over-report corrected errors, or misclassify fatal/non-fatal status.
- Corrected parity counters are only 8 bits in the covered definitions. Consumers must account for saturation or wrap behavior according to hardware rules instead of assuming unbounded counts.

## Test and Validation Signals

Useful validation is mostly build-time and hardware/integration coverage:

- Build AMDGPU paths that include `nbio_7_2_0_sh_mask.h`; this catches missing, renamed, or syntactically invalid macros.
- Compile tests around `REG_SET_FIELD` and `REG_GET_FIELD` usage for NBIO 7.2.0 should verify representative fields such as `PCIE_VDM_CNTL2__MCTPMasterID`, `STALL_CONTROL_XBARPORT0_0__StallVC0ReqEn`, `TRAP_REQUEST0__Valid`, `SB_COMMAND__BUS_MASTER_EN`, and `PARITY_CONTROL_0__ParityEnable`.
- PCIe bring-up and enumeration tests should confirm secondary-bus number, I/O, memory, prefetchable, interrupt, slot, root, and device-control fields preserve expected bridge behavior.
- Debug/trap validation should exercise trap slot programming, request construction, request completion polling, response valid/error handling, data-word counts, and byte strobe/data paths.
- RAS validation should cover parity enablement, controlled injection, global status collection, uncorrected/corrected/UCP group status reads, corrected counter reads, severity policy, MCA/SMN interrupt routing, and interrupt reporting.
- Stress or fault-injection tests should confirm DMA dropped-log bits, XBAR stall controls, and RAS status bitmaps do not produce false positives under normal traffic and do report expected state under injected or hardware-observed fault conditions.
