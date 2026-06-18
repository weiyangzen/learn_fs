# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_regs.h

## Purpose
`airoha_regs.h` is the Airoha Ethernet hardware register map. It defines FE, PSE, CDM, GDM, PPE, QDMA, QoS, trTCM, descriptor, and interrupt register offsets plus bit masks used by the Airoha Ethernet/PPE datapath.

## Important APIs, types, and constants
- Base-address macros (`PSE_BASE`, `CDM*_BASE`, `GDM*_BASE`, `PPE*_BASE`) and selector macros (`CDM_BASE()`, `GDM_BASE()`) encode per-block register layout.
- FE/GDM/PSE macros configure forwarding, ingress, length, loopback, VIP ports, WAN ports, multicast VLAN tables, PSE buffer reservations, and GDM MIB counters.
- PPE macros define global enable, flow configuration, protocol checks, table base/sizing, bind rates/limits, aging, hash seed, default CPU ports, MTU, SRAM RAM access, and update-memory registers.
- QDMA macros define global DMA enable/reset, interrupt status/enable banks, TX/RX ring registers, IRQ rings, descriptor count/low-threshold controls, QoS/trTCM registers, and congestion settings.
- `struct airoha_qdma_desc` and `struct airoha_qdma_fwd_desc` define the on-memory hardware descriptor layouts and message/control fields.

## Control flow and integration
The header has no runtime control flow. Driver code uses these macros with `airoha_fe_rr/wr/rmw()` and `airoha_qdma_rr/wr/rmw()` to initialize hardware, set up queues, enable interrupts, program PPE tables, collect stats, and fill/parse QDMA descriptors.

## State and persistence behavior
All named state is hardware register or DMA descriptor state. Register state is volatile and reset by device reset/power-management paths. Descriptor structs represent DMA-visible memory shared between CPU and QDMA hardware.

## Dependencies and integration points
The header depends only on Linux types and common bit macros. It is included by Airoha implementation files, especially `airoha_ppe.c`, and must remain consistent with hardware documentation and the descriptor layouts declared in `airoha_eth.h`.

## Risks and edge cases
Register macros are hardware ABI. Incorrect offsets, masks, or shift assumptions can break traffic, offload, interrupts, or stats with little compile-time signal. Some macros encode split register spaces for low/high RX/TX rings and interrupt banks; off-by-one errors can target the wrong register block. Descriptor fields mix CPU and little-endian storage, so callers must preserve correct conversions.

## Test signals
Compile all Airoha users, boot on supported SoCs, validate DMA reset/enable, RX/TX rings, interrupt masking/unmasking, QDMA descriptor ownership, GDM MIB counters, PPE table programming, SRAM read/write polling, and QoS/trTCM programming under real traffic.
