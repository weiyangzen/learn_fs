# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002961`: lines 1-2525, `Docs/researches/chunks/subset-b-002961_research.md`
- `subset-b-002962`: lines 2526-5053, `Docs/researches/chunks/subset-b-002962_research.md`
- `subset-b-002963`: lines 5054-7579, `Docs/researches/chunks/subset-b-002963_research.md`
- `subset-b-002964`: lines 7580-10029, `Docs/researches/chunks/subset-b-002964_research.md`
- `subset-b-002965`: lines 10030-12477, `Docs/researches/chunks/subset-b-002965_research.md`
- `subset-b-002966`: lines 12478-14939, `Docs/researches/chunks/subset-b-002966_research.md`
- `subset-b-002967`: lines 14940-17466, `Docs/researches/chunks/subset-b-002967_research.md`
- `subset-b-002968`: lines 17467-19906, `Docs/researches/chunks/subset-b-002968_research.md`
- `subset-b-002969`: lines 19907-22328, `Docs/researches/chunks/subset-b-002969_research.md`
- `subset-b-002970`: lines 22329-24747, `Docs/researches/chunks/subset-b-002970_research.md`
- `subset-b-002971`: lines 24748-27173, `Docs/researches/chunks/subset-b-002971_research.md`
- `subset-b-002972`: lines 27174-29592, `Docs/researches/chunks/subset-b-002972_research.md`
- `subset-b-002973`: lines 29593-31977, `Docs/researches/chunks/subset-b-002973_research.md`
- `subset-b-002974`: lines 31978-34356, `Docs/researches/chunks/subset-b-002974_research.md`
- `subset-b-002975`: lines 34357-36823, `Docs/researches/chunks/subset-b-002975_research.md`
- `subset-b-002976`: lines 36824-39244, `Docs/researches/chunks/subset-b-002976_research.md`
- `subset-b-002977`: lines 39245-41680, `Docs/researches/chunks/subset-b-002977_research.md`
- `subset-b-002978`: lines 41681-44102, `Docs/researches/chunks/subset-b-002978_research.md`
- `subset-b-002979`: lines 44103-46534, `Docs/researches/chunks/subset-b-002979_research.md`
- `subset-b-002980`: lines 46535-48958, `Docs/researches/chunks/subset-b-002980_research.md`
- `subset-b-002981`: lines 48959-51417, `Docs/researches/chunks/subset-b-002981_research.md`
- `subset-b-002982`: lines 51418-54381, `Docs/researches/chunks/subset-b-002982_research.md`
- `subset-b-002983`: lines 54382-56932, `Docs/researches/chunks/subset-b-002983_research.md`
- `subset-b-002984`: lines 56933-59410, `Docs/researches/chunks/subset-b-002984_research.md`
- `subset-b-002985`: lines 59411-61872, `Docs/researches/chunks/subset-b-002985_research.md`
- `subset-b-002986`: lines 61873-64306, `Docs/researches/chunks/subset-b-002986_research.md`
- `subset-b-002987`: lines 64307-66765, `Docs/researches/chunks/subset-b-002987_research.md`
- `subset-b-002988`: lines 66766-69194, `Docs/researches/chunks/subset-b-002988_research.md`
- `subset-b-002989`: lines 69195-71626, `Docs/researches/chunks/subset-b-002989_research.md`
- `subset-b-002990`: lines 71627-74047, `Docs/researches/chunks/subset-b-002990_research.md`
- `subset-b-002991`: lines 74048-76466, `Docs/researches/chunks/subset-b-002991_research.md`
- `subset-b-002992`: lines 76467-78893, `Docs/researches/chunks/subset-b-002992_research.md`
- `subset-b-002993`: lines 78894-81346, `Docs/researches/chunks/subset-b-002993_research.md`
- `subset-b-002994`: lines 81347-82050, `Docs/researches/chunks/subset-b-002994_research.md`

## Chunk Research

### subset-b-002961: lines 1-2525

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

### subset-b-002962: lines 2526-5053

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 2526-5053

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, enums, variables, loops, branches, allocations, locking paths, or direct MMIO accesses in the assigned range.

The slice starts inside the `RCC_DEV0_EPF0_VF0` register-control/configuration block, covers the VF0 graphics MSI-X table and pending-bit-array masks, then fully repeats the same per-virtual-function NBIF/RCC register families for VF1 through VF7. It begins VF8 at `BIF_BX_DEV0_EPF0_VF8_BIF_BME_STATUS` and stops at the end of the `BIF_BX_DEV0_EPF0_VF8_GPU_HDP_FLUSH_REQ` masks; the VF8 flush-done, transaction-pending, mailbox, MMIO index/data, RCC, and MSI-X masks continue after this chunk.

Although the file is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions for NBIO 4.3.0 SR-IOV virtual-function register windows. Each generated field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update a field.

Runtime AMDGPU code combines these constants with matching generated register offsets, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` and related NBIF offset headers, through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The VF0 portion is a boundary fragment. It includes the tail of `RCC_DEV0_EPF0_VF0_RCC_DOORBELL_APER_EN`, complete masks for VF0 `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`, then the VF0 `GFXMSIX` table under the `nbio_nbif0_rcc_dev0_epf0_vf0_BIFDEC2` address block. The MSI-X vector fields define low/high message address dwords, message data dwords, per-vector mask bits for vectors 0 through 3, and a two-bit pending-bit array.

VF1 through VF7 each have a complete `BIFPFVFDEC1` NBIF register group. The group starts with `BIF_BME_STATUS`, which records DMA activity while bus-master enable is low and supplies a clear bit, and `BIF_ATOMIC_ERR_LOG`, which records unsupported PCIe atomic cases such as opcode, request-enable-low, length, and non-relaxed ordering cases with paired clear bits.

Each full VF block defines a self-ring doorbell aperture: high and low GPA aperture base dwords plus `DOORBELL_SELFRING_GPA_APER_CNTL` enable, mode, and size fields. These fields describe the guest-visible or VF-visible doorbell mapping used by engines to submit work through MMIO doorbells.

Each full VF block defines HDP coherency controls. `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL` expose one-bit flush or invalidate addresses. `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` each allocate all 32 bits to engine request/done flags: CP0 through CP9, SDMA0 and SDMA1, followed by reserved engine bits 0 through 19. These are used to coordinate GPU-side register and memory visibility.

Each full VF block defines `BIF_TRANS_PENDING` master/slave transaction-pending bits and `NBIF_GFX_ADDR_LUT_BYPASS`. The transaction flags are important reset and quiesce signals because they indicate whether NBIF traffic is still outstanding.

Each full VF block defines mailbox data and handshake registers. `MAILBOX_MSGBUF_TRN_DW0` through `DW3` and `MAILBOX_MSGBUF_RCV_DW0` through `DW3` are full-width message-buffer dwords. `MAILBOX_CONTROL` contains transmit valid/ack and receive valid/ack bits. `MAILBOX_INT_CNTL` enables valid and ack interrupts. `BIF_VMHV_MAILBOX` packs VM/HV mailbox interrupt enables, four-bit transmit and receive message payloads, valid bits, and ack bits into one register.

Each full VF block defines a `SYSPFVFDEC` indirect MMIO aperture with `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`. `MM_INDEX` carries a 31-bit offset plus an aperture selector bit, `MM_DATA` is a full-width data dword, and `MM_INDEX_HI` carries the high offset dword.

Each full VF block defines RCC error/configuration fields. `RCC_ERR_LOG` records invalid SR-IOV register accesses and doorbell read access status. `RCC_DOORBELL_APER_EN` exposes the BIF doorbell aperture enable bit. `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration dwords. `RCC_IOV_FUNC_IDENTIFIER` carries a one-bit function identifier and an `IOV_ENABLE` bit at bit 31.

Each full VF block ends with an RCC `BIFDEC2` graphics MSI-X table. For each of vectors 0 through 3, the table exposes message address low bits 31:2, message address high bits 31:0, message data bits 31:0, and one mask bit. The per-VF `GFXMSIX_PBA` pending-bit-array field covers pending bits 0 and 1 in this NBIO 4.3.0 slice.

The VF8 portion is another boundary fragment. It covers `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, self-ring doorbell aperture base/control, HDP register/memory flush/invalidate control dwords, and all `GPU_HDP_FLUSH_REQ` shift/mask bits. The matching VF8 `GPU_HDP_FLUSH_DONE` and later state are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU selects a generated register offset such as a `regBIF_*`, `regRCC_*`, or matching SOC15 register identifier.
2. It reads, composes, or updates a 32-bit register value through the NBIO/NBIF access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or through `REG_SET_FIELD`/`REG_GET_FIELD`.
4. It writes a doorbell, mailbox, MSI-X, coherency, transaction, error-clear, or configuration value, or polls a hardware-owned status bit.

Typical consumers are NBIO setup, SR-IOV virtual-function management, doorbell aperture programming, HDP flush/remap setup, VM/HV mailbox messaging, MSI-X interrupt delivery, and reset/quiesce paths that need to know whether VF traffic is pending.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register state owned by the GPU, firmware, platform PCIe/SR-IOV configuration, host kernel policy, and AMDGPU's NBIO/NBIF management code.

The represented state includes VF doorbell aperture base/enable/size/mode, memory-size and reserved configuration values, IOV function enable/identity, atomic-error and invalid-access logs, BME-low DMA diagnostics, HDP flush and invalidate request/done state, transaction-pending status, indirect MMIO index/data state, mailbox payload and handshake bits, mailbox interrupt enables, MSI-X vector address/data/mask fields, and MSI-X pending bits.

Some fields are static configuration or capability-like values, some are software-programmed controls, some are hardware-updated status, and some are sticky diagnostics with explicit clear bits. The generated masks do not encode reset defaults, access permissions, write-one-to-clear semantics, polling timeouts, ownership boundaries, or ordering requirements; those rules must come from the NBIO/NBIF programming sequence and hardware documentation.

## Dependencies And Integration Points

The primary dependency is the generated NBIO/NBIF register database. This chunk must remain synchronized with the matching offset headers, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` and the NBIF 6.3.1 offset/mask headers that expose the same VF-oriented register naming in neighboring generated files.

Direct in-tree NBIO 4.3 users include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. The local `nbio_v4_3.c` code includes this header and uses adjacent NBIO masks for revision ID decoding, memory-size reads, doorbell aperture control, HDP flush remapping, interrupt setup, and clock/power controls.

The most relevant integration surfaces for this chunk are:

- SR-IOV VF register windows for VF0 through VF8.
- Doorbell and self-ring doorbell aperture setup.
- HDP memory/register coherency flush and invalidate operations.
- GPU engine flush request/done handshakes for CP and SDMA engines.
- Transaction-pending checks during reset, quiesce, or function teardown.
- VM/HV mailbox message transport and mailbox interrupt signaling.
- VF graphics MSI-X vector programming and pending-bit handling.
- RCC error logging for invalid SR-IOV accesses and doorbell read attempts.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the VF0 `RCC_DOORBELL_APER_EN` shift definition and stops after VF8 `GPU_HDP_FLUSH_REQ`; adjacent chunks are required for complete VF0 and VF8 analysis.
- These are untyped preprocessor constants. A stale mask or shift can compile cleanly while extracting or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around VF1 through VF8 can silently target the wrong virtual function and affect SR-IOV isolation, guest interrupt delivery, or diagnostics.
- Register-offset and field-mask mismatches are easy in generated headers. A valid VF4 mask applied to a VF5 offset, or an NBIO mask applied to an NBIF offset with a different generation, may still produce plausible-looking register operations.
- Doorbell aperture fields affect GPU command submission. Incorrect base, size, mode, or enable values can cause missed submissions, writes to the wrong aperture, or guest/host isolation problems.
- HDP coherency fields are ordering-sensitive. Missing or incorrect flush/invalidate request and done handling can leave stale CPU-visible or GPU-visible data, especially across queue submission, VM updates, reset, or power transitions.
- Flush request/done fields are dense 32-bit bitmaps. Engine-bit mislabeling can cause software to wait on the wrong engine, skip a required flush, or time out during reset.
- Mailbox valid/ack fields are handshake state. Incorrect clear/set ordering or interrupt-enable handling can lose PF/VF messages, wedge VM/HV communication, or produce interrupt storms.
- MSI-X address/data/mask/PBA fields directly affect interrupt delivery. Width mistakes, address-low alignment mistakes, stale mask bits, or pending-bit confusion can cause lost, misrouted, or unexpectedly masked interrupts.
- Error-log and clear bits may be sticky or write-one-to-clear. Generic read/modify/write treatment can erase diagnostic evidence or fail to clear latched error state.
- `MM_INDEX`/`MM_DATA` indirect access fields can reach broad register space. Incorrect aperture or high-offset handling can redirect indirect accesses to unrelated registers.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c`, SMU13 files, or generated-header include paths.
- Compare this chunk against `nbio_4_3_0_offset.h` and neighboring NBIF generated headers to confirm VF suffixes, register names, base indices, and repeated VF strides stay synchronized.
- Boot affected NBIO 4.3 hardware and confirm memory-size, doorbell aperture, interrupt, HDP remap, and clock/power paths still initialize without register-access faults.
- In SR-IOV configurations, create and remove VFs spanning VF0 through VF8, bind guest drivers, and verify VF isolation, doorbell writes, mailbox messaging, MSI-X delivery, and reset behavior.
- Exercise graphics, compute, and SDMA workloads while monitoring HDP flush request/done progress; stale data, timeout logs, or hung queues can indicate flush bit or offset drift.
- Exercise VF reset, suspend/resume, runtime power transitions, and quiesce flows while checking `BIF_TRANS_PENDING` and engine flush done state.
- Trigger or observe mailbox traffic between PF/hypervisor and VFs; lost valid/ack transitions or unexpected mailbox interrupts point to mailbox field layout problems.
- Exercise MSI-X masking/unmasking and interrupt-heavy workloads; lost interrupts or stuck pending bits can indicate vector table or PBA field mismatches.
- Use SR-IOV error and diagnostics paths, where available, to verify BME-low DMA status, atomic error logging, invalid register access logging, and doorbell read status map to expected bits.

## Chunk Notes

- Lines 2526-2538 are the tail of VF0 RCC configuration and IOV identifier masks.
- Lines 2540-2592 cover VF0 graphics MSI-X vector and PBA masks.
- Lines 2596-4937 cover complete VF1 through VF7 NBIF/RCC/SYSPFVFDEC/MSI-X mask groups.
- Lines 4941-5053 begin VF8 and stop after `BIF_BX_DEV0_EPF0_VF8_GPU_HDP_FLUSH_REQ__RSVD_ENG19_MASK`.
- The assigned range contains 2,065 `#define` entries for 374 register-name prefixes, with 1,032 shift definitions and 1,033 mask definitions.

### subset-b-002963: lines 5054-7579

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 5054-7579

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,063 preprocessor `#define` entries across 2,526 source lines. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `VF8` virtual-function register template at `BIF_BX_DEV0_EPF0_VF8_GPU_HDP_FLUSH_DONE`, covers all corresponding BIF/RCC system PF/VF decode and MSI-X register field maps for `VF9` through `VF14`, and then enters `VF15` through `RCC_DEV0_EPF0_VF15_GFXMSIX_VECT1_ADDR_LO__MSG_ADDR_LO__SHIFT`. The boundaries are artificial: the `VF8` flush-request fields are before this chunk, and the rest of `VF15` MSI-X vector definitions continue after it.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 hardware interface. For each named NBIO register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for extracting or packing a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, preserve, or compose that field.

The matching register offsets live in `nbio_4_3_0_offset.h`; consumers include the generated offset and mask headers together. This chunk specifically maps SR-IOV virtual-function NBIO/BIF/RCC registers for endpoint function 0. The repeated `BIF_BX_DEV0_EPF0_VF<n>_*` and `RCC_DEV0_EPF0_VF<n>_*` namespaces describe per-VF state for DMA enable reporting, atomic-operation error logging, doorbell aperture selection, HDP coherency flush/invalidate control, PF/VF mailbox messaging, indirect MMIO access, SR-IOV decode errors, and MSI-X message routing.

## Important Macro Families

The `BIF_BX_DEV0_EPF0_VF*_BIFPFVFDEC1` families define per-VF BIF-facing state:

- `BIF_BME_STATUS` exposes whether bus-master enable is set for the VF.
- `BIF_ATOMIC_ERR_LOG` reports atomic-operation error status, including `ERR_VALID`, `ERR_UPID`, `ERR_ADDR`, `ERR_OPCODE`, `ERR_FUNC_NUM`, and `ERR_VF`.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `DOORBELL_SELFRING_GPA_APER_BASE_LOW`, and `DOORBELL_SELFRING_GPA_APER_CNTL` define the guest physical doorbell aperture base, size, select-ring enable, and process-isolation logic.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL` provide coherency flush and invalidate controls.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` expose 32 engine bits for command processors `CP0` through `CP9`, `SDMA0`, `SDMA1`, and reserved engines `RSVD_ENG0` through `RSVD_ENG19`.
- `BIF_TRANS_PENDING` exposes master and slave transaction-pending bits used for quiesce/reset sequencing.
- `NBIF_GFX_ADDR_LUT_BYPASS` controls address LUT bypass behavior.
- `MAILBOX_MSGBUF_TRN_DW[0-3]` and `MAILBOX_MSGBUF_RCV_DW[0-3]` define four-word transmit and receive buffers.
- `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX` define valid/ack handshakes, interrupt enables, compact message data fields, and VM/hypervisor mailbox status.

The `BIF_BX_DEV0_EPF0_VF*_SYSPFVFDEC` families define an indirect MMIO access path:

- `MM_INDEX` contains a 31-bit `MM_OFFSET` and the `MM_APER` selector bit.
- `MM_DATA` carries the 32-bit data payload.
- `MM_INDEX_HI` extends the offset through `MM_OFFSET_HI`.

The `RCC_DEV0_EPF0_VF*_BIFPFVFDEC1` families define RCC-side virtualization and configuration state:

- `RCC_ERR_LOG` has status bits for invalid SR-IOV register access and doorbell-read access.
- `RCC_DOORBELL_APER_EN` exposes the BIF doorbell aperture enable bit.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` carry full-width configuration values.
- `RCC_IOV_FUNC_IDENTIFIER` contains a function identifier bit and high `IOV_ENABLE` bit.

The `RCC_DEV0_EPF0_VF*_BIFDEC2` families define graphics MSI-X state:

- `GFXMSIX_VECT[0-3]_ADDR_LO` and `_ADDR_HI` carry the MSI-X message address. The low address field starts at bit 2 and masks the lower alignment bits.
- `GFXMSIX_VECT[0-3]_MSG_DATA` carries the 32-bit MSI-X message data.
- `GFXMSIX_VECT[0-3]_CONTROL` exposes the vector mask bit.
- `GFXMSIX_PBA` exposes pending bits for the four MSI-X vectors.

## APIs, Types, And Functions

There are no runtime APIs or C types in this chunk. The public interface is the generated macro namespace. Runtime code normally combines these masks with register offsets and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.

The macros are untyped integer constants with an `L` suffix. They encode bit layout only; they do not encode register access method, privilege, reset behavior, write-one-to-clear semantics, polling requirements, or whether a field is read-only, write-only, sticky, or side-effecting.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU or firmware-facing code selects a register offset from `nbio_4_3_0_offset.h`.
2. The caller reads, modifies, writes, polls, or decodes the register using the `__SHIFT` and `_MASK` constants from this header.
3. Hardware implements the state transition, such as mailbox valid/ack exchange, HDP flush completion, transaction quiesce, doorbell aperture programming, MSI-X vector delivery, or error-log update.

Important external flows represented by this chunk include VF bring-up, SR-IOV PF/VF isolation, virtual doorbell mapping, PF/VF or hypervisor mailbox communication, HDP cache coherency maintenance before command submission or reset, transaction-drain checks before reset or teardown, indirect MMIO access through `MM_INDEX/MM_DATA`, and MSI-X interrupt setup and masking.

## State And Persistence Behavior

The header stores no state. It names hardware-visible state in NBIO/BIF/RCC registers for SR-IOV virtual functions. Persistence is controlled by GPU reset domains, PF-managed SR-IOV lifecycle, VF function-level reset, suspend/resume save/restore, firmware initialization, and explicit driver writes.

Represented state includes:

- VF bus-master status and transaction-pending state.
- Atomic-operation error logs and invalid-access logs.
- Doorbell aperture base, size, enable, and process-isolation controls.
- HDP register and memory coherency flush/invalidate request and completion bits.
- PF/VF mailbox buffers, valid/ack flags, and interrupt enables.
- Indirect MMIO index/data registers.
- RCC configuration memory size, reserved configuration storage, IOV enablement, and function identifier state.
- MSI-X message address, message data, per-vector mask bits, and pending-bit-array state.

Several fields are not ordinary storage bits. HDP flush request bits are paired with done bits and generally require polling/order guarantees. Error-log status bits can be sticky or clear-on-write depending on the hardware register contract. Mailbox valid/ack bits are protocol state and can deadlock if producer and consumer order is wrong. MSI-X address/data/control fields directly affect interrupt routing. Doorbell and IOV fields affect virtualization isolation and DMA-facing access.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register set:

- `nbio_4_3_0_offset.h` supplies matching register addresses and base indices.
- `nbio_4_3_0_sh_mask.h` supplies the field layout documented here.
- Other generated NBIO headers may provide defaults or companion register metadata for the same IP block.

Observed include-level integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, SMU 13 power-management files such as `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`, and DCN 3.2 display resource files that include the NBIO 4.3.0 offset header. The macros integrate with AMDGPU NBIO initialization, power management, SR-IOV virtualization paths, interrupt delivery, register debugging, reset/quiesce sequencing, and firmware or hypervisor mailbox protocols.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile successfully while making runtime code touch the wrong hardware bit. The highest-risk fields here are doorbell aperture controls, IOV enablement, MSI-X routing, HDP flush request/done bits, and mailbox valid/ack bits.
- The chunk starts and ends inside repeated VF templates. Merge/reconciliation must not treat the missing `VF8` flush-request prefix or incomplete `VF15` MSI-X suffix as source omissions.
- Per-VF repetition is intentional. A mismatch among `VF9` through `VF14` may be meaningful generator/register-database drift, but boundary truncation for `VF8` and `VF15` must be accounted for first.
- Mailbox fields combine payload, valid, ack, and interrupt-enable bits. Incorrect masking or write ordering can lose messages, duplicate notifications, or wedge PF/VF synchronization.
- HDP coherency bits gate correctness between CPU-visible memory, GPU engines, and DMA. Wrong engine masks or polling logic can leave stale data visible to command processors or SDMA engines.
- Doorbell aperture and process-isolation fields affect guest access to doorbells. Wrong base, size, enable, or process-isolation logic can cause missed submissions or cross-tenant isolation failures.
- MSI-X vector address/data/control/PBA fields affect interrupt routing. Bad masks can cause lost, spurious, or misdirected interrupts.
- Atomic and RCC error logs are diagnostic and possibly sticky; treating them as ordinary writable state can clear evidence or fail to clear real fault conditions.

## Test Signals

- Build AMDGPU with NBIO 4.3 support enabled. Missing or misspelled generated macros should be caught by consumers of the header set.
- Runtime probe on affected AMD GPUs should show stable NBIO initialization and no register-access faults for NBIO 4.3.0 paths.
- SR-IOV tests should enumerate multiple VFs and verify that VF-specific doorbell, mailbox, MM index/data, and interrupt state does not alias across VFs.
- Doorbell tests should validate programmed guest physical aperture base/size, enable state, and process-isolation behavior under VF command submission.
- Coherency tests should exercise HDP flush request/done paths for CP and SDMA engines and verify data visibility after command submission, reset, and queue teardown.
- Mailbox tests should verify four-DW transmit/receive payload transfer, valid/ack handshakes, and interrupt-enable behavior in both PF-to-VF and VF-to-PF directions.
- MSI-X tests should verify vector address/data programming, per-vector masking, PBA pending bits, and interrupt delivery for vectors 0 through 3.
- Error-injection or fault-path tests should verify atomic error logging, invalid SR-IOV register access reporting, doorbell-read access reporting, and preservation/clear behavior for diagnostic status fields.

### subset-b-002964: lines 7580-10029

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 7580-10029

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: no C functions, structs, enums, storage, locking, allocation, or executable statements are defined in this line range.

The range starts in the tail of the `RCC_DEV0_EPF0_VF15_GFXMSIX_*` MSI-X table definitions, then covers a large `PSWUSCFG0_0_*` PCIe switch/upstream configuration block, and finally begins the `BIF_CFG_DEV0_RC0_*` root-complex configuration block through `PCIE_VC1_RESOURCE_STATUS`. Adjacent chunks are needed for the complete file-wide picture because the first register family starts before line 7580 and the final root-complex VC1 status masks continue after line 10029.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of the generated NBIO 4.3.0 hardware interface. Each register field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, or preserve the field.

The companion `nbio_4_3_0_offset.h` supplies the register/config-space offsets, while runtime AMDGPU code consumes this file through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and SOC15 address calculation. These macros are generated hardware metadata; correctness depends on the masks matching the ASIC register database and matching offset/default headers.

This specific chunk documents three related hardware surfaces:

- VF15 graphics MSI-X vector table fields for SR-IOV/virtualized interrupt delivery.
- `PSWUSCFG0_0`, a PCIe upstream/switch configuration image with conventional PCI bridge fields, PCIe capability fields, AER, ACS, multicast, LTR, ARI, data-link feature, 16 GT/s, margining, and 32 GT/s capability fields.
- `BIF_CFG_DEV0_RC0`, the beginning of a root-complex PCI configuration image, including bridge/resource windows, power-management, PCIe link/device/slot controls, MSI, subsystem ID, vendor-specific capability, and virtual-channel fields.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The `RCC_DEV0_EPF0_VF15_GFXMSIX_*` tail defines the remaining VF15 graphics MSI-X table entries:

- `VECT1`, `VECT2`, and `VECT3` message address low/high fields, message data fields, and per-vector `MASK_BIT`.
- `RCC_DEV0_EPF0_VF15_GFXMSIX_PBA` pending-bit fields for the first two pending bits.
- These fields pair with offset definitions such as `regRCC_DEV0_EPF0_VF15_GFXMSIX_VECT*_...` in generated offset headers and describe the hardware layout that a hypervisor, PF path, or resume path may need to preserve or reprogram.

The `PSWUSCFG0_0_*` block is a complete PCI/PCIe configuration-space bit map for the `nbio_pcie0_pswuscfg0_cfgdecp` address block:

- Conventional PCI bridge header fields: vendor/device ID, command/status, revision/class bytes, cache-line/latency/header/BIST, BAR-like base addresses, primary/secondary/subordinate bus numbers, I/O and memory windows, prefetchable memory windows, ROM BAR, capability pointer, interrupt line/pin, adapter/subsystem IDs, and vendor capability metadata.
- Command/status and bridge-status fields: I/O/memory access, bus mastering, parity response, SERR, interrupt disable, immediate readiness, capability-list presence, DEVSEL timing, target/master abort, system error, and parity error reporting.
- Power-management capability fields: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` expose PM version, PME support, D-state control, PME enable/status, data scale/select, B2/B3 support, and related bridge power-management controls.
- PCIe base capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover PCIe version/device type, error-reporting enables, relaxed ordering, max payload/read request size, extended tag, no-snoop, FLR initiation, link speed/width, ASPM/PM control, retraining, common clock, bandwidth interrupts, and data-link active/training status.
- PCIe capability 2 fields: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion-timeout controls, ARI forwarding, atomic-op routing/completion, ID-based ordering, LTR enable, emergency power reduction, ten-bit tags, OBFF, end-to-end TLP prefix support, target link speed, compliance mode, de-emphasis, crosslink, DRS, and 8 GT/s equalization status.
- MSI fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address high/low, and 32-bit/64-bit message-data fields define MSI enablement, vector count, 64-bit capability, extended message data capability, and message payload layout.
- Subsystem and VSEC fields: `SSID_CAP_LIST`, `SSID_CAP`, `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and two scratch payload registers define subsystem identity and vendor-specific extended-capability metadata.
- Virtual-channel fields: `PCIE_VC_ENH_CAP_LIST`, port VC capabilities/control/status, and VC0/VC1 resource capabilities/control/status define VC counts, arbitration table controls, traffic-class mappings, VC IDs, enable bits, and negotiation status.
- AER fields: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four header-log registers, and four TLP-prefix-log registers cover PCIe error classes and diagnostics.
- Secondary PCIe enhanced capability fields: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS` plus lane 0-15 equalization controls expose link-equalization policy and lane error reporting.
- ACS fields: `PCIE_ACS_CAP` and `PCIE_ACS_CNTL` cover source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, direct-translated peer-to-peer, I/O request blocking, memory target access controls, and unclaimed-request redirect behavior.
- Multicast, LTR, ARI, and data-link feature fields: the `PCIE_MC_*`, `PCIE_LTR_*`, `PCIE_ARI_*`, and `DATA_LINK_FEATURE_*` groups describe multicast groups/windows, latency tolerance reporting limits, ARI capability/control, and data-link feature exchange.
- 16 GT/s, margining, and 32 GT/s fields: `PCIE_PHY_16GT_*`, per-lane 16 GT/s equalization presets, per-lane margining control/status pairs, `PCIE_PHY_32GT_*`, 32 GT/s link capability/control/status, and per-lane 32 GT/s equalization presets represent high-speed PCIe link training, diagnostics, and margining surfaces.

The `BIF_CFG_DEV0_RC0_*` block begins the `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` address block:

- The initial fields mirror a PCI-to-PCI bridge/root-port configuration image: vendor/device ID, command/status, revision/class/header/BIST, BAR-like base addresses, bus-number/latency register, I/O/memory/prefetchable windows, ROM BAR, capability pointer, interrupt line/pin, and PM capability registers.
- PCIe capability fields in this block include device/link capability, control, and status, plus root-port slot capability/control/status. Slot fields cover attention button/indicator, power controller/indicator, MRL sensor, electromechanical interlock, hot-plug, physical slot number, software-controlled attention/power controls, interrupt enables, and hot-plug status bits.
- The block continues into device/link capability 2, slot capability/control/status 2, MSI configuration including extended message-data variants, subsystem ID, vendor-specific capability, and VC capability/control/resource fields.
- The final line in this chunk is inside `BIF_CFG_DEV0_RC0_PCIE_VC1_RESOURCE_STATUS`, so the merge lane should treat the VC1 status register as chunk-split.

## APIs, Types, And Functions

There are no callable APIs, C types, or local functions in this chunk. The macro namespace is the public interface. Consumers combine these constants with the companion offset macros and generic AMDGPU register helpers.

Important caller-side APIs and integration types observed in the tree include:

- `nbio_v4_3.c`, which includes `nbio/nbio_4_3_0_offset.h` and `nbio/nbio_4_3_0_sh_mask.h` and registers `nbio_v4_3_funcs` / `nbio_v4_3_sriov_funcs` as `struct amdgpu_nbio_funcs` implementations.
- `struct amdgpu_nbio_funcs` in `amdgpu_nbio.h`, which gives higher-level AMDGPU code function pointers for NBIO operations such as PCIe index/data offsets, revision ID, memory controller access, doorbell ranges, interrupt handling, clock gating, register remap, ROM offset, and ASPM programming.
- SMU13 power-management files `smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the same generated NBIO 4.3.0 headers for power and link-management register definitions.

The macros are untyped integer constants and do not encode read-only, write-one-to-clear, side-effect, reset-domain, or privilege information. Callers must know the register semantics from the hardware block and PCIe specification context.

## Control Flow

This header has no local control flow. Runtime control flow is external:

1. AMDGPU or firmware-facing code selects a register/config-space offset from `nbio_4_3_0_offset.h`.
2. The code reads, composes, masks, extracts, or writes a value using these `__SHIFT` and `_MASK` constants.
3. Hardware interprets the resulting register accesses as PCIe configuration, interrupt-routing, error-reporting, link-management, virtualization, or power-management operations.

Representative flows tied to this chunk include:

- MSI-X programming or restoration for SR-IOV virtual functions. `amdgpu_device.c` notes that QEMU programming of a VF `GFXMSIX_VECT0_ADDR_LO` register can be blocked by nBIF protection during VM resume until exclusive access is restored; the driver calls `amdgpu_restore_msix()` to force reprogramming. The VF15 MSI-X masks in this chunk belong to the same generated MSI-X table surface.
- PCIe ASPM/LTR setup in `nbio_v4_3_program_aspm()` and `nbio_v4_3_program_ltr()`. Those routines read/modify/write NBIO and PCIe config fields, including `DEVICE_CNTL2` LTR enable in the endpoint function block. The `PSWUSCFG0_0_*` and `BIF_CFG_DEV0_RC0_*` link/LTR fields in this chunk represent adjacent switch/root-complex control and status surfaces that must stay synchronized with platform PCIe policy.
- PCIe link diagnostics and training. Link status, 8 GT/s equalization, 16 GT/s equalization, margining, and 32 GT/s status fields are hardware-updated and can be used by debug, firmware, or platform validation paths to determine whether the negotiated width/speed and equalization state are healthy.
- PCIe error handling. AER status/mask/severity/header-log/prefix-log fields expose sticky diagnostic state that software may read, mask, or clear according to PCIe AER rules.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration registers, MSI-X tables, PCIe link controls/status registers, capability registers, and diagnostic registers.

State represented in this chunk includes:

- Static or strap-derived identity/capability state: vendor/device ID, revision/class codes, capability-chain IDs/versions/next pointers, supported link speeds, supported error/ACS/ARI/LTR/VC features, slot capabilities, and subsystem IDs.
- Host/programmed state: PCI command bits, bridge bus/resource windows, ROM enable/base, MSI enable/address/data, MSI-X per-vector mask bits, device/link controls, completion-timeout policy, LTR enable, ARI/ACS controls, multicast controls, VC arbitration/resource enables, and slot controls.
- Hardware-updated state: link training/current speed/current width, data-link active, equalization completion/phase status, DRS/crosslink/downstream component presence, slot status, AER status/logs, MSI-X pending bits, VC negotiation pending, margining status, and parity mismatch status.

Persistence is governed by GPU/NBIO reset domains, PCI configuration save/restore, firmware initialization, platform ASPM policy, SR-IOV PF/VF management, hypervisor accesses, FLR, suspend/resume, and explicit AMDGPU register writes. Some fields are sticky diagnostics or action bits, not ordinary storage. Examples include AER status bits and logs, MSI-X pending bits, `INITIATE_FLR`, link retrain/disable controls, slot power/attention controls, VC load-arbitration bits, and margining command/status fields.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register header set:

- `nbio_4_3_0_offset.h` provides the matching `reg...` offsets for the same register names.
- Other generated NBIO headers provide defaults and adjacent masks outside this chunk.
- SOC15/NBIO register helpers in AMDGPU provide access paths and field helpers that consume the generated masks.

Integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, the main NBIO 4.3 implementation that includes this header and programs related NBIO registers for doorbells, interrupt handling, HDP remap, clock gating, ROM offset, ASPM, and LTR.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_device.c`, where virtualization resume explicitly restores MSI-X after exclusive access is regained, because VF MSI-X table programming can be blocked by NBIF protection.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the NBIO 4.3.0 generated headers alongside SMU and MP register headers for SMU13 power/link-management code.
- Linux PCIe infrastructure and platform firmware indirectly integrate with these fields through enumeration, bridge window assignment, ASPM/LTR policy, AER handling, MSI/MSI-X setup, hot-plug/slot state, and SR-IOV virtualization.

## Risks And Edge Cases

- Generated bitfield drift is high impact. A wrong shift or mask can compile cleanly while causing software to touch the wrong PCIe control bit.
- Chunk boundaries are artificial. The VF15 MSI-X vector set starts before this range, and the root-complex VC1 status register continues after it.
- Many fields are side-effectful or sticky. Treating AER status/log, FLR, link retrain, slot control, MSI-X mask/pending, VC table load, or margining fields as normal read/write storage can lose diagnostics, interrupt delivery, or link stability.
- MSI-X VF registers are virtualization-sensitive. The resume comment in `amdgpu_device.c` shows that VF MSI-X programming can fail while NBIF protection blocks access; restore sequencing and PF/VF access mode matter.
- PCI command and bridge-window masks control memory access, bus mastering, resource windows, and interrupt-disable behavior. Incorrect masks can break enumeration or create DMA/resource exposure.
- ASPM/LTR/link-control fields interact with platform policy and device power states. Incorrect programming can produce link retraining failures, latency issues, power-management hangs, or performance regressions.
- AER, ACS, ARI, multicast, VC, and ATS-adjacent controls affect isolation, error routing, and traffic ordering. Misprogramming can weaken PCIe isolation or make error handling misleading.
- High-speed link fields are lane-repeated and mechanically similar. A generator mismatch for one lane can be hard to spot by code review but visible in link-training or margining failures.

## Test Signals

- Build coverage: compile AMDGPU with NBIO 4.3.0 and SMU13 support enabled. Missing or renamed generated macros should fail at compile time in `nbio_v4_3.c` or SMU13 files.
- Boot/probe coverage: affected AMD GPUs should enumerate normally, report expected PCI class/capability chains, and expose valid bridge/root-port resource windows.
- SR-IOV coverage: create/resume VFs under a hypervisor and verify MSI-X delivery after suspend/resume or VM resume, including no lost interrupts after `amdgpu_restore_msix()`.
- PCIe link coverage: verify negotiated link width/speed, data-link active state, no unexpected retraining loops, and expected 8 GT/s/16 GT/s/32 GT/s equalization status on supported hardware.
- Power-management coverage: exercise ASPM and LTR policy paths with `CONFIG_PCIEASPM`, checking that suspend/resume, runtime PM, and performance states do not regress.
- AER coverage: monitor kernel logs and PCIe AER counters for correctable/uncorrectable error storms; injected errors should populate status/header-log fields and clear according to PCIe rules.
- Slot/root-port coverage: hot-plug or slot-status tests, where applicable, should validate attention/power/MRL/interlock bits and interrupts.
- VC/ACS/ARI coverage: virtualization and IOMMU tests should verify enumeration, isolation, peer-to-peer routing policy, and traffic-class/virtual-channel negotiation on platforms that expose those features.

### subset-b-002965: lines 10030-12477

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 10030-12477

## Scope

This chunk covers generated AMD NBIO 4.3.0 shift and mask macros for two adjacent PCIe configuration-space decode regions. It starts in the root-complex function `BIF_CFG_DEV0_RC0` extended PCIe capability area, beginning at the tail of `PCIE_VC1_RESOURCE_STATUS`, and continues through device serial number, Advanced Error Reporting, secondary PCIe, ACS, Data Link Feature, 16 GT/s and 32 GT/s PHY/equalization, lane margining, Alternate Protocol, and Reset Time Reporting fields. The range then crosses into `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and covers the beginning of endpoint function 0 (`BIF_CFG_DEV0_EPF0_0`) configuration space through `DATA_LINK_FEATURE_STATUS`.

The file is a generated hardware register bitfield header. This range defines C preprocessor constants only; it has no C functions, structs, variables, executable branches, loops, allocation, locking, I/O calls, or direct register accesses.

## Purpose

The purpose of this header segment is to publish the bit-level ABI for NBIO/NBIF PCIe configuration-space registers on NBIO 4.3.0 hardware. Each field is represented as the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or compose the field.

The companion NBIO 4.3.0 offset header supplies the register addresses. Runtime AMDGPU and PCIe/NBIO code can combine those offsets with these masks through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 register accessors, and PCIe/NBIO indirect config-space accessors, without hard-coding bit positions.

## Important Macro Families

### RC0 Extended PCIe Capabilities

The opening RC0 portion is rooted under `BIF_CFG_DEV0_RC0_*`. It finishes `PCIE_VC1_RESOURCE_STATUS`, then defines the device serial number enhanced capability (`PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `DW2`).

The AER block defines:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` for capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise-down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked conditions.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3` for first-error pointer, ECRC controls, multi-header recording, completion-timeout logging, and captured packet/header diagnostics.

The secondary PCIe and lane-equalization section includes `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `LANE_15_EQUALIZATION_CNTL`. These fields describe perform-equivalent-control, link equalization request interrupt enable, lane error status, and Gen3 8 GT/s upstream/downstream preset and hint fields.

The RC0 access/isolation and data-link groups include `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS`. ACS fields cover source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, direct translated P2P, I/O request blocking, memory target access controls, and unclaimed request redirection. DLF fields cover local and remote data-link feature support plus validity and exchange-enable bits.

The high-speed PHY sections define 16 GT/s and 32 GT/s capability/control/status layouts:

- `PCIE_PHY_16GT_ENH_CAP_LIST`, reserved `LINK_CAP_16GT` and `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local/RTM parity mismatch status, and per-lane `LANE_0..15_EQUALIZATION_CNTL_16GT` fields for DSP/USP presets.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and per-lane `MARGINING_LANE_CNTL`/`STATUS` pairs for lanes 0 through 15, carrying receiver number, margin type, usage model, and payload/status fields.
- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, `LINK_STATUS_32GT`, received/transmitted modified training sequence data, and per-lane `LANE_0..15_EQUALIZATION_CNTL_32GT` DSP/USP presets.

The RC0 tail covers `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA1`, `AP_DATA2`, `AP_SEL_EN_MASK`, plus `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. These encode alternate protocol negotiation metadata, selected protocol masks, vendor/usage information, and reset/link-up/FLR/D3hot-to-D0 timing values.

### EPF0 Configuration Space

After the address-block marker, the chunk starts the endpoint function 0 config decoder `BIF_CFG_DEV0_EPF0_0_*`.

The conventional PCI header section covers identity and base configuration fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1..6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, min grant, max latency, vendor capability list, and writable adapter ID. `COMMAND` exposes I/O, memory, bus master, parity, SERR, and interrupt disable bits; `STATUS` exposes capability-list presence, interrupt status, target/master aborts, system error, parity error, and related status.

The PM and PCIe capability portions include `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. These masks describe max payload and read request sizes, relaxed ordering, no-snoop, error-reporting enables, FLR, completion timeout controls, ARI forwarding, atomic operation controls, LTR/OBFF, 10-bit tags, TLP prefix controls, link speed/width, ASPM, retrain, common clock, bandwidth interrupts, target link speed, compliance/de-emphasis controls, equalization status, RTM presence, DRS, and downstream component presence.

The interrupt capability section defines MSI and MSI-X state: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data fields, extended MSI data, mask and pending fields, 64-bit aliases, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`. These fields are used to describe interrupt enablement, table/PBA placement, vector masking, pending state, address, and data payloads.

The endpoint extended capability groups include vendor-specific capability metadata and scratch dwords, virtual channel capability/control/resource registers for VC0 and VC1, device serial number, AER status/masks/severity/logs, resizable BAR capability/control registers for BAR1 through BAR6, power budget data selection/data/capability, DPA capability/status/control and eight substate power allocation dwords, secondary PCIe link/lane equalization fields, ACS capability/control, PASID capability/control, multicast capability/control/address/receive/block registers, LTR, ARI, SR-IOV capability/control/status and VF BAR/page-size/count/stride fields, and finally DLF capability/status. The assigned range stops after `BIF_CFG_DEV0_EPF0_0_DATA_LINK_FEATURE_STATUS`; the following EPF0 16 GT/s PHY fields are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime code uses these constants in a simple pattern:

1. Select the matching `cfg...` register offset from the NBIO 4.3.0 offset header.
2. Read or compose a PCIe configuration-space dword or word through AMDGPU's NBIO/register access layer.
3. Apply this header's `__SHIFT` and `_MASK` macros directly or via field helper macros.
4. Write controls, poll hardware status, clear sticky diagnostics, decode PCIe capability state, or expose values through PCIe/SR-IOV/error handling paths.

All sequencing, access rights, polling, write-one-to-clear behavior, and reset ordering are defined outside this file by PCIe rules, AMD hardware behavior, firmware/platform policy, and the consuming driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and status state.

The RC0 portion describes root-complex-side capability, error, lane, margining, alternate protocol, and reset timing state. Some fields are static capabilities, some are software-programmed policy bits, and others are hardware-updated or sticky status/log fields.

The EPF0 portion describes endpoint function state: PCI identity, class, command/status, BARs, ROM BAR, PM state, PCIe device/link capabilities, MSI/MSI-X programming, vendor-specific scratch state, virtual channels, serial number, AER logs and masks, resizable BAR controls, power budget/DPA state, ACS/PASID/multicast/LTR/ARI/SR-IOV controls, VF BAR metadata, and data-link feature negotiation state. The macros do not encode whether a field is read-only, write-once, volatile, sticky, write-one-to-clear, PF-only, firmware-owned, or safe for guest/VF access.

## Dependencies And Integration Points

The direct dependencies are the generated NBIO 4.3.0 register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` for matching register offsets.
- Any matching default/reset-value header generated for NBIO 4.3.0, where present.
- AMDGPU register helper macros and NBIO/PCIe accessors that consume generated `__SHIFT` and `_MASK` constants.

Integration points include AMDGPU NBIO initialization, PCIe config-space access, PCIe link training and speed management, AER diagnostics and recovery, SR-IOV/VF provisioning, MSI/MSI-X interrupt setup, ACS/PASID/ARI/LTR/multicast policy, resizable BAR and VF BAR exposure, DPA/power-budget handling, lane margining/equalization diagnostics, alternate protocol negotiation, and reset/link-up timing reporting.

Although the source lives under a `ceph-client` mirror path in this repository, this header is AMDGPU hardware metadata. It does not implement distributed filesystem behavior.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts at the last masks of `BIF_CFG_DEV0_RC0_PCIE_VC1_RESOURCE_STATUS` and stops immediately before EPF0 16 GT/s PHY definitions, so neighboring chunks are required for complete whole-register and whole-address-block conclusions.
- These macros are hardware ABI. A stale shift or mask can compile cleanly while silently reading or programming the wrong PCIe field.
- RC0 and EPF0 prefixes are both present. Applying an endpoint mask to a root-complex offset, or vice versa, can produce plausible bit operations against the wrong register family.
- AER status, severity, masks, header logs, and TLP prefix logs are diagnostic and policy-sensitive. Generic read/modify/write treatment can clear evidence, leave errors masked, or misclassify fatal versus non-fatal errors.
- Link equalization, lane margining, 16/32 GT/s status, and modified training sequence fields are interoperability-sensitive. Incorrect sequencing can cause link instability, failed speed changes, or misleading training diagnostics.
- ACS, PASID, ARI, multicast, SR-IOV, and VF BAR fields affect isolation, address translation, enumeration, and resource exposure. Incorrect masks or writes can break VF creation, DMA isolation, interrupt routing, or PCIe request routing.
- MSI/MSI-X fields have interrupt-delivery side effects. Wrong address/data, mask, pending, table, or PBA decoding can cause lost or misrouted interrupts.
- Reserved fields such as RC0 `LINK_CAP_16GT`/`LINK_CNTL_16GT` still have full-width masks in the generated file; consumers should not infer that all bits are writable or meaningful.
- Generated-file maintenance is fragile. Manual edits should be avoided unless cross-checked against the authoritative register database, offset header, and hardware documentation.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 headers enabled and confirm no missing, renamed, or duplicate `BIF_CFG_DEV0_RC0_*` or `BIF_CFG_DEV0_EPF0_0_*` macros.
- Compare this shift/mask range against the matching `nbio_4_3_0_offset.h` names and any generated defaults to catch register-name drift or field-order mismatches.
- Exercise PCI enumeration on affected hardware and compare decoded EPF0 config-space fields with `lspci -vv`, especially command/status, BARs, PM, PCIe capability, link capability/status, MSI/MSI-X, AER, ACS, PASID, ARI, SR-IOV, LTR, and DLF exposure.
- Run PCIe link-management tests that retrain links, change target speed where supported, and observe 8 GT/s, 16 GT/s, and 32 GT/s equalization/status fields.
- Use AER injection or platform error-observation paths to verify uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, and first-error pointer decoding.
- In SR-IOV configurations, create/remove VFs, validate VF BAR sizing and page-size fields, exercise FLR/reset paths, and confirm isolation-related ACS/PASID/ARI fields behave as expected.
- Verify MSI and MSI-X interrupt delivery under load, including enable/disable, vector masking, pending bits, MSI-X table/PBA placement, and reset/rebind behavior.
- Where hardware and platform support it, run lane margining/equalization diagnostics and confirm per-lane control/status masks decode lane number, receiver, margin type, payload, and preset fields consistently.

## Chunk Notes

Lines 10030-11080 remain in the `BIF_CFG_DEV0_RC0` root-complex config-space block and cover RC0 extended PCIe capability, AER, ACS, DLF, high-speed PHY, lane margining, alternate protocol, and reset-time reporting masks.

Lines 11081-12477 start `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and cover the beginning of endpoint function 0 through `BIF_CFG_DEV0_EPF0_0_DATA_LINK_FEATURE_STATUS`. The next chunk continues with EPF0 16 GT/s PHY fields.

### subset-b-002966: lines 12478-14939

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 12478-14939

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It covers 2,462 source lines and contains 2,119 preprocessor definitions: 1,068 `__SHIFT` constants and 1,051 `_MASK` constants. There are no C functions, structs, enums, variables, memory allocations, locks, or executable statements in this range.

The source boundary is artificial. The chunk opens at the tail of `BIF_CFG_DEV0_EPF0_0_DATA_LINK_FEATURE_STATUS`, then covers EPF0 PCIe extended capability maps for 16 GT/s PHY, lane margining, VF resizable BARs, 32 GT/s PHY, alternate protocol, and routing/transport-related data. It then crosses into `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, covering the full endpoint-function 1 PCI/PCIe configuration template through SR-IOV, VF resize BAR, and RTR fields. The final section starts `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and reaches EPF2 PCIe `DEVICE_CAP2`; EPF2 later PCIe capability, interrupt, AER, and extended-capability fields continue after this chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the field-layout half of the generated NBIO 4.3.0 hardware interface. For each NBIO or PCI configuration register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

The companion generated address header, `nbio_4_3_0_offset.h`, supplies register/config-space offsets. Runtime AMDGPU code combines the offsets with these field constants through helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related NBIO/PCI config access paths.

This chunk specifically describes PCI Express configuration-space capability layout for NBIO device 0 endpoint functions 0, 1, and 2. EPF0 content is focused on high-speed PHY/link features and newer extended capabilities. EPF1 content is a broad endpoint configuration image, including conventional PCI header fields, power management, PCIe device/link controls, MSI/MSI-X, AER, BAR resizing, DPA, ACS, PASID, multicast, LTR, ARI, SR-IOV, and RTR. EPF2 begins the same conventional PCI and PCIe capability pattern.

Although the repository path sits under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

### EPF0 high-speed PCIe capabilities

The chunk begins with the remaining `DATA_LINK_FEATURE_STATUS` fields for remote data-link feature support and validity, then maps the 16 GT/s PHY enhanced capability:

- `BIF_CFG_DEV0_EPF0_0_PCIE_PHY_16GT_ENH_CAP_LIST` supplies the extended capability ID, version, and next-pointer fields.
- `LINK_CAP_16GT` and `LINK_CNTL_16GT` are fully reserved in this generated layout.
- `LINK_STATUS_16GT` exposes equalization completion, equalization phase 1/2/3 success, and link equalization request status.
- `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT` define 16-bit parity mismatch status fields.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` define downstream/upstream 16 GT/s transmit preset fields per lane.

The margining enhanced capability is represented by:

- `PCIE_MARGINING_ENH_CAP_LIST`, with standard extended-capability ID/version/next-pointer fields.
- `MARGINING_PORT_CAP` and `MARGINING_PORT_STATUS`, indicating software-based margining support/readiness.
- `LANE_0_MARGINING_LANE_CNTL` through `LANE_15_MARGINING_LANE_CNTL`, each carrying receiver number, margin type, usage model, and margin payload.
- `LANE_0_MARGINING_LANE_STATUS` through `LANE_15_MARGINING_LANE_STATUS`, which mirror receiver, type, usage, and payload status fields.

The EPF0 VF resizable BAR capability includes:

- `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST`.
- `PCIE_VF_RESIZE_BAR1_CAP` through `PCIE_VF_RESIZE_BAR6_CAP`, each exposing the resizable BAR size capability mask.
- `PCIE_VF_RESIZE_BAR1_CNTL` through `PCIE_VF_RESIZE_BAR6_CNTL`, each exposing BAR index, BAR size, and VF BAR offset fields.

The 32 GT/s PHY enhanced capability includes:

- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT`.
- `LINK_CAP_32GT` fields for equalization bypass-to-highest-rate support, no-equalization-needed support, modified transmission support, DRS support, and flit support.
- `LINK_CNTL_32GT` fields for equalization bypass, equalization-method selection, modified TS usage, DRS, and flit controls.
- `LINK_STATUS_32GT` fields for equalization bypassed, no-equalization-needed received, modified TS received, retimer DRS message receipt, and flit status.
- Modified TS capture fields in `RECEIVED_MODIFIED_TS_DATA1/2` and `TRANSMITTED_MODIFIED_TS_DATA1/2`, covering link-valid, number of lanes, lane number, N_FTS, pre-code request, DRS, speed-change/auto-speed/auto-lane capability, and lane margining fields.
- `LANE_0_EQUALIZATION_CNTL_32GT` through `LANE_15_EQUALIZATION_CNTL_32GT`, again encoding downstream/upstream per-lane transmit presets.

The remaining EPF0 extended capability families are:

- `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA1`, `AP_DATA2`, and `AP_SEL_EN_MASK`, which describe alternate-protocol capability, control, protocol ID/data, and selection masks.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`, which expose routing/transport related capability payload fields including feature bits, segment ID, protocol ID, and lane/lane-margining data.

### EPF1 endpoint configuration block

The `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` address block is a full endpoint-function configuration template.

Conventional PCI header fields include:

- Identity and class: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status controls: `COMMAND` exposes I/O space, memory space, bus master, special cycle, memory write/invalidate, VGA palette snoop, parity response, wait cycle, SERR, fast back-to-back, interrupt disable, and capability enable bits; `STATUS` exposes immediate readiness, interrupt status, capability-list presence, DEVSEL timing, target/master abort, system error, parity error, and reserved bits.
- Header and resource fields: `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, `MAX_LATENCY`, `VENDOR_CAP_LIST`, and `ADAPTER_ID_W`.

Power-management and PCIe base capability fields include:

- `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, covering capability ID/next pointer, version, PME clock/support, D-state support, power state, no-soft-reset, PME enable/status, data select/scale, bus power enable, and PMI data.
- `PCIE_CAP_LIST` and `PCIE_CAP`, covering PCIe capability ID, next pointer, capability version, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS`, with payload/read-request sizing, relaxed ordering, extended tag, no-snoop, FLR initiation, error reporting enables/statuses, slot power limits, and pending transactions.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`, with link speed/width, ASPM/PM support, exit latency, clock power management, surprise-down/DL-active/bandwidth reporting, port number, link disable/retrain, common clock, extended sync, bandwidth interrupts, DRS signaling, negotiated width/speed, training, and data-link active status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, with completion timeout, ARI, atomic operations, LTR, TPH, ten-bit tags, OBFF, TLP prefix support/blocking, emergency power reduction, target link speed, compliance/de-emphasis, equalization status, lane-error status, and equalization phase indicators.

Interrupt capability fields include:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MASK`, 64-bit data/mask aliases, and `MSI_PENDING`/`MSI_PENDING_64`.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`, covering MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

Error-reporting, diagnostic, and vendor-specific fields include:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.
- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `PCIE_DEV_SERIAL_NUM_DW2`.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`, covering data-link protocol errors, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP prefix blocked.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`, covering receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow classes.
- `PCIE_ADV_ERR_CAP_CNTL`, including first-error pointer, ECRC generation/check capability/enables, multi-header logging capability/enables, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`.

Resource sizing, power, and secondary PCIe capabilities include:

- `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP/CNTL` through `PCIE_BAR6_CAP/CNTL`, describing resizable BAR size capability and selected BAR size.
- `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP`, describing power-budget table select/readback and system allocation.
- `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7`, describing dynamic power allocation capability, transition latency, substate status/control, and per-substate power allocations.
- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, covering secondary PCIe capability metadata, perform equalization, lane error status, and per-lane equalization presets.

Isolation, address translation, routing, and virtualization fields include:

- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`, covering source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, egress-control vector size, and related controls.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL`, covering execute-permission, privileged-mode support, maximum PASID width, and enable bits.
- `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0/1`, `PCIE_MC_RCV0/1`, `PCIE_MC_BLOCK_ALL0/1`, and `PCIE_MC_BLOCK_UNTRANSLATED_0/1`, covering multicast capability, enablement, group count, address, receiver, and block masks.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP`, covering max snoop/no-snoop latency value and scale fields.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, covering MFVC/ACS function-group capability, next-function number, forwarding, MFVC, ACS function groups, and function group selection.
- `PCIE_SRIOV_ENH_CAP_LIST`, `PCIE_SRIOV_CAP`, `PCIE_SRIOV_CONTROL`, `PCIE_SRIOV_STATUS`, `PCIE_SRIOV_INITIAL_VFS`, `PCIE_SRIOV_TOTAL_VFS`, `PCIE_SRIOV_NUM_VFS`, `PCIE_SRIOV_FUNC_DEP_LINK`, `PCIE_SRIOV_FIRST_VF_OFFSET`, `PCIE_SRIOV_VF_STRIDE`, `PCIE_SRIOV_VF_DEVICE_ID`, `PCIE_SRIOV_SUPPORTED_PAGE_SIZE`, `PCIE_SRIOV_SYSTEM_PAGE_SIZE`, `PCIE_SRIOV_VF_BASE_ADDR_0` through `_5`, and `PCIE_SRIOV_VF_MIGRATION_STATE_ARRAY_OFFSET`.
- `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST`, `PCIE_VF_RESIZE_BAR1_CAP/CNTL` through `PCIE_VF_RESIZE_BAR6_CAP/CNTL`, describing VF BAR resize capability and selected sizes.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`, mirroring the RTR-style payload used in the EPF0 block.

### EPF2 partial endpoint configuration block

The `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` block begins near the end of the chunk. It repeats the early endpoint template:

- Conventional PCI fields from `VENDOR_ID` through `MAX_LATENCY`, including command/status, BARs, ROM BAR, capability pointer, interrupts, and adapter ID.
- `VENDOR_CAP_LIST` and `ADAPTER_ID_W`.
- Power-management fields `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- USB-related conventional fields `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- PCIe base fields `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and the first part of `DEVICE_CAP2`.

Because the source range ends in `BIF_CFG_DEV0_EPF2_0_DEVICE_CAP2`, no complete conclusions should be drawn about EPF2's later PCIe, MSI/MSI-X, AER, or extended capability coverage from this chunk alone.

## APIs, Types, And Functions

There are no callable APIs or C types in this segment. The public interface is the macro namespace itself. The generated macro names are part of AMDGPU's hardware register ABI inside the driver source: consumers rely on the exact spelling, shift values, and masks matching the corresponding register offsets and the hardware register database for NBIO 4.3.0.

The constants do not encode access width, read/write permission, reset defaults, volatile behavior, write-one-to-clear behavior, or side effects. Those semantics are supplied by the PCIe specification, AMD hardware definitions, firmware setup, and the runtime driver code that chooses when and how to access the fields.

## Control Flow

This header has no local control flow. Runtime flow is external and typically follows this shape:

1. AMDGPU code selects an NBIO 4.3.0 register/configuration offset from `nbio_4_3_0_offset.h`.
2. It reads or composes a register value using these `__SHIFT` and `_MASK` constants, usually through register helper macros.
3. It writes, polls, decodes, logs, or preserves the value according to PCIe/NBIO semantics.

Likely call-path categories include NBIO initialization, PCIe capability discovery, link and equalization handling, GPU power management, SR-IOV PF/VF setup, interrupt routing, AER collection, resizable BAR configuration, ATS/PASID/IOMMU-related enablement, ACS isolation, ARI routing, and device display/power code that needs NBIO capability or register data.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. It names hardware-visible PCI configuration and extended-capability state owned by the NBIO block.

Represented state includes static identity and capability fields, driver or firmware configured control bits, host-assigned resource BARs, MSI/MSI-X message routing state, power-management status/control, PCIe link state, equalization and lane-margining status, AER sticky error state and logs, resizable BAR selections, SR-IOV VF layout, ACS/PASID/ARI isolation/routing controls, multicast state, DPA power allocations, and endpoint-function capability-chain topology.

Persistence is governed outside this file by GPU/NBIO reset domains, PCI config save/restore, firmware initialization, suspend/resume, function-level reset, SR-IOV PF/VF lifecycle, and explicit driver writes. Many fields are not ordinary memory-like storage:

- Error status and AER fields may be sticky and may require write-one-to-clear handling.
- `INITIATE_FLR` starts reset behavior rather than storing a passive bit.
- Link disable/retrain and equalization controls can disturb link training and device availability.
- MSI/MSI-X enable, mask, pending, table, and PBA fields affect interrupt delivery.
- ACS, PASID, ARI, and SR-IOV controls affect isolation, enumeration, and routing.
- BAR sizing and VF resize fields interact with PCI resource assignment and virtualization layout.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register family:

- `nbio_4_3_0_offset.h` provides matching register/configuration offsets.
- `nbio_4_3_0_default.h`, when present in the generated header set, provides reset/default values for adjacent register families.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions for field extraction and updates.

Observed in-tree include-level integration for `nbio_4_3_0_sh_mask.h` includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, the NBIO 4.3 implementation.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`.

Related display resource files include `nbio_4_3_0_offset.h` for address data without directly including this shift/mask header. The generated names also align with other NBIO generation headers, but values and feature coverage are generation-specific; consumers should use the header selected by the active ASIC/IP block.

The endpoint-function and SR-IOV fields integrate with Linux PCI enumeration, resource assignment, MSI/MSI-X setup, virtualization/PF management, IOMMU/PASID flows, AER reporting, power management, and PCIe link training. The file does not implement those policies; it supplies the bit layout used by policy code.

## Risks And Edge Cases

- Generated field drift can compile cleanly while making the driver touch the wrong hardware bit. High-risk fields include command/bus-master bits, BAR sizes, MSI/MSI-X enables, FLR, AER clear/status bits, ACS/PASID/ARI controls, SR-IOV controls, and link retrain/equalization controls.
- The chunk starts and ends inside larger logical regions. EPF0 `DATA_LINK_FEATURE_STATUS` begins before the chunk, and EPF2 `DEVICE_CAP2` continues after it. Merge/reconciliation should avoid treating those partial boundaries as complete register-family coverage.
- EPF0 16 GT/s and 32 GT/s per-lane definitions are mechanically repeated for lanes 0-15. Any lane-specific mismatch may be meaningful, but repeated definitions alone are intentional generator output.
- Reserved fields such as the 16 GT/s link cap/control masks should not be assumed writable just because a mask exists. Reserved bit preservation matters when composing register writes.
- Link equalization, margining, modified TS, DRS, and flit controls can change link-training behavior; incorrect masks can cause downtraining, failed retraining, or intermittent PCIe link failures.
- Resizable BAR and VF BAR controls affect host PCI resource layout. Wrong size masks or selected-size encodings can break BAR probing, memory windows, or VF exposure.
- MSI/MSI-X table, PBA, mask, and pending fields can cause lost, repeated, or misrouted interrupts if decoded incorrectly.
- AER status/log fields are diagnostic evidence. Incorrect write handling may clear useful data or fail to clear real faults.
- ACS/PASID/ARI/SR-IOV fields are isolation-sensitive. Wrong masks can affect DMA isolation, function routing, VF enumeration, and translation-tag behavior.
- The EPF1 block includes many PCIe optional capabilities. Runtime code must still check capability presence and platform policy before assuming a feature should be enabled.

## Test Signals

- Build AMDGPU with NBIO 4.3 and SMU13 support enabled. Missing, renamed, or malformed macros should surface through compile failures in NBIO and PM users.
- Probe a supported AMD GPU and confirm `nbio_v4_3` initialization completes without register access faults or PCIe capability decode warnings.
- PCI enumeration should show stable vendor/device/class IDs, capability chains, BAR sizing, ROM BAR state, and endpoint functions for EPF1/EPF2 where applicable.
- Link-health testing should verify expected negotiated width/speed, successful link retrain paths, no unexpected 16 GT/s or 32 GT/s equalization failures, and stable lane-status reporting.
- Margining and modified-TS diagnostics, where platform-supported, should produce coherent per-lane status without corrupting link state.
- Interrupt smoke tests should verify MSI/MSI-X enable, mask, pending, table, and PBA behavior under load.
- Error-injection or PCIe health tests should verify AER status/mask/severity decoding and preservation of header/TLP-prefix logs.
- SR-IOV validation should cover PF controls, VF counts/stride/offset/device ID, VF BARs, VF resizable BAR controls, FLR, and per-VF resource exposure.
- IOMMU/virtualization tests should exercise PASID, ACS, ARI, and related isolation/routing behavior.
- Suspend/resume and GPU reset tests should confirm PCI config save/restore and NBIO reinitialization preserve or restore expected field values.

### subset-b-002967: lines 14940-17466

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 14940-17466

## Scope

This chunk covers 2,527 lines from the generated NBIO 4.3.0 shift/mask header. It starts in the tail of the `BIF_CFG_DEV0_EPF2_0_DEVICE_CAP2` register and ends inside `BIF_BACO_EXIT_TIMER1`, after the `BACO_EXIT_SIDEBAND_TIMER` and `BACO_HW_AUTO_FLUSH_EN` shift definitions but before their masks. Within the range there are 379 register/comment sections, about 996 `__SHIFT` definitions, and about 1,140 `_MASK` definitions.

The covered range is a hardware bitfield map only. It has no C functions, structs, variables, executable branches, or in-memory persistence. It defines preprocessor constants consumed by AMDGPU NBIO, SMU, RAS, PCIe, power-management, and virtualization paths together with register offsets from `nbio_4_3_0_offset.h`.

## Purpose

The header is the bit-level ABI for programming AMD NBIO 4.3.0 registers. Each register field is represented by the usual pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to right-shift extracted fields or position new values.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, or compose the field.

Driver code combines these macros with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`. The companion offset header provides addresses such as `regRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL`, `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, and `regBIF_BX0_BIF_FB_EN`; this header supplies the field encodings.

## Important Macro Families

### EPF2 PCIe Capability Tail

The chunk begins in the final fields of `BIF_CFG_DEV0_EPF2_0_DEVICE_CAP2`, including completion timeout support, ARI forwarding, AtomicOp support, LTR, TPH completer support, 10-bit tag support, OBFF, TLP prefix support, emergency power reduction, and FRS support.

It then covers EPF2 Device Control/Status 2 and Link Capability/Control/Status 2 fields:

- Device Control 2 fields configure completion timeout, ARI forwarding, AtomicOp request/egress behavior, IDO request/completion, LTR enablement, emergency power reduction requests, 10-bit tag requester enablement, OBFF, and TLP prefix blocking.
- Link Capability 2 and Link Control 2 define supported PCIe speeds up to the hardware-advertised mask, crosslink, skip ordered-set support, retimer presence detection, DRS support, target link speed, compliance entry, autonomous speed disable, deemphasis, transmit margin, and compliance SOS.
- Link Status 2 exposes equalization completion and phases, equalization requests, retimer detection, crosslink resolution, downstream component presence, and DRS message status.

These fields are PCIe config-space representations for function 2. A mismatch between these masks and the real hardware layout would cause Linux PCIe capability programming to toggle or report the wrong bits.

### EPF2 MSI, MSI-X, Vendor, AER, BAR, Power, DPA, ACS, PASID, ARI, and RTR

The EPF2 section includes conventional MSI and MSI-X capability fields: capability IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector/extended-data controls, MSI address/data/mask/pending registers, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The extended capability macros cover:

- Vendor-specific enhanced capability headers and scratch registers.
- PCIe Advanced Error Reporting status, mask, and severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast blocked TLP, AtomicOp egress blocking, TLP prefix blocking, and poisoned TLP egress blocking.
- Correctable error status/mask fields for receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal error, corrected internal error, header log overflow, and optional semantic-error classes.
- AER capability/control fields for first error pointer, ECRC generation/checking capability and enablement, multiple header recording, TLP prefix log presence, completion timeout prefix/header log capability, and poison TLP egress blocking.
- Header log and TLP prefix log registers, each represented as full-width log data.
- BAR enhanced capability controls for BAR1 through BAR6, including capability flags and 64-bit/memory/io/prefetch/size fields.
- Power budget, Dynamic Power Allocation, Access Control Services, PASID, ARI, and Reset Time Reporting capability/control/data fields.

These macros mostly describe PCIe capability state exposed to the host and firmware. They can be read for diagnostics and may be written by low-level setup code when advertising or masking device capabilities.

### EPF3 Complete PCI Configuration Space

Lines 15596-16611 introduce `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, a full config-space map for endpoint function 3. It includes:

- Standard PCI header fields: vendor/device ID, command, status, revision, class code, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- Vendor capability and power management capability/status fields, including power state, PME control/status, data select/scale, B2/B3 support, and bus power enable.
- PCIe capability, Device/Link Capability/Control/Status, Device/Link 2, MSI/MSI-X, vendor-specific, AER, BAR, power budget, DPA, ACS, PASID, ARI, and RTR groups with the same general semantics as the EPF2 capability tail.

The EPF3 command and status fields include bus master, memory/io enable, interrupt disable, parity/SERR, target/master abort, system error, and parity detected state. EPF3 Device/Link fields include max payload/read request, phantom functions, extended tags, relaxed ordering, no-snoop, bridge config retry, FLR, ASPM/link disable/retrain/common-clock, slot clock config, link bandwidth management, equalization, LTR, OBFF, and TLP prefix controls. These definitions matter for multi-function or SR-IOV-related device exposure because they encode per-function configuration semantics.

### Indirect PCIe Access and Scratch Windows

The `nbio_nbif0_bif_bx_SYSDEC` block defines indirect access and scratch registers:

- `PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, `PCIE_DATA2`, `PCIE_INDEX_HI`, and `PCIE_INDEX2_HI` provide indexed PCIe register windows.
- `SBIOS_SCRATCH_0` through `SBIOS_SCRATCH_15`, `BIOS_SCRATCH_0` through `BIOS_SCRATCH_15`, `DRIVER_SCRATCH_0` through `DRIVER_SCRATCH_15`, and `FW_SCRATCH_0` through `FW_SCRATCH_15` are full-width scratch registers for firmware, BIOS, driver, and SBIOS coordination.
- `BIF_EngineA_INTR_CNTL` and `BIF_EngineB_INTR_CNTL` expose per-engine interrupt status/ack/enable fields for poll, read, write, and trap conditions.
- `GFX_MMIOREG_CAM_ADDR0-7`, `GFX_MMIOREG_CAM_REMAP_ADDR0-7`, and related CAM completion/control registers describe MMIO register remapping windows and completion behavior.

Scratch registers are persistent hardware state across short driver phases and can carry firmware/driver handoff information. They are not C storage; reads and writes affect device registers.

### Downstream and Endpoint PCIe Control Blocks

The `nbio_nbif0_rcc_dwn_dev0_BIFDEC1`, `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`, and `nbio_nbif0_rcc_ep_dev0_BIFDEC1` blocks define lower-level PCIe link, error, configuration, LTR, DPA, strap, and DVSEC controls.

Important downstream fields include:

- `DN_PCIE_CNTL`, `DN_PCIE_CONFIG_CNTL`, `DN_PCIE_RX_CNTL2`, `DN_PCIE_BUS_CNTL`, and `DN_PCIE_CFG_CNTL` for unsupported-request reporting, malformed atomic operations, hidden register decode, invalid PASID handling, immediate PMI behavior, and generation-specific hidden register decode.
- `DN_PCIE_STRAP_F0`, `DN_PCIE_STRAP_MISC`, and `DN_PCIE_STRAP_MISC2` for F0 DPA/PASID support and TPH/multifunction strap behavior.
- `PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_LC_SPEED_CNTL`, and `PCIE_LC_CNTL2` for AER reporting disablement, header-log timeout, immediate error messages, clearing received errors, ignoring RX protocol classes, completion timeout disablement, link generation strap enablement, and link bandwidth/state notifications.

Important endpoint fields include:

- `EP_PCIE_CNTL`, `EP_PCIE_INT_CNTL`, and `EP_PCIE_INT_STATUS` for UR reporting, malformed atomic handling, LTR-message UR behavior, corrected/nonfatal/fatal/user/misc/power-state interrupt enablement and status.
- `EP_PCIE_TX_LTR_CNTL` for snooped and non-snooped private LTR values, LTR requirement bits, disabling LTR messages outside D0, resetting LTR when data link is down, checking flow control for L1, and D-state-driven LTR write data.
- Function 0 and function 1 DPA capability, latency, control, and eight substate power allocation registers.
- Endpoint TX control and requester ID fields for SNR/relaxed-ordering override, per-function TPH disablement, and requester ID bus/device/function composition.
- Endpoint error/RX/link-control fields for AER header log timers across functions 0-7, poisoned advisory nonfatal strap, invalid PASID/not-PASID/prefix/TPH receive handling, and Gen2-Gen5 link-speed straps.
- `DVSEC_PRIV_CNTL*` and `DVSEC_VF_PRIV_CNTL*` full-width private DVSEC registers.

The concrete direct consumer observed in `amdgpu/nbio_v4_3.c` is `nbio_v4_3_program_ltr()`, which reads `regRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL`, programs a target value, and explicitly clears `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_MSG_DIS_IN_PM_NON_D0_MASK` and `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_RST_LTR_IN_DL_DOWN_MASK` before writing the register back when needed.

### BIF/BX Control, Interrupts, Doorbells, Framebuffer Access, and BACO

The final `nbio_nbif0_bif_bx_BIFDEC1` block defines general NBIO bus interface controls:

- `BIF_MM_INDACCESS_CNTL`, `BUS_CNTL`, `MM_CFGREGS_CNTL`, and `BX_RESET_CNTL` gate indirect MMIO access, VGA/HDP coherency and flush stalls, zero-byte-enable behavior, transaction-class selection, config-space function/device selection, MM write-to-config enablement, and link training.
- `INTERRUPT_CNTL` and `INTERRUPT_CNTL2` configure IH dummy reads, nonsnoop/relaxed-ordering interrupt requests, interrupt delay, general IH interrupt enablement, dummy-read bypass in MSI, and dummy-read address.
- `CLKREQB_PAD_CNTL` defines pad control, slew, wake, Schmitt enable, output, and enable bits.
- `BIF_FEATURES_CONTROL_MISC` and `HDP_ATOMIC_CONTROL_MISC` expose request/completion error path disables, MSI vector behavior, BIF ring overflow, atomic error interrupt disablement, non-virtual bus-master handling, HDP outstanding limits, 48-bit GPA aperture checking for doorbell self-ring, and HDP atomic outstanding limits.
- `BIF_DOORBELL_CNTL` controls self-ring, translation checks, untranslated loopback, non-consecutive byte-enable policy, monitor enablement, and monitor interrupt generation modes.
- `BIF_DOORBELL_INT_CNTL` exposes doorbell/RAS/ATHUB interrupt status, clear, enable, disable, and "set status when ring buffer enabled" bits.
- `BIF_FB_EN` gates framebuffer reads and writes. The prefixed version of the same concept, `BIF_BX0_BIF_FB_EN`, is used by `nbio_v4_3_mc_access_enable()` to enable or disable memory-controller framebuffer access.
- `BIF_INTR_CNTL`, `BIF_MST_TRANS_PENDING_VF`, and `BIF_SLV_TRANS_PENDING_VF` cover RAS interrupt vector selection and pending master/slave VF transactions.
- `BACO_CNTL`, `BIF_BACO_EXIT_TIME0`, and the beginning of `BIF_BACO_EXIT_TIMER1` define bus-active chip-off controls: BACO enable, dummy enable, power-off, D-state bypass, reset interrupt mask, BACO mode, RCU BIF config done, VDDSOC power-good, auto-exit, and exit timers.

`amdgpu/nbio_v4_3.c` also uses the doorbell interrupt area for RAS ATHUB error events. It reads `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, toggles the RAS ATHUB interrupt disable bit when enabling/disabling the IRQ source, checks `BIF_DOORBELL_INT_CNTL__RAS_ATHUB_ERR_EVENT_INTERRUPT_STATUS`, sets `BIF_DOORBELL_INT_CNTL__RAS_ATHUB_ERR_EVENT_INTERRUPT_CLEAR`, writes the register back, and invokes the global RAS ISR when BIF ring handling is disabled.

## Control Flow

There is no local control flow in this chunk. The runtime flow is imposed by consumers:

1. Include `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`.
2. Read a SOC15 register with `RREG32_SOC15` or via an indexed PCIe access path.
3. Extract fields with `REG_GET_FIELD` or clear/compose fields with masks and shifts.
4. Write changed values back with `WREG32_SOC15` or field-specific helpers.
5. For status/clear registers, poll status bits or write clear bits according to the hardware contract.

Register operations are order-sensitive. For example, LTR programming must preserve unrelated bits while clearing only the two LTR disable/reset bits; RAS doorbell handling must clear the interrupt status after observing it; BACO and link/power fields normally participate in larger power-state sequences coordinated with SMU or firmware.

## State and Persistence

The macros themselves are compile-time constants and persist only in object code after preprocessing. The state they address is hardware state:

- PCIe config-space capability bits advertise device/function behavior to the host and may persist across driver phases until reset or firmware reinitialization.
- Scratch registers can carry handoff data between SBIOS, BIOS, firmware, and the driver.
- Doorbell interrupt status/clear bits are event state and must be serviced carefully to avoid lost or repeated interrupts.
- LTR, DPA, ASPM/link, RX ignore, and AER controls alter live PCIe behavior.
- `BIF_FB_EN`, transaction pending bits, and BACO controls affect memory access, virtualization teardown/reset safety, and power transitions.

Because this is generated hardware ABI data, persistence behavior is determined by the underlying register block, reset domain, and firmware policy rather than by this header.

## Dependencies and Integration Points

Key dependencies are:

- `nbio_4_3_0_offset.h` for register addresses and base indices.
- AMDGPU register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.
- SOC15 NBIO IP versioning and register routing.
- Linux PCI/PCIe concepts: standard config header, MSI, MSI-X, PM, PCIe capability, AER, DPA, ACS, PASID, ARI, LTR, OBFF, FLR, and link equalization.
- AMDGPU NBIO, SMU, RAS, interrupt, doorbell, SR-IOV, and power-management code.

Observed includes/users in this source tree include `amdgpu/nbio_v4_3.c`, `pm/swsmu/smu13/smu_v13_0_0_ppt.c`, and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`. Direct use from this specific chunk includes the endpoint LTR control masks in `nbio_v4_3_program_ltr()` and unprefixed `BIF_DOORBELL_INT_CNTL` field names in RAS ATHUB interrupt handling. Similar or prefixed equivalents exist earlier in the same header, so consumers can mix prefixed register names (`BIF_BX0_BIF_DOORBELL_INT_CNTL`) with unprefixed field names (`BIF_DOORBELL_INT_CNTL`) when the field layout is identical.

## Risks

- Bitfield drift is high impact. If generated masks or shifts do not match the silicon register layout, the driver can silently program unrelated PCIe, doorbell, power, or error-reporting bits.
- The slice boundary is mid-register for `BIF_BACO_EXIT_TIMER1`; merge/reconciliation must combine the following chunk before treating that register as fully documented.
- Many fields are write-one-to-clear, status, or command-like strobes. Treating all masks as ordinary persistent configuration can lose events or trigger unintended hardware actions.
- PCIe capability fields interact with Linux PCI core assumptions. Incorrect ACS/PASID/ARI/DPA/AER/LTR advertisement or enablement can break IOMMU isolation, peer-to-peer behavior, power management, or error recovery.
- Doorbell and RAS interrupt bits are shared between normal driver interrupt flow, RAS, and BIF ring behavior. Incorrect status clearing or disable-bit polarity can suppress critical RAS events or cause repeated interrupts.
- BACO, framebuffer access, link training, and transaction-pending fields are power/reset sensitive. Writes outside the expected SMU/NBIO sequence can hang memory access, strand VF transactions, or fail power transitions.
- Scratch registers are coordination channels; treating them as disposable debug storage can overwrite firmware or driver handoff state.

## Test Signals

Useful validation signals for changes touching these definitions or consumers include:

- Build coverage for AMDGPU with NBIO 4.3.0 and SMU 13 paths enabled, catching missing or renamed macro definitions.
- Runtime boot/probe on NBIO 4.3.0 hardware, checking that PCI config space enumerates all functions, BARs, MSI/MSI-X, AER, ACS, PASID, ARI, and power capabilities as expected.
- ASPM/LTR validation under `CONFIG_PCIEASPM`: verify `nbio_v4_3_program_ltr()` writes `regRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL` without disabling private LTR messages unexpectedly and honors `pdev->ltr_path`.
- RAS ATHUB interrupt testing with BIF ring disabled: inject or simulate an ATHUB RAS event, observe `RAS_ATHUB_ERR_EVENT_INTERRUPT_STATUS`, verify the clear bit is written, and confirm the global RAS ISR runs once.
- Doorbell tests for self-ring, monitor, and interrupt generation behavior, including SR-IOV/VF cases where transaction-pending and VF reset bits matter.
- BACO enter/exit and suspend/resume stress, especially around `BACO_CNTL` mode/power-good/config-done/auto-exit and the exit timer registers split across this and the next chunk.
- PCIe AER injection or error-reporting tests for correct fatal/nonfatal/correctable status, mask, severity, header log, and TLP prefix log behavior.
- Static generation checks that every `__SHIFT` has a matching `_MASK` within the complete file, allowing for chunk boundaries where a pair may be split.

### subset-b-002968: lines 17467-19906

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 17467-19906

## Scope

This chunk is a generated AMD NBIO 4.3.0 shift/mask header segment. It contains 2,163 `#define` entries across 261 register-comment blocks. The range starts in the middle of `BIF_BACO_EXIT_TIMER1`, continues through BACO timers, memory type control, graphics address LUTs, SR-IOV virtual-function enable/status bitmaps, reset/remap/ring-buffer/mailbox/pad/power/GPIO controls, RCC decode and strap fields, PF mailbox and HDP coherency controls, GDC clock/power controls, shadowed PCI bridge configuration registers, PF1 MM-index registers, and ends after the first `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL__PM_CONTROL__SHIFT` line.

The content is C preprocessor data only. It defines no functions, structs, variables, local state, allocation, locking, branching, or direct MMIO operations. Its public interface is the generated register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by AMDGPU register helpers.

## Purpose

`nbio_4_3_0_sh_mask.h` supplies the bitfield half of the NBIO 4.3.0 hardware ABI. Driver code pairs these macros with addresses from `nbio_4_3_0_offset.h`, then uses helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 field helpers to compose or decode register values without hard-coding bit positions.

This chunk specifically describes fields used for:

- BACO exit timing and S5/power-transition support.
- Graphics address lookup-table configuration for NBIF routing and MSI address behavior.
- SR-IOV VF register-write, doorbell, and framebuffer access gates and their matching status bitmaps for VF0 through VF30.
- Reset, HDP flush remapping, BIF ring buffer, mailbox, pad, GPIO, CLDO, and SMN clock-select control.
- RCC register decode, peer range, bus-number, requester ID, link, margining, GPU IOV, host VM, and console IOV behavior.
- RCC straps that describe PCIe/NBIO advertised capabilities, including link speeds, power-management support, ACS, ATS, PASID, ARI, AER, SR-IOV, MSI/MSI-X, BAR sizing, device IDs, class codes, reset timing, and vendor-specific capability sizing.
- PF-side HDP coherency flush request/done bits, PF mailbox words, VMHV mailbox, GDC clock/power controls, SWUS/SUC indexed access, PCI bridge shadow registers, and the beginning of VF0 PCIe config-space decoding.

## Important Macro Families

### BACO, Memory, LUT, and VF Gates

The range begins with the tail of `BIF_BACO_EXIT_TIMER1`, defining hardware auto-flush, hardware exit disable, PX_EN output-enable behavior, BACO mode select, and automatic exit-clear disable masks. `BIF_BACO_EXIT_TIMER2`, `BIF_BACO_EXIT_TIMER3`, and `BIF_BACO_EXIT_TIMER4` add 20-bit timer fields for LCLK backup, dummy-enable clear, and BACO-enable clear timing. `MEM_TYPE_CNTL` exposes a single `BF_MEM_PHY_G5_G3` bit.

`NBIF_GFX_ADDR_LUT_CNTL` controls LUT enable, MSI address mode, and broadcast mode. `NBIF_GFX_ADDR_LUT_0` through `_15` each expose a 24-bit `ADDR` field, giving a compact table-like mapping area for NBIF graphics address routing.

`VF_REGWR_EN`, `VF_DOORBELL_EN`, and `VF_FB_EN` are 31-bit per-VF enable bitmaps for VF0 through VF30. Their matching `VF_REGWR_STATUS`, `VF_DOORBELL_STATUS`, and `VF_FB_STATUS` families expose per-VF status bits. `VF_DOORBELL_EN` also includes `VF_DOORBELL_RD_LOG_DIS` at bit 31. These families are central SR-IOV controls: a single wrong bit selects a different virtual function.

### Reset, Remap, Ring Buffer, Mailbox, Pad, and S5 Controls

`GFX_RST_CNTL` exposes graphics reset control. `REMAP_HDP_MEM_FLUSH_CNTL` and `REMAP_HDP_REG_FLUSH_CNTL` hold remapped HDP flush control values used by runtime code that maps KFD/amdgpu-visible flush registers into a remap aperture.

`BIF_RB_CNTL`, `BIF_RB_BASE`, `BIF_RB_RPTR`, `BIF_RB_WPTR`, `BIF_RB_WPTR_ADDR_HI`, and `BIF_RB_WPTR_ADDR_LO` describe BIF ring-buffer enable, size, base, read/write pointers, and write-pointer address fields. `MAILBOX_INDEX`, `BACO_AZ_ENHANCE_CTRL`, `BIF_MP1_INTR_CTRL`, and the `BIF_*_GPUIOV_CFG_SIZE` registers describe mailbox indexing, audio/BACO request handling, MP1 interrupt routing, and GPU IOV config sizing for VCN and GFX/SDMA.

`BIF_PERSTB_PAD_CNTL`, `BIF_PX_EN_PAD_CNTL`, `BIF_REFPADKIN_PAD_CNTL`, `BIF_CLKREQB_PAD_CNTL`, `BIF_PWRBRK_PAD_CNTL`, `BIF_WAKEB_PAD_CNTL`, and `BIF_VAUX_PRESENT_PAD_CNTL` define pad pull-up/pull-down, input receive, impedance, output-enable, and signal-specific GPIO settings. `GPIO_CNTL_0_REG` through `GPIO_CNTL_4_REG` repeat a broader GPIO control pattern with input, output-enable, and output value fields.

`PCIE_PAR_SAVE_RESTORE_CNTL`, `BIF_S5_MEM_POWER_CTRL0`, `BIF_S5_MEM_POWER_CTRL1`, `BIF_S5_DUMMY_REGS`, `CLDO_075_S5_CTRL`, `CLDO_12_PCIE_CTRL`, and `SMNCLK_SEL` describe PCIe parameter save/restore state, S5 memory-power control words, S5 dummy storage, LDO voltage/config enable fields, and S5 SMN clock selection.

### RCC Decode, Peer, Bus, Link, and Strap Controls

The `nbio_nbif0_rcc_dev0_BIFDEC1` address block starts at `RCC_ERR_INT_CNTL`. It defines SR-IOV invalid-register-access interrupt enable, BACO request-disables, doorbell aperture reset enable, vendor-defined-message support, margining parameter fields, GPU IOV region and host VM enable fields, console IOV mode and VF spacing, peer register ranges, bus-control policy, config aperture sizing, XDMA bounds, and miscellaneous feature controls for unsupported-request handling, MSI/MSI-X pending behavior, ECRC error policy, and poison-flag handling.

`RCC_BUSNUM_*`, `RCC_CAPTURE_HOST_BUSNUM`, `RCC_HOST_BUSNUM`, `RCC_PEER*_FB_OFFSET_*`, `RCC_DEVFUNCNUM_LIST*`, `RCC_DEV0_LINK_CNTL`, `RCC_CMN_LINK_CNTL`, `RCC_EP_REQUESTERID_RESTORE`, `RCC_LTR_LSWITCH_CNTL`, and `RCC_MH_ARB_CNTL` define bus-number filters, captured host bus numbers, peer framebuffer offsets, device/function number lists, link control behavior, requester-ID restore, LTR local switch behavior, and multi-host arbitration.

The `nbio_nbif0_rcc_strap_BIFDEC1` block dominates the middle of the chunk. `RCC_BIF_STRAP0` through `RCC_BIF_STRAP6` describe broad BIF/PCIe strap state such as bus/device/function IDs, link width and port presence, L1/LTR/OBFF behavior, completion timeout policy, maximum payload/read-request sizes, lane/equalization presets, Gen2/Gen3/Gen4/Gen5 capability, ten-bit tags, hotplug-style presence bits, error reporting, clock power management, local DLF support, ACS-related capability, downstream port settings, and vendor/device identity fields.

`RCC_DEV0_PORT_STRAP0` through `RCC_DEV0_PORT_STRAP14` define device-port advertised behavior: device/function numbers, link width/speed, reset and power timing, link power-management latencies, MSI/downstream support, ECRC, DSN, VC, atomic operations, ACS, power budget tables, port numbers, revision IDs, target link speed, Gen5 and 32 GT/s lane-equalization presets, TPH, and downstream-specific error reporting.

`RCC_DEV0_EPF0_STRAP*` and `RCC_DEV0_EPF1_STRAP*` define endpoint function straps. EPF0 receives the richest set here: device/vendor/subsystem IDs, SR-IOV VF device ID and page size, class code and total VFs, RTR reset/DLUP/FLR/D3 timings, SR-IOV enable, BAR sizing/disables, PASID width and capability bits, ARI/AER/ACS/ATS enables, MSI/MSI-X and interrupt pin behavior, FLR/PME/atomic support, doorbell and VF aperture sizes, VGA disable, VF mapping mode, GPUIOV VSEC length, extended capability pointers, and interrupt routing behavior. EPF1 repeats many of the same identity, SR-IOV, BAR, MSI/MSI-X, PM, and capability fields, with numerous empty strap placeholders also present.

### PF, GDC, Shadow, and VF0 PCI Config

The `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` block covers PF-visible behavior. `BIF_BX_PF_BIF_BME_STATUS` exposes bus-master status, `BIF_BX_PF_BIF_ATOMIC_ERR_LOG` captures atomic error metadata, and `BIF_BX_PF_DOORBELL_SELFRING_GPA_APER_*` defines the self-ring doorbell GPA aperture. HDP coherency controls include register/memory flush, memory-flush-only, invalidate-only, and 31 client-style `BIF_BX_PF_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF_GPU_HDP_FLUSH_DONE` bitmaps. `BIF_BX_PF_BIF_TRANS_PENDING`, address-LUT bypass, transmit/receive mailbox dwords, mailbox control, mailbox interrupt control, and VMHV mailbox fields round out the PF virtualization/coordination surface.

The `nbio_nbif0_gdc_GDCDEC` block includes SHUB non-PF drop behavior, `NGDC_MGCG_CTRL` medium-grain clock-gating fields, reserved dwords, graphics doorbell sent status, ATDMA/S2A arbitration weights and modes, early wakeup controls, MCA SMN posted behavior, and NGDC power-gating master/slave controls.

`SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI` plus `SUC_INDEX` and `SUC_DATA` expose indexed access windows. The shadow block describes upstream PCI bridge shadow state: command IO/memory enables, BAR1/BAR2, secondary/subordinate bus numbers, IO base/limit, memory base/limit, prefetchable memory windows, and upper 32-bit window halves. `BIF_BX_PF1_MM_INDEX`, `BIF_BX_PF1_MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI` provide an indexed PF1 MMIO access path.

The final address block begins `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`. This chunk covers VF0 config-space fields from vendor/device ID through the first `LINK_CNTL` shift: command/status, revision/class fields, BARs, ROM BAR, capability pointer, interrupt line/pin, PCIe capability header, device capability/control/status, and link capability. The matching `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL` masks and later VF0 PCIe capability fields continue in the next chunk.

## Control Flow

There is no executable control flow in this header. The operational flow is external:

1. NBIO 4.3, SMU13, virtualization, power-management, or platform code includes `nbio_4_3_0_offset.h` and this shift/mask header.
2. The caller selects an address macro such as `cfgBIF_BX_PF_GPU_HDP_FLUSH_REQ`, `cfgRCC_BUS_CNTL`, `cfgNGDC_MGCG_CTRL`, or `cfgBIF_CFG_DEV0_EPF0_VF0_0_COMMAND`.
3. Register helper macros combine the selected register name, field name, shift, and mask to update or extract a field.
4. Hardware, firmware, the PF driver, a VF guest, or a hypervisor observes the result according to the selected access path and permissions.

Because the chunk includes PCIe config-space, SR-IOV, indexed MMIO, mailbox, HDP flush, and power-management fields, the real ordering and polling rules live in the driver logic and hardware specification, not in this generated header.

## State and Persistence Behavior

The header itself has no runtime state. It names hardware-visible fields whose values can persist across ordinary software calls until overwritten or until a reset/power/firmware/hypervisor event changes them.

Important represented state includes:

- BACO and S5 transition timers and power-control settings.
- Address LUT entries and address-LUT bypass state.
- Per-VF enable/status state for register writes, doorbells, and framebuffer access.
- Ring-buffer pointers, remap registers, mailbox valid/ack/data bits, and VMHV mailbox interrupt enables.
- Pad, GPIO, CLDO, and SMN clock selection state used around board signaling and low-power modes.
- RCC decode policy, peer ranges, host/peer bus numbers, requester-ID restore, XDMA bounds, link controls, and feature-policy bits.
- Strap-derived capability state that determines what PCIe/SR-IOV/ATS/PASID/ARI/AER/MSI/MSI-X/ACS/link/power behavior the device advertises.
- PF HDP flush request/done bitmaps and PF mailbox transport state.
- GDC clock-gating, arbitration, wakeup, MCA SMN, and power-gating controls.
- Shadowed upstream PCI bridge aperture and command state.
- VF0 PCI config-space identity, command/status, BAR, ROM BAR, device capability/control/status, and link capability fields.

Many fields are not ordinary read/write storage. Status latches, HDP flush request/done bits, mailbox valid/ack bits, reset controls, FLR-capable fields, PCIe status/error fields, link controls, and power-gating controls can have side effects, clear-on-write behavior, hardware ownership, firmware ownership, or ordering requirements.

## Dependencies and Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the addresses for these field names. Examples from the same tree include `cfgBIF_BACO_EXIT_TIMER2` at `0x302038b8`, `cfgRCC_BUS_CNTL` at `0x30203784`, `cfgBIF_BX_PF_GPU_HDP_FLUSH_REQ` at `0x30203898`, `cfgNGDC_MGCG_CTRL` at `0x30203ba8`, `cfgBIF_CFG_DEV0_EPF0_VF0_0_VENDOR_ID` at `0xfffe10300000`, and `cfgBIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL` at `0xfffe10300074`. The same offset header also contains SMN/register-space aliases such as `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP2` and later instance-specific forms.

Observed local consumers of `nbio_4_3_0_sh_mask.h` are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which includes this header with the matching offset header and uses generated NBIO field macros in register reads/writes and `REG_SET_FIELD`/mask operations.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`, which includes the NBIO 4.3.0 offset and mask headers alongside SMU13 headers.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, which includes the same NBIO 4.3.0 generated headers for SMU13 platform behavior.

The field vocabulary also lines up with generated NBIO/NBIF headers for other ASIC revisions. That makes it useful for cross-version comparison, but it also means callers must use the NBIO 4.3.0 address and mask files as a matched pair.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can enable the wrong VF, mis-size a BAR, corrupt a mailbox handshake, break HDP flush signaling, alter PCIe advertised capabilities, or change power/reset behavior.
- The per-VF bitmaps are dense and repetitive. VF0 through VF30 use one bit each; off-by-one mistakes compile cleanly while affecting a different virtual function.
- Strap fields are capability-defining. Incorrect SR-IOV, ACS, ATS, PASID, ARI, AER, MSI/MSI-X, BAR, link-speed, or power-management bits can cause enumeration failures, isolation bugs, or host/device protocol errors.
- PF mailbox and VMHV mailbox fields mix data, valid, ack, and interrupt-enable bits. Incorrect sequencing can lose notifications or leave one side waiting for an acknowledgment.
- HDP flush request/done bits must match the hardware client convention expected by the runtime flush path. Mis-decoding these bits can produce stale CPU/GPU memory visibility.
- PCIe config-space fields have standard side effects and access policies. Command/status, BAR, ROM BAR, link, device-control, and error-status fields should not be treated as inert storage.
- Power, BACO, S5, GDC MGCG, and power-gating controls are timing-sensitive. Changing timer or gating masks without matching firmware/hardware sequencing can lead to resume, reset, or low-power failures.
- This chunk has two incomplete boundaries: it starts after earlier `BIF_BACO_EXIT_TIMER1` shift definitions and ends after only the first VF0 `LINK_CNTL` shift line. The final per-file report must reconcile adjacent chunks before claiming complete coverage of those registers.

## Test and Validation Signals

Useful validation is mostly build, generated-header consistency, hardware enumeration, power-management, and SR-IOV behavior:

- Build AMDGPU paths that include `nbio_4_3_0_sh_mask.h`, especially `nbio_v4_3.c` and SMU13 platform files.
- Check that every field family in this chunk has a matching address in `nbio_4_3_0_offset.h` where applicable, and that generated mask widths match the intended field widths.
- Exercise SR-IOV flows that enable and disable VF register-write, doorbell, and framebuffer access, then verify the expected VF0 through VF30 status bits change.
- Validate VF0 PCI config-space enumeration: vendor/device ID, command/status, BAR sizing, ROM BAR, capability list, device capability/control/status, and link capability should decode as expected.
- Run doorbell and self-ring aperture tests that cover PF doorbell aperture base/cntl fields and doorbell status reporting.
- Exercise HDP memory/register flush paths and confirm request/done bits transition correctly under GPU memory coherency tests.
- Test BACO/S5 suspend-resume and reset paths for timer, CLDO, GPIO/pad, and SMN clock-selection regressions.
- Validate GDC clock-gating and power-gating controls under runtime power-management and idle/resume workloads.
- Use PCIe/AER/ATS/PASID/ARI capability and error-injection tests where platform support exists, especially around strap-derived capability fields and RCC bus/error policy bits.
- Static review should compare repeated strap, VF bitmap, and PCI config-space families against neighboring NBIO 4.3.0 chunks and other ASIC versions to detect generator or copy drift.

## Unresolved Cross-Chunk References

This range begins with `BIF_BACO_EXIT_TIMER1` fields whose earlier shift definitions are in the previous chunk. It ends immediately after `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL__PM_CONTROL__SHIFT`; the rest of `LINK_CNTL` and later VF0 PCIe config-space fields continue in the next chunk. The merge/reconciliation lane should stitch those boundaries before producing the final source-tree-aligned per-file report.

### subset-b-002969: lines 19907-22328

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 19907-22328

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, dynamic allocations, locks, branches, loops, or direct register accesses in this range.

The assigned lines contain 2,142 `#define` entries: 1,071 `__SHIFT` constants and 1,071 `_MASK` constants across 272 commented register blocks. The slice starts in the middle of the `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL` definition, completes the remainder of the `VF0_0` PCIe virtual-function configuration image, contains complete `BIF_CFG_DEV0_EPF0_VF1_0` and `BIF_CFG_DEV0_EPF0_VF2_0` blocks, and starts `BIF_CFG_DEV0_EPF0_VF3_0` before stopping after the first field of `VF3_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.

Although this file lives under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bitfield positions for NBIO 4.3.0 PCIe/SR-IOV virtual-function configuration-space registers. Each hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update a field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, supplies matching `regBIF_CFG_DEV0_EPF0_VF*_*` register offsets and base indices. Runtime AMDGPU code combines those offsets with this shift/mask header through the normal register helper layer, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF0 fragment starts at `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL__PTM_PROP_DELAY_ADAPT_INTER_B__SHIFT`, so the `PM_CONTROL` shift immediately before it is outside this chunk while the matching `PM_CONTROL_MASK` is inside. The rest of VF0 covers link status, PCIe device/link capability 2 controls and status, MSI and MSI-X capability fields, vendor-specific extended capability fields, AER status/mask/severity/log fields, ARI capability/control fields, route-through-router enhanced capability, and `RTR_DATA1`/`RTR_DATA2` payload fields.

The complete VF1 and VF2 blocks repeat a full Type 0 PCI configuration-space image for `BIF_CFG_DEV0_EPF0`. Each block includes identity/header fields (`VENDOR_ID`, `DEVICE_ID`, command/status, revision/class codes, cache line, latency, header/device type, BIST), BAR fields `BASE_ADDR_1` through `BASE_ADDR_6`, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min-grant/max-latency fields.

The VF1 and VF2 PCIe capability sections define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, phantom function support, role-based error reporting, function-level reset capability/initiation, completion timeout controls, atomic operation support/enables, ID-based ordering, LTR, OBFF, emergency power reduction, 10-bit tags, link speed/width, ASPM, clock power management, link disable/retrain, common clock, autonomous width/speed disables, DRS signaling, de-emphasis, compliance controls, equalization status, and downstream component presence.

The interrupt capability portions cover MSI and MSI-X. MSI fields include capability-list linkage, enable/multiple-message/64-bit/per-vector masking controls, MSI message address low/high, message data, extended message data, mask and pending dwords, and 64-bit aliases for data, extended data, mask, and pending state. MSI-X fields include table size, function mask, enable, table BIR/offset, and pending-bit-array BIR/offset.

The vendor-specific and AER portions define PCIe vendor-specific enhanced capability list/header fields, two scratch payload dwords, AER enhanced capability list fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, poisoned TLP egress blocked, receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow conditions.

The ARI and router portions expose `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. ARI fields include capability ID/version/next pointer, MFVC and ACS function-group capability, next-function number, MFVC/ACS enable, and function-group selection. Router fields are opaque full-dword payload masks in this header.

The VF3 block is only partial in this chunk. It covers VF3 from identity/header fields through BARs, PCIe device/link controls, MSI/MSI-X, vendor-specific enhanced capability fields, and the first `PCIE_ADV_ERR_RPT_ENH_CAP_LIST__CAP_ID__SHIFT` line. The rest of VF3 AER, ARI, router, and any following VF definitions are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU code selects a `regBIF_CFG_DEV0_EPF0_VF*_*` offset from `nbio_4_3_0_offset.h`.
2. It reads or composes a PCIe configuration-space dword through the AMD register access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or via helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`.
4. It writes a control value, decodes a capability/status value, polls a hardware-owned bit, clears a sticky diagnostic bit, or exposes decoded state to PCIe, SR-IOV, interrupt, reset, RAS, or diagnostics code.

Typical consuming flows include VF configuration-space presentation, SR-IOV VF lifecycle handling, PCIe link/power policy, function-level reset, MSI/MSI-X interrupt delivery, AER diagnostics, ARI enumeration, route-through-router configuration, and PF or hypervisor inspection of VF state.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SR-IOV management code.

The represented state includes VF identity/header values, BAR and ROM address windows, command/status bits, capability-list pointers, PCIe capability/control/status fields, link capability and link-training state, MSI/MSI-X programming state, vendor-specific scratch fields, AER error status/mask/severity/log state, ARI function-group controls, and router data payloads. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some may be sticky or write-one-to-clear diagnostics. The generated masks do not encode access permissions, reset defaults, side effects, polling rules, or ownership boundaries.

VF1 and VF2 are complete within this chunk and can be reasoned about as complete repeated config-space layouts. VF0 and VF3 are boundary fragments and require adjacent chunks before making whole-VF or whole-register claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database. This file must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the matching register addresses and base indices. This tree has no sibling `nbio_4_3_0_default.h`, so reset/default-value validation for these fields must come from the hardware database, firmware behavior, or runtime observations rather than a local default header.

Direct in-tree consumers of the NBIO 4.3 generated headers include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. `amdgpu_discovery.c` selects `nbio_v4_3_funcs` or `nbio_v4_3_sriov_funcs`, and `nbio_v4_3.c` provides the NBIO v4.3 operations for HDP flush offsets, PCIe index/data offsets, memory access enablement, doorbell range programming, interrupt handler control, clock gating/light sleep, LTR/ASPM programming, register remapping, and RAS error-event handling.

The most relevant integration surfaces are AMDGPU NBIO/BIF setup, PCIe index/data indirect access, SR-IOV VF initialization and teardown, VF interrupt delivery, PCIe link and power-management policy, FLR/reset flows, AER/RAS diagnostics, ARI-capable enumeration, router/VSEC diagnostics, suspend/resume, and runtime power transitions. These fields also overlap generic PCIe concepts managed by platform firmware and the Linux PCI core: command/status, BARs, MSI/MSI-X, PCIe device/link control, AER, ARI, LTR, OBFF, completion timeout, and FLR.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after `VF0_0_LINK_CNTL__PM_CONTROL__SHIFT` but includes `PM_CONTROL_MASK`, and it stops before the mask fields for `VF3_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`; adjacent chunks are required for complete VF0 and VF3 analysis.
- These are untyped preprocessor constants. A stale mask or shift can compile cleanly while decoding or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around `VF0_0`, `VF1_0`, `VF2_0`, and `VF3_0` can silently target the wrong virtual function and break SR-IOV isolation, interrupt routing, or diagnostics.
- Register-address and field-mask mismatches are easy in generated headers. A valid `VF2_0_LINK_CNTL` mask applied to a `VF1_0`, `VF3_0`, or non-VF offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, completion timeout, relaxed ordering, no-snoop, LTR, OBFF, ARI, link disable/retrain, or target-speed values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Width, aliasing, table offset/BIR, mask, pending-bit, or enable mistakes can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures, confuse VF resource sizing, or undermine isolation expectations in virtualized configurations.
- ARI and router/VSEC fields affect enumeration and routing semantics. Incorrect next-function numbers, function-group controls, or opaque router data interpretation can affect VF discovery and PF/hypervisor coordination.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c`, SMU13 power-management files, or generated-header include paths.
- Compare the VF0 through VF3 field layouts against `nbio_4_3_0_offset.h` to confirm register names, order, and repeated VF stride remain synchronized.
- Boot affected hardware and confirm PCIe config exposure remains sane: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, vendor-specific capability, AER, ARI, and router fields should decode consistently.
- In SR-IOV configurations, create and remove VFs around VF0 through VF3, bind guest drivers, exercise VF FLR, and verify that VF isolation, config-space access, ARI behavior, mailbox/reset flows, and PF-visible diagnostics remain stable.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, ASPM/LTR, and link retraining tests while monitoring link speed/width, completion timeout behavior, DRS/link bandwidth status, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.
- For ARI-capable configurations, verify function enumeration, next-function values, and function-group controls through PCIe config-space dumps before and after VF lifecycle and reset operations.

## Chunk Notes

- Lines 19907-20402 are the tail of `BIF_CFG_DEV0_EPF0_VF0_0`, starting inside `LINK_CNTL` and completing through `RTR_DATA2`.
- Lines 20403-22024 are complete `BIF_CFG_DEV0_EPF0_VF1_0` and `BIF_CFG_DEV0_EPF0_VF2_0` PCIe VF config-space shift/mask blocks.
- Lines 22025-22328 begin `BIF_CFG_DEV0_EPF0_VF3_0` and end after `PCIE_ADV_ERR_RPT_ENH_CAP_LIST__CAP_ID__SHIFT`; the rest of that register and the following VF3 AER/ARI/router fields continue after this chunk.

### subset-b-002970: lines 22329-24747

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 22329-24747

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,141 preprocessor field definitions across 2,419 source lines. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `BIF_CFG_DEV0_EPF0_VF3_0_*` virtual-function PCI configuration template at the Advanced Error Reporting extended capability, covers complete `VF4`, `VF5`, and `VF6` templates, and ends near the beginning of `VF7` after the `COMMAND` fields start. The source boundary is artificial: the earlier standard PCI/PCIe/MSI/MSI-X/VSEC fields for VF3 are in the previous chunk, and most of VF7 is in the next chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of the generated NBIO 4.3.0 hardware register interface. For each named NBIO/PCI configuration register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update the field.

The companion `nbio_4_3_0_offset.h` supplies matching register/config-space offsets, and AMDGPU code uses both headers through register field helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 register addressing helpers, and NBIO/PCI config access paths.

This chunk specifically describes SR-IOV virtual-function PCI configuration-space layout for NBIO device 0, endpoint function 0. The repeated `BIF_CFG_DEV0_EPF0_VF<n>_0_*` names map per-VF identity, BAR/resource, PCIe capability, interrupt, vendor-specific, Advanced Error Reporting, ARI, and Readiness Time Reporting fields.

## Important Macro Families

The VF3 tail in this chunk covers the later extended-capability portion of a virtual-function config image:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` defines the AER extended-capability ID, version, and next-pointer fields.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` define uncorrectable PCIe error classes: data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover correctable receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow events.
- `PCIE_ADV_ERR_CAP_CNTL` covers first-error pointer, ECRC generation/check capability and enable bits, multi-header receive capability/enablement, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG[0-3]` and `PCIE_TLP_PREFIX_LOG[0-3]` expose four 32-bit diagnostic words each for captured TLP headers and prefixes.
- `PCIE_ARI_*` covers Alternative Routing-ID Interpretation capability metadata, MFVC/ACS function-group capability bits, next-function number, function-group enables, and selected ARI function group.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` define Readiness Time Reporting metadata and timing fields: reset time, DL-up time, FLR time, D3hot-to-D0 time, and the validity bit.

The complete `VF4`, `VF5`, and `VF6` blocks repeat the full VF PCI configuration template:

- Conventional PCI header fields: vendor/device ID, command, status, revision ID, class-code bytes, cache-line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- PCI command/status bits: I/O and memory access, bus mastering, special cycle, memory write invalidate, parity response, SERR, interrupt disable, immediate readiness, interrupt status, capability-list presence, DEVSEL timing, target/master abort, signaled system error, and parity-error detected.
- PCIe capability fields: PCIe capability-list header, PCIe version, device/port type, slot implementation, interrupt message number, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Device and link controls: correctable/non-fatal/fatal/unsupported-request reporting, relaxed ordering, max payload, extended tags, phantom functions, aux power PM, no-snoop, max read request size, bridge config retry, function-level reset initiation, link disable/retrain, common clock, extended sync, ASPM controls, bandwidth-management interrupts, target link speed, compliance controls, de-emphasis, equalization status, completion-timeout settings, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, emergency power reduction, ten-bit tags, and end-to-end TLP prefix blocking.
- MSI/MSI-X fields: capability IDs and next pointers, MSI enable and multiple-message fields, 32-bit and 64-bit message address/data fields, mask and pending fields, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability fields: VSEC capability-list metadata, VSEC ID/revision/length, and two 32-bit scratch payload registers.
- AER, ARI, and RTR fields with the same semantics as the VF3 tail.

The VF7 start covers only `VENDOR_ID`, `DEVICE_ID`, and the beginning of `COMMAND`; the rest of VF7 is outside this chunk.

## APIs, Types, And Functions

There are no runtime APIs or C types here. The public interface is the macro namespace itself. Consumers rely on the generated names, shifts, and masks staying synchronized with the companion offset/default headers and the hardware register database.

The constants are untyped preprocessor integer literals, usually using an `L` suffix and sized to the represented field. They do not encode access width, volatility, reset value, read/write permission, write-one-to-clear behavior, or side effects. Callers must know whether a field is PCI config space, an extended capability, a read-only capability bit, a writable control bit, a sticky status bit, or a command bit that triggers hardware behavior.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU, firmware-facing, SR-IOV, or PCIe code selects a register/config offset from `nbio_4_3_0_offset.h`.
2. The code reads, decodes, composes, or updates a register value using this file's `__SHIFT` and `_MASK` constants directly or through field helper macros.
3. The updated or decoded value is written back, polled, saved/restored, reported, or used to make PCIe/NBIO policy decisions.

Likely flows using these fields include VF config-space presentation, PCI enumeration, BAR sizing and resource programming, command-bit enablement for memory access and bus mastering, PCIe link/device negotiation, function-level reset, MSI/MSI-X interrupt setup, AER status collection and masking, ARI routing, Readiness Time Reporting, and SR-IOV validation.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration registers for SR-IOV virtual functions. Persistence is determined by the GPU/NBIO reset domain, firmware initialization, PF/VF management, hypervisor policy, VF FLR, suspend/resume save-restore, and explicit driver writes.

Represented state includes static PCI identity and capability data, host-programmed command bits, BAR and ROM resource registers, interrupt routing state, MSI/MSI-X message address/data/mask/pending state, PCIe device/link control settings, hardware-updated link/device status, AER sticky status/mask/severity and diagnostic logs, vendor-specific scratch payloads, ARI function-routing controls, and RTR timing-validity data.

Several fields are not ordinary storage bits. PCI command bits enable memory access and bus mastering, `INITIATE_FLR` starts a function-level reset, link retrain/disable controls affect PCIe link state, MSI/MSI-X enable and mask fields affect interrupt delivery, and AER status/log fields can be sticky or write-one-to-clear depending on hardware semantics. This generated file only gives the bit layout; ordering, privilege, and side-effect rules are implemented by hardware and driver call sites.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 header set:

- `nbio_4_3_0_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets.
- Other generated NBIO 4.3.0 headers provide related defaults and register metadata where present.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions for field extraction and update.

Observed include-level integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, SMU 13 power-management files such as `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`, and display resource files that include the matching offset header. The per-VF fields integrate with PCI enumeration/configuration, SR-IOV VF exposure, PF/VF or hypervisor-managed virtualization, interrupt delivery, AER reporting, reset handling, ARI routing, PCIe link management, and readiness-time reporting.

Although this source path is under a `ceph-client` mirror, the content is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while making software touch the wrong hardware bit. This is most risky for command, DMA enable, interrupt, FLR, AER clear/mask, link-control, ARI, and RTR fields.
- The chunk starts and ends inside repeated VF templates. Merge/reconciliation should combine adjacent chunks before making complete per-VF claims about VF3 or VF7.
- Repetition across VF4, VF5, and VF6 is intentional. Any per-VF mismatch may indicate generator or register-database drift, but chunk-boundary truncation must not be misread as such drift.
- PCI command bits control memory access, bus mastering, SERR/parity behavior, and interrupt disable. Wrong masks can break VF probing, DMA enablement, or isolation assumptions.
- Link controls, completion-timeout controls, payload/read-request sizing, relaxed ordering, no-snoop, ID-based ordering, and atomic operation bits affect PCIe liveness and memory-ordering behavior.
- MSI/MSI-X table offsets, pending bits, masks, and enables can cause lost, repeated, or misrouted interrupts if decoded or programmed incorrectly.
- AER logs are diagnostic evidence. Treating status/log fields as normal writable state can clear useful error data or fail to clear real errors.
- ARI controls affect function routing and enumeration. Incorrect masks can break VF discovery or route transactions to the wrong function.
- RTR fields report timing characteristics for reset, DL-up, FLR, and D3hot-to-D0 transitions. Incorrect masks can make management software under-wait, over-wait, or trust invalid timing data.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Missing or misspelled macros should be caught by direct users of the generated header set.
- Runtime probe on affected AMD GPUs should show stable PCI config enumeration for SR-IOV virtual functions, valid vendor/device IDs, correct class/capability data, and sane BAR sizing.
- SR-IOV validation should exercise multiple VFs, especially VF4 through VF6, because this chunk contains mechanically repeated per-VF templates.
- Interrupt smoke tests should verify MSI/MSI-X enablement, masking, pending-bit behavior, and absence of spurious or lost interrupts.
- PCIe health signals include expected negotiated link width/speed, successful FLR and link-retrain paths, no unexpected AER storms, and preserved AER diagnostics when errors are injected.
- ARI/virtualization tests should verify VF enumeration, function routing, and isolation under PF/VF and hypervisor-controlled setups.
- RTR-related validation should compare advertised reset/DL-up/FLR/D3hot-to-D0 timing fields against observed wait paths and ensure the `VALID` bit is honored before timing data is trusted.

### subset-b-002971: lines 24748-27173

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 24748-27173

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It contains C preprocessor constants for bit positions and masks in NBIF/BIF PCI configuration decode space for SR-IOV virtual functions.

The range starts inside the `BIF_CFG_DEV0_EPF0_VF7_0_COMMAND` register, after the first command-field masks and after all command shift definitions. It then covers the rest of the VF7 PCI/PCIe capability block, full VF8 and VF9 PCI/PCIe capability blocks, and the beginning of the VF10 block through the first `DEVICE_CAP2` shift definitions. The next line after this chunk continues `VF10_0_DEVICE_CAP2`, so this range is not a complete VF10 block.

The chunk is declarative. It defines roughly 2,100 `#define` constants over 276 visible register-name prefixes. It has no functions, structs, executable control flow, allocation, locking, initialization, or direct persistence logic.

## Purpose

The macros provide symbolic field layouts for NBIO 4.3.0 PCI configuration-space registers so AMDGPU code and generated register helpers can decode, mask, and compose hardware register values without embedding raw bit constants.

The dominant naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK`

where `<n>` is mostly `7`, `8`, `9`, or `10` in this slice. The companion `nbio_4_3_0_offset.h` maps these same register names to concrete NBIO configuration-space addresses such as the VF7 window starting around `0xfffe10307000`, while this file describes the field packing inside each addressed register.

## Address Blocks and Register Coverage

Visible address-block markers in this slice:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf9_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf10_bifcfgdecp`

The `VF7_0` address-block marker and early `COMMAND` definitions are before the chunk. This range begins with `VF7_0_COMMAND` masks for `PAL_SNOOP_EN`, parity response, stepping, SERR, fast back-to-back, and interrupt disable, then covers these VF7 register families:

- PCI header/configuration fields: `STATUS`, revision and class fields, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: capability list headers, MSI message control/address/data/mask/pending registers, MSI-X message control, table location, and PBA location.
- PCIe vendor-specific extended capability fields: capability-list header, vendor-specific header, and two vendor-specific data registers.
- Advanced Error Reporting fields: AER extended capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ARI and ready-time reporting fields: ARI enhanced capability list, ARI capability/control, router enhanced capability header, and `RTR_DATA1`/`RTR_DATA2` timing fields.

`VF8_0` and `VF9_0` are complete within this chunk and repeat the same register families as VF7, including basic PCI header fields, PCIe capabilities, MSI/MSI-X, vendor-specific extended capability, AER, ARI, and RTR timing.

`VF10_0` starts at its address-block marker and includes basic PCI header fields through `LINK_STATUS`, plus the initial `DEVICE_CAP2` shifts for completion timeout, ARI forwarding, atomic operation support, CAS128 support, and no-relaxed-ordering peer-to-peer passing. Its `DEVICE_CAP2` remaining shifts, masks, and later capability registers are outside this chunk.

## Important APIs, Types, and Functions

There are no C APIs, type definitions, or functions in this header chunk. The externally consumed interface is the macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` model standard PCI command/status bits such as memory access, bus mastering, SERR, interrupt disable, capability-list presence, abort reporting, parity reporting, and interrupt status. In this range, VF7 command coverage is partial because earlier masks and shifts are in the previous chunk.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, and adapter/class/header fields describe the virtual function's PCI header layout. BAR-like fields use wide masks such as `0xFFFFFFFFL`, while ROM BAR fields split enable/validation bits from the base-address bits.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` expose PCIe capability version, device type, slot implementation, payload/read-request sizing, relaxed ordering, no-snoop, FLR, power-management support, ASPM controls, link retrain/disable, common clock, negotiated link speed/width, and link-bandwidth events.
- `*_DEVICE_CAP2` and `*_DEVICE_CNTL2` cover newer PCIe controls and capabilities such as completion timeout values, ARI forwarding, atomic operations, LTR, TPH completer support, 10-bit tags, OBFF, end-to-end TLP prefixes, emergency power reduction, FRS, EETLP blocking, IDO, LTR enable, OBFF enable, emergency power reduction request, and FRS signaling.
- `*_LINK_CAP2`, `*_LINK_CNTL2`, and `*_LINK_STATUS2` define supported link-speed vectors and equalization-related control/status fields, including target speed, enter compliance, selectable de-emphasis, transmit margin, compliance SOS, modified compliance, equalization request, and equalization phase statuses.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability programming, including MSI enablement, multi-message capability/enable, 64-bit address capability, per-vector masking capability, message address/data fields, vector mask/pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and pending-bit-array BIR/offset.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define AER status, reporting masks, severity classification, first-error pointer, ECRC support and enable bits, multiple-header recording, TLP prefix log presence, and completion-timeout prefix/header logging capability.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` are raw 32-bit capture fields used by PCIe error diagnostics.
- `*_PCIE_VENDOR_SPECIFIC*` exposes the PCIe vendor-specific extended capability header and two 32-bit vendor-defined data registers.
- `*_PCIE_ARI_*` defines Alternate Routing-ID capability/control fields including MFVC and ACS function-group support/enables, next function number, and function-group selection.
- `*_PCIE_RTR_ENH_CAP_LIST`, `*_RTR_DATA1`, and `*_RTR_DATA2` describe ready-time reporting capability headers and timing fields for reset, data-link-up, FLR, D3hot-to-D0, and validity.

## Control Flow

This chunk has no runtime control flow. Inclusion is controlled only by the file-level header guard established at the top of `nbio_4_3_0_sh_mask.h`.

Typical consumer flow is inferred from the generated register convention:

1. A translation unit includes `nbio/nbio_4_3_0_offset.h` and `nbio/nbio_4_3_0_sh_mask.h`.
2. The consumer selects a register address from the offset header, for example a `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` definition.
3. The driver reads the register through AMDGPU MMIO, PCI configuration, or indirect NBIO/BIF access helpers.
4. The value is decoded with the `*_MASK` and `__SHIFT` constants, commonly through `REG_GET_FIELD`-style helpers.
5. If the driver must modify a control register, it composes the new field value with `REG_SET_FIELD`-style helpers and writes the result back.

Local include-level integration confirms the header is pulled into `amdgpu/nbio_v4_3.c` and SMU 13 power-management files. In `nbio_v4_3.c`, adjacent NBIO 4.3.0 masks are used for revision decoding, framebuffer access enablement, doorbell aperture setup, ROM offset extraction, LTR programming, and ASPM programming. The VF-specific macros in this chunk are not directly referenced by ordinary C symbols in the inspected tree snapshot; they are still part of the generated NBIO register ABI available to SR-IOV and diagnostics paths.

## State and Persistence Behavior

The header stores no software state and persists nothing by itself. It describes state held in hardware configuration registers.

Control fields represented here are persistent hardware configuration until reset, function-level reset, PF/VF reinitialization, guest driver action, or host PCI policy changes. Examples include command enable bits, interrupt disable, MSI/MSI-X enable and mask controls, MSI-X function mask, AER masks and severity controls, ECRC enable bits, completion timeout controls, LTR enablement, IDO/OBFF/FRS controls, ARI forwarding, and link-control settings.

Status and diagnostic fields are hardware-updated or sticky according to PCIe rules. Examples include PCI status error bits, device/link status, AER correctable and uncorrectable status, first-error pointer, TLP header logs, TLP prefix logs, MSI pending bits, link equalization phase indicators, link bandwidth status, and RTR valid/timing values. Some status fields may be clear-on-write or write-one-to-clear in hardware even though this generated header does not encode access semantics.

Because these are per-VF configuration blocks, state is scoped to individual SR-IOV virtual functions. VF7, VF8, VF9, and VF10 have separate configuration windows in the offset header and separate field macro namespaces here. Host PF management, guest VF drivers, FLR, PCI reset, and SR-IOV enable/disable sequences can all change the underlying hardware state.

## Dependencies and Integration Points

Primary dependencies and integration points:

- `nbio_4_3_0_offset.h` supplies the register addresses matching these field macro prefixes. For example, the VF7 block begins at `cfgBIF_CFG_DEV0_EPF0_VF7_0_VENDOR_ID` and proceeds through capability offsets for the same register names used in this chunk.
- `amdgpu/nbio_v4_3.c` includes this header and provides the NBIO 4.3 function table (`nbio_v4_3_funcs` and `nbio_v4_3_sriov_funcs`) used by discovery and IP block setup.
- SMU 13 power-management files include the NBIO 4.3.0 offset and mask headers, giving power-management code access to NBIO register field layouts.
- AMDGPU register helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD` depend on the generated `__SHIFT` and `_MASK` naming convention.
- Linux PCI/PCIe concepts are mirrored in the macro names: standard PCI config header, PCIe capability, MSI, MSI-X, AER, ARI, link control/status, completion timeout, LTR, OBFF, FRS, and TLP prefix logging.
- SR-IOV PF/VF orchestration depends on the separate VF configuration windows represented here. These macros describe high-numbered virtual functions in the device 0 endpoint function 0 decode space.
- Interrupt setup and teardown integrate through MSI/MSI-X address, data, mask, pending, table, PBA, and enable/function-mask fields.
- Error handling and RAS diagnostics integrate through AER status/mask/severity and header/prefix log definitions, even though this chunk contains only field constants.

No `nbio_4_3_0_default.h` file was present at the inspected path, so default/reset-value integration for this exact header family is not represented locally the way it is for some other generated NBIO versions.

## Risks and Edge Cases

- The file is generated and highly repetitive. A wrong shift or mask can silently corrupt every consumer that decodes or composes that field.
- The chunk boundaries are partial: VF7 starts mid-`COMMAND` and VF10 ends mid-`DEVICE_CAP2`. Merge/reconciliation must not treat this chunk alone as a complete VF7 or VF10 documentation unit.
- VF8 and VF9 should be structurally identical for same-named registers except for the VF number and offset-window base. Copy-generation drift is hard to spot because most lines differ only by the numeric prefix.
- AER register families have similar field names across status, mask, and severity registers. Using the wrong macro family can clear the wrong status, suppress reporting, or misclassify uncorrectable errors.
- MSI and MSI-X register layouts contain overlapping addresses and encoded low bits in standard PCI capability space. Consumers must not treat all masked address/table/PBA fields as simple byte addresses without preserving BIR and capability-specific bits.
- BAR and ROM BAR fields mix address bits with enable, validation, and type bits. Raw writes that do not preserve low control bits can break PCI resource decoding.
- Link-control and link-control-2 fields can affect link training, target speed, compliance mode, equalization, and bandwidth management. Incorrect writes can degrade performance or make the device unreachable.
- Device capability/control 2 fields interact with platform support for ARI, atomics, LTR, OBFF, 10-bit tags, FRS, and TLP prefixes. Enabling unsupported features can break routing, DMA ordering, or power-management behavior.
- VF configuration state may be concurrently influenced by host PF code, PCI core, virtualization tooling, and guest drivers. Register access needs the same synchronization and ownership assumptions as the surrounding SR-IOV management path.
- Masks use `L` suffixes and cover 8-bit, 16-bit, and 32-bit fields. Consumers should avoid implicit truncation, sign-extension, and width assumptions when using them outside normal AMDGPU register helper macros.

## Test Signals

Useful validation signals for this chunk:

- Compile AMDGPU configurations that include `nbio_4_3_0_sh_mask.h`; malformed macro names, duplicate definitions with different values, or missing generated constants should fail early.
- Generated-register consistency checks comparing this range against the hardware register database and `nbio_4_3_0_offset.h`, including the VF7/VF8/VF9/VF10 window bases and capability offsets.
- Pattern checks across VF8 and VF9 to confirm same-named fields have identical shifts and masks; separately handle partial VF7 and VF10 boundaries.
- SR-IOV smoke tests with enough virtual functions enabled to enumerate VF7 through VF10, bind host/guest drivers, enable memory and bus mastering, and verify PCI config-space access.
- MSI/MSI-X tests on these VFs: program MSI address/data, toggle MSI enable and per-vector mask bits, program MSI-X table/PBA locations, confirm interrupts deliver, mask, unmask, and quiesce correctly.
- PCIe capability inspection with driver debug output or `lspci -vv` to verify payload sizes, max read request, FLR, completion timeout, LTR, OBFF, FRS, ARI, MSI/MSI-X, and link capability/status decode as expected.
- AER injection or observation tests to verify uncorrectable/correctable status bits, masks, severity fields, first-error pointer, ECRC controls, TLP header logs, and TLP prefix logs decode correctly.
- Reset lifecycle tests around VF FLR, PF teardown/recreation, guest detach/attach, and SR-IOV disable/re-enable to confirm status/control fields return to expected defaults.
- Link-management tests that exercise ASPM, target link speed, retrain, equalization status, and bandwidth notification bits without leaving the link in compliance or disabled states.

### subset-b-002972: lines 27174-29592

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 27174-29592

## Scope

This chunk is a generated AMD NBIO 4.3.0 shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, enums, variables, branches, loops, allocations, locks, direct MMIO operations, or local persistence behavior.

The range starts inside `BIF_CFG_DEV0_EPF0_VF10_0_DEVICE_CAP2`, after that register's first capability-field shifts have already been defined by the previous chunk. It then completes the rest of the VF10 PCIe capability/control, MSI/MSI-X, vendor-specific, AER, ARI, and reset-time-reporting masks. The range fully covers the generated PCI configuration-space field layouts for `VF11` and `VF12`. It begins the `VF13` block and stops inside `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_MASK`, so the remainder of VF13 AER mask/severity/log/ARI fields continues after this work item.

Although this source tree is under a `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`nbio_4_3_0_sh_mask.h` gives AMDGPU code symbolic bit layouts for NBIO 4.3.0 registers. Each field is exported as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or update a field.

This specific range describes PCI configuration-space fields for SR-IOV-style virtual functions under `BIF_CFG_DEV0_EPF0_VF<n>_0_*`. Runtime code pairs these macros with matching addresses from `nbio_4_3_0_offset.h`, then typically applies them through `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, or related SOC15/NBIO helpers.

The assigned interval contains 2,139 `#define` entries across 272 register-name prefixes: 1,067 shift definitions and 1,072 mask definitions. The mask/shift imbalance is expected because the chunk begins and ends at artificial boundaries inside register definitions.

## Important Macro Families

The VF10 opening fragment completes PCIe 2.0+ and interrupt/error-reporting fields. It includes `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` fields for completion timeout, ARI forwarding, AtomicOp support/control, ID-based ordering, LTR, OBFF, 10-bit tags, TLP prefix support/blocking, supported link speeds, de-emphasis, equalization status, crosslink status, DRS, and downstream-component presence.

The VF10 interrupt portion defines MSI and MSI-X layouts: capability-list IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector-mask/extended-data bits, MSI address/data/mask/pending dwords, MSI 64-bit aliases, MSI-X table size/function-mask/enable, table BIR/offset, and pending-bit-array BIR/offset.

The VF10 PCIe extended capability portion defines vendor-specific enhanced capability headers and scratch dwords, AER capability headers, uncorrectable and correctable error status/mask/severity bits, AER capability/control fields, header-log dwords, TLP-prefix-log dwords, ARI capability/control fields, and reset-time-reporting fields. High-risk AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.

The `VF11` and `VF12` blocks are complete generated PCI configuration-space layouts. Each block starts with identity and standard PCI header fields: vendor/device ID, command, status, revision/class codes, cache line, latency, header type, BIST, six BAR dwords, CardBus CIS pointer, subsystem IDs, ROM base and validation fields, capability pointer, legacy interrupt line/pin, and min/max latency.

The full VF11/VF12 PCIe capability groups define device capability/control/status and link capability/control/status fields. These cover max payload and read request sizes, FLR capability/control, extended tags, relaxed ordering, no-snoop, error-reporting enables/status bits, ASPM capability/control, link speed/width, link training, slot clock, data-link active, bandwidth-management interrupts, clock power management, retrain/link disable, common clock configuration, and DRS signaling.

VF11/VF12 then repeat the `DEVICE_CAP2`/`CNTL2` and `LINK_CAP2`/`CNTL2`/`STATUS2` families described above, followed by the same MSI/MSI-X capability and AER/ARI/RTR extended capability groups used by VF10.

The VF13 block is complete only through early AER. It includes identity/header, BAR, PCIe capability, device/link capability/control/status, PCIe 2.0+ capability/control/status, MSI/MSI-X, vendor-specific enhanced capability, AER enhanced capability, and uncorrectable error status. The range ends after the first three shift definitions of `VF13_0_PCIE_UNCORR_ERR_MASK`; the matching masks and later VF13 AER severity/log/ARI/RTR fields are outside this chunk.

## Control Flow

There is no executable control flow in this header. The runtime pattern is external:

1. NBIO 4.3.0 AMDGPU code includes the generated offset and shift/mask headers for this ASIC generation.
2. The caller chooses a VF-specific register address from `nbio_4_3_0_offset.h`.
3. It reads or composes a 16-bit or 32-bit PCI configuration-space value through the NBIO/SOC15 register-access path.
4. It uses this header's `__SHIFT` and `_MASK` constants, directly or through field helper macros, to inspect or modify individual PCIe capability, interrupt, or error-reporting fields.

The `VF10`, `VF11`, `VF12`, and `VF13` suffixes are part of the hardware address namespace. Reusing a mask with the wrong VF register can still compile, but it represents the wrong virtual function's PCI configuration state.

## State And Persistence Behavior

This header stores no software state and persists nothing to disk. It describes hardware-backed PCI configuration and NBIO state owned by the GPU, platform PCIe logic, firmware, the host kernel, and SR-IOV/hypervisor policy.

The represented state includes VF identity and class presentation, PCI command/status, BARs and ROM decode state, capability-list linkage, PCIe capability and control fields, link-training and link-status bits, completion-timeout and ordering controls, LTR/OBFF/AtomicOp/ARI controls, MSI and MSI-X programming state, AER status/mask/severity/log state, TLP prefix logs, vendor-specific scratch registers, ARI function-group controls, and reset-time-reporting values.

Some fields are software-programmed controls, some are hardware-updated status, and some may be sticky diagnostics with clear semantics defined by PCIe/AER behavior or hardware documentation. The generated masks do not encode reset defaults, access widths, write-one-to-clear behavior, polling timeouts, ownership rules, or ordering requirements.

## Dependencies And Integration Points

The primary dependency is the AMD generated NBIO 4.3.0 register database. This file must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, where the corresponding `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` addresses are defined.

Direct in-tree include users of the NBIO 4.3.0 offset/mask pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`

Display DCN32/DCN321 resource files include the matching NBIO 4.3.0 offset header, while field-level NBIO programming in AMDGPU and SMU code uses the shift/mask header. The most relevant integration surfaces for this chunk are SR-IOV VF enumeration/configuration, VF BAR and ROM presentation, VF PCIe capability reporting, VF MSI/MSI-X programming, VF AER reporting, ARI support, link-capability reporting, and function reset/power-transition timing metadata.

## Risks And Edge Cases

- The chunk boundaries are artificial. The range starts inside VF10 `DEVICE_CAP2` and ends inside VF13 `PCIE_UNCORR_ERR_MASK`; adjacent chunks are required for full VF10 and VF13 coverage.
- These macros are untyped constants. A stale or mismatched mask can compile while reading or writing the wrong hardware bit.
- The repeated VF blocks are mechanically similar. Off-by-one suffix mistakes around VF10/VF11/VF12/VF13 can affect another virtual function's PCI config, interrupt, or error-reporting state.
- PCI configuration registers frequently pack multiple fields into 8-, 16-, or 32-bit values. Using the wrong access width or treating adjacent fields as separate registers can corrupt neighboring capability state.
- MSI and MSI-X layouts contain intentional aliases and format-dependent fields, especially 32-bit versus 64-bit MSI data/mask/pending locations. Consumers must follow the matching PCI capability format.
- AER status/mask/severity bits can be sticky, write-one-to-clear, or policy-sensitive. Generic read/modify/write treatment can lose diagnostic evidence, fail to clear latched errors, or mask significant PCIe faults.
- Capability `NEXT_PTR` fields define the PCIe capability chain. Incorrect generated values or wrong offsets can break VF capability discovery by the host, guest, or hypervisor.
- ARI and function-group fields affect multi-function/VF enumeration. Incorrect masks can make VF routing or capability walking look valid while exposing the wrong function topology.
- Link capability/status fields are status/control metadata. Misreporting supported speeds, widths, equalization state, or DRS/crosslink support can confuse PCIe policy and diagnostics.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware/SR-IOV integration oriented:

- Build AMDGPU with NBIO 4.3.0 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c` or SMU13 include paths.
- Diff this chunk against the authoritative NBIO 4.3.0 register database and `nbio_4_3_0_offset.h` to confirm register names, VF suffixes, and field masks remain synchronized.
- In SR-IOV environments, enumerate VFs spanning at least VF10 through VF13 and verify PCI config-space identity, BARs, capability chains, PCIe capability values, MSI/MSI-X capabilities, and ARI/AER visibility.
- Exercise VF MSI and MSI-X enable, mask, unmask, pending-bit, and interrupt-delivery paths; lost or misrouted interrupts can indicate address/data/mask field drift.
- Trigger or observe PCIe/AER diagnostics and confirm correct uncorrectable/correctable status, mask, severity, header-log, and TLP-prefix-log behavior for the affected VFs.
- Exercise FLR, D3hot-to-D0, reset-time-reporting, suspend/resume, and VF teardown paths while watching for stuck completion-timeout, transaction, or AER states.
- Run link retrain/equalization and PCIe power-management tests where available, checking that link capability/control/status fields report coherent speed, width, ASPM, LTR, OBFF, and equalization state.

## Chunk Notes

- Lines 27174-27611 complete the VF10 PCIe capability, MSI/MSI-X, vendor-specific, AER, ARI, and RTR field definitions started by the previous chunk.
- Lines 27612-28333 cover a complete `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp` field-mask block.
- Lines 28334-29055 cover a complete `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp` field-mask block.
- Lines 29056-29592 begin `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp` and stop inside `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_MASK`.

### subset-b-002973: lines 29593-31977

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 29593-31977

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: field `__SHIFT` values and `_MASK` values for NBIF/BIF PCIe configuration and port-control registers. There are no C functions, structs, enums, local variables, loops, branches, allocations, locks, or direct register accesses in the range.

The range starts in the middle of `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_STATUS`, completes the VF13 AER tail, contains complete PCI/PCIe configuration layouts for `BIF_CFG_DEV0_EPF0_VF14_0_*` and `BIF_CFG_DEV0_EPF0_VF15_0_*`, then enters the `nbio_pcie0_pswusp0_pciedir_p` address block and covers PCIe port/link-control register fields through `PCIE_LC_CNTL6`. The next chunk is needed for the continuation after `PCIE_LC_CNTL6`.

Although this file is under the local `ceph-client` source mirror, the content is AMDGPU hardware metadata. It describes GPU NBIO/NBIF PCIe bitfields, not Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header slice is to publish the bit-level ABI for NBIO 4.3.0 PCIe virtual-function configuration space and PSWUSP0 PCIe link-control registers. Companion offset headers provide the register addresses; this file provides the field positions and masks used to extract or compose register values.

The dominant macro patterns are:

- `BIF_CFG_DEV0_EPF0_VF13_0_*`, for the tail of VF13 Advanced Error Reporting and ARI/RTR fields.
- `BIF_CFG_DEV0_EPF0_VF14_0_*` and `BIF_CFG_DEV0_EPF0_VF15_0_*`, for complete SR-IOV virtual-function PCI config-space images.
- `PCIEP_*`, `PSWUSP0_PCIE_*`, `PCIE_RX_*`, and `PCIE_LC_*`, for physical PCIe port, receiver, error injection, link training, equalization, lane, speed, and retimer controls.

Driver code consumes these macros through generated-register helper conventions such as `REG_GET_FIELD`, `REG_SET_FIELD`, raw mask/shift operations, and AMDGPU register access wrappers. The macros are a hardware contract: stale or shifted values can compile cleanly while causing the driver to inspect, mask, or program the wrong bit.

## Important Macro Families

### VF13 AER Tail

The chunk opens in the tail of `BIF_CFG_DEV0_EPF0_VF13_0_PCIE_UNCORR_ERR_STATUS` and then covers `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, four `PCIE_HDR_LOG*` words, four `PCIE_TLP_PREFIX_LOG*` words, ARI enhanced capability/cap/control fields, RTR enhanced capability, and `RTR_DATA1/2`.

These fields model the Advanced Error Reporting status/mask/severity split for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal, multicast-blocked, atomic egress blocked, TLP-prefix blocked, and poisoned-egress-blocked errors. The ARI/RTR fields expose alternate routing-ID capability/control and reset/DL-up/FLR/D3hot-D0 timing data. The chunk boundary means VF13's earlier PCI config fields are not complete here.

### VF14 and VF15 PCI Configuration Images

The full `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` blocks repeat the same generated layout for virtual functions 14 and 15:

- Standard PCI identity and header fields: vendor ID, device ID, command, status, revision ID, programming interface, subclass, base class, cache line size, latency timer, header type, BIST, six BARs, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability-list header, PCIe capability, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2.
- Interrupt capability fields: MSI capability list, MSI message control, MSI address low/high, MSI data, extended data, mask, 64-bit data and mask aliases, pending bits, MSI-X capability list, MSI-X message control, table descriptor, and PBA descriptor.
- Vendor-specific and AER extended capability fields: vendor-specific enhanced capability header/data, AER enhanced capability header, uncorrectable and correctable error status/mask/severity, AER capability/control, TLP header logs, and TLP prefix logs.
- ARI and RTR fields: ARI enhanced capability list, ARI capability/control, RTR enhanced capability, and reset/DL-up/FLR/D3hot-D0 timing validity fields.

The VF14 and VF15 layouts should be structurally identical except for the VF number in the macro prefix. This repetition is useful for generated-header validation: fields with the same suffix should carry the same shifts and masks across both VFs unless the hardware database explicitly diverges.

### PSWUSP0 PCIe Port Registers

At `nbio_pcie0_pswusp0_pciedir_p`, the chunk moves from VF config-space images to the physical PCIe port and link-control surface:

- `PCIEP_RESERVED`, `PCIEP_SCRATCH`, and `PCIEP_PORT_CNTL` expose miscellaneous port state and control bits such as power state, hotplug message control, DLLP receive behavior, lane reversal, bridge-side flush behavior, ECRC checking, routing-ID logic, interrupt message selection, and wake masking.
- `PCIE_TX_REQUESTER_ID` exposes function, device, and bus-number fields used to form requester IDs.
- `PCIE_P_PORT_LANE_STATUS` exposes per-lane receive-valid and lane-reversal status.
- `PSWUSP0_PCIE_ERR_CNTL` exposes link-training and error-handling controls, including CRC checking, ECRC skipping, link-down error masking, data-parity masking, poisoned-advisory-nonfatal masking, and AER private masks for bad DLLP/TLP.
- `PSWUSP0_PCIE_RX_CNTL` is a dense receiver-error policy register. It controls whether the receiver ignores IO/BE/message/CRC/config/completion/EP/length/max-payload/TC/unsupported-request/AT/PASID/prefix errors, whether to NAK on FIFO full or generate a NAK, completion-timeout behavior, TPH disablement, FLR timeout handling, CTO masking, RTRC/BFRC swapping, and DPC private trigger behavior.
- `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_VENDOR_SPECIFIC`, `PCIE_RX_CNTL3`, and the three `PCIE_RX_CREDITS_ALLOCATED_*` groups expose expected sequence number, vendor-specific receive state, receiver filtering/poison behavior, tag availability checks, expected sequence number reset, and posted/non-posted/completion credit allocation.
- `PCIEP_ERROR_INJECT_PHYSICAL` and `PCIEP_ERROR_INJECT_TRANSACTION` expose deliberate error-injection controls for physical-layer and transaction-layer testing.
- `PCIEP_NAK_COUNTER` exposes the NAK count field used for link diagnostics.

### Link Controller, Training, Speed, Width, and Equalization

The `PCIE_LC_*` and `PSWUSP0_PCIE_LC_*` groups define the link controller surface:

- `PCIE_LC_CNTL` covers LC enablement, link reversal enablement, hot reset, link disablement, receiver detection, standby and lane-active status, extended sync, lane-count selection, link-status clear, common clock config, ASPM and L1 controls, configured link width, lane-allocated status, ASPM gating while in L0, and directed speed change.
- `PCIE_LC_TRAINING_CNTL` covers training sequencing and timeout policy, including configuration-link timeouts, link-lost detection, deassertion delays, skip-order set behavior, DLLP behavior, electrical idle handling, EIEOS/EIOS behavior, directed/link-down resets, reserved lane selection, and safe mode.
- `PCIE_LC_LINK_WIDTH_CNTL` covers negotiated/configured link width, lane-to-slot selection, link-width read/write controls, renegotiation enablement, upconfigure support, short-reconfigure behavior, reconfiguration arcs, and reversal decisions.
- `PCIE_LC_N_FTS_CNTL` and `PSWUSP0_PCIE_LC_SPEED_CNTL` cover fast-training-sequence counts, lane-change FTS programming, initial speed, current data rate, speed-change command/status, auto-speed-change enablement, equalization search mode, equalization disablement at 8 GT/s, and speed-change failure counters.
- `PCIE_LC_STATE0` through `PCIE_LC_STATE5` expose low-level LTSSM/debug state encodings for link-controller state machines.
- `PSWUSP0_PCIE_LC_CNTL2`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_CDR_CNTL`, and `PCIE_LC_LANE_CNTL` expose additional bandwidth-change, receiver-detection, EIEOS, L1 powerdown, auto disable, parity ignore, recovery, quiesce, clock-data-recovery, and per-lane control fields.
- `PCIE_LC_CNTL3`, `PCIE_LC_CNTL4`, `PCIE_LC_CNTL5`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, and the visible start of `PCIE_LC_CNTL6` cover deemphasis, auto speed-change retry policy, hot plug, reconfiguration, equalization coefficients, local presets, forced 8 GT/s coefficient settings, best equalization results, requested coefficient forcing, SRIS/SRNS support, and retimer presence overrides/status.

These fields are timing-sensitive. They do not implement link training themselves, but they define the masks used by runtime code that steers link bring-up, retraining, equalization, speed changes, margin/debug behavior, and error recovery.

## Important APIs, Types, and Functions

This chunk declares no functions, types, or exported C symbols. Its API is the generated macro namespace.

Important consumer-facing field categories are:

- Standard PCI fields such as `*_COMMAND__BUS_MASTER_EN`, `*_COMMAND__MEM_ACCESS_EN`, `*_STATUS__CAP_LIST`, BAR address masks, ROM enable/address fields, and interrupt line/pin fields.
- PCIe device/link fields such as max payload, max read request, relaxed ordering, no-snoop, completion timeout, FLR, ASPM, link retrain, link disable, negotiated speed/width, equalization-complete and phase-success bits, target link speed, and DRS/retimer status.
- MSI/MSI-X fields for vector enablement, masking, pending state, message address/data, table size, function mask, table BIR/offset, and PBA BIR/offset.
- AER fields for correctable/uncorrectable status, masks, severity, first-error pointer, ECRC generation/checking, header logs, and TLP prefix logs.
- ARI/RTR fields for function-group capability/control, next-function number, reset-time validity, DL-up timing, FLR timing, and D3hot-D0 timing.
- Port-level `PCIEP_*`, `PSWUSP0_PCIE_*`, `PCIE_RX_*`, and `PCIE_LC_*` fields for physical port control, receiver error policy, credit accounting, error injection, LTSSM/link training, link width/speed management, equalization, SRIS, and retimers.

The usual integration contract is that the matching `__SHIFT` and `_MASK` names are passed to helper macros or used by hand-coded bit operations. A missing or mismatched pair is a compile-time or generated-header correctness issue; a wrong numeric value is a hardware behavior issue.

## Control Flow

There is no executable control flow in this header chunk. Runtime flow is supplied by AMDGPU code that includes the NBIO 4.3.0 register headers:

1. Code selects an ASIC/IP-version-specific register address from the companion offset header.
2. It selects the field mask and shift from this header.
3. It reads the target register through PCI config, MMIO, SMN, SOC15, or NBIO-specific helpers.
4. It extracts fields or composes a read/modify/write value using `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent mask/shift logic.
5. Hardware applies the change as PCIe VF capability state, interrupt capability programming, AER policy/logging, ARI/RTR behavior, receiver policy, error injection, link training, speed/width/equalization policy, or retimer/SRIS state.

For the port/link-controller groups, higher-level code must also respect hardware sequencing: link disable/retrain, directed speed changes, coefficient forcing, error injection, and indirect state-machine controls can require ordering, polling, and timeout handling outside this header.

## State and Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware-backed register fields whose state is controlled by reset, firmware/BIOS setup, PCI enumeration, SR-IOV PF/VF policy, guest or host drivers, power management, link retraining, FLR, hot reset, and error-recovery paths.

For VF14 and VF15, represented state includes PCI command/status, class and BAR presentation, ROM and subsystem IDs, MSI/MSI-X configuration, PCIe device/link controls, AER status/masks/severity/logs, ARI controls, and RTR timing data. Some of these fields are durable configuration until reset or reprogramming; others are read-only capability bits, hardware-updated status bits, sticky diagnostics, or write-one-clear error state depending on PCIe semantics.

For PSWUSP0, represented state includes receiver ignore policies, completion-timeout behavior, NAK and credit accounting, error injection settings, LC training/speed/width controls, LTSSM debug state, equalization coefficients, bandwidth-change controls, lane controls, SRIS/SRNS settings, and retimer presence overrides/status. Many control bits can alter live link behavior immediately. Status fields such as lane-valid, lane-reversal, link-state, equalization results, speed-change failure counters, and retimer presence are hardware-updated.

The header does not encode access permissions or clear semantics. Callers must know whether a field is read-only, read/write, sticky, write-one-clear, self-clearing, reserved, or timing-sensitive from the PCIe specification, AMD's register database, and existing AMDGPU access patterns.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 4.3.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies matching register offsets.
- Any NBIO 4.3.0 default-value header generated from the same hardware database.
- AMDGPU register helper conventions such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_*`, `WREG32_*`, `RREG32_PCIE`, `WREG32_PCIE`, SOC15 helpers, and NBIO-specific access wrappers.
- Linux PCI/PCIe, MSI/MSI-X, SR-IOV, AER, ARI, link management, and error-recovery semantics.
- Firmware and platform policy that initially strap or expose VF capabilities, BARs, interrupt capability, link width/speed support, equalization behavior, SRIS mode, and retimer presence.

Important integration surfaces are SR-IOV VF enumeration and reset paths, VF interrupt setup, PCIe AER diagnostics and recovery, link bring-up/retrain paths, ASPM/LTR/power-management policy, PCIe speed-change and equalization code, error-injection diagnostics, and hardware validation tools that inspect generated NBIO register fields.

## Risks and Edge Cases

- The range starts mid-`VF13_0_PCIE_UNCORR_ERR_STATUS` and ends mid-file after `PCIE_LC_CNTL6`; adjacent chunks are needed for complete register-group coverage at both boundaries.
- Generated hardware contract drift is the main risk. A wrong mask or shift can silently program a different field while all C code still compiles.
- VF14 and VF15 are highly repetitive. A copied field with the wrong VF prefix, missing field, or different mask is easy to miss and can affect only one virtual function.
- AER status, mask, and severity groups use nearly identical field names. Mixing them can hide errors, misclassify errors, or clear/inspect the wrong diagnostic bit.
- MSI and MSI-X fields contain encoded address/table/PBA bits and aliasing layout variants. Treating every field as an independent plain address can corrupt vector setup.
- PCI BAR, ROM BAR, and MSI-X table/PBA fields carry type, enable, BIR, and reserved low-bit encodings. Consumers must preserve and interpret those bits according to PCI layout.
- Receiver ignore bits and AER private masks can suppress hardware diagnostics. Setting them to work around one condition can hide real data-link, transaction-layer, PASID, prefix, or timeout failures.
- Error-injection fields should be used only in controlled diagnostic paths. Accidental writes can create artificial physical or transaction-layer failures.
- Link controller fields are timing-sensitive. Incorrect masks for retrain, link disable, directed speed change, width renegotiation, equalization, SRIS, or retimer override fields can cause intermittent link training failures, speed fallback, loss of device reachability, or recovery loops.
- LTSSM/debug state masks are observability aids, not stable software state. Tests should tolerate hardware-updated state changing during reads.
- Literal masks use `L` suffixes and vary across 8-bit, 16-bit, and 32-bit register layouts. Callers should avoid signedness or truncation assumptions.

## Test Signals

Useful validation signals for this chunk are mostly generated-header checks, build coverage, and PCIe hardware behavior:

- Build AMDGPU configurations that include the NBIO 4.3.0 register headers; malformed macro names, missing generated pairs, or include-order breakage should surface at compile time.
- Run generated-header consistency checks: each field should usually have a matching `__SHIFT` and `_MASK`, masks should align with the shift and width, and VF14/VF15 matching suffixes should carry the same numeric values.
- Compare representative fields against `nbio_4_3_0_offset.h`, any matching defaults file, and the source hardware register database, especially chunk-boundary VF13 fields, VF14/VF15 AER/MSI/MSI-X fields, and `PCIE_LC_*` link-control masks.
- Enable enough SR-IOV VFs to exercise VF14 and VF15, enumerate them, bind/unbind guest or host drivers, run VF FLR, and verify config-space fields decode as expected.
- Exercise MSI/MSI-X on VF14/VF15: program vectors, mask/unmask, verify pending bits, and confirm interrupts are delivered and quiesced correctly.
- Use PCIe AER injection or observed error paths to verify correctable and uncorrectable status/mask/severity fields, header logs, and prefix logs decode without disturbing unrelated bits.
- Exercise link retrain, directed speed change, ASPM/L1 paths, equalization, width negotiation, and retimer/SRIS configurations on hardware using this NBIO version. Symptoms of mask drift include speed/width mismatches, equalization phase failures, repeated retraining, link-down recovery loops, or unexpected LTSSM states.
- Validate receiver policy and completion-timeout behavior by checking that expected errors are reported or masked only when the corresponding policy bits are intentionally configured.
- Run controlled error-injection diagnostics for `PCIEP_ERROR_INJECT_PHYSICAL` and `PCIEP_ERROR_INJECT_TRANSACTION`, confirming injected failures are attributable and reversible.

### subset-b-002974: lines 31978-34356

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 31978-34356

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: register-field `__SHIFT` and `_MASK` macros for PCIe/NBIO register words. There are no C functions, structs, enums, branches, loops, locks, allocations, MMIO accesses, or persistence operations in this range.

The range starts in the tail of `PCIE_LC_CNTL6`, then covers `PCIE_LC_CNTL7`, PCIe strap controls, L1 PM substate controls, link-control and equalization controls, transmit/data-link credit controls, a `nbio_pcie0_pciedir` address block, PCIe RX/config/status/PM/performance/strap/PRBS registers, software reset and clock/power-management control registers, SMN aperture IDs, lane-count and interrupt-pin-sharing indicators, RX margining controls, TX last-TLP/tracking/status/attribute controls, HIP aperture registers, SMU fenced policy bits, and the beginning of `PCIE_PERF_CNTL_TXCLK10`.

Both boundaries are artificial. The first visible lines are only the final `PCIE_LC_CNTL6` masks for retimer presence handling, and the last visible line is the first `PCIE_PERF_CNTL_TXCLK10__EVENT0_SEL__SHIFT` definition without that register's remaining fields. Adjacent chunks must be merged before making whole-register claims for those boundary groups.

Although the repository path is under a local `ceph-client` mirror, this source is AMDGPU hardware metadata. It describes GPU PCIe/NBIO register bit layout, not Ceph or distributed filesystem logic.

## Purpose

The purpose of this header section is to publish bit positions and masks for NBIO 4.3.0 PCIe link-management, power-management, transmit/receive, flow-control, diagnostic, reset, aperture, and performance-counter registers. Matching address macros live in `nbio_4_3_0_offset.h`; this file defines how software extracts or updates individual fields after selecting the correct register address.

Driver code consumes these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and related SOC15/NBIO access wrappers. The macros form a hardware ABI. A wrong mask or shift can compile cleanly while programming the wrong bit in a PCIe control register, misreading a status bit, or corrupting adjacent fields during read/modify/write.

The chunk's main functional surfaces are:

- PCIe link controller behavior: training, ESM/retimer handling, scheduled RX equalization, lane reversal, link management, and link state/status controls.
- Strap-derived PCIe configuration: lane negotiation, compliance behavior, retimer presence-detect support, CCIX/LTR/OBFF capability, ESM support, and I2C board strap data.
- L1 PM substates and save/restore timing: ASPM/PCI-PM L1.1/L1.2 overrides, CLKREQ filtering, power-on timers, LTR thresholds, FCH target addressing, save/restore write-enable and register-data fields.
- Transmit/data-link controls: replay buffer behavior, ACK latency, advertised/init credits, flow-control credit limits, No-Op DLLP handling, request-number controls, and credit-status visibility.
- PCIe direct-register block diagnostics: RX NAK counters, config controls, AER masking, bus/CI controls, link-controller states/status, write-protection, last received and transmitted TLP logging, I2C register access, PM controls, SDP controls, and performance-counter selectors/counts.
- PRBS, RX margining, reset, clock/power management, SMN aperture, page-gating, HIP aperture, SMU policy, TX tracking, and TX attribute override fields.

## Important Macro Families

### Link Controller, Straps, And L1 PM

The chunk begins with the last `PCIE_LC_CNTL6` masks for retimer presence behavior: override, ignore, and retimer-presence bit fields. The next complete group, `PCIE_LC_CNTL7`, exposes link-controller toggles for TS2 config completion expectations, robust training-bit checks, electrical-idle handling, NBIF ASPM input, reversal clearing/locking, forced RX equalization progress, scheduled RX equalization interval/mode/upconfig, link-management enablement, timeout auto-reject, and ESM PLL/init state bits.

`PCIEP_STRAP_LC`, `PSWUSP0_PCIEP_STRAP_MISC`, and `PCIEP_STRAP_LC2` describe strap-sourced configuration. These include FTS/TS count encodings, skip interval, receiver-detect bypass, compliance disable/force, lane reversal, auto root-complex speed negotiation disable bits for base, 16 GT/s, and 32 GT/s speeds, lane-negotiation width, software margining ownership, retimer presence-detect support, E2E prefix support, extended format support, OBFF/LTR support, CCIX enablement, and ESM mode/reach/recalibration/timing/quick-equalization timeout capability.

`PCIE_LC_L1_PM_SUBSTATE` through `PCIE_LC_L1_PM_SUBSTATE5` define the L1 substate and save/restore timing surface. The fields cover L1 substate override enablement, PCI-PM and ASPM L1.1/L1.2 override bits, CLKREQ filtering, `T_POWER_ON` scale/value, FCH copy enable/trigger, L1.2 exit blocking, L1.1/L1.2 powerdown encodings, deferred L1.2 exit handling, wake/abort controls, AUX counter increment sources, common-mode restore time, LTR threshold scale/value, FCH target address, L1.2 powerdown delay and LTR-latency fields. These definitions are used around link power-management programming, where preserving unrelated bits during read/modify/write is critical.

### Link Equalization, Clock Gating, Save/Restore, And Speed Controls

`PCIEP_BCH_ECC_CNTL` exposes ECC enable, correction-disable, debug, and syndrome-related fields for the PCIe BCH path.

`PCIE_LC_CNTL8`, `PCIE_LC_CNTL9`, `PCIE_LC_CNTL10`, `PCIE_LC_CNTL11`, and `PCIE_LC_CNTL12` add more link-controller behavior: linkwidth overrun controls, periodic TS/FTS count controls, received-FTS thresholds, lane reversal/cropping controls, target link speed, persistent reset behavior, ASPM L1 entry/exit delays, RX electric-idle detection, retimer and upconfig behavior, EQ-related options, lane reversal request controls, PCIe generation transition controls, and ESM-related knobs.

`PCIE_LC_FORCE_COEFF2`, `PCIE_LC_FORCE_EQ_REQ_COEFF2`, `PCIE_LC_FORCE_COEFF3`, and `PCIE_LC_FORCE_EQ_REQ_COEFF3` publish coefficient override and equalization-request fields. They are highly timing-sensitive: callers must understand the PCIe equalization flow before forcing coefficient or request values.

`PCIE_LC_FINE_GRAIN_CLK_GATE_OVERRIDES` defines per-subblock clock-gating override bits for the link controller. `PCIE_LC_SAVE_RESTORE_1` and `PCIE_LC_SAVE_RESTORE_2` describe register address, data, write-enable, and port fields for save/restore flows. `PCIE_LC_SPEED_CNTL2` contains speed-change and reserved control fields used around link speed management.

### TX, Replay, Credits, And Flow Control

`PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, `PCIE_TX_ACK_LATENCY_LIMIT`, `PCIE_TX_CREDITS_FCU_THRESHOLD`, `PCIE_TX_VENDOR_SPECIFIC`, `PCIE_TX_NOP_DLLP`, and `PCIE_TX_REQUEST_NUM_CNTL` define transmit and data-link layer policy. They cover sequence/replay behavior, ACK latency bounds, FC update thresholds, vendor-specific message fields, No-Op DLLP generation, and requester/request-number control.

`PCIE_TX_CREDITS_ADVT_P`, `PCIE_TX_CREDITS_ADVT_NP`, and `PCIE_TX_CREDITS_ADVT_CPL` define advertised posted, non-posted, and completion header/data credits. `PCIE_TX_CREDITS_INIT_P`, `PCIE_TX_CREDITS_INIT_NP`, and `PCIE_TX_CREDITS_INIT_CPL` define initial credit values. `PCIE_TX_CREDITS_STATUS` exposes selected credit status and update behavior.

`PCIE_FC_P`, `PCIE_FC_NP`, `PCIE_FC_CPL`, and their `VC1` variants expose flow-control limit/receive fields for posted, non-posted, and completion traffic classes. These fields are central to PCIe data-link correctness. Misprogramming credit masks can manifest as stalls, replay storms, or traffic-class-specific failures rather than a simple boot-time error.

### PCIe Direct Address Block

The `addressBlock: nbio_pcie0_pciedir` marker starts a direct PCIe register namespace. The early groups include:

- `PCIE_RESERVED` and `PCIE_SCRATCH` fields for reserved/debug scratch state.
- `PCIE_RX_NUM_NAK` and `PCIE_RX_NUM_NAK_GENERATED` counters for received and generated NAK diagnostics.
- `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, `PCIE_CNTL2`, `PCIE_CFG_CNTL`, `PCIE_CI_CNTL`, and `PCIE_BUS_CNTL` fields for global PCIe, configuration, client-interface, and bus behavior.
- `PCIE_RX_CNTL5`, `PCIE_RX_CNTL4`, `PCIE_RX_CNTL2`, `PCIE_RX_AD`, and `PCIE_COMMON_AER_MASK` fields for RX behavior and common AER masking.
- `PCIE_LC_STATE6` through `PCIE_LC_STATE11`, `PCIE_LC_STATUS1`, and `PCIE_LC_STATUS2` fields for link-controller internal state and status visibility.
- `PCIE_WPR_CNTL` and `PCIE_RX_LAST_TLP0` through `PCIE_RX_LAST_TLP3` fields for write-protection control and last-received-TLP capture.

`PCIE_I2C_REG_ADDR_EXPAND` and `PCIE_I2C_REG_DATA` define address/data fields for an I2C-style register access path. `PCIE_LC_PM_CNTL` and `PCIE_LC_PM_CNTL2` define link power-management control. `PCIE_P_CNTL`, `PCIE_P_BUF_STATUS`, `PCIE_P_DECODER_STATUS`, `PCIE_P_MISC_STATUS`, and `PCIE_P_RCV_L0S_FTS_DET` describe protocol/parser buffer, decoder, miscellaneous, and L0s FTS detection state. `PCIE_SDP_CTRL`, `PCIE_SDP_SWUS_SLV_ATTR_CTRL`, and `PCIE_SDP_CTRL2` describe SDP path control and slave attribute overrides.

### Performance Counters, Straps, And PRBS Diagnostics

`PCIE_PERF_COUNT_CNTL` controls performance counting. `PCIE_PERF_CNTL_TXCLK1` through `PCIE_PERF_CNTL_TXCLK6` and `PCIE_PERF_CNTL_TXCLK7` through `PCIE_PERF_CNTL_TXCLK9` define event selectors and full flags for two counters per TX clock domain group. Matching `PCIE_PERF_COUNT0_TXCLK*` and `PCIE_PERF_COUNT1_TXCLK*` macros expose full-width counter values. The chunk ends as `PCIE_PERF_CNTL_TXCLK10` begins, so that register's full field list is in the next chunk.

`PCIE_PERF_CNTL_EVENT_LC_PORT_SEL` and `PCIE_PERF_CNTL_EVENT_CI_PORT_SEL` select link-controller and client-interface event ports. `PCIE_STRAP_F0`, `PCIE_STRAP_MISC`, `PCIE_STRAP_MISC2`, `PCIE_STRAP_PI`, and `PCIE_STRAP_I2C_BD` expose additional strap-derived feature and board-data fields.

`PCIE_PRBS_CLR`, `PCIE_PRBS_STATUS1`, `PCIE_PRBS_STATUS2`, `PCIE_PRBS_FREERUN`, `PCIE_PRBS_MISC`, `PCIE_PRBS_USER_PATTERN`, `PCIE_PRBS_LO_BITCNT`, `PCIE_PRBS_HI_BITCNT`, and `PCIE_PRBS_ERRCNT_0` through `PCIE_PRBS_ERRCNT_15` define pseudo-random bit sequence test controls, bit counters, and lane-specific error counters. These are hardware validation and signal-integrity diagnostics rather than normal data-path policy.

### Reset, Clock/Power Management, Apertures, And Margining

`SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0`, `SWRST_COMMAND_1`, `SWRST_CONTROL_0` through `SWRST_CONTROL_6`, `SWRST_EP_COMMAND_0`, and `SWRST_EP_CONTROL_0` define software-reset command, status, and endpoint reset-control fields. The macros expose bit locations only; reset sequencing, polling, and dependency ordering are handled by executable driver code outside this header.

`CPM_CONTROL`, `CPM_SPLIT_CONTROL`, and `CPM_CONTROL_EXT` describe clock/power-management controls. `SMN_APERTURE_ID_A` and `SMN_APERTURE_ID_B` expose SMN aperture identifiers. `LNCNT_CONTROL` exposes lane-count control fields. `SMU_INT_PIN_SHARING_PORT_INDICATOR` and `SMU_INT_PIN_SHARING_PORT_INDICATOR_TWO` expose port-indicator bits used for SMU interrupt pin-sharing state. `PCIE_PGMST_CNTL` and `PCIE_PGSLV_CNTL` define master/slave page-gating controls, while `LC_CPM_CONTROL_0` and `LC_CPM_CONTROL_1` define link-controller CPM fields.

`PCIE_RXMARGIN_CONTROL_CAPABILITIES`, `PCIE_RXMARGIN_1_SETTINGS`, and `PCIE_RXMARGIN_2_SETTINGS` define receiver-margining capabilities and settings. These fields are relevant to PCIe signal margin diagnostics and must be interpreted with the hardware and PCIe margining protocol.

### TX Logging, Tracking, Status, Attributes, HIP, And SMU Fenced Bits

`PCIE_TX_LAST_TLP0` through `PCIE_TX_LAST_TLP3` capture the last transmitted TLP words. `PCIE_TX_TRACKING_ADDR_LO`, `PCIE_TX_TRACKING_ADDR_HI`, and `PCIE_TX_TRACKING_CTRL_STATUS` define address, enable, port, unit ID, and status-valid fields for TX tracking. `PCIE_TX_CTRL_4` adds a TX port access timer skew field.

`PCIE_TX_STATUS` exposes memory-ready, CI idle, pending-read, write-response, TX idle, clock-request idle, header/data FIFO empty, and no-free-credit status bits. `PCIE_TX_F0_ATTR_CNTL` and `PCIE_TX_SWUS_ATTR_CNTL` provide IDO, relaxed-ordering, and no-snoop override fields for posted, non-posted, and completion traffic. `PCIE_MST_CTRL_1` describes master posted-data/header credit advertisements, override enables, pending-reset behavior, and idle hysteresis.

`PCIE_HIP_REG0` through `PCIE_HIP_REG8` define host-interface aperture base, limit, enable, PASID mode, ReqAT mode, ReqIO mode, and mask fields for two apertures. `SMU_PCIE_FENCED1_REG` and `SMU_PCIE_FENCED2_REG` expose one-bit SMU-fenced policy toggles for CrossFire lockdown and overclocking enablement.

## Important APIs, Types, And Functions

This chunk defines no APIs, C types, or functions by itself. Its externally visible interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask at its already-shifted position.
- Register names correspond to address macros in `nbio_4_3_0_offset.h`, usually named `reg<REGISTER>` or a closely related generated address symbol.

The practical API boundary is the AMDGPU register helper layer. Typical consumers read a register, clear a mask, set a value shifted by the corresponding `__SHIFT`, and write the register back. For single-bit fields, code commonly ORs or ANDs the `_MASK` directly. For example, `amdgpu/nbio_v4_3.c` includes this header and uses `PCIE_LC_CNTL7__LC_NBIF_ASPM_INPUT_EN_MASK` with `regPCIE_LC_CNTL7` in `nbio_v4_3_program_aspm()`.

## Control Flow

There is no executable control flow in this header. Runtime control flow is supplied by driver code that includes the generated NBIO 4.3.0 headers:

1. The driver selects an ASIC/IP-specific register address from `nbio_4_3_0_offset.h`.
2. It selects one or more field definitions from this `nbio_4_3_0_sh_mask.h` file.
3. It reads or writes through SOC15/NBIO/PCIe helper functions.
4. For field updates, it performs read/modify/write using masks and shifts so unrelated fields are preserved.
5. Hardware applies the update to link training, ASPM/L1 substate behavior, credit flow, reset, diagnostics, margining, performance counting, or aperture policy.

One concrete in-tree flow is `nbio_v4_3_program_aspm()`: it reads `regPCIE_LC_CNTL7`, sets `PCIE_LC_CNTL7__LC_NBIF_ASPM_INPUT_EN_MASK`, and writes the register back if the value changed. Other fields in this chunk may be used by board bring-up, debug, validation, power management, or generated-register coverage even when not referenced explicitly in the visible C files.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It describes hardware-backed state whose lifetime is controlled by GPU reset type, PCIe link resets, firmware/BIOS initialization, driver programming, power-state transitions, link retraining, diagnostic commands, and SMU policy.

The represented hardware state includes:

- Sticky or live PCIe link-controller control/status fields for training, equalization, speed control, ESM, retimers, lane reversal, and link-management state.
- Strap-derived configuration that may be sampled from fuses/straps or firmware-configured defaults and may not be freely writable at runtime.
- L1 PM substate controls, timings, LTR thresholds, save/restore register-data fields, and powerdown delay state.
- TX sequence, replay, ACK latency, advertised/init credits, flow-control limits, request numbering, and credit-status state.
- RX/CI/bus/config status, NAK counters, last-TLP capture words, AER masking, and performance counter state.
- PRBS test control, bit counters, and lane-specific error counters.
- Software-reset command/status state and page-gating or clock/power-management controls.
- SMN aperture IDs, HIP aperture base/limit/mode fields, and SMU-fenced policy bits.

Some fields are stable configuration until reset or reprogramming, such as ASPM input enable, L1 substate overrides, credit advertisements, strap-derived feature bits, aperture base/limit registers, and attribute override controls. Other fields are live status, counters, latched diagnostics, command triggers, or hardware-updated logs. The macro names do not encode access semantics such as read-only, write-one-clear, self-clearing, sticky, strap-only, or reset-only; callers must rely on AMD's register database, PCIe semantics, and existing AMDGPU programming sequences.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the matching register addresses and base indices.
- Other generated NBIO 4.3.0 headers such as defaults or SMN definitions where present.
- AMDGPU helper conventions for `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, PCIe indirect/direct access, and SOC15 IP block selection.
- PCIe architectural semantics for link training, ASPM, L1 substates, flow-control credits, AER, PRBS, receiver margining, and reset behavior.

Direct in-tree include points for `nbio_4_3_0_sh_mask.h` include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which programs NBIO 4.3 behavior and directly uses the `PCIE_LC_CNTL7` ASPM-input field from this chunk.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, which include the NBIO 4.3.0 offsets and masks for SMU13 power-management register access.

The related offset header is also included by DCN 3.2 resource code. Those display paths need register addresses, while field-level use in this chunk is mainly visible in NBIO and SMU code.

## Risks And Edge Cases

- Generated hardware contract drift is the main risk. A stale shift or mask can compile but update the wrong hardware bit or silently decode a status field incorrectly.
- The chunk starts and ends mid-register-family. `PCIE_LC_CNTL6` and `PCIE_PERF_CNTL_TXCLK10` require adjacent chunks for complete documentation.
- Many fields are timing-sensitive. Link training, equalization, ESM, retimer, L1.2, CLKREQ, and speed-change bits can create intermittent link failures rather than immediate deterministic failures.
- Strap fields may be read-only, sampled at reset, or firmware-owned. Treating all strap masks as ordinary writable state can produce misleading tests or ineffective writes.
- L1 PM substate and LTR fields interact with platform PCIe ASPM policy, endpoint capability, root-port behavior, and SMU power management. Incorrect masks can cause resume failures, latency regressions, link drops, or excess power draw.
- TX credit and flow-control fields are tightly coupled. Bad masks can corrupt posted/non-posted/completion accounting and appear as stalls, replays, NAK storms, or throughput drops.
- Counter, last-TLP, PRBS, and margining fields may be self-clearing, latch-on-read, command-triggered, or lane-specific. Generic read/modify/write can lose diagnostics if the access semantics are ignored.
- Reset and page-gating controls can affect multiple subblocks. Wrong field definitions or sequencing can leave the device partially reset, clock-gated during access, or unable to complete later register transactions.
- HIP and SMN aperture fields encode address windows and request modes. Incorrect base/limit or mode masks can redirect access, break PASID/ReqAT/ReqIO behavior, or expose isolation issues.
- SMU fenced bits are policy-sensitive. Overclocking or CrossFire lockdown fields should be interpreted with SMU ownership and platform policy rather than as unconditional driver toggles.

## Test Signals

Useful validation signals for this chunk are a mix of generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU configurations that include `nbio_v4_3.c` and SMU13 PPT files. Missing or renamed macros in this chunk should surface as compile failures.
- Run generated-header consistency checks: for each register field, verify that masks align with shifts, multi-bit masks are contiguous where expected, single-bit masks match `1 << shift`, and repeated counter/lane/performance blocks follow the expected pattern.
- Compare `nbio_4_3_0_sh_mask.h` against `nbio_4_3_0_offset.h` and AMD's source register database, especially `PCIE_LC_CNTL7`, L1 PM substate groups, TX credit groups, PRBS counters, HIP registers, SMU fenced registers, and boundary groups.
- Exercise `nbio_v4_3_program_aspm()` on supported hardware and check that ASPM/LTR behavior, link stability, suspend/resume, and power measurements remain sane.
- Validate PCIe link speed changes, retraining, equalization, retimer paths, and L1.1/L1.2 entry/exit around the fields in the link-controller and PM-substate groups.
- Use PCIe error and performance diagnostics where available: NAK counters, last-TLP logs, TX status bits, flow-control counters, and AER masks should behave without unrelated bit corruption.
- Run PRBS and RX margining diagnostics across all lanes; lane-specific error counters and margin settings should map to the intended lane and not cross-affect adjacent counters.
- Exercise software reset and page-gating paths under runtime suspend/resume or recovery scenarios; incomplete reset status, hung register reads, or clock-gating deadlocks are strong signals of field drift.
- Validate HIP/SMN aperture programming only through approved platform flows; wrong address-window decoding or request-mode behavior points to aperture mask or shift mistakes.

### subset-b-002975: lines 34357-36823

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 34357-36823

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It defines C preprocessor constants for bit positions and bit masks in several NBIO/PCIe configuration decode blocks. The range begins at the tail of the PCIe performance counter definitions for `TXCLK10`, then covers:

- `nbio_pcie0_pswuscfg0_cfgdecp`, with upstream-switch/bridge configuration fields prefixed `PSWUSCFG0_*`.
- `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, with root-complex bridge and slot capability/control/status fields.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, with endpoint PF0 PCI configuration space and PCIe extended capability fields.
- The beginning of `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, with virtual-function 0 PCI configuration and early PCIe capability fields.

The chunk is declarative only. It contains no functions, structs, enums, executable control flow, allocations, locking, initialization routines, or direct register access. Its interface is the macro namespace consumed by AMDGPU code and generated register helpers.

## Purpose

The macros give symbolic layouts for NBIO 4.3.0 PCIe/NBIF registers so driver code can decode or compose register values without open-coded bit constants. Each register field generally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The companion offset header, `nbio_4_3_0_offset.h`, provides addresses and base indices. This file provides field extraction and update metadata used by register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/PCIE read-modify-write paths.

This range is concentrated around PCIe configuration exposure: bus numbering, bridge windows, standard PCI command/status, BARs, power management, MSI/MSI-X, PCIe device/link controls, AER, resizable BAR, DPA, ACS, PASID, SR-IOV, link equalization, lane margining, and high-speed link capability status up to 32 GT/s.

## Address Blocks and Register Coverage

The first few lines complete PCIe performance counter macros:

- `PCIE_PERF_CNTL_TXCLK10` selects two performance events and exposes counter-full status bits.
- `PCIE_PERF_COUNT0_TXCLK10` and `PCIE_PERF_COUNT1_TXCLK10` expose full 32-bit counter values.

`nbio_pcie0_pswuscfg0_cfgdecp` covers a PCI-to-PCI bridge style configuration block:

- `PSWUSCFG0_SUB_BUS_NUMBER_LATENCY` fields for primary, secondary, subordinate bus numbers, and secondary latency timer.
- `PSWUSCFG0_IO_BASE_LIMIT`, `PSWUSCFG0_MEM_BASE_LIMIT`, and `PSWUSCFG0_PREF_BASE_LIMIT` fields for bridge I/O, memory, and prefetchable memory windows.
- Upper 32-bit prefetchable base/limit and high I/O base/limit fields.
- `PSWUSCFG0_SECONDARY_STATUS` error and status bits.
- SSID capability list and subsystem vendor/device identity fields.

`nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` mirrors bridge/root-complex configuration:

- `BIF_CFG_DEV0_RC_SUB_BUS_NUMBER_LATENCY`, I/O base/limit, memory base/limit, prefetchable base/limit, upper base/limit, and high I/O base/limit.
- PCIe slot capability, control, and status registers, including hotplug, attention/power indicators, presence detect, MRL sensor, power fault, command-completed interrupt, electromechanical interlock, and physical slot number fields.
- Slot capability/control/status version 2 placeholder or reserved fields.
- Root-complex SSID capability list and subsystem ID fields.

`nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` is the dominant part of the chunk. It covers PF0 config-space and extended capability fields:

- Basic PCI header: vendor/device IDs, command, status, revision, programming interface, class/subclass, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and writeable adapter ID.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, including PME support/status, power state, data select/scale, B2/B3 support, and bus power enable.
- PCIe base capability: `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X: MSI control, 32-bit and 64-bit message address/data layout, extended message data, mask and pending bits, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability and virtual-channel capability/resource fields.
- Device serial number fields.
- PCIe Advanced Error Reporting: uncorrectable error status, mask, severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- Resizable BAR controls for BAR1 through BAR6.
- Power budget and Dynamic Power Allocation capability/control/status/substate allocation registers.
- Secondary PCIe extended capability, link control 3, lane error status, and per-lane 8 GT/s equalization controls for lanes 0 through 15.
- Access Control Services capability/control.
- PASID capability/control.
- Multicast capability/control/address/receive/block registers.
- Latency Tolerance Reporting capability.
- ARI capability/control.
- SR-IOV capability/control/status and VF resource fields.
- Data Link Feature capability/status.
- PHY 16 GT/s capability/control/status, parity mismatch status, and per-lane 16 GT/s equalization control for lanes 0 through 15.
- PCIe lane margining capability plus per-lane margining control/status for lanes 0 through 15.
- VF resizable BAR capability/control for BAR1 through BAR6.
- 32 GT/s link capability/control/status.

`nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` begins near the end of the range:

- VF0 basic PCI header fields from vendor/device IDs through max latency.
- VF0 PCIe capability list, `PCIE_CAP`, device capability/control/status, link capability/control/status.
- The first line of `BIF_CFG_DEV0_EPF0_VF0_DEVICE_CAP2` starts at the chunk boundary, so the VF0 PCIe capability block is incomplete in this chunk.

## Important APIs, Types, and Functions

There are no C functions, types, or callable APIs in this chunk. The significant interface is the generated macro set. Important macro families include:

- `*_COMMAND__*` and `*_STATUS__*` for PCI enablement and reporting bits: I/O access, memory access, bus master, special cycles, parity response, SERR, fast back-to-back, interrupt disable, capability list presence, abort reporting, parity error, and detected parity.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR`, `*_PCIE_BAR*_CAP`, and `*_PCIE_BAR*_CNTL` for BAR layout, ROM enablement, resizable BAR supported sizes, selected size, BAR index, and total BAR count.
- `*_SUB_BUS_NUMBER_LATENCY`, `*_IO_BASE_LIMIT*`, `*_MEM_BASE_LIMIT`, and `*_PREF_BASE_LIMIT*` for bridge bus numbering and decode windows.
- `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` for hotplug and slot events. These fields are particularly relevant to bridge/root-complex behavior.
- `*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` for payload size, read request size, relaxed ordering, no-snoop, auxiliary power, FLR, completion timeout, LTR enable, emergency power reduction, atomic operations, ID-based ordering, 10-bit tags, and error reporting.
- `*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` for supported/current link speed, link width, ASPM, retraining, link disable, common clock, clock power management, autonomous bandwidth, DRS, equalization state, and high-speed link features.
- `*_MSI_*` and `*_MSIX_*` for interrupt delivery programming and masking.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, `*_PCIE_ADV_ERR_CAP_CNTL`, `*_PCIE_HDR_LOG*`, and `*_PCIE_TLP_PREFIX_LOG*` for PCIe AER status, mask, severity, ECRC, first-error pointer, multi-header recording, and diagnostic captured TLP data.
- `*_PCIE_DPA_*`, `*_PCIE_PWR_BUDGET_*`, and `*_PCIE_LTR_*` for PCIe power-management reporting and latency tolerance contracts.
- `*_PCIE_ACS_*`, `*_PCIE_PASID_*`, `*_PCIE_ARI_*`, and `*_PCIE_SRIOV_*` for isolation, address-space IDs, alternate routing-ID interpretation, and virtualization resources.
- `*_PCIE_LANE_*_EQUALIZATION_CNTL`, `*_LANE_*_MARGINING_LANE_CNTL`, and `*_LANE_*_MARGINING_LANE_STATUS` for per-lane signal integrity tuning and diagnostics.
- `*_LINK_CAP_32GT`, `*_LINK_CNTL_32GT`, and `*_LINK_STATUS_32GT` for PCIe 5.0 class 32 GT/s equalization and modified training-sequence behavior.

## Control Flow

This header range has no runtime control flow. Inclusion is controlled by the file-level header guard defined near the start of `nbio_4_3_0_sh_mask.h`.

The expected consumer flow is inferred from AMDGPU generated register conventions:

1. Include `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`.
2. Select a register address from the offset header, for example a `cfgBIF_CFG_DEV0_EPF0_*` or related NBIO address.
3. Read the register through the appropriate AMDGPU access path, such as SOC15/NBIO helpers, PCIE config access, or firmware/SMU code that includes these headers.
4. Extract a field with the `*_MASK` and `*_SHIFT` constants, or compose a new register value with the same constants.
5. Write the new value only when the target field is a writable control bit and surrounding bits have been preserved.

The range is used as a compile-time description of hardware layout. Any behavioral sequencing, delays, reset ordering, PCI enumeration, SR-IOV provisioning, interrupt setup, or error recovery is implemented elsewhere.

## State and Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware state held in NBIO and PCIe configuration registers.

Several fields represent long-lived configuration state until reset, function-level reset, or PCI reconfiguration:

- Bridge bus numbers and decode windows.
- `COMMAND` control bits such as memory access, I/O access, bus mastering, SERR enable, and interrupt disable.
- BAR/ROM mappings and resizable BAR size selections.
- Power management control bits such as power state, PME enable/status, LTR enable, DPA substate control, and power budget selection.
- MSI/MSI-X enablement, MSI address/data fields, mask bits, and MSI-X table/PBA descriptors.
- PCIe device/link controls such as maximum payload/read request, relaxed ordering, no-snoop, completion timeout, FLR initiate, link retrain/disable, autonomous speed/width controls, and equalization controls.
- AER masks/severity and ECRC generation/checking enables.
- ACS/PASID/ARI/SR-IOV controls, including VF enablement, VF migration, memory-space enablement, VF BARs, and system page size.

Other fields are status or diagnostics updated by hardware and sometimes sticky or write-one-to-clear according to PCIe semantics:

- PCI status, secondary status, slot status, device status, and link status.
- AER correctable and uncorrectable status, first-error pointer, header logs, and prefix logs.
- Lane error status, 8 GT/s/16 GT/s/32 GT/s equalization status, parity mismatch status, DRS messages, and margining lane status.
- MSI pending bits and PME status.

Because the macros do not encode access permissions, consumers must know from the PCIe specification and hardware register database whether a field is read-only, read/write, clear-on-write, sticky, reserved, or hardware-updated.

## Dependencies and Integration Points

This chunk depends conceptually on nearby generated register headers:

- `nbio_4_3_0_offset.h` supplies addresses and base indices for the registers whose fields are described here.
- `nbio_4_3_0_default.h`, when present for the same register database, supplies default/reset values used for comparison or initialization.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` naming convention for field extraction and read-modify-write updates.

Direct include integration found in this tree includes SMU 13 code paths, such as `smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include both `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`. The field names also align with broader AMDGPU NBIO/PCIe handling used by NBIO, power-management, RAS, PCIe, and virtualization code.

Subsystem integration points include:

- Linux PCI and PCIe enumeration/configuration for command/status, bridge windows, capabilities, BARs, link controls, slot state, AER, MSI/MSI-X, ACS, PASID, ARI, and SR-IOV.
- AMDGPU power-management and SMU code that needs NBIO/PCIe capability fields, LTR, DPA, power budget, or BACO-adjacent PCIe state.
- AMDGPU RAS and PCIe recovery code through AER status/mask/severity and TLP log fields.
- IOMMU and process-address-space integration through PASID fields and ATS/PASID-adjacent PCIe capability policy.
- SR-IOV PF/VF orchestration through PF0 SR-IOV controls and the VF0 configuration-space window started at the end of the chunk.
- Hardware validation and debug tooling through per-lane equalization, margining, lane error, and high-speed link status fields.

## Risks and Edge Cases

- The header is generated and highly repetitive. A single incorrect shift or mask can make all downstream field extraction or read-modify-write logic wrong while still compiling.
- This chunk starts and ends at arbitrary boundaries. It begins mid `PCIE_PERF_CNTL_TXCLK10` and ends immediately after the first `BIF_CFG_DEV0_EPF0_VF0_DEVICE_CAP2` shift definition, so final reconciliation must not treat either boundary as a complete register family.
- Many fields have standard PCIe names but hardware-specific decode locations. Mixing macros from NBIO 4.3.0 with offsets from another NBIO generation can produce silent register corruption.
- Address-like fields such as BARs, ROM BARs, MSI-X table offsets, PBA offsets, bridge windows, and resizable BAR controls contain encoded low bits. Treating them as plain addresses can lose type, enable, BIR, or size metadata.
- Status, mask, and severity macros in the AER block have nearly identical names. Confusing these can clear the wrong status, suppress error reporting, or misclassify fatal and non-fatal errors.
- Some status bits may be sticky or clear-on-write while this header only exposes bit layout. Read-modify-write sequences that write back a stale status word can accidentally clear events.
- Link-control, compliance, retraining, autonomous speed/width, and equalization fields can affect PCIe reachability. Incorrect writes may trigger link retrains, force compliance behavior, or degrade width/speed.
- ACS, PASID, ARI, and SR-IOV controls interact with isolation and IOMMU policy. Enabling a field purely because the bit exists can break DMA translation, PCIe routing, VF enumeration, or peer-to-peer isolation.
- Per-lane equalization and margining fields repeat for lanes 0 through 15. Copy/paste or generation drift in one lane is hard to detect by manual review because the only expected textual difference is the lane number.
- Literal widths vary between byte, word, and dword registers, while masks use `L` suffixes. Consumers need correct access width and no implicit truncation.

## Test Signals

Useful validation signals for this chunk:

- Build AMDGPU code that includes `nbio_4_3_0_sh_mask.h`; malformed or missing macros should fail compile-time references.
- Run generated-register consistency checks comparing this range against the authoritative NBIO 4.3.0 register database and the matching `nbio_4_3_0_offset.h`.
- Pattern-check repeated families: BAR1 through BAR6, lane 0 through 15 equalization, lane 0 through 15 margining, VF resizable BAR1 through BAR6, and PF0 versus VF0 common PCIe capability fields.
- Verify bridge and slot fields against PCI config dumps from hardware using `lspci -vv` or driver debug output: bus numbers, bridge windows, slot capabilities, hotplug bits, and secondary status should decode as expected.
- Exercise PCIe capability decoding on supported NBIO 4.3.0 devices: payload/read request sizes, FLR, completion timeout, LTR, link width/speed, ASPM, DRS, 16 GT/s and 32 GT/s status.
- Test MSI and MSI-X enable, masking, pending, table, and PBA behavior during interrupt setup, teardown, suspend/resume, and reset.
- Use AER injection or observed hardware errors to validate uncorrectable/correctable status, mask, severity, first-error pointer, ECRC bits, header logs, and prefix logs.
- Validate SR-IOV lifecycle: enable VFs, enumerate VF0, program VF BARs, perform VF FLR, and confirm PF0 SR-IOV control/status fields return expected values after teardown.
- Validate ACS/PASID/ARI behavior in IOMMU-enabled configurations by checking device isolation, PASID width/enablement, and ARI function discovery.
- For hardware validation environments, use link equalization and margining diagnostics to confirm per-lane fields map to the expected physical lanes and do not drift across lane indices.

### subset-b-002976: lines 36824-39244

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 36824-39244

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It covers PCI/PCIe configuration-space field definitions for `BIF_CFG_DEV0_EPF0` SR-IOV virtual functions `VF0` through `VF3`.

The range starts inside the `VF0_DEVICE_CAP2` register: line 36823, just before the requested range, defines the `CPL_TIMEOUT_RANGE_SUPPORTED` shift, while line 36824 begins at `CPL_TIMEOUT_DIS_SUPPORTED`. It then completes the remainder of the `VF0` PCIe capability, MSI/MSI-X, vendor-specific, AER, TLP log, and ARI field families. `VF1` and `VF2` are complete logical VF blocks in this range. `VF3` begins at its PCI header fields and continues through the first masks of `PCIE_UNCORR_ERR_SEVERITY`; the rest of `VF3_PCIE_UNCORR_ERR_SEVERITY` and later `VF3` AER/ARI fields are outside this chunk.

The chunk is declarative only. It contains `#define` constants for field shifts and masks. It has no functions, structs, enums, runtime branches, allocation, locking, I/O calls, or initialization code.

## Purpose

The macros give symbolic names to NBIO 4.3.0 PCIe configuration register fields so AMDGPU and related generated-register helpers can read, decode, compose, and write hardware register values without open-coded bit positions.

The dominant naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>_MASK`

where `<n>` is `0`, `1`, `2`, or `3` in this chunk. The companion offset header maps register names to addresses; this `_sh_mask.h` file maps each register's fields to bit positions and bit masks.

## Register Coverage

The visible register-comment markers show 263 register blocks and 2149 macro definitions in the requested line range. Coverage is source-tree aligned to the requested header slice:

- Partial `VF0` PCIe capability tail: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- `VF0` MSI/MSI-X: MSI capability list, message control, low/high message address, data, extended data, mask, 64-bit data/mask variants, pending bits, MSI-X capability list, message control, table, and PBA location.
- `VF0` vendor-specific and AER tail: vendor-specific enhanced capability/header/scratch fields, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four header-log words, four TLP-prefix-log words, and ARI enhanced capability/capability/control.
- Complete `VF1` and `VF2` PCI configuration blocks: vendor/device ID, command/status, revision/interface/class fields, cache line/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, PCIe capability, device/link capability/control/status, second-generation PCIe capability/control/status, MSI/MSI-X, vendor-specific capability, AER, TLP logs, and ARI.
- Partial `VF3` block: basic PCI header fields, BARs, PCIe capability, device/link controls and status, MSI/MSI-X, vendor-specific capability, AER enhanced capability list, uncorrectable error status, uncorrectable error mask, and the shift fields plus first three masks of uncorrectable error severity.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The public interface is the generated macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` describe standard PCI control and status fields such as I/O access, memory access, bus mastering, SERR, interrupt disable, capability-list presence, abort status, parity error, and detected parity.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, and `*_MSIX_PBA__*` expose address-like fields where low bits encode memory type, prefetchability, enablement, BIR, or offset metadata.
- `*_PCIE_CAP*`, `*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` cover PCIe capability version/type, FLR, error reporting, payload size, read request size, relaxed ordering, no-snoop, completion timeout, atomic operations, ten-bit tags, OBFF, emergency power reduction, and TLP prefix support.
- `*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` describe supported/current link speeds, link width, ASPM/L1 behavior, link disable/retrain, common clocking, clock power management, bandwidth interrupts/status, equalization status, crosslink state, DRS support, and compliance controls.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability fields, including MSI enablement, multi-message capability/count, 64-bit MSI addressing, per-vector masking capability, message data, masks, pending bits, MSI-X function mask/enable, table size, table BIR/offset, and PBA BIR/offset.
- `*_PCIE_VENDOR_SPECIFIC*` exposes PCIe vendor-specific extended capability headers and two 32-bit scratch registers.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define AER status, reporting masks, severity classification, first-error pointer, ECRC generation/checking support and enables, multi-header recording, TLP prefix log presence, and completion-timeout log capability.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw diagnostic capture words for PCIe error analysis.
- `*_PCIE_ARI_*` defines Alternate Routing-ID capability and control fields: function-group capabilities, next function number, function-group enables, and function group value.

## Control Flow

This header chunk has no runtime control flow. Inclusion is governed by the enclosing header guard outside this slice, and all definitions become compile-time constants for translation units that include the generated NBIO 4.3.0 register headers.

Typical consumer flow is inferred from AMDGPU generated-register conventions:

1. Select a register address from the matching NBIO 4.3.0 offset header.
2. Read the register through PCI configuration, MMIO, or AMDGPU register access helpers.
3. Decode fields with `*_MASK` and `*_SHIFT`, often through `REG_GET_FIELD`-style helpers.
4. Compose writes with the matching field constants, often through `REG_SET_FIELD`-style helpers, when programming PCIe controls, interrupt delivery, AER policy, ARI behavior, or VF config-space state.

## State and Persistence Behavior

The file stores no software state and performs no persistence. It describes state held by hardware registers in NBIO/BIF PCI configuration decode space.

The represented state is per virtual function. Some fields model durable configuration until reset, function-level reset, guest reprogramming, or PF-mediated SR-IOV teardown: command bits, bus mastering, memory access, interrupt disable, payload/read-request sizing, completion-timeout controls, MSI/MSI-X enables and masks, MSI-X function mask, AER masks/severity settings, ECRC enablement, link-control fields, and ARI function-group controls.

Other fields are status or diagnostic capture: device/link status, link training/equalization indicators, MSI pending bits, correctable and uncorrectable AER status, first-error pointer, TLP header logs, and TLP prefix logs. Depending on the PCIe register model and NBIO implementation, these may be read-only, hardware-updated, sticky, write-one-to-clear, or reset by VF/PF lifecycle events.

Because this is SR-IOV VF config-space layout, practical ownership can be split between guest VF drivers, the host PF driver, firmware/hardware reset logic, and Linux PCI core policy. Consumers must preserve reserved bits and avoid treating status-like fields as normal writable storage.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_4_3_0_offset.h`, which provides concrete register offsets for the field names defined here.
- `nbio_4_3_0_default.h`, where generated reset/default values for related NBIO registers are normally stored.
- AMDGPU register helpers and generated-register naming conventions that expect matching `__SHIFT` and `_MASK` symbols.
- Linux PCI and PCIe subsystem concepts mirrored by the generated names: config header, PCIe capability, MSI, MSI-X, SR-IOV VFs, AER, ARI, link training, and power-management policy.
- SR-IOV PF/VF management paths that expose or virtualize these config-space fields for `VF0` through `VF3`.
- Interrupt setup and teardown paths that program MSI/MSI-X address/data/mask/pending/table/PBA state.
- PCIe diagnostics and recovery paths that inspect AER status, masks, severity, header logs, prefix logs, and link status after errors.

## Risks and Edge Cases

- The file is generated and highly repetitive. A wrong shift or mask can compile cleanly while causing incorrect hardware programming or misleading diagnostics.
- This chunk has two partial boundaries. It omits the first `VF0_DEVICE_CAP2` shift at line 36823 and stops in the middle of `VF3_PCIE_UNCORR_ERR_SEVERITY`; merge/reconciliation should not treat either boundary as a complete register family.
- `VF1` and `VF2` should be structurally identical except for the VF number. Copy-generation drift is hard to detect manually because most lines differ only by prefix.
- Status, mask, and severity AER registers use very similar names. Mixing them can clear, suppress, or misclassify PCIe errors.
- BAR, ROM BAR, MSI-X table, and MSI-X PBA fields include encoded low bits. Consumers must not treat every masked value as a plain byte address.
- Link-control and link-control-2 fields can disable links, force retraining, enter compliance modes, or alter autonomous speed/width behavior. Incorrect writes can make a function unreachable or unstable.
- MSI/MSI-X fields interact with Linux interrupt allocation and guest/host VF ownership. Stale mask, pending, or message data handling can lose interrupts or deliver them to the wrong vector.
- ARI fields affect PCIe routing and function discovery. Enabling function-group behavior without platform support can break VF enumeration or isolation assumptions.
- Masks use `L`-suffixed integer literals over 8-bit, 16-bit, and 32-bit fields. Callers should avoid signedness and truncation assumptions when composing values.
- Reserved fields such as `DEVICE_STATUS2__RESERVED` are named but should still be preserved according to the hardware specification.

## Test Signals

Useful validation signals for this chunk:

- Build coverage for AMDGPU code that includes `nbio_4_3_0_sh_mask.h`; malformed macro names or duplicate definitions should fail compilation.
- Generated-register consistency checks comparing this range with `nbio_4_3_0_offset.h`, `nbio_4_3_0_default.h`, and the upstream hardware register database.
- Pattern checks across complete `VF1` and `VF2` blocks to confirm identical field shifts and masks for the same register families; handle the partial `VF0` and `VF3` boundaries separately.
- SR-IOV runtime smoke tests with at least four enabled VFs: enumerate `VF0` through `VF3`, bind host/guest drivers, enable memory access and bus mastering, and verify config-space decoding.
- MSI/MSI-X tests for low-numbered VFs: allocate vectors, program message address/data, toggle vector/function masks, inspect pending state, and confirm interrupt delivery and quiescence.
- PCIe capability inspection through driver debug output or `lspci -vv` to validate payload size, read request size, FLR, link speed/width, MSI/MSI-X, AER, and ARI fields against hardware expectations.
- AER injection or observation tests to verify correctable and uncorrectable status, mask, severity, first-error pointer, TLP header logs, and TLP prefix logs decode correctly.
- Reset and lifecycle tests around VF FLR, PF driver reload, SR-IOV disable/re-enable, and guest detach/attach to confirm status/control fields return to expected defaults.

### subset-b-002977: lines 39245-41680

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 39245-41680

## Scope

This chunk covers generated shift and mask definitions for part of AMD NBIO 4.3.0 PCIe configuration-space register fields. The covered range starts in the tail of the `BIF_CFG_DEV0_EPF0_VF3` Advanced Error Reporting/ARI definitions, contains the full visible `BIF_CFG_DEV0_EPF0_VF4` virtual-function register field map, continues through `BIF_CFG_DEV0_EPF0_VF5` and `VF6` field groups, and ends at the beginning of `BIF_CFG_DEV0_EPF0_VF7_LINK_CAP`. The source is a pure C preprocessor header: it declares no functions, storage, structs, or executable control flow.

The file belongs to the AMDGPU driver register-description layer. It is included with `nbio/nbio_4_3_0_offset.h` by `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 PPT code, where address macros from the offset header are paired with field macros from this header for typed bit manipulation.

## Purpose

The purpose of this chunk is to provide stable symbolic names for bit positions and bit masks in SR-IOV virtual function PCI/PCIe configuration registers on NBIO 4.3.0 ASICs. The names encode:

- The target PCI config block, such as `BIF_CFG_DEV0_EPF0_VF4`.
- The register or capability dword/word, such as `DEVICE_CNTL`, `LINK_STATUS2`, `MSI_MSG_CNTL`, `PCIE_UNCORR_ERR_STATUS`, or `PCIE_ARI_CNTL`.
- The individual field, such as `MAX_PAYLOAD_SIZE`, `LTR_EN`, `MSIX_EN`, `CPL_TIMEOUT_STATUS`, or `ARI_FUNCTION_GROUP`.
- Whether the macro is a bit shift (`__SHIFT`) or an already shifted mask (`_MASK`).

This lets C code avoid literal bit numbers when reading, updating, or testing PCIe configuration fields through MMIO/config-space accessors.

## Register Groups Covered

The chunk includes these major groups:

- `VF3` tail: correctable error status/mask, AER capability control, TLP header/prefix log registers, and ARI enhanced capability fields.
- `VF4` base PCI header: vendor/device ID, command/status, revision/class fields, cache-line/latency/header/BIST fields, BARs, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- `VF4` PCIe capability: capability list, `PCIE_CAP`, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- `VF4` MSI/MSI-X capability: MSI message control, MSI address/data/mask/pending fields for 32-bit and 64-bit forms, MSI-X table/PBA fields, and MSI-X enable/function-mask/table-size fields.
- `VF4` vendor-specific and AER extended capabilities: VSEC header/scratch fields, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability control, header log dwords, TLP prefix log dwords, and ARI capability/control fields.
- `VF5` and `VF6`: the same virtual-function PCIe capability layout continues for later VFs in the visible chunk. These are structurally repetitive field maps for per-VF config-space instances.
- `VF7` beginning: base PCI header through device capability/control/status and the start of `LINK_CAP` fields. The chunk boundary ends after `VF7_LINK_CAP__LINK_SPEED`, `LINK_WIDTH`, power-management/latency/reporting bits, and `PORT_NUMBER` masks.

## Important APIs, Types, and Macros

There are no functions or C types in this range. The important interface is the generated macro naming convention:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REG>__<FIELD>__SHIFT` gives the low bit of a field.
- `BIF_CFG_DEV0_EPF0_VF<n>_<REG>__<FIELD>_MASK` gives the shifted mask suitable for clearing, testing, or extracting field bits.
- Full-register payload fields use `0xFFFFFFFFL`, for example TLP header logs, TLP prefix logs, BARs, MSI pending/mask, and VSEC scratch registers.
- Smaller config-space fields use natural PCI/PCIe widths: byte fields often use `0xFFL`, 16-bit fields use `0xFFFFL`, and packed capability/control/status fields use narrower masks within 16-bit or 32-bit registers.

In normal AMDGPU code, these macros are consumed through helper macros and register accessors, including:

- `REG_GET_FIELD(value, REG, FIELD)` to extract a field using the `REG__FIELD_MASK` and `REG__FIELD__SHIFT` definitions.
- `REG_SET_FIELD(value, REG, FIELD, new_value)` to update one field while preserving the other bits.
- `RREG32_SOC15()` and `WREG32_SOC15()` to read and write NBIO registers by the corresponding `reg...` address macro from `nbio_4_3_0_offset.h`.
- `WREG32_FIELD15_PREREG()` and related helpers for direct field writes where supported by the local driver code.

The matching address definitions are not in this header. For example, `nbio_4_3_0_offset.h` maps `regBIF_CFG_DEV0_EPF0_VF4_DEVICE_CNTL` to `0x1901b` with base index `5`, `regBIF_CFG_DEV0_EPF0_VF4_PCIE_UNCORR_ERR_STATUS` to `0x19055`, and `regBIF_CFG_DEV0_EPF0_VF7_LINK_CAP` to `0x19c1c`. This chunk supplies the field layout for those addresses.

## Control Flow

This chunk has no runtime control flow. It is compile-time metadata that affects generated machine code only when included by C sources. The effective control flow is in callers:

1. A caller reads a register or configuration dword using an offset macro from `nbio_4_3_0_offset.h`.
2. It uses this header's mask/shift macros directly or indirectly through `REG_GET_FIELD`/`REG_SET_FIELD`.
3. It conditionally interprets status bits or constructs a modified value.
4. It writes the result back if configuration needs to change.

Examples elsewhere in the NBIO 4.3 implementation show this pattern for NBIO fields in general. `nbio_v4_3_program_ltr()` and `nbio_v4_3_program_aspm()` read device control and link/power registers, clear or set named masks, and write back only when the value changes. The exact VF4/VF7 macros in this chunk are not directly referenced in the searched C files, but they provide the same interface for SR-IOV virtual-function config-space handling, diagnostics, and future feature code.

## State and Persistence Behavior

The header itself has no state. The fields it describes map to hardware and PCIe configuration state:

- Command/status and device/link control bits can enable bus mastering, memory access, interrupts, relaxed ordering, no-snoop, max payload size, max read request size, LTR, completion timeout behavior, ARI forwarding, AtomicOp behavior, OBFF, and function-level reset initiation.
- Device/link status bits expose transient link state, link training, data-link active state, pending transactions, device errors, and equalization state.
- MSI/MSI-X registers hold interrupt routing state programmed by the PCI core or device driver, including MSI address/data, masks, pending bits, MSI-X table location, PBA location, and enable/mask controls.
- AER status registers represent latched hardware error state. AER mask and severity registers persist until software or firmware changes them. Header and TLP-prefix logs capture diagnostic packet context for errors.
- BAR, ROM, adapter ID, capability-pointer, and VSEC fields represent per-VF PCI config-space identity and resource layout.

Persistence depends on the underlying hardware reset domain. Values may be reset by PCI function reset, GPU reset, power state transitions, or firmware initialization. Because many status bits are write-one-to-clear or hardware-owned in PCIe-style registers, callers must use register-specific semantics rather than treating every mask as a normal read-modify-write field.

## Dependencies

This chunk depends on generated AMD register metadata consistency:

- The include guard and file-level register family identify NBIO 4.3.0.
- Address macros from `nbio_4_3_0_offset.h` are required to locate the registers described here.
- AMDGPU SOC15 accessors and field helpers need the `REG__FIELD_MASK` and `REG__FIELD__SHIFT` naming convention.
- PCI/PCIe architectural semantics define the meaning of many fields: standard PCI command/status, PCIe device/link capability and control, MSI/MSI-X, AER, VSEC, and ARI.
- SR-IOV integration depends on VF-specific register windows: this chunk covers fields for `VF3`, `VF4`, `VF5`, `VF6`, and the beginning of `VF7`.

The header is generated from ASIC register descriptions, so hand edits would be risky unless synchronized with the source register database and offset header.

## Integration Points

The most direct integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which includes this header and uses NBIO field masks for register programming, HDP remap/flush setup, doorbell aperture setup, ROM offset handling, ASPM/LTR programming, and SR-IOV register remap behavior.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include this NBIO register metadata along with SMU/MP register metadata for power-management paths.
- The Linux PCI core and AMDGPU SR-IOV support, which may interact with the same VF config-space concepts even when not directly referencing these exact generated names.
- Error handling and RAS/diagnostic paths that interpret AER error status, mask, severity, and TLP/header logs.

The register names also align with other generated families such as `nbif_6_3_1_sh_mask.h` and older `nbio_*_sh_mask.h` headers. That alignment allows common driver patterns to be carried across ASIC generations while selecting the correct per-generation offsets and masks.

## Risks and Edge Cases

- Boundary risk: this chunk begins mid-register group with `VF3_PCIE_UNCORR_ERR_SEVERITY` masks already in progress, and it ends mid-`VF7` capability group. Any final merged file-level research must reconcile this with adjacent chunks to avoid claiming the range contains complete VF3 or VF7 coverage.
- Width and aliasing risk: PCI config registers pack byte, word, and dword fields into the same 32-bit MMIO/config dword. Offset headers show aliases such as `DEVICE_CNTL` and `DEVICE_STATUS` sharing an address. Callers must use the correct field masks and access width/semantics.
- Status-clearing risk: AER and PCIe status bits often have write-one-to-clear behavior. Generic read-modify-write code can accidentally clear latched errors if it writes back a value containing status bits.
- Capability-chain risk: `CAP_ID`, `NEXT_PTR`, enhanced capability `CAP_VER`, and `NEXT_PTR` fields define discoverability. Incorrect masks or offsets can break capability traversal or cause software to misidentify MSI, MSI-X, AER, VSEC, or ARI capabilities.
- SR-IOV isolation risk: VF-specific control, BAR, MSI/MSI-X, and AER fields affect virtual functions. Using a PF or wrong VF register name can corrupt another function's configuration or expose incorrect state to a guest/host boundary.
- Generated-header drift: field names are repeated across VF instances and ASIC-generation headers. Copy/paste or generator defects can be hard to see in review because most lines differ only by VF number or mask suffix.
- Hardware-version risk: this is NBIO 4.3.0 metadata. Reusing these masks with a different NBIO/NBIF generation may silently address the wrong bit layout even when names look similar.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver integration signals:

- Build coverage: AMDGPU builds that include `nbio_v4_3.c` and the SMU13 PPT files should compile without undefined `BIF_CFG...` field macros or naming mismatches.
- Register helper coverage: code using `REG_GET_FIELD` or `REG_SET_FIELD` with registers from this range should expand successfully to the expected `__SHIFT` and `_MASK` names.
- Offset/mask consistency: each field group in this header should have a corresponding `regBIF_CFG_DEV0_EPF0_VF<n>_<REG>` entry in `nbio_4_3_0_offset.h`; spot checks show VF4 device control, VF4 AER status, and VF7 link capability are present.
- SR-IOV smoke tests: VF creation, VF reset, guest driver probe, BAR assignment, and MSI/MSI-X interrupt delivery should work without PCI config-space corruption.
- PCIe capability visibility: `lspci -vv` or equivalent config-space reads on supported hardware/VFs should show coherent PCIe, MSI/MSI-X, AER, VSEC, and ARI capability fields.
- Error-path diagnostics: injected or naturally occurring PCIe correctable/uncorrectable errors should set expected AER bits, preserve header/TLP-prefix logs, and respect mask/severity programming.
- Power/link behavior: link speed/width, ASPM/LTR, completion-timeout, and link-status reporting should match expected values across boot, runtime PM, reset, and resume.

## Summary

Lines 39245-41680 of `nbio_4_3_0_sh_mask.h` are generated register field metadata for NBIO 4.3.0 SR-IOV VF PCIe configuration space. The chunk is dominated by repeated per-VF masks and shifts for PCI header fields, PCIe device/link capabilities, MSI/MSI-X, vendor-specific capability, AER, TLP/header logs, and ARI. It has no runtime behavior on its own, but it is a critical compile-time contract between AMDGPU NBIO/SMU code, SOC15 register access helpers, PCIe config semantics, and hardware register offsets.

### subset-b-002978: lines 41681-44102

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 41681-44102

## Scope And Purpose

This chunk is part of the generated AMDGPU NBIO 4.3.0 shift/mask register header. It contains C preprocessor constants for decoding and composing bitfields in NBIO/BIF PCI configuration-space registers for SR-IOV virtual functions under `BIF_CFG_DEV0_EPF0`. The source is declarative: it has no executable functions, no structs, and no runtime control flow. Its purpose is to give AMDGPU code stable symbolic names for register field shifts and bit masks.

The covered range starts in the middle of VF7's PCIe capability block at `BIF_CFG_DEV0_EPF0_VF7_LINK_CAP`, continues through the rest of VF7's PCIe/MSI/MSI-X/AER/ARI field definitions, covers complete VF8 and VF9 virtual-function configuration layouts, and ends in VF10 after `BIF_CFG_DEV0_EPF0_VF10_PCIE_UNCORR_ERR_STATUS`. VF8 and VF9 each include 622 `#define` entries in this slice; VF7 contributes the tail of its map, and VF10 contributes its beginning through uncorrectable-error status.

## Register Families Covered

The macros follow the generated naming convention:

- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>_MASK` gives the field mask already positioned in the register.
- Comment lines such as `//BIF_CFG_DEV0_EPF0_VF8_COMMAND` delimit a logical register section.
- `// addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp` and similar comments identify the generated address block for full VF maps.

Major register groups in the range are:

- PCI configuration identity and header fields for VF8, VF9, and the beginning of VF10: vendor/device IDs, command/status, revision and class code fields, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI Express capability registers: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI registers: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data registers, extended data, masks, pending bits, and 64-bit message variants.
- MSI-X registers: `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific enhanced capability registers: list header, vendor-specific header, and two scratch registers.
- Advanced Error Reporting registers: enhanced capability list, uncorrectable-error status/mask/severity, correctable-error status/mask, AER capability/control, header logs, and TLP prefix logs. VF10 in this chunk reaches only the uncorrectable-error status register; its following mask/severity definitions are outside this chunk.
- ARI extended capability registers for VF7, VF8, and VF9: capability-list header, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

## Important Fields

The PCIe capability fields expose link negotiation, power management, and error-reporting controls. `LINK_CAP` and `LINK_STATUS` encode link speed, width, power-management support, exit latencies, data-link active reporting, link bandwidth notification, current link speed, negotiated width, link training, slot clock, and autonomous bandwidth status. `LINK_CNTL` and `LINK_CNTL2` provide writable controls such as PM control, link disable, retrain link, common clock configuration, autonomous width/speed disable, target link speed, compliance mode, de-emphasis, and transmit margin.

`DEVICE_CAP`, `DEVICE_CNTL`, and their second-generation variants model core PCIe endpoint features: payload/read-request sizes, relaxed ordering, extended tags, function-level reset initiation, completion-timeout support/configuration, ARI forwarding, atomic operations, ID-based ordering, LTR, ten-bit tags, OBFF, end-to-end TLP prefix behavior, and emergency power reduction signaling. `DEVICE_STATUS` exposes error and transaction-pending state bits.

The interrupt capability blocks define MSI and MSI-X programming fields: capability IDs and next pointers, MSI enable/multiple-message settings, 64-bit MSI support, per-vector masking capability, message address/data payloads, interrupt masks, pending bits, MSI-X table size, function mask, MSI-X enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

The AER fields are diagnostic and recovery-sensitive. Uncorrectable-error fields include data link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic operation egress blocked, TLP prefix blocked, and poisoned TLP egress blocked status. Correctable-error fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory non-fatal error, corrected internal error, and header log overflow. Header-log and TLP-prefix-log registers expose raw captured dwords.

## APIs, Types, And Functions

This chunk defines no C APIs, types, functions, or inline helpers. The public surface is entirely macro names and literal constants. Downstream code typically combines these definitions with the matching address macros from `nbio_4_3_0_offset.h` and register read/write helpers in AMDGPU code, for example using the mask to isolate a field and the shift to normalize it:

```c
field = (reg_value & BIF_CFG_DEV0_EPF0_VF8_LINK_STATUS__CURRENT_LINK_SPEED_MASK) >>
        BIF_CFG_DEV0_EPF0_VF8_LINK_STATUS__CURRENT_LINK_SPEED__SHIFT;
```

The header is included directly by NBIO 4.3 integration code such as `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and by SMU13 power-management files that also include the matching NBIO offset header. Those consumers provide the actual register access functions and hardware sequencing.

## Control Flow

There is no local control flow. The operational control flow lives in AMDGPU call paths that include this header, select an NBIO register address from the offset header, read or modify the register, and apply these masks and shifts to access individual fields. Typical flows include:

- Reading link status fields to report or validate negotiated PCIe speed/width.
- Updating link-control fields when forcing retrain, changing target link speed, or managing autonomous width/speed behavior.
- Inspecting AER status/log fields during PCIe error handling.
- Programming MSI/MSI-X registers as part of virtual-function interrupt setup.
- Reading or writing SR-IOV VF configuration-space shadow registers while managing virtual functions.

Because this file only names bit positions, it does not impose ordering, locking, polling, timeout, or reset behavior. Callers must supply those semantics according to the PCIe spec, the NBIO IP block rules, and the AMDGPU subsystem that is touching the register.

## State And Persistence Behavior

The header itself has no state and no persistence. The state represented by these macros is hardware-backed PCI configuration and capability state for AMD NBIO virtual functions. Some fields are read-only hardware capability/status bits, some are software-programmable configuration bits, and some are write-1-to-clear or otherwise side-effecting status bits depending on the underlying PCIe register semantics.

State persists in device registers across normal driver reads and writes, but may be reset by GPU reset, PCI function reset, virtual-function reset, power transitions, or firmware-managed reinitialization. BAR, command/status, MSI/MSI-X, AER, and link-control values are particularly sensitive because they affect memory decoding, interrupt delivery, error reporting, and PCIe link behavior.

## Dependencies And Integration Points

This chunk depends on generated ASIC register metadata being consistent across the NBIO 4.3.0 register header family:

- `nbio_4_3_0_offset.h` supplies corresponding register offsets/addresses.
- `nbio_4_3_0_default.h`, where present in the same generated family, supplies reset/default values for registers.
- AMDGPU NBIO code supplies register access wrappers, device discovery, and IP-version dispatch.
- SMU13 power-management code includes the same header for NBIO-related power, clock, or link-management fields.
- Linux PCIe, SR-IOV, MSI/MSI-X, and AER subsystems provide the higher-level concepts these register fields mirror.

The integration boundary is intentionally low-level. Higher layers should not duplicate numeric masks; they should refer to these generated names so ASIC header updates remain centralized.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask, shift, or VF register mapping can silently decode the wrong bits or write reserved bits in hardware registers.
- The chunk boundaries split logical register maps. VF7 starts before this chunk and VF10 continues after it, so research or tooling that treats this chunk as a complete per-file contract must account for adjacent chunks.
- Several registers use overlapping PCIe terms such as `MASK` as both a field name and the generated suffix, producing names like `...MSI_MASK__MSI_MASK_MASK`. Consumers must use exact generated identifiers.
- AER status registers may have side-effecting clear behavior in hardware. Using these macros in read-modify-write code without respecting PCIe semantics can lose diagnostic information.
- Link-control fields such as retrain, link disable, target speed, compliance mode, and autonomous speed/width disable can disrupt the PCIe link if written at the wrong time.
- MSI/MSI-X address, data, mask, pending, table, and PBA fields are security and stability sensitive for SR-IOV VFs; incorrect programming can break interrupt delivery or leak interrupts across isolation boundaries.
- Some fields are 16-bit PCI capability fields and others are 32-bit enhanced-capability or BAR/log fields. Callers must use access widths and register offsets that match the underlying register, not just the mask literal width.

## Test Signals

Useful validation for this chunk is mostly compile-time and hardware/driver-integration oriented:

- Build AMDGPU objects that include `nbio_4_3_0_sh_mask.h`, especially `amdgpu/nbio_v4_3.c` and SMU13 files, with warnings enabled.
- Run generated-header consistency checks that compare every `__SHIFT`/`_MASK` pair against the register database and matching offset/default headers.
- Verify that masks are contiguous where the field is multi-bit, are aligned with their shift values, and do not overlap unexpected adjacent fields inside each register.
- Exercise PCIe link reporting and management on NBIO 4.3 ASICs and confirm decoded link speed/width/status values match Linux PCI core observations.
- Exercise SR-IOV VF creation/reset paths and confirm VF8/VF9/VF10 config-space fields, BARs, MSI/MSI-X capabilities, and ARI capability exposure match expected hardware behavior.
- Trigger or inject PCIe AER conditions where possible and verify uncorrectable/correctable status, severity/mask, header-log, and TLP-prefix-log decoding uses the documented bits.
- Run suspend/resume, GPU reset, function-level reset, and VF reset tests to catch stale assumptions about which register fields persist across resets.

### subset-b-002979: lines 44103-46534

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 44103-46534

## Scope

This chunk is a generated AMD NBIO 4.3.0 shift/mask header segment for BIF/NBIF PCI configuration-space registers on device 0, endpoint function 0 virtual functions. It contains only C preprocessor macros: no functions, structs, executable statements, storage declarations, locking, or initialization logic.

The range starts inside the virtual-function 10 (`VF10`) PCIe Advanced Error Reporting tail, beginning at the final `PCIE_UNCORR_ERR_STATUS` masks and continuing through VF10 AER mask/severity, correctable-error, AER capability/control, TLP header/prefix log, and ARI definitions. It then contains full address blocks for `VF11`, `VF12`, and `VF13`, and ends after the early `VF14` PCIe capability header fields at `BIF_CFG_DEV0_EPF0_VF14_PCIE_CAP__INT_MESSAGE_NUM_MASK`.

The visible address-block markers are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp`

There is no address-block marker for `VF10` in this range because the chunk begins in the middle of the preceding VF10 block.

## Purpose

The macros define bit positions and masks for NBIO 4.3.0 PCI/PCIe configuration decode fields. AMDGPU code pairs these definitions with register offsets from `nbio_4_3_0_offset.h` and register access helpers so it can read, decode, compose, or write hardware register values without embedding raw bit constants.

The dominant macro shape is:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>_MASK`

where `<n>` is `10`, `11`, `12`, `13`, or `14` in this chunk. The full VF11, VF12, and VF13 blocks are mechanically repeated per virtual function and model a PCI function's standard header, PCIe capability, MSI/MSI-X capability, vendor-specific extended capability, AER diagnostics, TLP log registers, and ARI extended capability. VF10 and VF14 are partial due to chunk boundaries.

## Register Coverage

VF10 coverage in this chunk is the tail of its PCIe error and routing capability definitions:

- AER uncorrectable error status masks for data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked cases.
- AER uncorrectable error mask and severity fields for the same error classes.
- Correctable error status and mask fields for receiver error, bad TLP, bad DLLP, replay number rollover, replay timer timeout, advisory nonfatal, correctable internal error, and header-log overflow.
- AER capability/control fields such as first-error pointer, ECRC generation/checking capability and enable bits, multi-header recording controls, TLP prefix logging presence, and completion-timeout logging capability.
- Four 32-bit TLP header log words and four 32-bit TLP prefix log words.
- ARI enhanced capability list, ARI capability, and ARI control fields.

VF11, VF12, and VF13 are complete within this chunk. Each full VF block includes:

- Standard PCI header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list header, PCIe capability word, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- MSI fields: MSI capability list, message control, low/high message address, message data, extended message data, vector mask, 64-bit data/mask aliases, and pending bits.
- MSI-X fields: MSI-X capability list, table size, function mask, enable bit, table BIR/offset, and pending-bit-array BIR/offset.
- Vendor-specific PCIe extended capability fields: enhanced capability list metadata, vendor-specific header metadata, and two 32-bit scratch registers.
- AER fields: enhanced capability list metadata, uncorrectable status/mask/severity, correctable status/mask, AER capability/control, four header log dwords, and four TLP prefix log dwords.
- ARI fields: enhanced capability list metadata, multifunction/ACS function-group capability bits, next function number, function-group enable bits, and function-group selector.

VF14 coverage starts a new full VF block but ends early. It includes the standard PCI header field definitions through `MAX_LATENCY`, the `PCIE_CAP_LIST` fields, and the `PCIE_CAP` fields for PCIe capability version, device type, slot implemented, and interrupt message number. The remaining VF14 PCIe device/link/MSI/MSI-X/vendor-specific/AER/ARI field definitions belong to the next chunk.

## Important APIs, Types, and Functions

There are no C APIs, type definitions, or functions in this header slice. Its consumed interface is the macro namespace itself.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` define standard PCI command/status bits such as I/O access, memory access, bus master enable, SERR, interrupt disable, capability-list presence, target/master abort reporting, parity reporting, and interrupt status.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, and `*_MSIX_PBA__*` expose address-like registers whose low bits encode enablement, type, BIR, validation, or reserved state. Consumers must preserve those encodings rather than treating every bit as a plain address.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` model PCIe capability metadata, device type, slot implementation, interrupt message number, FLR capability/initiation, payload and read-request sizing, relaxed ordering, no-snoop, completion-timeout controls, ASPM, link retrain/disable, negotiated speed/width, bandwidth status, equalization status, retimer and crosslink indicators, and supported link speed vectors.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability programming: MSI enablement, multi-message capability/enable values, 64-bit address support, per-vector mask capability, message address/data registers, vector masks, pending bits, MSI-X table sizing, function masking, enablement, and table/PBA locations.
- `*_PCIE_VENDOR_SPECIFIC_*` fields define the vendor-specific enhanced capability list header, VSEC ID/revision/length, and scratch dwords.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define PCIe AER reporting status, reporting masks, severity classification, ECRC controls, multi-header recording, TLP prefix log presence, completion-timeout log capability, and first-error pointer fields.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw 32-bit diagnostic capture words used after PCIe/AER events.
- `*_PCIE_ARI_*` defines Alternate Routing-ID Interpretation capability and control fields for function grouping and next-function discovery.

## Control Flow

This chunk has no runtime control flow. Inclusion is governed by the surrounding header guard in the full file. At compile time, translation units that include `nbio_4_3_0_sh_mask.h` receive these symbolic constants.

The intended consumer flow is inferred from generated AMDGPU register conventions:

1. A caller selects a register address from `nbio_4_3_0_offset.h`, for example a `cfgBIF_CFG_DEV0_EPF0_VF11_*` register.
2. The driver reads or writes the register through AMDGPU/SOC15 PCI config, MMIO, or indirect register helpers.
3. Field extraction or composition uses these `__SHIFT` and `_MASK` definitions, commonly through helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`.
4. The resulting values control or inspect VF configuration, interrupt delivery, PCIe link/device controls, AER diagnostics, or ARI routing metadata.

Direct include users found in this tree are `amdgpu/nbio_v4_3.c`, `pm/swsmu/smu13/smu_v13_0_0_ppt.c`, and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`. These files include the NBIO 4.3.0 offset and shift/mask headers to access NBIO/PCIe register fields in a SoC-version-specific way.

## State and Persistence Behavior

The header stores no software state and performs no persistence. It describes bit layout for state held in hardware PCI configuration and PCIe extended-capability registers.

State represented by these macros is per virtual function. Configuration/control fields can persist in hardware until reset, function-level reset, PF-mediated VF teardown/recreation, or driver reprogramming. Examples include PCI command enables (`MEM_ACCESS_EN`, `BUS_MASTER_EN`, `IO_ACCESS_EN`), interrupt disable, MSI/MSI-X enables and masks, device-control fields such as payload size, extended tag enable, relaxed ordering, no-snoop, completion timeout, FLR initiation, link-control fields, AER mask/severity/ECRC controls, and ARI function-group controls.

Status and diagnostic fields are hardware-updated. PCI status bits, device/link status bits, AER correctable and uncorrectable status bits, first-error pointer, TLP header logs, TLP prefix logs, MSI pending bits, and link equalization indicators can be sticky, read-only, clear-on-write, or otherwise side-effectful according to PCIe and NBIO hardware rules. This header does not encode those access semantics; it only supplies bit positions and masks.

Because this range covers SR-IOV VF config decode windows, mistakes in a VF number or macro family can affect the wrong VF's configuration view. That is especially important for VF11 through VF13, which are complete and nearly identical aside from the numeric VF prefix.

## Dependencies and Integration Points

Key dependencies and integration points:

- `nbio_4_3_0_offset.h` supplies the matching register offsets. This header supplies the bitfield masks and shifts for those offsets.
- Other generated NBIO 4.3.0 headers, especially default-value headers, must remain synchronized with this register database.
- AMDGPU register helper macros consume the generated naming convention. The `__SHIFT` and `_MASK` suffixes are expected by field-access patterns such as `REG_GET_FIELD`/`REG_SET_FIELD`.
- `amdgpu/nbio_v4_3.c` is the direct NBIO runtime integration point in the tree for this generation.
- SMU 13.0.0 and 13.0.7 power-management code includes this header, so build coverage for those paths also validates that the macro names remain available.
- Linux PCI/PCIe concepts mirrored by this chunk include SR-IOV VFs, PCI command/status, BAR/ROM layout, capability lists, PCIe device/link capability, MSI, MSI-X, AER, and ARI.
- PCIe diagnostics and recovery paths can use the AER and TLP log field definitions when decoding error status from NBIO hardware.
- Interrupt setup and teardown paths depend on the MSI/MSI-X field definitions when programming VF interrupt delivery, masks, pending bits, and table/PBA locations.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file itself is AMD GPU driver hardware metadata and has no Ceph filesystem behavior.

## Risks and Edge Cases

- This is generated, highly repetitive hardware metadata. A single wrong shift or mask can silently corrupt all consumers that decode or compose the affected register field.
- Chunk boundaries are partial. VF10 begins before this range and VF14 continues after it. Whole-VF conclusions for those two functions require adjacent chunks.
- VF11, VF12, and VF13 should be structurally identical except for VF number. Copy-generation drift between these blocks is difficult to catch by manual review.
- AER status, mask, and severity families use almost identical field names. Using a status mask where a reporting mask or severity mask is intended can suppress errors, misclassify errors, or inspect/clear the wrong hardware state.
- Correctable and uncorrectable AER status fields may have write-one-to-clear or sticky behavior. The macros do not communicate those semantics, so consumers need hardware/PCIe knowledge when writing them.
- BAR, ROM, MSI-X table, and MSI-X PBA fields contain encoded low bits. Treating them as raw addresses can damage BIR/type/enable/reserved fields.
- MSI and MSI-X fields include 32-bit and 64-bit layout aliases. Consumers must select offsets and masks consistently with the capability's 64-bit addressing and per-vector masking bits.
- Link-control fields such as retrain, disable, autonomous speed disable, compliance controls, and equalization-related controls can affect device reachability if written incorrectly.
- ARI controls interact with PCIe function routing and enumeration. Enabling or interpreting ARI function groups incorrectly can expose the wrong function topology to software.
- Literal masks use `L` suffixes and cover 8-bit, 16-bit, and 32-bit fields. Consumers should avoid implicit truncation, sign-extension, or host-width assumptions.

## Test Signals

Useful validation signals for this chunk:

- Compile AMDGPU configurations that include `nbio_4_3_0_sh_mask.h`, especially `amdgpu/nbio_v4_3.c` and SMU 13.0.0/13.0.7 paths; malformed or missing macro names should fail the build.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database, ensuring every offset in `nbio_4_3_0_offset.h` has the expected shift/mask definitions and vice versa.
- Pattern-check VF11, VF12, and VF13 for identical register families, field names, shifts, and masks after normalizing the VF number. Treat VF10 and VF14 separately because they are partial in this chunk.
- Validate mask/shift consistency mechanically: each `_MASK` should align with its paired `__SHIFT`, multi-bit masks should have contiguous bit ranges where expected, and full-dword fields should use shift `0x0` with mask `0xFFFFFFFFL`.
- On NBIO 4.3.0 SR-IOV-capable hardware, enable enough virtual functions to exercise VF11 through VF13, enumerate them, bind host/guest drivers, and compare decoded PCI config-space capability fields with `lspci -vv` or driver debug output.
- Exercise MSI/MSI-X on VF11 through VF13: enable vectors, program message address/data, toggle masks, inspect pending bits, and verify interrupts are delivered and quiesced as expected.
- Use PCIe/AER injection or observed error paths to verify uncorrectable/correctable status, mask, severity, first-error pointer, header logs, and TLP prefix logs decode correctly.
- Run VF lifecycle tests around FLR, guest detach/attach, PF reset, and VF recreation to confirm command/status, interrupt, AER, and ARI state returns to expected defaults.
- Merge-lane validation should explicitly reconcile the adjacent chunks so VF10 and VF14 are not represented as complete blocks based on this slice alone.

### subset-b-002980: lines 46535-48958

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 46535-48958

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It contains only C preprocessor constants for register-field shifts and masks in NBIF/BIF PCI configuration decode space. There are no functions, structs, enums, executable statements, allocation paths, locks, or runtime initialization in this range.

The range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF14_PCIE_CAP` definitions, completes the rest of the `EPF0_VF14` PCIe capability block, covers the full `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` virtual-function block, and then begins `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` through the first `PCIE_MC_RCV0` shift definition. The chunk ends before the `PCIE_MC_RCV0` mask and before later EPF1 multicast, LTR, ARI, SR-IOV, and trailing register families.

## Purpose

The macros provide symbolic bit layouts for NBIO 4.3.0 PCI/PCIe configuration registers so AMDGPU code can decode and compose hardware register values without embedding raw bit numbers. The dominant interface is the paired macro convention:

- `BIF_CFG_DEV0_EPF0_VF14_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF14_<REGISTER>__<FIELD>_MASK`
- `BIF_CFG_DEV0_EPF0_VF15_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF15_<REGISTER>__<FIELD>_MASK`
- `BIF_CFG_DEV0_EPF1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF1_<REGISTER>__<FIELD>_MASK`

The companion generated offset header supplies concrete register addresses and base indices; this file supplies the field encodings consumed by `REG_GET_FIELD`, `REG_SET_FIELD`, and direct mask/shift operations.

## Register Coverage

The `EPF0_VF14` portion is partial at the beginning. It starts after the first `PCIE_CAP` shift fields and then covers the rest of VF14's PCIe capability and extended capability layout:

- PCIe capability, device, and link registers: `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus PCIe 2.0 style `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X: capability list pointers, MSI message control, message address/data fields, mask and pending fields, 64-bit variants, MSI-X table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific PCIe extended capability header and payload registers.
- Advanced Error Reporting: uncorrectable status/mask/severity, correctable status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ARI enhanced capability, ARI capability, and ARI control fields.

The `EPF0_VF15` block is complete in this chunk. It repeats the full per-VF PCI configuration model:

- Standard PCI header registers: vendor/device ID, command, status, revision and class code bytes, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability, device/link control and status, completion timeout, FLR, ASPM/L1 PM substates, link speed/width, link retrain/disable, autonomous width/speed disable, equalization completion, and link speed vector fields.
- MSI/MSI-X, vendor-specific PCIe extended capability, AER, TLP logs, TLP prefix logs, and ARI.

The `EPF1` block begins at line 47795 and is partial at the end. In this chunk it covers:

- Standard PCI header registers and base address fields for endpoint function 1.
- Vendor capability list and writable adapter ID fields.
- Power Management Interface: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- PCIe capability, device/link control and status, MSI/MSI-X, vendor-specific capability, device serial number, AER, and TLP log fields.
- Resizable BAR enhanced capability and `BAR1` through `BAR6` capability/control fields.
- Power budget capability/data/select fields.
- Dynamic Power Allocation capability, status/control, latency indicator, and substate power allocation registers 0 through 7.
- Secondary PCIe extended capability, link control 3, lane error status, and lane 0 through lane 15 equalization control fields.
- ACS capability/control, PASID capability/control, and the start of multicast capability registers: `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0`, `PCIE_MC_ADDR1`, and the first shift definition for `PCIE_MC_RCV0`.

## Important APIs, Types, and Functions

There are no callable APIs, declared types, or functions in this chunk. The externally visible interface is the macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` mirror standard PCI command/status bits, including I/O access, memory access, bus mastering, special cycle, memory write/invalidate, VGA palette snoop, parity response, SERR, fast back-to-back enable, interrupt disable, capability-list presence, abort status, parity status, and PME status.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, `*_MSIX_PBA__*`, and EPF1 resizable BAR control fields expose BAR-like encodings where low bits are attributes, BIR selectors, or enable bits rather than address bits.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` define PCIe version/type, slot implementation, interrupt message number, payload and read request sizing, relaxed ordering, no-snoop, FLR, completion timeout, ASPM, L1 PM substates, link speed, link width, retrain/disable, common clock, extended sync, bandwidth interrupt enables, equalization completion, and compliance flags.
- `*_MSI_*` and `*_MSIX_*` cover interrupt capability programming: MSI enable, multi-message capability and enable values, 64-bit address support, per-vector masking support, address/data programming, masks, pending bits, MSI-X table size, function mask, table location, and PBA location.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` encode AER status, reporting masks, severity classification, ECRC generation/check support and enables, multi-header recording, first-error pointer, completion-timeout prefix/header logging, and TLP prefix log presence.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw captured diagnostic words for PCIe error analysis.
- `*_PCIE_ARI_*` encodes alternate routing-ID support, next function number, and function group controls for VF14/VF15.
- EPF1-only capability families in this range add serial number fields, resizable BAR sizing/control, power budget reporting, DPA power allocation, secondary capability link control and lane equalization, ACS peer-to-peer/isolation controls, PASID enablement and width, and multicast base/receive/control definitions.

## Control Flow

This header chunk has no runtime control flow. Inclusion is controlled by the enclosing header guard outside this slice. At compile time, translation units including `nbio_4_3_0_sh_mask.h` receive these constants.

Typical consumer flow is inferred from the generated-register pattern:

1. Use the matching `nbio_4_3_0_offset.h` register macro to identify the MMIO/config-space address.
2. Read the register through AMDGPU PCI config, NBIO, or MMIO helpers.
3. Extract fields using the `*_MASK` and `*_SHIFT` constants, usually through generated register helper macros.
4. Compose and write new values when enabling PCIe features, interrupt routing, AER policy, power management, BAR sizing, ACS/PASID/multicast policy, or VF-visible configuration state.

## State and Persistence Behavior

The header stores no software state and persists nothing. It describes state held by PCI/PCIe hardware configuration registers.

Control fields described here can persist until reset, function-level reset, PF reconfiguration, or driver/PCI core writes. Examples include command bits such as memory access and bus mastering, interrupt disable, MSI/MSI-X enable and mask bits, payload/read request size, completion timeout control, link control, AER masks and severity bits, ECRC enables, ARI controls, EPF1 resizable BAR sizing enables, power-management controls, ACS isolation controls, PASID enables, and multicast controls.

Status and diagnostic fields are hardware-owned or sticky according to PCIe semantics. Examples include device and link status, AER correctable and uncorrectable status, first-error pointer, TLP header and prefix logs, MSI pending bits, lane error status, equalization completion flags, DPA status, and multicast receive bits. These may be read-only, write-one-to-clear, clear-on-reset, or hardware-updated depending on the underlying register.

The VF14 and VF15 blocks represent SR-IOV virtual-function configuration decode windows under `EPF0`. EPF1 is a separate endpoint-function configuration block with richer physical-function style capabilities in this range, including resizable BAR, power budget, DPA, ACS, PASID, and multicast support.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_4_3_0_offset.h`, which maps these symbolic field layouts to concrete register offsets and base indices.
- `nbio_4_3_0_default.h`, where generated defaults for the same ASIC register set are expected.
- AMDGPU generated register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, which rely on the exact `__SHIFT`/`_MASK` naming convention.
- NBIO 4.3 code such as `amdgpu/nbio_v4_3.c`, and SMU 13 power-management files that include `nbio/nbio_4_3_0_sh_mask.h`.
- Linux PCI/PCIe, MSI/MSI-X, SR-IOV, AER, ARI, ACS, PASID/IOMMU, resizable BAR, power management, and DPA concepts mirrored by the field names.
- Firmware and hardware register database generation. The file is generated and should generally be updated from the authoritative register description rather than hand-edited.

## Risks and Edge Cases

- This range has chunk-boundary partial registers. It starts after the first `VF14_PCIE_CAP` shift fields and ends before the `EPF1_PCIE_MC_RCV0` mask; reconciliation should avoid treating those two register definitions as complete inside this chunk alone.
- The definitions are highly repetitive. Copy-generation drift between VF14, VF15, and EPF1 register families can be hard to detect visually because most macro names differ only by function or VF number.
- A wrong shift or mask silently corrupts all consumers of that field. This is especially risky for AER status/mask/severity fields, which have similar names but different behavior.
- BAR, ROM BAR, MSI-X table/PBA, resizable BAR, and multicast address fields contain encoded attribute or selector bits. Consumers must not treat every masked bit as a plain byte address.
- Link-control, equalization, autonomous width/speed, and retrain fields can affect link stability and device reachability when written incorrectly.
- Interrupt fields have multiple layers of masking and enablement. Confusing MSI mask/pending fields, MSI-X function mask, and PCI command interrupt disable can produce lost or unexpected interrupts.
- ACS and PASID controls interact with IOMMU isolation and process-address-space translation. Incorrect enablement can break DMA translation or peer-to-peer access policy.
- AER fields may be sticky and write-one-to-clear. Using the wrong mask or severity definition can clear evidence, hide errors, or misclassify fatal/non-fatal conditions.
- Literal mask widths vary from byte and word fields to full 32-bit fields, all expressed as `L` constants. Callers should avoid implicit truncation, signedness, or read-modify-write assumptions.

## Test Signals

Useful validation signals for this chunk:

- Build coverage of AMDGPU translation units that include `nbio_4_3_0_sh_mask.h`; malformed macro names or missing field pairs should fail compile-time consumers.
- Generated-register consistency checks against `nbio_4_3_0_offset.h`, `nbio_4_3_0_default.h`, and the upstream hardware register database.
- Pattern checks comparing `EPF0_VF15` against neighboring VF blocks, with explicit allowance that `EPF0_VF14` is partial in this chunk.
- Pattern checks comparing EPF1 fields against other ASIC versions with the same capability families, especially ACS, PASID, multicast, DPA, power budget, and resizable BAR definitions.
- SR-IOV runtime tests that enumerate enough VFs to exercise VF14 and VF15, bind/unbind guest or host drivers, trigger VF FLR, and verify command, MSI/MSI-X, AER, and ARI-visible config state.
- Interrupt tests that program MSI and MSI-X vectors, toggle masks, inspect pending bits, and verify delivery and quiescence for VF and EPF1 contexts.
- PCIe capability inspection with `lspci -vv` or driver debug output to confirm payload sizes, link speed/width, FLR support, completion timeout, MSI/MSI-X, AER, ARI, ACS, PASID, power budget, and resizable BAR fields match hardware expectations.
- AER injection or observation tests validating uncorrectable/correctable status, masks, severity, first-error pointer, header logs, and TLP prefix logs.
- Link training and equalization diagnostics for EPF1, including lane error status and lane 0 through 15 equalization control fields.
- Reset/lifecycle tests around PF reset, VF FLR, SR-IOV enable/disable, suspend/resume, and hotplug-like teardown to ensure control/status fields return to expected defaults.

### subset-b-002981: lines 48959-51417

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 48959-51417

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It exports C preprocessor constants for hardware register bit positions and masks; it contains no executable code, functions, type declarations, allocation, locking, or direct register I/O.

The range starts in the tail of the `BIF_CFG_DEV0_EPF1` PCIe multicast/SR-IOV capability area, covers the full visible `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` address block, enters most of the `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block, and ends inside the `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_2` definition. It also includes RCC port-decode and endpoint PCIe control blocks for device 0 instance 1.

The chunk defines 2,134 `#define` rows across 314 distinct register-name prefixes. The interface is entirely macro based: each register field is represented by a `__SHIFT` value and a matching `_MASK` value.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 4.3.0 register interface. This slice lets AMDGPU code and related firmware-facing paths decode or compose NBIF/BIF PCI configuration-space and RCC endpoint register values without hard-coding bit offsets.

The main naming families are:

- `BIF_CFG_DEV0_EPF1_PCIE_*` for endpoint function 1 PCIe extended capabilities, especially multicast, LTR, ARI, SR-IOV, and VF resizable BAR controls.
- `BIF_CFG_DEV0_EPF2_*` for a complete endpoint function 2 PCI/PCIe configuration decode block.
- `BIF_CFG_DEV0_EPF3_*` for endpoint function 3 configuration decode fields through its ARI capability area.
- `RCC_DEV0_1_RCC_*` for root/control-complex port behavior, link policy, requester-ID restore, LTR, arbitration, and margining parameters.
- `RCC_EP_DEV0_1_*` for endpoint-side PCIe scratch, error interrupt, unsupported-request handling, LTR transmission, straps, and DPA state.

The companion `nbio_4_3_0_offset.h` supplies the register addresses; this file supplies the per-field shifts and masks that register helpers use after reading those addresses.

## Address Blocks and Register Coverage

Visible address-block markers in this range:

- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`
- `nbio_nbif0_rcc_dev0_RCCPORTDEC`
- `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`

The leading `EPF1` portion completes higher-level PCIe capability definitions:

- Multicast receive and block registers: `PCIE_MC_RCV*`, `PCIE_MC_BLOCK_ALL*`, and `PCIE_MC_BLOCK_UNTRANSLATED_*`.
- Latency Tolerance Reporting: `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP`.
- ARI capability/control: `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.
- SR-IOV capability/control/status and VF layout: `PCIE_SRIOV_*`, including VF counts, first VF offset, VF stride, VF device ID, page-size masks, six VF BAR base registers, and migration-state-array offset.
- VF resizable BAR capability/control registers for VF BAR1 through VF BAR6.

The `EPF2` and `EPF3` BIF configuration blocks define standard PCI and PCIe configuration-space fields:

- Basic PCI header fields: vendor/device ID, command/status, revision/class, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, adapter/subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PM and vendor capabilities: vendor capability list, writable adapter ID mirror, PMI capability list, PM capability, PM status/control, SBRN, FLADJ, and DBESL/DBESLD.
- PCIe device/link capability and control: device type, max payload/read request size, relaxed ordering, no-snoop, FLR, power states, ASPM/link disable/retrain, common clock, link speed/width, link bandwidth notification, DRS signaling, equalization, supported speed vectors, and compliance controls.
- Interrupt capabilities: MSI and MSI-X capability headers, MSI message control/address/data/mask/pending registers, MSI extended data, 64-bit variants, MSI-X table control, table BIR/offset, and PBA BIR/offset.
- PCIe extended capabilities: vendor-specific extended capability, AER status/mask/severity, correctable-error status/mask, AER capability/control, TLP header logs, TLP prefix logs, resizable BAR capabilities, power-budgeting registers, DPA capability/status/control and substate power allocation, ACS, PASID, and ARI.

The RCC blocks define non-config-space controls around the PCIe port and endpoint:

- `RCC_VDM_SUPPORT` exposes VDM/MCTP/AMPTP support and root-mode routing checks.
- `RCC_BUS_CNTL` covers bus-reset, error-log, poisoned TLP, completion-abort/unsupported-request, and downstream primary/secondary error signaling policy.
- `RCC_FEATURES_CONTROL_MISC` controls unsupported-request handling for ATC/PASID, translated requests, page requests, invalid completions, MSI/MSI-X pending cleanup, BME checks, ECRC device-error behavior, and poison-flag handling.
- `RCC_DEV0_LINK_CNTL` and `RCC_CMN_LINK_CNTL` cover link-down entry/exit, PME blocking, L1/LTR timing, and reset gating around link-down transitions.
- `RCC_EP_REQUESTERID_RESTORE`, `RCC_LTR_LSWITCH_CNTL`, `RCC_MH_ARB_CNTL`, and `RCC_MARGIN_PARAM_CNTL*` describe requester-ID restoration, LTR switch latency, arbitration mode/priority, and PCIe margining parameters.
- `RCC_EP_DEV0_1_*` defines endpoint scratch, PCIe control, error interrupt enable/status, invalid-PASID unsupported-request handling, hidden-register decode enablement, private LTR transmit controls, straps, DPA fields, and initial DPA substate power allocation entries.

## Important APIs, Types, and Functions

There are no C functions, structures, or callable APIs in this range. The consumed API surface is the macro namespace itself.

Important macro groups:

- `*_COMMAND__*` and `*_STATUS__*` define standard PCI command/status bits such as I/O access, memory access, bus mastering, SERR, interrupt disable, capability-list presence, parity, aborts, and system-error reporting.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, `*_MSIX_PBA__*`, and `*_SRIOV_VF_BASE_ADDR_*` define address-like fields where low bits can encode enablement, BIR, type, validation, or reserved state.
- `*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` model PCIe device controls such as payload sizing, read request sizing, FLR, error reporting, relaxed ordering, no-snoop, completion timeout, atomic operations, LTR, OBFF, ten-bit tags, and end-to-end TLP prefixes.
- `*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` define link speed/width capability, ASPM, retraining, disablement, common clock, autonomous width/speed controls, DRS, equalization, compliance settings, and live negotiated-link status.
- `*_MSI_*` and `*_MSIX_*` define interrupt-delivery fields for MSI enablement, multiple-message capability/enables, 64-bit addressing, per-vector masking, extended data, vector masks, pending bits, MSI-X function mask/enable, table location, and PBA location.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, `*_PCIE_ADV_ERR_CAP_CNTL__*`, `*_PCIE_HDR_LOG*`, and `*_PCIE_TLP_PREFIX_LOG*` define AER status, masks, severity policy, ECRC support/enables, first-error pointers, multi-header logging, and diagnostic packet capture words.
- `*_PCIE_ACS_*`, `*_PCIE_PASID_*`, and `*_PCIE_ARI_*` describe access-control, process address-space ID, and alternate routing-ID capabilities and controls used by PCIe/IOMMU/SR-IOV integration.
- `*_PCIE_DPA_*` and `RCC_EP_DEV0_1_*DPA*` define dynamic power allocation capability, latency indicators, substate status, compliance mode, and per-substate power allocation fields.
- `RCC_*` macros expose NBIO root/endpoint policy controls that are not simply standard PCI config-space fields, including unsupported-request filtering, pending MSI cleanup, BME checks, link-down reset behavior, requester-ID restore, and margining geometry.

## Control Flow

This chunk has no runtime control flow. Inclusion is controlled by the enclosing generated header guard outside this slice. At compile time, any translation unit that includes the NBIO 4.3.0 generated headers receives these constants.

Typical consumer flow is inferred from the macro design:

1. Select a register offset from `nbio_4_3_0_offset.h`.
2. Read the register through AMDGPU MMIO, PCI config, or SOC15 register helpers.
3. Extract fields with the `*_MASK`/`__SHIFT` pair, commonly via generated-register helper macros such as `REG_GET_FIELD`.
4. Compose updated values with matching masks/shifts, commonly with `REG_SET_FIELD`, then write the register back when enabling or disabling PCIe, interrupt, SR-IOV, AER, ACS/PASID/ARI, power, or RCC policy bits.

## State and Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes state held in NBIO/PCIe hardware registers.

Configuration fields such as `MEM_ACCESS_EN`, `BUS_MASTER_EN`, MSI/MSI-X enables, MSI-X function mask, PM state, FLR initiation, payload sizing, link controls, AER masks/severity, ACS/PASID/ARI enables, SR-IOV VF enables/counts/page sizes, VF BAR sizes, and RCC policy bits persist in hardware until changed by driver, firmware, PCI core, SR-IOV management, function-level reset, hot reset, or broader GPU reset.

Status fields such as device/link status, MSI pending bits, AER status, DPA status, equalization status, interrupt status, migration status, and TLP/header logs are hardware-updated. Some are sticky or clear-on-write according to PCIe/NBIO semantics, so mask misuse can acknowledge or hide events rather than merely inspect them.

Address-like fields in BAR, ROM BAR, MSI-X table/PBA, SR-IOV VF BAR, migration-state-array, and capability-list registers include encoded low bits. The masks in this header distinguish payload address/offset bits from control or selector bits, but consumers must preserve fields that are outside the intended update.

The RCC endpoint scratch register is a raw 32-bit field and may be used by low-level firmware/driver coordination, but this chunk does not define higher-level ownership or lifetime rules.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_4_3_0_offset.h`, which provides the corresponding register offsets for the field layouts described here.
- Other generated NBIO 4.3.0 headers such as defaults and register-base definitions, which must stay synchronized with this shift/mask file.
- AMDGPU/SOC15 register helper macros that expect the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- `amdgpu/nbio_v4_3.c` and SMU/DC display power-management code paths that include the NBIO 4.3.0 generated headers for PCIe/NBIO control.
- Linux PCI/PCIe subsystems for command/status, PM, MSI/MSI-X, AER, resizable BAR, DPA, ACS, PASID, ARI, SR-IOV, and link-management semantics.
- IOMMU and SR-IOV orchestration paths where PASID, ACS, ARI, VF BAR sizing, VF stride/offset, and VF enablement define how PFs and virtual functions are exposed and isolated.
- Hardware diagnostics and recovery paths that depend on AER status/mask/severity, ECRC controls, header logs, TLP prefix logs, RCC interrupt status, and link-down controls.

## Risks and Edge Cases

- The file is generated and very repetitive. A single shift or mask generation error can silently corrupt every consumer of that field.
- This chunk begins mid-`EPF1` area and ends mid-`RCC_EP_DEV0_1` DPA substate definition. Merge/reconciliation should not treat it as a complete file or even a complete final address-block slice.
- `EPF2` and `EPF3` are structurally similar, but some partial-boundary differences are due to chunking rather than hardware differences. Cross-function comparison checks should account for the truncated start/end of the range.
- Status, mask, and severity AER registers share nearly identical field names. Using a status mask where a severity or enable mask is required can suppress reporting, misclassify faults, or clear the wrong condition.
- MSI/MSI-X fields are split across 32-bit and 64-bit variants. Incorrect use of `*_64` definitions can program the wrong data/mask/pending register layout.
- BAR-like fields include encoded low bits. Treating the full masked value as a plain byte address can lose BIR, enable, validation, or type information.
- Link-control fields such as retrain, disable, autonomous speed/width controls, compliance entry, and equalization controls can affect reachability if written without PCIe state-machine coordination.
- ACS, PASID, ARI, ATS-related RCC behavior, and SR-IOV VF controls interact with IOMMU isolation and PCIe routing. Enabling them without platform support can break DMA translation, function discovery, or VF isolation.
- RCC policy bits around unsupported requests, BME checks, MSI pending cleanup, ECRC, poison handling, and completion abort/unsupported-request signaling can hide real hardware errors or generate unexpected errors if configured incorrectly.
- DPA, LTR, and power-management fields influence latency and power behavior. Bad values may cause incorrect power-state transitions, missed LTR messages, or poor link/power performance.

## Test Signals

Useful validation signals for this chunk:

- Build AMDGPU configurations that include `nbio_4_3_0_sh_mask.h`; malformed, missing, or duplicate macros should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database and against `nbio_4_3_0_offset.h`, especially for offset-to-field pairing and address-block boundaries.
- Compare `EPF2` and `EPF3` register families for expected structural parity while ignoring the known chunk boundaries.
- SR-IOV smoke tests that enable VFs, verify VF counts/stride/first-offset/device-ID exposure, exercise VF BAR sizing, and bind/unbind PF/VF drivers.
- PCIe capability inspection with `lspci -vv` or driver debug output to confirm command/status, PM, MSI/MSI-X, AER, ACS, PASID, ARI, resizable BAR, DPA, and link capability fields decode as expected.
- MSI/MSI-X tests that program vectors, toggle masks/function mask, check pending state, and verify delivery and quiescing for EPF2/EPF3 paths.
- AER injection or observation tests that verify correctable/uncorrectable status, masks, severity, first-error pointer, ECRC controls, TLP header logs, and TLP prefix logs.
- Link-management tests around retraining, speed/width negotiation, equalization, DRS, ASPM/LTR, and reset/link-down transitions.
- Power-management tests for PM states, LTR transmit controls, DPA latency/substate/power-allocation fields, and RCC L1/LTR timers.
- RCC error-path tests that toggle unsupported-request filtering, invalid PASID handling, BME checks, poison/ECRC behavior, and endpoint interrupt enable/status bits, then verify visible driver error reporting.

### subset-b-002982: lines 51418-54381

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 51418-54381

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,002 preprocessor `#define` entries across 2,964 source lines. There are no C functions, structs, enums, variables, allocation sites, locks, branches, loops, or executable statements in this range.

The range starts inside an endpoint DPA power-allocation register definition: line 51418 is only the mask for `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_2`, while its comment and shift definition are in the previous chunk. It then covers endpoint PCIe control/status field maps, two RCC downstream/downstream-port address blocks, and a large MSI-X table sequence. The range ends inside `PCIEMSIX_VECT230_ADDR_HI`: the `_SHIFT` is present at line 54381, while the matching `_MASK` is on line 54382 in the next chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 hardware interface. For each named hardware register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to extract or pack the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or compose the field.

The companion `nbio_4_3_0_offset.h` header supplies the matching register offsets and base indices. Runtime driver code combines the offsets and masks through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

This particular chunk describes PCIe endpoint behavior for NBIO/RCC device 0 function group `DEV0_1`, downstream port decode fields, downstream-port PCIe error/link/power-management fields, and the start of a large MSI-X vector table. It is hardware metadata rather than policy code.

## Important Macro Families

The `RCC_EP_DEV0_1_*` endpoint families at the start of the chunk expose PCIe endpoint capability and control fields:

- `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_[2-7]` defines 8-bit dynamic power allocation substate power values. The chunk contains only the mask for substate 2, then complete shift/mask pairs for substates 3 through 7.
- `RCC_EP_DEV0_1_EP_PCIE_PME_CONTROL` defines the `PME_SERVICE_TIMER` field.
- `RCC_EP_DEV0_1_EP_PCIEP_RESERVED` maps a full-width reserved value.
- `RCC_EP_DEV0_1_EP_PCIE_TX_CNTL` defines transmit-side override and TPH-disable bits: `TX_SNR_OVERRIDE`, `TX_RO_OVERRIDE`, and `TX_F[0-2]_TPH_DIS`.
- `RCC_EP_DEV0_1_EP_PCIE_TX_REQUESTER_ID` splits requester ID into function, device, and bus fields.
- `RCC_EP_DEV0_1_EP_PCIE_ERR_CNTL` defines error-reporting control, AER header-log timeout, immediate error-message send, poisoned advisory nonfatal behavior, and AER header-log timer-expired bits for functions 0 through 7.
- `RCC_EP_DEV0_1_EP_PCIE_RX_CNTL` defines receive-side ignore/disable controls for max-payload, traffic-class, completion-timeout, prefix, PASID, not-PASID unsupported-request, and TPH behavior.
- `RCC_EP_DEV0_1_EP_PCIE_LC_SPEED_CNTL` defines link-speed strap enables for Gen2, Gen3, Gen4, and Gen5.

The `nbio_nbif0_rcc_dwn_dev0_RCCPORTDEC` address block maps downstream decode registers:

- `RCC_DWN_DEV0_1_DN_PCIE_RESERVED` and `RCC_DWN_DEV0_1_DN_PCIE_SCRATCH` expose full 32-bit reserved/scratch fields.
- `RCC_DWN_DEV0_1_DN_PCIE_CNTL` includes `HWINIT_WR_LOCK`, downstream unsupported-request error-report disable, and `RX_IGNORE_LTR_MSG_UR`.
- `RCC_DWN_DEV0_1_DN_PCIE_CONFIG_CNTL` exposes the `CI_EXTENDED_TAG_EN_OVERRIDE` field.
- `RCC_DWN_DEV0_1_DN_PCIE_RX_CNTL2` exposes `FLR_EXTEND_MODE`.
- `RCC_DWN_DEV0_1_DN_PCIE_BUS_CNTL` includes immediate-PMI disable and AER completion-timeout relaxed-ordering disable.
- `RCC_DWN_DEV0_1_DN_PCIE_CFG_CNTL` controls decode to hidden registers for baseline and Gen2 through Gen5 capability spaces.
- `RCC_DWN_DEV0_1_DN_PCIE_STRAP_F0`, `STRAP_MISC`, and `STRAP_MISC2` map downstream strap state including function enable, memory-controller enable, MSI multi-message capability, clock power management, 64-bit master address support, and master completion-timeout enable.

The `nbio_nbif0_rcc_dwnp_dev0_RCCPORTDEC` address block maps downstream-port PCIe-facing fields:

- `RCC_DWNP_DEV0_1_PCIE_ERR_CNTL` provides error-reporting disable, AER header-log timeout, function-0 timer-expired, immediate error-message send, and clear bits for received correctable, nonfatal, and fatal errors.
- `RCC_DWNP_DEV0_1_PCIE_RX_CNTL` defines downstream receive ignore/disable controls for max-payload errors, traffic-class errors, completion timeout, short-prefix errors, and RCB FLR timeout.
- `RCC_DWNP_DEV0_1_PCIE_LC_SPEED_CNTL` defines Gen2 through Gen5 link-speed strap enables.
- `RCC_DWNP_DEV0_1_PCIE_LC_CNTL2` controls link-state and link-bandwidth notification disable bits.
- `RCC_DWNP_DEV0_1_PCIEP_STRAP_MISC` exposes downstream-port multi-function strap enable.
- `RCC_DWNP_DEV0_1_LTR_MSG_INFO_FROM_EP` maps a full 32-bit LTR message-info value received from the endpoint.

The `PCIEMSIX_VECT*` families dominate the chunk. Vectors 0 through 229 are complete; vector 230 is partial because of the chunk boundary. For each complete vector:

- `PCIEMSIX_VECT<n>_ADDR_LO__MSG_ADDR_LO` starts at bit 2 and masks with `0xFFFFFFFC`, reflecting the alignment of MSI/MSI-X message addresses.
- `PCIEMSIX_VECT<n>_ADDR_HI__MSG_ADDR_HI` is a full 32-bit high-address field.
- `PCIEMSIX_VECT<n>_MSG_DATA__MSG_DATA` is a full 32-bit message data field.
- `PCIEMSIX_VECT<n>_CONTROL__MASK_BIT` is bit 0, the per-vector mask control.

## APIs, Types, And Functions

There are no runtime APIs, C types, or functions in this chunk. The public interface is the generated macro namespace. The macros are untyped integer constants, mostly with an `L` suffix, and are intended for compile-time use by register access helpers.

The field macros do not encode access semantics. They identify bit positions and masks only. They do not specify whether a register is read-only, write-only, sticky, write-one-to-clear, reset-sensitive, privilege-gated, posted, side-effecting, or safe to modify while hardware is active. Those properties come from the hardware register specification and from driver code that sequences reads and writes.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. Driver code selects a register offset from `nbio_4_3_0_offset.h`.
2. The caller reads, writes, modifies, polls, or decodes the register through AMDGPU SOC15 access helpers.
3. The caller uses the `__SHIFT` and `_MASK` constants from this header to isolate or compose fields.
4. Hardware implements the resulting state transition, such as PCIe link capability exposure, AER status updates, DPA/PME behavior, downstream hidden-register decode, LTR propagation, or MSI-X interrupt routing.

Important external flows represented by this chunk include PCIe endpoint bring-up, link-speed capability strap handling, PCIe error-reporting and AER timer handling, receive/transmit policy overrides, downstream port configuration, latency tolerance reporting propagation, dynamic power allocation reporting, and MSI-X vector table programming/masking.

## State And Persistence Behavior

The header stores no software state. It names hardware-visible state in NBIO/RCC/PCIe registers. Persistence is controlled by GPU reset domains, PCIe function-level reset, suspend/resume handling, firmware initialization, strap sampling, and explicit driver writes.

Represented hardware state includes:

- DPA substate power allocation values and endpoint PME service timer configuration.
- PCIe requester ID bus/device/function fields.
- Transmit and receive policy bits for relaxed ordering, snoop behavior, TPH, PASID-related receive handling, prefix handling, completion timeout, and traffic-class errors.
- AER/error-reporting control and timer-expired/received-error status or clear bits.
- Link-speed strap enables for Gen2 through Gen5 and link notification disable controls.
- Downstream hidden-register decode enables and downstream-port strap fields.
- LTR message information received from an endpoint.
- MSI-X per-vector message address, message data, and vector mask bits.

Several fields are not ordinary retained storage. Error status and clear bits may be sticky or write-one-to-clear depending on the register contract. Strap-derived fields may be sampled at hardware initialization and may not be freely mutable later. MSI-X vector address/data/control fields directly affect interrupt delivery. Link and receive/transmit policy bits can alter PCIe protocol behavior while traffic is active.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register set:

- `nbio_4_3_0_offset.h` supplies matching register addresses and base indices, including RCC downstream registers and `PCIEMSIX_VECT*` table offsets.
- `nbio_4_3_0_sh_mask.h` supplies the field layout documented here.
- Other generated NBIO/RCC/PCIe headers provide adjacent chunks and other IP-generation layouts.

Observed include-level integration in this repository includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`

The exact macros in this chunk were not found as direct references in those implementation files during this pass, but the include relationship matters: the header is part of the shared generated register contract for NBIO 4.3.0. Nearby NBIO code in `nbio_v4_3.c` uses the same pattern of generated register offsets plus generated shift/mask macros through `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while causing the driver to touch the wrong hardware bits. Highest-risk fields in this chunk include MSI-X address/data/control, AER status/clear bits, PCIe receive/transmit policy bits, link-speed straps, hidden-register decode enables, and LTR/DPA power-management fields.
- The chunk boundaries split real register definitions. The merge lane must not interpret the lone `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_2` mask at the start or the missing `PCIEMSIX_VECT230_ADDR_HI` mask at the end as whole-file omissions.
- The MSI-X sequence is intentionally repetitive. A missing vector, incorrect low-address alignment mask, or changed control bit position would be easy to miss in review but could cause lost, misdirected, or permanently masked interrupts.
- Error-control fields include both disable bits and clear/status bits. Confusing these semantics can either suppress real PCIe errors or clear diagnostic evidence before software observes it.
- Link-speed strap and hidden-register decode bits can affect enumeration, capability exposure, and access to generation-specific PCIe configuration space. Incorrect masks can make device behavior differ from hardware straps or firmware expectations.
- Receive/transmit policy bits change how the endpoint handles completion timeouts, prefixes, PASID-related requests, TPH, relaxed ordering, and snoop behavior. Incorrect updates may create subtle I/O correctness or interoperability failures.
- Full-width reserved/scratch fields are still register-addressable; treating reserved fields as safe general storage can conflict with undocumented hardware behavior.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Missing or misspelled generated macros should be caught by consumers that include the NBIO 4.3.0 header pair.
- Run runtime probe on affected AMD GPUs and verify stable NBIO initialization, PCIe enumeration, suspend/resume, and reset behavior.
- Exercise MSI-X setup and teardown for high vector counts. Verify vector address/data programming, per-vector masking, interrupt delivery, and absence of vector aliasing across vectors 0 through at least 229.
- Exercise PCIe AER/error paths where possible. Verify correct logging, clear behavior, and no unintended suppression when error-reporting disable fields are toggled by firmware or driver code.
- Validate link capability exposure and negotiated speed for Gen2 through Gen5-capable platforms, especially after resume and reset.
- Exercise power-management paths that depend on PME, LTR, and DPA state and verify no regressions in low-power entry/exit or wake behavior.
- Use register-dump or debugfs tooling to compare `nbio_4_3_0_offset.h` addresses with these shift/mask definitions for the downstream RCC blocks and MSI-X table layout.
- For generated-header maintenance, diff this chunk against the authoritative hardware register database and adjacent NBIO generations to catch accidental vector-count, field-width, or bit-position drift.

### subset-b-002983: lines 54382-56932

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 54382-56932

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,128 preprocessor `#define` entries across 2,551 source lines. It has no C functions, structs, enums, variables, allocation, locking, or executable statements.

The range starts inside the global `PCIEMSIX_VECT230_ADDR_HI` register family, after the `MSG_ADDR_HI` shift from the previous chunk. It then completes the MSI-X vector table from the tail of vector 230 through vector 255, defines the eight MSI-X pending-bit-array registers, covers the `nbio_nbif0_rcc_strap_rcc_strap_internal` strap block, covers `nbio_nbif0_bif_rst_bif_rst_regblk` reset and lifecycle interrupt masks, and enters `nbio_nbif0_bif_misc_bif_misc_regblk`. The chunk ends inside `BIF_ATOMIC_ERR_LOG_DEV0_F1`; the remaining mask for `UR_ATOMIC_NR_DEV0_F1` and the clear masks continue after this range.

The source is declarative hardware metadata. It defines field bit positions and masks used by AMDGPU register access code in combination with `nbio_4_3_0_offset.h` and the common AMD register helper macros.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 register interface. For each hardware register field, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to extract or pack the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or compose the field.

This chunk describes several NBIO/BIF/RCC hardware surfaces:

- MSI-X message table and pending-bit-array layout for high vector numbers.
- Strap-derived PCIe/NBIF capability, identity, power-management, reset, SR-IOV, PASID/ATS/ACS/AER, MSI/MSI-X, BAR, and class-code exposure.
- Reset-control and reset-status/interrupt state for endpoint, downstream-port, PF FLR, D3hot-to-D0, power, and PF D-state transitions.
- BIF miscellaneous controls for BIOS strap override, interrupt-line state, outstanding virtual-channel allocation, DMA/GMI/HST/GSI/SDP behavior, bus-master and atomic error logs, PASID checks, performance counters, NBIF power gating, SMN master behavior, doorbell monitor vector routing, INTx/PMI behavior in low-power states, GMI WRR weights, and power-break requests.

The repository path is under a `ceph-client` mirror, but this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The first part of the range is the tail of the global `PCIEMSIX` block:

- `PCIEMSIX_VECT230_*` starts as a boundary fragment with only `ADDR_HI` mask, then `MSG_DATA` and `CONTROL`.
- `PCIEMSIX_VECT231_*` through `PCIEMSIX_VECT255_*` repeat the standard MSI-X vector pattern: `ADDR_LO__MSG_ADDR_LO` shifted by 2 and masked with `0xFFFFFFFC`, `ADDR_HI__MSG_ADDR_HI` full-width, `MSG_DATA__MSG_DATA` full-width, and `CONTROL__MASK_BIT` at bit 0.
- `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` expose full-width `MSIX_PENDING_BITS` fields. Together they represent 256 pending MSI-X bits.

The `rcc_strap_internal` block is strap-oriented configuration metadata:

- `RCC_STRAP1_RCC_DEV0_PORT_STRAP0` through `STRAP14` define device-0 downstream-port identity and PCIe capability exposure. Fields cover device/vendor/subsystem IDs, ARI/ACS/AER, completion-abort handling, interrupt pin, E2E prefix handling, payload/link-width support, ECRC generation/checking, error reporting, Gen2/Gen3/Gen4/Gen5 capability and compliance, L0s/L1 latency, LTR, MSI, timeout behavior, OBFF, lane-equalization presets, PM support, atomics, power budget data, virtual channel and TPH support, 10-bit tags, no-command-completed support, target link speed, port and bus/device/function numbers, modified TS metadata, reset timing, alternate protocol details, CTO logging, DOE, and correctable-error subclass capability.
- `RCC_DEV1_PORT_STRAP*` and `RCC_DEV2_PORT_STRAP*` appear as register-family comments only in this chunk. Their field definitions are absent from the visible range.
- `RCC_STRAP1_RCC_BIF_STRAP0` through `STRAP6` define global BIF/NBIF strap controls, including Gen3/Gen4/Gen5 disable/kill bits, ROM validation, VGA and memory aperture pins, BIOS ROM enable, PX capability, MSI first-BE behavior, error-ignore policy, local-prefix behavior, VF bus-number check, Big APU mode, link-down reset, ROM strap validity, SWUS aperture sizing/prefetchability, hardware/software revision bits, link-reset policy, IOV link-reset disable, DLF, PHY 16GT/32GT enablement, margining controls, S5 access behavior, posted writes, LTR mode, GSI SMN post-write behavior, indirect access disables, link-down DMA-drop policy, power-break deglitching, ASPM/PM/L0s/L1 timers, SMN error data behavior, emergency power reduction, and power-break status timing.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*`, `RCC_STRAP1_RCC_DEV0_EPF1_STRAP*`, and `RCC_DEV0_EPF2/EPF3_STRAP*` provide endpoint-function strap fields. They cover function enablement, legacy-device type, D1/D2 support, SR-IOV VF device ID and supported page size, SR-IOV enable, 64-bit BAR disable, soft-reset behavior, resizable BAR, PASID width and permissions, MSI per-vector masking and multi-message capability, ARI/AER/ACS/ATS, completion-abort handling, DPA/DSN/VC/page request/PASID features, subsystem ID/vendor ID, poisoned advisory nonfatal behavior, power enablement, MSI/MSI-X enablement, MSI clear-pending, SMN error mask enablement, clock PM, true PM status, reset-time reporting, atomic 64-bit and atomic enablement, FLR enablement, PME support, interrupt pin, auxiliary power/current, aperture enablement, class code, and vendor ID.
- Many later endpoint-function families for `DEV0_EPF4` through `DEV2_EPF2` are present only as comments in this slice, which signals generated register names but not visible field definitions.

The `bif_rst_regblk` block defines reset and lifecycle interrupt controls:

- `HARD_RST_CTRL` and `SELF_SOFT_RST` expose reset enables and active reset bits for DSPT, endpoint, SDP port, SION always-on, strap, SWUS shadow, core, and sticky reset domains.
- `BIF_GFX_DRV_VPU_RST`, `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3` define graphics-driver/VPU reset state, reset timer and abort behavior, FLR and D3hot timing, power-gating bypass behavior, spare fields, reset interrupt enables, and reset pending masks.
- `DEV0_PF0_FLR_RST_CTRL` through `DEV0_PF3_FLR_RST_CTRL` define per-PF FLR reset participation for configuration and private reset domains, including sticky reset enablement.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` expose reset, FLR, D3hot/D0, power, and D-state interrupt status bits.
- The matching `*_INTR_MASK` registers control masking for those interrupt sources.
- `BIF_PF_FLR_RST` provides per-PF FLR reset request/state bits.
- `BIF_DEV0_PF[0-3]_DSTATE_VALUE` and `BIF_PORT0_DSTATE_VALUE` expose target and acknowledged D-state values.
- `DEV0_PF[0-3]_D3HOTD0_RST_CTRL` defines per-PF reset handling for D3hot-to-D0 transitions.

The `bif_misc_regblk` portion supplies BIF/NBIF behavior and diagnostics:

- `REGS_ROM_OFFSET_CTRL`, `NBIF_STRAP_BIOS_CNTL`, and `MISC_SCRATCH` define ROM offset, BIOS-driven strap overrides, and scratch storage.
- `INTR_LINE_POLARITY` and `INTR_LINE_ENABLE` describe legacy interrupt-line behavior for device 0.
- `OUTSTANDING_VC_ALLOC` allocates DMA and HST outstanding transaction slots across virtual channels and threshold fields.
- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` cover DMA/GMI/HST/GSI/SDP behavior, including VC4 non-DVM status, chain-lock/chain-break controls, split read stall behavior, atomic length checking, forcing VF-as-PF semantics when SR-IOV enable is low, HDP P2P direct address adjustment, SWUS selection, poison and ACS violation reporting, unsupported SDP command status, response ordering controls, BME-drop disables, request-attribute masks, and message block-level selection.
- `BIFC_BME_ERR_LOG_LB` and `BIFC_RCCBIH_BME_ERR_LOG0` log DMA or RCCBIH activity while bus master enable is low for `DEV0_F0` through `DEV0_F3`, with clear fields at bits 16-19.
- `BIFC_LC_TIMER_CTRL` defines ASPM idle and L1 exit timer scales.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `_F6_F7` define ID-based ordering, relaxed ordering, snoop/no-snoop, and block-level override fields for pairs of functions.
- `BIFC_DMA_ATTR_CNTL2_DEV0`, `BME_DUMMY_CNTL_0`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, `BIFC_PASID_STS`, `BIFC_ATHUB_ACT_CNTL`, `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the `BIFC_PERF_CNT_*_L32BIT` registers define DMA attribute policy, dummy BME behavior, host arbitration, GSI read/write selection and PIO handling, function-level PCIe controls, PASID checking and status, SDP arbitration/disconnect behavior, ATHUB activity controls, and performance counter selection/values.
- `NBIF_REGIF_ERRSET_CTRL`, `BIFC_SDP_CNTL_2`, `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` define register-interface error set behavior, disconnect hysteresis, NBIF master/slave power-gating hysteresis/enables, idleness counting, firmware power-gating exit behavior, SHUBCLK idle hysteresis, D3-only power gating, clock permissions, refclk timing, load masking, and power-gating exit override.
- `SMN_MST_EP_CNTL3`, `SMN_MST_EP_CNTL4`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL5` control zero-byte-enable write/read behavior and all-ones error-response data behavior for endpoint PFs.
- `BIF_SELFRING_BUFFER_VID` and `BIF_SELFRING_VECTOR_CNTL` select doorbell-monitor and RAS interrupt client IDs and control doorbell-monitor interrupt/timestamp behavior.
- `NBIF_STRAP_WRITE_CTRL`, `NBIF_INTX_DSTATE_MISC_CNTL`, and `NBIF_PENDING_MISC_CNTL` control one-time strap writes, INTx/PMI behavior in D-states and non-D0 states, and pending-check bypasses for FLR master/slave paths.
- `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3` define GMI weighted-round-robin modes and weights for entries 0-7.
- `NBIF_PWRBRK_REQUEST` exposes a one-bit NBIF power-break request.
- `BIF_ATOMIC_ERR_LOG_DEV0_F0` and the beginning of `BIF_ATOMIC_ERR_LOG_DEV0_F1` expose unsupported-request atomic error causes for opcode, request-enable-low, length, and non-relaxed-request conditions, with clear fields for the complete F0 block.

## APIs, Types, And Functions

There are no runtime APIs, type declarations, or functions in this chunk. The public interface is the generated macro namespace. These constants are normally consumed with the companion offset header and helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

The macros are untyped integer constants with an `L` suffix. They encode field layout only. They do not encode read/write permissions, write-one-to-clear behavior, sticky status semantics, reset defaults, polling requirements, register access ordering, or privilege rules.

## Control Flow

This header has no local control flow. Runtime flow is external to the file:

1. AMDGPU code selects a register address from `nbio_4_3_0_offset.h`.
2. The caller reads, writes, polls, or composes the register value using the `__SHIFT` and `_MASK` constants from this header.
3. NBIO/BIF/RCC hardware implements the side effect, such as interrupt routing, pending-bit updates, strap-derived capability exposure, reset assertion/deassertion, D-state transition acknowledgement, power-gating entry/exit, error logging, PASID checking, or GMI arbitration.

Important represented flows include MSI-X setup and masking, PF/port strap interpretation during initialization, SR-IOV capability exposure, PF FLR and D3hot-to-D0 reset sequencing, reset interrupt masking/status handling, bus-master and atomic error diagnosis, power management and power-gating policy, SMN master error response behavior, doorbell-monitor/RAS interrupt routing, and performance-counter sampling.

## State And Persistence Behavior

The header stores no software state. It describes hardware state held in NBIO/BIF/RCC registers. Persistence and reset behavior depend on the GPU reset domain, strap load/reload, firmware initialization, platform policy, suspend/resume save-restore, PF/VF lifecycle, FLR, D-state transitions, and explicit AMDGPU writes.

The MSI-X vector address/data/control and PBA fields affect interrupt delivery until reprogrammed or reset. The vector mask bit suppresses delivery for one vector, while the PBA fields represent pending interrupt state.

Strap fields are generally derived from hardware straps, fuses, firmware, or BIOS override mechanisms and become the basis for PCIe capability and identity presentation. In this chunk, strap state influences device IDs, vendor/subsystem IDs, link capability, power-management support, reset timing, MSI/MSI-X capability, SR-IOV/PASID/ATS/ACS/AER exposure, BAR behavior, aperture support, and class codes.

Reset and D-state registers represent transition state. Some bits enable participation of reset domains; status/mask registers report or suppress reset-related interrupts; target/acknowledge D-state fields reflect ongoing device and port power-state transitions.

Miscellaneous BIF controls are a mix of persistent configuration, live policy, counters, and sticky diagnostic state. Error-log registers such as `BIFC_BME_ERR_LOG_LB`, `BIFC_RCCBIH_BME_ERR_LOG0`, and `BIF_ATOMIC_ERR_LOG_DEV0_F0/F1` contain status bits paired with clear bits. Performance-counter registers expose sampled low 32-bit counter values. Power-gating controls, GMI weights, and outstanding VC allocation fields can affect live traffic behavior until changed or reset.

## Dependencies And Integration Points

This chunk depends on the generated AMD NBIO 4.3.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies matching register offsets and base indices.
- Other generated NBIO headers, including default/reset-value metadata where present.
- AMDGPU register helper macros that assume the generated `__SHIFT` and `_MASK` naming convention.

Observed include-level integration for the NBIO 4.3.0 header set in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, SMU 13.0.0/13.0.7 power-management files, and DCN 3.2 display resource files. Semantically, these masks integrate with Linux PCI/PCIe, MSI/MSI-X, SR-IOV, AER, ACS, ATS, PASID/IOMMU, power-management, reset, and interrupt-handling paths.

## Risks And Edge Cases

- The chunk starts inside `PCIEMSIX_VECT230_ADDR_HI`; the paired shift for `MSG_ADDR_HI` is outside this range. The final merge lane must not treat vector 230 as a complete vector definition from this chunk alone.
- The chunk ends inside `BIF_ATOMIC_ERR_LOG_DEV0_F1`; the `UR_ATOMIC_NR_DEV0_F1` mask and clear masks continue in the next chunk. Consumers and final research must reconcile that boundary.
- Generated strap definitions are broad and high-impact. A wrong mask can misrepresent PCIe identity, SR-IOV, PASID/ATS, AER/ACS, MSI/MSI-X, BAR sizing, or link capability without causing a compile failure.
- Many reset and interrupt fields differ only by PF index or event type. Mixing FLR, D3hot/D0, power, PF D-state, and instance-reset fields can cause missed interrupts, stuck reset state, or reset of the wrong domain.
- Status/clear pairs in BME and atomic error logs use low bits for status and bits 16-19 for clear requests. Treating them as ordinary read-modify-write storage can accidentally clear diagnostic evidence.
- MSI-X address low fields intentionally mask off low alignment bits. Treating the field as a raw byte address can corrupt vector programming.
- Strap comments for many devices/functions appear without field definitions in this slice. A report or tooling pass should distinguish present macros from comment-only register names.
- Power-gating, D-state, and link-management bits can affect device reachability and timing. Incorrect writes may surface as hangs, lost interrupts, or resume/reset regressions rather than immediate register-access faults.
- Performance-counter and arbitration fields influence observation and traffic scheduling; bad masks can lead to misleading diagnostics or unfair/incorrect traffic weighting.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage of AMDGPU code that includes the NBIO 4.3.0 headers. Missing or malformed generated macros should fail compilation in direct consumers.
- Generated-header consistency checks against the authoritative NBIO 4.3.0 register database, including offset-to-mask pairing with `nbio_4_3_0_offset.h`.
- Pattern checks that complete MSI-X vector definitions from `PCIEMSIX_VECT231` through `PCIEMSIX_VECT255` all have the expected four-register field pattern and masks.
- Boundary checks that vector 230 is completed by the previous chunk and `BIF_ATOMIC_ERR_LOG_DEV0_F1` is completed by the next chunk.
- Strap decode validation against expected PCIe configuration space: vendor/device/subsystem IDs, class codes, link capabilities, MSI/MSI-X, SR-IOV, PASID, ATS, ACS, AER, BAR, and power-management capability exposure.
- Runtime reset tests that exercise PF FLR, D3hot-to-D0, power, and PF D-state transitions while checking status and mask behavior.
- MSI-X tests that program high-numbered vectors 231-255, toggle per-vector masks, inspect PBA bits, and confirm interrupt delivery and quiescing.
- Error-path tests that force or observe bus-master-low and unsupported atomic conditions, then verify status and clear bits for `BIFC_BME_ERR_LOG_LB`, `BIFC_RCCBIH_BME_ERR_LOG0`, and `BIF_ATOMIC_ERR_LOG_DEV0_F0/F1`.
- Power-management and resume tests that cover NBIF power-gating hysteresis, clock permission, refclk cycle, power-break, INTx/PMI-in-D-state, and pending-check controls.
- Performance-counter and arbitration diagnostics that verify BIFC counter selection/value fields and GMI WRR weight fields decode as expected on supported hardware.

### subset-b-002984: lines 56933-59410

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 56933-59410

## Scope

This chunk is a generated AMD NBIO 4.3.0 shift/mask header segment. It contains 2,133 C preprocessor definitions and address-block comments, but no functions, structs, or executable control flow. The exported `*_SHIFT` and `*_MASK` constants describe bitfield layouts for NBIF/BIF/RCC/RAS/PCIe registers. Runtime code pairs these field definitions with the corresponding register offsets from `nbio_4_3_0_offset.h` and with AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

The chunk begins in the middle of `BIF_ATOMIC_ERR_LOG_DEV0_F1`, covers the full `DEV0_F2` and `DEV0_F3` atomic-error definitions, and ends partway through `BIF_BX_PF1_GPU_HDP_FLUSH_DONE`. The merge lane should preserve this boundary context because the first and last logical register records are split across neighboring chunks.

## Purpose

The file gives AMDGPU code a compile-time map from NBIO register fields to bit positions. In practice, this chunk supports:

- decoding and clearing PCIe atomic, PASID, DMA, BME, RAS, and doorbell error status bits;
- programming NBIF virtual-wire behavior, low-power clock/deep-sleep controls, early wakeup, and pool-credit allocation;
- configuring RCC PCIe endpoint/downstream behavior including straps, DPA, LTR, link speed, requester IDs, SR-IOV regioning, GPUIOV, peer windows, and host bus numbering;
- controlling `BIF_BX1` MMIO indirection, BIOS/driver/FW scratch registers, interrupt routing, doorbells, frame-buffer access, VF permissions, remap LUTs, ring-buffer state, MP1/VCN/GFX/SDMA IOV sizing, pads, S5 power state registers, and PF1 coherency/flush surfaces.

Because this is generated hardware metadata, the principal semantics are in the names and bit layouts. A wrong value here compiles cleanly but can program the wrong hardware bit.

## Register Families Covered

### Error and PASID logs

The first section defines status and clear bits for `BIF_ATOMIC_ERR_LOG_DEV0_F2` and `BIF_ATOMIC_ERR_LOG_DEV0_F3`, continuing from `DEV0_F1`. Each function gets four error status bits for unsupported atomic opcode, request-enable-low, length, and non-relaxed/non-routing conditions, plus matching clear bits at positions 16-19. `BIF_DMA_MP4_ERR_LOG` adds MP4SDP VC4 non-DVM and atomic request-enable-low errors with matching clear bits. `BIF_PASID_ERR_LOG` and `BIF_PASID_ERR_CLR` expose one bit per function F0-F3.

These fields integrate with PCIe/ATS/PASID handling paths. They are read for diagnosis and written through clear masks after logging or recovery. Clear fields are write-sensitive; using a combined value without preserving the intended clear mask can acknowledge more events than intended.

### Virtual-wire, clock, and power controls

`NBIF_VWIRE_CTRL` defines SMN and SDP virtual-wire disable bits, reset delay counts, posted behavior, and SDP block level. `NBIF_SMN_VWR_*` and `NBIF_SDP_VWR_*` groups define ten set-indexed voltage-change disable, reset-default, trigger, write-trigger, differential-detect, and value fields. These are dense one-bit-per-set maps and are likely used by platform power/reset sequencing rather than hot-path command submission.

`NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK` define LCLK medium-grain clock-gating and deep-sleep control fields such as enable bits, delay counters, dynamic gating selectors, target-unit IDs, hysteresis, and software-forced clock request behavior. `BIFC_EARLY_WAKEUP_CNTL` provides early wakeup control from client activity, deep-sleep exit, and AER activity.

### SMN master and SHUB timeout detector

`SMN_MST_CNTL0`, `SMN_MST_EP_CNTL1`, and `SMN_MST_EP_CNTL2` expose SMN master flow-control and timeout behavior, including NACK-on-consumer-initiated bits, timeout select, soft reset, valid signal, pending request, posted write pending, response pending, and timeout status. `NBIF_SHUB_TODET_*` groups define timeout-detector enable/disable behavior, client status, sync-flood controls, and second-bank variants. These fields feed reset, error containment, and system-fabric timeout diagnosis.

### BIFC credits, counters, and RAS

The `BIFC_*_POOLCRED_ALLOC` groups encode virtual-channel allocation nibbles for HRP/SDP/GMI/SST request, data, and response pools. `DISCON_HYSTERESIS_HEAD_CTRL` stores upstream/downstream SDP disconnect hysteresis. `BIFC_PERF_CNT_*_H16BIT` defines upper 16-bit fields for MMIO and DMA read/write performance counters.

The `BIFL_RAS_*` groups under `nbio_nbif0_bif_ras_bif_ras_regblk` define central RAS controls/status and four leaf control/status register pairs. Leaf controls include error-event detection, poison and parity handling, receive-error events, generated/propagated egress stalls, RAS interrupt enables, and MCA logging selects. Status fields expose received error events, poison/parity detection, generated events, and propagated stall state. `BIFL_IOHUB_RAS_IH_CNTL` and `BIFL_RAS_VWR_FROM_IOHUB` connect this RAS block to interrupt-handler and virtual-wire paths.

### RCC PCIe and GPUIOV controls

The `RCC_DWN_DEV0_2_*`, `RCC_DWNP_DEV0_2_*`, and `RCC_EP_DEV0_2_*` blocks mirror PCIe downstream/downstream-port/endpoint controls for device 0 instance 2. They include reserved and scratch fields, hardware-init write locks, unsupported-request reporting disables, LTR handling, extended-tag overrides, FLR extension mode, PMI/AER completion timeout controls, hidden config decoding by generation, strap controls, AER error-reporting controls, link speed enables for Gen2 through Gen5, link-bandwidth notifications, multifunction straps, endpoint interrupt enable/status bits, LTR transmit policy, DPA capability/latency/power-allocation registers, PME service timer, TX requester ID, TPH controls, and PASID-related RX ignore controls.

The `RCC_DEV0_1_*` and `RCC_DEV0_2_*` groups configure broader RCC behavior: SR-IOV invalid-register-access interrupt enable, BACO request disable bits, doorbell aperture reset enable, vendor-defined message routing support, link margining capabilities, GPUIOV region/HostVM enablement, console IOV mode and VF stride/offset, peer register ranges, bus control/error policy, VGA config aperture sizing, XDMA bounds, feature-control error behavior, bus-number allow lists, captured host bus ID, peer framebuffer offsets and enables, device/function ID lists, link-down entry/exit, common link L1/LTR behavior, endpoint requester ID restoration, LTR switch latency, and multi-host arbitration.

### BIF_BX1 system and BIF controls

`BIF_BX1_PCIE_INDEX`, `BIF_BX1_PCIE_DATA`, `BIF_BX1_PCIE_INDEX2`, `BIF_BX1_PCIE_DATA2`, and high-index fields implement indirect PCIe register access. The many `SBIOS_SCRATCH`, `BIOS_SCRATCH`, `DRIVER_SCRATCH`, and `FW_SCRATCH` registers are full-width scratch storage surfaces shared by firmware, BIOS, and driver flows.

`BIF_BX1_GFX_MMIOREG_CAM_ADDR*` and `BIF_BX1_GFX_MMIOREG_CAM_REMAP_ADDR*` define eight programmable MMIO CAM/remap entries with enable, comparator, physical-function, and VF fields. Companion control registers select zero-completion, one-completion, and programmable completion behavior.

Core `BIF_BX1` BIF controls include straps, pinstrap status, indirect access control, bus coherency and HDP-flush stall behavior, reset enables, MM config selection, link training, interrupt controls, pad controls, feature misc bits, HDP atomic outstanding limits, doorbell controls and doorbell/RAS interrupt bits, framebuffer read/write enables, RAS vector select, master/slave transaction-pending bitmaps for VFs, memory PHY generation select, and a 16-entry NBIF graphics address LUT.

The VF access controls are especially important for SR-IOV. `BIF_BX1_VF_REGWR_EN`, `BIF_BX1_VF_DOORBELL_EN`, and `BIF_BX1_VF_FB_EN` provide one-bit-per-VF enables, while `BIF_BX1_VF_REGWR_STATUS`, `BIF_BX1_VF_DOORBELL_STATUS`, and `BIF_BX1_VF_FB_STATUS` expose the matching status. The doorbell enable register also includes a `VF_DOORBELL_RD_LOG_DIS` bit. These fields define isolation boundaries between PF-managed hardware and guest-visible VF access.

Ring-buffer, mailbox, and IOV sizing fields appear in `BIF_BX1_BIF_RB_CNTL`, `BIF_BX1_BIF_RB_BASE`, `BIF_BX1_BIF_RB_RPTR`, `BIF_BX1_BIF_RB_WPTR`, `BIF_BX1_BIF_RB_WPTR_ADDR_HI/LO`, `BIF_BX1_MAILBOX_INDEX`, `BIF_BX1_BIF_MP1_INTR_CTRL`, and `BIF_BX1_BIF_VCN0/VCN1/GFX_SDMA_GPUIOV_CFG_SIZE`. The pad-control groups cover PERSTB, PX_EN, REFPADKIN, CLKREQB, PWRBRK, WAKEB, and VAUX_PRESENT GPIO characteristics. `BIF_BX1_PCIE_PAR_SAVE_RESTORE_CNTL` and S5 memory-power fields support save/restore and low-power state bookkeeping.

### BIF_BX PF1 controls

The final section starts `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`. `BIF_BX_PF1_BIF_BME_STATUS` exposes DMA-on-BME-low status plus clear. `BIF_BX_PF1_BIF_ATOMIC_ERR_LOG` repeats the atomic unsupported-request status/clear pattern for PF1. Doorbell self-ring GPA aperture base high/low and control fields define enable, mode, and size. HDP coherency flush, flush-only, and invalidate-only controls each expose an address trigger bit.

`BIF_BX_PF1_GPU_HDP_FLUSH_REQ` defines a 32-bit engine bitmap for CP0-CP9, SDMA0-SDMA1, and reserved engines 0-19. The chunk ends in the corresponding `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` shifts, which continue in the next chunk. Consumers request an HDP flush by setting an engine bit and poll the matching done bit. Any mismatch between request and done masks can deadlock waits or skip required cache coherency.

## Important APIs, Types, and Functions

This header does not declare C APIs or types. Its effective API is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit position used to shift an unmasked field value;
- `REGISTER__FIELD_MASK`: bit mask used to isolate or update a field;
- address-block comments such as `nbio_nbif0_rcc_dev0_BIFDEC1` and `nbio_nbif0_bif_bx_SYSDEC`, which document the hardware decode region for nearby fields.

AMDGPU code normally consumes these macros through helper macros rather than by open-coding bit arithmetic. A typical write pattern is to read a 32-bit register, use `REG_SET_FIELD(value, REGISTER, FIELD, new_value)`, then write it back through the correct SOC15/PCIe accessor. A typical read path uses `REG_GET_FIELD(value, REGISTER, FIELD)`.

## Control Flow

There is no local control flow. Runtime control flow lives in consumers:

1. Select the correct hardware IP instance, register address, and access path.
2. Read the 32-bit register value, or construct a write-only clear/request value.
3. Use the matching `*_SHIFT` and `*_MASK` macros to isolate, update, or encode a field.
4. Write the register back, or write a clear/request bit.
5. For status paths, poll or check the matching status/done bit and handle timeout/error reporting.

The main control-flow risk is pairing a field macro from this chunk with the wrong register offset or wrong instance namespace. Many names differ only by `DEV0_1`, `DEV0_2`, `BIF_BX1`, `BIF_BX_PF1`, `F0`, `F1`, `F2`, or `F3`.

## State and Persistence Behavior

The macros do not store state. The hardware registers they describe do:

- error-log and RAS status registers latch events until cleared;
- clear bits acknowledge or drop latched events;
- scratch registers persist platform/firmware/driver state across parts of initialization or reset flows, depending on reset domain;
- strap and pinstrap fields reflect boot-time hardware configuration;
- VF enable/status bitmaps persist access policy until PF software or reset changes them;
- doorbell aperture, GPUIOV, peer FB offset, LUT, mailbox, ring-buffer, and XDMA fields persist address translation or communication state programmed by the driver;
- HDP flush request/done bits represent transient coherency handshakes;
- S5 and save/restore registers support low-power or resume sequencing.

Write ordering matters for stateful hardware. Doorbell apertures, VF permissions, and peer/LUT translations should be programmed before enabling guest or engine access. Flush requests should be followed by done-bit checks before assuming host/device memory coherency.

## Dependencies and Integration Points

The direct generated-header dependency is the matching NBIO 4.3.0 offset header. Without the correct offset symbol, the shift/mask pair does not identify a register by itself. Runtime dependencies include AMDGPU SOC15 and PCIe register accessors, register field helpers, SR-IOV setup paths, NBIO initialization, power-management flows, RAS/error handlers, HDP flush code, doorbell setup, and firmware/BIOS handoff code.

The source tree path places this under `drivers/gpu/drm/amd/include/asic_reg/nbio`, so it is an AMDGPU hardware-definition layer, not Ceph logic despite the surrounding repository prefix. It integrates upward into AMDGPU NBIO/BIF source files and indirectly into DRM device bring-up, reset, suspend/resume, virtualization, and error recovery.

## Risks

- Split logical records: this chunk starts after the first fields of `BIF_ATOMIC_ERR_LOG_DEV0_F1` and ends before the `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` masks. Reconciliation must merge with neighboring chunks for complete per-register coverage.
- Generated macro drift: manual edits can desynchronize `*_SHIFT` and `*_MASK`, or desynchronize this file from `nbio_4_3_0_offset.h`.
- Namespace confusion: similar fields exist across function, PF, BIF_BX, RCC, and device-instance namespaces. Compile-time type checking will not catch a wrong-but-existing macro.
- Write-one-to-clear hazards: atomic, DMA, PASID, BME, doorbell, and RAS clear fields can acknowledge hardware events unintentionally if broad masks are written.
- Virtualization isolation risk: incorrect VF register-write, doorbell, or framebuffer enable masks can expose PF or peer resources to a VF, or break guest operation.
- Coherency risk: wrong HDP flush request/done bits can leave CPU/GPU memory views stale or cause waits on a done bit that never changes.
- Power/reset risk: virtual-wire, clock-gating, deep-sleep, DPA, LTR, PME, and S5 fields affect sequencing. Incorrect values can produce resume failures, link instability, or lost error signaling.
- Performance-counter and pool-credit fields are compact nibbles/halfwords; off-by-one shifts can silently corrupt multiple virtual-channel allocations or counter reads.

## Test Signals

Useful validation signals for this chunk are mostly generated-header and hardware-integration checks:

- Compile AMDGPU users with `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h` included together; any renamed or missing macro should fail at build time.
- Run generated-header consistency checks that every `*_MASK` matches its `*_SHIFT` width and that every field belongs to the expected register family.
- Compare the generated definitions against AMD's authoritative NBIO 4.3.0 register database, especially split-boundary records and repeated VF bitmaps.
- Exercise AMDGPU probe, suspend/resume, BACO/reset, SR-IOV enable/disable, and GPU reset flows on matching ASICs.
- Validate doorbell programming and VF isolation with SR-IOV guests: VF register-write, doorbell, and framebuffer permissions should match the intended PF policy.
- Trigger or inspect RAS, PASID, atomic, BME, and DMA error paths and confirm status bits are logged and clear bits clear only the intended events.
- Exercise HDP flush paths from CP and SDMA engines; request bits should be followed by matching done bits without timeout, and memory coherency tests should pass.
- Inspect low-power/link behavior: LCLK gating, deep sleep, LTR, DPA, PME, S5 save/restore, and virtual-wire sequencing should not regress resume, link training, or AER reporting.

### subset-b-002985: lines 59411-61872

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 59411-61872

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header range. It contains C preprocessor constants, not executable functions. Each hardware field is represented as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro; consumers combine these with register offsets from `nbio_4_3_0_offset.h` and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

The range starts at the tail of the PF1 HDP flush-done register masks, then covers PF1 BIF transaction/mailbox registers, the `nbio_nbif0_rcc_strap_BIFDEC1` strap block, GDC DMA/HST SION scheduling blocks, S2A doorbell routing entries, GDC clock/reset/RAS controls, and the beginning of the `PSWUSCFG0_1` PCIe configuration-space mirror through `LINK_STATUS`.

## Purpose

These macros define the bit-level ABI between NBIO v4.3.0 driver code, firmware-owned policy, and NBIO/PCIe hardware. The fields in this chunk support:

- Per-engine HDP flush completion status for PF1, covering CP0-CP9, SDMA0-1, and reserved engine bits.
- PF1 BIF transaction pending status, address-LUT bypass, and mailbox transmit/receive handshakes.
- Strap-derived PCIe/NBIF behavior including link-generation disable/kill bits, ASPM/LTR timers, power break timing, error ignore policy, ARI/ACS/AER/ATS/PASID/SR-IOV capabilities, BAR sizing, GPUIOV VSEC sizing/revision, reset timing, and endpoint/root-port identity fields.
- GDC DMA and host SION arbitration tables for request/data/read-response/write-response burst targets, time slots, and pool-credit allocation.
- S2A doorbell entry routing for ports 0-15, including enable, AWID, range offset/size, and high address nibble selection.
- GDC clock gating, power-gating, reset, SDP port reset, ATDMA, and RAS leaf controls/status.
- PCIe type-1 configuration registers for PSWUSCFG0, including command/status, bridge bus/window registers, PM capability, PCIe device/link capability/control/status fields.

Because this is generated hardware metadata, correctness is mostly about exact macro names, masks, shifts, generation pairing, and register ownership. Many fields represent straps or firmware-programmed state and should not be treated as ordinary scratch registers.

## Important Macro Families

PF1 BIF status and mailbox:

- Lines 59411-59452 finish `BIF_BX_PF1_GPU_HDP_FLUSH_DONE`; masks map flush completion bits for CP0-CP9, SDMA0-1, and reserved engines 0-19. This mirrors the PF0 flush-done family used by `nbio_v4_3_hdp_flush_reg`, but this chunk is specifically the PF1 register family.
- `BIF_BX_PF1_BIF_TRANS_PENDING` exposes master and slave transaction-pending bits.
- `BIF_BX_PF1_NBIF_GFX_ADDR_LUT_BYPASS` exposes a one-bit LUT bypass control.
- `BIF_BX_PF1_MAILBOX_MSGBUF_TRN_DW0..3` and `RCV_DW0..3` are full 32-bit message buffer words.
- `BIF_BX_PF1_MAILBOX_CONTROL` provides transmit valid/ack and receive valid/ack bits; `BIF_BX_PF1_MAILBOX_INT_CNTL` enables valid/ack interrupts.
- `BIF_BX_PF1_BIF_VMHV_MAILBOX` is a compact VM/HV mailbox with transmit/receive 4-bit data fields plus valid, ack, and interrupt enable bits.

RCC BIF strap block:

- `RCC_STRAP2_RCC_BIF_STRAP0..6` describe NBIF/PCIe strap policy for Gen3/Gen4/Gen5 disable and kill bits, ROM/VGA/audio presence, PX capability, PME compliance, MSI payload behavior, error-ignore controls, local prefix handling, big-APU mode, link-down reset, ECRC, margining, SWUS aperture settings, DLF, 16 GT/s and 32 GT/s PHY enablement, power-break deglitch timing, VLINK L0s/L1/LDN timers, emergency power reduction, and ASPM/LTR interlocks.
- Multi-bit timer fields such as `STRAP_VLINK_ASPM_IDLE_TIMER`, `STRAP_VLINK_PM_L1_ENTRY_TIMER`, `STRAP_VLINK_L0S_EXIT_TIMER`, `STRAP_VLINK_L1_EXIT_TIMER`, and `STRAP_VLINK_LDN_ENTRY_TIMER` are programming surfaces for link power-management policy.
- `nbio_v4_3_program_aspm()` in the implementation actively programs the related `RCC_STRAP0` generation of these BIF strap timers; this `RCC_STRAP2` family is a parallel strap address block with the same class of semantics.

Device 0 port straps:

- `RCC_STRAP2_RCC_DEV0_PORT_STRAP0..14` encode downstream/root-port identity and PCIe capability advertisement: device/vendor/subsystem IDs, ARI/ACS/AER, completion abort behavior, interrupt pin, max payload, max link width, modified TS support, RTR timing, alternate protocol details, class of timeout/logging support, ECRC generation/checking, extended tags, virtual channels, L0s/L1 acceptable/exit latency, LTR/OBFF/power-management support, atomic support, power-budget table bytes, ACS capability bits, 10-bit tag support, 16 GT/s and 32 GT/s equalization presets, target link speed, port number, bus/device/function numbers, and revision IDs.
- These strap fields are source-of-truth inputs for how hardware exposes PCIe bridge/root-port capability, so changing them can alter OS-visible PCI configuration behavior.

Device 0 endpoint function straps:

- `RCC_STRAP2_RCC_DEV0_EPF0_STRAP*` defines endpoint function 0 identity, SR-IOV, ATS/PASID/page-request, BAR, MSI/MSI-X, DPA/DSN/VC, FLR, PME, resize BAR, GPUIOV, and reset timing fields.
- Notable virtualization fields include `STRAP_SRIOV_EN_DEV0_F0`, `STRAP_SRIOV_VF_DEVICE_ID_DEV0_F0`, `STRAP_SRIOV_SUPPORTED_PAGE_SIZE_DEV0_F0`, `STRAP_SRIOV_TOTAL_VFS_DEV0_F0`, `STRAP_VF_DOORBELL_APER_SIZE_DEV0_F0`, `STRAP_VF_MEM_AP_SIZE_DEV0_F0`, `STRAP_VF_REG_AP_SIZE_DEV0_F0`, `STRAP_SRIOV_VF_MAPPING_MODE_DEV0_F0`, and `STRAP_VF_REG_PROT_DIS_DEV0_F0`.
- Address-translation fields include ATS enable, ATS invalidate queue depth, ATS page-aligned request, PASID enable, maximum PASID width, page request enable, and PASID permission/global-invalidate/private-mode support.
- `RCC_STRAP2_RCC_DEV0_EPF1_STRAP*` provides a smaller endpoint function 1 family with identity, capability, MSI/MSI-X, AER/ACS/ATS/PASID, and BAR/cacheline/class-code style fields. Empty comment-only placeholders for EPF1 straps 20-25 indicate generated register headings without bit definitions in this chunk.

GDC DMA/HST SION scheduling:

- `GDC_DMA_SION_CL0..CL3_*` and `GDC_HST_SION_CL0..CL2_*` define repeated 64-bit register pairs for `RdRsp_BurstTarget`, `RdRsp_TimeSlot`, `WrRsp_BurstTarget`, `WrRsp_TimeSlot`, `Req_BurstTarget`, `Req_TimeSlot`, and pool-credit allocation.
- Each low/high pair exposes a full 32-bit field at shift 0. Together they represent 64-bit scheduling, credit, or time-slot bitmaps/values for client classes.
- `GDC_DMA_SION_CNTL_REG0/1` and `GDC_HST_SION_CNTL_REG0/1` expose SION glue clock soft-overrides and control fields for the DMA and host paths.

Doorbell, GDC control, and reset/RAS:

- `S2A_DOORBELL_ENTRY_0_CTRL` through `S2A_DOORBELL_ENTRY_15_CTRL` repeat the same five fields per port: enable, AWID, range offset, range size, and high address bits. `nbio_v4_3.c` programs entries 0, 1, 2, 3, 4, and 5 for graphics, IH, SDMA, and VCN doorbell routing.
- `S2A_DOORBELL_COMMON_CTRL_REG` provides common S2A doorbell policy outside the per-entry routing fields.
- `GDC1_SHUB_REGS_IF_CTL`, `GDC1_NGDC_MGCG_CTRL`, `GDC1_NBIF_GFX_DOORBELL_STATUS`, `GDC1_ATDMA_MISC_CNTL`, `GDC1_S2A_MISC_CNTL`, `GDC1_NGDC_EARLY_WAKEUP_CTRL`, `GDC1_NGDC_PG_MISC_CTRL`, `GDC1_NGDC_PGMST_CTRL`, and `GDC1_NGDC_PGSLV_CTRL` cover GDC register-interface, medium-grain clock gating, doorbell status, ATDMA, S2A, early wakeup, and power-gating controls.
- `GDCSOC_ERR_RSP_CNTL`, `GDCSOC_RAS_CENTRAL_STATUS`, `GDCSOC_RAS_LEAF*_CTRL`, `GDCSOC_RAS_LEAF*_STATUS`, and leaf-2 misc controls define RAS/error-response enable, injection, interrupt, and status surfaces for GDC SOC leaves.
- `SHUB_PF_FLR_RST`, `SHUB_GFX_DRV_VPU_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, `SHUB_SOFT_RST_CTRL`, and `SHUB_SDP_PORT_RST` define reset controls for PF FLR, graphics-driver/VPU reset, link reset, hard/soft reset, and SDP port reset.
- `HST_CLK0_SW0_CL0_CNTL` and `HST_CLK0_SW1_CL0_CNTL` are system-hub direct clock controls.

PSWUSCFG0_1 PCIe configuration-space mirror:

- `PSWUSCFG0_1_VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, class-code, cache-line, latency, header, and BIST macros define standard PCI identity/header fields.
- `PSWUSCFG0_1_COMMAND` and `STATUS` define I/O, memory, bus-master, parity, SERR, interrupt disable, capability-list, interrupt, error, and devsel status bits.
- Bridge-window registers include primary/secondary/subordinate bus numbers, I/O base/limit, memory base/limit, prefetchable base/limit upper/lower fields, ROM base address, and interrupt line/pin.
- Capability-list macros include a vendor capability list, adapter ID, PM capability/list/status-control, and PCIe capability/list registers.
- `PSWUSCFG0_1_DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` expose max payload/read request, relaxed ordering, extended tag, phantom functions, no-snoop, AUX power, error-reporting enables/status, FLR capability, slot power fields, and transaction-pending status.
- `PSWUSCFG0_1_LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` define link speed/width, ASPM/power-management support, common clock, retrain/link disable, bandwidth interrupt enables/status, DL active, slot clock, and current negotiated link state.

## Control Flow and Runtime Use

There is no local control flow in this header. Runtime behavior comes from NBIO v4.3.0 code and firmware paths that include this mask header with the matching offset header.

Key in-tree flows connected to this chunk:

1. `amdgpu_discovery.c` selects `nbio_v4_3_funcs` or `nbio_v4_3_sriov_funcs` for NBIO IP 4.3 devices and installs `nbio_v4_3_hdp_flush_reg`.
2. `nbio_v4_3_hdp_flush_reg` uses the generated HDP flush-done masks for CP and SDMA engines. That object currently references the PF family, while this chunk exposes the PF1-specific equivalent at the start of the range.
3. `nbio_v4_3_sdma_doorbell_range()`, `nbio_v4_3_vcn_doorbell_range()`, `nbio_v4_3_gc_doorbell_init()`, and `nbio_v4_3_ih_doorbell_range()` read/modify/write `S2A_DOORBELL_ENTRY_*_CTRL` registers using the per-port fields defined in this chunk.
4. `nbio_v4_3_update_medium_grain_clock_gating()` and `nbio_v4_3_update_medium_grain_light_sleep()` use other NBIO v4.3 masks for BIF clock/light-sleep controls; the GDC clock-gating and SION soft-override fields in this chunk are adjacent integration surfaces for lower-level GDC/SION power behavior.
5. `nbio_v4_3_program_aspm()` programs related BIF strap and PCIe link control registers to configure ASPM/LTR behavior. The `RCC_STRAP2` BIF/port strap families in this chunk describe the same PCIe capability and timing domain for another address block.
6. `nbio_v4_3_init_registers()` clears a no-soft-reset strap bit for IP 4.3.0 using generated RCC strap macros; the EPF strap families in this chunk contain parallel no-soft-reset, FLR, VF reset, D3hot-to-D0, and RTR timing fields.
7. `nbio_v4_3_set_reg_remap()` and the doorbell functions distinguish bare-metal and SR-IOV behavior. That lines up with the SR-IOV, VF BAR, VF mapping, VF protection, and GPUIOV strap fields in this range.
8. `nbio_v4_3_set_ras_err_event_athub_irq_state()` and related RAS hooks manage NBIO RAS interrupt routing using generated masks outside this exact chunk; this chunk contributes GDC SOC RAS leaf control/status fields for the GDC-side error-reporting surface.
9. SMU13 power-management code includes `nbio_4_3_0_offset.h` and this mask header, so power/ASPM/PPT paths may rely on the same generated bitfields even when they are not touched by `nbio_v4_3.c` directly.

Many fields in this chunk are not directly manipulated by the searched in-tree C implementation. The strap, SION scheduling, PF1 mailbox, PSWUSCFG0 bridge config, and several GDC reset/RAS fields are likely consumed by firmware, silicon initialization scripts, debug tooling, or future driver paths. They still form ABI documentation for those MMIO/config registers.

## State and Persistence Behavior

The header stores no software state. It describes hardware MMIO, strap, and PCIe configuration state that persists until reset, power-domain loss, firmware reprogramming, suspend/resume reinitialization, FLR, or explicit driver writes.

Important persistent state represented here:

- HDP flush-done bits are live completion state used to determine whether CPU-visible memory flushes for CP/SDMA clients have completed.
- PF1 transaction-pending and mailbox control bits are synchronization state; valid/ack and interrupt-enable fields can be edge/level sensitive depending on hardware behavior and should be updated with handshake discipline.
- Strap registers encode boot/firmware policy for PCIe capability exposure. Mutating strap-derived fields at runtime can change advertised capability, reset timing, BAR sizing, SR-IOV exposure, ATS/PASID support, or link power behavior.
- SION scheduling registers hold arbitration/credit policy for GDC DMA and host paths. Bad values can throttle or starve request/response classes.
- Doorbell entry controls define which doorbell ranges reach which hardware clients. These values must match `adev->doorbell` allocation and client ring setup.
- GDC reset controls and SDP port reset fields represent destructive state transitions; writes can reset SHUB/GDC paths, links, or ports.
- GDC RAS controls/status registers are error-detection, interrupt, and status state. Status bits may be sticky until explicitly cleared by the appropriate RAS flow.
- PSWUSCFG0_1 fields mirror PCIe config-space state that the OS, PCI core, firmware, and device hardware may all observe. Command, bridge-window, PM, PCIe capability, device control/status, and link control/status fields can affect enumeration, routing, power management, and error reporting.

## Dependencies and Integration Points

Generated-register dependencies:

- `nbio_4_3_0_offset.h` supplies register addresses and base indices matching these masks. The same symbolic field names must be paired with NBIO 4.3.0 offsets, not copied across NBIO/PCIE generations.
- Earlier chunks of `nbio_4_3_0_sh_mask.h` define the PF0 HDP flush, BIF interrupt, doorbell aperture, PCIe link, CPM, and RCC strap families that `nbio_v4_3.c` actively uses with the same helper style.
- Later chunks continue the PSWUSCFG0_1 PCIe capability space beyond `LINK_STATUS`, including higher-speed link and lane-equalization fields.

Driver integration:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` is the principal NBIO v4.3.0 implementation consumer. It uses generated NBIO masks for HDP flush offsets, memory controller access, doorbell routing, interrupt control, ASPM/LTR, clock gating, ROM offset, register remap, SR-IOV function selection, and RAS interrupt setup.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c` binds NBIO v4.3.0 function tables and HDP flush descriptors during IP discovery.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c` include the NBIO v4.3.0 offset and mask headers, connecting these fields to SMU13 platform power-management decisions.
- Display resource code includes the NBIO v4.3.0 offset header, so display/IP discovery code can share the same generated register namespace even when it does not include this mask header directly.
- SR-IOV integration is explicit: bare-metal and SR-IOV NBIO function tables differ for doorbell setup, while the strap fields in this chunk define SR-IOV/VF identity and mapping policy.

## Risks and Edge Cases

- Generation mismatch is the primary risk. NBIO, NBIF, and PCIe headers contain many similarly named register families. Using NBIO 4.3.0 masks with a different offset header can silently program wrong bits.
- The chunk starts in the middle of `BIF_BX_PF1_GPU_HDP_FLUSH_DONE`. The register heading and earlier shift definitions are outside this chunk, so whole-register analysis needs adjacent lines.
- PF0 and PF1 HDP/mailbox fields are easy to confuse. Current `nbio_v4_3_hdp_flush_reg` uses PF-family flush masks; PF1-specific use must select the matching PF1 offset and mask set.
- Strap fields often reflect firmware/boot-time policy. Runtime writes can conflict with firmware ownership, PCI core expectations, or silicon validation assumptions.
- SR-IOV, ATS, PASID, page request, GPUIOV, and VF BAR fields affect isolation and IOMMU behavior. Incorrect advertisement or enablement can expose host/VF access bugs.
- Doorbell range offset and size fields must be consistent with allocated doorbell index space. Overlap or incorrect AWID/high-address settings can route ring writes to the wrong client.
- SION burst/time-slot/pool-credit registers are wide and repeated. Partial low/high updates can create transient inconsistent arbitration policy if hardware observes them between writes.
- Reset-control fields can be destructive and may require sequencing with clock/power gating, firmware ownership, and outstanding transactions.
- RAS leaf status/control bits may have write-one-to-clear, sticky, or interrupt side effects not visible from the macro names. Generic read/modify/write helpers must respect hardware-clearing rules.
- PSWUSCFG0_1 PCIe config fields overlap with OS PCI configuration management. Driver writes must coordinate with the PCI core and avoid changing bridge apertures, link control, or command bits behind the OS's back.

## Test and Verification Signals

Useful validation for this chunk is mostly compile coverage, register readback, and platform smoke testing:

- Build AMDGPU configurations that include `nbio_v4_3.c`, SMU13 PPT files, and the NBIO 4.3.0 generated headers; this catches missing or renamed generated macros.
- On NBIO 4.3.0 hardware, verify `nbio_v4_3_hdp_flush_reg` masks still match CP/SDMA flush completion behavior, and use PF1-specific masks only with PF1 offsets.
- Exercise SDMA, IH, GC, and VCN doorbell setup and read back `S2A_DOORBELL_ENTRY_0/1/2/3/4/5_CTRL` to confirm enable, AWID, range offset, range size, and high address fields match the programmed ring topology.
- Run SR-IOV VF smoke tests to ensure VF doorbell setup remains skipped by the SR-IOV function table while VF capability/mapping straps match expected virtualization policy.
- Validate ASPM/LTR changes with link-state telemetry and PCIe config-space reads, especially when strap timers or LTR enablement are touched.
- Check PCI enumeration and `lspci -vv` output against PSWUSCFG0_1 identity, PM, PCIe device, and link capability fields after firmware/driver initialization.
- For RAS work, inject or observe GDC/NBIO RAS events and confirm leaf status/control bits, interrupt status, and global RAS ISR behavior are consistent.
- For SION scheduling changes, use traffic stress on DMA/host paths and compare performance counters or timeout/error signals before and after programming burst target, time slot, or credit allocation fields.
- For reset-control changes, verify suspend/resume, FLR, link reset, and GPU reset paths on both bare-metal and SR-IOV configurations.

### subset-b-002986: lines 61873-64306

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 61873-64306

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, locks, allocation paths, or direct register reads/writes in this range.

The slice starts at the final `PSWUSCFG0_1_LINK_STATUS` mask bit, then covers most of the `PSWUSCFG0_1` PCIe capability and extended-capability field layout. It includes PCIe Device/Link Capability 2, MSI, subsystem ID, vendor-specific, virtual channel, AER, secondary PCIe, 8 GT/s lane equalization, ACS, multicast, LTR, ARI, data-link feature, 16 GT/s PHY, lane margining, and 32 GT/s PHY fields. It then switches to `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and defines the beginning of the `BIF_CFG_DEV0_RC1` root-complex PCI configuration layout from identity/header fields through ACS capability. The chunk stops at the `BIF_CFG_DEV0_RC1_PCIE_ACS_CNTL` comment; its control-field definitions are outside this work item.

Although this path sits under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bit positions for NBIO 4.3.0 PCIe configuration-space and PCIe extended-capability registers. Each hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update that field.

The matching address constants live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`. Runtime AMDGPU code combines offsets from that file with these masks through register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

## Important Macro Families

The opening `PSWUSCFG0_1` PCIe capability portion describes PCIe Device/Link Capability 2, Control 2, and Status 2 fields. Important fields include completion-timeout ranges and disable controls, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, TLP prefix support/blocking, emergency power reduction, supported link speeds, crosslink support, SKP ordered set support, downstream presence, DRS, compliance entry, transmit margin, de-emphasis, 8 GT/s equalization status, and autonomous link bandwidth status.

The `PSWUSCFG0_1` MSI and identity capability section defines capability-list linkage, MSI enable/multiple-message/64-bit/per-vector-mask/extended-data controls, MSI address/data fields, and subsystem vendor/device IDs. The two `PCIE_VENDOR_SPECIFIC` scratch dwords expose full 32-bit payload masks under a vendor-specific extended capability.

The `PSWUSCFG0_1` virtual-channel section covers the VC enhanced-capability header, port VC capability/control/status, and VC0/VC1 resource capability/control/status fields. These masks describe extended VC counts, arbitration table sizes and offsets, TC-to-VC maps, load/select controls, VC enable bits, negotiation-pending status, and max time slots.

The `PSWUSCFG0_1` AER section defines advanced error reporting capability list fields, uncorrectable status/mask/severity bits, correctable status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered uncorrectable errors include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked. Correctable fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal error, correctable internal error, and header-log overflow.

The `PSWUSCFG0_1` link-training and isolation capabilities include secondary PCIe link control 3, lane error status, per-lane 8 GT/s equalization controls for lanes 0 through 15, ACS capability/control, multicast capability/control/address/receive/blocking registers, LTR capability, ARI capability/control, and data-link feature capability/status. These masks are relevant to link equalization, peer-to-peer routing restrictions, multicast routing, latency tolerance reporting, ARI function-group behavior, and DLF exchange.

The `PSWUSCFG0_1` high-speed PHY capability sections cover 16 GT/s and 32 GT/s link capabilities. The 16 GT/s block contains equalization bypass, modified TS, transmitter precoding, DRS, retimer presence, control/status, parity mismatch status for local/RTM1/RTM2 paths, and per-lane downstream/upstream TX presets for lanes 0 through 15. The 32 GT/s block similarly describes highest-rate equalization bypass, no-equalization-needed support/disable, modified TS modes, 32 GT/s equalization phase status, enhanced link behavior status, transmitter precoding state/request, and per-lane TX preset fields.

The `PSWUSCFG0_1` margining block defines the PCIe margining enhanced-capability header, port capability/status, and per-lane control/status pairs for lanes 0 through 15. Each lane uses fields for receiver number, margin type, usage model, and margin payload, mirrored by matching status fields.

After the `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` marker, the `BIF_CFG_DEV0_RC1` block defines a root-complex PCI-to-PCI bridge configuration image. It starts with vendor/device ID, command/status, class code, cache-line/latency/header/BIST, BARs, secondary/subordinate bus numbering, I/O and memory base/limit windows, prefetchable base/limit upper halves, capability pointer, ROM base, interrupt line/pin, and power-management capability/status/control.

The `BIF_CFG_DEV0_RC1` PCIe capability portion includes device, link, and slot capability/control/status fields, plus Device/Link/Slot Capability 2 and Control 2/Status 2. Important fields include payload and read-request sizing, relaxed ordering, no-snoop, extended tag, FLR, link speed/width, ASPM and clock policy, retrain/link-disable controls, slot power/indicator/hotplug fields, completion timeout, ARI forwarding, atomic operations, LTR, OBFF, emergency power reduction, 10-bit tags, TLP prefix blocking, crosslink/SKP/DRS support, and 8 GT/s equalization status.

The `BIF_CFG_DEV0_RC1` MSI, SSID, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, lane equalization, and ACS sections mirror many of the `PSWUSCFG0_1` concepts for the RC1 configuration space. The chunk fully covers RC1 AER status/mask/severity/log fields, lane 0 through lane 15 8 GT/s equalization controls, and ACS capability bits. It does not include the actual RC1 ACS control field definitions because the assigned range ends immediately after the `PCIE_ACS_CNTL` comment.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU code selects a register offset from `nbio_4_3_0_offset.h`.
2. It reads a PCIe or SOC15 register value through the AMD register access layer.
3. It extracts or composes a field using these `__SHIFT` and `_MASK` macros directly or through `REG_GET_FIELD` and `REG_SET_FIELD`.
4. It writes a control field, decodes capability/status, polls a hardware-owned bit, clears a sticky status, or reports hardware state to PCIe, power-management, display, reset, virtualization, or diagnostics code.

Direct in-tree includes of the NBIO 4.3.0 shift/mask header appear in `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`. Display resource files include the paired offset header for related NBIO addressing.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and extended-capability state owned by the GPU, platform firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SMU code.

The represented state includes capability-list topology, MSI programming, subsystem identity, virtual-channel configuration, AER status/masks/severity/logs, link equalization and lane error status, ACS routing restrictions, multicast address/blocking controls, LTR and ARI capability/control state, data-link feature state, PCIe 4.0/5.0/6.0-era PHY equalization and margining state, bridge resource windows, PM capability state, slot controls, and RC1 link/device/slot state. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some AER or link diagnostic fields may be sticky or write-one-to-clear in the underlying hardware. The generated masks do not encode reset defaults, access permissions, side effects, ordering requirements, or ownership boundaries.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 4.3.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` provides the matching register addresses.
- Any generated NBIO 4.3.0 default-value header, when present in the source tree, must remain aligned with these register and field names.
- AMDGPU register helper macros and accessors provide the actual read/modify/write mechanics.

Integration points include AMDGPU NBIO setup, SMU13 power-management policy, PCIe link training and speed policy, ASPM/LTR/OBFF configuration, MSI interrupt programming, AER diagnostics, ACS and peer-to-peer isolation, multicast routing, bridge resource-window handling, hotplug/slot status, retimer-aware equalization, 16 GT/s and 32 GT/s link tuning, lane margining diagnostics, suspend/resume, runtime power transitions, reset/FLR paths, and platform PCIe enumeration.

The fields overlap generic PCIe concepts that may also be managed by firmware and the Linux PCI core. Consumers must pair the right mask with the right NBIO instance and offset, and must respect whether the PCI core, firmware, AMDGPU, SMU, or hardware owns a particular control or status bit at a given point in time.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts with only the final `PSWUSCFG0_1_LINK_STATUS__LINK_AUTONOMOUS_BW_STATUS_MASK` line and ends at the `BIF_CFG_DEV0_RC1_PCIE_ACS_CNTL` comment before any ACS control shifts or masks.
- These are untyped preprocessor constants. A stale shift or mask can compile cleanly while decoding or programming the wrong hardware field.
- The file is mechanically generated and heavily repetitive. Lane 0-15 equalization and margining blocks are especially vulnerable to copy/generation drift, lane-number mismatch, or off-by-one field naming.
- PCIe control fields are interoperability-sensitive. Incorrect completion timeout, ARI, atomic-op, IDO, LTR, OBFF, TLP-prefix, ASPM, retrain, link-disable, target-speed, de-emphasis, or equalization programming can cause enumeration failures, DMA ordering bugs, link instability, reset failures, or platform-specific hangs.
- MSI fields carry interrupt-delivery side effects. Width, 64-bit address, extended data, mask, or multiple-message mistakes can cause lost or misrouted interrupts.
- AER status/mask/severity/log fields may be sticky or write-one-to-clear in hardware. Generic read/modify/write use can lose diagnostic evidence or leave errors masked incorrectly.
- ACS and multicast fields affect routing and isolation. Incorrect source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, or multicast blocking can break isolation or peer-to-peer traffic behavior.
- Bridge base/limit, BAR, ROM, bus-number, and prefetchable-window masks affect resource exposure. Wrong masks can confuse PCI enumeration or expose invalid apertures.
- 16 GT/s, 32 GT/s, retimer, parity, and margining fields are signal-integrity sensitive. Incorrect interpretation can hide marginal links or destabilize high-speed link training.
- `PSWUSCFG0_1` and `BIF_CFG_DEV0_RC1` names describe different address blocks. Applying a mask from one family to an offset from the other may still produce plausible bit operations while corrupting unrelated configuration state.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 support enabled; missing, renamed, or duplicate macros should surface in `nbio_v4_3.c`, SMU13 power-management files, or generated-header include paths.
- Compare this field list against `nbio_4_3_0_offset.h` to confirm the `PSWUSCFG0_1` and `BIF_CFG_DEV0_RC1` register names, ordering, and address-block transitions remain synchronized.
- Boot affected hardware and verify PCIe config-space exposure for RC1: vendor/device IDs, bridge windows, PM capability, PCIe capability, MSI, SSID, vendor-specific, VC, serial-number, AER, secondary PCIe, lane equalization, and ACS capability should decode consistently.
- Exercise PCIe link-speed changes, retraining, suspend/resume, runtime power, ASPM/LTR/OBFF policy, and reset paths while monitoring link width/speed, equalization completion, lane error status, DRS/retimer presence, and autonomous bandwidth status.
- Use MSI-enabled workloads and interrupt-stress tests to catch MSI address/data/mask or multiple-message field drift.
- Use AER injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severities, header logs, TLP prefix logs, and first-error pointers.
- Validate ACS, multicast, and peer-to-peer DMA scenarios on systems that expose those features; isolation failures, blocked traffic, or unexpected upstream forwarding can indicate mask or ownership mistakes.
- Run high-speed link diagnostics for 16 GT/s and 32 GT/s-capable platforms, including lane equalization, parity mismatch reporting, transmitter precoding, modified TS state, and lane margining readiness/status.

## Chunk Notes

- Line 61873 is only the final mask from the preceding `PSWUSCFG0_1_LINK_STATUS` block.
- Lines 61874 through the 32 GT/s lane equalization section cover a broad `PSWUSCFG0_1` PCIe endpoint/upstream-switch-style capability map.
- The `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` marker begins the `BIF_CFG_DEV0_RC1` root-complex configuration-space map within this same chunk.
- Line 64306 is only the `BIF_CFG_DEV0_RC1_PCIE_ACS_CNTL` section marker; the ACS control field definitions begin after the assigned range.

### subset-b-002987: lines 64307-66765

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 64307-66765

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,117 `#define` field-layout macros across 2,459 source lines. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range starts in the tail of the `BIF_CFG_DEV0_RC1_*` PCIe root-complex capability layout, beginning with the control fields for Access Control Services and continuing through Data Link Feature, 16 GT/s and 32 GT/s PHY/equalization, lane margining, Alternate Protocol, and Readiness Time Reporting registers. It then switches at the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block to the `BIF_CFG_DEV0_EPF0_1_*` endpoint function 0 PCI configuration-space template. The endpoint block covers conventional PCI identity/resource registers, PM/PCIe/MSI/MSI-X/VSEC/VC/DSN/AER/BAR/PWR/DPA/ACS/PASID/MC/LTR/ARI/SR-IOV capability fields, Data Link Feature and 16 GT/s PHY fields, and most of the endpoint lane-margining sequence. The source boundary is artificial: it starts after earlier RC1 ACS capability definitions and ends after only the first field of `BIF_CFG_DEV0_EPF0_1_LANE_15_MARGINING_LANE_CNTL`.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 hardware register interface. For each named register or PCI configuration-space word, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used to position a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion `nbio_4_3_0_offset.h` supplies matching register/config offsets. Runtime AMDGPU code combines the offset macros with these shift/mask macros through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 addressing helpers, and NBIO or PCI configuration accessors.

This chunk specifically documents the software-visible bit layout for PCIe root-complex and endpoint-function configuration structures in NBIO. The represented fields control or report link training, lane equalization, lane margining, PCI command/status, BARs, interrupt delivery, error reporting, power management, traffic classes/virtual channels, isolation controls, PASID/ARI/SR-IOV virtualization features, and readiness timing.

## Important Macro Families

The initial `BIF_CFG_DEV0_RC1_*` portion covers later root-complex extended capabilities:

- `PCIE_ACS_CNTL` enables or configures source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, egress control, direct translated P2P, I/O request blocking, downstream/upstream memory target access, and unclaimed-request redirect behavior.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` expose Data Link Feature capability metadata, local feature support, exchange enablement, remote feature support, and remote support validity.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, and parity mismatch status registers describe 16 GT/s PHY capability metadata, equalization completion/phase state, link equalization requests, and local/RTM parity mismatch status.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` provide downstream/upstream 16 GT/s TX preset fields per lane.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_LANE_{CNTL,STATUS}` through `LANE_15_MARGINING_LANE_{CNTL,STATUS}` define software-controlled lane margining readiness and per-lane receiver number, margin type, usage model, and payload/status fields.
- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, `LINK_STATUS_32GT`, modified training sequence data, and `LANE_0_EQUALIZATION_CNTL_32GT` through `LANE_15_EQUALIZATION_CNTL_32GT` provide the analogous PCIe 5.0/32 GT/s capability, control, status, modified TS, and per-lane preset layout.
- `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA1`, `AP_DATA2`, and `AP_SEL_EN_MASK` cover Alternate Protocol capability/control/data fields, including capability identification, alternate protocol selection, reset behavior, enablement, and selected lane mask bits.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` define Readiness Time Reporting metadata and timing fields for reset, data-link-up, FLR, and D3hot-to-D0 transition timing, plus a validity bit.

The `BIF_CFG_DEV0_EPF0_1_*` endpoint-function portion starts a full PCI/PCIe configuration image:

- Conventional PCI header fields: vendor/device ID, command, status, revision, programming interface, subclass, base class, cache-line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, maximum latency, and a vendor capability header.
- PCI command/status bits: I/O and memory access enables, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, fast back-to-back, interrupt disable, immediate readiness, interrupt status, capability-list presence, DEVSEL timing, target/master abort reporting, system-error signaling, and parity error detection.
- Power Management capability fields: PM capability list header, version, PME support, D-state support, auxiliary current, power-state control, PME enable/status, data select/scale, bus-power enable, and PMI data.
- PCIe base capability fields: capability header, PCIe version, device/port type, slot implementation, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Device and link controls: correctable/non-fatal/fatal/unsupported request reporting enables, relaxed ordering, max payload, extended tags, phantom functions, auxiliary power PM, no-snoop, max read request size, FLR initiation, ASPM, link retrain/disable, common clock, extended sync, bandwidth-management interrupts, target speed, compliance, de-emphasis, equalization status, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, emergency power reduction, ten-bit tags, and end-to-end TLP prefix blocking.
- MSI/MSI-X fields: capability metadata, MSI enable and multiple-message state, 32-bit and 64-bit message address/data, masks, pending bits, MSI-X table size/function mask/enable, and MSI-X table/PBA BIR and offset fields.
- PCIe vendor-specific, Virtual Channel, Device Serial Number, Advanced Error Reporting, BAR, Power Budgeting, Dynamic Power Allocation, and Secondary PCIe capabilities.
- AER fields: uncorrectable status/mask/severity bits, correctable status/mask bits, first-error pointer, ECRC generation/check capability and enablement, multi-header receive controls, TLP prefix log presence, completion-timeout log capability, header logs, and TLP prefix logs.
- BAR and power capabilities: BAR1 through BAR6 capability/control masks for BAR size and enablement, power-budget selection/data/capability, DPA capability/status/control, latency indicator, and per-substate power allocation.
- PCIe Secondary and lane equalization fields: link control 3, lane error status, and per-lane 8 GT/s downstream/upstream TX preset and RX preset hint fields for lanes 0 through 15.
- Isolation and virtualization features: ACS capability/control, PASID capability/control, multicast capability/control/address/receive/block masks, LTR capability, ARI capability/control, and SR-IOV capability/control/status/resource fields including VF counts, offsets, stride, VF device ID, page sizes, VF BARs, and migration-state array offset.
- Endpoint DLF/16 GT/s/lane-margining fields: Data Link Feature metadata/status, 16 GT/s PHY metadata/status/equalization/parity fields, per-lane 16 GT/s presets, margining readiness, and per-lane margin control/status fields through the chunk's truncated `LANE_15_MARGINING_LANE_CNTL` start.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace. Consumers rely on the generated register names, field names, shifts, and masks staying synchronized with offsets and hardware behavior.

The constants are untyped preprocessor integer literals, generally with an `L` suffix. They encode bit positions and bit masks only. They do not encode register access width, reset value, read/write permissions, write-one-to-clear behavior, privilege requirements, ordering constraints, or side effects. Callers must know from the hardware specification and access path whether a field is read-only capability data, writable policy, sticky error status, W1C status, diagnostic log data, or a command bit that triggers hardware behavior.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU, SMU, PCIe, SR-IOV, virtualization, or display code selects an NBIO register or PCI configuration-space offset from the companion offset header.
2. The code reads a hardware value, extracts fields with the `__SHIFT` and `_MASK` constants, or composes an updated value through field helpers.
3. The decoded value drives policy or diagnostics, or the composed value is written back to hardware.

Likely flows using fields from this chunk include PCI enumeration, endpoint resource assignment, BAR sizing and enablement, memory access and bus-mastering setup, MSI/MSI-X interrupt programming, PCIe link training and equalization diagnostics, lane margining, 16 GT/s and 32 GT/s feature negotiation, AER collection/masking/clearing, power-management transitions, virtual-channel/resource setup, ACS/PASID/ARI/SR-IOV virtualization policy, VF resource exposure, multicast filtering, and readiness-time reporting.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCIe root-complex and endpoint-function configuration registers. Persistence is determined by the GPU/NBIO reset domain, PCI configuration reset, function-level reset, suspend/resume save-restore, firmware initialization, PF/VF management, hypervisor policy, and explicit driver writes.

Represented state includes static PCI identity/capability information, host-programmed command bits, BAR and ROM resource windows, interrupt routing and MSI/MSI-X message state, PCIe device/link controls, link/device status, equalization outcomes, per-lane presets and margining controls, AER status/mask/severity/log registers, power-management settings, virtual-channel resource controls, ACS/PASID/ARI/SR-IOV virtualization state, VF resource windows, multicast address/blocking state, and readiness timing data.

Several fields have side effects or non-storage semantics. `BUS_MASTER_EN` and `MEM_ACCESS_EN` gate DMA and MMIO decode; `INITIATE_FLR` starts a function-level reset; link retrain/disable controls affect PCIe link state; MSI/MSI-X enables and masks affect interrupt delivery; AER status/log bits may be sticky or write-one-to-clear; ACS/PASID/ARI/SR-IOV controls affect isolation and address routing; and lane margining/equalization fields interact with live PHY training state. The generated file only supplies bit layout, so call sites must provide ordering, privilege, and reset handling.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 4.3.0 register database and must stay aligned with sibling generated headers:

- `nbio_4_3_0_offset.h` supplies matching `reg...`/`cfg...` offsets for the register names in this file.
- Other generated NBIO 4.3.0 headers provide related defaults and register metadata where present.
- AMDGPU register helper macros consume these field constants for extraction and update.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU 13 power-management files such as `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`. The surrounding AMDGPU stack integrates these definitions with PCI probing, GPU reset, interrupt setup, power management, SR-IOV/PF/VF handling, link management, error reporting, and diagnostics.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem control flow.

## Risks And Edge Cases

- Generated mask or shift drift can compile cleanly while causing software to read, preserve, clear, or set the wrong hardware bit. This is most dangerous for command, DMA enable, interrupt, FLR, AER, ACS, PASID, ARI, SR-IOV, link-control, and lane-training fields.
- The chunk starts and ends mid-family. The previous chunk is needed for complete RC1 ACS context, and the next chunk is needed for the rest of endpoint lane 15 margining plus any later endpoint capability fields.
- Repeated per-lane definitions are intentionally mechanical. A single lane-specific mismatch can indicate register database or generator drift, but chunk-boundary truncation must not be misread as a real lane mismatch.
- PCI command and BAR masks affect resource decode and bus mastering. Incorrect values can break probing, expose the wrong MMIO window, or enable DMA at the wrong time.
- MSI/MSI-X address/data/mask/pending fields affect interrupt routing. Incorrect masks can produce lost, repeated, or misrouted interrupts.
- AER status and log fields are diagnostic evidence. Treating sticky/W1C status fields as ordinary writable state can lose error evidence or fail to quiesce an error condition.
- ACS, PASID, ARI, multicast, and SR-IOV fields affect isolation, routing, and VF resource exposure. Incorrect masks can break VF discovery, IOMMU/PASID behavior, or peer-to-peer isolation assumptions.
- Link equalization, margining, and 16/32 GT/s controls interact with live PCIe PHY state. Wrong field definitions can produce misleading link diagnostics or unstable retrain/margining flows.
- Readiness timing fields should only be trusted when their validity bits and capability metadata indicate usable data; under-waiting after reset, FLR, or D-state transitions can cause probe or resume races.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Direct macro users should catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks within registers, capability-list continuity, per-lane repetition checks, and EPF0_1/SR-IOV field consistency.
- Runtime probe on affected AMD GPUs should show stable PCI enumeration, correct vendor/device/class/capability data, sane BAR sizing, and correct command-bit transitions for memory access and bus mastering.
- Interrupt validation should exercise MSI and MSI-X enablement, table/PBA offsets, masking, pending bits, and absence of lost or spurious interrupts.
- PCIe health validation should cover negotiated speed/width, 8/16/32 GT/s equalization status, link retrain behavior, lane error status, lane margining readiness/status, and absence of unexpected AER storms.
- Error-injection or fault-observation tests should confirm AER status/mask/severity/log fields decode correctly and that diagnostic logs are not unintentionally cleared.
- Virtualization tests should cover ACS isolation, PASID enablement, ARI routing, SR-IOV VF counts/strides/BARs/page sizes, VF enumeration, FLR timing, and PF/VF reset behavior.
- Power-management and readiness tests should compare advertised reset/DL-up/FLR/D3hot-to-D0 timing fields against actual wait paths and verify validity bits are honored.

### subset-b-002988: lines 66766-69194

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 66766-69194

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: no C functions, structs, enums, variables, allocations, locks, or executable statements.

The range starts in the final fields for `BIF_CFG_DEV0_EPF0_1_LANE_15_MARGINING_LANE_CNTL`, covers the lane-15 margining status, VF resizable BAR capability registers, PCIe 32 GT/s capability/control/status fields, per-lane 32 GT/s equalization presets, Alternate Protocol and RTR capability fields, complete SR-IOV `VF0_1` and `VF1_1` PCI configuration templates, and the beginning of `VF2_1` through AER header/TLP prefix logs and the first ARI enhanced-capability fields. The source boundary is artificial: preceding lane-margining fields and the rest of VF2 ARI/RTR fields are outside this chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of the NBIO 4.3.0 hardware register interface. For each named NBIO or PCI configuration register, it defines:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit used to pack or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update the field.

The companion offset header provides the register/config-space addresses. AMDGPU code combines the offset and shift/mask headers through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 register accessors, and PCI/NBIO configuration-space paths.

This chunk mainly describes PCIe capability layout for NBIO device 0, endpoint function 0, including physical-function capability extensions and SR-IOV virtual-function configuration images. It is hardware metadata; although it lives under a `ceph-client` source mirror, it has no direct distributed-filesystem behavior.

## Important Macro Families

The physical-function `BIF_CFG_DEV0_EPF0_1_*` tail covers late PCIe 5.0 style capability blocks:

- Lane 15 margining fields expose receiver number, margin type, usage model, and margin payload status for PCIe lane margining.
- `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST` plus `PCIE_VF_RESIZE_BAR[1-6]_CAP/CNTL` describe VF resizable BAR support, selected BAR index, total BAR count, programmed BAR size, and upper supported-size bits.
- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT` describe 32 GT/s equalization behavior, no-equalization-needed signaling, modified training sequence modes, transmitter precoding, enhanced link behavior controls, and per-phase equalization status.
- `RECEIVED_MODIFIED_TS_DATA[1-2]` and `TRANSMITTED_MODIFIED_TS_DATA[1-2]` expose modified training sequence usage mode, vendor ID, information payload, and alternate protocol negotiation status.
- `LANE_[0-15]_EQUALIZATION_CNTL_32GT` repeats downstream/upstream 32 GT/s transmit preset fields per lane.
- `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA[1-2]`, and `AP_SEL_EN_MASK` describe Alternate Protocol capability, status/control, and protocol-selection data.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` describe Readiness Time Reporting metadata and reset, DL-up, FLR, D3hot-to-D0, and validity fields.

The `BIF_CFG_DEV0_EPF0_VF0_1_*` and `VF1_1_*` blocks repeat complete virtual-function PCI configuration templates:

- Conventional PCI header fields: vendor/device ID, command, status, revision ID, class-code bytes, cache-line size, latency timer, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- PCI command/status bits: I/O and memory access, bus mastering, special cycles, memory write invalidate, VGA palette snoop, parity response, SERR, interrupt disable, immediate readiness, interrupt status, capabilities-list presence, master-data parity, DEVSEL timing, target/master abort reporting, signaled system error, detected parity error, and status bits for unsupported request, fatal, non-fatal, and correctable PCIe errors.
- PCIe capability fields: capability IDs and next pointers, PCIe version, device/port type, slot implemented, interrupt message number, device/link capability, control, and status registers, plus device/link capability/control/status 2.
- Device and link controls: error-reporting enables, relaxed ordering, max payload, extended tags, phantom functions, aux power PM, no-snoop, max read request, bridge config retry, function-level reset, ASPM, link disable/retrain/common-clock/extended-sync, bandwidth-management interrupts, target link speed, compliance controls, de-emphasis, transmit margin, enter modified compliance, equalization phase status, completion-timeout ranges and controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, emergency power reduction, ten-bit tags, and end-to-end TLP prefix blocking.
- MSI and MSI-X fields: capability-list metadata, MSI enable and multiple-message controls, 32-bit/64-bit message address and data registers, masks and pending bits, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability fields: capability-list metadata, VSEC ID/revision/length, and two 32-bit scratch/payload registers.
- Advanced Error Reporting: AER capability metadata; uncorrectable status/mask/severity fields for DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked; correctable status/mask fields for receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow events; AER capability/control; four TLP header log words; and four TLP prefix log words.
- ARI and RTR fields: Alternative Routing-ID Interpretation capability/control metadata, function group and next-function fields, and readiness timing fields.

The `BIF_CFG_DEV0_EPF0_VF2_1_*` block begins at `VENDOR_ID` and follows the same VF template through `PCIE_ARI_ENH_CAP_LIST__CAP_ID_MASK`. The remainder of VF2 ARI and RTR fields belongs to the next chunk.

## APIs, Types, And Functions

There are no runtime APIs or C types in this range. The exported interface is the generated macro namespace itself. Consumers rely on exact macro names, masks, and shifts staying synchronized with the matching NBIO 4.3.0 offset/default headers and with AMD's hardware register database.

The constants are untyped preprocessor integer literals, mostly with an `L` suffix. They describe bit positions and masks only. They do not encode access width, read/write permissions, reset values, volatility, privilege requirements, write-one-to-clear behavior, or hardware side effects. Call sites must know whether a bit is a read-only capability bit, writable policy/control bit, sticky status bit, diagnostic log word, or command bit with immediate hardware effect.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. Driver, firmware-facing, SR-IOV, PCIe, or diagnostic code selects a register/config-space offset from the companion NBIO 4.3.0 offset header.
2. The code reads, decodes, composes, or updates register values using this file's `__SHIFT` and `_MASK` constants directly or through field helper macros.
3. The resulting value is written back, polled, saved/restored, exposed to PCI enumeration, used for interrupt routing, or reported in diagnostics.

Likely flows using this chunk include PCIe 32 GT/s link bring-up/equalization, lane margining diagnostics, VF BAR sizing, VF PCI enumeration, SR-IOV virtual-function resource enablement, MSI/MSI-X setup, function-level reset, AER collection/masking, ARI routing, Alternate Protocol negotiation, and Readiness Time Reporting.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration and PCIe extended capability registers. Persistence is determined by GPU reset domains, firmware initialization, PF/VF management, hypervisor policy, VF FLR, suspend/resume save-restore, and explicit driver writes.

Represented state includes static identity/capability values, host-programmed PCI command bits, BAR and ROM resource registers, interrupt routing state, MSI/MSI-X message address/data/mask/pending state, PCIe device/link policy and status, 32 GT/s equalization and modified-training-sequence state, lane margining status, Alternate Protocol negotiation state, AER sticky status/mask/severity/log values, ARI function-routing controls, and RTR timing-validity data.

Several fields are not ordinary storage. `MEM_ACCESS_EN`, `BUS_MASTER_EN`, MSI/MSI-X enable bits, link retrain/disable controls, `INITIATE_FLR`, AER status/log fields, AP negotiation controls, and 32 GT/s equalization controls can alter hardware behavior or clear/consume diagnostic state. This generated file only gives bit layout; sequencing, privilege, reset, and side-effect rules are enforced by hardware and by the driver code that uses the macros.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 header set:

- `nbio_4_3_0_offset.h` supplies matching `cfg`/`reg` offsets and base-index metadata for the register names covered here.
- Other generated NBIO 4.3.0 headers supply defaults or related register metadata where present.
- AMDGPU register helper macros consume these `__SHIFT` and `_MASK` definitions for field extraction and read-modify-write composition.

Integration points include AMDGPU NBIO initialization, PCIe link management, SR-IOV PF/VF presentation, Linux PCI config-space enumeration, BAR resource assignment, interrupt setup, AER reporting, reset handling, ARI routing, and power-management save/restore paths. The repeated VF templates are intended to align with hardware-configured virtual function instances; adjacent chunks must be merged before drawing whole-file conclusions about the complete VF2 template.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while making software touch the wrong hardware bit. Risk is highest for PCI command, bus mastering, interrupt, FLR, link control, equalization, AER, ARI, AP, and RTR fields.
- The chunk starts and ends inside logical register groups. The missing beginning of lane-15 margining control and the missing tail of VF2 ARI/RTR should not be interpreted as absent hardware support.
- VF0, VF1, and VF2 repetition is intentional. Per-VF differences should be checked against the generator and companion offset header before treating them as a bug.
- Incorrect VF resizable BAR masks can produce wrong BAR sizing or expose incorrect resource windows to guests.
- Wrong PCI command or BAR fields can break VF probing, DMA enablement, memory access isolation, or host resource assignment.
- 32 GT/s link/equalization, transmitter precoding, modified training sequence, and Alternate Protocol masks affect link training and negotiation. Bad values can cause link instability or negotiation failures that look like platform or signal-integrity problems.
- MSI/MSI-X table, PBA, mask, pending, and enable fields can cause lost, repeated, or misrouted interrupts if decoded or programmed incorrectly.
- AER status and log fields are diagnostic evidence. Treating sticky or write-one-to-clear fields as ordinary writable state can lose the first-error pointer, TLP header/prefix logs, or severity information.
- ARI controls affect function routing and enumeration. Incorrect masks can hide VFs or route transactions to the wrong function.
- RTR timing fields must be gated by their validity bit; otherwise management code can under-wait, over-wait, or trust stale timing data.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Missing or misspelled macro users should fail at compile time.
- Runtime PCI enumeration on affected AMD GPUs should show stable PF and VF config-space identity, capabilities, BAR sizing, and class information.
- SR-IOV validation should exercise at least VF0, VF1, and VF2 because this chunk contains complete templates for the first two VFs and the front of the third.
- VF resource tests should confirm resizable BAR support bits and BAR-size control fields match advertised capabilities and host-assigned windows.
- PCIe link health tests should check negotiated width/speed, successful retrain paths, 32 GT/s equalization status, and absence of unexpected AER storms.
- Lane-margining and modified-training-sequence diagnostics should decode receiver, margin type, payload, vendor, usage mode, and alternate protocol status consistently with hardware documentation.
- Interrupt smoke tests should verify MSI/MSI-X enablement, masking, pending-bit behavior, and absence of spurious or lost interrupts.
- Error-injection or platform AER tests should preserve and decode uncorrectable/correctable status, severity, first-error pointer, TLP header logs, and TLP prefix logs.
- ARI and virtualization tests should verify VF enumeration, function routing, and isolation under PF/VF and hypervisor-controlled setups.
- RTR validation should compare advertised reset, DL-up, FLR, and D3hot-to-D0 timing fields with observed waits and ensure invalid timing data is ignored.

### subset-b-002989: lines 69195-71626

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 69195-71626

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask-header slice. It contains C preprocessor constants only: per-field `__SHIFT` and `_MASK` macros for PCI/PCIe configuration-space registers. There are no functions, structs, enums, variables, allocations, locks, loops, branches, or executable statements in this range.

The range starts at the tail of the `BIF_CFG_DEV0_EPF0_VF2_1` virtual-function capability block, covering ARI and Readiness Time Reporting fields, then defines full field layouts for `VF3_1`, `VF4_1`, and `VF5_1`, and ends partway through `VF6_1` at `LINK_CAP`. All of these live under NBIO address blocks named like `nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp`.

Although this source tree is under a `ceph-client` mirror, this file is AMD DRM/AMDGPU hardware metadata. It has no Ceph distributed-filesystem control path.

## Purpose

`nbio_4_3_0_sh_mask.h` publishes generated bit positions and masks for NBIO 4.3.0 registers. This chunk maps PCIe configuration fields for SR-IOV-style virtual functions on device 0, endpoint function 0, instance 1:

- `VF2_1` tail fields for `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`.
- Complete `VF3_1`, `VF4_1`, and `VF5_1` layouts from standard PCI identity/configuration registers through PCIe capability, MSI/MSI-X, vendor-specific enhanced capability, Advanced Error Reporting, ARI, and Readiness Time Reporting.
- Initial `VF6_1` fields through standard PCI identity/configuration, BARs, PCIe capability, device capability/control/status, and the beginning of `LINK_CAP`.

The macros let consumers extract or compose fields without embedding literal bit positions. Typical use is `value & FIELD_MASK`, `(value & FIELD_MASK) >> FIELD__SHIFT`, or a helper such as `REG_SET_FIELD` where the generated name is part of the hardware ABI.

## Important APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace. The chunk contributes 2,140 `#define` lines: 1,072 shift definitions and 1,068 mask definitions.

Important field families visible here include:

- Standard PCI header fields: vendor/device IDs, command/status bits, revision/class codes, cache-line and latency timers, header/BIST, six BARs, CardBus CIS pointer, subsystem adapter IDs, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list linkage, device type, max payload support/size, extended tags, no-snoop, relaxed ordering, FLR, error enables/status, link speed/width, ASPM and link disable/retrain controls, link training/status bits, slot clock, data-link active reporting, and bandwidth notification bits.
- PCIe Capability 2 fields: completion-timeout support/control, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS, supported link speeds, compliance/deemphasis controls, equalization status, crosslink/resolution, and DRS status.
- Interrupt capability fields: MSI enablement, multi-message support/enable, 64-bit addressing, per-vector masking, message address/data, MSI mask/pending bits, MSI-X table/PBA offsets and sizes.
- Extended capability fields: vendor-specific capability header/scratch fields, Advanced Error Reporting uncorrectable/correctable status/mask/severity bits, AER control bits, header logs, TLP prefix logs, ARI capability/control, and Readiness Time Reporting data.

The exact VF-suffixed macros in this chunk are mostly generated ABI surface rather than common hand-written call sites in the observed tree. Nearby NBIO 4.3 driver code uses the same register-field pattern for non-VF endpoint registers: `nbio_v4_3.c` reads `regBIF_CFG_DEV0_EPF0_DEVICE_CNTL2`, toggles `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK`, and writes it back through `RREG32_SOC15`/`WREG32_SOC15`. VF consumers would use this chunk's suffixed variants in the same style when addressing virtual-function config space.

## Control Flow

This header chunk has no local control flow. Runtime behavior is supplied by external driver paths:

1. AMDGPU code includes the NBIO 4.3.0 offset and shift/mask headers for matching ASICs.
2. A caller selects an address macro from the sibling offset header for a VF PCI/PCIe config register.
3. The caller reads or writes that hardware register through PCIe, MMIO, SOC15, or generated register helpers.
4. The caller applies this chunk's shift/mask macro to decode a field, test status, preserve unrelated bits, or compose a new value.
5. Hardware state changes or reports status according to the PCIe/NBIO specification.

Ordering, retry, reset, and write-one-to-clear behavior are not encoded here. Those rules must come from the consuming driver path and the hardware spec.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It names bitfields in hardware-visible PCI configuration state for virtual functions. Persistence is therefore controlled by GPU/NBIO reset domains, PCI config-space save/restore, firmware initialization, SR-IOV enablement/disablement, function-level reset, hot reset, suspend/resume, and explicit driver or firmware writes.

Some represented fields are static capabilities, such as max payload support, FLR capability, supported link speeds, MSI-X table size, ARI capability, and readiness-time support. Others are controls, such as bus mastering, interrupt disable, MSI/MSI-X enables, error-reporting enables, max payload size, no-snoop, link retrain, completion-timeout disable, ARI forwarding, LTR enable, OBFF mode, and AER ECRC controls. Several fields are status or diagnostic logs, including PCI status bits, device status, link status, AER error status, first-error pointer, header logs, TLP prefix logs, and readiness-time valid bits.

The macros do not distinguish read-only, read/write, sticky, write-one-to-clear, or firmware-owned fields. Consumers must preserve reserved bits and use the correct access width for each PCIe register.

## Dependencies And Integration Points

Direct dependencies are the sibling generated NBIO headers:

- `nbio_4_3_0_offset.h` supplies the register offsets that pair with these field masks.
- Other generated NBIO 4.3.0 headers provide related reset/default/SMN metadata outside this shift/mask file.

Broader integration points include AMDGPU NBIO initialization, PCIe capability enumeration, SR-IOV virtual-function exposure, PCI resource/BAR handling, MSI/MSI-X interrupt setup, PCIe AER/RAS diagnostics, link training and ASPM/LTR policy, IOMMU and virtualization policy, ARI function routing, FLR handling, and suspend/resume config restore. Similar generated field families exist for other NBIO generations, but these names and masks are specific to NBIO 4.3.0.

## Risks And Edge Cases

- Generated bit drift can compile cleanly while decoding or programming the wrong bit. That is highest risk for control fields such as bus mastering, interrupt disable, MSI/MSI-X enable, max payload size, no-snoop, FLR initiation, LTR, ARI forwarding, AER masks, and link controls.
- This is a chunk boundary. `VF2_1` begins in a preceding chunk, and `VF6_1` continues in a following chunk. The final per-file report must merge adjacent chunks before describing complete VF2/VF6 coverage.
- Multi-bit fields must be shifted after masking. Using the mask as a raw value or forgetting the shift can silently misconfigure fields such as payload sizes, link width/speed, OBFF mode, MSI vector counts, AER first-error pointer, and readiness-time values.
- Several mask names intentionally include repeated words, such as `PCIE_UNCORR_ERR_MASK__DLP_ERR_MASK_MASK`, because the register name and field name both contain `MASK`. String-based tooling must not try to normalize these names.
- PCIe error status bits may be sticky or write-one-to-clear depending on the register. A generic read-modify-write using these masks can accidentally clear diagnostic state if the access semantics are wrong.
- Link-control and compliance fields can affect negotiated link speed, link retraining, electrical compliance mode, and autonomous speed changes. Incorrect writes can cause performance loss or link instability.
- Interrupt table/PBA fields are offset and size descriptors for MSI-X. Wrong interpretation can break vector setup or point the driver at the wrong table aperture.
- VF configuration fields are virtualization-sensitive. Misprogramming ARI, ACS-related AER bits, FLR, MSI/MSI-X, or BAR metadata can affect guest isolation, function routing, reset behavior, or interrupt delivery.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with NBIO 4.3.0 support enabled to catch syntax, include-order, and missing-macro failures.
- Run generated-register consistency checks against the authoritative NBIO 4.3.0 register database, especially across the repeated VF3/VF4/VF5 blocks and the VF2/VF6 chunk boundaries.
- Boot matching AMD GPUs and verify PCI config-space enumeration, capability-chain traversal, VF discovery, BAR/resource reporting, and interrupt setup.
- Exercise SR-IOV or virtualization paths that expose these virtual functions, including VF enable/disable, FLR, guest driver probing, MSI/MSI-X delivery, and suspend/resume restore.
- Validate PCIe link and power-management behavior around ASPM/LTR/OBFF settings, link retrain/status reporting, and negotiated speed/width.
- Inject or observe PCIe AER/RAS events where possible and confirm uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs decode as expected.

## Chunk-Specific Notes For Merge

When merging this chunk into the final `nbio_4_3_0_sh_mask.h` research document, preserve that lines 69195-71626 cover the tail of `VF2_1`, all of `VF3_1` through `VF5_1`, and the beginning of `VF6_1`. The range is generated register metadata only; its significance is the breadth of PCIe virtual-function field definitions rather than local algorithmic behavior.

### subset-b-002990: lines 71627-74047

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 71627-74047

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocation paths, locks, branches, loops, or direct MMIO accesses in this range.

The slice starts at the tail of `BIF_CFG_DEV0_EPF0_VF6_1_LINK_CAP`, covers the rest of the `BIF_CFG_DEV0_EPF0_VF6_1` PCIe virtual-function configuration-space block, then covers complete `BIF_CFG_DEV0_EPF0_VF7_1` and `BIF_CFG_DEV0_EPF0_VF8_1` blocks. It begins `BIF_CFG_DEV0_EPF0_VF9_1` and stops at `BIF_CFG_DEV0_EPF0_VF9_1_PCIE_VENDOR_SPECIFIC_HDR`; VF9 vendor-specific payload, AER, ATS, ARI, and later fields continue after this chunk.

Although this file is located under a `ceph-client` source mirror, this header is AMDGPU ASIC register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield layouts for NBIO 4.3.0 SR-IOV virtual-function PCI configuration-space images. Each generated field is represented by the usual AMD register macro pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, supplies the matching register offsets. Runtime code combines those offsets with this header through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF6 fragment completes `LINK_CAP` fields for link speed, link width, power-management support, L0s/L1 exit latency, clock power management, surprise-down reporting, data-link active reporting, bandwidth notification capability, ASPM optionality, and port number. The rest of VF6 then defines link control/status, PCIe capability 2, MSI/MSI-X, vendor-specific enhanced capability, AER, and ARI/router-related fields.

The full VF7 and VF8 blocks repeat a standard PCI Type 0 virtual-function configuration image:

- Identity and header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, adapter/subsystem ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability-list linkage, PCIe type/version/slot/message fields, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Interrupt capability fields: MSI capability list/control, MSI address/data/ext-data/mask/pending registers, 64-bit MSI aliases, MSI-X table-size/function-mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific and AER fields: vendor-specific enhanced capability list/header, two scratch payload dwords, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- Virtualization-oriented capability fields: ARI enhanced capability list/capability/control and router data fields. Unlike some related NBIO generations, this specific slice exposes ARI/RTR tails here and not a complete ATS family for these VFs inside the covered range.

The VF9 block repeats the same layout from identity/header fields through PCIe, MSI/MSI-X, and the beginning of vendor-specific enhanced capability state. This chunk ends after the VF9 vendor-specific header mask, before VF9 vendor-specific scratch payload, AER, ARI/RTR, and any remaining extended capability fields.

Important PCIe fields in these blocks include max payload support/size, phantom functions, extended tags, endpoint L0s/L1 acceptable latency, function-level reset capability/initiation, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, 10-bit tag support, target link speed, link retraining/disable, common clock configuration, autonomous width/speed disable controls, de-emphasis, equalization status, DRS status, and link bandwidth status. AER fields cover conditions such as DLP errors, surprise down, poisoned TLP, flow-control protocol error, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked.

## Control Flow

There is no executable control flow in this header. Its effect is compile-time: it gives C code the constants needed to compose and decode NBIO PCIe configuration-space register values.

Typical runtime use follows this pattern:

1. AMDGPU code selects a `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` or related NBIO register offset from `nbio_4_3_0_offset.h`.
2. The register access layer reads or writes a 16-bit or 32-bit PCIe/NBIO configuration value through SOC15 helpers.
3. Code applies this header's `__SHIFT` and `_MASK` macros directly or via field helpers.
4. The resulting value configures a VF control bit, decodes capability/status state, clears a sticky error, polls hardware-owned state, or exposes decoded state to PCIe, SR-IOV, reset, interrupt, power-management, or diagnostics code.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU PF/SR-IOV management paths.

The represented state includes VF identity/header values, BAR and ROM resource windows, command/status bits, capability-list pointers, PCIe device/link capability and control state, link training and equalization status, MSI/MSI-X programming state, vendor-specific capability payloads, AER error status/mask/severity/log state, ARI function controls, and router data fields. Some fields are static capability declarations, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The generated masks do not encode reset defaults, access permissions, side effects, ordering requirements, polling timeouts, or ownership boundaries.

VF7 and VF8 are complete within this chunk. VF6 and VF9 are boundary fragments and require adjacent chunks before making whole-VF claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database:

- `nbio_4_3_0_offset.h` supplies the matching register addresses and base indices.
- `nbio_4_3_0_sh_mask.h` supplies the field positions and masks in this chunk.
- AMDGPU register helpers in the SOC15/NBIO access layer consume the generated `__SHIFT`/`_MASK` convention.

Observed direct include sites for this generated header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which uses NBIO 4.3 offsets and masks for revision discovery, framebuffer access enablement, doorbell aperture/range setup, interrupt handling, clock gating, and related NBIO control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, which include the same NBIO 4.3 generated headers in SMU13 power-management paths.

The most relevant integration surfaces for these VF configuration fields are SR-IOV VF creation/removal, PF-side VF config-space emulation or inspection, guest driver binding, VF FLR/reset flows, MSI/MSI-X interrupt delivery, PCIe link and power-management policy, AER diagnostics, ARI enumeration/function grouping, suspend/resume, runtime power transitions, and SMU/NBIO coordination on hardware that uses the NBIO 4.3.0 register map.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the VF6 `LINK_CAP` shift lines and stops inside VF9's vendor-specific capability area; adjacent chunks are needed for complete VF6 and VF9 analysis.
- These are untyped preprocessor constants. A stale or incorrect mask can compile cleanly while reading or writing the wrong hardware bit.
- The VF blocks are mechanically repetitive. Suffix mistakes between VF6, VF7, VF8, and VF9 can silently target the wrong virtual function and affect SR-IOV isolation, interrupt delivery, or diagnostics.
- Register-address and field-mask synchronization is critical. Applying a valid VF8 mask to a VF9 or non-VF offset can produce plausible bit operations while corrupting unrelated configuration state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, relaxed-ordering, no-snoop, LTR, OBFF, ARI, link retraining, completion-timeout, or autonomous speed/width values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Wrong address/data width, table/PBA BIR, table offset, mask, pending, or enable fields can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave serious errors masked.
- BAR and ROM masks describe resource exposure. Wrong masks can confuse VF resource sizing or expose invalid apertures.
- Vendor-specific and ARI/router fields are virtualization-sensitive. Incorrect capability-list linkage, VSEC length, ARI function controls, or router data decoding can break guest enumeration or PF/VF management assumptions.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 and SMU13 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c` or the SMU13 PPT files that include this generated header.
- Compare VF6 through VF9 register names against `nbio_4_3_0_offset.h` to confirm field masks and offsets remain synchronized across repeated VF blocks.
- Boot affected hardware and confirm PCIe config-space exposure remains sane for VF7 and VF8: identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, vendor-specific capability, AER, ARI, and router data should decode consistently.
- In SR-IOV configurations, create and remove VFs covering the VF6-VF9 range, bind guest drivers, perform VF FLR, and verify VF isolation, config-space access, reset behavior, ARI enumeration, and interrupt delivery.
- Exercise graphics, compute, DMA, and guest workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion-timeout behavior, LTR/OBFF state, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.

## Chunk Notes

- Lines 71627-72119 complete the latter portion of `BIF_CFG_DEV0_EPF0_VF6_1`, beginning at `LINK_CAP` masks and ending with `RTR_DATA2`.
- Lines 72120-72841 cover the complete `BIF_CFG_DEV0_EPF0_VF7_1` address block.
- Lines 72842-73563 cover the complete `BIF_CFG_DEV0_EPF0_VF8_1` address block.
- Lines 73564-74047 begin `BIF_CFG_DEV0_EPF0_VF9_1` and end at `PCIE_VENDOR_SPECIFIC_HDR`; later VF9 vendor-specific, AER, ARI/RTR, and remaining extended capability fields are outside this work item.

### subset-b-002991: lines 74048-76466

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 74048-76466

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocations, locks, branches, loops, or direct register accesses in this range.

The slice starts at the final mask for the `BIF_CFG_DEV0_EPF0_VF9_1_PCIE_VENDOR_SPECIFIC_HDR` register and then covers the tail of the VF9 PCIe extended capability block: vendor-specific scratch dwords, AER status/mask/severity/log fields, ARI capability/control fields, and Readiness Time Reporting fields. It then defines complete repeated PCIe configuration-space field layouts for `BIF_CFG_DEV0_EPF0_VF10_1`, `BIF_CFG_DEV0_EPF0_VF11_1`, and `BIF_CFG_DEV0_EPF0_VF12_1`. The range ends after the first seven `BIF_CFG_DEV0_EPF0_VF13_1_COMMAND` shift definitions, so VF13 is only a beginning fragment.

Although this path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata rather than Ceph or distributed filesystem logic.

## Purpose

The purpose of this header range is to publish bitfield layouts for NBIO 4.3.0 SR-IOV virtual-function PCI configuration-space images. Each generated hardware field follows the usual AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for isolating, clearing, preserving, or updating that field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_*` offsets. Runtime code combines those offsets with this shift/mask header through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF9 fragment completes the end of a virtual-function extended capability chain. It includes `PCIE_VENDOR_SPECIFIC1/2` scratch dwords, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, AER uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header-log dwords, four TLP prefix-log dwords, ARI enhanced capability/capability/control fields, and Readiness Time Reporting list/data fields.

The full VF10 through VF12 blocks repeat a standard SR-IOV VF PCI Type 0 configuration image. Each block starts with identity and header fields: vendor ID, device ID, command, status, revision ID, programming interface, subclass, base class, cache line, latency, header type/device type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min-grant/max-latency bytes.

The PCIe capability portions for VF10 through VF12 define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, function-level reset capability/initiation, completion timeout controls, ARI forwarding, atomic operation capability/enables, ID-based ordering, LTR, OBFF, 10-bit tag support, link speed/width, ASPM/power-management controls, link disable/retrain, common clock, autonomous bandwidth/speed disables, target link speed, de-emphasis, compliance controls, equalization status, and component presence status.

The MSI and MSI-X portions of VF10 through VF12 cover capability-list linkage, MSI enable/multiple-message/64-bit/per-vector masking controls, MSI message address/data/mask/pending fields, 64-bit MSI aliases, MSI-X table size/function mask/enable fields, MSI-X table BIR/offset, and PBA BIR/offset fields. These masks describe how interrupt capability state is packed in the VF config-space image.

The vendor-specific and AER portions define PCIe vendor-specific enhanced capability list/header fields, two vendor-specific payload dwords, AER enhanced capability list fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header-log dwords, and four TLP prefix-log dwords. Covered AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked conditions.

The ARI and RTR portions at the end of each full VF block define enhanced capability list entries plus ARI capability/control and readiness-time reporting fields. ARI fields expose MFVC/ACS function-group support, next-function number, function-group enable bits, and selected function group. RTR fields expose reset, data-link-up, FLR, and D3hot-to-D0 timing values plus a valid bit for the first RTR timing dword.

The VF13 fragment begins another repeated VF config-space map. This chunk covers VF13 only through vendor ID, device ID, and the first seven command-register shift definitions; the command masks and all later VF13 fields continue after this work item.

## Control Flow

There is no executable control flow in this header. Its effect is compile-time: it gives C code the constants needed to produce or decode the exact PCIe config-space bit patterns expected by NBIO 4.3.0 hardware.

Typical runtime flow in consuming code is:

1. Select a `cfgBIF_CFG_DEV0_EPF0_VF*_*` offset from `nbio_4_3_0_offset.h`.
2. Read or compose a 16-bit or 32-bit PCIe configuration value through the AMD register access layer.
3. Apply this header's `__SHIFT` and `_MASK` macros directly or through `REG_SET_FIELD` and `REG_GET_FIELD`.
4. Write a control value, decode a capability/status value, poll a hardware-owned bit, clear sticky diagnostic status, or expose decoded state to PCIe, SR-IOV, reset, interrupt, virtualization, or diagnostics code.

Flows that can consume these fields include VF PCI capability presentation, VF MSI/MSI-X setup, AER error logging and clearing, function-level reset, PCIe link and power policy, ARI VF enumeration support, readiness-time reporting, PF or hypervisor inspection of VF config state, and suspend/resume or reset validation.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU PF/SR-IOV management code.

The represented state includes identity/header values, BAR and ROM address windows, command/status bits, capability-list pointers, PCIe capability/control/status fields, link capability and link training state, MSI/MSI-X programming state, vendor-specific capability payloads, AER error status/mask/severity/log data, ARI function-group controls, and RTR timing capability data. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The masks do not encode access permissions, reset defaults, ordering requirements, side effects, polling rules, or ownership boundaries.

VF10 through VF12 are complete within this chunk, so their repeated config-space layout can be reasoned about locally. VF9 and VF13 are boundary fragments and require adjacent chunks before making whole-VF claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the matching config-space offsets.
- Other generated NBIO 4.3.0 headers, including defaults or related register maps when present.
- AMDGPU register helper macros and accessors, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Observed direct C-file includes of this exact NBIO 4.3.0 shift/mask header in this source tree are SMU13 power-management files `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. Even where these VF-specific macros are not referenced directly by name, the generated header participates in the common AMDGPU NBIO register ABI used by PCIe, link, power, SR-IOV, reset, and diagnostics paths.

Relevant integration surfaces are AMDGPU NBIO/BIF setup, PCIe link control, SR-IOV VF lifecycle, VF interrupt delivery, AER diagnostics, FLR and readiness-time reporting, ARI capability handling, power-management transitions, and platform firmware or Linux PCI core interactions over command/status, BARs, MSI/MSI-X, PCIe device/link control, AER, ARI, LTR, OBFF, completion timeout, and FLR fields.

## Risks And Edge Cases

- The chunk boundaries are artificial. The range starts at only one remaining VF9 vendor-specific-header mask and ends before VF13 command masks are emitted; adjacent chunks are required for complete VF9 and VF13 analysis.
- These are untyped preprocessor constants. A stale shift or mask can compile cleanly while decoding or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around VF9 through VF13 could silently target the wrong virtual function and break SR-IOV isolation, interrupt routing, diagnostics, or reset handling.
- Register-address and field-mask mismatches are easy in generated headers. A valid `VF11_LINK_CNTL` mask applied to a `VF12` or non-VF offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, completion timeout, relaxed-ordering, no-snoop, LTR, OBFF, ARI, or link-control values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Width, aliasing, table offset/BIR, mask, pending, or enable mistakes can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures, confuse VF resource sizing, or conflict with Linux PCI resource management.
- ARI and RTR fields affect VF enumeration and reset/power timing assumptions. Incorrect next-function numbers, function-group controls, reset timing, DL-up timing, FLR timing, or D3hot-to-D0 timing values can mislead virtualization and recovery paths.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 and SMU13 support enabled; missing, renamed, or duplicated macros should surface in include paths such as `smu_v13_0_0_ppt.c`, `smu_v13_0_7_ppt.c`, or shared AMDGPU register code.
- Compare VF10 through VF12 field layouts against `nbio_4_3_0_offset.h` to confirm register names, order, widths, and repeated VF layout remain synchronized.
- Boot affected hardware and confirm PCIe config exposure remains sane: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, AER, ARI, and RTR fields should decode consistently.
- In SR-IOV configurations, create and remove VFs around the VF9-VF13 range, bind guest drivers, exercise VF FLR, and verify VF isolation, config-space access, ARI enumeration behavior, interrupt delivery, and reset/recovery timing.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout behavior, LTR/OBFF state, FLR completion, and RTR timing assumptions.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.

## Chunk Notes

- Line 74048 is only the final `VSEC_LENGTH_MASK` for `BIF_CFG_DEV0_EPF0_VF9_1_PCIE_VENDOR_SPECIFIC_HDR`; the rest of that register's shifts and masks are in the previous chunk.
- Lines 74049-74257 cover the remaining VF9 vendor-specific, AER, ARI, and RTR field definitions.
- Lines 74260-76254 define complete `BIF_CFG_DEV0_EPF0_VF10_1`, `VF11_1`, and `VF12_1` PCIe VF config-space shift/mask blocks.
- Lines 76257-76466 begin `BIF_CFG_DEV0_EPF0_VF13_1` and stop inside the command register after `PARITY_ERROR_RESPONSE__SHIFT`; VF13 command masks and subsequent fields continue in the next chunk.

### subset-b-002992: lines 76467-78893

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 76467-78893

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, locks, allocations, loops, branches, or direct MMIO/config-space accesses in this range.

The range starts inside `BIF_CFG_DEV0_EPF0_VF13_1_COMMAND`, covers the remainder of `BIF_CFG_DEV0_EPF0_VF13_1`, then defines complete repeated PCIe configuration-space field layouts for `BIF_CFG_DEV0_EPF0_VF14_1` and `BIF_CFG_DEV0_EPF0_VF15_1`. It then enters the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` block and covers `BIF_CFG_DEV0_EPF1_1` from vendor/device identity through the first half of `LINK_CAP`; later EPF1 link-control/status, MSI/MSI-X, vendor-specific, AER, VC, serial-number, BAR, and GPUIOV-related fields continue after this chunk.

Although this source tree is under a local `ceph-client` mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield positions for NBIO 4.3.0 PCIe/BIF configuration registers. Every represented field follows the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate, clear, preserve, or update the field.

The matching address side is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the register offsets. This source tree has no local `nbio_4_3_0_default.h` companion, so reset/default-value analysis for these exact registers cannot be derived from a same-generation default header here.

Runtime code combines these constants with AMDGPU access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The constants themselves are a compile-time ABI between generated hardware register descriptions and the C code that reads, programs, or decodes the NBIO block.

## Important Macro Families

The opening `VF13_1` fragment completes most of virtual function 13's PCIe configuration image after the command-register boundary. It covers PCI status, revision and class-code bytes, cache-line/latency/header/BIST fields, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.

The same `VF13_1` block then defines PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, FLR capability/initiation, completion-timeout controls, ARI forwarding, atomic operation enables, ID-based ordering, LTR, OBFF, 10-bit tag support, link speed/width, ASPM/power-management controls, link disable/retrain, common clock, target link speed, equalization status, and link bandwidth notification state.

The VF MSI and MSI-X families describe capability-list linkage, MSI enable/multiple-message/64-bit/per-vector masking controls, MSI address/data/mask/pending storage, 64-bit aliases, MSI-X table size/function mask/enable bits, MSI-X table BIR/offset, and MSI-X PBA BIR/offset fields. These masks describe how interrupt programming state is packed in the virtual function's config image.

The VF vendor-specific and AER families define PCIe vendor-specific enhanced capability headers and payload dwords, AER enhanced capability headers, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered AER conditions include DLP, surprise down, poisoned TLP, flow control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked.

The VF ARI and RTR tails define `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. ARI fields expose MFVC/ACS function-group support, next-function number, function-group enable bits, and selected function group. RTR data fields expose readiness time reporting method/value/scale and readiness-valid state.

`BIF_CFG_DEV0_EPF0_VF14_1` and `BIF_CFG_DEV0_EPF0_VF15_1` are complete within this slice. Each repeats the full VF config-space pattern: identity/header/BAR fields, PCIe device/link capabilities and controls, MSI/MSI-X state, vendor-specific capability dwords, AER diagnostics, ARI fields, and RTR fields. This repetition is important for SR-IOV or GPU virtualization paths that address a specific virtual-function config image by suffix.

The final EPF1 fragment begins a physical or exposed function 1 config block rather than another EPF0 VF block. It covers vendor/device ID, command/status, revision and class-code bytes, header/BIST, BARs, adapter ID, ROM base address, cap pointer, interrupt and legacy timing fields, a vendor capability list, a writeable adapter ID alias, power-management capability/status/control fields, PCIe capability headers, device capability/control/status fields, and the first `LINK_CAP` shift fields through `ASPM_OPTIONALITY_COMPLIANCE__SHIFT`. Unlike the VF blocks in this chunk, EPF1 uses PMI and vendor-capability families before its PCIe capability chain and is incomplete at the chunk boundary.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these macros:

1. AMDGPU code selects a register offset from `nbio_4_3_0_offset.h`, usually through generated `reg...` names and SOC15/NBIO access helpers.
2. The driver reads a 16-bit or 32-bit hardware/config-space value, or prepares a value to write.
3. The driver applies this header's `__SHIFT` and `_MASK` constants directly or through `REG_SET_FIELD` and `REG_GET_FIELD`.
4. The resulting value is written, decoded for diagnostics, polled as hardware-owned state, cleared as sticky status, or propagated to higher-level PCIe, SR-IOV, reset, interrupt, power, or RAS logic.

Typical consumers of these fields are VF PCI config-space presentation, MSI/MSI-X setup, AER error reporting and clearing, function-level reset, PCIe link and power policy, ARI virtualization support, readiness-time reporting, and physical-function PCIe capability management.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and capability state owned by the GPU, platform firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SR-IOV management code.

The represented state includes identity and class-code values, BAR and ROM apertures, command/status bits, capability-list pointers, PCIe device/link capability and control/status fields, MSI/MSI-X address/data/mask/pending state, vendor-specific payloads, AER status/mask/severity/log data, ARI function-group controls, RTR readiness fields, and EPF1 power-management capability state. Some fields are static capabilities, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The generated masks do not encode access width, reset defaults, ownership, polling requirements, or side effects.

VF14 and VF15 are complete in this chunk. VF13 and EPF1 are boundary fragments and require adjacent chunks before making complete per-function claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` supplies matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h` supplies the field masks and shifts documented here.
- AMDGPU SOC15 and register helper macros consume the `__SHIFT`/`_MASK` convention for field composition, extraction, and register addressing.

Observed direct include sites for `nbio_4_3_0_sh_mask.h` in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. `nbio_v4_3.c` actively uses NBIO-generated masks for doorbell aperture setup, interrupt control, HDP flush registers, ROM offset control, LTR enablement, and doorbell interrupt handling. The SMU13 power-management files include the same NBIO 4.3.0 header family and use SOC15/PCIE access helpers for firmware flag and debug-register paths.

The semantic integration surface overlaps generic PCIe and platform components: command/status, BAR sizing/exposure, MSI/MSI-X delivery, PCIe link state, AER, ARI, RTR, LTR, OBFF, completion timeout, FLR, and power management. Correct behavior depends on pairing the right field mask with the right NBIO 4.3.0 register offset and access path.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the first `VF13_1_COMMAND` shift fields and ends before EPF1 `LINK_CAP` masks or any later EPF1 PCIe capability families.
- These are untyped preprocessor constants. A stale or misgenerated mask can compile cleanly while reading or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Suffix mistakes around `VF13_1`, `VF14_1`, and `VF15_1` can silently address the wrong virtual function and affect SR-IOV isolation, guest-visible config state, or diagnostics.
- Register-offset and field-mask mismatches are easy in generated headers. A valid `VF15_1_LINK_CNTL` mask applied to a `VF14_1`, EPF1, or non-NBIO offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect max payload, max read request, relaxed ordering, no-snoop, FLR, completion timeout, LTR, OBFF, atomic-op, ARI, link-control, or target-link-speed programming can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields have interrupt-delivery side effects. Wrong table BIR/offset, 64-bit alias, vector mask, pending, or enable handling can lose interrupts, route interrupts incorrectly, or unexpectedly unmask vectors.
- AER status, masks, severity, header logs, and TLP prefix logs may be sticky, hardware-owned, or write-one-to-clear. Generic read/modify/write treatment can clear useful diagnostics or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures, confuse resource sizing, or break guest-visible VF config space.
- EPF1 PMI fields interact with PCI power management. Wrong power-state, PME enable/status, data-select/scale, or bus-power handling can break suspend/resume or wake signaling.
- The source tree lacks a same-generation default header, so tests that depend on reset values need hardware reads, firmware specifications, or another authoritative register database.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU paths that include `nbio/nbio_4_3_0_sh_mask.h`; missing, duplicated, or renamed macros should surface in `nbio_v4_3.c` or SMU13 power-management files.
- Compare the covered register names against `nbio_4_3_0_offset.h` to confirm the VF13/VF14/VF15 and EPF1 register names and ordering remain synchronized.
- Boot affected NBIO 4.3.0 hardware and inspect PCIe config exposure: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, vendor-specific capability, AER, ARI, and RTR fields should decode consistently.
- In SR-IOV or virtualization configurations, create/remove VFs around the VF13-VF15 range, bind guest drivers, exercise VF FLR, and verify VF isolation, config-space access, ARI behavior, interrupt delivery, and reset paths.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate interrupt field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout behavior, LTR/OBFF state, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.
- For EPF1, validate power-management capability and PME behavior across D-state transitions, suspend/resume, and runtime power-management paths.

## Chunk Notes

- Lines 76467-77173 are the trailing part of `BIF_CFG_DEV0_EPF0_VF13_1`, beginning inside `COMMAND` and ending after `RTR_DATA2`.
- Lines 77174-77895 are a complete `BIF_CFG_DEV0_EPF0_VF14_1` config-space shift/mask block.
- Lines 77896-78617 are a complete `BIF_CFG_DEV0_EPF0_VF15_1` config-space shift/mask block.
- Lines 78618-78893 begin `BIF_CFG_DEV0_EPF1_1` and stop inside `LINK_CAP`; subsequent EPF1 fields are outside this work item.

### subset-b-002993: lines 78894-81346

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 78894-81346

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, dynamic allocations, locks, loops, branches, or direct register reads/writes in this range.

The assigned lines contain 2,128 `#define` entries across 319 commented register blocks plus two generated address-block markers. The slice starts in the middle of `BIF_CFG_DEV0_EPF1_1_LINK_CAP`, continues through the remaining `BIF_CFG_DEV0_EPF1_1` PCIe capability and extended-capability field definitions, covers a broad `BIF_CFG_DEV0_EPF2_1` function configuration image, and ends inside `BIF_CFG_DEV0_EPF3_1_LINK_CNTL`.

Although this file is under a `ceph-client` source mirror, the content is AMDGPU hardware metadata for GPU NBIO/BIF PCIe configuration space. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions for NBIO 4.3.0 PCIe endpoint-function configuration and extended-capability registers. Each hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or update that field.

Consumers pair these field macros with matching register offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` and, where defaults are needed, related generated default headers for other NBIO versions. Runtime AMDGPU code normally reaches these constants through register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The `EPF1_1` portion starts at the tail of `LINK_CAP`: link speed, width, ASPM/power-management support, latency, surprise-down reporting, data-link active reporting, bandwidth notification, ASPM optionality, and port number. It then covers PCIe link control/status, device/link capability 2 controls/status, MSI and MSI-X capability programming, vendor-specific enhanced capability fields, device serial number fields, AER enhanced capability fields, resizable BAR controls, power budget, dynamic power allocation, secondary PCIe capability, per-lane equalization controls, ACS, PASID, multicast, LTR, ARI, SR-IOV, VF resizable BAR, and route-through-router fields.

The `EPF2_1` address block begins at `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`. It defines a Type 0 PCI configuration image for endpoint function 2: vendor/device identity, command/status, revision/class bytes, cache line and latency, header/BIST, six BARs, CardBus CIS pointer, subsystem IDs, ROM base address, capability pointer, interrupt line/pin, min-grant/max-latency, vendor capability, PM capability/status, serial-bus release number, frame length adjustment, DBESL/DBESLD, PCIe capability, device/link control/status, MSI/MSI-X, vendor-specific capability, AER, BAR capability/control groups, power budget, DPA, ACS, PASID, ARI, and route-through-router data.

The `EPF3_1` address block begins at `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`. This chunk covers its identity/header fields, BAR and ROM resource fields, capability pointers, vendor and PM capability fields, PCIe capability, device capability/control/status, link capability, and the beginning of `LINK_CNTL`. The range stops at `BIF_CFG_DEV0_EPF3_1_LINK_CNTL__DRS_SIGNALING_CONTROL__SHIFT`, so the corresponding `LINK_CNTL` masks and all later EPF3 registers continue in the next chunk.

Notable field categories include PCI command/status bits, BAR aperture encodings, MSI address/data/mask/pending state, MSI-X table and pending-bit-array locations, AER uncorrectable/correctable error status/mask/severity and header/TLP prefix logs, resizable BAR sizing and control, PCIe power budget and DPA substate allocation, secondary capability equalization controls for lanes 0-15, ACS controls, PASID enablement and width, multicast filtering/blocking controls, LTR latency values, ARI next-function/function-group controls, SR-IOV VF counts/stride/page size/VF BARs, and opaque router payload registers.

## APIs, Types, And Functions

There are no C APIs, callable functions, or types in this chunk. The exported interface is the generated macro namespace itself:

- `BIF_CFG_DEV0_EPF1_1_*__SHIFT` and `BIF_CFG_DEV0_EPF1_1_*_MASK` for endpoint function 1 field layouts.
- `BIF_CFG_DEV0_EPF2_1_*__SHIFT` and `BIF_CFG_DEV0_EPF2_1_*_MASK` for endpoint function 2 field layouts.
- `BIF_CFG_DEV0_EPF3_1_*__SHIFT` and `BIF_CFG_DEV0_EPF3_1_*_MASK` for the beginning of endpoint function 3 field layouts.

The constants are untyped preprocessor values, mostly 16-bit or 32-bit field masks with `L` suffixes. Callers must supply the correct register offset, access method, access width, and access semantics; the macros only describe bit positions.

## Control Flow

This header has no executable control flow. Runtime behavior appears only in code that includes the generated header:

1. AMDGPU/NBIO code chooses a matching `regBIF_CFG_DEV0_EPF*_1_*` offset from the companion offset header.
2. The driver reads or composes a PCIe configuration-space dword through the PCIe or SOC15 register access layer.
3. It applies this header's shift/mask constants directly or via field helpers.
4. It writes control state, decodes capability/status state, clears sticky diagnostics, polls hardware-owned state, or exposes decoded values to PCIe, SR-IOV, interrupt, reset, power-management, or RAS flows.

Typical consuming flows include endpoint-function configuration, SR-IOV PF/VF setup, VF BAR/resource publication, MSI/MSI-X interrupt routing, PCIe link and power policy, DPA/LTR/ASPM decisions, AER/RAS diagnostics, ARI enumeration, ACS/PASID-related isolation controls, resizable BAR handling, and suspend/resume restore paths.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, platform PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SR-IOV management code.

The represented state spans static capabilities, software-programmed controls, hardware-updated status, and diagnostic logs. Identity, class, BAR, capability-list, SR-IOV, and VF BAR fields describe how functions and virtual functions are presented to the host. Link, LTR, DPA, power budget, and equalization fields describe power and signal behavior. MSI/MSI-X fields affect interrupt delivery state. AER fields can be sticky and may use write-one-to-clear behavior depending on the hardware register. ACS, PASID, ARI, multicast, and router fields affect enumeration, isolation, routing, and peer-to-peer behavior.

The generated shift/mask macros do not encode reset defaults, read-only versus writable ownership, write-one-to-clear behavior, polling requirements, firmware ownership, or required ordering around reads and writes.

## Dependencies And Integration Points

The immediate dependency is the generated NBIO 4.3.0 register database. This chunk must remain synchronized with `nbio_4_3_0_offset.h`, which supplies the matching register offsets and base indices. It also overlaps generated default-value data in newer NBIO headers such as `nbio_6_1_default.h`, which contains similarly named `EPF1_1`, `EPF2_1`, and `EPF3_1` default macros and is useful as a comparison point but not an authoritative default source for NBIO 4.3.0.

Direct in-tree includes of `nbio_4_3_0_sh_mask.h` appear in `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. `amdgpu_discovery.c` selects NBIO v4.3 operation tables, and `nbio_v4_3.c` provides integration for PCIe index/data access, HDP flush offsets, memory access enablement, doorbell range programming, interrupt handler control, clock gating/light sleep, LTR/ASPM programming, register remapping, and RAS error-event handling.

The important external integration surfaces are the Linux PCI core, platform firmware, IOMMU/virtualization policy, SR-IOV PF/VF lifecycle code, guest drivers, MSI/MSI-X interrupt delivery, PCIe AER handling, runtime power management, suspend/resume, reset/FLR handling, and diagnostic tools that dump PCIe configuration space.

## Risks And Edge Cases

- The chunk boundaries are artificial. It begins after most of `EPF1_1_LINK_CAP` shifts and ends before the `EPF3_1_LINK_CNTL` masks; adjacent chunks are required for complete per-register and per-function analysis.
- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can program or decode the wrong PCIe bit.
- The EPF1/EPF2/EPF3 blocks are highly repetitive. Suffix drift between endpoint functions can silently target the wrong function and affect isolation, interrupts, BAR resources, or diagnostics.
- Offset/header drift is dangerous: a valid-looking mask from this header applied to a mismatched register offset from another function or NBIO version can corrupt unrelated configuration state.
- PCIe link and device-control fields are platform-sensitive. Incorrect max payload, max read request, relaxed ordering, no-snoop, completion timeout, FLR, target speed, link disable, retrain, LTR, DPA, or ASPM-related programming can cause DMA ordering bugs, enumeration failures, reset hangs, or link instability.
- MSI/MSI-X fields have interrupt-delivery side effects. Mistakes in enable bits, message address/data, table BIR/offset, mask, pending, or 64-bit aliases can cause lost, misrouted, or unexpectedly unmasked interrupts.
- AER fields may be sticky or write-one-to-clear. Generic read/modify/write treatment can erase diagnostic evidence or leave errors masked with the wrong severity.
- SR-IOV and VF resizable BAR fields affect resource exposure and virtualization. Incorrect VF count, stride, page size, VF BAR, migration-state offset, or resize encoding can break VF enumeration or guest isolation.
- ACS, PASID, ARI, multicast, and router controls affect isolation and routing semantics. Misprogramming them can cause peer-to-peer access surprises, bad function enumeration, or IOMMU/guest-visible inconsistencies.
- Lane equalization and per-lane error fields depend on negotiated link width. Assuming all 16 lanes are active can misinterpret inactive-lane status or hide signal-integrity problems.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU with NBIO 4.3 support enabled so renamed, missing, or malformed macros surface in NBIO v4.3 and SMU13 users.
- Compare `EPF1_1`, `EPF2_1`, and `EPF3_1` register names against `nbio_4_3_0_offset.h` to confirm field blocks have matching offsets and base indices.
- Dump PCIe config space on affected hardware and verify identity, command/status, BARs, capability lists, PCIe capability, MSI/MSI-X, AER, ARI, SR-IOV, ACS, PASID, LTR, and router registers decode consistently with these masks.
- Enable SR-IOV where supported, create/remove VFs, bind guest drivers, exercise VF BAR sizing and VF migration-state exposure, and verify PF-visible VF counts, stride, page-size, and resource fields.
- Exercise MSI/MSI-X interrupt delivery under graphics, compute, and DMA workloads; watch for lost vectors, stuck pending bits, or unexpected masking.
- Run suspend/resume, runtime power transitions, PCIe link retraining, ASPM/LTR policy changes, DPA/power-budget queries, and FLR/reset paths while monitoring link speed/width, equalization state, and completion timeout behavior.
- Use AER/error-injection or platform diagnostics where available to verify correctable and uncorrectable status, masks, severity, header logs, and TLP prefix logs map to expected PCIe errors without losing diagnostic state.
- In ARI/ACS/PASID-capable configurations, verify function enumeration, isolation policy, PASID controls, multicast fields, and peer-to-peer behavior before and after VF lifecycle and reset operations.

## Chunk Notes

- Lines 78894-79047 start inside `BIF_CFG_DEV0_EPF1_1_LINK_CAP` and then define `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Lines 79048-80221 continue `EPF1_1` through MSI/MSI-X, vendor-specific capabilities, device serial number, AER, resizable BAR, power budget, DPA, secondary capability, lane equalization, ACS, PASID, multicast, LTR, ARI, SR-IOV, VF resizable BAR, and router data.
- Lines 80222-81210 define the `BIF_CFG_DEV0_EPF2_1` address block from identity/header registers through router data.
- Lines 81211-81346 begin the `BIF_CFG_DEV0_EPF3_1` address block and stop inside `LINK_CNTL`; the rest of EPF3 link control/status and later capabilities continue after this chunk.

### subset-b-002994: lines 81347-82050

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 81347-82050

## Scope

This chunk is the final 704-line segment of the generated AMDGPU NBIO 4.3.0 shift/mask header. It contains preprocessor-only bitfield definitions for the tail of the `BIF_CFG_DEV0_EPF3_1_*` PCIe configuration-space template and then closes the header guard. There are no C functions, structs, enums, runtime variables, locks, allocations, or executable statements in this range.

The chunk starts at the mask definitions for `BIF_CFG_DEV0_EPF3_1_LINK_CNTL`, then covers link status, PCIe Device/Link Capability 2, MSI and MSI-X, vendor-specific extended capability, Advanced Error Reporting, resizable/enhanced BAR capability registers, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, Readiness Time Reporting, one standalone `PCIE_LC_RXRECOVER_RXSTANDBY_CNTL` mask, and the final `#endif`. The corresponding offsets are expected in the matching NBIO 4.3.0 offset header; this file only defines field positions and masks.

## Purpose

`nbio_4_3_0_sh_mask.h` is generated hardware metadata for AMDGPU's NBIO 4.3.0 block. Its public interface is a macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate, preserve, clear, or compose that field.

This chunk describes PCI/PCIe configuration and extended-capability fields for device 0, endpoint function 3, instance/index `1`. The fields model hardware-visible PCIe state: link negotiation, extended PCIe capabilities, interrupt programming, error reporting, BAR sizing/control, power management capability data, access-control/isolation features, PASID/ARI routing, and reset/readiness timing. Driver code can combine these masks with register offsets and AMDGPU register helpers to decode or update NBIO config-space values without hard-coded bit numbers.

Although this source tree is under a `ceph-client` mirror, this header is AMDGPU hardware metadata and has no direct distributed-filesystem logic.

## Important Macro Families

The initial lines complete `BIF_CFG_DEV0_EPF3_1_LINK_CNTL` masks:

- `PM_CONTROL`, `LINK_DIS`, `RETRAIN_LINK`, `COMMON_CLOCK_CFG`, `EXTENDED_SYNC`, and `CLOCK_POWER_MANAGEMENT_EN` map ASPM/link-management controls.
- `HW_AUTONOMOUS_WIDTH_DISABLE`, `LINK_BW_MANAGEMENT_INT_EN`, `LINK_AUTONOMOUS_BW_INT_EN`, and `DRS_SIGNALING_CONTROL` affect autonomous width changes, bandwidth notifications, and dynamic speed/DRS signaling.

PCIe link and device extension fields follow:

- `LINK_STATUS` exposes negotiated link speed/width, link training, slot clock configuration, data-link-layer active state, and bandwidth-management/autonomous-bandwidth status bits.
- `DEVICE_CAP2` advertises completion-timeout ranges, ARI forwarding, AtomicOp routing and completion support, CAS128 completion support, no-relaxed-ordering P2P passing, LTR, TPH completer support, local node/system cache-line size, ten-bit tag support, OBFF support, end-to-end TLP prefix support, emergency power reduction, and FRS support.
- `DEVICE_CNTL2` controls completion timeout, ARI forwarding, AtomicOp requests and egress blocking, ID-based ordering for requests/completions, LTR, emergency power reduction request, ten-bit tag requester enable, OBFF, and end-to-end TLP prefix blocking.
- `DEVICE_STATUS2` is marked fully reserved by a single 16-bit reserved mask.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` describe supported link speeds, crosslink/skip-ordered-set capabilities, retimer presence detect support, target link speed, compliance/test controls, transmit margin, de-emphasis, equalization phases for 8 GT/s, crosslink resolution, downstream component presence, and DRS message receipt.

Interrupt capability definitions cover both MSI and MSI-X:

- `MSI_CAP_LIST` and `MSIX_CAP_LIST` define conventional capability ID and next-pointer bytes.
- `MSI_MSG_CNTL` defines MSI enable, multiple-message capability and enable fields, 64-bit address support, per-vector masking support, and extended message data support/enable bits.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, and their 64-bit layout variants define MSI target address, message data, mask, and pending fields.
- `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` define MSI-X table size, function mask, enable bit, table BAR indicator and offset, and PBA BAR indicator and offset.

Vendor-specific and Advanced Error Reporting definitions include:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` define VSEC metadata and two 32-bit scratch payload registers.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` defines AER extended-capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` cover DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked classes.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP, bad DLLP, replay number rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header log overflow.
- `PCIE_ADV_ERR_CAP_CNTL` defines first-error pointer, ECRC generation/check capability and enable bits, multi-header received capability/enable bits, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG[0-3]` and `PCIE_TLP_PREFIX_LOG[0-3]` provide full 32-bit masks for captured diagnostic TLP header and prefix log words.

BAR, power, isolation, addressing, and readiness capability families close the PCIe template:

- `PCIE_BAR_ENH_CAP_LIST` and `PCIE_BAR[1-6]_{CAP,CNTL}` define enhanced BAR capability metadata, supported BAR-size bitmaps, BAR index, total number, selected size, and upper supported-size bits for BAR1 through BAR6.
- `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP` define power budgeting table selection, base power, scale, PM state/substate, type, power rail, and whether the budget is system allocated.
- `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7` define Dynamic Power Allocation capability metadata, substate count, transition latency encoding, power allocation scale, current/enabled substate status, control, and per-substate power allocation bytes.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define Access Control Services support and controls for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, enhanced capability, egress vector size, I/O request blocking, downstream/upstream memory target access controls, and unclaimed request redirect.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL` define PASID capability metadata, execute-permission support, privileged-mode support, maximum PASID width, and enable bits.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` define Alternative Routing-ID Interpretation capability metadata, MFVC/ACS function-group capability bits, next function number, function-group enables, and selected ARI function group.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` define Readiness Time Reporting metadata and reset, data-link-up, FLR, D3hot-to-D0, and validity fields.
- `PCIE_LC_RXRECOVER_RXSTANDBY_CNTL__LC_RX_L0S_STANDBY_EN_MASK` is a standalone link-control mask for RX recover/RX standby L0s behavior.

## APIs, Types, And Functions

There are no callable APIs or declared C types in this chunk. The only interface is the generated macro set. Consumers are expected to combine these constants with:

- companion register/config offsets from the NBIO 4.3.0 offset header,
- generated reset/default metadata where present,
- AMDGPU/SOC15 register access macros,
- generic field helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`,
- PCI/NBIO config-space access paths that understand the relevant address space and access width.

The constants are simple integer literals, mostly with an `L` suffix. They do not carry access permissions, reset values, volatility, field width type, write-one-to-clear rules, polling requirements, or side-effect semantics. Those rules come from hardware documentation and the driver call sites.

## Control Flow

This header has no local control flow. Runtime control flow is external and typically looks like:

1. AMDGPU/NBIO, PCIe, SR-IOV, interrupt, reset, or diagnostic code selects an NBIO register or PCI config-space offset.
2. Code reads the raw register/config value through the appropriate MMIO or config access path.
3. The value is decoded with this file's shift and mask constants, often through register helper macros.
4. For writable control fields, code composes a new raw value by preserving unrelated bits, clearing the target mask, and inserting a shifted field value.
5. Hardware observes the write, or the driver uses the decoded status/capability value to decide enumeration, interrupt, link, power, AER, reset, or virtualization policy.

Likely flows include link training and retrain handling, PCIe capability enumeration, MSI/MSI-X setup, AER status reporting and masking, BAR sizing/resource control, power budgeting and DPA reporting, ACS/PASID/ARI virtualization setup, and FLR/reset readiness timing.

## State And Persistence Behavior

The header itself stores no state. It names bits in hardware-backed PCIe configuration and NBIO registers. Persistence depends on the GPU/NBIO reset domain, PCI reset, function-level reset, power management transitions, firmware initialization, driver save/restore, and host or hypervisor configuration.

The represented state falls into several categories:

- Static or mostly static capability state, such as supported link speeds, MSI/MSI-X capability data, AER/VSEC/enhanced-capability metadata, supported BAR sizes, power budget descriptors, DPA capabilities, ACS/PASID/ARI support, and RTR capability data.
- Host-programmed control state, such as link control, device control 2, MSI/MSI-X enable/mask/address/data, AER masks and severities, selected BAR sizes, DPA controls, ACS controls, PASID enablement, and ARI controls.
- Hardware-updated status state, such as link status/training/equalization bits, MSI pending bits, AER status and diagnostic logs, DPA substate status, and RTR validity/timing information.
- Side-effect trigger or policy bits, such as link disable/retrain, compliance entry, emergency power reduction request, interrupt enable/mask bits, and ACS/ARI/PASID routing controls.

Because this generated file only gives layouts, callers must enforce ordering and privilege rules. A mask that is harmless when used for readback can be dangerous when used for writes to status, interrupt, link-control, AER, or routing fields.

## Dependencies And Integration Points

This chunk depends on the rest of the generated AMDGPU NBIO register header set:

- `nbio_4_3_0_offset.h` supplies the matching `BIF_CFG_DEV0_EPF3_1_*` register/config offsets.
- Other NBIO 4.3.0 generated headers provide defaults or related register definitions when present.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` names for field extraction and update.

Integration points include AMDGPU NBIO initialization, PCIe link-management code, PCI capability/configuration handling, SR-IOV PF/VF management, interrupt setup, AER/error collection paths, power-management policy, reset/FLR handling, and virtualization/isolation plumbing. The ACS, PASID, and ARI fields are especially relevant where GPU functions interact with IOMMU, VFIO, hypervisor, or SR-IOV flows.

The final `#endif` means this range also closes the whole `_nbio_4_3_0_SH_MASK_HEADER` include guard. Any edits here can affect successful inclusion of the entire generated header, not just the final PCIe capability template.

## Risks And Edge Cases

- Generated register drift can compile cleanly while decoding or programming the wrong hardware bit. High-risk fields include MSI/MSI-X enable/mask/address/data, AER status/mask/severity, link retrain/disable/compliance controls, ACS/PASID/ARI controls, BAR sizing controls, and DPA/power-budget selectors.
- This chunk starts mid-register after `LINK_CNTL` shifts and earlier masks were defined in the previous chunk. Merge/reconciliation must not treat the visible `LINK_CNTL` masks as a complete register description for this chunk alone.
- Many status fields may be sticky, hardware-updated, or write-one-to-clear. The masks do not say which. Misusing AER status/log masks can destroy diagnostic evidence or leave active faults uncleared.
- Link control and equalization fields influence PCIe liveness. Wrong target speed, compliance, retrain, or de-emphasis handling can cause link training failures or performance degradation.
- MSI/MSI-X fields affect interrupt delivery. Incorrect message address/data, table/PBA offsets, or mask bits can lead to lost, repeated, or misrouted interrupts.
- BAR capability/control fields affect host resource sizing and mapping. Incorrect masks can produce invalid apertures or resource conflicts.
- ACS/PASID/ARI controls affect isolation, routing, and address-space tagging. Misprogramming can break VF discovery, IOMMU integration, peer-to-peer routing, or security assumptions.
- RTR timing fields should only be trusted when their validity bit and capability chain are sane. Underestimating reset, DL-up, FLR, or D3hot-to-D0 timing can cause premature access after reset or power transition.
- The standalone `PCIE_LC_RXRECOVER_RXSTANDBY_CNTL` mask is outside the `BIF_CFG_DEV0_EPF3_1_*` naming family; consumers should verify its offset/address-space pairing rather than infer one from neighboring PCI config definitions.

## Test Signals

- Compile AMDGPU with NBIO 4.3.0 support enabled. Direct macro users should catch missing, renamed, or malformed definitions.
- Run PCI enumeration on affected AMD hardware and verify stable capability chains, link status, BAR sizing, MSI/MSI-X capability reporting, AER capability reporting, ACS/PASID/ARI capability reporting, and no malformed config-space reads.
- Exercise MSI and MSI-X interrupt setup, masking, unmasking, and pending behavior; watch for lost interrupts, unexpected interrupt storms, or incorrect table/PBA placement.
- Validate PCIe link behavior across boot, suspend/resume, retrain, speed changes, and error recovery. Expected signals include sane negotiated width/speed, successful equalization, and no unexpected link-down events.
- Inject or observe PCIe AER events where possible and confirm status, mask, severity, header log, and TLP prefix log decoding matches hardware behavior without clearing evidence unexpectedly.
- Exercise SR-IOV/VFIO/hypervisor paths that rely on ACS, PASID, and ARI; expected signals are correct function enumeration, preserved isolation policy, and correct IOMMU/PASID behavior.
- Test FLR and power-state transitions with RTR timing honored. Hardware should not be accessed before reported reset/DL-up/FLR/D3hot-to-D0 readiness windows have elapsed.
- Compare generated masks against the authoritative register database or adjacent NBIO generation headers before changing this file; mechanical consistency is a strong validation signal for generated register metadata.
