## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.h

Purpose: Declares Gen2 PF/VF communication initialization and Gen2 error source/mask offsets used for VF2PF interrupt handling.

Important APIs/types: Defines ERRSOU/ERRMSK offsets and, when `CONFIG_PCI_IOV` is enabled, declares `adf_gen2_init_pf_pfvf_ops()` and `adf_gen2_init_vf_pfvf_ops()`. Without SR-IOV, inline fallbacks disable communications by assigning `adf_pfvf_comms_disabled`.

Control flow/state: No state is stored. The compile-time branch decides whether real PF/VF ops are installed.

Dependencies/integration: Used by Gen2 PF and VF product drivers during `adf_pfvf_ops` setup.

Risks and test signals: Build matrix coverage with and without `CONFIG_PCI_IOV` is important. Runtime tests should confirm PF/VF messaging is unavailable but harmless when SR-IOV support is compiled out.
