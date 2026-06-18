# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 75614-78264

## Scope

This chunk is a macro-only section of the AMD NBIO 7.0 register mask header. It defines `__SHIFT` and `__MASK` constants for PCIe shadow bridge configuration, IOHC miscellaneous/fast-register control, trap/debug capture, bridge decode/QoS policy, and the beginning of IOHC SION scheduling/credit tables. There are no C functions, structs, enums, storage objects, or executable control-flow constructs in this slice; its API surface is the exported preprocessor symbol set consumed by lower-level AMDGPU register access code.

## Purpose

The constants in this range describe bitfield layouts for 32-bit NBIO/IOHC registers. Driver code can combine these masks with ASIC register addresses from companion `*_offset.h` headers and reset values from `*_default.h` headers to compose writes, decode reads, and preserve reserved bits. The chunk covers:

- `NB_PCIE0SHADOW0_*` through `NB_PCIE0SHADOW6_*` PCIe type-1 bridge shadow fields.
- Address blocks for `nbio_iohub_nb_NBIF1shadow0_pcieshadow_cfgdecp` and `nbio_iohub_nb_NBIF1shadow1_pcieshadow_cfgdecp`, followed by the fastreg and misc IOHC decode areas.
- IOHC clock gating, performance counters, programmable PCI bridge device/function remaps, interrupt/NMI/SMI/SCI controls, DMA dropped logs, VDM, stall controls, MMIO aperture base/lock controls, power gating, SDP/parity controls, scratch/status, trap request/response state, and `TRAP0` through `TRAP15` comparator programming fields.
- Southbridge-style `SB_*` bridge shadow masks, IOHC decode override masks, QoS priority masks, USB QoS masks, and SION client arbitration/credit fields through `IOHC_SION_S0_Client4_WrRsp_TimeSlot_Lower`.

## Important Macro Families

### PCIe Shadow Bridge Masks

Each `NB_PCIE0SHADOWn_*` group for shadows 0-6 repeats the same bridge register schema:

- `COMMAND`: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`.
- `SUB_BUS_NUMBER_LATENCY`: secondary and subordinate bus number fields.
- `IO_BASE_LIMIT`, `IO_BASE_LIMIT_HI`: split I/O window base/limit fields.
- `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`: memory and prefetchable memory bridge windows.
- `IRQ_BRIDGE_CNTL`, `EXT_BRIDGE_CNTL`, `PMI_STATUS_CNTL`, `SLOT_CAP`, `ROOT_CNTL`, `DEVICE_CNTL2`: bridge legacy decode, port 0x80 routing, power state, slot power, CRS visibility, and ARI forwarding fields.

These macros are integration points for PCIe topology setup, GPU bridge enumeration, reset restore paths, and any platform-specific bridge resource programming. The fields mirror PCI/PCIe configuration space semantics, but live in NBIO shadow decode space.

### IOHC Fastreg and Miscellaneous Controls

The fastreg/misc section defines masks for IOHC mode and policy registers:

- `IOHC_REFCLK_MODE`, `IOHC_PCIE_CRS_Count`, `IOHC_P2P_CNTL`, `IOHC_AER_CNTL`, and `SB_LOCATION` expose reference clock, CRS retry timing, peer-to-peer behavior, AER behavior, and southbridge location metadata.
- `IOHC_GLUE_CG_LCLK_CTRL_0/1/2` soft override fields cover many local clock lanes. These are hardware power/clock controls; incorrect writes can prevent expected clock gating or force clocks on.
- `IOHC_PERF_CNTL` selects four performance events, with `IOHC_PERF_COUNT0..3` and `*_UPPER` exposing 56-bit-style counter values split across lower 32-bit and upper 24-bit fields.
- `NB_PROG_DEVICE_REMAP_PBr0..PBr8` maps PCI bridge device/function identifiers.
- `SW_NMI_CNTL`, `SW_SMI_CNTL`, `SW_SCI_CNTL`, `SW_GIC_SPI_CNTL`, `IOHC_INTERRUPT_EOI`, `SW_SYNCFLOOD_CNTL`, `IOHC_PIN_CNTL`, and `IOHC_INTR_CNTL` define software interrupt, end-of-interrupt, sync flood, pin mode, and destination controls.
- `IOHC_FEATURE_CNTL` and `IOHC_FEATURE_CNTL2` expose P2P mode, architecture/ARI/dGPU feature bits and status bits such as NMI, SERR, CRS, and posted/non-posted DMA dropped status.
- `NB_TOP_OF_DRAM3` and `NB_DRAM3_BASE` describe high DRAM decode ranges.
- `PSP_BASE_ADDR_*`, `SMU_BASE_ADDR_*`, `IOAPIC_BASE_ADDR_*`, `FASTREG_BASE_ADDR_*`, `FASTREGCNTL_BASE_ADDR_*`, and `SMMU_BASE_ADDR_*` encode MMIO aperture enables, lock bits, and base address fields for security, firmware, interrupt, fast register, and SMMU blocks.
- `IOHC_PGMST_CNTL`, `IOHC_SDP_PORT_CONTROL`, `IOHC_SDP_PARITY_CONTROL`, and `IOHC_PGSLV_CNTL` define power-gating/idleness and SDP parity behavior.
- `SCRATCH_4`, `SCRATCH_5`, `SMU_BLOCK_CPU`, and `SMU_BLOCK_CPU_STATUS` provide firmware/driver scratch and SMU CPU-block handshake/status fields.

### CAM, DMA Dropped Logs, VDM, and Stall Controls

`CAM_CONTROL` plus `CAM_TARGET_*` fields configure a content/address match mechanism with enable, operation, access type, data-match, VC, and cross-trigger controls. The DMA dropped log families (`P_DMA_DROPPED_LOG_LOWER/UPPER` and `NP_DMA_DROPPED_LOG_LOWER/UPPER`) expose one mask bit per logged source/slot across lower and upper words. `PCIE_VDM_NODE0_CTRL4`, `PCIE_VDM_CNTL2`, and `PCIE_VDM_CNTL3` provide VDM routing and SMU/MCTP/APMTP master controls. `STALL_CONTROL_XBARPORT*_0/1` fields allow request/response stalling per virtual channel for crossbar ports, which is useful for debug but risky for normal traffic.

### Trap Request, Response, and Comparator Programming

The trap infrastructure has two layers:

- Global trap request/response capture: `TRAP_STATUS`, `TRAP_REQUEST0..5`, `TRAP_REQUEST_DATASTRB0/1`, `TRAP_REQUEST_DATA0..15`, `TRAP_RESPONSE_CONTROL`, `TRAP_RESPONSE0`, and `TRAP_RESPONSE_DATA0..15` describe a captured request address, command, attributes, length, VC, security level, data/parity, response status, and response payload.
- Sixteen trap comparators: `TRAP0_*` through `TRAP15_*` repeat the same pattern of `CONTROL0`, `ADDRESS_LO`, `ADDRESS_HI`, `COMMAND`, `ADDRESS_LO_MASK`, `ADDRESS_HI_MASK`, and `COMMAND_MASK`. Each control register has enable, SMU interrupt, and cross-trigger fields. Address low fields start at bit 2, matching dword alignment.

This block is a debug and error-observation interface. Driver consumers should program trap enables and masks carefully because overly broad comparators can generate interrupt/debug traffic or stall diagnosis paths.

### Decode, SB Bridge, QoS, and SION Scheduling

The decode override registers (`IOHC_REQDECODE_OVERRIDE`, `IOHC_RSPDECODE_OVERRIDE`, and `IOHC_RSPPASSPW_OVERRIDE`) allocate four bits per client 0-7. `IOHC_USERBIT_BYPASS`, `IOHC_SMN_MASTER_CNTL`, and `IOHC_SMN_MASTER_STATUS` control user-bit bypass and SMN error/poison status mapping.

`SB_*` repeats the PCIe bridge schema for southbridge shadow configuration: command bits, bus numbers, I/O and memory windows, IRQ/VGA/ISA decode, port 0x80, power state, slot power, CRS, and ARI forwarding.

`IOHC_QOS_CONTROL` assigns four-bit QoS priority fields to VC0-VC7, while `USB_QoS_CNTL` carries unit IDs, priority, and enable fields for two USB units.

The SION block begins a large table of 32-bit full-word masks for per-client arbitration and credit programming. For clients 0-3, this chunk includes S0 and S1 request, read-response, and write-response `BurstTarget` and `TimeSlot` lower/upper words plus request/data/read-response/write-response pool credit allocation lower/upper words. Client 4 begins in this chunk and continues into the next chunk, ending here at `IOHC_SION_S0_Client4_WrRsp_TimeSlot_Lower`.

## Control Flow and State Behavior

There is no runtime control flow in this header. State changes happen only when consumers use these masks to read or write hardware registers. The state represented here is persistent hardware-visible state until reset, power-gated domain loss, firmware reprogramming, or explicit driver writes. Notable state categories include:

- PCI bridge resource windows and enable bits that affect config-space decode and DMA reachability.
- Interrupt, NMI/SMI/SCI, sync flood, and EOI state that can affect platform signaling.
- MMIO base/enable/lock fields for PSP, SMU, IOAPIC, fastreg, fastreg control, and SMMU apertures. Lock fields are especially sensitive because writes may become irreversible until reset.
- Debug/trap/CAM/stall state that can capture, reroute, or block traffic.
- QoS and SION scheduling/credit state that changes ordering, bandwidth share, and backpressure behavior for IOHC clients.

## Dependencies and Integration Points

This file depends on the C preprocessor only. It is intended to be included by AMDGPU/NBIO code alongside related generated headers:

- `nbio_7_0_offset.h` for register addresses.
- `nbio_7_0_default.h` for reset/default values.
- AMDGPU register helpers that apply `MASK`, `SHIFT`, `REG_SET_FIELD`, or equivalent bitfield utilities.

The constants integrate with Linux DRM AMDGPU PCIe/NBIO initialization, suspend/resume restore, reset handling, debugfs or diagnostics that expose performance/trap/error state, firmware-mediated SMU/PSP control paths, and platform-specific bridge or MMIO aperture setup.

## Risks

- Because this is generated hardware documentation as C macros, a single wrong mask or shift silently corrupts unrelated bits in hardware register writes.
- Many fields share repeated schemas. Copy/paste or generation mistakes are hard to detect by inspection, especially across `NB_PCIE0SHADOW0..6`, `TRAP0..15`, dropped-log bit arrays, and SION client tables.
- Lock bits in MMIO base registers can make bad base/enable programming persist until reset.
- Trap, CAM, and stall controls can perturb live traffic if debug code enables broad matches or stalls production virtual channels.
- QoS and SION credit fields are full-width table entries; invalid scheduling or credit values can create starvation, latency spikes, or deadlock-like backpressure.
- This chunk ends in the middle of the client 4 SION block, so downstream reconciliation must merge with the next chunk before treating the SION table as complete.

## Test and Validation Signals

- Build-time validation: compile AMDGPU code that includes `nbio_7_0_sh_mask.h`; undefined or duplicate macro failures would catch gross header breakage.
- Static consistency checks: verify every `__MASK` aligns with its `__SHIFT`, especially repeated one-bit fields, address low fields shifted by 2, upper 24-bit performance counters, and four-bit-per-client decode/QoS fields.
- Cross-header checks: compare symbol stems against `nbio_7_0_offset.h` register names and `nbio_7_0_default.h` defaults for the same NBIO generation.
- Runtime smoke signals: successful PCIe bridge enumeration, preserved BAR/resource windows after suspend/resume, no unexpected NMI/SMI/SCI or AER/CRS status changes, and stable PSP/SMU/SMMU/IOAPIC MMIO access.
- Debug validation: trap/CAM programming should capture expected requests only; performance counters should increment for selected events; SION/QoS changes should be tested with traffic stress and checked for hangs, dropped DMA status bits, or performance regressions.
