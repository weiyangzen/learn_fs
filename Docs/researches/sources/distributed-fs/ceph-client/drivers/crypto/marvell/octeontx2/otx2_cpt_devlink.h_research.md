# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.h

### Purpose
`otx2_cpt_devlink.h` declares the small devlink integration surface for the OcteonTX2 CPT PF driver.

### Important APIs, Types, And Functions
`struct otx2_cpt_devlink` stores the devlink handle and owning `struct otx2_cptpf_dev`. It declares `otx2_cpt_register_dl()` and `otx2_cpt_unregister_dl()`.

### Control Flow, State, And Persistence
The PF driver creates a devlink object during probe/setup and stores the pointer in PF state; unregister consumes the same PF pointer during teardown. The private struct ties devlink callbacks back to the PF's engine-group and AF mailbox state.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on common CPT definitions and PF state. Risks are mostly lifetime-related: callbacks must not outlive the PF and `cptpf->dl` must be cleared or treated carefully by teardown code. Test signals include PF probe/remove with devlink enabled, devlink command execution after registration, and no callbacks after unregister.
