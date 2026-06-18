# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf.h

## Purpose
This PF header defines the Physical Function driver state, VF bookkeeping, FLR work records, mailbox work entry points, and inline CPT LF setup/cleanup prototypes. It is the shared state contract between PF probe, PF mailbox handling, SR-IOV support, devlink, microcode management, and inline IPsec setup.

## Important APIs and types
`struct otx2_cptvf_info` tracks each enabled VF, including PF backpointer, mailbox work item, VF PCI device pointer, VF id, and interrupt index. `struct cptpf_flr_work` wraps per-VF FLR handling. `struct otx2_cptpf_dev` holds PF BAR mappings, AF/PF and VF/PF mailbox objects, workqueues, VF table, engine groups, LF state for CPT0 and CPT1, hardware capability cache, PF id, VF counts, sysfs-tunable limits, CPT1 presence, devlink handle, and serialization mutex. Prototypes expose AF/PF and VF/PF mailbox handlers plus `otx2_inline_cptlf_setup()` and `otx2_inline_cptlf_cleanup()`.

## Control flow
The header itself has no executable flow. `otx2_cptpf_main.c` allocates and populates `otx2_cptpf_dev` during probe, then SR-IOV enable fills the VF table and FLR work. `otx2_cptpf_mbox.c` consumes the same state to process AF responses, VF requests, and inline IPsec LF configuration.

## State and persistence
All fields are runtime kernel/device state. Engine groups and capability caches persist only while the PF driver is loaded. VF state exists only while SR-IOV is enabled. Sysfs attributes mutate fields such as `kvf_limits` and `sso_pf_func_ovrd`, but no file-backed persistence is implemented.

## Dependencies and integration points
The header depends on common CPT definitions, microcode engine-group types, and LF structures. It integrates PF core code with devlink, mailbox code, LF code, VF request forwarding, and CN10K LMTST support.

## Risks and edge cases
`otx2_cptpf_dev` centralizes many ownership domains, so cleanup order matters: VFs, inline LFs, devlink, sysfs, engine groups, interrupts, mailboxes, and LMT memory must be torn down in dependency order. The mutex serializes AF mailbox access and protects paths that forward VF requests; callers must avoid unprotected mailbox reuse.

## Test signals
PF probe/remove, SR-IOV enable/disable, VF FLR, VF mailbox forwarding, inline IPsec LF setup on CPT0/CPT1, devlink custom engine group operations, and sysfs `kvf_limits` updates are the main integration signals for this state definition.
