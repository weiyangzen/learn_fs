# sources/distributed-fs/ceph-client/kernel/locking/lockdep_states.h research

## Purpose
`lockdep_states.h` is a tiny X-macro list of lockdep IRQ usage states. It currently declares `HARDIRQ` and `SOFTIRQ`, and consumers expand each state into enum values, bitmasks, usage strings, character output, state names, and verbose handlers.

## Important APIs, Types, and Functions
The only interface is repeated invocation of `LOCKDEP_STATE(HARDIRQ)` and `LOCKDEP_STATE(SOFTIRQ)`. `lockdep_internals.h` expands these into `LOCK_USED_IN_*`, `LOCK_USED_IN_*_READ`, `LOCK_ENABLED_*`, and `LOCK_ENABLED_*_READ` enum values and masks. `lockdep.c` expands the same list into printable usage strings, usage characters, state name arrays, and per-state verbosity dispatch. `lockdep_proc.c` indirectly relies on these generated masks when counting hardirq/softirq safe and unsafe classes.

## Control Flow
This file has no standalone execution. It is included multiple times with different `LOCKDEP_STATE` definitions. The include style is intentional: consumers define the macro, include this file, and undefine the macro to keep one authoritative list of states.

## State and Persistence Behavior
There is no runtime state. Its contents define the shape of runtime state in lock classes: usage-mask width, trace arrays, printable usage character count, and proc statistics categories.

## Dependencies and Integration Points
It must stay synchronized with public lockdep constants, especially `XXX_LOCK_USAGE_STATES` in `include/linux/lockdep.h`, as the file comment warns. Adding a state affects lockdep bit layout, diagnostics, proc output, and any assertions that compare trace-state counts.

## Risks and Edge Cases
The risk is maintenance mismatch. Adding, deleting, or reordering states without updating public constants and auditing bit-layout assumptions can break IRQ inversion detection. Because the bit encoding is used arithmetically in `lockdep.c`, the generated order must preserve read and direction bit meanings.

## Test Signals
Build failures, static assertions, or malformed `/proc/lockdep` usage strings are immediate signals of an incorrect update. Runtime lockdep tests covering hardirq and softirq inversion should still produce coherent state names and usage characters after any change.
