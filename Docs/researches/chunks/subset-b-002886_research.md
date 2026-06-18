# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 22599-25014

## Scope And Purpose

This chunk is a generated AMD NBIF 6.3.1 shift/mask header segment. It contains no executable C code, functions, structs, or persistent software objects. Its purpose is to publish preprocessor constants that name bit positions and bit masks for NBIF/NBIO hardware registers so driver code can read, write, and preserve individual register fields through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15`.

The selected range starts in the middle of the `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` field list, with the corresponding register family beginning just above the requested line range. From there it covers the rest of the PF1 BIF/PFVF register field definitions, an extensive `RCC_STRAP2` strap block, GDC DMA/HST SION arbitration and credit controls, GDC core and power/clock controls, GDC RAS controls/status registers, GDC reset controls, GDC S2A doorbell routing controls, A2S arbitration and tag allocation controls, syshub direct reset/NIC400 overrides, and the start of the device/function VF0 BIF/PFVF register field definitions.

The chunk is source-tree-aligned with AMDGPU's NBIF/NBIO hardware support. Its constants are only meaningful together with sibling generated register offset definitions from `nbif_6_3_1_offset.h` and with the driver code that selects the matching register namespace for the ASIC instance/function being programmed.

## Important APIs, Types, And Macro Families

There are no C APIs or types defined here. The "interface" is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.
- Register address symbols with matching `<REGISTER>` names live in `nbif_6_3_1_offset.h`.
- Consumers rely on the AMDGPU register helpers to combine these field constants with read-modify-write operations.

The PF1 BIF/PFVF families cover a second physical-function style register namespace. `BIF_BX_PF1_BIF_BME_STATUS` reports and clears DMA activity observed while bus mastering is low. `BIF_BX_PF1_BIF_ATOMIC_ERR_LOG` reports unsupported-request atomic error causes such as opcode, request-enable-low, length, and non-relaxed cases, with separate clear bits. `BIF_BX_PF1_DOORBELL_SELFRING_GPA_APER_*` defines the low/high base and enable/mode/size fields for the doorbell self-ring GPA aperture. `BIF_BX_PF1_HDP_*_COHERENCY_*` provides one-bit control fields for HDP register and memory coherency flush, flush-only, and invalidate-only controls.

The PF1 HDP flush request/done families are repeated 32-bit bitmaps. Bits 0-9 map command processor engines `CP0` through `CP9`, bits 10-11 map `SDMA0` and `SDMA1`, and bits 12-31 are reserved engine slots. `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` is the request bitmap, while `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` is the completion/status bitmap. The same layout appears later for `BIF_BX_DEV0_EPF0_VF0_GPU_HDP_FLUSH_REQ` and the beginning of `..._DONE` for VF0.

The PF1 mailbox families define 32-bit transmit and receive message buffers, a four-bit handshake in `BIF_BX_PF1_MAILBOX_CONTROL` (`TRN_MSG_VALID`, `TRN_MSG_ACK`, `RCV_MSG_VALID`, `RCV_MSG_ACK`), interrupt enables for valid/ack transitions, and a compact VM/HV mailbox register with 4-bit transmit/receive payload fields, valid/ack bits, and interrupt enable bits. These are low-level hardware communication registers, not software queues.

The `RCC_STRAP2` block describes strap-derived PCIe/NBIF configuration. The general BIF strap registers include link-generation disables and kills, VGA/ROM/memory aperture pins, GPUIOV enablement, local prefix/error ignore policy, link-down reset, fuse/ROM strap validity, write-disable, SWUS aperture settings, DLF/margining/PHY support, PCIe extended capability behavior, lane equalization, target link speed, and reset/link power policy. Device port straps describe downstream-port capabilities such as LTR, MSI, timeout, OBFF, power budget data, atomics, virtual channels, ACS controls, 10-bit tags, TPH, Gen5 compliance, port identity, bus/device/function numbers, and vendor ID. EPF0 and EPF1 straps describe function identity, SR-IOV, page-size/VF counts, class/vendor/subsystem IDs, reset-time-reporting timings, PASID/ATS/PRI-related capabilities, MSI/MSI-X, AER/ACS, FLR, PME, BAR/aperture sizing, VF BAR sizing, GPUIOV VSEC revision, and other capability exposure.

The `nbif_gdc_dma_sion_SIONDEC` and `nbif_gdc_hst_sion_SIONDEC` blocks define sideband/interconnect arbitration for DMA and host-facing SION client lanes. For DMA clients CL0-CL3 and host clients CL0-CL1, the macros cover read-response, write-response, and request burst target registers, time-slot registers, request/data/read-response/write-response pool credit allocation registers, and per-block control registers with clock-gating enable/mode/hysteresis and live-active fields. These fields tune traffic shaping and resource allocation rather than implementing a software algorithm.

The `nbif_gdc_GDCDEC` block defines GDC-level controls. `GDC1_SHUB_REGS_IF_CTL` controls non-PF MMREG request handling and VF protection. `GDC1_A2S_QUEUE_FIFO_ARB_CNTL`, `GDC1_S2A_MISC_CNTL`, and `GDC1_ATDMA_MISC_CNTL` expose arbitration priorities, arbitration modes, and weighted round-robin weights. `GDC1_NGDC_MGCG_CTRL`, `GDC1_NGDC_EARLY_WAKEUP_CTRL`, `GDC1_NGDC_PG_MISC_CTRL`, `GDC1_NGDC_PGMST_CTRL`, and `GDC1_NGDC_PGSLV_CTRL` define medium-grain clock gating, SRAM fine-grain clock gating, early wakeup, power-gating, idleness, firmware exit, and clock idle hysteresis controls.

The `nbif_gdc_ras_gdc_ras_regblk` block provides GDC RAS/error response control and observability. `GDCSOC_ERR_RSP_CNTL` can bypass, accumulate, or force read-response status/data-status behavior. `GDCSOC_RAS_CENTRAL_STATUS` summarizes L2C and C2L egress-stall and error-event detections. Leaf control registers 0-4 repeat enable bits for error-event detection, poison/parity/receiver-error event and stall handling, generation/propagation of error events and egress stalls, MCA logging, UCP, and for leaf2 a RAS interrupt enable. Leaf2 misc controls define RAS drop, interrupt mask disable, ATHUB request/response action, and dummy-chain controls. Leaf status registers report error event received, poison/parity detection, generated status, propagated status, and egress-stall status.

The `nbif_gdc_rst_GDCRST_DEC` block describes reset controls for PF FLR, graphics driver/VPU reset, link reset, hard reset, soft reset, SDP port reset, and reset-misc trailer settings. These fields distinguish reset enable, action, mask, completion, global assertion, link-reset selection, hard/soft reset modes, and per-port reset bits.

The `nbif_gdc_s2a_GDCS2A_DEC` block maps sixteen `GDC_S2A1_S2A_DOORBELL_ENTRY_N_CTRL` registers. Each entry has enable, AWID, range offset, range size, address-high nibble value, address-high compare enable, and BIF queue-select fields. The common control register defines BIF doorbell packet mode and the NBIF graphics doorbell status register exposes `DOORBELL_INTERRUPT_STATUS`. These fields gate which doorbell address ranges are routed to which clients.

The `nbif_gdc_a2s_GDCA2S_DEC` block defines A2S traffic controls: static/dynamic virtual-channel selection, SDP write-chain disable controls, write tag behavior for chained and non-chained writes, read/write WRR weights, message block level, response accumulation selection, read-response priority, and tag allocation counts for VC0, VC1, VC3, and VC7.

The syshub direct block contains small reset and fabric override controls: `HST_CLK0_SW0_CL0_CNTL`, `HST_CLK0_SW1_CL0_CNTL`, and `DMA_CLK0_SW0_CL0_CNTL` can enable FLR or link-reset behavior on reset sequencers; `NIC400_1_ASIB_0_FN_MOD` and `NIC400_1_IB_0_FN_MOD` expose read/write issuing override bits.

The VF0 BIF/PFVF block at the end mirrors the PF BME status, atomic error log, doorbell self-ring GPA aperture, HDP coherency flush, and GPU HDP flush request/done layout for `BIF_BX_DEV0_EPF0_VF0_*`. This is the virtual-function scoped register namespace for the same classes of behavior.

## Control Flow And Runtime Use

This header has no runtime control flow. It participates at preprocessing and compile time: a driver source file names a register and field, then macro expansion supplies the shift and mask used to construct or extract a hardware register value.

The main NBIF 6.3.1 integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes `nbif_6_3_1_offset.h` and this header. That C file primarily uses the PF0 version of the same generated register families for this ASIC generation. For example, `nbif_v6_3_1_enable_doorbell_selfring_aperture()` sets the self-ring aperture enable, mode, and size fields, then writes low/high doorbell base registers. `nbif_v6_3_1_get_hdp_flush_req_offset()` and `nbif_v6_3_1_get_hdp_flush_done_offset()` return the HDP flush request/done offsets, and `nbif_v6_3_1_hdp_flush_reg` stores per-engine done masks for common HDP flush handling.

The PF1 names covered by this chunk are directly visible in related NBIO code, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`. There, `nbio_v7_11_enable_doorbell_selfring_aperture()` uses `BIF_BX_PF1_DOORBELL_SELFRING_GPA_APER_CNTL` fields to enable and size the self-ring aperture, writes the PF1 self-ring GPA base registers, and then writes the PF1 aperture control register. The same file returns PF1 HDP flush request/done offsets and fills `nbio_v7_11_hdp_flush_reg` with the PF1 `GPU_HDP_FLUSH_DONE` engine masks.

S2A doorbell entry fields are used by NBIF/NBIO doorbell range setup paths. In `nbif_v6_3_1.c`, the visible code uses S2A0 entry macros to program SDMA and IH doorbell windows by setting enable, AWID, range offset, range size, and address-high fields. This chunk's S2A1 entry macros provide the same style of register surface for the S2A1 block.

The strap, RAS, reset, GDC power/clock, SION arbitration, A2S, and syshub macros are mostly hardware register surface in this tree. They may be read by init, diagnostics, firmware, virtualization, RAS, or future power/traffic-management code, but the header itself does not dictate sequencing. Correct sequencing lives in the NBIF/NBIO driver, firmware interface, and ASIC programming guide.

## State And Persistence Behavior

No software state is allocated or persisted by this header. Including it only adds macro definitions to a compilation unit.

The hardware registers described by the macros do hold device state. Important state classes include PF/VF DMA and BME-low latches, atomic error logs and clear bits, HDP coherency flush request/done state, mailbox message payloads and valid/ack handshakes, PCIe strap-derived capability exposure, SR-IOV and GPUIOV capability/control exposure, doorbell self-ring base and aperture enablement, S2A doorbell routing windows, SION arbitration/credit allocations, GDC clock/power-gating policy, RAS detection/propagation/logging controls, RAS status latches, and reset controls.

Many fields in this range are persistent until the device is reset or the driver/firmware reprograms them. Strap fields may be read-only or effectively fixed after fuse/ROM strap sampling. Status fields such as RAS central/leaf status, BME-low status, atomic error status, transaction-pending bits, mailbox valid/ack bits, and HDP flush done bits are hardware-updated. Clear fields such as `CLEAR_DMA_ON_BME_LOW` and `CLEAR_UR_ATOMIC_*` are write-control fields. The masks do not encode access permissions, side effects, or write-one-to-clear semantics; call sites must know that behavior from the register specification.

State persistence is security-sensitive for virtualization fields. Incorrect GPUIOV/SR-IOV strap interpretation, VF aperture sizing, VF register protection, VF doorbell mapping mode, ATS/PASID/PRI exposure, or non-PF MMREG request handling can affect isolation between PFs, VFs, and guests.

## Dependencies And Integration Points

The immediate dependency is `nbif_6_3_1_offset.h`, which supplies the register addresses and base indices corresponding to these field layouts. Consumers must pair the correct offset symbol with the matching shift/mask register namespace; mixing PF0, PF1, BIF_BX0, BIF_BX1, S2A0, S2A1, or VF0 families can compile while programming the wrong register.

The generated field names depend on AMDGPU's register helper conventions. `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` expects both `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` to exist. `REG_GET_FIELD` has the same naming dependency for extracting bitfields. `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET` supply the SOC15 register access path and base-index selection.

Direct include integration points include `amdgpu/nbif_v6_3_1.c` and display resource code that includes the NBIF 6.3.1 offsets. Related PF1 use appears in `amdgpu/nbio_v7_11.c`, where the same register family names are used to implement doorbell self-ring aperture setup and HDP flush offsets/masks. Broader AMDGPU subsystems that consume the resulting NBIO/NBIF hooks include KFD doorbell remapping, interrupt handling, SDMA/IH doorbell setup, HDP cache flush synchronization, PCIe/RSMU indexed access, reset handling, SR-IOV/GPUIOV support, RAS logging, and power management.

The mailbox and VM/HV mailbox definitions are integration points for low-level firmware or hypervisor communication flows. The RAS definitions integrate with any code that enables, injects, logs, or reports GDC error events. The SION/A2S/GDC arbitration definitions integrate with performance, traffic-shaping, and QoS tuning. The strap definitions integrate with capability discovery and emulated PCI configuration exposure.

## Risks And Edge Cases

This file is generated hardware metadata, so manual edits are high risk. A one-bit mask or shift error can silently change the hardware field being programmed while still compiling cleanly.

The requested chunk begins after the `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` comment and initial field definitions. Any chunk-local research or automated parser must account for that boundary; the complete request family starts just above line 22599, while this chunk contains its tail plus all masks and the following done register.

PF, PF1, BIF_BX0/BIF_BX1, and VF0 register names are similar but not interchangeable. The visible NBIF 6.3.1 C path mainly uses PF0 field macros, while related NBIO 7.11 code uses PF1 macros directly. Using the wrong namespace can route doorbells or HDP flushes to the wrong function or instance.

HDP flush bits are per engine. Missing a CP or SDMA mask, using a request bit as a done bit, or polling the wrong done register can hang cache-flush waits or let GPU/CPU coherency proceed before HDP writes are visible.

Doorbell aperture programming splits a 64-bit base across low/high registers and uses a compact control register for enable, mode, and size. Wrong base splitting, stale enable state, or bad range size can make rings unreachable or expose doorbell pages outside the intended aperture.

Strap fields expose PCIe, SR-IOV, GPUIOV, ATS, PASID, ACS, BAR, MSI/MSI-X, reset, and power-management capabilities. Treating strap values as freely writable policy instead of sampled hardware configuration can break enumeration, hot reset, FLR, VF assignment, or IOMMU behavior. Fields such as `WRITE_DISABLE`, strap validity bits, reset-time-reporting values, and SR-IOV total VF counts need especially cautious interpretation.

RAS and reset fields have strong side effects. Enabling error propagation, MCA logging, RAS interrupts, egress stalls, dummy-chain behavior, PF FLR reset, hard reset, soft reset, link reset, or SDP port reset without the expected sequencing can cause device hangs, unexpected interrupts, or loss of in-flight transactions.

SION/A2S arbitration and credit fields can create performance regressions that are not obvious in functional tests. Bad weights, credits, time slots, or virtual-channel mappings may only show under DMA, host-response, or doorbell-heavy workloads.

Mailbox valid/ack bits are handshake state. A caller must preserve the expected ordering between writing message buffer dwords, asserting valid, observing ack, consuming receive buffers, and clearing/acking receive state; the masks alone do not provide synchronization or locking.

## Test Signals

Build coverage should compile all AMDGPU files that include `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`. Related NBIO PF1 coverage should include `amdgpu/nbio_v7_11.c`, where PF1 doorbell self-ring and HDP flush masks are consumed.

Static generated-header validation should confirm that every field in this chunk has a matching `__SHIFT` and `_MASK`, that masks align with shifts and expected widths, and that register names match entries in `nbif_6_3_1_offset.h`. It should also flag duplicate-looking PF/PF1/VF0 names for manual namespace review rather than collapsing them.

Runtime HDP flush tests should exercise CP0-CP9 and SDMA0-SDMA1 flush request/done paths on supported hardware. A useful signal is that common AMDGPU HDP flush waits complete reliably and that CPU-visible memory reflects GPU writes after the flush.

Doorbell tests should enable and disable the self-ring aperture, program a high 64-bit doorbell base, submit work through command processor, SDMA, and interrupt-handler doorbell paths, and verify that incorrect ranges do not receive writes. SR-IOV or GPUIOV configurations should verify PF/VF doorbell isolation.

PCIe/strap validation should compare decoded strap fields against expected device enumeration: link speed capabilities, BAR sizes, MSI/MSI-X, AER/ACS/ATS/PASID/PRI capability exposure, SR-IOV VF count and page sizes, class/vendor/device IDs, FLR/PME support, and reset-time-reporting values.

RAS tests should enable GDC RAS detection/logging paths in a controlled environment, inject or provoke supported parity/poison/error-event cases, and verify central status, leaf status, interrupt/MCA reporting, and clear/recovery behavior. Negative tests should verify that disabled propagation or logging bits remain quiet.

Reset tests should cover PF FLR, link reset, soft reset, hard reset, and SDP port reset paths, checking that completion bits and post-reset register state match expectations and that in-flight DMA/doorbell paths recover.

Traffic and performance tests should stress DMA, host response, SION, A2S, and doorbell-heavy workloads while changing only validated arbitration/credit/clock-gating settings. Regressions may appear as latency spikes, timeouts, lower throughput, or RAS/error response events rather than immediate functional failure.
