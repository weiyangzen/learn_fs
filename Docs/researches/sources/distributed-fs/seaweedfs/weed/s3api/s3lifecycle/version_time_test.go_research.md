# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/version_time_test.go

## Purpose
This file tests version ID recency comparison used by lifecycle version ranking.

## Important APIs and helpers
Tests call `CompareVersionIds`, `isNewFormatVersionId`, and `getVersionTimestamp`. Constants define representative new-format and old-format 16-character hex prefixes. `uintToHex16` builds padded hex strings for synthesized equal-timestamp mixed-format cases.

## Control flow and state behavior under test
The suite asserts equality returns zero, `"null"` sorts older than real version IDs, smaller new-format prefixes are newer because timestamps are inverted, larger old-format prefixes are newer because timestamps are raw, and mixed old/new formats compare derived timestamps. It constructs a mixed-format equal timestamp pair and verifies comparison returns zero. It also pins rejection of too-short, null, and non-hex IDs, strict threshold behavior, zero timestamp on malformed inputs, raw old-format extraction, inverted new-format extraction, and ignored trailing suffixes after the first 16 hex characters.

## Dependencies and integration points
The tests use testify assertions and protect router ranking logic in `router.go`.

## Risks and gaps
These are unit tests against the duplicated lifecycle implementation. They do not automatically compare against the source implementation in `s3api_version_id.go`, so future drift between packages could still occur unless both suites are updated.

## Test signals
The suite is comprehensive for documented branches and directly guards lifecycle retention ordering for same-second version mtimes.
