# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 1-2525

## Scope

This chunk is the opening segment of a generated AMD NBIO 4.3.0 register shift/mask header. It contains only C preprocessor constants; there are no functions, structs, variables, allocation paths, locks, loops, branches, or direct register reads/writes in this range.

The slice starts with the file license/header guard and covers NBIF/BIF system decode, downstream/root-complex/endpoint PCIe controls, PF system registers, BIF control registers, RCC root-complex controls, graphics MSI-X vector registers, RCC strap registers, PF BIFPFVF registers, GDC miscellaneous controls, and the start of the `DEV0_EPF0_VF0` PF/VF register view. It ends at `RCC_DEV0_EPF0_VF0_RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN__SHIFT`, before that register's mask definition, so the final VF0 RCC block is incomplete in this chunk.

Although this file is under a local `ceph-client` source mirror, it is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bit positions for NBIO 4.3.0 hardware registers. Each generated field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, poll, or update the field.

Runtime AMDGPU code pairs these masks with matching offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` and the register helper layer, including `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

## Important Macro Families

The opening `nbio_nbif0_bif_bx_SYSDEC` block defines indirect PCIe index/data registers, high index bytes, BIOS/SBIOS/driver/firmware scratch registers, graphics MMIO CAM address/remap windows, CAM enable/completion controls, and full-width scratch payload fields. These constants describe low-level firmware/driver communication space and address remap controls, but the header does not assign semantics to scratch contents.

The `rcc_dwn_dev0`, `rcc_dwnp_dev0`, and `rcc_ep_dev0` blocks define downstream-port and endpoint PCIe controls. Covered fields include unsupported-request reporting suppression, LTR-message handling, hidden-register decode enables through Gen5, FLR extension mode, completion-timeout and error-report controls, received error clear/status bits, link speed straps through Gen5, link bandwidth and data-link notification disables, endpoint PCIe interrupt enables/status, DPA substate power allocation registers, endpoint LTR transmit message fields, requester ID selection, TX/RX controls, atomic/malformed TLP behavior, and completion timeout options.

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` block exposes PF MMIO indirection registers: `BIF_BX_PF0_MM_INDEX`, `BIF_BX_PF0_MM_DATA`, and `BIF_BX_PF0_MM_INDEX_HI`. These allow software to select MMIO offsets and access indirect data through PF-visible system/PF/VF decode space.

The `nbio_nbif0_bif_bx_BIFDEC1` block covers central BIF control. It includes bus control bits for master/response behavior, memory lock and BAR-origin options, BIF scratch and reset fields, interrupt handler dummy-read controls, CLKREQ# pad controls, BIF feature disables and outstanding HDP non-posted limits, doorbell control and doorbell/RAS/ATHUB interrupt status/clear/disable fields, framebuffer read/write enable, transaction-pending views, NBIF graphics address LUT control and 16 LUT entries, HDP flush register remap controls, BIF ring-buffer base/read/write pointers and writeback controls, and an MP1 interrupt bit for BACO exit completion.

The `nbio_nbif0_rcc_dev0_BIFDEC1` block defines root-complex controls for device 0. Important fields cover invalid SR-IOV register-access interrupt enable, BACO request gating, doorbell-aperture reset, VDM/MCTP/AMPTP support, PCIe margining capability parameters, GPUIOV and GPU host-VM enablement, console IOV VF offset/stride, peer register ranges and peer framebuffer offsets, bus-number and device/function-number lists, XDMA aperture bounds, VGA/config aperture controls, payload/read-request size overrides, poisoning/completion-abort policy, ATC/PASID/ATS-related unsupported-request behavior, requester-ID restore, LTR low-power switch control, and memory-hub arbitration.

The `nbio_nbif0_rcc_dev0_epf0_BIFDEC2` block defines four graphics MSI-X table vector entries. Each vector has address-low, address-high, message-data, and vector-control fields, followed by a PBA register with pending bits for the same vector set.

The `nbio_nbif0_rcc_strap_BIFDEC1` block is the largest area in this slice. It defines BIF and port straps for feature advertisement and reset/default hardware behavior: device/vendor/subsystem IDs, ARI/ACS/AER/MSI capabilities, link width/speed, Gen2-Gen5 support, equalization presets, LTR/OBFF/power-management support, ASPM and L1/LDN timers, emergency power-reduction fields, completion-timeout logging, DOE/ATS/PRI/PASID/TPH/10-bit tag capabilities, SR-IOV VF device IDs and supported page sizes, class code, total VF count, reset/FLR timing, atomic support, ACS controls, power-budget data, function enables, and EPF1-specific audio/function straps. Some strap comments appear without field definitions in this chunk, indicating generated empty or reserved registers.

The PF `BIFPFVFDEC1` block exposes runtime PF controls and status: BME status, atomic error log bits, self-ring doorbell GPA aperture base/control, HDP register/memory coherency flush controls, flush-only/invalidate-only selectors, per-engine GPU HDP flush request/done bits for CP0-CP9 and SDMA0-SDMA1 plus reserved engines, PF transaction-pending status, LUT bypass, RCC error log, doorbell aperture enable, reported config memory size, a reserved config register, and IOV function identifiers.

The `GDCDEC` block defines GDC/SHUB control surfaces: SHUB register-interface control, graphics doorbell status, ATDMA miscellaneous clock/flush/ordering fields, and S2A miscellaneous timeout/backoff/urgency fields.

The `DEV0_EPF0_VF0` blocks mirror part of the PF-facing register set for VF0. They cover VF0 BME status, atomic error log, self-ring doorbell GPA aperture base/control, HDP coherency flush controls, per-engine HDP flush request/done bits, transaction-pending status, LUT bypass, four transmit and four receive mailbox message-buffer dwords, mailbox valid/ack control, mailbox interrupt enables, compact VMHV mailbox data/valid/ack fields, VF0 MMIO index/data/high-index registers, VF0 RCC error log, and the first shift constant for VF0 doorbell-aperture enable.

## Control Flow

There is no executable control flow in this header. Runtime behavior is provided by code that includes the generated constants:

1. A caller selects a register offset from `nbio_4_3_0_offset.h`.
2. It reads or composes a 32-bit hardware value through the SOC15/NBIO accessors.
3. It applies this header's `__SHIFT` and `_MASK` constants directly or through `REG_SET_FIELD`/`REG_GET_FIELD`.
4. It writes a control bit, decodes a status/capability value, polls a hardware-owned bit, clears sticky interrupt/error state, or exposes the offset/mask to a higher-level AMDGPU subsystem.

Direct examples are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`: HDP remap registers are programmed with `regBIF_BX0_REMAP_HDP_*`; the revision ID is extracted from `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0`; framebuffer access is toggled with `BIF_BX0_BIF_FB_EN`; doorbell aperture and self-ring aperture controls use `RCC_DEV0_EPF0_RCC_DOORBELL_APER_EN` and `BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL`; interrupt handler dummy-read behavior uses `BIF_BX0_INTERRUPT_CNTL`; HDP flush request/done offsets and masks feed `nbio_hdp_flush_reg`; ASPM/LTR programming updates RCC strap and endpoint LTR fields; and RAS ATHUB interrupt handling reads, clears, and disables bits in `BIF_BX0_BIF_DOORBELL_INT_CNTL`.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed state in NBIO, BIF, RCC, GDC, PF, and VF register spaces. The represented state includes firmware/driver scratch dwords, PCIe control/status, link and power-management policy, strap-derived capability advertisement, interrupt enable/status/clear bits, doorbell aperture configuration, HDP flush synchronization, transaction-pending state, MSI-X vector programming, mailbox payload/handshake bits, SR-IOV/IOV identifiers, peer aperture routing, and memory/config aperture sizing.

Some described bits are static strap or capability fields, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The generated masks do not encode access permissions, reset defaults, side effects, polling requirements, ordering requirements, or PF/VF ownership rules.

## Dependencies And Integration Points

This header must stay synchronized with `nbio_4_3_0_offset.h`, which supplies the matching register addresses. It is included by `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and by SMU13 power-management files `smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`; display DC resource files include the offset header for related NBIO addressing.

The most important runtime integration surfaces are AMDGPU NBIO setup, PCIe ASPM/LTR policy, interrupt-handler configuration, RAS ATHUB error-event interrupt handling, HDP coherency flush and remap paths, memory-controller access enable/disable, doorbell aperture programming, self-ring doorbell support, SR-IOV PF/VF register access, VF mailbox handshakes, GPU reset/FLR/BACO behavior, and power-management coordination through SMU13.

These fields also overlap generic PCIe and platform concepts: AER/error reporting, MSI-X vector storage, link speed/width capability, max payload/read-request policy, LTR/OBFF/DPA, ATS/PASID/PRI advertisement, ARI/ACS, SR-IOV VF counts and page sizes, completion timeout behavior, and function/device identity straps. AMDGPU code must combine these masks with the correct address space and the correct ownership model for bare-metal PF, SR-IOV PF, or SR-IOV VF operation.

## Risks And Edge Cases

- The chunk boundary is artificial. The final VF0 RCC doorbell-aperture register has only its shift macro in this slice; its mask and following VF0 fields are outside the work item.
- These are untyped generated constants. A stale shift or mask can compile successfully while silently changing a hardware bit, status interpretation, or aperture address.
- Naming is highly repetitive across PF, VF0, endpoint, downstream, and root-complex views. Applying a PF mask to a VF register, or a BIFDEC mask to a BIFPFVFDEC register, may still produce plausible 32-bit operations while targeting the wrong semantics.
- HDP flush request/done masks are synchronization-critical. Wrong CP or SDMA bits can cause cache/coherency flush waits to complete too early, time out, or miss a producer.
- Doorbell aperture and self-ring GPA fields affect command submission and interrupt paths. Incorrect base, enable, mode, or size fields can cause lost doorbells, misrouted writes, invalid guest access, or security issues under SR-IOV.
- Interrupt and RAS bits include status, clear, disable, and enable fields in the same register family. Generic read/modify/write handling can clear diagnostic state accidentally or leave RAS interrupts masked.
- Strap fields define advertised PCIe/SR-IOV capabilities. Incorrect defaults or masks around ACS, ATS, PASID, PRI, ARI, MSI/MSI-X, link speed, reset timing, and VF counts can break enumeration, isolation, guest passthrough, or link training.
- PCIe power-management fields are platform-sensitive. ASPM/LTR/DPA/OBFF and L1/LDN timer mistakes can cause resume failures, latency regressions, hangs during link state transitions, or excess power draw.
- Scratch registers are shared communication surfaces with firmware/BIOS/driver users. The masks are full-width, so consumers need external ownership conventions before writing them.

## Test Signals

Useful validation is mostly build-time plus hardware integration:

- Build AMDGPU with NBIO 4.3.0 and SMU13 support; renamed or missing masks should surface in `nbio_v4_3.c`, `smu_v13_0_0_ppt.c`, and `smu_v13_0_7_ppt.c`.
- Compare this chunk against `nbio_4_3_0_offset.h` to confirm every register family in lines 1-2525 has a matching address and the same PF/VF/root-complex suffix.
- Boot affected ASICs and confirm revision ID, reported memory size, framebuffer access enablement, and PCIe link state remain sane.
- Exercise HDP flush users from graphics, compute, KFD, SDMA, and reset paths; timeouts or stale memory visibility can indicate bad flush request/done masks or remap fields.
- Exercise doorbell-based GC, IH, SDMA, and VCN submission paths, including self-ring aperture enablement; lost submissions or interrupts point to doorbell aperture, S2A, or interrupt-control drift.
- Run suspend/resume, BACO, runtime power, ASPM/LTR, and link retraining tests while checking for link instability, latency regressions, or power-management hangs.
- In SR-IOV configurations, create VFs, bind guest drivers, test VF0 mailbox exchange, VF MMIO index/data access, VF HDP flush controls, and PF/VF transaction-pending status.
- Inject or provoke RAS/ATHUB and PCIe error events where possible, then confirm `BIF_BX0_BIF_DOORBELL_INT_CNTL` status/clear/disable behavior and global RAS ISR routing.
- Validate MSI-X vector programming for the GFX vector table and PBA fields; misprogramming can show up as masked, pending, or misrouted interrupts.

## Chunk Notes

- Lines 1-302 are the header guard plus `nbio_nbif0_bif_bx_SYSDEC`.
- Lines 303-629 cover downstream-port, downstream-path, endpoint, and PF MMIO-index register blocks.
- Lines 630-941 cover central BIF controls, doorbell/RAS interrupt fields, HDP remap registers, and BIF ring-buffer controls.
- Lines 942-1292 cover root-complex controls and EPF0 GFX MSI-X vector/PBA fields.
- Lines 1293-2017 cover the RCC strap block for BIF, device port, EPF0, and EPF1 feature advertisement/defaults.
- Lines 2018-2227 cover PF BIFPFVF and RCC PF controls; lines 2228-2260 cover GDC controls.
- Lines 2261-2525 begin `DEV0_EPF0_VF0` BIFPFVF, SYSPFVF, and RCC blocks and stop inside `RCC_DEV0_EPF0_VF0_RCC_DOORBELL_APER_EN`.
