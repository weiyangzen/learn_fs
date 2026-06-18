# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3.c

## Purpose
`vgic-v3.c` is the main runtime backend for GICv3-compatible VGIC CPU interface state. It configures ICH_HCR traps, encodes/folds list registers, handles deactivation, manages VMCR/APR state, saves LPI pending tables, validates v3 MMIO resources, probes host GICv3 capability, and loads/puts v3 or nested state around VCPU execution.

## Important APIs, Types, And Functions
Core runtime functions include `vgic_v3_configure_hcr()`, `vgic_v3_fold_lr_state()`, `vgic_v3_deactivate()`, `vgic_v3_populate_lr()`, `vgic_v3_clear_lr()`, `vgic_v3_set_vmcr()`, `vgic_v3_get_vmcr()`, `vgic_v3_reset()`, `vcpu_set_ich_hcr()`, `vgic_v3_lpi_sync_pending_status()`, `vgic_v3_save_pending_tables()`, `vgic_v3_check_base()`, `vgic_v3_map_resources()`, `vgic_v3_enable_cpuif_traps()`, `vgic_v3_probe()`, `vgic_v3_load()`, and `vgic_v3_put()`. `vgic_v3_compute_lr()` is the private LR encoder.

## Control Flow
Before entry, VGIC core populates LRs with INTID, group, active/pending state, HW physical ID, EOI hints, and full priority. `vgic_v3_configure_hcr()` enables the interface and sets maintenance interrupt controls for IRQs outside LRs, empty SGI tracking, group enable/disable transitions, and DIR trapping when needed. On exit, `vgic_v3_fold_lr_state()` folds used LRs into `vgic_irq` state and replays EOICOUNT deactivations for active interrupts outside LRs. `vgic_v3_deactivate()` handles DIR writes in EOImode 1 and falls back to active-clear MMIO if the target IRQ is still on an LR.

Probe reads ICH_VTR via hyp, derives LR count and feature bits, optionally registers v2 compatibility, registers v3 device ops, handles GICv4 enablement, applies workarounds for broken SEIS, computes CPU interface trap bits, and records global VGIC type and limits. Load/put either delegate to nested VGIC logic or save/restore VMCR/APRs through hyp and coordinate GICv4 vPE residency.

## State And Persistence
Per-VCPU state includes `vgic_hcr`, `vgic_vmcr`, `vgic_sre`, `vgic_lr[]`, APR arrays, `used_lrs`, ID and priority bit counts, and PENDBASER defaults. VM persistent state includes active SPI count, redistributor regions, distributor base, GICv4 capability, and pending LPI tables in guest memory. `vgic_v3_save_pending_tables()` writes LPI pending bits back to guest RAM and temporarily unmaps/remaps vPEs on GICv4.1 to sample VLPI state.

## Dependencies And Integration Points
The file integrates with hyp save/restore routines, common VGIC ap_list scheduling, `vgic-mmio-v3.c` redistributor resource state, `vgic-its.c` LPI structures, GICv4 vPE load/put, nested VGIC support, KVM MMU and firmware GIC info, static keys for trap modes, and CPU erratum/workaround detection.

## Risks
LR fold/populate correctness is central to interrupt delivery and migration. EOICOUNT replay relies on ap_list ordering. DIR trapping is required on hardware without TDIR or with active SPIs outside LRs; missing it can leave stale active state. Pending-table save must coordinate with GICv4.1 residency. Probe paths must preserve v2 compatibility and pKVM restrictions without exposing unsupported devices.

## Test Signals
Exercise v3 IRQ injection/folding for edge, level, SGI, SPI, LPI, and HW-mapped interrupts; EOImode 0/1 deactivation; pending LPI table save/restore; redistributor overlap checks; probe on hosts with and without v2 compatibility/GICv4; trap-bit early params; nested load/put delegation; and migration of VMCR/APR/LR state.
