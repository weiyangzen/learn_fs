
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memcpy.c

## Purpose

This test checks the field-specific source-read overflow diagnostic for `memcpy()`.

## Important APIs, Control Flow, And State

`TEST` is `memcpy(large, instance.buf, sizeof(instance.buf) + 1)`. It reads one byte beyond the known struct field while writing into a large enough destination.

## Dependencies, Risks, And Test Signals

The integration point is fortify's distinction between whole-object and field-size checking. The expected warning/symbol is `__read_overflow2_field`, which catches field-local overreads even when surrounding struct storage exists.
