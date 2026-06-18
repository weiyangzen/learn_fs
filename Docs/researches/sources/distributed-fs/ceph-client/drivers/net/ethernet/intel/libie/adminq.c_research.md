# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/adminq.c

## Purpose
`adminq.c` provides a small admin queue error-code-to-string helper for Intel Ethernet drivers.

## Important APIs, Types, and Functions
`libie_aq_str(enum libie_aq_err err)` returns a symbolic string for known `LIBIE_AQ_RC_*` codes and falls back to `LIBIE_AQ_RC_UNKNOWN`. It is exported in the `LIBIE_ADMINQ` namespace.

## Control Flow
The function bounds-checks the enum and verifies that a string exists at that index; invalid or sparse values map to the final unknown entry.

## State and Persistence Behavior
The only state is a static const string table. No mutable runtime state.

## Dependencies and Integration Points
Depends on `<linux/net/intel/libie/adminq.h>` for the enum. Used by drivers or libraries that need stable admin queue diagnostics.

## Risks and Edge Cases
The array must remain synchronized with enum values. Sparse enum values are handled by null-entry fallback if the table has holes.

## Test Signals
Unit-style checks for each known admin queue code, out-of-range values, and sparse/unassigned values returning unknown.
