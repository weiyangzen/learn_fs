# sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.cc

## Purpose
`rgw_s3_filter.cc` implements S3 notification filter parsing, formatting, and matching. Filters can match object key prefix/suffix/regex, user metadata key-value pairs, and object tag key-value pairs.

## Important APIs, Types, and Functions
`rgw_s3_key_filter::{dump,decode_xml,dump_xml,has_content}` handles the `S3Key` filter. XML decode allows one prefix, one suffix, and one regex rule and throws on invalid or duplicate rule names. `rgw_s3_key_value_filter` handles metadata/tag `FilterRule` lists as a flat key-value map. `rgw_s3_filter` composes key, metadata, and tag filters and emits JSON/XML only when content exists.

`match(const rgw_s3_key_filter&, const std::string&)` checks prefix, suffix, and full regex match. `match(const rgw_s3_key_value_filter&, const KeyValueMap&)` uses sorted `std::includes()` for flat metadata. The multimap overload checks that each filter pair appears among equal-range values. `match(const rgw_s3_filter&, const rgw::sal::Object*)` returns true if any one of key, metadata, or tag filter matches.

## Control Flow
Notification configuration XML is decoded into filter structs. During event evaluation, the object pointer is checked, then key filter is evaluated first. If metadata rules exist, RGW object attrs with `RGW_ATTR_META_PREFIX` are converted into a flat map and compared. If tag rules exist, `RGW_ATTR_TAGS` is decoded into `RGWObjTags` and compared. A match in any category returns true.

## State and Persistence Behavior
The structs are serializable into bucket notification configuration. `rgw_s3_filter` encoder version 2 added `tag_filter`; decoding old version 1 configs leaves tags empty. Matching reads cached object attrs but does not persist or mutate state.

## Dependencies and Integration Points
The file depends on RGW XML helpers, formatter encode helpers, notification/pubsub structures, SAL `Object`, RGW object tags, Boost string prefix checks, and C++ regex. It is used by bucket notification topic filtering.

## Risks
Top-level matching is OR across key, metadata, and tags; if intended semantics require all configured filter categories to match, this is broad. Regexes are compiled on every match and invalid regex strings can throw. Metadata key stripping uses `sizeof(RGW_ATTR_PREFIX)-1` after checking `RGW_ATTR_META_PREFIX`, so prefix constants must stay compatible. Metadata comparison depends on sorted `flat_map` ordering.

## Test Signals
Tests should cover XML duplicates, JSON/XML dump elision, prefix/suffix/regex combinations, invalid regex handling, metadata extraction from attrs, tag decode failure returning false, multivalue tag matching, old encoded filters without tags, and OR-versus-AND behavior expected by notification APIs.
