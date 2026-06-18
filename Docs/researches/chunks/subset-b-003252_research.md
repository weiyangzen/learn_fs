# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 14646-17059

## Purpose

This chunk is an auto-generated AMD NBIO 7.7 register-offset slice for PCIe/NBIO hardware blocks. It contains no executable C logic. Its purpose is to publish preprocessor constants that map symbolic register names to NBIO 7.7 register offsets, plus the matching `*_BASE_IDX` values used by SOC15 register-access helpers.

The selected line range starts in the middle of the `nbio_pcie0_bifp3_pciedir_p` block, covers the complete `nbio_pcie0_bifp4_pciedir_p` block, covers the global `nbio_pcie0_pciedir` block, covers complete `nbio_pcie1_bifplr0_cfgdecp`, `bifplr1`, and `bifplr2` PCIe link-root/config-decode blocks, and ends at the beginning of `nbio_pcie1_bifplr3_cfgdecp`.

## Public Surface In This Chunk

The public surface is 2,390 `#define` macros: 1,195 register offset macros and 1,195 matching `*_BASE_IDX` macros. Every `*_BASE_IDX` value in this range is `5`, so consumers rely on these constants as part of the SOC15 address-space tuple rather than as independently computed values.

Macro families in this range are:

- `regBIFP3_0_*`: tail of PCIe port 3 directory-port registers, beginning at `PCIE_TX_REQUESTER_ID` and covering lane status, receive controls, flow-control credits, error injection, link-control state, link training/speed/width, straps, L1 PM substates, equalization controls, save/restore registers, transmit sequence/replay, and advertised/initialized flow-control credits.
- `regBIFP4_0_*`: complete PCIe port 4 directory-port register set with the same structure as the port 3 tail, starting at `PCIEP_RESERVED`, `PCIEP_SCRATCH`, and `PCIEP_PORT_CNTL`.
- `regBIF0_*`: global PCIe/NBIO directory registers at base `0x11180000`, including PCIe control/status/debug, common AER mask, last received TLP logs, link power-management controls, physical-layer and SDP controls, clock-request mapping, performance counters, SW reset request/status/masking, LC/HP/CPM controls, straps, SMN/SMU fenced registers, master request/error controls, and HIP registers.
- `regBIFPLR0_1_*`, `regBIFPLR1_1_*`, and `regBIFPLR2_1_*`: complete PCIe root-port/link-root configuration decode maps for PCIe1 blocks at bases `0x11200000`, `0x11201000`, and `0x11202000`.
- `regBIFPLR3_1_*`: beginning of the next PCIe1 link-root config-decode map at base `0x11203000`, from vendor/device ID through `ROOT_CNTL`.

There are no functions, structs, enums, inline helpers, or data objects here. The API contract is the exact macro spelling and numeric value, synchronized with the companion `nbio_7_7_0_sh_mask.h` field definitions and AMD's generated NBIO 7.7 register database.

## Register Coverage

The `BIFP3_0` and `BIFP4_0` directory-port portions describe per-port PCIe datapath registers. These cover data-link transmit/receive state (`PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, `PCIE_RX_EXPECTED_SEQNUM`), credit allocation/advertisement (`RX_CREDITS_ALLOCATED_*`, `TX_CREDITS_*`, `PCIE_FC_*`), error control and injection (`PCIE_ERR_CNTL`, `PCIEP_ERROR_INJECT_*`, `PCIEP_NAK_COUNTER`), link-controller state and policy (`PCIE_LC_CNTL*`, `PCIE_LC_STATE*`, `PCIE_LC_SPEED_CNTL*`, `PCIE_LC_LINK_WIDTH_CNTL`), link equalization (`PCIE_LC_FORCE_COEFF*`, `PCIE_LC_BEST_EQ_SETTINGS`, `PCIE_LC_FORCE_EQ_REQ_COEFF*`), and low-power link behavior (`PCIE_LC_L1_PM_SUBSTATE*`, clock-gate override, save/restore registers).

The `BIF0` global block describes the shared PCIe directory and NBIO control surface. It includes broad PCIe control and diagnostics, AER policy, RX/TX logging, power-management controls, physical-port status, I2C sideband access registers, SDP slave attributes, performance counter controls for multiple TX clocks, software-reset controls and status, register-write activity tracking, link-controller/hotplug/clock-power-management knobs, strap shadow registers, master request sizing/error controls, and SMU/SMN integration registers.

Each complete `BIFPLR*_1` block repeats a PCI/PCIe configuration-space layout for a link-root/root-port function:

- Conventional PCI bridge header: vendor/device ID, command/status, revision/class bytes, cache-line/latency/header/BIST, secondary/subordinate bus information, I/O/memory/prefetchable windows, ROM BAR, interrupt line/pin, and bridge controls.
- Capability structures: vendor capability, power-management capability/status, PCIe capability, device/link/slot/root control and status, second-generation device/link/slot capability registers, MSI, SSID, MSI map, and vendor-specific enhanced capability.
- Advanced PCIe features: virtual-channel controls, AER status/mask/severity/logging, ACS controls, latency tolerance reporting, L1 PM substates, second vendor-specific capability payload, DPC capability/control/status, resizable BAR, and local error status/masking/severity/injection.
- High-speed link tuning: 16 GT/s link and lane equalization registers, lane margining controls/status for lanes 0 through 15, CCIX/ESM capability and control registers, 20 GT/s and 25 GT/s ESM lane equalization groups, and 32 GT/s link capability/control/status.

The `BIFPLR3_1` portion is intentionally partial in this chunk. It only covers the start of the conventional PCI/PCIe header through `ROOT_CNTL`; `ROOT_CAP`, `ROOT_STATUS`, MSI, AER, equalization, margining, CCIX/ESM, and 32 GT/s registers for this block continue after line 17059.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_7_0_offset.h`, usually alongside `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code selects a register macro, often through `SOC15_REG_OFFSET(NBIO, instance, reg...)` or through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.
3. The numeric offset and base index are resolved by the compiler into the register-access helper call.
4. Actual reads, writes, polling, reset observation, and bit manipulation occur in AMDGPU/NBIO code outside this header.

The header stores no software state and persists nothing. Persistent or sticky behavior belongs to the hardware registers named here. Some registers are writable policy/configuration registers that remain effective until reset, power transition, firmware reinitialization, link reset, function reset, or driver reprogramming. Others are hardware-updated status, error-log, performance-counter, strap-shadow, or write-one-to-clear style registers whose access rules are not encoded in this offset header.

## Dependencies And Integration Points

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That implementation uses the generated register names with SOC15 helpers to initialize NBIO state, configure memory-controller access, doorbell apertures and ranges, interrupt handling, HDP flush offsets, PCIe index/data offsets, clock-gating policy, and PCIe master control. For this specific chunk, `nbio_v7_7_init_registers()` reads and conditionally writes `regBIF0_PCIE_MST_CTRL_3` using companion shift/mask fields.

The semantic dependencies are AMD's NBIO 7.7 register database, the SOC15 register addressing model, the PCI and PCI Express configuration-space specifications, root-port/link training semantics, PCIe AER, ACS, DPC, LTR, L1 PM substates, lane margining, high-speed equalization, CCIX/ESM capability layout, and AMD firmware/SMU ownership rules for selected NBIO and PCIe registers.

The companion `nbio_7_7_0_sh_mask.h` file is required when consumers need bitfield extraction or insertion. This offset header only identifies register addresses; it does not describe bit positions, masks, reset values, access widths, access permissions, side effects, or firmware arbitration.

## Risks And Maintenance Notes

- This is generated hardware ABI. Renaming a macro, changing an offset, or mixing it with a different NBIO generation can compile cleanly while targeting the wrong register.
- The chunk starts and ends mid-block. Adjacent chunks are required for a full per-file report and for complete `BIFP3_0` and `BIFPLR3_1` coverage.
- Repeated `BIFPLR0_1`, `BIFPLR1_1`, `BIFPLR2_1`, and `BIFPLR3_1` layouts are easy to confuse. Prefix mistakes can affect the wrong root port or link-root instance without producing a compiler error.
- Some symbolic registers intentionally share offsets because multiple PCI config fields occupy the same DWORD, for example `VENDOR_ID`/`DEVICE_ID`, `COMMAND`/`STATUS`, `LINK_CNTL`/`LINK_STATUS`, lane control/status pairs, and grouped per-lane equalization registers. Consumers must use the companion masks rather than assuming one macro means one independent storage location.
- Error injection, AER, DPC, reset, and local error registers can have destructive or sticky side effects on real hardware. Offset availability does not imply safe unconditional writes.
- Link speed, width, equalization, L1 substate, clock gating, and save/restore registers interact with live PCIe link training and platform power policy. Incorrect programming can cause link retraining, performance loss, hangs, or device disappearance.
- Strap and SMU/SMN-facing registers may reflect firmware-owned state. Driver writes must follow the sequencing and ownership rules in the NBIO implementation and platform firmware documentation.
- All macros use untyped preprocessor constants. There is no compile-time check that a register is accessed through the right aperture, with the right width, or under the right lock/clock/power condition.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage of `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` with this header and `nbio_7_7_0_sh_mask.h` included.
- Generated-header comparison against AMD's authoritative NBIO 7.7 register database, with special attention to the repeated port/root-port offsets and the mid-block chunk boundaries.
- Static checks that every non-`_BASE_IDX` macro in this range has a matching `*_BASE_IDX` macro and that all base indexes remain the expected SOC15 NBIO value.
- Cross-checks that bitfield references used with chunk registers, such as `BIF0_PCIE_MST_CTRL_3__*`, exist in the matching shift/mask header for the same ASIC generation.
- Hardware or simulator register-dump comparisons for NBIO 7.7 devices, especially PCIe port 3/4 link state, global `BIF0` PCIe control/status, and PCIe1 root-port config spaces for `BIFPLR0_1` through `BIFPLR3_1`.
- PCIe enumeration and `lspci -vvxxx` style validation for root-port identity, bridge windows, PCIe capabilities, AER, ACS, DPC, L1 PM substates, lane margining, and high-speed link capability/status fields.
- Runtime validation around `nbio_v7_7_init_registers()` that `regBIF0_PCIE_MST_CTRL_3` reads and writes the expected register and that master request-size behavior remains stable.
- Negative testing or guarded debug-only testing for error-injection, reset, and DPC paths, because those registers can intentionally perturb link or device state.
