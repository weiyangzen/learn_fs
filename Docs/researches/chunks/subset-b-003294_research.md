# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 84946-87341

## Chunk Scope

- Work item: `subset-b-003294`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, lines 84946-87341
- Parent file role: generated AMDGPU NBIO 7.7.0 register shift/mask map.
- Chunk shape: 2,396 source lines with 2,175 `#define` entries and 219 register-group comments. The range starts inside the mask half of `BIF0_SWRST_COMMAND_0` and ends after `BIFPLR0_1_PCIE_RP_PIO_SEVERITY`, immediately before the next `BIFPLR0_1_PCIE_RP_PIO_SYSERROR` group.

This is generated hardware ABI data, not executable driver logic. It supplies field positions and masks; the paired register addresses and SOC15 base indices live in `nbio_7_7_0_offset.h`.

## Purpose

This chunk describes two major regions of NBIO 7.7.0 hardware state.

The first region is `BIF0` control and diagnostics. It covers software-reset command/control fields, reset read/auto/write enable policy, endpoint reset controls, clock/power-management controls, SMU/HP interrupt handoff fields, PCIe RX margining capability/settings, presence-detect routing, TX tracking and last-TLP capture, TX power/status/attribute controls, master credit/tag/payload behavior, master error policy, HIP aperture registers, SMU fenced registers, and per-TXCLK performance counter controls for TX clocks 7 through 10.

The second region begins at `addressBlock: nbio_pcie1_bifplr0_cfgdecp` and defines bitfields for the `BIFPLR0_1` PCIe logical-root-port configuration image. It starts with the standard PCI bridge header and continues through PM, PCIe device/link/slot/root capabilities, MSI, subsystem ID, MSI mapping, vendor-specific capability, virtual-channel resources, device serial number, Advanced Error Reporting, secondary PCIe/lane equalization, ACS, multicast, L1 PM substates, Downstream Port Containment, and root-port PIO status/mask/severity fields.

## Important APIs, Types, And Functions

There are no functions, structs, enums, variables, or callable APIs in this range. The exported surface is the generated macro namespace:

- `BIF0_<REGISTER>__<FIELD>__SHIFT` and `BIF0_<REGISTER>__<FIELD>_MASK` define field positions and masks for NBIO BIF0 control/status registers.
- `BIFPLR0_1_<REGISTER>__<FIELD>__SHIFT` and `BIFPLR0_1_<REGISTER>__<FIELD>_MASK` define field positions and masks for PCIe logical-root-port config-space registers.
- Whole-register fields use full-width masks, for example last-TLP dwords, TX tracking high address, vendor scratch dwords, device serial number dwords, AER header logs, TLP prefix logs, and multicast receive/block bitmaps.
- Narrow PCI configuration fields use byte/word masks even though the generated symbols are C constants, for example vendor/device ID, command/status, class/revision, interrupt line/pin, PM status/control, MSI message control, and PCIe capability words.

The chunk is intentionally repetitive. PCS reset lanes 0-15, ports A-P, VC0/VC1 resources, AER status/mask/severity families, equalization lanes 0-15, and root-port PIO status/mask/severity families all share layout templates with different prefixes.

## Major Register Families

The reset groups start with the tail of `BIF0_SWRST_COMMAND_0` and then cover `BIF0_SWRST_COMMAND_1`. They expose reset assertions for port configuration blocks, BIF0 global/calibration/core/register/PHY/sticky/config/SDP-credit domains, PCS reset bits 0-15, AXI master/slave/internal blocks, PCFG, lane control, monitor, halt, CPM, PHY0, clock switching, and strap toggle.

`BIF0_SWRST_CONTROL_0` through `BIF0_SWRST_CONTROL_6` describe reset-control policy. The repeated suffixes map to read-control enable (`RCEN`), auto-trigger enable (`ATEN`), write-reset enable (`WREN` / `WRRESETEN`), write-enable controls, and reset-status fields. These fields determine whether software can observe, trigger, or write reset state for the same port, BIF0-wide, PCS, AXI, PCFG, lane-control, monitor, halt, CPM, PHY, and strap-valid domains.

`BIF0_SWRST_EP_COMMAND_0` and `BIF0_SWRST_EP_CONTROL_0` provide endpoint-oriented global reset and read/write/auto-enable fields for global, calibration, core, register, PHY, sticky, config, and SDP-credit reset behavior.

The CPM and local-clock groups include `BIF0_CPM_CONTROL`, `BIF0_CPM_SPLIT_CONTROL`, `BIF0_CPM_CONTROL_EXT`, `BIF0_LNCNT_CONTROL`, `BIF0_PCIE_PGMST_CNTL`, `BIF0_PCIE_PGSLV_CNTL`, `BIF0_LC_CPM_CONTROL_0`, and `BIF0_LC_CPM_CONTROL_1`. They describe dynamic/static clock gating, TXCLK sleep/debounce timing, delay-gate bypass, master/slave clock requests, snoop responses, memory light/deep/shutdown enables, lane-count control, auto-lane-disable, and per-port TXCLK/RXP clock gating across ports A-P.

The SMU/interrupt and diagnostic groups include `BIF0_SMN_APERTURE_ID_A/B`, `BIF0_SMU_HP_STATUS_UPDATE`, `BIF0_HP_SMU_COMMAND_UPDATE`, `BIF0_SMU_HP_END_OF_INTERRUPT`, `BIF0_SMU_INT_PIN_SHARING_PORT_INDICATOR`, `BIF0_SMU_INT_PIN_SHARING_PORT_INDICATOR_TWO`, `BIF0_SMU_PCIE_FENCED1_REG`, and `BIF0_SMU_PCIE_FENCED2_REG`. They support SMN aperture identification, high-priority SMU command/status updates, EOI signaling, interrupt-status sharing for DPC/presence-detect style port events, and fenced SMU-visible PCIe register payloads.

The PCIe link/test and transaction groups include RX margining capability/settings, presence-detect select, LC debug lane enable, last transmitted TLP capture, TX tracking address/control/status, TX power controls, TX idle/credit status, F0/SWUS TLP attribute overrides, bandwidth-by-unit-id selection, master credit controls, payload/read-request/tag overrides, error egress-blocking and parity policy, HIP aperture registers, and performance counter controls/counts for TXCLK7 through TXCLK10.

The `BIFPLR0_1` root-port block begins with conventional PCI bridge identity and header fields: vendor/device ID, command/status, revision and class code, cache-line/latency/header/BIST, bus numbering, I/O and memory windows, prefetchable windows, ROM BAR, interrupt line/pin, extended bridge control, vendor capability, and adapter/subsystem ID.

The PCIe capability groups cover PM capability/status, PCIe capability metadata, Device Capability/Control/Status, Link Capability/Control/Status, Slot Capability/Control/Status, Root Control/Capability/Status, Device/Link/Slot Capability 2 and Control 2/Status 2, MSI, SSID, MSI-map, vendor-specific enhanced capability, VC port and VC0/VC1 resource controls, device serial number, AER status/mask/severity/capability/log/root-error/source-ID fields, secondary PCIe link control 3, lane-error status, and lane equalization control for lanes 0-15.

The final root-port enhanced capability groups cover ACS capability/control, multicast capability/control/address/receive/block/overlay fields, L1 PM substate capability/control/timing fields, Downstream Port Containment capability/control/status/error-source fields, and RP PIO status/mask/severity for unsupported request, completer abort, and completion timeout events across config, I/O, and memory transaction classes.

## Control Flow

This header has no runtime control flow. Runtime flow is supplied by AMDGPU and PCIe/NBIO code that includes this generated header:

1. The NBIO 7.7.0 implementation includes `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`.
2. Code selects a register offset macro from the offset header and a field shift/mask macro from this header.
3. Register access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, or PCIe-port accessors compute and perform the hardware read/write.
4. Field extraction and insertion use the generated masks and shifts, often through AMDGPU helper macros such as `REG_SET_FIELD`.
5. Hardware executes the resulting reset, gating, link, error-reporting, interrupt, or PCIe configuration behavior.

The main operational flows represented by this chunk are reset sequencing, clock/power gating, SMU/NBIO event reporting, PCIe link training and margining, PCIe transaction credit/tag/payload policy, error reporting and containment, MSI programming, virtual-channel negotiation, ACS/multicast routing policy, L1 PM substate programming, DPC handling, and root-port PIO error diagnosis.

## State And Persistence

The header itself is stateless. It allocates no memory, performs no I/O, and stores no persistent data. It is a compile-time description of fields in hardware registers.

The described hardware state includes writable control bits, read-only capability bits, sticky status/log bits, and policy fields:

- Reset state and reset access policy for ports, PCS lanes, AXI-side blocks, BIF0-wide reset domains, PHY/sticky/config domains, and endpoint-global domains.
- Clock and power-management state for BIF0 CPM, LC CPM, TX clock gating, master/slave memory low-power modes, and lane-count control.
- SMU-visible handoff and interrupt state, including high-priority command/status updates, EOI, port interrupt sharing, and fenced PCIe status payloads.
- PCIe diagnostics such as RX margining capabilities/settings, debug-lane selection, last-TLP logs, TX tracking status, TX queue/credit readiness, performance counter selects and counts, and HIP apertures.
- Root-port configuration and live PCIe state for bridge windows, bus numbers, PM/PME, MSI, PCIe device/link/slot/root controls, VC mapping, AER logs, lane equalization, ACS, multicast, L1 PM substates, DPC, and RP PIO errors.

Persistence across suspend/resume, hot reset, FLR, GPU reset, BACO, or power-gated transitions is not encoded in this file. Some fields are likely reset by hardware resets or power transitions; others may be sticky until explicitly cleared by a write-one-to-clear or similar policy. The macros do not indicate read-only/write-only semantics, reset defaults, side effects, access width, or clear behavior.

## Dependencies And Integration Points

The required companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which names the register offsets and base indices that correspond to these field layouts. Field masks from this chunk are not sufficient without the correct `reg...` address from the offset header.

The direct source-tree include found for this generated header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`. That implementation includes both NBIO 7.7.0 generated headers and uses generated register fields for NBIO operations such as HDP remapping, revision-ID reads, framebuffer access control, memory-size reads, doorbell range/aperture setup, interrupt control, and PCIe/RSMU index/data offset access.

The specific macro groups in this chunk integrate with:

- AMDGPU SOC15 register access infrastructure and field helpers.
- NBIO 7.7.0 reset, clock-gating, power-management, interrupt, SMU, and diagnostics paths.
- PCIe root-port configuration and Linux PCI/PCIe expectations for bridge headers, capability lists, MSI, AER, ACS, VC, L1 PM substates, DPC, hotplug/presence detect, and link state.
- RAS, fault-injection, or debug paths that decode AER, DPC, RP PIO, last-TLP, TX tracking, lane error, and performance-counter fields.
- Hardware validation tools that compare generated NBIO register layouts against ASIC register specifications.

## Risks And Edge Cases

- Chunk boundaries split complete register groups. Lines 84946-84960 contain only part of `BIF0_SWRST_COMMAND_0`; the corresponding shifts and earlier port masks are in the previous chunk. The next group after line 87341 is `BIFPLR0_1_PCIE_RP_PIO_SYSERROR`, so RP PIO status/mask/severity are visible here but the related system-error policy continues outside the range.
- Generated names are highly repetitive. Mixing `COMMAND`, `CONTROL_0`, `CONTROL_2`, and `CONTROL_4`, or `RCEN`, `ATEN`, and `WREN` fields, can compile while changing reset-observation, auto-reset, or write-enable behavior instead of the intended reset assertion.
- Reset and power-gating fields are hardware-critical. Incorrect masks can wedge PCIe/NBIO fabric blocks, leave PHY/PCS/AXI domains in reset, disable clocking needed for MMIO access, or break resume/reset sequencing.
- Many BIF0 TX and master-control fields affect protocol ordering, tags, payload/read-request sizing, credits, egress blocking, relaxed ordering, no-snoop, and poison/prefix/atomic handling. Bad writes can cause data corruption, PCIe completion failures, performance collapse, or hard-to-debug bus errors.
- PCIe status and error fields may be sticky or write-one-to-clear. This header does not encode clear semantics, so generic read-modify-write code can accidentally clear AER, DPC, RP PIO, device-status, slot-status, or root-status evidence.
- Capability fields and reserved fields are not automatically writable. A generated mask for a `RESERVED` or capability field must not be treated as permission to write that bit.
- `BIFPLR0_1` names describe the PCIe1 logical root-port 0 image. Copying fields from similar `BIFPLR0_0`, `BIFPLR1_0`, or endpoint blocks can target the wrong root port or function image.
- Lane and port fields repeat across lanes 0-15 and ports A-P. Off-by-one lane or port use can corrupt link-training diagnostics or clock-gating state while leaving adjacent code syntactically correct.
- MSI, ACS, VC, multicast, and bridge-window controls affect interrupt delivery, isolation, routing, and enumeration. Misprogramming these fields can cause security/isolation problems, device enumeration failures, or lost interrupts.
- DPC and RP PIO fields are containment and diagnosis critical. Incorrect masks can suppress containment, misreport trigger reason/source ID, or make firmware/driver logs point at the wrong transaction class.

## Test And Validation Signals

Useful validation is mostly generated-data, build, and hardware integration coverage:

- Build AMDGPU with NBIO 7.7.0 support so `amdgpu/nbio_v7_7.c` resolves the generated offset and shift/mask headers.
- Static generated-header checks should confirm that complete register groups have paired `__SHIFT` and `_MASK` macros, while allowing the documented boundary splits for `BIF0_SWRST_COMMAND_0` and the following RP PIO system-error group.
- Cross-check this chunk against `nbio_7_7_0_offset.h` so every complete `BIF0_*` and `BIFPLR0_1_*` field group has a matching register offset/base-index definition.
- Compare repeated reset-control templates, lane templates, port A-P templates, VC0/VC1 templates, AER status/mask/severity templates, and RP PIO status/mask/severity templates for structural symmetry and expected mask values.
- Runtime smoke tests on matching hardware should cover GPU probe, NBIO reset/resume, PCIe link bring-up, doorbell and interrupt setup, SMU event paths, and suspend/resume or BACO-style power transitions.
- PCIe link tests should decode link speed/width/training state, equalization phase state for lanes 0-15, L1 PM substate timing, RX margining settings, presence-detect events, and DL-active indicators.
- RAS/error tests should exercise AER correctable/uncorrectable status, masks, severity, header logs, TLP prefix logs, DPC trigger/status/source-ID handling, and RP PIO status/mask/severity decoding.
- MSI and hotplug/presence tests should validate MSI address/data/control programming, interrupt pin/line reporting, slot control/status, presence-detect selection, SMU interrupt-sharing indicators, and EOI behavior.
- Performance/debug tests should validate TX last-TLP capture, TX tracking valid/status fields, TX queue/credit idle status, bandwidth-by-unit-ID selection, and TXCLK7-10 performance counter controls/counts.

## Notes For Merge/Reconciliation

This document is only the chunk research note for `subset-b-003294`. The final per-file report should be produced later by the merge lane after adjacent chunks for `nbio_7_7_0_sh_mask.h` are available.

The merge lane should preserve that this range is one generated shift/mask slice, not a standalone API implementation. It should combine the boundary context from the previous chunk for complete `BIF0_SWRST_COMMAND_0` coverage and from the next chunk for the rest of the RP PIO policy groups that follow `BIFPLR0_1_PCIE_RP_PIO_SEVERITY`.
