# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 20124-22598

## Scope

This chunk is a generated AMD NBIF 6.3.1 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, dynamic state, allocation, locking, or executable control flow.

The range starts at the tail of `BIF_PASID_ERR_LOG`, covers `BIF_PASID_ERR_CLR`, then spans NBIF virtual-wire, LCLK clock/deepsleep, SMN master, SDP, timeout-detection, BIFC credit/performance, RAS, RCC/PCIe endpoint and root-complex, BIF BX system, BIFDEC, and PF/PF-VF register-field families. It ends inside `BIF_BX_PF1_GPU_HDP_FLUSH_REQ`, after the `CP7` shift definition; the remaining shift and mask definitions for that register are in the next chunk.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIF 6.3.1 registers. Each field generally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for isolating or preserving the field.

The matching register-address metadata lives in `nbif_6_3_1_offset.h`, which provides symbols such as `regBIF_PASID_ERR_CLR`, `regNBIF_MGCG_CTRL_LCLK`, `regBIF_BX1_BIF_RB_CNTL`, and `regBIF_BX_PF1_GPU_HDP_FLUSH_REQ`. AMDGPU NBIO/BIF code combines the offset and mask headers with helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The early NBIF control block includes PASID error clear bits for device 0 functions 0-6, virtual-wire controls for SMN and SDP paths, per-set virtual-wire change disable/reset/trigger fields, medium-grain clock gating, LCLK deep sleep, SMN master arbitration and posted/zero-byte behavior, SDP virtual-wire triggers, SHUB timeout-detection controls/status, BIFC SDP/GMI/SST pool-credit allocation, early wakeup, and simple performance counter selectors/count values.

`NBIF_MGCG_CTRL_LCLK` is a notable integration point. It defines `NBIF_MGCG_EN_LCLK`, mode, hysteresis, host/DMA/register/AER/debug disable bits, and SRAM fine-grain clock-gating enable. Existing NBIO code reads this register, toggles `NBIF_MGCG_EN_LCLK` according to `AMD_CG_SUPPORT_BIF_MGCG`, and writes it back through PCIe register helpers.

The `BIFL_RAS_*` block covers centralized NBIF RAS handling and four repeated leaf blocks. Central control/status fields gate error-event, interrupt, egress-stall, and link-disable propagation. Each leaf exposes parity, poison, receiver-error-event, timeout logging, MCA logging, propagation, generated egress-stall, and UCP enable/status bits. `BIFL_IOHUB_RAS_IH_CNTL` and `BIFL_RAS_VWR_FROM_IOHUB` bridge these RAS events into the IOHUB interrupt/virtual-wire path.

The RCC and PCIe families cover downstream, downstream-port, endpoint, and common root-complex controls. They define fields for hidden config decoding by PCIe generation, unsupported-request reporting, AER timer/status clear behavior, completion timeout and FLR handling, link speed straps through Gen5, link bandwidth/state notification suppression, endpoint interrupt enables/status, LTR messaging, dynamic power allocation substate power values, requester ID restore, bus and device/function number capture/listing, peer framebuffer offsets, XDMA aperture bounds, VDM support, link-down entry/exit, PME blocking, and max payload/read-request sizing.

The `nbif_bif_bx_SYSDEC` block exposes indirect PCIe index/data windows, BIOS/SBIOS/driver/firmware scratch registers, GFX MMIO register CAM remap entries, and scratch/status locations. Many of these are full-width fields, meaning the macros primarily name persistent scratch or address payload registers rather than subfields.

The `nbif_bif_bx_BIFDEC1` block covers BIF strap/status/control surfaces: bus control, reset enable/control, interrupt control, CLKREQ pad fields, feature control, HDP atomic behavior, doorbell control and interrupt control, framebuffer enable, master/slave pending status, BACO entry/exit timers, memory type, SR-IOV virtual-function enable/status bitmaps, HDP flush remap addresses, a BIF ring buffer, mailbox index, MP1 interrupt control, PCIe pad controls, save/restore scratch state, S5 memory power controls, and dummy registers.

The VF bitmaps are especially repetitive and hardware-facing. `BIF_BX1_VF_REGWR_EN`, `BIF_BX1_VF_DOORBELL_EN`, `BIF_BX1_VF_FB_EN`, and matching `*_STATUS` registers provide one-bit-per-VF enable/status fields for virtual functions 0-30 or 0-31 depending on the family. These macros are part of the SR-IOV boundary where PF code controls or observes VF register-write, doorbell, and framebuffer access.

The final PF/PF-VF block begins with BME-low status/clear fields, unsupported atomic operation error logs and clear bits, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate-only controls, and the start of `BIF_BX_PF1_GPU_HDP_FLUSH_REQ`. In this assigned range, only `CP0` through `CP7` shift constants for the flush request register are present; the rest of that register continues after line 22598.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing belongs to the AMDGPU NBIO/BIF code that includes it:

1. Driver code selects a register offset from the companion offset header.
2. It reads or prepares a 32-bit value with SOC15/PCIE MMIO helpers.
3. It uses these `__SHIFT` and `_MASK` constants, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to update or decode individual fields.
4. It writes the value back or polls status/done bits according to the hardware programming sequence.

For example, NBIO clock-gating code reads `smnNBIF_MGCG_CTRL_LCLK`, toggles `NBIF_MGCG_CTRL_LCLK__NBIF_MGCG_EN_LCLK_MASK`, and writes the value only when it changed. Another NBIO path returns `SOC15_REG_OFFSET(NBIO, 0, regBIF_BX_PF1_GPU_HDP_FLUSH_REQ)` so higher-level HDP flush logic can request engine flushes through the BIF/PF flush-request register.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO-backed hardware state whose lifetime is controlled by the GPU, firmware, power management, PCIe link state, reset, suspend/resume, BACO, FLR, and SR-IOV PF/VF policy.

The represented state includes sticky error logs and clear bits, clock-gating and deepsleep configuration, RAS routing/status, PCIe link and error behavior, virtual-wire trigger/disable state, scratch registers shared with BIOS/SBIOS/firmware/driver code, doorbell and framebuffer apertures, virtual-function enable/status maps, HDP flush controls, a BIF ring-buffer base/pointers/writeback address, pad controls, and S5 memory power state. Some fields are durable configuration until reset or reprogramming; others are status, command strobes, write-one-to-clear bits, sticky logs, or hardware-owned counters/pointers. The header names bit positions but does not encode read/write side effects.

## Dependencies And Integration Points

This chunk depends on the generated NBIF 6.3.1 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`. The offset header supplies numeric register addresses and base-index selectors; this shift/mask header supplies field layouts for those addresses.

Direct integration is through AMDGPU NBIO/BIF code under `drivers/gpu/drm/amd/amdgpu`. Nearby versioned NBIO files show the same macro families consumed for LCLK clock gating, interrupt control, indirect PCIe access, and HDP flush offsets. This chunk's `BIF_BX1_*` and `BIF_BX_PF1_*` fields also align with SR-IOV, doorbell, HDP coherency, BACO/power, PCIe error handling, and RAS paths.

The macros are untyped constants, so their correctness is enforced mostly by generated-header consistency and by hardware behavior. A renamed macro will usually fail at compile time, but a wrong mask value can compile cleanly and program the wrong bit.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first line is already inside `BIF_PASID_ERR_LOG`, and the final line stops before `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` masks and later engine bits. File-level reconciliation must join adjacent chunks before making whole-register claims.
- Side-effect fields are not distinguishable from plain configuration fields by type. Clear bits such as PASID, atomic, BME, AER, and status-clear fields must be used according to hardware write-one-to-clear or command semantics, not treated as ordinary persistent bits.
- Clock-gating and deep-sleep masks can affect register accessibility, DMA paths, AER/debug logic, and low-power behavior. Incorrect `NBIF_MGCG_CTRL_LCLK` or `NBIF_DS_CTRL_LCLK` programming can cause hangs, missed wakeups, or power regressions.
- RAS masks affect error propagation, MCA logging, interrupts, and egress stalls. Incorrect settings can hide poison/parity/timeout errors, create interrupt storms, or stall links unexpectedly.
- PCIe/RCC fields are interoperability-sensitive. Changing FLR, LTR, AER, max payload, requester ID, link speed, hidden config decode, or completion timeout behavior can break specific root complexes, virtualization flows, or suspend/resume cases.
- SR-IOV VF enable/status bitmaps are dense and repetitive. Off-by-one shifts in VF register-write, doorbell, or framebuffer access maps can grant or deny the wrong VF.
- HDP flush request/done and coherency flush controls are ordering-sensitive. Wrong masks or offsets can leave CPU-visible GPU memory stale or cause hangs in code waiting for a flush acknowledgment.
- Full-width scratch and address fields are not self-validating. Using the wrong offset with a full-width mask can silently overwrite firmware/BIOS/driver coordination state.

## Test Signals

Useful validation is mostly integration and hardware oriented:

- Build AMDGPU with NBIF/NBIO support for ASICs using the NBIF 6.3.1 headers; missing or renamed macros should fail in versioned NBIO/BIF code.
- Exercise clock-gating enable/disable paths and confirm `NBIF_MGCG_CTRL_LCLK` changes do not produce register-access failures, hangs, or power-management regressions.
- Run PCIe and suspend/resume tests that cover FLR, link-state changes, LTR, AER/error reporting, BACO, and S5-related state.
- In SR-IOV configurations, validate PF-controlled VF register-write, doorbell, and framebuffer enable/status behavior for every VF represented by the bitmaps.
- Use RAS/error-injection or diagnostic paths, where available, to confirm leaf and central RAS status, logging, interrupt, and clear behavior.
- Exercise HDP flush paths through command processor and SDMA workloads; stale CPU-visible memory, timeout waiting for flush done, or incorrect flush request offsets are strong signals of mask/offset drift.
