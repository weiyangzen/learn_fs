## sources/cloud-native/buildkit/util/gitutil/git_commit_test.go

Purpose: table-tests `IsCommitSHA`.

Important coverage: accepts 40-character SHA-1 and 64-character SHA-256 lowercase hex strings. Rejects empty, too-short/long, punctuation, and `z` characters at valid lengths.

Dependencies: `testify/assert`.

Risk/test signal: confirms current strict lowercase behavior but does not document whether uppercase should be accepted. No integration with actual git object lookup.
