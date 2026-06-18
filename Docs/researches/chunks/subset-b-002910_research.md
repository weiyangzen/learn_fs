# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 14791-17171

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, dynamic storage, locks, or executable branches. The range covers 2,164 `#define` entries and starts in the middle of the PCIe lane-margining definitions, at the masks for lane 4 status and the complete lane 5-15 control/status pairs. It ends in the middle of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4`, after the `STRAP_ATOMIC_EN_DEV0_F0` shift but before the rest of that register's shifts and masks.

Major covered register families are:

- PCIe lane-margining control/status fields for `BIF_CFG_DEV0_SWDS_LANE_5_MARGINING_LANE_CNTL` through `LANE_15`, plus the tail of lane 4 status from the previous chunk.
- PF system/VF indirect MMIO aperture fields: `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- `RCC_STRAP0` strap registers for global BIF behavior, device 0 downstream port straps, endpoint function 0 straps, and endpoint function 1 straps.
- Runtime RCC endpoint/downstream PCIe controls for device 0: endpoint interrupt/status, DPA, PME, TX/RX controls, link-speed controls, downstream-port controls, VDM support, PCIe margining parameter controls, bus controls, feature-misc controls, link controls, requester-ID restore, LTR switch latency, and multi-host arbitration.
- BIF PF/VF registers for BME-low status, unsupported atomic error logging, self-ring doorbell GPA aperture, HDP coherency flush, GPU HDP flush request/done bits, transaction-pending status, mailbox message buffers, mailbox interrupts, and VM/hypervisor mailbox fields.
- Shadow configuration-space bridge fields: shadow command, BARs, bus numbers, I/O/memory/prefetchable apertures, interrupt/bridge control, and SUC index/data indirect access.
- `RCC_STRAP1` internal strap mirrors for device 0-2 downstream port straps, BIF straps, and the start of device 0 endpoint function 0 straps.

Although this path sits under `sources/distributed-fs/ceph-client`, the file is AMD GPU NBIO PCIe/MMIO metadata, not Ceph or distributed-filesystem logic.

## Purpose

The purpose of this slice is to publish the bit-level ABI for NBIO 2.3 registers. Each register field follows the generated AMD naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for placing or extracting a field value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or clearing that field in a 32-bit register.

The paired `nbio_2_3_offset.h` header supplies the MMIO register offsets such as `mmRCC_BIF_STRAP2`, `mmRCC_DEV0_EPF0_STRAP0`, `mmBIF_BX_PF_GPU_HDP_FLUSH_REQ`, `mmBIF_BX_PF_GPU_HDP_FLUSH_DONE`, `mmMAILBOX_MSGBUF_TRN_DW0`, and `mmMAILBOX_INT_CNTL`. This shift/mask header supplies the field definitions consumed by `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_FIELD_MASK`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_PCIE`, `RREG32_PCIE`, `WREG32_NO_KIQ`, and related AMDGPU register helpers.

Operationally, the slice defines the NBIO register contract for PCIe capability straps, ASPM/LTR timing, SR-IOV capability advertisement, doorbell aperture routing, HDP cache flush signaling, host/VF mailbox transport, shadow PCI bridge state, PCIe lane margining, and low-level error/status handling.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the generated macro namespace.

Important macro groups include:

- `BIF_CFG_DEV0_SWDS_LANE_*_MARGINING_LANE_CNTL` and `*_STATUS`: per-lane receiver number, margin type, usage model, and payload fields for PCIe lane margining. This chunk completes lanes 5-15 and carries the tail of lane 4 status.
- `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`: indirect MMIO index/data fields, including low/high offset and aperture select. These are the field-level contract for accessing an indexed register aperture rather than a direct MMIO register.
- `RCC_STRAP0_RCC_BIF_STRAP0` through `RCC_STRAP0_RCC_BIF_STRAP6`: BIF strap state for link generation disable/kill bits, clock power management, VGA/ROM/memory aperture settings, PX capability, error-ignore policy, fuse/ROM strap validity, software write disable, margining readiness, SWUS aperture sizing and prefetchability, hardware/software revision bits, link-reset behavior, DLF/16GT/margin enablement, LTR in ASPM L1 disable, ASPM/LDN timers, power-brake deglitch/status fields, and reserved strap bits.
- `RCC_STRAP0_RCC_DEV0_PORT_STRAP0` through `PORT_STRAP9`: downstream-port straps for ARI/ACS/AER, completion-abort error handling, device ID, interrupt pin, max payload/link width, dummy endpoint-function enable, port type, reset slot clock, slot power limit/scale/value, ECRC, link bandwidth notification, ASPM support, L0s/L1 latency, MSI/PME/PME-clock behavior, DPA, LTR, OBFF, power indicator/control, attention indicator/button, hotplug, surprise down, MRL sensor, electromechanical interlock, no-command-complete support, component latency, and power budget data.
- `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` through `EPF0_STRAP13`: endpoint function 0 identity and capability straps: device/revision IDs, function enable, D-states, SR-IOV VF device ID and page-size support, SR-IOV enable/total VFs, 64-bit BAR/Resizable BAR, PASID/ATS/ACS/AER/ARI, DPA, DSN, VC, MSI/MSI-X capability, page request, PASID privilege/execute/global invalidate support, subsystem/vendor IDs, power enable, function-level reset, PME support, interrupt pin, auxiliary power support, doorbell/memory/register/ROM aperture sizes, VF aperture sizes, VGA disable, VF MSI multi-capability, SR-IOV VF mapping mode, VM disable, and VF BAR0/2 size fields.
- `RCC_STRAP0_RCC_DEV0_EPF1_STRAP*`: endpoint function 1 straps for a second function, including identity, MSIX table/PBA BIR, ATI capability pointer, SR-IOV window, VC, AER, MSI/MSI-X, PME, FLR, memory aperture, subsystem/vendor IDs, and several reserved fields.
- `RCC_EP_DEV0_0_EP_PCIE_*`: endpoint runtime controls and status for Unsupported Request reporting, malformed atomic ops, interrupt enables/status, bus master/memory enable, non-fatal/fatal/correctable/system-error signaling, LTR message values and requirements, DPA capability/substate power allocation, PME, TX completion/NPH/NPD tuning, requester ID, PCIe error controls, RX ignore policy, and endpoint link-speed strap bits.
- `RCC_DWN_DEV0_0_*` and `RCC_DWNP_DEV0_0_*`: downstream and downstream-port PCIe controls for register access enables, config-RD CRS return, RX ignore behavior, bus master/memory enable, config-control, strap status, link-speed strap bits, link-bandwidth notification disable, multifunction strap, and LTR message information received from the endpoint.
- `RCC_DEV0_0_RCC_MARGIN_PARAM_CNTL0/1`: lane-margining capability description, including voltage/timing support, independent direction/sampler flags, sample-reporting method, number and max offset of timing/voltage steps, sampling rates, max lanes, and sample count.
- `RCC_DEV0_0_RCC_BUS_CNTL`, `RCC_FEATURES_CONTROL_MISC`, `RCC_DEV0_LINK_CNTL`, `RCC_CMN_LINK_CNTL`, `RCC_EP_REQUESTERID_RESTORE`, `RCC_LTR_LSWITCH_CNTL`, and `RCC_MH_ARB_CNTL`: root-complex bus policy, poison/UR/ECRC/MSI behavior, link down entry/exit, L1/L0s/LDN PME blocking, DMA idle checks, requester-ID restore, LTR latency, and arbitration mode/priority fields.
- `BIF_BME_STATUS` and `BIF_ATOMIC_ERR_LOG`: bus-master-enable low-status and unsupported atomic error status/clear bits.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH/LOW` and `DOORBELL_SELFRING_GPA_APER_CNTL`: self-ring doorbell GPA aperture base, enable, mode, and size fields.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, and `GPU_HDP_FLUSH_DONE`: register/memory HDP flush controls and per-engine request/done bits for CP0-CP9 and SDMA0-1.
- `MAILBOX_MSGBUF_TRN_DW0` through `TRN_DW3`, `MAILBOX_MSGBUF_RCV_DW0` through `RCV_DW3`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`: SR-IOV host/VF mailbox payload words, valid/ack handshake bits, interrupt enables, and compact VM/hypervisor mailbox fields.
- `SHADOW_*`, `SUC_INDEX`, and `SUC_DATA`: shadowed PCI bridge command/address/window/IRQ fields and indirect SUC access fields.
- `RCC_STRAP1_*`: an internal strap block that mirrors many `RCC_STRAP0` downstream-port and BIF strap layouts for device 0 and extends to device 1 and device 2 port straps. The chunk ends before `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` is complete.

## Control Flow

The header has no runtime control flow. Runtime sequencing is supplied by the AMDGPU consumers that include it:

1. `nbio_v2_3_get_rev_id()` reads `mmRCC_DEV0_EPF0_STRAP0`, masks with `RCC_DEV0_EPF0_STRAP0__STRAP_ATI_REV_ID_DEV0_F0_MASK`, shifts by `RCC_DEV0_EPF0_STRAP0__STRAP_ATI_REV_ID_DEV0_F0__SHIFT`, and returns a revision ID. It avoids the read for SR-IOV VFs because guest reads can return `0xffffffff`.
2. `nbio_v2_3_enable_doorbell_selfring_aperture()` writes self-ring doorbell aperture base registers and composes `BIF_BX_PF_DOORBELL_SELFRING_GPA_APER_CNTL` fields for enable, mode, and size.
3. `nbio_v2_3_get_hdp_flush_req_offset()` and `nbio_v2_3_get_hdp_flush_done_offset()` expose HDP flush request/done register offsets. The `nbio_v2_3_hdp_flush_reg` table maps engine names to `GPU_HDP_FLUSH_DONE` masks for CP0-CP9 and SDMA0-1 so shared HDP flush code can request and poll per-engine coherency flushes.
4. `nbio_v2_3_program_ltr()` clears `RCC_BIF_STRAP2__STRAP_LTR_IN_ASPML1_DIS_MASK`, writes endpoint TX LTR controls, and enables LTR in the PCIe device control path when the platform advertises LTR support.
5. `nbio_v2_3_program_aspm()` programs ASPM-related fields and timers, including `RCC_BIF_STRAP3__STRAP_VLINK_ASPM_IDLE_TIMER_MASK`, `RCC_BIF_STRAP3__STRAP_VLINK_PM_L1_ENTRY_TIMER_MASK`, and `RCC_BIF_STRAP5__STRAP_VLINK_LDN_ENTRY_TIMER_MASK`.
6. `mxgpu_nv.c` uses the mailbox payload registers and valid/ack control bytes to implement VF-to-PF requests, polling, acknowledgement, interrupt enablement, FLR notification handling, RAS bad-page notification, and GPU access handshakes.
7. SMU power-management files include this header alongside the offset header so NBIO/PCIe fields are available to SMU11 platform code, even though many fields in this exact chunk are not directly referenced in the portions inspected.

Many strap, PCIe error-control, lane-margining, shadow, and diagnostic fields are not actively manipulated by `nbio_v2_3.c` in the inspected tree. They remain part of the generated hardware ABI for firmware, platform initialization, validation tools, debug paths, or future driver code.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes MMIO-backed hardware state in the NBIO/PCIe fabric.

The represented hardware state includes:

- Boot/fuse/ROM strap-derived state: device/function identity, capability advertisement, link generation availability, aperture sizes, SR-IOV topology, D-state support, FLR/PME/MSI/MSI-X, PASID/ATS/ACS/AER/ARI, Resizable BAR, DPA, LTR, OBFF, power budget, slot, hotplug, and endpoint/downstream port behavior.
- Runtime link and power-management state: ASPM timers, L0s/L1/LDN behavior, LTR behavior, link-down entry/exit state, clock/power management enables, and link bandwidth notification controls.
- Error and status state: UR/malformed atomic reporting, ECRC and poisoned completion behavior, BME-low status, unsupported atomic error logs with clear bits, endpoint/downstream interrupt status, transaction-pending bits, and root-complex error logging policy.
- Doorbell and coherency state: self-ring doorbell GPA aperture base/mode/size, HDP register/memory flush controls, and per-engine HDP flush request/done status.
- Virtualization state: SR-IOV capability straps, VF aperture sizing/mapping, mailbox payload and handshake state, VM/hypervisor mailbox fields, and VF/host reset or RAS notification transport state.
- Shadow PCI configuration state: bridge command bits, BAR shadows, subordinate bus numbers, I/O and memory window shadows, prefetchable-memory upper/lower bounds, IRQ/bridge controls, and indirect SUC register access.
- PCIe lane-margining state: per-lane control and status fields for selected receiver, margin type, usage model, payload, and returned status.

Persistence is hardware-defined. Strap values are usually latched from fuses, ROM straps, pins, or firmware-controlled strap sources and can be read-only, write-protected, or only writable before `WRITE_DISABLE`. Runtime control and status registers persist until reset, power-gating loss, suspend/resume reprogramming, FLR, or explicit driver/firmware writes. Handshake, clear, request/done, interrupt, and error-log fields may be transient, write-one-to-clear, or self-clearing depending on the register.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` supplies matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h` supplies generated default values for the same hardware generation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes and consumes this header for revision ID extraction, doorbell self-ring aperture programming, HDP flush register/mask exposure, ASPM/LTR strap programming, and broader NBIO setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header and uses the mailbox offsets and handshake fields for SR-IOV guest/host messaging on Navi-class GPUs.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c` include the NBIO 2.3 offset and shift/mask headers as part of SMU11 power-management platform integration.
- Common AMDGPU register helpers in `amdgpu.h`, `soc15_common.h`, and related SOC15 infrastructure interpret these macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_FIELD_MASK`, `SOC15_REG_OFFSET`, and raw MMIO/PCIE read-write helpers.

Key integration surfaces are:

- PCIe power management and ASPM: `RCC_BIF_STRAP2`, `RCC_BIF_STRAP3`, and `RCC_BIF_STRAP5` fields interact with `nbio_v2_3_program_aspm()` and `nbio_v2_3_program_ltr()`. Wrong masks here can alter LTR behavior, ASPM entry timing, or low-power state transitions.
- HDP coherency: `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` fields are wired into the NBIO HDP flush table. Incorrect engine masks can make the driver poll the wrong done bit or miss a flush completion.
- SR-IOV mailbox: `MAILBOX_MSGBUF_*`, `MAILBOX_CONTROL`, and `MAILBOX_INT_CNTL` define the register-level protocol used by `mxgpu_nv.c` for GPU access, reset, initialization data, RAS bad-page notifications, CPER/RAS requests, and host FLR notifications.
- Device identity and SR-IOV capabilities: `RCC_DEV0_EPF0_STRAP*` and the mirrored `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*` expose fields that determine PCI config-space identity and capabilities; the driver directly uses the ATI revision field and may rely indirectly on the rest through PCI enumeration and firmware setup.
- Doorbell routing: self-ring GPA aperture fields are written during NBIO setup so GPU queues can use the doorbell aperture correctly.
- Shadow config-space and SUC fields: these define internal register views used by firmware/platform code and by any debug/validation paths that inspect or emulate bridge config windows.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently program another PCIe/NBIO field, causing broken enumeration, wrong capabilities, SR-IOV misconfiguration, invalid doorbell routing, HDP flush hangs, link instability, or broken power management.
- The chunk starts and ends mid-register-family. Lane 4 margining status begins in the previous chunk, and `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` is incomplete at the end. The merge lane must reconcile adjacent chunks before making complete file-level claims about those registers.
- Strap registers are not ordinary mutable configuration. Some fields are latched, firmware-owned, fuse/ROM-derived, write-protected, or only valid in privileged PF contexts. Treating every mask as safe to write risks violating platform or SR-IOV ownership.
- SR-IOV behavior is privilege-sensitive. `nbio_v2_3_get_rev_id()` already avoids an endpoint strap read for VFs because it can return `0xffffffff`; similar PF-owned strap, aperture, mailbox, or shadow registers may be inaccessible or virtualized for guests.
- Mailbox valid/ack bits are sequencing-sensitive. `mxgpu_nv.c` clears transmit-valid before sending so stale host ACK state does not make a new request appear acknowledged. Incorrect masks or byte offsets can cause deadlocks, lost messages, or reset/RAS event handling failures.
- HDP flush bits are command/status synchronization points. Polling the wrong done bit or ignoring firmware-reserved bits can leave stale CPU/GPU-visible data after command submission, SDMA, or memory-management activity.
- ASPM/LTR fields interact with platform policy. Timer or disable-bit mistakes can cause link power-state hangs, poor idle power, PCIe timeouts, or regressions that appear only on removable devices, Thunderbolt paths, or systems with different LTR support.
- Error-control and clear fields can change observability. Misprogramming UR/ECRC/poison/malformed-atomic/clear bits can hide real PCIe errors, create false clears, or alter Linux PCIe AER behavior.
- Repeated strap layouts are easy to confuse. `RCC_STRAP0`, `RCC_STRAP1`, `RCC_DEV1`, and `RCC_DEV2` port strap names have similar field layouts but different address blocks and potentially different ownership.
- Lane-margining controls may be used by validation or PCIe service flows. Bad per-lane receiver, margin type, usage model, or payload fields can produce misleading margin data or disturb active links if used without hardware sequencing.

## Test Signals

Useful validation signals for this chunk are generated-header consistency, build coverage, and NBIO/PCIe runtime behavior:

- Build AMDGPU with Navi/NBIO 2.3 support enabled. Direct consumers in `nbio_v2_3.c`, `mxgpu_nv.c`, and SMU11 platform files should compile against the offset and shift/mask macros.
- Compare this header slice against AMD's authoritative NBIO 2.3 register database and the paired `nbio_2_3_offset.h`; every field name must match the correct register offset and bit range.
- Boot supported Navi hardware and confirm PCIe enumeration exposes expected device/revision IDs, BAR apertures, SR-IOV capabilities, MSI/MSI-X, PASID/ATS/ACS/AER/ARI, FLR, PME, and Resizable BAR behavior.
- Exercise `nbio_v2_3_get_rev_id()` on PF and VF configurations. PF should decode the expected ATI revision from `RCC_DEV0_EPF0_STRAP0`; VF should follow the guarded default path rather than trusting a poisoned strap read.
- Validate doorbell setup by enabling self-ring doorbells and running graphics, compute, SDMA, and VCN queues that rely on doorbell writes.
- Stress HDP flush paths with command submission, SDMA copies, CPU/GPU coherency tests, and suspend/resume. Timeouts or stale data point to request/done mask or remap problems.
- Exercise SR-IOV mailbox workflows: GPU init/fini/reset access, init-data exchange, host FLR notification, bad-page notification, RAS error count/CPER/poison paths, and mailbox ACK/valid interrupts.
- Test ASPM/LTR on systems with and without LTR path support, including removable/Thunderbolt devices if available. Watch for link-state transition failures, PCIe AER noise, idle-power regressions, or resume failures.
- Run PCIe error-injection or validation tests for unsupported atomic operations, BME-low status, ECRC/poison behavior, and AER reporting to ensure status/clear bits behave as expected.
- For hardware validation, exercise lane-margining status/control on lanes 5-15 and compare reported receiver/type/usage/payload status against expected PCIe margining behavior. Keep those tests isolated from normal runtime paths.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `BIF_CFG_DEV0_SWDS_LANE_4_MARGINING_LANE_STATUS` register and lanes before 5. This chunk starts with the last lane 4 status masks and then covers lanes 5-15. The next chunk owns the remainder of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` and later NBIO 2.3 registers. The final per-file research document should merge these boundaries before describing complete lane 4 margining or complete `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` semantics.
