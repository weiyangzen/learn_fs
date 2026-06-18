# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_queue_pair.h

Purpose: declares internal queue-pair structures, ioctl payloads, page-store formats, and broker/client APIs.

Important types/APIs: `struct ppn_set` stores guest PPN lists. `struct vmci_qp_alloc_info`, `vmci_qp_set_va_info`, `vmci_qp_page_file_info`, and `vmci_qp_dtch_info` are ioctl payloads. `struct vmci_qp_page_store` describes guest backing memory. `struct vmci_queue` pairs queue header, saved header, and OS-specific kernel interface. Prototypes expose broker lifecycle, allocation, page-store setup, detach, guest endpoint cleanup, generic `vmci_qp_alloc()`, and broker map/unmap.

Control flow/integration: host ioctl code uses the ioctl structs and broker APIs. Exported public qpair APIs in the C file use `vmci_qp_alloc()` to choose host/guest implementation. Guest queue allocation passes PPN sets to hypervisor commands.

State/persistence: ioctl structs are ABI-facing. `vmci_qp_page_file_info` includes comments documenting compatibility with old VMX struct versions. Queue headers can be saved during memory unmap.

Risks: struct layout changes can break VMX compatibility. `VMCI_QP_PAGESTORE_IS_WELLFORMED()` only checks length >= 2; callers must validate sizes and addresses elsewhere. Include dependency on `vmci_context.h` makes this part of the internal subsystem cycle.

Test signals: ioctl struct size/version compatibility, old/new VMX page-file paths, page-store validation, and qpair allocation behavior across host/guest personalities.
