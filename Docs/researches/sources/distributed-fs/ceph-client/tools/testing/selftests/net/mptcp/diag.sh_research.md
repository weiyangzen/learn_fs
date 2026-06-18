# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/diag.sh

## Purpose
This shell selftest validates MPTCP diagnostic visibility and counters through `ss`, `/proc/net/protocols`, MPTCP nstat counters, and the compiled `mptcp_diag` helper.

## Important APIs and Functions
It uses `mptcp_lib_check_mptcp`, `mptcp_lib_check_tools`, `mptcp_lib_ns_init`, `mptcp_lib_result_*`, and `mptcp_connect`. Local helpers include `flush_pids`, `cleanup`, `get_msk_inuse`, `__chk_nr`, `chk_msk_nr`, `chk_listener_nr`, `wait_msk_nr`, `chk_msk_fallback_nr`, `chk_msk_remote_key_nr`, `chk_msk_listen`, `chk_msk_inuse`, `chk_msk_cestab`, `chk_dump_one`, `chk_dump_subflow`, `chk_msk_info`, `chk_last_time_info`, `wait_connected`, and `chk_sndbuf`.

## Control Flow and State
The script creates one namespace, starts MPTCP listener/client pairs on loopback, validates listener filters and post-handshake socket counts, checks send-buffer parity and last activity timestamps, verifies remote keys and fallback state, compares `mptcp_diag` output with `ss`, kills processes, and repeats with TCP fallback and many-client/listener scenarios. State is namespace-scoped sockets/processes and counters, cleaned by trap.

## Dependencies and Integration
It depends on `mptcp_lib.sh`, `ip`, `ss`, `mptcp_connect`, `mptcp_diag`, MPTCP diag kernel support, and loopback namespace networking. It integrates with the MPTCP Makefile as a `TEST_PROGS` entry.

## Risks and Test Signals
Timing and process cleanup are important; `flush_pids` uses SIGUSR1 then waits before SIGKILL cleanup. Feature gaps may be skipped if the suite is not requiring all features. Pass/fail signals are accumulated TAP results from `mptcp_lib_result_print_all_tap`; failures include mismatched socket counts, missing tokens, missing fallback, stale in-use counters, or mismatched diag output.
