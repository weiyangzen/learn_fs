# sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil_test.go

## Purpose
Tests Docker build-context Git URL detection for explicit git transports, HTTP(S) `.git` URLs with fragments, legacy GitHub shorthand, and known invalid suffixes.

## Important APIs, Types, And Functions
Defines `gitUrls`, `incompleteGitUrls`, `invalidGitUrls`, and `TestIsGIT`, which exercises `IsGitURL`.

## Control Flow
The test loops accepted full Git URLs and legacy shorthand expecting true, then loops invalid HTTP(S) cases expecting false.

## State And Persistence
No state or filesystem access.

## Dependencies And Integration Points
Direct unit coverage for `urlutil.go`, indirectly protecting build context dispatch behavior.

## Risks And Test Signals
The test name uses `GIT` but only tests git classification, not `IsURL`. Coverage reflects compatibility examples rather than exhaustive URL syntax. Failures signal user-visible context-type detection changes.
