# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-boottrace.sh

Purpose: bootconfig verification script that checks a rich tracing setup under `/sys/kernel/tracing`.

Important APIs, types, and functions: helper functions `compare_file()`, `compare_file_partial()`, `file_contains()`, and `compare_mask()` validate exact values, prefix/regex partials, grep containment, and CPU masks. It checks task and kprobe event filters/enables, synthetic event triggers, histogram triggers, tracing instances `foo` and `bar`, snapshot allocation, tracer options, buffers, clocks, and global initcall enablement.

Control flow: changes to `/sys/kernel/tracing`, defines helpers, executes a linear sequence of assertions, prints a failure message and exits 1 on the first mismatch, otherwise exits 0.

State and persistence: no intentional writes. It reads tracefs/procfs state left by bootconfig.

Dependencies and integration points: depends on tracefs mounted at `/sys/kernel/tracing`, bootconfig having set the expected tracing state, and shell tools `cat`, `sed`, and `grep`. It is intended for ktest bootconfig examples.

Risks: exact string comparisons are sensitive to kernel formatting and tracefs representation changes. Some grep patterns are unquoted as filenames/values and could be brittle. CPU mask comparison accepts leading zero/space formatting but still expects specific masks.

Test signals: exit status 0 means the boottrace bootconfig applied all expected events, instances, hist triggers, clocks, masks, and options.
