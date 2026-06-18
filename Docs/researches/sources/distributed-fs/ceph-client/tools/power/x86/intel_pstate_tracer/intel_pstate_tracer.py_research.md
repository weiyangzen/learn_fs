# sources/distributed-fs/ceph-client/tools/power/x86/intel_pstate_tracer/intel_pstate_tracer.py

## Purpose
`intel_pstate_tracer.py` is a Python 3 utility for collecting, parsing, and plotting Linux `power/pstate_sample` trace data for debugging and tuning the `intel_pstate` driver. It can either parse an existing trace file or enable tracing for a requested interval, then generate CSV files and many PNG graphs under `results/<testname>/`.

## Important APIs, Types, And Functions
The script is procedural. Constants `C_CPU` through `C_COMM` define CSV column indexes used by gnuplot commands, and `MAX_CPUS` caps supported CPUs at 256. Plot functions generate per-CPU and all-CPU graphs for P-state, performance busy, scaled busy, IO boost, durations, loads, frequency, and TSC sanity data. `common_gnuplot_settings()` and `set_4_plot_linestyles()` configure Gnuplot. Data functions include `store_csv()`, `split_csv()`, `cleanup_data_files()`, and `read_trace_data()`. Trace-control functions are `clear_trace_file()`, `enable_trace()`, `disable_trace()`, `set_trace_buffer_size()`, and `free_trace_buffer()`. `fix_ownership()` gives outputs back to the sudo caller when applicable.

## Control Flow
The `__main__` block parses getopt options for existing trace file, interval collection, CPU mask, test name, and buffer memory. It creates `results/<testname>`, writes a CSV header, optionally clears tracing, sets buffer size, enables the `pstate_sample` event, sleeps for the interval, disables tracing, then parses `/sys/kernel/tracing/trace` or the provided trace file. `read_trace_data()` reads the whole file, regex-matches pstate sample lines, computes elapsed time, load, duration, frequency in GHz, and TSC-derived GHz, appends rows to `cpu.csv`, splits the master CSV into per-CPU CSVs, and finally plotting functions render PNGs with Gnuplot.

## State And Persistence Behavior
Global state tracks sample number, per-CPU last timestamp, start time, current max CPU, graph-data presence, test name, and trace file path. Persistent outputs are directories and files under `results/<testname>/`: `cpu.csv`, `cpuNNN.csv`, and PNG graphs. When interval mode is used, the script mutates tracing sysfs state under `/sys/kernel/tracing/`, including event enablement, trace buffer size, and trace contents. SIGINT cleanup disables tracing, clears the trace file, and frees the buffer if interval mode is active.

## Dependencies And Integration Points
The script requires Python 3, `Gnuplot`, `numpy`, Linux tracing, and shell tools invoked via `subprocess.check_output()` and `os.system()`. It expects trace lines emitted by the kernel `power:pstate_sample` event with fields such as `core_busy`, `scaled`, `from`, `to`, `mperf`, `aperf`, `tsc`, `freq`, and optional `io_boost`.

## Risks And Edge Cases
The parser reads the full trace file into memory and uses a long regex tied to trace formatting. CPU ids beyond 255 are not supported. `split_csv()` uses shell `grep` with formatted CPU names and can be sensitive to shell environment. Existing test directories abort reruns. Test names are used as directory names and in gnuplot titles; help text warns against underscores for plot rendering but there is no strict sanitization. Tracing sysfs writes require root and can leave tracing enabled if the process is killed outside SIGINT handling. Bare `except` blocks hide specific IO failures.

## Test Signals
Tests should include parsing a small canned trace with and without `io_boost`, CPU mask filtering, per-CPU split output, no-data failure, existing test directory failure, option validation, and plot command generation with mocked `Gnuplot`. Integration tests on a tracing-enabled kernel should verify interval cleanup restores buffer size and disables the event after normal completion and SIGINT.
