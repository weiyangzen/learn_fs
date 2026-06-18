# sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/BalancerEngineTypeTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/BalancerEngineTypeTests.cc

Purpose: validates string-to-`GroupStatus` conversion for group-balancer status labels.

Important APIs and types: `getGroupStatus`, `GroupStatus::ON`, `GroupStatus::DRAIN`, and `GroupStatus::OFF`. It uses both compile-time `static_assert` with string literals and runtime assertions with `std::string`, `const char*`, and string-view-like inputs.

Control flow: compile-time checks ensure constexpr conversion works for `"on"`, `"drain"`, and unknown values. Runtime checks exercise conversion overloads or implicit conversions.

State and persistence: none.

Dependencies and integration: depends only on `BalancerEngineTypes.hh` and GoogleTest. This is a guard for parsing config or group status text into balancer decisions.

Risks and test signals: unknown strings fall back to `OFF`, which is conservative but can hide malformed config unless higher-level validation reports it. Compile-time coverage is useful for refactors of constexpr parsing.
