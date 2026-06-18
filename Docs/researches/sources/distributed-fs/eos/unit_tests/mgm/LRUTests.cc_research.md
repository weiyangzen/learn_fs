# sources/distributed-fs/eos/unit_tests/mgm/LRUTests.cc

## Purpose
Tests parsing of MGM LRU expiration policies. These policies combine filename patterns, age thresholds, and optional size comparisons for cleanup decisions.

## Important APIs, types, and functions
The tests cover `LRU::parseExpireMatchPolicy`, `LRU::extractTimeSizeCriterias`, `LRU::parseExpireSizeMatchPolicy`, and `LRU::PolicyRule` equality. Units include days, weeks, and months, and size suffixes include SI-style K/M/G values.

## Control flow
Single and multiple pattern tests parse simple `pattern:age` rules. Time/size extraction tests validate empty/invalid strings, plain seconds, month age, greater-than and less-than size filters. Full policy tests iterate expected valid strings and invalid strings.

## State and persistence
State is parsed into maps or ordered policy-rule vectors. Production policy strings are persisted as namespace/MGM configuration values.

## Dependencies and integration points
Depends on Google Test and `mgm/lru/LRU.hh`. It integrates with LRU cleanup and policy enforcement code.

## Risks and test signals
Tests protect grammar and rule ordering, including trailing/duplicate commas. Risks include unit interpretation (`1mo` fixed at 31 days), SI vs binary size assumptions, wildcard matching semantics not covered here, and missing tests for huge values or whitespace.
