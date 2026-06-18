# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_taprio.sh

Purpose: offloaded TAPRIO time-aware scheduler test using PTP, ETF/TXTIME, and `isochron` traffic. It checks gate open/closed behavior, max-SDU enforcement, and tolerance of PHC clock jumps.

Important functions are `ptp_setup`, `txtime_setup`, `taprio_replace`, `probe_path_delay`, `run_test`, `run_subtests`, `test_taprio_after_ptp`, `test_max_sdu`, `test_clock_jump_backward`, and `test_clock_jump_backward_forward`. It sources `tsn_lib.sh`, requires `python3`, and uses `tc_offload_check`. Setup builds a VLAN-aware bridge, static FDB, H1 txtime qdiscs, PTP sync, and path-delay calibration from isochron reports processed by Python/numpy.

Control flow calibrates path delay, installs TAPRIO schedules with gates for priorities 6/5/4, sends scheduled packets, counts received packets, computes median delay, and validates expected pass/fail. State is ptp4l/phc2sys processes, TAPRIO/ETF/MQPRIO/clsact qdiscs, temporary isochron data/Python files, bridge VLAN/FDB state, and PHC time. Risks are high: hardware offload, PHC synchronization, external tools, CPU frequency manipulation, timing thresholds, and cleanup of background processes. Test signals are packet reception counts, median-delay bounds, ping after clock jumps, and max-SDU pass/fail.
