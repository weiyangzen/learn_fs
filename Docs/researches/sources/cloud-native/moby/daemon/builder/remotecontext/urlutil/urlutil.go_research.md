# sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil.go

## Purpose
Classifies docker build context strings as HTTP(S) URLs or remote Git repository references using Docker-specific compatibility rules.

## Important APIs, Types, And Functions
Exports `IsURL` and `IsGitURL`. Uses lazy regexp `urlPathWithFragmentSuffix` for `.git` suffixes with optional fragments.

## Control Flow
`IsURL` checks literal `https://` or `http://` prefixes without URL parsing. `IsGitURL` returns true for HTTP(S) strings ending in `.git` plus optional fragment, and for legacy prefixes `git://`, `github.com/`, and `git@`.

## State And Persistence
No persistent state beyond the compiled lazy regexp.

## Dependencies And Integration Points
Used by Docker build context resolution before deciding whether to clone, download, or treat input as a local path. It intentionally is not a general URL validator.

## Risks And Test Signals
Rudimentary prefix checks can classify malformed strings as git or ignore valid but unsupported forms. The `github.com/` legacy path requires callers to check local existence first. `urlutil_test.go` guards known accepted and rejected patterns.
