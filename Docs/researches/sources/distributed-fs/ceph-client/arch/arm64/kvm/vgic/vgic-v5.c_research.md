# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v5.c

## Purpose
`vgic-v5.c` implements early KVM support for GICv5/GCIE guests and the GICv5 PPI handling model. It probes and registers v5 and legacy v3-compatible devices, tracks implemented PPIs, initializes exposed userspace PPIs, handles mostly hardware-managed PPI state, and saves/restores GICv5 CPU interface state around VCPU execution.

## Important APIs, Types, And Functions
Probe and setup functions are `vgic_v5_probe()`, `vgic_v5_reset()`, `vgic_v5_init()`, `vgic_v5_map_resources()`, and `vgic_v5_finalize_ppi_state()`. PPI helpers include `vgic_v5_ppi_queue_irq_unlock()`, `vgic_v5_set_ppi_dvi()`, `vgic_v5_set_ppi_ops()`, `vgic_v5_has_pending_ppi()`, `vgic_v5_fold_ppi_state()`, and `vgic_v5_flush_ppi_state()`. CPU interface state functions are `vgic_v5_load()`, `vgic_v5_put()`, `vgic_v5_get_vmcr()`, `vgic_v5_set_vmcr()`, `vgic_v5_restore_state()`, and `vgic_v5_save_state()`.

## Control Flow
Probe marks the global type as VGIC_V5, disables v2/GICv4 assumptions, skips v5 registration under protected KVM, discovers implemented architectural PPIs, and registers the v5 KVM device. If legacy GICv3 compatibility is available, it also registers a v3 device, fills ICH_VTR state, enables the global GICv3 CPU interface static branch, and applies v3 trap configuration.

VM init rejects nested GICv5 VMs, then exposes only implemented userspace-drivable PPIs, currently centered on SW_PPI. Finalization inspects VCPU0's implemented PPIs and exposes only PPIs with an owner or the SW_PPI, while recording hardware mode level/edge information. PPI queueing does not put interrupts on the VGIC ap_list; it unlocks and kicks the target VCPU because the hardware CPU interface handles most PPI delivery. Entry flush builds pending PPI shadow state, and exit fold merges hardware exit pending/active state back into `vgic_irq`.

## State And Persistence
Persistent VM state includes implemented PPI capability masks, userspace PPI mask, exposed VGIC PPI mask, PPI hardware mode register, and per-VCPU GICv5 CPU interface fields: VMCR, APR, PPI priority registers, active/pending/direct-virtual-injection bitmaps, and residency flag. Edge pending state is ORed on fold to avoid losing incoming edges, while flush clears edge pending after transferring it to the shadow pending registers.

## Dependencies And Integration Points
It depends on ARM64 GICv5 CPU interface capabilities, GICv5 hyp save/restore helpers, generic VGIC IRQ objects and ops override, PMU feature detection for PMUIRQ exposure, `vgic-v3.c` for legacy compatibility registration/traps, and the KVM device layer for the limited v5 userspace ABI.

## Risks
The implementation is intentionally narrower than v2/v3: no nested GICv5 support and no pKVM v5 guests. PPI exposure depends on owner state sampled from VCPU0, so heterogeneous or late owner changes would be risky. Residency guards avoid double save/restore on WFI paths; mistakes could lose VMCR/APR state. Priority synchronization only happens on WFI entry, so tests should verify priority changes around sleep paths.

## Test Signals
Cover probe on v5-only, v5 plus legacy v3, and pKVM configurations; userspace PPI mask readback; nested VM rejection; PPI finalization with owned and unowned PPIs; pending/active fold and flush for edge and level PPIs; WFI double load/put paths; VMCR get/set; and legacy v3 device behavior on GICv5 hosts.
