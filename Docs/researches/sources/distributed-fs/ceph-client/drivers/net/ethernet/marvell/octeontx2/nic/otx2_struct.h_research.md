# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_struct.h

## Purpose
`otx2_struct.h` defines the low-level NIX completion queue entry, send queue entry, receive parser, scatter/gather, and error/status layouts used by the OcteonTX2/CN10K RVU Ethernet data path. It is the bitfield contract between the driver and NIX hardware, consumed by TX/RX, XDP, QoS, timestamp, and offload paths.

## Important APIs, Types, and Functions
The file exports enums for CQE/SQE sizes, SQE subdescriptor kinds, load types, checksum L3/L4 encoding, CQE types, send memory algorithms, CQ/RQ/SQ interrupt bits, SQ operation errors, MNQ errors, and send completion statuses. Important structures include `nix_cqe_hdr_s`, `nix_rx_parse_s`, `nix_rx_sg_s`, `nix_send_comp_s`, `nix_cqe_rx_s`, `nix_cqe_tx_s`, `nix_sqe_hdr_s`, `nix_sqe_ext_s`, `nix_sqe_sg_s`, and `nix_sqe_mem_s`.

## Control Flow
There is no executable flow in this header. Runtime flow is imposed by descriptor ordering: RX CQEs contain a header, parser result, and SG descriptors; TX SQEs are built as a send header followed by optional extended, SG, and memory subdescriptors. `otx2_txrx.c` reads CQE types/status and writes SQE subdescriptor fields according to these layouts.

## State and Persistence
All state represented here is hardware ring state or mailbox-programmed descriptor interpretation. Bitfield values persist only while CQEs/SQEs reside in DMA-backed queue memory. Error/status enums feed interrupt handling and cleanup decisions.

## Dependencies and Integration Points
The header depends on Linux fixed-width integer types through included driver headers. It integrates with `otx2_txrx.c`, `otx2_xsk.c`, `qos_sq.c`, CN10K IPsec/LSO helpers, and hardware register/mailbox definitions in `otx2_reg.h` and `otx2_common.h`.

## Risks and Edge Cases
Bitfield layout correctness is critical and architecture-sensitive; endian assumptions and descriptor size mismatches can corrupt packet parsing or transmission. Several fields are reused for timestamp, VLAN insertion, shaping, and checksum offload, so changes need hardware documentation coverage. Error enums must stay synchronized with firmware/AF behavior.

## Test Signals
Useful signals include RX/TX traffic with checksum, VLAN, TSO, XDP, AF_XDP, PTP timestamp, and QoS enabled; CQ/SQ interrupt error injection; sparse/packed struct layout build checks; and hardware trace dumps validating parser words and completion status decoding.
