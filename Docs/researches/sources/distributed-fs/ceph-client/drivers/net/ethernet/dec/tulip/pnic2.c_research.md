<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic2.c

Purpose: Implements PNIC-II autonegotiation, link-change handling, and timer support for Lite-On PNIC-II chips, whose CSR6/CSR12/CSR14 semantics differ from classic 21142/21143 Tulip parts.

Important APIs and functions: `pnic2_timer()` logs negotiation state and reschedules a long media tick. `pnic2_start_nway()` encodes `tp->sym_advertise` into CSR14 advertisement bits, puts CSR6 into NWAY mode, marks `tp->nway`/`tp->mediasense`, clears `tp->lpar`, and writes CSR12 bits 14:12 to start autonegotiation. `pnic2_lnk_change()` processes negotiation completion, maps negotiated partner abilities to `dev->if_port`, sets `tp->full_duplex`, programs CSR14/CSR6, restarts RX/TX, and restarts NWAY on link loss.

Control flow: `tulip_core.c` initializes PNIC2 with all 10/100 half/full capabilities, enables autonegotiation interrupts, calls `pnic2_start_nway()`, and installs `pnic2_lnk_change()`. Interrupt paths call the link-change hook with CSR5. Link failure branches delete and re-add the media timer around renegotiation.

State and persistence: Maintains negotiation state in `tp->sym_advertise`, `tp->lpar`, `tp->nway`, `tp->nwayset`, `tp->mediasense`, `tp->full_duplex`, `tp->csr6`, `dev->if_port`, and the timer. No persistent storage beyond hardware registers.

Dependencies and integration: Depends on `tulip.h` CSR constants, `medianame[]`, `tulip_start_rxtx()`, and `tulip_restart_rxtx()`. It plugs into the Tulip core chip table and shared interrupt link-change dispatch.

Risks: The implementation is based on sparse datasheet knowledge and uses magic masks `0xfe3bd1fd` and `0xfff0ee39`. Incorrect masking can corrupt unrelated CSR bits. Timer deletion from link-change context must avoid timer races. Failure fallback always chooses 10baseT half-duplex when negotiation is inconclusive.

Test signals: Cover successful negotiation for 100FD, 100HD, 10FD, and 10HD, autonegotiation failure fallback, link loss at 100 and 10 Mbps, medialock preventing renegotiation, CSR14 bit 7 clearing after NWAY, and timer rescheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic2.c -->
