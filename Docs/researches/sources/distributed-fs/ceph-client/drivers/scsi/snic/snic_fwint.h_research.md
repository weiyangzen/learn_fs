# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_fwint.h

Purpose: this header defines the SNIC host-to-firmware and firmware-to-host wire protocol. It contains request/response opcodes, status codes, common headers, payload structures, color-bit helpers, and sizing constants.

Important APIs, types, and functions: `enum snic_io_type` defines request, completion, ACK, and async event message types. `enum snic_io_status` maps firmware completion statuses to driver behavior. `struct snic_io_hdr` is the common message header encoded/decoded by `snic_io_hdr_enc()` and `snic_io_hdr_dec()`. Payloads include exchange-version, report-targets, initiator command, task management, HBA reset, notify, and async event structures. `struct snic_host_req` is the 128-byte host request format, and `struct snic_fw_req` is the 64-byte firmware completion format. `snic_color_enc()` and `snic_color_dec()` manage completion color.

Control flow: control, discovery, SCSI I/O, task-management, reset, and CQ service paths all fill or parse these structures. Host requests are DMA-mapped and posted to the vNIC WQ. Firmware completions are consumed from the firmware CQ, decoded by type/status, and dispatched by `snic_io_cmpl_handler()`.

State and persistence: no software state is persisted here, but the structures define in-memory DMA ABI shared with firmware. Fields such as host id, command id, initiator context, SG counts, target/lun ids, sense address, and async event ids are runtime protocol state.

Dependencies and integration: used by nearly every SNIC implementation file, especially `snic_ctl.c`, `snic_disc.c`, `snic_res.h`, `snic_scsi.c`, and `vnic_cq_fw.h`. It assumes kernel endian types and memory barriers are available.

Risks: ABI drift is high risk because most structures have fixed expected sizes but `VERIFY_REQ_SZ` and `VERIFY_CMPL_SZ` are empty macros in this snapshot. `ulong init_ctx` is embedded in DMA-visible protocol and assumes host/firmware compatibility for pointer-width context. Color bit placement in the last byte is protocol-critical.

Test signals: firmware interoperability tests should cover every request/completion type, each status mapping, 32-bit and 64-bit build assumptions where relevant, CQ color wrap, endian correctness, and structure size/layout validation.
