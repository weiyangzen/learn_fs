# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/libcxgb/libcxgb_cm.h

## Purpose

`libcxgb_cm.h` declares common Chelsio connection-management helper APIs and provides inline builders for frequently used CPL control messages.

## Important APIs, Types, and Functions

- Declared exported APIs: `cxgb_get_4tuple()`, `cxgb_find_route()`, and `cxgb_find_route6()`.
- `cxgb_is_neg_adv()` identifies negative-advice CPL statuses.
- `cxgb_best_mtu()` chooses an aligned MTU index from adapter MTU tables while accounting for IPv4/IPv6, TCP, and timestamp option header sizes.
- CPL builders: `cxgb_mk_tid_release()`, `cxgb_mk_close_con_req()`, `cxgb_mk_abort_req()`, `cxgb_mk_abort_rpl()`, and `cxgb_mk_rx_data_ack()`.
- `cxgb_compute_wscale()` computes a TCP window scale for a desired receive window.

## Control Flow

Callers allocate an SKB of suitable size and use the inline builders to append zeroed CPL structures, initialize TP WR fields, set opcode/TID, choose TX priority/queue, and optionally attach ARP error handlers. Route and tuple functions are implemented in `libcxgb_cm.c`.

## State and Persistence Behavior

No state is owned here. Inline builders mutate caller-provided SKBs and rely on caller-owned TID/channel/handler values.

## Dependencies and Integration Points

The header depends on Linux TCP headers and Chelsio `cxgb4`, CPL, and L2T APIs. It is intended as shared glue for Chelsio offload consumers that need consistent CPL construction.

## Risks and Edge Cases

- Inline builders assume the caller sized the SKB correctly and that `__skb_put_zero()` has enough tailroom.
- `cxgb_best_mtu()` subtracts header size from MTU; callers must avoid invalid MTU/header combinations.
- `cxgb_compute_wscale()` caps at 13/14 loop behavior consistent with TCP scaling but should be validated against max window expectations.

## Test Signals

Compile consumers with this header, inspect generated CPLs for opcode/TID/queue/handler fields, test MTU selection with timestamp and IPv6 combinations, and validate negative-advice recognition against firmware statuses.
