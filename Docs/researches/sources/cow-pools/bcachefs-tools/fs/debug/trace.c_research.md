# File Research: sources/cow-pools/bcachefs-tools/fs/debug/trace.c

## Purpose

Instantiates bcachefs tracepoints.

## Behavior

Includes required bcachefs types and subsystem headers, defines `CREATE_TRACE_POINTS`, then includes `debug/trace.h`. This causes the tracepoint declarations in the header to emit definitions in this compilation unit.

## Dependencies

Pulls in alloc, btree cache/iter/key-cache/locking/interior, keylist, move types, six locks, and Linux blktrace API so tracepoint argument types and helpers are visible.

## Notes

There is no runtime logic beyond tracepoint definition instantiation.
