
# sources/distributed-fs/ceph-client/include/linux/nvme-tcp.h

Purpose: defines NVMe/TCP PDU wire formats, protocol constants, digest/TLS options, fatal error codes, and a union over all supported PDU layouts.

Important APIs/types/functions: constants include discovery port 8009, admin capsule size, digest length, and termination PDU size limits. Enums define protocol format version, TLS cipher IDs, fatal error status values, digest option bits, PDU types, and PDU flags. `struct nvme_tcp_hdr` is the common PDU header. Specific structures model ICReq, ICResp, termination, command capsule, response capsule, R2T, and data PDUs; `union nvme_tcp_pdu` overlays them.

Control flow: a TCP queue starts with ICReq/ICResp negotiation of version, alignment, digests, and R2T/data limits. Command PDUs carry NVMe commands, responses carry completions, R2T PDUs authorize host-to-controller data, data PDUs transfer payload, and termination PDUs report fatal protocol errors.

State and persistence: no state is stored by the header. The structures describe transient socket payloads; connection state lives in the NVMe/TCP host/target implementations.

Dependencies and integration points: depends on `linux/nvme.h` for command/completion structures and size macros. It integrates NVMe fabrics core, TCP transport parsing, optional header/data digests, and TLS cipher negotiation.

Risks and test signals: risks include PDU length/data-offset validation bugs, digest flag mismatch, duplicate fatal error code values, alignment negotiation mistakes, R2T/data limit enforcement, and TLS cipher mapping errors. Test signals include NVMe/TCP connect tests with/without digests and TLS, malformed PDU fuzzing, R2T boundary tests, termination PDU validation, and interop with target stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-tcp.h -->
