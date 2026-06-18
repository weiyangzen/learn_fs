# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs.py

## Purpose

`sysfs.py` verifies that DAMON sysfs configurations are committed to live kernel DAMON contexts, using drgn to compare internal structures against Python model objects.

## Important APIs, Types, and Functions

It defines many assertion helpers for watermarks, quota goals, quotas, migrate destinations, filters, access patterns, schemes, monitoring attrs, targets, contexts, and kdamonds. It uses `_damon_sysfs`, `drgn_dump_damon_status.py`, JSON loading, and `subprocess`.

## Control Flow

The script starts a minimal kdamond, dumps and asserts it, replaces the context with a complex configuration containing attrs, pageout scheme, quota goal, temporal goal tuner, watermarks, migrate destinations, core/ops filters, and commits it. It then commits a minimum context, stops, starts a vaddr context with three shell targets, marks one target obsolete, commits, removes it from the expected model, and asserts live state.

## State and Persistence Behavior

It mutates DAMON sysfs and kdamond live state, writes `damon_dump_output`, and spawns shell processes as monitoring targets. It stores expected state in Python objects.

## Dependencies and Integration Points

It depends on `_damon_sysfs.py`, drgn, kernel debug info, DAMON sysfs commit support, and internal DAMON struct layout. It integrates sysfs ABI with live in-kernel object verification.

## Risks and Edge Cases

Missing drgn turns into failure after starting kdamond. Enum mapping typos in test expectations can produce false failures when kernel enums change. The obsolete target case depends on shell process lifetime and commit ordering.

## Test Signals

Failures print unexpected field names and JSON dumps, making mismatched committed state visible. Success means sysfs-staged attrs, schemes, filters, quotas, destinations, and target obsolescence reached live DAMON structures.
