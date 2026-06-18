# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_common.h

## Purpose
Defines the host/firmware ABI shared across LiquidIO PF, VF, queue, network, console, and representor code. It contains protocol opcodes, command bit layouts, instruction and receive headers, link descriptors, interface configuration payloads, statistics layouts, capabilities, and VF representor request/response formats.

## Important APIs, Types, and Functions
Important constants include base driver version fields, `OPCODE_CORE`, `OPCODE_NIC`, `OPCODE_SUBCODE`, NIC subcodes such as `OPCODE_NIC_NW_DATA`, `OPCODE_NIC_CMD`, `OPCODE_NIC_IF_CFG`, `OPCODE_NIC_VF_REP_PKT`, and `OPCODE_NIC_VF_REP_CMD`, app modes, firmware capability flags, and NIC command IDs for MTU, MAC, RX control, multicast, LRO, checksum, VLAN, VXLAN, queue count, spoof check, and VF link state. Core types include `lio_version`, `octeon_sg_entry`, `union octnet_cmd`, `octeon_instr_ih3`, `octeon_instr_pki_ih3`, `octeon_instr_ih2`, `octeon_instr_irh`, `octeon_instr_rdp`, `union octeon_rh`, `union octnic_packet_params`, `union oct_link_status`, `oct_link_info`, `liquidio_if_cfg_info`, `nic_rx_stats`, `nic_tx_stats`, `oct_link_stats`, `oct_intrmod_cfg`, `union oct_nic_if_cfg`, and the VF-rep structures.

## Control Flow
The header has no standalone execution. It controls runtime branching through bitfields and helpers such as `incr_index`, `add_sg_size`, and `opcode_slow_path`. Queue code uses `opcode_slow_path` to decide whether a received packet is normal NIC data or should be dispatched to a registered opcode handler.

## State and Persistence Behavior
Most structs are serialized across PCI queues or firmware shared messages, so field widths, endian annotations, and bit ordering are persistent ABI. `oct_link_info` carries queue assignments, MAC, GMX port, link status, and spoof/admin flags. Stats structs are firmware snapshots. VF-rep request and response structs persist representor state changes, MTU, stats, and netdev names through firmware.

## Dependencies and Integration Points
Includes `octeon_config.h` and is included by most LiquidIO C files. It integrates Linux networking concepts with firmware protocol fields: checksum features, VLAN tags, hardware timestamps, LRO, VXLAN ports, link settings, and representor operations.

## Risks
This file is ABI-sensitive. Incorrect bitfield order, endian conversion, opcode values, struct sizes, or command constants can break host/firmware communication while compiling cleanly. Some fields are embedded in SKB control blocks or DMA command descriptors, so alignment and size changes have wide impact. `opcode_slow_path` depends on exact opcode/subcode composition.

## Test Signals
Compile on little- and big-endian bitfield configurations, firmware IF_CFG negotiation, NIC command round trips, RX/TX data paths, dispatch of non-data opcodes, link update parsing, stats fetches, VF-rep commands, timestamp packets, checksum/VLAN/VXLAN offload commands, and static checks for ABI struct sizes.
