# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h lines 9164-10004

## Scope

This chunk is the tail of the generated AMD NBIO 7.9.0 register offset header. It contains C preprocessor constants only: 361 register-offset macros and 361 matching `_BASE_IDX` macros, followed by the closing header guard. The requested range begins in the VF0 RCC block and then covers the repeated virtual-function register windows for VF1 through VF7.

The content is source-tree-aligned with AMDGPU's `drivers/gpu/drm/amd/include/asic_reg/nbio` generated register database. It does not define executable code, structs, enums, allocation paths, callbacks, or locks.

## Purpose and Register Families

The macros identify NBIO/BIF/RCC register addresses for SR-IOV endpoint function `DEV0_EPF0` virtual functions. They are used by AMDGPU SOC15 register access helpers to compute MMIO offsets for NBIO 7.9.0 hardware.

The covered address blocks are:

- VF0 RCC `BIFDEC2` MSI-X tail: `regRCC_DEV0_EPF0_VF0_GFXMSIX_VECT{0..3}_*` and `regRCC_DEV0_EPF0_VF0_GFXMSIX_PBA`.
- VF1 through VF7 `BIFPFVFDEC1`: BIF bus-master/atomic status, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate controls, GPU HDP flush request/done, BIF transaction pending, NBIF graphics address LUT bypass, and mailbox transmit/receive/control/interrupt registers.
- VF1 through VF7 `SYSPFVFDEC`: indexed MMIO access registers `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- VF1 through VF7 RCC `BIFPFVFDEC1`: RCC error log, doorbell aperture enable, configured memory size/reserved registers, and IOV function identifier.
- VF1 through VF7 RCC `BIFDEC2`: four MSI-X vector table entries with address low/high, message data, control, and the pending-bit array register.

The repeated VF blocks intentionally share the same per-function register offsets, while the macro names encode the virtual-function number. `_BASE_IDX` selects the NBIO address-base slot used by the SOC15 register-offset machinery.

## Important APIs, Types, and Macros

This header exposes generated register-address macros in the AMDGPU naming convention:

- `regBIF_BX_DEV0_EPF0_VF<n>_*` for BIF virtual-function registers.
- `regRCC_DEV0_EPF0_VF<n>_*` for RCC virtual-function registers, including MSI-X table/PBA registers.
- `*_BASE_IDX` companions that tell `SOC15_REG_OFFSET()` and `RREG32_SOC15`/`WREG32_SOC15` style helpers which base-index table entry to apply.

The constants are not public APIs by themselves. They are consumed by NBIO and RAS code that includes `nbio/nbio_7_9_0_offset.h`, most directly `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`. A concrete integration point in `nbio_v7_9_set_reg_remap()` uses `regBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` via `SOC15_REG_OFFSET()` to choose the HDP flush register remap location for SR-IOV VF or large-page configurations.

The companion `nbio_7_9_0_sh_mask.h` supplies bit shifts and masks for field-level operations. This `*_offset.h` file only identifies register locations.

## Control Flow and Data Flow

There is no control flow inside this chunk. Runtime behavior is indirect:

1. AMDGPU selects NBIO 7.9.0 support for a device generation and includes this generated header.
2. Driver code names a register macro and passes it to a SOC15 helper such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, or an extended instance-aware variant.
3. The helper combines the register offset with the macro's `_BASE_IDX`, NBIO instance information, and the device's MMIO base mapping.
4. Reads and writes then interact with hardware state such as doorbell aperture control, HDP coherency, mailbox buffers, transaction-pending status, or MSI-X vector state.

The data represented here is address metadata. Hardware supplies or consumes the actual register values. For example, HDP flush request/done registers coordinate cache coherency with the host data path, mailbox registers carry PF/VF or VM/HV communication words, and MSI-X table/PBA registers describe interrupt delivery state for each virtual function.

## State and Persistence

The header itself has no mutable software state and no persistence. Its constants are fixed at compile time.

The state addressed by these macros persists in hardware or PCIe configuration/MMIO-visible register space according to the NBIO reset and power domains:

- Doorbell aperture base/control and RCC doorbell enable registers affect how a VF's doorbell MMIO range is exposed and routed.
- HDP coherency and GPU HDP flush request/done registers represent synchronization with memory-visible GPU/CPU data paths.
- Mailbox transmit/receive/control/interrupt registers hold communication state between the VF-facing BIF path and management or virtualization components.
- `BIF_TRANS_PENDING`, error logs, BME status, and atomic error logs expose transient hardware status that may be asynchronously updated by the device.
- MSI-X vector address/data/control and PBA registers reflect interrupt-table state for each VF and must match PCI/MSI-X expectations.

Because these are generated address constants, an incorrect value becomes a systematic runtime hardware access bug wherever the macro is used.

## Dependencies and Integration Points

This chunk depends on the AMDGPU SOC15/NBIO register access framework and the generated NBIO 7.9.0 register database layout. It integrates with:

- `amdgpu/nbio_v7_9.c`, which includes this header for NBIO initialization, register remapping, doorbell setup, clock-gating controls, and HDP flush register location logic.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes the offset and shift/mask headers while wiring NBIO RAS interrupt sources, even though the file's current handlers are dummy registration hooks.
- `nbio_7_9_0_sh_mask.h`, used with this offset file for field extraction and update.
- AMDGPU SR-IOV paths, where PF and VF register windows differ and VF-specific HDP/doorbell/mailbox/MSI-X offsets must resolve correctly.
- PCIe/MSI-X and virtualization semantics for BME, atomic operations, mailboxes, doorbells, function identifiers, and pending interrupts.

The chunk also mirrors similar generated VF blocks in other NBIO/NBIF generation headers, which is a useful cross-check but not a substitute for the NBIO 7.9.0 hardware register specification.

## Risks and Edge Cases

- The range starts at line 9164, just after most of VF0's BIF/RCC PFVF decode registers. Merge/reconciliation should treat this as a chunk boundary: VF0's HDP and mailbox definitions are in the preceding chunk, while VF0's MSI-X RCC tail is here.
- `_BASE_IDX` values are as important as the raw offsets. A correct register number with the wrong base index can access the wrong NBIO aperture.
- VF1 through VF7 are highly repetitive. Generated copy/paste or table-generation errors would likely affect only one VF number and may not appear unless that VF is enabled under SR-IOV.
- Doorbell aperture and HDP coherency registers are synchronization-sensitive. Wrong offsets can break queue submission, host/GPU coherency, or interrupt progress without producing an obvious compile-time failure.
- Mailbox and VM/HV mailbox registers are virtualization-facing. Accessing the wrong VF mailbox can leak state across functions or prevent PF/VF coordination.
- MSI-X vector and PBA offsets must remain aligned with PCI/MSI-X table layout. Incorrect offsets can misroute interrupts, leave vectors masked, or corrupt pending-bit accounting.
- Status/log registers such as BME status, atomic error log, RCC error log, and transaction-pending are hardware-updated; driver code must respect their documented clear/read semantics from the hardware spec and companion masks.

## Test and Validation Signals

Validation is mostly compile-time and hardware-integration oriented:

- Build AMDGPU configurations that include `nbio_7_9_0_offset.h`; missing or renamed macros fail at compile time in NBIO/RAS users.
- Boot NBIO 7.9.0 hardware in PF mode and SR-IOV VF mode and verify `nbio_v7_9_set_reg_remap()` maps the HDP memory coherency flush register as expected.
- Exercise SR-IOV with multiple enabled VFs, not only VF0, and verify queue doorbells, HDP flush completion, and mailbox traffic for VF1 through VF7.
- Inspect MSI-X behavior per VF: vector programming, masking/unmasking, pending-bit updates, and interrupt delivery under load.
- Use PCIe/AER or device diagnostics to confirm BME status, atomic error logging, RCC error logging, and BIF transaction-pending registers report plausible values.
- Run suspend/resume, FLR, hot reset, and GPU reset paths to ensure VF doorbell, mailbox, HDP, and MSI-X state is either preserved or reinitialized by the owning driver/firmware path.
