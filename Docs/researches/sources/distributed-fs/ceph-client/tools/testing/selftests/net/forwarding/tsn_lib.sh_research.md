# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tsn_lib.sh

Purpose: shared TSN helper library for TAPRIO/isochron tests. It manages linuxptp processes, CPU frequency stabilization, isochron send/receive runs, and waiting for TAPRIO admin schedule activation.

Important functions are `phc2sys_start/stop`, `ptp4l_start/stop`, `cpufreq_max/restore`, `isochron_recv_start/stop`, `isochron_do`, `isochron_report_num_received`, and `taprio_wait_for_admin`. It conditionally requires `isochron`, `phc2sys`, `ptp4l`, and `phc_ctl` based on `REQUIRE_ISOCHRON` and `REQUIRE_LINUXPTP`. Dynamic global variable names track per-interface logs and PIDs.

Control flow helpers start realtime-priority daemons with temporary log files, start an isochron receiver, run `isochron send` in L2 or L4 mode with TXTIME and PTP UDS options, stop receiver, and restore CPU frequency. State includes background process PIDs, temp logs, CPU scaling governor/min frequency, generated isochron output files supplied by callers, and external TAPRIO wait script invocation under `tc-testing/scripts`. Risks include dynamic variable indirection, missing cpufreq sysfs, unbound PIDs if startup fails, stale temp logs, and hardcoded stats port 5000. Test signals are successful command exits and received-packet counts from `isochron_report_num_received`.
