# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 17032-19461

## Scope

This chunk covers a generated AMD NBIO 7.2.0 register offset header section. It starts in the tail of the `nbio_pcie0_bifplr5_cfgdecp` PCIe root-port capability map, then covers the complete `nbio_pcie0_bifplr6_cfgdecp` root-port configuration block, repeated per-port PCIe directory blocks `nbio_pcie0_bifp0_pciedir_p` through `nbio_pcie0_bifp6_pciedir_p`, the shared `nbio_pcie0_pciedir` block, the one-register `nbio_iohub_nb_fastreg_fastreg_cfgdec` block, and the start of `nbio_iohub_nb_misc_misc_cfgdec`.

The file is data-only C preprocessor material. This range defines 2386 `#define` constants: register-offset macros such as `regBIFPLR6_0_LINK_STATUS` and their matching `<name>_BASE_IDX` macros. It defines no functions, structs, variables, storage, locks, allocations, or executable MMIO operations.

## Purpose

This header section is the address side of the NBIO 7.2.0 hardware register ABI used by AMDGPU code. Each non-`_BASE_IDX` macro maps a symbolic NBIO/PCIe register name to a generated register offset, while each `_BASE_IDX` macro identifies the SOC15 base-index slot used by AMDGPU register helpers.

Consumers normally pair these offsets with matching shift/mask definitions from `nbio_7_2_0_sh_mask.h` and defaults from `nbio_7_2_0_default.h`. Driver code then accesses the registers through helper patterns such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`, depending on the call site and address space.

## Important Macro Families

### BIFPLR5 Tail: Margining, CCIX, and ESM

The chunk begins after the `BIFPLR5_0` register family has already started. Covered macros finish lane margining control/status for lanes 10-15, then define CCIX and ESM-related capability/control offsets:

- `regBIFPLR5_0_PCIE_CCIX_CAP_LIST`, `PCIE_CCIX_HEADER_1/2`, `PCIE_CCIX_CAP`, `PCIE_CCIX_ESM_REQD_CAP`, `PCIE_CCIX_ESM_OPTL_CAP`, `PCIE_CCIX_ESM_STATUS`, and `PCIE_CCIX_ESM_CNTL`.
- `regBIFPLR5_0_ESM_LANE_0_EQUALIZATION_CNTL_20GT` through lane 15 and the equivalent `25GT` lane equalization controls.
- `regBIFPLR5_0_PCIE_CCIX_TRANS_CAP` and `PCIE_CCIX_TRANS_CNTL`.

This is a partial family because lanes 0-9 margining and earlier BIFPLR5 capability fields live in the previous chunk.

### BIFPLR6 Root-Port Configuration Space

The `nbio_pcie0_bifplr6_cfgdecp` block begins at base address `0x11106000` and is represented by `regBIFPLR6_0_*` offsets. It mirrors a PCIe root-port configuration-space view and includes:

- Standard PCI/PCIe header fields: vendor/device ID, command/status, class/revision, cache/latency/header/BIST, bus number and bridge window registers, ROM base, interrupt fields, and bridge control.
- Power management and PCIe capability registers: `PMI_*`, `PCIE_CAP`, `DEVICE_CAP/CNTL/STATUS`, `LINK_CAP/CNTL/STATUS`, slot/root capability and status registers, plus PCIe 2 capability/status families.
- MSI, SSID, MSI map, vendor-specific, virtual-channel, device serial number, advanced error reporting, secondary PCIe, ACS, multicast, L1 PM substate, DPC, RP PIO, data-link feature, 16GT PHY, margining, CCIX, and ESM/ESM-lane equalization registers.

Many logical fields intentionally share the same DWORD offset because PCI config registers pack multiple fields into one 32-bit location. For example ID, command/status, class-code, MSI, PCIe capability, margining control/status, and CCIX header/capability macros often alias the same offset with different symbolic names.

### Repeated BIFP0-BIFP6 PCIe Port Directories

The seven `nbio_pcie0_bifp*_pciedir_p` blocks at base addresses `0x11140000` through `0x11146000` repeat an identical per-port register layout using prefixes `regBIFP0_` through `regBIFP6_`. Each block covers:

- Per-port scratch, port control, requester ID, vendor-specific, sequence/replay/ACK/NAK, TX/RX control, and skid/nop-DLLP controls.
- Posted, non-posted, and completion flow-control credit advertising, initialization, allocation, and status registers, including VC1 flow-control views.
- CCIX port controls and stacked base/limit/misc status.
- Error handling and debug registers such as `PCIE_ERR_CNTL`, physical/transaction error injection, NAK counters, captured LTR control/status, AER private uncorrectable mask, and AER private trigger.
- Link-control and training registers: `PCIE_LC_CNTL`, training, width, speed, N_FTS, CDR, lane control, bandwidth-change control, force coefficient, best equalization settings, equalization request coefficient, link-management status/mask/control, L1 PM substates, port order, and later LC control/save-restore registers.
- Strap, BCH ECC, HPGI, HCNT descriptor, performance count, fine-grain clock-gate override, and save/restore offsets.

The repeated shape is important: a caller that selects the wrong `BIFP` prefix will program a different physical PCIe port even though the register family name and relative layout look correct.

### Shared PCIe Directory and Link/Performance Diagnostics

The `nbio_pcie0_pciedir` block at base address `0x11180000` defines shared `regPCIE_*`, `regSWRST_*`, `regCPM_*`, `regSMN_*`, `regLNCNT_*`, and `regLC_*` offsets. Major groups include:

- Common PCIe control/status: reserved/scratch, RX NAK counters, `PCIE_CNTL`, `CONFIG_CNTL`, TX tracking address/control/status, master control, common AER mask, bus control, WPR control, last-TLP capture, I2C register address/data, and configuration control.
- Link-state and power-management state: `PCIE_LC_STATE6` through `STATE11`, `PCIE_LC_STATUS1/2`, `PCIE_LC_PM_CNTL`, port-order control, P-buffer/P-decoder/P-misc status, and receive L0s FTS detect.
- CCIX and SDP controls: `PCIE_TX_CCIX_CNTL0/1`, `PCIE_TX_CCIX_PORT_MAP`, `PCIE_TX_CCIX_ERR_CTL`, `PCIE_RX_CCIX_CTL0`, `PCIE_RX_AD`, `PCIE_SDP_CTRL`, and SDP slave attribute controls for SWUS and RC paths.
- Performance counters across TXCLK and SCLK domains: `PCIE_PERF_COUNT_CNTL`, `PCIE_PERF_CNTL_TXCLK1..4`, `PCIE_PERF_COUNT0/1_TXCLK1..4`, `PCIE_PERF_CNTL_SCLK1/2`, `PCIE_PERF_COUNT0/1_SCLK1/2`, and event port-select registers.
- Strap and PRBS diagnostics: `PCIE_STRAP_*`, `PCIE_PRBS_CLR`, status, freerun, misc, user pattern, low/high bit counts, and per-lane error counters `PCIE_PRBS_ERRCNT_0..15`.
- Software reset, clock/power management, SMN aperture IDs, lane-count controls, programmable master/slave controls, CPM split/extension controls, RX margin settings, and presence-detect selection.

These offsets are used for link bring-up, low-level diagnostics, power/clock sequencing, PRBS link tests, and reset control.

### IOHUB Fastreg and Miscellaneous NB Registers

The `nbio_iohub_nb_fastreg_fastreg_cfgdec` block contains `regFASTREG_APERTURE` at base address `0x13b07000`.

The next block, `nbio_iohub_nb_misc_misc_cfgdec`, starts at base address `0x13b10000` and this chunk covers its first misc registers:

- LCLK deep-sleep masking and software interrupt routing/control: `regNBIO_LCLK_DS_MASK`, `regSB_LOCATION`, `regSW_US_LOCATION`, `regSW_NMI_CNTL`, `regSW_SMI_CNTL`, `regSW_SCI_CNTL`, `regAPML_SW_STATUS`, `regSW_GIC_SPI_CNTL`, and `regSW_SYNCFLOOD_CNTL`.
- CAM target index/data address and mask registers: `regCAM_CONTROL`, `regCAM_TARGET_INDEX_*`, and `regCAM_TARGET_DATA_*`.
- Posted and non-posted DMA dropped-log lower/upper registers.
- PCIe VDM controls and crossbar stall controls for ports 0-6.
- Fastreg base-address programming registers: `regFASTREG_BASE_ADDR_LO/HI` and `regFASTREGCNTL_BASE_ADDR_LO/HI`.

The chunk ends before scratch/trap request/response registers that continue the same misc block in the following lines.

## Control Flow and State Behavior

There is no runtime control flow in this header. Its effect is compile-time: symbolic constants determine which MMIO/config-space offsets AMDGPU code reads or writes.

The state described by this chunk is hardware state, not software state in the header. Durable configuration includes PCIe command/status and bridge aperture registers, root-port capabilities and controls, MSI mapping, virtual-channel controls, ACS/multicast/L1 PM/DPC settings, lane equalization and margining controls, per-port flow-control credits, link training policy, clock-gating overrides, reset controls, SMN aperture IDs, fastreg base addresses, and CAM target mappings.

Other offsets expose volatile or sticky hardware status: link status, AER/DPC/RP PIO error status and logs, lane error status, margining status, CCIX/ESM status, TX/RX replay and NAK counters, captured LTR and last-TLP data, PRBS bit/error counters, software reset command status, DMA dropped logs, and crossbar stall state. Some registers are command-like, including software reset command/control registers, PRBS clear controls, error-injection registers, AER/DPC clear/status paths, and margining control/status windows. The header does not encode ordering, polling, timeout, or clear-on-write semantics; those must come from the owning driver code and hardware specification.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.2.0 header set:

- `nbio_7_2_0_sh_mask.h` supplies field positions and masks for the offsets named here.
- `nbio_7_2_0_default.h` supplies generated reset/default values where present.
- SOC15 and AMDGPU register helpers consume the `<register>` and `<register>_BASE_IDX` convention to form MMIO addresses for NBIO instances.

Primary integration points are AMDGPU NBIO, PCIe, reset, RAS, and low-level diagnostics code. Typical consumers include ASIC-specific NBIO initialization and suspend/resume paths, PCIe link-speed/link-width management, ASPM/L1 PM handling, AER/DPC error reporting, SR-IOV or partitioning code that must distinguish ports and requester IDs, and debug tooling for PRBS, flow-control, replay/NAK, last-TLP, lane margining, and equalization. Because this is an offset header, most call sites include it indirectly through NBIO 7.2.0 register header aggregation rather than manipulating the file directly.

The chunk also integrates with adjacent generated chunks. The BIFPLR5 family is incomplete at the start, and the IOHUB misc block is incomplete at the end. The final per-file reconciliation should stitch these boundaries before treating either address block as fully documented.

## Risks

- Offset drift is high impact. An incorrect register offset or base index can send an otherwise valid read/write to the wrong NBIO or PCIe register, causing link training failure, bad bridge apertures, broken interrupts, lost AER/DPC information, hangs, or misleading diagnostics.
- Packed PCI config registers create deliberate aliasing. Multiple symbolic names often share a DWORD offset; consumers must use the matching shift/mask header instead of assuming each macro names an independent register.
- The BIFP0-BIFP6 blocks are mechanically repetitive. Copying code between ports with the wrong prefix can silently target the wrong physical PCIe port.
- Link-control, equalization, margining, and speed/width registers are sequencing-sensitive. Writes outside the expected training/retraining flow can destabilize the PCIe link.
- Error-injection, PRBS, AER, DPC, and RP PIO registers are diagnostic or fault-management surfaces. Leaving injected-error or clear/status bits in the wrong state can hide real link faults or create false ones.
- Flow-control credit and VC/CCIX controls can affect traffic ordering and forward progress. Incorrect programming can cause packet stalls, replay storms, or CCIX/VC interoperability failures.
- Reset and clock/power management registers are broad in blast radius. `SWRST_*`, `CPM_*`, lane-count, LCLK, and fine-grain clock-gate override registers must stay coordinated with NBIO reset and power-management policy.
- Fastreg, CAM, and SMN aperture registers affect address routing or indirect register access. Incorrect base/mask programming can route transactions incorrectly or make diagnostic windows point at the wrong target.
- Chunk boundaries split families. The BIFPLR5 start is partial, and the misc block continues after `FASTREGCNTL_BASE_ADDR_HI`; conclusions about those blocks need adjacent chunks.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and PCIe diagnostics coverage:

- Build AMDGPU code paths that include the NBIO 7.2.0 offset/mask/default headers; this catches missing, renamed, or syntactically broken generated macros.
- PCIe enumeration and bridge-window tests should validate standard BIFPLR6 config-space offsets for vendor/device ID, class code, command/status, bus numbers, BAR/ROM/interrupt fields, and capability-list traversal.
- Link bring-up and retraining tests should cover BIFP link-control, link-width, speed, N_FTS, CDR, equalization, margining, L1 PM substate, and lane-status registers across ports 0-6.
- Error-path validation should exercise AER, DPC, RP PIO, lane-error, replay/NAK counters, captured LTR, and last-TLP logging, including status clear behavior.
- PRBS and performance-counter diagnostics should verify shared `PCIE_PRBS_*`, per-lane error counters, and TXCLK/SCLK performance counters produce expected counts during controlled link tests.
- Reset and suspend/resume testing should exercise `SWRST_*`, `CPM_*`, LCLK deep-sleep masks, fine-grain clock-gating overrides, and save/restore registers without leaving links wedged or counters stale.
- Multi-port systems should verify that operations against `regBIFP0_*` through `regBIFP6_*` affect only the intended physical port.
- IOHUB misc validation should confirm fastreg aperture/base programming, CAM target mapping, dropped-DMA logs, VDM controls, and crossbar stall registers decode consistently with hardware events.

## Unresolved Cross-Chunk References

Line 17032 starts in the middle of the BIFPLR5 lane-margining family; lanes 0-9 and earlier BIFPLR5 PCIe capability registers are in the previous chunk. Line 19461 stops after `regFASTREGCNTL_BASE_ADDR_HI`, while the same `nbio_iohub_nb_misc_misc_cfgdec` block continues immediately afterward with scratch and trap request/response registers. The merge/reconciliation lane should connect both boundaries when producing the final per-file research document.
