# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 56560-57899

## Scope

This chunk is the final generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 1,107 `#define` field-layout macros over 1,340 source lines, covering 198 register names and 10 address-block comments. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the tail of `GDC1_BIF_DOORBELL_FENCE_CNTL`, continues through `GDC1_S2A_MISC_CNTL`, covers large BIF/RCC register groups for the `BX2`/`PF2` instance, and ends after the `GDC2_BIF_DOORBELL_FENCE_CNTL` masks and the file's closing `#endif`. Because this is the end of the header, no later chunk is needed to complete the final `GDC2` register group, but the first `GDC1_BIF_DOORBELL_FENCE_CNTL` register is split from the previous chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem or Ceph behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.11.0 register interface. For each hardware field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position used to encode or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

This chunk describes NBIO BIF and RCC field geometry for PCIe index/data access, BIOS and SBIOS scratch storage, engine interrupt controls, MMIO remap CAMs, PCIe downstream and endpoint controls, Dynamic Power Allocation registers, reset/interrupt/pad controls, HDP coherency flush and invalidate handshakes, mailbox transport buffers, virtualization mailbox signaling, function doorbell aperture/memsize state, and the second GDC doorbell/fence block.

## Important Macro Families

The opening `GDC1` tail completes doorbell-fence masks for SDMA4/5, CSDMA, VPE, and one-shot trigger disable, then `GDC1_S2A_MISC_CNTL` exposes 64-bit doorbell support disable bits for SDMA0-5, CP, RLC, VPE, and CSDMA plus AXI host completion and arbitration-mode fields.

The `nbio_nbif0_bif_bx_SYSDEC` block defines indirect PCIe index/data registers (`BIF_BX2_PCIE_INDEX`, `DATA`, `INDEX2`, `DATA2`), SBIOS and BIOS scratch dwords, RLC/VCE/UVD BIF interrupt-control bits, UVD instance selection, and eight-entry GFX MMIO register CAM address/remap pairs with CAM enable and completion-value registers. These macros support firmware/driver scratch exchange, indexed PCIe access, interrupt event enabling, and address remapping around selected MMIO regions.

The downstream RCC blocks cover `RCC_DWN_DEV0_3_*` and `RCC_DWNP_DEV0_3_*` PCIe controls. Field names include hardware-init write lock, unsupported-request reporting disables, LTR message handling, PCIe config access settings, RX/TX and bus controls, error-control bits, link-speed control, link-control 2, and LTR message information from the endpoint.

The endpoint RCC block covers `RCC_EP_DEV0_3_*` registers for endpoint scratch, control, interrupt control/status, RX/BUS/CFG controls, TX LTR control, PME control, PCIe reserved/tx/requester/error/rx/link-speed controls, and PCIe Dynamic Power Allocation. DPA fields include function 1 substate power allocation entries 0-7 and function 0 DPA capability, latency indicator, control, and substate power allocation entries 0-7.

The BIF PF/SYS blocks define PF2 MM indirect access macros (`MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`), BIF MM indirect-access control, bus control, BIF scratch registers, reset enable/control, config-register control, interrupt controls, pad controls, feature controls, HDP atomic control, doorbell control and interrupt control, framebuffer enable, BIF interrupt control, VF master/slave transaction pending vectors, BACO control and exit timers, memory-type control, sixteen NBIF GFX address LUT entries, GFX reset control, remapped HDP flush controls, BIF ring-buffer base/read/write pointer registers, mailbox index, GPUIOV config size, and PERST/PX/REFPADKIN/CLKREQ/PWRBRK pad controls.

The PF2 BIFPFVF block covers bus-master-enable status, atomic error logging, doorbell self-ring GPA aperture base/control, HDP register and memory coherency flush controls, flush-only and invalidate-only request/done vectors for CP, SDMA, UVD, VCE, RLC, VPE, ACP, and reserved engines, BIF master/slave transaction-pending flags, address-LUT bypass, four transmit and four receive mailbox message-buffer dwords, mailbox valid/ack control, mailbox interrupt enables, and compact VM/HV mailbox data/valid/ack/intr bits.

The final endpoint-function block exposes `RCC_DEV0_EPF0_1_RCC_DOORBELL_APER_EN` and `RCC_CONFIG_MEMSIZE`, indicating per-function doorbell aperture enablement and memory-size configuration. The closing `GDC2` block mirrors the GDC doorbell theme with A2S queue FIFO arbitration, GFX doorbell-sent status, doorbell ranges for SDMA0-5, IH, VCN0/1, RLC, CSDMA, and VPE, ATDMA arbitration/weight controls, and `GDC2_BIF_DOORBELL_FENCE_CNTL` enable bits for CP, SDMA0-5, RLC, CSDMA, VPE, and one-shot trigger disable.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. The constants are untyped integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not encode register addresses, defaults, access widths, read/write permissions, reset domains, clear semantics, or sequencing. Consumers must use the matching generated address/default metadata, such as NBIO 7.11.0 offset/SMN/default headers, together with AMDGPU bitfield and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the appropriate PCI config, MMIO-indirect, SMN, NBIO, or mailbox access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU, firmware-facing, virtualization, PCIe, or power-management code selects a register address from companion NBIO generated metadata.
2. It reads a hardware register and decodes fields with the `__SHIFT` and `_MASK` constants, or creates a write value by inserting field values while preserving unrelated and reserved bits.
3. The resulting values drive PCIe configuration, BIF reset and interrupt behavior, doorbell aperture and range programming, HDP coherency operations, mailbox handshakes, address remap/LUT decisions, power-management state, or transaction-pending polling.

The field names imply several asynchronous hardware flows outside this file: doorbell delivery and fencing, MMIO/PCIe indirect register access, firmware scratch exchange, engine command/hang/VM-busy interrupts, endpoint LTR/PME/DPA negotiation, BACO exit timing, HDP flush/invalidate request-done handshakes, GPU-to-host or VM/HV mailbox valid/ack protocols, and GDC queue arbitration.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO registers. Persistence depends on GPU reset domains, PCIe reset, BACO or power-gating transitions, firmware/BIOS initialization, PSP/SMU ownership, SR-IOV or hypervisor ownership, suspend/resume restore, and explicit driver writes.

Represented state includes BIOS/SBIOS and BIF scratch dwords, PCIe control and error-policy bits, interrupt enable/status fields, MMIO CAM address/remap entries, endpoint DPA power allocation records, reset/pad/power controls, BACO exit timers, memory-type and address-LUT programming, BIF ring-buffer pointers, mailbox payload and valid/ack bits, doorbell aperture and range definitions, HDP coherency request and completion vectors, and GDC arbitration/doorbell-fence controls.

Several names indicate status, latch, or handshake semantics (`INT_STATUS`, `TRANS_PENDING`, `FLUSH_REQ`, `FLUSH_DONE`, `VALID`, `ACK`, `BME_STATUS`, `DOORBELL_SENT`). The shift/mask header does not define how those bits clear, whether reads are destructive, or which bits are write-one-to-clear; callers must follow the hardware specification and companion generated metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database and must stay synchronized with sibling headers that provide register addresses, default values, and access routing. It is intended to be included through AMDGPU ASIC register include stacks under `drivers/gpu/drm/amd/include/asic_reg/nbio`.

Primary integration points are AMDGPU NBIO/BIF code, PCIe config and link-management paths, firmware and SBIOS handoff paths, engine interrupt handling for RLC/VCE/UVD, GFX MMIO remapping, PCIe endpoint/root-complex controls, dynamic power-management, BACO reset/power transitions, SR-IOV or hypervisor mailbox paths, HDP cache/coherency flush logic, doorbell setup for CP/SDMA/IH/VCN/RLC/CSDMA/VPE, and GPUIOV configuration.

The PF2 mailbox and VM/HV mailbox fields are especially tied to virtualization and host-driver coordination. The HDP coherency request/done fields integrate with memory visibility between GPU engines and host-visible apertures. The GDC doorbell range and fence fields integrate with queue submission plumbing because incorrect doorbell routing can prevent work from reaching the intended engine.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while targeting the wrong hardware bit, causing PCIe configuration failures, reset hangs, missed interrupts, incorrect doorbell routing, or broken coherency flushes.
- This chunk begins mid-register with `GDC1_BIF_DOORBELL_FENCE_CNTL`; whole-file reconciliation must merge the preceding CP/SDMA/RLC fields from the previous chunk before treating that register as complete.
- Repeated scratch, CAM, DPA substate, LUT, mailbox-buffer, HDP engine-vector, and doorbell-range definitions are mechanically patterned. A single index mismatch can create function-, engine-, or instance-specific failures that are hard to reproduce.
- Doorbell range fields use offset and size masks with different widths for CSDMA compared with most other GDC2 ranges. Consumers must not assume every engine range has the same size encoding.
- HDP flush and invalidate request/done vectors span many named engines and reserved engines. Code must poll the correct done bit for the requested engine and avoid clearing or overwriting unrelated pending requests.
- Mailbox valid/ack fields require ordered handshakes. Writing message-buffer dwords without the expected valid/ack sequencing can drop messages, duplicate notifications, or wedge host/guest communication.
- Reset, BACO, pad-control, and clock/power fields can affect link availability or physical signaling. Writes need hardware-specific ordering and wait conditions not represented in this header.
- PCIe error-control, unsupported-request, LTR, PME, and DPA fields affect platform power and error reporting. Incorrect values can hide real faults, generate spurious PCIe errors, or break low-power transitions.
- BIOS/SBIOS scratch and firmware-owned registers may be shared with platform firmware. Driver updates must preserve ownership rules and avoid treating scratch state as stable across reset or suspend.
- Transaction-pending status and BME status are observations of in-flight hardware state. Polling code must include timeouts and reset-aware behavior.

## Test Signals

- Build AMDGPU with NBIO 7.11.0 support enabled. Compile-time coverage catches removed, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should fit 32-bit register width, repeated indexed groups should preserve stride/index naming, and boundary registers should be reconciled with adjacent chunks.
- Cross-check every register name in this chunk against NBIO 7.11.0 address/default headers so field layouts map to known registers and reset values.
- On supported hardware, validate PCIe enumeration, bus mastering, link speed changes, LTR/PME behavior, DPA state reporting, suspend/resume, BACO entry/exit, and GPU reset recovery.
- Exercise queue submission and doorbell paths for CP, SDMA0-5, IH, VCN0/1, RLC, CSDMA, and VPE; confirm doorbell ranges, aperture enables, sent status, and fence controls match expected engine behavior.
- Exercise HDP coherency flush and invalidate paths under CPU/GPU shared-memory workloads; trace request and done bits for selected engines and watch for stale data or timeout regressions.
- Exercise virtualization or host/guest mailbox flows where available, confirming message dwords, valid/ack bits, and mailbox interrupts progress in the documented order.
- Validate interrupt controls for RLC, VCE, and UVD command-complete, hang, and VM-busy events where hardware and test firmware support injection or observation.
- Check MMIO CAM and address-LUT programming with register traces to ensure remap and bypass settings preserve reserved bits and do not alias unrelated MMIO space.
