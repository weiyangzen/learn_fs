# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 63823-66205

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It provides C preprocessor constants for bitfield extraction and update across three adjacent register-map regions:

- the tail of `BIFPLR5_1_PCIE_ESM_CAP_3` plus `BIFPLR5_1_PCIE_ESM_CAP_4` through `BIFPLR5_1_PCIE_ESM_CAP_7`;
- the full `nbio_pcie0_bifplr6_cfgdecp` address block, exposed as `BIFPLR6_1_*` PCIe bridge/root-port configuration-space fields;
- the beginning of `nbio_pcie0_bifp0_pciedir_p`, exposed as `BIFP0_*` direct PCIe port control, transmit, receive, flow-control, and error-control fields through the start of receive-credit allocation.

The file is hardware-description data, not executable driver logic. Its purpose is to give AMDGPU NBIO code stable symbolic names for hardware bit positions and masks instead of hard-coded numeric constants. Address headers provide the register offsets; this `*_sh_mask.h` header provides the register field layout.

## Register Families Covered

The opening lines finish the `BIFPLR5_1` Equalization Service/Extended Speed Mode capability bitmap. `BIFPLR5_1_PCIE_ESM_CAP_3` covers the remaining `ESM_14P1G` through `ESM_15P9G` masks after the chunk starts mid-register. `BIFPLR5_1_PCIE_ESM_CAP_4` maps `ESM_16P0G` through `ESM_18P9G`, `CAP_5` maps `ESM_19P0G` through `ESM_21P9G`, `CAP_6` maps `ESM_22P0G` through `ESM_24P9G`, and `CAP_7` maps `ESM_25P0G` through `ESM_26P3G`. These are one-bit advertised capability entries, with matching `__SHIFT` and `_MASK` constants for each speed point.

The `BIFPLR6_1_*` section is a complete PCIe root-port/bridge configuration decode block. It starts with conventional PCI identity and bridge header fields: vendor and device ID, command and status, revision/class code fields, cache line, latency, header, BIST, primary/secondary/subordinate bus numbering, I/O and memory base/limit windows, prefetchable windows, upper base/limit halves, capability pointer, interrupt line/pin, bridge control, and extended bridge control. It then describes the capability chain for power management, PCI Express device/link/slot/root capabilities and controls, MSI, SSID, MSI mapping, vendor-specific enhanced capability, virtual channel resources, device serial number, Advanced Error Reporting, secondary PCIe extended capability, lane equalization controls for lanes 0 through 15, ACS, multicast, L1 PM substates, Downstream Port Containment, RP PIO status/mask/severity/logging, and the `BIFPLR6_1_PCIE_ESM_*` capability group.

The `BIFP0_*` section switches from PCIe config-space description to the direct PCIe port register view. This chunk includes `BIFP0_PCIEP_RESERVED`, `BIFP0_PCIEP_SCRATCH`, `BIFP0_PCIEP_PORT_CNTL`, transmit control and request accounting (`BIFP0_PCIE_TX_CNTL`, requester ID, vendor-specific fields, request number control, sequence and replay state, ACK latency limit), transmit credit advertise/init/status registers, flow-control update thresholds, physical lane status, received flow-control credit snapshots, PCIe error-control knobs, receive filtering/control (`BIFP0_PCIE_RX_CNTL` and `RX_CNTL3`), receive expected sequence number, vendor-specific receive status, and the first lines of `BIFP0_PCIE_RX_CREDITS_ALLOCATED_P`.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or runtime APIs in this slice. The consumed interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted mask for that field.
- `BIFPLR5_1`, `BIFPLR6_1`, and `BIFP0` identify distinct NBIO/PCIe register namespaces and must not be treated as interchangeable even when field names resemble standard PCIe fields.

Important `BIFPLR6_1` groups include PCI command bits (`IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`), bridge bus/window registers (`PRIMARY_BUS`, `SECONDARY_BUS`, `SUB_BUS`, I/O and memory base/limit fields), power-management controls (`POWER_STATE`, `PME_EN`, `PME_STATUS`, data select/scale), PCIe device control (`CORR_ERR_EN`, `NON_FATAL_ERR_EN`, `FATAL_ERR_EN`, `USR_REPORT_EN`, `MAX_PAYLOAD_SIZE`, `MAX_READ_REQUEST_SIZE`), link controls/status (`PM_CONTROL`, `LINK_DIS`, `RETRAIN_LINK`, negotiated speed/width, bandwidth status), slot and root controls, MSI message address/data fields, virtual-channel arbitration and resource fields, lane equalization presets/cursors for lanes 0-15, ACS source validation/translation/blocking bits, multicast address/block/overlay BAR fields, L1 PM substate timing and enable fields, DPC control/status, RP PIO status/masks/severity/sys-error/exception fields, and ESM status/control/capability bits.

The AER block is particularly important for error handling. `BIFPLR6_1_PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` use related field names for DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked events. Correctable error status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, corrected internal error, and header-log overflow. Header and TLP-prefix log registers are full-width fields.

Important `BIFP0` fields cover direct port behavior rather than standard config-space presentation. `BIFP0_PCIEP_PORT_CNTL` gates slave-port requests, hotplug/PME behavior, completion allocation, completion payload sizing, and poisoned unsupported-request response mode. `BIFP0_PCIE_TX_CNTL` controls transmit ordering/no-snoop overrides, packet packing, TLP flushing, completion/non-posted pass behavior, power-management request clearing, and flow-control update timeout handling. The transmit credit registers expose advertised and initialized posted, non-posted, and completion data/header credits, and `BIFP0_PCIE_TX_CREDITS_STATUS` reports per-class credit errors and current status. `BIFP0_PCIE_ERR_CNTL` can disable error reporting, select first-received error logging behavior, drop ECRC failures, deliberately generate LCRC/ECRC errors, tune AER header-log timeout behavior, inspect/halt slave buffers, and force immediate error messaging. `BIFP0_PCIE_RX_CNTL` contains many receive-side ignore toggles for malformed or unsupported TLP classes, completion timeout controls, PASID/prefix error handling, TPH disable, and FLR timeout behavior; `BIFP0_PCIE_RX_CNTL3` extends this to root-complex PASID and invalidation request unsupported-request cases.

## Control Flow

This chunk has no direct control flow. It influences driver control flow when AMDGPU code performs register reads, masks fields, builds read/modify/write values, or decodes hardware state for logging and diagnostics. The common pattern is: read a register using the address macro from the corresponding NBIO register header, clear or test the relevant `_MASK`, shift values by the matching `__SHIFT`, then write or interpret the result.

Ordering in this file follows the hardware register map. The transition at `nbio_pcie0_bifplr6_cfgdecp` begins a complete configuration-space layout for `BIFPLR6_1`; the transition at `nbio_pcie0_bifp0_pciedir_p` begins direct PCIe port registers. Adjacent chunks are needed for full file-level control reasoning because this slice starts mid-`BIFPLR5_1_PCIE_ESM_CAP_3` and ends mid-`BIFP0_PCIE_RX_CREDITS_ALLOCATED_P`.

## State And Persistence Behavior

The header itself has no mutable software state and persists nothing. The described state is in GPU NBIO/PCIe hardware registers. Some fields are configuration state programmed by firmware, the kernel PCI core, or AMDGPU, such as command enables, bus/window ranges, bridge controls, MSI fields, PCIe device/link controls, VC resource controls, ACS controls, L1 PM substate controls, DPC control, ESM control, direct port control, TX/RX policy bits, and error-control knobs. Other fields are hardware capability, status, counter, or log state, such as vendor/device IDs, capability IDs and next pointers, link status, lane equalization status, AER status and header logs, DPC trigger/status/source IDs, RP PIO logs, sequence/replay state, credit status, lane reversal/width status, and receive expected sequence number.

Persistence and side effects are defined by the ASIC register specification and PCIe rules, not by these macros. Many PCIe status and AER fields are latched or write-one-to-clear in hardware, while control fields may reset on function, link, bus, or GPU reset boundaries. Full-width log and address fields can be read-only, writeable, or side-effectful depending on the underlying register; this header only gives bit positions and masks and does not encode access type, reset values, write constraints, or sequencing requirements.

## Dependencies And Integration Points

This file is included by AMDGPU NBIO register-access code in the Ceph-client Linux kernel source mirror. It integrates with adjacent generated headers for NBIO 7.0 register offsets, with AMDGPU MMIO or indirect-register helpers, and with Linux PCI/PCIe subsystem concepts. The `BIFPLR6_1` config-decode definitions mirror architectural PCIe capability structures that must stay coherent with PCI core expectations for bridge configuration, MSI, power management, AER, ACS, DPC, L1 PM substates, and link training. The `BIFP0` direct-register definitions are more ASIC-specific and integrate with GPU reset, link bring-up, error injection/diagnostics, flow-control tuning, and low-level PCIe transport handling.

The ESM capability bitmaps are integration points for any code or firmware that advertises, validates, or programs supported PCIe link speed/equalization modes. The repeated capability-list and enhanced-capability fields are also integration points for debug tooling and register dumps because they allow raw NBIO values to be decoded into PCIe-visible state.

## Risks And Edge Cases

Generated-register drift is the main risk. A wrong shift or mask can make driver code silently set the wrong bit, clear reserved bits, mis-size a bridge window, enable/disable the wrong PCIe behavior, misreport link capabilities, or decode error status incorrectly. The risk is higher in this chunk because many fields are repeated across status, mask, severity, and log registers with very similar names.

Write paths must preserve reserved and unrelated bits unless the ASIC documentation explicitly permits whole-register writes. Several registers pack many single-bit controls into one word, while log/address/data registers use full-width `0xFFFFFFFFL` masks. Treating all macros as equally writeable is unsafe: capability IDs, next pointers, status, logs, lane status, credit status, and sequence state may be read-only or have write-clear semantics.

The `BIFPLR6_1_PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, `PCIE_DPC_*`, and `PCIE_RP_PIO_*` groups are semantically close but target different error-handling layers. Using a status mask against a severity or mask register may compile because the bit positions align, but it changes behavior. Direct error-injection or error-generation fields in `BIFP0_PCIE_ERR_CNTL` are also hazardous outside validation contexts because they can deliberately create link-layer or end-to-end CRC failures.

Chunk boundaries matter for reconciliation. The first visible register in this slice is incomplete because the matching `BIFPLR5_1_PCIE_ESM_CAP_3` shifts and the `ESM_14P0G` mask are just before line 63823. The final visible register is also incomplete because only the first `BIFP0_PCIE_RX_CREDITS_ALLOCATED_P` definitions appear before line 66205; the NP/CPL receive-credit allocation registers and later direct-port registers are in the following chunk.

## Test Signals

There are no unit tests local to this generated header. Useful validation signals are build, static comparison, and hardware behavior:

- Full kernel or AMDGPU builds catch malformed macro names, missing includes, and syntax errors after generated-header changes.
- Generator-output review should compare this chunk against the authoritative NBIO 7.0 register database, especially repeated AER/DPC/RP-PIO fields, ESM capability ranges, lane equalization fields, and `BIFP0` direct-port controls.
- PCI config-space dumps and register dumps can validate that decoded `BIFPLR6_1` bridge, capability, MSI, AER, ACS, DPC, L1 PM, and ESM fields match expected hardware values.
- Link bring-up, retraining, hotplug/PME, ASPM/L1 substate, and bandwidth-change logs are practical signals for the device/link/slot/root control fields.
- AER or PCIe error-injection validation can confirm uncorrectable/correctable status, mask, severity, header-log, DPC, RP-PIO, and `BIFP0_PCIE_ERR_CNTL` behavior.
- Flow-control and stability tests under posted, non-posted, and completion traffic pressure can exercise TX credit advertise/init/status fields, FCU thresholds, RX timeout/ignore controls, and credit allocation decoding.
