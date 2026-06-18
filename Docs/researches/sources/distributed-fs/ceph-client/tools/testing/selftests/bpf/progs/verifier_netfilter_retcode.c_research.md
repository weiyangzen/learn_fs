# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_retcode.c

## Purpose
This file tests netfilter BPF return-code validation. Netfilter programs must return a known value in the accepted range.

## Important APIs, Types, And Functions
It uses four `SEC("netfilter")` naked programs with success/failure annotations and inline return values.

## Control Flow
The first test returns an unknown context-derived value and fails. The next two return constants `0` and `1` and pass. The final test returns `2` and fails range validation.

## State And Persistence
No persistent state exists. Verifier state tracks whether `R0` is known at exit and whether its signed range is within `[0, 1]`.

## Dependencies And Integration Points
It integrates with netfilter program-type metadata and verifier exit-state checks.

## Risks
Allowing unknown or out-of-range return values could confuse netfilter verdict handling.

## Test Signals
Expected messages include `R0 is not a known value` and `R0 has smin=2 smax=2 should have been in [0, 1]`.
