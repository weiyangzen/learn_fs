# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh_internal.h

## Purpose
This internal register-map header defines ATL2/A2 register addresses, masks, shifts, widths, defaults, and address-calculation macros used by the low-level hardware helpers.

## Important APIs, types, and functions
Important macro groups include RPF redirection and RSS hash controls, new RPF enable, L2 unicast/broadcast request tags, RSS redirection table addressing, VLAN request tags, RX/TX queue-to-TC map addressing, TX buffer and scheduler controls, TX interrupt moderation register addresses, launch-time control, FPGA version encoding, action resolver request tag/mask/action addresses, resolver section enable, firmware shared input/output buffer addresses, host/MCP shared-buffer handshake registers, MCP boot register, and host request interrupt set/clear addresses.

## Control flow
No functions execute here, but address macros are used to generate the control flow in `hw_atl2_llh.c`. Queue and TC address macros choose register blocks and bit shifts based on indices, so loop bounds in higher-level code must match their supported ranges.

## State and persistence
The header defines hardware state layout only. Values written through these definitions persist in NIC registers, resolver SRAM, firmware shared buffers, or interrupt status registers.

## Dependencies and integration points
This file is included by `hw_atl2_llh.c` and indirectly underpins ATL2 filtering, QoS, firmware, and boot flows. It intentionally remains internal so policy code uses named helper functions rather than raw offsets.

## Risks
Register-map headers are high blast-radius: a wrong address, mask, or shift can break traffic steering, firmware communication, or boot handling. Several address macros return zero for out-of-range queues; callers that pass invalid indices may write address zero. Naming/comments show generated-register style and should be kept in sync with hardware documentation.

## Test signals
Hardware bring-up, RSS distribution, VLAN filter hits, ART behavior, firmware boot/handshake, and interrupt moderation are practical runtime signals. Static tests can compare macro names and masks against vendor register specifications.
