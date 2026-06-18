# sources/compression/zstd/tests/cli-tests/bin/die

## Purpose

This helper terminates a CLI shell test with an error message.

## Important APIs, Types, and Functions

It calls `println "${*}"` to stderr and exits 1.

## Control Flow, State, and Persistence

The script always fails and has no persistent state.

## Dependencies and Integration Points

It depends on the sibling `println` helper being on `PATH`.

## Risks and Test Signals

It collapses all arguments into one string. The signal is simple: any path invoking `die` should mark the test failed with a visible diagnostic.
