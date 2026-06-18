# sources/distributed-fs/ceph/src/rgw/rgw_website.h

## Purpose
`rgw_website.h` declares the serialized bucket website configuration model and routing helpers.

## Important APIs, Types, and Functions
`RGWRedirectInfo` stores protocol, host, and redirect code. `RGWBWRedirectInfo` adds key replacement controls. `RGWBWRoutingRuleCondition` stores key prefix and HTTP error condition. `RGWBWRoutingRule` combines condition and redirect. `RGWBWRoutingRules` stores ordered rules. `RGWBucketWebsiteConf` stores redirect-all, index suffix, error document, listing metadata, flags, and routing rules.

## Control Flow
Callers decode config from XML/JSON, persist it in bucket metadata through Ceph encoding, and later evaluate redirect/effective-key helpers during website requests.

## State and Persistence Behavior
All structs use Ceph encode/decode. `RGWBucketWebsiteConf` struct version 2 adds subdir marker, listing CSS doc, and listing enabled while preserving older decode. Boolean flags such as `is_redirect_all` and `is_set_index_doc` are decode/request-state hints rather than encoded fields.

## Dependencies and Integration Points
Depends on Ceph JSON, RGW XML, Formatter, bufferlist encoding, and bucket website REST handlers.

## Risks
Ordering of `std::list<RGWBWRoutingRule>` matters for first-match semantics. `is_empty()` ignores redirect-all and routing rules, so callers must understand what emptiness means. Listing fields are encoded but not dumped to XML in this implementation.

## Test Signals
Binary version compatibility, XML decode flags, routing rule order, redirect-all encoding, listing-field decode, and effective-key behavior should be covered.
