# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pcie/pcie_6_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003357`: lines 1-2355, `Docs/researches/chunks/subset-b-003357_research.md`
- `subset-b-003358`: lines 2356-4250, `Docs/researches/chunks/subset-b-003358_research.md`

## Chunk Research

### subset-b-003357: lines 1-2355

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pcie/pcie_6_1_0_sh_mask.h lines 1-2355

## Scope

This chunk covers the opening 2,355 lines of the generated AMD PCIe 6.1.0 shift/mask header. The range starts with the license and include guard, then defines register-field `__SHIFT` and `_MASK` macros for these address blocks:

- `pcie_container_pcs0_pcie_lcu_pcie_pcs_prime_pcie_master_x1_xx16_pcs_prime_dir`: DXIO hardware identity/linkage and MAC capability fields.
- `pcie_container_pcie0_pswuscfg0_cfgdecp`: PCI/PCIe configuration-space command/status fields plus per-lane equalization, LTR, L1 PM substates, and margining capability-list fields.
- `pcie_container_pcie0_pswusp0_pciedir_p`: a large port/link-control block covering PCIEP port control, RX/TX path control, LTSSM/link training, link width/speed/equalization, low-power substates, error injection, ECC, save/restore, clock gating, replay/credits, and flow-control fields.
- The beginning of `pcie_container_pcie0_pciedir`: reserved/scratch/NAK counters and the first few `PCIE_CNTL` shifts. The chunk ends in the middle of `PCIE_CNTL`; its remaining masks and later registers are outside this work item.

The file is a generated C preprocessor register-field map. It defines no functions, structs, storage, locks, or executable code. Runtime behavior exists in AMDGPU consumers that combine these masks with companion register-offset headers and AMDGPU register access helpers.

## Purpose

This header records the bit-level ABI for AMD PCIe 6.1.0 hardware. Each field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`: the field's low bit.
- `<REGISTER>__<FIELD>_MASK`: the field's packed mask in the raw register value.

Driver code can use these constants with helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` to safely extract, compose, and update MMIO/config-space values without hard-coding bit positions. The header is particularly important because many fields control PCIe training, equalization, power management, flow control, error reporting, and error injection, where adjacent bits often have unrelated effects.

## Important Macro Families

### DXIO and MAC Capability Fields

The first address block exposes low-level identity and discovery fields:

- `DXIO_HWDID` splits hardware revision, minor version, and major version.
- `DXIO_LINKAGE_LANEGRP` exposes lane-group indirect-access support, aperture size, index offset, and presence bits.
- `DXIO_LINKAGE_KPDMX` exposes overlay, base offset, and presence fields. `DXIO_LINKAGE_KPMX`, `DXIO_LINKAGE_KPFIFO`, and `DXIO_LINKAGE_KPNP` are named as register comments but define no fields in this chunk.
- `MAC_CAPABILITIES1` reports number of lanes and engines.
- `MAC_CAPABILITIES2` contains a one-bit `reserved` field.

These definitions are discovery and decode aids for code that needs to identify the PCIe/DXIO block revision and lane topology before configuring link behavior.

### PCI Configuration and Extended Capability Fields

The `pswuscfg0_cfgdecp` block begins with standard PCI configuration concepts:

- `COMMAND` covers I/O, memory, bus-master, special-cycle, memory-write-invalidate, parity response, SERR, fast back-to-back, and interrupt-disable controls.
- `STATUS` covers immediate readiness, interrupt status, capability-list presence, parity/master abort/target abort/system error status, and DEVSEL timing.
- `LATENCY` and `HEADER` define latency timer and header/device type fields.

The same block then defines PCIe capability-related fields:

- `PCIE_LANE_ERROR_STATUS` exposes a 16-bit lane-error bitmap.
- `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` are repeated lane controls for downstream/upstream TX presets and RX preset hints. Every lane has the same four fields and masks.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_L1_PM_SUB_CAP_LIST` expose extended capability ID, version, and next-pointer fields.
- `PCIE_LTR_CAP` carries max snoop and no-snoop latency values and scales.
- `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2` describe and control PCI-PM/ASPM L1.1/L1.2 support, link activation, common-mode restore time, LTR L1.2 threshold, and T_POWER_ON values.
- `PCIE_MARGINING_ENH_CAP_LIST` provides capability-list fields for PCIe margining support.

These macros are integration points for PCI enumeration, capability publication, ASPM/L1SS policy, latency tolerance reporting, and per-lane equalization programming.

### PCIEP Port, RX, Error, and Injection Controls

The `pcie0_pswusp0_pciedir_p` block starts with port-local registers:

- `PCIEP_RESERVED` and `PCIEP_SCRATCH` are full-width fields.
- `PCIEP_PORT_CNTL` controls slave-port request enable, snoop override, hotplug/PME/power-fault handling, completion payload sizing, poisoned unsupported-request behavior, and completion allocation limits.
- `PCIE_TX_REQUESTER_ID` maps requester function/device/bus fields used for outgoing requests.
- `PCIE_P_PORT_LANE_STATUS` reports lane reversal and physical link width.
- `PCIE_ERR_CNTL` contains broad error-reporting controls, ECRC/LCRC/poison generation controls, AER header-log timing, private AER masks, slave-buffer halt status/reset, advisory nonfatal handling, poisoned TLP handling, parity masking, replay-error masking, and extended sync/header logging controls.
- `PCIE_RX_CNTL` controls RX completion timeout behavior, replay behavior, ECRC checking, atomic-op and ID-order handling, malformed TLP and LTR behavior, flush behavior, message filtering, FLR waiting, and reset-disable policy.
- `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_VENDOR_SPECIFIC`, `PCIE_RX_CNTL3`, and RX credit allocation registers expose receiver sequence, vendor DLLP, additional timeout/error masks, and allocated posted/non-posted/completion credits.
- `PCIEP_ERROR_INJECT_PHYSICAL` and `PCIEP_ERROR_INJECT_TRANSACTION` provide test hooks for physical-layer and transaction-layer error injection, including bad sync/header/LCRC/ECRC/sequence paths, replay timer manipulation, NAK injection, DLLP/TLP error selectors, and send-trigger bits.
- `PCIEP_NAK_COUNTER` reports generated and received NAK counts.

This is the main interface for low-level PCIe reliability, protocol validation, debug, and port policy code. Error-injection fields are especially sensitive because they intentionally create malformed protocol behavior.

### Link Controller, LTSSM, Training, Width, and Speed

Most of the chunk defines `PCIE_LC_*` link-controller fields:

- `PCIE_LC_CNTL`, `PCIE_LC_CNTL2` through `PCIE_LC_CNTL13`, and `PCIE_LC_TRAINING_CNTL` expose LTSSM control, receiver-detect selection, link disable, hot reset, lane reversal, loopback, hold-training, skip-order behavior, electrical-idle handling, L0/L0s/L1/L23 policy, wake/refclkreq behavior, reset timing, illegal-state handling, and training debug controls.
- `PCIE_LC_LINK_WIDTH_CNTL` controls negotiated link width, link-width overrides, dynamic lane negotiation, unused-lane powerdown, lane reversal, reconfiguration behavior, and electrical-idle handling.
- `PCIE_LC_N_FTS_CNTL` controls transmitted FTS/EIE counts and generation-specific N_FTS controls.
- `PCIE_LC_SPEED_CNTL` and `PCIE_LC_SPEED_CNTL2` cover Gen2 through Gen5 strap support, advertised/current/target speeds, override enable/value, companion pattern speed, partner support detection, full-swing/low-swing support, high-speed timeout controls, safe-mode fallback, and train-to-max behavior.
- `PCIE_LC_STATE0` through `PCIE_LC_STATE5` expose the current LTSSM state and a history of previous states.
- `PCIE_LC_LINK_MANAGEMENT_CNTL`, `PCIE_LC_LINK_MANAGEMENT_CNTL2`, `PCIE_LC_LINK_MANAGEMENT_CNTL3`, `PCIE_LC_LINK_MANAGEMENT_STATUS`, and `PCIE_LC_LINK_MANAGEMENT_MASK` cover bandwidth-change hints, link active/idle transitions, PME/PMI gating, dynamic link-width/speed reporting, L1/L23 events, requesters for active-idle, link-turnoff requests, and interrupt/status masks.
- `PCIE_LC_BW_CHANGE_CNTL` reports and controls bandwidth-change interrupts and classifies speed/width changes, failed negotiations, and link bandwidth notifications.
- `PCIE_LC_CDR_CNTL`, `PCIE_LC_LANE_CNTL`, `PCIE_LC_Z10_IDLE_CNTL`, and `PCIE_LC_TRANMIT_FIFO_CDC_CNTL` define CDR test values, corrupted-lane status, Z10 idle gating/timing, and transmit FIFO CDC threshold control.

Consumers use these fields during ASIC initialization, link bring-up, link retraining, suspend/resume, hot reset handling, ASPM/CLKREQ interactions, debugfs diagnostics, and recovery from bad link states.

### Equalization, Presets, Coefficients, and Margining-Related Controls

The chunk contains a dense set of equalization and coefficient controls:

- `PCIE_LC_FORCE_COEFF`, `PCIE_LC_FORCE_COEFF2`, and `PCIE_LC_FORCE_COEFF3` force TX coefficients for 8GT, 16GT, and 32GT paths.
- `PCIE_LC_FORCE_EQ_REQ_COEFF`, `PCIE_LC_FORCE_EQ_REQ_COEFF2`, and `PCIE_LC_FORCE_EQ_REQ_COEFF3` force requested coefficients and record/override other-end FS/LF values for equalization request phases.
- `PCIE_LC_BEST_EQ_SETTINGS` records best preset/pre-cursor/cursor/post-cursor values and the lane these settings apply to.
- `PCIE_LC_CNTL5`, `PCIE_LC_CNTL6`, `PCIE_LC_CNTL7`, `PCIE_LC_CNTL8`, and `PCIE_LC_CNTL10` expose local preset/cursor values, safe recovery, equalization wait/acceptance behavior, FOM timers, loopback equalization controls, default preset overrides, and low-swing link-down controls.
- `PCIE_LC_EQ_CNTL_8GT`, `PCIE_LC_EQ_CNTL_16GT`, and `PCIE_LC_EQ_CNTL_32GT` contain generation-specific equalization bypass/redo/search/preset fields, EQTS2 preset behavior, and preset conversion flags.
- `PCIE_LC_PRESET_MASK_CNTL` masks downstream and upstream preset usage.
- `PCIE_LC_RXRECOVER_RXSTANDBY_CNTL` contains RX recover/standby timing, OOB wait, enable-duration, and symbol-lock controls.

These fields are coupled to PCIe Gen3/Gen4/Gen5 link training and margining flows. The masks are narrowly packed, so callers should use generated helpers instead of open-coded shifts when setting local or remote coefficient values.

### Low-Power, L1 Substate, Save/Restore, and Clock Gating

Power-management-related fields include:

- `PCIE_LC_L1_PM_SUBSTATE` through `PCIE_LC_L1_PM_SUBSTATE5`, which control L1.1/L1.2 advertisement, ASPM and PCI-PM L1 substate entry/exit, T_POWER_ON, common-mode restore timing, LTR thresholds, CLKREQ/FCH target address fields, abort/defer behavior, and refclk/electrical-idle interactions.
- `PCIE_LC_SAVE_RESTORE_1`, `PCIE_LC_SAVE_RESTORE_2`, and `PCIE_LC_SAVE_RESTORE_3`, which expose save/restore enable, direction, index, acknowledge/done bits, data, restored status, timing, and stop-on-error behavior.
- `PCIE_LC_FINE_GRAIN_CLK_GATE_OVERRIDES`, which disables specific dynamic/output/debug-bus clock-gating points for the link controller.
- `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, and `PCIEP_STRAP_LC2`, which describe strap-derived defaults for link width/speed, lane reversal, FTS counts, port type, ASPM/L0s/L1 support, lane equalization, and ECRC generation/checking.

These macros are used where the driver needs to align runtime link behavior with fuses/straps and platform power policy. Save/restore fields indicate that some link-controller state can be moved through a hardware save/restore sequencer rather than represented as kernel memory in this header.

### TX Replay, Credits, and Flow Control

The later part of the `pciedir_p` block defines transmit and credit accounting:

- `PCIE_TX_SEQ` exposes next transmit and acknowledged sequence numbers.
- `PCIE_TX_REPLAY` controls replay number, rollover, stalls, disabling, force replay, timer disable/overwrite, and replay timer.
- `PCIE_TX_ACK_LATENCY_LIMIT` controls ACK latency limit, overwrite, ACK flow-control arbitration, scale, and adjustment.
- `PCIE_TX_CREDITS_FCU_THRESHOLD`, `PCIE_TX_CREDITS_ADVT_*`, `PCIE_TX_CREDITS_INIT_*`, and `PCIE_TX_CREDITS_STATUS` define advertised, initialized, threshold, current, and error status fields for posted, non-posted, and completion credits.
- `PCIE_TX_VENDOR_SPECIFIC` and `PCIE_TX_NOP_DLLP` send vendor-specific and NOP DLLP data.
- `PCIE_TX_REQUEST_NUM_CNTL` limits outstanding non-posted requests.
- `PCIE_FC_P`, `PCIE_FC_NP`, `PCIE_FC_CPL`, and their `VC1` variants expose flow-control credit counters for VC0 and VC1.

These fields matter for performance tuning, link-layer diagnostics, deadlock analysis, and validation of credit return/advertisement behavior.

### Start of the PCIE Directory Block

The chunk enters `pcie_container_pcie0_pciedir` at line 2334. It defines full-width fields for `PCIE_RESERVED`, `PCIE_SCRATCH`, `PCIE_RX_NUM_NAK`, and `PCIE_RX_NUM_NAK_GENERATED`. It then begins `PCIE_CNTL` with shifts for hardware-init write lock, hot-plug delay selection, unsupported-request error reporting disable, malformed atomic operations, HyperTransport non-posted memory write behavior, RX sideband adjusted payload size, ATS unordered-completion RCB disable, and RX RCB reorder enable. The corresponding masks and later `PCIE_CNTL` fields are outside this chunk.

## Control Flow

There is no executable control flow in this header. The implied runtime control flow belongs to AMDGPU register consumers:

1. Include this shift/mask header together with the matching PCIe 6.1.0 offset header.
2. Read a register through the appropriate MMIO, SMN, or config-space helper.
3. Extract fields with the generated mask/shift pair for diagnostics, capability reporting, or policy decisions.
4. Compose a modified register value with field helpers and write it back when changing link, power, error, or credit behavior.

For link bring-up or retraining, the typical sequence is to read strap and capability fields, program link width/speed/equalization/L1SS policy, trigger or wait for training/recovery, then poll state/status/history registers. For error validation, code may enable reporting, inject a physical or transaction error, then inspect RX/TX counters, NAK counts, AER/logging fields, and link-management status.

## State and Persistence Behavior

This chunk defines hardware register state only. The header stores no software state and performs no persistence itself.

Important state classes represented by the fields are:

- Hardware identity and topology state: DXIO revision, linkage presence, lane count, engine count, lane reversal, and physical link width.
- PCI configuration-visible state: command/status bits, capability-list links, LTR/L1SS capabilities, L1SS controls, and lane equalization capability fields.
- Link-controller state: current and historical LTSSM states, negotiated width/speed, partner speed support, bandwidth-change status, link active/idle status, and L1/L23 transitions.
- Programmed policy state: speed/width overrides, equalization presets/coefficients, ASPM/L1SS policy, error reporting masks, hotplug/PME controls, outstanding request limits, credit thresholds, and clock-gating overrides.
- Diagnostic and test state: scratch registers, NAK counters, replay/sequence values, error-injection triggers, ECC status, corrupted-lane status, and save/restore completion/error status.

Persistence across GPU reset, BACO, suspend/resume, or hot reset is determined by the hardware reset domain and by AMDGPU initialization/save/restore code. The presence of `PCIE_LC_SAVE_RESTORE_*` suggests a hardware save/restore mechanism for selected link-controller state, but this header does not specify which registers are covered or when the sequencer must be used.

## Dependencies and Integration Points

This header depends on the wider AMD ASIC register ecosystem:

- Companion PCIe 6.1.0 offset/address headers provide register addresses; this file provides only field positions.
- AMDGPU SOC15 register helpers perform the actual read/modify/write operations.
- PCI core and AMDGPU PCIe code consume command/status, capability, LTR, L1SS, hotplug, FLR, requester-ID, and bus-mastering fields.
- AMDGPU platform power management, ASPM, runtime PM, suspend/resume, BACO, and CLKREQ/refclk code integrate with the L0s/L1/L1SS/L23/Z10 and save/restore fields.
- Link training, recovery, and debug paths integrate with LTSSM state history, speed/width controls, equalization coefficient/preset controls, FTS settings, CDR controls, and lane status.
- RAS/AER/debug paths integrate with error-reporting masks, ECRC/LCRC/poison controls, AER log controls, NAK/replay counters, BCH ECC controls, and error-injection registers.
- Performance and protocol validation paths use TX/RX credit, flow-control, outstanding-request, ACK latency, and replay/sequence fields.

The file is source-tree-aligned with generated AMD hardware names. Downstream code should generally keep these names intact and use wrapper helpers only where an existing AMDGPU abstraction already exists.

## Risks

- Register layout drift is high impact. A wrong mask or shift can change link speed/width policy, corrupt adjacent equalization coefficients, suppress errors, or trigger disruptive power/link behavior.
- Repeated lane and generation blocks are easy to miscopy. Lane equalization fields repeat for lanes 0-15; EQ/coefficient fields repeat across 8GT, 16GT, and 32GT variants.
- Error-injection fields must be gated to test/debug flows. Accidentally enabling bad LCRC/ECRC, malformed TLP, replay timer, NAK, or DLLP injection on a live link can create real protocol failures.
- Link-training fields can strand hardware in recovery, detect, loopback, hold-training, or illegal-state recovery if written out of order.
- Power-management fields interact with CLKREQ, refclk, electrical idle, L1.1/L1.2, L23, and Z10 behavior. Incorrect programming can cause resume failures or intermittent link loss.
- Status-clearing semantics are not encoded here. Some status bits may be sticky, write-one-to-clear, self-clearing, or read-only; callers must follow the register spec and existing AMDGPU access patterns.
- Credit and replay controls can affect forward progress. Misprogrammed FCU thresholds, outstanding request limits, ACK latency, or replay disable/timer fields can create stalls that look like unrelated GPU hangs.
- The chunk ends mid-`PCIE_CNTL`. The merge lane must combine this document with the next chunk before treating `PCIE_CNTL` coverage as complete.

## Test Signals

Useful validation signals for code consuming these macros include:

- Build coverage for AMDGPU PCIe 6.1.0 paths that include this header with the matching offset header and no missing or duplicate macro definitions.
- Compile-time or unit-style checks that representative `REG_SET_FIELD`/`REG_GET_FIELD` operations round-trip multi-bit fields, especially packed equalization coefficients, L1SS timing values, speed/width overrides, and credit counters.
- Hardware link bring-up and retraining tests across supported widths and speeds, with `PCIE_LC_STATE*`, `PCIE_LC_SPEED_CNTL*`, `PCIE_LC_LINK_WIDTH_CNTL`, and bandwidth-change status matching expected transitions.
- Suspend/resume, BACO, runtime PM, and hot reset tests that verify L1SS, CLKREQ/refclk, save/restore, and scratch/status fields are restored or reinitialized as platform policy requires.
- AER/RAS validation that uses controlled error injection and confirms expected ECRC/LCRC/poison/NAK/replay counters, status bits, and interrupt/log behavior without leaving injection bits armed.
- ASPM/L1SS tests that validate LTR thresholds, common-mode restore time, T_POWER_ON, L1.1/L1.2 enablement, and abort/defer behavior under traffic and idle conditions.
- Flow-control stress tests that monitor advertised/initialized/current credits, FCU thresholds, outstanding non-posted request limits, and ACK latency fields under heavy DMA and completion traffic.
- Debugfs or trace diagnostics that decode LTSSM history, partner speed support, lane reversal, physical width, NAK counters, replay sequence values, and ECC/corrupted-lane status into expected human-readable values.

### subset-b-003358: lines 2356-4250

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
