# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.h

Purpose: declares PF-side PF/VF notification and block-message provider interfaces with no-op fallbacks when PCI IOV is disabled.

Important API: declares restart/fatal notification helpers, `adf_pf2vf_blkmsg_provider` callback type, `adf_pf_capabilities_msg_provider`, and `adf_pf_ring_to_svc_msg_provider`.

Control flow and state: when `CONFIG_PCI_IOV` is absent, notification functions compile to empty inline stubs so common lifecycle code can call them without ifdefs. Provider declarations remain available for protocol code.

Dependencies and integration: includes `adf_accel_devices.h` for device types. Implemented by `adf_pfvf_pf_msg.c` and used by SR-IOV and PF protocol request handling.

Risks and test signals: stubs mean PF/VF tests must cover both IOV-enabled and disabled builds. Check compile coverage for both configs and runtime delivery of restarting/restarted/fatal notifications in SR-IOV mode.
