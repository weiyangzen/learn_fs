# sources/distributed-fs/openafs/src/rx/IRIX/rx_knet.c

Purpose: IRIX Rx kernel network integration for listener and UDP-intercept modes plus interface discovery.

Important APIs/types/functions: listener `osi_NetReceive`; non-listener `rxk_input`, `rxk_fasttimo`, `rxk_init`; interface helpers `rxi_FindIfnet`, `rxi_GetIFInfo`, `rxi_MatchIfnet`, `rxi_EnumGetIfInfo`; `osi_NetSend`.

Control flow: listener receive calls IRIX `soreceive` through behavior descriptors and clears signals/socket errors on interrupt. Non-listener mode hooks UDP protocol input/timer, validates UDP packets for registered Rx ports, handles checksum including `M_CKSUMMED`, converts mbufs to Rx packets, and falls through to parent UDP otherwise. Interface helpers enumerate `hashinfo_inaddr` to cache addresses/MTUs and update Rx max receive sizes.

State/persistence: socket error counters, `parent_proto`, local address/MTU arrays, `numMyNetAddrs`, `rx_maxReceiveSize`, and jumbo receive sizing.

Dependencies/integration: IRIX sockets, mbufs, behavior descriptors, hash-based interface tables, Rx packet/rxevent internals.

Risks: old-style prototypes and platform-specific signal clearing are brittle; interface cache can be stale; non-listener protocol hooking is invasive; send path trusts vector count. Test signals include listener interrupt recovery, interface MTU discovery, UDP pass-through, checksum handling, and Rx send/receive.
