# sources/distributed-fs/ceph-client/net/can/j1939/address-claim.c

## Purpose
This file implements J1939 address-claim processing and NAME-to-source-address fixup. It tracks observed address-claimed messages, resolves source/destination names into current addresses for outgoing traffic, annotates incoming skbs with source/destination names, and enforces J1939 address-claim message validity.

## Important APIs, Types, And Functions
Exported internal functions are `j1939_ac_fixup()` for TX-time address/name resolution and `j1939_ac_recv()` for RX-time address-claim and name annotation.

Important helpers include `j1939_skb_to_name()`, `j1939_ac_msg_is_request()`, `j1939_ac_verify_outgoing()`, and `j1939_ac_process()`. They operate on `struct j1939_priv`, `struct j1939_sk_buff_cb`, `struct j1939_ecu`, and the ECU mapping APIs from `bus.c`.

## Control Flow
On transmit, `j1939_send_one()` calls `j1939_ac_fixup()`. Address-claimed PGNs are validated for 8-byte NAME payload, matching source name, non-broadcast source address, and broadcast destination. If a claimed ECU's address differs from the outgoing source address, the old mapping is removed so the later looped-back address-claim receive path can establish the new mapping. Non-address-claim traffic with a source or destination name is resolved through `j1939_name_to_addr()` and rejected with `-EADDRNOTAVAIL` when no unicast mapping exists, except for address-claim request messages.

On receive, `j1939_ac_recv()` handles address-claimed PGNs through `j1939_ac_process()`. That function validates DLC/name/source address, finds or creates the ECU by NAME, cancels pending claim timers, handles idle-address unmapping, applies J1939 NAME priority when two ECUs contend for the same address, and starts the ECU's 250 ms claim timer. For other received traffic, it looks up current source and destination names by address and stores them in the skb control block.

## State And Persistence
Address-claim state is stored in `struct j1939_priv`: the ECU list and 256-entry address map maintained by `bus.c`. Mappings are not committed immediately on address-claimed reception; they become active after the ECU timer expires, matching the J1939 contention window. State lasts while the J1939 per-device private object exists and is cleared on netdevice down/unregister.

## Dependencies And Integration Points
The file depends on `j1939-priv.h`, ECU map helpers from `bus.c`, and send/receive orchestration in `main.c`. It relies on CAN echo: locally sent address-claim frames are processed in the receive path so local and remote claims are ordered consistently.

## Risks And Edge Cases
Address-claim correctness depends on receiving local echo. If echo is absent or delayed, local ECU mappings may not become active when user space expects.

The code intentionally does not send address-claim responses itself; user space must implement policy daemons. Kernel state only observes and resolves claims.

NAME priority conflict handling unmaps the losing ECU and starts/restarts timers under `priv->lock`; missed refcount or timer cancellation bugs here would affect all name/address resolution.

Outgoing named traffic can fail until the 250 ms address-claim timer maps the ECU, even if an address-claimed frame was just seen.

## Test Signals
Tests should inject address-claimed frames with valid, idle, duplicate, and malformed payloads; verify 250 ms delayed mapping; verify lower NAME wins address contention; verify outgoing named traffic fails before claim and succeeds after mapping; and verify local echo address claims update mappings in transmit order.
