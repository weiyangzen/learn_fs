# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/q_struct.h

## Purpose
`q_struct.h` is the hardware descriptor and queue-register layout contract for ThunderX NIC queues. It describes completion queue entries, receive buffer descriptors, send subdescriptors, RSS/CPI protocol classifications, error codes, and packed queue configuration bitfields with separate little- and big-endian definitions.

## Important APIs, Types, and Constants
Important enums include send load types, Ethernet parsing algorithms, L3/L4 type identifiers, CPI and RSS algorithms, RSS hash controls, CQE types, RX TCP status/end reasons, RX error levels/opcodes, send checksum modes, send CRC/memory operations, and SQ subdescriptor types. Major structures are `cqe_rx_t`, `cqe_rx_tcp_err_t`, `cqe_rx_tcp_t`, `cqe_send_t`, `union cq_desc_t`, `rbdr_entry_t`, `rbe_tcp_cnxt_t`, `rx_hdr_t`, `sq_crc_subdesc`, `sq_gather_subdesc`, `sq_imm_subdesc`, `sq_mem_subdesc`, `sq_hdr_subdesc`, `rq_cfg`, `cq_cfg`, `sq_cfg`, `rbdr_cfg`, and `qs_cfg`.

## Control Flow and Integration
There is no executable logic. `nicvf_queues.c` writes SQ header/gather/immediate descriptors, reads CQE RX/send fields, and casts config structs to 64-bit register values when programming RQ/CQ/SQ/RBDR/QS registers. `nicvf_main.c` interprets RX CQE fields for hash, VLAN, checksum, timestamp, queue selection, and XDP constraints. Because the definitions mirror hardware words, field order and endian guards are core integration points.

## State and Persistence
The structures represent transient DMA-visible state shared with the NIC. CQEs are written by hardware and consumed by NAPI. SQ descriptors are written by the driver and consumed by hardware. RBDR entries hold buffer DMA addresses. Queue config structs are short-lived stack objects used to produce register values. No persistent storage is involved.

## Dependencies and Risks
This header depends on architecture byteorder macros and the hardware programming manual. The largest risk is ABI drift: bitfield ordering, width, or enum value changes can corrupt DMA descriptors or registers. Another risk is that C bitfield layout is compiler- and endian-sensitive, so build coverage on supported architectures matters. Consumers also perform raw pointer arithmetic into `cqe_rx_t`, which makes word offsets sensitive to this layout.

## Test Signals
Signals include compile tests for both endian bitfield modes, hardware RX/TX smoke tests, validation of RSS/VLAN/checksum/offload fields in CQEs, TX descriptor inspection with TSO and timestamping, queue register programming tests, and regression tests for pass1 versus later silicon CQE pointer offsets.
