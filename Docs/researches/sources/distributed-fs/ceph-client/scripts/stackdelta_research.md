# sources/distributed-fs/ceph-client/scripts/stackdelta

Purpose: `stackdelta` compares two stack-usage reports produced by `stackusage` and prints size deltas for functions present in both reports.

Important APIs, types, and functions: `read_stack_usage_file()` reads lines split into file, function, size, and type; skips numeric-only GCC-generated names; strips suffixes after `.` from function names; strips line numbers from file names; and returns a hash keyed by `file\tfunction`. The main block requires two arguments, intersects keys, and prints old size, new size, and signed delta for changed entries.

Control flow: both files are read fully, common keys are sorted, and only nonzero deltas are emitted.

State and persistence: no writes except stdout.

Dependencies and integration points: companion to `stackusage`, useful for compiler/config/change impact analysis of stack usage.

Risks: stripping at the first dot collapses functions with meaningful dots and intentionally ignores inlining suffix differences. Functions that appear or disappear are not reported.

Test signals: compare small synthetic `.su` reports with common, changed, added, removed, numeric-suffix, and dotted function names.
