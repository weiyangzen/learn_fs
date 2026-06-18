# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 25136-27410

## Scope

This chunk is a generated AMD NBIO 7.9 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, storage definitions, or executable control flow. The constants describe bit positions and masks for NBIO RAS parity status, parity counters, RAS policy controls, scratch registers, and the first part of per-event PCIe action-control registers. The paired register-address definitions for these names are in `nbio_7_9_0_offset.h`, mostly in the `0xe88018` through `0xe88070` NBIO RAS register range.

## Purpose

The purpose of this chunk is to let NBIO 7.9 driver code build and decode 32-bit register values using symbolic field names rather than hard-coded bit arithmetic. The repeated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pattern is consumed by AMDGPU register helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` after including this file together with `nbio_7_9_0_offset.h`.

The covered registers are RAS-oriented:

- `PARITY_ERROR_STATUS_UNCORR_GRP14` tail fields and complete groups `15` and `16`: one-bit `ParityErrDetected_IdN` flags for uncorrectable parity events.
- `PARITY_ERROR_STATUS_CORR_GRP0` through `7` and `10` through `17`: one-bit corrected parity event flags.
- `PARITY_COUNTER_CORR_GRP0` through `7` and `10` through `17`: 8-bit corrected parity counters split into `ParityErrorCount0` through `ParityErrorCount3`.
- `PARITY_ERROR_STATUS_UCP_GRP0` through `7` and `10` through `12`: one-bit UCP parity event flags.
- `PARITY_COUNTER_UCP_GRP0` through `7` and `10` through `12`: 8-bit UCP counters split into four counter fields.
- `MISC_SEVERITY_CONTROL`, `MISC_RAS_CONTROL`, `RAS_SCRATCH_0`, and `RAS_SCRATCH_1`: global RAS severity, interrupt/output control, and scratch storage fields.
- `ErrEvent_ACTION_CONTROL`, generic parity action controls, and PCIe port A/early port B action controls through `PCIE0PortBExtFatal_ACTION_CONTROL` at the end of the assigned range.

## Important Definitions

The status registers use a uniform 32-bit bitmap layout. Each `ParityErrDetected_IdN` field maps directly to bit `N`, with shifts `0x0` through `0x1f` and masks from `0x00000001L` through `0x80000000L`. This chunk starts in the middle of `PARITY_ERROR_STATUS_UNCORR_GRP14`, at `Id5`, so IDs `0` through `4` and the group comment are in the previous chunk.

Corrected and UCP counter registers use four byte-wide fields:

- `ParityErrorCount0`: shift `0x0`, mask `0x000000FFL`.
- `ParityErrorCount1`: shift `0x8`, mask `0x0000FF00L`.
- `ParityErrorCount2`: shift `0x10`, mask `0x00FF0000L`.
- `ParityErrorCount3`: shift `0x18`, mask `0xFF000000L`.

`MISC_SEVERITY_CONTROL` defines two 2-bit severity selectors:

- `ErrEventErrSev`: bits `5:4`, mask `0x00000030L`.
- `PcieParityErrSev`: bits `7:6`, mask `0x000000C0L`.

`MISC_RAS_CONTROL` exposes output and interrupt policy bits:

- `PIN_NMI_SyncFlood_En` and `GNB_SB_LinkNeverDis` at bits `2` and `3`.
- Output suppressors: `InterruptOutputDis`, `LinkDisOutputDis`, and `SyncFldOutputDis` at bits `9`, `10`, and `11`.
- PCIe event routing enables for `NMI`, `SCI`, and `SMI` at bits `12`, `13`, and `14`.
- Software event routing enables for `SCI`, `SMI`, and `NMI` at bits `15`, `16`, and `17`.

The scratch registers are full-width:

- `RAS_SCRATCH_0__SCRATCH_0_MASK` is `0xFFFFFFFFL`.
- `RAS_SCRATCH_1__SCRATCH_1_MASK` is `0xFFFFFFFFL`.

The action-control registers in this chunk have a common low-bit layout:

- `APML_ERR_En`: bit `0`, mask `0x00000001L`.
- `IntrGenSel`: bits `2:1`, mask `0x00000006L`.
- `LinkDis_En`: bit `3`, mask `0x00000008L`.
- `SyncFlood_En`: bit `4`, mask `0x00000010L`.

This repeated layout applies to `ErrEvent_ACTION_CONTROL`, `ParitySerr_ACTION_CONTROL`, `ParityFatal_ACTION_CONTROL`, `ParityNonFatal_ACTION_CONTROL`, `ParityCorr_ACTION_CONTROL`, `PCIE0PortASerr_ACTION_CONTROL`, `PCIE0PortAIntFatal_ACTION_CONTROL`, `PCIE0PortAIntNonFatal_ACTION_CONTROL`, `PCIE0PortAIntCorr_ACTION_CONTROL`, `PCIE0PortAExtFatal_ACTION_CONTROL`, `PCIE0PortAExtNonFatal_ACTION_CONTROL`, `PCIE0PortAExtCorr_ACTION_CONTROL`, `PCIE0PortAParityErr_ACTION_CONTROL`, `PCIE0PortBSerr_ACTION_CONTROL`, `PCIE0PortBIntFatal_ACTION_CONTROL`, `PCIE0PortBIntNonFatal_ACTION_CONTROL`, `PCIE0PortBIntCorr_ACTION_CONTROL`, and `PCIE0PortBExtFatal_ACTION_CONTROL`.

## Control Flow

There is no direct control flow in this header segment. At runtime, control flow exists in consumers that include this header:

- `amdgpu/nbio_v7_9.c` includes this file and uses the same register helper ecosystem for NBIO setup, doorbell routing, interrupt setup, partition state, and other NBIO 7.9 hardware interactions. The RAS constants from this chunk are available there even though the visible code paths primarily use other NBIO fields.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes this file and registers NBIO RAS interrupt sources with `amdgpu_irq_add_id()`. Its IRQ set/process callbacks are dummy by design in the current implementation because the BIF ring path is disabled due to a hardware issue, so these masks are mostly latent support for RAS register programming and future diagnostics.

Any future executable path would combine the `reg...` address from `nbio_7_9_0_offset.h` with these masks through helpers such as `RREG32_SOC15()`, `WREG32_SOC15()`, `REG_GET_FIELD()`, and `REG_SET_FIELD()`.

## State and Persistence

The header itself holds no state and persists nothing. The represented hardware state is persistent only in NBIO registers while the GPU is powered and configured:

- Parity status registers are hardware-owned sticky or status bitmaps for detected events.
- Counter registers expose hardware-maintained counts for corrected and UCP parity classes.
- `MISC_RAS_CONTROL` and action-control registers are policy state that can alter interrupt, link-disable, APML error, and sync-flood behavior if written.
- `RAS_SCRATCH_0` and `RAS_SCRATCH_1` are full 32-bit scratch fields whose persistence depends on the NBIO register lifetime across reset, power gating, or firmware/driver ownership.

Because these definitions are compile-time constants, any mismatch between the header and silicon register layout becomes a runtime hardware programming error rather than a C language type error.

## Dependencies

This chunk depends on the AMDGPU register access convention:

- The paired address/base-index definitions in `nbio_7_9_0_offset.h`.
- AMDGPU SOC15 accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- Field helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which assume the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- NBIO 7.9 IP selection through the `NBIO` hardware block and base index values, where these RAS registers use base index `8` in the offset header.

The chunk mirrors equivalent RAS action-control and parity layouts in other NBIO generation headers, including NBIO 7.0, 7.2, and 7.7 variants. That repetition is useful for cross-generation review but risky if a generated copy is accepted without checking NBIO 7.9-specific address and field changes.

## Integration Points

The main integration point is inclusion by NBIO 7.9 driver code:

- `amdgpu/nbio_v7_9.c` includes the header alongside `nbio_7_9_0_offset.h`; it uses many neighboring NBIO fields for register programming. The RAS fields in this chunk are therefore in the same namespace and available for NBIO 7.9 runtime programming.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes this header and the NBIO IRQ source IDs. It wires RAS controller and err-event ATHUB interrupts into the AMDGPU IRQ layer, even though the callbacks are currently inert.
- The register offsets in `nbio_7_9_0_offset.h` align this chunk with concrete addresses from `regPARITY_ERROR_STATUS_UNCORR_GRP14` at `0xe88018` through `regPCIE0PortBExtFatal_ACTION_CONTROL` at `0xe8806e`, plus adjacent registers continuing after the chunk.

The status and counter definitions are likely intended for RAS collection, error reporting, and clear-on-write flows. The action-control definitions integrate with platform-level error response policy, including APML signaling, generated interrupt selection, link disable, and sync flood behavior.

## Risks

- The assigned range begins mid-register for `PARITY_ERROR_STATUS_UNCORR_GRP14`; any chunk-level interpretation of that group must merge with the previous chunk to recover IDs `0` through `4` and the group boundary.
- The status/counter groups skip numbers `8` and `9` in several families. This appears intentional because the paired offset header has corresponding address gaps, but generated-table consumers must not assume dense group numbering.
- Since these are untyped macros, bad masks, shifted field widths, or address/header mismatches compile successfully and can silently corrupt hardware programming.
- Action-control fields can affect severe platform behavior. Incorrect writes to `LinkDis_En`, `SyncFlood_En`, or interrupt routing bits could escalate recoverable parity events into link disable, sync flood, or unwanted platform interrupts.
- `RAS_SCRATCH_0/1` are full-width fields with no semantic typing here; firmware/driver ownership assumptions need external documentation or cross-file evidence before use.
- Current NBIO 7.9 RAS manager interrupt processing is deliberately dummy, so compile-time presence of these masks does not prove that all represented RAS events are surfaced to Linux error reporting today.

## Test Signals

Useful validation signals are mostly compile-time and hardware/driver integration checks:

- Build AMDGPU code that includes `nbio_7_9_0_sh_mask.h`; failures in `REG_SET_FIELD`/`REG_GET_FIELD` use sites would catch naming drift for referenced fields.
- Compare this chunk against generated hardware register metadata or neighboring NBIO generation headers to detect accidental mask/shift drift.
- Verify each field mask corresponds to its shift and width: 32 one-bit status masks, four 8-bit counter masks, two 2-bit severity fields, and the common low-bit action-control layout.
- On NBIO 7.9 hardware or emulation, read the paired offsets from `nbio_7_9_0_offset.h` and confirm that status/counter/action-control fields respond according to the documented bit positions.
- RAS testing should include corrected, uncorrectable, and UCP parity injection where available, then confirm status bitmaps/counters and interrupt/action policy behavior.
- Because `amdgpu_ras_nbio_v7_9.c` currently registers dummy IRQ processing paths, tests should distinguish raw hardware register updates from Linux IRQ/error-report delivery.

## Chunk Boundary Notes

The previous chunk owns the start of `PARITY_ERROR_STATUS_UNCORR_GRP14`. The next chunk continues after `PCIE0PortBExtFatal_ACTION_CONTROL` into the remaining port B and later action-control register definitions. A final per-file merge should connect those boundaries before drawing whole-file conclusions about all NBIO 7.9 RAS masks.
