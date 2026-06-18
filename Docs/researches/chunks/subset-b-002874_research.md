# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h lines 4954-7387

## Scope

This chunk covers a generated AMD NBIF 6.3.1 register-offset header section. It starts at the tail of the MSI-X vector table with `regPCIEMSIX_VECT32_CONTROL_BASE_IDX`, then defines complete MSI-X vector entries for vectors 33 through 255. The later lines switch through several NBIF address blocks: RCC PFC USB and PD-controller restore registers, the MSI-X pending-bit array, RCC shadow and BIF SWUS indirect-access registers, RCC strap registers, BIF reset controls, and the first part of the BIF miscellaneous block.

The file is data-only C preprocessor material. It defines no functions, structs, variables, runtime control flow, locks, memory allocations, or direct MMIO operations. Its public interface is the generated register-address convention:

- `reg<REGISTER>` expands to the register offset used by AMDGPU register access helpers.
- `reg<REGISTER>_BASE_IDX` expands to the SOC15 base-index selector for the IP/register aperture. In this chunk every visible base index is `5`.

## Purpose

This header is part of the generated NBIF register ABI for ASIC version 6.3.1. NBIF is the northbridge/PCIe-facing block used by the AMD GPU driver for PCIe function control, MSI-X interrupt programming, reset and function-level-reset handling, power-state transitions, strap-derived configuration, and miscellaneous BIF controls.

Consumers include the matching NBIF 6.3.1 shift/mask header and AMDGPU/SOC15 register helpers that combine a base index, register offset, and field definitions into MMIO accesses. This chunk supplies addresses only; bit layout and semantics are provided by companion `*_sh_mask.h` files and by the owning driver code.

## Important Macro Families

### PCIe MSI-X Vector Table

The chunk begins in the `nbif_pciemsix_0_usb_MSIXTDEC` table. Line 4954 is only `regPCIEMSIX_VECT32_CONTROL_BASE_IDX`, so the vector-32 address macros themselves belong to the previous chunk. Complete definitions then cover vectors 33 through 255:

- `regPCIEMSIX_VECTn_ADDR_LO` and `regPCIEMSIX_VECTn_ADDR_HI` define the low and high message-address dwords.
- `regPCIEMSIX_VECTn_MSG_DATA` defines the message data register.
- `regPCIEMSIX_VECTn_CONTROL` defines the vector control register.

The offsets are contiguous four-dword records. Vector 33 starts at `0x1e084` and vector 255 ends at `0x1e3ff`; for each vector the fields appear as address-low, address-high, message-data, and control. These addresses are used when the driver or PCI/MSI-X infrastructure programs interrupt delivery for GPU functions exposed through this NBIF instance.

### RCC PFC Restore Blocks

Two short `RCCPFCDEC` blocks follow:

- `nbif_rcc_pfc_usb_RCCPFCDEC`, base address `0x10134400`, provides `regRCC_PFC_USB_RCC_PFC_LTR_CNTL`, `PME_RESTORE`, `STICKY_RESTORE_0` through `STICKY_RESTORE_5`, and `AUXPWR_CNTL` at offsets `0xd140` through `0xd148`.
- `nbif_rcc_pfc_pd_controller_RCCPFCDEC`, base address `0x10134600`, mirrors the same LTR, PME restore, sticky restore, and auxiliary-power control pattern at offsets `0xd1c0` through `0xd1c8`.

These macros name registers that preserve or restore PCIe/power-management state across low-power or reset transitions.

### MSI-X Pending-Bit Array

The `nbif_pciemsix_0_usb_MSIXPDEC` block, base address `0x10179000`, defines `regPCIEMSIX_PBA_0` through `regPCIEMSIX_PBA_7` at offsets `0x1e400` through `0x1e407`. These are the MSI-X pending-bit array registers paired with the vector-table region above. Software should treat them as interrupt pending/status storage rather than ordinary policy configuration.

### Shadow and SWUS Indirect Access

The `nbif_rcc_shadow_reg_shadowdec` block, base address `0x10130000`, defines:

- `regSHADOW_COMMAND`
- `regSHADOW_BASE_ADDR_1`
- `regSHADOW_BASE_ADDR_2`
- `regSHADOW_IRQ_BRIDGE_CNTL`
- `regSUC_INDEX`
- `regSUC_DATA`

The `nbif_bif_swus_SUMDEC` block, base address `0x1013b000`, defines `regSUM_INDEX`, `regSUM_DATA`, and `regSUM_INDEX_HI`. The index/data naming indicates indirect register windows: users select an internal index and then read or write data through a companion data register. Correct sequencing is controlled by driver code and hardware rules, not by this header.

### RCC Strap Registers

The `nbif_rcc_strap_rcc_strap_internal` block, base address `0x10100000`, occupies the largest non-MSI-X part of this chunk. It defines strap offsets for:

- Device-port straps for device 0, device 1, and device 2: `PORT_STRAP0` through `PORT_STRAP14` at `0xc400`, `0xc480`, and `0xc500` ranges.
- BIF-level straps: `regRCC_STRAP1_RCC_BIF_STRAP0` through `STRAP6` at `0xc600` through `0xc606`.
- Endpoint-function straps for device 0 EPF0 through EPF7, device 1 EPF0 through EPF5, and device 2 EPF0 through EPF2, using sparse offset groups from `0xd000` through `0xd90e`.

These registers expose strap-latched hardware configuration for PCIe/device/function behavior. The sparse numbering is intentional: not every possible strap index is represented for every EPF group in this chunk.

### BIF Reset and Power-State Registers

The `nbif_bif_rst_bif_rst_regblk` block, base address `0x10100000`, defines reset, interrupt, and power-state offsets:

- Global and self reset controls: `regHARD_RST_CTRL`, `regRSMU_SOFT_RST_CTRL`, `regSELF_SOFT_RST`, `regSELF_SOFT_RST_2`, plus `regBIF_GFX_DRV_VPU_RST`.
- Miscellaneous reset controls: `regBIF_RST_MISC_CTRL`, `regBIF_RST_MISC_CTRL2`, and `regBIF_RST_MISC_CTRL3`.
- Per-function FLR reset controls for device 0 PF0 through PF6.
- Reset/power interrupt status and mask registers for instance reset, PF FLR, D3hot-to-D0, generic power, and PF D-state events.
- `regBIF_PF_FLR_RST`, per-PF D-state value registers for device 0 PF0 through PF6, per-PF D3hot-to-D0 reset controls, `regBIF_PORT0_DSTATE_VALUE`, and `regBIF_USB_SHUB_RS_RESET_CNTL`.

These addresses are integration points for device reset, suspend/resume, function-level reset, and power-management paths.

### BIF Miscellaneous Registers

The chunk ends in the `nbif_bif_misc_bif_misc_regblk` block, base address `0x10100000`. Visible macros include:

- ROM/BIOS and scratch/control registers: `regREGS_ROM_OFFSET_CTRL`, `regNBIF_STRAP_BIOS_CNTL`, `regMISC_SCRATCH`, `regINTR_LINE_POLARITY`, `regINTR_LINE_ENABLE`, and `regOUTSTANDING_VC_ALLOC`.
- BIFC controls and logs: `regBIFC_MISC_CTRL0`, `regBIFC_MISC_CTRL1`, `regBIFC_BME_ERR_LOG_LB`, `regBIFC_LC_TIMER_CTRL`, `regBIFC_RCCBIH_BME_ERR_LOG0`, and DMA attribute override/control registers for device 0 functions.
- Miscellaneous BIFC controls for throttling, host arbitration, GSI, PCIe function behavior, PASID checking/status, SDP controls, ATHUB activity, and the start of performance controls at `regBIFC_PERF_CNTL_0`.

The line range ends at `regBIFC_PERF_CNTL_0 0xe830`; the matching base-index macro and remaining BIF miscellaneous definitions continue in a later chunk.

## Control Flow and State Behavior

There is no executable control flow in this chunk. Its behavior is compile-time symbol substitution for register offsets and base indices. Runtime ordering, locking, polling, interrupt masking, reset sequencing, and error handling all live in the AMDGPU/NBIF code that consumes these macros.

The state represented by these offsets is hardware state. Some registers are persistent configuration or restore state, such as straps, PFC sticky restore registers, DMA attribute controls, PASID controls, interrupt-line settings, and miscellaneous BIFC policy controls. Others are status or command-like, including MSI-X PBA registers, reset interrupt status/mask registers, FLR/D3hot reset controls, scratch registers, and performance-control registers.

The MSI-X vector table is especially stateful: each vector has address, data, and control registers that determine interrupt delivery. Incorrect writes can redirect interrupts, mask vectors unexpectedly, or leave pending bits uncleared. The reset and D-state registers also carry sequencing-sensitive state where write order and acknowledgement polling matter.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register-header ecosystem:

- Companion NBIF 6.3.1 shift/mask headers provide field positions and masks for many of these offsets.
- AMDGPU SOC15 helpers use base index `5` together with the `reg...` offsets to access the correct NBIF aperture.
- PCI/MSI-X setup, interrupt handling, reset, suspend/resume, FLR, RAS/error logging, and PCIe link/device-function management are the likely consumers of the address families visible here.

The generated names are version-specific. Similar register names in other NBIF versions should not be assumed to have identical offsets, base-index values, or field layouts.

## Risks

- Offset drift is high impact. A wrong MSI-X vector-table address can program the wrong vector's message address, message data, or mask/control word.
- The line-range boundary is mid-family at both ends: vector 32 is only represented by one base-index macro here, and BIF miscellaneous performance-control definitions continue after the chunk. Per-file reconciliation must merge neighboring chunks before making whole-file coverage claims.
- The MSI-X vector table is mechanically repetitive. Insertions, deletions, or off-by-one vector numbering errors can silently remap hundreds of interrupt registers.
- All visible macros use `_BASE_IDX 5`; changing any one base index would redirect SOC15 access to the wrong register aperture even if the offset value looked correct.
- Strap and restore registers represent hardware-latched or power-management state. Treating them as ordinary mutable configuration can break PCIe enumeration, resume, or endpoint-function behavior.
- Reset and D-state registers are sequencing-sensitive. Incorrect ordering around FLR, D3hot-to-D0, soft reset, or interrupt status/mask handling can hang the device or lose reset-completion events.
- Indirect index/data registers such as `SUC_INDEX`/`SUC_DATA` and `SUM_INDEX`/`SUM_DATA` are prone to races if consumers do not serialize index selection and data access.
- PASID, DMA attribute, BME error-log, and ATHUB activity controls affect isolation, error reporting, and memory-transaction behavior. Bad field definitions or wrong offsets can create security, reliability, or performance regressions.

## Test and Validation Signals

Useful validation is mostly compile, integration, and hardware bring-up coverage:

- Build AMDGPU code paths that include `nbif_6_3_1_offset.h` and the matching NBIF shift/mask header; this catches missing or renamed generated macros.
- Exercise MSI-X interrupt allocation and interrupt delivery on ASICs using NBIF 6.3.1, including vector masking/unmasking and pending-bit behavior.
- Run suspend/resume and runtime power-management tests that cover RCC PFC restore/sticky state and auxiliary-power controls.
- Run PCIe FLR, soft reset, D3hot-to-D0, and device reset tests for device 0 PF0 through PF6 paths, verifying reset status/mask interrupts and D-state value registers.
- Validate strap-derived configuration against expected PCIe/device/function enumeration, especially for sparse EPF strap groups.
- Check indirect-access users for serialized `INDEX`/`DATA` sequences around `SUC_*` and `SUM_*` registers.
- Run error-reporting and stress tests that touch BIFC BME logs, DMA attribute overrides, PASID controls/status, ATHUB activity controls, and BIFC performance controls.

## Unresolved Cross-Chunk References

The previous chunk contains the address macros for MSI-X vector 32 and probably the earlier vectors in the same table. This chunk only contains `regPCIEMSIX_VECT32_CONTROL_BASE_IDX` before continuing with vector 33. The next chunk is needed to complete the BIF miscellaneous block because this range ends at `regBIFC_PERF_CNTL_0` without the corresponding `_BASE_IDX` line or later miscellaneous registers.
