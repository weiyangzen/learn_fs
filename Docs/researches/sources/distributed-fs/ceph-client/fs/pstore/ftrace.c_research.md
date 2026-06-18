# sources/distributed-fs/ceph-client/fs/pstore/ftrace.c

## Purpose
`ftrace.c` records function trace records into the active pstore backend and exposes a debugfs knob to enable or disable recording.

## Important APIs, types, and functions
Key functions are `pstore_register_ftrace`, `pstore_unregister_ftrace`, `pstore_set_ftrace_enabled`, `pstore_ftrace_call`, `adjust_ip`, `decode_ip`, and `pstore_ftrace_combine_log`. State includes `pstore_ftrace_ops`, `record_ftrace`, `pstore_ftrace_lock`, `pstore_ftrace_stamp`, and the debugfs directory.

## Control flow
Registration creates `/sys/kernel/debug/pstore/record_ftrace`, optionally registers global ftrace ops, and writes each callback as a `PSTORE_TYPE_FTRACE` record through `psinfo->write`. The callback avoids oops recursion, disables local IRQs while creating the record, stores CPU and timestamp metadata, and lets the backend choose the zone.

## State and persistence
Runtime state is the enable flag and timestamp counter. Persistence is delegated to the backend ftrace storage. KASLR-aware address adjustment supports decoding after reboot.

## Dependencies and integration points
It depends on function tracer internals, debugfs, pstore frontend records, SMP CPU encoding helpers, and optional KASLR built-in address handling.

## Risks and test signals
Risks include recursion, tracing during unstable oops paths, timestamp races by design, KASLR address decode errors, and memory allocation failures while combining per-CPU logs. Test signals include toggling the debugfs knob, per-CPU ftrace recovery, KASLR built-in boot, disabled backend write support, and trace ordering after merge.
