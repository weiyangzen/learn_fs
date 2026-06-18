# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 2467-4944

## Scope

This chunk covers a generated NBIO 2.3 register-offset header slice. It starts in the tail of the `nbio_nbif0_bif_cfg_dev0_epf0_vf2_bifcfgdecp` address block, covering VF2 PCIe AER log, ATS, and ARI config-space offsets, then contains the complete PCI configuration-space offset maps for `DEV0_EPF0` virtual functions VF3 through VF30. The final portion begins the per-VF MMIO/RCC/BIF register maps for VF0 and VF1:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf3_bifcfgdecp` through `vf30_bifcfgdecp`
- `nbio_nbif0_bif_bx_dev0_epf0_vf0_SYSPFVFDEC`
- `nbio_nbif0_rcc_dev0_epf0_vf0_BIFPFVFDEC1`
- `nbio_nbif0_bif_bx_dev0_epf0_vf0_BIFPFVFDEC1`
- `nbio_nbif0_rcc_dev0_epf0_vf0_BIFDEC2`
- the start of the same `SYSPFVFDEC`, `BIFPFVFDEC1`, and BIF register families for VF1

The source is a hardware register map: it defines preprocessor constants only. There are no C functions, structs, variables, dynamic allocation, locks, or executable control flow in this range.

## Purpose

`nbio_2_3_offset.h` provides the numeric register offsets used by AMDGPU NBIO 2.3 code and shared SOC15 register helpers. This chunk specifically describes the SR-IOV virtual-function-facing PCI configuration and BIF/RCC register windows for the NBIO northbridge I/O block.

The `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` macros map PCI/PCIe configuration-space offsets relative to base address `0x0` for virtual functions. These cover standard PCI header fields, PCIe capability fields, MSI/MSI-X capability offsets, vendor-specific extended capability offsets, advanced error reporting offsets, ATS capability offsets, and ARI capability offsets.

The `mmBIF_BX_DEV0_EPF0_VF*_*` and `mmRCC_DEV0_EPF0_VF*_*` macros map memory-mapped NBIO/BIF/RCC registers for virtual functions. Each `mm*` register is accompanied by a `*_BASE_IDX` macro that selects the SOC15 register-base segment used by `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.

## Important Macro Families

### VF PCI Configuration Offsets

The dominant pattern is one repeated config-space map per VF. VF3 through VF30 each define the same offset names and values:

- PCI identity and command/status fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Standard header fields: cache line, latency, header type, BIST, BARs `BASE_ADDR_1` through `BASE_ADDR_6`, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus the second-generation `*_CAP2`, `*_CNTL2`, and `*_STATUS2` fields.
- MSI/MSI-X capability fields: `MSI_CAP_LIST`, message control/address/data/mask/pending offsets, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Extended capability fields: vendor-specific capability at `0x0100`, AER at `0x0150`, TLP header/prefix logs, ATS at `0x02b0`, and ARI at `0x0328`.

The chunk begins just before VF3, with the tail of the VF2 map from `PCIE_UNCORR_ERR_STATUS` through `PCIE_ARI_CNTL`. That means the chunk document must be reconciled with the previous chunk for the full VF2 map.

### VF MMIO Index/Data Apertures

`nbio_nbif0_bif_bx_dev0_epf0_vf0_SYSPFVFDEC` and the start of the VF1 equivalent define:

- `mmBIF_BX_DEV0_EPF0_VF*_MM_INDEX`
- `mmBIF_BX_DEV0_EPF0_VF*_MM_DATA`
- `mmBIF_BX_DEV0_EPF0_VF*_MM_INDEX_HI`

These are indirect index/data apertures for VF-addressed MMIO access. The base index is `0`, distinguishing this decode space from the BIF/RCC register windows later in the chunk.

### VF RCC Configuration and Doorbell Aperture

The `mmRCC_DEV0_EPF0_VF*_RCC_*` families in `BIFPFVFDEC1` provide per-VF RCC offsets:

- `RCC_ERR_LOG`
- `RCC_DOORBELL_APER_EN`
- `RCC_CONFIG_MEMSIZE`
- `RCC_CONFIG_RESERVED`
- `RCC_IOV_FUNC_IDENTIFIER`

These expose virtual-function error logging, doorbell aperture enablement, memory-size reporting, reserved configuration, and SR-IOV function identity. Their `*_BASE_IDX` values are `2`, so callers must route them through the correct NBIO register base.

### VF BIF Doorbell, HDP Flush, Transaction, and Mailbox Registers

The VF0 `nbio_nbif0_bif_bx_dev0_epf0_vf0_BIFPFVFDEC1` block, continued for VF1 at the end of this chunk, includes:

- `BIF_BME_STATUS` and `BIF_ATOMIC_ERR_LOG`
- self-ring doorbell GPA aperture base high/low and control registers
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL`
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE`
- `BIF_TRANS_PENDING`
- `NBIF_GFX_ADDR_LUT_BYPASS`
- transmit and receive mailbox message buffers `MAILBOX_MSGBUF_TRN_DW0..3` and `MAILBOX_MSGBUF_RCV_DW0..3`
- `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`

These registers are the VF-side control surface for host/device coherency flushes, doorbell self-ring setup, outstanding BIF transaction status, and VM/hypervisor mailbox exchange.

### VF0 MSI-X Table Window

`nbio_nbif0_rcc_dev0_epf0_vf0_BIFDEC2` defines a small GFX MSI-X table for VF0:

- `GFXMSIX_VECT0_ADDR_LO/HI`, `MSG_DATA`, and `CONTROL`
- the same four-register layout for vectors 1 through 3
- `GFXMSIX_PBA`

These offsets use base index `3`. They are separate from the PCI config-space `MSIX_TABLE` and `MSIX_PBA` capability offsets; this block maps the actual register-window representation of the MSI-X vector table and pending-bit array.

## Integration Points

`drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this header along with `nbio_2_3_default.h` and `nbio_2_3_sh_mask.h`. Most driver code works through SOC15 helpers that combine a block ID, instance, register offset, and base index into an MMIO address. Examples in that file include `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`.

The most direct consumer in the inspected code is `nbio_v2_3_init_registers()`, which computes `adev->rmmio_remap.reg_offset` from `SOC15_REG_OFFSET(NBIO, 0, mmBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL) << 2` for ASICs that do not use the generic MMIO hole. That value is later used by `nbio_v2_3_remap_hdp_registers()` to program `mmREMAP_HDP_MEM_FLUSH_CNTL` and `mmREMAP_HDP_REG_FLUSH_CNTL`, allowing KFD/user-visible remapped HDP flush offsets to hit the correct NBIO register.

The `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` macros also align with sibling generated defaults in `nbio_2_3_default.h`. The offset header supplies the byte offsets; the default header supplies reset values for the same register names. Bit-level interpretation, where available, lives in `nbio_2_3_sh_mask.h`.

## Control Flow

There is no local control flow in this chunk. Runtime control flow is external:

1. AMDGPU selects NBIO 2.3 support during device bring-up.
2. NBIO helper code includes this generated offset header.
3. Register helper macros resolve `mm*` constants and `*_BASE_IDX` constants into physical MMIO addresses.
4. Driver code reads, writes, or remaps those addresses to configure doorbells, HDP flushes, interrupts, memory-size visibility, PCIe behavior, and virtualization-facing register access.

For PCI config-space macros, the flow is generally indirect through PCIe configuration access or SMN/PCIE index-data paths rather than ordinary C calls inside this header.

## State and Persistence Behavior

The header itself has no persistent state. It names hardware state that persists in the GPU/NBIO registers across driver operations until reset, power-state transition, FLR, VF reset, or explicit driver/firmware writes.

Important state represented by this chunk includes per-VF PCI identity and capability presentation, MSI/MSI-X programming state, AER status and log registers, ATS/ARI capability control, doorbell aperture enablement, HDP coherency flush request/done state, BIF transaction pending status, mailbox contents/control, and VF MSI-X vector table contents.

Because these are VF-specific registers, persistence and visibility are affected by SR-IOV mode. PF, VF, firmware, hypervisor, and guest driver paths may see different access permissions or reset domains for the same logical register family.

## Dependencies

This chunk depends on the AMDGPU SOC15 register access framework and the surrounding generated NBIO register headers:

- `nbio_2_3_offset.h` for register offsets and base indices.
- `nbio_2_3_sh_mask.h` for field masks and shifts used with the offsets.
- `nbio_2_3_default.h` for reset/default values matching many of the same names.
- AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and `WREG32_FIELD15`.
- PCIe/SR-IOV conventions for VF configuration space, MSI/MSI-X, ATS, ARI, and AER capability layout.

The offset values are hardware ABI data. They must match the NBIO 2.3 register specification and the firmware/hypervisor view of PF/VF register decode windows.

## Risks

- Off-by-one or wrong-VF macro use can address a different VF's PCI config or BIF/RCC state. This is especially risky because VF3 through VF30 repeat identical offset values with only the VF number changing.
- Using a correct offset with the wrong `*_BASE_IDX` resolves to the wrong SOC15 register segment. The VF0/VF1 `SYSPFVFDEC` entries use base index `0`, `BIFPFVFDEC1` entries use `2`, and the VF0 MSI-X table block uses `3`.
- PCI config-space offsets are byte offsets, while many MMIO register offsets are dword-oriented and are commonly shifted by `<< 2` when forming byte addresses. The HDP remap path in `nbio_v2_3.c` is an example where this distinction matters.
- MSI and MSI-X fields intentionally overlap in config space depending on 32-bit versus 64-bit MSI layout, such as `MSI_MSG_ADDR_HI` sharing `0x00a8` with `MSI_MSG_DATA` and `MSI_MASK_64` sharing `0x00b0` with `MSI_PENDING`. Consumers must interpret those offsets according to the active capability format.
- AER, mailbox, HDP flush, and doorbell registers can be shared with firmware, PF, hypervisor, or guest VF code. Uncoordinated writes can lose diagnostics, break coherency flush completion, misroute interrupts, or disrupt VF communication.
- Generated headers are not self-validating. A typo or stale hardware drop can compile cleanly but produce incorrect MMIO traffic only visible on affected ASICs.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware bring-up oriented:

- Build coverage for AMDGPU NBIO 2.3 code proves all referenced macros remain defined and compatible with the SOC15 helper interfaces.
- SR-IOV VF boot and teardown should expose sane PCI IDs, BARs, MSI/MSI-X capabilities, ATS/ARI capabilities, and AER capability chains for VF3 through VF30 when those functions are enabled.
- KFD and graphics workloads should continue to complete HDP flushes after `nbio_v2_3_init_registers()` remaps the VF0 `HDP_MEM_COHERENCY_FLUSH_CNTL` register. Failures would appear as coherency bugs, stuck flush waits, or user-mode queue hangs.
- Doorbell tests should verify VF doorbell aperture enablement and self-ring aperture programming without spurious BIF doorbell interrupts.
- Interrupt tests should validate MSI/MSI-X vector programming and pending-bit behavior for the VF0 `GFXMSIX` table.
- Error-injection or PCIe AER diagnostics should confirm correct AER status, mask, severity, header log, and TLP prefix log visibility.
- Static checks can compare the repeated VF3-VF30 config maps against neighboring chunks and against `nbio_2_3_default.h` to detect missing or drifted generated entries.
