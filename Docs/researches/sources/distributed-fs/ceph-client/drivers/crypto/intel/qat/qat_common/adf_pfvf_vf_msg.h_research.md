# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.h

Purpose: declares VF-side PF/VF high-level message helpers with no-op fallbacks for non-IOV builds.

Important API: declares VF init/shutdown/restart-complete notifications plus version, capabilities, and ring-to-service query functions. In non-`CONFIG_PCI_IOV` builds, init returns success and shutdown is empty.

Control flow and state: header-only configuration gating. Runtime state is `accel_dev->vf` and hardware data updated by the implementation.

Dependencies and integration: consumed by VF device setup and VF protocol enablement. Complements `adf_pfvf_vf_proto.h`, which provides lower-level request transport.

Risks and test signals: no-op fallbacks can mask missing SR-IOV coverage in tests. Build both PCI_IOV modes and verify VF probe obtains PF capabilities before services depend on them.
