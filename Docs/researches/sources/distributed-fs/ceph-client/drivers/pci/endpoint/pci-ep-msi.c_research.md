<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-msi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-msi.c

## Purpose
Implements the endpoint-function MSI doorbell helper. It allocates platform MSI vectors for an EPC parent device and records the MSI message address/data in the first EPF so endpoint functions can expose those messages to a host as doorbell targets.

## Important APIs, Types, and Functions
`pci_epf_alloc_doorbell()` allocates `struct pci_epf_doorbell_msg` entries, initializes platform MSI interrupts, and records Linux virtual IRQs. `pci_epf_free_doorbell()` releases all platform MSI interrupts and clears EPF doorbell state. `pci_epf_write_msi_msg()` is the MSI message writer callback that copies generated `struct msi_msg` values into the EPF doorbell array.

## Control Flow
Allocation verifies that the requesting EPF is the first EPF on the EPC list, rejects duplicate allocation, locates an immutable platform MSI parent domain for `epc->dev.parent`, sets that domain on the parent device, allocates the message array, calls `platform_device_msi_init_and_alloc_irqs()`, and stores `msi_get_virq()` results per doorbell. The write callback looks up the EPC by device name and updates the matching doorbell message slot when the platform MSI layer creates or rewrites messages.

## State and Persistence
Doorbell state lives in `epf->db_msg` and `epf->num_db` until freed. The MSI domain is attached to the EPC parent device. The helper does not persist data outside the live kernel objects, and it intentionally supports only one EPF per EPC for doorbell allocation.

## Dependencies and Integration Points
Depends on irqdomain/MSI APIs, OF MSI mapping, platform-device MSI allocation, the EPC class lookup helper, and EPF state. It is consumed by `pci-epf-test.c` and `pci-epf-vntb.c` to implement host-visible doorbells.

## Risks and Edge Cases
The explicit TODO means multi-EPF doorbells are unsupported; using this helper when multiple EPFs share an EPC returns `-EINVAL`. Mutable MSI controllers and missing MSI domains are rejected. The write callback looks up the EPC by `dev_name(msi_desc_to_dev(desc))`, so naming consistency is important. Freeing releases all platform MSI IRQs for the EPC parent, which assumes this helper owns them.

## Test Signals
Test allocation/free cycles, duplicate allocation returning `-EBUSY`, missing or mutable MSI domain failure, IRQ request/use by caller drivers, correct MSI message address/data propagation, and rejection when the requester is not the first EPF on the EPC list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-msi.c -->
