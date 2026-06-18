# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.h

Purpose: this header provides inline firmware request initialization helpers and the WQ Ethernet descriptor posting helper, plus resource-management prototypes.

Important APIs, types, and functions: `snic_icmnd_init()` fills a `SNIC_REQ_ICMND` request with command id, host id, context, flags, target/lun, CDB, data length, SGL address, sense address, and sense length. `snic_itmf_init()` fills a `SNIC_REQ_ITMF` task-management request. `snic_queue_wq_eth_desc()` obtains the next vNIC WQ descriptor, encodes a `wq_enet_desc`, and posts it through `svnic_wq_post()`.

Control flow: SCSI queueing and task-management paths initialize requests with these helpers before calling `snic_queue_wq_desc()`. That queueing routine maps the whole request buffer for DMA and then calls the WQ descriptor helper.

State and persistence: the header mutates request buffers and WQ ring state supplied by callers. It owns no state.

Dependencies and integration: includes SNIC I/O, WQ descriptor, vNIC WQ, firmware interface, and CQ firmware headers. It is shared by `snic_scsi.c`, `snic_res.c`, and queueing code.

Risks: helpers trust CDB length and caller-provided LUN pointer. `snic_itmf_init()` leaves timeout unfilled despite a timeout field in the wire structure. `snic_queue_wq_eth_desc()` hard-codes offload/vlan/fcoe fields for SNIC use and assumes a descriptor is available.

Test signals: validate encoded host requests with firmware or trace dumps for read, write, no-data, abort, LUN reset, and HBA reset requests. DMA/IOMMU testing should verify WQ descriptors point at mapped request buffers.
