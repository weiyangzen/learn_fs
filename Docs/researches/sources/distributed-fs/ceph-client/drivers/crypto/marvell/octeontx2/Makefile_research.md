# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/Makefile Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/Makefile

### Purpose
This Makefile composes the OcteonTX2/CN10K CPT common, PF, and VF driver objects when `CONFIG_CRYPTO_DEV_OCTEONTX2_CPT` is enabled.

### Important APIs, Types, And Functions
It builds `rvu_cptcommon.o` from CN10K, LF, and mailbox common files; `rvu_cptpf.o` from PF main, PF mailbox, PF microcode, and devlink files; and `rvu_cptvf.o` from VF main, VF mailbox, VF request manager, and VF algorithms. It also adds the OcteonTX2 AF include path for `rvu.h` and `mbox.h`.

### Control Flow, State, And Persistence
The common object provides shared LF, mailbox, and CN10K hardware ops exported to PF/VF modules. PF and VF objects are built as separate driver units under the same Kconfig switch. Build state is limited to object membership and include path selection.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile integrates the crypto driver with the networking AF headers under `drivers/net/ethernet/marvell/octeontx2/af`. Risks include broken namespace exports if common objects are omitted, missing include path for AF mailbox definitions, and link errors from splitting shared CN10K helpers. Test signals include all built-in/module combinations for `CONFIG_CRYPTO_DEV_OCTEONTX2_CPT`, modpost namespace checks, and PF/VF module load.
