# sources/distributed-fs/ceph-client/fs/jffs2/debug.h

## Purpose
`debug.h` centralizes JFFS2 debug configuration, message macros, and declarations/wrappers for sanity, paranoia, and dump helpers. It lets the filesystem compile most diagnostics away while keeping lightweight accounting sanity checks enabled by default.

## Important APIs, Types, And Functions
The header defines `jffs2_dbg()`, `JFFS2_ERROR()`, `JFFS2_WARNING()`, `JFFS2_NOTICE()`, `JFFS2_DEBUG()`, legacy `D1`/`D2` wrappers, subsystem-specific macros such as `dbg_fragtree`, `dbg_dentlist`, `dbg_noderef`, `dbg_inocache`, and `dbg_memalloc`, plus conditional wrappers around the `__jffs2_dbg_*` functions implemented in `debug.c`.

## Control Flow
Compile-time `CONFIG_JFFS2_FS_DEBUG` selects which message categories and heavy checks are active. Level 1 enables paranoia and dumps plus broad subsystem messages; level 2 adds more verbose fragment/readinode and memory allocation traces. Disabled categories route to `no_printk()` to preserve format checking without runtime output.

## State And Persistence Behavior
This header has no runtime state, but controls whether debug code inspects and asserts over in-core eraseblock, inode, node-ref, and fragment state. Its macros may turn validation calls into no-ops or into fatal checks depending on configuration.

## Dependencies And Integration Points
It depends on printk and scheduler task id APIs, and it is included through `nodelist.h`, making the debugging surface broadly available across JFFS2. `debug.c` supplies the backing implementations when enabled.

## Risks And Test Signals
Macro mistakes can silently remove checks or evaluate arguments differently between debug and non-debug builds. The `jffs2_dbg_dump_buffer` wrapper appears argument-sensitive and should be compile-tested when dumps are enabled. Test signals include clean builds for debug levels 0, 1, and 2, plus runtime validation that subsystem messages and sanity checks appear only under the intended configs.
