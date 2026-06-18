# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.cc

## Purpose
Implements object manifest manipulation, iteration, dumping, test instances, and conversion between logical RGW objects and raw RADOS object locations. Manifests describe how an RGW object is split between a head object and tail stripes or explicit part objects.

## Important APIs And Functions
`RGWObjManifest::append()` combines manifests, using rule merging when both are implicit and falling back to explicit conversion otherwise. `convert_to_explicit()` iterates implicit stripes and records concrete `RGWObjManifestPart` entries. `append_explicit()` appends explicit part maps at the current object size. `get_rule()` finds the active rule for an offset. `obj_find_part()` locates the start of a multipart part. `RGWObjManifest::generator::create_begin()` and `create_next()` build simple manifests as object data is written.

Dump and test-instance functions are implemented for manifest parts, rules, tiers, and manifests. `rgw_obj_select::get_raw_obj()` maps either an already raw object or a logical `rgw_obj` plus placement rule into a `rgw_raw_obj`.

## Control Flow
Append checks whether either manifest is explicit. If both are implicit and the destination has no rules, it copies the source manifest. Otherwise it compares adjacent rule part size, stripe size, and effective prefixes to decide whether rules can be merged or must be appended with adjusted offsets and optional override prefix. Explicit conversion walks object iterators from begin to end, computes raw locations through zone placement, and records part size as the distance to the next stripe offset.

The generator initializes tail placement by inheriting from the head placement when needed, assigns a random prefix when absent, fetches rule zero, sets initial stripe size from head size or stripe max, and updates object size/head size/current stripe on each `create_next()` call.

## State And Persistence
The manifest itself is serialized by methods in the header; this file mutates in-memory fields that later persist as object attributes. Important fields include `explicit_objs`, `objs`, `obj_size`, `obj`, `head_size`, `max_head_size`, `prefix`, `tail_placement`, `rules`, `tail_instance`, tier type, and tier config. Raw object mapping depends on zonegroup and zone params at interpretation time.

## Dependencies And Integration Points
Depends on zone service placement, `RGWRados::get_obj_data_pool()` under RADOS builds, bucket helpers, random prefix generation, and `RGWSI_Tier_RADOS::raw_obj_to_obj()` for explicit conversion. The manifest is consumed by object read/write, multipart, copy, tiering, and data layout code across RGW.

## Risks And Edge Cases
Append mutates source manifest rules by filling zero `part_size`, so callers should not assume the appended source is unchanged. `obj_find_part()` is linear over stripes. Explicit test instance construction stores parts keyed by accumulated total size, which is useful for encoding coverage but does not mirror every production layout. Raw object mapping falls back to default placement if head placement has no data pool; placement drift can affect interpretation of older manifests. Tests should cover old explicit manifests, implicit append with same/different prefix, multipart part seeking, generated random prefixes, and pool selection for normal and extra data.
