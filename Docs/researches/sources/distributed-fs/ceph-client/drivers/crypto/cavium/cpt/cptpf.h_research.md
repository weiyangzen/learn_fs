# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf.h

Purpose: declares PF-side Thunder CPT device state, microcode metadata, VF bookkeeping, sizing limits, and mailbox handler entry point.

Important APIs and types: constants cover core groups, SE/AE core counts, maximum VFs, MSI-X vector mapping, and microcode version length. `struct microcode` tracks AE/SE firmware validity, group, core mask, DMA backing, and version. `struct cpt_vf_info` tracks VF state, priority, ID, and queue length. `struct cpt_device` stores flags, VF array, BAR mapping, PCI device, loaded microcode array, group index, and detected SE/AE core counts.

Control flow and state: persistent state is per-PF and mirrors hardware resources: loaded firmware groups, enabled core masks, and SR-IOV VF configuration. `cpt_mbox_intr_handler()` is exported to `cptpf_main.c` IRQ handling.

Dependencies and integration points: depends on `cpt_common.h`, PF main code, and PF mailbox code. It is the contract between PCI probe/remove, firmware loading, and VF mailbox requests.

Risks and test signals: risks include fixed core/VF limits drifting from hardware, loaded microcode state needing to match group programming, and non-atomic VF state updates from IRQ context. Test signals include firmware group allocation, VF queue binding to valid groups, SR-IOV enable count capping, and clean microcode DMA free on remove.
