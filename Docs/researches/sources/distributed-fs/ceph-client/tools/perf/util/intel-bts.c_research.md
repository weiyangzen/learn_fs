# sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.c

Purpose: implements perf auxtrace support for Intel Branch Trace Store (BTS). It consumes AUX trace buffers containing fixed-size branch records, orders them, decodes source instructions when possible, feeds thread-stack call/return tracking, and synthesizes perf branch samples or auxtrace errors.

Important APIs and types: `struct intel_bts` owns auxtrace callbacks, queues, heap, PMU metadata, TSC conversion, synthesis options, branch event metadata, and event counters. `struct intel_bts_queue` tracks one auxtrace queue's current buffer, thread identity, CPU, instruction decode cache, and sample flags. `struct branch` is the on-trace record with little-endian `from`, `to`, and `misc`. The public entry point is `intel_bts_process_auxtrace_info()`.

Control flow: auxtrace-info parsing allocates `intel_bts`, installs callbacks into `session->auxtrace`, reads private metadata, configures itrace synth options, synthesizes a branch event if requested, and processes indexed queues. AUXTRACE events add buffers unless index data has already populated queues. Ordered perf events call `intel_bts_process_event()`, which converts event time to TSC, updates queues, drains heap entries up to that timestamp, flushes on thread exit, and reports lost trace on truncated AUX. Buffer processing maps data, optionally removes snapshot overlap, walks branch records, decodes instruction type through the Intel PT instruction decoder, updates thread-stack state, filters by call/return options, and delivers synthetic samples.

State and persistence: queue state persists across ordered events through `auxtrace_queue->priv`. Heap ordering persists pending buffer references. Snapshot overlap mutates `use_data/use_size`; data mappings are dropped after processing. No durable writes are made.

Dependencies and integration: depends on perf auxtrace queues/heaps, sessions, evlists, evsels, machines, threads, `thread-stack`, synthetic events, TSC conversion, and `intel-pt-insn-decoder`.

Risks: requires ordered events; split buffers are unsupported; instruction lookup can fail and optionally emits errors; overlap removal is byte-pattern based; no KVM support is noted by using host machine only. Endian conversion is manual for trace records.

Test signals: decode BTS samples with branch synthesis on/off, snapshot overlap fixtures, truncated AUX error delivery, thread-exit flushing, call/return filtering, big-endian record conversion, and instruction lookup failure paths.
