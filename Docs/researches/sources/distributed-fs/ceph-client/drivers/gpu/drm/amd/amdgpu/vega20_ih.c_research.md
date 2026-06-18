# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.c

## Purpose

`vega20_ih.c` implements the AMDGPU interrupt handler (IH) IP block for Vega20-generation OSSSYS IH hardware. It initializes interrupt ring buffers, programs their register offsets and doorbells, enables and disables interrupt delivery, reads and advances write/read pointers, handles overflow recovery, dispatches secondary IH ring work, and exposes the block through `amd_ip_funcs` and `amdgpu_ih_funcs`.

The implementation supports primary ring `adev->irq.ih`, secondary rings `ih1` and `ih2`, and software ring `ih_soft`. It also has SR-IOV paths where IH control register programming may be delegated to PSP firmware instead of direct MMIO writes.

## Important APIs, Types, And Functions

Exported objects:

- `const struct amd_ip_funcs vega20_ih_ip_funcs`: AMDGPU IP lifecycle entry points for early init, software init/fini, hardware init/fini, suspend/resume, reset, idle, clock gating, and power gating.
- `const struct amdgpu_ip_block_version vega20_ih_ip_block`: IP block descriptor with type `AMD_IP_BLOCK_TYPE_IH`, version 4.2.0, and `vega20_ih_ip_funcs`.

Internal function groups:

- Register layout: `vega20_ih_init_register_offset()` fills `struct amdgpu_ih_regs` for ring0, ring1, and ring2 based on `OSSSYS` SOC15 register offsets and PSP register IDs.
- Ring enable/disable: `vega20_ih_toggle_ring_interrupts()` toggles `IH_RB_CNTL.RB_ENABLE`, GPU timestamp enable, overflow clear, and ring0 `ENABLE_INTR`; `vega20_ih_toggle_interrupts()` applies that to every allocated hardware ring.
- Ring programming: `vega20_ih_rb_cntl()` constructs core `IH_RB_CNTL` fields; `vega20_ih_doorbell_rptr()` and `vega20_setup_retry_doorbell()` construct doorbell control values; `vega20_ih_enable_ring()` writes base address, control, writeback address, pointers, and doorbell rptr.
- Hardware lifecycle: `vega20_ih_irq_init()` disables interrupts, configures NBIO IH control, programs ASIC-specific `IH_CHICKEN` behavior, enables rings, configures doorbell range and retry CAM, and re-enables interrupts. `vega20_ih_irq_disable()` disables all rings and waits briefly.
- Pointer operations: `vega20_ih_get_wptr()` reads write pointers from writeback memory or registers, detects and clears overflow, and adjusts the read pointer after overflow. `vega20_ih_set_rptr()` writes the read pointer through doorbells or MMIO. `vega20_ih_irq_rearm()` retries lost SR-IOV doorbell writes.
- Self interrupt dispatch: `vega20_ih_self_irq()` schedules `ih1_work` or `ih2_work` based on `entry->ring_id`; `vega20_ih_set_self_irq_funcs()` wires the IRQ source.
- IP lifecycle: `vega20_ih_early_init()`, `vega20_ih_sw_init()`, `vega20_ih_sw_fini()`, `vega20_ih_hw_init()`, `vega20_ih_hw_fini()`, `vega20_ih_suspend()`, and `vega20_ih_resume()`.
- Power management: `vega20_ih_update_clockgating_state()`, `vega20_ih_set_clockgating_state()`, and no-op `vega20_ih_set_powergating_state()`.

Important external types and helpers include `struct amdgpu_device`, `struct amdgpu_ih_ring`, `struct amdgpu_ih_regs`, `struct amdgpu_irq_src`, `struct amdgpu_iv_entry`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `WREG32_NO_KIQ`, `WDOORBELL32`, `SOC15_REG_OFFSET`, `WREG32_SOC15`, `WREG32_FIELD15`, `amdgpu_ih_ring_init()`, `amdgpu_irq_init()`, and `psp_reg_program()`.

## Control Flow

Driver bring-up starts with `vega20_ih_early_init()`, which installs IH function tables. `vega20_ih_sw_init()` registers the self-IRQ source, decides whether rings use bus addresses, allocates ring0, ring1, conditionally ring2, and the software ring, assigns doorbell indices, initializes per-ring register offsets, and calls generic IRQ software initialization.

Hardware initialization flows through `vega20_ih_hw_init()` to `vega20_ih_irq_init()`:

1. Disable all allocated rings via `vega20_ih_toggle_interrupts(false)`.
2. Let NBIO perform IH control setup through `adev->nbio.funcs->ih_control(adev)`.
3. On bare metal, program `IH_CHICKEN` or Aldebaran-specific `mmIH_CHICKEN_ALDEBARAN` when the ASIC/version and address-space mode require `MC_SPACE_GPA_ENABLE`.
4. For each allocated hardware ring, call `vega20_ih_enable_ring()` and clear the software overflow flag.
5. Program the IH doorbell range on non-SR-IOV configurations.
6. Enable PCI bus mastering.
7. Allocate and program the retry CAM doorbell, then enable retry CAM using normal or Aldebaran-specific registers.
8. Re-enable all hardware rings via `vega20_ih_toggle_interrupts(true)`.
9. Mark `ih_soft` enabled when its ring exists.

Interrupt processing uses the generic AMDGPU IRQ flow through `adev->irq.ih_funcs`. `get_wptr` obtains the producer pointer. Ring0 normally uses memory writeback; secondary rings fall back to register reads. If overflow is detected, the handler warns, advances `ih->rptr` to `(wptr + 32) & ptr_mask`, clears hardware overflow, and returns the masked pointer. After consumers parse IV entries, `set_rptr` publishes the consumer pointer through a doorbell or MMIO register.

Self-IRQ entries from the IH client schedule asynchronous work for ring1 or ring2. Suspend and resume map directly to hardware fini/init.

## State And Persistence Behavior

Persistent state is in `adev->irq` and hardware registers, not on disk. The file mutates:

- Ring allocation fields, `ring_size`, `enabled`, `rptr`, `overflow`, `gpu_addr`, `wptr_addr`, `wptr_cpu`, `rptr_cpu`, `use_bus_addr`, `use_doorbell`, and `doorbell_index`.
- Register offset descriptors under `ih->ih_regs`.
- Device doorbell state including `adev->irq.retry_cam_doorbell_index` and `adev->irq.retry_cam_enabled`.
- Hardware IH registers for ring base, control, read/write pointers, doorbell read pointers, writeback address, retry CAM, `IH_CHICKEN`, and clock-control overrides.

State is re-created during driver load or resume. Ring hardware pointers are reset to zero when rings are disabled or enabled. Overflow handling updates the software read pointer to reduce the chance of parsing overwritten vectors.

## Dependencies

The file includes Linux PCI support and AMDGPU internal headers: `amdgpu.h`, `amdgpu_ih.h`, `soc15.h`, OSSSYS register offset/mask headers, `soc15_common.h`, and `vega20_ih.h`.

Runtime dependencies include:

- SOC15 register offset macros and OSSSYS register field definitions.
- NBIO callbacks for IH control and doorbell range programming.
- PSP register programming for SR-IOV virtual functions.
- AMDGPU interrupt core registration and ring allocation helpers.
- Doorbell index setup from Vega20 register initialization.
- PCI bus mastering.
- ASIC version checks for OSSSYS 4.2.1 and 4.4.x behavior.

## Integration Points

`vega20_ih_ip_block` is added by device discovery for supported ASICs. Generic AMDGPU IRQ code calls `adev->irq.ih_funcs->get_wptr`, `decode_iv`, `decode_iv_ts`, and `set_rptr`. The file relies on `vega20_doorbell_index_init()` from `vega20_reg_init.c` having established `adev->doorbell_index.ih` before `sw_init` assigns IH doorbells.

The IP block also integrates with:

- `amdgpu_irq_add_id()` for the self interrupt source.
- Workqueues `adev->irq.ih1_work` and `adev->irq.ih2_work` for secondary ring draining.
- SR-IOV paths that require PSP-mediated register writes and retry rearming.
- Clock gating control through `AMD_CG_SUPPORT_IH_CG`.

## Risks

- PSP programming failures return `-ETIMEDOUT`; incomplete error recovery can leave interrupts disabled during bring-up or resume.
- Overflow recovery intentionally skips to a guessed readable position. This can drop interrupt vectors, so downstream users must tolerate missed or delayed events after overflow.
- Ring0 has writeback and `ENABLE_INTR` behavior that secondary rings do not. Applying ring0 assumptions to ring1/ring2 would be incorrect.
- SR-IOV doorbell rearm loops are bounded by `MAX_REARM_RETRY`; persistent lost doorbell writes may still leave interrupts unacknowledged.
- ASIC-specific register selection for Aldebaran/OSSSYS 4.4.x is version-sensitive. Missing a new version can program the wrong retry CAM or chicken register.
- `vega20_ih_wait_for_idle()` deliberately returns `-ETIMEDOUT`, which means generic callers should not expect a useful idle wait implementation.
- The APU special case for OSSSYS 4.4.2 disables bus addresses. Regressions in address-space selection can break IH ring memory access.

## Test Signals

Useful test and debug signals:

- Driver load/resume on Vega20 and related OSSSYS 4.4.x ASICs should complete with `vega20_ih_irq_init()` returning zero.
- Interrupt-driven workloads should show advancing IH write/read pointers and no persistent `ring buffer overflow` warnings.
- Suspend/resume tests should confirm interrupts resume and rings are reinitialized.
- SR-IOV VF testing should cover PSP register programming paths and doorbell rearm behavior.
- MSI and non-MSI configurations should verify `RPTR_REARM` behavior on ring0.
- Secondary ring tests should confirm self IRQs schedule `ih1_work` and `ih2_work`.
- Clock gating tests should verify `IH_CLK_CTRL` soft override fields change only when `AMD_CG_SUPPORT_IH_CG` is set.
