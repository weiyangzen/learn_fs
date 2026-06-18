# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/t3_cpl.h

## Purpose

`t3_cpl.h` defines the Chelsio Protocol Language message ABI for T3 firmware, hardware offload, and the Linux driver. It enumerates CPL opcodes and status/error values, defines work request and RSS headers, and declares packed-on-wire structures and bitfield helpers for TCP connection setup/teardown, L2 table operations, route/SMT operations, packet Tx/Rx, iSCSI/DDP/RDMA notifications, and ULP memory I/O. The file is consumed by both NIC data path code and offload support.

## Important APIs, Types, and Structures

- Opcode and status enums: `enum CPL_opcode`, `enum CPL_error`, ULP modes, connection policies, abort modes, LSO Ethernet types, congestion algorithms, and RSS hash types define the protocol vocabulary.
- Common headers: `union opcode_tid`, `struct rss_header`, and `struct work_request_hdr` encode opcode/TID, RSS steering metadata, and SGE work request metadata. Macros such as `MK_OPCODE_TID()`, `GET_TID()`, `V_WR_OP()`, `V_WR_LEN()`, `V_WR_TID()`, and `F_WR_SOP/F_WR_EOP` are used heavily by Tx paths.
- Connection messages: `cpl_pass_open_req/rpl`, `cpl_pass_accept_req/rpl`, `cpl_act_open_req/rpl`, `cpl_pass_establish`, `cpl_act_establish`, close and abort messages, and TCB get/set messages model TCP offload connection lifecycle.
- Packet data messages: `struct cpl_tx_pkt`, `struct cpl_tx_pkt_lso`, `struct cpl_rx_pkt`, `struct cpl_trace_pkt`, `struct cpl_tx_data`, `struct tx_data_wr`, and `struct cpl_rx_data`/`struct cpl_rx_data_ack` are used for NIC and offload packet movement.
- Table-management messages: L2T, SMT, and route read/write/delete request/reply structures support firmware-managed lookup tables.
- Upper-layer messages: iSCSI header, DDP completion/data, RDMA terminate/read/status, and `struct ulp_mem_io` support offload clients beyond the basic netdev path.

## Control Flow and Usage

There is no runtime control flow in this header. Runtime code constructs these structures in DMA-visible descriptors or interprets them from response descriptors. In `sge.c`, `write_tx_pkt_wr()` writes `cpl_tx_pkt` or `cpl_tx_pkt_lso` headers for Ethernet traffic, `rx_eth()` interprets `cpl_rx_pkt` before delivering skbs to the network stack, and offload transmit paths preserve prebuilt work-request/CPL headers supplied by offload clients. Offload modules use connection, TCB, L2T, route, and ULP structures to ask firmware/hardware to create, update, or tear down state.

## State and Persistence Behavior

The structures represent transient command and completion messages, but many fields refer to persistent hardware/firmware state: TIDs, L2T indexes, SMT entries, route entries, TCB words, RSS queues, offload receive credits, DDP tags, page pods, and ULP memory addresses. The header defines how that state is addressed and modified. Endianness annotations (`__be16`, `__be32`, `__be64`) and conditional bitfields for little vs big endian are essential because these layouts cross the CPU/hardware boundary.

## Dependencies and Integration Points

`t3_cpl.h` is included by `sge.c` and offload code that constructs CPL work requests. It depends on kernel byteorder definitions and is conditionally shaped by `CHELSIO_FW`, allowing a different view when compiled for firmware. It integrates with firmware opcode definitions, SGE work request rings, TP/TCP offload state, L2 table management, iSCSI/RDMA/DDP upper-layer drivers, and Linux skb metadata translation.

## Risks and Edge Cases

- Structure layout and endian bitfield order are hardware ABI. Padding, field reordering, or native-endian misuse can corrupt firmware commands or misread completions.
- Many macros share generic names and similar field names across option words; using an option-0 field on option-1/2 data can silently create invalid requests.
- Some definitions are excluded or altered under `CHELSIO_FW`; host and firmware builds must agree on the wire format for shared portions.
- `GET_TID()` and opcode/TID packing assume 24-bit TIDs; callers must avoid over-wide identifiers.
- Immediate packet sizes and work-request lengths in `sge.c` depend on these structures staying the expected size.

## Test Signals

Validation signals include successful offload connection setup/teardown, correct TID extraction, Ethernet Tx/Rx with VLAN/checksum/LSO fields, route/L2T/SMT commands receiving matching replies, iSCSI/DDP/RDMA completions decoded correctly, and sparse/build checks for endian annotations. Packet capture or firmware trace comparison is useful for confirming exact on-wire CPL encoding.
