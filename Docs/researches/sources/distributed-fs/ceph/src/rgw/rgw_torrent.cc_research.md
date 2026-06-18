# sources/distributed-fs/ceph/src/rgw/rgw_torrent.cc

## Purpose
`rgw_torrent.cc` builds and reads bencoded torrent metadata for RGW object torrent support.

## Important APIs, Types, and Functions
`bencode_dict()`, `bencode_list()`, `bencode_end()`, `bencode_key()`, and overloads of `bencode()` write bencoded primitives and dictionary entries. `rgw_read_torrent_file()` loads stored object torrent info and adds configured tracker/comment/created-by/encoding fields. `RGWPutObj_Torrent::process()` computes SHA1 piece hashes while streaming upload data. `bencode_torrent()` produces the stored info dictionary for eligible objects.

## Control Flow
On upload, the torrent pipe forwards all data downstream while updating piece digest state. A final zero-length process call flushes the last partial piece. If object length reaches the configured max, hash state is cleared and no torrent metadata is produced. On read, stored info is appended after top-level configured fields.

## State and Persistence Behavior
The pipe stores upload-local length, piece length, current piece offset, piece count, SHA1 state, and concatenated piece hashes. The object's torrent info is persisted by callers using the buffer returned from `bencode_torrent()`.

## Dependencies and Integration Points
Depends on Ceph SHA1, bufferlist, config fields (`rgw_torrent_tracker`, etc.), SAL object `get_torrent_info()`, and put-object filter pipeline.

## Risks
Integer bencode overloads accept `int`, while object lengths are `size_t`; large values may truncate through overload selection. Torrent generation stops at `len >= max_len`, excluding objects exactly at the limit. Bencode correctness depends on stored info already containing a valid `info` key sequence.

## Test Signals
Cover small object, exact piece boundary, partial final piece, max length boundary, multiple trackers, empty optional config fields, bencode syntax, and read failure from `get_torrent_info()`.
