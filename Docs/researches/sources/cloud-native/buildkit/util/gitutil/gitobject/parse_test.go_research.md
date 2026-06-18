## sources/cloud-native/buildkit/util/gitutil/gitobject/parse_test.go

Purpose: validates raw Git object parsing, signed-data extraction, checksum verification, and actor parsing.

Important tests: `TestParseGitObject` parses a real signed merge commit with two parents and a signed tag, verifies SHA-1 checksums, signature block normalization, `SignedData` exclusion/inclusion rules, header maps, `ToCommit`, `ToTag`, and wrong-type conversion errors. `TestParseActor` covers normal actors, missing/invalid timestamps, malformed timezone, missing brackets, extra spaces, and names containing `<`.

Dependencies: `crypto/sha1`, `testify/require`, time zones.

Risk/test signal: strong fixtures for PGP commit/tag formats and actor parsing. Gaps: no SHA-256 object fixture, no SSH signature fixture, no invalid required-header tests.
