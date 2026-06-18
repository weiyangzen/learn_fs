# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 51445-54195

## Scope

This chunk covers a generated AMD NBIO 2.3 shift/mask header section. It starts in the middle of the `PCIEMSIX_VECT102_ADDR_HI` definitions, continues through the rest of the MSI-X vector table entries for vectors 102 through 255, covers the `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` pending-bit-array masks, and then enters `addressBlock: nbio_pcie0_pswusp0_pciedir_p`.

The PCIe portion covers port control, transmit and receive control, flow-control credits, error control and error injection, SR-IOV private control, NAK counters, link-control/training/link-width/speed state, link-management status, bandwidth-change status, clock/data recovery controls, lane corruption status, and PCIe link equalization controls through the first four `PCIE_LC_CNTL5` mask definitions. The range ends mid-register in `PCIE_LC_CNTL5`; the remaining masks for that register and later PCIe link-control registers are in the next chunk.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or runtime MMIO access. Its exported convention is:

- `<REGISTER>__<FIELD>__SHIFT` for bit offsets.
- `<REGISTER>__<FIELD>_MASK` for 32-bit field masks.

## Purpose

This header is the bitfield side of the NBIO 2.3 register ABI used by AMDGPU and SMU/power-management code. The companion `nbio_2_3_offset.h` header supplies the register addresses and base indices; this file supplies the field positions and masks used to compose and decode register values with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15`.

The two major hardware surfaces in this chunk are MSI-X interrupt-table state and PCIe link/port state. MSI-X definitions describe per-vector message address, message data, and mask bits. PCIe definitions describe how software reads link width/speed, manages ASPM and low-power transitions, tracks link-training state, handles flow-control credits, injects or masks errors, and controls equalization or recovery behavior.

## Important Macro Families

### MSI-X Vector Table and Pending Bit Array

The first part continues the `nbio_nbif0_pciemsix_0_usb_MSIXTBLDEC` table:

- `PCIEMSIX_VECT102_ADDR_HI` starts this chunk at the high address portion of vector 102.
- `PCIEMSIX_VECT102_MSG_DATA` and `PCIEMSIX_VECT102_CONTROL` finish vector 102.
- `PCIEMSIX_VECT103_*` through `PCIEMSIX_VECT255_*` provide the regular four-register pattern for each vector: `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL`.

The field layouts are uniform: low message address fields start at bit 2 with `0xFFFFFFFC`, high address and message data fields are full-width `0xFFFFFFFF`, and control exposes bit 0 as `MASK_BIT`. This is the software-visible MSI-X vector table programming model: each vector carries a message address, message data payload, and a per-vector mask.

`PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` then expose full-width `MSIX_PENDING_BITS` masks. Together these eight 32-bit registers cover the pending state for 256 MSI-X vectors.

### PCIe Port, Transmit Path, and Flow-Control Credits

The `nbio_pcie0_pswusp0_pciedir_p` block begins with basic port registers:

- `PCIEP_RESERVED` and `PCIEP_SCRATCH` are full-width placeholder/scratch fields.
- `PCIEP_PORT_CNTL` controls slave-port request enablement, snoop override, hotplug messages, native PME, power-fault handling, bus-mastering PMI behavior, completion allocation limits, private completion payload sizing, poisoned/UR response mode, and completion-payload mode.

Transmit-side registers include:

- `PCIE_TX_CNTL` for relaxed-ordering/non-snoop overrides, packet packing, TLP flush behavior, posted-pass behavior for CPL/NP traffic, extra PM request cleanup, flow-control update timeout disable, TPH disable per function, and RTRC/BFRC swapping.
- `PCIE_TX_REQUESTER_ID` for function/device/bus requester ID fields.
- `PCIE_TX_VENDOR_SPECIFIC` and `PCIE_TX_NOP_DLLP` for vendor and NOP DLLP data plus send strobes.
- `PCIE_TX_REQUEST_NUM_CNTL` for outstanding NP request limits and enable bits.
- `PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, and `PCIE_TX_ACK_LATENCY_LIMIT` for sequence-number tracking, replay count/timer override, and ACK latency override.
- `PCIE_TX_CNTL_2` for skid credit limit override.

The transmit credit definitions separate advertised, initialized, current/error, and flow-control-update threshold state:

- `PCIE_TX_CREDITS_ADVT_P/NP/CPL` and `PCIE_TX_CREDITS_INIT_P/NP/CPL` define header/data credit fields for posted, non-posted, and completion traffic.
- `PCIE_TX_CREDITS_STATUS` exposes error and current-status bits for all six credit categories.
- `PCIE_TX_CREDITS_FCU_THRESHOLD` defines per-VC threshold fields for posted, non-posted, and completion flow-control updates.

`PCIE_FC_P`, `PCIE_FC_NP`, `PCIE_FC_CPL`, and their `_VC1` variants describe advertised flow-control credit state for VC0 and VC1.

### Receive Path, Error Control, Error Injection, and SR-IOV

`PSWUSP0_PCIE_ERR_CNTL` controls error reporting, ECRC dropping, generated LCRC/ECRC errors, AER header-log timeout and expiry status, slave-buffer halt status/reset, immediate error messages, poisoned advisory behavior, and private AER masks for bad DLLP/TLP.

`PSWUSP0_PCIE_RX_CNTL` is a dense receive-policy register. It can ignore or mask IO, BE, message, CRC, config, completion, poisoned, length mismatch, max payload, traffic class, unsupported request, address translation, prefix, PASID, and CTO-related errors. It also controls NAK generation, RX flow-control initialization from registers, RCB completion timeout behavior, TPH disable, and FLR timeout disable.

`PCIE_RX_CNTL3` adds root-complex/PASID-related unsupported-request ignore bits. `PCIE_RX_EXPECTED_SEQNUM` and `PCIE_RX_VENDOR_SPECIFIC` expose receive sequence/vendor state. `PCIE_RX_CREDITS_ALLOCATED_P/NP/CPL` define allocated receive data/header credits for posted, non-posted, and completion traffic.

The physical and transaction error-injection registers are explicit test/debug surfaces:

- `PCIEP_ERROR_INJECT_PHYSICAL` covers lane, framing, SKP parity/LFSR, loopback underflow/overflow, deskew, 8b/10b disparity/decode, SKP ordered-set, invalid ordered-set identifier, and bad sync-header injection fields.
- `PCIEP_ERROR_INJECT_TRANSACTION` covers flow-control, replay rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout injection fields.

`PCIEP_SRIOV_PRIV_CTRL` defines VF mapping mode and VF-save behavior when VF enable is cleared. `PCIEP_NAK_COUNTER` exposes 16-bit counters for NAKs received and generated by the port.

### Link Control, Training, Width, Speed, and State History

The `PCIE_LC_*` families describe the link controller and are the most directly integrated with power-management and link-management paths:

- `PCIE_LC_CNTL` controls entry into L2/L3 from D0, link reset, x16 TX pipe clearing, L0s/L1 inactivity timers, PMI-to-L1 behavior, idle detection, wake from L2/L3, ASPM-to-L1 disable, L0s/L1 exit delays, L1/L23 escape, and receiver idle gating.
- `PCIE_LC_TRAINING_CNTL` covers training mode, compliance receive, L0s/L1 training enable, power state, CSR-initiated speed change, training-bit behavior, hot-reset quick exit, autonomous change/upconfigure disablement, hardware link-disable state, ASPM L1 NAK timer selection/reset, receiver enable behavior during speed/test states, and equalization timing extension.
- `PCIE_LC_LINK_WIDTH_CNTL` has requested and read-back link width fields, reconfiguration support/control, renegotiation enable, upconfigure support/disable, dynamic lane power state, reversal/equalization helpers, idle/electrical-idle waits, unused-lane shutdown, and RX standby bypass.
- `PCIE_LC_N_FTS_CNTL` controls transmitted FTS counts, override, pre-recovery FTS, EIE selection, 8GT/16GT behavior, FTS limit, and received/negotiated FTS count.
- `PSWUSP0_PCIE_LC_SPEED_CNTL` defines Gen2/Gen3/Gen4 enable straps, target speed override, forced software/hardware speed-change enable/disable, speed-change initiation, allowed attempts, failure/current data-rate status, failed-count clear, peer Gen2/Gen3/Gen4 support/ever-sent indicators, advertised rate, data-rate checking, and speed negotiation from L0s/L1.
- `PCIE_LC_STATE0` through `PCIE_LC_STATE5` expose the current link-controller state plus a rolling history of 23 previous states, six bits per state slot.

`PCIE_LINK_MANAGEMENT_CNTL2` reports quiesce and equalization request send/receive state and defines bandwidth hint mode plus low/high bandwidth thresholds for Gen2, Gen3, and Gen4. `PSWUSP0_PCIE_LC_CNTL2` exposes timed-out/illegal-state status, bandwidth-reduction behavior, TS2 behavior, x12 negotiation disable, link-up reversal, electrical-idle behavior, L1/L23 powerdown permission, lost-symbol-lock behavior, bandwidth notification disable, PMI L1 slave-idle wait, test timer selection, and inferred electrical idle control.

`PCIE_LC_BW_CHANGE_CNTL` provides bandwidth-change interrupt enable and status causes for hardware, software, other, reliability, failed speed negotiation, long/short link-width changes, other/failed link-width changes, notification detect mode, and unsuccessful speed negotiation.

### Equalization, CDR, Lane Status, and Partial CNTL5

The late-link portion includes:

- `PCIE_LC_CDR_CNTL` for CDR test offset, test sets, and set type.
- `PCIE_LC_LANE_CNTL` for a 16-bit corrupted-lane bitmap.
- `PCIE_LC_CNTL3` for de-emphasis selection, received de-emphasis, detect completion, TS counter reset in recovery lock, automatic speed-change attempts/failure/clear, enhanced hotplug, receiver-detect override, link-down speed-change enable, L1 reconfiguration block, automatic speed-support disablement, fast L1 entry/exit, P0 powerdown/refclkack wait, `LC_DSC_DONT_ENTER_L23_AFTER_PME_ACK`, hardware voltage interface, recovery trigger, and automatic recovery disable.
- `PCIE_LC_CNTL4` for TX-enable behavior, ASPM L1 disable during speed changes, Gen3/8GT equalization bypass/redo/search behavior, quiesce set/received state, forced presets and coefficients in EQ request phase, TX swing, wait-for-evaluation-done, skip ordering, and recovery-lock TS wait count.
- `PCIE_LC_CNTL5` begins local equalization settings with rate, preset, pre-cursor, and cursor fields. The chunk stops before the rest of `PCIE_LC_CNTL5` is fully documented in-source.

## Control Flow and State Behavior

There is no executable control flow in this header. Its effect is compile-time: C code includes the header and uses these constants to produce or decode exact 32-bit MMIO bit patterns for NBIO 2.3 hardware.

The represented state is persistent hardware register state, not software-owned storage in this file. MSI-X vector entries persist message address/data/mask configuration and pending bits until programmed or cleared through the PCI/MSI-X path. PCIe port and link registers persist link policy, link-training state, flow-control credit state, error policy, SR-IOV behavior, and debug/error-injection settings across the hardware lifetime defined by reset, power-gating, suspend/resume, and firmware/driver reinitialization.

Several fields are status, sticky status, or command-like strobes rather than ordinary configuration. Examples include MSI-X pending bits, vendor/NOP send bits, generated error controls, slave-buffer halt reset, NAK generation, link reset, reconfiguration-now, initiate-link-speed-change, failed-speed-change clear, bandwidth-change cause bits, quiesce set/received, `LC_GO_TO_RECOVERY`, and error-injection fields. Correct users must follow ordering, polling, timeout, and clear semantics from the AMDGPU code and hardware specification; the masks alone do not express those rules.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 header set:

- `nbio_2_3_offset.h` supplies matching register addresses and base indices.
- `nbio_2_3_default.h` supplies generated defaults where available.
- AMDGPU register helper macros consume the `__SHIFT`/`_MASK` convention for field composition and extraction.

Observed integration in this source tree includes:

- `amdgpu/nbio_v2_3.c` includes `nbio_2_3_offset.h`, `nbio_2_3_default.h`, and this mask header. Its ASPM programming path uses `PCIE_LC_CNTL`, `PCIE_LC_CNTL3`, `PSWUSP0_PCIE_LC_CNTL2`, and `PCIE_LC_LINK_WIDTH_CNTL` masks to disable/restore L0s/L1 timers, prevent L2/L3 entry during PME-ack handling, allow L1/L23 powerdown, and read link width.
- `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c` include the NBIO 2.3 mask header alongside SMU tables, so SMU power-management code can share generated NBIO field definitions.
- `amdgpu/mxgpu_nv.c` includes this header in SR-IOV/MxGPU support, matching the presence of `PCIEP_SRIOV_PRIV_CTRL` and MSI-X/PCIe virtualization-sensitive register state in the chunk.
- Older and related generation code (`cik.c`, `vi.c`, and Vega powerplay hwmgr files) uses the same PCIe link-control field families to read current link speed/width, initiate speed changes, quiesce/re-equalize links, enter recovery, and tune ASPM. This shows the expected usage pattern for the NBIO 2.3 macros even when the exact include file differs by ASIC generation.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write the wrong PCIe control bit, causing link retraining failures, lost interrupts, incorrect power-state behavior, or GPU hangs.
- MSI-X vector definitions are extremely repetitive and mechanically fragile. Off-by-one vector numbering or wrong `MASK_BIT`/message-address masks can route interrupts to the wrong vector, leave interrupts masked, or corrupt the pending-bit mapping.
- PCIe link-control fields affect live bus connectivity. Incorrect use of link reset, speed-change initiation, reconfiguration, quiesce, recovery, dynamic lane power state, or equalization controls can drop the link or leave the GPU unreachable until reset.
- ASPM and L1/L23 powerdown bits are platform-sensitive. Values that work on one board or bridge can regress hotplug, Thunderbolt/removable devices, resume, or idle power on another.
- Error masking and error-injection fields are reliability-sensitive. Accidentally enabling injection, suppressing AER/ECRC/PASID errors, or clearing/ignoring completion timeout behavior can hide real PCIe faults or create false fault reports.
- Flow-control credit masks describe protocol-level resources. Bad advertised/allocated credit values can deadlock traffic, create replay storms, or produce misleading credit-error status.
- SR-IOV private controls and MSI-X state are virtualization-sensitive. Incorrect PF/VF mapping or interrupt masking can break VF isolation, event delivery, or guest-driver behavior.
- The chunk boundary is mid-family: it starts after `PCIEMSIX_VECT102_ADDR_LO` and ends before all of `PCIE_LC_CNTL5` is present. The final per-file merge must reconcile those boundaries before making complete source-file claims.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and link-state testing:

- Build AMDGPU, SMU11, and MxGPU/SR-IOV code that includes `nbio/nbio_2_3_sh_mask.h`; this catches missing or renamed generated macros.
- Boot Navi/NBIO 2.3 hardware through `nbio_v2_3.c` and verify ASPM programming does not regress suspend/resume, hotplug/removable-device behavior, or idle power.
- Read current PCIe link width and speed through power-management paths and compare against `lspci` link status and expected platform capabilities.
- Exercise link retraining and recovery paths where available, checking that `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_GO_TO_RECOVERY`, bandwidth-change status, and state-history fields converge without timeouts.
- Validate MSI-X interrupt delivery across high vector numbers, especially vectors above 102, and verify per-vector masking plus PBA pending bits behave as expected.
- Run PCIe AER/RAS diagnostics or controlled error-injection tests only in a suitable lab environment, confirming injected physical/transaction errors surface through expected AER/status paths and are not left enabled.
- For SR-IOV, create/destroy VFs and verify VF MSI-X delivery, VF mapping state, and PF/VF isolation remain correct across VF enable/disable and reset.

## Unresolved Cross-Chunk References

Line 51445 is the tail of the `PCIEMSIX_VECT102_ADDR_HI` register; the matching `PCIEMSIX_VECT102_ADDR_LO` definition belongs to the previous chunk. Line 54195 ends after `PCIE_LC_CNTL5__LC_LOCAL_CURSOR_MASK`; later `PCIE_LC_CNTL5` fields such as local post-cursor, RX standby, safe recovery, preset acceptance, detect wait, and hold-training masks continue in the next chunk. The merge lane should stitch these partial register families together.
