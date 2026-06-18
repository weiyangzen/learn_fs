# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-slice-hist.py

Purpose: `rseq-slice-hist.py` is an offline trace analysis helper for rseq time-slice extension experiments. It reads `trace.dat` produced by `trace-cmd` hrtimer events and prints per-task histograms for rseq slice timer cancellation latency and expiration.

Important APIs, types, and functions: it imports `tracecmd.Trace`, defines `load_kallsyms()`, `OnlineHarmonicMean`, `handle_start()`, `handle_cancel()`, and `handle_expire()`. Global dictionaries `pending`, `histograms`, and `ohms` track outstanding timers, latency buckets, and per-command harmonic means.

Control flow: at startup it loads `/proc/kallsyms`, opens `trace.dat`, iterates events per CPU, and routes `hrtimer_start`, `hrtimer_cancel`, and `hrtimer_expire_entry` records. Starts whose function symbol contains `rseq_slice_expired` enter `pending`. Cancels compute duration and bucket counts. Expirations add an `EXPIRED` bucket.

State and persistence: state is in memory only and is keyed by hrtimer pointer and task command name. The script reads but does not modify kernel symbol state or trace files.

Dependencies and integration points: it depends on the Python `tracecmd` module, a readable `trace.dat`, and optionally readable `/proc/kallsyms`. It is complementary to `slice_test.c` and the comment documents the intended `trace-cmd record` invocation.

Risks and test signals: direct `ksyms[addr]` lookup can raise `KeyError` if symbols are unavailable or addresses are hidden. `handle_expire()` records histograms but not harmonic means, while the final print unconditionally reads `ohms[comm]`, so tasks with only expirations can fail. Useful output is a populated histogram with latency buckets and mean values.
