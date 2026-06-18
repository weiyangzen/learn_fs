# sources/cloud-native/buildkit/util/wildcard/wildcard.go

## Purpose
implementation file in the adjacent Go package, contributing the symbols and behavior listed below.

## Important APIs, Types, Functions, Or Configuration
package wildcard; types Wildcard, Match; functions/methods New, Wildcard2Regexp, String, Match, String, Format.

## Control Flow And Integration Points
The file is 88 lines in wildcard and participates in this package role: Wildcard matching helper that translates BuildKit wildcard strings into anchored regular expressions and exposes captured substitutions. Control flow should be read through the listed functions and methods; notable exported or lifecycle symbols are included above. Integration points are matching/formatting callers that use * captures. Risks include greedy regexp behavior, invalid ** handling, and replacement semantics; unit tests cover escaping and formatting.

## State, Persistence, Dependencies, Risks, And Test Signals
State and persistence are inferred from symbols and dependencies: globals/types/functions listed above, filesystem/process/network state where the APIs call external daemons or stores, and in-memory closure/mutex/channel state where concurrency helpers are present. Dependencies: external packages: regexp, strings, github.com/pkg/errors. Primary risks are package-specific integration coupling, platform/build-tag behavior where present, cleanup and cancellation boundaries for daemon/executor/tracing code, and stale assumptions in tests or constants. This is production/helper code; test signal comes from adjacent package tests and integration users.
