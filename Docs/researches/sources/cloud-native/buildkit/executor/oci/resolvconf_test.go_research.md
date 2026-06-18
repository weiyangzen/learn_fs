# Research: sources/cloud-native/buildkit/executor/oci/resolvconf_test.go

## Purpose
Tests for resolver generation.

## Important APIs, Types, and Functions
Temporary-root tests for DNS nameserver/search/options and fallback behavior.

## Control Flow
Calls helper and inspects written files.

## State and Persistence
Temporary files only.

## Dependencies and Integration Points
Depends on Go testing. Protects executor DNS setup.

## Risks and Edge Cases
Cannot emulate every host resolver distribution.

## Test Signals
`go test ./executor/oci` signal.
