# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 36865-39263

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains 2,149 `#define` field-layout macros across 2,399 source lines. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range starts inside the mask half of `RCC_STRAP1_RCC_BIF_STRAP1`, then covers the rest of the `RCC_STRAP1` strap block for BIF and device 0, endpoint/downstream/RCC control blocks for BIFDEC1, the `BIF_BX1` NBIF/BIF block, the `BIF_BX_PF1` physical-function block, and the beginning of the internal `RCC_STRAP2` device 0 strap block. The chunk ends in the early shift definitions for `RCC_STRAP2_RCC_DEV0_PORT_STRAP2`, so adjacent chunks are needed for complete `RCC_STRAP1` and `RCC_STRAP2` context.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.7.0 register interface. For every named register, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the field bit position.
- `<REGISTER>__<FIELD>_MASK`, the field mask in the raw register value.

The companion `nbio_7_7_0_offset.h` supplies matching `reg...` addresses and `*_BASE_IDX` values. Runtime AMDGPU code combines those offsets and these masks through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

This chunk documents NBIO/BIF PCIe strap policy, endpoint and downstream-port PCIe controls, RCC host/peer/bus-number controls, BIF block state, GPUIOV VF access gates, HDP coherency flush controls, and PF mailbox registers. These definitions are hardware metadata, not Ceph/distributed-filesystem logic despite the repository path.

## Important Macro Families

The `RCC_STRAP1_RCC_BIF_STRAP*` macros define boot/strap-derived NBIO and PCIe policy: software-user aperture enable/size/prefetchability, fuse/ROM strap validity, register write-disable, link reset behavior, DLF, Gen3/Gen4/Gen5 kill or PHY enable bits, ASPM/L1 timers, link-down DMA-drop policy, power-break debounce and status timers, emergency power reduction, SMN error-response forcing, alternate protocol enable, and vlink low-power timers.

The `RCC_STRAP1_RCC_DEV0_PORT_STRAP*` and `RCC_STRAP2_RCC_DEV0_PORT_STRAP*` families expose downstream-port capability straps for device 0. They include ARI, ACS, AER, completion-abort, device/subsystem/vendor IDs, interrupt pin, max payload, max link width, DSN, ECRC, extended tag/format, VC count, L0s/L1 acceptable and exit latency, LTR, OBFF, atomic operation support, DPA, power-budget data, SR-IOV counts and strides, page sizes, VF BAR masks, Modified TS, Alternate Protocol, and Readiness Time Reporting fields.

The `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*` and `RCC_STRAP1_RCC_DEV0_EPF1_STRAP*` families describe endpoint-function strap fields. EPF0 includes PCI command defaults, vendor/device/class IDs, revision IDs, BAR masks and control bits, memory and bus-master enable behavior, MSI/MSI-X-related capability toggles, PASID/ARI/ACS/SR-IOV enablement, power capability metadata, and GPUIOV-facing VF resource fields. EPF1 provides analogous function-1 identity, command, BAR, power, atomic, ACS, and capability toggles for a second endpoint function.

The `RCC_EP_DEV0_1_*`, `RCC_DWN_DEV0_1_*`, `RCC_DWNP_DEV0_1_*`, and `RCC_DEV0_1_*` blocks define live RCC endpoint, downstream, downstream-port, and common device registers. These fields cover PCIe scratch/control, interrupt enable/status, RX/TX control, bus/config controls, LTR transmit control, DPA capability and substate power allocations, PME controls, error controls, link speed controls, BACO/reset/VDM support, margin parameters, GPUIOV region and host-VM controls, console IOV VF layout, peer register and FB ranges, bus-number lists, requester-ID restore, LTR local-switch control, and memory-hub arbitration.

The `BIF_BX1_*` block defines the second BIF/BX instance. It includes BIF straps and pinstraps, MM indirect access controls, bus control, scratch registers, reset controls, interrupt controls, clock-request and pad controls, BIF feature controls, doorbell control and interrupts, FB read/write enable, transaction-pending status for VFs, BACO control and exit timers, memory type control, NBIF GFX address LUT control and entries 0-15, GPUIOV VF register-write/doorbell/FB enable and status bitmaps, HDP register remap controls, BIF ring-buffer control/base/read/write pointers, mailbox index, VCN and GFX/SDMA GPUIOV config sizes, and PERST/PX/REFCLK/CLKREQ/PWRBRK pad controls.

The `BIF_BX_PF1_*` block defines physical-function 1 fields. It includes bus-master-enable status, atomic error logging, doorbell self-ring GPA aperture base/control, HDP register/memory coherency flush controls, flush-only and invalidate-only request bits, full GPU HDP flush request/done bits for CP0-CP9, SDMA0-1, and reserved engines 0-19, master/slave transaction-pending bits, NBIF GFX address-LUT bypass, four transmit and four receive mailbox message-buffer DWORDs, mailbox valid/ack control, mailbox interrupt enables, and compact VM/hypervisor mailbox data/valid/ack fields.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, typically with an `L` suffix, and encode only bit positions and masks.

The macros do not encode reset values, access permissions, write-one-to-clear behavior, ordering requirements, privilege level, or whether a bit is a status, capability, policy, command, or side-effectful latch. Those semantics come from the hardware specification, the matching offset/default database, firmware setup, and the AMDGPU register-access code that consumes the macros.

## Control Flow

This header has no local runtime control flow. The effective flow is external:

1. NBIO 7.7 code includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. The driver selects a register offset with a `reg...` macro and reads or prepares a 32-bit value through the SOC15/NBIO access layer.
3. The driver extracts or composes fields with the generated `__SHIFT` and `_MASK` constants, usually via AMDGPU field helpers.
4. The resulting value drives device bring-up, interrupt setup, doorbell setup, HDP flush programming, PCIe policy, virtualization state, reset handling, or diagnostics.

The direct include user in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`. In that file, sibling macros from this generated header are used to enable BIF FB reads/writes, program interrupt control, enable doorbell apertures, expose HDP flush request/done offsets, and publish the NBIO HDP flush done masks consumed by GFX and SDMA ring flush paths. This chunk's `BIF_BX_PF1_*` forms the same PF1 register vocabulary used by closely related NBIO 7.11 code, while NBIO 7.7's direct code path primarily programs PF0 for the selected ASIC instance.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCIe/RCC/BIF registers. Persistence is controlled by ASIC reset domains, PCI reset and function-level reset, firmware strap loading, BACO and suspend/resume flows, SR-IOV PF/VF management, and explicit driver writes.

Represented persistent or semi-persistent state includes strap-derived PCIe capabilities, endpoint identity, BAR/resource policy, interrupt capability routing, bus-master and memory decode gates, link speed/width capability, ASPM and LTR timing, AER/ECRC policy, ACS/ARI/PASID/SR-IOV virtualization controls, GPUIOV VF aperture enable/status maps, peer and bus-number routing, BACO/reset behavior, mailbox buffers and valid/ack handshakes, and HDP coherency flush request/done status.

Several fields are side-effectful or externally visible. Bus-master and FB enable bits gate DMA/MMIO behavior; reset and BACO fields can change device power/reset state; link-speed and RX/TX controls interact with live PCIe link training; AER/ECRC/status fields can be sticky or write-one-to-clear; HDP flush request bits trigger coherency operations and are polled through corresponding done bits; mailbox valid/ack bits synchronize PF/VF or VM/hypervisor communication; GPUIOV enable and status bitmaps affect VF access to registers, doorbells, and framebuffer.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 7.7.0 register database. This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which supplies matching addresses and base indices. Spot checks show matching offsets for representative registers in this chunk, including `regRCC_STRAP1_RCC_BIF_STRAP2` at base index 5, `regBIF_BX1_BIF_FB_EN` at base index 5, `regBIF_BX_PF1_GPU_HDP_FLUSH_REQ` at base index 5, `regBIF_BX_PF1_MAILBOX_CONTROL` at base index 5, and `regRCC_STRAP2_RCC_DEV0_PORT_STRAP0` at base index 5. This directory does not contain a same-generation `nbio_7_7_0_default.h` or `nbio_7_7_0_smn.h`, so reset/default validation for these fields cannot be derived from a local 7.7.0 default header.

Runtime integration is through AMDGPU's NBIO 7.7 implementation, the SOC15 register helpers, and shared ring/HDP flush paths. HDP flush masks published by NBIO are consumed by GFX and SDMA command emission to flush host-data-path caches before synchronization. Doorbell and interrupt fields connect to queue submission, interrupt handling, and KFD remap support. The mailbox and GPUIOV fields are integration points for virtualization and PF/VF management, even when a particular ASIC path uses PF0 rather than PF1 aliases.

The semantic dependencies are the PCI, PCIe, SR-IOV, AER, ACS, ARI, PASID, DPA, LTR, ASPM, BACO, and AMD GPUIOV/NBIO hardware contracts. The generated names expose fields from those contracts but do not enforce legal sequencing or safe read-modify-write patterns.

## Risks And Edge Cases

- The chunk starts and ends mid-family. Missing adjacent context can hide the full strap layout for `RCC_STRAP1_RCC_BIF_STRAP1` and the rest of `RCC_STRAP2_RCC_DEV0_PORT_STRAP2`.
- Generated shift/mask drift can compile cleanly while causing software to preserve, clear, or set the wrong hardware bit. High-risk fields include bus-mastering, FB enable, reset/BACO, doorbell aperture, HDP flush, mailbox valid/ack, AER/ECRC, ACS/ARI/PASID/SR-IOV, link-speed, and GPUIOV VF access maps.
- Strap fields often describe reset-time or firmware-loaded policy. Treating them as ordinary mutable runtime controls can conflict with hardware ownership or write-disable behavior.
- Some fields are status or W1C latches. Read-modify-write on error, interrupt, flush, mailbox, or transaction-pending status can lose evidence or break handshakes if the caller does not know the hardware semantics.
- Repeated GPUIOV bitmap fields span many VF bits. A single lane/VF/index-specific generation error is hard to detect in review because surrounding definitions are mechanically similar.
- HDP flush request/done masks must match the engine numbering expected by GFX and SDMA rings. A wrong mask can produce stale memory visibility or hangs while polling for a done bit that never corresponds to the requesting engine.
- Mailbox transmit/receive valid and ack bits require ordering between data DWORD writes, valid assertion, interrupt enables, and ack clearing. The masks alone do not provide barriers or timeout policy.
- Cross-generation NBIO headers contain homologous register names with different PF instance choices, base indices, and sometimes field coverage. Mixing NBIO 7.7 offsets with masks from another generation can silently target the wrong register or field.

## Test Signals

- Build AMDGPU with NBIO 7.7 support enabled so direct users of `nbio_7_7_0_sh_mask.h`, especially `amdgpu/nbio_v7_7.c`, catch missing or renamed generated symbols.
- Run generated-header consistency checks: every visible field should have a coherent `__SHIFT`/`_MASK` pair, masks should align to shifts, fields in each register should not overlap unexpectedly, and repeated VF/engine/lane bitmap fields should follow the expected sequence.
- Cross-check this chunk against `nbio_7_7_0_offset.h` so each register family has matching address macros and the expected base index. Because no local 7.7 default header is present, compare reset values against hardware dumps or the authoritative register database.
- Runtime probe on NBIO 7.7 hardware should verify stable PCIe enumeration, correct endpoint identity and capability exposure, valid BAR/resource decode, expected bus-master and FB enable transitions, and sane link speed/width/power-management state.
- HDP flush validation should exercise GFX and SDMA ring flush paths and confirm request/done masks complete for the intended engines without stale CPU/GPU memory visibility.
- Doorbell and interrupt tests should cover aperture enablement, self-ring base programming, IH interrupt control, and absence of lost or spurious interrupts.
- Virtualization tests should cover GPUIOV VF register/doorbell/FB enable and status maps, mailbox valid/ack handshakes, PF/VF reset behavior, and SR-IOV identity/resource fields.
- PCIe error and recovery tests should observe AER/ECRC reporting, transaction-pending bits during quiesce/reset, BACO exit timing, link-down/reset behavior, and preservation of diagnostic status until explicitly cleared.
