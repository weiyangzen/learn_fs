# sources/cloud-native/moby/daemon/internal/system/chtimes_nowindows.go

## Purpose
Provides the non-Windows `setCTime` implementation for `Chtimes`.

## Important APIs, Types, And Functions
`setCTime(path string, ctime time.Time) error` always returns nil. Its comment explains that Unix create/change time behavior is updated as a side effect of modifying mtime, so no explicit creation-time call exists.

## Control Flow
There is no conditional behavior; every call is a no-op success.

## State And Persistence
No additional state is mutated beyond the preceding `os.Chtimes` call in `Chtimes`.

## Dependencies And Integration Points
Selected by the `!windows` build tag. It satisfies the shared `Chtimes` call site.

## Risks And Test Signals
The abstraction name says create time, but Unix exposes ctime as metadata change time rather than creation time on most filesystems. Tests for Unix focus on atime/mtime and do not verify birth time.
