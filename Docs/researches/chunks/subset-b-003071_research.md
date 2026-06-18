# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 7419-9885

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It provides C preprocessor constants for bitfield extraction and update of NBIF/BIF PCI configuration-space registers, specifically the tail of `BIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL`, the complete `BIF_CFG_DEV0_EPF3_0_*` and `BIF_CFG_DEV0_EPF4_0_*` register families, and the beginning of `BIF_CFG_DEV0_EPF5_0_*` through `PCIE_UNCORR_ERR_SEVERITY`.

The header is data-like hardware description, not executable logic. Its purpose is to let AMDGPU NBIO code address individual PCIe configuration fields by symbolic names instead of hand-coded shifts and masks. Consumers pair these `__SHIFT` and `__MASK` constants with register addresses from adjacent generated headers and with AMDGPU register access helpers to program or inspect GPU endpoint functions.

## Register Families Covered

The opening lines finish the EPF2 ARI control register masks for `ARI_MFVC_FUNC_GROUPS_EN`, `ARI_ACS_FUNC_GROUPS_EN`, and `ARI_FUNCTION_GROUP`. The main body then declares the address block `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, followed by a full PCI configuration layout for endpoint function 3. The same generated layout repeats for endpoint function 4 in `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`.

For EPF3 and EPF4, the chunk covers conventional PCI header fields such as vendor/device ID, command/status, revision and class codes, cache line/latency/header/BIST, BAR1 through BAR6, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. It then covers common and extended PCIe capability structures: vendor capability list, power management capability/status, serial bus release number, frame length adjustment, DBESL/DBESLD, PCIe capability/list, device/link capability/control/status including version 2 forms, MSI, MSI-X, SATA capability and indexed data port, vendor-specific enhanced capability, advanced error reporting, BAR enhanced capability, power budgeting, dynamic power allocation, access control services, and ARI.

The EPF5 section begins another copy of the same endpoint-function layout. In this chunk it reaches from identity/header/BAR/capability fields through MSI/MSI-X, SATA, vendor-specific capability, AER enhanced capability list, uncorrectable error status/mask, and uncorrectable error severity. The next chunk continues EPF5 with correctable AER and later capability blocks.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or runtime APIs in this slice. The externally consumed interface is the macro naming convention:

- `BIF_CFG_DEV0_EPF{N}_0_<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `BIF_CFG_DEV0_EPF{N}_0_<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for that field.
- `EPF3`, `EPF4`, and `EPF5` distinguish logical PCI endpoint functions under device 0; the repeated register names intentionally represent separate hardware function configuration spaces.

Notable field groups include PCI command bits (`IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`), status/error bits (`MASTER_DATA_PARITY_ERROR`, target/master aborts, system error, parity error), BAR masks (`BASE_ADDR` over full 32-bit BAR registers), MSI/MSI-X routing fields (`MSI_EN`, `MME`, message address/data, mask/pending, table/PBA BIR and offsets), power management fields (`POWER_STATE`, `PME_EN`, `PME_STATUS`, data select/scale), and PCIe link/device control fields (`MAX_PAYLOAD_SIZE`, `MAX_READ_REQUEST_SIZE`, relaxed ordering, no-snoop, link speed/width, ASPM, retraining, bandwidth notifications).

The AER groups are particularly important for diagnosis and containment. The uncorrectable status/mask/severity fields include DLP, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors. Correct interpretation requires using the status, mask, and severity registers together.

## Control Flow

This chunk has no direct control flow. It participates in control flow indirectly when AMDGPU code reads a hardware register, isolates fields with these masks, or constructs writes by shifting values into the bit positions defined here. Typical generated-header use is a read/modify/write pattern: read a register value, clear a `*_MASK`, OR in `(value << *_SHIFT) & *_MASK`, then write the register back.

Because these macros describe hardware layout, ordering in the file follows the register map rather than program execution. The EPF3, EPF4, and EPF5 blocks repeat because each endpoint function exposes the same or nearly same PCIe capability chain and configuration fields.

## State And Persistence Behavior

The header itself has no mutable software state and persists nothing. The state it describes lives in GPU NBIO/BIF PCI configuration registers. Some fields are software-controlled configuration state, such as PCI command enables, interrupt disable, MSI/MSI-X enable/masks, power-management controls, ACS controls, ARI controls, BAR controls, and DPA controls. Other fields are hardware-reported capability or status state, such as vendor/device IDs, link status, error status, and capability pointers.

Persistence depends on hardware reset and PCIe configuration behavior, not this file. Driver code using these definitions must treat many status fields as hardware-latched or write-one-to-clear according to the underlying PCIe/AER specification and ASIC register documentation. Mask constants alone do not encode access type, reset value, side effects, or required sequencing.

## Dependencies And Integration Points

This file is included by AMDGPU NBIO and register-access code in the Ceph-client Linux kernel source mirror. It is one member of a generated register family: address headers provide register offsets, this `*_sh_mask.h` file provides bit positions and masks, and driver C code combines both with AMDGPU helpers for MMIO or indirect register access.

The constants align with PCI/PCIe architectural concepts used elsewhere in the kernel: standard PCI config header fields, PCI power management, PCI Express capability, MSI and MSI-X capabilities, SATA capability, PCIe extended capabilities, AER, ACS, ARI, power budgeting, and dynamic power allocation. Integration code must also coordinate with the Linux PCI core, interrupt setup, runtime power management, GPU reset flows, error handling, SR-IOV or multi-function exposure if present, and any ASIC-specific NBIO access methods.

## Risks And Edge Cases

The highest risk is generated-register drift. If a shift or mask does not match the NBIO 7.0 hardware specification, downstream code may silently program the wrong bit, clear reserved bits, fail to enable a device function, mis-handle interrupts, or misclassify PCIe errors. Repeated EPF blocks make copy/paste or generation-template errors hard to spot manually because EPF3 and EPF4 are expected to look almost identical while still naming separate function spaces.

Boundary fields need special care. Full-width masks such as `0xFFFFFFFFL` are used for BARs, MSI addresses, IDP data, and log registers, while small-width fields share registers with reserved bits. Any write path should preserve reserved fields unless the hardware documentation explicitly allows full-register writes. AER status/mask/severity naming also invites mistakes: using a status mask constant against the severity register may compile and appear plausible because the bit positions are often the same, but it changes the semantic target.

Chunk boundaries are another review risk. This slice starts mid-EPF2 and ends mid-EPF5, so file-level reasoning must be reconciled with adjacent chunks before drawing conclusions about all endpoint functions. The EPF5 AER correctable status/mask and later BAR/power/ACS/ARI blocks are outside this chunk.

## Test Signals

There are no unit tests for these macros in this header. Useful validation signals are compile-time and hardware/driver behavior:

- Full kernel or AMDGPU builds catch missing, duplicated, or malformed macro names after generated-header changes.
- Register programming tests or bring-up logs should confirm PCI command enables, BAR programming, MSI/MSI-X setup, power-management transitions, and link/device control values are written to the intended fields.
- PCIe AER injection or real error telemetry can validate that uncorrectable status, mask, and severity bits decode consistently with Linux PCIe error handling.
- Runtime checks through PCI config dumps, debugfs, register dumps, or ASIC validation tools can compare decoded EPF3/EPF4/EPF5 values against expected hardware capability chains.
- Static review should compare this generated output against the authoritative NBIO 7.0 register database, especially around repeated EPF blocks, reserved masks, and the chunk boundaries at EPF2 ARI and EPF5 AER.
