# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 34238-36659

## Scope

This chunk covers a generated section of AMDGPU's NBIO 7.4 shift/mask header for PCIe configuration-space fields under `BIF_CFG_DEV0_EPF0` virtual-function address blocks. It starts in the middle of `BIF_CFG_DEV0_EPF0_VF4_0_DEVICE_CAP2`: the first lines in this chunk are the tail of the `DEVICE_CAP2` `__SHIFT` definitions, and the corresponding `DEVICE_CAP2` masks are in this chunk. It then completes the rest of the `VF4_0` PCIe capability and enhanced-capability blocks, covers complete `VF5_0` and `VF6_0` endpoint virtual-function configuration images, and covers `VF7_0` from conventional PCI identity/header registers through AER header log registers. The next chunk continues `VF7_0` with TLP prefix logs and later enhanced capabilities.

The chunk is declarative generated C preprocessor data. It contains no functions, structs, enums, runtime storage, loops, branches, or persistence logic. The public surface is a large set of symbols following the generated AMD register bitfield convention:

- `BIF_CFG_DEV0_EPF0_VF*_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF*_0_<REGISTER>__<FIELD>_MASK`

These constants are meant to be paired with register-address definitions from `nbio_7_4_offset.h`.

## Purpose

`nbio_7_4_sh_mask.h` provides the bit layout contract for NBIO 7.4 registers. This slice describes PCI/PCIe configuration fields for SR-IOV-style virtual-function config images on device 0, endpoint function 0, especially VFs 4 through 7. Consumers use the shifts and masks to extract hardware-reported capability/status bits or compose safe read-modify-write values for writable control fields.

The field families in this chunk are standard PCI/PCIe-facing areas: PCI command/status and BAR metadata, PCIe device/link capability and control, MSI/MSI-X interrupt capability registers, vendor-specific enhanced capability headers/payloads, Advanced Error Reporting, Address Translation Services, and Alternative Routing-ID Interpretation. The header does not decide policy for these features; it only names bit positions for code that already knows when and how to touch the registers.

## Major Register Families

### Tail Of `BIF_CFG_DEV0_EPF0_VF4_0`

The `VF4_0` portion begins after `LINK_STATUS`, with `DEVICE_CAP2` and `DEVICE_CNTL2` PCIe capability 2 fields. These define completion-timeout support and control, ARI forwarding support/enable, atomic operation support and request enablement, ID-based ordering enables, LTR support/enable, OBFF support/control, 10-bit tag support/control, end-to-end TLP prefix support/blocking, and emergency power reduction fields.

The remaining `VF4_0` block includes:

- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for supported/target link speeds, compliance controls, de-emphasis/transmit margin, autonomous speed disable, 8 GT/s equalization completion and phase success, link equalization request, retimer presence, crosslink status, and downstream component presence.
- Sparse slot capability/control/status 2 registers represented as all-reserved masks.
- MSI and MSI-X capability registers, including capability IDs/next pointers, MSI enable, multi-message capability/enable, 64-bit MSI support, per-vector masking capability, message address/data, mask and pending bitmaps, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- PCIe vendor-specific enhanced capability list/header plus two 32-bit scratch payload registers.
- PCIe AER capability, uncorrectable status/mask/severity, correctable status/mask, AER capability/control, header logs, and TLP prefix logs.
- ATS capability/control, including invalidate queue depth and small enable/stall fields.
- ARI capability/control, including multifunction/device-function-group capability, next function number, function group, and ACS function group enable.

Because the chunk starts mid-register, whole-register research for `VF4_0_DEVICE_CAP2` must also consult the previous chunk for the earliest `DEVICE_CAP2` shift definitions.

### Complete `BIF_CFG_DEV0_EPF0_VF5_0` And `VF6_0`

The `VF5_0` and `VF6_0` address blocks are complete in this range and have the same generated shape. Each block starts with conventional PCI configuration header fields:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, cache-line size, latency timer, header type, and BIST.
- `COMMAND` and `STATUS`: I/O, memory, bus master, special cycle, memory write invalidate, VGA palette snoop, parity response, SERR, fast back-to-back, interrupt disable, interrupt/status and error indication bits, capability-list support, devsel timing, target/master abort, signaled system error, and parity error detection.
- BAR and resource metadata: six base address registers, adapter/subsystem identity, ROM base address, capability pointer, interrupt line, and interrupt pin.

Each full VF block then defines PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` expose PCIe capability ID, next pointer, capability version, device/port type, slot implemented, interrupt message number, and related capability metadata.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` describe maximum payload support, phantom functions, extended tag, endpoint L0s/L1 latency, role-based error reporting, FLR support, corrected/nonfatal/fatal/unsupported request status, AUX power, and pending transaction state.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe max speed/width, ASPM and L1 exit latency, clock power management, surprise down and DLL active reporting support, link bandwidth notification capability, ASPM enables, read completion boundary, link disable/retrain/common clock/extended sync, negotiated speed/width, training, slot clock, data-link active, and bandwidth status bits.
- Capability 2 and link 2 registers repeat the modern PCIe controls and statuses noted for `VF4_0`.

The interrupt and enhanced-capability tail of each full block mirrors `VF4_0`: MSI/MSI-X, vendor-specific enhanced capability, AER status/mask/severity/control/logs, ATS, and ARI.

### Partial `BIF_CFG_DEV0_EPF0_VF7_0`

The `VF7_0` section is complete from its address-block marker through `PCIE_HDR_LOG3`, but not through the whole virtual-function capability image. It includes the same conventional PCI header, PCIe capability, device/link capability/control/status, MSI/MSI-X, vendor-specific capability, and AER status/mask/severity/control fields as `VF5_0` and `VF6_0`.

The chunk ends exactly at `BIF_CFG_DEV0_EPF0_VF7_0_PCIE_HDR_LOG3__TLP_HDR_MASK`. The subsequent `VF7_0` TLP prefix logs, ATS, ARI, and any later capability definitions are outside this work item.

## Important APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The important interface is the macro namespace itself. Callers normally use these constants through AMDGPU register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, or through explicit mask/shift arithmetic after reading the associated register via NBIO/PCIE register access helpers.

The header is included with `nbio_7_4_offset.h` by NBIO and platform code such as `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, SMU power-management files, PSP files, and display-resource code that needs NBIO 7.4 register definitions. `nbio_v7_4.c` provides the runtime NBIO 7.4 function table for revision ID, memory size, doorbell apertures, interrupt/doorbell ranges, clock gating, RAS interrupt handling, LTR/ASPM programming, and PCIE index/data access. This chunk's VF-specific PCIe config macros are part of the same generated register ABI, even when individual symbols are consumed indirectly by hardware debug, RAS, PCIe, or future enablement paths rather than visibly referenced one by one.

## Control Flow

This header section has no local control flow. Runtime flow belongs to consumers:

1. Select NBIO 7.4 support based on the detected `NBIO_HWIP` version.
2. Use the paired `nbio_7_4_offset.h` symbol for the target `BIF_CFG_DEV0_EPF0_VF*_0_*` register.
3. Read the register through AMDGPU MMIO, SOC15, or PCIe-index/data access paths.
4. Decode fields with the `*_MASK` and `*__SHIFT` constants, usually through `REG_GET_FIELD`.
5. For writable controls, preserve unrelated and reserved bits, insert a shifted field value with the matching mask, and write the register only when the PCIe/NBIO programming sequence allows it.

The runtime flows affected by these definitions include PCIe VF enumeration and configuration visibility, link-state reporting, completion timeout policy, LTR/OBFF and ASPM-adjacent power behavior, MSI/MSI-X interrupt programming, AER diagnostics, ATS enablement, and ARI routing metadata.

## State And Persistence

The macros are compile-time constants and store no state. The state they describe lives in NBIO/PCIe configuration registers for virtual functions.

Capability fields such as vendor/device IDs, class codes, maximum payload support, link speed/width support, MSI/MSI-X table layout, AER capability metadata, ATS queue depth, and ARI multifunction support are generally hardware- or firmware-defined values. Control fields such as PCI command enables, device control, link control, completion timeout disable/value, LTR enable, MSI/MSI-X enable and masking, AER masks/severity, ATS enable/stall, and ARI/ACS function-group enables are writable only where the underlying config-space register permits it. Status fields such as PCI error status, device status, link training/equalization status, MSI pending bits, and AER correctable/uncorrectable status are hardware-updated and can be sticky or write-one-to-clear depending on the PCIe specification and ASIC register rules.

Persistence is therefore hardware-domain-specific. Software does not persist these fields in this header; values may survive until FLR, hot reset, GPU reset, link reset, power-gating transition, suspend/resume, or explicit driver reprogramming depending on the register and platform.

## Dependencies And Integration Points

- Requires exact synchronization with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`. A shift/mask macro is only meaningful with the matching `regBIF_CFG_DEV0_EPF0_VF*_0_*` address and base-index definition.
- Integrates with AMDGPU NBIO 7.4 runtime code in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which includes the generated NBIO 7.4 headers and supplies NBIO callbacks selected by `amdgpu_discovery.c` for NBIO IP versions 7.4.x.
- Supports PM/SMU, PSP, display, and legacy powerplay files that include NBIO 7.4 generated headers to access platform-specific NBIO registers.
- Supports PCIe and virtualization-facing functionality: VF config-space exposure, MSI/MSI-X programming, AER/RAS decode, ATS translation services, ARI routing, link capability/status reporting, and power/link policy controls such as LTR, OBFF, and ASPM-adjacent bits.
- Relies on generic AMDGPU register helper conventions; the macros do not define access width, register reset values, write masks, side effects, or sequencing requirements.

## Risks

- Generated-header drift is the main risk. A wrong bit shift or mask silently misdecodes config-space state or writes the wrong field, which can affect VF enumeration, BAR interpretation, PCI command enables, MSI/MSI-X routing, link policy, AER masking, ATS enablement, or ARI routing.
- The chunk boundaries split logical `VF4_0` and `VF7_0` sections. A per-file merge must not treat this chunk as the full source of `VF4_0_DEVICE_CAP2` or the full `VF7_0` enhanced-capability tail.
- Repetition across `VF5_0`, `VF6_0`, and `VF7_0` makes copy/generation mistakes hard to review manually. A single wrong VF number in a macro name would compile but target the wrong config image in source code.
- PCIe status and AER fields have hardware-defined side effects that masks alone do not communicate. Writing a status register as if it were ordinary RAM can clear sticky diagnostics or lose first-error/header-log context.
- Mixed field widths matter. This range contains 8-bit, 16-bit, and 32-bit logical fields in config registers. Consumers must use the access width and read-modify-write discipline required by the register path and hardware documentation.
- Control fields for MSI/MSI-X, ATS, ARI, LTR, OBFF, atomic operations, and completion timeout can alter interrupt delivery, address translation behavior, routing, ordering, and link/power behavior. They should only be modified in established initialization, reset, or policy paths.

## Test Signals

- Build signal: AMDGPU sources that include `nbio_7_4_sh_mask.h` and `nbio_7_4_offset.h` compile without undefined, duplicate, or mismatched macro errors.
- Static generation signal: compare this section against the NBIO 7.4 register database/spec and verify matching offset symbols exist for every `BIF_CFG_DEV0_EPF0_VF4_0`, `VF5_0`, `VF6_0`, and `VF7_0` register covered here.
- PCIe enumeration signal: on hardware using NBIO 7.4.x paths, virtual functions expose plausible vendor/device/class/header/BAR/capability-chain data and do not report corrupted capability pointers.
- Interrupt signal: MSI/MSI-X setup, mask/unmask, pending-bit behavior, table/PBA decoding, and interrupt delivery work for VFs that use these capability images.
- Link/power signal: device/link status, negotiated speed/width, LTR/OBFF-related controls, completion-timeout settings, and equalization status decode consistently with `lspci -vv` style diagnostics and platform logs.
- Error-handling signal: AER/RAS decode reports correct uncorrectable/correctable error bits, masks, severities, first-error pointers, ECRC controls, and header-log contents under fault injection or captured hardware errors.
- Reset/resume signal: FLR, hot reset, GPU reset, suspend/resume, and SR-IOV enable/disable paths restore or reinitialize writable VF PCIe controls without stale MSI/MSI-X, ATS, ARI, AER, or link-control state.
