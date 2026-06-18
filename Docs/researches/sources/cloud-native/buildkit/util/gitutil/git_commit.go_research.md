## sources/cloud-native/buildkit/util/gitutil/git_commit.go

Purpose: validates whether a string is a lowercase Git object hash suitable for SHA-1 or SHA-256 commit IDs.

Important API: `IsCommitSHA(str string) bool` returns true only for length 40 or 64 and characters `0-9` or `a-f`.

Control flow/state: simple length and rune scan; stateless.

Integration points: used by Git fetch retry logic to identify commit refspecs and by URL/source handling that needs to distinguish refs from hashes. Risks: uppercase hex hashes are rejected even though Git may accept them; function name says commit SHA but validates only hash shape, not object existence/type. Test signals: `git_commit_test.go` covers valid SHA-1/SHA-256 lengths and invalid lengths/chars.
