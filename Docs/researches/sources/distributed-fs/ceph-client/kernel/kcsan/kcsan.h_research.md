# sources/distributed-fs/ceph-client/kernel/kcsan/kcsan.h

## Purpose
Private KCSAN runtime header shared by core, debugfs, reporting, and tests. It centralizes runtime constants, counters, global knobs, and reporting interfaces.

## Important APIs, Types, and Functions
Defines `KCSAN_CHECK_ADJACENT`, `NUM_SLOTS`, `enum kcsan_counter_id`, and `enum kcsan_value_change`. Declares `kcsan_enabled`, delay knobs, `kcsan_counters`, IRQ trace helpers, debugfs report filter hook, and report producer/consumer functions.

## Control Flow
No direct control flow. It describes the communication contract: core records counters and calls report APIs; report code consults debugfs filters and value-change states; debugfs displays counters and can suppress reports.

## State and Persistence
Declares global state owned elsewhere. Counters and enable state persist for the boot only.

## Dependencies and Integration Points
Depends on `linux/kcsan.h` public definitions and task structures. It binds together `core.c`, `debugfs.c`, `report.c`, `encoding.h`, and tests.

## Risks
Counter or enum reordering must stay synchronized with `debugfs.c` names. Value-change semantics are used by report filtering and cannot be changed casually without altering user-visible report behavior.

## Test Signals
Debugfs counter output and KUnit report expectations validate the enum/API contract.
