# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker_test.go

## Purpose
This test file validates checker construction, retry behavior, and internal check error handling.

## Important APIs, Types, and Functions
Tests target `New`, `Check`, and `check`. They monkeypatch `parser.New`, `parser.Parser.Parse`, `Checker.Output`, and rule `Validate` methods.

## Control Flow
Constructor tests simulate target remote failure, parser failure, source remote failure, source parser failure, and success. `TestCheck` simulates a retryable HTTPS connection error and confirms HTTP fallback, then a non-retryable parse error. `TestCheckInternal` covers cleanup failure, source parse failure, output failures, and rule validation failure.

## State, Persistence, and Dependencies
Most tests use temporary workdirs or invalid paths. No real registries or binaries are invoked due to monkeypatching. Dependencies include gomonkey, parser, remote, rule, syscall, and testify.

## Integration Points
These tests guard the orchestration layer without depending on parser/rule internals.

## Risks and Test Signals
Monkeypatch-heavy tests can miss integration mismatches between real parser output and rule inputs. They do not cover successful full validation with real image data.
