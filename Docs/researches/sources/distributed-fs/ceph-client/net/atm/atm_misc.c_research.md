# sources/distributed-fs/ceph-client/net/atm/atm_misc.c

Purpose: provides small exported helper routines for ATM drivers and protocol adapters, covering receive-buffer accounting, PCR selection, and SONET statistics conversion.

Important APIs, types, and functions: exported helpers are `atm_charge`, `atm_alloc_charge`, `atm_pcr_goal`, `sonet_copy_stats`, and `sonet_subtract_stats`.

Control flow: `atm_charge` force-charges receive memory to the VCC socket, checks against `sk_rcvbuf`, and either keeps the charge or returns it and increments `rx_drop`. `atm_alloc_charge` estimates skb truesize, charges first, allocates the skb, adjusts accounting to actual truesize, or rolls back on failure. `atm_pcr_goal` converts ATM traffic parameters into a positive, negative, or zero PCR target describing rounding direction or maximum bandwidth. SONET helpers copy/subtract atomic stats through the `__SONET_ITEMS` macro list.

State and persistence: no independent state. It mutates per-socket receive accounting and VCC statistics counters provided by callers.

Dependencies and integration points: exported to ATM drivers and modules that receive cells/PDUs and need consistent socket buffer accounting. Relies on `atm_force_charge`, `atm_return`, `sk_atm`, skb allocation, and SONET stat definitions.

Risks: accounting correctness is critical; double charging or missing rollback can create memory pressure or false leakage warnings. `atm_alloc_charge` uses an estimate before allocation and must compensate for actual skb truesize. PCR sign semantics are compact and easy for callers to misuse.

Test signals: receive path under small `sk_rcvbuf`, allocation failure injection, rx_drop counter increments, accounting returning to zero after skb free, PCR table cases from the comment, and SONET stat copy/subtract with nonzero atomic counters.
