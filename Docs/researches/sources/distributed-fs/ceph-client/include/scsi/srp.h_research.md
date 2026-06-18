# sources/distributed-fs/ceph-client/include/scsi/srp.h

Purpose: defines the wire-format constants and Information Unit layouts for SCSI RDMA Protocol (SRP), including login, command, task management, response, credit, logout, and asynchronous event messages.

Important APIs and types: opcode enums identify SRP request/response IUs; buffer descriptor enums distinguish direct, indirect, immediate, and absent data descriptors. `struct srp_direct_buf`, `struct srp_indirect_buf`, and `struct srp_imm_buf` describe RDMA and immediate data payloads. `struct srp_login_req`, `struct srp_login_req_rdma`, `struct srp_login_rsp`, `struct srp_login_rej`, `struct srp_cmd`, `struct srp_rsp`, `struct srp_tsk_mgmt`, `struct srp_cred_req`, and AER/logout structs model protocol messages. Packed/aligned annotations preserve T10-specified offsets.

Control flow: SRP initiators build login requests, negotiate IU size and descriptor formats, submit SCSI commands with LUN/CDB and descriptor counts, receive `srp_rsp` completions, and manage credits/AER/logout through corresponding IUs. The header has no executable dispatcher; it is consumed by transport drivers when marshalling DMA-visible protocol buffers.

State and persistence: no state is stored here. Runtime protocol state is held by SRP initiator/target drivers, while these structs define transient wire buffers and endian fields.

Dependencies and integration points: depends on Linux scalar types and `struct scsi_lun`. It integrates SRP transports such as RDMA and virtual I/O SCSI with SCSI midlayer command representation.

Risks and test signals: risks are ABI/wire-layout drift, missing byte-order conversion for `__be*` fields, wrong packed alignment on 64-bit builds, descriptor count/format mismatches, and immediate-data offset mistakes. Test with SRP login negotiation, direct/indirect/immediate I/O, task management, logout, sense data responses, credit handling, and compile-time structure-size assertions where available.
