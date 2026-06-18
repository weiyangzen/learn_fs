# sources/cloud-native/composefs/tests/test-should-fail.sh

## Purpose
This shell test verifies malformed dump fixtures are rejected by `mkcomposefs --from-file`.

## Important APIs, Types, And Functions
It sources `test-lib.sh`, loops over fixture paths, runs `mkcomposefs --from-file`, captures stderr, and asserts exit code `1`.

## Control Flow
For each fixture, successful image creation is a failure, non-1 failure exit is also a failure, and exit code 1 prints `ok`.

## State And Persistence
Uses one temporary directory removed by trap.

## Dependencies And Integration Points
Driven by `tests/meson.build` fixture list. Depends on built `mkcomposefs`.

## Risks
Only validates CLI exit code, not exact error messages. If CLI exit conventions change, this test needs updating.

## Test Signals
Important negative coverage for long links, invalid xattrs, oversized files, missing file types, empty or dot names, bad hardlinks, and oversized inline content.
