# sources/distributed-fs/eos/unit_tests/mgm/RecycleTests.cc

## Purpose
Tests recycle-bin date cutoff calculation and recycled-path demangling. It verifies user-visible recycle cleanup date strings and conversion from mangled recycle names back to original paths.

## Important APIs, types, and functions
The tests use `Recycle`, its fake/test clock, `Recycle::GetCutOffDate()`, policy field `mKeepTimeSec`, and static `Recycle::DemanglePath()`.

## Control flow
The cutoff test advances the clock to a fixed September 2025 timestamp, sets keep times for six months, one month, and one week, and asserts expected `YYYY/MM/DD` strings. Demangle tests reject empty or slash-containing recycle names, and decode `#:#` separators plus trailing file ids into original paths.

## State and persistence
State is test-clock time and policy keep duration. Production recycle paths are persisted in recycle namespace layouts, so demangling compatibility matters.

## Dependencies and integration points
Depends on Google Test/Mock and recycle internals. It integrates with recycle cleanup and restore/listing behavior.

## Risks and test signals
Date math uses fixed month approximations from policy seconds, not calendar-month semantics. Tests should also cover timezone boundaries, leap days, malformed suffix ids, names containing literal `#`, and demangling of file vs directory names.
