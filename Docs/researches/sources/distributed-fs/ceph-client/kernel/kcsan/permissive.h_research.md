# sources/distributed-fs/ceph-client/kernel/kcsan/permissive.h

## Purpose
Contains optional permissive-mode rules that suppress selected noisy KCSAN reports without embedding those policy decisions in the core runtime.

## Important APIs, Types, and Functions
Defines `kcsan_ignore_address` and `kcsan_ignore_data_race`.

## Control Flow
If `CONFIG_KCSAN_PERMISSIVE` is disabled, helpers return false. If enabled, `kcsan_ignore_address` suppresses races on `current->flags`. `kcsan_ignore_data_race` suppresses plain read races on word-sized or smaller values when the observed change affects only one bit, except boolean-looking 0/1 changes.

## State and Persistence
No state; all decisions are derived from access parameters and config.

## Dependencies and Integration Points
Called from `core.c` during found-watchpoint and setup/value-change paths. Uses bit counting, current task state, and KCSAN access type flags.

## Risks
This intentionally creates false negatives to reduce noise. The comments emphasize that ignored races are not generally safe, and future bug patterns may be hidden by broad rules.

## Test Signals
`kcsan_test.c` includes a one-bit value-change test that expects no report only when permissive mode is enabled.
