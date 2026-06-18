# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 87342-89760

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It exports bit positions and bit masks for PCIe/NBIO configuration registers; it does not contain executable driver logic. Register addresses and base indices are supplied by the paired `nbio_7_7_0_offset.h` header, while this file supplies the field layout used by register helper macros.

The range begins in the `BIFPLR0_1` PCIe root-port block after the preceding chunk's DPC/RP PIO status, mask, and severity definitions. It covers the remaining RP PIO system-error/exception/log fields, ESM capability fields, data-link feature capability, 16 GT/s PHY/link fields, 16-lane 16 GT/s equalization controls, lane margining controls/status, CCIX/ESM-related capability fields, 20 GT/s and 25 GT/s lane preset tables, and 32 GT/s link capability/control/status fields. It then switches at `addressBlock: nbio_pcie1_bifplr1_cfgdecp` into the `BIFPLR1_1` PCIe root-port configuration-space image and defines the conventional PCI bridge header, PM capability, PCIe capability, MSI, SSID/MSI mapping, vendor-specific and VC enhanced capabilities, AER, secondary PCIe, lane equalization, ACS, and the start of multicast capability fields.

The chunk contains 2,165 `#define` entries, made up of 1,083 `__SHIFT` constants and 1,110 `_MASK` constants, plus register comments and one address-block marker. It is generated hardware ABI material: the names and numeric constants are the public interface.

## Major Register Groups

### BIFPLR0_1 error logging and ESM/link features

The first `BIFPLR0_1` section completes PCIe Downstream Port Containment/root-port PIO error handling:

- `PCIE_RP_PIO_SYSERROR` and `PCIE_RP_PIO_EXCEPTION` expose the same config, I/O, and memory completion-error classes used by the adjacent status/mask/severity registers: unsupported request completion, completer-abort completion, and completion timeout.
- `PCIE_RP_PIO_HDR_LOG0..3` and `PCIE_RP_PIO_PREFIX_LOG0..3` provide full-register TLP header and prefix log masks for captured failed transactions.

The next group defines ESM and higher-speed link capabilities:

- `PCIE_ESM_CAP_LIST`, `PCIE_ESM_HEADER_1`, `PCIE_ESM_HEADER_2`, `PCIE_ESM_STATUS`, and `PCIE_ESM_CTRL` describe the ESM enhanced capability header, timing/status fields, Gen3/Gen4 data-rate selectors, and enable state.
- `PCIE_ESM_CAP_1..7` advertise fine-grained supported data rates. The masks enumerate decimal GT/s-style names from `ESM_8P0G` through `ESM_32P0G` across seven capability words.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` define data-link feature capability/status fields such as local exchange support, exchange enable, data-link feature valid, and remote feature support.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, `RTM2_PARITY_MISMATCH_STATUS_16GT`, and `LANE_0..15_EQUALIZATION_CNTL_16GT` describe 16 GT/s link capability, link control/status, parity mismatch status, and per-lane downstream/upstream transmit presets.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0..15_MARGINING_LANE_CNTL/STATUS` define PCIe lane margining support, per-lane margin commands, payloads, receiver numbers, timing/voltage margin status, and ready/soft-ready reporting.
- `PCIE_CCIX_*`, `ESM_LANE_0..15_EQUALIZATION_CNTL_20GT`, `ESM_LANE_0..15_EQUALIZATION_CNTL_25GT`, `PCIE_CCIX_TRANS_*`, and `LINK_*_32GT` cover CCIX capability/header/status/control fields, required and optional ESM support, per-lane 20 GT/s and 25 GT/s preset controls, translation capability/control, and 32 GT/s link capability/control/status fields.

The paired offset header maps examples from this group at base index 5, including `regBIFPLR0_1_PCIE_RP_PIO_SYSERROR`, `regBIFPLR0_1_PCIE_ESM_CAP_LIST`, `regBIFPLR0_1_PCIE_DLF_ENH_CAP_LIST`, `regBIFPLR0_1_PCIE_PHY_16GT_ENH_CAP_LIST`, `regBIFPLR0_1_PCIE_MARGINING_ENH_CAP_LIST`, `regBIFPLR0_1_PCIE_CCIX_CAP_LIST`, and `regBIFPLR0_1_LINK_CAP_32GT`.

### BIFPLR1_1 PCIe root-port configuration space

The second half starts a new root-port configuration image:

- Basic bridge/configuration registers: vendor/device IDs, command/status, revision and class code, cache-line/latency/header/BIST, secondary/subordinate bus numbering, I/O and memory window base/limit registers, prefetchable window upper dwords, capability pointer, ROM base address, interrupt line/pin, extended bridge control, vendor capability list, and adapter ID.
- Power-management capability: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define PM capability ID/version/next pointer, PME support, D1/D2 support, aux-current/DSI fields, current power state, PME enable/status, data select/scale, and B2/B3 support.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, `ROOT_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and slot capability/control/status 2 fields. These cover payload/read-request sizes, error enables, relaxed ordering/no-snoop, FLR, link speed/width, ASPM and retraining, slot/hotplug state, root error/PME handling, completion timeout ranges, ARI/atomic/TPH/LTR/OBFF related feature bits, target link speed, equalization controls, and equalization status.
- Interrupt and identity fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI message address/data registers, `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, and `MSI_MAP_CAP`.
- PCIe extended capabilities: vendor-specific capability header/data, virtual-channel capability/control/status for VC0 and VC1, device serial number, AER status/mask/severity/control/log/root-error/source-ID fields, TLP prefix logs, secondary PCIe capability, Link Control 3, lane error status, and 8 GT/s lane equalization controls for lanes 0-15.
- ACS and multicast start: `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define access-control capability and enable bits. The chunk ends at the start of `PCIE_MC_CAP`, after its `MC_MAX_GROUP` shift; the rest of multicast capability/control/register masks are in the next chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, globals, or callable APIs in this range. The exported interface is a generated macro namespace:

- `BIFPLR0_1_<REGISTER>__<FIELD>__SHIFT` and `BIFPLR1_1_<REGISTER>__<FIELD>__SHIFT` give the zero-based bit position for a field.
- `BIFPLR0_1_<REGISTER>__<FIELD>_MASK` and `BIFPLR1_1_<REGISTER>__<FIELD>_MASK` give the field mask in the register word.

These constants are intended to be paired with `regBIFPLR0_1_*` and `regBIFPLR1_1_*` offset macros from `nbio_7_7_0_offset.h`. AMDGPU code includes this generated header from `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, and similar generated register maps are normally consumed through helpers such as field set/get macros and SOC15/NBIO register read/write paths. The macros are untyped integer constants, so the compiler cannot enforce that a `BIFPLR0_1` mask is applied only to a `BIFPLR0_1` register value, or that a 16 GT/s lane field is not used with an 8 GT/s equalization register.

## Control Flow

This header has no executable control flow. Runtime behavior appears in consumers that include the NBIO 7.7.0 register headers:

1. Select the correct NBIO 7.7.0 register offset and base index from `nbio_7_7_0_offset.h`.
2. Read a PCIe/NBIO configuration register through the AMDGPU register access path.
3. Decode fields by applying this chunk's `_MASK` constants and shifting by the matching `__SHIFT` constants.
4. For writable controls, preserve unrelated bits, insert the shifted field value, and write the register back through the same register access path.
5. For command/status sequences, poll or snapshot status/log registers according to hardware semantics.

The hardware state machines implied by the fields include root-port PIO error capture, DPC/AER/root-error reporting, ESM data-rate advertisement and enablement, data-link feature exchange, 16 GT/s/20 GT/s/25 GT/s/32 GT/s link equalization and status reporting, lane margining command/status exchange, CCIX capability reporting, PCI bridge window configuration, link retraining, hotplug/slot event reporting, MSI delivery, virtual-channel configuration, and ACS traffic isolation.

## State And Persistence

The header itself is stateless and persists nothing. It is a compile-time description of register bit layouts.

The state described by the masks lives in hardware PCIe configuration or NBIO registers. Capability fields such as capability IDs, versions, next pointers, supported link speeds, maximum payload/read-request sizes, ESM data-rate masks, DLF/PHY/margining/CCIX/ACS/AER/VC support, and device serial number are usually hardware- or firmware-defined descriptors. Control fields such as command bits, device/link/root/slot controls, MSI enables, VC controls, AER masks/severity/root-error command, ESM enable/rate control, data-link exchange enable, 16 GT/s and higher-speed link controls, lane margining commands, and ACS enables are writable hardware configuration when the current operating mode permits access.

Status and log fields such as PCI status, device/link/slot/root status, RP PIO system-error/exception, TLP header/prefix logs, ESM status, data-link feature status, 16 GT/s status/parity mismatch, margining lane status, CCIX ESM status, Link Status 2, AER correctable/uncorrectable status, root-error status, lane error status, and multicast fields are live hardware observations. Their reset defaults, read-only/write-only access policy, latching, side effects, and write-one-to-clear behavior are not encoded in this generated header.

Persistence across suspend/resume, GPU reset, hot reset, FLR, and power-domain transitions is determined by the hardware and by higher-level AMDGPU restore paths. The generated constants do not provide reset values or save/restore policy.

## Dependencies And Integration Points

Primary dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which provides matching offsets and base-index constants such as `regBIFPLR0_1_PCIE_RP_PIO_SYSERROR`, `regBIFPLR0_1_PCIE_ESM_CAP_LIST`, `regBIFPLR0_1_LINK_CAP_32GT`, `regBIFPLR1_1_VENDOR_ID`, `regBIFPLR1_1_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `regBIFPLR1_1_PCIE_LANE_15_EQUALIZATION_CNTL`, and `regBIFPLR1_1_PCIE_MC_CAP`.
- AMDGPU NBIO 7.7 support, notably `amdgpu/nbio_v7_7.c`, which includes this shift/mask header and the offset header as the ASIC-specific register map.
- AMDGPU register helper macros and PCIe/NBIO accessors that compose field values with `*_MASK` and `*__SHIFT`.
- PCIe capability semantics for PM, MSI, PCIe device/link/slot/root registers, VC, AER, secondary PCIe, ACS, DLF, lane margining, and high-speed PHY/link controls.

Integration surfaces include PCIe enumeration and diagnostics, root-port bridge-window programming, link training/retraining and equalization diagnostics, lane margining tools, AER/RAS error capture, DPC/RP PIO fault analysis, interrupt setup via MSI, virtual-channel configuration, ACS isolation, power management, and any debug tooling that dumps NBIO register fields by generated name.

## Risks

The main risk is silent hardware misprogramming if these masks are stale, regenerated inconsistently with the offset header, or paired with offsets from another ASIC or another port block. Because these are preprocessor constants, using a `BIFPLR0_1` mask on a `BIFPLR1_1` value, or using an 8 GT/s lane equalization mask on a 16/20/25 GT/s equalization register, compiles but decodes or writes the wrong bits.

Chunk boundaries are important. The requested range starts after `BIFPLR0_1_PCIE_RP_PIO_STATUS`, `BIFPLR0_1_PCIE_RP_PIO_MASK`, and `BIFPLR0_1_PCIE_RP_PIO_SEVERITY`, so a full RP PIO discussion must merge with the preceding chunk. The requested range ends inside `BIFPLR1_1_PCIE_MC_CAP`: only the `MC_MAX_GROUP` shift is present here, while the remaining shifts and all masks for that register continue in the next chunk.

Many fields are status, log, or command/status fields with hardware side effects. AER status, PCI status, RP PIO logs, root-error status, lane error status, parity mismatch status, margining status, and slot/link status fields may latch events or clear on specific write patterns. Generic read/modify/write code must not treat every mask as a safe writable field.

Capability/control naming is easy to confuse. Fields such as `*_CAP`, `*_CNTL`, `*_STATUS`, `*_MASK`, `*_SEVERITY`, and `*_SYSERROR` often repeat the same error names but mean advertised support, enable state, current status, reporting policy, severity policy, or system-error routing. Similar repeated lane tables exist for 8 GT/s, 16 GT/s, 20 GT/s, and 25 GT/s operation.

SR-IOV or virtualized environments may restrict access to host-owned PCIe/NBIO registers. Even though this chunk names root-port bridge, link, ACS, VC, and AER controls, guest drivers may observe read-only, trapped, or filtered access depending on platform policy.

## Test Signals

Useful validation signals for this chunk and its consumers include:

- Kernel/AMDGPU build coverage with NBIO 7.7 enabled, proving that generated names still compile with the ASIC-specific driver code.
- Generator or static comparison against the source register database, checking that every complete register group has paired shift/mask definitions and matching offsets in `nbio_7_7_0_offset.h`.
- PCIe enumeration and debug dumps on matching hardware showing coherent `BIFPLR1_1` vendor/device, class, bridge window, PM, MSI, PCIe, VC, AER, secondary PCIe, ACS, and multicast capability data.
- Link training diagnostics that decode expected negotiated speed/width, target speed, equalization status, lane error status, 16 GT/s parity mismatch status, and per-lane preset values across 8/16/20/25/32 GT/s-related fields.
- Lane margining tests or debug reads that show command-ready/status-ready handshakes and plausible voltage/time margin results for lanes 0-15.
- AER/DPC/RAS fault-injection or platform error-log tests that verify RP PIO status, system-error/exception routing, TLP header/prefix logs, correctable/uncorrectable error status, masks, severity, root-error status, and source IDs decode as expected.
- Suspend/resume, hot reset, FLR, and GPU reset tests confirming that higher-level code restores writable PCIe controls instead of relying on this generated header for defaults.
