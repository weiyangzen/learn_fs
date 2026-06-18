# sources/distributed-fs/ceph-client/net/ethtool/channels.c

## Purpose
This file implements the ethtool netlink get/set interface for netdevice channel counts. Channels describe RX, TX, combined, and other queue group counts plus their driver-reported maxima.

## Important APIs, Types, And Functions
The key local types are `channels_req_info` and `channels_reply_data`. Public objects are `ethnl_channels_get_policy`, `ethnl_channels_set_policy`, and `ethnl_channels_request_ops`. Important functions are `channels_prepare_data()`, `channels_reply_size()`, `channels_fill_reply()`, `ethnl_set_channels_validate()`, and `ethnl_set_channels()`.

## Control Flow
GET checks that `get_channels` exists, calls it under ethtool ops bracketing, and emits only groups with nonzero maxima. SET starts from the current channel configuration, applies any supplied count attributes, exits if unchanged, validates each count against its maximum, ensures at least one RX and TX path remain, asks `ethtool_check_max_channel()` whether existing RSS, ntuple, or memory-provider configuration needs higher channel indices, verifies queues being removed are not busy, then calls the driver `set_channels()` callback.

## State, Persistence, And Dependencies
The only persistent effect is through the driver callback, which reconfigures the device's queue/channel state. The file depends on netdev queue busy checks, `ethtool_ops`, shared netlink update helpers, and `common.c` validation helpers.

## Integration Points
`ethnl_channels_request_ops` is registered in the ethtool netlink dispatcher for `ETHTOOL_MSG_CHANNELS_GET`, SET, and notifications. It mirrors legacy ioctl behavior while adding netlink extack messages and queue-busy validation.

## Risks
Reducing channels can invalidate existing RSS indirection tables, ntuple filters, memory-provider queue bindings, or active AF_XDP/leased queues. Drivers can report inconsistent maxima/counts, so validation before `set_channels()` is critical. Omitting notifications or returning the wrong status can leave userspace with stale topology.

## Test Signals
Tests should cover no-op SET, each maximum violation, zero RX/TX rejection, reductions blocked by RSS or ntuple state, queue-busy failures, successful increases/decreases, and GET replies that omit unsupported channel groups.
