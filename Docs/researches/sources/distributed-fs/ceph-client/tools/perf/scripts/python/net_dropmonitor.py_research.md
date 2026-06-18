# sources/distributed-fs/ceph-client/tools/perf/scripts/python/net_dropmonitor.py

Purpose: `net_dropmonitor.py` counts packet drops by `skb:kfree_skb` location and resolves those locations to kernel symbols at report time.

Important APIs and state: globals `drop_log` and `kallsyms` hold location counters and sorted symbol addresses. `get_kallsyms_table` reads `/proc/kallsyms`; `get_sym` performs a binary predecessor search; `print_drop_table` formats the report; `skb__kfree_skb` is the tracepoint callback.

Control flow: `trace_begin` prints a start message. Each `skb__kfree_skb` event stringifies the `location` field and increments its count. `trace_end` loads and sorts kallsyms, then prints one row per recorded location with nearest symbol, offset, and count.

State and persistence: the script does not persist across runs. It reads `/proc/kallsyms` once at the end and emits stdout only.

Dependencies, integration, risks, and tests: it depends on perf Python trace modules, the `skb:kfree_skb` tracepoint signature, and kallsyms readability. Kernel address restrictions can leave symbols unresolved or zeroed. It counts all kfree_skb events, so current kernels with explicit drop reasons may need reason-aware extension for richer analysis. Test signals include a trace with drops yielding nonzero rows and resolved symbol offsets.
