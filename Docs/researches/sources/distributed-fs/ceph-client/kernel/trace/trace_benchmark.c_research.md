# sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.c

## Purpose
`trace_benchmark.c` implements the runtime side of the `benchmark_event` tracepoint. When that tracepoint is enabled, it starts a kernel thread that continuously emits the tracepoint and measures the time spent writing it, producing rolling latency statistics in the next tracepoint payload.

## Important APIs, types, and functions
The main functions are `trace_do_benchmark()`, `benchmark_event_kthread()`, `trace_benchmark_reg()`, `trace_benchmark_unreg()`, and `ok_to_run_trace_benchmark()`. Global state includes `bm_event_thread`, the formatted payload buffer `bm_str`, counters and accumulators (`bm_total`, `bm_totalsq`, `bm_last`, `bm_max`, `bm_min`, `bm_first`, `bm_cnt`, `bm_avg`, `bm_std`, `bm_stddev`), and `ok_to_run`.

## Control flow
`TRACE_EVENT_FN` in the header wires tracepoint registration to `trace_benchmark_reg()` and unregistration to `trace_benchmark_unreg()`. Registration refuses command-line startup before `early_initcall` sets `ok_to_run`, then starts `event_benchmark`. The thread waits 100 ms, then loops until `kthread_should_stop()`, calling `trace_do_benchmark()` and `cond_resched_tasks_rcu_qs()`. The benchmark path checks that the tracepoint is enabled and tracing is on, disables local IRQs, records `trace_clock_local()` before and after `trace_benchmark_event()`, then updates statistics and formats the next message.

## State and persistence behavior
All benchmark statistics are static in-memory state. `trace_benchmark_unreg()` stops the thread and resets the payload and counters, so disabling the tracepoint clears history. The first sample is treated separately as cold-cache data and is not folded into the hot-path average.

## Dependencies and integration points
The file depends on `trace_benchmark.h`, tracepoint generated helpers, kthreads, local trace clock, `tracing_is_on()`, scheduler quiescent-state reporting for RCU tasks, and module/kernel thread infrastructure. It integrates with tracefs through the tracepoint enable count rather than its own files.

## Risks
This intentionally burns CPU while enabled; incorrect enable checks could create unexpected load. Statistics can overflow or become meaningless after very large sample counts, so the code freezes average/stddev updates after `bm_cnt > UINT_MAX`. IRQ disabling around the tracepoint narrows the measured region but also makes recursion and latency behavior important.

## Test signals
Enable `benchmark:benchmark_event`, read `trace_pipe`, confirm the kthread appears and disappears on enable/disable, verify the first payload is marked cold cached, and check that `last`, `max`, `min`, `avg`, and `std` evolve without warnings or stalls.
