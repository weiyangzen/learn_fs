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
