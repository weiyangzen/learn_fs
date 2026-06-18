# sources/distributed-fs/ceph-client/arch/s390/kernel/debug.c

## Purpose
Implements the s390 debug feature (s390dbf), a per-component ring-buffer logging facility exposed through debugfs views. It supports raw hex/ascii, sprintf formatting, level and page controls, flushing, snapshots, and critical/oops behavior.

## Important APIs, Types, And Functions
Public APIs include `debug_register_mode()`, `debug_register()`, `debug_register_static()`, `debug_unregister()`, `debug_register_view()`, `debug_unregister_view()`, `debug_set_level()`, `debug_stop_all()`, `debug_set_critical()`, `debug_event_common()`, `debug_exception_common()`, `__debug_sprintf_event()`, `__debug_sprintf_exception()`, `debug_dump()`, `debug_dflt_header_fn()`, and `debug_sprintf_format_fn()`. Key state is `debug_info_t`, `debug_view`, and per-open `file_private_info_t`.

## Control Flow
Postcore init creates `/sys/kernel/debug/s390dbf` and registers sysctls. Components register debug areas, which allocate multi-area page rings and create debugfs files for default and custom views. Writes append event or exception records under raw spinlock; exception records advance to the next area. Opens create snapshots so reads are consistent. Control views parse writes to change level, page count, or flush areas.

## State And Persistence
State is in memory ring buffers, debugfs dentries, sysctl flags, linked debug-area list, refcounts, and per-open snapshots. There is no durable persistence, but static debug info can preserve early events until dynamic registration copies them.

## Dependencies And Integration Points
Depends on debugfs, sysctl, raw spinlocks, refcounts, TOD clock, SMP CPU IDs, copy_to/from_user, and s390 debug headers. Many s390 drivers and firmware paths use this for diagnostics.

## Risks And Edge Cases
Buffer resizing copies existing events and must not race writers. Critical mode uses trylock to avoid deadlocks after CPU-stop scenarios. `sprintf` view stores format pointers and long arguments, so callers must use stable format strings and compatible argument widths.

## Test Signals
Signals include debugfs read/write tests for all default views, concurrent logging and resize, static debug registration, oops path `debug_stop_all()`, critical mode behavior, and component users such as cert_store debug output.
