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
