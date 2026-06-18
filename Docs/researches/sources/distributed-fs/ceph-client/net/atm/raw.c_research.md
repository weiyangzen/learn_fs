# sources/distributed-fs/ceph-client/net/atm/raw.c

## Purpose
`raw.c` installs raw AAL0, AAL3/4, and AAL5 VCC handlers. These handlers provide the default ATM data path: receive packets into the socket queue, account transmit completion, and use device send callbacks.

## Important Functions
- `atm_push_raw`: receive callback; queues non-NULL skbs to `sk_receive_queue` and signals `sk_data_ready`.
- `atm_pop_raw`: transmit-completion callback; returns TX accounting, frees the skb, and wakes writers.
- `atm_send_aal0`: AAL0 send wrapper that prevents unprivileged users from sending cells whose encoded VPI/VCI does not match the VCC.
- `atm_init_aal0`, `atm_init_aal34`, `atm_init_aal5`: set `push`, `pop`, `push_oam`, and `send` callbacks on the VCC.

## Control Flow
After VCC setup chooses an AAL, the corresponding initializer mutates the VCC callback table. Incoming packets enter `atm_push_raw` from drivers and become socket-readable data. Transmit completion enters `atm_pop_raw`, releases accounting, frees the skb, and notifies write waiters. AAL3/4 and AAL5 send directly through `dev->ops->send_bh` when available, otherwise `dev->ops->send`; AAL0 adds the capability/address check first.

## State and Persistence
The file stores no global state. Runtime state is VCC callback assignment, socket queues, skb ownership, and ATM accounting in the VCC/socket.

## Dependencies and Integration
Depends on ATM device ops, socket queues, skb APIs, capability checks, and `protocols.h` declarations. `atm_init_aal5` is exported for users outside the immediate file.

## Risks and Test Signals
Risks include skb ownership on send failures, accounting mismatch between `atm_account_tx` users and `atm_return_tx`, and AAL0 header validation with `_ANY`/`_UNSPEC` VPI/VCI. Test signals include raw AAL5 send/receive, write-space wakeups after completion, AAL0 permission rejection for mismatched cell headers, and device variants with and without `send_bh`.
