# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_reg.h

## Purpose
This header defines the XRS700x register map and bit fields used by the common DSA driver and transport bindings. It is a hardware contract rather than executable logic.

## Important APIs, Types, and Functions
- Base regions cover device ID, GPIO, per-port blocks, RTC, timestampers, and switch configuration.
- Port macros cover state, speed, VLAN, forwarding masks, HSR/PRP, PTP delay, counters, and inbound policy entries.
- Counter macros enumerate RX/TX low/high halves for byte, packet, size, HSR/PRP, duplicate, and drop counters.
- RTC/timestamp macros expose current time, adjustment, command, and per-frame timestamp records.
- Switch macros cover global control, interrupt status/mask, MAC table, timestamp tables, and VLAN entries.

## Control Flow
There is no runtime flow. Callers compose addresses with the macros, for example `XRS_PORT_BASE(x)` for per-port blocks and `XRS_VLAN(v)` for 2-byte VLAN table entries.

## State and Persistence
The header describes persistent hardware state: port configuration, counters, RTC/PTP state, MAC table, switch reset/configuration, and VLAN table. Rollover and consistency of paired counter registers must be handled by callers.

## Dependencies and Integration Points
It relies on kernel bit helpers such as `BIT()`. It is included by the XRS700x MDIO transport and common switch implementation, and coordinates with Linux VLAN limits through `XRS_VLAN(VLAN_N_VID - 1)`.

## Risks and Edge Cases
The hardware uses 16-bit registers with 2-byte alignment, so offset mistakes can address the wrong register. Counter macros are centered on `XRS_PORT_CNT_BASE(0)`, requiring careful caller interpretation. HSR/PRP and PTP fields are dense and datasheet-sensitive.

## Test Signals
Compile coverage, successful device ID reads, expected port state changes, VLAN programming, monotonic counters, timestamp reads, and reset/global bit behavior.
