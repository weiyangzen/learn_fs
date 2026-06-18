# sources/cloud-native/moby/daemon/internal/usergroup/parser_test.go

## Purpose
Tests subordinate ID file parsing across comments and blank lines using the shared `moby/sys/user` parser.

## Important APIs, Types, And Functions
`TestParseSubidFileWithNewlinesAndComments` writes a temporary subuid-style file and calls `user.ParseSubIDFileFilter` for `dockremap`.

## Control Flow
The test file includes one ordinary range, a comment line, a blank line, and a target range. The test expects exactly one returned range with `SubID` 231072 and `Count` 65536.

## State And Persistence
Uses a temporary directory and file only.

## Dependencies And Integration Points
Although it does not call `parseSubuid` directly, it validates the parser behavior those helpers rely on.

## Risks And Test Signals
The test does not cover malformed lines, numeric-name matching, duplicate ranges, or the package constants pointing at `/etc/subuid` and `/etc/subgid`. Its signal is that comments and blank lines are tolerated.
