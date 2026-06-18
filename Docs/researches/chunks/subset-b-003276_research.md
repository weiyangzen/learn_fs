# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 41635-44042

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains preprocessor constants only: no functions, structs, enums, executable statements, locks, allocations, or software-owned storage. The assigned line range covers 2,408 source lines with 2,154 `#define` macros over 215 register comment groups. Of those macros, 1,078 are field `__SHIFT` values and 1,076 are field `_MASK` values. The count is not balanced because the range starts with the last mask for `RCC_DEV2_EPF2_STRAP13`, then defines `RCC_DEV2_EPF2_STRAP14`, and ends after the first three `SMN_MST_CNTL1` shift definitions before that register's masks appear in the next chunk.

The chunk's main coverage is RCC PCIe port-decode field geometry for device 0, device 1, and device 2; endpoint and downstream-port field geometry for those devices; and the NBIF/BIF miscellaneous register block from `NBIF_STRAP_BIOS_CNTL` through the beginning of `SMN_MST_CNTL1`.

## Purpose

`nbio_7_7_0_sh_mask.h` is the field-layout half of AMD's generated NBIO 7.7.0 register interface. It gives C code stable macro names for bit positions and masks so register read/modify/write code can avoid hard-coded constants. The sibling `nbio_7_7_0_offset.h` supplies the register addresses and base indices; this file supplies the geometry used by helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

This chunk describes hardware state for:

- RCC root-complex/device controls for devices 0-2, including vendor-defined-message support, power-management inhibit bits, error-log policy, link-down entry/exit bits, common L1/LTR policy, requester-ID restore, link margining parameters, and arbitration priority.
- RCC endpoint PCIe controls for devices 0-2, including scratch registers, unsupported-request handling, interrupt enables/status, hidden-register config decode enables, LTR transmit controls, DPA capability/state/power-allocation fields, PME service timing, TPH disable bits, requester-ID fields, AER/error reporting controls, RX error-ignore policy, and link-speed capability straps up to Gen5.
- RCC downstream and downstream-path controls for devices 0-2, including hardware write-lock, downstream UR/LTR handling, extended-tag overrides, FLR extension mode, downstream AER completion-timeout policy, hidden config decode enables, function-enable/MSI straps, downstream link-speed straps, link-bandwidth notifications, multifunction straps, and LTR message capture.
- NBIF/BIF miscellaneous controls, including BIOS strap enable, scratch, interrupt line polarity/enable, virtual-channel outstanding allocation, BIFC policy controls, BME and RCCBIH error logs, LC timing, DMA transaction attribute overrides for dev0/dev1/dev2 functions, block-level bypass controls, dummy BME response state, arbitration and GSI/SDP controls, PASID check/status, ATHUB activity, MMIO/DMA performance counters, register-interface error behavior, NBIF power-gating controls, host outstanding limits, and SMN zero-byte read/write enable fields.

Although this repository path is under a `ceph-client` source mirror, the file is AMDGPU ASIC register metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The chunk begins at the end of `RCC_DEV2_EPF2_STRAP13` with `STRAP_CLASS_CODE_BASE_DEV2_F2_MASK`, then defines `RCC_DEV2_EPF2_STRAP14__STRAP_VENDOR_ID_DEV2_F2`. This is the tail of the device-2 endpoint-function strap coverage from the previous chunk.

The `RCC_DEV*_RCC_*` groups repeat for dev0, dev1, and dev2. They expose `RCC_VDM_SUPPORT` bits for MCTP/AMPTP/other vendor-defined messages and routing checks; `RCC_BUS_CNTL` bits for PMI IO/memory/bus-master disables, downstream/primary completion-abort and unsupported-request handling, root error logging, poisoned completion logging, and privileged max payload/read-request-size fields; `RCC_FEATURES_CONTROL_MISC` bits for PASID/ATS/Page Request/Invalid Completion UR handling, MSI/MSI-X pending-bit clearing policy, BME checks, ECRC error policy, and poisoned-chain checking; and link, LTR, requester-ID, MH arbitration, and PCIe margining parameter fields.

The `RCC_EP_DEV*_EP_PCIE_*` endpoint groups repeat for dev0, dev1, and dev2. Important controls include UR-report disable, malformed atomic behavior, LTR UR ignore, correctable/nonfatal/fatal/user/misc/power-state interrupt enable and status bits, invalid-PASID UR ignore, hidden-register config decode enables for Gen2 through Gen5, transmit LTR short/long values and requirements, DPA transition-latency and power-allocation fields, PME timer, TX snoop/relaxed-ordering overrides, per-function TPH disable fields, requester-ID function/device/bus packing, AER header-log timeout and per-function timer-expired bits, poisoned-advisory nonfatal strap, RX ignore controls for max payload, traffic class, completion timeout, short/max prefix, invalid PASID, no-PASID UR, TPH disable, and link-speed straps for Gen2 through Gen5.

The `RCC_DWN_DEV*_DN_PCIE_*` groups describe downstream-facing control for each device: reserved/scratch dwords, hardware-init write lock, downstream UR-report disable, LTR UR ignore, extended-tag enable override, FLR extend mode, immediate PMI disable, downstream AER completion-timeout relaxed-ordering disable, hidden-register decode enables, function zero enable/multicast/MSI multi-cap straps, clock PM and 64-bit master-address straps, and master completion-timeout enable.

The `RCC_DWNP_DEV*_PCIE_*` groups describe downstream-path controls: error-reporting disable, AER header-log timeout and timer-expired status, immediate error-message sending, correctable/nonfatal/fatal received clear bits, downstream RX ignore policy, completion-timeout and FLR-timeout disable bits, link-speed straps, data-link/link-bandwidth notification disables, multifunction straps, and a full-width LTR message information register from the endpoint.

The `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` groups are dense BIFC policy registers. They cover virtual-wire unit-id checks, active vlink L0, DMA VC4 non-DVM status, DMA chain break behavior in root-complex mode, host/GSI arbitration locking, GSI split-read stall behavior, preceding-write suppression, DMA atomic checks, SR-IOV VF-as-PF forcing, DMA address phase handling, RCC/GMI traffic forcing, host flush behavior, BME-drop behavior, SDP read response error forcing, unsupported-command sticky status, DMA request interrupt-mask modes, VC7 IO config disable, second-request disable, D-state bypass, PME turnoff mode, SWUS selection, per-traffic-class TPH request mask, read-request size/mask controls, direct mapping controls, posted counter threshold, credit suppression, and completion-buffer CAM disable bits.

The BME/error log families include `BIFC_BME_ERR_LOG_LB`, `BIFC_RCCBIH_BME_ERR_LOG0`, and `BIFC_RCCBIH_BME_ERR_LOG1`. They pack per-device/per-function lower-bound or BME error indicators and write/clear controls. These fields are diagnostic and recovery-oriented and can be hardware-updated.

The `BIFC_DMA_ATTR_OVERRIDE_DEV{0,1,2}_F*_F*` families pack two functions per register. Each function has two-bit fields for posted/non-posted ID-based ordering override, relaxed-ordering override, snoop/no-snoop override, and block-level selection for IDO and non-IDO traffic. The chunk covers dev0 F0-F7, dev1 F0-F7, and dev2 F0-F7. `BIFC_DMA_ATTR_CNTL2_DEV0/1/2` then adds per-function `BLKLVL_BYPASS_PCIE_IDO_CONTROL` bits.

The later BIFC/NBIF groups cover `BME_DUMMY_CNTL_0/1` dummy-response status and completion policy, `BIFC_THT_CNTL` DMA virtual-channel thresholds, `BIFC_HSTARB_CNTL` host arbitration mode, `BIFC_GSI_CNTL` SDP arbitration, GSI completion response and timeout policy, `BIFC_PCIEFUNC_CNTL`, PASID check disable/status, SDP disconnect hysteresis and disconnect disable policy, ATHUB activity status, MMIO/DMA performance-counter enable/reset/selector and value fields, register-interface error-set behavior, NBIF power-gating master/slave/misc controls, host outstanding limits, and SMN master zero-byte write/read enables for dev0/dev1/dev2 PF0-PF7.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public surface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit number for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit field mask.
- Full-width fields such as scratch, reserved, LTR message info, and performance-counter value registers use `0xFFFFFFFFL` masks.
- Narrow packed fields use masks such as `0x00000007L`, `0x00000C00L`, or `0xF0000000L` and rely on the corresponding shift macro for extraction or insertion.

Consumers combine these macros with register addresses from `nbio_7_7_0_offset.h` and AMDGPU helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and related SOC15/NBIO access wrappers. The macros do not encode access permissions, reset values, write-one-to-clear semantics, reserved-bit policy, locking, or sequencing requirements.

## Control Flow

This header has no local runtime control flow. Runtime flow is imposed by AMDGPU code:

1. ASIC-specific code includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. Code reads an NBIO/RCC/BIF register through a SOC15 or indexed access helper.
3. Code extracts or updates a field using this header's shift and mask macros, usually through `REG_GET_FIELD()` or `REG_SET_FIELD()`.
4. Code writes the register back if the operation is a control update, or uses the extracted value for revision, capability, status, error, power, interrupt, or performance decisions.

In this repository, `amdgpu/nbio_v7_7.c` includes the NBIO 7.7 shift/mask header and uses nearby RCC/doorbell/strap field macros from the same generated header family. A quick source search did not find direct `.c` uses of the exact field names in this chunk, so most of this slice is presently a hardware-description surface for future code, debug tooling, register dumps, or out-of-tree/vendor paths rather than directly referenced runtime logic in the visible tree.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names MMIO/config-backed hardware state in NBIO 7.7.

State represented here includes firmware/strap identity fields, PCIe endpoint and downstream link policy, LTR and DPA power-management controls, interrupt enable/status bits, AER/error-log state, requester IDs, traffic ordering and snoop attributes, BME and dummy-response logs, PASID check state, ATHUB activity, SDP/GSI arbitration and disconnect policy, NBIF power-gating configuration, performance counter control and observed counter values, SMN zero-byte request handling, and partial `SMN_MST_CNTL1` error-response data policy.

Persistence is hardware-defined. Strap-derived fields may be initialized by fuses, firmware, or SBIOS and are not ordinary persistent software state. Error logs, interrupt status bits, performance counters, activity bits, and timeout/timer-expired bits can change asynchronously as hardware runs and may have clear-on-write or latch semantics documented outside this header. Power-gating and link-control fields can be reset or reprogrammed across GPU reset, PCIe FLR, BACO, suspend/resume, runtime power transitions, firmware handoff, or virtualization reset flows.

## Dependencies And Integration Points

The direct sibling dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which supplies the matching register addresses and base indices. The visible NBIO 7.7 implementation is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`; it includes both generated headers and exposes the `nbio_v7_7_funcs` implementation used by common AMDGPU NBIO code.

Integration points for this chunk's fields include:

- PCIe/RCC initialization and debug paths that may need endpoint, downstream, link-speed, AER, LTR, DPA, requester-ID, and margining fields.
- Power-management paths that interact with PMI disable controls, LTR timers, DPA substates, PME service timing, link-down handling, NBIF power-gating controls, and GSI/SDP disconnect hysteresis.
- Error handling and recovery paths for AER timer-expired bits, BME error logs, dummy-response controls, completion-timeout behavior, invalid PASID handling, unsupported-request handling, and register-interface error-set behavior.
- Virtualization/SR-IOV and PASID/ATS paths that care about per-function field packing, PASID check disable/status, VF-as-PF forcing, requester IDs, traffic ordering, and SMN zero-byte enables.
- Performance and diagnostics paths that may use `BIFC_PERF_CNTL_0/1` and the MMIO/DMA counter value registers.

The macro names are generated and strongly tied to the ASIC register database. Similar families appear in other NBIO/NBIF generations, but the matching generation's offset and shift/mask headers must be used together because field coverage and masks differ.

## Risks And Edge Cases

- Field-geometry drift is silent at compile time if macro names remain stable. A wrong shift or mask can preserve the wrong bits, clear unrelated hardware state, or misreport status while code still builds.
- The chunk begins and ends mid-register-family. `RCC_DEV2_EPF2_STRAP13` and `SMN_MST_CNTL1` are incomplete here; adjacent chunks are required before making whole-register claims.
- The repeated dev0/dev1/dev2 and function-pair layouts are copy/generation sensitive. Applying a dev0 or F0/F1 mask to another device/function can silently alter unrelated PF fields.
- Several registers contain live status and clear bits. Read/modify/write updates must preserve hardware-updated state and avoid accidentally clearing BME logs, AER timer bits, interrupt statuses, PASID status, activity bits, or performance counter resets.
- PCIe link, LTR, DPA, and power-gating fields are sequencing-sensitive. Writes during link training, runtime power transitions, suspend/resume, or BACO/FLR recovery can create intermittent link or resume failures.
- Error-reporting disable and RX-ignore fields can hide real protocol problems. They should be treated as policy or workaround controls rather than generic error suppression.
- DMA attribute overrides, relaxed-ordering/no-snoop controls, PASID checks, and SMN zero-byte enables affect memory ordering, isolation, and translation behavior. Incorrect values can cause stale data, ordering violations, security/isolation issues, or guest/PF/VF-specific failures.
- Performance counter controls include enable, reset, and selector fields. Concurrent debug/perf users need coordination to avoid resetting or retargeting counters unexpectedly.
- Some masks use small literals such as `0xFFL` or `0x001FL`; callers relying on 32-bit unsigned arithmetic should still treat these as register-field constants, not typed values with explicit width metadata.

## Test Signals

Useful validation combines generated-header checks with hardware and driver tests:

- Build AMDGPU with NBIO 7.7 support enabled. The include in `amdgpu/nbio_v7_7.c` should catch missing or renamed macros that are directly used by visible code.
- Mechanically compare this chunk against AMD's authoritative NBIO 7.7.0 register database and the matching `nbio_7_7_0_offset.h`; every shift/mask pair should map to a valid register address and expected field width.
- Check that each complete register group in the chunk has expected shift/mask pairing and that the known partial boundaries are limited to `RCC_DEV2_EPF2_STRAP13` at the start and `SMN_MST_CNTL1` at the end.
- Exercise GPU boot, reset, suspend/resume, runtime power management, BACO, PCIe FLR, and link retraining on NBIO 7.7 hardware while watching for link-speed, LTR/DPA, PME, and power-gating regressions.
- Validate AER/error paths with PCIe error injection or diagnostics where available; inspect BME logs, AER timer-expired bits, completion-timeout policy, and interrupt status behavior.
- Test PASID/ATS/KFD and SR-IOV workloads because this chunk contains PASID check controls, requester-ID fields, per-function DMA attributes, and per-PF SMN zero-byte enables.
- Run CPU/GPU shared-memory, DMA, SDMA, and graphics/compute workloads sensitive to relaxed ordering, no-snoop, IDO, and block-level behavior.
- Use debug/perf tooling that reads MMIO and DMA performance counters, verifying enable/reset/selector fields and 32-bit count registers behave as expected.

## Cross-Chunk Notes

The previous chunk owns most of the endpoint-function strap context before the tail `RCC_DEV2_EPF2_STRAP13` mask seen here. The next chunk owns the remainder of `SMN_MST_CNTL1` and later NBIO field definitions. The final per-file report should merge all 64 chunks for this generated header before summarizing complete NBIO 7.7 shift/mask coverage.
