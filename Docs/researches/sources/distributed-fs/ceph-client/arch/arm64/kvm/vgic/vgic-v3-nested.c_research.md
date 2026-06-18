# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3-nested.c

## Purpose
`vgic-v3-nested.c` implements nested virtualization support for the GICv3 virtual CPU interface. It lets an L1 hypervisor program virtual ICH_* state for an L2 guest, shadows that state into host hardware LRs when running L2, syncs results back to the VNCR-backed L1 state, and synthesizes maintenance interrupt status.

## Important APIs, Types, And Functions
`struct mi_state` holds computed EISR/ELRSR/pending status. `struct shadow_if` is per-CPU shadow VGIC state with a compact LR map. Public entry points are `vgic_state_is_nested()`, `vgic_v3_get_eisr()`, `vgic_v3_get_elrsr()`, `vgic_v3_get_misr()`, `vgic_v3_flush_nested()`, `vgic_v3_sync_nested()`, `vgic_v3_load_nested()`, `vgic_v3_put_nested()`, `vgic_v3_handle_nested_maint_irq()`, and `vgic_v3_nested_update_mi()`.

## Control Flow
`vgic_state_is_nested()` enables the nested path when the VCPU is in nested context and L1 has set virtual IRQ/FIQ routing with matching IMO/FMO bits. On L2 load, `vgic_v3_create_shadow_state()` copies L1-visible HCR, VMCR, APRs, SRE, and valid LRs from vCPU sysreg storage into the per-CPU shadow. `vgic_v3_create_shadow_lr()` skips invalid LRs, translates guest pINTIDs for HW-backed LRs to host hardware interrupt IDs, compacts them into the real LR array, and records the source-index map. The shadow is restored to hardware and traps are activated.

On L2 put/sync, host LR state is read back using the LR map. State bits are merged into the original L1-visible LR, HW deactivation side effects are emulated through `vgic_v3_deactivate()`, VMCR and EOIcount are copied back, hardware HCR is disabled, and L1 maintenance interrupt level is recomputed. Trapped status registers (`EISR`, `ELRSR`, `MISR`) are synthesized from in-memory L1 LR/HCR/VMCR state rather than stored directly.

## State And Persistence
Persistent nested state lives in the VCPU sysreg array for ICH_LR*, ICH_AP*, ICH_HCR_EL2, and ICH_VMCR_EL2. The per-CPU `shadow_if` is transient and only valid during L2 execution on that CPU. Maintenance interrupt state is not stored as a hardware register snapshot; it is recomputed and injected as the VM's configured maintenance PPI.

## Dependencies And Integration Points
It depends on nested context helpers, VNCR/sysreg storage, low-level GICv3 LR accessors, VGIC IRQ lookup for HW LR translation, `vgic_v3_deactivate()` from the main v3 runtime, trap activation helpers, and KVM virtual IRQ injection. It is called by `vgic_v3_load()` and `vgic_v3_put()` when nested state is active.

## Risks
The compact LR map must preserve correspondence between L1 LR indexes and hardware LR indexes. HW-bit translation must avoid letting L1 name arbitrary host physical interrupts. Maintenance interrupt emulation is approximate because many ICH registers are memory-backed and L0 only observes status at load/put or trapped register reads. The code warns that separate virtual IRQ/FIQ routing is unsupported.

## Test Signals
Use nested KVM tests that run an L2 guest with L1-programmed virtual interrupts, HW-backed timer LR translation, EISR/ELRSR/MISR reads, L2 exit with pending maintenance interrupt, EOICOUNT propagation, and invalid HW-bit pINTID cases. Lockless per-CPU shadow assumptions should be tested under VCPU migration and preemption-disabled entry paths.
