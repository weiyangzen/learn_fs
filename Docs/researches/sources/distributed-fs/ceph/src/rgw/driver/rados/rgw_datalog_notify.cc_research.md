# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.cc

## Purpose
This file implements JSON compatibility adapters for the v1 RGW data-log notification API. The current notification entry type contains both bucket key and generation, but the v1 wire shape only exposed object keys as strings. These helpers encode and decode the old map-of-shards-to-set-of-strings form while preserving the current in-memory `rgw_data_notify_entry` container type.

## Important APIs, Types, and Functions
`EntryEncoderV1` wraps a single `rgw_data_notify_entry` and emits only `entry.key`. `SetEncoderV1` wraps a flat set of notification entries and emits an array of `"obj"` strings. The exported `encode_json(const char*, const rgw_data_notify_v1_encoder&, Formatter*)` emits an array of objects with `"key"` shard id and `"val"` encoded set.

`EntryDecoderV1` decodes one JSON string into `entry.key` and explicitly sets `entry.gen = 0`, because the v1 API had no generation field. `SetDecoderV1` iterates array children and inserts decoded entries into a `bc::flat_set`. The exported `decode_json_obj(rgw_data_notify_v1_decoder&, JSONObj*)` decodes the top-level array back into a flat map of shard id to entry set.

## Control Flow
Encoding walks shards in sorted flat-map order, opens an object for each shard, writes the shard id, then writes the v1 set of strings. Decoding mirrors that flow by iterating top-level array entries, reading `"key"` into `shard_id`, decoding `"val"` through `SetDecoderV1`, and replacing `d.shards[shard_id]` with the decoded set.

## State and Persistence Behavior
The file does not persist data directly. It defines a compatibility JSON representation used at API boundaries. Generation state is intentionally discarded when encoding v1 and defaults to zero when decoding v1, so v1 clients cannot distinguish bilog generations for the same key.

## Dependencies and Integration Points
It depends on `rgw_datalog_notify.h`, `rgw_datalog.h`, `Formatter`, `JSONObj`, `JSONObjIter`, and `JSONDecoder`. It integrates with data-log notification REST/admin paths that need legacy JSON while the internal notification set remains generation-aware.

## Risks and Test Signals
The main risk is lossy generation conversion. If a shard contains multiple entries with the same key but different generations, v1 encoding collapses them to duplicate strings in semantic terms, and v1 decoding reintroduces only `gen = 0`. Tests should verify exact v1 JSON shape, empty shard maps, multiple shards, deterministic ordering from flat containers, and mixed generation inputs documenting the lossy behavior.
