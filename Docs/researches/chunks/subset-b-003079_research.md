# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 26841-29278

## Scope And Purpose

This chunk is a generated NBIO 7.0 register field-mask slice. It contains no executable code; its public surface is a large set of C preprocessor constants that describe bit positions and already-shifted bit masks for hardware registers. Consumers pair these definitions with the matching NBIO 7.0 register-address header and AMDGPU MMIO/SMN register access helpers to encode writes, decode reads, and preserve fields during read-modify-write sequences.

The range starts in the tail of `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS`, then covers PCIe advanced error reporting, link/lane capability, access control services, multicast, L1 PM substates, downstream port containment, root-port PIO logging, and Equalization Status Method fields. It then moves through DBGU indexed debug ports, GDC doorbell and miscellaneous controls, SYSHUB clock/power/QoS controls, NIC400 fabric issue-override fields, SION arbitration/credit controls, SHUB reset controls, GDC RAS leaf controls, and the first IOMMU L2 MMIO base-address registers.

This chunk contains 2,135 `#define` entries: 1,061 `__SHIFT` macros and 1,074 `_MASK` macros. The small mismatch is expected at chunk boundaries and because the first visible lines continue masks for a register whose shift definitions appear before this chunk.

## Register Families Covered

The PCIe block covers multiple capability and error-management areas for `BIFPLR6_0`. AER-related definitions include uncorrectable error mask and severity bits for data-link, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable, multicast-blocked, atomic-op egress-blocked, TLP-prefix-blocked, and poisoned-TLP egress-blocked errors. Correctable error status/mask fields cover receiver error, bad TLP/DLLP, replay rollover/timeout, advisory nonfatal, internal correctable, and header-log overflow bits. Header, prefix, source-ID, root-error-command, and root-error-status registers provide error reporting and diagnostic log metadata.

The PCIe extended capability definitions include secondary enhanced capability, link control 3, lane error status, per-lane equalization controls for lanes 0 through 15, ACS capability/control, multicast capability/control/address/receive/block/overlay BAR fields, L1 PM substate capability/control/timing fields, DPC capability/control/status/source-ID fields, and root-port PIO status/mask/severity/system-error/exception plus header/prefix log windows. The ESM area describes capability headers, minimum electrical-idle timing, Gen3/Gen4 data-rate controls, an enable bit, and dense capability bitmaps for rates from 8.0G through the high 20G ranges across `ESM_CAP_1` through `ESM_CAP_7`.

The `nbio_dbgu0_dbgudec` address block defines four indexed debug ports. Each port has an address register with `Index`, reserved bits, and `ReadEnable`, plus low/high 32-bit data windows. These are low-level debug access windows rather than normal driver state variables.

The `nbio_nbif0_gdc_GDCDEC` block describes GDC/NGDC and doorbell-related fields. It includes SDP disconnect hysteresis, dropping non-PF MMREG requests, reserved 32-bit windows, SDMA0/SDMA1/IH/MMSCH doorbell range offset and size fields, ATDMA weighted round-robin controls, a doorbell fence enable, 64-bit doorbell support disable bits for SDMA and CP, AXI host completion endpoint disable, and a GDC power-gating reset-select bit.

The `nbio_nbif0_syshub_mmreg_direct_syshubdirect` block is the largest non-PCIe block in this chunk. It defines SOCCLK and SHUBCLK deep-sleep controls for HST and DMA client lanes, deep-sleep timers, BGEN bypass/immediate enable bits, DMA QoS max/min/mode fields, per-clock/per-client control registers with FLR-on-reset, link-reset-on-reset, static QoS override, read WRR weight, and write WRR weight fields. It also exposes SYSHUB clock-gating control, per-VF/PF transaction-idle status bits, high-precision timer and scratch windows, MGCG controls, CL masking for MP1/MP1DRAM, and NIC400 `read_iss_override` / `write_iss_override` fields for several ASIB/AMIB interfaces.

The `nbio_nbif0_nbif_sion_SIONDEC` block is dominated by repeated SION class-of-service controls. For CL0 through CL3, it defines read-response, write-response, and request burst-target/time-slot registers and request/data/read-response/write-response pool credit allocations. Each of these simple windows exposes a full-width `DATA` field. `SION_CNTL_REG0` adds many clock soft-override bits, while `SION_CNTL_REG1` defines livelock watchdog threshold and clock-gating-off hysteresis fields.

The `nbio_nbif0_gdc_rst_GDCRST_DEC` block covers reset controls. It includes PF FLR reset bits for device 0 and device 1 PF0 through PF7, a graphics driver VPU reset bit, link P0/P1 reset bits, PF0 VF0 through VF15 FLR reset bits plus a PF0 soft-PF FLR reset bit, hard and soft reset enable bits for COR/REG/STY/NIC400/SDP port reset domains, an SDP port reset bit, and RSMU soft-reset atomic/cycle fields.

The `nbio_nbif0_gdc_ras_gdc_ras_regblk` block defines six identical-looking RAS leaf controls. Each leaf has poison and parity detection enable, error-event enable, stall enable, local error reporting enable, event/link-disconnect receive status, poison/parity detected status, error-event sent, and egress-stalled bits.

The chunk ends at the beginning of `nbio_iohub_iommu_l2mmio_l2mmiocfg`. Visible IOMMU L2 MMIO registers define low/high portions and length fields for the device table base, command buffer base, and event log base, with reserved masks included in the layout. The final `IOMMU_L2MMIO0_IOMMU_MMIO_EVENT_BASE_1` register is cut off by the chunk boundary; its remaining masks continue in a later chunk.

## APIs, Types, And Functions

There are no functions, structs, enums, inline helpers, or runtime APIs in this chunk. The important interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` is the zero-based bit position of a field.
- `<REGISTER>__<FIELD>_MASK` is the field mask in register position.
- Full-width data/log registers use masks such as `0xFFFFFFFFL`; shorter PCIe capability registers often use 16-bit masks, while NBIF/SYSHUB/GDC/SION blocks generally use 32-bit masks.

Normal consumers are AMDGPU register manipulation paths that read a register, clear the field mask, OR in `(value << SHIFT) & MASK`, then write it back. Diagnostic paths use the same pairs to decode status, error, credit, QoS, reset, RAS, and IOMMU base-address fields.

## Control Flow

The header has no runtime control flow. All behavior is deferred to whichever driver, firmware interface, debug tool, or generated access helper includes these macros.

The field names imply several sequencing-sensitive hardware protocols. PCIe AER, DPC, root-port PIO, and ESM fields require capability discovery, status collection, mask/severity programming, and bounded recovery or logging sequences. SYSHUB, SION, and GDC fields influence clock gating, QoS, arbitration credits, doorbell routing, and fabric resets, so writes must follow the hardware's ordering rules. Reset and FLR fields are especially stateful: asserting PF/VF, link, hard, or soft resets without waiting for completion or preserving unrelated bits can interrupt live functions. IOMMU base registers must be programmed coherently across low/high halves and length fields before enabling translation or command/event handling.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware state that persists in NBIO registers until reset, power transition, firmware action, or driver write.

State categories visible in this chunk include PCIe error status, masks, severities, root error source IDs, header and prefix logs, lane equalization settings, ACS and multicast controls, L1 substate controls, DPC trigger/status state, ESM rate capabilities/enables, DBGU indexed debug data, GDC doorbell ranges and fences, SYSHUB deep-sleep/clock-gating/QoS/idle state, NIC400 issue-override bits, SION arbitration and credit allocation state, SHUB reset request state, RAS detection/reporting/stall state, and IOMMU device-table/command/event base-address state.

Reserved fields are explicitly defined in several registers. They are part of the documented bit layout, but driver writes should not treat them as feature state. Read-modify-write paths should preserve reserved bits unless the hardware specification requires a fixed write value.

## Dependencies And Integration Points

This chunk depends on the rest of the generated NBIO 7.0 register package. The matching offset header supplies addresses for the registers named here, the default header supplies reset/default values where generated, and adjacent chunks of `nbio_7_0_sh_mask.h` define the preceding and following fields cut by this line range.

Integration is hardware-facing and primarily through AMDGPU NBIO, PCIe, SR-IOV, reset, RAS, IOMMU, doorbell, clock/power-management, and low-level diagnostic code. The BIFPLR6 PCIe fields align with PCIe capability and error-handling flows. GDC and SHUB reset fields align with FLR, link reset, and NBIF reset handling. Doorbell ranges and fence controls affect SDMA, IH, CP, and MMSCH doorbell routing. SYSHUB/SION fields affect fabric QoS, clock gating, transaction-idle checks, and credit arbitration. IOMMU L2 MMIO base fields are integration points for GPU-side IOMMU table, command, and event-log setup.

## Risks And Edge Cases

Generated shift/mask headers are passive data, but mistakes are high-impact because consumers write directly to hardware. A wrong mask or shift can alter PCIe error policy, disable doorbell support, change QoS arbitration, reset the wrong PF/VF, corrupt RAS reporting, or program an invalid IOMMU base.

Many fields represent write-one, sticky status, or clear-on-write hardware state in the underlying registers, but this header does not encode access semantics. Callers must know whether a field is read-only, write-one-to-clear, sticky, reset-sensitive, or preserved across power states.

The PCIe section mixes 16-bit capability-style registers, 32-bit status/log registers, and dense per-lane/per-rate arrays. Generic code should not infer register width solely from the namespace. The chunk boundary also begins and ends mid-register-family: uncorrectable error status starts before line 26841, and `IOMMU_MMIO_EVENT_BASE_1` continues after line 29278.

Reset and FLR fields are risky in virtualized environments. `SHUB_PF_FLR_RST` and `SHUB_PF0_VF_FLR_RST` expose per-function reset controls; writing the wrong bit can disrupt another PF/VF or leave functions stuck if polling and deassert sequencing are wrong.

IOMMU base fields split addresses across low/high registers with reserved bits and length fields. Code must enforce alignment, program both halves consistently, avoid tearing while the unit is active, and preserve reserved bits.

QoS, SION credits, SYSHUB clock gating, MGCG, and deep-sleep controls can cause performance regressions or hangs if programmed without workload and power-state awareness. RAS poison/parity stall settings can intentionally stop egress traffic; enabling stall paths without recovery handling can wedge the affected leaf.

## Test Signals

Primary validation for this header is successful compilation of AMDGPU code that includes the generated NBIO 7.0 register package. Because this chunk has no executable logic, behavioral confidence comes from static generated-header checks plus hardware, simulator, or register-trace validation.

Useful static checks include verifying that each field normally has both a shift and mask, that masks align with shifts and widths, that duplicate lane/rate/client arrays are monotonic, that reserved masks do not overlap active fields within a register, and that chunk-boundary exceptions are accounted for during merge.

Useful runtime or integration signals include PCIe AER/DPC/root-port PIO tests that inject correctable and uncorrectable errors and validate status, mask, severity, source-ID, header-log, prefix-log, and DPC status decoding; link training and compliance traces that validate lane equalization and ESM rate fields; SR-IOV reset tests that exercise PF/VF FLR and link reset bits with bounded polling; doorbell tests that verify SDMA/IH/CP/MMSCH routing and 64-bit support flags; clock/power tests that observe SYSHUB transaction-idle, deep-sleep, MGCG, and scratch/timer behavior; QoS and SION stress tests that check arbitration credit programming and livelock watchdog behavior; RAS tests that inject poison/parity events and observe leaf event, stall, and reporting bits; and IOMMU setup tests that validate device table, command buffer, and event log base programming against real translated traffic and event generation.

Merged per-file research should connect this chunk with adjacent `nbio_7_0_sh_mask.h` chunks for the complete generated field map and with the matching NBIO 7.0 offset/default headers for addresses, reset values, and access widths.
