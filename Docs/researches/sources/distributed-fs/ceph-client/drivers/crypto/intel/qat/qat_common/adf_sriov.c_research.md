# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sriov.c

Purpose: manages QAT PF SR-IOV enable/disable, VF info initialization, VF2PF work scheduling, and the PF response workqueue.

Important APIs: `adf_schedule_vf2pf_handler`, `adf_reenable_sriov`, `adf_disable_sriov`, `adf_sriov_configure`, `adf_init_pf_wq`, and `adf_exit_pf_wq`. Static helpers enable/disable SR-IOV and add SR-IOV configuration.

Control flow and state: enabling warns without IOMMU, brings down a running idle PF, adds kernel config forcing CY/DC counts to zero, allocates `pf.vf_info`, brings device up without reconfig, initializes VF locks/ratelimits, configures IOV threads, enables VF2PF interrupts, and enables all hardware VFs. Disabling checks busy/reset state, optionally brings device down, notifies VFs restarting, waits for completion, disables PCI SR-IOV and interrupts, clears IOV threads, destroys locks, and frees VF info unless restarting.

Dependencies and integration: uses PCI SR-IOV APIs, QAT lifecycle, config, PF/VF messaging, ISR VF interrupts, and workqueues.

Risks and test signals: `numvfs` is ignored and all hardware VFs are enabled; error paths must clean config and VF info. Test enable/disable while busy, IOMMU warning, VF interrupt flood handling, restart reenable, and full-VF hardware resource mapping.
