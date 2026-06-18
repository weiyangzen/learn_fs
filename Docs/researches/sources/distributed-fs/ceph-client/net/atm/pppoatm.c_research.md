# sources/distributed-fs/ceph-client/net/atm/pppoatm.c

## Purpose
`pppoatm.c` implements RFC 2364 PPP over ATM/AAL5. It binds an already connected ATM VCC to the generic PPP channel layer, installs ATM push/pop/release callbacks, encapsulates outbound PPP frames as VC-mux or LLC, and decapsulates inbound AAL5 PDUs back into PPP.

## Important APIs, Types, and Functions
- `struct pppoatm_vcc`: per-bound-VCC state containing the original ATM callbacks, encapsulation mode, PPP channel, inflight accounting, blocked bit, compression flags, and wakeup tasklet.
- `pppoatm_assign_vcc`: validates `struct atm_backend_ppp`, allocates state, registers a PPP channel, hooks the ATM VCC callbacks, takes module ownership, and replays queued receives with `vcc_process_recv_queue`.
- `pppoatm_push`: inbound ATM callback; handles VCC close notification, LLC/autodetect parsing, `atm_return`, `ppp_input`, and `ppp_input_error`.
- `pppoatm_send`: PPP `start_xmit`; applies protocol-field compression, adds LLC when needed, enforces ATM/socket readiness, accounts TX, and calls the ATM device send method.
- `pppoatm_may_send`, `pppoatm_pop`, and `pppoatm_release_cb`: flow-control loop that limits the queue to two packets and schedules `ppp_output_wakeup` from a tasklet.
- `pppoatm_ioctl`: ATM backend ioctl handler registered through `register_atm_ioctl`.

## Control Flow
Userspace issues `ATM_SETBACKEND` with `ATM_BACKEND_PPP`; `ioctl.c` may autoload the module, then the registered handler checks `CAP_NET_ADMIN`, connected socket state, and encapsulation options. On success, PPP owns the send path while ATM still owns device delivery. Outbound packets enter through the PPP channel, are optionally compressed/encapsulated, and are sent only when `atm_may_send` and the `inflight` counter permit. Completion calls the hooked ATM `pop` callback, decrements `inflight`, and wakes PPP if it was blocked. Inbound AAL5 packets enter `pppoatm_push`, are decoded by selected/autodetected encapsulation, and are delivered to `ppp_input`.

## State and Persistence
State persists in `atm_vcc->user_back`, replaced VCC callbacks, module owner, PPP channel registration, `inflight` atomic, `blocked` bit, and selected encapsulation. The special `NONE_INFLIGHT == -2` scheme allows `atomic_inc_not_zero` to enforce a maximum of two queued packets.

## Dependencies and Integration
Integrates with the ATM core callback model, the common ioctl registration list, PPP generic channel APIs, kernel tasklets, module refcounts, and `linux/atmppp.h` backend definitions.

## Risks and Test Signals
Important risks are callback restoration on close, tasklet lifetime, atomic flow-control races, skb ownership across reallocation/send failure, and incomplete RFC 2364 encapsulation-change detection noted by the file comment. Test signals include PPPoA session setup/teardown for VC and LLC modes, autodetection from LCP frames, blocked-output wakeups after ATM `pop`/`release_cb`, backend permission checks, and fault injection for `skb_realloc_headroom`, `ppp_register_channel`, and ATM send errors.
