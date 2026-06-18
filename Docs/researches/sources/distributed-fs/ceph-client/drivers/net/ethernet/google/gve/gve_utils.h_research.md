
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_utils.h

## Purpose

This header declares shared GVE helper functions implemented in `gve_utils.c` for queue notification block management, RX packet copying, page bias accounting, and NAPI lifecycle.

## Important APIs, Types, and Functions

The exported declarations cover TX/RX add/remove/status helpers, `gve_rx_copy_data()`, `gve_rx_copy()`, `gve_dec_pagecnt_bias()`, `gve_add_napi()`, and `gve_remove_napi()`. It includes `gve.h` and `<linux/etherdevice.h>` so callers see the GVE private structures and netdev types.

## Control Flow

There is no runtime control flow in this header. It establishes compile-time function contracts for GVE source files.

## State and Persistence

No state is stored here. State effects happen in the implementation and callers.

## Dependencies and Integration Points

The header integrates multiple GVE RX/TX implementations with common helpers and must remain consistent with the function definitions in `gve_utils.c`.

## Risks and Edge Cases

Prototype drift would break builds or, if types changed incompatibly in related headers, cause incorrect caller assumptions about object ownership and NAPI locking context. The header is small but central to TX/RX lifecycle code.

## Test Signals

Build coverage of all GVE objects using this header is the primary signal. Runtime signals are the same queue/NAPI/RX-copy behavior covered by `gve_utils.c`.
