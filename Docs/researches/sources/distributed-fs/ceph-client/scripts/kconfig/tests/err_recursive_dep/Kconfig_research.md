# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/Kconfig

## Purpose
This fixture defines multiple invalid recursive dependency patterns that Kconfig must reject.

## Important APIs, Types, and Functions
It covers self-dependency (`A depends on A`), self-select (`B select B`), mutual depends (`C1`/`C2`), depends plus select (`D1`/`D2`), depends plus imply (`E1`/`E2`), default dependency (`F1`/`F2`), and a menu depending on its own content (`G`).

## Control Flow
During post-parse dependency validation, `sym_check_deps()` should find recursion and emit diagnostics.

## State and Persistence
No persistent state beyond a failed temporary config run.

## Dependencies and Integration Points
Targets symbol dependency graph traversal and diagnostic formatting.

## Risks and Edge Cases
The fixture contains several independent recursive cases; diagnostic ordering can be implementation-dependent.

## Test Signals
The paired test expects `oldaskconfig()` to fail with stderr matching `expected_stderr`.
