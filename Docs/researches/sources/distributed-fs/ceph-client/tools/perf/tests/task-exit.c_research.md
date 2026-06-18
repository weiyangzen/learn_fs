## sources/distributed-fs/ceph-client/tools/perf/tests/task-exit.c

Purpose: verifies perf receives exactly one `PERF_RECORD_EXIT` for a simple workload.
Important functions: `sig_handler`, `workload_exec_failed_signal`, and `test__task_exit`.
Control flow: creates a dummy evlist, prepares workload `true`, enables task events and sample parameters, opens/mmaps, starts workload, polls/reads mmap data until child exits and an exit event is seen, then validates `nr_exit == 1`.
State and persistence: globals `exited` and `nr_exit` track SIGCHLD/exec failure and exit event count; evlist maps monitor a prepared workload.
Dependencies and integration: evlist workload preparation/start, SIGCHLD handling, perf mmap event reading, and task event attr.
Risks: retries up to 1000 polls; s390x uses higher sample frequency; exec failure sets `nr_exit=-1`.
Test signals: exactly one `PERF_RECORD_EXIT`; suite is marked exclusive.
