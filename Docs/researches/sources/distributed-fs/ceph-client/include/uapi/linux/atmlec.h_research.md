<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmlec.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmlec.h

## Purpose
Defines the ATM LAN Emulation Client daemon interface for LANE control/data/multicast sockets and messages.

## Important APIs, Types, And Functions
Ioctls `ATMLEC_CTRL`, `ATMLEC_DATA`, and `ATMLEC_MCAST` register socket roles. `atmlec_msg_type` enumerates MAC/ATM mapping, topology, flush, ARP, config, LEC id, and bridge decisions. `atmlec_config_msg`, `atmlec_msg`, and `atmlec_ioc` carry LANE parameters and addresses.

## Control Flow
The LEC daemon registers control/data sockets, exchanges `atmlec_msg` records with the kernel to resolve MAC-to-ATM mappings, react to topology/flush events, and configure LANE parameters. Data and multicast VCCs are attached through `atmlec_ioc`.

## State And Persistence
State includes LEC interfaces, ATM/MAC cache entries, LANE config, LEC id, proxy state, TLV data, and attached VCCs. It is runtime networking state.

## Dependencies And Integration Points
Depends on ATM core/API, Ethernet address definitions, and ATM ioctl ranges. Integrates with LANE daemons such as zeppelin and ATM network interfaces.

## Risks And Edge Cases
Fixed max LEC interfaces, variable TLVs after messages, LANE1/2 differences, cache flush ordering, and proxy mapping correctness are risks.

## Test Signals
Daemon registration, config message exchange, MAC/ATM mapping updates/deletes, topology change/flush handling, multicast/data VCC setup, and TLV length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmlec.h -->
