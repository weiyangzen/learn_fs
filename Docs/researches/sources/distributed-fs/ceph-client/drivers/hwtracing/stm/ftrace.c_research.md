
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/ftrace.c

Purpose: STM source that exports kernel ftrace records to a linked STM device.

Important APIs/types/functions: static `stm_ftrace` embeds `stm_source_data` and `struct trace_export`. `stm_ftrace_write()` sends trace records using CPU-indexed channels. Link/unlink callbacks register/unregister the ftrace export. Init sets `nr_chans` to a power-of-two number of possible CPUs.

Control flow: when the source is linked to an STM device, it registers a trace export for functions, events, and markers. Trace callbacks run with preemption disabled and write to `STM_FTRACE_CHAN + cpu`, relying on the source's channel allocation width to cover CPUs.

State and persistence: one static source/export object; active only while linked.

Dependencies and integration: depends on `CONFIG_TRACING`, trace export APIs, STM source APIs, and STM policy allocation wide enough for all possible CPUs.

Risks: high-frequency trace path must remain `notrace` and low overhead. Channel count grows with `num_possible_cpus()` and may fail on devices/policies with too few channels. CPU-indexed channel mapping assumes stable CPU IDs below allocated width.

Test signals: link ftrace source, enable function/event tracing, confirm per-CPU channel output, test large CPU-count systems, unlink under active tracing, and use `p_sys-t` ftrace-compatible SBD path.
