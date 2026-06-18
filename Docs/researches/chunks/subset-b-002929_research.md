# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 61470-63890

## Scope And Purpose

This chunk is a generated AMD GPU NBIO 2.3 register shift/mask header slice. It contains C preprocessor constants for bitfield extraction and construction, not executable functions. The slice covers PCI configuration-space fields for SR-IOV virtual functions under `BIF_CFG_DEV0_EPF0_VF*_0`, starting in the middle of the VF5 PCIe capability register definitions and ending after the VF8 vendor-specific scratch registers.

The definitions are part of the AMDGPU driver's hardware register contract for NBIO 2.3 ASICs. They pair with the sibling offset/default headers, especially `nbio_2_3_offset.h`, and are consumed by driver code through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` from `amdgpu.h`. These helpers concatenate names like `BIF_CFG_DEV0_EPF0_VF6_0_COMMAND__BUS_MASTER_EN_MASK` and `...__SHIFT` to modify or decode fields without open-coded bit arithmetic.

Within this chunk there are 2,145 `#define` entries across VF5, VF6, VF7, and VF8. VF6 and VF7 are complete virtual-function register field blocks in this line window. VF5 is a tail block that begins after the VF5 capability-list fields, and VF8 is a head block that ends just before the VF8 advanced-error-reporting fields that continue in the next chunk.

## Covered Register Groups

The repeated naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>_MASK`

The chunk covers these virtual functions and approximate scope:

- `VF5`: PCIe capability, device/link capability and control/status, MSI/MSI-X, vendor-specific, advanced error reporting, ATS, and ARI field masks from lines 61470-62026.
- `VF6`: a full PCI config header and extended capability block from vendor/device IDs through ARI control at lines 62028-62722.
- `VF7`: another full PCI config header and extended capability block from vendor/device IDs through ARI control at lines 62724-63418.
- `VF8`: PCI config header through PCIe vendor-specific scratch fields at lines 63420-63890; AER and later capability masks continue after this chunk.

Important register families represented here include:

- Basic PCI config fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, `MSI_PENDING_64`, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor and PCIe extended capabilities: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, `PCIE_VENDOR_SPECIFIC2`, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable AER status/mask/severity registers, `PCIE_ADV_ERR_CAP_CNTL`, header/TLP-prefix logs, `PCIE_ATS_*`, and `PCIE_ARI_*`.

## Important APIs, Types, And Functions

This header chunk defines no C types, structs, enums, or functions. Its "API" is the exported macro namespace used by AMDGPU source files at compile time.

The most important consumer API shape is:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
- `REG_SET_FIELD(orig_val, reg, field, field_val)` clears the field's mask in `orig_val` and inserts `field_val << SHIFT` masked by `MASK`.
- `REG_GET_FIELD(value, reg, field)` extracts `(value & MASK) >> SHIFT`.

These macros mean a constant pair such as `BIF_CFG_DEV0_EPF0_VF6_0_COMMAND__MEM_ACCESS_EN__SHIFT` and `BIF_CFG_DEV0_EPF0_VF6_0_COMMAND__MEM_ACCESS_EN_MASK` is a compile-time dependency for code that calls:

```c
REG_SET_FIELD(value, BIF_CFG_DEV0_EPF0_VF6_0_COMMAND, MEM_ACCESS_EN, 1)
```

Direct includes found in this tree include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, `pm/swsmu/smu11/navi10_ppt.c`, and `pm/swsmu/smu11/sienna_cichlid_ppt.c`. Those files include `nbio_2_3_sh_mask.h` together with NBIO offset/default headers or other ASIC register headers to compile register access paths for NBIO 2.3 hardware.

## Field Semantics

The basic PCI config fields describe each virtual function's PCI identity and resource aperture:

- `COMMAND` has enable/control bits such as I/O access, memory access, bus mastering, parity-error response, SERR, and interrupt disable.
- `STATUS` has detected-capability and error/status bits such as interrupt status, capability-list presence, master-data parity error, signaled target abort, received target/master abort, signaled system error, detected parity error, and immediate-readiness.
- BAR and ROM fields expose address/memory properties through masks over the full 32-bit register value or low-order type bits.
- `CAP_PTR`, interrupt line/pin, min grant, and max latency preserve legacy PCI capability and interrupt metadata.

The PCIe capability blocks expose negotiated link/device behavior:

- `DEVICE_CAP` and `DEVICE_CNTL` describe and control maximum payload size, relaxed ordering, extended tags, no-snoop, read request size, FLR, and power-management related bits.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover speed, width, ASPM, link retraining/disable, clocking, link-bandwidth interrupts, data-link active state, and training/status indicators.
- `DEVICE_CAP2` and `DEVICE_CNTL2` add completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefix handling, emergency power reduction, and FRS support/control.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover supported link speeds, compliance modes, autonomous speed disable, de-emphasis, equalization status, crosslink resolution, downstream presence, and DRS message status.

The interrupt capability blocks mirror the standard MSI and MSI-X PCI capability layouts:

- `MSI_MSG_CNTL` fields include `MSI_EN`, multi-message capability/enables, 64-bit support, and per-vector masking capability.
- `MSI_MSG_ADDR_*`, `MSI_MSG_DATA*`, `MSI_MASK*`, and `MSI_PENDING*` provide payload and mask/pending fields.
- `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` describe MSI-X table size, function mask, enable bit, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

The AER, ATS, ARI, and vendor-specific groups provide extended capability metadata and error reporting:

- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` define fields for data-link protocol, surprise-down, poisoned TLP, flow-control, completion-timeout, completer-abort, unexpected completion, receiver-overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP-prefix blocked conditions.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` define receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal, header-log overflow, and similar correctable conditions.
- `PCIE_ADV_ERR_CAP_CNTL` defines first-error pointer, ECRC generation/check capability and enable bits, multiple-header recording, TLP prefix log presence, and log size.
- `PCIE_HDR_LOG*` and `PCIE_TLP_PREFIX_LOG*` expose raw logged DWORD fields.
- `PCIE_ATS_*` and `PCIE_ARI_*` expose address-translation-service and alternative routing-ID capability/control fields.
- `PCIE_VENDOR_SPECIFIC*` supplies VSEC capability headers and scratch fields.

## Control Flow And Execution Behavior

There is no runtime control flow in this chunk. The effective flow is compile-time name resolution:

1. A driver file includes `nbio_2_3_sh_mask.h`.
2. The compiler expands a field helper such as `REG_SET_FIELD` or direct bit arithmetic using the `__SHIFT` and `_MASK` constants.
3. Runtime register access code uses the computed value with hardware accessors such as `RREG32*`, `WREG32*`, `RREG32_SOC15`, `WREG32_SOC15`, or PCI/SMN helpers elsewhere in the driver.

Because each macro is a raw literal, the header has no branches, loops, allocation, locking, or function-call side effects. Behavioral changes only happen indirectly when a consumer reads or writes the affected hardware register field.

## State And Persistence Behavior

The file stores no software state and has no persistence layer. Its constants describe persistent or semi-persistent hardware state in the GPU's PCI configuration and NBIO register space:

- Command/control masks may be used to enable memory access, bus mastering, MSI/MSI-X, link retraining, FLR, ARI, ATS, LTR, OBFF, and related VF-visible controls.
- Status masks decode transient hardware state such as link training, pending transactions, MSI pending bits, AER status bits, and equalization/link status.
- Log masks identify AER header/TLP prefix logging registers that may retain hardware error evidence until software clears or hardware overwrites it.

In SR-IOV environments, these fields represent per-virtual-function configuration surfaces. Incorrect masks can cause the host PF/VF boundary to expose, hide, or mutate the wrong bit in a VF's virtual PCI config space.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- `nbio_2_3_offset.h`: supplies register addresses/offsets corresponding to the shift/mask names in this header.
- `nbio_2_3_default.h`: supplies reset/default values for some NBIO 2.3 registers.
- `amdgpu.h`: defines `REG_FIELD_SHIFT`, `REG_FIELD_MASK`, `REG_SET_FIELD`, and `REG_GET_FIELD`, the token-pasting helpers that rely on this naming convention.
- SOC15 and NBIO accessors: code in `nbio_v2_3.c` uses NBIO register constants with `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and related helpers.
- Virtualization paths: `mxgpu_nv.c` includes this header while implementing Navi SR-IOV mailbox interactions between VF and PF, making the NBIO VF register namespace relevant to virtual GPU operation.
- SMU power-management paths: Navi10/Sienna Cichlid SMU tables include this header alongside other register headers for ASIC-specific power, link, and status handling.

The chunk also has structural dependencies on adjacent line ranges of the same file. VF5's basic config fields precede this chunk, and VF8's AER/ATS/ARI fields continue after it. A final per-file merge must preserve that this chunk is one middle segment of a much larger generated register table.

## Risks And Maintenance Notes

The main risk is silent hardware misprogramming from incorrect generated constants. A wrong shift or mask can compile cleanly while causing runtime code to write adjacent control bits or misread status/error state.

Specific risks in this chunk:

- SR-IOV VF replication: VF6, VF7, and VF8 blocks repeat nearly identical layouts. Copy-generation drift in one VF block could affect only that virtual function and may be missed by tests that exercise a smaller VF count.
- PCIe capability correctness: fields such as payload size, read request size, FLR, ARI, ATS, atomic ops, LTR, OBFF, MSI/MSI-X enable/mask, and AER severity directly influence PCIe interoperability and error handling.
- Boundary completeness: this chunk starts inside VF5 and ends inside VF8. Research or validation that treats it as a standalone complete file would miss preceding/following fields required for a full VF definition.
- Token-paste coupling: consumers depend on exact spelling of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Renaming a field or changing one half of a shift/mask pair breaks helper expansion or creates mismatched behavior.
- Width assumptions: most values use `L` suffix literals and are intended for 32-bit register fields. Any consumer using narrower types could truncate masks such as `0xFFFFFFFFL`, `0xFFF00000L`, or `0x80000000L`.

## Test Signals

There are no unit tests for this generated header in the chunk itself. Useful validation signals are compile-time and hardware/driver behavior:

- Build coverage for AMDGPU configurations that include NBIO 2.3 users. Missing or misspelled macros should fail compilation in files that call `REG_SET_FIELD` or `REG_GET_FIELD`.
- Static comparison against AMD's register database or sibling generated headers, especially for repeated VF6/VF7/VF8 layouts, can detect copy-generation drift.
- SR-IOV smoke tests that enumerate multiple VFs and validate PCI config space fields, BARs, MSI/MSI-X capability tables, and ARI/ATS capability chains.
- PCIe link and power-management tests that check advertised link speed/width, ASPM behavior, retraining, LTR/OBFF control, FLR, and completion-timeout behavior.
- RAS/AER tests that inject or observe correctable and uncorrectable PCIe errors and confirm that status, mask, severity, header log, and TLP prefix log fields decode correctly.
- Runtime register tracing around NBIO 2.3 driver paths can confirm that field writes preserve unrelated bits by using the matching mask/shift pairs.

## Chunk Boundary Notes

Line 61470 continues `BIF_CFG_DEV0_EPF0_VF5_0_PCIE_CAP`; the `VERSION__SHIFT` and earlier VF5 base config definitions are above the chunk. Line 63890 ends with `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_VENDOR_SPECIFIC2__SCRATCH_MASK`; the next block, `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, begins after this chunk.
