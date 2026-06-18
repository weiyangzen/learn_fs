# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/Makefile Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/Makefile

### Purpose
This Makefile wires the OcteonTX CPT PF and VF drivers into the kernel build when `CONFIG_CRYPTO_DEV_OCTEONTX_CPT` is enabled.

### Important APIs, Types, And Functions
It builds two composite objects: `octeontx-cpt.o` from `otx_cptpf_main.o`, `otx_cptpf_mbox.o`, and `otx_cptpf_ucode.o`; and `octeontx-cptvf.o` from `otx_cptvf_main.o`, `otx_cptvf_mbox.o`, `otx_cptvf_reqmgr.o`, and `otx_cptvf_algs.o`.

### Control Flow, State, And Persistence
The PF object owns physical-function probing, SR-IOV, mailbox service, and microcode/engine-group management. The VF object owns virtual-function probing, PF mailbox handshakes, CPT instruction queues, completion processing, and crypto algorithm registration. Build composition persists only as link-time object membership controlled by the Kconfig symbol.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with symbols shared across PF/VF sources, especially mailbox definitions in `otx_cpt_common.h` and exported microcode helpers used by PF mailbox handling. Risks are unresolved symbols if object membership changes and accidentally building only PF or VF halves. Test signals are `CONFIG_CRYPTO_DEV_OCTEONTX_CPT=y/m` builds and module load/unload with both `octeontx-cpt` and `octeontx-cptvf`.
