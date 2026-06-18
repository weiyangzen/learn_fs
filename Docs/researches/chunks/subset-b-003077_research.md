# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 22049-24433

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register field header. It provides C preprocessor constants for bit shifts and bit masks used to decode or update PCIe/NBIO configuration-space registers. The range starts in the middle of `BIFPLR3_0_PCIE_ESM_CAP_1`, completes the `BIFPLR3_0_PCIE_ESM_CAP_2` through `CAP_7` field maps, defines the full `nbio_pcie0_bifplr4_cfgdecp` address block, and begins the `nbio_pcie0_bifplr5_cfgdecp` address block through `BIFPLR5_0_IRQ_BRIDGE_CNTL`.

The header has no executable code. Its purpose is to be a stable hardware contract for AMDGPU C code that uses register access helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET` together with matching `reg...` address definitions from the NBIO offset headers.

## Macro API Surface

Every field is represented as two macros:

- `<register>__<field>__SHIFT`: the least-significant bit position for the field.
- `<register>__<field>_MASK`: the bit mask already positioned in the register word.

The naming style is important because AMDGPU helper macros concatenate `reg` and `field` tokens. Any rename, spelling change, or mask/shift mismatch breaks compile-time expansion or silently targets the wrong hardware bits.

The visible register families in this chunk are:

- `BIFPLR3_0_PCIE_ESM_CAP_2` through `BIFPLR3_0_PCIE_ESM_CAP_7`: supported ESM data-rate bitmap fields for bridge/root-port instance 3. The chunk begins with the tail of `CAP_1` masks for `ESM_9P7G` through `ESM_10P9G`; nearby context shows `CAP_1` starts at `ESM_8P0G`.
- `BIFPLR4_0_*`: a full PCI/PCIe root-port/bridge configuration decode block for instance 4, including conventional PCI header fields, PCI PM capability, PCIe capability, MSI and subsystem IDs, vendor-specific and virtual-channel extended capabilities, AER, secondary PCIe, lane equalization, ACS, multicast, L1 PM substate, DPC, RP PIO error logging, and ESM capability fields.
- `BIFPLR5_0_*`: the start of the same configuration decode pattern for instance 5, covering vendor/device IDs, command/status, class/revision/header/BIST, bridge bus and window registers, capability pointer, interrupt line/pin, and bridge control.

## Important Register Groups

The BIFPLR3 and BIFPLR4 ESM groups expose a bitmap of link data rates. `PCIE_ESM_CAP_LIST`, `HEADER_1`, `HEADER_2`, `STATUS`, and `CTRL` describe an extended-speed-mode capability: vendor/capability metadata, minimum electrical-idle time, selected Gen3 and Gen4 ESM data rates, and the enable bit. `PCIE_ESM_CAP_1` through `CAP_7` then map individual 0.1 GT/s-style rate buckets from `ESM_8P0G` up to `ESM_28P0G`.

The conventional PCI bridge header fields for BIFPLR4 and BIFPLR5 include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class-code bytes, cache-line/latency/header/BIST bytes, bus-number routing, I/O and memory base/limit windows, prefetchable memory upper/lower windows, capability pointer, interrupt registers, and bridge controls. These fields mirror PCI bridge config-space layout and determine enumeration-visible capabilities and routing windows.

The BIFPLR4 PCI PM and PCIe capability fields include `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot/root registers, and the PCIe capability-2 registers. These masks cover power states, PME signaling, payload/read-request sizes, error-reporting enables, link speed/width, ASPM/clock-management controls, retraining, link status, slot hotplug signals, root PME/error reporting, completion timeout, ARI, AtomicOps, LTR, OBFF, and link-speed-vector information.

The BIFPLR4 MSI/SSID/MSI-map/VSEC/VC groups describe interrupt message routing, subsystem identity, fixed MSI mapping, vendor-specific extended capability scratch registers, and virtual-channel capability/resource controls for VC0 and VC1.

The BIFPLR4 reliability and isolation groups include AER uncorrectable/correctable error status, masks, severity, header and TLP-prefix logs, root-error command/status/source IDs, secondary PCIe lane equalization controls for lanes 0 through 15, ACS capability/control, multicast registers, L1 PM substate capability/control, DPC capability/control/status/source IDs, and RP PIO status/mask/severity/sys-error/exception/header-log/prefix-log fields.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow happens in consumers:

1. A consumer includes `nbio_7_0_sh_mask.h` and the matching offset header.
2. It computes or names a register address, often via SOC15/NBIO register-address macros.
3. It reads a 16-bit or 32-bit register value from MMIO, PCIe indirect space, or config decode space.
4. It extracts a field with `(value & MASK) >> SHIFT` or `REG_GET_FIELD`.
5. For writes, it clears the mask and inserts a shifted field value with `REG_SET_FIELD` or a write-modify helper.

Because these are hardware-field constants, the relevant sequencing constraints are imposed by PCIe/NBIO hardware, not by this header. Fields such as `RETRAIN_LINK`, `SECONDARY_BUS_RESET`, DPC triggers, AER status bits, PME status, MSI enable, and ESM enable are especially order-sensitive when used by real driver code.

## State And Persistence Behavior

The header itself stores no state. The state represented by these masks is persistent hardware or PCI configuration state in the GPU/NBIO block:

- PCI bridge configuration fields can persist for the lifetime of device initialization and influence Linux PCI enumeration, BAR/window routing, bus mastering, memory access, SERR/parity reporting, and interrupt routing.
- PCIe capability and link-control fields affect link training, speed, width, equalization, ASPM, clock power management, and error reporting until changed by firmware, the kernel PCI core, or AMDGPU.
- AER, DPC, RP PIO, slot, root, and PME status fields may be latched by hardware and can require write-one-to-clear handling by consumers. The masks do not encode clear semantics, so call sites must know each register's access type.
- ESM capability/status/control fields describe and potentially select extended-speed-mode behavior. Incorrect writes can affect link reach, electrical-idle timing, or link negotiation.

## Dependencies And Integration Points

This file is guarded by `_nbio_7_0_SH_MASK_HEADER` and is included directly by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Those consumers integrate NBIO masks into AMDGPU device bring-up, SOC15 register offset setup, and SMU/power-management code paths.

The field names are coupled to matching register-offset macros in headers such as `nbio_7_0_offset.h` and related NBIO version offset files. For example, BIFPLR ESM and config-decode registers have `regBIFPLR*_...` address macros and `..._BASE_IDX` values that select the correct SOC15 register base.

The helper dependency is mostly macro-level: `REG_GET_FIELD` and `REG_SET_FIELD` in `amdgpu.h` expect the `reg__field_MASK` and `reg__field__SHIFT` naming convention; SOC15 helpers in `soc15_common.h` provide register address calculation; `RREG32_PCIE*` and `WREG32_PCIE*` provide PCIe indirect access paths.

The hardware dependency is the NBIO 7.0 PCIe root-port/register specification. Several BIFPLR4 fields correspond to standardized PCI/PCIe capabilities, but the exact register packing and availability are ASIC-specific and generated here for this AMD block.

## Risks And Edge Cases

The main risk is silent bitfield drift. A wrong mask or shift can compile cleanly while causing the driver to read the wrong status bit or write adjacent control bits. For this chunk, high-impact examples include `COMMAND` access enables, `DEVICE_CNTL` payload/request sizes, `LINK_CNTL` retrain/link-disable bits, AER/DPC status and mask bits, bridge-window base/limit fields, and ESM enable/data-rate fields.

The chunk boundary starts mid-register at `BIFPLR3_0_PCIE_ESM_CAP_1` and ends mid-address-block at `BIFPLR5_0_IRQ_BRIDGE_CNTL`. Any generated-document merge must preserve that this research describes only this partial source range, not the complete file or complete BIFPLR5 block.

Reserved fields are explicitly exposed in some registers, while other registers omit unused bits. Consumers should avoid writing whole literal values based only on these masks unless they preserve unspecified/reserved bits through read-modify-write.

Several status/error registers likely include write-one-to-clear or sticky hardware behavior. This header does not distinguish read-only, read-write, write-one-to-clear, sticky, or strap-derived fields; users need the register spec or established call-site pattern before writing them.

The BIFPLR3/BIFPLR4/BIFPLR5 repetition is mechanical. Copy/paste or generation errors between instances could leave one root-port instance with a divergent field definition. Cross-checking against the generated offset header and sibling NBIO mask headers is useful when debugging instance-specific link behavior.

## Test Signals

There are no unit tests for this header alone. Useful validation signals are build-time and hardware/runtime oriented:

- Compile AMDGPU code that includes `nbio_7_0_sh_mask.h`; token-pasting users fail quickly if macro names are missing or malformed.
- Exercise AMDGPU probe/resume paths on NBIO 7.0 ASICs and verify PCIe link speed/width, bus-master and memory access, BAR/window enumeration, and interrupt routing remain correct.
- Compare decoded values from debugfs, MMIO traces, or PCI config dumps against expected PCI/PCIe fields, especially `LINK_STATUS`, `DEVICE_STATUS`, AER status, DPC status, and ESM status/control.
- Run suspend/resume, hot reset, link retraining, ASPM, AER/DPC injection, and PCIe error-recovery scenarios where these fields are most likely to be read or updated.
- For generated-header maintenance, diff this chunk against the hardware register database and sibling NBIO version headers to catch mask/shift drift before runtime testing.
