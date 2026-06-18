# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_ppp.c

## Purpose
`hdlc_ppp.c` implements PPP over generic HDLC, including HDLC-style PPP framing, LCP/IPCP/IPv6CP control protocol state machines, echo keepalives, and protocol demux for IP and IPv6 payloads.

## Important APIs, Types, And Functions
`struct hdlc_header` and `struct cp_header` describe PPP-over-HDLC and PPP control packets. `struct proto` stores one CP instance with timer, PID, state, last request ID, and retry counter. `struct ppp` stores the three CP instances, shared lock, last echo reply time, retry/timeout settings, and sequence numbers. `ppp_cp_event()` is the main state-machine executor using `cp_table`. Other important functions are `ppp_hard_header()`, `ppp_tx_cp()`, `ppp_cp_parse_cr()`, `ppp_rx()`, `ppp_timer()`, `ppp_start()`, `ppp_stop()`, and `ppp_ioctl()`.

## Control Flow
Attaching PPP through `ppp_ioctl()` requires CAP_NET_ADMIN, a down device, and successful hardware attach with NRZ/CRC16. The module allocates `struct ppp`, initializes defaults, installs PPP header ops, sets `ARPHRD_PPP`, and marks the device dormant. On start, all CP structs are initialized and LCP receives a START event. LCP opening clears dormancy, starts IPCP and IPv6CP, records `last_pong`, and schedules echo keepalives. Incoming control packets are parsed under `ppp->lock`; Configure-Request options are ACKed, NAKed, or rejected, ACK/NAK/Terminate/Code-Reject events drive `cp_table`, and unsupported protocols are rejected when LCP is open. Timers retransmit configure/terminate requests, restart after carrier loss, or send LCP echo requests.

## State And Persistence
State is per attached HDLC device plus one module-global `tx_queue`, used to defer `dev_queue_xmit()` until after releasing the PPP spinlock. There is no durable persistence. Timers are deleted when protocols reach CLOSED, and `ppp_close()` flushes pending control packets.

## Dependencies And Integration Points
The file integrates with generic HDLC attach/xmit, header ops, `netif_dormant_on/off()`, timer APIs, skb queues, and standard PPP protocol identifiers. IP and IPv6 payloads are exposed to the kernel stack through `ppp_type_trans()` after stripping the four-byte HDLC PPP header.

## Risks
The module-global `tx_queue` is shared by all PPP HDLC devices and relies on flushing discipline after lock release; concurrency assumptions should not be relaxed casually. Control parsing uses direct casts after length checks; option parsing must preserve the existing bounds checks. `ppp_tx_cp()` uses a static zero-initialized `magic` value for echo/control magic, so it is not a robust loop-detection mechanism. All configurable retry/keepalive values are hard-coded; behavior changes require protocol-level testing.

## Test Signals
Signals include successful PPP attach, LCP open/dormant-off, IPCP/IPv6CP start after LCP, handling of Configure-Ack/Nak/Rej, Echo-Reply updating `last_pong`, timeout-triggered LCP restart, IP/IPv6 payload demux, and module unload with timers inactive. Fuzzing CP frames should focus on short packets, malformed option lengths, and unknown protocol rejection.
