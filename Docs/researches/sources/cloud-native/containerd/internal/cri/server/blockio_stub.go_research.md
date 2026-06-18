# sources/cloud-native/containerd/internal/cri/server/blockio_stub.go

## Purpose

This non-Linux server helper disables block I/O annotation handling on unsupported platforms.

## Important APIs, Types, and Functions

`blockIOClassFromAnnotations` always returns an empty class and nil error.

## Control Flow

The method immediately returns with no annotation parsing.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and allows shared server code to call the helper without platform conditionals.

## Risks and Edge Cases

Blockio annotations are ignored outside Linux. Users may expect annotations to fail or warn, but this stub silently drops them.

## Test Signals

Non-Linux tests should confirm annotated containers still create and no blockio spec fields are applied.
