# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall_inst.c

Purpose: Implements debugfs hcall instrumentation by recording per-CPU, per-hcall counts and time totals from hcall tracepoints.

Important APIs/types/functions: Defines `struct hcall_stats`, per-CPU `hcall_stats[HCALL_STAT_ARRAY_SIZE]`, seq_file operations, trace probes `probe_hcall_entry()` and `probe_hcall_exit()`, and init `hcall_inst_init()`.

Control flow: Init on LPAR registers hcall entry/exit trace probes and creates debugfs directory `hcall_inst` with one file per possible CPU. Entry probe records timebase and PURR start for the opcode slot. Exit probe increments call count and accumulates elapsed timebase and PURR. Seq output skips zero-count hcalls and prints opcode, calls, TB total, and optionally PURR total.

State and persistence: Persistent state is per-CPU stats arrays. Probe start fields are overwritten on each hcall entry per opcode and CPU. Debugfs files reference the per-CPU arrays directly.

Dependencies and integration points: Depends on hcall tracepoints emitted by `hvCall.S`, debugfs, seq_file, firmware LPAR feature detection, timebase, PURR CPU feature, and pseries machine initcalls.

Risks: Nested or reentrant hcalls with the same opcode on one CPU would overwrite start timestamps. No debugfs reset operation is provided. Trace registration failure must unwind entry probe registration. PURR reads depend on CPU feature availability for display but are still accumulated.

Test signals: Enabling `CONFIG_HCALL_STATS`, debugfs `hcall_inst/cpuN` contents after hcall activity, tracepoint registration failure tests, CPU hotplug visibility, and comparison against ftrace hcall events are useful.

Source read size: 140 lines, 3297 bytes.
