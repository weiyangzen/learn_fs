# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.h

## Purpose
`network.h` declares the IPWireless network-layer interface used by hardware and tty layers. It names card channel indices, exposes packet/control-line callbacks from hardware, and exposes PPP and tty association helpers.

## Important APIs, Types, And Functions
- Channel constants define `IPW_CHANNEL_RAS`, `IPW_CHANNEL_DIALLER`, `IPW_CHANNEL_CONSOLE`, and `NO_OF_IPW_CHANNELS`.
- Hardware-to-network entry points are `ipwireless_network_packet_received` and `ipwireless_network_notify_control_line_change`.
- Lifecycle functions are `ipwireless_network_create` and `ipwireless_network_free`.
- TTY association functions connect or clear ttys from channel fanout arrays.
- PPP helpers open/close the PPP channel and expose channel index, unit number, and MRU.

## Control Flow And State
The header has no implementation flow. It defines the contract by which hardware delivers channel events to `network.c` and by which `tty.c` opens/closes PPP and queries PPP identifiers. Channel constants drive routing in both network and tty creation.

## State And Persistence Behavior
`struct ipw_network`, `struct ipw_tty`, and `struct ipw_hardware` are opaque. State is owned by implementing modules. Channel IDs are stable firmware protocol identifiers.

## Dependencies And Integration Points
The header depends only on Linux types and local opaque declarations. It integrates hardware receive/control callbacks with tty-visible modem/monitor devices and Linux PPP wrapper APIs.

## Risks And Edge Cases
`NO_OF_IPW_CHANNELS` is 5 although only three named channels appear here; array callers must still honor the full size. Implementations index arrays directly, so callers must pass valid channel indices. PPP metadata helpers return negative values when the channel is offline.

## Test Signals
Build against hardware and tty users. Runtime checks should confirm RAS/dialler routing, no out-of-bounds channel access, and valid PPP metadata only while PPP is online.
