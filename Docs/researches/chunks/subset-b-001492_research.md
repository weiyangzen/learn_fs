# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h

Chunk: `subset-b-001492`
Covered source range: lines 12893-16994 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h`

## Purpose

This chunk is a generated AMD BIF 5.1 register field mask header segment. It contains no executable code; it supplies C preprocessor constants that describe bit masks and bit shifts for fields in PCIe/BIF configuration and link-control registers.

The assigned range covers 4,102 `#define` lines: 2,051 `_MASK` macros and 2,051 matching `__SHIFT` macros. It starts in the middle of the `D2F5_PCIE_LC_CNTL3` register field family and ends in the middle of the `D3F2_PCIE_LC_N_FTS_CNTL` family. The merge/reconciliation lane should combine adjacent chunks before producing final file-level conclusions for `bif_5_1_sh_mask.h`.

The covered register prefixes are:

- `D2F5`: completes a large function-5 PCIe/BIF block, beginning at the later `PCIE_LC_CNTL3` fields and continuing through PCIe link-control, PCI/PCIe capability, MSI, AER, ACS, VC, multicast, slot/root, config-space, and error-reporting fields.
- `D3F1`: a full function-1 style block in this range, including PCIe port, RX/TX, flow-control, error-injection, link-control, configuration-space capability, AER/ACS/VC/multicast, lane equalization, and bridge/root/slot fields.
- `D3F2`: the start of a function-2 block, covering PCIe port, RX/TX, flow-control, error-injection, link-control, and early `LC_N_FTS` fields before the chunk boundary.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The public surface is entirely macro constants used by AMDGPU register helper code.

The naming convention is consistent:

- `<REGISTER>__<FIELD>_MASK` isolates or clears the field in a 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count for extracting the field or the left-shift count before applying the mask.
- The register prefix, such as `D3F1_PCIE_LC_SPEED_CNTL`, is expected to match an address macro in `bif_5_1_d.h`, commonly named with an `ix` prefix for indexed PCIe/BIF config space.

Important macro families in this range include:

- Link controller fields: `PCIE_LC_CNTL`, `PCIE_LC_CNTL2`, `PCIE_LC_CNTL3`, `PCIE_LC_CNTL4`, `PCIE_LC_CNTL5`, `PCIE_LC_CNTL6`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_CDR_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, and `PCIE_LC_STATE0` through `PCIE_LC_STATE5`.
- PCIe data-link and transaction-layer controls: `PCIE_TX_CNTL`, `PCIE_TX_REPLAY`, `PCIE_TX_REQUESTER_ID`, `PCIE_TX_REQUEST_NUM_CNTL`, `PCIE_TX_CREDITS_*`, `PCIE_RX_CNTL`, `PCIE_RX_CNTL3`, `PCIE_RX_CREDITS_ALLOCATED_*`, `PCIE_FC_P`, `PCIE_FC_NP`, and `PCIE_FC_CPL`.
- Error handling and diagnostics: `PCIE_ERR_CNTL`, `PCIEP_HW_DEBUG`, `PCIEP_ERROR_INJECT_PHYSICAL`, `PCIEP_ERROR_INJECT_TRANSACTION`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, `PCIE_ERR_SRC_ID`, and header/TLP prefix log registers.
- Link capability and status: `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CAP2`, `DEVICE_CNTL`, `DEVICE_CNTL2`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CAP2`, `LINK_CNTL`, `LINK_CNTL2`, `LINK_STATUS`, `LINK_STATUS2`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`.
- Virtualization, peer routing, and multicast capability fields: `PCIE_ACS_*`, `PCIE_MC_*`, `PCIE_VC_*`, and `PCIE_PORT_VC_*`.
- Per-lane equalization definitions for lanes 0-15, with downstream/upstream TX preset and RX preset-hint fields.
- Conventional PCI config-space and bridge fields such as `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `BASE_CLASS`, `SUB_CLASS`, `PROG_INTERFACE`, `BIST`, `CACHE_LINE`, `HEADER`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, and `SUB_BUS_NUMBER_LATENCY`.
- MSI and power-management capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_*`, `MSI_MSG_DATA*`, `MSI_MAP_*`, `PMI_CAP`, `PMI_CAP_LIST`, and `PMI_STATUS_CNTL`.

## Control Flow

This chunk has no runtime control flow. It is a compile-time register-description table expressed as preprocessor macros.

Runtime control flow is created by consumers that use these macros in read/modify/write or read/poll/write sequences. Typical patterns are:

- read a BIF or PCIe register through AMDGPU register accessors;
- use `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent mask/shift logic to extract or update a field;
- write the modified register value back;
- poll status fields such as link-training state, error status, credit availability, or interrupt/error bits until hardware reaches the expected state.

The link controller families influence PCIe state-machine decisions in consuming code or firmware flows: speed changes, link-width renegotiation, ASPM L0s/L1 transitions, recovery, equalization, fast training sequence counts, receiver detection, and hot-reset behavior.

## State And Persistence Behavior

The header itself owns no mutable state and persists nothing. Its constants are compiled into any translation unit that includes it.

The state addressed by the constants is device hardware state in BIF/PCIe configuration and link-controller registers. Values written through these masks can persist until overwritten by the driver, firmware, PCIe link events, function-level reset, hot reset, GPU reset, power-management transition, or device removal. Status and counter fields expose transient hardware observations such as current link speed, link width, lane equalization state, replay/error counts, flow-control credits, AER status, and root/slot events.

Some fields are latched or clear-on-write style in the broader PCIe/AER model. This header does not encode access semantics, so callers must know whether a field is read-only, write-one-to-clear, sticky, strap-derived, or writable before using a mask in a generic update operation.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The practical companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h`, which defines the register addresses that correspond to these field masks.

Direct BIF 5.1 mask-header includes found in the AMDGPU tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c`

Those interrupt-handler files include both `bif_5_1_d.h` and `bif_5_1_sh_mask.h` and use the same generated mask/shift naming style through register field helpers. Their visible runtime work is interrupt-ring setup, interrupt enable/disable, dummy-read control, MSI-related behavior, write-pointer writeback, and register programming via `RREG32`, `WREG32`, and `REG_SET_FIELD`.

The D2F5/D3F1/D3F2 prefix families also integrate with the indexed PCIe/BIF register address space exposed in `bif_5_1_d.h`. These definitions are architecture-generation specific and should not be mixed with a different BIF generation unless the hardware documentation explicitly guarantees identical layouts.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These are untyped integer macros, so the compiler cannot tell whether a caller uses a `D3F1` field mask against a `D2F5` register, combines a mask with the wrong shift, or updates a read-only or write-one-to-clear status field as if it were a normal writable control bit.

This chunk starts and ends inside generated register families. The first visible field is not the first `D2F5_PCIE_LC_CNTL3` field, and the final `D3F2_PCIE_LC_N_FTS_CNTL__LC_N_FTS` mask/shift pair is outside this range. Any final register-family summary must include neighboring chunks.

Several fields affect live PCIe link behavior: speed change, link-width change, receiver detection, equalization, ASPM/L0s/L1, hot reset, recovery entry, lane power state, FTS counts, and PHY command behavior. Incorrect writes can destabilize the PCIe link, break resume, mask real errors, or make the device require reset.

Error-injection and hardware-debug registers are especially risky because they can deliberately create malformed physical or transaction-layer behavior. A production path should not write those fields except under explicit debug or validation control.

Capability and status fields mirror standardized PCI/PCIe concepts but still live in ASIC-specific generated headers. A field name that looks generic, such as `LINK_STATUS` or `DEVICE_CNTL2`, must still be interpreted through the exact BIF 5.1 address and access path.

Per-lane equalization macros are repetitive and easy to misuse. Lane numbering, upstream versus downstream preset fields, and paired fields packed into the same 32-bit register need careful review in any hand-written access code.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware integration checks:

- Compile all AMDGPU targets that include `bif_5_1_sh_mask.h`, especially Iceland, Tonga, and Carrizo interrupt-handler paths.
- Static generator checks that every `_MASK` macro has exactly one matching `__SHIFT` macro in the final full header and that no duplicate macro name has conflicting values. In this assigned range, the 2,051 masks and 2,051 shifts are balanced.
- Cross-check field register prefixes in `bif_5_1_sh_mask.h` against address macros in `bif_5_1_d.h`, especially for `D2F5`, `D3F1`, and `D3F2`.
- Exercise interrupt-ring initialization, MSI and non-MSI interrupt handling, dummy-read setup, write-pointer writeback, suspend/resume, and GPU reset on BIF 5.1 ASICs.
- Validate PCIe link training and retraining paths across Gen1/Gen2/Gen3 speed selection, lane-width negotiation, ASPM transitions, hot reset, function-level reset, and recovery.
- Read back representative single-bit and multi-bit fields after controlled writes where the hardware permits it, confirming that mask/shift extraction matches expected values.
- Run AER/error-status tests that verify correct handling of correctable/uncorrectable error masks, root error status, header logs, and clear-on-write semantics.
- Lab-test lane equalization and per-lane status reporting because those fields can compile cleanly while targeting the wrong lane or preset nibble.
