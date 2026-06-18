# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 90325-92667

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains 2,178 `#define` field-layout macros and 161 register/address-block comments. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the mask half of `BIFP0_PCIE_LC_CNTL7`, finishes the remaining `BIFP0` PCIe link-management, strap, L1 substate, HPGI, clock-gating, link-control, and save/restore field definitions, then enters the `// addressBlock: nbio_pcie0_bifp1_pciedir_p` block. It covers a complete `BIFP1` PCIe-direct register set and then starts `// addressBlock: nbio_pcie0_bifp2_pciedir_p`, ending partway through the `BIFP2_PCIE_RX_CNTL` mask definitions. Adjacent chunks are required for the beginning of `BIFP0_PCIE_LC_CNTL7` and the rest of `BIFP2_PCIE_RX_CNTL`/following `BIFP2` registers.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.2.0 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk describes PCIe port/link controller register layouts for BIFP0, BIFP1, and the start of BIFP2. The constants support AMDGPU code that decodes or composes NBIO PCIe-direct, link-control, flow-control, error, strap, CCIX, LTR, power-management, equalization, and link-training registers without hard-coding bit positions at call sites.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The `BIFP0` tail section covers link-management and link-controller state after the preceding chunk's `BIFP0_PCIE_LC_CNTL7` shifts. It defines masks for scheduled RX equalization evaluation, link management enablement, ESM rates and PLL initialization state, plus status and interrupt-mask style fields for speed/width updates, failed speed/width changes, power-down completion, bandwidth updates, link-power-state changes, equalization requests, partner ESM requests, immediate low-speed requests, and ESM PLL setup. `BIFP0_PCIE_LINK_MANAGEMENT_CNTL` exposes far-end width support, current link power state, link-up and port-powered-down state, clock rate, low/high bandwidth hints, bandwidth thresholds, and equalization request status.

The `BIFP0` strap and power-management registers describe hardware strap-derived policy and L1 substate programming: training sequence counts, receiver-detect bypass, compliance controls, lane reversal, auto root-complex speed negotiation disable, lane negotiation, software-controlled margining, RTM presence-detect support, E2E prefix, OBFF, LTR, CCIX enablement, ESM capability, L1.1/L1.2 overrides, CLKREQ filtering, power-on scale/value, L1.1/L1.2 powerdown, deferred L1.2 exit, auxiliary counter reference-clock behavior, and L1.2 abort/powerdown quirks.

The `BIFP0` controller extension registers cover HPGI private and public controls, HCNT descriptor fields, TXCLK performance counters, fine-grain clock-gate overrides, and `LC_CNTL8` through `LC_CNTL12`. These `LC_CNTL*` groups encode advanced link-training and power behavior: Gen3/Gen4 equalization settings, recovery-state behavior, EIEOS handling, lane deconfiguration rules, dynamic lane powerdown, refclk request handling, scheduled RXEQ evaluation, margining, local preset handling, L1/L1.1/L1.2 abort and wake controls, and save/restore fields for link state across power/reset sequences.

The `BIFP1` PCIe-direct block starts with port scratch/control fields and then defines transmit-side PCIe controls. TX macros cover unsupported-request response mode, IDO, TLP prefix handling, TC and requester ID selection, vendor-specific behavior, request-number limits, sequence/replay control, ACK latency, NOP DLLP generation, skid control, advertised and initial flow-control credits for posted, non-posted, and completion traffic, current credit-error status, FCU thresholds, and CCIX transmit attributes, target/source IDs, routing ID, stacked address base/limit, and CCIX miscellaneous error status.

The `BIFP1` receive and error groups describe lane status, posted/non-posted/completion flow-control credits for VC0 and VC1, PCIe error-control knobs, RX ignore masks for many packet/configuration/completion/PASID/prefix error classes, NAK-on-full behavior, completion timeout controls, TPH disablement, FLR timeout masking, expected sequence number, vendor-specific RX data, received credit allocation, physical and transaction error injection controls, NAK counter status, captured LTR control/status and threshold values, private AER uncorrectable mask and trigger controls, and root-complex/PASID-specific unsupported-request ignore bits in `RX_CNTL3`.

The `BIFP1` link-controller section is the largest part of the chunk. `LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_STATE0` through `LC_STATE5`, `LC_CNTL2` through `LC_CNTL12`, `LC_BW_CHANGE_CNTL`, `LC_CDR_CNTL`, `LC_LANE_CNTL`, forced coefficient registers, best equalization settings, forced EQ request coefficients, link-management status/mask/control, strap fields, L1 PM substate fields, HPGI, performance counters, fine-grain clock-gate overrides, and save/restore registers collectively describe PCIe LTSSM behavior, reset and L0/L0s/L1/L2/L3 transitions, lane-width negotiation, lane reversal, speed changes, fast training sequence counts, Gen3/Gen4 equalization presets and coefficients, bandwidth-change timing, CDR control, dynamic lane powerdown, ESM entry, clock/refclk request sequencing, and hardware-managed save/restore state.

The `BIFP2` start repeats the same PCIe-direct pattern as `BIFP1` through `BIFP2_PCIE_RX_CNTL`: scratch/port controls, TX requester/vendor/request/replay/ACK/NOP/skid controls, TX advertised/init/current credit registers, CCIX control and address-window fields, port lane status, VC0/VC1 flow-control credits, error-control fields, and the beginning of RX ignore/timeout/TPH/PASID controls. The chunk ends before the final `BIFP2_PCIE_RX_CNTL` masks for some high bits and before `BIFP2_PCIE_RX_CNTL3`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. The constants are untyped integer literals, mostly with an `L` suffix, and encode only bit geometry.

These definitions do not encode register addresses, default values, access width, read/write permissions, write-one-to-clear behavior, firmware ownership, sequencing requirements, or hardware side effects. Consumers combine them with `nbio_7_2_0_offset.h` register-address macros such as `regBIFP1_PCIE_LC_CNTL` and `regBIFP2_PCIE_RX_CNTL`, and with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT` where appropriate.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a generated NBIO 7.2.0 register address from `nbio_7_2_0_offset.h`.
2. The code reads a hardware register or prepares a write value through the SOC15/NBIO/PCIe-port access path.
3. The caller applies the generated `*_MASK` and `*_SHIFT` constants to decode status fields or compose updated control fields while preserving unrelated bits.

The field names imply several asynchronous hardware flows outside the header: PCIe link training and recovery, speed and width negotiation, lane reversal, Gen3/Gen4 equalization, scheduled RXEQ evaluation, flow-control credit accounting, LTR capture, AER/error injection, CCIX routing/window checks, ASPM/L1.1/L1.2 entry and exit, refclk/CLKREQ handshakes, powerdown/wakeup handling, and save/restore across low-power or reset transitions.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe registers. Persistence depends on the GPU reset domain, PCIe reset, link retraining, power-gating and clock-gating state, BIOS/firmware setup, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable policy bits, strap-derived capabilities, link and lane status, LTSSM diagnostics, flow-control credit counts, timeout controls, interrupt/status masks, error-injection controls, AER/private error masks and triggers, CCIX addressing and IDs, LTR capture registers, equalization coefficients and presets, and save/restore slots. Some fields are live status or sticky events, while others are controls that can affect the PCIe link immediately. The macro definitions alone do not say whether a status bit is read-only, write-one-to-clear, self-clearing, or safe for read-modify-write.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with sibling metadata. In this tree the direct companion is `nbio_7_2_0_offset.h`, which provides matching addresses and base indices for the same register names. Unlike some other NBIO generations in this mirror, there is no adjacent `nbio_7_2_0_default.h` file visible in the same directory, so reset/default validation for this exact generation must come from the hardware database or other upstream material.

The direct C include point found in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h` and uses AMDGPU register helpers to program NBIO behavior. The semantic dependencies are the PCIe specification and AMD/CCIX hardware definitions for link training, flow control, AER, LTR, TPH, PASID/prefix handling, ASPM/L1 substates, root-port style error handling, and vendor-specific link-controller registers.

The chunk's macros are most relevant to NBIO bring-up, PCIe link recovery, speed/width control, power-management policy, error handling, hardware debug, diagnostics, and platform-specific tuning rather than high-level GPU memory-management or display logic.

## Risks And Edge Cases

- The range starts and ends mid-register. Whole-file research must reconcile the preceding `BIFP0_PCIE_LC_CNTL7` shifts and the following `BIFP2_PCIE_RX_CNTL` masks before treating either register as complete.
- Generated shift/mask drift can compile cleanly while causing code to read or write the wrong hardware bit. Failures may appear as PCIe link instability, incorrect speed/width negotiation, broken L1 substates, lost interrupts/status, or masked error reporting.
- `BIFP0`, `BIFP1`, and `BIFP2` blocks are highly repetitive. Copy or generation errors can affect only one port, making failures topology-dependent.
- Some status and event bits may be sticky or write-one-to-clear at the hardware level. The presence of a mask does not imply read-modify-write is safe.
- Link-control, equalization, forced coefficient, CDR, lane powerdown, refclk, and save/restore fields are sequencing-sensitive. Writes at the wrong point in LTSSM or suspend/resume flow can hang or degrade the link.
- Error ignore, timeout disable, AER private mask, and error-injection fields can hide real PCIe failures or intentionally create bad packets. They should be constrained to documented recovery, debug, or test paths.
- CCIX, PASID, TPH, LTR, E2E prefix, and extended-format controls interact with platform capabilities and peer devices. Enabling unsupported combinations can create interoperability or isolation problems.
- Masks use C integer constants with an `L` suffix and include high-bit values. Callers should keep the established AMDGPU 32-bit register helper types to avoid signedness or truncation surprises.

## Test Signals

- Build AMDGPU with NBIO 7.2 support enabled. Compile-time coverage should catch missing or renamed generated symbols used by `nbio_v7_2.c` and related include paths.
- Run generated-header consistency checks: each complete field in the slice should have a compatible `__SHIFT`/`_MASK` pair, masks should align with shifts, and repeated `BIFP1`/`BIFP2` register families should match except for intentional port-prefix and endpoint differences.
- Cross-check register names against `nbio_7_2_0_offset.h` so every complete register family in this slice maps to an address and base index.
- On supported NBIO 7.2 hardware, compare decoded link speed, link width, lane status, strap-derived capabilities, L1 PM substate settings, flow-control credits, AER/private masks, LTR captures, and CCIX controls against PCIe config dumps and AMDGPU debug register reads.
- Exercise PCIe link retrain, speed change, width change, suspend/resume, runtime power management, GPU reset, and link recovery paths while watching `LINK_MANAGEMENT_STATUS`, `LC_STATE*`, `LC_SPEED_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_CNTL*`, and save/restore fields.
- For diagnostics or negative tests, verify error injection, NAK counters, RX ignore masks, completion timeout controls, and AER/private trigger paths report and clear the intended bits without disturbing unrelated status.
- Review any code that writes these registers for reserved-bit preservation, correct polling timeouts, and separation between production policy writes and debug-only error/equalization overrides.
