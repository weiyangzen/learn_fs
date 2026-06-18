# sources/cloud-native/cri-o/internal/hostport/suite_test.go

## Purpose
Bootstraps the Ginkgo/Gomega hostport test suite.

## Important APIs, Types, And Functions
- `TestHostPort(t *testing.T)` registers fail handling and runs framework specs.
- Package global `t *TestFramework` is initialized by `BeforeSuite` and torn down by `AfterSuite`.

## Control Flow
Before the suite, a CRI-O test framework is created with no-op callbacks and setup is run. After the suite, teardown is run.

## State And Persistence
Holds package-global test framework state. Individual tests create fake in-memory iptables/nftables state; this file does not persist data.

## Dependencies And Integration Points
Integrates ONSI Ginkgo/Gomega with CRI-O's shared test framework for hostport tests.

## Risks And Edge Cases
Suite setup does not reset external kernel state because tests use fakes. Any future test using real netfilter state must handle its own isolation.

## Test Signals
Provides test runner plumbing only.
