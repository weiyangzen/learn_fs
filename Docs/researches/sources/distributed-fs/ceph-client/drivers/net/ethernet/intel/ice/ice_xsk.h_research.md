# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.h

## Purpose
Declares AF_XDP zero-copy APIs and provides stubs when `CONFIG_XDP_SOCKETS` is disabled.

## Important APIs
Defines `PKTS_PER_BATCH` as 8 for batched AF_XDP Tx descriptor handling. Real builds export pool setup, zero-copy Rx clean, wakeup, Rx buffer allocation, XSK-enabled query, ring cleanup, zero-copy Tx, Rx XDP buffer reallocation, and queue-vector IRQ/NAPI helpers. Non-XDP-sockets builds return conservative false/zero/`-EOPNOTSUPP` results and no-op cleanup/IRQ helpers.

## Control Flow and State
The header gates all AF_XDP behavior at compile time. Callers can invoke helpers without conditional code and receive disabled behavior when sockets support is absent.

## Dependencies and Integration Points
Includes `ice_txrx.h` for ring and q_vector types; used by netdev XSK hooks, XDP setup, queue pair management, and Tx/Rx datapath code.

## Risks
Stub return values must match caller expectations. In particular, `ice_clean_rx_irq_zc()` returns 0 when disabled, and `ice_xmit_zc()` returns false, so callers must only choose the zero-copy path when feature/pool state is active.

## Test Signals
Compile with `CONFIG_XDP_SOCKETS=y/n`, verify no unresolved XSK symbols, and run datapath tests that ensure disabled builds fall back to normal Rx/Tx paths.
