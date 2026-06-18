# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.c` implements s390 CPU Measurement Sampling Facility AUX trace support. It registers an auxtrace decoder, validates and dumps raw sampling-data blocks, queues per-CPU AUX buffers, orders decoding by timestamps, synthesizes perf sample events from hardware sampling entries, handles lost AUX data, and optionally logs AUX/counter raw data to files.

## Important APIs, Types, and Functions

Public APIs are `s390_cpumsf_process_auxtrace_info` and, through `s390-cpumsf.h`, `s390_cpumsf_recording_init` from the broader subsystem. Primary state containers are `struct s390_cpumsf` for auxtrace instance state and `struct s390_cpumsf_queue` for per-queue buffer/log state.

Important internal functions include counter logging `s390_cpumcf_dumpctr`, entry display helpers `s390_cpumsf_basic_show`, `s390_cpumsf_diag_show`, `s390_cpumsf_trailer_show`, validation `s390_cpumsf_validate`, trailer checks/timestamps `s390_cpumsf_reached_trailer`, `trailer_timestamp`, `get_trailer_time`, dumping `s390_cpumsf_dump`, sample synthesis `s390_cpumsf_make_event`, decoding `s390_cpumsf_samples`, `s390_cpumsf_run_decoder`, queue setup/update/process functions, lost/error synthesis, auxtrace callbacks, config handling, and itrace option validation.

## Control Flow

`s390_cpumsf_process_auxtrace_info` validates the AUXTRACE_INFO record, allocates `struct s390_cpumsf`, checks supported `--itrace` options, reads optional `auxtrace.dumpdir`, initializes auxtrace queues, fills session/machine/type metadata, installs auxtrace callbacks on the session, and processes the auxtrace index unless dump mode is active.

During report processing, `s390_cpumsf_process_event` is called for timestamped events. It ignores dump mode, requires ordered events, dumps raw counter-set samples for `PERF_EVENT_CPUM_CF_DIAG`, synthesizes lost-buffer errors for truncated AUX records, then updates queues and processes queued AUX data up to the event timestamp. Queue processing uses an auxtrace heap ordered by the next timestamp; it pops the earliest queue, decodes one or more pages until the timestamp boundary, updates partial buffer state when a later page is not ready, and re-adds the queue with the next timestamp.

Decoding validates that AUX data is page-sized, begins with a basic entry, and has descriptor sizes from the trailer or old-machine fallback. It iterates basic and diagnostic entries, skips trailers at page ends, converts basic entries into `perf_sample` objects with IP, pid/tid, CPU, period, and cpumode heuristics, then delivers synthetic sample events through `perf_session__deliver_synth_event`. Dump mode prints basic, diagnostic, and trailer records instead of synthesizing samples.

## State and Persistence Behavior

Runtime state is attached to `session->auxtrace` and owns auxtrace queues, heap, per-queue private objects, optional log directory string, and optional open log files. AUX buffers may be mmaped/read from perf.data and partially consumed via `use_data` and `use_size`. Optional logging writes `aux.smp.XX` and `aux.ctr.XX` files in the configured dump directory or current directory. Cleanup closes logs, frees queue private data, frees queues and heap, clears `session->auxtrace`, and frees the instance.

## Dependencies and Integration Points

The file integrates with perf auxtrace infrastructure, ordered events, perf sessions/data files, machines, evlists/evsels, PMU raw event constants from s390 headers, config parsing, sample delivery, and dump/color/debug output. It assumes host machine support only and sets `sf->machine` to `session->machines.host`.

## Risks and Edge Cases

Timestamp ordering is central; unordered tools are rejected. Invalid trailer TOD clock base makes a queue skip or error with max timestamp. Descriptor-size fallback depends on machine type parsed from cpuid and may reject unknown old hardware. Endian/bitfield decoding has separate little-endian fixups. `s390_cpumcf_dumpctr` writes `raw_size - 4`; malformed small raw samples would underflow if called without upstream validation. Optional log-file failures disable or degrade logging but continue processing. KVM support is explicitly absent. Heap re-addition after decoder errors can keep a queue alive with max timestamps.

## Test Signals

Tests should include AUXTRACE_INFO validation, unsupported itrace option rejection, config dumpdir handling, queue/index setup, timestamp-ordered partial page decoding, invalid page size/basic/trailer cases, old hardware descriptor fallback, little-endian field extraction, sample cpumode heuristics for native/guest/old hardware, lost AUX error synthesis, dump mode output, log file creation/write failures, and cleanup closing all resources.
