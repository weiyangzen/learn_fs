# sources/cloud-native/cri-o/server/metrics/collectors/collectors_test.go

Purpose: Ginkgo suite for collector-name normalization helpers.

Important APIs and functions: `TestCollectors`, suite setup/teardown with `TestFramework`, and specs for `Stripped`, `FromSlice`, and `ToSlice`.

Control flow: creates sample names with full, CRI-O-only, and no prefixes; asserts stripped output and containment semantics.

State and persistence: uses framework global state only; no external metrics registry is mutated by these tests.

Dependencies and integration: Ginkgo/Gomega, CRI-O test framework, and the collectors package under test.

Risks: does not assert `All()` contents or every real collector constant, so additions can miss test coverage.

Test signals: good focused coverage for the name-normalization contract used by metrics configuration.
