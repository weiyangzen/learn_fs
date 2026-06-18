<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/runtest.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/runtest.c

## Purpose
Executes IFS tests on a selected physical core: SAF scan tests, Array BIST, and SBAF. It synchronizes SMT siblings, writes activation MSRs, interprets status, and records user-visible pass/fail/untested details.

## Important APIs, Types, And Functions
`do_core_test()` is the sysfs entry point. `ifs_test_core()` runs SAF over all valid chunks with retry/forward-progress logic. `ifs_array_test_core()` and `ifs_array_test_gen1()` run Array BIST generations. `ifs_sbaf_test_core()` runs SBAF over bundle/program indexes. Worker callbacks `doscan()`, `do_array_test()`, `do_array_test_gen1()`, and `dosbaf()` execute under `stop_core_cpuslocked()`.

## Control Flow
`do_core_test()` takes `cpus_read_lock()`, rejects offline CPUs, then dispatches by test type. SAF and SBAF require a loaded image. Sibling CPUs rendezvous using atomics and short delay loops, then write activation MSRs together. Status is reported by the first SMT thread. Retry loops restart from the hardware-reported chunk, bundle, or program index until success, non-restartable error, timeout, or no forward progress.

## State And Persistence
Updates `ifs_data.status` and `ifs_data.scan_details` for the last test only. Hardware test execution temporarily takes all threads of the tested core out of normal execution for up to hundreds of milliseconds.

## Dependencies And Integration Points
Depends on CPU hotplug read locks, stop-machine CPU coordination, MSR access, NMI watchdog touch, tracepoints `trace/events/intel_ifs.h`, and generation fields from `ifs_data`.

## Risks And Test Signals
Risks include latency impact, SMT sibling offline cases, forward-progress bugs, status bitfield interpretation, and stale loaded firmware. Test pass/fail/untested paths, offline sibling rejection, repeated interrupted tests, tracepoint output, and latency impact under workload isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/runtest.c -->
