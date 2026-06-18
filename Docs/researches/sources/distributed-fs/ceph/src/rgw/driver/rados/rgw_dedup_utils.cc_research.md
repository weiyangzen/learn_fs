# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.cc

## Purpose
`rgw_dedup_utils.cc` implements serialization, parsing, formatting, and stats aggregation helpers for the RGW dedup subsystem. It provides encoded forms for throttles, stats, and throttle messages; parses S3 ETags into dedup keys; and dumps worker and MD5 shard stats for admin output.

## Important APIs, Types, And Functions
`operator<<` for `dedup_req_type_t` prints estimate or execution mode. `validate_max_calls_offset()` enforces that `Throttle::max_calls` is first for aligned non-atomic updates. `encode()` and `decode()` for `Throttle` persist only its configured rate limit, not runtime counters.

`throttle_action_t` and `throttle_msg_t` have stream and encode/decode helpers. `dedup_stats_t`, `worker_stats_t`, and `md5_stats_t` implement `operator+=`, stream formatting via `JSONFormatter`, `dump()` methods, and Ceph encode/decode.

`hex2int()`, private `dec2int()`, `get_num_parts()`, `parse_etag_string()`, and `etag_to_bufferlist()` convert S3 ETag strings to and from MD5 high/low words and multipart part counts. `get_next_data_ptr()` extracts contiguous data from possibly fragmented bufferlists by zero-copy when possible or copying into a caller buffer.

## Control Flow
Stats flow from worker and MD5 shard phases into token completion xattrs. Cluster stats aggregation decodes them and calls their `dump()` methods. ETag parsing runs during bucket-index ingress and filters out corrupted or unsupported ETags before a disk record is created.

Throttle messages arrive over watch/notify, decode into action vectors, and change the live control throttles in the background service.

## State And Persistence Behavior
All encode/decode functions use Ceph encoding version 1 and form part of the persisted xattr/notify ABI. Worker and MD5 stats are stored in shard progress xattrs. Throttle config is carried in notify payloads and control acknowledgements.

## Dependencies And Integration Points
The file depends on Ceph crypto MD5 support, bufferlist, formatter, JSON formatter, and the utility declarations. It is heavily consumed by `rgw_dedup_cluster.cc`, the main background dedup implementation, and `rgw_dedup_table.cc`.

## Risks And Edge Cases
`parse_etag_string()` assumes a 32-hex-character MD5 prefix and optional `-parts` suffix. Quoted or otherwise decorated ETags must be normalized before this function or they will fail. `get_num_parts()` caps multipart parts at 10,000 and rejects too-long suffixes. `get_next_data_ptr()` relies on the caller-provided buffer being at least `len` bytes.

Stats encoding is append-only sensitive: changing field order breaks decode compatibility. Some dump methods always emit zero counters while others emit conditionally, so admin output stability should be considered.

## Test Signals
Tests should cover single-part and multipart ETag parsing, invalid hex, invalid part suffixes, max part count, ETag formatting, fragmented bufferlist copy paths, encode/decode round trips for stats and throttle messages, and aggregation of every stats counter.
