# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c

## Purpose
`ih_v6_0.c` implements the amdgpu Interrupt Handler IP block for IH version 6.0. It allocates and programs interrupt rings, enables/disables hardware interrupt delivery, services write/read pointer synchronization, and wires the block into the generic `amd_ip_funcs` lifecycle.

## Important APIs, Types, And Functions
The exported object is `ih_v6_0_ip_block`. Important internal functions include `ih_v6_0_init_register_offset`, `ih_v6_0_toggle_ring_interrupts`, `ih_v6_0_enable_ring`, `ih_v6_0_irq_init`, `ih_v6_0_irq_disable`, `ih_v6_0_get_wptr`, `ih_v6_0_set_rptr`, `ih_v6_0_self_irq`, and clock/power-gating helpers. It installs `amdgpu_ih_funcs` with `get_wptr`, common IV decoders, and `set_rptr`.

## Control Flow
Early init installs IH and self-IRQ callbacks. Software init registers self interrupt source `SOC21_IH_CLIENTID_IH`, allocates ring0, optionally ring1 on dGPU, then allocates a software IH ring and calls `amdgpu_irq_init`. Hardware init disables rings, lets NBIO configure IH, optionally enables GPA addressing when firmware loading bypasses PSP, programs ring bases/control/doorbells, configures storm/flood handling and ring1 redirection, enables PCI bus mastering, enables interrupts, and enables forced write-pointer updates for self interrupts. Suspend/resume call hardware fini/init.

## State And Persistence
State is kept in `adev->irq.ih`, `adev->irq.ih1`, and `adev->irq.ih_soft`: ring sizes, GPU addresses, CPU writeback/readback pointers, doorbell indices, enabled flags, read pointers, and overflow flags. Register programming persists until reset or hardware fini. Disabling resets hardware rptr/wptr to zero and clears software `enabled`/`rptr`.

## Dependencies And Integration Points
The file depends on `amdgpu.h`, `amdgpu_ih.h`, OSSSYS 6.0 register headers, SOC15 accessors, PSP indirect register programming for SR-IOV VF, NBIO IH hooks, PCI core, delayed work for ring1, and amdgpu IRQ registration. It integrates with PSP firmware loading mode and with MSI doorbell behavior.

## Risks
Interrupt loss or storms can occur if doorbell indices, writeback addresses, or storm registers are wrong. Overflow recovery skips to `wptr + 32`, which may lose vectors but lets parsing catch up. SR-IOV indirect paths return timeouts on PSP programming failure. `wait_for_idle` is a TODO returning `-ETIMEDOUT`, so callers must not treat idle wait as implemented. Big-endian rptr writeback is called out as unchecked.

## Test Signals
Signals include boot/resume interrupt delivery, ring0/ring1 IRQ processing, self-interrupt write-pointer update work, SR-IOV VF operation, MSI/non-MSI doorbell rearm behavior, interrupt storm tests, overflow injection, and clock/power-gating transitions.
