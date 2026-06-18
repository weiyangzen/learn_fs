# Research: sources/cloud-native/buildkit/executor/proxyca_linux_test.go

## Purpose
Tests for proxy CA injection helpers.

## Important APIs, Types, and Functions
Exercises PEM parsing, existing cert detection, bundle insertion, and cleanup removal.

## Control Flow
Builds sample cert data and compares helper output.

## State and Persistence
Temporary/in-memory state only.

## Dependencies and Integration Points
Depends on Go testing and x509/PEM. Protects proxy-network executor behavior.

## Risks and Edge Cases
Does not cover every distro bundle path/permission.

## Test Signals
Linux `go test` signal.
