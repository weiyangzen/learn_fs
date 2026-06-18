# sources/cloud-native/containerd/internal/cri/opts/spec_nonwindows.go

## Purpose

This file provides a non-Windows implementation of the Windows process argument spec option.

## Important APIs, Types, and Functions

`WithProcessCommandLineOrArgsForWindows` returns a spec option that fails with `errdefs.ErrNotImplemented`.

## Control Flow

The returned spec option immediately returns not implemented when applied. Normal non-Windows process argument composition is handled by callers using `WithProcessArgs` directly; this function only satisfies shared references to the Windows-specific API.

## State and Persistence Behavior

It does not mutate the spec because it returns before applying any process arguments.

## Dependencies and Integration Points

It is selected by `//go:build !windows` and lets shared code reference the Windows-named option while compiling on non-Windows platforms.

## Risks and Edge Cases

Windows `ArgsEscaped` semantics are intentionally ignored outside Windows. Cross-platform callers should only rely on Windows command-line behavior on Windows builds.

## Test Signals

Tests should confirm non-Windows callers do not accidentally use this Windows-specific option and that applying it returns `errdefs.ErrNotImplemented`.
