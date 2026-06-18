# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 31978-34356

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: register-field `__SHIFT` and `_MASK` macros for PCIe/NBIO register words. There are no C functions, structs, enums, branches, loops, locks, allocations, MMIO accesses, or persistence operations in this range.

The range starts in the tail of `PCIE_LC_CNTL6`, then covers `PCIE_LC_CNTL7`, PCIe strap controls, L1 PM substate controls, link-control and equalization controls, transmit/data-link credit controls, a `nbio_pcie0_pciedir` address block, PCIe RX/config/status/PM/performance/strap/PRBS registers, software reset and clock/power-management control registers, SMN aperture IDs, lane-count and interrupt-pin-sharing indicators, RX margining controls, TX last-TLP/tracking/status/attribute controls, HIP aperture registers, SMU fenced policy bits, and the beginning of `PCIE_PERF_CNTL_TXCLK10`.

Both boundaries are artificial. The first visible lines are only the final `PCIE_LC_CNTL6` masks for retimer presence handling, and the last visible line is the first `PCIE_PERF_CNTL_TXCLK10__EVENT0_SEL__SHIFT` definition without that register's remaining fields. Adjacent chunks must be merged before making whole-register claims for those boundary groups.

Although the repository path is under a local `ceph-client` mirror, this source is AMDGPU hardware metadata. It describes GPU PCIe/NBIO register bit layout, not Ceph or distributed filesystem logic.

## Purpose

The purpose of this header section is to publish bit positions and masks for NBIO 4.3.0 PCIe link-management, power-management, transmit/receive, flow-control, diagnostic, reset, aperture, and performance-counter registers. Matching address macros live in `nbio_4_3_0_offset.h`; this file defines how software extracts or updates individual fields after selecting the correct register address.

Driver code consumes these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and related SOC15/NBIO access wrappers. The macros form a hardware ABI. A wrong mask or shift can compile cleanly while programming the wrong bit in a PCIe control register, misreading a status bit, or corrupting adjacent fields during read/modify/write.

The chunk's main functional surfaces are:

- PCIe link controller behavior: training, ESM/retimer handling, scheduled RX equalization, lane reversal, link management, and link state/status controls.
- Strap-derived PCIe configuration: lane negotiation, compliance behavior, retimer presence-detect support, CCIX/LTR/OBFF capability, ESM support, and I2C board strap data.
- L1 PM substates and save/restore timing: ASPM/PCI-PM L1.1/L1.2 overrides, CLKREQ filtering, power-on timers, LTR thresholds, FCH target addressing, save/restore write-enable and register-data fields.
- Transmit/data-link controls: replay buffer behavior, ACK latency, advertised/init credits, flow-control credit limits, No-Op DLLP handling, request-number controls, and credit-status visibility.
- PCIe direct-register block diagnostics: RX NAK counters, config controls, AER masking, bus/CI controls, link-controller states/status, write-protection, last received and transmitted TLP logging, I2C register access, PM controls, SDP controls, and performance-counter selectors/counts.
- PRBS, RX margining, reset, clock/power management, SMN aperture, page-gating, HIP aperture, SMU policy, TX tracking, and TX attribute override fields.

## Important Macro Families

### Link Controller, Straps, And L1 PM

The chunk begins with the last `PCIE_LC_CNTL6` masks for retimer presence behavior: override, ignore, and retimer-presence bit fields. The next complete group, `PCIE_LC_CNTL7`, exposes link-controller toggles for TS2 config completion expectations, robust training-bit checks, electrical-idle handling, NBIF ASPM input, reversal clearing/locking, forced RX equalization progress, scheduled RX equalization interval/mode/upconfig, link-management enablement, timeout auto-reject, and ESM PLL/init state bits.

`PCIEP_STRAP_LC`, `PSWUSP0_PCIEP_STRAP_MISC`, and `PCIEP_STRAP_LC2` describe strap-sourced configuration. These include FTS/TS count encodings, skip interval, receiver-detect bypass, compliance disable/force, lane reversal, auto root-complex speed negotiation disable bits for base, 16 GT/s, and 32 GT/s speeds, lane-negotiation width, software margining ownership, retimer presence-detect support, E2E prefix support, extended format support, OBFF/LTR support, CCIX enablement, and ESM mode/reach/recalibration/timing/quick-equalization timeout capability.

`PCIE_LC_L1_PM_SUBSTATE` through `PCIE_LC_L1_PM_SUBSTATE5` define the L1 substate and save/restore timing surface. The fields cover L1 substate override enablement, PCI-PM and ASPM L1.1/L1.2 override bits, CLKREQ filtering, `T_POWER_ON` scale/value, FCH copy enable/trigger, L1.2 exit blocking, L1.1/L1.2 powerdown encodings, deferred L1.2 exit handling, wake/abort controls, AUX counter increment sources, common-mode restore time, LTR threshold scale/value, FCH target address, L1.2 powerdown delay and LTR-latency fields. These definitions are used around link power-management programming, where preserving unrelated bits during read/modify/write is critical.

### Link Equalization, Clock Gating, Save/Restore, And Speed Controls

`PCIEP_BCH_ECC_CNTL` exposes ECC enable, correction-disable, debug, and syndrome-related fields for the PCIe BCH path.

`PCIE_LC_CNTL8`, `PCIE_LC_CNTL9`, `PCIE_LC_CNTL10`, `PCIE_LC_CNTL11`, and `PCIE_LC_CNTL12` add more link-controller behavior: linkwidth overrun controls, periodic TS/FTS count controls, received-FTS thresholds, lane reversal/cropping controls, target link speed, persistent reset behavior, ASPM L1 entry/exit delays, RX electric-idle detection, retimer and upconfig behavior, EQ-related options, lane reversal request controls, PCIe generation transition controls, and ESM-related knobs.

`PCIE_LC_FORCE_COEFF2`, `PCIE_LC_FORCE_EQ_REQ_COEFF2`, `PCIE_LC_FORCE_COEFF3`, and `PCIE_LC_FORCE_EQ_REQ_COEFF3` publish coefficient override and equalization-request fields. They are highly timing-sensitive: callers must understand the PCIe equalization flow before forcing coefficient or request values.

`PCIE_LC_FINE_GRAIN_CLK_GATE_OVERRIDES` defines per-subblock clock-gating override bits for the link controller. `PCIE_LC_SAVE_RESTORE_1` and `PCIE_LC_SAVE_RESTORE_2` describe register address, data, write-enable, and port fields for save/restore flows. `PCIE_LC_SPEED_CNTL2` contains speed-change and reserved control fields used around link speed management.

### TX, Replay, Credits, And Flow Control

`PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, `PCIE_TX_ACK_LATENCY_LIMIT`, `PCIE_TX_CREDITS_FCU_THRESHOLD`, `PCIE_TX_VENDOR_SPECIFIC`, `PCIE_TX_NOP_DLLP`, and `PCIE_TX_REQUEST_NUM_CNTL` define transmit and data-link layer policy. They cover sequence/replay behavior, ACK latency bounds, FC update thresholds, vendor-specific message fields, No-Op DLLP generation, and requester/request-number control.

`PCIE_TX_CREDITS_ADVT_P`, `PCIE_TX_CREDITS_ADVT_NP`, and `PCIE_TX_CREDITS_ADVT_CPL` define advertised posted, non-posted, and completion header/data credits. `PCIE_TX_CREDITS_INIT_P`, `PCIE_TX_CREDITS_INIT_NP`, and `PCIE_TX_CREDITS_INIT_CPL` define initial credit values. `PCIE_TX_CREDITS_STATUS` exposes selected credit status and update behavior.

`PCIE_FC_P`, `PCIE_FC_NP`, `PCIE_FC_CPL`, and their `VC1` variants expose flow-control limit/receive fields for posted, non-posted, and completion traffic classes. These fields are central to PCIe data-link correctness. Misprogramming credit masks can manifest as stalls, replay storms, or traffic-class-specific failures rather than a simple boot-time error.

### PCIe Direct Address Block

The `addressBlock: nbio_pcie0_pciedir` marker starts a direct PCIe register namespace. The early groups include:

- `PCIE_RESERVED` and `PCIE_SCRATCH` fields for reserved/debug scratch state.
- `PCIE_RX_NUM_NAK` and `PCIE_RX_NUM_NAK_GENERATED` counters for received and generated NAK diagnostics.
- `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, `PCIE_CNTL2`, `PCIE_CFG_CNTL`, `PCIE_CI_CNTL`, and `PCIE_BUS_CNTL` fields for global PCIe, configuration, client-interface, and bus behavior.
- `PCIE_RX_CNTL5`, `PCIE_RX_CNTL4`, `PCIE_RX_CNTL2`, `PCIE_RX_AD`, and `PCIE_COMMON_AER_MASK` fields for RX behavior and common AER masking.
- `PCIE_LC_STATE6` through `PCIE_LC_STATE11`, `PCIE_LC_STATUS1`, and `PCIE_LC_STATUS2` fields for link-controller internal state and status visibility.
- `PCIE_WPR_CNTL` and `PCIE_RX_LAST_TLP0` through `PCIE_RX_LAST_TLP3` fields for write-protection control and last-received-TLP capture.

`PCIE_I2C_REG_ADDR_EXPAND` and `PCIE_I2C_REG_DATA` define address/data fields for an I2C-style register access path. `PCIE_LC_PM_CNTL` and `PCIE_LC_PM_CNTL2` define link power-management control. `PCIE_P_CNTL`, `PCIE_P_BUF_STATUS`, `PCIE_P_DECODER_STATUS`, `PCIE_P_MISC_STATUS`, and `PCIE_P_RCV_L0S_FTS_DET` describe protocol/parser buffer, decoder, miscellaneous, and L0s FTS detection state. `PCIE_SDP_CTRL`, `PCIE_SDP_SWUS_SLV_ATTR_CTRL`, and `PCIE_SDP_CTRL2` describe SDP path control and slave attribute overrides.

### Performance Counters, Straps, And PRBS Diagnostics

`PCIE_PERF_COUNT_CNTL` controls performance counting. `PCIE_PERF_CNTL_TXCLK1` through `PCIE_PERF_CNTL_TXCLK6` and `PCIE_PERF_CNTL_TXCLK7` through `PCIE_PERF_CNTL_TXCLK9` define event selectors and full flags for two counters per TX clock domain group. Matching `PCIE_PERF_COUNT0_TXCLK*` and `PCIE_PERF_COUNT1_TXCLK*` macros expose full-width counter values. The chunk ends as `PCIE_PERF_CNTL_TXCLK10` begins, so that register's full field list is in the next chunk.

`PCIE_PERF_CNTL_EVENT_LC_PORT_SEL` and `PCIE_PERF_CNTL_EVENT_CI_PORT_SEL` select link-controller and client-interface event ports. `PCIE_STRAP_F0`, `PCIE_STRAP_MISC`, `PCIE_STRAP_MISC2`, `PCIE_STRAP_PI`, and `PCIE_STRAP_I2C_BD` expose additional strap-derived feature and board-data fields.

`PCIE_PRBS_CLR`, `PCIE_PRBS_STATUS1`, `PCIE_PRBS_STATUS2`, `PCIE_PRBS_FREERUN`, `PCIE_PRBS_MISC`, `PCIE_PRBS_USER_PATTERN`, `PCIE_PRBS_LO_BITCNT`, `PCIE_PRBS_HI_BITCNT`, and `PCIE_PRBS_ERRCNT_0` through `PCIE_PRBS_ERRCNT_15` define pseudo-random bit sequence test controls, bit counters, and lane-specific error counters. These are hardware validation and signal-integrity diagnostics rather than normal data-path policy.

### Reset, Clock/Power Management, Apertures, And Margining

`SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0`, `SWRST_COMMAND_1`, `SWRST_CONTROL_0` through `SWRST_CONTROL_6`, `SWRST_EP_COMMAND_0`, and `SWRST_EP_CONTROL_0` define software-reset command, status, and endpoint reset-control fields. The macros expose bit locations only; reset sequencing, polling, and dependency ordering are handled by executable driver code outside this header.

`CPM_CONTROL`, `CPM_SPLIT_CONTROL`, and `CPM_CONTROL_EXT` describe clock/power-management controls. `SMN_APERTURE_ID_A` and `SMN_APERTURE_ID_B` expose SMN aperture identifiers. `LNCNT_CONTROL` exposes lane-count control fields. `SMU_INT_PIN_SHARING_PORT_INDICATOR` and `SMU_INT_PIN_SHARING_PORT_INDICATOR_TWO` expose port-indicator bits used for SMU interrupt pin-sharing state. `PCIE_PGMST_CNTL` and `PCIE_PGSLV_CNTL` define master/slave page-gating controls, while `LC_CPM_CONTROL_0` and `LC_CPM_CONTROL_1` define link-controller CPM fields.

`PCIE_RXMARGIN_CONTROL_CAPABILITIES`, `PCIE_RXMARGIN_1_SETTINGS`, and `PCIE_RXMARGIN_2_SETTINGS` define receiver-margining capabilities and settings. These fields are relevant to PCIe signal margin diagnostics and must be interpreted with the hardware and PCIe margining protocol.

### TX Logging, Tracking, Status, Attributes, HIP, And SMU Fenced Bits

`PCIE_TX_LAST_TLP0` through `PCIE_TX_LAST_TLP3` capture the last transmitted TLP words. `PCIE_TX_TRACKING_ADDR_LO`, `PCIE_TX_TRACKING_ADDR_HI`, and `PCIE_TX_TRACKING_CTRL_STATUS` define address, enable, port, unit ID, and status-valid fields for TX tracking. `PCIE_TX_CTRL_4` adds a TX port access timer skew field.

`PCIE_TX_STATUS` exposes memory-ready, CI idle, pending-read, write-response, TX idle, clock-request idle, header/data FIFO empty, and no-free-credit status bits. `PCIE_TX_F0_ATTR_CNTL` and `PCIE_TX_SWUS_ATTR_CNTL` provide IDO, relaxed-ordering, and no-snoop override fields for posted, non-posted, and completion traffic. `PCIE_MST_CTRL_1` describes master posted-data/header credit advertisements, override enables, pending-reset behavior, and idle hysteresis.

`PCIE_HIP_REG0` through `PCIE_HIP_REG8` define host-interface aperture base, limit, enable, PASID mode, ReqAT mode, ReqIO mode, and mask fields for two apertures. `SMU_PCIE_FENCED1_REG` and `SMU_PCIE_FENCED2_REG` expose one-bit SMU-fenced policy toggles for CrossFire lockdown and overclocking enablement.

## Important APIs, Types, And Functions

This chunk defines no APIs, C types, or functions by itself. Its externally visible interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask at its already-shifted position.
- Register names correspond to address macros in `nbio_4_3_0_offset.h`, usually named `reg<REGISTER>` or a closely related generated address symbol.

The practical API boundary is the AMDGPU register helper layer. Typical consumers read a register, clear a mask, set a value shifted by the corresponding `__SHIFT`, and write the register back. For single-bit fields, code commonly ORs or ANDs the `_MASK` directly. For example, `amdgpu/nbio_v4_3.c` includes this header and uses `PCIE_LC_CNTL7__LC_NBIF_ASPM_INPUT_EN_MASK` with `regPCIE_LC_CNTL7` in `nbio_v4_3_program_aspm()`.

## Control Flow

There is no executable control flow in this header. Runtime control flow is supplied by driver code that includes the generated NBIO 4.3.0 headers:

1. The driver selects an ASIC/IP-specific register address from `nbio_4_3_0_offset.h`.
2. It selects one or more field definitions from this `nbio_4_3_0_sh_mask.h` file.
3. It reads or writes through SOC15/NBIO/PCIe helper functions.
4. For field updates, it performs read/modify/write using masks and shifts so unrelated fields are preserved.
5. Hardware applies the update to link training, ASPM/L1 substate behavior, credit flow, reset, diagnostics, margining, performance counting, or aperture policy.

One concrete in-tree flow is `nbio_v4_3_program_aspm()`: it reads `regPCIE_LC_CNTL7`, sets `PCIE_LC_CNTL7__LC_NBIF_ASPM_INPUT_EN_MASK`, and writes the register back if the value changed. Other fields in this chunk may be used by board bring-up, debug, validation, power management, or generated-register coverage even when not referenced explicitly in the visible C files.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It describes hardware-backed state whose lifetime is controlled by GPU reset type, PCIe link resets, firmware/BIOS initialization, driver programming, power-state transitions, link retraining, diagnostic commands, and SMU policy.

The represented hardware state includes:

- Sticky or live PCIe link-controller control/status fields for training, equalization, speed control, ESM, retimers, lane reversal, and link-management state.
- Strap-derived configuration that may be sampled from fuses/straps or firmware-configured defaults and may not be freely writable at runtime.
- L1 PM substate controls, timings, LTR thresholds, save/restore register-data fields, and powerdown delay state.
- TX sequence, replay, ACK latency, advertised/init credits, flow-control limits, request numbering, and credit-status state.
- RX/CI/bus/config status, NAK counters, last-TLP capture words, AER masking, and performance counter state.
- PRBS test control, bit counters, and lane-specific error counters.
- Software-reset command/status state and page-gating or clock/power-management controls.
- SMN aperture IDs, HIP aperture base/limit/mode fields, and SMU-fenced policy bits.

Some fields are stable configuration until reset or reprogramming, such as ASPM input enable, L1 substate overrides, credit advertisements, strap-derived feature bits, aperture base/limit registers, and attribute override controls. Other fields are live status, counters, latched diagnostics, command triggers, or hardware-updated logs. The macro names do not encode access semantics such as read-only, write-one-clear, self-clearing, sticky, strap-only, or reset-only; callers must rely on AMD's register database, PCIe semantics, and existing AMDGPU programming sequences.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the matching register addresses and base indices.
- Other generated NBIO 4.3.0 headers such as defaults or SMN definitions where present.
- AMDGPU helper conventions for `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, PCIe indirect/direct access, and SOC15 IP block selection.
- PCIe architectural semantics for link training, ASPM, L1 substates, flow-control credits, AER, PRBS, receiver margining, and reset behavior.

Direct in-tree include points for `nbio_4_3_0_sh_mask.h` include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which programs NBIO 4.3 behavior and directly uses the `PCIE_LC_CNTL7` ASPM-input field from this chunk.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, which include the NBIO 4.3.0 offsets and masks for SMU13 power-management register access.

The related offset header is also included by DCN 3.2 resource code. Those display paths need register addresses, while field-level use in this chunk is mainly visible in NBIO and SMU code.

## Risks And Edge Cases

- Generated hardware contract drift is the main risk. A stale shift or mask can compile but update the wrong hardware bit or silently decode a status field incorrectly.
- The chunk starts and ends mid-register-family. `PCIE_LC_CNTL6` and `PCIE_PERF_CNTL_TXCLK10` require adjacent chunks for complete documentation.
- Many fields are timing-sensitive. Link training, equalization, ESM, retimer, L1.2, CLKREQ, and speed-change bits can create intermittent link failures rather than immediate deterministic failures.
- Strap fields may be read-only, sampled at reset, or firmware-owned. Treating all strap masks as ordinary writable state can produce misleading tests or ineffective writes.
- L1 PM substate and LTR fields interact with platform PCIe ASPM policy, endpoint capability, root-port behavior, and SMU power management. Incorrect masks can cause resume failures, latency regressions, link drops, or excess power draw.
- TX credit and flow-control fields are tightly coupled. Bad masks can corrupt posted/non-posted/completion accounting and appear as stalls, replays, NAK storms, or throughput drops.
- Counter, last-TLP, PRBS, and margining fields may be self-clearing, latch-on-read, command-triggered, or lane-specific. Generic read/modify/write can lose diagnostics if the access semantics are ignored.
- Reset and page-gating controls can affect multiple subblocks. Wrong field definitions or sequencing can leave the device partially reset, clock-gated during access, or unable to complete later register transactions.
- HIP and SMN aperture fields encode address windows and request modes. Incorrect base/limit or mode masks can redirect access, break PASID/ReqAT/ReqIO behavior, or expose isolation issues.
- SMU fenced bits are policy-sensitive. Overclocking or CrossFire lockdown fields should be interpreted with SMU ownership and platform policy rather than as unconditional driver toggles.

## Test Signals

Useful validation signals for this chunk are a mix of generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU configurations that include `nbio_v4_3.c` and SMU13 PPT files. Missing or renamed macros in this chunk should surface as compile failures.
- Run generated-header consistency checks: for each register field, verify that masks align with shifts, multi-bit masks are contiguous where expected, single-bit masks match `1 << shift`, and repeated counter/lane/performance blocks follow the expected pattern.
- Compare `nbio_4_3_0_sh_mask.h` against `nbio_4_3_0_offset.h` and AMD's source register database, especially `PCIE_LC_CNTL7`, L1 PM substate groups, TX credit groups, PRBS counters, HIP registers, SMU fenced registers, and boundary groups.
- Exercise `nbio_v4_3_program_aspm()` on supported hardware and check that ASPM/LTR behavior, link stability, suspend/resume, and power measurements remain sane.
- Validate PCIe link speed changes, retraining, equalization, retimer paths, and L1.1/L1.2 entry/exit around the fields in the link-controller and PM-substate groups.
- Use PCIe error and performance diagnostics where available: NAK counters, last-TLP logs, TX status bits, flow-control counters, and AER masks should behave without unrelated bit corruption.
- Run PRBS and RX margining diagnostics across all lanes; lane-specific error counters and margin settings should map to the intended lane and not cross-affect adjacent counters.
- Exercise software reset and page-gating paths under runtime suspend/resume or recovery scenarios; incomplete reset status, hung register reads, or clock-gating deadlocks are strong signals of field drift.
- Validate HIP/SMN aperture programming only through approved platform flows; wrong address-window decoding or request-mode behavior points to aperture mask or shift mistakes.
