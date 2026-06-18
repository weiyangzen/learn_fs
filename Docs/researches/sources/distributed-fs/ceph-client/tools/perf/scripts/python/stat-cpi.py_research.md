# sources/distributed-fs/ceph-client/tools/perf/scripts/python/stat-cpi.py

Purpose: `stat-cpi.py` computes cycles per instruction from `perf stat` interval callbacks for cycles and instructions events.

Important APIs and state: dictionaries and lists store event values by time, CPU, and thread. Event callbacks cover kernel, user, and generic cycles/instructions variants and normalize them to `"cycles"` or `"instructions"`. `stat__interval` prints CPI for every observed CPU/thread pair at a given interval.

Control flow: each stat callback calls `store`, which records the key dimensions and stores value/enabled/running data. `stat__interval` retrieves cycles and instructions for the interval, computes `cycles / instructions` when nonzero, and prints a timestamped line.

State and persistence: the script keeps all interval values in memory and does not clear old data. It prints interval results immediately and `trace_end` is a no-op.

Dependencies, integration, risks, and tests: it depends on perf stat Python callback naming and both cycles and instructions being present for each CPU/thread/time combination. Missing keys raise exceptions. It ignores enabled/running scaling despite storing those values. Test signals are interval perf stat runs that include cycles and instructions and produce expected CPI rows.
