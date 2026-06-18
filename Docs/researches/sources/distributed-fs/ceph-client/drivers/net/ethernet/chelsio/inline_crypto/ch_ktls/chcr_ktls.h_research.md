# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_ktls.h

## Purpose

`chcr_ktls.h` declares the private data structures, constants, inline accessors, and CPL handler type used by the Chelsio kTLS TX offload driver. It bridges Linux TLS offload driver-state storage with Chelsio adapter/TCB/L2T resources.

## Important APIs, Types, and Functions

- `struct chcr_ktls_info` is the per-TX-offload connection object. It stores socket, adapter, L2T, netdev, completion, key context, record/IV state, TCB sequence/cache fields, queue/channel/port identity, open state, and pending-close flag.
- `struct chcr_ktls_ctx_tx` is the small object stored in `TLS_DRIVER_STATE_SIZE_TX`; it points to `chcr_ktls_info`.
- `struct chcr_ktls_uld_ctx` stores per-ULD adapter data: list linkage, copied `cxgb4_lld_info`, TID xarray, and detach flag.
- `enum ch_ktls_open_state` defines `CH_KTLS_OPEN_SUCCESS`, `CH_KTLS_OPEN_PENDING`, and `CH_KTLS_OPEN_FAILURE`.
- Inline accessors `__chcr_get_ktls_tx_info()`, `chcr_get_ktls_tx_info()`, and `chcr_set_ktls_tx_info()` safely cast TLS driver state and enforce size with `BUILD_BUG_ON`.
- `chcr_get_first_rx_qid()` fetches the first RX queue ID from the KTLS ULD handle saved on the adapter.
- `chcr_handler_func` is the CPL handler signature used by `chcr_ktls.c`.

## Control Flow

This header does not implement protocol flow directly. It defines how `chcr_ktls.c` stores and retrieves per-connection offload state from `struct tls_context`, how ULD receive handlers reference per-adapter state, and how the first RX queue is selected for control replies.

## State and Persistence Behavior

All state is volatile kernel memory. The design relies on TLS core driver-state memory to hold a pointer, while the actual `chcr_ktls_info` object is allocated/freed by add/delete and detach paths. `chcr_ktls_uld_ctx.detach` is a coarse state bit used to suppress normal deletion during adapter teardown.

## Dependencies and Integration Points

The header includes Chelsio adapter, CPL, TCB, L2T, common crypto, ULD, and CLIP definitions. It also depends on Linux TLS offload context layout via the functions used in inline accessors.

## Risks and Edge Cases

- The TLS driver-state area only stores a pointer; use-after-free prevention depends on the lifecycle in `chcr_ktls.c`.
- `chcr_get_first_rx_qid()` returns `-1` when the ULD handle is absent; callers must treat this as setup failure.
- `chcr_ktls_info` stores both connection state and cached TX state, so partial initialization must be cleaned carefully on errors.

## Test Signals

Compile-time coverage should catch driver-state size regressions through `BUILD_BUG_ON`. Runtime tests should validate that `tls_dev_add` fails cleanly when no KTLS ULD context exists and that detach clears TLS driver state for all TIDs.
