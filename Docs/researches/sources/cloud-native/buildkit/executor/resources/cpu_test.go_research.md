# Research: sources/cloud-native/buildkit/executor/resources/cpu_test.go

## Purpose
Unit tests for CPU cgroup resource parsing.

## Important APIs, Types, and Functions
Creates sample controller files and asserts the CPU parser populates expected typed fields.

## Control Flow
Uses temporary directories/files, calls the parser, and compares counters/optional pressure data.

## State and Persistence
Temporary test files only.

## Dependencies and Integration Points
Depends on Go testing and parser helpers. Protects resource reports consumed by executor recorders.

## Risks and Edge Cases
Synthetic fixtures do not cover every kernel variant.

## Test Signals
`go test ./executor/resources` signal.
