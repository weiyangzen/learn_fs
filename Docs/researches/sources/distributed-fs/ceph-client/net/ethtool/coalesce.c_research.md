# sources/distributed-fs/ceph-client/net/ethtool/coalesce.c

## Purpose
This file implements the ethtool netlink get/set interface for interrupt moderation, packet coalescing, CQE mode, TX aggregation, RX CQE parameters, and dynamic interrupt moderation profiles.

## Important APIs, Types, And Functions
Public objects are `ethnl_coalesce_get_policy`, `ethnl_coalesce_set_policy`, and `ethnl_coalesce_request_ops`. Key local types are `coalesce_req_info` and `coalesce_reply_data`. Important helpers include `attr_to_mask()`, `coalesce_prepare_data()`, `coalesce_reply_size()`, `coalesce_fill_reply()`, `ethnl_set_coalesce_validate()`, `ethnl_update_irq_moder()`, `ethnl_update_profile()`, `__ethnl_set_coalesce()`, and `ethnl_set_coalesce()`.

## Control Flow
GET records driver-supported parameter bits, calls `get_coalesce()`, then emits only supported or nonzero attributes plus optional DIM RX/TX profile nests under RCU. SET first verifies `get_coalesce`/`set_coalesce` and rejects unsupported attributes based on driver-supported coalesce bits plus available DIM profile flags. It reads current driver settings, applies supplied numeric and boolean attributes, updates DIM profiles by duplicating old profile arrays and RCU-swapping new ones, then calls `set_coalesce()`. If a request changes both operation mode and parameters, it calls the driver twice so mode resets do not discard user parameter changes.

## State, Persistence, And Dependencies
Persistent effects are driver coalescing configuration and RCU-published DIM profile arrays on `dev->irq_moder`. The file depends on `linux/dim.h`, ethtool ops, shared netlink update helpers, supported-parameter bit layout, and RCU memory reclamation through `kfree_rcu()`.

## Integration Points
The request ops are registered for coalesce GET/SET/notification messages. Legacy ioctl coalescing shares the same driver callbacks, while this file exposes richer netlink attributes and DIM profile controls.

## Risks
The build-time static assertions rely on ethtool coalesce bit constants matching netlink attribute offsets. Unsupported-parameter filtering must include DIM profile bits only when the netdevice actually has those profiles. Profile parsing currently iterates supplied profile nests into fixed `NET_DIM_PARAMS_NUM_PROFILES` storage; malformed overlong nest counts are a boundary to watch. Dual mode/parameter changes are driver-sensitive.

## Test Signals
Tests should cover unsupported attributes, zero-valued unsupported fields omitted from GET, CQE mode toggles, TX aggregation values, RX/TX DIM profile reads and writes, unsupported DIM subfields, dual mode/parameter SET, no-op SET, and RCU-safe profile replacement.
