# sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.cc

## Purpose
Implements a RADOS watch/notify based fairness protocol for RGW sync shard processing. Each gateway generates random bids per replication log shard, exchanges bids with peers, and processes only shards where it holds the highest known bid.

## Important APIs, types, and functions
- Encoded `BidRequest` and `BidResponse` carry bid vectors.
- `apply_notify_responses()` decodes watch notify replies and timeout lists into a peer bid map.
- `Watcher` owns a librados `watch2()` registration on a control object, creates the object if missing, responds to peer bid notifications, and restarts on watch errors.
- `NotifyCR` wraps `RGWRadosNotifyCR` to broadcast this gateway's bids and feed responses back into the manager.
- `RadosBidManager` implements `BidManager`, `Server`, and `DoutPrefix`; it stores local bids and peer bids under a mutex.
- `create_rados_bid_manager()` returns the concrete manager.

## Control flow
On construction, `RadosBidManager` fills a vector with shard indices and shuffles it, producing a unique bid ordering. `start()` registers the watcher. Incoming notifications decode peer bids, update `all_bids`, and reply with local bids. `notify_cr()` snapshots local bids into a coroutine request; completion decodes responders and timeouts, clears previous peer bids, and installs the latest response set. `is_highest_bidder(index)` compares the local bid against each peer's bid at the same index.

## State and persistence behavior
The durable/control object is only used as a watch/notify rendezvous point in RADOS. Bid state is in memory: `my_bids` and `all_bids`. Peer entries are removed when notify responses report timeouts, and the response path clears all peer bids before applying the latest replies.

## Dependencies and integration points
Depends on librados watch/notify, `RGWRadosNotifyCR`, `rgw::sal::RadosStore`, Ceph encoding, logging, random shuffle, and coroutine macros. It integrates with RGW sync logic through the `BidManager` interface in `sync_fairness.h`.

## Risks and edge cases
`is_highest_bidder()` uses `vector::at()` for local and peer bids, so mismatched shard counts throw exceptions. Clearing `all_bids` on notify response can drop newer bids that raced with the outgoing notify, as noted in the code. Ties favor the local gateway because only strictly greater peer bids win. Watch restart failures close the ioctx. Decode failures return `-EIO` but notification handler only logs bad requests.

## Test signals
Tests should cover bid encode/decode, timeout removal, highest-bid comparison, equal-bid tie behavior, mismatched bid vector size handling, watcher creation when object is absent, notify response races, and restart after watch error.
