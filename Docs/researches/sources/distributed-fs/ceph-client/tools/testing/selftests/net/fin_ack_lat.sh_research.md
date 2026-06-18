# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.sh

## Purpose
`fin_ack_lat.sh` is the kselftest wrapper for `fin_ack_lat`. It runs the generated latency probe for a fixed period and fails if the probe reports any FIN/ACK latency spike.

## Important APIs, Functions, and Types
The script is intentionally small. `cleanup()` kills processes named `fin_ack_lat` and removes the temporary log. `do_test()` starts `./fin_ack_lat`, pipes stdout through `tee` into a temporary file, sleeps for the requested runtime, counts log lines with `wc -l`, and returns failure if the count is greater than zero. It uses `mktemp`, `trap`, `pidof`, `kill`, `tee`, `wc`, and `awk`.

## Control Flow
The script enables `set -e`, creates `/tmp/fin_ack_latency.XXXX.log`, installs `trap cleanup EXIT`, and calls `do_test "30"`. The probe runs in the background while the wrapper sleeps for 30 seconds. After the sleep, the wrapper counts spike lines and prints `FAIL: N spikes detected` when any are present. If no spikes are observed, it prints `test done`.

## State and Persistence
The only persistent state during execution is the temporary log file under `/tmp`. Cleanup removes that file and attempts to kill all processes returned by `pidof fin_ack_lat`. The background PID is stored in `PID` but not used by cleanup.

## Dependencies and Integration Points
The wrapper assumes the `fin_ack_lat` binary exists in the current directory, typically built by the kselftest harness. It depends on normal POSIX shell utilities and process visibility through `pidof`. It integrates with kselftest via its exit status: zero when no spikes are logged, nonzero when `do_test` returns failure.

## Risks
`kill $(pidof fin_ack_lat)` can fail when no process exists; because cleanup runs under `set -e`, that can affect script exit behavior if the process has already exited. It also kills every matching process name, not only the PID started by this script. The wrapper only watches stdout; stderr server-port output is not counted as a failure. The 30-second runtime is a compromise and may miss rare races on quiet systems or produce environment-sensitive failures on overloaded hosts.

## Test Signals
The signal is binary: zero spike lines means pass and `test done`; one or more stdout lines from the C probe means failure with a count. A spike line contains the client local port, the single-iteration latency, the running average, and the number of samples.
