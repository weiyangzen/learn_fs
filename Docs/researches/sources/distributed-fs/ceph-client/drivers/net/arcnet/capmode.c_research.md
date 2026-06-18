# sources/distributed-fs/ceph-client/drivers/net/arcnet/capmode.c

Purpose: ARCNET CAP mode encapsulation module. CAP mode adds a four-byte userspace cookie after the protocol byte and reports transmit acknowledgement status back to userspace as a received protocol-0 packet.

Important APIs and functions: `rx()` builds an skb with space for the inserted cookie and copies card data around that extra integer. `build_header()` fills the hardware header and logs the cookie. `prepare_tx()` subtracts the ARC header and cookie from the length, writes the ARC header and protocol byte, skips the cookie while copying the message body to the card, and records `lastload_dest`. `ack_tx()` creates an acknowledgement skb, copies the original header/cookie, sets CAP protocol to 0, writes the hardware ack result, feeds it through `netif_rx()`, frees the outgoing skb, and clears `lp->outgoing.proto`. `capmode_proto` provides callbacks and `XMTU`.

Control flow: module init assigns CAP mode to protocol IDs 1 through 8 if still default, potentially makes it broadcast/default/raw protocol, and exit unregisters it through the core. During transmit, ARCNET core calls `ack_tx()` after hardware completion because `capmode_proto` advertises an ack callback.

State and dependencies: persistent state is protocol-map registration and `lp->outgoing` ownership until ack completion. Dependencies are `arcdevice.h`, netdevice receive, and ARCNET core transmit completion. Risks include skb layout assumptions around the inserted cookie, double ack paths if core error-report work and CAP ack both observe the outgoing skb, and protocol-map takeover for raw/default behavior. Test signals include ack statuses 0/1/2, cookie round trip, protocol IDs 1-8, short/extended packet offsets, and unload restoration.
