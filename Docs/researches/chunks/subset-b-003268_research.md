# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 22180-24629

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It contains C preprocessor constants for extracting and composing bitfields in NBIO/PCIe configuration-space registers. The range is not executable code; it is a hardware register layout contract consumed by AMDGPU register access code after the caller has selected the matching register offset.

The chunk begins in the tail of the `BIFPLR2` root-port block, covering 20 GT and 25 GT Equalization Status Monitoring lane preset fields and the CCIX transition capability. It then starts `// addressBlock: nbio_pcie0_bifplr3_cfgdecp` at line 22310 and covers nearly the full `BIFPLR3` PCI/PCIe root-port configuration image. The last lines enter `// addressBlock: nbio_pcie0_bifplr4_cfgdecp` and only begin the `BIFPLR4_COMMAND` shifts, so the `BIFPLR4` command masks and remaining fields are outside this chunk.

## Major Register Groups

The `BIFPLR2` tail covers per-lane ESM equalization controls:

- `BIFPLR2_ESM_LANE_7_EQUALIZATION_CNTL_20GT` through `BIFPLR2_ESM_LANE_15_EQUALIZATION_CNTL_20GT`.
- `BIFPLR2_ESM_LANE_0_EQUALIZATION_CNTL_25GT` through `BIFPLR2_ESM_LANE_15_EQUALIZATION_CNTL_25GT`.
- `BIFPLR2_PCIE_CCIX_TRANS_CAP`, whose field reports CCIX optimized TLP format support.

The `BIFPLR3` block is the substantive part of the chunk. It defines standard PCI bridge-like fields, including vendor/device IDs, command/status, class code, BIST/header/cache/latency bytes, BAR placeholders, bus-number and bridge-window registers, interrupt line/pin, bridge control, vendor capability, adapter/subsystem IDs, and capability pointers. The command and status fields include IO/memory/bus-master enables, interrupt disable, SERR/parity controls, capability-list presence, interrupt status, and PCI error status bits.

The PCI power-management and PCIe capability groups cover `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot control/status/capability, root control/capability/status, and the PCIe 2.0 device/link/slot control and status registers. These macros encode fields for payload size, read request size, relaxed ordering, no-snoop, error-report enables, FLR, completion timeout, ARI forwarding, AtomicOp, ID-based ordering, LTR, OBFF, target link speed, retraining, ASPM, link disable, negotiated speed/width, data link active, bandwidth notifications, and 8 GT/s equalization status.

Interrupt and identity capabilities include MSI capability/list/address/data fields, SSID capability fields, MSI mapping fields, and AMD vendor-specific enhanced capability headers and payload registers. These are layout definitions for interrupt programming and PCI capability enumeration rather than interrupt handling logic.

RAS and diagnostics are represented by AER and related PCIe enhanced capabilities: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, root error command, error source IDs, TLP prefix logs, secondary PCIe capability, lane error status, and lanes 0-15 secondary PCIe equalization controls. The uncorrectable status family includes completion timeout/abort, unexpected completion, malformed TLP, ECRC, unsupported request, ACS violation, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked bits.

The later `BIFPLR3` enhanced-capability groups cover ACS list metadata, multicast capability/control/address/receive/block/overlay BAR fields, LTR capability, ARI capability/control, DPC capability/status/source, root-port PIO status/mask/severity/system-error/exception/header-log/prefix-log registers, ESM capability headers/status/control/capability bitmaps, Data Link Feature capability/status, 16 GT/s PHY capability/status/parity/equalization fields, lane margining controls/status for lanes 0-15, CCIX capability/header/status/ESM capability fields, and 20 GT/25 GT ESM per-lane transmit preset controls.

The final `BIFPLR4` portion contains only `VENDOR_ID`, `DEVICE_ID`, and the first four `COMMAND` shift definitions (`IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, and `SPECIAL_CYCLE_EN`). Treat this as a chunk boundary, not a complete `BIFPLR4` register group.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. The exported interface is the generated macro namespace:

- `BIFPLR<n>_<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position for a field.
- `BIFPLR<n>_<REGISTER>__<FIELD>_MASK` gives the field mask in the containing register.

The chunk contains 2,158 `#define` entries across 288 register/comment markers. Most repeated lane families use identical local layouts across lane numbers. For example, 20 GT and 25 GT ESM lane registers encode downstream-port and upstream-port TX presets in low and high nibbles (`0x0f` and `0xf0` style masks), while secondary PCIe equalization registers encode downstream TX preset, downstream RX preset hint, upstream TX preset, and upstream RX preset hint in four nibble-sized fields.

These macros are normally paired with the matching offsets in `nbio_7_7_0_offset.h`. Spot checks show corresponding entries such as `cfgBIFPLR2_ESM_LANE_7_EQUALIZATION_CNTL_20GT`, `cfgBIFPLR3_VENDOR_ID`, `cfgBIFPLR3_COMMAND`, `cfgBIFPLR3_PCIE_UNCORR_ERR_STATUS`, `cfgBIFPLR3_PCIE_ESM_CAP_LIST`, `cfgBIFPLR3_ESM_LANE_0_EQUALIZATION_CNTL_20GT`, `cfgBIFPLR3_PCIE_CCIX_TRANS_CAP`, and `cfgBIFPLR4_COMMAND`.

## Control Flow

The header has no executable control flow. Runtime behavior comes from AMDGPU code that includes this header, chooses the NBIO 7.7 register set for the discovered ASIC, reads or writes a register through the appropriate MMIO or PCIe configuration path, and applies these masks and shifts.

A typical consumer flow is:

1. Select a `cfgBIFPLR2_*`, `cfgBIFPLR3_*`, or `cfgBIFPLR4_*` offset from `nbio_7_7_0_offset.h`.
2. Read the hardware register through the NBIO/PCIe indexed access path or another AMDGPU register helper.
3. Decode fields by masking and shifting with the `nbio_7_7_0_sh_mask.h` constants.
4. For writable control fields, preserve unrelated and reserved bits, insert the shifted new value, and write the register back through the same access domain.

The hardware flows represented by this chunk include PCI bridge enumeration, memory and IO decode enablement, bus mastering, interrupt disablement, power-management state, PCIe link training/retraining, link speed/width reporting, payload and completion-timeout policy, AER reporting and masking, DPC containment reporting, root-port PIO exception reporting, ESM speed support and calibration status, lane equalization presets, lane margining commands, multicast routing/filter state, ARI function control, LTR capability reporting, Data Link Feature exchange, and CCIX capability/status reporting.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of field positions.

The state described by the macros lives in hardware configuration registers. Capability and identity fields such as vendor/device IDs, class code, PCIe capability metadata, supported link speeds/widths, 16 GT/20 GT/25 GT lane capabilities, ESM supported-rate bitmaps, CCIX capability bits, multicast capability, and lane margining capability are generally hardware-, firmware-, or strap-defined.

Writable controls include PCI command enables, PCIe device/link/slot controls, MSI/MSI-map controls, AER masks/severity/root error command, DPC controls, root-port PIO masks/severity/system-error routing, ESM control fields, Data Link Feature exchange enable, ARI controls, multicast controls and address/block registers, margining lane controls, CCIX controls, and equalization preset fields. Their lifetime depends on PCIe function reset, FLR, hot reset, GPU reset, suspend/resume, and firmware reinitialization paths.

Status and log fields such as PCI status, Device Status, Link Status, Link Status 2, AER status, AER header logs, TLP prefix logs, DPC status/error source, RP PIO status/header/prefix logs, ESM status/calibration complete, 16 GT equality/parity status, lane margining status, and CCIX ESM status are live hardware observations. This header does not encode reset defaults, access permissions, write-one-to-clear behavior, read side effects, volatility, ordering requirements, or whether a field must be read or written through PCI config space versus an internal NBIO path.

## Dependencies And Integration Points

The direct companion for this file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which supplies register offsets for the field names defined here. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`, exposes `nbio_v7_7_funcs`, and provides NBIO accessors such as PCIe index/data and PCIe port index/data offset hooks. `amdgpu_discovery.c` selects `nbio_v7_7_funcs` for matching hardware discovery data.

Integration points include:

- PCI/PCIe enumeration and bridge setup code that needs vendor/device/class, bridge windows, command/status, capability-list, and interrupt metadata.
- NBIO/PCIe link management and diagnostics that decode link capability/control/status, negotiated speed and width, retrain state, link bandwidth events, 8 GT/s/16 GT/s equalization, and 20 GT/25 GT ESM presets.
- Power-management code that inspects or programs PM capability/status-control fields, ASPM/LTR/OBFF-related controls, and suspend/resume restoration.
- Interrupt setup and validation paths that decode MSI, MSI mapping, interrupt line/pin, and interrupt-disable state.
- RAS and error handling paths that use AER, root error, DPC, RP PIO, TLP header logs, TLP prefix logs, lane error status, and parity mismatch status.
- PCIe advanced feature paths for ACS, multicast, ARI, Data Link Feature exchange, lane margining, ESM, and CCIX.

## Risks

The principal risk is silent hardware misprogramming if a mask or shift is wrong, if this NBIO 7.7 header is paired with offsets from another ASIC generation, or if a caller mixes `BIFPLR2`, `BIFPLR3`, and `BIFPLR4` names. The compiler will not catch a semantically wrong but syntactically valid mask/offset pairing.

The range has chunk-boundary hazards. It starts in the middle of the `BIFPLR2` ESM lane family and ends in the middle of `BIFPLR4_COMMAND`. Final per-file research must merge adjacent chunks before treating those register groups as complete.

Repeated lane and port blocks are easy to review incorrectly. Lane 0-15 equalization, 16 GT presets, margining control/status, 20 GT ESM presets, and 25 GT ESM presets differ mainly by lane number. A generated drift or copy/paste mistake could affect one lane while neighboring lanes look correct at a glance.

Reserved fields and whole-register `RESERVED` masks should not be treated as permission to write those bits. The header only describes bit positions. It does not tell consumers which fields are read-only, write-one-to-clear, write-only, self-clearing, sticky across reset, firmware-owned, or unsafe to modify during active link training.

AER, DPC, RP PIO, and log registers need careful access semantics. Clearing or masking the wrong bit can hide real PCIe errors; reading logs too late can miss fault context; writing severity or system-error routing fields incorrectly can change platform error policy.

## Test Signals

Useful validation signals are mostly build, static consistency, and hardware integration checks:

- The AMDGPU tree builds with `nbio_v7_7.c` including both the 7.7 offset and shift/mask headers.
- Static generation checks confirm every `BIFPLR2_*`, `BIFPLR3_*`, and started `BIFPLR4_*` register in this chunk has a matching `cfg...` offset in `nbio_7_7_0_offset.h` for the same ASIC generation.
- PCIe enumeration on matching AMD hardware reports plausible `BIFPLR3` vendor/device/class, bridge-window, capability-list, MSI, PCIe capability, AER, DPC, ESM, lane margining, and CCIX fields.
- Link-management tests or diagnostics decode expected current speed, negotiated width, retrain state, data link active state, 8 GT/s and 16 GT/s equalization status, and ESM current data rate/calibration completion.
- RAS/AER fault injection or hardware error tests show correct decoding of uncorrectable/correctable statuses, severity/mask fields, root error reporting, source IDs, TLP header logs, TLP prefix logs, DPC status, and RP PIO status/logs.
- Lane-level diagnostics confirm lane 0-15 equalization, margining control/status, and ESM 20 GT/25 GT preset fields address the intended lane and do not cross-program neighboring lane fields.
- Suspend/resume, FLR, hot reset, and GPU reset tests verify that writable PCIe/NBIO controls are restored or reinitialized by higher-level driver paths, since this header does not carry defaults or persistence policy.
