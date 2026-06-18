## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-kmsg.c

### Purpose
`opal-kmsg.c` registers a kmsg dumper whose only job is to flush OPAL console output on panic so panic messages are not left buffered in firmware.

### Important APIs, Types, And Functions
The key functions are `kmsg_dump_opal_console_flush()` and `opal_kmsg_init()`. The file owns one static `struct kmsg_dumper` that calls `opal_flush_console(0)` for panic dumps.

### Control Flow
Initialization registers the dumper with `kmsg_dump_register()`. During dump callbacks it checks `detail->reason`; non-panic dumps return immediately because normal OPAL pollers should continue flushing. Panic dumps synchronously flush virtual terminal 0.

### State, Persistence, And Dependencies
There is no persistent state beyond kmsg dumper registration. It depends on the OPAL console flushing implementation in `opal.c` and the kernel kmsg dump framework.

### Integration Points
`opal_init()` installs this after creating other OPAL platform services. It complements `panic_flush_kmsg_start()` and the OPAL console backend by draining firmware state when the regular poll loop is no longer running.

### Risks
The code assumes vterm 0 is the relevant panic console. If firmware flush never completes, `opal_flush_console()` can spin in panic context. Registration failure only logs an error, leaving panic output dependent on the existing poll/console path.

### Test Signals
Test kmsg dumper registration, panic-only behavior, firmware with and without `OPAL_CONSOLE_FLUSH`, busy/partial console responses, and panic output visibility on OPAL-backed consoles.
