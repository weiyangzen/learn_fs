# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/phc.sh

Purpose: shell functional tests for a PTP hardware clock using `phc_ctl`, covering set time, adjust time, and adjust frequency.

Important APIs and functions: `require_command`, `phc_sanity`, `check_err`, `log_test`, `tests_run`, `cleanup`, and test wrappers `settime`, `adjtime`, `adjfreq`. It parses `phc_ctl` output with `awk`.

Control flow: require root, require a device argument, require `phc_ctl`, verify the device, then run requested tests or all tests. Each test invokes `phc_ctl`, handles "Operation not supported" as skip, checks resulting integer seconds, logs status, and resets the clock in cleanup.

State and persistence: modifies the PTP clock's time and frequency, then attempts cleanup on every test and at exit.

Dependencies and integration: requires linuxptp `phc_ctl`, root, and a valid PHC device such as `/dev/ptp0`.

Risks and test signals: hardware and driver support determine skip/fail. Time checks assume command latency does not move integer seconds outside expected values.
