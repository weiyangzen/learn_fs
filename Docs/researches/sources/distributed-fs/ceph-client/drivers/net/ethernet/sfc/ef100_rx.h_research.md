# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.h

Purpose: Declares the EF100 RX entry points consumed by the generic SFC channel, RX, and NIC-type dispatch layers.

Important APIs and types: Exports `ef100_rx_buf_hash_valid()`, `efx_ef100_ev_rx()`, `ef100_rx_write()`, and `__ef100_rx_packet()`. It includes `net_driver.h` for `struct efx_channel`, `struct efx_rx_queue`, and `efx_qword_t`.

Control flow and integration: These prototypes bind EF100-specific RX behavior into generic indirect calls in `efx.h` and event dispatch from NIC-specific event processing. `ef100_rx_write()` is used when refilling descriptors; `efx_ef100_ev_rx()` is used when event queues produce RX completions; `__ef100_rx_packet()` is the flush/finalize hook.

State and persistence: The header owns no state. Its ABI shape determines how EF100 RX code is called from shared queue and event code.

Dependencies: Depends on shared SFC data structures from `net_driver.h` and on matching implementations in `ef100_rx.c`.

Risks: Prototype drift would break indirect-call targets or NIC type tables. Including this header in `efx.h` makes circular dependency hygiene important.

Test signals: Compile coverage for EF100 NIC type setup, RX event handling, RX refill, and generic `efx_rx_flush_packet()` indirect calls.
