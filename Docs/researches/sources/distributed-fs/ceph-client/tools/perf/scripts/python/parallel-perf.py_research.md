# sources/distributed-fs/ceph-client/tools/perf/scripts/python/parallel-perf.py

Purpose: `parallel-perf.py` runs a `perf script` command many times in parallel by splitting input by CPU and/or time, writing each shard into a separate output directory.

Important APIs and types: `Verbosity` centralizes quiet/verbose/debug behavior. `Work` wraps a subprocess, optional pipe consumer, and `cmd.txt`/`out.txt`/`err.txt` paths. `OptPos` parses and optionally removes short and long perf options from an argv list. `CPUTimeRange` carries Intel PT density-splitting state. `ParallelPerf` coordinates parsing, header reads, split planning, self-checking, work creation, and execution.

Control flow: `Main` parses tool options and the perf command after `--`. `ParallelPerf.Config` finds the input file, reads `perf script --header-only`, extracts original command line, time bounds, and CPU bounds, chooses per-CPU defaults for Intel PT, splits time ranges by fixed count, fixed interval, or Intel PT double-quick sample density, verifies recombination, opens boundary ranges, and builds the worklist. `RunWork` keeps up to `--jobs` subprocesses active and kills outstanding work on failure.

State and persistence: persistent output is an output directory containing per-shard command, stdout, and non-empty stderr files. The script refuses to overwrite an existing output directory.

Dependencies, integration, risks, and tests: it depends on `perf script`, perf header field names, Python subprocess behavior, and command-line time/CPU syntax. Risks include assuming CPU is the first field in quick-output lines, treating any stderr as error after successful exit, fatal `grep`-style pipe consumers with no matches, and expensive pre-analysis on huge PT data. Test signals are dry-run command lists, self-test range recombination, successful shard completion, and expected directory trees.
