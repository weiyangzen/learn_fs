# sources/cloud-native/moby/daemon/server/middleware/debug_test.go

## Purpose
Tests redaction behavior for debug request logging.

## Important APIs, Types, And Functions
`TestMaskSecretKeys` calls the unexported `maskSecretKeys` helper with map structures.

## Control Flow
Table cases cover redacting `Data` in secret/config-style payloads, recursive masking of password/secret/jointoken/unlockkey/signingcakey fields, and case-insensitive matching.

## State And Persistence
The input maps are mutated in place and compared to expected maps. No logging or HTTP request handling is exercised.

## Dependencies And Integration Points
Uses gotest assertions. It guards the security-sensitive part of `DebugRequestMiddleware`.

## Risks And Edge Cases
The tests do not cover arrays even though `maskSecretKeys` supports them. They also do not verify middleware body preservation.

## Test Signals
Failures indicate potential debug-log secret leakage or intentional scrub-list changes.
