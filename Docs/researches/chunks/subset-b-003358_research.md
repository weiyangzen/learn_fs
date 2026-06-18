# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pcie/pcie_6_1_0_sh_mask.h lines 2356-4250

## Scope

This chunk is the tail of AMDGPU's generated PCIe 6.1.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage, locking, allocation, or direct register I/O.

The range starts in the middle of `PCIE_CNTL`, covers PCIe controller policy, receive/completion handling, common AER masking, link-controller state/status, PHY and packet status, SDP/CI controls, performance counters, function and miscellaneous straps, PRBS diagnostics, software-reset controls, CPM clock/power management, RX margining, TX tracking/status, HIP aperture registers, lane error counters, and ends at the `SMU_PCIE_FENCED2_REG` field before the file's closing `#endif`.

Although the repository path is under a `ceph-client` mirror, this file is AMD GPU PCIe register metadata. It does not implement distributed filesystem behavior.

## Purpose

`pcie_6_1_0_sh_mask.h` provides symbolic bitfield geometry for PCIe 6.1.0 hardware registers. Each generated field is represented by a pair of macros:

- `REGISTER__FIELD__SHIFT`: least-significant bit position for the field.
- `REGISTER__FIELD_MASK`: raw 32-bit mask for the field before shifting.

AMDGPU code includes this header with the matching PCIe 6.1.0 register address/default headers and uses the macro naming convention with helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`. This lets code build, preserve, and decode register values without embedding literal masks throughout executable driver paths.

## Register Families

The opening controller section finishes `PCIE_CNTL` and then defines small policy/control registers:

- `PCIE_CNTL` fields cover hot-plug delay, unsupported-request reporting suppression, malformed atomic operation handling, non-posted memory write mode, receive-side payload adjustment, RCB reorder and completion timeout behavior, ATS completion splitting, completion debug selection, LTR message handling, and posted/completion ordering.
- `PCIE_CONFIG_CNTL`, `PCIE_DEBUG_CNTL`, `PCIE_RX_CNTL5`, `PCIE_RX_CNTL4`, `PCIE_COMMON_AER_MASK`, `PCIE_CNTL2`, `PCIE_RX_CNTL2`, and `PCIE_CI_CNTL` expose dynamic clock latency, debug-port selection, sideband arbitration, atomic/ATS/TPH handling, AER masking, slave-memory low-power controls, MCA behavior, completion timeout policy, CI slave allocation, SDP connectivity, and DPC/completion-timeout conversion behavior.
- `PCIE_BUS_CNTL`, `PCIE_CFG_CNTL`, `PCIE_LC_PM_CNTL`, `PCIE_LC_PM_CNTL2`, and `PCIE_LC_STRAP_BUFF_CNTL` describe global bus/reset and link power-management controls.

The link-controller and PHY/status sections describe lane/link observation and physical-layer behavior:

- `PCIE_LC_STATE6` through `PCIE_LC_STATE11` expose per-lane or per-group link controller state fields such as MAC/PLL state, receiver-detect validity, TSX counters, electrical-idle inhibit state, and FTS counts.
- `PCIE_LC_STATUS1` and `PCIE_LC_STATUS2` expose received TLP FTS and reset/loopback/alignment status.
- `PCIE_P_CNTL` controls PHY behavior, including powerdown, symbol alignment, elastic deskew debug, error-ignore bits for CRC/length/EDB/IDL/token cases, block-lock mode, electrical-idle mode, master PLL lane selection, refclk request behavior, CXL-related ignore bits, and tracking/reset behavior.
- `PCIE_P_BUF_STATUS`, `PCIE_P_DECODER_STATUS`, `PCIE_P_MISC_STATUS`, and `PCIE_P_RCV_L0S_FTS_DET` expose overflow/underflow, decode, deskew, symbol-unlock, and L0s FTS detector status.

Receive, SDP, and packet/tracking sections include:

- `PCIE_RX_AD` policy bits for SWUS/root-complex handling of PME timeout, unlock, VDM0/VDM1, unsupported-request generation, message-prefix behavior, ECRC failure, LTAR VDM, poisoned atomics, large VDM broadcast, ACS-on-DRS, and routing checks.
- `PCIE_SDP_CTRL`, `PCIE_SDP_SWUS_SLV_ATTR_CTRL`, and `PCIE_SDP_CTRL2` fields for SDP unit IDs, disconnect/wakeup policy, LTR dropping, sideband completion headers, parity checking, MCA severity, error-event generation, virtual-wire mode, reconfiguration, RO/SNR/IDO attribute overrides, and initial SDP credits.
- `PCIE_RX_LAST_TLP0-3` and `PCIE_TX_LAST_TLP0-3` full-width fields for last observed RX/TX TLP words.
- `PCIE_TX_TRACKING_ADDR_LO`, `PCIE_TX_TRACKING_ADDR_HI`, and `PCIE_TX_TRACKING_CTRL_STATUS` for address tracking, enable/start selection, match address space, and hit status.
- `PCIE_TX_CTRL_4`, `PCIE_TX_STATUS`, `PCIE_TX_F0_ATTR_CNTL`, and `PCIE_TX_SWUS_ATTR_CNTL` for transmit idle/pending status, tag-buffer and master ordering status, debug modes, and per-traffic-class IDO/RO/SNR override behavior.

Performance and diagnostic registers are repeated by clock domain and lane:

- `PCIE_PERF_COUNT_CNTL` contains global counter enable, shadow-write, reset, and mux-select fields.
- `PCIE_PERF_CNTL_TXCLK1` through `PCIE_PERF_CNTL_TXCLK10` use a common layout with two 8-bit event selectors and `COUNTER0_FULL`/`COUNTER1_FULL` status bits.
- Each `PCIE_PERF_COUNT0_TXCLK*` and `PCIE_PERF_COUNT1_TXCLK*` register is a full 32-bit counter.
- `PCIE_PERF_CNTL_EVENT_LC_PORT_SEL` and `PCIE_PERF_CNTL_EVENT_CI_PORT_SEL` select LC and CI event ports.
- `PCIE_LANE_ERROR_COUNTERS_0` through `_3` pack four 8-bit lane error counters per register for lanes 0-15.
- `PCIE_PRBS_*` registers control PRBS clear/freerun/test-mode settings and expose lock/error/done status, bit counts, a 30-bit user pattern, and full-width error counters for lanes or channels 0-15.

Strap and configuration-capability sections describe sampled or firmware-provided PCIe capability policy:

- `PCIE_STRAP_F0` controls function-0 capability exposure for MSI, VC, DSN, AER, ACS, BAR, power management, DPA, ATS, page request, PASID, ECRC, completion-abort error handling, multicast, atomic operations, MSI multi-message capability, SR-IOV, ARI, and MSI mapping.
- `PCIE_STRAP_MISC`, `PCIE_STRAP_MISC2`, `PCIE_STRAP_PI`, and `PCIE_STRAP_I2C_BD` expose DLF, 16GT/32GT, margining, NPEM, DOE, clock power management, extended VC count, lane reversal, 64-bit master addressing, internal error, bandwidth notification, compliance modes, TPH, quicksim/test toggles, clock switch behavior, auxiliary clock behavior, and I2C debug strap fields.
- `SMN_APERTURE_ID_A/B`, `LNCNT_CONTROL`, `SMU_INT_PIN_SHARING_PORT_INDICATOR`, and `SMU_INT_PIN_SHARING_PORT_INDICATOR_TWO` provide SMN aperture identity, lane-count control, and interrupt-pin sharing indicators.

Reset and clock/power-management groups are the largest high-impact control surface in this chunk:

- `SWRST_COMMAND_STATUS` reports or triggers reconfigure, atomic reset, reset-complete/wait/PERST state, upstream/downstream link reset modes, and link reset type bits.
- `SWRST_GENERAL_CONTROL` configures reset enablement, reset period, link-up wait, register-idle forcing, idle blocking, config transfer mode, CrossFire lockdown, SDP reset ignoring, and SDP credit wait.
- `SWRST_COMMAND_0/1` command port, BIF, PCS, AXI, PCFG, LNCT, monitor, HLTR, CPM, PHY, and strap reset actions.
- `SWRST_CONTROL_0` through `_5` provide repeated reset control enable, atomic enable, and write-enable layouts for those same port/BIF/PCS/core domains.
- `SWRST_CONTROL_6`, `SWRST_EP_COMMAND_0`, and `SWRST_EP_CONTROL_0` expose link-training hold bits and endpoint reset modes for config-only, hot reset, link-down reset, and link-disable reset.
- `CPM_CONTROL`, `CPM_SPLIT_CONTROL`, `CPM_CONTROL_EXT`, `CLKREQB_PAD_CNTL`, `PCIE_PGMST_CNTL`, `PCIE_PGSLV_CNTL`, `LC_CPM_CONTROL_0`, and `LC_CPM_CONTROL_1` configure dynamic clock gating, L1/L1.1/L1.2 power gating, TXCLK/register gating, reference-clock request pad behavior, master/slave power-gating settings, LC idle hysteresis, and LC clock/power state transitions.

The tail adds newer link diagnostics and address translation/control fields:

- `PCIE_RXMARGIN_CONTROL_CAPABILITIES`, `PCIE_RXMARGIN_1_SETTINGS`, and `PCIE_RXMARGIN_2_SETTINGS` describe receiver margining capability and settings for error-count limit, sample reporting method, voltage/timing offset support, independent timing/error sampler, voltage offset, and sampling rate.
- `PCIE_LC_DEBUG_CNTL` and `PCIE_LC_DESKEW_CNTL` expose link-controller debug and deskew controls.
- `PCIE_BW_BY_UNITID` and `PCIE_MST_CTRL_1` expose performance unit ID filtering, master posted/header credit advertisement/override, SDP connectivity/mode, credit override behavior, and master idle hysteresis.
- `PCIE_HIP_REG0-8` define two HIP APT aperture base/limit pairs, enable bits, PASID mode, request attributes, request IO mode, and a HIP mask.
- `SMU_PCIE_FENCED1_REG` and `SMU_PCIE_FENCED2_REG` provide MP0-controlled fenced bits for CrossFire lockdown and overclocking enable.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace. Important macro categories are:

- Field geometry pairs consumed by AMDGPU register helpers: `*_SHIFT` and `*_MASK`.
- One-bit control/status flags for reset, power, error handling, link state, interrupt sharing, and capability exposure.
- Packed multi-bit selectors and counters, especially performance event selectors, reset periods, credit counts, SDP/CI allocation policy, electrical-idle modes, receiver-margin settings, and lane error counters.
- Full-width 32-bit fields for last TLP words, PRBS bit/error counters, tracking addresses, HIP aperture low words, and performance counters.

All semantics are hardware-owned. The header gives bit locations, not allowed values, sequencing rules, reset values, or ownership policy.

## Control Flow and Data Flow

This header has no local control flow. Runtime flow is indirect through consumers:

1. The driver selects a PCIe 6.1.0 register address from the matching generated offset/header file.
2. It reads a 32-bit register value, builds one with `REG_SET_FIELD()`, or extracts fields with `REG_GET_FIELD()`.
3. The shift/mask macros in this chunk isolate the intended field.
4. Hardware interprets the resulting value in PCIe controller, LC, PHY, CI/SDP, reset, CPM, TX/RX, HIP, PRBS, or performance-counter logic.

Several groups imply sequencing that must be implemented outside this file. Reset commands require enable/write-enable policy and polling of status bits. Performance counters require event selection, global enable/reset, overflow/full handling, and reads of the paired count registers. PRBS testing requires clear, configuration, freerun/test-mode, lock checking, bit-count completion, and error-counter reads. Margining and link diagnostics require coordination with PCIe link state and host/platform policy.

## State and Persistence Behavior

The header itself stores no software state and persists nothing. The represented state lives in PCIe 6.1.0 hardware registers:

- Controller policy state: completion timeout handling, AER masking, malformed request behavior, LTR/ATS/atomic handling, ordering overrides, and DPC conversion behavior.
- Link/PHY state: LC state/status, deskew status, symbol lock/unlock status, overflow/underflow status, electrical-idle behavior, PLL/refclk request controls, lane-count control, and lane error counters.
- Capability/strap state: function-0 and miscellaneous capability exposure, compliance modes, SR-IOV/ARI/PASID/ATS/AER/ACS/MSI/MSI-X-like capability knobs, DOE/TPH/margining/link-speed capability bits, and debug/I2C strap behavior.
- Diagnostic state: last observed RX/TX TLP words, PRBS status/counters, performance counter selections/counts, TX tracking hit state, and RX margining settings.
- Reset and power state: software-reset commands, reset-complete/wait/PERST/link-reset state, per-domain reset enables, training holds, endpoint reset modes, dynamic clock gating, power gating, and CLKREQB pad behavior.
- Aperture and translation state: HIP APT base/limit registers, enable bits, PASID mode, request attribute mode, request IO mode, and HIP masks.
- SMU fenced state: MP0-controlled lockdown/overclocking gates.

Persistence follows the PCIe IP block's reset, power, firmware, and strap-sampling rules. Some fields are likely sticky status or clear-on-write by hardware convention, but this header does not encode access type. Writes to reset, power, strap, or fenced fields can immediately affect live hardware behavior.

## Dependencies and Integration Points

This chunk depends on the AMDGPU generated register-header ecosystem:

- The matching PCIe 6.1.0 address/offset header supplies concrete register offsets for the names used here.
- AMDGPU helper macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()` depend on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- SOC/IP-version selection must include this header only for ASICs whose PCIe register layout matches version 6.1.0.
- Register defaults and access permissions, if needed, must come from companion generated headers or hardware documentation; they are not present here.

Practical integration points include AMDGPU PCIe/BIF initialization, link training and recovery, ASPM/L1/L1.1/L1.2 power-management setup, reset and FLR/link-reset recovery, RAS/AER policy, SR-IOV and capability exposure, host/SMU coordination, performance diagnostics, register dumps, margining diagnostics, PRBS/lane validation, and low-level bring-up/debug tooling.

## Risks and Edge Cases

- The chunk begins mid-register in `PCIE_CNTL`; whole-register interpretation must merge with the previous chunk.
- These macros are untyped constants. Incorrect masks, shifts, or stale generated data can compile successfully but program the wrong hardware bits.
- Reset fields are high risk. A bad read/modify/write can reset ports, BIF domains, PCS lanes, AXI interfaces, PHY, CPM, or endpoint link state unexpectedly.
- Power-management and clock-gating fields can cause intermittent link, suspend/resume, or performance failures if programmed without respecting hardware sequencing.
- Strap fields may be sampled or firmware-owned rather than normal writable state. Treating capability straps as runtime toggles can desynchronize PCI config-space exposure from hardware behavior.
- AER, DPC, completion timeout, poisoned atomic, ECRC, ACS, and unsupported-request policy bits affect error reporting and containment. Incorrect settings can hide real faults or escalate recoverable errors.
- PRBS, margining, and debug/status registers often require test-mode entry and specific clearing/polling order. The shift/mask header alone does not document that order.
- Full-width last-TLP and tracking registers may expose transient diagnostic snapshots; tests should avoid assuming they are stable without freezing or polling rules.
- HIP aperture base/limit fields span high/low registers. Partial writes or inconsistent base/limit programming can expose wrong address windows.
- SMU fenced bits imply firmware/MP0 ownership. Driver writes without firmware coordination could conflict with platform security, overclocking, or board policy.

## Test and Validation Signals

Useful validation is mostly generated-header and hardware integration testing:

- Build AMDGPU configurations that include PCIe 6.1.0 support; referenced field names must match helper call sites.
- Compare every shift/mask pair in this range against the authoritative PCIe 6.1.0 register database, including field width checks for packed counters/selectors and full-width fields.
- Decode PCIe 6.1.0 register dumps from matching hardware and verify controller policy, LC/PHY state, straps, CPM, reset, performance counter, PRBS, RX margining, TX tracking, HIP, and lane error fields land at expected bits.
- Exercise link training, hot reset, link-down reset, link-disable reset, FLR-like recovery, suspend/resume, and power-gating flows while checking reset status, LC state, CPM controls, and restored register state.
- Run PCIe error injection or platform AER/DPC tests where available to confirm unsupported request, ECRC, ACS, completion-timeout, poisoned atomic, and AER mask behavior.
- Run PRBS and lane diagnostics on hardware or simulation: clear counters, enable test mode, verify lock/done status, bit counts, per-lane error counters, and lane error counter packing.
- Exercise performance counters by selecting known LC/CI/TXCLK events, enabling global count, observing counter increments, and checking full flags.
- Validate receiver margining and link-speed capability fields against PCIe config-space capability exposure and margining tools.
- Cross-check function and miscellaneous strap fields against enumerated PCIe capabilities such as AER, ACS, ATS, PASID, page request, SR-IOV, ARI, DOE, TPH, DLF, and 16GT/32GT support.

## Chunk Boundary Notes

The previous chunk owns the beginning of `PCIE_CNTL`. This chunk owns the remainder of the header through `SMU_PCIE_FENCED2_REG` and the closing guard. The final per-file reconciliation should merge the `PCIE_CNTL` boundary before making complete whole-file statements about PCIe 6.1.0 control masks.
