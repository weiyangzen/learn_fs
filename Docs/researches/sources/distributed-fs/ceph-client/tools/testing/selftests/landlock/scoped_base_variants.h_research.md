# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_base_variants.h

## Purpose

`scoped_base_variants.h` is a shared fixture-variant header for two-process Landlock scope tests. It defines all parent/child domain topologies needed to reason about whether access from P1 to P2 or P2 to P1 should be allowed.

## Important APIs, Types, and Functions

The header defines `FIXTURE_VARIANT(scoped_domains)` with `domain_both`, `domain_parent`, and `domain_child` booleans, plus eight `FIXTURE_VARIANT_ADD()` cases: `without_domain`, `child_domain`, `parent_domain`, `sibling_domain`, `inherited_domain`, `nested_domain`, `nested_and_parent_domain`, and `forked_domains`.

## Control Flow and State

It contains no executable runtime logic, but the booleans drive test control flow in ptrace, signal, and abstract UNIX socket tests. `domain_both` means a ruleset is applied before fork and inherited, while `domain_parent` or `domain_child` adds extra domains after fork in the corresponding process.

## Dependencies and Integration Points

It must be included after a fixture named `scoped_domains` is declared. It depends on kselftest harness macros and is source-included by several Landlock scope tests.

## Risks and Test Signals

The key risk is semantic drift between the diagrams and the booleans, which would invert expected allow/deny decisions across multiple tests. Test signals are the downstream fixture matrix expanding to all eight domain ancestry cases and producing consistent access results for ptrace, signals, and abstract sockets.
