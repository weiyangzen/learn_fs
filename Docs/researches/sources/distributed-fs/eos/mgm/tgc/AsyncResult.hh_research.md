# sources/distributed-fs/eos/mgm/tgc/AsyncResult.hh

## Purpose
`AsyncResult.hh` defines a small templated value object used to report the poll result of an asynchronous task that may still be running. It distinguishes pending-without-cache, pending-with-previous-value, successful value, and error states.

## Important APIs, Types, And Functions
`AsyncResult<Value>` contains enum `State`, `stateToStr()`, factory methods `createPendingAndNoPreviousValue()`, `createPendingAndPreviousValue()`, `createValue()`, and `createError()`, plus accessors `getState()`, `getPreviousValue()`, `getValue()`, and `getError()`. Values and errors are stored as `std::optional`.

## Control Flow
Construction is private so callers must use factory methods, which set exactly one state and populate the associated optional when appropriate. Consumers switch on `getState()` and then inspect the matching optional.

## State And Persistence
The object has no external persistence and owns only copied optionals. State is immutable by convention after factory construction, although the fields are not `const`.

## Dependencies And Integration Points
This template is used by `AsyncUint64ShellCmd` and `SmartSpaceStats` to poll an optional `tgc.freebytesscript` without blocking the main stats path. It depends only on EOS namespace macros, `<optional>`, and `<string>`.

## Risks And Edge Cases
The type does not enforce state/optional consistency beyond its factory methods; future direct member changes would be unsafe. Accessors return optionals by value, which is simple but copies large value types if instantiated with non-trivial payloads. The default branch in `stateToStr()` is defensive but should be unreachable.

## Test Signals
Tests should verify each factory's state and optional contents, string conversion for all enum values, and consumer behavior when pending states are returned with or without previous values.
