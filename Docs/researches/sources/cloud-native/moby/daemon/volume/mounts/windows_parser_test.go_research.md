# sources/cloud-native/moby/daemon/volume/mounts/windows_parser_test.go

## Purpose
Unit tests for Windows raw mount parsing and structured validation.

## Important APIs, Types, And Functions
Tests include `TestWindowsParseMountRaw`, `TestWindowsParseMountRawSplit`, `TestWindowsValidateMounts`, and `TestWindowsParseMountSpecBindWithFileinfoError`.

## Control Flow
Raw tests cover drive roots, long paths, paths with spaces, named volumes, mixed-case modes, forward slash normalization, named pipes, invalid punctuation, reserved names, root C drive destination rejection, missing sources, file sources, and invalid pipe targets. Split tests compare complete `MountPoint` structs for bind, volume, read-only, driver, and pipe cases. Structured tests validate bind, anonymous volume, invalid sources/types, and provider error propagation.

## State And Persistence
No persistent state; mock file provider supplies deterministic Windows paths.

## Dependencies And Integration Points
Depends on Windows parser, shared mocks, Docker API mount types, cmp options, and assertion helpers.

## Risks
Most paths are syntactic mocks rather than real Windows filesystem state. The tests intentionally document compatibility quirks such as destination/mode ambiguity.

## Test Signals
Strong signal for Windows mount-spec grammar, reserved-name handling, named pipe validation, and stat error fidelity.
