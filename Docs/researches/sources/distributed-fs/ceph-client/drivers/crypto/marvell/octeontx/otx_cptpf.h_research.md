# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf.h

### Purpose
`otx_cptpf.h` defines the PF driver state container and PF-local cross-file APIs for OcteonTX CPT physical-function management.

### Important APIs, Types, And Functions
`struct otx_cpt_device` stores the MMIO register base, PCI device, engine-group manager, list node, PF type, maximum VF count, and enabled VF count. It declares `otx_cpt_mbox_intr_handler()` from the PF mailbox path and `otx_cpt_disable_all_cores()` from the microcode/engine management path.

### Control Flow, State, And Persistence
The PF probe allocates and stores this structure as PCI drvdata, initializes hardware capabilities and engine groups, and later uses the same state for SR-IOV enable/disable and mailbox handling. Engine-group state persists across VF mailbox requests while SR-IOV is active and is marked read-only during VF exposure.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on `otx_cptpf_ucode.h` for `struct otx_cpt_eng_grps`. Risks include stale `vfs_enabled` relative to PCI SR-IOV state, mailbox handlers seeing partially initialized engine groups, and PF teardown while VFs are still live. Test signals include PF probe/remove, SR-IOV sysfs configuration, mailbox interrupts after VF probe, engine disable on remove, and drvdata lifetime checks.
