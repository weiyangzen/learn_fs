# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 12179-14599

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 register bitfield header. It contains C preprocessor definitions for shift positions and masks used to encode and decode PCI/PCIe configuration-space registers in the NBIO BIF configuration decoder. The visible range starts in the middle of virtual function 5 (`BIF_CFG_DEV0_EPF0_VF5_0`) PCIe link/capability definitions, covers all of virtual functions 6 and 7, and reaches the beginning-to-middle of virtual function 8, ending inside `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_CORR_ERR_STATUS`.

The source is declarative register metadata, not executable logic. Its purpose is to give AMDGPU NBIO, power-management, and hardware-access code stable symbolic names for bit extraction and field composition. Register addresses are defined separately in the paired `nbio_7_4_offset.h`; this file supplies the field-level `__SHIFT` and `_MASK` constants for those address macros.

Within lines 12179-14599 there are 2141 `#define` entries: 1070 shift macros and 1071 mask macros. The one-count difference comes from the chunk boundary starting after the comment for `VF5_0_LINK_CAP` and including some masks for fields whose shifts were defined before line 12179.

## Register Blocks Covered

The chunk follows generated address-block structure:

- Lines 12179-12655: tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`, from `VF5_0_LINK_CAP` masks through PCIe ARI control.
- Lines 12659-13339: full `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`.
- Lines 13343-14023: full `nbio_nbif0_bif_cfg_dev0_epf0_vf7_bifcfgdecp`.
- Lines 14027-14599: start of `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, from standard PCI config header fields through part of PCIe advanced error reporting.

VF6 and VF7 have the complete repeated register layout in this chunk: vendor/device identity, PCI command and status, class/revision/header/BIST fields, BARs, subsystem IDs, ROM base, capability pointer, interrupt line/pin, PCIe capability, device/link capability and control/status registers, MSI/MSI-X capability registers, vendor-specific enhanced capability registers, Advanced Error Reporting registers, header/TLP-prefix logs, ATS capability/control, and ARI capability/control. VF8 follows the same layout but this chunk ends before its AER corrected-error block is complete.

## Important Macros And Field Families

The macros use the generated naming form:

- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>_MASK`

Important field groups in this chunk include:

- Standard PCI command/status controls: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `PARITY_ERROR_RESPONSE`, `SERR_EN`, `INT_DIS`, status error bits, `CAP_LIST`, and device timing/status indicators.
- PCI identity and header fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE_SIZE`, `LATENCY_TIMER`, `HEADER_TYPE`, `DEVICE_TYPE`, and BIST fields.
- BAR and adapter registers: `BASE_ADDR_1` through `BASE_ADDR_6`, `SUBSYSTEM_VENDOR_ID`, `SUBSYSTEM_ID`, and `ROM_BASE_ADDR`.
- PCIe capability registers: `VERSION`, `DEVICE_TYPE`, `SLOT_IMPLEMENTED`, `INT_MESSAGE_NUM`, device capability/control/status, link capability/control/status, and PCIe 2.0 capability/control/status.
- Link management fields: `LINK_SPEED`, `LINK_WIDTH`, `PM_SUPPORT`, `L0S_EXIT_LATENCY`, `L1_EXIT_LATENCY`, `CLOCK_POWER_MANAGEMENT`, surprise-down reporting, data-link active reporting, bandwidth notification, target link speed, compliance controls, equalization status, de-emphasis, and downstream component presence.
- Interrupt capability fields: MSI capability list and message control, message address/data, mask and pending registers, 64-bit MSI variants, MSI-X table/PBA BIR and offset, table size, function mask, and enable bit.
- Vendor-specific enhanced capability fields: VSEC list header fields, VSEC ID/revision/length, and two scratch registers.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP-prefix blocked conditions.
- Correctable error fields: receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow. The VF8 corrected-error status masks continue beyond the chunk.
- Error log fields: four `PCIE_HDR_LOG*` 32-bit TLP header words and four `PCIE_TLP_PREFIX_LOG*` 32-bit prefix words.
- ATS/ARI virtualization fields: ATS capability/control fields such as invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable; ARI capability/control fields such as MFVC/ACS function group support, next function number, enable bits, and function group selection.

## Control Flow

There is no runtime control flow in this header. All behavior is compile-time substitution by the C preprocessor. Downstream code includes this header, reads or writes MMIO/config-space registers using address macros from `nbio_7_4_offset.h`, then applies these masks and shifts to isolate or construct field values.

The implicit data flow for consumers is:

1. Select a register address such as `cfgBIF_CFG_DEV0_EPF0_VF6_0_LINK_CNTL2` from `nbio_7_4_offset.h`.
2. Read the hardware register through the AMDGPU register-access helpers, or prepare a register value for writing.
3. Use this header's `...__FIELD_MASK` and `...__FIELD__SHIFT` macros to test, extract, clear, or set the target bitfield.
4. Write updated control values back to hardware only when the register is writable and the operation is valid for the active virtual function.

Because these are raw bit definitions, the header does not enforce read-only, write-1-to-clear, sticky status, reset, or side-effect semantics. Those semantics must be honored by the calling driver code and the hardware specification.

## State And Persistence Behavior

This chunk does not allocate memory or persist software state. The persistent state represented by these definitions is hardware state in PCI/PCIe configuration registers for SR-IOV-style virtual functions. Fields such as command enables, bus mastering, MSI/MSI-X enable/mask state, link control, AER masks/severity settings, ATS enable, and ARI control can affect hardware behavior until reset or reprogramming. Fields such as status, link status, AER status, header logs, TLP-prefix logs, MSI pending bits, and corrected/uncorrected error reports reflect hardware-observed state and may be sticky depending on register semantics outside this header.

The repeated VF5/VF6/VF7/VF8 naming is significant: each virtual function exposes the same PCIe register layout, but each macro is namespaced to one function. This reduces accidental cross-function field use when paired with matching per-VF offset macros.

## Dependencies And Integration Points

The header guard `_nbio_7_4_SH_MASK_HEADER` makes the file safe for repeated inclusion. The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` and several power-management paths, including Arcturus, Aldebaran, SMU 13.0.6, and Vega20 code. Those consumers use NBIO 7.4 register names to configure or inspect GPU PCIe/NBIO behavior.

Important adjacent generated files are:

- `nbio_7_4_offset.h`, which defines the corresponding register offsets, for example `cfgBIF_CFG_DEV0_EPF0_VF6_0_*`, `VF7`, and `VF8` addresses.
- `nbio_7_4_default.h`, which records reset/default values for many of the same registers.
- Other ASIC NBIO headers such as `nbio_6_1_*`, `nbio_2_3_*`, and `nbio_4_3_0_*`, which expose similar generated fields for different hardware IP versions or address encodings.

These macros integrate with the AMDGPU register access conventions and common bitfield helpers such as masking, shifting, `REG_GET_FIELD`-style extraction, and read/modify/write operations. The exact helper use is in C implementation files, not in this header.

## Risks And Edge Cases

The main risk is metadata drift from the hardware register specification. A wrong shift or mask can silently decode the wrong status bit or program the wrong control bit, which is especially risky for PCIe link training, bus mastering, MSI/MSI-X, AER severity/masking, ATS, and ARI controls.

Chunk-boundary risk is present here. The range begins after some `VF5_0_LINK_CAP` shift definitions and ends before the full `VF8_0_PCIE_CORR_ERR_STATUS` block is complete, so the eventual per-file merge must reconcile this report with neighboring chunks before treating VF5 and VF8 coverage as complete.

The names contain repeated words such as `..._MASK__..._MASK` for mask-register fields. This is expected generated style: the first `MASK` is part of the hardware register or field name, while the final `_MASK` suffix denotes the bitmask macro. Reviewers should not "simplify" these names manually because downstream generated code and register documentation rely on exact spellings.

Many masks are 16-bit or 32-bit constants with an `L` suffix. Callers should take care with integer width, sign extension, and casts when combining these with 64-bit register addresses from other NBIO generations. The mask constants describe field width, not register address width.

Read/write semantics are not visible in this file. Status fields, AER log fields, MSI pending bits, and link status fields may require write-1-to-clear, polling, or hardware sequencing rules defined elsewhere. Using only these masks without consulting register semantics can cause missed errors, uncleared sticky bits, or disruptive link/control changes.

## Test Signals

There are no unit tests for this header in the chunk itself. Practical validation signals are mostly compile-time and hardware/integration oriented:

- The kernel build should compile all consumers including `nbio_v7_4.c` and PM files that include `nbio_7_4_sh_mask.h`.
- Generated offset, default, and mask headers should stay internally consistent: every field mask should match the intended register width and every register family should align with the paired `cfgBIF_CFG_DEV0_EPF0_VF<N>_0_*` offset definitions.
- Static checks can verify paired `__SHIFT` and `_MASK` macros for each field, expected repeated layouts across VF6 and VF7, and expected continuation into VF8 in later chunks.
- Runtime smoke tests on NBIO 7.4 ASICs should cover PCIe link status decoding, bus-master/memory access programming, MSI/MSI-X enable paths, AER status reporting/masking, and SR-IOV virtual-function enumeration where applicable.
- Regression signals include incorrect PCI config values in debug dumps, AER errors being misclassified or not masked, virtual functions failing enumeration, MSI/MSI-X interrupts not enabling, ATS/ARI capability negotiation failures, and link speed/width reporting mismatches.

## Cross-Chunk Notes

This chunk is not a standalone final file report. The merge lane should combine it with earlier and later chunks for the full `nbio_7_4_sh_mask.h` analysis. Neighboring chunks are needed to cover the start of VF5 and the remainder of VF8 plus subsequent virtual-function/register families.
