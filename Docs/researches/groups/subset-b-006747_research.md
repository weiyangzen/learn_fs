# subset-b-006747 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/intel-pt-events.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/intel-pt-events.py

Purpose: `intel-pt-events.py` is a `perf script` Python report for Intel Processor Trace streams. It formats branch/instruction samples, PTWRITE, CBR, MWAIT, PWRE/PWRX, EXSTOP, PSB, EVT, IFLAG, auxtrace errors, and context-switch notifications into readable trace output.

Important APIs and state: the perf integration points are `trace_begin`, `trace_end`, `process_event`, `auxtrace_error`, and `context_switch`. It imports `perf_set_itrace_options`, `perf_sample_insn`, and `perf_sample_srccode` from perf's Python trace utilities and uses `LibXED` from `libxed.py` when instruction disassembly is requested. Global state tracks options, disassembler availability, previous source location, pending switch strings by CPU, interleaved output buffers by CPU, and the current event time.

Control flow: `trace_begin` parses script options, chooses an itrace mode (`bepwxI` for branch/event output or `i0nsepwxI` for instruction/source output), optionally initializes XED, and configures perf. `process_event` either handles the event directly or captures per-CPU output into stashes for timestamp-level interleaving. `do_process_event` dispatches by event name, decodes raw payloads with `struct.unpack_from`, prints common sample prefixes, and attaches symbol, DSO, source, instruction, IPC, and correlated address data when available.

Persistence and dependencies: it is stateful only for the life of the perf-script process and writes to stdout. It depends on `PERF_EXEC_PATH`, perf's Python helper modules, optional `libxed.so`, and sample dictionaries containing Intel PT synthetic event fields.

Integration, risks, and tests: this script is used through `perf script -s` and depends on kernel/perf field naming stability. Risks include optional raw fields missing on older perf versions, XED decode silently degrading to address-only output, `print_evt` reusing offset zero while iterating event-data records, and unbounded stashed output under large interleaved traces. Test signals are successful perf-script execution with branch, instruction, source, PTWRITE, power, auxtrace-error, VM, and context-switch samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/intel-pt-events.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/libxed.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/libxed.py

Purpose: `libxed.py` is a minimal ctypes wrapper around Intel XED for perf Python scripts that want x86 instruction disassembly without embedding XED bindings in perf itself.

Important APIs and types: `xed_state_t` mirrors the XED machine-mode state passed to `xed_operand_values_set_mode`. `XEDInstruction` owns a fixed-size decoded-instruction buffer, mode state, and output text buffer. `LibXED` loads `libxed.so`, binds the XED entry points, initializes tables, and exposes `Instruction`, `SetMode`, and `DisassembleOne`.

Control flow: `LibXED.__init__` first tries the dynamic linker path and then `/usr/local/lib/libxed.so`, assigns return and argument types for the used functions, and calls `xed_tables_init`. Callers allocate an `XEDInstruction`, set 32-bit or 64-bit mode, and pass bytes plus an IP to `DisassembleOne`. That method clears the decoded instruction while preserving mode, decodes bytes, formats AT&T syntax, decodes the output buffer for Python 3, and returns an instruction length plus text.

State and dependencies: all state is per-wrapper or per-instruction object. There is no persistent file output. The dependency is a compatible `libxed.so` ABI with symbols and layout matching this wrapper.

Integration, risks, and tests: `intel-pt-events.py` uses this helper opportunistically. The largest risk is ABI drift: decoded instruction length is read from hard-coded byte `166` in a 512-byte scratch buffer, so a future XED layout could return wrong lengths while still loading. Test signals are successful import, library load, and known-byte disassembly in instruction trace mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/libxed.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/mem-phys-addr.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/mem-phys-addr.py

Purpose: `mem-phys-addr.py` resolves perf samples with `phys_addr` into `/proc/iomem` ranges and prints a count/percentage table by memory-resource type.

Important APIs and state: `IomemEntry` is an immutable dataclass for begin/end/indent/label lines. Global containers hold ranges by indentation, parent-child edges, maximum indent, counted memory types, and the first event name. `parse_iomem`, `find_memory_type`, `print_memory_type`, `trace_begin`, `trace_end`, and `process_event` are the main functions.

Control flow: `trace_begin` parses `/proc/iomem`, discovering hierarchy by indentation and parent lookup. `process_event` ignores events without samples or without `phys_addr`, stores the first event name, finds the deepest matching range via `bisect_right` over sorted ranges, and increments the matching entry counter. `trace_end` rolls child counts into parents and recursively prints nonzero entries ordered by descending count.

State and persistence: state is process-local and accumulates for the full perf-script stream. The only external read is `/proc/iomem`; output is stdout.

Dependencies, integration, risks, and tests: it relies on Python dataclasses, `bisect` with a `key` argument, `/proc/iomem` readability, and perf sample dictionaries including physical addresses. Risks include requiring newer Python for `bisect(..., key=...)`, assertion failure if indentation hierarchy is unexpected, and division by zero when no counted samples exist. Test signals are samples from physical-address capable perf events producing a non-empty memory type table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/mem-phys-addr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/net_dropmonitor.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/net_dropmonitor.py

Purpose: `net_dropmonitor.py` counts packet drops by `skb:kfree_skb` location and resolves those locations to kernel symbols at report time.

Important APIs and state: globals `drop_log` and `kallsyms` hold location counters and sorted symbol addresses. `get_kallsyms_table` reads `/proc/kallsyms`; `get_sym` performs a binary predecessor search; `print_drop_table` formats the report; `skb__kfree_skb` is the tracepoint callback.

Control flow: `trace_begin` prints a start message. Each `skb__kfree_skb` event stringifies the `location` field and increments its count. `trace_end` loads and sorts kallsyms, then prints one row per recorded location with nearest symbol, offset, and count.

State and persistence: the script does not persist across runs. It reads `/proc/kallsyms` once at the end and emits stdout only.

Dependencies, integration, risks, and tests: it depends on perf Python trace modules, the `skb:kfree_skb` tracepoint signature, and kallsyms readability. Kernel address restrictions can leave symbols unresolved or zeroed. It counts all kfree_skb events, so current kernels with explicit drop reasons may need reason-aware extension for richer analysis. Test signals include a trace with drops yielding nonzero rows and resolved symbol offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/net_dropmonitor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/netdev-times.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/netdev-times.py

Purpose: `netdev-times.py` reconstructs RX and TX packet processing timelines from IRQ, softirq, NAPI, net, and skb tracepoints, making network device latency visible in a textual chart.

Important APIs and state: perf callbacks append normalized event tuples to `all_event_list`. Handler functions then correlate them into `irq_dic`, `net_rx_dic`, `receive_hunk_list`, `rx_skb_list`, `tx_queue_list`, `tx_xmit_list`, and `tx_free_list`. Options parsed from `sys.argv` select TX/RX output, device filtering, and debug buffer status.

Control flow: callbacks only collect event data. `trace_end` sorts collected events by timestamp and dispatches to handlers that build receive hunks around NET_RX softirq windows and transmit records from queue to xmit to free. RX output prints IRQ entry, netif_rx, softirq entry, NAPI poll, netif_receive_skb, copy, free, or consume events relative to the first IRQ timestamp. TX output prints queue-to-driver and driver-to-free latencies.

State and persistence: all correlation state is in memory. The script enforces fixed budgets for RX, TX queue, and TX xmit lists and increments overflow counters when old unmatched records are dropped.

Dependencies, integration, risks, and tests: it relies on perf's trace utility modules, symbol decoding for `NET_RX`, and tracepoint field compatibility across kernel versions. Risks include high memory use from `all_event_list`, fragile stack matching for nested IRQs, correlation loss under buffer overflow, and a comparator-style sort lambda that returns booleans rather than a three-way compare. Test signals are realistic RX/TX traces where skb addresses match across tracepoints and debug mode reports low overflow counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/netdev-times.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/parallel-perf.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/parallel-perf.py

Purpose: `parallel-perf.py` runs a `perf script` command many times in parallel by splitting input by CPU and/or time, writing each shard into a separate output directory.

Important APIs and types: `Verbosity` centralizes quiet/verbose/debug behavior. `Work` wraps a subprocess, optional pipe consumer, and `cmd.txt`/`out.txt`/`err.txt` paths. `OptPos` parses and optionally removes short and long perf options from an argv list. `CPUTimeRange` carries Intel PT density-splitting state. `ParallelPerf` coordinates parsing, header reads, split planning, self-checking, work creation, and execution.

Control flow: `Main` parses tool options and the perf command after `--`. `ParallelPerf.Config` finds the input file, reads `perf script --header-only`, extracts original command line, time bounds, and CPU bounds, chooses per-CPU defaults for Intel PT, splits time ranges by fixed count, fixed interval, or Intel PT double-quick sample density, verifies recombination, opens boundary ranges, and builds the worklist. `RunWork` keeps up to `--jobs` subprocesses active and kills outstanding work on failure.

State and persistence: persistent output is an output directory containing per-shard command, stdout, and non-empty stderr files. The script refuses to overwrite an existing output directory.

Dependencies, integration, risks, and tests: it depends on `perf script`, perf header field names, Python subprocess behavior, and command-line time/CPU syntax. Risks include assuming CPU is the first field in quick-output lines, treating any stderr as error after successful exit, fatal `grep`-style pipe consumers with no matches, and expensive pre-analysis on huge PT data. Test signals are dry-run command lists, self-test range recombination, successful shard completion, and expected directory trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/parallel-perf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/powerpc-hcalls.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/powerpc-hcalls.py

Purpose: `powerpc-hcalls.py` reports PowerPC hypervisor call latency statistics from `powerpc:hcall_entry` and `powerpc:hcall_exit` tracepoints.

Important APIs and state: `hcall_table` maps opcodes to names, `d_enter` tracks in-flight entry timestamps by CPU and opcode, and `output` stores total time, count, min, and max per opcode. Perf callbacks are `powerpc__hcall_entry`, `powerpc__hcall_exit`, and `trace_end`.

Control flow: entry events store `nsecs(sec, nsec)` under the event CPU and opcode. Exit events look for a matching entry on the same CPU/opcode, compute elapsed nanoseconds, update aggregate counters, and delete the in-flight entry. `trace_end` prints a fixed-width table with count, min, max, and average nanoseconds.

State and persistence: state is in memory only and is keyed by CPU, so nested or overlapping calls with the same opcode on one CPU would overwrite the prior entry. There is no file persistence.

Dependencies, integration, risks, and tests: it depends on perf Python `Core`/`Util`, PowerPC tracepoint availability, and stable opcode values. Risks include unmatched exits after dropped events, overwritten nested entries, unordered output, and integer opcode printing for unknown hcalls. Test signals are paired hcall traces producing nonzero aggregate rows with plausible latency ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/powerpc-hcalls.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/sched-migration.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/sched-migration.py

Purpose: `sched-migration.py` is a GUI-oriented toy analyzer that visualizes scheduler runqueue load, wakeups, migrations, and context switches over time.

Important APIs and types: event classes describe sleep, wakeup, fork, migrate-in/out, unknown, and snapshot states. `TimeSlice` captures per-CPU runqueue state over a timestamp interval, while `TimeSliceList` stores ordered slices and paints ranges through `SchedGui`. `SchedEventProxy` is the perf callback facade. Tracepoint callbacks route sched switch, migrate, and wakeup events into that proxy.

Control flow: `trace_begin` initializes the proxy. Each sched event obtains or creates a time slice for its timestamp and mutates runqueue state. Context switches check the expected current task, update thread names, mark previous task sleep/runnable state, and schedule the next task. Migrations move tasks between CPU queues. At `trace_end`, wxPython creates a `RootFrame` and enters the GUI main loop.

State and persistence: state is fully in memory and retained until the GUI closes. It does not write files; the persistent result is user inspection of the rendered timeline.

Dependencies, integration, risks, and tests: it depends on perf Python trace helpers, `SchedGui`, wxPython, and scheduler tracepoint fields. Risks include Python 3 division returning floats in binary search code, large trace memory use, GUI-only output unsuited to headless automation, and approximate runqueue reconstruction when trace events are missed. Test signals are a sched trace opening a responsive migration window and showing reasonable CPU load coloring and event summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/sched-migration.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/sctop.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/sctop.py

Purpose: `sctop.py` periodically displays syscall counts like a simple top-style view for perf syscall traces.

Important APIs and state: global `for_comm`, `interval`, and `syscalls` hold filter and count state. `trace_begin` starts a background thread running `print_syscall_totals`; syscall callbacks update counters for `raw_syscalls:sys_enter` or `syscalls:sys_enter`.

Control flow: argument parsing accepts optional command name and interval. The printer thread clears the terminal, prints sorted syscall counts, clears the counter map, sleeps, and repeats forever. Event callbacks filter by `common_comm` when requested and increment the syscall ID count.

State and persistence: counters are in memory and are periodically reset after display. There is no durable output.

Dependencies, integration, risks, and tests: it depends on perf Python trace helpers, `clear_term`, `syscall_name`, thread/_thread availability, and syscall tracepoints. Risks include unsynchronized access between printer and callback, no graceful thread termination, and terminal-oriented output that is awkward in non-interactive logs. Test signals are a live syscall trace refreshing at the requested interval and showing changing counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/sctop.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/stackcollapse.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/stackcollapse.py

Purpose: `stackcollapse.py` converts perf samples into folded stack lines suitable for flame graph tooling: `frame;frame;comm count`.

Important APIs and state: command options control PID/TID inclusion, comm inclusion, Java signature cleanup, and kernel annotation. `lines` is a `defaultdict(int)` keyed by folded stack string. `process_event` consumes perf sample dictionaries, and `trace_end` prints sorted results.

Control flow: each event builds a stack from `callchain` entries when present or from the sample symbol/DSO otherwise. `tidy_function_name` replaces semicolons, optionally tidies Java-style names, and annotates kernel kallsyms. The process name is appended as the logical root when enabled, optionally including pid/tid. The reversed stack string is counted. End-of-trace output is deterministic lexical order.

State and persistence: state accumulates in memory until `trace_end`; output is stdout only.

Dependencies, integration, risks, and tests: it depends on perf sample dictionaries with callchain entries, symbol names, DSO names, and sample PID/TID fields. Risks include memory growth proportional to distinct stacks, partial Java tidying, and `[unknown]` aggregation when symbols are missing. Test signals are folded-stack output accepted by flame graph tooling and stable counts for repeated stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/stackcollapse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/stat-cpi.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/stat-cpi.py

Purpose: `stat-cpi.py` computes cycles per instruction from `perf stat` interval callbacks for cycles and instructions events.

Important APIs and state: dictionaries and lists store event values by time, CPU, and thread. Event callbacks cover kernel, user, and generic cycles/instructions variants and normalize them to `"cycles"` or `"instructions"`. `stat__interval` prints CPI for every observed CPU/thread pair at a given interval.

Control flow: each stat callback calls `store`, which records the key dimensions and stores value/enabled/running data. `stat__interval` retrieves cycles and instructions for the interval, computes `cycles / instructions` when nonzero, and prints a timestamped line.

State and persistence: the script keeps all interval values in memory and does not clear old data. It prints interval results immediately and `trace_end` is a no-op.

Dependencies, integration, risks, and tests: it depends on perf stat Python callback naming and both cycles and instructions being present for each CPU/thread/time combination. Missing keys raise exceptions. It ignores enabled/running scaling despite storing those values. Test signals are interval perf stat runs that include cycles and instructions and produce expected CPI rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/stat-cpi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts-by-pid.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts-by-pid.py

Purpose: `syscall-counts-by-pid.py` summarizes syscall entry counts grouped first by command name and PID, then by syscall.

Important APIs and state: optional `for_comm` or `for_pid` filters are parsed from argv. `syscalls` is an auto-vivifying nested dictionary from comm to pid to syscall ID. `trace_begin`, `trace_end`, `raw_syscalls__sys_enter`, `syscalls__sys_enter`, and `print_syscall_totals` are the perf-facing functions.

Control flow: syscall-entry callbacks filter by command or PID and increment the nested count. The non-raw syscall callback delegates to the raw handler through `locals()`. At `trace_end`, output is sorted by syscall count within each comm/pid section and syscall IDs are resolved via `syscall_name`.

State and persistence: counts are in memory until the script exits or is interrupted, then printed to stdout. There is no external persistence.

Dependencies, integration, risks, and tests: it depends on perf Python trace helpers and syscall tracepoint signatures. Risks include command-name collisions across processes, non-deterministic comm/pid section order, and large memory use on long traces with many processes. Test signals are traces where a PID or comm filter reduces output and unfiltered runs show per-process syscall sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts-by-pid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts.py

Purpose: `syscall-counts.py` summarizes syscall entry counts across the whole trace, optionally filtered by command name.

Important APIs and state: `for_comm` holds the optional filter and `syscalls` maps syscall ID to count. Perf entry points are `trace_begin`, `trace_end`, `raw_syscalls__sys_enter`, `syscalls__sys_enter`, and `print_syscall_totals`.

Control flow: callbacks filter by `common_comm` and increment counts. At end, the script prints a count-sorted table of syscall names and totals. The `syscalls__sys_enter` handler delegates to the raw tracepoint handler through `locals()`.

State and persistence: state is process-local and printed once on exit; no files are written.

Dependencies, integration, risks, and tests: it depends on perf's syscall tracepoint callback contract and `Util.syscall_name`. Risks include aggregating across all PIDs for a shared comm, missing output until the script exits, and memory growth bounded by syscall ID variety rather than event count. Test signals are expected syscall totals from a known workload and correct optional comm filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/task-analyzer.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/task-analyzer.py

Purpose: `task-analyzer.py` analyzes `sched:sched_switch` traces, printing task runtime rows and optional summaries, extended inter-run timings, highlighting, filtering, and CSV exports.

Important APIs and types: `Task` records one scheduled-in interval. `Timespans` computes out-in, out-out, in-in, and in-out gaps between occurrences of the same task. `Summary` calculates per-TID runtime statistics and dynamic column alignment. Global `db` holds running tasks, completed tasks by CPU/TID, global order, and summary alignment metadata. Perf entry points are `trace_begin`, `trace_end`, and `sched__sched_switch`.

Control flow: `trace_begin` parses arguments, validates incompatible options, opens optional CSV files, disables colors when needed, initializes the database, and prints a trace header unless summary-only. Each switch converts raw sample time to `Decimal` seconds, applies the time window, finishes the previous PID on that CPU, and starts the next PID. Finish handling records PID from the sample, prints the row when not filtered, and indexes the task for summaries. `trace_end` emits summaries when requested.

State and persistence: running and historical task state is in memory. Optional CSV paths are opened for trace and summary output. Without `--summary`, record lists are trimmed to the latest item to reduce memory.

Dependencies, integration, risks, and tests: it depends on perf's scheduler tracepoint fields and raw sample time. Risks include open CSV descriptors not explicitly closed, use of `quit()` for time-window termination, possible `None` return from `_limit_filtered`, and sensitivity to missed switch-in events. Test signals are traces with known sched switches producing correct runtime rows, filters, highlights, CSV delimiters, and summary statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/task-analyzer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/api-io.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/api-io.c

Purpose: `api-io.c` tests perf's buffered `api/io.h` helpers for character, hexadecimal, decimal, and line reads.

Important APIs and state: helpers create temporary files, initialize `struct io`, and clean up buffers, descriptors, and paths. Macros `EXPECT_EQUAL` and `EXPECT_EQUAL64` mark failures while continuing within a case. The suite entry is `test__api_io`, registered as `"Test api io"`.

Control flow: `make_test_file` writes exact test contents to `/tmp/perf-test-XXXXXX`. `setup_test` opens it and initializes a caller-provided buffer size. Character tests iterate through multiple buffer powers to verify refill and EOF. Hex and decimal tests exercise delimiters, invalid leading characters, `0x`-style handling, oversized values, and EOF flags. Line testing verifies a line longer than the internal buffer and a final unterminated line.

State and persistence: temporary files are created and unlinked per case; heap buffers are freed. No durable state remains on success.

Dependencies, integration, risks, and tests: this is a direct perf test suite for `io__get_char`, `io__get_hex`, `io__get_dec`, and `io__getline`. Risks are mostly environment cleanup on early setup failures and assumptions about `/tmp`. Test signals are exact return values, parsed values, EOF flags, line lengths, and no leaked files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/api-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/backward-ring-buffer.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/backward-ring-buffer.c

Purpose: `backward-ring-buffer.c` verifies perf overwrite/backward ring-buffer reading for a tracepoint event.

Important APIs and state: `testcase` triggers `NR_ITERS` `prctl(PR_SET_NAME)` calls. `count_samples` reads `evlist->overwrite_mmap` and counts only `PERF_RECORD_SAMPLE` and `PERF_RECORD_COMM`. `do_test` mmap/enables/disables/reads a configured evlist. The suite is `"Read backward ring buffer"`.

Control flow: the test targets the current PID/TID, parses `syscalls:sys_enter_prctl/overwrite/`, configures mmap recording, opens the evlist, runs once with default mmap pages and checks exact sample and comm counts, then reopens and runs with one mmap page to exercise constrained backward-buffer behavior.

State and persistence: state is kernel perf event descriptors and mmaps owned by the evlist. They are opened, unmapped, closed, and deleted during the test. No files are written.

Dependencies, integration, risks, and tests: it depends on syscall tracepoints, sufficient permissions, and overwrite mmap support. It skips when tracepoint parsing fails, commonly without root or tracing access. Risks include exact count sensitivity to lost records or environment changes. Test signals are `NR_ITERS` sample records and `NR_ITERS` comm records in the first run and successful processing in the one-page run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/backward-ring-buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bitmap.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/bitmap.c

Purpose: `bitmap.c` tests bitmap string formatting used by perf utilities.

Important APIs and state: the file builds small static bitmap cases, formats them through perf's bitmap printing helper, and compares the resulting string with expected compact range/list syntax. The suite is registered as `"Print bitmap"`.

Control flow: the test populates bitmap words with selected bits, calls the formatting helper into a fixed buffer, and asserts the printed representation matches expected output. It covers empty/single/range/list style behavior rather than runtime perf events.

State and persistence: all state is stack-local test data; no file or kernel state is touched.

Dependencies, integration, risks, and tests: it depends on perf's bitmap helper and Linux bitmap primitives. Risks are mostly buffer-size assumptions and formatting contract churn. Test signals are exact string comparisons for representative bit patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bp_account.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/bp_account.c

Purpose: `bp_account.c` validates hardware breakpoint/watchpoint slot accounting when a watchpoint is modified into an instruction breakpoint.

Important APIs and state: `__event` creates `PERF_TYPE_BREAKPOINT` events through `sys_perf_event_open`; `wp_event` and `bp_event` select watchpoint or breakpoint setup. Detection helpers count available slots, check `PERF_EVENT_IOC_MODIFY_ATTRIBUTES`, and discover whether watchpoints and breakpoints share slots. The suite is `"Breakpoint accounting"`.

Control flow: unsupported architectures skip. The test detects watchpoint count, breakpoint count, modify-attributes support, and shared-slot behavior. It fills watchpoint slots, modifies the first event into a breakpoint, and when slots are separate, creates one more watchpoint to verify accounting was released or reclassified correctly.

State and persistence: state is kernel perf event file descriptors and debug-register allocation. All opened fds are closed.

Dependencies, integration, risks, and tests: it depends on hardware breakpoint support, perf_event permissions, default breakpoint length helpers, and architecture behavior. Risks include environment-specific slot counts, unsupported PowerPC/S390 paths, and failures when security policy blocks perf_event_open. Test signals are successful slot detection, successful modify ioctl, and no failed watchpoint creation after modification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bp_account.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal.c

Purpose: `bp_signal.c` tests signal delivery and resume-flag behavior for hardware breakpoint and watchpoint overflow notifications.

Important APIs and state: three global fds represent a breakpoint on `__test_function`, a breakpoint on the signal handler, and a watchpoint on `the_var`. `sig_handler` and `sig_handler_2` count nested notifications and disable events if recursion runs away. `__event` configures async perf events with `F_SETSIG` and `F_SETOWN`.

Control flow: after architecture support checks, the test installs SIGIO and SIGUSR1 handlers, creates the three events, enables them, and calls `test_function`. Expected execution triggers one primary breakpoint, nested handler breakpoints, and two watchpoint hits. It disables events, reads counts, closes fds, and validates counts and overflow counters exactly.

State and persistence: state is global counters and event descriptors for the test duration only. No files are written.

Dependencies, integration, risks, and tests: it depends on debug-register support, async signal delivery, architecture-specific inline assembly on x86_64, and perf_event permissions. Risks include flaky behavior under signal restrictions, unsupported architectures, and false failures if RF EFLAG or nested signal behavior changes intentionally. Test signals are count1=1, count2=3, count3=2, overflows=3, and overflows_2=3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal_overflow.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal_overflow.c

Purpose: `bp_signal_overflow.c` verifies breakpoint sample-period overflow delivery through SIGIO.

Important APIs and state: constants define execution count and overflow threshold. A global fd and overflow counter are used by the SIGIO handler. `test_function` is the breakpoint target, and `bp_count` reads the final event count.

Control flow: the test installs a SIGIO handler, configures a disabled instruction breakpoint with `sample_period = THRESHOLD` and async notification, enables it, executes the target function `EXECUTIONS` times, disables it, reads the count, and compares both total executions and overflow notifications with expected values.

State and persistence: kernel event state exists only while the fd is open. The software state is the overflow counter.

Dependencies, integration, risks, and tests: it depends on hardware instruction breakpoint support and signal delivery. Risks include unsupported architectures, perf_event permissions, and noisy signal behavior if events are not disabled promptly. Test signals are final count equal to `EXECUTIONS` and overflows equal to `EXECUTIONS / THRESHOLD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/bp_signal_overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/builtin-test.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/builtin-test.c

Purpose: `builtin-test.c` implements the `perf test` command: suite registry, filtering, forking/parallel execution, workload dispatch, result formatting, leak checking, and command-line options.

Important APIs and state: `generic_tests` and `arch_tests` define registered suites; `workloads` defines runnable test workloads. Global options include `dont_fork`, `sequential`, `runs_per_test`, `dso_to_test`, and `test_objdump_path`. Core helpers include `build_suites`, `__cmd_test`, `start_test`, `finish_test`, `run_test_child`, `perf_test__list`, and `cmd_test`.

Control flow: `cmd_test` parses options/subcommands, handles suite listing and workloads, initializes symbols and memlock limits, builds suite ordering, and delegates to `__cmd_test`. The runner can fork each test into a child, close inherited fds, install crash signal handlers with optional backtraces, run leak checks, and collect stdout/stderr. Parallel mode runs non-exclusive tests first and exclusive tests sequentially in a second pass.

State and persistence: persistent state is limited to process execution; child pipes and fds are closed. Configuration reads `annotate.objdump`. No commits or durable test artifacts are created by the harness itself.

Dependencies, integration, risks, and tests: it integrates all perf test suites, script-generated suites, workloads, symbol initialization, parse-options, run-command, colors, and rlimits. Risks include global `num_tests` accumulation, child process cleanup on signals, and environment-sensitive suite order. Test signals are correct listing/filtering, skip handling, parallel/sequential execution, child leak detection, and nonzero failures when any suite fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/builtin-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/code-reading.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/code-reading.c

Purpose: `code-reading.c` integration-tests perf's ability to read object code from mapped DSOs and compare it with `objdump` output for sampled instruction addresses.

Important APIs and state: a red-black tree of `tested_section` avoids retesting identical file/address sections. Objdump parsing helpers read hex bytes from disassembly lines and account for endian display. `read_object_code` resolves sample IPs to maps/DSOs, reads bytes through `dso__data_read_offset`, maps RIP to objdump address, and compares byte buffers. `do_test_code_reading` records a workload and processes samples.

Control flow: the test creates a live machine, loads kernel maps, optionally forces kallsyms for kcore testing, synthesizes thread maps, opens a suitable event from a fallback list, records a local workload that does file, sort, and syscall work, disables recording, and processes mmap events. Sample processing updates machine state for non-sample records and validates object-code reads for sample records. It tries normal and kcore paths and treats missing vmlinux/kcore/access as non-fatal skip-like success.

State and persistence: temporary workload files are removed. The test owns evlists, maps, machine, thread maps, CPU maps, and tested-section memory.

Dependencies, integration, risks, and tests: it depends on perf event access, symbol maps, DSO cache reads, objdump, kernel object availability, decompression for kernel modules, and architecture quirks such as RISC-V stop-address adjustment. Risks include environment sensitivity, objdump format changes, inaccurate kernel maps, and sampling nondeterminism. Test signals are matching byte buffers for sampled code sections or accepted no-access/no-kernel-object outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/code-reading.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/config-fragments/config -->
# sources/distributed-fs/ceph-client/tools/perf/tests/config-fragments/config

Purpose: this config fragment declares kernel tracing features expected by perf test/config fragment workflows.

Important entries: it enables tracepoints, stacktrace support, nop tracer, ring buffer, event tracing, context-switch tracer, generic tracing, ftrace, syscall ftrace, kprobes, kprobe events, and uprobe events, while selecting `CONFIG_BRANCH_PROFILE_NONE`.

Control flow and state: there is no executable logic. The file is consumed as static configuration input by build or test tooling that assembles required kernel config fragments.

Dependencies, integration, risks, and tests: it integrates with perf tests that need ftrace, tracepoints, syscall tracing, kprobes, and uprobes. Risks are stale config expectations if perf tests begin requiring additional tracing features or if a target architecture names options differently. Test signals are kernel builds/config checks where this fragment satisfies perf tracing test prerequisites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/config-fragments/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/cpumap.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/cpumap.c

Purpose: `cpumap.c` validates CPU map serialization, parsing, printing, merging, intersection, equality, and synthetic event decoding.

Important APIs and state: processors for synthetic CPU map events validate mask, explicit CPU list, and CPU range encodings. Test helpers use `perf_cpu_map__new`, `perf_event__synthesize_cpu_map`, `cpu_map__new_data`, `cpu_map__snprint`, `perf_cpu_map__merge`, `perf_cpu_map__intersect`, and `perf_cpu_map__equal`. The suite has multiple named test cases under `"CPU map"`.

Control flow: synthesis tests build maps that should choose mask, explicit CPUs, or range forms and validate the generated data. Print tests assert canonical string output. Merge and intersect tests build maps from strings and compare count and formatted result. Equality tests verify self-equality, inequality across empty/any/single/pair maps, and equality after merge/intersect transformations.

State and persistence: state is allocated CPU map objects with reference-count assertions; objects are put before exit. No files or kernel events are needed.

Dependencies, integration, risks, and tests: it depends on libperf cpumap internals and synthetic event layout. Risks include fragile expectations if canonical formatting changes. Test signals are exact map sizes, CPU values, strings, and reference counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/cpumap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/demangle-java-test.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/demangle-java-test.c

Purpose: `demangle-java-test.c` verifies perf's Java symbol demangler for JVM descriptor-style method names.

Important APIs and state: the test calls `dso__demangle_sym(NULL, 0, mangled)` over a table of mangled and expected strings. It uses `pr_debug` for mismatches and registers `"Demangle Java"`.

Control flow: each case demangles a Java-like method descriptor, checks for non-null output, compares against the expected dotted class/method/signature form, frees the buffer, and accumulates failure state.

State and persistence: all state is local; returned demangled strings are freed.

Dependencies, integration, risks, and tests: it depends on perf's symbol demangler dispatch recognizing Java names. Risks are expected-output drift as demangling behavior is improved or descriptor coverage expands. Test signals are exact matches for StringLatin1, ZipUtils, regex, AbstractStringBuilder, and constructor descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/demangle-java-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/demangle-ocaml-test.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/demangle-ocaml-test.c

Purpose: `demangle-ocaml-test.c` checks OCaml symbol demangling behavior.

Important APIs and state: it calls `dso__demangle_sym` on a small table containing a non-OCaml symbol and OCaml-encoded names. The suite is `"Demangle OCaml"`.

Control flow: each test case accepts either null output for non-demangled input or an exact demangled string. It reports mismatches with `pr_debug`, frees any returned buffer, and returns failure if any case differs.

State and persistence: no persistent state; allocations are freed per case.

Dependencies, integration, risks, and tests: it depends on perf's OCaml demangler and encoding rules for module separators and escaped punctuation. Risks are strict expected strings when demangler policy changes. Test signals include `main` remaining undemangled and OCaml names producing `Stdlib.array.map_154`, source-location anonymous function text, and operator decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/demangle-ocaml-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/demangle-rust-v0-test.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/demangle-rust-v0-test.c

Purpose: `demangle-rust-v0-test.c` validates Rust v0 symbol demangling across functions, impls, traits, closures, const generics, arrays, and statics.

Important APIs and state: it calls `dso__demangle_sym(NULL, 0, mangled)` for a table of v0 mangled names and expected readable symbols. The suite is `"Demangle Rust"`.

Control flow: the test iterates all cases, requires a non-null demangled buffer, compares it with expected text, logs detailed mismatches, frees the buffer, and returns aggregate success/failure.

State and persistence: no persistent state; heap outputs are freed.

Dependencies, integration, risks, and tests: it depends on perf's Rust v0 demangler. Risks include strict string expectations for Rust demangling syntax and missing coverage for newer mangling features. Test signals are exact demangling for standard path impls, trait-qualified methods, closures, higher-ranked function types, numeric consts, arrays, and nested statics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/demangle-rust-v0-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/dlfilter-test.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/dlfilter-test.c

Purpose: `dlfilter-test.c` tests perf script's dlfilter C API by synthesizing a perf.data stream and running versioned test filter shared objects against it.

Important APIs and state: `struct test_data` carries the synthetic machine, file descriptors, generated C/program/perf.data paths, symbol addresses, and selected dlfilter name/description. Helpers write attr, comm, mmap, and sample records; compile a small C program; locate symbols with `nm`; and run `perf script --dlfilter`.

Control flow: each API version test locates the dlfilter shared object, verifies its description, requires gcc, writes and compiles a program with `foo` and `bar`, resolves their addresses, creates a pipe-mode perf.data file with attr/comm/mmap/sample events, optionally dumps it under high verbosity, then runs `perf script` with dlfilter arguments for multiple early/normal modes. Version 0 and 2 are tested.

State and persistence: temporary C, executable, and perf.data files are created under `/tmp` and removed unless verbosity is high. The machine and fd are cleaned up.

Dependencies, integration, risks, and tests: it depends on gcc, perf executable discovery, dlfilter test shared objects, symbol tools, synthetic event helpers, and filesystem permissions. Risks include shell command quoting limits, missing gcc/filter artifacts, and environment-sensitive paths. Test signals are successful filter description lookup and all `perf script --dlfilter` invocations returning zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/dlfilter-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/dso-data.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/dso-data.c

Purpose: `dso-data.c` tests DSO file data reads, cache behavior, descriptor limit handling, and reopen behavior.

Important APIs and state: `test_file` creates patterned temporary files. `dso__data_fd`, `dso__data_read_offset`, `dso__data_close`, `reset_fd_limit`, `dsos__add`, and `dsos__exit` are exercised. Three test cases are registered under `"DSO data tests"`: read, cache, and reopen.

Control flow: the read test creates a large file, wraps it in a DSO, reads offsets across cache pages and file end, and verifies bytes. The cache test lowers `RLIMIT_NOFILE`, creates many DSOs, opens enough data fds to force LRU closing, reads some DSOs, and checks no fd leaks. The reopen test sets a tight fd limit, opens DSOs plus an extra fd, and verifies older DSO fds are closed and later reopened as needed.

State and persistence: temporary files are created and unlinked; process fd limits are modified during tests. DSO containers and references are released.

Dependencies, integration, risks, and tests: it depends on `/tmp`, `/proc/self/fd`, procfs mount discovery, and ability to adjust rlimits. Risks include fd-limit side effects, early-return cleanup gaps, and environment-specific open-fd baselines. Test signals are exact byte reads, expected DSO fd eviction, and equal open-fd counts before/after.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/dso-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/dwarf-unwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/dwarf-unwind.c

Purpose: `dwarf-unwind.c` tests user-space DWARF unwinding by constructing a known call chain and verifying resolved symbols in both caller and callee order.

Important APIs and state: global non-static functions are deliberately retained for symbol lookup. `unwind_entry` validates each frame against an expected stack. `test_dwarf_unwind__thread` captures an arch unwind sample and calls `unwind__get_entries`. The suite is `"Test dwarf unwind"`.

Control flow: `test__dwarf_unwind` enables DWARF callchain mode, creates a live machine and kernel maps, finds the current thread, and calls a chain of noinline functions. The deepest function invokes `bsearch` through a volatile function pointer so unwinding crosses libc and calls a comparator. The comparator runs unwinding once in caller order and again in callee order.

State and persistence: state is process-local machine/thread/sample data. Allocated user stack and register sample buffers are freed.

Dependencies, integration, risks, and tests: it depends on architecture-specific `test__arch_unwind_sample`, unwind support, symbols, frame retention despite optimization, and available maps. Risks include compiler tail-call optimization, stripped symbols, missing unwind backend, and libc differences. Test signals are exactly `MAX_STACK` resolved frames matching the expected function sequence in both orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/dwarf-unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/event-times.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/event-times.c

Purpose: `event-times.c` verifies that software event `cpu-clock:u` reports equal enabled and running time across different attach/enable modes.

Important APIs and state: attach helpers cover enable-on-exec child workload, current thread enabled, current thread disabled then enabled, CPU disabled then enabled, and CPU enabled. `test_times` creates an evlist, parses the event, requests total enabled/running read formats, attaches, does busy work, detaches, reads counts, and checks equality.

Control flow: the suite iterates all attach/detach combinations, preserving a skip result for permission failures. Child workload mode prepares and starts `true`; CPU mode may skip on `EACCES`.

State and persistence: evlists, thread maps, CPU maps, and workload process state are owned and cleaned up per test. No files persist.

Dependencies, integration, risks, and tests: it depends on perf event open permissions, process spawning, and stable software clock behavior. Risks include scheduling races, insufficient CPU permissions, and a possible typo-like `detach__disable` name that enables rather than disables before read. Test signals are `count.ena == count.run` for each successful attach mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/event-times.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/event_groups.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/event_groups.c

Purpose: `event_groups.c` tests valid and invalid perf event group combinations across hardware, software, and available uncore PMUs.

Important APIs and state: static `types` and `configs` represent hardware cycles, software context-switches, and one detected uncore PMU. `setup_uncore_event` scans PMUs and validates a candidate event can open. `run_test` opens a group leader plus two siblings and checks expected success/failure. The suite is `"Event groups"`.

Control flow: the test skips if no usable uncore PMU is found. It tries every 3-event combination of hardware/software/uncore. Combinations containing both hardware and uncore are marked erroneous by the bitmask logic and should fail; others should succeed. All fds are closed after each attempt.

State and persistence: state is only event fds and the selected PMU type/config. No files are written.

Dependencies, integration, risks, and tests: it depends on available uncore PMUs, permissions, architecture-specific event constraints, and `perf_pmus__scan`. Risks include false skip on systems without known PMUs, false failures from PMU permissions, and hard-coded uncore config values. Test signals are expected pass/fail matrix rows in debug output and overall `TEST_OK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/event_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/event_update.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/event_update.c

Purpose: `event_update.c` verifies synthetic `PERF_RECORD_EVENT_UPDATE` records for unit, scale, name, and CPU map updates.

Important APIs and state: processor callbacks validate event ID `123`, update type, and payload. `struct event_name` embeds a `perf_tool` and expected name for name-update validation. The suite is `"Synthesize attr update"`.

Control flow: the test creates a default evlist/evsel, allocates one ID, maps it to ID 123, mutates evsel unit and scale, synthesizes corresponding update records, initializes a perf tool for name and CPU callbacks, replaces `pmu_cpus` with CPU map `1,2,3`, and synthesizes CPU update.

State and persistence: all state is heap perf objects freed by `evlist__delete`; the temporary unit string and CPU map are owned through evsel fields.

Dependencies, integration, risks, and tests: it depends on synthetic-events helpers and event-update record layout. Risks include exact floating comparison for `0.123`, ownership mistakes around replacing `pmu_cpus`, and ID mapping assumptions. Test signals are all callbacks receiving expected ID, type, string, scale, and CPU list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/event_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/evsel-roundtrip-name.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/evsel-roundtrip-name.c

Purpose: `evsel-roundtrip-name.c` validates that parsed events round-trip back to their canonical evsel names.

Important APIs and state: cache-name tests use `__evsel__hw_cache_type_op_res_name`, `parse_event`, and `evsel__name_is`. Generic name-array tests parse lists of event names and compare every resulting evsel. The suite is `"Roundtrip evsel->name"`.

Control flow: cache testing iterates every hardware cache type, op, and result, skipping invalid cache operations and parse failures for unsupported PMUs. Name-array testing parses known hardware/software/tracepoint names, then verifies each evsel reports the same name expected from the input array.

State and persistence: evlists are allocated and deleted per case. No external state persists.

Dependencies, integration, risks, and tests: it depends on parser support, PMU availability, and canonical name formatting. Risks include platform-specific unsupported events and strict string matching when display names intentionally change. Test signals are no mismatches for supported parsed events and graceful skips for unsupported cache events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/evsel-roundtrip-name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/evsel-tp-sched.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/evsel-tp-sched.c

Purpose: `evsel-tp-sched.c` validates parsed field metadata for the `sched:sched_switch` tracepoint.

Important APIs and state: `evsel__test_field` looks up a field by name in the tracepoint format and checks size and signedness. `test__perf_evsel__tp_sched_test` opens the sched tracepoint evsel and validates key fields. The suite object is `suite__perf_evsel__tp_sched_test`.

Control flow: the test parses or creates the sched switch tracepoint evsel, verifies it has trace-event format data, then checks fields such as previous and next comm, pid, prio, and state for expected sizes/sign flags.

State and persistence: all state is evsel/trace-event metadata allocated during the test and cleaned with normal suite ownership. No files are written.

Dependencies, integration, risks, and tests: it depends on libtraceevent, sched tracepoint format availability, and kernel field definitions. The suite is compiled only when traceevent support is available. Risks include kernel tracepoint format changes and unavailable tracing files. Test signals are exact field lookup, size, and signedness matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/evsel-tp-sched.c -->
