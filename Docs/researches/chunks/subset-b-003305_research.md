# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 111116-113578

## Purpose

This chunk is generated AMD NBIO 7.7.0 register-field metadata. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for NBIO/BIF1 PCIe, reset, clock/power, SMU handoff, address-aperture, northbridge miscellaneous, remap, stall, and trap/debug registers. AMDGPU NBIO and PCIe code pairs these field constants with the matching register offset header and generic register helpers to pack, extract, preserve, or clear individual hardware fields.

The range starts in the BIF1 PCIe link-controller state history area, covering `BIF1_PCIE_LC_STATE8` through later BIF1 PCIe control/status groups. It then transitions through BIF1 reset and clock/power-management controls, PCIe margining and transaction tracking, performance counters, and finally into NB address blocks: `nbio_iohub_nb_nbcfg_nb_cfgdec`, `nbio_iohub_nb_fastreg_fastreg_cfgdec`, and `nbio_iohub_nb_misc_misc_cfgdec`. The chunk ends mid-register at `TRAP3_COMMAND__Trap3Cmd0__SHIFT`; the remaining `TRAP3_COMMAND` fields and later trap metadata belong to the following chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, or clearing that field.

Major register families in this chunk:

- BIF1 PCIe link and PHY metadata: `BIF1_PCIE_LC_STATE8` through `STATE11` expose previous link-controller states 32-47; `LC_STATUS1/2` expose reverse-lane flags, operating/detected width, inactive lanes, and lane turn-on state; `P_CNTL`, `P_BUF_STATUS`, `P_DECODER_STATUS`, `P_MISC_STATUS`, and `P_RCV_L0S_FTS_DET` cover PHY powerdown, symbol align/deskw/error-ignore controls, electrical-idle behavior, master PLL lane/refclk handling, lane tieoff behavior, buffer overflow/underflow, decoder errors, deskew/symbol-unlock errors, and L0s FTS detection windows.
- BIF1 PCIe packet, sideband, and config controls: RX/TX last-TLP registers capture last received/transmitted TLP dwords; `RX_AD` controls received VDM/drop/unsupported-request behavior; `CFG_CNTL` controls hidden config decode; `I2C_REG_ADDR_EXPAND` and `I2C_REG_DATA` expose expanded I2C register access; `SDP_CTRL`, `SDP_CTRL2`, SWUS/RC slave attribute controls, and TX F0/SWUS attribute controls define SDP disconnect, wake, virtual-wire, parity, RO/SNR/IDO override, and request handling behavior.
- Clock request and power-management mapping: `PCIE_LC_PM_CNTL`, `PCIE_LC_PM_CNTL2`, `NBIO_CLKREQb_MAP_CNTL`, and `NBIO_CLKREQb_MAP_CNTL2` map PCIe ports 0-11 to CLKREQ# lines and provide per-line control-mask bits.
- PCIe performance counters: global enable/shadow/reset in `PCIE_PERF_COUNT_CNTL`; repeated `PCIE_PERF_CNTL_TXCLK1` through `TXCLK10` selector/full bits; paired 32-bit counter registers; and LC/CI port-selection registers for choosing which port feeds individual TXCLK/LCLK counter lanes.
- Strap and capability registers: `PCIE_STRAP_F0`, `PCIE_STRAP_NTB`, `PCIE_STRAP_MISC`, `PCIE_STRAP_MISC2`, `PCIE_STRAP_PI`, and `PCIE_STRAP_I2C_BD` describe enablement bits for function 0, NTB, MSI/MSI-X style capabilities, VC, DSN, AER, ACS, BAR/power/DPA, ATS/PASID/page request, ECRC, atomic ops, ARI/SR-IOV, DLF, Gen2-Gen5 compliance, DRS/FRS/RTR/immediate-readiness, 16/32 GT operation, link-bandwidth notification, bypass scrambler, clock PM, reverse lane behavior, address width, and I2C board strap fields.
- PRBS and link test registers: clear/status/freerun/misc/user-pattern/bit-count fields plus per-lane `PRBS_ERRCNT_0` through `PRBS_ERRCNT_15` counters for PCIe pseudo-random bit sequence diagnostics.
- Software reset controls: `SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0/1`, `SWRST_CONTROL_0` through `CONTROL_6`, and EP command/control registers define reconfigure/atomic-reset commands, reset completion/wait/perst state, SWUS/SWDS link reset types, per-port config/COR reset, BIF global/calib/core/register/PHY/sticky/config/SDP-credit reset, PCS reset 0-15, AXI/PCFG/LNCT/MNTR/HLTR/CPM/PHY reset, strap toggling, and RCEN/ATEN/other enable masks for those reset sources.
- Clock and power management: `CPM_CONTROL`, `CPM_SPLIT_CONTROL`, `CPM_CONTROL_EXT`, and `LC_CPM_CONTROL_0/1` define LCLK/REFCLK/PCLK/TXCLK inactivity timers, hysteresis, shutdown/disconnect controls, clock-domain selection, clock-gating, link-state and SDP-related power behavior, and LC-specific CPM overrides.
- SMU and interrupt handoff: `SMN_APERTURE_ID_A/B`, `SMU_HP_STATUS_UPDATE`, `HP_SMU_COMMAND_UPDATE`, `SMU_HP_END_OF_INTERRUPT`, `SMU_INT_PIN_SHARING_PORT_INDICATOR`, `SMU_INT_PIN_SHARING_PORT_INDICATOR_TWO`, `SMU_PCIE_FENCED1_REG`, and `SMU_PCIE_FENCED2_REG` expose SMN aperture IDs, host/SMU status-command signaling, interrupt pin sharing indicators, and fenced SMU-controlled PCIe lockdown/overclocking bits.
- PCIe margining, presence, debug, tracking, and master/slave controls: `PCIE_RXMARGIN_*` advertise and configure receiver margining; `PRESENCE_DETECT_SELECT` chooses presence-detect inputs; `LC_DEBUG_CNTL` controls link-controller debug output; `TX_TRACKING_*` captures tracked TX addresses and valid/status bits; `TX_STATUS` exposes master/slave idle and credit-empty/no-credit state; `BW_BY_UNITID` and `MST_CTRL_1` control bandwidth accounting and advertised master credits.
- HIP aperture registers: `PCIE_HIP_REG0` through `HIP_REG8` provide two HIP aperture base/limit pairs, enable bits, PASID mode, request-AT/request-IO mode, and masks.
- NB address-block registers: `NB_NBCFG0_NBCFG_SCRATCH_4` is a scratch register; `FASTREG_APERTURE` identifies fastreg aperture, node, and posted-transaction mode; `NB_CNTL`, `NB_SPARE1/2`, `NB_REVID`, `NBIO_LCLK_DS_MASK`, bus-number controls, MMIO base/limit, TOM2/DRAM2/DRAM3 base/top registers, SB/SW-US location, and `NB_PROG_DEVICE_REMAP_PBr*` define northbridge lock/spare/revision/address/remap state.
- NB misc debug and error path registers: software interrupt/status controls (`SW_NMI_CNTL`, `SW_SMI_CNTL`, `SW_SCI_CNTL`, `SW_GIC_SPI_CNTL`, `SW_SYNCFLOOD_CNTL`, `APML_SW_STATUS`), CAM target index/data/mask registers, posted/non-posted DMA dropped-log registers, PCIe VDM controls, crossbar stall controls for ports 0-6, SMU/FastReg base-address registers, scratch registers, SMU CPU-block status, trap request/response payload registers, and trap match controls for traps 0-3 through the first field of `TRAP3_COMMAND`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU's NBIO, PCIe, power-management, reset, and diagnostic paths:

1. NBIO 7.7.0 code includes this shift/mask header with the matching NBIO offset header.
2. Register helper macros or tables combine an offset, a mask, and a shift into read/modify/write or field-extract operations.
3. Driver initialization, reset, suspend/resume, runtime power management, PCIe link management, SMU handoff, and diagnostics select a register, read or update a field, and rely on these constants to touch only the intended bits.
4. Hardware owns the actual sequencing for link-state transitions, PRBS counting, performance counters, reset completion, clock-gating transitions, trap capture, dropped-DMA logging, and SMU/host interrupt handshakes.

The macros themselves do not encode ordering rules. Consumers must still sequence reset enables before commands, wait for reset/link completion where required, gate PRBS and performance counters around reads, avoid modifying strap-derived fields at unsafe times, preserve reserved bits during read/modify/write, and coordinate SMU-controlled fields with firmware ownership.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed state in NBIO/BIF1 registers:

- Link and PHY state includes previous LC state history, detected/operating link width, inactive lanes, lane turn-on state, PHY power and alignment controls, decoder/buffer/deskw/symbol errors, and L0s FTS detection thresholds.
- Packet and transaction state includes last RX/TX TLP captures, VDM/drop/UR routing controls, SDP wake/disconnect/virtual-wire/parity behavior, TX idle/credit status, per-unit bandwidth selection, master credit advertisement, and HIP aperture base/limit/mode registers.
- Power, clock, and reset state includes CLKREQ# mappings, CPM timers/overrides, clock shutdown/gating enables, software reset commands and enables, reset status bits, and endpoint reset masks.
- Capability and strap state exposes static or strap-latched PCIe feature advertisement for function 0, NTB, link rates, compliance modes, SR-IOV/ARI/PASID/ATS/page request, AER/ECRC/atomic behavior, and related PCIe features.
- Diagnostic state includes performance counter selectors/counters/full flags, PRBS bit/error counters, RX margining controls, presence-detect selection, debug controls, dropped DMA logs, crossbar stall controls, trap requests, trap responses, and trap comparator programming.
- NB address state includes MMIO ranges, top/base of DRAM windows, bus numbering, programmed device remap entries, SMU/FastReg aperture bases, and scratch/spare registers.

Persistence is hardware-defined. Strap-derived and aperture fields may be latched during boot or early initialization. Runtime configuration fields generally survive until GPU reset, BIF/NBIO reset, power-gating, suspend/resume reinitialization, or explicit driver/firmware reprogramming. Status, interrupt, dropped-log, trap, PRBS, performance-counter, and reset-complete fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant clock or power domain is active. This generated header does not document access semantics; consumers need the hardware specification and local driver conventions.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.7.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which provides the matching register offsets and base-index selectors.
- AMDGPU NBIO 7.7.0 implementation files that include `nbio_7_7_0_sh_mask.h` to program PCIe, reset, clock/power, interrupt, and SMU-facing behavior.
- Generic AMD register-helper macros used throughout the driver to pair `__SHIFT` and `_MASK` constants with MMIO/SMN/indirect register accesses.
- PCIe link training and power-management paths that inspect LC status/state history, program CLKREQ# mappings, control CPM behavior, and coordinate link resets.
- GPU reset and recovery paths that use the `SWRST_*` fields to command and observe port, BIF, PCS, AXI, PHY, CPM, and endpoint resets.
- SMU/firmware integration paths that exchange host-port status/commands, handle SMU interrupt pin sharing, respect fenced lockdown/overclocking fields, and manage SMN/FastReg apertures.
- Diagnostic and validation tooling that reads PRBS, performance counters, dropped DMA logs, TX tracking, RX margining, crossbar stall, and trap capture registers.
- PCI core-facing behavior, because strap, remap, aperture, bus-number, MMIO, and capability fields affect how the GPU presents PCIe capabilities and address routing to the host.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while reading or modifying the wrong hardware bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The requested range begins after earlier LC state definitions and ends inside `TRAP3_COMMAND`. Complete reasoning about adjacent LC history and trap-3 command masks requires neighboring chunks.
- Several fields are safety-critical for reset and power sequencing. Incorrect `SWRST_*`, CPM, CLKREQ#, or clock-gating masks can cause hangs, incomplete recovery, resume failures, link loss, or register access while a clock domain is inactive.
- Strap/capability fields can affect externally visible PCIe behavior. Bad masks may advertise unsupported PCIe rates, atomic operations, PASID/ATS/page request, SR-IOV/ARI, AER/ECRC, DRS/FRS, or compliance modes.
- Link-status and lane-width fields are used for diagnostics and policy decisions. Wrong masks can misreport negotiated width, lane reversal, inactive lanes, or link-controller history.
- Counter and diagnostic fields are often latch, shadow, clear, or full-status sensitive. Incorrect sequencing around `GLOBAL_SHADOW_WR`, counter reset, PRBS clear, trap trigger, or dropped-log reads can produce stale or destructive diagnostics.
- SMU and fenced registers may have firmware ownership constraints. Driver writes without coordinating with SMU policy can conflict with lockdown, overclocking, interrupt, or host-port command handling.
- Address-window and remap fields are high blast-radius. Wrong TOM/MMIO/DRAM base, FastReg, SMU aperture, or device-remap masks can route traffic incorrectly or break CPU/GPU/firmware access paths.
- Repeated per-port/per-lane/per-counter definitions are copy-sensitive. Testing a single port, lane, trap, or TXCLK counter does not validate the rest of the repeated namespace.

## Test Signals

Useful validation combines generated-header consistency checks with hardware-facing AMDGPU tests:

- Build AMDGPU with NBIO 7.7.0 support enabled. Missing or renamed macros should fail in NBIO, PCIe, reset, power-management, SMU, or diagnostic register-table code.
- Mechanically verify every complete register field in this slice has a matching `__SHIFT` and `_MASK`, while allowing the line-boundary exception at `TRAP3_COMMAND__Trap3Cmd0__SHIFT`.
- Diff this slice against AMD's authoritative NBIO 7.7.0 register database and adjacent generated ASIC headers where layout compatibility is expected.
- Exercise PCIe link bring-up, retraining, ASPM/L1 entry and exit, CLKREQ# behavior, lane-width reporting, hot reset, link-disable reset, link-down reset, suspend/resume, and full GPU reset/recovery.
- Validate PRBS, performance counters, RX margining, TX tracking, last-TLP capture, dropped-DMA logs, crossbar stall controls, and trap capture using hardware diagnostics or debugfs paths where available.
- Confirm SMU handoff paths: host-port command/status update, end-of-interrupt handling, interrupt pin sharing, SMU block CPU/status, fenced lockdown, and overclocking policy fields.
- Check PCIe capability enumeration and OS-visible behavior for strap-controlled features such as AER, ACS, ATS, PASID, page request, SR-IOV/ARI, ECRC, atomic ops, DRS/FRS, RTR, and advertised link-rate/compliance behavior.
- Read back MMIO/TOM/DRAM/FastReg/SMU aperture and device-remap registers after initialization and resume to catch address-window or remap regressions.
- Monitor kernel logs for PCIe AER events, reset timeouts, link-width/speed downgrades, SMU command failures, suspend/resume failures, stuck interrupts, and NBIO diagnostic counter anomalies.

## Cross-Chunk Notes

The previous chunk owns earlier BIF1 LC state-history definitions before `LC_STATE8`. This chunk covers BIF1 PCIe link, packet, clock/power, performance, strap, PRBS, reset, CPM, SMU, margining, TX tracking, HIP aperture, NB scratch/FastReg/misc, remap, stall, dropped-log, and trap request/response metadata through the opening field of `TRAP3_COMMAND`. The next chunk must supply the rest of `TRAP3_COMMAND` and following trap definitions before the final per-file report makes complete claims about trap comparator coverage in `nbio_7_7_0_sh_mask.h`.
