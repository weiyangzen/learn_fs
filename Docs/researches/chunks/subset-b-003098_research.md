# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 73205-75613

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,170 `#define` field-layout macros and 231 register/address-block comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the middle of `BIFP6_PCIEP_ERROR_INJECT_TRANSACTION`, after the first transaction-layer error-injection shift fields are defined in the preceding lines. It then covers PCIe link-controller, PCIe0 directory, performance-counter, PRBS, software-reset, RSMU/SMU, link-counter, NB configuration, SMN-index/data, and IOMMU-shadow field definitions. The chunk ends after `SHADOW_IOMMU_CAP_BASE_HI`; the next source lines begin `nbio_iohub_nb_PCIE0shadow0_pcieshadow_cfgdecp`.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMDGPU's generated NBIO 7.0 register interface. For each hardware register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position used when encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the register mask used to isolate, clear, preserve, or update the field.

This slice describes PCIe link-management and NBIO control state rather than filesystem behavior, despite living under the repository's Ceph-client source mirror. It gives AMDGPU code symbolic access to low-level PCIe/NBIO hardware fields for link training, link width and speed changes, ASPM/L1 substates, link-management interrupts, error injection, performance counters, PRBS diagnostics, software reset sequencing, SMU/RSMU coordination, NB config-space windows, and IOMMU capability shadowing.

## Important Macro Families

The opening `BIFP6_*` section covers PCIe port and link-controller fields. It includes transaction-layer error-injection masks for flow-control errors, replay-number rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout. It also defines NAK counters, captured LTR interrupt/threshold state, broad `LC_*` controls for link reset, L0s/L1/L23 entry and exit timing, training state, link width renegotiation, N_FTS, speed changes, equalization, lane control, bandwidth-change interrupt status/masks, CDR controls, L1 PM substates, strap fields, BCH ECC, HPGI, and host-controller descriptor/performance counter state.

The `addressBlock: nbio_pcie0_pciedir` section describes the PCIE0 directory register layout. It includes general `PCIE_CNTL` and `PCIE_CONFIG_CNTL` fields, TX tracking address/control fields, bandwidth-by-unit-ID state, RX/TX attributes, CI and bus controls, additional link-controller state/status registers, write-protect control, captured last-RX/TX TLP dwords, I2C register-data expansion, PCIe config control, link power-management controls, port-order controls, port-buffer and decoder status, L0s FTS detection, RX AD controls, SDP/SWUS/RC slave attributes, and `NBIO_CLKREQb_MAP_CNTL`.

The same PCIE0 directory block also contains observability and validation facilities. `PCIE_PERF_CNTL_*` and `PCIE_PERF_COUNT*_*` define event selectors and 32-bit counters for TXCLK, master read/complete clocks, slave read/complete clocks, non-snoop complete clocks, and additional TXCLK lanes. `PCIE_PERF_CNTL_EVENT0_PORT_SEL` and `PCIE_PERF_CNTL_EVENT1_PORT_SEL` select per-clock-domain ports. `PCIE_PRBS_*` defines PRBS clear/status/freerun/misc/user-pattern registers, bit counters, and per-lane error counters 0 through 15.

The reset and management section covers `SWRST_*`, `CPM_CONTROL`, `SMN_APERTURE_ID_*`, `RSMU_*`, `LNCNT_*`, and SMU/HP registers. These fields model software-triggered upstream/downstream link resets, endpoint reset controls, wait-for-linkup behavior, hot-reset/link-disable/link-down reset type selection, reset hold/release enables, clock/power management control, SMN aperture identifiers for SMU/PCS/IOHUB/NBIF, RSMU master/slave/power-gating and BIOS-timer controls, link-counter windows/weights/thresholds/accumulators, SMU hotplug status and command-update handshakes, end-of-interrupt state, interrupt-pin sharing indicators for link management and LTR, and PCIe master/slave power-gating hysteresis.

The `addressBlock: nbio_iohub_nb_nbcfg_nb_cfgdec` section defines northbridge PCI configuration fields. It includes standard identity and header fields (`VENDOR_ID`, `DEVICE_ID`, command, status, revision, class/subclass, cache line, latency, header type, subsystem IDs, and capability pointer), PCI control bits (`PMEDis`, `SErrDis`, `MMIOEnable`, `HPDis`), PCI arbiter/PME/VGA-hole state, DRAM slot base/top-of-DRAM fields, scratch registers, SMN index-extension/index/data windows 0 through 6, index-data mutexes, and a global NB performance-counter control register with enable, shadow-write, reset, and delayed reset/shadow timing fields.

The final `addressBlock: nbio_iohub_nb_iommushadow_iommushadow_cfgdecp` fragment defines the IOMMU shadow capability base. It contains `SHADOW_IOMMU_MMIO_CNTRL_0__IOMMU_EN`, `SHADOW_IOMMU_CAP_BASE_LO__IOMMU_ENABLE`, low base-address bits starting at bit 19, and the high 32 bits of the IOMMU base address.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped C preprocessor integer literals, mostly with an `L` suffix.

Consumers combine these definitions with sibling generated address/default headers and AMDGPU register helpers. Typical users read a hardware register, extract a field with `*_MASK` and `*_SHIFT`, or perform a read/modify/write that clears a field mask and ORs in `(value << shift) & mask`. These macros do not encode register addresses, access permissions, reset values, write-one-to-clear semantics, reserved-bit policy, firmware ownership, or required timing between writes.

## Control Flow

This header has no local runtime control flow. Runtime flow is external and hardware-driven:

1. AMDGPU code selects an NBIO/PCIe/NB configuration register address from companion generated metadata.
2. It reads the register through an MMIO, SMN, PCI config, or indirect-index path appropriate for the register block.
3. It decodes status fields or composes a new register value using the shift/mask constants in this chunk.
4. Hardware state machines then perform link training, link-speed changes, width renegotiation, L1/L23 transitions, reset sequencing, PRBS counting, power gating, or SMU/RSMU handshakes.

The field names imply several asynchronous hardware flows that call sites must sequence and poll carefully: LTSSM/link-controller training state, ASPM and L1-substate entry/exit, receiver idle and electrical-idle detection, speed-change/equalization, CDR behavior, hot reset and link disable, PRBS measurement windows, performance-counter latching, LTR interrupt reporting, power-gating idleness, and IOMMU shadow-base exposure.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state in NBIO 7.0 PCIe, RSMU/SMU, NB config, and IOMMU-shadow registers.

Represented state includes writable control bits, strap-derived configuration, counters, interrupt masks/status bits, latched last-TLP captures, error-injection controls, diagnostic selectors, reset commands, reset status, power-gating knobs, SMN index/data windows, scratch registers, DRAM aperture fields, and IOMMU capability-base fields. Some fields are live hardware status (`LC_STATE*`, `LC_STATUS*`, decoder/buffer status, PRBS status, RSMU/SMU status, counter accumulators), while others are configuration or command inputs.

Persistence depends on the ASIC reset domain, PCIe hot/cold reset, NBIO reset, power gating, firmware/BIOS initialization, suspend/resume restore, and explicit AMDGPU writes. The shift/mask macros do not say which fields survive resets, which fields are sticky, or which fields clear on read/write; that must come from the hardware specification and sibling generated default/access metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must stay synchronized with sibling headers such as NBIO 7.0 offset, SMN, and default-value headers. Address metadata names the registers; this file only names the fields inside those registers.

Integration points in AMDGPU include NBIO initialization, PCIe link bring-up and recovery, ASPM/runtime power-management policy, GPU reset and hot-reset handling, interrupt routing and masking, performance/debug tooling, PRBS/link-quality diagnostics, SMU/RSMU mailbox or handshake paths, SMN indirect access through NB config windows, and IOMMU capability/shadow setup. Because many fields mirror standard PCIe concepts, code using them also intersects with the Linux PCI core, PCIe AER/link management, MSI/MSI-X setup elsewhere in the device, power management, and platform firmware configuration.

The SMN index/data definitions are especially sensitive integration points because they describe indirect access windows and mutex bits. Any caller using those windows must coordinate ownership and preserve the unlock/mutex protocol rather than treating index/data writes as independent ordinary registers.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while programming the wrong hardware bit, causing link-training failures, incorrect speed/width negotiation, broken ASPM/L1-substate behavior, missed interrupts, bad reset sequencing, or misleading diagnostics.
- This range starts and ends on chunk boundaries that split logical groups. `BIFP6_PCIEP_ERROR_INJECT_TRANSACTION` begins before line 73205, and the next PCIe shadow address block begins after line 75613. Whole-file research must reconcile those adjacent chunks before treating either boundary group as complete.
- Link-controller fields are timing- and state-machine-sensitive. Writes that reset links, force speed changes, alter equalization, change FTS counts, or override lane controls need ordering, timeouts, and recovery paths.
- Status, mask, and control registers often share similar bit names. Accidentally using a status mask against a control register, or vice versa, can silently change semantics because the constants have compatible integer types.
- Full-width masks such as `0xFFFFFFFFL` appear for captured TLP dwords, counters, scratch registers, SMN index/data windows, and IOMMU high-base fields. Writers still need to respect ownership and side effects; a full mask is not permission for arbitrary writes.
- PRBS, error injection, captured TLP, performance counter, and debug mux fields are diagnostic surfaces. Leaving them enabled or misconfigured can perturb normal PCIe operation or produce confusing telemetry.
- SMN index/data windows and index-data mutex fields are shared access paths. Missing locking, stale indexes, or failure to release/unlock can corrupt unrelated register accesses.
- Power-gating and RSMU/SMU handshake fields can race with runtime PM, suspend/resume, firmware ownership, and GPU reset flows.
- IOMMU shadow enable/base fields affect how the device exposes or mirrors IOMMU capability information. Incorrect base or enable values can break platform enumeration or DMA-remapping expectations.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing, renamed, or malformed generated symbols referenced by consumers.
- Run generated-header consistency checks: each field should have a coherent `__SHIFT`/`_MASK` pair, masks within a register should not overlap unexpectedly, reserved gaps should match the source register database, and repeated performance-counter or PRBS lane definitions should follow the expected pattern.
- Cross-check this shift/mask segment against sibling NBIO 7.0 address/default headers so every register comment in this chunk maps to a known address and reset/default value.
- On supported hardware, validate cold boot, warm reset, GPU reset, suspend/resume, PCIe link retrain, speed changes, width negotiation, ASPM/L1-substate behavior, and hot-reset/link-disable recovery.
- Exercise diagnostics where available: PRBS bit/error counters, performance counters across all listed clock domains, link-management/LTR interrupt status and masks, NAK counters, captured last-TLP registers, and transaction-layer error injection.
- Trace register writes in reset and power-management paths to verify reserved bits are preserved, status bits are cleared according to their documented access type, and SMN index/data mutex ownership is acquired and released correctly.
- Validate IOMMU shadow values during PCI enumeration or platform bring-up by comparing the decoded enable and base-address fields against expected firmware and IOMMU capability placement.
