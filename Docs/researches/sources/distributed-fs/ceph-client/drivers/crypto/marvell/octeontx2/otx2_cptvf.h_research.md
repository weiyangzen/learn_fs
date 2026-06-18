# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf.h

## Purpose
This VF header defines the Virtual Function device state and mailbox-facing APIs. It is the shared contract between VF probe/remove, PF/VF mailbox handling, LF setup, request submission, and Crypto API algorithm registration.

## Important APIs and types
`struct otx2_cptvf_dev` holds VF BAR mappings, PF/VF mailbox mapping, PCI device, attached LF state, VF id, mailbox workqueue/work item, selected CPT block address, bounce buffer, hardware capability flags, and engine capability words. Prototypes include `otx2_cptvf_pfvf_mbox_intr()`, `otx2_cptvf_pfvf_mbox_handler()`, `otx2_cptvf_send_eng_grp_num_msg()`, `otx2_cptvf_send_kvf_limits_msg()`, `otx2_cpt_mbox_bbuf_init()`, and `otx2_cptvf_send_caps_msg()`.

## Control flow
The header has no executable flow. VF main allocates and populates `otx2_cptvf_dev`, initializes mailbox and LFs, and later algorithm/request code retrieves it from `pci_get_drvdata()`. Mailbox code fills VF id, LF attach state, MSI-X offsets, kernel VF limits, and engine capabilities.

## State and persistence
All state is runtime-only and tied to the VF PCI device. The mailbox bounce buffer is device-managed memory. Engine capabilities and VF id are populated from PF responses during probe and are lost on remove.

## Dependencies and integration points
The header depends on RVU mailbox definitions and CPT LF structures. It integrates VF PCI probe with PF mailbox service, LF common setup, request manager, and crypto algorithms.

## Risks and edge cases
Because mailbox responses mutate fields consumed immediately by probe, ready/capability/order failures can leave incomplete state. `bbuf_base` changes the mailbox device base to a bounce buffer, so synchronization from hardware mailbox memory is required before response processing.

## Test signals
Signals include VF probe/remove, ready message setting a valid `vf_id`, capability response filling `eng_caps`, KVF limit response selecting LF count, valid MSI-X offsets, and mailbox bounce-buffer synchronization on both OTX2 and CN10K mailbox layouts.
