# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_mac.h

## Purpose
Defines the MSCC line-MAC register map, status/statistics offsets, packet formatting controls, pause controls, loopback bits, and related 1588 top protocol-mode field.

## Important APIs, Types, And Constants
Register offsets cover MAC enable/mode/max length/tags/advanced checks/LFS/loopback/packet info, pause TX/RX controls, sticky status, 32-bit frame counters, and 40-bit byte counters. Bitfield macros configure RX/TX clocks, software resets, MAC enablement, preamble/IPG behavior, FCS/preamble insertion and stripping, padding, LPI/LF/RF relay, pause behavior, VLAN tag matching, loopback, and 1588 protocol mode.

## Control Flow
No executable control flow. It is consumed by MSCC implementation files that perform CSR or paged register writes.

## State And Persistence
No software state. Hardware state controls line-MAC datapath behavior and exposes sticky/error/statistics counters.

## Dependencies And Integration Points
Depends on Linux `BIT()`/`GENMASK()` availability through consumers. Integrates with MSCC MACsec, PTP, and core PHY code configuring the embedded line MAC.

## Risks
Callers must use the correct access width and CSR target. Paired 40-bit counters need careful read ordering. Packet formatting options interact with MACsec and PTP timestamping, especially FCS, preamble, padding, and PTP stall clock fields.

## Test Signals
Compile consumers, validate MAC enable/reset sequencing, check counters under traffic, test pause and loopback modes, and verify PTP/MACsec packet formatting.
