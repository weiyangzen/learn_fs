# sources/cloud-native/buildkit/util/wildcard/wildcard_test.go

## Purpose
test coverage for the adjacent package behavior, using table tests, integration sandboxes, or worker execution helpers depending on package.

## Important APIs, Types, Functions, Or Configuration
package wildcard; functions/methods TestWildcard, TestWildcardInvalid, TestWildcardEscape, TestWildcardParentheses; tests TestWildcard, TestWildcardInvalid, TestWildcardEscape, TestWildcardParentheses.

## Control Flow And Integration Points
The file is 52 lines in wildcard and participates in this package role: Wildcard matching helper that translates BuildKit wildcard strings into anchored regular expressions and exposes captured substitutions. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are matching/formatting callers that use * captures. Risks include greedy regexp behavior, invalid ** handling, and replacement semantics; unit tests cover escaping and formatting.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: testing, github.com/stretchr/testify/assert, github.com/stretchr/testify/require. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. Direct test functions in this file: TestWildcard, TestWildcardInvalid, TestWildcardEscape, TestWildcardParentheses.
