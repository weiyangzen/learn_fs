## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_perl.sh

Purpose: validates generated Perl scripts from `perf script -g`.
Important functions: `check_perl_support` and `test_script`.
Control flow: sets `PERF_EXEC_PATH` for source-tree scripts, checks libperl support, tries `sched:sched_switch` first, then `task-clock` if tracepoint recording skips. For each event it records `thloop`, generates a Perl script, executes it, and searches for expected callback output.
State and persistence: temp perf.data and generated `.pl` are cleaned by traps.
Dependencies and integration: requires libperl support, tracepoints or task-clock, Data::Dumper output for generic events, and perf workload.
Risks: tracepoint recording may require permissions; expected output differs by event class.
Test signals: generated script exists and execution output contains `sched::sched_switch` or `$VAR1`.
