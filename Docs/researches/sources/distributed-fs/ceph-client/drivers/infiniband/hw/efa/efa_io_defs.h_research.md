# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_io_defs.h

Defines EFA IO queue wire formats for send, receive, RDMA read/write, fast memory registration/invalidation, and completions. These layouts are hardware-visible and shared with userspace queue handling.

Important definitions include queue type, send opcode, completion status, and fast-registration PBL-mode enums; TX metadata and buffer descriptors; remote memory and RDMA request descriptors; fast MR register/invalidate descriptors; RX descriptors; base and extended completion descriptors; and masks for op type, phase, immediate data, inline data, LKey, first/last, queue type, and unsolicited receive flags.

The header has no executable control flow. It controls how userspace and hardware compose WQEs/CQEs and how `efa_verbs.c` validates CQ entry sizes for base and extended RX completions. Queue phase bits, request IDs, qtype fields, status codes, immediate data, and descriptor indexes form persistent queue protocol state while a QP/CQ exists.

Dependencies are project bit macros and consumers in EFA verbs/userspace ABI code. Risks are layout drift, incorrect union interpretation, and status/opcode mismatches with userspace completion parsing. Test signals include CQ creation with both entry sizes, send/recv completions, immediate data, RDMA read/write statuses, unsolicited write receive behavior, and fast MR operations.
