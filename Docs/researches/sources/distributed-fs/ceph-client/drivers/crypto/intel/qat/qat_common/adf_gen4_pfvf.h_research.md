## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.h

Purpose: Declares Gen4 PF/VF PF-side operation initialization.

Important APIs/types: Declares `adf_gen4_init_pf_pfvf_ops()` when `CONFIG_PCI_IOV` is enabled. Otherwise, an inline fallback sets `enable_comms` to `adf_pfvf_comms_disabled`.

Control flow/state: No runtime state is stored. Compile-time SR-IOV support controls whether real communication ops are installed.

Dependencies/integration: Used by Gen4 PF product drivers during PF/VF ops setup.

Risks and test signals: Build tests should cover `CONFIG_PCI_IOV=y/n`. Runtime tests should confirm no accidental PF/VF communication dependency when SR-IOV is disabled.
