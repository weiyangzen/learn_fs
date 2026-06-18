# sources/cloud-native/containerd/internal/failpoint/fail.go

## Purpose
Implements configurable failpoints for tests and fault-injection paths, inspired by FreeBSD fail(9).

## Important APIs, Types, And Functions
`Type` enumerates off, error, panic, and delay actions. `Failpoint` stores a function name and ordered `failpointEntry` terms. `NewFailpoint`, `Evaluate`, `DelegatedEval`, and `Marshal` are public. Parsing helpers handle `count*type(arg)->...` term strings.

## Control Flow
Evaluation locks the failpoint, finds the first entry with remaining count, decrements it, unlocks, then executes the selected action. Cascading terms allow off/delay/error/panic sequences.

## State And Persistence
Entry counts are mutable in-memory state and are serialized by `Marshal`. There is no global registry or file persistence.

## Dependencies And Integration Points
Uses parsing primitives from bytes/strings/strconv, synchronization, and time sleeps. It can be embedded at selected code points where callers decide whether to trigger delegated errors.

## Risks
Malformed terms return parse errors, but map iteration in `parseType` relies on non-overlapping prefixes. Delay failpoints block the caller. Panic actions intentionally crash the evaluated path.

## Test Signals
`fail_test.go` covers parse errors, cascading terms, evaluate sequencing, delay duration, panic, and final marshaled counts.
