# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.h

Purpose: UIOM protection-domain, registration, and chunk data model plus public APIs.

Important APIs/types: defines access constants, maximum PD/MR/MR-size/page-size values, `struct usnic_uiom_dev`, `struct usnic_uiom_pd`, `struct usnic_uiom_reg`, `struct usnic_uiom_chunk`, and APIs for PD allocation, device attach/detach/listing, memory registration, and release.

Control flow: verbs PD allocation creates `usnic_uiom_pd`; QP group VF binding attaches VF devices; MR registration creates `usnic_uiom_reg`; MR deregistration releases it.

State and persistence: header shows the persistent IOMMU domain, interval tree, attached device list, VA/length/offset/writable fields, pinned-page chunk list, work item, and owning mm reference.

Dependencies and integration: includes Linux list/scatterlist and the usNIC interval tree header. Used by verbs, QP group, and UIOM implementation.

Risks: public constants advertise very large MR count/size limits; actual behavior is constrained by memlock, IOMMU, and pinned-page availability. The `work_struct` and `page_size` fields are present but unused in the mapped implementation, suggesting legacy design surface.

Test signals: compile coverage, PD attach/detach with multiple VFs, MR registration limits, and release of chunk lists.
