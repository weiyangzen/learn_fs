## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.hh

Purpose: declares URL parsing utilities for REST route recognition and path normalization.

Important APIs/types/functions: constructor, `startsBy`, `matches`, `matchesAndExtractParameters`, static `removeDuplicateSlashes`, and private token vector.

Control flow: callers instantiate parser per URL and compare it against access URLs or route patterns.

State and persistence: stores parsed URL tokens only.

Dependencies and integration points: central utility for REST manager/router and tape model path storage.

Risks and test signals: ensure callers understand `matchesAndExtractParameters` key names include placeholder braces and that matching is token-based, not URL-decoding-aware.
