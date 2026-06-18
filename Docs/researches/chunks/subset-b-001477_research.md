# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h lines 7581-8127

## Purpose

This chunk is the closing register-field mask/shift section for the AMD BIF 3.0 generated header. It defines C preprocessor constants that describe bit layouts for PCIe/BIF registers rather than executable code. The paired address header is `bif_3_0_d.h`; this file supplies the per-field `*_MASK` and `*__SHIFT` values used with those register addresses.

The covered range starts in the middle of the PCIe PRBS error-counter definitions and then covers the tail of the BIF register map:

- PCIe PRBS checker/counter fields, receive L0s FTS detection, and PCIE/PCIEP scratch or reserved registers.
- PCIe link-control and function strap fields, including function enablement and advertised PCIe capabilities for functions F0-F2.
- PCIe receive-side controls, error/unsupported-request ignore controls, completion timeout controls, receive credits, sequence numbers, NAK counters, and last-TLP capture registers.
- PCIe transmit-side controls, requester ID, sequence/replay status, advertised and initialized flow-control credits, and credit error/status fields.
- WPR reset policy bits, peer frame-buffer offset windows, peer register ranges, slave hang/credit controls, SMBus pad controls, and the BACO SMBus dummy register.

The final `#endif` closes the `BIF_3_0_SH_MASK_H` include guard. The chunk therefore completes the generated BIF 3.0 mask header and should be reconciled with preceding chunks for a full per-file view.

## Important APIs, Types, And Functions

There are no functions, structs, or runtime APIs in this chunk. The important interface is the set of macro names and their stable generated naming convention:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask for a field.
- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for extracting or inserting that field.
- Full-width registers use `0xffffffffL` masks and shift `0`, such as PRBS error counters, `PCIE_RX_LAST_TLP*`, `PCIE_TX_LAST_TLP*`, scratch registers, and `SMBUS_BACO_DUMMY`.
- Multi-bit fields preserve their hardware width, for example `PCIE_RX_CNTL__RX_RCB_CPL_TIMEOUT_MASK`, `PCIE_TX_REPLAY__TX_REPLAY_TIMER_MASK`, `PCIE_STRAP_MISC__STRAP_MAX_PASID_WIDTH_MASK`, and peer range start/end address fields.

The macros in this chunk are meaningful only alongside BIF 3.0 register address macros from `bif_3_0_d.h`, such as `ixPCIE_RX_CNTL`, `ixPCIE_TX_CNTL`, `ixPCIE_PRBS_MISC`, `ixPCIE_STRAP_F0`, `mmPEER0_FB_OFFSET_LO`, `mmSLAVE_HANG_ERROR`, `mmSMBCLK_PAD_CNTL`, and `mmSMBUS_BACO_DUMMY`.

Key groups in this range:

- PRBS diagnostics: `PCIE_PRBS_ERRCNT_3` through `PCIE_PRBS_ERRCNT_9`, `PCIE_PRBS_FREERUN`, `PCIE_PRBS_HI_BITCNT`, `PCIE_PRBS_LO_BITCNT`, `PCIE_PRBS_MISC`, `PCIE_PRBS_STATUS1`, `PCIE_PRBS_STATUS2`, and `PCIE_PRBS_USER_PATTERN`.
- PCIe port and strap configuration: `PCIE_P_RCV_L0S_FTS_DET`, `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, `PCIE_STRAP_F0` through `PCIE_STRAP_F7`, `PCIE_STRAP_I2C_BD`, `PCIE_STRAP_MISC`, `PCIE_STRAP_MISC2`, and `PCIE_STRAP_PI`.
- Receive path: `PCIE_RX_CNTL`, `PCIE_RX_CNTL2`, `PCIE_RX_CNTL3`, `PCIE_RX_CREDITS_ALLOCATED_*`, `PCIE_RX_EXPECTED_SEQNUM`, last-TLP capture, NAK counters, and `PCIE_RX_VENDOR_SPECIFIC`.
- Transmit path: `PCIE_TX_ACK_LATENCY_LIMIT`, `PCIE_TX_CNTL`, `PCIE_TX_CREDITS_*`, `PCIE_TX_REPLAY`, `PCIE_TX_REQUESTER_ID`, `PCIE_TX_REQUEST_NUM_CNTL`, `PCIE_TX_SEQ`, and `PCIE_TX_VENDOR_SPECIFIC`.
- BIF fabric/support registers: `PCIE_WPR_CNTL`, `PEER[0-3]_FB_OFFSET_{HI,LO}`, `PEER_REG_RANGE[0-1]`, `SLAVE_HANG_ERROR`, `SLAVE_HANG_PROTECTION_CNTL`, `SLAVE_REQ_CREDIT_CNTL`, `SMBCLK_PAD_CNTL`, `SMBDAT_PAD_CNTL`, and `SMBUS_BACO_DUMMY`.

## Control Flow

This header has no control flow. All behavior comes from compile-time macro substitution in source files that include it. Callers typically read a 32-bit hardware register, mask and shift a field out, or construct a value by shifting an input and applying the mask before writing the register through AMDGPU register-access helpers.

The order of definitions follows the generated register-map order. The assigned range begins with `PCIE_PRBS_ERRCNT_3__PRBS_ERRCNT_3__SHIFT`; the matching `PCIE_PRBS_ERRCNT_3__PRBS_ERRCNT_3_MASK` appears immediately before this chunk. That line-boundary split is important for merge reconciliation because the `ERRCNT_3` field is incomplete if reviewed from this chunk alone.

## State And Persistence Behavior

The header itself stores no software state and performs no hardware access. The persistent state affected by users of these macros is the BIF/PCIe hardware register state on Sea Islands-era AMD GPUs:

- Strap fields describe or override link/function capability exposure, including ACS, AER, MSI, VC, BAR, DPA, ATS, page request, PASID, power management, link configuration, lane reversal, and FLR support.
- RX/TX control fields can alter how the PCIe block handles malformed TLPs, unsupported requests, completion timeouts, NAK generation, relaxed ordering/no-snoop behavior, flow-control updates, replay timers, and requester IDs.
- Credit fields expose or configure posted, non-posted, and completion header/data credits, both allocated on RX and advertised/initialized/status on TX.
- Peer FB offsets and peer register ranges define windows used for peer access routing or aperture translation.
- Slave hang/error and request-credit fields persistently tune BIF access crediting and hang detection until reset or later driver/firmware reprogramming.
- SMBus pad-control fields persist pad mode, selection, slew, Schmitt trigger, wake, and drive/control bits for the SMB clock/data pins.

Because these are raw bit definitions, there is no locking, allocation, reference counting, or validation here. Ordering, concurrency, and register side effects are controlled entirely by the driver code that uses the macros.

## Dependencies And Integration Points

This file depends on the AMD ASIC register-generation contract: every mask and shift must match the BIF 3.0 hardware specification and the address macros in `bif_3_0_d.h`. The suffixes `ix` and `mm` in the paired address header distinguish indirect-indexed PCIe register spaces from direct MMIO registers; these mask definitions are shared by both access styles according to the register named in the macro.

Direct include points in this source tree include AMDGPU Sea Islands components such as `amdgpu/si.c`, `amdgpu/gfx_v6_0.c`, `amdgpu/gmc_v6_0.c`, `amdgpu/dce_v6_0.c`, and `pm/legacy-dpm/si_dpm.c`. Those files can combine BIF 3.0 address constants, these masks, and AMDGPU register helpers to program GPU initialization, power management, PCIe link behavior, memory controller/BIF aperture setup, display bring-up, and diagnostics.

The chunk also has cross-generation relevance. Similar fields appear in later `bif_*`, `nbif_*`, and `nbio_*` mask headers, sometimes with changed field names or extra bits. Code that is generic across ASIC generations must include the correct generation header and avoid assuming BIF 3.0 masks match newer NBIF/NBIO layouts.

## Risks And Edge Cases

The primary risk is silent register-field drift. A wrong mask or shift compiles cleanly but can program the wrong hardware bit, misread status, or leave a field unchanged. This is especially risky for control fields that suppress PCIe errors or timeouts, such as `RX_IGNORE_*`, `RX_PCIE_CPL_TIMEOUT_DIS`, `RX_RCB_CPL_TIMEOUT`, `TX_REPLAY_TIMER`, and `TX_FC_UPDATE_TIMEOUT_DIS`.

Strap fields are capability-sensitive. Incorrect function strap bits can advertise unsupported capabilities, hide required capabilities, or change function enumeration behavior for MSI, AER, ACS, ATS, PASID, page-request, BAR, power-management, virtual-channel, lane, and FLR support. Since many strap values are latched or firmware-influenced, driver writes may be constrained by timing or platform policy.

Several counters and capture registers are full-width fields. Code should not shift these values unnecessarily or treat them as signed quantities. Conversely, narrow fields such as peer offsets, credit counts, requester ID bus/device/function fields, and SMBus pad controls require proper mask/shift handling to avoid clobbering neighboring bits.

The chunk includes reserved-register masks (`PCIEP_RESERVED`, `PCIE_RESERVED`, and reserved `PCIE_STRAP_F3` through `F7`). These should not be interpreted as safe writable feature fields; full-width masks on reserved registers are generated descriptions, not permission to write arbitrary values.

Peer offset and range registers can affect address-routing behavior. Programming `PEER*_FB_OFFSET_LO__PEER*_FB_EN`, high/low offset fields, or `PEER_REG_RANGE*` with stale values can expose the wrong aperture or break peer access paths.

The first line of this chunk is a continuation of the previous PRBS counter field. Any automated extraction or review process that reasons about complete fields must merge adjacent chunks or tolerate a split mask/shift pair at the line boundary.

## Test Signals

Useful validation is mostly compile-time, register-dump, and hardware-behavior oriented:

- Build coverage for the Sea Islands AMDGPU paths that include `bif_3_0_sh_mask.h`; missing or renamed macros should fail compilation in `si.c`, `gfx_v6_0.c`, `gmc_v6_0.c`, `dce_v6_0.c`, or `si_dpm.c`.
- Static register-map checks can compare every `REGISTER__FIELD_MASK`/`__SHIFT` pair against the generated BIF 3.0 source data and against paired addresses in `bif_3_0_d.h`.
- PCIe link bring-up and resume should keep expected negotiated width/speed, requester ID, completion behavior, replay/NAK behavior, and flow-control credit status after initialization.
- PCIe error-handling tests should observe expected AER/UR/completion-timeout behavior when RX ignore bits are enabled or disabled by the driver or firmware policy.
- PRBS diagnostics should show sane lock, bit-count, free-run, user-pattern, and per-lane error-counter behavior when exercising PCIe PHY test modes.
- Peer aperture tests should verify that `PEER[0-3]_FB_OFFSET_{HI,LO}` and `PEER_REG_RANGE[0-1]` route only the intended windows and that disabling `PEER*_FB_EN` blocks the corresponding path.
- SMBus/BACO tests should confirm that `SMBCLK_PAD_CNTL`, `SMBDAT_PAD_CNTL`, and `SMBUS_BACO_DUMMY` accesses do not regress BACO or board-management sideband behavior.

## Cross-Chunk Notes

The final per-file research should merge this tail with earlier chunks that define the rest of `bif_3_0_sh_mask.h`, including BACO, BIF bus numbering, BIOS scratch, config aperture, interrupt, performance counter, PCIe PHY/link, and the beginning of the PRBS register set. This chunk supplies the closing PCIe RX/TX, strap, peer-window, hang-protection, SMBus pad, and final include-guard context.
