# sources/distributed-fs/ceph/src/rgw/rgw_keystone.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This implementation provides Keystone token id helpers, config-bound endpoint/password access, admin and Barbican token requests over RGW HTTP, token JSON parsing, role annotation, LRU token caching, invalidation, and Keystone v3 request JSON dumping. Runtime state is process-local token caches keyed by token id; outbound Keystone requests and cached tokens are security-sensitive. Dependencies include RGW HTTP, Ceph JSON/Formatter, MD5 for PKI cache ids, ISO8601 parsing, config, and perf counters. Risks include secret-file edge cases, endpoint static normalization, missing subject tokens, malformed JSON, clock skew, wildcard role matching, and partial invalidation behavior. Tests should cover token ids, request JSON, unauthorized/malformed responses, expiry/LRU, invalidation, and cache hit/miss counters.
