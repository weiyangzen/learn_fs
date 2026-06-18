# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.h

## Purpose
`qla_nvme.h` defines the qla2xxx FC-NVMe private structures, firmware IOCB layouts, constants, and public prototypes used by `qla_nvme.c` and other qla2xxx files that submit or complete NVMe-FC commands and link-service exchanges.

It forms the interface between the Linux NVMe-FC transport, qla2xxx SRB machinery, and QLogic firmware IOCB formats for `COMMAND_NVME`, LS4 request, and unsolicited LS4 receive entries.

## Important APIs, Types, And Functions
Queue constants include `MIN_NVME_HW_QUEUES`, `DEF_NVME_HW_QUEUES`, `Q2T_NVME_NUM_TAGS`, and `QLA_MAX_FC_SEGMENTS`. PURLS retry policy is described by `PURLS_MSLEEP_INTERVAL` and `PURLS_RETRY_COUNT`.

`struct nvme_private` is per-NVMe-FC request state. It stores the qla2xxx SRB pointer, LS request descriptor, scheduled LS completion work, scheduled abort work, completion status, and a spinlock used to coordinate abort and completion.

`struct qla_nvme_rport` is private data attached to an `nvme_fc_remote_port`. It points back to the qla2xxx `fc_port` and may reference an unsolicited LS context.

`struct cmd_nvme` defines the firmware FC-NVMe command IOCB. It includes a handle, NPORT handle, timeout, DSD count, response DSD length/address, command IU DSD length/address, byte count, destination PortID, VP index, first payload DSD, and control flags such as `CF_READ_DATA`, `CF_WRITE_DATA`, `CF_DATA_SEG_DESCR_ENABLE`, `CF_DIF_SEG_DESCR_ENABLE`, `CF_NVME_FIRST_BURST_ENABLE`, and `CF_ADMIN_ASYNC_EVENT`.

`struct pt_ls4_request` defines the firmware pass-through LS4 request IOCB used for outgoing NVMe LS requests, LS responses, LS rejects, and exchange termination. It carries status, NPORT handle, TX/RX DSD counts, VP index, timeout, responder/originator control flags, exchange address, byte counts, and two DSD slots.

`struct pt_ls4_rx_unsol` defines unsolicited received FC-NVMe LS entries. It carries VP index, NPORT handle, frame size, exchange address, destination/source IDs, FC header fields, OX/RX IDs, a descriptor, and the first payload words.

Exported prototypes include `qla_nvme_register_hba()`, `qla_nvme_register_remote()`, `qla_nvme_delete()`, `qla24xx_nvme_ls4_iocb()`, and `qla24xx_async_gffid_sp_done()`.

## Control Flow
The header does not execute logic, but its data layouts drive the `qla_nvme.c` flows.

For FCP I/O, `qla2x00_start_nvme_mq()` fills `cmd_nvme`: it marks `entry_type = COMMAND_NVME`, stores a qla2xxx handle, sets control flags from NVMe-FC direction, first-burst, EDIF, and admin async-event state, writes NPORT/PortID/VP routing, points firmware at the NVMe command IU and response IU DMA addresses, then appends payload DSDs.

For LS requests and responses, qla2xxx code fills `pt_ls4_request`: originator requests use TX and RX buffers from the transport LS request, responder replies use the unsolicited exchange address and TX response buffer, reject IOCBs use a locally formatted FC-NVMe LS reject buffer, and terminate IOCBs set responder-terminate control flags with no payload.

For unsolicited LS receive, response queue handling provides a `pt_ls4_rx_unsol` to `qla2xxx_process_purls_iocb()`, which uses VP index for virtual host lookup, source ID for `fc_port` lookup, exchange and OX_ID for later response, and payload offset/first-packet length constants for purex payload assembly.

## State And Persistence
There is no persistent storage. `struct nvme_private` and `struct qla_nvme_rport` are transport-private runtime allocations. Firmware IOCB structures are transient request/response ring entries.

`nvme_private.sp` is cleared under lock during completion. `qla_nvme_rport.fcport` links transport remote ports back to qla2xxx FC sessions for as long as the remote port remains registered. The unsolicited context forward declaration allows the remote-port private object to point at an active unsolicited LS exchange.

The constants in this header encode stable firmware/transport constraints, such as default queue count, first LS payload offset, number of target tags, and maximum FC segments.

## Dependencies And Integration Points
The header includes FC protocol UAPI headers, `linux/nvme-fc-driver.h`, `qla_def.h`, and `qla_dsd.h`. It therefore depends on Linux FC ELS/FS types, NVMe-FC transport request structures, qla2xxx host/port/SRB types, and qla2xxx DSD definitions.

It is consumed by `qla_nvme.c` and by other qla2xxx source files that need to build LS4 IOCBs or finish asynchronous GFF_ID work. Firmware consumes the binary layouts of `cmd_nvme`, `pt_ls4_request`, and `pt_ls4_rx_unsol`.

## Risks And Edge Cases
The firmware IOCB layouts are ABI-sensitive. Field movement, widening, signedness changes, or removing `__packed` on unaligned 64-bit fields can break DMA descriptors.

Control flag bit definitions overlap with firmware semantics. Setting both read and write, missing first-burst constraints, or using responder/originator LS4 control flag shifts incorrectly can cause firmware rejection or protocol errors.

The unsolicited receive payload only carries the first payload words in the IOCB; callers must use the defined offset/first-packet length and purex copy helpers for larger frames rather than assuming the embedded payload is complete.

`QLA_MAX_FC_SEGMENTS` and template segment limits must remain consistent with transport-advertised limits and firmware IOCB/continuation capacity.

## Test Signals
Build and static-layout review should validate `cmd_nvme`, `pt_ls4_request`, and `pt_ls4_rx_unsol` sizes and endian annotations against firmware expectations.

Runtime tests should verify command IOCBs for read/write/no-data/admin async event, LS4 originator and responder IOCBs, reject and terminate control flags, VP/PortID/NPORT routing fields, response and command IU DMA addresses, and continuation DSD behavior.

Unsolicited LS tests should assert correct extraction of opcode, source/destination IDs, exchange address, OX/RX IDs, and first payload handling.
