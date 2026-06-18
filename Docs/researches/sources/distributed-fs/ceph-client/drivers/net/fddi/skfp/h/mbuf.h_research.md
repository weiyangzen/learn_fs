# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/mbuf.h

## Purpose
`mbuf.h` defines the small SMT mbuf abstraction used for internal SMT/RAF/management frames independent of Linux `sk_buff` data paths.

## Important APIs, Types, And Functions
It defines `M_SIZE`, `MAX_MBUF`, `struct s_mbuf`, typedef `SMbuf`, compatibility aliases (`sm_next`, `sm_off`, `sm_len`, `sm_data`, `SMbuf`, `mtod`, `mtodoff`), and pointer conversion macros `smtod()` and `smtodoff()`.

## Control Flow
No code executes here. SMT builders allocate an `SMbuf`, set offset and length, write a typed frame with `smtod()`, and transmit or free it through SMT/HWM functions.

## State And Persistence
Each mbuf stores next pointer, data offset, length, optional PCI use count, and a fixed 4504-byte data buffer. Pools live in HWM state or outside `smc` when configured.

## Dependencies And Integration Points
Used by SMT frame construction, ESS RAF handling, HWM mbuf pools, and TX/RX queues. It depends on base integer types from `types.h`.

## Risks And Edge Cases
The fixed buffer size must cover maximum SMT/FDDI management frames. `smtod()` trusts `sm_off` and requested type alignment. `NO_STD_MBUF` changes compatibility aliases and can affect legacy code.

## Test Signals
Allocate/free pool behavior, SMT frame construction at max sizes, offset handling, PCI use-count behavior, and typed access with aligned `struct smt_header`.
