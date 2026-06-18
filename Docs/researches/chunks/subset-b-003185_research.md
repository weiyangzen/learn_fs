# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 61040-63515

## Purpose

This chunk is an auto-generated AMD NBIO 7.2 shift/mask slice for PCI/PCIe configuration-space fields in NBIF endpoint-function decode blocks. It defines preprocessor constants of the form `BIF_CFG_*__FIELD__SHIFT` and `BIF_CFG_*__FIELD_MASK` so AMDGPU code can extract or update individual fields after addressing a register with the companion `nbio_7_2_0_offset.h` header.

The selected range starts inside the `DEV0_EPF6` PCIe capability layout, covers the full `DEV0_EPF7` endpoint-function field map, and ends after the first identity/class fields for `DEV1_EPF0`. It contains no executable code, no storage, and no C types; its API is the macro namespace consumed by register helpers and field helper macros elsewhere in the AMDGPU driver.

## Public Surface In This Chunk

The public surface is a dense set of `#define` constants:

- `*_SHIFT` macros provide the least-significant bit position of a field within a PCI config word or dword.
- `*_MASK` macros provide the already-positioned bit mask for that field.
- Register grouping comments such as `//BIF_CFG_DEV0_EPF7_0_PCIE_UNCORR_ERR_STATUS` identify the register whose fields follow.
- Address-block comments identify generated hardware blocks; this chunk includes `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp` and begins `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`.

The chunk continues `DEV0_EPF6` at `DEVICE_CAP` masks and then covers its PCIe device/link control and status registers, MSI/MSI-X fields, vendor-specific enhanced capability fields, AER fields, enhanced BAR fields, power-budget and Dynamic Power Allocation fields, ACS, PASID, ARI, TPH requester fields, and all 64 TPH steering-table entries.

The complete `DEV0_EPF7` block covers the standard PCI header fields from vendor/device ID through BARs, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, and timing fields. It then defines PM capability fields, PCIe capability fields, device/link capability/control/status fields, MSI and MSI-X configuration fields, vendor-specific and AER enhanced capability fields, enhanced BAR controls, power budget, DPA, ACS, PASID, ARI, TPH requester capability/control, and TPH steering table entries 0-63. The chunk finishes by starting `DEV1_EPF0` with vendor/device ID, command/status, revision ID, programming interface, subclass, and base-class field masks.

## Important Register Families

For `DEV0_EPF6` and `DEV0_EPF7`, the PCIe capability fields describe endpoint link and device behavior: maximum payload and read request sizes, extended tags, no-snoop and relaxed ordering enables, FLR capability and initiation, completion timeout support/control, atomic operation support, LTR and OBFF support, link speed/width capability, ASPM and clock power management controls, retrain/link-disable controls, equalization-related link status 2 bits, and link bandwidth notification status.

Interrupt-related definitions cover MSI and MSI-X capability list headers plus message control, 32-bit and 64-bit message address/data aliases, mask and pending bits, MSI-X table and pending-bit-array BAR indicators/offsets, function masking, and table size. These constants are field definitions only; actual interrupt enablement and delivery state is held in hardware and managed by AMDGPU/PCI core code.

AER definitions cover uncorrectable error status, mask, and severity fields such as data-link protocol error, surprise down, poisoned TLP, flow control protocol error, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable error fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, header log overflow, and parity error. The AER capability/control block adds first-error pointer, ECRC generation/check capability/enables, multiple header recording, TLP prefix log presence, and completion-timeout prefix/header-log controls.

Capability-extension definitions include enhanced BAR capability/control pairs for BAR1 through BAR6, power-budget data selection/data/capability, DPA substate support/status/control and per-substate power allocations, ACS capability/control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and enhanced capability, PASID width/execute/privileged-mode capability and enables, ARI next-function/function-group controls, and TPH requester support/mode/enable controls.

TPH steering-table entries dominate the tail of both EPF6 and EPF7 coverage. Each table register exposes `TPH_ST_LOWER_ENTRY` at bits 0-7 and `TPH_ST_UPPER_ENTRY` at bits 8-15. Entries are paired by register in the offset header, so consumers must combine these masks with the matching register offset and not assume each table entry has independent register storage.

The `DEV1_EPF0` portion at the end is intentionally partial. It begins the same endpoint-function pattern, defining identity and class-code fields plus PCI command/status bits such as I/O access, memory access, bus master enable, parity/SERR handling, interrupt disable, capability-list presence, target/master abort status, system error, and parity error detected. The rest of `DEV1_EPF0` is outside this selected line range.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A C translation unit includes `nbio/nbio_7_2_0_sh_mask.h`, usually alongside `nbio/nbio_7_2_0_offset.h`.
2. The caller selects a register offset such as `regBIF_CFG_DEV0_EPF7_0_DEVICE_CNTL` from the offset header.
3. The caller uses these `*_SHIFT` and `*_MASK` constants directly, or through helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, to decode or compose register values.
4. Register reads and writes happen through AMDGPU accessors such as SOC15/NBIO or PCIe-port helpers outside this generated header.

The header itself stores no state and has no persistence behavior. Persistent or externally visible state lives in NBIO PCI/PCIe configuration registers and in host-visible PCI configuration space. Depending on the field, writes can change endpoint decode, bus mastering, link behavior, power-management policy, MSI/MSI-X interrupt routing, AER reporting/masking, ACS isolation, PASID/ARI behavior, TPH steering, and DPA power allocation.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header contract: names in this shift/mask file must align exactly with register names and offsets in `nbio_7_2_0_offset.h`. The offsets select the hardware register, while this file describes how to interpret that register's bitfields. `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes both headers and uses the same field/mask convention with AMDGPU register helpers; other NBIO 7.2 consumers follow the same generated macro pattern.

The semantic dependencies are PCI and PCI Express configuration-space definitions for endpoint functions, PM capability, MSI, MSI-X, PCIe capability, advanced error reporting, vendor-specific enhanced capabilities, resizable/enhanced BAR control, power budget, Dynamic Power Allocation, ACS, PASID, ARI, and TPH requester capability. The header does not encode access width, write-one-to-clear behavior, reserved-bit requirements, capability-list traversal, sequencing constraints, or ASIC-specific policy; those obligations remain with the code that reads or writes the registers.

Integration is especially sensitive for multi-function endpoint blocks. The `DEV0_EPF6` and `DEV0_EPF7` namespaces describe different endpoint functions with highly repetitive field layouts. Code must pair a field macro with the corresponding `regBIF_CFG_DEV*_EPF*_0_*` offset and base index from the offset header. Reusing an EPF6 field with an EPF7 register may be harmless only when the layouts are identical; relying on that accidentally makes generated-header drift difficult to detect.

## Risks And Maintenance Notes

- The line range starts in the middle of `DEV0_EPF6`; the earlier standard header, PM, and initial PCIe capability fields for EPF6 are in a previous chunk.
- The range ends just after `DEV1_EPF0_0_BASE_CLASS`; the remainder of `DEV1_EPF0` is covered by later chunks and must be merged before drawing whole-file conclusions.
- Generated masks must match the hardware register specification exactly. A wrong bit position can silently corrupt link control, AER masking, interrupt delivery, BAR behavior, or isolation features.
- Some status fields may be write-one-to-clear in hardware even though this header only exposes masks. Generic read-modify-write code can lose events if it treats all masks as ordinary read/write bits.
- Link-control fields such as retrain, disable, equalization controls, ASPM, and clock power management can affect PCIe link stability and should not be modified outside the driver's established sequencing.
- AER, ACS, PASID, ARI, and TPH fields affect reliability, isolation, address interpretation, routing, and performance. Incorrect programming can produce data corruption, security isolation problems, or hard-to-debug PCIe errors.
- Repeated TPH steering table definitions are easy to review incorrectly because every entry has the same lower/upper-entry mask pattern. Cross-checking generator output against the offset header is more reliable than manual review.
- Shared register storage is expected for packed PCI config fields, such as command/status, device control/status, link control/status, DPA status/control, ACS capability/control, PASID capability/control, ARI capability/control, and paired TPH entries. Consumers must use the correct mask and access width.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for AMDGPU NBIO 7.2 users that include `nbio_7_2_0_sh_mask.h` and exercise `REG_GET_FIELD`/`REG_SET_FIELD` calls with generated NBIO masks.
- Static checks that every `BIF_CFG_DEV0_EPF6_0_*`, `BIF_CFG_DEV0_EPF7_0_*`, and partial `BIF_CFG_DEV1_EPF0_0_*` field group in this chunk has a matching register offset in `nbio_7_2_0_offset.h`.
- Generator consistency checks that each field has matching `__SHIFT` and `_MASK` values with no overlapping masks inside a register except where the hardware layout intentionally aliases packed views.
- Hardware register dump comparison on NBIO 7.2 ASICs against PCI config-space tools such as `lspci -vvxxx`, especially for capability pointers, command/status, device/link capability, MSI/MSI-X, AER, ACS/PASID/ARI, and TPH requester tables.
- Runtime error-path tests that inject or observe AER events and confirm status, mask, and severity fields decode correctly without clearing unrelated bits.
- Link-management tests covering negotiated speed/width, retrain status, bandwidth notifications, and link status 2 fields while verifying that mask values do not disturb reserved or write-sensitive bits.
- Interrupt tests that validate MSI/MSI-X message control, masking, pending bits, table/PBA offset decoding, and function-mask behavior after driver initialization and reset paths.
