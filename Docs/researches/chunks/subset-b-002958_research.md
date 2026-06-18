# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 12431-14904

## Scope

This chunk is a generated AMD NBIO 4.3.0 register offset header segment. It contains only C preprocessor constants: one `reg...` address macro and one matching `reg..._BASE_IDX` macro per visible register. There are no functions, structs, enums, variables, executable branches, loops, locks, allocation paths, or direct MMIO accesses in this range.

The assigned range contains 2,396 `#define` lines: 1,198 register-offset macros and 1,198 base-index macros. It starts in the middle of the PCIe MSI-X table, at `regPCIEMSIX_VECT173_ADDR_LO`, runs through vectors 173-255 and pending-bit-array registers `regPCIEMSIX_PBA_0` through `regPCIEMSIX_PBA_7`, then covers RCC shadow/strap, BIF reset/misc/RAS/RCC/BX, and GDC SION/doorbell offset blocks. The last line is only the next address-block marker, `nbio_nbif0_gdc_GDCDEC`; the `GDCDEC` registers themselves continue after this chunk.

Although this file is under a local `ceph-client` source mirror, the content in this chunk is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish symbolic register addresses for NBIO 4.3.0 blocks so AMDGPU code can use named constants instead of raw MMIO offsets. Each register appears in the generated pattern:

- `reg<NAME>`, the register offset value used by SOC15/NBIO register access helpers.
- `reg<NAME>_BASE_IDX`, the AMDGPU register-base index used to select the correct register aperture for that offset.

Most early NBIF/BIF/RCC registers in this chunk use base index `5`, while the GDC SION and S2A doorbell registers use base index `3`. Runtime code combines these offsets with field definitions from the matching shift/mask header and with generated default-value data where available.

## Important Macro Families

The opening `PCIEMSIX` fragment completes the MSI-X table area that began in an earlier chunk. It defines vector-table entries 173 through 255. Each vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` registers, followed by `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` for the MSI-X pending-bit array at base address `0x10171000`. These symbols are relevant to interrupt-vector programming, vector masking, and pending-bit observation.

The `nbio_nbif0_rcc_shadow_reg_shadowdec` block at base address `0x10130000` defines shadow PCI configuration registers such as `SHADOW_COMMAND`, `SHADOW_BASE_ADDR_1`, `SHADOW_BASE_ADDR_2`, bus-number/latency fields, memory and I/O base/limit registers, and interrupt/pin/cacheline-style shadow fields. These offsets describe the NBIO/RCC shadow image used when hardware or firmware exposes, mirrors, or restores PCI configuration state.

The `nbio_nbif0_bif_swus_SUMDEC` block defines the small SWUS/SUM indirect register window: `SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI`. This is an indirect access surface, so the address constants are only the visible index/data registers; actual target state is selected through values written by consuming code.

The large `nbio_nbif0_rcc_strap_rcc_strap_internal` block at base address `0x10100000` defines many `RCC_STRAP1_*` registers for device, port, and endpoint-function strap state. The visible families include `RCC_DEV0_PORT_STRAP*`, `RCC_DEV0_EPF0_STRAP*`, `RCC_DEV0_EPF1_STRAP*`, and additional `DEV1`/`DEV2` endpoint-function strap registers. These are boot/configuration strap offsets that influence PCIe/NBIO identity, capability, link, function, and virtualization-related hardware behavior.

The `nbio_nbif0_bif_rst_bif_rst_regblk` block defines reset and power-state offsets: hard reset, self soft reset, BIF/GFX/VPU reset controls, reset miscellaneous controls, PF FLR reset controls for device 0 PF0-PF3, reset/power/D3hot interrupt status and mask registers, PF FLR reset request state, per-PF D-state values, D3hot-to-D0 reset controls, and port D-state state. These constants are consumed by reset, FLR, suspend/resume, and power-management paths.

The `nbio_nbif0_bif_misc_bif_misc_regblk` block defines miscellaneous BIF/NBIF control and observation offsets. It includes ROM-offset and BIOS strap control, scratch registers, interrupt line polarity/enable, outstanding VC allocation, `BIFC_MISC_CTRL*`, BME error logs, link-control timers, DMA attribute override registers, SMN master endpoint controls, disconnect hysteresis controls, SHUB sync-flood controls, and BIFC performance counter/latency/debug registers. The adjacent `bif_misc_pfvf` block is present as an address-block marker but has no register macros in this slice.

The `nbio_nbif0_bif_ras_bif_ras_regblk` block defines BIF RAS central control/status, leaf control/status registers, IOHUB RAS interrupt handling, and view-from-IOHUB offsets. These are reliability, availability, and serviceability diagnostic/control registers rather than general data-path registers.

The RCC `BIFDEC1` blocks at base address `0x10120000` define downstream, downstream-port, endpoint, and core RCC PCIe controls. The visible names cover endpoint/downstream scratch/control/config registers, RX/link-speed/link-control registers, LTR message/control offsets, DPA capability/control/substate allocation aliases, PME control, requester ID restore, VDM support, margining parameters, GPU IOV and host-VM enablement, console IOV mode/first-VF/stride fields, peer register ranges, bus/config control, and reset-enablement controls. Several DPA-related symbols intentionally share the same offset because different fields or conceptual registers are packed into the same hardware dword.

The `nbio_nbif0_bif_bx_SYSDEC` block defines the BIF BX1 system register aperture. It starts with PCIE indirect index/data pairs, then defines SBIOS/BIOS/driver/firmware scratch registers, interrupt controls for RLC/VCE/UVD, GFX MMIO register CAM address/remap/control registers, mailbox and scratch-style state, BIF control/status/debug registers, pad controls, save/restore controls, and S5 memory-power controls. These offsets are integration points between firmware, driver, PCIe fabric control, and graphics IP blocks behind NBIO.

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` blocks define PF1-scoped BIF/BX offsets. They include PF MM index/data windows, BME status and atomic error log state, doorbell self-ring GPA aperture high/low/control registers, HDP coherency flush/invalidate controls, GPU HDP flush request/done registers, transaction-pending observation, NBIF/GFX address LUT bypass, and mailbox transmit/receive/control/interrupt registers including `BIF_VMHV_MAILBOX`.

The `nbio_nbif0_rcc_strap_BIFDEC1:1` block defines `RCC_STRAP2_*` BIF/port/EPF strap offsets at the `0x10120000` base, complementing the earlier `RCC_STRAP1_*` internal strap block. It includes BIF strap registers, device 0 port straps, and endpoint-function strap registers for EPF0 and EPF1.

The `nbio_nbif0_gdc_dma_sion_SIONDEC` and `nbio_nbif0_gdc_hst_sion_SIONDEC` blocks define GDC DMA-side and host-side SION quality-of-service/credit programming registers. They repeat per-client-lane (`CL0` through `CL3` for DMA, `CL0` through `CL2` for host in this slice) patterns for read-response, write-response, and request burst targets, time slots, request/data/read-response/write-response pool credit allocation, plus control registers. These constants are likely used when programming NBIO/GDC arbitration, traffic shaping, or fabric credit behavior.

The closing `S2A_DOORBELL` registers define doorbell entry control offsets `S2A_DOORBELL_ENTRY_0_CTRL` through `S2A_DOORBELL_ENTRY_15_CTRL` and `S2A_DOORBELL_COMMON_CTRL_REG`. The next `nbio_nbif0_gdc_GDCDEC` address-block marker appears at the final assigned line, but its register definitions are outside this work item.

## Control Flow

There is no local control flow in this chunk. Runtime behavior appears only in code that includes the generated constants:

1. Driver code selects a `reg...` macro for an NBIO/BIF/RCC/GDC register.
2. It combines the offset with the paired `_BASE_IDX` value through AMDGPU register-address helpers, commonly via `SOC15_REG_OFFSET`-style address construction or generated register accessor macros.
3. It reads, writes, polls, or read-modify-writes the hardware register through AMDGPU MMIO/PCIE access helpers.
4. It applies bit positions and masks from the companion `nbio_4_3_0_sh_mask.h` header when manipulating individual fields.

Typical higher-level flows using these offsets include MSI-X programming, PF/VF reset and FLR handling, PCIe link/power policy, strap interpretation, indirect-register access, RAS status handling, mailbox communication, doorbell aperture configuration, HDP coherency flushes, virtualization/IOV setup, and GDC SION arbitration tuning.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed state in NBIO, BIF, RCC, PCIe, and GDC register blocks. The represented state includes MSI-X vector address/data/control registers, pending interrupt bits, shadow PCI configuration state, strap-derived configuration, reset controls and reset interrupt state, D-state and power-transition state, RAS control/status, PCIe endpoint/downstream/link-control state, scratch and firmware/driver communication registers, mailbox buffers, doorbell controls, HDP flush state, and SION credit/time-slot/traffic-shaping registers.

Some represented registers are static or strap-derived, some are firmware-owned scratch/configuration values, some are driver-programmed controls, some are hardware-updated status, and some may be sticky, write-one-to-clear, or side-effectful. The offset header does not encode access width, reset defaults, required sequencing, locking, ownership boundaries, timeout requirements, or field-level side effects.

## Dependencies And Integration Points

The immediate dependency is the generated NBIO 4.3.0 register database. This header must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h`, which supplies bit shifts and masks for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_default.h`, where generated reset/default values exist for corresponding registers.
- AMDGPU SOC15/NBIO register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Important integration surfaces are AMDGPU NBIO 4.3 support code, PCIe/BIF initialization, MSI-X interrupt setup, SR-IOV and PF/VF virtualization code, reset/FLR and D-state transitions, runtime power management, RAS diagnostics, mailbox paths used by virtualization or firmware coordination, doorbell routing, HDP coherency operations, and GDC/NBIO fabric scheduling. Firmware and platform PCIe policy also intersect with the shadow, strap, scratch, link, LTR, DPA, PME, and BIOS/SBIOS scratch registers.

## Risks And Edge Cases

- The chunk boundaries are artificial. The MSI-X table begins before line 12431, and the `GDCDEC` block begins at the last assigned line but has no register content inside this chunk.
- These are untyped preprocessor constants. A stale or misgenerated offset compiles cleanly but can redirect MMIO to the wrong hardware register.
- The paired `_BASE_IDX` values are as important as the offsets. Using a base index `5` NBIF/BIF/RCC offset through the base index `3` GDC aperture, or the inverse, can access unrelated hardware state.
- Repeated generated families are easy to misuse. MSI-X vector numbers, PF numbers, EPF strap suffixes, client-lane suffixes, and `REG0`/`REG1` SION pairs must be kept aligned with the intended hardware instance.
- Some macros deliberately alias the same offset under different conceptual names, especially DPA substate and control registers. Consumers must use field masks and documented ownership rules rather than assuming one macro name equals one independent dword.
- Reset, FLR, D3hot/D0, power, and link-control registers are sequencing-sensitive. Incorrect writes can wedge PCIe links, interrupt reset flows, or leave functions in inconsistent power states.
- MSI-X vector control and PBA registers affect interrupt delivery. Incorrect vector or PBA handling can lose interrupts, leave vectors masked, or report stale pending state.
- Strap registers may be read-only, latched, firmware-controlled, or only valid at specific phases. Treating strap offsets as normal mutable control registers can produce ineffective writes or undefined behavior.
- RAS status/control registers may be sticky or write-one-to-clear. Generic read/modify/write treatment can clear diagnostic evidence or mask future errors.
- Doorbell, mailbox, HDP flush, and transaction-pending registers cross ownership boundaries between CPU, GPU, firmware, PF, VF, and possibly guests. Missing serialization or timeout handling in consumers can cause lost notifications or hung waits.
- SION credit and time-slot registers influence fabric scheduling. Misprogramming can cause performance regressions, starvation, backpressure, or unstable DMA/host traffic behavior.

## Test Signals

Useful validation is mostly build-time plus hardware integration:

- Build AMDGPU with NBIO 4.3.0 support enabled; missing or renamed macros should surface in NBIO/BIF/GDC/PCIe include paths.
- Compare this offset chunk with `nbio_4_3_0_sh_mask.h` and `nbio_4_3_0_default.h` to confirm register names and generated families remain synchronized.
- On matching hardware, verify MSI-X allocation and interrupt delivery across high vector numbers, including vector masking/unmasking and pending-bit-array behavior.
- Exercise PF FLR, D3hot-to-D0, suspend/resume, runtime power transitions, and PCIe link retraining while checking reset interrupt status/mask handling.
- Validate SR-IOV or virtualization paths that rely on PF1 mailbox registers, VM/HV mailbox state, GPU IOV region controls, first-VF/stride registers, and doorbell aperture programming.
- Run RAS or error-injection diagnostics where available and confirm BIF RAS central/leaf status and IOHUB notification registers map to expected events without clearing evidence prematurely.
- Exercise HDP coherency flush/invalidate paths and confirm `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, and transaction-pending status complete within expected timeouts.
- Run DMA, graphics, compute, and host traffic workloads while changing or validating SION credit/time-slot programming; regressions in throughput, latency, or hangs are signals of GDC SION offset or field drift.
- Validate firmware/BIOS scratch and strap interpretation during boot and resume, especially where SBIOS, firmware, and driver scratch registers are used as handoff state.

## Chunk Notes

- Lines 12431-13113 finish the `PCIEMSIX` vector table from vector 173 through vector 255 and define `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7`.
- Lines 13116-13587 cover RCC shadow, SWUS/SUM, and the large internal `RCC_STRAP1_*` device/port/EPF strap block.
- Lines 13590-13871 cover BIF reset, BIF miscellaneous, an empty PFVF miscellaneous marker, and BIF RAS offsets.
- Lines 13874-14571 cover RCC `BIFDEC1`, BIF BX system/PF/PFVF, and `RCC_STRAP2_*` blocks at base address `0x10120000`.
- Lines 14574-14901 cover GDC DMA SION, GDC host SION, and S2A doorbell control offsets at the `0x1400000` base using base index `3`.
- Line 14904 is only the `nbio_nbif0_gdc_GDCDEC` address-block marker; later chunks must cover that block's actual register offsets.
