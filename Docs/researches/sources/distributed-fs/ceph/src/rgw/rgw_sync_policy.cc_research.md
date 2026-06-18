# sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.cc

## Purpose
`rgw_sync_policy.cc` implements mutation, expansion, matching, JSON decode/dump, and helper logic for RGW multisite sync policy data structures.

## Important APIs, Types, and Functions
Filter tags parse `key` or `key=value` strings, filters manage optional prefixes and tag sets, and check whether object names/tags pass. Bucket entity helpers apply buckets, add/remove zones, set wildcard bucket fields, expand aggregate zone/bucket sets into concrete pipe endpoints, and compute related buckets. Data-flow helpers find/create/remove symmetrical groups and directional rules. Policy group helpers find/create/remove pipes and walk related buckets. Dump/decode functions serialize the policy model to JSON.

## Control Flow
Admin/config operations mutate `rgw_sync_policy_info` through group/pipe/filter/data-flow helpers. Runtime code expands aggregate pipes into concrete `rgw_sync_bucket_pipe` combinations and uses match helpers to discover whether a bucket may source or receive sync. JSON decode maps lists of groups back into the `groups` map keyed by id.

## State and Persistence Behavior
The file mutates in-memory policy structures that are encoded by the header's Ceph encoding methods for persistence in realm/zonegroup/bucket metadata. Wildcards are represented by empty bucket fields, unset zones, or `all_zones`.

## Dependencies and Integration Points
It depends on `rgw_sync_policy.h`, `rgw_bucket.h`, `rgw_tag.h`, Boost prefix matching, Ceph JSON encoders, and bucket-key parsing. It integrates with multisite sync policy admin commands and data-sync selection logic.

## Risks
`rgw_sync_pipe_filter_tag::operator==(const string&)` appears to compare `s` against itself for the key range, which can make tag-string equality wrong. Tag filters use any-match semantics in `check_tags()`, not all-match semantics. Wildcard representation through empty strings can be subtle when tenant/name/bucket_id are partially set. Decode silently resets invalid bucket strings.

## Test Signals
Cover `key` and `key=value` parsing, prefix subset checks, tag add/remove and object tag matching, wildcard bucket fields, all-zones expansion, directional/symmetrical removal, aggregate pipe expansion, related bucket discovery, JSON round trips, and invalid bucket-key decode behavior.
