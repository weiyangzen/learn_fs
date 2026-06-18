# sources/distributed-fs/coda/coda-src/resolution/timing.cc

Purpose: implements a lightweight timestamp path recorder for resolution profiling. It records probe ids with time values and prints deltas between consecutive probes and from first to last probe.

Important functions: `tvaminustvb` subtracts timeval values with microsecond borrow handling. `timing_path::timing_path` allocates initial storage, `grow_storage` doubles capacity or allocates `TIMEGROWSIZE`, `insert` records the id and either `gettimeofday` or an optional `_NSC_TIMING_` hardware counter, and `postprocess` overloads write trace output to `stdout`, a `FILE *`, or an fd.

Control flow and state: callers insert probe ids through the `PROBE` macro in `timing.h`/`rvmrestiming.h`. Storage is process-local heap memory and is not synchronized. Output uses direct `write` calls after formatting into a fixed buffer.

Dependencies, risks, tests: depends on `coda_assert`, `sys/time`, optional ioctl counter support, and C string/memory functions. Risks include no locking, unchecked initial malloc before later assertion only on grow, fixed 256-byte output buffer, and old-style external `clockFD` declaration. Test with zero entries, one entry, growth beyond initial capacity, normal timeval borrow, `_NSC_TIMING_` wrap behavior if enabled, and concurrent-probe exclusion by caller.
