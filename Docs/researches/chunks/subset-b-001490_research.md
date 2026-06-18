# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 4659-8787

## Scope And Purpose

This chunk is part of AMDGPU's generated BIF 5.1 register field mask header. It contains no executable logic; it is a compile-time hardware register layout contract for the Bus Interface and PCIe blocks used by VI-era AMD GPUs. The paired `*_MASK` and `*__SHIFT` macros tell driver code where each field lives inside a 32-bit MMIO or indirect PCIe register.

The line range starts in top-level BIF control fields, including reset enables, PCIe/PIF clock-switch timing, BACO misc selection, reset-control strap state, RFE access mode, and BIF memory power-gating control. It then defines the indexed PCIe port access registers and a large set of PCIe bridge/function field layouts for downstream functions `D2F1`, `D2F2`, and the beginning of `D2F3`.

The dominant content is the repeated `D2F1_*` and `D2F2_*` PCI configuration and PCIe capability/register spaces. These cover port indirect access, transaction-layer transmit and receive controls, credit accounting, AER/error handling, link-controller state, link training and equalization, hotplug/PME behavior, MSI/MSI-map capability fields, virtual-channel resources, ACS, multicast, and conventional PCI-to-PCI bridge configuration fields. The `D2F3_*` section begins the same pattern but this chunk ends inside `D2F3_PCIE_ERR_CNTL`, so later lines complete that function's register families.

The file path is under a Ceph source mirror, but the content here is AMDGPU Linux kernel driver register metadata. There is no Ceph filesystem behavior in this chunk.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or persistent variables in this range. The API surface is the generated macro naming scheme:

- `<REGISTER>__<FIELD>_MASK` is the raw bit mask for a register field.
- `<REGISTER>__<FIELD>__SHIFT` is the least-significant bit position used to normalize or insert that field.
- Callers use these constants directly or through AMDGPU helpers such as `REG_SET_FIELD()`, `RREG32_PCIE()`, `WREG32_PCIE()`, `RREG32()`, and `WREG32()`.

The top-level BIF families are small but important:

- `BIF_RESET_EN` exposes enable bits for BIF soft/cold-style reset and per-function FLR/reset delay controls.
- `BIF_PIF_TXCLK_SWITCH_TIMER` describes PLL acknowledgement and switch timers for PCIe/PIF transmit clock changes.
- `BIF_BACO_MSIC` contains BACO-related clock/reset mux selection fields.
- `BIF_RESET_CNTL` exposes strap capture, reset-done, link-training enable, strap-valid, and warm-reset recapture/hold behavior.
- `BIF_RFE_CNTL_MISC` exposes access-mode selectors for PIF, power-register, and PCIe-core back-end register access.
- `BIF_MEM_PG_CNTL` describes BIF memory shutdown enable and timer fields.
- `C_PCIE_P_INDEX` and `C_PCIE_P_DATA` are full-width indexed PCIe port address/data registers.

The `D2F1_PCIE_PORT_INDEX/DATA`, `D2F2_PCIE_PORT_INDEX/DATA`, and `D2F3_PCIE_PORT_INDEX/DATA` macros describe per-function indirect PCIe port access windows. The matching `*_PCIEP_RESERVED`, `*_PCIEP_SCRATCH`, `*_PCIEP_HW_DEBUG`, and `*_PCIEP_PORT_CNTL` fields expose reserved/scratch/debug bits plus port request, snoop override, hotplug message, native PME, power fault, payload/completion allocation, and sequence-number debug controls.

The transmit path families appear for each function covered by the chunk. `*_PCIE_TX_CNTL` controls non-snoop/relaxed ordering overrides, packed packet and TLP flush behavior, completion/non-posted pass policies, extra power-management request clearing, and flow-control update timeout. `*_PCIE_TX_REQUESTER_ID`, `*_PCIE_TX_REQUEST_NUM_CNTL`, `*_PCIE_TX_SEQ`, `*_PCIE_TX_REPLAY`, and `*_PCIE_TX_ACK_LATENCY_LIMIT` expose requester ID fields, outstanding non-posted request limits, transmit sequence state, replay counters/timers, and ACK latency overrides. `*_PCIE_TX_CREDITS_*` and `*_PCIE_FC_*` define posted, non-posted, and completion credit advertisement, initialization, status, and flow-control thresholds.

The receive path and error-control families include `*_PCIE_ERR_CNTL`, `*_PCIE_RX_CNTL`, `*_PCIE_RX_CNTL3`, `*_PCIE_RX_EXPECTED_SEQNUM`, `*_PCIE_RX_VENDOR_SPECIFIC`, and `*_PCIE_RX_CREDITS_ALLOCATED_*`. These define error reporting disables and injection bits, ECRC/LCRC handling, AER header log timers, slave buffer halt reset/status, completion timeout handling, TPH and PASID-related unsupported-request filters, receive sequence numbers, vendor status/data, and allocated receive credits.

The link-controller families are one of the highest-impact parts of the chunk. `*_PCIE_LC_CNTL` through `*_PCIE_LC_CNTL6`, `*_PCIE_LC_BW_CHANGE_CNTL`, `*_PCIE_LC_TRAINING_CNTL`, `*_PCIE_LC_LINK_WIDTH_CNTL`, `*_PCIE_LC_N_FTS_CNTL`, `*_PCIE_LC_SPEED_CNTL`, `*_PCIE_LC_CDR_CNTL`, `*_PCIE_LC_LANE_CNTL`, `*_PCIE_LC_FORCE_COEFF`, `*_PCIE_LC_BEST_EQ_SETTINGS`, `*_PCIE_LC_FORCE_EQ_REQ_COEFF`, and `*_PCIE_LC_STATE0` through `STATE5` describe ASPM/L0s/L1 policy, recovery and quiesce controls, link reset/retrain controls, link speed and width requests/status, N_FTS training parameters, Gen3 equalization coefficients, CDR behavior, lane control, and link-controller state machine observability.

The conventional PCI/PCIe capability space for `D2F1` and `D2F2` is also laid out in detail. It includes `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class code fields, bridge bus-number/base/limit windows, interrupt pins/lines, bridge-control fields, PM capability/status, PCIe capability and device/link/slot/root capability-control-status registers, MSI capability/message/data registers, SSID and MSI-map capability registers, vendor-specific enhanced capability headers, virtual-channel capability/resource controls, device serial number, AER enhanced capability, uncorrectable/correctable error status/mask/severity, header/TLP-prefix logs, root error command/status/source ID, secondary/link-control capability, per-lane equalization control for lanes 0-15, ACS capability/control, and multicast capability/control/address/receive/block/overlay fields.

## Control Flow

This chunk has no local control flow. Its effect on runtime behavior is indirect: code that touches BIF or PCIe registers depends on these constants for every branch condition and write value that interprets packed fields.

A typical consumer sequence is:

1. Read a register through a matching address macro from `bif_5_1_d.h`, often via `RREG32_PCIE()`/`RREG32()` or an indirect port accessor.
2. Decode a field with `value & REGISTER__FIELD_MASK`, optionally shifting by `REGISTER__FIELD__SHIFT`.
3. For updates, clear the old field with `value &= ~REGISTER__FIELD_MASK`.
4. Insert a new value at `REGISTER__FIELD__SHIFT` or use `REG_SET_FIELD()`.
5. Write the register back through `WREG32_PCIE()`/`WREG32()` while holding any required register-access lock.

The VI AMDGPU code shows the relevant access pattern. `vi_pcie_rreg()` and `vi_pcie_wreg()` serialize indirect PCIe access with `adev->reg.pcie.lock`, write `mmPCIE_INDEX`, drain/read it back, then read or write `mmPCIE_DATA`. Link-power and ASPM paths in `vi.c` use macros from this BIF namespace such as `PCIE_LC_CNTL__LC_L0S_INACTIVITY_MASK`, `PCIE_LC_CNTL__LC_L1_INACTIVITY_MASK`, `PCIE_LC_CNTL__LC_PMI_TO_L1_DIS_MASK`, `PCIE_LC_CNTL2__LC_ALLOW_PDWN_IN_L1_MASK`, `PCIE_LC_CNTL3__LC_GO_TO_RECOVERY_MASK`, and `PCIE_LC_TRAINING_CNTL__LC_DISABLE_TRAINING_BIT_ARCH_MASK` in read-modify-write sequences. The `iceland_ih.c` and `uvd_v6_0.c` files include `bif/bif_5_1_d.h` and, for interrupt handling, `bif/bif_5_1_sh_mask.h`, making this generated header part of the ASIC-specific compile-time register interface.

Because the chunk is macro-only, wrong values do not create obvious local control-flow defects. Instead they alter the behavior of distant driver flows: reset programming, power-management setup, PCIe link retraining, AER error handling, MSI programming, virtual-channel configuration, multicast/ACS exposure, and diagnostic/debug paths.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It describes hardware-backed state owned by the PCIe/BIF block. Values represented by these fields can persist until changed by a driver write, firmware, hardware self-clearing behavior, link retrain, FLR, hot reset, BACO/power-gating transition, suspend/resume, or full ASIC reset.

The state described by this chunk spans several categories:

- Reset and strap state: `BIF_RESET_EN` and `BIF_RESET_CNTL` can affect whether functions accept FLR/reset paths, when reset completion is visible, and whether straps are recaptured or considered valid.
- Link state and policy: `*_PCIE_LC_*`, `*_LINK_*`, `*_DEVICE_*`, `*_SLOT_*`, and `*_ROOT_*` fields reflect negotiated speed/width, link training, equalization, ASPM/L-state policy, slot/hotplug behavior, root error state, and PCIe capability settings.
- Data-path counters and credits: TX/RX credit fields, flow-control thresholds, advertised/init/current credit status, and allocated receive credit registers report or program the movement of posted, non-posted, and completion traffic.
- Error and diagnostic state: AER status/masks/severity, header/TLP logs, ECC/error-injection fields, debug buses, lane error status, LC state registers, and replay/sequence fields describe sticky or instantaneous error/debug state.
- Configuration identity/capability state: vendor/device/class IDs, bridge windows, MSI, PM, virtual-channel, ACS, multicast, and enhanced capability-list pointers are part of the PCI configuration view exposed for each downstream function.

The macros do not encode access semantics. A field name alone does not say whether the bit is read-only, write-one-to-clear, strap-derived, sticky until reset, self-clearing, reserved, or safe only when the link is quiesced. Consumers must rely on ASIC documentation and existing driver sequencing.

## Dependencies And Integration Points

This header depends on the generated AMDGPU register-header ecosystem. It should be used with matching address definitions from `bif_5_1_d.h`; the address header names the MMIO or indirect register, while this file names the bit layout inside the register.

Primary integration points are:

- AMDGPU VI ASIC initialization and golden-register setup, including indirect PCIe register programming through `mmPCIE_INDEX` and `mmPCIE_DATA`.
- PCIe link and ASPM management in AMDGPU, where `PCIE_LC_*` masks and shifts tune L0s/L1 inactivity, L1 powerdown, recovery, quiesce, training-disable workarounds, and link state transitions.
- Interrupt and ring-related VI code that includes the BIF 5.1 headers as part of the ASIC register namespace.
- Power and reset flows that may use BIF reset, BACO, memory power-gating, strap, and PIF clock-switch timing fields.
- PCI configuration exposure and virtualization/bridge behavior for downstream functions `D2F1` and `D2F2`, plus the start of `D2F3`.
- Error reporting and diagnostics, especially AER status/mask/severity, error-injection, header/TLP prefix logs, lane equalization controls, debug fields, and flow-control/replay state.
- Common AMDGPU register helper macros such as `REG_SET_FIELD()` and accessor functions/macros that require exact field-mask names.

The `D2F1`/`D2F2` duplication matters for multi-function PCIe layouts: generation consistency is required so the same semantic field maps correctly for each downstream function. The `D2F3` portion begins in this chunk, but its complete surface is split across the following lines/chunk.

## Risks And Edge Cases

The central risk is silent hardware misprogramming. A single incorrect mask or shift can read the wrong status bit, corrupt adjacent fields during a read-modify-write, or leave a control bit unchanged while the driver believes it acted.

High-risk fields include reset and FLR enables, link retraining/quiesce/reset controls, ASPM/L0s/L1 inactivity fields, link speed/width request fields, equalization coefficient fields, error injection bits, AER masks/severities/status bits, MSI message controls, bridge window base/limit fields, ACS controls, and virtual-channel resource controls. Many of these can affect device visibility, DMA traffic, interrupt delivery, error containment, or PCIe fabric isolation.

The repeated `D2F1` and `D2F2` definitions are vulnerable to generated-copy mistakes. A field that is correct for one function but shifted incorrectly for another would compile cleanly and only fail on hardware paths that exercise that specific function. The same applies to the per-lane equalization macros for lanes 0-15, where suffix/order mistakes can present as failures only at specific widths, lane reversals, or Gen3 equalization states.

Fields with paired enable/value semantics are easy to misuse. Override/value fields in link control, error injection, and credit/timing controls may have no effect without an enable bit, while enabling an override with a stale value can force an unintended PCIe state.

Status and sticky error fields need caller-specific clearing rules. This header describes bits for AER, root error status, correctable/uncorrectable errors, lane errors, replay counters, buffer halt status, and header/TLP logs, but it does not define whether reads clear them, writes clear them, or separate reset bits are required.

The requested range ends at line 8787 on `D2F3_PCIE_ERR_CNTL__STRAP_POISONED_ADVISORY_NONFATAL_MASK` without the matching `__SHIFT` line and without the rest of the `D2F3` function register set. The merge lane should treat this as a chunk boundary artifact, not as an absent definition in the full source file.

## Test Signals

Useful validation is mostly build-time plus hardware behavior:

- AMDGPU builds for VI-era ASICs should compile with all BIF 5.1 field names used by `vi.c`, `iceland_ih.c`, `uvd_v6_0.c`, and related code.
- Indirect PCIe register access should remain serialized and stable through `mmPCIE_INDEX`/`mmPCIE_DATA`; failures can appear as inconsistent link-state reads or writes landing on the wrong index.
- PCIe link reporting should show correct negotiated speed, width, lane reversal, and training state after boot, suspend/resume, and link retrain.
- ASPM and power-management testing should not cause hangs, surprise link down events, unexpected width/speed downgrades, or failures entering/leaving L0s/L1/L23/BACO-like states.
- FLR/reset testing should confirm reset-done and strap-valid behavior, and should not leave functions inaccessible.
- MSI, bridge window, PM capability, virtual-channel, ACS, and multicast capability fields should enumerate consistently through PCI config-space inspection.
- AER/error-injection tests should report, mask, log, and clear expected correctable/uncorrectable/root errors without spurious fatal/nonfatal classification changes.
- Diagnostic tests for replay/sequence state, flow-control credits, lane equalization, lane error status, debug registers, and LC state machines should show fields changing in the expected bit positions.

Regression symptoms from bad constants include PCIe link retraining loops, GPU disappearance after reset or resume, interrupt delivery failures, incorrect MSI programming, DMA or completion timeouts, noisy or missing AER logs, link stuck at a lower generation or width, broken hotplug/PME state, wrong ACS isolation behavior, or per-lane equalization diagnostics attributed to the wrong lane.

## Cross-Chunk Notes

Earlier lines in `bif_5_1_sh_mask.h` define preceding BIF and PCIe field families for the same ASIC register namespace. This chunk starts mid-register with the tail of `BIF_RESET_EN`, then covers complete `D2F1` and `D2F2` PCIe/config blocks and the start of `D2F3`. Later chunks complete `D2F3` and the remaining generated BIF 5.1 register-mask definitions. The final per-file report should present this file as generated AMDGPU hardware metadata rather than algorithmic driver code.
