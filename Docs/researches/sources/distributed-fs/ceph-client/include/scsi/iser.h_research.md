# sources/distributed-fs/ceph-client/include/scsi/iser.h

Purpose: Defines iSER connection-manager and control PDU headers used to carry iSCSI over RDMA capabilities and RDMA steering keys.

Important APIs/types/functions: Capability flags describe ZBVA and Send-with-Invalidate support or use. Opcodes identify iSCSI control, iSER hello, and hello reply messages. `struct iser_cm_hdr` carries negotiation flags. `struct iser_ctrl` carries opcode/read-write-valid flags, write/read STags, and virtual addresses.

Control flow and state: During connection setup peers exchange CM headers to negotiate optional behavior. For iSCSI control PDUs, `iser_ctrl` indicates whether write/read RDMA buffers are valid and supplies remote keys and virtual addresses.

Dependencies and integration: Used by iSER initiator/target RDMA transports alongside iSCSI protocol headers and RDMA memory registration.

Risks and test signals: Risks include packed layout mismatch, wrong flag polarity between supported and used bits, endian errors for STags/VAs, and invalid key lifetime. Tests should cover CM negotiation, control PDU encode/decode, read/write steering combinations, and invalidation behavior.
