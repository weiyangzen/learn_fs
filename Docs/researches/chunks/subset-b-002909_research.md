# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 12322-14790

## Scope

This chunk is a generated AMD NBIO 2.3 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, dynamic allocation, locking, persistence code, or executable control flow.

The range starts in the middle of `SYSHUB_TRANS_IDLE_SOCCLK`: only the masks for VF5 through VF30 and PF are present here, while the matching shifts and early VF masks belong to the previous chunk. It then covers SYSHUB SOCCLK/SHUBCLK/LCLK controls, HST and DMA per-client reset/QoS controls, NIC400 interconnect ordering and QoS registers, the SION arbitration/credit block, SHUB reset controls, GDCL/GDCSOC/GDCSHUB RAS status/control registers, and a large `BIF_CFG_DEV0_SWDS` PCI/PCIe bridge configuration-space decode. The range ends inside `BIF_CFG_DEV0_SWDS_LANE_4_MARGINING_LANE_STATUS`, after the `LANE_4_RECEIVER_NUMBER_STATUS_MASK` definition; the remaining lane-4 status fields and later margining lanes continue in the next chunk.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIO 2.3 registers. Each generated field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or preserve a field in a 16-bit or 32-bit register value.

The companion address metadata lives in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`. Runtime AMDGPU code combines the offset header and this shift/mask header through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_NO_KIQ`, `WREG32_NO_KIQ`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening SYSHUB block names SOCCLK transaction-idle masks for SR-IOV virtual functions and the physical function. These masks let software or firmware observe which VF/PF endpoints are idle before clock, reset, virtualization, or power transitions. The chunk then defines `SYSHUB_HP_TIMER_SOCCLK`, `SYSHUB_MGCG_CTRL_SOCCLK`, `SYSHUB_CPF_DOORBELL_RS_RESET_SOCCLK`, scratch registers, client-mask controls, and hang handling bits for dropping unexpected responses on SW0/SW1 client lanes.

The HST and DMA control families repeat per switch/client lane. `HST_CLK0_SW{0,1}_CL{0,1,2}_CNTL` exposes `FLR_ON_RS_RESET_EN` and `LKRST_ON_RS_RESET_EN` bits. `DMA_CLK0_SW0_SYSHUB_QOS_CNTL` controls QoS mode and min/max QoS values, while `DMA_CLK0_SW0_CL{0,1}_CNTL` adds FLR/link-reset enables, static QoS override, and read/write weighted-round-robin weights. These fields are hardware policy inputs for reset propagation and fabric arbitration.

The SHUBCLK/LCLK SYSHUB block covers deep sleep and clock gating. `SYSHUB_DS_CTRL_SHUBCLK` has deepsleep-allow and deepsleep-enable bits; `SYSHUB_DS_CTRL2_SHUBCLK` provides the deep-sleep timer; `SYSHUB_MGCG_CTRL_SHUBCLK` mirrors the SOCCLK medium-grain clock-gating fields for enable, mode, hysteresis, and host/DMA/register/AER disables; and scratch/select registers expose full-width scratch state plus USB0/USB1 selection bits. The two `SYSHUB_BGEN_ENHANCEMENT_*_SHUBCLK` comment markers have no field macros in this chunk, indicating empty or reserved generated register descriptions.

The NIC400 families describe ARM NIC-400 interconnect behavior for several ASIB, AMIB, and IB ports. Simple `*_FN_MOD` and `*_FN_MOD_BM_ISS` registers expose read/write issuing override bits. The `NIC400_2_ASIB_{0,1}` QoS groups expose rate, flow-control, outstanding-transaction, priority, burst, rate, target-latency, KI flow-control, and QoS-range fields for AW and AR channels. These are low-level fabric tuning knobs where an incorrect mask can alter ordering, throughput, fairness, or forward progress.

The `nbio_nbif0_nbif_sion_SIONDEC` address block contains a dense SION schedule and credit table for client lanes CL0 through CL3. For each client lane, it provides full-width low/high halves for read-response, write-response, and request burst targets, matching time-slot registers, request/data/read-response/write-response pool credit allocation registers, and two SION control registers. `SION_CNTL_REG0` exposes twenty soft override bits for clock-gating control groups, and `SION_CNTL_REG1` contains livelock watchdog threshold and clock-gating-off hysteresis fields.

The `nbio_nbif0_gdc_rst_GDCRST_DEC` block defines SHUB/GDC reset surfaces. It includes PF FLR reset bits for device 0 PF0-PF3, a graphics-driver mode1 reset bit, three link reset bits, a dense PF0 VF FLR reset bitmap for VF0-VF30 plus a soft-PF reset bit, hard and soft reset enable fields for core/register/STY/NIC400/SDP/SION-AON blocks, and SDP port reset bits for A2S, NBIFSION BIF, ATHUB, ATDMA, INT, MP4, GDC, NTB, and SION-AON paths.

The `nbio_nbif0_gdc_ras_gdc_ras_regblk` block covers RAS status and controls for GDC link-to-core and core-to-link paths. Central status registers report egress-stall and error-event detection for GDCL, GDCSOC, and GDCSHUB. `GDCSOC_RAS_LEAF{0..5}_CTRL` registers enable detection, poison/parity/receiver-error handling, generated error events, egress stalls, propagation, and, for leaf2, RAS interrupts. Leaf2 also has miscellaneous control registers for slave access disable, poisoned response generation, egress-stall response enable, and timeout/fatal-error classification. Matching `GDCSOC_RAS_LEAF{0..5}_STATUS` registers report received error events, poison/parity detections, generated status, and propagated status.

The `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` block maps a PCI-to-PCIe bridge-like configuration space for `BIF_CFG_DEV0_SWDS`. It starts with standard PCI IDs, command/status, revision/class/interface, cache line, latency, header/BIST, BARs, bus numbers, I/O and memory windows, prefetchable windows, capability pointer, ROM base, interrupt line/pin, and bridge control. The field widths match PCI configuration-space conventions, including 8-bit class fields, 16-bit status/control fields, and full-width address fields.

The same BIF configuration block then exposes PM, PCIe, MSI, SSID, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, ACS, DLF, 16GT PHY, and PCIe margining capabilities. Important field groups include power-state and PME controls, device/link capability/control/status fields, max payload and max read request size, FLR capability, completion timeout and atomic operation controls, LTR and OBFF controls, target link speed and equalization state, MSI address/data fields, VC0/VC1 resource maps, AER uncorrectable/correctable status/mask/severity and header/TLP-prefix logs, ACS source-validation/translation/blocking/direct-translated/P2P controls, DLF exchange-enable/status fields, 16GT link speed/equalization/parity mismatch state, per-lane 16GT transmit presets for lanes 0-15, and margining capability/status plus margining control/status fields for lanes 0 through the start of lane 4.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing belongs to AMDGPU NBIO, virtualization, SMU, PCIe, power-management, and error-handling code that includes it:

1. Driver code selects an MMIO, SMN, PCIe, mailbox, or configuration-space register offset from `nbio_2_3_offset.h` or a local address define.
2. It reads or prepares a 16-bit or 32-bit value through SOC15, PCIE, or KIQ-safe register helpers.
3. It uses the `__SHIFT` and `_MASK` constants, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to update or decode a specific field.
4. It writes the value back, polls status bits, or records decoded state according to the hardware programming sequence.

Direct include sites in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`. `nbio_v2_3.c` demonstrates the typical pattern by combining this header with `nbio_2_3_offset.h`, reading/writing NBIO registers, and using generated field masks for doorbell ranges, framebuffer access, interrupt control, clock/power controls, strap decoding, and PCIe link behavior. `mxgpu_nv.c` uses the same NBIO 2.3 generated headers around VF/PF mailbox and virtualization flows.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO-backed hardware state whose lifetime is controlled by the GPU, firmware, PCIe link state, driver initialization, runtime power management, SR-IOV PF/VF policy, FLR/link reset, suspend/resume, and fatal error handling.

The represented state includes clock-gating and deep-sleep configuration, scratch registers, VF/PF transaction-idle visibility, reset propagation controls, QoS and WRR arbitration policy, NIC400 outstanding/rate/latency/flow-control limits, SION schedule and pool-credit tables, reset request/status bits, RAS control/status bits, PCI/PCIe configuration-space fields, capability-list linkage, MSI programming state, AER error status/mask/severity/logs, virtual-channel negotiation state, ACS/DLF policy, 16GT link/equalization/parity state, and PCIe margining command/status payloads. Some fields are configuration that persists until reset or reprogramming; others are status, sticky error state, command strobes, write-one-to-clear status, or hardware-owned training/negotiation state. The header names bit positions but does not encode access size, reset defaults, read/write side effects, required ordering, or polling rules.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 2.3 register database. This shift/mask file must stay synchronized with `nbio_2_3_offset.h` and `nbio_2_3_default.h`; offsets identify where a register lives, defaults document reset values, and this file documents how fields are packed inside the register. A correct field name with a stale mask is particularly dangerous because it compiles cleanly while programming the wrong hardware bits.

The integration surface is AMDGPU's NBIO/BIF layer, PCIe link-management code, SR-IOV support, mailbox virtualization paths, RAS/error-reporting paths, SMU power-management code, doorbell setup, reset flows, and low-power clock-gating code. The BIF configuration-space macros also align with generic PCIe concepts managed by the Linux PCI core, but they are accessed here as GPU-internal register definitions rather than as ordinary host PCI config reads.

The macro families in this chunk have strong hardware coupling. SYSHUB and SION fields affect fabric liveness and clocking; NIC400 fields affect interconnect ordering and throughput; SHUB reset fields affect PF/VF isolation and recovery; GDC RAS fields affect whether poison, parity, receiver-error, egress-stall, interrupt, and propagation events are surfaced; and BIF config fields affect PCIe enumeration, link training, error handling, MSI, virtual channels, ACS, DLF, Gen4/16GT PHY behavior, and margining.

## Risks And Edge Cases

- The assigned range has artificial boundaries. It starts mid-register in `SYSHUB_TRANS_IDLE_SOCCLK` and ends mid-register in `BIF_CFG_DEV0_SWDS_LANE_4_MARGINING_LANE_STATUS`. File-level reconciliation must join adjacent chunks before making whole-register claims about those two registers.
- These are untyped preprocessor constants. A typo in a mask value, an offset/mask mismatch, or use with the wrong register can compile successfully and only fail as a hardware behavior regression.
- Reset and FLR bitmaps are dense. Off-by-one errors in `SHUB_PF0_VF_FLR_RST` can reset the wrong VF or fail to reset the intended VF, which is a virtualization isolation and recovery risk.
- Clock-gating and deep-sleep fields can make register paths inaccessible or change wakeup latency. Incorrect `SYSHUB_MGCG_CTRL_*`, `SYSHUB_DS_CTRL*`, SION soft-overrides, or hysteresis programming can cause hangs, missed wakeups, or power regressions.
- NIC400 and SION QoS/credit fields are fabric-liveness-sensitive. Wrong outstanding limits, rate controls, target latencies, time slots, burst targets, or pool credits can cause throughput collapse, starvation, or deadlock-like symptoms.
- RAS control/status fields have side effects outside local status reporting. Incorrect masks can suppress error propagation, create unexpected egress stalls, miss poison/parity errors, or produce interrupt storms.
- PCIe configuration and capability fields have strict protocol meanings. Incorrect command/status, bridge-window, power-management, MSI, max-payload, completion-timeout, atomic, LTR, VC, ACS, AER, DLF, 16GT equalization, or margining values can break enumeration, suspend/resume, link training, hot reset, or interoperability with specific platforms.
- AER status, RAS status, PME status, parity mismatch, equalization, and margining status fields may be sticky or hardware-owned. The header cannot tell callers whether a bit is read-only, write-one-to-clear, self-clearing, or requires a specific sequence.
- Several registers are full-width scratch or address payloads. Using a full-width `0xFFFFFFFF` mask against the wrong offset can silently overwrite firmware/driver coordination state or address programming.

## Test Signals

Useful validation is mostly build, integration, and hardware oriented:

- Build AMDGPU with NBIO 2.3 consumers enabled. Missing or renamed macros should fail in `nbio_v2_3.c`, `mxgpu_nv.c`, and SMU11 files that include `nbio_2_3_sh_mask.h`.
- Exercise NBIO initialization, doorbell setup, interrupt setup, framebuffer access enable/disable, and HDP/PCIe paths on ASICs that use the NBIO 2.3 headers; register access failures, hangs, or stale memory are strong mask/offset drift signals.
- Run clock-gating and runtime power-management tests with BIF/NBIO medium-grain clock gating and light sleep toggled; watch for power regressions, wakeup failures, register read timeouts, and link instability.
- In SR-IOV configurations, validate PF/VF mailbox traffic, VF FLR/reset recovery, VF idle detection, and isolation behavior across all represented VF bits.
- Run PCIe link tests across suspend/resume, hot reset or FLR, link retraining, MSI delivery, AER reporting, ACS policy, and 16GT-capable links. Equalization failures, unexpected completion timeouts, AER storms, or bad max-payload/read-request behavior point to this family.
- Use RAS/error-injection or platform diagnostics, where available, to confirm GDC leaf/central status, error propagation, stall generation, interrupt routing, and clear behavior.
- For platforms exposing PCIe margining or 16GT diagnostics, verify margining ready/software-ready status, lane control/status payload echo, per-lane 16GT preset fields, and parity mismatch reporting.
