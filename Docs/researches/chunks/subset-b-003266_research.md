# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 17301-19738

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for bitfield offsets and masks in PCIe/NBIO configuration registers, mainly for `BIFPLR0` and `BIFPLR1` PCIe root/port register images. The matching register addresses live in `nbio_7_7_0_offset.h`; this file only describes how to extract or insert fields inside those registers.

The range starts in the middle of the `BIFPLR0_LANE_6_MARGINING_LANE_CNTL` group and continues through the tail of `BIFPLR0` PCIe margining, CCIX, and ESM-related fields. It then enters the `nbio_pcie0_bifplr1_cfgdecp` address block and covers most of the `BIFPLR1` conventional PCI header, PCIe capability, MSI, vendor-specific, virtual-channel, AER, DPC, ESM, DLF, 16 GT/s PHY, and margining capability definitions. The range ends after the shift definitions for `BIFPLR1_LANE_13_MARGINING_LANE_CNTL`; that register's masks and the following lane status groups are outside this chunk.

## Major Register Groups

The initial `BIFPLR0` portion completes lane margining and high-speed link capability definitions for the first PCIe port block. It includes lane 6 through lane 15 margining control/status fields, each with receiver-number, margin-type, usage-model, and margin-payload bit definitions. It also defines `BIFPLR0_PCIE_CCIX_*` capability headers and controls, CCIX ESM required/optional capability and status fields, per-lane 20 GT/s and 25 GT/s equalization control fields, and a CCIX transfer capability bit.

The `BIFPLR1` block begins with conventional PCI configuration-space fields: vendor/device IDs, command/status, revision and class-code bytes, cache line, latency, header, BIST, BAR placeholders, bridge bus/window registers, secondary status, capability pointer, interrupt line/pin, bridge control, vendor capability list, adapter ID, and power-management capability/status-control fields.

The main PCIe capability definitions cover capability-list metadata, PCIe capability version/type/slot/interrupt message fields, Device Control/Status, Link Capability/Status, Slot Capability/Control/Status, Root Control/Capability/Status, Device Control 2, Device Status 2, Link Status 2, and second-generation slot fields. These fields describe PCIe error reporting enables, payload/read request sizing, relaxed/no-snoop behavior, completion timeout policy, ARI/atomic/IDO/LTR/OBFF controls, negotiated link speed and width, slot power/attention/presence indicators, and root error reporting status.

Interrupt and identity capability groups include MSI capability list/control and message-address fields, SSID, MSI map capability/list, AMD vendor-specific enhanced capability headers, and vendor-specific payload words. Virtual-channel fields define port VC capabilities, VC arbitration/TC mapping controls, and VC0/VC1 resource capability/control/status registers. Device serial number fields provide the two serial-number dwords and enhanced capability header.

RAS and PCIe error-reporting groups cover AER enhanced capability list/header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, root error command/source ID, and TLP prefix logs. DPC and root-port PIO groups define Downstream Port Containment capability/status/error source fields plus PIO status, mask, severity, system-error, exception, header-log, and prefix-log registers.

Late PCIe feature groups include Secondary PCIe enhanced capability and lane error status, per-lane equalization controls for lanes 0 through 15, ACS capability header, multicast capability/control/address/receive/block/overlay BAR fields, LTR capability, ARI capability/control, ESM capability list/headers/status/control, ESM supported-data-rate bitmaps, Data Link Feature capability/status, 16 GT/s PHY capability/link/parity/equalization fields, and PCIe margining capability/status plus per-lane margining controls/status for lanes 0 through 12 and the start of lane 13 control.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. Its exported interface is the generated macro namespace:

- `BIFPLR0_*__<FIELD>__SHIFT` and `BIFPLR1_*__<FIELD>__SHIFT` give the bit position for a field.
- `BIFPLR0_*__<FIELD>_MASK` and `BIFPLR1_*__<FIELD>_MASK` give the field mask within the containing register.

The chunk contains 2,164 `#define` entries. Consumers combine these constants with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, raw mask/shift operations, and SOC15 or PCIe-port read/write helpers. The local NBIO 7.7 implementation in `amdgpu/nbio_v7_7.c` includes both `nbio_7_7_0_offset.h` and this header, then uses generated mask names with `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT` for ASIC-specific register programming.

## Control Flow

This header has no executable control flow. The runtime flow belongs to the code that includes it:

1. Detect an NBIO 7.7.0 ASIC path and include the generated NBIO offset and shift/mask headers.
2. Select the desired `BIFPLR0` or `BIFPLR1` register address from the paired offset header.
3. Read the hardware register through the appropriate SOC15, PCIe, or PCIe-port accessor.
4. Decode fields with the `*_MASK` and `*__SHIFT` macros, or update writable fields with read-modify-write helpers.
5. Preserve reserved and unrelated bits unless the hardware specification explicitly says otherwise.

The hardware flows represented by this chunk include PCI command enablement, bridge decode and bus-window state, PCIe error reporting, link capability/status reporting, slot/root status, MSI metadata, virtual channel resource control, AER/DPC fault capture and masking, LTR/ARI/multicast capabilities, ESM data-rate capability and enablement, 16 GT/s link equalization, and PCIe lane margining.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of register layout.

The state described by these macros lives in hardware PCIe/NBIO configuration registers. Identity and capability fields such as vendor/device ID, class code, capability IDs, version fields, supported link speed/width, ESM supported rates, Data Link Feature capabilities, and margining capability bits are generally hardware- or firmware-defined. Control fields such as `COMMAND`, `DEVICE_CNTL`, `DEVICE_CNTL2`, `SLOT_CNTL`, `ROOT_CNTL`, VC resource controls, AER masks/severity policy, DPC controls, ESM control, and margining lane control are writable hardware state whose lifetime depends on PCIe reset, GPU reset, FLR, suspend/resume, and power-gating domains.

Status fields such as PCI status, Device Status, Link Status, Slot Status, Root Status, AER status, correctable/uncorrectable error logs, DPC status, RP PIO status, ESM status, 16 GT/s parity mismatch, lane error status, and margining lane status are live hardware observations. This header does not encode reset defaults, access width, read-only/write-only attributes, write-one-to-clear semantics, sticky/latching behavior, or side effects on read.

## Dependencies And Integration Points

These definitions must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`. A field macro such as `BIFPLR1_PCIE_UNCORR_ERR_STATUS__CPL_TIMEOUT_STATUS_MASK` is meaningful only when paired with the matching NBIO 7.7 register offset for `BIFPLR1_PCIE_UNCORR_ERR_STATUS`.

Primary integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this header for NBIO 7.7 register field programming.
- SOC15 register access paths that use generated NBIO register names and masks to initialize doorbells, HDP flush registers, interrupt behavior, memory-controller access, revision identification, and related NBIO state.
- PCIe diagnostics and link-management paths that decode Device/Link/Slot/Root capability and status fields, equalization state, negotiated speed/width, ESM capability, and margining data.
- RAS/AER/DPC handling that decodes and clears PCIe error status, masks, severity bits, header logs, prefix logs, DPC trigger status, and root-port PIO fault details.
- Interrupt setup and virtualization-adjacent paths that inspect MSI metadata, SSID, MSI map, vendor capabilities, virtual channels, ARI, ACS, multicast, and LTR support.
- Generated-register tooling and merge lanes that must reconcile this chunk with adjacent chunks because the source range begins and ends inside logical register groups.

## Risks

The main risk is silent hardware misprogramming if generated masks or shifts are wrong, stale, truncated by a chunk boundary, or paired with an offset from the wrong ASIC/register block. A one-bit error can enable the wrong PCI command feature, misreport link state, suppress or escalate the wrong AER condition, corrupt virtual-channel routing, alter ESM behavior, or issue the wrong PCIe margining request.

The chunk boundary is a specific documentation risk. `BIFPLR0_LANE_6_MARGINING_LANE_CNTL` starts one line before this range, and `BIFPLR1_LANE_13_MARGINING_LANE_CNTL` continues after it. Any per-file synthesis must merge adjacent chunk research before treating those two register groups as complete.

Repeated lane definitions are easy to copy incorrectly. Lane margining and equalization macros differ mostly by lane number and port prefix (`BIFPLR0` versus `BIFPLR1`), so consumers can compile while targeting the wrong lane or the wrong PCIe port block. The same applies to repeated ESM rate bitmap fields, where each bit maps to a narrow data-rate increment.

Reserved or status-looking fields should not be treated as ordinary writable state. The generated header exposes masks for many hardware-defined bits but does not specify which bits are reserved, read-only, sticky, write-one-to-clear, write-one-to-set, or cleared by reset. Error-status and log registers are especially sensitive because an incorrect write can lose fault evidence or leave interrupts asserted.

Access width and addressing mode also matter. These macros mix conventional PCI 8/16-bit concepts, 32-bit PCIe capability registers, and NBIO/SOC15 register access naming. Consumers must use the access width and indexed-port path expected by surrounding AMDGPU code and hardware documentation.

## Test Signals

Useful validation signals include:

- The AMDGPU tree builds with `nbio_v7_7.c` including `nbio_7_7_0_sh_mask.h`, proving referenced generated names resolve.
- Generator or static checks confirm every register group in this chunk has matching offset/base-index definitions in `nbio_7_7_0_offset.h`.
- Hardware PCIe enumeration on an NBIO 7.7.0 ASIC reports plausible `BIFPLR1` vendor/device/class, command/status, bridge window, capability-list, MSI, PCIe, VC, AER, DPC, LTR, ARI, ESM, DLF, PHY 16 GT/s, and margining capability data.
- Link diagnostics decode negotiated speed/width, link training state, equalization completion, 16 GT/s parity mismatch, ESM-supported rates, and lane margining status consistently with hardware documentation.
- AER/RAS or fault-injection tests observe expected uncorrectable/correctable error bits, masks, severity policy, header logs, prefix logs, root error source IDs, DPC trigger/source fields, and RP PIO status.
- Runtime reset testing across FLR, GPU reset, suspend/resume, and power-management transitions verifies higher-level driver code restores writable controls rather than relying on this header for defaults.
- Targeted lane tests verify that lane 0 through lane 15 equalization and margining accesses do not cross-program neighboring lanes or confuse `BIFPLR0` and `BIFPLR1` namespaces.
