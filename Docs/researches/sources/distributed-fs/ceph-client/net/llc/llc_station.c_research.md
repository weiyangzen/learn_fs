# Research: sources/distributed-fs/ceph-client/net/llc/llc_station.c

## sources/distributed-fs/ceph-client/net/llc/llc_station.c

Purpose: Implements the LLC station component for NULL DSAP XID and TEST commands.

Important APIs/types/functions: Provides `llc_station_init()` and `llc_station_exit()`, which install/remove the station receive handler through `llc_set_station_handler()`. Internal predicates detect NULL DSAP XID/TEST command U-PDUs, and action helpers send XID/TEST responses.

Control flow: `llc_station_rcv()` checks whether the incoming frame is a NULL DSAP XID command or TEST command, sends the corresponding response, then frees the original skb. XID responses are allocated with `struct llc_xid_info` space and use LSAP 0. TEST responses calculate payload size from the 802.2 length field minus the U header, echo data, build a MAC header, and transmit.

State and persistence behavior: The station file itself stores no protocol state; its only persistent effect is registering the global station handler in `llc_input.c`.

Dependencies and integration points: Receives frames from `llc_input.c` when DSAP is zero. Uses frame allocation from `llc_sap.c`, MAC header setup from `llc_output.c`, and PDU helpers from `llc_pdu.c`.

Risks and test signals: Length-derived TEST response sizing and short MAC headers are important validation points. Tests should inject NULL DSAP XID and TEST commands, non-command U frames, non-NULL DSAP frames, malformed short Ethernet frames, allocation failure, and verify generated responses use local device MAC as source and requester MAC as destination.
