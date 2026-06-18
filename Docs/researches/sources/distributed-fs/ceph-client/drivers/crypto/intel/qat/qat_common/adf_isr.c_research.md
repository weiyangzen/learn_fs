# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_isr.c

Purpose: allocates MSI-X vectors, registers QAT interrupt handlers, manages bank response tasklets, handles AE-cluster interrupts for VF2PF, PM, and RAS events, and owns the shared misc workqueue used by several subsystems.

Important APIs: `adf_isr_resource_alloc`, `adf_isr_resource_free`, `adf_enable_vf2pf_interrupts`, `adf_disable_all_vf2pf_interrupts`, `adf_init_misc_wq`, `adf_exit_misc_wq`, `adf_misc_wq_queue_work`, `adf_misc_wq_queue_delayed_work`, and `adf_misc_wq_flush`.

Control flow and state: allocation builds IRQ metadata, enables MSI-X, initializes bank tasklets, and requests bank plus AE-cluster vectors. Bank ISR clears interrupt flags and schedules the response handler. AE ISR checks VF2PF interrupts first in SR-IOV mode, then PM, then RAS. VF2PF handling disables pending VF interrupts, applies rate limiting, and queues PF work.

Dependencies and integration: uses PCI IRQ APIs, transport CSR ops, PF/VF ops, RAS ops, PM hooks, SR-IOV VF info, and workqueues used by telemetry/timers/PF responses.

Risks and test signals: IRQ count differs with SR-IOV; affinity hints and tasklets need cleanup on failures. Test MSI-X allocation failure unwinds, VF interrupt flood rate limiting, RAS fatal notification, PM interrupt dispatch, and workqueue lifecycle.
